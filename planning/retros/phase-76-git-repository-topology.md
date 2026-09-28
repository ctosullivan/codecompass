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
