"""Ecosystem adapter dispatch. See architecture/overview.md's "Adapter
interface" section.
"""

from __future__ import annotations

from pathlib import Path

from depcompass.adapters.base import AdapterError, EcosystemAdapter
from depcompass.adapters.cargo import CargoAdapter
from depcompass.adapters.npm import NpmAdapter
from depcompass.adapters.python import PythonAdapter
from depcompass.core import Ecosystem, VendorConfig

__all__ = ["AdapterError", "EcosystemAdapter", "get_adapter"]

_ADAPTER_BY_ECOSYSTEM: dict[Ecosystem, type[EcosystemAdapter]] = {
    Ecosystem.NPM: NpmAdapter,
    Ecosystem.PYTHON: PythonAdapter,
    Ecosystem.CARGO: CargoAdapter,
}


def get_adapter(config: VendorConfig, project_root: Path) -> EcosystemAdapter:
    """Construct the EcosystemAdapter matching `config.ecosystem` — the
    single dispatch point `sync.py` uses instead of each call site
    constructing an adapter class directly.
    """
    return _ADAPTER_BY_ECOSYSTEM[config.ecosystem](config, project_root)
