"""Phase 83 — Semantic Change Assurance: maintainer-only change-impact
assessment, reusing Phase 82's oracle machinery and the existing
knowledge-record Evidence/Claim citation chains unchanged.

See `planning/phase-83-semantic-change-assurance.md` (the full design)
and `decisions/0086`/`0087`/`0089` (the three corrective amendments this
implementation follows). This is a maintainer script, like
`scripts/run_balance_from_spec_oracle.py` -- not a shipped `codecompass`
subcommand (`planning/v2-roadmap.md`'s own Phase 83 scoping).

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

No new `context-graph.db` table, no first-party call-graph, no `git diff`
parser (plan §9's own exclusions) -- this module reads `source_files`/
`source_symbols` directly via `sqlite3`, and `oracle.py`/`knowledge_
intermediate.py` unmodified; it never writes to any of them.
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parent.parent

# Reused unchanged, not reimplemented -- the exact convention
# `scripts/check_contracts.py::_SOURCE_REF_WITH_SYMBOL_RE` already
# validates for an Evidence's own `source_ref`. Duplicated, not imported,
# matching this project's own established scripts/-duplicates-scripts/
# convention (`oracle.py`'s own module docstring states the same
# rationale for `scripts/` not being part of the installed package).
_SOURCE_REF_WITH_SYMBOL_RE = re.compile(
    r"^(?P<path>[^:]+):(?P<start>\d+)(?:-(?P<end>\d+))?\s+(?P<kind>def|class)\s+(?P<symbol>\w+)$"
)
_ID_PATTERN = re.compile(r"\b(OBS|EV|CL|DE|DEC|REQ)-[A-Z0-9]+-\d+\b")


def _extract_id_strings(value: str) -> list[str]:
    return [m.group(0) for m in _ID_PATTERN.finditer(value)]


def _unquote(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


def _normalize_source_path(path: str) -> str:
    """The `source_ref`/`--changed` path convention is always a relative,
    forward-slash path from the target repository's own root (`decisions/
    0089` §A) -- normalised, never filesystem-resolved, so a disposable
    scratch copy and the real checkout compare identically without either
    existing on disk at comparison time."""
    return PurePosixPath(path.strip()).as_posix()


def _load_codecompass_modules():
    src_path = ROOT / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    from codecompass import knowledge_intermediate as ki
    from codecompass import oracle

    return oracle, ki


@dataclass
class ChangedRange:
    path: str
    start: int
    end: int


def parse_changed_arg(raw: str) -> ChangedRange:
    """`path:start-end` or `path:line` (a single changed line)."""
    if ":" not in raw:
        raise argparse.ArgumentTypeError(
            f"--changed {raw!r}: expected 'path:start-end' or 'path:line'"
        )
    path, _, range_part = raw.rpartition(":")
    if not path:
        raise argparse.ArgumentTypeError(f"--changed {raw!r}: missing path before ':'")
    if "-" in range_part:
        start_s, _, end_s = range_part.partition("-")
    else:
        start_s = end_s = range_part
    try:
        start, end = int(start_s), int(end_s)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"--changed {raw!r}: start/end must be integers"
        ) from exc
    if start < 1 or end < start:
        raise argparse.ArgumentTypeError(
            f"--changed {raw!r}: start must be >= 1 and end >= start"
        )
    return ChangedRange(path=path, start=start, end=end)


# ---------------------------------------------------------------------------
# §5 -- revision consistency via source_files.content_hash (decisions/0086 §3),
# resolving every symbol whose own span intersects the range (decisions/0089 §B)
# ---------------------------------------------------------------------------


@dataclass
class SymbolRow:
    name: str
    kind: str
    line: int


def _load_file_row(graph_db: Path, path: str) -> tuple[int, str | None] | None:
    """Returns `(source_file_id, content_hash)` or `None` if `path` has no
    `source_files` row in this graph at all."""
    con = sqlite3.connect(f"file:{graph_db}?mode=ro", uri=True)
    try:
        row = con.execute(
            "SELECT id, content_hash FROM source_files WHERE path = ?", (path,)
        ).fetchone()
    finally:
        con.close()
    return tuple(row) if row is not None else None


def _load_symbols(graph_db: Path, source_file_id: int) -> list[SymbolRow]:
    con = sqlite3.connect(f"file:{graph_db}?mode=ro", uri=True)
    try:
        rows = con.execute(
            "SELECT name, kind, line FROM source_symbols "
            "WHERE source_file_id = ? ORDER BY line",
            (source_file_id,),
        ).fetchall()
    finally:
        con.close()
    return [SymbolRow(name=n, kind=k, line=line_) for n, k, line_ in rows]


@dataclass
class SymbolSpan:
    symbol: SymbolRow
    span_start: int
    span_end: int


def compute_symbol_spans(symbols: list[SymbolRow], line_count: int) -> list[SymbolSpan]:
    """Plan §5's own convention: a symbol's span runs from its own line to
    one less than the next symbol's line, or to the file's own last line
    for the last symbol. `symbols` must already be ordered by line."""
    spans: list[SymbolSpan] = []
    for i, sym in enumerate(symbols):
        span_end = symbols[i + 1].line - 1 if i + 1 < len(symbols) else line_count
        spans.append(SymbolSpan(symbol=sym, span_start=sym.line, span_end=span_end))
    return spans


def resolve_intersecting_symbols(
    symbols: list[SymbolRow], line_count: int, start: int, end: int
) -> list[SymbolSpan]:
    """Every symbol whose own span intersects `[start, end]` -- generalised
    from a single enclosing-symbol lookup (`decisions/0089` §B) to the full
    requested range, since a real changed range commonly crosses more than
    one top-level declaration."""
    spans = compute_symbol_spans(symbols, line_count)
    return [s for s in spans if s.span_start <= end and s.span_end >= start]


def _describe_uncovered_lines(uncovered: list[int]) -> str:
    """Groups a sorted list of line numbers into contiguous sub-ranges for
    a human-readable "these specific lines are unmapped" reason -- never a
    silent drop of the gap (`decisions/0089` §B)."""
    parts: list[str] = []
    start = prev = uncovered[0]
    for n in uncovered[1:]:
        if n == prev + 1:
            prev = n
            continue
        parts.append(str(start) if start == prev else f"{start}-{prev}")
        start = prev = n
    parts.append(str(start) if start == prev else f"{start}-{prev}")
    return (
        f"line(s) {', '.join(parts)} within the requested range are not covered "
        "by any indexed top-level symbol's own span"
    )


@dataclass
class RangeResolution:
    changed: ChangedRange
    status: str  # "resolved" | "partially_resolved" | "stale_index" | "cannot_map"
    reason: str | None = None
    symbols: list[SymbolRow] = field(default_factory=list)


def resolve_changed_range(
    oracle_mod, target_repo_root: Path, graph_db: Path, changed: ChangedRange
) -> RangeResolution:
    live_path = target_repo_root / changed.path
    if not live_path.is_file():
        return RangeResolution(
            changed, "cannot_map", reason=f"{changed.path!r} does not exist under {target_repo_root}"
        )
    if not graph_db.is_file():
        # Fail closed, never an uncaught sqlite3.OperationalError: a
        # missing/unreadable target graph is exactly as unusable for
        # revision-consistency purposes as a graph with no matching row.
        return RangeResolution(
            changed, "cannot_map", reason=f"target graph database {graph_db} does not exist or is unreadable"
        )
    file_row = _load_file_row(graph_db, changed.path)
    if file_row is None:
        return RangeResolution(
            changed, "cannot_map",
            reason=f"{changed.path!r} has no source_files row in {graph_db} -- not indexed",
        )
    source_file_id, recorded_hash = file_row
    live_hash = oracle_mod.sha256_file(live_path)
    if recorded_hash != live_hash:
        return RangeResolution(
            changed, "stale_index",
            reason=(
                f"live content_hash ({live_hash}) does not match the graph's own "
                f"recorded content_hash ({recorded_hash}) for {changed.path!r} -- "
                "the target graph was not re-synced against this exact content; "
                "source_symbols.line values cannot be trusted for this file"
            ),
        )
    line_count = len(live_path.read_text(encoding="utf-8", errors="replace").splitlines())
    if changed.start > line_count:
        return RangeResolution(
            changed, "cannot_map",
            reason=f"start={changed.start} is past {changed.path!r}'s own extent ({line_count} lines)",
        )
    if changed.end > line_count:
        return RangeResolution(
            changed, "cannot_map",
            reason=f"end={changed.end} is past {changed.path!r}'s own extent ({line_count} lines)",
        )
    symbols = _load_symbols(graph_db, source_file_id)
    matched = resolve_intersecting_symbols(symbols, line_count, changed.start, changed.end)
    if not matched:
        return RangeResolution(
            changed, "cannot_map",
            reason=(
                f"no indexed top-level symbol's span intersects lines "
                f"{changed.start}-{changed.end} in {changed.path!r}"
            ),
        )
    covered: set[int] = set()
    for span in matched:
        lo, hi = max(span.span_start, changed.start), min(span.span_end, changed.end)
        covered.update(range(lo, hi + 1))
    requested = set(range(changed.start, changed.end + 1))
    uncovered = sorted(requested - covered)
    matched_symbols = [s.symbol for s in matched]
    if uncovered:
        return RangeResolution(
            changed, "partially_resolved",
            reason=_describe_uncovered_lines(uncovered),
            symbols=matched_symbols,
        )
    return RangeResolution(changed, "resolved", symbols=matched_symbols)


# ---------------------------------------------------------------------------
# §3 -- three-tier relevance/coverage classification (decisions/0086 §1,
# corrected for source-path identity and validated test-evidence --
# decisions/0089 §A/§C)
# ---------------------------------------------------------------------------


@dataclass
class ClaimFinding:
    claim_id: str
    requirement_ids: list[str]
    tier: str  # "behavioural_risk" | "relevant_no_coverage_link"
    check_id: str | None = None


def _requirement_ids_depending_on(records, claim_id: str) -> list[str]:
    out = []
    for rec in records.values():
        if rec.kind != "requirement":
            continue
        if claim_id in _extract_id_strings(rec.fields.get("depends_on", "")):
            out.append(rec.record_id)
    return sorted(out)


def classify_symbol(
    records, contract, oracle_mod, symbol_name: str, source_path: str, knowledge_root: Path
) -> tuple[str, list[ClaimFinding]]:
    """§3.1/§3.2/§3.3. `records` is `knowledge_intermediate.load_slug_
    records`'s own return value -- read, never written. A `test_ref` is
    always resolved against `knowledge_root` (never the hardcoded
    CodeCompass checkout `ROOT`) -- the whole point of `--knowledge-root`
    being a distinct, explicit input (plan §7, governing prompt §6) is
    that canonical knowledge need not reside under the target repository,
    and a disposable demonstration may legitimately use its own,
    separate knowledge-root copy.

    `source_path` is the path of the file `symbol_name` was actually
    resolved in (the `--changed` range's own path) -- a citing Evidence's
    `source_ref` must match on **both** `symbol` and `path` (normalised),
    never on symbol name alone, so two first-party files declaring a
    same-named symbol never inherit each other's Evidence (`decisions/
    0089` §A)."""
    normalized_source_path = _normalize_source_path(source_path)
    citing_evidence_ids: set[str] = set()
    for rec in records.values():
        if rec.kind != "evidence" or rec.fields.get("evidence_kind") != "source":
            continue
        raw_ref = rec.fields.get("source_ref", "")
        if not raw_ref or raw_ref == "null":
            continue
        match = _SOURCE_REF_WITH_SYMBOL_RE.match(_unquote(raw_ref))
        if not match or match.group("symbol") != symbol_name:
            continue
        if _normalize_source_path(match.group("path")) != normalized_source_path:
            continue
        citing_evidence_ids.add(rec.record_id)

    if not citing_evidence_ids:
        return "no_recorded_relationship", []

    # test-kind Evidence -> check_id, via its own test_ref resolving to a
    # genuinely valid OracleResult for the live contract (decisions/0086
    # §1 -- this IS the existing, curated relationship; test_input_paths
    # is never consulted). `decisions/0089` §C: the referenced result must
    # actually parse as a well-formed OracleResult and must genuinely
    # belong to this contract/check/scope -- never a bare YAML key check.
    # This is a historical-relationship question only, deliberately never
    # calling evaluate_result_precedence (a current-execution-outcome
    # question, §4's job alone -- see decisions/0089 §C's own rationale).
    test_evidence_check_id: dict[str, str] = {}
    for rec in records.values():
        if rec.kind != "evidence" or rec.fields.get("evidence_kind") != "test":
            continue
        raw_ref = rec.fields.get("test_ref", "")
        if not raw_ref or raw_ref == "null":
            continue
        result_path = knowledge_root / _unquote(raw_ref)
        if not result_path.is_file():
            continue
        try:
            result = oracle_mod.parse_oracle_result(result_path)
        except oracle_mod.OracleSchemaError:
            continue
        if result.contract_id != contract.contract_id:
            continue
        check = contract.check_by_id(result.check_id)
        if check is None:
            continue
        if result.scope != check.scope:
            continue
        test_evidence_check_id[rec.record_id] = result.check_id

    findings: list[ClaimFinding] = []
    for rec in records.values():
        if rec.kind != "claim":
            continue
        supporting = set(_extract_id_strings(rec.fields.get("supporting_evidence", "")))
        if not (supporting & citing_evidence_ids):
            continue
        req_ids = _requirement_ids_depending_on(records, rec.record_id)
        bridging_check_ids = sorted(
            {test_evidence_check_id[ev] for ev in supporting if ev in test_evidence_check_id}
        )
        if bridging_check_ids:
            for check_id in bridging_check_ids:
                findings.append(ClaimFinding(rec.record_id, req_ids, "behavioural_risk", check_id))
        else:
            findings.append(ClaimFinding(rec.record_id, req_ids, "relevant_no_coverage_link", None))

    if any(f.tier == "behavioural_risk" for f in findings):
        return "behavioural_risk", findings
    return "relevant_no_coverage_link", findings


# ---------------------------------------------------------------------------
# §4 -- independent assurance-report semantics (decisions/0087 §1, corrected
# precedence: fresh FAIL > fresh INVALID > fresh PASS > no fresh result)
# ---------------------------------------------------------------------------


@dataclass
class AssuranceFinding:
    check_id: str
    classification: str  # CONFIRMED_REGRESSION | VERIFIED_SCOPE | INVALID_ASSESSMENT | VERIFICATION_GAP
    fresh_effective_outcome: str | None
    fresh_invalid_reason: str | None
    aggregate_state: str | None
    observed_outcomes: list[str]
    contributing_symbols: list[str] = field(default_factory=list)


def run_check_assurance(
    oracle_mod, contract_path: Path, contract, check_id: str,
    target_repo_root: Path, raw_output_dir: Path, historical_results: list,
) -> AssuranceFinding:
    check = contract.check_by_id(check_id)
    fresh_result = oracle_mod.evaluate_check(
        contract, check, contract_path=contract_path, repo_root=target_repo_root,
        raw_output_dir=raw_output_dir,
    )
    fresh_effective_outcome, fresh_reason = oracle_mod.evaluate_result_precedence(
        fresh_result, contract, check, contract_path=contract_path, repo_root=target_repo_root,
    )
    all_results = [*historical_results, fresh_result]
    aggregates = oracle_mod.aggregate_contract(
        contract, all_results, contract_path=contract_path, repo_root=target_repo_root,
    )
    aggregate = next((a for a in aggregates if a.check_id == check_id), None)

    # decisions/0087 §1: classification reads ONLY the fresh result's own
    # effective outcome -- never the aggregate state, which is shown
    # alongside for context, never as a precedence step.
    if fresh_effective_outcome == "FAIL":
        classification = "CONFIRMED_REGRESSION"
    elif fresh_effective_outcome == "INVALID":
        classification = "INVALID_ASSESSMENT"
    elif fresh_effective_outcome == "PASS":
        classification = "VERIFIED_SCOPE"
    else:  # pragma: no cover -- evaluate_result_precedence never returns
        # anything else, named defensively, never silently swallowed.
        classification = "VERIFICATION_GAP"

    return AssuranceFinding(
        check_id=check_id,
        classification=classification,
        fresh_effective_outcome=fresh_effective_outcome,
        fresh_invalid_reason=fresh_reason if fresh_effective_outcome == "INVALID" else None,
        aggregate_state=aggregate.state if aggregate else None,
        observed_outcomes=aggregate.observed_outcomes if aggregate else [],
    )


def _load_historical_results(oracle_mod, slug_dir: Path) -> list:
    results_dir = slug_dir / "results"
    results = []
    if not results_dir.is_dir():
        return results
    for result_path in sorted(results_dir.glob("*.yaml")):
        try:
            results.append(oracle_mod.parse_oracle_result(result_path))
        except oracle_mod.OracleSchemaError:
            continue
    return results


# ---------------------------------------------------------------------------
# Orchestration and reporting
# ---------------------------------------------------------------------------


@dataclass
class RangeReport:
    path: str
    requested_range: list[int]
    status: str
    reason: str | None
    resolved_symbols: list[dict] = field(default_factory=list)
    symbol_classifications: list[dict] = field(default_factory=list)
    assurance: list[dict] = field(default_factory=list)


def assess(
    *, target_repo_root: Path, target_graph_db: Path, knowledge_root: Path,
    slug: str, changed: list[ChangedRange], run_checks: bool,
) -> dict:
    oracle_mod, ki = _load_codecompass_modules()
    slug_dir = knowledge_root / "planning" / "knowledge" / slug
    contract_path = knowledge_root / "planning" / "contracts" / slug / "oracle-contract.yaml"
    records = ki.load_slug_records(slug_dir)
    contract = oracle_mod.parse_oracle_contract(contract_path) if contract_path.is_file() else None
    historical_results = _load_historical_results(oracle_mod, knowledge_root / "planning" / "contracts" / slug) if contract else []
    raw_output_dir = knowledge_root / "planning" / "contracts" / slug / "scratch-assessments"

    range_reports: list[RangeReport] = []
    for c in changed:
        res = resolve_changed_range(oracle_mod, target_repo_root, target_graph_db, c)
        if res.status in ("cannot_map", "stale_index"):
            range_reports.append(RangeReport(
                path=c.path, requested_range=[c.start, c.end], status=res.status, reason=res.reason,
            ))
            continue

        # res.status is "resolved" or "partially_resolved" -- at least one
        # symbol was matched; a partial match is still assessed, never
        # discarded wholesale (decisions/0089 §B).
        if contract is None:
            range_reports.append(RangeReport(
                path=c.path, requested_range=[c.start, c.end], status=res.status,
                reason=f"no oracle-contract.yaml for slug {slug!r} under {knowledge_root}",
                resolved_symbols=[asdict(s) for s in res.symbols],
            ))
            continue

        symbol_classifications: list[dict] = []
        check_contributors: dict[str, set[str]] = {}
        for sym in res.symbols:
            classification, claim_findings = classify_symbol(
                records, contract, oracle_mod, sym.name, c.path, knowledge_root
            )
            symbol_classifications.append({
                "symbol": asdict(sym),
                "classification": classification,
                "claims": [asdict(cf) for cf in claim_findings],
            })
            for cf in claim_findings:
                if cf.tier == "behavioural_risk" and cf.check_id:
                    check_contributors.setdefault(cf.check_id, set()).add(sym.name)

        assurance: list[AssuranceFinding] = []
        for check_id in sorted(check_contributors):
            contributing = sorted(check_contributors[check_id])
            if run_checks:
                finding = run_check_assurance(
                    oracle_mod, contract_path, contract, check_id,
                    target_repo_root, raw_output_dir, historical_results,
                )
            else:
                finding = AssuranceFinding(
                    check_id=check_id, classification="VERIFICATION_GAP",
                    fresh_effective_outcome=None, fresh_invalid_reason=None,
                    aggregate_state=None, observed_outcomes=[],
                )
            finding.contributing_symbols = contributing
            assurance.append(finding)

        range_reports.append(RangeReport(
            path=c.path, requested_range=[c.start, c.end], status=res.status, reason=res.reason,
            resolved_symbols=[asdict(s) for s in res.symbols],
            symbol_classifications=symbol_classifications,
            assurance=[asdict(a) for a in assurance],
        ))

    return {
        "target_repo_root": str(target_repo_root),
        "target_graph_db": str(target_graph_db),
        "knowledge_root": str(knowledge_root),
        "slug": slug,
        "ran_checks": run_checks,
        "findings": [asdict(r) for r in range_reports],
    }


def render_text_report(report: dict) -> str:
    lines = [
        f"assess_change_impact: slug={report['slug']!r} "
        f"target_repo_root={report['target_repo_root']!r}",
    ]
    for f in report["findings"]:
        lines.append(f"\n- {f['path']}:{f['requested_range'][0]}-{f['requested_range'][1]}")
        lines.append(f"  status: {f['status']}")
        if f["reason"]:
            lines.append(f"  reason: {f['reason']}")
        for sc in f["symbol_classifications"]:
            sym = sc["symbol"]
            lines.append(f"  symbol: {sym['kind']} {sym['name']} (line {sym['line']}) -> {sc['classification']}")
            for cl in sc["claims"]:
                lines.append(
                    f"    claim {cl['claim_id']} (requirements: {cl['requirement_ids'] or 'none'}) "
                    f"-> {cl['tier']}" + (f" (check: {cl['check_id']})" if cl["check_id"] else "")
                )
        for a in f["assurance"]:
            lines.append(
                f"  check {a['check_id']} (symbols: {a['contributing_symbols']}): {a['classification']}"
                f" (fresh={a['fresh_effective_outcome']}, aggregate={a['aggregate_state']},"
                f" observed={a['observed_outcomes']})"
            )
            if a["fresh_invalid_reason"]:
                lines.append(f"    invalid_reason: {a['fresh_invalid_reason']}")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--target-repo-root", type=Path, required=True)
    parser.add_argument("--target-graph-db", type=Path, default=None)
    parser.add_argument("--knowledge-root", type=Path, default=ROOT)
    parser.add_argument("--slug", required=True)
    parser.add_argument("--changed", type=parse_changed_arg, action="append", default=[])
    parser.add_argument("--run-checks", action="store_true")
    parser.add_argument("--json", action="store_true", help="print the machine-readable report only")
    args = parser.parse_args()

    target_graph_db = args.target_graph_db or (args.target_repo_root / "context-graph.db")
    if not args.changed:
        print("error: at least one --changed path:start-end is required", file=sys.stderr)
        return 2

    report = assess(
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
        print(render_text_report(report))
        print("\n--- JSON ---")
        print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
