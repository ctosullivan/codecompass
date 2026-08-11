# 0017. Zero-question deterministic bootstrap

## Status

Accepted

## Context

Today, `init` requires `--scan <file>` repeated once per manifest file
(`--scan package.json --scan pyproject.toml`) — there is no filesystem
auto-discovery, and bare `depcompass` (no subcommand) exits with code 2
("Missing command") rather than doing anything. A first-time user must
already know which manifest files exist in their project and name each
one explicitly before getting any output at all, even though `SURFACE`
generation has no AI cost and nothing about it requires that knowledge
in advance.

`architecture/overview.md`'s "Retrofitting to existing projects" section
already states the reactive-promotion principle: promotion to `FULL`
happens "selectively and reactively later," not as a batch decision at
setup time. This decision extends that same principle one step earlier —
setup itself should require no decisions, not just no *AI* decisions.

## Decision

1. Bare `depcompass` (no subcommand) auto-discovers manifests across all
   three ecosystems by walking the project root for known filenames
   (`package.json` for npm; `pyproject.toml`/`requirements.txt` for
   Python; `Cargo.toml` for Cargo), writes every discovered dependency
   into `vendor.toml` at `depth = SURFACE`, generates the deterministic
   tree files (`FILETREE.md`, `DEPTREE.md`), and updates the root
   `CLAUDE.md` routing table. No prompts, no AI calls.
2. Running it again on an already-bootstrapped project (`vendor.toml`
   already exists) is an idempotent refresh: newly discovered
   dependencies are appended at `SURFACE`; existing entries — including
   any already promoted to `FULL` via `depcompass promote`
   (`decisions/0018`) — are left untouched; trees and the routing table
   are regenerated. It does not error.
3. `init --scan <file>` (repeated flag) remains, unchanged, as the
   explicit, scripted/CI-friendly synonym for naming specific manifest
   files. It keeps its current stricter contract — it still errors if
   `vendor.toml` already exists — since that strictness is what makes it
   suitable for scripted use in the first place.
4. `sync` and `index` remain independently invokable for maintenance,
   unchanged.

## Alternatives considered

- **Interactive prompting at bootstrap** (e.g. confirming discovered
  ecosystems before writing `vendor.toml`). Rejected — directly
  contradicts the goal of asking nothing; a user who wants control
  already has `--scan`.
- **Auto-discovery as an opt-in flag** (e.g. `--auto`) rather than the
  bare-command default. Rejected — this preserves the exact adoption
  barrier being removed: a first-time user must already know the flag
  exists. Making auto-discovery the default for bare invocation is the
  point.
- **Treat bare `depcompass` on an already-bootstrapped project as an
  error**, forcing explicit `sync`/`index` for maintenance instead of an
  idempotent refresh. Rejected — reintroduces the "re-ask of settled
  questions" friction this decision exists to remove; a five-dependency
  repo and a five-hundred-dependency monorepo should differ only in
  wall-clock time, not in decisions asked of the user on a re-run.

## Consequences

- `discovery.py` gains new filesystem-walking logic to locate manifest
  files, in addition to its existing parsers (`discover_npm`,
  `discover_python`, `discover_cargo`, `discover_all`), which currently
  only operate on `Path` objects supplied explicitly by the caller.
- `vendor.toml` writing splits into two modes: "create fresh" (current
  behavior, still used by `--scan` against a project with no
  `vendor.toml`) and "diff and merge" (new, used by bare-invocation
  refresh) — existing entries' `depth` and any vendor-specific fields are
  authoritative and are never overwritten by a refresh; only newly
  discovered dependencies are appended.
- `docs/cli-reference.md` and `README.md`'s "Quick example" need
  rewriting to lead with bare `depcompass` rather than `init --scan`.
- `--scan`'s existing error-if-`vendor.toml`-exists behavior is preserved
  unchanged, so scripted/CI usage already depending on that strictness
  is not silently affected by this change.
