# Reference-project plan — Ledgerkit (required output 9)

**Amended 2026-09-12 (`realignment-2026-09.md`, gate G11): Ledgerkit is
now the Stage B / first reference project**, not the harder second one —
Technical Clipper moved to a new Stage F cross-ecosystem-regression role.
This document's content (originally written for the old Stage D slot,
Phases 52–55) is otherwise unchanged in substance; only phase numbers and
stage references were updated (§2 below now covers Phases 45–47 + 52–55,
split across the new Stage B baseline and Stage D deeper-dogfooding).

Repo: **https://github.com/ctosullivan/ledgerkit**

## 1. Inspection findings

**Re-confirmed live 2026-09-12** (via `gh`, superseding the 2026-09-09
desk assessment where it differs):

| Aspect | Finding |
|---|---|
| Purpose | "A bridge to the hledger plain-text accounting ecosystem." Parse journal files, query transactions, export reports to pandas DataFrames. |
| Language | Pure Python 3.8–3.12. **No third-party runtime dependencies.** `pandas` is an optional extra. |
| Structure | `/ledgerkit` (library), `/tests`, `/docs` (user), `/dev-docs` (architecture + API specs). |
| Features | Journal parsing "compatible with hledger 1.52 format"; directives (`include`, `account`, `commodity`, `payee`, `alias`, price rules); CLI `balance` / `register` / `print` / `accounts` / `stats` / `check`; multi-commodity tree rollup. |
| hledger alignment | Modelled "primarily on the hledger 1.52 specification"; credits hledger's maintainer. |
| Governance | `CLAUDE.md` (root) + `CONTEXT.md` (root, explicitly "throwaway... overwritten completely") + `ROADMAP.md` (root, milestone-numbered) + a `knowledge/` folder (`DECISIONS.md`, `EDGE_CASES.md`, `ANTIPATTERNS.md`, `DOMAIN_RULES.md`) + `dev-docs/` (`architecture.md`, `api-spec.md`, `hledger-compatibility.md`). No `decisions/` ADR folder — a different governance shape from CodeCompass's own (`adoption-blueprint.md` must generalise across this). |
| Current roadmap state (live, 2026-09-12) | Milestones 0–4 `[DONE]` (foundation; journal parser; core reports; comprehensive hledger-1.52 format compatibility — 485 tests passing at Milestone 4). **Milestone 5 — "CLI Filter Flags" is `[PLANNED]`, next up**: wire the existing `Query` dataclass to `--account`/`--date-from`/`--date-to`/`--payee`/`--depth` CLI flags across `balance`/`register`/`accounts`/`stats`. A `Future/Backlog` table holds lower-priority items (periodic/auto postings explicitly out of scope for v1; account-type inference; `EditorDocument` include-directive support — implying a companion **Ledgerkit Editor** project). |
| Confirm at Phase 45/46 | current roadmap state, test layout, `dev-docs/` contents, current priorities — the repo will have moved again by then. |

### Why this is the harder test

Ledgerkit's real technical dependencies are, in rough order of
importance:

1. the **`hledger` executable** — its actual runtime behaviour;
2. **hledger manuals / reference documentation** — journal format,
   query semantics, the `hledger`/`hledger-ui`/`hledger-web` command
   docs;
3. **journal syntax** as a file-format / grammar;
4. **query semantics** (hledger's query language);
5. general **accounting / plain-text-accounting reference material**;
6. **observed black-box hledger behaviour** (where docs are silent or
   ambiguous, established by experiment);
7. the **local Ledgerkit implementation**;
8. **compatibility tests** pinning 1–7 together.

None of 1–6 is a package. CodeCompass's current model represents exactly
one of these (7, partially, as "the project's own source") and relates
nothing.

## 2. Stage B + D plan

**Phase 45** (Stage B baseline) is this document's §"Phase 45" below;
**Phases 52–55** (Stage D, deeper dogfooding) continue it once Stage B/C
evidence is in. Both use the same protocol
(`reference-project-protocol.md` §2), just at different depths.

### Phase 45 — Register + baseline (EXPERIMENTAL)
Clone at a pinned commit; run CodeCompass as-is; record the (expected
near-empty) result precisely; `context-evaluator` baseline report for
2–3 "what does this depend on / what governs this behaviour" questions.
Output: `planning/reference-projects/ledgerkit.md`. (Phase 46 then runs
the genuine current task — Milestone 5's CLI filter flags, §1 — through
the full per-task procedure; Phase 47 consolidates — GATE DB.)

### Phase 52 — Continue genuine Ledgerkit Core development (EXPERIMENTAL)
Further real tasks beyond Phase 46's single baseline, drawn from
Ledgerkit's own roadmap at the time (confirm live — it will have moved
past Milestone 5 by this point).

### Phase 53 — Doc / reference test (EXPERIMENTAL)
Question: can CodeCompass usefully **index and relate reference
material** — the hledger manual (as fetched/vendored text), the journal
format spec, command docs — to Ledgerkit's local implementation and
compatibility tests, **as evidence nodes with provenance**, without a
premature schema commitment?

- Try it with the mechanisms that already exist: register the manual
  text the way vendor upstream docs are registered (`kind='vendor_doc'`
  precedent, Phase 27/29); see whether mechanical mention-detection +
  the doc-relations graph produce anything trustworthy linking "manual
  section on X" ↔ "ledgerkit code implementing X" ↔ "test verifying X".
- `context-evaluator` rates whether the resulting relations are accurate,
  grounded, and materially useful for a real Ledgerkit task (e.g. a
  journal-directive compatibility fix).

### Phase 54 — Behavioural / executable test (EXPERIMENTAL)
Question: can CodeCompass **consume and relate** externally-produced
behavioural evidence?

- **CodeCompass does not run `hledger`.** Ledgerkit-specific tooling (a
  script in Ledgerkit, or a scratch harness) executes `hledger`, creates
  fixtures, inspects outputs, does differential tests, and emits evidence
  records (a small structured file: "input journal J, `hledger balance`
  produced O, at hledger version V, date D").
- CodeCompass's role under test: ingest those evidence records and relate
  them — "behaviour B is *documented by* manual §M, *observed by*
  experiment E, *implemented by* `ledgerkit/report.py:balance`,
  *verified by* `tests/test_balance.py::test_multi_commodity`."
- `context-evaluator` rates whether that assembled map is accurate and
  whether it would genuinely help an agent working on a real hledger
  compatibility gap — versus the agent just running `hledger` itself and
  reading the manual.

### Phase 55 — Decision (EXPERIMENTAL → GATE DD, gate G7)
Written decision at `planning/reference-projects/ledgerkit/findings.md`:

1. Is a generalised **technical-dependency** concept necessary for v1?
   If yes — which kinds beyond `package` (executable? manual/reference?
   spec? file-format? behavioural contract?), each backed by a Ledgerkit
   finding. (Technical Clipper hasn't run yet at this point in the
   reordered roadmap — Stage F, after this decision — so it cannot yet
   corroborate; Stage F's job is precisely to check whatever gets
   approved here doesn't overfit to Ledgerkit/hledger alone.)
2. Is first-class **provenance/evidence** necessary for v1? If yes —
   which distinctions (source-derived fact / doc statement / spec
   requirement / observed behaviour / test result / ADR / agent
   inference), and which per-claim attributes (what is claimed / which
   version / evidence source / verification state / route back /
   relationship to local impl+tests).
3. **What is the smallest model** that covers the demonstrated need?
   (`conditional-generalisation.md` structures this.)
4. Or: "not justified for v1 — the package-source model plus Stage C
   improvements is the redefined v1; Ledgerkit-driven scope becomes
   v1.x." This is a fully acceptable outcome.

## 3. Hard boundaries (task instruction)

- CodeCompass is **not** the hledger black-box experiment runner
  (`README.md` §1.9).
- The Ledgerkit relationship model
  (`external behaviour → documented by / observed by / implemented by /
  verified by`) is a **candidate to validate**, not a design to
  implement before the experiment.
- No feature is added to Ledgerkit to make CodeCompass easier to
  evaluate; Stage B and D are both subordinate to Ledgerkit's own
  roadmap.
- Actionable friction gets formatted per `codecompass-feedback-ingestion.md`
  once Ledgerkit adopts a context-curator role
  (`adoption-blueprint.md` §1, §8); until then, `reference-project-tester`
  files it the existing way (`planning/learnings/`, `planning/context-gaps/`).
