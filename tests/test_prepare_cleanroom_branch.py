"""Tests for scripts/prepare_cleanroom_branch.py -- a maintainer-only tool,
not part of the codecompass package. Imported directly from its file
path (see tests/test_check_knowledge_base.py's own identical precedent).

Phase 81B (`planning/phase-81b-clean-room-redocumentation.md` §6.1/
§6.1.1/§22 item 4, corrected by §27 "Amendment 5"): confirms the branch
validator's own fail-closed conditions are genuinely enforced against a
real build, not merely trivially passing, and confirms the Amendment 5
corrective fixes -- exact-revision export, submodule gitlink pinning,
file-level narrative classification, self-contained content-addressed
validation -- are real, not aspirational.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

_SCRIPT_PATH = (
    Path(__file__).resolve().parent.parent / "scripts" / "prepare_cleanroom_branch.py"
)
_spec = importlib.util.spec_from_file_location("prepare_cleanroom_branch", _SCRIPT_PATH)
prepare_cleanroom_branch = importlib.util.module_from_spec(_spec)
sys.modules["prepare_cleanroom_branch"] = prepare_cleanroom_branch
_spec.loader.exec_module(prepare_cleanroom_branch)

REPO_ROOT = Path(__file__).resolve().parent.parent


def _real_head_revision() -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, capture_output=True, text=True, check=True
    ).stdout.strip()


def _build(
    tmp_path: Path, *, revision: str | None = None, slugs: str = "codecompass-domain"
) -> Path:
    staging = tmp_path / "staging"
    args = type(
        "Args",
        (),
        {
            "staging": str(staging),
            "documented_revision": revision or _real_head_revision(),
            "slugs": slugs,
        },
    )()
    assert prepare_cleanroom_branch.cmd_build(args) == 0
    return staging


def _validate(staging: Path) -> int:
    args = type("Args", (), {"staging": str(staging)})()
    return prepare_cleanroom_branch.cmd_validate(args)


# ---------------------------------------------------------------------------
# Baseline real build/validate round-trip
# ---------------------------------------------------------------------------


def test_real_build_validates_clean(tmp_path):
    """A genuine build against the real repository, at a real resolvable
    revision, passes its own self-contained validator with zero findings."""
    staging = _build(tmp_path)
    assert _validate(staging) == 0


def test_no_manifest_fails_closed(tmp_path):
    staging = tmp_path / "empty"
    staging.mkdir()
    assert _validate(staging) == 1


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
        {"staging": str(staging), "documented_revision": _real_head_revision(), "slugs": ""},
    )()
    assert prepare_cleanroom_branch.cmd_build(args) == 1
    assert (staging / ".git").exists()


# ---------------------------------------------------------------------------
# Self-contained, content-addressed validation (§27.1 item 4 / §27.3 item 3)
# ---------------------------------------------------------------------------


def test_excluded_path_present_fails_closed(tmp_path):
    staging = _build(tmp_path)
    (staging / "README.md").write_text("smuggled narrative content\n", encoding="utf-8")
    assert _validate(staging) == 1


def test_unlisted_path_present_fails_closed(tmp_path):
    staging = _build(tmp_path)
    (staging / "src" / "sneaky.txt").write_text("not in the manifest\n", encoding="utf-8")
    assert _validate(staging) == 1


def test_manifest_listed_path_missing_fails_closed(tmp_path):
    staging = _build(tmp_path)
    (staging / "pyproject.toml").unlink()
    assert _validate(staging) == 1


def test_payload_file_content_mutation_fails_closed(tmp_path):
    """Regression test for a real gap: the old validator never hashed
    payload (source/test/config) content at all -- only the separate
    intermediary-knowledge projection hashes. A changed payload file must
    now fail validation (§27.1 item 4)."""
    staging = _build(tmp_path)
    target = staging / "pyproject.toml"
    target.write_text(target.read_text(encoding="utf-8") + "\n# tampered\n", encoding="utf-8")
    result = _validate(staging)
    assert result == 1


def test_handoff_knowledge_file_mutation_fails_closed(tmp_path):
    """The exact mutation scenario named in §27.6: mutate
    planning/documentation-handoff/knowledge/overview.md inside the
    staged tree and confirm validation fails -- entirely self-contained,
    no access to the parent repository."""
    staging = _build(tmp_path)
    candidates = list((staging / "planning" / "documentation-handoff").rglob("*.md"))
    assert candidates, "expected at least one handoff knowledge file in a real build"
    target = candidates[0]
    target.write_text(target.read_text(encoding="utf-8") + "\nTAMPERED\n", encoding="utf-8")
    assert _validate(staging) == 1


def test_test_file_mutation_fails_closed(tmp_path):
    staging = _build(tmp_path)
    target = staging / "tests" / "fixtures" / "sample_readme.md"
    assert target.is_file()
    target.write_text("tampered fixture content\n", encoding="utf-8")
    assert _validate(staging) == 1


def test_source_file_mutation_fails_closed(tmp_path):
    staging = _build(tmp_path)
    py_files = list((staging / "src").rglob("*.py"))
    assert py_files
    target = py_files[0]
    target.write_text(target.read_text(encoding="utf-8") + "\n# tampered\n", encoding="utf-8")
    assert _validate(staging) == 1


def test_manifest_payload_tree_sha256_tampering_fails_closed(tmp_path):
    """Manifest-internal inconsistency: hand-edit the recorded top-level
    digest without touching any payload file. The validator must detect
    this purely from the manifest's own internal consistency (§27.1
    item 4 / §27.3 item 3's "manifest tampering/inconsistency" class)."""
    staging = _build(tmp_path)
    manifest_path = staging / "CLEANROOM-MANIFEST.yaml"
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    manifest["payload_tree_sha256"] = "0" * 64
    manifest_path.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
    assert _validate(staging) == 1


def test_validate_never_reads_outside_the_staging_tree(tmp_path, monkeypatch):
    """Validation must be self-contained: moving the staged tree to an
    isolated location with the parent repository entirely out of reach
    (simulated by monkeypatching ROOT to a nonexistent path) must not
    change the validation outcome."""
    staging = _build(tmp_path)
    monkeypatch.setattr(prepare_cleanroom_branch, "ROOT", Path("/nonexistent-parent-repo"))
    assert _validate(staging) == 0


def test_manifest_schema_version_and_no_self_referential_commit_field(tmp_path):
    """Handoff-identity corrective (§27.1 item 3 / §27.3 item 4): the
    manifest no longer tries to name its own commit SHA. It records
    documented_revision, payload_tree_sha256, and manifest_schema_version
    instead -- all computable before any commit exists."""
    staging = _build(tmp_path)
    manifest = yaml.safe_load((staging / "CLEANROOM-MANIFEST.yaml").read_text(encoding="utf-8"))
    assert manifest["manifest_schema_version"] == prepare_cleanroom_branch.MANIFEST_SCHEMA_VERSION
    assert "handoff_commit" not in manifest
    assert len(manifest["payload_tree_sha256"]) == 64
    assert manifest["documented_revision"] == _real_head_revision()


# ---------------------------------------------------------------------------
# Exact-revision export (§27.1 item 2 / §27.3 item 1)
# ---------------------------------------------------------------------------


def _init_scratch_repo(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init", "-q"], cwd=path, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=path, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=path, check=True)
    subprocess.run(["git", "config", "commit.gpgsign", "false"], cwd=path, check=True)


def _commit_all(path: Path, message: str) -> str:
    subprocess.run(["git", "add", "-A"], cwd=path, check=True)
    subprocess.run(["git", "commit", "-q", "-m", message], cwd=path, check=True)
    return subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=path, capture_output=True, text=True, check=True
    ).stdout.strip()


def test_export_reads_committed_content_not_a_dirty_working_tree(tmp_path):
    repo = tmp_path / "scratch_repo"
    _init_scratch_repo(repo)
    (repo / "src").mkdir()
    (repo / "src" / "a.py").write_text("committed content\n", encoding="utf-8")
    rev = _commit_all(repo, "c1")

    # Dirty the working tree *after* recording the revision we will export.
    (repo / "src" / "a.py").write_text("DIRTY UNCOMMITTED CONTENT\n", encoding="utf-8")

    staging = tmp_path / "staging"
    staging.mkdir()
    included = prepare_cleanroom_branch._export_path(repo, rev, "src", staging)
    assert included == ["src/a.py"]
    assert (staging / "src" / "a.py").read_text(encoding="utf-8") == "committed content\n"


def test_export_does_not_leak_a_later_commit_into_an_earlier_revisions_export(tmp_path):
    repo = tmp_path / "scratch_repo"
    _init_scratch_repo(repo)
    (repo / "src").mkdir()
    (repo / "src" / "a.py").write_text("v1\n", encoding="utf-8")
    rev1 = _commit_all(repo, "c1")

    (repo / "src" / "b.py").write_text("added later\n", encoding="utf-8")
    _commit_all(repo, "c2")

    staging = tmp_path / "staging"
    staging.mkdir()
    included = prepare_cleanroom_branch._export_path(repo, rev1, "src", staging)
    assert sorted(included) == ["src/a.py"]
    assert not (staging / "src" / "b.py").exists()


def test_export_fails_closed_for_an_unresolvable_revision(tmp_path):
    repo = tmp_path / "scratch_repo"
    _init_scratch_repo(repo)
    (repo / "f.txt").write_text("x\n", encoding="utf-8")
    _commit_all(repo, "c1")

    with pytest.raises(prepare_cleanroom_branch.CleanroomExportError):
        prepare_cleanroom_branch._require_commit_exists(repo, "0" * 40)


def test_cmd_build_fails_closed_for_an_unresolvable_documented_revision(tmp_path):
    staging = tmp_path / "staging"
    args = type(
        "Args",
        (),
        {"staging": str(staging), "documented_revision": "0" * 40, "slugs": ""},
    )()
    assert prepare_cleanroom_branch.cmd_build(args) == 1
    assert not staging.exists()


def test_submodule_export_uses_the_pinned_gitlink_not_the_checked_out_head(tmp_path):
    """Regression test proving submodule content comes from the exact
    gitlink SHA the superproject recorded at `documented_revision`, even
    when the submodule's own working copy has since been checked out to
    a later commit locally (§27.1 item 2 / §27.3 item 1)."""
    sub = tmp_path / "sub_repo"
    _init_scratch_repo(sub)
    (sub / "lib.py").write_text("v1\n", encoding="utf-8")
    sha_v1 = _commit_all(sub, "sub c1")

    superproject = tmp_path / "super_repo"
    _init_scratch_repo(superproject)
    subprocess.run(
        ["git", "-c", "protocol.file.allow=always", "submodule", "add", str(sub), "vendor_sub"],
        cwd=superproject,
        check=True,
    )
    rev_super = _commit_all(superproject, "super c1 (pins vendor_sub at v1)")

    # Advance the submodule's own history AND the superproject's locally
    # checked-out submodule copy to v2, without committing a new gitlink
    # update in the superproject -- simulates local checkout drift.
    (sub / "lib.py").write_text("v2\n", encoding="utf-8")
    sha_v2 = _commit_all(sub, "sub c2")
    subprocess.run(["git", "fetch", "-q", "origin"], cwd=superproject / "vendor_sub", check=True)
    subprocess.run(["git", "checkout", "-q", sha_v2], cwd=superproject / "vendor_sub", check=True)

    gitlink = prepare_cleanroom_branch._submodule_gitlink_sha(superproject, "vendor_sub", rev_super)
    assert gitlink == sha_v1
    assert gitlink != sha_v2

    staging = tmp_path / "staging"
    staging.mkdir()
    included = prepare_cleanroom_branch._export_path(
        superproject / "vendor_sub", gitlink, ".", staging, dest_prefix="vendor_sub"
    )
    assert included == ["vendor_sub/lib.py"]
    assert (staging / "vendor_sub" / "lib.py").read_text(encoding="utf-8") == "v1\n"


def test_submodule_export_fails_closed_when_gitlink_object_is_unavailable(tmp_path):
    """If the submodule's own local object database does not contain the
    pinned gitlink commit (e.g. it was never fetched), the export must
    fail closed rather than silently substituting whatever the submodule
    currently has checked out (§27.1 item 2 / §27.3 item 1)."""
    sub = tmp_path / "sub_repo"
    _init_scratch_repo(sub)
    (sub / "lib.py").write_text("v1\n", encoding="utf-8")
    _commit_all(sub, "sub c1")

    with pytest.raises(prepare_cleanroom_branch.CleanroomExportError):
        prepare_cleanroom_branch._require_commit_exists(sub, "f" * 40)


def test_git_tracked_files_at_revision_resolves_paths_inside_a_real_submodule(tmp_path):
    """Regression test for a real bug this phase's own cold-reader
    testing found: a directory inside a Git submodule (e.g.
    protocol/codecompass-adaptor-protocol/schemas) is invisible to
    `git ls-tree` run from the superproject's own root, since the
    superproject only tracks the submodule as a single gitlink entry.
    Exercised against the real repository's own real submodule."""
    submodule_rel = "protocol/codecompass-adaptor-protocol"
    sub_repo_root = REPO_ROOT / submodule_rel
    assert (sub_repo_root / ".git").exists(), (
        "fixture assumption broken: this is no longer a real submodule checkout"
    )
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=sub_repo_root, capture_output=True, text=True, check=True
    ).stdout.strip()
    tracked = prepare_cleanroom_branch._git_tracked_files_at_revision(
        sub_repo_root, head, "schemas"
    )
    assert tracked, "expected real tracked files inside the submodule's schemas/ directory"
    for t in tracked:
        assert (sub_repo_root / t).is_file()


def test_build_includes_real_haskell_adapter_source(tmp_path):
    """Regression test for a real cold-reader finding: the Haskell
    external-adapter's own Requirements/Claims describe exact scanning
    behaviour of code that, before this fix, was entirely excluded from
    the writer's workspace -- leaving nothing to verify those
    Requirements against. Narrative files (README/CHANGELOG/LICENSE)
    stay excluded, matching the protocol submodule's own treatment."""
    staging = _build(tmp_path)
    assert (staging / "adapters" / "haskell" / "app" / "Main.hs").is_file()
    assert (staging / "adapters" / "haskell" / "test" / "Spec.hs").is_file()
    assert (staging / "adapters" / "haskell" / "codecompass-adaptor-haskell.cabal").is_file()
    assert not (staging / "adapters" / "haskell" / "README.md").exists()
    assert not (staging / "adapters" / "haskell" / "CHANGELOG.md").exists()
    assert not (staging / "adapters" / "haskell" / "LICENSE").exists()
    assert not (staging / "adapters" / "haskell" / ".git").exists()


def test_build_excludes_gitignored_regenerated_fixture_artifacts(tmp_path):
    """Regression test for the real bug this phase's own investigation
    found: a raw filesystem walk once silently included local,
    `.gitignore`d, regenerated test-fixture artifacts that exist on disk
    but are not tracked by Git at all. Exact-revision export via
    `git ls-tree` makes this structurally impossible now (there is no
    filesystem walk left to regress), confirmed against the real fixture
    directory's own real `.gitignore`."""
    gitignore = (
        REPO_ROOT / "tests" / "fixtures" / "ledgerkit_lifecycle_demo" / ".gitignore"
    ).read_text(encoding="utf-8")
    assert "CLAUDE.md" in gitignore, "fixture assumption broken: expected these to stay gitignored"
    staging = _build(tmp_path)
    assert not (staging / "tests" / "fixtures" / "ledgerkit_lifecycle_demo" / "CLAUDE.md").exists()
    assert not (
        staging / "tests" / "fixtures" / "ledgerkit_lifecycle_demo" / "context-graph.db"
    ).exists()
    assert not (
        staging / "tests" / "fixtures" / "ledgerkit_lifecycle_demo" / "vendor.toml"
    ).exists()


def test_build_includes_gitmodules(tmp_path):
    """Regression test: a cold-reader finding noted the real remote URL
    for the Haskell adapter submodule was never visible anywhere in the
    writer's workspace, even though .gitmodules states it plainly and
    is pure structural config, not narrative."""
    staging = _build(tmp_path)
    gitmodules = staging / ".gitmodules"
    assert gitmodules.is_file()
    assert "codecompass-adaptor-haskell" in gitmodules.read_text(encoding="utf-8")


def test_allow_list_contains_no_narrative_documentation_paths():
    """Amendment 2/3: README.md/docs/**/architecture/**/ai-docs/** (and
    docs/domain/** specifically) must never appear in the allow-list
    itself -- a structural guard against the allow-list silently growing
    to include narrative documentation later."""
    excluded_prefixes = (
        "README.md", "docs", "architecture", "ai-docs", "CONTRIBUTING.md", "CLAUDE.md",
    )
    for allowed in prepare_cleanroom_branch.ALLOW_PATHS:
        assert not any(
            allowed == p or allowed.startswith(p + "/") for p in excluded_prefixes
        ), f"narrative-documentation-shaped path leaked into ALLOW_PATHS: {allowed}"


# ---------------------------------------------------------------------------
# File-level narrative exclusion for broad allow-listed directories
# (§27.1 item 1 / §27.3 item 2)
# ---------------------------------------------------------------------------


def test_known_narrative_fixture_leaks_are_excluded_from_a_real_build(tmp_path):
    """The six real leaks Amendment 5's own review found: a project-
    process README and four narrative fixture docs beneath the broadly
    allow-listed tests/** tree."""
    staging = _build(tmp_path)
    for rel in prepare_cleanroom_branch._CLASSIFIED_EXCLUDE_DOC_PATHS:
        assert not (staging / rel).exists(), f"narrative leak not excluded: {rel}"


def test_required_structural_fixtures_remain_present(tmp_path):
    """Excluding narrative prose must not blanket-exclude genuine
    structural/machine-fixture/test-evidence doc-shaped files."""
    staging = _build(tmp_path)
    for rel in prepare_cleanroom_branch._CLASSIFIED_KEEP_DOC_PATHS:
        assert (staging / rel).is_file(), f"required structural fixture missing: {rel}"
    # And the executable test module that actually exercises one of them.
    assert (staging / "tests" / "test_adapter_npm.py").is_file()


def test_unclassified_narrative_shaped_file_fails_closed():
    """A brand-new, never-reviewed doc-shaped file beneath a broad
    allow-listed directory must fail the build closed rather than
    silently riding along either way."""
    with pytest.raises(prepare_cleanroom_branch.UnclassifiedNarrativeShapedFileError):
        prepare_cleanroom_branch._filter_narrative_shaped(
            ["tests/fixtures/brand_new_unreviewed_notes.md"], "tests"
        )


def test_filter_narrative_shaped_passes_through_non_doc_shaped_files():
    kept = prepare_cleanroom_branch._filter_narrative_shaped(
        ["tests/test_something.py", "tests/fixtures/data.json"], "tests"
    )
    assert kept == ["tests/test_something.py", "tests/fixtures/data.json"]


def test_classified_keep_and_exclude_sets_are_disjoint():
    overlap = (
        prepare_cleanroom_branch._CLASSIFIED_KEEP_DOC_PATHS
        & prepare_cleanroom_branch._CLASSIFIED_EXCLUDE_DOC_PATHS
    )
    assert not overlap


def test_cmd_build_fails_closed_end_to_end_for_an_unclassified_narrative_file(
    tmp_path, monkeypatch
):
    """End-to-end, through the real `cmd_build` entrypoint (not just the
    inner classification helper): a scratch repository with a brand-new,
    never-reviewed doc-shaped file inside a broad allow-listed directory
    must make the whole build fail closed, leaving no partial staging
    tree behind."""
    repo = tmp_path / "scratch_repo"
    _init_scratch_repo(repo)
    (repo / "tests").mkdir()
    (repo / "tests" / "test_x.py").write_text("# a real test module\n", encoding="utf-8")
    (repo / "tests" / "unreviewed_notes.md").write_text(
        "# some new, never-classified doc\n", encoding="utf-8"
    )
    rev = _commit_all(repo, "c1")

    monkeypatch.setattr(prepare_cleanroom_branch, "ALLOW_PATHS", ["tests"])
    monkeypatch.setattr(prepare_cleanroom_branch, "ROOT", repo)

    staging = tmp_path / "staging"
    args = type("Args", (), {"staging": str(staging), "documented_revision": rev, "slugs": ""})()
    assert prepare_cleanroom_branch.cmd_build(args) == 1
    assert not staging.exists()
