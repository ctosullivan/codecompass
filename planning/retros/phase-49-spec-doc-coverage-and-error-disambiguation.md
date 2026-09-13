# Phase 49 retro — `dev-docs/` spec-doc coverage + "not found" disambiguation

- **Date:** 2026-09-13
- **Commit(s):** `780e97b` (`fix(phase-49)`)
- **Agents used:** `docs-maintainer` (reconcile), `docs-reconstructor`
  (drift audit), `knowledge-curator` (finalize promotion),
  `release-phase-auditor` (final pass)

## Where we are

Stage C's first (and, per GATE DB, only currently-funded) phase. Stage B
(Phases 44–47) produced the evidence; this phase spends it. This is
**CodeCompass's first `src/codecompass/` change driven by external
reference-project evidence** — the redefined v1's central hypothesis
(`decisions/0048`) made concrete for the first time since Phase 43a's
own-repo dogfood.

## Goal

Close `CG-002` (add `"dev-docs/**/*.md"` to `_DEFAULT_GLOBS`) and `L-016`
(disambiguate `query relations`'s "not found" error from a genuine
coverage gap), per `planning/reference-projects/ledgerkit/findings.md`'s
ratified GATE DB recommendation. Live-verify the fix against the actual
Ledgerkit clone.

## Scope delivered vs planned

Delivered exactly as planned — a genuinely narrow, two-part fix, no
scope creep. One small self-correction: `_relations_not_found_error`'s
docstring initially cited `decisions/0051` (agent-suggested-context
graphing, unrelated) instead of the actual evidence trail (`CG-002`/
`L-016`, GATE DB Phase 47) — caught by the independent drift audit, fixed
before commit.

## What was achieved

1. `src/codecompass/spec_docs.py::_DEFAULT_GLOBS` gained
   `"dev-docs/**/*.md"` — the exact Phase 37 `ai-docs/` precedent applied
   a second time, this time from external evidence.
2. `src/codecompass/cli.py` gained `_relations_not_found_error`: a real
   on-disk file not detected as a doc artifact now gets an explicit,
   mechanism-naming message ("check whether it's covered by spec_docs's
   glob coverage") instead of an authoritative-sounding bare "not
   found." Scoped precisely to `query_relations` — `query vendor`/`query
   symbol`'s `_not_found_error` call sites are untouched, correctly,
   since "does this path exist on disk" isn't a meaningful question for
   a vendor/symbol name.
3. 3 new tests (`test_scan_spec_docs_finds_dev_docs_directory` including
   a nested-path case; two `query_relations` disambiguation tests).
4. **Live-verified against the real Ledgerkit clone**, not just unit
   tests: `dev-docs/hledger-compatibility.md` and a nested
   `dev-docs/planning/core-redefinition/07-query-regex.md` now correctly
   resolve to an honest empty "no relations" table (not "not found"); a
   genuinely nonexistent name still gets the plain message; a
   still-uncovered real file (`knowledge/DOMAIN_RULES.md`) correctly
   triggers the new disambiguated message — confirming the fix
   generalises beyond the one directory it was evidenced against.
5. `docs-maintainer` fixed two current-truth docs
   (`architecture/overview.md`'s glob enumeration, `docs/cli-reference.md`'s
   `query relations` error-behavior description), correctly following
   the Phase 37 precedent for what *not* to touch (illustrative "etc."
   lists elsewhere, left alone exactly as Phase 37 left them).

## What worked

- **A live smoke-test against the actual reference-project clone, not
  just synthetic unit-test fixtures** — this is what actually confirms
  the fix closes the evidenced gap, not just that the code behaves as
  intended in isolation. Testing against `knowledge/DOMAIN_RULES.md` (a
  directory *not* covered by the fix) was a cheap, valuable extra check
  that the disambiguation generalises rather than being
  coincidentally-`dev-docs/`-specific.
- **The independent drift audit caught a real, if minor, defect** (the
  mistaken ADR citation) that neither the lead nor `docs-maintainer`
  noticed — exactly the kind of thing an independent, from-scratch read
  is supposed to catch, and it did.
- **Keeping the fix exactly as narrow as GATE DB ratified** — no
  temptation to also touch `query vendor`/`query symbol`'s messages or
  build the rejected `vendor.toml`-configurable glob list "while we're in
  here."

## What didn't work

- Minor: the docstring citation slip above. Caught before commit, no
  real cost, but worth naming since it's a small instance of writing a
  citation from memory/pattern-matching ("this smells like a
  decisions/0051-shaped thing") rather than verifying it names the right
  ADR.

## Lessons learnt

1. **A code comment citing an ADR/gap/learning ID should be verified
   against that artifact's actual content before committing**, not
   assumed correct because the shape of the sentence matches a familiar
   pattern from other recent work.
2. **Testing a fix against a case slightly outside its evidenced scope
   (a different still-uncovered directory) is cheap and meaningfully
   strengthens confidence** that a fix is a real generalisation, not a
   coincidence that happens to work for the one case it was built from.

## Process-improvement feedback

None new this phase.

## Candidate learnings filed

None new. `CG-002` and `L-016` move from `promoted-to-roadmap`/`retained`
to fully `promoted` this phase (the code fix has now landed) —
documented as a status transition, not a new finding.

## Where we're going

- **Next: Phase 50 or Phase 51** — per the roadmap, Phase 51 (re-run
  Ledgerkit evaluation, GATE DC) is the natural next step to confirm the
  fix actually moves Phase 45/46's two FAIL verdicts, since Phase 50 was
  explicitly not funded by GATE DB. Re-check live before committing to
  either, per this project's now-standard practice.
- **Trajectory: confirmed.** The redefined-v1 loop (external evidence →
  gated decision → narrow fix → re-verification) completed one full
  cycle for the first time.

## Time / cost note

Single session, continuing directly from Phase 47 (same day). No AI
enrichment spend (mechanical-only `codecompass --budget 0` against the
Ledgerkit clone for the smoke test). `pytest` 557 passed / 2 skipped (+3
from 554), `ruff` clean, `check_user_docs.py --strict` clean.
