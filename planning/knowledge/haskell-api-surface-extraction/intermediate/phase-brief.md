# haskell-api-surface-extraction — phase brief

A single entry point into this slug's own `intermediate/*.md` files — mechanically compiled from the same records they render, never a separate representation of the same knowledge (planning/phase-81-intermediate-knowledge-layer.md §5.2).

- **Concepts, architecture, domain knowledge** — `overview.md` (7: CL-HSAPI-001, CL-HSAPI-002, CL-HSAPI-003, CL-HSAPI-004, CL-HSAPI-005, CL-HSAPI-006, DEC-HSAPI-001)
- **Invariants and constraints** — `invariants-and-constraints.md` (0: none yet)
- **Interfaces and behaviours** — `interfaces-and-behaviours.md` (0: none yet)
- **Open questions and conflicts** — `open-questions-and-conflicts.md` (0: none)
- **Test scenarios and acceptance behaviour** — `tests-and-acceptance.md` (6: REQ-HSAPI-001, REQ-HSAPI-002, REQ-HSAPI-003, REQ-HSAPI-004, REQ-HSAPI-005, REQ-HSAPI-006)

Edge cases and compatibility constraints are recorded as ordinary Claims above (typically under invariants/constraints or open questions) rather than in a separate section here — see each file's own content for the real detail; this brief only indexes it.

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
