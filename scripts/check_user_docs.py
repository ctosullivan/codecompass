"""Maintainer-only smoke check: does this repo's own user-facing docs match
its own code? Mechanical only — no edits, no AI calls. See
planning/phase-36-docs-sync-tooling.md and .claude/skills/docs-sync/SKILL.md.

Not part of the codecompass package: this checks codecompass's own repo,
not a consuming project's docs. Not shipped, not a `codecompass` subcommand.

    python scripts/check_user_docs.py [--strict]

Report-only by default (always exits 0). `--strict` exits 1 if any rule
below finds a problem, for optional local/pre-commit use.
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
    number marked `done` anywhere in planning/ROADMAP.md."""
    readme_text = _read(root / "README.md")
    roadmap_text = _read(root / "planning" / "ROADMAP.md")

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


CHECKS = [
    check_cli_commands_documented,
    check_readme_phase_count,
    check_api_key_documented,
    check_vendor_config_fields_documented,
    check_ai_docs_present,
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

    if not findings:
        print("check_user_docs: no findings")
    else:
        print(f"check_user_docs: {len(findings)} finding(s)")
        for f in findings:
            print(f"  [{f.rule}] {f.message}")

    return 1 if (args.strict and findings) else 0


if __name__ == "__main__":
    sys.exit(main())
