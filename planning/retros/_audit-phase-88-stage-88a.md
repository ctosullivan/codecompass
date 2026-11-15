# Audit: Phase 88, Stage 88A (MCP foundation, read-only)

**Scope**: the Stage 88A diff committed at `7a96d89` — new package
`src/codecompass/mcp/` (`__init__.py`, `security.py`, `tools.py`,
`server.py`); `codecompass mcp-serve` CLI command (`cli.py`); `mcp>=2.0,<3`
added to `pyproject.toml`; filesystem-confinement fixes applied directly
to `knowledge_api.py`/`knowledge_intermediate.py`/`oracle.py` (specified
in the plan's own §17/§17.9/§18.1 amendment rounds but not yet in code
before this commit); `tests/test_mcp_server.py`,
`tests/test_mcp_security_confinement.py`; `docs/reference/mcp.md`,
`docs/reference/cli.md`, `docs/architecture/components.md`,
`docs/architecture/overview.md`. This review was dispatched and run
**before** the commit landed (against the then-uncommitted working
tree, identical in content to what `7a96d89` records) and **before**
Stage 88B existed — it is not the terminal Phase 88 DoD audit.

**Verdict: PASS WITH NON-BLOCKING OBSERVATIONS**

This record reconstructs the independent `release-phase-auditor`-style
review dispatched for Stage 88A, persisted here per a later Stage 88B
audit's own non-blocking finding that no such record existed in
`planning/retros/` despite the verdict being reported. The content
below is the reviewing agent's own verbatim findings, carried forward
faithfully from its hand-back report (not re-derived or reworded after
the fact), consistent with this project's established "preserve actual
review history, never retrospectively smooth over" convention.

## What was independently re-run (not trusted from self-report)

1. **Full test suite**: `.venv/bin/python -m pytest tests/ -q` →
   **1424 passed, 2 skipped** (438s), exit 0. Matched the expected skip
   count from Phase 87 precedent.
2. **Ruff**: whole-repo `.venv/bin/ruff check . --statistics` → **176
   findings**, identical before and after (confirmed via `git stash`/
   `stash pop`, restored cleanly — `git status --porcelain` clean
   afterward). `.venv/bin/ruff check src/codecompass/mcp/
   tests/test_mcp_server.py tests/test_mcp_security_confinement.py` →
   **All checks passed!** No new debt.
3. **`.venv/bin/python scripts/check_user_docs.py --strict`** →
   `no findings`.
4. **Security reproduction** (the reviewer's own script, independent
   of this project's own tests): opened a confined `dir_fd` via
   `_open_confined_dir_fd`, then renamed the real directory aside and
   symlinked the original name to attacker content. A fresh pathname
   read at the same name returned attacker content (confirming the
   attack is real); a read through the **already-held `dir_fd`** via
   `_read_confined_bytes(..., dir_fd=fd)` returned the original content
   unaffected. This is exactly the property §18.1/`decisions/0095`
   amendment item 6 claims, and it held. The project's own
   `tests/test_mcp_security_confinement.py::
   test_directory_substitution_after_open_does_not_affect_held_fd`
   independently exercises the identical scenario and also passed.
5. **`git diff` touches no `CLAUDE.md` line** (0 diff), **no**
   `decisions/*` file, and `grep -n mcp CLAUDE.md` found no new
   dependency-table row (§0 compliance confirmed).
   `knowledge_api.find_gaps(root, "balance-from-spec")` output was
   **byte-identical** before/after (via `git stash`/pop comparison) —
   no behavioural change for legitimate input.
6. All **9** tools confirmed reachable via a real in-memory MCP session
   (`test_exactly_nine_tools_registered_with_object_schemas`, since
   renamed for Stage 88B's 12-tool count) and via direct `tools.py`
   calls; every function in `mcp/tools.py` confirmed a thin delegate
   (validate → call one `knowledge_api`/`knowledge_intermediate`
   function → envelope) — no Phase 84 logic reimplemented. Real-corpus
   parity tests (`TestRealCorpusParity`) confirmed byte-for-byte match
   against direct `knowledge_api` calls for 7 of 9 tools at review
   time.
7. **Read/write/execute separation** confirmed to hold: no tool has a
   side effect; `grep -rn "oracle_execute_check|impact_classify_change|
   oracle_list_checks|change_impact" src/codecompass/mcp/` returned
   only docstring/comment mentions, never a registered tool or import;
   `src/codecompass/change_impact.py` did not yet exist at review time.
   `--enable-execution` CLI flag and `require_enabled_execution`/
   `ServerConfig.execution_enabled` plumbing existed but were inert (no
   Stage 88B tool consumed them yet) — harmless, forward-compatible,
   not scope creep.
8. **Changed-file set matches plan scope exactly**: `mcp/` package,
   `cli.py` (`mcp-serve` only — diffed and confirmed no other command
   touched), `pyproject.toml` (one line), the three named
   security-fix files (`knowledge_api.py`, `knowledge_intermediate.py`,
   `oracle.py`), two new test files, and docs (`mcp.md`, `cli.md`,
   `components.md`, `overview.md`) — all required by `CLAUDE.md` §2/§5,
   not extraneous.

## Non-blocking observation (found and closed the same day)

Plan §5.8/§11.1 explicitly name "malformed-input tests per tool (wrong
id shape, out-of-range `max_items`, unknown `relation` value, unknown
`slug`)" as a Stage 88A acceptance item. `unknown relation`/`unknown
slug` were tested; **`wrong id shape` (empty/whitespace `record_id`/
`text`/`topic`) and `out-of-range max_items`/`max_chars` (the `<=0`
`ToolError` paths in `tools.py`, and `security.require_non_empty_str`)
had zero test coverage** at review time — confirmed by grep. The
validation logic itself was correct (raised `ToolError` as designed),
so this was a test-completeness shortfall against the plan's own named
list, not a functional defect.

**Closed same day**: `TestWrongIdShape`/`TestContextPacketBounds`
added to `tests/test_mcp_server.py` (parametrized empty/whitespace
checks for every tool taking a required string; non-positive
`max_items`/`max_chars` rejection and a valid-bounds sanity check for
`knowledge_context_packet`) — 15 additional tests, all passing,
Ruff-clean. No further defect found on re-check.

## Final status

Stage 88A implementation sound, matches plan §6/§11.1/§5 and
`decisions/0095`. Committed at `7a96d89`. Stage 88B was authorised to
begin on this verdict; its own independent audit is
`planning/retros/_audit-phase-88-stage-88b.md`.
