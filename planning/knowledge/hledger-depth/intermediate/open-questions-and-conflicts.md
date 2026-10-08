# hledger-depth — open questions and conflicts

<!-- codecompass-knowledge: CL-HLEDGERDEPTH-002 semantic-sha256:7d1a4c88e0dfcbf8d3303706499ef70112655a046188116d101e09dd81e40470 projection-sha256:f4dc7c7c24d1c72d7be108b1f6f9d187d505408ed0e220957fabaa96cb5cc2f8 -->
### CL-HLEDGERDEPTH-002

External proposal (simulating an outside tool/contributor, not yet verified by this project): the balancesheet and incomestatement report commands likely apply depth the same display-only clipping way balance does, since they are documented as thin wrappers around the same balance-report machinery -- but this has not been directly observed against the real hledger binary here and should be checked before being trusted.

Status: status=proposed
Provenance: DECLARED
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
