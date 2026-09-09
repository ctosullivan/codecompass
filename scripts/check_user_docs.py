"""Maintainer-only smoke check: does this repo's own user-facing docs match
its own code? Mechanical only — no edits, no AI calls. See
planning/phase-36-docs-sync-tooling.md and .claude/skills/docs-sync/SKILL.md.

Not part of the codecompass package: this checks codecompass's own repo,
not a consuming project's docs. Not shipped, not a `codecompass` subcommand.

    python scripts/check_user_docs.py [--strict]

Report-only by default (always exits 0). `--strict` exits 1 if any
*blocking* finding is reported (findings tagged `(info)` never fail
`--strict` — they just prompt a decision). For optional local/pre-commit
use.

Covers, as of Phase 41: CLI command coverage, README phase-count
consistency, `ANTHROPIC_API_KEY` mention, `VendorConfig` field coverage,
`ai-docs/` presence, project-learning candidate provenance +
promoted-log consistency, and per-phase retro presence
(`planning/retros/`).
"""

from __future__ import annotations

import argparse
import ast
import re
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


@dataclass
class Finding:
    rule: str
    message: str
    strict: bool = True  # False = informational, never fails --strict


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def check_cli_commands_documented(root: Path) -> list[Finding]:
    """Every @app.command()/@query_app.command() name in cli.py has a
    matching mention in docs/cli-reference.md."""
    cli_path = root / "src" / "codecompass" / "cli.py"
    doc_path = root / "docs" / "cli-reference.md"
    tree = ast.parse(_read(cli_path), filename=str(cli_path))
    doc_text = _read(doc_path)

    findings: list[Finding] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef):
            continue
        for dec in node.decorator_list:
            if not isinstance(dec, ast.Call):
                continue
            func = dec.func
            attr_chain = None
            if isinstance(func, ast.Attribute):
                attr_chain = (
                    func.value.id if isinstance(func.value, ast.Name) else None,
                    func.attr,
                )
            if attr_chain is None or attr_chain[1] != "command":
                continue
            base = attr_chain[0]
            if base not in ("app", "query_app"):
                continue
            if dec.args and isinstance(dec.args[0], ast.Constant):
                name = str(dec.args[0].value)
            else:
                name = node.name.replace("_", "-")
            needle = f"codecompass {name}" if base == "app" else f"query {name}"
            if needle not in doc_text:
                findings.append(
                    Finding(
                        "cli_commands_documented",
                        f"'{needle}' (from cli.py's @{base}.command on "
                        f"{node.name!r}) not found in docs/cli-reference.md",
                    )
                )
    return findings


def check_readme_phase_count(root: Path) -> list[Finding]:
    """README's Status-line phase-count claim matches the highest phase
    number marked `done` in planning/ROADMAP.md's *foundation* tables.

    The README's "phases 0-N" claim describes the foundation (the
    npm/PyPI/Cargo package/source tool, MVP v0.1/v0.2 + Post-MVP). The
    "Redefined CodeCompass v1 — Stages A–F" phases (39+) are a separate
    process/validation milestone group (decisions/0048) whose completion
    does not change what "phases 0-N" means to a prospective user, so
    ROADMAP content from that heading onward is excluded from this check.
    """
    readme_text = _read(root / "README.md")
    roadmap_text = _read(root / "planning" / "ROADMAP.md")

    # Exclude the redefined-v1 milestone-group section from the scan.
    _redef_heading = re.search(
        r"^##\s+Redefined CodeCompass v1", roadmap_text, re.MULTILINE
    )
    if _redef_heading:
        roadmap_text = roadmap_text[: _redef_heading.start()]

    readme_match = re.search(r"phases 0-(\d+)", readme_text, re.IGNORECASE)
    if not readme_match:
        return [
            Finding(
                "readme_phase_count",
                "README.md's Status section has no 'phases 0-N' claim to check",
            )
        ]
    readme_n = int(readme_match.group(1))

    done_numbers: list[int] = []
    for line in roadmap_text.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 3 or not cells[0].isdigit():
            continue
        if "done" in cells:
            done_numbers.append(int(cells[0]))
    if not done_numbers:
        return [Finding("readme_phase_count", "no `done` phase rows found in ROADMAP.md")]
    highest_done = max(done_numbers)

    if readme_n != highest_done:
        return [
            Finding(
                "readme_phase_count",
                f"README.md claims 'phases 0-{readme_n}' but the highest "
                f"`done` phase in planning/ROADMAP.md is {highest_done}",
            )
        ]
    return []


def check_api_key_documented(root: Path) -> list[Finding]:
    """README.md mentions ANTHROPIC_API_KEY somewhere."""
    readme_text = _read(root / "README.md")
    if "ANTHROPIC_API_KEY" not in readme_text:
        return [
            Finding(
                "api_key_documented",
                "README.md never mentions ANTHROPIC_API_KEY",
            )
        ]
    return []


def check_vendor_config_fields_documented(root: Path) -> list[Finding]:
    """Every VendorConfig field is mentioned in docs/config-schema.md."""
    core_path = root / "src" / "codecompass" / "core.py"
    doc_path = root / "docs" / "config-schema.md"
    tree = ast.parse(_read(core_path), filename=str(core_path))
    doc_text = _read(doc_path)

    findings: list[Finding] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "VendorConfig":
            for stmt in node.body:
                if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
                    field_name = stmt.target.id
                    if f"`{field_name}`" not in doc_text:
                        findings.append(
                            Finding(
                                "vendor_config_fields_documented",
                                f"VendorConfig field '{field_name}' not mentioned "
                                "in docs/config-schema.md",
                            )
                        )
    return findings


def check_ai_docs_present(root: Path) -> list[Finding]:
    """Every file directly under ai-docs/ exists and is non-empty."""
    ai_docs_dir = root / "ai-docs"
    if not ai_docs_dir.is_dir():
        return [Finding("ai_docs_present", "ai-docs/ directory does not exist")]

    findings: list[Finding] = []
    files = [p for p in ai_docs_dir.iterdir() if p.is_file()]
    if not files:
        findings.append(Finding("ai_docs_present", "ai-docs/ exists but contains no files"))
    for path in files:
        if path.stat().st_size == 0:
            findings.append(Finding("ai_docs_present", f"ai-docs/{path.name} is empty"))
    return findings


_LEARNING_REQUIRED_FIELDS = (
    "origin",
    "date",
    "project_revision",
    "observation",
    "evidence",
    "classification",
    "status",
)


def _iter_learning_candidates(root: Path):
    """Yield (id, body_text) for every candidate in planning/learnings/inbox.md
    and planning/learnings/candidates/*.md. A candidate block starts at a
    `### L-NNN` heading and runs to the next `### ` heading or EOF."""
    learn_dir = root / "planning" / "learnings"
    texts: list[str] = []
    inbox = learn_dir / "inbox.md"
    if inbox.is_file():
        texts.append(_read(inbox))
    cand_dir = learn_dir / "candidates"
    if cand_dir.is_dir():
        for p in sorted(cand_dir.glob("*.md")):
            texts.append(_read(p))

    for text in texts:
        blocks = re.split(r"(?m)^###\s+", text)
        for block in blocks[1:]:
            m = re.match(r"(L-\d+)", block.strip())
            if not m:
                continue
            yield m.group(1), block


def check_learnings_candidate_fields(root: Path) -> list[Finding]:
    """Every candidate learning carries all required provenance fields
    (planning/v1-redefinition/learning-lifecycle.md §3)."""
    findings: list[Finding] = []
    for cand_id, body in _iter_learning_candidates(root):
        low = body.lower()
        missing = [
            f for f in _LEARNING_REQUIRED_FIELDS if f"**{f}:**" not in low
        ]
        if missing:
            findings.append(
                Finding(
                    "learnings_candidate_fields",
                    f"candidate {cand_id} is missing field(s): {', '.join(missing)}",
                )
            )
    return findings


def check_promoted_learnings_logged(root: Path) -> list[Finding]:
    """Every candidate with `status: promoted` has a matching pointer line
    in planning/learnings/promoted.md."""
    promoted_path = root / "planning" / "learnings" / "promoted.md"
    promoted_text = _read(promoted_path) if promoted_path.is_file() else ""
    findings: list[Finding] = []
    for cand_id, body in _iter_learning_candidates(root):
        status_match = re.search(r"\*\*status:\*\*\s*([a-z:_-]+)", body, re.IGNORECASE)
        status = status_match.group(1).lower() if status_match else ""
        if status == "promoted" and not re.search(
            rf"(?m)^{re.escape(cand_id)}\b", promoted_text
        ):
            findings.append(
                Finding(
                    "promoted_learnings_logged",
                    f"candidate {cand_id} is `status: promoted` but has no "
                    "pointer line in planning/learnings/promoted.md",
                )
            )
    return findings


def check_stale_evidence_gathering(root: Path) -> list[Finding]:
    """Informational: candidates sitting in `evidence-gathering` prompt a
    promote/discard decision (never fails --strict)."""
    findings: list[Finding] = []
    for cand_id, body in _iter_learning_candidates(root):
        status_match = re.search(r"\*\*status:\*\*\s*([a-z:_-]+)", body, re.IGNORECASE)
        status = status_match.group(1).lower() if status_match else ""
        if status == "evidence-gathering":
            findings.append(
                Finding(
                    "stale_evidence_gathering",
                    f"candidate {cand_id} is in `evidence-gathering` — the "
                    "knowledge-curator should decide promote/retain/discard",
                    strict=False,
                )
            )
    return findings


def check_phase_retros_present(root: Path) -> list[Finding]:
    """Every phase marked `done` in planning/ROADMAP.md with number >= 41
    (when the retro rule took effect) has a planning/retros/phase-N-*.md."""
    roadmap_text = _read(root / "planning" / "ROADMAP.md")
    retro_dir = root / "planning" / "retros"
    retro_nums = set()
    if retro_dir.is_dir():
        for p in retro_dir.glob("phase-*.md"):
            m = re.match(r"phase-(\d+)-", p.name)
            if m:
                retro_nums.add(int(m.group(1)))

    findings: list[Finding] = []
    for line in roadmap_text.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 3 or not cells[0].isdigit():
            continue
        num = int(cells[0])
        if num >= 41 and "done" in cells and num not in retro_nums:
            findings.append(
                Finding(
                    "phase_retros_present",
                    f"phase {num} is `done` in ROADMAP.md but has no "
                    f"planning/retros/phase-{num}-*.md retro",
                )
            )
    return findings


CHECKS = [
    check_cli_commands_documented,
    check_readme_phase_count,
    check_api_key_documented,
    check_vendor_config_fields_documented,
    check_ai_docs_present,
    check_learnings_candidate_fields,
    check_promoted_learnings_logged,
    check_stale_evidence_gathering,
    check_phase_retros_present,
]


def run_all(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    for check in CHECKS:
        findings.extend(check(root))
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
        print("check_user_docs: no findings")
    else:
        print(f"check_user_docs: {len(findings)} finding(s)")
        for f in findings:
            tag = "" if f.strict else " (info)"
            print(f"  [{f.rule}]{tag} {f.message}")

    return 1 if (args.strict and blocking) else 0


if __name__ == "__main__":
    sys.exit(main())
