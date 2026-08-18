# Project context

This file reflects the *current* state of the project — overwritten at
each stopping point, not appended to. See `CHANGELOG.md` and git history
for the log of how it got here.

## Current phase

**Phase 10: SQLite graph foundation — planned, not yet implemented.** All
eight v0.1 MVP phases (0-8) remain `done` (`decisions/0022`); Phase 9
(rename) is `done`. MVP (v0.2) (`decisions/0030`, phases 9-19) had its
phase order corrected this session — see "Decisions made this session"
below — before Phase 10's plan file was written.

## What was just completed

Implemented `planning/phase-9-rename-to-codecompass.md` in full —
mechanical rename, zero behavior change, exactly as scoped:

- `git mv src/depcompass src/codecompass` (blame preserved) and
  `git mv .claude/skills/depcompass .claude/skills/codecompass`; every
  internal import and literal `"depcompass"` string across all ~15
  modules replaced with `"codecompass"`.
- `pyproject.toml`: package name and console script (`codecompass =
  "codecompass.cli:app"`).
- Root `CLAUDE.md`: the routing-table marker
  (`<!-- codecompass:start/end -->`) **and** its opening sentence — both
  presented as a diff and explicitly approved by the user before being
  written, per `CLAUDE.md` §0 (the plan's literal scope only covered the
  marker; the opening-sentence change was flagged as slightly beyond that
  scope but approved anyway to avoid leaving the file's first line stale).
- `README.md`, `CONTRIBUTING.md`, `docs/cli-reference.md`,
  `docs/config-schema.md`, `architecture/overview.md`, `.gitignore`'s
  comment, `tests/README.md`, and every test file's imports/assertions —
  all swept.
- `decisions/*.md` (all 29 files) and `CHANGELOG.md`'s pre-Phase-9
  entries — deliberately **not** touched, exactly per the plan's
  Explicitly-deferred list; `planning/phase-0` through `phase-8` and
  `planning/ROADMAP.md`/`CONTEXT.md`'s own historical prose were also left
  alone (not in the plan's explicit Files list — they're the project's
  historical record of what was true when built, same treatment as
  `decisions/`/`CHANGELOG.md`).
- Stale gitignored build artifacts cleaned up: `src/depcompass.egg-info/`
  removed, `__pycache__` dirs cleared; fresh `pip install -e ".[dev]"`
  confirmed `codecompass` resolves as the console script.

**Verification, all green:**
- `pytest` — 218 passed, 1 skipped (pre-existing, unrelated).
- `ruff check .` — clean.
- `codecompass --help` lists the same six commands (`init`, `sync`,
  `index`, `promote`, `check`, `chat`) as before, under the new name.
- Bare `codecompass` (idempotent — 4 already-tracked vendors, 0 newly
  discovered, correctly touched nothing) followed by `codecompass sync`
  (whole-project) against this repo itself: regenerated `vendor/` for all
  four vendors, confirmed `CLAUDE.md`'s marker and
  `.claude/skills/codecompass/SKILL.md` both render correctly under the
  new name.
- Final sweep: `grep -rn "depcompass" src/ tests/ pyproject.toml
  README.md CONTRIBUTING.md docs/ architecture/` — zero hits.

**Last session's file-loss incident (see prior `CONTEXT.md` revision,
now resolved and no longer tracked here) is fully closed**: `vendor.toml`
and `.claude/skills/*/SKILL.md` were restored via `git restore` before
this phase began; `vendor/` and the tool-level Skill have now been freshly
regenerated as part of this phase's own verification, under the new name.
The one piece that isn't back — `rich`'s promoted (`depth = full`) state
and its per-vendor Skill/`.mdc` — was never committed and remains
un-regenerated; re-run `codecompass promote rich` if that validation is
wanted again (real API cost).

## Decisions made this session not already captured in an ADR

**One real correction, recorded in `planning/ROADMAP.md`'s own
renumbering-note convention rather than a new ADR (bookkeeping, not a
design reversal — same precedent as every prior renumbering note in that
file):** the original phase order placed "Retire `Depth`" second (Phase
10), before anything existed to replace its role. `Depth` is read by
eight call sites across `sync.py`, `grounded_description.py`, `cli.py`,
`index.py`, `skill.py`, `claude_md.py`, `chat.py`, and `discovery.py` —
removing it that early would either break all eight or force Phase 10 to
prematurely absorb most of the graph/cloning/enrichment/CLI-rewire work.
Corrected: "Retire `Depth`" moves to **Phase 16** (after phases 13-15
replace every one of those call sites); the graph/usage-detection/
mapping/cloning/enrichment/CLI phases shift from 11-16 down to **10-15**.
Phases 17-19 unaffected. `decisions/0031`-`0034` (already written, before
this correction) each contain a few internal "Phase N" citations keyed to
the *old* numbering — not editable (append-only) — `planning/ROADMAP.md`'s
renumbering note has the explicit old→new translation table for anyone
cross-referencing them.

## Next concrete step

Implement `planning/phase-10-sqlite-graph-foundation.md` (just written
this session) — the new `graph.py` module: SQLite schema, `init_schema`,
`rebuild_deterministic`, and read-only query functions, per
`decisions/0032`. Library-only in this phase, deliberately not wired into
any CLI command yet (that's Phase 15). After Phase 10, write
`planning/phase-11-project-source-usage-detection.md` next, per the
corrected phase order above.

**Still outstanding, not a blocker but worth remembering** (carried
forward, still applicable):
- Once a Rust toolchain is available anywhere in the pipeline,
  `decisions/0014` requires validating the Cargo adapter's fixture
  assumptions (including `repository_url()`) and regex-based `pub`
  extraction against real `cargo metadata` output and a real crate —
  currently entirely unverified. Relevant to Phase 13's universal cloning
  (every vendor gets cloned, including Cargo ones).
- `extract_npm_symbols` (Phase 3) is untested against real-world `.d.ts`
  authoring styles beyond hand-written fixtures.
- `grounded_description.py` (soon retired/replaced by `enrichment.py`,
  Phase 14) and `chat.py` (Phase 8) have never been run against the real
  Anthropic API in this environment — a human must do this manually at
  least once, now specifically against Phase 14's *batched* call shape,
  before trusting output quality (`decisions/0016`).
- `staleness.py`'s custom version parser (Phase 6) has no real PEP 440 or
  full-semver correctness — flag if it misclassifies a real-world version
  string once used against real projects.
- A formal trigger-accuracy evaluation harness for per-vendor Skills
  (`decisions/0013`'s Consequences) remains outstanding.
- Cursor `.mdc` export has no `globs` field (description-based relevance
  only) — glob scoping to wherever a vendor is actually imported in the
  consuming codebase is a documented future refinement, not implemented.
- `chat` has no conversation-length capping, no streaming, and no
  cumulative-cost display — all explicitly deferred in
  `planning/phase-8-chat-repl.md`, now lower priority given
  `decisions/0034`'s demotion, revisit only if real usage shows a need.
- Whether/when to cut the `v0.1` tag remains a separate, not-yet-made
  decision (`decisions/0022`). `v0.2`'s own tag is not before Phase 19 is
  `done` (`decisions/0030`).
- Background research/planning subagents spawned via the `Agent` tool
  retain `Bash` access even under explicit read-only instructions, which
  caused real (though fully recovered) file loss in the previous session
  — see git history's prior `CONTEXT.md` revision for the full incident
  writeup. Consider `isolation: "worktree"` for any future
  research/planning subagent spawned against this repo.
- `rich`'s `depth = full` promotion (and its per-vendor Skill/`.mdc`) was
  lost in that incident and never regenerated — harmless for Phase 9/10's
  purposes (no test depends on it), but note it if a future session
  expects `.claude/skills/codecompass-rich/` to already exist.
