# Phase 73 retro — `mentions_artifact` filename-based matching (closes `CG-006`)

- **Date:** 2026-09-27.
- **Commit(s):** `6861250` (plan + ROADMAP row), `0f3337d` (core fix:
  `build_doc_relations_edges` filename/stem matching), `29ced55`
  (follow-on fix: `relation_enrichment.py` excerpt-needle widening,
  found by `docs-maintainer`), `07c8475` (`CG-006` status flip),
  `38d577c` (drift audit report + `historical-notes.md` fix).
- **Agents used:** `docs-maintainer` (reconciliation), `docs-reconstructor`
  (per-phase drift audit).

## Where we are

First concrete implementation phase after Phase 72's roadmap
realignment — Priority A's first deliverable, per direct user
instruction to proceed with implementation.

## Goal

Close `CG-006`: extend `mentions_artifact` detection to also match a
target doc's filename/stem, not only its title, closing a real gap
found on the exact real-world pair `CG-004`'s own fix was motivated by.

## Scope delivered vs planned

Delivered as planned, with one real, necessary in-scope addition:
`docs-maintainer`'s own independent reconciliation pass found that
`relation_enrichment.py::_relation_needle` (excerpt-centering during AI
enrichment) was not updated for the same widening — a headerless source
doc citing a target only by filename would have silently fallen back to
a worse excerpt. Fixed in the same phase (renamed `_relation_needles`,
widened identically), not deferred — matching `L-055`'s own lesson
(check every consumer of a widened match, not just the primary
edge-creation path) applied here for the first time to a different
sub-system.

## What was achieved

`build_doc_relations_edges` now tries a named target's filename and
stem, gated through the reused `_is_specific_enough` noise filter,
alongside its existing title check — closing `CG-006` for real,
confirmed via both a unit test and a real integration test through
`rebuild_project_graph`. `relation_enrichment.py`'s excerpt-selection
now mirrors the same widened priority order. `CG-006` flipped to
`promoted-to-roadmap`.

## What worked

- **The independent `docs-maintainer` reconciliation pass caught a real
  completeness gap** the implementation itself missed — exactly the
  value this step exists for, and a second confirmation (after Phase
  72's own two-round rework) that a detection-side widening needs its
  consumers checked, not just its own tests.
- **`docs-reconstructor`'s drift audit caught a real, if minor, doc
  drift** (`historical-notes.md`'s closing paragraph understated the
  fix's own robustness after the follow-on fix landed) — the persisted-
  report discipline landed at Phase 72 (`L-056`) worked cleanly this
  time, no rework needed.

## What didn't work

Nothing beyond the two catches above, both the review process working
as intended.

## Lessons learnt

None new beyond what Phase 72 already generalised (`L-055`'s own
"check every consumer of a widened match" principle, now confirmed a
second time in a different sub-system). Left for `knowledge-curator`'s
own independent assessment of whether a second confirmation is itself
worth noting.

## Process-improvement feedback

None.

## Candidate learnings filed

None directly by the lead — left for `knowledge-curator`'s own
independent triage.

## Where we're going

Priority A's own harder candidates (`CG-001`, `CG-007` — task-oriented
retrieval edges, execution-path modelling) remain unplanned, genuinely
larger design questions not suited to this phase's "smallest justified
fix" shape.

## Time / cost note

Two agent dispatches (`docs-maintainer`, `docs-reconstructor`). One
`src/` behavioral change plus one same-phase follow-on fix.
