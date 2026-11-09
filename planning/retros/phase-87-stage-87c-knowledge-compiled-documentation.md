# Phase 87 Stage 87C retro — Knowledge-compiled Concepts pages, real multi-region maintenance, and matched-baseline comparator

- **Date:** 2026-11-10
- **Commit(s) this stage, in order:** `c16c8a5` (context.md adoption,
  declined), `82b5547` (context.md revert), `9b98433` (adapter.md
  adoption), `5df280f` (vendor-and-ecosystem.md adoption), `d908da2`
  (boundary corrections), `4a661b8` (adapter.md dispatch-table
  extraction), `27e265f` (adapter.md + vendor-and-ecosystem.md
  compile/publish), `8f943e2` (knowledge-model.md adoption, narrowed
  scope), `f593319` (knowledge-model.md compile/publish), `0ea4001`
  (CL-ADPT-005 amendment — the real incremental-change proof's own
  knowledge amendment), `1fba77d` (seeded human edit for the
  demonstration), `28c3a6c` (recompile/review/republish of both
  affected regions), plus this retro's own closeout commits.
- **Governing authorisation:** "Amend and implement Stage 87C,
  conditional on an independent planning review returning READY...
  Do not expand into later roadmap phases." Planning review returned
  **READY WITH NON-BLOCKING OBSERVATIONS** (plan §S.12, 2026-11-09)
  before implementation began.
- **Agents used:** `general-purpose` (×11 real dispatches across this
  stage: independent-check of EV-ADPT-013, 4 targeted semantic/
  editorial reviews of the CL-ADPT-005 amendment's two new sentences,
  the comparator's arm-A documentation task, the comparator's blind
  comparative review, the §S.8 independent documentation usability
  exercise, plus the earlier migration-round reviews recorded in the
  pending-review/published-evidence JSON history), `docs-reconstructor`
  (×2 — initial drift audit, FAIL with 2 blocking + 1 non-blocking
  findings; re-audit after the fix commit, PASS),
  `release-phase-auditor` (×1 so far — FAIL, missing changelog entry/
  incomplete retro/no learnings filed; fix in progress, re-audit
  pending).

## Where we are

Stage 87A and 87B (knowledge compilation, concurrency hardening, and
their own comparators) are complete and independently audited. Stage
87C's plan was independently reviewed and amended across three rounds
(§S.12: first and second rounds found blocking contradictions in the
reconciliation-state model, the declined-amendment branch, a stale
Getting Started reference, a missing compilation-readiness preflight,
and an incomplete comparative-cost accounting; third round returned
READY WITH NON-BLOCKING OBSERVATIONS) before this governing task
explicitly authorised implementation.

## Goal

Prove that CodeCompass can safely maintain a useful, coherent
documentation set from shared, evidence-backed canonical knowledge,
while preserving human contributions and measuring the actual quality
and cost of doing so — via four real additions to the existing
compiled-documentation pipeline: genuinely knowledge-compiled Concepts
pages beyond README.md, a real migration procedure for pre-existing
human-authored pages, a real multi-region knowledge-change
demonstration, and a matched-baseline comparator with an honest
three-way cost accounting.

## What was achieved

### §3A/§3B — Concepts-page compilation and migration

Four pages were attempted; **three succeeded, one was correctly
declined**:

| Page | Outcome | Regions |
|---|---|---|
| `docs/concepts/context.md` | **Declined.** Two full compile+review rounds both failed (UNSUPPORTED/FAIL — untagged sentences worsened 1→3 on `depth: detailed`; persistent factual/structural regression). Reverted to original content; schema deleted. | — |
| `docs/concepts/adapter.md` | Migrated, two regions | `adapter-concept` (CL-ADPT-001/002/012 — see the corrective addendum below for why `CL-ADPT-012`, not `CL-ADPT-005`), `adapter-term-ambiguity` (CL-ADPT-007) |
| `docs/concepts/vendor-and-ecosystem.md` | Migrated, one region, deliberately narrowed (excludes the depth-toggle fact and the `vendor.toml` file-format section — neither has a backing Claim) | `ecosystem-vendor-adapter` (CL-ADPT-004/012) |
| `docs/concepts/knowledge-model.md` | Migrated, two regions, deliberately narrowed from the plan's original ambition (record-kind table stays human-authored) | `provenance-cross-cutting` (CL-EVID-013), `invariant-not-a-record-kind` (CL-EVID-007) |

**Documentation-coverage accounting, corrected by this stage's own
corrective-closeout pass (§ below) — the original figures below were
wrong about `CONTRIBUTING.md` and conflated two distinct counts; these
are independently re-verified against the live repository, not
assumed**:

- **Schema-governed documents: 5** — `README.md`,
  `docs/getting-started.md`, `docs/concepts/adapter.md`,
  `docs/concepts/vendor-and-ecosystem.md`,
  `docs/concepts/knowledge-model.md`. `CONTRIBUTING.md` has **no**
  schema file and never has (confirmed: no `CONTRIBUTING.md.schema.yaml`
  exists, and no `codecompass-grounded-by` marker of any kind appears
  anywhere in `CONTRIBUTING.md` or `docs/development/contributing.md`)
  — the original retro draft's claim that it was one of Stage 87A/87B's
  compiled documents was simply wrong.
- **Documents with actual compiler-published (knowledge-grounded)
  regions: 4** — `README.md`, `adapter.md`, `vendor-and-ecosystem.md`,
  `knowledge-model.md`. **Not** `docs/getting-started.md`: it is
  schema-governed (5 sections) but every section has
  `required_knowledge: []` — it exists for Stage 87B's own tested-
  example-execution harness (`requires_tested_example`/
  `example_comparison_mode`), not knowledge compilation; it has zero
  `codecompass-grounded-by` regions of any kind.
- **Compiler-published regions: 6** — README.md's 1
  (`vendor-digest-concept`, Stage 87A) + adapter.md's 2 + vendor-and-
  ecosystem.md's 1 + knowledge-model.md's 2, all from this stage.
- **Other grounded regions from the earlier (Phase 81) intermediate-
  knowledge mechanism, pre-existing and untouched by Stage 87C: 1** —
  `README.md:75`'s own `intermediate-knowledge-layer` region, citing
  `CL-KNOW-001`, with **no** corresponding schema section at all (not
  listed in `README.md.schema.yaml`) — a plain Phase-81-era
  `codecompass-grounded-by` marker, structurally distinct from the five
  Phase-87 doc-compiler regions even though both use the identical
  marker syntax and are detected by the same
  `detect_grounded_region_changes` function. This is the region that
  has shown as the persistent, pre-existing `intermediate-knowledge-
  layer` `doc_candidate` throughout every `docs maintain` run in this
  stage, never auto-reconciled, never belonging to Stage 87C's own
  scope.
- **Wholly human-authored, never attempted for compilation**:
  `CONTRIBUTING.md` / `docs/development/contributing.md` (no schema, no
  marker, never part of any Phase 87 stage's own scope at all — not
  even a declined attempt, unlike `context.md`), plus every Concepts
  page's own deliberately-retained human-authored portions outside a
  compiled region's marker (adapter.md's dispatch table and "connector"
  section; vendor-and-ecosystem.md's depth-toggle paragraph and
  `vendor.toml` file-format section; knowledge-model.md's six-record-
  kind table and reconciliation-loop section; `context.md` in full).

Final scope: **5 schema-governed documents, 4 with actual compiler-
published content, 6 compiler-published regions overall** — one fewer
schema-governed Concepts page than the plan's own "six overall"
Concepts-page target, because `context.md`'s migration was honestly
declined rather than forced. `context.md`'s decline is itself real
evidence, not a null result: it is the first case in this project
where the compiler's own editorial reviewer recommended *not*
iterating further, because the underlying knowledge record itself
lacks the missing facts — a correctly triggered "preserve original
content when generation is inferior" outcome, exactly as the plan's
own instruction required.

Real defects found and fixed during migration (each independently
re-reviewed after the fix, never assumed correct): a required-Claim
coverage gap not caught by the citation-scope checker (fixed by
splitting `adapter-concept` into two schema sections); markdown-table
flattening (fixed by moving the table to permanent human-authored
content above the compiled region); dropped-but-cited identifiers,
recurring untagged topic sentences (fixed via mechanical JSON
patching, independently re-verified each time); a hallucinated
heuristic sentence (fixed by lowering `depth`); and, most seriously, a
fabricated-sounding claim in `knowledge-model.md`'s first draft that a
specific file exists in this repository when it does not — traced to
the cited Claim's own forward-looking framing being silently flattened
to a present-tense claim about this repository, requiring two
correction rounds (the first, adding a qualifier, was itself judged
insufficient by a second reviewer) before the unsupported sentence was
removed outright.

### §3D — Real multi-region maintenance demonstration

Real evidence (`EV-ADPT-013`, citing `src/codecompass/config.py:62-71`
and the already-passing
`tests/test_config.py::test_invalid_ecosystem_raises_config_error`,
`repository_revision` confirmed against real `git log` output)
established that `CL-ADPT-005`'s own statement was missing a true,
currently-real boundary fact: an out-of-enum `vendor.toml` ecosystem
string is rejected at config-load time, before `get_adapter`'s own
dispatch table is ever reached. Independently re-checked by a fresh
dispatch (confirmed source, test, test result, prior-claim absence,
and revision SHA) before acceptance.

**Controlled acceptance**: `CL-ADPT-005.yaml` amended directly, citing
`EV-ADPT-013`. The intermediate-knowledge-layer's own Markdown
projection was refreshed via the existing, unrelated
`codecompass knowledge select-candidates` mechanism (a mechanical,
no-review-needed auto-refresh — confirmed via `--dry-run` first).

A deliberate human edit was then seeded into `knowledge-model.md`'s
`invariant-not-a-record-kind` region (chosen as the designated
"unrelated edited region" after `context.md`'s decline removed it as
a candidate — the plan's own named fallback, "context.md **or**
knowledge-model.md," was exercised honestly rather than silently
substituted).

`docs maintain`, run once, correctly reported:

```
claims_changed: adapter-md-adapter-concept, vendor-and-ecosystem-md-ecosystem-vendor-adapter
doc_candidates: intermediate-knowledge-layer (pre-existing), knowledge-model-md-invariant-not-a-record-kind (seeded)
noop: readme-md-vendor-digest-concept, adapter-md-adapter-term-ambiguity, knowledge-model-md-provenance-cross-cutting
```

Both affected regions were then recompiled — not via a full blind
recompile, which, tried once, **lost** previously hard-won specific
identifiers (the `decisions/0002`/`0057` citations, the
`_resolve_package_dir`/hledger monorepo example) by regenerating the
whole section from a fresh model call — but by keeping each region's
already-published, already-reviewed prose exactly as published and
appending exactly one new sentence citing the amendment's new fact.
Each new sentence was independently re-reviewed (semantic:
SUPPORTED/SUPPORTED; editorial: PASS/PASS) before republication; the
unchanged base content was not re-reviewed, since it is byte-identical
to content that already passed review and publication. `git diff`
confirmed exactly one hunk, one changed line, in each of the two
published files.

A second `docs maintain` run confirmed the final state exactly as the
plan required: both affected regions `noop` (successfully
reconciled); the seeded edit and the pre-existing README candidate
both still `doc_candidate`, never auto-regenerated;
`claims_changed` empty; no other region's state changed.

### §4/§S.7 — Matched-baseline comparator

Both arms ran from the identical pinned starting revision (`1fba77d`
— the real repository state immediately before the `CL-ADPT-005`
amendment, already carrying the seeded human edit), given the same
underlying fact to independently verify and document (not a
pre-written sentence): "a teammate confirmed a new fact about invalid
`vendor.toml` ecosystem values — go verify it yourself and figure out
what needs updating."

**Arm A** (conventional agent, isolated git worktree
`/tmp/codecompass-arm-a`, no compiler/schema/citation tooling,
discarded after the comparator): independently read
`src/codecompass/config.py` and `tests/test_config.py`, correctly
identified the fact (and additionally found the fail-fast-on-
first-invalid-entry behaviour, which `EV-ADPT-013` did not capture),
and edited **only** `docs/concepts/vendor-and-ecosystem.md` — one new
paragraph in its "`vendor.toml` — the file format" section. It
explicitly recognised and declined to touch the seeded human edit
elsewhere in the same file, and explicitly declined to touch the
compiled/grounded region, reasoning (correctly) that a hand-edit does
not belong inside a machine-managed block. It could not run `pytest`
in its sandbox (no `pytest` installed) and disclosed this honestly,
relying on direct source/test reading instead of a live test run —
a real, honestly-disclosed verification-rigor gap relative to arm B,
whose evidence was independently confirmed by actually running the
test (`1 passed in 0.13s`).

**Arm B** is this stage's own real work above: both genuinely affected
regions correctly identified via the shared-citation dependency graph
(`CL-ADPT-005` is cited by both), both updated, both independently
reviewed, the seeded edit and pre-existing candidate both correctly
left alone.

**Blind comparative review** (a fresh `general-purpose` dispatch, told
only "Draft 1" / "Draft 2" against the same baseline, not which
process produced which, and instructed to establish ground truth by
reading the real source/tests/docs itself):

- Factual correctness: **both PASS** — no unsupported claims in
  either draft.
- Coverage: **Draft 2 (arm B) stronger** — Draft 1 (arm A) never
  mentions `get_adapter` or its dispatch table at all, so it never
  states (or implies) the fact's own stated consequence; Draft 2
  states it explicitly in both files.
- Cross-document consistency: **Draft 2 stronger** — identical,
  mutually reinforcing sentence in both files; Draft 1 is not
  inconsistent but leaves `adapter.md` silent despite `adapter.md`'s
  own extended discussion of the closed dispatch table.
- Editorial register: both pass.
- Scoping judgment: the reviewer judged arm B's substantive scoping
  call (touch both files) as the better one, but flagged a *process*
  concern — that arm B's new sentences sit inside the markdown's
  `codecompass-grounded-by` marker with no visible new citation in the
  rendered diff. **This concern reflects a real limitation of blind
  review, not a real defect**: `citation_display: none` in both
  schemas strips `{{cite:...}}` tags from the rendered file by design
  (the same convention Stage 87A/87B's own published README section
  already uses), so the reviewer, seeing only the rendered diff and
  not the pending-review JSON, could not see that the new sentence
  does carry its own `{{cite:CL-ADPT-005}}` tag, matching the already-
  published region's own cited-claim set exactly, and went through the
  real compile→review→publish pipeline rather than a hand-edit. Noted
  here rather than silently corrected in the reviewer's own report, so
  this methodological limit of the blinding is visible, not hidden.

**Cost accounting** (§S.7's three-category split):

| Category | Arm A | Arm B |
|---|---|---|
| Historical knowledge-preparation cost | Not reconstructable — "whatever general understanding of the codebase a conventional agent needs" has no bounded log. Disclosed as unavailable, not zero. | Not reconstructable — `CL-ADPT-005` and its sibling Claims were produced by `context-researcher` dispatches in Phase 79/80, well before Stage 87 existed; no bounded cost/value log exists for that work. Disclosed as unavailable, not zero. |
| Initial setup cost | N/A (arm A has none) | Not separately re-measured by this comparator (it is the cost of this stage's own §3A/§3B migration work, above); a precise aggregate figure was not instrumented in real time and is not estimated here. |
| Marginal-maintenance cost (the real, measured §S.6 task) | **1 dispatch, 110,527 ms, 59,631 tokens, 19 tool uses**, no retries. | **4 targeted review dispatches, 119,318 ms combined (26,585 + 33,828 + 28,971 + 29,934 ms), 193,754 tokens combined (49,206 + 48,668 + 48,397 + 47,483)**, plus 1 independent-check dispatch for `EV-ADPT-013` whose own usage was **not captured** (it hit a transient rate-limit error after delivering its full result — disclosed as unavailable, not zero), plus an unmeasured amount of lead-orchestration time (evidence authoring, `CL-ADPT-005` editing, draft patching, two `docs maintain` runs, four `docs record-review` calls, two `docs publish` calls, two commits) that the harness does not separately instrument — **a genuine, disclosed undercount, not a true total**. |

**Predeclared material-improvement threshold** (strictly fewer
major-severity human corrections **and** ≤1.5× arm A's total
marginal-maintenance time, both required):

- Correction count: **met for arm B.** Arm A's draft has one real,
  major-severity gap — the missing `adapter.md` update — that a human
  reviewer would need to send back before publication. Arm B's two
  new sentences passed independent review on the first attempt, with
  zero corrections.
- Time: **not clearly met, and plausibly violated.** Arm A's total
  measured time is 110.5s. Arm B's *measured* review-dispatch time
  alone is already 119.3s — about 1.08× arm A's — before counting the
  unmeasured independent-check dispatch or any lead-orchestration time
  at all, both of which were real and nonzero. The true total for arm
  B is undercounted by this report, not overcounted, which means the
  real ratio is *at least* 1.08× and very plausibly above 1.5× once
  the uninstrumented portions are included — but this cannot be
  certified with instrumented precision, only disclosed as doubtful.

**Two separate verdicts** (per §S.7, never conflated):

1. **Experiment completed rigorously: PASS.** Both arms ran to
   completion against the identical pinned revision and task; every
   rubric line was measured or its unavailability honestly disclosed;
   the §S.6 proof's own steps were independently verified by a fresh
   dispatch at each stage, not self-certified.
2. **CodeCompass advantage demonstrated: NOT DEMONSTRATED.** The
   quality condition (fewer major corrections) is met; the time
   condition is not clearly met and is plausibly violated once
   uninstrumented lead-orchestration overhead is honestly accounted
   for. Per the governing task's own explicit instruction, this
   neutral result is reported as measured, without adjusting the
   predeclared threshold or excluding any measurement to make it
   pass.

This is a genuinely useful, honest result: CodeCompass's structural
advantage (a shared-citation dependency graph that lets it correctly
scope a change across multiple documents without being told where to
look) is real and measured. Its current time/token cost for a small,
single-fact marginal change is not clearly cheaper than a capable
conventional agent doing the same task end-to-end in one dispatch —
largely because the real pipeline's own review/reconciliation
machinery (multiple independent dispatches, multiple CLI round-trips)
carries fixed overhead that does not shrink with the size of the
change. Whether this changes for larger or more structurally-entangled
changes is a question for a future stage, not this one.

**Explicit limitations assessment, added by this stage's own
corrective-closeout pass** — six specific ways this comparator's own
scope is narrower than "CodeCompass vs. a conventional agent" in
general, each affecting how far the two verdicts above may be read:

1. **Arm A's interaction with the existing `codecompass-grounded-by`
   marker was a single, favorable data point, not a demonstrated
   general property.** Arm A was never briefed on what the marker
   means; it correctly inferred, from reading the file alone, that the
   bracketed region was machine-managed and chose to place its edit
   outside it. A less careful conventional agent, or the same agent on
   a different day, might not show the same restraint — this comparator
   provides one encouraging data point about arm A's own judgment, not
   evidence that conventional agents reliably respect this project's
   own documentation-management conventions.
2. **Arm A's lack of access to the compilation workflow was a
   deliberate design choice of this comparator, not an inherent
   property of "a conventional agent."** `docs compile`/`docs record-
   review`/`docs publish` are ordinary CLI commands in this same
   repository; arm A was explicitly instructed not to use them, to
   isolate "what happens without the pipeline" as the comparison's own
   independent variable. A conventional agent *with* CLI access to
   these same commands is a different, unmeasured condition.
3. **Arm A's sandbox lacked an installed `pytest`, so its own
   verification fell back to static source/test reading instead of a
   live test run — an environment artifact of this comparator's own
   isolated worktree setup, not a general limitation of conventional
   agents.** Arm B's own evidence was independently confirmed by
   actually running the cited test. Had arm A's sandbox had `pytest`
   available, this specific verification-rigor gap between the two
   arms would likely not have appeared at all — it reflects this one
   setup, not a structural CodeCompass-vs-conventional-agent
   difference.
4. **Historical knowledge-preparation cost is missing for both arms,
   not merely "not estimated" — it is not reconstructable from any
   record this project kept**, for the same reason already disclosed
   in the cost table above. This is a structural gap in what this
   comparator (or any comparator run now) can ever measure about Stage
   87C's own true total cost, not a gap specific to this one
   experiment.
5. **CodeCompass-side orchestration time (lead-side CLI invocations,
   evidence/Claim authoring, commits) was never separately
   instrumented, and this cuts in only one direction**: the reported
   time figures for arm B are an undercount of its true total cost, so
   the "advantage demonstrated: NOT DEMONSTRATED" verdict is, if
   anything, **conservative in CodeCompass's own favor** — the real gap
   between the two arms' total cost is at least as large as measured,
   very plausibly larger, never smaller.
6. **One real case per arm, one single-fact change.** This remains,
   as already stated above, not a statistically powered trial. Combined
   with points 1-3, the comparator demonstrates one specific, real
   thing well (that CodeCompass's citation graph correctly scoped a
   change a capable conventional agent scoped too narrowly, on this one
   task) and should not be read as settling the broader question of
   economic efficiency at any other scale.

**The demonstrated-capability/demonstrated-efficiency distinction,
stated explicitly**: this comparator demonstrates **change-impact
coverage** (CodeCompass found both genuinely affected documents from a
shared citation; the conventional agent found only one) as a real,
measured technical capability. It does **not** demonstrate **economic
efficiency** (lower cost, faster turnaround) — the measured time/cost
comparison is neutral-to-negative for CodeCompass on this one small
change, honestly reported, and must never be silently read or restated
as if the capability finding also proved the efficiency question.

### §5/§S.8 — Independent documentation usability exercise

A fresh `general-purpose` dispatch, with no prior context of this
plan or any of Stage 87's own work and explicitly told not to read
`planning/`, worked through all five of §S.8's named tasks using only
the published documentation (falling back to source/tests only to
verify a doc claim or resolve genuine confusion).

**Directly relevant to this stage's own compiled pages**: task 2
(explain adapter/ecosystem/vendor/digest in your own words, from
`docs/concepts/` alone) produced correct, accurate paraphrases for all
four, with no source-reading needed — real, positive evidence that
`adapter.md` and `vendor-and-ecosystem.md`'s compiled regions
(migrated this stage) are comprehensible and non-misleading to a fresh
reader, directly answering §S.8's own "comprehension drift" concern.
Task 4 (the five-state reconciliation loop) also resolved correctly
from the architecture docs, with one minor, honestly-disclosed gap
(distinguishing `new` from the other four states required one
`doc_compiler.py` docstring check).

**Findings surfaced, none touching this stage's own compiled
content, none fixed here (out of this stage's scope — logged for
triage, not silently dropped)**:

- A real, reproducible, previously-undisclosed gap in `codecompass
  undo`: on a project's very first `codecompass` run, the whole-project
  graph rebuild that records `doc_artifacts` rows runs *before* the
  Skill/slash-command files are generated, so `undo --dry-run`
  immediately afterward omits `.claude/skills/codecompass/` and
  `.claude/commands/discovery.md` from its own reported `doc_artifacts`-
  backed removal list, and a real `undo --yes` leaves both on disk. A
  second sync backfills the missing rows and self-heals the gap. None
  of `docs/reference/cli.md`, `docs/getting-started.md`, or the
  architecture docs disclose this edge case, despite `cli.md`'s own
  unqualified claim that `undo` "correctly distinguishes a
  CodeCompass-generated artifact from a third-party one by its real,
  recorded origin." Independently reproduced (before/after `sync`,
  real `doc_artifacts` row counts) by the dispatch itself, not merely
  asserted.
- `docs/getting-started.md`'s own captured `codecompass query vendors`
  transcript renders as a plain ASCII table; the real command renders
  a Rich Unicode box-drawing table — the data matches, the rendering
  doesn't, and the doc never explains the discrepancy. Cosmetic, not
  factual.
- `docs/reference/cli.md` documents `knowledge trace`'s `--relation`
  flag's full choice set correctly but omits its default value
  (`supported_evidence` — confirmed via `--help` and source). Minor
  omission, not an inaccuracy.

These three are genuine documentation findings outside any page this
stage touched (`undo`'s own CLI reference and behavior, and
`getting-started.md`'s transcript), so fixing them is explicitly
**not** undertaken here, per the governing task's own instruction not
to expand scope beyond Stage 87C. Recorded as unresolved findings for
the learning-lifecycle triage below.

## Scope delivered vs planned

Delivered: §3A/§3B (four Concepts pages attempted, three migrated,
one honestly declined), §3D (real multi-region maintenance proof,
corrected §S.6 experiment), §4/§S.7 (matched-baseline comparator with
the full three-category cost split and both predeclared verdicts),
§5/§S.8 (independent usability exercise). §3C was not separately
exercised as new work — it is the claim that the existing Stage
87A/87B pipeline was reused unchanged, which is true by construction
(no new orchestration code was written this stage) and independently
confirmed by the `release-phase-auditor`'s own re-run of the full
regression suite and `docs maintain`.

Deviations from the plan, each disclosed in place above rather than
silently absorbed: `context.md`'s migration was declined (plan named
this as a real possible outcome, not a target); final compiled-page
count is five overall, not six (`context.md` didn't join); the §S.6
demonstration's "unrelated edited region" moved from `context.md` to
`knowledge-model.md` (the plan's own named fallback, exercised because
`context.md` no longer had a live grounded region to edit);
`vendor-and-ecosystem.md` and `knowledge-model.md`'s compiled scope
was each deliberately narrowed below the plan's original ambition,
in both cases because the excluded content had no citable knowledge
record. No scope was added beyond §3-§7 of the governing task.

## What worked

- **Appending one new, independently-reviewed sentence to an already-
  published region, instead of a full blind recompile, for a small
  marginal knowledge change.** A full recompile of `adapter-concept`
  against the amended `CL-ADPT-005`, tried once, regenerated the whole
  section from a fresh model call and lost previously hard-won,
  already-reviewed specific identifiers. Keeping the published prose
  and appending one new, independently-reviewed sentence preserved
  everything already correct and only needed review of the new
  content.
- **Dispatching a genuinely isolated arm A (a separate git worktree,
  no mention of the compiled pipeline) for the comparator**, rather
  than trying to simulate a conventional agent's behavior from inside
  this same context. It produced a real, independently-reached
  scoping decision (touch only one of the two affected files) that
  turned out to be a genuine, defensible-but-incomplete call — exactly
  the kind of real data point a simulated arm could not have produced
  honestly.
- **A genuinely fresh, no-prior-context dispatch for the §S.8 usability
  exercise** surfaced a real, previously-unknown `codecompass undo`
  defect that none of this stage's own (necessarily non-blind) work on
  the Concepts pages would have been positioned to find.
- **Mechanical JSON patching, always followed by a fresh independent
  re-review**, continued to be the right tool for narrow, factual
  citation-tag fixes (recurring untagged topic sentences, dropped
  identifiers) — carried over from Stage 87A/87B and still correct
  here.

## What didn't work

- **A full blind recompile as the default response to a marginal
  knowledge change.** Tried once for `adapter-concept` after the
  `CL-ADPT-005` amendment; it regenerated the section from scratch and
  silently dropped the `decisions/0002`/`0057` citations and the
  `_resolve_package_dir`/hledger example that an earlier patching round
  had already fixed and had already passed review. Abandoned in favor
  of the targeted-sentence-append approach described above.
- **This retro's own first draft was incomplete against `TEMPLATE.md`**
  — written covering only the technical narrative (goal, what was
  achieved, the four §3/§4/§5 subsections) and missing eight of the
  template's eleven sections entirely, including this stage's own
  candidate-learnings filing. Caught by the independent
  `release-phase-auditor` dispatch, not self-noticed before that audit
  ran. The lesson is filed below rather than merely fixed silently.
- **`context.md`'s two compile rounds** cost real dispatch time
  (compile + two independent reviews, twice) before being declined —
  not wasted in the sense of being hidden (both rounds are preserved
  as real, honest evidence in `planning/retros/phase-87-pending-review/
  context-md/five-senses-of-context.json`), but a real cost that
  produced no shipped page.

## Lessons learnt

- A documentation-compilation pipeline's real incremental-maintenance
  advantage is structural (it knows which documents share a citation
  dependency without being told), not necessarily a time/cost
  advantage on a small, single-fact change — the fixed overhead of
  independent review dispatches does not shrink with the size of the
  change, so a matched comparator on a small task can show "better
  scoped, not cheaper." Whether this changes at larger scale is an
  open question for a future stage, not resolved here.
- When a required citation is simply missing from a compiled draft
  (as opposed to present-but-wrong), the existing citation-scope
  checker provides no signal at all — it only checks citations that
  exist. This is a real, structural blind spot in the current
  verification mechanism, not merely an occasional model mistake (see
  `L-125`).
- Preserving an already-published, already-reviewed region's own
  prose and appending a small, independently-reviewed addition is a
  materially better response to a marginal knowledge change than a
  full recompile, specifically because a full recompile has no memory
  of prior, already-fixed defects.
- A phase retro is itself a DoD artifact with a required shape
  (`TEMPLATE.md`), not just a narrative write-up — writing it well
  does not substitute for writing it complete, and completeness is
  exactly the kind of thing a self-review tends to miss (this retro's
  own first draft is the evidence).

## Process-improvement feedback

- This stage's own retro was drafted incrementally, alongside the
  work, rather than against `TEMPLATE.md` from the start — leading
  directly to the missing-sections finding above. Starting a retro
  file from a copy of `TEMPLATE.md` (even with most sections stubbed
  "TBD") at the *start* of a stage, rather than writing free-form
  prose and only checking it against the template at the end, would
  have caught this before the auditor had to.
- No friction found in the agent-boundary model itself this stage —
  `docs-reconstructor`'s per-phase mode, `release-phase-auditor`'s
  read-only re-verification (it re-ran `docs maintain` and the full
  suite itself rather than trusting this retro's numbers), and the
  general-purpose dispatches for isolated-arm/blind-review work all
  behaved as their role definitions describe.

## Candidate learnings filed

`L-125` (citation-scope checker validates existence, not completeness,
of `required_knowledge`), `L-126` (markdown tables flatten under the
current clean-room composition step), `L-127` (a Claim's forward-
looking framing can be silently flattened into a fabricated-sounding
present-tense claim), `L-128` (blind review of a compiled document
cannot see a citation binding `citation_display: none` hides from the
rendered file), `L-129` (`codecompass undo`'s first-run
`doc_artifacts`-ordering gap) — all filed to `planning/learnings/
inbox.md`, status `candidate`, pending `knowledge-curator` triage.

## Where we're going

Stage 87C is the last stage this governing task authorised; later
Phase 87 work (the deterministic `docs/reference/cli.md` generator and
the semantic cross-document consistency checker, both named in §S.11
as real but deferred opportunities) requires separate authorisation
and is not started here. Phase 87 overall is **not** marked complete —
only Stage 87C's own completion is in scope for this closeout, per the
governing task's explicit instruction.

## Time / cost note

This stage ran across one long session, continued from Stage 87B's
own session via conversation-summary handoff. Real, instrumented AI
dispatch time/cost for the pieces this retro measured precisely: the
§S.6 maintenance demonstration's 4 targeted reviews (119.3s, 193,754
tokens combined) plus 1 independent-check dispatch (usage not
captured — rate-limited after delivering its result); the comparator's
arm A (110.5s, 59,631 tokens, 1 dispatch) and its blind review (140.7s,
72,423 tokens); the §S.8 usability exercise (333.0s, 106,130 tokens);
the `docs-reconstructor` pair (198.0s + 105.4s); the
`release-phase-auditor`'s first, FAIL-returning pass (1035.6s,
162,294 tokens — long because it independently re-ran the full
regression suite twice plus `docs maintain` plus a disposable ruff-
baseline worktree). Lead-side orchestration time (evidence/Claim
authoring, CLI invocations, commits, this retro) was not separately
instrumented, matching this stage's own disclosed-unavailable
discipline rather than being estimated.

## Addendum: Stage 87C corrective-closeout pass (2026-11-10)

A separately authorised corrective-review governing task, issued after
Stage 87C's own independent PASS audit (`planning/retros/
_audit-phase-87-stage-87c.md`, preserved unmodified — its PASS verdict
is not revisited or reopened by anything below), identified five real
issues in the completed Stage 87C work. All five were investigated
against the live repository before any change was made, and all five
were genuine (none were false alarms). Fixed in this order:

**A. The seeded experimental annotation in `knowledge-model.md` is
resolved, through the real reconciliation workflow, not a manual
baseline edit.** The original demonstration's own before/after state
and reconciliation evidence (§3D above, unchanged) stand as the real
record of what the five-state mechanism correctly did at the time. Two
further, real `knowledge apply` cycles then ran, each independently
reviewed before acceptance: (1) the originally-seeded `doc_candidate`
(bracket included) was accepted as-is, exactly as first captured,
advancing its baseline for the first time via `codecompass knowledge
apply` against the real pending manifest — never a hand-edited
`.grounding-state.toml`; (2) the bracketed annotation was then removed
as a separate, authorised, independently-reviewed edit (a fresh
dispatch confirmed the removal was clean and the surviving sentence's
own factual claim — "nothing currently cross-links" the two named
artifacts — is independently true), producing a second real
`doc_candidate`, resolved the same way. Both unrelated regions and the
separate, pre-existing README `intermediate-knowledge-layer` candidate
were re-confirmed unchanged after each cycle via a real `docs maintain`
run. The published `knowledge-model.md` now reads the useful factual
sentence with no experimental annotation.

**B. A real canonical-mutation governance violation was found and
corrected.** Stage 87C's own §S.6 implementation amended
`CL-ADPT-005.yaml`'s own `statement` field directly, in place — this
is a genuine violation of `planning/phase-54c-evidence-knowledge-
workflow.md` §2.4 ("a superseded Claim ... is never deleted or edited
in place — a new record of the same kind is written with `supersedes:
<old-id>`"), confirmed by direct re-reading of that governing section;
it was not an authorised exception (the Stage 87C plan's own "the
lead's own documented reconciliation decision" language authorised
*who* could decide to accept new evidence, not an exemption from this
already-standing record-mutation rule) and not merely a documentation
inconsistency (the rule is explicit, predates Stage 87C, and has a real
precedent already on file — `CL-ADPT-011` supersedes `CL-ADPT-009` the
correct way). The underlying fact itself was never in question: the
evidence (`EV-ADPT-013`) was real, independently checked twice over
(once during Stage 87C's own implementation, once again by a fresh
dispatch during this corrective pass), and the new boundary fact is
genuinely true and genuinely absent from `CL-ADPT-005`'s own original
text. The violation was in the *record structure*, not the *fact* —
so the fix repairs the audit trail rather than touching the fact:
`CL-ADPT-005.yaml` was restored to its exact pre-amendment text (`git
show 0ea4001^:...`) and its own `status` field changed to `superseded`
(a one-line field edit, matching this project's own "not a rewrite of
its content" convention); a new Claim, `CL-ADPT-012.yaml` (with its own
`DE-ADPT-012.yaml` derivation), was written carrying `CL-ADPT-005`'s
full original statement forward unchanged plus the new boundary
sentence, `supersedes: CL-ADPT-005`. The two published regions that had
come to cite `CL-ADPT-005` for the boundary fact (`adapter.md`'s
`adapter-concept`, `vendor-and-ecosystem.md`'s `ecosystem-vendor-
adapter`) had their grounding-marker citations swapped to `CL-ADPT-012`
— itself a real, detected `doc_candidate` (a citation-membership
change), independently reviewed (a fresh dispatch confirmed `CL-ADPT-
012` is a strict superset of what `CL-ADPT-005` supported and that the
swap is citation-accurate) and resolved via the same real `knowledge
apply` workflow as finding A, not a direct edit. No fact was reverted,
no history was rewritten, no second knowledge store was created, and no
past acceptance action was fabricated — `EV-ADPT-013`'s own real
evidence trail and both independent checks of it stand unchanged.
`knowledge select-candidates`/`render` were re-run to keep the
intermediate Markdown projection consistent with both record changes.

**C. Documentation-coverage accounting is corrected in place** (§3A/
§3B above, now reads the corrected figures): `CONTRIBUTING.md` was
never schema-governed and was never part of any Phase 87 stage's own
scope — the original retro's claim that it was one of Stage 87A/87B's
compiled documents was simply wrong, confirmed by the absence of any
`CONTRIBUTING.md.schema.yaml` and the absence of any
`codecompass-grounded-by` marker anywhere in `CONTRIBUTING.md` or
`docs/development/contributing.md`. The real, independently re-derived
figures: **5** schema-governed documents (README.md,
`docs/getting-started.md`, and the three Concepts pages) — of which
**4** have actual compiler-published regions (not
`docs/getting-started.md`, which is schema-governed only for its own
tested-example-execution harness, with zero knowledge-grounded
regions); **6** compiler-published regions in total; **1** further
grounded region from the earlier, structurally distinct Phase-81
intermediate-knowledge mechanism (`README.md`'s own
`intermediate-knowledge-layer` region, no schema section at all) —
this is the region that has shown as the persistent, pre-existing,
correctly-untouched `doc_candidate` throughout every `docs maintain`
run in this entire stage.

**D. The matched-baseline comparator's own limitations are now
explicitly assessed** (§4/§S.7 above, now includes a six-point
limitations list and an explicit capability-vs-efficiency distinction):
arm A's correct handling of the existing grounding marker, its
deliberately withheld compiler access, its sandbox's missing `pytest`,
both arms' missing historical knowledge-preparation cost, CodeCompass's
own uninstrumented orchestration time (which makes the measured
non-advantage result conservative *in CodeCompass's own favour*, not
against it), and the one-case sample size are all named individually.
The original two verdicts (experiment completed rigorously: PASS;
CodeCompass advantage demonstrated: NOT DEMONSTRATED) are unchanged —
this addendum narrows what they may be read to mean, it does not
rerun the experiment or move either verdict.

**E. `L-125` through `L-129`'s own triage was independently
re-confirmed already complete and substantive**, not merely present:
the second `release-phase-auditor` pass (`_audit-phase-87-stage-87c.md`,
the "RE-AUDIT" section) directly re-read every entry's own curation
note and disposition and found three re-derived the underlying
technical claim independently, one disclosed and then closed a real
evidentiary gap, and two substantively overrode the filer's own
classification with a reasoned, cited argument — a defensible,
non-rubber-stamp triage, each with a clear `promote` disposition, a
named destination artifact, and `status: candidate` pending that
artifact actually landing (unchanged from `L-122`/`L-124`'s own real
precedent). Nothing further was required or done for this finding; it
is recorded here as confirmed, not as a new fix.

Verification after all five fixes: the full regression suite, the
applicable strict validators, a fresh `codecompass docs maintain` run
across all five schema-governed documents, a fresh independent
`docs-reconstructor` pass, and a fresh independent `release-phase-
auditor` pass against the complete corrective diff are recorded below
this addendum once each has actually run — see the dated verification
log for their real results, not asserted here in advance of them
running.
