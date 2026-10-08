# Phase 81B retro — clean-room project redocumentation from intermediary knowledge

- **Date:** 2026-10-08
- **Commit(s):** `c10f054`/`14878a4`/`17046e8` (planning + two amendments),
  `46601a1` (knowledge preparation — `documented_revision`), `547dd58`
  (handoff package, branch tooling, isolation investigation), `5f501a3`
  (git-tracked-files fix, template disposition report). Clean-room
  branch: `cleanroom/redoc-46601a1`, `handoff_commit` `468cffa4e013e56ad17df6c7536dd32a5774cd4b`
  (orphan branch, pushed to `origin`).
- **Agents used:** `docs-reconstructor` (drift audit), `knowledge-curator`
  (learning/context-gap triage), `release-phase-auditor` (completion
  audit).

## Where we are

Phase 81B operationalises Phase 79/80's clean-room methodology and
Phase 81's own intermediary-knowledge layer into a reproducible, whole-
project documentation reconstruction workflow for both CodeCompass and
`codecompass-template`. It is explicitly the named revisit trigger for
the standing "Strict mechanical isolation for documentation-
reconstruction stages" backlog item
(`planning/strict-isolation-for-documentation-reconstruction.md`), which
Phase 79/80 both left as honestly `UNMET`. The plan itself went through
three same-day amendments before implementation began (verified Mode B
made a hard prerequisite; no pre-existing narrative reaching the writer;
an explicit allowlist/manifest; cold-reader inside verified Mode B; and
further: per-file template classification, frozen `documented_revision`/
`handoff_commit` provenance, blocked-run doc-publication discipline,
historical-notes disposition) — each one recorded in place in the plan
file itself, not silently.

## Goal

Implement the thrice-amended plan: prepare and validate CodeCompass's
intermediary knowledge, build a manifest-validated clean-room branch
under an explicit allowlist, achieve and mechanically verify Mode B
isolation, and — only if that succeeds — run the cold-reader and a fresh
documentation writer inside it for both repositories, verify the result,
execute documentation disposition, and persist the proven workflow.

## Scope delivered vs planned

Everything up to and including the Mode B isolation investigation was
delivered in full, for real, against the real repository — not a
mechanism sketch. The isolation investigation itself produced a
genuinely new, actively-tested result. **The plan's own hard gate then
fired as designed**: no model-API credential is provisionable in this
environment for an AI writer, so the authoritative writer run, cold-
reader, result branches, informed verification, documentation deletion/
archival execution, link reconciliation, and the stored workflow
document were correctly **not** attempted — proceeding past the gate
would have violated the plan's own explicit Amendment 1 requirement.
`codecompass-template`'s own clean-room branch was also not built, as a
deliberate, recorded scope decision (the isolation mechanism is
repository-agnostic and the blocker is identical regardless of which
repository) rather than a silent omission.

## What was achieved

1. **Knowledge preparation** (`documented_revision` `46601a1`): 26 of 30
   previously-unclassified `codecompass-domain` Claims given a real,
   individually-read, evidence-grounded `assertion_kind` — the measured
   root cause of 88% of the rendered projection sitting in `overview.md`.
   4 left genuinely unclassified rather than forced. All five knowledge
   slugs rendered fresh, including three that had never been rendered at
   all. A new `check_no_pending_reconciliation` check
   (`scripts/check_knowledge_base.py`) closes the one gap
   `check_anchor_integrity` explicitly disclaimed in its own docstring.
2. **Explicit handoff selection** (plan §9.6): four of five knowledge
   slugs selected into the handoff, with the fifth (`hledger-depth`)
   excluded and the reason recorded, not silently included because it
   existed.
3. **The real handoff package** (`planning/documentation-handoff/`):
   built from real rendered canonical content, mechanically-generated
   decision/evidence indexes, and genuinely honest curated syntheses
   (thin where the underlying knowledge base has little to offer, not
   padded).
4. **A real, reusable branch-preparation tool**
   (`scripts/prepare_cleanroom_branch.py`) under an explicit, named
   allowlist, with a fail-closed validator proven against four real
   violation scenarios plus a real bug it caught and that was then fixed
   (a raw filesystem walk silently including untracked, `.gitignore`d
   local artifacts — switched to `git ls-files`).
5. **A real, pushed clean-room branch** (`cleanroom/redoc-46601a1`),
   confirmed via Mode A review (`git diff main..origin/cleanroom/redoc-46601a1`
   — note: double-dot, not triple-dot, since this is an orphan branch
   with no merge base with `main`) and via a genuine `git archive`
   extraction with zero `.git` directories anywhere.
6. **A rigorous, honest Mode B isolation investigation**
   (`planning/phase-81b-mode-b-isolation-investigation.md`): a namespace/
   `pivot_root`-based mechanism, actively tested against every named
   escape route (filesystem, parent-path traversal, `.git` history,
   branches, remotes, public network, filesystem and environment
   credentials, MCP/connectors, agent/project context), confirmed against
   both a disposable fixture and the real clean-room branch. A real
   credential leak (`CLAUDE_CODE_MESSAGING_TOKEN` inheriting via the
   environment) was found and fixed during the investigation itself. This
   is a materially stronger result than Phase 79/80's own `UNMET` finding.
7. **`codecompass-template`'s own documentation inventory/disposition
   report**, classified per-file (per Amendment 5) rather than per-
   directory, correctly distinguishing the seven structural `TEMPLATE.md`
   skeletons from the narrative prose living alongside them in the same
   directories.

## What worked

- Testing the isolation mechanism on a disposable fixture *before*
  touching real content caught a real design flaw (the deny-list
  approach's parent-path-traversal failure) cheaply, before it could have
  mattered against real data.
- Building the branch-manifest validator and testing it against real
  injected violations (not just a happy-path run) caught a genuine,
  otherwise-invisible bug (the `.gitignore`d-artifact leak) the very
  first time it ran against real repository content — exactly the value
  a validator is supposed to provide, demonstrated for real rather than
  merely claimed.
- The plan's own hard gate (Amendment 1) did its job: it stopped
  implementation from drifting into "run the writer anyway, label it
  best-effort" the moment the real credential-provisioning gap was
  found, which is precisely the discipline the amendment was written to
  enforce.

## What didn't work

- The first attempt at Mode B filesystem isolation (a deny-list — hiding
  specific sensitive paths with `tmpfs`) failed a real, active escape
  attempt (sibling checkouts under the same parent directory remained
  fully visible) — a design that looked reasonable on paper but needed a
  real test to disprove. Corrected to an allow-list (`pivot_root`) design
  before any real content was exposed to it.
- `git worktree add --orphan` followed immediately by the branch-
  preparation script's own `shutil.rmtree(staging)` destroyed the
  worktree's own `.git` link file on the first attempt, since the script
  didn't anticipate its own staging target already being a git worktree.
  Worked around by building in a plain scratch directory first and
  copying the validated result into the worktree afterward, rather than
  building directly inside a worktree.

## Lessons learnt

- A genuinely new isolation-mechanism finding (here: namespace/
  `pivot_root` achieves real, active-escape-resistant isolation for
  every route except model-API credential provisioning) can still leave
  the overall capability blocked — isolation and "a writer can actually
  run" are two different questions, and conflating them would have
  produced a false "verified" claim. Keeping them separate, as the plan's
  own four-way verdict structure requires, is what let this investigation
  report a precise, useful, honest result instead of a vague `UNMET`.
- Testing a validator against real, deliberately-injected violations
  (not just confirming it passes on a correct input) is what actually
  earns trust in a fail-closed mechanism — and it found a real bug the
  very first time it was tried this way.
- A tool's own staging-target assumptions (plain directory vs. a git
  worktree) matter and are worth testing explicitly before relying on
  them, especially for a destructive operation (`rmtree`).

## Process-improvement feedback

- None beyond what's already captured above — the amendment-review
  discipline (ten corrections made in place before implementation, each
  recorded) and the plan's own hard-gate structure both worked exactly as
  designed when the real investigation produced a result the original
  plan hadn't pre-committed to.

## Candidate learnings filed

To be determined by this phase's own `knowledge-curator` triage step —
recorded here once that step runs. Candidate observations for triage:
(1) deny-list filesystem isolation approaches should be tested against
sibling-path traversal specifically, not just the one path being hidden;
(2) a tool that builds into a directory should explicitly handle (or
refuse) the case where that directory is already a git worktree, rather
than blindly `rmtree`-ing it; (3) a clean-room/export tool's own file
inclusion must be sourced from `git ls-files`, never a raw filesystem
walk, to avoid silently including local untracked artifacts.

## Where we're going

Phase 81B remains `blocked`, not `done` — the authoritative writer run
cannot proceed without a separately-scoped model-API credential (or a
local/offline model) becoming available in this project's own working
environment. The strict-isolation backlog item is updated with this real,
substantive, partial result rather than closed. All preparation work
(knowledge enrichment, the handoff package, the branch-preparation
tooling, the pushed clean-room branch) remains genuine, reusable progress
for whenever that blocker is resolved — none of it needs to be redone.

## Time / cost note

One session. The bulk of the real engineering time went into the Mode B
isolation investigation itself (iterating from a failed deny-list design
to a working `pivot_root` allow-list, then debugging the `pivot_root`
mount-point requirement, then finding and fixing the environment-variable
credential leak, then finding and fixing the `git ls-files` bug) — this
is exactly the kind of cost this project's own backlog item anticipated
("not urgent... revisit when a genuinely separate execution substrate
becomes available") and it was worth spending here specifically because
the result (a real, substantive, reusable mechanism) is durable progress
even though the overall phase remains blocked.
