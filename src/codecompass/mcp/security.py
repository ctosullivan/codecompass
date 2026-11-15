"""Phase 88 -- MCP server-side security primitives: repo-root pinning,
slug-allowlist enforcement, relation/doc-path validation, execution-mode
gating, and response-size bounding. See `planning/
phase-88-agent-integration-mcp.md` §4/§5 for the full design -- this
module implements it, it does not re-derive it.

No tool ever accepts a caller-supplied filesystem path for a target
repository. `repo_root_key` is always a symbolic key resolved against a
fixed `--repo-root <key>=<path>` mapping given at server startup; a
`slug` is always validated against the server's own real, enumerated
slug list (`knowledge_intermediate._list_slugs`) before it reaches any
delegate (§5.2). Raising `ToolError` here is what turns a rejection into
a structured, explicit MCP `isError: true` response -- never a silent
no-op, never a degraded result masquerading as a legitimate answer.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from mcp.server.mcpserver.exceptions import ToolError

from codecompass import knowledge_api as _ka
from codecompass import knowledge_intermediate as _ki

# Phase 87's own five schema-governed documents -- re-derived here from
# the real `**/*.schema.yaml` files at import time (never hardcoded from
# the plan's own memory, per the plan's own explicit instruction, §6
# tool 8), so this allowlist can never silently drift from what Phase 87
# actually ships.


def _discover_allowed_doc_paths(project_root: Path) -> tuple[str, ...]:
    paths: list[str] = []
    for schema_path in sorted(project_root.glob("**/*.md.schema.yaml")):
        if ".venv" in schema_path.parts or "node_modules" in schema_path.parts:
            continue
        doc_path = schema_path.relative_to(project_root)
        paths.append(str(doc_path)[: -len(".schema.yaml")])
    return tuple(paths)


# Every base (forward) relation `knowledge_api.traverse` recognises via a
# literal cross-reference field, reused directly rather than duplicated
# -- drift-proof by construction (`traverse` itself is the only place
# that actually interprets these strings).
_BASE_FIELD_RELATIONS = tuple(_ka._FORWARD_FIELD_RELATIONS)
_SPECIAL_RELATIONS = ("cites", "cited_by", "checks", "results", "doc_mentions")
ALL_RELATIONS = frozenset(
    _BASE_FIELD_RELATIONS
    + tuple(f"{r}_reverse" for r in _BASE_FIELD_RELATIONS)
    + _SPECIAL_RELATIONS
)


@dataclass(frozen=True)
class ServerConfig:
    """Everything a tool call needs to know about how this server
    instance was started -- set once, at `codecompass mcp-serve` launch,
    never mutated by any MCP call (there is no tool that writes to it)."""

    project_root: Path
    repo_roots: dict[str, Path] = field(default_factory=dict)
    execution_enabled: bool = False
    codecompass_version: str = "unknown"
    allowed_doc_paths: tuple[str, ...] = ()

    @classmethod
    def build(
        cls,
        project_root: Path,
        repo_roots: dict[str, Path],
        *,
        execution_enabled: bool = False,
        codecompass_version: str = "unknown",
    ) -> ServerConfig:
        return cls(
            project_root=project_root,
            repo_roots=dict(repo_roots),
            execution_enabled=execution_enabled,
            codecompass_version=codecompass_version,
            allowed_doc_paths=_discover_allowed_doc_paths(project_root),
        )


def resolve_repo_root(config: ServerConfig, repo_root_key: str | None) -> Path | None:
    """`None` in, `None` out (no target repo consulted) -- an unknown
    *non-`None`* key is always a tool error, never silently ignored."""
    if repo_root_key is None:
        return None
    try:
        return config.repo_roots[repo_root_key]
    except KeyError:
        raise ToolError(
            f"unknown repo_root_key {repo_root_key!r} -- configured keys: "
            f"{sorted(config.repo_roots)}"
        ) from None


def require_known_slug(project_root: Path, slug: str) -> str:
    known = _ki._list_slugs(project_root)
    if slug not in known:
        raise ToolError(f"unknown slug {slug!r} -- known slugs: {known}")
    return slug


def require_non_empty_str(value: str, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ToolError(f"{field_name} must be a non-empty string")
    return value


def validate_relation(relation: str) -> str:
    if relation not in ALL_RELATIONS:
        raise ToolError(f"unknown relation {relation!r} -- must be one of {sorted(ALL_RELATIONS)}")
    return relation


def validate_doc_path(config: ServerConfig, doc_path: str) -> str:
    if doc_path not in config.allowed_doc_paths:
        raise ToolError(
            f"doc_path {doc_path!r} is not an approved documentation target -- "
            f"must be one of {config.allowed_doc_paths}"
        )
    return doc_path


def clamp_limit(limit: int, *, lo: int = 1, hi: int = 100) -> tuple[int, bool]:
    """Returns `(clamped_value, was_clamped)` -- an out-of-range `limit`
    is clamped, not rejected, with the clamp disclosed in the response
    rather than silently applied (§6 tool 2)."""
    clamped = max(lo, min(hi, limit))
    return clamped, clamped != limit


def require_enabled_execution(config: ServerConfig) -> None:
    if not config.execution_enabled:
        raise ToolError(
            "oracle_execute_check is disabled -- this server was started without "
            "--enable-execution (the default, read-only mode)"
        )
