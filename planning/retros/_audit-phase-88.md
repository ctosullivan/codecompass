# Audit: Phase 88 — Agent Integration and MCP (terminal, whole-phase DoD audit)

**Scope**: the full Phase 88 effort — Stage 88A (`7a96d89`), Stage 88B +
Ledgerkit demonstration (`a554d52`), and the learnings-triage commit
(`4763fcb`) — against `CLAUDE.md` §5 and
`planning/phase-88-agent-integration-mcp.md`'s own §13 Definition-of-Done
mapping.

**Important correction to the dispatch's own framing**: the dispatch
named `a554d52` as "the actual current HEAD" and described the
candidate-learnings triage (L-131–L-134) as staged-but-blocked-from-
committing. By the time this audit ran, that triage had actually been
committed and pushed as `4763fcb` (on top of `a554d52`), and `main` is
up to date with `origin/main` at `4763fcb`. This audit evaluates the
real, current repository state (`4763fcb`), noting this discrepancy
explicitly rather than silently auditing a commit that is no longer
HEAD. `4763fcb` only touches governance/learnings files (`CLAUDE.md`,
`CONTRIBUTING.md`, `.claude/agents/release-phase-auditor.md`,
`planning/agent-led-workflow.md`, `planning/learnings/*`,
`planning/v1-redefinition/*`, one `planning/ROADMAP.md` backlog-table
line) — it does **not** touch `src/`, `tests/`, or flip Phase 88's own
`ROADMAP.md` row to `done`, so it is not the narrow terminal
reconciliation commit either; it is a legitimate, separate
documentation/governance commit that happened to land mid-audit.

## VERDICT: FAIL

Two of `CLAUDE.md` §5's own named Definition-of-Done conditions are
genuinely unmet **right now, against the real current HEAD** — not
hypothetically, and both independently confirmed by direct re-reading
rather than trusted from any prior report:

1. **No independent `docs-reconstructor` per-phase drift audit ever ran
   for Phase 88** (DoD condition: "an independent `docs-reconstructor`
   per-phase drift audit finds no current-truth doc ... left
   misdescribing the system, scoped to what the phase changed").
2. **`planning/CONTEXT.md` does not reflect the current state** (DoD
   condition: "`planning/CONTEXT.md` reflects the new state").

Both are detailed below, with the live drift this audit found as direct
evidence that (1) is a real gap, not a paperwork formality.

---

## What was independently re-run (not trusted from self-report)

1. **Full regression suite**: `.venv/bin/python -m pytest -q` →
   **1464 passed, 2 skipped**, exit 0 (433s). Matches the stage audits'
   own reported trajectory (1424 → 1461+ → 1464); no regression.
2. **Ruff, whole repo**: `.venv/bin/ruff check .` → **167 errors**,
   matching the dispatch's own expected post-Stage-88B baseline exactly
   (176 → 167, net lower from the `scripts/assess_change_impact.py`
   relocation shedding long lines). No new debt confirmed independently
   by the Stage 88B audit's own `git stash`/`stash pop` comparison
   (re-read, not re-run, since that comparison is already recorded and
   the working tree is currently clean against `4763fcb`).
3. **`.venv/bin/python scripts/check_user_docs.py --strict`** →
   `check_user_docs: no findings`.
4. **`decisions/0095` append-only integrity**: `git log --follow -p` on
   the file shows it was created at `dbcfe50`, amended twice
   (`06c095a` adding a new `## Amendment` section, `26947ff` appending
   item 6 to that same amendment section) — both diffs are pure
   additions; no line of the original `## Decision`/`## Context`
   content was ever edited. No commit after `26947ff` touches the file
   at all. Append-only convention held.
5. **Protected-file drift**: `git diff --cached`/working tree is clean
   at `4763fcb`. The one `CLAUDE.md` edit in this phase's own history
   (landed in `4763fcb`, the L-131 promotion into §1) is explicitly
   recorded as user-approved per §0 in
   `planning/v1-redefinition/proposed-governance-changes.md` §Q
   ("Status: approved and landed (2026-11-15) ... presented to the user
   for §0 approval and approved as drafted") and mirrored into
   `CONTRIBUTING.md` in the same commit. No other `CLAUDE.md` content
   changed in this diff (`git show 4763fcb -- CLAUDE.md` is a single,
   pure addition after the existing L-088 sentence). No other phase
   commit (`7a96d89`, `a554d52`) touches `CLAUDE.md` at all. No
   `decisions/*` file other than `0095` (append-only, confirmed above)
   is touched anywhere in this phase's commits.
6. **Real `~/projects/ledgerkit` checkout confirmed untouched**:
   `git status --porcelain` and `git diff --stat` both empty, `HEAD` at
   `a7740fd04fe1814d2a557bfcb67a9a775a4a22f9` (independently re-run by
   this audit, not trusted from the demonstration retro's own account).
7. **Real committed oracle-result files** (Stage 88B's own real,
   non-demonstration `oracle_execute_check` call): the committed YAML
   (`planning/contracts/balance-from-spec/results/single-section-
   expense-subtotal--20261115T063229247317Z-075c7da9.yaml`) targets
   `check_id: single-section-expense-subtotal` — one of the two
   already-passing checks the plan's own §11.2 names for this real,
   non-scratch verification call, not the demonstration's own gap check
   — confirmed consistent, not a conflation.
8. **Stage audit reports** (`planning/retros/_audit-phase-88-stage-88a.md`,
   `-88b.md`): both read in full. Both are genuinely substantive —
   independent re-runs of the full suite, Ruff, `check_user_docs.py`,
   direct source reads confirming no Phase 82/83/84 logic duplicated,
   and (for 88B) real, non-mocked reproductions of the `_chdir`
   cwd-dependency defect (via monkey-patching `_chdir` to a no-op and
   confirming the exact `PASS`→`GAP` misclassification reappears) and
   the process-group-kill claim (a real spawned `sleep 60` child
   confirmed dead via `os.kill(pid, 0)` after the parent is killed).
   Neither report is a stub or a self-report rehash.
9. **Stage 88B's own non-blocking finding #1 (`confine_changed_paths`
   bare `KeyError`) verified fixed in the final code**: read
   `src/codecompass/mcp/tools.py:296-330` directly — the dict-shape
   validation (`{"path", "start", "end"} <= c.keys()`) now runs and
   raises a clean `ToolError` *before* `_sec.confine_changed_paths` ever
   indexes `c["path"]`. `tests/test_mcp_assurance.py::
   test_changed_entry_missing_path_key_is_a_tool_error_not_a_bare_keyerror`
   exists and exercises exactly this shape. Closed, not merely claimed
   closed.
10. **`oracle_execute_check` schema separation**: confirmed in code
    (`tools.py`) that `outcome` and `aggregate_state` are two
    independent response keys, matching plan §18.3 and
    `decisions/0081`'s own established semantics — no collapsed
    four-valued field.
11. **`--enable-execution` disclosure**: `codecompass mcp-serve --help`
    (re-run directly) states, verbatim, "equivalent to letting that
    client run `pytest` on this machine directly. No sandbox, container,
    or restricted user is implemented" — matches plan §5.2's own
    required disclosure exactly. `docs/reference/mcp.md` carries the
    identical disclosure.

## DoD condition 1 — FAIL: no `docs-reconstructor` audit evidence, and real drift found

`grep`-ing every Phase 88 artifact this phase produced (both stage
commit messages in full, both stage audit reports, the phase retro, the
Ledgerkit-demonstration retro, every `CHANGELOG.md` entry under "Phase
88 ...", `planning/CONTEXT.md`) for `docs-reconstructor` returns **zero
hits** — contrasted directly against every comparable prior
phase/sub-stage (e.g. every one of Phase 87's four sub-stages explicitly
names a `docs-reconstructor` dispatch and its verdict, `NO DRIFT` or
`DRIFT`-then-fixed, in its own retro and `CHANGELOG.md` entry). No
`planning/retros/_drift-audit-phase-88*.md`-style record exists either
(unlike e.g. `_drift-audit-phase-85.md`). The plan's own §13 DoD-mapping
table explicitly names this check as required. This looks like the
check was simply never dispatched for this phase, not merely
under-recorded.

**Direct confirmation this is a real gap, not a formality**: this audit
independently read `docs/architecture/overview.md` (a file Stage 88A's
own commit *did* touch, to fix a now-stale "no server component"/"no
MCP integration" claim) and found it **still contains a stale claim
today**, at the current HEAD:

> "5. **The MCP server** (`mcp/`, Phase 88) — a thin, read-mostly layer
> exposing subsystem 4's own knowledge API (and, **once Stage 88B
> lands**, controlled oracle execution) to a real coding agent..."
> (`docs/architecture/overview.md` line 11)

Stage 88B **has** landed — `oracle_execute_check`, `oracle_list_checks`,
and `impact_classify_change` are implemented, tested, independently
audited `PASS WITH NON-BLOCKING OBSERVATIONS`, and committed at
`a554d52`, well before this audit. `docs/architecture/overview.md` was
not touched by `a554d52` at all (confirmed via `git show --stat
--name-status a554d52`) — Stage 88B's own closeout never revisited the
one sentence Stage 88A had deliberately phrased as a future-conditional
pending that stage's own completion. This is exactly the shape of
drift a per-phase `docs-reconstructor` dispatch exists to catch (a
current-truth architecture doc misdescribing the system as of the
audited commit), and it is live in the repository today, not a
hypothetical risk.

Secondary, lower-severity observation found in the same sweep:
`docs/reference/cli.md`'s `## codecompass mcp-serve (Phase 88, Stage
88A)` heading could read as scoping the whole command to Stage 88A only
(the body text immediately below correctly describes `--enable-
execution`/Stage 88B, so this is a heading-only ambiguity, not a
body-text inaccuracy) — worth folding into the same fix pass, not
independently blocking.

Everything else checked for drift (`docs/architecture/components.md`'s
`mcp`/`change_impact.py`/`oracle.py` entries, `docs/reference/mcp.md`
in full, `docs/reference/cli.md`'s body text) is accurate and current —
the gap found is narrow, but its existence, combined with zero
process evidence that the required independent check ever ran, is
sufficient on its own to fail this condition.

## DoD condition 2 — FAIL: `planning/CONTEXT.md` does not reflect the current state

`planning/CONTEXT.md`, as currently committed (unchanged by `a554d52`
beyond its own prior update, and **not touched at all** by `4763fcb`),
states, verbatim, at the current HEAD:

- "**Stage 88B (assurance integration) is now also implemented, not yet
  committed**" — false: Stage 88B has been committed since `a554d52`.
- "...its two new append-only result files are **staged** alongside
  this stage" — false: both files are committed (confirmed in `a554d52`'s
  own `--name-status` diff, item A).
- "**Next step: learnings triage**, then the terminal, whole-phase
  Definition-of-Done audit... not yet re-attempted as of this note" —
  false: the triage completed and landed as `4763fcb`.
- "Nothing is pushed to `origin/main` yet beyond `7a96d89`" — false:
  `origin/main` is at `4763fcb` (confirmed via `git fetch` +
  `git rev-parse HEAD origin/main`, both identical).

This is not a cosmetic staleness — it is the file `CLAUDE.md` §4
designates as "the tie-breaker if commits, changelog, and milestones
ever drift" currently asserting commit/push state that is mechanically,
trivially false against `git log`/`git status` at the moment of this
audit. `CLAUDE.md` §5 names "`planning/CONTEXT.md` reflects the new
state" as its own, separate DoD condition — distinct from the retro,
the changelog, and the audit itself — and it does not hold.

(For context, not excusing the gap: the underlying cause is that the
Stage 88B commit and the Ledgerkit-demonstration/retro/learnings work
were drafted in one continuous session and the `CONTEXT.md`/retro
"Outstanding" language describing the not-yet-committed state was swept
into the final commits without a last reconciliation pass once they
actually landed — the phase retro's own "Outstanding at the time of
this retro" section has the identical shape of staleness for the same
reason, though that section is explicitly framed as a point-in-time
note rather than a current-state claim, which `CONTEXT.md` is not.)

## Everything else checked — holds

- **Code implemented**: Stage 88A's nine tools + Stage 88B's three
  tools, `src/codecompass/mcp/{security,tools,server}.py`,
  `src/codecompass/change_impact.py`, `oracle.py` hardening — all
  present, tested, matching the plan's own §6/§11.1/§11.2 design
  exactly (independently spot-checked against source for several of the
  plan's own most load-bearing claims: confinement-before-delegation,
  schema separation, `_chdir` wrapper coverage, `--enable-execution`
  disclosure — see "independently re-run" above).
- **`CHANGELOG.md`**: a distinct `[Unreleased]` entry per sub-stage/
  amendment, each scoped to its own commit, none batching unrelated
  phases together — matches `CLAUDE.md` §3.
- **Phase retro** (`planning/retros/phase-88-agent-integration-mcp.md`):
  every `TEMPLATE.md`-equivalent section substantively filled (Goal,
  Delivered vs planned, Lessons learnt ×3 with real generalisable
  content, Process-improvement feedback, Outstanding) — not a stub.
- **Ledgerkit demonstration retro**
  (`planning/retros/phase-88-ledgerkit-demonstration.md`): real,
  independently-verified (not self-certified) per item 8 of the
  dispatch — the reviewer reproduced the negative control directly with
  `pytest` (not trusting the implementing session's own script output),
  independently assessed context relevance against real Ledgerkit
  source, and confirmed the real checkout's clean `git status`/`git
  diff` itself — all three independently re-confirmed by this audit too
  (see item 6 above).
- **Reference-project / context-evaluator condition**: satisfied — the
  "Independent verification" section of the Ledgerkit retro is a
  genuine `context-evaluator`-style independent pass, not the
  implementing session's own account, and is linked from both the
  phase retro and `planning/CONTEXT.md`.
- **Scratch-copy vs real-landed-change distinction (dispatch item 10a)**:
  honestly and correctly drawn throughout — the plan's own §12.2
  pre-authorises the scratch-copy fallback explicitly, the demonstration
  retro states plainly "This is the weaker, scratch-copy variant, not
  the real-change variant," and this audit independently confirmed the
  real `~/projects/ledgerkit` checkout is untouched. Phase 88's own
  exit gate (§13's own DoD-mapping table) does **not** require landing
  the real change — it requires completing "a genuine development
  change ... through supported interfaces," which §12.2's own
  pre-authorised fallback explicitly allows to be the scratch-copy
  variant when cross-repository write authorisation isn't separately
  granted. This is genuinely true from the plan's own text, not
  assumed.
- **Knowledge-retrieval vs generated-documentation distinction (dispatch
  item 10b)**: honestly drawn — plan §18.2 redirects the
  documentation-use evidence from `docs_get_grounded_region` (which
  genuinely has no relevant published region) to `knowledge_get`-
  surfaced Claim/Evidence/Decision records: no claim anywhere in the
  retro, `CONTEXT.md`, or `CHANGELOG.md` that generated/published
  documentation was the source of the demonstration's materially-useful
  context.
- **Learnings triage (DoD condition 5)**: genuinely completed —
  L-131 through L-134 each have full `origin`/`evidence`/
  `classification`/`status` fields in `planning/learnings/inbox.md`,
  each resolved to a real outcome (three `promoted` into named
  governance/agent-definition files, confirmed by direct diff reading
  of all four destination files; none left at `candidate`). **Now
  actually committed and pushed** (`4763fcb`), not merely staged as the
  dispatch described — a positive correction to the dispatch's own
  framing, not a gap.
- **Stage-level audits persisted (dispatch item 9)**: both exist, both
  substantive (see "independently re-run" item 8 above).
- **No scope creep**: `git show --stat --name-status` for all three
  commits (`7a96d89`, `a554d52`, `4763fcb`) lists only files the plan's
  own §11.1/§11.2 deliverables name, or governance/learnings files for
  the triage commit — no unexplained file.

## What must be fixed before re-audit

1. **Dispatch an independent `docs-reconstructor` per-phase drift audit**
   scoped to everything Phase 88 changed (Stage 88A + 88B + the
   demonstration + the closeout commits), and fix every finding it
   raises — at minimum, the already-identified stale sentence in
   `docs/architecture/overview.md` line 11 ("...and, once Stage 88B
   lands, controlled oracle execution..." must state Stage 88B's
   oracle-execution capability as already present, not pending).
   Consider the `docs/reference/cli.md` heading-scoping ambiguity in
   the same pass.
2. **Rewrite `planning/CONTEXT.md`'s current-state section** to reflect
   the real, current state: Stage 88A and Stage 88B are both committed
   (`7a96d89`, `a554d52`); the Ledgerkit demonstration is done
   (scratch-copy variant, real checkout untouched); learnings L-131
   through L-134 are triaged and landed (`4763fcb`); everything through
   `4763fcb` is pushed to `origin/main`. Remove every "staged"/"not yet
   committed"/"not yet re-attempted" clause that is no longer true.
3. **Re-run this audit** against the resulting commit(s) once 1-2 land —
   per `CLAUDE.md` §5's own voiding rule, this FAIL (and the evidence
   above) does not carry forward once new commits touch the
   just-audited scope; a fresh pass is required, not a re-stamp of this
   one.

---

# Re-audit (2026-11-15, commit `65ab8d9`)

**Scope**: the full Phase 88 effort as it now stands at `65ab8d9`
("fix(phase-88): resolve terminal audit documentation findings") on
`main`, confirmed pushed to `origin/main` (`git status` clean, branch
up to date). This supersedes nothing above — the original FAIL and its
evidence are preserved verbatim; this section is a fresh, independent
pass against the corrected state, per `CLAUDE.md` §5's voiding rule
("any commit after the auditor's own pass that touches audited scope
voids that pass and requires a fresh one").

## VERDICT: FAIL

Both of the prior FAIL's own named gaps are now genuinely closed,
confirmed below by direct re-reading rather than trusted from either
prior report's own account. But this re-audit, run fresh rather than as
a checklist against the prior report, finds one further, real,
non-trivial Definition-of-Done gap the prior pass did not check: the
phase retro omits substantial required content from
`planning/retros/TEMPLATE.md`'s own structure — not merely a heading
mismatch, but the actual content a future session needs (arc
orientation, forward trajectory) is genuinely absent from the one file
`CLAUDE.md` §5 designates to carry it.

## What was independently re-verified (not trusted from either prior report)

1. **Full regression suite, re-run myself**: `.venv/bin/python -m
   pytest -q` → **1464 passed, 2 skipped**, exit 0 (429s). No
   regression, including from the `server.py` docstring-only edit in
   `65ab8d9`.
2. **Ruff, whole repo, re-run myself**: `.venv/bin/ruff check .` →
   **167 errors** — matches the confirmed post-Stage-88B baseline
   exactly; `65ab8d9`'s own diff touches no `.py` logic besides
   docstrings, so no debt change is expected or found.
3. **`.venv/bin/python scripts/check_user_docs.py --strict`** →
   `check_user_docs: no findings`.
4. **Finding 1 (no `docs-reconstructor` drift audit had ever run)
   — confirmed fixed**: `planning/retros/_drift-audit-phase-88.md`
   exists (186 lines), read in full. Genuinely substantive, not a
   stub: scoped explicitly to `dbcfe50^..4763fcb` (all five Phase 88
   commits including the learnings-triage commit), checks
   `docs/reference/mcp.md`'s full tool table line-by-line against the
   real 12 registered tools, the validation/confinement section
   against `security.py` directly, the bounded-subprocess claims
   against `oracle.py::run_pytest_check` directly, re-greps for every
   other "Stage 88" conditional across `README.md`/`docs/`/
   `architecture/`/`ai-docs/` and inspects each hit individually,
   checks `docs/architecture/components.md`'s new rows against the real
   modules, and explicitly flags (non-blocking) the two omissions later
   fixed in `65ab8d9` (`ai-docs/README.md`, `README.md`'s doc map) plus
   the `server.py` docstring staleness. Verdict **NO DRIFT**. This is a
   real, independent audit, not a self-report.
5. **The specific live drift that audit found, re-checked directly in
   the current file**: `docs/architecture/overview.md` line 11 now
   reads "...a thin layer exposing subsystem 4's own knowledge API, plus
   controlled oracle execution (Stage 88B), to a real coding agent...:
   nine read-only tools and three assurance tools (`impact_classify_
   change`, `oracle_list_checks`, `oracle_execute_check`)" — the "once
   Stage 88B lands" conditional is gone, present-tense, accurate against
   `server.py::build_server`'s real 12-tool registration (confirmed by
   reading `server.py` directly). `docs/reference/cli.md`'s `mcp-serve`
   heading now reads `(Phase 88)`, not `(Phase 88, Stage 88A)` —
   confirmed by direct read, matching the body text which already
   covered both stages.
6. **The three further non-blocking omissions, re-checked directly,
   all fixed**: `src/codecompass/mcp/server.py`'s module docstring and
   `build_server`'s own docstring now both read "the nine Stage 88A
   read-only tools and the three Stage 88B assurance tools" / "Registers
   the nine Stage 88A read-only tools and the three Stage 88B assurance
   tools" — no longer claims only nine total; grepped the whole repo for
   a stray unqualified "nine"/"twelve" claim in `docs/reference/mcp.md`,
   `README.md`, `ai-docs/README.md` — none found. `ai-docs/README.md`
   now has a new "An MCP server" bullet under "What it does" (names
   `codecompass mcp-serve`, the stdio transport, `--enable-execution`,
   "no sandbox isolation, no network exposure") and a new table row
   under "Where to look next" pointing at `docs/reference/mcp.md` —
   confirmed by direct read, not just the diff. `README.md`'s
   documentation-map bullet for `docs/reference/` now explicitly names
   "the MCP server's tool surface/security model" alongside the CLI
   reference, `vendor.toml`, and the adapter protocol it already named —
   confirmed by direct read.
7. **Finding 2 (`planning/CONTEXT.md` stale) — confirmed fixed**: read
   the file's full "Current phase" section directly (not the diff
   alone). It now states, accurately against `git log`: Stage 88A
   committed `7a96d89`; Stage 88B "implemented and committed (`a554d52`)"
   (no longer "not yet committed"); the demonstration's two result files
   "committed alongside this stage" (no longer "staged"); learnings
   triage "complete and committed (`4763fcb`)", all four promoted, with
   the correct destination files named; "Everything through `4763fcb`
   is pushed to `origin/main`" (independently re-confirmed myself via
   `git status`/`git log` — true); the first terminal-audit FAIL and its
   two fixes are recorded accurately, in past tense, as a point-in-time
   note, with the correct "Next step" pointing at the drift audit then
   a fresh terminal re-audit; `planning/ROADMAP.md`'s Phase 88 row
   "remains, correctly, not `done`" — true, independently confirmed
   (`grep` on the live row: status is `planned`). No false claim found
   anywhere in this section against the real current git state.
8. **`CHANGELOG.md`**: the new `[Unreleased]` "Phase 88 — learnings
   triage and terminal-audit corrective pass" entry (added in `4763fcb`,
   unchanged by `65ab8d9` except that `65ab8d9` is itself documented
   inline within that same entry's own "Both fixed" closing sentence) —
   read directly, accurately summarises the FAIL, its two causes, and
   that both are fixed. Distinct, correctly scoped to this phase only.
9. **Protected-file drift**: `git log --oneline dbcfe50^..65ab8d9 --
   CLAUDE.md` shows exactly one touching commit (`4763fcb`); `git log -p`
   on that commit confirms a pure addition (the L-131 sentence) directly
   after the existing `L-088` sentence, no other line changed. Recorded
   as user-approved per §0 in `planning/v1-redefinition/
   proposed-governance-changes.md` §Q ("Status: approved and landed
   (2026-11-15) ... presented to the user for §0 approval and approved
   as drafted") — same evidentiary form this project has used for every
   prior §0 approval record (e.g. `L-070`, `L-075`). `decisions/0095`:
   `git log --follow -p dbcfe50^..65ab8d9 -- decisions/0095*` shows three
   touching commits, all before implementation (`dbcfe50`, `06c095a`,
   `26947ff`), each appending a new `## Amendment` section or a bullet
   inside one; no line of the original `## Decision`/`## Context`
   content is ever removed or rewritten — append-only convention held.
   No other `decisions/*` file touched anywhere in this phase's commits.
10. **Real `~/projects/ledgerkit` checkout, re-checked myself (not
    trusted from the demonstration retro)**: `git status --porcelain`
    and `git diff --stat` both empty; `git rev-parse HEAD` →
    `a7740fd04fe1814d2a557bfcb67a9a775a4a22f9` — untouched.
11. **Changed-file list vs. the plan's own Files section**: `git show
    --stat --name-status` for `7a96d89` and `a554d52` lists only
    `src/codecompass/mcp/*`, `change_impact.py`, `scripts/
    assess_change_impact.py`, `oracle.py`, `cli.py`, `pyproject.toml`,
    the named test files, the named docs, `CHANGELOG.md`, `planning/
    CONTEXT.md`, `planning/ROADMAP.md`, the two new result files, and
    the retro/audit files — every one named by the plan's own §6/§11.1/
    §11.2/§12 deliverables or required by `CLAUDE.md` §2/§3/§5; nothing
    extraneous. `65ab8d9` touches only the seven files its own commit
    message describes plus the two new audit-report files — no scope
    creep.
12. **Stage audit reports, re-read in full**: `_audit-phase-88-stage-
    88a.md` (110 lines) and `-88b.md` (199 lines) — both substantive,
    both independently re-run full suite/Ruff/`check_user_docs.py`,
    both include real, non-mocked reproductions of their own named
    defects (the directory-substitution-after-open adversarial test for
    88A; the `_chdir` monkey-patch-to-no-op reproduction and the
    `changed[].path` missing-key `KeyError`-to-clean-`ToolError` fix for
    88B). Neither is a self-report rehash.
13. **Roadmap exit criteria, independently assessed from the plan text
    itself** (not the prior audit's conclusion):
    - **(a)** `planning/phase-88-agent-integration-mcp.md` §12.2
      ("Fallback") states, verbatim: "The honest fallback is the same
      candidate, executed against a disposable scratch copy of
      Ledgerkit rather than the real checkout ... used only if the
      cross-repository write authorisation for the real
      `~/projects/ledgerkit` checkout isn't granted at the
      demonstration's own start," and requires only that "the
      demonstration's own closeout report ... must name explicitly
      which of the two actually ran, since the scratch-copy variant is
      a weaker, not equivalent, substitute." The plan's own §13 DoD
      mapping (and §12.4, "Explicitly not a productivity claim") does
      not require a landed change in the real checkout to close the
      phase — it pre-authorises the scratch-copy variant as sufficient,
      provided it is named honestly as the weaker substitute. Confirmed
      from the plan's own text, not assumed or taken on the prior
      audit's word.
    - **(b)** Re-checked myself: `~/projects/ledgerkit`'s `git status
      --porcelain` and `git diff --stat` are both empty; `HEAD` is
      `a7740fd04fe1814d2a557bfcb67a9a775a4a22f9`. Untouched.
    - **(c)** `planning/retros/phase-88-ledgerkit-demonstration.md`
      (read in full): states plainly, in its own "Independent
      verification" section, that the `docs_get_grounded_region`
      documentation-use leg was corrected during planning (§18.2) to
      acknowledge it has no genuinely relevant published region for
      this task, and that "the materially-informing context here comes
      from `knowledge_get`-surfaced" Claim/Evidence/Decision records
      (`EV-BFS-001`, `CL-BFS-004`/`CL-BFS-005`, `DEC-BFS-002`) — matching
      the phase retro's own §12.1 account of `DEC-BFS-002` shaping the
      new test's row/subtotal assertions. No claim anywhere in the
      demonstration retro, the phase retro, `CONTEXT.md`, or
      `CHANGELOG.md` that generated/published documentation
      (`docs_get_grounded_region`) was the source of the demonstration's
      materially-useful context. Honestly reflected, not overclaimed.

## New finding this re-audit raises — DoD condition 4 (phase retro) — FAIL

`planning/retros/phase-88-agent-integration-mcp.md` (141 lines, read in
full) uses only five headings: `## Goal`, `## Delivered vs planned`,
`## Lessons learnt`, `## Process-improvement feedback`, `## Outstanding
at the time of this retro`. This satisfies `CLAUDE.md` §5's own literal,
narrower four-part list ("goal, delivered vs planned, lessons learnt,
process-improvement feedback") — which is why the prior audit pass
(above) accepted it as "every `TEMPLATE.md`-equivalent section
substantively filled... not a stub." Re-reading `planning/retros/
TEMPLATE.md` directly for this re-audit, that acceptance was too
lenient: the template's real, required structure is `Where we are` /
`Goal` / `Scope delivered vs planned` / `What was achieved` / `What
worked` / `What didn't work` / `Lessons learnt` / `Process-improvement
feedback` / `Candidate learnings filed` / `Where we're going` / `Time /
cost note` — and this project's own three immediately-preceding phase
retros (`phase-83-semantic-change-assurance.md`,
`phase-84-consolidated-knowledge-api.md`,
`phase-85-self-curation-knowledge-quality-validation.md`, all read and
`grep`-checked directly for this re-audit) each use every one of these
headings in full, with real, substantive, phase-specific content under
each.

Phase 88's own retro has **no `Where we are` section at all** (no arc/
stage-group orientation — nothing locating this phase inside the
Knowledge-Driven Software Development group, nothing on what Phase 87
established that this phase built on, nothing narrating the
project's overall state after this phase in the template's own
requested form) and **no `Where we're going` section at all** (no
explicit statement of the next phase(s) — Phase 89's reconciliation
work, Phase 90's comparative trials — the gate ahead, or the
trajectory). It also has no separately-framed `What worked` / `What
didn't work` sections — "Lessons learnt" and "Process-improvement
feedback" cover adjacent ground but answer a different question each
(a generalizable takeaway vs. a workflow-friction report) than "what
should we keep doing" / "what failed or cost more than it returned,"
which the template asks for explicitly and separately. No `Candidate
learnings filed` section (the four learnings this phase produced are
recorded only in `CLAUDE.md`'s diff, `promoted.md`, and `CONTEXT.md` —
never listed inside the retro itself, unlike every one of the three
comparison retros). No `Time / cost note`.

This is not a cosmetic heading mismatch: the actual *content* those
missing sections would carry — arc orientation and forward trajectory,
specifically — is genuinely absent from the one document `CLAUDE.md`
§5 designates to carry a phase retro. A future session opening only
this retro (as `CLAUDE.md` §4's own CONTEXT.md-is-for-session-resumption
split implies a retro should support) gets no sense of where Phase 88
sits in the v2 roadmap's arc or what comes next from the retro itself —
that information exists only in `CONTEXT.md`/`ROADMAP.md`, not in the
retro the DoD names as the vehicle for it.

This is not a hypothetical process nitpick: `release-phase-auditor`'s
own governing checklist (item 4) is explicit and unconditional — "with
every `planning/retros/TEMPLATE.md` section filled substantively —
including **Where we are** (arc/stage context), **What worked** /
**What didn't work**, and **Where we're going** (next phase(s), gate
ahead, trajectory). Not a stub, unless the phase is genuinely trivial
(then a few real lines still cover where-we-are/goal/shipped/
worked-didn't/next)." Phase 88 — a five-round-amended, two-stage,
12-tool MCP server plus a real cross-repository demonstration — is
plainly not a trivial phase, so no carve-out applies. `CLAUDE.md` §5's
own shorter list is the DoD's minimum restatement, not a license to
skip the template's own additional required structure that this
project's own immediately preceding three phases all satisfied in
full; reading it as satisfied by the narrower four-item list alone (as
the prior pass did) was the error, not a genuine disagreement between
`CLAUDE.md` and this checklist that would make `CLAUDE.md`'s text
"win" under §0's hierarchy — there is no textual conflict here, only a
retro that is thinner than the template and than precedent, and item 4
requires catching that.

## Everything else checked — holds

- **Code implemented, docs/architecture/decisions updated, changelog
  entry added**: all confirmed directly, items 1-9 above.
- **Learnings triage (DoD condition 5)**: `planning/learnings/
  promoted.md` has all four entries (`L-131` through `L-134`), each
  with a real classification, a real destination file, and (for
  `L-131`) the explicit "user-approved per §0" annotation — confirmed
  genuinely triaged, not left at `candidate`. **Observation, not a
  finding**: all four still cite `@ <this phase's own closeout commit>`
  rather than the real hash of `65ab8d9`/`4763fcb`. Checked this
  specifically per the dispatch's own instruction to look for exactly
  this — but `grep -n "this phase's own closeout commit"
  planning/learnings/promoted.md` shows this literal, unresolved
  placeholder string is this file's own long-standing, unbroken
  convention going back dozens of phases (e.g. `L-022`, `L-050`,
  `L-061`, `L-089`, `L-121`, all long-`done` phases, all still carry the
  identical placeholder text, never backfilled with a real hash after
  the fact). This is not a Phase-88-specific regression or an omitted
  fix — it is this project's own established (if slightly imprecise)
  practice, applied consistently here exactly as everywhere else in the
  same file. Not counted as a finding.
- **Reference-project / `context-evaluator` condition**: satisfied —
  confirmed directly in item 13(c) above.
- **Stage-level audits persisted**: both exist, both substantive
  (item 12 above).
- **No scope creep**: confirmed directly in item 11 above.
- **Roadmap exit criteria**: independently assessed from the plan text
  itself, confirmed in item 13 above — the scratch-copy variant is
  genuinely plan-pre-authorised, not a workaround invented after the
  fact.

## What must be fixed before re-audit

1. **Bring `planning/retros/phase-88-agent-integration-mcp.md` up to
   `planning/retros/TEMPLATE.md`'s full required structure**, matching
   the three immediately-preceding phase retros' own established
   practice: add a substantive `Where we are` section (this phase's
   place in the Knowledge-Driven Software Development arc; what Phase
   87 established that this phase built on; the project's overall state
   after Phase 88, narratively); separately-framed `What worked` and
   `What didn't work` sections (distinct from the existing "Lessons
   learnt"/"Process-improvement feedback," which may be retained
   alongside them); a `Candidate learnings filed` section naming
   `L-131`-`L-134` and their real destinations; a `Where we're going`
   section naming Phase 89 (incremental knowledge/documentation
   reconciliation) and Phase 90 (comparative development trials) as
   the next phases, and the gate/trajectory between here and there; a
   `Time / cost note` if information to populate one is available (a
   few honest lines if not, rather than omitting the heading).
2. **Re-run this audit** against the resulting commit once 1 lands —
   per `CLAUDE.md` §5's own voiding rule, this FAIL does not carry
   forward once a new commit touches the just-audited scope (the retro
   file itself); a fresh pass is required, not a re-stamp of this one.
   Everything else checked in this re-audit (items 1-13 above) should
   not need re-verification unless the retro edit itself touches
   anything beyond the retro file.


---

# Second re-audit (2026-11-15, commit `f2a1d72`)

**Scope**: the full Phase 88 effort as it now stands at `f2a1d72`
("fix(phase-88): complete phase retro per TEMPLATE.md"), the current
local `main` HEAD (one commit ahead of `origin/main` — not yet pushed,
blocked by this environment's own commit-control classifier per the
dispatch; this does not affect the audit itself). This supersedes
nothing above — the original FAIL and the first re-audit's own FAIL are
preserved verbatim; this section is a fresh, independent pass against
the retro-rewrite state, per `CLAUDE.md` §5's own voiding rule.

## VERDICT: PASS

The one gap the first re-audit raised — the phase retro's own
incomplete `TEMPLATE.md` structure — is now genuinely closed. Nothing
else in Phase 88's scope was touched by this commit, and the prior
re-audit's own confirmations (items 1-13 of that section) remain valid
on direct spot-check, below.

## What was independently re-confirmed

1. **Commit scope, confirmed directly, not assumed**: `git show --stat
   f2a1d72` touches exactly three files: `CHANGELOG.md` (+9, pure
   addition), `planning/retros/_audit-phase-88.md` (+309, the first
   re-audit's own report, appended before this commit landed — not this
   pass's own writing), `planning/retros/
   phase-88-agent-integration-mcp.md` (+242/-57, the retro rewrite). No
   `src/`, `tests/`, `docs/`, `architecture/`, `decisions/`, `CLAUDE.md`,
   or `planning/ROADMAP.md`/`planning/CONTEXT.md` file is touched —
   confirmed directly, not taken from the dispatch's own framing.
   `CLAUDE.md` specifically: absent from the file list entirely, so no
   protected-file drift in this commit.
2. **`planning/retros/phase-88-ledgerkit-demonstration.md`**: untouched
   by `f2a1d72` (absent from its file list) and by any commit after
   `a554d52` (`git log --oneline -- planning/retros/
   phase-88-ledgerkit-demonstration.md` shows only `a554d52`); still
   155 lines, still exists, still the same substantive, independently-
   verified account the first re-audit confirmed (its own item 13(c)) —
   a non-event, exactly as the dispatch anticipated.
3. **Retro content, read in full against `TEMPLATE.md` section-by-
   section**: `planning/retros/phase-88-agent-integration-mcp.md` now
   carries all eleven of `TEMPLATE.md`'s headings in the template's own
   order — `Where we are`, `Goal`, `Scope delivered vs planned`, `What
   was achieved`, `What worked`, `What didn't work`, `Lessons learnt`,
   `Process-improvement feedback`, `Candidate learnings filed`, `Where
   we're going`, `Time / cost note` — each with phase-specific,
   substantive content, not filler:
   - **Where we are**: names the three foundations this phase built on
     (Phase 83 change-impact analysis, Phase 84 consolidated knowledge
     API, Phase 87 documentation-grounding surface), the v2-roadmap
     deliverable group and line range it belongs to, the Phase 88/89
     split and why (`decisions/0084`/`0085`), and the concrete
     post-phase state (a working 12-tool stdio MCP server) — genuine
     arc orientation, not a re-list of "Phase 88 did X." Independently
     verified against `planning/v2-roadmap.md` lines 115-128 and
     `decisions/0085` §3 (see below) — both check out exactly.
   - **What worked / What didn't work**: now separately framed and
     genuinely distinct, as the template requires. "What worked" names
     three concrete, positive mechanisms (the amendment-round planning
     investment, stage-level audits catching gaps early, the rigorous
     scratch-copy demonstration). "What didn't work" names three real
     frictions — the unwritten Stage 88A audit record, the two-pass
     terminal-audit FAIL history (detailed further immediately below),
     and a learnings-triage rate-limit delay — not vague, not a restated
     "Lessons learnt."
   - **Candidate learnings filed**: names all four (`L-131`-`L-134`) with
     their real destinations. Cross-checked directly against
     `planning/learnings/promoted.md`: `L-131` → `CLAUDE.md` §1
     (user-approved per §0) match, `L-132` → `agent-led-development.md`
     §1 match, `L-133` → `context-quality-evaluation.md` §1 match,
     `L-134` → `release-phase-auditor.md` + `agent-led-workflow.md`
     match — exact, no destination misstated.
   - **Where we're going**: names Phase 89 (incremental knowledge/
     documentation reconciliation) as next, states it is independently
     deliverable and not dependent on this phase's MCP server, citing
     `decisions/0085` §3. Independently verified against that decision
     record directly (§3's own text: "Its prerequisites are Phase 84
     (API) and Phase 87 (documentation surface to reconcile) only — not
     Phase 88") and against `planning/v2-roadmap.md`'s own dependency
     diagram (lines 115-128, which labels the Phase 89 branch "...
     independent of MCP transport (0085 §3)") — both confirm the
     retro's claim exactly, not merely asserted. Also correctly names
     Phase 90 as the gate both 88 and 89 feed, and states explicitly
     that this phase confirmed rather than changed the planned
     trajectory.
   - **Time / cost note**: present, honest about the absence of token
     metering, and does not overclaim an economic comparison (correctly
     deferring that to Phase 90's own separately-gated scope, consistent
     with the Ledgerkit demonstration retro's own "not a productivity
     claim" framing).
4. **Honesty check on "What didn't work"**: the retro's own account of
   the two-pass terminal-audit FAIL history is not softened — it states
   plainly that the audit "FAILed twice before reaching PASS," names
   both causes accurately (the missing `docs-reconstructor` drift audit
   plus stale `CONTEXT.md`, then the retro's own incomplete template
   structure caught only by "a second, independent re-audit holding the
   retro to `release-phase-auditor`'s own fuller governing checklist"),
   and does not reframe the first terminal-audit pass's leniency as
   anything other than what it was. Matches this file's own prior two
   sections verbatim in substance.
5. **Light re-confirmation of the first re-audit's own prior findings**
   (per the dispatch's own instruction — not a full from-scratch
   reproduction, since `f2a1d72`'s diff touches none of that scope):
   - `git status` on `codecompass`: working tree clean, local `main` one
     commit ahead of `origin/main` (`f2a1d72` itself, unpushed) —
     consistent with the dispatch's own account of the push being
     blocked by the environment's commit-control classifier, not a
     defect in this audit's own scope.
   - `.venv/bin/ruff check .`: **167 errors** — identical to both prior
     passes' own recorded baseline; no regression, as expected from a
     docs/retro-only diff.
   - `~/projects/ledgerkit`: `git status --porcelain` and `git diff
     --stat` both empty; `HEAD` at
     `a7740fd04fe1814d2a557bfcb67a9a775a4a22f9` — identical to both
     prior passes' own recorded value. Untouched.
   - `planning/ROADMAP.md`'s Phase 88 row: still `planned`, correctly —
     the terminal reconciliation commit has not happened yet, as
     expected; this audit does not flip it.
   - `planning/CONTEXT.md`: still carries its pre-fix "Learnings triage
     and the terminal, whole-phase DoD audit remain not yet done"
     language — stale again relative to the now-complete triage and
     two-pass audit, but this is expected and not a new finding: per
     `CLAUDE.md` §5's own explicit exemption, `CONTEXT.md`'s
     current-state section is overwritten by the terminal
     `roadmap-context-curator` reconciliation commit itself, which has
     not yet run and is not required before this audit's own PASS.
     Flagging this explicitly for the lead's reconciliation commit, not
     as a gap in this commit's own scope.

## What remains — none, for this commit's own scope

No further finding. The retro is now genuinely complete against
`TEMPLATE.md`, consistent with the real git/audit history, and
consistent with `decisions/0085` §3 / `planning/v2-roadmap.md`'s own
dependency diagram on the one forward-looking claim ("Phase 89 is
independently deliverable") that was checkable against an external
source rather than taken on the retro's own word.

## Conclusion

Every `CLAUDE.md` §5 Definition-of-Done condition for Phase 88 now
holds against the real, current commit (`f2a1d72`): code implemented
and tested (prior passes); `docs/`/`architecture/`/`decisions/` updated
(prior passes, re-confirmed via the unchanged diff scope here); an
independent `docs-reconstructor` per-phase drift audit ran and returned
`NO DRIFT` (first re-audit, item 4); a `CHANGELOG.md` entry exists for
this specific corrective commit (confirmed directly above) in addition
to every prior phase-scoped entry; `planning/CONTEXT.md` reflects the
state as of the last commit that was in scope for it to describe (the
one remaining staleness is explicitly exempted pending the terminal
reconciliation commit, not a live gap this audit is required to close);
`planning/ROADMAP.md` has not yet been marked `done` (correctly, pending
that same reconciliation commit); the phase retro now satisfies
`TEMPLATE.md` in full (this section); candidate learnings are triaged
with destinations confirmed (this section); no protected-file drift in
this commit (this section); no scope creep (this section); the
reference-project/`context-evaluator` condition is satisfied (first
re-audit, item 13(c)).

**`planning/ROADMAP.md`'s Phase 88 row may now be flipped to `done`.**
Per `CLAUDE.md` §5's own explicit, narrow exemption, the terminal
`roadmap-context-curator` reconciliation commit itself — flipping
`ROADMAP.md`'s Phase 88 row to `done`, overwriting `planning/
CONTEXT.md`'s current-state section, and updating
`planning/phase-88-agent-integration-mcp.md`'s own Status line, and
nothing else — is not "audited scope" for this purpose and does not
require a further re-audit, provided it touches only those three named
targets. If it touches anything beyond them (a changelog entry,
`docs/`, `architecture/`, `decisions/*`, `src/`, tests,
`planning/learnings/**`, `planning/context-gaps/**`, or any other file),
this PASS is voided and a fresh audit is required, exactly as
`CLAUDE.md` §5 states.
