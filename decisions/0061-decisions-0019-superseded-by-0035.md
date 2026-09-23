# 0061. `decisions/0019` is superseded by `decisions/0035`

## Status

Accepted

## Context

Phase 65's own ADR status review (`planning/phase-65-architecture-adr-reconciliation.md`
§2.1) found a real governance gap: `decisions/0019` ("Grounded
description replaces gap analysis for `FULL`-depth generation") has, in
practice, been fully reversed by `decisions/0035` ("`sync_vendor` reads
enrichment from the graph; `grounded_description.py` retired") — the
module `0019`'s own Decision section introduces
(`grounded_description.py`, generating `FULL`-depth content at
`promote` time) is deleted, confirmed absent from `src/codecompass/`
entirely. Unlike every other reversal in this project's history
(`decisions/0031` superseding `0001`; `0032` superseding `0024`/`0025`;
`0033` superseding `0017`/`0018`; `0034` superseding `0012`), `0035`'s
own text never states that it supersedes `0019` — an oversight, not a
deliberate choice, since `0035`'s own Context section is explicit that
retiring `grounded_description.py` is exactly the mechanism `0019`
introduced. `0019`'s own Status field has stood as plain `Accepted`,
unmodified, since it was written — describing a mechanism that has not
existed since Phase 16.

This ADR does not reverse any decision itself — `0035` already made
the actual technical reversal, and shipped it (Phase 16). This ADR only
formally records the supersession relationship `0035` should have
stated at the time, per `CLAUDE.md` §2's own append-only convention:
`0019`'s and `0035`'s own original content are both left untouched.

## Decision

`decisions/0019` is superseded by `decisions/0035`. `0019`'s own
Decision section (grounded description generated at `promote` time,
gated on `Depth.FULL`) no longer describes CodeCompass's real behaviour
as of Phase 16 — `0035`'s own Decision section (enrichment read from
the context graph during `sync_vendor`, no `Depth` gate) is the current
mechanism. Neither `0019`'s nor `0035`'s own original text is edited.

## Alternatives considered

- **Edit `decisions/0035` directly to add the missing "supersedes 0019"
  line.** Rejected — `CLAUDE.md` §2 is explicit that a past ADR's
  original content is never edited, even to add a clarifying
  cross-reference after the fact; a new numbered ADR is the correct
  mechanism for exactly this situation.
- **Edit `decisions/0019`'s own Status field to `Superseded`.** Rejected
  for the same reason — this project's own established precedent
  (`0001`, `0012`, `0017`, `0018`, `0024`, `0025`) is that the superseded
  ADR's Status line stays exactly as originally written; the
  superseding ADR is what records the relationship, never the
  superseded one.

## Consequences

- `decisions/0019` should be read as historical only — describing a
  mechanism CodeCompass no longer has, superseded by `decisions/0035`.
- No `src/codecompass/` or documentation change — `0035`'s own Phase 16
  implementation already shipped the actual reversal; this ADR only
  closes the governance gap in how that reversal was recorded.
- Closes Phase 65's own ADR status review finding for `decisions/0019`
  — no other silent reversal was found among the 48 ADRs checked
  without existing supersession text
  (`planning/phase-65-architecture-adr-reconciliation.md` §2.1).
