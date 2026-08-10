"""Manifest-based dependency discovery and vendor.toml bootstrap, for
`init --scan`. See docs/config-schema.md.
"""

from __future__ import annotations

import json
import re
import tomllib
from pathlib import Path

from depcompass.core import Ecosystem


class DiscoveryError(Exception):
    """Raised when `init --scan` can't produce a vendor.toml — an
    unrecognized manifest filename, an unreadable/malformed manifest, or
    an existing vendor.toml at the target path.
    """


def discover_npm(manifest: Path) -> list[str]:
    """`package.json`'s `dependencies` + `devDependencies` keys."""
    try:
        data = json.loads(manifest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise DiscoveryError(f"{manifest}: could not read as JSON: {exc}") from exc
    names = set(data.get("dependencies", {})) | set(data.get("devDependencies", {}))
    return sorted(names)


_REQUIREMENT_NAME_RE = re.compile(r"^[A-Za-z0-9._-]+")


def discover_python(manifest: Path) -> list[str]:
    """`pyproject.toml`'s `[project.dependencies]` array, stripping
    version specifiers/extras/markers down to bare package names.
    `[project.optional-dependencies]` is not scanned (documented
    limitation — see planning/phase-4-sync-index-init.md).
    """
    data = _load_toml(manifest)
    raw_requirements = data.get("project", {}).get("dependencies", [])
    names = {_bare_requirement_name(req) for req in raw_requirements}
    names.discard("")
    return sorted(names)


def _bare_requirement_name(requirement: str) -> str:
    match = _REQUIREMENT_NAME_RE.match(requirement.strip())
    return match.group(0) if match else ""


def discover_cargo(manifest: Path) -> list[str]:
    """`Cargo.toml`'s `[dependencies]` + `[dev-dependencies]` table keys."""
    data = _load_toml(manifest)
    names = set(data.get("dependencies", {})) | set(data.get("dev-dependencies", {}))
    return sorted(names)


def _load_toml(manifest: Path) -> dict:
    try:
        with manifest.open("rb") as fp:
            return tomllib.load(fp)
    except OSError as exc:
        raise DiscoveryError(f"{manifest}: could not read: {exc}") from exc
    except tomllib.TOMLDecodeError as exc:
        raise DiscoveryError(f"{manifest}: not valid TOML: {exc}") from exc


_ECOSYSTEM_BY_MANIFEST_NAME = {
    "package.json": Ecosystem.NPM,
    "pyproject.toml": Ecosystem.PYTHON,
    "Cargo.toml": Ecosystem.CARGO,
}
_DISCOVER_BY_ECOSYSTEM = {
    Ecosystem.NPM: discover_npm,
    Ecosystem.PYTHON: discover_python,
    Ecosystem.CARGO: discover_cargo,
}


def discover_all(manifests: list[Path]) -> dict[Ecosystem, list[str]]:
    """Dispatch each manifest to the matching discoverer by filename,
    merging names per ecosystem across however many manifests were given.
    """
    result: dict[Ecosystem, set[str]] = {}
    for manifest in manifests:
        ecosystem = _ECOSYSTEM_BY_MANIFEST_NAME.get(manifest.name)
        if ecosystem is None:
            expected = ", ".join(sorted(_ECOSYSTEM_BY_MANIFEST_NAME))
            raise DiscoveryError(
                f"{manifest}: unrecognized manifest filename — expected one of {expected}"
            )
        names = _DISCOVER_BY_ECOSYSTEM[ecosystem](manifest)
        result.setdefault(ecosystem, set()).update(names)
    return {ecosystem: sorted(names) for ecosystem, names in result.items()}


def write_vendor_toml(names_by_ecosystem: dict[Ecosystem, list[str]], path: Path) -> None:
    """Hand-rolled minimal TOML serialization — `tomllib` has no write
    support, but this produces a fresh, comment-free draft, not an
    edit-in-place of a hand-authored file, so a round-trip-preserving
    writer library isn't needed (decisions/0011). Errors rather than
    overwriting if `path` already exists.
    """
    if path.exists():
        raise DiscoveryError(f"{path} already exists — refusing to overwrite it")
    blocks = [
        f'[[vendor]]\nname = "{name}"\necosystem = "{ecosystem.value}"\ndepth = "surface"\n'
        for ecosystem, names in names_by_ecosystem.items()
        for name in names
    ]
    path.write_text("\n".join(blocks), encoding="utf-8")
