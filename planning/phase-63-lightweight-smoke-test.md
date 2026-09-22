# Phase 63: Lightweight ordinary-project smoke test — plan

**Status:** plan only, not started. Do not begin implementation until
this plan is reviewed (`CLAUDE.md` §1).

Gates Stage G (and, per `decisions/0060`, the new Phase 63D that now
precedes it) via **GATE DF**. Depends on Phase 62's own output (done,
`96428a8`+). Not gated on GATE DD.

## 0. Why this phase, and why now

Phases 60–62 changed real shared surface: a new `EcosystemAdapter`
external-process strategy, a new concrete `symbols()` default every
in-process adapter (npm/Python/Cargo) now inherits, and `sync.py`'s own
`_collect_vendor_symbols` removed and replaced by `adapter.symbols()`
calls. GATE DF's own question: did any of that disturb ordinary
npm/Python/Cargo project support? Per
`planning/v1-redefinition/roadmap.md`'s own Phase 63 entry: "a
deliberately small confirmation — not a full reference-project protocol
run."

## 1. Scope

**Amended before implementation (2026-09-22, direct user instruction,
Plan-stage re-entry per `development-methodology.md`'s own re-entry
rules — the chosen approach changed, the objective/GATE DF criterion
did not):** the live Technical Clipper clone is dropped entirely.
npm/cargo binaries are confirmed absent from this sandbox (`which npm`/
`which cargo` both fail live, matching Phase 62's own independent audit
finding), so a live bootstrap could only exercise a fraction of the npm
adapter's own real behaviour (`dependency_tree()` needs a real `npm ls`
call and would simply fail) — a partial live signal was judged not worth
its own setup cost when the full regression suite already covers the
same npm/Python/Cargo adapter logic at the fixture level, unchanged
since Phase 62's own 623-passed baseline.

**In scope:**

- Full `pytest`/`ruff check .`/`python scripts/check_user_docs.py --strict`
  re-run — this phase's own entire evidence base for GATE DF. Confirms
  the existing npm/Python/Cargo adapter fixture-test coverage (unchanged
  by Phases 60–62 beyond `EcosystemAdapter.symbols()`'s new inherited
  default, itself already covered by that phase's own tests) still
  passes exactly as it did at Phase 62's own closeout.
- **GATE DF verdict**, per the roadmap: fix only *general* problems
  supported by evidence. A genuine regression blocks Stage G (and
  Phase 63D specifically) until fixed or explicitly, narrowly scoped
  away with its own ADR — unchanged from the original GATE DF bar.

**Explicitly out of scope**:

- **No live clone of Technical Clipper or any other ordinary project**
  — dropped by the amendment above. The roadmap's own "if convenient,
  not required" framing for Technical Clipper, and its explicit
  allowance of "a different ordinary project instead," already
  anticipated that the live-clone leg might not be exercised every time
  this phase runs.
- No genuine Technical Clipper (or any reference project's) development
  task — that was the *original*, now-superseded Stage F content
  (`decisions/0056`), unaffected by this amendment either way.
- No formal `planning/reference-projects/*.md` registration record — moot
  once no live clone is used.
- No fix to Stage E, GATE DD, or anything Phases 55–59 already left
  open — unaffected, exactly as every phase since 60 has stated.

## 2. A real, disclosed environment constraint (the reason for the amendment above)

This sandbox has no live `npm` or `cargo` binary installed — confirmed
directly (`which npm` → not found, `which cargo` → not found), matching
Phase 62's own independent DoD audit finding. This is why the live
Technical Clipper leg was dropped rather than run partially: `NpmAdapter.
dependency_tree()` requires a real `npm ls ... --json` subprocess call
and would simply fail here, and a live check that can only exercise
`installed_version()`/`source_location()`/`readme_and_api_surface()`
(the parts that read `node_modules/<name>/package.json` directly, no
subprocess needed) was judged not to add enough real signal over the
existing fixture-test suite to justify its own setup cost, for a phase
whose own roadmap entry explicitly permits skipping the live-project
leg. The Cargo ecosystem was never going to get a live check regardless
— no Cargo-real-world project was ever named as this phase's target —
so its own fixture-test-only regression signal is unchanged from every
prior phase's own accepted position (`decisions/0014`).

## Design decisions

- **Drop the live clone rather than run it partially.** A live bootstrap
  that can only exercise three of `NpmAdapter`'s five methods (never
  `dependency_tree()`, the one method Phases 60–62 most directly risked
  disturbing via `sync.py`'s own wiring changes) risks *looking* like a
  real regression check while actually testing less than the existing
  fixture suite already does for the same adapter. Skipping it outright
  and saying so plainly is more honest than a partial run that could be
  mistaken for a fuller confirmation than it is.
- **The full regression suite is this phase's entire evidence base.**
  Proportionate to "deliberately small" and to the roadmap's own express
  permission to skip the live-project leg; GATE DF's own bar ("fix only
  general problems supported by evidence") is unaffected by which
  evidence source produced the finding.

## Files

- `planning/phase-63-lightweight-smoke-test.md` (this plan).
- `planning/retros/phase-63-lightweight-smoke-test.md` (new — records
  the regression-suite result and the GATE DF verdict).
- `planning/ROADMAP.md`, `planning/v1-redefinition/roadmap.md`,
  `planning/CONTEXT.md`, `CHANGELOG.md` (status flip to done).
- No `src/codecompass/` change expected — this phase confirms existing
  behaviour, it does not add anything. If a genuine regression is found,
  a fix would touch whichever of `src/codecompass/adapters/{npm,python,
  cargo}.py` or `sync.py` the evidence points at — not planned in
  advance, scoped narrowly to what's actually found.

## Verification

- Full `pytest` suite passes (matching Phase 62's own 623-passed
  baseline, ± legitimate skip-count changes); `ruff check .` clean;
  `check_user_docs.py --strict` clean.
- GATE DF verdict stated plainly in the retro: PASS (no regression
  found) or a named, evidenced regression with its own fix or scoping
  ADR.

## Done when

- The full regression suite ran for real, with the result recorded in
  the retro.
- GATE DF's verdict is stated and, if PASS, Stage G (and Phase 63D
  specifically) is unblocked to proceed.
- Standard DoD: retro exists; `planning/ROADMAP.md`/`CONTEXT.md`/
  `CHANGELOG.md` mark this phase done; `docs-reconstructor` drift audit
  (`NO DRIFT` expected — this phase changes no observable behaviour
  unless a regression fix lands) and `release-phase-auditor` pass —
  run as standard independent audits rather than a trivial-phase lead
  confirmation, since this phase's own verdict gates Stage G's entire
  progression.

## Review gate

Resolved before implementation (direct user instruction, 2026-09-22):
skip the live clone entirely and rely on the full regression suite as
GATE DF's evidence, per the amendment in §1. No further open review
items — the two remaining judgment calls the original plan flagged (no
formal reference-project registration file; the npm-only/`dependency_
tree()` constraint) are both moot once no live clone is used.
