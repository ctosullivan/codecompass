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

Covers, as of Phase 43b: CLI command coverage, README phase-count
consistency, `ANTHROPIC_API_KEY` mention, `VendorConfig` field coverage,
`ai-docs/` presence, project-learning candidate provenance +
promoted-log consistency, per-phase retro presence (`planning/retros/`),
internal-link resolution across hand-authored docs, fenced `codecompass`
example commands using real subcommands, ADR Status +
cross-reference integrity, retired names appearing as live prose
(the standing-content complement to the per-phase docs-drift audit), and
generated-artifact-vs-generator drift.
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


_CONTEXT_OBSERVATION_REQUIRED_FIELDS = (
    "origin",
    "date",
    "codecompass_revision",
    "project",
    "edge identity",
    "observation type",
    "edge correctness",
    "task usefulness",
    "status",
)


def _iter_context_observations(root: Path):
    """Yield (id, body_text) for every record in
    planning/context-observations/inbox.md. A record block starts at a
    `### OBS-NNN` heading and runs to the next `### ` heading or EOF —
    same shape as `_iter_learning_candidates`, one inbox file only (no
    `candidates/` subdir equivalent exists for this queue)."""
    inbox = root / "planning" / "context-observations" / "inbox.md"
    if not inbox.is_file():
        return
    text = _read(inbox)
    blocks = re.split(r"(?m)^###\s+", text)
    for block in blocks[1:]:
        m = re.match(r"(OBS-\d+)", block.strip())
        if not m:
            continue
        yield m.group(1), block


def check_context_observation_fields(root: Path) -> list[Finding]:
    """Every context-observation record carries all required provenance
    fields (planning/context-observations/TEMPLATE.md) — including the
    edge-correctness/task-usefulness split Phase 52 introduced
    specifically to stop those two questions being collapsed into one
    rating (see planning/context-observations/README.md)."""
    findings: list[Finding] = []
    for obs_id, body in _iter_context_observations(root):
        low = body.lower()
        missing = [
            f
            for f in _CONTEXT_OBSERVATION_REQUIRED_FIELDS
            if f"**{f}:**" not in low
        ]
        if missing:
            findings.append(
                Finding(
                    "context_observation_fields",
                    f"observation {obs_id} is missing field(s): {', '.join(missing)}",
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


# ── documentation-lifecycle checks (Phase 42) ──────────────────────────

_DOC_DIRS = ("docs", "ai-docs", "architecture", "examples")
_DOC_ROOT_FILES = ("README.md", "CONTRIBUTING.md")


def _iter_doc_files(root: Path):
    """Yield every hand-authored user-facing/contributor Markdown file."""
    for name in _DOC_ROOT_FILES:
        p = root / name
        if p.is_file():
            yield p
    for d in _DOC_DIRS:
        base = root / d
        if base.is_dir():
            yield from sorted(base.rglob("*.md"))


def _lines_with_fence_state(text: str):
    """Yield (lineno, line, in_fence, fence_lang) for each line, tracking
    ``` / ~~~ fenced code blocks."""
    fence: str | None = None
    lang = ""
    for i, line in enumerate(text.splitlines(), start=1):
        stripped = line.lstrip()
        m = re.match(r"(```+|~~~+)(.*)", stripped)
        if m and (fence is None or stripped.startswith(fence)):
            if fence is None:
                fence = m.group(1)
                lang = m.group(2).strip().lower()
                yield i, line, True, lang
                continue
            else:
                fence = None
                lang = ""
                yield i, line, True, ""
                continue
        yield i, line, fence is not None, lang


_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
_HEADING_RE = re.compile(r"^#{1,6}\s+(.*?)\s*#*\s*$")


def _slugify_heading(text: str) -> str:
    text = re.sub(r"`", "", text).strip().lower()
    text = re.sub(r"[^\w\s-]", "", text)
    return re.sub(r"[\s_]+", "-", text)


def _doc_anchor_slugs(text: str) -> set[str]:
    slugs: set[str] = set()
    for _lineno, line, in_fence, _lang in _lines_with_fence_state(text):
        if in_fence:
            continue
        m = _HEADING_RE.match(line)
        if m:
            slugs.add(_slugify_heading(m.group(1)))
    return slugs


def check_internal_links_resolve(root: Path) -> list[Finding]:
    """Every relative Markdown link in a hand-authored doc points at a
    file that exists; a `#fragment` (where present) matches a heading
    (informational)."""
    findings: list[Finding] = []
    for path in _iter_doc_files(root):
        text = _read(path)
        own_anchors = _doc_anchor_slugs(text)
        for lineno, line, in_fence, _lang in _lines_with_fence_state(text):
            if in_fence:
                continue
            for target in _LINK_RE.findall(line):
                target = target.split()[0].strip()  # drop optional "title"
                if re.match(r"^(https?:|mailto:|tel:)", target):
                    continue
                if target.startswith("#"):
                    if _slugify_heading(target[1:]) not in own_anchors:
                        findings.append(
                            Finding(
                                "internal_links_resolve",
                                f"{path.relative_to(root)}:{lineno} — anchor "
                                f"'{target}' has no matching heading",
                                strict=False,
                            )
                        )
                    continue
                file_part = target.split("#", 1)[0]
                if not file_part:
                    continue
                dest = (path.parent / file_part).resolve()
                if not dest.exists():
                    findings.append(
                        Finding(
                            "internal_links_resolve",
                            f"{path.relative_to(root)}:{lineno} — link target "
                            f"'{target}' does not exist",
                        )
                    )
                elif "#" in target and dest.is_file() and dest.suffix == ".md":
                    frag = target.split("#", 1)[1]
                    if frag and _slugify_heading(frag) not in _doc_anchor_slugs(
                        _read(dest)
                    ):
                        findings.append(
                            Finding(
                                "internal_links_resolve",
                                f"{path.relative_to(root)}:{lineno} — '{target}': "
                                f"no heading matching '#{frag}' in {dest.name}",
                                strict=False,
                            )
                        )
    return findings


def _codecompass_command_names(root: Path) -> tuple[set[str], set[str]]:
    """(top-level `codecompass` subcommands, `codecompass query` subcommands)
    parsed from cli.py's Typer decorators + `app.add_typer(name=...)`."""
    cli_path = root / "src" / "codecompass" / "cli.py"
    tree = ast.parse(_read(cli_path), filename=str(cli_path))
    app_cmds: set[str] = set()
    query_cmds: set[str] = set()
    for node in ast.walk(tree):
        # app.add_typer(sub_app, name="query")
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "add_typer"
        ):
            for kw in node.keywords:
                if kw.arg == "name" and isinstance(kw.value, ast.Constant):
                    app_cmds.add(str(kw.value.value))
        if not isinstance(node, ast.FunctionDef):
            continue
        for dec in node.decorator_list:
            if not isinstance(dec, ast.Call) or not isinstance(dec.func, ast.Attribute):
                continue
            if dec.func.attr != "command":
                continue
            base = dec.func.value.id if isinstance(dec.func.value, ast.Name) else None
            if dec.args and isinstance(dec.args[0], ast.Constant):
                name = str(dec.args[0].value)
            else:
                name = node.name.replace("_", "-")
            if base == "app":
                app_cmds.add(name)
            elif base == "query_app":
                query_cmds.add(name)
    return app_cmds, query_cmds


def check_fenced_codecompass_examples(root: Path) -> list[Finding]:
    """Fenced example lines invoking `codecompass` use a real subcommand."""
    app_cmds, query_cmds = _codecompass_command_names(root)
    findings: list[Finding] = []
    for path in _iter_doc_files(root):
        for lineno, line, in_fence, _lang in _lines_with_fence_state(_read(path)):
            if not in_fence:
                continue
            cmd = re.sub(r"^\$\s+", "", line.strip())
            if not (cmd == "codecompass" or cmd.startswith("codecompass ")):
                continue
            toks = cmd.split()[1:]
            # strip an inline "# comment"
            if "#" in toks:
                toks = toks[: toks.index("#")]
            if not toks or toks[0].startswith("-"):
                continue  # bare `codecompass` or only options — the app itself
            sub = toks[0]
            if sub not in app_cmds:
                findings.append(
                    Finding(
                        "fenced_codecompass_examples",
                        f"{path.relative_to(root)}:{lineno} — 'codecompass {sub}' "
                        f"is not a real subcommand ({sorted(app_cmds)})",
                    )
                )
                continue
            if sub == "query":
                q_args = [t for t in toks[1:] if not t.startswith("-")]
                if q_args and q_args[0] not in query_cmds:
                    findings.append(
                        Finding(
                            "fenced_codecompass_examples",
                            f"{path.relative_to(root)}:{lineno} — 'query {q_args[0]}' "
                            f"is not a real query subcommand ({sorted(query_cmds)})",
                        )
                    )
    return findings


def check_adr_status_and_supersedes(root: Path) -> list[Finding]:
    """Every ADR has a Status; every `decisions/NNNN` cross-reference in an
    ADR resolves to a real ADR file."""
    dec_dir = root / "decisions"
    if not dec_dir.is_dir():
        return []
    adrs = sorted(p for p in dec_dir.glob("*.md") if re.match(r"\d{4}-", p.name))
    numbers = {p.name[:4] for p in adrs}
    findings: list[Finding] = []
    for p in adrs:
        text = _read(p)
        head = "\n".join(text.splitlines()[:20]).lower()
        if "## status" not in head and "**status:**" not in head and "status:" not in head:
            findings.append(
                Finding("adr_status_and_supersedes", f"{p.name} has no Status line")
            )
        for ref in re.findall(r"decisions/(\d{4})\b", text):
            if ref not in numbers:
                findings.append(
                    Finding(
                        "adr_status_and_supersedes",
                        f"{p.name} references decisions/{ref} which does not exist",
                    )
                )
        for lineno, line in enumerate(text.splitlines(), start=1):
            if "supersed" not in line.lower():
                continue
            for ref in re.findall(r"`(\d{4})`", line):
                if ref not in numbers:
                    findings.append(
                        Finding(
                            "adr_status_and_supersedes",
                            f"{p.name}:{lineno} — supersede reference `{ref}` "
                            "resolves to no ADR file",
                        )
                    )
    return findings


# ── standing-drift checks (Phase 43b, GATE DA) ─────────────────────────

# Retired identifiers/config values, each *verified against src/* to no
# longer exist under this name. A retired name may still legitimately
# appear in current-truth docs as *history* ("X was removed in Phase N");
# this check only flags an occurrence with no historical marker nearby —
# i.e. one that reads as a live, present-tense fact. Each entry names the
# decision/phase that retired it, for the finding message.
_RETIRED_NAMES = (
    ("grounded_description", "module deleted, decisions/0031/0035 (Phase 16)"),
    ("Depth.FULL", "Depth enum deleted, decisions/0031"),
    ("depth = full", "VendorConfig.depth field deleted, decisions/0031/0035"),
    ('depth = "full"', "VendorConfig.depth field deleted, decisions/0031/0035"),
    ("_ESTIMATED_COST_PER_CALL_USD", "renamed to _ESTIMATED_COST_PER_BATCH_USD, Phase 15"),
    ("codecompass promote", "promote command removed, decisions/0033 (Phase 15)"),
)

# Substrings whose presence anywhere in the same *prose unit* (the whole
# wrapped bullet, or the whole blank-line-delimited paragraph — see
# `_iter_prose_units`) marks a retired-name mention as historical framing
# rather than a live claim. Deliberately generous — false negatives here
# (missing a genuinely stale claim) are recoverable at the next phase
# that touches the passage; false positives (flagging correct history)
# make the check noise that gets ignored. Calibrated against this repo's
# own architecture/overview.md, which narrates its implementation history
# extensively and correctly, at unit granularity, not a fixed line count.
_HISTORICAL_MARKERS = (
    "retired",
    "removed",
    "deleted",
    "no longer",
    "not longer",
    "used to",
    "former",
    "formerly",
    "renamed",
    "replaced",
    "now lives in",
    "moved to",
    "superseded",
    "the old",
    "extended from",
    "coexist through",
    "aren't retired until",
    "isn't retired until",
    "only deleted once",
    "carried over from the retired",
    "was removed",
    "were removed",
    "is gone",
)


def _iter_prose_units(text: str):
    """Yield (start_lineno, unit_text) blocks of hand-written prose: a
    top-level `- `/`* ` list item plus its wrapped continuation lines
    (this doc's lists have no blank line between items — a new bullet
    line starts a new unit), or otherwise a blank-line-delimited
    paragraph. Fenced code blocks and headings are unit boundaries, never
    unit content — a retired name inside a fence is a code example, not a
    prose claim, and this check only judges prose."""
    units: list[tuple[int, str]] = []
    current_lines: list[str] = []
    current_start: int | None = None

    def flush() -> None:
        nonlocal current_lines, current_start
        if current_lines:
            units.append((current_start, "\n".join(current_lines)))
        current_lines = []
        current_start = None

    for lineno, line, in_fence, _lang in _lines_with_fence_state(text):
        if in_fence:
            flush()
            continue
        stripped = line.strip()
        if not stripped or _HEADING_RE.match(line):
            flush()
            continue
        if re.match(r"^[-*]\s+", stripped):
            flush()
            current_start = lineno
            current_lines = [line]
        else:
            if current_start is None:
                current_start = lineno
            current_lines.append(line)
    flush()
    return units


def check_no_deleted_names_as_live(root: Path) -> list[Finding]:
    """A retired identifier/config value (`_RETIRED_NAMES`) appears in a
    current-truth doc's prose with no historical marker anywhere in the
    same unit (bullet or paragraph) — i.e. described as though it still
    exists. The standing-content complement to the per-phase
    `docs-reconstructor` drift audit (decisions/0050), which is
    diff-scoped and blind to pre-existing false-as-live prose no phase's
    diff touches (candidate learnings L-003 + L-004)."""
    findings: list[Finding] = []
    for path in _iter_doc_files(root):
        for start_lineno, unit in _iter_prose_units(_read(path)):
            unit_lower = unit.lower()
            has_marker = any(marker in unit_lower for marker in _HISTORICAL_MARKERS)
            if has_marker:
                continue
            for name, retired_note in _RETIRED_NAMES:
                if name.lower() not in unit_lower:
                    continue
                # Report the specific line the name occurs on, not just
                # the unit's start, for a click-to-line finding.
                offset = next(
                    i for i, ln in enumerate(unit.splitlines()) if name.lower() in ln.lower()
                )
                findings.append(
                    Finding(
                        "no_deleted_names_as_live",
                        f"{path.relative_to(root)}:{start_lineno + offset} — "
                        f"'{name}' appears with no historical marker anywhere "
                        f"in its bullet/paragraph ({retired_note}); reads as "
                        "live, not history",
                    )
                )
    return findings


def _load_codecompass_generators():
    """Import codecompass's deterministic (non-AI) generator functions for
    check_generated_artifacts_match_source. Returns None if the package
    isn't importable (informational finding, not a hard error — this repo
    normally has it installed editable, but a bare checkout shouldn't
    crash the whole script)."""
    src_path = ROOT / "src"
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    try:
        from codecompass import commands, config, skill

        return commands, config, skill
    except Exception:
        return None


def check_generated_artifacts_match_source(root: Path) -> list[Finding]:
    """Git-tracked but *generated* artifacts byte-match their generator's
    output against this repo's own real config/graph state — a hand edit,
    or a generator change without regeneration, drifts silently otherwise
    (candidate learning L-005: `docs-maintainer` once edited a generated
    file directly instead of fixing the generator).

    Deliberately narrow: only the two artifacts a bare function call can
    reproduce without a live sync. The root CLAUDE.md routing-table block
    and per-vendor `codecompass-*` Skills/`.mdc` files are regenerated
    from full graph/enrichment state this check doesn't reconstruct —
    out of scope here, covered by the per-phase docs-drift audit instead.

    `discovery.md` truly needs no graph state, but `render_tool_skill`'s
    output includes an enrichment count read from `context-graph.db`
    (candidate learning L-011) — on a checkout that has never run
    `codecompass sync` (a fresh clone, this script's own test suite run
    cold), that db doesn't exist and the count degrades to zero, so a
    byte-for-byte comparison against a SKILL.md committed from a
    machine that *had* synced would false-positive as drift. When the db
    is missing, that one comparison is skipped (informational, not
    strict) rather than trusted.
    """
    generators = _load_codecompass_generators()
    if generators is None:
        return [
            Finding(
                "generated_artifacts_match_source",
                "could not import codecompass (src/ not importable) — "
                "skipped the generated-artifact comparison",
                strict=False,
            )
        ]
    commands, config, skill = generators
    findings: list[Finding] = []

    tool_skill_path = root / ".claude" / "skills" / "codecompass" / "SKILL.md"
    vendor_toml = root / "vendor.toml"
    if tool_skill_path.is_file() and vendor_toml.is_file():
        if not (root / "context-graph.db").is_file():
            findings.append(
                Finding(
                    "generated_artifacts_match_source",
                    "context-graph.db not present — skipped comparing "
                    ".claude/skills/codecompass/SKILL.md against "
                    "skill.render_tool_skill(...) (its enrichment count "
                    "depends on graph state this checkout doesn't have; "
                    "run `codecompass sync` first to check it for real)",
                    strict=False,
                )
            )
        else:
            try:
                configs = config.load_vendor_config(vendor_toml)
                expected = skill.render_tool_skill(configs, root)
            except Exception as exc:
                findings.append(
                    Finding(
                        "generated_artifacts_match_source",
                        f"could not render the tool Skill to compare: {exc}",
                        strict=False,
                    )
                )
            else:
                if _read(tool_skill_path) != expected:
                    findings.append(
                        Finding(
                            "generated_artifacts_match_source",
                            ".claude/skills/codecompass/SKILL.md does not match "
                            "skill.render_tool_skill(...) — regenerate via "
                            "`codecompass index`/`sync` rather than hand-editing",
                        )
                    )

    discovery_path = root / ".claude" / "commands" / "discovery.md"
    if discovery_path.is_file():
        if _read(discovery_path) != commands.render_discovery_command():
            findings.append(
                Finding(
                    "generated_artifacts_match_source",
                    ".claude/commands/discovery.md does not match "
                    "commands.render_discovery_command() — regenerate "
                    "rather than hand-editing",
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
    check_context_observation_fields,
    check_stale_evidence_gathering,
    check_phase_retros_present,
    check_internal_links_resolve,
    check_fenced_codecompass_examples,
    check_adr_status_and_supersedes,
    check_no_deleted_names_as_live,
    check_generated_artifacts_match_source,
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
