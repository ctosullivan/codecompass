# Phase 63 retro — lightweight ordinary-project smoke test

- **Date:** 2026-09-22
- **Commit(s):** this phase's own closeout commit, see `planning/CONTEXT.md`
- **Agents used:** none — a small, lead-only phase; no subagent dispatches during implementation (drift audit and DoD audit dispatched separately for closeout, per usual).

## Where we are

Stage F, its final phase — GATE DF. Phases 60–62 shipped the Haskell
adapter reference implementation (a new `EcosystemAdapter.symbols()`
default every in-process adapter now inherits, and `sync.py`'s own
`_collect_vendor_symbols` replaced by `adapter.symbols()` calls). Phase
63 is the one remaining question before Stage G (and the new Phase 63D,
`decisions/0060`) can proceed: did any of that disturb ordinary
npm/Python/Cargo project support?

## Goal

Per the roadmap's own framing: "a deliberately small confirmation — not
a full reference-project protocol run" — confirm no regression, state a
GATE DF verdict.

## Scope delivered vs planned

The plan's own original scope named Technical Clipper (reachable,
already-scouted, zero-runtime-dependency npm project) as the live
smoke-test target. **Amended before implementation** (direct user
instruction, once `which npm`/`which cargo` both confirmed absent from
this sandbox): the live clone was dropped entirely rather than run
partially. A live bootstrap that could only exercise
`NpmAdapter.installed_version()`/`source_location()`/
`readme_and_api_surface()` — never `dependency_tree()`, the one method
requiring a real `npm ls` subprocess call, and the one method closest to
what Phases 60–62's `sync.py` wiring changes could plausibly have
disturbed — was judged to add too little real signal over the existing
fixture suite to justify its own setup cost, for a phase whose own
roadmap entry explicitly permits skipping the live-project leg
("Technical Clipper... if convenient, not required... a different
ordinary project instead").

Delivered: the full regression suite as this phase's entire evidence
base, exactly as the amended plan scoped.

## What was achieved

- `pytest`: **623 passed, 2 skipped** — identical to Phase 62's own
  closeout baseline. No regression in npm/Python/Cargo adapter fixture
  coverage from anything Phases 60–62 changed.
- `ruff check .`: clean.
- `python scripts/check_user_docs.py --strict`: clean.
- **GATE DF verdict: PASS.** No regression found; nothing to fix or
  scope away with an ADR. Stage G (and Phase 63D specifically, gated on
  this phase per `decisions/0060`) is unblocked.

## What worked

- Checking the environment constraint directly (`which npm`, `which
  cargo`) before committing to a live-clone plan, rather than assuming
  the earlier Phase 62 audit finding still held — it did, but confirming
  it live rather than trusting memory is the same "verify independently,
  every time" discipline this project already applies elsewhere.
- Pausing to ask before executing, once the plan surfaced a genuinely
  open, roadmap-unsettled choice (live clone vs. regression-suite-only)
  — `CLAUDE.md` §1's own instruction, followed rather than defaulted
  past. The user's own answer ("skip the live clone entirely") matched
  the plan's own explicit recommendation once the partial-signal
  tradeoff was laid out, but the choice was genuinely the user's to
  make, not mine to assume.

## What didn't work

- Nothing found. The phase's own scope was small enough, and the
  environment constraint clear-cut enough, that there was no real
  friction once the live-clone question was resolved.

## Lessons learnt

- A live smoke test that can only exercise a fraction of an adapter's
  own methods is not automatically better evidence than an existing,
  already-passing fixture suite covering the same adapter more
  completely — "real" and "more informative" are not the same axis, and
  a partial live run risks being mistaken for fuller confirmation than
  it actually is. Worth stating explicitly rather than assuming "live
  beats fixture" by default.

## Process-improvement feedback

- None. `CLAUDE.md` §1's plan-then-ask-then-implement sequence worked
  exactly as intended for a small phase with one genuinely open
  question.

## Candidate learnings filed

- None — the lesson above is scoped narrowly to this one phase's own
  tradeoff (a partial live check vs. a fuller existing fixture suite)
  and doesn't generalise past "read what a partial live check would and
  wouldn't cover before assuming it's worth running," which is already
  this project's own standing evidence-first discipline, not a new rule.

## Where we're going

Stage G is unblocked. Phase 63D (Domain reconstruction, `decisions/0060`)
is next — its own plan (`planning/phase-63d-domain-reconstruction.md`,
already thrice-amended) is ready; it was explicitly gated on this
phase's own GATE DF passing, which it now has. Phase 64 (blank-slate
documentation reconstruction) follows once Phase 63D's own domain corpus
is approved.

## Time / cost note

No AI-API spend — this phase is pure `pytest`/`ruff`/`check_user_docs.py`
verification, no live external-project bootstrap, no new `src/` code.
