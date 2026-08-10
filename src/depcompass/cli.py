"""depcompass CLI entry point.

`init`, `sync`, and `index` are implemented (Phase 4). `check` and `chat`
are still stubs — see docs/cli-reference.md for the planned surface and
the roadmap phase each command's real logic lands in.
"""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from depcompass.config import ConfigError, load_vendor_config
from depcompass.core import VendorConfig
from depcompass.discovery import DiscoveryError, discover_all, write_vendor_toml
from depcompass.gap_analysis import GapAnalysisError
from depcompass.index import load_routing_rows, render_routing_table, update_root_claude_md
from depcompass.sync import sync_all

app = typer.Typer(
    help="Grounded, version-pinned dependency reference docs for AI coding agents."
)
console = Console()

_PHASE_BY_COMMAND = {
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


@app.command()
def init(
    scan: list[Path] = typer.Option(
        ...,
        "--scan",
        help="Manifest file to scan; repeat for multiple "
        "(--scan package.json --scan pyproject.toml).",
    ),
    vendor_toml: Path = typer.Option(
        Path("vendor.toml"), "--output", help="Where to write the generated vendor.toml."
    ),
) -> None:
    """Bulk-discover dependencies and write a draft vendor.toml."""
    try:
        names_by_ecosystem = discover_all(scan)
        write_vendor_toml(names_by_ecosystem, vendor_toml)
    except DiscoveryError as exc:
        console.print(f"[red]error:[/red] {exc}")
        raise typer.Exit(code=1) from exc
    total = sum(len(names) for names in names_by_ecosystem.values())
    console.print(f"[green]wrote[/green] {vendor_toml} with {total} discovered dependencies")


@app.command()
def sync(
    vendor: str | None = typer.Argument(None, help="Sync only this vendor; omit to sync all."),
    budget: float | None = typer.Option(
        None,
        "--budget",
        help="Cap estimated gap-analysis spend (USD) for this run; aborts before any "
        "API call if the estimate exceeds it. Omit for no cap.",
    ),
) -> None:
    """Regenerate digests and trees for one or all vendors."""
    configs = _load_config()
    if vendor is not None:
        configs = [c for c in configs if c.name == vendor]
        if not configs:
            console.print(f"[red]error:[/red] {vendor!r} not found in vendor.toml")
            raise typer.Exit(code=1)
    try:
        digests = sync_all(configs, Path.cwd(), budget=budget)
    except GapAnalysisError as exc:
        console.print(f"[red]error:[/red] {exc}")
        raise typer.Exit(code=1) from exc
    failed = False
    for digest in digests:
        if digest.gap_analysis_error:
            failed = True
            console.print(
                f"[yellow]synced (gap analysis failed)[/yellow] "
                f"{digest.config.name}@{digest.installed_version}: {digest.gap_analysis_error}"
            )
        else:
            console.print(
                f"[green]synced[/green] {digest.config.name}@{digest.installed_version}"
            )
    if failed:
        raise typer.Exit(code=1)


@app.command()
def index() -> None:
    """Regenerate the routing table injected into the project's root CLAUDE.md."""
    configs = _load_config()
    rows = load_routing_rows(configs, Path.cwd())
    update_root_claude_md(Path.cwd(), render_routing_table(rows))
    console.print(f"[green]updated[/green] CLAUDE.md routing table ({len(rows)} vendors)")


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
