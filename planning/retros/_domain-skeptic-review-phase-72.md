# Domain-skeptic review — Phase 72 drift-audit staleness candidate

## Scope

Phase 72's own per-phase drift audit flagged seven `docs/domain/
concepts/*.md` pages (`evidence.md`, `claim.md`, `decision.md`,
`observation.md`, `derivation.md`, `provenance.md`,
`relationship-edge.md`) plus `docs/domain/open-questions.md` item 7 as a
possible staleness candidate: their citation of
`planning/v1-redefinition/roadmap.md:1061-1087` and its "Stage E's own
future Domain stage" framing, now that `decisions/0062` (Phase 72)
reorganises post-v1 work into Priority A-F rather than lettered stages.
Independently checked per this role's charter (`decisions/0060`,
`planning/phase-63d-domain-reconstruction.md` §4).

## What I checked

- Read `planning/v1-redefinition/roadmap.md:1030-1110` (the Stage E
  section) directly and confirmed it is byte-identical to its
  pre-Phase-72 content — Phase 72 did not edit it.
- Read `decisions/0062` in full (Decision, Alternatives, Consequences).
- Read `planning/ROADMAP.md`'s "Post-v1 priorities (A-F)" section.
- Read `planning/v1-redefinition/conditional-generalisation.md:1-45`,
  including its own dated 2026-09-27 (Phase 72) amendment note.
- Read `planning/pre-v1-disposition.md` §7 in full, including its own
  §2.1-§2.6 disposition table.
- Read each of the seven concept pages' full "Stage E" mentions and
  their own `## References` blocks (not just the lines the audit
  named).
- Read `docs/domain/open-questions.md` item 7 in full.
- Read the source knowledge records the "Stage E's own future Domain
  stage" language traces back to: `CL-EVID-003.yaml`, `CL-EVID-009.yaml`,
  `DE-EVID-009.yaml`.
- Ran `scripts/check_knowledge_base.py` after appending new records —
  no findings.

## Verdict: genuine staleness, same pattern as `EV-SKEP-003`/`EV-SKEP-004`

The citation *pointer* itself
(`planning/v1-redefinition/roadmap.md:1061-1087`) remains completely
accurate — that file is historical/frozen, Phase 72 did not touch it,
and the naming-collision paragraph it points to reads exactly as before.
What has gone stale is the *interpretive gloss* three places add on top
of that citation, asserting a **future resolution mechanism** that
`decisions/0062` now explicitly retires:

- `decisions/0062`'s own "Decision" section: "The old Stage E phase
  grouping (Phases 56-59...) is superseded as a phase group — its
  candidate designs (`conditional-generalisation.md` §2.1-2.4) are not
  discarded, they are re-homed under whichever Priority above actually
  needs them, decided when that Priority's own phase is planned."
- `conditional-generalisation.md` itself already carries its own dated
  2026-09-27 amendment confirming this in its own voice: "the old
  'Stage E' phase-group framing... that would have resolved it is
  superseded — post-v1 work is no longer organised into lettered
  stages at all."
- `pre-v1-disposition.md` §7's own table re-homes §2.4
  ("provenance/evidence" — exactly the candidate design that names the
  colliding `Evidence`/`Observation`/`Claim`/`Decision` graph-level
  entity kinds) specifically to **Priority B**, not an unspecified
  future stage.

GATE DD itself remains exactly as open as before — `decisions/0062`
states this explicitly ("GATE DD is not resolved by this decision").
The naming-collision fact is exactly as real and exactly as unresolved
as it was. This is a citation/framing break from an unrelated planning
restructure, not a domain-meaning change — the same shape as
`connector.md`'s staleness at Phase 66/71.

### Precisely which pages are affected

**Stale** (assert "Stage E's own future Domain stage," or an
equivalent live-gate name, as the resolution vehicle):

- `docs/domain/concepts/claim.md:41`
- `docs/domain/concepts/decision.md:38`
- `docs/domain/open-questions.md` item 7 (lines 74-80)
- `docs/domain/concepts/relationship-edge.md`'s "What this is NOT" item
  1 (names "a Stage C mechanical-detection decision or a Stage E
  graph-capability decision" as a currently-live gate pair)

**Not stale** — these four pages only use "Phase 57"/"Stage E" as a
historical label for where a candidate design originated or currently
lives, never as a claim about the future resolution mechanism, and
their substantive claims are all still true post-Phase-72:

- `docs/domain/concepts/evidence.md` (lines 100-106)
- `docs/domain/concepts/derivation.md` (lines 92-97)
- `docs/domain/concepts/provenance.md` (lines 95-102)
- `docs/domain/concepts/observation.md` (lines 42-45)

### A secondary finding: the audit's own framing overstated uniformity

Of the seven pages named, only three (`evidence.md`, `claim.md`,
`decision.md`) actually cite `roadmap.md:1061-1087` verbatim in their
own `## References` block. `provenance.md` cites the narrower
`:1081-1087`. `observation.md`, `derivation.md`, and
`relationship-edge.md` don't cite that line range in References at all
— they only discuss "Stage E" in body text. Worth noting for whoever
tunes the drift-audit's own pattern-matching, though it doesn't change
the substantive verdict.

### The staleness originates in a Claim record, not just corpus prose

`CL-EVID-009.yaml` (status `supported`) is the actual source of the
"Stage E's own future Domain stage" language — its own `statement`
field: "The roadmap itself already states the correct resolution path:
Stage E's own future Domain stage must either pick genuinely distinct
names or explicitly justify sharing the terms." `CL-EVID-003.yaml`
echoes the same framing. `claim.md`/`decision.md`/`open-questions.md`
inherit the stale phrase directly from this Claim. Revising it is
`context-researcher`'s own synthesis work (a Claim revision, with a new
Derivation explaining why), not a citation-list fix — out of this
role's write boundary.

## Resolved myself (no escalation — this is a researchable fact, not a
genuine ambiguity)

New records appended to `planning/knowledge/codecompass-domain/`:

- **`OBS-SKEP-007.yaml`** — the direct checks performed (listed above),
  with full raw results.
- **`EV-SKEP-006.yaml`** — the conclusion: genuine staleness, exactly
  which pages are and aren't affected, and the exact fix for each.

### Exact fix needed (for the lead / whoever holds `docs/domain/` write
access, and for `context-researcher` on the two Claim records)

1. **`CL-EVID-009.yaml` / `CL-EVID-003.yaml`** (`context-researcher`):
   revise "Stage E's own future Domain stage" to reflect
   `decisions/0062`/`pre-v1-disposition.md` §7 — e.g. "the candidate
   design's own future Domain stage, whichever Priority phase
   (`pre-v1-disposition.md` §7 currently re-homes this specifically to
   Priority B) eventually takes it up" — with a new Derivation
   documenting the revision, not a silent edit.
2. **`docs/domain/concepts/claim.md:41`**: replace "deferred to Stage
   E's own future Domain stage" with wording that doesn't name a
   retired phase-group, e.g. "deferred to whichever future Priority B
   phase takes up this candidate design's own Domain stage
   (`decisions/0062`; `pre-v1-disposition.md` §7's own disposition
   table)."
3. **`docs/domain/concepts/decision.md:38`**: same fix.
4. **`docs/domain/open-questions.md` item 7 (lines 74-80)**: same fix,
   replacing "explicitly deferred to Stage E's own future Domain stage
   in `planning/v1-redefinition/roadmap.md`'s own Stage E entry" with a
   version naming `decisions/0062` and `pre-v1-disposition.md` §7's
   Priority B re-homing instead, while still citing
   `roadmap.md:1061-1087` as the (unedited, still accurate) historical
   origin of the collision itself.
5. **`docs/domain/concepts/relationship-edge.md`**'s "What this is
   NOT" item 1: replace "a Stage C mechanical-detection decision or a
   Stage E graph-capability decision" with "a Stage C
   mechanical-detection decision or a future Priority A/B
   graph-capability decision (`decisions/0062` retires the old Stage E
   phase-group label; the same gated-ADR promotion mechanism
   `decisions/0051` describes still applies)."

No fix needed for `evidence.md`, `derivation.md`, `provenance.md`, or
`observation.md`.

## Escalations

None. This is a mechanical citation/framing correction traceable
directly to `decisions/0062`'s own text and `conditional-
generalisation.md`'s own Phase-72 amendment — not a genuine,
unresolved product/domain ambiguity. Nothing here required or received
a ruling from this role; the fix is named, not applied (write boundary,
`decisions/0060`).

## Write-boundary compliance

- No edits made to `docs/domain/`, `decisions/`, `planning/
  v1-redefinition/`, or any source/design content — read-only, as
  required.
- Two new records appended under `planning/knowledge/codecompass-domain/`
  (`OBS-SKEP-007.yaml`, `EV-SKEP-006.yaml`) — Observation/Evidence only,
  no Claim, Derivation, or Decision record written.
- `scripts/check_knowledge_base.py` run after appending — no findings.
