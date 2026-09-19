# Packet sufficiency log — `haskell-api-surface-extraction`

**Addendum (2026-09-19, before implementation began):** this log's own
single most important flagged gap — §11/the wire-protocol mapping for
REQ-HSAPI-002/003/005 never having been addressed by any record in this
knowledge base — is now resolved: `decisions/0059` extends
`codecompass-adaptor-protocol`'s `analyze_project-response.json` with
optional `kind` (`"export"`/`"reexport"`/`"undetermined"`) and `note`
fields on each `symbols` entry, and `src/codecompass/adapters/haskell.py`
was updated to render them. This addendum is added rather than rewriting
the predictive assessment below, per this project's own "retarget, don't
delete" convention — the original assessment correctly predicted this
gap before it was fixed, and remains accurate history.

Per `planning/phase-54c-evidence-knowledge-workflow.md` §6.1: every time
implementation needs something **not already in `context-packet.md`** to
make progress, this should be logged live, not reconstructed afterward.
Consulting a file/function the packet already *named* (its §7 pointer
list) is expected, normal use of the packet — not a gap.

**This log is written at packet-assembly time, before implementation has
happened** (`codecompass-adaptor-haskell` does not exist yet), so it is
necessarily a **predictive assessment**, not a live record of real
gaps encountered — a different exercise from
`doc-origin-pinned-reference/packet-sufficiency.md`, which was filled in
during real implementation. Per this project's own workflow document
(§6.1: "During implementation ... the coding agent ... keeps a running
log"), the authoritative version of this file is the one updated live
once `codecompass-adaptor-haskell`'s own implementation actually starts
— this pre-implementation assessment should be treated as a prediction
to check the real log against, not a substitute for it.

## Overall judgement

**Not sufficient on its own for a first-attempt, no-further-research
implementation of REQ-HSAPI-002/003/005 as specified.** The packet **is**
sufficient for REQ-HSAPI-001 and REQ-HSAPI-006 (the baseline scan and
the two-pass purpose-pairing algorithm): both are backed by
compiler-verified evidence, a concrete algorithm shape, and a named,
still-accessible real fixture file with exact line numbers a coding
agent can re-read directly. REQ-HSAPI-004 (exposed-modules filter) is
also implementable directly from the packet, modulo the ordinary
implementation-mechanism latitude any Requirement leaves open. The
scanning/detection **logic** for REQ-HSAPI-002, REQ-HSAPI-003, and
REQ-HSAPI-005 is likewise fully specified — a competent Haskell-capable
agent could write correct Haskell code that decides "this is a
re-export occurrence" / "this entry is CPP-gated" / "this module has no
export list." What is **not** specified anywhere in the knowledge base
is how that decision gets **represented on the wire** the adapter
actually speaks, and that gap would force a real implementer to stop
and either invent an unratified convention or go read
`protocol/codecompass-adaptor-protocol/` and `src/codecompass/adapters/
haskell.py` cold — exactly the "go back and re-read something the packet
should have settled" outcome this file exists to flag honestly.

## Gap 1 (predicted, high-confidence) — no wire-shape mapping for
REQ-HSAPI-002/003/005's richer output

**What would be needed:** to actually emit a conformant `analyze_project`
response, the adapter must decide *how* "this is a re-export occurrence
covering modules A, B" (REQ-HSAPI-002), "this entry is undetermined due
to CPP" (REQ-HSAPI-003), and "this module has zero enumerable symbols,
here is a diagnostic" (REQ-HSAPI-005) map onto a `symbols` array whose
schema is fixed at exactly `{name, purpose, module}` (all required,
`additionalProperties: false`) plus a `diagnostics` array of free-text
`{severity, message}`. No record in this knowledge base ever looked at
that schema.

**Why the packet doesn't (fully) have it:** this is not a one-off
omission in the packet-assembly step — it traces back further, to the
Context Researcher's own research scope (§3 of design.md), which
investigated Haskell-source behaviour exhaustively but never
cross-checked the target wire contract at all. The packet-assembly step
(this document) *did* discover the mismatch by reading the schema
directly (not named in any OBS/EV/CL/DE/DEC/REQ record) and has
disclosed it in `context-packet.md` §11 with candidate resolutions,
which is the most a compaction step can honestly do without making the
call itself (per this agent's own "mechanical compaction, not fresh
judgement" boundary) — but disclosure is not the same as resolution. A
real implementer will still need to either get this ratified as a new
Decision (extending `DEC-HSAPI-001` or adding a new one) or make a
unilateral implementation choice that the packet cannot pre-empt for
them.

**Classification:** **structural knowledge-base gap**, not a packet-
assembly oversight — the Context Researcher's own brief (§3 of the
governing workflow doc) doesn't currently instruct tracing the *target
wire protocol*, only "every real implementation path that could
plausibly explain the observed behaviour" on the *source* side. Worth
naming in a future retro: when a feature's Requirements describe an
adapter's *output*, the research phase should trace the actual
serialization contract that output must satisfy, not only the
input-side domain logic.

## Gap 2 (predicted, medium-confidence) — tokenising algorithm's exact
implementation shape

**What would be needed:** `CL-HSAPI-001` confirms the *scope* of a
"comment-stripping, identifier-tokenising scan" is sufficient (verified
against real GHC `:browse` output), but the verification itself used a
scratch **Python** regex script, not a Haskell implementation, and no
record specifies whether the real Haskell scanner should use a regex
library, a hand-rolled character-by-character scan, or an existing
lightweight Haskell tokenising library. This is flagged honestly in
`context-packet.md` §11, and per the packet's own reasoning, it is a
low-risk gap: the *test* (does the scan reproduce `:browse`'s name set)
is unambiguous regardless of implementation approach, so a competent
Haskell implementer can make this call without going back to any
research record — it would only become a real blocking gap if the
implementer needed to know something about GHC/Haskell-ecosystem
tokenising conventions the packet doesn't cover, which nothing in this
knowledge base suggests.

**Classification:** minor, self-resolvable at implementation time —
included here for completeness per this file's own "honestly disclosed,
not smoothed over" standard, not because it is expected to actually
block anyone.

## Gap 3 (predicted, low-confidence) — no test fixtures materialized yet

**What would be needed:** every concrete example in `context-packet.md`
§4/§7 points at the **live, pinned hledger checkout**
(`/home/cormac/projects/hledger/`), not at fixture files inside
`codecompass-adaptor-haskell`'s own eventual test tree. An implementer
will need to decide whether to read the pinned checkout directly in
tests (coupling test correctness to that external checkout's continued
availability at the pinned commit) or vendor small excerpts as
fixtures — this decision is unresolved in the knowledge base and not
attempted here, since it is properly an implementation-time choice
(mirroring `doc-origin-pinned-reference/design.md`'s own precedent of
leaving such choices to implementation) rather than a research-derived
fact.

**Classification:** expected, ordinary implementation latitude — not
treated as insufficiency, listed for completeness.

## What this predicts for the real, live sufficiency log

Once `codecompass-adaptor-haskell` implementation actually begins, this
file should be **updated** (not replaced) with a real, live log entry
recording whether Gap 1 was in fact hit, what resolution was actually
chosen, and whether Gaps 2/3 turned out to matter in practice — per this
project's own "the log is the retro's own primary evidence" standard
(`planning/phase-54c-evidence-knowledge-workflow.md` §6.1). If Gap 1 is
resolved via a new Decision record, that record's id should be added
here and cross-referenced from `context-packet.md` §11 in a follow-up
edit.
