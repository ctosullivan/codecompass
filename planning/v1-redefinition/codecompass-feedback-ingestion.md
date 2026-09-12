# CodeCompass feedback-ingestion plan (required output 10)

How actionable findings from an adopting project's context curator (first:
Ledgerkit's — `adoption-blueprint.md` §8) are received, stored, reviewed,
classified, promoted, or rejected **in this repository**. Ledgerkit
discovers problems; CodeCompass generalises them. Ledgerkit must never
directly edit CodeCompass in response to its own friction — this document
*is* the review path that keeps that rule real rather than aspirational.

## 1. Where findings land

```
validation/codecompass/
    findings/
        CC-LK-001.yaml
        CC-LK-001.md
```

`CC-<project>-<NNN>` — a short project tag (`LK` for Ledgerkit, `TC` for
Technical Clipper if it ever produces one during its regression stage)
keeps ids collision-free across reference projects without inventing a
central registry. Each finding is **two files**: a `.yaml` (the
machine-readable record, §2) and a `.md` (the human-readable narrative —
same split CodeCompass already uses for `planning/retros/`'s structured
vs. narrative content, not a new pattern).

**Why a new top-level `validation/` folder, not `planning/learnings/`:**
a Ledgerkit finding is evidence *about CodeCompass from outside
CodeCompass* — a different provenance class from an agent's own
in-repository observation (`planning/learnings/`) or an agent-suggested
graph relationship (`planning/context-gaps/`). Keeping it visibly
separate matters because a finding's evidence lives partly in another
repository (Ledgerkit's own commit history, its own evaluation reports)
— `validation/codecompass/` is the place that fact is expected and
findable, not folded into a folder whose whole point is "this project's
own agents' own observations." **No duplicate store is created if a
future CodeCompass capability already provides ingestion** — if Stage C
builds a structured-findings feature for another reason, this folder
becomes its seed data, not a permanent parallel system.

## 2. Finding format (`.yaml`)

```yaml
id: CC-LK-001

identification:
  ledgerkit_revision: <commit sha>
  codecompass_revision: <commit sha / version>
  task_or_session: <Ledgerkit task slug, e.g. "milestone-5-cli-filter-flags">
  date: <YYYY-MM-DD>

problem_statement: >
  <Exactly what the Ledgerkit agent needed. E.g. "Agent needed to
  determine which hledger manual/source material constrains Ledgerkit
  query-regex semantics.">

context_supplied:
  what_codecompass_returned: <verbatim or summarised query/Skill output>
  relevant_edges_or_context: [<list>]
  suggested_edges_involved: true | false

independent_evaluation:
  accuracy: <assessment>
  relevance: <assessment>
  completeness: <assessment>
  freshness: <assessment>
  grounding: <assessment>
  noise: <assessment>
  misleading: yes | no | partially
  verdict: PASS | PASS WITH GAPS | FAIL

context_advantage: LOW | MODERATE | HIGH

manual_rediscovery: >
  <What the agent had to find manually after using CodeCompass.>

impact:
  classification: incorrect-context | missing-context | stale-context
    | retrieval-ux-friction | missing-relationship
    | missing-technical-dependency-type | noisy-relationship
    | product-hypothesis

proposed_generalised_improvement: >
  <Generalised, not Ledgerkit-specific — e.g. "Support authoritative
  documentation-to-implementation relationships", not "Add special
  support for the hledger manual".>

evidence:
  - session_evidence: <link/description>
  - ledgerkit_files: [<paths>]
  - hledger_evidence: [<manual section / source file / executable output>]
  - codecompass_output: [<query/report captured>]
  - related_findings: [<CC-LK-NNN, ...>]

recommendation: fix-bug | add-regression-test | investigate | prototype
  | collect-more-evidence | promote-to-roadmap-candidate | no-action

suggested_priority: <low | medium | high — proposed, not binding; CodeCompass review decides>
```

The `.md` companion is free-form narrative for anything the YAML's
fixed shape can't carry well (a longer excerpt, a screenshot-shaped
description, cross-links to the Ledgerkit-side evaluation report this
finding was extracted from).

## 3. Lifecycle

```
Ledgerkit development task
        ↓
CodeCompass context used
        ↓
context quality evaluated (Ledgerkit's context-evaluator / context-curator)
        ↓
curator prepares CC-LK-NNN (this format)
        ↓
lands in validation/codecompass/findings/ (this repository)
        ↓
CodeCompass review — knowledge-curator triages alongside
planning/learnings/ and planning/context-gaps/ at the normal per-phase
triage step, and in bulk at GATE DB (Phase 47) / GATE DD (Phase 55)
        ↓
promote?
 ┌──┴──┐
 no    yes
 │      ↓
retain  → roadmap candidate (Stage C phase, gate G6-equivalent per stage)
         / regression test / architecture work
              ↓
         CodeCompass improvement lands
              ↓
         rerun the same Ledgerkit context case
              ↓
         measure whether context improved (a new finding, or an update
         to the original recording "resolved")
```

**A finding never becomes a CodeCompass change automatically.** It is
reviewed the same way a `planning/learnings/` candidate is — by the
`knowledge-curator`, with the lead's final judgement on anything
touching `src/`, `decisions/`, or `CLAUDE.md`.

## 4. Promotion rules (restated, generalised from the task instruction)

A finding becomes a **strong roadmap candidate** when one or more apply:

1. CodeCompass provided **incorrect or misleading** context (outranks
   everything else — same "incorrect > incomplete" priority
   `context-quality-evaluation.md` already establishes).
2. The gap **blocked genuine work** (Ledgerkit's real task didn't
   proceed, or proceeded materially slower).
3. The **same problem recurred** across ≥2 Ledgerkit tasks, or was
   independently hit by two different agents/sessions.
4. The proposed fix **clearly generalises** beyond Ledgerkit/hledger/
   accounting.
5. **Another reference project** exposes the same need (this is exactly
   what Stage F's Technical Clipper regression is *for* — a second,
   deliberately different data point).
6. A **prototype measurably improves** a re-run context-evaluator
   verdict or advantage rating.
7. A **suggested relationship** (`planning/context-gaps/`) repeatedly
   improves later tasks' context — i.e. it reaches `recurred`, per
   `decisions/0051`'s existing lifecycle, unchanged.

**Explicit classification, not a single bucket** — every finding gets
one `impact.classification` value, distinguishing: a plain bug; missing
mechanical coverage; retrieval/UX friction; a graph/relationship problem;
a missing technical-dependency *concept* (the heavy one — this is what
feeds `conditional-generalisation.md`); noise; or a product hypothesis
not yet actionable.

**Preference for generalised framing, always.** "CodeCompass cannot
represent authoritative documentation-to-implementation relationships"
over "add hledger manual support"; "executable technical dependencies
need first-class representation" over "add a special hledger executable
node." A finding written the narrow way is sent back to the curator for
reframing before it's reviewed as a roadmap candidate — not rejected,
just not yet in the right shape to weigh against `conditional-generalisation.md`'s
evidence bar.

## 5. Relationship to existing mechanisms (no duplication)

| Existing mechanism | This plan's relationship to it |
|---|---|
| `planning/context-gaps/` | A Ledgerkit finding whose `impact.classification` is `missing-relationship` names a candidate that, if it recurs, is also filed as (or linked to) a `context-gaps/CG-NNN` entry — same GATE DB/DD evidence pool, viewed from the external-project side rather than CodeCompass's own dogfooding side. |
| `planning/learnings/` | Ledgerkit findings are a distinct provenance class (§1) but are triaged in the **same** `knowledge-curator` pass — a Ledgerkit finding can promote into a test/doc/ADR exactly like an internal candidate learning does. |
| `context-quality-evaluation.md` | Supplies the `independent_evaluation` block's vocabulary verbatim (PASS/PASS WITH GAPS/FAIL, LOW/MODERATE/HIGH) — one evaluation language across CodeCompass's own dogfooding and every reference project. |
| `reference-project-protocol.md` §2.6 (friction → confirmed finding) | This plan is that same funnel's terminal, external-facing stage — a Ledgerkit-produced finding is what a confirmed, recurring `reference-project-tester` observation *becomes* once formatted for cross-repository review. |

## 6. Cross-ecosystem regression check on the ingestion process itself

Stage F (Technical Clipper) is also the check that this ingestion format
and its promotion rules **generalise** — if Technical Clipper's own
findings (should it produce any during its regression phase) don't fit
the same YAML shape without Ledgerkit-specific fields creeping in, that
is itself a finding about this plan, filed the same way.

## 7. What this plan explicitly does not do

- It does not give Ledgerkit write access to any part of this
  repository beyond `validation/codecompass/findings/` (and even that is
  conceptually "submitted for review", not self-merged — in practice,
  since both repositories are developed by the same person via Claude
  Code sessions, a finding is added to *this* repository directly, but
  the review/promotion step is still separate from the act of filing).
- It does not promise a turnaround time or a guarantee that any given
  finding becomes a fix — §4's rules are the actual gate.
- It does not replace `context-evaluator`'s own Stage-B reports
  (`planning/reference-projects/ledgerkit/<NN>-*.md`) — those are the
  primary evidence; a `validation/codecompass/findings/CC-LK-NNN` is the
  distilled, CodeCompass-facing summary extracted from one or more of
  them once a curator judges it actionable.
