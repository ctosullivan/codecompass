# first-party-source-symbols — interfaces and behaviours

<!-- codecompass-knowledge: CL-FPSS-003 semantic-sha256:ffcd040d6eb8c25fefadae9bce540b5a3fe5ccd71b08316d4d33a08a516ab5f0 projection-sha256:5cf9d7798d244089a4b9a2131d84c4d9fb2534a06ab6d2f7e8ba19230bb3617e -->
### CL-FPSS-003

The five-state SymbolIndexStatus model (indexed/indexed_partial/ unsupported/parse_error/unreadable) exists to prevent a bare empty symbols list from ambiguously standing in for more than one real cause. indexed and indexed_partial are distinguished purely by extraction *technique fidelity*, never by whether anything was found: indexed means a real structural parser (Python's ast.parse) ran and either succeeded (possibly finding zero symbols) or the extractor never reaches this status if parsing itself failed; indexed_partial means a coarse line-scan/regex heuristic ran (Rust, JS, TypeScript) -- a technique with no real parse step, so it can never fail structurally the way ast.parse can, and is dispatched unconditionally on successful file read regardless of what (if anything) it finds. unsupported means no extractor exists for the file's language at all (Haskell today) -- the file is never even opened. parse_error is Python-specific (ast.parse raising SyntaxError) since Rust/JS/TS have no real parse step to fail. unreadable applies to any language (OSError or UnicodeDecodeError on read). No code path in this module ever returns indexed_partial for Python or indexed for Rust/JS/TS -- the mapping from language to indexed-vs-indexed_partial is fixed, not content-dependent.

Supporting evidence: ["EV-FPSS-006", "EV-FPSS-007", "EV-FPSS-020"]
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
