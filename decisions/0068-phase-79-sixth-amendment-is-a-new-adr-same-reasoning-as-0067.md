# 0068. Phase 79's sixth amendment is a new ADR, by the same reasoning `0067` established for the fifth

## Status

Accepted (2026-10-01, direct user instruction).

## Context

`decisions/0067` corrected four defects found by direct review of Phase
79's fourth-revision delivered result, and reasoned that those
corrections belonged in a new, numbered ADR rather than a fifth in-place
edit to `decisions/0066`, specifically because `0066` had "already
informed real, executed, `done`-flipped work" — editing it further would
quietly rewrite the historical record of what was decided under what
understanding, at the time.

`0067`'s own corrections have since been implemented, independently
re-audited (`planning/retros/_audit-phase-79-fifth-amendment.md` and its
re-confirmation addendum), and terminally reconciled
(`planning/ROADMAP.md`/`planning/CONTEXT.md` updated, commit `8911be1`).
A direct user review of that fifth-amendment result (verbatim prompt:
`planning/phase-79-sixth-amendment-prompt.md`) independently reproduced
and confirmed three further real defects, all requiring the same kind of
post-implementation correction `0067` itself was created to handle.

## Decision

**Correct these three defects as a new ADR, `decisions/0068` (this
document), rather than editing `decisions/0067` in place.** By the exact
same reasoning `0067` applied to `0066`: `0067` has itself already
informed real, executed, reconciled work, so it is left with its own
four-item Decision section unedited, plus a short Status-line note
pointing here.

The three corrections themselves (full detail: the Phase 79 plan's own
§0 "Sixth revision" entry, which this ADR defers to rather than
duplicating):

1. `check_snapshot_completeness`'s own Evidence/Derivation closure check
   (added by the fifth amendment) compared a real historical record's
   cited ids against the raw *keys* of a snapshot's nested
   `supporting_evidence`/`contradicting_evidence`/`derivation` tables —
   never checking whether each key's own *value* was a well-formed table
   or actually identified the record its key claims to. Two real attack
   shapes, independently reproduced before fixing: a nested table
   replaced by a scalar string (silently still counted as "captured");
   and an identity swap (a key kept, its own `path`/`content_hash`
   re-pointed at a *different* real record with that record's own
   genuinely correct hash — invisible to pure hash-integrity checking).
   A new `knowledge-base-snapshot-kind-mismatch` finding additionally
   catches a nested entry pointing at a record of the wrong `kind`.
2. The fifth amendment's own downstream usability-exercise evidence
   (`template-usability-exercise/tinytodo-after-adoption/`) asserted a
   false conceptual claim: that `tinytodo`'s `_next_id` guarantees a
   deleted task's id is "never reused." Independently reproduced and
   disproven: deleting whichever task currently holds the maximum live
   id causes the very next `add` to reuse that id, even with other,
   older tasks still present — a case the original exercise's own single
   test never exercised (it only ever deleted a non-maximum id).
   Corrected via dated notices in the affected assertion, documentation,
   and decision-record files, preserving each one's own original,
   incorrect conclusion as historical record underneath.
3. The fifth amendment's own template-usability exercise prohibited
   commits (leaving its snapshot structurally `UNCOMMITTED`) and
   inspected several downstream templates (assertions, snapshots,
   coding-context selection) rather than actually exercising them
   end to end with independent evaluation and demonstrated propagation.
   A fresh, complete, commit-permitting exercise was run in a disposable
   git repository, producing a fully-committed snapshot, a real
   model-blind implementation reconstruction, a real alignment
   comparison, real conceptual documentation, a real task-specific
   coding-context packet, independent assessment of both outputs, and a
   real (not asserted) propagation demonstration — a genuine source fix,
   mechanically shown to surface as evidence-staleness divergence against
   the frozen snapshot and to reach both derived outputs through that one
   shared foundation.

## Alternatives considered

- **Edit `decisions/0067` in place.** Rejected, for the identical reason
  `0067` itself gave for not editing `0066`: it has already informed
  real, executed, reconciled work.
- **Treat the first correction (nested-entry validation) as a
  continuation of the fifth amendment's own `check_snapshot_completeness`
  work, not a new decision.** Considered, but the fifth amendment's own
  closure already passed an independent re-audit and terminal
  reconciliation — reopening that closed record to insert new content
  would be exactly the kind of after-the-fact rewrite this project's
  append-only convention exists to prevent, even though the change is to
  code this same ADR lineage introduced.

## Consequences

The pattern `0067` established — a plan file may still amend itself
directly and implement without a fresh planning round-trip even
post-`done`, but its *governing ADR* gets a new numbered record once
real implementation has shipped and been reconciled under it — is
confirmed as a repeatable one, not a one-off: this is its second
application in the same phase's own lineage (`0066` → `0067` → `0068`).
A future phase in the same situation can cite this precedent directly
rather than re-deriving it from `CLAUDE.md` §2's more general wording.
