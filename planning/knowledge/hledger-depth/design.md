---
status: RESEARCHED
---

# hledger `depth:`/`--depth` behaviour — design document

**Retroactive record** (Phase 54c secondary proving case — tests
knowledge→documentation fidelity, not fresh research). This document is
generated from the records in this same directory, which were
reconstructed from Phase 54b's own already-completed, independently
verified work — not from a new investigation. See
`planning/phase-54c-evidence-knowledge-workflow.md` §7.

## Observed current/upstream behaviour

hledger's `depth:`/`--depth` query term does not behave uniformly across
commands (`CL-DEPTH-001`):

- **`balance`, `register`, `accounts`** — a display-only clip/aggregate
  operation. Postings/accounts deeper than the given depth are never
  excluded from the underlying computation; they are clipped to the
  depth limit for display, and where clipping produces duplicate names,
  aggregated (`balance`/`register`) or deduplicated (`accounts`)
  (`EV-DEPTH-001`).
- **`stats`** — a genuine, partial exclusion. Postings deeper than the
  limit are dropped from the journal `stats` reads its own
  posting-derived counts (e.g. "Accounts") from; whole transactions are
  never dropped, so "Txns" is unaffected (`EV-DEPTH-002`).
- **`print`** — no effect at all. Depth is stripped from the query
  before filtering and never consulted again (`EV-DEPTH-003`).

## Behavioural rules and precedence

The root mechanism (`DE-DEPTH-001`): every command that must not let
depth affect its underlying data strips the depth term from the query
used for selection, then re-derives depth separately, purely for
display. `stats` is the one command where the *unstripped* query reaches
a real exclusion-semantics filter (`filterJournalPostings`) — a
deliberate, source-documented divergence (`Ledger.hs`'s own doc
comment), not an inconsistency.

## Examples

```
Given a journal with assets:bank:checking:sub:deepest = $5
When running `hledger balance --depth 2`
Then the output includes one aggregated row whose total includes that
$5 — no row is silently dropped (EV-DEPTH-001, OBS-DEPTH-002).

Given the same journal
When running `hledger stats --depth 2`
Then "Txns" is unchanged but "Accounts" drops, because postings deeper
than 2 vanish from the count entirely (EV-DEPTH-002, OBS-DEPTH-004).

Given the same journal
When running `hledger print --depth 2`
Then output is byte-identical to `hledger print` with no depth term at
all (EV-DEPTH-003, OBS-DEPTH-005).
```

## Known uncertainties

None at `status: contradicted` — every Claim in this directory is
`supported`/`verified` with no retained contradicting evidence. This is
itself a notable (and honestly disclosed) property of reusing an
already-independently-verified source rather than fresh research: a
fresh Context Researcher run would be expected to pass through at least
one `contradicted`-status intermediate Claim before converging, the way
the real Stage C Phase 1 → Phase 5 history did.

## Proposed behaviour for the target project (Ledgerkit)

Not addressed by this retroactive record — Ledgerkit's own Stage C Phase
5 already independently implemented and shipped this exact behaviour
(`ledgerkit.query.depth.DepthSpec`) before this Phase 54c experiment
existed. This design document tests fidelity of projection, not
forward-looking design proposal, for this specific feature.

## Acceptance criteria

This document is graded, not written prospectively: does it correctly
and completely state the same three-way behavioural split
(`balance`/`register`/`accounts` clip; `stats` partially excludes;
`print` is inert) that Ledgerkit's real, shipped Stage C Phase 5 work
independently arrived at? See `planning/reference-projects/ledgerkit/findings.md`'s
"Phase 54b" section for the real, independently-verified outcome this
document is checked against.
