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
