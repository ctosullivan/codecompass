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

## A known, accepted limit on verifiability (added 2026-10-09, cold-reader finding #7)

`knowledge/source-and-evidence-map.md` cites some Evidence/Observation
records against paths that are *not* in your own workspace (ADR files,
`architecture/`, internal planning documents) — this is intentional: the
underlying narrative/governance material those paths would otherwise
expose is deliberately excluded from what you can see, by design, not an
oversight. A Claim id is, on its own, sufficient grounding under this
project's own evidence model even when you cannot personally re-open the
file it ultimately traces to. This means a real, non-trivial share of
the knowledge layer's assertions cannot be independently spot-checked by
you — treat a `knowledge/` Claim's own `status` field (and whether it
cites workspace-visible evidence you *can* check) as your signal for how
much independent confidence to place in it, rather than expecting every
citation to be openable.

## On synthesising architecture/workflow material directly from source (cold-reader finding #2)

`knowledge/workflows-and-state-transitions.md` and the architecture-
relevant Claims are intentionally thin — the knowledge layer does not
attempt to pre-digest CodeCompass's own module structure or pipeline
shape for you. This is not an omission to work around quietly: expect to
build the architecture and workflow sections of your documentation
primarily by reading the allowlisted source directly (module layout,
call structure, the real CLI surface), using `knowledge/` only for the
conceptual vocabulary and invariants it does cover. Say so if you find
the source insufficient to confidently describe a given workflow end to
end, rather than presenting a partial read as complete.

## A directly-observable fact with no recorded "why" (cold-reader finding #6)

`pyproject.toml` declares `name = "codecompass-context"`, but the
importable package and CLI entry point are both `codecompass`. Nothing
in your evidence explains why these differ (e.g. a PyPI name collision).
You do not need to explain the history — document both names correctly
wherever each is the one a reader actually needs (the PyPI/install name
vs. the import/CLI name), rather than conflating them or guessing at a
reason you cannot verify.
