# Phase 81 — persistent bidirectional intermediate knowledge layer

**Status: planned. Planning only — implementation (touching `src/`, new
record kinds, new CLI surface, template changes) does not begin until
this plan is reviewed and approved.**

Direct user request, 2026-10-07. Evolves CodeCompass toward a model
where its canonical knowledge is editable, through ordinary Markdown,
by humans and external AI tools (ChatGPT, Copilot, Claude Code, plain
Git PRs) via a reconciliation boundary — never bypassing it — while
project documentation and coding/planning context are grounded in the
same reconciled knowledge rather than drifting as independent sources
of truth.

**Naming note**: `planning/phase-81-strict-isolation-backlog-prompt.md`
already exists, using "81" as a filename prefix for a *backlog item's
saved prompt* (recorded 2026-10-02). That item has **no phase number in
`planning/ROADMAP.md`** — unscheduled backlog rows explicitly carry none
(`ROADMAP.md`'s own "Future-improvement backlog" convention) — so there
is no real numbering collision; "Phase 81" is genuinely free as the next
real phase number (Phase 80 is the last `done` phase; nothing is
currently `planned`/`in progress`). Flagged here only so a future reader
isn't confused by the coincidence.

---

## 0. Current-state findings (read live for this plan, not assumed)

Three independent research passes (forks) plus direct reading grounded
this plan in the real, current repository — not memory of how
CodeCompass used to work. Findings are organized by what's directly
reusable, since the single governing instruction behind this whole plan
is: **reuse existing abstractions; do not build a parallel knowledge
system.**

### 0.1 The canonical knowledge model already mostly exists

Phase 54c's **six-record-kind model** (`docs/domain/concepts/{observation,evidence,claim,derivation,decision,requirement}.md`,
validated by `scripts/check_knowledge_base.py`, one flat `key: value`
YAML-like file per record under `planning/knowledge/<slug>/`) already
provides:

| Kind | Prefix | Role | Status enum |
|---|---|---|---|
| Observation | `OBS-` | a dated, reproducible research action and its raw result | `recorded` (fixed) |
| Evidence | `EV-` | what a cluster of Observations shows | `current \| superseded` |
| Claim | `CL-` | an assertion about the system, built from Evidence | `proposed\|supported\|contradicted\|superseded\|verified` |
| Derivation | `DE-` | how a Claim was reached from its Evidence (1:1 with the Claim) | narrative only |
| Decision | `DEC-` | a human-ratified choice, possibly agreeing/disagreeing with a Claim | `proposed\|approved\|rejected\|superseded` — **the only kind a human alone authors** |
| Requirement | `REQ-` | an obligation a Decision authorises | `proposed\|approved\|implemented\|verified` |

Phase 79 (`decisions/0066`) already added optional Claim-only fields:
`assertion_kind` (`definition\|relationship\|rule\|invariant\|state_transformation\|boundary`),
`basis` (`directly_stated\|inferred\|proposed_policy\|observed_behaviour`),
`evidence_support_state` (`supported\|partially_supported\|unsupported\|conflicting`),
plus free-form `examples`/`counterexamples`/`depends_on`/`open_questions`
(inline-list form only, enforced fail-closed). A Claim's own `supersedes`
only ever names another Claim; a Decision's own `supersedes` only ever
names another Decision — **never cross-kind**, mechanically enforced
(`check_supersedes_never_crosses_kind`). Fact (Claim) and intent
(Decision) already sit on separate tracks: a Decision can
`agree_with_claim` or diverge, but can never *supersede or revise* a
Claim.

Also already real: a **frozen-snapshot format** (`decisions/0066`, TOML)
capturing a versioned assertion-plus-evidence-closure with real
historical git-blob hashes, and three already-working checks:
`check_snapshot_completeness` (fail-closed structural validation, hardened
across Phases 79/80), `check_snapshot_historical_integrity` (tamper
detection against historical content), and — **directly relevant to this
phase** — `check_snapshot_current_divergence`, which already detects when
a record's *current* content hash has drifted from what a snapshot froze,
informationally. This is the nearest existing thing to a
staleness/reconciliation trigger.

**Honest, pre-existing gaps in this model**, disclosed by its own docs:
`contradicting_evidence` and Claim-`supersedes` have never once been
exercised with real content across the whole corpus (structurally
supported, never proven); **"invariant" is not a seventh record kind** —
it exists only as one `assertion_kind` enum value on Claims, an informal
`design.md` subsection convention, and the unrelated
`docs/domain/invariants.md` project-level file — three unlinked senses,
never consolidated.

### 0.2 `context-graph.db`'s own boundary is deliberate and must not move

`src/codecompass/graph.py` (read in full) is a deterministically
rebuilt store of **mechanically-detected structural facts only** — three
lifecycle categories (delete-and-reinsert edge/leaf tables; upserted-by-
natural-key identity-preserving node tables; never-touched-by-rebuild
enrichment tables). This boundary has been reaffirmed, not reopened, at
every prior opportunity (`decisions/0024`/`0025`/`0031`/`0037`/`0045`,
most explicitly `decisions/0051`: *"An agent's suggested relationship is
an observation with provenance. It is captured in `planning/context-gaps/`
and nowhere else... no agent, or any AI call, [gets] influence over the
contents of the graph."*). **This plan does not propose new "concept"/
"invariant"/"behaviour" tables in `context-graph.db`.** The graph stays
exactly what it is; it becomes one of several **evidence sources** the
knowledge layer cites (an Evidence record's `source_ref` can already
point at a `source_files`/`source_symbols`/`doc_artifacts` row by path +
content hash — no schema change needed for this).

**A project's own documentation is already a first-class graph object**,
confirmed by direct reading of `spec_docs.py`/`doc_mapping.py`: every
whole-project `sync` already detects `README.md`, `architecture/**/*.md`,
`decisions/**/*.md`, `docs/**/*.md`, `ai-docs/**/*.md`, `dev-docs/**/*.md`
(and more) as `doc_artifacts` rows (`kind='spec_doc'`, `origin='project'`
or `'pinned_reference'`), chunks them (`doc_chunks`, content-hashed), and
mechanically mention-links them to vendors/other docs
(`doc_relations_edges`). **`CONTRIBUTING.md` and `CLAUDE.md` are
explicitly, deliberately excluded** (`_EXCLUDED_ROOT_NAMES`). This phase
can ground project documentation directly on these *already-existing*
`doc_artifacts`/`doc_chunks` rows — no new doc-identity concept needed —
and should explicitly decide whether to bring `CONTRIBUTING.md` into
scope (§2 flags this as a decision requiring approval; `CLAUDE.md` stays
excluded, it is self-governing per its own §0).

The existing `enrich apply` CLI command (`cli.py`, `relation_enrichment.py`,
`decisions/0038`/`0054`) is the closest existing precedent for "an
external actor's claim is mechanically reconciled against the graph, not
trusted on its own say-so": an agent-authored enrichment is accepted
*only* if it exactly matches a currently-pending, mechanically-detected
candidate, written through the same validated path as automated
enrichment, and always tagged `model = "agent:<name>"` — structurally
distinguishable from an Anthropic-API-authored row with zero code change
needed to tell them apart. This is the direct precedent for this phase's
own "external contribution enters as a distinguishable candidate, never
automatically authoritative" requirement.

### 0.3 Every existing projection is one-directional; nothing reconciles back

`VendorDigest` rendering (`sync_vendor` → `vendor/<name>/*.md`) is a
real, deterministic DB→Markdown projection, but strictly
regenerate-and-overwrite — it never reads the Markdown back.
`knowledge-curator`'s EXPERIMENTAL **context-packet assembly mode**
(Phase 54c) already compacts everything reachable from an `APPROVED`
`design.md` into one Markdown file (`context-packet.md`) — this is
directly the shape of a **phase knowledge package** (§13), already
built, already bounded, already excludes non-approved records — but it
too is write-once. `documentation-agent`'s own `design.md` projection is
explicitly documented as one-directional ("never hand-edited out of
step with it"). A repo-wide grep for any reconciliation/round-trip
mechanism found none. **The bidirectional loop this phase proposes does
not exist anywhere today, even partially — this is the genuinely new
~20% this phase must build; everything else is reuse.**

Two existing, independently-evolved comparison vocabularies already do
almost exactly what the new phase's own semantic-diff step needs:
`docs-maintainer`'s legacy-reconciliation mode already classifies an
existing doc's claims as `supported` / `stale_or_contradicted` /
`rationale_requiring_verification` / `useful_example` / `obsolete`;
`domain-skeptic`'s comparison mode already classifies alignment as
`aligned` / `partial` / `conflicting` / `not_implemented` /
`insufficiently_verified`. §7 below maps the user's requested
reconciliation-state vocabulary onto these, rather than inventing a
third.

### 0.4 The clean-room methodology, isolation backlog, and template

`decisions/0066`–`0070` establish a five-stage pipeline (research/freeze
→ model-blind reconstruction → comparison → draft → legacy
reconciliation) and the append-only ADR-supersession convention this
plan follows. `planning/strict-isolation-for-documentation-reconstruction.md`
(backlog, unfunded) already proposes exactly the kind of stage-specific
input-contract boundary this phase's own reconciliation engine needs
between canonical knowledge, intermediate docs, and legacy project docs
— this phase reuses its *framing*, not its (still-unbuilt) enforcement
mechanism; Tier 1 isolation remains unavailable in this environment, so
this phase's own isolation posture stays `best-effort`, honestly labelled,
same as every clean-room phase to date. `codecompass-template` (HEAD
`68bae8e`) has no `.codecompass/` or intermediate-document convention
yet; its `optional-clean-room-workflow/` directory is the natural sibling
location for whatever this phase delivers to the template.

### 0.5 Net effect — what's retained / generalised / migrated / superseded / deprecated (§17)

| Existing component | Disposition |
|---|---|
| Observation/Evidence/Claim/Derivation/Decision/Requirement model + `check_knowledge_base.py` | **Retain**, as the canonical knowledge store — this phase does not create a parallel store. |
| Frozen-snapshot format + its three checks | **Generalise**: reused for the new "live projection" concept (§8), with `check_snapshot_current_divergence`'s own hash-comparison logic as the direct basis for drift detection. |
| `context-graph.db` schema/boundary | **Retain unchanged.** No new knowledge-object tables. Cited as an evidence source only. |
| `spec_docs.py`/`doc_mapping.py` project-doc tracking | **Retain**, reused as the existing identity anchor for project documentation grounding (§9). |
| `VendorDigest` rendering pattern | **Generalise** into the new intermediate-document renderer (§4/§8). |
| `knowledge-curator`'s context-packet-assembly mode | **Generalise** into the phase-knowledge-package mechanism (§13), loosening its current `APPROVED`-`design.md`-only gate. |
| `docs-maintainer`/`domain-skeptic`'s two comparison vocabularies | **Generalise**, mapped onto one reconciliation-state vocabulary (§7) for this new use case; original vocabularies untouched for their own existing use cases. |
| `decisions/0051`'s "agent-suggested content is captured, never graphed, promoted only via a gate" | **Retain as the governing precedent**, extended from edges specifically to the new intermediate-document change class generally (§14). |
| `enrich apply`'s mechanical-candidate-matching + `agent:<name>` provenance tagging | **Generalise** into the new reconciliation CLI surface (§11/§8). |
| `documentation-lifecycle.md`'s six content categories + incremental-maintenance loop | **Retain**, extended (not replaced) by this phase's own targeted-update mechanism (§12). |
| `reference-project-protocol.md`'s dogfood conventions | **Retain unchanged**, reused directly for this phase's own Ledgerkit-style validation (§6/§16). |
| Bidirectional Markdown↔record reconciliation | **New — does not exist today in any form.** This is the phase's own real deliverable. |
| A formal "invariant" record kind | **Superseded in its current fragmented form** by an explicit, minimal consolidation (§1.3) — not a new seventh record kind; reuses `assertion_kind: invariant` on Claims, with the two other existing informal senses pointed at it, not duplicated. |

---

## 1. Canonical knowledge model (governing ownership rule)

**The canonical knowledge model is `planning/knowledge/`'s existing
Observation/Evidence/Claim/Derivation/Decision/Requirement corpus, not a
new or extended `context-graph.db` schema.** `context-graph.db` remains
exactly what it is today: a deterministic store of mechanically-detected
structural fact, cited *as evidence* by the knowledge layer, never
itself holding semantic/interpretive content. This is the single most
consequential architectural decision in this plan and is named
explicitly for approval (§"Decisions requiring explicit maintainer
approval").

### 1.1 Why the existing model, not a new one

- It already has real status lifecycles distinguishing fact from intent
  (Claim vs. Decision), real evidence-citation discipline
  (`supporting_evidence`/`contradicting_evidence` with mechanical
  cross-reference resolution), and a real, already-hardened validation
  script with three rounds of fail-closed fixes behind it
  (Phases 79/80).
- It is already file-based, already lives in Git, already has a stable
  per-record identity (`id:` field + filename) — exactly the "version-
  controlled with the project, stable semantic identity" property the
  user's brief requires (§3.4/§8), just never tested under reimport.
- Building a second, parallel store (e.g. new SQLite tables, or a new
  YAML shape) would violate the governing instruction to reuse existing
  abstractions and would create exactly the "two competing sources of
  truth" failure mode this whole phase exists to prevent.

### 1.2 Minimal schema extension — provenance and reconciliation fields

No new record *kind*. Two new optional fields, added the same way Phase
79 added `assertion_kind`/`basis`/`evidence_support_state` (additive,
optional, fail-closed-validated, no migration of existing records
required):

- **`provenance_dimension`** (Claim/Requirement only), closed enum,
  adapting rather than replacing existing vocabulary per the user's own
  instruction:
  - `OBSERVED` — grounded in `basis: observed_behaviour` (already
    exists) — a fact about what the system currently does.
  - `DECLARED` — grounded in `basis: proposed_policy` or a Decision's own
    stated intent — what a maintainer asserts *should* be true, not yet
    (or not necessarily) independently observed.
  - `DECIDED` — a Requirement authorised by an `approved` Decision.
  - `DERIVED` — the default for any Claim reached by `inferred`
    reasoning over Evidence (already the `basis: inferred` value) —
    named explicitly here because the user's brief calls it out
    separately from `OBSERVED`.
  - `HISTORICAL` — a `superseded` record, kept for its own documented
    provenance trail (already how `status: superseded` behaves for
    Claims/Decisions/Evidence; this value exists so a reader doesn't have
    to infer historicity from `status` alone when `provenance_dimension`
    is being rendered in a projected document).

  This is an explicit *relabelling and unification* of fields that
  already exist and already mean almost this (`basis`, `status`), not a
  new ontology — see §0.1's own honest account of how fragmented the
  existing provenance story is (three incompatible shapes). A record's
  `provenance_dimension` is computable from its existing `basis`/`status`
  fields in the common case; it is stored explicitly only where that
  computation would be ambiguous (see `check_provenance_dimension_consistency`,
  §11).

- **`reconciliation_state`** (Claim/Requirement only), closed enum — new,
  since nothing today tracks "has this record's own content been checked
  against an intermediate-document edit":
  - `CONFIRMED` — the record's content and its cited evidence currently
    agree (maps onto `docs-maintainer`'s `supported` / `domain-skeptic`'s
    `aligned`).
  - `INTENT_ONLY` — a `DECLARED`-provenance record with no supporting
    `OBSERVED` evidence yet — maps onto an un-evidenced Decision/proposed
    Claim.
  - `CONFLICT` — new or edited content contradicts existing evidence
    (maps onto `stale_or_contradicted` / `conflicting`).
  - `UNVERIFIED` — a new claim with no evidence checked either way yet
    (maps onto `insufficiently_verified`).
  - `STALE` — the record's own cited evidence has itself moved since
    last reconciled (reuses `check_snapshot_current_divergence`'s own
    hash-comparison logic directly, generalised from "snapshot vs. live"
    to "last-reconciled vs. live").
  - `PRESENTATION_ONLY` — not a record state at all; a *projection-level*
    tag applied to a Markdown edit found to carry no semantic change
    (§9's presentation-vs-semantic distinction) — recorded in the
    reconciliation log, never written onto a knowledge record, since
    nothing about the canonical model changed.

  **A semantic change introduced through an intermediate document is
  never set directly to `CONFIRMED`.** The reconciliation engine (§8)
  always lands a new/edited claim at `INTENT_ONLY`, `CONFLICT`, or
  `UNVERIFIED` first; only a *separate*, evidence-gated re-verification
  step (reusing the existing Claim `verified` promotion discipline —
  independent re-derivation or a human Decision, never an `aligned`
  comparison finding alone, per `decisions/0066`'s own already-established
  rule) can move it to `CONFIRMED`. This directly satisfies the user's
  own explicit requirement: *"A semantic change introduced through an
  intermediate document must not become OBSERVED merely because an
  external AI wrote it."*

### 1.3 Consolidating "invariant" — not a new record kind

Per §0.1's own honest finding, "invariant" is currently three unlinked
things. This phase consolidates, minimally:

- `assertion_kind: invariant` (already exists on Claims) becomes the one
  authoritative way to mark a Claim as an invariant.
- `docs/domain/invariants.md` (the existing project-wide file) becomes a
  **projected view** (§4) filtering Claims by `assertion_kind: invariant`
  — not a separately hand-maintained file once this phase ships, though
  it is not migrated in this phase (see §18 non-goals: "migrate every
  existing `docs/domain/` page" is out of scope — this phase ships the
  *mechanism*; migrating `invariants.md` itself to be a live projection
  is a natural, separately-scoped follow-on named in §19).
- A `design.md`'s own informal "Invariants" subsection convention is
  documented as "this is where a Claim with `assertion_kind: invariant`,
  not yet promoted, is drafted before promotion" — a workflow note, not a
  schema change.

"Constraint," "edge case," and "assumption" (named in the user's own
brief alongside "invariant") are **not** given their own record kinds
either, per the explicit non-goal against "exhaustive ontology
modelling" (§18): a constraint is a `rule`- or `invariant`-kind Claim; an
edge case is a `boundary`-kind Claim (already an enum value); an
assumption is a Claim with `basis: proposed_policy` not yet checked
against evidence (`reconciliation_state: INTENT_ONLY`). "Workflow" and
"behaviour" similarly map onto existing kinds: a behaviour is typically a
`relationship`- or `state_transformation`-kind Claim; a workflow is a
named, ordered sequence of such Claims (a Claim can already `depends_on`
another Claim — an ordered workflow is expressible as a chain of
`depends_on` links plus one summarising Claim, not a new kind). **One
small, genuinely new addition**: `assertion_kind` gains two more enum
values, `workflow` and `constraint`, for the cases where forcing a
workflow/constraint into `relationship`/`rule` would lose real meaning a
reader needs — reviewed for approval alongside the rest of §1.2's schema
change, kept to the smallest addition that covers the brief's own named
list without inventing a parallel taxonomy.

### 1.4 Stable semantic identity

Already provided by the existing `id:` field + filename convention —
**untested under reimport, not actually broken.** This phase's own
acceptance tests (§16) are what first exercise this property for real:
a record's `id` must survive (a) the intermediate document being
re-rendered after the record's own prose is edited by a human, and (b)
the record's own file being reorganised (moved, renamed, split) on the
canonical side, without the projected Markdown's own per-paragraph
anchors breaking. §4.3 defines the concrete anchor mechanism.

---

## 2. Intermediate knowledge documents

### 2.1 Smallest coherent representation — not the brief's own illustrative layout verbatim

The brief's own sketched `.codecompass/knowledge/{project,phases}/...`
layout is explicitly offered as illustrative, not prescribed ("Do not
adopt this exact filesystem layout without first evaluating existing
repository conventions"). Evaluated against what already exists:

- `planning/knowledge/<slug>/` is **already** this project's own
  established convention for a bounded knowledge scope (one directory
  per feature/topic, holding its own records + optional snapshot).
  Reusing it directly avoids introducing a second, competing directory
  convention — a new top-level `.codecompass/` tree would duplicate
  exactly the thing this plan's governing instruction forbids.
- **Decision**: intermediate knowledge documents for a bounded scope
  (project-wide concepts, or one phase) live at
  `planning/knowledge/<slug>/intermediate/<name>.md` — a new
  `intermediate/` subdirectory sitting alongside each slug's existing
  records and (where one exists) its `snapshots/` directory. This keeps
  the new, editable, human/tool-facing Markdown clearly separated from
  the canonical YAML records in the same place a reader already knows to
  look, rather than inventing a new top-level location.
- Project-wide intermediate documents (the brief's own
  `project/architecture.md`/`concepts.md`/`invariants.md`/`interfaces.md`/
  `domain.md`) use a reserved slug, `planning/knowledge/codecompass-domain/intermediate/`
  — reusing the *existing* `codecompass-domain` slug (already the home
  of CodeCompass's own project-wide domain corpus, per Phase 80's own
  snapshot work), not inventing a new "project" slug.
- Phase-scoped intermediate documents use whatever slug that phase's own
  research already uses (e.g. `planning/knowledge/first-party-source-symbols/intermediate/`)
  — reused, not duplicated, when a phase already has a knowledge slug;
  a genuinely new phase with no prior knowledge work gets a new slug the
  same way `context-researcher` already names one today.

### 2.2 What an intermediate document actually is

A **live, re-renderable projection** of a filtered set of canonical
records (not a frozen snapshot, and not freshly-generated prose each
time) — the content is deterministically assembled from the records'
own fields (statement, evidence citations, status, examples,
counterexamples, open questions), formatted for human/tool readability,
with **stable per-record anchors** (§4.3) so a targeted edit can be
mapped back to the exact record it changed.

### 2.3 Regeneration without destroying accepted human contributions

The projection/reconciliation loop (§8) guarantees: re-rendering a
record whose own canonical content has not changed since last
reconciliation reproduces byte-identical prose for that record's own
block (no formatting churn); a record whose canonical content *has*
changed (e.g. a Decision promoted it) re-renders that one block, leaving
every other block's own prose untouched; **a block corresponding to a
record still sitting at `INTENT_ONLY`/`CONFLICT`/`UNVERIFIED` is never
silently overwritten by a regeneration** — regeneration only ever
replaces a block once reconciliation has processed whatever edit
produced its current state, never speculatively.

---

## 3. Explicit external editing protocol

### 3.1 The guide

`docs/codecompass-knowledge-workflow.md` (new, user-facing, no
CodeCompass-internals knowledge assumed) — covers the 11 points the
brief names, each mapped onto a concrete mechanism already designed
above:

1. **What intermediate documents represent** — §2.2's own definition,
   stated plainly: "a live view of what CodeCompass's own canonical
   knowledge currently says, that you can edit."
2. **Which files may be edited** — anything under
   `planning/knowledge/*/intermediate/` — never `planning/knowledge/*/*.yaml`
   directly (those are the canonical records' own storage format, not
   meant for hand-editing — editing a projection and letting
   reconciliation update the record is the supported path), never
   `planning/knowledge/*/snapshots/*.toml` (frozen, historical).
3. **Machine-derived vs. maintainer-authored** — every rendered block
   carries a provenance line (reusing §1.2's `provenance_dimension`) so
   a reader can tell "this is `OBSERVED` fact" from "this is `DECLARED`
   intent" from "this is historical" without reading YAML.
4. **How to add new material** — append a new block under the
   document's own "Candidate additions" section (a plain Markdown
   heading, not requiring any special syntax) describing the new domain
   knowledge/edge case/invariant/test/constraint/rationale in ordinary
   prose; reconciliation (§8) turns it into a new Observation+Claim pair.
5. **What not to modify directly** — the YAML records, the snapshots,
   and any block's own anchor comment (§4.3) — edit the prose around an
   anchor, never the anchor itself.
6. **How identity/provenance is preserved** — the anchor mechanism
   (§4.3), explained at a level a non-technical reader/tool can follow
   without understanding the underlying YAML.
7. **How changes are submitted** — an ordinary Git commit/PR, exactly
   like any other file change; reconciliation runs as a checked-in step
   (§11), not a separate submission channel.
8. **What happens when Markdown disagrees with source evidence** — §1.2's
   `CONFLICT` state, surfaced explicitly in the reconciliation log and
   the next re-rendered projection (never silently resolved — §14).
9. **How conflicts/unverified claims are surfaced** — a dedicated
   "Open conflicts" section in every projected document (§4), populated
   from any record at `CONFLICT`/`UNVERIFIED` touching that document's own
   scope.
10. **Editing ≠ immediate canonicity** — stated as the single most
    important sentence in the guide, verbatim close to: *"Editing this
    file does not make your statement true in CodeCompass's own records
    until reconciliation has checked it against evidence. Until then,
    your addition is `INTENT_ONLY`, visible, and real — just not yet
    confirmed."*
11. **The reconciled database is authoritative afterward** — stated
    explicitly, with a pointer to what "the database" means here (§1 —
    the `planning/knowledge/` corpus, not a literal SQL database), so a
    reader doesn't go looking for a `.db` file.

### 3.2 Suitability for AI tools specifically

The guide is written to be a complete, self-contained instruction set
for an LLM reading cold — no reference to "see the CLAUDE.md file" as a
prerequisite (though it is cross-linked from `CLAUDE.md`/`README.md`/
`CONTRIBUTING.md`, §10), no CodeCompass-internal terminology introduced
without a one-sentence definition inline. This mirrors the existing,
already-proven `ai-docs/README.md` pattern (an agent-oriented capability
overview, self-contained, example-prompt-driven) rather than inventing a
new documentation register.

---

## 4. Intermediate document structure and rendering

### 4.1 File set — minimal, not the brief's own full illustrative tree

Per §2.1, one `intermediate/` directory per knowledge slug. Within it,
the smallest coherent file split (not the brief's own 5+8 file
illustrative layout, evaluated and reduced):

- `overview.md` — concepts, architecture, domain knowledge for this
  slug (the brief's own `architecture.md`/`concepts.md`/`domain.md`
  merged — splitting them further is deferred until real usage shows a
  single file is unwieldy, per "prefer the smallest coherent
  representation").
- `invariants-and-constraints.md` — invariant/rule/boundary-kind Claims.
- `interfaces-and-behaviours.md` — relationship/state_transformation-kind
  Claims, including workflows (§1.3).
- `open-questions-and-conflicts.md` — every `CONFLICT`/`UNVERIFIED`
  record touching this slug, plus genuinely open questions
  (`open_questions` field content) — this is the one file every
  reconciliation run is guaranteed to touch, so it is kept separate from
  the calmer reference material above.

A phase-scoped slug may also render `tests-and-acceptance.md` (§5) when
the phase's own records include Requirement-kind entries citing test
expectations — omitted when there's nothing to put in it, never an empty
placeholder file.

### 4.2 Rendering algorithm

Deterministic, reusing `VendorDigest`'s own established rendering
pattern: for each target file, select the records matching that file's
own filter (by `assertion_kind`, by `reconciliation_state`, by slug),
render each as one Markdown block (heading + statement + citations +
status line), in a stable sort order (by `id`), wrapped in the anchor
comment (§4.3). No AI call in the rendering step itself — this is
mechanical formatting of already-existing record content, the same
posture `VendorDigest` rendering already has.

### 4.3 Stable anchors

Each rendered block opens with an HTML comment carrying the record's own
`id` and the exact content-hash of what was rendered:

```markdown
<!-- codecompass-knowledge: CL-ARCH-014 sha256:3f9a1c... -->
### The sync pipeline is idempotent under repeated invocation

[rendered statement, citations, status line]

<!-- /codecompass-knowledge -->
```

On reimport (§8), the reconciliation engine parses every
`codecompass-knowledge` comment pair, diffs the enclosed prose against
what the *current* canonical record would render, and classifies the
result. Prose a human edited between the markers is a candidate
semantic change; a comment pair itself being moved, or new, unmarked
prose appearing outside any marker pair, is the "Candidate additions"
case (§3.1 point 4) — new content with no existing record to diff
against, always entering as a brand-new proposed Claim, never silently
attached to an unrelated existing one.

---

## 5. Phase knowledge packages

### 5.1 Reuse `knowledge-curator`'s existing context-packet-assembly mode, generalised

Per §0.3, this mechanism already exists for one narrow case
(compacting an `APPROVED design.md`'s own reachable records into
`context-packet.md`). This phase generalises its *gate*, not its
*mechanism*: a phase knowledge package is assembled the same way,
**triggered by a phase's own plan file existing** (not requiring a
separate `design.md`/`APPROVED` gate that most phases don't produce),
scoped to whatever `planning/knowledge/<slug>/` the phase's own research
populates.

### 5.2 Not separate files, not a separate representation — a filtered view

Per the brief's own point 5 ("determine whether these are separate
files, views over common knowledge objects, or another lightweight
representation"): **a view.** A phase knowledge package is the same
`intermediate/*.md` rendering (§4) scoped to one phase's own slug, plus
one additional file, `phase-brief.md`, summarising the Ledgerkit-style
categories the brief names (feature intent, domain terminology, edge
cases, invariants, existing/desired behaviour, compatibility
constraints, affected interfaces, test scenarios, acceptance behaviour,
open questions) as a single entry point linking into the slug's own
`intermediate/` files rather than duplicating their content.

### 5.3 Promotion, not permanent detachment

Per the brief's own explicit requirement: a durable discovery made
during a phase (a real invariant, a real domain-semantics fact) is a
Claim in that phase's own `planning/knowledge/<slug>/`, exactly like
today. **What's new**: reconciliation (§8) checks, for every Claim
reaching `CONFIRMED`, whether its own `assertion_kind`/content makes it
relevant beyond the originating phase — a project-wide invariant
discovered mid-phase gets a `depends_on`/cross-reference into
`codecompass-domain`'s own corpus (a Claim can already cite another
Claim via `depends_on`; this phase adds a convention, not a schema
change, for when a project-wide cross-reference is warranted) — so nothing
durable stays trapped in a historical phase's own planning directory
once Phase N closes, matching this project's own existing practice
(e.g. Phase 77's first-party-source findings feeding Phase 78's own
`CG-001` evidence) rather than inventing a new promotion mechanism.

---

## 6. Ledgerkit-style expected workflow (dogfood design)

Reuses `reference-project-protocol.md`'s own established conventions
throughout (§0.4) — no new reference-project methodology is invented.

1. CodeCompass (the lead, planning a bounded Ledgerkit phase) retrieves
   repository evidence the same way it already does, plus any existing
   reconciled knowledge for the relevant slug (`planning/knowledge/<slug>/`,
   if one already exists from a prior phase).
2. A phase knowledge package (§5) is assembled and committed, covering
   the brief's own named categories.
3. The developer (or an external tool: ChatGPT, Copilot, Claude Code, a
   plain editor) inspects and edits the package's own `intermediate/`
   files using ordinary repository workflows — no CodeCompass invocation
   required to *read* or *propose* a change.
4. Changes are submitted as an ordinary Git commit/PR (§3.1 point 7).
5. Reconciliation (§8/§11) runs — either as a CI check, a pre-merge
   step, or an explicit CLI invocation (§11 names the exact surface) —
   classifying each semantic change (§7) against available evidence.
6. Reconciled knowledge lands in the canonical records with provenance
   (§1.2); conflicts/unsupported claims stay explicit, never silently
   resolved (§14).
7. Updated `intermediate/*.md` files are re-rendered (§4.2) from the
   now-current records.
8. Coding/planning agents consume the reconciled knowledge directly
   (§13) — no separate development-only store.
9. After implementation, changed source/tests trigger revalidation
   (§12) of whichever Claims cited the now-changed evidence.
10. README/CONTRIBUTING/architecture docs are refreshed where the
    reconciled knowledge actually bears on their own content (§9/§12),
    not wholesale.

**This workflow is explicitly validated to remain useful when the code
is written manually** (§16's dogfood scenarios include a pure
knowledge-refinement cycle with no implementation step at all) — nothing
in steps 1-7 requires an agent to write the implementation.

---

## 7. Provenance and reconciliation — the unified state model

§1.2 already defines the two closed enums (`provenance_dimension`,
`reconciliation_state`) and their mapping onto existing vocabulary. This
section states the cross-cutting rules the brief asks for explicitly:

- **Observed reality and declared intent are separate dimensions,
  never merged into one field.** A record's `provenance_dimension`
  (what kind of grounding it has) is independent of its
  `reconciliation_state` (whether that grounding currently checks out)
  — a `DECLARED` record can be `CONFIRMED` (a maintainer's stated intent
  that evidence happens to also support) or `INTENT_ONLY` (asserted, not
  yet checked); an `OBSERVED` record can be `CONFIRMED` or `STALE` (the
  behaviour it observed has since changed) but is never `INTENT_ONLY` —
  observation doesn't have an "intent-only" reading.
- **A human edit to an intermediate document may change `DECLARED`
  content; it may never directly overwrite `OBSERVED` content.** Reusing
  the existing `basis` field's own semantics: if an edited block's
  underlying record has `basis: observed_behaviour`, the reconciliation
  engine (§8) treats the edit as a *new, competing* Claim requiring fresh
  observation to confirm, never as a direct rewrite of the existing
  Claim's own `basis: observed_behaviour` content — this is the
  mechanical enforcement of the brief's own rule.
- **Repository evidence may update `OBSERVED` content; it may never
  silently overwrite `DECLARED` intent.** The symmetric case: if a code
  change invalidates an `OBSERVED` Claim, revalidation (§12) marks that
  Claim `STALE`/re-derives it, but a *separate*, `DECLARED`-provenance
  Claim about intended behaviour is never auto-edited by this process —
  a genuine intent-vs-reality conflict surfaces as `CONFLICT`, not a
  silent overwrite in either direction.

---

## 8. Database authority and document projection — the mechanical loop

```
canonical records (planning/knowledge/*/*.yaml)
        ↓  render (§4.2, deterministic, no AI call)
intermediate/*.md  (stable per-record anchors, §4.3)
        ↓  human/tool edit, ordinary Git workflow
edited intermediate/*.md
        ↓  parse anchors, diff enclosed prose (§11, mechanical)
semantic diff: per-anchor {unchanged | edited | new-unanchored}
        ↓  for each `edited`/`new`: classify (§7) against cited evidence
        ↓  (a fresh, read-only comparison dispatch — reusing the
        ↓   domain-skeptic/docs-maintainer dispatch pattern, §0.3 —
        ↓   never the lead's own assertion, matching this project's
        ↓   established non-rubber-stamp discipline)
reconciliation result: new/updated record(s) at CONFIRMED/INTENT_ONLY/
CONFLICT/UNVERIFIED, written via the canonical records' own existing
file format (same validation script, same fail-closed checks)
        ↓  re-render (§4.2) — unaffected anchors reproduce byte-identical
        ↓  prose; only changed anchors' own blocks are rewritten
refreshed intermediate/*.md
```

**No formatting churn**: re-rendering a record whose content is
unchanged since it was last rendered produces byte-identical output for
that block (the renderer is a pure function of the record's own current
field values plus the fixed template — same record content in, same
bytes out, regardless of how many times it runs). **No erased prose
improvements**: a maintainer's own free-text edit to *wording only*
(inside an anchor, same semantic content) is detected as
`PRESENTATION_ONLY` at the per-anchor diff step and the maintainer's own
edited wording is kept as the record's own new rendered form (the
record's `statement` field itself is updated to the clarified wording,
with no status-field change) — not reverted on the next regeneration, and
not a cost accounted the way a semantic change is.

**Users never manipulate opaque database internals**: every edit happens
in ordinary Markdown; the YAML records are an implementation detail the
guide (§3) explicitly tells a reader not to touch directly, but nothing
about the *editing* workflow requires understanding them.

---

## 9. Project documentation integration

### 9.1 Reuse existing doc-artifact identity

Per §0.2, `README.md`/`architecture/**`/`docs/**`/`decisions/**` are
*already* `doc_artifacts` rows with stable path identity and content
hashes (`doc_chunks`). This phase does not invent a parallel identity —
a presentation-vs-semantic classification (§9.2) is keyed on the same
`doc_artifacts.path`/content-hash CodeCompass already tracks.

### 9.2 Detecting presentation vs. semantic edits

A documentation file's own content-hash changing is already mechanical
(every `sync` recomputes it). Whether the change is *semantic*
(asserts/changes a project-fact a Claim should reconcile) or
*presentational* (wording, formatting, reorganisation with no factual
change) is **not mechanically decidable from the hash alone** — this
requires the same kind of fresh, read-only comparison dispatch already
established for `docs-maintainer`/`domain-skeptic` (§0.3), given the
changed doc's own diff and the Claims it's already known to relate to
(via existing `doc_relations_edges` mention-detection, or an explicit
citation if the doc already names a Claim id). This keeps the detection
step bounded and reusing an existing dispatch pattern, rather than
building new NLP/classification machinery — explicitly named as a
judgment call requiring real evidence to tune (§16 includes this as a
dogfood scenario), not assumed solved on day one.

### 9.3 The flow

```
canonical project knowledge (Claims tagged relevant to a doc, via
  depends_on or explicit citation)
        ↓
documentation knowledge/context view (a new intermediate/*.md scoped to
  "project documentation," reusing §4's rendering)
        ↓
README / CONTRIBUTING / architecture / guides / reference
  (human/external-tool-authored prose, NOT auto-generated wholesale —
  per the brief's own explicit "do not require every sentence to be
  generated")
        ↑  refinement (ordinary edits)
        ↓
presentation edit → logged, no reconciliation triggered, no Claim touched
semantic edit → candidate Claim change → reconciliation (§8), same path
  as an intermediate-document edit
```

### 9.4 Worked examples, matching the brief's own three

- Rewriting a README introduction for clarity: hash changes, comparison
  dispatch finds no Claim-relevant factual delta → `PRESENTATION_ONLY`,
  logged, nothing reconciled.
- Changing a supported-behaviour statement: comparison dispatch finds
  the new wording asserts something the cited Claim doesn't currently
  say → a candidate Claim edit, enters reconciliation exactly like an
  `intermediate/` document change.
- Adding an architectural invariant to `CONTRIBUTING.md` (if brought
  into scope — §2.1's open decision): either the invariant already
  exists as a Claim (the addition is treated as a citation, not a new
  claim) or it doesn't (a new candidate Claim, `assertion_kind: invariant`,
  entering reconciliation at `INTENT_ONLY`/`UNVERIFIED`).

---

## 10. README and CONTRIBUTING implications

- **`README.md`** gains one short paragraph (not a new top-level
  section competing with its own existing, carefully-curated structure)
  under "How it works," pointing to `docs/codecompass-knowledge-workflow.md`
  — matching this project's own established "link, don't duplicate"
  convention (e.g. how it already points to `ai-docs/` rather than
  restating its content). No new authority: the paragraph explicitly
  states the knowledge workflow doc is itself grounded in and
  reconciled against the same canonical records, so README never
  becomes a second, divergent description of what's canonical.
- **`CONTRIBUTING.md`** gains a new section, "Knowledge-affecting
  changes," explaining: when a code change also changes/reveals project
  knowledge (a new invariant, a changed behaviour), the accompanying
  commit should either cite the relevant existing Claim or add a new one
  via the intermediate-document workflow — mirroring `CLAUDE.md` §1's
  own existing "plan before implementing" discipline, extended to
  knowledge rather than code. This is process guidance, not a
  machine-manifest — written in the same register as the rest of
  `CONTRIBUTING.md`'s existing prose.
- Neither file becomes a second authority: both explicitly state that a
  factual claim here, if it ever disagrees with the reconciled
  knowledge, is itself a `CONFLICT` to be reconciled, not a correction
  to apply by hand to the knowledge layer — closing the loop the brief's
  own point 10 asks for ("avoid becoming an independent authority that
  silently diverges from the knowledge DB").

---

## 11. CLI / reconciliation surface

One new CLI surface, following `enrich apply`'s own established shape
(§0.2) rather than inventing a new command family:

- **`codecompass knowledge render [<slug>]`** — runs §4.2's rendering
  for one slug or all slugs with an `intermediate/` directory. Pure,
  deterministic, no AI call, safe to run any time (matches `VendorDigest`
  rendering's own existing idempotent-refresh posture).
- **`codecompass knowledge reconcile <slug> [--dry-run]`** — runs §8's
  loop for one slug: parses anchors, computes the per-anchor diff,
  dispatches the comparison step (§8's "fresh, read-only comparison
  dispatch" — in this CLI-only, non-agent-orchestrated context, this
  means: flag every `edited`/`new` anchor for a human/agent-led
  reconciliation pass, rather than this CLI command itself invoking an
  LLM — **CodeCompass's own process never calls an AI model to decide
  reconciliation outcomes autonomously**, consistent with
  `decisions/0051`'s determinism-first boundary; the actual
  classification judgment is made by whichever agent or human runs the
  reconciliation, the same way `enrich apply` requires a human/agent to
  have already produced the content it mechanically validates). `--dry-run`
  reports what would change without writing records.
- **`codecompass knowledge status [<slug>]`** — reports every record at
  `CONFLICT`/`UNVERIFIED`/`STALE`, reusing `check`'s own existing
  reporting conventions (table/JSON, `--strict` exit-code semantics).

New validation additions to `scripts/check_knowledge_base.py` (same
file, same fail-closed discipline, not a new script):
`check_provenance_dimension_consistency` (a record's own
`provenance_dimension`, where explicitly set, must not contradict its
`basis`/`status`), `check_anchor_integrity` (every `intermediate/*.md`
file's own anchors resolve to a real record with matching id/kind — the
same "identity, not merely a hash match" discipline Phase 80 hardened
for snapshots, applied here to live projections).

---

## 12. Incremental documentation maintenance

Reuses `documentation-lifecycle.md`'s own existing per-phase drift-audit
mechanism and incremental-maintenance loop (§0.4), extended — not
replaced — with the new knowledge-layer's own revalidation trigger:

```
source/test changed
       ↓  (existing: sync detects the content-hash change on the
       ↓   relevant source_files/doc_artifacts row)
affected evidence identified
       ↓  (new: any Claim whose Evidence cites that file/path is flagged)
dependent knowledge revalidated
       ↓  (existing comparison-dispatch pattern, §0.3 — not a new
       ↓   mechanism)
canonical record updated (CONFIRMED→STALE, or re-derived) or CONFLICT
raised
       ↓
affected intermediate/*.md re-rendered (§4.2, targeted — only the
file(s) containing the affected record's own anchor)
       ↓
affected project docs identified (via existing doc_relations_edges
mention-detection, or explicit citation)
       ↓
targeted documentation update (§9.2's semantic-diff dispatch, scoped to
just the affected doc, not a full-tree regeneration)
```

**Explicitly not** a full documentation-tree regeneration on every
change — the existing `documentation-lifecycle.md` §2.5 per-phase drift
audit already establishes the "scoped to what changed" discipline this
phase extends, not reinvents.

---

## 13. Development/coding context integration

**No separate development-only knowledge database** (explicit non-goal,
matching the brief). A coding/planning/review context package for a
bounded task is: the same `intermediate/*.md` rendering (§4), scoped by
the task's own slug/phase, optionally filtered to just the relevant
records (reusing `context-packet.md`'s own existing per-feature
compaction logic, §0.3) — consumed directly by a CodeCompass agent
(reading the Markdown, same as any other file) or externally (handed to
ChatGPT/Copilot/a future MCP surface as-is, since it's already plain,
self-contained Markdown — no new export format needed). The "open
conflicts" section (§4.1) is always included, so a consuming agent sees
unresolved contradictions rather than a falsely-confident single answer.

---

## 14. Safe collaboration model

Ownership semantics, reusing `decisions/0051`/`0054`'s own established
provenance-tagging convention (`model`/`performed_by`-style fields,
`agent:<name>` namespacing) rather than inventing a new identity system:

| Content class | Who may author it | Enters as |
|---|---|---|
| Machine-observed evidence | Mechanical detection only (existing `sync` pipeline) | `OBSERVED`, directly |
| Machine-derived knowledge | A derivation dispatch (`context-researcher`-style), citing real evidence | `DERIVED`, `UNVERIFIED` until checked |
| Maintainer-declared intent | A human, via a Decision or a direct intermediate-document edit | `DECLARED`, `INTENT_ONLY` until evidence-checked |
| Accepted decisions | A human only — unchanged from today's existing rule (Decision is "the only kind a human alone authors") | `DECIDED` |
| Externally proposed knowledge | Any external tool/person, via an intermediate-document edit | always a **candidate** — `UNVERIFIED`/`INTENT_ONLY`/`CONFLICT`, never `CONFIRMED` on entry (§1.2) |
| Presentation prose | Anyone, anywhere (README wording, etc.) | not a knowledge record at all — `PRESENTATION_ONLY`, logged only |

Retained per-record: who/what introduced a change (reusing the existing
`derived_by`/`decided_by`/`performed_by` fields, extended with the
`agent:<name>` convention for an external-tool-authored edit where the
tool identifies itself — and an honest, unlabelled "external edit, tool
unknown" value when it doesn't, never a guess), the evidence used during
reconciliation (the Evidence record itself), previous states (Git
history of the YAML file — already real, nothing new needed), and
unresolved contradictions (`CONFLICT`-state records, never silently
dropped). **No contradiction is resolved merely to keep documentation
internally consistent** — a `CONFLICT` stays a `CONFLICT`, rendered
explicitly in every affected projection, until a real Decision or new
Evidence resolves it; reconciliation is explicitly forbidden from
picking a side on its own.

---

## 15. Repository self-description

Minimum standard files for a CodeCompass-enabled project to be
self-describing to a cold external agent (per the brief's own nine
questions):

- `docs/codecompass-knowledge-workflow.md` (§3) — answers "what is
  CodeCompass doing here," "where does intermediate knowledge live,"
  "what is canonical," "what may be edited," "how to propose a change,"
  "how reconciliation occurs," "where evidence belongs."
- The existing `CLAUDE.md`/`CONTRIBUTING.md` (§10's additions) — "how
  phase knowledge should be extended" and "how documentation relates to
  knowledge," cross-linking rather than duplicating §3's own guide.
- `planning/knowledge/<slug>/intermediate/` itself, once it exists, is
  self-describing by structure (its own file names already say what
  they contain, per §4.1) — no separate manifest file needed inside each
  slug beyond what §3's guide already establishes project-wide.

### 15.1 `codecompass-template` implications

A new, concise addition — not a copy of CodeCompass's own full
`planning/knowledge/` apparatus (the template's own established
"lightweight adoption, avoid importing CodeCompass's governance
ceremony" convention from Phase 80 applies unchanged here). Proposed:
a new `optional-intermediate-knowledge/` directory, sibling to the
existing `optional-clean-room-workflow/` (which already shares this
phase's own underlying "canonical knowledge → documentation" idea in
narrower, one-shot form) — containing: a short `README.md` explaining
what this is and when to adopt it (mirroring
`optional-clean-room-workflow/README.md`'s own established tone and
length), one worked example (reusing `worked-example.md`'s own existing
pattern), and the minimal file skeleton (§4.1's four files, empty/
templated). **Whether to merge this into `optional-clean-room-workflow/`
itself (since the two are conceptually related — this phase's own
bidirectional loop is a natural generalisation of that workflow's
one-shot pipeline) or keep them as separate opt-in directories is named
as a decision requiring approval** (§"Decisions requiring explicit
maintainer approval") — both are defensible, and the template's own
"smallest coherent representation" goal applies here too.

---

## 16. Testing and dogfood validation

### 16.1 Deterministic unit/integration tests (new `tests/test_knowledge_intermediate.py`, following this project's own existing test-file-per-module convention)

- Render → no-op reimport → re-render produces byte-identical output
  (proves §8's "no formatting churn" claim mechanically, not by
  assertion).
- Render → edit one anchor's prose (same semantic content, different
  wording) → reconcile → classified `PRESENTATION_ONLY`-equivalent (a
  wording-only Claim-statement update, no status change) → re-render
  preserves the edited wording (proves "no erased prose improvements").
- Render → edit one anchor's prose (new factual claim) → reconcile →
  new/edited Claim lands at `UNVERIFIED` or `INTENT_ONLY`, never
  `CONFIRMED` (proves §1.2's core safety rule mechanically).
- Render → canonical record's own file is reorganised (moved to a
  different filename, same `id:`) → re-render still resolves the
  existing anchor correctly (proves §1.4's stable-identity claim under
  the one reorganisation case that's cheap to test without a full
  dogfood run).
- `check_anchor_integrity`/`check_provenance_dimension_consistency`:
  disposable-git-fixture reproductions of each failure mode (a stale
  anchor hash, an id/kind mismatch, a contradicting `provenance_dimension`/
  `basis` pair) *before* the fix, matching this project's own established
  "reproduce before fixing" discipline for every fail-closed check
  (Phases 79/80's own precedent) — required by `CLAUDE.md` §1's own
  minimal-content-edge-case and depth-vs-scope rules for any new
  fail-closed mechanism.

### 16.2 Realistic dogfood scenarios (reusing `reference-project-protocol.md`'s own conventions, §0.4) — the brief's own eight scenarios, each mapped to a concrete mechanism above

1. **External knowledge refinement** → §8's reconciliation loop, a real
   Ledgerkit-scoped `intermediate/` edit adding a genuine edge case,
   verified end to end.
2. **Unsupported external claim** → §1.2's `UNVERIFIED` state, verified
   that no code path can promote it to `CONFIRMED`/`OBSERVED` without a
   real re-verification step.
3. **Code contradicts intent** → §7's `CONFLICT` state, a real disposable
   fixture: a declared invariant, an implementation that violates it,
   confirm both survive and the conflict is explicit, never silently
   dropped (reusing the disposable-git-fixture pattern already
   established for Phase 80's own correction work).
4. **Code changes first** → §12's revalidation loop, a real source
   change invalidating a Claim's cited evidence, confirmed to trigger
   `STALE` and a targeted (not whole-tree) documentation-impact check.
5. **Presentation-only edit** → §9.4's first worked example, confirmed
   no knowledge conflict/record write occurs.
6. **README factual edit** → §9.4's second worked example, confirmed the
   semantic-diff dispatch actually fires and README cannot silently
   diverge.
7. **Phase promotion** → §5.3, a real phase-scoped Claim promoted into
   `codecompass-domain`'s own corpus, confirmed retrievable by a later,
   independent phase.
8. **Clean-room isolation held** → reusing the existing
   `boundary_check.py` mechanical-transcript-analysis tool (Phase 79/80's
   own established method, §0.4) against whatever dispatch runs the
   comparison step in scenario 1/6 above — proving excluded legacy
   documentation cannot enter the reconstructed canonical knowledge
   during a clean-room-scoped reconciliation run, labelled `best-effort`
   per this project's own honest, unchanged isolation posture (§0.4) —
   never claimed `verified`.

Every dogfood scenario above is run against a real, pinned Ledgerkit
commit, using the existing seed-then-fork scratch-clone discipline
(`reference-project-protocol.md` §2.2) — no new reference-project
convention invented.

---

## 17. Migration of existing documentation/redoc work

Already tabulated in full at §0.5. Summary: **nothing existing is
discarded.** The clean-room pipeline (`decisions/0066`-`0070`), the
Observation/Evidence/Claim/Derivation model, the frozen-snapshot format,
`spec_docs.py`'s project-doc tracking, the two comparison vocabularies,
and `knowledge-curator`'s context-packet mode all become **downstream
consumers or direct foundations** of this phase's own mechanism, exactly
as the brief's own governing architectural principle requires. The one
genuinely new thing is the bidirectional reconciliation loop itself
(§8) — everything else is retained or generalised in place.

---

## 18. Scope discipline — this phase's own vertical slice

Ships exactly:

- Canonical knowledge storage: the existing six-record-kind model, with
  §1.2's two new optional fields and §1.3's two new `assertion_kind`
  values.
- Human/tool-editable intermediate docs: §2-§4, for **one** real slug
  (`codecompass-domain`, reusing Phase 80's own already-populated
  corpus) plus **one** real phase-scoped slug exercised end-to-end in
  dogfood (§16.2).
- Semantic reconciliation: §7/§8/§11's CLI surface and validation
  additions.
- Phase knowledge workflow: §5/§6, validated once, end to end, against
  a real Ledgerkit task (reusing an already-identified, already-
  live-verified candidate if one is still current at implementation
  time — e.g. the Phase 78-amendment's own named `stats` follow-up
  candidate, `planning/phase-78-amendment-followup-plan.md`, re-verified
  live before use, not assumed still accurate).
- At least one project-doc consumer: README's own new pointer paragraph
  (§10) plus one real semantic-edit reconciliation exercised against it
  (§16.2 scenario 6).

**Explicitly not in this phase** (named for the follow-on backlog, §19):
a complete general-purpose knowledge graph (new `context-graph.db`
tables for concepts/behaviours — §0.2's boundary holds); full MCP
delivery (Phase 25, already independently deferred); autonomous
conflict resolution (§14's own explicit prohibition); arbitrary
natural-language database editing (every edit goes through the
anchor-based, record-identified mechanism — never "describe a change in
prose anywhere and have it parsed into an arbitrary record"); a rich UI
(plain Markdown + existing CLI only); exhaustive ontology modelling
(§1.3's own explicit minimalism); automatic acceptance of AI-generated
claims (§1.2/§14's own core safety rule).

---

## 19. Files expected to change

### This planning commit (now)

- **New**: this file,
  `planning/phase-81-intermediate-knowledge-layer.md`.
- **`planning/ROADMAP.md`**: new Phase 81 row (status `planned`);
  Priority D's own status cell gains a pointer to this phase as its next
  concrete deliverable (Priority B's own status cell gains a
  cross-reference too, since this phase substantially delivers Priority
  B's own stated success criterion — "a downstream-facing claim can be
  recorded with evidence, a closed status, and a genuine contradiction
  surfaced" — as a side effect of its own core mechanism, without being
  primarily scoped as a Priority B phase).
- **`planning/CONTEXT.md`**: current-state section updated — Phase 81
  planned, pending review; next concrete step named (human review, then
  implementation per the sequence below).

### At implementation time (later commits, not this one)

1. `scripts/check_knowledge_base.py`: §1.2/§1.3's new optional fields
   and enum values; §11's two new checks — each following the existing
   "reproduce the failure in a disposable fixture before fixing"
   discipline.
2. `src/codecompass/`: new `knowledge_intermediate.py` (rendering,
   anchor-parsing, reconciliation-classification dispatch wiring) and
   `cli.py` additions (§11's three subcommands) — **no `context-graph.db`
   schema change** (§0.2/§1's own governing rule).
3. `docs/codecompass-knowledge-workflow.md` (new, §3);
   `README.md`/`CONTRIBUTING.md` additions (§10).
4. `planning/knowledge/codecompass-domain/intermediate/*.md` — the
   project-wide pilot slug (§18).
5. One phase-scoped dogfood run against Ledgerkit (§16.2), producing its
   own real `planning/knowledge/<slug>/intermediate/` content and
   reconciliation log.
6. `codecompass-template` — §15.1's new directory, a separate commit to
   that repository, after the decision named there is resolved.
7. Tests: `tests/test_knowledge_intermediate.py` (§16.1).
8. New `decisions/` ADR(s): at minimum, one recording this phase's own
   central architectural choice (§1 — canonical model stays
   `planning/knowledge/`, not `context-graph.db`) and one recording the
   unified provenance/reconciliation vocabulary (§1.2/§7) and its mapping
   onto existing fields — both genuine non-obvious tradeoffs per
   `CLAUDE.md` §2.

### At closeout (later, branch-dependent on what dogfooding finds)

- Standard closeout sequence (`CLAUDE.md` §5): retro, learning triage,
  per-phase drift audit, independent `release-phase-auditor` completion
  audit, terminal `roadmap-context-curator` reconciliation.
- If dogfooding (§16.2) surfaces a real design flaw (e.g. the anchor
  mechanism doesn't survive a reorganisation pattern real usage
  produces), a corrective amendment follows this project's own
  established append-only-ADR convention (`decisions/0066`→`0070`'s own
  precedent) — not a silent in-place fix.

---

## Risks and mitigations

- **Risk**: the bidirectional loop is the one genuinely novel mechanism
  in this whole plan (§0.3) — everything else is reuse, but this part
  has no existing precedent to lean on. **Mitigation**: the vertical
  slice (§18) validates it against exactly one real project-wide slug
  and one real phase-scoped slug before any broader rollout; §16.1's
  unit tests pin the three core correctness properties (no churn, no
  erased improvements, no silent promotion) mechanically before any
  dogfood run.
- **Risk**: conflating "canonical knowledge model" with "`context-graph.db`"
  is the most likely way a reviewer or future contributor could
  misread this plan's own intent, given how central the graph already
  is to CodeCompass's own identity. **Mitigation**: §0.2/§1 state the
  boundary explicitly and repeatedly; the new ADR named in §19 point 8
  makes it a permanent, citable record, not just this plan's own prose.
- **Risk**: the presentation-vs-semantic classification (§9.2) is a
  genuine judgment call with no mechanical ground truth — it could be
  wrong in either direction (false `PRESENTATION_ONLY`, silently missing
  a real factual drift; false semantic flag, generating reconciliation
  noise for harmless wording changes). **Mitigation**: honestly named as
  a dogfood-tunable judgment call (§9.2), not assumed solved; §16.2
  scenarios 5/6 are specifically designed to catch both failure
  directions before the mechanism is trusted more broadly.
- **Risk**: strict isolation remains `UNMET`/`best-effort` for whatever
  dispatch performs the comparison/classification step, same as every
  prior clean-room phase. **Mitigation**: this is a known, already-
  disclosed, already-accepted limitation of this project's own current
  environment (§0.4) — not a new risk this phase introduces, and not
  something this phase attempts to solve (the separate, unfunded
  backlog item already names that work).

## Non-goals (restated from §18 for visibility)

A complete general-purpose knowledge graph; full MCP delivery;
autonomous conflict resolution; arbitrary natural-language database
editing; a rich UI; exhaustive ontology modelling; automatic acceptance
of AI-generated claims as canonical fact.

## Follow-on roadmap/backlog candidates (not scoped into this phase)

- Migrating `docs/domain/invariants.md` (and other existing hand-
  maintained `docs/domain/` pages) to be live projections rather than
  one-shot-written prose, once this phase's own mechanism is proven
  (§1.3).
- Extending the intermediate-document convention to every existing
  `planning/knowledge/<slug>/`, not just the two piloted here.
- A genuinely separate execution substrate for the comparison/
  classification dispatch step, closing the `best-effort`→`verified`
  isolation gap — this is exactly the scope of the already-filed,
  unfunded `planning/strict-isolation-for-documentation-reconstruction.md`
  backlog item; this phase does not fund or implement it, only reuses
  its framing (§0.4).
- A future MCP surface consuming phase-knowledge packages directly
  (§13) — Phase 25's own existing, independently-deferred scope.
- Resolving `CONTRIBUTING.md`'s own scope decision (§9's flagged open
  question) and then, if brought into scope, auditing it for the same
  presentation-vs-semantic treatment README gets in this phase.

---

## Decisions requiring explicit maintainer approval

Named throughout; collected here for the review pass:

1. **The canonical knowledge model is `planning/knowledge/`'s existing
   record corpus, not a `context-graph.db` schema extension** (§1). This
   is the plan's own central architectural choice and the one most worth
   a direct maintainer confirmation before implementation starts.
2. **Two new optional Claim/Requirement fields** (`provenance_dimension`,
   `reconciliation_state`) and **two new `assertion_kind` enum values**
   (`workflow`, `constraint`) — a real, if small, schema extension to an
   already-hardened validation script (§1.2/§1.3).
3. **Whether `CONTRIBUTING.md` is brought into `spec_docs.py`'s own
   scanning scope** (currently excluded alongside `CLAUDE.md`) — §0.2/§9.
4. **Whether the template's new intermediate-knowledge material is a
   separate `optional-intermediate-knowledge/` directory or merged into
   the existing `optional-clean-room-workflow/`** (§15.1).
5. **The new CLI surface's exact command names**
   (`codecompass knowledge render/reconcile/status`) — a genuine new
   top-level verb, the kind of addition this project has historically
   treated carefully (§11).
