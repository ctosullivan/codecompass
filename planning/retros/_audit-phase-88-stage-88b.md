# Audit: Phase 88, Stage 88B (Assurance integration)

**Scope**: the uncommitted working-tree diff described in the dispatch —
`src/codecompass/change_impact.py` (new), `oracle.py` hardening (§5.3),
`mcp/security.py::confine_changed_paths`, `mcp/tools.py` tools 10-12 plus
the `_chdir` retrofit across all twelve tools, `mcp/server.py`
registration, `tests/test_mcp_assurance.py`,
`tests/test_oracle_bounded_execution.py`, `tests/test_mcp_server.py`
(tool-count update), `docs/reference/mcp.md`, `docs/architecture/
components.md`, and the two new real result files under
`planning/contracts/balance-from-spec/results/`. This is **not** the
terminal Phase 88 DoD audit — the Ledgerkit demonstration, final
documentation/retro, and learnings triage remain separately gated.

**Verdict: PASS WITH NON-BLOCKING OBSERVATIONS**

## What was independently re-run (not trusted from self-report)

1. **Full test suite**, `.venv/bin/python -m pytest tests/ -q`:
   `1461 passed, 2 skipped in 474.98s` — matches the reported count
   exactly, confirmed by my own run, not assumed.
2. **Ruff, whole repo**: `.venv/bin/ruff check . --statistics` →
   `Found 167 errors` (162 E501, 2 F841, 1 UP037, 1 I001, 1 F401).
   Re-confirmed the claimed 176-finding baseline myself via
   `git stash -u` against the working tree (restoring commit 7a96d89's
   committed state) → `Found 176 errors`, identical breakdown except
   171 vs 162 E501. **167 < 176 — no increase**, consistent with
   `scripts/assess_change_impact.py` shrinking from 638 lines to a
   thin wrapper (removing long lines, not adding any). `git stash pop`
   restored the working tree; confirmed via the subsequent `git status`
   output shown inline that nothing was lost.
   `.venv/bin/ruff check src/codecompass/change_impact.py
   scripts/assess_change_impact.py src/codecompass/mcp/tools.py
   src/codecompass/mcp/security.py src/codecompass/mcp/server.py
   src/codecompass/oracle.py tests/test_mcp_assurance.py
   tests/test_oracle_bounded_execution.py tests/test_mcp_server.py` →
   **All checks passed.** Every new/changed Python file this phase
   touches is Ruff-clean, as required.
3. **`.venv/bin/python scripts/check_user_docs.py --strict`** →
   `check_user_docs: no findings`.
4. **`_chdir` retrofit correctness** — independently reproduced (scratch
   script, not the project's own tests). Built a synthetic target
   repo + knowledge/contract fixture, ran `oracle_execute_check` (fresh
   `PASS`), then called `oracle_list_checks`/`knowledge_epistemic_
   status`/`knowledge_find_gaps` with the process cwd deliberately set
   to `/` vs. left at `project_root`: **identical results in both
   cases** (`oracle_list_checks`'s `latest_result_status` == `"PASS"`
   either way). To confirm the fix is load-bearing (not merely
   harmless), I monkey-patched `mcp_tools._chdir` to a true no-op and
   re-ran: with cwd == `project_root` it still reported `PASS`, but
   with cwd == `/` it silently misclassified as **`GAP`** — reproducing
   exactly the defect the retrofit exists to prevent. This confirms (a)
   the fix is genuinely necessary, and (b) the real implementation
   closes it for every path I exercised (`oracle_list_checks`,
   `oracle_execute_check`, `knowledge_epistemic_status`,
   `knowledge_find_gaps`). Cross-checked against source: `oracle.py:914-
   916`'s `Path(result.raw_output_ref).is_file()` is reached, via
   `aggregate_contract`/`evaluate_result_precedence`, from `get`
   (`_get_check`/`_get_result`), `traverse` (`_traverse_check_results`),
   `find_gaps`, and — via `derive_epistemic_profile` — from
   `_knowledge_consistency` (used by `get`/`trace_evidence`) and
   directly from `epistemic_status`. `knowledge_search` correctly has
   **no** `_chdir` wrap (`tools.py:71-89`) since `search`'s own results
   use the default, never-recomputed `ConsistencyEnvelope()` and never
   call `evaluate_result_precedence` — confirmed by reading
   `knowledge_api.py:948-999`. No missed call site found.
5. **Process-group-kill claim** — re-read
   `tests/test_oracle_bounded_execution.py::TestTimeout::
   test_descendant_process_is_also_terminated_not_only_pytest_itself`:
   it spawns a real `sleep 60` child from inside the pytest-under-test,
   writes its real PID to a file, and after `run_pytest_check` returns
   polls `os.kill(pid, 0)` to confirm it is genuinely dead — a real,
   non-mocked assertion. Independently verified the large-output test's
   own "`assert False`" reasoning empirically (not merely trusted as
   written): wrote a 2000-line-flooding *passing* test and the
   identical flooding *failing* test under the real `.venv` pytest —
   the passing test's stdout never reached the real subprocess pipe (98
   bytes total), the failing test's full flood did (402,677 bytes).
   This confirms the test's own stated rationale is sound, not a
   rationalization.
6. **Protected-file/scope diff**: `git diff --stat -- CLAUDE.md
   decisions/ pyproject.toml` → empty (no changes to any of the three).
   Confirmed `pyproject.toml` is byte-identical to its state at commit
   7a96d89 (only the already-audited `mcp` dependency line exists;
   nothing added this round).
7. **Confinement-before-delegation**: read `impact_classify_change`
   (`tools.py:296-344`) — `confine_changed_paths` runs before
   `ChangedRange` construction and before `_ci.assess()` is ever
   called, for all three rejection cases (absolute, `..`, symlink
   escape); the absolute/`..` checks touch no filesystem at all, and
   the symlink check only resolves path components (`.resolve()`), never
   opens or reads the escaping target's content.
8. **Schema separation**: `oracle_execute_check`'s response
   (`tools.py:469-479`) carries `outcome` and `aggregate_state` as two
   independent dict keys, never merged — confirmed both in code and in
   `test_real_execution_writes_append_only_result`. `oracle_list_checks`'s
   `latest_result_status` is `state_by_check.get(...)` from
   `aggregate_contract`'s own `CheckAggregate.state`
   (`tools.py:377-388`), confirmed by `test_lists_real_checks_with_
   aggregate_status` (expects `"GAP"` for a required check with zero
   results, matching `aggregate_contract`'s own `elif check.required:
   state = "GAP"` branch, `oracle.py:966-967` — never a per-result raw
   outcome).
9. **Two new real files**
   (`planning/contracts/balance-from-spec/results/...`): verified the
   `.yaml`'s `raw_output_ref` is relative and portable, matches the
   established sibling-result field convention exactly field-for-field,
   and independently recomputed the `.txt`'s SHA-256 — matches
   `raw_output_sha256` in the YAML exactly. `git status --porcelain
   planning/contracts/balance-from-spec/` shows these two new files and
   nothing else modified under that tree.
10. `tests/test_assess_change_impact.py` (the relocated module's own
    pre-existing suite): **47 passed** (exceeds the "27+" the ADR
    names). Re-read `TestRunCheckAssurance.
    test_fresh_tampered_raw_output_is_invalid_assessment`
    (`tests/test_assess_change_impact.py:841-877`): it injects a
    `_TamperingOracle` wrapper as `run_check_assurance`'s own
    `oracle_mod` positional argument; `__getattr__` delegates every
    other call (including `evaluate_result_precedence`, which performs
    the actual tamper-detection) to the real `oracle` module, while only
    `evaluate_check` is overridden to corrupt the fresh raw output
    immediately after it's written. This is a genuine exercise of the
    injection seam — the override only touches the write side, and
    detection happens entirely through the real, undisturbed
    `evaluate_result_precedence` path — not a coincidental pass.

## Non-blocking observations

1. **`impact_classify_change` raises an uncaught `KeyError`, not a
   `ToolError`, for a `changed[]` entry missing its `path` key**
   (`mcp/security.py::confine_changed_paths`, line `path = c["path"]`,
   called from `tools.py:312` *before* the later `try: ... except
   (KeyError, TypeError)` block at `tools.py:314-319` that was clearly
   intended to catch exactly this shape of malformed input). Reproduced
   directly: `impact_classify_change(config, "target", "demo",
   [{"start": 1, "end": 2}])` raises a bare `KeyError: 'path'`. This
   does **not** crash the server or escape the MCP boundary — the `mcp`
   SDK's own `_handle_call_tool`
   (`.venv/.../mcp/server/mcpserver/server.py:441-456`) catches *any*
   `Exception`, including a bare `KeyError`, and returns
   `CallToolResult(is_error=True, ...)` regardless — so this is a
   message-quality/logging-precision gap (logged as `UnexpectedToolError`
   with a full traceback, rather than the project's own clean,
   intentional `ToolError` message), not a security or availability
   defect. It is, however, a real gap against §5.8's own "malformed-
   input tests per tool" convention and `CLAUDE.md`'s `L-070` discipline
   (test the mechanism's own minimal-content edge case) — no test in
   `tests/test_mcp_assurance.py` exercises a `changed[]` entry missing
   `path` itself (only `start`/`end` are exercised post-confinement).
   Recommend: validate dict shape (`"path" in c`) before
   `confine_changed_paths` touches `c["path"]`, plus one regression
   test.
2. **No persisted audit report exists for Stage 88A** —
   `planning/retros/` has no `_audit-phase-88*` file at all before this
   one, despite the dispatch stating 88A was "independently audited
   PASS WITH NON-BLOCKING OBSERVATIONS." Every Stage 87 sub-stage has
   its own `_audit-phase-87-stage-87X.md` file (confirmed by directory
   listing); Phase 88 currently has none for 88A. Per `CLAUDE.md` §5 /
   this agent's own governing instructions (`L-060`), the lead should
   confirm 88A's own audit was in fact persisted somewhere, or treat it
   as not yet durably evidenced.
3. No test explicitly names a filesystem-path-shaped string (e.g.
   `"/etc/passwd"`) as a `repo_root_key` for the two new Stage 88B
   tools, distinct from an arbitrary unrecognized key. This is a
   cosmetic test-naming gap only — `resolve_repo_root` does a plain
   dict lookup (`security.py:87-98`), so a path-shaped string is
   mechanically indistinguishable from any other unrecognized key, and
   `test_unconfigured_repo_root_key_rejected`/`test_unknown_repo_root_
   key_rejected` already exercise the real rejection path.

## Confirmed sound, not merely claimed

- Behaviour-preserving relocation: `change_impact.py` is a faithful,
  unmodified-logic move of `scripts/assess_change_impact.py`'s core
  functions; `resolve_changed_range` deliberately performs no
  confinement of its own (by design, confinement is the MCP wrapper's
  job) — confirmed by direct reading of both files' docstrings and
  code.
- `oracle.py`'s new `timeout_seconds`/`max_output_bytes` parameters are
  keyword-only with unchanged defaults; `evaluate_check` passes them
  through unchanged otherwise; existing callers
  (`scripts/run_balance_from_spec_oracle.py`, `check_contracts.py`) are
  unaffected since they never pass these new keywords.
- No Phase 82/83 logic duplicated inside the MCP layer; no Phase 89/90
  scope (reconciliation, comparative trials) touched.
- `docs/reference/mcp.md` and `--enable-execution`'s own `--help` text
  (`cli.py:1237-1245`) both state the no-sandbox trust model plainly, as
  §5.2 requires.

## What must be fixed before this verdict would become a plain PASS

Nothing blocks proceeding to the Ledgerkit demonstration — both
observations above are real but non-blocking (no crash, no security
regression, no silent misclassification; the 88A-audit-persistence gap
is a process-evidence question, not a Stage 88B code defect). Before
Phase 88's **terminal** DoD audit, recommend: (1) fix the
`changed[].path`-missing-key `KeyError` to a clean `ToolError` plus a
regression test; (2) confirm or produce a persisted Stage 88A audit
record.
