"""Phase 85 — maintainer-only, on-demand knowledge-quality validator for
CodeCompass's own first-party `planning/knowledge/` corpus. Mirrors
`scripts/check_knowledge_base.py`/`scripts/check_contracts.py`'s own
exact `Finding(rule, message, strict)` convention, report-only by
default, `--strict` exits 1 on a *blocking* finding only. Mechanical
only — no AI call, no edits, no mutation of canonical knowledge.

See `planning/phase-85-self-curation-knowledge-quality-validation.md`
§4.C for the full design this implements. **Composes** existing
`codecompass.knowledge_api`/`codecompass.knowledge_intermediate`
functions; adds no logic already present there, and makes no change to
either module.

    python scripts/check_self_knowledge_quality.py [--strict]

Not part of the `codecompass` package: like its siblings, this checks
CodeCompass's own planning artefacts, not a consuming project's, and is
not a `codecompass` subcommand.

Checks:

1. `knowledge_api.find_gaps(project_root, slug=None)` — its own existing
   six rules, unchanged, corpus-wide. Every resulting `Gap` is reported
   as blocking **except**: `missing_contract`, which is always
   informational (see below); and `contradiction`, which is
   informational when the subject's own `status` is `superseded` *and*
   it is genuinely, credibly named by another same-kind record's
   `supersedes` field (never trusted from `status: superseded` alone —
   see `_resolved_by_credible_supersession`). `missing_contract`: no
   existing canonical record or accepted decision currently establishes
   that an oracle contract is a mandatory obligation for any subject but
   `balance-from-spec` — confirmed by direct reading of `decisions/0081`
   §3, which explicitly defers this ("a future phase may choose to
   require contracts project-wide once real use justifies that cost...
   not pre-committed here") and ties its own, narrower compatibility
   exemption to the identical mechanical condition this script reuses
   ("no contract directory exists for this slug," preferred there over
   an allow-list). This is not a per-slug allowlist: the real corpus has
   six knowledge slugs and one oracle contract, so five of six would
   otherwise fail `--strict` for a condition nothing has ever decided is
   a defect. `contradiction`'s own superseded-and-resolved carve-out
   (corrective pass): `CL-ADPT-008` (`status: superseded`, retaining
   `contradicting_evidence: [EV-ADPT-008]` as historical provenance) is
   genuinely resolved by `CL-ADPT-010` (`status: supported`,
   `supersedes: CL-ADPT-008`) — reusing `knowledge_intermediate.
   derive_provenance_label`'s own existing, unchanged `status ==
   "superseded" -> "HISTORICAL"` classification, not a new invented
   semantic. A Claim/Decision merely marked `status: superseded` with no
   real successor naming it back, or whose only named successor is
   itself not credible (e.g. itself `contradicted`), is **not** exempted
   — it stays blocking.
2. `knowledge_intermediate.knowledge_status(project_root)` — needs-review
   records and unresolved concurrent-change conflicts, reported
   informational (this function's own existing design; `codecompass
   knowledge status --strict` is the separate, existing command that
   blocks on a concurrent conflict specifically).
3. A corpus-wide `missing_evidence` scan: for every `claim`/`requirement`
   record, call `knowledge_api.trace_evidence()` and report any `Gap`
   whose own `kind == "missing_evidence"` — not every `status="gap"`
   response, which would double-report `dangling_evidence_reference`/
   `dangling_dependency_reference` already covered by check 1. Blocking
   only when the subject's own `status` is already decided
   (`supported`/`verified`/`contradicted` for a Claim;
   `approved`/`implemented`/`verified` for a Requirement) — never for
   `status: proposed`, normal, undecided workflow state.
4. A missing/malformed/unreadable `test_ref`-file check: for every
   `test`-kind Evidence record, resolve its own `test_ref` path under
   `project_root` and report (always blocking) if the path does not
   exist, exists but fails `oracle.parse_oracle_result()`'s own schema
   validation, or exists but could not be read at all (any `OSError` —
   e.g. a permission error — raised while reading it; narrowly scoped to
   `OSError`, never a bare `except Exception`, so a genuine programming
   error still surfaces as a crash rather than a misleading finding).
   Distinct from an unresolved Evidence *id* (check 1's own
   `dangling_evidence_reference`) — this is the Evidence record
   resolving fine while the *file it cites* does not.
5. Deterministic duplicate/overlap detection, within one slug: byte-
   identical (whitespace-normalised) `statement` fields between two
   Claims (always informational, regardless of evidence); non-empty,
   identical `supporting_evidence` sets between two Claims (always
   informational, a possible-overlap signal, never conclusive). An
   empty `supporting_evidence` set never triggers this check by itself.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KNOWLEDGE_DIR = ROOT / "planning" / "knowledge"
DEFAULT_LEDGERKIT_ROOT = Path.home() / "projects" / "ledgerkit"

_ID_PATTERN = re.compile(r"\b(OBS|EV|CL|DE|DEC|REQ)-[A-Z0-9]+-\d+\b")

# decisions/0080's own INTENDED-Requirement statuses, reused unchanged —
# a Requirement is an accepted obligation only once it reaches one of
# these; a Claim's analogous "decided" set is this project's existing
# closed status enum minus its own undecided `proposed` state.
_DECIDED_REQUIREMENT_STATUSES = {"approved", "implemented", "verified"}
_DECIDED_CLAIM_STATUSES = {"supported", "verified", "contradicted"}


@dataclass
class Finding:
    rule: str
    message: str
    strict: bool = True  # False = informational, never fails --strict


def _extract_id_strings(value: str) -> list[str]:
    return [m.group(0) for m in _ID_PATTERN.finditer(value)]


def _unquote(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


def _normalize_statement(value: str) -> str:
    return " ".join(value.split())


def _load_codecompass():
    """Mirrors `check_knowledge_base.py::_load_knowledge_intermediate`'s
    own import-or-None pattern — a bare checkout shouldn't crash this
    whole script. Returns `(knowledge_api, knowledge_intermediate,
    oracle)`, each `None` if unimportable."""
    src_path = ROOT / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    try:
        from codecompass import knowledge_api, knowledge_intermediate, oracle

        return knowledge_api, knowledge_intermediate, oracle
    except Exception:
        return None, None, None


def _iter_slug_dirs(root: Path) -> list[Path]:
    knowledge_dir = root / "planning" / "knowledge"
    if not knowledge_dir.is_dir():
        return []
    return sorted(p for p in knowledge_dir.iterdir() if p.is_dir())


def _load_all_records(project_root: Path, ki) -> dict[str, object]:
    """Every canonical record across every slug, keyed by `id` — local
    equivalent of `knowledge_api._all_records` (private to that module),
    needed here so this script's own severity logic can inspect a
    subject's and a candidate successor's fields directly rather than
    re-deriving them from `find_gaps()`'s own prose `reason` string."""
    all_records: dict[str, object] = {}
    for slug_dir in _iter_slug_dirs(project_root):
        all_records.update(ki.load_slug_records(slug_dir))
    return all_records


# A `superseded` Claim/Decision's own successor must itself be in one of
# these states to count as a *credible* resolution — a successor that is
# itself merely `proposed`, or (for a Claim) itself `contradicted`, does
# not genuinely resolve anything, so severity is not downgraded on its
# account. Decision has no analogous "contradicted"-like state; its own
# decided set is just `approved` (`decisions/0080`'s own enum).
_CREDIBLE_SUCCESSOR_STATUSES = {
    "claim": _DECIDED_CLAIM_STATUSES - {"contradicted"},
    "decision": {"approved"},
}


def _resolved_by_credible_supersession(subject, all_records: dict[str, object]) -> bool:
    """True only when `subject` (`status: superseded`) is genuinely named
    in some other, same-kind record's own `supersedes` field, and that
    successor is itself credible (see `_CREDIBLE_SUCCESSOR_STATUSES`).
    Mirrors `knowledge_intermediate.derive_provenance_label`'s own
    existing, unchanged `status == "superseded" -> "HISTORICAL"`
    classification — this does not invent a new semantic, it reuses one
    this project already treats as authoritative to correct this
    script's own severity, rather than `find_gaps()`'s public behaviour.
    Never trusts `status: superseded` alone: an orphaned record (nothing
    names it back) or one whose only named successor is itself broken
    stays blocking (fail-closed) — confirmed real against `CL-ADPT-008`
    (`status: superseded`, named by `CL-ADPT-010`'s own `supersedes:
    CL-ADPT-008`, `CL-ADPT-010` itself `status: supported`)."""
    if subject.fields.get("status") != "superseded":
        return False
    credible_statuses = _CREDIBLE_SUCCESSOR_STATUSES.get(subject.kind)
    if credible_statuses is None:
        return False
    for other in all_records.values():
        if other.kind != subject.kind:
            continue
        if subject.record_id not in _extract_id_strings(other.fields.get("supersedes", "")):
            continue
        if other.fields.get("status") in credible_statuses:
            return True
    return False


def check_find_gaps_composed(
    project_root: Path, ka, repo_root: Path | None, ki
) -> list[Finding]:
    """Check 1 (module docstring). `find_gaps()` itself is never edited
    or re-implemented — this only re-classifies its own `Gap.kind` into
    a `Finding.strict` value, since `find_gaps()`'s own typed response
    carries no severity concept of its own. `repo_root` is threaded
    through exactly like `check_contracts.py`/`check_knowledge_base.py`'s
    own `--ledgerkit-root` — without it, `unverified_required_scope`/
    `stale_test_citation` can never report a scope as currently
    reconfirmed (decisions/0092), which would otherwise make every
    oracle-backed Claim look permanently unverified regardless of real
    implementation health.

    Corrective pass: a `contradiction` Gap whose own subject has
    `status: superseded` and is genuinely, credibly superseded (see
    `_resolved_by_credible_supersession`) is downgraded to informational
    — the contradiction is real, historical provenance, already resolved
    by a later Claim/Decision, not an active defect. A `contradiction`
    Gap for a record with `status: contradicted` is never downgraded by
    this rule (status values are mutually exclusive, so the two cases
    cannot collide on one record)."""
    findings: list[Finding] = []
    all_records = _load_all_records(project_root, ki)
    response = ka.find_gaps(project_root, slug=None, repo_root=repo_root)
    for gap in sorted(response.gaps, key=lambda g: (g.kind, g.subject_id or "", g.scope or "")):
        rule = f"self-knowledge-quality-{gap.kind.replace('_', '-')}"
        if gap.kind == "missing_contract":
            strict = False
        elif gap.kind == "contradiction":
            subject = all_records.get(gap.subject_id) if gap.subject_id else None
            strict = not (subject is not None and _resolved_by_credible_supersession(subject, all_records))
        else:
            strict = True
        findings.append(Finding(rule, gap.reason, strict))
    return findings


def check_knowledge_status_composed(project_root: Path, ki) -> list[Finding]:
    """Check 2 (module docstring) — always informational in this
    composing script, per this project's own design (`codecompass
    knowledge status --strict` already exists as the separate, blocking
    surface for a concurrent-change conflict specifically)."""
    findings: list[Finding] = []
    report = ki.knowledge_status(project_root)
    for item in sorted(report.needs_review):
        findings.append(Finding("self-knowledge-quality-needs-review", item, False))
    for item in sorted(report.concurrent_conflicts):
        findings.append(Finding("self-knowledge-quality-concurrent-conflict", item, False))
    return findings


def check_missing_evidence_composed(project_root: Path, ka, ki, repo_root: Path | None) -> list[Finding]:
    """Check 3 (module docstring)."""
    findings: list[Finding] = []
    all_records = _load_all_records(project_root, ki)

    seen_gap_keys: set[tuple[str, str | None]] = set()
    for record_id in sorted(all_records):
        record = all_records[record_id]
        if record.kind not in ("claim", "requirement"):
            continue
        response = ka.trace_evidence(project_root, record_id, repo_root=repo_root)
        for gap in response.gaps:
            if gap.kind != "missing_evidence":
                continue
            key = (gap.subject_id or record_id, gap.scope)
            if key in seen_gap_keys:
                continue
            seen_gap_keys.add(key)
            subject = all_records.get(gap.subject_id or record_id)
            decided = False
            if subject is not None:
                if subject.kind == "claim":
                    decided = subject.fields.get("status") in _DECIDED_CLAIM_STATUSES
                elif subject.kind == "requirement":
                    decided = subject.fields.get("status") in _DECIDED_REQUIREMENT_STATUSES
            findings.append(
                Finding("self-knowledge-quality-missing-evidence", gap.reason, decided)
            )
    return sorted(findings, key=lambda f: f.message)


def check_test_ref_files(project_root: Path, ki, oracle) -> list[Finding]:
    """Check 4 (module docstring). **Scoped to contract-bearing slugs
    only** (discovered live, running this script against the real
    corpus for the first time): a `test`-kind Evidence's `test_ref` only
    means "a path under `planning/contracts/<slug>/results/*.yaml`" for
    a slug that actually has an oracle contract at all — for a slug with
    none (e.g. `codecompass-domain`, `doc-origin-pinned-reference`),
    `test_ref` legitimately uses this project's older, pre-Phase-82
    convention (a plain pytest file/file:line citation, e.g.
    `"tests/test_graph.py:1426-1436"`), which was never intended to
    resolve as a file path at all and is not a defect — confirmed real
    by direct inspection (`EV-ADPT-006`/`EV-CTXT-011`/`EV-SKEP-005`/
    `EV-DOCORIGIN-008`, none in a contract-bearing slug). `find_gaps()`'s
    own `stale_test_citation` rule already silently treats any
    non-resolving `test_ref` as not-applicable for exactly this reason;
    this check narrows to the one population where "doesn't resolve"
    can only mean "broken," never "a different, equally legitimate
    citation style.\""""
    findings: list[Finding] = []
    for slug_dir in _iter_slug_dirs(project_root):
        contract_path = project_root / "planning" / "contracts" / slug_dir.name / "oracle-contract.yaml"
        if not contract_path.is_file():
            continue
        records = ki.load_slug_records(slug_dir)
        for record_id in sorted(records):
            record = records[record_id]
            if record.kind != "evidence" or record.fields.get("evidence_kind") != "test":
                continue
            raw_ref = record.fields.get("test_ref", "")
            if not raw_ref or raw_ref == "null":
                continue
            rel_ref = _unquote(raw_ref)
            result_path = project_root / rel_ref
            if not result_path.is_file():
                findings.append(
                    Finding(
                        "self-knowledge-quality-missing-test-ref-file",
                        f"{record_id} ({slug_dir.name}): test_ref {rel_ref!r} does not "
                        "resolve to any file",
                    )
                )
                continue
            try:
                oracle.parse_oracle_result(result_path)
            except oracle.OracleSchemaError as exc:
                findings.append(
                    Finding(
                        "self-knowledge-quality-malformed-test-ref-file",
                        f"{record_id} ({slug_dir.name}): test_ref {rel_ref!r} exists but "
                        f"does not parse as a valid oracle result: {exc}",
                    )
                )
            except OSError as exc:
                # Corrective pass: a filesystem failure reading an
                # otherwise-existing file (permission denied, a path that
                # turned into a directory/special file between the
                # `is_file()` check and the read, etc.) is a distinct
                # failure mode from "missing" and from "malformed YAML" —
                # `oracle.parse_oracle_result`'s own `_safe_load_yaml`
                # catches `yaml.YAMLError` but not `OSError`, so this was
                # previously uncaught and crashed the whole validator run,
                # silently hiding every other real finding. Narrowly
                # scoped to `OSError` (never a bare `except Exception`) so
                # a genuine programming error elsewhere still surfaces as
                # a crash rather than a misleading "finding".
                findings.append(
                    Finding(
                        "self-knowledge-quality-unreadable-test-ref-file",
                        f"{record_id} ({slug_dir.name}): test_ref {rel_ref!r} exists but "
                        f"could not be read ({type(exc).__name__}: {exc})",
                    )
                )
    return findings


def check_duplicate_overlap(project_root: Path, ki) -> list[Finding]:
    """Check 5 (module docstring)."""
    findings: list[Finding] = []
    for slug_dir in _iter_slug_dirs(project_root):
        records = ki.load_slug_records(slug_dir)
        claims = sorted(
            (r for r in records.values() if r.kind == "claim"), key=lambda r: r.record_id
        )
        for i, a in enumerate(claims):
            for b in claims[i + 1 :]:
                stmt_a = _normalize_statement(a.fields.get("statement", ""))
                stmt_b = _normalize_statement(b.fields.get("statement", ""))
                if stmt_a and stmt_b and stmt_a == stmt_b:
                    findings.append(
                        Finding(
                            "self-knowledge-quality-duplicate-statement",
                            f"{a.record_id} and {b.record_id} ({slug_dir.name}) have "
                            "byte-identical normalised statements -- candidate duplicate, "
                            "not automatically merged",
                            False,
                        )
                    )
                ev_a = set(_extract_id_strings(a.fields.get("supporting_evidence", "")))
                ev_b = set(_extract_id_strings(b.fields.get("supporting_evidence", "")))
                if ev_a and ev_a == ev_b:
                    findings.append(
                        Finding(
                            "self-knowledge-quality-possible-evidence-overlap",
                            f"{a.record_id} and {b.record_id} ({slug_dir.name}) cite an "
                            f"identical, non-empty supporting_evidence set {sorted(ev_a)} -- "
                            "a possible overlap signal, not conclusive duplication",
                            False,
                        )
                    )
    return findings


def run_all(project_root: Path = ROOT, repo_root: Path | None = DEFAULT_LEDGERKIT_ROOT) -> list[Finding]:
    """`repo_root` defaults to `~/projects/ledgerkit`, matching `check_
    contracts.py`/`check_knowledge_base.py`'s own `--ledgerkit-root`
    default exactly; pass `None` (or a non-existent path) to confirm the
    honest `unconfirmed` behaviour when no live checkout is reachable
    (decisions/0082 §A's own "cannot currently confirm" treatment)."""
    ka, ki, oracle = _load_codecompass()
    if ka is None or ki is None or oracle is None:
        return [
            Finding(
                "self-knowledge-quality-unimportable",
                "could not import codecompass's knowledge_api/knowledge_intermediate/oracle "
                "modules (src/ not importable, or a required dependency is missing) -- no "
                "self-knowledge-quality check could run",
            )
        ]
    findings: list[Finding] = []
    findings.extend(check_find_gaps_composed(project_root, ka, repo_root, ki))
    findings.extend(check_knowledge_status_composed(project_root, ki))
    findings.extend(check_missing_evidence_composed(project_root, ka, ki, repo_root))
    findings.extend(check_test_ref_files(project_root, ki, oracle))
    findings.extend(check_duplicate_overlap(project_root, ki))
    return sorted(findings, key=lambda f: (f.rule, f.message))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--strict",
        action="store_true",
        help="exit 1 if any blocking finding is reported (default: always exit 0)",
    )
    parser.add_argument("--ledgerkit-root", type=Path, default=DEFAULT_LEDGERKIT_ROOT)
    args = parser.parse_args()

    findings = run_all(ROOT, args.ledgerkit_root)
    blocking = [f for f in findings if f.strict]

    if not findings:
        print("check_self_knowledge_quality: no findings")
    else:
        print(f"check_self_knowledge_quality: {len(findings)} finding(s)")
        for f in findings:
            tag = "" if f.strict else " (info)"
            print(f"  [{f.rule}]{tag} {f.message}")

    return 1 if (args.strict and blocking) else 0


if __name__ == "__main__":
    sys.exit(main())
