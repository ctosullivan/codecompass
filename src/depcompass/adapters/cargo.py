"""Cargo (crates.io) ecosystem adapter.

**Unverified against real cargo output** — no Rust toolchain in this dev
environment as of Phase 2. Built entirely against the `_run_json` seam so
its parsing logic is unit-tested via hand-written fixture JSON modeled on
cargo's public `cargo metadata --format-version 1` schema docs. See
decisions/0014 and architecture/overview.md's Known footguns.
"""

from __future__ import annotations

from pathlib import Path

from depcompass.adapters.base import AdapterError, EcosystemAdapter, _run_json
from depcompass.core import DepNode
from depcompass.symbols import extract_rust_symbols


class CargoAdapter(EcosystemAdapter):
    def installed_version(self) -> str:
        metadata = self._metadata(no_deps=True)
        return self._find_package(metadata)["version"]

    def source_location(self) -> Path:
        metadata = self._metadata(no_deps=True)
        package = self._find_package(metadata)
        return Path(package["manifest_path"]).parent

    def dependency_tree(self) -> DepNode:
        metadata = self._metadata(no_deps=False)
        packages_by_id = {p["id"]: p for p in metadata.get("packages", [])}
        resolve_nodes_by_id = {
            n["id"]: n for n in metadata.get("resolve", {}).get("nodes", [])
        }

        root_package = self._find_package(metadata)
        root_id = root_package["id"]

        def kind_for_child(parent_package: dict, child_name: str) -> str | None:
            for dep in parent_package.get("dependencies", []):
                if dep.get("name") == child_name:
                    return dep.get("kind")
            return None

        def build(node_id: str, dev_only: bool, visited: set[str]) -> DepNode:
            package = packages_by_id[node_id]
            node = DepNode(name=package["name"], version=package["version"], dev_only=dev_only)
            if node_id in visited:
                # Cycle guard — a defensive implementation detail, not
                # Phase 3's semantic diamond-dependency dedup.
                return node
            visited = visited | {node_id}
            for dep_id in resolve_nodes_by_id.get(node_id, {}).get("dependencies", []):
                child_package = packages_by_id[dep_id]
                kind = kind_for_child(package, child_package["name"])
                node.children.append(build(dep_id, kind == "dev", visited))
            return node

        return build(root_id, False, set())

    def readme_and_api_surface(self) -> str:
        location = self.source_location()
        parts: list[str] = []
        for readme in sorted(location.glob("README*"))[:1]:
            parts.append(f"# {readme.name}\n\n{readme.read_text(encoding='utf-8')}")
        src_dir = location / "src"
        if src_dir.exists():
            for rs_file in sorted(src_dir.rglob("*.rs")):
                symbols = extract_rust_symbols(rs_file)
                if symbols:
                    rel = rs_file.relative_to(location)
                    items = [
                        f"{s.name}: {s.purpose}" if s.purpose else s.name for s in symbols
                    ]
                    parts.append(f"# {rel}\n\n" + "\n\n".join(items))
        return "\n\n".join(parts)

    def _metadata(self, *, no_deps: bool) -> dict:
        cmd = ["cargo", "metadata", "--format-version", "1"]
        if no_deps:
            cmd.append("--no-deps")
        return _run_json(cmd, cwd=self.project_root)

    def _find_package(self, metadata: dict) -> dict:
        for package in metadata.get("packages", []):
            if package.get("name") == self.config.name:
                return package
        raise AdapterError(
            f"{self.config.name}: not found in cargo metadata output — "
            "is it a dependency of this project?"
        )
