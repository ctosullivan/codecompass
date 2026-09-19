"""Haskell/Stack ecosystem adapter — the reference implementation of an
**external-process** adapter (`decisions/0057`, `decisions/0058`).

Deliberately thin: this module reads `package.yaml` directly (real
`package.yaml`-key lookups are the same class of generic,
ecosystem-adjacent code `discovery.py` already does for every other
ecosystem's own manifest — not "Haskell-specific implementation code" in
the sense that matters), resolves the monorepo package root, and
delegates everything that embodies real ecosystem-specific *logic*
(`stack`'s own dependency-tree semantics, `.hs`-source API-surface
extraction) to the external adapter process checked out at
`adapters/haskell/` (a separate, GPL-3.0-or-later, publicly hosted
repository — `codecompass-adaptor-haskell` — never imported from here;
this module only ever invokes its built executable as an opaque
subprocess via `external_process.py`).

See architecture/overview.md's "External adapters" section.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import yaml

from codecompass.adapters.base import AdapterError, EcosystemAdapter
from codecompass.adapters.external_process import ExternalAdapterProcess
from codecompass.core import DepNode, RepositoryLocation, VendorConfig
from codecompass.symbols import Symbol

# Where the built adapter executable is expected once
# `codecompass-adaptor-haskell` (checked out at this path as a git
# submodule) has been built with `stack build` — see
# docs/external-adapters.md.
_ADAPTER_SUBMODULE_DIR = "adapters/haskell"


class HaskellAdapter(EcosystemAdapter):
    def __init__(self, config: VendorConfig, project_root: Path) -> None:
        super().__init__(config, project_root)
        # Per-instance-only cache (Phase 62, §3 of the phase plan):
        # `dependency_tree()`, `readme_and_api_surface()`, and `symbols()`
        # each independently called `_analyze()`, spawning a full external
        # subprocess and re-running the *entire* `analyze_project` request
        # (computing both `dependencies` and `symbols` server-side) every
        # time, even though each caller only ever reads one of the two
        # fields. Deliberately not a cross-instance cache — `sync_vendor`
        # and `rebuild_project_graph` each construct their own separate
        # `HaskellAdapter`, and that redundancy is out of this phase's
        # scope (accepted, disclosed inefficiency).
        self._cached_analysis: dict | None = None

    def installed_version(self) -> str:
        manifest = self._resolve_package_yaml()
        version = manifest.get("version")
        if not version:
            raise AdapterError(
                f"{self.config.name}: package.yaml has no 'version' field"
            )
        return str(version)

    def source_location(self) -> Path:
        return self._resolve_package_dir()

    def repository_url(self) -> RepositoryLocation | None:
        """hpack's own `github:` shorthand key (`owner/repo`) is the only
        repository-location field `package.yaml` conventionally carries
        — resolved into a full URL the same way every other adapter
        resolves locally-available metadata only, never a network call
        (`decisions/0021`).

        `subdirectory` is set whenever `_resolve_package_dir()` resolves
        somewhere other than `self.project_root` itself — the monorepo
        case (e.g. `hledger-lib` inside the `hledger` monorepo, per
        `decisions/0057` §"Monorepo package roots"). Without it,
        `source_resolution.resolve_and_clone` (which honours this field
        exactly the way the npm adapter's own monorepo case already
        relies on) has no way to know the cloned repository root isn't
        itself the package's own source — it would silently treat the
        whole monorepo clone as `self.config.name`'s own source tree.
        Found live, during Phase 61's own planning, as a real
        pre-existing gap in this method (Phase 60 never set this field
        at all): a real `codecompass sync` produced a
        `vendor/hledger-lib/src/` containing `hledger`/`hledger-ui`/
        `hledger-web` too, not scoped to `hledger-lib`.
        """
        manifest = self._resolve_package_yaml()
        github = manifest.get("github")
        if not github:
            return None
        resolved_dir = self._resolve_package_dir()
        subdirectory = None
        if resolved_dir != self.project_root:
            subdirectory = str(resolved_dir.relative_to(self.project_root))
        return RepositoryLocation(url=f"https://github.com/{github}", subdirectory=subdirectory)

    def dependency_tree(self) -> DepNode:
        result = self._analyze()
        dependencies = result.get("dependencies")
        if dependencies is None:
            raise AdapterError(
                f"{self.config.name}: external Haskell adapter did not report "
                "a 'dependencies' capability"
            )
        return _dep_node_from_wire(dependencies)

    def readme_and_api_surface(self) -> str:
        location = self._resolve_package_dir()
        parts: list[str] = []
        for readme in sorted(location.glob("README*"))[:1]:
            parts.append(f"# {readme.name}\n\n{readme.read_text(encoding='utf-8')}")
        result = self._analyze()
        symbols_wire = result.get("symbols")
        if symbols_wire:
            by_module: dict[str, list[str]] = {}
            for entry in symbols_wire:
                by_module.setdefault(entry["module"], []).append(_render_symbol_line(entry))
            for module, lines in sorted(by_module.items()):
                parts.append(f"# {module}\n\n" + "\n\n".join(lines))
        return "\n\n".join(parts)

    def symbols(self) -> list[Symbol]:
        """Overrides `EcosystemAdapter.symbols()`'s own default (a local
        source-file walk through `extract_symbols_for_file`, which has no
        Haskell branch and never will — see that method's own docstring).
        Converts the (now-cached) `_analyze()` result's own wire `symbols`
        list into `Symbol` objects — real, already-computed data, no new
        Haskell-specific logic added to `src/codecompass/` beyond this
        plain dict-to-dataclass mapping.

        This is the one place the external wire protocol's own `kind`
        field (`decisions/0059`) and CodeCompass-core's own `export_kind`
        field (Phase 62 — deliberately not named `kind`; see `Symbol`'s
        own docstring) meet: read one, write the other.
        """
        result = self._analyze()
        symbols_wire = result.get("symbols")
        if not symbols_wire:
            return []
        return [
            Symbol(
                name=entry["name"],
                purpose=entry.get("purpose"),
                export_kind=entry.get("kind", "export"),
                note=entry.get("note"),
            )
            for entry in symbols_wire
        ]

    # --- internals ---------------------------------------------------

    def _resolve_package_dir(self) -> Path:
        """Monorepo package-root resolution (`decisions/0057` §"Monorepo
        package roots"): if `self.project_root` itself is the package
        (its own `package.yaml` declares the matching `name`), use it
        directly. Otherwise search immediate subdirectories for the one
        whose own `package.yaml` declares `name: <config.name>` — never
        hand the adapter process the monorepo root itself.
        """
        own_manifest = self.project_root / "package.yaml"
        if own_manifest.is_file():
            data = _safe_load_yaml(own_manifest)
            if data.get("name") == self.config.name:
                return self.project_root
        for child in sorted(self.project_root.iterdir()):
            if not child.is_dir():
                continue
            candidate = child / "package.yaml"
            if not candidate.is_file():
                continue
            data = _safe_load_yaml(candidate)
            if data.get("name") == self.config.name:
                return child
        raise AdapterError(
            f"{self.config.name}: no package.yaml declaring this name found "
            f"at {self.project_root} or in any of its immediate subdirectories"
        )

    def _resolve_package_yaml(self) -> dict:
        return _safe_load_yaml(self._resolve_package_dir() / "package.yaml")

    def _analyze(self) -> dict:
        if self._cached_analysis is None:
            executable = _adapter_executable(self.project_root)
            process = ExternalAdapterProcess([str(executable)])
            process.initialize()
            try:
                self._cached_analysis = process.analyze_project(
                    self._resolve_package_dir(), self.config.name
                )
            finally:
                process.shutdown()
        return self._cached_analysis


def _render_symbol_line(entry: dict) -> str:
    """One rendered line for a wire `symbols` entry. `kind`/`note`
    (`decisions/0059`) are surfaced explicitly, never silently dropped
    — a `"reexport"`/`"undetermined"` entry is not equivalent in
    confidence to a plain `"export"` one, and this rendering must not
    blur that distinction away.
    """
    kind = entry.get("kind", "export")
    line = f"{entry['name']}: {entry['purpose']}" if entry.get("purpose") else entry["name"]
    if kind != "export":
        line = f"{line} [{kind}]"
    note = entry.get("note")
    if note:
        line = f"{line} — {note}"
    return line


def _dep_node_from_wire(node: dict) -> DepNode:
    result = DepNode(
        name=node["name"], version=node["version"], dev_only=node.get("dev_only", False)
    )
    for child in node.get("children", []):
        result.children.append(_dep_node_from_wire(child))
    return result


def _safe_load_yaml(path: Path) -> dict:
    try:
        with path.open("r", encoding="utf-8") as fp:
            data = yaml.safe_load(fp)
    except OSError as exc:
        raise AdapterError(f"{path}: could not read: {exc}") from exc
    except yaml.YAMLError as exc:
        raise AdapterError(f"{path}: not valid YAML: {exc}") from exc
    if not isinstance(data, dict):
        raise AdapterError(f"{path}: expected a YAML mapping at top level")
    return data


def _adapter_executable(project_root: Path) -> Path:
    """Resolve the built `codecompass-adaptor-haskell` executable inside
    the `adapters/haskell/` git submodule, searching upward from
    `project_root` for the CodeCompass repository root that hosts it —
    the same "the tool lives next to where CodeCompass itself is
    checked out, not inside the analyzed project" relationship every
    external-process adapter has to its host.
    """
    stack_exe = shutil.which("stack")
    if stack_exe is None:
        raise AdapterError(
            "required tool not found: 'stack' — is it installed and on PATH?"
        )
    submodule_dir = _find_adapter_submodule()
    if submodule_dir is None:
        raise AdapterError(
            f"{_ADAPTER_SUBMODULE_DIR} not found — has the "
            "codecompass-adaptor-haskell git submodule been checked out? "
            "See docs/external-adapters.md."
        )
    result = subprocess.run(
        [stack_exe, "path", "--local-install-root"],
        cwd=submodule_dir,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise AdapterError(
            f"'stack path --local-install-root' failed in {submodule_dir} "
            f"(exit {result.returncode}): {result.stderr.strip()} — has "
            "'stack build' been run in adapters/haskell/? See "
            "docs/external-adapters.md."
        )
    install_root = Path(result.stdout.strip())
    executable = install_root / "bin" / "codecompass-adaptor-haskell-exe"
    if not executable.is_file():
        raise AdapterError(
            f"{executable} not found — has 'stack build' been run in "
            f"{submodule_dir}? See docs/external-adapters.md."
        )
    return executable


def _find_adapter_submodule() -> Path | None:
    here = Path(__file__).resolve()
    for ancestor in here.parents:
        candidate = ancestor / _ADAPTER_SUBMODULE_DIR
        if (candidate / "package.yaml").is_file():
            return candidate
    return None
