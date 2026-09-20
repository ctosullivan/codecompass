# Context-quality evaluation specification (required output 8)

The minimum report the `context-evaluator` produces for each
CodeCompass-assisted reference-project task. Narrowly focused on **context
quality**, not productivity benchmarking.

Operationalised by Phase 44 (as a template); applied in Phases 46, 51, 59
(Ledgerkit), 54b and 61 (Ledgerkit behaviour validation and the hledger
cross-language experiment, Stage D/F), and 67 (final confirmation).
**Amended 2026-09-12** (`realignment-2026-09.md`): Ledgerkit is now
first (was Technical Clipper); phase numbers updated, template and
criteria unchanged — this spec was always project-agnostic. **Amended
again 2026-09-17** (`decisions/0056`): Phase 61 now evaluates the
hledger cross-language experiment (via the new Haskell adapter), not a
Technical Clipper task — the template/criteria are unaffected either
way, exactly as the note above already anticipated. **Amended again
2026-09-18**: Phase 54b adds one additional, phase-scoped criterion
("execution-path completeness" — did the agent identify and inspect all
materially relevant behavioural entry points before concluding?), defined
in `planning/phase-54b-ledgerkit-behavioural-understanding-experiment.md`
§5. It is deliberately **not** added to §3's shared criteria table here —
staying phase-scoped unless Phase 54b's own result justifies promoting
it, the same evidence-before-generalisation discipline this file's own
history already follows. **Amended again 2026-09-19** (Phase 61 —
`L-027`): a new ground rule (§1) on single-trial baseline/treatment
comparisons, added to the shared instrument this time (not kept
phase-scoped like Phase 54b's own addition) because the confound it
names is a property of the *comparison design itself*, not of any one
phase's own subject matter — it applies to every future two-run
reference-project evaluation, not just Phase 61's own.

## 1. Ground rules

- The evaluator inspects the **target repository directly** to establish
  ground truth. It does **not** use CodeCompass to validate CodeCompass.
- The evaluator is **not told** the answer the lead was hoping for.
- **Incorrect or misleading context is treated as more serious than
  incomplete context.** A FAIL for one confidently-wrong claim outranks a
  PASS WITH GAPS for three missing-but-harmless ones.
- A technically-correct result that offers little advantage over a couple
  of cheap searches is recorded **honestly as low-advantage** — not
  rounded up because it wasn't *wrong*.
- **A single-trial (N=1-per-condition) baseline/treatment comparison
  cannot, by construction, separate "the tool's real contribution" from
  "one agent read more carefully than the other."** Before crediting
  CodeCompass for a treatment-arm finding the baseline missed,
  explicitly check whether both arms had equal raw-source access to the
  decisive evidence (both agents' own file-read logs, not just the
  polish of the final report) — if they did, the quality delta is
  agent-diligence variance, not a context-quality result, regardless of
  how well the treatment report reads. Confirmed necessary at Phase 61
  (`L-027`): a real, independently-confirmed divergence discovery would
  have been misattributed to CodeCompass had this check not been made
  explicitly — both agents had read the exact same decisive raw source,
  which was not itself a CodeCompass vendor.

## 2. Report structure

```
# Context-quality evaluation — <task slug>

## Setup
- Reference project: <url>
- Pinned commit: <sha>
- CodeCompass revision: <sha> / version
- Task: <one paragraph — the genuine development task>
- Context CodeCompass supplied: <verbatim or attached — graph query
  results, generated Skill content, "what matters for this task" output>

## Criteria assessment
(one short paragraph + a rating per criterion — §3)

## Verdict:  PASS | PASS WITH GAPS | FAIL
(one paragraph justifying it)

## Context advantage:  LOW | MODERATE | HIGH
Answer explicitly: "Could a competent fresh Claude session have obtained
equivalent context trivially through ordinary repository inspection
(a few greps, reading an obvious file, one `--help`)?"  <yes/partly/no>
+ one paragraph.

## Material gaps / failures
- <bullets — each also filed as a candidate learning with an ID>

## Would this have misled the implementing agent?  yes | no | partially
(the single most important line — expand if yes/partially)
```

## 3. Criteria (each rated: strong / adequate / weak / n/a)

| Criterion | Question |
|---|---|
| **Accuracy** | Were CodeCompass's claims correct against the actual target source/docs? |
| **Relevance** | Was the supplied context actually connected to *this task*, or generic? |
| **Completeness** | Did it contain the *important* context needed to understand the task (not everything — the important things)? |
| **Freshness** | Did it reflect the actual pinned target revision and the actual dependency versions in play? |
| **Grounding / provenance** | Could each material claim be traced back to a specific source/project evidence location? |
| **Noise** | Was irrelevant information kept reasonably low? |
| **Safety / trustworthiness** | Did CodeCompass present any incorrect or misleading relationship/claim as if it were authoritative? |

## 4. Verdict definitions

- **PASS** — every material claim accurate and grounded; no misleading
  content; context was relevant and sufficiently complete for the task.
  Gaps, if any, are immaterial.
- **PASS WITH GAPS** — no incorrect or misleading content, but a
  material piece of context was missing, stale, or too noisy to rely on
  without extra work. Trustworthy but incomplete.
- **FAIL** — at least one incorrect or misleading claim presented
  authoritatively, **or** the context was so incomplete/noisy/stale that
  relying on it would have sent the implementing agent wrong.

## 5. Context-advantage definitions

- **LOW** — a fresh Claude session gets equivalent context from a couple
  of obvious searches / reading one file. CodeCompass's contribution is
  marginal on this task. (Common for small repos — this is an honest,
  expected outcome, not a failure to hide.)
- **MODERATE** — CodeCompass meaningfully shortened the path (surfaced a
  non-obvious relationship, the exact version, the right test, a relevant
  ADR) but a diligent agent would have gotten there.
- **HIGH** — CodeCompass surfaced context that a fresh session would
  plausibly have missed or gotten wrong (a subtle version-specific
  behaviour, an easily-overlooked caller, a cross-cutting relationship),
  with grounding an agent could verify.

## 6. Aggregation (Phase 47 / 62–63)

Across all evaluated tasks:
- count of PASS / PASS WITH GAPS / FAIL;
- distribution of LOW / MODERATE / HIGH;
- every "would this have misled the agent? yes/partially" — listed in
  full (these drive R3/R4 mitigation and are the highest-priority
  findings);
- recurring gap categories (the input to GATE DB / GATE DD).

**Shipping bar for redefined v1 (Phase 70):** zero FAIL verdicts on the
final suite; MODERATE-or-higher advantage on the majority of tasks — or a
written, explicit justification for shipping below that bar (e.g. "LOW
advantage is the honest result for repos this small; the value case is
X"). The bar is a forcing function for honesty, not a number to
game.
