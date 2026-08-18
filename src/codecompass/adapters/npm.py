"""npm ecosystem adapter. See architecture/overview.md's Adapter interface
section and decisions/0002.
"""

from __future__ import annotations

import json
from pathlib import Path

from codecompass.adapters.base import AdapterError, EcosystemAdapter, _run_json
from codecompass.core import DepNode, RepositoryLocation

_DTS_FILE_CAP = 5


class NpmAdapter(EcosystemAdapter):
    def installed_version(self) -> str:
        return self._package_json()["version"]

    def source_location(self) -> Path:
        return self._package_dir()

    def repository_url(self) -> RepositoryLocation | None:
        """`package.json`'s `repository` field — a bare string
        (`"github:user/repo"`, `"git+https://.../repo.git"`, or a plain
        URL) or an object (`{"type": "git", "url": "...", "directory":
        "packages/foo"}`). `directory` scopes a monorepo package to its
        subdirectory (decisions/0021) — respected here, not dropped.
        """
        repository = self._package_json().get("repository")
        if repository is None:
            return None
        if isinstance(repository, str):
            url, subdirectory = repository, None
        else:
            url, subdirectory = repository.get("url"), repository.get("directory")
        if not url:
            return None
        return RepositoryLocation(url=_normalize_git_url(url), subdirectory=subdirectory)

    def dependency_tree(self) -> DepNode:
        data = _run_json(
            ["npm", "ls", self.config.name, "--json", "--all"],
            cwd=self.project_root,
        )
        entry = data.get("dependencies", {}).get(self.config.name)
        if entry is None:
            raise AdapterError(
                f"{self.config.name}: not found in npm ls output — is it installed?"
            )
        dev_deps = set(self._root_package_json().get("devDependencies", {}))
        root = self._build_node(self.config.name, entry, dev_deps)
        postinstall = self._package_json().get("scripts", {}).get("postinstall")
        if postinstall:
            root.side_effects.append(f"npm postinstall script: {postinstall}")
        return root

    def readme_and_api_surface(self) -> str:
        location = self.source_location()
        parts: list[str] = []
        for readme in sorted(location.glob("README*"))[:1]:
            parts.append(f"# {readme.name}\n\n{readme.read_text(encoding='utf-8')}")
        for dts in sorted(location.rglob("*.d.ts"))[:_DTS_FILE_CAP]:
            rel = dts.relative_to(location)
            parts.append(f"# {rel}\n\n{dts.read_text(encoding='utf-8')}")
        return "\n\n".join(parts)

    def _build_node(self, name: str, entry: dict, dev_deps: set[str]) -> DepNode:
        node = DepNode(
            name=name,
            version=entry.get("version", "unknown"),
            dev_only=name in dev_deps,
        )
        for child_name, child_entry in entry.get("dependencies", {}).items():
            node.children.append(self._build_node(child_name, child_entry, dev_deps))
        return node

    def _package_dir(self) -> Path:
        return self.project_root / "node_modules" / self.config.name

    def _package_json(self) -> dict:
        path = self._package_dir() / "package.json"
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except OSError as exc:
            raise AdapterError(
                f"{self.config.name}: not found at "
                f"node_modules/{self.config.name}/package.json — "
                "run npm install first"
            ) from exc

    def _root_package_json(self) -> dict:
        path = self.project_root / "package.json"
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except OSError:
            return {}


_SHORTHAND_HOSTS = {
    "github": "github.com",
    "gitlab": "gitlab.com",
    "bitbucket": "bitbucket.org",
}


def _normalize_git_url(url: str) -> str:
    """`git clone`-able form of an npm `repository.url` value.

    Handles the two non-plain-URL forms npm accepts: the `git+` scheme
    prefix (`"git+https://github.com/user/repo.git"`) and the
    `github:`/`gitlab:`/`bitbucket:` host-shorthand (`"github:user/repo"`).
    A plain URL passes through unchanged.
    """
    if url.startswith("git+"):
        return url[len("git+") :]
    for shorthand, host in _SHORTHAND_HOSTS.items():
        prefix = f"{shorthand}:"
        if url.startswith(prefix):
            return f"https://{host}/{url[len(prefix):]}"
    return url
