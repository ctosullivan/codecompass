# Phase 60: Minimal Haskell adapter — plan

**Status:** plan only, not started. Do not begin implementation until
this plan is reviewed — per this project's own established "write the
plan first" discipline (`CLAUDE.md` §1).

**Amended 2026-09-19** (direct user instruction, before implementation
began — the original in-process version is preserved below at §A for
reference, never deleted, per this project's own "retarget, don't
delete" convention): the Haskell adapter is no longer an in-process
Python class. It is now the **reference implementation of a genuinely
external adapter** — a separate OS process, communicating over a small,
versioned, JSON-based protocol (`decisions/0057`, new this amendment) —
validating that CodeCompass's core never needs to import
ecosystem-specific implementation code for a new adapter, motivated by a
real future case named directly: a potentially proprietary COBOL/
mainframe adapter suite that could never ship as importable GPL Python
code inside `src/codecompass/`. The behavioural goals (§0-§1, §4's own
open design question, the monorepo/testing scope) are preserved; the
*mechanism* changes throughout §2 onward.

## 0. Why this phase, and why now

Stage F (`decisions/0056`) retargeted CodeCompass's remaining
cross-project validation from Technical Clipper (a same-ecosystem
regression check — npm is already shipped) to a genuinely new ecosystem
adapter, on the theory that a fourth real `EcosystemAdapter`
implementation is a stronger test of `decisions/0002`'s own claim
("adding an ecosystem later means writing a new adapter from scratch's
own native tooling, not extending a generic parser") than a regression
check ever could be. Phase 54b independently strengthened the case for
choosing Haskell/hledger specifically: it is CodeCompass's single most
evidence-rich reference target (six phases of real Ledgerkit work), and
Phase 54b's own retro named a concrete, still-open design question for
this exact phase (§5 below). Phase 60 is the next unstarted phase on
Stage F's sequence, gated on nothing (Stage F is a separate axis from
Stage E/GATE DD, per `decisions/0056`).

**This amendment adds a second "why now":** `decisions/0002`'s own
in-process, native-tooling adapter strategy has an unstated assumption —
every adapter's own logic can live as importable GPL-licensed Python
code inside CodeCompass's own process. That assumption holds for npm/
Python/Cargo; it may never hold for a real future proprietary or
differently-licensed ecosystem (COBOL/mainframe named directly). Phase
60 is the first real, concrete opportunity to build and test the
alternative — a genuinely external adapter — against a real toolchain
and a real, evidence-rich target, rather than designing it speculatively
for a hypothetical future ecosystem with no adapter to actually run yet.

## 1. Current-state inspection (real, re-verified this session)

**Toolchain — confirmed available, unlike Cargo's still-open gap
(`decisions/0014`):**
```
$ stack --version
Version 3.11.1, Git revision 979bf6339fd..., aarch64 hpack-0.39.6
```
This is the exact toolchain that already built the pinned hledger binary
this project has used since Phase 54 (`/home/cormac/.local/bin/hledger`,
`1.52.4-g33fa849e7-...`). `ghc`/`cabal` are not directly on `PATH` —
`stack` manages them internally.

**Real manifest format, inspected directly** (`hledger-lib/package.yaml`,
hpack format — the same file this project already read during Phase 54):
plain YAML, top-level `name`/`version`/`license`/`maintainer`/
`dependencies` keys — directly analogous to `package.json`/
`pyproject.toml`'s own shape.

**Real dependency-tree command, checked live against the real hledger
project:**

- `stack ls dependencies` produces a **flat, plain-text** list
  (`NAME VERSION`, one per line, alphabetically sorted, deduplicated) —
  **no JSON output mode exists** (`--help` confirms no `--json`/
  `--format` flag).
- `stack dot --external` produces a real GraphViz DOT graph with actual
  parent→child edges (`"Cabal" -> "base";`, etc.) — checked live against
  the real hledger project, confirmed working. **This, not `stack ls
  dependencies`, is the real source for the dependency tree's recursive
  structure** — combined with `stack ls dependencies`'s flat name→version
  map to attach a version to each node the DOT graph names.
- `stack query` exists but is documented as "experimental" and returns
  general build info, not a dependency tree — not used by this plan.

**Real, live confirmation this amendment's own external-process design
is actually buildable, not just theoretically sound** — a genuine
smoke test run this session, not assumed:
```
$ cat smoketest.hs
{- stack script
   --resolver lts
   --package aeson
   --package bytestring
-}
{-# LANGUAGE OverloadedStrings #-}
import qualified Data.Aeson as A
import qualified Data.ByteString.Lazy.Char8 as BL
main :: IO ()
main = BL.putStrLn (A.encode (A.object ["id" A..= (1::Int), "result" A..= A.object ["ok" A..= True]]))

$ stack --resolver nightly-2026-09-01 script smoketest.hs
# (first run: ~5 min, compiles aeson from source against the pinned
#  snapshot resolver — succeeds, no network-fetch failures)
{"id":1,"result":{"ok":true}}

$ stack --resolver nightly-2026-09-01 script smoketest.hs   # second run
{"id":1,"result":{"ok":true}}
# real  0m3.301s   (warm — aeson now cached in ~/.stack, no rebuild)
```
This confirms: `stack script` (a single self-contained `.hs` file, no
separate `package.yaml`/`stack.yaml` needed for the adapter itself) is a
real, working mechanism in this environment; `aeson` (Haskell's standard
JSON library) builds successfully against the same pinned snapshot
resolver hledger itself uses; and warm-cache per-invocation overhead
(~3s) is acceptable for a subprocess called once per `codecompass sync`.
`--compile`/`--use-root` are available `stack script` flags that would
cache a compiled executable for lower latency still, if real usage ever
shows this matters — not needed for correctness, named for later.

## 2. Architecture: an external process, not an in-process class

Per `decisions/0057` (new this amendment — read it in full before
implementing). Three real, separate pieces:

1. **`src/codecompass/adapters/external_process.py`** (new) — a fully
   generic JSON-Lines subprocess client. Zero ecosystem-specific
   knowledge: `spawn(command)`, `initialize()`, `analyze_project(root,
   package_name)`, `shutdown()`. Reusable by any future external-process
   adapter, not rewritten per ecosystem. This is the piece that actually
   satisfies "CodeCompass core must not import Haskell-specific
   implementation code" — it never mentions Haskell, `stack`, or
   `package.yaml` anywhere in its own source.
2. **`src/codecompass/adapters/haskell.py`** (new, but now *thin*) — the
   `HaskellAdapter(EcosystemAdapter)` class. Reads `package.yaml`
   directly via `yaml.safe_load()` for `installed_version()`/
   `repository_url()` (simple manifest-key lookups — the same class of
   generic, ecosystem-adjacent code `discovery.py` already does for
   every other ecosystem's own manifest, not "Haskell-specific
   implementation code" in the sense `decisions/0057` draws the line
   around); resolves the monorepo package root (§6); constructs an
   `external_process.ExternalAdapterProcess` pointed at the reference
   adapter script (§3) and delegates `dependency_tree()`/
   `readme_and_api_surface()`'s API-surface half to it.
3. **`adapters/haskell/`** (new **top-level** directory, sibling to
   `src/`, **outside** `src/codecompass/` entirely) — the actual
   reference adapter: a single-file `stack script` (`adapter.hs`, using
   `aeson`, confirmed buildable above) that reads one JSON request line
   from stdin, dispatches on `method`, and for `analyze_project`: runs
   `stack dot --external`/`stack ls dependencies` inside the given
   project root and parses their real, verified text output (§4 below —
   same parsing job the original in-process plan had, now living here
   instead), plus a real `.hs`-source export-list scan for API surface
   (§5). Writes one JSON response line to stdout. **No Python code
   anywhere imports from this directory**, and nothing in
   `src/codecompass/`'s own test suite depends on this directory
   existing to pass (its own tests are `stack`-availability-gated,
   skip-if-unavailable, matching `decisions/0014`'s existing posture).
   This directory could be extracted into its own repository with no
   CodeCompass-core change required — the real, checkable property
   behind "independently versionable and distributable."

**Every real touchpoint still needed on the CodeCompass-core side**
(unchanged in *kind* from the original plan, changed in *content* —
`adapters/haskell.py` is now thin, and `external_process.py` is new):

| File | What widens | Precedent |
|---|---|---|
| `src/codecompass/core.py::Ecosystem` (a `StrEnum`) | new `HASKELL = "haskell"` member | Phase 8's own NPM/PYTHON/CARGO members |
| `src/codecompass/graph.py`'s `vendors.ecosystem` CHECK constraint | widen to include `'haskell'`; bump `_SCHEMA_VERSION` (currently `"7"`, per Phase 54c → `"8"`) | The exact same `_migrate_doc_artifacts_constraints`-style widening Phase 54c just did for `doc_artifacts.origin` |
| `src/codecompass/discovery.py`'s manifest-discoverer table | add `"package.yaml": (Ecosystem.HASKELL, discover_haskell)`, parsed via `yaml.safe_load()` | Mirrors `"package.json"`/`"pyproject.toml"`/`"Cargo.toml"`'s own entries |
| `src/codecompass/adapters/external_process.py` (new) | the generic protocol client | New — no direct precedent, deliberately generic |
| `src/codecompass/adapters/haskell.py` (new, thin) | manifest reads + protocol-client dispatch | Structurally unlike `cargo.py` now — thinner, since the real logic moved out-of-process |
| `src/codecompass/adapters/__init__.py::_ADAPTER_BY_ECOSYSTEM` | add `Ecosystem.HASKELL: HaskellAdapter` | One-line dict addition, unchanged |
| `adapters/haskell/adapter.hs` (new, outside `src/`) | the actual `stack dot`/`stack ls dependencies`/`.hs`-export-scan logic | New |

**`src/codecompass/symbols.py`'s planned `extract_haskell_symbols`
(the original plan's own §"What minimal means here") is now removed
from this list** — Haskell source parsing for API surface happens
inside the external adapter process (§5), not in CodeCompass's own
`symbols.py`, per the whole point of this amendment. `symbols.py`
itself is untouched by this phase.

**Explicitly not touched this phase** (unchanged from the original
plan): `src/codecompass/usage.py`'s `detect_imports_for_file` — Phase
61's own scope, not this phase's.

## 3. The protocol, restated concretely for this phase's own use

Full protocol definition: `decisions/0057`. For Phase 60 specifically,
exactly two request types are ever sent:

```jsonc
// CodeCompass -> adapter
{"id": 1, "method": "initialize", "params": {"protocol_version": 1}}
// adapter -> CodeCompass
{"id": 1, "result": {"protocol_version": 1, "adapter_name": "codecompass-haskell-adapter",
  "adapter_version": "0.1.0", "ecosystem": "haskell",
  "capabilities": ["dependencies", "symbols", "observations", "diagnostics"]}}

// CodeCompass -> adapter
{"id": 2, "method": "analyze_project",
 "params": {"project_root": "/home/cormac/projects/hledger/hledger-lib",
            "package_name": "hledger-lib"}}
// adapter -> CodeCompass
{"id": 2, "result": {
  "dependencies": {"name": "hledger-lib", "version": "1.52.4", "dev_only": false,
                    "children": [{"name": "aeson", "version": "2.2.5.1", "dev_only": false, "children": []}, ...]},
  "symbols": [{"name": "Query", "purpose": null, "module": "Hledger.Query"}, ...],
  "observations": [{"method": "executable", "what_was_done": "ran stack dot --external",
                     "location": null, "raw_result": "...", "tool": "stack", "tool_version": "3.11.1"}],
  "diagnostics": []}}

// CodeCompass -> adapter
{"id": 3, "method": "shutdown"}
{"id": 3, "result": {}}
```

**Parsing `stack dot`/`stack ls dependencies`'s real, verified text
output happens inside the adapter process now** (not in Python) — a
small, mechanical, hand-rolled job in Haskell (a regex/line-split over
known-shape text, no new Haskell library needed beyond `aeson` for the
JSON output itself): a pattern for `"(\S+)"\s*->\s*"(\S+)";` edge lines,
and a plain space-split for `stack ls dependencies`'s `NAME VERSION`
lines.

## 4. `package.yaml` parsing: real `PyYAML`, per direct instruction

**Superseded, not merely revisited**: the original plan's own
"hand-roll, don't add a dependency" recommendation for `package.yaml` is
overridden by direct instruction. `discover_haskell` (in
`discovery.py`) and `HaskellAdapter`'s own manifest reads use
`yaml.safe_load()` — a real, declared `PyYAML` dependency added to
`pyproject.toml`. This is the right call independent of the instruction
too: hpack's real shape (nested `dependencies:` lists with version
constraints, multi-line `description: |` blocks, `flags:` sub-maps —
all visible in the real `hledger-lib/package.yaml` inspected this
session) is genuinely more than a hand-rolled parser scoped to a handful
of flat keys can safely claim to handle, unlike `references.toml`'s own
much flatter shape. `yaml.safe_load()` specifically (never `yaml.load()`
without a loader) — no arbitrary-object deserialization, matching this
project's own general security posture for parsing untrusted/external
file content.

## 5. The one genuinely open design question: API-surface extraction

Unchanged in substance from the original plan, now scoped to what the
**external adapter process** must do, not `symbols.py`:

- Rust's own precedent (`extract_rust_symbols`) is a coarse line scan for
  `pub fn`/`pub struct`/`pub enum`/`pub trait`. Haskell's own visibility
  model is different in kind — a module's exports are declared in its
  own `module Foo (a, b, c) where` header line, not per-declaration
  keywords, and that header can span multiple lines, use `(..)` to
  re-export a type's constructors, or omit an export list entirely
  (meaning *everything* top-level is exported).
- A real, immediately-available proving case exists: `hledger-lib`'s own
  modules (already read directly during Phase 54b — e.g. `Hledger.Query`,
  `Hledger.Data.AccountName`) are exactly the kind of real, non-trivial,
  multi-hundred-line module with a real export list this extraction
  needs to handle correctly.
- This is genuinely uncertain in a way Phase 54c's own two proving cases
  were not (per that phase's own retro, which explicitly flagged
  "neither proving case presented a genuine pre-implementation
  misunderstanding for review to catch" as an untested gap).

**Per direct instruction, this is no longer a flagged recommendation —
it is mandated**: run "what should Haskell API-surface extraction
actually capture, and does a naive first attempt get it wrong in a way
real testing against `hledger-lib` would catch" through Phase 54c's
evidence-backed workflow (`context-researcher` → `documentation-agent` →
review → `REQ-`-backed implementation), scoped only to this one
question — `planning/knowledge/haskell-api-surface-extraction/`. The
resulting `REQ-` records specify exactly what the external adapter's own
export-list-scanning code must do; the adapter script implements that
specification, in Haskell, inside `adapters/haskell/adapter.hs` — not in
any Python module.

## 6. Monorepo package roots (now an explicit, tested requirement)

**Resolution happens on the CodeCompass side, before the adapter is ever
invoked** — the adapter is never handed a monorepo root and asked to
figure out which subdirectory is the real package (`decisions/0057`).
Given a configured project root (`/home/cormac/projects/hledger`) and a
target package name (`hledger-lib`), `HaskellAdapter` searches immediate
subdirectories for the one whose own `package.yaml` declares a matching
`name:` field, and passes **that resolved subdirectory**
(`hledger-lib/`) as `analyze_project`'s `project_root` parameter — never
the monorepo root itself. This is a real, explicit test case (§"Files"),
not an incidental side effect: a test asserts that analyzing
`hledger-lib` inside the real `hledger` monorepo resolves to
`hledger-lib/`, not `/home/cormac/projects/hledger`, and that `stack
dot`/`stack ls dependencies` (run by the adapter, inside that resolved
directory) produce output scoped to `hledger-lib` specifically.

## 7. Testing strategy

Per `decisions/0014`'s own standing rule (fixture-based tests as the
*primary* strategy; live smoke tests wherever the toolchain is actually
present) — now applied across the process boundary:

- **`external_process.py`** (generic protocol client): fixture-tested
  against a small, hand-written fake adapter process (a tiny Python
  script printing canned JSON-Lines responses, or a `subprocess`-free
  unit test against pre-recorded response strings fed through the same
  parsing code) — no real Haskell toolchain needed for these, matching
  every prior adapter's own primary-strategy precedent.
- **`HaskellAdapter`** (thin dispatcher): fixture-tested for the
  `package.yaml`-reading half (a real `yaml.safe_load()` call against
  fixture text, not mocked); the monorepo-resolution logic (§6) gets its
  own fixture test using a small synthetic two-package directory tree.
- **`adapters/haskell/adapter.hs`**: this is real Haskell code with its
  own test needs. Given `stack` **is** available in this environment,
  this phase gets real live tests — `pytest.mark.skipif(shutil.which("stack")
  is None, ...)`-guarded from the Python test suite's own side, invoking
  the real adapter script against the real `hledger-lib` directory and
  asserting on its real JSON output — the second adapter (after npm/
  Python) to get this from day one, unlike Cargo's still-outstanding
  gap. A small number of the adapter script's own internal parsing
  functions (the DOT-edge regex, the `stack ls dependencies` line split)
  may also get direct Haskell-side unit tests if `adapter.hs` is
  structured to expose them separately from `main` — a real
  implementation-time decision, not fixed in this plan.
- **End-to-end**: register `hledger-lib` in a scratch project's
  `vendor.toml` with `ecosystem = "haskell"`, run a real `codecompass
  sync`, and confirm the resulting `context-graph.db` row's
  `installed_version`/dependency-tree/API-surface content matches real,
  independently checked values — the whole protocol round-trip, not
  just the adapter script in isolation.

## Scope

**In scope:**

- `src/codecompass/core.py::Ecosystem` gains `HASKELL`.
- `src/codecompass/graph.py`: `vendors.ecosystem` CHECK widened;
  `_SCHEMA_VERSION` "7" → "8"; migration docstring updated.
- `src/codecompass/discovery.py`: `package.yaml` manifest discovery via
  `yaml.safe_load()`.
- `pyproject.toml`: `PyYAML` added as a real, declared dependency.
- `src/codecompass/adapters/external_process.py` (new) — the generic
  JSON-Lines protocol client.
- `src/codecompass/adapters/haskell.py` (new, thin) — manifest reads,
  monorepo resolution, protocol-client delegation.
- `src/codecompass/adapters/__init__.py` — dispatch table entry.
- `adapters/haskell/adapter.hs` (new, **outside** `src/codecompass/`) —
  the reference external adapter, per §5's own `REQ-`-backed
  specification for API-surface extraction.
- `planning/knowledge/haskell-api-surface-extraction/` (new feature
  directory, Phase 54c's own model) — mandated, not optional, per direct
  instruction (§5).
- Fixture tests (primary) + `stack`-gated live smoke tests, both for the
  Python-side protocol client and the real adapter script.
- `architecture/overview.md`/`docs/` updated: the adapter section gains
  a description of the external-process strategy alongside the
  in-process one, and the npm/Python/Cargo trio no longer described as
  the complete adapter set.
- `decisions/0057` (already written this amendment) — no further new
  ADR expected unless implementation surfaces a real need for one.

**Explicitly deferred / out of scope:**

- `src/codecompass/usage.py`'s Haskell import detection — Phase 61's own
  scope.
- Source location resolution for an externally-fetched,
  `~/.stack/snapshots/`-resident dependency (only same-project monorepo
  members are handled this phase, §6).
- Any non-hpack (`.cabal`-only, no `package.yaml`) project.
- Any AI/semantic interpretation of Haskell source — mechanical
  detection only, inside the adapter process, matching the
  determinism-first boundary every other adapter already holds.
- Tracking hledger-lib as a real CodeCompass vendor and evaluating it
  (Phase 61's own scope).
- **gRPC, network services, a plugin marketplace/registry, remote
  execution, or a versioned SDK** — explicitly named as premature by
  direct instruction; the local-subprocess, JSON-Lines-on-stdio protocol
  is the whole of this phase's own communication mechanism.
- A distribution/versioning/discovery mechanism for the external adapter
  beyond it existing as a file in this same repository, invoked by a
  fixed, known path — "independently versionable and distributable" is
  validated as an **architectural property** (no Python import
  dependency on the adapter directory) this phase, not built out as a
  real separate-repository/package-registry mechanism yet.
- Resolving whether a future proprietary adapter distribution model is
  actually GPL-compatible — explicitly named as a legal question outside
  this project's own competence (`decisions/0057`'s own closing section).

## Design decisions

- **External process + JSON-Lines-on-stdio, not in-process** — per
  direct instruction; full rationale and protocol shape in
  `decisions/0057`.
- **`stack script` (a single `.hs` file), not a separate Stack project**
  for the reference adapter — confirmed buildable this session (§1);
  the smallest-footprint way to ship a real, independently-versionable
  Haskell program without a second `package.yaml`/`stack.yaml` pair to
  maintain.
- **`stack dot`, not `stack ls dependencies`, is the tree source** —
  unchanged real finding from the original planning pass.
- **Real `PyYAML` (`yaml.safe_load()`), not a hand-rolled parser, for
  `package.yaml`** — per direct instruction, and independently justified
  by hpack's real nested/multi-line shape (§4).
- **API-surface extraction routed through Phase 54c's workflow is now
  mandatory, not a review-gate option** — per direct instruction.
- **Monorepo package-root resolution happens in `HaskellAdapter` (Python
  side), never inside the adapter process** — keeps the adapter itself
  simpler and this capability reusable by any future external adapter
  without reimplementation.
- **No new ecosystem-agnostic core change beyond the exact touchpoints
  named in §2's table** — the external-process *boundary* itself is the
  one deliberate addition beyond the original plan's own scope, per the
  user's own "preserve current Phase 60 scope limits unless the
  external-process boundary itself requires a minimal additional
  component" instruction; `external_process.py` and
  `adapters/haskell/adapter.hs` are exactly that minimal addition, not a
  broader rearchitecture of the adapter system.

## Files

- `decisions/0057-external-process-adapter-protocol.md` — written this
  amendment.
- `src/codecompass/core.py` — `Ecosystem.HASKELL`.
- `src/codecompass/graph.py` — CHECK-enum widening, `_SCHEMA_VERSION` 8.
- `src/codecompass/discovery.py` — `package.yaml` discoverer entry (via
  `yaml.safe_load()`).
- `pyproject.toml` — `PyYAML` dependency.
- `src/codecompass/adapters/external_process.py` (new).
- `src/codecompass/adapters/haskell.py` (new, thin).
- `src/codecompass/adapters/__init__.py` — dispatch entry.
- `adapters/haskell/adapter.hs` (new, top-level, outside `src/`).
- `planning/knowledge/haskell-api-surface-extraction/*.yaml`,
  `design.md`, `context-packet.md` (new — Phase 54c's model, mandated).
- `tests/test_core.py`, `tests/test_graph.py`, `tests/test_discovery.py`,
  `tests/test_adapters_external_process.py` (new),
  `tests/test_adapters_haskell.py` (new) — fixture tests + `stack`-gated
  live smoke tests. `tests/test_symbols.py` is **not** touched this
  phase (§2's own removal note).
- `architecture/overview.md`, `docs/` — updated: external-process
  adapter strategy documented alongside the in-process one.
- `planning/retros/phase-60-minimal-haskell-adapter.md` — the retro.

## Verification

- Every new function/method (both Python-side and the adapter script's
  own internal parsing functions, where feasible) has fixture-based unit
  test coverage.
- `stack`-availability-gated live smoke tests actually run in this
  environment (not merely written and skipped) and pass against the
  real `hledger-lib` package, including the monorepo-root-resolution
  case (§6).
- A real, end-to-end confirmation: the full protocol round-trip
  (`initialize` → `analyze_project` → `shutdown`) against the real
  adapter process, feeding a real `codecompass sync`, with the resulting
  `context-graph.db` row's content independently checked against real
  values — not just that the sync command exits zero.
- The seven capabilities named in the governing prompt are each checked
  explicitly, not merely implied: (1) discover/invoke the external
  adapter; (2) negotiate/inspect its capabilities via `initialize`; (3)
  request project analysis; (4) receive language-neutral structured
  results; (5) ingest those results with zero Haskell-specific logic in
  `src/codecompass/` outside `adapters/haskell.py`'s own thin dispatch;
  (6) preserve evidence/provenance across the process boundary (the
  `observations` section becoming real `planning/knowledge/` records);
  (7) the existing real hledger validation (the end-to-end confirmation
  above) succeeds.
- `pytest`/`ruff check .`/`check_user_docs.py --strict` all clean.
- `release-phase-auditor` PASS or PASS WITH NON-BLOCKING OBSERVATIONS.

## Done when

Standard DoD (`CLAUDE.md` §5) + all five `EcosystemAdapter` methods
implemented (via the thin dispatcher + external process) and both
fixture-tested and live-smoke-tested + the real end-to-end confirmation
passes + all seven named capabilities independently verified, not
asserted + Phase 54c's evidence-backed workflow actually run for the
API-surface-extraction sub-question, with its own `REQ-` records folded
into this phase's own retro + `architecture/overview.md`/`docs/` updated
to describe both adapter strategies + a retro that states plainly
whether the protocol design held up against real `hledger-lib` output
without surprises, whether `stack script`'s own build/cache behaviour
was practical at real usage cadence, and — explicitly — whether this
phase's own experience suggests the external-process strategy should
become the *default* for future adapters or stay a deliberate exception
for cases (like a future COBOL adapter) that specifically need it.

**Not done merely because the protocol works and one round-trip
succeeds** — done only once the real hledger validation this phase's
own governing instruction names (capability 7) passes for real, and the
retro can honestly answer whether the architecture is worth its real,
measured overhead (process-spawn latency, a second language's own
toolchain to maintain) relative to what an in-process adapter would have
cost.

---

## Review gate

Presented for review before implementation starts.

1. **The external-process architecture itself** (§2, `decisions/0057`)
   — this is a direct instruction, not a judgment call being presented
   for a decision; flagged here only so its scope is visible before
   implementation starts, not because it's still open.
2. **`stack script` (single-file), not a separate Stack project, for the
   reference adapter** — confirmed buildable this session; if a real
   implementation need later shows a full Stack project is warranted
   (e.g. the adapter's own logic outgrows one file, or its own test
   suite needs Haskell-side unit tests that `stack script` can't host
   cleanly), that's a small, disclosed scope growth to make at that
   point, not a reason to over-build the skeleton now.
3. **`PyYAML` as a real, declared dependency** — per direct instruction;
   flagged for visibility (a new runtime dependency is always worth a
   moment's explicit notice) rather than as an open question.
4. **Phase 54c's workflow, mandated for the API-surface-extraction
   question** — per direct instruction; this is also that methodology's
   own first real test under genuine uncertainty (per its own retro's
   explicit recommendation), so the two decisions reinforce each other
   rather than being independent choices.
5. **The GPL/legal-separation caveat** (`decisions/0057`'s own closing
   section) — presented as a disclosed, deliberate non-claim, not a
   question needing a decision here; flagged so it isn't read past
   silently, since it directly bears on whether this architecture
   actually delivers what motivates it (a future proprietary adapter
   option) once a real one is ever built.

---

## §A. Original in-process plan (preserved, superseded by this amendment — not deleted)

The original Phase 60 plan (before this amendment) specified an
in-process `HaskellAdapter(EcosystemAdapter)` class living entirely
inside `src/codecompass/adapters/haskell.py`, implementing all five
`EcosystemAdapter` methods directly against `stack`/`package.yaml`, with
no process boundary — `symbols.py` gaining `extract_haskell_symbols`
directly, and `discovery.py`'s `package.yaml` parsing hand-rolled rather
than using `PyYAML`. Its own real findings (the `stack ls dependencies`
JSON-mode gap, `stack dot`'s real DOT-graph output, the monorepo
source-location scope boundary, the API-surface-extraction open
question) all carry forward into this amendment unchanged — only *where*
the Haskell-specific logic lives, and *how* `package.yaml` gets parsed,
changed. Available as the basis for a future in-process fallback if the
external-process architecture's own real overhead (§"Done when") proves
not worth it — superseded as this phase's *required* architecture, not
discarded.
