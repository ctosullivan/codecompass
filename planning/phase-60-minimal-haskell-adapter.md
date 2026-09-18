# Phase 60: Minimal Haskell adapter — plan

**Status:** plan only, not started. Do not begin implementation until
this plan is reviewed — per this project's own established "write the
plan first" discipline (`CLAUDE.md` §1).

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
this exact phase (§4 below). Phase 60 is the next unstarted phase on
Stage F's sequence, gated on nothing (Stage F is a separate axis from
Stage E/GATE DD, per `decisions/0056`).

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
`stack` manages them internally, so every command below goes through
`stack`, never a bare `ghc`/`cabal` invocation.

**Real manifest format, inspected directly** (`hledger-lib/package.yaml`,
hpack format — the same file this project already read during Phase 54):
plain YAML, top-level `name`/`version`/`license`/`maintainer`/
`dependencies` keys — directly analogous to `package.json`/
`pyproject.toml`'s own shape, not a novel format to design a parser
against blind.

**Real dependency-tree command, checked live against the real hledger
project** — a genuinely new finding this planning pass makes, not
assumed from the other adapters' own JSON-based precedent:

- `stack ls dependencies` produces a **flat, plain-text** list
  (`NAME VERSION`, one per line, alphabetically sorted, deduplicated) —
  **no JSON output mode exists** (`--help` confirms no `--json`/
  `--format` flag). This cannot be dropped into the shared `_run_json`
  seam every other adapter uses.
- `stack dot --external` produces a real GraphViz DOT graph with actual
  parent→child edges (`"Cabal" -> "base";`, etc.) — checked live against
  the real hledger project, confirmed working. **This, not `stack ls
  dependencies`, is the real source for `dependency_tree()`'s recursive
  structure** — combined with `stack ls dependencies`'s flat name→version
  map to attach a version to each node the DOT graph names.
- `stack query` exists but is documented as "experimental" and returns
  general build info, not a dependency tree — not used by this plan.

**Every real touchpoint a new ecosystem must widen** (traced directly,
not assumed from the plan's own description of prior phases):

| File | What widens | Precedent |
|---|---|---|
| `src/codecompass/core.py::Ecosystem` (a `StrEnum`) | new `HASKELL = "haskell"` member | Phase 8's own NPM/PYTHON/CARGO members |
| `src/codecompass/graph.py`'s `vendors.ecosystem` CHECK constraint | widen to include `'haskell'`; bump `_SCHEMA_VERSION` (currently `"7"`, per Phase 54c → `"8"`) | The exact same `_migrate_doc_artifacts_constraints`-style widening Phase 54c just did for `doc_artifacts.origin` — direct, fresh precedent, not a hypothetical one |
| `src/codecompass/discovery.py`'s manifest-discoverer table | add `"package.yaml": (Ecosystem.HASKELL, discover_haskell)` | Mirrors `"package.json"`/`"pyproject.toml"`/`"Cargo.toml"`'s own entries exactly |
| `src/codecompass/symbols.py::extract_symbols_for_file` | add a Haskell branch + `extract_haskell_symbols` | Mirrors `extract_rust_symbols`'s own precedent |
| `src/codecompass/adapters/haskell.py` (new) | the `HaskellAdapter` class itself | Mirrors `cargo.py`'s own shape |
| `src/codecompass/adapters/__init__.py::_ADAPTER_BY_ECOSYSTEM` | add `Ecosystem.HASKELL: HaskellAdapter` | One-line dict addition |

**Explicitly not touched this phase**: `src/codecompass/usage.py`'s
`detect_imports_for_file` (project-source-side import detection for a
*consuming* project's own source files). This matters only once a real
consuming project's source is scanned for hledger-lib imports — that is
Phase 61's own scope ("track hledger-lib... as a real CodeCompass-tracked
vendor... generate real digests, real graph entries"), not this phase's
("build the adapter, confirm it produces correct metadata/tree/API-surface
output"). Named explicitly so it isn't silently assumed to be in scope
here and then missed.

## 2. What "minimal" means here

The `EcosystemAdapter` interface (`src/codecompass/adapters/base.py`) has
exactly five abstract methods. This phase implements all five for
Haskell/Stack, each against the *native* tool that already produces the
answer — no new core logic, no Haskell-specific branch anywhere outside
`adapters/haskell.py`/`symbols.py`'s new function/`discovery.py`'s new
entry, per `decisions/0002`'s own hard constraint (restated, not
reinterpreted, by `decisions/0056`):

- `installed_version()` — the tracked package's own `version` field from
  its `package.yaml`.
- `source_location()` — **scoped this phase to the case where the
  tracked package is a member of the same Stack project being synced**
  (e.g. `hledger-lib/` within the `hledger` monorepo) — its own manifest
  directory, exactly like Cargo/npm workspace members already resolve.
  An externally-fetched, `~/.stack/snapshots/`-resident dependency's
  source location is **explicitly deferred** (§6) — a real, disclosed
  scope boundary, not silently assumed to work.
- `repository_url()` — `package.yaml`'s own `github`/`repository` field
  (hpack's shorthand `github: owner/repo` expands to a full GitHub URL;
  a full `repository:` block, if present instead, is read directly) —
  local-metadata-only, no network call, matching `decisions/0021`'s
  existing rule for every other adapter.
- `dependency_tree()` — `stack dot --external` parsed into a `DepNode`
  tree (recursive edge-following from the tracked package's own node),
  cross-referenced against `stack ls dependencies`'s flat name→version
  map for each node's version. **Not deduplicated**, matching every
  other adapter's own `dependency_tree()` contract exactly (diamond
  dependencies appear in full — Phase 3's own tree-rendering concern,
  unaffected).
- `readme_and_api_surface()` — the package's own `README*` file, plus a
  new `extract_haskell_symbols` (§4) for its exported top-level module
  signatures.

## 3. Real command shapes (verified live, not assumed)

```
$ stack ls dependencies --depth 1
Decimal 0.5.2
Diff 1.0.2
...

$ stack dot --external
strict digraph deps {
"hledger" [style=dashed];
...
"Cabal" -> "Cabal-syntax";
"Cabal" -> "base";
...
```

Parsing both is a small, mechanical, hand-rolled job — no new
dependency, matching this project's own established precedent
(`reference_pipeline.py::load_references_toml`'s hand-rolled TOML
parsing, Phase 54c's own hand-rolled YAML-frontmatter check): a regex
for `"(\S+)"\s*->\s*"(\S+)";` edge lines, and a plain `line.rsplit(" ",
1)` split for `stack ls dependencies`'s `NAME VERSION` lines.

`package.yaml` parsing needs real YAML — `PyYAML` is present in this
dev environment (confirmed, `python3 -c "import yaml"` succeeds) but is
**not currently a declared CodeCompass dependency**, and every other
adapter's own manifest format so far has been parseable without one
(`json`/`tomllib`, both stdlib). **Open question, named for the review
gate**: add `PyYAML` as a real, declared dependency (hpack's own YAML
shape is more than this project has hand-rolled a parser for
elsewhere — nested `dependencies:` lists, multi-line `description: |`
blocks), or hand-roll a parser scoped to the small, fixed set of
top-level keys this phase actually needs (`name`, `version`, `license`,
`github`/`repository`, `dependencies`) — the same "hand-roll first,
justify a dependency only once that proves insufficient" discipline
this project has applied every other time so far. **Recommendation**:
hand-roll, scoped narrowly — `package.yaml`'s own top-level keys are
flat scalars/lists, the same shape `references.toml`'s own hand-rolled
parser already handles for a comparable format; a nested/multi-document
YAML feature would only be needed if a real Haskell package's manifest
turns out to need one, which is exactly the kind of thing to discover by
testing against the real `hledger-lib/package.yaml`, not to guess at
now.

## 4. The one genuinely open design question: API-surface extraction

Every other method above has one clear, precedented, low-ambiguity
answer. `readme_and_api_surface()`'s Haskell-symbol extraction does not:

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
  needs to handle correctly, not a toy example.
- This is genuinely uncertain in a way Phase 54c's own two proving cases
  were not (per that phase's own retro, which explicitly flagged
  "neither proving case presented a genuine pre-implementation
  misunderstanding for review to catch" as an untested gap) — a
  plausible-but-wrong first attempt (e.g. "just grep for `^[a-z]\w* ::`
  type-signature lines," which would over-include every unexported
  helper function) is a real risk here, not a hypothetical one.

**Recommendation, flagged for the review gate, not decided
unilaterally**: run this one specific sub-question — "what should
Haskell API-surface extraction actually capture, and does a naive first
attempt get it wrong in a way real testing against `hledger-lib` would
catch" — through Phase 54c's evidence-backed workflow
(`context-researcher` → `documentation-agent` → review → a small
`REQ-`-backed implementation), scoped **only** to this one question, not
the whole adapter. This is exactly the "genuinely uncertain, real
pre-implementation question" Phase 54c's own retro named as the next
needed test for that methodology — and keeps the rest of this phase
(config parsing, dependency tree, schema widening) on the normal,
directly-implemented track, since those genuinely don't have the same
open-question shape.

## 5. Testing strategy

Per `decisions/0014`'s own standing rule (fixture-based tests as the
*primary* strategy; live smoke tests wherever the toolchain is actually
present): every adapter method's core parsing logic is tested against
hand-written fixture text (a small `package.yaml`, a small `stack dot`/
`stack ls dependencies` output sample) via the same `_run_json`-adjacent
seam pattern other adapters use (adapted for text output, not JSON,
since `stack`'s own tools don't offer a JSON mode — §3). **Because
`stack` is actually available in this environment**, this phase also
gets real, `pytest.mark.skipif(shutil.which("stack") is None, ...)`-guarded
live smoke tests run directly against `hledger-lib`'s real
`package.yaml`/`stack dot`/`stack ls dependencies` output — the second
adapter (after npm/Python) to get this from day one, unlike Cargo's
still-outstanding gap. `decisions/0014`'s own account of what this
already caught for npm/Python (two real discrepancies fixtures alone
would have hidden) is the direct justification for doing the same here
rather than shipping fixture-only coverage by default.

## Scope

**In scope:**

- `src/codecompass/core.py::Ecosystem` gains `HASKELL`.
- `src/codecompass/graph.py`: `vendors.ecosystem` CHECK widened;
  `_SCHEMA_VERSION` "7" → "8"; migration docstring updated (mirrors
  Phase 54c's own just-completed precedent exactly).
- `src/codecompass/discovery.py`: `package.yaml` manifest discovery
  (hpack `dependencies:` list → dependency names), added to the existing
  discoverer table.
- `src/codecompass/symbols.py::extract_haskell_symbols` — module export
  list extraction, scope resolved per §4's own process.
- `src/codecompass/adapters/haskell.py` (new) — the full `HaskellAdapter`
  class, all five `EcosystemAdapter` methods.
- `src/codecompass/adapters/__init__.py` — dispatch table entry.
- Fixture-based unit tests (primary) + `stack`-availability-gated live
  smoke tests (this environment has `stack`, so these actually run) for
  every new function/method above.
- `architecture/overview.md`/`docs/` updated wherever the npm/Python/
  Cargo adapter trio is currently described as the complete set.
- One new ADR if the interface needs any real change to accommodate
  Haskell (expected minimal-to-none per `decisions/0002`'s own design —
  confirmed, not assumed, once the adapter is actually built).

**Explicitly deferred / out of scope:**

- `src/codecompass/usage.py`'s Haskell import detection (a consuming
  project's own source scan) — Phase 61's own scope, not this phase's.
- Source location resolution for an externally-fetched,
  `~/.stack/snapshots/`-resident dependency (only same-project workspace
  members are handled this phase) — a real, disclosed boundary.
- Any non-hpack (`.cabal`-only, no `package.yaml`) project — deferred
  until a real project without `package.yaml` is actually the proving
  case (hledger itself uses hpack throughout).
- Any AI/semantic interpretation of Haskell source — mechanical
  detection only, matching the determinism-first boundary every other
  adapter already holds.
- Tracking hledger-lib as a real CodeCompass vendor and evaluating it
  (Phase 61's own scope).

## Design decisions

- **`stack dot`, not `stack ls dependencies`, is the tree source** — a
  real finding from live-checking both commands this planning pass,
  not assumed from the other adapters' own JSON-tooling precedent.
- **Hand-roll `package.yaml` parsing, scoped to the specific top-level
  keys needed**, rather than adding a `PyYAML` dependency — flagged
  explicitly for review (§3), since it's a real judgment call this plan
  doesn't want to make silently.
- **API-surface extraction routed through Phase 54c's workflow, scoped
  narrowly to that one sub-question** — flagged explicitly for review
  (§4), since committing CodeCompass's own development process to reuse
  an experimental, not-yet-generally-validated workflow is itself a
  real choice, not a foregone conclusion.
- **Source-location scope limited to same-project workspace members**
  this phase — the real, immediate proving case (`hledger-lib` within
  `hledger`) needs nothing more, and guessing at the external-dependency
  case without a real one to test against would repeat exactly the
  "designed speculatively, not from evidence" mistake this project's
  own conventions exist to avoid.

## Files

- `src/codecompass/core.py` — `Ecosystem.HASKELL`.
- `src/codecompass/graph.py` — CHECK-enum widening, `_SCHEMA_VERSION` 8.
- `src/codecompass/discovery.py` — `package.yaml` discoverer entry.
- `src/codecompass/symbols.py` — `extract_haskell_symbols`.
- `src/codecompass/adapters/haskell.py` (new).
- `src/codecompass/adapters/__init__.py` — dispatch entry.
- `tests/test_core.py`, `tests/test_graph.py`, `tests/test_discovery.py`,
  `tests/test_symbols.py`, `tests/test_adapters_haskell.py` (new) —
  fixture tests + `stack`-gated live smoke tests.
- `architecture/overview.md`, `docs/` — updated wherever the adapter
  trio is described as complete.
- `decisions/00NN-...md` — only if the interface actually needs a
  change (checked, not assumed).
- If §4's review-gate recommendation is approved:
  `planning/knowledge/haskell-api-surface-extraction/` (new feature
  directory, Phase 54c's own model) for that one sub-question.
- `planning/retros/phase-60-minimal-haskell-adapter.md` — the retro.

## Verification

- Every new function/method has fixture-based unit test coverage
  (primary strategy, `decisions/0014`).
- `stack`-availability-gated live smoke tests actually run in this
  environment (not merely written and skipped) and pass against the
  real `hledger-lib` package.
- A real, end-to-end confirmation: register `hledger-lib` (or a small
  synthetic Haskell package, whichever proves more practical once the
  adapter exists) in a scratch project's `vendor.toml` with
  `ecosystem = "haskell"`, run a real `codecompass sync`, and confirm
  the resulting `context-graph.db` row's `installed_version`/
  dependency-tree/API-surface content matches real, independently
  checked values — not just that the sync command exits zero.
- `pytest`/`ruff check .`/`check_user_docs.py --strict` all clean.
- `release-phase-auditor` PASS or PASS WITH NON-BLOCKING OBSERVATIONS.

## Done when

Standard DoD (`CLAUDE.md` §5) + all five `EcosystemAdapter` methods
implemented and both fixture-tested and live-smoke-tested + the real
end-to-end confirmation above passes + `architecture/overview.md`/
`docs/` no longer describe three adapters as the complete set + a retro
that states plainly whether `stack dot`'s DOT-graph parsing and the
hand-rolled `package.yaml` parsing held up against real `hledger-lib`
output without surprises, or what had to change + (if §4's workflow
route was approved) that sub-question's own retro-worthy result folded
into this phase's own retro, not a separate one.

---

## Review gate

Presented for review before implementation starts. Two judgment calls
worth explicit attention:

1. **Hand-roll `package.yaml` parsing vs. add a `PyYAML` dependency**
   (§3) — recommendation: hand-roll, scoped narrowly, consistent with
   this project's standing "smallest justified fix" discipline. If a
   real Haskell package's manifest later proves the hand-rolled parser
   insufficient, that becomes real evidence for revisiting this choice,
   not a reason to guess at the fuller need now.
2. **Route the API-surface-extraction sub-question through Phase 54c's
   evidence-backed workflow** (§4) — recommendation: yes, scoped only to
   this one question, since it is this project's first genuinely
   open, real pre-implementation design question since that workflow was
   built, and Phase 54c's own retro explicitly named exactly this kind
   of case as the next needed test. If the user prefers keeping Phase 60
   entirely on the normal, directly-implemented track (deferring the
   workflow's next real test to a later phase), that's a smaller,
   equally valid choice — just say so and this phase proceeds without
   it, implementing the API-surface extraction directly instead.
