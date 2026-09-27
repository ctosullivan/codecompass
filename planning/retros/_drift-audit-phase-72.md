# Drift audit — Phase 72 (Ledgerkit Stage C learnings capture + post-v1 roadmap realignment)

**Auditor:** `docs-reconstructor`, MODE 1 (per-phase drift audit),
independent of `docs-maintainer`, `domain-skeptic`, and the fork review
already run for this phase. This report was verbally summarized during
the phase (its "Stage E" citation-staleness candidate was routed to
`domain-skeptic` and fixed in `336b4cd`, see
`planning/retros/_domain-skeptic-review-phase-72.md`) but the standalone
report file was never written to disk at the time. This is that report,
redone from scratch against the phase's final state (`2066a49`), not
reconstructed from memory of the earlier verbal pass.

Diff audited: `933579c^..2066a49` — all six commits (`933579c`,
`b014068`, `c0c0d15`, `336b4cd`, `0cbad62`, `2066a49`).

**Verdict: DRIFT — 2 findings, both non-blocking.** No user-facing false
statement about CodeCompass's own runtime/CLI behaviour resulted from
this phase. Both findings are internal domain-corpus terminology
staleness left over from this phase's *own* remediation commit
(`336b4cd`) not being fully thorough against sibling instances of the
identical pattern it set out to fix.

## 1. Scope confirmation

```
git diff --stat 933579c^..2066a49 -- src/ docs/ architecture/ ai-docs/ README.md CLAUDE.md CONTRIBUTING.md decisions/
```

Touches only: `decisions/0062-post-v1-priorities-are-task-context-completeness-first.md`
(new ADR) and four `docs/domain/concepts/*.md` + `docs/domain/open-questions.md`
files. No `src/`, no `docs/` outside `docs/domain/`, no `architecture/`,
no `ai-docs/`, no `README.md`, no `CLAUDE.md`/`CONTRIBUTING.md` changes.

This is a pure planning/knowledge-base/domain-corpus phase: it records
learnings from studying an external project (Ledgerkit), writes one ADR
about post-v1 *prioritisation*, dispositions old pre-v1 backlog items,
rewrites `planning/ROADMAP.md`'s own backlog section structure, and
fixes a citation-staleness cluster in `docs/domain/`. No CLI flag,
config schema, generated-file format, module responsibility, or
observable user-facing behaviour changed. This matches the plan's own
scope statement.

## 2. `README.md`, `architecture/`, `ai-docs/` — no drift

Grepped for every term this phase's diff introduces or retires
project-wide: `Stage E`, `Stage C`, `GATE DD`, `Ledgerkit`,
`conditional-generalisation`, `Deferred/not-funded`,
`Future-improvement backlog`, `Priority A-F`.

- `README.md:289` ("`planning/ROADMAP.md`'s 'Future-improvement
  backlog'") — still accurate; that section still exists under that
  exact name in `planning/ROADMAP.md:93` after this phase's rewrite.
  `README.md`'s two `Ledgerkit` mentions (lines 29, 265) are generic
  ("real external project tested end-to-end") and unaffected by the
  Stage-C-learnings content this phase added.
- No hit for `Stage E`, `Stage C`, `GATE DD`, or
  `Deferred/not-funded` in `README.md`, `docs/` (outside `docs/domain/`),
  `architecture/`, or `ai-docs/`. Nothing there described the old
  Stage-E/GATE-DD framing this phase's ADR retires, so nothing there
  went stale.
- `architecture/context-graph-schema.md` cross-references
  `docs/domain/concepts/relationship-edge.md` and
  `docs/domain/concepts/context.md` generically ("what this graph means
  conceptually") — not dependent on the specific sentence this phase's
  fix commit touched in `relationship-edge.md`. Not affected.

**No drift found in `README.md`, `architecture/`, or `ai-docs/`.**

## 3. `docs/domain/` — the fix commit's own remediation was incomplete

`336b4cd` (this same phase) correctly identified and fixed a real
staleness cluster: `decisions/0062` retires the old "Stage E" phase-group
label project-wide (post-v1 work is no longer organised into lettered
stages, per `planning/ROADMAP.md`'s Phase 71 restructure), which made
four `docs/domain/` sentences — each naming "Stage E's own future Domain
stage" as the resolution vehicle for the `Evidence`/`Observation`/
`Claim`/`Decision` graph-level naming collision — false. The commit fixed
exactly those four locations (`claim.md`, `decision.md`,
`relationship-edge.md`, `open-questions.md` item 7) and superseded the
two originating Claims (`CL-EVID-009` → `CL-EVID-011`, `CL-EVID-003` →
`CL-EVID-012`) correctly, per `decisions/0060`'s Claim-supersedes-Claim
model.

Verifying independently against every occurrence of the retired
terminology in `docs/domain/` (not just the four the fix commit touched)
finds **three sibling instances of the identical pattern that the same
commit did not fix** — in the same files, in one case two lines from a
sentence it did fix:

- **`docs/domain/concepts/decision.md:27`** — "Those queues promote into
  a Stage C/E *roadmap* decision..." Still describes the general
  `context-gaps`/`context-observations` promotion path as going through
  a "Stage C/E" gated decision. Now false in the same way the fixed
  sentences were false: "Stage E" no longer exists as a phase-group
  label to promote *into*, and "Stage C" (per `planning/ROADMAP.md:513`)
  is a *completed, historical* phase, not a live promotion destination.
  `relationship-edge.md`'s own corrected language (same commit, same
  concept) shows the right fix: "...the old 'Stage C'/'Stage E'
  phase-group labels are retired (`decisions/0062`), but the same
  gated-ADR promotion mechanism `decisions/0051` describes still
  applies." `decision.md:27` never received the equivalent correction.
- **`docs/domain/concepts/decision.md:101`** — "**Narrower cousin of →
  a Stage C/E gated roadmap decision** reached via
  `context-gaps`/learning-lifecycle promotion..." Same issue, same file
  — this is 62 lines below the sentence (`decision.md:34-39`) that
  `336b4cd` *did* fix in this exact file, for this exact naming-collision
  topic.
- **`docs/domain/concepts/observation.md:51`** — "...its promotion path
  is a Stage C/E gated roadmap decision." Same issue, in a file the fix
  commit never touched at all, even though `observation.md` shares the
  same collision material as `claim.md`/`decision.md`/`evidence.md`
  (e.g. `observation.md:112` correctly still cites "Phase 57's Stage E
  design sketch" as a historical fact about where the collision was
  first proposed — that citation is fine, unlike the promotion-path
  claim at line 51, which describes a live/future mechanism).

A fourth, weaker instance: **`docs/domain/concepts/evidence.md:106`** —
the parenthetical citation `(CL-EVID-009)` backing "not yet built or
funded" for the graph-level `Evidence` entity-kind candidate still cites
the now-`superseded` `CL-EVID-009` rather than its replacement
`CL-EVID-011`. `claim.md`'s parallel citation for the identical fact was
updated by `336b4cd` to cite `CL-EVID-012, CL-EVID-011`; `evidence.md`'s
was not. (Weaker because `CL-EVID-011`'s own supersession note says it
supersedes `CL-EVID-009` "for exactly one reason, narrower than the
substantive collision itself" — the "not yet built or funded" fact this
citation backs may be part of the unchanged remainder of `CL-EVID-009`'s
statement. Flagging it because the sibling fix in `claim.md` treated the
citation as needing an update regardless, and consistency says
`evidence.md` should match.)

**Severity: non-blocking.** None of these four sentences describes
CodeCompass's own CLI/runtime behaviour to a user; all four are internal
domain-corpus vocabulary/citation staleness in a doc aimed at
contributors and AI agents orienting to the project's own concepts, not
end users. But they are real: `decisions/0062`'s retirement of the
"Stage E" label made them false in exactly the way the four sentences
`336b4cd` already fixed were false, and three of the four sit in files
that commit was already editing for the identical underlying issue.
Recommend routing to `domain-skeptic` for the same treatment already
applied to the four it did catch (likely as a follow-on to
`EV-SKEP-006`/`OBS-SKEP-007` rather than new records, since it's the
same collision, same retirement event, same evidence trail).

## 4. `docs/domain/` internal consistency of the fix itself

Independently verified (not trusting the commit message) that the parts
of the fix which *were* made are actually correct:

- `decisions/0062-post-v1-priorities-are-task-context-completeness-first.md`
  exists, is titled "...not the old Stage E/graph-capability grouping,"
  and states "GATE DD is not resolved by this decision" — matches
  `claim.md`/`decision.md`'s corrected text ("unresolved... re-homed to
  whichever future Priority B phase").
- `planning/pre-v1-disposition.md` §7 ("GATE DD / Stage E (Phases
  56-59)") exists, is headed "superseded as a phase group; candidate
  designs retained, re-homed under Priority A/B," and contains the
  exact re-homing table (`conditional-generalisation.md` §2.1-2.6 →
  Priority A/B/C/Backlog) the corrected `docs/domain/` prose cites.
  Matches.
- `CL-EVID-011.yaml` (`status: supported`, `supersedes: CL-EVID-009`)
  and `CL-EVID-012.yaml` (`status: supported`, `supersedes:
  CL-EVID-003`) exist and are well-formed; `CL-EVID-009.yaml` and
  `CL-EVID-003.yaml` correctly show `status: superseded`,
  `supersedes: null` (unedited original content, per `decisions/0060`'s
  append-only model). `DE-EVID-011.yaml`/`DE-EVID-012.yaml` (Derivations)
  and `EV-SKEP-006.yaml`/`OBS-SKEP-007.yaml` (the originating
  Evidence/Observation) are present and cross-reference consistently.
  This part of the remediation is genuinely correct, not just
  self-reported as correct.

## 5. Domain-claim staleness candidates (step 5 of my brief)

None beyond what's already covered in §3 above (which is drift, not a
staleness *candidate*, because the causal change — `decisions/0062`
retiring "Stage E" — already definitively landed in this same phase,
rather than being a change elsewhere that might or might not affect a
domain claim). No other `docs/domain/concepts/*.md` reference block
cites a file/symbol this phase's diff touched outside the cluster
already discussed.

## Scope note

Checked: full `933579c^..2066a49` diff stat against `src/`, `docs/`,
`architecture/`, `ai-docs/`, `README.md`, `CLAUDE.md`,
`CONTRIBUTING.md`, `decisions/`; every occurrence of `Stage E`, `Stage
C`, `GATE DD`, `Ledgerkit`, `conditional-generalisation`,
`Deferred/not-funded`, `Future-improvement backlog` across
`README.md`/`docs/`/`architecture/`/`ai-docs/`; independent re-read of
all seven `docs/domain/concepts/*.md` files this phase's retired
terminology touches (`claim.md`, `decision.md`, `observation.md`,
`derivation.md`, `evidence.md`, `provenance.md`, `relationship-edge.md`)
plus `open-questions.md`; independent verification of the new
ADR/disposition-table/Claim-yaml content the fix commit's message
claims exists, rather than trusting the commit message. Did not
re-derive or second-guess `docs/domain/` concept *content* itself
(out of scope — `domain-skeptic`'s territory); did not re-audit
`planning/ROADMAP.md`, `planning/CONTEXT.md`, or `planning/
pre-v1-disposition.md` for internal self-consistency beyond what was
needed to verify the `docs/domain/` citations against them, since those
files are session-state/planning docs, not in the `README.md`/`docs/**`/
`architecture/**`/`ai-docs/**` current-truth set this role audits. Did
not re-run or contest `domain-skeptic`'s or `knowledge-curator`'s own
substantive judgments (Claim supersession correctness, L-051 promotion) —
only checked that their claimed *outputs* exist and match what they say.
