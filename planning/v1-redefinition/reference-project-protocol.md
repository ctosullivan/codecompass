# Reference-project plan — Technical Clipper (required output 7)

Also defines the **repeatable reference-project protocol** (§2) used for
every reference project — Ledgerkit first, Technical Clipper second.
Operationalised by Phase 44 (generic; unchanged by the realignment
below).

**Amended 2026-09-12 (`realignment-2026-09.md`, gate G11): Technical
Clipper is no longer the first reference project.** It moves to a new
**Stage F** — cross-ecosystem regression, run *after* Ledgerkit has
driven whatever Stage C/D/E changes land, to check they generalise
rather than overfit to accounting/hledger. §1's inspection findings and
§2.3's task pool are otherwise unchanged in substance; only phase numbers
moved (were 45–47, now 60–63) and their scope-label context changed
(was "first proof point", now "regression/generalisation check").

**Amended again 2026-09-17 (`decisions/0056`): Stage F no longer runs
Technical Clipper as its required content either.** Stage F is now a
minimal Haskell `EcosystemAdapter` spike validated against hledger
(`planning/v1-redefinition/roadmap.md`'s Stage F). **This file's own
content below is not deleted** — the registration/protocol material
(§2), the real inspection findings (§1), and the task pool (§2.3) remain
accurate and reusable, exactly as they were the last time this file was
amended rather than rewritten. Technical Clipper is now an *optional*
candidate for Phase 63's lightweight ordinary-project smoke test (not
the multi-task protocol below in full), or for later ecosystem-expansion
work picked up independently of the redefined-v1 roadmap's own
sequencing. If Phase 63 does use Technical Clipper, this file's §2.1
registration format and §2.2 working-copy discipline still apply; §2.3's
full task pool and §2.4's full per-task procedure are heavier than a
"lightweight smoke test" calls for — use only as much of them as Phase
63's own scope actually needs.

Repo: **https://github.com/ctosullivan/technical-clipper**

## 1. Inspection findings (2026-09-09 planning session — reconfirm live at Phase 60, its state will have moved)

Established by reading the live repository, per the task's requirement to
inspect rather than rely on the prompt.

| Aspect | Finding |
|---|---|
| Purpose | Local-first Chromium MV3 browser extension: captures code-heavy technical web content + ChatGPT conversations into deterministic Markdown. "A deterministic web document compiler with strong code awareness, not an AI summariser." Obsidian is the primary export target. |
| Language / build | TypeScript, ESM, pnpm monorepo (`pnpm@9.12.0`), Node ≥20. `vitest`, ESLint 9, Prettier, `typescript` 5.6. |
| Packages | `packages/core` (typed IR, provenance/confidence, normalization, hashing, rendering, bundle validation), `packages/detectors` (code blocks, terminal output, tab groups — Prism, highlight.js, Docusaurus), `packages/adapters` (site-specific + ChatGPT), `packages/pipeline` (clone→detect→extract→assemble→validate→evaluate), `packages/extension` (MV3 UI). |
| Runtime dependencies | **Zero.** |
| Dev dependencies | ~7, all build/test tooling: `@eslint/js`, `@types/node`, `eslint`, `prettier`, `typescript`, `typescript-eslint`, `vitest`. |
| Tests | 160 tests; 15 release "gates" (`pnpm gates`); fixture corpus — 22 articles (5 revision-pinned Wikipedia), 19 code fixtures, 87 code blocks, 4 conversations. Offline HTML/IR/Markdown fixtures under `fixtures/`. |
| Governance | `AGENTS.md` (canonical tool-neutral working contract) + `CLAUDE.md` (points to it); `CHANGELOG.md` (`[Unreleased]`, untagged); `planning/CONTEXT.md`; `architecture/` (current + target); `decisions/` (append-only ADRs); `.claude/skills/markdown-clipping/`. Governance shape is close to CodeCompass's own. |
| State | "MVP candidate — awaiting release approval." All 10 roadmap phases complete. Phase 10 done except final release approval (blocked on explicit user approval by design). All checks pass. Nothing tagged/released. On `master`. |
| Deferred / post-MVP (from `planning/CONTEXT.md`) | Firefox + Safari extensions; native Obsidian plugin; ClipSpec editor UI; image mirroring; enhanced HTML sanitization; manifest-based integrity verification for packaged distributions. Plus ongoing detector-robustness / adapter-coverage refinement implied by the architecture. |

### Why this is now the cross-ecosystem regression check (was: the first reference project)

Its substantive technical context is **almost entirely not in the
package graph**: DOM APIs, `MutationObserver`/`TreeWalker`, Chromium MV3
extension APIs (`chrome.scripting`, `chrome.runtime`, content scripts),
CommonMark / GFM fenced-code-block semantics, highlight.js & Prism
class-name conventions, Docusaurus/Docsify DOM shapes, ChatGPT's DOM
structure. CodeCompass's current model discovers ~7 build-tool
devDependencies and nothing else. That made it a strong *first* test
originally; it now makes it the ideal **regression** test — deliberately
different from Ledgerkit/hledger (TypeScript/npm/browser vs.
Python/accounting), so Stage F measures whether Ledgerkit-driven changes
generalise or accidentally became accounting-shaped
(`realignment-2026-09.md` §4, R10 in `README.md` §13).

## 2. The repeatable protocol

### 2.1 Registration

Each reference project gets a record at
`planning/reference-projects/<name>.md` capturing, at minimum:

- reference project repository URL;
- **starting revision** — the exact commit the baseline was taken at;
- **pinned revision per evaluation** — the exact commit a given task
  evaluation used (may advance as the reference project's own work
  advances; always recorded, never "latest");
- CodeCompass revision / version used;
- for each evaluated task: the genuine development task; the context
  CodeCompass supplied; the independent context-evaluation result;
  material gaps or failures.

### 2.2 Working copy discipline

- The reference project is cloned into a **scratch location outside this
  repository** (the session scratchpad or a sibling directory). It is
  **never** added to CodeCompass's own tree, `vendor.toml`, or
  `context-graph.db`.
- CodeCompass is run against that clone from CodeCompass's installed CLI
  (editable install or the foundation-release wheel).
- Where reproducibility matters, the clone is checked out at a **pinned
  commit** and that SHA is recorded in the evaluation report.

### 2.3 Task selection — genuine work only

Tasks come from the reference project's **own** roadmap, deferred-work
list, real open bugs, or a real refactor its architecture docs call for.
**Not** artificial benchmark tasks constructed to exercise CodeCompass.

Rule (task instruction, restated): the reference-project process is
**subordinate to Technical Clipper's own roadmap and architecture**. No
feature is added to Technical Clipper to make CodeCompass easier to
evaluate. If a task turns out to need such a change, pick a different
task.

Candidate task pool for Technical Clipper (confirm against the live repo
at Phase 61 — its state may have moved):

- a **fenced Markdown code-block handling** change (e.g. an edge case in
  language-tag inference, nested fences, or a highlight.js class mapping)
  — this is the task type the CodeCompass v1 vision doc explicitly names;
- a **detector-robustness** fix for a real HTML shape the corpus doesn't
  yet cover (a docs framework, a code-sample widget);
- an **adapter-coverage** extension (a new site adapter, or hardening the
  ChatGPT adapter against a DOM change);
- a **DOM-extraction** correctness fix (whitespace, entity handling,
  element-boundary bug);
- a bounded slice of a deferred item if the maintainer approves it as
  genuine (e.g. the HTML-sanitization hardening).

For each: the task must be something worth doing for Technical Clipper
regardless of CodeCompass.

### 2.4 Per-task procedure (Phase 61 for Technical Clipper; Phase 46 for Ledgerkit's own instantiation of the same steps — `ledgerkit-plan.md`)

1. Lead states the task and the pinned Technical Clipper commit.
2. Lead attempts the task **using CodeCompass context** where CodeCompass
   would plausibly help (query the graph, read a generated Skill, ask
   "what matters for this task" once that exists).
3. `reference-project-tester` records, live, every instance of:
   - bypassing CodeCompass (going straight to `grep`/file reads);
   - a manual search done because context was missing;
   - a stale relationship;
   - an incorrect relationship;
   - excessive irrelevant context;
   - a technical dependency CodeCompass could not represent at all;
   - context no better than direct repository inspection.
4. `context-evaluator` **independently** inspects the Technical Clipper
   repo at the same pinned commit (without using CodeCompass) and rates
   the context CodeCompass supplied, per `context-quality-evaluation.md`.
5. Both outputs land as an evaluation report at
   `planning/reference-projects/technical-clipper/<NN>-<task-slug>.md`,
   and every friction instance becomes a candidate learning
   (`learning-lifecycle.md`).

**Added 2026-09-18 (`L-022`, Phase 54b):** before dispatching any run,
when the per-task procedure includes constructing hand-authored material
a dispatched agent-under-test will read (e.g. a reference-ingestion
excerpt's `label`/`note` fields, a synthetic fixture file, any
authoring-time rationale meant to explain *why* a selection was made) —
re-verify, by reading the actual rendering/output function itself (not
just the authoring schema or interface), that no field intended only as
internal authoring commentary is actually written into the agent-visible
output. A field named `note` or similar reads as private authoring
rationale; if the renderer writes it into the file body, it is
agent-visible content indistinguishable from the rest of the material.
Confirmed the hard way at Phase 54b: an early draft's `note` fields
stated the experiment's own correct answer outright and would have
silently invalidated the entire baseline-vs-treatment comparison had the
rendering path not been re-checked before either agent was dispatched.
Scoped to controlled experiments that construct hand-authored material
for a dispatched agent to read — genuine-task evaluations (§2.3/§2.4's
ordinary case, using the target repo's own real content) carry no
equivalent risk and are unaffected.

### 2.5 The central question every evaluation answers

> **Is CodeCompass supplying context that another development agent can
> safely trust, and is that context materially useful compared with cheap
> direct project exploration?**

Do **not** over-focus on token counts, development speed, or artificial
performance scoring. The primary object of evaluation is **context
quality** (`context-quality-evaluation.md`).

### 2.6 Friction → product improvement (do not react per-observation)

```
reference-project observation
        ↓
candidate learning
        ↓
repeated evidence  (recurs across tasks, or both agents hit it)
        ↓
confirmed finding  (consolidation phase, knowledge-curator)
        ↓
roadmap implication  (Ledgerkit's instantiation: a Stage C phase, gated
                       by GATE DB. Technical Clipper's instantiation: a
                       narrowly-scoped Stage G fix, gated by GATE DF —
                       "fix only general problems with evidence")
```

A single observation never directly adds a product feature. This is the
mechanism by which **demonstrated agent needs — not speculation —
reshape the v1 plan.**

### 2.7 Non-invasiveness check (per phase)

Before closing the per-task phase (61 for Technical Clipper),
`reference-project-tester` confirms in writing that no change was made
to the working copy that its own maintainers wouldn't want on its own
merits, and that no CodeCompass repair was made *by the tester* to make
an evaluation pass.

## 3. Outputs of Stage F (Technical Clipper)

- `planning/reference-projects/README.md` — the registry (shared with
  Ledgerkit's entries).
- `planning/reference-projects/technical-clipper.md` — registration +
  baseline (Phase 60).
- `planning/reference-projects/technical-clipper/<NN>-*.md` — one per
  evaluated task (Phase 61).
- `planning/reference-projects/technical-clipper/findings.md` — confirmed
  findings + the fix-only-general-problems decision (Phase 62–63) →
  **GATE DF**.
