"""Ecosystem adapter dispatch. See architecture/overview.md's "Adapter
interface" section.
"""

from __future__ import annotations

from pathlib import Path

from codecompass.adapters.base import AdapterError, EcosystemAdapter
from codecompass.adapters.cargo import CargoAdapter
from codecompass.adapters.npm import NpmAdapter
from codecompass.adapters.python import PythonAdapter
from codecompass.core import Ecosystem, VendorConfig

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
