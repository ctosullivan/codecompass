---
status: RESEARCHED
feature: haskell-api-surface-extraction
related_phase: "Phase 60 (codecompass-adaptor-haskell, minimal Haskell adapter)"
reference_corpus: "hledger-lib (and sibling hledger/hledger-ui/hledger-web packages), pinned commit 33fa849e7ae841968bd21c427094c4fb4a4ec38d"
researched_at: "2026-09-19T00:00:00Z"
---

# Design: mechanical, no-AI Haskell public API-surface extraction

## 1. Feature purpose and concepts

The Haskell adapter (`codecompass-adaptor-haskell`, a separate,
external Haskell/Stack process communicating over the adapter protocol
— not Python, not part of `src/codecompass/`) needs its own equivalent
of `extract_rust_symbols` in `src/codecompass/symbols.py`: a small,
mechanical, single-pass-or-near-single-pass, no-AI, no-full-parser
scanner over `.hs` source files that produces a public API surface
(symbol name + optional one-line purpose) (`EV-HSAPI-001`,
`OBS-HSAPI-001`). The real target corpus researched is hledger-lib and
its sibling packages (hledger, hledger-ui, hledger-web) at the commit
this project has already pinned elsewhere.

Two concepts govern what "public" means in Haskell, distinct from
Rust's single per-declaration `pub` keyword:

- **A module's own export list** — the parenthesised list between
  `module <Name> (` and `where`, naming exactly which of the module's
  top-level names are visible outside it (or, if omitted, every
  top-level name is visible) (`OBS-HSAPI-002`, `OBS-HSAPI-005`).
- **A package's own `exposed-modules` list** (in `package.yaml`/the
  generated `.cabal` file) — a second, higher-level visibility boundary
  above the per-module export list: a module not listed there is not
  part of the package's public surface at all, regardless of its own
  export list (`OBS-HSAPI-007`, `OBS-HSAPI-008`, `CL-HSAPI-005`).

## 2. Observed current/upstream behaviour

- **Existing precedent (Rust adapter).** `extract_rust_symbols` is a
  single-pass, line-based scan keyed on a per-declaration visibility
  keyword (`pub ...`) physically adjacent, on consecutive lines, to
  both the declaration and its own preceding `///` doc comment; no
  separate, file-header-level export list exists in Rust for this
  construct (`EV-HSAPI-001`, `OBS-HSAPI-001`).
- **Haskell export lists are large and stylistically varied even
  within one real package.** `Hledger/Query.hs`'s export list spans 65
  lines and mixes bare trailing-comma identifiers, `Type(..)` entries,
  Haddock `-- * Section` grouping headers (which carry no identifier),
  and a whole-line `--`-commented-out disabled entry
  (`OBS-HSAPI-002`, `EV-HSAPI-002`). `Hledger/Data/AccountName.hs`'s
  export list instead uses leading-comma style, has no section
  headers at all, and has its own commented-out entry in that same
  leading-comma shape (`OBS-HSAPI-003`, `EV-HSAPI-003`) — confirming
  comma style and section-header use are per-module stylistic choices,
  not universal structure.
- **A module can have no export list at all.** `module Foo where`
  (no parenthesised list, not even an empty `()`) means every
  top-level name is exported. This form does not occur anywhere in
  hledger-lib's own 65 modules, but is real and confirmed present 17
  times across the wider pinned checkout (hledger, hledger-ui,
  hledger-web, and standalone scripts), with two instances read
  directly and confirmed genuinely bare
  (`OBS-HSAPI-004`, `OBS-HSAPI-005`, `EV-HSAPI-004`).
- **`module <Name>` re-export entries resolve in (at least) four real,
  distinct shapes**, not one: (1) an unaliased, directly-named other
  module (`Hledger/Utils.hs`'s six `module Hledger.Utils.*` entries);
  (2) an import alias standing for several distinct real modules at
  once (`Hledger.hs`'s `module X`, covering five modules;
  `Hledger/Cli/Script.hs`'s `module M`, covering a dozen-plus); (3)
  another package's own aggregation module named directly
  (`Hledger/Cli.hs`'s `module Hledger`); (4) a self-re-export of the
  current module's own name (`Hledger/Data/Types.hs`'s
  `module Hledger.Data.Types`) (`OBS-HSAPI-006`, `OBS-HSAPI-012`,
  `EV-HSAPI-005`, `EV-HSAPI-009`, `EV-HSAPI-010`, `CL-HSAPI-002`). A
  single real export list (`Hledger/Cli.hs`) mixes several of these
  shapes together with plain bare names and a section header in one
  list (`OBS-HSAPI-012`).
- **A literal CPP conditional can sit inside an export list**, gating
  whether a specific name is exported at all:
  `Hledger/Data/Types.hs` gates `Year` behind
  `#if MIN_VERSION_time(1,11,0)` / `#endif`, and this is only
  meaningful because `{-# LANGUAGE CPP #-}` is active for that file
  (`OBS-HSAPI-011`, `EV-HSAPI-009`, `CL-HSAPI-003`). A wider grep found
  CPP conditionals are common near module headers generally in this
  codebase, but on closer inspection most sit in the file *body* after
  `where`, not literally inside the export-list parentheses — Types.hs
  remains the one confirmed case of a conditional gating an
  export-list entry specifically (`OBS-HSAPI-012`).
- **The package-level `exposed-modules` boundary is real but barely
  exercised by this corpus.** In both `hledger-lib.cabal` and
  `hledger.cabal`, every hand-authored source module is exposed; the
  only entries excluded are `Setup.hs` and build-autogenerated
  `Paths_*`/`PackageInfo_*` modules — files a plain filesystem walk
  would likely exclude anyway (`OBS-HSAPI-007`, `OBS-HSAPI-008`,
  `EV-HSAPI-006`, `CL-HSAPI-005`).
- **Export-list order and doc-comment location are decoupled.** In
  `AccountName.hs`, `accountLeafName` is listed *first* in the export
  list but its own definition (with **no** attached Haddock comment at
  all) appears in the body *after* `accountNameComponents`/
  `accountNameFromComponents`, which are listed second and third
  (`OBS-HSAPI-003`, `EV-HSAPI-003`, `CL-HSAPI-004`).
- **Two further real Haskell export-list grammar shapes were searched
  for and not found anywhere in this corpus**: a same-line trailing
  comment attached directly after an identifier, and a
  named-constructor-subset export (`Type(Ctor1, Ctor2)` rather than
  full `Type(..)`) (`OBS-HSAPI-013`, `EV-HSAPI-011`). Both are valid
  Haskell grammar; this reference corpus simply does not exercise
  them.

## 3. Syntax/API forms confirmed real in this corpus

| Form | Confirmed real? | Evidence |
|---|---|---|
| Bare comma-separated identifier, trailing-comma style | yes | `OBS-HSAPI-002`, `EV-HSAPI-002` |
| Bare comma-separated identifier, leading-comma style | yes | `OBS-HSAPI-003`, `EV-HSAPI-003` |
| `Type(..)` (all constructors) | yes, confirmed against real GHC `:browse` output | `OBS-HSAPI-010`, `EV-HSAPI-008` |
| Haddock `-- * Section` grouping header (no identifier) | yes | `OBS-HSAPI-002`, `EV-HSAPI-002` |
| Whole-line `--`-commented-out disabled entry | yes, in both comma styles | `OBS-HSAPI-002`, `OBS-HSAPI-003`, `EV-HSAPI-002`, `EV-HSAPI-003` |
| No export list at all (`module Foo where`) | yes, 17 instances outside hledger-lib | `OBS-HSAPI-004`, `OBS-HSAPI-005`, `EV-HSAPI-004` |
| `module <Name>` re-export, 4 distinct resolution shapes | yes | `OBS-HSAPI-006`, `OBS-HSAPI-012`, `CL-HSAPI-002` |
| CPP conditional gating an export-list entry | yes, one confirmed instance | `OBS-HSAPI-011`, `EV-HSAPI-009`, `CL-HSAPI-003` |
| Same-line trailing comment after an identifier | valid grammar, **not found** in this corpus | `OBS-HSAPI-013`, `EV-HSAPI-011` |
| Named-constructor-subset export `Type(Ctor1, Ctor2)` | valid grammar, **not found** in this corpus | `OBS-HSAPI-013`, `EV-HSAPI-011` |

## 4. Behavioural rules and precedence

- **A simple comment-stripping-then-tokenising scan is sufficient for
  the baseline shapes** (bare identifiers in either comma style,
  `Type(..)`, whole-line comments, section headers) — this was not
  merely inferred from reading source text, but independently
  confirmed against a real compiler: a naive comment-aware Python scan
  over `AccountName.hs` produced exactly the same 48-name set as GHC's
  own `:browse` output, correctly excluding the one commented-out
  name, and `Query(..)`/`OrdPlus(..)`/`QueryOpt(..)` were confirmed
  via `:browse` to expand to all 18/10/3 real constructors
  respectively (`CL-HSAPI-001`, derivation `DE-HSAPI-001`,
  `EV-HSAPI-007`, `EV-HSAPI-008`).
- **`module <Name>` cannot be resolved from its own line's text
  alone**, and no single fixed strategy covers all four real shapes.
  Resolving cases (1)-(3) requires cross-file reads (another module's
  own export list, or first this same file's own `import ... as
  <Name>` lines then a cross-file read); case (4) resolves in-file but
  is semantically "this module's entire export surface." A minimal,
  per-file scanner can mechanically *detect* a `module <Name>` entry
  and can do the one file-local step of matching it against this same
  file's own `import ... as <Name>` lines, but cannot fully expand it
  to real names without reading other files — explicitly named as a
  scope decision the design step (not the research step) must make
  (`CL-HSAPI-002`, derivation `DE-HSAPI-002`).
- **A CPP-gated export entry cannot be evaluated by a pure text
  scanner** — the condition depends on which version of an external
  package the file is compiled against, information absent from the
  `.hs` file itself. Three mechanical responses are possible: (a)
  always treat the name as exported (over-approximation, silently
  wrong when the guard is false); (b) always skip `#`-prefixed lines
  while scanning (under-approximation, silently drops a real,
  sometimes-exported name); (c) treat a `#`-line inside the
  export-list span as reason to flag that one entry as
  undetermined rather than guessing. The research does not resolve
  which is correct — it depends on how much precision the adapter
  needs, a design choice (`CL-HSAPI-003`, derivation `DE-HSAPI-003`).
- **Purpose-pairing cannot reuse the Rust adapter's single-forward-scan
  logic.** Haskell decouples *where a name is declared exported*
  (the header export list, which carries no attached per-item doc text
  of its own beyond optional section headers) from *where that name's
  own documentation lives* (a `-- | ...` Haddock comment immediately
  preceding that name's own definition, elsewhere in the file body, in
  body-declaration order rather than export-list order). A Haskell
  equivalent of Rust's "purpose" field requires a two-pass algorithm:
  first collect exported names from the header, then for each name
  separately locate its own definition line later in the same file's
  body and check that site's own preceding comment.
  `purpose: None` is an expected, common, correct outcome for many
  real exported names (`accountLeafName` being a direct, confirmed
  example) rather than a sign of scanner failure (`CL-HSAPI-004`,
  derivation `DE-HSAPI-004`).

## 5. Important interactions and dependencies

- **Package manifest parsing is a dependency of correct scope, not
  merely of per-file scanning.** Whether a candidate `.hs` file should
  be scanned at all depends on the package's own `exposed-modules`
  list (or the hpack default, "all modules in source-dirs less
  other-modules"), a boundary above the per-file export-list scan
  (`CL-HSAPI-005`, derivation `DE-HSAPI-005`, `EV-HSAPI-006`).
- **Import-alias resolution is a file-local dependency of the
  `module <Name>` case**, specifically: correctly recognising case (2)
  requires the scanner to also read this same file's own
  `import ... as <Name>` lines, not the export list in isolation
  (`CL-HSAPI-002`, `EV-HSAPI-010`).
- **CPP awareness is a dependency only insofar as detecting its
  presence, not evaluating it** — the scanner cannot depend on an
  actual C preprocessor pass (out of scope for a no-full-parser
  extractor), so it can only detect that a `#if`/`#endif` pair appears
  within an export list's line span, not resolve its truth value
  (`CL-HSAPI-003`).

## 6. Architecture / implementation concepts

- **File-local, two-pass structure** (per §4's purpose-pairing rule):
  pass 1 walks the module header/export-list span, comment-stripping
  and tokenising to produce the raw exported-name set (`CL-HSAPI-001`);
  pass 2 walks the whole file body once, and for each exported name
  found in pass 1, records the nearest preceding `-- | ...` comment at
  that name's own definition site, if any (`CL-HSAPI-004`). This is a
  structurally different shape from the Rust adapter's single forward
  scan (`EV-HSAPI-001`), not a drop-in reuse of it.
- **Detecting "no export list" is a cheap, reliable discriminator**:
  no `(` between `module <Name>` and the module's own `where` was
  checked as a classifier across a 147-module real sample with zero
  false positives/negatives found (`OBS-HSAPI-005`, `CL-HSAPI-006`).
  Correctly *enumerating* every top-level binding in that case is a
  materially harder, untested problem, since Haskell's layout rule
  (not a single-token marker like Rust's `pub`) governs where one
  top-level declaration ends and the next begins — no fallback
  heuristic was built or tested against a real file in this research
  (`CL-HSAPI-006`, derivation `DE-HSAPI-006`).

## 7. Examples (Given/When/Then)

These illustrate confirmed real behaviour this design proposes the
extractor handle; none is yet a ratified Requirement (no Decision
record exists for this feature yet — see §14).

**Example 1 — baseline bare-identifier and `Type(..)` scan
(supports `CL-HSAPI-001`):**
> Given `hledger-lib/Hledger/Data/AccountName.hs`'s real export list
> (leading-comma style, one commented-out entry),
> When a comment-stripping, identifier-tokenising scan runs over it,
> Then it produces exactly the same 48-name set GHC's own `:browse`
> confirms as actually exported, correctly excluding the
> commented-out name (`EV-HSAPI-007`).

**Example 2 — `Type(..)` expands to real constructors (supports
`CL-HSAPI-001`):**
> Given `hledger-lib/Hledger/Query.hs`'s `Query(..)` entry,
> When the scanner records it as "exports `Query` and all of its
> constructors" rather than just the bare type name,
> Then this matches GHC's own confirmed 18-constructor `:browse`
> output for `Query` (`EV-HSAPI-008`).

**Example 3 — purpose-pairing requires a second, body-wide pass
(supports `CL-HSAPI-004`):**
> Given `AccountName.hs`, where `accountLeafName` is exported first
> but its own definition (no preceding doc comment) appears in the
> body after two later-listed exports' own, documented definitions,
> When the extractor runs its second body-wide pass per name rather
> than pairing by export-list-adjacent lines,
> Then `accountLeafName` correctly gets `purpose: None` and the two
> later names correctly get their own real Haddock text, matching
> body location rather than export-list order (`EV-HSAPI-003`).

**Example 4 — a `module <Name>` entry is detected but not expanded
(supports `CL-HSAPI-002`, proposed minimal v1 behaviour, §10):**
> Given `hledger-lib/Hledger.hs`'s `module X` entry, where `X` is an
> alias for five real imports,
> When the extractor encounters this entry,
> Then it records that a re-export entry named `X` occurred (and,
> minimally, which real modules `X` aliases in this file, from the
> file's own `import ... as X` lines) without attempting to expand it
> into a flat list of real exported names (`EV-HSAPI-005`,
> `EV-HSAPI-010`).

## 8. Edge cases

- A module's export list can contain a mix of several `module <Name>`
  resolution shapes *and* plain bare names *and* a section header, all
  in the same list (`Hledger/Cli.hs`) — a scanner must not assume a
  file uses only one shape (`OBS-HSAPI-012`).
- A commented-out export candidate can appear in either comma style
  and must be excluded even though it is textually identical in shape
  to a live entry apart from its leading `--` (`OBS-HSAPI-002`,
  `OBS-HSAPI-003`).
- A CPP-gated entry sits *inside* the export-list parentheses in the
  one confirmed instance, not merely somewhere in the file body —
  naive "skip anything after `where`" logic would not even notice this
  case (`OBS-HSAPI-011`).
- A self-re-export (`module <OwnName>`) is functionally close to, but
  not textually the same as, omitting the export list — a scanner that
  only checks "is there a `(` at all" would treat this file as
  export-list-present when its practical effect is closer to
  export-everything (`OBS-HSAPI-011`, `CL-HSAPI-002`).
- A frontmatter-free — sorry, export-list-free — module (`module Foo
  where`) is real but never occurs inside hledger-lib's own 65
  modules; it only shows up once the wider checkout is sampled. A
  scanner validated only against hledger-lib alone would not exercise
  this path at all (`OBS-HSAPI-004`, `OBS-HSAPI-005`).
- No real instance of a same-line trailing comment or a
  named-constructor-subset export was found anywhere in this corpus,
  despite both being valid Haskell grammar — an extractor that does
  not special-case them is untested against real evidence either way,
  not confirmed safe or confirmed broken (`OBS-HSAPI-013`,
  `EV-HSAPI-011`).

## 9. Known uncertainties

- **No Claim in this knowledge base carries `status: contradicted`.**
  All six Claims (`CL-HSAPI-001` through `CL-HSAPI-006`) are `status:
  supported`, each with an empty `contradicting_evidence` list. There
  is no disputed factual claim to flag here — worth stating plainly
  rather than silently omitting the category, matching this project's
  own `doc-origin-pinned-reference/design.md` precedent.
- **Genuine open design questions the research explicitly did not
  resolve** (each is a scope/precision decision, not a fact about
  hledger's own source, and each is carried into §14's numbered
  decision list rather than silently answered here):
  - How far to resolve `module <Name>` re-export entries
    (`CL-HSAPI-002`).
  - Which of the three mechanical responses to a CPP-gated export
    entry to adopt (`CL-HSAPI-003`).
  - Whether to implement the package-level `exposed-modules` filter
    given it is real but essentially untested by this one reference
    corpus (`CL-HSAPI-005`).
  - Whether to attempt any fallback enumeration for no-export-list
    modules, given no such fallback was built or tested
    (`CL-HSAPI-006`).
  - Whether to implement the two-pass purpose-pairing algorithm in a
    first version at all, given its added complexity relative to the
    Rust adapter's single-pass version (`CL-HSAPI-004`).
  - Whether to add explicit handling now for the two grammar-valid
    shapes never observed in this corpus (`EV-HSAPI-011`).
- **Untested-but-real gap, disclosed rather than smoothed over**: the
  `exposed-modules` package filter cannot be shown to change scanner
  behaviour using hledger-lib/hledger alone, since every real,
  hand-authored module in both packages happens to already be exposed
  (`CL-HSAPI-005`). This is a real limit of the reference corpus, not
  a claim that the mechanism is unimportant for other Haskell
  packages.

## 10. Contradictions between behaviour/source/tests/docs

None found. This research is inspection of upstream Haskell source and
independent GHC-compiler confirmation (`stack ghci` + `:browse`), not
a comparison against any existing CodeCompass test suite or
documentation for this not-yet-implemented feature — there is nothing
yet on the CodeCompass side to contradict. The one place a contrast
was explicitly checked (mechanical-scan output vs. real compiler
output, `EV-HSAPI-007`/`EV-HSAPI-008`) found agreement, not
contradiction.

## 11. Proposed behaviour for the target project

Proposed only — pending the review this design doc requests (§14); no
Decision or Requirement record exists yet for this feature.

- Implement a comment-stripping, identifier-tokenising scan over each
  module's export-list span (between `module <Name> (` and its own
  `where`) as the baseline mechanism for bare identifiers (both comma
  styles), `Type(..)`, section headers (skipped, no identifier), and
  whole-line/leading-comma-shaped commented-out entries (excluded) —
  directly following `CL-HSAPI-001`'s confirmed-sufficient scope.
- Implement the two-pass purpose-pairing algorithm described in §6,
  rather than attempting to reuse the Rust adapter's adjacent-comment
  pairing unchanged — per `CL-HSAPI-004`.
- Detect a `module <Name>` entry and record its occurrence plus (where
  it is a file-local `import ... as <Name>` alias) which real modules
  that alias covers in this file, without attempting further cross-file
  expansion in this version — per `CL-HSAPI-002`'s own scope note; see
  §14 decision 1 for the exact recommended minimal behaviour.
- Detect a `#if`/`#endif` span occurring inside an export list's own
  parentheses and flag the enclosed entry/entries as undetermined
  rather than silently guessing include or exclude — per
  `CL-HSAPI-003`'s option (c); see §14 decision 2.
- Detect "no export list present" (`module <Name> where`, no `(` before
  `where`) reliably, per the confirmed 147-module discriminator
  (`CL-HSAPI-006`), but do not attempt to enumerate top-level bindings
  for such a module in this version; see §14 decision 4.

## 12. Intentional differences from upstream behaviour

Not a target-vs-upstream divergence in the sense the `hledger depth:`
knowledge base uses that phrase (there, Ledgerkit chooses whether its
own re-implementation matches hledger's real computed output). Here,
the relevant "upstream" is GHC's own real, complete resolution of a
module's visible surface (as confirmed via `:browse`), and the
adapter's proposed behaviour is a deliberately **partial, mechanical
approximation of it, not a full reimplementation** — a real,
disclosed gap rather than a values-based deviation:

- The adapter will not evaluate CPP conditionals the way GHC's own
  `-XCPP` pass does, and instead flags affected entries as
  undetermined (`CL-HSAPI-003`).
- The adapter will not fully expand `module <Name>` re-exports across
  files the way GHC's own module system does (`CL-HSAPI-002`).
- The adapter will not enumerate top-level bindings for
  export-list-free modules the way GHC's own layout-aware parser does
  (`CL-HSAPI-006`).

Each of these is an intentional scope limit of a no-AI, no-full-parser
extractor (matching the Rust adapter's own precedent tier,
`EV-HSAPI-001`), not a claim that GHC's own real resolution is
somehow different from what the research found it to be.

## 13. Non-goals

- A full Haskell parser or a GHC-API-backed extractor — explicitly out
  of scope per this feature's own framing as the Rust adapter's
  analogue (`EV-HSAPI-001`).
- Evaluating CPP conditionals for real (would require knowing the
  target build's actual dependency versions) — `CL-HSAPI-003`.
- Full cross-file/cross-package expansion of `module <Name>` re-export
  entries — `CL-HSAPI-002`.
- Enumerating top-level bindings for export-list-free modules via a
  layout-rule-aware scan — untested and not attempted in this research
  (`CL-HSAPI-006`).
- Handling the two grammar-valid-but-unobserved shapes (same-line
  trailing comment; named-constructor-subset export) with dedicated
  logic in a first version, absent real evidence from this corpus that
  they occur (`EV-HSAPI-011`) — see §14 decision 6.
- AI-based or heuristic "guess the purpose" fallback when no Haddock
  comment is found — `purpose: None` is treated as a correct, expected
  outcome (`CL-HSAPI-004`), not a gap to be papered over.

## 14. Acceptance criteria (proposed, pending review)

These are drafted directly from the Claims above, not yet ratified as
Requirements — no Decision record exists for this feature yet:

- A comment-stripping, identifier-tokenising scan of a real export
  list reproduces the exact exported-name set GHC's own `:browse`
  confirms, for both comma styles, `Type(..)` expansion, and
  commented-out-entry exclusion (`CL-HSAPI-001`).
- Each detected `module <Name>` entry is recorded as occurring (and,
  where file-locally resolvable via an `import ... as <Name>` line,
  which real modules it covers in this file) without the extractor
  silently asserting a flattened, fully-resolved name list it cannot
  actually derive (`CL-HSAPI-002`).
- A CPP conditional inside an export list's own parentheses does not
  cause the extractor to silently assert a name is exported or
  silently drop it without any signal — the affected entry is
  flagged, not guessed (`CL-HSAPI-003`).
- Purpose-pairing correctly reflects body-location doc comments rather
  than export-list order, including correctly returning `purpose:
  None` for an exported name with no doc comment at its own
  definition site (`CL-HSAPI-004`).
- A module with no export list at all is correctly detected as such
  (no false positive/negative against the 147-module discriminator
  sample) even if its top-level bindings are not enumerated in this
  version (`CL-HSAPI-006`).

## 15. Open decisions for review

No Decision or Requirement record exists yet for this feature — the
six open questions below are presented for the project owner's review,
each with a recommended answer and its reasoning, mirroring
`doc-origin-pinned-reference/design.md`'s own worked precedent for this
section.

1. **How far should the extractor resolve `module <Name>` re-export
   entries?** (`CL-HSAPI-002`) — Options: (a) fully opaque: record only
   that a re-export entry occurred, with no attempt to name what it
   covers; (b) file-local partial resolution: additionally match the
   entry against this same file's own `import ... as <Name>` lines
   when the alias case applies, but never follow into another file;
   (c) full cross-file/cross-package expansion. **Recommended: (b).**
   Reasoning: (c) is explicitly beyond a no-full-parser, per-file
   scanner's scope (`CL-HSAPI-002`), while (a) discards a
   genuinely file-local, cheap piece of information (the alias's own
   `import` lines are already being read in the same pass) that
   materially improves the recorded surface for the common alias
   case (`Hledger.hs`, `Hledger/Cli/Script.hs`) at no cross-file cost.

2. **How should a CPP-gated export-list entry be handled?**
   (`CL-HSAPI-003`) — Options: (a) always treat as exported
   (over-approximation); (b) always skip (under-approximation); (c)
   flag as undetermined. **Recommended: (c).** Reasoning: both (a) and
   (b) produce a confident-looking but sometimes-silently-wrong
   result with no signal to a consumer that anything was uncertain;
   (c) is the only option consistent with this project's own "an
   honest gap is more useful than a confident-looking guess" governing
   rule, at the cost of leaving one field undetermined for a
   confirmed-rare real case (one instance found in this corpus,
   `OBS-HSAPI-011`/`OBS-HSAPI-012`).

3. **Should the extractor implement the package-level
   `exposed-modules` filter?** (`CL-HSAPI-005`) — Options: (a) implement
   it (parse `package.yaml`/`.cabal`, exclude non-exposed modules
   before per-file scanning); (b) skip it for v1, since this reference
   corpus cannot demonstrate it changes anything. **Recommended: (a).**
   Reasoning: the mechanism is real, cheap to parse (already a planned
   package-manifest read), and the fact that hledger-lib/hledger happen
   not to exercise it is an honestly-disclosed property of *this*
   reference corpus, not evidence the mechanism is unneeded for other
   Haskell packages a user might point the adapter at — implementing
   it now avoids a silent correctness gap for exactly the packages
   this corpus didn't happen to test.

4. **Should the extractor attempt to enumerate top-level bindings for
   export-list-free modules?** (`CL-HSAPI-006`) — Options: (a) attempt
   a coarse, untested layout-heuristic fallback; (b) detect the
   condition reliably but do not enumerate — return an empty symbol
   list plus a diagnostic marker for such files in v1.
   **Recommended: (b).** Reasoning: no heuristic was built or tested
   against a real no-export-list file's own actual bindings in this
   research (`CL-HSAPI-006`); shipping an untested heuristic risks
   exactly the "confident-looking guess" this project's governing
   rules warn against, whereas a reliable detect-but-decline is honest
   and matches this feature's own "minimal first version" framing.
   This form is real (17 instances) but never occurs inside hledger-lib
   itself, so declining it does not silently degrade the primary
   target corpus's own coverage.

5. **Should the two-pass purpose-pairing algorithm be built in this
   first version, or should `purpose` be `None` for every Haskell
   symbol in v1?** (`CL-HSAPI-004`) — Options: (a) implement the
   two-pass algorithm now; (b) defer it, shipping `purpose: None`
   uniformly for v1 and revisiting later. **Recommended: (a).**
   Reasoning: the algorithm's shape is already fully determined by
   confirmed evidence (`CL-HSAPI-004`/`DE-HSAPI-004`) — there is no
   remaining research uncertainty to defer against, only an
   implementation-size trade-off, and a purpose field is a real part
   of this feature's own stated shape (mirroring the Rust adapter's
   `Symbol.purpose`).

6. **Should the extractor add explicit handling now for the two
   grammar-valid, zero-observed-instance shapes (same-line trailing
   comment; named-constructor-subset export)?** (`EV-HSAPI-011`) —
   Options: (a) add handling pre-emptively; (b) leave unhandled until
   real evidence of occurrence surfaces. **Recommended: (b).**
   Reasoning: this project's own "smallest useful move" / "favour
   empirical discovery over speculative architecture" discipline
   (`planning/phase-54c-evidence-knowledge-workflow.md` §0) argues
   against building for shapes with zero confirmed real instances
   across the entire sampled corpus; revisit if a future corpus (or a
   future hledger revision) is found to use either shape.
