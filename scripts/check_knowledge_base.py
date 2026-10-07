"""Maintainer-only smoke check for Phase 54c's evidence/knowledge model
(planning/knowledge/<feature-slug>/*.yaml, design.md, context-packet.md)
and, since Phase 79, its snapshot artefacts
(planning/knowledge/<feature-slug>/snapshots/*.toml). Mechanical only —
no edits, no AI calls, no YAML library dependency (hand-rolled parsing
sufficient for this flat, six-kind record shape, same "avoid an unneeded
dependency" posture reference_pipeline.py::load_references_toml already
established for a comparably simple format). Snapshot sidecars are TOML,
not YAML, precisely because they are genuinely nested (an assertion's own
supporting-evidence/derivation chain) in a way the flat records above are
not — parsed with stdlib `tomllib` (this project's own `pyproject.toml`
already requires Python >=3.11 specifically so `tomllib` needs no
dependency), not by extending the hand-rolled flat parser to handle
nesting it was never designed for. See
planning/phase-54c-evidence-knowledge-workflow.md §2/§9 and
planning/phase-79-clean-room-understanding-and-documentation-reconstruction.md
§4-§5.

Not part of the codecompass package: this checks CodeCompass's own
planning artefacts, not a consuming project's. Not shipped, not a
`codecompass` subcommand.

    python scripts/check_knowledge_base.py [--strict]

Report-only by default (always exits 0). `--strict` exits 1 if any
*blocking* finding is reported, mirroring check_user_docs.py's own
convention exactly.

Checks, per planning/phase-54c-evidence-knowledge-workflow.md §2/§9:
- every record has the required fields for its `kind`;
- every cross-referenced id resolves to a real file in the same feature
  directory;
- `status` values come from the closed set for that record's `kind`;
- the structural hard rule (§5.2): a Claim's `supersedes` only ever
  names another Claim; a Decision's `supersedes` only ever names another
  Decision — never across kinds;
- every id cited from a feature's `design.md`/`context-packet.md`
  actually exists as a record in that same feature directory (the
  *only* direction required — a stored record has no obligation to be
  cited from either document, §4's own explicit non-requirement).

Checks added Phase 79 (planning/phase-79-...md §4.2, §5.3):
- the new optional Claim fields (`assertion_kind`/`basis`/
  `evidence_support_state`), when present, use one of their own closed
  values;
- every list-valued field (`supporting_evidence`/`contradicting_evidence`/
  `examples`/`counterexamples`/`depends_on`/`open_questions`), when
  present, uses the inline `[a, b]` form this parser can actually
  validate — fail-closed: the *parsed value* is checked directly against
  the inline-form shape, not a pattern-match against one named bad YAML
  shape, so a block-style list (indented or not, with or without
  intervening comments/blank lines — none of which this parser's own
  single-line key:value capture can see) is caught uniformly;
- a snapshot's own cited historical content still matches the exact git
  revision it was frozen from (`check_snapshot_historical_integrity` —
  should always pass; a failure means tampering or rewritten history,
  never a legitimate supersession, since that only ever touches the
  *current*, not the *historical*, file);
- whether a snapshot's cited assertions have since diverged from their
  current, live record (`check_snapshot_current_divergence` —
  informational only, never `--strict`-blocking; a legitimate
  supersession or withdrawal is *expected* to diverge here).

Checks added Phase 81 (planning/phase-81-intermediate-knowledge-layer.md
§11/§14.3): a Requirement's `decision:` field must resolve to a Decision
whose own `status` is `approved`, not merely to any resolvable record
(`check_requirement_cites_approved_decision`); every stable knowledge
anchor in a slug's own `intermediate/*.md` projection must resolve to a
real record of the matching kind (`check_anchor_integrity`). Phase 81
adds no new record kind and no new persisted field — both checks operate
entirely on the existing schema.
"""

from __future__ import annotations

import argparse
import hashlib
import re
import subprocess
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KNOWLEDGE_DIR = ROOT / "planning" / "knowledge"

_ID_PATTERN = re.compile(r"\b(OBS|EV|CL|DE|DEC|REQ)-[A-Z0-9]+-\d+\b")

_REQUIRED_FIELDS: dict[str, set[str]] = {
    "observation": {
        "id",
        "kind",
        "method",
        "what_was_done",
        "repository_revision",
        "timestamp",
        "performed_by",
        "status",
    },
    "evidence": {
        "id",
        "kind",
        "evidence_kind",
        "what_it_shows",
        "repository_revision",
        "status",
    },
    "claim": {
        "id",
        "kind",
        "statement",
        "derivation",
        "supporting_evidence",
        "contradicting_evidence",
        "derived_by",
        "repository_revision",
        "timestamp",
        "status",
    },
    "derivation": {
        "id",
        "kind",
        "claim",
        "method",
        "inputs",
        "performed_by",
        "timestamp",
    },
    "decision": {
        "id",
        "kind",
        "decides",
        "rationale",
        "supersedes",
        "decided_by",
        "timestamp",
        "status",
    },
    "requirement": {
        "id",
        "kind",
        "statement",
        "example",
        "decision",
        "status",
    },
}

_STATUS_ENUMS: dict[str, set[str]] = {
    "observation": {"recorded"},
    "evidence": {"current", "superseded"},
    "claim": {"proposed", "supported", "contradicted", "superseded", "verified"},
    "decision": {"proposed", "approved", "rejected", "superseded"},
    "requirement": {"proposed", "approved", "implemented", "verified"},
}

_ID_PREFIX_FOR_KIND = {
    "observation": "OBS",
    "evidence": "EV",
    "claim": "CL",
    "derivation": "DE",
    "decision": "DEC",
    "requirement": "REQ",
}

# Phase 79: optional Claim fields carrying an understanding assertion.
# Absent entirely for an ordinary feature-scoped Claim -- no existing
# record needs to gain any of these.
_OPTIONAL_ENUM_FIELDS: dict[str, dict[str, set[str]]] = {
    "claim": {
        "assertion_kind": {
            "definition",
            "relationship",
            "rule",
            "invariant",
            "state_transformation",
            "boundary",
            # Phase 81: a named, ordered sequence of claims (expressible via
            # depends_on, but losing real meaning if forced into
            # "relationship") and a cross-cutting limitation distinct from a
            # "rule" in the narrower sense already covered above.
            "workflow",
            "constraint",
        },
        "basis": {
            "directly_stated",
            "inferred",
            "proposed_policy",
            "observed_behaviour",
        },
        "evidence_support_state": {
            "supported",
            "partially_supported",
            "unsupported",
            "conflicting",
        },
    },
}

# Every list-valued field this parser can validate at all -- each must
# use the inline `[a, b]` form (see check_list_fields_are_inline).
_LIST_VALUED_FIELDS = {
    "supporting_evidence",
    "contradicting_evidence",
    "examples",
    "counterexamples",
    "depends_on",
    "open_questions",
}
_INLINE_LIST_RE = re.compile(r"^\[.*\]$")


@dataclass
class Finding:
    rule: str
    message: str
    strict: bool = True  # False = informational, never fails --strict


def _strip_inline_comment(value: str) -> str:
    """Strip a trailing ` # ...` inline comment, respecting that `#` can
    legitimately appear inside a quoted string — same simple, good-enough
    heuristic reference_pipeline.py's own hand-rolled TOML rendering
    accepts (this checker only needs the value well enough to spot an id
    or a bare status word, not to round-trip prose).
    """
    if '"' in value or "'" in value:
        return value.strip()
    idx = value.find(" #")
    return (value[:idx] if idx != -1 else value).strip()


def parse_record_text(text: str) -> dict[str, str]:
    """Same hand-rolled, deliberately minimal parse as `parse_record`,
    operating on already-read text rather than a filesystem path — so a
    historical git-blob string (never written to disk) can be parsed the
    same way a live file is, without a temp-file detour. Every top-level
    (column-0) `key: value` pair. Multi-line `>`/`|` block scalars are
    recognised (the key is present) but their continuation lines are not
    reconstructed — this checker only needs field *presence* and short
    scalar/list values (ids, statuses), never a record's own prose
    content.
    """
    fields: dict[str, str] = {}
    for line in text.splitlines():
        if not line or line[0] in " \t#":
            continue
        match = re.match(r"^([a-zA-Z_][a-zA-Z0-9_]*):\s*(.*)$", line)
        if not match:
            continue
        key, value = match.group(1), _strip_inline_comment(match.group(2))
        fields[key] = value
    return fields


def parse_record(path: Path) -> dict[str, str]:
    """`parse_record_text`, reading `path` first."""
    return parse_record_text(path.read_text(encoding="utf-8"))


def _extract_id_strings(value: str) -> list[str]:
    """Every `PREFIX-FEATURE-NNN`-shaped id mentioned in a field's raw
    value (handles a bare id, `null`, or a `[a, b]`-style bracketed
    list equally, since this checker only needs the ids themselves)."""
    return [m.group(0) for m in _ID_PATTERN.finditer(value)]


def check_required_fields(feature_dir: Path) -> list[Finding]:
    findings: list[Finding] = []
    for yaml_path in sorted(feature_dir.glob("*.yaml")):
        fields = parse_record(yaml_path)
        kind = fields.get("kind")
        if kind not in _REQUIRED_FIELDS:
            findings.append(
                Finding(
                    "knowledge-base-unknown-kind",
                    f"{yaml_path.relative_to(ROOT)}: kind={kind!r} is not one "
                    f"of {sorted(_REQUIRED_FIELDS)}",
                )
            )
            continue
        missing = _REQUIRED_FIELDS[kind] - fields.keys()
        if missing:
            findings.append(
                Finding(
                    "knowledge-base-missing-field",
                    f"{yaml_path.relative_to(ROOT)}: missing required field(s) "
                    f"for kind={kind}: {sorted(missing)}",
                )
            )
        prefix = _ID_PREFIX_FOR_KIND[kind]
        record_id = fields.get("id", "")
        if not record_id.startswith(f"{prefix}-"):
            findings.append(
                Finding(
                    "knowledge-base-id-prefix-mismatch",
                    f"{yaml_path.relative_to(ROOT)}: id={record_id!r} does not "
                    f"start with the expected prefix {prefix!r} for kind={kind}",
                )
            )
    return findings


def check_status_enums(feature_dir: Path) -> list[Finding]:
    findings: list[Finding] = []
    for yaml_path in sorted(feature_dir.glob("*.yaml")):
        fields = parse_record(yaml_path)
        kind = fields.get("kind")
        if kind not in _STATUS_ENUMS:
            continue  # derivation has no status field
        status = fields.get("status", "")
        if status not in _STATUS_ENUMS[kind]:
            findings.append(
                Finding(
                    "knowledge-base-bad-status",
                    f"{yaml_path.relative_to(ROOT)}: status={status!r} is not "
                    f"one of {sorted(_STATUS_ENUMS[kind])} for kind={kind}",
                )
            )
    return findings


def check_optional_enum_fields(feature_dir: Path, root: Path = ROOT) -> list[Finding]:
    """Phase 79: any of the fields in _OPTIONAL_ENUM_FIELDS, if present at
    all, must use one of its own closed values. Absence is always fine --
    these fields are optional, unlike `status`. `root` defaults to the
    real repository but is threaded through explicitly so tests can point
    this at a disposable fixture directory outside it."""
    findings: list[Finding] = []
    for yaml_path in sorted(feature_dir.glob("*.yaml")):
        fields = parse_record(yaml_path)
        kind = fields.get("kind")
        enum_fields = _OPTIONAL_ENUM_FIELDS.get(kind, {})
        for field, allowed in enum_fields.items():
            if field not in fields:
                continue
            value = fields[field]
            if value not in allowed:
                findings.append(
                    Finding(
                        "knowledge-base-bad-optional-enum",
                        f"{yaml_path.relative_to(root)}: field {field!r}="
                        f"{value!r} is not one of {sorted(allowed)}",
                    )
                )
    return findings


def check_list_fields_are_inline(feature_dir: Path, root: Path = ROOT) -> list[Finding]:
    """Phase 79: every list-valued field, when present, must use the
    inline `[a, b]` form -- validated by checking the *parsed* value
    directly against that shape, fail-closed, rather than pattern-matching
    the raw YAML text for one named bad shape (a block list, with or
    without an intervening comment/blank line, indented or not, all parse
    to the same empty/malformed value via parse_record's own single-line
    key:value capture -- checking the parsed value catches every one of
    them uniformly, including a shape not specifically enumerated here).
    `root` defaults to the real repository but is threaded through
    explicitly so tests can point this at a disposable fixture directory
    outside it.
    """
    findings: list[Finding] = []
    for yaml_path in sorted(feature_dir.glob("*.yaml")):
        fields = parse_record(yaml_path)
        if fields.get("kind") != "claim":
            continue
        for field in _LIST_VALUED_FIELDS:
            if field not in fields:
                continue  # absent is fine -- every one of these is optional
            value = fields[field]
            if not _INLINE_LIST_RE.match(value):
                findings.append(
                    Finding(
                        "knowledge-base-non-inline-list",
                        f"{yaml_path.relative_to(root)}: field {field!r} "
                        f"is present but its parsed value {value!r} is "
                        "not the inline `[a, b]` form this parser can "
                        "validate -- if this was written as a YAML block "
                        "list (indented or not, with or without "
                        "intervening comments/blank lines), it parses as "
                        "an empty string and would otherwise silently "
                        "skip all cross-reference/dangling-id checking "
                        "for this field",
                    )
                )
    return findings


def check_cross_references_resolve(
    feature_dir: Path, all_known_ids: set[str] | None = None
) -> list[Finding]:
    """Every id mentioned in another record's own fields must exist as a
    real `<id>.yaml`-derived file — normally in the same feature
    directory (the naming convention this phase uses: one file per
    record, named however is convenient, but always containing
    `id: <the same id>`), but a project-scoped corpus (Phase 63D's own
    `codecompass-domain/`, which deliberately cites real examples from
    other features' own knowledge folders as required "at least one
    concrete example" evidence) may legitimately cite an id that only
    exists in a *different* feature directory. `all_known_ids`, when
    given, is the union of every record id across all of
    `planning/knowledge/*/` — checked as a fallback only after the
    local (same-directory) scope fails to resolve, so a genuinely
    dangling reference is still reported exactly as before.
    """
    findings: list[Finding] = []
    known_ids: set[str] = set()
    file_fields: dict[Path, dict[str, str]] = {}
    for yaml_path in sorted(feature_dir.glob("*.yaml")):
        fields = parse_record(yaml_path)
        file_fields[yaml_path] = fields
        if "id" in fields:
            known_ids.add(fields["id"])

    for yaml_path, fields in file_fields.items():
        this_id = fields.get("id", "")
        for key, value in fields.items():
            if key in ("id",):
                continue
            for referenced_id in _extract_id_strings(value):
                if referenced_id == this_id:
                    continue  # a self-mention in prose, not a dangling reference
                if referenced_id in known_ids:
                    continue
                if all_known_ids is not None and referenced_id in all_known_ids:
                    # Resolves in another feature directory — a legitimate
                    # cross-directory citation.
                    continue
                findings.append(
                    Finding(
                        "knowledge-base-dangling-reference",
                        f"{yaml_path.relative_to(ROOT)}: field {key!r} "
                        f"references {referenced_id!r}, which has no "
                        f"matching record in {feature_dir.relative_to(ROOT)} "
                        "or any other planning/knowledge/ directory",
                    )
                )
    return findings


def check_supersedes_never_crosses_kind(feature_dir: Path) -> list[Finding]:
    """The structural hard rule
    (planning/phase-54c-evidence-knowledge-workflow.md §5.2): a Claim's
    `supersedes` only ever names another Claim (CL-...); a Decision's
    `supersedes` only ever names another Decision (DEC-...) — never a
    Decision superseding a Claim, or vice versa.
    """
    findings: list[Finding] = []
    for yaml_path in sorted(feature_dir.glob("*.yaml")):
        fields = parse_record(yaml_path)
        kind = fields.get("kind")
        if kind not in ("claim", "decision"):
            continue
        supersedes = fields.get("supersedes", "")
        referenced = _extract_id_strings(supersedes)
        if not referenced:
            continue
        expected_prefix = _ID_PREFIX_FOR_KIND[kind]
        for ref in referenced:
            if not ref.startswith(f"{expected_prefix}-"):
                findings.append(
                    Finding(
                        "knowledge-base-cross-kind-supersede",
                        f"{yaml_path.relative_to(ROOT)}: a {kind}'s "
                        f"`supersedes` names {ref!r}, which is not a "
                        f"{expected_prefix}-... id — a {kind} may only "
                        f"supersede another {kind} (see §5.2's hard rule: "
                        "a Decision must never supersede a Claim)",
                    )
                )
    return findings


def check_requirement_cites_approved_decision(
    feature_dir: Path,
    all_decision_status: dict[str, str] | None = None,
    root: Path = ROOT,
) -> list[Finding]:
    """Phase 81 (§11/§14.3): a Requirement's `decision:` field must not
    merely *resolve* to a real record (already covered by
    `check_cross_references_resolve`) — the record it resolves to must be
    a Decision whose own `status` is `approved`. Closes a real,
    previously-unenforced gap: nothing before this checked that a
    Requirement's authorising Decision was ever actually approved, rather
    than merely proposed, rejected, or superseded. `all_decision_status`,
    when given, is the id->status map for every Decision across every
    `planning/knowledge/*/` directory (a Requirement may legitimately cite
    a Decision recorded in a different feature directory, exactly as
    `check_cross_references_resolve` already allows for cross-directory
    citation) — checked as a fallback only after the local (same-
    directory) scope fails to resolve.
    """
    findings: list[Finding] = []
    local_decision_status: dict[str, str] = {}
    for yaml_path in feature_dir.glob("*.yaml"):
        fields = parse_record(yaml_path)
        if fields.get("kind") == "decision" and fields.get("id"):
            local_decision_status[fields["id"]] = fields.get("status", "")

    for yaml_path in sorted(feature_dir.glob("*.yaml")):
        fields = parse_record(yaml_path)
        if fields.get("kind") != "requirement":
            continue
        decision_id = fields.get("decision", "")
        referenced = _extract_id_strings(decision_id)
        if not referenced:
            continue  # missing entirely is already reported by check_required_fields
        cited = referenced[0]
        status = local_decision_status.get(cited)
        if status is None and all_decision_status is not None:
            status = all_decision_status.get(cited)
        if status is None:
            continue  # dangling reference already reported by check_cross_references_resolve
        if status != "approved":
            findings.append(
                Finding(
                    "knowledge-base-requirement-cites-unapproved-decision",
                    f"{yaml_path.relative_to(root)}: decision={cited!r} has "
                    f"status={status!r}, not 'approved' — a Requirement must "
                    "cite a Decision that has actually been approved, never "
                    "one that is merely proposed, rejected, or superseded",
                )
            )
    return findings


def check_anchor_integrity(feature_dir: Path, root: Path = ROOT) -> list[Finding]:
    """Phase 81 (§4.3/§11): every stable knowledge anchor in a slug's own
    `intermediate/*.md` projection must resolve to a real record, and that
    record's own `kind` must match the id's own prefix — identity, not
    merely a hash match, the same discipline Phase 80 hardened for
    snapshots, applied here to live projections. The anchor's own
    semantic/projection hashes are reconciliation's own concern
    (`knowledge select-candidates`), not this structural check's.
    """
    findings: list[Finding] = []
    intermediate_dir = feature_dir / "intermediate"
    if not intermediate_dir.is_dir():
        return findings
    known_kind_by_id: dict[str, str] = {}
    for yaml_path in feature_dir.glob("*.yaml"):
        fields = parse_record(yaml_path)
        if fields.get("id"):
            known_kind_by_id[fields["id"]] = fields.get("kind", "")

    anchor_re = re.compile(
        r"<!--\s*codecompass-knowledge:\s*([A-Z]+-[A-Z0-9]+-\d+)\b"
    )
    for md_path in sorted(intermediate_dir.glob("*.md")):
        text = md_path.read_text(encoding="utf-8")
        for match in anchor_re.finditer(text):
            anchor_id = match.group(1)
            prefix = anchor_id.split("-", 1)[0]
            expected_kind = {
                v: k for k, v in _ID_PREFIX_FOR_KIND.items()
            }.get(prefix)
            kind = known_kind_by_id.get(anchor_id)
            if kind is None:
                findings.append(
                    Finding(
                        "knowledge-base-dangling-anchor",
                        f"{md_path.relative_to(root)}: anchor cites "
                        f"{anchor_id!r}, which has no matching record in "
                        f"{feature_dir.relative_to(root)}",
                    )
                )
            elif expected_kind is not None and kind != expected_kind:
                findings.append(
                    Finding(
                        "knowledge-base-anchor-kind-mismatch",
                        f"{md_path.relative_to(root)}: anchor cites "
                        f"{anchor_id!r} as if it were a {expected_kind!r}, "
                        f"but the matching record's own kind is {kind!r}",
                    )
                )
    return findings


def check_design_doc_citations_resolve(feature_dir: Path) -> list[Finding]:
    """Every id cited from `design.md`/`context-packet.md` must exist as
    a real record — the *only* direction required (§4's own explicit
    non-requirement: a stored record need not be cited from either
    document).
    """
    findings: list[Finding] = []
    known_ids = {
        parse_record(p).get("id", "") for p in feature_dir.glob("*.yaml")
    }
    known_ids.discard("")
    for doc_name in ("design.md", "context-packet.md"):
        doc_path = feature_dir / doc_name
        if not doc_path.is_file():
            continue
        text = doc_path.read_text(encoding="utf-8")
        for cited_id in sorted(set(_extract_id_strings(text))):
            if cited_id not in known_ids:
                findings.append(
                    Finding(
                        "knowledge-base-dangling-citation",
                        f"{doc_path.relative_to(ROOT)}: cites {cited_id!r}, "
                        f"which has no matching record in "
                        f"{feature_dir.relative_to(ROOT)}",
                    )
                )
    return findings


def _git_show_content(root: Path, repository_revision: str, path: str) -> str | None:
    """The exact historical content of `path` at `repository_revision`,
    via `git show <rev>:<path>` -- the real historical git blob, never
    the live working-tree file. `None` if the revision/path can't be
    resolved (e.g. a shallow clone, or a path that did not exist at that
    revision) -- treated as its own finding, never a crash. `root` is
    threaded through explicitly (rather than hardcoded to the module's
    own `ROOT`) so tests can point this at a disposable git fixture."""
    try:
        result = subprocess.run(
            ["git", "show", f"{repository_revision}:{path}"],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return None
    if result.returncode != 0:
        return None
    return result.stdout


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _git_list_files_at_revision(root: Path, revision: str, dir_path: Path) -> list[str] | None:
    """Every file git tracked under `dir_path` (relative-to-`root`
    already resolved by the caller into a real path) at `revision` --
    the historical directory listing, never the live filesystem's own
    `glob`. Returns `None` if the revision can't be resolved (shallow
    clone, bad ref), the same "unresolvable, report it, don't crash"
    contract `_git_show_content` already uses. Used specifically so a
    snapshot's own assertion-inventory completeness is checked against
    what existed *at its own freeze revision* -- a snapshot frozen before
    a later Claim was ever created must never be flagged as "incomplete"
    for not capturing it (that is ordinary, healthy history, not
    truncation).
    """
    try:
        rel_dir = dir_path.relative_to(root)
    except ValueError:
        rel_dir = dir_path
    try:
        result = subprocess.run(
            ["git", "ls-tree", "-r", "--name-only", revision, "--", str(rel_dir)],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return None
    if result.returncode != 0:
        return None
    return [line for line in result.stdout.splitlines() if line]


def _iter_snapshot_files(feature_dir: Path):
    snapshots_dir = feature_dir / "snapshots"
    if not snapshots_dir.is_dir():
        return
    yield from sorted(snapshots_dir.glob("snapshot-*.toml"))


_SNAPSHOT_CLOSURE_SUB_KINDS = ("supporting_evidence", "contradicting_evidence")


def _iter_snapshot_entries(snapshot: dict):
    """Yield `(dotted_label, entry_dict)` for every assertion and its
    `supporting_evidence`/`contradicting_evidence`/`derivation` entries in
    a parsed snapshot TOML structure (planning/phase-79-...md §5.2).
    Defensive against a malformed/truncated sidecar (a non-dict
    `assertions` table, a non-dict assertion/sub-entry) -- silently skips
    what it can't iterate rather than raising, since `check_snapshot_completeness`
    is what reports a malformed structure as its own actionable finding;
    the hash-integrity/divergence checks below must still be able to
    process whatever *is* well-formed in the same snapshot."""
    assertions = snapshot.get("assertions", {})
    if not isinstance(assertions, dict):
        return
    for assertion_id, assertion in assertions.items():
        if not isinstance(assertion, dict):
            continue
        yield assertion_id, assertion
        for sub_kind in (
            "supporting_evidence",
            "contradicting_evidence",
            "derivation",
        ):
            sub_table = assertion.get(sub_kind, {})
            if not isinstance(sub_table, dict):
                continue
            for sub_id, sub_entry in sub_table.items():
                if not isinstance(sub_entry, dict):
                    continue
                yield f"{assertion_id}.{sub_kind}.{sub_id}", sub_entry


_SNAPSHOT_REQUIRED_METADATA: dict[str, type] = {
    "snapshot_id": str,
    "created": str,
    "repository_revision_at_freeze": str,
    "excluded_assertions": list,
}


_EXPECTED_KIND_FOR_SUB_KIND = {
    "supporting_evidence": "evidence",
    "contradicting_evidence": "evidence",
    "derivation": "derivation",
}


def _validate_nested_entries(
    root: Path,
    rel: Path,
    assertion_id: str,
    sub_kind: str,
    sub_table: object,
) -> tuple[set[str], list[Finding]]:
    """Validates every entry in one assertion's own nested
    `supporting_evidence`/`contradicting_evidence`/`derivation` table --
    closing the gap where a sub-table's own *keys* were previously treated
    as "captured" regardless of whether each key's *value* was a
    well-formed table, pointed at the record it claims to (by id), or
    pointed at a record of the right *kind*. Returns the subset of keys
    that are genuinely, validly captured (only these satisfy closure --
    see `check_snapshot_completeness`'s own use of this), plus the
    findings for everything that doesn't qualify. Never raises on a
    malformed input; every malformed shape becomes its own Finding.
    """
    findings: list[Finding] = []
    valid_ids: set[str] = set()
    if not isinstance(sub_table, dict):
        return valid_ids, findings  # reported separately, by the caller, as a top-level shape issue

    expected_kind = _EXPECTED_KIND_FOR_SUB_KIND[sub_kind]
    for entry_id, entry in sub_table.items():
        label = f"assertions[{assertion_id!r}].{sub_kind}[{entry_id!r}]"
        if not isinstance(entry, dict):
            findings.append(
                Finding(
                    "knowledge-base-snapshot-malformed-structure",
                    f"{rel}: {label} must be a table, got "
                    f"{type(entry).__name__} ({entry!r}) -- a scalar here "
                    "cannot carry a real path/repository_revision/"
                    "content_hash, so this entry cannot be validated and "
                    "does not count as capturing anything",
                )
            )
            continue

        entry_path = entry.get("path")
        entry_rev = entry.get("repository_revision")
        if not (isinstance(entry_path, str) and isinstance(entry_rev, str)):
            # Already reported by check_snapshot_historical_integrity's own
            # incomplete-entry finding (it walks every well-formed dict
            # entry _iter_snapshot_entries yields, including nested ones).
            continue

        content = _git_show_content(root, entry_rev, entry_path)
        if content is None:
            continue  # already reported as unresolvable, by the same function

        real_fields = parse_record_text(content)
        real_id = real_fields.get("id")
        real_kind = real_fields.get("kind")
        ok = True
        if not real_id:
            findings.append(
                Finding(
                    "knowledge-base-snapshot-identity-missing",
                    f"{rel}: {label} cites path {entry_path!r} at revision "
                    f"{entry_rev!r}, whose historical content has no `id:` "
                    f"field at all -- it cannot be confirmed to actually be "
                    f"{entry_id!r} (or any record), not merely a hash match "
                    "for some arbitrary committed content",
                )
            )
            ok = False
        elif real_id != entry_id:
            findings.append(
                Finding(
                    "knowledge-base-snapshot-identity-mismatch",
                    f"{rel}: {label} cites path {entry_path!r} at revision "
                    f"{entry_rev!r}, whose own record id is {real_id!r}, "
                    f"not {entry_id!r} -- this entry's key does not match "
                    "what it actually points to",
                )
            )
            ok = False
        if not real_kind:
            findings.append(
                Finding(
                    "knowledge-base-snapshot-kind-missing",
                    f"{rel}: {label} cites path {entry_path!r} at revision "
                    f"{entry_rev!r}, whose historical content has no `kind:` "
                    f"field at all -- it cannot be confirmed to actually be "
                    f"a {expected_kind!r}-kind record",
                )
            )
            ok = False
        elif real_kind != expected_kind:
            findings.append(
                Finding(
                    "knowledge-base-snapshot-kind-mismatch",
                    f"{rel}: {label} must cite a {expected_kind!r}-kind "
                    f"record, but {entry_path!r}@{entry_rev!r} is "
                    f"kind={real_kind!r}",
                )
            )
            ok = False
        if ok:
            valid_ids.add(entry_id)
    return valid_ids, findings


def check_snapshot_completeness(feature_dir: Path, root: Path = ROOT) -> list[Finding]:
    """Fail-closed structural/completeness validation for a snapshot
    sidecar -- distinct from `check_snapshot_historical_integrity`'s own
    hash-tampering check (which only validates entries already *present*,
    and so returns zero findings against a sidecar truncated down to
    nothing but its own `snapshot_id`). This check validates that the
    sidecar is actually the complete thing it claims to be:

    1. Required top-level metadata (`snapshot_id`/`created`/
       `repository_revision_at_freeze`/`excluded_assertions`) is present
       and correctly typed.
    2. `assertions` is present and is a table (never silently treated as
       "zero assertions is fine" the way a missing key would be).
    3. **Assertion inventory**: every real `CL-*.yaml` Claim record in
       `feature_dir`, not named in `excluded_assertions`, has a matching
       entry in the snapshot's own `assertions` table -- this is what
       catches a sidecar reduced to only `snapshot_id`, where real Claims
       exist on disk but none were actually captured.
    4. **Record identity**: every entry's own `path` resolves to a real
       file whose own `id:` field matches the key the snapshot filed it
       under (catches a copy-paste/key-typo mismatch).
    5. **Evidence/Derivation closure, including nested-entry validity**:
       for every assertion the snapshot does capture, the real historical
       record's own `supporting_evidence`/`contradicting_evidence`/
       `derivation` citations (read from the exact git-blob content at
       the snapshot's own recorded `repository_revision` for that
       assertion -- the same historical source
       `check_snapshot_historical_integrity` hashes, never the live file)
       must each have a matching nested entry in the snapshot's own
       sidecar -- and that nested entry must itself be a well-formed
       table whose own `path`/`repository_revision` resolve to a real
       record with a matching `id` *and* the expected `kind`
       (`evidence` for `supporting_evidence`/`contradicting_evidence`,
       `derivation` for `derivation`). A nested key is never treated as
       "captured" merely for being present: a scalar standing in for the
       required table, or a key that resolves to a *different* real
       record than the id it's filed under (or a record of the wrong
       kind), is exactly as much a gap as the key being absent outright,
       and is reported as its own distinct finding
       (`knowledge-base-snapshot-malformed-structure` /
       `knowledge-base-snapshot-identity-mismatch` /
       `knowledge-base-snapshot-kind-mismatch`) in addition to the
       resulting incomplete-closure finding.

    Every condition below produces an actionable `Finding` -- never an
    uncaught exception -- regardless of how malformed the sidecar is.
    `root` defaults to the real repository but is threaded through
    explicitly so tests can point this at a disposable git fixture.
    """
    findings: list[Finding] = []

    for snapshot_path in _iter_snapshot_files(feature_dir):
        try:
            snapshot = tomllib.loads(snapshot_path.read_text(encoding="utf-8"))
        except tomllib.TOMLDecodeError:
            continue  # already reported by check_snapshot_historical_integrity
        rel = snapshot_path.relative_to(root) if root in snapshot_path.parents else snapshot_path

        for field, expected_type in _SNAPSHOT_REQUIRED_METADATA.items():
            if field not in snapshot:
                findings.append(
                    Finding(
                        "knowledge-base-snapshot-missing-metadata",
                        f"{rel}: missing required top-level field {field!r}",
                    )
                )
            elif not isinstance(snapshot[field], expected_type):
                findings.append(
                    Finding(
                        "knowledge-base-snapshot-malformed-structure",
                        f"{rel}: top-level field {field!r} must be a "
                        f"{expected_type.__name__}, got "
                        f"{type(snapshot[field]).__name__}",
                    )
                )

        excluded = snapshot.get("excluded_assertions", [])
        if not isinstance(excluded, list):
            excluded = []  # already reported above; don't let it crash this pass
        excluded = {x for x in excluded if isinstance(x, str)}

        assertions = snapshot.get("assertions")
        if assertions is None:
            findings.append(
                Finding(
                    "knowledge-base-snapshot-missing-metadata",
                    f"{rel}: missing required top-level field 'assertions'",
                )
            )
            assertions = {}
        elif not isinstance(assertions, dict):
            findings.append(
                Finding(
                    "knowledge-base-snapshot-malformed-structure",
                    f"{rel}: top-level field 'assertions' must be a table, "
                    f"got {type(assertions).__name__}",
                )
            )
            assertions = {}

        # 3. Assertion inventory: every Claim that existed at this
        # snapshot's own freeze revision, and isn't excluded, must be
        # captured -- checked against the historical directory listing at
        # `repository_revision_at_freeze`, never the live filesystem, so
        # a snapshot frozen before a later Claim existed is never wrongly
        # flagged for "missing" it (that's ordinary history, not
        # truncation -- the same distinction check_snapshot_current_divergence
        # already draws between tampering and legitimate change).
        freeze_rev = snapshot.get("repository_revision_at_freeze")
        if isinstance(freeze_rev, str):
            historical_files = _git_list_files_at_revision(root, freeze_rev, feature_dir)
            if historical_files is None:
                findings.append(
                    Finding(
                        "knowledge-base-snapshot-unresolvable-revision",
                        f"{rel}: its own repository_revision_at_freeze "
                        f"{freeze_rev!r} could not be resolved by `git "
                        "ls-tree` -- cannot check assertion-inventory "
                        "completeness against it",
                    )
                )
            else:
                real_claim_ids: set[str] = set()
                for rel_path in historical_files:
                    if not Path(rel_path).name.startswith("CL-"):
                        continue
                    content = _git_show_content(root, freeze_rev, rel_path)
                    if content is None:
                        continue
                    record_id = parse_record_text(content).get("id")
                    if record_id:
                        real_claim_ids.add(record_id)
                for claim_id in sorted(real_claim_ids):
                    if claim_id in excluded:
                        continue
                    if claim_id not in assertions:
                        findings.append(
                            Finding(
                                "knowledge-base-snapshot-missing-assertion",
                                f"{rel}: real record {claim_id!r} existed at "
                                f"this snapshot's own freeze revision "
                                f"({freeze_rev!r}) and is not listed in "
                                "excluded_assertions, but has no entry in "
                                "this snapshot's own assertions table -- "
                                "the snapshot is incomplete",
                            )
                        )

        # 4 & 5: per-captured-assertion identity + closure, only for
        # well-formed entries (a malformed one was already reported by
        # check_snapshot_historical_integrity's own incomplete-entry finding).
        for assertion_id, assertion in assertions.items():
            if not isinstance(assertion, dict):
                findings.append(
                    Finding(
                        "knowledge-base-snapshot-malformed-structure",
                        f"{rel}: assertions[{assertion_id!r}] must be a "
                        f"table, got {type(assertion).__name__}",
                    )
                )
                continue

            entry_path = assertion.get("path")
            rev = assertion.get("repository_revision")
            if not (isinstance(entry_path, str) and isinstance(rev, str)):
                continue  # already reported as an incomplete entry
            historical = _git_show_content(root, rev, entry_path)
            if historical is None:
                continue  # already reported as unresolvable

            historical_fields = parse_record_text(historical)

            # Identity + kind, checked against the exact historical content
            # at the snapshot's own recorded revision -- never the live
            # file, for the same reason every other check here hashes
            # history, not the working tree. A record with no `id:`/`kind:`
            # field at all is not "fine because it doesn't contradict" --
            # it is unidentified, which `if real_id and real_id != X` used
            # to silently treat as a pass.
            real_assertion_id = historical_fields.get("id")
            if not real_assertion_id:
                findings.append(
                    Finding(
                        "knowledge-base-snapshot-identity-missing",
                        f"{rel}: assertions[{assertion_id!r}] cites path "
                        f"{entry_path!r} at revision {rev!r}, whose "
                        "historical content has no `id:` field at all -- it "
                        f"cannot be confirmed to actually be {assertion_id!r} "
                        "(or any record), not merely a hash match for some "
                        "arbitrary committed content",
                    )
                )
            elif real_assertion_id != assertion_id:
                findings.append(
                    Finding(
                        "knowledge-base-snapshot-identity-mismatch",
                        f"{rel}: assertions[{assertion_id!r}] cites "
                        f"path {entry_path!r}, whose own record id is "
                        f"{real_assertion_id!r}, not {assertion_id!r}",
                    )
                )
            real_assertion_kind = historical_fields.get("kind")
            if not real_assertion_kind:
                findings.append(
                    Finding(
                        "knowledge-base-snapshot-kind-missing",
                        f"{rel}: assertions[{assertion_id!r}] cites path "
                        f"{entry_path!r} at revision {rev!r}, whose "
                        "historical content has no `kind:` field at all -- "
                        "it cannot be confirmed to actually be a 'claim'-kind "
                        "record",
                    )
                )
            elif real_assertion_kind != "claim":
                findings.append(
                    Finding(
                        "knowledge-base-snapshot-kind-mismatch",
                        f"{rel}: assertions[{assertion_id!r}] must cite a "
                        f"'claim'-kind record, but {entry_path!r}@{rev!r} is "
                        f"kind={real_assertion_kind!r}",
                    )
                )
            for sub_kind in _SNAPSHOT_CLOSURE_SUB_KINDS:
                cited_ids = set(_extract_id_strings(historical_fields.get(sub_kind, "")))
                sub_table = assertion.get(sub_kind, {})
                if sub_kind not in assertion:
                    sub_table = {}
                elif not isinstance(sub_table, dict):
                    findings.append(
                        Finding(
                            "knowledge-base-snapshot-malformed-structure",
                            f"{rel}: assertions[{assertion_id!r}].{sub_kind} "
                            f"must be a table, got {type(sub_table).__name__}",
                        )
                    )
                    sub_table = {}
                valid_ids, nested_findings = _validate_nested_entries(
                    root, rel, assertion_id, sub_kind, sub_table
                )
                findings.extend(nested_findings)
                for missing_id in sorted(cited_ids - valid_ids):
                    findings.append(
                        Finding(
                            "knowledge-base-snapshot-incomplete-closure",
                            f"{rel}: assertions[{assertion_id!r}]'s real "
                            f"historical record cites {missing_id!r} in its "
                            f"own {sub_kind}, but this snapshot has no "
                            f"corresponding, validly-identified "
                            f"assertions[{assertion_id!r}].{sub_kind}[{missing_id!r}] "
                            "entry -- incomplete Evidence/Derivation closure",
                        )
                    )

            derivation_id = historical_fields.get("derivation")
            if derivation_id:
                derivation_table = assertion.get("derivation", {})
                if "derivation" not in assertion:
                    derivation_table = {}
                elif not isinstance(derivation_table, dict):
                    findings.append(
                        Finding(
                            "knowledge-base-snapshot-malformed-structure",
                            f"{rel}: assertions[{assertion_id!r}].derivation "
                            f"must be a table, got "
                            f"{type(derivation_table).__name__}",
                        )
                    )
                    derivation_table = {}
                valid_derivation_ids, derivation_findings = _validate_nested_entries(
                    root, rel, assertion_id, "derivation", derivation_table
                )
                findings.extend(derivation_findings)
                if derivation_id not in valid_derivation_ids:
                    findings.append(
                        Finding(
                            "knowledge-base-snapshot-incomplete-closure",
                            f"{rel}: assertions[{assertion_id!r}]'s real "
                            f"historical record cites derivation "
                            f"{derivation_id!r}, but this snapshot has no "
                            f"corresponding, validly-identified "
                            f"assertions[{assertion_id!r}].derivation[{derivation_id!r}] "
                            "entry -- incomplete Evidence/Derivation closure",
                        )
                    )
    return findings


def check_snapshot_historical_integrity(
    feature_dir: Path, root: Path = ROOT
) -> list[Finding]:
    """Phase 79 (§5.3, check 1 of 3 -- corruption). For every assertion
    (and its evidence/derivation) a snapshot cites, the exact historical
    git blob at its own recorded `repository_revision` must still hash to
    the value the snapshot itself recorded. This should always pass in
    normal operation: a legitimate supersession or withdrawal only ever
    edits the *current* file, never the historical git blob at an
    already-committed revision. A mismatch means either the snapshot's
    own sidecar was hand-edited after the fact, or git history itself was
    rewritten since that revision -- a genuine, serious finding, never
    triggered by routine record lifecycle transitions. `root` defaults to
    the real repository but is threaded through explicitly so tests can
    point this at a disposable git fixture."""
    findings: list[Finding] = []
    for snapshot_path in _iter_snapshot_files(feature_dir):
        try:
            snapshot = tomllib.loads(snapshot_path.read_text(encoding="utf-8"))
        except tomllib.TOMLDecodeError as exc:
            findings.append(
                Finding(
                    "knowledge-base-snapshot-unparseable",
                    f"{snapshot_path.relative_to(root)}: not valid TOML: {exc}",
                )
            )
            continue
        for label, entry in _iter_snapshot_entries(snapshot):
            rev = entry.get("repository_revision")
            path = entry.get("path")
            expected_hash = entry.get("content_hash")
            if not (rev and path and expected_hash):
                findings.append(
                    Finding(
                        "knowledge-base-snapshot-incomplete-entry",
                        f"{snapshot_path.relative_to(root)}: entry {label!r} "
                        "is missing repository_revision/path/content_hash",
                    )
                )
                continue
            content = _git_show_content(root, rev, path)
            if content is None:
                findings.append(
                    Finding(
                        "knowledge-base-snapshot-unresolvable-revision",
                        f"{snapshot_path.relative_to(root)}: entry {label!r} "
                        f"cites {path!r} at revision {rev!r}, which `git "
                        "show` could not resolve (shallow clone, or the "
                        "path did not exist at that revision)",
                    )
                )
                continue
            actual_hash = _sha256(content)
            if actual_hash != expected_hash:
                findings.append(
                    Finding(
                        "knowledge-base-snapshot-tampering",
                        f"{snapshot_path.relative_to(root)}: entry {label!r}'s "
                        f"historical content at {path!r}@{rev!r} hashes to "
                        f"{actual_hash!r}, not the recorded {expected_hash!r} "
                        "-- this should never happen from a legitimate "
                        "supersession (which only ever edits the *current* "
                        "file, never a historical git blob); it means "
                        "either the snapshot's own sidecar was hand-edited, "
                        "or git history was rewritten since that revision",
                    )
                )
    return findings


def check_snapshot_current_divergence(
    feature_dir: Path, root: Path = ROOT
) -> list[Finding]:
    """Phase 79 (§5.3, check 2 of 3 -- informational). Compare a
    snapshot's own historical, revision-pinned content against the
    *current*, live file at the same path. A difference here is expected
    and healthy over time (the assertion may have been legitimately
    superseded or withdrawn, moving its own `status` field) -- this is
    the mechanical hook propagation (§10.2) uses to flag a snapshot-level
    citation as `needs reassessment`, and is never `--strict`-blocking in
    its own right (`strict=False` on every finding here). `root` defaults
    to the real repository but is threaded through explicitly so tests
    can point this at a disposable git fixture."""
    findings: list[Finding] = []
    for snapshot_path in _iter_snapshot_files(feature_dir):
        try:
            snapshot = tomllib.loads(snapshot_path.read_text(encoding="utf-8"))
        except tomllib.TOMLDecodeError:
            continue  # already reported by check_snapshot_historical_integrity
        for label, entry in _iter_snapshot_entries(snapshot):
            rev = entry.get("repository_revision")
            path = entry.get("path")
            if not (rev and path):
                continue  # already reported as incomplete
            historical = _git_show_content(root, rev, path)
            if historical is None:
                continue  # already reported as unresolvable
            current_file = root / path
            if not current_file.is_file():
                findings.append(
                    Finding(
                        "knowledge-base-snapshot-current-divergence",
                        f"{snapshot_path.relative_to(root)}: entry {label!r}'s "
                        f"current file {path!r} no longer exists -- the "
                        "record this snapshot cites may have been moved, "
                        "renamed, or removed since freeze time",
                        strict=False,
                    )
                )
                continue
            current = current_file.read_text(encoding="utf-8")
            if current == historical:
                continue
            current_fields = parse_record(current_file)
            historical_status_match = re.search(
                r"^status:\s*(.*)$", historical, re.MULTILINE
            )
            historical_status = (
                _strip_inline_comment(historical_status_match.group(1))
                if historical_status_match
                else None
            )
            findings.append(
                Finding(
                    "knowledge-base-snapshot-current-divergence",
                    f"{snapshot_path.relative_to(root)}: entry {label!r}'s "
                    f"current content at {path!r} differs from what "
                    f"snapshot {snapshot.get('snapshot_id')!r} recorded "
                    f"(current status={current_fields.get('status')!r}, "
                    f"historical status={historical_status!r}) -- expected "
                    "and healthy if this is a legitimate supersession/"
                    "withdrawal; worth investigating (a fresh "
                    "context-researcher pass) if the underlying evidence "
                    "itself changed, not just the lifecycle status",
                    strict=False,
                )
            )
    return findings


CHECKS = [
    check_required_fields,
    check_status_enums,
    check_optional_enum_fields,
    check_list_fields_are_inline,
    check_cross_references_resolve,
    check_supersedes_never_crosses_kind,
    check_requirement_cites_approved_decision,
    check_anchor_integrity,
    check_design_doc_citations_resolve,
    check_snapshot_completeness,
    check_snapshot_historical_integrity,
    check_snapshot_current_divergence,
]


def run_all(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    knowledge_dir = root / "planning" / "knowledge"
    if not knowledge_dir.is_dir():
        return findings
    feature_dirs = sorted(p for p in knowledge_dir.iterdir() if p.is_dir())
    all_known_ids: set[str] = set()
    all_decision_status: dict[str, str] = {}
    for feature_dir in feature_dirs:
        for yaml_path in feature_dir.glob("*.yaml"):
            fields = parse_record(yaml_path)
            record_id = fields.get("id")
            if record_id:
                all_known_ids.add(record_id)
                if fields.get("kind") == "decision":
                    all_decision_status[record_id] = fields.get("status", "")
    for feature_dir in feature_dirs:
        for check in CHECKS:
            if check is check_cross_references_resolve:
                findings.extend(check(feature_dir, all_known_ids))
            elif check is check_requirement_cites_approved_decision:
                findings.extend(check(feature_dir, all_decision_status, root))
            elif check in (
                check_optional_enum_fields,
                check_list_fields_are_inline,
                check_anchor_integrity,
                check_snapshot_completeness,
                check_snapshot_historical_integrity,
                check_snapshot_current_divergence,
            ):
                findings.extend(check(feature_dir, root))
            else:
                findings.extend(check(feature_dir))
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--strict",
        action="store_true",
        help="exit 1 if any finding is reported (default: always exit 0)",
    )
    args = parser.parse_args()

    findings = run_all(ROOT)
    blocking = [f for f in findings if f.strict]

    if not findings:
        print("check_knowledge_base: no findings")
    else:
        print(f"check_knowledge_base: {len(findings)} finding(s)")
        for f in findings:
            tag = "" if f.strict else " (info)"
            print(f"  [{f.rule}]{tag} {f.message}")

    return 1 if (args.strict and blocking) else 0


if __name__ == "__main__":
    sys.exit(main())
