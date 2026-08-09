"""depcompass CLI entry point.

Every command is currently a stub — see docs/cli-reference.md for the
planned surface and the roadmap phase each command's real logic lands in.
"""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from depcompass.config import ConfigError, load_vendor_config
from depcompass.core import VendorConfig

app = typer.Typer(
    help="Grounded, version-pinned dependency reference docs for AI coding agents."
)
console = Console()

_PHASE_BY_COMMAND = {
    "init": 4,
    "sync": 4,
    "index": 4,
    "check": 6,
    "chat": 7,
}


def _not_implemented(command: str) -> None:
    phase = _PHASE_BY_COMMAND[command]
    console.print(
        f"[yellow]depcompass {command}[/yellow] is not yet implemented "
        f"(planned for Phase {phase}). See docs/cli-reference.md."
    )
    raise typer.Exit(code=1)


def _load_config(path: Path = Path("vendor.toml")) -> list[VendorConfig]:
    """Load and validate vendor.toml, exiting with a clear message on failure."""
    try:
        return load_vendor_config(path)
    except ConfigError as exc:
        console.print(f"[red]error:[/red] {exc}")
        raise typer.Exit(code=1) from exc


def _write_claude_md(*args: object, **kwargs: object) -> None:
    raise NotImplementedError(
        "_write_claude_md is a deliberate stub pending Phase 4 "
        "(per-vendor CLAUDE.md template rendering)."
    )


@app.command()
def init() -> None:
    """Bulk-discover dependencies and write a draft vendor.toml."""
    _not_implemented("init")


@app.command()
def sync() -> None:
    """Regenerate digests and trees for one or all vendors."""
    _not_implemented("sync")


@app.command()
def index() -> None:
    """Regenerate the routing table injected into the project's root CLAUDE.md."""
    _not_implemented("index")


@app.command()
def check() -> None:
    """Staleness gate comparing digests against installed versions."""
    _not_implemented("check")


@app.command()
def chat() -> None:
    """Lightweight terminal REPL grounded in vendor digests."""
    _not_implemented("chat")


if __name__ == "__main__":
    app()
