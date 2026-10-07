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

**Amendment note (2026-10-07, same day, before implementation began)**:
this plan is amended in place — following this project's own existing
convention of revising a still-unapproved, not-yet-executed plan
directly (e.g. Phase 78's own plan was revised in place via a
`plan(phase-78): amend` commit before any trial was dispatched;
`CLAUDE.md`'s append-only-ADR convention applies to decisions that have
already informed real executed/reconciled work, which this plan has not
yet done). The amendment, direct user request, corrected twelve issues
found on review before implementation: (1) the render/edit/reconcile
loop had no account of concurrent change — a stale projection could
silently clobber a canonical record that moved after the projection was
rendered; (2) a presentation-only wording improvement was written
straight into the canonical Claim's own `statement` field, quietly
conflating presentation with semantic truth; (3) the plan's own
"Candidate additions" mechanism, as drafted, read as turning an external
assertion directly into an Observation+Claim pair — fabricating
observed-research provenance no one actually performed; (4) candidate
additions had no bounded region, risking arbitrary prose being
misread as knowledge; (5) project-document grounding relied on an AI
rediscovering relevant Claims each time rather than a durable, explicit
relationship; (6) the single `reconcile` CLI verb conflated mechanical
detection, semantic judgment, and canonical mutation into one step; (7)
the persisted `provenance_dimension` field duplicated information
already fully derivable from existing `kind`/`basis`/`status` fields;
(8) `CONFIRMED` risked letting an accepted human Decision silently
stand in for actually-observed implementation behaviour; plus
(9)-(12) the maintainer-approval list, test coverage, and the rest of
this document needed updating to match. Every numbered section below
reflects the corrected design; nothing below is stale relative to the
corrections, and no earlier draft's contradictory text survives.

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
Claim. A Requirement already records which Decision authorised it
(`authorised_by: DEC-...`) — this existing link is what lets this
amended plan compute "decided intent" without a new field (§1.2).

Also already real: a **frozen-snapshot format** (`decisions/0066`, TOML)
capturing a versioned assertion-plus-evidence-closure with real
historical git-blob hashes, and three already-working checks:
`check_snapshot_completeness` (fail-closed structural validation, hardened
across Phases 79/80), `check_snapshot_historical_integrity` (tamper
detection against historical content), and — **directly relevant to this
phase** — `check_snapshot_current_divergence`, which already detects when
a record's *current* content hash has drifted from what a snapshot froze,
informationally. This is the nearest existing thing to a
staleness/reconciliation trigger, and its own TOML shape is reused
directly (§8) for the new reconciliation manifest.

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
content hash — no schema change needed for this). **Approved without
further review — see "Decisions" at the end of this plan.**

**A project's own documentation is already a first-class graph object**,
confirmed by direct reading of `spec_docs.py`/`doc_mapping.py`: every
whole-project `sync` already detects `README.md`, `architecture/**/*.md`,
`decisions/**/*.md`, `docs/**/*.md`, `ai-docs/**/*.md`, `dev-docs/**/*.md`
(and more) as `doc_artifacts` rows (`kind='spec_doc'`, `origin='project'`
or `'pinned_reference'`), chunks them (`doc_chunks`, content-hashed), and
mechanically mention-links them to vendors/other docs
(`doc_relations_edges`). `CONTRIBUTING.md` and `CLAUDE.md` are currently
both explicitly excluded (`_EXCLUDED_ROOT_NAMES`). **Decided by this
amendment**: `CONTRIBUTING.md` is brought into scanning scope for Phase
81 (removed from `_EXCLUDED_ROOT_NAMES`), since it is now explicitly
part of project-document grounding (§9/§10); `CLAUDE.md` stays excluded
— it remains self-governing under its own §0 (any change to it needs a
reviewed diff, never mechanical scanning or grounding).

The existing `enrich` CLI command family (`cli.py`, `relation_enrichment.py`,
`decisions/0038`/`0054`) is the closest existing precedent for *both*
things this phase needs: (a) "an external actor's claim is mechanically
reconciled against the graph, not trusted on its own say-so" — an
agent-authored enrichment is accepted only if it exactly matches a
currently-pending, mechanically-detected candidate, tagged
`model = "agent:<name>"`; and (b) — directly reused for §11's amended CLI
design — **`enrich` already separates mechanical detection from
validated mutation as two distinct commands**: `enrich select-candidates`
(mechanical, read-only, produces a list of pending candidates) and
`enrich apply` (validated, the only command that writes). This two-stage
shape is the direct, already-proven precedent this phase's own
`knowledge select-candidates` / `knowledge apply` split (§11) copies,
rather than inventing new verbs.

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
yet. **Decided by this amendment**: the template gets a *separate*,
lightweight `optional-intermediate-knowledge/` directory rather than
being merged into `optional-clean-room-workflow/` — see §15.1.

### 0.5 Net effect — what's retained / generalised / migrated / superseded / deprecated (§17)

| Existing component | Disposition |
|---|---|
| Observation/Evidence/Claim/Derivation/Decision/Requirement model + `check_knowledge_base.py` | **Retain**, as the canonical knowledge store — this phase does not create a parallel store. |
| Frozen-snapshot format + its three checks | **Generalise**: reused for the new "live projection" concept (§8), with `check_snapshot_current_divergence`'s own hash-comparison logic as the direct basis for drift detection, and the TOML shape itself reused for the new reconciliation manifest (§8/§11). |
| `context-graph.db` schema/boundary | **Retain unchanged.** No new knowledge-object tables. Cited as an evidence source only. |
| `spec_docs.py`/`doc_mapping.py` project-doc tracking | **Retain**, reused as the existing identity anchor for project documentation grounding (§9), extended to include `CONTRIBUTING.md` (§0.2). |
| `VendorDigest` rendering pattern | **Generalise** into the new intermediate-document renderer (§4/§8). |
| `knowledge-curator`'s context-packet-assembly mode | **Generalise** into the phase-knowledge-package mechanism (§13), loosening its current `APPROVED`-`design.md`-only gate. |
| `docs-maintainer`/`domain-skeptic`'s two comparison vocabularies | **Generalise**, mapped onto one reconciliation-state vocabulary (§7) for this new use case; original vocabularies untouched for their own existing use cases. |
| `decisions/0051`'s "agent-suggested content is captured, never graphed, promoted only via a gate" | **Retain as the governing precedent**, extended from edges specifically to the new intermediate-document change class generally (§14). |
| `enrich select-candidates`/`enrich apply`'s detection-vs-mutation split + `agent:<name>` provenance tagging | **Generalise directly** into the new `knowledge select-candidates`/`knowledge apply` CLI surface (§11) — the single biggest reuse this amendment adds. |
| `documentation-lifecycle.md`'s six content categories + incremental-maintenance loop | **Retain**, extended (not replaced) by this phase's own targeted-update mechanism (§12). |
| `reference-project-protocol.md`'s dogfood conventions | **Retain unchanged**, reused directly for this phase's own Ledgerkit-style validation (§6/§16). |
| Bidirectional Markdown↔record reconciliation, with three-way (base/current/edited) concurrency handling | **New — does not exist today in any form.** This is the phase's own real deliverable (§1.5/§8). |
| A formal "invariant" record kind | **Superseded in its current fragmented form** by an explicit, minimal consolidation (§1.3) — not a new seventh record kind; reuses `assertion_kind: invariant` on Claims, with the two other existing informal senses pointed at it, not duplicated. |

---

## 1. Canonical knowledge model (governing ownership rule)

**The canonical knowledge model is `planning/knowledge/`'s existing
Observation/Evidence/Claim/Derivation/Decision/Requirement corpus, not a
new or extended `context-graph.db` schema.** `context-graph.db` remains
exactly what it is today: a deterministic store of mechanically-detected
structural fact, cited *as evidence* by the knowledge layer, never
itself holding semantic/interpretive content. This is the single most
consequential architectural decision in this plan — **approved by this
amendment** (§"Decisions requiring explicit maintainer approval");
nothing found during research contradicts it.

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
  user's brief requires, just never tested under reimport.
- Building a second, parallel store (e.g. new SQLite tables, or a new
  YAML shape) would violate the governing instruction to reuse existing
  abstractions and would create exactly the "two competing sources of
  truth" failure mode this whole phase exists to prevent.

### 1.2 Minimal schema extension — one new field, not two

**Revised by this amendment**: the original draft proposed two new
persisted fields, `provenance_dimension` and `reconciliation_state`.
Reviewing both against the amendment's own instruction to persist "only
where it captures irreducible state not safely derivable from existing
fields":

- **`provenance_dimension` is dropped — not persisted at all.** Every
  value it was meant to carry is already fully computable, without
  ambiguity in the overwhelming common case, from fields that already
  exist:
  - `OBSERVED` ⇐ `basis: observed_behaviour`.
  - `DECLARED` ⇐ `basis: proposed_policy`, or the record is itself a
    Decision.
  - `DECIDED` ⇐ a Requirement whose `authorised_by` Decision has
    `status: approved` (the link already exists, §0.1).
  - `DERIVED` ⇐ `basis: inferred`.
  - `HISTORICAL` is not a provenance source at all — it is a *lifecycle*
    condition (`status: superseded`), already fully expressed by the
    existing `status` field. Labelling it as a sibling of `OBSERVED` in
    the original draft conflated "where this came from" with "is this
    still current" — two different questions, both already answerable
    from existing fields.
  - The one genuinely ambiguous input is `basis: directly_stated` (the
    evidence states the fact directly, without inference) — it can mean
    either OBSERVED (the directly-stated evidence is itself an
    Observation-backed `EV-` record) or DECLARED (the directly-stated
    evidence is a doc/design assertion of intent, not a research
    action). This is resolved by walking the Claim's own cited Evidence
    chain at render time: if every cited Evidence traces to at least one
    `OBS-` Observation, label `OBSERVED`; otherwise label `DECLARED`; if
    the chain is genuinely mixed, label `MIXED` rather than guessing —
    **ambiguity always resolves to the more cautious, lower-confidence
    label, never the stronger one.**

  A new pure function, `derive_provenance_label(record, evidence_index)`
  (in the new `knowledge_intermediate.py`, §19 — not in the validation
  script, since it validates nothing, it only renders), computes this at
  render time for the provenance line shown in every rendered block
  (§3.1 point 3) and nowhere else. No schema field, no new validation
  check, no risk of the label and its own source fields silently
  disagreeing (the original draft's planned
  `check_provenance_dimension_consistency` check is dropped along with
  the field it would have validated — a derived value cannot drift from
  what it is derived from).

- **`reconciliation_state` is retained, persisted, as the one genuinely
  new field.** Unlike provenance, this tracks real new state this
  phase's own mechanism introduces — whether a record's content has been
  checked against a pending Markdown edit — which has no existing field
  to derive it from (nothing before this phase tracked "is this record's
  Markdown projection in sync with it"). Added the same way Phase 79
  added `assertion_kind`/`basis`/`evidence_support_state`: additive,
  optional, fail-closed-validated, no migration of existing records
  required. Closed enum, on Claim/Requirement only:
  - `CONFIRMED` — the record's own content currently agrees with
    evidence appropriate to *its own* basis (§1.2.1 below spells out
    what "appropriate" means per basis — this is the amendment's
    tightening of confirmation semantics, point 8).
  - `INTENT_ONLY` — a `DECLARED`-provenance record (derived, not stored)
    with no supporting `OBSERVED` evidence yet.
  - `CONFLICT` — new or edited content contradicts existing evidence, or
    two records about the same thing (one DECLARED, one OBSERVED)
    disagree (§1.2.1).
  - `UNVERIFIED` — a new claim with no evidence checked either way yet —
    **this is the only state a brand-new external candidate addition may
    ever enter at (§3 point 3's own correction)**.
  - `STALE` — the record's own cited evidence has itself moved since
    last reconciled (reuses `check_snapshot_current_divergence`'s own
    hash-comparison logic directly, generalised from "snapshot vs. live"
    to "last-reconciled vs. live").
  - `PRESENTATION_ONLY` — not a record state at all; a *projection-level*
    tag applied to a Markdown edit found to carry no semantic change
    (§4.5's presentation/semantics split) — recorded in the
    reconciliation manifest, never written onto a knowledge record,
    since nothing about the canonical model changed.

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

#### 1.2.1 Confirmation semantics — tightened (amendment point 8)

`CONFIRMED` is never a single undifferentiated "this is true" stamp. It
always means: **evidence of the kind appropriate to this specific
record's own basis currently supports it.**

- An `OBSERVED`-labelled Claim (`basis: observed_behaviour`) is
  `CONFIRMED` only by real, reproducible Observation+Evidence — a human
  Decision alone can never move it there.
- A `DECLARED`-labelled record (intent — a Decision, or a Claim with
  `basis: proposed_policy`) is `CONFIRMED` only in the sense of "this
  intent is still affirmed" — a human Decision is exactly the right and
  sufficient evidence for *this*. **This confirmation of intent must
  never be read, rendered, or mechanically treated as confirmation that
  the implementation currently behaves this way** — that is always a
  separate, `OBSERVED`-labelled Claim, confirmed only by its own
  evidence.
- A `DERIVED`-labelled Claim (`basis: inferred`) is `CONFIRMED` only
  when its own cited Evidence chain (not a human's say-so) supports the
  inference.

**When a DECLARED record and an OBSERVED record about the same subject
disagree** (intent says X, implementation establishes Y): both are kept,
neither is edited to match the other, and reconciliation produces an
explicit `CONFLICT` naming both record ids — reconciliation is never
permitted to collapse the two into one authoritative statement (§7
restates this as a cross-cutting rule; this subsection is its schema-
level grounding).

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

### 1.5 Three-way reconciliation identity — BASE, CURRENT, EDITED

**New section, added by this amendment (point 1).** The render/edit/
reconcile loop (§8) must distinguish three states of a single knowledge
record at the moment reconciliation runs, not just two:

- **BASE** — the canonical record's content hash *at the moment the
  currently-open projection was last rendered*. This is exactly the hash
  already stored in each anchor comment (§4.3) — the amendment makes
  explicit that this hash is BASE, not "the" hash, since there are now
  three to compare.
- **CURRENT** — the canonical record's content hash *right now*, at
  reconciliation time. May equal BASE (nothing changed canonically since
  render) or differ (something else — a Decision, a prior reconciliation
  run, a direct YAML edit — changed the record since).
- **EDITED** — the content hash of the prose currently sitting between
  that same anchor's markers in the open Markdown file. May equal BASE
  (the human/tool never touched this block) or differ (they did).

This is a standard three-way-merge identity (the same shape Git itself
uses for a merge base), applied to one knowledge record's own rendered
block instead of a whole file. §8 defines the four resulting cases and
their handling; §16's new concurrent-edit test is this section's own
acceptance proof.

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
  records and (where one exists) its `snapshots/` directory. A sibling
  `reconciliation/` directory (new, §8/§11) holds that same slug's
  durable, auditable reconciliation manifests. This keeps the new,
  editable, human/tool-facing Markdown clearly separated from the
  canonical YAML records in the same place a reader already knows to
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
with **stable per-record anchors** (§4.3) carrying BASE identity (§1.5)
so a targeted edit can be mapped back to the exact record it changed and
checked for concurrent drift.

### 2.3 Regeneration without destroying accepted human contributions or canonical semantics

The projection/reconciliation loop (§8) guarantees, now covering both
the concurrency case and the presentation/semantics split this
amendment adds:

- Re-rendering a record whose own canonical content has not changed
  since last reconciliation, and whose block was not edited, reproduces
  byte-identical prose for that block (no formatting churn).
- A record whose canonical content *has* changed since the projection
  was last rendered (CURRENT ≠ BASE, EDITED = BASE) is refreshed
  automatically — that one block is re-rendered from the new canonical
  state; every other block's own prose is untouched.
- A block a human edited for wording only (EDITED ≠ BASE, CURRENT = BASE,
  no semantic change detected) keeps the human's own wording via the
  presentation cache (§4.5) — **the canonical record itself is never
  touched by this case**, so "no erased prose improvements" and "no
  false semantic reconciliation event" both hold simultaneously, which
  the original draft's design (writing wording straight into the
  record's `statement` field) did not guarantee.
- A block edited with new semantic content (EDITED ≠ BASE, CURRENT =
  BASE) becomes a candidate reconciliation, landing the affected record
  at `INTENT_ONLY`/`CONFLICT`/`UNVERIFIED` — never silently applied, and
  never applied anywhere except through the `apply` step (§11).
- A block both canonically changed and locally edited (EDITED ≠ BASE,
  CURRENT ≠ BASE) is a **concurrent-change conflict** (§1.5/§8): neither
  side is overwritten; the conflict is surfaced in the manifest and in
  `knowledge status`, and the block is left exactly as the human left it
  until someone resolves it.

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
   directly, never `planning/knowledge/*/snapshots/*.toml` (frozen,
   historical), never `planning/knowledge/*/reconciliation/*.toml` (the
   new manifest trail, §8/§11 — these are written by the tooling and
   read by a reviewer, not hand-edited), and never the hidden
   `planning/knowledge/*/intermediate/.presentation-cache.toml` sidecar
   (§4.5).
3. **Machine-derived vs. maintainer-authored** — every rendered block
   carries a provenance line, computed at render time (§1.2's
   `derive_provenance_label`, not a stored field) so a reader can tell
   "this is OBSERVED fact" from "this is DECLARED intent" from "this is
   historical" without reading YAML.
4. **How to add new material** — write new prose strictly inside the
   file's own bounded `Candidate additions` region (§4.4's marker pair,
   present in every rendered file). **This never creates an Observation.**
   It proposes exactly one new candidate Claim (or Requirement) per
   block of new prose, entering at `UNVERIFIED` — a real Observation can
   only come from someone actually performing the reproducible research
   action it represents (§3's own correction, point 3 below; §14).
5. **What not to modify directly** — the YAML records, the snapshots,
   the reconciliation manifests, the presentation cache, and any block's
   own anchor comment (§4.3) or candidate-region marker comment (§4.4) —
   edit the prose around them, never the markers themselves.
6. **How identity/provenance is preserved** — the anchor mechanism
   (§4.3) and its BASE/CURRENT/EDITED concurrency identity (§1.5),
   explained at a level a non-technical reader/tool can follow without
   understanding the underlying YAML.
7. **How changes are submitted** — an ordinary Git commit/PR, exactly
   like any other file change; mechanical detection runs as a checked-in
   step (`knowledge select-candidates`, §11), not a separate submission
   channel.
8. **What happens when Markdown disagrees with source evidence** — §1.2's
   `CONFLICT` state, surfaced explicitly in the reconciliation manifest
   and the next re-rendered projection (never silently resolved — §14).
9. **How conflicts/unverified claims are surfaced** — a dedicated
   "Open conflicts" section in every projected document (§4), populated
   from any record at `CONFLICT`/`UNVERIFIED` touching that document's own
   scope, plus any anchor currently sitting at an unresolved
   concurrent-change conflict (§1.5).
10. **Editing ≠ immediate canonicity** — stated as the single most
    important sentence in the guide, verbatim close to: *"Editing this
    file does not make your statement true in CodeCompass's own records
    until it has been reviewed and checked against evidence. A brand-new
    addition starts out UNVERIFIED — real, visible, and not yet
    confirmed — because writing a sentence here is not the same thing as
    CodeCompass having actually observed it."*
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
  (`open_questions` field content) plus any unresolved concurrent-change
  conflict (§1.5) — this is the one file every reconciliation run is
  guaranteed to touch, so it is kept separate from the calmer reference
  material above.

A phase-scoped slug may also render `tests-and-acceptance.md` (§5) when
the phase's own records include Requirement-kind entries citing test
expectations — omitted when there's nothing to put in it, never an empty
placeholder file. **Every file in this set always ends with one
`Candidate additions` section** (§4.4), present even when currently
empty, so a human/tool always has an obvious, bounded place to propose
something new without needing to know the marker syntax in advance (the
rendered instructions above the markers explain it inline).

### 4.2 Rendering algorithm

Deterministic, reusing `VendorDigest`'s own established rendering
pattern: for each target file, select the records matching that file's
own filter (by `assertion_kind`, by `reconciliation_state`, by slug).
For each selected record: compute its derived provenance label (§1.2),
check the presentation cache (§4.5) for an accepted wording still valid
against the record's current semantic content, and render one Markdown
block (heading + statement/presentation-cache wording + citations +
status + provenance line) wrapped in its anchor comment (§4.3) carrying
the record's current content hash as the new BASE. Blocks are sorted by
`id` for a stable diff-friendly order. No AI call in the rendering step
itself — this is mechanical formatting of already-existing record
content plus a cache lookup, the same posture `VendorDigest` rendering
already has.

### 4.3 Stable anchors

Each rendered block opens with an HTML comment carrying the record's own
`id` and the BASE content-hash of what was rendered (§1.5):

```markdown
<!-- codecompass-knowledge: CL-ARCH-014 base-sha256:3f9a1c... -->
### The sync pipeline is idempotent under repeated invocation

[rendered statement or cached presentation wording, citations, status line]

<!-- /codecompass-knowledge -->
```

On `select-candidates` (§8/§11), the engine parses every
`codecompass-knowledge` comment pair, recomputes CURRENT (the record's
live content hash) and EDITED (the hash of the prose currently between
the markers), and classifies the block into one of §8's four cases.
A comment pair itself being moved, or new, unmarked prose appearing
outside any anchor or candidate-region marker pair (§4.4), is never
treated as a semantic change to an existing record — it is either
ignored (ordinary narrative prose a human added around the blocks) or,
if it sits inside the candidate-region markers, handled by §4.4.

### 4.4 Candidate-addition boundaries (new, amendment point 4)

Arbitrary unanchored Markdown prose anywhere in an intermediate document
is never interpreted as candidate canonical knowledge. The only place
new knowledge can be proposed is the one bounded region every rendered
file carries:

```markdown
## Candidate additions

Add new domain knowledge, edge cases, invariants, or open questions
below, strictly between the two marker comments. Content outside this
region — including this paragraph — is never read as knowledge; it is
just narrative framing CodeCompass leaves untouched.

<!-- codecompass-candidates:start -->

<!-- codecompass-candidates:end -->
```

`select-candidates` reads only the text strictly between
`codecompass-candidates:start` and `codecompass-candidates:end`, splits
it into blocks on blank-line/heading boundaries, and proposes exactly
one new candidate **Claim or Requirement** per block — **never a
Decision**: a Decision stays a human-alone-authored record via its
existing path (§0.1); the candidate-region mechanism cannot manufacture
one, closing a gap the original draft left open. Every proposal enters
the manifest at `UNVERIFIED` (§1.2), never auto-classified further.
Moving headings, reformatting, or adding commentary anywhere else in the
file — including directly above or below the candidate region, outside
the markers — has no effect on canonical knowledge: the parser only ever
looks inside recognised anchor pairs (§4.3) and this one candidate-region
pair. The format stays ordinary, readable Markdown; no opaque database
manipulation, no required special syntax beyond the two HTML comments
every file already ships with pre-rendered.

### 4.5 Presentation wording vs. canonical semantics (new, amendment point 2)

**Canonical knowledge owns semantic meaning. Projections own
presentation.** A record's own `statement` field (and its other semantic
fields — `basis`, `evidence_support_state`, citations) is the single
source of *meaning*; it is written only by reconciliation's `apply` step
(§11), never by a presentation-only edit.

Wording, however, may legitimately differ across every surface that
shows the same fact — the intermediate doc, a future MCP projection, a
context packet, and (trivially, since they are never rendered from
records in the first place) README/CONTRIBUTING/guides. For the one
surface that *is* literally re-rendered from records — `intermediate/*.md`
— a small sidecar, `planning/knowledge/<slug>/intermediate/.presentation-cache.toml`,
keyed by record `id`, holds:

```toml
["CL-ARCH-014"]
accepted_for_semantic_hash = "sha256:3f9a1c..."   # the record's content hash this wording was accepted against
wording = "The sync pipeline can be invoked any number of times without changing its own result."
```

Rendering (§4.2) checks this cache before falling back to the record's
own deterministically-formatted `statement`: if an entry exists **and**
its `accepted_for_semantic_hash` still equals the record's current
semantic content hash, the cached wording is rendered; otherwise the
cache entry is stale (the underlying meaning moved) and is dropped,
falling back to fresh deterministic prose from the record's own current
fields. A reconciliation outcome classified `PRESENTATION_ONLY` (§8 case
2, no semantic delta detected) is exactly what writes a *new* cache
entry — it never touches the YAML record.

Context packets (§13) are themselves a scoped re-rendering of the same
`intermediate/*.md` content (§5.2), so they inherit whatever wording the
cache already holds with no separate cache of their own. README/
CONTRIBUTING/guides need no cache at all, since — as §9.3 already
establishes — they are hand-authored prose that cites/grounds against
canonical knowledge without ever being regenerated from it; "different
legitimate presentations of the same fact" is the architecture's default
state for those surfaces, not a special case this mechanism has to
create.

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
today. **What's new**: reconciliation's `apply` step (§11) checks, for
every Claim reaching `CONFIRMED`, whether its own `assertion_kind`/content
makes it relevant beyond the originating phase — a project-wide
invariant discovered mid-phase gets a `depends_on`/cross-reference into
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
   files using ordinary repository workflows, writing new material only
   inside each file's candidate region (§4.4) — no CodeCompass invocation
   required to *read* or *propose* a change.
4. Changes are submitted as an ordinary Git commit/PR (§3.1 point 7).
5. `codecompass knowledge select-candidates <slug>` runs — either as a
   CI check, a pre-merge step, or an explicit invocation — mechanically
   detecting every anchor's three-way state (§1.5) and every new
   candidate-region block (§4.4), writing a durable manifest
   (§8/§11). No semantic judgment happens in this step.
6. A human or an agent dispatch (reusing the existing `docs-maintainer`/
   `domain-skeptic` comparison dispatch pattern, §0.3) reviews the
   manifest, gathers or checks evidence, and annotates each pending item
   with its proposed classification (§7) — producing a filled-in
   **reconciliation proposal**.
7. `codecompass knowledge apply <proposal>` validates the proposal
   mechanically (same fail-closed checks as `check_knowledge_base.py`,
   plus a fresh concurrency check against CURRENT at apply time) and —
   only here — writes the canonical records. Conflicts stay explicit,
   never silently resolved (§14).
8. `codecompass knowledge render` refreshes `intermediate/*.md` from the
   now-current records, preserving presentation wording where still
   valid (§4.5).
9. Coding/planning agents consume the reconciled knowledge directly
   (§13) — no separate development-only store.
10. After implementation, changed source/tests trigger revalidation
    (§12) of whichever Claims cited the now-changed evidence.
11. README/CONTRIBUTING/architecture docs are refreshed where the
    reconciled knowledge actually bears on their own content (§9/§12),
    not wholesale.

**This workflow is explicitly validated to remain useful when the code
is written manually** (§16's dogfood scenarios include a pure
knowledge-refinement cycle with no implementation step at all) — nothing
in steps 1-8 requires an agent to write the implementation.

---

## 7. Provenance and reconciliation — the unified state model

§1.2 defines the one persisted enum (`reconciliation_state`) and the
derived, render-time-only provenance classification that replaces the
original draft's persisted `provenance_dimension` field. This section
states the cross-cutting rules the brief asks for explicitly, restated
against the corrected schema:

- **Observed reality and declared intent are separate dimensions,
  never merged into one field, and never merged into one record.** A
  record's derived provenance label (what kind of grounding it has) is
  independent of its persisted `reconciliation_state` (whether that
  grounding currently checks out) — a `DECLARED`-labelled record can be
  `CONFIRMED` (§1.2.1: a maintainer's stated intent still affirmed) or
  `INTENT_ONLY` (asserted, not yet checked); an `OBSERVED`-labelled
  record can be `CONFIRMED` or `STALE` (the behaviour it observed has
  since changed) but is never `INTENT_ONLY` — observation doesn't have
  an "intent-only" reading.
- **A human edit to an intermediate document may change `DECLARED`
  content; it may never directly overwrite `OBSERVED` content.** If an
  edited block's underlying record is `OBSERVED`-labelled
  (`basis: observed_behaviour`), the edit is never applied as a direct
  rewrite of that record. It is treated as a *new, competing* candidate
  Claim requiring fresh observation to confirm — this is mechanically
  enforced at the `apply` step (§11), which refuses to apply a
  semantic-content change directly onto an `OBSERVED`-labelled record's
  own `basis`/`statement` fields; it always creates a new Claim instead.
- **Repository evidence may update `OBSERVED` content; it may never
  silently overwrite `DECLARED` intent.** The symmetric case: if a code
  change invalidates an `OBSERVED` Claim, revalidation (§12) marks that
  Claim `STALE`/re-derives it, but a *separate*, `DECLARED`-labelled
  Claim about intended behaviour is never auto-edited by this process —
  a genuine intent-vs-reality conflict surfaces as `CONFLICT`
  (§1.2.1's worked example), not a silent overwrite in either direction.
- **The four confirmation categories stay distinct** (§1.2.1, amendment
  point 3/8): accepted intent, verified behaviour, evidence-backed
  derivation, and unsupported external assertion are never collapsed
  into each other by reconciliation — see §14's table for exactly how
  each enters and how each is strengthened.

---

## 8. Reconciliation mechanics — detection, review, and application as separate stages

**Substantially revised by this amendment (points 1 and 6).** The
original draft's single "reconciliation" step mixed mechanical diff
detection, semantic judgment, evidence-gathering, and canonical mutation
into one conceptual box. This amendment separates them into four
distinct stages, mirroring `enrich select-candidates`/`enrich apply`'s
own already-proven split (§0.2):

```
canonical records (planning/knowledge/*/*.yaml)
        ↓  render (§4.2, deterministic, no AI call)
intermediate/*.md  (per-record anchors carry BASE, §1.5/§4.3;
                     one candidate region per file, §4.4)
        ↓  human/tool edit, ordinary Git workflow
edited intermediate/*.md
        ↓  STAGE 1: DETECT — `codecompass knowledge select-candidates <slug>`
        ↓  mechanical only, read-only, no AI call:
        ↓   - for every anchor, compute BASE / CURRENT / EDITED (§1.5)
        ↓     and classify into one of the four cases below
        ↓   - for every candidate-region block (§4.4), emit one new
        ↓     UNVERIFIED candidate Claim/Requirement proposal
reconciliation manifest (durable, committed, §11 — TOML, reusing the
  frozen-snapshot format's own shape)
        ↓  STAGE 2: REVIEW — human or an agent dispatch (reusing the
        ↓  existing docs-maintainer/domain-skeptic comparison-dispatch
        ↓  pattern, §0.3) reads the manifest, gathers/checks evidence,
        ↓  and annotates each item with its proposed classification —
        ↓  this is the ONLY stage where semantic judgment happens
reconciliation proposal (the same manifest file, now annotated —
  not yet authoritative; no record has been touched)
        ↓  STAGE 3: APPLY — `codecompass knowledge apply <proposal>`
        ↓  re-validates mechanically (same fail-closed checks as
        ↓  check_knowledge_base.py, plus a fresh BASE-vs-CURRENT
        ↓  concurrency re-check, since time may have passed since
        ↓  detection) — this is the ONLY stage allowed to write
        ↓  planning/knowledge/*/*.yaml
canonical record(s) updated, each landing at CONFIRMED/INTENT_ONLY/
CONFLICT/UNVERIFIED per §1.2/§7 — never written by any other stage
        ↓  STAGE 4: RE-RENDER — `codecompass knowledge render <slug>`
        ↓  (§4.2) — unaffected anchors reproduce byte-identical prose;
        ↓  only changed anchors' own blocks are rewritten; presentation
        ↓  wording preserved where still valid (§4.5)
refreshed intermediate/*.md
```

**The four three-way cases (§1.5), handled at Stage 1 (DETECT):**

| BASE vs CURRENT | BASE vs EDITED | Case | Outcome |
|---|---|---|---|
| unchanged | unchanged | Nothing happened | **No-op.** No manifest entry. |
| unchanged | edited | Human/tool edited the projection, canonical record untouched | **Candidate reconciliation** — manifest entry, proceeds to Stage 2. |
| changed | unchanged | Canonical record moved (e.g. a prior `apply`, a direct YAML edit), projection untouched | **Refresh** — no semantic judgment needed; Stage 4 re-renders that block directly from the new canonical state. |
| changed | edited | Both moved independently since this projection was rendered | **Concurrent-change conflict** (§1.5). **Neither side is overwritten.** The manifest records BASE, CURRENT, and EDITED content side by side; `apply` refuses to act on this entry until a human resolves it (by re-rendering fresh and manually reapplying their intent, or by explicitly picking a side) — the Markdown file itself is left completely untouched by detection, so the human's own wording is never silently discarded, and `knowledge status` surfaces it as an open item. |

**No formatting churn**: re-rendering a record whose content and
presentation-cache entry are both unchanged since it was last rendered
produces byte-identical output for that block. **No erased prose
improvements, and no conflation of presentation with canonical
semantics**: a wording-only edit (EDITED ≠ BASE, CURRENT = BASE, no
semantic delta found at Stage 2) writes only to the presentation cache
(§4.5) — the canonical YAML record is never touched by this case, unlike
the original draft's design. **Users never manipulate opaque database
internals**: every edit happens in ordinary Markdown; the YAML records,
manifests, and cache are implementation details the guide (§3)
explicitly tells a reader not to touch directly, but nothing about the
*editing* workflow requires understanding them.

**An LLM/human reconciliation judgment cannot bypass mechanical
validation**: Stage 2's annotation is advisory until Stage 3 re-validates
it from scratch — `apply` never trusts a proposal's own self-reported
correctness, the same mechanical-trust-boundary discipline `enrich
apply` already enforces for agent-authored enrichment (§0.2).

---

## 9. Project documentation integration

### 9.1 Reuse existing doc-artifact identity

Per §0.2, `README.md`/`CONTRIBUTING.md`/`architecture/**`/`docs/**`/
`decisions/**` are *already* (or, for `CONTRIBUTING.md`, become by this
amendment, §0.2) `doc_artifacts` rows with stable path identity and
content hashes (`doc_chunks`). This phase does not invent a parallel
identity — grounding (§9.2) is keyed on the same `doc_artifacts.path`/
content-hash CodeCompass already tracks.

### 9.2 Explicit grounding, not rediscovery every time (amendment point 5)

**Revised by this amendment.** The original draft relied on an AI
rediscovering which Claims a documentation region relates to at every
single check. This amendment adds a durable, explicit relationship for
the regions a maintainer chooses to ground, falling back to the
existing mechanical mention-detection only as a weaker signal:

- A documentation region may carry an explicit grounding marker:

  ```markdown
  <!-- codecompass-grounded-by: CL-ARCH-014, REQ-ARCH-002 -->
  ### How sync handles idempotency
  ...ordinary, hand-authored prose...
  <!-- /codecompass-grounded-by -->
  ```

  This is **optional, per-region, never required for every sentence** —
  exactly the brief's own explicit constraint. A maintainer adds one
  where they want a specific factual claim durably tied to the record(s)
  that ground it.
- **Canonical knowledge changes → affected doc region identified**: a
  small, mechanical reverse index (built by scanning `doc_chunks` content
  for `codecompass-grounded-by:` markers citing a given record id — a
  text scan, no new graph table) tells reconciliation exactly which
  documentation regions cite a record whose content just changed.
- **Factual doc changes → relevant canonical knowledge identified**: if
  the changed region carries a grounding marker, those exact ids are the
  answer (strong case, no guessing). If it doesn't, the existing
  `doc_relations_edges` mention-detection (already real, §0.2) is used as
  a weaker signal — flagged for Stage 2 review/triage, never
  auto-triggering `apply` on its own.
- **Presentation-only doc changes → no semantic mutation**, unaffected
  by whether a grounding marker is present (§9.4 below still applies
  unchanged).

This mechanism directly reuses `doc_artifacts`/`doc_chunks`/
`doc_relations_edges` and stable paths, per the brief's own explicit
preference, rather than inventing a new relationship store.

### 9.3 Detecting presentation vs. semantic edits

A documentation file's own content-hash changing is already mechanical
(every `sync` recomputes it). Whether the change is *semantic*
(asserts/changes a project-fact a grounded Claim should reconcile) or
*presentational* (wording, formatting, reorganisation with no factual
change) is **not mechanically decidable from the hash alone** — this
requires the same kind of fresh, read-only comparison dispatch already
established for `docs-maintainer`/`domain-skeptic` (§0.3), given the
changed region's own diff and whichever Claims ground it (§9.2, strong
case) or merely mention it (weak case). This keeps the detection step
bounded and reusing an existing dispatch pattern, rather than building
new NLP/classification machinery — explicitly named as a judgment call
requiring real evidence to tune (§16 includes this as a dogfood
scenario), not assumed solved on day one.

### 9.4 The flow

```
canonical project knowledge (Claims/Requirements grounding a doc region
  via an explicit codecompass-grounded-by marker, or merely mentioned
  via doc_relations_edges)
        ↓
documentation knowledge/context view (a new intermediate/*.md scoped to
  "project documentation," reusing §4's rendering, for reference only —
  README/CONTRIBUTING themselves are never generated from it)
        ↓
README / CONTRIBUTING / architecture / guides / reference
  (human/external-tool-authored prose, NOT auto-generated wholesale —
  per the brief's own explicit "do not require every sentence to be
  generated")
        ↑  refinement (ordinary edits)
        ↓
presentation edit → logged, no reconciliation triggered, no Claim touched
semantic edit to a grounded region → candidate Claim change → enters the
  same Stage 1→4 pipeline (§8) as an intermediate-document edit
semantic edit to an ungrounded region → flagged via weak mention-
  detection for Stage 2 triage, same pipeline, lower confidence
```

### 9.5 Worked examples, matching the brief's own three

- Rewriting a README introduction for clarity: hash changes, comparison
  dispatch finds no Claim-relevant factual delta → `PRESENTATION_ONLY`,
  logged, nothing reconciled.
- Changing a supported-behaviour statement in a grounded region:
  comparison dispatch finds the new wording asserts something the
  grounding Claim doesn't currently say → a candidate Claim edit, enters
  the Stage 1→4 pipeline exactly like an `intermediate/` document
  change.
- Adding an architectural invariant to `CONTRIBUTING.md` (now in scope,
  §0.2): either the invariant already exists as a Claim (the addition is
  treated as adding a `codecompass-grounded-by` citation, not a new
  claim) or it doesn't (a new candidate Claim, `assertion_kind: invariant`,
  entering the pipeline at `UNVERIFIED`).

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
- **`CONTRIBUTING.md`** — now brought fully into scope by this amendment
  (§0.2): gains a new section, "Knowledge-affecting changes," explaining
  when a code change also changes/reveals project knowledge (a new
  invariant, a changed behaviour), the accompanying commit should either
  cite the relevant existing Claim (optionally via a
  `codecompass-grounded-by` marker, §9.2) or add a new one via the
  intermediate-document candidate-region workflow (§4.4) — mirroring
  `CLAUDE.md` §1's own existing "plan before implementing" discipline,
  extended to knowledge rather than code. This is process guidance, not
  a machine-manifest — written in the same register as the rest of
  `CONTRIBUTING.md`'s existing prose. Its own factual sections may now
  also carry grounding markers where a maintainer chooses.
- Neither file becomes a second authority: both explicitly state that a
  factual claim here, if it ever disagrees with the reconciled
  knowledge, is itself a `CONFLICT` to be reconciled, not a correction
  to apply by hand to the knowledge layer — closing the loop the brief's
  own point 10 asks for ("avoid becoming an independent authority that
  silently diverges from the knowledge DB"). `CLAUDE.md` stays outside
  this entire mechanism, self-governing under its own §0.

---

## 11. CLI / reconciliation surface

**Revised by this amendment (point 6)**, directly mirroring the existing
`enrich select-candidates`/`enrich apply` two-stage split (§0.2) rather
than one ambiguous `reconcile` verb:

- **`codecompass knowledge render [<slug>]`** — Stage 4 (and the initial
  projection). Runs §4.2's rendering for one slug or all slugs with an
  `intermediate/` directory. Pure, deterministic, no AI call, safe to
  run any time (matches `VendorDigest` rendering's own existing
  idempotent-refresh posture).
- **`codecompass knowledge select-candidates <slug> [--dry-run]`** —
  Stage 1 (§8). Mechanical only: computes every anchor's BASE/CURRENT/
  EDITED classification (§1.5) and every candidate-region block (§4.4),
  and writes a reconciliation manifest to
  `planning/knowledge/<slug>/reconciliation/<timestamp>.toml` (reusing
  the frozen-snapshot TOML shape, §0.1). Never invokes an AI model,
  never writes a canonical record. `--dry-run` prints the manifest
  without writing it to disk.
- **`codecompass knowledge apply <manifest-path> [--strict]`** — Stage 3
  (§8). The **only** command that writes `planning/knowledge/*/*.yaml`.
  Requires the manifest's items to already be annotated (Stage 2's own
  output — produced by a human or an agent dispatch, never by this
  command itself); re-validates every annotation mechanically (same
  fail-closed checks as `check_knowledge_base.py`), re-checks BASE
  against CURRENT at apply time (catching a concurrency race that opened
  up between detection and apply), and refuses — fail-closed — to touch
  any item still marked as an unresolved concurrent-change conflict.
  Writes via the same validated file-write path the existing
  `knowledge-curator`/direct-YAML-authoring paths already use; tags
  externally-sourced content `source: "external:<tool-name>"` or
  `source: "external:unknown"` (never a guess) alongside the existing
  `agent:<name>` convention (§14) where an agent performed Stage 2.
- **`codecompass knowledge status [<slug>]`** — reports every record at
  `CONFLICT`/`UNVERIFIED`/`STALE`, plus every unresolved concurrent-change
  conflict from the latest manifest, reusing `check`'s own existing
  reporting conventions (table/JSON, `--strict` exit-code semantics).

New validation addition to `scripts/check_knowledge_base.py` (same file,
same fail-closed discipline, not a new script): `check_anchor_integrity`
(every `intermediate/*.md` file's own anchors resolve to a real record
with matching id/kind — the same "identity, not merely a hash match"
discipline Phase 80 hardened for snapshots, applied here to live
projections). **Dropped by this amendment**: the originally-planned
`check_provenance_dimension_consistency` — there is no longer a
persisted `provenance_dimension` field for it to validate (§1.2); its
replacement, `derive_provenance_label`, is a pure function covered by an
ordinary unit test (§16.1), not a knowledge-base validator, since it
cannot drift from the fields it derives.

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
raised — only via `knowledge apply` (§8/§11), same as any other change
       ↓
affected intermediate/*.md re-rendered (§4.2, targeted — only the
file(s) containing the affected record's own anchor)
       ↓
affected project docs identified (via explicit codecompass-grounded-by
markers, §9.2, falling back to doc_relations_edges mention-detection)
       ↓
targeted documentation update (§9.3's semantic-diff dispatch, scoped to
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
self-contained Markdown — no new export format needed). As noted in
§4.5, a context packet inherits whichever presentation wording the
underlying `intermediate/*.md` files already carry, with no separate
cache of its own. The "open conflicts" section (§4.1) is always
included, so a consuming agent sees unresolved contradictions — including
any unresolved concurrent-change conflict (§1.5) — rather than a
falsely-confident single answer.

---

## 14. Safe collaboration model

### 14.1 Ownership semantics

Reusing `decisions/0051`/`0054`'s own established provenance-tagging
convention (`model`/`performed_by`-style fields, `agent:<name>`
namespacing) rather than inventing a new identity system:

| Content class | Who may author it | Enters as |
|---|---|---|
| Machine-observed evidence | Mechanical detection only (existing `sync` pipeline) | `OBSERVED`-labelled, directly |
| Machine-derived knowledge | A derivation dispatch (`context-researcher`-style), citing real evidence | `DERIVED`-labelled, `UNVERIFIED` until checked |
| Maintainer-declared intent | A human, via a Decision or a direct intermediate-document edit | `DECLARED`-labelled, `INTENT_ONLY` until evidence-checked |
| Accepted decisions | A human only — unchanged from today's existing rule (Decision is "the only kind a human alone authors") | `DECIDED`-labelled |
| Externally proposed knowledge (candidate-region addition or a Markdown edit) | Any external tool/person | always a **candidate Claim/Requirement** — `UNVERIFIED`/`INTENT_ONLY`/`CONFLICT`, **never an Observation, never `CONFIRMED`, on entry** (§1.2/§3 point 3 below) |
| Presentation prose | Anyone, anywhere (README wording, an intermediate doc's own accepted wording) | not a knowledge record at all — `PRESENTATION_ONLY`, cached or logged only (§4.5) |

### 14.2 External additions are candidate claims, never fabricated observations (amendment point 3)

**Corrected by this amendment.** An Observation record (`OBS-`) means a
reproducible observation/research action *actually occurred* — someone
or something ran a check, read a source, executed a test, and recorded
what happened. An external user or tool writing the sentence "Behaviour
X exists" inside a candidate region has not, by writing that sentence,
performed that observation. The original draft's "reconciliation turns
it into a new Observation+Claim pair" language is wrong and is replaced
by:

```
external addition (candidate region, §4.4)
      ↓
candidate Claim / Requirement proposal (never a Decision, §4.4)
      ↓
UNVERIFIED  (or, if the proposal itself reads as a statement of desired
             future state rather than current fact, INTENT_ONLY once a
             human Decision affirms the intent — still never OBSERVED)
      ↓
independent research or evidence acquisition — a real Observation,
performed by a human or by context-researcher-style primary research,
reusing the existing Observation/Evidence machinery (§0.1) exactly as
it works today for any other Claim
      ↓
Evidence, built from that Observation
      ↓
Claim support / contradiction / verification, following the existing,
unmodified Claim status lifecycle — reaching CONFIRMED only through
this path, never by the external text alone
```

A maintainer may, via a Decision, author or ratify project intent — but
**a human's approval of an external candidate never fabricates OBSERVED
behaviour**. Approving "this should be invariant X" is a Decision about
intent (`DECLARED`, confirmable as intent per §1.2.1); it is not, and
cannot become, an Observation that invariant X actually holds in the
implementation. The four categories stay explicitly distinct throughout
this phase's own design (§1.2.1, §7):

| Category | How it is produced | Confirmable by |
|---|---|---|
| Accepted intent | A human Decision (approving a Claim/Requirement's stated intent) | Further human Decision only — never promotes to OBSERVED |
| Verified behaviour | Real Observation + Evidence, `basis: observed_behaviour` | Fresh Observation/Evidence only |
| Evidence-backed derivation | `basis: inferred`, citing real Evidence | Its own cited Evidence chain holding up |
| Unsupported external assertion | A candidate-region addition or an unreviewed Markdown edit, no Evidence cited | Nothing, until someone performs the Observation it claims — stays `UNVERIFIED` indefinitely otherwise, exactly as intended |

### 14.3 Retained per-record, and the no-silent-resolution rule

Retained per-record: who/what introduced a change (reusing the existing
`derived_by`/`decided_by`/`performed_by` fields, extended with the
`agent:<name>`/`external:<tool-name>`/`external:unknown` convention,
§11, for a Markdown-originated edit — and never a guess at which), the
evidence used during reconciliation (the Evidence record itself),
previous states (Git history of the YAML file, and now also the
committed reconciliation manifests, §8/§11 — a durable, auditable trail
that did not exist in the original draft), and unresolved contradictions
(`CONFLICT`-state records, and unresolved concurrent-change conflicts,
§1.5, never silently dropped). **No contradiction is resolved merely to
keep documentation internally consistent** — a `CONFLICT` stays a
`CONFLICT`, rendered explicitly in every affected projection, until a
real Decision or new Evidence resolves it; reconciliation's `apply` step
is mechanically forbidden from picking a side on its own (§1.2.1, §7).

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
  they contain, per §4.1, and every file carries its own inline
  candidate-region instructions, §4.4) — no separate manifest file
  needed inside each slug beyond what §3's guide already establishes
  project-wide.

### 15.1 `codecompass-template` implications — decided by this amendment

A new, concise addition — not a copy of CodeCompass's own full
`planning/knowledge/` apparatus (the template's own established
"lightweight adoption, avoid importing CodeCompass's governance
ceremony" convention from Phase 80 applies unchanged here). **Decided**:
a new, *separate* `optional-intermediate-knowledge/` directory, sibling
to the existing `optional-clean-room-workflow/` — not merged into it.
Clean-room documentation reconstruction is one *consumer* of the
broader knowledge layer (it can freeze a snapshot of the same canonical
records this phase's intermediate documents also project from), not the
definition of the knowledge layer itself; keeping them separate avoids
implying every adopter of one needs the other. Contains: a short
`README.md` explaining what this is and when to adopt it (mirroring
`optional-clean-room-workflow/README.md`'s own established tone and
length), one worked example (reusing `worked-example.md`'s own existing
pattern), and the minimal file skeleton (§4.1's four files, empty/
templated, each pre-populated with its own candidate-region markers,
§4.4).

---

## 16. Testing and dogfood validation

### 16.1 Deterministic unit/integration tests (new `tests/test_knowledge_intermediate.py`, following this project's own existing test-file-per-module convention)

**Expanded by this amendment (point 10)** to cover the three-way
concurrency model, the presentation/semantics split, the corrected
candidate-addition semantics, explicit grounding, and the
detect/review/apply separation, in addition to the original draft's
core properties:

- **No formatting churn**: render → no-op reimport → re-render produces
  byte-identical output.
- **Presentation independence** (replaces the original draft's
  "PRESENTATION_ONLY-equivalent Claim-statement update"): render → edit
  one anchor's prose (same semantic content, different wording) →
  `select-candidates` classifies it `PRESENTATION_ONLY` → `apply` writes
  *only* the presentation cache, confirmed via a direct read of the
  record's own YAML file showing zero byte change → re-render preserves
  the edited wording, sourced from the cache → a *second* projection of
  the same record (e.g. a differently-worded README grounding, §9) is
  independently confirmed to keep its own, different wording
  unaffected — proving one canonical fact legitimately supports multiple
  live presentations at once.
- **External unsupported assertion creates no fabricated observation**
  (amendment point 3): add a candidate-region block asserting a new
  behaviour → `select-candidates` → `apply` → confirm the result is
  exactly one new Claim at `UNVERIFIED`, `basis` reflecting an
  unsupported external assertion, **and assert directly, by querying the
  Observation/Evidence stores, that zero new `OBS-`/`EV-` records were
  created** — proving the fabrication the original draft risked cannot
  happen even as an implementation accident.
- **Candidate-region boundary**: (a) add explanatory prose *outside* the
  candidate-region markers in an otherwise-untouched file → run
  `select-candidates` → assert the manifest is empty (no record
  created); (b) add a statement *inside* the markers → run
  `select-candidates` → assert exactly one candidate entry appears in
  the manifest. Both run in the same test to make the boundary's own
  sharp edge explicit.
- **Concurrent-change conflict** (amendment point 1, §1.5): render
  version A of a record → independently mutate the canonical YAML record
  to version B (simulating a second actor) → separately edit the
  rendered projection's own anchor text → run `select-candidates` →
  assert the manifest reports a concurrent-change conflict for that
  anchor, `apply` refuses to act on it, and **both** the canonical
  record (still at version B, untouched) and the projection file (still
  showing the human's own edit, untouched) are confirmed unchanged after
  the run.
- **Explicit documentation grounding** (amendment point 5): (a) a Claim
  with a `codecompass-grounded-by` reference from a README region
  changes → assert the affected README region is identified
  deterministically from the grounding marker alone, with no dispatch
  call needed; (b) the grounded README region's own text changes
  factually → assert the grounding marker's cited Claim(s) are
  identified and a manifest entry is produced, without relying on
  `doc_relations_edges` mention-detection for this case.
- **Three-stage application safety** (amendment point 6): a semantic
  edit is detected (Stage 1) → a proposal is generated and annotated
  (Stage 2, simulated) → assert the canonical record is **still
  unchanged** at this point (proposal ≠ authoritative) → only after
  `apply` (Stage 3) runs does the canonical record change — asserted via
  a direct YAML read before and after each stage.
- Stable identity under reorganisation: render → canonical record's own
  file is reorganised (moved to a different filename, same `id:`) →
  re-render still resolves the existing anchor correctly.
- `check_anchor_integrity`: disposable-git-fixture reproduction of a
  stale anchor hash and an id/kind mismatch *before* the fix, matching
  this project's own established "reproduce before fixing" discipline
  (Phases 79/80's own precedent) — required by `CLAUDE.md` §1's own
  minimal-content-edge-case and depth-vs-scope rules for any new
  fail-closed mechanism.
- `derive_provenance_label`: an ordinary unit test (not a knowledge-base
  validator, since nothing is persisted to validate, §1.2) covering each
  of the five labels plus the `directly_stated`/mixed-evidence-chain
  ambiguous case, confirming it resolves to the more cautious label.

### 16.2 Realistic dogfood scenarios (reusing `reference-project-protocol.md`'s own conventions, §0.4) — the brief's own eight scenarios, each mapped to a concrete mechanism above

1. **External knowledge refinement** → §8's Stage 1→4 pipeline, a real
   Ledgerkit-scoped `intermediate/` candidate-region addition adding a
   genuine edge case, verified end to end through to a `CONFIRMED` Claim
   once real evidence is gathered.
2. **Unsupported external claim** → §1.2/§14.2's `UNVERIFIED` state,
   verified that no code path can promote it to `CONFIRMED`/`OBSERVED`
   without a real re-verification step, and that no Observation was
   fabricated (§16.1).
3. **Code contradicts intent** → §1.2.1/§7's `CONFLICT` state, a real
   disposable fixture: a declared invariant, an implementation that
   violates it, confirm both survive and the conflict is explicit, never
   silently dropped (reusing the disposable-git-fixture pattern already
   established for Phase 80's own correction work).
4. **Code changes first** → §12's revalidation loop, a real source
   change invalidating a Claim's cited evidence, confirmed to trigger
   `STALE` and a targeted (not whole-tree) documentation-impact check via
   the grounding mechanism (§9.2).
5. **Presentation-only edit** → §9.5's first worked example, confirmed
   no knowledge conflict/record write occurs.
6. **README factual edit** → §9.5's second worked example, confirmed the
   grounding-marker-driven detection actually fires and README cannot
   silently diverge.
7. **Phase promotion** → §5.3, a real phase-scoped Claim promoted into
   `codecompass-domain`'s own corpus, confirmed retrievable by a later,
   independent phase.
8. **Clean-room isolation held** → reusing the existing
   `boundary_check.py` mechanical-transcript-analysis tool (Phase 79/80's
   own established method, §0.4) against whatever dispatch runs the
   Stage 2 review in scenario 1/6 above — proving excluded legacy
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
`enrich select-candidates`/`enrich apply`'s own two-stage shape, and
`knowledge-curator`'s context-packet mode all become **downstream
consumers or direct foundations** of this phase's own mechanism, exactly
as the brief's own governing architectural principle requires. The one
genuinely new thing is the bidirectional reconciliation loop itself,
with its three-way concurrency handling (§1.5/§8) — everything else is
retained or generalised in place.

---

## 18. Scope discipline — this phase's own vertical slice

Ships exactly:

- Canonical knowledge storage: the existing six-record-kind model, with
  §1.2's one new optional field (`reconciliation_state`) and §1.3's two
  new `assertion_kind` values. `provenance_dimension` is explicitly not
  shipped as schema (§1.2).
- Human/tool-editable intermediate docs: §2-§4, with full three-way
  concurrency handling, presentation/semantics separation, and bounded
  candidate regions, for **one** real slug (`codecompass-domain`, reusing
  Phase 80's own already-populated corpus) plus **one** real phase-scoped
  slug exercised end-to-end in dogfood (§16.2).
- Semantic reconciliation: §7/§8/§11's four-stage pipeline and CLI
  surface (`render`/`select-candidates`/`apply`/`status`) and validation
  additions.
- Phase knowledge workflow: §5/§6, validated once, end to end, against
  a real Ledgerkit task (reusing an already-identified, already-
  live-verified candidate if one is still current at implementation
  time — e.g. the Phase 78-amendment's own named `stats` follow-up
  candidate, `planning/phase-78-amendment-followup-plan.md`, re-verified
  live before use, not assumed still accurate).
- At least one project-doc consumer, with explicit grounding: README's
  own new pointer paragraph (§10) plus one real semantic-edit
  reconciliation exercised against a grounded README region (§16.2
  scenario 6). `CONTRIBUTING.md` is brought into scanning/grounding
  scope (§0.2/§10) as part of this same slice, but its own live
  end-to-end dogfood exercise is not required within this bounded slice
  — it is the natural, low-effort next validation once README's own
  exercise passes (named explicitly in the follow-on backlog below), so
  the vertical slice itself stays to one fully-exercised project-doc
  consumer, not two.

**Explicitly not in this phase** (named for the follow-on backlog, §19):
a complete general-purpose knowledge graph (new `context-graph.db`
tables for concepts/behaviours — §0.2's boundary holds); full MCP
delivery (Phase 25, already independently deferred); autonomous
conflict resolution (§14's own explicit prohibition — a concurrent-
change conflict or a CONFLICT state is always surfaced, never
auto-resolved); autonomous evidence research (Stage 2's review always
requires a human or an explicit agent dispatch — the pipeline never
decides on its own to go gather evidence); arbitrary natural-language
database editing (every edit goes through the anchor-based,
record-identified mechanism, or the one bounded candidate-region per
file — never "describe a change in prose anywhere and have it parsed
into an arbitrary record"); a rich UI (plain Markdown + existing CLI
only); exhaustive ontology modelling (§1.3's own explicit minimalism);
automatic acceptance of AI-generated claims (§1.2/§14's own core safety
rule); automatic documentation rewriting across the full repository
(§12's targeted-update discipline).

---

## 19. Files expected to change

### This planning commit (now)

- **Amended**: this file,
  `planning/phase-81-intermediate-knowledge-layer.md`.
- **`planning/ROADMAP.md`**: Phase 81's own row text updated to reflect
  the amendment (still `planned`, not yet implemented).
- **`planning/CONTEXT.md`**: current-state section updated to record the
  amendment and its twelve corrections.

### At implementation time (later commits, not this one)

1. `scripts/check_knowledge_base.py`: §1.2's one new optional field
   (`reconciliation_state`) and §1.3's two new enum values;
   `check_anchor_integrity` (§11) — each following the existing
   "reproduce the failure in a disposable fixture before fixing"
   discipline. **No `check_provenance_dimension_consistency`** (dropped,
   §11).
2. `src/codecompass/`: new `knowledge_intermediate.py` (rendering,
   anchor/candidate-region/grounding-marker parsing, the three-way
   detection logic, `derive_provenance_label`, the presentation cache,
   manifest read/write) and `cli.py` additions (§11's four subcommands:
   `render`/`select-candidates`/`apply`/`status`) — **no
   `context-graph.db` schema change** (§0.2/§1's own governing rule).
3. `src/codecompass/spec_docs.py` (or wherever `_EXCLUDED_ROOT_NAMES` is
   defined): remove `CONTRIBUTING.md` from the exclusion list; `CLAUDE.md`
   stays excluded (§0.2).
4. `docs/codecompass-knowledge-workflow.md` (new, §3);
   `README.md`/`CONTRIBUTING.md` additions (§10), including at least one
   real `codecompass-grounded-by` marker in each, exercised by dogfood
   scenario 6.
5. `planning/knowledge/codecompass-domain/intermediate/*.md` — the
   project-wide pilot slug (§18), each file pre-populated with its own
   candidate-region markers (§4.4).
6. One phase-scoped dogfood run against Ledgerkit (§16.2), producing its
   own real `planning/knowledge/<slug>/intermediate/` content and
   `planning/knowledge/<slug>/reconciliation/` manifest trail.
7. `codecompass-template` — §15.1's new, separate
   `optional-intermediate-knowledge/` directory, a separate commit to
   that repository.
8. Tests: `tests/test_knowledge_intermediate.py` (§16.1, expanded).
9. New `decisions/` ADR(s): at minimum, one recording this phase's own
   central architectural choice (§1 — canonical model stays
   `planning/knowledge/`, not `context-graph.db`) and one recording the
   corrected provenance/reconciliation design (§1.2/§7/§8 — derived
   provenance classification plus the one persisted `reconciliation_state`
   field, the three-way concurrency model, and the detect/review/apply
   separation) and its mapping onto existing fields — genuine non-obvious
   tradeoffs per `CLAUDE.md` §2, now including the record of *why*
   `provenance_dimension` was dropped after being proposed, which is
   itself worth a durable rationale trail.

### At closeout (later, branch-dependent on what dogfooding finds)

- Standard closeout sequence (`CLAUDE.md` §5): retro, learning triage,
  per-phase drift audit, independent `release-phase-auditor` completion
  audit, terminal `roadmap-context-curator` reconciliation.
- If dogfooding (§16.2) surfaces a real design flaw (e.g. the anchor
  mechanism doesn't survive a reorganisation pattern real usage
  produces), a corrective amendment follows this project's own
  established append-only-ADR convention (`decisions/0066`→`0070`'s own
  precedent) — not a silent in-place fix. (This plan file itself may
  still be amended in place, as it was today, only up until
  implementation begins; once implementation starts and is reconciled,
  corrections become new ADRs, not further rewrites of this file.)

---

## Risks and mitigations

- **Risk**: the bidirectional loop, now with three-way concurrency
  handling, is the one genuinely novel mechanism in this whole plan
  (§0.3) — everything else is reuse, but this part has no existing
  precedent to lean on beyond Git's own merge-base concept, borrowed by
  analogy. **Mitigation**: the vertical slice (§18) validates it against
  exactly one real project-wide slug and one real phase-scoped slug
  before any broader rollout; §16.1's unit tests pin the concurrency,
  presentation-independence, and no-fabricated-observation properties
  mechanically before any dogfood run.
- **Risk**: conflating "canonical knowledge model" with "`context-graph.db`"
  is the most likely way a reviewer or future contributor could
  misread this plan's own intent, given how central the graph already
  is to CodeCompass's own identity. **Mitigation**: §0.2/§1 state the
  boundary explicitly and repeatedly; the new ADR named in §19 point 9
  makes it a permanent, citable record, not just this plan's own prose.
- **Risk**: the presentation-vs-semantic classification (§9.3) is a
  genuine judgment call with no mechanical ground truth — it could be
  wrong in either direction (false `PRESENTATION_ONLY`, silently missing
  a real factual drift; false semantic flag, generating reconciliation
  noise for harmless wording changes). **Mitigation**: honestly named as
  a dogfood-tunable judgment call, not assumed solved; §16.2 scenarios
  5/6 are specifically designed to catch both failure directions before
  the mechanism is trusted more broadly.
- **Risk**: splitting reconciliation into four stages (detect/review/
  apply/re-render) adds real process overhead compared to the original
  draft's single step, and a maintainer could be tempted to skip Stage 2
  review under time pressure. **Mitigation**: `apply` mechanically
  re-validates from scratch regardless of what Stage 2 claims (§8), so
  skipping genuine review degrades to "an unreviewed proposal was
  mechanically checked and still landed at UNVERIFIED/INTENT_ONLY" rather
  than to "an unreviewed claim became canonical fact" — the fail-closed
  floor holds even under a rushed Stage 2.
- **Risk**: strict isolation remains `UNMET`/`best-effort` for whatever
  dispatch performs the Stage 2 review/classification step, same as
  every prior clean-room phase. **Mitigation**: this is a known,
  already-disclosed, already-accepted limitation of this project's own
  current environment (§0.4) — not a new risk this phase introduces, and
  not something this phase attempts to solve (the separate, unfunded
  backlog item already names that work).

## Non-goals (restated from §18 for visibility)

A complete general-purpose knowledge graph; full MCP delivery;
autonomous conflict resolution; autonomous evidence research; arbitrary
natural-language database editing (outside recognised anchor/
candidate-region boundaries); a rich UI; exhaustive ontology modelling;
automatic acceptance of AI-generated claims as canonical fact; automatic
documentation rewriting across the full repository.

## Follow-on roadmap/backlog candidates (not scoped into this phase)

- Extending `CONTRIBUTING.md`'s own grounding to a full live dogfood
  exercise (not just scanning scope + markers), once README's own
  exercise (§18) has proven the mechanism.
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
- Richer concurrent-change conflict resolution tooling (e.g. a
  side-by-side three-way merge view) beyond this phase's own minimal
  "surface it, never auto-resolve it" behaviour (§1.5/§8), if real usage
  shows the bare manifest listing is too manual.

---

## Decisions requiring explicit maintainer approval

**Resolved by this amendment**, per the user's own explicit disposition
for each (nothing found during research contradicts any of them):

1. **Canonical semantic knowledge remains outside `context-graph.db`
   — approved.** The graph's own mechanical-fact boundary is preserved
   unchanged (§0.2/§1).
2. **`reconciliation_state` — retained**, confirmed by this amendment's
   own analysis to represent genuinely new state with no existing field
   to derive it from (§1.2).
3. **`provenance_dimension` — dropped.** Every value it would have
   carried is fully, unambiguously derivable from existing `kind`/
   `basis`/`status`/`authorised_by` fields (with one documented
   resolution rule for the single ambiguous `directly_stated` case,
   always defaulting to the more cautious label); persisting it would
   have duplicated state and created a drift risk with no offsetting
   benefit (§1.2).
4. **`CONTRIBUTING.md` — brought into project-document grounding/
   reconciliation scope for Phase 81.** Removed from `_EXCLUDED_ROOT_NAMES`
   alongside README (§0.2/§9/§10); `CLAUDE.md` remains separately
   governed and excluded, per its own §0.
5. **Template organisation — a separate, lightweight
   `optional-intermediate-knowledge/` directory**, not merged into
   `optional-clean-room-workflow/` (§15.1). Clean-room documentation
   remains one consumer of the broader knowledge layer, not its
   definition.
6. **CLI namespace — retained in principle, revised in shape.** The
   `codecompass knowledge ...` family is kept, now as
   `render`/`select-candidates`/`apply`/`status` — directly mirroring the
   existing `enrich select-candidates`/`enrich apply` split (§0.2/§11)
   so detection, review, and canonical mutation are mechanically
   separated and an LLM/human judgment can never bypass validation when
   writing to the canonical store.

No open maintainer-approval items remain from the original draft. Any
further refinement (e.g. the exact candidate-region parsing granularity,
or the manifest's precise TOML field names) is an ordinary implementation
detail, not a architectural decision requiring approval before work
starts.
