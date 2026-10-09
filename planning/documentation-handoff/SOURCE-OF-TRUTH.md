# Evidence hierarchy and conflict handling

## Hierarchy, highest authority first

1. **Current, allowlisted source code, tests, and configuration** in your
   own workspace — the ground truth for exact behaviour, flag names,
   defaults, error messages, and anything else directly observable by
   reading or running the code.
2. **`knowledge/` canonical Claims** — evidence-backed conceptual and
   architectural understanding, each traceable via
   `knowledge/source-and-evidence-map.md` back to the Evidence/Observation
   that originally grounded it. Treat an `UNCLASSIFIED`/no-`basis` Claim
   as an honestly-unverified factual hypothesis, not a confirmed fact —
   check it against source/tests where you can.
3. **`knowledge/decisions-and-rationale.md`** — what was decided and its
   current status, for the narrow cases where a documentation statement
   genuinely depends on project rationale rather than current behaviour.
   This is a title+status index, not full ADR text — treat a decision's
   own `status` field (approved/superseded/etc.) as authoritative for
   whether it's still in force; do not assume every listed decision is
   still current practice.

## When evidence conflicts

- Source/tests always win over a `knowledge/` Claim if they genuinely
  disagree — the Claim may be stale relative to a later code change.
- Two `knowledge/` Claims that explicitly disagree (check
  `contradicting_evidence` fields, and `OPEN-QUESTIONS.md`) should be
  presented as an open question in your own output, not silently
  resolved by picking one.
- If you cannot verify a claim against anything in your own workspace,
  say so explicitly rather than presenting it as confirmed.

## What "verified" means for your own output

Every important technical statement in your documentation must trace to
either (1) a specific file/line or command output you can point to in
your own workspace, or (2) a specific `knowledge/` Claim id. A statement
that traces to neither should not appear as settled fact.
