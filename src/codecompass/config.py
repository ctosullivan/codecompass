"""Parsing for vendor.toml — see docs/config-schema.md for the file format."""

from __future__ import annotations

import tomllib
from pathlib import Path

from codecompass.core import Ecosystem, VendorConfig


class ConfigError(Exception):
    """Raised when vendor.toml is missing, malformed, or has an invalid entry.

    Validation is fail-fast: the first invalid vendor entry raises,
    naming the vendor and the problem, rather than collecting every
    issue in the file before reporting.
    """


def load_vendor_config(path: Path) -> list[VendorConfig]:
    """Parse `path` (a vendor.toml file) into a list of VendorConfig."""
    try:
        with path.open("rb") as fp:
            data = tomllib.load(fp)
    except OSError as exc:
        raise ConfigError(f"could not read {path}: {exc}") from exc
    except tomllib.TOMLDecodeError as exc:
        raise ConfigError(f"{path} is not valid TOML: {exc}") from exc

    raw_entries = data.get("vendor", [])
    if not isinstance(raw_entries, list):
        raise ConfigError(f"{path}: 'vendor' must be an array of tables ([[vendor]])")

    vendors: list[VendorConfig] = []
    for index, entry in enumerate(raw_entries):
        vendors.append(_parse_entry(path, index, entry))
    return vendors


def _parse_entry(path: Path, index: int, entry: dict) -> VendorConfig:
    """A legacy `depth = "surface"`/`depth = "full"` key (Phase 16 retired
    the field — decisions/0031, decisions/0035) is silently tolerated:
    this function simply never looks at it, so an old vendor.toml still
    parses without error. No migration, no warning.
    """
    label = entry.get("name", f"entry #{index + 1}")

    name = _require_field(path, label, entry, "name")
    ecosystem = _require_enum(path, name, entry, "ecosystem", Ecosystem)
    return VendorConfig(name=name, ecosystem=ecosystem)


def _require_field(path: Path, label: str, entry: dict, field_name: str) -> str:
    try:
        return entry[field_name]
    except KeyError as exc:
        raise ConfigError(
            f"{path}: vendor {label!r} is missing required field {field_name!r}"
        ) from exc


def _require_enum(path: Path, label: str, entry: dict, field_name: str, enum_cls):
    raw = _require_field(path, label, entry, field_name)
    try:
        return enum_cls(raw)
    except ValueError as exc:
        valid = ", ".join(member.value for member in enum_cls)
        raise ConfigError(
            f"{path}: vendor {label!r} has invalid {field_name} {raw!r} "
            f"(expected one of: {valid})"
        ) from exc
