# Concept: the Knowledge Placement Policy

Phase 86. Formalises **where a piece of project knowledge belongs** —
eight categories, each mapped onto a real, already-existing artifact
this project owns. Introduces **no new record kind, no new storage
location, and no new write path**: every category below maps onto
something that already exists and is already owned by an existing role
(`CLAUDE.md` §8). Reproduced from `decisions/0085` §4 (the later,
"formalised" source), not re-derived — see `planning/phase-86-
knowledge-placement-code-quality-review.md` §5 for the full per-category
detail (authoritative source, ownership/change procedure, relationship
to every other category) this page summarises.

| # | Category | This project's artifact |
|---|---|---|
| 1 | Implementation logic | `src/codecompass/*.py` source itself |
| 2 | Interface documentation and docstrings | module/function docstrings |
| 3 | Non-obvious local comments | inline code comments — this project's own existing comment discipline (comment only when the WHY is non-obvious, never restate the WHAT) is the placement rule, not a new one |
| 4 | Architectural rationale and approved decisions | `decisions/*.md` (ADRs) |
| 5 | Behavioural requirements and invariants | `planning/knowledge/<slug>/*.yaml` Requirement records and `planning/contracts/<slug>/` oracle contracts |
| 6 | Verification evidence | `planning/contracts/<slug>/*.yaml` oracle-result files and `planning/knowledge/<slug>/` Evidence records |
| 7 | Human-oriented project documentation | `docs/**`, `README.md`, `ai-docs/**` (Phase 87's compiled output lands here) |
| 8 | Historical design context | `decisions/*.md` (append-only), `planning/retros/`, `architecture/historical-notes.md` where it exists |

**Not a single-location rule.** A critical invariant may legitimately
live in a comment, a contract, and human documentation simultaneously,
with one consistent meaning — this policy flags *inconsistency*
between locations, never mere repetition across them.

## The defining distinction: category 2/3 (current) vs. category 8 (historical)

This policy's own most characteristic defect, and the one this phase's
real dogfood (`planning/retros/phase-86-knowledge-placement-code-
quality-review.md`) demonstrates: a docstring or comment presenting a
**superseded** rationale as if it still justified the module's
**current** purpose — category 8 content masquerading as category 2.
Legitimately citing superseded context ("this used to work differently,
see `decisions/0019`, superseded by `decisions/0035`") is correctly
placed; the same citation presented as if it still justifies current
behaviour is misplaced.

## Three enforcement classes (`decisions/0085` §4)

- **Mechanical** — objective, deterministic, independently reproducible
  (e.g. a comment citing a `decisions/NNNN` number that does not exist).
  May block where policy explicitly requires.
- **Behavioural** — a violation demonstrated through an accepted
  executable contract or independently verifiable evidence (e.g. a
  docstring's claimed behaviour contradicted by a real, current oracle
  `FAIL`). Blocks only on real, live-reconfirmed evidence, never on
  assertion — a valid `INVALID`, stale, or missing result is a gap or
  uncertainty, never a demonstrated contradiction.
- **Semantic/editorial** — AI-assisted judgment of verbosity, abstraction
  quality, placement appropriateness, or architectural consistency.
  **Always advisory**, unless and until a specific instance is converted
  into an independently testable Requirement (category 5) — at which
  point it is enforced through the existing behavioural path, never
  through a reviewer gaining new authority on its own say.

**A prose contradiction with an accepted ADR is never classified
mechanically proven merely because an agent judges it contradictory** —
that judgment is semantic/editorial by construction unless a real,
citable mechanical check backs it.

## How this is enforced today

- `scripts/check_knowledge_placement.py` — two mechanical checks
  (`decision-citation-exists`, blocking; `decision-citation-superseded`,
  informational) plus an always-blocking parse-failure diagnostic. See
  the script's own module docstring for the exact extraction method and
  the real-corpus examples its design was verified against.
- `docs/workflows/knowledge-placement-review.md` — the ad-hoc
  semantic/editorial review, dispatched on demand, never a standing
  merge gate.

A third, originally-proposed mechanical check
(`decision-citation-status-mismatch`) and a proposed behavioural check
(`docstring-contradicted-by-oracle-result`) are both **deferred, not
shipped** — see the script's own module docstring and `planning/phase-
86-knowledge-placement-code-quality-review.md` §6.A/§7/§12/§13 for the
full rationale (in short: both would have required a semantic inference
this project's own Oracle/ADR conventions do not license mechanically).
