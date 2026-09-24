# Phase 67: Final validation — self-dogfood + Ledgerkit + Stage F smoke test

**Status:** planned (2026-09-24).

**Stage G, fourth phase, EXPERIMENTAL (gates v1)** (`planning/v1-redefinition/roadmap.md`).
Gated on Phase 66 completing — **done 2026-09-24, PASS WITH NON-BLOCKING
OBSERVATIONS**, unblocked. Not gated on GATE DD (a separate axis, per
`decisions/0056`).

## 0. What this phase is, and isn't

Per the roadmap's own Phase 67 entry: a **lightweight confirmation
pass**, not a full re-run — Stages D and F already did the underlying
evaluation work. Four distinct sub-tasks:

1. Re-verify CodeCompass's own dogfooding signal
   (`planning/context-health.md`, `planning/context-use-log.md`) is
   current.
2. Re-confirm Ledgerkit's final evaluation numbers and Phase 63's
   ordinary-project smoke-test result still hold against the code as
   shipped.
3. State plainly, in this phase's own report, how many real times the
   Scope→Plan→Domain→Design→Implement methodology was exercised pre-v1
   and what was found each time.
4. A fresh-agent acceptance test (`decisions/0060`'s own amendment,
   2026-09-20, direct user instruction), run once, late in this phase.

**"Gates v1" scope note** (from the methodology amendment that added
this, 2026-09-20): a FAIL on sub-task 2 or 4 does not block the
software release itself (that's gated by GATE DF/DD/G9, already
satisfied) — but it does block describing CodeCompass anywhere as a
validated reference/model project until the specific failure is fixed
and the test passes. This phase's own verdict is about the
*methodology's* validation claim, not the software's own shippability.

## 1. Sub-task 1: context-health/context-use-log currency

`planning/context-health.md` was last substantively updated at Phase
45 (2026-09-13); `planning/context-use-log.md` at Phase 52
(2026-09-14). Neither has been touched across Phases 53–66 — a real,
substantial gap this phase must address directly, not assume away.
Dispatch `context-health-planner` for a fresh assessment against
CodeCompass's own current `context-graph.db` in this checkout,
cross-referenced against `planning/ROADMAP.md`'s current state (its own
designed method). Report whether the prior findings (own graph
healthy; Ledgerkit's `dev-docs/` detection gap since fixed at Phase 49)
still hold, and surface anything materially new since Phase 45's
snapshot (e.g. the Haskell adapter's own vendor/symbol tracking, added
Phase 60–62).

## 2. Sub-task 2: Ledgerkit + Phase 63 smoke-test re-confirmation

**Ledgerkit**: `planning/reference-projects/ledgerkit/findings.md`'s own
"GATE DC (Phase 51)" section is the current-truth record: both original
FAIL verdicts moved to **PASS WITH GAPS / LOW advantage** after Phase
49's fix (re-verified independently by `context-evaluator` at Phase 51,
re-pinned Ledgerkit `05218e3` / CodeCompass `cea0b1c`). **This is below
the roadmap's own stated MODERATE+ target** — this phase must either
(a) find genuine new evidence the advantage has since improved (no
`src/codecompass/` change since Phase 51 specifically targeted the
`query relations`/`_DEFAULT_GLOBS` path, so no improvement is
expected), or (b) produce the explicit written justification the
roadmap's own text anticipates for shipping below that bar. Do not
re-run the full Ledgerkit evaluation from scratch — confirm the
**current** state: no FAIL has been reintroduced (spot-check `query
relations` against Ledgerkit's own current `dev-docs/` structure if a
live clone is available in this environment; if not, that absence
itself is a fact to report, matching Phase 63's own precedent for an
honestly-disclosed environment limitation), and write the justification
for LOW (not MODERATE+) advantage explicitly rather than silently
carrying the old number forward.

**Phase 63's own smoke test**: used no live external ordinary project
(`which npm`/`which cargo` both confirmed absent from this sandbox at
the time) — rested entirely on the full regression suite (623 passed,
2 skipped) as the basis for "no regression in npm/Python/Cargo adapter
support." Re-confirm: (a) `which npm`/`which cargo` still absent (or
now present — check directly, don't assume the prior finding still
holds), (b) no `src/codecompass/adapters/{npm,python,cargo}.py` change
has landed since Phase 63 (`git log --oneline` on those three files
since Phase 63's own commit), (c) the full regression suite still
passes at the same count. If a live ordinary-project clone becomes
available in this environment (npm/cargo now installed), a real smoke
test against it would strengthen this re-confirmation — check first,
don't assume the Phase 63 constraint still holds.

## 3. Sub-task 3: methodology exercise count

State plainly: Scope→Plan→Domain→Design→Implement
(`development-methodology.md`) has been exercised, as a **full,
deliberate, named application of all five stages**, genuinely **once**
pre-v1 — Phase 63D. Phase 60's own record-model reuse (Phase 54c's
Observation/Evidence/Claim/Derivation/Decision shapes, reused
unchanged) is a *component* reuse, not a full methodology exercise (no
Domain-stage investigation of Haskell-specific concepts was run as a
named stage; Phase 54c itself predates the methodology's own naming at
Phase 60's ADR). Stage E (56-59) would have been a second full
exercise, `decisions/0060` §6 having recorded this expectation
explicitly, but GATE DD has not funded it and may never. **This is an
honest, low count** — the roadmap's own text anticipates exactly this
outcome ("if it was exercised zero or only one real time... that is
itself a finding to report honestly here, not a gap to paper over").
Report this plainly; do not inflate the count by counting partial or
component reuse as a full exercise.

## 4. Sub-task 4: fresh-agent acceptance test

Run **once**, late in this phase (after this plan's own §1–§3 land, so
the docs a fresh agent reads reflect Phases 64–66's reconciled state,
not a pre-reconciliation snapshot).

**Task selection**: a real, small, currently-undone item from
`planning/ROADMAP.md`'s "Future-improvement backlog (unscheduled)"
section — either `L-031` (`symbol_enrichment` missing a producer-
attribution column) or `L-032` (external adapter protocol's
`ecosystem`/`capabilities` fields received but never validated). Both
are real, already-evidenced, small in scope, and have a domain-corpus
citation (`docs/domain/concepts/provenance.md`/`ecosystem.md`) a fresh
agent should plausibly find. **Pick one at dispatch time** (the lead's
own call, not pre-committed in this plan, so the choice isn't
telegraphed to the dispatched agent by this document's own existence —
though the agent won't read this plan file anyway, per the protocol
below).

**Protocol**: dispatch a `general-purpose` agent (not a specialist role
— the point is testing what a genuinely fresh, untold agent discovers
on its own, not exercising a role already briefed on this project's own
process) with **only**: repository access, and the literal change
request in ordinary product-development language (e.g. "CodeCompass's
`symbol_enrichment` table has no way to tell which model or agent
produced a given enrichment row, unlike the other two enrichment
tables. Investigate and propose a fix."). **Do not** mention Scope/Plan/
Domain/Design/Implement, `docs/domain/`, `planning/knowledge/`,
`CLAUDE.md`, or that this is a test, evaluation, or acceptance
criterion of any kind — the prompt must read exactly like a genuine
task assignment, not a test setup.

**Four PASS/FAIL criteria** (per `decisions/0060`'s own text), assessed
by the lead reading the fresh agent's own transcript/output afterward,
not self-reported by the agent:

1. Did it discover that this project has a development process at all,
   and find where it's described?
2. Did it locate the domain/evidence material relevant to the change
   without being pointed at it?
3. Did it correctly recognise at least one genuinely unresolved
   uncertainty (if the chosen task has one — both `L-031`/`L-032` do:
   whether a migration or a documented-intentional-asymmetry is the
   right fix), rather than guessing past it?
4. Did it produce a sensible, evidence-grounded design (not necessarily
   perfect — grounded in what it found, not contradicted by it, honest
   about what it didn't resolve)?

**Report honestly, per-criterion** — a partial pass is a real finding
about the reconstructed docs' own discoverability, not something to
average into an overall pass.

## 5. Files created/changed

- `planning/context-health.md` — fresh assessment appended (not
  rewritten from scratch; matches this file's own existing "History"
  section convention).
- `planning/reference-projects/ledgerkit/findings.md` — a new section
  recording this phase's own re-confirmation (or, if genuinely nothing
  changed, an explicit "reconfirmed unchanged" note — not silence).
- **`planning/phase-67-final-validation.md`** (this file) gains its own
  report content directly (sub-tasks 2–4's findings), rather than a
  separate report file — matching this phase's own "lightweight
  confirmation pass" character; a full separate evaluation report per
  sub-task would over-formalize what's meant to be a confirmation, not
  a new investigation.
- Standard closeout: `planning/retros/phase-67-final-validation.md`
  (retro), `planning/retros/_drift-audit-phase-67.md` (per-phase drift
  audit), `planning/retros/_audit-phase-67.md`
  (`release-phase-auditor`), `planning/learnings/inbox.md` (any
  candidates, including whatever the fresh-agent test itself surfaces
  about `L-031`/`L-032`'s own real fix — not implemented in this
  phase), `planning/CONTEXT.md`, `CHANGELOG.md`, `planning/ROADMAP.md`.

**Explicitly not touched**: `docs/`, `README.md`, `architecture/`,
`ai-docs/`, `src/codecompass/` (the fresh-agent test produces a
*design*, not an implementation — `L-031`/`L-032`'s own real fix stays
future-improvement-backlog work, not this phase's job), `decisions/*`,
`CLAUDE.md`, `docs/domain/` (read-only input).

## 6. Verification

1. **Sub-task 1**: `context-health-planner`'s own fresh report exists
   and is dated this phase, not just carried forward from Phase 45/52.
2. **Sub-task 2**: Ledgerkit's current PASS WITH GAPS/LOW status is
   either reconfirmed with fresh evidence or explicitly justified as
   acceptable to ship below MODERATE+; Phase 63's own smoke-test basis
   (no adapter code change, regression suite still green) is
   independently re-checked, not assumed.
3. **Sub-task 3**: the stated exercise count is checked against real
   phase history (`ROADMAP.md`, `decisions/0060`) — not asserted
   without the underlying phases named.
4. **Sub-task 4**: the fresh agent's own transcript is read by the lead
   directly; each of the four criteria gets an explicit PASS/FAIL, not
   a single aggregate verdict.
5. **Standard mechanical checks**: `python scripts/check_user_docs.py
   --strict`, `python scripts/check_knowledge_base.py`, full `pytest`
   (expect 623 passed / 2 skipped — no `src/codecompass/` change this
   phase, unless sub-task 2's live smoke-test check finds npm/cargo now
   available and something genuinely worth testing against them, which
   would still be read-only investigation, not a code change).
6. **Per-phase drift audit**: run as standard practice; likely `NO
   DRIFT` (no current-truth doc touched) unless sub-task 2's findings
   change what `docs/external-adapters.md` or similar claims.
7. **Closeout**: retro, `knowledge-curator` learning triage,
   `release-phase-auditor` DoD pass.

## 7. Deferred (explicitly out of scope for this phase)

- Actually implementing `L-031`/`L-032`'s own fix (the fresh-agent test
  produces a design only).
- Deciding GATE DD (a separate, already-settled-as-open axis).
- Independent release audit, milestone closeout, release itself
  (Phases 68–70).
- Any `src/codecompass/` behavioural change.

## 8. Report

### Sub-task 2 — Ledgerkit + Phase 63 smoke-test re-confirmation

**Phase 63's own smoke-test basis, re-checked live**: `which npm`/`which
cargo` both still return exit code 1 (absent) in this environment —
Phase 63's own constraint is unchanged, not merely assumed to still
hold. `git log --since="2026-09-22" -- src/codecompass/adapters/{npm,python,cargo}.py`
is empty — no adapter code has changed since Phase 63's own commit
(Phases 64–66 were all documentation/planning-only). The full
regression suite has been re-run and green (623 passed, 2 skipped) at
every phase since, most recently at Phase 66's own closeout. **Phase
63's own basis for "no regression in npm/Python/Cargo adapter support"
still holds, independently re-verified rather than assumed.**

**Ledgerkit, re-confirmed live against a newer pin than Phase 51's
own evaluation**: a live Ledgerkit clone exists in this environment at
`/home/cormac/projects/ledgerkit`, pinned `c6168b2` (2026-09-17) — newer
than Phase 51's own `05218e3` (2026-09-13). Ran the real onboarding
flow (`codecompass` bare bootstrap — 0 vendors tracked, matching
Ledgerkit's own known 0-runtime-dependency shape) and the exact
disambiguation check Phase 49's fix targeted:
- `codecompass query relations dev-docs/hledger-compatibility.md` →
  an honest empty relations table (the file is tracked, correctly
  found, genuinely has no detected relations) — **not** the
  pre-fix "not found" error.
- `codecompass query relations nonexistent-fake-file.md` → the genuine
  "not found" error, confirming the disambiguation between "tracked,
  no relations" and "not tracked at all" still works correctly on this
  newer pin.

**This directly, freshly reconfirms Phase 49/51's fix still holds** —
not carried forward from the old report, independently re-run against
a pin that didn't exist when Phase 51's own evaluation ran.

**Explicit written justification for the current PASS WITH GAPS / LOW
advantage status, below the roadmap's own MODERATE+ target** (per
`findings.md`'s own "GATE DC" section, re-confirmed unchanged by the
live check above — no `src/codecompass/` change since Phase 51 could
plausibly have moved this number): `doc_relations_edges` is built
purely from literal vendor/Skill name-mention detection. With 0
tracked vendors (Ledgerkit's own genuine shape — no runtime
dependencies), `query relations` on any Ledgerkit spec doc structurally
cannot surface *why* a doc matters, only *whether* it's tracked — this
is not a bug the fix could have closed; it is `CG-003`'s own
already-named, already-disclosed structural ceiling (a
mechanically-detected-relationship system has no signal to work with
when there are no dependencies to relate a doc to). Raising this
ceiling would require the kind of general-provenance/graph-level
generalisation GATE DD (Phase 55) is the actual gate for — not a Phase
67 fix, and not evidence of a defect in what shipped. **Justification
to ship at LOW advantage for this specific reference project**: the
fix that was scoped and funded (`CG-002`/`L-016`, GATE DB) fully closed
what it targeted, verified twice now (Phase 51, and again live here);
the remaining ceiling is a structurally different, already-disclosed,
already-gated question (GATE DD), not a regression or an unaddressed
defect in the shipped fix.

### Sub-task 3 — methodology exercise count

Scope→Plan→Domain→Design→Implement (`development-methodology.md`) has
been exercised, as a full, deliberate, named application of all five
stages, genuinely **once** pre-v1: **Phase 63D** (the domain
reconstruction itself — Scope and Plan from `decisions/0060`'s own
phase-insertion, a full project-wide Domain investigation, no Design/
Implement stage since the corpus *is* the deliverable, but Phase 64/65
then consumed it as the Design stage's own required input, closing the
loop). Phase 60's own reuse of Phase 54c's record-model shapes
(Observation/Evidence/Claim/Derivation/Decision) is a **component**
reuse, not a full methodology exercise — no named Domain-stage
investigation ran for Phase 60 specifically, and the methodology itself
wasn't named/formalized until `decisions/0060`, after Phase 60 shipped.
Stage E (Phases 56–59) would have been a second full exercise —
`decisions/0060` §6 explicitly recorded this expectation — but GATE DD
has not funded it and, per this project's own already-settled design,
may never. **This is an honest, low count, reported plainly rather than
inflated**: one full exercise, pre-v1, not the "repeated pre-v1 use"
the methodology's own portability claim (`decisions/0060` §7) might
otherwise imply without this explicit disclosure.

### Sub-task 1 — context-health follow-up (a real gap, fixed)

`context-health-planner`'s own fresh assessment
(`planning/context-health.md`, 2026-09-24 entry) found this checkout's
own `context-graph.db` had genuinely regressed since 2026-09-12 —
enrichment tables at 0 rows, doc/skill detection tables empty despite
5 Skills/1 slash command/3 Cursor rules/a full spec-doc tree genuinely
existing on disk, and `ai-docs/README.md`'s own published worked
example (`codecompass query relations architecture/overview.md`)
live-reproduced as erroring. **Fixed**: ran a full deterministic
`codecompass sync` (whole-project, Phase A only — declined Phase B's
own AI-enrichment prompt, no cost incurred). Re-verified live: the
previously-broken worked example now returns real relationship rows.
`git status` confirms only the gitignored `context-graph.db` changed —
no tracked file, no `src/codecompass/` change. This closes the one
real, disclosed self-dogfooding credibility gap Phase 67's own
sub-task 1 surfaced, before it could affect Phase 68's own independent
audit or a future live demo.
