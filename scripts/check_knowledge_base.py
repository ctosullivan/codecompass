"""Maintainer-only smoke check for Phase 54c's evidence/knowledge model
(planning/knowledge/<feature-slug>/*.yaml, design.md, context-packet.md).
Mechanical only — no edits, no AI calls, no YAML library dependency
(hand-rolled parsing sufficient for this flat, six-kind record shape,
same "avoid an unneeded dependency" posture
reference_pipeline.py::load_references_toml already established for a
comparably simple format). See
planning/phase-54c-evidence-knowledge-workflow.md §2/§9.

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
"""

from __future__ import annotations

import argparse
import re
import sys
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


def parse_record(path: Path) -> dict[str, str]:
    """Hand-rolled, deliberately minimal parse of one record YAML file:
    every top-level (column-0) `key: value` pair. Multi-line `>`/`|`
    block scalars are recognised (the key is present) but their
    continuation lines are not reconstructed — this checker only needs
    field *presence* and short scalar/list values (ids, statuses), never
    a record's own prose content.
    """
    fields: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line or line[0] in " \t#":
            continue
        match = re.match(r"^([a-zA-Z_][a-zA-Z0-9_]*):\s*(.*)$", line)
        if not match:
            continue
        key, value = match.group(1), _strip_inline_comment(match.group(2))
        fields[key] = value
    return fields


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


CHECKS = [
    check_required_fields,
    check_status_enums,
    check_cross_references_resolve,
    check_supersedes_never_crosses_kind,
    check_design_doc_citations_resolve,
]


def run_all(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    knowledge_dir = root / "planning" / "knowledge"
    if not knowledge_dir.is_dir():
        return findings
    feature_dirs = sorted(p for p in knowledge_dir.iterdir() if p.is_dir())
    all_known_ids: set[str] = set()
    for feature_dir in feature_dirs:
        for yaml_path in feature_dir.glob("*.yaml"):
            record_id = parse_record(yaml_path).get("id")
            if record_id:
                all_known_ids.add(record_id)
    for feature_dir in feature_dirs:
        for check in CHECKS:
            if check is check_cross_references_resolve:
                findings.extend(check(feature_dir, all_known_ids))
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
