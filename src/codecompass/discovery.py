"""Manifest-based dependency discovery and vendor.toml bootstrap. Two
entry points: `init --scan` (explicit manifests, `discover_all` +
`write_vendor_toml`, unchanged since Phase 4) and bare `codecompass`'s
zero-question auto-discovery (`discover_manifest_paths` + `discover_all`
+ `append_vendor_toml`, new in Phase 7 — decisions/0017). See
docs/config-schema.md.
"""

from __future__ import annotations

import json
import re
import tomllib
from collections.abc import Callable
from pathlib import Path

from codecompass.core import Ecosystem, VendorConfig


class DiscoveryError(Exception):
    """Raised when discovery can't produce (or extend) a vendor.toml — an
    unrecognized manifest filename, an unreadable/malformed manifest, or
    (for `init --scan` specifically) an existing vendor.toml at the
    target path.
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


def discover_requirements_txt(manifest: Path) -> list[str]:
    """Line-based `requirements.txt` parser (decisions/0017 — bare
    `codecompass` auto-discovery recognizes this alongside
    `pyproject.toml` for Python). One requirement per line; blank lines,
    `#` comments, and pip-option lines (`-r other.txt`, `-e .`, etc.,
    which aren't package names) are skipped. Version specifiers/extras/
    environment markers are stripped the same way `discover_python`
    strips them from PEP 508 strings.
    """
    try:
        lines = manifest.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise DiscoveryError(f"{manifest}: could not read: {exc}") from exc
    names = {
        _bare_requirement_name(stripped)
        for stripped in (line.strip() for line in lines)
        if stripped and not stripped.startswith(("#", "-"))
    }
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


_MANIFEST_HANDLERS: dict[str, tuple[Ecosystem, Callable[[Path], list[str]]]] = {
    "package.json": (Ecosystem.NPM, discover_npm),
    "pyproject.toml": (Ecosystem.PYTHON, discover_python),
    "requirements.txt": (Ecosystem.PYTHON, discover_requirements_txt),
    "Cargo.toml": (Ecosystem.CARGO, discover_cargo),
}


def discover_manifest_paths(root: Path) -> list[Path]:
    """Root-level (non-recursive) scan for every known manifest filename
    present in `root` — the auto-discovery bare `codecompass` and its
    idempotent refresh use (decisions/0017), as opposed to `init
    --scan`'s explicit, individually-named manifests.
    """
    return [root / name for name in _MANIFEST_HANDLERS if (root / name).is_file()]


def discover_all(manifests: list[Path]) -> dict[Ecosystem, list[str]]:
    """Dispatch each manifest to the matching discoverer by filename,
    merging names per ecosystem across however many manifests were given
    (e.g. `pyproject.toml` and `requirements.txt` both contributing to
    `Ecosystem.PYTHON`).
    """
    result: dict[Ecosystem, set[str]] = {}
    for manifest in manifests:
        handler = _MANIFEST_HANDLERS.get(manifest.name)
        if handler is None:
            expected = ", ".join(sorted(_MANIFEST_HANDLERS))
            raise DiscoveryError(
                f"{manifest}: unrecognized manifest filename — expected one of {expected}"
            )
        ecosystem, discover_fn = handler
        names = discover_fn(manifest)
        result.setdefault(ecosystem, set()).update(names)
    return {ecosystem: sorted(names) for ecosystem, names in result.items()}


def render_vendor_block(config: VendorConfig) -> str:
    """One `[[vendor]]` TOML block for `config`, in the same hand-rolled
    format `write_vendor_toml` already produces — see its docstring for
    why this isn't a round-trip-preserving TOML writer (decisions/0011).
    """
    return f'[[vendor]]\nname = "{config.name}"\necosystem = "{config.ecosystem.value}"\n'


def write_vendor_toml(names_by_ecosystem: dict[Ecosystem, list[str]], path: Path) -> None:
    """Fresh `vendor.toml` — `init --scan`'s contract. Errors rather than
    overwriting if `path` already exists.
    """
    if path.exists():
        raise DiscoveryError(f"{path} already exists — refusing to overwrite it")
    configs = [
        VendorConfig(name=name, ecosystem=ecosystem)
        for ecosystem, names in names_by_ecosystem.items()
        for name in names
    ]
    path.write_text("\n".join(render_vendor_block(c) for c in configs), encoding="utf-8")


def append_vendor_toml(new_configs: list[VendorConfig], path: Path) -> None:
    """Append `new_configs` as fresh blocks onto an already-existing
    `vendor.toml` — the idempotent-refresh path bare `codecompass` uses
    (decisions/0017) when new dependencies are discovered in a project
    that's already bootstrapped. A no-op if `new_configs` is empty.
    Callers are responsible for `path` already existing; unlike
    `write_vendor_toml`, this never creates a fresh file.
    """
    if not new_configs:
        return
    blocks = "\n".join(render_vendor_block(c) for c in new_configs)
    with path.open("a", encoding="utf-8") as fp:
        fp.write("\n" + blocks)


def rewrite_vendor_toml(configs: list[VendorConfig], path: Path) -> None:
    """Overwrite `path` with a fresh serialization of `configs`. Unused
    since `promote` (its only caller, `decisions/0018`) was retired in
    Phase 15 (`decisions/0033`) — kept rather than deleted since it's a
    generically useful, tested primitive and removing it wasn't in any
    phase's scope; a future command that needs to rewrite `vendor.toml`
    wholesale can reuse it. Same non-round-trip-preserving rationale as
    `write_vendor_toml`: a fresh, comment-free rewrite, not an
    edit-in-place of a hand-authored file.
    """
    path.write_text("\n".join(render_vendor_block(c) for c in configs), encoding="utf-8")
