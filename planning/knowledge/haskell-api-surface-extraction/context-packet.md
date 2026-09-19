# Context packet: Haskell public API-surface extraction (`codecompass-adaptor-haskell`)

Feature: `haskell-api-surface-extraction` | Related phase: Phase 60
(`codecompass-adaptor-haskell`, minimal external Haskell adapter) |
Design: `design.md` (`status: RESEARCHED`) | Decision: `DEC-HSAPI-001`
(`status: approved`, approved by "project owner (lead standing in for
this dogfooding run)")

This packet is a compacted implementation input, not a copy of
`design.md`. It is deliberately smaller — read `design.md` (and, where
named below, the real pinned hledger source) only if this packet turns
out to be insufficient, and log the gap in `packet-sufficiency.md`.

**Where this code actually lives**: `codecompass-adaptor-haskell` is a
**separate repository** (checked out locally as the `adapters/haskell`
git submodule of `codecompass`), not part of `src/codecompass/`. The
scanner this packet describes is Haskell code, most naturally living
under that repository's own `app/Main.hs` (or a module it imports) —
**never** Python, and never `src/codecompass/`. `src/codecompass/`
already contains the *host*-side stub that invokes this adapter as an
opaque subprocess (`src/codecompass/adapters/haskell.py`); that file is
out of scope for this packet's own implementation work, but §6/§7 below
name it because its existing behavior fixes constraints (especially the
wire shape, §11) this packet's own implementer cannot renegotiate.

## 1. Goal

CodeCompass's Rust/Cargo adapter has `extract_rust_symbols`
(`src/codecompass/symbols.py`), a small, mechanical, no-AI, no-full-parser
scanner that produces a public API surface (symbol name + optional
one-line purpose) from `pub ...`-prefixed declarations. The Haskell
adapter needs its own equivalent, scanning `.hs` source files in a
pinned real reference corpus — hledger-lib and its sibling packages
(hledger, hledger-ui, hledger-web), checked out at
`/home/cormac/projects/hledger/`, pinned commit
`33fa849e7ae841968bd21c427094c4fb4a4ec38d` — to identify each module's
genuinely public names (governed by the module's own export list) and,
within a package, which modules are exposed at all (governed by the
package's own `exposed-modules`/hpack manifest). (`OBS-HSAPI-001`,
`EV-HSAPI-001`)

## 2. Approved semantics (compacted)

- **Baseline mechanism, compiler-verified**: a comment-stripping,
  identifier-tokenising scan over the text strictly between
  `module <Name> (` and that module's own `where` correctly and
  completely handles bare comma-separated identifiers (both leading- and
  trailing-comma style), `Type(..)` (expands to the type **and every
  real data constructor**), Haddock `-- * Section` grouping headers (no
  identifier — skip), and whole-line `--`-commented-out disabled entries
  (exclude). This was checked against real GHC behavior, not just
  inferred from text: a naive comment-aware scan over `AccountName.hs`
  produced the exact same 48-name set as `stack ghci`'s own `:browse`
  output (correctly excluding the one commented-out name), and
  `Query(..)`/`OrdPlus(..)`/`QueryOpt(..)` were confirmed via `:browse`
  to expand to all 18/10/3 real constructors respectively.
  (`CL-HSAPI-001`, `DE-HSAPI-001`, `EV-HSAPI-002/003/007/008`)
- **`module <Name>` re-export entries get file-local partial resolution,
  never cross-file expansion.** Four distinct real resolution shapes
  exist (unaliased other module named directly; an `import ... as
  <Name>` alias covering one or many real modules; another package's own
  aggregation module named directly; a self-re-export of the current
  module's own name) and no single strategy covers all four from one
  line's text alone. **Decided** (`DEC-HSAPI-001` item 1, design.md §15.1
  option b): record that a `module <Name>` entry occurred; additionally,
  when `<Name>` matches this same file's own `import ... as <Name>`
  line(s), record which real module(s) that alias covers **in this
  file**; never read another file to resolve it further.
  (`CL-HSAPI-002`, `DE-HSAPI-002`, `EV-HSAPI-005/009/010`)
- **A CPP conditional inside an export list's own parentheses must be
  flagged undetermined, never silently guessed.** Confirmed real (one
  instance: `Hledger/Data/Types.hs` gates `Year` behind
  `#if MIN_VERSION_time(1,11,0)` / `#endif`, only meaningful because
  `{-# LANGUAGE CPP #-}` is active for that file). A pure text scanner
  cannot evaluate the condition (it depends on an external package
  version the `.hs` file's own text doesn't state). **Decided**
  (`DEC-HSAPI-001` item 2, design.md §15.2 option c): flag the
  enclosed entry/entries as undetermined — never (a) always-exported nor
  (b) always-dropped. (`CL-HSAPI-003`, `DE-HSAPI-003`, `EV-HSAPI-009`)
- **The package-level `exposed-modules` filter is implemented, not
  skipped**, despite this specific reference corpus not being able to
  demonstrate it changes anything (every real, hand-authored module in
  both `hledger-lib.cabal` and `hledger.cabal` happens to already be
  exposed; only `Setup.hs` and generated `Paths_*`/`PackageInfo_*`
  modules are excluded). **Decided** (`DEC-HSAPI-001` item 3, design.md
  §15.3 option a): before per-file scanning, resolve the package's own
  exposed-module set (explicit `exposed-modules:` in the generated
  `.cabal`, or hpack's own default — "all modules in source-dirs less
  other-modules" — when `package.yaml` states no explicit list) and
  scan only modules in that set. (`CL-HSAPI-005`, `DE-HSAPI-005`,
  `EV-HSAPI-006`)
- **A module with no export list at all (`module Foo where`, no `(`
  before `where`) is real** (17 confirmed instances across the wider
  pinned checkout, zero inside hledger-lib's own 65 modules) and means
  every top-level name is exported. Detecting its absence is a cheap,
  reliable discriminator (checked with zero false positives/negatives
  across a 147-module real sample). **Decided** (`DEC-HSAPI-001` item 4,
  design.md §15.4 option b): detect this case reliably, but do **not**
  attempt to enumerate the module's top-level bindings in this version —
  no fallback heuristic was built or tested, and Haskell's layout rule
  (not a single-token marker like Rust's `pub`) makes that materially
  harder than the export-list-present case. Report zero symbols plus one
  diagnostic for such a module. (`CL-HSAPI-006`, `DE-HSAPI-006`,
  `OBS-HSAPI-005`)
- **Purpose-pairing needs its own two-pass algorithm — the Rust
  adapter's single forward scan does not transfer.** Haskell decouples
  *where a name is declared exported* (the header export list, which
  itself carries no attached per-item doc text) from *where that name's
  documentation lives* (a `-- | ...` Haddock comment immediately
  preceding that name's own definition, elsewhere in the file body, in
  body order, not export-list order) — confirmed directly:
  `AccountName.hs` lists `accountLeafName` **first** in its export list,
  but its own definition (no preceding Haddock comment at all) appears
  in the body **after** two later-listed exports' own, documented
  definitions. **Decided** (`DEC-HSAPI-001` item 5, design.md §15.5
  option a): build the two-pass algorithm now (pass 1: collect exported
  names from the header per the baseline scan; pass 2: walk the file
  body once, and for each exported name, record the nearest preceding
  `-- | ...` comment at that name's own definition site). `purpose: null`
  for a name with no such comment is a correct, expected outcome, not a
  bug. (`CL-HSAPI-004`, `DE-HSAPI-004`, `EV-HSAPI-002/003`)
- **No handling is added for two grammar-valid-but-zero-observed shapes**
  (a same-line trailing comment after an identifier; a
  named-constructor-subset export, `Type(Ctor1, Ctor2)`, as opposed to
  full `Type(..)`) — both were searched for across hledger-lib, hledger,
  hledger-ui, and hledger-web and found nowhere. **Decided**
  (`DEC-HSAPI-001` item 6, design.md §15.6 option b): leave unhandled
  until real evidence of occurrence surfaces. (`OBS-HSAPI-013`,
  `EV-HSAPI-011`)

## 3. Requirements (verbatim, all `status: pending`, all under `DEC-HSAPI-001`)

**REQ-HSAPI-001**
> codecompass-adaptor-haskell's export-list scanner MUST, for the
> baseline shapes (bare identifiers in either leading- or trailing-comma
> style, `Type(..)` all-constructors expansion, Haddock `-- * Section`
> grouping headers, and whole-line commented-out entries), produce
> exactly the exported-name set a real GHC `:browse` would report for
> that module — comment-stripping and tokenising the export-list span
> between `module <Name> (` and its own `where`.

**REQ-HSAPI-002**
> When the scanner encounters a `module <Name>` entry inside an export
> list, it MUST record that a re-export entry named `<Name>` occurred,
> and MUST NOT assert a flattened, fully-resolved list of real exported
> names for it. If `<Name>` matches this same file's own
> `import ... as <Name>` line, the scanner additionally records which
> real module(s) that alias covers in this file. No cross-file read is
> performed to resolve any `module <Name>` entry.

**REQ-HSAPI-003**
> If a `#if`/`#endif` (or other CPP conditional directive) span appears
> within an export list's own parentheses, the scanner MUST flag the
> entry/entries enclosed by that span as undetermined rather than
> silently treating them as exported or silently dropping them.

**REQ-HSAPI-004**
> Before scanning any module's own export list, the adapter MUST
> determine whether that module is part of the package's own exposed
> surface (an explicit `exposed-modules` list in the generated `.cabal`,
> or hpack's own "all modules in source-dirs less other-modules" default
> when no explicit list is present). A module not in the package's
> exposed set MUST NOT contribute any symbols to the reported API
> surface, regardless of what its own export list says.

**REQ-HSAPI-005**
> The scanner MUST reliably detect a module with no export list at all
> (`module <Name> where`, with no `(`-delimited list before `where`) as
> a distinct case, without false positives or false negatives, but MUST
> NOT attempt to enumerate that module's top-level bindings in this
> version — such a module contributes zero symbols plus one diagnostic
> noting the undetermined-surface condition.

**REQ-HSAPI-006**
> Purpose-pairing MUST use a two-pass algorithm: pass 1 collects the
> exported-name set from the module header (per REQ-HSAPI-001); pass 2
> walks the file body once and, for each exported name, records the
> nearest preceding `-- | ...` Haddock comment at that name's own
> definition site, independent of the name's position in the export
> list. An exported name with no such comment at its definition site
> MUST be reported with `purpose: null`, which is a correct, expected
> outcome, not an error condition.

## 4. Behavioural examples (verbatim, Given/When/Then)

**REQ-HSAPI-001's example:**
```
Given hledger-lib/Hledger/Data/AccountName.hs's real export list
  (leading-comma style, one commented-out entry)
When the scanner runs over it
Then it produces the same 48-name set `stack ghci`'s own `:browse
  AccountName` confirms, correctly excluding the commented-out name.
```

**REQ-HSAPI-002's example:**
```
Given hledger-lib/Hledger.hs's `module X` entry, where `X` is a
  file-local alias (via `import ... as X`) for five real imports
When the scanner encounters this entry
Then it records a re-export occurrence named `X` plus the five real
  module names `X` aliases in this file, without attempting to expand
  `X` into a flat list of the real names those five modules export.
```

**REQ-HSAPI-003's example:**
```
Given hledger-lib/Hledger/Data/Types.hs's export list, where `Year`
  sits inside a `#if MIN_VERSION_time(1,11,0)` / `#endif` span
When the scanner processes this export list
Then `Year` is reported with an undetermined/flagged status rather
  than being silently included in or silently omitted from the
  confirmed exported-name set.
```

**REQ-HSAPI-004's example:**
```
Given a package whose package.yaml declares no explicit
  exposed-modules (hpack default: all source-dir modules except
  other-modules), and hledger-lib's own real other-modules exclusions
  (Setup.hs, generated Paths_*/PackageInfo_* files)
When the adapter analyzes the package
Then Setup.hs and any generated Paths_*/PackageInfo_* module
  contribute no symbols, and every other real source module does.
```

**REQ-HSAPI-005's example:**
```
Given a module written as `module Foo where` with no parenthesised
  export list
When the scanner processes this module
Then it is detected as an export-list-free module (matching the
  147-module real-corpus discriminator with zero false
  positives/negatives) and reported with an empty symbol list plus a
  diagnostic, never a guessed enumeration of its top-level bindings.
```

**REQ-HSAPI-006's example:**
```
Given AccountName.hs, where `accountLeafName` is listed first in the
  export list but its own definition (no preceding Haddock comment)
  appears in the body after `accountNameComponents`/
  `accountNameFromComponents` (listed second/third, each with real
  Haddock text at their own definition sites)
When the scanner runs its two-pass algorithm
Then `accountLeafName` is reported with `purpose: null` and the other
  two are reported with their own real Haddock text, matching body
  location rather than export-list order.
```

## 5. Invariants

- The baseline scan never needs a full Haskell parser or the GHC API —
  a comment-stripping, identifier-tokenising pass over the export-list
  span is sufficient for every baseline shape, compiler-verified.
  (`REQ-HSAPI-001`, `CL-HSAPI-001`)
- `module <Name>` entries are **never** expanded across files, even when
  a same-file `import ... as <Name>` resolves the alias to real module
  names. (`REQ-HSAPI-002`, `CL-HSAPI-002`)
- A CPP-gated export-list entry is **never** silently included or
  silently dropped — it is always flagged. (`REQ-HSAPI-003`,
  `CL-HSAPI-003`)
- A module outside the package's own exposed-module set contributes
  **zero** symbols, regardless of its own export list's content.
  (`REQ-HSAPI-004`, `CL-HSAPI-005`)
- An export-list-free module is detected, never guessed-enumerated, in
  this version. (`REQ-HSAPI-005`, `CL-HSAPI-006`)
- Purpose is paired by body-definition location, never by export-list
  adjacency; `purpose: null` is a correct, common, expected result, not
  a failure signal. (`REQ-HSAPI-006`, `CL-HSAPI-004`)
- No AI/heuristic guess ever fills in for an undetermined case (CPP gate,
  no-export-list enumeration, unresolved `module <Name>`) — every one of
  these is disclosed, not smoothed over. (`design.md` §13, `DEC-HSAPI-001`
  rationale)

## 6. Relevant architecture (pointers, not an essay)

- **The Rust/Cargo adapter's own precedent**, the closest existing
  analogue in shape and scope (single-pass, mechanical, no-AI,
  no-full-parser): `extract_rust_symbols` in `src/codecompass/symbols.py`
  (not part of this packet's own implementation surface, but the
  standard this feature is held to). (`EV-HSAPI-001`)
- **The external-process adapter architecture**
  (`decisions/0057-external-process-adapter-protocol.md`,
  `decisions/0058-adapter-protocol-and-haskell-adapter-as-separate-repositories.md`,
  `architecture/overview.md`'s "External adapters" section): the
  Haskell scanner runs as an independent subprocess of
  `codecompass-adaptor-haskell`, speaking the JSON-Lines protocol
  defined by the separate `codecompass-adaptor-protocol` repository
  (checked out at `protocol/codecompass-adaptor-protocol/` in this
  repository) — never imported into, and never importing from,
  `src/codecompass/`.
- **The wire contract this scanner's output MUST fit** — see §11
  below; this is the single most load-bearing architecture pointer for
  this packet, since none of `design.md`'s Requirements were derived
  with this schema in view.
- **File-local, two-pass scanner structure** (design.md §6): pass 1
  walks the module header/export-list span (comment-stripping,
  tokenising) to produce the raw exported-name set; pass 2 walks the
  whole file body once and, per exported name, records the nearest
  preceding `-- | ...` comment at that name's own definition site. This
  is a structurally different shape from the Rust adapter's single
  forward scan, not a drop-in port of it.
- **Package-manifest read is a prerequisite of correct scope, not an
  optional enrichment** (design.md §5): which `.hs` files are even
  candidates for scanning depends on the package's own
  `exposed-modules` (or hpack default), resolved once per package,
  before any per-file scan.

## 7. Relevant symbols / files / dependencies

**Reference corpus (read-only; the scanner is validated against this,
but ships independent of it)** — checked out locally at
`/home/cormac/projects/hledger/`, pinned commit
`33fa849e7ae841968bd21c427094c4fb4a4ec38d`:

- `hledger-lib/Hledger/Query.hs:1-79` — export list lines 13-78 (65
  lines): trailing-comma bare identifiers, `Query(..)`/`QueryOpt(..)`
  (lines 15-16), six `-- * Section` Haddock headers (lines 14, 21, 27,
  32, 50, 58, 74), one whole-line commented-out entry
  (`-- patternsMatchTags,`, line 72). (`OBS-HSAPI-002`)
- `hledger-lib/Hledger/Data/AccountName.hs:1-230` — export list lines
  11-62 (leading-comma style, 48 live entries), one commented-out entry
  in the same leading-comma shape (`--  ,isAccountRegex`, line 45); body:
  `accountLeafName` listed first (line 12) but defined at line 144 with
  no preceding Haddock comment, while `accountNameComponents`/
  `accountNameFromComponents` (listed 2nd/3rd) are defined earlier, at
  lines 138/141, each with real `-- | ...` text; other documented
  definitions at lines 95, 106, 119, 147, 157, 169, 192, 197, 204, 216.
  (`OBS-HSAPI-003`) — **the canonical fixture for both REQ-HSAPI-001 and
  REQ-HSAPI-006**.
- `hledger-lib/Hledger.hs:22-33` — `module X` where `X` is an
  `import ... as X` alias for five modules
  (`Hledger.Data`/`Hledger.Read`/`Hledger.Reports`/`Hledger.Query`/
  `Hledger.Utils`, lines 29-33). (`OBS-HSAPI-006`) — **the canonical
  fixture for REQ-HSAPI-002's aliased case.**
- `hledger-lib/Hledger/Data/Types.hs:29-34` — export list:
  `module Hledger.Data.Types,` (self-re-export) then
  `#if MIN_VERSION_time(1,11,0)` / `Year` / `#endif`. (`OBS-HSAPI-011`)
  — **the canonical fixture for REQ-HSAPI-003, and a second real case
  for REQ-HSAPI-002's self-re-export shape.**
- `hledger-lib/Hledger/Utils.hs:1-75` (lines 8-69: six unaliased
  `module Hledger.Utils.*` re-exports, matched by plain `import
  Hledger.Utils.*` lines 91-97, no `as`); `hledger/Hledger/Cli.hs:83-99`
  (mixes bare names, a section header, six unaliased re-exports, one
  whole-other-package re-export of `Hledger`, and one aliased
  `module CmdArgsWithoutName`, all in the same list);
  `hledger/Hledger/Cli/Script.hs:1-20` (entire export list is
  `( module M )`, `M` aliasing a dozen+ imports). (`OBS-HSAPI-012`) —
  **the canonical multi-shape-in-one-list fixture; do not assume a file
  uses only one `module <Name>` resolution shape.**
- `hledger/Hledger/Cli/Commands/Activity.hs:9-10`
  (`module Hledger.Cli.Commands.Activity` / `where`, no `(`) and
  `hledger-ui/Hledger/UI/UITypes.hs:41`
  (`module Hledger.UI.UITypes where`) — two directly-confirmed
  genuine no-export-list modules, out of 17 found across the wider
  checkout (list of all 17 in `OBS-HSAPI-005`'s `raw_result`) — **none
  inside hledger-lib's own 65 modules**, so a scanner validated only
  against hledger-lib alone never exercises REQ-HSAPI-005's path.
  (`OBS-HSAPI-004`, `OBS-HSAPI-005`)
- `hledger-lib/hledger-lib.cabal:54-125` (65 `exposed-modules`; only
  `Setup`, `Paths_hledger_lib`, `PackageInfo_hledger_lib` excluded, the
  latter two only appearing under `.stack-work` build output, not real
  source) and `hledger-lib/package.yaml:122` (hpack default comment);
  `hledger/hledger.cabal:104-190` (40 `exposed-modules` under
  `Hledger.Cli.*`; only `Paths_hledger` excluded) — the two real
  manifests to validate REQ-HSAPI-004 against. (`OBS-HSAPI-007`,
  `OBS-HSAPI-008`)
- Zero real instances anywhere in hledger-lib/hledger/hledger-ui/
  hledger-web of a same-line trailing comment after an identifier, or a
  named-constructor-subset export (`Type(Ctor1, Ctor2)`) — confirmed by
  two targeted whole-repository greps, not merely "not noticed."
  (`OBS-HSAPI-013`)
- **Independent compiler ground truth**: `stack ghci hledger-lib:lib`
  (stack 3.11.1, GHC 9.12.4, resolver lts-24.59) + `:browse
  Hledger.Data.AccountName` (48 bindings, confirms `isAccountRegex`
  absent) and `:browse Hledger.Query` (confirms `Query`/`OrdPlus`/
  `QueryOpt` expand to 18/10/3 real constructors respectively) — the
  exact commands and full `:browse` output are in `OBS-HSAPI-009`/
  `OBS-HSAPI-010`'s own `raw_result` fields; re-run these directly
  against the pinned checkout to re-derive the same ground truth rather
  than trusting this packet's paraphrase.

**Target repository / host-side integration:**

- `codecompass-adaptor-haskell` (external repo, checked out as the
  `adapters/haskell` git submodule) — this scanner's own implementation
  home, most naturally under `app/Main.hs` or a module it imports. No
  file in that repository exists yet; nothing here should be read as
  naming an established internal structure to preserve.
- `src/codecompass/adapters/haskell.py` — the **host-side** stub, already
  written (uncommitted in this working tree). Its `readme_and_api_surface`
  method already consumes the wire response by reading
  `entry["name"]`, `entry.get("purpose")`, `entry["module"]` per symbol
  entry — i.e. the 3-field wire shape (§11) is not speculative, it is
  already relied upon by real, if currently uncommitted, host code.
  `_analyze()`/`_adapter_executable()` show the executable is expected
  to be named `codecompass-adaptor-haskell-exe`, resolved via
  `stack path --local-install-root` inside `adapters/haskell/`.
- `src/codecompass/adapters/external_process.py` — the generic JSON-Lines
  client (`initialize`/`analyze_project`/`shutdown`, one outstanding
  request at a time); `CAPABILITIES = ("dependencies", "symbols",
  "observations", "diagnostics")`, `PROTOCOL_VERSION = 1`. Confirms the
  adapter must declare `"symbols"` in its own `initialize` response's
  `capabilities` array to have its `symbols` output honored at all.
- `protocol/codecompass-adaptor-protocol/SCHEMA.md` and
  `schemas/analyze_project-response.json` — the **canonical wire
  contract** (§11). Read this directly; it is the one piece of context
  this packet cannot faithfully compact further without losing
  precision.
- `docs/external-adapters.md` — build/clone instructions
  (`cd adapters/haskell && stack build`), and the version-compatibility
  matrix this feature's release should extend.

## 8. Existing tests

**None exist yet for this feature specifically** — `codecompass-adaptor-haskell`
is unwritten. Two categories of pre-existing test material are relevant:

- `protocol/codecompass-adaptor-protocol/conformance/valid/analyze_project-response-full.json`
  and `.../schemas/analyze_project-response.json` — an adapter's own
  `symbols`/`diagnostics`/`observations` output can be validated against
  these directly (structurally, not semantically) as a first conformance
  check, independent of this feature's own Haskell-specific correctness.
- On the CodeCompass (Python) host side, `tests/test_adapter_haskell.py`
  and `tests/test_adapters_external_process.py` already exist
  (uncommitted in this working tree) exercising `HaskellAdapter`/
  `ExternalAdapterProcess` against a fake adapter process
  (`tests/fixtures/fake_adapter.py`) — these do not test this packet's
  own Haskell-side scanning logic, but do fix the host-side contract
  (§11) this packet's own output must satisfy to be usable at all;
  worth reading before finalizing the wire-shape approach for the
  outstanding questions in §11/§12.
- No Haskell-side test framework, fixture convention, or test file has
  been chosen yet — this is itself a §12 open question, not an oversight
  of this packet.

## 9. Non-goals

- A full Haskell parser or a GHC-API-backed extractor.
- Evaluating CPP conditionals for real (would require knowing the target
  build's actual dependency versions).
- Full cross-file/cross-package expansion of `module <Name>` re-export
  entries.
- Enumerating top-level bindings for export-list-free modules via a
  layout-rule-aware scan — untested, not attempted in this version.
- Handling the two grammar-valid-but-unobserved shapes (same-line
  trailing comment; named-constructor-subset export) with dedicated
  logic in a first version, absent real evidence from this corpus that
  they occur.
- AI-based or heuristic "guess the purpose" fallback when no Haddock
  comment is found — `purpose: null` is the correct, expected outcome,
  not a gap to paper over.

(`design.md` §13)

## 10. Deliberate upstream differences

Not a target-vs-upstream divergence in the `hledger depth:` sense
(there, a re-implementation's own chosen behavior vs. hledger's real
computed output). Here, "upstream" is GHC's own real, complete
resolution of a module's visible surface (confirmed via `:browse`), and
the adapter's approved behavior is a deliberate, disclosed **partial
mechanical approximation** of it, not a full reimplementation:

- The adapter will not evaluate CPP conditionals the way GHC's own
  `-XCPP` pass does — it flags affected entries as undetermined instead.
  (`CL-HSAPI-003`)
- The adapter will not fully expand `module <Name>` re-exports across
  files the way GHC's own module system does. (`CL-HSAPI-002`)
- The adapter will not enumerate top-level bindings for
  export-list-free modules the way GHC's own layout-aware parser does.
  (`CL-HSAPI-006`)

Each is an intentional scope limit of a no-AI, no-full-parser extractor
(matching the Rust adapter's own precedent tier), not a claim that GHC's
own real resolution differs from what the research found it to be.
(`design.md` §12)

## 11. Unresolved questions (honestly disclosed)

- **The wire-protocol mapping for REQ-HSAPI-002/003/005's richer output
  was never addressed by any record in this knowledge base, and this is
  the single most important gap in this packet.** The actual wire
  contract the adapter must emit through
  (`protocol/codecompass-adaptor-protocol/schemas/analyze_project-response.json`)
  fixes `symbols` as a flat array of exactly
  `{"name": string, "purpose": string|null, "module": string}` — no
  field for "this is a re-export occurrence, not a concrete exported
  name" (REQ-HSAPI-002), no field for "this entry's exported status is
  undetermined" (REQ-HSAPI-003), and the `diagnostics` array is only
  `{"severity": "warning"|"error", "message": string}` — free text, with
  no structured module/name reference (relevant to REQ-HSAPI-003's
  per-entry flag and REQ-HSAPI-005's per-module diagnostic). No
  Observation, Evidence, Claim, or Requirement in this knowledge base
  ever inspected this schema — the research was conducted entirely from
  the Haskell-source side. **This must be resolved before or during
  implementation, not guessed**: candidate resolutions (not yet decided
  by anyone) include (a) synthesizing a `symbols` entry with a marker
  convention in `purpose` (e.g. a `[re-export: ...]`/`[undetermined]`
  prefix) or a dedicated field name outside the current schema (a
  protocol change, out of scope for a first version), or (b) routing
  all of this via free-text `diagnostics` messages that embed the
  module/name themselves. Whichever is chosen, it changes what a
  conformant `analyze_project` response actually looks like for a real
  hledger-lib-shaped package — resolve this with the protocol's own
  maintainer view in mind (`decisions/0057`/`0058`), not unilaterally
  inside the adapter alone, since `src/codecompass/adapters/haskell.py`'s
  own parsing of the response (§7) has to agree with whatever is chosen.
- **Frontmatter/manifest-parsing mechanism is unspecified** (mirroring
  `doc-origin-pinned-reference`'s own equivalent open question): no
  record says whether to use an existing Haskell YAML-parsing library
  for `package.yaml`, a hand-rolled `.cabal`/`package.yaml` key scan, or
  something else. `REQ-HSAPI-004`'s observable contract (which modules
  get scanned) is unambiguous either way — this is an implementation
  choice, not a behavioural ambiguity.
- **No decision exists on the exact tokenising algorithm's implementation
  form** (regex vs. hand-rolled character scan vs. a minimal Haskell
  lexer library) — `CL-HSAPI-001`'s own verification used a scratch
  Python regex script, not a Haskell implementation; "comment-stripping
  and tokenising" is confirmed **sufficient in scope**, not prescribed
  as a specific algorithm/library choice. See `packet-sufficiency.md`
  for why this matters for a first-attempt implementation.
- **No test fixture files exist yet.** Every real file citation in §7 is
  a pointer into the live, pinned hledger checkout, not a materialized
  fixture inside `codecompass-adaptor-haskell`'s own test tree — deciding
  whether to vendor small excerpts as fixtures or read the pinned
  checkout directly in tests is unresolved.
- **No record addresses what happens when the pinned hledger checkout is
  unavailable** (e.g. CI without network access to clone it, or a
  contributor who hasn't fetched it) — out of scope for this
  knowledge base, but a real implementation-time question.

## 12. Provenance references

Every id this packet draws from:

- **Observations:** OBS-HSAPI-001 through OBS-HSAPI-013 (all)
- **Evidence:** EV-HSAPI-001 through EV-HSAPI-011 (all)
- **Claims:** CL-HSAPI-001, CL-HSAPI-002, CL-HSAPI-003, CL-HSAPI-004,
  CL-HSAPI-005, CL-HSAPI-006
- **Derivations:** DE-HSAPI-001 through DE-HSAPI-006 (all)
- **Decision:** DEC-HSAPI-001
- **Requirements:** REQ-HSAPI-001, REQ-HSAPI-002, REQ-HSAPI-003,
  REQ-HSAPI-004, REQ-HSAPI-005, REQ-HSAPI-006
- **Related phase plan/architecture (not part of the knowledge base, but
  load-bearing per §11):** `decisions/0057`, `decisions/0058`,
  `protocol/codecompass-adaptor-protocol/SCHEMA.md`,
  `protocol/codecompass-adaptor-protocol/schemas/analyze_project-response.json`,
  `docs/external-adapters.md`
