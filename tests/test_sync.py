import shutil
from pathlib import Path

import pytest

import codecompass.sync as sync_module
from codecompass.core import DepNode, Ecosystem, RepositoryLocation, VendorConfig
from codecompass.graph import open_graph, record_enrichment, unused_vendors, vendor_profile
from codecompass.source_resolution import SourceResolutionError
from codecompass.sync import rebuild_project_graph, sync_all, sync_vendor


class _FakeAdapter:
    def __init__(
        self,
        config: VendorConfig,
        project_root: Path,
        *,
        version: str = "1.0.0",
        api_surface: str = "some_fn: does a thing.",
        tree: DepNode | None = None,
        source_dir: Path | None = None,
        repository: RepositoryLocation | None = None,
    ) -> None:
        self.config = config
        self.project_root = project_root
        self._version = version
        self._api_surface = api_surface
        self._tree = tree or DepNode(name=config.name, version=version)
        self._source_dir = source_dir or project_root
        self._repository = repository

    def installed_version(self) -> str:
        return self._version

    def source_location(self) -> Path:
        return self._source_dir

    def readme_and_api_surface(self) -> str:
        return self._api_surface

    def dependency_tree(self) -> DepNode:
        return self._tree

    def repository_url(self) -> RepositoryLocation | None:
        return self._repository


def _build_source_tree(root: Path) -> Path:
    src = root / "pkgsrc"
    (src).mkdir()
    (src / "__init__.py").write_text(
        '"""Entry point for the demo package."""\n\ndef main() -> None:\n    pass\n',
        encoding="utf-8",
    )
    (src / "tests").mkdir()
    (src / "tests" / "test_thing.py").write_text("def test_thing(): ...\n", encoding="utf-8")
    (src / "dist").mkdir()
    (src / "dist" / "bundle.js").write_text("built\n", encoding="utf-8")
    return src


def _patch_adapter(monkeypatch: pytest.MonkeyPatch, **adapter_kwargs: object) -> None:
    monkeypatch.setattr(
        sync_module,
        "get_adapter",
        lambda config, project_root: _FakeAdapter(config, project_root, **adapter_kwargs),
    )


def _fake_clone(fake_repo: Path):
    def _resolve_and_clone(adapter, dest: Path) -> Path:
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(fake_repo, dest)
        return dest

    return _resolve_and_clone


def _build_fake_repo(root: Path) -> Path:
    fake_repo = root / "fake_repo"
    fake_repo.mkdir()
    (fake_repo / "README.md").write_text("This is the readme.", encoding="utf-8")
    return fake_repo


def _record_enrichment_for(
    project_root: Path,
    vendor_name: str,
    *,
    ecosystem: str = "python",
    technical_description: str = "Grounded technical description.",
    conversational_overview: str = "Friendly overview.",
    action_pointer_file: str | None = None,
    action_pointer_note: str | None = None,
) -> None:
    """Write a `vendor_enrichment` row directly against `context-graph.db`
    — the state `sync_vendor`'s new graph lookup (Phase 16, decisions/0035)
    reads back, standing in for a real Phase B enrichment run.
    """
    conn = open_graph(project_root)
    try:
        conn.execute(
            "INSERT OR IGNORE INTO vendors (name, ecosystem) VALUES (?, ?)",
            (vendor_name, ecosystem),
        )
        conn.commit()
        (vendor_id,) = conn.execute(
            "SELECT id FROM vendors WHERE name = ?", (vendor_name,)
        ).fetchone()
        record_enrichment(
            conn,
            vendor_id,
            technical_description=technical_description,
            conversational_overview=conversational_overview,
            action_pointer_file=action_pointer_file,
            action_pointer_note=action_pointer_note,
            symbol_set_hash="fake-hash",
            model="claude-haiku-4-5-20251001",
            generated_at="2026-01-01T00:00:00+00:00",
        )
    finally:
        conn.close()


def test_sync_vendor_writes_all_five_output_files(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    src = _build_source_tree(tmp_path)
    _patch_adapter(monkeypatch, version="2.0.0", source_dir=src)
    config = VendorConfig(name="demo", ecosystem=Ecosystem.PYTHON)

    digest = sync_vendor(config, tmp_path)

    vendor_dir = tmp_path / "vendor" / "demo"
    for filename in ("FILETREE.md", "DEPTREE.md", "filetree.json", "deptree.json", "CLAUDE.md"):
        assert (vendor_dir / filename).exists(), filename

    assert digest.installed_version == "2.0.0"
    claude_md = (vendor_dir / "CLAUDE.md").read_text(encoding="utf-8")
    assert "- **Installed version:** 2.0.0" in claude_md.splitlines()


def test_sync_vendor_omits_test_dirs_from_filetree(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    src = _build_source_tree(tmp_path)
    _patch_adapter(monkeypatch, source_dir=src)
    config = VendorConfig(name="demo", ecosystem=Ecosystem.PYTHON)

    sync_vendor(config, tmp_path)

    filetree_md = (tmp_path / "vendor" / "demo" / "FILETREE.md").read_text(encoding="utf-8")
    assert "test_thing.py" not in filetree_md
    assert "bundle.js" not in filetree_md
    assert "__init__.py" in filetree_md


def test_sync_vendor_clones_repo_into_src(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Cloning is unconditional (Phase 13, decisions/0033) — every vendor
    gets a real `src/` clone attempt, independent of enrichment status.
    """
    src = _build_source_tree(tmp_path)
    _patch_adapter(monkeypatch, source_dir=src)
    fake_repo = _build_fake_repo(tmp_path)
    monkeypatch.setattr(sync_module, "resolve_and_clone", _fake_clone(fake_repo))
    config = VendorConfig(name="demo", ecosystem=Ecosystem.PYTHON)

    digest = sync_vendor(config, tmp_path)

    snapshot = tmp_path / "vendor" / "demo" / "src"
    assert (snapshot / "README.md").exists()
    assert digest.technical_description is None
    assert digest.description_error is None
    assert not (tmp_path / "vendor" / "demo" / "OVERVIEW.md").exists()


def test_sync_vendor_filetree_reflects_clone_not_local_install(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """FILETREE.md renders from the clone root when cloning succeeds, for
    every vendor (Phase 13) — a real, visible output change from always
    reading `source_location()`.
    """
    src = _build_source_tree(tmp_path)
    _patch_adapter(monkeypatch, source_dir=src)
    fake_repo = _build_fake_repo(tmp_path)
    monkeypatch.setattr(sync_module, "resolve_and_clone", _fake_clone(fake_repo))
    config = VendorConfig(name="demo", ecosystem=Ecosystem.PYTHON)

    sync_vendor(config, tmp_path)

    filetree_md = (tmp_path / "vendor" / "demo" / "FILETREE.md").read_text(encoding="utf-8")
    assert "README.md" in filetree_md
    assert "__init__.py" not in filetree_md  # local-install content, not in the clone


def test_sync_vendor_clone_failure_falls_back_to_local_snapshot(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    src = _build_source_tree(tmp_path)
    _patch_adapter(monkeypatch, source_dir=src)
    config = VendorConfig(name="demo", ecosystem=Ecosystem.PYTHON)

    digest = sync_vendor(config, tmp_path)  # should not raise; no repository configured

    snapshot = tmp_path / "vendor" / "demo" / "src"
    assert (snapshot / "tests" / "test_thing.py").exists()  # kept, unlike FILETREE.md
    assert not (snapshot / "dist").exists()  # stripped, same as FILETREE.md
    assert (snapshot / "__init__.py").exists()
    assert digest.description_error is not None
    assert digest.technical_description is None


def test_sync_vendor_is_idempotent_on_repeat_runs(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    src = _build_source_tree(tmp_path)
    _patch_adapter(monkeypatch, source_dir=src)
    fake_repo = _build_fake_repo(tmp_path)
    monkeypatch.setattr(sync_module, "resolve_and_clone", _fake_clone(fake_repo))
    config = VendorConfig(name="demo", ecosystem=Ecosystem.PYTHON)

    sync_vendor(config, tmp_path)
    sync_vendor(config, tmp_path)  # should not raise

    assert (tmp_path / "vendor" / "demo" / "src" / "README.md").exists()


def test_sync_vendor_known_gotchas_from_dependency_tree_side_effects(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    src = _build_source_tree(tmp_path)
    tree = DepNode(name="demo", version="1.0.0", side_effects=["postinstall: node build.js"])
    _patch_adapter(monkeypatch, source_dir=src, tree=tree)
    config = VendorConfig(name="demo", ecosystem=Ecosystem.PYTHON)

    digest = sync_vendor(config, tmp_path)

    assert digest.side_effects == ["postinstall: node build.js"]
    claude_md = (tmp_path / "vendor" / "demo" / "CLAUDE.md").read_text(encoding="utf-8")
    assert "- postinstall: node build.js" in claude_md.splitlines()


def test_sync_vendor_source_resolution_failure_falls_back_to_local_snapshot(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    src = _build_source_tree(tmp_path)
    _patch_adapter(monkeypatch, source_dir=src)

    def _raise(*args: object, **kwargs: object) -> None:
        raise SourceResolutionError("no repository found")

    monkeypatch.setattr(sync_module, "resolve_and_clone", _raise)
    config = VendorConfig(name="demo", ecosystem=Ecosystem.PYTHON)

    digest = sync_vendor(config, tmp_path)  # should not raise

    snapshot = tmp_path / "vendor" / "demo" / "src"
    assert (snapshot / "tests" / "test_thing.py").exists()  # kept, unlike FILETREE.md
    assert not (snapshot / "dist").exists()  # stripped, same as FILETREE.md
    assert (snapshot / "__init__.py").exists()
    assert digest.description_error == "no repository found"
    assert digest.technical_description is None
    vendor_dir = tmp_path / "vendor" / "demo"
    for filename in ("FILETREE.md", "DEPTREE.md", "filetree.json", "deptree.json", "CLAUDE.md"):
        assert (vendor_dir / filename).exists(), filename
    assert not (vendor_dir / "OVERVIEW.md").exists()


# --- graph-sourced enrichment (Phase 16, decisions/0035) --------------------


def test_sync_vendor_reads_enrichment_from_graph_and_reproduces_description(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Direct regression test for the bug decisions/0035 describes: a
    vendor with an existing `vendor_enrichment` row must have its
    Description section (and OVERVIEW.md) reproduced by an ordinary,
    from-scratch `sync_vendor` re-render — not silently erased, which is
    exactly what happened on `main` before this fix (a whole-project
    `sync` re-run used to blank out Phase B's enrichment output every
    time, since `sync_vendor`'s digest never carried it).
    """
    src = _build_source_tree(tmp_path)
    _patch_adapter(monkeypatch, source_dir=src)
    fake_repo = _build_fake_repo(tmp_path)
    monkeypatch.setattr(sync_module, "resolve_and_clone", _fake_clone(fake_repo))
    config = VendorConfig(name="demo", ecosystem=Ecosystem.PYTHON)

    _record_enrichment_for(
        tmp_path,
        "demo",
        technical_description="Grounded technical description.",
        conversational_overview="Friendly overview.",
        action_pointer_file="README.md",
        action_pointer_note="start here",
    )

    digest = sync_vendor(config, tmp_path)

    assert digest.technical_description == "Grounded technical description."
    assert digest.conversational_overview == "Friendly overview."
    assert digest.action_pointer_file == "README.md"
    assert digest.action_pointer_note == "start here"

    vendor_dir = tmp_path / "vendor" / "demo"
    claude_md = (vendor_dir / "CLAUDE.md").read_text(encoding="utf-8")
    assert "## Description" in claude_md
    assert "Grounded technical description." in claude_md
    assert (vendor_dir / "OVERVIEW.md").read_text(encoding="utf-8") == "Friendly overview."
    filetree_md = (vendor_dir / "FILETREE.md").read_text(encoding="utf-8")
    assert "← ACTION TARGET: start here" in filetree_md

    # An ordinary re-sync (no new enrichment, same graph state) reproduces
    # the same Description section rather than blanking it — the literal
    # regression the bug shipped as.
    digest_again = sync_vendor(config, tmp_path)
    assert digest_again.technical_description == "Grounded technical description."
    claude_md_again = (vendor_dir / "CLAUDE.md").read_text(encoding="utf-8")
    assert "## Description" in claude_md_again
    assert "Grounded technical description." in claude_md_again


def test_sync_vendor_no_enrichment_record_gets_no_description_section(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """A `context-graph.db` exists (e.g. from a prior whole-project sync)
    but carries no `vendor_enrichment` row for this vendor — same "nothing
    to show" outcome as today, not an error.
    """
    src = _build_source_tree(tmp_path)
    _patch_adapter(monkeypatch, source_dir=src)
    config = VendorConfig(name="demo", ecosystem=Ecosystem.PYTHON)

    conn = open_graph(tmp_path)
    conn.close()

    digest = sync_vendor(config, tmp_path)

    assert digest.technical_description is None
    claude_md = (tmp_path / "vendor" / "demo" / "CLAUDE.md").read_text(encoding="utf-8")
    assert "## Description" not in claude_md
    assert not (tmp_path / "vendor" / "demo" / "OVERVIEW.md").exists()


def test_sync_vendor_no_graph_at_all_gets_no_description_section(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """No `context-graph.db` yet (a project that's never run a
    whole-project sync) — the enrichment lookup is skipped gracefully,
    same posture as `index.py`'s existing "no graph yet" fallback. Crucially,
    `sync_vendor` itself must never create the file — only a real
    whole-project sync's `rebuild_project_graph` does that.
    """
    src = _build_source_tree(tmp_path)
    _patch_adapter(monkeypatch, source_dir=src)
    config = VendorConfig(name="demo", ecosystem=Ecosystem.PYTHON)

    assert not (tmp_path / "context-graph.db").exists()

    digest = sync_vendor(config, tmp_path)

    assert digest.technical_description is None
    assert not (tmp_path / "context-graph.db").exists()


def test_sync_all_syncs_every_config(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    src = _build_source_tree(tmp_path)
    _patch_adapter(monkeypatch, source_dir=src)
    configs = [
        VendorConfig(name="a", ecosystem=Ecosystem.PYTHON),
        VendorConfig(name="b", ecosystem=Ecosystem.PYTHON),
    ]

    digests = sync_all(configs, tmp_path)

    assert [d.config.name for d in digests] == ["a", "b"]
    assert (tmp_path / "vendor" / "a" / "CLAUDE.md").exists()
    assert (tmp_path / "vendor" / "b" / "CLAUDE.md").exists()


# --- rebuild_project_graph ----------------------------------------------------


def test_rebuild_project_graph_records_vendor_and_resolved_symbol_usage(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    src = tmp_path / "vendor_src"
    src.mkdir()
    (src / "__init__.py").write_text(
        '"""Demo vendor."""\n\ndef greet():\n    """Say hi."""\n    pass\n', encoding="utf-8"
    )
    monkeypatch.setattr(
        sync_module,
        "get_adapter",
        lambda config, project_root: _FakeAdapter(
            config,
            project_root,
            version="3.1.4",
            source_dir=src,
            repository=RepositoryLocation(url="https://example.com/demo.git"),
        ),
    )
    (tmp_path / "app.py").write_text("from demo import greet\n", encoding="utf-8")
    config = VendorConfig(name="demo", ecosystem=Ecosystem.PYTHON)

    rebuild_project_graph([config], tmp_path)

    conn = open_graph(tmp_path)
    profile = vendor_profile(conn, "demo")
    assert profile is not None
    assert profile["vendor"]["installed_version"] == "3.1.4"
    assert profile["vendor"]["repository_url"] == "https://example.com/demo.git"
    assert profile["vendor"]["ecosystem"] == "python"
    assert profile["usage_count"] == 1
    assert [s["name"] for s in profile["symbols"]] == ["greet"]


def test_rebuild_project_graph_includes_unused_vendor_with_zero_usage(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    src = _build_source_tree(tmp_path)
    _patch_adapter(monkeypatch, source_dir=src)
    config = VendorConfig(name="demo", ecosystem=Ecosystem.PYTHON)

    rebuild_project_graph([config], tmp_path)

    conn = open_graph(tmp_path)
    assert unused_vendors(conn) == ["demo"]


def test_rebuild_project_graph_unresolved_symbol_name_stays_vendor_level_edge(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    src = tmp_path / "vendor_src"
    src.mkdir()
    (src / "__init__.py").write_text("def known(): ...\n", encoding="utf-8")
    _patch_adapter(monkeypatch, source_dir=src)
    (tmp_path / "app.py").write_text("from demo import unknown_symbol\n", encoding="utf-8")
    config = VendorConfig(name="demo", ecosystem=Ecosystem.PYTHON)

    rebuild_project_graph([config], tmp_path)

    conn = open_graph(tmp_path)
    (symbol_id,) = conn.execute("SELECT symbol_id FROM uses_edges").fetchone()
    assert symbol_id is None


def test_rebuild_project_graph_scans_project_tests_directory(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    src = tmp_path / "vendor_src"
    src.mkdir()
    (src / "__init__.py").write_text("def greet(): ...\n", encoding="utf-8")
    _patch_adapter(monkeypatch, source_dir=src)
    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    (tests_dir / "test_app.py").write_text("from demo import greet\n", encoding="utf-8")
    config = VendorConfig(name="demo", ecosystem=Ecosystem.PYTHON)

    rebuild_project_graph([config], tmp_path)

    conn = open_graph(tmp_path)
    (path,) = conn.execute("SELECT path FROM source_files").fetchone()
    assert path == "tests/test_app.py"


def test_rebuild_project_graph_reflects_full_tracked_list_not_a_subset(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """The graph must represent every tracked vendor passed in, regardless
    of whether this particular run is what synced each one's files.
    """
    src = _build_source_tree(tmp_path)
    _patch_adapter(monkeypatch, source_dir=src)
    configs = [
        VendorConfig(name="a", ecosystem=Ecosystem.PYTHON),
        VendorConfig(name="b", ecosystem=Ecosystem.PYTHON),
    ]

    rebuild_project_graph(configs, tmp_path)

    conn = open_graph(tmp_path)
    names = {name for (name,) in conn.execute("SELECT name FROM vendors")}
    assert names == {"a", "b"}
