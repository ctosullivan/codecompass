import json
import shutil
import subprocess
from pathlib import Path

import pytest

import codecompass.adapters.npm as npm_module
from codecompass.adapters.base import AdapterError
from codecompass.adapters.npm import NpmAdapter
from codecompass.core import Depth, Ecosystem, RepositoryLocation, VendorConfig

FIXTURES = Path(__file__).parent / "fixtures"


def _write_package(project_root: Path, vendor: str, package_json: dict) -> None:
    pkg_dir = project_root / "node_modules" / vendor
    pkg_dir.mkdir(parents=True, exist_ok=True)
    (pkg_dir / "package.json").write_text(json.dumps(package_json), encoding="utf-8")


def test_installed_version_and_source_location(tmp_path: Path) -> None:
    postinstall_pkg = json.loads(
        (FIXTURES / "npm_package_with_postinstall.json").read_text(encoding="utf-8")
    )
    _write_package(tmp_path, "turndown", postinstall_pkg)
    config = VendorConfig(name="turndown", ecosystem=Ecosystem.NPM, depth=Depth.SURFACE)
    adapter = NpmAdapter(config, project_root=tmp_path)

    assert adapter.installed_version() == "7.1.2"
    assert adapter.source_location() == tmp_path / "node_modules" / "turndown"


def test_repository_url_from_plain_string(tmp_path: Path) -> None:
    _write_package(
        tmp_path,
        "turndown",
        {
            "name": "turndown",
            "repository": "git+https://github.com/mixmark-io/turndown.git",
        },
    )
    config = VendorConfig(name="turndown", ecosystem=Ecosystem.NPM, depth=Depth.SURFACE)
    adapter = NpmAdapter(config, project_root=tmp_path)

    assert adapter.repository_url() == RepositoryLocation(
        url="https://github.com/mixmark-io/turndown.git", subdirectory=None
    )


def test_repository_url_from_object_with_directory(tmp_path: Path) -> None:
    _write_package(
        tmp_path,
        "some-pkg",
        {
            "name": "some-pkg",
            "repository": {
                "type": "git",
                "url": "https://github.com/org/monorepo.git",
                "directory": "packages/some-pkg",
            },
        },
    )
    config = VendorConfig(name="some-pkg", ecosystem=Ecosystem.NPM, depth=Depth.SURFACE)
    adapter = NpmAdapter(config, project_root=tmp_path)

    assert adapter.repository_url() == RepositoryLocation(
        url="https://github.com/org/monorepo.git", subdirectory="packages/some-pkg"
    )


def test_repository_url_shorthand_expands_to_https(tmp_path: Path) -> None:
    _write_package(tmp_path, "some-pkg", {"name": "some-pkg", "repository": "github:org/some-pkg"})
    config = VendorConfig(name="some-pkg", ecosystem=Ecosystem.NPM, depth=Depth.SURFACE)
    adapter = NpmAdapter(config, project_root=tmp_path)

    assert adapter.repository_url() == RepositoryLocation(
        url="https://github.com/org/some-pkg", subdirectory=None
    )


def test_repository_url_none_when_field_absent(tmp_path: Path) -> None:
    _write_package(tmp_path, "some-pkg", {"name": "some-pkg"})
    config = VendorConfig(name="some-pkg", ecosystem=Ecosystem.NPM, depth=Depth.SURFACE)
    adapter = NpmAdapter(config, project_root=tmp_path)

    assert adapter.repository_url() is None


def test_missing_package_raises_adapter_error(tmp_path: Path) -> None:
    config = VendorConfig(name="nonexistent-pkg", ecosystem=Ecosystem.NPM, depth=Depth.SURFACE)
    adapter = NpmAdapter(config, project_root=tmp_path)
    with pytest.raises(AdapterError, match="not found"):
        adapter.installed_version()


def test_dependency_tree_no_dedup_and_dev_only(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    ls_data = json.loads((FIXTURES / "npm_ls.json").read_text(encoding="utf-8"))
    (tmp_path / "package.json").write_text(
        (FIXTURES / "npm_package_root.json").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    postinstall_pkg = json.loads(
        (FIXTURES / "npm_package_with_postinstall.json").read_text(encoding="utf-8")
    )
    _write_package(tmp_path, "turndown", postinstall_pkg)

    monkeypatch.setattr(npm_module, "_run_json", lambda cmd, cwd: ls_data)

    config = VendorConfig(name="turndown", ecosystem=Ecosystem.NPM, depth=Depth.SURFACE)
    adapter = NpmAdapter(config, project_root=tmp_path)
    tree = adapter.dependency_tree()

    assert tree.name == "turndown"
    assert tree.version == "7.1.2"
    assert tree.dev_only is False
    assert [c.name for c in tree.children] == ["domino", "commander"]

    commander = tree.children[1]
    assert commander.dev_only is True  # in root package.json's devDependencies
    assert [c.name for c in commander.children] == ["domino"]

    # No dedup: "domino" appears twice, as two distinct DepNode instances.
    domino_direct = tree.children[0]
    domino_nested = commander.children[0]
    assert domino_direct is not domino_nested
    assert domino_direct.dev_only is False  # not itself a devDependency

    # Side effect picked up from turndown's own package.json.
    assert any("postinstall" in effect for effect in tree.side_effects)


def test_readme_and_dts_cap(tmp_path: Path) -> None:
    pkg_dir = tmp_path / "node_modules" / "turndown"
    pkg_dir.mkdir(parents=True)
    (pkg_dir / "package.json").write_text(
        json.dumps({"name": "turndown", "version": "7.1.2"}), encoding="utf-8"
    )
    (pkg_dir / "README.md").write_text(
        (FIXTURES / "sample_readme.md").read_text(encoding="utf-8"), encoding="utf-8"
    )
    dts_content = (FIXTURES / "sample.d.ts").read_text(encoding="utf-8")
    for i in range(1, 7):  # 6 files, cap is 5
        (pkg_dir / f"{i}.d.ts").write_text(dts_content, encoding="utf-8")

    config = VendorConfig(name="turndown", ecosystem=Ecosystem.NPM, depth=Depth.SURFACE)
    adapter = NpmAdapter(config, project_root=tmp_path)
    surface = adapter.readme_and_api_surface()

    assert "Convert HTML into Markdown" in surface
    for i in range(1, 6):
        assert f"{i}.d.ts" in surface
    assert "6.d.ts" not in surface  # trimmed by the cap


def test_readme_with_no_dts_files(tmp_path: Path) -> None:
    """A real npm package (turndown) ships no .d.ts at all — must not crash."""
    pkg_dir = tmp_path / "node_modules" / "turndown"
    pkg_dir.mkdir(parents=True)
    (pkg_dir / "package.json").write_text(
        json.dumps({"name": "turndown", "version": "7.1.2"}), encoding="utf-8"
    )
    (pkg_dir / "README.md").write_text(
        (FIXTURES / "sample_readme.md").read_text(encoding="utf-8"), encoding="utf-8"
    )

    config = VendorConfig(name="turndown", ecosystem=Ecosystem.NPM, depth=Depth.SURFACE)
    adapter = NpmAdapter(config, project_root=tmp_path)
    surface = adapter.readme_and_api_surface()

    assert "Convert HTML into Markdown" in surface


@pytest.mark.smoke
@pytest.mark.skipif(shutil.which("npm") is None, reason="npm not installed")
def test_live_smoke_npm_install_lodash(tmp_path: Path) -> None:
    # Resolve npm's full path before invoking directly (bypassing
    # _run_json here since this test wants to drive `npm install`, not
    # `npm ls`) — a bare "npm" fails on Windows without shell=True, since
    # it's a .cmd shim there. See base.py's _run_json docstring.
    npm_path = shutil.which("npm")
    assert npm_path is not None
    subprocess.run(
        [npm_path, "install", "lodash", "--no-save"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )
    config = VendorConfig(name="lodash", ecosystem=Ecosystem.NPM, depth=Depth.SURFACE)
    adapter = NpmAdapter(config, project_root=tmp_path)

    assert adapter.installed_version()
    assert adapter.source_location().exists()
    assert adapter.dependency_tree().name == "lodash"
    assert adapter.readme_and_api_surface()  # lodash ships a README
