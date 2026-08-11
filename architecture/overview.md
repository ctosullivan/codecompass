# Architecture overview

This document describes depcompass's **current** design — component
responsibilities and how they fit together. Unlike `decisions/`, which
records the historical *why* behind a choice and is append-only, this file
is a living document updated in place as the system evolves. When in doubt
about *why* something is designed the way it is, check `decisions/`; when
you want to know *what exists now*, check here.

As of Phase 6, the core data model (`depcompass.core`), `vendor.toml`
parsing (`depcompass.config`), all three ecosystem adapters
(`depcompass.adapters`), per-ecosystem symbol/purpose extraction
(`depcompass.symbols`), deterministic tree generation
(`depcompass.deptree`, `depcompass.filetree`), per-vendor `CLAUDE.md`
templating (`depcompass.claude_md`), per-vendor sync orchestration
(`depcompass.sync`), root routing-table injection (`depcompass.index`),
manifest-based `vendor.toml` bootstrap (`depcompass.discovery`), AI-gated
gap analysis (`depcompass.gap_analysis`), and severity-aware staleness
checking (`depcompass.staleness`) are implemented — `init`, `sync`
(including `--budget`), `index`, and `check` (including `--strict`/
`--fix`) are real CLI commands, not stubs. MVP phases 0-6 are complete.
Everything else described below — the chat REPL, Skills/Cursor export —
is still the target design that later phases build toward; see
`planning/CONTEXT.md` for current status.

## Core data model

- **`VendorConfig(name, ecosystem, depth, context_path)`** — one entry per
  dependency, sourced from `vendor.toml`. See
  [`docs/config-schema.md`](../docs/config-schema.md) for the file format.
- **`Depth`** enum: `SURFACE` (metadata + API surface only, no AI call, no
  pinned source copy) vs `FULL` (pinned source snapshot + AI-generated gap
  analysis). Depth is set **per vendor**, not globally — most dependencies
  are used as-is and only need surface info; only the handful being
  extended, subclassed, or written custom rules against justify `FULL`'s
  cost. See [`decisions/0001`](../decisions/0001-depth-is-per-vendor-not-global.md).
- **`DepNode(name, version, children, dev_only, side_effects)`** — one node
  in a dependency tree, ecosystem-agnostic. `side_effects` captures things
  like postinstall scripts or native binary downloads that are invisible in
  a raw manifest but explain real-world install size/behavior.
- **`VendorDigest`** — the aggregate return type each vendor's generation
  produces: config, installed version, generated trees, API surface,
  optional gap analysis. Carries no staleness information — `check`
  (Phase 6) reads persisted per-vendor `CLAUDE.md` files directly rather
  than building a `VendorDigest`, the same pattern `index.py` established
  in Phase 4, and returns its own `depcompass.staleness.VendorStaleness`
  type instead. An earlier `is_stale` stub on this class, speculatively
  added in Phase 1, was removed in Phase 6 once it became clear no code
  path would ever populate it. See **Known footguns** below.

## Adapter interface

`EcosystemAdapter` (ABC, `src/depcompass/adapters/base.py`) is constructed
with `(config: VendorConfig, project_root: Path)` and defines four methods
every ecosystem implements: `installed_version() -> str`,
`source_location() -> Path`, `readme_and_api_surface() -> str`,
`dependency_tree() -> DepNode`. Adding a new ecosystem means writing one
adapter class against this interface, not touching core logic.

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
`depcompass.filetree` renders from a vendor's source directory
(`source_location()`, or the copied `vendor/<name>/src/` snapshot for
`depth = full` — both point at the same content, since the snapshot is a
copy of `source_location()`). Both are wired into `sync.py` (Phase 4),
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
- **Cross-linking FILETREE entries to gap-analysis action pointers**
  (e.g. `src/commonmark-rules.js  ← ACTION TARGET: override
  fencedCodeBlock here`) — implemented in Phase 5 via the
  `action_pointer` parameter above. `sync_vendor` threads a successful
  gap analysis's `(action_pointer_file, action_pointer_note)` into both
  `render_filetree_markdown` and `render_filetree_json`; a `depth =
  surface` vendor, or one with no gap analysis this run, passes `None`
  and the parameter has no effect.

## Gap analysis — the only AI-cost step (`depcompass.gap_analysis`)

Only runs for `depth = FULL` vendors with `context_path` set. Uses the
dated snapshot `claude-haiku-4-5-20251001` — a Q&A/summarization task,
not agentic coding, so the cheapest capable model tier is the right
default (`decisions/0003`); pinned to a dated snapshot rather than the
rolling `claude-haiku-4-5` alias `decisions/0003` names literally, so
gap-analysis output doesn't silently change character if Anthropic
updates what the alias resolves to — a plan-level refinement of that
ADR's model-*tier* choice, not a reversal of it.

**Requires `context_path`** (pointing at the consuming project's own
README/spec) — without project context, the model has no basis to judge
what counts as a "gap"; a gap analysis generated without this input is
generic and low value, not just slightly worse. Content is truncated to
an arbitrary, tunable character cap before entering the prompt (see Known
footguns).

**Output is dual-audience** (see
[`decisions/0012`](../decisions/0012-conversational-first-repl-design.md)),
produced by **one forced-tool-use API call**: `generate_gap_analysis(config,
api_surface, project_root) -> GapAnalysis` returns `technical` (agent-
facing, goes in `CLAUDE.md`, unchanged in spirit from the original
design), `conversational_overview` (human-facing, written the way you'd
explain the dependency to a colleague — what it does, why the project
uses it, its risk posture — rather than the way you'd document it), and
an optional `action_pointer_file`/`action_pointer_note` pair. Same call,
same cost — a prompt/schema change, not a new cost center. The
conversational overview is persisted to a new `vendor/<name>/OVERVIEW.md`
(Phase 5) — not duplicated into `CLAUDE.md`, which stays agent-facing
technical content only — for Phase 8's Chat REPL project-wide dependency
rollup to consume later (see **Chat REPL** below); `decisions/0012`
requires it already exist by then, since the rollup makes no new
per-dependency AI calls.

**Real cost implication**: like every other `sync` output, gap analysis
is fully regenerated on every `sync` run, not diffed or cached — a
`depth = full` vendor's gap analysis is re-purchased every time `sync`
runs, not just the first time it's promoted.

**Failure handling**: a `GapAnalysisError` (API failure, unreadable
`context_path`, malformed response) is caught inside `sync_vendor` for
that one vendor — its deterministic output still gets written (with an
explicit "unavailable" note in `CLAUDE.md`, see below), remaining
vendors still run, and `sync` exits non-zero at the end if anything
failed. This is local to one vendor; it never aborts the batch.

**`sync --budget <amount>`**: `check_budget` runs once per `sync_all`
call, *before* any vendor's `sync_vendor` runs. If the estimated cost of
this run's pending gap-analysis calls (vendors with `depth = full` and
`context_path`, at a fixed rough per-call placeholder estimate — not
live-queried pricing) exceeds `budget`, the whole run aborts with a clear
message and **nothing is written this invocation**, not even other
vendors' free deterministic output.

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
4. **Gap analysis + action pointer** — `digest.gap_analysis` plus an
   `**Action pointer:**` line when `digest.action_pointer_file` is set.
   If `digest.gap_analysis_error` is set instead, renders an explicit
   `_Gap analysis unavailable: `<error>`_` note rather than silently
   omitting the section — consistent with this project's never-silent-
   failure convention (explicit collapse/cap notices elsewhere). Omitted
   entirely (no heading at all) when neither is set — `depth = surface`,
   or `full` without `context_path`, where gap analysis never runs.
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
   `sync.py`'s snapshot copy is pruned *more loosely* than `FILETREE.md`'s
   walk — it strips `node_modules`/`dist`/`build`/`.git`-style noise only
   and keeps `test`/`tests`/`__tests__`/`fixtures` directories, since a
   `FULL` vendor is one being extended or subclassed and its own test
   suite is often exactly what someone wants to reference here. Includes a
   backlink to the project root `CLAUDE.md` so the agent can escalate from
   "how does this library work" to "how is it used in our project."
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

## Multi-tool export (Skills, Cursor)

**Agent Skills are the primary multi-tool export target** (see
[`decisions/0013`](../decisions/0013-agent-skills-as-shared-context-selection-source.md)),
motivated by a reliability gap in the root `CLAUDE.md` routing table: its
"consult this vendor's digest first" instruction is a soft instruction
competing for attention with everything else in context, so an agent
confident in its training knowledge may never read the digest at all —
precisely the failure mode depcompass exists to prevent. A Skill's
description is mechanically part of how Claude decides what's relevant to
load, a stronger (though not absolute) guarantee than the routing table's
instruction-following alone.

One Skill per `depth = FULL` vendor, generated at
`.claude/skills/depcompass-<vendor>/SKILL.md`:
- The trigger description is built from data already generated — the
  routing table's "Consult when" column plus a condensed gap-analysis
  summary — not new content generation. **Description length is a real,
  ongoing tuning knob, not a one-time writing task**: every skill's
  name+description loads into every session unconditionally, so a long
  description that maximizes one vendor's trigger accuracy has a real
  per-vendor cost that compounds as `FULL`-depth vendor count grows.
  Specificity (concrete API methods, file/function names, exact trigger
  situations) — not length — is what drives triggering accuracy.
- `FILETREE.md`/`DEPTREE.md` bundle as `references/` files inside the
  skill folder rather than inlining — progressive disclosure means they
  only cost tokens when Claude actually needs to navigate source.
- A wrapper script shelling out to `depcompass check <vendor>` at trigger
  time (a live staleness read instead of a cached line) is deferred to a
  later phase, not required for the initial export.
- `depth = SURFACE` vendors don't get a Skill yet — no gap-analysis
  content exists to build a meaningful trigger description from; worth
  revisiting with a templated (non-AI-generated) description later.

**Cursor `.mdc` export is retained, not replaced.** Cursor does not read
`CLAUDE.md` natively. Its modern context system is `.cursor/rules/*.mdc`
files with YAML frontmatter (`description`, `globs`, `alwaysApply`)
controlling activation — the legacy single `.cursorrules` file is
deprecated and unreliable in Cursor's agent mode specifically, so it isn't
targeted. `.mdc` is a **generated export**, not a separately maintained
file — same content, different serialization — with `globs` scoped to
wherever the vendor is actually imported in the consuming codebase
(inferred, not hand-written) and `alwaysApply: false` (token cost control,
same reasoning as the depth system). Cursor's glob-scoped file-pattern
activation is a different — sometimes more precise — trigger model than
Skills' description-matching, and not every Cursor setup has Skills
support, so this export stays alongside Skills rather than being dropped.

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
full` vendors whose gap analysis succeeded — `OVERVIEW.md`, Phase 5's
persisted conversational overview) are backing store for two consumers —
AI agents reading them directly (see **Two
consumption modes** above) and the REPL synthesizing them into
conversation — and content generation is written with "does this read
well spoken aloud in a casual chat" as a first-class constraint, not an
afterthought handled by reformatting at query time.

`depcompass chat [<name>]` — a lightweight terminal REPL, distinct from
just using Claude Code in the vendor folder. It loads only the vendor's
digest files as system context and calls the API directly (Haiku) with no
tool-use/file-exploration loop — faster and cheaper per query, but
strictly narrower: it only knows what's in the digest, not the full pinned
source. This tradeoff is stated in the REPL's startup banner so a user
doesn't over-trust an answer beyond what the digest actually covers.

- **Explicit vendor** (`chat turndown`) — loads that vendor's digest only,
  single system prompt, no routing needed.
- **No vendor specified** (project-root mode) — loads a **project-wide
  dependency rollup unconditionally at session start**, before any
  routing happens. The rollup is synthesized once per `sync` (not per
  query) from the already-generated per-vendor conversational overviews
  (see **Gap analysis** above): dependency count by depth, a staleness
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
    Skill description text** that Phase 9 produces for Claude Code's
    native Skills triggering (see
    [`decisions/0013`](../decisions/0013-agent-skills-as-shared-context-selection-source.md)),
    not an independently-authored keyword/alias list. One source of
    truth for "what fires on what," tuned once via Phase 9's
    trigger-accuracy evaluation, benefiting both native Skills triggering
    and this routing tier. Whichever of Phase 8/Phase 9 is built first
    exposes this data in a form the other consumes, rather than
    duplicating it — a sequencing note for both phases' plan files. If
    nothing matches, check for project-level signal instead (question
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
  reusing Phase 9's output rather than inventing a separate
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

`depcompass init --scan <manifest file> [--scan <manifest file> ...]`
(`depcompass.discovery`) bulk-discovers dependencies and writes a draft
`vendor.toml` with everything defaulted to `depth = SURFACE` — free,
since surface generation has no AI cost, so it's safe to run immediately
on a large existing dependency list without a cost conversation first.
`--scan` is a repeated flag, not one flag followed by several
space-separated files (not how a named Click/Typer option works — the
CLI reference's earlier draft syntax was corrected to match in Phase 4).
Errors rather than overwriting if `vendor.toml` already exists. Python
discovery reads only `[project.dependencies]`, not
`[project.optional-dependencies]`. Promotion to `FULL` is selective and
reactive (promote a vendor the first time someone actually needs its deep
digest mid-task) rather than batch-promoting a whole existing dependency
graph up front. If several vendors get promoted to `FULL` at once,
`--budget` will cap concurrent AI calls and print an estimated cost
before running — not yet implemented, since it's meaningless before
Phase 5 adds any AI call to `sync` at all.

## Cost model

Structural generation (trees, API-surface extraction) makes no AI calls
and is effectively free. The only cost center is gap-analysis generation
at `depth = FULL`, using Haiku, and it is **not cached** — every `sync`
run regenerates it fresh for every `depth = full` + `context_path`
vendor, so cost scales with how often `sync` is run, not just with how
many vendors are `FULL`. At realistic project scale (dozens of
dependencies, a handful at `FULL`, weekly scheduled refresh), total
ongoing cost is estimated well under $2/month. This is a design constraint
worth preserving — if a future change would make gap-analysis run more
broadly or more often by default, that's a deliberate tradeoff to flag,
not something to drift into silently. `sync --budget <amount>` guards
against one specific runaway scenario (several vendors promoted to
`FULL` at once) by refusing to run at all — not partially — once the
projected cost for a single run exceeds the cap.

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
- **Gap analysis is fully regenerated, and re-purchased, on every `sync`
  run** for a `depth = full` + `context_path` vendor — no caching or
  diffing against a previous result, consistent with every other `sync`
  output but the one step where that consistency has a real dollar cost.
- **`gap_analysis.py`'s `_CONTEXT_PATH_CHAR_CAP` (8000) and
  `_ESTIMATED_COST_PER_CALL_USD` (a rough placeholder, not live-queried
  Anthropic pricing)** are initial, arbitrary, tunable values — same
  treatment as every other cap in this project. The cost estimate is not
  a guarantee of actual billed cost; `--budget` decisions should be made
  with that in mind.
- **No test ever makes a real Anthropic API call** (see
  [`decisions/0016`](../decisions/0016-gap-analysis-tests-never-call-the-live-anthropic-api.md))
  — `gap_analysis.py`'s prompt/schema correctness against the real model
  is not validated by the automated suite at all; a human must run `sync`
  against a real `depth = full` vendor with a real `ANTHROPIC_API_KEY` at
  least once to trust this phase's output quality.
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
