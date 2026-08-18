"""Severity-aware staleness checking (`codecompass check`).

Compares each vendor's persisted `**Installed version:**` line (read via
`claude_md.read_installed_version`, the same helper `index.py` uses)
against the ecosystem adapter's live read. Severity follows
`decisions/0005`: patch delta is `NONE` (silent/ignored), minor delta
warns, major delta hard-fails. Never builds a `VendorDigest` — same
cheap, side-effect-free, no-AI-cost pattern `index.py` (Phase 4) already
established for the same reason: `check` must stay usable as a fast CI
gate. See planning/phase-6-staleness-checking.md.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from codecompass.adapters import AdapterError, get_adapter
from codecompass.claude_md import read_installed_version
from codecompass.core import VendorConfig
from codecompass.deptree import render_deptree_json

_VERSION_TRIPLE_RE = re.compile(r"^\D*(\d+)\.(\d+)\.(\d+)")


class Severity(StrEnum):
    """Semantic-version-delta severity, per decisions/0005. `UNKNOWN`
    means at least one side of the comparison couldn't be parsed as a
    `major.minor.patch` triple — treated as a hard-fail case under
    `--strict`, since an unclassifiable delta is a "can't verify" state,
    not a "safe to ignore" one.
    """

    NONE = "none"
    PATCH = "patch"
    MINOR = "minor"
    MAJOR = "major"
    UNKNOWN = "unknown"


def _parse_version(version: str) -> tuple[int, int, int] | None:
    """Extracts a leading `major.minor.patch` integer triple, tolerating a
    `v` prefix and ignoring any trailing pre-release/build suffix. Not a
    real PEP 440 or full semver parser — no epoch or pre-release-ordering
    support. Never raises; returns `None` on anything it can't parse.
    """
    match = _VERSION_TRIPLE_RE.match(version)
    if not match:
        return None
    major, minor, patch = match.groups()
    return (int(major), int(minor), int(patch))


def classify(recorded: str, live: str) -> Severity:
    """decisions/0005's patch/minor/major policy. Two strings whose parsed
    numeric triples match classify as `NONE` even if the raw strings
    differ (e.g. a build-metadata-only difference) — this is about
    semantic delta, not string equality.
    """
    if recorded == live:
        return Severity.NONE
    old = _parse_version(recorded)
    new = _parse_version(live)
    if old is None or new is None:
        return Severity.UNKNOWN
    if old == new:
        return Severity.NONE
    if old[0] != new[0]:
        return Severity.MAJOR
    if old[1] != new[1]:
        return Severity.MINOR
    return Severity.PATCH


@dataclass
class VendorStaleness:
    """One vendor's staleness comparison. Mirrors `index.py`'s
    `RoutingRow` in spirit — a lightweight, persisted-state-based result
    type, not a `VendorDigest`.

    `recorded_version` is `None` if the vendor has never been synced —
    `severity` stays `NONE` in that case (nothing to classify), and the
    CLI reports it as "not synced" rather than a staleness failure, same
    treatment `index.py` gives an unsynced vendor's routing-table row.
    `live_version`/`error` are mutually exclusive: `error` is set (and
    `live_version` stays `None`) only if the adapter's live read itself
    failed.
    """

    config: VendorConfig
    recorded_version: str | None
    live_version: str | None
    severity: Severity
    transitive_drift: bool
    error: str | None = None


def _flatten(node: dict, out: dict[str, set[str]] | None = None) -> dict[str, set[str]]:
    """Walks a `deptree.render_deptree_json`-shaped tree into a flat
    `name -> {versions}` map, resolving `{"ref": "name@version"}` back-
    references via `rpartition("@")` (not `split`) so scoped npm names
    like `@babel/core` — which themselves contain `@` — parse correctly,
    since only the last `@` in a ref string separates name from version.
    Used on both the persisted `deptree.json` dict and a freshly built
    live tree in the same shape, so one function serves both sides of the
    transitive-drift diff.
    """
    if out is None:
        out = {}
    if "ref" in node:
        name, sep, version = node["ref"].rpartition("@")
        if sep:
            out.setdefault(name, set()).add(version)
        return out
    name = node.get("name")
    version = node.get("version")
    if name is not None and version is not None:
        out.setdefault(name, set()).add(version)
    for child in node.get("children", []):
        _flatten(child, out)
    return out


def _detect_transitive_drift(vendor_dir: Path, adapter: object) -> bool:
    """Only meaningful when the vendor's own root version is unchanged —
    callers only invoke this when `severity is Severity.NONE`. Best-effort
    ("where practical" per decisions/0005): a missing/corrupt persisted
    `deptree.json`, or a failure building the live tree, just means "no
    drift signal available this run" rather than failing the whole
    vendor's staleness check — the root-version comparison already
    succeeded by the time this runs.
    """
    deptree_path = vendor_dir / "deptree.json"
    if not deptree_path.exists():
        return False
    try:
        persisted_tree = json.loads(deptree_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    try:
        live_tree = render_deptree_json(adapter.dependency_tree())  # type: ignore[attr-defined]
    except AdapterError:
        return False
    return _flatten(persisted_tree) != _flatten(live_tree)


def check_vendor(config: VendorConfig, project_root: Path) -> VendorStaleness:
    """Reads the persisted version, then the live one — catching
    `AdapterError` locally so one vendor's broken adapter read can't crash
    the whole `check` run (unlike `sync_vendor`, which lets `AdapterError`
    propagate; `check`'s read-only nature makes this isolation cheap and
    worth doing here regardless).
    """
    vendor_dir = project_root / "vendor" / config.name
    recorded_version = read_installed_version(vendor_dir / "CLAUDE.md")
    adapter = get_adapter(config, project_root)

    try:
        live_version = adapter.installed_version()
    except AdapterError as exc:
        return VendorStaleness(
            config=config,
            recorded_version=recorded_version,
            live_version=None,
            severity=Severity.NONE,
            transitive_drift=False,
            error=str(exc),
        )

    severity = (
        Severity.NONE if recorded_version is None else classify(recorded_version, live_version)
    )
    transitive_drift = False
    if recorded_version is not None and severity is Severity.NONE:
        transitive_drift = _detect_transitive_drift(vendor_dir, adapter)

    return VendorStaleness(
        config=config,
        recorded_version=recorded_version,
        live_version=live_version,
        severity=severity,
        transitive_drift=transitive_drift,
        error=None,
    )


def check_all(configs: list[VendorConfig], project_root: Path) -> list[VendorStaleness]:
    return [check_vendor(config, project_root) for config in configs]
