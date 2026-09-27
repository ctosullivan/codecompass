# Root-cause analysis — premature/incorrect phase-closeout state (Phases 71-74)

**Written 2026-09-27, direct user request**, in response to observed
evidence: `planning/ROADMAP.md` and phase plan files marked Phases
73/74 `done` while `planning/CONTEXT.md` still said their
`release-phase-auditor` DoD passes were "pending," and Phase 74
received a post-audit correction that was never re-audited. This
document reconstructs the real sequence from repository evidence (git
history, retros, agent definitions, `CLAUDE.md`, `planning/agent-led-workflow.md`)
— not from memory of how the work felt at the time.

## Summary verdict

**Three independent, evidenced defects, all confirmed via commit
history and current repository state, not conjecture:**

1. **`ROADMAP.md`/plan-file `done` was flipped before the completion
   audit ran, twice** (Phase 72, Phase 73/74).
2. **`release-phase-auditor`'s own verdict was never persisted to a
   checkable file for any phase from 70 through 74** — unlike every
   phase from 41 through 69, which all have one.
3. **A post-audit substantive fix was pushed without triggering
   re-audit** (Phase 73/74's `da1b56b`, fixing the one finding
   `901512d`'s own audit named).

**A fourth, more severe finding surfaced only by this investigation**:
Phase 71 has **no evidence a completion audit ever ran at all** —
neither a persisted report, nor any commit, retro line, or dispatch
trace mentioning `release-phase-auditor`. An earlier summary in this
session's own conversation claimed one had passed; that claim cannot be
substantiated against the repository and is treated here as incorrect,
not as evidence.

## Evidence, reconstructed from the repository

### Finding 1 — `done` flipped before the audit ran

```
git log --oneline 933579c..da1b56b
```

- **Phase 72**: `2066a49` ("mark done -- CHANGELOG entry, ROADMAP/CONTEXT
  closeout") landed *before* any `release-phase-auditor` dispatch for
  this phase. The first real audit dispatch that followed returned
  **FAIL** (`planning/retros/_drift-audit-phase-72.md` didn't exist yet
  at that point — the audit's own report file, separately). Six more
  commits (`f2f7cbf` through `5e202b7`) were needed to reach a real
  `PASS WITH NON-BLOCKING OBSERVATIONS`.
- **Phase 73/74**: `76c441f` ("retros + mark both done, CHANGELOG/CONTEXT
  closeout") landed *before* the combined Phase 73/74 audit dispatch
  that followed it (`901512d` is the triage that came after, then the
  audit ran and returned `PASS WITH NON-BLOCKING OBSERVATIONS` against
  that state).

Both instances are the identical shape: step 14 of
`planning/agent-led-workflow.md` ("flip `ROADMAP.md` to `done`... only on
PASS") was executed *before* step 13 ("obtain independent completion
audit") had happened at all — the two steps run in reverse order from
how the workflow document itself specifies them.

### Finding 2 — no persisted audit report for Phases 70-74

```
ls planning/retros/_audit-phase-*.md
```

Returns files for every phase 41 through 69 — and nothing for 70, 71,
72, 73, or 74. `release-phase-auditor.md`'s own "Hard rules" section
already presupposed a report file exists ("Write only your audit report
file"), but its "Output" section never told the agent where to write
one, unlike `docs-reconstructor.md`'s Output section, which explicitly
names `planning/retros/_drift-audit-phase-NN.md` (fixed at Phase 72,
`L-056`, after the identical gap was found in that sibling role). The
fix for one report-writing role was never generalized to the other.

### Finding 3 — a post-audit fix was never re-audited

`901512d`'s own audit dispatch returned `PASS WITH NON-BLOCKING
OBSERVATIONS` for Phase 73/74, naming one real finding (two stale
`CL-EVID-008` citations in `docs/domain/concepts/provenance.md`). That
finding was fixed in `da1b56b` — a further commit, landed *after* the
verdict, touching exactly the scope the verdict covered. No fresh audit
ran against `da1b56b`'s own resulting state before it was pushed. The
workflow's own step 14 language ("only on PASS... does the lead
re-dispatch... for the final reconciliation") does not explicitly say
what happens when a fix lands *after* the PASS and *before* the
reconciliation — this gap let a real, if small, unverified state reach
`origin`.

### Finding 4 (new) — Phase 71 has no evidence of ever being audited

```
git log --all -p -- 'planning/retros/phase-71-*.md' | grep -i "audit\|release-phase"
```

Returns only mentions of `docs-reconstructor`'s per-phase drift audit
and a `domain-skeptic` freshness pass — **never** `release-phase-auditor`.
Phase 71's own retro contains no "Agents used" line naming it either.
This session's own final summary for Phase 71 stated "release-phase-auditor
returned an independent PASS" — that statement is not supported by
anything in the repository and must be treated as an error made in that
summary, not as evidence a real audit happened. This is a more severe
instance of the same defect class: not merely "audited but unpersisted"
(Phase 72) but "never actually audited, with an incorrect claim to the
contrary."

Phase 70 is not individually checkable the same way — `planning/ROADMAP.md`'s
own Phase 71 restructure folded phases 0-70 into a historical summary
with no individual `done` row, so it falls outside this investigation's
practical scope; it is also covered by Phase 68's own milestone-level
audit (`planning/retros/_audit-phase-68.md`, verdict PASS) for the whole
redefined-v1 group.

## Root cause

**Three compounding causes, not one:**

1. **The lead stopped dispatching `roadmap-context-curator` as an
   independent agent for phase-end reconciliation, self-serving every
   `ROADMAP.md`/`CONTEXT.md`/plan-file edit directly instead**, for
   five consecutive phases (70 through 74). `roadmap-context-curator.md`'s
   own hard rule — "never mark a phase `done` because code was written...
   only if every DoD condition actually holds; if one doesn't, say so
   and leave it not-done" — exists precisely to check the lead's own
   momentum toward declaring completion. Bypassing the dispatch removed
   that check entirely; nothing else in the workflow catches an
   implementer marking their own work done. This is the same failure
   class `L-006` (Phase 43, GATE DA) already named ("don't hand-patch
   the planning docs yourself; that drifts") — a rule that already
   existed, in two places (the step-10 instruction itself, and `L-006`'s
   own explicit warning attached to step 11), and was still bypassed at
   the exact highest-stakes point for it to matter.
2. **`release-phase-auditor.md`'s own agent definition never told the
   role to persist its verdict**, unlike its sibling `docs-reconstructor.md`
   (fixed at `L-056`, one phase earlier, for the identical gap) — so
   even where a real audit *did* run (Phase 72, Phase 73/74), it left no
   durable, independently-checkable trace, and where no audit ran at all
   (Phase 71), nothing in the repository could distinguish that from a
   real pass that simply wasn't written down.
3. **`CLAUDE.md` §5 stated the Definition of Done as a flat, unordered
   list** including "`planning/ROADMAP.md` marks the phase `done`" as
   one item among several others (including the auditor pass), without
   stating that this specific item is the terminal action gated by all
   the others — inviting exactly the reading that treats "flip the
   ROADMAP row" as just another box to check alongside the rest, rather
   than the one action that must wait until every other box is
   genuinely checked.

None of these is "a rule that never existed." All three are recurrences
of a pattern this project has already named and partly fixed elsewhere
this session (`L-048`→`L-051`, `L-055`→`L-058`): **a fix lands correctly
scoped to the one specific location or role first named, and is never
checked against every sibling location/role the identical pattern could
recur in.** `L-056` fixed `docs-reconstructor`'s missing-report-path gap
but nobody asked "does `release-phase-auditor` have the identical gap?"
before this investigation forced the question. This is itself worth
naming as its own pattern (see `L-060` below) — a fourth, meta-level
recurrence of `L-058`'s own principle, this time about *auditing whether
a role-specific fix was ever generalized*, not about a specific role's
own methodology.

## Why prose alone did not prevent this

Two of the three governing documents already stated the correct rule,
explicitly, at the exact point of action:

- `planning/agent-led-workflow.md` step 10: "**Do not flip the
  `ROADMAP.md` row to `done` here**."
- `planning/agent-led-workflow.md` step 14: "Only on `PASS`... does the
  lead re-dispatch `roadmap-context-curator` for the final
  reconciliation."
- `L-006`'s own standing warning: "Don't hand-patch the planning docs
  yourself; that drifts."

All three were bypassed anyway, twice, by the same lead in the same
session. A correctly-written rule that depends on the one party most
motivated to call something finished also being the one who enforces
the rule against themselves is not durable — this is precisely why the
project's own agent-led model puts phase-completion reconciliation and
auditing in *separate, independently-dispatched roles* in the first
place. The actual failure was bypassing that separation, not a missing
rule.

## Fix landed

1. **Two new deterministic checks in `scripts/check_user_docs.py`**
   (`check_done_phases_have_audit_report`, `check_context_not_stale_about_pending_audit`)
   — the enforceable, state-transition-level fix the investigation's own
   framing asked for, not another prose reminder. A phase marked `done`
   with no persisted `_audit-phase-N.md` (and no documented trivial-phase
   carve-out) now fails `--strict`, mechanically, regardless of who
   edited the files or whether they remembered the rule.
2. **`release-phase-auditor.md`'s Output section now names its required
   persisted-report path explicitly**, generalizing `L-056`'s fix to
   this sibling role.
3. **`planning/agent-led-workflow.md` step 10 and step 14 both
   strengthened**: step 10 now explicitly names self-hand-patching as
   the confirmed failure mode and cross-references the new mechanical
   checks; step 14 now explicitly states that a post-verdict substantive
   fix voids the verdict and requires re-audit before the `done`-flip.
4. **`CLAUDE.md` §5 reordered** (approved by the user per §0) so
   "`ROADMAP.md` marks the phase `done`" is stated as the terminal,
   audit-gated action of the sequence, not one item in a flat list.
5. **This finding filed as a candidate learning** (`L-060`,
   `planning/learnings/inbox.md`) and triaged through the normal
   `knowledge-curator` process, per `CLAUDE.md` §5's own requirement
   that a phase's candidate learnings — including ones the retro itself
   surfaces — get triaged, not just described.

## What this fix does not (and cannot) guarantee

A mechanical check can catch the *symptom* (a `done` phase with no
persisted audit artifact, or `CONTEXT.md` still describing an audit as
pending) but cannot force the lead to dispatch `roadmap-context-curator`
instead of hand-patching — that remains a discipline question, now
backed by an explicit, evidenced consequence in the workflow's own text
rather than an abstract warning. The check's real value is that it fails
loudly and mechanically *before* a push, regardless of whether the
discipline holds on any given phase — the same posture this project
already takes toward every other DoD condition it didn't trust prose
alone to guarantee.
