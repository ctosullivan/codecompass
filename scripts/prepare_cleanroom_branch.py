#!/usr/bin/env python3
"""Phase 81B (`planning/phase-81b-clean-room-redocumentation.md` §6.1/
§6.1.1/§22 item 4): build and validate a clean-room handoff tree for
CodeCompass, under an explicit, named allowlist — never an ambiguous
"handoff filesystem".

Two sub-commands:

    build      Copy the real, current allowlisted tree plus the handoff
               package (planning/documentation-handoff/) into a staging
               directory, write CLEANROOM-MANIFEST.yaml/
               CLEANROOM-INSTRUCTIONS.md/DOCUMENTATION-TARGET.md at its
               root.
    validate   Confirm a built staging directory's own tree matches its
               own manifest exactly: every included_path present, every
               intermediary_projection_hash matching a fresh re-hash, no
               excluded path present, no unlisted path present.

Deliberately a plain script, not wired into `codecompass` itself --
Phase 81B's own clean-room mechanism is an orchestrator-side tool, not a
runtime capability of the product.
"""

from __future__ import annotations

import argparse
import hashlib
import shutil
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Amendment 3 (§6.1.1): every writer-visible path is named explicitly.
# Anything not covered by ALLOW_PATHS below is absent from the staging
# tree by construction -- this is an allow-list, not a deny-list
# (decisions/0066's own "a same-host curated export provides no
# architectural guarantee" finding applies equally to an ambiguous,
# implicitly-defined one).
ALLOW_PATHS: list[str] = [
    "src",
    "tests",
    "scripts",
    "pyproject.toml",
    "vendor.toml",
    "protocol/codecompass-adaptor-protocol/SCHEMA.md",
    "examples/toy-project",
    "planning/documentation-handoff",
]

# Named explicitly so a reviewer sees what was deliberately left out, not
# only what's present (decisions/0066's own manifest discipline). Not
# exhaustive of the real repository tree -- only the paths a reviewer
# would most plausibly expect to find and should confirm are genuinely
# absent.
EXCLUDED_PATHS: list[str] = [
    "README.md",
    "docs",
    "architecture",
    "ai-docs",
    "CONTRIBUTING.md",
    "CLAUDE.md",
    "decisions",
    "planning/retros",
    "planning/ROADMAP.md",
    "planning/CONTEXT.md",
    "planning/learnings",
    "planning/knowledge",
    "adapters",
    "vendor",
    "examples/README.md",
    "protocol/codecompass-adaptor-protocol/.git",
    "protocol/codecompass-adaptor-protocol/README.md",
    "protocol/codecompass-adaptor-protocol/CHANGELOG.md",
    "protocol/codecompass-adaptor-protocol/LICENSE",
    ".git",
    ".claude",
    ".cursor",
    "dist",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
]

ROOT_FILES = ["CLEANROOM-MANIFEST.yaml", "CLEANROOM-INSTRUCTIONS.md", "DOCUMENTATION-TARGET.md"]

def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git_tracked_files(root: Path, rel: str) -> list[str]:
    """Only files `git` itself actually tracks under `rel` -- never a raw
    filesystem walk. A local, `.gitignore`d, regenerated artifact (e.g. a
    test fixture's own `context-graph.db` left over from a prior local
    run) must never silently ride along into the clean-room tree just
    because it happens to exist on disk at build time; it was never part
    of the repository's own real content, and `git add -A` would skip it
    in the real committed branch anyway -- using the same source of truth
    here avoids a manifest that claims more than the actual commit
    contains (exactly the mismatch the validator's own "manifest-listed
    path is missing" check exists to catch)."""
    result = subprocess.run(
        ["git", "ls-files", "-z", "--", rel],
        cwd=root,
        capture_output=True,
        check=True,
    )
    return [p for p in result.stdout.decode("utf-8").split("\0") if p]


def _copy_allowed(root: Path, staging: Path) -> list[str]:
    included: list[str] = []
    for rel in ALLOW_PATHS:
        src = root / rel
        if not src.exists():
            print(f"WARNING: allow-listed path does not exist, skipped: {rel}", file=sys.stderr)
            continue
        if src.is_dir():
            tracked = _git_tracked_files(root, rel)
            if not tracked:
                print(f"WARNING: allow-listed dir has no git-tracked files: {rel}", file=sys.stderr)
            for tracked_rel in tracked:
                dst = staging / tracked_rel
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(root / tracked_rel, dst)
                included.append(tracked_rel)
        else:
            dst = staging / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            included.append(rel)
    return included


def _intermediary_hashes(root: Path, selected_slugs: list[str]) -> dict[str, dict[str, str]]:
    hashes: dict[str, dict[str, str]] = {}
    for slug in selected_slugs:
        inter_dir = root / "planning" / "knowledge" / slug / "intermediate"
        if not inter_dir.is_dir():
            continue
        hashes[slug] = {
            p.name: sha256_file(p) for p in sorted(inter_dir.glob("*.md"))
        }
    return hashes


_CLEANROOM_INSTRUCTIONS = """\
# Clean-room documentation writer instructions

You have no prior knowledge of this project.

Construct its documentation from first principles.

Use only the evidence supplied in this workspace -- the allowlisted
source/tests/configuration you can see, and the
`planning/documentation-handoff/` package, specifically.

The `planning/documentation-handoff/` package represents the project's
prepared semantic understanding. Start with its own `README.md`.

Use the current source, tests, configuration, and schemas in your own
workspace to verify and add technical detail the knowledge layer doesn't
carry.

Do not attempt to recover previous project documentation. None exists
anywhere in your own workspace, in any form.

Do not use Git history, external repository search, internet search, or
other repositories as project-documentation sources -- none of these are
technically reachable from inside your own workspace.

Do not assume undocumented behaviour.

Every important technical statement must either:
1. be supported by the supplied intermediary/evidence material; or
2. be independently verified by you against the current source/tests/
   configuration in your own workspace.

If evidence conflicts, preserve the conflict or uncertainty -- do not
silently resolve it.

Your workspace's `scripts/` directory contains maintainer-only tooling,
not part of the `codecompass` package itself (each one's own module
docstring says so). `check_knowledge_base.py`, `check_user_docs.py`, and
`prepare_cleanroom_branch.py` are ordinary repository-maintenance
tooling -- you may mention their existence and purpose briefly in a
development/contributing section if you judge that useful, the same way
you would any other maintainer script. `cleanroom_broker.py`,
`cleanroom_broker_client.py`, and `cleanroom_prompt_assembler.py`
specifically implement the clean-room mechanism that produced the
workspace you are reading right now -- do not describe, explain, or
reference this mechanism in the documentation you write; it is
orchestrator-internal tooling, not a CodeCompass product capability, and
is entirely out of scope for what you are being asked to document.

Write a complete new README and docs tree from zero.

Do not simply paraphrase the intermediary package mechanically.

See `planning/documentation-handoff/DOCUMENTATION-TARGET.md` for the
required coverage and expected structure.
"""


def cmd_build(args: argparse.Namespace) -> int:
    root = ROOT
    staging = Path(args.staging).resolve()
    if staging.exists():
        if (staging / ".git").is_file():
            print(
                f"FAIL: {staging} is already a git worktree (has a `.git` "
                "link file) -- refusing to rmtree it. Build into a plain "
                "scratch directory and copy the validated result into the "
                "worktree afterward instead.",
                file=sys.stderr,
            )
            return 1
        shutil.rmtree(staging)
    staging.mkdir(parents=True)

    included = sorted(_copy_allowed(root, staging))

    selected_slugs = args.slugs.split(",") if args.slugs else []
    inter_hashes = _intermediary_hashes(root, selected_slugs)

    all_slugs = sorted(
        p.name for p in (root / "planning" / "knowledge").iterdir() if p.is_dir()
    )

    (staging / "CLEANROOM-INSTRUCTIONS.md").write_text(_CLEANROOM_INSTRUCTIONS, encoding="utf-8")
    doc_target_src = root / "planning" / "documentation-handoff" / "DOCUMENTATION-TARGET.md"
    if doc_target_src.is_file():
        shutil.copy2(doc_target_src, staging / "DOCUMENTATION-TARGET.md")

    pyproject_text = (root / "pyproject.toml").read_text(encoding="utf-8")
    version_line = next(
        (line for line in pyproject_text.splitlines() if line.strip().startswith("version")), ""
    )
    codecompass_version = (
        version_line.split("=", 1)[-1].strip().strip('"') if version_line else "unknown"
    )

    manifest_lines = [
        "source_repository: ctosullivan/codecompass",
        f"documented_revision: {args.documented_revision}",
        "handoff_commit: null  # filled in after this tree is committed to its own branch",
        f"generated_at: \"{datetime.now(UTC).isoformat()}\"",
        f"codecompass_version: \"{codecompass_version}\"",
        "",
        "included_paths:",
    ]
    manifest_lines += [f"  - {p}" for p in included]
    manifest_lines += ["", "excluded_paths:"]
    manifest_lines += [f"  - {p}" for p in EXCLUDED_PATHS]
    manifest_lines += ["", f"all_rendered_knowledge_slugs: {all_slugs}", ""]
    manifest_lines += [f"handoff_selected_slugs: {selected_slugs}", ""]
    manifest_lines += ["intermediary_projection_hashes:"]
    for slug, files in inter_hashes.items():
        manifest_lines.append(f"  {slug}:")
        for fname, h in files.items():
            manifest_lines.append(f"    {fname}: {h}")
    manifest_lines += [
        "",
        "documentation_disposition: planning/documentation-handoff/DISPOSITION-REPORT.md",
        "",
        'network_policy: "no network interfaces configured in the Mode B '
        'workspace -- see planning/phase-81b-mode-b-isolation-investigation.md"',
        'history_policy: "none -- this filesystem has no .git directory"',
        'credential_policy: "none -- no SSH keys, tokens, or env-var secrets included"',
        'narrative_documentation_policy: "none of README.md/docs/**/'
        'architecture/**/ai-docs/**, including docs/domain/**, is present '
        'in this filesystem in its own original prose form"',
        "invalidated_by: null",
        "",
    ]
    (staging / "CLEANROOM-MANIFEST.yaml").write_text("\n".join(manifest_lines), encoding="utf-8")

    print(f"Built clean-room staging tree at {staging}")
    print(f"  {len(included)} allow-listed files")
    print(f"  {len(EXCLUDED_PATHS)} named exclusions recorded")
    print(f"  handoff_selected_slugs: {selected_slugs}")
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    staging = Path(args.staging).resolve()
    manifest_path = staging / "CLEANROOM-MANIFEST.yaml"
    if not manifest_path.is_file():
        print("FAIL: no CLEANROOM-MANIFEST.yaml found", file=sys.stderr)
        return 1

    import re

    text = manifest_path.read_text(encoding="utf-8")
    failures: list[str] = []

    # 1. No excluded path present.
    for excl in EXCLUDED_PATHS:
        if (staging / excl).exists():
            failures.append(f"excluded path IS present: {excl}")

    # 2. Every included_path from the manifest is present.
    in_included = False
    manifest_included: list[str] = []
    for line in text.splitlines():
        if line.strip() == "included_paths:":
            in_included = True
            continue
        if in_included:
            if line.startswith("  - "):
                manifest_included.append(line[4:].strip())
            else:
                in_included = False
    for rel in manifest_included:
        if not (staging / rel).is_file():
            failures.append(f"manifest-listed path is missing: {rel}")

    # 3. No unlisted writer-visible path -- every real file under staging
    #    (other than the three root files and the manifest itself) must
    #    appear in manifest_included.
    manifest_included_set = set(manifest_included)
    for p in sorted(staging.rglob("*")):
        if p.is_dir():
            continue
        rel = str(p.relative_to(staging))
        if rel in ROOT_FILES or rel == "CLEANROOM-MANIFEST.yaml":
            continue
        if rel not in manifest_included_set:
            failures.append(f"unlisted writer-visible path present: {rel}")

    # 4. intermediary_projection_hashes match a fresh re-hash.
    hash_re = re.compile(r"^\s{4}(\S+\.md):\s*([0-9a-f]{64})\s*$")
    slug_re = re.compile(r"^\s{2}([\w-]+):\s*$")
    in_hashes_block = False
    current_slug: str | None = None
    for line in text.splitlines():
        if line.strip() == "intermediary_projection_hashes:":
            in_hashes_block = True
            continue
        if not in_hashes_block:
            continue
        if line and not line.startswith(" "):
            in_hashes_block = False
            continue
        m_slug = slug_re.match(line)
        if m_slug:
            current_slug = m_slug.group(1)
            continue
        m_hash = hash_re.match(line)
        if m_hash and current_slug:
            fname, recorded_hash = m_hash.groups()
            real_path = (
                ROOT / "planning" / "knowledge" / current_slug / "intermediate" / fname
            )
            if not real_path.is_file():
                failures.append(f"hash recorded for missing file: {current_slug}/{fname}")
                continue
            fresh_hash = sha256_file(real_path)
            if fresh_hash != recorded_hash:
                failures.append(
                    f"hash mismatch for {current_slug}/{fname}: manifest says "
                    f"{recorded_hash[:12]}..., fresh render is {fresh_hash[:12]}..."
                )

    if failures:
        print(f"FAIL: {len(failures)} finding(s)")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("PASS: staging tree matches its own manifest exactly")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p_build = sub.add_parser("build")
    p_build.add_argument("staging", help="Directory to build the staging tree into")
    p_build.add_argument("--documented-revision", required=True)
    p_build.add_argument(
        "--slugs", default="", help="Comma-separated handoff_selected_slugs"
    )
    p_build.set_defaults(func=cmd_build)

    p_validate = sub.add_parser("validate")
    p_validate.add_argument("staging", help="Staging directory to validate")
    p_validate.set_defaults(func=cmd_validate)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
