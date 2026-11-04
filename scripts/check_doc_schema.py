"""Phase 87 documentation-schema validator (`decisions/0085` §5; see
planning/phase-87-documentation-schema-knowledge-compiled-documentation.md
§B). Mirrors `scripts/check_contracts.py`'s own `Finding`/`--strict`
convention exactly.

    python scripts/check_doc_schema.py [--strict] [--files PATH [PATH ...]]

Report-only by default (always exits 0). `--strict` exits 1 if any
*blocking* finding is reported. `--files` requires at least one path
(`nargs="+"`, never `"*"` -- an explicit, empty `--files` selection is a
usage error, not a silently-clean zero-schema scan, matching Phase 86's
own corrected convention); omitting it entirely scans every
`*.schema.yaml` file under the repository.

One side effect, and only one: a `discover:<query>` `required_knowledge`
entry that resolves to exactly one real record is rewritten in place to
that concrete record id (idempotent -- a second run sees only concrete
ids and makes no further change). No other field is ever modified.

Not a `codecompass` subcommand -- checks CodeCompass's own planning
artefacts, like `check_contracts.py`/`check_knowledge_base.py`.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from codecompass import doc_compiler as dc  # noqa: E402
from codecompass import knowledge_api as ka  # noqa: E402

_VALID_MIN_CLAIM_STATUS = {"candidate", "supported", "verified"}
_VALID_DEPTH = {"brief", "standard", "detailed"}
_VALID_TONE = {"instructional", "reference", "narrative"}
_VALID_COMPARISON_MODE = {"exact", "normalized_whitespace", "regex"}
_VALID_CITATION_DISPLAY = {"inline", "none"}
_SUPPORTED_SCHEMA_VERSIONS = {1}

# Stage 87A's own minimal schema (plan §B) -- requires_tested_example/
# example_comparison_mode (needs the 87B execution harness) and
# verification_method/full acceptance_criteria richness (87C) are
# deliberately NOT required here; `_check_section_fields` below still
# validates them *if present*, so this script stays forward-compatible
# with 87B/87C without needing to change again when those stages land.
_REQUIRED_TOP_FIELDS = (
    "schema_version", "document", "audience", "sections",
    "acceptance_criteria", "owner",
)
_REQUIRED_SECTION_FIELDS = (
    "id", "required_knowledge", "max_evidence_chars",
)
# Amendment finding A (restructuring pass, §G.A): a section id composes
# into a `codecompass-grounded-by region:<id>` token, whose own real
# parser (`knowledge_intermediate._REGION_ID_RE`) accepts only
# `[A-Za-z0-9_-]+` -- lowercase-hyphenated here specifically, matching
# the schema's own id convention, never a dot (which silently truncates
# at the parser, confirmed by direct execution).
_SECTION_ID_RE = re.compile(r"^[a-z0-9-]+$")


@dataclass
class Finding:
    rule: str
    message: str
    strict: bool = True


def _check_top_level_fields(data: dict, schema_path: Path) -> list[Finding]:
    findings = []
    for field_name in _REQUIRED_TOP_FIELDS:
        if field_name not in data:
            findings.append(Finding(
                "doc-schema-missing-field",
                f"{schema_path}: missing required top-level field {field_name!r}",
            ))
    return findings


def _check_schema_version(data: dict, schema_path: Path) -> list[Finding]:
    version = data.get("schema_version")
    if version not in _SUPPORTED_SCHEMA_VERSIONS:
        return [Finding(
            "doc-schema-unknown-version",
            f"{schema_path}: schema_version {version!r} is not one of the "
            f"versions this validator supports ({sorted(_SUPPORTED_SCHEMA_VERSIONS)}) "
            "-- fail closed rather than guess at a forward-compatible interpretation",
        )]
    return []


def _check_section_fields(section: dict, schema_path: Path) -> list[Finding]:
    findings = []
    section_id = section.get("id", "<missing id>")
    for field_name in _REQUIRED_SECTION_FIELDS:
        if field_name not in section:
            findings.append(Finding(
                "doc-schema-missing-field",
                f"{schema_path}: section {section_id!r} missing required field {field_name!r}",
            ))
    if section_id != "<missing id>" and not _SECTION_ID_RE.match(section_id):
        findings.append(Finding(
            "doc-schema-invalid-section-id",
            f"{schema_path}: section id {section_id!r} must match "
            f"{_SECTION_ID_RE.pattern!r} (lowercase, hyphen-separated) -- a dot or "
            "any other separator silently truncates at the real region-id parser",
        ))
    depth = section.get("depth")
    if depth is not None and depth not in _VALID_DEPTH:
        findings.append(Finding(
            "doc-schema-invalid-depth",
            f"{schema_path}: section {section_id!r} has invalid depth {depth!r}",
        ))
    tone = section.get("tone")
    if tone is not None and tone not in _VALID_TONE:
        findings.append(Finding(
            "doc-schema-invalid-tone",
            f"{schema_path}: section {section_id!r} has invalid tone {tone!r}",
        ))
    # Flat per-section field (restructuring-pass correction) -- never
    # nested under an `evidence_requirements` dict.
    min_status = section.get("min_claim_status")
    if min_status is not None and min_status not in _VALID_MIN_CLAIM_STATUS:
        findings.append(Finding(
            "doc-schema-invalid-min-claim-status",
            f"{schema_path}: section {section_id!r} has invalid "
            f"min_claim_status {min_status!r}",
        ))
    citation_display = section.get("citation_display")
    if citation_display is not None and citation_display not in _VALID_CITATION_DISPLAY:
        findings.append(Finding(
            "doc-schema-invalid-citation-display",
            f"{schema_path}: section {section_id!r} has invalid "
            f"citation_display {citation_display!r}",
        ))
    if section.get("requires_tested_example"):
        mode = section.get("example_comparison_mode")
        if mode is None:
            findings.append(Finding(
                "doc-schema-missing-comparison-mode",
                f"{schema_path}: section {section_id!r} has requires_tested_example: true "
                "but no example_comparison_mode -- how real vs. expected output is "
                "compared must be declared at schema-authoring time, never invented post-hoc",
            ))
        elif mode not in _VALID_COMPARISON_MODE:
            findings.append(Finding(
                "doc-schema-invalid-comparison-mode",
                f"{schema_path}: section {section_id!r} has invalid "
                f"example_comparison_mode {mode!r}",
            ))
    return findings


def _resolve_required_knowledge(
    project_root: Path, data: dict, schema_path: Path
) -> list[Finding]:
    """Amendment finding A: every `required_knowledge` entry is resolved
    to a concrete record id here, at validation time -- never at compile
    time, and never by the compiler's own `search()` fallback. A
    `discover:<query>` entry must resolve to EXACTLY one record; zero or
    more than one is blocking, never a silent `results[0]` guess. A
    concrete id must resolve via `knowledge_api.get()`."""
    findings: list[Finding] = []
    rewritten = False
    for section in data.get("sections", []):
        section_id = section.get("id", "<missing id>")
        entries = section.get("required_knowledge", [])
        resolved_entries = []
        for entry in entries:
            if isinstance(entry, str) and entry.startswith("discover:"):
                query = entry[len("discover:"):]
                response = ka.search(project_root, query)
                if response.status != "result":
                    findings.append(Finding(
                        "doc-schema-ambiguous-discover-query",
                        f"{schema_path}: section {section_id!r}'s discover query "
                        f"{query!r} resolved to zero records",
                    ))
                    resolved_entries.append(entry)
                elif len(response.results) != 1:
                    ids = [r.id for r in response.results]
                    findings.append(Finding(
                        "doc-schema-ambiguous-discover-query",
                        f"{schema_path}: section {section_id!r}'s discover query "
                        f"{query!r} resolved to {len(ids)} records ({ids}) -- "
                        "ambiguous; narrow the query or name an explicit record id, "
                        "never guessed via the first match",
                    ))
                    resolved_entries.append(entry)
                else:
                    resolved_entries.append(response.results[0].id)
                    rewritten = True
            else:
                response = ka.get(project_root, entry)
                if response.status != "result" or not response.results:
                    findings.append(Finding(
                        "doc-schema-unresolved-record-id",
                        f"{schema_path}: section {section_id!r} requires {entry!r}, "
                        "which does not resolve via knowledge_api.get()",
                    ))
                resolved_entries.append(entry)
        section["required_knowledge"] = resolved_entries

    if rewritten and not findings:
        schema_path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")

    return findings


def _check_document_path(project_root: Path, data: dict, schema_path: Path) -> list[Finding]:
    """Hardening pass §N.B: the same `resolve_publication_target`
    policy `docs publish` enforces at write time is also enforced here,
    at schema-validation time -- so an unsafe `document` field is
    caught as soon as the schema is authored, never only when a
    publish is attempted."""
    document = data.get("document")
    if document is None:
        return []
    try:
        dc.resolve_publication_target(project_root, document)
    except dc.DocCompilerError as exc:
        return [Finding("doc-schema-unsafe-document-path", f"{schema_path}: {exc}")]
    return []


def _check_document_uniqueness(all_data: list[tuple[Path, dict]]) -> list[Finding]:
    findings = []
    seen: dict[str, Path] = {}
    for schema_path, data in all_data:
        document = data.get("document")
        if document is None:
            continue
        if document in seen and seen[document] != schema_path:
            findings.append(Finding(
                "doc-schema-duplicate-document-path",
                f"{schema_path} and {seen[document]} both govern document {document!r} "
                "-- two schemas may never govern the same file",
            ))
        else:
            seen[document] = schema_path
    return findings


def run_all(project_root: Path, schema_paths: list[Path]) -> list[Finding]:
    findings: list[Finding] = []
    all_data: list[tuple[Path, dict]] = []

    for schema_path in schema_paths:
        try:
            data = yaml.safe_load(schema_path.read_text(encoding="utf-8"))
        except (OSError, yaml.YAMLError) as exc:
            findings.append(Finding(
                "doc-schema-unparseable",
                f"{schema_path}: could not be parsed as YAML: {exc}",
            ))
            continue
        if not isinstance(data, dict):
            findings.append(Finding(
                "doc-schema-unparseable",
                f"{schema_path}: top-level content is not a YAML mapping",
            ))
            continue
        all_data.append((schema_path, data))

    for schema_path, data in all_data:
        findings.extend(_check_top_level_fields(data, schema_path))
        findings.extend(_check_schema_version(data, schema_path))
        findings.extend(_check_document_path(project_root, data, schema_path))
        for section in data.get("sections", []) or []:
            findings.extend(_check_section_fields(section, schema_path))
        findings.extend(_resolve_required_knowledge(project_root, data, schema_path))

    findings.extend(_check_document_uniqueness(all_data))
    return findings


def _discover_schema_files(project_root: Path) -> list[Path]:
    return sorted(project_root.glob("**/*.schema.yaml"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strict", action="store_true")
    parser.add_argument(
        "--files", nargs="+", type=Path, default=None,
        help="Explicit schema file(s) to check (at least one required if given); "
             "omit entirely to scan every *.schema.yaml file under the repository",
    )
    args = parser.parse_args(argv)

    schema_paths = args.files if args.files is not None else _discover_schema_files(ROOT)
    findings = run_all(ROOT, schema_paths)
    blocking = [f for f in findings if f.strict]

    if not findings:
        print("check_doc_schema: no findings")
    else:
        print(f"check_doc_schema: {len(findings)} finding(s)")
        for f in findings:
            tag = "" if f.strict else " (info)"
            print(f"  [{f.rule}]{tag} {f.message}")

    return 1 if (args.strict and blocking) else 0


if __name__ == "__main__":
    sys.exit(main())
