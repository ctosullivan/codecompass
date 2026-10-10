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

Triaged by `knowledge-curator` 2026-10-08 (`planning/learnings/inbox.md`):

- **L-091** (deny-list filesystem isolation needs a sibling-path-traversal
  escape test, not just the one path being hidden) — classification
  `scoped-rule`, **status: retained**. Real and evidenced, but its own
  promotion destination (an ADR for a *finalized, production* isolation
  mechanism) doesn't exist yet while the authoritative writer run stays
  `blocked`; already substantively preserved verbatim in
  `planning/phase-81b-mode-b-isolation-investigation.md`.
- **L-090** (a tool that `rmtree`s its own staging target never checks
  whether that target is already a git worktree — the real bug this
  phase hit was only worked around procedurally, never fixed in
  `scripts/prepare_cleanroom_branch.py` itself) — classification
  `invariant`, **status: promoted**. Landed: `cmd_build` now refuses
  (exit 1) rather than `rmtree`-ing an existing git-worktree staging
  target; `test_refuses_to_rmtree_an_existing_git_worktree` added and
  passing.
- **L-089** (the `git ls-files`-not-a-filesystem-walk fix landed, but no
  regression test exists that would actually catch a reversion to a raw
  walk) — classification `invariant`, **status: promoted**. Landed:
  `test_build_excludes_untracked_gitignored_files` added and passing
  (functionally equivalent to the curator's own scratch-repo sketch, run
  against this repository's own real tree instead). A project-wide/
  scoped-rule promotion was judged premature on a single instance
  (narrow, one maintainer-only script) — revisit if a second,
  independently-built export tool repeats the same mistake.

Also checked `planning/context-gaps/inbox.md` and
`planning/context-observations/inbox.md`: nothing from this phase's work
belongs in either queue — these are tooling/methodology bugs the
orchestrator itself found and fixed, not a context-graph/mechanical-
detection gap.

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

---

## Amendment 4 (2026-10-09/10) — the credential gap closed, the run completed

### Goal

Remove the one specific blocker the original implementation left: no AI
writer could run inside the verified Mode B boundary without either
weakening isolation (giving it broader session credentials) or lacking
model access entirely. Give the sandbox an *inference capability*
instead of a *credential*, and — contingent on that genuinely working —
complete the full redocumentation this phase was always meant to
produce, for both CodeCompass and `codecompass-template`.

### Delivered vs. planned

Everything the amendment's own plan (§26) committed to, delivered for
real: a model-inference broker (`scripts/cleanroom_broker.py`) proven,
by active test, to keep every credential outside the sandbox while
giving it real inference; a broker-specific isolation investigation
(including a context-contamination canary test) finding and fixing a
real defect (the broker's own inference subprocess inheriting its
launch directory) before reaching a clean verdict; 11 real cold-reader
passes against the actual handoff, with 10 rounds of genuine
reconciliation (not padding) — 6 of which were real bugs in the
clean-room tooling itself, not missing content; a preserved first
writer result; an independently-verified legacy-document gap review (6
candidates, 5 real, reconciled via a second isolated writer context,
never shown legacy prose); full documentation disposition execution
against the real, live CodeCompass repository (77 files changed) and a
lightweight pass against `codecompass-template` (9 files); the durable
workflow document, written only once the run had actually succeeded;
and a defect-class regression sweep confirming none of the twelve named
failure categories recurred undetected.

One piece of the plan's own closeout sequence did not go as planned:
the dispatched `knowledge-curator` subagent for learning triage failed
outright with a session-level rate limit. The lead performed that
triage directly instead, rather than leaving it undone or silently
skipping it.

### What worked

- The decision to test the broker against a disposable fixture *and*
  the real handoff, with a real canary test each time, caught a real
  defect (the launch-directory leak) before it could contaminate any
  real documentation output.
- Treating every cold-reader `GAPS FOUND` verdict as something to
  investigate against real primary evidence — never patched reflexively
  — caught multiple cases where the "obvious" fix would have been wrong
  (the symbol-indexing-states finding on pass 6 was a false positive on
  re-check; the `pyyaml`/`yaml` vendor.toml fix was reverted once the
  real, deeper `PythonAdapter` limitation was found, rather than landing
  a broken hand-edit).
- Separating "give the writer a fresh context" from "give the writer
  tool access" early — the broker's fixed, narrow
  `{system_prompt, messages} -> {output}` protocol, with evidence
  assembled up front rather than browsed interactively — avoided ever
  needing to solve the much harder problem of proxying a full agentic
  tool-use loop through the isolation boundary.
- Reading real current repository content in depth before treating a
  disposition plan's own prior classification as final — `CONTRIBUTING.md`
  turned out to be primarily a CLAUDE.md-mirroring governance document,
  not ordinary narrative documentation, and was correctly left
  untouched instead of being overwritten with thinner content.

### What didn't work

- The suffix-based file-extension allow-list in the original prompt
  assembler silently dropped real evidence for several cold-reader
  rounds before being caught — a second, independently-maintained list
  drifting out of sync with the real allow-list (L-096).
- The first hand-edit attempt at fixing the `vendor.toml`/`pyyaml` gap
  (adding an entry, then trying to regenerate its digest) surfaced a
  real, deeper, pre-existing adapter limitation mid-attempt and had to
  be reverted cleanly rather than landed half-finished.
- The learning-triage subagent dispatch failed on a session-level rate
  limit with no partial output — a real, external failure mode this
  phase's own closeout sequence had to route around rather than retry
  blindly.

### Lessons learnt

- A hard isolation gate (plan §26.5, extending §21) did its job a
  second time: the broker-specific verdict kept "isolation mechanism
  verified" and "authoritative writer run blocked" as separate
  findings even as the blocker was being removed, so the amendment's
  own eventual success is traceable to a real, demonstrated change
  (the broker), not a redefinition of what counts as success.
- An 11-round cold-reader cycle is not a sign the preparation work was
  bad — it is the mechanism doing exactly what it is for. The real
  value was concentrated in the rounds that found tooling bugs (which
  would have silently affected any future redoc run) rather than the
  rounds that found content gaps (which affect only this one run).
- "Verify every agent/tool report against primary evidence before
  acting on it" paid for itself concretely at least three times this
  phase (the symbol-indexing false positive, the `pyyaml` adapter
  limitation, and re-confirming the fork's legacy-gap findings against
  real source before reconciling any of them).

### Process-improvement feedback

- When a dispatched subagent fails with a rate-limit error rather than
  completing, the lead performing the same work directly — with a
  clear note in the resulting commit that this happened and why — kept
  the closeout sequence honest (no silently-skipped triage step) without
  blocking on a retry that might hit the same limit again immediately.

### Final status

The credential-provisioning blocker that kept Phase 81B `blocked` is
resolved; the authoritative redocumentation ran, succeeded, and was
applied to both repositories; the closeout sequence this far (defect-
class sweep, tests/lint, independent drift audit, learning triage, this
retro) is complete. Per `CLAUDE.md` §5, `planning/ROADMAP.md` is marked
`done` only after an independent `release-phase-auditor` pass confirms
every one of these conditions against the exact commit about to be
marked done — that pass is the next, final step, not yet run as of this
retro.
