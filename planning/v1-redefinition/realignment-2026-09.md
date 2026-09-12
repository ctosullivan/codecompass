# v1 realignment — Ledgerkit-first, GPL-3.0-or-later, adoption blueprint (2026-09-12)

**Planning only. No implementation has started from this document.** This
amends the v1-redefinition package (`README.md` and its siblings) in light
of a strategic redirection: reorder the remaining roadmap so **Ledgerkit**,
not Technical Clipper, is the next external reference project; plan a
**GPL-3.0-or-later** relicensing (aligning with `hledger`); and require
CodeCompass to produce a **reusable agent-led adoption blueprint** before
the next round of architectural expansion.

Read this alongside `README.md` (still authoritative for what it isn't
superseding) and `roadmap.md` (amended in the same commit as this file).

---

## 1. Current-state assessment (this session, 2026-09-12)

### 1.1 CodeCompass itself

| Aspect | Finding |
|---|---|
| Stage A (redefine v1, make CodeCompass agent-led) | **`done`.** Phases 39–43 done, GATE DA passed (roster stays at 7, 4 process amendments). Phases 43b (`check_user_docs.py` standing-drift checks + `architecture/overview.md` §C fix) and 43c (agent context-suggestion pathways + context-health planning) also **`done`**. |
| Agent roster | **8** agents: `context-evaluator`, `reference-project-tester`, `docs-maintainer`, `roadmap-context-curator`, `knowledge-curator`, `docs-reconstructor`, `release-phase-auditor`, and **`context-health-planner`** (added Phase 43c). |
| Agent-suggested-edge / usefulness-evaluation capability | **Already built** (Phase 43c, `decisions/0051`): `planning/context-gaps/` is a capture pathway for relationships an agent believes the graph should hold but mechanical detection cannot produce; `planning/context-use-log.md` records a LOW/MODERATE/HIGH context-vs-default-pathway advantage per real use; both are captured as reviewable candidates and **never written to `context-graph.db`** — promotable only via the learning lifecycle into a Stage-C detection heuristic or a Stage-E graph capability, each gated on evidence. This is the mechanism this task calls "agent-suggested edges / usefulness evaluation" — it exists; it is not being replaced, only **exercised at scale by Ledgerkit** (§4 below) and, if warranted by recurrence, promoted. |
| Deterministic/suggested/evaluated/rejected relationship lifecycle | Effectively defined already: `candidate` → `recurred` → `promoted-to-roadmap` / `discarded` (`planning/context-gaps/README.md`). No new lifecycle needed; Ledgerkit dogfooding is what will actually exercise `recurred` for the first time (Phase 43c's only entry, `CG-001`, is still `candidate` — single observer). |
| Claude entry points | Root `CLAUDE.md` routing table (per-vendor rows: path/version/enriched/deps-link/"consult when"), 5 generated Skills (tool-level + 3 per-vendor + one third-party), 3 Cursor `.mdc` rules, `/discovery` slash command. All generated from `src/`, none hand-maintained (Phase 43's `check_generated_artifacts_match_source`, Phase 43b, now guards this mechanically). |
| Context-quality evaluation methodology | Defined (`context-quality-evaluation.md`): PASS/PASS WITH GAPS/FAIL + LOW/MODERATE/HIGH advantage, "incorrect > incomplete", evaluator inspects the target directly and never uses CodeCompass to validate CodeCompass. Not yet exercised against any reference project — Stage B (Phase 44) hasn't started. |
| Tests | 554 passed / 1 skipped (`pytest`), `ruff` clean, `check_user_docs.py --strict` clean (14 mechanical doc-drift rules). |
| Version / release | `pyproject.toml` `1.0.0.dev0`. **No git tags. Never published to PyPI** (confirmed: `git tag -l` empty). Gate G2-b (hold all publishing until redefined v1) stands, reaffirmed by this realignment — see §7. |
| Licence | **MIT** (`LICENSE`, `pyproject.toml` `license = { text = "MIT" }`, classifier `License :: OSI Approved :: MIT License`, `README.md` §"License"). |
| Copyright / contribution history | **Single author, single copyright holder.** `git log --format='%an <%ae>'` returns exactly one identity across all 129 commits (`ctosullivan`). `pyproject.toml` `authors = [{ name = "Cormac O' Sullivan" }]` matches. **No third-party contributions to seek consent for.** |
| Bundled/vendored third-party source | **None committed.** `vendor/` (the per-dependency cloned-upstream-source directories CodeCompass itself generates) is entirely `.gitignore`d (`decisions/0004`/`0010`) — CodeCompass's own repository contains none of its tracked dependencies' source. Relicensing has no bundled-code entanglement. |
| Runtime dependencies' licences | `typer`, `rich`, `anthropic`, `pipdeptree` — all **MIT** (confirmed via `pip show`). No GPL-incompatibility risk from depending on them (permissive libraries used by a GPL-3.0-or-later application is standard and unproblematic; this is a one-way compatibility, not a requirement that they also be GPL). |
| `CONTRIBUTING.md` licence mentions | **None** — nothing to update there beyond the same-commit sync `CLAUDE.md` §2 already requires. |
| `planning/reference-projects/` | **Does not exist yet** — Phase 44 (Stage B's first phase) has not started. Nothing to un-register or re-target; the reorder costs nothing here. |

### 1.2 hledger (the compatibility reference, inspected live)

| Aspect | Finding |
|---|---|
| Licence | **GPL-3.0-or-later**, confirmed at the SPDX-field level (`hledger/package.yaml`, `hledger-lib/package.yaml`: `license: GPL-3.0-or-later`) — not merely GitHub's coarse `gpl-3.0` detection. This is exactly the target licence string this task specifies; no ambiguity to resolve. |
| Stable release | **1.52.4** (published 2026-09-10, non-prerelease) is the current stable line. `1.99.4` (published 2026-09-11) is a **prerelease** — the in-progress "2.x" preview branch this task's own guidance says to *monitor*, not target now. |
| Implication for Ledgerkit / CodeCompass | Confirms the existing `ledgerkit-plan.md` assumption ("hledger 1.52 compatibility") needs **no correction** — it was already targeting the right stable baseline. No architecture separation work is owed yet beyond what `conditional-generalisation.md` already reserves for a hypothetical future hledger-2 profile. |

### 1.3 Ledgerkit (the next reference project, inspected live via `gh`)

| Aspect | Finding |
|---|---|
| Licence | **MIT** (`gh repo view` `licenseInfo.key: mit`). Ledgerkit's own relicensing (if any) is Ledgerkit's decision, not this task's — CodeCompass's licence change is about aligning *CodeCompass* with the ecosystem it's now inspecting more deeply, not about Ledgerkit. |
| Governance | `CLAUDE.md` (root) + `CONTEXT.md` (root, explicitly "throwaway... overwritten completely") + `ROADMAP.md` (root, milestone-numbered `[DONE]`/`[IN PROGRESS]`/`[PLANNED]`/`[BACKLOG]`) + a `knowledge/` folder (`DECISIONS.md`, `EDGE_CASES.md`, `ANTIPATTERNS.md`, `DOMAIN_RULES.md`) + `dev-docs/` (`architecture.md`, `api-spec.md`, `hledger-compatibility.md`). A different shape from CodeCompass's own (no `decisions/` ADR folder; project-specific knowledge lives in `knowledge/` instead) — the adoption blueprint (§3) must generalise across this shape, not assume CodeCompass's own folder layout. |
| Current roadmap state | Milestones 0–4 `[DONE]` (foundation, journal parser, core reports, comprehensive hledger-1.52 format compatibility — 485 tests passing as of Milestone 4). **Milestone 5 — CLI Filter Flags is `[PLANNED]`, next up**: wiring the existing `Query` dataclass to CLI flags (`--account`, `--date-from`/`--date-to`, `--payee`, `--depth`) across `balance`/`register`/`accounts`/`stats`. A `Future/Backlog` table exists for lower-priority items (periodic/auto postings explicitly "out of scope for v1"; account-type inference; `EditorDocument` include-directive support, implying a companion **Ledgerkit Editor** project). |
| Runtime dependencies | Pure Python, stdlib only (`pandas` optional/extra). |
| Why Milestone 5 is a strong genuine-task candidate for the Stage B baseline | It is real, next, and already scoped by the maintainer (not invented for CodeCompass) — squarely satisfying this task's "use a genuine current task, not a constructed benchmark" rule. It also touches exactly the kind of context this realignment is testing for: the `Query` dataclass (local Python), the hledger 1.52 manual's query-flag semantics (external reference material), and the existing `dev-docs/hledger-compatibility.md` compatibility ledger (a project-local compatibility record) — three different evidence kinds in one task. |

### 1.4 What this confirms about the strategic premise

- The prompt's central claim — "Ledgerkit's important technical dependencies span local Python source, hledger source, hledger manuals, specifications, tests, executable behaviour, compatibility contracts, intentional divergences, local architecture decisions" — holds up under direct inspection. Its immediate task (Milestone 5) alone already touches three of those kinds.
- `hledger`'s actual GPL-3.0-or-later declaration and stable-1.52/preview-1.99 split match the existing plan's assumptions exactly — nothing here forces a design change, only a **reordering** (Ledgerkit before Technical Clipper) and the **two genuinely new work items** (relicensing, adoption blueprint) identified in §1.1.
- CodeCompass's relicensing is legally simple (single copyright holder, no bundled third-party source, permissive runtime deps) — the complexity in §5 is about **doing it as a deliberate, documented, gated milestone**, not about resolving any actual legal tangle.

---

## 2. What already satisfies this task's requirements (do not rebuild)

Reconciling this task's prompt against the current repository, the
following requested capabilities **already exist** and are not being
redesigned — only pointed at Ledgerkit and, where the prompt asks for
something adjacent-but-new, extended:

| Requested in this task | Existing artifact | Disposition |
|---|---|---|
| Agent-led CodeCompass development before major expansion | Stage A (39–43), `decisions/0049`, `agent-led-development.md`, `agent-led-workflow.md` | **Done.** Nothing to redo. |
| Minimal specialist roles, independence, no orchestrator inside CodeCompass | The 8-agent roster (§1.1) | **Done.** The roster review this task implies (§1.1's Stage-B-review item) already happened at GATE DA + the 43c addition; no further pruning is indicated. |
| Preserve Claude/agent entry points as routing, not context dumps | Root `CLAUDE.md` table, generated Skills, `/discovery` | **Done and holding** — `check_generated_artifacts_match_source` (Phase 43b) now mechanically guards against entry points drifting from their generators. |
| Agent-suggested relationships; correctness vs usefulness evaluated separately; not silently authoritative | `planning/context-gaps/`, `decisions/0051` | **Done** (Phase 43c). Ledgerkit dogfooding is precisely what will generate real volume for it (§4). |
| Project-learning lifecycle (observation → candidate → evidence → curation → promote/retain/discard) | `planning/learnings/`, `learning-lifecycle.md`, `decisions/0050` | **Done.** |
| Documentation lifecycle (incremental + blank-slate milestone reconstruction) | `documentation-lifecycle.md`, `docs-reconstructor` (dual mode) | **Done.** |
| Context-quality evaluation methodology (PASS/PASS WITH GAPS/FAIL, LOW/MODERATE/HIGH) | `context-quality-evaluation.md`, `context-evaluator` | **Done as a spec; not yet exercised** — Stage B's job. |
| A Ledgerkit reference-project plan | `ledgerkit-plan.md` | **Exists**, written for the old Stage D slot. Promoted to Stage B position + extended with the context-curator finding format this task adds (§6) — see amendments in §4/§6. |
| A repeatable reference-project protocol | `reference-project-protocol.md` | **Exists**, generic (§2 of that file). Its Technical-Clipper-specific content is repositioned, not deleted — Technical Clipper still uses the same protocol, just later (§5). |
| Conditional technical-dependency/evidence generalisation, evidence-gated | `conditional-generalisation.md` | **Exists**, already forbids a premature universal ontology and already structures the GATE-DD decision procedure. Phase-number cross-references updated only. |

**Net new work this realignment actually adds:** the GPL-3.0-or-later
relicensing plan (§5); the reusable agent-led adoption blueprint (§6.1);
the CodeCompass feedback-ingestion process for Ledgerkit's context-curator
findings (§6.2); and the roadmap reorder itself (§4).

---

## 3. Why the v1 boundary still holds (not reopened)

`decisions/0048`'s definition of the redefined-v1 milestone —
agent-led development, evaluated relationships, real reference-project
work, evidence-driven improvement, generalisation checks against a
materially different second project, disciplined learning/doc
lifecycles, independently verified context quality — is **unchanged**
by this realignment. What changes is:

1. **Which reference project goes first** (Ledgerkit, not Technical
   Clipper — §4), because it is the stronger test of CodeCompass's
   distinctive value: a project whose important dependencies are mostly
   *not* packages, confirmed by direct inspection (§1.3), not assumed.
2. **What licence CodeCompass ships under** (§5) — an alignment
   decision, not a product-scope decision.
3. **That CodeCompass must also produce something Ledgerkit (and future
   projects) can adopt** (§6.1) — a new deliverable, not a redefinition
   of what v1 *is*.

The guiding v1 product principle from `README.md` §1.4 stands verbatim:
*"Give AI development agents a small, trustworthy, version-correct map
of the technical context relevant to their task, with clear routes back
to evidence."* Technical Clipper's earlier role (proving CodeCompass adds
value on conventional package-graph-poor projects) is **not discarded** —
it becomes the cross-ecosystem regression check that verifies whatever
Ledgerkit-driven changes land don't overfit to accounting/hledger (§4,
Stage F).

---

## 4. Revised roadmap — the reorder, at a glance

Full detail in the amended [`roadmap.md`](roadmap.md) (same commit).
Phases 39–43 (+ 43b, 43c) are **unchanged, `done`, not renumbered** —
this section only concerns Stage A's two new bridge phases and
everything from Stage B onward, none of which has started (confirmed:
`planning/reference-projects/` doesn't exist; only `phase-44-*.md` has a
plan file, still `planned`). Renumbering **not-yet-started** phases has
direct precedent in this project (the Phase-9→16 "Retire `Depth`"
reorder, `ROADMAP.md`'s renumbering note) and is the clean choice here
for the same reason: nothing in flight breaks.

```
STAGE A — Redefine v1 & make CodeCompass agent-led         (done, + 2 new bridge phases)
  39–43   (done — GATE DA passed)
  43b     (done — standing-doc-drift checks + arch.md fix)
  43c     (done — agent context-suggestion pathways + context-health)
  43d     GPL-3.0-or-later relicensing PLAN + human gate          ← NEW
  43e     Reusable agent-led adoption blueprint                    ← NEW

STAGE B — Ledgerkit baseline                     (COMMITTED protocol / EXPERIMENTAL findings)
  44      Reference-project protocol + context-quality eval spec  (unchanged; retargets "writes Phase 45" to Ledgerkit)
  45      Register Ledgerkit, pin commit, baseline evaluation      ← was Stage D's Phase 52
  46      Genuine Ledgerkit task (Milestone 5: CLI filter flags) + independent evals
  47      Consolidate findings                              ── GATE DB ──

STAGE C — Evidence-driven CodeCompass improvements       (CONDITIONAL on GATE DB)
  48      Task-oriented context retrieval        (if supported)
  49      Graph / relationship model improvements (if supported)
  50      Shared-agent-context / entry-point improvements (if supported)
  51      Re-run Ledgerkit evaluation — did context quality improve? ── GATE DC ──

STAGE D — Deeper Ledgerkit dogfooding                    (EXPERIMENTAL)
  52      Continue genuine Ledgerkit Core development with CodeCompass
  53      Heterogeneous doc/reference/manual dependency test (hledger manual ↔ code ↔ tests)
  54      Behavioural/executable evidence test (hledger executable, differential verification)
  55      Decide: is broader generalisation necessary + refine the blueprint  ── GATE DD ──

STAGE E — Implement the minimum justified generalisation  (CONDITIONAL on GATE DD)
  56      Technical-dependency abstraction        (only what GATE DD justifies)
  57      Provenance/evidence features             (only what GATE DD justifies)
  58      Migrate package/source functionality cleanly into the final model
  59      Re-run Ledgerkit validation                                ── GATE DE ──

STAGE F — Cross-ecosystem regression: Technical Clipper    (COMMITTED protocol / EXPERIMENTAL findings)  ← MOVED HERE
  60      Register Technical Clipper, pin commit, baseline evaluation
  61      Genuine Technical Clipper task(s) + independent evals
  62      Consolidate: package/vendor context still strong? relationships generalise? no accounting-specific overfit? entry points still lean?
  63      Decision — fix only general problems with evidence          ── GATE DF ──

STAGE G — v1 consolidation                                (COMMITTED once F completes)
  64      Blank-slate documentation reconstruction
  65      Architecture + ADR reconciliation
  66      Roadmap + context reconciliation
  67      Self-dogfood + Ledgerkit + Technical Clipper final confirmation (lightweight — the heavy lifting already happened in D/F)
  68      Independent release audit  (FAIL blocks)
  69      Milestone closeout artifact + git tag
  70      Release redefined CodeCompass v1                            ── gate G9 ──
```

### 4.1 Why this mapping, not a bigger rewrite

- **GATE letters keep their meaning.** GATE DB/DC/DD/DE occupy the same
  *relative* position they always did — DB and DC just now run on
  Ledgerkit evidence instead of Technical Clipper's, and DD is **literally
  the same decision** the old Stage D's Phase 55 already described
  ("is a generalised technical-dependency concept necessary, what
  evidence, what is the smallest model") — that content moves down to
  the new Phase 55 almost unchanged. Only **GATE DF** is new (Technical
  Clipper's regression check, which the old plan didn't have its own
  letter for).
- **Stage C, E's content is unchanged**, just Ledgerkit-driven instead of
  Technical-Clipper-driven and renumbered by the same offset.
- **Stage G is the old Stage F**, renumbered +4 (to make room for
  Stage F's new Technical-Clipper-regression slot), with one addition
  (an explicit "self-dogfood" line, folded into a single consolidation
  phase rather than three separate re-validation phases — Stage D and F
  already did the heavy Ledgerkit/Technical-Clipper re-validation work,
  so Stage G's version is a final confirmation, not a repeat).
- **`ledgerkit-plan.md`'s existing Stage-D content (old Phases 52–55)
  becomes Stage B+D's content** (Phases 45–47 for the baseline, 52–55 for
  the deeper dogfooding) — nothing in it was Technical-Clipper-specific
  to begin with, so it ports over with a phase-number and stage-letter
  change only.
- **`reference-project-protocol.md`'s Technical-Clipper-specific content
  (old Phases 45–47) becomes Stage F's content (new Phases 60–63)** — the
  *generic* protocol (§2 of that file) is unchanged and now serves
  Ledgerkit first, Technical Clipper second, exactly as designed (it was
  always written to be reusable).

### 4.2 Phase-43d and 43e — the two new Stage A bridge phases

Neither has a phase-N plan file written yet in this session (per the
established discipline — `README.md`: "later phases exist only as
roadmap rows until the evidence gates ahead of them resolve" — except
these two are immediately next, so they get real plan files alongside
this package, same as 39–44 did originally).

- **`planning/phase-43d-gpl-relicensing-plan.md`** — writes the licence
  migration plan (§5) as a phase, with the actual mechanical edits
  **held behind gate G11** (new — §7). Planning-only until approved.
- **`planning/phase-43e-agent-led-adoption-blueprint.md`** — writes
  `adoption-blueprint.md` (§6.1). No governance gate (pure planning/doc
  artifact, same shape as 43c) but **held, along with everything else in
  this package, until the user reviews this realignment** — this is a
  planning *session*; nothing implements until the user says so.

---

## 5. Licence migration — GPL-3.0-or-later (required output 3)

Full detail: [`licence-migration.md`](licence-migration.md). Summary:

- **Current:** MIT, single copyright holder, no bundled third-party
  source, no other contributors to consult (§1.1).
- **Target:** `GPL-3.0-or-later`, matching hledger's own SPDX declaration
  exactly (§1.2) — the explicit purpose being to let Ledgerkit-facing
  CodeCompass development inspect `hledger` source directly without an
  artificial clean-room restriction, while keeping the hledger
  **executable** as an independent behavioural oracle regardless of
  licence (source access changes what agents may *read and understand*;
  it does not replace differential/behavioural verification — this
  applies to *Ledgerkit's* development methodology, not CodeCompass's own
  redistribution needs, since CodeCompass never bundles hledger).
- **Files/metadata to change** (mechanical, once gated — §7 G11):
  `LICENSE` (replace text; GPL-3.0-or-later's own boilerplate is the
  canonical `COPYING` text, unmodified per the FSF's own instructions —
  do not paraphrase it), `pyproject.toml` (`license` field +
  classifier), `README.md` §"License", any generated-template licence
  mentions (checked — none found; `check_generated_artifacts_match_source`
  and a manual grep confirm no generator embeds a licence string today).
- **Provenance/attribution policy for source-assisted development**
  (this task's distinct requirement, but relevant here because the
  licence change is what makes it legally comfortable): recorded in
  `licence-migration.md` §4 and cross-referenced from
  `adoption-blueprint.md` (§6.1) since it's a policy every project
  adopting the blueprint inherits, not just CodeCompass's own use of it
  against Ledgerkit/hledger.
- **ADR:** proposed draft `decisions/0053` in
  `proposed-governance-changes.md` §C (not yet written to `decisions/`).
- **Human-decision gate G11** — explicit approval required before any
  file changes; see §7.

---

## 6. Two new planning artifacts (required outputs 6, 10)

### 6.1 Reusable agent-led adoption blueprint

Full detail: [`adoption-blueprint.md`](adoption-blueprint.md). This is
the "reusable blueprint another repository can adopt" this task asks
for — extracted and generalised from `agent-led-development.md` +
`agent-led-workflow.md` + the 8 agent briefs, with an explicit
generic/project-specific/optional/CodeCompass-generated/manually-governed
split so Ledgerkit (and later projects) can tell what to copy verbatim,
what to adapt, and what only makes sense for CodeCompass itself.

### 6.2 CodeCompass feedback-ingestion plan

Full detail: [`codecompass-feedback-ingestion.md`](codecompass-feedback-ingestion.md).
Defines the standard finding format (finding ID, both projects'
revisions, task/session, context required vs. supplied, evaluator
verdict, manual-rediscovery record, impact classification, evidence,
generalised proposed improvement, recommendation, priority), where
findings land in *this* repository for review, and the promotion rules
(a finding becomes a strong roadmap candidate only when incorrect
context / a genuine blocker / recurrence / clear generalisation / a
second project's need / a measured prototype improvement / a
repeatedly-useful suggested relationship applies — never "Ledgerkit hit
friction" alone). Ledgerkit's own context-curator produces the findings;
CodeCompass reviews, classifies, and — only when justified — turns one
into roadmap work.

---

## 7. Human-decision gates added by this realignment

These are **additional** to `README.md` §7/§14's existing table (G1–G10,
all resolved except G6–G10 which remain conditional on later evidence).
None blocks *writing* plans; each blocks the *phase* that acts on it.

**All three resolved 2026-09-12** ("Proceed as recommended").

| Gate | Decision | Needed before | Resolution |
|---|---|---|---|
| **G11** | Roadmap restructuring: Ledgerkit becomes the Stage B reference project, Technical Clipper moves to a new Stage F cross-ecosystem-regression role; phases 45–67 renumbered (none started); GATE letters DB/DC/DD/DE keep their meaning, GATE DF is new | Phase 44's retarget (its "writes Phase 45" line) and any Phase 45+ work | ✅ **Approved** — `decisions/0052` Accepted; `roadmap.md` amended |
| **G12** | GPL-3.0-or-later relicensing: replace `LICENSE`, `pyproject.toml` metadata, README/docs licence statements; publish ADR `decisions/0053` | Phase 43d's mechanical step (planning itself is ungated) | ✅ **Approved and executed** (Phase 43d) — `LICENSE`/`pyproject.toml`/`README.md`/`CONTRIBUTING.md` updated; `decisions/0053` Accepted |
| **G13** | Agent-led adoption blueprint: approve `adoption-blueprint.md` as the version CodeCompass hands to Ledgerkit (and, later, other adopting projects) | Phase 43e completion / before Ledgerkit applies it (Stage B) | ✅ **Approved** (Phase 43e) |

This mirrored the original v1-redefinition session's own posture — plan
first, gates surfaced, proceed only on explicit instruction — which the
user then gave ("Proceed as recommended").

---

## 8. Risks specific to this realignment (additive to `README.md` §13)

| # | Risk | Mitigation |
|---|---|---|
| R17 | **Relicensing regret / downstream confusion** (a licence change, even a legally simple one, changes what others may do with CodeCompass) | Gate G12; explicit ADR `decisions/0053` arguing the specific reason (source-assisted hledger-facing development, not a generic preference); no retroactive claim about unpublished history (there is none to rewrite — §1.1) |
| R18 | **Treating "GPL alignment" as licence permission to copy hledger source into CodeCompass wholesale** | `licence-migration.md` §4's provenance policy explicitly distinguishes source inspection / algorithm understanding / adapted implementation / directly translated material / upstream-derived tests, each with its own attribution requirement; this is a Ledgerkit-methodology concern this task explicitly asks CodeCompass's own planning to record, even though CodeCompass itself never bundles hledger code |
| R19 | **The reorder is treated as a green light to redesign CodeCompass for Ledgerkit before baseline evidence exists** | Explicitly forbidden (§4, Phase 44/45): Stage B starts with CodeCompass *as it exists*; Stage C is the only place evidence-driven changes land, gated on GATE DB |
| R20 | **The adoption blueprint becomes a large autonomous-development framework** | `adoption-blueprint.md` is scoped as "a practical project-development protocol", explicitly not a framework; kept to the same roster-cap discipline `agent-led-development.md` already established (R9) |
| R21 | **CodeCompass's feedback-ingestion process becomes Ledgerkit's roadmap remote control** | `codecompass-feedback-ingestion.md`'s promotion rules (§6.2) are explicit gatekeeping; Ledgerkit's context-curator produces evidence, CodeCompass's own review decides — never automatic |
| R22 | **Technical Clipper's later slot causes it to go stale as a regression check** (its repo may have moved materially by Stage F) | `reference-project-protocol.md`'s registration step already requires re-confirming the live repo state at the phase that uses it ("confirm at Phase 46 — its state may have moved" — same discipline now applies at the renumbered Stage F phase) |

---

## 9. Success criteria for this realignment session (all met)

1. Current CodeCompass state inspected directly (§1.1) — not assumed from the prompt.
2. Current agent-suggested-edge work (Phase 43c) understood and pointed at, not replaced (§1.1, §2).
3. Current v1/release state reassessed — no tags, no PyPI release, G2-b reaffirmed (§1.1, §7).
4. hledger's actual licence and stable-release state inspected live (`gh`) — GPL-3.0-or-later confirmed exactly, 1.52.4 stable / 1.99.x preview confirmed (§1.2).
5. Ledgerkit's actual current repo/governance/roadmap inspected live (`gh`) — MIT, single-copyright, Milestone 5 next (§1.3).
6. A GPL-3.0-or-later migration plan exists, gated (§5, `licence-migration.md`, gate G12).
7. Agent-led CodeCompass development confirmed already prioritised and complete before this realignment (§1.1, §2) — no reordering needed there.
8. A reusable agent-led adoption blueprint is planned (§6.1, `adoption-blueprint.md`, gate G13).
9. Claude entry points remain the routing mechanism, unchanged and now mechanically guarded (§1.1, §2).
10. Relationship correctness and usefulness stay independently evaluated via the existing Phase 43c mechanism, not re-designed (§1.1, §2).
11. Ledgerkit is explicitly the next external project tested (§4, Stage B).
12. Ledgerkit testing begins with current CodeCompass, using a genuine current Ledgerkit task (Milestone 5), not a Ledgerkit-specific CodeCompass redesign (§1.3, §4 Phase 46).
13. A CodeCompass feedback-ingestion path for Ledgerkit's context-curator findings is defined (§6.2).
14. Recurring findings — not speculation — remain the only path to architectural change (Stage C gated on GATE DB; `codecompass-feedback-ingestion.md`'s promotion rules).
15. Technical Clipper is repositioned as the later cross-ecosystem regression/generalisation test, not dropped (§4, Stage F).
16. Broader technical-dependency/evidence models remain conditional on evidence (`conditional-generalisation.md`, cross-references updated only).
17. The project-learning and documentation-renewal lifecycles are unchanged and confirmed still fit for purpose (§1.1, §2).
18. Historical roadmap work (phases 0–43c) is preserved, unchanged, not renumbered (§4).
19. The revised roadmap has clear phase dependencies, DoDs (inherited from the existing per-phase DoD in `CLAUDE.md` §5), and gate positions (§4, `roadmap.md`).
20. `CLAUDE.md` itself is untouched by this session (confirmed: no edit made; any future governance change still goes through §0's diff-and-approve process — none is proposed here).
21. The final v1 release gate (G9) is unchanged and still requires explicit approval (§7, unchanged from `README.md`).
22. No broad implementation has started (planning artifacts + two small, ungated-content phase plan files only).
23. A fresh subsequent session could implement Phase 43e (the blueprint) or, once G12 resolves, Phase 43d (the licence mechanics), using only this package.

**Update, same day (2026-09-12):** the user resolved all three gates
("Proceed as recommended"). Phase 43d (GPL-3.0-or-later relicensing) and
Phase 43e (adoption blueprint) executed the same session — see their
plan files' status lines, `decisions/0052`/`0053` (`Accepted`), and
`planning/retros/phase-43d-gpl-relicensing-plan.md` /
`phase-43e-agent-led-adoption-blueprint.md`. This §9 list above remains
the historical record of the planning-only commit's own state at the
time it was written (`411cda6`) — not retroactively edited.
