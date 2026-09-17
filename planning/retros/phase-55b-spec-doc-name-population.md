# Phase 55b retro — Populate `doc_artifacts.name` for `spec_doc` rows

- **Date:** 2026-09-17
- **Commit(s):** (this phase's own closeout commit)
- **Agents used:** `context-evaluator` (two independent rounds —
  round 1 FAIL, round 2 PASS WITH NON-BLOCKING OBSERVATIONS),
  `docs-maintainer` (architecture/CLI doc reconciliation),
  `docs-reconstructor` (drift audit →
  `planning/retros/_drift-audit-phase-55b.md`, **NO DRIFT — 1
  non-blocking finding**, fixed before commit), `knowledge-curator`
  (triage), `release-phase-auditor` (final pass, PASS WITH NON-BLOCKING
  OBSERVATIONS — 4 findings, all fixed before commit: two stale-plan
  corrections, one factual misstatement about the approved plan's own
  scope corrected in both this retro and
  `proposed-governance-changes.md` §D, and this drift-audit verdict
  itself recorded as its own artifact for the first time).

## Where we are

The one item `planning/phase-55-evidence-reconciliation.md` classified
**IMPLEMENT**: doubly-corroborated by CodeCompass's own Phase 54 (`CG-004`)
and Ledgerkit's independent, real-live-repo `CC-LK-001` finding. User
approved implementation with a non-binding preference for a bridge-style
phase number, hence "Phase 55b" (43d/43e precedent), leaving Stage E
(56-59)/Stage F (60-63)'s own pre-written sketches untouched.

## Goal

Close `CG-004` — populate `doc_artifacts.name` for `spec_doc` rows so
the existing, unmodified `mentions_artifact` relation-detection mechanism
can relate two of a project's own docs to each other — and validate the
fix with a real before/after comparison against the live Ledgerkit
repository, using the exact three files `CC-LK-001` already documented
as a real weakness.

## Scope delivered vs planned

Delivered, but only after a genuine, independently-caught process
failure mid-phase, honestly recorded here rather than smoothed over.

**Process deviation, disclosed up front:** the dedicated
`planning/phase-55b-spec-doc-name-population.md` plan file was written
*after* implementation had already started, not before — `CLAUDE.md` §1
requires the reverse. The phase's full plan content did already exist
and was already user-reviewed, inside `planning/phase-55-evidence-reconciliation.md`'s
§G, before any code was written — so the substance of "plan before
implementing" was honored, but the *form* (a dedicated, discoverable
`planning/phase-N-*.md` file) was not, until caught and fixed within
this same phase.

**A more consequential failure, caught by independent evaluation, not
by the lead:** the first implementation attempt shipped a change that
looked complete (population logic correct, unit tests passing, `CG-004`
apparently closed) but was never actually wired into the real, running
tool — `sync.py`'s own production call to `build_doc_relations_edges`
never included `spec_doc_rows` as a target, so the real gap this phase
existed to close still reproduced identically against the live
Ledgerkit repository. `context-evaluator`'s round-1 pass caught this by
doing exactly what independent evaluation exists to do: re-running the
real tool against real data rather than trusting the unit tests' own
pass/fail. The same pass additionally quantified a second, more severe
problem the naive fix for the first one would have caused: wiring
`spec_doc_rows` in naively would have produced ~55 false-positive edges
in the real Ledgerkit repository, 50 of them "every doc mentions
`README.md`" purely because README's own H1 is the bare project name.

## What was achieved

1. **`spec_docs.py::_extract_title`/`_is_specific_enough`** — populates
   `name` from a doc's first H1, or its filename stem, gated by a
   genericity check (reject a single bare word with no digit/hyphen)
   found necessary only after the live noise was quantified, not
   designed in speculatively.
2. **`doc_mapping.py`'s self-mention exclusion for `mentions_artifact`**
   — a second, previously-latent bug, discovered live while writing this
   phase's own first integration test: a titled doc's own H1 line
   trivially contains its own name, so without this exclusion every
   titled `spec_doc` would self-match, guaranteed.
3. **`sync.py`'s production wiring fix** — `spec_doc_rows` added to
   `build_doc_relations_edges`'s target argument, the actual missing
   piece round 1 caught.
4. **Real, independently-verified before/after evidence against the
   live Ledgerkit repository**: 3 genuine `mentions_artifact` edges now
   appear (a real `##` section cross-reference, a real subsystem
   relationship, a real roadmap-to-milestone citation), zero
   reintroduced README-style noise, confirmed by direct inspection of
   file contents, not asserted.
5. **A new, honestly-reported residual limitation**: the original three
   `CC-LK-001` files still show zero relations to each other, because
   they cross-reference each other by filename in prose, not by title
   text — a real, separate gap, filed as `CG-006`, not claimed to be
   fixed by this phase.

## What worked

- **Independent evaluation caught what unit tests alone could not.**
  Every new unit test in `test_spec_docs.py`/`test_doc_mapping.py`
  passed on the very first implementation attempt — and that attempt
  still didn't work in the real tool. Only a test that goes through the
  real production entry point (`rebuild_project_graph`, added to
  `test_sync.py` only after round 1's finding) would have caught the
  gap; this phase's own retro names this as the durable lesson, not
  just a one-off fix.
- **Quantifying the noise risk against real data, not reasoning about
  it in the abstract.** The plan's own risk section (in
  `phase-55-evidence-reconciliation.md`) predicted "graph noise" as a
  possible risk and said it was worth checking empirically — but the
  empirical check I did *before* implementing (scanning for duplicate
  H1 titles across two real repos) missed the actual failure mode
  entirely (bare single-word project-name titles matching *everywhere*,
  not colliding titles matching *each other*). Only testing against the
  real running tool, post-implementation, surfaced the real problem.
- **Not shipping the first "PASS"-looking result.** The unit-test-green,
  production-broken state would have been very easy to commit and call
  done. Dispatching independent evaluation specifically to check the
  real-world claim, not just the diff, is what caught it.

## What didn't work

- The plan-file-before-implementation ordering was violated (see above)
  — a real, if minor, process gap, not hidden.
- The pre-implementation noise-risk check (scanning for duplicate H1
  titles) was the wrong check for the risk that actually materialized —
  worth naming as its own lesson (see below), since a smarter
  pre-implementation check plausibly would have caught it before
  needing a second evaluation round at all.

## Lessons learnt

1. **A unit test that calls a function directly, bypassing its real
   production call site, cannot catch a wiring gap at that call site —
   no matter how thorough the unit test is.** This phase's first attempt
   had good, real, meaningful unit tests and was still non-functional in
   the shipped tool. The fix is procedural: any phase that adds a new
   capability to an existing multi-argument function must include at
   least one test that exercises the function's *real caller*, not only
   the function in isolation.
2. **A "will this cause noise?" check should test the actual failure
   shape (most commonly: a single ubiquitous entity's name recurring in
   unrelated prose), not a proxy for it (duplicate titles across
   documents).** These are different risks; checking one doesn't clear
   the other. The real check that would have caught this in advance:
   "for every candidate name, how many *other* real documents contain it
   as a literal substring?" — a frequency check, not a uniqueness check.
3. **Independent evaluation earns its cost precisely at moments like
   this one** — a lead confident the unit tests are green has no
   internal signal telling it to distrust that confidence; only a
   separate process re-deriving the real-world claim from scratch
   reliably catches this class of gap.

## Process-improvement feedback

Worth naming as a standing rule, not just a one-off retro note: **when a
phase adds behavior to an existing function that already has a real
production call site, the phase's own plan must name that call site
explicitly under "Affected architecture" and require at least one test
through it** — not left to the implementing agent's own judgment about
whether the unit tests "are enough."

**Correction, caught by `release-phase-auditor`, not by this retro's
own first draft:** this section originally claimed the approved plan
(`phase-55-evidence-reconciliation.md` §G) "did list `sync.py` under
'Affected architecture' but didn't explicitly require a test through
it." That is not what §G says. Re-checked directly: §G's "Affected
architecture" bullet names only `src/codecompass/spec_docs.py` and
explicitly states `doc_mapping.py` is "untouched" — `sync.py` is never
mentioned anywhere in §G. The user-approved plan was more under-scoped
than this retro first credited it with: both `doc_mapping.py`'s
substantive change (not just a docstring update) and the entirety of
`sync.py`'s wiring fix were discovered necessary *during*
implementation, beyond what was actually presented for approval — not
merely "named but under-tested." The actionable lesson stands (name the
real call site, test through it), but the honest account is "the
approved plan didn't anticipate needing `sync.py` at all," not "named it
but skipped a test."

## Candidate learnings filed

- `CG-006` — `mentions_artifact` matches by title text only, never by
  filename, filed `candidate`.
- `OBS-012` — one of Phase 55b's three real edges is a technically-correct
  but weakly-attributed title-prefix coincidence, filed `recorded`.
- (A process-lesson candidate — "a unit test bypassing a function's real
  call site can't catch a wiring gap there" — is named in this retro's
  own "Lessons learnt" §1/§Process-improvement above; `knowledge-curator`
  to judge whether it warrants its own `L-NNN` filing during this
  phase's triage, given it's a genuine, generalizable process lesson
  distinct from anything already on file.)

## Where we're going

- `CG-004` is closed (`promoted-to-roadmap`, fix landed this phase).
- `CG-006` (filename-based matching) is a small, precedented,
  independently-fundable follow-on — same shape and scale as `CG-004`
  itself — available whenever picked up, not urgent.
- `CG-005` (the `origin` enum extension) and the broader GATE DD
  ontology question remain exactly as open as `phase-55-evidence-reconciliation.md`
  left them — this phase did not touch either.
- Ledgerkit's own real, live, concurrent development (observed
  incidentally during this phase's real-repo validation runs — new
  `tag:`-family implementation files appeared mid-session, entirely
  independent of this work) is a reminder that the next real validation
  opportunity may arrive from Ledgerkit's own progress before CodeCompass
  goes looking for one.

## Time / cost note

Single session, continuing directly from the Phase 55 evidence
reconciliation (same day). No AI enrichment spend. Two
`context-evaluator` dispatches (round 1 FAIL, round 2 PASS WITH
NON-BLOCKING OBSERVATIONS) — the second directly caused by the first's
findings, not redundant process overhead. `pytest` 581 passed / 2
skipped (main suite; +14 net from the pre-phase 567 passed, across
`test_spec_docs.py`, `test_doc_mapping.py`, and two new `test_sync.py`
integration tests), `ruff check .` clean,
`check_user_docs.py --strict` clean throughout. Two real, read-only
validation runs against the live Ledgerkit repository, both fully
reverted afterward (confirmed via `git status` before and after).
