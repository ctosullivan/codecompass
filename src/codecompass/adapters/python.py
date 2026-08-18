"""Python (PyPI) ecosystem adapter. See architecture/overview.md's Adapter
interface section and decisions/0002.
"""

from __future__ import annotations

import ast
import importlib.metadata
import importlib.util
import sys
from pathlib import Path

from codecompass.adapters.base import AdapterError, EcosystemAdapter, _run_json
from codecompass.core import DepNode, RepositoryLocation
from codecompass.symbols import extract_python_symbols

_PYI_FILE_CAP = 5

# PyPI `project_urls` keys aren't standardized across packages — checked
# case-insensitively, in this priority order (decisions/0021).
_REPOSITORY_URL_LABELS = ("source", "repository", "code", "github", "homepage")


class PythonAdapter(EcosystemAdapter):
    def installed_version(self) -> str:
        try:
            return importlib.metadata.version(self.config.name)
        except importlib.metadata.PackageNotFoundError as exc:
            raise AdapterError(
                f"{self.config.name}: not installed in this environment — "
                "pip install it first"
            ) from exc

    def source_location(self) -> Path:
        spec = importlib.util.find_spec(self.config.name)
        if spec is None or spec.origin is None:
            raise AdapterError(
                f"{self.config.name}: not installed in this environment — "
                "pip install it first"
            )
        return Path(spec.origin).parent

    def repository_url(self) -> RepositoryLocation | None:
        """Installed package metadata's `Project-URL` entries (PEP 621
        `project_urls`, already present locally in `METADATA`/`PKG-INFO`
        — no PyPI network call needed). Keys aren't standardized across
        packages, so `_REPOSITORY_URL_LABELS` is checked in priority
        order; `None` if nothing matches (decisions/0021's fail-loud
        case — the caller does not fall back to a source tarball).
        """
        try:
            urls = importlib.metadata.metadata(self.config.name).get_all("Project-URL") or []
        except importlib.metadata.PackageNotFoundError:
            return None
        by_label = {}
        for entry in urls:
            label, _, url = entry.partition(",")
            by_label[label.strip().lower()] = url.strip()
        for label in _REPOSITORY_URL_LABELS:
            if label in by_label:
                return RepositoryLocation(url=by_label[label])
        return None

    def dependency_tree(self) -> DepNode:
        # Invoked via `sys.executable -m pipdeptree` rather than a bare
        # "pipdeptree" on PATH — pipdeptree is a codecompass dependency
        # installed into this same environment, so this reliably finds
        # it regardless of whether the venv's script shims happen to be
        # on PATH (e.g. an unactivated venv).
        data = _run_json(
            [
                sys.executable,
                "-m",
                "pipdeptree",
                "--output",
                "json-tree",
                "--packages",
                self.config.name,
            ],
            cwd=self.project_root,
        )
        if not data:
            raise AdapterError(
                f"{self.config.name}: not found in pipdeptree output — "
                "is it installed?"
            )
        return self._build_node(data[0])

    def readme_and_api_surface(self) -> str:
        location = self.source_location()
        pyi_files = sorted(location.rglob("*.pyi"))[:_PYI_FILE_CAP]
        if pyi_files:
            parts = []
            for pyi in pyi_files:
                rel = pyi.relative_to(location)
                parts.append(f"# {rel}\n\n{pyi.read_text(encoding='utf-8')}")
            return "\n\n".join(parts)
        return self._ast_fallback(location)

    def _build_node(self, entry: dict) -> DepNode:
        node = DepNode(
            name=entry.get("package_name", entry.get("key", "unknown")),
            version=entry.get("installed_version", "unknown"),
        )
        for child in entry.get("dependencies", []):
            node.children.append(self._build_node(child))
        return node

    def _ast_fallback(self, location: Path) -> str:
        """Static-parse the package's __init__.py for __all__ and
        top-level docstrings — chosen over actually importing the
        installed module, which would execute unrelated module-level
        side effects purely to generate documentation. See
        planning/phase-2-ecosystem-adapters.md's Design decisions.

        Per-symbol extraction is delegated to `codecompass.symbols`
        (generalized in Phase 3 for reuse by `filetree.py`); `__all__`
        extraction stays here since it's module-level data, not a symbol.
        """
        init_file = location / "__init__.py"
        if not init_file.exists():
            return ""
        parts: list[str] = []

        all_names = self._extract_all(ast.parse(init_file.read_text(encoding="utf-8")))
        if all_names:
            parts.append("__all__ = " + ", ".join(all_names))

        for symbol in extract_python_symbols(init_file):
            parts.append(f"{symbol.name}: {symbol.purpose}" if symbol.purpose else symbol.name)

        return "\n".join(parts)

    @staticmethod
    def _extract_all(tree: ast.Module) -> list[str]:
        for node in ast.iter_child_nodes(tree):
            if not isinstance(node, ast.Assign):
                continue
            if not any(isinstance(t, ast.Name) and t.id == "__all__" for t in node.targets):
                continue
            if isinstance(node.value, ast.List | ast.Tuple):
                return [
                    elt.value
                    for elt in node.value.elts
                    if isinstance(elt, ast.Constant) and isinstance(elt.value, str)
                ]
        return []
