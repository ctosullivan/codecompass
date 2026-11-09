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
  comparative review, plus the earlier migration-round reviews
  recorded in the pending-review/published-evidence JSON history).

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
| `docs/concepts/adapter.md` | Migrated, two regions | `adapter-concept` (CL-ADPT-001/002/005), `adapter-term-ambiguity` (CL-ADPT-007) |
| `docs/concepts/vendor-and-ecosystem.md` | Migrated, one region, deliberately narrowed (excludes the depth-toggle fact and the `vendor.toml` file-format section — neither has a backing Claim) | `ecosystem-vendor-adapter` (CL-ADPT-004/005) |
| `docs/concepts/knowledge-model.md` | Migrated, two regions, deliberately narrowed from the plan's original ambition (record-kind table stays human-authored) | `provenance-cross-cutting` (CL-EVID-013), `invariant-not-a-record-kind` (CL-EVID-007) |

Final scope: **five schema-governed, genuinely compiled documents**
(README.md and CONTRIBUTING.md from Stage 87A/87B, plus
adapter.md, vendor-and-ecosystem.md, and knowledge-model.md from this
stage) — one fewer than the plan's own "six overall" target, because
context.md's migration was honestly declined rather than forced.
`context.md`'s decline is itself real evidence, not a null result: it
is the first case in this project where the compiler's own editorial
reviewer recommended *not* iterating further, because the underlying
knowledge record itself lacks the missing facts — a correctly
triggered "preserve original content when generation is inferior"
outcome, exactly as the plan's own instruction required.

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
