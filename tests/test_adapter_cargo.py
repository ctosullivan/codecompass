import json
import shutil
import subprocess
from pathlib import Path

import pytest

import depcompass.adapters.cargo as cargo_module
from depcompass.adapters.base import AdapterError
from depcompass.adapters.cargo import CargoAdapter
from depcompass.core import Depth, Ecosystem, RepositoryLocation, VendorConfig

FIXTURES = Path(__file__).parent / "fixtures"


def _adapter(name: str, project_root: Path) -> CargoAdapter:
    config = VendorConfig(name=name, ecosystem=Ecosystem.CARGO, depth=Depth.SURFACE)
    return CargoAdapter(config, project_root=project_root)


def _metadata() -> dict:
    return json.loads((FIXTURES / "cargo_metadata.json").read_text(encoding="utf-8"))


def test_installed_version_and_source_location(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(cargo_module, "_run_json", lambda cmd, cwd: _metadata())
    adapter = _adapter("serde", tmp_path)

    assert adapter.installed_version() == "1.0.0"
    assert adapter.source_location() == Path("/registry/serde-1.0.0")


def test_repository_url_none_when_field_absent(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """The shared `cargo_metadata.json` fixture's packages carry no
    `repository` field — the common real-world case for a fixture built
    before this field mattered.
    """
    monkeypatch.setattr(cargo_module, "_run_json", lambda cmd, cwd: _metadata())
    adapter = _adapter("demo-crate", tmp_path)

    assert adapter.repository_url() is None


def test_repository_url_present(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    data = _metadata()
    data["packages"][0]["repository"] = "https://github.com/example/demo-crate"
    monkeypatch.setattr(cargo_module, "_run_json", lambda cmd, cwd: data)
    adapter = _adapter("demo-crate", tmp_path)

    assert adapter.repository_url() == RepositoryLocation(
        url="https://github.com/example/demo-crate", subdirectory=None
    )


def test_missing_package_raises_adapter_error(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(cargo_module, "_run_json", lambda cmd, cwd: _metadata())
    adapter = _adapter("nonexistent-crate", tmp_path)
    with pytest.raises(AdapterError, match="not found"):
        adapter.installed_version()


def test_dependency_tree_dev_only_and_nesting(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(cargo_module, "_run_json", lambda cmd, cwd: _metadata())
    adapter = _adapter("demo-crate", tmp_path)
    tree = adapter.dependency_tree()

    assert tree.name == "demo-crate"
    assert tree.dev_only is False
    by_name = {c.name: c for c in tree.children}
    assert set(by_name) == {"serde", "serde_test"}
    assert by_name["serde"].dev_only is False
    assert by_name["serde_test"].dev_only is True

    # Nested: serde's own child, serde_derive, inherits serde's declared
    # (non-dev) kind for it — not transitively marked dev via the parent.
    assert [c.name for c in by_name["serde"].children] == ["serde_derive"]
    assert by_name["serde"].children[0].dev_only is False


def test_readme_and_api_surface(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Pub-item extraction itself is covered by tests/test_symbols.py
    (extract_rust_symbols) since Phase 3 moved that logic there; this
    test only confirms the adapter wires README + extracted symbols
    together. Rendered format changed from raw signature lines to
    `name: purpose` when the adapter switched to the shared, name-based
    extractor (planning/phase-3-tree-generation.md)."""
    (tmp_path / "README.md").write_text("# demo-crate\n\nA demo crate.", encoding="utf-8")
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    (src_dir / "lib.rs").write_text(
        (FIXTURES / "sample_lib.rs").read_text(encoding="utf-8"), encoding="utf-8"
    )

    adapter = _adapter("demo-crate", tmp_path)
    monkeypatch.setattr(adapter, "source_location", lambda: tmp_path)

    surface = adapter.readme_and_api_surface()
    assert "A demo crate." in surface
    assert "add: Adds two numbers together." in surface


@pytest.mark.smoke
@pytest.mark.skipif(shutil.which("cargo") is None, reason="cargo not installed")
def test_live_smoke_cargo_self_package(tmp_path: Path) -> None:
    """Unexercised in this dev environment (no Rust toolchain available)
    — written and ready for whenever a toolchain becomes available. See
    decisions/0014 and planning/phase-2-ecosystem-adapters.md's
    Verification follow-up note."""
    cargo_path = shutil.which("cargo")
    assert cargo_path is not None
    subprocess.run(
        [cargo_path, "init", "--name", "depcompass_cargo_smoke", "--vcs", "none"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )
    adapter = _adapter("depcompass_cargo_smoke", tmp_path)
    assert adapter.installed_version() == "0.1.0"
    assert adapter.source_location().exists()
