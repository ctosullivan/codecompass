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
versioned, JSON-based protocol (`decisions/0057`) — validating that
CodeCompass's core never needs to import ecosystem-specific
implementation code for a new adapter, motivated by a real future case
named directly: a potentially proprietary COBOL/mainframe adapter suite
that could never ship as importable GPL Python code inside
`src/codecompass/`. The behavioural goals (§0-§1, §5's own open design
question, the monorepo/testing scope) are preserved; the *mechanism*
changes throughout §2 onward.

**Amended again 2026-09-19** (second direct instruction, same day,
before implementation began — `decisions/0058`, new): the protocol and
the Haskell adapter are no longer even files inside this repository's
own `adapters/haskell/` directory (this amendment's own first version,
preserved at §A alongside the original in-process plan) — they are now
**two separate, standalone, publicly-hosted repositories**,
`codecompass-adapter-protocol` (MIT) and `codecompass-adapter-haskell`
(GPL-3.0-or-later, matching CodeCompass's own license), checked out as
git submodules inside this repository's own workspace. §2 onward is
rewritten again to reflect this; the protocol *shape* itself
(`decisions/0057`) and every real technical finding (the `stack
ls dependencies`/`stack dot` distinction, the `stack script`+`aeson`
smoke test, the monorepo package-root resolution rule, the mandatory
Phase 54c workflow routing for API-surface extraction) are all
**unchanged** by this second amendment — only *where the code lives and
how it is licensed/versioned* changes again.

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

## 2. Architecture: three repositories, one local workspace

Per `decisions/0057` (protocol shape) and `decisions/0058` (the
multi-repository/licensing/submodule decision — new this second
amendment, read both in full before implementing). Four real, separate
pieces now, not three:

1. **`codecompass-adapter-protocol`** (new, standalone, public
   repository, **MIT license**) — the language-neutral contract only:
   `SCHEMA.md`, `schemas/*.json` (real JSON Schema documents for every
   message shape), `examples/`, `conformance/` (a small, standalone
   schema-validation test harness). **No CodeCompass code, no Haskell
   code.** Checked out locally at `protocol/codecompass-adapter-protocol/`
   as a git submodule.
2. **`codecompass-adapter-haskell`** (new, standalone, public
   repository, **GPL-3.0-or-later**, matching CodeCompass's own
   license) — the actual reference adapter, now a real minimal Stack
   project (`package.yaml`/`stack.yaml`/`app/Main.hs` — superseding this
   plan's own first-amendment "bare `stack script`" sketch, whose real,
   confirmed-working `stack`+`aeson` finding, §1, remains valid technical
   grounding, just packaged properly now since a real standalone public
   repository needs its own `LICENSE`, `README.md`, and CI, not one
   script file). Implements the protocol repository's own schemas —
   validated by running that repository's own conformance tests against
   this adapter's real output in this repository's own CI, not by a
   Haskell-code-level library dependency (the protocol repo ships no
   Haskell code to depend on). Runs as an independent executable/
   process, per `decisions/0057`, unchanged. Checked out locally at
   `adapters/haskell/` as a git submodule.
3. **`src/codecompass/adapters/external_process.py`** (new, inside this
   repository) — a fully generic JSON-Lines subprocess client. Zero
   ecosystem-specific knowledge: `spawn(command)`, `initialize()`,
   `analyze_project(root, package_name)`, `shutdown()`. This is the
   piece that actually satisfies "CodeCompass core must not import
   Haskell-specific implementation code" — it never mentions Haskell,
   `stack`, or `package.yaml` anywhere in its own source, and has no
   dependency (Python import or otherwise) on either submodule's own
   content — it invokes whatever executable it's configured to invoke
   (the adapter submodule's own built binary, once implementation
   builds it) purely as an opaque subprocess.
4. **`src/codecompass/adapters/haskell.py`** (new, thin, inside this
   repository) — the `HaskellAdapter(EcosystemAdapter)` class. Reads
   `package.yaml` directly via `yaml.safe_load()` for
   `installed_version()`/`repository_url()`; resolves the monorepo
   package root (§6); constructs an
   `external_process.ExternalAdapterProcess` pointed at the built
   adapter executable and delegates `dependency_tree()`/
   `readme_and_api_surface()`'s API-surface half to it.

**Local workspace layout** (git submodules — `decisions/0058`):

```
codecompass/                              (this repository, main)
├── protocol/
│   └── codecompass-adapter-protocol/     (git submodule)
└── adapters/
    └── haskell/                          (git submodule)
```

`codecompass`'s own `.gitmodules` records each submodule's remote URL;
CodeCompass's own git history commits only a pinned commit SHA per
submodule (a gitlink), never the submodules' own file content. **No
Python code anywhere imports from either submodule's own directory**,
and nothing in `src/codecompass/`'s own test suite depends on either
submodule being checked out to pass (their own tests are gated on
`git submodule status` reporting them initialized *and* `stack`
availability, skip-if-either-is-missing, matching `decisions/0014`'s
existing posture for the Cargo adapter).

**Every real touchpoint still needed on the CodeCompass-core side**
(unchanged in *kind* from the prior amendment, paths updated for the
submodule layout):

| File | What widens | Precedent |
|---|---|---|
| `src/codecompass/core.py::Ecosystem` (a `StrEnum`) | new `HASKELL = "haskell"` member | Phase 8's own NPM/PYTHON/CARGO members |
| `src/codecompass/graph.py`'s `vendors.ecosystem` CHECK constraint | widen to include `'haskell'`; bump `_SCHEMA_VERSION` (currently `"7"`, per Phase 54c → `"8"`) | The exact same `_migrate_doc_artifacts_constraints`-style widening Phase 54c just did for `doc_artifacts.origin` |
| `src/codecompass/discovery.py`'s manifest-discoverer table | add `"package.yaml": (Ecosystem.HASKELL, discover_haskell)`, parsed via `yaml.safe_load()` | Mirrors `"package.json"`/`"pyproject.toml"`/`"Cargo.toml"`'s own entries |
| `src/codecompass/adapters/external_process.py` (new) | the generic protocol client | New — no direct precedent, deliberately generic |
| `src/codecompass/adapters/haskell.py` (new, thin) | manifest reads + protocol-client dispatch, configured to invoke the submodule's own built executable | Structurally unlike `cargo.py` now — thinner, since the real logic moved out-of-process and out-of-repository |
| `src/codecompass/adapters/__init__.py::_ADAPTER_BY_ECOSYSTEM` | add `Ecosystem.HASKELL: HaskellAdapter` | One-line dict addition, unchanged |
| `.gitmodules` (new, repo root) | two submodule entries | New — this repository's first submodule use |
| `protocol/codecompass-adapter-protocol/` (submodule, separate repo) | the schemas/conformance tests | New, external |
| `adapters/haskell/` (submodule, separate repo) | the real Stack project implementing the protocol | New, external |

**`src/codecompass/symbols.py`'s planned `extract_haskell_symbols` is
still not touched this phase** — unchanged from the first amendment;
Haskell source parsing for API surface happens inside the (now
separately-repositoried) adapter, per its own `REQ-`-backed
specification (§5).

**Explicitly not touched this phase** (unchanged from every prior
version of this plan): `src/codecompass/usage.py`'s
`detect_imports_for_file` — Phase 61's own scope, not this phase's.

## 3. The protocol, restated concretely for this phase's own use

Full protocol definition: `decisions/0057` (its own inline description
remains a valid, accurate summary) — the **canonical, versioned source
becomes `protocol/codecompass-adapter-protocol/SCHEMA.md` and its own
`schemas/*.json`** once that repository exists, per `decisions/0058`.
For Phase 60 specifically, exactly two request types are ever sent:

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
output happens inside the adapter process now** (not in Python, and now
not even in this repository) — a small, mechanical, hand-rolled job in
Haskell, living in `codecompass-adapter-haskell`'s own
`app/Main.hs` (a regex/line-split over known-shape text, no new Haskell
library needed beyond `aeson` for the JSON output itself): a pattern for
`"(\S+)"\s*->\s*"(\S+)";` edge lines, and a plain space-split for `stack
ls dependencies`'s `NAME VERSION` lines.

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
export-list-scanning code must do; `codecompass-adapter-haskell`
(checked out locally at `adapters/haskell/`) implements that
specification, in Haskell, inside its own `app/Main.hs` — not in any
Python module, and not in this repository's own tracked content at all.

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
- **`codecompass-adapter-protocol`'s own conformance tests**: schema
  validation against the repository's own recorded example messages —
  entirely standalone, no CodeCompass or Haskell dependency, run in that
  repository's own CI.
- **`codecompass-adapter-haskell`'s own tests** (in its own repository,
  its own CI): real Haskell code with its own test needs, run against
  `codecompass-adapter-protocol`'s conformance suite (a real dependency
  on the protocol repo's own conformance tests, not its code — there is
  none to depend on) to confirm its real output actually validates
  against the schemas, plus its own internal unit tests for the
  DOT-edge-parsing/`stack ls dependencies`-line-parsing functions if
  `app/Main.hs` is structured to expose them separately from `main`.
- **From `codecompass`'s own test suite** (this repository):
  `external_process.py` (generic protocol client) is fixture-tested
  against a small, hand-written fake adapter process (a tiny script
  printing canned JSON-Lines responses) — no real Haskell toolchain
  needed, matching every prior adapter's own primary-strategy precedent.
  `HaskellAdapter` (thin dispatcher) is fixture-tested for the
  `package.yaml`-reading half (a real `yaml.safe_load()` call against
  fixture text) and the monorepo-resolution logic (§6, a small synthetic
  two-package directory tree). Given `stack` **is** available in this
  environment and both submodules are checked out, this repository also
  gets real, `pytest.mark.skipif`-guarded (on both `stack` availability
  and submodule initialization) live smoke tests invoking the real,
  submodule-built adapter executable against the real `hledger-lib`
  directory and asserting on its real JSON output — the second adapter
  (after npm/Python) to get this from day one, unlike Cargo's
  still-outstanding gap.
- **End-to-end**: register `hledger-lib` in a scratch project's
  `vendor.toml` with `ecosystem = "haskell"`, run a real `codecompass
  sync`, and confirm the resulting `context-graph.db` row's
  `installed_version`/dependency-tree/API-surface content matches real,
  independently checked values — the whole three-repository protocol
  round-trip, not just the adapter script in isolation.

## 8. Local development, clone/submodule setup, and version compatibility

New documentation, `docs/external-adapters.md` (mandated by direct
instruction, not optional), must cover:

- **Cloning**: `git clone --recurse-submodules <codecompass-url>` for a
  fresh clone; `git submodule update --init --recursive` for an
  already-existing clone that predates this phase. A plain `git clone`
  with no submodule flag leaves `protocol/codecompass-adapter-protocol/`
  and `adapters/haskell/` as empty directories — documented explicitly
  as the single most likely point of confusion for a new contributor,
  not left to be discovered by trial and error.
- **Building the adapter locally**: `cd adapters/haskell && stack
  build` (once its own `package.yaml`/`stack.yaml` exist) — a real,
  runnable set of steps, not a placeholder.
- **Updating a submodule to a new release**: `cd
  protocol/codecompass-adapter-protocol && git checkout <tag>`, back out
  to the main repository, `git add protocol/codecompass-adapter-protocol`,
  commit — a real, disclosed gitlink-bump workflow (`decisions/0058`),
  distinguished explicitly from *editing* the submodule's own content
  from the parent repository, which this workflow never does.
- **Commit independence** (`decisions/0058`): a change to the protocol's
  own schemas is a commit in `codecompass-adapter-protocol`'s own
  history; a change to the adapter's own Haskell code is a commit in
  `codecompass-adapter-haskell`'s own history; a change to CodeCompass
  core (including a submodule gitlink bump) is a commit in
  `codecompass`'s own history. Stated as a hard rule for contributors,
  not merely a description of what happens to be true.
- **Version-compatibility matrix**: a table (CodeCompass version ↔
  minimum `codecompass-adapter-protocol` version ↔ tested
  `codecompass-adapter-haskell` version(s)) — for Phase 60 itself, a
  single row (this phase's own CodeCompass commit ↔ protocol `0.1.0`
  ↔ adapter `0.1.0`), with the table's own existence and format
  established for future phases/releases to extend, not populated
  speculatively beyond what Phase 60 itself actually produces.
- **What `protocol_version` (the wire-level integer,
  `decisions/0057`/`0058`) is not**: explicitly distinguished from each
  repository's own semver release version, so a contributor doesn't
  conflate "protocol version 1" with "protocol repo version 1.0.0."

## Scope

**In scope:**

- Two new, standalone, public repositories created:
  `codecompass-adapter-protocol` (MIT) and `codecompass-adapter-haskell`
  (GPL-3.0-or-later) — each with its own `LICENSE`, `README.md`,
  `CHANGELOG.md`, CI configuration, and an initial `0.1.0` release tag.
- Both checked out as git submodules in this repository at
  `protocol/codecompass-adapter-protocol/` and `adapters/haskell/`;
  `.gitmodules` added to this repository's own root.
- `codecompass-adapter-protocol`'s own content: `SCHEMA.md`,
  `schemas/*.json`, `examples/`, `conformance/`.
- `codecompass-adapter-haskell`'s own content: `package.yaml`/
  `stack.yaml`/`app/Main.hs`, implementing `analyze_project`'s
  dependency-tree (`stack dot`/`stack ls dependencies` parsing, §3) and
  API-surface extraction (per §5's `REQ-`-backed specification), its own
  tests run against the protocol repo's conformance suite.
- `src/codecompass/core.py::Ecosystem` gains `HASKELL`.
- `src/codecompass/graph.py`: `vendors.ecosystem` CHECK widened;
  `_SCHEMA_VERSION` "7" → "8"; migration docstring updated.
- `src/codecompass/discovery.py`: `package.yaml` manifest discovery via
  `yaml.safe_load()`.
- `pyproject.toml`: `PyYAML` added as a real, declared dependency.
- `src/codecompass/adapters/external_process.py` (new, this repository)
  — the generic JSON-Lines protocol client, invoking the submodule's own
  built executable as an opaque subprocess.
- `src/codecompass/adapters/haskell.py` (new, thin, this repository) —
  manifest reads, monorepo resolution, protocol-client delegation.
- `src/codecompass/adapters/__init__.py` — dispatch table entry.
- `planning/knowledge/haskell-api-surface-extraction/` (new feature
  directory, Phase 54c's own model, in this repository) — mandated, not
  optional, per direct instruction (§5); its own `REQ-` records specify
  what `codecompass-adapter-haskell`'s own `app/Main.hs` must implement.
- `docs/external-adapters.md` (new, this repository) — clone/submodule
  setup, commit-independence rules, version-compatibility matrix (§8),
  mandated, not optional.
- Fixture tests (primary) + `stack`/submodule-gated live smoke tests, in
  this repository's own suite, for the Python-side protocol client and
  the real submodule-built adapter.
- `architecture/overview.md`/`docs/` updated: the adapter section gains
  a description of the external-process, multi-repository strategy
  alongside the in-process one, and the npm/Python/Cargo trio no longer
  described as the complete adapter set.
- `decisions/0057` and `decisions/0058` (both already written) — no
  further new ADR expected unless implementation surfaces a real need
  for one.

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
  direct instruction, restated by this second amendment; the
  local-subprocess, JSON-Lines-on-stdio protocol, checked out via git
  submodules at a fixed, hand-configured path, is the whole of this
  phase's own distribution/communication mechanism.
- Any *automatic* discovery/registry of adapters beyond the two fixed
  submodule paths this phase actually uses — "independently
  versionable and distributable" is now realized as two real separate
  repositories (`decisions/0058`), not merely an architectural property
  of one repository's own internal layout, but discovery stays fixed
  and hand-configured, not dynamic.
- Resolving whether a future proprietary adapter distribution model is
  actually GPL-compatible — explicitly named as a legal question outside
  this project's own competence (`decisions/0057`/`0058`'s own closing
  sections).

## Design decisions

- **External process + JSON-Lines-on-stdio, not in-process** — per
  direct instruction; full rationale and protocol shape in
  `decisions/0057`.
- **Two separate repositories, differently licensed, checked out as git
  submodules** — per direct instruction; full rationale in
  `decisions/0058`, including why submodules (not subtree, not a
  build-time-only fetch) are the mechanism.
- **A real Stack project (`package.yaml`/`stack.yaml`/`app/Main.hs`),
  not a bare `stack script`, for `codecompass-adapter-haskell`** — this
  amendment's own refinement of the prior amendment's "single-file"
  sketch: a real, standalone public repository needs its own `LICENSE`,
  `README.md`, and CI, which a bare script doesn't naturally host. The
  prior amendment's own confirmed-working `stack`+`aeson` smoke test
  (§1) remains the valid technical grounding that this is buildable
  here — only the packaging changed, not the underlying feasibility
  finding.
- **The protocol repository ships schemas and documentation only, no
  code in any language** — keeps it genuinely language-neutral and
  license-neutral (MIT, so a future differently-licensed adapter can
  depend on the *contract* without inheriting anything from either
  CodeCompass's GPL or a hypothetical adapter's own license,
  `decisions/0058`).
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
  named in §2's table** — the external-process/multi-repository
  *boundary* itself is the one deliberate addition beyond the original
  plan's own scope, per the user's own repeated "preserve current Phase
  60 scope limits unless the external-process boundary itself requires
  a minimal additional component" instruction; `external_process.py`
  and the two new repositories are exactly that minimal addition, not a
  broader rearchitecture of the adapter system.

## Files

**In `codecompass` (this repository):**

- `decisions/0057-external-process-adapter-protocol.md`,
  `decisions/0058-adapter-protocol-and-haskell-adapter-as-separate-repositories.md`
  — both already written.
- `.gitmodules` (new) — two submodule entries.
- `src/codecompass/core.py` — `Ecosystem.HASKELL`.
- `src/codecompass/graph.py` — CHECK-enum widening, `_SCHEMA_VERSION` 8.
- `src/codecompass/discovery.py` — `package.yaml` discoverer entry (via
  `yaml.safe_load()`).
- `pyproject.toml` — `PyYAML` dependency.
- `src/codecompass/adapters/external_process.py` (new).
- `src/codecompass/adapters/haskell.py` (new, thin).
- `src/codecompass/adapters/__init__.py` — dispatch entry.
- `planning/knowledge/haskell-api-surface-extraction/*.yaml`,
  `design.md`, `context-packet.md` (new — Phase 54c's model, mandated).
- `docs/external-adapters.md` (new — §8, mandated).
- `tests/test_core.py`, `tests/test_graph.py`, `tests/test_discovery.py`,
  `tests/test_adapters_external_process.py` (new),
  `tests/test_adapters_haskell.py` (new) — fixture tests + submodule-
  and `stack`-gated live smoke tests. `tests/test_symbols.py` is **not**
  touched this phase.
- `architecture/overview.md`, `docs/` — updated: external-process,
  multi-repository adapter strategy documented alongside the in-process
  one.
- `planning/retros/phase-60-minimal-haskell-adapter.md` — the retro.

**In `codecompass-adapter-protocol` (new, separate repository, MIT):**

- `LICENSE` (MIT), `README.md`, `CHANGELOG.md`.
- `SCHEMA.md` — the canonical protocol specification.
- `schemas/*.json` — one JSON Schema document per message shape.
- `examples/*.json` — worked request/response pairs.
- `conformance/` — the standalone schema-validation test harness.
- CI configuration validating the repo's own examples against its own
  schemas.

**In `codecompass-adapter-haskell` (new, separate repository,
GPL-3.0-or-later):**

- `LICENSE` (GPL-3.0-or-later), `README.md`, `CHANGELOG.md`.
- `package.yaml`, `stack.yaml`, `app/Main.hs` — the real adapter,
  implementing §3's protocol messages and §5's `REQ-`-backed
  API-surface-extraction specification.
- Its own tests, run in its own CI against
  `codecompass-adapter-protocol`'s conformance suite (a real Git
  dependency on that repository, declared however Stack/CI most
  naturally expresses it — an implementation-time detail, not fixed
  here).

## Verification

- Both `codecompass-adapter-protocol` and `codecompass-adapter-haskell`
  exist as real, separate, publicly hosted repositories, each with its
  own real commit history, its own `LICENSE` matching this plan's own
  licensing decision, its own CI passing, and at least one real release
  tag (`0.1.0`) — checked directly (a real `git log`/`git remote` inside
  each submodule, a real license-file read), not assumed from having
  written the plan for them.
- `codecompass`'s own `.gitmodules` and gitlink commits correctly
  reference both repositories at real, resolvable commits; a fresh
  `git clone --recurse-submodules` of `codecompass` actually checks out
  working copies of both.
- **Commit independence is real, not just documented**: the phase's own
  implementation history shows commits landing in three genuinely
  separate repositories (checked via each repository's own `git log`),
  never one commit touching tracked content in more than one.
- Every new function/method (Python-side, and the adapter's own internal
  parsing functions, where feasible) has fixture-based unit test
  coverage, in the repository that owns it.
- `stack`- and submodule-availability-gated live smoke tests actually
  run in this environment (not merely written and skipped) and pass
  against the real `hledger-lib` package, including the
  monorepo-root-resolution case (§6).
- A real, end-to-end confirmation: the full protocol round-trip
  (`initialize` → `analyze_project` → `shutdown`) against the real,
  submodule-built adapter process, feeding a real `codecompass sync`,
  with the resulting `context-graph.db` row's content independently
  checked against real values — not just that the sync command exits
  zero.
- The seven capabilities named in the governing prompt are each checked
  explicitly, not merely implied: (1) discover/invoke the external
  adapter (via the submodule's own known, built-executable path); (2)
  negotiate/inspect its capabilities via `initialize`; (3) request
  project analysis; (4) receive language-neutral structured results;
  (5) ingest those results with zero Haskell-specific logic anywhere in
  `src/codecompass/` outside `adapters/haskell.py`'s own thin dispatch,
  and zero Haskell-specific logic in this repository's own tracked
  content at all (it all lives in the separate `codecompass-adapter-haskell`
  repository); (6) preserve evidence/provenance across the process
  boundary (the `observations` section becoming real
  `planning/knowledge/` records); (7) the existing real hledger
  validation (the end-to-end confirmation above) succeeds.
- `docs/external-adapters.md`'s own documented clone/setup steps are
  followed literally, from a fresh clone, and actually work.
- `pytest`/`ruff check .`/`check_user_docs.py --strict` all clean (this
  repository); each submodule's own CI clean (independently, in its own
  repository).
- `release-phase-auditor` PASS or PASS WITH NON-BLOCKING OBSERVATIONS.

## Done when

Standard DoD (`CLAUDE.md` §5) + both new repositories real, public,
independently licensed, and independently releasing (`0.1.0`) + checked
out cleanly as submodules with `docs/external-adapters.md`'s own
documented setup steps actually working from a fresh clone + all five
`EcosystemAdapter` methods implemented (via the thin dispatcher +
external, submodule-hosted process) and both fixture-tested and
live-smoke-tested + the real end-to-end confirmation passes + all seven
named capabilities independently verified, not asserted + Phase 54c's
evidence-backed workflow actually run for the API-surface-extraction
sub-question, with its own `REQ-` records folded into this phase's own
retro + commit independence across all three repositories demonstrated,
not merely designed + the version-compatibility matrix (§8) populated
with this phase's own real row + `architecture/overview.md`/`docs/`
updated to describe both adapter strategies + a retro that states
plainly whether the protocol design held up against real `hledger-lib`
output without surprises, whether the real multi-repository/submodule
workflow was practical at real development cadence (not just at
one-time setup), and — explicitly — whether this phase's own experience
suggests the external-process, separate-repository strategy should
become the *default* for future adapters or stay a deliberate exception
for cases (like a future COBOL adapter) that specifically need it.

**Not done merely because the protocol works and one round-trip
succeeds, and not done merely because two repositories exist** — done
only once the real hledger validation this phase's own governing
instruction names (capability 7) passes for real, and the retro can
honestly answer whether the architecture is worth its real, measured
overhead (process-spawn latency, a second language's own toolchain to
maintain, three repositories' worth of real maintenance burden instead
of one) relative to what an in-process, single-repository adapter would
have cost.

---

## Review gate

Presented for review before implementation starts.

1. **The external-process architecture itself** (§2, `decisions/0057`)
   and **the two-separate-repositories/submodule architecture**
   (§2, `decisions/0058`) — both direct instructions, not judgment calls
   being presented for a decision; flagged here only so their combined
   scope is visible before implementation starts, not because either is
   still open.
2. **A real Stack project, not a bare `stack script`, for
   `codecompass-adapter-haskell`** — this amendment's own refinement,
   made necessary by the repository-separation requirement itself (a
   real public repo needs its own `LICENSE`/CI/release process); the
   underlying `stack`+`aeson` feasibility finding stays the same, only
   the packaging grew slightly. Flagged for visibility as a real, if
   small, scope consequence of this amendment, not an open question.
3. **`PyYAML` as a real, declared dependency** — per direct instruction;
   flagged for visibility rather than as an open question.
4. **Phase 54c's workflow, mandated for the API-surface-extraction
   question** — per direct instruction; also that methodology's own
   first real test under genuine uncertainty.
5. **The GPL/legal-separation caveat** (`decisions/0057`/`0058`'s own
   closing sections) — presented as a disclosed, deliberate non-claim,
   not a question needing a decision here; now more concrete, since real
   separate repositories and real separate `LICENSE` files are actually
   being created, which strengthens the architecture's own real-world
   realization of "separately licensed" without resolving whether that
   is legally sufficient for an actual future proprietary adapter.
6. **Where exactly `codecompass-adapter-protocol` and
   `codecompass-adapter-haskell` are actually hosted** (which forge,
   which account/organisation, what "public" concretely means for this
   project's own practice) is an operational detail this plan does not
   fix — flagged explicitly as needing a real answer at implementation
   time, not because the *architecture* (separate repos, submodules,
   differing licenses) is in question, but because "create two public
   repositories" is itself an action with real, hard-to-reverse
   consequences (a public commit history, once pushed, is not easily
   un-published) that this planning-only phase should not decide
   silently on the user's behalf.

---

## §A. Original in-process plan (preserved, superseded by the first amendment — not deleted)

The original Phase 60 plan (before any amendment) specified an
in-process `HaskellAdapter(EcosystemAdapter)` class living entirely
inside `src/codecompass/adapters/haskell.py`, implementing all five
`EcosystemAdapter` methods directly against `stack`/`package.yaml`, with
no process boundary — `symbols.py` gaining `extract_haskell_symbols`
directly, and `discovery.py`'s `package.yaml` parsing hand-rolled rather
than using `PyYAML`. Its own real findings (the `stack ls dependencies`
JSON-mode gap, `stack dot`'s real DOT-graph output, the monorepo
source-location scope boundary, the API-surface-extraction open
question) all carry forward into every later amendment unchanged — only
*where* the Haskell-specific logic lives, and *how* `package.yaml` gets
parsed, changed. Available as the basis for a future in-process fallback
if the external-process architecture's own real overhead (§"Done when")
proves not worth it — superseded as this phase's *required*
architecture, not discarded.

## §B. First-amendment single-repository design (preserved, superseded by the second amendment — not deleted)

The first amendment (this file's own earlier revision, same day)
specified the external-process architecture correctly (unchanged by the
second amendment) but located the actual reference adapter *inside this
repository*, at `adapters/haskell/adapter.hs` — a single self-contained
`stack script` file, no separate `package.yaml`/`stack.yaml`, no
separate repository, no submodule. `decisions/0057` (still valid in
full for the protocol shape) originally described this single-repository
layout in its own "Consequences" section before `decisions/0058`
superseded that specific part. The real, confirmed-working `stack`+
`aeson` smoke test this first amendment ran (§1) remains the technical
grounding both this amendment and the second amendment rely on —
nothing about *whether the mechanism works* changed between amendments,
only *where the resulting code is committed and how it is licensed*.
