# Completion audit — Phase 74 (Priority B provenance hardening, closes `L-031` + `L-032`)

**Auditor:** `release-phase-auditor`, third independent completion-audit
pass for this phase, dispatched specifically to verify the third fix
round (`f667da4`, fixing `capability.md`'s own intra-file contradiction
found by this report's own second version) and, per explicit
instruction, to do a full top-to-bottom independent re-read of every
`docs/domain/concepts/*.md` file this phase touched at any point — not
grep alone, since grep already missed the flagged contradiction once
(the two contradicting sections didn't share matching keywords).

**Audited state:** current `main` HEAD, `f667da4` ("fix(phase-74): fix
capability.md's own intra-file contradiction"), covering all of Phase
74's commits (`1dc228f`, `050e366`, `40e7718`, `3d0ed30`), the shared
Phase 73/74 closeout (`76c441f`), the retro/triage commit (`901512d`),
the first post-audit fix (`da1b56b`), the second post-audit fix
(`157957b`), the intervening process fixes (`f1ddc4c`, `9a14753`,
unrelated Phase 75 planning `60c175c`), and this third post-audit fix
(`f667da4`).

**Verdict: PASS WITH NON-BLOCKING OBSERVATIONS.** The specific defect
that produced the second FAIL — `capability.md`'s "What it is NOT"
section contradicting its own "Counterexample" section — is genuinely,
verifiably fixed, and a full independent re-read of all six
`docs/domain/` files this phase touched, plus a full-corpus grep sweep,
found no further instance of this or any related contradiction. All
required commands re-run clean, matching exact expectations. No new
protected-file drift or scope creep from `f667da4`. Two items are noted
as non-blocking observations below (§5) — both pre-existing, already
named and root-caused as `L-060`, neither reintroduced or worsened by
this pass's own audited commit.

## 1. `capability.md`'s intra-file contradiction — confirmed fixed

Re-read the live file (`docs/domain/concepts/capability.md`) top to
bottom. "What it is NOT" (lines 36-39) now reads: "**Closed as of
Phase 74 (`L-032`) — now validated against its own closed set by the
receiving code.** See 'Counterexample' below for the full detail of
what changed and why this was a real, observed gap before this phase,
not merely a hypothetical one." This now matches, rather than
contradicts, the "Counterexample / edge case" section (lines 63-76),
which states "**Closed as of Phase 74 (`L-032`) — the received
`capabilities` list IS now validated against the closed 4-value set at
parse time**" with the full enforcement-code detail. Both sections now
agree: the gap was real before Phase 74, and is closed as of Phase 74.
`git show --stat f667da4`: exactly one file changed, 4 insertions/3
deletions — the minimal, precisely-scoped fix the prior audit's
required-fix list asked for.

## 2. Full independent top-to-bottom re-read of all six `docs/domain/` files this phase touched

Per the dispatch's explicit instruction, read every section (Definition,
"What it is NOT", Invariants, Example, Counterexample/edge case,
Relationships, References) of all six files in full, not just the
previously-flagged locations, hunting for any other present-tense claim
that `symbol_enrichment`'s provenance column or the adapter
`ecosystem`/`capabilities` validation is absent/unvalidated/not-yet-built
in a way current code contradicts.

- **`capability.md`** (107 lines, read in full): now internally
  consistent throughout — see §1. "Relationships" and "References"
  sections make no competing claim.
- **`protocol.md`** (151 lines, read in full): "What it is NOT" makes no
  claim about validation status at all (its four bullets are about gRPC/
  network/plugin-marketplace exclusions, protocol-vs-adapter identity,
  the "adaptor"/"adapter" repo-naming drift, and protocol-vs-`context-graph.db`
  schema independence — none touch the `L-032` gap). "Invariants" §3
  correctly cross-references `ecosystem.md`'s own edge case rather than
  asserting a status itself. "Counterexample / edge case" correctly
  states "Closed as of Phase 74." No contradiction found.
- **`ecosystem.md`** (101 lines, read in full): "What it is NOT" third
  bullet describes the wire-protocol `ecosystem` field as "free text,"
  which is a structural fact (still true — the *type* is still free
  text) not a validation-status claim, and does not conflict with the
  Counterexample section's "now read and compared" framing — the two
  are talking about different properties (type openness vs. whether a
  comparison now happens) and are explicitly reconciled by the file's
  own "Narrower point preserved unchanged" paragraph. No contradiction
  found.
- **`provenance.md`** (138 lines, read in full): Definition point 2 and
  the Counterexample section both consistently state the current,
  correct picture — all three enrichment tables now carry `model`, with
  `symbol_enrichment.model` nullable as a stated, deliberate residual
  asymmetry (not glossed over, not contradicted anywhere else in the
  file). "What Provenance is NOT" makes no claim about `symbol_enrichment`
  specifically. No contradiction found.
- **`evidence.md`** (140 lines, read in full — the file the first FAIL
  pass fixed): the "Thinner/different-shaped analogue" relationship
  bullet correctly states all three enrichment tables "now carry a
  `model` provenance column each," consistent with `provenance.md`.
  No other section makes a competing claim. No contradiction found.
- **`open-questions.md`** (145 lines, read in full): items 9 and 10 are
  both explicitly marked **RESOLVED (Phase 74)**, with accurate
  before/after framing and correct cross-references to the now-fixed
  `provenance.md`/`ecosystem.md`/`capability.md` sections. No
  contradiction found.

**Full-corpus grep sweep** (not relied on alone, but run as a
cross-check after the manual read): `grep -rn "real, observed gap\|not a
hypothetical" docs/domain/` → exactly one hit, in `capability.md`'s own
now-corrected past-tense framing ("why this was a real, observed gap
before this phase"), not a live contradiction. A second sweep for
`not validated|never validated|unvalidated` (case-insensitive) across
all of `docs/domain/` → zero hits. A third sweep (from the first FAIL
pass's own fixed claim) for `carries none|no provenance column|has
no.*model` scoped to `symbol_enrichment` → zero hits. **No third sibling
instance of this contradiction pattern exists anywhere in `docs/domain/`.**

## 3. Commands re-run against the current working tree

- `pytest -q`: `1 failed, 640 passed, 2 skipped` (191.84s). The one
  failure is the expected, named-in-advance
  `tests/test_check_user_docs.py::test_no_false_positives_against_real_repo`
  finding (`context_not_stale_about_pending_audit` on
  `planning/CONTEXT.md`) — not a Phase 74 regression, matches the
  dispatch's stated expectation exactly.
- `ruff check .`: `All checks passed!`
- `python scripts/check_user_docs.py --strict`: exactly 1 finding —
  the same `context_not_stale_about_pending_audit` finding, nothing
  else. Confirmed identical with and without `--strict` (no additional
  non-strict findings either). No finding attributable to `f667da4` or
  to any other Phase 74 change.
- `python scripts/check_knowledge_base.py`: no findings.

All four commands match the dispatch's stated expectations exactly.

## 4. Protected-file drift / scope-creep check on `f667da4`

`git show --stat f667da4`: one file changed —
`docs/domain/concepts/capability.md` (7 lines). `git diff
157957b..f667da4 -- CLAUDE.md decisions/`: empty. No protected file
touched, no scope creep — the commit does exactly, and only, what its
message and the prior audit's required-fix list describe.

Separately, `CLAUDE.md` itself *was* changed earlier in this session
(`f1ddc4c`, "docs(claude): make ROADMAP-done the terminal, audit-gated
DoD action (L-060)"), but this predates the second audit pass's own
baseline (`60c175c`) and was already outside this pass's or the prior
pass's audited-commit range; the prior pass's own §4 already confirmed
`git diff 60c175c..157957b -- CLAUDE.md decisions/` was empty, and
`f667da4` (this pass's only new commit) does not touch it either. Per
`planning/retros/_root-cause-closeout-defect.md`, this CLAUDE.md change
was presented to and approved by the user per §0 as part of the `L-060`
process fix — not a silent edit — and is not part of Phase 74's own
scope; it is noted here only for completeness of the protected-file
check, not as a finding against this phase.

## 5. Non-blocking observations (pre-existing, already named as `L-060`, not introduced or worsened by `f667da4`)

1. **`planning/ROADMAP.md`'s Phase 74 row, and the plan file's own
   Status line, already say `done`** — flipped at `76c441f`, chronologically
   *before* any completion audit had run at all, let alone passed. This
   is the exact `L-060` defect (`planning/retros/_root-cause-closeout-defect.md`),
   already root-caused, already fixed at the process level going forward
   (mechanical checks in `scripts/check_user_docs.py`, strengthened
   `agent-led-workflow.md` steps 10/14, `CLAUDE.md` §5 reordering). I am
   not re-litigating or reversing that historical flip — by the time of
   *this* pass, the underlying content the `done` label describes is now
   genuinely, verifiably complete (per §§1-4 above), so the label is
   substantively accurate even though the process that produced it was
   not. Flagged here for the record, not as a required fix for this
   phase specifically, since `L-060`'s own fix already exists and
   applies going forward; unwinding the historical sequencing now would
   be process theater with no substantive effect on Phase 74's actual
   state.
2. **`L-060` itself remains untriaged** (`planning/learnings/inbox.md`,
   status: `candidate`, `promoted_to:` empty) — filed at `9a14753`, no
   `knowledge-curator` triage commit has landed since. `L-060` is a
   cross-phase (70-74) process learning, not literally surfaced by
   Phase 74's own retro (the retro's own "Candidate learnings filed"
   section predates `L-060`'s filing and does not mention it), so I do
   not read `CLAUDE.md` §5's "candidate learnings from the phase...
   including any surfaced by the retro" as strictly requiring `L-060`'s
   triage as a gate on *this specific* phase's `done` status — but it is
   worth the lead's attention soon, given it documents exactly the
   defect class this phase's own closeout has now hit three times.
3. **`planning/retros/phase-74-provenance-hardening.md`'s "Commit(s)"
   list does not yet mention `f1ddc4c`/`9a14753`/`157957b`/`f667da4`** —
   it was last updated to add `da1b56b` (the first post-audit fix) but
   predates the second FAIL pass and this third fix. Not a DoD blocker
   (the retro's required sections are all present and substantive — see
   §6 below) but worth a final append before the lead's own closing
   reconciliation, matching the retro's own established practice of
   keeping this list current.
4. **`planning/CONTEXT.md` still says the `release-phase-auditor` pass
   is "Pending"** — this is expected and named in advance by the
   dispatch (Phase 73/74's own final reconciliation step, not yet done).
   Now that this pass has returned PASS WITH NON-BLOCKING OBSERVATIONS,
   the lead's own next step (per `CLAUDE.md` §5/§6 and
   `agent-led-workflow.md` step 14) is to dispatch `roadmap-context-curator`
   for the final reconciliation — updating `CONTEXT.md` to reflect this
   verdict — then push, per §6's auto-push rule (a `PASS WITH
   NON-BLOCKING OBSERVATIONS` verdict qualifies).

## 6. Everything else already independently re-verified by the prior two passes, re-confirmed unchanged

The first pass's plan-verification re-run, the second pass's independent
re-verification of the `evidence.md` fix and the retro's commit-list
correction, and both passes' review of `L-031`/`L-032`/`L-058` tracking
accuracy, the retro's structural completeness (all `TEMPLATE.md`
sections present and substantive: Where we are, Goal, Scope delivered
vs planned, What was achieved, What worked, What didn't work, Lessons
learnt, Process-improvement feedback, Candidate learnings filed, Where
we're going, Time/cost note), and the "not a reference-project phase"
determination all concern content `f667da4` did not touch and remain
valid. `L-031`/`L-032`/`L-058` are all confirmed `promoted` in
`planning/learnings/promoted.md` at this HEAD (re-verified directly,
not merely trusted from the prior report).

## Summary

All three concrete FAIL findings across this phase's three audit rounds
are now genuinely closed: the stale `evidence.md` claim, the stale
retro commit list, and `capability.md`'s intra-file contradiction. A
full independent top-to-bottom re-read of all six `docs/domain/` files
this phase touched, plus three targeted full-corpus grep sweeps, found
no further instance of the same or a related contradiction. All
required verification commands produce exactly the expected results.
`f667da4` introduces no protected-file drift or scope creep.

**Verdict: PASS WITH NON-BLOCKING OBSERVATIONS** — the four items in §5
are process/bookkeeping notes (a pre-existing, already-named-and-fixed
premature-ROADMAP-flip defect; `L-060`'s own pending triage; the
retro's commit list needing one more append; `CONTEXT.md`'s expected
pending-audit text) for the lead's final reconciliation pass, not
defects in Phase 74's own delivered content requiring another
fix-and-re-audit cycle.
