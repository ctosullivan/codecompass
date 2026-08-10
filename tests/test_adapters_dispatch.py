from pathlib import Path

from depcompass.adapters import get_adapter
from depcompass.adapters.cargo import CargoAdapter
from depcompass.adapters.npm import NpmAdapter
from depcompass.adapters.python import PythonAdapter
from depcompass.core import Depth, Ecosystem, VendorConfig


def _config(ecosystem: Ecosystem) -> VendorConfig:
    return VendorConfig(name="demo", ecosystem=ecosystem, depth=Depth.SURFACE)


def test_get_adapter_dispatches_by_ecosystem(tmp_path: Path) -> None:
    assert isinstance(get_adapter(_config(Ecosystem.NPM), tmp_path), NpmAdapter)
    assert isinstance(get_adapter(_config(Ecosystem.PYTHON), tmp_path), PythonAdapter)
    assert isinstance(get_adapter(_config(Ecosystem.CARGO), tmp_path), CargoAdapter)


def test_get_adapter_passes_config_and_project_root_through(tmp_path: Path) -> None:
    config = _config(Ecosystem.NPM)
    adapter = get_adapter(config, tmp_path)

    assert adapter.config is config
    assert adapter.project_root == tmp_path
