"""codecompass CLI entry point.

Bare `codecompass` (no subcommand) runs the zero-question Phase A
bootstrap (decisions/0017) and then, if usage-proven enrichment
candidates exist, an auto-triggered but disclosed/confirmable Phase B
(decisions/0031, decisions/0033). `init`, `sync`, `index`, `check`,
`query`, and `chat` are all implemented — see docs/cli-reference.md.
`promote` was removed in Phase 15 (decisions/0033): its three former jobs
(clone, enrich, generate Skill) are now automatic outcomes of
bootstrap/`sync`.
"""

from __future__ import annotations

import json
import re
import sqlite3
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from codecompass import enrichment, graph, relation_enrichment
from codecompass.adapters import AdapterError
from codecompass.chat import ChatError, run_chat
from codecompass.commands import write_discovery_command
from codecompass.config import ConfigError, load_vendor_config
from codecompass.core import VendorConfig
from codecompass.discovery import (
    DiscoveryError,
    append_vendor_toml,
    discover_all,
    discover_manifest_paths,
    write_vendor_toml,
)
from codecompass.index import (
    _MARKER_BLOCK_RE,
    load_routing_rows,
    render_routing_table,
    update_root_claude_md,
)
from codecompass.skill import _TOOL_SKILL_DIR_NAME, write_tool_skill
from codecompass.source_resolution import rmtree_best_effort
from codecompass.staleness import Severity, VendorStaleness, check_all
from codecompass.sync import rebuild_project_graph, sync_all, sync_vendor

app = typer.Typer(
    help="Grounded, version-pinned dependency reference docs for AI coding agents."
)
query_app = typer.Typer(help="Query the context graph (context-graph.db).")
app.add_typer(query_app, name="query")
console = Console()

_STRICT_FAIL_SEVERITIES = {Severity.MAJOR, Severity.UNKNOWN}
_GRAPH_DB_FILENAME = "context-graph.db"
_NO_GRAPH_NOTE = "no context-graph.db yet — run `codecompass sync` first"


def _load_config(path: Path = Path("vendor.toml")) -> list[VendorConfig]:
    """Load and validate vendor.toml, exiting with a clear message on failure."""
    try:
        return load_vendor_config(path)
    except ConfigError as exc:
        console.print(f"[red]error:[/red] {exc}")
        raise typer.Exit(code=1) from exc


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    yes: bool = typer.Option(
        False, "--yes", help="Skip Phase B's (AI enrichment) confirmation prompt."
    ),
    budget: float | None = typer.Option(
        None,
        "--budget",
        help="Cap estimated Phase B enrichment spend (USD) for this run; aborts "
        "before any API call if the estimate exceeds it. Omit for no cap.",
    ),
) -> None:
    """With no subcommand: Phase A bootstrap (decisions/0017) —
    auto-discovers manifests, writes/refreshes vendor.toml, clones every
    vendor's source, and regenerates trees + the routing table + the
    tool-level Skill. No prompts, no AI calls. If Phase A's context-graph
    rebuild finds usage-proven vendors eligible for AI enrichment, Phase B
    (decisions/0031) auto-triggers right after — cost-disclosed and
    confirmed (`--yes` skips the prompt; `--budget` caps spend).
    """
    if ctx.invoked_subcommand is not None:
        return
    _bootstrap(Path.cwd(), yes=yes, budget=budget)


def _bootstrap(project_root: Path, *, yes: bool, budget: float | None) -> None:
    vendor_toml = project_root / "vendor.toml"
    try:
        discovered = discover_all(discover_manifest_paths(project_root))
    except DiscoveryError as exc:
        console.print(f"[red]error:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    if vendor_toml.exists():
        existing_names = {c.name for c in load_vendor_config(vendor_toml)}
        new_configs = [
            VendorConfig(name=name, ecosystem=ecosystem)
            for ecosystem, names in discovered.items()
            for name in names
            if name not in existing_names
        ]
        append_vendor_toml(new_configs, vendor_toml)
    else:
        write_vendor_toml(discovered, vendor_toml)
        new_configs = load_vendor_config(vendor_toml)

    # Only newly-discovered vendors are synced here — an already-tracked
    # vendor's generated output is left untouched by a bare-command
    # refresh, so Phase A never pays AI cost (decisions/0017).
    if new_configs:
        sync_all(new_configs, project_root)

    all_configs = load_vendor_config(vendor_toml)
    # Only the graph rebuild happens here, pre-enrichment — it must exist
    # before `enrichment.select_candidates` can read usage-proven
    # candidates from it. The routing table/tool Skill/discovery command
    # are regenerated post-enrichment instead (`_refresh_generated_artifacts`
    # below) so they reflect this run's enrichment, not the state before it
    # (planning/phase-20-refresh-generated-artifacts-after-enrichment.md).
    rebuild_project_graph(all_configs, project_root)

    console.print(
        f"[green]bootstrapped[/green] {vendor_toml} — {len(all_configs)} vendor(s) "
        f"tracked, {len(new_configs)} newly discovered"
    )

    try:
        _maybe_run_enrichment(project_root, all_configs, yes=yes, budget=budget)
    finally:
        # Unconditional, success or budget-abort (`typer.Exit` from
        # `_maybe_run_enrichment`) — the routing table/tool Skill/graph are
        # always left in a consistent, freshly-generated state after any
        # invocation (phase-20 plan's Design decisions).
        _refresh_generated_artifacts(project_root, all_configs)


def _maybe_run_enrichment(
    project_root: Path, configs: list[VendorConfig], *, yes: bool, budget: float | None
) -> None:
    """Phase B: usage-driven AI enrichment, auto-triggered right after
    Phase A's free work (decisions/0033) — the literal mechanism behind
    `decisions/0033`'s "Phase A's zero-question guarantee is preserved for
    Phase A specifically; Phase B keeps a real consent gate." A no-op if
    neither `enrichment.select_candidates` nor `relation_enrichment.
    select_candidates` finds anything eligible. Budget is checked *before*
    the confirmation prompt — no point asking a human to confirm a run
    that's already going to be refused on cost grounds.

    Phase 22 folds spec-doc relationship enrichment (`relation_
    enrichment`) into this same call: both candidate sets are selected up
    front, their combined cost is disclosed once, and one confirm/`--yes`/
    `--budget` gate covers both — not a second separate prompt (see the
    phase plan's Covered list). Relationship candidates are selected
    *before* this run's own vendor enrichment is applied below, so a
    vendor being enriched for the very first time in this same invocation
    grounds any relationship mentioning it in whatever that vendor's
    digest said before this run started, not the freshly-generated one —
    accepted: the next sync's candidates re-derive from the newer content
    once it exists.
    """
    conn = graph.open_graph(project_root)
    try:
        candidates = enrichment.select_candidates(conn, configs, project_root)
        relation_candidates = relation_enrichment.select_candidates(conn, project_root)
        if not candidates and not relation_candidates:
            return

        batch_count = len(enrichment.plan_batches(candidates))
        relation_batch_count = len(relation_enrichment.plan_batches(relation_candidates))
        estimated = enrichment.estimate_cost(batch_count, relation_batch_count)
        vendor_names = ", ".join(c.vendor.name for c in candidates) or "(none)"
        console.print(
            f"[yellow]enrichment[/yellow] will make ~{batch_count + relation_batch_count} "
            f"AI call(s) (~${estimated:.2f}) using claude-haiku-4-5-20251001 to describe "
            f"{len(candidates)} vendor(s): {vendor_names}, and "
            f"{len(relation_candidates)} relationship(s)"
        )

        try:
            enrichment.check_budget(candidates, budget, relation_candidates=relation_candidates)
        except enrichment.EnrichmentError as exc:
            console.print(f"[red]error:[/red] {exc}")
            raise typer.Exit(code=1) from exc

        if not yes and not typer.confirm("Proceed?"):
            console.print("[yellow]enrichment skipped[/yellow]")
            return

        results = enrichment.run_enrichment_batches(candidates)
        enrichment.apply_results(conn, project_root, results)

        relation_results = relation_enrichment.run_enrichment_batches(relation_candidates)
        relation_enrichment.apply_results(conn, relation_results)

        console.print(
            f"[green]enriched[/green] {len(results)} vendor(s), "
            f"{len(relation_results)} relationship(s)"
        )
    finally:
        conn.close()


def _refresh_generated_artifacts(project_root: Path, configs: list[VendorConfig]) -> None:
    """Re-run the graph rebuild plus everything derived from it — the
    routing table, the tool-level Skill, and the discovery command —
    called once, unconditionally, at the very end of both `_bootstrap` and
    `sync`'s whole-project branch, *after* `_maybe_run_enrichment` returns
    (success or budget-abort). Closes two gaps
    (planning/phase-20-refresh-generated-artifacts-after-enrichment.md):
    the routing table/tool Skill otherwise reflect pre-enrichment state
    for a vendor enriched in this same invocation, and `sync`'s
    whole-project branch never refreshed them at all. A second full
    `rebuild_project_graph` pass, not a lighter targeted update — see that
    plan's Design decisions for why: `graph.rebuild_deterministic` is a
    deliberate wipe-and-rewrite transaction with no partial-update mode,
    and the redundant pass is deterministic and free (no AI call).
    """
    rebuild_project_graph(configs, project_root)
    rows = load_routing_rows(configs, project_root)
    update_root_claude_md(project_root, render_routing_table(rows))
    write_tool_skill(project_root, configs)
    write_discovery_command(project_root)


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
    `codecompass`'s auto-discovery (decisions/0017). Errors if vendor.toml
    already exists. Not a Phase A/B trigger point itself — unaffected by
    this phase's rewiring.
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
    yes: bool = typer.Option(
        False, "--yes", help="Skip Phase B's (AI enrichment) confirmation prompt."
    ),
    budget: float | None = typer.Option(
        None,
        "--budget",
        help="Cap estimated AI spend (USD) for this run — for a whole-project "
        "sync, Phase B enrichment; aborts before any API call if the "
        "estimate exceeds it. Omit for no cap. No effect on `sync <vendor>` "
        "(single-vendor), which never triggers Phase B (decisions/0025).",
    ),
) -> None:
    """Regenerate digests and trees for one or all vendors. A whole-project
    sync (no vendor name) also rebuilds context-graph.db and, if usage-proven
    enrichment candidates exist, auto-triggers Phase B — same trigger bare
    `codecompass` gains (decisions/0033). `sync <vendor>` (single-vendor) is
    unaffected: no graph rebuild, no enrichment trigger (decisions/0025).
    """
    configs = _load_config()
    if vendor is not None:
        configs = [c for c in configs if c.name == vendor]
        if not configs:
            console.print(f"[red]error:[/red] {vendor!r} not found in vendor.toml")
            raise typer.Exit(code=1)
    digests = sync_all(configs, Path.cwd())
    if vendor is None:
        # Whole-project sync only (decisions/0025) — `sync <vendor>` and
        # `check --fix`'s per-vendor loop leave the graph untouched.
        rebuild_project_graph(configs, Path.cwd())
        try:
            _maybe_run_enrichment(Path.cwd(), configs, yes=yes, budget=budget)
        finally:
            # Unconditional post-enrichment refresh — closes the gap where
            # a whole-project `sync` never regenerated the routing
            # table/tool Skill at all (planning/phase-20-refresh-
            # generated-artifacts-after-enrichment.md).
            _refresh_generated_artifacts(Path.cwd(), configs)
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
    write_discovery_command(Path.cwd())
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
        "as `sync`).",
    ),
) -> None:
    """Staleness gate comparing digests against installed versions, plus
    report-only context-graph coverage-gap sections (unused vendors,
    documented-but-unused/used-but-undocumented symbols, orphaned
    third-party skill mentions) if context-graph.db exists.

    With no flags, always exits 0 — a report-only table for a human
    running it locally. `--strict` and `--fix` are mutually exclusive.
    `--strict`'s exit code is governed by version-drift severity alone —
    none of the coverage-gap sections affect it.
    """
    if strict and fix:
        console.print("[red]error:[/red] --strict and --fix are mutually exclusive")
        raise typer.Exit(code=1)

    configs = _load_config()
    results = check_all(configs, Path.cwd())
    console.print(_render_check_table(results))
    _print_coverage_gap_sections(Path.cwd())

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


def _open_graph_or_note(project_root: Path) -> sqlite3.Connection | None:
    """`None` (having already printed a one-line note) if context-graph.db
    doesn't exist yet — the graceful-skip posture `query`'s subcommands and
    `check`'s coverage-gap sections both use, rather than a traceback from
    trying to query tables that don't exist, or silently creating a fresh
    empty db as a side effect of a read-only command.
    """
    db_path = project_root / _GRAPH_DB_FILENAME
    if not db_path.exists():
        console.print(f"[yellow]{_NO_GRAPH_NOTE}[/yellow]")
        return None
    return graph.open_graph(project_root)


def _print_coverage_gap_sections(project_root: Path) -> None:
    conn = _open_graph_or_note(project_root)
    if conn is None:
        return
    try:
        _print_name_list_table("Unused vendors", graph.unused_vendors(conn))
        _print_pair_table("Documented but unused", graph.documented_but_unused(conn))
        _print_pair_table("Used but undocumented", graph.used_but_undocumented(conn))
        orphaned_skills = [
            entry["path"]
            for entry in graph.skills_index(conn)
            if entry["origin"] == "third_party"
            and not entry["mentions_vendors"]
            and not entry["mentions_source_files"]
        ]
        _print_name_list_table(
            "Third-party skill mentions with no backing vendor/symbol", orphaned_skills
        )
        _print_name_list_table(
            "Spec docs with no detected relations", graph.spec_docs_without_relations(conn)
        )
        _print_name_list_table(
            "Vendor docs with no detected relations", graph.vendor_docs_without_relations(conn)
        )
    finally:
        conn.close()


def _print_name_list_table(title: str, names: list[str]) -> None:
    # The section heading prints as plain text, not `Table(title=...)` —
    # Rich wraps a table's title to the table's own (content-driven) box
    # width, which can split a multi-word heading mid-word for a narrow,
    # short-content table like these.
    console.print(f"[bold]{title}[/bold]")
    table = Table("Name")
    for name in names:
        table.add_row(name)
    if not names:
        table.add_row("[dim](none)[/dim]")
    console.print(table)


def _print_pair_table(title: str, pairs: list[tuple[str, str]]) -> None:
    console.print(f"[bold]{title}[/bold]")
    table = Table("Vendor", "Symbol")
    for vendor_name, symbol_name in pairs:
        table.add_row(vendor_name, symbol_name)
    if not pairs:
        table.add_row("[dim](none)[/dim]", "")
    console.print(table)


@query_app.command("vendors")
def query_vendors(
    unused: bool = typer.Option(
        False, "--unused", help="List only vendors with no detected usage anywhere."
    ),
    json_output: bool = typer.Option(
        False, "--json", help="Raw JSON instead of a Rich table."
    ),
) -> None:
    """Every tracked vendor's usage/enrichment status, from the context graph."""
    conn = _open_graph_or_note(Path.cwd())
    if conn is None:
        return
    try:
        unused_names = set(graph.unused_vendors(conn))
        rows = conn.execute(
            "SELECT name, ecosystem, installed_version FROM vendors ORDER BY name"
        ).fetchall()
        results = []
        for name, ecosystem, installed_version in rows:
            if unused and name not in unused_names:
                continue
            results.append(
                {
                    "name": name,
                    "ecosystem": ecosystem,
                    "installed_version": installed_version,
                    "used": name not in unused_names,
                    "enriched": graph.has_enrichment(conn, name),
                }
            )
        if json_output:
            console.print(json.dumps(results, indent=2), soft_wrap=True)
            return
        table = Table("Vendor", "Ecosystem", "Version", "Used", "Enriched")
        for r in results:
            table.add_row(
                r["name"],
                r["ecosystem"],
                r["installed_version"] or "_unknown_",
                "yes" if r["used"] else "no",
                "yes" if r["enriched"] else "no",
            )
        console.print(table)
    finally:
        conn.close()


@query_app.command("vendor")
def query_vendor(
    name: str = typer.Argument(..., help="Vendor name to look up."),
    json_output: bool = typer.Option(
        False, "--json", help="Raw JSON instead of a Rich table."
    ),
) -> None:
    """One vendor's full profile: symbols, usage count, documenting
    artifacts, routed Skills, and its `depends_on` vendors.
    """
    conn = _open_graph_or_note(Path.cwd())
    if conn is None:
        return
    try:
        profile = graph.vendor_profile(conn, name)
        if profile is None:
            console.print(f"[red]error:[/red] {name!r} not found in context-graph.db")
            raise typer.Exit(code=1)
        if json_output:
            console.print(json.dumps(profile, indent=2), soft_wrap=True)
            return
        vendor = profile["vendor"]
        console.print(
            f"[bold]{vendor['name']}[/bold] ({vendor['ecosystem']}) "
            f"{vendor['installed_version'] or '_unknown_'} — "
            f"usage count: {profile['usage_count']}"
        )
        # Section headings print as plain text, not `Table(title=...)` —
        # see `_print_name_list_table`'s comment on why.
        console.print("[bold]Symbols[/bold]")
        symbols_table = Table("Symbol", "Purpose")
        for symbol in profile["symbols"]:
            symbols_table.add_row(symbol["name"], symbol["purpose"] or "")
        console.print(symbols_table)
        console.print("[bold]Documenting artifacts[/bold]")
        docs_table = Table("Path", "Kind")
        for doc in profile["documenting_artifacts"]:
            docs_table.add_row(doc["path"], doc["kind"])
        console.print(docs_table)
        console.print("[bold]Routed Skills[/bold]")
        skills_table = Table("Path")
        for skill in profile["routed_skills"]:
            skills_table.add_row(skill["path"])
        console.print(skills_table)
        console.print("[bold]Used at[/bold]")
        used_at_table = Table("File", "Line")
        for u in profile["used_at"]:
            line = str(u["line"]) if u["line"] is not None else ""
            used_at_table.add_row(u["source_file_path"], line)
        console.print(used_at_table)
        console.print(f"Depends on: {', '.join(profile['depends_on']) or '(none)'}")
    finally:
        conn.close()


@query_app.command("symbol")
def query_symbol(
    name: str = typer.Argument(..., help="Symbol name to look up (across all vendors)."),
    json_output: bool = typer.Option(
        False, "--json", help="Raw JSON instead of a Rich table."
    ),
) -> None:
    """Every symbol named `name`, across every vendor — symbol names aren't
    globally unique.
    """
    conn = _open_graph_or_note(Path.cwd())
    if conn is None:
        return
    try:
        profiles = graph.symbol_profile(conn, name)
        if json_output:
            console.print(json.dumps(profiles, indent=2), soft_wrap=True)
            return
        if not profiles:
            console.print(f"[yellow]no symbol named {name!r} found in context-graph.db[/yellow]")
            return
        table = Table("Vendor", "Purpose", "Usage count", "Documenting artifacts", "Used at")
        for profile in profiles:
            docs = ", ".join(doc["path"] for doc in profile["documenting_artifacts"]) or "(none)"
            used_at = (
                ", ".join(f"{u['source_file_path']}:{u['line']}" for u in profile["used_at"])
                or "(none)"
            )
            table.add_row(
                profile["vendor"],
                profile["purpose"] or "",
                str(profile["usage_count"]),
                docs,
                used_at,
            )
        console.print(table)
    finally:
        conn.close()


@query_app.command("skills")
def query_skills(
    unused_mentions: bool = typer.Option(
        False,
        "--unused-mentions",
        help="List only Skills/.mdc rules that mention no known vendor or source file.",
    ),
    json_output: bool = typer.Option(
        False, "--json", help="Raw JSON instead of a Rich table."
    ),
) -> None:
    """Every Skill/`.mdc` rule under the project, its origin, and what it
    mechanically mentions.
    """
    conn = _open_graph_or_note(Path.cwd())
    if conn is None:
        return
    try:
        index_rows = graph.skills_index(conn)
        if unused_mentions:
            index_rows = [
                entry
                for entry in index_rows
                if not entry["mentions_vendors"] and not entry["mentions_source_files"]
            ]
        if json_output:
            console.print(json.dumps(index_rows, indent=2), soft_wrap=True)
            return
        table = Table("Path", "Name", "Origin", "Mentions vendors", "Mentions files")
        for entry in index_rows:
            table.add_row(
                entry["path"],
                entry["name"] or "",
                entry["origin"] or "",
                ", ".join(entry["mentions_vendors"]) or "(none)",
                str(len(entry["mentions_source_files"])),
            )
        console.print(table)
    finally:
        conn.close()


def _incoming_doc_relations(conn: sqlite3.Connection, column: str, value: int) -> list[dict]:
    """Reverse lookup for `_resolve_relations`'s vendor-name/doc-artifact-
    name branches: every spec doc whose `doc_relations_edges` row targets
    `value` via `column` (always one of this function's own two fixed
    literal column names below, never external input). Shaped like
    `graph.doc_relations`'s own per-row dicts (`relation_kind`, plus
    which "other" thing is on the far end) so `query_relations` can render
    both directions the same way.
    """
    return [
        {"relation_kind": relation_kind, "source_doc_artifact_path": path}
        for path, relation_kind in conn.execute(
            f"""
            SELECT da.path, dre.relation_kind
            FROM doc_relations_edges dre
            JOIN doc_artifacts da ON dre.source_doc_artifact_id = da.id
            WHERE dre.{column} = ?
            ORDER BY da.path
            """,
            (value,),
        )
    ]


def _relation_ai_summary(
    conn: sqlite3.Connection,
    source_doc_path: str,
    target_vendor_name: str | None,
    target_doc_path: str | None,
) -> str | None:
    """The cached `ai_summary` for one relationship, keyed by the exact
    natural-key triple `doc_relation_enrichment` uses (Phase 22) — `None`
    if Phase B enrichment hasn't produced one yet for this relationship
    (or ever will, if it isn't usage-proven). Ignores `content_hash`
    entirely: display only cares whether *some* summary is cached —
    staleness is `relation_enrichment.select_candidates`'s concern, not
    this read's, mirroring `graph.has_enrichment`'s same two-state posture
    for vendors. Resolved directly here with ad hoc SQL, the same
    "CLI-specific shape" precedent `_incoming_doc_relations` above already
    set, rather than a new `graph.py` function.
    """
    row = conn.execute(
        """
        SELECT ai_summary FROM doc_relation_enrichment
        WHERE source_doc_path = ?
          AND target_vendor_name IS ?
          AND target_doc_path IS ?
        """,
        (source_doc_path, target_vendor_name, target_doc_path),
    ).fetchone()
    return row[0] if row is not None else None


def _resolve_relations(conn: sqlite3.Connection, name: str) -> list[dict] | None:
    """Resolves `query relations <name>`'s three accepted shapes, tried in
    order: a spec-doc path (its own outgoing `doc_relations_edges` rows,
    via `graph.doc_relations`), a vendor name, or any other doc artifact's
    `name` field (a Skill's frontmatter name, a dependency doc's
    `f"{vendor} CLAUDE.md"`-style name) — the latter two are incoming
    lookups: which spec docs mechanically mention it. `None` if `name`
    matches nothing in the graph at all. Each returned dict gets an
    `ai_summary` key (Phase 22) attached here — `None` if this exact
    relationship hasn't been AI-enriched yet.
    """
    if conn.execute("SELECT 1 FROM doc_artifacts WHERE path = ?", (name,)).fetchone():
        relations = graph.doc_relations(conn, name)
        for r in relations:
            r["ai_summary"] = _relation_ai_summary(
                conn, name, r["target_vendor"], r["target_doc_artifact_path"]
            )
        return relations

    vendor_row = conn.execute("SELECT id FROM vendors WHERE name = ?", (name,)).fetchone()
    if vendor_row is not None:
        relations = _incoming_doc_relations(conn, "target_vendor_id", vendor_row[0])
        for r in relations:
            r["ai_summary"] = _relation_ai_summary(
                conn, r["source_doc_artifact_path"], name, None
            )
        return relations

    artifact_rows = conn.execute(
        "SELECT id, path FROM doc_artifacts WHERE name = ?", (name,)
    ).fetchall()
    if artifact_rows:
        results: list[dict] = []
        for artifact_id, artifact_path in artifact_rows:
            relations = _incoming_doc_relations(conn, "target_doc_artifact_id", artifact_id)
            for r in relations:
                r["ai_summary"] = _relation_ai_summary(
                    conn, r["source_doc_artifact_path"], None, artifact_path
                )
            results.extend(relations)
        return results

    return None


@query_app.command("relations")
def query_relations(
    name: str = typer.Argument(
        ..., help="A spec-doc path, a vendor name, or a Skill/doc-artifact name."
    ),
    json_output: bool = typer.Option(
        False, "--json", help="Raw JSON instead of a Rich table."
    ),
) -> None:
    """What a spec doc mechanically mentions (given its path — a vendor or
    another doc artifact), or which spec docs mechanically mention a
    vendor/Skill (given its name) — `doc_relations_edges`, Phase 21's
    mechanical spec-doc <-> dependency-doc <-> Skill web. Each relation
    shows its AI-enriched `ai_summary` (Phase 22, `doc_relation_
    enrichment`) when one has been generated, else "mentioned, not yet
    enriched" — the same two-state display `query vendor` already uses
    for `has_enrichment`. Also shows a "Package code" trace (Phase 30,
    `graph.doc_code_trace`): real project-source usage sites for whatever
    `name` mechanically mentions or documents, or its own usage sites if
    `name` is a vendor. `--json` output is `{"relations": [...],
    "package_code": [...]}`, not a bare list — the two are different
    shapes (a relation vs. a usage site) that don't merge into one row.
    """
    conn = _open_graph_or_note(Path.cwd())
    if conn is None:
        return
    try:
        relations = _resolve_relations(conn, name)
        if relations is None:
            console.print(f"[red]error:[/red] {name!r} not found in context-graph.db")
            raise typer.Exit(code=1)
        package_code = graph.doc_code_trace(conn, name)
        if json_output:
            console.print(
                json.dumps({"relations": relations, "package_code": package_code}, indent=2),
                soft_wrap=True,
            )
            return
        table = Table("Relation", "Other")
        table.add_column("AI summary", no_wrap=True)
        for r in relations:
            other = (
                r.get("source_doc_artifact_path")
                or r.get("target_vendor")
                or r.get("target_doc_artifact_path")
                or ""
            )
            table.add_row(
                r["relation_kind"], other, r.get("ai_summary") or "mentioned, not yet enriched"
            )
        if not relations:
            table.add_row("[dim](none)[/dim]", "", "")
        console.print(table)
        console.print("[bold]Package code[/bold]")
        trace_table = Table("Vendor", "Symbol", "File", "Line", "Via")
        for t in package_code:
            trace_table.add_row(
                t["vendor"],
                t["symbol"] or "",
                t["source_file_path"],
                str(t["line"]) if t["line"] is not None else "",
                t["via"],
            )
        console.print(trace_table)
    finally:
        conn.close()


@app.command()
def chat(
    vendor: str = typer.Argument(..., help="Vendor name to chat about."),
) -> None:
    """Terminal REPL grounded in one vendor's already-generated digest —
    `vendor/<name>/CLAUDE.md`, plus `OVERVIEW.md` if enriched. Never
    regenerates anything (decisions/0023): works whether or not the vendor
    has been AI-enriched yet, with a thinner grounding + a `sync` hint for
    a vendor with no grounded description yet.
    """
    configs = _load_config()
    matches = [c for c in configs if c.name == vendor]
    if not matches:
        console.print(f"[red]error:[/red] {vendor!r} not found in vendor.toml")
        raise typer.Exit(code=1)
    try:
        run_chat(matches[0], Path.cwd(), console)
    except ChatError as exc:
        console.print(f"[red]error:[/red] {exc}")
        raise typer.Exit(code=1) from exc


@app.command()
def undo(
    yes: bool = typer.Option(False, "--yes", help="Skip the confirmation prompt."),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Print what would be removed, without deleting anything."
    ),
) -> None:
    """Best-effort cleanup of everything codecompass generated in this
    project (`decisions/0036`): every tracked vendor's `vendor/<name>/`
    directory, `vendor.toml`, `context-graph.db`, every codecompass-
    generated Skill/`.mdc`/slash-command artifact, and the root
    `CLAUDE.md` routing-table marker block (stripped in place — the file
    itself, and any hand-written content around the block, is left
    untouched). Never removes a hand-written or third-party Skill/`.mdc`
    file, and never runs a git command of any kind — plain filesystem
    operations only; committing the result is left entirely to you.

    Two enumeration strategies depending on whether `context-graph.db`
    exists yet: the precise graph-backed one (every `doc_artifacts` row
    tagged `codecompass_tool`/`codecompass_vendor`, never `third_party`),
    or a pattern-based fallback for a project that hasn't run a
    whole-project sync yet. See docs/cli-reference.md.
    """
    project_root = Path.cwd()
    targets = _dedupe_contained(_codecompass_generated_paths(project_root))

    claude_md_path = project_root / "CLAUDE.md"
    stripped_claude_md: str | None = None
    if claude_md_path.exists():
        stripped_claude_md = _strip_routing_table_block(
            claude_md_path.read_text(encoding="utf-8")
        )

    if not targets and stripped_claude_md is None:
        console.print("[yellow]nothing to undo[/yellow]")
        return

    console.print("[bold]codecompass undo[/bold] would remove:")
    for target in targets:
        suffix = "/" if target.is_dir() else ""
        console.print(f"  {target.relative_to(project_root).as_posix()}{suffix}")
    if stripped_claude_md is not None:
        console.print("  CLAUDE.md (strip the codecompass routing-table block only)")

    if dry_run:
        return

    if not yes and not typer.confirm("Proceed?"):
        console.print("[yellow]undo skipped[/yellow]")
        return

    leftovers: list[Path] = []
    for target in targets:
        if target.is_dir():
            if not rmtree_best_effort(target):
                leftovers.append(target)
        elif target.exists():
            try:
                target.unlink()
            except OSError:
                leftovers.append(target)
    if stripped_claude_md is not None:
        claude_md_path.write_text(stripped_claude_md, encoding="utf-8")

    if leftovers:
        console.print(
            "[yellow]undo finished, but could not fully remove:[/yellow]"
        )
        for leftover in leftovers:
            console.print(f"  {leftover.relative_to(project_root).as_posix()}")
    else:
        console.print("[green]undo complete[/green]")


def _codecompass_generated_paths(project_root: Path) -> set[Path]:
    """Every path `undo` should remove, before de-duplication. Two mutually
    exclusive enumeration strategies, chosen by whether `context-graph.db`
    exists:

    - **Graph available:** every `doc_artifacts` row tagged
      `codecompass_tool`/`codecompass_vendor` (`third_party` is never
      selected — by construction, not a filter applied after the fact),
      resolved to a real path, plus every tracked vendor's `vendor/<name>/`
      directory (`_graph_backed_undo_paths`).
    - **No graph yet:** a pattern-based fallback matching the exact
      generated-name conventions `skill.py`/`commands.py` use
      (`_fallback_undo_paths`) — less precise (can't distinguish a
      hand-renamed third-party Skill that happens to match), but functional
      without requiring a prior whole-project sync.

    Always, regardless of path: `vendor.toml` and `context-graph.db`
    themselves, if present.
    """
    targets: set[Path] = set()
    db_path = project_root / _GRAPH_DB_FILENAME
    if db_path.exists():
        conn = graph.open_graph(project_root)
        try:
            targets |= _graph_backed_undo_paths(conn, project_root)
        finally:
            conn.close()
    else:
        targets |= _fallback_undo_paths(project_root)

    vendor_toml = project_root / "vendor.toml"
    if vendor_toml.exists():
        targets.add(vendor_toml)
    if db_path.exists():
        targets.add(db_path)
    return targets


def _graph_backed_undo_paths(conn: sqlite3.Connection, project_root: Path) -> set[Path]:
    """`origin IN ('codecompass_tool', 'codecompass_vendor')` — the CHECK
    constraint on `doc_artifacts.origin` only ever allows those two values
    plus `third_party`, so this is an exact match on "starts with
    codecompass_", not a `LIKE` pattern.
    """
    targets: set[Path] = set()
    for path, kind in conn.execute(
        "SELECT path, kind FROM doc_artifacts "
        "WHERE origin IN ('codecompass_tool', 'codecompass_vendor')"
    ):
        resolved = project_root / path
        # A Skill's doc_artifacts row points at its SKILL.md, but the
        # generated artifact skill.py actually writes is the whole Skill
        # directory (SKILL.md plus a references/ subdir for a per-vendor
        # Skill) — remove the directory, not just the one file, or
        # references/*.md would be left orphaned behind an otherwise-deleted
        # Skill.
        targets.add(resolved.parent if kind == "skill" else resolved)
    for (vendor_name,) in conn.execute("SELECT name FROM vendors"):
        targets.add(project_root / "vendor" / vendor_name)
    return targets


def _fallback_undo_paths(project_root: Path) -> set[Path]:
    """Pattern-based enumeration for a project with no `context-graph.db`
    yet (e.g. only `init --scan` has run) — matches the exact naming
    conventions `skill.py`/`commands.py` use to generate these paths, never
    a broader glob that could sweep in a hand-written or third-party file.
    """
    targets: set[Path] = set()

    tool_skill_dir = project_root / ".claude" / "skills" / _TOOL_SKILL_DIR_NAME
    if tool_skill_dir.is_dir():
        targets.add(tool_skill_dir)
    targets |= set(project_root.glob(".claude/skills/codecompass-*"))
    targets |= set(project_root.glob(".cursor/rules/codecompass-*.mdc"))

    discovery_md = project_root / ".claude" / "commands" / "discovery.md"
    if discovery_md.exists():
        targets.add(discovery_md)

    try:
        configs = load_vendor_config(project_root / "vendor.toml")
    except ConfigError:
        configs = []
    for config in configs:
        targets.add(project_root / "vendor" / config.name)

    return targets


def _dedupe_contained(paths: set[Path]) -> list[Path]:
    """Drop any path that's a strict descendant of another path already in
    the set (e.g. `vendor/<name>/CLAUDE.md` once `vendor/<name>/` itself is
    already slated for removal) — `rmtree`ing the ancestor directory already
    removes it, so listing/deleting it again separately would just be
    redundant. Shallowest paths first, so an ancestor is always recorded
    before a descendant is checked against it.
    """
    ordered = sorted(paths, key=lambda p: len(p.parts))
    kept: list[Path] = []
    for path in ordered:
        if not any(path == k or k in path.parents for k in kept):
            kept.append(path)
    return sorted(kept)


def _strip_routing_table_block(text: str) -> str | None:
    """`None` if `text` has no codecompass marker block to strip (nothing
    to change). Otherwise the block is removed and the blank-line gap it
    leaves behind is collapsed — `index.py`'s `update_root_claude_md`'s own
    `_MARKER_BLOCK_RE`-based insertion logic, run in reverse. Hand-written
    content before/after the block is untouched either way.
    """
    if not _MARKER_BLOCK_RE.search(text):
        return None
    stripped = _MARKER_BLOCK_RE.sub("", text)
    return re.sub(r"\n{3,}", "\n\n", stripped)


if __name__ == "__main__":
    app()
