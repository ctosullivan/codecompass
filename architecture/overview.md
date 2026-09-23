# Architecture overview

This document describes codecompass's **current** design — component
responsibilities and how they fit together. Unlike `decisions/`, which
records the historical *why* behind a choice and is append-only, this file
is a living document updated in place as the system evolves. When in doubt
about *why* something is designed the way it is, check `decisions/`; when
you want to know *what exists now*, check here.

Every CLI command described in this document is real and implemented,
not a stub: bare `codecompass` (zero-question bootstrap), `init`
(including `--scan`), `sync` (whole-project or single-vendor, including
`--budget`), `index`, `check` (including `--strict`/`--fix`), `query`
(`vendors`/`vendor`/`symbol`/`skills`/`relations`), `enrich apply`,
`chat <vendor>`, and `undo` (`--yes`/`--dry-run`). `promote` and the
per-vendor `depth` toggle are both retired (`decisions/0033`,
`decisions/0031`) — every tracked vendor gets the same deterministic
treatment, and AI enrichment eligibility comes from the context graph's
usage evidence, not a config field or a separate command. Bare
`codecompass chat` project-root routing and the whole-project dependency
rollup, described in the Chat REPL section below, are deferred design,
not yet implemented — see
`planning/phase-20-chat-project-root-routing-design.md`.

For the module inventory and how responsibility is layered across
`src/codecompass/`, see [`module-map.md`](module-map.md); for current
milestone/phase status, see `planning/ROADMAP.md` and
`planning/CONTEXT.md` rather than this document, which does not track
that state.

**Where to look**: this document covers what has no dedicated home below
— consumption surfaces (Skills, Cursor, `/discovery`, the chat REPL),
staleness checking, `undo`, the cost model, and known footguns — and
points into five companion documents for everything else:
[`module-map.md`](module-map.md) (what each module is responsible for),
[`core-data-model.md`](core-data-model.md) (the core dataclasses),
[`adapter-interface.md`](adapter-interface.md) (the `EcosystemAdapter`
contract and its two implementation strategies),
[`context-graph-schema.md`](context-graph-schema.md) (every
`context-graph.db` table), and
[`sync-and-enrichment-pipeline.md`](sync-and-enrichment-pipeline.md)
(what actually happens on `sync`/bare `codecompass`, traced through the
real call graph). [`historical-notes.md`](historical-notes.md) records
two past behavior changes with no ADR of their own that are still
relevant to understanding today's code.

## Core data model

`codecompass.core` holds the small set of ecosystem-agnostic dataclasses
everything else is built from — `VendorConfig`, `RepositoryLocation`,
`DepNode`, `VendorDigest` — plus `codecompass.symbols`' `Symbol`. See
[`core-data-model.md`](core-data-model.md) for their fields and the
design rationale behind each; a summary here would only restate that
document. `VendorConfig` has exactly two fields (`name`, `ecosystem`) —
no per-vendor `depth`/`context_path` field exists; a legacy `vendor.toml`
entry still carrying either key keeps parsing without error. See
[`../docs/config-schema.md`](../docs/config-schema.md) for the file
format.

## Adapter interface

This section covers the **ecosystem adapter** package
(`src/codecompass/adapters/`) — a different sense of "adapter" from the
**host-output adapters** described in **Module tiers: CORE, AGENT,
HOST-OUTPUT ADAPTERS** below (Claude Skills, `/discovery`, the root
`CLAUDE.md` routing table), which render already-computed content into
tool-specific formats rather than abstracting a package manager. See
[`adapter-interface.md`](adapter-interface.md) for the full
`EcosystemAdapter` contract (five abstract methods plus the concrete,
overridable `symbols()`), the closed adapter-dispatch table, and both
coexisting implementation strategies — in-process (npm, Python, Cargo,
sharing a `_run_json` subprocess seam) and external-process (Haskell,
the reference implementation, delegating real ecosystem-specific logic
to a separate `codecompass-adaptor-haskell` process rather than
in-process Python). `Symbol.export_kind`/`note` (`decisions/0059`) are
deliberately narrow **export/exposure-status** fields, not a
symbol-type/kind field — see [`core-data-model.md`](core-data-model.md).

## External adapters (`codecompass.adapters.external_process`)

A second `EcosystemAdapter` implementation strategy, alongside the
in-process one above: an adapter runs as an independent OS process,
speaking a small, versioned, language-neutral JSON protocol over
stdin/stdout, rather than being importable Python code inside
`src/codecompass/`. Exists specifically for ecosystems where in-process
Python code is the wrong distribution model — a hypothetical future
proprietary COBOL/mainframe adapter suite is the motivating case; it
could never ship as importable GPL-licensed Python code inside this
repository even if CodeCompass wanted to bundle one. See
[`adapter-interface.md`](adapter-interface.md#strategy-2-external-process-haskell-the-reference-implementation)
for how `HaskellAdapter` delegates to it (per-instance analysis caching,
monorepo package-root resolution, locating the built executable).

**Three real repositories, one local workspace**, checked out as git
submodules:

```
codecompass/                                  (this repository)
├── protocol/
│   └── codecompass-adaptor-protocol/         (git submodule — MIT)
└── adapters/
    └── haskell/                              (git submodule — GPL-3.0-or-later)
```

- **`codecompass-adaptor-protocol`** — the language-neutral contract
  only: `SCHEMA.md`, JSON Schema documents, worked examples, and
  conformance test vectors. No CodeCompass code, no Haskell code, MIT
  licensed so any future adapter, in any language or license, can
  depend on the contract alone.
- **`codecompass-adaptor-haskell`** — the real reference adapter, a
  Stack project implementing the protocol against `hledger`-style
  `stack`-managed Haskell projects. GPL-3.0-or-later, matching
  CodeCompass's own license.
- **`src/codecompass/adapters/external_process.py`** — a fully generic
  JSON-Lines subprocess client (`initialize` → `analyze_project` →
  `shutdown`). Zero ecosystem-specific knowledge; reusable by any future
  external-process adapter without modification.

**Protocol shape**: JSON Lines framing, one outstanding request at a
time, an `id`-correlated request/response pair, a closed method set
(`initialize`, `analyze_project`, `shutdown`), a closed capability list
(`dependencies`, `symbols`, `observations`, `diagnostics`), a closed
error-code set (`not_found`, `parse_error`, `unsupported_capability`,
`internal_error`). `analyze_project`'s `observations` section mirrors
this codebase's own Observation record field vocabulary, expressed as
JSON on the wire, so provenance survives the process boundary
losslessly. Full spec: `protocol/codecompass-adaptor-protocol/SCHEMA.md`
once checked out, or `decisions/0057`.

**Real command shape, verified live against the real `hledger-lib`
package inside the `hledger` monorepo**: `stack dot --external
<package-name>` and `stack ls dependencies --external <package-name>`
(both take an explicit `TARGET` positional argument) scope their output
to exactly that package's own dependency closure — bare `stack dot
--external`/`stack ls dependencies --external` (no target) instead
walks *every* project package declared in the enclosing `stack.yaml`
(all four of `hledger`/`hledger-lib`/`hledger-ui`/`hledger-web` in the
real monorepo), which is the wrong scope for a single-package analysis.
`codecompass-adaptor-haskell` always passes the resolved package name as
`TARGET` for both commands.

**Where the boundary falls**: simple manifest-key reads
(`package.yaml`'s `name`/`version`/`github` fields) stay on the
CodeCompass/Python side — that's the same class of generic,
ecosystem-adjacent code `discovery.py` already does for every other
ecosystem's manifest, not "Haskell-specific implementation code."
`stack`'s own dependency-tree resolution and real `.hs`-source
API-surface extraction are genuine ecosystem-specific *logic* — those
live entirely inside `codecompass-adaptor-haskell`'s own `app/Main.hs`,
never in this repository's own tracked content.

**Local development**: see
[`../docs/external-adapters.md`](../docs/external-adapters.md) for
clone/submodule setup, building the adapter locally, and the
version-compatibility matrix between CodeCompass, the protocol, and the
adapter.

**Explicit non-claim**: process/repository/license separation is an
architectural property, not a legal conclusion about GPL compatibility
for a future proprietary adapter distributed this way — see
`decisions/0057`'s and `decisions/0058`'s own closing sections. Any real
future proprietary adapter distribution model needs review from a
qualified open-source/IP legal specialist first.

## Module tiers: CORE, AGENT, HOST-OUTPUT ADAPTERS

The runtime modules under `src/codecompass/` group into three tiers —
host-agnostic content production kept separate from tool-specific
rendering — plus one module that fits neither:

- **CORE** (host-agnostic — behaves identically whether Claude Code, a
  plain terminal, or some other agent runtime is driving it):
  `discovery.py`, `config.py`, `adapters/**` (the *ecosystem* adapters —
  see **Adapter interface** above), `sync.py`, `symbols.py`,
  `filetree.py`, `deptree.py`, `usage.py`, `source_resolution.py`,
  `staleness.py`, `graph.py`, `claude_md.py`, `doc_mapping.py`,
  `doc_chunking.py`, `skill_scan.py`, `spec_docs.py`, the `query` CLI
  subgroup, and `enrich apply`.
- **AGENT** (interchangeable content producers, each writing through
  CORE's own graph tables rather than through one another):
  `enrichment.py` and `relation_enrichment.py` (direct-Anthropic-API
  producers), and the `context-enrichment-agent` role (agent-driven
  producer invoked via `enrich apply`, `decisions/0054`).
- **HOST-OUTPUT ADAPTERS** (format-specific renderers with no logic of
  their own beyond templating content CORE/AGENT already computed):
  `skill.py` (Claude Skills + Cursor `.mdc`), `commands.py`
  (`/discovery`), `index.py` (root `CLAUDE.md` routing table).
- **SECONDARY**: `chat.py` is a fourth, standalone consumption surface
  that doesn't cleanly fit any of the three tiers above — it is neither
  a content producer nor a router to another surface.

**Maintenance-burden caveat**: the tool-level Skill's command list
(`skill.py::render_tool_skill`), `/discovery`'s command list
(`commands.py::render_discovery_command`), and
[`docs/cli-reference.md`](../docs/cli-reference.md) are three
independently hand-maintained enumerations of the same `query`
subcommand set, kept in sync by convention rather than by any shared
source. Adding a new `query` subcommand means updating all three by
hand; there is no structural safeguard against one being missed.

## Symbol/purpose extraction (`codecompass.symbols`)

`Symbol(name, purpose, export_kind="export", note=None)` plus one no-AI,
no-subprocess extractor per ecosystem, each `Path -> list[Symbol]`:
`extract_python_symbols` (`ast`-based top-level `def`/`class` +
docstring), `extract_rust_symbols` (line-based `pub fn`/`struct`/`enum`/
`trait` + `///` doc-comment scan), `extract_npm_symbols` (regex scan of
`.d.ts` `export function/class/interface/const/type/enum <name>` + a
leading JSDoc line) — none of these three sets anything but `export_kind`'s
default, since none has a confidence-tiering concept of its own.
`purpose_for_file(path, ecosystem)` dispatches to the matching extractor
by ecosystem *and* file suffix, falling back to a generic leading-
comment-marker scan (`#`, `//`, `/*`, `"""`, `'''`) for files no
ecosystem parser claims. Extraction functions never raise — a file that
fails to parse returns `[]`/`None`.

`export_kind`/`note` generalize `decisions/0059`'s external-wire-protocol
addition — see [`core-data-model.md`](core-data-model.md) and
[`adapter-interface.md`](adapter-interface.md) for the full reasoning
behind the deliberately narrow, non-`kind` naming.

This module is shared: `adapters/cargo.py` and `adapters/python.py` call
into it for their `readme_and_api_surface()` output, and `filetree.py`
(below) calls it for per-file purpose annotations and the symbol index.
See
[`decisions/0015`](../decisions/0015-symbol-extraction-reuses-adapter-parsing-per-ecosystem.md).

## Tree generation — deterministic, always free

`FILETREE.md` and `DEPTREE.md` (plus `filetree.json`/`deptree.json`
sidecars) involve **no AI calls** and run on every `sync` for every
tracked vendor. `codecompass.deptree` renders from a `DepNode` tree;
`codecompass.filetree` renders from `sync_vendor`'s clone-or-fallback
root, not unconditionally `source_location()` — that root is
`vendor/<name>/src/`'s clone content (via `codecompass.source_resolution`,
`decisions/0021`) for **every** vendor, unconditionally
(`decisions/0033`); when this run's clone attempt fails, it falls back to
the vendor's **locally-installed** source directory (`source_location()`)
instead, the same fallback semantics already established for the
`vendor/<name>/src/` snapshot itself. `FILETREE.md` therefore reflects a
vendor's actual upstream repository (README, docs, tests, examples
included) rather than a possibly-trimmed local install, for every
tracked vendor whose clone succeeds. Both tree renderers are wired into
`sync.py`, which writes their output to
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
  **Known gap, disclosed, not fixed**: this function and
  `purpose_for_file` are per-file, synchronous, no-subprocess, with zero
  adapter awareness — they take `(path, ecosystem)`, not an adapter
  instance, so a Haskell vendor's `FILETREE.md` still shows no
  symbol-index entries, even though `context-graph.db`'s own `symbols`
  table (via `adapter.symbols()`) correctly holds its real symbols.
  Retrofitting this would mean either spawning the external process once
  *per file* during the tree walk (a severe regression, the opposite of
  the per-instance cache in [`adapter-interface.md`](adapter-interface.md)),
  or threading a pre-fetched `Symbol` list through the whole
  `FILETREE.md`-rendering call chain — a materially larger change than a
  "smallest justified interface change" scope covers.
- **Cross-linking FILETREE entries to description action pointers**
  (e.g. `src/commonmark-rules.js  ← ACTION TARGET: override
  fencedCodeBlock here`) — the `action_pointer` parameter above.
  `sync_vendor` threads `(action_pointer_file, action_pointer_note)`,
  read from this vendor's current enrichment record in the context graph
  (`decisions/0035`), into both `render_filetree_markdown` and
  `render_filetree_json`; a vendor with no enrichment record yet passes
  `None` and the parameter has no effect.

## Per-vendor CLAUDE.md structure (`codecompass.claude_md`)

`render_vendor_claude_md(digest: VendorDigest) -> str`. `sync_vendor`
never generates a vendor's Description content itself — before building
`VendorDigest`, it opens a read-only connection to `context-graph.db`
(`None`, gracefully, if the file doesn't exist yet) and looks up that
vendor's current `vendor_enrichment` row, if any; `codecompass.enrichment`
(see [`sync-and-enrichment-pipeline.md`](sync-and-enrichment-pipeline.md))
is the only writer of that table (`decisions/0035`). This makes a
from-scratch `CLAUDE.md` regeneration —
including a plain whole-project `sync` that touches every tracked
vendor, not just newly-enriched ones — idempotent with respect to
enrichment: it always reproduces whatever the graph currently says.
`digest.description_error` is set only by a source-clone failure
(`SourceResolutionError`), never a description failure — there is no
description "attempt" inside `sync_vendor` to fail, so a clone failure
and an existing enrichment record are unrelated facts about the same
vendor.

Sections, in order:

1. **Metadata** — ecosystem and a `**Installed version:**` line. This
   exact format (`\*\*Installed version:\*\*\s*(\S+)`) is what
   `claude_md.read_installed_version` regexes against — a shared helper
   both `staleness.py` and `index.py` (populating the routing table's
   Version column) call, rather than each keeping its own copy of the
   regex. It is load-bearing, not cosmetic.
2. **Grounding preamble** — fixed instructional text: the pinned version
   is authoritative over training knowledge for this library. This is the
   actual mechanism that changes agent behavior — without an explicit
   "prefer this over what you already know" instruction, an agent has no
   signal to override its training data.
3. **Public API surface** — `digest.api_surface`.
4. **Description + action pointer** — `digest.technical_description` plus
   an `**Action pointer:**` line when `digest.action_pointer_file` is set.
   Omitted entirely (no heading at all) when `technical_description` is
   unset — a vendor with no enrichment record yet. This section never
   consults `digest.description_error`: a vendor with a good enrichment
   record still shows its Description even on a run where this sync's
   own clone attempt failed, since description content comes from the
   graph, not from this run's own generation attempt.
5. **Known gotchas** — deterministically derived from `digest.side_effects`
   (the dependency tree's root `DepNode.side_effects`, e.g. npm's
   postinstall-script detection) rather than left empty or AI-generated.
   A vendor with none detected renders a fixed "No known side effects
   detected." line.
6. **Quick links** — relative links to `./FILETREE.md`, `./DEPTREE.md`,
   and a backlink to the project root `CLAUDE.md`.

A second, narrower write path exists alongside this from-scratch
renderer: `update_description_section`/`read_enrichment_hash` (see
[`sync-and-enrichment-pipeline.md`](sync-and-enrichment-pipeline.md))
rewrite just an already-rendered file's
Description section and a `**Enrichment symbol-set hash:**` metadata
line in place, for `codecompass.enrichment`'s batched, usage-driven
enrichment. This path has no eligibility gate of its own — it's only
ever invoked for a vendor `codecompass.enrichment` just actually
enriched, never as a generic re-render. Both write paths agree on
exactly the same "is there enrichment content" test
(`technical_description`'s own truthiness), reading from and writing to
the same `vendor_enrichment` table.

## Two consumption modes

Both must work:

1. **Standalone** — `cd vendor/<name> && claude`. Requires a *copied*
   pinned source snapshot at `vendor/<name>/src/`, for every tracked
   vendor, unconditionally (`decisions/0033`), NOT a reference into
   `node_modules` — package managers prune/dedupe/reinstall `node_modules`
   contents, so it isn't a stable pin target. See
   [`decisions/0004`](../decisions/0004-vendor-src-snapshot-not-node-modules-reference.md).
   The snapshot is a shallow `git clone` of the vendor's own upstream
   repository (`codecompass.source_resolution`, `decisions/0021`) rather
   than a copy of the local install — richer (a published package often
   excludes docs/tests) and, per `decisions/0004`'s own underlying
   concern, at least as stable a pin target. If source resolution fails,
   `sync_vendor` falls back to a pruned copy of `source_location()`
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
   it. Table columns: Vendor, Path, Version, Enriched, Deps, Consult when —
   paired with an explicit routing instruction sentence, since the table
   alone is inert data. `index` **reads each vendor's already-synced
   `CLAUDE.md`** (regexing the Metadata section's `**Installed
   version:**` line) rather than re-running `sync` — this keeps `index`
   cheap and side-effect-free even though `sync` itself may make AI
   calls, and a vendor with no synced `CLAUDE.md` yet shows `_not
   synced_` rather than erroring. The Version column has no ✅/⚠
   freshness indicator — `check` reports staleness in its own separate
   table (`codecompass check`) rather than being wired into `index`'s
   routing table, a deliberate scope boundary rather than an oversight
   (see **Known footguns**); the Deps column links to `DEPTREE.md`
   rather than showing a live dependency count, since `index`
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

Never builds a `VendorDigest` — the same reasoning `index.py` already
established for staying cheap and side-effect-free. `VendorStaleness`
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
  itself uses — unmodified. This makes **no AI call**: `sync_vendor`
  only re-clones and re-renders deterministic output, reading back
  whatever enrichment content the context graph already has (see
  **Per-vendor CLAUDE.md structure** above); `--fix` never re-purchases
  a vendor's description. `check`'s own `--fix` loop (not
  `sync_vendor`) wraps each regeneration in `try/except AdapterError`, so
  one vendor's broken adapter read doesn't abort the rest of the batch;
  exits non-zero if anything failed — either an adapter error, or a
  vendor whose `sync_vendor` call hit a source-clone failure
  (`digest.description_error`) — 0 otherwise.

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
instruction-following alone. A vendor's Skill/`.mdc` pair is written by
`enrichment.apply_results`
(see [`sync-and-enrichment-pipeline.md`](sync-and-enrichment-pipeline.md))
the moment usage-driven AI enrichment succeeds for that vendor,
automatically — no separate command to trigger it (`decisions/0018`,
`decisions/0033`).

One Skill per **enriched** vendor (one with a `vendor_enrichment`
record), generated at `.claude/skills/codecompass-<vendor>/SKILL.md`:
- The trigger description is built from data already generated — a
  condensed conversational overview — not a new AI call. **Description
  length is a real, ongoing tuning knob, not a one-time writing task**:
  every skill's name+description loads into every session
  unconditionally, so a long description that maximizes one vendor's
  trigger accuracy has a real per-vendor cost that compounds as enriched
  vendor count grows (`_VENDOR_SKILL_DESCRIPTION_CAP`, 400 characters).
  Specificity (concrete API methods, file/function names, exact trigger
  situations) — not length — is what drives triggering accuracy.
- `FILETREE.md`/`DEPTREE.md` bundle as `references/` files inside the
  skill folder rather than inlining — progressive disclosure means they
  only cost tokens when Claude actually needs to navigate source.
- A wrapper script shelling out to `codecompass check <vendor>` at trigger
  time (a live staleness read instead of a cached line) is deferred to a
  later phase, not required for the initial export.
- A formal trigger-accuracy evaluation harness (a battery of test
  questions checked against whether the Skill actually loads) is not
  implemented — the same category of manual-verification gap accepted
  for AI-generated content against the live API generally
  (`decisions/0016`), extended here to Skill triggering.
- A vendor with no enrichment record yet doesn't get a per-vendor Skill —
  no grounded-description content exists to build a meaningful trigger
  description from. This gap is covered separately by the **tool-level
  Skill** (`decisions/0020`): a templated, non-AI-generated Skill at
  `.claude/skills/codecompass/SKILL.md`, generated unconditionally by
  `index` (and by bare `codecompass`) regardless of vendor count or
  enrichment status — listing codecompass's own commands and the current
  vendor table, so an agent has a mechanical signal that codecompass
  exists even before any vendor has been enriched.

**Cursor `.mdc` export** targets Cursor's modern context system — Cursor
does not read `CLAUDE.md` natively. `.cursor/rules/*.mdc` files use YAML
frontmatter (`description`, `alwaysApply`) to control activation — the
legacy single `.cursorrules` file is deprecated and unreliable in
Cursor's agent mode specifically, so it isn't targeted. `.mdc` is a
**generated export**, not a separately maintained file — same
technical-description content as the Skill, different serialization —
written to `.cursor/rules/codecompass-<vendor>.mdc` by
`enrichment.apply_results` alongside the Skill. `alwaysApply: false`
(token cost control, same reasoning applied to the Skill description
cap above); Cursor falls back to description-based relevance without an
explicit `globs` key — a `globs` field scoped to wherever the vendor is
actually imported in the consuming codebase is a documented future
refinement, not implemented (would require scanning the consuming
project's own source, a different kind of input than enrichment reads
today). Cursor's glob-scoped file-pattern activation is a different —
potentially more precise, once implemented — trigger model than Skills'
description-matching, and not every Cursor setup has Skills support, so
this export exists alongside Skills, for Cursor users specifically.

**The `CLAUDE.md` root routing table** is the fallback for any tool or
context that doesn't support Skills at all, including the standalone
`cd`-into-vendor scenario (see **Two consumption modes** above), which
isn't a "current task the agent judges relevant" situation the way
Skills triggering assumes.

## `/discovery` custom slash command — `codecompass.commands`

A third generated-artifact type alongside Skills and `.mdc` rules, but a
genuinely different Claude Code mechanism from either: a **custom slash
command**, written to `.claude/commands/discovery.md` and invoked
explicitly by typing `/discovery` inside a Claude Code session, rather
than auto-triggered by description matching the way Skills are.
`codecompass.commands` follows `codecompass.skill`'s render/write split
(`render_discovery_command() -> str` /
`write_discovery_command(project_root: Path) -> None`) rather than
inventing a new pattern, but stays a separate module — different
directory convention, different frontmatter shape, no vendor-specific
content threaded in (unlike `render_tool_skill`, its content is entirely
static: it teaches Claude *how* to explore whatever a project's
codecompass output currently is, not what that output currently
contains).

**Generated unconditionally**, same free/no-AI-cost posture as the
tool-level Skill, at every whole-project trigger point: bare
`codecompass`, `codecompass index`, and whole-project `codecompass sync`
(the last via `_refresh_generated_artifacts`, which regenerates the
routing table, the tool-level Skill, and `/discovery` together at the
end of the invocation — see **Retrofitting to existing projects** below).

**Mechanically read-only for the single turn that invokes it; held by
prose for the rest of the session (`decisions/0040`).** Its frontmatter
sets `allowed-tools` to `Read`/`Grep`/`Glob` plus narrowly-scoped
`Bash(...)` patterns for exactly two sanctioned escape hatches:
`codecompass query`/`check`, and read-only `sqlite3` access to
`context-graph.db` for anything the canned `query` subcommands don't
cover. `Write`/`Edit` are never granted — but confirmed against actual
Claude Code behavior, not assumed, this pre-approval grant **clears the
moment the next message is sent**; nothing re-applies it or blocks
`Write`/`Edit`/`ExitPlanMode` on a later turn in the same conversation.
There is no frontmatter field or session "mode" that locks a whole
conversation to read-only. The command body is written knowing this: it
states the mechanical grant's one-turn scope explicitly and instructs
Claude to hold the read-only posture — no plan file, no code change, say
so and stop if one would be needed — for every later turn by default,
deliberately, not because the frontmatter still enforces it.

**Indexed into the context graph the same way Skills/`.mdc` rules are**:
`skill_scan.scan_skills` (a name that predates this artifact type, but
the function covers all three) additionally globs for
`.claude/commands/discovery.md` and, if present, appends it as a
`doc_artifacts` row (`kind='slash_command'`). Flowing through the same
`scan_skills` return value it also participates in
`skill_scan.build_skill_mentions_edges`' word-boundary mention detection,
same as any other Skill/`.mdc` doc artifact.

`graph.skills_index`/`codecompass query skills` surface the
`/discovery`-generated `doc_artifacts` row too: the read-side query
matches `kind IN ('skill', 'cursor_mdc', 'slash_command')`, so a
`slash_command` row (and any Cursor `.mdc` rule) appears alongside Skills,
each tagged with its `kind`.

## Chat REPL

**Chat is a secondary, dev/debug-oriented tool, not the product's primary
interface**, per
[`decisions/0034`](../decisions/0034-chat-demoted-graph-and-skills-are-primary.md).
The SQLite context graph (`codecompass.graph`), generated Skills, and the
`/discovery` slash command are the primary way both humans and agents
consume codecompass's output (see **Multi-tool export** and
**`/discovery`** above). `chat <vendor>` remains fully functional and
genuinely useful for a quick, digest-only Q&A in a plain terminal — just
not the product's centerpiece.

The digests (`CLAUDE.md`, `FILETREE.md`, `DEPTREE.md`, and — for a vendor
that's been usage-driven AI-enriched — `OVERVIEW.md`, the persisted
conversational overview) are backing store for two consumers — AI agents
reading them directly (see **Two consumption modes** above) and `chat`
synthesizing them into conversation — and content generation is written
with "does this read well spoken aloud in a casual chat" as a first-class
constraint, not an afterthought handled by reformatting at query time.

`codecompass chat <name>` — a lightweight terminal REPL, distinct from
just using Claude Code in the vendor folder. It loads only `CLAUDE.md`
(and `OVERVIEW.md`, if the vendor's been AI-enriched) as system context and
calls the API directly (Haiku) with plain multi-turn text completion — no
forced tool-use, no tool-use/file-exploration loop — faster and cheaper
per query, but strictly narrower: it only knows what's in those two files,
not `FILETREE.md`/`DEPTREE.md` or the full pinned source. This tradeoff is
stated in the REPL's startup banner so a user doesn't over-trust an answer
beyond what the digest actually covers. Critically, `chat` never calls
`sync` — it reads whatever's already on disk, so starting a session never
re-incurs a clone or an AI-generation call (`decisions/0023`).

- **Explicit vendor** (`chat turndown`) — the only mode implemented
  today. Loads that vendor's `CLAUDE.md`/`OVERVIEW.md` only, single
  system prompt, no routing needed. Works whether or not the vendor's
  been AI-enriched — one with no `OVERVIEW.md` yet gets thinner
  grounding plus a `sync` hint, not a hard block.
- **No vendor specified** (project-root mode) — **not yet implemented.**
  Would load a project-wide dependency rollup and route between vendor
  and project context. See
  `planning/phase-20-chat-project-root-routing-design.md` for the full
  (unbuilt) design.

`Table` (Rich) renders `check`/`query` output; `Markdown` renders chat
answers.

## Retrofitting to existing projects

Two phases, back to back, both triggered from the same call sites (bare
`codecompass` and whole-project `sync` — `init --scan` and
`sync <vendor>` are explicitly not trigger points): **Phase A** is the
always-free, no-prompts bootstrap (manifest discovery, `vendor.toml`
write/refresh, universal cloning, tree generation, graph rebuild);
**Phase B** is usage-driven AI enrichment, auto-triggered right after
Phase A but kept behind a real disclose-and-confirm gate
(`decisions/0031`, `decisions/0033`). See
[`sync-and-enrichment-pipeline.md`](sync-and-enrichment-pipeline.md) for
the full traced flow, including the cost/budget gate and both phases'
exact call sequence. Artifacts derived from the graph (the routing
table, the tool-level Skill, `/discovery`) are refreshed once,
unconditionally, at the end of the invocation, after Phase B returns —
success, decline, or budget-abort — so they never reflect
pre-enrichment state; see [`historical-notes.md`](historical-notes.md)
for the bug this design fixed.

`codecompass init --scan <manifest file> [--scan <manifest file> ...]`
(`codecompass.discovery`) is the explicit, scripted/CI-friendly synonym
for Phase A's discovery step — useful for naming specific manifests
rather than relying on root-level auto-discovery. Unlike bare
`codecompass`, it keeps a stricter contract: errors rather than
overwriting if `vendor.toml` already exists. It is not a Phase A/B
trigger point itself — no cloning, no graph rebuild, no Phase B.

`promote` is retired (`decisions/0033`) — its three former jobs (clone,
enrich, generate Skill/`.mdc`) are these two phases' automatic outcomes.
`codecompass query vendor <name>`/`check` are the replacement for
"inspect what promote would tell you," reading the graph rather than
requiring a vendor to have been manually escalated first.

## Context graph (`codecompass.graph`)

Fully populated at both whole-project call sites (bare `codecompass` and
whole-project `sync`) and CLI-readable via `query`/`check`. See
[`context-graph-schema.md`](context-graph-schema.md) for the literal
schema — every table, the closed `kind`/`origin`/`relation_kind` sets,
which tables survive a rebuild and why, the migrations, and every
read/write function — and
[`sync-and-enrichment-pipeline.md`](sync-and-enrichment-pipeline.md) for
how `sync.rebuild_project_graph` populates it end to end. See
[`decisions/0032`](../decisions/0032-context-graph-stored-in-sqlite.md)
(SQLite storage) and
[`decisions/0025`](../decisions/0025-context-graph-rebuilds-only-on-whole-project-sync.md)
(full rebuild only on whole-project `sync`, never incrementally).
`context-graph.db` is gitignored — a deterministic, cheaply
regeneratable artifact, same precedent as `vendor/` (`decisions/0010`).

**Spec docs and vendor docs** (`codecompass.spec_docs`, extended
`codecompass.doc_mapping`) are the two non-generated `doc_artifacts`
sources: `spec_docs.scan_spec_docs` globs a fixed default pattern set
rooted at the project (`README.md`, `ARCHITECTURE.md`, `docs/**/*.md`,
`architecture/**/*.md`, `decisions/**/*.md`, `spec/**/*.md`,
`ai-docs/**/*.md`, `dev-docs/**/*.md`, and similar), excluding
`CHANGELOG.md`, `CONTRIBUTING.md`, `LICENSE*`, and root `CLAUDE.md`
itself, plus anything under `vendor/` or another pruned directory;
`doc_mapping.collect_vendor_upstream_doc_artifacts` globs a small fixed
root-level filename set (`README*.md`, `CHANGELOG.md`, `CONTRIBUTING.md`,
`SECURITY.md`, `MIGRATION.md`) directly under each vendor's own cloned
source. Each row's `name` is extracted via a title-extraction function
with a specificity guard: the doc's own first level-1 heading text if it
exists and is "specific enough" (more than one word, or containing a
digit/hyphen), else the filename stem if that's specific enough, else
`None` — this guard exists because a bare repo-name heading (`#
ledgerkit`) or one-word stem produces guaranteed noise once used as a
`mentions_artifact` match target, confirmed against a real reference
project. Both spec docs and vendor docs can be a relation *source*
(`doc_mapping.build_doc_relations_edges`, closed allow-set) as well as a
relation *target* — including a vendor's own embedded README both
documenting its own symbols (`documents_edges`) and mechanically
mentioning another tracked vendor or doc artifact
(`doc_relations_edges`) — with two independent self-mention exclusions
(by vendor name, by doc path) preventing guaranteed-noise edges; see
[`context-graph-schema.md`](context-graph-schema.md) and
[`decisions/0043`](../decisions/0043-vendor-docs-become-relationship-sources-closed-allow-set-plus-self-mention-exclusion.md).
Mention detection throughout this arc is **word-boundary
(`\b<name>\b`), not substring** — see
[`sync-and-enrichment-pipeline.md`](sync-and-enrichment-pipeline.md).

**Doc chunking** (`codecompass.doc_chunking`) splits a chunkable doc
artifact's markdown text into heading-scoped chunks
(`chunk_markdown(text) -> list[DocChunk]`) — root-first nested
`heading_path`, 1-indexed inclusive line ranges, a per-chunk content
hash — used to attribute a mechanical mention to the specific heading
section it occurred in, when exactly one chunk's text contains it. It
tracks fenced-code-block state and never treats a line inside one as a
heading candidate — a `#`-prefixed comment in an example fence would
otherwise be misdetected as a real heading, confirmed live against this
repo's own `docs/cli-reference.md`. See
[`decisions/0046`](../decisions/0046-doc-chunking-heading-based-additive.md).

**Relationship enrichment** (`codecompass.relation_enrichment`) asks an
AI call to explain, in a sentence or two, *how* a spec/vendor doc relates
to something already mechanically proven (the same "mechanical detection
first, AI enrichment only over what it proved" gating
`decisions/0031`/`0033` established for vendors, generalized to
relationships) — see
[`sync-and-enrichment-pipeline.md`](sync-and-enrichment-pipeline.md) for
current excerpt-selection and candidate-caching behavior, and
[`historical-notes.md`](historical-notes.md) for why today's fixed-window
excerpt fallback exists at all. The AI-generated summary is written
*only* to `doc_relation_enrichment`, never into a spec doc's own file —
enforced structurally (`apply_results` has no filesystem handle to write
one). A second, agent-driven producer writes through the same function
(`codecompass enrich apply`, `decisions/0054`), distinguished only by its
`model` value.

**CLI surface**: `codecompass query relations <name>` — given a spec/
vendor doc path, prints what it mechanically mentions; given a vendor or
doc artifact name, prints which docs mechanically mention it (see
[`docs/cli-reference.md`](../docs/cli-reference.md)). `check` reports two
independent coverage-gap sections — spec docs with no detected outgoing
relations, and vendor docs nothing points at — neither `--strict`-blocking,
the same posture as every other graph-derived coverage gap.

## `undo` — best-effort generated-artifact cleanup (`codecompass.cli`)

`codecompass undo [--yes] [--dry-run]` (`decisions/0036`) is the only
command whose job is to *remove* generated
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
effectively free, for every tracked vendor, regardless of usage. **Phase
B is the sole AI cost center in this codebase** (`decisions/0031`):
usage-driven batched enrichment, using Haiku, wired into `cli.py` behind
bare `codecompass` and whole-project `sync` (see "Retrofitting to
existing projects" above and
[`sync-and-enrichment-pipeline.md`](sync-and-enrichment-pipeline.md) for
the full disclose/confirm/budget flow). Phase B is **cached** — a vendor
already enriched at its current used-symbol set is skipped
(`enrichment.select_candidates`'s two-tier hash check), so cost scales
with how often the project's actual dependency *usage* changes, not with
how often `sync` is run. `enrichment.estimate_cost(batch_count,
relation_batch_count=0)` / `enrichment.check_budget(candidates, budget,
relation_candidates=None)` scale with `len(plan_batches(candidates))`
(batches, not vendors) — several vendors' material and output share one
call. `--yes` skips the confirmation prompt; `--budget <amount>` refuses
to make any Phase B API call at all (not partially) once the projected
cost for a single run exceeds the cap. Regardless of how Phase B ends —
enriched, declined, or budget-aborted — `cli._refresh_generated_artifacts`
still runs once at the end of the invocation, so a budget-aborted run's
already-free Phase A output is left with a freshly-regenerated routing
table/tool Skill, not a stale one from before the abort.

Spec-doc relationship enrichment (`codecompass.relation_enrichment`)
folds into this same cost center, not a second one: `relation_
batch_count`/`relation_candidates` (both optional) let `estimate_cost`/
`check_budget` add `len(relation_enrichment.plan_batches(relation_
candidates))` batches to the same flat per-batch rate — one Anthropic
call either way, a vendor batch or a relationship batch. `cli.py`'s
`_maybe_run_enrichment` selects both candidate sets up front, discloses
one combined estimate, and gates both behind the same confirm/`--yes`/
`--budget` — a relationship-only run (zero vendor candidates, some
relationship candidates, or vice versa) still triggers exactly this one
prompt, never a silent skip and never a second separate one. Also
cached, the same way vendor enrichment is, though by a single
content-hash check (source spec doc text + target's digest text), not a
two-tier one — spec docs are never written to, so there's no file-level
fallback cache to check a second way.

**There is no other cost path.** `sync`/`check --fix` make no AI call at
all; Phase B, triggered only from bare `codecompass` and whole-project
`sync`, is the only place this codebase spends Anthropic-API money.

## Known footguns

- **`resolve_and_clone`'s `subdirectory` scopes the *rendered* view
  only, never the raw on-disk clone.** `_git_clone` always clones the
  *whole* upstream repository into `dest` (`vendor/<name>/src`);
  `subdirectory` only changes the function's *return value*
  (`source_root = dest / subdirectory`), which `sync_vendor` consumes as
  `tree_root` for rendering `FILETREE.md`/the symbol index. For a
  monorepo (npm's `repository.directory`, or two Haskell packages
  sharing one repository URL — `hledger-lib`/`hledger`), every vendor
  backed by the same upstream repository gets its own full, duplicate,
  unscoped clone at `vendor/<name>/src/` — doubled disk cost per
  sibling, and a real misattribution risk for anyone who `grep`s/`find`s
  the raw clone directly instead of following `FILETREE.md`. Confirmed
  live: `vendor/hledger-lib/src/` and `vendor/hledger/src/` are
  byte-identical top-level listings of the whole monorepo, while both
  packages' `FILETREE.md`s stay correctly scoped to their own package.
- **`readme_and_api_surface()` (any ecosystem adapter) extracts a
  symbol's declared one-line purpose (doc-comment/docstring/Haddock),
  never its body.** It answers "what exists and what's it called," not
  "what does it do" or "why does behaviour differ between two call
  sites of it." Confirmed three times independently across two
  structurally different context sources: a hand-curated
  `dev-docs/hledger-reference/` corpus and a live
  Haskell-adapter-generated `CLAUDE.md` digest (`grep -ci depth` returns
  `0` across all 44 rendered command modules, including the ones the
  task specifically asked about). A task whose answer depends on
  control-flow/business-logic detail inside a function body is not
  answerable from the digest alone, regardless of ecosystem or whether
  the digest came from human curation or mechanical generation — direct
  source reading is required for that class of question by design, not
  by omission.
- **`VendorDigest` has no `is_stale` field** — `check` never builds a
  `VendorDigest` (the same reasoning `index.py` established for staying
  cheap), so there is no code path that could ever populate one. If
  older notes or memory reference `digest.is_stale`, that API doesn't
  exist; use `codecompass.staleness.check_vendor`/`check_all` instead.
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
- The `.d.ts` file cap (5 files) in the npm adapter, and the matching
  `.pyi` cap in the Python adapter, are arbitrary initial values for
  cost control, not validated final numbers — flag if they clip useful
  API surface on real-world packages.
- `vendor/<name>/src/` snapshots are gitignored and regenerated by
  `sync`, not committed (see
  [`decisions/0010`](../decisions/0010-vendor-src-gitignored-and-regenerated.md)).
  A fresh clone has no working standalone-mode chat until `sync` has
  been run at least once — easy to forget when onboarding a new
  checkout.
- **`_run_json`'s subprocess seam resolves `cmd[0]` via `shutil.which`
  before invoking it** — not just for a nicer "not found" error. On
  Windows, `npm` resolves to a `.cmd` shim, which `subprocess.run` can't
  launch by bare name without a shell; resolving to the full path first
  keeps `shell=False` (and its narrower injection surface) working
  cross-platform. Found and fixed via a live npm smoke test — fixture-only
  testing would not have caught it (see
  [`decisions/0014`](../decisions/0014-adapter-tests-use-fixture-mocking-not-live-subprocesses.md)).
- **The Python adapter invokes `pipdeptree` as `sys.executable -m
  pipdeptree`**, not a bare `pipdeptree` on `PATH` — a standalone venv's
  `Scripts`/`bin` directory isn't reliably on `PATH` unless the venv is
  activated. Also found via a live smoke test, for the same reason as
  the npm fix above.
- **npm `dev_only` is not transitive**: a node is marked `dev_only` only
  if its own name is a *direct* `devDependency` of the root consuming
  project — a transitive dependency of a dev-only package isn't
  propagated. Documented limitation.
- **Python `dev_only` is always `False`** — `pipdeptree`'s output carries
  no dev/runtime distinction once a package is installed, a real
  structural difference from npm's `package.json`, not an oversight.
- **Cargo's API-surface extraction is a coarse, line-based scan**, not a
  real Rust parser — it misses multi-line function/struct signatures
  (generic bounds or `where` clauses spanning lines). `rustdoc
  --output-format json` remains the documented eventual fix.
- **The Cargo adapter is unverified against real `cargo` output** — no
  Rust toolchain has been available in this dev environment. Its
  parsing logic is tested only against hand-written fixture JSON modeled
  on cargo's public schema docs. See
  [`decisions/0014`](../decisions/0014-adapter-tests-use-fixture-mocking-not-live-subprocesses.md)
  for the follow-up required once a toolchain becomes available.
- **`deptree.py`'s `_DEPTREE_MAX_DEPTH` (20)**, **`filetree.py`'s
  `_PRUNE_DIR_NAMES`/`_PRUNE_FILE_GLOBS`, and `_SYMBOL_INDEX_CAP` (200)**
  are initial, arbitrary, tunable values, not validated final numbers —
  flag if they clip useful tree/index content on real-world packages.
- **`CargoAdapter.readme_and_api_surface()` renders items as `name:
  purpose`**, not the raw `pub fn ...` signature line, because
  extraction goes through `symbols.extract_rust_symbols`'s name-based
  `Symbol` objects. See
  [`decisions/0015`](../decisions/0015-symbol-extraction-reuses-adapter-parsing-per-ecosystem.md).
- **`extract_npm_symbols`'s JSDoc/export regex scan is coarse** —
  unlike the Cargo/Python extractors, it has no adapter-level precedent
  of its own and is only tested against hand-written `.d.ts` fixtures,
  not a wide range of real-world authoring styles.
- **`filetree.py`'s directory walk (`_iter_files`) uses `Path.rglob("*")`
  then filters pruned directories post-hoc** — it doesn't stop descending
  into a pruned directory like `node_modules/` before walking it, just
  excludes its contents from the result. Fine at this project's scale
  (a single vendor package's source tree), but not optimized for very
  large pruned subtrees.
- **`enrichment.py`'s `_RAW_TEXT_CHAR_CAP` (50,000), `_DOCS_FILE_CAP`
  (5), and `_ESTIMATED_COST_PER_BATCH_USD` (a rough placeholder, not
  live-queried Anthropic pricing)** are initial, arbitrary, tunable
  values — same treatment as every other cap in this project. The cost
  estimate is not a guarantee of actual billed cost; `--budget` decisions
  should be made with that in mind.
- **No test ever makes a real Anthropic API call** (see
  [`decisions/0016`](../decisions/0016-gap-analysis-tests-never-call-the-live-anthropic-api.md)) —
  `codecompass.enrichment`'s batched prompt/schema correctness against
  the real model is not validated by the automated suite at all; a human
  must run bare `codecompass`/`sync` against a real, usage-proven vendor
  with a real `ANTHROPIC_API_KEY` (confirming with `--yes` or the
  disclosed prompt) to trust Phase B's output quality. Source resolution
  and cloning are separately validated against a real repository
  (pytest's own, via its PyPI `Project-URL` metadata) — only the AI call
  itself remains unvalidated against the live API.
- **`git` is a required external tool for the universal cloning step**
  (every vendor, unconditionally) — `codecompass source_resolution._git_clone`
  shells out to it the same way adapters shell out to
  `npm`/`cargo`/`pipdeptree`, with the same `shutil.which`-first
  resolution pattern. Not declared as a Python dependency (it isn't
  one), but its absence surfaces as a clear `SourceResolutionError`
  rather than a cryptic subprocess failure.
- **`index` reads persisted per-vendor `CLAUDE.md` files rather than
  re-running `sync`** — re-running `sync` inside `index` would make
  `index` silently pay AI cost, defeating the reason `index` exists as a
  separate, cheap command. Consequence: a vendor that's never been
  synced shows `_not synced_` in the routing table instead of an error,
  and the Deps column links to `DEPTREE.md` instead of showing a live
  dependency count (no adapter/tree data is available to `index`).
- **`VendorDigest.side_effects`** is populated by `sync_vendor` from the
  dependency tree's root `DepNode.side_effects` — not from every node in
  the tree, only the vendor's own top-level entry. A transitive
  dependency's side effects (e.g. a sub-dependency's own postinstall
  script) aren't surfaced in Known Gotchas.
- **`sync_vendor` fully overwrites `vendor/<name>/` on every call** — no
  diffing, no incremental update, and the entire `vendor/<name>/src/`
  snapshot is deleted and recopied each time, not merged, for every
  vendor. Simple and correct, but means a large vendor's `sync` is not
  cheap to run repeatedly in a tight loop.
