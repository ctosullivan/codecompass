# Project context

This file reflects the *current* state of the project — overwritten at
each stopping point, not appended to. See `CHANGELOG.md` and
`planning/retros/` for history; per `CLAUDE.md` §4, this file is for
session-resumption, not a project history.

## Current phase

**Phase 81B (clean-room project redocumentation from intermediary
knowledge) is `planned` — committed and amended, not started, direct
user request, 2026-10-08.** Implementation is explicitly gated on direct
user approval of the committed, amended plan
(`planning/phase-81b-clean-room-redocumentation.md`). No clean-room
branch, isolated workspace, writer dispatch, documentation
deletion/archival, or `codecompass-template` change has happened — both
the original planning task and this same-day amendment were planning-only;
the plan file, this file, and `planning/ROADMAP.md` are the only
artefacts either produced.

What the plan commits to, grounded in real investigation (not assumed):
a reproducible, mechanically-isolated whole-project clean-room
documentation reconstruction workflow, run to completion against both
`ctosullivan/codecompass` and `ctosullivan/codecompass-template`,
operationalising Phase 79/80's clean-room methodology and Phase 81's own
intermediary-knowledge layer together for the first time. Key findings
the plan is built on: CodeCompass's own rendered intermediary knowledge
is real but heavily concentrated (88% of `codecompass-domain`'s
projection sits in `overview.md`, traced to 30 of 31 Claims having no
`assertion_kind` set — a measured root cause the plan's own preparation
stage enriches honestly, never fabricates); three of five knowledge
slugs have never been rendered at all; a new candidate isolation
mechanism (`unshare`-based Linux network/mount namespaces) was
identified and minimally probed (confirmed to genuinely block outbound
network — stronger than `Agent(isolation: "remote")`'s own
already-tried, same-host result at Phase 79) but not yet proven against
the full five-route-preflight-plus-active-escape protocol, and one real
open sub-problem (an AI writer's own need for network access to its
model provider) is named explicitly, not assumed solved.

**Same-day amendment (ten corrections)**: (1) verified Mode B isolation
is now a **hard prerequisite** for the authoritative clean-room run — a
`best-effort`/`UNMET` outcome **blocks** Phase 81B rather than
satisfying it, correcting the first-committed version's own symmetric
"either outcome is acceptable" framing; (2) no pre-existing human-facing
narrative documentation may reach the writer in any form, including
`docs/domain/**` and anything derived from the current `README.md` —
old prose is preparation-side input only, re-grounded into validated
knowledge before it can influence the handoff; (3) the clean-room branch
now carries an explicit, named allowlist/exclusion list
(`src/**`/`tests/**`/schemas/handoff vs. `README.md`/`docs/**`/
`architecture/**`/`ai-docs/**`/`.git/**`/raw ADR history) with a
fail-closed branch validator, replacing the ambiguous "handoff
filesystem" description; (4) the cold-reader gate now runs inside the
same verified Mode B boundary as the real writer — a Mode A cold-reader
pass is no longer treated as sufficiency evidence; plus corrections
tightening `codecompass-template`'s own preparation (no longer
synthesising directly from its current README/docs prose), the
render-everything-vs-include-everything distinction for knowledge slugs,
the "full re-doc" completion bar (no narrative category implicitly
exempt), an explicit preparation-side/writer-side trust-boundary
statement, and the verification stage's own "informed but never relays
old prose to the writer" rule. The plan explicitly adopts, rather than
duplicates, the existing
`planning/strict-isolation-for-documentation-reconstruction.md` backlog
item's own scope and acceptance criteria — Phase 81B is, explicitly,
that item's own named revisit trigger ("a third independent application
of the clean-room methodology"); `planning/ROADMAP.md`'s backlog row for
it now links forward to Phase 81B rather than restating it. **Resolution
is no longer symmetric**: only a genuine `verified` isolation outcome
both closes that backlog item and allows Phase 81B to proceed to
completion; an honest `UNMET` outcome (after genuinely investigating the
`unshare`-based candidate and at least one alternative substrate) updates
the backlog item but leaves Phase 81B itself `blocked`, not closed.

**Phase 81 (persistent bidirectional intermediate knowledge layer)
remains `done`, unmodified, not reopened by this planning phase** —
original implementation plus three corrective passes
(`decisions/0073`/`0074`/`0075`) all closed out 2026-10-07/08; full
history in `planning/retros/phase-81-*.md` and `CHANGELOG.md`, not
repeated here per this file's own "history lives elsewhere" convention.

Central architecture is unchanged and remains approved: canonical
knowledge stays in `planning/knowledge/`, `context-graph.db` stays
mechanical-only, reconciliation stays detect → review → validated apply,
zero new persisted canonical fields.

Next concrete step: await explicit user approval of the committed Phase
81B plan (e.g. "Approve Phase 81B and implement the committed plan").
Only on that approval does implementation begin, starting with §6.3's
own isolation-mechanism investigation (the plan's own first concrete
implementation step).

---

**Phase 78's own exit decision has been corrected by amendment, 2026-10-02
(`decisions/0070`, direct user request, following a post-completion
review of `decisions/0069`).** Phase 78 itself (the trial's own
execution, evidence, and standard closeout sequence, narrated in full
below) remains `done` and is not reopened or re-run — only the exit
decision's own conclusion, drawn from that evidence, is corrected. The
original `CG-001` `not-recurred` rule relied on relative cost-parity
(treatment vs. baseline), not absolute materiality (would a plausible
relationship capability have actually avoided real, avoidable work) —
logically insufficient, since both arms could incur the same cost
precisely because the capability is missing. A fresh, independent
re-evaluation of the *existing* trial evidence (no re-run; full detail
`planning/reference-projects/ledgerkit/07-cg001-corrective-reevaluation.md`)
confirmed the one genuinely-existing relationship the trial actually
tested (`ReportSpec`/`ReportSection` ↔ `balance_from_spec`) still reads
`not-recurred` under the corrected rule, but found the trial's own
**applicability was only partial** — four of its five derived chain
links were proposed, not-yet-existing design work no capability could
ever discover. Per the corrective amendment's own decision structure, a
partial applicability finding is treated the same as inconclusive for
deciding Priority A's own exit question. **Priority A is reopened, not
closed**: further capability investment is not currently justified by
demonstrated marginal benefit — a materially weaker, more honest claim
than "the success criterion is met" — pending one additional, better-
targeted trial exercising only already-existing relationships, named
(not run) in `planning/phase-78-amendment-followup-plan.md`. `CG-001`
stays `candidate`, explicitly unaffected by this correction either way,
per a new symmetric evidence rule: a differently-shaped instance of its
own broader hypothesis tests the hypothesis at the track level only,
never this entry's own status, regardless of which direction its own
result reads. `decisions/0069` is superseded by `decisions/0070`,
preserved unedited as historical record. Full corrective detail:
`planning/retros/phase-78-amendment-corrective-exit-decision.md`.

---

**Phase 78 (Priority A backlog rationalisation + second Ledgerkit
validation trial) is `done`** (historical account below — see the
correction above for what has since changed). Direct
user request, 2026-10-02 ("Implement phase 78 plan"). §5's trial ran to
an applicable result: seed-then-fork Ledgerkit scratch clones,
fixture-equivalence confirmed clean, Stage 1 discovery/design comparison
(both arms independently derived the identical real `parser.py`→`Journal`→
`reports.py::balance_from_spec`→`cli.py` producer/consumer chain, clean
read-scope-symmetric boundary checks), Stage 2 independent
`context-evaluator` assessment — **PASS WITH GAPS, advantage LOW, `CG-001`
outcome not-recurred** on a confirmed-applicable task (CodeCompass's
existing surfaces genuinely cannot answer the relationship question —
`query relations` errors on both symbols, confirmed against the real
schema — but the treatment agent reconstructed the chain at no greater
cost than the baseline) — Stage 3 correctly not run (the evaluator's own
documented call). A second, independent `knowledge-curator` triage
re-verified this classification from scratch (not a rubber-stamp) and
confirmed **§7.2 Branch A fires: Priority A is closed as a strategic
capability-building track** (`decisions/0069`) — `CG-001` itself stays
`candidate`, unaffected in status, reopenable by new evidence of a
different, not-yet-tested shape; `CG-010`'s own independent maintenance-
backlog funding explicitly unaffected. Phase retro filed, two candidate
learnings triaged (`L-081` promoted into
`planning/v1-redefinition/reference-project-protocol.md` §2.2, `L-082`
retained), a docs-drift audit found NO DRIFT (one trivial citation-line
staleness fixed, unrelated to this phase's own findings). Independent
`release-phase-auditor` completion audit: **PASS WITH NON-BLOCKING
OBSERVATIONS** (`planning/retros/_audit-phase-78.md`) — one missing
durable artifact (`planning/retros/_drift-audit-phase-78.md`, the drift
audit's own work was genuine, only its report file was never persisted)
backfilled before this terminal reconciliation. Terminal
`roadmap-context-curator` reconciliation (this update) flips
`planning/ROADMAP.md`'s Phase 78 row to `done` and the plan file's own
Status line, per `CLAUDE.md` §5's narrow three-target exemption. Fully
closed; commits pushed to `origin` immediately after this reconciliation,
per §6. Full plan:
`planning/phase-78-priority-a-closeout-and-second-ledgerkit-trial.md`.
Retro: `planning/retros/phase-78-priority-a-closeout-and-second-ledgerkit-trial.md`.

---

**Phase 80 (CodeCompass-wide documentation reconstruction + lightweight
template refresh) is `done`** — direct user request, 2026-10-02,
approved to proceed directly into implementation, no planning
round-trip. Independent `release-phase-auditor` completion audit: first
pass **FAIL** on one finding (this file unsynced past Part 3, every
other claim independently re-verified accurate,
`planning/retros/_audit-phase-80.md`), fixed, re-audited **PASS**
(`planning/retros/_audit-phase-80-reaudit.md`). Terminal
`roadmap-context-curator` reconciliation (this update) flips
`planning/ROADMAP.md`'s Phase 80 row to `done` and the plan file's own
Status line, per `CLAUDE.md` §5's narrow three-target exemption. Fully
closed; commits for both repositories pushed to their own `origin`
immediately after this reconciliation, per §6. Full plan:
`planning/phase-80-codecompass-documentation-reconstruction.md`. Full
initiating prompt saved verbatim:
`planning/phase-80-documentation-reconstruction-prompt.md`. Retro:
`planning/retros/phase-80-codecompass-documentation-reconstruction.md`.

**Part 1 (two further Phase 79 defects, found by direct user review) is
done:**

1. `check_snapshot_completeness`'s identity/kind checks used a truthy
   guard (`if real_id and real_id != expected_id`) that silently skipped
   validation when historical content had no `id:`/`kind:` field at all.
   Independently reproduced in a disposable git fixture (an Assertion
   slot, then an Evidence slot, pointed at a plain identity-less
   committed file with its own correct historical hash — both produced
   zero findings pre-fix). Fixed via two new Finding rules
   (`knowledge-base-snapshot-identity-missing`/`-kind-missing`),
   generalized to the top-level assertion slot (which also gained a kind
   check it never had, and now reads historical content via `git show`,
   not the live file) and every nested Evidence/Derivation entry. Three
   new regression tests (34 total, up from 31). Committed `a1f12b3`.
2. `template-usability-exercise-2`'s `id-reuse-001` assertion
   overgeneralized its causal rule to "reuse depends on whether the
   most-recently-deleted task held the current maximum id." Both
   counterexamples named in the correction request were independently
   reproduced against the real pre-fix `_next_id`, directly disproving
   the rule (`add 1,2,3 → delete 2, then 3 → add` yields id `2`, not the
   rule's own predicted `3`; id `3` is never reused in that sequence at
   all). A reference model tracking every id ever assigned confirmed the
   real mechanism (`candidate = max(live)+1`, reuse iff ever-assigned-
   before) across 5 sequences with zero deviation, then survived an
   independent falsification attempt (18 self-designed sequences,
   several thousand operations, a CLI cross-check — found no
   counterexample). Corrected via `id-reuse-002.md` superseding
   `id-reuse-001.md` (dated correction notice, original preserved),
   corrected `docs/id-reuse.md` and `context-packet-fix-id-reuse.md`,
   and a new snapshot `id-reuse@v2.toml` — all as four real commits
   inside `template-usability-exercise-2`'s own git history (17 commits
   total, up from 13), re-bundled and replacing the preserved evidence
   in the main repo. Committed `024efcd`.

**Part 2, Stage 1 (freshness review + frozen project-wide snapshot) is
done.** A freshness review of all 28 Claim clusters backing
`docs/domain/`'s 19 concept pages found 17/19 fresh, found and fixed two
genuine staleness issues (`CL-ADPT-009` never superseded after Phase 74,
`relationship-edge.md`'s "six edge tables" count not accounting for
Phase 76's git-topology tables — both committed `e7eb22b`), then froze
`planning/knowledge/codecompass-domain/snapshots/snapshot-codecompass-overview-v1.toml`
citing all 25 active (non-superseded) Claims plus their full evidence/
derivation closure (committed `4965384`).

**Part 2, Stage 2 (model-blind implementation reconstruction) is done.**
A fresh `implementation-reconstructor` dispatch, isolated to a bounded
export (`cli.py`/`commands.py`/`config.py`/`sync.py`/`graph.py`/
`core.py`/`discovery.py`/`adapters/{base,python}.py` + tests, zero access
to any documentation), recovered the CLI command surface, the full
`graph.py` schema/migration/rebuild-determinism behavior (confirmed live
via 116/117 passing tests), and the adapter pattern — honestly
disclosing that `cli.py`/`sync.py`/the adapter layer could only be
reconstructed by reading, not running, since the bounded export wasn't a
runnable whole (deliberately excluded sibling modules). Mechanical
boundary-check (same method as Phase 79's fifth amendment) confirmed
best-effort isolation held — the only out-of-scope path referenced was
the dispatch's own disclosed scratch venv. Report:
`/tmp/.../scratchpad/phase80-implementation-reconstruction.md` (scratch,
not yet committed into the repo — will move into
`planning/knowledge/codecompass-domain/` at Stage 5 reconciliation,
matching Phase 79's own pattern).

**Part 2 (Stages 1-5) is done.** Stage 3 (comparison): 3 aligned, 8
partial, 14 insufficiently_verified, 0 conflicting, 0 not_implemented —
no real conflicts anywhere the snapshot and reconstruction actually
overlap (`4965384`→`7134f3e`). Stage 4: a fresh, isolated
`docs-reconstructor` dispatch wrote a complete 9-file documentation
draft from only the frozen snapshot + reconstruction + alignment
guidance (zero access to existing docs), staged at
`planning/phase-80-docs-draft/`, mechanical boundary-check clean
(`743df80`). Stage 5: reconciled the draft against the real live docs —
11 supported, 0 stale, 1 genuine gap found and fixed (`docs/cli-reference.md`
was missing a Haskell `when:`-block limitations bullet parallel to its
existing Python one, independently re-verified against
`discovery.py:90-109` before accepting), 0 obsolete pages to
redirect/remove (`911981f`). Confirms Stage 3's own "zero real
conflicts" finding — the existing documentation corpus was already
substantially accurate. Full test suite (767 passed, 2 skipped), `ruff
check .`, and both strict doc checkers clean throughout.

**Part 3 (lighter-weight `codecompass-template` application) is done.**
Read-through inspection alone wasn't trusted as proof of usability — a
genuinely fresh, context-free agent actually adopted the template into
both a new toy project and an existing one (its own pre-existing
README/Apache-2.0-LICENSE/CLAUDE.md with real rules). Found real,
concrete friction: `CLAUDE.md` wasn't named alongside README/LICENSE as
needing careful merge rather than blind overwrite (the adopter had to
invent a merge convention with nothing to check it against);
`docs/architecture.md` (copied into every adopting project) ended with a
first-person section describing the template repository's own
relationship to CodeCompass — copied verbatim, every adopter's
architecture doc would wrongly claim to itself be a template; the
"heavier, optional" clean-room workflow (7 template folders + 2 guides)
physically lived inside `planning/knowledge/`/`docs/`, the exact
directories the everyday adoption step says to copy, so "most projects
won't need this" was true in prose but not mechanically; no worked
example existed anywhere. All four fixed: explicit `CLAUDE.md` merge
guidance added; the self-referential section removed from
`docs/architecture.md` (content already existed, correctly scoped, in
`README.md`'s own License note); the whole heavier workflow moved to a
new top-level `optional-clean-room-workflow/` directory with its own
README explaining when to use it; two short worked examples added
(`docs/worked-example.md` for the everyday loop,
`optional-clean-room-workflow/worked-example.md` for the clean-room
loop). Pushed to the real `codecompass-template` remote: `68bae8e`.

**Part 4 (verification/closeout for both repositories) is done.** 15
reader questions frozen (`planning/phase-80-frozen-reader-questions.md`)
before evaluating anything, then verified against primary evidence: 13/15
CORRECT, 2/15 INCOMPLETE (no WRONG/AMBIGUOUS), both fixed (`README.md`'s
"What to commit" paragraph; `architecture/context-graph-schema.md`'s new
"Checklist for a new table" section). Separately, a bounded
coding-context packet (add `codecompass query source-stats`) was
independently assessed by `context-evaluator`: **FAIL, advantage LOW** —
a genuine, consequential finding, not softened to pass. Root cause
traced to a real helper-function conflation
(`_open_graph_or_note`/`_graph_session` vs. the actually-used
`_open_graph_if_exists`) originating in the Stage 2 reconstruction's own
summary prose, which had survived Stage 3's comparison and Stage 5's
reconciliation untouched because neither check's own evidentiary scope
covered that level of detail — corrected at the source in all four
affected Stage 2/4 draft files, and never reached the real published
docs. A follow-on docs-drift audit (scoped to everything this phase
touched) found one further real inaccuracy in the Part 4 README fix
itself (Skills/`/discovery`/`.mdc` rules were wrongly described as
gitignored, when this repository actually tracks and commits them) —
corrected (`672881d`). Documentation-accuracy and coding-context-
advantage reported as two separate, independently-run results
throughout, never merged into one verdict.

**Phase retro filed** (`planning/retros/phase-80-codecompass-documentation-reconstruction.md`,
`78fdf35`), naming the coding-context-packet FAIL as this phase's single
most important methodological result. Two candidate learnings
(`L-079`/`L-080`) triaged by `knowledge-curator` and **both promoted**:
`L-080` landed in `planning/agent-led-workflow.md` step 6 (never
construct a multi-line `git commit -m` message containing backtick-
quoted code identifiers as an interpolated shell string — discovered
mid-phase when exactly this corrupted a real commit, fixed via
`git commit --amend -F` before it reached `origin`); `L-079` landed in
`planning/v1-redefinition/context-quality-evaluation.md` §1 Ground rules
(a documentation-accuracy check and a coding-context-advantage check are
not substitutes for each other, since their own ground truth operates at
different levels of granularity) (`5344e5d`).

An independent `release-phase-auditor` completion audit against this
exact state (`5344e5d`) returned **FAIL** — one genuine, well-evidenced
blocking finding: this file (`planning/CONTEXT.md`) had not been synced
past Part 3's own completion (last synced `8ab50e0`), so its own
sections contradicted the phase's real, independently-re-verified final
state (every other Part 1-4 claim above was independently re-confirmed
accurate by that same audit, including re-cloning the exercise-2 bundle
to confirm 17 commits, re-reading `cli.py` directly to confirm the
packet-evaluation's central claim, and re-cloning `codecompass-template`
to confirm the push). That fix (`2acd63b`) was re-audited and returned
**PASS** with no further findings (`planning/retros/_audit-phase-80-reaudit.md`),
after which the terminal `roadmap-context-curator` reconciliation above
flipped the phase to `done`.

---

**CodeCompass v1.0.0 is released.** The redefined-v1 milestone group
(`decisions/0048`, Phases 0–70) is complete and closed: published to
PyPI as the `codecompass-context` distribution (CLI command and Python
import package both stay `codecompass`), tagged `v1.0.0`. Current-state
description of what CodeCompass does: `README.md`,
`architecture/module-map.md`, `docs/quickstart.md` — not this file.
Full status: `planning/ROADMAP.md`. Closeout record:
`planning/v1-closeout.md`.

Post-v1 work is organised into six priorities (A-F,
`planning/ROADMAP.md`'s "Post-v1 priorities" section, `decisions/0062`),
not lettered stages. Priority A's first concrete deliverable
(Phase 73, `CG-006`), Priority B's first hardening step (Phase 74,
`L-031`/`L-032`), and Priority A's first real-task validation trial
(Phase 75) are all **done**, audited, and closed.

**Phase 76 (Git repository topology awareness, Priority A) is `done`,**
including its same-day post-closeout corrective pass (three real
defects found and fixed, fresh drift audit **NO DRIFT**, fresh
`release-phase-auditor` **PASS WITH NON-BLOCKING OBSERVATIONS**). Fully
closed and pushed to `origin`; no further action needed. Full history in
`planning/retros/phase-76-git-repository-topology.md` and prior
`CONTEXT.md` git history if needed.

**Phase 77 (First-party source awareness (`CG-009`) + a usable
`codecompass-template`, Priority A + Priority D) is `done`,** including
its independent `release-phase-auditor` completion audit (**PASS**,
`planning/retros/_audit-phase-77.md`, against final HEAD `d74ee47`) and
its terminal `roadmap-context-curator` reconciliation. Fully closed and
pushed to `origin`.

**Phase 78 (Priority A backlog rationalisation + second Ledgerkit
validation trial) is `planned`, direct user request, 2026-09-29, amended
same day — planning only, not yet implemented.** The amendment fixed six
real issues in the first draft: an exit-gate contradiction
(`task-not-applicable` was wrongly treated as equivalent to
`not-recurred` for closing Priority A — now evidence-neutral, triggers a
re-run via a new applicability gate, §7.2.0), a `CG-010`/Priority-A-closure
inconsistency (now resolved by an explicit strategic-closure-vs-
maintenance-backlog distinction, §3.1), a trial-design confound (both
arms independently inventing different implementation contracts and
comparing the implementations, not the context — restructured into a
discovery/design comparison, an independent evaluation, and an optional
shared-contract implementation check, §5.3), a missing observable-
evidence requirement (both arms' reports must now record files read,
queries run, commands executed — never private chain-of-thought, §5.3.4),
residual pre-judgment of the trial's own likely result (removed, §1), and
imprecise evaluation terminology (`internal` exposure is not uncertainty;
an omission is a completeness gap, not automatically a safety failure,
§6). Full amendment log: the plan's own §13.

Audits every still-open Priority A item/context gap
(`CG-001`/`CG-003`/`CG-007`/`CG-010`/`CG-011`, Phase 24/25/50) and
dispositions each against real evidence; designs (does not run) a second,
differently-shaped Ledgerkit trial against a genuine,
currently-unimplemented Stage D task (journal-comment `ReportSpec`
parsing, verified live as `[DEFERRED — Milestone 3]` in Ledgerkit's own
`dev-docs/api-spec.md`), specifically to test whether `CG-001`'s
first-party-relationship hypothesis (Phase 77's own explicitly-deferred
follow-on, §13 of that plan) is a real blocker before any such capability
is built. This is the second, differently-shaped Priority A Ledgerkit
trial Phase 75's own closeout recommended and Phase 77's own plan
explicitly deferred (precedes, does not replace) — now finally claimed
and scoped, not abandoned. Full plan:
`planning/phase-78-priority-a-closeout-and-second-ledgerkit-trial.md`.

**Phase 79 (Clean-room conceptual understanding + documentation
reconstruction, methodology hardening + Priority D template delivery) is
`done`** (direct user request, 2026-09-30, amended six times,
`decisions/0066`/`decisions/0067`/`decisions/0068`, approved 2026-10-01
and executed the same day). The phase's own prior terminal `done` flip
is not reopened by any of this — each amendment corrects that
already-`done` result's own output in place. A **fifth amendment**
(`decisions/0067`), landed the day after the original `done` flip via
direct review of the delivered result, implemented four further
corrections: snapshot validation now genuinely fails closed against a
minimal-content fixture (not merely against entries already present in a
table), previously-dropped documentation citations were restored and
content-matched, the Track 2 isolation verdict was corrected with real
new mechanical evidence (a boundary-check script run against all six
original pilot dispatches' own still-extant transcripts, finding one
real, previously-undetected boundary deviation), and the template
usability "exercise" — previously only a link-integrity check — was
replaced with a real downstream adoption attempt by a fresh,
context-free agent (found and fixed a real `README.md`/`LICENSE`
collision in the adoption instructions, pushed to the real
`codecompass-template` remote). An independent `release-phase-auditor`
audit of this fifth amendment
(`planning/retros/_audit-phase-79-fifth-amendment.md`, against
`b95a1f1`, re-confirmed in an appended addendum against the amendment's
own final commit `0e1c63a`) returned **Track 1 (workflow/template
completion): PASS WITH NON-BLOCKING OBSERVATIONS** — two trivial
narrative-only gaps (a "13 new tests" miscount, actually 11;
`CONTRIBUTING.md` not yet mirroring `CLAUDE.md`'s new `L-070` sentence)
were both fixed in the immediately following commit (`0e1c63a`) and
re-confirmed closed by the audit's own addendum. **Track 2 (strict
clean-room isolation validation) was, at that point, confirmed and
honestly reported as `UNMET`** — not a defect, the amendment's own
intended outcome: honest `best-effort` labelling throughout is not the
same as strict isolation actually being achieved; see
`planning/knowledge/first-party-source-symbols/isolation/isolation-evidence-inventory.md`
for the real, mechanically-derived evidence behind this verdict.

A **sixth amendment** (`decisions/0068`), landed the same day as the
fifth via direct, independent reproduction of three further defects in
that amendment's own delivered result, implemented three corrections:
(1) **nested snapshot-entry validation gaps closed** —
`_validate_nested_entries` (`scripts/check_knowledge_base.py`) now
closes `check_snapshot_completeness`'s Evidence/Derivation checks
against validated ids rather than raw dict keys, catching malformed
nested entries (scalars, identity swaps, kind mismatches, empty dicts,
and whole-table-shape errors) that previously passed silently; (2) **a
false conceptual claim corrected** — `task-ids-001`'s "ids are never
reused" claim was independently reproduced false (a just-deleted
current-maximum id is in fact reused by the next `add`) and fixed via
dated correction notices preserving the original, incorrect text as
historical record across the assertion, `docs/task-ids.md`,
`decisions/0001`, and the snapshot sidecar; (3) **a complete,
commit-permitting template exercise** replaced the fifth amendment's own
no-commit limitation — a fresh disposable repository with a verified
13-commit git bundle, a real persisted-`next_id` counter fix, and a
passing test suite (5 tests, including 3 new regressions), finding no
new template usability defect. An independent `release-phase-auditor`
audit of this sixth amendment
(`planning/retros/_audit-phase-79-sixth-amendment.md`, against
`9982d22`) returned **Track 1 (workflow/template completion): PASS WITH
NON-BLOCKING OBSERVATIONS** — one trivial, accepted-as-is observation
(two compiled `.pyc` files tracked in the disposable exercise's own
bundle history, explicitly not a defect in the corrections or in
CodeCompass's own source) — and **Track 2 (strict clean-room isolation
validation): UNMET**, honestly and correctly re-confirmed rather than
newly assessed; this is the fifth amendment's own established verdict
holding, not a new gap. This terminal reconciliation (this commit) is
the sixth amendment's own closeout — the phase's `done` status on
`planning/ROADMAP.md` is unchanged by it. Does not touch, reorder, or
depend on Phase 78. Fully closed and pushed to `origin`. See "What was
just completed" below for the pre-fifth-amendment delivered result; the
summary immediately following this paragraph describes the
pre-implementation, fourth-revision plan and is retained for its own
amendment history, not as a description of current state.

**Revised objective (unchanged since the first amendment)**: one
evidence-backed knowledge foundation supplies both coding context and
project documentation — conceptual understanding is incorporated
directly into documentation, mechanical context separation is preserved.

**Third-revision corrections, same day, found by direct technical
inspection before any implementation began:**

1. **Isolation verification was too weak; completion criteria now split
   honestly.** A single self-reported failed read is not proof of a
   boundary — replaced with observed (raw tool-call transcript, not
   self-report) probes across filesystem, search, command, network, and
   delegation routes. **Most consequential finding: CodeCompass is a
   public GitHub repository, so network egress through a granted `Bash`
   can reach the "excluded" narrative content regardless of local
   filesystem isolation** — omitting `WebFetch`/`WebSearch` does not
   close this. Tier 2 (same-host export) is now *always* `best-effort`,
   never upgraded by an incidental probe result. The Definition of Done
   is split into two separately-reported tracks: workflow/template
   completion (fully satisfiable) and strict clean-room validation
   (honestly expected to remain **unmet** for the network dimension) —
   removing the human-review gate does not relax this.
2. **The pipeline was circular** — comparison needed "published
   documentation," writing needed that plus comparison, publication
   happened only after writing. Replaced with a linear chain: canonical
   assertions → a new **frozen knowledge snapshot** (versioned, hash-
   integrity-checked, cited as `<topic-slug>@v<N>#<id>`) → independent
   implementation reconstruction (model-blind — no access to the
   snapshot at this stage) → comparison → documentation architecture/
   draft (comparison and writing are what actually consume the
   snapshot, not not-yet-existing prose) → legacy reconciliation →
   publication. Understanding still lands directly in the final
   published documentation — once, at the real end of the chain.
3. **Dependency validation was verified false, not merely restated.**
   Direct, empirical testing confirms `scripts/check_knowledge_base.py`'s
   parser cannot see a YAML *block*-style list — `depends_on:` in that
   form parses as empty, silently passing validation with zero ids
   checked. The inline `[a, b]` form (this project's own universal
   existing convention) works correctly. This project's own prior claim
   that `depends_on` "already validates with zero code change" is
   corrected: true for inline, false in general — a new check now rejects
   the block form outright.
4. **Alignment no longer auto-promotes to `verified`.** An `aligned`
   comparison finding is recorded in the alignment report only — moving a
   Claim to `verified` needs its own claim-specific check against primary
   evidence, since implementation conformance never by itself proves a
   domain rule or proposed policy is correct.
5. **Coding context is now independently validated, not just cited.** A
   frozen, bounded task generates a real packet from the same snapshot
   the documentation uses; a fresh `context-evaluator` dispatch assesses
   it with this project's own existing `context-quality-evaluation.md`
   rubric (LOW/MODERATE/HIGH advantage) — reused, not invented.
6. **The propagation demonstration now runs in a disposable fixture**,
   deleted afterward — never leaving a synthetic `CONTROLLED TEST`
   contradiction in real canonical knowledge or real published
   documentation. Propagation also now starts from a changed *source
   file* (via Evidence's own citation fields), not an assertion already
   identified by hand, and the transitive `depends_on` walk is explicitly
   cycle-safe.

Everything else (the schema's field set minus `human_review_state`, the
`implementation-reconstructor` role, the draft-before-reconciliation
ordering, the Priority-B boundary, the validation topic) carries forward
unchanged. **Explicitly not Priority B** (no `src/codecompass/` change at
all). Full plan:
`planning/phase-79-clean-room-understanding-and-documentation-reconstruction.md`.

See "Next concrete step" below.

Backlog, each with its own revisit trigger: Phases 24/25, Phase 50's
remainder, `CG-003`, `CG-007`, `CG-011`, the `browser_api`/`platform_api`
kind — full detail `planning/pre-v1-disposition.md` and Phase 78's own §3
disposition table. `CG-010` is tracked separately as already-evidenced,
ready-to-fund Git-topology maintenance backlog (Phase 78's own §3.1) —
not waiting on a revisit trigger, and not gated on Priority A's own
strategic exit decision either way.

## What was just completed

**Phase 81 was reopened for a corrective pass the same day it was first
closed `done`**, direct user request, following post-completion review
that found real defects outside the original audit's own scope. See
"Current phase" above for the full list of nine corrections underway.
The original implementation/retro/audit are preserved unedited as
history, not superseded wholesale — only the specific defective
behaviours are being corrected.

**Phase 78's exit decision — corrected by amendment.** Priority A's
original closure (`decisions/0069`) is superseded by `decisions/0070`:
reopened, not closed, after a fresh independent re-evaluation of the
existing trial evidence found the original `CG-001` rule logically
insufficient and the trial's own applicability only partial. See
"Current phase" above for full detail. `CG-001` stays `candidate`,
unaffected either way, under a new symmetric evidence rule. A narrowly-
scoped follow-up trial candidate is named (not run) for review:
`planning/phase-78-amendment-followup-plan.md`. Phase 78 itself remains
`done` — its own trial execution, evidence, and closeout sequence are
unaffected and not reopened.

**Phase 80 (CodeCompass-wide documentation reconstruction + lightweight
template refresh) — `done`, fully closed.** See "Current phase" above
for full detail on all four parts, including the first completion-audit
pass's one real finding (this file unsynced past Part 3), its fix, and
the clean re-audit `PASS` that followed. Full test suite (767 passed, 2
skipped), `ruff check .`, and both strict doc checkers clean throughout
the whole phase. Retro filed; both candidate learnings (`L-079`/`L-080`)
promoted and landed. `planning/ROADMAP.md`'s Phase 80 row flipped to
`done` by the terminal reconciliation; commits pushed to `origin` for
both repositories.

**Separately, a new unscheduled backlog item was recorded** (direct user
request, 2026-10-02, planning-only, no implementation):
`planning/strict-isolation-for-documentation-reconstruction.md` —
strict mechanical isolation for the clean-room documentation-
reconstruction methodology's isolation-sensitive stages, linking rather
than duplicating the existing Tier-1-failed/Tier-2-best-effort isolation
evidence (`decisions/0066`, `planning/knowledge/first-party-source-symbols/isolation/`).
Cross-referenced from `planning/ROADMAP.md`'s Priority D row and its
"Backlog, not absorbed into A-F" table. Does not gate or reopen Phase
78, 79, or 80.

**Phase 79 — Clean-room conceptual understanding + documentation
reconstruction — `done` (historical; see above for Phase 80's own
corrections to two of its downstream artifacts).**

Four checker functions landed in `scripts/check_knowledge_base.py`
(`check_optional_enum_fields`, `check_list_fields_are_inline` — fail-
closed, immediately found and fixed 15 real pre-existing YAML
block-list violations — `check_snapshot_historical_integrity`,
`check_snapshot_current_divergence`), 14 new tests, all passing
(`b42e6c8`/`38c8d7a`-range). New agent role `implementation-reconstructor`
plus extensions to `domain-skeptic` (comparison mode), `context-researcher`
(isolated mode), `docs-reconstructor` (hardened topic-scoped route),
`docs-maintainer` (legacy reconciliation mode), and
`planning/v1-redefinition/agent-led-development.md`'s own catalogue/
write-boundary table.

A live Tier-1 isolation preflight (`Agent(isolation: "remote")`) was run
for real and **failed all five tested routes** in this environment —
filesystem, search, command, network, and environment-identity all
reached content it was supposed to exclude (a same-host git worktree,
not a separate environment). Every downstream stage used Tier 2 and is
labelled `best-effort`, never `verified`, accordingly
(`planning/knowledge/first-party-source-symbols/isolation/tier1-preflight.md`).

Validated end to end on the real pilot topic (Phase 77's first-party
source/symbol subsystem, previously undocumented): 8 reviewed Claims
(`context-researcher` → `domain-skeptic` adversarial review, which
independently resolved all five of the research dispatch's own disclosed
open questions), a frozen-then-re-frozen snapshot (v1→v2, both with
passing historical-integrity/zero-divergence checks against real git
history), a model-blind `implementation-reconstructor` report (one
export-curation bug found and fixed mid-phase, disclosed rather than
silently corrected), a fresh comparison-mode `domain-skeptic` alignment
pass (promoted one Claim to `verified` via a real separate check, found
one genuine new knowledge-base gap), a disposable propagation-
demonstration fixture proving the full source→evidence→assertions→
transitive-dependents→snapshots→both-outputs chain including real
two-node cycle-safety (deleted afterward, zero survivors), published
documentation merged into `architecture/overview.md`/
`architecture/context-graph-schema.md` (not a new `docs/domain/` page —
that corpus turned out to be a separate, already-approved one for
CodeCompass's own meta-level concepts, not implementation subsystem
detail), a legacy-reconciliation pass (all 7 pre-existing claims
`supported`, one real documentation-verification gap fixed directly),
and two independent verification passes — one (coding-context packet)
**PASS, LOW advantage**; one (documentation Q&A) **5/6 confirmed, 1/6
wrong-and-fixed** (a real, pre-existing `core.Ecosystem`-cardinality
defect in `architecture/overview.md`, unrelated to this phase's own new
content, caught only by this independent check).

Nine portable workflow/guide templates delivered to
`https://github.com/ctosullivan/codecompass-template` and pushed
(confirmed via `git log origin/main..HEAD` empty), verified via a fresh-
clone link-integrity check before pushing.

Full test suite: 747 passed, 2 skipped. `ruff check .`: clean.
`check_knowledge_base.py --strict` / `check_user_docs.py --strict`:
clean (one expected, disclosed informational snapshot-divergence
finding). Retro: `planning/retros/phase-79-clean-room-understanding-and-documentation-reconstruction.md`.
Learning triage landed `L-068`/`L-069`, refined `L-023`. A docs-drift
audit found and fixed 4 non-blocking findings (a stale line-citation in
`docs/domain/concepts/claim.md`, two `agent-led-development.md` staleness
gaps, `CONTRIBUTING.md`'s incomplete agent roster) — persisted at
`planning/retros/_drift-audit-phase-79.md`.

An independent `release-phase-auditor` audit against the pre-CHANGELOG/
pre-CONTEXT.md-update commit (`cbf3582`) returned **Track 1 (workflow/
template completion): FAIL** — three real gaps (no `CHANGELOG.md` entry,
this file not updated past the pre-implementation plan state, no
persisted `_drift-audit-phase-79.md`) — and (at the time) reported
**Track 2 (strict isolation validation): "PASS"**, language a fifth
amendment the same day corrected: that audit genuinely confirmed the
`best-effort` labelling was honest throughout, but honest labelling of
an unenforced boundary is not the same as strict isolation being
achieved — the corrected verdict is **Track 2: UNMET**, unaffected by
and independent of any Track 1 fix (see the isolation-evidence-inventory
document cited above). All three Track 1 gaps were fixed (`d9b9175`). A
re-audit against `d9b9175` (`planning/retros/_audit-phase-79-reaudit.md`)
returned **Track 1: PASS** (all three fixes independently verified
genuinely closed, not merely present) and reconfirmed the same Track 2
language, since corrected identically; two further trivial, non-blocking
observations (the `claim.md` citation off-by-2, this file's own
duplicated Phase 78 paragraph) were fixed in the following commit
`a119f4c`. A fourth-revision terminal `roadmap-context-curator`
reconciliation then flipped `planning/ROADMAP.md`'s Phase 79 row to
`done`. The fifth and sixth amendments described above, and their own
respective terminal reconciliations, followed afterward and corrected
that already-`done` result's own output in place — see the "Current
phase" section above for their full detail; the phase's `done` status
itself has not changed since.

**Phase 77 — First-party source awareness (`CG-009`) + a usable
`codecompass-template` — `done`.**

Implementation (`03f8519`): new `source_files.language`/`content_hash`/
`symbol_index_status`/`symbol_index_diagnostic` columns (nullable
identically on fresh or migrated databases, `_migrate_source_files_columns`,
`ALTER TABLE ADD COLUMN` only — `source_files.id` is referenced by
`uses_edges ON DELETE CASCADE`); a `Language` concept (python/rust/
javascript/typescript/haskell) deliberately distinct from `core.Ecosystem`
(whose single `npm` value cannot distinguish JS from TS); new
`source_symbols` table with occurrence-based identity
(`UNIQUE(source_file_id, name, kind, line)`, `line NOT NULL`) after
live-verifying a name-only key crashes real `sync` on genuine function
overloads (Python `@typing.overload` and TypeScript both reproduced); a
five-value `exposure` (public/restricted/internal/conventional_private/
unknown, live-verified against 8 real Rust visibility forms); a new
`source_symbols.py` module; `codecompass query source`/
`query source-symbol`; `meta.source_index_version` distinguishing
never-indexed from indexed-but-empty; `decisions/0065`.

`codecompass-template` (`https://github.com/ctosullivan/codecompass-template`,
confirmed empty at plan time) is now **populated and pushed to its own
real remote**, cross-linked from `README.md`/`ai-docs/README.md`
(`5993113`).

Three real validations persisted: the template repository's own clean
clone (zero-vendor acceptance test), Ledgerkit, and CodeCompass's own
dogfooding (`planning/reference-projects/codecompass-self/phase-77-validation.md`,
`planning/reference-projects/ledgerkit/05-phase-77-first-party-source-validation.md`,
`910fb35`).

An independent Priority A task-context evaluation was persisted for both
reference projects — verdict **PASS WITH GAPS, advantage LOW**
(`planning/reference-projects/codecompass-self/phase-77-context-evaluation.md`,
`planning/reference-projects/ledgerkit/phase-77-{fixture-equivalence,baseline-report,treatment-report}.md`,
`b473e84`, `f75bd99`).

`CG-009` was reassessed and resolved by independent `knowledge-curator`
triage, re-verified by direct code reading (not taken on the entry's own
or `context-evaluator`'s word) — **promoted-to-roadmap**
(`planning/context-gaps/inbox.md`, `5398eb3`).

Independent `docs-reconstructor` drift audit ran twice: the first pass
found three real findings (stale migration count, incomplete CORE module
list, incomplete exposure enumeration), all fixed (`04b87c2`); the
re-audit confirmed **NO DRIFT** (`planning/retros/_drift-audit-phase-77.md`,
`490ce4d`). An independent `domain-skeptic` citation-currency review of
five `docs/domain/` pages found stale citations; all fixes applied
(`68e80b3`, `41ed6aa`).

A phase retro exists
(`planning/retros/phase-77-first-party-source-and-template.md`, `4fb9483`).
Two new learnings triaged: `L-066` (confirms `L-064`'s already-landed
`agent-led-workflow.md` fix worked cleanly on its first real exercise —
**discarded**, no new gap) and `L-067` (two schema/plan-design
heuristics from the second plan amendment — binary-first-guess is often
wrong for a cross-language concept; live-verify a natural key against
ordinary real code before committing to schema — real and evidenced but
single-phase, **retained** as a candidate, not yet promotable to one
specific artifact) (`planning/learnings/inbox.md`, `f92d3f2`).

Independent `release-phase-auditor` completion audit against final HEAD
`d74ee47`: **PASS** (`planning/retros/_audit-phase-77.md`), all 17
checked conditions held with real, independently-gathered evidence
(full 733-passed/2-skipped test run, `ruff check .` clean, both doc-check
scripts clean, the prior FAIL audit's own trip-wire defect confirmed
genuinely fixed, schema/ADR/docs cross-checked directly against live
code, the real `codecompass-template` repository independently confirmed
via the GitHub API, protected-file boundaries and commit hygiene clean,
no scope creep, scratch clones confirmed cleaned up), independently
re-confirmed by this `roadmap-context-curator` reconciliation. Full plan
(amended twice): `planning/phase-77-first-party-source-and-template.md`.

**Phase 76 — Git repository topology awareness (worktrees + submodules)
— `done`,** including its same-day post-closeout corrective pass (three
real defects found and fixed; fresh `docs-reconstructor` audit **NO
DRIFT**; `L-065` **promoted**; fresh `release-phase-auditor` **PASS WITH
NON-BLOCKING OBSERVATIONS**, `planning/retros/_audit-phase-76-corrective.md`).
Fully closed and pushed to `origin`. Full history:
`planning/retros/phase-76-git-repository-topology.md`.

**Phase 75 — Priority A Ledgerkit validation — `done`.** Real-task
evaluation (hledger's `cur:` query term in Ledgerkit's own query
engine); `context-evaluator` verdict **PASS WITH GAPS, advantage LOW**;
`CG-001` stayed `candidate`; `CG-009` filed (now resolved by Phase 77
above). Full report:
`planning/reference-projects/ledgerkit/04-cur-query-priority-a-validation.md`.

## Known standing gaps (current-state facts, not phase history)

- Cargo adapter (`decisions/0014`) never validated against real `cargo
  metadata` output or a real crate — no Rust toolchain available yet.
- `extract_npm_symbols` untested against real-world `.d.ts` authoring
  styles beyond hand-written fixtures.
- `chat.py` never run against the real Anthropic API in this
  environment.
- `staleness.py`'s version parser has no real PEP 440/semver
  correctness — string comparison only.
- No formal trigger-accuracy evaluation harness for per-vendor Skills.
- Cursor `.mdc` export has no `globs` field.
- A pre-Phase-74 `symbol_enrichment` row's producer remains honestly
  unknown (`NULL`) — new rows are attributed, historical ones cannot be
  retroactively.
- A submodule pin/checkout mismatch has no field distinguishing
  committed-parent-state divergence from purely local uncommitted
  checkout state (`CG-010`, filed Phase 76) — `codecompass query
  topology` gives the two SHAs and a match/mismatch verdict, but
  determining *why* they differ still requires `git status`/`git diff
  --cached` directly.
- A sibling worktree's dirtiness, when unprobed/stale, is honestly
  reported as such but carries no inline CLI signal that this could be
  the case — only `--help` text documents the sync-time-snapshot
  guarantee (`CG-011`, filed Phase 76).
- `vendor/` and a local `.venv/` exist in this checkout (both
  gitignored, freely regeneratable) — live artifacts, not fixtures.

## Next concrete step

**Phase 81's corrective pass: implementation, tests, and real dogfood
validation are complete** (`decisions/0073`, `planning/retros/phase-81-corrective-pass.md`).
`codecompass-template`'s delivery item (point 9) is also resolved — the
public `ctosullivan/codecompass-template` repo was confirmed to still
lack the work, and it was pushed successfully via the repo's own SSH
remote (HTTPS had no stored credentials), verified by a fresh fetch.
**Still outstanding before Phase 81 can be marked `done` again**: a
fresh per-phase docs-drift audit, learning/context-gap triage for any
new candidates this pass surfaces, and a fresh independent completion
audit against the corrected HEAD — none of these have run yet.

**Phase 80 is `done`, fully closed.** `planning/ROADMAP.md`'s Phase 80
row and this file's own "Current phase" section were both flipped in the
same terminal reconciliation commit. No further action needed on Phase
80 itself.

**Phase 78 itself is `done`, fully closed and unaffected by this
correction.** Its own exit decision has been corrected by amendment
(`decisions/0070`, see "Current phase" above) — Priority A is now
**reopened**, not closed. The next concrete step for Priority A is a
human/lead decision on whether to approve and run the narrowly-scoped
follow-up trial sketched (not started) in
`planning/phase-78-amendment-followup-plan.md` — an existing-relationship-
only task (Ledgerkit's own `stats` query-support extension), designed
specifically to avoid repeating the original trial's own partial-
applicability flaw. Not approved, not scheduled, no phase number
assigned.

Per `CLAUDE.md` §6, Phases 75, 76 (including its corrective pass), 77,
78, 79, and 80 are fully closed and pushed to `origin` — no further
action needed on any of them. Phase 78's own corrective-amendment
commits are **not yet pushed** — pending this amendment's own DoD gate
(an independent audit of the corrective decision itself).

**Phase 78's own closure leaves no active roadmap phase in progress.**
The next open item requiring a decision is Priorities B/C/E/F (all
`decisions/0062`'s own "not yet planned" state, unaffected by Priority
A's own closure) — none currently claimed by a drafted plan.

A new unscheduled backlog item (`planning/strict-isolation-for-documentation-reconstruction.md`,
recorded 2026-10-02) is **not** a next concrete step to execute — it is
`candidate, not funded, not scheduled`, revisited only on a third
independent recurrence of the same isolation gap or a genuinely separate
execution substrate becoming available, per its own "Suggested priority"
section.
