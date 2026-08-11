"""depcompass CLI entry point.

Bare `depcompass` (no subcommand) runs the zero-question bootstrap
(decisions/0017). `init`, `sync`, `index`, `check`, and `promote` are
implemented (Phases 4-7). `chat` is still a stub — see
docs/cli-reference.md for the planned surface and the roadmap phase its
real logic lands in.
"""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from depcompass.adapters import AdapterError
from depcompass.config import ConfigError, load_vendor_config
from depcompass.core import Depth, VendorConfig
from depcompass.discovery import (
    DiscoveryError,
    append_vendor_toml,
    discover_all,
    discover_manifest_paths,
    rewrite_vendor_toml,
    write_vendor_toml,
)
from depcompass.grounded_description import GroundedDescriptionError, estimate_cost
from depcompass.index import load_routing_rows, render_routing_table, update_root_claude_md
from depcompass.skill import write_cursor_mdc, write_tool_skill, write_vendor_skill
from depcompass.staleness import Severity, VendorStaleness, check_all
from depcompass.sync import sync_all, sync_vendor

app = typer.Typer(
    help="Grounded, version-pinned dependency reference docs for AI coding agents."
)
console = Console()

_PHASE_BY_COMMAND = {
    "chat": 8,
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


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context) -> None:
    """With no subcommand: zero-question bootstrap (decisions/0017) —
    auto-discovers manifests, writes/refreshes vendor.toml at
    `depth = surface`, and regenerates trees + the routing table + the
    tool-level Skill. No prompts, no AI calls.
    """
    if ctx.invoked_subcommand is not None:
        return
    _bootstrap(Path.cwd())


def _bootstrap(project_root: Path) -> None:
    vendor_toml = project_root / "vendor.toml"
    try:
        discovered = discover_all(discover_manifest_paths(project_root))
    except DiscoveryError as exc:
        console.print(f"[red]error:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    if vendor_toml.exists():
        existing_names = {c.name for c in load_vendor_config(vendor_toml)}
        new_configs = [
            VendorConfig(name=name, ecosystem=ecosystem, depth=Depth.SURFACE)
            for ecosystem, names in discovered.items()
            for name in names
            if name not in existing_names
        ]
        append_vendor_toml(new_configs, vendor_toml)
    else:
        write_vendor_toml(discovered, vendor_toml)
        new_configs = load_vendor_config(vendor_toml)

    # Only newly-discovered (guaranteed depth=surface) vendors are synced
    # here — an already-tracked vendor's generated output is left
    # untouched by a bare-command refresh, including any already at
    # depth=full, so this command never pays AI cost (decisions/0017).
    if new_configs:
        sync_all(new_configs, project_root)

    all_configs = load_vendor_config(vendor_toml)
    rows = load_routing_rows(all_configs, project_root)
    update_root_claude_md(project_root, render_routing_table(rows))
    write_tool_skill(project_root, all_configs)

    console.print(
        f"[green]bootstrapped[/green] {vendor_toml} — {len(all_configs)} vendor(s) "
        f"tracked, {len(new_configs)} newly discovered"
    )


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
    """Bulk-discover dependencies from named manifests and write a draft
    vendor.toml — the explicit, scripted/CI-friendly synonym for bare
    `depcompass`'s auto-discovery (decisions/0017). Errors if vendor.toml
    already exists.
    """
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
        help="Cap estimated grounded-description spend (USD) for this run; aborts "
        "before any API call if the estimate exceeds it. Omit for no cap.",
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
    except GroundedDescriptionError as exc:
        console.print(f"[red]error:[/red] {exc}")
        raise typer.Exit(code=1) from exc
    failed = False
    for digest in digests:
        if digest.description_error:
            failed = True
            console.print(
                f"[yellow]synced (description failed)[/yellow] "
                f"{digest.config.name}@{digest.installed_version}: {digest.description_error}"
            )
        else:
            console.print(
                f"[green]synced[/green] {digest.config.name}@{digest.installed_version}"
            )
    if failed:
        raise typer.Exit(code=1)


@app.command()
def index() -> None:
    """Regenerate the routing table injected into the project's root
    CLAUDE.md, and the tool-level Skill (decisions/0020).
    """
    configs = _load_config()
    rows = load_routing_rows(configs, Path.cwd())
    update_root_claude_md(Path.cwd(), render_routing_table(rows))
    write_tool_skill(Path.cwd(), configs)
    console.print(f"[green]updated[/green] CLAUDE.md routing table ({len(rows)} vendors)")


@app.command()
def promote(
    vendor: str = typer.Argument(..., help="Vendor name to escalate to depth=full."),
    yes: bool = typer.Option(
        False, "--yes", help="Skip the confirmation prompt (for scripted use)."
    ),
) -> None:
    """Escalate one vendor to depth=full — the only command that costs
    money or asks anything (decisions/0018). Discloses estimated cost,
    then: resolves the vendor's upstream repository, generates a
    grounded description, generates its Skill and Cursor `.mdc` export,
    and refreshes the routing table. Safe to re-run on an already-full
    vendor — it regenerates in place rather than erroring.
    """
    vendor_toml = Path("vendor.toml")
    configs = _load_config(vendor_toml)
    if not any(c.name == vendor for c in configs):
        console.print(f"[red]error:[/red] {vendor!r} not found in vendor.toml")
        raise typer.Exit(code=1)

    estimated = estimate_cost(1)
    console.print(
        f"[yellow]promote[/yellow] will make ~1 AI call (~${estimated:.2f}) using "
        f"claude-haiku-4-5-20251001 to generate {vendor!r}'s grounded description."
    )
    if not yes and not typer.confirm("Proceed?"):
        console.print("aborted")
        raise typer.Exit(code=1)

    updated_configs = [
        replace(c, depth=Depth.FULL) if c.name == vendor else c for c in configs
    ]
    rewrite_vendor_toml(updated_configs, vendor_toml)
    promoted_config = next(c for c in updated_configs if c.name == vendor)

    try:
        digest = sync_vendor(promoted_config, Path.cwd())
    except AdapterError as exc:
        console.print(f"[red]error:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    write_vendor_skill(Path.cwd(), digest)
    write_cursor_mdc(Path.cwd(), digest)

    rows = load_routing_rows(updated_configs, Path.cwd())
    update_root_claude_md(Path.cwd(), render_routing_table(rows))
    write_tool_skill(Path.cwd(), updated_configs)

    if digest.description_error:
        console.print(
            f"[yellow]promoted (description failed)[/yellow] {vendor}: "
            f"{digest.description_error}"
        )
        raise typer.Exit(code=1)
    console.print(f"[green]promoted[/green] {vendor} to depth=full")


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
        "as `sync`, including grounded description for depth=full vendors).",
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
        if digest.description_error:
            failed = True
            console.print(
                f"[yellow]fixed (description failed)[/yellow] "
                f"{result.config.name}: {digest.description_error}"
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
