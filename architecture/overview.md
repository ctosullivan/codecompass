# Architecture overview

This document describes codecompass's **current** design — component
responsibilities and how they fit together. Unlike `decisions/`, which
records the historical *why* behind a choice and is append-only, this file
is a living document updated in place as the system evolves. When in doubt
about *why* something is designed the way it is, check `decisions/`; when
you want to know *what exists now*, check here.

As of Phase 7, the core data model (`codecompass.core`), `vendor.toml`
parsing (`codecompass.config`), all three ecosystem adapters
(`codecompass.adapters`), per-ecosystem symbol/purpose extraction
(`codecompass.symbols`), deterministic tree generation
(`codecompass.deptree`, `codecompass.filetree`), per-vendor `CLAUDE.md`
templating (`codecompass.claude_md`), per-vendor sync orchestration
(`codecompass.sync`), root routing-table injection (`codecompass.index`),
manifest-based `vendor.toml` bootstrap and zero-question auto-discovery
(`codecompass.discovery`), upstream repository resolution
(`codecompass.source_resolution`), AI-gated grounded-description
generation (`codecompass.grounded_description`, replacing Phase 5's
`context_path`-gated gap analysis — `decisions/0019`), Skill/Cursor
export (`codecompass.skill`), severity-aware staleness checking
(`codecompass.staleness`), and the single-vendor chat REPL
(`codecompass.chat`, grounded on persisted digest files, never live
regeneration — `decisions/0023`) are all implemented — bare `codecompass`,
`init`, `sync` (including `--budget`), `index`, `check` (including
`--strict`/`--fix`), `promote`, and `chat <vendor>` are real CLI
commands, not stubs. The MVP spans phases 0-8 (`decisions/0022`); all
eight are now `done` (a `v0.1` tag/release has not yet been cut).
Bare `codecompass chat` project-root routing and the whole-project
dependency rollup, described in the Chat REPL section below, remain
post-MVP (Phase 9) target design; see `planning/CONTEXT.md` for current
status.

## Core data model

- **`VendorConfig(name, ecosystem)`** — one entry per dependency, sourced
  from `vendor.toml`. `context_path` (a Phase 5 field) was removed in
  Phase 7 (`decisions/0019`); the per-vendor `depth` toggle
  (`SURFACE`/`FULL`, originally `decisions/0001`) was removed in Phase 16
  once usage-driven enrichment (`decisions/0031`) and unconditional
  cloning (`decisions/0033`) made it meaningless — every tracked vendor
  now gets the same deterministic treatment on `sync`, and AI enrichment
  eligibility is derived from the context graph's actual usage evidence,
  not a config field. A legacy `vendor.toml` entry still carrying a
  `depth = "..."` line keeps parsing without error (`codecompass.config`
  simply never looks at that key). See
  [`docs/config-schema.md`](../docs/config-schema.md) for the file format.
- **`DepNode(name, version, children, dev_only, side_effects)`** — one node
  in a dependency tree, ecosystem-agnostic. `side_effects` captures things
  like postinstall scripts or native binary downloads that are invisible in
  a raw manifest but explain real-world install size/behavior.
- **`RepositoryLocation(url, subdirectory)`** — a vendor's resolved
  upstream repository (Phase 7, `decisions/0021`), returned by each
  adapter's `repository_url()`. `subdirectory` is set only where an
  ecosystem can express "this package is part of a larger repo" (npm's
  `repository.directory`); `None` means the repository root is the
  package root.
- **`VendorDigest`** — the aggregate return type each vendor's generation
  produces: config, installed version, generated trees, API surface,
  optional `technical_description`/`conversational_overview` (renamed
  from Phase 5's `gap_analysis` field in Phase 7 — same dual-audience
  shape, different generation mechanism). Carries no staleness
  information — `check` (Phase 6) reads persisted per-vendor `CLAUDE.md`
  files directly rather than building a `VendorDigest`, the same pattern
  `index.py` established in Phase 4, and returns its own
  `codecompass.staleness.VendorStaleness` type instead. An earlier
  `is_stale` stub on this class, speculatively added in Phase 1, was
  removed in Phase 6 once it became clear no code path would ever
  populate it. See **Known footguns** below.

## Adapter interface

`EcosystemAdapter` (ABC, `src/codecompass/adapters/base.py`) is constructed
with `(config: VendorConfig, project_root: Path)` and defines five methods
every ecosystem implements: `installed_version() -> str`,
`source_location() -> Path`, `readme_and_api_surface() -> str`,
`repository_url() -> RepositoryLocation | None` (Phase 7 —
`decisions/0021`), `dependency_tree() -> DepNode`. Adding a new ecosystem
means writing one adapter class against this interface, not touching
core logic.

`repository_url()` resolves the vendor's upstream repository from
locally-available package metadata only — never a network call, unlike
the clone `codecompass.source_resolution` performs from its result. Per
ecosystem: npm reads `package.json`'s `repository` field (string,
`git+`-prefixed, or `github:`-shorthand — all normalized to a plain
`git clone`-able URL; an object form's `directory` key is respected for
monorepo packages); Python reads the installed package's `Project-URL`
metadata entries (PEP 621 `project_urls`, already present locally in
`METADATA`/`PKG-INFO` — no PyPI network call needed), checking key
variants ("Source", "Repository", "Code", "GitHub", "Homepage") in that
priority order since PyPI packages don't standardize this field's
labeling; Cargo reads `cargo metadata`'s package-level `repository`
field, with no equivalent to npm's `directory` (a known, accepted
limitation for workspace crates sharing one repository URL). Returns
`None` if nothing resolves — callers treat that as fail-loud, never a
fallback trigger (`decisions/0021`).

`dependency_tree()` returns the **raw, fully-expanded** tree exactly as
the underlying tool reports it — no diamond-dependency dedup. Dedup into
"see X above" back-references is Phase 3's tree-*rendering* concern, not
this method's tree-*construction* concern.

All three adapters call subprocesses through a shared `_run_json(cmd,
cwd)` seam in `base.py`, which resolves `cmd[0]` via `shutil.which` before
invoking it (needed cross-platform — see **Known footguns**) and wraps
failures into `AdapterError`. Tests monkeypatch this seam per-module to
inject fixture JSON rather than requiring a real toolchain — see
[`decisions/0014`](../decisions/0014-adapter-tests-use-fixture-mocking-not-live-subprocesses.md).

MVP ships three adapters on day one — npm, Python, Cargo — rather than
starting npm-only. See
[`decisions/0008`](../decisions/0008-mvp-ships-three-adapters-day-one.md).

- **npm adapter** — version/location read `node_modules/<name>/package.json`
  directly (no subprocess); tree via `npm ls <name> --json --all` (the
  `--all` flag is required — bare `npm ls --json` truncates to top-level
  only). `dev_only` cross-references the *root* project's `package.json`
  `devDependencies` against every node's name, regardless of depth — not
  propagated to a marked node's own children (see **Known footguns**). API
  surface via README + up to 5 `.d.ts` files, capped for cost/size control
  — that cap is a known limitation, not a validated final number (see
  **Known footguns**). `side_effects` picked up from the vendor's own
  `package.json` `scripts.postinstall`, if present.
- **Python adapter** — version/location via `importlib.metadata`/
  `importlib.util.find_spec` (no subprocess); tree via `sys.executable -m
  pipdeptree --output json-tree --packages <name>` (invoked as a module of
  the current interpreter, not a bare PATH lookup, so it's found
  regardless of venv activation state; the flat/deprecated `--json` output
  is the wrong shape — every installed package with only direct deps
  each, not a single-rooted tree). API surface has no single canonical
  source like `.d.ts` — uses `.pyi` stub files where present, else falls
  back to static `ast` parsing of `__all__`/docstrings (chosen over
  actually importing the module, which would execute unrelated
  module-level side effects purely to generate documentation). `dev_only`
  is always `False` — `pipdeptree` output carries no such field, a real
  structural difference from npm, not an oversight.
- **Cargo adapter** — version/location via `cargo metadata
  --format-version 1 --no-deps`; tree via the full `cargo metadata
  --format-version 1` call, walking the resolve graph's adjacency list
  cross-referenced against each package's declared dependency `"kind"`
  (`"dev"` vs `null`) for per-edge `dev_only` — a cleaner signal than npm
  has. API surface via a coarse, line-based scan for `pub fn`/`pub
  struct`/`pub enum`/`pub trait` (+ preceding `///` doc comment) — no
  standardized doc-comment extraction assumed; misses multi-line
  signatures (see **Known footguns**). `rustdoc --output-format json`
  remains a documented future refinement, not attempted since no
  toolchain is available locally to validate its shape against.
  **Unverified against real cargo output** — built and tested entirely
  against hand-written fixture JSON (see **Known footguns**).

See [`decisions/0002`](../decisions/0002-adapter-approach-differs-per-ecosystem.md).

## Symbol/purpose extraction (`codecompass.symbols`)

`Symbol(name, purpose)` plus one no-AI, no-subprocess extractor per
ecosystem, each `Path -> list[Symbol]`: `extract_python_symbols` (`ast`-
based top-level `def`/`class` + docstring), `extract_rust_symbols`
(line-based `pub fn`/`struct`/`enum`/`trait` + `///` doc-comment scan),
`extract_npm_symbols` (regex scan of `.d.ts` `export function/class/
interface/const/type/enum <name>` + a leading JSDoc line). `purpose_for_file(path,
ecosystem)` dispatches to the matching extractor by ecosystem *and* file
suffix, falling back to a generic leading-comment-marker scan (`#`, `//`,
`/*`, `"""`, `'''`) for files no ecosystem parser claims. Extraction
functions never raise — a file that fails to parse returns `[]`/`None`.

This module is shared: `adapters/cargo.py` and `adapters/python.py` call
into it for their `readme_and_api_surface()` output (generalized from
private per-adapter helpers in Phase 2), and `filetree.py` (below) calls
it for per-file purpose annotations and the symbol index. See
[`decisions/0015`](../decisions/0015-symbol-extraction-reuses-adapter-parsing-per-ecosystem.md).

## Tree generation — deterministic, always free

`FILETREE.md` and `DEPTREE.md` (plus `filetree.json`/`deptree.json`
sidecars) involve **no AI calls** and run on every `sync` for every
tracked vendor. `codecompass.deptree` renders from a `DepNode` tree;
`codecompass.filetree` renders from `sync_vendor`'s clone-or-fallback
root, not unconditionally `source_location()` — **since Phase 13**, that
root is `vendor/<name>/src/`'s clone content (via
`codecompass.source_resolution`, `decisions/0021`) for **every** vendor,
since cloning is unconditional (`decisions/0033`); when this run's clone
attempt fails, it falls back to
the vendor's **locally-installed** source directory (`source_location()`)
instead, the same fallback semantics already established for the
`vendor/<name>/src/` snapshot itself. This is a real, visible output
change: `FILETREE.md` now reflects a vendor's actual upstream repository
(README, docs, tests, examples included) rather than a possibly-trimmed
local install, for every tracked vendor whose clone succeeds. Both tree
renderers are wired into `sync.py` (Phase 4), which writes their output to
`FILETREE.md`/`DEPTREE.md`/`filetree.json`/`deptree.json` under
`vendor/<name>/`.

- `deptree.render_deptree_markdown(root: DepNode, *, max_depth: int = 20)
  -> str` / `render_deptree_json(root, *, max_depth=20) -> dict` —
  **deduplicate diamond dependencies**: render each unique `name@version`
  once, back-reference repeats (`(see lodash@4.17.21 above)` in Markdown,
  `{"ref": "lodash@4.17.21"}` in JSON) rather than re-expanding. The
  single biggest token-reduction lever for real npm trees. Dev-only
  children always collapse to a single count line
  (`N dev-only dependencies (not shown)`), never an enumerated list, at
  every level. Past `max_depth`, an explicit collapse notice is emitted
  (`truncated at depth N — see deptree.json for the full tree` in
  Markdown, `"truncated": true` in JSON) — never a silent truncation.
- `filetree.render_filetree_markdown(root: Path, ecosystem: Ecosystem, *,
  action_pointer: tuple[str, str] | None = None) -> str` /
  `render_filetree_json(root, ecosystem, *, action_pointer=None) -> dict`
  — a deterministic (sorted), pruned walk: drops `dist/`, `build/`,
  `.git/`, `__pycache__/`, `node_modules/`, `.venv/`/`venv/`,
  `test/`/`tests/`/`__tests__/`/`fixtures/` directories and
  `*.min.js`/`*.map` files — noise that adds tokens without adding
  navigation value. Omits version numbers (that's `DEPTREE.md`'s job) but
  includes a one-line purpose annotation per file via
  `symbols.purpose_for_file` where inferable.
- `filetree.build_symbol_index(root: Path, ecosystem: Ecosystem) -> str`
  — a **flat, greppable symbol index** (`name -> path`) built from every
  file's `symbols.extract_symbols_for_file` output, closer to a ctags
  model than a directory listing. Nested trees are for first-read
  orientation; flat indexes are for "jump straight to the thing" on a
  targeted question. Capped at 200 entries with an explicit `+N more, not
  shown` notice if exceeded — same never-silent-truncation rule as the
  depth cap above. Renders as a `## Symbol index` section within
  `FILETREE.md` itself (`sync.py`), not a separate sidecar file.
- **Cross-linking FILETREE entries to description action pointers**
  (e.g. `src/commonmark-rules.js  ← ACTION TARGET: override
  fencedCodeBlock here`) — implemented in Phase 5 via the
  `action_pointer` parameter above (mechanism unchanged by Phase 7's
  gap-analysis-to-grounded-description swap). `sync_vendor` threads
  `(action_pointer_file, action_pointer_note)`, read from this vendor's
  current enrichment record in the context graph (Phase 16,
  `decisions/0035`), into both `render_filetree_markdown` and
  `render_filetree_json`; a vendor with no enrichment record yet passes
  `None` and the parameter has no effect.

## Grounded description — retired; `sync_vendor` now reads it back (Phase 16)

`codecompass.grounded_description` — the original one-call-per-vendor,
`depth = FULL`-gated AI description step this section used to document —
is **deleted** as of Phase 16 (`decisions/0035`). It made a single
forced-tool-use call against `claude-haiku-4-5-20251001` per `depth =
full` vendor, on *every* `sync` run, uncached; that entire mechanism is
gone. Usage-driven, batched AI enrichment (`codecompass.enrichment`, see
**Batched enrichment** below) is the sole remaining generator of a
vendor's Description content, and it writes what it generates straight to
the context graph's `vendor_enrichment` table (`graph.record_enrichment`)
— `sync_vendor` itself makes no AI call, ever.

**What `sync_vendor` does instead**: before building a vendor's
`VendorDigest`, it opens a genuine read-only connection to
`context-graph.db` (the same cheap, side-effect-free pattern
`index.py`'s `_open_graph_readonly` already used — `None`, gracefully, if
the file doesn't exist yet) and looks up that vendor's current
`vendor_enrichment` row, if any. Found or not, this is a pure read: no
retrieval, no prompt, no API call, no write. If found, its four fields
(`technical_description`, `conversational_overview`,
`action_pointer_file`, `action_pointer_note`) populate the digest exactly
as a live-generated description used to; if not, they stay `None`,
same as an unenriched vendor always looked. This makes a from-scratch
`CLAUDE.md` regeneration — including a plain whole-project `sync` that
touches every tracked vendor, not just newly-enriched ones — idempotent
with respect to enrichment: it always reproduces whatever the graph
currently says, rather than either requiring `sync_vendor` to somehow
preserve file content it isn't re-deriving, or (the bug this fix
replaces) silently dropping the Description section on every ordinary
resync because nothing in the deterministic path ever populated it.

**Failure handling**: `description_error` is set only by a source-clone
failure (`SourceResolutionError` — no repository field, `git` missing,
network failure, or a declared monorepo subdirectory that doesn't exist);
`vendor/<name>/src/` falls back to the old local-install-sourced copy
(`decisions/0004`) so standalone browsing still has *something*. There is
no longer a second failure point here — no AI call happens inside
`sync_vendor` to fail. A clone failure and an existing enrichment record
are unrelated: `claude_md._render_description_section` does not consult
`description_error` at all, so a vendor with a good enrichment record
still shows its Description section even on a run where this particular
clone attempt failed (see **Per-vendor CLAUDE.md structure** below).

**No more `sync`-level AI budget gate**: `sync_all` used to run
`check_budget` once, before any vendor's `sync_vendor`, aborting the
whole run before any output was written if the estimated cost of this
run's pending `depth = full` generation calls exceeded `--budget`. That
gate is deleted along with the generation it was guarding. The one
AI-cost budget gate left in the codebase is Phase B enrichment's, in
`cli.py`'s `_maybe_run_enrichment` (see **Batched enrichment** below);
`sync --budget`/bare `codecompass --budget` are passed through to it, not
consulted by `sync_all`/`sync_vendor` themselves.

## Per-vendor CLAUDE.md structure (`codecompass.claude_md`)

`render_vendor_claude_md(digest: VendorDigest) -> str`. Sections, in
order:

1. **Metadata** — ecosystem and a `**Installed version:**` line (the
   `**Depth:**` line was removed in Phase 16 along with the field).
   This exact format (`\*\*Installed version:\*\*\s*(\S+)`) is what
   `claude_md.read_installed_version` regexes against — a shared helper
   both `staleness.py` (Phase 6) and `index.py` (Phase 4, populating the
   routing table's Version column) call, rather than each keeping its own
   copy of the regex. It is load-bearing, not cosmetic.
2. **Grounding preamble** — fixed instructional text: the pinned version
   is authoritative over training knowledge for this library. This is the
   actual mechanism that changes agent behavior — without an explicit
   "prefer this over what you already know" instruction, an agent has no
   signal to override its training data.
3. **Public API surface** — `digest.api_surface`.
4. **Description + action pointer** — `digest.technical_description` plus
   an `**Action pointer:**` line when `digest.action_pointer_file` is set.
   Omitted entirely (no heading at all) when `technical_description` is
   unset — a vendor with no enrichment record yet. As of Phase 16
   (`decisions/0035`), `digest.description_error` is a source-clone
   failure, not a description failure, and this section no longer
   consults it at all: a vendor with a good enrichment record still shows
   its Description even on a run where this sync's own clone attempt
   failed, since the two are unrelated once description content comes
   from the graph rather than this run's own generation attempt.
5. **Known gotchas** — deterministically derived from `digest.side_effects`
   (the dependency tree's root `DepNode.side_effects`, e.g. npm's
   postinstall-script detection) rather than left empty or AI-generated.
   A vendor with none detected renders a fixed "No known side effects
   detected." line.
6. **Quick links** — relative links to `./FILETREE.md`, `./DEPTREE.md`,
   and a backlink to the project root `CLAUDE.md`.

**Phase 14 adds a second, narrower write path** alongside this
from-scratch renderer: `update_description_section`/`read_enrichment_hash`
(see **Batched enrichment** above) rewrite just an already-rendered
file's Description section and a `**Enrichment symbol-set hash:**`
metadata line in place, for `codecompass.enrichment`'s batched,
usage-driven enrichment. This path never had an eligibility gate — it's
only ever invoked for a vendor `codecompass.enrichment` just actually
enriched, never as a generic re-render. Section 4's from-scratch render
path used to differ (gated on `depth is FULL`, to avoid a misleading
Description note on a vendor that was never eligible for the old
grounded-description step); Phase 16 (`decisions/0035`) drops that gate
too, since `technical_description`'s own truthiness already says
everything the `Depth` gate used to — the two write paths now agree on
exactly the same "is there enrichment content" test, reading from and
writing to the same `vendor_enrichment` table.

## Two consumption modes

Both must work:

1. **Standalone** — `cd vendor/<name> && claude`. Requires a *copied*
   pinned source snapshot at `vendor/<name>/src/` for `FULL` vendors, NOT a
   reference into `node_modules` — package managers prune/dedupe/reinstall
   `node_modules` contents, so it isn't a stable pin target. See
   [`decisions/0004`](../decisions/0004-vendor-src-snapshot-not-node-modules-reference.md).
   Since Phase 7, the snapshot is a shallow `git clone` of the vendor's
   own upstream repository (`codecompass.source_resolution`,
   `decisions/0021`) rather than a copy of the local install — richer
   (a published package often excludes docs/tests) and, per
   `decisions/0004`'s own underlying concern, at least as stable a pin
   target. If source resolution fails, `sync_vendor` falls back to the
   original Phase 4 behavior — a pruned copy of `source_location()`
   (loosely: strips `node_modules`/`dist`/`build`/`.git`-style noise only
   and keeps `test`/`tests`/`__tests__`/`fixtures` directories) — so
   standalone mode always has *something* to reference, never nothing.
   Includes a backlink to the project root `CLAUDE.md` so the agent can
   escalate from "how does this library work" to "how is it used in our
   project."
2. **Routed from project root** — a routing table is injected into the
   consuming project's own root `CLAUDE.md`, between
   `<!-- codecompass:start -->` / `<!-- codecompass:end -->` markers.
   Idempotent regeneration via `codecompass.index.update_root_claude_md`:
   handles both the first-run case (markers don't exist yet, the block is
   appended) and the regenerate case (`re.sub` with `DOTALL` replaces
   just the marked block), without clobbering hand-written content around
   it. Table columns: Vendor, Path, Version, Depth, Deps, Consult when —
   paired with an explicit routing instruction sentence, since the table
   alone is inert data. As of Phase 4: `index` **reads each vendor's
   already-synced `CLAUDE.md`** (regexing the Metadata section's
   `**Installed version:**` line) rather than re-running `sync` — this
   keeps `index` cheap and side-effect-free even after Phase 5 adds an
   AI-gated step to `sync`, and a vendor with no synced `CLAUDE.md` yet
   shows `_not synced_` rather than erroring. The Version column still has
   no ✅/⚠ freshness indicator — `check` (Phase 6) reports staleness in
   its own separate table (`codecompass check`) rather than being wired
   into `index`'s routing table, a deliberate scope boundary rather than
   an oversight (see **Known footguns**); the Deps column links to
   `DEPTREE.md` rather than showing a live dependency count, since `index`
   deliberately has no adapter/tree data to draw one from.

## Staleness checking (`codecompass.staleness`)

`check_all(configs, project_root) -> list[VendorStaleness]` /
`check_vendor(config, project_root) -> VendorStaleness`. Compares the
`**Installed version:**` line in a vendor's persisted `CLAUDE.md` (read
via `claude_md.read_installed_version`, shared with `index.py`) against
the ecosystem adapter's live `installed_version()` read. **Severity-aware,
not binary** (`Severity`: `NONE`/`PATCH`/`MINOR`/`MAJOR`/`UNKNOWN`): patch
delta is `NONE` (silent/ignored), minor delta is a warning that never
fails, major delta is the hard-fail case. `UNKNOWN` — either version
string doesn't parse as a `major.minor.patch` triple — is treated the same
as `MAJOR` for gating purposes, since an unclassifiable delta is a "can't
verify" state, not a "safe to ignore" one. See
[`decisions/0005`](../decisions/0005-severity-aware-staleness.md).

Never builds a `VendorDigest` — same reasoning `index.py` (Phase 4)
already established for staying cheap and side-effect-free. `VendorStaleness`
(`config`, `recorded_version`, `live_version`, `severity`,
`transitive_drift`, `error`) is its own lightweight result type, not
reused from anywhere else. A vendor whose adapter's live read itself fails
gets `error` set (caught locally — `check` isolates one broken vendor's
read rather than crashing the whole run, unlike `sync_vendor`, which lets
`AdapterError` propagate) and is treated as a `--strict` failure the same
way `MAJOR`/`UNKNOWN` is.

**Two run modes, `check`'s own flags, mutually exclusive with each
other**:
- Bare `check` (no flags) — report-only. Always prints the severity table
  and exits 0, regardless of what it finds. For a human running it
  locally.
- `--strict` — the actual CI gate. Same table, but exits non-zero if any
  vendor has `MAJOR`/`UNKNOWN` severity or a live-read `error`. Never
  regenerates anything — a human (or a scheduled job) runs `sync`/`--fix`
  separately, so an automated PR check doesn't unpredictably spend
  AI-pass tokens.
- `--fix` — regenerates every vendor where `recorded_version !=
  live_version` (including a vendor that's never been synced at all) or
  `transitive_drift` is set, via the exact same `sync_vendor` `sync`
  itself uses — unmodified, including a fresh gap-analysis call for
  `depth = full` vendors. `check`'s own `--fix` loop (not `sync_vendor`)
  wraps each regeneration in `try/except AdapterError`, so one vendor's
  broken adapter read doesn't abort the rest of the batch; exits non-zero
  if anything failed (an adapter error or a gap-analysis error), 0
  otherwise.

**Transitive-vs-vendor drift** — a full diff, not just a root-version
comparison. When a vendor's own root version is unchanged
(`severity is NONE`), `check_vendor` reads the persisted `deptree.json`,
calls the adapter's `dependency_tree()` fresh (a local
subprocess/metadata read, same cost profile `sync` already pays — no AI,
no network beyond what the adapter does at `sync` time), and flattens both
into `name -> {versions}` maps via a shared `_flatten` helper (reusing
`deptree.render_deptree_json`'s already-deduplicated shape for the live
side, resolving `{"ref": "name@version"}` back-references via
`rpartition("@")` so scoped npm names like `@babel/core` parse correctly).
A mismatch sets `transitive_drift = True` — informational only, it never
affects `--strict`'s exit code, consistent with `decisions/0005` treating
transitive-only drift as lower risk than the vendor's own version moving.

**Hook placement**: pre-commit only fires when a lockfile actually changed
(`package-lock.json`, `pyproject.lock`, `Cargo.lock`) — not on every
commit. Pre-commit is a courtesy/fast-fail; **CI's `codecompass check
--strict` is the actual enforcement point** that blocks merge.

## Multi-tool export (Skills, Cursor) — `codecompass.skill`

**Agent Skills are the primary multi-tool export target** (see
[`decisions/0013`](../decisions/0013-agent-skills-as-shared-context-selection-source.md)),
motivated by a reliability gap in the root `CLAUDE.md` routing table: its
"consult this vendor's digest first" instruction is a soft instruction
competing for attention with everything else in context, so an agent
confident in its training knowledge may never read the digest at all —
precisely the failure mode codecompass exists to prevent. A Skill's
description is mechanically part of how Claude decides what's relevant to
load, a stronger (though not absolute) guarantee than the routing table's
instruction-following alone. Implemented in Phase 7 as part of
`codecompass promote` (`decisions/0018`), not a separate later phase — the
Skill for a vendor is generated at the moment it's promoted, the same
call that generates its grounded description.

One Skill per `depth = FULL` vendor, generated at
`.claude/skills/codecompass-<vendor>/SKILL.md`:
- The trigger description is built from data already generated — a
  condensed conversational overview — not a new AI call. **Description
  length is a real, ongoing tuning knob, not a one-time writing task**:
  every skill's name+description loads into every session
  unconditionally, so a long description that maximizes one vendor's
  trigger accuracy has a real per-vendor cost that compounds as
  `FULL`-depth vendor count grows (`_VENDOR_SKILL_DESCRIPTION_CAP`, 400
  characters). Specificity (concrete API methods, file/function names,
  exact trigger situations) — not length — is what drives triggering
  accuracy.
- `FILETREE.md`/`DEPTREE.md` bundle as `references/` files inside the
  skill folder rather than inlining — progressive disclosure means they
  only cost tokens when Claude actually needs to navigate source.
- A wrapper script shelling out to `codecompass check <vendor>` at trigger
  time (a live staleness read instead of a cached line) is deferred to a
  later phase, not required for the initial export.
- A formal trigger-accuracy evaluation harness (a battery of test
  questions checked against whether the Skill actually loads) is not
  implemented — the same category of manual-verification gap Phase 5
  accepted for gap analysis against the live API (`decisions/0016`), now
  extended to Skill triggering.
- `depth = SURFACE` vendors don't get a per-vendor Skill — no grounded-
  description content exists to build a meaningful trigger description
  from. Since Phase 7, this gap is covered separately by the **tool-level
  Skill** (`decisions/0020`): a templated, non-AI-generated Skill at
  `.claude/skills/codecompass/SKILL.md`, generated unconditionally by
  `index` (and by bare `codecompass`) regardless of vendor count or depth
  — listing codecompass's own commands and the current vendor table, so
  an agent has a mechanical signal that codecompass exists even before
  anything has been promoted.

**Cursor `.mdc` export is retained, not replaced.** Cursor does not read
`CLAUDE.md` natively. Its modern context system is `.cursor/rules/*.mdc`
files with YAML frontmatter (`description`, `alwaysApply`) controlling
activation — the legacy single `.cursorrules` file is deprecated and
unreliable in Cursor's agent mode specifically, so it isn't targeted.
`.mdc` is a **generated export**, not a separately maintained file —
same technical-description content as the Skill, different serialization
— written to `.cursor/rules/codecompass-<vendor>.mdc` by `promote`
alongside the Skill. `alwaysApply: false` (token cost control, same
reasoning as the depth system); Cursor falls back to description-based
relevance without an explicit `globs` key — a `globs` field scoped to
wherever the vendor is actually imported in the consuming codebase is a
documented future refinement, not implemented in Phase 7 (would require
scanning the consuming project's own source, a different kind of input
than anything else `promote` reads). Cursor's glob-scoped file-pattern
activation is a different — potentially more precise, once implemented —
trigger model than Skills' description-matching, and not every Cursor
setup has Skills support, so this export stays alongside Skills rather
than being dropped.

**The `CLAUDE.md` root routing table is also retained, not replaced** — it
remains the fallback for any tool or context that doesn't support Skills
at all, including the Mode-1 standalone `cd`-into-vendor scenario (see
**Two consumption modes** above), which isn't a "current task the agent
judges relevant" situation the way Skills triggering assumes.

## `/discovery` custom slash command — `codecompass.commands`

**New in Phase 17.** A third generated-artifact type alongside Skills and
`.mdc` rules, but a genuinely different Claude Code mechanism from
either: a **custom slash command**, written to `.claude/commands/
discovery.md` and invoked explicitly by typing `/discovery` inside a
Claude Code session, rather than auto-triggered by description matching
the way Skills are. `codecompass.commands` follows `codecompass.skill`'s
render/write split (`render_discovery_command() -> str` /
`write_discovery_command(project_root: Path) -> None`) rather than
inventing a new pattern, but stays a separate module — different
directory convention, different frontmatter shape, no vendor-specific
content threaded in (unlike `render_tool_skill`, its content is entirely
static: it teaches Claude *how* to explore whatever a project's
codecompass output currently is, not what that output currently
contains).

**Generated unconditionally**, same trigger points and free/no-AI-cost
posture as the tool-level Skill: bare `codecompass` (`_bootstrap`) and
`codecompass index`. Whole-project `codecompass sync` does **not** also
call it, as of this phase — that call site has never called
`write_tool_skill` either (only `_bootstrap` and `index` do), so there was
no existing "same points write_tool_skill already is" precedent at that
third call site to actually mirror; see `planning/CONTEXT.md` for the
current status of this gap.

**Read-only by mechanical constraint, not just instruction.** Its
frontmatter sets `allowed-tools` — confirmed, as of this phase's
implementation date, to be supported identically for `.claude/commands/
*.md` files as for Agent Skills (same frontmatter reference, pre-approving
the listed tools for that invocation without a permission prompt) — to
`Read`/`Grep`/`Glob` plus narrowly-scoped `Bash(...)` patterns for exactly
two sanctioned escape hatches: `codecompass query`/`check`, and read-only
`sqlite3` access to `context-graph.db` for anything the canned `query`
subcommands don't cover. `Write`/`Edit` are never granted. The command
body also repeats, in plain instructional text (not solely relying on the
tool restriction), that it must never create a plan file or make a code
change — if answering a question would require one, it states that
explicitly and stops rather than proceeding.

**Indexed into the context graph the same way Skills/`.mdc` rules are**:
`skill_scan.scan_skills` (Phase 12's mapping module — the name predates
this phase but the function now covers a third artifact type, not just
Skills/`.mdc`) additionally globs for `.claude/commands/discovery.md` and,
if present, appends it as a `doc_artifacts` row (`kind='slash_command'` —
`doc_artifacts.kind`'s CHECK constraint was widened for this,
`schema_version` bumped from `"1"` to `"2"`, with `open_graph` migrating
an already-existing pre-Phase-17 `context-graph.db` by dropping and
recreating just the `doc_artifacts` table — safe, since that table (and
everything that cascades from it) is fully rebuilt by
`rebuild_deterministic` on every whole-project sync anyway, and
`vendor_enrichment`/`symbol_enrichment` have no foreign key to
`doc_artifacts` at all, so this migration can't reach them regardless).
Flowing through the same `scan_skills` return value it also participates
in `skill_scan.build_skill_mentions_edges`' word-boundary mention
detection, same as any other Skill/`.mdc` doc artifact.

`graph.skills_index`/`codecompass query skills` were not widened in this
phase — they remain hard-filtered to `kind = 'skill'`, so a
`/discovery`-generated `doc_artifacts` row doesn't currently surface
through `codecompass query skills`, only through a direct
`context-graph.db` read. See `planning/CONTEXT.md` for the current status
of this gap.

## Chat REPL

**The REPL is a primary consumption mode for vendor digests, not a
convenience layer bolted onto the markdown files** (see
[`decisions/0012`](../decisions/0012-conversational-first-repl-design.md)).
The digests (`CLAUDE.md`, `FILETREE.md`, `DEPTREE.md`, and — for `depth =
full` vendors whose grounded description succeeded — `OVERVIEW.md`, the
persisted conversational overview) are backing store for two consumers —
AI agents reading them directly (see **Two
consumption modes** above) and the REPL synthesizing them into
conversation — and content generation is written with "does this read
well spoken aloud in a casual chat" as a first-class constraint, not an
afterthought handled by reformatting at query time.

`codecompass chat <name>` — a lightweight terminal REPL, distinct from
just using Claude Code in the vendor folder. It loads only `CLAUDE.md`
(and `OVERVIEW.md`, if the vendor's been `promote`d) as system context and
calls the API directly (Haiku) with plain multi-turn text completion — no
forced tool-use, no tool-use/file-exploration loop — faster and cheaper
per query, but strictly narrower: it only knows what's in those two files,
not `FILETREE.md`/`DEPTREE.md` or the full pinned source. This tradeoff is
stated in the REPL's startup banner so a user doesn't over-trust an answer
beyond what the digest actually covers. Critically, `chat` never calls
`sync`/`promote` — it reads whatever's already on disk, so starting a
session never re-incurs a clone or an AI-generation call
(`decisions/0023`).

- **Explicit vendor** (`chat turndown`) — **implemented (Phase 8).** Loads
  that vendor's `CLAUDE.md`/`OVERVIEW.md` only, single system prompt, no
  routing needed. Works at any depth — a vendor with no `OVERVIEW.md` yet
  gets thinner grounding plus a `promote` hint, not a hard block.
- **No vendor specified** (project-root mode) — **not yet implemented
  (Phase 9).** Will load a **project-wide
  dependency rollup unconditionally at session start**, before any
  routing happens. The rollup is synthesized once per `sync` (not per
  query) from the already-generated per-vendor conversational overviews
  (see **Grounded description** above): dependency count by depth, a staleness
  rollup by severity, notable side-effect flags, and a short narrative.
  No new per-dependency AI calls — one cheap summarization pass over data
  that's already paid for. This exists because a large share of realistic
  casual usage ("anything risky in my deps right now," "why do we even
  use X," "what changed recently") doesn't cleanly signal either "vendor"
  or "project" the way keyword/phrase matching expects — waiting for a
  routing match before loading *any* project-level context would miss
  these. The REPL's startup banner states that the rollup is loaded, once,
  up front.

  Vendor-specific escalation still uses two-tier routing **on top of**
  that baseline rollup, across three possible context targets (a specific
  vendor, several vendors, or the project itself):
  - **Tier 1** (free, instant) — match against the **same generated
    Skill description text** that `promote` (Phase 7) produces for Claude
    Code's native Skills triggering (see
    [`decisions/0013`](../decisions/0013-agent-skills-as-shared-context-selection-source.md)),
    not an independently-authored keyword/alias list. One source of
    truth for "what fires on what" — Phase 9's REPL routing reads the
    same Skill-description data Phase 7 already generates, rather than
    duplicating it. If nothing matches, check for project-level signal
    instead (question
    references architecture, a roadmap phase, a past decision, or general
    "how does this project..." phrasing) and load **project context**
    (root `CLAUDE.md` + `architecture/` + relevant `decisions/` entries +
    `planning/CONTEXT.md`'s current-state section) rather than any vendor
    digest.
  - **Tier 2** (fallback, only if Tier 1 is ambiguous) — pass both the
    vendor routing table and a summary of available project-context
    sources, and let the model itself judge relevance (no extra API call),
    escalating to a one-shot Haiku classification call only if that's
    insufficient.
  - **Always print a visible context indicator line before answering** —
    e.g. `→ loaded turndown digest (exact match)` or `→ using project
    context (architecture/overview.md, decisions/0003-*.md)`. This tells
    the user what *additional* context, beyond the baseline rollup, grounded
    a given answer — the rollup itself isn't re-announced every turn, only
    at session start. If a question pulls in both a vendor digest and
    project context, the indicator line lists both explicitly rather than
    picking one to display.
  Loaded context (the baseline rollup, plus anything Tier 1/2 escalation
  adds) persists in the system prompt for the rest of the session (cheap
  to keep, cache-friendly); a soft cap (~3-4 loaded context sources beyond
  the rollup, LRU eviction) prevents a long mixed session from letting the
  system prompt grow unbounded.
- **Escalation when a question exceeds digest-only scope** (see
  [`decisions/0013`](../decisions/0013-agent-skills-as-shared-context-selection-source.md))
  — deep source inspection, execution, or reasoning beyond what a digest
  captures. Rather than answering confidently from incomplete context
  (the same over-trust risk flagged for digest-only answers generally),
  the REPL states the limitation and points at the already-generated
  `.claude/skills/codecompass-<vendor>/` folder as the handoff artifact for
  a full Claude Code session, already grounded via the same Skill —
  reusing Phase 7's `promote` output rather than inventing a separate
  context-packaging mechanism. The REPL's startup disclaimer ("this only
  knows what's in the digest") is extended to mention this escalation
  path exists, so a user hitting the boundary knows there's a next step
  rather than just receiving a lower-confidence answer.
- Rich handles presentation: `Panel` for the startup grounding disclaimer,
  `Markdown` for rendering answers, `Progress`/spinner for multi-vendor
  `sync` runs, `Table` for `check` output with stale rows highlighted.
  Since `check` also runs in CI, ANSI codes are explicitly guarded against
  polluting CI logs (`Console(force_terminal=...)` / `sys.stdout.isatty()`
  checks) rather than relying solely on Rich's auto-detection.

## Retrofitting to existing projects

**Two phases, back to back, both triggered from the same call sites**
(bare `codecompass` and whole-project `sync` — `init --scan` and
`sync <vendor>` are explicitly not trigger points): Phase A is the
always-free, no-prompts bootstrap; Phase B is usage-driven AI enrichment,
auto-triggered right after Phase A but kept behind a real disclose-and-
confirm gate. This is Phase 15's rewiring of `decisions/0031` (enrichment
is usage-driven, not a per-vendor `Depth` toggle) and `decisions/0033`
(`promote` retired; universal cloning + auto-triggered, disclosed
consent is the sole cost point) into the actual CLI — see those two ADRs
for the full rationale; this section describes the resulting flow.

**Phase A** (`decisions/0017`, Phase 7; extended Phase 15 with universal
cloning and a graph rebuild): auto-discovers manifests at the project
root (`package.json`, `pyproject.toml`, `requirements.txt`,
`Cargo.toml`), writes/refreshes `vendor.toml`, clones every vendor's
source (`decisions/0033` — extended from `depth = FULL`-only cloning),
regenerates trees, the routing table, and the tool-level Skill, and
rebuilds `context-graph.db` from the whole project's current state. No
prompts, no AI calls, regardless of project size. Re-running it on an
already-bootstrapped project is an **idempotent refresh**: newly
discovered dependencies are appended; already-tracked vendors are left
untouched by Phase A itself, so Phase A alone never pays AI cost no
matter how many times it's run.

`codecompass init --scan <manifest file> [--scan <manifest file> ...]`
(`codecompass.discovery`) remains as the explicit, scripted/CI-friendly
synonym — useful for naming specific manifests rather than relying on
root-level auto-discovery. `--scan` is a repeated flag, not one flag
followed by several space-separated files (not how a named Click/Typer
option works — the CLI reference's earlier draft syntax was corrected to
match in Phase 4). Unlike bare `codecompass`, it keeps its original
stricter contract: errors rather than overwriting if `vendor.toml`
already exists. Python discovery reads `[project.dependencies]` from
`pyproject.toml` and every non-comment, non-option line of
`requirements.txt` (Phase 7 addition) — not
`[project.optional-dependencies]`. `init --scan` is not a Phase A/B
trigger point itself — no cloning, no graph rebuild, no Phase B.

**Phase B** (`decisions/0031`, `decisions/0033`, wired in Phase 15):
after Phase A's graph rebuild, `enrichment.select_candidates` checks
which vendors the project's own source actually imports
(`graph.enrichment_candidates`, usage-driven — not a per-vendor toggle)
and don't already have up-to-date enrichment (a two-tier hash check —
DB-level and, for a fresh clone with no `context-graph.db` yet,
file-level against the committed `CLAUDE.md`). If any exist, `cli.py`
discloses an estimated cost (`enrichment.estimate_cost`) and asks for
confirmation (`typer.confirm`, skipped by `--yes`) before calling
`enrichment.run_enrichment_batches` + `enrichment.apply_results` — the
one step that calls the Anthropic API, batched across several vendors
per call rather than one call per vendor (unlike the retired `promote`).
`--budget <amount>` is checked via `enrichment.check_budget` *before any
API call*; if exceeded, Phase B aborts for this run without undoing
Phase A's already-written output, and the command exits non-zero.
Declining the confirmation prompt is not a failure — Phase A already
succeeded — and exits 0. Both bare `codecompass` and whole-project `sync`
gained `--yes`/`--budget` for this reason (`sync` already had `--budget`
for its pre-existing `depth = FULL` regeneration path, now shared by
Phase B too); `sync <vendor>` (a named vendor) skips both the graph
rebuild and Phase B entirely (`decisions/0025`).

`promote` is retired (`decisions/0033`) — its three former jobs (clone,
enrich, generate Skill/`.mdc`) are these two phases' automatic outcomes.
`codecompass query vendor <name>`/`check` are the replacement for
"inspect what promote would tell you," reading the graph rather than
requiring a vendor to have been manually escalated first.

## Context graph (`codecompass.graph`)

**Fully populated at both whole-project call sites and, as of Phase 15,
CLI-readable too.** `codecompass.graph` is the SQLite persistence layer
every phase in the v0.2 rework (10-16) builds on: a schema, a set of typed
row dataclasses that form the insertion contract for a full-rebuild
orchestrator, and a set of read-only query functions. Phase 10 built it as
a standalone library; Phase 11 was the first phase to actually populate it
from real project data — `sync.rebuild_project_graph` (below) — wiring in
`vendors`/`source_files`/`symbols`/`uses_edges` and calling that from
`cli.py`'s two whole-project call sites; Phase 12 extends the same call
site with the remaining five tables (`doc_artifacts`/`documents_edges`/
`skill_mentions_edges`/`routes_via_edges`/`depends_on_edges`), which
previously received empty lists. Phase 15 is the first phase to read it
back through the CLI: the new `codecompass query` command group renders
`unused_vendors`/`vendor_profile`/`symbol_profile`/`skills_index` as Rich
tables or raw JSON, `check` gains report-only coverage-gap sections built
on the same queries, and `index.py`/`skill.py` source their
"Enriched"/enrichment-count display from the new `has_enrichment` query —
each gracefully falls back to "no graph yet" rather than erroring if
`context-graph.db` doesn't exist. See
[`decisions/0032`](../decisions/0032-context-graph-stored-in-sqlite.md)
(SQLite over the original `decisions/0024` JSON-file choice) and
[`decisions/0025`](../decisions/0025-context-graph-rebuilds-only-on-whole-project-sync.md)
(the rebuild-trigger posture — full rebuild only on whole-project `sync`,
never incrementally — carried forward unchanged, just retargeted from "one
JSON file" to "wipe and rewrite every deterministic table").

**Storage**: `context-graph.db` at the project root, one SQLite database.
Gitignored (extends `decisions/0010`'s existing `vendor/` precedent — a
deterministic, cheaply regeneratable artifact). `open_graph(project_root:
Path) -> sqlite3.Connection` is the one function later phases actually
call to get a working handle: it resolves the db path, connects (creating
the file if absent), sets `PRAGMA foreign_keys = ON` (SQLite defaults this
off, and it must be set per-connection, not just once at the file level),
calls `init_schema`, and returns the connection. `init_schema(conn)` is an
idempotent `CREATE TABLE IF NOT EXISTS`/`CREATE INDEX IF NOT EXISTS` for
every table, seeding a `meta.schema_version` row on first call.

**Schema** — nine deterministic tables plus `meta` plus two enrichment
tables:
- `vendors`, `source_files`, `symbols` (unique per `(vendor_id, name)`,
  since symbol names aren't globally unique across vendors) — the graph's
  nodes.
- `uses_edges` (`source_file → vendor`/`symbol`, `symbol_id` nullable for
  a usage that resolves to a vendor but not a specific symbol),
  `doc_artifacts` (`kind` one of `claude_md`/`overview`/`skill`/
  `cursor_mdc`; `vendor_id` nullable for tool-level artifacts like the
  unconditional tool Skill, `decisions/0020`), `documents_edges` (a doc
  artifact documenting one symbol), `skill_mentions_edges` (a Skill
  mechanically mentioning a vendor and/or a source file — both nullable,
  independently), `routes_via_edges` (a vendor routed to a Skill),
  `depends_on_edges` (vendor-to-vendor dependency) — the graph's edges.
- `vendor_enrichment`/`symbol_enrichment` — the two tables that **survive
  every `rebuild_deterministic` call**, holding Phase 14's paid AI
  enrichment output (`technical_description`, `conversational_overview`,
  `action_pointer_file`/`action_pointer_note`, plus `symbol_set_hash` and
  `model`/`generated_at` for cache-key purposes). `DocChunk`/`EXPLAINS`
  tables from the former phase-9d design are explicitly not part of this
  schema at all (`decisions/0032`), not even as unused tables.

Every table with a foreign key to `vendors`/`symbols`/`doc_artifacts`/
`source_files` declares `ON DELETE CASCADE` — deliberate, so
`rebuild_deterministic` never has to manually clear dependent tables in a
specific order.

**Row dataclasses reference each other by natural key, not by pre-assigned
integer id** — `VendorRow` (keyed by `name`), `SourceFileRow` (keyed by
`path`), `SymbolRow` (keyed by `(vendor_name, name)`), `UsesEdgeRow`,
`DocArtifactRow` (keyed by `path`), `DocumentsEdgeRow`,
`SkillMentionEdgeRow`, `RoutesViaEdgeRow`, `DependsOnEdgeRow`. This is a
deliberate Phase 10 design choice, not spelled out verbatim in the SQL
schema itself: the detection logic that will construct these rows in
Phases 11-13 (an AST/regex walk over project source, doc/Skill mapping)
naturally produces vendor names, file paths, and symbol names — not
opaque database-assigned ids — and keeping the row dataclasses natural-key-
shaped means `graph.py` has no import dependency on those not-yet-existing
modules, avoiding any circular-import risk. `rebuild_deterministic`
resolves natural keys to integer primary keys internally.

**`rebuild_deterministic(conn, *, vendors, source_files, symbols,
uses_edges, doc_artifacts, documents_edges, skill_mentions_edges,
routes_via_edges, depends_on_edges) -> None`** wipes and rewrites every
deterministic table inside one transaction and updates
`meta.last_deterministic_rebuild_at`. **Never touches
`vendor_enrichment`/`symbol_enrichment`** — the mechanical reason Phase
14's enrichment output survives a later whole-project refresh. Because
both enrichment tables cascade from `vendors`/`symbols` on delete, "never
touches" is implemented, not just declared: `vendors` and `symbols` are
**upserted by their natural key** (`INSERT ... ON CONFLICT(name) DO
UPDATE`, respectively `ON CONFLICT(vendor_id, name) DO UPDATE`) rather
than deleted and reinserted, which preserves their integer id across a
rebuild and leaves any enrichment row referencing that id completely
untouched. Only a vendor or symbol that no longer appears in the new
fixture at all is deleted (correctly cascading away its enrichment too,
since the thing it enriched no longer exists). Every other table
(`source_files`, `uses_edges`, `doc_artifacts`, and the four edge tables
other than the ones above) carries no cross-rebuild identity worth
preserving and is unconditionally cleared and reinserted.

**Query functions**, each a plain read against already-populated tables —
none of them write, none of them decide staleness:
- `unused_vendors(conn) -> list[str]` — vendor names with zero
  `uses_edges` rows anywhere.
- `documented_but_unused(conn) -> list[tuple[str, str]]` /
  `used_but_undocumented(conn) -> list[tuple[str, str]]` — `(vendor,
  symbol)` pairs covering the two one-sided coverage-gap cases.
- `vendor_profile(conn, name) -> dict | None` — the vendor row plus its
  symbols, total usage count, documenting artifacts (linked directly or
  via one of its symbols), routed Skills, and its `depends_on` vendor
  names; `None` for an unknown name.
- `symbol_profile(conn, name) -> list[dict]` — every symbol row named
  `name` across every vendor (symbol names aren't globally unique), each
  with its own usage count and documenting artifacts.
- `skills_index(conn) -> list[dict]` — every `doc_artifacts` row with
  `kind='skill'`, its `origin`, and what it mechanically mentions via
  `skill_mentions_edges`.
- `enrichment_candidates(conn) -> list[dict]` — every vendor with at least
  one `uses_edges` row, its currently-used symbol names, and its existing
  `vendor_enrichment.symbol_set_hash` if any. `graph.py` deliberately
  doesn't decide staleness here — Phase 14's `enrichment.py` diffs the
  returned hash against a freshly-computed one itself.

**`record_enrichment(conn, vendor_id, **fields)` /
`record_symbol_enrichment(conn, symbol_id, purpose, generated_at)`** are
the only writers to the two enrichment tables, both upserting (`INSERT ...
ON CONFLICT DO UPDATE`) so a second call for the same vendor/symbol
updates in place rather than erroring or duplicating. Kept as separate
functions from `rebuild_deterministic` on purpose — a deterministic
rebuild and a paid enrichment write are different trigger points with
different costs, and conflating them would risk an enrichment write
becoming implicitly part of the "free, always safe to rerun" rebuild path.

### Batched enrichment (`codecompass.enrichment`)

**New in Phase 14 — library only, like Phase 10's `graph.py` was: nothing
here is called from `cli.py`/`sync.py` yet (Phase 15's job).** Conceptually
replaces `codecompass.grounded_description` (below), but that module stays
in place, unmodified, and still the one `sync_vendor` actually calls for
`depth = full` vendors through this phase — `Depth`/`promote` aren't
retired until Phase 15/16 (`decisions/0033`). The two modules coexist
through Phase 14; `grounded_description.py` is only deleted once Phase 15
rewires `cli.py`/`sync.py` off it entirely. `enrichment.py` ports
`_gather_material`/`_find_entry_point`/`_read_text`/`_first_existing` and
the `_call_anthropic` forced-tool-use pattern from
`grounded_description.py` near-verbatim (same caps, same
per-module-monkeypatch test seam — `decisions/0016`).

**Selection is usage-driven, not `Depth`-driven** — the whole point of
`decisions/0031`, already reflected in Phase 10's `graph.enrichment_candidates`
even though `Depth` itself isn't removed until later. `select_candidates(conn,
configs, project_root) -> list[EnrichmentCandidate]` takes every vendor
`graph.enrichment_candidates` reports as usage-proven, computes its
*current* symbol-set hash (`_compute_symbol_set_hash(vendor_name,
sorted(used_symbol_names), installed_version)`, sha256 over the three
joined with a separator byte that can't appear in any of them), and skips
it if that hash already matches — checked two independent ways
(`decisions/0032`'s belt-and-suspenders design): the DB-level
`vendor_enrichment.symbol_set_hash` `graph.enrichment_candidates` already
surfaces, and a file-level check via the new `claude_md.read_enrichment_hash`
against the committed `vendor/<name>/CLAUDE.md`. The file-level check is
the one that actually survives a fresh clone with no `context-graph.db` at
all (gitignored) — belt-and-suspenders, not redundant for no reason. A
vendor with no retrievable material (no README/docs/entry-point in its
`vendor/<name>/src/` clone — unconditional since Phase 13) is skipped
outright rather than aborting the run. `EnrichmentCandidate` carries
`installed_version` alongside `vendor`/`used_symbol_names`/`material` —
beyond the phase plan's field sketch, but required so
`run_enrichment_batches` can recompute the *exact* same hash later when
writing `EnrichmentResult.symbol_set_hash` back; without it the cache-key
contract silently breaks (a written hash that never matches what the next
`select_candidates` call recomputes, re-purchasing enrichment every run).

**Batched, not one call per vendor**: `plan_batches(candidates, *,
batch_char_budget=150_000) -> list[list[EnrichmentCandidate]]` greedily
groups candidates into as few batches as fit under the character budget
(a single oversized candidate still gets its own batch rather than being
split or dropped) — a conservative starting constant, flagged for
empirical tuning once Phase 15 makes a real multi-vendor batched call
reachable to test manually, the same treatment this project already gives
`_RAW_TEXT_CHAR_CAP` and friends. `run_enrichment_batches(candidates) ->
list[EnrichmentResult]` calls `_call_anthropic` once per batch against a
batched `_TOOL_SCHEMA` (forced tool-use; input schema is an array of
per-vendor results — `vendor`, `technical_description`,
`conversational_overview`, `symbol_purposes` (one purpose per used
symbol), optional `action_pointer_file`/`action_pointer_note`), then maps
each batch's response back onto that batch's candidates. A result naming
a vendor outside the batch (a hallucinated/misspelled entry) is dropped
rather than failing the whole batch.

**`apply_results(conn, project_root, results) -> None`** writes each
result three ways: `graph.record_enrichment`/`graph.record_symbol_enrichment`
(Phase 10's writers, unchanged); `claude_md.update_description_section`
(new — see **Per-vendor CLAUDE.md structure** below) to rewrite just that
vendor's `CLAUDE.md` Description section and hash line in place, without
re-running `sync_vendor`'s whole pipeline; and
`skill.write_vendor_skill`/`write_cursor_mdc` against a **minimal
`VendorDigest`** populated only with the fields those two functions
actually read (`config`, `installed_version`, `conversational_overview`,
`technical_description`, `action_pointer_file`, `action_pointer_note`) —
confirmed by reading both functions' bodies that neither touches
`api_surface`/`file_tree`/`dep_tree`/`side_effects`, so leaving those at
their dataclass defaults is safe, not a partial digest.
`VendorConfig.depth` has no real meaning on this path (`decisions/0031`)
and isn't derivable from an `EnrichmentResult` (which only carries the
vendor's name); it's set to `Depth.FULL` as the closest existing label,
a value `skill.py` never actually reads.

**Cost model reworked for the batched shape**: `estimate_cost(batch_count)`
/`check_budget(candidates, budget)` scale with `len(plan_batches(candidates))`,
not 1:1 with vendor count — several vendors' material and output now share
one call, so the old per-vendor formula
(`grounded_description.estimate_cost`) would overstate cost for a batch of
more than one. Same abort-before-any-spend contract otherwise.

### Project-source usage detection (`codecompass.usage`)

**New in Phase 11 — the first module to inspect the *consuming project's*
source at all.** `symbols.py`'s extractors run in the opposite direction
(pulling symbols *out of* a vendor's own source); `usage.py` walks the
project's own source tree looking for imports *of* a tracked vendor.
`DetectedImport(vendor, symbol_name, line)` — `symbol_name=None` is the
vendor-level fallback for an import that doesn't resolve to one specific
bound name (`import rich`, `use serde::*;`, `require("pkg")`). One no-AI,
no-subprocess detector per ecosystem, each `Path -> list[DetectedImport]`:
`detect_python_imports` (`ast`-based; `import` is vendor-level, `from X
import Y` captures one entry per bound name off `X`'s first dotted
component; relative imports are skipped outright — they can never name an
external vendor); `detect_npm_imports` (regex over named/default/
namespace `import` and `require()` forms, same coarse-regex posture
already accepted for `extract_npm_symbols`); `detect_rust_imports` (regex
over `use vendor::Symbol;` / `use vendor::*;` / `use vendor;`).
`detect_imports_for_file(path, ecosystem)` dispatches by ecosystem and
file suffix, mirroring `symbols.extract_symbols_for_file`'s dispatch
shape; every detector never raises, returning `[]` for an unparseable
file, the same convention `symbols.py` established.

`resolve_project_usage(project_root, configs) -> list[tuple[str,
DetectedImport]]` walks `project_root` via
`filetree.iter_source_files(project_root, prune_dirs=
_PROJECT_PRUNE_DIR_NAMES)` — deliberately **not**
`filetree._PRUNE_DIR_NAMES`: a project's own `tests`/`fixtures` importing
a vendor is real usage signal, so `usage.py`'s prune set drops only
build/dependency noise (`node_modules`, `dist`, `build`, `.git`,
`__pycache__`, `.venv`, `venv`), never test directories. This is exactly
why `filetree._iter_files` became the public, parameterizable
`iter_source_files(root, *, prune_dirs=..., prune_globs=...)` in this same
phase — same deterministic sorted-and-pruned walk shape, reused with a
different prune set, rather than a second copy of the walk logic. Results
are filtered to only vendor names present in `configs` — an import of an
untracked package isn't this project's concern. `usage.py` has no
`graph.py` dependency (it only detects and filters against `configs`),
keeping it independently unit-testable; symbol-name-to-`symbol_id`
resolution happens one layer up, in `sync.py`.

### Populating the graph (`sync.rebuild_project_graph`)

`rebuild_project_graph(configs: list[VendorConfig], project_root: Path) ->
None`, added to `sync.py` in Phase 11: for **every** tracked vendor in
`configs` (not just ones a particular `sync_all` call touched — the graph
must reflect the full current state regardless of which vendors were just
resynced), reads `installed_version()`/`repository_url()` (both
already-existing, no-network adapter methods) and collects that vendor's
own symbol list via the same `iter_source_files` + `extract_symbols_for_file`
pairing `build_symbol_index` already uses internally — reused, not
duplicated, just captured as structured `Symbol` objects instead of a
rendered string. Then `usage.resolve_project_usage` detects the project's
imports, and each `DetectedImport.symbol_name` is resolved against the
matching vendor's just-collected symbol names: a match becomes a
symbol-level `UsesEdgeRow`, no match (or `symbol_name=None` to begin with)
stays a vendor-level fallback edge, matching `uses_edges.symbol_id`'s
nullability (`decisions/0031`). Phase 12 adds real `doc_artifacts`/
`documents_edges`/`skill_mentions_edges`/`routes_via_edges`/
`depends_on_edges` data (below); `graph.open_graph` +
`graph.rebuild_deterministic` then writes everything in one transaction.

**Deliberately decoupled from `sync_all`'s per-vendor loop, not threaded
through it as a flag** — `sync_all` is sometimes called with a *subset* of
configs (bare bootstrap's `new_configs` only) even on a whole-project run,
but the graph needs *every* tracked vendor's data regardless. `cli.py`
calls `rebuild_project_graph` explicitly at its two whole-project call
sites, each with the *full* tracked config list: `_bootstrap`, after
`write_tool_skill`, with `all_configs`; the `sync` command, only when
`vendor is None` (the whole-project branch — matching `decisions/0025`'s
existing rebuild-trigger posture, carried into `decisions/0032`), with
`configs` right after `sync_all` succeeds. `sync <vendor>` (single-vendor)
and `check --fix`'s per-vendor loop (already calling `sync_vendor`
directly, never `sync_all`) leave the graph untouched.

### Doc & wide skill mapping (`codecompass.doc_mapping`, `codecompass.skill_scan`)

**New in Phase 12 — still not CLI-visible (Phase 15's job); this phase
only populates the five tables `rebuild_project_graph` previously passed
empty lists for.** Both modules are pure transformations over
already-generated artifacts — no new AI call, no new extraction — called
from `rebuild_project_graph` alongside the Phase 11 pieces above.

`doc_mapping.py`:
- `collect_vendor_doc_artifacts(configs, project_root) ->
  list[DocArtifactRow]` — one `kind='claude_md'` row per tracked vendor's
  `vendor/<name>/CLAUDE.md` (skipped if that vendor hasn't been synced
  yet — no row points at a nonexistent file) and one `kind='overview'` row
  for `vendor/<name>/OVERVIEW.md` if it exists (only currently-`promote`d
  vendors have one). Both `origin='codecompass_vendor'`.
- `build_documents_edges(doc_artifact_rows, symbol_rows, project_root) ->
  list[DocumentsEdgeRow]` — for each `claude_md`/`overview` doc artifact,
  reads its file text off disk and word-boundary-matches it against
  *that same vendor's* known symbol names. A coverage heuristic ("this
  symbol's name appears in the vendor's own digest text"), not a quality
  judgment. Takes `project_root` (beyond the phase plan's originally
  sketched two-arg signature) since resolving `DocArtifactRow.path` — a
  natural key, deliberately relative — to an actual file to read requires
  it; `build_skill_mentions_edges` below needs it for the same reason.
- `build_routes_via_edges(configs, doc_artifact_rows) ->
  list[RoutesViaEdgeRow]` — routes each vendor to its own per-vendor
  Skill doc artifact (`kind='skill'`, `origin='codecompass_vendor'`) if
  one exists, else to the shared tool-level Skill
  (`kind='skill'`, `origin='codecompass_tool'`) if present — operationalizes
  `decisions/0013` point 6 as real queryable data.
- `build_depends_on_edges(configs, project_root) -> list[DependsOnEdgeRow]`
  — reads each tracked vendor's persisted `vendor/<name>/deptree.json` and
  flattens it with a module-local `_flatten_deptree` (mirroring
  `staleness._flatten`, deliberately duplicated rather than imported —
  same small-local-helper style as elsewhere in this codebase), emitting a
  `Vendor → Vendor` edge wherever a flattened name matches another
  *tracked* vendor's name. An untracked transitive dependency isn't a
  graph node, so no edge for it. A missing/corrupt `deptree.json` is
  skipped, best-effort, the same tolerant posture
  `staleness._detect_transitive_drift` already takes toward this file.

`skill_scan.py` — the scope-expanded piece: indexes **every** Skill under
`.claude/skills/` and every Cursor rule under `.cursor/rules/`, not just
codecompass's own generated ones:
- `scan_skills(project_root, configs) -> list[DocArtifactRow]` — globs
  `.claude/skills/**/SKILL.md` (`kind='skill'`) and `.cursor/rules/*.mdc`
  (`kind='cursor_mdc'`), extracting `name`/`description` via a **minimal
  custom frontmatter extractor** (`_extract_scalar` — split on `---`
  delimiters, handle a single-line `key: value` and a folded `key: >-`
  block with indented continuation lines, the two shapes this project's
  own generated Skills use; never raises, returns `None` on anything else
  — deliberately not a real YAML parser, since this project has no YAML
  dependency and doesn't need to fully solve arbitrary third-party
  frontmatter). Classifies `origin` by directory name (`SKILL.md`) or
  filename stem (`.mdc`) against codecompass's own naming convention,
  reusing `skill.py`'s own `_TOOL_SKILL_DIR_NAME`/`_vendor_skill_name`
  rather than duplicating those literals: an exact match on the tool
  Skill's directory name is `codecompass_tool`; a match against a tracked
  vendor's `_vendor_skill_name` is `codecompass_vendor` (`vendor_name`
  set); anything else is `third_party`.
- `build_skill_mentions_edges(skill_doc_artifacts, configs,
  source_file_rows, project_root) -> list[SkillMentionEdgeRow]` — for
  each skill's body text (everything after the frontmatter, not just the
  parsed `name`/`description` fields), word-boundary-matches against every
  tracked vendor name (→ vendor-mention edge) and every tracked project
  source file's basename (→ source-file-mention edge, one per source file
  sharing that basename). A presence heuristic, same posture as
  `documents_edges` — explicitly not a claim the skill is *about* that
  vendor/file, just that it mentions it mechanically. Also takes
  `project_root` for the same disk-read reason as `build_documents_edges`.

**Word-boundary (`\b<name>\b`), not substring, matching for both mention-
edge types** — case-sensitive, matching this project's own generated
Skill/doc content being lowercase-consistent. A naive substring match
risks false positives on any vendor/file name that collides with a common
English word (`rich`, `six`) or is short enough to appear inside an
unrelated word (a vendor named `six` must not match `sixty-four`) —
covered by a regression test in both `tests/test_doc_mapping.py` and
`tests/test_skill_scan.py`.

## `undo` — best-effort generated-artifact cleanup (`codecompass.cli`)

**New in Phase 18 (`decisions/0036`).** `codecompass undo [--yes]
[--dry-run]` is the first command whose job is to *remove* generated
output rather than produce it: every tracked vendor's `vendor/<name>/`
directory, `vendor.toml`, `context-graph.db`, every codecompass-generated
Skill/`.mdc`/slash-command artifact, and the root `CLAUDE.md`
routing-table marker block. Implemented entirely in `cli.py` — no new
module — as a handful of small enumeration helpers plus the command
function itself.

**Two mutually exclusive enumeration strategies**, chosen by whether
`context-graph.db` exists (`_codecompass_generated_paths`):

- **Graph-backed** (`_graph_backed_undo_paths`): `SELECT path, kind FROM
  doc_artifacts WHERE origin IN ('codecompass_tool', 'codecompass_vendor')`
  — an exact match against `doc_artifacts.origin`'s CHECK constraint
  (which only ever allows those two values plus `third_party`), not a
  `LIKE` pattern, so `origin='third_party'` is excluded by construction,
  never by a filter applied after the fact. A `kind='skill'` row's `path`
  points at its `SKILL.md` file, but the generated artifact `skill.py`
  actually writes is the *whole Skill directory* (`SKILL.md` plus a
  `references/` subdir for a per-vendor Skill) — this function resolves
  such a row to its parent directory, not the file alone, or
  `references/*.md` would be orphaned behind an otherwise-deleted Skill.
  Every tracked vendor's `vendor/<name>/` directory is added directly from
  the `vendors` table, independent of the `doc_artifacts` rows.
- **Fallback** (`_fallback_undo_paths`), used only when `context-graph.db`
  doesn't exist yet (a project that's only run `init`/a single `sync
  <vendor>`): pattern-matches the exact generated-name conventions
  `skill.py`'s `_TOOL_SKILL_DIR_NAME`/`commands.py`'s discovery-command
  path use — `.claude/skills/codecompass/`,
  `.claude/skills/codecompass-*/` (glob), `.cursor/rules/codecompass-*.mdc`
  (glob), `.claude/commands/discovery.md` (if present) — plus every vendor
  listed directly in `vendor.toml` (`load_vendor_config`, no graph
  needed). Strictly less precise than the graph-backed path (it can't
  distinguish a hand-renamed third-party Skill that happens to collide
  with the `codecompass-*` naming pattern from one this tool actually
  generated) but functional without ever requiring a prior whole-project
  sync — the scenario `undo` most needs to work in
  (`decisions/0036`).

Either path, `vendor.toml` and `context-graph.db` themselves are always
added if present.

**Deduplication** (`_dedupe_contained`): a `claude_md`/`overview`
`doc_artifacts` row's path (e.g. `vendor/demo/CLAUDE.md`) is always a
descendant of that same vendor's `vendor/demo/` directory, already in the
target set — printing and deleting both would be redundant, so any path
that's a strict descendant of another already-collected path is dropped,
shallowest paths processed first.

**The root `CLAUDE.md` marker block is stripped, never deleted** —
`_strip_routing_table_block` reuses `index.py`'s own `_MARKER_BLOCK_RE`
(imported directly, not duplicated — unlike `skill.py`'s/`sync.py`'s
locally-duplicated `_open_graph_readonly`, drift between two independent
copies of *this* regex would be a correctness bug, not just redundant
code) and runs `update_root_claude_md`'s insertion logic in reverse:
`_MARKER_BLOCK_RE.sub("", text)` removes the block, then a `\n{3,}` ->
`\n\n` collapse cleans up the blank-line gap left behind. Hand-written
content before/after the block survives untouched either way.

**Flow:** enumerate, print the full list, stop if `--dry-run`, otherwise
prompt (`typer.confirm`, skippable with `--yes`), then delete
(`shutil.rmtree` for directories, `Path.unlink` for files) and rewrite
`CLAUDE.md` with the block stripped.

**Never touches git** (no `git rm`/`git add`/`git status`) and **never
commits** — plain filesystem operations only, the same posture every
other `codecompass` command already has toward git. Best-effort, not
transactional: a failure partway through a multi-path deletion is not
rolled back (`decisions/0036` has the full rationale).

## Cost model

Structural generation (trees, API-surface extraction, source cloning,
Phase A's entire zero-question bootstrap) makes no AI calls and is
effectively free. As of Phase 15, the primary cost center is **Phase B**
(`decisions/0031`): usage-driven batched enrichment, using Haiku, wired
into `cli.py` behind bare `codecompass` and whole-project `sync` (see
"Retrofitting to existing projects" above for the full disclose/confirm/
budget flow). Unlike the retired `promote`, Phase B is **cached** — a
vendor already enriched at its current used-symbol set is skipped
(`enrichment.select_candidates`'s two-tier hash check), so cost scales
with how often the project's actual dependency *usage* changes, not with
how often `sync` is run. `enrichment.estimate_cost(batch_count)` /
`enrichment.check_budget(candidates, budget)` scale with
`len(plan_batches(candidates))` (batches, not vendors) — several
vendors' material and output share one call, reworked from the old
per-vendor formula `grounded_description.estimate_cost` used. `--yes`
skips the confirmation prompt; `--budget <amount>` refuses to make any
Phase B API call at all (not partially) once the projected cost for a
single run exceeds the cap — same abort-before-any-spend contract the
retired `promote`/`sync --budget` guaranteed.

A `depth = FULL` vendor's per-vendor grounded-description regeneration
(`codecompass.grounded_description`, pre-Phase-15) still exists and still
runs on every `sync`, uncached, for as long as `Depth` isn't retired
(Phase 16) — a legacy cost path, not the primary one going forward.

## Known footguns

- **`VendorDigest.is_stale` was removed in Phase 6**, not left as a stub —
  `check` never builds a `VendorDigest` (same reasoning `index.py`
  established for staying cheap), so the Phase-1 stub had no code path
  that could ever populate it. If older notes or memory reference
  `digest.is_stale`, that API no longer exists; use
  `codecompass.staleness.check_vendor`/`check_all` instead.
- **`staleness.py`'s version parser is a small custom regex, not a real
  PEP 440 or full semver parser** — it only extracts a leading
  `major.minor.patch` integer triple, tolerating a `v` prefix and ignoring
  any trailing suffix. No epoch support, no pre-release-ordering
  correctness (e.g. it can't tell `1.0.0-alpha` from `1.0.0-beta` apart
  semantically — both parse to the same triple as `1.0.0`). Either side
  failing to parse a triple at all yields `Severity.UNKNOWN`, treated as a
  `--strict` failure. A deliberate dependency-avoidance choice
  (`decisions/0009`, `decisions/0011`), not an oversight — flag if it
  misclassifies a real-world version string.
- **Bare `codecompass check` (no flags) always exits 0**, even with a major
  severity present — it's a report-only table for local use. Only
  `--strict` turns severity/error findings into a non-zero exit. Don't
  assume plain `check` in a script or hook enforces anything; use
  `check --strict` for that.
- `_load_config` and `claude_md.render_vendor_claude_md` are both
  implemented (Phases 1 and 4) — the CLI skeleton's old `_write_claude_md`
  `NotImplementedError` stub was removed in Phase 4, not left behind.
- The `.d.ts` file cap (5 files) in the npm adapter, and the matching
  `.pyi` cap in the Python adapter, are arbitrary initial values for
  cost control, not validated final numbers — flag if they clip useful
  API surface on real-world packages.
- `vendor/<name>/src/` snapshots are gitignored and regenerated by `sync`,
  not committed (resolved in Phase 1, see
  [`decisions/0010`](../decisions/0010-vendor-src-gitignored-and-regenerated.md)).
  A fresh clone has no working standalone-mode chat for `FULL` vendors
  until `sync` has been run at least once — easy to forget when
  onboarding a new checkout.
- **`_run_json`'s subprocess seam resolves `cmd[0]` via `shutil.which`
  before invoking it** — not just for a nicer "not found" error. On
  Windows, `npm` resolves to a `.cmd` shim, which `subprocess.run` can't
  launch by bare name without a shell; resolving to the full path first
  keeps `shell=False` (and its narrower injection surface) working
  cross-platform. Found and fixed via Phase 2's live npm smoke test —
  fixture-only testing would not have caught it (see
  [`decisions/0014`](../decisions/0014-adapter-tests-use-fixture-mocking-not-live-subprocesses.md)).
- **The Python adapter invokes `pipdeptree` as `sys.executable -m
  pipdeptree`**, not a bare `pipdeptree` on `PATH` — a standalone venv's
  `Scripts`/`bin` directory isn't reliably on `PATH` unless the venv is
  activated. Also found via a Phase 2 live smoke test, for the same
  reason as the npm fix above.
- **npm `dev_only` is not transitive**: a node is marked `dev_only` only
  if its own name is a *direct* `devDependency` of the root consuming
  project — a transitive dependency of a dev-only package isn't
  propagated. Documented limitation, not solved in Phase 2.
- **Python `dev_only` is always `False`** — `pipdeptree`'s output carries
  no dev/runtime distinction once a package is installed, a real
  structural difference from npm's `package.json`, not an oversight.
- **Cargo's API-surface extraction is a coarse, line-based scan**, not a
  real Rust parser — it misses multi-line function/struct signatures
  (generic bounds or `where` clauses spanning lines). `rustdoc
  --output-format json` remains the documented eventual fix.
- **The Cargo adapter is unverified against real `cargo` output** — no
  Rust toolchain is available in this dev environment as of Phase 2. Its
  parsing logic is tested only against hand-written fixture JSON modeled
  on cargo's public schema docs. See
  [`decisions/0014`](../decisions/0014-adapter-tests-use-fixture-mocking-not-live-subprocesses.md)
  for the follow-up required once a toolchain becomes available.
- **`deptree.py`'s `_DEPTREE_MAX_DEPTH` (20)**, **`filetree.py`'s
  `_PRUNE_DIR_NAMES`/`_PRUNE_FILE_GLOBS`, and `_SYMBOL_INDEX_CAP` (200)**
  are initial, arbitrary, tunable values, not validated final numbers —
  same treatment as Phase 2's `.d.ts`/`.pyi` 5-file cap. Flag if they
  clip useful tree/index content on real-world packages.
- **`CargoAdapter.readme_and_api_surface()`'s output format changed in
  Phase 3** — items now render as `name: purpose` instead of the raw `pub
  fn ...` signature line, because the underlying extraction moved to
  `symbols.extract_rust_symbols`'s name-based `Symbol` objects. See
  [`decisions/0015`](../decisions/0015-symbol-extraction-reuses-adapter-parsing-per-ecosystem.md).
- **`extract_npm_symbols`'s JSDoc/export regex scan is coarse and new** —
  unlike the Cargo/Python extractors (which generalize Phase 2-validated
  logic), it has no adapter-level precedent and is only tested against
  hand-written `.d.ts` fixtures, not a wide range of real-world authoring
  styles.
- **`filetree.py`'s directory walk (`_iter_files`) uses `Path.rglob("*")`
  then filters pruned directories post-hoc** — it doesn't stop descending
  into a pruned directory like `node_modules/` before walking it, just
  excludes its contents from the result. Fine at this project's scale
  (a single vendor package's source tree), but not optimized for very
  large pruned subtrees.
- **Grounded description is fully regenerated (re-cloned and
  re-purchased) on every `sync` run** for a `depth = full` vendor — no
  caching or diffing against a previous result, consistent with every
  other `sync` output but the one step where that consistency has a real
  dollar cost.
- **`grounded_description.py`'s `_RAW_TEXT_CHAR_CAP` (50,000),
  `_DOCS_FILE_CAP` (5), and `_ESTIMATED_COST_PER_CALL_USD` (a rough
  placeholder, not live-queried Anthropic pricing)** are initial,
  arbitrary, tunable values — same treatment as every other cap in this
  project. The cost estimate is not a guarantee of actual billed cost;
  `--budget` decisions should be made with that in mind.
- **No test ever makes a real Anthropic API call** (see
  [`decisions/0016`](../decisions/0016-gap-analysis-tests-never-call-the-live-anthropic-api.md),
  which continues to apply unchanged to `grounded_description.py`) —
  its prompt/schema correctness against the real model is not validated
  by the automated suite at all; a human must run `codecompass promote`
  against a real vendor with a real `ANTHROPIC_API_KEY` at least once to
  trust this phase's output quality. (Source resolution and cloning were
  validated against a real repository — pytest's own, via its PyPI
  `Project-URL` metadata — during Phase 7's implementation; only the AI
  call itself remains unvalidated against the live API.)
- **`git` is now a required external tool for `promote`** (and for
  `sync`/`check --fix` on any already-`FULL` vendor) — `codecompass
  source_resolution._git_clone` shells out to it the same way adapters
  shell out to `npm`/`cargo`/`pipdeptree`, with the same `shutil.which`-
  first resolution pattern. Not declared as a Python dependency (it isn't
  one), but its absence surfaces as a clear `SourceResolutionError`
  rather than a cryptic subprocess failure.
- **`index` reads persisted per-vendor `CLAUDE.md` files rather than
  re-running `sync`** — a deliberate deviation from
  `planning/phase-4-sync-index-init.md`'s literal `render_routing_table(digests:
  list[VendorDigest])` signature (that plan explicitly left this detail
  open). Re-running `sync` inside `index` would make `index` silently pay
  gap-analysis AI cost once Phase 5 lands, defeating the reason `index`
  exists as a separate, cheap command. Consequence: a vendor that's never
  been synced shows `_not synced_` in the routing table instead of an
  error, and the Deps column links to `DEPTREE.md` instead of showing a
  live dependency count (no adapter/tree data is available to `index`).
- **`VendorDigest.side_effects`** (added in Phase 4) is populated by
  `sync_vendor` from the dependency tree's root `DepNode.side_effects` —
  not from every node in the tree, only the vendor's own top-level entry.
  A transitive dependency's side effects (e.g. a sub-dependency's own
  postinstall script) aren't surfaced in Known Gotchas.
- **`sync_vendor` fully overwrites `vendor/<name>/` on every call** — no
  diffing, no incremental update, and (for `depth = full`) the entire
  `vendor/<name>/src/` snapshot is deleted and recopied each time, not
  merged. Simple and correct, but means a large `FULL` vendor's `sync` is
  not cheap to run repeatedly in a tight loop.
