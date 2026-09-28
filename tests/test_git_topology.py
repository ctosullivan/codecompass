import subprocess
from pathlib import Path

import pytest

from codecompass.git_topology import (
    TopologyStatus,
    detect_git_topology,
    sanitize_git_url,
)


def _git(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args], cwd=cwd, capture_output=True, text=True, check=True
    )


def _init_repo(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    _git(["init", "-q"], path)
    _git(["config", "user.email", "test@example.com"], path)
    _git(["config", "user.name", "Test"], path)


def _commit(path: Path, message: str = "commit") -> str:
    _git(["add", "-A"], path)
    _git(["commit", "-q", "-m", message], path)
    result = _git(["rev-parse", "HEAD"], path)
    return result.stdout.strip()


# --- Whole-pass status -------------------------------------------------------


def test_not_a_git_repository(tmp_path) -> None:
    topo = detect_git_topology(tmp_path)
    assert topo.status == TopologyStatus.NOT_GIT
    assert topo.reason is None
    assert topo.worktree_root is None
    assert topo.common_dir is None
    assert topo.worktrees == ()
    assert topo.submodules == ()


def test_git_binary_missing(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr("codecompass.git_topology.shutil.which", lambda _name: None)
    topo = detect_git_topology(tmp_path)
    assert topo.status == TopologyStatus.UNAVAILABLE
    assert "not found" in topo.reason


def test_rev_parse_failure_unrelated_to_not_a_repository_is_unavailable(
    tmp_path, monkeypatch
) -> None:
    class _FakeResult:
        returncode = 128
        stdout = ""
        stderr = "fatal: some unexpected permission error"

    def _fake_run(*args, **kwargs):
        return _FakeResult()

    monkeypatch.setattr("codecompass.git_topology.subprocess.run", _fake_run)
    topo = detect_git_topology(tmp_path)
    assert topo.status == TopologyStatus.UNAVAILABLE
    assert "permission" in topo.reason
    assert topo.status != TopologyStatus.NOT_GIT


def test_unrecognized_option_from_an_old_git_is_unavailable_not_not_git(
    tmp_path, monkeypatch
) -> None:
    """Second amendment regression: a Git too old to know --git-common-dir
    must classify as UNAVAILABLE (with the raw message surfaced), never
    NOT_GIT."""

    class _FakeResult:
        returncode = 129
        stdout = ""
        stderr = "error: unknown option `git-common-dir'\nusage: git rev-parse ..."

    def _fake_run(*args, **kwargs):
        return _FakeResult()

    monkeypatch.setattr("codecompass.git_topology.subprocess.run", _fake_run)
    topo = detect_git_topology(tmp_path)
    assert topo.status == TopologyStatus.UNAVAILABLE
    assert "unknown option" in topo.reason


def test_bare_repository_is_unavailable_not_a_crash(tmp_path) -> None:
    bare = tmp_path / "bare.git"
    _git(["init", "-q", "--bare", str(bare)], tmp_path)
    topo = detect_git_topology(bare)
    assert topo.status == TopologyStatus.UNAVAILABLE
    assert "bare repository" in topo.reason
    assert topo.worktrees == ()


def test_single_worktree_clean_repo(tmp_path) -> None:
    repo = tmp_path / "repo"
    _init_repo(repo)
    (repo / "a.txt").write_text("hello")
    sha = _commit(repo)

    topo = detect_git_topology(repo)
    assert topo.status == TopologyStatus.DETECTED
    assert topo.worktree_root == str(repo.resolve())
    assert topo.common_dir == str((repo / ".git").resolve())
    assert len(topo.worktrees) == 1
    w = topo.worktrees[0]
    assert w.is_current is True
    assert w.branch in ("main", "master")
    assert w.head_commit == sha
    assert w.is_dirty is False
    assert topo.submodules == ()


def test_detect_git_topology_from_root_and_nested_subdirectory_agree(tmp_path) -> None:
    """Core regression for the invocation-root/worktree-root distinction:
    invoking from a real nested subdirectory must resolve the identical
    worktree_root/common_dir as invoking from the repository root -- the
    relative `--git-common-dir` output from the subdirectory case must be
    manually resolved correctly, with no `--path-format` flag involved."""
    repo = tmp_path / "repo"
    _init_repo(repo)
    nested = repo / "src" / "pkg"
    nested.mkdir(parents=True)
    (nested / "mod.py").write_text("x = 1")
    _commit(repo)

    from_root = detect_git_topology(repo)
    from_nested = detect_git_topology(nested)

    assert from_root.common_dir == from_nested.common_dir
    assert from_root.worktree_root == from_nested.worktree_root
    assert from_nested.worktree_root == str(repo.resolve())


def test_dirty_tracked_edit(tmp_path) -> None:
    repo = tmp_path / "repo"
    _init_repo(repo)
    (repo / "a.txt").write_text("hello")
    _commit(repo)
    (repo / "a.txt").write_text("changed")

    topo = detect_git_topology(repo)
    assert topo.worktrees[0].is_dirty is True


def test_dirty_untracked_only_change(tmp_path) -> None:
    repo = tmp_path / "repo"
    _init_repo(repo)
    (repo / "a.txt").write_text("hello")
    _commit(repo)
    (repo / "untracked.txt").write_text("new")

    topo = detect_git_topology(repo)
    assert topo.worktrees[0].is_dirty is True


def test_detached_head(tmp_path) -> None:
    repo = tmp_path / "repo"
    _init_repo(repo)
    (repo / "a.txt").write_text("hello")
    sha = _commit(repo)
    _git(["checkout", "-q", "--detach", sha], repo)

    topo = detect_git_topology(repo)
    w = topo.worktrees[0]
    assert w.is_detached is True
    assert w.branch is None
    assert w.head_commit == sha


def test_unborn_branch_no_commits_yet(tmp_path) -> None:
    repo = tmp_path / "repo"
    _init_repo(repo)

    topo = detect_git_topology(repo)
    assert topo.status == TopologyStatus.DETECTED
    w = topo.worktrees[0]
    assert w.head_commit is None


def test_two_real_worktrees_share_common_dir(tmp_path) -> None:
    repo = tmp_path / "repo"
    _init_repo(repo)
    (repo / "a.txt").write_text("hello")
    _commit(repo)
    other = tmp_path / "other-worktree"
    _git(["worktree", "add", "-q", str(other), "-b", "feature"], repo)

    from_main = detect_git_topology(repo)
    from_other = detect_git_topology(other)

    assert from_main.common_dir == from_other.common_dir
    assert len(from_main.worktrees) == 2
    assert len(from_other.worktrees) == 2

    main_current = next(w for w in from_main.worktrees if w.is_current)
    assert main_current.path == str(repo.resolve())
    other_current = next(w for w in from_other.worktrees if w.is_current)
    assert other_current.path == str(other.resolve())
    assert other_current.branch == "feature"

    # The sibling in either direction is never probed for dirty state.
    main_sibling = next(w for w in from_main.worktrees if not w.is_current)
    assert main_sibling.is_dirty is None


def test_prunable_worktree(tmp_path) -> None:
    repo = tmp_path / "repo"
    _init_repo(repo)
    (repo / "a.txt").write_text("hello")
    _commit(repo)
    other = tmp_path / "gone-worktree"
    _git(["worktree", "add", "-q", str(other), "-b", "feature"], repo)
    import shutil as _shutil

    _shutil.rmtree(other)

    topo = detect_git_topology(repo)
    sibling = next(w for w in topo.worktrees if not w.is_current)
    assert sibling.is_prunable is True


def test_branch_name_is_short_form_not_full_ref(tmp_path) -> None:
    repo = tmp_path / "repo"
    _init_repo(repo)
    (repo / "a.txt").write_text("hello")
    _commit(repo)
    _git(["checkout", "-q", "-b", "feature-x"], repo)

    topo = detect_git_topology(repo)
    assert topo.worktrees[0].branch == "feature-x"
    assert "refs/heads" not in topo.worktrees[0].branch


def test_worktree_list_failure_yields_partial(tmp_path, monkeypatch) -> None:
    repo = tmp_path / "repo"
    _init_repo(repo)
    (repo / "a.txt").write_text("hello")
    _commit(repo)

    import codecompass.git_topology as gt

    real_run_git = gt._run_git

    def _fake_run_git(args, cwd):
        if args[:2] == ["worktree", "list"]:
            raise OSError("boom")
        return real_run_git(args, cwd)

    monkeypatch.setattr(gt, "_run_git", _fake_run_git)
    topo = detect_git_topology(repo)
    assert topo.status == TopologyStatus.PARTIAL
    assert "worktrees" in topo.reason
    assert topo.worktrees == ()


# --- Submodules ---------------------------------------------------------------


def _make_submodule_source(tmp_path: Path) -> Path:
    source = tmp_path / "submodule-source"
    _init_repo(source)
    (source / "lib.txt").write_text("v1")
    _commit(source, "v1")
    (source / "lib.txt").write_text("v2")
    _commit(source, "v2")
    return source


def test_submodule_fully_in_sync(tmp_path) -> None:
    source = _make_submodule_source(tmp_path)
    repo = tmp_path / "repo"
    _init_repo(repo)
    _git(["-c", "protocol.file.allow=always", "submodule", "add", "-q", str(source), "sub"], repo)
    _commit(repo, "add submodule")

    topo = detect_git_topology(repo)
    assert len(topo.submodules) == 1
    s = topo.submodules[0]
    assert s.path == "sub"
    assert s.is_path_safe is True
    assert s.is_initialized is True
    assert s.pinned_commit == s.checked_out_commit
    assert s.revision_matches_pin is True


def test_submodule_checked_out_behind_its_pin(tmp_path) -> None:
    source = _make_submodule_source(tmp_path)
    repo = tmp_path / "repo"
    _init_repo(repo)
    _git(["-c", "protocol.file.allow=always", "submodule", "add", "-q", str(source), "sub"], repo)
    _commit(repo, "add submodule")

    sub_path = repo / "sub"
    _git(["checkout", "-q", "HEAD~1"], sub_path)

    topo = detect_git_topology(repo)
    s = topo.submodules[0]
    assert s.pinned_commit != s.checked_out_commit
    assert s.revision_matches_pin is False
    assert s.pinned_commit is not None
    assert s.checked_out_commit is not None


def test_submodule_never_initialized(tmp_path) -> None:
    source = _make_submodule_source(tmp_path)
    repo = tmp_path / "repo"
    _init_repo(repo)
    _git(["-c", "protocol.file.allow=always", "submodule", "add", "-q", str(source), "sub"], repo)
    _commit(repo, "add submodule")
    _git(["submodule", "deinit", "-q", "-f", "sub"], repo)
    import shutil as _shutil

    _shutil.rmtree(repo / "sub", ignore_errors=True)
    (repo / "sub").mkdir()

    topo = detect_git_topology(repo)
    s = topo.submodules[0]
    assert s.is_initialized is False
    assert s.pinned_commit is not None
    assert s.checked_out_commit is None
    assert s.revision_matches_pin is None
    assert s.child_branch is None
    assert s.child_is_dirty is None


def test_submodule_declared_but_no_gitlink_in_head_tree(tmp_path) -> None:
    """A .gitmodules entry with no corresponding gitlink committed yet (a
    real, mid-edit state) still produces a row -- never omitted."""
    repo = tmp_path / "repo"
    _init_repo(repo)
    (repo / ".gitmodules").write_text(
        '[submodule "sub"]\n\tpath = sub\n\turl = https://example.com/sub.git\n'
    )
    _commit(repo, "declare submodule without gitlink")

    topo = detect_git_topology(repo)
    assert len(topo.submodules) == 1
    s = topo.submodules[0]
    assert s.path == "sub"
    assert s.pinned_commit is None
    assert s.revision_matches_pin is None


def test_submodule_path_escaping_worktree_root_is_refused(tmp_path, monkeypatch) -> None:
    repo = tmp_path / "repo"
    _init_repo(repo)
    (repo / ".gitmodules").write_text(
        '[submodule "evil"]\n\tpath = ../../../etc\n\turl = https://example.com/evil.git\n'
    )
    _commit(repo, "malicious gitmodules")

    calls: list[list[str]] = []
    import codecompass.git_topology as gt

    real_run_git = gt._run_git

    def _spy_run_git(args, cwd):
        calls.append(args)
        return real_run_git(args, cwd)

    monkeypatch.setattr(gt, "_run_git", _spy_run_git)
    topo = detect_git_topology(repo)

    assert len(topo.submodules) == 1
    s = topo.submodules[0]
    assert s.is_path_safe is False
    assert s.pinned_commit is None
    assert s.is_initialized is None

    escaping = str((repo / "../../../etc").resolve())
    for args in calls:
        assert escaping not in args
        # None of the calls should have `cwd` pointed at the escaping path
        # either -- checked via the recorded args not naming it anywhere.


def test_submodule_path_absolute_is_refused(tmp_path) -> None:
    repo = tmp_path / "repo"
    _init_repo(repo)
    (repo / ".gitmodules").write_text(
        f'[submodule "evil"]\n\tpath = {tmp_path / "outside"}\n\turl = https://example.com/evil.git\n'
    )
    _commit(repo, "absolute path gitmodules")

    topo = detect_git_topology(repo)
    assert len(topo.submodules) == 1
    assert topo.submodules[0].is_path_safe is False


def test_submodule_credential_bearing_url_is_sanitized(tmp_path) -> None:
    repo = tmp_path / "repo"
    _init_repo(repo)
    (repo / ".gitmodules").write_text(
        '[submodule "sub"]\n\tpath = sub\n\turl = https://user:secret@example.com/sub.git\n'
    )
    _commit(repo, "declare submodule with credential url")

    topo = detect_git_topology(repo)
    assert topo.submodules[0].child_repository_url == "https://example.com/sub.git"
    assert "secret" not in (topo.submodules[0].child_repository_url or "")


# --- URL sanitization ---------------------------------------------------------


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        ("https://user:password@host/repo.git", "https://host/repo.git"),
        ("https://TOKEN@host/repo.git", "https://host/repo.git"),
        ("ssh://user:password@host/repo.git", "ssh://user@host/repo.git"),
        ("ssh://git@host/repo.git", "ssh://git@host/repo.git"),
        ("git@host:org/repo.git", "git@host:org/repo.git"),
        ("https://host/repo.git", "https://host/repo.git"),
        ("https://user:pass@host:8443/repo.git", "https://host:8443/repo.git"),
        (
            "git@github.com:ctosullivan/codecompass-adaptor-haskell.git",
            "git@github.com:ctosullivan/codecompass-adaptor-haskell.git",
        ),
    ],
)
def test_sanitize_git_url(url, expected) -> None:
    assert sanitize_git_url(url) == expected
