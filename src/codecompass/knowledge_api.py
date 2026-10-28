"""Phase 84 -- Consolidated Knowledge API.

One stable, **read-only**, typed query/traversal interface over
CodeCompass's existing knowledge: `context-graph.db` (mechanical facts),
`planning/knowledge/` (reconciled Observation/Evidence/Claim/Derivation/
Decision/Requirement records), and `planning/contracts/` (behavioural
contracts and oracle results). See
`planning/phase-84-consolidated-knowledge-api.md` and `decisions/0084`/
`0085` for the full design -- this module implements it, it does not
re-derive it.

**Logical consolidation only.** No new database, no new schema, no new
persisted identity. Every function here reads `graph.py`/
`knowledge_intermediate.py`/`oracle.py`'s own existing, already-shipped
surface -- never a parallel parser, never a mutation. Confirmed by a
dedicated test (`tests/test_knowledge_api.py::TestNoMutationPath`)
inspecting this module's own source text for any writer-function
reference.

Connections to `context-graph.db` are opened **read-only** via a
`file:...?mode=ro` URI, deliberately never through `graph.open_graph`
(which creates the file and runs schema migrations as a side effect of
opening it -- exactly the kind of incidental mutation this module must
never perform). A missing or unreadable graph database is reported as
an absent/unconfirmed fact, never silently created.

Three-way response shape (plan §3.0 point 8), used by every public
function via `ApiResponse`:

- `"result"` -- at least one real item was found.
- `"empty"` -- the requested identity, slug, or query matched nothing at
  all (never a recorded obligation).
- `"gap"` -- reserved for `trace_evidence`/`find_gaps`: a specific,
  nameable obligation (a required check, a cited claim) exists but no
  current evidence resolves it. Never conflated with `"empty"`.

Authority tags (plan §3.C), attached to every `KnowledgeResult`:
`primary_evidence` (live source, read directly), `derived_index`
(`context-graph.db` -- what was last recorded, not current behaviour),
`stated_intent` (an accepted Decision), `accepted_obligation` (a
Requirement), `scoped_verification` (an Oracle result, within its exact
tested scope and revision), `editable_projection` (an
`intermediate/*.md` presentation projection), `presentation_artifact`
(generated documentation). A `derived_index` fact never stands in for
`scoped_verification` -- both are surfaced, visibly separate, never
merged into one "verified" answer.
"""

from __future__ import annotations

import json
import re
import sqlite3
import subprocess
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath

from codecompass import knowledge_intermediate as _ki
from codecompass import oracle as _oracle

_DB_FILENAME = "context-graph.db"

# ---------------------------------------------------------------------------
# §3.C authority tags
# ---------------------------------------------------------------------------

AUTHORITY_PRIMARY_EVIDENCE = "primary_evidence"
AUTHORITY_DERIVED_INDEX = "derived_index"
AUTHORITY_STATED_INTENT = "stated_intent"
AUTHORITY_ACCEPTED_OBLIGATION = "accepted_obligation"
AUTHORITY_SCOPED_VERIFICATION = "scoped_verification"
AUTHORITY_EDITABLE_PROJECTION = "editable_projection"
AUTHORITY_PRESENTATION_ARTIFACT = "presentation_artifact"

# Canonical-record-kind -> default authority, when no more specific rule
# (an Evidence record's own `evidence_kind`) applies.
_RECORD_KIND_AUTHORITY = {
    "decision": AUTHORITY_STATED_INTENT,
    "requirement": AUTHORITY_ACCEPTED_OBLIGATION,
    "observation": AUTHORITY_PRIMARY_EVIDENCE,
    "claim": AUTHORITY_DERIVED_INDEX,
    "derivation": AUTHORITY_DERIVED_INDEX,
}
_EVIDENCE_KIND_AUTHORITY = {
    "source": AUTHORITY_PRIMARY_EVIDENCE,
    "test": AUTHORITY_SCOPED_VERIFICATION,
    "doc": AUTHORITY_DERIVED_INDEX,
}


def _record_authority(record: "_ki.KnowledgeRecord") -> str:
    if record.kind == "evidence":
        return _EVIDENCE_KIND_AUTHORITY.get(record.fields.get("evidence_kind", ""), AUTHORITY_DERIVED_INDEX)
    return _RECORD_KIND_AUTHORITY.get(record.kind, AUTHORITY_DERIVED_INDEX)


# ---------------------------------------------------------------------------
# Typed response shapes
# ---------------------------------------------------------------------------


@dataclass
class ConsistencyEnvelope:
    """§3.B -- five already-existing values, bundled at response time.
    Never persisted; recomputed on every call. `status` is `"current"`
    only when every applicable piece could be positively (re)confirmed;
    `"unconfirmed"` when a piece exists but could not be live-reconfirmed
    (e.g. no `repo_root` supplied); `"stale"` when a piece was *actively*
    found to disagree with the live source."""

    source_revision: str | None = None
    knowledge_revision: str | None = None
    graph_revision: str | None = None
    contract_revision: str | None = None
    evidence_currency: str = "unknown"  # "current" | "unconfirmed" | "absent"
    status: str = "current"  # "current" | "stale" | "unconfirmed"
    reasons: list[str] = field(default_factory=list)


@dataclass
class KnowledgeResult:
    id: str
    kind: str
    authority: str
    summary: str
    details: dict = field(default_factory=dict)
    consistency: ConsistencyEnvelope = field(default_factory=ConsistencyEnvelope)


@dataclass
class Gap:
    kind: str  # "unverified_required_scope" | "contradiction" | "stale_test_citation" | "missing_contract"
    subject_id: str | None
    scope: str | None
    reason: str


@dataclass
class ApiResponse:
    status: str  # "result" | "empty" | "gap"
    results: list[KnowledgeResult] = field(default_factory=list)
    gaps: list[Gap] = field(default_factory=list)
    message: str | None = None

    def to_dict(self) -> dict:
        return {
            "status": self.status,
            "results": [
                {**asdict(r), "consistency": asdict(r.consistency)} for r in self.results
            ],
            "gaps": [asdict(g) for g in self.gaps],
            "message": self.message,
        }


def _empty(message: str) -> ApiResponse:
    return ApiResponse(status="empty", message=message)


def _result(results: list[KnowledgeResult], message: str | None = None) -> ApiResponse:
    return ApiResponse(status="result", results=results, message=message)


def _gap_response(gaps: list[Gap], message: str | None = None) -> ApiResponse:
    status = "gap" if gaps else "empty"
    return ApiResponse(status=status, gaps=gaps, message=message)


# ---------------------------------------------------------------------------
# Natural-key identity scheme (§3.A) -- pure functions over columns that
# already exist; no new persisted identifier anywhere.
# ---------------------------------------------------------------------------


def _normalize_path(path: str) -> str:
    return PurePosixPath(path.strip()).as_posix()


def symbol_identity(path: str, name: str, kind: str, line: int) -> str:
    """`(source_file.path, name, kind, line)` -- `source_symbols`'s own
    existing `UNIQUE` constraint, read as an identity (plan §3.A)."""
    return f"symbol:{_normalize_path(path)}:{name}:{kind}:{line}"


def vendor_identity(name: str) -> str:
    return f"vendor:{name}"


def doc_identity(path: str) -> str:
    return f"doc:{_normalize_path(path)}"


def contract_identity(contract_id: str) -> str:
    return f"contract:{contract_id}"


def check_identity(contract_id: str, check_id: str) -> str:
    return f"check:{contract_id}:{check_id}"


def result_identity(contract_id: str, check_id: str, run_id: str) -> str:
    return f"result:{contract_id}:{check_id}:{run_id}"


def _is_knowledge_record_id(id_: str) -> bool:
    return _ki._ID_PATTERN.fullmatch(id_) is not None


_SYMBOL_ID_RE = re.compile(r"^symbol:(?P<path>.+):(?P<name>[^:]+):(?P<kind>[^:]+):(?P<line>\d+)$")
_VENDOR_ID_RE = re.compile(r"^vendor:(?P<name>.+)$")
_DOC_ID_RE = re.compile(r"^doc:(?P<path>.+)$")
_CONTRACT_ID_RE = re.compile(r"^contract:(?P<contract_id>.+)$")
_CHECK_ID_RE = re.compile(r"^check:(?P<contract_id>[^:]+):(?P<check_id>.+)$")
_RESULT_ID_RE = re.compile(r"^result:(?P<contract_id>[^:]+):(?P<check_id>[^:]+):(?P<run_id>.+)$")


# ---------------------------------------------------------------------------
# Read-only graph access -- never `graph.open_graph` (creates + migrates).
# ---------------------------------------------------------------------------


def _open_ro(project_root: Path) -> sqlite3.Connection | None:
    db_path = project_root / _DB_FILENAME
    if not db_path.is_file():
        return None
    try:
        return sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    except sqlite3.OperationalError:
        return None


def _graph_meta(conn: sqlite3.Connection) -> dict[str, str | None]:
    out: dict[str, str | None] = {}
    for key in ("schema_version", "last_deterministic_rebuild_at", "source_index_version"):
        row = conn.execute("SELECT value FROM meta WHERE key = ?", (key,)).fetchone()
        out[key] = row[0] if row is not None else None
    return out


def _graph_revision_string(meta: dict[str, str | None]) -> str | None:
    if meta.get("last_deterministic_rebuild_at") is None and meta.get("schema_version") is None:
        return None
    return (
        f"schema={meta.get('schema_version')};"
        f"rebuilt_at={meta.get('last_deterministic_rebuild_at')};"
        f"source_index={meta.get('source_index_version')}"
    )


# ---------------------------------------------------------------------------
# Cross-slug record access
# ---------------------------------------------------------------------------


def _all_records(project_root: Path) -> dict[str, _ki.KnowledgeRecord]:
    """Every canonical record, across every slug, keyed by its own id --
    matches `_find_record_in_any_slug`'s own established cross-slug
    posture, built once per call (slug counts are small; never cached
    across calls, since this module must always read current state)."""
    merged: dict[str, _ki.KnowledgeRecord] = {}
    for slug in _ki._list_slugs(project_root):
        merged.update(_ki.load_slug_records(_ki.slug_dir(project_root, slug)))
    return merged


def _owning_slug(project_root: Path, record: _ki.KnowledgeRecord) -> str:
    return record.path.parent.name


def _contracts_root(project_root: Path) -> Path:
    return project_root / "planning" / "contracts"


def _slug_contract_path(project_root: Path, slug: str) -> Path:
    return _contracts_root(project_root) / slug / "oracle-contract.yaml"


def _slug_results_dir(project_root: Path, slug: str) -> Path:
    return _contracts_root(project_root) / slug / "results"


def _load_slug_results(project_root: Path, slug: str) -> list[_oracle.OracleResult]:
    results_dir = _slug_results_dir(project_root, slug)
    out: list[_oracle.OracleResult] = []
    if not results_dir.is_dir():
        return out
    for result_path in sorted(results_dir.glob("*.yaml")):
        try:
            out.append(_oracle.parse_oracle_result(result_path))
        except _oracle.OracleSchemaError:
            continue
    return out


def _find_contract(project_root: Path, contract_id: str) -> tuple[str, _oracle.OracleContract, Path] | None:
    """`(slug, contract, contract_path)` for the slug whose own
    `oracle-contract.yaml` has this `contract_id` -- the contract's own
    natural key, resolved by scanning (there are only ever a handful of
    slugs; no index needed)."""
    contracts_root = _contracts_root(project_root)
    if not contracts_root.is_dir():
        return None
    for slug_path in sorted(p for p in contracts_root.iterdir() if p.is_dir()):
        contract_path = slug_path / "oracle-contract.yaml"
        if not contract_path.is_file():
            continue
        try:
            contract = _oracle.parse_oracle_contract(contract_path)
        except _oracle.OracleSchemaError:
            continue
        if contract.contract_id == contract_id:
            return slug_path.name, contract, contract_path
    return None


# ---------------------------------------------------------------------------
# get()
# ---------------------------------------------------------------------------


def get(project_root: Path, record_id: str, *, repo_root: Path | None = None) -> ApiResponse:
    """Retrieve one item by its own stable identity (plan §4.1). Dispatches
    on the id's own shape -- a canonical `REQ-`/`CL-`/`EV-`/`OBS-`/`DE-`/
    `DEC-` id, or one of this module's own natural-key identities (§3.A).
    `"empty"` if the id is well-formed but resolves to nothing; this
    function never reports `"gap"` -- identity resolution is a different
    question from obligation coverage (`epistemic_status`/`find_gaps`).
    """
    if _is_knowledge_record_id(record_id):
        return _get_knowledge_record(project_root, record_id, repo_root=repo_root)

    m = _SYMBOL_ID_RE.match(record_id)
    if m:
        return _get_symbol(project_root, m.group("path"), m.group("name"), m.group("kind"), int(m.group("line")))

    m = _VENDOR_ID_RE.match(record_id)
    if m:
        return _get_vendor(project_root, m.group("name"))

    m = _DOC_ID_RE.match(record_id)
    if m:
        return _get_doc(project_root, m.group("path"))

    m = _CONTRACT_ID_RE.match(record_id)
    if m:
        return _get_contract(project_root, m.group("contract_id"))

    m = _CHECK_ID_RE.match(record_id)
    if m:
        return _get_check(project_root, m.group("contract_id"), m.group("check_id"))

    m = _RESULT_ID_RE.match(record_id)
    if m:
        return _get_result(project_root, m.group("contract_id"), m.group("check_id"), m.group("run_id"))

    return _empty(f"{record_id!r} does not match any known identity shape")


def _get_knowledge_record(
    project_root: Path, record_id: str, *, repo_root: Path | None = None
) -> ApiResponse:
    records = _all_records(project_root)
    record = records.get(record_id)
    if record is None:
        return _empty(f"no knowledge record {record_id!r} found under any planning/knowledge/<slug>")
    slug = _owning_slug(project_root, record)
    consistency = _knowledge_consistency(project_root, record, records, repo_root=repo_root)
    result = KnowledgeResult(
        id=record.record_id,
        kind=record.kind,
        authority=_record_authority(record),
        summary=_summarize_record(record),
        details={"slug": slug, "fields": dict(record.fields),
                 "provenance_label": _ki.derive_provenance_label(record, records)},
        consistency=consistency,
    )
    return _result([result])


def _summarize_record(record: _ki.KnowledgeRecord) -> str:
    for key in ("statement", "decides", "what_it_shows", "what_was_done"):
        value = record.fields.get(key)
        if value:
            return " ".join(value.split())[:280]
    return f"{record.kind} {record.record_id}"


def _knowledge_consistency(
    project_root: Path,
    record: _ki.KnowledgeRecord,
    records: dict[str, _ki.KnowledgeRecord],
    *,
    repo_root: Path | None = None,
) -> ConsistencyEnvelope:
    knowledge_revision = _ki.sha256_text(record.path.read_text(encoding="utf-8"))
    conn = _open_ro(project_root)
    graph_revision = None
    if conn is not None:
        try:
            graph_revision = _graph_revision_string(_graph_meta(conn))
        finally:
            conn.close()

    # A slug's contract_id is conventionally the slug's own owning
    # Requirement's id (confirmed real: `balance-from-spec`'s contract_id
    # is `REQ-BFS-001`) -- resolved by owning slug, never guessed from an
    # unrelated field.
    slug = _owning_slug(project_root, record)
    found = _find_contract_for_slug(project_root, slug)

    profile = None
    contract_revision = None
    evidence_currency = "unknown"
    status = "current"
    reasons: list[str] = []
    if found is not None:
        slug, contract, contract_path = found
        results_by_ref = _results_by_test_ref(project_root, slug)
        profile = _ki.derive_epistemic_profile(
            record, records, oracle_contract=contract,
            oracle_results_by_test_ref=results_by_ref,
            contract_path=contract_path, repo_root=repo_root,
        )
        contract_revision = _oracle.sha256_file(contract_path)
        if profile.verified_scopes and not profile.unconfirmed_scopes and not profile.known_gap_scopes:
            evidence_currency = "current"
        elif profile.unconfirmed_scopes:
            evidence_currency = "unconfirmed"
            status = "unconfirmed"
            reasons.append(
                f"{len(profile.unconfirmed_scopes)} scope(s) have only a historically "
                "recorded PASS, not live-reconfirmed (no reachable repo_root supplied)"
            )
        elif profile.known_gap_scopes:
            evidence_currency = "absent"
            status = "unconfirmed"
            reasons.append(f"{len(profile.known_gap_scopes)} required scope(s) have no passing evidence at all")
        else:
            evidence_currency = "current"

    source_revision = None
    for ev_id in _ki._extract_id_strings(record.fields.get("supporting_evidence", "")) + [record.record_id]:
        ev = records.get(ev_id)
        if ev is not None and ev.fields.get("repository_revision"):
            source_revision = _KI_unquote(ev.fields["repository_revision"])
            break
    if source_revision is None and record.fields.get("repository_revision"):
        source_revision = _KI_unquote(record.fields["repository_revision"])

    return ConsistencyEnvelope(
        source_revision=source_revision,
        knowledge_revision=knowledge_revision,
        graph_revision=graph_revision,
        contract_revision=contract_revision,
        evidence_currency=evidence_currency,
        status=status,
        reasons=reasons,
    )


def _KI_unquote(value: str) -> str:
    return _ki._unquote(value)


def _results_by_test_ref(project_root: Path, slug: str) -> dict[str, _oracle.OracleResult]:
    by_ref: dict[str, _oracle.OracleResult] = {}
    results_dir = _slug_results_dir(project_root, slug)
    if not results_dir.is_dir():
        return by_ref
    for result_path in sorted(results_dir.glob("*.yaml")):
        try:
            result = _oracle.parse_oracle_result(result_path)
        except _oracle.OracleSchemaError:
            continue
        rel = str(result_path.relative_to(project_root))
        by_ref[rel] = result
    return by_ref


def _find_contract_for_slug(project_root: Path, slug: str) -> tuple[str, _oracle.OracleContract, Path] | None:
    contract_path = _slug_contract_path(project_root, slug)
    if not contract_path.is_file():
        return None
    try:
        contract = _oracle.parse_oracle_contract(contract_path)
    except _oracle.OracleSchemaError:
        return None
    return slug, contract, contract_path


def _get_symbol(project_root: Path, path: str, name: str, kind: str, line: int) -> ApiResponse:
    conn = _open_ro(project_root)
    if conn is None:
        return _empty(f"no {_DB_FILENAME} under {project_root} -- cannot resolve a symbol identity")
    try:
        row = conn.execute(
            """
            SELECT ss.purpose, ss.exposure, sf.language, sf.content_hash
            FROM source_symbols ss JOIN source_files sf ON ss.source_file_id = sf.id
            WHERE sf.path = ? AND ss.name = ? AND ss.kind = ? AND ss.line = ?
            """,
            (_normalize_path(path), name, kind, line),
        ).fetchone()
    finally:
        conn.close()
    if row is None:
        return _empty(f"no source_symbols row for {symbol_identity(path, name, kind, line)!r}")
    purpose, exposure, language, content_hash = row

    # §3.B: re-confirm the indexed content_hash against the live file under
    # this exact project_root, when it's actually there -- a derived_index
    # fact is "current" only when positively re-confirmed, "stale" when
    # actively found to disagree, "unconfirmed" only when neither could be
    # established (the live file isn't reachable at all).
    status, reasons = "unconfirmed", [
        "derived_index fact -- live source not reachable under this project_root to re-confirm"
    ]
    live_path = project_root / path
    if content_hash is not None and live_path.is_file():
        live_hash = _oracle.sha256_file(live_path)
        if live_hash == content_hash:
            status, reasons = "current", []
        else:
            status, reasons = "stale", [
                f"live content_hash ({live_hash}) does not match the graph's own recorded "
                f"content_hash ({content_hash}) -- the graph was not re-synced against this file"
            ]

    result = KnowledgeResult(
        id=symbol_identity(path, name, kind, line),
        kind="source_symbol",
        authority=AUTHORITY_DERIVED_INDEX,
        summary=f"{kind} {name} at {path}:{line}",
        details={"path": path, "name": name, "kind": kind, "line": line,
                 "purpose": purpose, "exposure": exposure, "language": language},
        consistency=ConsistencyEnvelope(
            graph_revision=content_hash, evidence_currency="unknown", status=status, reasons=reasons,
        ),
    )
    return _result([result])


def _get_vendor(project_root: Path, name: str) -> ApiResponse:
    conn = _open_ro(project_root)
    if conn is None:
        return _empty(f"no {_DB_FILENAME} under {project_root}")
    try:
        from codecompass import graph as _graph

        profile = _graph.vendor_profile(conn, name)
    finally:
        conn.close()
    if profile is None:
        return _empty(f"no vendor named {name!r}")
    result = KnowledgeResult(
        id=vendor_identity(name), kind="vendor", authority=AUTHORITY_DERIVED_INDEX,
        summary=f"vendor {name}", details=profile,
    )
    return _result([result])


def _get_doc(project_root: Path, path: str) -> ApiResponse:
    conn = _open_ro(project_root)
    if conn is None:
        return _empty(f"no {_DB_FILENAME} under {project_root}")
    try:
        row = conn.execute(
            "SELECT kind, origin, name, description FROM doc_artifacts WHERE path = ?",
            (_normalize_path(path),),
        ).fetchone()
    finally:
        conn.close()
    if row is None:
        return _empty(f"no doc_artifacts row for {path!r}")
    kind, origin, name, description = row
    result = KnowledgeResult(
        id=doc_identity(path), kind="doc_artifact", authority=AUTHORITY_PRESENTATION_ARTIFACT,
        summary=description or path,
        details={"path": path, "doc_kind": kind, "origin": origin, "name": name},
    )
    return _result([result])


def _get_contract(project_root: Path, contract_id: str) -> ApiResponse:
    found = _find_contract(project_root, contract_id)
    if found is None:
        return _empty(f"no oracle contract with contract_id {contract_id!r}")
    slug, contract, contract_path = found
    result = KnowledgeResult(
        id=contract_identity(contract_id), kind="oracle_contract", authority=AUTHORITY_ACCEPTED_OBLIGATION,
        summary=f"oracle contract {contract_id} ({len(contract.checks)} check(s))",
        details={"slug": slug, "contract_id": contract_id, "tested_paths": contract.tested_paths,
                 "checks": [c.check_id for c in contract.checks]},
        consistency=ConsistencyEnvelope(contract_revision=_oracle.sha256_file(contract_path), status="current"),
    )
    return _result([result])


def _get_check(project_root: Path, contract_id: str, check_id: str) -> ApiResponse:
    found = _find_contract(project_root, contract_id)
    if found is None:
        return _empty(f"no oracle contract with contract_id {contract_id!r}")
    slug, contract, contract_path = found
    check = contract.check_by_id(check_id)
    if check is None:
        return _empty(f"contract {contract_id!r} has no check {check_id!r}")
    results = [r for r in _load_slug_results(project_root, slug) if r.check_id == check_id]
    aggregates = _oracle.aggregate_contract(contract, results, contract_path=contract_path)
    aggregate = next((a for a in aggregates if a.check_id == check_id), None)
    result = KnowledgeResult(
        id=check_identity(contract_id, check_id), kind="oracle_check",
        authority=AUTHORITY_ACCEPTED_OBLIGATION,
        summary=f"check {check_id} ({check.scope})",
        details={"slug": slug, "contract_id": contract_id, "check_id": check_id, "scope": check.scope,
                 "required": check.required, "check_reference": check.check_reference,
                 "aggregate_state": aggregate.state if aggregate else None,
                 "observed_outcomes": aggregate.observed_outcomes if aggregate else []},
    )
    return _result([result])


def _get_result(project_root: Path, contract_id: str, check_id: str, run_id: str) -> ApiResponse:
    found = _find_contract(project_root, contract_id)
    if found is None:
        return _empty(f"no oracle contract with contract_id {contract_id!r}")
    slug, contract, contract_path = found
    for r in _load_slug_results(project_root, slug):
        if r.check_id == check_id and r.run_id == run_id:
            check = contract.check_by_id(check_id)
            effective, reason = (None, None)
            if check is not None:
                effective, reason = _oracle.evaluate_result_precedence(r, contract, check, contract_path=contract_path)
            result = KnowledgeResult(
                id=result_identity(contract_id, check_id, run_id), kind="oracle_result",
                authority=AUTHORITY_SCOPED_VERIFICATION,
                summary=f"result {run_id} for {check_id}: recorded={r.outcome}, effective={effective}",
                details={"slug": slug, **{k: v for k, v in asdict(r).items()}},
                consistency=ConsistencyEnvelope(
                    contract_revision=r.oracle_contract_content_hash,
                    evidence_currency="current" if effective == "PASS" else "unconfirmed",
                    status="stale" if effective == "INVALID" else "current",
                    reasons=[reason] if reason else [],
                ),
            )
            return _result([result])
    return _empty(f"no oracle result {run_id!r} for check {check_id!r} under contract {contract_id!r}")


# ---------------------------------------------------------------------------
# search()
# ---------------------------------------------------------------------------


def search(project_root: Path, text: str, kinds: list[str] | None = None) -> ApiResponse:
    """Free-text discovery across knowledge-record fields and oracle
    contract/check ids (plan §4.1). `kinds`, when given, restricts to
    these record kinds (`"requirement"`, `"claim"`, `"evidence"`,
    `"observation"`, `"decision"`, `"derivation"`, `"oracle_contract"`,
    `"oracle_check"`). Bounded substring match -- never an embedding
    search, never an AI call (plan §5's own exclusion of unnecessary AI
    inference)."""
    needle = text.strip().lower()
    if not needle:
        return _empty("empty search text")
    results: list[KnowledgeResult] = []
    records = _all_records(project_root)
    for record in records.values():
        if kinds and record.kind not in kinds:
            continue
        haystack = " ".join([record.record_id, record.kind, *record.fields.values()]).lower()
        if needle in haystack:
            slug = _owning_slug(project_root, record)
            results.append(KnowledgeResult(
                id=record.record_id, kind=record.kind, authority=_record_authority(record),
                summary=_summarize_record(record), details={"slug": slug},
            ))
    if not kinds or "oracle_contract" in kinds or "oracle_check" in kinds:
        contracts_root = _contracts_root(project_root)
        if contracts_root.is_dir():
            for slug_path in sorted(p for p in contracts_root.iterdir() if p.is_dir()):
                contract_path = slug_path / "oracle-contract.yaml"
                if not contract_path.is_file():
                    continue
                try:
                    contract = _oracle.parse_oracle_contract(contract_path)
                except _oracle.OracleSchemaError:
                    continue
                if needle in contract.contract_id.lower():
                    results.append(KnowledgeResult(
                        id=contract_identity(contract.contract_id), kind="oracle_contract",
                        authority=AUTHORITY_ACCEPTED_OBLIGATION,
                        summary=f"oracle contract {contract.contract_id}",
                        details={"slug": slug_path.name},
                    ))
                for check in contract.checks:
                    if needle in check.check_id.lower() or needle in check.scope.lower():
                        results.append(KnowledgeResult(
                            id=check_identity(contract.contract_id, check.check_id), kind="oracle_check",
                            authority=AUTHORITY_ACCEPTED_OBLIGATION,
                            summary=f"check {check.check_id} ({check.scope})",
                            details={"slug": slug_path.name, "contract_id": contract.contract_id},
                        ))
    if not results:
        return _empty(f"no match for {text!r}")
    return _result(results)


# ---------------------------------------------------------------------------
# traverse()
# ---------------------------------------------------------------------------

_FORWARD_FIELD_RELATIONS = {
    "depends_on": "depends_on",
    "supporting_evidence": "supporting_evidence",
    "contradicting_evidence": "contradicting_evidence",
    "observations": "observations",
    "decision": "decision",
}


def traverse(
    project_root: Path, record_id: str, relation: str, depth: int = 1
) -> ApiResponse:
    """Follow one recorded relationship outward from `record_id` (plan
    §4.1). `relation` is one of: any canonical cross-reference field name
    (`"depends_on"`, `"supporting_evidence"`, `"contradicting_evidence"`,
    `"observations"`, `"decision"` -- a Requirement's own cited Decision),
    its reverse (suffix `"_reverse"`, e.g.
    `"depends_on_reverse"` -- every record whose own field cites this
    one), `"cites"` (an Evidence's own `source_ref`/`test_ref` target),
    `"cited_by"` (the reverse), `"checks"` (a contract's own checks),
    `"results"` (a check's own results), or `"doc_mentions"` (the
    mechanical `doc_relations_edges` web -- `query relations`'s own
    migrated resolution, plan §4.3). `depth` > 1 repeats one more hop
    per level over whichever records were just reached, bounded and
    deterministic -- never a general graph walk or call-graph (plan §6).

    `"empty"` with no results when the starting identity does not
    resolve to anything recognised. `"result"` with an empty `results`
    list when the identity resolves but this relation yields nothing --
    a confirmed, informative zero, not an absence of the record itself.
    """
    if relation == "doc_mentions":
        return _traverse_doc_mentions(project_root, record_id)
    if relation == "checks":
        return _traverse_contract_checks(project_root, record_id)
    if relation == "results":
        return _traverse_check_results(project_root, record_id)
    if relation == "cites":
        return _traverse_cites(project_root, record_id)
    if relation == "cited_by":
        return _traverse_cited_by(project_root, record_id)

    reverse = relation.endswith("_reverse")
    base_relation = relation[: -len("_reverse")] if reverse else relation
    if base_relation not in _FORWARD_FIELD_RELATIONS:
        return _empty(f"unknown relation {relation!r}")

    records = _all_records(project_root)
    if record_id not in records:
        return _empty(f"no knowledge record {record_id!r}")

    frontier = {record_id}
    visited = {record_id}
    collected: dict[str, KnowledgeResult] = {}
    for _ in range(max(depth, 1)):
        next_frontier: set[str] = set()
        for current_id in frontier:
            neighbours = (
                _reverse_field_citers(records, current_id, base_relation)
                if reverse
                else _extract_id_strings_from(records.get(current_id), base_relation)
            )
            for nid in neighbours:
                other = records.get(nid)
                if other is None or nid in visited:
                    continue
                visited.add(nid)
                next_frontier.add(nid)
                collected[nid] = KnowledgeResult(
                    id=other.record_id, kind=other.kind, authority=_record_authority(other),
                    summary=_summarize_record(other),
                    details={"slug": _owning_slug(project_root, other), "via": relation},
                )
        frontier = next_frontier
        if not frontier:
            break

    return _result(list(collected.values()))


def _extract_id_strings_from(record: _ki.KnowledgeRecord | None, field_name: str) -> list[str]:
    if record is None:
        return []
    return _ki._extract_id_strings(record.fields.get(field_name, ""))


def _reverse_field_citers(records: dict[str, _ki.KnowledgeRecord], target_id: str, field_name: str) -> list[str]:
    return sorted(
        other.record_id
        for other in records.values()
        if target_id in _ki._extract_id_strings(other.fields.get(field_name, ""))
    )


def _traverse_contract_checks(project_root: Path, contract_qualified_id_or_bare: str) -> ApiResponse:
    m = _CONTRACT_ID_RE.match(contract_qualified_id_or_bare)
    contract_id = m.group("contract_id") if m else contract_qualified_id_or_bare
    found = _find_contract(project_root, contract_id)
    if found is None:
        return _empty(f"no oracle contract with contract_id {contract_id!r}")
    slug, contract, _ = found
    results = [
        KnowledgeResult(
            id=check_identity(contract_id, c.check_id), kind="oracle_check",
            authority=AUTHORITY_ACCEPTED_OBLIGATION, summary=f"check {c.check_id} ({c.scope})",
            details={"slug": slug, "contract_id": contract_id, "required": c.required},
        )
        for c in contract.checks
    ]
    return _result(results)


def _traverse_check_results(project_root: Path, check_qualified_id: str) -> ApiResponse:
    """Every historical result for one check, each showing **both** its
    own recorded `outcome` and its current, independently recomputed
    `effective_outcome` (`evaluate_result_precedence`, unchanged) side by
    side -- a recorded `PASS` whose `oracle_contract_content_hash` no
    longer matches the live contract (e.g. after a sibling check was
    added, `decisions/0089`'s own documented scenario) shows
    `effective_outcome: "INVALID"` right alongside its own
    `outcome: "PASS"`, never silently presented as current verification
    on the strength of the recorded field alone."""
    m = _CHECK_ID_RE.match(check_qualified_id)
    if not m:
        return _empty(f"{check_qualified_id!r} is not a check identity (expected check:<contract_id>:<check_id>)")
    contract_id, check_id = m.group("contract_id"), m.group("check_id")
    found = _find_contract(project_root, contract_id)
    if found is None:
        return _empty(f"no oracle contract with contract_id {contract_id!r}")
    slug, contract, contract_path = found
    check = contract.check_by_id(check_id)
    results = []
    for r in _load_slug_results(project_root, slug):
        if r.check_id != check_id:
            continue
        effective, reason = (
            _oracle.evaluate_result_precedence(r, contract, check, contract_path=contract_path)
            if check is not None else (None, None)
        )
        results.append(KnowledgeResult(
            id=result_identity(contract_id, check_id, r.run_id), kind="oracle_result",
            authority=AUTHORITY_SCOPED_VERIFICATION,
            summary=f"result {r.run_id}: recorded={r.outcome}, effective={effective}",
            details={"slug": slug, "run_id": r.run_id, "outcome": r.outcome,
                     "effective_outcome": effective, "invalid_reason": reason,
                     "executed_at": r.executed_at},
            consistency=ConsistencyEnvelope(
                contract_revision=r.oracle_contract_content_hash,
                evidence_currency="current" if effective == "PASS" else "unconfirmed",
                status="stale" if effective == "INVALID" else "current",
                reasons=[reason] if reason else [],
            ),
        ))
    return _result(results)


def _traverse_cites(project_root: Path, evidence_id: str) -> ApiResponse:
    records = _all_records(project_root)
    record = records.get(evidence_id)
    if record is None or record.kind != "evidence":
        return _empty(f"{evidence_id!r} is not a known evidence record")
    results: list[KnowledgeResult] = []
    source_ref = record.fields.get("source_ref", "")
    if source_ref and source_ref != "null":
        results.append(KnowledgeResult(
            id=f"source_ref:{_KI_unquote(source_ref)}", kind="source_ref",
            authority=AUTHORITY_PRIMARY_EVIDENCE, summary=_KI_unquote(source_ref),
            details={"raw": _KI_unquote(source_ref)},
        ))
    test_ref = record.fields.get("test_ref", "")
    if test_ref and test_ref != "null":
        slug = _owning_slug(project_root, record)
        result_path = project_root / _KI_unquote(test_ref)
        details: dict = {"raw": _KI_unquote(test_ref), "slug": slug}
        authority = AUTHORITY_SCOPED_VERIFICATION
        if result_path.is_file():
            try:
                parsed = _oracle.parse_oracle_result(result_path)
                details["check_id"] = parsed.check_id
                details["outcome"] = parsed.outcome
            except _oracle.OracleSchemaError:
                details["parse_error"] = "malformed OracleResult"
        else:
            details["missing"] = True
        results.append(KnowledgeResult(
            id=f"test_ref:{_KI_unquote(test_ref)}", kind="test_ref", authority=authority,
            summary=_KI_unquote(test_ref), details=details,
        ))
    observation_ids = _ki._extract_id_strings(record.fields.get("observations", ""))
    for oid in observation_ids:
        other = records.get(oid)
        if other is not None:
            results.append(KnowledgeResult(
                id=other.record_id, kind=other.kind, authority=_record_authority(other),
                summary=_summarize_record(other), details={"slug": _owning_slug(project_root, other)},
            ))
    if not results:
        return _result([])
    return _result(results)


def _traverse_cited_by(project_root: Path, target_id: str) -> ApiResponse:
    records = _all_records(project_root)
    if _is_knowledge_record_id(target_id) and target_id not in records:
        return _empty(f"no knowledge record {target_id!r}")
    results: list[KnowledgeResult] = []
    for other in records.values():
        cited = set()
        for field_name in ("depends_on", "supporting_evidence", "contradicting_evidence", "observations", "decision"):
            cited.update(_ki._extract_id_strings(other.fields.get(field_name, "")))
        if target_id in cited:
            results.append(KnowledgeResult(
                id=other.record_id, kind=other.kind, authority=_record_authority(other),
                summary=_summarize_record(other), details={"slug": _owning_slug(project_root, other)},
            ))
    return _result(results)


def _traverse_doc_mentions(project_root: Path, name: str) -> ApiResponse:
    """`query relations <name>`'s exact pre-Phase-84 resolution (Phase 21's
    `doc_relations_edges` web plus Phase 22's `doc_relation_enrichment`
    cache, Phase 31's `relation_label`, Phase 32's `heading`), moved here
    unchanged so both `knowledge_api.traverse` and the migrated CLI
    command share one implementation (plan §4.3)."""
    conn = _open_ro(project_root)
    if conn is None:
        return _empty(f"no {_DB_FILENAME} under {project_root}")
    try:
        relations = resolve_doc_mentions(conn, name)
    finally:
        conn.close()
    if relations is None:
        return _empty(f"{name!r} does not match a spec doc, vendor, or doc artifact name")
    results = [
        KnowledgeResult(
            id=f"docrel:{name}:{i}", kind="doc_relation", authority=AUTHORITY_DERIVED_INDEX,
            summary=r.get("relation_kind", ""), details=r,
        )
        for i, r in enumerate(relations)
    ]
    return _result(results)


def resolve_doc_mentions(conn: sqlite3.Connection, name: str) -> list[dict] | None:
    """Public so `cli.py::query_relations` can reuse the identical
    resolution without going through the `ApiResponse` envelope (it
    needs the raw per-relation dicts to render its own, pre-existing
    table/JSON shape byte-identically). `None` if `name` matches nothing;
    `[]` if it matches a real spec doc/vendor/doc-artifact with zero
    recorded relations -- the same distinction `_resolve_relations` (this
    function's own, now-removed, prior home in `cli.py`) already made.
    """
    from codecompass import graph as _graph

    if conn.execute("SELECT 1 FROM doc_artifacts WHERE path = ?", (name,)).fetchone():
        relations = _graph.doc_relations(conn, name)
        for r in relations:
            r["ai_summary"], r["relation_label"] = _relation_enrichment_row(
                conn, name, r["target_vendor"], r["target_doc_artifact_path"]
            )
        return relations

    vendor_row = conn.execute("SELECT id FROM vendors WHERE name = ?", (name,)).fetchone()
    if vendor_row is not None:
        relations = _incoming_doc_relations(conn, "target_vendor_id", vendor_row[0])
        for r in relations:
            r["ai_summary"], r["relation_label"] = _relation_enrichment_row(
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
                r["ai_summary"], r["relation_label"] = _relation_enrichment_row(
                    conn, r["source_doc_artifact_path"], None, artifact_path
                )
            results.extend(relations)
        return results

    return None


def _incoming_doc_relations(conn: sqlite3.Connection, column: str, value: int) -> list[dict]:
    return [
        {"relation_kind": relation_kind, "source_doc_artifact_path": path, "heading": heading}
        for path, relation_kind, heading in conn.execute(
            f"""
            SELECT da.path, dre.relation_kind, dch.heading_path
            FROM doc_relations_edges dre
            JOIN doc_artifacts da ON dre.source_doc_artifact_id = da.id
            LEFT JOIN doc_chunks dch ON dre.chunk_id = dch.id
            WHERE dre.{column} = ?
            ORDER BY da.path
            """,
            (value,),
        )
    ]


def _relation_enrichment_row(
    conn: sqlite3.Connection, source_doc_path: str, target_vendor_name: str | None, target_doc_path: str | None,
) -> tuple[str | None, str | None]:
    row = conn.execute(
        """
        SELECT ai_summary, relation_label FROM doc_relation_enrichment
        WHERE source_doc_path = ? AND target_vendor_name IS ? AND target_doc_path IS ?
        """,
        (source_doc_path, target_vendor_name, target_doc_path),
    ).fetchone()
    return (row[0], row[1]) if row is not None else (None, None)


# ---------------------------------------------------------------------------
# trace_evidence()
# ---------------------------------------------------------------------------


def trace_evidence(project_root: Path, record_id: str, *, repo_root: Path | None = None) -> ApiResponse:
    """Supporting and contradicting evidence for one Claim/Requirement
    (plan §4.1/§3.0 point 6). `"gap"` when the record is itself an
    obligation-bearing kind (`claim`/`requirement`) with zero evidence
    anywhere citing it -- never conflated with `"empty"` (the record not
    existing at all)."""
    records = _all_records(project_root)
    record = records.get(record_id)
    if record is None:
        return _empty(f"no knowledge record {record_id!r}")

    supporting_ids = _ki._extract_id_strings(record.fields.get("supporting_evidence", ""))
    contradicting_ids = _ki._extract_id_strings(record.fields.get("contradicting_evidence", ""))

    results: list[KnowledgeResult] = []
    for ev_id in supporting_ids:
        ev = records.get(ev_id)
        if ev is None:
            continue
        results.append(KnowledgeResult(
            id=ev.record_id, kind="evidence", authority=_record_authority(ev),
            summary=_summarize_record(ev),
            details={"role": "supporting", "evidence_kind": ev.fields.get("evidence_kind")},
        ))
    for ev_id in contradicting_ids:
        ev = records.get(ev_id)
        if ev is None:
            continue
        results.append(KnowledgeResult(
            id=ev.record_id, kind="evidence", authority=_record_authority(ev),
            summary=_summarize_record(ev),
            details={"role": "contradicting", "evidence_kind": ev.fields.get("evidence_kind")},
        ))

    if record.kind in ("claim", "requirement") and not supporting_ids:
        gap = Gap(
            kind="missing_evidence", subject_id=record_id, scope=None,
            reason=f"{record_id} ({record.kind}) has no supporting_evidence citation at all",
        )
        return ApiResponse(status="gap", results=results, gaps=[gap])

    return _result(results)


# ---------------------------------------------------------------------------
# epistemic_status()
# ---------------------------------------------------------------------------


def epistemic_status(project_root: Path, record_id: str, *, repo_root: Path | None = None) -> ApiResponse:
    """INTENDED/OBSERVED/VERIFIED/CONTESTED for one record (plan §4.1) --
    a thin wrapper around `knowledge_intermediate.derive_epistemic_profile`
    (unchanged, per plan §0/§3.0 point 5). For a Requirement (which has no
    `supporting_evidence` field of its own), the profile is computed per
    dependent Claim (its own `depends_on`) and the verified/gap/
    unconfirmed scope lists are unioned -- a Requirement's own evidence
    is always indirect, through the Claims it depends on."""
    records = _all_records(project_root)
    record = records.get(record_id)
    if record is None:
        return _empty(f"no knowledge record {record_id!r}")

    slug = _owning_slug(project_root, record)
    found = _find_contract_for_slug(project_root, slug)
    oracle_contract = contract_path = None
    results_by_ref: dict[str, _oracle.OracleResult] = {}
    if found is not None:
        _, oracle_contract, contract_path = found
        results_by_ref = _results_by_test_ref(project_root, slug)

    subjects = [record]
    if record.kind == "requirement":
        dep_ids = _ki._extract_id_strings(record.fields.get("depends_on", ""))
        subjects = [records[d] for d in dep_ids if d in records and records[d].kind == "claim"] or [record]

    intended = observed = contested = False
    verified: set[str] = set()
    gap: set[str] = set()
    unconfirmed: set[str] = set()
    for subject in subjects:
        profile = _ki.derive_epistemic_profile(
            subject, records, oracle_contract=oracle_contract,
            oracle_results_by_test_ref=results_by_ref, contract_path=contract_path, repo_root=repo_root,
        )
        intended = intended or profile.intended
        observed = observed or profile.observed
        contested = contested or profile.contested
        verified.update(profile.verified_scopes)
        gap.update(profile.known_gap_scopes)
        unconfirmed.update(profile.unconfirmed_scopes)
    gap -= verified
    unconfirmed -= verified

    result = KnowledgeResult(
        id=record_id, kind=record.kind, authority=_record_authority(record),
        summary=f"epistemic status of {record_id}",
        details={
            "intended": intended, "observed": observed, "contested": contested,
            "verified_scopes": sorted(verified), "known_gap_scopes": sorted(gap),
            "unconfirmed_scopes": sorted(unconfirmed),
        },
    )
    return _result([result])


# ---------------------------------------------------------------------------
# find_gaps()
# ---------------------------------------------------------------------------


def find_gaps(project_root: Path, slug: str | None = None, *, repo_root: Path | None = None) -> ApiResponse:
    """Missing, stale, or conflicting knowledge, across record kinds, in
    one call (plan §3.0 point 6 -- the one genuinely new cross-cutting
    capability no existing command provides). Scans one slug or every
    slug. Detection rules, each independently real (not merely
    hypothetical), reusing only existing mechanisms:

    - `unverified_required_scope` -- a required oracle check with no
      currently-matched `PASS` for any Claim that cites it
      (`derive_epistemic_profile`'s own `known_gap_scopes`, unchanged).
    - `contradiction` -- a record `status: contradicted`, or with a
      non-empty `contradicting_evidence`.
    - `stale_test_citation` -- a `test`-kind Evidence whose `test_ref`
      resolves to a result that is `INVALID` against the *live* contract
      (`evaluate_result_precedence`, unchanged) while a different,
      currently-valid `PASS` for the very same `check_id` exists in the
      same slug's own `results/` directory -- i.e. a newer confirming run
      exists but no Evidence record was ever updated to cite it.
    - `missing_contract` -- a slug with Claims/Requirements but no
      `oracle-contract.yaml` under `planning/contracts/<slug>/` at all.
    """
    slugs = [slug] if slug else _ki._list_slugs(project_root)
    records = _all_records(project_root)
    gaps: list[Gap] = []

    for s in slugs:
        slug_records = _ki.load_slug_records(_ki.slug_dir(project_root, s))
        if not slug_records:
            continue

        for record in slug_records.values():
            if record.fields.get("status") == "contradicted":
                gaps.append(Gap(kind="contradiction", subject_id=record.record_id, scope=None,
                                 reason=f"{record.record_id} has status=contradicted"))
            contradicting = _ki._extract_id_strings(record.fields.get("contradicting_evidence", ""))
            if contradicting:
                gaps.append(Gap(kind="contradiction", subject_id=record.record_id, scope=None,
                                 reason=f"{record.record_id} has contradicting_evidence: {contradicting}"))

        has_obligations = any(r.kind in ("claim", "requirement") for r in slug_records.values())
        found = _find_contract_for_slug(project_root, s)
        if has_obligations and found is None:
            gaps.append(Gap(kind="missing_contract", subject_id=None, scope=None,
                             reason=f"slug {s!r} has claims/requirements but no oracle-contract.yaml"))
            continue
        if found is None:
            continue
        _, contract, contract_path = found

        results_by_ref = _results_by_test_ref(project_root, s)
        for claim in slug_records.values():
            if claim.kind != "claim":
                continue
            profile = _ki.derive_epistemic_profile(
                claim, records, oracle_contract=contract, oracle_results_by_test_ref=results_by_ref,
                contract_path=contract_path, repo_root=repo_root,
            )
            for scope in profile.known_gap_scopes:
                gaps.append(Gap(kind="unverified_required_scope", subject_id=claim.record_id, scope=scope,
                                 reason=f"{claim.record_id} cites no currently-passing result for required scope {scope!r}"))

        all_results = _load_slug_results(project_root, s)
        current_pass_by_check: dict[str, bool] = {}
        for check in contract.checks:
            check_results = [r for r in all_results if r.check_id == check.check_id]
            aggregates = _oracle.aggregate_contract(contract, check_results, contract_path=contract_path)
            agg = next((a for a in aggregates if a.check_id == check.check_id), None)
            current_pass_by_check[check.check_id] = bool(agg and agg.state == "PASS")

        for record in slug_records.values():
            if record.kind != "evidence" or record.fields.get("evidence_kind") != "test":
                continue
            raw_ref = record.fields.get("test_ref", "")
            if not raw_ref or raw_ref == "null":
                continue
            result_path = project_root / _KI_unquote(raw_ref)
            if not result_path.is_file():
                continue
            try:
                cited = _oracle.parse_oracle_result(result_path)
            except _oracle.OracleSchemaError:
                continue
            check = contract.check_by_id(cited.check_id)
            if check is None:
                continue
            outcome, reason = _oracle.evaluate_result_precedence(cited, contract, check, contract_path=contract_path)
            if outcome == "INVALID" and current_pass_by_check.get(cited.check_id):
                gaps.append(Gap(
                    kind="stale_test_citation", subject_id=record.record_id, scope=check.scope,
                    reason=(
                        f"{record.record_id}'s test_ref ({raw_ref}) is INVALID against the live contract "
                        f"({reason}), but a different, currently-passing result for check_id "
                        f"{cited.check_id!r} exists in {s!r}'s own results/ directory -- no Evidence "
                        "record cites it"
                    ),
                ))

    return _gap_response(gaps, message=None if gaps else "no gaps found")


# ---------------------------------------------------------------------------
# get_context_packet()
# ---------------------------------------------------------------------------


@dataclass
class ContextBounds:
    max_items: int = 20
    max_chars: int = 6000
    truncated: bool = False


def get_context_packet(
    project_root: Path, topic: str, *, max_items: int = 20, max_chars: int = 6000,
    repo_root: Path | None = None,
) -> ApiResponse:
    """A bounded, coherent, deterministic development-context packet for
    `topic` (a knowledge-record id, or free text) -- plan §4.1/§4.E.
    Priority order (fixed, never re-ranked by any heuristic or AI call):
    (1) the subject record itself; (2) its direct `depends_on`/
    `depends_on_reverse`/`supporting_evidence`/`contradicting_evidence`
    neighbours (one hop each); (3) explicit gaps for this one subject
    (`trace_evidence`'s own gap detection). Oracle checks/results are
    reachable for the subject separately, via `get`/`traverse(...,
    "checks"/"results")` -- this packet does not itself expand into
    them, keeping the traversal bounded to knowledge-record relations
    only. Deduplicated by id. Truncated, deterministically (by this
    fixed priority order, then by id), at `max_items`/`max_chars` --
    `details.bounds.truncated` says so explicitly rather than silently
    dropping items.
    """
    records = _all_records(project_root)
    subject_id = topic if topic in records else None
    if subject_id is None:
        search_response = search(project_root, topic)
        if search_response.status != "result":
            return _empty(f"no knowledge found for topic {topic!r}")
        subject_id = search_response.results[0].id
        if subject_id not in records:
            # A non-knowledge-record search hit (an oracle contract/check) --
            # still a valid topic anchor, just not further traversable here.
            item = search_response.results[0]
            packet_items = [item]
            return _result([KnowledgeResult(
                id=f"context:{topic}", kind="context_packet", authority=AUTHORITY_DERIVED_INDEX,
                summary=f"context packet for {topic!r}",
                details={"topic": topic, "items": [asdict(i) for i in packet_items],
                         "gaps": [], "bounds": asdict(ContextBounds(max_items, max_chars, False))},
            )])

    ordered_ids: list[str] = [subject_id]
    seen = {subject_id}
    for relation in ("depends_on", "depends_on_reverse", "supporting_evidence", "contradicting_evidence"):
        response = traverse(project_root, subject_id, relation)
        for r in response.results:
            if r.id not in seen:
                seen.add(r.id)
                ordered_ids.append(r.id)

    gap_response = trace_evidence(project_root, subject_id, repo_root=repo_root)

    items: list[KnowledgeResult] = []
    char_budget = max_chars
    truncated = False
    for rid in ordered_ids:
        if len(items) >= max_items:
            truncated = True
            break
        record = records.get(rid)
        if record is None:
            continue
        summary = _summarize_record(record)
        if char_budget - len(summary) < 0:
            truncated = True
            break
        char_budget -= len(summary)
        items.append(KnowledgeResult(
            id=record.record_id, kind=record.kind, authority=_record_authority(record), summary=summary,
            details={"slug": _owning_slug(project_root, record)},
        ))

    packet = KnowledgeResult(
        id=f"context:{subject_id}", kind="context_packet", authority=AUTHORITY_DERIVED_INDEX,
        summary=f"context packet for {subject_id}",
        details={
            "topic": topic, "subject_id": subject_id,
            "items": [asdict(i) for i in items],
            "gaps": [asdict(g) for g in gap_response.gaps],
            "bounds": asdict(ContextBounds(max_items, max_chars, truncated)),
        },
    )
    return _result([packet])


# ---------------------------------------------------------------------------
# export_snapshot()
# ---------------------------------------------------------------------------


def _git_head_revision(project_root: Path) -> dict:
    try:
        sha = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=project_root, capture_output=True, text=True, timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return {"scheme": "unknown", "as_of": datetime.now(UTC).date().isoformat()}
    if sha.returncode != 0:
        return {"scheme": "unknown", "as_of": datetime.now(UTC).date().isoformat()}
    return {"scheme": "git-commit", "sha": sha.stdout.strip()}


def export_snapshot(
    project_root: Path, slug: str, out_path: Path, *, project_id: str = "codecompass",
) -> ApiResponse:
    """A portable, versioned export of one slug's canonical knowledge --
    `decisions/0079` §5's own project-identity envelope, reused directly
    (plan §3.0 point 9/§3.A). Writes exactly `out_path` -- never any file
    under `planning/knowledge/`/`planning/contracts/` (refused outright,
    never silently redirected, if `out_path` resolves inside either).
    Never mutates canonical project knowledge."""
    canonical_roots = [
        (project_root / "planning" / "knowledge").resolve(),
        (project_root / "planning" / "contracts").resolve(),
    ]
    resolved_out = out_path.resolve()
    for canonical in canonical_roots:
        if resolved_out == canonical or canonical in resolved_out.parents:
            raise ValueError(
                f"export_snapshot refuses to write inside a canonical knowledge tree: {canonical}"
            )

    slug_dir = _ki.slug_dir(project_root, slug)
    records = _ki.load_slug_records(slug_dir)
    if not records and not _slug_contract_path(project_root, slug).is_file():
        return _empty(f"slug {slug!r} has no records and no oracle contract -- nothing to export")

    found = _find_contract_for_slug(project_root, slug)
    contract_payload = None
    results_payload: list[dict] = []
    if found is not None:
        _, contract, contract_path = found
        contract_payload = {
            "contract_id": contract.contract_id, "tested_paths": contract.tested_paths,
            "checks": [asdict(c) for c in contract.checks],
            "oracle_contract_content_hash": _oracle.sha256_file(contract_path),
        }
        results_payload = [asdict(r) for r in _load_slug_results(project_root, slug)]

    envelope = {
        "project_id": project_id,
        "source_locator": {"scheme": "local-only", "note": str(project_root)},
        "revision": _git_head_revision(project_root),
        "knowledge_schema_version": 1,
        "exported_at": datetime.now(UTC).isoformat(),
        "slug": slug,
        "records": {rid: {"kind": r.kind, "fields": r.fields} for rid, r in records.items()},
        "contract": contract_payload,
        "results": results_payload,
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(envelope, indent=2, sort_keys=True), encoding="utf-8")

    result = KnowledgeResult(
        id=f"export:{slug}", kind="portable_snapshot", authority=AUTHORITY_DERIVED_INDEX,
        summary=f"exported {len(records)} record(s) for slug {slug!r} to {out_path}",
        details={"out_path": str(out_path), "record_count": len(records),
                 "has_contract": contract_payload is not None, "result_count": len(results_payload)},
    )
    return _result([result])
