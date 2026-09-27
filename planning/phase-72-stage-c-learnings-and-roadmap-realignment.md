# Phase 72: Ledgerkit Stage C learnings capture + post-v1 roadmap realignment — plan

**Status:** done (2026-09-27).

**First post-v1 phase after Phase 71** (`planning/ROADMAP.md`'s "Post-v1
development" section) — not part of the redefined-v1 milestone group
(closed, `decisions/0048`, Phases 39-70). Direct user request,
2026-09-27: record the real learnings from Ledgerkit's own Stage C
(the query-language stage of Ledgerkit's own development, studied by
CodeCompass's Phases 54/54b/54c/61 — **not** to be confused with
CodeCompass's own redefined-v1 "Stage C," Phases 48-51, task-oriented
context retrieval; both names are real and both are used verbatim by
this project's own history, so this plan is explicit about which is
which every time it matters) as durable project knowledge, then realign
the post-v1 roadmap around the highest-value capabilities those
learnings demonstrate.

## 0. What this phase is, and isn't

**A synthesis-and-realignment phase: recording real evidence already in
this repository as durable, structured knowledge, and using it to
reorder the post-v1 roadmap — not a new research exercise, and not
implementation.** The 11 learnings the user's request names are not
novel to this phase; they are a distillation of evidence CodeCompass's
own Phases 54, 54b, 54c, 55, 60, 61, and the `context-gaps`/`learnings`
queues already produced during Ledgerkit's Stage C work. This phase's
job is to (a) make that distillation an explicit, citable, durable
record rather than leaving it scattered across a dozen phase files, and
(b) use it to decide what CodeCompass builds next, in what order —
reusing the project's own existing GATE DD decision procedure
(`planning/v1-redefinition/conditional-generalisation.md` §3) rather
than inventing a new prioritization mechanism.

**Explicitly not in scope**: implementing any new roadmap capability
(no `src/codecompass/` change is expected; if the closing consistency
pass finds a genuinely necessary one-line documentation-supporting fix,
it is called out explicitly, not silently bundled in). Not resolving
GATE DD's own graph-schema funding question in full — the evidence for
most individual `context-gaps` candidates (CG-001, CG-003, CG-006,
CG-007) has not independently crossed this project's own established
recurrence bar (`context-gaps/README.md`: "recurs, or is filed
independently by two agents") even though the qualitative Stage C
narrative is compelling; this phase says so honestly rather than
funding a schema generalisation on thinner evidence than the project's
own discipline requires elsewhere. Not writing an implementation-ready
`planning/phase-73-*.md` for whatever Priority A work comes next — that
is the next session's own job, per `CLAUDE.md` §1, once this
realignment is approved.

## 1. Scope

### 1.1 Durable learnings record (new)

`planning/ledgerkit-stage-c-learnings.md` — a new, dedicated document
(judged non-redundant: `findings.md` and the individual phase files are
raw evidence and per-phase narrative, not a distilled, principle-level
synthesis connecting evidence to roadmap priorities; nothing like this
currently exists). Structure: for each of the user's 11 numbered
learnings — a validated observation (citing the real phase/evidence
record that established it), the design principle it implies, any
capability already implemented vs. still proposed, and any genuinely
open hypothesis. Cross-references existing concepts
(`docs/domain/concepts/adapter.md`, `decisions/0051`, `decisions/0054`,
`decisions/0060`, `conditional-generalisation.md` §2) rather than
restating them.

### 1.2 New ADR — the prioritisation pivot

`decisions/0062-*.md` — records the shift in what post-v1 CodeCompass
optimises for (task-context completeness over graph completeness) as a
Decision, citing the learnings document as its evidence base, and
formally establishes the Priority A-F ordering. This is a
prioritisation/direction decision, not a schema-funding one — it does
not itself resolve GATE DD's own open graph-capability questions (§2.1/
2.3/2.4 of `conditional-generalisation.md`), which stay explicitly open
and are re-homed under the new priorities rather than the old Stage E
phase numbers.

### 1.3 Pre-v1 disposition record (new)

`planning/pre-v1-disposition.md` — a systematic pass over every
material pre-v1 roadmap item (all ~70 phases, `decisions/0048`'s
deferred list, the still-open `context-gaps` graph-capability
candidates, the two live future-improvement backlog entries) with an
explicit disposition: incorporated into the new roadmap / merged /
satisfied by existing implementation / backlog / retired-superseded,
with a one-line reason and a citation for each non-trivial one. Ordinary
shipped phases (the large majority) are dispositioned in bulk by
citation to `planning/v1-closeout.md` and `planning/v1-redefinition/roadmap.md`,
not repeated row-by-row — only phases whose old status was anything
other than a clean `done` (deferred, not-funded, retargeted, superseded,
skipped) get individual treatment.

### 1.4 `planning/ROADMAP.md` realignment

Replace the current "Deferred / not-funded" and "Future-improvement
backlog" sections (and extend "Post-v1 development") with the new
Priority A-F structure: each priority as a named track with its own
one-paragraph scope, success criteria, and current evidence pointer;
the still-relevant deferred items (Phase 24, 25, 50, the GATE DD
graph-capability candidates) re-homed under whichever priority they
actually inform, or left as an explicit low-priority backlog with its
own revisit trigger, not silently dropped. Names the first concrete
recommended next phase (Priority A, informed by Phase 48's own history)
without writing that phase's own plan file.

### 1.5 Consistency sweep (small)

`conditional-generalisation.md` gets a dated amendment note (its own
existing convention — see the 2026-09-12 and 2026-09-18 notes already
in that file) pointing at the new ADR and learnings doc, not a rewrite
of its content. `planning/CONTEXT.md` updated for the new state.
`CHANGELOG.md` entry. Anything else only if the sweep finds a genuine,
specific inconsistency (e.g. a stale pointer) — not a second rewrite of
already-fresh material.

## 2. Dispatch strategy

1. **Lead** drafts all four new/changed planning documents directly (a
   synthesis task requiring the full arc of this project's Ledgerkit
   evidence, not delegable, matching the precedent set for `README.md`
   at Phase 71).
2. **`context-health-planner`**, dispatched once: this realignment is a
   stage-boundary-shaped moment (`agent-led-workflow.md` step 4's own
   "any future boundary the roadmap's own stage grouping defines"
   language) — a forward-looking adequacy assessment for whatever
   Priority A work comes next.
3. **A fork**, independent consistency review: does the learnings
   document accurately cite real evidence (spot-check against the
   underlying phase files), does the ADR's Priority ordering follow
   from that evidence without overclaiming, does the disposition record
   miss any material pre-v1 item, does the ROADMAP.md rewrite disagree
   with anything in `v1-closeout.md`/`v1-redefinition/roadmap.md`.
4. **Lead**, informed by 3: fixes findings.
5. **`docs-reconstructor`** (MODE 1, per-phase drift audit).

## 3. Files created/changed

- `planning/ledgerkit-stage-c-learnings.md` — new.
- `decisions/0062-*.md` — new ADR.
- `planning/pre-v1-disposition.md` — new.
- `planning/ROADMAP.md` — Priority A-F realignment.
- `planning/v1-redefinition/conditional-generalisation.md` — dated
  amendment note only.
- `planning/CONTEXT.md`, `CHANGELOG.md` — closeout.
- `planning/context-health.md` — new entry from `context-health-planner`.
- Standard closeout: `planning/retros/phase-72-*.md`,
  `planning/retros/_drift-audit-phase-72.md`,
  `planning/learnings/inbox.md` (any candidates).

**Explicitly not touched**: `src/codecompass/` (no behaviour change
expected), `docs/domain/*` (frozen corpus; a task-context-completeness
concept page, if warranted, is a future Scope→Plan→Domain phase's own
job, not this one), `planning/learnings/*` existing entries, `README.md`
(no capability shipped this phase to describe), `CLAUDE.md`.

## 4. Verification

1. Every one of the user's 11 learnings is recorded in
   `ledgerkit-stage-c-learnings.md` with a real citation (a phase file,
   an `OBS-`/`CG-`/`L-` id, or a decision), not asserted from memory —
   spot-checked against the underlying file during the fork review.
2. No pre-v1 roadmap item disappears without an explicit disposition in
   `pre-v1-disposition.md` — checked by enumerating every
   `planning/phase-N-*.md` file and every `v1-closeout.md` §3 deferred
   item against the disposition record.
3. The new `ROADMAP.md` Priority A-F structure gives each priority a
   concrete, checkable success criterion — not merely a description.
4. GATE DD's own graph-capability questions are not silently declared
   "resolved" anywhere — the ADR and ROADMAP.md both state explicitly
   what remains open and why.
5. `scripts/check_user_docs.py --strict` and
   `scripts/check_knowledge_base.py` pass.
6. Full `pytest` unchanged (625 passed / 2 skipped expected — no
   `src/codecompass/` change).
7. The independent fork review's findings are addressed before
   closeout.
8. Per-phase drift audit: `NO DRIFT` expected (no current-truth product
   doc claims anything about this phase's own planning-document
   changes).
9. Closeout: retro, `knowledge-curator` learning triage,
   `release-phase-auditor` DoD pass (standard single-phase).

## 5. Deferred (explicitly out of scope for this phase)

- Actually resolving GATE DD's graph-schema funding question for
  CG-001/CG-003/CG-006/CG-007 (evidence not yet at this project's own
  recurrence bar for most of them — named as open in the ADR).
- Writing Priority A's own `planning/phase-N-*.md` implementation plan.
- Any `docs/domain/` concept work for "task-context completeness" as a
  first-class CodeCompass term.
- Any adapter/ecosystem-expansion work.
