"""Single-vendor chat REPL (`codecompass chat <vendor>`).

Grounds every answer on the vendor's already-persisted digest files
(`vendor/<name>/CLAUDE.md`, and `OVERVIEW.md` if the vendor has been
promoted) — never calls `sync_vendor` or reconstructs a `VendorDigest`,
so starting a chat session never re-incurs `promote`'s clone + AI-
generation cost (decisions/0023). Explicit-vendor mode only; project-root
routing and the whole-project rollup are Phase 9
(planning/phase-8-chat-repl.md, decisions/0012, decisions/0013).
"""

from __future__ import annotations

from pathlib import Path

import anthropic
from rich.console import Console
from rich.markdown import Markdown
from rich.prompt import Prompt

from codecompass.core import VendorConfig

_MODEL = "claude-haiku-4-5-20251001"
_MAX_TOKENS = 1024

_EXIT_COMMANDS = {"exit", "quit"}

_SYSTEM_PREAMBLE = (
    "You are answering questions about a single software dependency, "
    "grounded entirely in the reference material below — a generated "
    "digest for the exact version installed in this project. Answer only "
    "from this material. If something isn't covered here, say so rather "
    "than falling back on general prior knowledge, which may be outdated "
    "or describe a different version."
)


class ChatError(Exception):
    """Raised when a chat session can't start (the vendor was never
    synced — no `vendor/<name>/CLAUDE.md`) or an Anthropic API call fails
    mid-conversation.
    """


def _build_system_prompt(vendor_dir: Path, config: VendorConfig) -> str:
    """Reads `CLAUDE.md` (required) and `OVERVIEW.md` (optional) as raw
    text and concatenates them under a grounding-only instruction — no
    parsing of individual sections, no reconstructed `VendorDigest`
    (decisions/0023).
    """
    claude_md_path = vendor_dir / "CLAUDE.md"
    if not claude_md_path.is_file():
        raise ChatError(
            f"{config.name}: not yet synced (no {claude_md_path}) — run `codecompass` first"
        )
    sections = [claude_md_path.read_text(encoding="utf-8")]
    overview_path = vendor_dir / "OVERVIEW.md"
    if overview_path.is_file():
        sections.append(overview_path.read_text(encoding="utf-8"))
    return f"{_SYSTEM_PREAMBLE}\n\n" + "\n\n".join(sections)


def _call_anthropic(system_prompt: str, messages: list[dict[str, str]]) -> str:
    """One plain multi-turn text-completion call against `_MODEL` — no
    forced tool-use, unlike `grounded_description._call_anthropic`'s
    single-shot structured call. Tests monkeypatch this function directly
    (decisions/0016 — no test ever makes a real API call).
    """
    try:
        client = anthropic.Anthropic()
        response = client.messages.create(
            model=_MODEL,
            max_tokens=_MAX_TOKENS,
            system=system_prompt,
            messages=messages,
        )
    except anthropic.AnthropicError as exc:
        raise ChatError(f"Anthropic API call failed: {exc}") from exc

    for block in response.content:
        if block.type == "text":
            return block.text
    raise ChatError("Anthropic response did not include a text block")


def run_chat(config: VendorConfig, project_root: Path, console: Console) -> None:
    """The REPL loop: a context-indicator line, then prompt/response
    turns until `exit`/`quit`/EOF (`Ctrl-D`)/`Ctrl-C`. Raises `ChatError`
    (propagated to the caller) only if the session can't start at all —
    a mid-conversation API failure is reported inline and the loop
    continues, rather than ending the whole session.
    """
    vendor_dir = project_root / "vendor" / config.name
    system_prompt = _build_system_prompt(vendor_dir, config)

    console.print(
        f"[bold]codecompass chat[/bold] — {config.name}. Digest-only, no live source. "
        "Type 'exit' or Ctrl-D to quit."
    )
    if not (vendor_dir / "OVERVIEW.md").is_file():
        console.print(
            "[yellow]no grounded description yet — run `codecompass sync` to "
            "let usage-driven AI enrichment (Phase B) pick this vendor up for "
            "deeper answers[/yellow]"
        )

    messages: list[dict[str, str]] = []
    while True:
        try:
            question = Prompt.ask("[bold cyan]>[/bold cyan]", console=console)
        except (EOFError, KeyboardInterrupt):
            console.print()
            break
        question = question.strip()
        if question.lower() in _EXIT_COMMANDS:
            break
        if not question:
            continue

        messages.append({"role": "user", "content": question})
        try:
            reply = _call_anthropic(system_prompt, messages)
        except ChatError as exc:
            console.print(f"[red]error:[/red] {exc}")
            messages.pop()
            continue
        messages.append({"role": "assistant", "content": reply})
        console.print(Markdown(reply))
