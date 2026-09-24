# Drift audit — Phase 71 (post-v1 documentation refresh)

**Auditor:** `docs-reconstructor`, MODE 1 (per-phase drift audit),
independent of `docs-maintainer`/the fork review already run for this
phase. Diff audited: `9ce200f..HEAD` (`657dceb`, `4bc7c1d`, `0e36123`).

**Verdict: DRIFT — 3 findings** (all non-blocking-to-moderate; none is a
false statement about CodeCompass's own runtime behaviour). Plus 2
domain-claim staleness candidates and 1 process-consistency note.

## 1. Scope confirmation

`git diff --stat 9ce200f..HEAD -- docs/ architecture/ ai-docs/
src/codecompass/ decisions/ CLAUDE.md` — empty. Confirmed: this phase's
full diff touches only `README.md`, `planning/CONTEXT.md`,
`planning/ROADMAP.md`, `planning/phase-71-*.md` (new plan file),
`scripts/check_user_docs.py`, `tests/test_check_user_docs.py`. No
`src/`, `docs/`, `architecture/`, `ai-docs/`, `decisions/`, or `CLAUDE.md`
changes. This matches the plan's own "explicitly not touched" list
except where the plan's §1.4 consistency sweep found something (it
found nothing, and — see Finding 1/2 below — should have found two
things).

## 2. `README.md` read end-to-end

Read all 330 lines independently, not just the sections the fork's
review focused on (capability claims, CLI surface, internal links).
Cross-checked line-by-line: `codecompass --budget 0` sample output
against `examples/README.md` (verbatim match); every `decisions/00NN`
citation resolves to a real file (`0008`, `0014`, `0019`, `0021`,
`0031`, `0033`, `0036`, `0045`, `0048`, `0053`, `0054`, `0055`, `0056`,
`0060`); "Haskell/Stack is a fourth, added in Phase 60" against
`docs/external-adapters.md`'s own "Phase 60" framing (consistent); the
"Future-improvement backlog" pointer against `ROADMAP.md`'s actual
section title (`## Future-improvement backlog (unscheduled)` — close
enough, not misleading); `L-031`/`L-032` descriptions in "Limitations"
against `ROADMAP.md`'s own backlog table entries (consistent in
substance). No tone seam or stale cross-reference found *within*
`README.md` itself — the fork's review of this file holds up under a
fresh, independent read.

## 3. `ROADMAP.md` restructure — dangling references elsewhere

No `ROADMAP.md#anchor`-style reference exists anywhere in the repo
(grepped). No prose reference to a specific removed phase row (e.g.
"see ROADMAP.md phase 24") exists outside `ROADMAP.md`/`README.md`
themselves — `architecture/overview.md:27`'s "for current milestone/phase
status, see `planning/ROADMAP.md`" is a generic pointer with no
dependency on the old row-table structure, still accurate.

However, two **pre-existing** sentences elsewhere in the repo describe
`ROADMAP.md`'s own *structure* in a way Phase 71's restructure now makes
false — the plan's own §1.4 consistency sweep was scoped to catch
exactly this and missed both:

- **`ai-docs/CLAUDE.md:22`** — "[`planning/ROADMAP.md`]... (full phase
  table)". `ROADMAP.md` no longer has a full phase table: its own new
  header explicitly says the v1.0.0 history is "preserved in three
  places, not repeated here as a 70-row table" (`ROADMAP.md:17-21`).
  Only the "Deferred/not-funded", "Post-v1 development" (one row, Phase
  71 itself), and "Future-improvement backlog" sections are tabular now.
  This is the file an agent is told to read first
  ("Understanding what codecompass does... start with
  `ai-docs/README.md`" → this file), for exactly the "current project
  state" question — a real, if narrow, misdirection. **Blocking**
  (directly false about where to find the thing it points at).
- **`CONTRIBUTING.md:56`** — "`planning/ROADMAP.md` — full-roadmap
  phase-status table (every phase, not just the current one)". Same
  literal claim, same staleness, aimed at human contributors this time.
  Note this phrasing is inherited near-verbatim from `CLAUDE.md` §2's
  own (untouchable, out-of-scope-for-this-audit) definition of what
  `ROADMAP.md` *is* — worth the lead's attention as a possible tension
  between Phase 71's restructure and `CLAUDE.md` §2's own standing
  requirement, not just a wording fix in `CONTRIBUTING.md`. **Blocking**
  as a literal description of current file content; flagging the
  `CLAUDE.md` tension as a process observation, not something I can
  resolve or that a docs fix alone settles.

## 4. Mechanical check adaptation (`check_readme_phase_count`)

Read the new implementation and its updated tests. Confirmed against the
actual current file contents:

```
$ grep -no "[Pp]hases 0-[0-9]*" README.md planning/ROADMAP.md
planning/ROADMAP.md:33:phases 0-38
README.md:10:phases 0-38
```

Exactly one match per file today, both `0-38`, both plain ASCII hyphens
— the regex's `re.search` (first-match) behaviour carries no live
ambiguity risk against the actual current files. Real, but currently
inert, fragility not covered by the test suite: the regex
(`r"phases 0-(\d+)"`) requires a literal ASCII hyphen and the literal
word "phases" (case-insensitive) — an en dash ("phases 0–38") or a
rephrasing ("Phases: 0 through 38") would silently degrade to the
"no claim to check" `Finding` branch rather than a real mismatch
finding. Given both files are hand-authored today with consistent
"phases 0-N" hyphenated phrasing and this is the phrasing the phase
itself just established, this is a **non-blocking observation**, not a
current drift — noting it because it's exactly the kind of edge case
this audit is asked to check, not because it's live today.

## 5. Domain-claim staleness candidates

`docs/domain/` exists; checked per my brief's step 5. Two of this
phase's changed files are directly cited by `docs/domain/concepts/*.md`
reference/example material:

- **`docs/domain/concepts/connector.md`** (lines ~17-24) cites
  `planning/ROADMAP.md` as one of several planning documents whose text
  "lists 'connector' alongside 'adapter, protocol, reference, decision,
  invariant' purely as a term to research." Verified: the actual source
  of that claim was the old Phase 63D row
  (`git show 9ce200f:planning/ROADMAP.md | grep connector`, line 352),
  which Phase 71 deleted along with the rest of the per-phase table.
  `planning/ROADMAP.md` today contains **no** occurrence of the string
  "connector" at all (`grep -n connector planning/ROADMAP.md` → no
  output). `connector.md`'s citation of this specific file is now
  unverifiable against current content. (Notably, `CHANGELOG.md:120`
  records that a near-identical break already happened once before, at
  Phase 66's `CONTEXT.md` rewrite — this concept page's citations to
  fast-moving planning docs appear to be a recurring fragility.)
- **`docs/domain/concepts/invariant.md`** ("Example" section) cites
  `tests/test_check_user_docs.py::TestReadmePhaseCount::
  test_ignores_done_phases_in_redefined_v1_section` as its worked
  example of a promoted `invariant`-classified learning (`L-001`).
  Phase 71's diff removed this exact test (it tested the now-deleted
  done-phase-row-table-scanning logic) and replaced it with
  `test_flags_missing_roadmap_claim`, which exercises different
  behaviour entirely. The cited test name no longer exists in
  `tests/test_check_user_docs.py`.

Per my brief, these are **candidates for `domain-skeptic`'s next
reconciliation pass, not drift findings** and are not counted in the
`DRIFT — 3 findings` verdict above.

## 6. Process-consistency note (not a doc-drift finding)

`planning/ROADMAP.md`'s own Phase 71 row (line 71) still says status
`planned`, but `planning/CONTEXT.md`'s "What was just completed" section
already says "Phase 71 — post-v1 documentation refresh — **in
progress**" and two implementation commits (`4bc7c1d`, `0e36123`) have
already landed. `ROADMAP.md`'s own "How this file is kept in sync"
section states: "This table is the source of truth for 'what phase are
we on' — if it ever disagrees with `planning/CONTEXT.md`, treat that as
a bug to fix immediately." That disagreement exists right now, within
the diff under audit. Not scored as a doc-drift finding (no user-facing
system-behaviour claim is wrong), but flagged since `ROADMAP.md`'s own
rule calls it a bug.

## Scope note

Checked: `README.md` (full, independent read), `planning/ROADMAP.md`
(full), `planning/CONTEXT.md` (full), `scripts/check_user_docs.py`'s
`check_readme_phase_count` and its tests, cross-repo grep for
`ROADMAP.md`-structure-dependent prose in `docs/`, `architecture/`,
`ai-docs/`, `CONTRIBUTING.md`, and the `docs/domain/concepts/*.md`
reference blocks that cite files this phase touched. Did not re-derive
or second-guess `docs/domain/` concept *content* (out of scope per
`documentation-lifecycle.md` — that's `domain-skeptic`'s territory, only
triggered here as staleness candidates). Did not re-check CLI-surface
accuracy or capability-claim honesty in `README.md` in exhaustive detail
a second time beyond spot-checks — the fork's own review already did
that specific pass and my independent read found no reason to doubt it.
