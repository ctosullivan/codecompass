# CLI reference

> `init`, `sync`, `index`, `check`, and `promote` are fully implemented
> (Phases 4-7). `chat` remains a stub — it prints a "not yet implemented"
> message and exits non-zero. The MVP spans phases 0-8
> (`decisions/0022`) — see [`planning/`](../planning/) for current phase
> status.

## `depcompass` (no subcommand)

**Status:** implemented (Phase 7, `decisions/0017`).

Zero-question bootstrap. Auto-discovers manifests at the project root
(`package.json`, `pyproject.toml`, `requirements.txt`, `Cargo.toml`),
writes every discovered dependency into `vendor.toml` at `depth =
surface`, regenerates `FILETREE.md`/`DEPTREE.md`/`CLAUDE.md` for any
newly-discovered vendor, refreshes the root `CLAUDE.md` routing table,
and writes the tool-level Skill (`decisions/0020`). No prompts, no AI
calls, regardless of project size.

- If `vendor.toml` doesn't exist yet, this is equivalent to `init --scan`
  against every manifest found at the project root.
- If `vendor.toml` already exists, this is an **idempotent refresh**:
  newly-discovered dependencies are appended at `depth = surface`;
  already-tracked vendors — including any at `depth = full` — are left
  completely untouched (their generated output is not regenerated), so
  this command never pays AI cost no matter how many times it's run.
- No manifests found is not an error — it produces (or leaves) an empty
  `vendor.toml`.

```bash
depcompass
```

## `depcompass init --scan <manifest file> [--scan <manifest file> ...] [--output <path>]`

**Status:** implemented (Phase 4). The explicit, scripted/CI-friendly
synonym for bare `depcompass`'s auto-discovery (`decisions/0017`) —
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
  the target path — unlike bare `depcompass`, this keeps a strict
  contract for scripted use.
- `[project.optional-dependencies]` in `pyproject.toml` is not scanned —
  only `[project.dependencies]`.

```bash
depcompass init --scan package.json --scan pyproject.toml --scan Cargo.toml
```

## `depcompass sync [<vendor>] [--budget <amount>]`

**Status:** fully implemented (Phases 4, 7).

Regenerates digests and trees. With no argument, syncs every vendor in
`vendor.toml`; with a vendor name, syncs just that one (errors clearly if
the name isn't found).

- Deterministic output — `FILETREE.md` (including the flat symbol index,
  appended as its own section), `DEPTREE.md`, `filetree.json`,
  `deptree.json`, and the per-vendor `CLAUDE.md` (Metadata, Grounding,
  API surface, Description, Known gotchas, Quick links) — is always
  regenerated under `vendor/<name>/`, regardless of `depth`, and makes no
  AI calls.
- `depth = full` vendors additionally get: a `vendor/<name>/src/`
  snapshot cloned from the vendor's own upstream repository
  (`decisions/0021` — falls back to a local-install-sourced copy if
  source resolution fails), and an AI-generated grounded description
  (`decisions/0019`) — the one step that calls the Anthropic API
  (`claude-haiku-4-5-20251001`). **Neither is cached** — every `sync` run
  re-clones and re-purchases the description for every `depth = full`
  vendor, so cost scales with how often you run `sync`, not just with how
  many vendors are `full`. A successful call also writes
  `vendor/<name>/OVERVIEW.md` (a conversational overview, for the future
  Chat REPL). A failure (source resolution, or the API call itself)
  doesn't block the rest of `sync`: that vendor still gets its
  deterministic output, with an explicit "unavailable" note in
  `CLAUDE.md`, and `sync` exits non-zero at the end.
- `--budget <amount>` caps estimated generation spend (USD) for this
  run, checked *before any API call is made*. If the estimate (a rough,
  fixed placeholder per vendor, not live-queried Anthropic pricing)
  exceeds `--budget`, the whole run aborts and **nothing is written**,
  not even other vendors' free deterministic output. Omit `--budget` for
  no cap.
- `sync` never escalates a vendor's depth — it only regenerates content
  at whatever depth `vendor.toml` already says. Use `promote` to move a
  vendor from `surface` to `full`.

```bash
depcompass sync
depcompass sync turndown
depcompass sync --budget 1.00
```

## `depcompass promote <vendor> [--yes]`

**Status:** implemented (Phase 7, `decisions/0018`).

Escalates one vendor to `depth = full` — the only command in depcompass
that costs money or asks anything (`decisions/0018`). Prints an estimated
cost disclosure and asks for confirmation before doing anything
AI-assisted (`--yes` skips the prompt, for scripted use). On
confirmation: sets `depth = full` in `vendor.toml`, resolves and clones
the vendor's upstream repository (`decisions/0021`), generates a grounded
description (`decisions/0019`), generates that vendor's per-vendor Skill
and Cursor `.mdc` export (`decisions/0013`), and refreshes the root
routing table and tool-level Skill so the change is visible immediately.

- Safe to re-run on an already-`full` vendor — it regenerates in place
  (same disclosure, same confirmation) rather than erroring.
- If source resolution fails (most commonly: a PyPI package with no
  recognized repository URL in its published metadata), `promote` fails
  loudly for that vendor rather than falling back to a source tarball —
  the vendor's `depth` is still set to `full` in `vendor.toml`, but its
  description is marked unavailable; re-running `promote` (or `sync`)
  later will try again.
- Batch promotion isn't supported — one vendor per invocation, by design
  (`decisions/0018`).

```bash
depcompass promote turndown
depcompass promote turndown --yes
```

## `depcompass index`

**Status:** implemented (Phase 4, extended Phase 7).

Regenerates the routing table injected into the consuming project's root
`CLAUDE.md` (between `<!-- depcompass:start -->` / `<!-- depcompass:end
-->` markers), and the tool-level Skill (`.claude/skills/depcompass/
SKILL.md`, `decisions/0020`) — both from the current `vendor.toml` and
each vendor's already-synced `CLAUDE.md`. Reads persisted state rather
than re-running `sync`, so it stays cheap regardless of `sync`'s AI-gated
step. Idempotent: safe to run repeatedly. A vendor that hasn't been
synced yet shows `_not synced_` in the Version column rather than
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
  shows transitive-dependency drift, via the same logic `sync` uses —
  including a fresh grounded-description call for `depth = full` vendors,
  so this is not free for those. One vendor's regeneration failure (a
  broken adapter read) doesn't block the rest; exits non-zero if anything
  failed, 0 otherwise.
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

**Status:** stub. Single-vendor mode planned for Phase 8; project-root
routing mode planned for Phase 9.

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
