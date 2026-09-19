"""Fixture tests for the thin `HaskellAdapter` dispatcher —
`package.yaml` reads (real `yaml.safe_load()`, not mocked) and monorepo
package-root resolution (`decisions/0057` §"Monorepo package roots").
The `analyze_project`/dependency-tree/API-surface half (delegated to the
external, submodule-hosted adapter process) is covered by
`tests/test_adapters_external_process.py`'s fixture tests plus this
repository's own `stack`/submodule-gated live smoke test — see
planning/phase-60-minimal-haskell-adapter.md §7.
"""

import shutil
from pathlib import Path

import pytest

from codecompass.adapters.base import AdapterError
from codecompass.adapters.haskell import HaskellAdapter
from codecompass.core import Ecosystem, RepositoryLocation, VendorConfig

_SUBMODULE_MANIFEST = (
    Path(__file__).resolve().parents[1] / "adapters" / "haskell" / "package.yaml"
)
_SIBLING_HLEDGER_CHECKOUT = Path(__file__).resolve().parents[2] / "hledger"
_STACK_AVAILABLE = shutil.which("stack") is not None

_PACKAGE_YAML = """\
name: {name}
version: {version}
github: {github}
dependencies:
- base >=4.18 && <4.23
- aeson
"""


def _adapter(name: str, project_root: Path) -> HaskellAdapter:
    config = VendorConfig(name=name, ecosystem=Ecosystem.HASKELL)
    return HaskellAdapter(config, project_root=project_root)


def test_installed_version_reads_package_yaml_directly(tmp_path: Path) -> None:
    (tmp_path / "package.yaml").write_text(
        _PACKAGE_YAML.format(name="demo-package", version="1.2.3", github="example/demo"),
        encoding="utf-8",
    )
    adapter = _adapter("demo-package", tmp_path)

    assert adapter.installed_version() == "1.2.3"


def test_installed_version_missing_version_field_raises_adapter_error(
    tmp_path: Path,
) -> None:
    (tmp_path / "package.yaml").write_text("name: demo-package\n", encoding="utf-8")
    adapter = _adapter("demo-package", tmp_path)

    with pytest.raises(AdapterError, match="no 'version' field"):
        adapter.installed_version()


def test_repository_url_from_github_shorthand(tmp_path: Path) -> None:
    (tmp_path / "package.yaml").write_text(
        _PACKAGE_YAML.format(name="demo-package", version="1.0.0", github="example/demo"),
        encoding="utf-8",
    )
    adapter = _adapter("demo-package", tmp_path)

    assert adapter.repository_url() == RepositoryLocation(url="https://github.com/example/demo")


def test_repository_url_none_when_github_field_absent(tmp_path: Path) -> None:
    (tmp_path / "package.yaml").write_text(
        "name: demo-package\nversion: 1.0.0\n", encoding="utf-8"
    )
    adapter = _adapter("demo-package", tmp_path)

    assert adapter.repository_url() is None


def test_source_location_is_project_root_when_not_a_monorepo(tmp_path: Path) -> None:
    (tmp_path / "package.yaml").write_text(
        "name: demo-package\nversion: 1.0.0\n", encoding="utf-8"
    )
    adapter = _adapter("demo-package", tmp_path)

    assert adapter.source_location() == tmp_path


def test_monorepo_resolves_to_matching_subdirectory(tmp_path: Path) -> None:
    """Mirrors the real `hledger` monorepo shape: a root with no
    `package.yaml` of its own, and several sibling package directories
    each with their own — the target must resolve to exactly the one
    whose own `name:` field matches, never the monorepo root itself.
    """
    (tmp_path / "hledger").mkdir()
    (tmp_path / "hledger" / "package.yaml").write_text(
        "name: hledger\nversion: 1.52.4\n", encoding="utf-8"
    )
    (tmp_path / "hledger-lib").mkdir()
    (tmp_path / "hledger-lib" / "package.yaml").write_text(
        "name: hledger-lib\nversion: 1.52.4\n", encoding="utf-8"
    )
    (tmp_path / "hledger-ui").mkdir()
    (tmp_path / "hledger-ui" / "package.yaml").write_text(
        "name: hledger-ui\nversion: 1.52.4\n", encoding="utf-8"
    )
    adapter = _adapter("hledger-lib", tmp_path)

    assert adapter.source_location() == tmp_path / "hledger-lib"
    assert adapter.installed_version() == "1.52.4"


def test_monorepo_no_matching_subdirectory_raises_adapter_error(tmp_path: Path) -> None:
    (tmp_path / "hledger").mkdir()
    (tmp_path / "hledger" / "package.yaml").write_text(
        "name: hledger\nversion: 1.52.4\n", encoding="utf-8"
    )
    adapter = _adapter("hledger-lib", tmp_path)

    with pytest.raises(AdapterError, match="no package.yaml declaring this name found"):
        adapter.source_location()


def test_readme_and_api_surface_renders_symbols_grouped_by_module(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    (tmp_path / "package.yaml").write_text(
        "name: demo-package\nversion: 1.0.0\n", encoding="utf-8"
    )
    (tmp_path / "README.md").write_text("# demo-package\n\nA demo package.", encoding="utf-8")
    adapter = _adapter("demo-package", tmp_path)
    monkeypatch.setattr(
        adapter,
        "_analyze",
        lambda: {
            "symbols": [
                {"name": "doThing", "purpose": "does the thing", "module": "Demo.Core"},
                {
                    "name": "X",
                    "purpose": None,
                    "module": "Demo.Core",
                    "kind": "reexport",
                    "note": "alias for Demo.Internal.A, Demo.Internal.B",
                },
                {
                    "name": "Year",
                    "purpose": None,
                    "module": "Demo.Types",
                    "kind": "undetermined",
                    "note": "gated by a CPP conditional",
                },
            ]
        },
    )

    surface = adapter.readme_and_api_surface()

    assert "A demo package." in surface
    assert "doThing: does the thing" in surface
    assert "X [reexport] — alias for Demo.Internal.A, Demo.Internal.B" in surface
    assert "Year [undetermined] — gated by a CPP conditional" in surface


def test_malformed_package_yaml_raises_adapter_error(tmp_path: Path) -> None:
    (tmp_path / "package.yaml").write_text("name: [unterminated\n", encoding="utf-8")
    adapter = _adapter("demo-package", tmp_path)

    with pytest.raises(AdapterError, match="not valid YAML"):
        adapter.installed_version()


@pytest.mark.smoke
@pytest.mark.skipif(not _STACK_AVAILABLE, reason="stack not installed")
@pytest.mark.skipif(
    not _SUBMODULE_MANIFEST.is_file(),
    reason="adapters/haskell/ git submodule not initialized (git submodule update --init)",
)
@pytest.mark.skipif(
    not _SIBLING_HLEDGER_CHECKOUT.is_dir(),
    reason=f"reference checkout not found at {_SIBLING_HLEDGER_CHECKOUT}",
)
def test_live_smoke_real_hledger_lib_end_to_end() -> None:
    """The real, submodule-built external adapter, run against the real
    pinned `hledger` monorepo — the same live confirmation
    `planning/retros/phase-60-minimal-haskell-adapter.md` describes.
    Skips cleanly wherever the toolchain/submodule/reference checkout
    isn't present, matching every other adapter's own smoke-test
    posture (`decisions/0014`) extended to this phase's own two extra
    real-world preconditions.
    """
    adapter = _adapter("hledger-lib", _SIBLING_HLEDGER_CHECKOUT)

    assert adapter.installed_version() == "1.52.4"
    assert adapter.source_location() == _SIBLING_HLEDGER_CHECKOUT / "hledger-lib"
    assert adapter.repository_url() == RepositoryLocation(
        url="https://github.com/simonmichael/hledger"
    )

    tree = adapter.dependency_tree()
    assert tree.name == "hledger-lib"
    assert tree.version == "1.52.4"
    assert len(tree.children) > 0

    surface = adapter.readme_and_api_surface()
    assert "accountLeafName" in surface
    assert "accountSummarisedName: Truncate all account name" in surface
    assert "[undetermined]" in surface  # Hledger/Data/Types.hs's CPP-gated `Year`
    assert "[reexport]" in surface  # e.g. Hledger.hs's `module X` alias
