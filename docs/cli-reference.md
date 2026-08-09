# CLI reference

> This document describes the **planned** CLI surface. As of Phase 0, no
> commands are implemented yet — see [`planning/`](../planning/) for
> current phase status. Each command below is tagged with the roadmap
> phase that's expected to implement it.

## `depcompass init [--scan <manifest files>]`

**Status:** not yet implemented (planned for Phase 4, refined in Phase 10)

Bulk-discovers dependencies from the given manifest files (e.g.
`package.json`, `pyproject.toml`, `Cargo.toml`) and writes a draft
`vendor.toml` with every discovered dependency defaulted to
`depth = surface`. Free to run — surface generation has no AI cost — so
this is safe to run immediately against a large existing dependency list
without a cost conversation first.

```bash
depcompass init --scan package.json pyproject.toml Cargo.toml
```

## `depcompass sync [<vendor>]`

**Status:** not yet implemented (deterministic path planned for Phase 4;
AI-gated gap analysis added in Phase 5)

Regenerates digests and trees. With no argument, syncs every vendor in
`vendor.toml`; with a vendor name, syncs just that one.

- Deterministic output (`FILETREE.md`, `DEPTREE.md`, JSON sidecars, the
  per-vendor `CLAUDE.md` metadata/API-surface sections) is always
  regenerated, regardless of `depth`, and makes no AI calls.
- Gap analysis (only for `depth = full` vendors with `context_path` set)
  is the one step that calls the Anthropic API (Haiku). See
  `--budget` below for cost control when many vendors are promoted to
  `full` at once.

```bash
depcompass sync
depcompass sync turndown
depcompass sync --budget 1.00
```

## `depcompass index`

**Status:** not yet implemented (planned for Phase 4)

Regenerates the routing table injected into the consuming project's root
`CLAUDE.md` (between `<!-- depcompass:start -->` / `<!-- depcompass:end
-->` markers) from the current `vendor.toml` and the latest `sync` output,
without re-running `sync` itself. Idempotent: safe to run repeatedly.

> The exact boundary between what `sync` regenerates automatically and
> what requires an explicit `index` call is still being refined — see
> `planning/phase-4-*.md` once that phase's plan is written.

```bash
depcompass index
```

## `depcompass check [--strict] [--fix]`

**Status:** not yet implemented (planned for Phase 6)

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

**Status:** not yet implemented (single-vendor mode planned for Phase 7;
project-root routing mode planned for Phase 8)

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
