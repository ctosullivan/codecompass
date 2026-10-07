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

To propose a Requirement rather than a Claim, cite an existing, already-approved Decision id explicitly (e.g. "per DEC-ARCH-003") — CodeCompass never invents a Decision on your behalf; without a cited, approved Decision, your addition becomes a Claim.

<!-- codecompass-candidates:start --><!-- codecompass-candidates:end -->
