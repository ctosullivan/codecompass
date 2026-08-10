from dataclasses import dataclass
from pathlib import Path

import pytest

import depcompass.gap_analysis as gap_analysis_module
from depcompass.core import Depth, Ecosystem, VendorConfig
from depcompass.gap_analysis import (
    GapAnalysis,
    GapAnalysisError,
    check_budget,
    estimate_cost,
    generate_gap_analysis,
)

_FIXED_RESULT = {
    "technical_analysis": "The API surface covers X but not Y.",
    "conversational_overview": "This library handles HTML-to-Markdown conversion.",
    "action_pointer_file": "src/commonmark-rules.js",
    "action_pointer_note": "override fencedCodeBlock here",
}


def _full_config(context_path: str = "README.md") -> VendorConfig:
    return VendorConfig(
        name="turndown",
        ecosystem=Ecosystem.NPM,
        depth=Depth.FULL,
        context_path=context_path,
    )


def test_generate_gap_analysis_maps_result_fields(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    (tmp_path / "README.md").write_text("This project converts HTML to Markdown.", encoding="utf-8")
    monkeypatch.setattr(gap_analysis_module, "_call_anthropic", lambda *a, **k: dict(_FIXED_RESULT))

    result = generate_gap_analysis(_full_config(), "some_fn(): does a thing.", tmp_path)

    assert result == GapAnalysis(
        technical="The API surface covers X but not Y.",
        conversational_overview="This library handles HTML-to-Markdown conversion.",
        action_pointer_file="src/commonmark-rules.js",
        action_pointer_note="override fencedCodeBlock here",
    )


def test_generate_gap_analysis_action_pointer_defaults_to_none(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    (tmp_path / "README.md").write_text("desc", encoding="utf-8")
    minimal_result = {
        "technical_analysis": "no gaps found",
        "conversational_overview": "does its job fine",
    }
    monkeypatch.setattr(
        gap_analysis_module, "_call_anthropic", lambda *a, **k: dict(minimal_result)
    )

    result = generate_gap_analysis(_full_config(), "surface", tmp_path)

    assert result.action_pointer_file is None
    assert result.action_pointer_note is None


def test_generate_gap_analysis_truncates_context_path(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    long_text = "x" * 20000
    (tmp_path / "README.md").write_text(long_text, encoding="utf-8")
    captured: dict[str, str] = {}

    def _fake_call(system_prompt: str, user_prompt: str) -> dict:
        captured["user_prompt"] = user_prompt
        return dict(_FIXED_RESULT)

    monkeypatch.setattr(gap_analysis_module, "_call_anthropic", _fake_call)

    generate_gap_analysis(_full_config(), "surface", tmp_path)

    embedded_x_count = captured["user_prompt"].count("x")
    assert embedded_x_count == gap_analysis_module._CONTEXT_PATH_CHAR_CAP
    assert embedded_x_count < len(long_text)


def test_generate_gap_analysis_missing_context_path_raises(tmp_path: Path) -> None:
    config = VendorConfig(
        name="lodash", ecosystem=Ecosystem.NPM, depth=Depth.SURFACE, context_path=None
    )
    with pytest.raises(GapAnalysisError, match="context_path"):
        generate_gap_analysis(config, "surface", tmp_path)


def test_generate_gap_analysis_unreadable_context_path_raises(tmp_path: Path) -> None:
    config = _full_config(context_path="does-not-exist.md")
    with pytest.raises(GapAnalysisError, match="could not read"):
        generate_gap_analysis(config, "surface", tmp_path)


def test_generate_gap_analysis_missing_required_field_raises(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    (tmp_path / "README.md").write_text("desc", encoding="utf-8")
    monkeypatch.setattr(
        gap_analysis_module, "_call_anthropic", lambda *a, **k: {"technical_analysis": "only this"}
    )
    with pytest.raises(GapAnalysisError, match="missing required field"):
        generate_gap_analysis(_full_config(), "surface", tmp_path)


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
        gap_analysis_module.anthropic, "Anthropic", lambda: _FakeClient(response)
    )

    result = gap_analysis_module._call_anthropic("system", "user")

    assert result == {"technical_analysis": "ok"}


def test_call_anthropic_raises_if_no_tool_use_block(monkeypatch: pytest.MonkeyPatch) -> None:
    response = _FakeResponse(content=[_FakeTextBlock(text="I refuse to use the tool")])
    monkeypatch.setattr(
        gap_analysis_module.anthropic, "Anthropic", lambda: _FakeClient(response)
    )

    with pytest.raises(GapAnalysisError, match="did not include the expected tool call"):
        gap_analysis_module._call_anthropic("system", "user")


def test_call_anthropic_wraps_sdk_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    import anthropic

    class _RaisingClient:
        @property
        def messages(self) -> object:
            raise anthropic.AnthropicError("boom")

    monkeypatch.setattr(gap_analysis_module.anthropic, "Anthropic", lambda: _RaisingClient())

    with pytest.raises(GapAnalysisError, match="Anthropic API call failed"):
        gap_analysis_module._call_anthropic("system", "user")


def test_estimate_cost_scales_with_vendor_count() -> None:
    assert estimate_cost(0) == 0
    assert estimate_cost(3) == pytest.approx(3 * gap_analysis_module._ESTIMATED_COST_PER_CALL_USD)


def test_check_budget_none_is_noop() -> None:
    check_budget([_full_config()], None)  # should not raise


def test_check_budget_under_budget_does_not_raise() -> None:
    check_budget([_full_config()], budget=100.0)  # should not raise


def test_check_budget_over_budget_raises() -> None:
    configs = [_full_config(), _full_config()]
    with pytest.raises(GapAnalysisError, match="exceeds --budget"):
        check_budget(configs, budget=0.0)


def test_check_budget_ignores_surface_vendors() -> None:
    configs = [VendorConfig(name="lodash", ecosystem=Ecosystem.NPM, depth=Depth.SURFACE)]
    check_budget(configs, budget=0.0)  # no full+context_path vendors, should not raise
