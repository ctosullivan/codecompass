# Docs-drift audit — Phase 88 (Agent Integration and MCP)

**Mode:** Per-phase docs-drift audit (MODE 1), per `docs-reconstructor`'s
own agent definition and `documentation-lifecycle.md` §2.5.

**Scope of diff audited:** `dbcfe50^..4763fcb` (five planning commits,
`7a96d89` Stage 88A, `a554d52` Stage 88B + Ledgerkit demonstration,
`4763fcb` learnings triage), confirmed directly via `git log` and
`git diff --stat` rather than trusted from the dispatch description.
Independent read of the diff and the current source — not based on
`docs-maintainer`'s own summary of what it changed.

## Verdict: NO DRIFT

No current-truth doc (`README.md`, `docs/`, `architecture/`,
`ai-docs/`) was found to misdescribe the system as it now stands. The
lead's own two targeted fixes are both verified correct and complete
(detail below). One pre-existing, non-blocking omission is flagged
(not new drift from this diff, but directly relevant to one of the
dispatch's own explicit questions) for the lead's discretion.

## What was checked, and how, against what ground truth

1. **`docs/reference/mcp.md`** (new, 139 lines) — checked line-by-line
   against `src/codecompass/mcp/tools.py`, `security.py`, `server.py`,
   and `src/codecompass/oracle.py`/`cli.py`:
   - Tool table: all 12 tools listed match exactly the 12 functions
     registered in `server.py::build_server` (9 Stage 88A +
     `impact_classify_change`/`oracle_list_checks`/
     `oracle_execute_check`). No extra, no missing, no renamed tool.
   - `--repo-root`/`--project-root`/`--enable-execution` flags verified
     against `cli.py`'s real `mcp_serve` command (`cli.py:1224-1263`) —
     match.
   - "Validation and confinement" section verified against
     `security.py`: `resolve_repo_root` (unknown key → `ToolError`),
     `require_known_slug`, `validate_doc_path` (re-derived allowlist,
     confirmed 5 real `*.md.schema.yaml` files exist on disk matching
     the doc's "schema-governed document set" claim),
     `validate_relation`, `confine_changed_paths` (absolute / `..` /
     symlink-escape rejection, all offending paths named at once) — all
     match the doc's prose exactly, including the "naming every
     offending path" and "before any assessment runs" claims.
   - `oracle_execute_check`'s bounded-subprocess claims ("bounded by a
     timeout and a total-output cap, with a process-group-wide kill ...
     on either breach") verified against `oracle.py::run_pytest_check`
     (`start_new_session=True`, `os.killpg(..., signal.SIGKILL)` on
     either a timeout or output-cap breach, chunked incremental
     reading) — match, including that only `pytest` is an implemented
     execution provider (`oracle._SUPPORTED_EXECUTION_PROVIDERS =
     {"pytest"}`), matching the doc's "runs a real `pytest`
     subprocess."
   - "Trust model and limitations" (no sandbox, single local operator,
     stdio-only, no auth) verified against `server.py::run`'s own
     docstring and `build_server`'s `instructions=` string — match.

2. **`docs/reference/cli.md`** `mcp-serve` section — the lead's own
   heading fix (`## codecompass mcp-serve (Phase 88, Stage 88A)` →
   `## codecompass mcp-serve (Phase 88)`) is correct: the section body
   already fully describes both stages (`--enable-execution` and what
   it grants), so scoping the heading to Stage 88A alone was the actual
   bug: **verified fixed**. Cross-checked the flags/behaviour described
   against `cli.py` directly (not trusting the plan) — accurate.

3. **`docs/architecture/overview.md`** subsystem 5 — the lead's own fix
   (removing the "once Stage 88B lands" conditional, replacing with
   "nine read-only tools and three assurance tools
   (`impact_classify_change`, `oracle_list_checks`,
   `oracle_execute_check`)") is correct and matches the 12 real
   registered tools. Also re-checked the rest of this file for any
   *other* stale Phase-88-era conditional: ran `grep -rn "Stage 88"`
   across `README.md`, `docs/`, `architecture/`, `ai-docs/` and
   inspected every hit (`overview.md` subsystem 5 — already fixed,
   present-tense; `components.md`'s `mcp/` row's "Stage 88A"/"Stage
   88B" — both used as accurate historical-stage labels for what each
   stage delivered, not "once X lands" conditionals; `mcp.md`'s
   "`--enable-execution` — turns on `oracle_execute_check` (Stage
   88B)" and `cli.md`'s matching sentence — same, accurate, present-
   tense "(Stage 88B)" labelling what already shipped). **No other
   stale conditional found.** The "Known footguns" and "What
   CodeCompass explicitly does not do" sections of this file were also
   read in full — both already current (the latter already documents
   `mcp-serve`'s own no-sandbox/single-operator limitation accurately).

4. **`docs/architecture/components.md`** — the new `mcp/` row and
   `change_impact.py` row, and the updated `cli.py`/`oracle.py` rows,
   checked against the real modules:
   - `mcp/` row's "all twelve" tool-wrapper claim, the `_chdir`
     rationale (stored *relative* `raw_output_ref` resolved against
     process cwd), and the `security.py`/`tools.py`/`server.py`
     role split — verified directly against `tools.py`'s `_chdir`
     docstring and actual delegate-call sites (every tool wraps its
     delegate call in `with _chdir(config.project_root):`) — accurate.
   - `change_impact.py` row's "relocated unchanged ... thin CLI
     wrapper ... preserving its own existing flags/behaviour and test
     suite exactly" — verified against `scripts/assess_change_impact.py`
     (now a 109-line argparse wrapper re-exporting `change_impact`'s
     functions by the same names, for `tests/test_assess_change_impact.py`'s
     existing direct imports) — accurate.
   - `cli.py` row's "`mcp-serve` (Phase 88, a thin launcher for
     `mcp/server.py`)" — matches `cli.py:1224-1263`'s actual body
     (parses `--repo-root`, calls `_mcp_server.run(...)`, no other
     logic).
   - `oracle.py` row's Phase 88 §5.3 hardening description (timeout,
     bounded-chunk capture, process-group `SIGKILL`, "no behavioural
     change to an ordinary, fast, bounded-output check") — verified
     against `run_pytest_check`'s real signature/defaults
     (`DEFAULT_CHECK_TIMEOUT_SECONDS`/`DEFAULT_CHECK_MAX_OUTPUT_BYTES`
     as keyword defaults, not required args) — accurate.

5. **`ai-docs/README.md`** — read in full. No sentence in it is now
   *false* as a result of this phase (nothing it claims about git
   non-mutation, AI-optionality, deterministic-vs-AI split, etc. is
   contradicted by the MCP server). **However**, this file's own stated
   purpose is to give an agent landing on the project "a fast, accurate
   picture of what it does before reading further," and its "What it
   does" / "What it does NOT do" lists do not mention the MCP server at
   all — a materially different capability from everything else listed
   there (a long-running server process; one opt-in tool,
   `oracle_execute_check`, that executes real code with no sandbox).
   This is an **omission, not a false statement** — I am not counting
   it toward the `DRIFT` verdict, since nothing it currently says is
   contradicted by Phase 88. Flagging it because the dispatch explicitly
   asked me to check it, and because the particular gap (a boundary a
   new agent would want up front: "this project can also run as a
   stdio MCP server, including one tool that can execute arbitrary
   repository test code if explicitly enabled") sits squarely inside
   this file's own stated job. Non-blocking; the lead's call whether to
   route it to `docs-maintainer`.

6. **`README.md`** — spot-checked the "Documentation map" section:
   it names `docs/reference/` generically ("CLI reference, `vendor.toml`
   configuration, the external adapter wire protocol, and
   symbol-extraction behaviour") without naming `docs/reference/mcp.md`
   specifically, unlike the other reference docs it does name. Not a
   false statement (the sentence doesn't claim to be exhaustive) — noting
   it only as a very minor, non-blocking observation, not a finding.

## What I deliberately did not re-litigate

- The MCP security/planning commits (`06c095a`, `26947ff`) and the
  phase/retro planning prose under `planning/` are not current-truth
  docs in the DoD's own sense (`README.md`/`docs/`/`architecture/`/
  `ai-docs/`) — not audited for drift, only used to orient.
- `CLAUDE.md` §1's new L-131 learning, `CONTRIBUTING.md`'s mirrored
  copy, `.claude/agents/release-phase-auditor.md`'s new item 15,
  `planning/agent-led-workflow.md`, and the three
  `planning/v1-redefinition/*.md` files touched by the learnings-triage
  commit are governance/process documents, not system-behaviour docs —
  out of this mode's scope (and `CLAUDE.md` changes are governed by
  §0's own separate human-approval gate, already evidently satisfied
  since the diff shows the change landed).
- Internal source docstrings (e.g. `server.py::build_server`'s own
  docstring, which still says "Registers the nine Stage 88A read-only
  tools" despite the function in fact registering all twelve) are
  *not* "current-truth docs" under the DoD's own named scope
  (`README.md`/`docs/`/`architecture/`/`ai-docs/`) and are not counted
  as a finding here — flagging only as a one-line heads-up to the lead,
  since it is the same class of staleness just fixed in `overview.md`,
  now sitting one level down in the source itself
  (`src/codecompass/mcp/server.py` lines 1-7, 29-33).
- Domain-claim staleness check (step 5 of this mode): skipped per the
  mode's own instruction — `docs/domain/` does not exist yet in this
  repository.
- `CHANGELOG.md` — not in the DoD's named current-truth-doc list;
  not audited for accuracy (only confirmed an `[Unreleased]` entry for
  Phase 88 exists, which is a different gate's concern).

## Summary for the lead

**NO DRIFT.** Both of your own fixes (`docs/architecture/overview.md`
line 11, `docs/reference/cli.md`'s `mcp-serve` heading) are verified
correct and complete against the real 12-tool `mcp/` implementation.
I found no other stale "Stage 88A"/"once Stage 88B lands"-style
conditional, and every specific claim the dispatch asked me to check
(tool table, security/confinement section, bounded-subprocess
semantics, components.md's new rows, overview.md's subsystem 5) holds
against the real source. Two non-blocking, pre-existing-style
omissions are named above for your discretion (`ai-docs/README.md`
not mentioning the MCP server's existence/trust-model boundary at all;
`README.md`'s docs-map not naming `mcp.md` specifically) — neither is
counted toward the drift verdict since nothing currently stated is
false, only incomplete. One further non-doc heads-up: `mcp/server.py`'s
own docstring and `build_server`'s docstring still say "nine" tools
despite registering twelve — not in audit scope (source, not a
current-truth doc) but the same staleness pattern, worth a one-line
fix if convenient.
