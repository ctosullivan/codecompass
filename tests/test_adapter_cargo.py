import json
import shutil
import subprocess
from pathlib import Path

import pytest

import depcompass.adapters.cargo as cargo_module
from depcompass.adapters.base import AdapterError
from depcompass.adapters.cargo import CargoAdapter, _extract_pub_items
from depcompass.core import Depth, Ecosystem, VendorConfig

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


def test_extract_pub_items_captures_doc_comment_and_signature() -> None:
    source = (FIXTURES / "sample_lib.rs").read_text(encoding="utf-8")
    items = _extract_pub_items(source)

    add_item = next(i for i in items if "pub fn add" in i)
    assert "Adds two numbers together." in add_item

    assert any("pub struct Point" in i for i in items)
    assert not any("internal_helper" in i for i in items)  # not pub


def test_extract_pub_items_misses_multi_line_signature() -> None:
    """Documents the coarse-scan limitation explicitly, rather than
    hiding it: only the opening line of a multi-line signature is
    captured."""
    source = (FIXTURES / "sample_lib.rs").read_text(encoding="utf-8")
    items = _extract_pub_items(source)

    multi_line_item = next(i for i in items if "multi_line_signature" in i)
    assert multi_line_item.strip().endswith("pub fn multi_line_signature(")
    assert "-> i32" not in multi_line_item  # the rest of the signature is missed


def test_readme_and_api_surface(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
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
    assert "pub fn add" in surface


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
