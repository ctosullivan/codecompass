# Phase 88 — Real-Agent MCP Acceptance Exercise

**What this is**: Phase 88 (Agent Integration and MCP) is already `done`
(`planning/ROADMAP.md`, terminal audit PASS, `planning/retros/
_audit-phase-88.md`) — that governance verdict is **not reopened or
invalidated** by this document. What that terminal audit's own
Ledgerkit demonstration (`planning/retros/
phase-88-ledgerkit-demonstration.md`) did **not** establish is that a
*real, separate* MCP client — not direct calls into
`codecompass.mcp.tools`, not an in-process unit test, not an
orchestrator-authored simulation — can actually discover and drive this
server's tools over the real MCP stdio transport. This document closes
that specific, narrower gap: a genuine, separate `claude` CLI process
was launched as a real MCP client, connected to a real `codecompass
mcp-serve` subprocess, and used to complete a real Ledgerkit development
task end to end.

## Environment

- Real `codecompass` package, editable-installed
  (`/home/cormac/.local/share/pipx/venvs/codecompass-context`, pointing
  at this checkout's own `src/`) — the real `mcp-serve` command, not a
  stub. The `mcp` SDK dependency (`mcp>=2.0,<3`, already declared in
  `pyproject.toml` since Phase 88) was installed into that venv this
  session (it had never actually been installed before — a real,
  previously-unexercised environment gap, now closed).
- Two disposable Ledgerkit scratch copies
  (`/tmp/claude-1000/.../scratchpad/phase88-acceptance/
  ledgerkit-correct` and `ledgerkit-mutated`), both `cp -r`'d from, and
  pinned at, the real `~/projects/ledgerkit` checkout's own current HEAD
  (`a7740fd04fe1814d2a557bfcb67a9a775a4a22f9`) — **the real checkout was
  never modified**, re-confirmed independently, more than once, through
  this exercise (see "Independent verification" below).
- `ledgerkit-mutated` additionally carries Phase 83's own
  already-documented double-counting mutation to
  `balance_from_spec`'s OR-union inclusion gate (`reports.py` — the
  single boolean `any(...)`-gated append changed to counting matching
  patterns and appending once per match) — re-applied exactly as
  previously documented, not reinvented.
- A disposable project-root (`.../disposable-project-root`, its own
  separate, locally `git init`'d snapshot of just `planning/knowledge/
  balance-from-spec/` and `planning/contracts/balance-from-spec/`) was
  used for `--project-root`, so every `oracle_execute_check` write
  landed only there — never in this repository's own committed
  `planning/contracts/balance-from-spec/results/`.
- The real MCP client: the actual `claude` CLI (`/home/cormac/.local/
  bin/claude`), invoked non-interactively (`claude -p ...`) with
  `--mcp-config`/`--strict-mcp-config` pointing at a real `codecompass
  mcp-serve` subprocess, and an explicit `--allowedTools` allowlist
  (the 12 real `mcp__codecompass__*` tool names plus `Read`/`Write`/
  `Edit`/`Bash`/`Glob`/`Grep`) — **not** `--dangerously-skip-permissions`/
  `--permission-mode bypassPermissions` (the harness's own auto-mode
  classifier denied a first attempt using that broader bypass, correctly
  flagging it as undermining oversight; the explicit, scoped allowlist
  was used instead and is itself confirmed, by the independent
  integration/security review below, to have kept the client's file
  access confined to its own disposable working directory with no
  `--add-dir` grant to either real repository).

## What was done

**Session 1** (server started *without* `--enable-execution` — read-only
mode): the real client, working inside `ledgerkit-correct` with no
filesystem access to this CodeCompass repository at all, was instructed
to get all CodeCompass knowledge exclusively through MCP tools. It:

1. Called `server_capabilities` (first, as `docs/reference/mcp.md`
   itself recommends) — real response:
   `{"repo_root_keys":["ledgerkit","ledgerkit-mutated"],
   "execution_enabled":false,"codecompass_version":"1.0.0"}`.
2. Discovered all 12 real tools via MCP's own tool-discovery mechanism
   (confirmed against the real
   `docs/reference/mcp.md` tool table by the independent integration
   review below).
3. Called `oracle_list_checks` (slug="balance-from-spec") and found the
   real, on-disk gap: `overlapping-account-patterns-no-double-count`,
   status `GAP`.
4. Called `knowledge_get`/`knowledge_search`/`knowledge_trace_evidence`
   for `REQ-BFS-001`, `REQ-BFS-002`, `DEC-BFS-002`, `CL-BFS-004`,
   `EV-BFS-001` — real responses from this repository's own canonical
   `planning/knowledge/balance-from-spec/` records (via the disposable
   project-root's own copy of them).
5. Correctly identified, grounded in `DEC-BFS-002` specifically (not
   generic background — see "Knowledge-retrieval vs. documentation" and
   the independent context review below for the materiality finding),
   that the missing test must assert *arithmetic*, not membership.
6. Wrote `test_section_accounts_overlapping_patterns_no_double_count`
   into `tests/test_reports.py::TestBalanceFromSpec`, asserting
   `rows["expenses:food:groceries"] == Decimal("150.00")` and
   `subtotal == Decimal("159.00")`.
7. Ran it (`1 passed`) and the full suite (`936 passed, 14 subtests
   passed`, no regressions) via its own ordinary `Bash`/`pytest` access
   inside the disposable checkout — not an MCP tool, exactly as the
   plan's own role split intends (CodeCompass supplies knowledge/
   assurance; the agent does the actual development work).
8. Called `impact_classify_change` against `ledgerkit/reports.py:
   600-696` (`repo_root_key="ledgerkit"`) — real response confirmed
   `ran_checks: false` (pure classification, never a fresh execution).
9. Attempted `oracle_execute_check` — real, clean permission error
   (`"oracle_execute_check is disabled -- this server was started
   without --enable-execution"`), no crash, no silent no-op.

**Session 2** (same client session, `--resume`'d; server restarted
*with* `--enable-execution` — controlled verification now authorised,
exactly as this task's own environment instruction required: execution
capability stayed disabled until this point, then was enabled
explicitly):

10. `oracle_execute_check` (slug="balance-from-spec",
    contract_id="REQ-BFS-001",
    check_id="overlapping-account-patterns-no-double-count",
    repo_root_key="ledgerkit") → real response: `outcome: "PASS"`,
    `aggregate_state: "PASS"`.
11. The identical call with `repo_root_key="ledgerkit-mutated"` → real
    response: `outcome: "FAIL"`, `aggregate_state: "GAP"` — the same
    check, the same tool, discriminating correctly between the correct
    and the mutated target purely from which pinned `repo_root_key` was
    named.
12. `knowledge_epistemic_status` for `REQ-BFS-002` — see "Non-blocking
    observation" below.

Before the mutated-target run, the exact same new test (byte-identical,
applied via `git apply` of `ledgerkit-correct`'s own diff) was added to
`ledgerkit-mutated`'s `tests/test_reports.py` by this orchestrating
session, and the mutation itself was independently confirmed, by direct
execution, to still be a real blind spot for Ledgerkit's own unmodified
suite (`935 passed`, zero failures, before the new test existed in that
tree) — matching Phase 83's own already-documented figures exactly.

## Independent verification (two fresh dispatches, no access to this
session's own conversation)

**`context-evaluator`** (full report: `planning/retros/
_review-phase88-mcp-acceptance-context.md`) — **PASS, context-advantage
HIGH**. Independently re-derived the correct arithmetic from
`reports.py`/`_matches_pattern`/`filtered.journal` directly and got the
identical numbers (150.00/159.00 vs. a 300.00/309.00 double-count);
independently confirmed the one existing sibling test
(`test_section_multiple_accounts_patterns_or_union`) asserts membership
only, never arithmetic — exactly `DEC-BFS-002`'s own claim, confirmed
*materially*, not generically, shaping the new assertion; independently
reproduced `936 passed` (correct) and the exact `AssertionError:
Decimal('300.00') != Decimal('150.00')` single failure (mutated); found
no overclaim in the client's own self-report.

**Independent integration/security reviewer** (full report: `planning/
retros/_review-phase88-mcp-acceptance-integration-security.md`) —
**PASS**. Confirmed, from the transcripts' own `system/init` records,
genuinely distinct session ids/socket paths and a real 12-tool MCP
manifest (not a mock); confirmed every `repo_root_key` was always
symbolic, the disabled-execution error text matches `security.py`
verbatim, the allowlisted `(slug, contract_id, check_id)` tuple matches
the real `oracle-contract.yaml` verbatim, and no path-confinement rule
was ever tested against or bypassed; confirmed both real repositories
(`~/projects/ledgerkit`, this CodeCompass checkout) are untouched;
confirmed the client's own permission mode was the explicit
`--allowedTools` allowlist, not a broad bypass, and its file access was
confined to its own disposable working directory.

## Non-blocking observation (both independent reviewers raised the same
one)

`knowledge_epistemic_status(REQ-BFS-002)` still reported all three
scopes as `known_gap_scopes` (and `verified_scopes: []`) immediately
after step 10's fresh `PASS`. **This is correct, intended behaviour,
not a defect**: `oracle_execute_check` only ever calls `evaluate_check`
+ the existing, unmodified, append-only `write_oracle_result` — it
never writes back into `planning/knowledge/`'s own curated Claim/
Requirement records (`decisions/0092`, `CLAUDE.md`'s own "no silent
modification of canonical knowledge" principle, Phase 88 plan §5.4,
unchanged). A fresh raw verification result and a curated canonical
fact are deliberately two different things until a human reviews and
promotes one into the other — exactly the detect-vs-act distinction
`CLAUDE.md` §1's own `L-087` already names, applied here to a boundary
this exercise newly made visible rather than newly created. **This gap
is also exactly Phase 89's own stated reason to exist** — see
`planning/phase-89-incremental-knowledge-documentation-reconciliation.md`
§6.1, which reuses this very `REQ-BFS-002`/`PASS` pair as its own Task
A. A minor, secondary observation (`impact_classify_change`'s
`assurance` array silently omitting a Claim with `check_id: null`
rather than an explicit "no linked check" row) was also raised by both
reviewers; disposed as non-blocking, cosmetic, and out of scope for a
narrowly-targeted correction in this exercise — recorded here with
reasoning, per this project's own established practice of never
silently dropping a raised finding.

## What this independently proves, and what it does not

**Proven**: a real, separate MCP client (the actual `claude` CLI, not a
simulation) can discover and drive all 12 of this server's tools over
real stdio transport; the server's own permission/validation/
confinement behaviour (execution-disabled rejection, symbolic
`repo_root_key`-only resolution, read-only-vs-execute separation) holds
under a real client's real calls, not only under this project's own
test suite; a genuine Ledgerkit development task — discovery, grounded
context retrieval, test authoring, impact classification, controlled
verification with both a positive and an independently-reproduced
negative result — completes correctly end to end through this
interface alone.

**Not proven, and not claimed**: that the real
`overlapping-account-patterns-no-double-count` gap is closed in the
real `~/projects/ledgerkit` checkout — it is not; that checkout remains
untouched, exactly as it was before Phase 88's own original
demonstration, per the standing cross-repository constraint. Landing
this byte-identical test (and the two oracle result files already
produced against the scratch copy) in the real checkout requires a
separate, explicit cross-repository authorisation this exercise was not
given and did not request.

## Corrections made as part of this exercise

- `planning/CONTEXT.md`'s "Current phase" section asserted `f2a1d72` was
  "committed on local `main` but not yet pushed to `origin/main`" — this
  was true when written but had since been superseded (the terminal
  reconciliation commits `9d0cbce`/`4615691` landed and were pushed
  after that paragraph was written, and `planning/ROADMAP.md`'s own
  Phase 88 row already correctly says `done`). Fixed in place in this
  exercise's own closeout commit — a narrowly-scoped correction of a
  genuinely stale pushed/unpushed claim, not a reopening of Phase 88
  itself.
- No other narrowly-scoped MCP integration defect was found requiring
  correction — both independent reviews returned PASS with only the one
  already-discussed, correctly-functioning-by-design observation and
  one disposed cosmetic finding.
