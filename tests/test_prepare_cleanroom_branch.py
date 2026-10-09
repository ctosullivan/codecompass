"""Tests for scripts/prepare_cleanroom_branch.py — a maintainer-only tool,
not part of the codecompass package. Imported directly from its file
path (see tests/test_check_knowledge_base.py's own identical precedent).

Phase 81B (`planning/phase-81b-clean-room-redocumentation.md` §6.1/
§6.1.1/§22 item 4): confirms the branch validator's own four fail-closed
conditions are genuinely enforced against a real build, not merely
trivially passing — an excluded path present, an unlisted path present,
a listed path missing, and a hash mismatch must each independently fail.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_SCRIPT_PATH = (
    Path(__file__).resolve().parent.parent / "scripts" / "prepare_cleanroom_branch.py"
)
_spec = importlib.util.spec_from_file_location("prepare_cleanroom_branch", _SCRIPT_PATH)
prepare_cleanroom_branch = importlib.util.module_from_spec(_spec)
sys.modules["prepare_cleanroom_branch"] = prepare_cleanroom_branch
_spec.loader.exec_module(prepare_cleanroom_branch)

REPO_ROOT = Path(__file__).resolve().parent.parent


def _build(tmp_path: Path) -> Path:
    staging = tmp_path / "staging"
    args = type(
        "Args",
        (),
        {
            "staging": str(staging),
            "documented_revision": "test-revision",
            "slugs": "codecompass-domain",
        },
    )()
    assert prepare_cleanroom_branch.cmd_build(args) == 0
    return staging


def test_real_build_validates_clean(tmp_path):
    """A genuine build against the real repository passes its own
    validator with zero findings."""
    staging = _build(tmp_path)
    args = type("Args", (), {"staging": str(staging)})()
    assert prepare_cleanroom_branch.cmd_validate(args) == 0


def test_excluded_path_present_fails_closed(tmp_path):
    staging = _build(tmp_path)
    (staging / "README.md").write_text("smuggled narrative content\n", encoding="utf-8")
    args = type("Args", (), {"staging": str(staging)})()
    assert prepare_cleanroom_branch.cmd_validate(args) == 1


def test_unlisted_path_present_fails_closed(tmp_path):
    staging = _build(tmp_path)
    (staging / "src" / "sneaky.txt").write_text("not in the manifest\n", encoding="utf-8")
    args = type("Args", (), {"staging": str(staging)})()
    assert prepare_cleanroom_branch.cmd_validate(args) == 1


def test_manifest_listed_path_missing_fails_closed(tmp_path):
    staging = _build(tmp_path)
    (staging / "pyproject.toml").unlink()
    args = type("Args", (), {"staging": str(staging)})()
    assert prepare_cleanroom_branch.cmd_validate(args) == 1


def test_no_manifest_fails_closed(tmp_path):
    staging = tmp_path / "empty"
    staging.mkdir()
    args = type("Args", (), {"staging": str(staging)})()
    assert prepare_cleanroom_branch.cmd_validate(args) == 1


def test_refuses_to_rmtree_an_existing_git_worktree(tmp_path):
    """Regression test for the real bug this phase's own investigation
    found: `git worktree add --orphan` followed immediately by
    `cmd_build`'s own `shutil.rmtree(staging)` destroyed the worktree's
    own `.git` link file, since the tool didn't anticipate its own
    staging target already being a git worktree. `cmd_build` must refuse
    rather than blindly `rmtree`."""
    staging = tmp_path / "staging"
    staging.mkdir()
    (staging / ".git").write_text("gitdir: /some/real/worktrees/path\n", encoding="utf-8")
    args = type(
        "Args",
        (),
        {"staging": str(staging), "documented_revision": "test-revision", "slugs": ""},
    )()
    assert prepare_cleanroom_branch.cmd_build(args) == 1
    assert (staging / ".git").exists()


def test_build_excludes_untracked_gitignored_files(tmp_path):
    """Regression test for the real bug this phase's own investigation
    found: a raw filesystem walk (shutil.copytree) silently included
    local, untracked, .gitignore'd artifacts that exist on disk but are
    not tracked by git at all -- the manifest claimed they were included,
    but `git add -A` in the real clean-room branch correctly refused to
    commit them, producing a real manifest/reality mismatch. The build
    must source its file list from `git ls-files`, never a directory
    walk, so an untracked file sitting in an allow-listed directory never
    makes it into the staging tree or the manifest at all."""
    sneaky = REPO_ROOT / "tests" / "__phase81b_untracked_regression_test__.txt"
    assert not sneaky.exists(), "fixture collision -- stale file from a prior failed run"
    try:
        sneaky.write_text(
            "should never be picked up by a git-tracked-files build\n", encoding="utf-8"
        )
        staging = _build(tmp_path)
        assert not (staging / "tests" / sneaky.name).exists()
        manifest_text = (staging / "CLEANROOM-MANIFEST.yaml").read_text(encoding="utf-8")
        assert sneaky.name not in manifest_text
    finally:
        sneaky.unlink(missing_ok=True)


def test_git_tracked_files_resolves_paths_inside_a_submodule(tmp_path):
    """Regression test for a real bug this phase's own cold-reader
    testing found: a directory inside a Git submodule (e.g.
    protocol/codecompass-adaptor-protocol/schemas) is invisible to
    `git ls-files` run from the superproject's own root, since the
    superproject only tracks the submodule as a single gitlink entry.
    _git_tracked_files must resolve the real git toplevel for the
    target path first, so it correctly descends into the submodule's
    own separate repository."""
    submodule_rel = "protocol/codecompass-adaptor-protocol"
    assert (REPO_ROOT / submodule_rel / ".git").exists(), (
        "fixture assumption broken: this is no longer a real submodule checkout"
    )
    tracked = prepare_cleanroom_branch._git_tracked_files(REPO_ROOT, f"{submodule_rel}/schemas")
    assert tracked, "expected real tracked files inside the submodule's schemas/ directory"
    assert all(t.startswith(f"{submodule_rel}/schemas/") for t in tracked)
    for t in tracked:
        assert (REPO_ROOT / t).is_file()


def test_allow_list_contains_no_narrative_documentation_paths():
    """Amendment 2/3: README.md/docs/**/architecture/**/ai-docs/** (and
    docs/domain/** specifically) must never appear in the allow-list
    itself — a structural guard against the allow-list silently growing
    to include narrative documentation later."""
    excluded_prefixes = (
        "README.md", "docs", "architecture", "ai-docs", "CONTRIBUTING.md", "CLAUDE.md",
    )
    for allowed in prepare_cleanroom_branch.ALLOW_PATHS:
        assert not any(
            allowed == p or allowed.startswith(p + "/") for p in excluded_prefixes
        ), f"narrative-documentation-shaped path leaked into ALLOW_PATHS: {allowed}"
