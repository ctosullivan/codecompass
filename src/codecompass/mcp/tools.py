"""Phase 88 -- the twelve MCP tool implementations (Stage 88A's nine
read-only tools, Stage 88B's three assurance tools). One function per
tool, each a thin wrapper delegating to `knowledge_api`/
`knowledge_intermediate`/`oracle`/`change_impact`. See `planning/
phase-88-agent-integration-mcp.md` §6 for each tool's full spec -- this
module implements it, it does not re-derive it.

No function here re-derives a knowledge fact, re-parses a record, or
re-implements a traversal/aggregation/classification rule that already
exists in the modules it wraps. Every response is one of those modules'
own `ApiResponse.to_dict()`/report dict (or an equally thin, explicitly-
shaped dict for the tools with no existing such delegate), enveloped
with `project_revision`/`target_revision` (§5.6) without altering the
delegate's own fields.
"""

from __future__ import annotations

import contextlib
import os
from pathlib import Path
from typing import Any

from mcp.server.mcpserver.exceptions import ToolError

from codecompass import change_impact as _ci
from codecompass import knowledge_api as _ka
from codecompass import knowledge_intermediate as _ki
from codecompass import oracle as _oracle

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
    with _chdir(config.project_root):
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
    with _chdir(config.project_root):
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
    with _chdir(config.project_root):
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
    with _chdir(config.project_root):
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
    with _chdir(config.project_root):
        resp = _ka.get_context_packet(
            config.project_root, topic, max_items=max_items, max_chars=max_chars,
            repo_root=target_root,
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
    with _chdir(config.project_root):
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
            with _chdir(config.project_root):
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


# ---------------------------------------------------------------------------
# Stage 88B -- assurance tools (10-12)
# ---------------------------------------------------------------------------


@contextlib.contextmanager
def _chdir(path: Path):
    """Scoped, restored `chdir`.

    A committed `oracle-result.yaml`'s own `raw_output_ref` is stored as
    a *relative* path (`scripts/run_balance_from_spec_oracle.py`'s own
    established convention, so the file stays portable across
    checkouts/machines) -- and `oracle.evaluate_result_precedence`
    (called by `aggregate_contract`, in turn called by every
    `knowledge_*` tool that surfaces a consistency envelope, plus both
    `oracle_list_checks` and `oracle_execute_check`) checks that stored
    relative path against disk with a plain `Path(ref).is_file()`,
    which only resolves correctly when the process's own cwd is
    `project_root`. The maintainer CLI already guarantees this by
    convention (every `codecompass` invocation runs from the project
    root the user is standing in); the MCP server has no such
    guarantee -- its own cwd at launch is whatever directory it
    happened to be started from. Every tool function in this module
    therefore wraps its own delegate call in this context manager
    rather than relying on the server's launch-time cwd, so correctness
    never depends on how or where the server process was started, and
    a direct unit-test call (bypassing the server entirely) behaves
    identically. Restores the original cwd unconditionally, never
    leaving a global side effect behind after any one call returns."""
    previous = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(previous)


def _contracts_root(project_root: Path) -> Path:
    return project_root / "planning" / "contracts"


def impact_classify_change(
    config: _sec.ServerConfig, repo_root_key: str, slug: str, changed: list[dict]
) -> dict[str, Any]:
    """Assesses a proposed source change's relationship to existing
    knowledge/evidence -- read-only classification, no check execution
    (plan §6 tool 10). Returns the real, relocated `change_impact.
    assess(..., run_checks=False)` report verbatim, field-for-field,
    with the server's own real local filesystem paths
    (`target_repo_root`/`target_graph_db`/`knowledge_root`) replaced by
    `repo_root_key`/`target_revision` so no local path ever crosses the
    MCP boundary -- the only transformation applied."""
    _sec.require_non_empty_str(repo_root_key, "repo_root_key")
    target_root = _sec.resolve_repo_root(config, repo_root_key)
    _sec.require_known_slug(config.project_root, slug)
    if not changed:
        raise ToolError("changed must be a non-empty list of {path, start, end} entries")
    # Validated before `confine_changed_paths` ever indexes `c["path"]`
    # -- a malformed entry (a missing key, or a non-dict item) must be
    # a structured ToolError, never a bare, uncaught KeyError/TypeError
    # escaping this function (§5.8's own malformed-input-test
    # convention, applied to this tool's own compound input shape).
    for c in changed:
        if not isinstance(c, dict) or not {"path", "start", "end"} <= c.keys():
            raise ToolError(
                f"malformed changed[] entry {c!r}: each entry must be a mapping with "
                "'path', 'start', and 'end' keys"
            )
    _sec.confine_changed_paths(target_root, changed)

    try:
        changed_ranges = [
            _ci.ChangedRange(path=c["path"], start=c["start"], end=c["end"]) for c in changed
        ]
    except (KeyError, TypeError) as exc:
        raise ToolError(f"malformed changed[] entry: {exc}") from exc
    for cr in changed_ranges:
        valid = (
            isinstance(cr.start, int) and isinstance(cr.end, int)
            and cr.start >= 1 and cr.end >= cr.start
        )
        if not valid:
            raise ToolError(
                f"changed entry {cr.path!r}: start/end must be integers with "
                "start >= 1 and end >= start"
            )

    report = _ci.assess(
        target_repo_root=target_root,
        target_graph_db=target_root / "context-graph.db",
        knowledge_root=config.project_root,
        slug=slug,
        changed=changed_ranges,
        run_checks=False,
    )
    report.pop("target_repo_root", None)
    report.pop("target_graph_db", None)
    report.pop("knowledge_root", None)
    report["target_revision"] = _ka._git_head_revision(target_root)
    report["project_revision"] = _ka._git_head_revision(config.project_root)
    return report


def oracle_list_checks(config: _sec.ServerConfig, slug: str) -> dict[str, Any]:
    """Surfaces the real, on-disk allowlist for `slug` -- what
    `oracle_execute_check` will actually accept (plan §6 tool 11).
    `latest_result_status` is `aggregate_contract`'s own
    `CheckAggregate.state` (`"PASS"|"GAP"|"NOT_REQUIRED"`) for that
    check against every currently-recorded result -- a check-level
    question, never a single result's raw or effective outcome
    (corrected §18.3)."""
    _sec.require_known_slug(config.project_root, slug)
    contract_path = _contracts_root(config.project_root) / slug / "oracle-contract.yaml"
    if not contract_path.is_file():
        return _envelope({"checks": []}, project_root=config.project_root, target_root=None)
    try:
        contract = _oracle.parse_oracle_contract(contract_path)
    except _oracle.OracleSchemaError as exc:
        raise ToolError(f"malformed oracle-contract.yaml for slug {slug!r}: {exc}") from None

    results_dir = _contracts_root(config.project_root) / slug / "results"
    results: list[_oracle.OracleResult] = []
    if results_dir.is_dir():
        for result_path in sorted(results_dir.glob("*.yaml")):
            try:
                results.append(_oracle.parse_oracle_result(result_path))
            except _oracle.OracleSchemaError:
                continue
    # `evaluate_result_precedence` (inside `aggregate_contract`) checks
    # each result's own *relative* `raw_output_ref` against disk --
    # resolves correctly only when the process's cwd is `project_root`,
    # the same relative-path convention `oracle_execute_check` already
    # honours (see that function's own comment).
    with _chdir(config.project_root):
        aggregates = _oracle.aggregate_contract(contract, results, contract_path=contract_path)
    state_by_check = {a.check_id: a.state for a in aggregates}

    checks = [
        {
            "contract_id": contract.contract_id,
            "check_id": check.check_id,
            "description": check.scope,
            "required": check.required,
            "check_reference": check.check_reference,
            "latest_result_status": state_by_check.get(check.check_id, "NOT_REQUIRED"),
        }
        for check in contract.checks
    ]
    return _envelope({"checks": checks}, project_root=config.project_root, target_root=None)


def oracle_execute_check(
    config: _sec.ServerConfig, slug: str, contract_id: str, check_id: str, repo_root_key: str
) -> dict[str, Any]:
    """The one controlled-verification execute operation (plan §6 tool
    12). Rejects immediately, before any subprocess, if: the server was
    not started with `--enable-execution`; `(slug, contract_id,
    check_id)` does not resolve against the real, on-disk `oracle-
    contract.yaml`; or `repo_root_key` does not resolve against the
    server's own pinned mapping. Writes exactly one new, append-only
    `OracleResult` file -- never overwrites or deletes an existing one.

    **Output, corrected §18.3**: `outcome` (`"PASS"|"FAIL"|"INVALID"`)
    is this call's own fresh `OracleResult.outcome`; `aggregate_state`
    (`"PASS"|"GAP"|"NOT_REQUIRED"`) is `aggregate_contract`'s own
    `CheckAggregate.state` for this `(contract_id, check_id)`,
    recomputed immediately after persisting the new result -- the two
    are never merged into one field."""
    _sec.require_enabled_execution(config)
    _sec.require_known_slug(config.project_root, slug)
    target_root = _sec.resolve_repo_root(config, repo_root_key)
    if target_root is None:
        raise ToolError("repo_root_key is required for oracle_execute_check")

    contracts_dir = _contracts_root(config.project_root) / slug
    contract_path = contracts_dir / "oracle-contract.yaml"
    if not contract_path.is_file():
        raise ToolError(f"no oracle-contract.yaml for slug {slug!r}")
    try:
        contract = _oracle.parse_oracle_contract(contract_path)
    except _oracle.OracleSchemaError as exc:
        raise ToolError(f"malformed oracle-contract.yaml for slug {slug!r}: {exc}") from None
    if contract.contract_id != contract_id:
        raise ToolError(
            f"contract_id {contract_id!r} does not match slug {slug!r}'s real "
            f"contract_id {contract.contract_id!r}"
        )
    check = contract.check_by_id(check_id)
    if check is None:
        raise ToolError(
            f"unknown check_id {check_id!r} for contract {contract_id!r} -- "
            f"known check ids: {[c.check_id for c in contract.checks]}"
        )

    results_dir = contracts_dir / "results"
    # The whole sequence -- fresh execution, persisting the new result,
    # and recomputing the aggregate -- runs under one scoped chdir, not
    # only the write step: `evaluate_result_precedence` (called inside
    # `aggregate_contract`) independently re-checks each existing
    # result's own *relative* `raw_output_ref` against disk, which only
    # resolves correctly when the process's cwd is `project_root` --
    # exactly the same relative-path convention `write_oracle_result`'s
    # caller relies on, applied consistently to reads as well as this
    # call's own write.
    with _chdir(config.project_root):
        raw_dir = results_dir.relative_to(config.project_root) / "raw"
        result = _oracle.evaluate_check(
            contract, check, contract_path=contract_path,
            repo_root=target_root, raw_output_dir=raw_dir,
        )
        out_path = results_dir / f"{check.check_id}--{result.run_id}.yaml"
        _oracle.write_oracle_result(out_path, result)

        all_results: list[_oracle.OracleResult] = []
        if results_dir.is_dir():
            for result_path in sorted(results_dir.glob("*.yaml")):
                try:
                    all_results.append(_oracle.parse_oracle_result(result_path))
                except _oracle.OracleSchemaError:
                    continue
        aggregates = _oracle.aggregate_contract(
            contract, all_results, contract_path=contract_path, repo_root=target_root
        )
        aggregate = next((a for a in aggregates if a.check_id == check_id), None)

    return _envelope(
        {
            "outcome": result.outcome,
            "invalid_reason": result.invalid_reason,
            "aggregate_state": aggregate.state if aggregate else None,
            "raw_output_ref": result.raw_output_ref,
            "run_id": result.run_id,
        },
        project_root=config.project_root,
        target_root=target_root,
    )
