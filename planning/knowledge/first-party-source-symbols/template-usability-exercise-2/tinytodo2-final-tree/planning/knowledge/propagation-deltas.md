# Propagation demonstration: source change reaching both documentation and the coding-context packet

Phase 79 sixth amendment, correction 3. Unlike the real CodeCompass
pilot's own disposable-fixture propagation demonstration, this one runs
against the exercise's own real, committed project — the source change
is a genuine fix, not a synthetic contradiction, and nothing here is
deleted afterward.

## The source change

`src/tinytodo.py`'s `_next_id` mechanism was replaced: from computing
`max(current task ids) + 1` (the behavior `id-reuse-001.md` documents as
buggy) to persisting a `next_id` high-water-mark counter in `todo.json`
itself (commit — see `git log -- src/tinytodo.py` in this project for
the exact SHA). Three new regression tests were added to
`tests/test_tinytodo.py` in the same change.

## Step 1: historical integrity — unaffected, as expected

Re-hashed every record the frozen snapshot (`id-reuse@v1.toml`) cites
against the exact historical git-blob content at its own recorded
`repository_revision` (never the live file):

```
[id-reuse-001] ...md@641daf64: hash matches recorded = True
  [supporting_evidence.src-next-id] src/tinytodo.py@b6a1bb5e: hash matches recorded = True
  [supporting_evidence.existing-tests] tests/test_tinytodo.py@b6a1bb5e: hash matches recorded = True
  [supporting_evidence.adversarial-review-evidence] ...md@1d2e6b87: hash matches recorded = True
```

All four pass. Nothing in the frozen snapshot's own historical record was
touched or corrupted by the source fix — exactly as it should be; the
fix is a legitimate current-state change, not tampering with history.

## Step 2: current divergence — the real signal

Compared each cited record's exact historical content against its
current, live file:

```
[id-reuse-001] planning/knowledge/assertions/id-reuse-001.md: current == historical? True
  [supporting_evidence.src-next-id] src/tinytodo.py: current == historical? False
  [supporting_evidence.existing-tests] tests/test_tinytodo.py: current == historical? False
  [supporting_evidence.adversarial-review-evidence] ...md: current == historical? True
```

**The assertion record itself (`id-reuse-001.md`) is unchanged** — its
own `status: contradicted` field is still literally accurate as a
historical fact (the code *used to* behave that way). **But the real
source evidence it cites has materially diverged**: `src/tinytodo.py`
and `tests/test_tinytodo.py` no longer match what the snapshot froze.

This is exactly the three-way distinction the real CodeCompass pilot's
own snapshot design draws, and this is a genuine instance of the
specific case it names separately from an ordinary Claim-status change:
**evidence/source staleness** — the Claim's own `status` field hasn't
moved, but what it's actually grounded in has, which is a stronger,
more specific trigger for re-derivation than "the record's own lifecycle
status changed." A check that only compared the assertion record's own
hash (ignoring its cited evidence) would have reported "no divergence at
all" here — technically true for the record's own text, but missing the
real, substantive fact that the code it describes no longer behaves that
way.

## Step 3: propagation to both derived outputs

Both derived outputs cite the same snapshot:

- `docs/id-reuse.md` cites `id-reuse@v1#id-reuse-001` throughout.
- `planning/knowledge/context-packet-fix-id-reuse.md` cites the same
  snapshot and assertion.

Since the snapshot's own cited evidence has diverged (Step 2), **both
derived outputs are flagged `needs reassessment`** by the same
mechanical signal, through the one shared foundation (the snapshot) —
not by two separate, redundant checks. This is the propagation this
exercise was asked to demonstrate: a single source change, reaching both
derived-output kinds, through the shared foundation, not by chasing each
one down independently.

Concretely, both documents are now stale in the same specific way: they
accurately describe what `_next_id` *used to* do (as of the frozen
snapshot), but no longer accurately describe what it *currently* does —
the bug they document has been fixed. Neither document is *wrong* about
history; both are now *incomplete* about the present.

## What this does not do (scope, stated explicitly)

This demonstration stops at "flagged, with the specific stale evidence
named" — it does not itself re-derive a new assertion documenting the
fix's own guarantee, freeze a v2 snapshot, or re-publish the
documentation/packet against it. That would be the natural next cycle
of this same workflow (research → review → freeze → publish, applied to
the *new* current behavior), not part of what was asked here: demonstrating
that the propagation signal itself fires correctly and reaches both
outputs through the shared foundation.

## Scope note

Unlike the real CodeCompass pilot (which has a committed `check_knowledge_base.py`
automating this exact check), the portable `codecompass-template` ships
no equivalent tool of its own — by design, per its own "What this
template deliberately does not include" section (no CodeCompass-specific
generated tooling). The checks above were run as a one-off Python script
against this exercise's own real git history, mechanically reproducing
the same logic `check_snapshot_historical_integrity`/
`check_snapshot_current_divergence` implement in the main CodeCompass
repository, to confirm the *template's own documented design*
(`docs/mechanical-isolation.md`, `snapshots/TEMPLATE.md`) actually holds
up against a real, non-trivial change — not because the template itself
runs such a check automatically.
