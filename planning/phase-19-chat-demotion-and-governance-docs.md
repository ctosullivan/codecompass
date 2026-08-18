# Phase 19: Chat demotion + governance docs

## Scope

The last phase of MVP (v0.2) (`decisions/0030`) — mostly documentation,
closing out the arc's framing consequences now that every behavioral
piece (phases 10-18) is actually built. Per `decisions/0034`, `chat.py`'s
**code is unchanged** in this phase; only how the project describes
itself changes.

**Covered:**
- `README.md` — rewritten around the new primary workflow: bare
  `codecompass` → automatic clone + usage-driven enrichment (with
  disclosed cost) → query the graph via `codecompass query` or
  `/discovery` → generated Skills as the steady-state consumption
  surface. `chat <vendor>` described as a secondary, digest-only, no-
  live-source option — present, useful for a quick terminal Q&A, not the
  headline feature.
- `architecture/overview.md`:
  - "Chat REPL" section rewritten: opens with `decisions/0034`'s framing
    instead of `decisions/0012`'s ("the REPL is the actual product")
    — historical note added that `decisions/0012` established the
    original framing and is now superseded, without editing
    `decisions/0012` itself (append-only).
  - Its "bare `depcompass chat` project-root routing... remain post-MVP
    (Phase 9) target design" note (stale since well before this rework —
    referring to the *original* Phase 9, now Phase 20 per this rework's
    renumbering) corrected to point at the current Phase 20
    (project-root routing/rollup, post-MVP) instead.
  - "Retrofitting to existing projects" and "Cost model" sections
    (already substantially rewritten in Phase 15) get a final pass
    confirming they read coherently end-to-end now that every phase in
    this arc has landed.
- `.claude/skills/codecompass/SKILL.md`'s generation (`skill.py`,
  `render_tool_skill`) — final wording pass: confirm it doesn't feature
  `chat` as a first-mentioned workflow step (it shouldn't, after Phase
  15's rewrite already dropped `promote` and added `query`/`/discovery`
  language — this phase double-checks and adjusts if `chat` crept back in
  anywhere prominent).
- `docs/cli-reference.md` — final consistency pass across the whole
  document now that phases 9-18 have each incrementally touched it;
  confirm no stale `promote`/`depth` references remain anywhere (a full
  read-through, not just a grep, since prose references don't always
  contain the literal strings a grep would catch).
- **MVP (v0.2) closes out**: `planning/ROADMAP.md`'s MVP (v0.2) table —
  all of phases 9-19 marked `done`; `CLAUDE.md` §6's milestone-grouping
  text (already updated in Phase 9's planning session to acknowledge two
  milestone groups) needs no further edit here, but `CLAUDE.md` §6's
  release-promotion step (`decisions/0030`: "`v0.2` tags only once
  Phase 19 is done") becomes applicable — **cutting the actual `v0.2`
  tag remains a separate, not-yet-made decision**, same posture
  `decisions/0022` established for `v0.1` and never contradicted since.
- Tests: no new test files expected — this phase's "verification" is
  documentation coherence, not code behavior. If the `chat.py` wording
  double-check above turns up an actual string change, `tests/test_chat.py`
  gets the matching assertion update.

**Explicitly deferred / out of scope:**
- Any code change to `chat.py` beyond a possible wording tweak surfaced
  by the double-check above.
- Cutting the `v0.2` git tag itself — a separate decision, not implied by
  this phase's completion (same non-implication `decisions/0022`/`0030`
  already establish for `v0.1`).
- Phase 20 (project-root routing/rollup) — explicitly the next phase
  after this arc, not started here; this phase only *corrects a stale
  cross-reference* to it in `architecture/overview.md`, doesn't implement
  it.

## Design decisions

No new ADR needed — `decisions/0034` already covers the substantive
"chat demoted" decision; this phase is its documentation execution, not
a new design choice.

## Files

- `README.md`, `architecture/overview.md`, `docs/cli-reference.md` —
  rewritten/corrected as above.
- `src/codecompass/skill.py` — wording-only adjustment if the double-check
  finds one.
- `tests/test_chat.py` — only if `chat.py` itself changes.
- `planning/ROADMAP.md` — MVP (v0.2) phases 9-19 all marked `done`.
  `planning/CONTEXT.md`, `CHANGELOG.md` — this phase's completion, plus
  an explicit note that MVP (v0.2) as a whole is now `done` and the
  `v0.2` tag decision is open (mirroring exactly how Phase 8's
  `CONTEXT.md` entry handled the `v0.1` milestone's completion).

## Verification

- `pytest` — full suite passes (expected unchanged from Phase 18, absent
  the possible `chat.py` wording tweak).
- `ruff check .` — clean.
- Read-through, not grep-only: `README.md`, `architecture/overview.md`,
  `docs/cli-reference.md` reviewed end-to-end for narrative coherence —
  confirm a first-time reader would understand `codecompass`'s primary
  workflow as "automatic clone + usage-driven enrichment + query the
  graph / generated Skills / `/discovery`," with `chat` clearly framed as
  a secondary option, not encounter any lingering `promote`/`depth`
  reference describing current behavior (historical mentions in
  `decisions/`/dated `CHANGELOG.md` entries excepted, as established
  since Phase 9).
- Confirm `planning/ROADMAP.md`'s MVP (v0.2) table shows all of phases
  9-19 as `done`, and that its "MVP (v0.2) done when" criteria (written
  during this rework's original planning session) are each concretely
  satisfiable against the now-fully-built system, not just aspirational
  text.
