#!/usr/bin/env python3
"""Phase 81B (`planning/phase-81b-clean-room-redocumentation.md` §6.1/
§6.1.1/§22 item 4, corrected by §27 "Amendment 5"): build and validate a
clean-room handoff tree for CodeCompass, under an explicit, named
allowlist -- never an ambiguous "handoff filesystem".

Two sub-commands:

    build      Export the allowlisted tree, at the exact declared
               `--documented-revision`, from the Git object database --
               never the live working tree -- plus the handoff package
               (planning/documentation-handoff/), into a staging
               directory. Writes CLEANROOM-MANIFEST.yaml/
               CLEANROOM-INSTRUCTIONS.md/DOCUMENTATION-TARGET.md at its
               root. The manifest cryptographically binds every
               writer-visible payload file.
    validate   Confirm a built staging directory's own tree matches its
               own manifest exactly, using only the staged tree itself --
               no access to the parent repository required. Checks: no
               excluded path present, no unlisted path present, every
               manifest-listed payload file present with a matching
               content hash, and the manifest's own canonical top-level
               digest is internally consistent.

Deliberately a plain script, not wired into `codecompass` itself --
Phase 81B's own clean-room mechanism is an orchestrator-side tool, not a
runtime capability of the product.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent

MANIFEST_SCHEMA_VERSION = 2


class CleanroomExportError(RuntimeError):
    """A requested export cannot be performed faithfully -- fail closed
    rather than silently falling back to the working tree or a different
    revision."""


class UnclassifiedNarrativeShapedFileError(RuntimeError):
    """A doc-shaped file appeared beneath a broad allow-listed directory
    with no explicit keep/exclude classification -- fail closed rather
    than guess (§27.1 item 1 / §27.3 item 2)."""


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
    "protocol/codecompass-adaptor-protocol/schemas",
    "protocol/codecompass-adaptor-protocol/conformance",
    "protocol/codecompass-adaptor-protocol/examples",
    "adapters/haskell/app",
    "adapters/haskell/src",
    "adapters/haskell/test",
    "adapters/haskell/codecompass-adaptor-haskell.cabal",
    "adapters/haskell/package.yaml",
    "adapters/haskell/stack.yaml",
    "adapters/haskell/stack.yaml.lock",
    "examples/toy-project",
    "planning/documentation-handoff",
    ".gitmodules",
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
    "vendor",
    "examples/README.md",
    "protocol/codecompass-adaptor-protocol/.git",
    "protocol/codecompass-adaptor-protocol/README.md",
    "protocol/codecompass-adaptor-protocol/CHANGELOG.md",
    "protocol/codecompass-adaptor-protocol/LICENSE",
    "adapters/haskell/.git",
    "adapters/haskell/.stack-work",
    "adapters/haskell/README.md",
    "adapters/haskell/CHANGELOG.md",
    "adapters/haskell/LICENSE",
    ".git",
    ".claude",
    ".cursor",
    "dist",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
]

# Amendment 5 (§27.1 item 1 / §27.3 item 2): a broad allow-listed
# directory is swept in wholesale by `git ls-tree`, with no per-file
# review -- unlike every other ALLOW_PATHS entry outside these three,
# which names an individual file or a narrow, already-reviewed
# subdirectory. A doc-shaped file (`.md`/`.rst`/`.txt`) found beneath one
# of these three is therefore not writer-visible merely because `git`
# tracks it: it must appear in exactly one of the two classification
# sets below, or the build fails closed.
_BROAD_ALLOW_PATHS_REQUIRING_CLASSIFICATION = ("src", "tests", "scripts")
_NARRATIVE_SHAPED_SUFFIXES = (".md", ".rst", ".txt")

# Genuinely structural/machine-fixture/test-evidence doc-shaped files
# beneath a broad directory -- each entry reviewed and justified, never a
# blanket allowance.
_CLASSIFIED_KEEP_DOC_PATHS: frozenset[str] = frozenset(
    {
        # A real external project's README, used only as parsing input
        # for the npm adapter's own README-scanning test
        # (tests/test_adapter_npm.py) -- not narrative ABOUT this
        # project.
        "tests/fixtures/sample_readme.md",
        # Exact machine fixtures of codecompass's OWN generated-artifact
        # format (Skill, slash command) -- structural evidence of output
        # shape, the same category as the schema/example fixtures already
        # kept elsewhere in ALLOW_PATHS, never narrative about project
        # history/process. (The sibling CLAUDE.md fixture in this same
        # directory is `.gitignore`d, regenerated-not-committed content --
        # see its own `.gitignore` -- so it is never git-tracked and never
        # reaches this classification gate at all; no entry is needed for
        # it here.)
        "tests/fixtures/ledgerkit_lifecycle_demo/.claude/commands/discovery.md",
        "tests/fixtures/ledgerkit_lifecycle_demo/.claude/skills/codecompass/SKILL.md",
    }
)

# Narrative/historical/project-process prose beneath a broad directory --
# confirmed real leaks found by Amendment 5's own review (§27.1 item 1).
_CLASSIFIED_EXCLUDE_DOC_PATHS: frozenset[str] = frozenset(
    {
        "tests/README.md",
        "tests/fixtures/ledgerkit_lifecycle_demo/DEMO.md",
        "tests/fixtures/ledgerkit_lifecycle_demo/dev-docs/architecture.md",
        "tests/fixtures/ledgerkit_lifecycle_demo/dev-docs/planning/README.md",
        "tests/fixtures/ledgerkit_lifecycle_demo/dev-docs/retros/README.md",
    }
)

ROOT_FILES = ["CLEANROOM-MANIFEST.yaml", "CLEANROOM-INSTRUCTIONS.md", "DOCUMENTATION-TARGET.md"]


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _filter_narrative_shaped(rel_paths: list[str], broad_prefix: str) -> list[str]:
    """Apply the fail-closed keep/exclude classification to files swept
    in by a broad allow-listed directory. Raises
    UnclassifiedNarrativeShapedFileError for any doc-shaped file that is
    neither explicitly kept nor explicitly excluded (§27.1 item 1)."""
    kept: list[str] = []
    for rel in rel_paths:
        if not rel.lower().endswith(_NARRATIVE_SHAPED_SUFFIXES):
            kept.append(rel)
            continue
        if rel in _CLASSIFIED_KEEP_DOC_PATHS:
            kept.append(rel)
            continue
        if rel in _CLASSIFIED_EXCLUDE_DOC_PATHS:
            continue
        raise UnclassifiedNarrativeShapedFileError(
            f"{rel!r} is a doc-shaped file beneath the broad allow-listed "
            f"directory {broad_prefix!r} with no explicit keep/exclude "
            "classification in prepare_cleanroom_branch.py -- refusing to "
            "guess whether it is narrative prose or structural evidence. "
            "Classify it in _CLASSIFIED_KEEP_DOC_PATHS or "
            "_CLASSIFIED_EXCLUDE_DOC_PATHS first."
        )
    return kept


def _require_commit_exists(repo_root: Path, revision: str) -> None:
    """Fail closed if `revision` does not resolve to a real commit object
    reachable in `repo_root`'s own object database -- never silently fall
    back to the working tree or another revision (§27.1 item 2)."""
    result = subprocess.run(
        ["git", "cat-file", "-e", f"{revision}^{{commit}}"],
        cwd=repo_root,
        capture_output=True,
    )
    if result.returncode != 0:
        raise CleanroomExportError(
            f"revision {revision!r} does not resolve to a commit object "
            f"reachable in {repo_root} -- refusing to export"
        )


def _git_submodule_paths(root: Path) -> list[str]:
    """Submodule paths declared in .gitmodules, read via `git config`."""
    gitmodules = root / ".gitmodules"
    if not gitmodules.is_file():
        return []
    result = subprocess.run(
        ["git", "config", "-f", str(gitmodules), "--get-regexp", r"^submodule\..*\.path$"],
        capture_output=True,
        text=True,
        check=True,
    )
    paths = []
    for line in result.stdout.splitlines():
        parts = line.split(None, 1)
        if len(parts) == 2:
            paths.append(parts[1].strip())
    return paths


def _submodule_gitlink_sha(root: Path, submodule_rel: str, documented_revision: str) -> str:
    """The exact commit SHA the superproject recorded for `submodule_rel`
    at `documented_revision` -- never the currently-checked-out submodule
    HEAD (§27.1 item 2)."""
    result = subprocess.run(
        ["git", "ls-tree", documented_revision, "--", submodule_rel],
        cwd=root,
        capture_output=True,
        text=True,
        check=True,
    )
    line = result.stdout.strip()
    if not line:
        raise CleanroomExportError(
            f"no gitlink entry for {submodule_rel!r} at revision "
            f"{documented_revision!r} -- refusing to export"
        )
    mode_type_sha, _, _path = line.partition("\t")
    parts = mode_type_sha.split()
    if len(parts) != 3 or parts[1] != "commit":
        raise CleanroomExportError(
            f"unexpected ls-tree entry for submodule {submodule_rel!r}: {line!r}"
        )
    return parts[2]


def _git_object_type(repo_root: Path, revision: str, rel: str) -> str | None:
    """'blob', 'tree', or None if `rel` does not exist at `revision`."""
    result = subprocess.run(
        ["git", "ls-tree", revision, "--", rel],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=True,
    )
    line = result.stdout.strip()
    if not line:
        return None
    mode_type_sha, _, _path = line.partition("\t")
    parts = mode_type_sha.split()
    return parts[1] if len(parts) == 3 else None


def _git_tracked_files_at_revision(repo_root: Path, revision: str, rel: str) -> list[str]:
    """Tracked files beneath `rel` exactly as they existed at `revision`,
    resolved purely from the Git object database -- never the working
    tree (§27.1 item 2)."""
    result = subprocess.run(
        ["git", "ls-tree", "-r", "--name-only", "-z", revision, "--", rel],
        cwd=repo_root,
        capture_output=True,
        check=True,
    )
    return [p for p in result.stdout.decode("utf-8").split("\0") if p]


def _export_file_at_revision(repo_root: Path, revision: str, rel: str, dst: Path) -> None:
    result = subprocess.run(
        ["git", "cat-file", "-p", f"{revision}:{rel}"],
        cwd=repo_root,
        capture_output=True,
        check=True,
    )
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_bytes(result.stdout)


def _export_path(
    repo_root: Path,
    revision: str,
    rel: str,
    staging: Path,
    *,
    dest_prefix: str = "",
    classify_narrative: str | None = None,
) -> list[str]:
    """Export `rel` at `revision` from `repo_root` into `staging`
    (optionally nested under `dest_prefix`, for submodule content).
    Returns the list of relpaths (relative to `staging`) actually
    written. If `classify_narrative` names a broad allow-listed directory
    prefix, doc-shaped files are run through the fail-closed keep/exclude
    gate first."""
    if rel == ".":
        # `git ls-tree <rev> -- .` is special-cased by git to mean "the
        # whole tree," not "look up an entry literally named '.'" --
        # routing it through _git_object_type would silently misread the
        # first real tree entry's own type/sha as if they belonged to
        # ".". Used when exporting an entire submodule root (dest_prefix
        # carries the submodule's own mount point).
        obj_type = "tree"
    else:
        obj_type = _git_object_type(repo_root, revision, rel)
        if obj_type is None:
            print(
                f"WARNING: allow-listed path does not exist at revision "
                f"{revision}, skipped: {rel}",
                file=sys.stderr,
            )
            return []

    included: list[str] = []
    if obj_type == "tree":
        tracked = _git_tracked_files_at_revision(repo_root, revision, rel)
        if not tracked:
            print(
                f"WARNING: allow-listed dir has no git-tracked files at "
                f"this revision: {rel}",
                file=sys.stderr,
            )
        if classify_narrative is not None:
            tracked = _filter_narrative_shaped(tracked, classify_narrative)
        for tracked_rel in tracked:
            dest_rel = str(Path(dest_prefix) / tracked_rel) if dest_prefix else tracked_rel
            _export_file_at_revision(repo_root, revision, tracked_rel, staging / dest_rel)
            included.append(dest_rel)
    else:
        dest_rel = str(Path(dest_prefix) / rel) if dest_prefix else rel
        _export_file_at_revision(repo_root, revision, rel, staging / dest_rel)
        included.append(dest_rel)
    return included


def _export_allowed(root: Path, staging: Path, documented_revision: str) -> list[str]:
    """Export every ALLOW_PATHS entry at the exact `documented_revision`
    -- including, for submodule-nested entries, the exact gitlink
    revision the superproject recorded at that same point, never the
    currently-checked-out submodule HEAD (§27.1 items 1-2)."""
    _require_commit_exists(root, documented_revision)
    submodule_paths = _git_submodule_paths(root)
    included: list[str] = []
    for rel in ALLOW_PATHS:
        broad_prefix = next(
            (p for p in _BROAD_ALLOW_PATHS_REQUIRING_CLASSIFICATION if rel == p), None
        )
        submodule_prefix = next(
            (sp for sp in submodule_paths if rel == sp or rel.startswith(sp + "/")), None
        )
        if submodule_prefix is None:
            included += _export_path(
                root, documented_revision, rel, staging, classify_narrative=broad_prefix
            )
            continue

        sub_repo_root = root / submodule_prefix
        if not sub_repo_root.is_dir():
            print(
                f"WARNING: submodule not checked out, skipped: {rel}",
                file=sys.stderr,
            )
            continue
        gitlink_sha = _submodule_gitlink_sha(root, submodule_prefix, documented_revision)
        _require_commit_exists(sub_repo_root, gitlink_sha)
        rel_within_submodule = os.path.relpath(rel, submodule_prefix)
        included += _export_path(
            sub_repo_root,
            gitlink_sha,
            rel_within_submodule,
            staging,
            dest_prefix=submodule_prefix,
        )
    return included


def _intermediary_hashes(root: Path, selected_slugs: list[str]) -> dict[str, dict[str, str]]:
    """Build-time-only informational freshness marker: has the live
    `planning/knowledge/<slug>/intermediate/` content on `main` moved on
    since this handoff was prepared? Deliberately **not** consulted by
    `cmd_validate` (§27.1 item 4 / §27.3 item 3) -- post-export validation
    must be self-contained, so this stays a build-time record only."""
    hashes: dict[str, dict[str, str]] = {}
    for slug in selected_slugs:
        inter_dir = root / "planning" / "knowledge" / slug / "intermediate"
        if not inter_dir.is_dir():
            continue
        hashes[slug] = {p.name: sha256_file(p) for p in sorted(inter_dir.glob("*.md"))}
    return hashes


def _canonical_digest_of_hashes(file_hashes: dict[str, str]) -> str:
    """SHA-256 over a canonical, sorted "hash  path" manifest built from
    an already-known {relpath: sha256} mapping."""
    canonical_lines = [f"{file_hashes[rel]}  {rel}" for rel in sorted(file_hashes)]
    canonical_text = "\n".join(canonical_lines) + "\n"
    return sha256_bytes(canonical_text.encode("utf-8"))


def _canonical_payload_digest(
    staging: Path, payload_relpaths: list[str]
) -> tuple[str, dict[str, str]]:
    """Hash every writer-visible payload file under `staging` and return
    the canonical top-level digest alongside the per-file hashes. The
    manifest file itself is deliberately excluded from `payload_relpaths`
    -- a file cannot bind its own identity without changing it (§27.1
    item 3 / §27.3 item 4)."""
    per_file: dict[str, str] = {rel: sha256_file(staging / rel) for rel in payload_relpaths}
    return _canonical_digest_of_hashes(per_file), per_file


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
`cleanroom_broker_client.py`, `cleanroom_prompt_assembler.py`, and
`verify_cleanroom_isolation.py` specifically implement the clean-room
mechanism that produced the workspace you are reading right now -- do
not describe, explain, or reference this mechanism in the documentation
you write; it is orchestrator-internal tooling, not a CodeCompass
product capability, and is entirely out of scope for what you are being
asked to document.

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

    try:
        included = sorted(_export_allowed(root, staging, args.documented_revision))
    except CleanroomExportError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        shutil.rmtree(staging, ignore_errors=True)
        return 1
    except UnclassifiedNarrativeShapedFileError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        shutil.rmtree(staging, ignore_errors=True)
        return 1

    selected_slugs = args.slugs.split(",") if args.slugs else []
    inter_hashes = _intermediary_hashes(root, selected_slugs)

    all_slugs = sorted(p.name for p in (root / "planning" / "knowledge").iterdir() if p.is_dir())

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

    # Amendment 5 (§27.3 item 3): every writer-visible payload file is
    # content-bound, including the two generated root instruction files
    # -- the manifest itself is the one, explicit, non-circular exception
    # (§27.3 item 4).
    payload_relpaths = sorted(included + [p for p in ROOT_FILES if p != "CLEANROOM-MANIFEST.yaml"])
    payload_tree_sha256, payload_file_hashes = _canonical_payload_digest(staging, payload_relpaths)

    manifest = {
        "manifest_schema_version": MANIFEST_SCHEMA_VERSION,
        "source_repository": "ctosullivan/codecompass",
        "documented_revision": args.documented_revision,
        "generated_at": datetime.now(UTC).isoformat(),
        "codecompass_version": codecompass_version,
        "included_paths": included,
        "excluded_paths": EXCLUDED_PATHS,
        "all_rendered_knowledge_slugs": all_slugs,
        "handoff_selected_slugs": selected_slugs,
        "intermediary_projection_hashes": inter_hashes,
        "payload_tree_sha256": payload_tree_sha256,
        "payload_file_hashes": payload_file_hashes,
        "documentation_disposition": "planning/documentation-handoff/DISPOSITION-REPORT.md",
        "network_policy": (
            "no network interfaces configured in the Mode B workspace -- "
            "see planning/phase-81b-mode-b-isolation-investigation.md"
        ),
        "history_policy": "none -- this filesystem has no .git directory",
        "credential_policy": "none -- no SSH keys, tokens, or env-var secrets included",
        "narrative_documentation_policy": (
            "none of README.md/docs/**/architecture/**/ai-docs/**, including "
            "docs/domain/**, is present in this filesystem in its own "
            "original prose form; doc-shaped files swept in by a broad "
            "allow-listed directory are additionally classified file-by-"
            "file -- see prepare_cleanroom_branch.py's own "
            "_CLASSIFIED_KEEP_DOC_PATHS/_CLASSIFIED_EXCLUDE_DOC_PATHS"
        ),
        "invalidated_by": None,
    }
    (staging / "CLEANROOM-MANIFEST.yaml").write_text(
        yaml.safe_dump(manifest, sort_keys=False, default_flow_style=False, width=1_000_000),
        encoding="utf-8",
    )

    print(f"Built clean-room staging tree at {staging}")
    print(f"  documented_revision: {args.documented_revision}")
    print(f"  {len(included)} allow-listed files exported from the Git object database")
    print(f"  {len(EXCLUDED_PATHS)} named exclusions recorded")
    print(f"  payload_tree_sha256: {payload_tree_sha256}")
    print(f"  handoff_selected_slugs: {selected_slugs}")
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    """Self-contained: validates the staged tree purely against its own
    manifest, with no access to the parent repository (§27.1 item 4 /
    §27.3 item 3)."""
    staging = Path(args.staging).resolve()
    manifest_path = staging / "CLEANROOM-MANIFEST.yaml"
    if not manifest_path.is_file():
        print("FAIL: no CLEANROOM-MANIFEST.yaml found", file=sys.stderr)
        return 1

    try:
        manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        print(f"FAIL: CLEANROOM-MANIFEST.yaml is not valid YAML: {exc}", file=sys.stderr)
        return 1

    failures: list[str] = []

    # 1. No excluded path present.
    for excl in EXCLUDED_PATHS:
        if (staging / excl).exists():
            failures.append(f"excluded path IS present: {excl}")

    payload_file_hashes = manifest.get("payload_file_hashes") or {}
    if not isinstance(payload_file_hashes, dict) or not payload_file_hashes:
        failures.append("manifest has no payload_file_hashes -- cannot self-validate")
        print(f"FAIL: {len(failures)} finding(s)")
        for f in failures:
            print(f"  - {f}")
        return 1

    # 2. Every manifest-listed payload file is present with a matching
    #    content hash (catches changed, removed, or renamed content --
    #    entirely from the staged tree itself).
    for rel, recorded_hash in payload_file_hashes.items():
        real_path = staging / rel
        if not real_path.is_file():
            failures.append(f"manifest-listed payload path is missing: {rel}")
            continue
        fresh_hash = sha256_file(real_path)
        if fresh_hash != recorded_hash:
            failures.append(
                f"hash mismatch for {rel}: manifest says {recorded_hash[:12]}..., "
                f"fresh hash is {fresh_hash[:12]}..."
            )

    # 3. No unlisted writer-visible path -- every real file under staging
    #    (other than the manifest itself) must appear in
    #    payload_file_hashes (catches an added file).
    payload_set = set(payload_file_hashes)
    for p in sorted(staging.rglob("*")):
        if p.is_dir():
            continue
        rel = str(p.relative_to(staging))
        if rel == "CLEANROOM-MANIFEST.yaml":
            continue
        if rel not in payload_set:
            failures.append(f"unlisted writer-visible path present: {rel}")

    # 4. The manifest's own canonical top-level digest is internally
    #    consistent with its own per-file hash list (catches manifest
    #    tampering/inconsistency, without touching the parent repo).
    recomputed_digest = _canonical_digest_of_hashes(payload_file_hashes)
    recorded_digest = manifest.get("payload_tree_sha256")
    if recorded_digest != recomputed_digest:
        failures.append(
            "payload_tree_sha256 is inconsistent with the manifest's own "
            f"payload_file_hashes: recorded {str(recorded_digest)[:12]}..., "
            f"recomputed {recomputed_digest[:12]}..."
        )

    if failures:
        print(f"FAIL: {len(failures)} finding(s)")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("PASS: staging tree matches its own manifest exactly (self-contained)")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p_build = sub.add_parser("build")
    p_build.add_argument("staging", help="Directory to build the staging tree into")
    p_build.add_argument(
        "--documented-revision",
        required=True,
        help="An exact, resolvable Git commit-ish on the superproject (e.g. a full or "
        "short SHA). Content is exported from the Git object database at this exact "
        "revision, never from the working tree.",
    )
    p_build.add_argument("--slugs", default="", help="Comma-separated handoff_selected_slugs")
    p_build.set_defaults(func=cmd_build)

    p_validate = sub.add_parser("validate")
    p_validate.add_argument("staging", help="Staging directory to validate")
    p_validate.set_defaults(func=cmd_validate)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
