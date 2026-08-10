# Architecture overview

This document describes depcompass's **current** design — component
responsibilities and how they fit together. Unlike `decisions/`, which
records the historical *why* behind a choice and is append-only, this file
is a living document updated in place as the system evolves. When in doubt
about *why* something is designed the way it is, check `decisions/`; when
you want to know *what exists now*, check here.

As of Phase 2, the core data model (`depcompass.core`), `vendor.toml`
parsing (`depcompass.config`), a CLI skeleton (`depcompass.cli`) whose
commands are stubs, and all three ecosystem adapters
(`depcompass.adapters`) are implemented. Everything else described below
— tree generation, gap analysis, staleness checking, the chat REPL,
Skills/Cursor export — is still the target design that later phases build
toward; see `planning/CONTEXT.md` for current status.

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

**Output is dual-audience** (see
[`decisions/0012`](../decisions/0012-conversational-first-repl-design.md)):
the same AI call produces two sections — the technical block described
above (agent-facing, unchanged), plus a short conversational overview
written the way you'd explain the dependency to a colleague (what it
does, why the project uses it, its risk posture) rather than the way
you'd document it. Same call, same cost — a prompt/schema change, not a
new cost center. The conversational overview is what feeds the Chat
REPL's project-wide dependency rollup (see **Chat REPL** below); it isn't
duplicated into the per-vendor `CLAUDE.md` file, which stays agent-facing
technical content only.

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
4. **Gap analysis + action pointer** (FULL only; technical output only —
   the parallel conversational overview isn't duplicated here, see **Gap
   analysis** above).
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
The digests (`CLAUDE.md`, `FILETREE.md`, `DEPTREE.md`) are backing store
for two consumers — AI agents reading them directly (see **Two
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
- `_load_config` is implemented (Phase 1); `_write_claude_md` in the CLI
  skeleton is still a deliberate `NotImplementedError` stub —
  templating glue, not an architectural decision, filled in during
  Phase 4.
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
