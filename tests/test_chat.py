from dataclasses import dataclass
from pathlib import Path

import pytest
from rich.console import Console
from typer.testing import CliRunner

import codecompass.chat as chat_module
from codecompass.chat import ChatError, _build_system_prompt, run_chat
from codecompass.cli import app
from codecompass.core import Depth, Ecosystem, VendorConfig

runner = CliRunner()


def _config(name: str = "lodash", depth: Depth = Depth.FULL) -> VendorConfig:
    return VendorConfig(name=name, ecosystem=Ecosystem.NPM, depth=depth)


def _sync_vendor(tmp_path: Path, name: str, *, overview: str | None = None) -> Path:
    vendor_dir = tmp_path / "vendor" / name
    vendor_dir.mkdir(parents=True)
    (vendor_dir / "CLAUDE.md").write_text(
        f"# {name}\n\n## Metadata\n\n- **Installed version:** 1.0.0\n", encoding="utf-8"
    )
    if overview is not None:
        (vendor_dir / "OVERVIEW.md").write_text(overview, encoding="utf-8")
    return vendor_dir


def test_build_system_prompt_includes_claude_md_and_overview(tmp_path: Path) -> None:
    vendor_dir = _sync_vendor(tmp_path, "lodash", overview="A grab-bag of JS utilities.")

    prompt = _build_system_prompt(vendor_dir, _config())

    assert "Installed version:** 1.0.0" in prompt
    assert "A grab-bag of JS utilities." in prompt


def test_build_system_prompt_without_overview_is_claude_md_only(tmp_path: Path) -> None:
    vendor_dir = _sync_vendor(tmp_path, "lodash")

    prompt = _build_system_prompt(vendor_dir, _config(depth=Depth.SURFACE))

    assert "Installed version:** 1.0.0" in prompt


def test_build_system_prompt_never_synced_vendor_raises(tmp_path: Path) -> None:
    vendor_dir = tmp_path / "vendor" / "lodash"
    with pytest.raises(ChatError, match="not yet synced"):
        _build_system_prompt(vendor_dir, _config())


@dataclass
class _FakeTextBlock:
    text: str
    type: str = "text"


@dataclass
class _FakeToolUseBlock:
    input: dict
    type: str = "tool_use"


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


def test_call_anthropic_returns_text_block(monkeypatch: pytest.MonkeyPatch) -> None:
    response = _FakeResponse(content=[_FakeTextBlock(text="lodash is a utility library.")])
    monkeypatch.setattr(chat_module.anthropic, "Anthropic", lambda: _FakeClient(response))

    result = chat_module._call_anthropic("system", [{"role": "user", "content": "what is it?"}])

    assert result == "lodash is a utility library."


def test_call_anthropic_raises_if_no_text_block(monkeypatch: pytest.MonkeyPatch) -> None:
    response = _FakeResponse(content=[_FakeToolUseBlock(input={})])
    monkeypatch.setattr(chat_module.anthropic, "Anthropic", lambda: _FakeClient(response))

    with pytest.raises(ChatError, match="did not include a text block"):
        chat_module._call_anthropic("system", [])


def test_call_anthropic_wraps_sdk_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    import anthropic

    class _RaisingClient:
        @property
        def messages(self) -> object:
            raise anthropic.AnthropicError("boom")

    monkeypatch.setattr(chat_module.anthropic, "Anthropic", lambda: _RaisingClient())

    with pytest.raises(ChatError, match="Anthropic API call failed"):
        chat_module._call_anthropic("system", [])


def test_run_chat_prints_context_indicator_and_reply(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _sync_vendor(tmp_path, "lodash", overview="A grab-bag of JS utilities.")
    monkeypatch.setattr(
        chat_module, "_call_anthropic", lambda system, messages: "It's a utility library."
    )
    console = Console(file=_NullFile(), force_terminal=False)
    monkeypatch.setattr(chat_module, "Prompt", _ScriptedPrompt(["what is it?", "exit"]))

    run_chat(_config(), tmp_path, console)


class _NullFile:
    def write(self, *_args: object, **_kwargs: object) -> None:
        pass

    def flush(self) -> None:
        pass


class _ScriptedPrompt:
    def __init__(self, answers: list[str]) -> None:
        self._answers = iter(answers)

    def ask(self, *_args: object, **_kwargs: object) -> str:
        return next(self._answers)


def test_run_chat_never_synced_vendor_raises(tmp_path: Path) -> None:
    console = Console(file=_NullFile(), force_terminal=False)
    with pytest.raises(ChatError, match="not yet synced"):
        run_chat(_config(), tmp_path, console)


def test_chat_cli_unknown_vendor_errors(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "vendor.toml").write_text(
        '[[vendor]]\nname = "lodash"\necosystem = "npm"\ndepth = "surface"\n',
        encoding="utf-8",
    )

    result = runner.invoke(app, ["chat", "not-a-real-vendor"])

    assert result.exit_code == 1
    assert "not found in vendor.toml" in result.output


def test_chat_cli_never_synced_vendor_errors(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "vendor.toml").write_text(
        '[[vendor]]\nname = "lodash"\necosystem = "npm"\ndepth = "surface"\n',
        encoding="utf-8",
    )

    result = runner.invoke(app, ["chat", "lodash"])

    assert result.exit_code == 1
    assert "not yet synced" in result.output


def test_chat_cli_full_conversation_round_trip(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "vendor.toml").write_text(
        '[[vendor]]\nname = "lodash"\necosystem = "npm"\ndepth = "full"\n',
        encoding="utf-8",
    )
    _sync_vendor(tmp_path, "lodash", overview="A grab-bag of JS utilities.")
    monkeypatch.setattr(
        chat_module, "_call_anthropic", lambda system, messages: "It's a utility library."
    )

    result = runner.invoke(app, ["chat", "lodash"], input="what is it?\nexit\n")

    assert result.exit_code == 0, result.output
    assert "lodash" in result.output
    assert "depth=full" in result.output
    assert "It's a utility library." in result.output
    assert "no grounded description yet" not in result.output


def test_chat_cli_surface_vendor_shows_promote_hint(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "vendor.toml").write_text(
        '[[vendor]]\nname = "lodash"\necosystem = "npm"\ndepth = "surface"\n',
        encoding="utf-8",
    )
    _sync_vendor(tmp_path, "lodash")
    monkeypatch.setattr(
        chat_module, "_call_anthropic", lambda system, messages: "It's a utility library."
    )

    result = runner.invoke(app, ["chat", "lodash"], input="what is it?\nexit\n")

    assert result.exit_code == 0, result.output
    assert "no grounded description yet" in result.output
    assert "codecompass promote lodash" in result.output
