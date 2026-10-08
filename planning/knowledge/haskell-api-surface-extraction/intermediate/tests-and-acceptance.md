# haskell-api-surface-extraction — tests and acceptance

<!-- codecompass-knowledge: REQ-HSAPI-001 semantic-sha256:4a4ea3117a3b68e2d93f7eb6fbad863cbc551ddfc0e198688a6067c651bebe95 projection-sha256:06fb276f03a85d12343f7929d1ca1b8332f5fb2050bf9b4ba2dadff7e894ba60 -->
### REQ-HSAPI-001

codecompass-adaptor-haskell's export-list scanner MUST, for the baseline shapes (bare identifiers in either leading- or trailing-comma style, `Type(..)` all-constructors expansion, Haddock `-- * Section` grouping headers, and whole-line commented-out entries), produce exactly the exported-name set a real GHC `:browse` would report for that module -- comment-stripping and tokenising the export-list span between `module <Name> (` and its own `where`.

Authorised by: DEC-HSAPI-001
Status: status=verified
Provenance: DECIDED
<!-- /codecompass-knowledge -->

<!-- codecompass-knowledge: REQ-HSAPI-002 semantic-sha256:6458ec75fdad7880ab51d74e94e01571a62aa405cf3925c48bf193c59fa2a630 projection-sha256:909c34f82a1bbac103f04228053990ba4a920793f2be5dc0b2eb754b1a567348 -->
### REQ-HSAPI-002

When the scanner encounters a `module <Name>` entry inside an export list, it MUST record that a re-export entry named `<Name>` occurred, and MUST NOT assert a flattened, fully-resolved list of real exported names for it. If `<Name>` matches this same file's own `import ... as <Name>` line, the scanner additionally records which real module(s) that alias covers in this file. No cross-file read is performed to resolve any `module <Name>` entry.

Authorised by: DEC-HSAPI-001
Status: status=verified
Provenance: DECIDED
<!-- /codecompass-knowledge -->

<!-- codecompass-knowledge: REQ-HSAPI-003 semantic-sha256:ee6f48a79e5e4eb3aae25bcfb8901dd828c1d1bd7bd13194a952d46734ede2df projection-sha256:ec4569ba3ce3ddca0e2e161f2cd6bf35d338d112039630ed97a1583be5334bf5 -->
### REQ-HSAPI-003

If a `#if`/`#endif` (or other CPP conditional directive) span appears within an export list's own parentheses, the scanner MUST flag the entry/entries enclosed by that span as undetermined rather than silently treating them as exported or silently dropping them.

Authorised by: DEC-HSAPI-001
Status: status=verified
Provenance: DECIDED
<!-- /codecompass-knowledge -->

<!-- codecompass-knowledge: REQ-HSAPI-004 semantic-sha256:8dfb79ecbd2b148f6dd62301e5a3fe252aca1d44b95bd39b0fa778af240a641a projection-sha256:34b2b4cd38876272b56569261334447ea4843d2dd6d752d1a06b0984d233f384 -->
### REQ-HSAPI-004

Before scanning any module's own export list, the adapter MUST determine whether that module is part of the package's own exposed surface (an explicit `exposed-modules` list in the generated `.cabal`, or hpack's own "all modules in source-dirs less other-modules" default when no explicit list is present). A module not in the package's exposed set MUST NOT contribute any symbols to the reported API surface, regardless of what its own export list says.

Authorised by: DEC-HSAPI-001
Status: status=verified
Provenance: DECIDED
<!-- /codecompass-knowledge -->

<!-- codecompass-knowledge: REQ-HSAPI-005 semantic-sha256:46f6dbb7a92089cc6370bc35e4abb5c158076cbc566f9644dec30b6a18918c31 projection-sha256:44d12aec76b1bbbb4686010ca911fa14c06ddc9243b255461edf480f7445c95a -->
### REQ-HSAPI-005

The scanner MUST reliably detect a module with no export list at all (`module <Name> where`, with no `(`-delimited list before `where`) as a distinct case, without false positives or false negatives, but MUST NOT attempt to enumerate that module's top-level bindings in this version — such a module contributes zero symbols plus one diagnostic noting the undetermined-surface condition.

Authorised by: DEC-HSAPI-001
Status: status=verified
Provenance: DECIDED
<!-- /codecompass-knowledge -->

<!-- codecompass-knowledge: REQ-HSAPI-006 semantic-sha256:aed3ba1d55c8c1e5741639d6d93d1d3dfa483285ae692aae79430bb26a142a5d projection-sha256:c9d613d2d98e3364f6d48095b2af907ee7823350f1b98b46f02afafd26b4fd3d -->
### REQ-HSAPI-006

Purpose-pairing MUST use a two-pass algorithm: pass 1 collects the exported-name set from the module header (per REQ-HSAPI-001); pass 2 walks the file body once and, for each exported name, records the nearest preceding `-- | ...` Haddock comment at that name's own definition site, independent of the name's position in the export list. An exported name with no such comment at its definition site MUST be reported with `purpose: null`, which is a correct, expected outcome, not an error condition.

Authorised by: DEC-HSAPI-001
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
