# Phase 55b: Populate `doc_artifacts.name` for `spec_doc` rows

**Status:** done (2026-09-17). `CG-004` closed
(`promoted-to-roadmap`). Two-round independent `context-evaluator`
verification (round 1 FAIL — real production wiring gap; round 2 PASS
WITH NON-BLOCKING OBSERVATIONS, confirmed against the real live
Ledgerkit repository). `release-phase-auditor` → PASS WITH
NON-BLOCKING OBSERVATIONS (4 findings, all fixed before commit).
`docs-reconstructor` drift audit
(`planning/retros/_drift-audit-phase-55b.md`) → NO DRIFT, 1 non-blocking
finding, fixed. `pytest` 581 passed / 2 skipped, `ruff check .` clean,
`check_user_docs.py --strict` clean. Residual limitation filed as
`CG-006`. A process-lesson candidate learning (`L-021`) recommends a
`CLAUDE.md` §1 amendment — filed, not yet approved; presented separately
per §0. Retro: `planning/retros/phase-55b-spec-doc-name-population.md`.
This dedicated plan
file is written slightly after implementation began — the plan's full
content (objective, scope, non-goals, affected architecture, agent
roles, sequence, tests, evaluation, validation, DoD) was already
specified in `planning/phase-55-evidence-reconciliation.md`'s §G, which
the user reviewed and approved ("Approved") before any code was
written; this file formalizes it as its own numbered plan per `CLAUDE.md`
§1, rather than leaving the phase's plan only inline in the
reconciliation document. Noted honestly as a minor process deviation in
this phase's own retro, not smoothed over.

**Numbering:** "Phase 55b" — a bridge-style number (matching the
43d/43e precedent), not a retarget of Phase 55's own GATE DD slot and
not consuming any of Stage E's (56-59) or Stage F's (60-63) pre-written
sketch numbers, all of which already have different, unrelated content.
See `phase-55-evidence-reconciliation.md` §G's own numbering discussion
for the alternatives considered.

## Depends on

- `planning/phase-55-evidence-reconciliation.md` (the evidence package
  and gate recommendation this phase implements).
- `CG-004` (`planning/context-gaps/inbox.md`) — the gap this phase closes.

## Scope

**In scope:**

- `src/codecompass/spec_docs.py`: new `_extract_title(path) -> str | None`
  (first H1 heading text, filename stem fallback, never raises);
  `scan_spec_docs` populates `DocArtifactRow.name` from it for every
  `spec_doc` row.
- `src/codecompass/doc_mapping.py`: `build_doc_relations_edges` gains a
  self-mention exclusion for `mentions_artifact` (`artifact.path ==
  row.path` skip) — a real, previously-latent bug this phase's own
  integration test exposed live (a titled doc's own H1 line trivially
  contains its own name, so without this exclusion every titled
  `spec_doc` would generate a guaranteed self-mention noise edge).
- Unit tests for `_extract_title` (H1 present/absent/multiple/empty/
  unreadable) and `scan_spec_docs`'s name population.
- An integration test in `test_doc_mapping.py` proving two real
  `spec_doc` rows (via `scan_spec_docs`, not hand-built `DocArtifactRow`s)
  can now mechanically relate to each other, and a regression test for
  the self-mention exclusion.
- A real before/after check against the live Ledgerkit repository
  (read-only), using `CC-LK-001`'s own three test files.

**Explicitly out of scope** (per the reconciliation's own Non-goals):

- No new `relation_kind`.
- No new `doc_artifacts.origin` value (`CG-005` stays deferred).
- No pinned-external-reference productisation.
- No executable-evidence representation.
- No `vendor.toml` change.
- No `CLAUDE.md` change.
- No change to `build_doc_relations_edges`'s existing vendor-mention
  logic, chunk-attribution logic, or any other relation kind.

## Design decisions

- **First H1, not a frontmatter `title:` field or the filename alone.**
  Markdown spec docs in both CodeCompass's own repo and Ledgerkit's real
  repo consistently open with a level-1 heading that states the doc's
  actual subject (confirmed by direct inspection of both repos' real
  `dev-docs/`/`docs/`/`decisions/` trees before implementing, not
  assumed) — no repository inspected uses YAML frontmatter for spec
  docs the way Skills do.
- **Filename-stem fallback, not `name=None`.** A doc with no H1 still
  gets a real, path-derived string as its name, consistent with this
  project's "never leave a a exploitable gap, degrade to a safe
  default" posture elsewhere (`staleness._parse_version`,
  `skill_scan._extract_scalar`).
- **A specificity guard (`_is_specific_enough`) was added — reversing
  this section's own original position, corrected here rather than left
  silently stale.** The pre-implementation check described below (no
  *duplicate* H1 titles found in either real repo) was real but tested
  the wrong risk: it caught title *collisions* between docs, not a
  single bare, ubiquitous word (a project's own root `README.md` titled
  just `# ledgerkit`) matching *everywhere* other docs mention the
  project's own name in ordinary prose. This second, more severe failure
  mode was found only once the fix was actually wired into `sync.py`
  and re-run against the real, live Ledgerkit repository — 55
  hypothetical edges, 50 of them exactly this pattern (see the phase
  retro's "What didn't work"/"Lessons learnt" §2). `_is_specific_enough`
  (reject a single whitespace-word with no digit/hyphen) was added in
  response, empirically confirmed clean against both real repos'
  H1/stem sets afterward. Originally-written pre-implementation
  reasoning, preserved for the record rather than deleted: *"Empirically
  checked before implementing: every H1 title across CodeCompass's own
  tracked spec docs and Ledgerkit's real `dev-docs/`/`docs/` tree is
  already distinctive... no observed collision risk in either real
  repository this phase could test against."* That check was necessary
  but not sufficient — it answered "do titles collide with each other,"
  not "does a title recur inside unrelated prose everywhere," which is
  the risk that actually materialized.
- **The self-mention fix is not scope creep** — it was undiscoverable
  before this phase (no `_DOC_RELATION_SOURCE_KINDS` member ever had a
  `name` before), found live while writing this phase's own integration
  test, and is required for the primary fix to ship without a guaranteed
  regression (every titled spec doc would otherwise self-match).

## Files

**Note, added post-implementation for accuracy (`release-phase-auditor`
finding):** the two entries marked *(added during implementation)*
below were not in this section's original version and were not named
in `planning/phase-55-evidence-reconciliation.md` §G's own "Affected
architecture" list either — `sync.py`'s wiring fix and `doc_mapping.py`'s
substantive change (not just a docstring update) were both discovered
necessary only once implementation was underway, beyond what was
actually presented to the user for approval. This is disclosed here
rather than retroactively implied to have been anticipated.

- `src/codecompass/spec_docs.py` — `_extract_title`, `_is_specific_enough`,
  `_H1_RE`, wiring into `scan_spec_docs`.
- `src/codecompass/doc_mapping.py` — self-mention exclusion in
  `build_doc_relations_edges` (a real logic change, not just a docstring
  update as originally scoped).
- `src/codecompass/sync.py` *(added during implementation — not in the
  original scope above or in `phase-55-evidence-reconciliation.md` §G)*
  — `spec_doc_rows` added to `build_doc_relations_edges`'s target
  argument; the actual production wiring, without which the fix has no
  effect on the real running tool.
- `tests/test_spec_docs.py` — new tests for `_extract_title`/
  `_is_specific_enough`.
- `tests/test_doc_mapping.py` — 2 new tests (the real cross-doc match,
  the self-mention regression).
- `tests/test_sync.py` *(added during implementation)* — 2 new
  integration tests through the real `rebuild_project_graph` entry
  point: a genuine cross-spec-doc match, and the README-noise
  regression guard.
- `architecture/overview.md`, `docs/cli-reference.md` — reconciled by
  `docs-maintainer`.
- `planning/context-gaps/inbox.md` — `CG-004` closed; `CG-006` (a
  residual, distinct limitation) filed.
- `planning/context-observations/inbox.md` — `OBS-012` filed.
- `planning/learnings/inbox.md` — `L-021` filed (a process lesson about
  testing through a function's real production call site).
- `planning/retros/phase-55b-spec-doc-name-population.md` — this
  phase's retro.

## Verification

- `pytest tests/test_spec_docs.py tests/test_doc_mapping.py -v` — new
  tests pass, nothing existing regresses.
- Full suite (`pytest -q`) + `ruff check .` + `check_user_docs.py
  --strict` clean.
- Real before/after check against the live Ledgerkit repository
  (read-only, revert-after), using `CC-LK-001`'s own three test files —
  independently confirmed by `context-evaluator`, honest result reported
  whether positive, negative, or null (per this project's own "treat
  negative/inconclusive results as valid evidence" posture, restated
  explicitly in the governing evidence-reconciliation prompt).

## Done when

Standard `CLAUDE.md` §5 DoD + `context-evaluator`'s independent
before/after report exists + `CG-004` updated to reflect the fix +
retro answers whether the real-world before/after showed a material
change on the exact `CC-LK-001` files, honestly, including if it did
not.
