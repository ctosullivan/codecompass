"""Phase 83 — Semantic Change Assurance: maintainer-only change-impact
assessment CLI, reusing Phase 82's oracle machinery and the existing
knowledge-record Evidence/Claim citation chains unchanged.

**Phase 88 relocation** (`planning/phase-88-agent-integration-mcp.md`
§1.1/§3.3): the actual logic now lives in the packaged, installed-
wheel-reachable `codecompass.change_impact` — this script is a thin CLI
wrapper over it, preserving every existing flag/behaviour exactly. Still
not a shipped `codecompass` subcommand itself (`planning/
v2-roadmap.md`'s own Phase 83 scoping) — the MCP-exposed equivalent is
`impact_classify_change` (Stage 88B), which calls the same packaged
module.

    python scripts/assess_change_impact.py \\
        --target-repo-root ~/projects/ledgerkit \\
        --slug balance-from-spec \\
        --changed ledgerkit/reports.py:644-668 \\
        [--target-graph-db PATH] [--knowledge-root PATH] [--run-checks]

Four distinct roots, never conflated (plan §7, governing prompt §6):
`--target-repo-root` (the checkout under assessment), `--target-graph-db`
(defaults to `<target-repo-root>/context-graph.db` -- the *target's own*
graph, never CodeCompass's self-referential one), `--knowledge-root`
(defaults to this CodeCompass checkout's own root, where
`planning/knowledge/`/`planning/contracts/` actually live), `--slug` (the
`planning/knowledge/<slug>/` directory to assess relevance against).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_src_path = ROOT / "src"
if str(_src_path) not in sys.path:
    sys.path.insert(0, str(_src_path))

from codecompass import change_impact as _ci  # noqa: E402

# ---------------------------------------------------------------------------
# Backward-compatible re-exports -- `tests/test_assess_change_impact.py`
# imports this script directly (not `codecompass.change_impact`) and
# calls these by these exact names. The packaged module keeps every
# original signature unchanged, including each function's own explicit
# `oracle_mod` dependency-injection parameter (see `change_impact.
# resolve_changed_range`'s own docstring) -- so a plain re-export is
# sufficient; no shim logic is needed here.
# ---------------------------------------------------------------------------

ChangedRange = _ci.ChangedRange
SymbolRow = _ci.SymbolRow
compute_symbol_spans = _ci.compute_symbol_spans
resolve_intersecting_symbols = _ci.resolve_intersecting_symbols
resolve_changed_range = _ci.resolve_changed_range
classify_symbol = _ci.classify_symbol
run_check_assurance = _ci.run_check_assurance
assess = _ci.assess
render_text_report = _ci.render_text_report


def parse_changed_arg(raw: str) -> _ci.ChangedRange:
    try:
        return _ci.parse_changed_arg(raw)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(str(exc)) from exc


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--target-repo-root", type=Path, required=True)
    parser.add_argument("--target-graph-db", type=Path, default=None)
    parser.add_argument("--knowledge-root", type=Path, default=ROOT)
    parser.add_argument("--slug", required=True)
    parser.add_argument("--changed", type=parse_changed_arg, action="append", default=[])
    parser.add_argument("--run-checks", action="store_true")
    parser.add_argument(
        "--json", action="store_true", help="print the machine-readable report only"
    )
    args = parser.parse_args()

    target_graph_db = args.target_graph_db or (args.target_repo_root / "context-graph.db")
    if not args.changed:
        print("error: at least one --changed path:start-end is required", file=sys.stderr)
        return 2

    report = _ci.assess(
        target_repo_root=args.target_repo_root,
        target_graph_db=target_graph_db,
        knowledge_root=args.knowledge_root,
        slug=args.slug,
        changed=args.changed,
        run_checks=args.run_checks,
    )
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(_ci.render_text_report(report))
        print("\n--- JSON ---")
        print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
