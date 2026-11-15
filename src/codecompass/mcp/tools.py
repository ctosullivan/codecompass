"""Phase 88 -- the nine Stage 88A (read-only) MCP tool implementations.
One function per tool, each a thin wrapper delegating to `knowledge_api`/
`knowledge_intermediate`/`oracle`. See `planning/
phase-88-agent-integration-mcp.md` §6 for each tool's full spec -- this
module implements it, it does not re-derive it.

No function here re-derives a knowledge fact, re-parses a record, or
re-implements a traversal/aggregation rule that already exists in the
modules it wraps. Every response is one of those modules' own
`ApiResponse.to_dict()` (or an equally thin, explicitly-shaped dict for
the two tools with no existing `ApiResponse`-shaped delegate, `docs_
get_grounded_region` and `server_capabilities`), enveloped with
`project_revision`/`target_revision` (§5.6) without altering the
delegate's own fields.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from mcp.server.mcpserver.exceptions import ToolError

from codecompass import knowledge_api as _ka
from codecompass import knowledge_intermediate as _ki

from . import security as _sec


def _envelope(
    payload: dict[str, Any], *, project_root: Path, target_root: Path | None
) -> dict[str, Any]:
    out = dict(payload)
    out["project_revision"] = _ka._git_head_revision(project_root)
    out["target_revision"] = (
        _ka._git_head_revision(target_root) if target_root is not None else None
    )
    return out


def _response(
    config: _sec.ServerConfig, resp: _ka.ApiResponse, *, target_root: Path | None
) -> dict[str, Any]:
    return _envelope(resp.to_dict(), project_root=config.project_root, target_root=target_root)


# ---------------------------------------------------------------------------
# 1. knowledge_get
# ---------------------------------------------------------------------------


def knowledge_get(
    config: _sec.ServerConfig, record_id: str, repo_root_key: str | None = None
) -> dict[str, Any]:
    _sec.require_non_empty_str(record_id, "record_id")
    target_root = _sec.resolve_repo_root(config, repo_root_key)
    resp = _ka.get(config.project_root, record_id, repo_root=target_root)
    return _response(config, resp, target_root=target_root)


# ---------------------------------------------------------------------------
# 2. knowledge_search
# ---------------------------------------------------------------------------


def knowledge_search(
    config: _sec.ServerConfig,
    text: str,
    kinds: list[str] | None = None,
    limit: int = 20,
) -> dict[str, Any]:
    _sec.require_non_empty_str(text, "text")
    clamped_limit, was_clamped = _sec.clamp_limit(limit)
    resp = _ka.search(config.project_root, text, kinds)
    payload = resp.to_dict()
    total = len(payload["results"])
    if total > clamped_limit:
        payload["results"] = payload["results"][:clamped_limit]
        payload["truncated"] = True
    else:
        payload["truncated"] = False
    payload["limit_applied"] = clamped_limit
    payload["limit_clamped"] = was_clamped
    return _envelope(payload, project_root=config.project_root, target_root=None)


# ---------------------------------------------------------------------------
# 3. knowledge_traverse
# ---------------------------------------------------------------------------


def knowledge_traverse(
    config: _sec.ServerConfig,
    record_id: str,
    relation: str,
    depth: int = 1,
    limit: int = 20,
    repo_root_key: str | None = None,
) -> dict[str, Any]:
    _sec.require_non_empty_str(record_id, "record_id")
    _sec.validate_relation(relation)
    clamped_limit, was_clamped = _sec.clamp_limit(limit)
    target_root = _sec.resolve_repo_root(config, repo_root_key)
    resp = _ka.traverse(config.project_root, record_id, relation, depth, repo_root=target_root)
    payload = resp.to_dict()
    total = len(payload["results"])
    if total > clamped_limit:
        payload["results"] = payload["results"][:clamped_limit]
        payload["truncated"] = True
    else:
        payload["truncated"] = False
    payload["limit_applied"] = clamped_limit
    payload["limit_clamped"] = was_clamped
    return _envelope(payload, project_root=config.project_root, target_root=target_root)


# ---------------------------------------------------------------------------
# 4. knowledge_trace_evidence
# ---------------------------------------------------------------------------


def knowledge_trace_evidence(
    config: _sec.ServerConfig, record_id: str, repo_root_key: str | None = None
) -> dict[str, Any]:
    _sec.require_non_empty_str(record_id, "record_id")
    target_root = _sec.resolve_repo_root(config, repo_root_key)
    resp = _ka.trace_evidence(config.project_root, record_id, repo_root=target_root)
    return _response(config, resp, target_root=target_root)


# ---------------------------------------------------------------------------
# 5. knowledge_epistemic_status
# ---------------------------------------------------------------------------


def knowledge_epistemic_status(
    config: _sec.ServerConfig, record_id: str, repo_root_key: str | None = None
) -> dict[str, Any]:
    _sec.require_non_empty_str(record_id, "record_id")
    target_root = _sec.resolve_repo_root(config, repo_root_key)
    resp = _ka.epistemic_status(config.project_root, record_id, repo_root=target_root)
    return _response(config, resp, target_root=target_root)


# ---------------------------------------------------------------------------
# 6. knowledge_context_packet
# ---------------------------------------------------------------------------


def knowledge_context_packet(
    config: _sec.ServerConfig,
    topic: str,
    max_items: int = 20,
    max_chars: int = 6000,
    repo_root_key: str | None = None,
) -> dict[str, Any]:
    _sec.require_non_empty_str(topic, "topic")
    if max_items <= 0:
        raise ToolError("max_items must be a positive integer")
    if max_chars <= 0:
        raise ToolError("max_chars must be a positive integer")
    target_root = _sec.resolve_repo_root(config, repo_root_key)
    resp = _ka.get_context_packet(
        config.project_root, topic, max_items=max_items, max_chars=max_chars, repo_root=target_root
    )
    return _response(config, resp, target_root=target_root)


# ---------------------------------------------------------------------------
# 7. knowledge_find_gaps
# ---------------------------------------------------------------------------


def knowledge_find_gaps(
    config: _sec.ServerConfig, slug: str | None = None, repo_root_key: str | None = None
) -> dict[str, Any]:
    if slug is not None:
        _sec.require_known_slug(config.project_root, slug)
    target_root = _sec.resolve_repo_root(config, repo_root_key)
    resp = _ka.find_gaps(config.project_root, slug, repo_root=target_root)
    return _response(config, resp, target_root=target_root)


# ---------------------------------------------------------------------------
# 8. docs_get_grounded_region
# ---------------------------------------------------------------------------


def docs_get_grounded_region(
    config: _sec.ServerConfig, doc_path: str, region_id: str | None = None
) -> dict[str, Any]:
    """Retrieve a published documentation region and its current
    grounding (plan §6 tool 8). `doc_path` is confined to the real,
    schema-governed document set (`security.ServerConfig.
    allowed_doc_paths`, re-derived from the real `**/*.schema.yaml`
    files, never hardcoded) -- a path outside this set is a validation
    error, never an arbitrary-file-read primitive."""
    _sec.validate_doc_path(config, doc_path)
    full_path = config.project_root / doc_path
    try:
        text = full_path.read_text(encoding="utf-8")
    except OSError:
        return _envelope(
            {"status": "empty", "regions": []}, project_root=config.project_root, target_root=None
        )

    markers = _ki.parse_grounding_markers(text)
    regions: list[dict[str, Any]] = []
    for i, (cited_ids, body, marker_region_id) in enumerate(markers):
        real_region_id = marker_region_id or f"{doc_path}::{i}"
        if region_id is not None and real_region_id != region_id:
            continue
        grounded_by: list[dict[str, Any]] = []
        for claim_id in cited_ids:
            claim_resp = _ka.get(config.project_root, claim_id)
            if claim_resp.status == "empty":
                grounded_by.append({"claim_id": claim_id, "status": "missing"})
            else:
                grounded_by.append(
                    {"claim_id": claim_id, "status": claim_resp.results[0].consistency.status}
                )
        regions.append({"region_id": real_region_id, "body": body, "grounded_by": grounded_by})

    status = "result" if regions else "empty"
    return _envelope(
        {"status": status, "regions": regions}, project_root=config.project_root, target_root=None
    )


# ---------------------------------------------------------------------------
# 9. server_capabilities
# ---------------------------------------------------------------------------


def server_capabilities(config: _sec.ServerConfig) -> dict[str, Any]:
    return {
        "repo_root_keys": sorted(config.repo_roots),
        "execution_enabled": config.execution_enabled,
        "codecompass_version": config.codecompass_version,
    }
