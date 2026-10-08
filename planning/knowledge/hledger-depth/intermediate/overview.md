# hledger-depth — overview

<!-- codecompass-knowledge: CL-DEPTH-001 semantic-sha256:35778b215850ecba2c99ef9a52e045b5ff7a3c65f56de049c5d1050b7ef5137d projection-sha256:5ad74802a5fb33ee4e002414fcf6556281da89b028251d60bbb4c64d1cf88c3c -->
### CL-DEPTH-001

hledger's depth:/--depth query term is not uniform across commands. For balance, register, and accounts it is a display-only clip/ aggregate operation: postings/accounts deeper than the limit are never excluded from the underlying computation, only clipped (and, where names collide after clipping, aggregated/deduplicated) for display. For stats it is a genuine, partial exclusion: postings deeper than the limit are dropped from the journal stats reads its own posting-derived counts (e.g. "Accounts") from, though whole transactions are never dropped, so "Txns" stays unaffected. For print it has no effect at all -- depth is stripped from the query before filtering and never consulted again.

Supporting evidence: [EV-DEPTH-001, EV-DEPTH-002, EV-DEPTH-003]
Status: status=verified
Provenance: UNCLASSIFIED
<!-- /codecompass-knowledge -->


## Candidate additions

Add new domain knowledge, edge cases, invariants, or open questions below, strictly between the two marker comments. Content outside this region — including this paragraph — is never read as knowledge; it is just narrative framing CodeCompass leaves untouched.

Plain prose becomes an unclassified Claim (a factual hypothesis, not yet evidence-backed) — this is the default and the common case. Merely mentioning a Decision id anywhere in your prose does NOT make your addition a Requirement, and merely using the word "should" or "must" does NOT make it declared intent — both need the explicit structured forms below.

To propose a REQUIREMENT, start the block with a line reading exactly "Type: Requirement", followed by:
  Decision: <id of an existing, already-approved Decision>
  Statement: <the requirement itself, one line>
  Example: <a Given/When/Then acceptance example>
CodeCompass never invents a Decision on your behalf — a missing or not-yet-approved Decision id, or an Example that doesn't structurally read as Given/When/Then, falls back to an ordinary Claim using your Statement text, never a fabricated placeholder example.

To declare project INTENT (a proposed policy, not yet a fact about the system), start the block with a line reading exactly "Type: Intent", followed by the intended behaviour as plain prose on the lines after it.

Anything else — plain prose with no Type: header — stays an unclassified Claim until a reviewer looks at it.

<!-- codecompass-candidates:start --><!-- codecompass-candidates:end -->
