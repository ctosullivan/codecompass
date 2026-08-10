# CLI reference

> `init`, `sync`, and `index` are implemented as of Phase 4. `check` and
> `chat` remain stubs: each prints a "not yet implemented" message naming
> its planned phase and exits non-zero — see [`planning/`](../planning/)
> for current phase status.

## `depcompass init --scan <manifest file> [--scan <manifest file> ...] [--output <path>]`

**Status:** implemented (Phase 4). Refined in Phase 10.

Bulk-discovers dependencies from the given manifest files (`package.json`,
`pyproject.toml`, `Cargo.toml` — dispatched by filename) and writes a
draft `vendor.toml` with every discovered dependency defaulted to
`depth = surface`. Free to run — surface generation has no AI cost — so
this is safe to run immediately against a large existing dependency list
without a cost conversation first.

- `--scan` is repeatable, one manifest file per flag (not space-separated
  after a single flag — that's not how a named Click/Typer option works).
- `--output` (default `vendor.toml`) is where the draft is written.
- Errors, rather than overwriting, if a `vendor.toml` already exists at
  the target path — this is a bootstrap command, not a merge tool yet.
- `[project.optional-dependencies]` in `pyproject.toml` is not scanned —
  only `[project.dependencies]`.

```bash
depcompass init --scan package.json --scan pyproject.toml --scan Cargo.toml
```

## `depcompass sync [<vendor>]`

**Status:** deterministic path implemented (Phase 4); `--budget` and
AI-gated gap analysis are **not yet implemented** (Phase 5).

Regenerates digests and trees. With no argument, syncs every vendor in
`vendor.toml`; with a vendor name, syncs just that one (errors clearly if
the name isn't found).

- Deterministic output — `FILETREE.md` (including the flat symbol index,
  appended as its own section), `DEPTREE.md`, `filetree.json`,
  `deptree.json`, and the per-vendor `CLAUDE.md` (Metadata, Grounding,
  API surface, Known gotchas, Quick links — Gap analysis section omitted
  until Phase 5) — is always regenerated under `vendor/<name>/`,
  regardless of `depth`, and makes no AI calls. `depth = full` vendors
  additionally get a pinned `vendor/<name>/src/` snapshot copy.
- Gap analysis (only for `depth = full` vendors with `context_path` set)
  will be the one step that calls the Anthropic API (Haiku), once Phase 5
  lands. `--budget` (cost control for promoting many vendors to `full` at
  once) is a Phase 5-only flag, not yet added to the CLI.

```bash
depcompass sync
depcompass sync turndown
```

## `depcompass index`

**Status:** implemented (Phase 4).

Regenerates the routing table injected into the consuming project's root
`CLAUDE.md` (between `<!-- depcompass:start -->` / `<!-- depcompass:end
-->` markers) from the current `vendor.toml` and each vendor's
already-synced `CLAUDE.md` — it reads persisted state rather than
re-running `sync`, so it stays cheap even once Phase 5 gives `sync` an
AI-gated step. Idempotent: safe to run repeatedly. A vendor that hasn't
been synced yet shows `_not synced_` in the Version column rather than
erroring.

```bash
depcompass index
```

## `depcompass check [--strict] [--fix]`

**Status:** stub. Real logic planned for Phase 6.

Staleness gate. Compares each vendor's recorded "last verified against
installed version" against the ecosystem adapter's live read of the
currently installed version. Severity-aware: patch delta is silent, minor
delta warns, major delta hard-fails.

- `--strict` — pure gate, does not regenerate anything; exits non-zero on
  any major-version staleness. Intended for CI.
- `--fix` — regenerates stale digests in place; exits 0 on success.
  Intended for a scheduled maintenance job; batches all stale vendors into
  one PR rather than one PR per bump.

```bash
depcompass check --strict
depcompass check --fix
```

## `depcompass chat [<name>]`

**Status:** stub. Single-vendor mode planned for Phase 7; project-root
routing mode planned for Phase 8.

Lightweight terminal REPL, distinct from running Claude Code directly in a
vendor folder. Loads only digest files as system context and calls the
Anthropic API directly (Haiku) — no tool-use/file-exploration loop, so
it's faster and cheaper per query but strictly narrower (only knows what's
in the digest, not the full pinned source). This tradeoff is stated in the
REPL's startup banner.

- With a vendor name: loads only that vendor's digest.
- Without a name: two-tier routing across vendor-specific, multi-vendor,
  and whole-project questions — see `architecture/overview.md`'s Chat REPL
  section for the full routing design.

```bash
depcompass chat
depcompass chat turndown
```
