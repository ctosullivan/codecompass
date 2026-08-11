# CLI reference

> `init`, `sync`, `index`, and `check` are fully implemented as of Phase 6.
> `promote` (Phase 7, planned) and `chat` (Phase 8, not started) are not
> yet implemented — `chat` remains a stub: it prints a "not yet
> implemented" message and exits non-zero. The MVP now spans phases 0-8,
> not just 0-6 (`decisions/0022`) — see [`planning/`](../planning/) for
> current phase status.

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

## `depcompass sync [<vendor>] [--budget <amount>]`

**Status:** fully implemented (Phases 4-5).

Regenerates digests and trees. With no argument, syncs every vendor in
`vendor.toml`; with a vendor name, syncs just that one (errors clearly if
the name isn't found).

- Deterministic output — `FILETREE.md` (including the flat symbol index,
  appended as its own section), `DEPTREE.md`, `filetree.json`,
  `deptree.json`, and the per-vendor `CLAUDE.md` (Metadata, Grounding,
  API surface, Gap analysis, Known gotchas, Quick links) — is always
  regenerated under `vendor/<name>/`, regardless of `depth`, and makes no
  AI calls. `depth = full` vendors additionally get a pinned
  `vendor/<name>/src/` snapshot copy.
- Gap analysis (only for `depth = full` vendors with `context_path` set)
  is the one step that calls the Anthropic API (`claude-haiku-4-5-20251001`).
  **It is not cached** — every `sync` run re-purchases it for every
  qualifying vendor, so cost scales with how often you run `sync`, not
  just with how many vendors are `full`. A successful call also writes
  `vendor/<name>/OVERVIEW.md` (a conversational overview, for the future
  Chat REPL). A failed call (network/auth/rate-limit error, unreadable
  `context_path`) doesn't block the rest of `sync`: that vendor still
  gets its deterministic output, with an explicit "unavailable" note in
  `CLAUDE.md`, and `sync` exits non-zero at the end.
- `--budget <amount>` caps estimated gap-analysis spend (USD) for this
  run, checked *before any API call is made*. If the estimate (a rough,
  fixed placeholder per vendor, not live-queried Anthropic pricing)
  exceeds `--budget`, the whole run aborts and **nothing is written**,
  not even other vendors' free deterministic output. Omit `--budget` for
  no cap.

```bash
depcompass sync
depcompass sync turndown
depcompass sync --budget 1.00
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

**Status:** implemented (Phase 6).

Staleness gate. Compares each vendor's recorded `**Installed version:**`
(from its already-synced `CLAUDE.md`) against the ecosystem adapter's live
read of the currently installed version. Severity-aware
(`decisions/0005`): patch delta is silent (`NONE`), minor delta warns
without failing, major delta — or an unparseable version on either side
(`UNKNOWN`) — is the hard-fail case. Makes no AI calls itself; only
`--fix` can trigger gap-analysis cost, and only for the vendors it
actually regenerates.

- No flags — **report-only**. Prints a table (Vendor, Recorded, Live,
  Severity, Notes) and **always exits 0**, regardless of what it finds.
  For a human checking status locally.
- `--strict` — the CI gate. Same table, but exits non-zero if any vendor
  has `MAJOR`/`UNKNOWN` severity or a failed live-version read. Never
  regenerates anything.
- `--fix` — regenerates every vendor whose recorded version differs from
  its live version (including one that's never been synced at all) or
  shows transitive-dependency drift, via the same logic `sync` uses —
  including a fresh gap-analysis call for `depth = full` vendors, so this
  is not free for those. One vendor's regeneration failure (a broken
  adapter read) doesn't block the rest; exits non-zero if anything failed,
  0 otherwise.
- `--strict` and `--fix` are mutually exclusive — gating and regenerating
  are different jobs. Passing both errors immediately, before doing
  anything.
- Where practical, distinguishes the vendor's own version bump from a
  transitive-only (DEPTREE) bump — the latter shows as "transitive drift"
  in the Notes column but never affects `--strict`'s exit code, since it's
  lower risk than the vendor itself moving.

```bash
depcompass check
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
