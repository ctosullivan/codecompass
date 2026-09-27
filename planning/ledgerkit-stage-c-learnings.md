# Ledgerkit Stage C learnings — a durable record

**Written Phase 72 (2026-09-27), direct user request.** Distills real
evidence CodeCompass's own Phases 54, 54b, 54c, 55, 60, and 61 already
produced while studying Ledgerkit's own Stage C work, into 11 numbered
learnings, each classified as a **validated observation**, the **design
principle** it implies, **existing vs. proposed capability**, and any
**open hypothesis** still requiring validation. This document does not
introduce new evidence — every claim below cites a real phase file,
`OBS-`/`CG-`/`L-` record, or ADR already in this repository. It exists
because that evidence was scattered across a dozen phase files with no
single place distilling it into design principles connected to roadmap
priorities.

Feeds `decisions/0062` (the resulting prioritisation ADR) and
`planning/ROADMAP.md`'s Priority A-F structure.

## 0. Naming disambiguation (read this first)

**"Ledgerkit's own Stage C" and CodeCompass's own redefined-v1 "Stage
C" are two different things that happen to share a name**, both real
and both used verbatim throughout this project's history:

- **Ledgerkit's own Stage C** is a stage of *Ledgerkit's* internal
  development roadmap — its query-language work (`depth:`, `status:`,
  `not:`, `tag:`, `date:`/`acct:`/`desc:` query terms). This document is
  about that one: the real-world validation exercise where CodeCompass
  was pointed at genuine, in-progress Ledgerkit Stage C work.
- **CodeCompass's own "Stage C"** (`planning/v1-redefinition/roadmap.md`,
  Phases 48-51) is a stage of *CodeCompass's* redefined-v1 roadmap —
  "improve the existing product, only where Stage B evidence supports
  it." Its history is dispositioned in `planning/pre-v1-disposition.md`,
  not here.

Every learning below cites which of Ledgerkit's Stage C investigations
(Phase 54's `tag:` brief, Phase 54b's `depth:` reconstruction, Phase 61's
cross-language work) it comes from.

## 1. Task-context completeness matters more than graph completeness

**Validated observation.** Every formally-evaluated Ledgerkit instance
(`planning/reference-projects/ledgerkit/findings.md` §1-2) rated **LOW
advantage**, with two of five instances a formal **FAIL** — both FAILs
were an authoritative-sounding "not found" for a real, load-bearing doc
(`dev-docs/hledger-compatibility.md`, `07-query-regex.md`), not a
missing exotic relationship. Fixing that (Phase 49) moved both to PASS
WITH GAPS, but the advantage ceiling **did not move**
(`findings.md`'s GATE DC section): `doc_relations_edges` is built from
literal mention detection, so it can say *whether* a doc is tracked but
never *why* it matters. `17-query-semantics-brief.md` — by both
evaluators' own independent assessment, "the single most valuable
artifact encountered in any Ledgerkit evaluation to date" — produces
**zero** `query relations` output. The system answered "how much can be
retrieved" adequately; it never answered "has this agent got what it
needs for *this* task."

**Design principle.** Optimise for "did a fresh agent get what it
needed to safely do this specific task," not for graph size, edge
count, or retrieval breadth. This reframes the metric `conditional-generalisation.md`
already uses (LOW/MODERATE/HIGH advantage vs. the default pathway) as
the *primary* success axis, not a secondary check.

**Existing vs. proposed.** `context-evaluator`'s PASS/PASS WITH GAPS/
FAIL verdict already operationalises task-level sufficiency judgment —
but only as an *internal evaluation instrument* run by CodeCompass's own
developers, never as something a downstream user of the shipped tool
can ask it directly ("do I have enough context for this change?").
**Proposed**: a product-facing task-context-completeness capability —
Priority A.

**Open hypothesis.** Whether the 100%-LOW-advantage result is inherent
to Ledgerkit's own ~0-runtime-dependency shape (`conditional-generalisation.md`
§1.1's own prior, confirmed twice) or generalises to dependency-heavier
projects too. Not yet corroborated by a second, differently-shaped
reference project.

## 2. Execution/behavioural paths matter more than structural proximity

**Validated observation.** Ledgerkit's own Stage C Phase 1 made a real,
dated mistake: it classified hledger's `depth:` term from one function's
signature (`Query.hs`'s `Depth` constructor) without tracing any
command's actual consumption of it. Phase 54b tested whether
CodeCompass's document layer helps a fresh agent avoid repeating that
mistake — both baseline and treatment correctly traced the real
entry-point→command-handler→`filterQuery`/`queryIsDepth`→`matchesAccount`
chain across five separate hledger commands, discovering three genuinely
distinct behaviours (clip/aggregate, partial exclusion, total inertness)
(`planning/reference-projects/ledgerkit/02-depth-behavioural-reconstruction-evaluation.md`).
Neither run repeated the shortcut. But `CG-007` found the underlying
*mechanism gap* directly: the exact three-file call chain this task
needed (`EntriesReport.hs` → `Ledger.hs` → `Query.hs::matchesAccount`)
produced **zero** representable relations in CodeCompass's graph — not
a wiring bug, a structural absence (`doc_relations_edges` has no
symbol-level/function-call edge kind at all). Separately, `L-026`
(promoted, architecture footgun) found the identical shape a **third**
independent time: an ecosystem adapter's generated digest answers "what
exists and what's it called," never "what does it do."

**Design principle.** CodeCompass's context model needs to represent
**A calls B calls C** execution chains, not only "A is structurally near
B" (same file, same package, same directory). A structurally distant
file that's on the real execution path is more relevant than a
structurally adjacent one that isn't.

**Existing vs. proposed.** Adapters already extract declared symbols
(`EcosystemAdapter.symbols()`, Phase 62) and dependency trees — purely
structural/declarative facts. Execution-path/call-graph tracing is
**not implemented anywhere in CodeCompass** — this is `conditional-generalisation.md`
§2.2's "executable kind" hypothesis, never funded, still open.

**Open hypothesis.** Whether a lightweight, mechanically-derived
call-path representation is tractable without CodeCompass becoming a
static-analysis/call-graph engine — a real risk against the project's
own non-goal ("CodeCompass does not run anything it grounds," `README.md`
§1.9, `conditional-generalisation.md` §4). Not yet designed, let alone
evidenced as tractable at the "smallest justified fix" size this
project otherwise insists on.

## 3. Tests are evidence, not absolute truth

**Validated observation.** Already a **promoted, enforced invariant**
(`L-020`): "content-hash pinning proves an excerpt hasn't silently
changed; it does not prove the excerpt's boundary covers what its own
description claims." Found when Phase 54's `tag-query-manual` excerpt
silently excluded one of three tag-inheritance rules while its own
frontmatter confidently claimed all three were present — a false
completeness claim inside the very artifact whose value proposition was
"trust this without re-checking it yourself." `context-evaluator`
independently caught it against the real pinned manual and rated the
treatment run **FAIL** even though the mechanism itself (content-hash
pinning) worked exactly as designed. Fixed same-phase with a new
regression test
(`test_reference_pipeline.py::test_tag_query_manual_excerpt_contains_all_three_inheritance_rules`,
`L-020`'s own citation) — the fix did not retroactively change the FAIL
verdict, which stands as the accurate record.

**Design principle.** A regression test proves a behaviour holds under
the conditions it exercises; it does not by itself prove the artifact
citing it is complete, or that the behaviour holds universally. This
principle is already load-bearing practice in this project (see
`docs/domain/concepts/invariant.md`'s own citation discipline, Phase
71).

**Existing vs. proposed.** Enforced within this project's own
Ledgerkit-experiment tooling and its own domain-corpus citation
discipline. **Not yet a general CodeCompass product capability** —
CodeCompass has no notion, surfaced to a downstream user, of "this test
covers conditions X and Y, not Z." Proposed: a coverage-scoped citation
convention when Priority A/B tooling references a test as evidence
(cite what the test actually exercises, not "this test proves the
claim").

**Open hypothesis.** Whether representing "tested under conditions
X, not Z" needs new product infrastructure or is adequately solved by a
citation-writing convention alone (documentation-only, no schema
change) — leans toward the latter given this project's own "smallest
justified fix" discipline, but not yet decided.

## 4. Behavioural claims need lightweight provenance

**Validated observation.** Ledgerkit's own `dev-docs/compat-register/*.yaml`
(real, hand-authored, studied Phases 54/54b) already links a claim to
`evidence: [{kind: manual|source|executable|test, ref, pinned_at}]` and
a closed `status` enum. Phase 54c generalised this shape into
CodeCompass's own Observation/Evidence/Claim/Derivation/Decision/
Requirement model (`decisions/0060`), proven for real at Phase 60
(Haskell adapter API-surface extraction, independently confirmed
correct) and again at Phase 63D (domain-corpus reconstruction, 144
supporting evidence records). Phase 54c's own retro rates the six record
kinds "**promote to durable, file-based convention** — held up cleanly
under real use... no further shape problems found"
(`planning/retros/phase-54c-evidence-knowledge-workflow.md` §"Durable-vs-experimental
recommendation"). No confidence scores or floats — a closed status enum
only (`.claude/agents/context-researcher.md` hard rule).

**Design principle.** Keep the model deliberately minimal: a Claim, a
list of Evidence items (each with a kind and a ref), a closed status
enum, no float confidence scores, no invented ontology beyond what's
been proven necessary.

**Existing vs. proposed — the single largest concrete opportunity.**
This model **already exists and is proven**, but strictly as
`planning/knowledge/`'s own internal mechanism for developing
CodeCompass itself (`decisions/0051`/`0054`'s own explicit boundary:
never written to `context-graph.db`, never a product feature). It has
never been offered to a **downstream user** of the shipped tool for
tracking claims about *their own* project's behaviour. Priority B is
this: productising an already-proven internal mechanism, not inventing
a new one.

**Open hypothesis.** Storage shape — Phase 54c's own retro explicitly
recommends "**keep file-based/experimental, revisit only if evidence
demands a query capability YAML files can't give**." No such evidence
exists yet. A product-facing version should default to the same
file-based shape unless a concrete need for graph-backed querying is
independently demonstrated — not assumed on architectural elegance
grounds.

## 5. Contradictions are valuable information

**Validated observation.** The model's own `contradicting_evidence`/
Claim-`supersedes` machinery exists and is structurally checked — but
Phase 54c's own retro is explicit that it was "**structurally-checked
but experimentally unproven — do not claim it 'works,' since it was
never exercised with real content**" (same retro table, row 6). No real
contradiction has ever been assembled and surfaced through it.

**Design principle.** Surface disagreement between sources explicitly
rather than silently picking one. This project already practices an
adjacent, proven pattern for a *different* content class:
`domain-skeptic`'s adversarial review of `docs/domain/` explicitly
hunts for internal contradictions before a corpus page is approved
(`decisions/0060`) — a real, working precedent for the *posture*, even
though it doesn't exercise the Claim-model's own supersedes mechanism.

**Existing vs. proposed.** The schema exists (Priority B's own record
model); the actual behaviour of surfacing a genuine contradiction has
**never been demonstrated with real data**. This is the most
directly-named open item in this entire learnings set — it is not a
new capability to build, but an existing one to actually exercise and
validate.

**Open hypothesis (explicitly named by this project's own prior
retro, not new to this document).** Needs a deliberately-chosen real
case with genuine conflicting evidence (e.g., a doc claiming one thing
and a test proving another) run through the existing mechanism, to find
out whether it actually helps or just adds unused schema surface.

## 6. Mechanically-established relationships must stay distinguishable from inferred ones

**Validated observation.** Already a first-class, largely well-executed
project value: `decisions/0051` (agent-suggested graph relationships are
captured as reviewable prose, never written to `context-graph.db`) and
`decisions/0054` (agent-driven enrichment is a second, non-authoritative
producer, tagged by a `model` column, never overwriting a mechanical
fact) are both real, shipped mechanisms enforcing exactly this
distinction. `CG-005`'s `origin` enum extension (`pinned_reference`,
Phase 54c) is a further real instance: externally-pinned reference
material is now provenance-tagged distinctly from hand-authored project
docs.

**Design principle.** Preserve provenance (mechanically derived /
agent-proposed / reviewed / experimentally verified) as a first-class,
queryable distinction — never let an inferred relationship render
indistinguishably from a proven one.

**Existing vs. proposed.** Substantially implemented, with **two known,
disclosed, currently-unfixed exceptions** already tracked in
`planning/ROADMAP.md`'s Future-improvement backlog: `L-031`
(`symbol_enrichment` has no producer-attribution column, unlike
`vendor_enrichment`/`doc_relation_enrichment` — an asymmetry that
directly undermines this exact principle for one specific table) and
`L-032` (the external-adapter wire protocol's `ecosystem`/`capabilities`
fields are received but never validated against what CodeCompass
configured, a related trust-boundary gap). Both are cheap, already
scoped, additive fixes — no new design work needed.

**Open hypothesis.** None beyond closing the two known gaps — this
learning is the most mature/validated of the eleven.

## 7. Context gaps should be first-class, convertible into research tasks

**Validated observation.** `planning/context-gaps/` (`decisions/0051`,
Phase 43c) already does close to exactly this: `CG-001` through `CG-008`
are real, structured, evidenced entries with an explicit promotion path
into a funded roadmap phase (`CG-002`→Phase 49, `CG-004`→Phase 55b,
`CG-005`→Phase 54c, `CG-008`→Phase 62 — all real, all landed). This
learning is **substantially already implemented** as an internal
project mechanism, not a hypothesis.

**Design principle.** A gap ("CodeCompass cannot represent X") is a
first-class, citable artifact with its own lifecycle (candidate →
recurred → promoted-to-roadmap / discarded), not an ephemeral
observation lost in conversation.

**Existing vs. proposed.** Exists and works — but, like learnings #4
and #8, **only for CodeCompass's own development process**. A
downstream user working on their own project has no equivalent: no way
for CodeCompass to say "here is what I don't know about your codebase,"
convertible into a concrete task. **Proposed** (Priority C): the
product-facing counterpart — the same lightweight lifecycle, pointed at
gaps in a *target* project's own context, not gaps in CodeCompass's
graph of itself.

**Open hypothesis.** Whether the existing prose-template mechanism
generalises cleanly to arbitrary target projects with no changes, or
needs product-specific tooling (a `codecompass gaps` surface, say) —
not yet designed.

## 8. Documentation-first development workflow

**Validated observation.** `decisions/0060` formalises exactly this
workflow — Scope → Plan → Domain → Design → Implement, with a
`DRAFT → RESEARCHED → USER REVIEW → APPROVED → IMPLEMENTING → VERIFIED`
review-gate lifecycle — as CodeCompass's own intended development
methodology, proven real at Phase 60 (Haskell adapter) and Phase 63D
(domain reconstruction).

**Design principle.** research → evidence/knowledge map → design
document → review → implementation context packet → implementation →
verification → retrospective → knowledge update, exactly the sequence
the user's own request names, matches this project's real, lived
practice almost verbatim.

**Existing vs. proposed.** This is CodeCompass's own **development
meta-process** — how *this project's* contributors (human and agent)
work — not a capability the shipped tool exposes to a downstream user
running the same workflow on *their* project. **Proposed** (Priority
D): package the proven workflow *shape* (not the CodeCompass-specific
agent roster) as guidance/tooling a downstream user's own process could
adopt, reusing existing `query`/Skill/context-graph capabilities rather
than duplicating them.

**Open hypothesis.** How much of this genuinely needs product tooling
versus being purely a project-management convention with no tooling
gap at all — named honestly as unresolved, not assumed either way.

## 9. Independent context evaluation is valuable

**Validated observation.** The single most consistently validated
practice across every Ledgerkit phase (Phases 45, 46, 49, 51, 54, 54b,
61, 67): every formal verdict in this project's evidence base came from
an independent, ground-truth-checked evaluation (`context-evaluator`),
never a self-report. Phase 54c's own `packet-sufficiency.md` log — a
fresh reviewer explicitly assessing whether an implementation-ready
context packet is sufficient — is rated by that phase's own retro as
"**the single highest-value mechanism this phase tested**," finding two
real, specific, actionable gaps on its very first real use.

**Design principle.** Never trust the producing agent's own assessment
of context sufficiency; a second, independent pass finds real, specific
gaps the first pass cannot see in itself.

**Existing vs. proposed.** **Fully validated, already core internal
practice** — the strongest-evidenced learning of the eleven. Gap: no
downstream-user-facing equivalent exists. A user of the shipped tool has
no "is my context packet sufficient" check of their own; this exists
only as an internal agent role serving CodeCompass's own development.
**Proposed** (Priority E): a reusable, repeatable protocol (not
necessarily a new agent) offered for downstream adoption.

**Open hypothesis.** Whether this needs a dedicated new capability at
all, or whether documenting the existing `packet-sufficiency.md`
protocol as a reusable pattern is sufficient — leans toward the latter
given this project's own "reuse, don't duplicate" discipline.

## 10. Clean-environment reproducibility matters

**Validated observation.** Already a hard, consistently enforced
practice: every reference-project phase uses disposable scratch clones
(never the real repository), fresh, independently-dispatched agents
with no access to the lead's own prior reads (Phase 54b's explicit
design, to avoid contaminating the experiment), and Phase 67's dedicated
fresh-agent acceptance test scored **4/4 PASS** (one disclosed
`CLAUDE.md`-auto-load confound on criterion 1 only, criteria 2-4
unconfounded — `planning/v1-closeout.md` §5).

**Design principle.** A context packet, evidence reference, or workflow
step must function for a fresh session with no hidden conversational
state — proven, load-bearing discipline, not aspirational.

**Existing vs. proposed.** Proven and enforced case-by-case, but with
**no formal, reusable, generalised check** — each phase re-establishes
the discipline by hand rather than running a standard, repeatable
verification. **Proposed** (Priority F): formalise the existing
discipline into a repeatable check rather than requiring each future
phase to re-invent it.

**Open hypothesis.** None on whether the principle holds (it's
proven); open only on the mechanical shape of a repeatable check.

## 11. Reduction in correct rediscovery work is the useful outcome metric

**Validated observation.** `context-quality-evaluation.md` already
commits to exactly this framing — LOW/MODERATE/HIGH advantage over "the
default pathway" (grep, direct read, `--help`) — explicitly **not**
graph size or edge count (`conditional-generalisation.md`'s own
repeated framing, confirmed as a real discipline, not aspirational,
across every Ledgerkit evaluation to date).

**Design principle.** Measure whether a fresh agent needed less manual
rediscovery to do the task correctly, with uncertainty and provenance
preserved — not how much the graph holds.

**Existing vs. proposed.** The qualitative verdict (LOW/MODERATE/HIGH,
PASS/PASS WITH GAPS/FAIL) already exists and is the metric this whole
evidence base is built on. **Open, not yet resolved**: whether a more
mechanical proxy (e.g., counted tool-calls/searches avoided) is worth
adding alongside the existing qualitative judgment, or whether that
would just reintroduce a graph-size-style vanity metric in different
clothing.

**Open hypothesis.** Genuinely unresolved, flagged as such rather than
decided either way in this document.

## Summary table

| # | Learning | Status |
|---|---|---|
| 1 | Task-context completeness > graph completeness | Validated; product capability proposed (Priority A) |
| 2 | Execution paths > structural proximity | Validated gap (`CG-007`, `L-026`); capability proposed, not designed (Priority A) |
| 3 | Tests are evidence, not truth | Validated + enforced (`L-020`); product convention proposed |
| 4 | Claims need lightweight provenance | Model proven internally (Phase 54c); productisation proposed (Priority B) |
| 5 | Contradictions are valuable | Schema exists, **never exercised with real content** — open |
| 6 | Mechanical vs inferred must stay distinct | Substantially implemented; 2 known gaps (`L-031`, `L-032`) |
| 7 | Context gaps as first-class tasks | Implemented internally (`context-gaps/`); productisation proposed (Priority C) |
| 8 | Documentation-first workflow | Proven internally (`decisions/0060`); productisation open question (Priority D) |
| 9 | Independent context evaluation | Fully validated, core practice; downstream equivalent proposed (Priority E) |
| 10 | Clean-environment reproducibility | Proven discipline; formalisation proposed (Priority F) |
| 11 | Reduction in rediscovery as metric | Already the practiced metric; mechanical-proxy question open |

See `decisions/0062` for the resulting prioritisation decision and
`planning/ROADMAP.md` for the Priority A-F roadmap structure this
document feeds.
