"""Python (PyPI) ecosystem adapter. See architecture/overview.md's Adapter
interface section and decisions/0002.
"""

from __future__ import annotations

import ast
import importlib.metadata
import importlib.util
import sys
from pathlib import Path

from depcompass.adapters.base import AdapterError, EcosystemAdapter, _run_json
from depcompass.core import DepNode

_PYI_FILE_CAP = 5


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

    def dependency_tree(self) -> DepNode:
        # Invoked via `sys.executable -m pipdeptree` rather than a bare
        # "pipdeptree" on PATH — pipdeptree is a depcompass dependency
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
        """
        init_file = location / "__init__.py"
        if not init_file.exists():
            return ""
        tree = ast.parse(init_file.read_text(encoding="utf-8"))
        parts: list[str] = []

        all_names = self._extract_all(tree)
        if all_names:
            parts.append("__all__ = " + ", ".join(all_names))

        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef):
                docstring = ast.get_docstring(node)
                parts.append(f"{node.name}: {docstring}" if docstring else node.name)

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
