# Independent integration/security review -- Phase 88 MCP acceptance exercise

**Reviewer:** independent adversarial pass, no access to prior conversation.
Everything below was re-derived from primary sources: the two MCP configs,
both full JSONL transcripts, `src/codecompass/mcp/{security,tools,server}.py`,
`docs/reference/mcp.md`, `planning/contracts/balance-from-spec/oracle-contract.yaml`,
and direct filesystem/git/pytest inspection. No claim below is taken from any
prior retro or transcript summary without being checked against the real
artifact.

## (a) Transport reality

Confirmed real, not simulated:

- Session 1 and session 2 transcripts each carry a distinct `session_id`,
  a distinct `memory_paths.auto` path, a distinct `messaging_socket_path`,
  and `claude_code_version: 2.1.299` -- these are properties of a genuine,
  separately-launched `claude` CLI process, not something a single session
  could fabricate inline.
- Each transcript's `system/init` line reports `mcp_servers: [{"name":
  "codecompass", "status": "connected", "source": "dynamic"}]` and lists
  exactly the 12 `mcp__codecompass__*` tool names in its `tools` array --
  consistent with a real `--mcp-config .../mcp-config-{readonly,exec}.json
  --strict-mcp-config` connection (only the one configured server is
  present; no other MCP server from the ambient environment leaked in).
- `session0-sanity.log` shows an earlier dry run where a call to
  `mcp__codecompass__server_capabilities` was outright **denied**
  (`permission_denials` populated, result: "I don't have permission to call
  that tool yet") before an allowlist was supplied, and `session0-sanity2.log`
  shows the same call succeeding once the tool was allowed. This is the
  real Claude Code permission gate firing against a real stdio-connected
  server -- not something a mocked harness would produce.
- `session{1,2}-stderr.log` are both 0 bytes -- the real `codecompass
  mcp-serve` subprocess ran clean, no crash/traceback suppressed.

**Verdict: the transport is real.** PASS.

## (b) Boundary checks

| # | Check | Result |
|---|---|---|
| 1 | `--project-root` / `--repo-root` point only at disposable scratch paths | **PASS.** `mcp-config-readonly.json` / `mcp-config-exec.json` both pin `--project-root` to `.../scratchpad/phase88-acceptance/disposable-project-root` -- confirmed by direct inspection to be its own git repo (distinct inode from `/home/cormac/projects/codecompass`, its own `.git`, and only a ~400KB minimal subset: `planning/contracts/balance-from-spec/` + `planning/knowledge/balance-from-spec/`, not the real codecompass source tree). `--repo-root ledgerkit=...ledgerkit-correct` and `ledgerkit-mutated=...ledgerkit-mutated` are likewise both under the same scratch directory, each its own distinct git checkout. **Neither config ever names `/home/cormac/projects/ledgerkit` nor `/home/cormac/projects/codecompass` directly for anything.** The only difference between the two configs is the appended `--enable-execution` flag on the exec config.
| 2 | Every `mcp__codecompass__*` tool call uses a real tool name, real input shape, gets a real structured result | **PASS.** Enumerated every `tool_use`/`tool_result` pair in both transcripts (8 distinct MCP calls across the two sessions: `server_capabilities`, `oracle_list_checks`, `knowledge_get` x4, `knowledge_search`, `knowledge_trace_evidence`, `impact_classify_change`, `oracle_execute_check` x3, `knowledge_epistemic_status`). All 8 tool names are a subset of the 12 real tools in `docs/reference/mcp.md`'s table. Every input shape matches the real parameter signatures in `tools.py` (e.g. `impact_classify_change(repo_root_key, slug, changed=[{"path","start","end"}])`, `oracle_execute_check(slug, contract_id, check_id, repo_root_key)`). Every result is real, well-formed JSON matching the real `ApiResponse`/report shapes in `knowledge_api.py`/`change_impact.py`/`oracle.py` -- no silently-swallowed error, no hallucinated-looking content (e.g. `oracle_list_checks` returned the real 3-check allowlist with real `check_reference` test paths that exist verbatim in `tests/test_reports.py`).
| 3a | `repo_root_key` always symbolic, never a raw path | **PASS.** Every occurrence across both transcripts is the literal string `"ledgerkit"` or `"ledgerkit-mutated"` -- never a filesystem path.
| 3b | Disabled-execution rejection text matches real code | **PASS, exact match.** Transcript: `"Error executing tool oracle_execute_check: oracle_execute_check is disabled -- this server was started without --enable-execution (the default, read-only mode)"`. `security.py:137-142` (`require_enabled_execution`) produces exactly this string, verbatim.
| 3c | `oracle_execute_check` tuple is real/allowlisted | **PASS.** `(slug="balance-from-spec", contract_id="REQ-BFS-001", check_id="overlapping-account-patterns-no-double-count")` was checked directly against `planning/contracts/balance-from-spec/oracle-contract.yaml` in this repo -- the check exists verbatim under that exact `contract_id`.
| 3d | No `changed[].path` absolute/`..`/escaping | **PASS.** Only one `impact_classify_change` call in the whole exercise: `changed=[{"path": "ledgerkit/reports.py", "start": 600, "end": 696}]` -- relative, no `..`, inside the pinned target. No other call used `changed[]`.
| 3e | No read/write attempted outside pinned boundaries | **PASS.** No tool call (MCP or local Read/Edit/Bash) in either transcript referenced an absolute path or a path outside the session's own working directory. All local `Read`/`Edit`/`Grep`/`Glob`/`Bash` calls used paths relative to `ledgerkit-correct` (`tests/test_reports.py`, `ledgerkit/reports.py`, `.venv/bin/python`, etc.); session 2 made no local file-editing calls at all (MCP calls only, per its prompt's "do not modify any file further").

## (c) Real-world boundary verification (direct inspection, not trusting any report)

- `cd /home/cormac/projects/ledgerkit && git status --porcelain && git diff --stat` -> **both empty.** Real Ledgerkit checkout completely untouched.
- `cd /home/cormac/projects/codecompass && git status --porcelain --branch` -> `## main...origin/main`, no other output. No unexpected changes.
- Oracle result files: the two new `overlapping-account-patterns-no-double-count--*.yaml`/`.txt` files from session 2's step 9/10 calls exist **only** under `.../scratchpad/phase88-acceptance/disposable-project-root/planning/contracts/balance-from-spec/results/{,raw/}`. The real repo's own `/home/cormac/projects/codecompass/planning/contracts/balance-from-spec/results/` was independently listed and contains **no** `overlapping-account-patterns-no-double-count` file at all -- confirming the execute-check write boundary held and the disposable project-root is not an alias for the real tree.

## (d) Independent re-execution of the negative control

Read `ledgerkit-mutated/ledgerkit/reports.py` directly (not via any tool output) and diffed it against `ledgerkit-correct/ledgerkit/reports.py`:

```diff
-                if not any(_matches_pattern(pat, posting.account) for pat in section.accounts):
+                _match_count = sum(
+                    1 for pat in section.accounts if _matches_pattern(pat, posting.account)
+                )
+                if _match_count == 0:
...
-                pairs.append((account, posting.amount.quantity))
+                for _ in range(_match_count):
+                    pairs.append((account, posting.amount.quantity))
```

This is a genuine behavioral mutation (turns the single boolean "any-match"
gate into a per-matching-pattern repeat-append loop -- the exact
double-counting bug the new regression test targets), not a no-op or a
cosmetic diff.

Independently ran, with my own tool calls, not trusting the transcript:

- `ledgerkit-correct`: `.venv/bin/python -m pytest -q` -> **936 passed, 14
  subtests passed.** `-k test_section_accounts_overlapping_patterns_no_double_count`
  -> **1 passed.**
- `ledgerkit-mutated`: same `-k` filter -> **1 failed**:
  `AssertionError: Decimal('300.00') != Decimal('150.00')` -- exactly the
  double-count signature the mutation should produce.

PASS/FAIL split reproduced independently and matches the transcript's
claimed `oracle_execute_check` outcomes (`PASS`/`aggregate_state=PASS` for
`ledgerkit`; `FAIL`/`aggregate_state=GAP` for `ledgerkit-mutated`).

## (e) Client-side boundary (how the connected agent itself was confined)

From each transcript's `system/init` line (session 1 and session 2 agree):

- `cwd`: `.../scratchpad/phase88-acceptance/ledgerkit-correct` -- the
  disposable Ledgerkit scratch checkout, not the real Ledgerkit repo and
  not the codecompass repo.
- No `additionalDirectories`/`--add-dir` key present at all in either
  init line -- the client was not granted any extra filesystem root beyond
  its own cwd.
- `permissionMode: "default"` in both sessions -- **not**
  `bypassPermissions`/`--dangerously-skip-permissions`. Combined with
  `session0-sanity.log`'s demonstrated real denial-then-allow behavior,
  this confirms an explicit `--allowedTools` allowlist was used (an
  oversight-preserving mode), not a blanket permission bypass.
- Every local tool call the client made (`Read`/`Edit`/`Grep`/`Glob`/`Bash`)
  used paths relative to that cwd; the one `git status --short` Bash call
  and the `.venv/bin/python -m pytest` calls likewise ran inside it.

## Non-blocking observation (not a defect)

Step 11 of session 2 (`knowledge_epistemic_status` for `REQ-BFS-002`,
`repo_root_key="ledgerkit"`, called immediately after step 9's fresh `PASS`)
still reports `verified_scopes: []` and all three scopes under
`known_gap_scopes`, apparently not reflecting step 9's fresh result. I
traced this to `knowledge_api.epistemic_status` -> `derive_epistemic_profile`:
`REQ-BFS-002` depends on `CL-BFS-004`, and `CL-BFS-004`'s own recorded
evidence (`EV-BFS-001`, role `supporting_indirect`) has no scope-level
coverage link to any specific `check_id` (confirmed in session 1's
`impact_classify_change` result: `CL-BFS-004` is tagged
`tier: "relevant_no_coverage_link"`, `check_id: null`). A fresh
`oracle_execute_check` result updates the *oracle contract's own aggregate*
(correctly visible via `oracle_list_checks`/`oracle_execute_check`'s own
`aggregate_state` field) but does **not** retroactively alter the
knowledge graph's Claim/Evidence records -- that only happens through
curation, matching this project's own stated principle (CLAUDE.md §8: "An
agent observation is not authoritative because an agent recorded it ...
only curation plus evidence promotes it"). This is correct, intended
separation of concerns, not a bug in the MCP boundary or in `oracle`/
`knowledge_api`. Flagged only so a reader isn't surprised by the
transcript's own (correct) observation that the two didn't match.

## Genuine defects found

None. Every boundary named in the brief held under direct, independent
re-verification (not just by reading the transcript's own narration).

## Overall verdict

**PASS.**

- Real MCP stdio transport between a genuine, separately-launched `claude`
  CLI client and a genuine `codecompass mcp-serve` subprocess -- confirmed
  via session/process/socket identity, a real permission-denial-then-allow
  sequence, and empty stderr logs.
- `repo_root_key` confinement, execution-mode gating, the allowlisted
  `(slug, contract_id, check_id)` tuple, and `changed[].path` confinement
  all held, matched against the real source in `security.py`/`tools.py`,
  not just the design doc.
- `--project-root` itself was a disposable scratch copy (stricter than the
  brief's own minimum bar of "just don't point it at the real codecompass
  repo for repo-root").
- Real repos (`/home/cormac/projects/ledgerkit`, `/home/cormac/projects/codecompass`)
  verified untouched by direct `git status`/`git diff --stat`, not by
  trusting any agent's report.
- The negative control (mutated `reports.py`) is a real, non-trivial
  behavioral change, and its PASS/FAIL split was reproduced independently
  with my own `pytest` runs, matching the transcript's claimed
  `oracle_execute_check` outcomes exactly.
- The connected client itself was confined to its own scratch cwd, granted
  no extra directories, and ran under `permissionMode: "default"` with an
  explicit tool allowlist rather than a permission bypass.
