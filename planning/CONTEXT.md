# Project context

This file reflects the *current* state of the project — overwritten at
each stopping point, not appended to. See `CHANGELOG.md` and git history
for the log of how it got here.

## Current phase

**Phase 9: Rename to codecompass — planned, not yet implemented.** All
eight v0.1 MVP phases (0-8) remain `done` (`decisions/0022`). This session
replanned the entire post-MVP roadmap from scratch into a new MVP (v0.2)
milestone (`decisions/0030`, phases 9-19) per explicit user request — the
previously-planned context-graph phases (9a-9e, `decisions/0024`-`0028`)
are superseded, not implemented, and not deleted (see
`planning/ROADMAP.md`'s "Superseded planning" note).

## What was just completed

Interviewed the user and fully replanned the post-MVP roadmap as a new
MVP (v0.2), then wrote the first phase's implementation-ready plan file
plus six foundational ADRs — no implementation code was written this
session, per `CLAUDE.md` §1.

**The new MVP (v0.2) scope** (`planning/ROADMAP.md`, phases 9-19):
1. Rename `depcompass` → `codecompass` (PyPI name confirmed available).
2. Retire the `Depth` enum/`vendor.toml` field — AI enrichment becomes
   automatic and usage-driven (a symbol only gets enriched once the
   project's own source is proven to reference it), not a manual
   per-vendor human toggle.
3. Retire `promote` entirely — source cloning happens for every vendor by
   default (free), and a batched, usage-scoped enrichment pass
   auto-triggers right after, still cost-disclosed and
   confirm/`--yes`/`--budget`-gated like `promote` was.
4. Replace the never-built JSON context-graph design with a SQLite
   database (`context-graph.db`, gitignored, deterministically rebuilt),
   recording vendors, symbols, source files, docs, and **every** skill
   under `.claude/skills/` (not just codecompass-generated ones) plus
   their interrelationships — queryable via a new `codecompass query`
   command.
5. A new `/discovery` Claude Code slash command (generated artifact,
   `.claude/commands/discovery.md`) — read-only guided exploration,
   explicitly forbidden from writing a plan or touching any file.
6. A new `undo` command — removes everything codecompass generated,
   driven by the graph's origin-tagged artifacts, confirm-gated, does not
   auto-commit the removal.
7. Chat (`chat <vendor>`) demoted from "the actual product"
   (`decisions/0012`) to a secondary, code-unchanged subcommand — the
   graph + generated Skills + `/discovery` become primary.
8. `check --strict` stays scoped to version-drift only (confirmed via
   interview) — new graph-derived coverage gaps are report-only.
9. The enrichment cache survives a fresh clone via a hash line in each
   vendor's *committed* `CLAUDE.md`, since `context-graph.db` itself is
   gitignored (confirmed via interview — DB not committed).

**Wrote this session:**
- `planning/phase-9-rename-to-codecompass.md` — mechanical rename only,
  zero behavior change, ~180 code references touched. Explicitly excludes
  editing `decisions/*.md` (append-only) and the repo/folder name (stays
  "Devcompass" — deliberate).
- Six new ADRs: `decisions/0029` (rename announcement), `decisions/0030`
  (MVP redefined — v0.2 spans phases 9-19, supersedes nothing directly but
  extends `decisions/0022`'s milestone-grouping precedent), `decisions/0031`
  (`Depth` retired, supersedes `decisions/0001`), `decisions/0032`
  (SQLite replaces JSON, supersedes `decisions/0024`), `decisions/0033`
  (`promote` retired, supersedes `decisions/0018` and partially `0017`;
  carries forward `decisions/0021`'s fail-loud rule under a new trigger),
  `decisions/0034` (chat demoted, supersedes `decisions/0012`).
- Restructured `planning/ROADMAP.md`: new "MVP (v0.2) — phases 9-19"
  table; former Post-MVP phases 9a-9e marked superseded and their plan
  files deleted (recoverable from git history at/before commit `a9969e4`
  if needed — their design is still the source Phase 11-13 port from,
  read from history rather than redesigned from scratch); their five ADRs
  (`decisions/0024`-`0028`) are kept, append-only; former
  routing/rollup/polish/MCP phases renumbered 10→20, 11→21, 12→22.
- `CHANGELOG.md`'s `[Unreleased]` gained a new `### Added` entry
  summarizing this session (the prior Phase-9-context-graph entry is left
  as-is, per Keep a Changelog convention — historical entries aren't
  rewritten).

**Only one of MVP (v0.2)'s eleven phases (9-19) has a full
implementation-ready plan file yet** — Phase 9 itself. Phases 10-19
exist only as `planning/ROADMAP.md` rows with a one-line scope each; each
needs its own `planning/phase-N-<name>.md` written (per `CLAUDE.md` §1)
immediately before it starts, the same way every prior phase in this
project has been planned incrementally rather than all at once — Phase 9
was written in full detail now because it's next; the 4-sub-phase
context-graph plan file style (writing several phases fully in one pass)
was deliberately *not* repeated here since this rework's phases are more
loosely coupled than 9a-9d's were.

## Decisions made this session not already captured in an ADR

- None outstanding. `CLAUDE.md` §6's illustrative parenthetical ("the MVP
  (phases 0-8) is one milestone") was updated to acknowledge the new MVP
  (v0.2) group, per `decisions/0030` — the diff was presented to the user,
  approved, and applied this session (along with the mirrored
  `CONTRIBUTING.md` text). Every other real design decision from this
  session (rename, MVP regrouping, Depth retirement, SQLite storage,
  promote retirement, chat demotion) is captured in
  `decisions/0029`-`0034`.

## Incident this session: unexplained deletion of generated/tracked files

Partway through this session, `vendor/` (gitignored, untracked — this
repo's own locally-generated digest output), `.claude/skills/
depcompass-rich/` and `.cursor/` (both untracked — local artifacts from
an earlier, never-committed `depcompass promote rich` run), and two
**tracked** files — `vendor.toml` and `.claude/skills/depcompass/
SKILL.md` — were found deleted from the working tree, and root
`CLAUDE.md` was found truncated (its trailing routing-table marker block
silently cut off, including a missing final newline — consistent with a
destructive overwrite, not a targeted edit). None of this was an action
taken directly in the main conversation thread.

**Likely cause, not confirmed:** several background research/planning
subagents were spawned earlier in this session with explicit read-only
instructions ("for planning purposes only — do not modify anything"), but
their tool access included `Bash` (only `Edit`/`Write`/`Agent`/`Artifact`/
`ExitPlanMode` were excluded) — a Bash-run command could still have
deleted files or overwritten `CLAUDE.md` despite the instruction. Raw
subagent transcripts were not inspected to confirm which one, if any, is
responsible (large JSONL files, not meant to be read directly). If this
recurs, consider running research/planning subagents with `isolation:
"worktree"` so they can't touch the primary working tree at all.

**Resolution applied this session:** the two tracked files were restored
via `git restore` (losing only trivial uncommitted local edits — `rich`'s
`vendor.toml` depth flipped to `full`, from the earlier unfinished
`promote` run); `CLAUDE.md`'s marker block was manually restored to match
the last commit. The untracked `vendor/`, `.claude/skills/
depcompass-rich/`, and `.cursor/` content is **not recoverable via git**
(never committed) — regenerate `vendor/` with a bare `depcompass`/
`codecompass` run, and regenerate `rich`'s promoted state (including
another real Haiku API call) by re-running `promote rich` once available,
or its Phase 14/15 successor after this rework lands. No committed
history or this session's own new planning files were affected.

## Next concrete step

Implement `planning/phase-9-rename-to-codecompass.md` — purely mechanical,
zero behavior change, full test suite must stay green. This unblocks
every later phase (10-19), which are all planned and reviewed against the
`codecompass` name from the start rather than threading the rename through
unrelated diffs later.

After Phase 9, write `planning/phase-10-retire-depth.md` next (per
`planning/ROADMAP.md`'s phase order — depth retirement is the data-model
shrink phases 11+ build on), following the same "write the phase plan
file, get any surfaced assumptions resolved, then implement" workflow
`CLAUDE.md` §1 requires for every phase.

**Still outstanding, not a blocker but worth remembering** (carried
forward from before this session, still applicable):
- Once a Rust toolchain is available anywhere in the pipeline,
  `decisions/0014` requires validating the Cargo adapter's fixture
  assumptions (including `repository_url()`) and regex-based `pub`
  extraction against real `cargo metadata` output and a real crate —
  currently entirely unverified. Now also relevant to Phase 14's
  universal cloning (every vendor gets cloned, including Cargo ones).
- `extract_npm_symbols` (Phase 3) is untested against real-world `.d.ts`
  authoring styles beyond hand-written fixtures.
- `grounded_description.py` (soon retired/replaced by `enrichment.py`,
  Phase 15) and `chat.py` (Phase 8) have never been run against the real
  Anthropic API in this environment — a human must do this manually at
  least once, now specifically against Phase 15's *batched* call shape,
  before trusting output quality (`decisions/0016`).
- `staleness.py`'s custom version parser (Phase 6) has no real PEP 440 or
  full-semver correctness — flag if it misclassifies a real-world version
  string once used against real projects.
- A formal trigger-accuracy evaluation harness for per-vendor Skills
  (`decisions/0013`'s Consequences) remains outstanding — nothing in this
  session's replanning closes it.
- Cursor `.mdc` export has no `globs` field (description-based relevance
  only) — glob scoping to wherever a vendor is actually imported in the
  consuming codebase is a documented future refinement, not implemented.
- `chat` has no conversation-length capping, no streaming, and no
  cumulative-cost display — all explicitly deferred in
  `planning/phase-8-chat-repl.md`, now lower priority given
  `decisions/0034`'s demotion, revisit only if real usage shows a need.
- Whether/when to cut the `v0.1` tag remains a separate, not-yet-made
  decision (`decisions/0022`), unaffected by this session's replanning.
  `v0.2`'s own tag is even further out — not before Phase 19 is `done`
  (`decisions/0030`).
- This repo's own working tree has pre-existing uncommitted local drift
  from an earlier manual `promote rich` run (`.claude/skills/
  depcompass/SKILL.md`, `CLAUDE.md`, `vendor.toml` modified;
  `.claude/skills/depcompass-rich/`, `.cursor/` untracked) — Phase 9's
  plan explicitly folds renaming these into its scope rather than leaving
  them stale under the old name; decide during Phase 9 implementation
  whether to commit them as part of the rename or handle separately.
