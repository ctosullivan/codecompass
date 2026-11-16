"""Phase 89 Stage 89A — source/test change detection and reconciliation.

Two sibling detectors feeding one shared manifest writer, layered on
top of the *existing* Phase 81 reconciliation flow (`write_manifest`/
`apply_manifest`), Phase 82 oracle (`oracle.py`, unmodified), and
Phase 83 change-impact classification (`change_impact.py`, extended
only with the additive `on_fresh_result`/`raw_output_dir` parameters —
see that module and `decisions/0096`). No new scheduler, event bus,
knowledge store, or documentation compiler.

See `planning/phase-89-incremental-knowledge-documentation-reconciliation.md`
for the full design and `decisions/0096` for the implementation-contract
resolutions made in this module (the final `on_fresh_result` callback
shape, the durable raw-output convention, and the test-input-path
contract-dependency mapping for test-only changes).

Three genuinely different detection pathways, never conflated:

- **(a) `detect_source_changes`** — re-verifying an already-covered
  scope. Tracks two kinds of files: (1) a changed *source* file named
  by an existing `source`-kind Evidence `source_ref` — resolved via the
  existing `change_impact.classify_symbol`/`assess()` pathway
  (`resolution="symbol_change"`); (2) a changed *test-input* file named
  by `oracle-contract.yaml`'s own `check.test_input_paths` for a check
  that already has at least one citing `test`-kind Evidence record —
  resolved directly via a check_id→Claim bridge lookup, never through
  `classify_symbol` (`resolution="test_input_change"`), since a pure
  test-file edit changes no source symbol at all.
- **(b) `detect_newly_coverable_checks`** — a required check with
  **zero** existing citing `test`-kind Evidence, whose test now
  collects. Never reaches a check detector (a) already owns.
"""

from __future__ import annotations

import contextlib
import os
import re
import sqlite3
import subprocess
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

from codecompass import change_impact as _ci
from codecompass import knowledge_intermediate as _ki
from codecompass import oracle as _oracle

_ID_PATTERN = re.compile(r"\b(OBS|EV|CL|DE|DEC|REQ)-[A-Z0-9]+-\d+\b")


def _extract_id_strings(value: str) -> list[str]:
    return [m.group(0) for m in _ID_PATTERN.finditer(value)]


@contextlib.contextmanager
def _chdir(path: Path):
    """Scoped, restored `chdir` — the same pattern `mcp/tools.py::_chdir`
    already establishes (duplicated here rather than imported from
    `mcp/`, which this module has no other dependency on and should
    not acquire one on just for this). A durable `raw_output_ref` is
    stored as a *relative* path, resolved correctly only when the
    process cwd is `knowledge_root` — see `decisions/0096`."""
    previous = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(previous)


def _load_file_hash(graph_db: Path, path: str) -> str | None:
    if not graph_db.is_file():
        return None
    con = sqlite3.connect(f"file:{graph_db}?mode=ro", uri=True)
    try:
        row = con.execute(
            "SELECT content_hash FROM source_files WHERE path = ?", (path,)
        ).fetchone()
    finally:
        con.close()
    return row[0] if row else None


def _repo_revision(repo_root: Path) -> str:
    try:
        proc = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=repo_root,
            capture_output=True, text=True, timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return "working tree"
    if proc.returncode != 0:
        return "working tree"
    return proc.stdout.strip()


# ---------------------------------------------------------------------------
# Shared bridge lookups (mirroring change_impact.classify_symbol's own
# test_evidence_check_id loop, change_impact.py:371-394 — reused as a
# lookup at the module/check_id level, never copy-pasted)
# ---------------------------------------------------------------------------


def _test_evidence_check_id_map(records, contract, knowledge_root: Path) -> dict[str, str]:
    """`{evidence_record_id: check_id}` for every existing `test`-kind
    Evidence record whose `test_ref` resolves to a real `OracleResult`
    genuinely belonging to this contract (both `contract_id` and
    `oracle_contract_id`, `decisions/0090`) and whose `scope` matches
    the check it claims. The single source of truth this whole module
    uses to answer "does this check_id already have a citing Evidence
    record" — never re-derived differently in two places."""
    mapping: dict[str, str] = {}
    for rec in records.values():
        if rec.kind != "evidence" or rec.fields.get("evidence_kind") != "test":
            continue
        raw_ref = rec.fields.get("test_ref", "")
        if not raw_ref or raw_ref == "null":
            continue
        ref = raw_ref.strip()
        if len(ref) >= 2 and ref[0] == ref[-1] and ref[0] in "\"'":
            ref = ref[1:-1]
        result_path = knowledge_root / ref
        if not result_path.is_file():
            continue
        try:
            result = _oracle.parse_oracle_result(result_path)
        except _oracle.OracleSchemaError:
            continue
        if result.contract_id != contract.contract_id:
            continue
        if result.oracle_contract_id != contract.contract_id:
            continue
        check = contract.check_by_id(result.check_id)
        if check is None or result.scope != check.scope:
            continue
        mapping[rec.record_id] = result.check_id
    return mapping


def _claims_bridged_by_check_id(
    records, check_id: str, evidence_check_ids: dict[str, str],
) -> list[str]:
    """Claims whose `supporting_evidence`/`contradicting_evidence` cites
    an Evidence record already bridged to `check_id` — the same
    direction `classify_symbol` resolves from a Claim, inverted to
    start from a `check_id` instead, for the test-input-change and
    newly-coverable-check pathways, which have no symbol to resolve
    from in the first place."""
    bridging_evidence = {ev for ev, cid in evidence_check_ids.items() if cid == check_id}
    if not bridging_evidence:
        return []
    claim_ids: list[str] = []
    for rec in records.values():
        if rec.kind != "claim":
            continue
        supporting = set(_extract_id_strings(rec.fields.get("supporting_evidence", "")))
        contradicting = set(_extract_id_strings(rec.fields.get("contradicting_evidence", "")))
        if (supporting | contradicting) & bridging_evidence:
            claim_ids.append(rec.record_id)
    return sorted(claim_ids)


def _had_historical_pass(historical_results: list, check_id: str) -> bool:
    return any(r.check_id == check_id and r.outcome == "PASS" for r in historical_results)


def _label_for(historical_results: list, check_id: str, fresh_outcome: str) -> str:
    """`"regression"` / `"newly_discovered_failure"` / `"newly_covered"` /
    `"re_confirmed"` / `"invalid"` — computed once, here, from data
    already available before this fresh result (never relabelling
    `change_impact.py`'s own `CONFIRMED_REGRESSION`/etc. classification,
    which is a Phase-83-level concern this module does not touch)."""
    had_pass = _had_historical_pass(historical_results, check_id)
    if fresh_outcome == "FAIL":
        return "regression" if had_pass else "newly_discovered_failure"
    if fresh_outcome == "PASS":
        return "re_confirmed" if had_pass else "newly_covered"
    return "invalid"


# ---------------------------------------------------------------------------
# Source baseline (planning/knowledge/<slug>/reconciliation/source-baseline.toml)
# ---------------------------------------------------------------------------


def source_baseline_path(project_root: Path, slug: str) -> Path:
    return _ki.reconciliation_dir(project_root, slug) / "source-baseline.toml"


def _read_baseline(project_root: Path, slug: str) -> dict[str, dict]:
    return _ki._read_simple_toml_tables(source_baseline_path(project_root, slug))


def _write_baseline(project_root: Path, slug: str, tables: dict[str, dict]) -> None:
    _ki._write_simple_toml_tables(source_baseline_path(project_root, slug), tables)


def establish_source_baseline(project_root: Path, slug: str, path: str, content_hash: str) -> None:
    """The only automatic baseline write this module performs
    implicitly is none at all — bootstrapping a file's *first-ever*
    baseline, exactly like `establish_new_region_baselines`, is always
    this separate, explicit call, never a side effect of detection
    (`CLAUDE.md` §1 L-087)."""
    tables = _read_baseline(project_root, slug)
    tables[path] = {
        "content_hash": content_hash,
        "last_reconciled": datetime.now(UTC).isoformat(),
    }
    _write_baseline(project_root, slug, tables)


def advance_source_baseline_after_apply(
    project_root: Path, slug: str, path: str, content_hash: str,
) -> None:
    """Mirrors `advance_region_baseline_after_publish` — called only
    after `apply_manifest` reports a real, successful write for the
    accepted item citing this file. A crash or partial failure leaves
    the baseline exactly where it was."""
    establish_source_baseline(project_root, slug, path, content_hash)


def establish_baselines_for_new_files(
    project_root: Path, slug: str, *, repo_root: Path,
    result: DetectSourceChangesResult, target_graph_db: Path | None = None,
) -> list[str]:
    """Bootstraps a *first-ever* baseline for every file `detect_source_
    changes` reported as `new` (mirrors `establish_new_region_baselines`
    exactly, §1.1's own "new is read-only" precedent) — never a side
    effect of detection itself (`CLAUDE.md` §1 L-087); an explicit,
    separate, opt-in call (`detect-changes --establish-baselines`, §4.10)
    a human runs once, deliberately, the first time a slug's own source/
    test tracking begins. Returns the paths actually established."""
    if target_graph_db is None:
        target_graph_db = repo_root / "context-graph.db"
    established: list[str] = []
    for path in result.new_files:
        content_hash = _load_file_hash(target_graph_db, path)
        if content_hash is None:
            continue  # not indexed -- never bootstrap a baseline from an unverifiable hash
        establish_source_baseline(project_root, slug, path, content_hash)
        established.append(path)
    return established


# ---------------------------------------------------------------------------
# §4.1(a)/§5.1 — detect_source_changes
# ---------------------------------------------------------------------------


@dataclass
class SourceChangeFinding:
    path: str
    resolution: str  # "symbol_change" | "test_input_change"
    check_id: str | None = None  # test_input_change only
    claim_ids: list[str] = field(default_factory=list)  # test_input_change only


@dataclass
class StaleGraphIndexFinding:
    path: str
    reason: str


@dataclass
class DetectSourceChangesResult:
    changed: list[SourceChangeFinding] = field(default_factory=list)
    stale_graph_index: list[StaleGraphIndexFinding] = field(default_factory=list)
    new_files: list[str] = field(default_factory=list)
    deleted_files: list[str] = field(default_factory=list)


def _tracked_source_paths(records) -> set[str]:
    """Every distinct path named by a `source`-kind Evidence `source_ref`
    (`path:start[-end] def/class symbol`) — the whole file is tracked,
    never a sub-range (Phase 83's own existing line-range convention
    resolves the actual symbol span later, via `classify_symbol`)."""
    paths: set[str] = set()
    for rec in records.values():
        if rec.kind != "evidence" or rec.fields.get("evidence_kind") != "source":
            continue
        raw_ref = rec.fields.get("source_ref", "")
        if not raw_ref or raw_ref == "null":
            continue
        match = _ci._SOURCE_REF_WITH_SYMBOL_RE.match(_ci._unquote(raw_ref))
        if match:
            paths.add(match.group("path"))
    return paths


def _tracked_test_input_paths(
    records, contract, knowledge_root: Path
) -> dict[str, str]:
    """`{test_input_path: check_id}` for every `required` or non-required
    check in the contract that already has at least one citing
    `test`-kind Evidence record (detector (a)'s own exclusive scope,
    §0.2.B) — a check with zero citing Evidence is detector (b)'s own
    scope and is never tracked here."""
    evidence_check_ids = _test_evidence_check_id_map(records, contract, knowledge_root)
    covered_check_ids = set(evidence_check_ids.values())
    mapping: dict[str, str] = {}
    for check in contract.checks:
        if check.check_id not in covered_check_ids:
            continue
        for test_input_path in check.test_input_paths:
            mapping[test_input_path] = check.check_id
    return mapping


def detect_source_changes(
    project_root: Path, slug: str, *, repo_root: Path, target_graph_db: Path | None = None,
) -> DetectSourceChangesResult:
    """§4.1(a)/§5.1. Purely observational — reads file/baseline/graph
    state only; never runs a subprocess, never writes any file (not
    even the baseline, §1 L-087). `target_graph_db` defaults to
    `<repo_root>/context-graph.db`, the target's own graph (never
    CodeCompass's self-referential one)."""
    if target_graph_db is None:
        target_graph_db = repo_root / "context-graph.db"
    sdir = _ki.slug_dir(project_root, slug)
    records = _ki.load_slug_records(sdir)
    contract_path = project_root / "planning" / "contracts" / slug / "oracle-contract.yaml"
    contract = _oracle.parse_oracle_contract(contract_path) if contract_path.is_file() else None

    tracked: dict[str, str] = {p: "symbol_change" for p in _tracked_source_paths(records)}
    test_input_check: dict[str, str] = {}
    if contract is not None:
        test_input_check = _tracked_test_input_paths(records, contract, project_root)
        for p in test_input_check:
            tracked.setdefault(p, "test_input_change")

    baseline = _read_baseline(project_root, slug)
    result = DetectSourceChangesResult()

    evidence_check_ids = (
        _test_evidence_check_id_map(records, contract, project_root) if contract else {}
    )

    for path, resolution in sorted(tracked.items()):
        live_path = repo_root / path
        if not live_path.is_file():
            if path in baseline:
                result.deleted_files.append(path)
            continue
        graph_hash = _load_file_hash(target_graph_db, path)
        live_hash = _oracle.sha256_file(live_path)
        if graph_hash is None:
            # Not indexed at all -- never silently treated as "unchanged";
            # excluded from baseline comparison exactly like a stale index.
            result.stale_graph_index.append(
                StaleGraphIndexFinding(
                    path, f"{path!r} has no source_files row in {target_graph_db}"
                )
            )
            continue
        if graph_hash != live_hash:
            result.stale_graph_index.append(
                StaleGraphIndexFinding(
                    path,
                    f"live content_hash ({live_hash}) does not match the graph's own "
                    f"recorded content_hash ({graph_hash}) for {path!r} -- the target "
                    "graph was not re-synced against this exact content",
                )
            )
            continue
        baseline_entry = baseline.get(path)
        if baseline_entry is None:
            result.new_files.append(path)
            continue
        if baseline_entry.get("content_hash") == graph_hash:
            continue  # unchanged
        if resolution == "symbol_change":
            result.changed.append(SourceChangeFinding(path=path, resolution="symbol_change"))
        else:
            check_id = test_input_check[path]
            claim_ids = _claims_bridged_by_check_id(records, check_id, evidence_check_ids)
            result.changed.append(
                SourceChangeFinding(
                    path=path, resolution="test_input_change",
                    check_id=check_id, claim_ids=claim_ids,
                )
            )
    return result


# ---------------------------------------------------------------------------
# §4.1(b)/§5.1 — detect_newly_coverable_checks
# ---------------------------------------------------------------------------


@dataclass
class NewlyCoverableCheck:
    check_id: str
    claim_id: str


@dataclass
class ConfigError:
    check_id: str
    reason: str


@dataclass
class DetectNewlyCoverableResult:
    coverable: list[NewlyCoverableCheck] = field(default_factory=list)
    not_yet_coverable: list[str] = field(default_factory=list)
    indeterminate: list[tuple[str, str]] = field(default_factory=list)  # (check_id, reason)
    config_errors: list[ConfigError] = field(default_factory=list)


def detect_newly_coverable_checks(
    project_root: Path, slug: str, *, repo_root: Path, probe: bool = False,
) -> DetectNewlyCoverableResult:
    """§4.1(b)/§5.1. `probe=False` (the default, `detect-changes`
    without `--probe-coverage`): purely observational, scans
    `oracle-contract.yaml` and existing Evidence only — never spawns a
    subprocess. `probe=True` (`--probe-coverage`): additionally runs
    `oracle.run_pytest_collect_only` for every check this scan finds
    with zero citing Evidence — exactly one subprocess per such check,
    never a full run, never a file write."""
    sdir = _ki.slug_dir(project_root, slug)
    records = _ki.load_slug_records(sdir)
    contract_path = project_root / "planning" / "contracts" / slug / "oracle-contract.yaml"
    if not contract_path.is_file():
        return DetectNewlyCoverableResult()
    contract = _oracle.parse_oracle_contract(contract_path)
    evidence_check_ids = _test_evidence_check_id_map(records, contract, project_root)
    covered_check_ids = set(evidence_check_ids.values())

    result = DetectNewlyCoverableResult()
    for check in contract.checks:
        if check.check_id in covered_check_ids:
            continue  # detector (a)'s own exclusive scope
        matching_reqs = [
            rec for rec in records.values()
            if rec.kind == "requirement" and rec.fields.get("check_id") == check.check_id
        ]
        if not matching_reqs:
            result.indeterminate.append(
                (check.check_id, "no Requirement names this check_id — nothing to resolve to")
            )
            continue
        resolved_claim_ids: set[str] = set()
        config_error = False
        for req in matching_reqs:
            deps = _extract_id_strings(req.fields.get("depends_on", ""))
            if len(deps) != 1:
                result.config_errors.append(
                    ConfigError(
                        check.check_id,
                        f"{req.record_id} names check_id={check.check_id!r} but its own "
                        f"depends_on has {len(deps)} entries, not exactly 1 — refusing to "
                        "resolve against a multi-check Requirement",
                    )
                )
                config_error = True
                continue
            resolved_claim_ids.add(deps[0])
        if config_error or not resolved_claim_ids:
            continue
        if len(resolved_claim_ids) != 1:
            result.config_errors.append(
                ConfigError(
                    check.check_id,
                    f"check_id={check.check_id!r} resolves to more than one distinct "
                    f"Claim via different Requirements: {sorted(resolved_claim_ids)}",
                )
            )
            continue
        claim_id = next(iter(resolved_claim_ids))
        if not probe:
            result.not_yet_coverable.append(check.check_id)  # unknown until probed
            continue
        collects, reason, _raw = _oracle.run_pytest_collect_only(repo_root, check.check_reference)
        if collects:
            result.coverable.append(NewlyCoverableCheck(check_id=check.check_id, claim_id=claim_id))
        else:
            result.not_yet_coverable.append(check.check_id)
    return result


# ---------------------------------------------------------------------------
# §5.1 — propose_reconciliation (the only point this module executes a
# check for real, always via verify-changes, never detect-changes)
# ---------------------------------------------------------------------------


@dataclass
class ContributingFinding:
    claim_id: str
    contract_id: str
    check_id: str
    run_id: str
    raw_output_ref: str
    label: str  # "regression" | "newly_discovered_failure" | "newly_covered" | "re_confirmed"
    target_field: str  # "supporting_evidence" | "contradicting_evidence"
    what_it_shows: str
    repository_revision: str
    source_path: str | None = None  # the tracked file whose drift triggered this
    # finding (detector (a) only -- symbol_change/test_input_change); None for
    # detector (b) (newly_coverable), which has no file-baseline concept at all.


def _durable_raw_output_dir(slug: str) -> Path:
    """Project-relative, portable, durable — `planning/contracts/<slug>/
    results/raw`, the same convention `mcp/tools.py::oracle_execute_check`
    already establishes, never Phase 83's own disposable
    `scratch-assessments` (`decisions/0096`)."""
    return Path("planning") / "contracts" / slug / "results" / "raw"


def _persist_and_verify(
    knowledge_root: Path, slug: str, result,
) -> tuple[Path, bool, str]:
    """Writes `result`'s own structured YAML to the slug's durable
    `results/` directory and round-trip-verifies it (dispatch §3.B item
    2-3): re-parses the just-written file and re-evaluates its
    precedence, confirming it still resolves to the same outcome and its
    `raw_output_ref` file genuinely exists with a matching hash. Runs
    under a scoped `chdir(knowledge_root)` so the already-relative
    `raw_output_ref` `evaluate_check` produced (via the durable
    `results/raw` dir) resolves correctly regardless of the caller's own
    cwd. Returns `(result_path, ok, reason)` — `ok=False` means this
    result must never be cited by any manifest item (fail-closed,
    dispatch §3.B's own acceptance criterion)."""
    results_dir = knowledge_root / "planning" / "contracts" / slug / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    out_path = results_dir / f"{result.check_id}--{result.run_id}.yaml"
    with _chdir(knowledge_root):
        if out_path.is_file():
            # Immutable per-run naming already guarantees a distinct
            # filename per real run (decisions/0082 §C) -- a retry that
            # reaches this exact path means this exact result was
            # already successfully persisted; never overwrite it, never
            # re-write it a second time.
            ok_existing = out_path.is_file()
        else:
            _oracle.write_oracle_result(out_path, result)
            ok_existing = False
        try:
            reparsed = _oracle.parse_oracle_result(out_path)
        except _oracle.OracleSchemaError as exc:
            return out_path, False, f"persisted result failed to re-parse: {exc}"
        raw_path = Path(reparsed.raw_output_ref)
        if not raw_path.is_file():
            return out_path, False, f"raw_output_ref {reparsed.raw_output_ref!r} does not exist"
        if reparsed.outcome != "INVALID":
            # A fresh re-evaluation of precedence against this persisted
            # result's own repo_root is a separate, later question
            # (staleness over time) -- here we only confirm the just-
            # written YAML/raw-output pair is internally consistent and
            # independently re-readable, the portability guarantee this
            # function exists to provide.
            if _oracle.sha256_file(raw_path) != reparsed.raw_output_sha256:
                return out_path, False, "raw output hash does not match the persisted record"
    return out_path, True, ("already persisted" if ok_existing else "persisted and verified")


def propose_reconciliation(
    project_root: Path, slug: str, *,
    repo_root: Path, target_graph_db: Path | None = None,
    source_changes: DetectSourceChangesResult | None = None,
    newly_coverable: list[NewlyCoverableCheck] | None = None,
) -> list[ContributingFinding]:
    """Executes real verification for every finding `detect_source_
    changes`/`detect_newly_coverable_checks` reported, persists and
    round-trip-verifies every fresh `OracleResult` (durable convention,
    `decisions/0096`), and returns the per-Claim contributing findings
    ready for `write_source_reconciliation_manifest`. Called only from
    `verify-changes` (§4.10) -- never `detect-changes`."""
    if target_graph_db is None:
        target_graph_db = repo_root / "context-graph.db"
    sdir = _ki.slug_dir(project_root, slug)
    records = _ki.load_slug_records(sdir)
    contract_path = project_root / "planning" / "contracts" / slug / "oracle-contract.yaml"
    contract = _oracle.parse_oracle_contract(contract_path)
    historical_results = []
    results_dir = project_root / "planning" / "contracts" / slug / "results"
    if results_dir.is_dir():
        for p in sorted(results_dir.glob("*.yaml")):
            try:
                historical_results.append(_oracle.parse_oracle_result(p))
            except _oracle.OracleSchemaError:
                continue

    out: list[ContributingFinding] = []

    # --- (a) symbol_change findings: through assess(), reusing the
    # existing classify_symbol pathway, never through a second,
    # independent execution of the same check. ---
    symbol_change_findings = [
        f for f in (source_changes.changed if source_changes else [])
        if f.resolution == "symbol_change"
    ]
    if symbol_change_findings:
        ranges = []
        for f in symbol_change_findings:
            live_path = repo_root / f.path
            line_count = len(live_path.read_text(encoding="utf-8", errors="replace").splitlines())
            ranges.append(_ci.ChangedRange(path=f.path, start=1, end=max(line_count, 1)))

        captured: dict[tuple[int, str], object] = {}

        def _capture(range_index: int, result, _store=captured) -> None:
            _store[(range_index, result.check_id)] = result

        with _chdir(project_root):
            report = _ci.assess(
                target_repo_root=repo_root, target_graph_db=target_graph_db,
                knowledge_root=project_root, slug=slug, changed=ranges, run_checks=True,
                on_fresh_result=_capture,
                raw_output_dir=_durable_raw_output_dir(slug),
            )
        for range_index, range_report in enumerate(report["findings"]):
            for assurance in range_report.get("assurance", []):
                check_id = assurance["check_id"]
                classification = assurance["classification"]
                if classification not in ("CONFIRMED_REGRESSION", "VERIFIED_SCOPE"):
                    continue
                fresh_result = captured.get((range_index, check_id))
                if fresh_result is None:
                    continue
                _, ok, _reason = _persist_and_verify(project_root, slug, fresh_result)
                if not ok:
                    continue
                fresh_outcome = "FAIL" if classification == "CONFIRMED_REGRESSION" else "PASS"
                label = _label_for(historical_results, check_id, fresh_outcome)
                target_field = (
                    "contradicting_evidence" if fresh_outcome == "FAIL" else "supporting_evidence"
                )
                for cf in range_report.get("symbol_classifications", []):
                    for claim_finding in cf.get("claims", []):
                        if claim_finding.get("check_id") != check_id:
                            continue
                        claim_id = claim_finding["claim_id"]
                        if (
                            classification == "VERIFIED_SCOPE"
                            and label == "re_confirmed"
                            and records.get(claim_id)
                            and records[claim_id].fields.get("evidence_support_state")
                            == "supported"
                        ):
                            # §4.3: a fresh VERIFIED_SCOPE against an
                            # ALREADY-supported Claim is a no-op -- but
                            # a Claim in any other state (partially_
                            # supported/unsupported/conflicting) still
                            # gets this new, materially useful
                            # confirming evidence proposed, e.g. a
                            # reversed regression re-verified PASS.
                            continue
                        out.append(ContributingFinding(
                            claim_id=claim_id,
                            contract_id=fresh_result.contract_id,
                            check_id=check_id, run_id=fresh_result.run_id,
                            raw_output_ref=fresh_result.raw_output_ref, label=label,
                            target_field=target_field,
                            what_it_shows=(
                                f"A real, independently executed oracle run of check "
                                f"{check_id!r} against the target checkout "
                                f"{'passes' if fresh_outcome == 'PASS' else 'fails'} "
                                f"({label})."
                            ),
                            repository_revision=_repo_revision(repo_root),
                            source_path=range_report["path"],
                        ))

    # --- test_input_change findings: direct execution, no symbol. ---
    for f in (source_changes.changed if source_changes else []):
        if f.resolution != "test_input_change":
            continue
        check = contract.check_by_id(f.check_id)
        if check is None or not f.claim_ids:
            continue
        with _chdir(project_root):
            fresh_result = _oracle.evaluate_check(
                contract, check, contract_path=contract_path, repo_root=repo_root,
                raw_output_dir=_durable_raw_output_dir(slug),
            )
        _, ok, _reason = _persist_and_verify(project_root, slug, fresh_result)
        if not ok or fresh_result.outcome == "INVALID":
            continue
        label = _label_for(historical_results, f.check_id, fresh_result.outcome)
        target_field = (
            "contradicting_evidence" if fresh_result.outcome == "FAIL" else "supporting_evidence"
        )
        for claim_id in f.claim_ids:
            if (
                label == "re_confirmed"
                and records.get(claim_id)
                and records[claim_id].fields.get("evidence_support_state") == "supported"
            ):
                continue  # §4.3: already-supported Claim, genuinely a no-op
            out.append(ContributingFinding(
                claim_id=claim_id, contract_id=fresh_result.contract_id, check_id=f.check_id,
                run_id=fresh_result.run_id, raw_output_ref=fresh_result.raw_output_ref, label=label,
                target_field=target_field,
                what_it_shows=(
                    f"A real, independently executed oracle run of check {f.check_id!r}, "
                    f"triggered by a change to its own test input, "
                    f"{'passes' if fresh_result.outcome == 'PASS' else 'fails'} ({label})."
                ),
                repository_revision=_repo_revision(repo_root),
                source_path=f.path,
            ))

    # --- (b) newly-coverable findings: direct execution, no symbol. ---
    for nc in (newly_coverable or []):
        check = contract.check_by_id(nc.check_id)
        if check is None:
            continue
        with _chdir(project_root):
            fresh_result = _oracle.evaluate_check(
                contract, check, contract_path=contract_path, repo_root=repo_root,
                raw_output_dir=_durable_raw_output_dir(slug),
            )
        _, ok, _reason = _persist_and_verify(project_root, slug, fresh_result)
        if not ok or fresh_result.outcome == "INVALID":
            continue
        label = _label_for(historical_results, nc.check_id, fresh_result.outcome)
        target_field = (
            "contradicting_evidence" if fresh_result.outcome == "FAIL" else "supporting_evidence"
        )
        out.append(ContributingFinding(
            claim_id=nc.claim_id, contract_id=fresh_result.contract_id, check_id=nc.check_id,
            run_id=fresh_result.run_id, raw_output_ref=fresh_result.raw_output_ref, label=label,
            target_field=target_field,
            what_it_shows=(
                f"A real, independently executed oracle run of the newly-coverable check "
                f"{nc.check_id!r} {'passes' if fresh_result.outcome == 'PASS' else 'fails'} "
                f"({label})."
            ),
            repository_revision=_repo_revision(repo_root),
        ))

    return out


# ---------------------------------------------------------------------------
# §5.3 — write_source_reconciliation_manifest (new sibling writer,
# mirroring write_doc_candidates_to_manifests exactly)
# ---------------------------------------------------------------------------


def write_source_reconciliation_manifest(
    project_root: Path, slug: str, findings: list[ContributingFinding],
    *, repo_root: Path | None = None, target_graph_db: Path | None = None,
) -> Path | None:
    """One manifest item **per Claim** (never per-finding, §4.8) —
    every contributing finding against the same Claim in one run is
    merged into that Claim's own single item, closing the self-conflict
    risk by construction (no two pending items can ever race the same
    Claim's own content hash within one `apply_manifest` batch).

    `repo_root`/`target_graph_db`, when given, let this function also
    record, per item, the distinct tracked file(s) (and their current
    graph `content_hash`) whose drift produced its own contributing
    findings (`ContributingFinding.source_path`, detector (a) only) —
    `advance_baselines_for_applied_item` reads these back, after a
    real, successful `apply`, to advance `source-baseline.toml` for
    exactly the files this item's own acceptance resolved (`CLAUDE.md`
    §1 L-087: a baseline never advances on detection alone)."""
    if not findings:
        return None
    by_claim: dict[str, list[ContributingFinding]] = {}
    for f in findings:
        by_claim.setdefault(f.claim_id, []).append(f)

    sdir = _ki.slug_dir(project_root, slug)
    records = _ki.load_slug_records(sdir)
    ts = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    manifest_path = _ki.reconciliation_dir(project_root, slug) / f"{ts}-source.toml"
    data: dict = {
        "manifest_id": f"{slug}@{ts}-source",
        "created": datetime.now(UTC).isoformat(),
        "slug": slug,
        "items": [],
    }
    for claim_id, claim_findings in sorted(by_claim.items()):
        claim = records.get(claim_id)
        if claim is None:
            continue
        base_hash = _ki.sha256_text(claim.path.read_text(encoding="utf-8"))
        touched_paths = sorted({f.source_path for f in claim_findings if f.source_path})
        touched_hashes = []
        if target_graph_db is not None:
            for p in touched_paths:
                touched_hashes.append(_load_file_hash(target_graph_db, p) or "")
        data["items"].append({
            "kind": "source_reconciliation",
            "record_id": claim_id,
            "base_claim_hash": base_hash,
            "repo_root": str(repo_root) if repo_root is not None else "",
            "contributing_source_paths": touched_paths,
            "contributing_source_hashes": touched_hashes,
            "contributing_contract_ids": [f.contract_id for f in claim_findings],
            "contributing_check_ids": [f.check_id for f in claim_findings],
            "contributing_run_ids": [f.run_id for f in claim_findings],
            "contributing_raw_output_refs": [f.raw_output_ref for f in claim_findings],
            "contributing_labels": [f.label for f in claim_findings],
            "contributing_target_fields": [f.target_field for f in claim_findings],
            "contributing_what_it_shows": [f.what_it_shows for f in claim_findings],
            "contributing_repository_revisions": [f.repository_revision for f in claim_findings],
            "state": "pending",
            "decision": "undecided",
        })
    if not data["items"]:
        return None
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(_ki._serialize_manifest(data), encoding="utf-8")
    return manifest_path


def advance_baselines_for_applied_item(project_root: Path, slug: str, item: dict) -> None:
    """Called by the CLI (`cli.py::knowledge_apply_manifest`) only after
    `apply_manifest` itself reports a real, successful write for this
    exact `source_reconciliation` item — never automatically, never on
    detection alone (`CLAUDE.md` §1 L-087). Advances `source-
    baseline.toml` for exactly the tracked file(s) this item's own
    acceptance resolved, using the graph `content_hash` recorded on the
    item at `verify-changes` time (never re-derived from a possibly
    different, later live state)."""
    paths = item.get("contributing_source_paths", [])
    hashes = item.get("contributing_source_hashes", [])
    for path, content_hash in zip(paths, hashes):
        if not content_hash:
            continue
        advance_source_baseline_after_apply(project_root, slug, path, content_hash)
