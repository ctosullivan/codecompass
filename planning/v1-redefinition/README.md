# CodeCompass v1 redefinition — planning package

This folder is an **umbrella planning package**, same role
`planning/v1.0-initial-release-roadmap.md` and
`planning/doc-graph-precision-roadmap.md` played for their phase groups,
but larger in scope: it redefines what "CodeCompass v1" means and lays
out an ordered, evidence-gated path to it.

**This package is planning only. No implementation has started. No
governance file (`CLAUDE.md`, `decisions/`) has been changed.** Every
governance/version/roadmap decision it depends on is listed in §7
(Human-decision gates). As of 2026-09-09, **G1 (version → `1.0.0.dev0`)
and G2 (→ G2-b: hold all publishing until redefined v1) are decided**;
G3, G4, G5 remain open and gate the phases named against them.

Per `CLAUDE.md` §1, each phase below still gets its own
`planning/phase-N-<name>.md` before its implementation starts. Stage A
phase files (39–43) and the first Stage B phase file (44) are written
alongside this package; later phases exist only as roadmap rows until the
evidence gates ahead of them resolve.

## Documents in this package

| File | Covers (required output #) |
|---|---|
| `README.md` (this file) | Redefined v1 overview (1); current-state & versioning assessment (2); risk analysis (13); human-decision gates (14) |
| [`roadmap.md`](roadmap.md) | Ordered redefined-v1 roadmap, stages A–F (3) |
| [`agent-led-development.md`](agent-led-development.md) | Specialist agents, boundaries, DoD integration (4) |
| [`learning-lifecycle.md`](learning-lifecycle.md) | Project-learning capture/curation/promotion (5) |
| [`documentation-lifecycle.md`](documentation-lifecycle.md) | Incremental maintenance + blank-slate reconstruction + closeout (6, 12) |
| [`reference-project-protocol.md`](reference-project-protocol.md) | Reference-project registration/inspection/task-selection; Technical Clipper specifics (7) |
| [`context-quality-evaluation.md`](context-quality-evaluation.md) | Context-quality evaluation spec (8) |
| [`ledgerkit-plan.md`](ledgerkit-plan.md) | Ledgerkit as the harder second reference project (9) |
| [`conditional-generalisation.md`](conditional-generalisation.md) | Technical-dependency / evidence-provenance generalisation, evidence-gated (10) |
| [`migration.md`](migration.md) | Keeping existing capabilities working through the evolution (11) |
| [`proposed-governance-changes.md`](proposed-governance-changes.md) | Proposed `CLAUDE.md` diff + proposed ADRs (feeds §7 gates) |

The learning-lifecycle scaffold itself lives at
[`../learnings/`](../learnings/) (created by this package as an empty,
ready-to-use structure — no phase needed to create a directory).

---

## 1. Redefined v1 overview

### 1.1 Current CodeCompass state (evidence)

CodeCompass is a mature, well-governed Python CLI (7,082 LOC across
`src/codecompass/`, 30 test modules, 520 passing tests). Phases 0–38 are
`done`. It currently does, for a project's **package** dependencies
(npm / PyPI / Cargo):

- manifest auto-discovery → `vendor.toml` (zero-question bootstrap);
- unconditional upstream **source cloning** per vendor (`vendor/<name>/src/`);
- deterministic, always-free per-vendor digests — `FILETREE.md`,
  `DEPTREE.md`, public API surface, flat symbol index;
- a **SQLite context graph** (`context-graph.db`) of vendors, symbols,
  real `(file, line)` usage sites, generated docs/Skills, and a project's
  own spec docs, with mechanical relationship edges and heading-scoped
  doc chunks;
- **usage-driven, batched, cost-disclosed AI enrichment** (grounded
  description, conversational overview, per-symbol purposes, typed
  relation labels) for vendors the project actually imports;
- generated consumption artifacts: per-vendor Skills, Cursor `.mdc`
  rules, a tool-level Skill, a `/discovery` slash command, a root
  `CLAUDE.md` routing table;
- `codecompass query` / `check` (severity-aware staleness) / `chat`
  (secondary) / `undo`.

The determinism-first boundary is a load-bearing, repeatedly-defended
design principle: **AI never decides *whether* a relationship exists,
only describes *how*** (`decisions/0031`, `0037`, `0045`;
`doc-graph-precision-roadmap.md`).

### 1.2 Why the v1 definition is being reconsidered

The repository's internal "v1.0" (`planning/v1.0-initial-release-roadmap.md`,
Phase 23) means: *"publish the package/source-grounding tool to PyPI."*
That is a **packaging milestone, not a validated-value milestone.** Three
concrete reasons it is the wrong place to plant the v1 flag:

1. **No evidence of value yet.** `decisions/0039` states plainly: "The
   project has no external users yet… Any decision made now is
   necessarily speculative." Every phase since 20 was found by CodeCompass
   dogfooding *itself* — a single Python project with 4 dependencies. The
   tool has never been pointed at a project it wasn't also developing.
2. **The interesting technical context of real projects is often not a
   package.** Both chosen reference projects (§1.6–1.7) have **≈0 runtime
   package dependencies**. Their real technical context is browser
   extension APIs, the CommonMark spec, ChatGPT DOM structure (Technical
   Clipper); the `hledger` executable, its manuals, journal syntax, and
   1.52 compatibility (Ledgerkit). CodeCompass's current model would
   produce a near-empty result for both. v1 should not be declared
   against a model that visibly fails its first two real targets.
3. **CodeCompass is not yet developed the way it claims to help others
   develop.** It is not agent-led; it has no independent evaluation of
   the context it produces; it has no systematic learning capture. It
   cannot credibly ship as *"the context layer for AI development agents"*
   until it has been built by one.

### 1.3 What remains valuable from the existing design (keep, do not rewrite)

- The **determinism-first boundary** (AI describes, never detects).
- **Source grounding**: cloning a dependency's own upstream source and
  grounding claims in it rather than model memory.
- The **context graph** as the connective substrate (SQLite, single
  file, rebuilt deterministically — `decisions/0032`).
- **Usage-driven gating**: enrich what the project actually uses, with
  disclosed, confirmable cost.
- **Generated Skills / `/discovery`** as the agent-facing consumption
  surface.
- The **governance system itself** (`CLAUDE.md`, ADRs, ROADMAP/CONTEXT,
  same-commit doc-sync, per-phase DoD). The redefined v1 *operationalises*
  this, it does not replace it.

### 1.4 The agent-first product direction

Positioning moves from:

> "A tool that indexes pinned dependency source for Claude."

to:

> "Give AI development agents a small, trustworthy, version-correct map
> of the technical context relevant to their task, with clear routes back
> to evidence."

Concretely, the target experience shifts from *"show me documents about
this dependency"* toward *"what technical context matters for this
task?"* — a small, high-confidence context map (relevant local
implementation, callers/callees, relevant tests, dependency + exact
version, APIs actually used, relevant local docs, relevant ADRs, known
gaps) with routes to deeper evidence, **not** a dump of everything.

### 1.5 Why CodeCompass becomes agent-led *first* (the prerequisite)

Before broadening the product model, change how CodeCompass is built
(Stage A). The main Claude Code session becomes project lead and
delegates bounded work to a **small** set of specialist agents
(`agent-led-development.md`). This is the prerequisite because:

- it is the mechanism that produces the independent verification,
  continuous doc/roadmap maintenance, and systematic learning capture
  that every later stage depends on;
- it must be **dogfooded on real CodeCompass changes before** large
  speculative architecture work, so the process is proven on low stakes;
- the reference-project and context-evaluation work in Stages B–D *is*
  specialist-agent work — the roles have to exist first.

### 1.6 Role of Technical Clipper (first proof point)

`https://github.com/ctosullivan/technical-clipper` — a TypeScript /
pnpm-monorepo Chromium MV3 browser extension that captures code-heavy web
content and ChatGPT conversations into deterministic Markdown. MVP
candidate, all 10 roadmap phases complete, awaiting release approval; no
tagged release. Tests: `vitest`, 160 tests, 15 release "gates", a
22-article / 87-code-block fixture corpus. Governance: `AGENTS.md` +
`CLAUDE.md`, `planning/CONTEXT.md`, `architecture/`, `decisions/` — a
governance shape close to CodeCompass's own.

It tests **conventional** development where the substantive technical
context is *not* in the package graph: DOM APIs, `MutationObserver`,
Chromium extension APIs, CommonMark / fenced-code-block semantics,
highlight.js / Prism detection, ChatGPT's DOM. Stage B measures whether
CodeCompass adds trustworthy, materially-useful context here, or whether
a fresh Claude session gets equivalent context from a couple of cheap
searches.

### 1.7 Role of Ledgerkit (harder second proof point)

`https://github.com/ctosullivan/ledgerkit` — a pure-Python
(3.8–3.12) library bridging to the `hledger` plain-text-accounting
ecosystem: journal parsing (hledger 1.52-compatible), `balance` /
`register` / `print` / `accounts` / `stats` / `check`, optional pandas
export. No runtime deps. Governance: `CLAUDE.md` / `CONTEXT.md` /
`ROADMAP.md`, `docs/` + `dev-docs/`.

Its important "dependencies" are an **executable** (`hledger`), its
**manuals / reference material**, **journal syntax**, **query
semantics**, and **observed black-box behaviour** verified by
compatibility tests. Stage D uses it to decide whether v1 scope must
expand beyond package-source grounding, and what the *smallest* useful
generalisation is. **CodeCompass does not become the hledger
experiment runner** — project-specific tools do that; CodeCompass may
consume and relate the resulting evidence.

### 1.8 Likely v1 boundaries (hypothesis, not commitment)

Based on §1.2, the redefined v1 will **probably** need:

- task-oriented context retrieval (a real answer to "what matters for
  this task");
- at least one non-package technical-dependency type (executable and/or
  reference-doc/spec), chosen empirically;
- explicit provenance so distinct knowledge sources
  (source-derived fact vs doc statement vs observed behaviour vs test
  result vs ADR vs agent inference) are not flattened.

The **exact** breadth is deliberately undecided here — it is the output
of Stages B–D, not an input. See `conditional-generalisation.md` for how
each candidate is gated.

### 1.9 Major non-goals (hard boundaries for the whole effort)

CodeCompass v1 does **not** become: a general agent orchestrator; an
autonomous development framework; a reverse-engineering or fuzzing
engine; an arbitrary application test runner; a replacement for Claude
reading source; an automatic roadmap generator; an opaque AI-memory
database; a store for every agent thought. Agents reason. Claude Code
orchestrates. Project-specific tools run project-specific experiments.
CodeCompass discovers, selects, connects, grounds, retrieves, and
explains technical context.

---

## 2. Current-state and versioning assessment

### 2.1 Package / release version — the facts

| Fact | Value | Source |
|---|---|---|
| `pyproject.toml` `version` | `1.0.0` | Phase 23 Part A (`decisions/0047`, CONTEXT.md) |
| Git tags | **none** | `git tag -l` empty |
| PyPI releases | **none** | not published (`decisions/0047` context) |
| `v0.1` / `v0.2` tags | **never cut** (deliberately deferred) | `decisions/0022`, `0030`, ROADMAP.md |
| `CHANGELOG.md` | everything under `[Unreleased]`, no dated section | CHANGELOG.md |
| `classifiers` | `Development Status :: 4 - Beta` | `pyproject.toml` |

**There is no public release history to preserve or protect.** The
constraint the task warns about ("do not rewrite published release
history") does not bind here — nothing has been published.

### 2.2 Current roadmap v1 assumptions

`planning/v1.0-initial-release-roadmap.md` and every "v1.0 scope note" in
`ROADMAP.md` treat v1.0 as: phases 20–23 + the 30–38 additions, then
`twine upload` + `v1.0` tag + `[Unreleased]` → dated section. Phases
24 (chat routing/rollup) and 25 (MCP) are proposed deferred past it
(not locked).

### 2.3 What appears complete vs what remains

**Complete and solid:** the package/source-grounding pipeline for
npm/PyPI/Cargo end to end; the context graph and its mechanical +
AI-enriched edges; generated Skills/`/discovery`; staleness; `undo`; the
governance/doc system. Phase 23 Part A (packaging readiness) is done and
the wheel is verified installable.

**Remains (existing roadmap):** Phase 23 Part B (publish — paused);
Phases 24–25 (deferred). Known smaller gaps catalogued in `CONTEXT.md`
("Still outstanding") — Cargo adapter never validated against a real
toolchain; `chat.py` never run against the real API; `staleness.py`
version parser has no real PEP 440/semver correctness; no
Skill-trigger-accuracy harness; `query skills` doesn't surface
`slash_command` rows; `/discovery` whole-project `sync` trigger gap.

**Remains (redefined v1, this package):** everything in Stages A–F.

### 2.4 Does public release history constrain redefinition? No.

Nothing is released. The redefinition is unconstrained by history. The
only real question is **what to do with `pyproject.toml`'s `1.0.0`**
before any publish (§2.5).

### 2.5 Recommended terminology / versioning strategy

**Problem:** `pyproject.toml` already says `1.0.0`, but under this
package "v1" is redefined to a milestone that is many phases away.
Publishing `1.0.0` now would (a) spend the SemVer "1.0.0 = first stable
public API" signal on a pre-validation snapshot, and (b) make "v1" mean
two different things (the published wheel vs. the internal milestone).

**Decided 2026-09-09 (gates G1, G2):**

1. **Separate the two meanings explicitly.** "**CodeCompass v1**" =
   the internal *product-validation milestone* defined by this package
   (Stage F, Phase 67). The `pyproject.toml` version string tracks the
   package's own release state under PEP 440 / SemVer.
2. **Publishing is held until redefined v1 (gate G2 → G2-b).** No PyPI
   upload, no git tag during Stages A–F. The first-ever public release is
   the redefined v1, published as `1.0.0` at Phase 67, legitimately
   earning the "validated" claim. The rejected alternative (G2-a —
   publish a `0.4.0` foundation release now for early external signal) is
   recorded in `decisions/0048`.
3. **Because no intermediate release will exist, `pyproject.toml` moves
   `1.0.0` → `1.0.0.dev0`** (gate G1) — accurately "in development toward
   the 1.0.0 that Phase 67 ships", not a phantom `0.4.0` that never gets
   released. Consistent with the project's prior practice
   (`version = "0.1.0.dev0"` before Phase 23, per `decisions/0047`).
   Keep `Development Status :: 4 - Beta`. Phase 67 drops the `.dev0`.
4. **`CHANGELOG.md`'s `[Unreleased]` section is not promoted** to a
   dated section until Phase 67.
5. **Milestone-grouping convention is preserved** (`CLAUDE.md` §6,
   `decisions/0022`/`0030`): tags are cut on *milestone-group*
   completion, not per phase. The redefined-v1 stages A–F are one
   milestone group.

`migration.md` §1 covers the mechanical steps; `proposed-governance-changes.md`
carries the ADR draft (proposed `decisions/0048`).

---

## 3. Ordered redefined-v1 roadmap

Full detail in [`roadmap.md`](roadmap.md). One-screen summary:

```
STAGE A — Redefine v1 & make CodeCompass agent-led    (COMMITTED)
  39  Reconcile repo state + versioning realignment
  40  Specialist agent roster + lead workflow
  41  Project-learning lifecycle
  42  Documentation lifecycle (incremental + blank-slate + closeout gate)
  43  Dogfood the agent-led loop on a real CodeCompass change
      ── GATE DA: agent-led loop proven end-to-end ──

STAGE B — Validate existing CodeCompass against real work  (COMMITTED protocol / EXPERIMENTAL findings)
  44  Reference-project evaluation protocol + context-quality eval spec
  45  Register Technical Clipper, pin commit, baseline evaluation
  46  Use CodeCompass during genuine Technical Clipper tasks + independent evals
  47  Consolidate recurring friction into confirmed findings
      ── GATE DB: which improvements are evidence-supported? ──

STAGE C — Improve the existing product                 (CONDITIONAL on GATE DB)
  48  Task-oriented context retrieval            (if supported)
  49  Graph / context quality                    (if supported)
  50  Shared-agent context                       (if supported)
  51  Re-run Technical Clipper evaluation — did context quality improve?
      ── GATE DC: measured improvement? ──

STAGE D — Test the broader product hypothesis         (EXPERIMENTAL)
  52  Register Ledgerkit, baseline
  53  Heterogeneous doc / reference / manual dependencies
  54  External executable / behavioural context (evidence consumed, not run, by CodeCompass)
  55  Decide whether broader dependency/evidence abstractions are necessary
      ── GATE DD: is generalisation required, and what is the minimum? ──

STAGE E — Implement the minimum justified generalisation  (CONDITIONAL on GATE DD)
  56  Technical-dependency abstraction (only what GATE DD justifies)
  57  Provenance / evidence features (only what GATE DD justifies)
  58  Migrate package/source functionality cleanly into the final model
  59  Re-run Technical Clipper + Ledgerkit validation
      ── GATE DE: existing capability preserved, new capability proven? ──

STAGE F — Define the real v1 release boundary          (COMMITTED once E completes)
  60  Blank-slate documentation reconstruction
  61  Architecture + ADR reconciliation
  62  Roadmap + context reconciliation
  63  Technical Clipper final validation
  64  Ledgerkit final validation (where in scope)
  65  Independent release audit  (FAIL blocks)
  66  Milestone closeout artifact + git tag
  67  Release redefined CodeCompass v1
```

**Committed vs experimental vs conditional vs deferred** is marked
per-phase in `roadmap.md`. Existing Phases 24 (chat routing/rollup) and
25 (MCP) are **not renumbered** — they become "deferred, revisit as
Stage C candidates if reference-project evidence supports them."

---

## 13. Risk analysis

| # | Risk | Likelihood | Mitigation in this plan |
|---|---|---|---|
| R1 | **CodeCompass context adds more overhead than value** | High for small repos | GATE DB is explicitly allowed to conclude "LOW advantage, defer improvements"; `context-quality-evaluation.md` forces an honest advantage rating; a technically-correct-but-low-value result is recorded as such, not spun. |
| R2 | **Small repos are cheaper to inspect directly** | High (both reference projects are small) | The evaluator's mandatory question "could a fresh Claude session get this from a couple of cheap searches?" and the LOW/MODERATE/HIGH advantage classification. If the answer is "yes" broadly, that is a finding that reshapes v1, not a failure to hide. |
| R3 | **Stale context becomes dangerous** (worse than missing) | Medium | Evaluation weights *misleading* > *incomplete* (task instruction + `context-quality-evaluation.md`). Freshness is a scored criterion. Staleness checking already exists; Stage C freshness work is gated on it recurring as a finding. |
| R4 | **Misleading graph relationships presented as authoritative** | Medium | Determinism-first boundary is preserved and reinforced; provenance work (Stage E, gated) exists specifically so a low-confidence claim is not shown like a source-derived fact. |
| R5 | **Context noise** (too much returned) | Medium-High | "Noise" is a scored criterion; the product direction is explicitly *small* maps, not completeness. Task-oriented retrieval (Phase 48) is gated on noise recurring as a finding. |
| R6 | **Duplicated project knowledge / opaque AI memory** | Medium | `learning-lifecycle.md`: canonical knowledge lives in reviewable repo artifacts; CodeCompass indexes/connects, never owns. Agent persistent memory is per-agent working aid only. Explicit non-goal (§1.9). |
| R7 | **Agent memory diverges from repo truth** | Medium | Recalled memories are background context, not instructions (per harness rules); knowledge curator promotes confirmed learnings *into* repo artifacts; candidate learnings carry a project-revision stamp so drift is detectable. |
| R8 | **Documentation accretion** (caveat-on-caveat) | High (already visible in `architecture/overview.md`, 1,954 lines) | `documentation-lifecycle.md`: blank-slate reconstruction at milestones + explicit reconciliation decisions (retain/rewrite/consolidate/split/replace/remove); current docs earn their place. |
| R9 | **Excessive agent/process complexity** | Medium-High | Roster is deliberately capped (`agent-led-development.md` §2); agents are added only where separation of context/authority adds value; GATE DA can prune roles that didn't earn their keep in dogfooding. |
| R10 | **Overfitting to Technical Clipper** | Medium | Two reference projects with deliberately different dependency shapes; Stage D exists to break Technical-Clipper-shaped assumptions; a Stage C improvement must survive Ledgerkit (Phase 59) before it counts toward v1. |
| R11 | **Overfitting to Ledgerkit** | Low-Medium | GATE DD demands the *minimum* generalisation; `conditional-generalisation.md` forbids a universal ontology adopted for elegance; Phase 58 migration must keep npm/PyPI/Cargo first-class. |
| R12 | **Speculative generalisation** (build the ontology anyway) | Medium | Every abstraction in Stage E is gated on a *recurring* finding with an ADR arguing the specific gap; `conditional-generalisation.md` separates "evidence exists" / "hypothesis" / "deferred" explicitly. |
| R13 | **Architectural rewrite risk** | Medium-High | `migration.md`: prefer migration over rewrite; the context graph rebuilds deterministically so schema change is additive-then-migrate, not big-bang; each Stage E phase is independently verifiable and revertible (the phase-per-commit property from `v0.2-implementation-execution-plan.md`). |
| R14 | **Indefinitely delaying a meaningful v1 release** | **High — the central risk (heightened by G2-b: nothing is published until Phase 67)** | (a) Every gate has an explicit "defer / stop" branch — the plan can conclude at GATE DC with a modest, real, measured improvement over the phases-0–38 baseline and ship *that* as `1.0.0` if Stage D evidence is weak. (b) `roadmap.md` §"Minimum viable redefined v1" defines the smallest shippable version and instructs the plan to take it rather than chase the broader hypothesis. (c) Time/phase tripwires are noted per stage. (d) If the hold starts to bite, gate G2 can be revisited to cut an interim `0.x` release — it was a preference, not a one-way door. |
| R15 | **Reference-project work distorts Technical Clipper / Ledgerkit** | Medium | Protocol rule (task instruction + `reference-project-protocol.md`): reference work is subordinate to each project's own roadmap; no feature is added to them to make CodeCompass easier to evaluate; the reference-project-tester never silently repairs CodeCompass to make its own eval pass. |
| R16 | **Governance drift** (silent CLAUDE.md / ADR edits by agents) | Medium | `CLAUDE.md` §0 preserved; `proposed-governance-changes.md` is the only route; docs-reconstructor and every agent are explicitly barred from editing protected files; DoD audit checks for it. |

---

## 7 / 14. Human-decision gates

These require explicit user approval. None blocks *writing* plans; each
blocks the *phase* that acts on it. Ordered by when they first bite.

| Gate | Decision | Needed before | Recommendation |
|---|---|---|---|
| **G1** | ✅ **DECIDED 2026-09-09** — bump `pyproject.toml` `1.0.0` → `1.0.0.dev0`; "CodeCompass v1" = internal validation milestone (Phase 67); Phase 67 drops `.dev0` and ships `1.0.0` | Phase 39 | done |
| **G2** | ✅ **DECIDED 2026-09-09 → G2-b** — hold all publishing until redefined v1; no PyPI upload, no git tag during Stages A–F; `[Unreleased]` stays undated until Phase 67 | Phase 39 | done |
| **G3** | Roadmap restructuring: add the Stage A–F milestone group to `ROADMAP.md`; retitle the existing "v1.0 scope notes" as "foundation-release scope"; keep historical tables intact; do **not** renumber phases 0–38 or 24–25 | Phase 39 | Yes — as specified in `roadmap.md` |
| **G4** | `CLAUDE.md` governance changes: new §8 (agent-led development model + learning lifecycle), amended §5 (DoD gains: independent audit PASS; candidate-learning triage; context-eval for reference-project phases), amended §1 (curator/auditor touchpoints). Full proposed diff in `proposed-governance-changes.md` | Phase 40 (agents) / Phase 41 (§8 learning) / Phase 42 | Review the diff; approve incrementally is fine |
| **G5** | Approve `decisions/0048` (redefined-v1 milestone) and `decisions/0049` (agent-led development model) — drafts in `proposed-governance-changes.md` | Phase 39 / 40 | Yes |
| **G6** | GATE DB outcome: which (if any) Stage C improvements are funded, based on Stage B findings | Phase 48 | Decided from evidence at that point |
| **G7** | GATE DD outcome: whether Stage E generalisation happens at all, and its exact minimum scope; approve the abstraction ADR(s) | Phase 56 | Decided from evidence at that point |
| **G8** | Any CLI breaking change introduced by Stage C or E migration (`migration.md` flags each) | The specific phase | Prefer additive; breaking changes need their own ADR + this gate |
| **G9** | Redefined-v1 release: drop `.dev0` → `1.0.0`, `twine upload` (first-ever publish), `v1.0.0` tag, `[Unreleased]` → dated section, public positioning change | Phase 67 | The terminal gate; same irreversibility posture as the old Phase 23 Part B |
| **G10** | Public product positioning / messaging change (README "what it is", `ai-docs/`) from "dependency reference docs" to "task context map for agents" | Phase 60–67 | Decided at closeout with the reconstructed docs in hand |

### Success criteria for *this planning session* (all met)

1. current repo state inspected ✓ (§1.1, §2)
2. release/version state established ✓ (§2.1 — nothing published)
3. existing v1 definition critically assessed ✓ (§1.2)
4. coherent redefined v1 proposed ✓ (§1.4, `roadmap.md`)
5. existing capabilities preserved where valuable ✓ (§1.3, `migration.md`)
6. agent-led development is the first prerequisite ✓ (Stage A, §1.5)
7. project-learning lifecycle planned ✓ (`learning-lifecycle.md`)
8. documentation renewal lifecycle planned ✓ (`documentation-lifecycle.md`)
9. current Technical Clipper repo inspected ✓ (§1.6, `reference-project-protocol.md` §"Inspection findings")
10. Technical Clipper established as first reference project ✓
11. reference work uses genuine roadmap tasks, not benchmarks ✓ (`reference-project-protocol.md` §"Task selection")
12. context-quality evaluation explicitly defined ✓ (`context-quality-evaluation.md`)
13. subsequent improvements driven by Technical Clipper evidence ✓ (Stage C gated on GATE DB)
14. Ledgerkit established as harder second reference project ✓ (`ledgerkit-plan.md`)
15. dependency/evidence generalisation stays evidence-conditional ✓ (`conditional-generalisation.md`)
16. final v1 closeout includes doc reconstruction + independent audit ✓ (Stage F)
17. each implementation phase has a DoD + exit gate ✓ (`roadmap.md`, Stage A phase files)
18. speculative scope separated from committed scope ✓ (`roadmap.md` labels)
19. governance/version decisions needing approval surfaced ✓ (§7)
20. no broad implementation started ✓ (planning only)
21. plans sufficient for a fresh session to implement the first approved phase ✓ (`planning/phase-39-*.md` … `phase-44-*.md`)
