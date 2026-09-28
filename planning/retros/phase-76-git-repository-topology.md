# Phase 76 retro — Git repository topology awareness (worktrees + submodules)

- **Date:** 2026-09-28
- **Commit(s):** `7ac9f34` (initial plan), `5c0705a` (first amendment),
  `e80044d` (second amendment), `c12b74a` (third amendment — fixture
  equivalence + unsynced query-topology path), `46ab3c5` (implementation),
  `92e6e8e` (task-context evaluation), `0db8c12` (drift-audit fix) — see
  git log for exact detail.
- **Agents used:** two independent agents (baseline, treatment),
  `context-evaluator`, `docs-reconstructor` (drift audit + re-audit),
  `knowledge-curator`, `release-phase-auditor`, `roadmap-context-curator`

## Where we are

Post-v1, Priority A track (`decisions/0062`). Phase 75 validated Priority
A's premise on Ledgerkit with a **LOW**-advantage result and recommended
a second, differently-shaped trial before any funding decision on
`CG-001`/`CG-007`. Rather than that trial, the user made a direct request
for a new, narrowly-scoped Priority A capability: Git repository topology
awareness (worktrees + submodules) — the ability for a fresh agent to
mechanically distinguish a worktree of *this* repository from a
genuinely separate project, and a submodule's parent-pinned commit from
what's actually checked out. This phase is both a capability build (the
first Priority A capability build since Phase 73) and its own real-task
validation trial, evaluated the same way as Phase 75.

## Goal

Deliver `codecompass query topology`, backed by a new read-only
`git_topology.py` detection module and three new graph tables, validated
against this project's own real submodules and a disposable worktree,
and independently evaluate whether it gives a fresh agent a measurable
task-context advantage — following the exact process this project
requires (plan → amend as issues surface → implement → validate against
real repository state → evaluate → close out), without skipping any
Definition-of-Done gate.

## Scope delivered vs planned

Delivered exactly as scoped in the thrice-amended
`planning/phase-76-git-repository-topology.md`: `git_topology.py`
(detection + scheme-aware URL sanitization); three new `context-graph.db`
tables (schema version 9→10) via the introspection-based migration
pattern; `rebuild_project_graph` wiring; `codecompass query topology`
(`--json`, plus a narrow not-yet-indexed path via
`_open_graph_for_topology` rather than touching the shared
`_open_graph_or_note` helper, per the user's own "don't change unrelated
query commands unless a shared change is cleaner" instruction); generated
Skill/CLI-reference/architecture/ADR updates; a full unit/integration
test suite (`tests/test_git_topology.py`, plus additions to
`test_graph.py`, `test_sync.py`, `test_cli.py`); real-repository
validation (real submodules, a disposable worktree, a disposable clone);
an independent baseline/treatment/`context-evaluator` assessment from a
verified-equivalent seed-then-fork fixture design; full closeout
(CHANGELOG, CONTEXT, ROADMAP, retro, learning triage, drift audit,
completion audit). No scope drift — bare-repository support and Phase 24
project-root routing were both correctly declined, per the plan's own
non-goals.

Two corrections were made to the plan itself immediately before
implementation, both requested by the user and both resolved before any
`src/` change: (1) the baseline/treatment fixture-equivalence
contradiction (identical HEADs required while also specifying a
treatment-only post-clone commit) — resolved with a shared normalized
seed forked into baseline/treatment *after* normalization, so the
scenario is constructed identically-but-independently in each clone,
never committed; (2) the unsynced `query topology` path — a brand-new
worktree with no `context-graph.db` needed a `{"indexed": false}`
outcome, which the shared graph-open helper couldn't produce without
touching unrelated query commands — resolved with a narrow,
command-specific `_open_graph_for_topology` function instead.

## What was achieved

A real, independently-verified answer to Priority A's validation
question, on the strongest evidence yet: **PASS WITH GAPS, advantage
MODERATE** — better than Phase 75's LOW. Full report:
`planning/reference-projects/codecompass-self/phase-76-context-evaluation.md`.
Two new context gaps filed and confirmed `candidate`: `CG-010`
(submodule pin/checkout mismatch has no field distinguishing
committed-parent-state divergence from purely local uncommitted checkout
state — corroborated twice in the same trial, by both the treatment
agent's own report and the evaluator's independent follow-up) and
`CG-011` (a sibling worktree's dirtiness is honestly reported as
unprobed rather than guessed, but the CLI output itself carries no
inline signal that this could be stale — only `--help` text says so).

Three real, pre-existing bugs were found and fixed via live testing
against the real repository and real Git behaviour, none of which any
unit test alone would have caught without that grounding:
`_migrate_doc_artifacts_constraints` firing on any unrelated
`schema_version` bump (confirmed historically triggered twice already,
Phases 60 and 62); `git rev-parse --show-toplevel` failing distinctively
against a bare repository while `--git-common-dir` succeeds; and the
original URL sanitizer leaving `ssh://user:password@host/...` passwords
fully exposed. A fourth bug (`git worktree list --porcelain` reporting
the all-zero SHA for an unborn branch, not an absent HEAD line) was
caught by the test suite itself before it ever reached real-repository
testing.

## What worked

- **Live testing against the real repository surfaced bugs no unit test
  would have found.** The bare-repo failure mode, the historical
  migration-trigger misfire, and the real submodule/worktree validation
  all depended on actually running commands against real Git state, not
  synthetic fixtures — consistent with this project's own stated
  preference for real-repository validation over mocked equivalents.
- **The seed-then-fork fixture design resolved a genuine methodological
  contradiction cleanly**, without weakening either the "same starting
  state" or "scenario constructed independently" requirement — normalize
  once, fork twice, construct identically-but-separately after the fork.
  This is a reusable pattern for any future baseline/treatment trial that
  needs both properties at once.
- **The narrow, command-specific `_open_graph_for_topology` fix matched
  the user's own instruction exactly** — no unrelated `query` command's
  behavior changed, and the fix is legible as belonging to this phase
  alone.
- **Three rounds of plan amendment before any code was written** caught
  real problems (a Git version floor no one had noticed, a bare-repo
  contradiction, a credential-leakage gap, a fixture-equivalence
  contradiction) at the cheapest possible point to fix them — before
  implementation, not after.
- **This is the best Priority A trial result yet (MODERATE vs. Phase
  75's LOW)** — real, corroborating evidence that a narrowly-scoped,
  concretely-motivated capability (distinguishing worktrees/submodules,
  a specific pain point rather than a broad "more context" bet) produces
  a stronger task-context advantage than a wider but vaguer capability
  would.

## What didn't work

- **`L-063` recurred, one phase after it was landed** (`L-064`, filed
  this phase). The `context-evaluator` dispatch prompt again claimed a
  fresh subagent already had access to conversation-only content (the
  baseline/treatment agents' full reports) — the exact violation `L-063`
  exists to prevent, landed at Phase 75's own closeout. The dispatched
  `context-evaluator` caught this itself, disclosed it honestly in its
  own report, and compensated by re-deriving ground truth independently
  rather than stalling. No harm resulted, but the recurrence itself is
  the finding: a rule that exists in a process document doesn't get
  consulted automatically at the point of writing a new dispatch prompt
  unless something in the writing process forces the check. `L-064`
  proposes a stronger fix than "remember the rule harder": write agent
  reports to disk immediately on receipt, before any downstream dispatch
  is drafted, so there is no conversation-only content left to
  mistakenly claim is already available.
- **The first drift-audit pass found real gaps** (`README.md`'s "Core
  idea" and `ai-docs/README.md`'s "What it does"/"It doesn't touch git"
  framing both omitted the new capability entirely) — not a process
  failure (the audit is supposed to catch exactly this), but worth
  noting that a phase this large, touching this many files, needs the
  audit to actually run rather than being treated as a formality.

## Lessons learnt

See `L-064` (filed this phase, a genuine recurrence of `L-063`): a
subagent dispatch prompt must never claim a fresh agent already has
access to conversation-only content — restating the rule a second time
clearly wasn't sufficient after its first landing; the actual fix is
mechanical (write reports to disk immediately on receipt) rather than
relying on remembering to check a process document at exactly the right
moment.

A second, non-`L-NNN` observation: plan amendments requested *before*
implementation are cheap; the same six-plus issues found across three
amendment rounds this phase (Git-version floor, bare-repo contradiction,
credential leakage, fixture-equivalence contradiction, unsynced
query-topology path, schema-migration safety) would each have been a
`src/` regression or a redone evaluation if caught after code was
written instead.

## Process-improvement feedback

Same recommendation as Phase 75's own retro, now with a second failure
to point at: write baseline/treatment (and any other agent-generated)
reports to disk immediately on receipt, before drafting any downstream
dispatch prompt that will reference them. This phase did eventually do
this (`phase-76-baseline-report.md`, `phase-76-treatment-report.md`,
written after the fact, post-`L-064`) — doing it *before* the
`context-evaluator` dispatch, not after, is the actual fix, not a
retrospective cleanup step.

## Candidate learnings filed

`L-064` (recurrence of `L-063`, filed with full root-cause analysis).
`CG-010` (submodule mismatch lacks committed-vs-uncommitted distinction)
and `CG-011` (sibling-worktree staleness has no inline signal), both
filed to `planning/context-gaps/inbox.md`, both corroborated within the
same trial (not single-occurrence speculation).

## Where we're going

Phase 76's MODERATE-advantage result is real evidence for Priority A's
premise that narrowly-scoped, concretely-motivated capabilities
outperform broad ones — this should inform how the next Priority A
candidate (from `CG-001`/`CG-007`/`CG-009`/`CG-010`/`CG-011`, or a new
one) is chosen and scoped, rather than defaulting back to the
broader-but-vaguer shape Phase 72 originally anticipated. `CG-010` and
`CG-011` are both new, narrow, concretely-corroborated candidates in the
same spirit as this phase's own motivating gap — either could be the
next Priority A trial's subject once a revisit trigger (a second
independent occurrence, per each gap's own bar) is met.

## Time / cost note

One extended session, continued across a context-compaction boundary,
spanning plan authorship, three amendment rounds, full implementation,
real-repository validation, and independent evaluation. Real AI subagent
spend: two dispatched agents (baseline, treatment) plus one
`context-evaluator` dispatch (with its own empirical follow-up
experiment), a `docs-reconstructor` drift audit and re-audit, and the
standard closeout roster (`knowledge-curator`, `release-phase-auditor`,
`roadmap-context-curator`) — no shortcuts taken on any of them. Test
suite grew by 30 new tests (`test_git_topology.py`) plus additions across
four existing test files; full `pytest`/`ruff`/`check_user_docs.py
--strict` sweep run at closeout.

## Corrective-pass addendum (2026-09-28, same day)

Phase 76 was marked `done` (commit `b3abe07`) and then reopened the same
day, at direct user request, after a review found three real defects the
original closeout — including its own independent `release-phase-auditor`
PASS WITH NON-BLOCKING OBSERVATIONS verdict — missed.

### What was found

1. **CLI false-certainty rendering.** `_render_topology`'s text renderer
   used plain Python truthiness for three nullable facts — the current
   worktree's own `is_dirty`, an initialized submodule's `child_is_dirty`,
   and `revision_matches_pin` — silently rendering an unresolved/unknown
   `None` the same as a hard `False` ("clean", "differs from pin"). This
   is exactly the false-certainty class of bug §8's own explicit-
   uncertainty discipline exists to prevent, and the original closeout's
   own test suite never caught it because no existing fixture exercised
   these three fields' `None` state specifically — every prior test used
   an explicit `True`/`False`. `--json` output was already correct (it
   round-trips the raw nullable value unchanged).
2. **Wrong Git minimum-version claim.** `decisions/0063` point 8 claimed
   Git 2.5 as the module's overall floor, verified only against
   `--git-common-dir` (genuinely 2.5). `git worktree list` and `git
   remote get-url` — both called unconditionally on every invocation —
   were confirmed, directly against Git's own release notes
   (`Documentation/RelNotes/2.7.0.txt`, cross-checked against the real
   `builtin/rev-parse.c` source at the `v2.4.0`/`v2.5.0` tags for
   `--git-common-dir` itself), to require Git 2.7.0. A real Git in the
   2.5–2.6 range would have passed the initial `rev-parse` call, then
   failed later at `worktree list` with a raw, confusing stderr string
   misclassified as a generic `PARTIAL` result rather than the
   structurally-expected, version-attributable failure it actually is.
3. **A genuinely contradictory closeout rule.** `CLAUDE.md` §5 required
   "any commit after the auditor's own pass that touches audited scope
   voids that pass" — but the same paragraph's own terminal step (a
   `roadmap-context-curator` reconciliation flipping `ROADMAP.md`'s row
   to `done`) necessarily lands after the audit and necessarily touches
   `ROADMAP.md`/`CONTEXT.md`, files the auditor's own checklist item 2
   explicitly checks. Every phase closeout to date, including this
   phase's own original one, had informally judged the curator's diff
   "narrow enough" by eye, with no written standard to judge it against.

### How each was fixed

1. A shared `_tri_state_label` helper renders all three states explicitly
   (`dirty`/`clean`/`unknown`, `matches pin`/`differs from pin`/
   `comparison unresolved`); four new regression tests exercise exactly
   the `None` cases the original suite never did; real rendered CLI
   output (not only pytest assertions) was inspected directly to confirm.
2. A single, narrow `git --version` check (`_detect_git_version`), run
   once after a real repository is confirmed and before either 2.7-gated
   command runs, short-circuits to an explicit, version-naming
   `UNAVAILABLE` for anything below 2.7; an unparseable version never
   blocks detection. `decisions/0064` supersedes `decisions/0063` point 8
   (append-only — `0063`'s own text is unedited, per `CLAUDE.md` §2's
   established convention, exercised previously at `decisions/0061`).
   Live-verified against a real disposable repository with a
   monkeypatched `git --version` output, not only via pytest.
3. `CLAUDE.md` §5 gained a narrow, explicitly-enumerated exemption
   covering only the terminal reconciliation commit's three legitimate
   targets (the phase row, the current-state section, the plan file's
   Status line) — the exact diff was presented to the user and approved
   before being written, per §0's own approval-gate requirement, since no
   agent may write `CLAUDE.md` and no exception exists for a
   lead-initiated fix either. `planning/agent-led-workflow.md` step 14
   and `.claude/agents/roadmap-context-curator.md` were both updated to
   operationalize the exemption (naming the exact three targets, and
   requiring the lead to read the curator's actual diff before treating a
   phase as done) rather than leaving it as an ad hoc judgment call.

### What worked

- **The user's own review caught all three defects that a fresh,
  independent `release-phase-auditor` pass had not** — a reminder that an
  audit verifying "does the plan's own stated behavior match the code"
  cannot catch a defect the plan itself never anticipated testing for
  (item 1), a factual claim the plan itself asserted confidently but
  never independently verified against primary sources (item 2), or a
  contradiction in the governing process document itself, which is
  outside any per-phase audit's own scope entirely (item 3).
- **Authoritative primary-source verification, not memory or inference,
  settled the Git-version question decisively.** Local
  `/usr/share/doc/git/RelNotes/2.7.0.txt` (this machine's own installed
  Git's bundled release notes) and GitHub's raw source at specific tags
  (`v2.4.0`/`v2.5.0` `builtin/rev-parse.c`) gave an unambiguous,
  independently-checkable answer rather than a plausible-sounding guess.
- **The append-only ADR-supersession convention (`decisions/0061`'s own
  precedent) resolved the "how do we correct an already-shipped ADR"
  question cleanly** — no ambiguity about whether to edit `0063` in
  place, because this project had already established the pattern once.
- **Splitting the corrective work into five small, single-purpose commits**
  (CLAUDE.md alone, CLI fix, Git-version fix, process operationalization,
  plan/changelog amendment) kept each change independently reviewable and
  matched `CLAUDE.md` §6's own "one logical change per commit" guidance
  even under corrective-pass pressure to move fast.

### What didn't work / process gap this surfaces

- **No existing DoD gate specifically checks "does every nullable field
  the renderer touches have a test exercising its `None` state."** This
  is a real, generalizable gap — any future phase with nullable
  provenance fields and a human-readable renderer is exposed to the same
  class of bug this phase's own test suite missed. Not filed as a new
  learning here (the corrective pass's own scope is Phase 76 specifically,
  per the user's explicit "no expansion" instruction) — worth a future
  phase's own consideration, not invented as a rule here.
- **No mechanical or process check previously existed for verifying a
  plan's own stated external-tool version-compatibility claim against
  the tool's actual authoritative history** — this phase's Git-2.5 claim
  went unverified against Git's own release notes for two full amendment
  rounds and the original implementation, only caught by an explicit,
  separate user-directed review. Also not expanded into a new rule here,
  per the same narrow-scope instruction — noted for awareness only.
- **`L-065`** (filed `candidate`, per explicit instruction to run the
  normal `knowledge-curator` triage rather than self-assign a promoted
  status) covers the third defect's own root-cause analysis in full.

### Corrective-pass commits

`feaaaa0` (CLAUDE.md §5 fix, alone, user-approved), `db33352` (CLI
rendering fix + 4 tests), `bb21122` (Git version floor fix +
`decisions/0064` + 2 tests + doc updates), `6d668db` (workflow/agent
operationalization + `L-065` filing), `a89920d` (plan-file corrective
amendment + CHANGELOG entry), `48a5fea` (interim `ROADMAP.md`/`CONTEXT.md`
reopening reconciliation).

### Closeout sequence for this corrective pass

Per the user's own explicit instruction: a fresh, independent
`docs-reconstructor` drift audit; `knowledge-curator` triage of `L-065`;
a fresh, independent `release-phase-auditor` completion audit (requiring
PASS or PASS WITH NON-BLOCKING OBSERVATIONS); and only then a final
`roadmap-context-curator` reconciliation, itself verified to satisfy
`CLAUDE.md` §5's own newly-fixed exemption, restoring Phase 76 to `done`.
