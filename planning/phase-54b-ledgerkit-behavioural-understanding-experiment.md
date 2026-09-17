# Phase 54b: LedgerKit reference/behaviour validation — plan

**Status:** plan only, not started. Do not begin implementation until
this plan is reviewed (per this project's own established two-step
pattern — Phase 54 itself was planned in one session and implemented
only after a separate "Implement the plan" instruction). Full verbatim
request:
`planning/phase-54b-ledgerkit-behavioural-understanding-prompt.md`.

Phase 54b already existed as a claimed-but-undetailed bridge phase
(`planning/v1-redefinition/roadmap.md`, claimed 2026-09-17,
`decisions/0056`) — the "External executable / behavioural context"
sketch (`ledgerkit-plan.md` §"Phase 54 — Behavioural / executable
test") finally given a number, but never turned into a `CLAUDE.md` §1
plan file. This document is that plan, written now because real new
evidence landed since the phase was claimed: Ledgerkit's **Stage C
Phase 5** (`17d7bcb`/`e8f3633`/`c6168b2`, done 2026-09-17, confirmed live
— Ledgerkit's `HEAD` and `origin/main` both at `c6168b2`) is a complete,
real, independently-verified behavioural investigation of hledger's
`depth:` query term, materially richer than the evidence available when
Phase 54b was first claimed (which only had Phase 2's incomplete,
Phase-1-superseding classification to point at).

## 0. Why this plan supersedes the existing one-paragraph placeholder

The current `roadmap.md` Phase 54b stanza says: use
`LK-COMPAT-QUERY-DEPTH-001`'s "manual/source/executable three-evidence
structure, already inspected during Phase 54/55b" to test relating a
provenance chain. That stanza was written against **Stage C Phase 2's**
classification (`intentional_divergence`/`incomparable` — hledger
truncates, Ledgerkit excluded) — already superseded. Stage C Phase 5
went materially further: it redesigned `depth:` to match hledger, and in
doing so produced exactly the kind of rich, multi-entry-point
behavioural evidence chain this phase should actually be testing
against, not an incidental byproduct of a fix that happened to also
generate compat-register YAML.

## 1. Ground truth, re-derived from primary sources (not from a summary)

Read directly from Ledgerkit's own committed material — `dev-docs/
planning/core-redefinition/21-stage-c-phase-5-depth-and-verification-plan.md`,
`dev-docs/compat-register/LK-COMPAT-QUERY-DEPTH-001.yaml`,
`LK-COMPAT-QUERY-DEPTH-STATS-001.yaml`, and
`dev-docs/retros/STAGE-C-PHASE-5.md` — not from this prompt's own
paraphrase of them.

### 1.1 The behaviour itself: one query term, five commands, three distinct outcomes

| Command | hledger's actual `depth:`/`--depth` behaviour |
|---|---|
| `balance` | Clips/truncates + aggregates display names. Never excludes postings. `depth:0` produces a single `"..."` row netting to zero, not an empty result. |
| `register` | Same clip-not-exclude behaviour; every posting still shown, account label truncated. |
| `accounts` | Deduplicates and clips the account list (a list-shrinking side effect of clipping, not a filter). |
| `print` | **Fully depth-blind.** `EntriesReport.hs` strips `Depth` from its filter and never calls any clip function at all — depth is consulted nowhere in this command's code path. |
| `stats` | **Genuinely exclusion-based** — the one real, source-confirmed exception. `Ledger.hs`'s `ledgerFromJournal` builds the account tree from depth-unfiltered postings (matching every other command) but *separately* filters the journal `stats` reads its own counts from using the raw `Depth`/`DepthAcct` boolean predicate — a real, doc-commented, deliberate divergence in hledger's own source, not an inconsistency Ledgerkit introduced. |

Three genuinely distinct behaviours (clip / exclude / ignore) across five
commands sharing one query term — this is the "command-specific
exception" structure the governing prompt names, and it is real,
already-independently-verified fact, not a constructed scenario.

### 1.2 The premature-conclusion failure this experiment specifically re-creates

Stage C **Phase 1** (source-reading only, no executable check) read
`hledger-lib/Hledger/Query.hs`'s `matchesAccount (Depth d) a =
accountNameLevel a <= d` — a real function, correctly type-checked,
genuinely exercised by hledger's own unit tests — and classified
Ledgerkit's exclusion-based `Depth` AST node as `compatible`/
`equivalent` on that single piece of evidence. This was wrong: **no
shipped hledger command ever calls that predicate for selection.**
Every one of six report-generating modules
(`Reports/MultiBalanceReport.hs`, `Reports/PostingsReport.hs`,
`Reports/EntriesReport.hs`, `Cli/Commands/Accounts.hs`,
`Reports/AccountTransactionsReport.hs`, `Data/Ledger.hs`) strips
`Depth`/`DepthAcct` out of the query used to select postings *before*
using it, and instead re-derives a separate `DepthSpec` for display
purposes only. Phase 1's mistake was reading one function's signature
and treating it as *the* semantics of `depth:`, without tracing whether
any real command path actually invokes it that way — none do. Stage C
Phase 2 (the first executable check) caught the surface symptom
(exclusion vs. truncation); it took Stage C **Phase 5**'s full six-file
source trace to explain *why*, and to discover `stats`' own genuine
exception, which Phase 2's own testing never touched.

**This is a real, dated, independently-verified instance of exactly the
failure mode the governing prompt asks Phase 54b to test for** —
reaching a locally-plausible-but-wrong conclusion from one piece of
source evidence, correctable only by tracing every consumer, not by
reading more carefully at the same spot.

### 1.3 The evidence-chain shape Ledgerkit's own process already uses

Each affected compat-register entry (`LK-COMPAT-QUERY-DEPTH-001`,
`LK-COMPAT-QUERY-DEPTH-STATS-001`) already carries, as plain YAML
fields, exactly the evidence categories the governing prompt names:

- **documentation** — `evidence: [{kind: manual, ref: "hledger.1:7054-7098, 7324-7332", pinned_at: "1.52.4"}]`
- **implementation paths (upstream)** — `evidence: [{kind: source, ref: "<6 files, exact line ranges>", pinned_at: "<commit sha>"}]`
- **observed executable behaviour** — `evidence: [{kind: executable, ref: "<fixture + exact commands run>", pinned_at: "<pinned binary version>"}]`
- **Ledgerkit's own implementation** — the entry's `implementation:` list (`ledgerkit/query/depth.py`, `reports.py`, etc.)
- **independent verification** — a second `executable` evidence item explicitly labelled as `compat-differential-tester`'s own separate dispatch, plus `status: verified` / `verified_by`

Nothing here needs a new CodeCompass concept to *describe* — this is
free-form YAML prose Ledgerkit already writes by hand. What Phase 54b
tests is whether CodeCompass can help an agent **assemble** this shape
for itself from primary sources, and whether doing so with CodeCompass's
help produces a more execution-path-complete result than doing it
without.

## 2. Refined objective (replaces the placeholder's "test relating a provenance chain")

**Not**: can CodeCompass mechanically relate an already-written
provenance chain to itself. **Instead**: does CodeCompass's context help
an agent, working the `depth:` question fresh, (a) find *all* the
materially relevant behavioural entry points before concluding anything,
(b) avoid Phase 1's own specific mistake (stopping at one plausible
function), and (c) assemble a behavioural claim with the evidence
categories in §1.3 — using only existing CodeCompass mechanisms
(detection, relation, the observation/gap queues), not a new one built
for this experiment.

## 3. Why this is a genuine task, not an invented benchmark

`reference-project-protocol.md` §2.3's rule ("genuine work only, not
artificial benchmark tasks") is satisfied differently here than in Phase
54: the `depth:` question is not *currently* open in Ledgerkit (Stage C
Phase 5 already answered and shipped it) — but it is a **real, dated,
already-independently-verified ground truth**, which is what makes it
usable as a controlled re-creation rather than an artificial one. Using
an already-answered real question, with an independently-verified
correct answer on record, lets `context-evaluator` grade the experiment
against **actual fact**, not against the lead's own judgment of what
"good" context would have looked like (a stronger evaluation bar than
Phase 54's own `tag:` task had, since `tag:` had no independently-known
correct answer at the time it was attempted). This is a deliberate,
disclosed design choice, not a substitute for a currently-open question —
if a currently-open, equally rich multi-entry-point Ledgerkit question
exists by the time this phase runs, using it instead is equally valid
and should be preferred if available (checked live at implementation
time, not assumed now).

## 4. Experiment design

### 4.1 Avoiding lead-contamination

The lead (this session) now has direct, detailed knowledge of the
correct answer from reading Ledgerkit's own committed material for this
plan. **The lead must not be the agent under test.** Both the baseline
and treatment runs are executed by freshly-dispatched agents with no
memory of this planning conversation (a `general-purpose` or
`Explore`-type dispatch for the runs themselves; `context-evaluator` and
`reference-project-tester` remain the existing independent-rating roles,
also freshly dispatched, re-deriving ground truth from the pinned
hledger source/manual/binary directly — never from this plan's own
summary of it, and never from Ledgerkit's own compat-register entries,
which would leak the answer).

### 4.2 The task given to both runs

*"Determine hledger's actual `depth:`/`--depth` behaviour for the
`balance`, `register`, `accounts`, `stats`, and `print` commands, citing
concrete evidence for each. State explicitly whether the behaviour is
uniform across all five commands or varies, and why."* — deliberately
phrased the same way Ledgerkit's own Stage C Phase 1 brief was scoped
(a semantics question, not "find the bug"), so a naive agent is exactly
as exposed to the Phase-1-style trap as the real historical attempt was.

### 4.3 Baseline run

A fresh agent, given: the pinned local hledger clone
(`/home/cormac/projects/hledger`, commit `33fa849e7ae8...`, tag
`1.52.4`) and ordinary tools (`Read`, `Grep`, `Bash`, `WebFetch` for the
manual) — **no CodeCompass**. This reproduces today's real baseline
workflow (`hledger-researcher`'s own brief), exactly as Phase 54's
baseline did for the `tag:` task.

### 4.4 Treatment run

A fresh agent given the same task, plus whatever CodeCompass context
can actually supply **given what exists before Phase 60's Haskell
adapter lands**. This is an important scope boundary, stated explicitly
rather than glossed over: CodeCompass has no Haskell-source parsing or
symbol/usage detection today (that is Phase 60's own job). What Phase
54b *can* test now is the **document/reference layer**: reusing Phase
54's already-built ingestion pipeline
(`planning/reference-projects/ledgerkit/reference-experiment/`) to
extract and index, as provenance-tagged Markdown, the *union* of source
material a thorough investigation needs — not hand-picked to contain
only the correct answer, but the same six-plus-one hledger source files
named in §1.2, the manual's Depth/queries sections, and (for contrast)
the single `Query.hs` `Depth` constructor definition that Phase 1's real
mistake stopped at — materialized into a scratch copy of Ledgerkit and
indexed via CodeCompass's ordinary `sync`/`query relations` machinery
(spec-doc detection, `mentions_artifact`), exactly as Phase 54 already
validated works for extracted reference material. The treatment agent
works from CodeCompass's query output over that indexed material, not
from re-reading the hledger source directly — if it falls back to direct
reading because the indexed material is confirmed insufficient, that is
itself a recordable finding (Phase 54's own precedent), not a disallowed
move.

**Deliberately not tested this phase**: automatic, CodeCompass-driven
*discovery* of which hledger files are relevant, with zero curation —
that requires Haskell-aware usage/call-site detection, which does not
exist until Phase 60. Phase 54b tests whether CodeCompass helps an agent
reason over a *given* (realistically-scoped, not answer-leaking) set of
ingested material; Phase 61 (§6) is where automatic cross-language
discovery itself gets tested, once the adapter exists.

### 4.5 Independent evaluation

`context-evaluator` re-derives the ground truth in §1.1/§1.2 directly
from the pinned hledger clone/manual/binary (never from Ledgerkit's own
compat-register entries or this plan), then rates both runs against
`context-quality-evaluation.md`'s standard instrument **plus** the new
criterion in §5. `reference-project-tester` records friction live for
both runs, same as every prior reference-project phase.

## 5. New evaluation criterion: execution-path completeness

Added as a **Phase-54b-scoped addendum**, not a change to the shared
`context-quality-evaluation.md` instrument (that file gets one pointer
sentence noting where this lives — see "Files" — not a rewrite of its
own criteria table; generalising it is a later, evidence-gated
decision, exactly like every other candidate abstraction in this
project):

> **Execution-path completeness**: did the agent identify and inspect
> **all** materially relevant behavioural entry points before reaching a
> conclusion? For this task, "all" is checkable against real fact: the
> five commands in §1.1, and specifically whether the agent's conclusion
> correctly distinguishes `stats`' genuine exception rather than
> asserting uniform behaviour across all five. Rate: **complete** (found
> and correctly characterised all five, including the `stats`
> exception) / **partial** (found the general clip-not-exclude rule but
> missed the `stats` exception, or missed `print`'s full depth-blindness)
> / **premature** (stopped at the `Depth` constructor's own definition
> and concluded uniform behaviour without checking any command's actual
> consumption of it — i.e., reproduced Stage C Phase 1's own real
> mistake).

This is deliberately a three-way, checkable rating tied to a real,
already-known-correct answer — not a subjective judgment call.

## 6. Reuse of existing mechanisms only (per the governing prompt's explicit constraint)

- Friction and missing/needed relationships: `planning/context-gaps/`
  and `planning/context-observations/` (Phase 52's existing lifecycle) —
  the same two queues Phase 54 already used, unchanged.
- Any candidate process/design lesson: `planning/learnings/`, triaged by
  `knowledge-curator`, same as every phase.
- Independent rating: `context-evaluator` (per §5's addendum) and
  `reference-project-tester`, both existing roles, no new agent.
- Closeout: `release-phase-auditor`, `docs-reconstructor` (drift audit,
  only if a `src/` or current-truth doc changes — none is planned; see
  Scope), same as every phase.
- **No new behaviour ontology, claim system, execution graph, or
  relationship-type set is introduced by this phase, full stop.** If the
  experiment finds CodeCompass's existing mechanisms (spec-doc ingestion
  + `mentions_artifact` + the observation/gap queues) are insufficient to
  even *represent* what was found, that insufficiency is filed as a
  `CG-NNN`/`OBS-NNN` entry for GATE DD to weigh (§7) — it is not treated
  as license to build the missing thing inside this phase.

## 7. Feeding GATE DD (Phase 55) and informing Phase 57

Per `conditional-generalisation.md` §3's existing GATE DD decision
procedure (list every confirmed "cannot represent" finding; name the
smallest candidate design; take the union), this phase's findings slot
into **existing** hypothesis rows, not a new one:

- **§2.2 "executable kind"** (feeds Phase 56): whether representing "a
  behaviour has multiple entry points, some of which diverge from the
  general rule" needs anything beyond the already-sketched executable
  kind's "relates to... behavioural-evidence records supplied by
  external tooling," or whether the document/reference layer (§2.3) is
  already sufficient for this class of finding.
- **§2.4 "provenance / evidence"** (feeds **Phase 57**): whether a
  behavioural claim assembled the way §1.3 shows Ledgerkit already does
  by hand (documentation + implementation-path + executable-observation
  + independent-verification, each a distinct evidence *kind*) needs a
  first-class `source_kind`/`confidence` distinction in CodeCompass's own
  model, or whether existing mechanisms (mechanical relation + prose
  evaluation reports) already carry this adequately for CodeCompass's
  own use.

**Explicitly not a new fourth hypothesis row.** "Behavioural" evidence,
as named in the governing prompt and in Phase 57's own existing
description ("distinguishing source-derived fact / doc statement /
**observed behaviour** / test result..."), is already inside §2.4's
scope, and the executable-kind side is already inside §2.2's. Phase 54b
sharpens both with a real, multi-entry-point, already-independently-
verified test case; it does not need a new candidate design to do so.
**A single instance recurring across ≥2 tasks/projects remains the
promotion bar** (`context-gaps/README.md`'s existing rule) — this phase
alone, whatever it finds, does not by itself justify Phase 56/57;
GATE DD still requires ≥2 independent occurrences or two independently
hitting agents, unchanged.

## 8. Carrying findings forward to Phase 60 (Haskell adapter)

Whatever Phase 54b finds about what the document/reference layer *can't*
do — specifically, whether an agent working from CodeCompass's ingested
material still has to fall back to raw source reading to find all five
commands' consumption of `Query`/`Depth`-shaped state — becomes a **named
requirement**, not a vague aspiration, for Phase 60's adapter design: the
Haskell `EcosystemAdapter`'s exported-module-signature scan
(`planning/v1-redefinition/roadmap.md` Phase 60) should be evaluated
against whether it would have surfaced all six real consumer files for a
concept like `Depth`, not just the defining module — i.e., whether
mechanical call-site/usage detection (the same shape as the existing
Python/Cargo/npm import-usage detectors) is needed for Haskell too, or
whether module-export-signature-level information is sufficient. This is
recorded as an open design question for Phase 60 to resolve with real
evidence once the adapter exists, not answered speculatively here.

## 9. Refining Phase 61 (hledger cross-language experiment)

Phase 61's existing roadmap description ("track hledger... evaluate
materially the same way every Ledgerkit task has been evaluated") is
refined, not replaced, to make the central test explicit: **once the
Haskell adapter (Phase 60) exists, re-run this same `depth:`
behavioural-reconstruction question (or another Ledgerkit compatibility
question with equally rich, independently-verified evidence, confirmed
live at Phase 61's own start per this project's standing "reconfirm
before use" discipline) using real Haskell-side structural information
instead of Phase 54b's document/reference-layer ingestion, and
separately test whether CodeCompass can relate the reconstructed
Haskell-side understanding to Ledgerkit's own Python implementation
(`ledgerkit.query.depth.DepthSpec`, `clip_account_name`, etc.) as the
same behavioural concept realised in two languages.** This is a genuine
cross-language behavioural-equivalence test — not "does the adapter
parse Haskell" (that is Phase 60's own DoD) but "does CodeCompass help
an agent recognise that two differently-implemented things are the same
behaviour." Phase 54b's own result (§1, §5) is Phase 61's baseline for
"how much better does real structural information do, compared to the
document-ingestion layer alone" — the same before/after comparison
structure Phase 54 already established for baseline-vs-treatment, one
level up.

## Scope

**In scope:**

- Two fresh-agent runs (baseline, treatment) of the `depth:`
  behavioural-reconstruction task (§4), or a live-reconfirmed equally-
  rich alternative if `depth:` is judged stale/compromised by
  implementation time.
- Extending Phase 54's existing reference-ingestion pipeline's *usage*
  (not its own code, unless a real gap is found) to extract the source-
  file/manual union named in §4.4, materialized into a **scratch** copy
  of Ledgerkit (never the real clone), indexed via CodeCompass's
  unmodified `sync`/`query relations`.
- `context-evaluator` report using `context-quality-evaluation.md`'s
  standard instrument plus §5's execution-path-completeness addendum.
- `reference-project-tester` friction log for both runs.
- New `planning/context-observations/`/`planning/context-gaps/` entries
  for every real friction point, same as every prior reference-project
  phase.
- `planning/reference-projects/ledgerkit/findings.md` gains a new dated
  section recording this phase's outcome for GATE DD (§7).
- One pointer sentence in `context-quality-evaluation.md` noting where
  the phase-scoped execution-path-completeness criterion lives (not a
  rewrite of its criteria table).

**Explicitly out of scope:**

- Any new graph table, column, relation kind, claim/ontology concept, or
  execution-graph structure — per §6, a hard constraint for this phase,
  not a default that yields under pressure.
- Automatic, zero-curation discovery of which hledger files are
  relevant — requires Haskell-aware usage detection, which is Phase 60's
  job (§8), not this phase's.
- Any change to the real Ledgerkit repository — read-only throughout,
  same discipline as every prior reference-project phase.
- Generalising the execution-path-completeness criterion into
  `context-quality-evaluation.md`'s shared instrument — stays
  phase-scoped unless a later phase's evidence justifies promoting it
  (a `knowledge-curator` / learning-lifecycle decision, not made here).
- Building anything toward the Haskell adapter itself (Phase 60's own
  scope) — this phase only names requirements for it (§8), doesn't
  implement any of them.

## Design decisions

- **No new ADR.** This plan refines Phase 54b/57/60/61's *scope* inside
  the framework `decisions/0056` and `conditional-generalisation.md`
  already establish; it makes no new architectural commitment of its
  own (§6, §7) — if implementation surfaces one, it gets its own ADR at
  that point, not pre-emptively here.
- **Fresh-dispatched agents for both runs, not the lead** (§4.1) — the
  single most important methodological point in this plan, since the
  lead's own detailed knowledge of Stage C Phase 5's answer (necessary to
  write this plan at all) would otherwise contaminate any run the lead
  performed directly.
- **Reusing an already-answered question as a controlled re-creation,
  with a live check for a better-fit currently-open alternative at
  implementation time** (§3) — disclosed as a deliberate departure from
  "genuine, currently-open task only," justified by the stronger,
  fact-checkable evaluation bar it buys.
- **The document/reference-layer vs. code-structural-layer split (§4.4,
  §8)** — deliberately narrows what this phase claims to test, so its
  result cannot be mistaken for "CodeCompass can (or can't) trace
  Haskell call sites," which is Phase 60/61's question, not this one's.

## Files

- `planning/phase-54b-ledgerkit-behavioural-understanding-experiment.md`
  — this plan.
- `planning/phase-54b-ledgerkit-behavioural-understanding-prompt.md` —
  the governing prompt, verbatim.
- `planning/reference-projects/ledgerkit/<NN>-depth-behavioural-reconstruction.md`
  — the per-task evaluation report (baseline + treatment + §5's
  addendum), once run.
- `planning/reference-projects/ledgerkit/findings.md` — new dated
  section.
- `planning/context-observations/inbox.md`,
  `planning/context-gaps/inbox.md` — new entries from both runs.
- `planning/v1-redefinition/context-quality-evaluation.md` — one pointer
  sentence only.
- No `src/codecompass/` change expected; if the document-ingestion
  extension needs a real code change to Phase 54's pipeline (not its own
  graph-facing code), that lives under
  `planning/reference-projects/ledgerkit/reference-experiment/`, same as
  Phase 54 itself.
- `planning/retros/phase-54b-ledgerkit-behavioural-understanding.md` —
  the phase retro.

## Verification

- Both runs produce a real, checkable artifact (a behavioural claim with
  evidence, per §1.3's categories) — `context-evaluator`'s independent
  verdict for each, including the §5 execution-path-completeness rating,
  not the lead's self-assessment.
- The ingestion extension (if any code changes) has its own passing
  tests, consistent with Phase 54's own precedent.
- `pytest`/`ruff check .`/`python scripts/check_user_docs.py --strict`
  clean throughout.

## Done when

Standard DoD (`CLAUDE.md` §5) + both runs completed and independently
rated, including the §5 addendum + every real friction point filed via
the existing observation/gap queues + §7's GATE DD framing answered with
real findings (not placeholders) + `findings.md` updated + the retro
states plainly whether the treatment run reached a **complete**,
**partial**, or **premature** conclusion, and whether that differed from
the baseline run's own rating + `release-phase-auditor` PASS or PASS
WITH NON-BLOCKING OBSERVATIONS.

**Not done merely because both runs completed** — done only once
`context-evaluator`'s independent verdict (standard instrument + §5
addendum) exists for both, and §7/§8/§9's forward-looking questions are
answered with real findings, not deferred silently.

---

## Review gate

Per this project's own "do not begin implementation until the plan is
produced and reviewed" precedent (Phase 54): this plan is presented for
review now. Judgment calls worth explicit attention before
implementation starts:

1. **Reusing the already-answered `depth:` question rather than an
   open one** (§3) — a deliberate trade of "genuine, currently-open
   task" for "fact-checkable against an independently-verified answer."
   If a currently-open, comparably rich Ledgerkit question is preferred
   even at the cost of losing the fact-checkable bar, say so before
   implementation.
2. **Splitting the document/reference layer (this phase) from the
   code-structural layer (Phase 60/61)** (§4.4, §8) — narrows what this
   phase can conclude. If the intent was for Phase 54b itself to already
   test Haskell-source structural tracing (pulling Phase 60 forward),
   that changes this plan's scope materially.
3. **Keeping the execution-path-completeness criterion (§5) phase-scoped
   rather than folding it into `context-quality-evaluation.md`
   immediately** — consistent with "don't generalise before evidence,"
   but if the user wants it adopted as a standing criterion for every
   future reference-project evaluation regardless of this phase's own
   result, that's a different, larger change than this plan makes.
