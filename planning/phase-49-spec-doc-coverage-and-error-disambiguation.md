# Phase 49: `dev-docs/` spec-doc coverage + "not found" disambiguation

**Status:** done (2026-09-13)

Stage C (CONDITIONAL on GATE DB — `planning/v1-redefinition/roadmap.md`).
**GATE DB ratified 2026-09-13** (`planning/reference-projects/ledgerkit/findings.md`
§7): fund one narrow phase closing `CG-002` and `L-016`. Phase 48 (the
roadmap's other Stage C sketch, task-oriented context retrieval) is
**not funded** — no corroborating evidence in the Phase 44–46 dataset
(`CG-001` is single-occurrence, own-dev only). This phase instead matches
the roadmap's own Phase 49 sketch exactly: "where a `planning/context-gaps/`
entry reaches `recurred` ... and is promoted here."

This is CodeCompass's **first `src/codecompass/` change driven by
external reference-project evidence** — the whole point of the redefined
v1 (`decisions/0048`).

## Depends on

- Phase 47 done: GATE DB resolved, findings recorded
  (`planning/reference-projects/ledgerkit/findings.md`).

## Scope

**In scope:**

1. **Close `CG-002`**: add `"dev-docs/**/*.md"` to
   `src/codecompass/spec_docs.py::_DEFAULT_GLOBS`, mirroring the Phase 37
   `"ai-docs/**/*.md"` precedent exactly (same module, same kind of fix,
   same evidence bar — a real project demonstrably wrong-footed by the
   fixed list). No other glob-list change; `findings.md` §4 explicitly
   rejects a `vendor.toml`-configurable glob list as premature at this
   evidence threshold (2 earned entries, not a pattern of many).
2. **Close `L-016`**: `query relations`'s not-found path
   (`src/codecompass/cli.py::query_relations` → `_resolve_relations`
   returning `None` → `_not_found_error`) currently gives the identical
   message whether `name` is a genuine typo/non-existent name or a real
   project file that simply wasn't scanned as a doc artifact. Disambiguate:
   if `name` resolves to an existing file under the project root that
   isn't a registered `doc_artifacts` row, say so explicitly (e.g. "exists
   on disk but wasn't detected as a spec/vendor doc — check
   `spec_docs`'s glob coverage") instead of the current bare "not found."
   A name that isn't a real path at all keeps the existing message
   unchanged. Scoped to `query_relations` only — `_not_found_error`'s
   other call sites (`query vendor`, `query symbol`) take a vendor/symbol
   name, not a path, so file-existence checking doesn't apply there and
   they are **not** touched.
3. New tests for both: a `dev-docs/**/*.md` detection test (mirroring
   `test_spec_docs.py`'s existing `ai-docs` regression test from Phase
   37) and a `query_relations` disambiguation test (a real on-disk file
   outside the glob set → the new message; a genuinely nonexistent name
   → the existing message, keeping `test_query_relations_unknown_name_errors`
   passing unchanged).
4. `docs-maintainer` reconciles any current-truth doc describing
   `_DEFAULT_GLOBS` or `query relations`'s error behaviour (check
   `docs/cli-reference.md`, `ai-docs/README.md` for anything now stale).

**Explicitly deferred / out of scope:**

- `CG-003` (external hledger.org manual) — Stage E/GATE DD territory,
  no glob fix could ever cover it (`findings.md` §5).
- `L-017` (WebFetch-as-fallback cost) — feeds Phase 53 directly, not a
  detection-improvement.
- `L-015` (optional-dependency CLI silence) — different code path
  (`discovery.py`), single occurrence, not bundled into this narrow fix
  (`findings.md` §4).
- Phase 48's original scope (task-oriented context retrieval) — not
  funded this gate.
- A `vendor.toml`-configurable spec-doc glob list — rejected as premature
  (`findings.md` §4); revisit only on a third distinct project/convention.
- Registering or touching Technical Clipper (Stage F).

## Design decisions

- **Smallest justified fix, not the more general one** — a single new
  glob entry, not configurability infrastructure. `conditional-
  generalisation.md`'s "smallest model that covers the demonstrated
  need" discipline applies to detection heuristics, not just to the
  technical-dependency/provenance model it was written for.
- **No ADR.** Same category as Phase 37's identical fix (no ADR either):
  a mechanical, narrow, evidence-driven detection-improvement, not an
  architectural decision or a new capability. The rationale is already
  fully documented in `CG-002`/`L-016`/`findings.md` — an ADR would
  duplicate, not add.
- **The disambiguation message must not become a second, competing
  source of truth about what's covered** — it should point at
  `spec_docs.py`'s glob list conceptually (e.g. "check spec-doc glob
  coverage"), not hard-code today's specific glob patterns into the
  error string, so it doesn't go stale the next time the list changes.

## Files

- `src/codecompass/spec_docs.py` — `_DEFAULT_GLOBS` gains one entry
- `src/codecompass/cli.py` — `query_relations`'s not-found branch
- `tests/test_spec_docs.py` — new `dev-docs` detection test
- `tests/test_cli.py` — new disambiguation test(s)
- `docs/cli-reference.md`, `ai-docs/README.md` — `docs-maintainer`, if
  either needs a fix
- `CHANGELOG.md`, `planning/ROADMAP.md`, `planning/CONTEXT.md` — curator
- `planning/reference-projects/ledgerkit/findings.md` — a short append
  once Phase 51 re-runs the evaluation (not this phase's job to append
  to; noted for continuity)

## Verification

- `pytest` — full suite passes, plus new tests for both fixes.
- `ruff check .` clean.
- `python scripts/check_user_docs.py --strict` clean.
- **Live re-check against the Ledgerkit clone** (the same scratch clone
  Phases 45–46 used, re-synced): `codecompass query relations
  dev-docs/hledger-compatibility.md` now returns real relations/results
  (or an honest "no relations," never "not found") instead of the FAIL
  this phase exists to fix. This is a confirming smoke test, not a
  re-run of the full evaluation — that's Phase 51's job.

## Done when

Standard DoD + verification + the live Ledgerkit re-check confirms the
fix + `release-phase-auditor` PASS + learnings/context-gaps
triaged (`CG-002` → `promoted-to-roadmap`, `L-016` → `promoted`).
