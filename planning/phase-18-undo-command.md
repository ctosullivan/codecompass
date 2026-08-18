# Phase 18: `undo` command

## Scope

**Covered:**
- `src/codecompass/cli.py` — new `undo(yes: bool = typer.Option(False,
  "--yes"), dry_run: bool = typer.Option(False, "--dry-run"))` command:
  1. **Enumerate everything to remove.** Two paths, depending on whether
     `context-graph.db` exists:
     - **Graph available** (the common case, once a whole-project sync
       has run): query `doc_artifacts` for every row with `origin`
       starting `codecompass_` (tool Skill, per-vendor Skills, Cursor
       `.mdc` files, `/discovery` — everything Phases 10-17 tagged),
       resolve each to a real path; query `vendors` for every tracked
       vendor's `vendor/<name>/` directory.
     - **No graph yet** (a project that's only run `init`/a single
       `sync <vendor>`): fall back to a pattern-based enumeration —
       `.claude/skills/codecompass/`, `.claude/skills/codecompass-*/`,
       `.cursor/rules/codecompass-*.mdc`, `.claude/commands/
       discovery.md` (glob-matched), plus every vendor directory listed
       in `vendor.toml` directly (no graph query needed for this part).
       Less precise than the graph-backed path (can't distinguish a
       hand-renamed third-party skill that happens to match the glob
       pattern, for instance) but functional without requiring a prior
       whole-project sync — explicitly noted as a known, accepted
       precision tradeoff for this fallback path only.
     - Always: `vendor.toml`, `context-graph.db` itself, and the root
       `CLAUDE.md` marker block (`<!-- codecompass:start -->` …
       `<!-- codecompass:end -->`) — the last one handled specially, see
       below.
  2. **Never touches anything with `origin='third_party'`** (or, in the
     fallback path, anything not matching the exact generated-name
     patterns above) — a hand-written or third-party Skill that happens
     to be indexed in the same graph is never a candidate for removal,
     confirmed explicitly by construction (the enumeration query/glob set
     never includes that origin/pattern at all, not a filter applied
     after the fact).
  3. **Print the full list before touching anything.** `--dry-run` stops
     here. Otherwise, prompt for confirmation via `typer.confirm` unless
     `--yes` (same pattern as the former `promote`/current Phase B
     confirmation).
  4. **Delete everything enumerated** except the root `CLAUDE.md` marker
     block — plain filesystem removal (`shutil.rmtree`/`Path.unlink`),
     no git interaction (`git rm`/`git add`) at all. **Does not commit**
     the resulting working-tree changes — committing the removal is left
     to the user, consistent with this project's existing practice of
     never auto-committing on the user's behalf (the same posture every
     other `codecompass` command already has — none of them touch git).
  5. **Root `CLAUDE.md`'s marker block removal goes through the same
     diff-presentation-and-approval flow every other root `CLAUDE.md`
     edit requires (`CLAUDE.md` §0)** — `undo` itself cannot silently
     strip it. In practice this means `undo`'s own implementation can
     compute the proposed diff (removing the marker block, same
     `re.sub`-based approach `index.py`'s `update_root_claude_md` already
     uses in reverse) and print it for the *human running `codecompass
     undo`* to review before it's applied — `undo` is a human-invoked CLI
     command, not an AI agent, so this isn't the same "present to the AI
     session's user for explicit approval" flow the rest of this
     project's `CLAUDE.md` §0 discipline governs (that's about *this
     project's own governance file* being edited by an AI session working
     *on* codecompass — a different, narrower thing than `codecompass`
     the tool editing *a consuming project's* `CLAUDE.md`). `undo`'s
     confirmation prompt (step 3) already covers this — no additional
     gate needed beyond what step 3 already provides, since the whole
     operation (including the marker-block removal) is disclosed and
     confirmed together as one action.
- Tests: `tests/test_undo.py` (new) — graph-backed enumeration against
  fixture state, fallback-path enumeration when no graph exists,
  `--dry-run` performs zero filesystem changes, `--yes` skips the prompt,
  third-party skills are never enumerated in either path, root `CLAUDE.md`
  marker-block removal is correct and leaves hand-written content around
  it untouched (mirroring `tests/test_index.py`'s existing coverage of
  `update_root_claude_md`'s insertion behavior, now exercised in
  reverse).

**Explicitly deferred / out of scope:**
- Any git interaction (`git rm`, `git status` reporting, staging) —
  deliberately out of scope; `undo` is a plain filesystem operation only.
- Undoing a partial/interrupted `undo` itself — not a transactional
  rollback (stated explicitly in `decisions/0033`... — actually see
  `decisions/0030`'s sibling framing; this phase's own ADR, if written,
  should state it plainly: best-effort cleanup, not atomic).
- A machine-readable `--json` output for `undo`'s enumeration — not
  requested; the human-readable list is sufficient for a confirm-before-
  delete flow.

## Design decisions

**A new ADR is warranted here** (`decisions/0035`, next sequential
number after whatever Phase 17 doesn't itself need — confirm the exact
next-available number at implementation time): "`undo` is a best-effort,
origin-tag-driven filesystem cleanup, not a transactional rollback,
and never commits on the user's behalf." Worth its own ADR rather than
folding into an existing one, since it's a genuinely new command with its
own non-obvious tradeoffs (the two-path enumeration strategy, the
git-interaction boundary) — matching this project's own rule ("write a
new ADR whenever a phase involves a non-obvious tradeoff").

**Why the fallback path exists at all** rather than requiring a graph:
`undo` should work even for a project that never got far enough to build
a full graph (e.g., someone ran `init --scan` once, didn't like the
result, and wants to clean up immediately) — refusing to function without
a graph would make `undo` useless in exactly the "I want to back out of
this" scenario it exists for.

## Files

- `src/codecompass/cli.py` — new `undo` command.
- `decisions/00XX-undo-is-best-effort-cleanup.md` (new — exact number
  TBD at implementation time).
- `tests/test_undo.py` (new).
- `docs/cli-reference.md` — `undo` documented, including the two-path
  enumeration behavior and the "never commits" guarantee.
  `architecture/overview.md` — new subsection. `planning/ROADMAP.md`,
  `planning/CONTEXT.md`, `CHANGELOG.md`.

## Verification

- `pytest` — full suite passes.
- `ruff check .` — clean.
- Manual round-trip, against a **scratch** project (not this repo):
  bootstrap it fully (including at least one enriched vendor, so
  per-vendor Skills/`.mdc` exist), run `codecompass undo --dry-run` and
  confirm the printed list matches exactly what was generated, then run
  `codecompass undo --yes` for real and confirm every generated path is
  gone (`vendor/`, `vendor.toml`, `context-graph.db`, `.claude/skills/
  codecompass*`, `.cursor/rules/codecompass-*.mdc`,
  `.claude/commands/discovery.md`, and the root `CLAUDE.md` marker block
  removed) while any hand-written content in that same `CLAUDE.md`
  survives untouched.
- Fallback-path check: in a fresh scratch project, run only `init --scan`
  (no `sync` at all, so no graph exists), then `codecompass undo --yes`
  — confirm it still cleans up `vendor.toml` and whatever partial state
  exists without erroring on the missing `context-graph.db`.
