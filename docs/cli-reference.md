# CLI reference

> `init`, `sync`, `index`, `check`, `query`, and `chat` are implemented.
> `promote` was removed in Phase 15 (`decisions/0033`) — its three former
> jobs (clone, enrich, generate Skill) are now automatic outcomes of
> bootstrap/`sync`. See [`planning/`](../planning/) for current status.

## `codecompass [--yes] [--budget <amount>]` (no subcommand)

**Status:** implemented (Phase 7, `decisions/0017`; Phase B auto-trigger
added Phase 15, `decisions/0031`/`decisions/0033`).

Two phases, back to back:

- **Phase A** (always free, no prompts): auto-discovers manifests at the
  project root (`package.json`, `pyproject.toml`, `requirements.txt`,
  `Cargo.toml`), writes every discovered dependency into `vendor.toml`,
  clones every vendor's source, regenerates `FILETREE.md`/`DEPTREE.md`/
  `CLAUDE.md` for any newly-discovered vendor, refreshes the root
  `CLAUDE.md` routing table, writes the tool-level Skill
  (`decisions/0020`), and rebuilds `context-graph.db` from the whole
  project's current state.
- **Phase B** (usage-driven AI enrichment, `decisions/0031`): if that
  rebuild finds vendors actually imported by the project's own source
  with no up-to-date enrichment yet, this phase auto-triggers —
  discloses an estimated cost, asks for confirmation (`--yes` skips the
  prompt), and on confirmation calls the Anthropic API in batches to
  generate each vendor's grounded description, per-symbol purposes, and
  Skill/`.mdc` export. `--budget <amount>` caps estimated spend (USD),
  checked *before any API call* — if exceeded, Phase B aborts (Phase A's
  already-completed output is unaffected) and the command exits non-zero.
  Declining the confirmation prompt skips Phase B without affecting exit
  code — Phase A already succeeded.

- If `vendor.toml` doesn't exist yet, Phase A is equivalent to `init
  --scan` against every manifest found at the project root.
- If `vendor.toml` already exists, Phase A is an **idempotent refresh**:
  newly-discovered dependencies are appended; already-tracked vendors are
  left untouched by Phase A itself (Phase B may still pick one up if its
  usage or enrichment status changed).
- No manifests found is not an error — it produces (or leaves) an empty
  `vendor.toml`, and Phase B has nothing to trigger on.
- No usage-proven enrichment candidates is the common case for a small or
  freshly-bootstrapped project — Phase B is then a silent no-op, and the
  whole command stays as prompt-free as it always was.

```bash
codecompass
codecompass --yes
codecompass --budget 1.00
```

## `codecompass init --scan <manifest file> [--scan <manifest file> ...] [--output <path>]`

**Status:** implemented (Phase 4). The explicit, scripted/CI-friendly
synonym for bare `codecompass`'s auto-discovery (`decisions/0017`) —
useful when you want to name specific manifest files rather than rely on
root-level auto-discovery.

Bulk-discovers dependencies from the given manifest files (`package.json`,
`pyproject.toml`, `requirements.txt`, `Cargo.toml` — dispatched by
filename) and writes a draft `vendor.toml` with every discovered
dependency defaulted to `depth = surface`. Free to run — surface
generation has no AI cost.

- `--scan` is repeatable, one manifest file per flag (not space-separated
  after a single flag — that's not how a named Click/Typer option works).
- `--output` (default `vendor.toml`) is where the draft is written.
- Errors, rather than overwriting, if a `vendor.toml` already exists at
  the target path — unlike bare `codecompass`, this keeps a strict
  contract for scripted use.
- `[project.optional-dependencies]` in `pyproject.toml` is not scanned —
  only `[project.dependencies]`.

```bash
codecompass init --scan package.json --scan pyproject.toml --scan Cargo.toml
```

## `codecompass sync [<vendor>] [--yes] [--budget <amount>]`

**Status:** fully implemented (Phases 4, 7; Phase B auto-trigger added
Phase 15).

Regenerates digests and trees. With no argument, syncs every vendor in
`vendor.toml`; with a vendor name, syncs just that one (errors clearly if
the name isn't found).

- Deterministic output — `FILETREE.md` (including the flat symbol index,
  appended as its own section), `DEPTREE.md`, `filetree.json`,
  `deptree.json`, and the per-vendor `CLAUDE.md` (Metadata, Grounding,
  API surface, Description, Known gotchas, Quick links) — is always
  regenerated under `vendor/<name>/`, and a `vendor/<name>/src/` snapshot
  is cloned from the vendor's own upstream repository (`decisions/0021`
  — falls back to a local-install-sourced copy if source resolution
  fails). Neither makes an AI call.
- **Whole-project sync only** (no vendor name): after every vendor's
  deterministic output is regenerated, `context-graph.db` is rebuilt from
  the project's current state, and — same Phase B trigger as bare
  `codecompass` (`decisions/0031`/`decisions/0033`) — if usage-proven
  enrichment candidates exist, their cost is disclosed and confirmed
  (`--yes` skips the prompt) before any AI call. `sync <vendor>` (a named
  vendor) skips both the graph rebuild and the Phase B trigger
  (`decisions/0025`).
- `--budget <amount>` caps estimated AI spend (USD) for this run —
  checked *before any API call is made*, covering both a whole-project
  sync's Phase B batch and (unchanged from before this phase) any
  `depth = full` vendor's per-vendor grounded-description regeneration —
  `Depth` isn't retired until Phase 16. If the estimate exceeds
  `--budget`, that step aborts; already-written deterministic output for
  other vendors is unaffected. Omit `--budget` for no cap.

```bash
codecompass sync
codecompass sync turndown
codecompass sync --yes
codecompass sync --budget 1.00
```

## `codecompass query vendors|vendor|symbol|skills`

**Status:** implemented (Phase 15).

Reads `context-graph.db` and renders the result as a Rich table by
default, or raw JSON with `--json`. If `context-graph.db` doesn't exist
yet (no whole-project `sync`/bare `codecompass` run yet), each subcommand
prints a one-line note pointing at `sync` rather than a traceback.

- `codecompass query vendors [--unused] [--json]` — every tracked
  vendor's ecosystem, installed version, usage status, and enrichment
  status. `--unused` filters to vendors with zero detected usage anywhere
  in the project (`graph.unused_vendors`).
- `codecompass query vendor <name> [--json]` — one vendor's full profile:
  its symbols, total usage count, documenting artifacts, routed Skills,
  and `depends_on` vendors (`graph.vendor_profile`). Errors if `<name>`
  isn't a known vendor in the graph.
- `codecompass query symbol <name> [--json]` — every symbol named
  `<name>`, across every vendor (symbol names aren't globally unique),
  each with its vendor, usage count, and documenting artifacts
  (`graph.symbol_profile`).
- `codecompass query skills [--unused-mentions] [--json]` — every
  Skill/`.mdc` rule under the project (not just codecompass's own), its
  origin, and what it mechanically mentions (`graph.skills_index`).
  `--unused-mentions` filters to ones mentioning no known vendor or
  source file.

```bash
codecompass query vendors
codecompass query vendors --unused --json
codecompass query vendor turndown
codecompass query symbol parse
codecompass query skills --unused-mentions
```

## `codecompass index`

**Status:** implemented (Phase 4, extended Phase 7).

Regenerates the routing table injected into the consuming project's root
`CLAUDE.md` (between `<!-- codecompass:start -->` / `<!-- codecompass:end
-->` markers), and the tool-level Skill (`.claude/skills/codecompass/
SKILL.md`, `decisions/0020`) — both from the current `vendor.toml` and
each vendor's already-synced `CLAUDE.md`. Reads persisted state rather
than re-running `sync`, so it stays cheap regardless of `sync`'s AI-gated
step. Idempotent: safe to run repeatedly. A vendor that hasn't been
synced yet shows `_not synced_` in the Version column rather than
erroring.

```bash
codecompass index
```

## `codecompass check [--strict] [--fix]`

**Status:** implemented (Phase 6; coverage-gap sections added Phase 15).

Staleness gate. Compares each vendor's recorded `**Installed version:**`
(from its already-synced `CLAUDE.md`) against the ecosystem adapter's live
read of the currently installed version. Severity-aware
(`decisions/0005`): patch delta is silent (`NONE`), minor delta warns
without failing, major delta — or an unparseable version on either side
(`UNKNOWN`) — is the hard-fail case. Makes no AI calls itself; only
`--fix` can trigger generation cost, and only for the vendors it
actually regenerates.

- No flags — **report-only**. Prints a table (Vendor, Recorded, Live,
  Severity, Notes) and **always exits 0**, regardless of what it finds.
  For a human checking status locally.
- `--strict` — the CI gate. Same table, but exits non-zero if any vendor
  has `MAJOR`/`UNKNOWN` severity or a failed live-version read. Never
  regenerates anything.
- `--fix` — regenerates every vendor whose recorded version differs from
  its live version (including one that's never been synced at all) or
  shows transitive-dependency drift, via the same logic `sync` uses. One
  vendor's regeneration failure (a broken adapter read) doesn't block the
  rest; exits non-zero if anything failed, 0 otherwise.
- `--strict` and `--fix` are mutually exclusive — gating and regenerating
  are different jobs. Passing both errors immediately, before doing
  anything.
- Where practical, distinguishes the vendor's own version bump from a
  transitive-only (DEPTREE) bump — the latter shows as "transitive drift"
  in the Notes column but never affects `--strict`'s exit code, since it's
  lower risk than the vendor itself moving.
- **Coverage-gap sections** (Phase 15), report-only and always alongside
  the staleness table if `context-graph.db` exists (a one-line note
  instead if it doesn't): "Unused vendors" (`graph.unused_vendors`),
  "Documented but unused" / "Used but undocumented"
  (`graph.documented_but_unused`/`used_but_undocumented`), and
  "Third-party skill mentions with no backing vendor/symbol" (Skills/
  `.mdc` rules not authored by codecompass that mention no known vendor
  or source file). **None of these affect `--strict`'s exit code** — it
  stays scoped to version-drift severity alone, confirmed during this
  rework's planning interview.

```bash
codecompass check
codecompass check --strict
codecompass check --fix
```

## `codecompass chat <name>`

**Status:** implemented (Phase 8, `decisions/0023`). Explicit single-vendor
mode only — bare `codecompass chat` with no vendor name (project-root
routing across vendor-specific, multi-vendor, and whole-project questions)
is Phase 9, not yet implemented.

Lightweight terminal REPL, distinct from running Claude Code directly in a
vendor folder. Grounds every answer on the named vendor's already-persisted
digest files (`vendor/<name>/CLAUDE.md`, plus `OVERVIEW.md` if a grounded
description exists) — it never calls `sync` itself, so starting a chat
session never re-clones or re-generates anything. Calls the Anthropic API
directly (Haiku) with plain multi-turn text completion — no tool-use/
file-exploration loop, so it's faster and cheaper per query but strictly
narrower (only knows what's in the digest, not the full pinned source).
This tradeoff is stated in the REPL's startup banner.

Works whether or not the vendor has been AI-enriched yet: a vendor with no
`OVERVIEW.md` yet gets thinner grounding from `CLAUDE.md` alone, plus a
one-line hint to run `codecompass sync` (Phase B may pick the vendor up)
for deeper answers — not a hard block.

Type `exit`, `quit`, or press `Ctrl-D`/`Ctrl-C` to end the session.

```bash
codecompass chat turndown
```
