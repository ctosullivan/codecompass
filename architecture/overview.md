# Architecture overview

This document describes depcompass's **current** design — component
responsibilities and how they fit together. Unlike `decisions/`, which
records the historical *why* behind a choice and is append-only, this file
is a living document updated in place as the system evolves. When in doubt
about *why* something is designed the way it is, check `decisions/`; when
you want to know *what exists now*, check here.

As of Phase 0, none of this is implemented yet — this document describes
the target design that later phases build toward.

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
  optional gap analysis. Its `is_stale` property is a documented stub
  (`NotImplementedError`) until `staleness.check()` populates it — calling
  it before a staleness check has run is a bug, not a valid empty state.
  See **Known footguns** below.

## Adapter interface

`EcosystemAdapter` (ABC) defines four methods every ecosystem must
implement: `installed_version`, `source_location`, `readme_and_api_surface`,
`dependency_tree`. Adding a new ecosystem means writing one adapter class,
not touching core logic.

MVP ships three adapters on day one — npm, Python, Cargo — rather than
starting npm-only. See
[`decisions/0008`](../decisions/0008-mvp-ships-three-adapters-day-one.md).

- **npm adapter** — version/tree via `package.json` + `npm ls --json`; API
  surface via README + `.d.ts` files, capped at 5 files read per package
  for cost/size control. That cap is a known limitation, not a validated
  final number — see **Known footguns**.
- **Python adapter** — version via `pip show` / installed package metadata;
  tree via `pipdeptree --json`; API surface has no single canonical source
  like `.d.ts` — uses `.pyi` stub files where present, else falls back to
  top-level docstrings/`__all__` exports. Structurally different from the
  npm adapter; its own judgment calls, not a direct port of npm's approach.
- **Cargo adapter** — version/tree via `cargo tree` / `cargo metadata
  --json`; API surface via public (`pub`) function/struct signatures — no
  standardized doc-comment extraction assumed. `rustdoc --output-format
  json` is worth investigating as an alternative during implementation,
  not assumed up front.

See [`decisions/0002`](../decisions/0002-adapter-approach-differs-per-ecosystem.md).

## Tree generation — deterministic, always free

`FILETREE.md` and `DEPTREE.md` (plus `filetree.json`/`deptree.json`
sidecars) involve **no AI calls** and run on every `sync` regardless of
`depth`. Rules:

- Prune `dist/`, `build/`, `.git/`, `__pycache__/`, `node_modules/`,
  `.venv/`, test/fixture directories, minified bundles, and source maps —
  they add tokens without adding navigation value.
- **Deduplicate diamond dependencies** in `DEPTREE.md` — render each unique
  `name@version` once, back-reference repeats (`(see lodash@4.17.21
  above)`) rather than re-expanding. The single biggest token-reduction
  lever for real npm trees.
- Dev-only dependencies collapse to a count, not an enumerated list.
- Depth-cap large trees with an explicit collapse notice — never a silent
  truncation; an agent must be able to tell an incomplete tree from a
  complete one.
- `FILETREE.md` omits version numbers (that's `DEPTREE.md`'s job) but
  includes a one-line purpose annotation per file where inferable.
- **Cross-link FILETREE entries to gap-analysis action pointers directly**
  — e.g. `src/commonmark-rules.js  ← ACTION TARGET: override
  fencedCodeBlock here` — collapsing a two-hop lookup (read gap analysis,
  then separately find the file) into one line.
- Also produce a **flat, greppable symbol index** (keyword → file path)
  alongside the nested tree — closer to a ctags model than a directory
  listing. Nested trees are for first-read orientation; flat indexes are
  for "jump straight to the thing" on a targeted question. Both are
  needed; they solve different lookup patterns.

## Gap analysis — the only AI-cost step

Only runs when `depth = FULL`. Uses `claude-haiku-4-5` — a Q&A/
summarization task, not agentic coding, so the cheapest capable model tier
is the right default. See
[`decisions/0003`](../decisions/0003-haiku-for-gap-analysis.md).

**Requires `context_path`** (pointing at the consuming project's own
README/spec) — without project context, the model has no basis to judge
what counts as a "gap"; a gap analysis generated without this input is
generic and low value, not just slightly worse.

## Per-vendor CLAUDE.md structure

Required sections, in order:

1. **Metadata** — version, ecosystem, depth, and a **"last verified
   against installed version"** line. This exact line format is parsed by
   `staleness.py` via regex — it is load-bearing, not cosmetic.
2. **Grounding preamble** — explicit instruction that the pinned version is
   authoritative over training knowledge for this library. This is the
   actual mechanism that changes agent behavior — without an explicit
   "prefer this over what you already know" instruction, an agent has no
   signal to override its training data.
3. **Public API surface**.
4. **Gap analysis + action pointer** (FULL only).
5. **Known gotchas**.
6. **Quick links**.

## Two consumption modes

Both must work:

1. **Standalone** — `cd vendor/<name> && claude`. Requires a *copied*
   pinned source snapshot at `vendor/<name>/src/` for `FULL` vendors, NOT a
   reference into `node_modules` — package managers prune/dedupe/reinstall
   `node_modules` contents, so it isn't a stable pin target. See
   [`decisions/0004`](../decisions/0004-vendor-src-snapshot-not-node-modules-reference.md).
   Includes a backlink to the project root `CLAUDE.md` so the agent can
   escalate from "how does this library work" to "how is it used in our
   project."
2. **Routed from project root** — a routing table is injected into the
   consuming project's own root `CLAUDE.md`, between
   `<!-- depcompass:start -->` / `<!-- depcompass:end -->` markers.
   Idempotent regeneration via `index()`: handles both the first-run case
   (markers don't exist yet, section is appended) and the regenerate case
   (`re.sub` with `DOTALL` replaces just the marked block), without
   clobbering hand-written content around it. Table columns: Vendor, Path,
   Version (✅/⚠), Depth, Deps, Consult when — paired with an explicit
   routing instruction sentence, since the table alone is inert data.

## Staleness checking

Compares the `**Installed version**:` line in a vendor's `CLAUDE.md`
against the ecosystem adapter's live lockfile read. **Severity-aware, not
binary**: patch delta is silent/ignored, minor delta warns without
failing, major delta hard-fails (`check` exits non-zero) because a major
bump may mean the digest describes removed or changed APIs. See
[`decisions/0005`](../decisions/0005-severity-aware-staleness.md).

Two run modes:
- `--strict` — pure gate, human runs `sync` manually. Appropriate for CI,
  so an automated process doesn't unpredictably spend AI-pass tokens on
  every PR.
- `--fix` — regenerates stale digests in place, exits 0 on success.
  Appropriate for a scheduled maintenance job. Should batch all stale
  vendors into one PR rather than one PR per bump, to avoid redundant
  token spend and PR noise.

Where practical, distinguish whether the *vendor itself* bumped version vs.
only one of its *transitive dependencies* bumped (DEPTREE drift) — the
latter is lower risk and shouldn't trigger the same urgency.

**Hook placement**: pre-commit only fires when a lockfile actually changed
(`package-lock.json`, `pyproject.lock`, `Cargo.lock`) — not on every
commit. Pre-commit is a courtesy/fast-fail; **CI's `depcompass check` is
the actual enforcement point** that blocks merge.

## Multi-tool export (Cursor)

Cursor does not read `CLAUDE.md` natively. Its modern context system is
`.cursor/rules/*.mdc` files with YAML frontmatter (`description`, `globs`,
`alwaysApply`) controlling activation — the legacy single `.cursorrules`
file is deprecated and unreliable in Cursor's agent mode specifically, so
it isn't targeted. `CLAUDE.md` remains the source of truth; `.mdc` is a
**generated export**, not a separately maintained file — same content,
different serialization — with `globs` scoped to wherever the vendor is
actually imported in the consuming codebase (inferred, not hand-written)
and `alwaysApply: false` (vendor digests should only load into context
when relevant files are open, not on every request — token cost control,
same reasoning as the depth system).

## Chat REPL

`depcompass chat [<name>]` — a lightweight terminal REPL, distinct from
just using Claude Code in the vendor folder. It loads only the vendor's
digest files as system context and calls the API directly (Haiku) with no
tool-use/file-exploration loop — faster and cheaper per query, but
strictly narrower: it only knows what's in the digest, not the full pinned
source. This tradeoff is stated in the REPL's startup banner so a user
doesn't over-trust an answer beyond what the digest actually covers.

- **Explicit vendor** (`chat turndown`) — loads that vendor's digest only,
  single system prompt, no routing needed.
- **No vendor specified** (project-root mode) — the REPL handles both
  vendor-specific *and* whole-project questions. Two-tier routing per
  question, across three possible context targets (a specific vendor,
  several vendors, or the project itself):
  - **Tier 1** (free, instant) — match vendor names/configured aliases
    against the question text. If none match, check for project-level
    signal instead (question references architecture, a roadmap phase, a
    past decision, or general "how does this project..." phrasing) and
    load **project context** (root `CLAUDE.md` + `architecture/` +
    relevant `decisions/` entries + `planning/CONTEXT.md`'s current-state
    section) rather than any vendor digest.
  - **Tier 2** (fallback, only if Tier 1 is ambiguous) — pass both the
    vendor routing table and a summary of available project-context
    sources, and let the model itself judge relevance (no extra API call),
    escalating to a one-shot Haiku classification call only if that's
    insufficient.
  - **Always print a visible context indicator line before answering** —
    e.g. `→ loaded turndown digest (exact match)` or `→ using project
    context (architecture/overview.md, decisions/0003-*.md)`. The user
    must always be able to tell what grounded a given answer. If a
    question pulls in both a vendor digest and project context, the
    indicator line lists both explicitly rather than picking one to
    display.
  Loaded context persists in the system prompt for the rest of the session
  (cheap to keep, cache-friendly); a soft cap (~3-4 loaded context
  sources, LRU eviction) prevents a long mixed session from letting the
  system prompt grow unbounded.
- Rich handles presentation: `Panel` for the startup grounding disclaimer,
  `Markdown` for rendering answers, `Progress`/spinner for multi-vendor
  `sync` runs, `Table` for `check` output with stale rows highlighted.
  Since `check` also runs in CI, ANSI codes are explicitly guarded against
  polluting CI logs (`Console(force_terminal=...)` / `sys.stdout.isatty()`
  checks) rather than relying solely on Rich's auto-detection.

## Retrofitting to existing projects

`depcompass init --scan <manifest files>` bulk-discovers dependencies and
writes a draft `vendor.toml` with everything defaulted to `depth =
SURFACE` — free, since surface generation has no AI cost, so it's safe to
run immediately on a large existing dependency list without a cost
conversation first. Promotion to `FULL` is selective and reactive
(promote a vendor the first time someone actually needs its deep digest
mid-task) rather than batch-promoting a whole existing dependency graph
up front. If several vendors get promoted to `FULL` at once, `--budget`
caps concurrent AI calls and prints an estimated cost before running.

## Cost model

Structural generation (trees, API-surface extraction) makes no AI calls
and is effectively free. The only cost center is gap-analysis generation
at `depth = FULL`, using Haiku. At realistic project scale (dozens of
dependencies, a handful at `FULL`, weekly scheduled refresh), total
ongoing cost is estimated well under $2/month. This is a design constraint
worth preserving — if a future change would make gap-analysis run more
broadly or more often by default, that's a deliberate tradeoff to flag,
not something to drift into silently.

## Known footguns

- `VendorDigest.is_stale` is a stub that raises until populated by a
  staleness check — don't treat a missing implementation there as a bug to
  "fix" by returning a default; it's intentionally unpopulated until
  `staleness.check()` runs.
- `_load_config` (parse `vendor.toml`) and `_write_claude_md` (render the
  CLAUDE.md template), once they exist in the CLI skeleton, are expected
  to start as deliberate `NotImplementedError` stubs — templating/parsing
  glue, not architectural decisions, filled in during Phase 1/4.
- The `.d.ts` file cap (5 files) in the npm adapter is an arbitrary initial
  value for cost control, not a validated final number — flag if it clips
  useful API surface on real-world packages during Phase 2 testing.
- Whether pinned `vendor/<name>/src/` snapshots get committed to git or
  gitignored-and-regenerated is unresolved as of Phase 0 — to be decided
  in the Phase 1 plan file. This affects both repo size and whether a
  clone has a working standalone-mode chat without first running `sync`.
