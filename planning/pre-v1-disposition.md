# Pre-v1 roadmap disposition

**Written Phase 72 (2026-09-27)**, per the user's own explicit
requirement that no pre-v1 roadmap commitment disappear without a
recorded disposition. Covers every phase numbered 0-70 (the foundation,
phases 0-38, plus the redefined-v1 effort, phases 39-70,
`decisions/0048`) and the still-open evidence queues
(`planning/context-gaps/`, `planning/learnings/`) that carried
unresolved candidates past Phase 70. Feeds `decisions/0062` and
`planning/ROADMAP.md`'s Priority A-F structure.

Five dispositions are used, per the user's own request:

- **Incorporated** — the item's substance now lives inside a named
  post-v1 priority.
- **Merged** — folded into a broader capability, no longer separately
  tracked.
- **Satisfied by existing implementation** — shipped, working, needs
  nothing further.
- **Backlog** — real, not funded, kept with its own revisit trigger.
- **Retired/superseded** — formally closed by a later decision; kept
  for history, acted on no further.

## 1. Phases 0-38 (the foundation) — satisfied by existing implementation

All 39 phases shipped and are load-bearing in the current product
(`architecture/overview.md`, `docs/`). No individual disposition
needed — none was deferred, retargeted, or superseded; the foundation
is simply what CodeCompass is. Full detail: git history (any commit
before Phase 39), `planning/v1-redefinition/roadmap.md`'s own framing of
"the foundation" as Stage A's starting point.

## 2. Phases 39-47, 49, 51-55, 55b, 60-70 — satisfied by existing implementation

The bulk of the redefined-v1 effort. Every one of these phases has a
real retro, a real commit, and (per `CLAUDE.md` §5) an independent
audit or drift check — traceable individually via
`planning/retros/phase-N-*.md` and `planning/v1-redefinition/roadmap.md`'s
own per-stage detail. `planning/v1-closeout.md` §2 ("What shipped") is
the canonical summary; not repeated here. No disposition beyond
"shipped, satisfied" applies to any of these — they are not backlog
candidates, and nothing about this phase's own realignment revisits
them.

**One historical retarget worth naming for traceability, already fully
resolved, no new action**: Phase 53's original slot (a Ledgerkit
Stage-C-adjacent follow-up) was retargeted on 2026-09-14 to legacy-
feature-rationalisation at direct user request
(`planning/v1-redefinition/roadmap.md`'s own Phase 53 amendment note);
the original follow-up work it would have covered is exactly what
Phases 54/54b/54c ran instead, under their own numbers. **Disposition:
retired/superseded** — its substance was absorbed by 54/54b/54c, not
lost.

## 3. Phase 24 — project-root-aware REPL routing + whole-project context

**Disposition: backlog, unchanged revisit trigger, lightly informed by
Priority A.** Deferred at `decisions/0048`; never had its own numbered
plan file, but real design content already exists —
`planning/phase-20-chat-project-root-routing-design.md` (relocated from
`architecture/overview.md` at Phase 65, "design content only... not yet
implemented") is the concrete design sketch for exactly this scope
(`codecompass chat` with no vendor argument, "project-root mode," plus a
related escalation idea) and is the right starting point if this item is
ever picked up. `planning/v1-closeout.md` §3's stated revisit trigger
stands: "reference-project evidence showing project-root context routing
is a recurring real need." Priority A's own task-context-completeness
work may incidentally touch session/routing concerns, but this item is
not folded into Priority A outright — its own trigger (a recurring
routing need, not a context-completeness need) is a different question,
unmet by the Stage C evidence this phase reviewed.

## 4. Phase 25 — MCP server (`query_vendor`)

**Disposition: backlog, unchanged.** Deferred at `decisions/0048`,
orthogonal to every learning in `planning/ledgerkit-stage-c-learnings.md`
(a transport/protocol concern, not a context-completeness one). Revisit
trigger unchanged: "real post-v1 CLI/Skill usage patterns informing
whether an MCP surface would add value" (`v1-closeout.md` §3).

## 5. Phase 48 — task-oriented context retrieval

**Disposition: incorporated into the new roadmap (Priority A).** Not
funded at GATE DB (Phase 47) for insufficient corroborating evidence at
the time (`CG-001` was single-occurrence, own-dev only).
`planning/ledgerkit-stage-c-learnings.md` learning #1 now provides a
materially broader evidentiary basis for the *category* of need (every
Ledgerkit instance's own LOW-advantage ceiling traces to exactly this
gap — "whether" a doc is tracked, never "why" it matters), even though
`CG-001` itself has still not independently crossed this project's own
formal recurrence bar. Priority A is this phase's real successor — not
a resumption of Phase 48's old scope unchanged, but a fresh scoping pass
against current evidence when it is next planned (`decisions/0062`).

## 6. Phase 50 — shared-agent context / entry-point improvements

**Disposition: partially incorporated (Priority A/D), remainder
backlog.** Not funded at GATE DB — no supporting finding existed at all
in the Phase 44-46 evidence base. Some of its original concern
(consistent context entry points across agents) now overlaps Priority
D's documentation-first-workflow productisation, but no Stage C evidence
directly names *this* item the way it names Phase 48's — kept as
backlog, revisit trigger unchanged ("new evidence emerging from post-v1
use," `v1-closeout.md` §3), rather than force-fit into a priority the
evidence doesn't actually support yet.

## 7. GATE DD / Stage E (Phases 56-59) — the generalised technical-dependency/provenance abstraction

**Disposition: superseded as a phase group; candidate designs
retained, re-homed under Priority A/B.** Never started — no plan file
for 56-59 was ever written; the gate itself (Phase 55, retargeted to
"evidence reconciliation") never ran the union-of-smallest-candidates
procedure `conditional-generalisation.md` §3 describes.
`decisions/0062` formally retires the "Stage E" phase-group framing
(post-v1 work is no longer organised into lettered stages at all,
`planning/ROADMAP.md`'s own Phase 71 restructure already established
this) without discarding the substantive candidate designs:

| Old candidate (`conditional-generalisation.md` §2) | New home |
|---|---|
| §2.1 `technical_dependency` generalisation | Priority A/B, if a future phase's own evidence justifies it — not pre-committed |
| §2.2 `executable` kind (execution/behavioural paths) | Priority A — directly names learning #2's own gap (`CG-007`, `L-026`) |
| §2.3 `reference_doc` kind | Priority A/C — informs task-context and gap-detection discovery of docs/manuals |
| §2.4 provenance/evidence | Priority B — directly the productisation this ADR names |
| §2.5 `browser_api`/`platform_api` kind | **Backlog, unchanged** — already explicitly deferred indefinitely at `decisions/0056` (Technical Clipper no longer required Stage F content); no Stage C evidence touches it |
| §2.6 task-oriented retrieval edges | Priority A — this *is* Phase 48/`CG-001`'s own hypothesis |

## 8. Stage F (Technical Clipper → Haskell adapter retarget)

**Disposition: retired/superseded, already fully resolved historically,
no new action.** `decisions/0056` retargeted Stage F from Technical
Clipper to a minimal Haskell adapter spike; Technical Clipper survives
only as an optional Phase 63 smoke-test candidate, never exercised live
in this environment (no external project available). Named here only
for traceability — nothing about this phase's own realignment reopens
it.

## 9. Open `context-gaps` graph-capability candidates — `CG-001`, `CG-003`, `CG-006`, `CG-007`

**Disposition: backlog, re-homed under Priority A/B per the table in
§7 above, evidence status unchanged.** None of these four has
independently crossed `context-gaps/README.md`'s own recurrence bar
("recurs, or is filed independently by two agents") — `decisions/0062`
is explicit that the qualitative Stage C narrative does not substitute
for that bar. They remain live, real, citable candidates
(`planning/context-gaps/inbox.md`), not silently dropped, and not
prematurely promoted either.

`CG-004`, `CG-005`, `CG-008` are **not** listed here — all three already
shipped (Phases 55b, 54c, 62 respectively) and are covered by §2's bulk
disposition.

## 10. Future-improvement backlog — `L-031`, `L-032`

**Disposition: backlog, unchanged status, now explicitly linked to
Priority B.** Both already tracked in `planning/ROADMAP.md`'s own
Future-improvement backlog table (unchanged by this phase). Learning #6
in `planning/ledgerkit-stage-c-learnings.md` names both as the two known,
concrete gaps in this project's own otherwise-well-executed provenance
discipline — cheap, already scoped, natural first hardening work inside
a future Priority B phase, not a new finding.

## 11. Superseded ADRs — traceability only, already resolved

Not roadmap phases, but named for completeness since the user asked
that nothing material be silently dropped: `decisions/0031` (`Depth`
retired), `decisions/0033` (`promote` retired), and `decisions/0061`
(`decisions/0019` formally recorded as superseded by `decisions/0035`)
are all already-closed, append-only historical supersessions with no
outstanding action. No new disposition needed.

## 12. Contradiction/provenance-model exercise gap — not a phase, named for completeness

Learning #5 (`planning/ledgerkit-stage-c-learnings.md`) is not a
pre-v1 roadmap item at all — it is a gap in how thoroughly an *existing*,
already-shipped mechanism (Phase 54c's Claim-model contradiction
handling) has been exercised. Named here only so it isn't lost between
"roadmap disposition" and "learnings record": it is **Priority B's own
first internal validation task**, not a backlog item with its own
revisit trigger.

## Summary — nothing material unaccounted for

Every phase 0-70, every item in `v1-closeout.md` §3's own deferred list,
every open `context-gaps` graph-capability candidate, and both live
future-improvement backlog entries has an explicit disposition above.
Table form, for the items that are not plain "shipped, satisfied":

| Item | Disposition |
|---|---|
| Phase 24 | Backlog, unchanged trigger |
| Phase 25 (MCP) | Backlog, unchanged trigger |
| Phase 48 | **Incorporated** — Priority A |
| Phase 50 | Partially incorporated (Priority A/D) + backlog remainder |
| GATE DD / Stage E (56-59) | **Superseded as a group** — designs re-homed, Priority A/B |
| Stage F retarget (Technical Clipper) | Retired/superseded, already resolved |
| Phase 53 retarget | Retired/superseded, already resolved |
| `CG-001`, `CG-003`, `CG-006`, `CG-007` | Backlog, re-homed Priority A/B |
| `L-031`, `L-032` | Backlog, unchanged, linked to Priority B |
| Contradiction-model exercise gap | Priority B's own first validation task |
