# 0067. Phase 79's fifth amendment corrects `decisions/0066`'s own post-implementation defects via a new ADR, not an in-place edit

## Status

Accepted (2026-10-01, direct user instruction).

**Post-implementation note (2026-10-01): three further defects found in
the shipped fifth-amendment result are corrected by `decisions/0068`, a
new ADR, not a sixth in-place edit here** — by the exact same reasoning
this ADR's own Decision section gives for not editing `decisions/0066`:
this ADR has already informed real, executed, reconciled work, so its
own content below is left exactly as originally written.

## Context

`decisions/0066` was amended in place four times, all same-day or the
following day, all explicitly while Phase 79 was still pre-implementation
— its own Status line says so directly: "Not yet acted upon by any
implementation until this fourth revision's own approval, so each
amendment through the third revision is a pre-implementation correction,
not a reversal of shipped work," and names the fourth revision as "the
point past which the ADR's own content stops being purely
pre-implementation." That self-aware framing was deliberate: `CLAUDE.md`
§2's append-only rule for `decisions/` exists specifically because an
ADR that has already informed real, executed work is a historical record
of *why* that work was done the way it was — editing it in place after
the fact would quietly rewrite that history.

Phase 79 has since been fully implemented and flipped to `done` on
`planning/ROADMAP.md`. A direct review of the delivered result found
four real defects (detailed in the Phase 79 plan's own §0 "Fifth
revision" entry: snapshot validation that still didn't fail closed,
dropped documentation citations, a closeout report that conflated honest
best-effort labelling with strict isolation actually being achieved, and
a template usability "exercise" that was really only a link check). These
are genuine defects in already-shipped, already-`done` work — not a
pre-implementation planning correction the way the first four amendments
were.

## Decision

**Correct these four defects as a new ADR, `decisions/0067` (this
document), rather than a fifth in-place edit to `decisions/0066`.**
`decisions/0066` is left with its existing four-times-amended content
unedited, plus a short Status-line note pointing here — the same
"note the supersession, leave the original content alone" pattern this
project's own `decisions/TEMPLATE.md` already prescribes for a reversed
decision. This is not a reversal of `0066`'s own decision (the objective,
architecture, and mechanisms it establishes are unchanged and remain
correct) — it is a narrower corrective amendment to specific,
identified execution defects, filed as its own numbered record because
the work it corrects already shipped.

The four corrections themselves (full detail: the Phase 79 plan's own §0
"Fifth revision" entry, which this ADR defers to rather than duplicating):

1. `scripts/check_knowledge_base.py` gains `check_snapshot_completeness`
   — required-metadata/type validation, assertion-inventory completeness
   checked against the real historical directory listing at a snapshot's
   own freeze revision (never the live filesystem), record-identity
   checking, and Evidence/Derivation closure checking. Closes the
   specific gap named: a snapshot sidecar reduced to only its own
   `snapshot_id` previously produced zero findings.
2. `architecture/overview.md`/`architecture/context-graph-schema.md`
   regain their `first-party-source-symbols@v2#CL-FPSS-NNN` citations,
   lost during the legacy-reconciliation merge that originally published
   them.
3. The closeout's own "Track 2 (strict clean-room isolation validation):
   PASS" language — in both audit reports and in
   `planning/CONTEXT.md`/`planning/ROADMAP.md`'s own narrative — is
   corrected to **Track 2: UNMET**, backed by newly-recovered, genuinely
   mechanical boundary-check evidence (derived from the original pilot
   dispatches' own still-extant transcripts, not a rerun) rather than
   the single prose self-report the original closeout relied on.
4. A real downstream usability exercise (a fresh agent actually adopting
   and using the template against a small invented project) replaces the
   original fresh-clone link-check as the template's own usability
   validation, finding and fixing one genuine adoption-instruction defect
   in `codecompass-template`.

## Alternatives considered

- **Edit `decisions/0066` in place a fifth time.** Rejected: `0066` has
  already informed real, executed, `done`-flipped work; doing so would
  violate the same append-only principle its own fourth-revision Status
  line already flagged as the boundary not to cross, and would make the
  ADR's own history of "what was decided when, under what pre-
  implementation understanding" unreliable for a future reader.
- **Treat this as ordinary bug-fixing needing no ADR at all.** Rejected:
  the isolation-verdict conflation in particular is a non-obvious
  reporting/epistemics tradeoff (what honest labelling of an unenforced
  boundary does and doesn't establish) worth recording as a real decision
  for future phases to reuse, not just a corrected sentence.

## Consequences

Future sessions reading `decisions/0066` get its own, unmodified,
historically-accurate four-revision pre-implementation record. A session
needing the post-implementation corrections' own rationale reads this
ADR. The general pattern — a plan file can still amend itself directly
and implement without a planning round-trip even post-`done`, but its
*governing ADR* gets a new numbered record rather than an in-place edit
once real implementation has shipped under it — is available for reuse
by a future phase in the same situation, without needing to re-derive it
from `CLAUDE.md` §2's own more general wording each time.
