# doc-origin-pinned-reference — tests and acceptance

<!-- codecompass-knowledge: REQ-DOCORIGIN-001 semantic-sha256:d8f1c1480cb976531184958a7bcfaa4b92df66829a546bb1f18703f43095a0d7 projection-sha256:4af15b4ed0228bd8248f662684b0dc7cf06dda5a733453cc9ba15fefdc1fe743 -->
### REQ-DOCORIGIN-001

doc_artifacts.origin's CHECK constraint MUST accept a new value, 'pinned_reference', added via the existing _migrate_doc_artifacts_constraints mechanism (one more _SCHEMA_VERSION bump), following the exact Phase 17/21/27 precedent. No other origin consumer in src/codecompass/ requires any change for this addition alone.

Authorised by: DEC-DOCORIGIN-001
Status: status=verified
Provenance: DECIDED
<!-- /codecompass-knowledge -->

<!-- codecompass-knowledge: REQ-DOCORIGIN-002 semantic-sha256:94b287fc5c3017a0e0a37498fbbb5bef0820d72a575d05b8219310aec142a0bd projection-sha256:9c0d01f682a227dfe00a0c763283cff94adcc47448002ed3c02a827fb2b44cb7 -->
### REQ-DOCORIGIN-002

scan_spec_docs MUST assign origin='pinned_reference' (instead of 'project') to a dev-docs/**/*.md-glob-matched file whose leading content is a YAML frontmatter block (delimited by --- lines) that contains both a `resolved_commit` key and a `source_url` key. A file with no such frontmatter, or frontmatter missing either key, MUST keep the existing origin='project' behaviour unchanged.

Authorised by: DEC-DOCORIGIN-001
Status: status=verified
Provenance: DECIDED
<!-- /codecompass-knowledge -->

<!-- codecompass-knowledge: REQ-DOCORIGIN-003 semantic-sha256:f5eb6e0a4de018ed4a54c15f62bb6a2c3cc4c906457c33f8c9c1169e8367b54a projection-sha256:5b5bb593638636a72aa91cc76da91ee8ea132c74d4f5db625048aac0522d5005 -->
### REQ-DOCORIGIN-003

A new test fixture (a frontmatter-bearing .md file under a test project's dev-docs/ tree) MUST exercise scan_spec_docs's new origin='pinned_reference' branch directly, closing the real, currently-missing test-coverage gap CL-DOCORIGIN-002/EV-DOCORIGIN-008 identified. Every existing test asserting origin='project' for frontmatter-free fixtures MUST continue to pass unchanged.

Authorised by: DEC-DOCORIGIN-001
Status: status=verified
Provenance: DECIDED
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
