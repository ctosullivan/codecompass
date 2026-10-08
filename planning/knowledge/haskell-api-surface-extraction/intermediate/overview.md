# haskell-api-surface-extraction — overview

<!-- codecompass-knowledge: CL-HSAPI-001 semantic-sha256:6330946842f6d7ec1fecdf71eb664f174c2aa8d6ad5f6e7c4d3023a06392c121 projection-sha256:90c611ad78e1433c5bbe857ffed6a74994d9ef9f562ffcd121226e1a40e76a35 -->
### CL-HSAPI-001

For a Haskell module's export list, the baseline mechanical shapes -- a bare comma-separated identifier list (leading- or trailing-comma style, both real), `Type(..)` (exports the type plus every one of its real data constructors), whole-line `--`-prefixed comments including commented-out disabled entries, and Haddock `-- * Section` grouping headers that carry no identifier -- are correctly and completely handled by a simple comment-stripping-then-tokenising scan, with no need for a full parser. This was independently confirmed against a real compiler, not merely re-derived from reading the same source text: a naive comment-aware scan over AccountName.hs produced exactly the same 48-name set as GHC's own `:browse` output, and Query.hs's `Query(..)`/`OrdPlus(..)`/`QueryOpt(..)` were confirmed via `:browse` to expand to all 18/10/3 real constructors respectively.

Supporting evidence: [EV-HSAPI-002, EV-HSAPI-003, EV-HSAPI-007, EV-HSAPI-008]
Status: status=supported
Provenance: UNCLASSIFIED
<!-- /codecompass-knowledge -->

<!-- codecompass-knowledge: CL-HSAPI-002 semantic-sha256:72dd75e19946c818595de45ec3838305252b5bb2d0148a779b634bdd71a74b13 projection-sha256:c238ffe2c56555c4fe0e2809afc452f474199b2be9ea9ef04296f59bc0fae0d0 -->
### CL-HSAPI-002

A `module <Name>` entry inside an export list cannot be resolved into a flat set of exported names by reading that one line's text alone, and no single fixed strategy handles every real instance found in this codebase: it can name a genuinely different, unaliased, directly importable other module (requires reading THAT module's own export list -- a cross-file read); it can name an import alias standing for one or many distinct real modules at once (requires first scanning THIS SAME FILE's own `import ... as <Name>` lines, then, to fully expand, still requires cross-file reads of each aliased module); it can name another package's own aggregation module by its real name (same as the first case, one level removed); or it can self-reference the current module's own name (resolves to "this module's own complete export surface," close to but not textually the same as having no export list at all). A minimal, per-file, no-full-parser extractor (matching the Rust adapter's own single-file scope) can mechanically detect and record a `module <Name>` entry as occurring, and can do the one file-local step of matching it against this same file's own `import ... as <Name>` lines when the alias case applies, but cannot fully expand it to real names without reading other files -- a scope decision the next design step must make explicitly, not an ambiguity this research can resolve on its own.

Supporting evidence: [EV-HSAPI-005, EV-HSAPI-009, EV-HSAPI-010]
Status: status=supported
Provenance: UNCLASSIFIED
<!-- /codecompass-knowledge -->

<!-- codecompass-knowledge: CL-HSAPI-003 semantic-sha256:cf706b3871fa37b3443bbbbaade02e9b506d2c21bf154ebad0cd01daf7a13b94 projection-sha256:a0853dfc41b6d9774df7b37776df0d78533b4572b67e6713fe0cb0781763b38e -->
### CL-HSAPI-003

A real export list can contain a literal C-preprocessor conditional (`#if MIN_VERSION_<pkg>(x,y,z)` / `#endif`) gating whether a particular name is exported at all (confirmed real: hledger-lib/Hledger/Data/Types.hs gates `Year` behind `#if MIN_VERSION_time(1,11,0)`). A purely mechanical, non-preprocessing line/text scanner (the Rust-adapter tier this feature is meant to match) has no way to evaluate that condition from the file's own text alone, since the condition depends on which version of an external package (`time`, in this instance) the file is actually compiled against -- information not present anywhere in the .hs file itself. Any such scanner will therefore either (a) always treat `#if`-gated names as exported (an over-approximation, silently wrong whenever the condition would in fact be false for the target build), or (b) always skip/ignore lines starting with `#` while scanning for names (an under-approximation, silently dropping a real, sometimes-exported name like `Year`), or (c) treat the presence of a `#`-line as reason to fall back to a coarser "cannot determine, flag for manual/AI follow-up" result for that specific entry. This research does not resolve which of (a)/(b)/(c) is correct -- it depends on how much precision the adapter's whole purpose actually needs, a design choice, not a fact about hledger's own source.

Supporting evidence: [EV-HSAPI-009]
Status: status=supported
Provenance: UNCLASSIFIED
<!-- /codecompass-knowledge -->

<!-- codecompass-knowledge: CL-HSAPI-004 semantic-sha256:75909bfca108d67b5fb95bc2348ade7ddac9c7ca15f280659ede64181700018c projection-sha256:bfcc2e696df96b95c4e70932b8696eaea92a0f1f50db6d6df5b24f01a8238e81 -->
### CL-HSAPI-004

The Rust adapter's "pair each exported item with an immediately preceding doc comment" pattern does not transfer directly to Haskell, because Haskell structurally decouples WHERE a name is declared exported (the module-header export list, which in every real file read carries no attached per-item doc text of its own beyond optional Haddock `-- * Section` grouping headers) from WHERE that name's own documentation lives (a `-- | ...` Haddock comment immediately preceding that name's own type-signature/definition, physically elsewhere in the same file's body, in body-declaration order rather than export-list order). Confirmed directly and concretely: AccountName.hs lists `accountLeafName` first in its export list, but that name's own definition (with no attached Haddock comment at all) appears in the body AFTER accountNameComponents/ accountNameFromComponents's own definitions, which are listed second and third in the export list. A Haskell equivalent of Rust's "purpose" field therefore requires a structurally different, two-pass algorithm (first collect exported names from the header, then for each name separately locate its own `<name> ::`/definition line anywhere later in the same file body and check THAT site's own preceding comment) -- not a single forward scan -- and `purpose: None` is an expected, common, correct outcome for many real exported names (accountLeafName being a direct, confirmed example), not a sign of scanner failure.

Supporting evidence: [EV-HSAPI-002, EV-HSAPI-003]
Status: status=supported
Provenance: UNCLASSIFIED
<!-- /codecompass-knowledge -->

<!-- codecompass-knowledge: CL-HSAPI-005 semantic-sha256:dc89a80fe4b2b779bcfd1d701b7586a933e544bc7af2f9c5b17788c7738ece3a projection-sha256:26726c74a4e34b952d2821f50f5b33ee9cace64d008e4538edca8c067ad9c16b -->
### CL-HSAPI-005

A package's own `exposed-modules` list (hpack `package.yaml` / generated `.cabal` file) is a real, separate visibility boundary, one level above a module's own export list -- only a module named in `exposed-modules` is visible to code outside the package at all, so a correct "public API surface" extractor for a Haskell package should filter candidate `.hs` files against this list (or the hpack default documented at package.yaml:122, "all modules in source-dirs less other-modules") before running any per-file export-list scan, matching the task's own framing that a module's own export list "only matters if the module itself is exposed by the package in the first place." HOWEVER, this specific reference package (hledger-lib, and likewise the sibling hledger package) does not actually exercise this filter in a way that would catch a scanner that skipped it entirely: every real, hand-authored source module in both packages IS exposed; the only excluded entries are Setup.hs and generated Paths_/ PackageInfo_ modules a filesystem walk would exclude for other reasons anyway (no `module ... where` matching the package's own namespace, or simply not being real source). Testing this mechanism against hledger-lib/hledger alone, as this research did, cannot demonstrate the filter actually changes which files get scanned -- an honest gap, not a settled confirmation that the mechanism matters in practice for THIS reference project, even though it is real Haskell/Cabal machinery that will matter for other, differently-structured Haskell packages.

Supporting evidence: [EV-HSAPI-006]
Status: status=supported
Provenance: UNCLASSIFIED
<!-- /codecompass-knowledge -->

<!-- codecompass-knowledge: CL-HSAPI-006 semantic-sha256:339418f2492de8fb2ae19f7ee75717feee909767f11a4c8b59bde8b93ca4073b projection-sha256:186992200b6324fa3aef3681994ed5f9252ba581b6486390a3922652e2f841b5 -->
### CL-HSAPI-006

A module with no export list at all (`module Foo where`, no parenthesised list, not even an empty `()`) is real and confirmed present 17 times across the pinned hledger checkout (though never inside hledger-lib itself), and per Haskell's own semantics means every top-level binding/type/class the module defines is exported. Detecting the ABSENCE of an export list mechanically is straightforward (no `(` between `module <Name>` and the module's own `where`, confirmed as a reliable discriminator across a 147-module real sample with zero false positives/negatives found). However, correctly ENUMERATING "every top-level binding" in that case is a materially harder problem than anything the export-list-present case requires: unlike Rust's `pub fn`/`pub struct` (a keyword physically at the start of the declaration), a bare Haskell top-level binding has no uniform single-token marker -- recognising where one top-level declaration ends and the next begins in general depends on Haskell's own column/layout rule, which a coarse line-based scan (the Rust adapter's own tier) does not attempt. This research did not build or test such a fallback scan against a real no-export-list file's own actual top-level bindings, so whether a Rust-adapter-tier heuristic (e.g. "a line starting at column 0 that isn't `import`/`{-`/a pragma/an operator-continuation is a new top-level name") is good enough in practice remains untested and is named here as an open question, not quietly assumed solved.

Supporting evidence: [EV-HSAPI-004]
Status: status=supported
Provenance: UNCLASSIFIED
<!-- /codecompass-knowledge -->

<!-- codecompass-knowledge: DEC-HSAPI-001 semantic-sha256:290e7077c5e7699368c79a4868fae11ce532e3d73559e928d3f40ca377f93342 projection-sha256:30429e00b6b230250400727c4100d2377ed76feee6d851dc8a2196f9943bd3da -->
### DEC-HSAPI-001

Adopts all six of design.md §15's recommended answers, unchanged: 1) `module <Name>` re-export entries get file-local partial resolution -- record the occurrence, and where it is a same-file `import ... as <Name>` alias, which real modules that alias covers in this file; never cross-file expansion (§15.1, option b). 2) A CPP conditional (`#if`/`#endif`) found inside an export list's own parentheses causes the enclosed entry/entries to be flagged undetermined, never silently included or excluded (§15.2, option c). 3) The package-level `exposed-modules` filter (from `package.yaml`'s own explicit list, or hpack's "all modules in source-dirs less other-modules" default when no explicit list exists) IS implemented: a module not in a package's own exposed set is not scanned for its export surface at all, regardless of what its own export list says (§15.3, option a). 4) A module with no export list (`module Foo where`, no parenthesised list) is reliably detected as such, but its top-level bindings are NOT enumerated in this version -- return an empty symbol list plus a diagnostic for such a module (§15.4, option b). 5) The two-pass purpose-pairing algorithm (collect exported names from the header, then separately locate each name's own definition site in the file body and check its preceding `-- | ...` comment) IS built in this first version, not deferred (§15.5, option a). 6) No explicit handling is added for the two grammar-valid, zero-observed-instance shapes (same-line trailing comment; `Type(Ctor1, Ctor2)` named-constructor-subset) -- left unhandled until real evidence of occurrence surfaces (§15.6, option b). Additionally ratifies design.md §11's baseline mechanism (a comment-stripping, identifier-tokenising scan over each module's export-list span, handling both comma styles, `Type(..)`, section headers, and commented-out entries) as the extractor's core, per CL-HSAPI-001's own compiler-verified sufficiency.

Status: status=approved
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
