# first-party-source-symbols — overview

<!-- codecompass-knowledge: CL-FPSS-001 semantic-sha256:36ddf18f0638184992eb7d3235aaaf8d39713dd66340a3e273e1b216bc84abdf projection-sha256:751f73b1aa783cb019c61fa9c2574b400ada4a5e466776fb6c242f5984ca1c36 -->
### CL-FPSS-001

source_symbols.Language is a new, narrow, five-value concept (python/rust/javascript/typescript/haskell) introduced specifically because the pre-existing core.Ecosystem concept cannot distinguish JavaScript from TypeScript (both collapse to a single NPM value there, a *package-ecosystem* concept), whereas first-party symbol-kind extraction genuinely needs that distinction (e.g. only TypeScript files can declare interface/type constructs). Language is defined in source_symbols.py itself, not core.py, and is not imported or referenced by core.Ecosystem or vice versa within this module.

Supporting evidence: ["EV-FPSS-001", "EV-FPSS-002", "EV-FPSS-016"]
Status: status=supported, evidence_support_state=supported
Provenance: OBSERVED
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
