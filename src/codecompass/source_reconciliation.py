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


def _repo_revision(repo_root: Path, *, fresh_result=None) -> str:
    """`git rev-parse HEAD` alone silently implies a clean commit was
    verified even when the working tree is dirty (Phase 89A corrective
    pass, bounded check 2) — a real risk here specifically, since
    reconciling a source/test change is routinely done against an
    *uncommitted* edit. When `git status --porcelain` reports any
    local modification, the returned string is marked `+dirty` and, if
    `fresh_result` (the real `OracleResult` this revision string is
    being recorded for) is given, its own `tested_subject_digest`/
    `test_input_digest` — genuine content-digest provenance, never
    derived from git — are embedded directly, so a reader can always
    tell the *actual* verified tree state apart from the named commit.
    A clean tree still returns the bare commit hash, unchanged."""
    try:
        rev_proc = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=repo_root,
            capture_output=True, text=True, timeout=10,
        )
        status_proc = subprocess.run(
            ["git", "status", "--porcelain"], cwd=repo_root,
            capture_output=True, text=True, timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        if fresh_result is not None:
            return (
                f"working tree (tested_subject_digest={fresh_result.tested_subject_digest}, "
                f"test_input_digest={fresh_result.test_input_digest})"
            )
        return "working tree"
    if rev_proc.returncode != 0:
        if fresh_result is not None:
            return (
                f"working tree (tested_subject_digest={fresh_result.tested_subject_digest}, "
                f"test_input_digest={fresh_result.test_input_digest})"
            )
        return "working tree"
    head = rev_proc.stdout.strip()
    dirty = status_proc.returncode == 0 and bool(status_proc.stdout.strip())
    if not dirty:
        return head
    if fresh_result is not None:
        return (
            f"{head}+dirty (tested_subject_digest={fresh_result.tested_subject_digest}, "
            f"test_input_digest={fresh_result.test_input_digest})"
        )
    return f"{head}+dirty"


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
    from in the first place.

    This identifies every Claim *affected* by a change to `check_id`'s
    own verification -- it deliberately does not yet distinguish a
    Claim whose own assertion is specifically governed by this one
    check from a broader Claim that merely cites the same bridging
    Evidence alongside others (Phase 89A corrective pass, defect A).
    Callers must run `claim_scope_category`/`_claim_bridging_check_ids`
    against each returned Claim before deciding whether it is eligible
    for this module's automatic single-check Evidence-update path."""
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


def _claim_bridging_check_ids(claim_rec, evidence_check_ids: dict[str, str]) -> set[str]:
    """The set of distinct `check_id`s `claim_rec`'s own existing
    `supporting_evidence`/`contradicting_evidence` already bridges to,
    via existing test-kind Evidence (`evidence_check_ids`, `_test_
    evidence_check_id_map`'s own return value) -- the per-Claim input
    `claim_scope_category`'s own `bridging_check_ids` ambiguity check
    needs (Phase 89A corrective pass, defect A)."""
    cited = set(_extract_id_strings(claim_rec.fields.get("supporting_evidence", "")))
    cited |= set(_extract_id_strings(claim_rec.fields.get("contradicting_evidence", "")))
    return {evidence_check_ids[ev] for ev in cited if ev in evidence_check_ids}


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
    test tracking begins. Returns the paths actually established.

    A non-Python oracle input (a fixture/data file, e.g. `tests/
    fixtures/filtered.journal`) is never indexed by the target's own
    symbol graph at all — for exactly those, already-tracked-as-
    `test_input_change` paths (never a `symbol_change`/source path,
    which genuinely needs graph indexing), fall back to a direct
    content hash rather than silently refusing to ever establish a
    baseline for a legitimate, contract-declared input (Phase 89A
    corrective pass, bounded check 1)."""
    if target_graph_db is None:
        target_graph_db = repo_root / "context-graph.db"
    sdir = _ki.slug_dir(project_root, slug)
    records = _ki.load_slug_records(sdir)
    contract_path = project_root / "planning" / "contracts" / slug / "oracle-contract.yaml"
    contract = _oracle.parse_oracle_contract(contract_path) if contract_path.is_file() else None
    test_input_paths = (
        set(_tracked_test_input_paths(records, contract, project_root)) if contract else set()
    )
    established: list[str] = []
    for path in result.new_files:
        content_hash = _load_file_hash(target_graph_db, path)
        if content_hash is None:
            if path not in test_input_paths:
                # not indexed, not a tracked test input -- never
                # bootstrap from an unverifiable hash
                continue
            live_path = repo_root / path
            if not live_path.is_file():
                continue
            content_hash = _oracle.sha256_file(live_path)
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
) -> dict[str, list[str]]:
    """`{test_input_path: [check_id, ...]}` for every `required` or
    non-required check in the contract that already has at least one
    citing `test`-kind Evidence record (detector (a)'s own exclusive
    scope, §0.2.B) — a check with zero citing Evidence is detector
    (b)'s own scope and is never tracked here.

    One-to-many by construction (Phase 89A corrective pass, defect A):
    the real Ledgerkit `balance-from-spec` contract already has
    multiple covered checks sharing both `tests/test_reports.py` and
    `tests/fixtures/filtered.journal` — a single-valued mapping here
    would silently drop every check but the last one `contract.checks`
    happens to iterate to for a shared path, permanently hiding its own
    drift from `detect_source_changes`."""
    evidence_check_ids = _test_evidence_check_id_map(records, contract, knowledge_root)
    covered_check_ids = set(evidence_check_ids.values())
    mapping: dict[str, list[str]] = {}
    for check in contract.checks:
        if check.check_id not in covered_check_ids:
            continue
        for test_input_path in check.test_input_paths:
            mapping.setdefault(test_input_path, []).append(check.check_id)
    for path, check_ids in mapping.items():
        mapping[path] = sorted(set(check_ids))
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
    test_input_check: dict[str, list[str]] = {}
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
            if resolution == "test_input_change":
                # A non-Python oracle input (a fixture/data file) is
                # never expected to be indexed by the target's own
                # symbol graph at all -- "not indexed" is never
                # "stale" here; track it directly by content hash
                # instead (Phase 89A corrective pass, bounded check 1).
                # `symbol_change` keeps the strict stale_graph_index
                # treatment below: that pathway genuinely needs the
                # graph for `classify_symbol` later.
                effective_hash = live_hash
            else:
                result.stale_graph_index.append(
                    StaleGraphIndexFinding(
                        path, f"{path!r} has no source_files row in {target_graph_db}"
                    )
                )
                continue
        elif graph_hash != live_hash:
            result.stale_graph_index.append(
                StaleGraphIndexFinding(
                    path,
                    f"live content_hash ({live_hash}) does not match the graph's own "
                    f"recorded content_hash ({graph_hash}) for {path!r} -- the target "
                    "graph was not re-synced against this exact content",
                )
            )
            continue
        else:
            effective_hash = graph_hash
        baseline_entry = baseline.get(path)
        if baseline_entry is None:
            result.new_files.append(path)
            continue
        if baseline_entry.get("content_hash") == effective_hash:
            continue  # unchanged
        if resolution == "symbol_change":
            result.changed.append(SourceChangeFinding(path=path, resolution="symbol_change"))
        else:
            for check_id in sorted(test_input_check[path]):
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
    resolution: str = ""  # "symbol_change" | "test_input_change" | "" (detector (b))


@dataclass
class AffectedClaim:
    """A Claim whose own existing Evidence bridges to a check that just
    drifted, but which is *not* eligible for this module's automatic
    single-check Evidence-update path (Phase 89A corrective pass,
    defect A) -- reported here so it is never silently discarded, but
    never turned into a `ContributingFinding`/manifest item: a broader
    Claim may only ever be updated through a separately justified,
    correctly scoped assessment of its own complete dependencies, not
    through this automatic mechanism."""
    claim_id: str
    check_id: str
    contract_id: str
    run_id: str
    category: str  # "aggregate" | "ambiguous"
    reason: str
    outcome: str  # the fresh result's own effective outcome ("PASS" | "FAIL")
    resolution: str  # "symbol_change" | "test_input_change" | "" (detector (b))
    source_path: str | None = None


@dataclass
class ReconciliationProposal:
    """`propose_reconciliation`'s own return type (Phase 89A corrective
    pass, defect A) — carries both the contributing findings and, for
    `test_input_change` findings specifically, which shared test-input
    paths are actually eligible to have their baseline advanced this
    round: a path is eligible only once *every* check sharing it
    (`required_by_path`, derived from every `test_input_change` finding
    `detect_source_changes` reported) was successfully, validly
    re-verified this run (`accounted_by_path`) -- never merely because
    *one* of several affected checks happened to be reconciled.

    `affected_claims` (Phase 89A corrective pass, defect A) carries
    every Claim a changed check's own bridging Evidence reaches but
    which `claim_scope_category` found ineligible for automatic
    mutation (`"aggregate"`/`"ambiguous"`) -- preserved as a visible
    finding, never silently dropped, and never fed into `findings`."""
    findings: list[ContributingFinding] = field(default_factory=list)
    baseline_eligible_test_input_paths: frozenset[str] = frozenset()
    affected_claims: list[AffectedClaim] = field(default_factory=list)


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
) -> ReconciliationProposal:
    """Executes real verification for every finding `detect_source_
    changes`/`detect_newly_coverable_checks` reported, persists and
    round-trip-verifies every fresh `OracleResult` (durable convention,
    `decisions/0096`), and returns the per-Claim contributing findings
    plus shared-baseline eligibility (`ReconciliationProposal`) ready
    for `write_source_reconciliation_manifest`. Called only from
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

    # Phase 89A corrective pass, defect A: the same bridge map used to
    # decide "does this Claim's own existing Evidence already reach a
    # single, unambiguous check" for every pathway below -- computed
    # once, here, never re-derived differently per pathway.
    evidence_check_ids = _test_evidence_check_id_map(records, contract, project_root)

    out: list[ContributingFinding] = []
    affected: list[AffectedClaim] = []

    def _gate_claim_scope(claim_id: str, *, bridging: bool) -> tuple[object, str, str]:
        """Resolves `claim_id`'s own record and scope category. Returns
        `(claim_rec_or_None, category, reason)` -- `category` is
        `"missing"` if the Claim no longer exists, `"superseded"`,
        `"aggregate"`, `"ambiguous"`, or `"eligible"`. `bridging=False`
        skips the ambiguous check (detector (b), which resolves a
        single check to a single Claim via a different, already
        fail-closed mechanism -- `detect_newly_coverable_checks`'s own
        `depends_on`-length guard)."""
        claim_rec = records.get(claim_id)
        if claim_rec is None:
            return None, "missing", f"{claim_id} no longer exists"
        bridging_check_ids = (
            _claim_bridging_check_ids(claim_rec, evidence_check_ids) if bridging else None
        )
        category, reason = _ki.claim_scope_category(
            claim_rec, bridging_check_ids=bridging_check_ids,
        )
        return claim_rec, category, reason

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
                        claim_rec, category, scope_reason = _gate_claim_scope(
                            claim_id, bridging=True,
                        )
                        if category == "missing":
                            continue
                        if category == "superseded":
                            continue
                        if category != "eligible":
                            affected.append(AffectedClaim(
                                claim_id=claim_id, check_id=check_id,
                                contract_id=fresh_result.contract_id, run_id=fresh_result.run_id,
                                category=category, reason=scope_reason,
                                outcome=fresh_outcome, resolution="symbol_change",
                                source_path=range_report["path"],
                            ))
                            continue
                        if (
                            classification == "VERIFIED_SCOPE"
                            and label == "re_confirmed"
                            and claim_rec.fields.get("evidence_support_state") == "supported"
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
                            repository_revision=_repo_revision(
                                repo_root, fresh_result=fresh_result,
                            ),
                            source_path=range_report["path"],
                            resolution="symbol_change",
                        ))

    # --- test_input_change findings: direct execution, no symbol. ---
    # A single check_id can be named by more than one shared test-input
    # finding in this same run (e.g. a check whose own `test_input_paths`
    # lists two files that both changed); execute it at most once per
    # call and reuse the result for every finding that names it --
    # deduplicating execution, never check identity or per-path
    # attribution (Phase 89A corrective pass, defect A).
    test_input_findings = [
        f for f in (source_changes.changed if source_changes else [])
        if f.resolution == "test_input_change"
    ]
    required_by_path: dict[str, set[str]] = {}
    for f in test_input_findings:
        if f.check_id:
            required_by_path.setdefault(f.path, set()).add(f.check_id)
    accounted_by_path: dict[str, set[str]] = {}
    executed_check_results: dict[str, tuple[object, bool]] = {}

    for f in test_input_findings:
        check = contract.check_by_id(f.check_id)
        if check is None or not f.claim_ids:
            continue
        if f.check_id in executed_check_results:
            fresh_result, ok = executed_check_results[f.check_id]
        else:
            with _chdir(project_root):
                fresh_result = _oracle.evaluate_check(
                    contract, check, contract_path=contract_path, repo_root=repo_root,
                    raw_output_dir=_durable_raw_output_dir(slug),
                )
            _, ok, _reason = _persist_and_verify(project_root, slug, fresh_result)
            executed_check_results[f.check_id] = (fresh_result, ok)
        if not ok or fresh_result.outcome == "INVALID":
            continue
        accounted_by_path.setdefault(f.path, set()).add(f.check_id)
        label = _label_for(historical_results, f.check_id, fresh_result.outcome)
        target_field = (
            "contradicting_evidence" if fresh_result.outcome == "FAIL" else "supporting_evidence"
        )
        for claim_id in f.claim_ids:
            claim_rec, category, scope_reason = _gate_claim_scope(claim_id, bridging=True)
            if category == "missing":
                continue
            if category == "superseded":
                continue
            if category != "eligible":
                affected.append(AffectedClaim(
                    claim_id=claim_id, check_id=f.check_id,
                    contract_id=fresh_result.contract_id, run_id=fresh_result.run_id,
                    category=category, reason=scope_reason,
                    outcome=fresh_result.outcome, resolution="test_input_change",
                    source_path=f.path,
                ))
                continue
            if (
                label == "re_confirmed"
                and claim_rec.fields.get("evidence_support_state") == "supported"
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
                repository_revision=_repo_revision(repo_root, fresh_result=fresh_result),
                source_path=f.path,
                resolution="test_input_change",
            ))

    baseline_eligible_test_input_paths = frozenset(
        p for p, required in required_by_path.items()
        if required <= accounted_by_path.get(p, set())
    )

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
        claim_rec, category, scope_reason = _gate_claim_scope(nc.claim_id, bridging=False)
        if category == "missing":
            continue
        if category == "superseded":
            continue
        if category != "eligible":
            affected.append(AffectedClaim(
                claim_id=nc.claim_id, check_id=nc.check_id,
                contract_id=fresh_result.contract_id, run_id=fresh_result.run_id,
                category=category, reason=scope_reason,
                outcome=fresh_result.outcome, resolution="",
            ))
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
            repository_revision=_repo_revision(repo_root, fresh_result=fresh_result),
        ))

    return ReconciliationProposal(
        findings=out, baseline_eligible_test_input_paths=baseline_eligible_test_input_paths,
        affected_claims=affected,
    )


# ---------------------------------------------------------------------------
# §5.3 — write_source_reconciliation_manifest (new sibling writer,
# mirroring write_doc_candidates_to_manifests exactly)
# ---------------------------------------------------------------------------


def write_source_reconciliation_manifest(
    project_root: Path, slug: str, findings: list[ContributingFinding],
    *, repo_root: Path | None = None, target_graph_db: Path | None = None,
    baseline_eligible_test_input_paths: frozenset[str] | None = None,
    affected_claims: list[AffectedClaim] | None = None,
) -> Path | None:
    """One manifest item **per Claim** (never per-finding, §4.8) —
    every contributing finding against the same Claim in one run is
    merged into that Claim's own single item, closing the self-conflict
    risk by construction (no two pending items can ever race the same
    Claim's own content hash within one `apply_manifest` batch).

    `repo_root`/`target_graph_db`, when given, let this function also
    record, per item, the distinct tracked file(s) (and their current
    content hash) whose drift produced its own contributing findings
    (`ContributingFinding.source_path`, detector (a) only) —
    `advance_baselines_for_applied_item` reads these back, after a
    real, successful `apply`, to advance `source-baseline.toml` for
    exactly the files this item's own acceptance resolved (`CLAUDE.md`
    §1 L-087: a baseline never advances on detection alone). A `path`
    not indexed by `target_graph_db` (a non-Python fixture) falls back
    to a direct content hash of the live file, mirroring `detect_
    source_changes`'s own fallback (bounded check 1).

    `baseline_eligible_test_input_paths` (from `propose_reconciliation`,
    defect A) gates a shared `test_input_change` path out of **every**
    item's `contributing_source_paths` this round unless *every* check
    that shares it was successfully, validly re-verified -- a
    `symbol_change`/detector-(b) path is never gated (unaffected by
    this parameter).

    `affected_claims` (Phase 89A corrective pass, defect A) is written
    as a separate, purely informational `[[affected_claims]]` array --
    never an `items` entry, so `apply_manifest`'s own dispatch (which
    only ever reads `data["items"]`) can never act on one: a broader
    Claim excluded from automatic mutation is reported here, visibly,
    rather than silently discarded, but can only ever be updated
    through a separately justified, human-reviewed mechanism.

    Manifest creation is collision-resistant (Phase 89A corrective
    pass, defect B): two calls landing within the same one-second-
    precision timestamp never race the same filename -- see
    `knowledge_intermediate._write_manifest_exclusive`."""
    findings = findings or []
    affected_claims = affected_claims or []
    if not findings and not affected_claims:
        return None
    eligible_paths = baseline_eligible_test_input_paths or frozenset()
    by_claim: dict[str, list[ContributingFinding]] = {}
    for f in findings:
        by_claim.setdefault(f.claim_id, []).append(f)

    sdir = _ki.slug_dir(project_root, slug)
    records = _ki.load_slug_records(sdir)
    ts = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    data: dict = {
        "created": datetime.now(UTC).isoformat(),
        "slug": slug,
        "items": [],
    }
    for claim_id, claim_findings in sorted(by_claim.items()):
        claim = records.get(claim_id)
        if claim is None:
            continue
        base_hash = _ki.sha256_text(claim.path.read_text(encoding="utf-8"))
        touched_paths = sorted({
            f.source_path for f in claim_findings
            if f.source_path and (
                f.resolution != "test_input_change" or f.source_path in eligible_paths
            )
        })
        touched_hashes = []
        if target_graph_db is not None:
            for p in touched_paths:
                h = _load_file_hash(target_graph_db, p)
                if h is None and repo_root is not None:
                    live_p = repo_root / p
                    if live_p.is_file():
                        h = _oracle.sha256_file(live_p)
                touched_hashes.append(h or "")
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
    data["affected_claims"] = [
        {
            "claim_id": a.claim_id,
            "check_id": a.check_id,
            "contract_id": a.contract_id,
            "run_id": a.run_id,
            "category": a.category,
            "reason": a.reason,
            "outcome": a.outcome,
            "resolution": a.resolution,
            "source_path": a.source_path or "",
        }
        for a in affected_claims
    ]
    if not data["items"] and not data["affected_claims"]:
        return None

    def _render(stem: str) -> str:
        data["manifest_id"] = f"{slug}@{stem}"
        return _ki._serialize_manifest(data)

    return _ki._write_manifest_exclusive(
        _ki.reconciliation_dir(project_root, slug), f"{ts}-source", _render,
    )


@dataclass
class PendingContradiction:
    """One still-genuinely-open contradicting finding, surfaced by
    `pending_contradicting_findings` for `knowledge_api.find_gaps`'s new
    `claim_contradicted_by_fresh_check` gap kind (Phase 89 Stage 89B,
    plan §5.4)."""
    claim_id: str
    check_id: str
    contract_id: str
    run_id: str
    label: str  # "regression" | "newly_discovered_failure"
    manifest_path: str
    live_reconfirmed: bool = True  # False: the item's own recorded repo_root
    # was unreachable, so only the contract-relative checks (contract hash,
    # raw-output tamper, scope match) could run -- the tested-subject/
    # test-input digests were trusted as recorded, not live-recomputed.


def pending_contradicting_findings(
    project_root: Path, slug: str, *, repo_root: Path | None = None,
) -> list[PendingContradiction]:
    """Scans every manifest already written for `slug` (the established
    read-only scanning convention this module's own callers already use
    elsewhere, e.g. `knowledge_intermediate._existing_pending_doc_
    region_edit_keys`) for a still-genuinely-open `source_reconciliation`
    item's own contradicting contributing finding(s) -- the data behind
    `find_gaps`'s new `claim_contradicted_by_fresh_check` gap kind (plan
    §5.4). Purely read-only: never writes to a manifest, a Claim, or
    anything else.

    Never trusts a manifest item's own cached fields at face value:

    - an item already `state == "applied"`, or `decision == "reject"`,
      is never genuinely pending -- skipped immediately, mirroring
      `apply_manifest`'s own identical checks.
    - the target Claim's own *current* scope category is independently
      re-checked (`claim_scope_category`) -- an aggregate/superseded
      Claim is never reported here, since it is already visible via
      this same manifest's own `affected_claims` array; reporting it a
      second time, differently, under this new gap kind would be
      confusing, not merely redundant, and this mechanism must never
      promote a broader Claim's own status either way (dispatch's own
      explicit "respect the Stage 89A Claim-scope eligibility rules").
    - the cited `OracleResult` is independently re-parsed and
      re-validated against the *live* contract (`evaluate_result_
      precedence`) -- an invalid, tampered, or since-superseded result
      is excluded, never reported as a trustworthy pending contradiction.
      Only a finding that still, genuinely, re-validates as `FAIL` is
      reported; the manifest's own cached `"regression"`/`"newly_
      discovered_failure"` label is still used for that distinction,
      since it describes history *at detection time* (whether a
      historical `PASS` existed), which live re-validation of the fresh
      result alone could never recompute differently.
    - when the item's own recorded `repo_root` is unreachable (a
      cleaned-up scratch checkout, a different machine), this never
      makes the finding vanish -- it falls through to a contract-
      relative-only re-validation (the same pre-existing behaviour
      `evaluate_result_precedence` already has for `repo_root=None`:
      contract hash, raw-output tamper, and scope checks still run; only
      the tested-subject/test-input digest recomputation is skipped) and
      is still reported, with `live_reconfirmed=False`, rather than
      either silently disappearing (the corrected defect) or being
      misrepresented as a fully live-reconfirmed `FAIL`.
    - a finding whose own `(contract_id, check_id, run_id)` already has
      a canonical Evidence record cited in the *live* Claim's own
      `contradicting_evidence` field is already durably resolved --
      applied via this exact manifest item, a sibling manifest citing
      the identical run (the collision/duplicate-manifest case), or a
      hand-applied edit -- even if this particular manifest file's own
      `state` field was never updated to say so. Skipped.

    Deterministically deduplicated by `(claim_id, check_id, run_id)`
    across every manifest file scanned for this slug, sorted for stable
    output -- the same run reported by two different pending manifests
    (e.g. one superseded by a re-run of `verify-changes`) is surfaced
    exactly once.
    """
    import tomllib

    rdir = _ki.reconciliation_dir(project_root, slug)
    if not rdir.is_dir():
        return []
    sdir = _ki.slug_dir(project_root, slug)
    records = _ki.load_slug_records(sdir)
    contract_path = project_root / "planning" / "contracts" / slug / "oracle-contract.yaml"
    try:
        contract = _oracle.parse_oracle_contract(contract_path)
    except (_oracle.OracleSchemaError, OSError):
        return []
    results_dir = project_root / "planning" / "contracts" / slug / "results"

    found: dict[tuple[str, str, str], PendingContradiction] = {}
    for manifest_path in sorted(rdir.glob("*.toml")):
        try:
            data = tomllib.loads(manifest_path.read_text(encoding="utf-8"))
        except (tomllib.TOMLDecodeError, OSError):
            continue
        for item in data.get("items", []):
            if item.get("kind") != "source_reconciliation":
                continue
            if item.get("state") == "applied" or item.get("decision") == "reject":
                continue
            record_id = item.get("record_id", "")
            claim = records.get(record_id)
            if claim is None:
                continue
            scope_category, _reason = _ki.claim_scope_category(claim)
            if scope_category != "eligible":
                continue
            item_repo_root_str = item.get("repo_root", "")
            item_repo_root = Path(item_repo_root_str) if item_repo_root_str else repo_root
            live_reconfirmed = item_repo_root is not None and item_repo_root.is_dir()
            # Phase 89 Stage 89B corrective pass: an unreachable repo_root
            # (a scratch checkout cleaned up, a different machine, a
            # transient mount) must never make a genuinely still-pending,
            # unreviewed contradiction silently vanish from find_gaps --
            # that would be a false "no gaps found" impression for an
            # unresolved finding, the opposite failure mode from what this
            # mechanism exists to prevent. Falling through with
            # `validation_repo_root = None` below still runs the real
            # contract-relative checks (contract hash, raw-output tamper,
            # scope match) -- only the tested-subject/test-input digest
            # recomputation is skipped, exactly `evaluate_result_
            # precedence`'s own documented, pre-existing behaviour for a
            # missing repo_root (never a new leniency invented here).
            validation_repo_root = item_repo_root if live_reconfirmed else None
            contract_ids = item.get("contributing_contract_ids", [])
            check_ids = item.get("contributing_check_ids", [])
            run_ids = item.get("contributing_run_ids", [])
            labels = item.get("contributing_labels", [])
            target_fields = item.get("contributing_target_fields", [])
            for i in range(len(check_ids)):
                if i >= len(target_fields) or target_fields[i] != "contradicting_evidence":
                    continue
                contract_id = contract_ids[i] if i < len(contract_ids) else ""
                check_id = check_ids[i]
                run_id = run_ids[i] if i < len(run_ids) else ""
                label = labels[i] if i < len(labels) else "regression"
                key = (record_id, check_id, run_id)
                if key in found:
                    continue
                existing_ev = _ki._find_existing_evidence_for_run(
                    project_root, records, contract_id, check_id, run_id
                )
                if existing_ev is not None:
                    live_contradicting = _ki._extract_id_strings(
                        claim.fields.get("contradicting_evidence", "")
                    )
                    if existing_ev in live_contradicting:
                        continue  # already durably resolved; stale manifest entry
                result_path = results_dir / f"{check_id}--{run_id}.yaml"
                if not result_path.is_file():
                    continue
                try:
                    result = _oracle.parse_oracle_result(result_path)
                except _oracle.OracleSchemaError:
                    continue
                if (result.contract_id, result.check_id, result.run_id) != (
                    contract_id, check_id, run_id,
                ):
                    continue
                check = contract.check_by_id(check_id)
                if check is None:
                    continue
                previous_cwd = Path.cwd()
                os.chdir(project_root)
                try:
                    effective_outcome, _reason2 = _oracle.evaluate_result_precedence(
                        result, contract, check, contract_path=contract_path,
                        repo_root=validation_repo_root,
                    )
                finally:
                    os.chdir(previous_cwd)
                if effective_outcome != "FAIL":
                    continue
                found[key] = PendingContradiction(
                    claim_id=record_id, check_id=check_id, contract_id=contract_id,
                    run_id=run_id, label=label,
                    manifest_path=str(manifest_path.relative_to(project_root)),
                    live_reconfirmed=live_reconfirmed,
                )
    return [found[k] for k in sorted(found)]


def advance_baselines_for_applied_item(
    project_root: Path, slug: str, item: dict, *, manifest_items: list[dict],
) -> None:
    """Called by the CLI (`cli.py::knowledge_apply_manifest`) only for
    an item `apply_manifest` reports as `state == "applied"` — never
    automatically, never on detection alone (`CLAUDE.md` §1 L-087).
    Advances `source-baseline.toml` for the tracked file(s) this item's
    own acceptance resolved, using the content hash recorded on the
    item at `verify-changes` time (never re-derived from a possibly
    different, later live state) -- **except** for a path shared with
    a sibling item (`manifest_items`, every item in the same manifest)
    that has not itself reached `state == "applied"` yet: a path's
    baseline only ever advances once *every* item citing it has been
    applied, so a still-pending or rejected sibling check can never be
    silently waived just because another check sharing the same file
    was resolved (Phase 89A corrective pass, defect A).

    `manifest_items` is required, not optional, so this cross-item
    guard can never be silently skipped by a caller that forgets to
    pass it. Required to be **idempotent**: calling this again for an
    item already `state == "applied"` is a harmless no-op (`establish_
    source_baseline` unconditionally overwrites with the same value),
    which is exactly what makes the CLI's own full, repeated pass over
    every already-applied item safe to retry after an interruption
    between a successful `apply_manifest` and this function completing
    (defect C, scenario 4)."""
    paths = item.get("contributing_source_paths", [])
    hashes = item.get("contributing_source_hashes", [])
    for path, content_hash in zip(paths, hashes):
        if not content_hash:
            continue
        siblings = [
            it for it in manifest_items
            if path in it.get("contributing_source_paths", [])
        ]
        if not all(it.get("state") == "applied" for it in siblings):
            continue  # at least one check sharing this file is still unresolved
        advance_source_baseline_after_apply(project_root, slug, path, content_hash)
