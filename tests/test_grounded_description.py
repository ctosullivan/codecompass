from dataclasses import dataclass
from pathlib import Path

import pytest

import codecompass.grounded_description as grounded_description_module
from codecompass.core import Depth, Ecosystem, VendorConfig
from codecompass.grounded_description import (
    GroundedDescription,
    GroundedDescriptionError,
    check_budget,
    estimate_cost,
    generate_grounded_description,
)

_FIXED_RESULT = {
    "technical_analysis": "TurndownService converts HTML to Markdown via visitor rules.",
    "conversational_overview": "This library handles HTML-to-Markdown conversion.",
    "action_pointer_file": "src/commonmark-rules.js",
    "action_pointer_note": "override fencedCodeBlock here",
}


def _npm_config(name: str = "turndown") -> VendorConfig:
    return VendorConfig(name=name, ecosystem=Ecosystem.NPM, depth=Depth.FULL)


def _repo_with_readme(
    tmp_path: Path, text: str = "This project converts HTML to Markdown."
) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text(text, encoding="utf-8")
    return repo


def test_generate_grounded_description_maps_result_fields(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    repo = _repo_with_readme(tmp_path)
    monkeypatch.setattr(
        grounded_description_module, "_call_anthropic", lambda *a, **k: dict(_FIXED_RESULT)
    )

    result = generate_grounded_description(_npm_config(), repo)

    assert result == GroundedDescription(
        technical="TurndownService converts HTML to Markdown via visitor rules.",
        conversational_overview="This library handles HTML-to-Markdown conversion.",
        action_pointer_file="src/commonmark-rules.js",
        action_pointer_note="override fencedCodeBlock here",
    )


def test_generate_grounded_description_action_pointer_defaults_to_none(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    repo = _repo_with_readme(tmp_path)
    minimal_result = {
        "technical_analysis": "does a thing",
        "conversational_overview": "does its job fine",
    }
    monkeypatch.setattr(
        grounded_description_module, "_call_anthropic", lambda *a, **k: dict(minimal_result)
    )

    result = generate_grounded_description(_npm_config(), repo)

    assert result.action_pointer_file is None
    assert result.action_pointer_note is None


def test_generate_grounded_description_no_retrievable_material_raises(tmp_path: Path) -> None:
    empty_repo = tmp_path / "empty_repo"
    empty_repo.mkdir()
    with pytest.raises(GroundedDescriptionError, match="no README, docs, or entry-point file"):
        generate_grounded_description(_npm_config(), empty_repo)


def test_generate_grounded_description_missing_required_field_raises(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    repo = _repo_with_readme(tmp_path)
    monkeypatch.setattr(
        grounded_description_module,
        "_call_anthropic",
        lambda *a, **k: {"technical_analysis": "only this"},
    )
    with pytest.raises(GroundedDescriptionError, match="missing required field"):
        generate_grounded_description(_npm_config(), repo)


def test_gather_material_includes_readme_docs_and_entry_point(tmp_path: Path) -> None:
    repo = _repo_with_readme(tmp_path, "readme text")
    (repo / "docs").mkdir()
    (repo / "docs" / "guide.md").write_text("docs text", encoding="utf-8")
    (repo / "index.js").write_text("module.exports = {};", encoding="utf-8")

    material = grounded_description_module._gather_material(repo, _npm_config())

    assert "readme text" in material
    assert "docs text" in material
    assert "module.exports" in material


def test_gather_material_caps_total_raw_text(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(grounded_description_module, "_RAW_TEXT_CHAR_CAP", 20)
    repo = _repo_with_readme(tmp_path, "x" * 1000)

    material = grounded_description_module._gather_material(repo, _npm_config())

    embedded_x_count = material.count("x")
    assert embedded_x_count == 20
    assert embedded_x_count < 1000


def test_find_entry_point_python_prefers_package_init(tmp_path: Path) -> None:
    (tmp_path / "widget").mkdir()
    init_file = tmp_path / "widget" / "__init__.py"
    init_file.write_text("", encoding="utf-8")
    config = VendorConfig(name="widget", ecosystem=Ecosystem.PYTHON, depth=Depth.FULL)

    assert grounded_description_module._find_entry_point(tmp_path, config) == init_file


def test_find_entry_point_cargo_prefers_lib_rs(tmp_path: Path) -> None:
    (tmp_path / "src").mkdir()
    lib_rs = tmp_path / "src" / "lib.rs"
    lib_rs.write_text("", encoding="utf-8")
    config = VendorConfig(name="serde", ecosystem=Ecosystem.CARGO, depth=Depth.FULL)

    assert grounded_description_module._find_entry_point(tmp_path, config) == lib_rs


def test_find_entry_point_returns_none_when_nothing_matches(tmp_path: Path) -> None:
    config = VendorConfig(name="widget", ecosystem=Ecosystem.NPM, depth=Depth.FULL)
    assert grounded_description_module._find_entry_point(tmp_path, config) is None


@dataclass
class _FakeToolUseBlock:
    input: dict
    type: str = "tool_use"


@dataclass
class _FakeTextBlock:
    text: str
    type: str = "text"


@dataclass
class _FakeResponse:
    content: list


class _FakeMessages:
    def __init__(self, response: object) -> None:
        self._response = response

    def create(self, **kwargs: object) -> object:
        return self._response


class _FakeClient:
    def __init__(self, response: object) -> None:
        self.messages = _FakeMessages(response)


def test_call_anthropic_returns_tool_use_input(monkeypatch: pytest.MonkeyPatch) -> None:
    response = _FakeResponse(content=[_FakeToolUseBlock(input={"technical_analysis": "ok"})])
    monkeypatch.setattr(
        grounded_description_module.anthropic, "Anthropic", lambda: _FakeClient(response)
    )

    result = grounded_description_module._call_anthropic("system", "user")

    assert result == {"technical_analysis": "ok"}


def test_call_anthropic_raises_if_no_tool_use_block(monkeypatch: pytest.MonkeyPatch) -> None:
    response = _FakeResponse(content=[_FakeTextBlock(text="I refuse to use the tool")])
    monkeypatch.setattr(
        grounded_description_module.anthropic, "Anthropic", lambda: _FakeClient(response)
    )

    with pytest.raises(GroundedDescriptionError, match="did not include the expected tool call"):
        grounded_description_module._call_anthropic("system", "user")


def test_call_anthropic_wraps_sdk_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    import anthropic

    class _RaisingClient:
        @property
        def messages(self) -> object:
            raise anthropic.AnthropicError("boom")

    monkeypatch.setattr(
        grounded_description_module.anthropic, "Anthropic", lambda: _RaisingClient()
    )

    with pytest.raises(GroundedDescriptionError, match="Anthropic API call failed"):
        grounded_description_module._call_anthropic("system", "user")


def test_estimate_cost_scales_with_vendor_count() -> None:
    assert estimate_cost(0) == 0
    assert estimate_cost(3) == pytest.approx(
        3 * grounded_description_module._ESTIMATED_COST_PER_CALL_USD
    )


def test_check_budget_none_is_noop() -> None:
    check_budget([_npm_config()], None)  # should not raise


def test_check_budget_under_budget_does_not_raise() -> None:
    check_budget([_npm_config()], budget=100.0)  # should not raise


def test_check_budget_over_budget_raises() -> None:
    configs = [_npm_config(), _npm_config()]
    with pytest.raises(GroundedDescriptionError, match="exceeds --budget"):
        check_budget(configs, budget=0.0)


def test_check_budget_ignores_surface_vendors() -> None:
    configs = [VendorConfig(name="lodash", ecosystem=Ecosystem.NPM, depth=Depth.SURFACE)]
    check_budget(configs, budget=0.0)  # no full vendors, should not raise
