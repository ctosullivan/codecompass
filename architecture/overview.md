# Architecture overview

This document describes depcompass's **current** design — component
responsibilities and how they fit together. Unlike `decisions/`, which
records the historical *why* behind a choice and is append-only, this file
is a living document updated in place as the system evolves. When in doubt
about *why* something is designed the way it is, check `decisions/`; when
you want to know *what exists now*, check here.

As of Phase 7, the core data model (`depcompass.core`), `vendor.toml`
parsing (`depcompass.config`), all three ecosystem adapters
(`depcompass.adapters`), per-ecosystem symbol/purpose extraction
(`depcompass.symbols`), deterministic tree generation
(`depcompass.deptree`, `depcompass.filetree`), per-vendor `CLAUDE.md`
templating (`depcompass.claude_md`), per-vendor sync orchestration
(`depcompass.sync`), root routing-table injection (`depcompass.index`),
manifest-based `vendor.toml` bootstrap and zero-question auto-discovery
(`depcompass.discovery`), upstream repository resolution
(`depcompass.source_resolution`), AI-gated grounded-description
generation (`depcompass.grounded_description`, replacing Phase 5's
`context_path`-gated gap analysis — `decisions/0019`), Skill/Cursor
export (`depcompass.skill`), severity-aware staleness checking
(`depcompass.staleness`), and the single-vendor chat REPL
(`depcompass.chat`, grounded on persisted digest files, never live
regeneration — `decisions/0023`) are all implemented — bare `depcompass`,
`init`, `sync` (including `--budget`), `index`, `check` (including
`--strict`/`--fix`), `promote`, and `chat <vendor>` are real CLI
commands, not stubs. The MVP spans phases 0-8 (`decisions/0022`); all
eight are now `done` (a `v0.1` tag/release has not yet been cut).
Bare `depcompass chat` project-root routing and the whole-project
dependency rollup, described in the Chat REPL section below, remain
post-MVP (Phase 9) target design; see `planning/CONTEXT.md` for current
status.

## Core data model

- **`VendorConfig(name, ecosystem, depth)`** — one entry per dependency,
  sourced from `vendor.toml`. `context_path` (a Phase 5 field) was
  removed in Phase 7 — `depth = full` needs no companion field anymore
  (`decisions/0019`). See
  [`docs/config-schema.md`](../docs/config-schema.md) for the file format.
- **`Depth`** enum: `SURFACE` (metadata + API surface only, no AI call, no
  pinned source copy) vs `FULL` (pinned source snapshot + AI-generated
  grounded description). Depth is set **per vendor**, not globally — most
  dependencies are used as-is and only need surface info; only the
  handful being extended, subclassed, or written custom rules against
  justify `FULL`'s cost, and the only path to `FULL` is
  `depcompass promote <vendor>` (`decisions/0018`). See
  [`decisions/0001`](../decisions/0001-depth-is-per-vendor-not-global.md).
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
  `depcompass.staleness.VendorStaleness` type instead. An earlier
  `is_stale` stub on this class, speculatively added in Phase 1, was
  removed in Phase 6 once it became clear no code path would ever
  populate it. See **Known footguns** below.

## Adapter interface

`EcosystemAdapter` (ABC, `src/depcompass/adapters/base.py`) is constructed
with `(config: VendorConfig, project_root: Path)` and defines five methods
every ecosystem implements: `installed_version() -> str`,
`source_location() -> Path`, `readme_and_api_surface() -> str`,
`repository_url() -> RepositoryLocation | None` (Phase 7 —
`decisions/0021`), `dependency_tree() -> DepNode`. Adding a new ecosystem
means writing one adapter class against this interface, not touching
core logic.

`repository_url()` resolves the vendor's upstream repository from
locally-available package metadata only — never a network call, unlike
the clone `depcompass.source_resolution` performs from its result. Per
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

## Symbol/purpose extraction (`depcompass.symbols`)

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
sidecars) involve **no AI calls** and run on every `sync` regardless of
`depth`. `depcompass.deptree` renders from a `DepNode` tree;
`depcompass.filetree` renders from a vendor's **locally-installed**
source directory (`source_location()`) — unchanged in Phase 7, always
the local install regardless of depth. This is now a distinct source
from `vendor/<name>/src/`'s snapshot content for `depth = full` vendors:
since Phase 7, that snapshot is cloned from the vendor's **upstream
repository** (`depcompass.source_resolution`, `decisions/0021`) rather
than copied from `source_location()`, since a locally-installed package
is often a trimmed build artifact missing README/docs content the
repository has. Both tree renderers are wired into `sync.py` (Phase 4),
which writes their output to `FILETREE.md`/`DEPTREE.md`/`filetree.json`/
`deptree.json` under `vendor/<name>/`.

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
  gap-analysis-to-grounded-description swap). `sync_vendor` threads a
  successful description's `(action_pointer_file, action_pointer_note)`
  into both `render_filetree_markdown` and `render_filetree_json`; a
  `depth = surface` vendor, or one with no description this run, passes
  `None` and the parameter has no effect.

## Grounded description — the only AI-cost step (`depcompass.grounded_description`)

Runs for every `depth = FULL` vendor, unconditionally — no longer gated
on a project-supplied field (Phase 5's `context_path`, removed in Phase 7
— `decisions/0019`). Uses the dated snapshot `claude-haiku-4-5-20251001`
— a summarization task, not agentic coding, so the cheapest capable model
tier is the right default (`decisions/0003`, unaffected by the Phase 7
mechanism swap); pinned to a dated snapshot rather than the rolling
`claude-haiku-4-5` alias `decisions/0003` names literally, so output
doesn't silently change character if Anthropic updates what the alias
resolves to.

**Grounded entirely in material retrieved from the vendor's own upstream
repository** — not a project-supplied README/spec, and not the model's
own training knowledge of the dependency (`decisions/0019`'s reversal of
Phase 5's design). `depcompass.source_resolution.resolve_and_clone`
clones the repository (resolved via each adapter's `repository_url()` —
see **Adapter interface** above) into `vendor/<name>/src/`;
`_gather_material` then assembles up to `_RAW_TEXT_CHAR_CAP` (50,000)
raw characters from: the repository's README, up to 5 Markdown files
from a `docs/`/`doc/` folder if present, and one ecosystem-typical entry
point file (npm: `package.json`'s `main`/`module`, or
`index.{js,ts}`/`src/index.{js,ts}`; Python: `<name>/__init__.py` or
`src/<name>/__init__.py`; Cargo: `src/lib.rs` or `src/main.rs`). The cap
keeps this comfortably within a single Haiku call — no multi-call
chunking is needed. Each retrieved section is tagged with its source
path in the prompt, and the system prompt instructs the model to cite
specific files/functions rather than rely on prior knowledge.

**Output is dual-audience** (see
[`decisions/0012`](../decisions/0012-conversational-first-repl-design.md)),
produced by **one forced-tool-use API call**:
`generate_grounded_description(config, repo_root) -> GroundedDescription`
returns `technical` (agent-facing, goes in `CLAUDE.md`'s Description
section), `conversational_overview` (human-facing, written the way you'd
explain the dependency to a colleague — what it does, why a project
might use it — rather than the way you'd document it), and an optional
`action_pointer_file`/`action_pointer_note` pair (repurposed from Phase
5's "most relevant file for the gap" to "most useful file to read next").
Same call shape, same cost — a prompt/schema and input-source change, not
a new cost center. The conversational overview is persisted to
`vendor/<name>/OVERVIEW.md` (unchanged since Phase 5) — not duplicated
into `CLAUDE.md`, which stays agent-facing technical content only. Phase
8's `chat <vendor>` reads it directly as part of its grounding
(`decisions/0023`); Phase 9's project-wide dependency rollup (see **Chat
REPL** below) will consume it too, with no new per-dependency AI calls,
once it's built.

**Real cost implication**: like every other `sync` output, grounded
description is fully regenerated (and re-cloned) on every `sync` run,
not diffed or cached — a `depth = full` vendor's description is
re-purchased every time `sync` runs, not just the first time it's
promoted.

**Failure handling, two distinct failure points**: if source resolution/
cloning itself fails (`SourceResolutionError` — no repository field, `git`
missing, network failure, or a declared monorepo subdirectory that
doesn't exist), `vendor/<name>/src/` falls back to the old local-install-
sourced copy (`decisions/0004`) so standalone browsing still has
*something*, and `description_error` is set. If cloning succeeds but the
AI call fails (`GroundedDescriptionError`), the real clone is kept as-is
rather than discarded in favor of the fallback. Either way, the failure
is caught inside `sync_vendor` for that one vendor — its deterministic
output still gets written (with an explicit "unavailable" note in
`CLAUDE.md`, see below), remaining vendors still run, and `sync` exits
non-zero at the end if anything failed. This is local to one vendor; it
never aborts the batch.

**`sync --budget <amount>`**: `check_budget` runs once per `sync_all`
call, *before* any vendor's `sync_vendor` runs. If the estimated cost of
this run's pending generation calls (every vendor with `depth = full` —
no longer additionally gated on `context_path`, since that field no
longer exists — at a fixed rough per-call placeholder estimate, not
live-queried pricing) exceeds `budget`, the whole run aborts with a clear
message and **nothing is written this invocation**, not even other
vendors' free deterministic output. `depcompass promote` performs the
same disclosure-then-confirm gate for the single vendor it's escalating,
before setting `depth = full` at all (`decisions/0018`).

## Per-vendor CLAUDE.md structure (`depcompass.claude_md`)

`render_vendor_claude_md(digest: VendorDigest) -> str`. Sections, in
order:

1. **Metadata** — ecosystem, depth, and a `**Installed version:**` line.
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
   If `digest.description_error` is set instead, renders an explicit
   `_Description unavailable: `<error>`_` note rather than silently
   omitting the section — consistent with this project's never-silent-
   failure convention (explicit collapse/cap notices elsewhere). Omitted
   entirely (no heading at all) when neither is set — `depth = surface`,
   where grounded-description generation never runs.
5. **Known gotchas** — deterministically derived from `digest.side_effects`
   (the dependency tree's root `DepNode.side_effects`, e.g. npm's
   postinstall-script detection) rather than left empty or AI-generated.
   A vendor with none detected renders a fixed "No known side effects
   detected." line.
6. **Quick links** — relative links to `./FILETREE.md`, `./DEPTREE.md`,
   and a backlink to the project root `CLAUDE.md`.

## Two consumption modes

Both must work:

1. **Standalone** — `cd vendor/<name> && claude`. Requires a *copied*
   pinned source snapshot at `vendor/<name>/src/` for `FULL` vendors, NOT a
   reference into `node_modules` — package managers prune/dedupe/reinstall
   `node_modules` contents, so it isn't a stable pin target. See
   [`decisions/0004`](../decisions/0004-vendor-src-snapshot-not-node-modules-reference.md).
   Since Phase 7, the snapshot is a shallow `git clone` of the vendor's
   own upstream repository (`depcompass.source_resolution`,
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
   `<!-- depcompass:start -->` / `<!-- depcompass:end -->` markers.
   Idempotent regeneration via `depcompass.index.update_root_claude_md`:
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
   its own separate table (`depcompass check`) rather than being wired
   into `index`'s routing table, a deliberate scope boundary rather than
   an oversight (see **Known footguns**); the Deps column links to
   `DEPTREE.md` rather than showing a live dependency count, since `index`
   deliberately has no adapter/tree data to draw one from.

## Staleness checking (`depcompass.staleness`)

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
commit. Pre-commit is a courtesy/fast-fail; **CI's `depcompass check
--strict` is the actual enforcement point** that blocks merge.

## Multi-tool export (Skills, Cursor) — `depcompass.skill`

**Agent Skills are the primary multi-tool export target** (see
[`decisions/0013`](../decisions/0013-agent-skills-as-shared-context-selection-source.md)),
motivated by a reliability gap in the root `CLAUDE.md` routing table: its
"consult this vendor's digest first" instruction is a soft instruction
competing for attention with everything else in context, so an agent
confident in its training knowledge may never read the digest at all —
precisely the failure mode depcompass exists to prevent. A Skill's
description is mechanically part of how Claude decides what's relevant to
load, a stronger (though not absolute) guarantee than the routing table's
instruction-following alone. Implemented in Phase 7 as part of
`depcompass promote` (`decisions/0018`), not a separate later phase — the
Skill for a vendor is generated at the moment it's promoted, the same
call that generates its grounded description.

One Skill per `depth = FULL` vendor, generated at
`.claude/skills/depcompass-<vendor>/SKILL.md`:
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
- A wrapper script shelling out to `depcompass check <vendor>` at trigger
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
  `.claude/skills/depcompass/SKILL.md`, generated unconditionally by
  `index` (and by bare `depcompass`) regardless of vendor count or depth
  — listing depcompass's own commands and the current vendor table, so
  an agent has a mechanical signal that depcompass exists even before
  anything has been promoted.

**Cursor `.mdc` export is retained, not replaced.** Cursor does not read
`CLAUDE.md` natively. Its modern context system is `.cursor/rules/*.mdc`
files with YAML frontmatter (`description`, `alwaysApply`) controlling
activation — the legacy single `.cursorrules` file is deprecated and
unreliable in Cursor's agent mode specifically, so it isn't targeted.
`.mdc` is a **generated export**, not a separately maintained file —
same technical-description content as the Skill, different serialization
— written to `.cursor/rules/depcompass-<vendor>.mdc` by `promote`
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

`depcompass chat <name>` — a lightweight terminal REPL, distinct from
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
  `.claude/skills/depcompass-<vendor>/` folder as the handoff artifact for
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

**Bare `depcompass` (no subcommand) is the zero-question path**
(`decisions/0017`, Phase 7): auto-discovers manifests at the project root
(`package.json`, `pyproject.toml`, `requirements.txt`, `Cargo.toml`),
writes/refreshes `vendor.toml` with everything defaulted to `depth =
SURFACE` — free, since surface generation has no AI cost — and
regenerates trees, the routing table, and the tool-level Skill. No
prompts, no AI calls, regardless of project size. Re-running it on an
already-bootstrapped project is an **idempotent refresh**: newly
discovered dependencies are appended at `SURFACE`; already-tracked
vendors, including any at `depth = FULL`, are left completely untouched
(their generated output isn't regenerated), so this command never pays
AI cost no matter how many times it's run.

`depcompass init --scan <manifest file> [--scan <manifest file> ...]`
(`depcompass.discovery`) remains as the explicit, scripted/CI-friendly
synonym — useful for naming specific manifests rather than relying on
root-level auto-discovery. `--scan` is a repeated flag, not one flag
followed by several space-separated files (not how a named Click/Typer
option works — the CLI reference's earlier draft syntax was corrected to
match in Phase 4). Unlike bare `depcompass`, it keeps its original
stricter contract: errors rather than overwriting if `vendor.toml`
already exists. Python discovery reads `[project.dependencies]` from
`pyproject.toml` and every non-comment, non-option line of
`requirements.txt` (Phase 7 addition) — not
`[project.optional-dependencies]`.

**Promotion to `FULL` is selective, reactive, and the only paid
action**: `depcompass promote <vendor>` (`decisions/0018`, Phase 7) is
the single command that costs money or asks anything — triggered when
someone actually needs a vendor's deep digest, not batch-decided for a
whole existing dependency graph up front. It prints an estimated cost
disclosure and asks for confirmation (or `--yes`) before doing anything
AI-assisted. `sync --budget <amount>` separately guards the case where
several vendors are already `FULL` and a routine `sync` would regenerate
all of them at once — refusing to run at all (not partially) if the
projected cost exceeds the cap.

## Cost model

Structural generation (trees, API-surface extraction, bare `depcompass`'s
entire zero-question bootstrap) makes no AI calls and is effectively
free. The only cost center is grounded-description generation at `depth
= FULL`, using Haiku, first entered through `depcompass promote`
(`decisions/0018`) and then paid again on every subsequent `sync`/`check
--fix` for that vendor — it is **not cached**, so cost scales with how
often `sync` is run, not just with how many vendors are `FULL`. At
realistic project scale (dozens of dependencies, a handful at `FULL`,
weekly scheduled refresh), total ongoing cost is estimated well under
$2/month. This is a design constraint worth preserving — if a future
change would make grounded-description generation run more broadly or
more often by default, that's a deliberate tradeoff to flag, not
something to drift into silently. `promote` discloses cost and confirms
before the first AI call for a vendor; `sync --budget <amount>` guards
the ongoing case (several vendors already `FULL`, a routine `sync` about
to regenerate all of them) by refusing to run at all — not partially —
once the projected cost for a single run exceeds the cap.

## Known footguns

- **`VendorDigest.is_stale` was removed in Phase 6**, not left as a stub —
  `check` never builds a `VendorDigest` (same reasoning `index.py`
  established for staying cheap), so the Phase-1 stub had no code path
  that could ever populate it. If older notes or memory reference
  `digest.is_stale`, that API no longer exists; use
  `depcompass.staleness.check_vendor`/`check_all` instead.
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
- **Bare `depcompass check` (no flags) always exits 0**, even with a major
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
  by the automated suite at all; a human must run `depcompass promote`
  against a real vendor with a real `ANTHROPIC_API_KEY` at least once to
  trust this phase's output quality. (Source resolution and cloning were
  validated against a real repository — pytest's own, via its PyPI
  `Project-URL` metadata — during Phase 7's implementation; only the AI
  call itself remains unvalidated against the live API.)
- **`git` is now a required external tool for `promote`** (and for
  `sync`/`check --fix` on any already-`FULL` vendor) — `depcompass
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
