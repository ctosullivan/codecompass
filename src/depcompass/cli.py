"""depcompass CLI entry point.

`init`, `sync`, `index`, and `check` are implemented (Phases 4-6). `chat`
is still a stub — see docs/cli-reference.md for the planned surface and
the roadmap phase its real logic lands in.
"""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from depcompass.adapters import AdapterError
from depcompass.config import ConfigError, load_vendor_config
from depcompass.core import VendorConfig
from depcompass.discovery import DiscoveryError, discover_all, write_vendor_toml
from depcompass.gap_analysis import GapAnalysisError
from depcompass.index import load_routing_rows, render_routing_table, update_root_claude_md
from depcompass.staleness import Severity, VendorStaleness, check_all
from depcompass.sync import sync_all, sync_vendor

app = typer.Typer(
    help="Grounded, version-pinned dependency reference docs for AI coding agents."
)
console = Console()

_PHASE_BY_COMMAND = {
    "chat": 7,
}

_STRICT_FAIL_SEVERITIES = {Severity.MAJOR, Severity.UNKNOWN}


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
def check(
    strict: bool = typer.Option(
        False,
        "--strict",
        help="Pure gate: exit non-zero if any vendor has major/unclassifiable drift "
        "or a failed live version read. Intended for CI. Never regenerates anything.",
    ),
    fix: bool = typer.Option(
        False,
        "--fix",
        help="Regenerate every stale vendor's digest in place (via the same logic "
        "as `sync`, including gap analysis for depth=full vendors).",
    ),
) -> None:
    """Staleness gate comparing digests against installed versions.

    With no flags, always exits 0 — a report-only table for a human
    running it locally. `--strict` and `--fix` are mutually exclusive.
    """
    if strict and fix:
        console.print("[red]error:[/red] --strict and --fix are mutually exclusive")
        raise typer.Exit(code=1)

    configs = _load_config()
    results = check_all(configs, Path.cwd())
    console.print(_render_check_table(results))

    if fix:
        _run_fix(results)
        return

    if strict and any(
        result.error or result.severity in _STRICT_FAIL_SEVERITIES for result in results
    ):
        raise typer.Exit(code=1)


def _render_check_table(results: list[VendorStaleness]) -> Table:
    table = Table("Vendor", "Recorded", "Live", "Severity", "Notes")
    for result in results:
        notes = []
        if result.error:
            notes.append(result.error)
        elif result.recorded_version is None:
            notes.append("not synced")
        if result.transitive_drift:
            notes.append("transitive drift")
        table.add_row(
            result.config.name,
            result.recorded_version or "_not synced_",
            result.live_version or "_unavailable_",
            result.severity.value,
            "; ".join(notes),
            style=_row_style(result),
        )
    return table


def _row_style(result: VendorStaleness) -> str | None:
    if result.error or result.severity in _STRICT_FAIL_SEVERITIES:
        return "red"
    if result.severity is Severity.MINOR:
        return "yellow"
    return None


def _run_fix(results: list[VendorStaleness]) -> None:
    stale = [r for r in results if r.recorded_version != r.live_version or r.transitive_drift]
    failed = False
    for result in stale:
        try:
            digest = sync_vendor(result.config, Path.cwd())
        except AdapterError as exc:
            failed = True
            console.print(f"[red]fix failed[/red] {result.config.name}: {exc}")
            continue
        if digest.gap_analysis_error:
            failed = True
            console.print(
                f"[yellow]fixed (gap analysis failed)[/yellow] "
                f"{result.config.name}: {digest.gap_analysis_error}"
            )
        else:
            console.print(f"[green]fixed[/green] {result.config.name}@{digest.installed_version}")
    if failed:
        raise typer.Exit(code=1)


@app.command()
def chat() -> None:
    """Lightweight terminal REPL grounded in vendor digests."""
    _not_implemented("chat")


if __name__ == "__main__":
    app()
