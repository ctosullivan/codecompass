# Phase 81 — persistent bidirectional intermediate knowledge layer

**Status: planned, amended twice, about to begin implementation.**

Direct user request, 2026-10-07. Evolves CodeCompass toward a model
where its canonical knowledge is editable, through ordinary Markdown,
by humans and external AI tools (ChatGPT, Copilot, Claude Code, plain
Git PRs) via a reconciliation boundary — never bypassing it — while
project documentation and coding/planning context are grounded in the
same reconciled knowledge rather than drifting as independent sources
of truth.

**Second amendment note (2026-10-07, same day, before implementation
began)**: four more issues were found on a second review and are
corrected here, in place, following this project's own established
convention of revising a still-unapproved plan directly rather than
appending a contradicting note (the first amendment, also in-place,
corrected twelve earlier issues; both amendments are summarised below so
a reader never needs the git history to understand why the design looks
the way it does).

1. **The three-way hash model compared two different representations.**
   The first amendment's single BASE/CURRENT/EDITED hash compared a
   canonical YAML record's own content hash against a rendered
   Markdown block's own content hash — two different texts that can
   never be expected to match even when nothing changed. Corrected:
   two distinct baselines per rendered block,
   `base_semantic_hash`/`base_projection_hash`, compared against freshly
   computed `current_semantic_hash`/`current_projection_hash` (§1.5).
2. **A second, overlapping epistemic-state system risked being bolted
   onto canonical Claims.** The first amendment already dropped
   `provenance_dimension`; this amendment goes further and finds that
   the retained `reconciliation_state` field is *also* unnecessary —
   every state it was meant to track is already fully expressible via
   the existing `status`/`evidence_support_state`/`basis`/
   `contradicting_evidence` fields Phase 54c/79 already ship. **Phase 81
   now adds zero new persisted fields to any canonical record.** The
   reconciliation *process's own* lifecycle (pending/reviewed/accepted/
   etc.) lives entirely in the manifest, which describes proposed edits,
   never the knowledge itself (§1.2).
3. **The candidate-region mechanism could produce a Requirement with no
   human-authorised Decision behind it**, and referred to a field,
   `authorised_by`, that does not exist in the real schema (the real
   field is `decision:`, confirmed by direct re-reading of
   `scripts/check_knowledge_base.py` and `docs/domain/concepts/requirement.md`).
   Corrected: a candidate addition only ever becomes a Claim by default;
   it may propose a Requirement only when it explicitly cites a real,
   already-`approved` Decision satisfying the existing schema — never an
   invented one (§4.4/§14.3). A new validator check,
   `check_requirement_cites_approved_decision`, makes this a mechanical,
   fail-closed guarantee project-wide, not just for Phase 81's own new
   content (§11; verified safe against every one of the nine existing
   Requirement records, §0.1).
4. **Explicit grounding alone could let ungrounded project-doc prose
   quietly keep drifting**, since grounding markers are intentionally
   optional. Added a small, advisory-only grounding-coverage report
   (§9.6/§11) distinguishing grounded regions, changed grounded regions,
   and changed-but-ungrounded regions needing a look — never blocking,
   never auto-mutating anything, just visibility.

**First amendment note (2026-10-07, earlier the same day)**, preserved
for context: corrected twelve issues in the original draft — no account
of concurrent change; a presentation-only wording edit being written
into canonical semantics; the candidate-region mechanism fabricating
Observation provenance; no bounded region for candidate additions;
project-doc grounding relying on AI rediscovery instead of a durable
marker; one CLI verb conflating detection/judgment/mutation; a
redundant persisted `provenance_dimension` field; confirmation semantics
that risked letting a human Decision stand in for an actual observation
of implementation behaviour; plus the maintainer-approval list, tests,
and the rest of the document being updated to match. Every numbered
section below reflects both amendments; nothing stale survives.

**Naming note**: `planning/phase-81-strict-isolation-backlog-prompt.md`
already exists, using "81" as a filename prefix for a *backlog item's
saved prompt* (recorded 2026-10-02). That item has **no phase number in
`planning/ROADMAP.md`** — unscheduled backlog rows explicitly carry none
— so there is no real numbering collision; "Phase 81" is genuinely free.

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

**The real Requirement schema, confirmed directly from
`scripts/check_knowledge_base.py`'s own `_REQUIRED_FIELDS["requirement"]`
and a live example (`REQ-DOCORIGIN-002.yaml`)**: `id`, `kind`,
`statement`, `example` (a Given/When/Then scenario), **`decision`** (not
`authorised_by` — the first amendment's own draft used the wrong field
name; every reference to it below uses the real one), `status`. There is
currently **no check that the cited Decision is actually `approved`** —
only that the id resolves to a real file at all
(`check_cross_references_resolve`). Checked directly against all nine
existing Requirement records in the repository: every single one already
cites an `approved` Decision, so adding this check (§11) is safe and
breaks nothing existing — it closes a real, previously-unenforced gap
this phase's own candidate workflow would otherwise be able to exploit.

Also already real: a **frozen-snapshot format** (`decisions/0066`, TOML)
capturing a versioned assertion-plus-evidence-closure with real
historical git-blob hashes, and three already-working checks:
`check_snapshot_completeness` (fail-closed structural validation, hardened
across Phases 79/80), `check_snapshot_historical_integrity` (tamper
detection against historical content), and — **directly relevant to this
phase** — `check_snapshot_current_divergence`, which already detects when
a record's *current* content hash has drifted from what a snapshot froze,
by comparing the **full raw YAML file text** (`current == historical`,
confirmed by direct reading of the function) — not a subset of fields.
This is both the nearest existing staleness-trigger precedent and the
exact precedent `base_semantic_hash`/`current_semantic_hash` (§1.5)
reuse: the semantic hash is the hash of the whole record file's own raw
text, computed the same way `_sha256` already computes a snapshot's own
`content_hash`.

**Honest, pre-existing gaps in this model**, disclosed by its own docs:
`contradicting_evidence` and Claim-`supersedes` have never once been
exercised with real content across the whole corpus (structurally
supported, never proven) — this phase's own dogfood (§16.2 scenario 3)
is the first real exercise of `contradicting_evidence` for a genuine
intent-vs-reality disagreement, reusing it rather than inventing a new
cross-Claim conflict field (§1.2); **"invariant" is not a seventh record
kind** — it exists only as one `assertion_kind` enum value on Claims, an
informal `design.md` subsection convention, and the unrelated
`docs/domain/invariants.md` project-level file — three unlinked senses,
never consolidated (§1.3).

### 0.2 `context-graph.db`'s own boundary is deliberate and must not move

`src/codecompass/graph.py` is a deterministically rebuilt store of
**mechanically-detected structural facts only** — three lifecycle
categories (delete-and-reinsert edge/leaf tables; upserted-by-
natural-key identity-preserving node tables; never-touched-by-rebuild
enrichment tables). This boundary has been reaffirmed, not reopened, at
every prior opportunity (`decisions/0024`/`0025`/`0031`/`0037`/`0045`,
most explicitly `decisions/0051`: *"An agent's suggested relationship is
an observation with provenance. It is captured in `planning/context-gaps/`
and nowhere else... no agent, or any AI call, [gets] influence over the
contents of the graph."*). **This plan does not propose new "concept"/
"invariant"/"behaviour" tables in `context-graph.db`.** The graph stays
exactly what it is; it becomes one of several **evidence sources** the
knowledge layer cites. **Approved, unchanged by either amendment** — see
"Decisions" at the end of this plan.

**A project's own documentation is already a first-class graph object**,
confirmed by direct reading of `spec_docs.py`/`doc_mapping.py`: every
whole-project `sync` already detects `README.md`, `architecture/**/*.md`,
`decisions/**/*.md`, `docs/**/*.md`, `ai-docs/**/*.md`, `dev-docs/**/*.md`
(and more) as `doc_artifacts` rows (`kind='spec_doc'`, `origin='project'`
or `'pinned_reference'`), chunks them (`doc_chunks`, content-hashed), and
mechanically mention-links them to vendors/other docs
(`doc_relations_edges`). `CONTRIBUTING.md` and `CLAUDE.md` are currently
both explicitly excluded (`_EXCLUDED_ROOT_NAMES`, confirmed directly:
`{"CHANGELOG.md", "CONTRIBUTING.md", "CLAUDE.md"}`). **Decided, unchanged
by this amendment**: `CONTRIBUTING.md` is removed from that set for
Phase 81 (§9/§10); `CLAUDE.md` stays excluded, self-governing under its
own §0.

The existing `enrich` CLI command family (`cli.py`,
`relation_enrichment.py`, `decisions/0038`/`0054`) is the closest
existing precedent for both things this phase needs: (a) an external
actor's claim is mechanically reconciled against the graph, not trusted
on its own say-so — an agent-authored enrichment is accepted only if it
exactly matches a currently-pending, mechanically-detected candidate,
tagged `model = "agent:<name>"`; and (b) **`enrich` already separates
mechanical detection from validated mutation as two distinct commands**:
`enrich select-candidates` (mechanical, read-only) and `enrich apply`
(validated, the only command that writes), confirmed directly from
`cli.py`'s own `enrich_apply` docstring: *"Enforces the trust boundary
mechanically, not by agent instruction alone... Writes only through the
existing `apply_results`."* This exact two-stage shape is what
`knowledge select-candidates`/`knowledge apply` copies (§11).

### 0.3 Every existing projection is one-directional; nothing reconciles back

`VendorDigest` rendering (`sync_vendor` → `vendor/<name>/*.md`) is a
real, deterministic DB→Markdown projection, but strictly
regenerate-and-overwrite — it never reads the Markdown back.
`knowledge-curator`'s EXPERIMENTAL **context-packet assembly mode**
(Phase 54c) already compacts everything reachable from an `APPROVED`
`design.md` into one Markdown file (`context-packet.md`) — directly the
shape of a **phase knowledge package** (§13), already built, already
bounded — but it too is write-once. A repo-wide grep for any
reconciliation/round-trip mechanism found none. **The bidirectional loop
this phase proposes does not exist anywhere today, even partially.**

Two existing, independently-evolved comparison vocabularies already do
almost exactly what the new phase's own semantic-diff step needs:
`docs-maintainer`'s legacy-reconciliation mode already classifies an
existing doc's claims as `supported` / `stale_or_contradicted` /
`rationale_requiring_verification` / `useful_example` / `obsolete`;
`domain-skeptic`'s comparison mode already classifies alignment as
`aligned` / `partial` / `conflicting` / `not_implemented` /
`insufficiently_verified`. These inform the manifest's own
Stage-2-classification vocabulary (§8) rather than being replaced by a
third.

### 0.4 The clean-room methodology, isolation backlog, and template

`decisions/0066`–`0070` establish a five-stage pipeline and the
append-only ADR-supersession convention this plan follows.
`planning/strict-isolation-for-documentation-reconstruction.md`
(backlog, unfunded) proposes exactly the kind of stage-specific
input-contract boundary this phase's own reconciliation engine needs —
reused as *framing*, not its still-unbuilt enforcement mechanism; Tier 1
isolation remains unavailable in this environment, so this phase's own
isolation posture stays `best-effort`, honestly labelled, same as every
clean-room phase to date. `codecompass-template` (HEAD `68bae8e`) has no
`.codecompass/` or intermediate-document convention yet. **Decided,
unchanged by this amendment**: the template gets a *separate*,
lightweight `optional-intermediate-knowledge/` directory, not merged
into `optional-clean-room-workflow/` (§15.1).

### 0.5 Net effect — what's retained / generalised / migrated / superseded / deprecated (§17)

| Existing component | Disposition |
|---|---|
| Observation/Evidence/Claim/Derivation/Decision/Requirement model + `check_knowledge_base.py` | **Retain, unmodified by schema.** Phase 81 adds zero new fields; it adds one new cross-reference check (`check_requirement_cites_approved_decision`) and one new structural check (`check_anchor_integrity`) to the same script. |
| Frozen-snapshot format + its three checks | **Generalise**: `check_snapshot_current_divergence`'s own full-file-hash comparison is the direct model for `base_semantic_hash`/`current_semantic_hash` (§1.5); the TOML shape itself is reused for the reconciliation manifest (§8/§11). |
| `context-graph.db` schema/boundary | **Retain unchanged.** No new knowledge-object tables. Cited as an evidence source only. |
| `spec_docs.py`/`doc_mapping.py` project-doc tracking | **Retain**, extended to include `CONTRIBUTING.md` (§0.2), reused as the identity anchor for project documentation grounding (§9). |
| `VendorDigest` rendering pattern | **Generalise** into the new intermediate-document renderer (§4). |
| `knowledge-curator`'s context-packet-assembly mode | **Generalise** into the phase-knowledge-package mechanism (§13), loosening its current `APPROVED`-`design.md`-only gate. |
| `docs-maintainer`/`domain-skeptic`'s two comparison vocabularies | **Generalise**, informing the manifest's own Stage-2 vocabulary (§8); original vocabularies untouched for their own existing use cases. |
| Existing Claim `status`/`evidence_support_state`/`contradicting_evidence`/`basis` fields | **Reused directly, unextended**, as the entire epistemic-state vocabulary this phase needs (§1.2) — the single biggest simplification this amendment makes. |
| `decisions/0051`'s "agent-suggested content is captured, never graphed, promoted only via a gate" | **Retain as the governing precedent**, extended to the new intermediate-document change class (§14). |
| `enrich select-candidates`/`enrich apply`'s detection-vs-mutation split + `agent:<name>` provenance tagging | **Generalise directly** into `knowledge select-candidates`/`knowledge apply` (§11). |
| `documentation-lifecycle.md`'s six content categories + incremental-maintenance loop | **Retain**, extended by this phase's own targeted-update mechanism (§12). |
| `reference-project-protocol.md`'s dogfood conventions | **Retain unchanged**, reused for this phase's own Ledgerkit-style validation (§6/§16). |
| Bidirectional Markdown↔record reconciliation, with dual-hash concurrency handling | **New — does not exist today in any form.** The phase's own real deliverable (§1.5/§8). |
| A formal "invariant" record kind | **Superseded in its current fragmented form** by a minimal consolidation (§1.3) — not a new seventh record kind. |

---

## 1. Canonical knowledge model (governing ownership rule)

**The canonical knowledge model is `planning/knowledge/`'s existing
Observation/Evidence/Claim/Derivation/Decision/Requirement corpus, not a
new or extended `context-graph.db` schema.** `context-graph.db` remains
exactly what it is today. **Approved** — nothing found during research
contradicts it, across either amendment.

### 1.1 Why the existing model, not a new one

- It already has real status lifecycles distinguishing fact from intent
  (Claim vs. Decision), real evidence-citation discipline
  (`supporting_evidence`/`contradicting_evidence` with mechanical
  cross-reference resolution), and a real, already-hardened validation
  script with three rounds of fail-closed fixes behind it.
- It is already file-based, already lives in Git, already has a stable
  per-record identity (`id:` field + filename).
- Building a second, parallel store would violate the governing
  instruction to reuse existing abstractions.

### 1.2 Schema — zero new persisted fields (fully revised by this amendment)

**The original draft proposed a persisted `provenance_dimension`; the
first amendment dropped it and kept one new field, `reconciliation_state`
(`CONFIRMED`/`INTENT_ONLY`/`CONFLICT`/`UNVERIFIED`/`STALE`). This
amendment reviews `reconciliation_state` against the same test the first
amendment applied to `provenance_dimension` — "does this capture
irreducible state not safely derivable from existing fields" — and finds
the answer is no. Every value maps cleanly onto fields that already
exist:**

| Proposed value | Already expressed by |
|---|---|
| `CONFIRMED` | `status: supported` or `status: verified` (existing Claim/Requirement status values, reached only through the existing evidence-gated promotion discipline — an `aligned` comparison finding alone never promotes, per `decisions/0066`, unchanged) |
| `INTENT_ONLY` | `status: proposed` with `basis: proposed_policy` (both already exist; a brand-new Claim already defaults to `proposed` — there is nothing to add) |
| `UNVERIFIED` | `status: proposed` with `evidence_support_state: unsupported` (both already exist) |
| `CONFLICT` (a record's own evidence disagrees with it) | `status: contradicted` plus `evidence_support_state: conflicting` plus the existing `contradicting_evidence` citation (all three already exist) |
| `CONFLICT` (two separate records about the same subject disagree — e.g. declared intent vs. observed reality) | **No new cross-Claim field needed.** File a disconfirming Evidence record (`EV-...`, ordinary `evidence_kind`, `what_it_shows` stating the cross-claim discrepancy plainly) and cite it from the `DECLARED`-labelled Claim's own existing `contradicting_evidence` field, moving that Claim's own `status` to `contradicted`. The `OBSERVED`-labelled Claim stands separately, unaffected, confirmed through its own evidence. Both records survive; the disagreement is fully traceable through ordinary citation (§8's own worked example makes this concrete) — reusing a field (`contradicting_evidence`) the project's own docs already admit "has never once been exercised with real content" (§0.1), rather than adding a new relationship type to avoid exercising it. |
| `STALE` | **Never persisted** — derived mechanically, exactly like `check_snapshot_current_divergence` already does for a frozen snapshot: compare the Claim's own current full-file hash against the hash recorded the last time reconciliation touched it (§8's manifest keeps this history; `knowledge status`, §11, reports staleness as a live computation, never a stored field). |

**Governing distinction, stated explicitly per the amendment's own
instruction**: *canonical records describe what the project knows,
intends, requires, and why. The reconciliation manifest describes the
lifecycle of a **proposed edit** to that knowledge* — `pending` /
`presentation_only` / `semantic_candidate` / `concurrent_conflict` /
`reviewed` / `accepted` / `rejected` / `applied` (§8) are manifest-item
states, never canonical-record states, and never written anywhere near
a `.yaml` record. Once an item reaches `applied`, the canonical record
it produced or edited is an **entirely ordinary** Claim/Requirement,
indistinguishable in its own schema from one authored any other way —
Phase 81 does not add a "this came through reconciliation" marker to the
record itself beyond the already-existing `derived_by`/`decided_by`
provenance fields, extended with an `external:<tool-name>`/
`external:unknown` value where appropriate (§14.4), exactly as those
fields already accept `"context-researcher agent dispatch"` or similar
free text today.

**Repository analysis found no irreducible canonical field is required.**
Per the amendment's own fallback instruction, this is stated and
justified explicitly here, in the plan, rather than silently decided —
and no ADR is needed to add a field, since none is added; the ADR this
phase does add (§19) instead records *why* the two previously-proposed
fields were both rejected, which is itself a real, citable, non-obvious
design decision worth a durable rationale trail.

#### 1.2.1 Derived provenance label — unchanged, still not persisted

A rendering-time-only classification (`derive_provenance_label`, in the
new `knowledge_intermediate.py`, not the validator) maps `kind`/`basis`/
`status` onto a human-readable `OBSERVED`/`DECLARED`/`DECIDED`/`DERIVED`/
`HISTORICAL` label for display purposes only (the provenance line shown
in every rendered block, §3.1 point 3):

- `OBSERVED` ⇐ `basis: observed_behaviour`.
- `DECLARED` ⇐ `basis: proposed_policy`, or the record is itself a
  Decision.
- `DECIDED` ⇐ a Requirement whose cited `decision:` has `status: approved`.
- `DERIVED` ⇐ `basis: inferred`.
- `HISTORICAL` ⇐ `status: superseded` (a lifecycle condition, not a
  provenance source — computed separately from the basis-driven labels
  above, and shown instead of them when it applies).
- The one ambiguous input, `basis: directly_stated`, is resolved by
  walking the Claim's own cited Evidence chain: if every cited Evidence
  traces to at least one `OBS-` Observation, label `OBSERVED`; if the
  chain is a doc/design assertion only, label `DECLARED`; if genuinely
  mixed, label `MIXED` — **ambiguity always resolves to the more
  cautious, lower-confidence label, never the stronger one.**

This remains purely a rendering convenience with no schema footprint —
it cannot drift from the fields it derives, and needs no validator
check, only an ordinary unit test (§16.1).

#### 1.2.2 Confirmation semantics — tightened, now stated against real fields

`status: supported`/`status: verified` is never a single undifferentiated
"this is true" stamp; it always means evidence of the kind appropriate
to the record's own `basis` currently supports it:

- A Claim with `basis: observed_behaviour` reaches `supported`/`verified`
  only through real, reproducible Observation+Evidence — a human
  Decision alone can never move it there.
- A Decision (or a Claim with `basis: proposed_policy`) reaching
  `approved` means "this intent is affirmed" — the right and sufficient
  evidence for *this* is exactly a human's own ratification. **This must
  never be read, rendered, or mechanically treated as confirmation that
  the implementation currently behaves this way** — that is always a
  separate, `basis: observed_behaviour` Claim, confirmed only by its own
  evidence.
- A Claim with `basis: inferred` reaches `supported` only when its own
  cited Evidence chain — not a human's say-so — supports the inference.

**When a `DECLARED` record and an `OBSERVED` record about the same
subject disagree**, both are kept; reconciliation's `apply` step is
mechanically forbidden from editing either to match the other; the
disagreement is filed as a disconfirming Evidence record per §1.2's own
table — never collapsed into one authoritative statement (§8 restates
this as a cross-cutting rule).

### 1.3 Consolidating "invariant" — not a new record kind

Per §0.1's own honest finding, "invariant" is currently three unlinked
things. This phase consolidates, minimally:

- `assertion_kind: invariant` (already exists on Claims) becomes the one
  authoritative way to mark a Claim as an invariant.
- `docs/domain/invariants.md` (the existing project-wide file) becomes a
  **projected view** (§4) filtering Claims by `assertion_kind: invariant`
  — not migrated in this phase (§18's own scope discipline); migrating
  it is a named follow-on (§19).
- A `design.md`'s own informal "Invariants" subsection convention is
  documented as "this is where a Claim with `assertion_kind: invariant`,
  not yet promoted, is drafted before promotion" — a workflow note, not a
  schema change.

"Constraint," "edge case," and "assumption" are **not** given their own
record kinds either, per the explicit non-goal against "exhaustive
ontology modelling" (§18): a constraint is a `rule`- or `invariant`-kind
Claim; an edge case is a `boundary`-kind Claim; an assumption is a Claim
with `basis: proposed_policy`, `status: proposed`. "Workflow" and
"behaviour" map onto existing kinds via `depends_on` chains. **One small,
genuinely new addition, unaffected by this amendment**: `assertion_kind`
gains two more enum values, `workflow` and `constraint`.

### 1.4 Stable semantic identity

Already provided by the existing `id:` field + filename convention —
untested under reimport, not actually broken. This phase's own
acceptance tests (§16) exercise it for real for the first time.

### 1.5 Dual-hash reconciliation identity — corrected by this amendment

**The first amendment's single BASE/CURRENT/EDITED hash compared a
canonical YAML record's own content hash directly against a rendered
Markdown block's own content hash — two different representations of
the same knowledge that will almost never byte-match even when nothing
meaningful changed, since rendering reformats (headings, citations,
status lines, the presentation cache, §4.5). Comparing them directly
could never actually answer "was this edited."** Corrected: **two
independent baselines, each compared only against its own kind of
current value**:

- **`base_semantic_hash`** — the hash of the canonical record's own full
  raw YAML file text, taken at the moment the currently-open projection
  was last rendered. Computed exactly the way `check_snapshot_current_divergence`
  already hashes a record for drift detection (§0.1) — full file text,
  not a field subset.
- **`base_projection_hash`** — the hash of the exact rendered Markdown
  text sitting between that same block's anchor markers, taken at the
  same render time.
- **`current_semantic_hash`** — the canonical record's own full raw file
  hash, computed fresh at reconciliation time.
- **`current_projection_hash`** — the hash of whatever text now sits
  between the anchor markers in the open Markdown file, computed fresh
  at reconciliation time.

Two independent booleans, each comparing like with like:

```
canonical_changed  = current_semantic_hash   != base_semantic_hash
projection_edited  = current_projection_hash != base_projection_hash
```

The four required cases (§8 details the handling of each):

| `canonical_changed` | `projection_edited` | Case |
|---|---|---|
| false | false | No-op. |
| false | true | Candidate reconciliation. |
| true | false | Safe, automatic projection refresh. |
| true | true | Concurrent-change conflict — neither side overwritten. |

`apply` re-checks `base_semantic_hash` against the canonical record's
*live* hash immediately before writing anything (§8), catching a race
that opened up between `select-candidates` and `apply` — this is
unchanged in spirit from the first amendment, only the hash names and
comparison semantics are corrected.

---

## 2. Intermediate knowledge documents

### 2.1 Smallest coherent representation

- `planning/knowledge/<slug>/` is already this project's own established
  convention for a bounded knowledge scope. Reusing it directly avoids a
  second, competing directory convention.
- **Decision, unchanged**: intermediate knowledge documents live at
  `planning/knowledge/<slug>/intermediate/<name>.md`, a new subdirectory
  sibling to each slug's existing records and (where one exists) its
  `snapshots/` directory. A sibling `reconciliation/` directory holds
  that slug's durable, committed reconciliation manifests (§8/§11).
- Project-wide intermediate documents use the reserved, already-existing
  `codecompass-domain` slug. Phase-scoped ones use whatever slug that
  phase's own research already uses.

### 2.2 What an intermediate document actually is

A **live, re-renderable projection** of a filtered set of canonical
records — content deterministically assembled from each record's own
fields, formatted for human/tool readability, with **stable per-record
anchors carrying both baseline hashes** (§1.5/§4.3) so a targeted edit
can be mapped back to the exact record it changed and checked for
concurrent drift.

### 2.3 Regeneration without destroying accepted human contributions or canonical semantics

The four-case table (§1.5/§8) governs regeneration directly:

- `canonical_changed = false, projection_edited = false` → byte-identical
  re-render (no formatting churn).
- `canonical_changed = true, projection_edited = false` → that block is
  refreshed automatically from the new canonical state; every other
  block is untouched.
- `canonical_changed = false, projection_edited = true`, and the edit
  carries no semantic delta → the human's wording is kept via the
  presentation cache (§4.5); **the canonical record itself is never
  touched** by this case, unlike the original draft's design.
- `canonical_changed = false, projection_edited = true`, and the edit
  does carry semantic content → a candidate reconciliation, landing at
  Stage 1 of the pipeline (§8) — never silently applied, never applied
  anywhere except through `apply` (§11).
- `canonical_changed = true, projection_edited = true` → a
  concurrent-change conflict (§1.5/§8): neither side is overwritten; the
  Markdown file is left exactly as the human left it until someone
  resolves it.

---

## 3. Explicit external editing protocol

### 3.1 The guide

`docs/codecompass-knowledge-workflow.md` (new, user-facing, no
CodeCompass-internals knowledge assumed):

1. **What intermediate documents represent** — §2.2's own definition.
2. **Which files may be edited** — anything under
   `planning/knowledge/*/intermediate/` — never `*.yaml` directly, never
   `snapshots/*.toml`, never `reconciliation/*.toml` (the manifest trail
   — written by tooling, read by a reviewer, not hand-edited), never the
   hidden `.presentation-cache.toml` sidecar (§4.5).
3. **Machine-derived vs. maintainer-authored** — every rendered block
   carries a provenance line computed at render time (§1.2.1, not a
   stored field).
4. **How to add new material** — write new prose strictly inside the
   file's own bounded `Candidate additions` region (§4.4). **This never
   creates an Observation.** It proposes exactly one new candidate
   **Claim** per block of new prose — **never directly a Requirement**,
   unless the prose explicitly cites a real, already-`approved` Decision
   satisfying the existing schema, in which case it may propose a
   Requirement tied to that Decision (§4.4/§14.3). A real Observation can
   only come from someone actually performing the reproducible research
   action it represents (§14.2).
5. **What not to modify directly** — the YAML records, the snapshots,
   the reconciliation manifests, the presentation cache, and any block's
   own anchor or candidate-region marker comments.
6. **How identity/provenance is preserved** — the dual-hash anchor
   mechanism (§1.5/§4.3), explained non-technically.
7. **How changes are submitted** — an ordinary Git commit/PR;
   `knowledge select-candidates` runs as a checked-in step, not a
   separate submission channel.
8. **What happens when Markdown disagrees with source evidence** — it
   stays visible as a candidate pending review; if the review finds a
   genuine cross-claim conflict, both sides are preserved and linked via
   a disconfirming Evidence record (§1.2) — never silently resolved.
9. **How conflicts/unverified claims are surfaced** — a dedicated
   "Open conflicts" section in every projected document (§4), populated
   from any `status: contradicted` record touching that document's own
   scope, plus any anchor currently sitting at an unresolved
   concurrent-change conflict.
10. **Editing ≠ immediate canonicity** — *"Editing this file does not
    make your statement true in CodeCompass's own records until it has
    been reviewed and checked against evidence. A brand-new addition
    starts out `proposed`/unsupported — real, visible, and not yet
    confirmed — because writing a sentence here is not the same thing as
    CodeCompass having actually observed it."*
11. **The reconciled database is authoritative afterward** — "the
    database" means the `planning/knowledge/` corpus, not a literal SQL
    database.

### 3.2 Suitability for AI tools specifically

Written to be a complete, self-contained instruction set for an LLM
reading cold, mirroring the existing, already-proven `ai-docs/README.md`
pattern.

---

## 4. Intermediate document structure and rendering

### 4.1 File set

Per §2.1, one `intermediate/` directory per knowledge slug:

- `overview.md` — concepts, architecture, domain knowledge.
- `invariants-and-constraints.md` — invariant/rule/boundary-kind Claims.
- `interfaces-and-behaviours.md` — relationship/state_transformation-kind
  Claims, including workflows.
- `open-questions-and-conflicts.md` — every `status: contradicted`
  record touching this slug, genuinely open questions, and any
  unresolved concurrent-change conflict.

A phase-scoped slug may also render `tests-and-acceptance.md` when
relevant Requirement entries exist. **Every file always ends with one
`Candidate additions` section** (§4.4), present even when empty.

### 4.2 Rendering algorithm

Deterministic, reusing `VendorDigest`'s own established rendering
pattern: for each target file, select matching records; for each, check
the presentation cache (§4.5), compute the current `base_semantic_hash`,
and render one Markdown block wrapped in an anchor comment (§4.3). Blocks
sorted by `id` for a stable diff-friendly order. No AI call.

### 4.3 Stable anchors — corrected by this amendment

Each rendered block opens with an HTML comment carrying **both**
baseline hashes (§1.5):

```markdown
<!-- codecompass-knowledge: CL-ARCH-014 semantic-sha256:3f9a1c... projection-sha256:9e04bb... -->
### The sync pipeline is idempotent under repeated invocation

[rendered statement or cached presentation wording, citations, status line]

<!-- /codecompass-knowledge -->
```

`projection-sha256` is computed over exactly the rendered text between
the two marker comments at render time — this is `base_projection_hash`.
`semantic-sha256` is `base_semantic_hash` (§1.5). On `select-candidates`
(§8/§11), the engine parses every anchor pair, recomputes both current
hashes, and classifies the block via the four-case table. A comment pair
being moved, or new unmarked prose appearing outside any anchor or
candidate-region marker, is never treated as a semantic change to an
existing record.

### 4.4 Candidate-addition boundaries, and the Requirement/Decision invariant

Arbitrary unanchored Markdown prose is never interpreted as candidate
canonical knowledge. The only place new knowledge can be proposed:

```markdown
## Candidate additions

Add new domain knowledge, edge cases, invariants, or open questions
below, strictly between the two marker comments. Content outside this
region — including this paragraph — is never read as knowledge.

To propose a Requirement rather than a Claim, cite an existing,
already-approved Decision id explicitly (e.g. "per DEC-ARCH-003") —
CodeCompass never invents a Decision on your behalf; without a cited,
approved Decision, your addition becomes a Claim.

<!-- codecompass-candidates:start -->

<!-- codecompass-candidates:end -->
```

`select-candidates` reads only the text strictly between the two marker
comments, splits it into blocks on blank-line/heading boundaries, and
for each block:

- **Default**: proposes exactly one new candidate **Claim**, `status:
  proposed`, `basis: proposed_policy` (an external assertion of intent)
  or `basis: directly_stated` (if the text itself reads as a factual
  assertion rather than a proposal) — never `basis: observed_behaviour`,
  since no Observation was performed (§14.2).
- **Only if the block explicitly cites a real id matching `DEC-...`**:
  the manifest additionally checks, mechanically, whether that id
  resolves to a real Decision record with `status: approved`. If it
  does, the block may instead propose a candidate **Requirement** citing
  that Decision in its own `decision:` field (satisfying
  `check_requirement_cites_approved_decision`, §11, from the moment it
  is created). If the cited id does not resolve, or resolves to a
  Decision that is not `approved`, the proposal **falls back to a
  Claim-level proposal** — it is never rejected outright, and it never
  fabricates or silently approves a Decision on the external author's
  behalf.
- **Never a Decision.** A Decision stays a human-alone-authored record
  via its existing path; the candidate-region mechanism cannot
  manufacture one.

Moving headings, reformatting, or adding commentary anywhere else in the
file has no effect on canonical knowledge — the parser only ever looks
inside recognised anchor pairs and this one candidate-region pair.

### 4.5 Presentation wording vs. canonical semantics

**Canonical knowledge owns semantic meaning. Projections own
presentation.** A record's own `statement` field is the single source of
*meaning*; it is written only by `apply` (§11), never by a
presentation-only edit.

For the one surface that is literally re-rendered from records —
`intermediate/*.md` — a small sidecar,
`planning/knowledge/<slug>/intermediate/.presentation-cache.toml`, keyed
by record `id`, holds:

```toml
["CL-ARCH-014"]
accepted_for_semantic_hash = "sha256:3f9a1c..."   # must equal current_semantic_hash to still apply
wording = "The sync pipeline can be invoked any number of times without changing its own result."
```

Rendering checks this cache before falling back to deterministically
formatted `statement` text: if an entry exists **and** its
`accepted_for_semantic_hash` still equals the record's current semantic
hash, the cached wording is rendered; otherwise the entry is stale and
is dropped. A reconciliation outcome classified `presentation_only`
(§8, manifest-item state) is exactly what writes a new cache entry — it
never touches the YAML record.

Context packets (§13) are themselves a scoped re-rendering of the same
`intermediate/*.md` content, so they inherit whatever wording the cache
already holds. README/CONTRIBUTING/guides need no cache at all — they
are hand-authored prose that cites/grounds against canonical knowledge
without ever being regenerated from it (§9.4).

---

## 5. Phase knowledge packages

### 5.1 Reuse `knowledge-curator`'s existing context-packet-assembly mode, generalised

A phase knowledge package is assembled the same way, **triggered by a
phase's own plan file existing**, scoped to whatever
`planning/knowledge/<slug>/` the phase's own research populates.

### 5.2 Not separate files, not a separate representation — a filtered view

A phase knowledge package is the same `intermediate/*.md` rendering
(§4) scoped to one phase's own slug, plus one additional file,
`phase-brief.md`, summarising feature intent, domain terminology, edge
cases, invariants, existing/desired behaviour, compatibility
constraints, affected interfaces, test scenarios, acceptance behaviour,
and open questions as a single entry point linking into the slug's own
`intermediate/` files.

### 5.3 Promotion, not permanent detachment

A durable discovery made during a phase is a Claim in that phase's own
`planning/knowledge/<slug>/`, exactly like today. `apply` (§11) checks,
for every Claim reaching `status: supported`/`verified`, whether its own
`assertion_kind`/content makes it relevant beyond the originating phase
— a project-wide invariant gets a `depends_on` cross-reference into
`codecompass-domain`'s own corpus (already a valid field; no schema
change), so nothing durable stays trapped in a historical phase's own
planning directory.

---

## 6. Ledgerkit-style expected workflow (dogfood design)

Reuses `reference-project-protocol.md`'s own established conventions
throughout — no new reference-project methodology is invented.

1. CodeCompass retrieves repository evidence plus any existing reconciled
   knowledge for the relevant slug.
2. A phase knowledge package (§5) is assembled and committed.
3. The developer (or an external tool: ChatGPT, Copilot, Claude Code, a
   plain editor) edits the package's own `intermediate/` files, writing
   new material only inside each file's candidate region (§4.4).
4. Changes are submitted as an ordinary Git commit/PR.
5. `codecompass knowledge select-candidates <slug>` runs — mechanically
   detecting every anchor's dual-hash classification (§1.5) and every
   new candidate-region block, writing a durable manifest (§8/§11). No
   semantic judgment happens in this step.
6. A human or an agent dispatch (reusing the existing `docs-maintainer`/
   `domain-skeptic` comparison dispatch pattern) reviews the manifest,
   gathers or checks evidence, and annotates each pending item —
   producing a filled-in **reconciliation proposal**.
7. `codecompass knowledge apply <proposal>` validates the proposal
   mechanically (same fail-closed checks as `check_knowledge_base.py`,
   plus a fresh `base_semantic_hash` recheck at apply time) and — only
   here — writes the canonical records, via the existing Claim/Requirement
   lifecycle unmodified. Conflicts stay explicit (§1.2).
8. `codecompass knowledge render` refreshes `intermediate/*.md`,
   preserving presentation wording where still valid.
9. Coding/planning agents consume the reconciled knowledge directly
   (§13) — no separate development-only store.
10. After implementation, changed source/tests trigger revalidation
    (§12) of whichever Claims cited the now-changed evidence.
11. README/CONTRIBUTING/architecture docs are refreshed where the
    reconciled knowledge actually bears on their own content (§9/§12).

**This workflow is explicitly validated to remain useful when the code
is written manually, via Copilot, via ChatGPT, or via Claude** (§16.2/§8
of the user's own governing prompt) — nothing in steps 1-8 requires any
particular tool to have written the implementation; reconciliation
operates on the resulting project state, independent of which tool
authored the code.

---

## 7. Provenance and reconciliation — the unified state model

§1.2 establishes that every epistemic state this phase needs is already
expressed by existing `status`/`evidence_support_state`/`basis`/
`contradicting_evidence` fields — no new vocabulary. This section states
the cross-cutting rules:

- **Observed reality and declared intent are separate dimensions, never
  merged into one field, never merged into one record.** A `DECLARED`-
  labelled record (§1.2.1) can reach `approved`/`supported` (as intent,
  §1.2.2) while a separate `OBSERVED`-labelled record about the same
  subject is independently `proposed` or `contradicted` — they are never
  forced to agree.
- **A human edit to an intermediate document may change `DECLARED`
  content; it may never directly overwrite `OBSERVED` content.** If an
  edited block's underlying record has `basis: observed_behaviour`, the
  edit is never applied as a direct rewrite of that record — `apply`
  (§11) always creates a new, competing candidate Claim instead,
  requiring fresh observation to confirm.
- **Repository evidence may update `OBSERVED` content; it may never
  silently overwrite `DECLARED` intent.** If a code change invalidates
  an `OBSERVED` Claim, revalidation (§12) marks it stale/re-derives it,
  but a separate `DECLARED` Claim about intended behaviour is never
  auto-edited — a genuine disagreement is filed per §1.2's own table,
  never silently resolved.
- **The four confirmation categories stay distinct** (§1.2.2/§14.3):
  accepted intent, verified behaviour, evidence-backed derivation, and
  unsupported external assertion are never collapsed by reconciliation.

---

## 8. Reconciliation mechanics — detection, review, and application as separate stages

Four distinct stages, mirroring `enrich select-candidates`/`enrich
apply`'s own already-proven split (§0.2):

```
canonical records (planning/knowledge/*/*.yaml)
        ↓  render (§4.2, deterministic, no AI call)
intermediate/*.md  (per-record anchors carry base_semantic_hash +
                     base_projection_hash, §1.5/§4.3; one candidate
                     region per file, §4.4)
        ↓  human/tool edit, ordinary Git workflow
edited intermediate/*.md
        ↓  STAGE 1: DETECT — `codecompass knowledge select-candidates <slug>`
        ↓  mechanical only, read-only, no AI call:
        ↓   - for every anchor, compute current_semantic_hash and
        ↓     current_projection_hash, derive canonical_changed /
        ↓     projection_edited (§1.5), classify into one of the four
        ↓     cases below
        ↓   - for every candidate-region block (§4.4), emit one new
        ↓     candidate Claim (or Requirement, if a valid approved
        ↓     Decision is cited) proposal, status: proposed
reconciliation manifest (durable, committed, §11 — TOML, reusing the
  frozen-snapshot format's own shape; manifest-item states: pending,
  presentation_only, semantic_candidate, concurrent_conflict, reviewed,
  accepted, rejected, applied — never written to any canonical record)
        ↓  STAGE 2: REVIEW — human or an agent dispatch (reusing the
        ↓  existing docs-maintainer/domain-skeptic comparison-dispatch
        ↓  pattern) reads the manifest, gathers/checks evidence, and
        ↓  annotates each item (pending → reviewed, with a proposed
        ↓  status/evidence_support_state/contradicting_evidence set,
        ↓  or rejected) — the ONLY stage where semantic judgment happens
reconciliation proposal (the same manifest file, now annotated — not yet
  authoritative; no canonical record has been touched)
        ↓  STAGE 3: APPLY — `codecompass knowledge apply <proposal>`
        ↓  re-validates mechanically (same fail-closed checks as
        ↓  check_knowledge_base.py, plus a fresh base_semantic_hash
        ↓  recheck against the live record, since time may have passed
        ↓  since detection) — this is the ONLY stage allowed to write
        ↓  planning/knowledge/*/*.yaml, and only via the existing,
        ↓  unmodified Claim/Requirement field set
canonical record(s) updated — an ordinary Claim/Requirement, status set
  per §1.2's own existing enum, never a reconciliation-specific field
        ↓  STAGE 4: RE-RENDER — `codecompass knowledge render <slug>`
        ↓  (§4.2) — unaffected anchors reproduce byte-identical prose;
        ↓  only changed anchors' own blocks are rewritten; presentation
        ↓  wording preserved where still valid (§4.5)
refreshed intermediate/*.md
```

**The four dual-hash cases (§1.5), handled at Stage 1 (DETECT):**

| `canonical_changed` | `projection_edited` | Manifest item state | Outcome |
|---|---|---|---|
| false | false | *(no entry created)* | **No-op.** |
| false | true | `pending` → (Stage 2) `semantic_candidate` or `presentation_only` | **Candidate reconciliation.** |
| true | false | *(no manifest entry; handled directly)* | **Safe automatic refresh** — Stage 4 re-renders that block from the new canonical state; no semantic judgment needed. |
| true | true | `concurrent_conflict` | **Concurrent-change conflict.** Neither side is overwritten. The manifest records both current hashes and, for human inspection, the live canonical content and the live projection content side by side. `apply` refuses to act on this item until a human resolves it; the Markdown file itself is left completely untouched by detection — `knowledge status` (§11) surfaces it as an open item. |

**Worked example — a declared-vs-observed conflict, using only existing
fields (§1.2)**: a `DECLARED` Claim states "the sync pipeline should
never make a network call during a dry run." A later `OBSERVED` Claim,
backed by a real Observation, establishes that it currently does. Stage
2 review files a new Evidence record describing this discrepancy and
cites it from the `DECLARED` Claim's own `contradicting_evidence`,
moving that Claim's `status` to `contradicted`. The `OBSERVED` Claim is
untouched, independently `supported`. Both are visible in
`open-questions-and-conflicts.md` (§4.1); neither is deleted or silently
rewritten to agree with the other.

**No formatting churn; no erased prose improvements; no conflation of
presentation with canonical semantics**: a wording-only edit
(`projection_edited = true`, `canonical_changed = false`, no semantic
delta found at Stage 2) writes only to the presentation cache (§4.5) —
the canonical YAML record is never touched by this case.

**An LLM/human reconciliation judgment cannot bypass mechanical
validation**: Stage 2's annotation is advisory until Stage 3 re-validates
it from scratch — `apply` never trusts a proposal's own self-reported
correctness, the same mechanical-trust-boundary discipline `enrich
apply` already enforces.

---

## 9. Project documentation integration

### 9.1 Reuse existing doc-artifact identity

`README.md`/`CONTRIBUTING.md` (brought into scope, §0.2)/`architecture/**`/
`docs/**`/`decisions/**` are `doc_artifacts` rows with stable path
identity and content hashes (`doc_chunks`). Grounding (§9.2) is keyed on
the same identity — no parallel identity invented.

### 9.2 Explicit grounding, not rediscovery every time

- A documentation region may carry an explicit grounding marker:

  ```markdown
  <!-- codecompass-grounded-by: CL-ARCH-014, REQ-ARCH-002 -->
  ### How sync handles idempotency
  ...ordinary, hand-authored prose...
  <!-- /codecompass-grounded-by -->
  ```

  Optional, per-region, never required for every sentence.
- **Canonical knowledge changes → affected doc region identified**: a
  small, mechanical reverse index (scanning `doc_chunks` content for
  `codecompass-grounded-by:` markers citing a given record id — a text
  scan, no new graph table) tells reconciliation exactly which
  documentation regions cite a record whose content just changed.
- **Factual doc changes → relevant canonical knowledge identified**: a
  grounding marker gives the exact ids directly; absent one, the
  existing `doc_relations_edges` mention-detection is a weaker signal,
  flagged for Stage 2 review, never auto-triggering `apply`.
- **Presentation-only doc changes → no semantic mutation**, unaffected
  by marker presence (§9.5).

### 9.3 Detecting presentation vs. semantic edits

Not mechanically decidable from a content-hash change alone — reuses the
same fresh, read-only comparison dispatch pattern already established
for `docs-maintainer`/`domain-skeptic`, given the changed region's own
diff and whichever Claims ground it (strong case) or merely mention it
(weak case). Named explicitly as a judgment call requiring real evidence
to tune (§16.2), not assumed solved on day one.

### 9.4 The flow

```
canonical project knowledge (Claims/Requirements grounding a doc region
  via an explicit codecompass-grounded-by marker, or merely mentioned
  via doc_relations_edges)
        ↓
documentation knowledge/context view (a new intermediate/*.md scoped to
  "project documentation," for reference only — README/CONTRIBUTING
  themselves are never generated from it)
        ↓
README / CONTRIBUTING / architecture / guides / reference
  (human/external-tool-authored prose, NOT auto-generated wholesale)
        ↑  refinement (ordinary edits)
        ↓
presentation edit → logged, no reconciliation triggered, no Claim touched
semantic edit to a grounded region → candidate Claim change → enters the
  same Stage 1→4 pipeline (§8) as an intermediate-document edit
semantic edit to an ungrounded region → flagged via weak mention-
  detection for Stage 2 triage, same pipeline, lower confidence, and
  surfaced in the advisory grounding-coverage report (§9.6)
```

### 9.5 Worked examples

- Rewriting a README introduction for clarity: hash changes, comparison
  dispatch finds no Claim-relevant factual delta → `presentation_only`,
  logged, nothing reconciled.
- Changing a supported-behaviour statement in a grounded region:
  comparison dispatch finds the new wording asserts something the
  grounding Claim doesn't currently say → a candidate Claim edit, enters
  the Stage 1→4 pipeline.
- Adding an architectural invariant to `CONTRIBUTING.md`: either the
  invariant already exists as a Claim (the addition is treated as adding
  a `codecompass-grounded-by` citation, not a new claim) or it doesn't
  (a new candidate Claim, `assertion_kind: invariant`, entering the
  pipeline at `status: proposed`).

### 9.6 Advisory grounding-coverage report (new, amendment point 4)

Grounding markers are deliberately optional, so nothing *requires* a
factual region to be tracked — which risks project docs gradually
drifting back into an opaque body of untracked prose. `knowledge status`
(§11) adds a small, purely advisory report, computed by scanning
`doc_chunks` for grounding markers and cross-referencing the last
`select-candidates` run's own detected content changes:

```
README.md
  grounded regions: 4
  changed grounded regions: 1   (CL-ARCH-014 — pending review)
  ungrounded changed regions requiring review: 2
```

This **never blocks** Phase 81 completion, never auto-mutates anything,
and never forces a grounding marker onto existing prose — it is purely
visibility, so a maintainer can see where documentation has drifted
ahead of (or independent of) the knowledge layer, and choose whether to
add a marker. It only becomes a real (still non-blocking) finding if an
*already-grounded* region is internally inconsistent with the Claim it
cites (e.g. the grounding marker survives a region's prose being deleted
entirely) — `knowledge status --strict` is reserved for genuine
reconciliation-mechanism failures (§11), not for coverage gaps.

---

## 10. README and CONTRIBUTING implications

- **`README.md`** gains one short paragraph under "How it works,"
  pointing to `docs/codecompass-knowledge-workflow.md` — matching this
  project's own "link, don't duplicate" convention.
- **`CONTRIBUTING.md`** — brought fully into scope (§0.2): gains a new
  section, "Knowledge-affecting changes," explaining that a
  knowledge-affecting commit should cite the relevant existing Claim
  (optionally via a grounding marker) or add a new one via the
  candidate-region workflow. Its own factual sections may now also carry
  grounding markers.
- Neither file becomes a second authority: a factual claim here, if it
  ever disagrees with the reconciled knowledge, is itself a candidate
  disagreement to be reconciled (§1.2's own disconfirming-Evidence
  pattern), not a correction applied by hand to the knowledge layer.
  `CLAUDE.md` stays outside this entire mechanism, self-governing under
  its own §0.

---

## 11. CLI / reconciliation surface

Directly mirrors `enrich select-candidates`/`enrich apply` (§0.2):

- **`codecompass knowledge render [<slug>]`** — Stage 4 (and the initial
  projection). Pure, deterministic, no AI call, idempotent.
- **`codecompass knowledge select-candidates <slug> [--dry-run]`** —
  Stage 1. Computes every anchor's dual-hash classification (§1.5) and
  every candidate-region block (§4.4), writing a reconciliation manifest
  to `planning/knowledge/<slug>/reconciliation/<timestamp>.toml` (reusing
  the frozen-snapshot TOML shape). Never invokes an AI model, never
  writes a canonical record. `--dry-run` prints without writing.
- **`codecompass knowledge apply <manifest-path> [--strict]`** — Stage 3.
  The **only** command that writes `planning/knowledge/*/*.yaml`.
  Requires the manifest's items to already be annotated (Stage 2's own
  output); re-validates every annotation mechanically (same fail-closed
  checks as `check_knowledge_base.py`, including the new
  `check_requirement_cites_approved_decision`), re-checks
  `base_semantic_hash` against the live record at apply time, and
  refuses — fail-closed — to touch any item still marked
  `concurrent_conflict`. Writes via the same validated file-write path
  the existing `knowledge-curator`/direct-YAML-authoring paths already
  use; tags externally-sourced content via the existing `derived_by`/
  `decided_by` free-text fields (`"external:<tool-name>"` or
  `"external:unknown"`, never a guess) alongside the existing
  `agent:<name>` convention where an agent performed Stage 2.
- **`codecompass knowledge status [<slug>]`** — reports every record at
  `status: contradicted`/`proposed`-with-`unsupported`-evidence, every
  mechanically-derived `STALE` record (§1.2), every unresolved
  concurrent-change conflict from the latest manifest, and the advisory
  grounding-coverage report (§9.6) — reusing `check`'s own existing
  reporting conventions (table/JSON, `--strict` exit-code semantics,
  where `--strict` covers only genuine reconciliation-mechanism failures,
  never coverage gaps).

New validation additions to `scripts/check_knowledge_base.py` (same
file, same fail-closed discipline, not a new script):

- `check_anchor_integrity` — every `intermediate/*.md` file's own
  anchors resolve to a real record with matching id/kind.
- `check_requirement_cites_approved_decision` (new, amendment point 3)
  — every Requirement's `decision:` field must resolve to a real
  Decision record with `status: approved` — not merely resolve to *any*
  record, which is all `check_cross_references_resolve` already checks.
  Verified safe against all nine existing Requirement records (§0.1) —
  every one already satisfies this.

**No `check_provenance_dimension_consistency`, no
`check_reconciliation_state_consistency`** — neither persisted field
exists (§1.2), so there is nothing for either check to validate.

---

## 12. Incremental documentation maintenance

Reuses `documentation-lifecycle.md`'s own existing per-phase drift-audit
mechanism and incremental-maintenance loop, extended with the new
knowledge-layer's own revalidation trigger:

```
source/test changed
       ↓  (existing: sync detects the content-hash change)
affected evidence identified
       ↓  (new: any Claim whose Evidence cites that file/path is flagged)
dependent knowledge revalidated
       ↓  (existing comparison-dispatch pattern — not a new mechanism)
canonical record updated (re-derived, or a disconfirming Evidence filed,
  §1.2) — only via `knowledge apply` (§8/§11), same as any other change
       ↓
affected intermediate/*.md re-rendered (targeted)
       ↓
affected project docs identified (via grounding markers, falling back to
  doc_relations_edges mention-detection)
       ↓
targeted documentation update (§9.3's semantic-diff dispatch, scoped)
```

**Explicitly not** a full documentation-tree regeneration on every
change.

---

## 13. Development/coding context integration

**No separate development-only knowledge database.** A coding/planning/
review context package for a bounded task is the same `intermediate/*.md`
rendering, scoped by the task's own slug/phase, optionally filtered
(reusing `context-packet.md`'s own existing per-feature compaction
logic) — consumed directly by a CodeCompass agent or externally (handed
to ChatGPT/Copilot/a future MCP surface as-is, since it's already plain,
self-contained Markdown). A context packet inherits whichever
presentation wording the underlying `intermediate/*.md` files already
carry, with no separate cache of its own. The "open conflicts" section
is always included.

---

## 14. Safe collaboration model

### 14.1 Ownership semantics

| Content class | Who may author it | Enters as |
|---|---|---|
| Machine-observed evidence | Mechanical detection only (existing `sync` pipeline) | `basis: observed_behaviour`, directly |
| Machine-derived knowledge | A derivation dispatch, citing real evidence | `basis: inferred`, `status: proposed` until checked |
| Maintainer-declared intent | A human, via a Decision or a direct intermediate-document edit | `basis: proposed_policy`, `status: proposed` until evidence-checked |
| Accepted decisions | A human only — unchanged existing rule | `status: approved` |
| Externally proposed knowledge (candidate-region addition or a Markdown edit) | Any external tool/person | always a **candidate Claim** (or Requirement, only with a cited approved Decision, §4.4) — `status: proposed`, **never an Observation, never `status: supported`/`verified`, on entry** |
| Presentation prose | Anyone, anywhere | not a knowledge record at all — cached or logged only (§4.5) |

### 14.2 External additions are candidate claims, never fabricated observations

An Observation record (`OBS-`) means a reproducible observation/research
action *actually occurred*. An external user or tool writing "Behaviour
X exists" inside a candidate region has not, by writing that sentence,
performed that observation:

```
external addition (candidate region, §4.4)
      ↓
candidate Claim, status: proposed  (or, with a cited approved Decision,
                                     a candidate Requirement, §14.3)
      ↓
independent research or evidence acquisition — a real Observation,
performed by a human or by context-researcher-style primary research,
reusing the existing Observation/Evidence machinery exactly as it works
today for any other Claim
      ↓
Evidence, built from that Observation
      ↓
Claim status moves to supported/contradicted/verified, following the
existing, unmodified Claim status lifecycle — never by the external
text alone
```

A maintainer may, via a Decision, author or ratify project intent — but
**a human's approval of an external candidate never fabricates observed
behaviour**. The four categories stay explicitly distinct:

| Category | How it is produced | Confirmable by |
|---|---|---|
| Accepted intent | A human Decision | Further human Decision only — never promotes to `basis: observed_behaviour` |
| Verified behaviour | Real Observation + Evidence, `basis: observed_behaviour` | Fresh Observation/Evidence only |
| Evidence-backed derivation | `basis: inferred`, citing real Evidence | Its own cited Evidence chain holding up |
| Unsupported external assertion | A candidate-region addition or an unreviewed Markdown edit, no Evidence cited | Nothing, until someone performs the Observation it claims — stays `status: proposed` indefinitely otherwise, exactly as intended |

### 14.3 The Requirement → Decision invariant, mechanically enforced (new, amendment point 3)

Every Requirement must cite exactly one human-authorised, `approved`
Decision via its real `decision:` field (§0.1). The candidate workflow
respects this by construction (§4.4): a candidate addition becomes a
Requirement only when it cites a real, already-`approved` Decision; it
is never auto-created or invented. The default flow for a genuinely new
product/design choice:

```
external Markdown addition
        ↓
candidate Claim
        ↓
evidence/research where applicable
        ↓
human Decision, if a product/design choice is required (unchanged
  existing path — a human authors this, nothing in Phase 81 changes it)
        ↓
Requirement, citing that Decision in its own decision: field
```

`check_requirement_cites_approved_decision` (§11) makes the invariant a
mechanical, fail-closed property of the whole repository, not just of
Phase 81's own new content — closing a real, previously-unenforced gap
(§0.1).

### 14.4 Retained per-record, and the no-silent-resolution rule

Retained per-record: who/what introduced a change (the existing
`derived_by`/`decided_by`/`performed_by` fields, extended with an
`external:<tool-name>`/`external:unknown` convention for a
Markdown-originated edit), the evidence used during reconciliation (the
Evidence record itself), previous states (Git history of the YAML file,
and now also the committed reconciliation manifests — a durable,
auditable trail that did not exist before), and unresolved
contradictions (`status: contradicted` records, and unresolved
concurrent-change conflicts, never silently dropped). **No contradiction
is resolved merely to keep documentation internally consistent** — a
`contradicted` Claim stays `contradicted`, rendered explicitly in every
affected projection, until a real Decision or new Evidence resolves it;
`apply` is mechanically forbidden from picking a side on its own.

---

## 15. Repository self-description

Minimum standard files for a CodeCompass-enabled project to be
self-describing to a cold external agent:

- `docs/codecompass-knowledge-workflow.md` (§3).
- The existing `CLAUDE.md`/`CONTRIBUTING.md` (§10's additions),
  cross-linking rather than duplicating §3's own guide.
- `planning/knowledge/<slug>/intermediate/` itself, self-describing by
  structure.

### 15.1 `codecompass-template` implications — decided, unchanged by this amendment

A new, concise, *separate* `optional-intermediate-knowledge/` directory,
sibling to the existing `optional-clean-room-workflow/` — not merged
into it. Clean-room documentation reconstruction is one *consumer* of
the broader knowledge layer, not its definition. Contains: a short
`README.md`, one worked example, and the minimal file skeleton (§4.1's
four files, each pre-populated with its own candidate-region markers).

---

## 16. Testing and dogfood validation

### 16.1 Deterministic unit/integration tests (new `tests/test_knowledge_intermediate.py`)

Covers the dual-hash concurrency model, the presentation/semantics
split, the corrected candidate-addition semantics, explicit grounding,
the Requirement/Decision invariant, the advisory grounding-coverage
report, and the detect/review/apply separation:

- **No-op round trip**: render → no edit → `select-candidates` → empty
  manifest (no candidate) → re-render byte-identical.
- **Projection-only edit**: canonical record unchanged, projection text
  changed → `projection_edited = true`, `canonical_changed = false` →
  a candidate is generated.
- **Canonical-only change**: projection untouched, canonical record
  changed independently → `canonical_changed = true`,
  `projection_edited = false` → that block is safely, automatically
  refreshed, no manifest entry, no human review needed.
- **Concurrent change**: render version A → an external edit changes the
  projection → the canonical record independently becomes version B →
  `select-candidates` reports a `concurrent_conflict` → assert, directly,
  that **neither** the canonical YAML file **nor** the edited projection
  file changed as a result of detection → `apply` refuses to act on the
  unresolved item.
- **Apply-time race**: `select-candidates` succeeds and produces a
  reviewed, accepted proposal → the canonical record is mutated
  independently before `apply` runs → `apply` re-checks
  `base_semantic_hash` against the live record → `apply` fails closed,
  refusing to write, with a clear error naming the race.
- **Presentation independence**: render → edit one anchor's prose (same
  meaning, different wording) → `select-candidates`/review classify it
  `presentation_only` → `apply` writes *only* the presentation cache,
  confirmed via a direct read of the record's own YAML showing zero byte
  change → re-render preserves the edited wording → a second, separately
  worded presentation of the same fact (e.g. a grounded README region)
  is independently confirmed to keep its own different wording.
- **Unsupported external assertion**: add a candidate-region block
  asserting a new behaviour → `select-candidates` → `apply` → confirm
  the result is exactly one new Claim at `status: proposed` with
  `evidence_support_state: unsupported` or absent, and — querying the
  Observation/Evidence stores directly — **zero new `OBS-`/`EV-`
  records were created**; confirm it cannot reach `supported`/`verified`
  without a real, separately-run Observation/Evidence pass.
- **Requirement invariant**: (a) a candidate block cites a non-existent
  or non-`approved` Decision id → `select-candidates`/`apply` → assert
  no Requirement is created, the proposal remains a Claim-level
  candidate; (b) a candidate block cites a real, `approved` Decision →
  assert a Requirement may be created, passing
  `check_requirement_cites_approved_decision`.
- **Candidate-region boundary**: (a) explanatory prose *outside* the
  candidate-region markers → `select-candidates` → empty manifest; (b) a
  statement *inside* the markers → exactly one candidate entry. Both in
  one test to make the boundary explicit.
- **Explicit documentation grounding**: (a) a Claim with a
  `codecompass-grounded-by` reference from a README region changes →
  assert the affected README region is identified deterministically from
  the marker alone, no dispatch call needed; (b) the grounded README
  region's own text changes factually → assert the grounding marker's
  cited Claim(s) are identified and a manifest entry is produced.
- **Grounding coverage (advisory)**: a changed, ungrounded documentation
  region → assert it is surfaced in `knowledge status`'s own coverage
  report as "requiring review," and assert, directly, that **no
  canonical record is mutated** as a side effect of this report running.
- **Three-stage application safety**: a semantic edit is detected
  (Stage 1) → a proposal is generated and annotated (Stage 2, simulated)
  → assert the canonical record is **still unchanged** → only after
  `apply` (Stage 3) runs does the canonical record change — asserted via
  a direct YAML read before and after each stage.
- Stable identity under reorganisation: render → canonical record's own
  file is reorganised (moved, same `id:`) → re-render still resolves the
  existing anchor correctly.
- `check_anchor_integrity`/`check_requirement_cites_approved_decision`:
  disposable-git-fixture reproductions of each failure mode *before* the
  fix, matching this project's own "reproduce before fixing" discipline
  — required by `CLAUDE.md` §1's own minimal-content-edge-case and
  depth-vs-scope rules for any new fail-closed mechanism.
- `derive_provenance_label`: an ordinary unit test covering each of the
  five labels plus the ambiguous `directly_stated` case.

### 16.2 Realistic dogfood scenarios (reusing `reference-project-protocol.md`'s own conventions)

1. **External knowledge refinement** → §8's Stage 1→4 pipeline, a real
   Ledgerkit-scoped candidate-region addition, verified end to end
   through to `status: supported` once real evidence is gathered.
2. **Unsupported external claim** → §14.2, verified no code path can
   promote it without a real re-verification step, and no Observation
   was fabricated.
3. **Code contradicts intent** → §1.2's disconfirming-Evidence pattern,
   a real disposable fixture: a declared invariant, an implementation
   that violates it, confirm both survive and the conflict is explicit.
4. **Code changes first** → §12's revalidation loop, confirmed to
   trigger a targeted (not whole-tree) documentation-impact check via
   the grounding mechanism.
5. **Presentation-only edit** → §9.5's first worked example, confirmed
   no knowledge conflict/record write occurs.
6. **README factual edit** → §9.5's second worked example, confirmed the
   grounding-marker-driven detection actually fires.
7. **Phase promotion** → §5.3, a real phase-scoped Claim promoted into
   `codecompass-domain`'s own corpus, confirmed retrievable later.
8. **Clean-room isolation held** → reusing the existing
   `boundary_check.py` mechanical-transcript-analysis tool against
   whatever dispatch runs the Stage 2 review in scenario 1/6 above —
   proving excluded legacy documentation cannot enter the reconstructed
   canonical knowledge during a clean-room-scoped reconciliation run,
   labelled `best-effort`, never claimed `verified`.

Every dogfood scenario above is run against a real, pinned Ledgerkit
commit, using the existing seed-then-fork scratch-clone discipline — no
new reference-project convention invented. The dogfood exercise also
demonstrates the development-tool-independence requirement directly: at
least one scenario's own implementation step is performed without any
AI coding tool at all (a manual edit), confirming reconciliation
operates on project state, not on which tool produced it.

---

## 17. Migration of existing documentation/redoc work

Already tabulated at §0.5. Summary: **nothing existing is discarded.**
The clean-room pipeline, the Observation/Evidence/Claim/Derivation
model, the frozen-snapshot format, `spec_docs.py`'s project-doc
tracking, the two comparison vocabularies, `enrich select-candidates`/
`enrich apply`'s own two-stage shape, and `knowledge-curator`'s
context-packet mode all become **downstream consumers or direct
foundations**. The one genuinely new thing is the bidirectional
reconciliation loop itself, with its dual-hash concurrency handling —
everything else is retained or generalised in place, with **zero new
canonical schema**.

---

## 18. Scope discipline — this phase's own vertical slice

Ships exactly:

- Canonical knowledge storage: the existing six-record-kind model,
  **unmodified by schema** except §1.3's two new `assertion_kind`
  values. Zero new persisted fields (§1.2).
- Human/tool-editable intermediate docs: §2-§4, with full dual-hash
  concurrency handling, presentation/semantics separation, and bounded
  candidate regions, for **one** real slug (`codecompass-domain`) plus
  **one** real phase-scoped slug exercised end-to-end in dogfood.
- Semantic reconciliation: §7/§8/§11's four-stage pipeline and CLI
  surface (`render`/`select-candidates`/`apply`/`status`) and the two
  new validator checks.
- Phase knowledge workflow: §5/§6, validated once, end to end, against
  a real Ledgerkit task.
- At least one project-doc consumer, with explicit grounding: README's
  own new pointer paragraph plus one real semantic-edit reconciliation
  exercised against a grounded README region. `CONTRIBUTING.md` is
  brought into scanning/grounding scope as part of this same slice, but
  its own live end-to-end dogfood exercise is not required within this
  bounded slice (named as a follow-on, §19).

**Explicitly not in this phase**: a complete general-purpose knowledge
graph; full MCP delivery; autonomous conflict resolution (a concurrent-
change conflict or a `contradicted` status is always surfaced, never
auto-resolved); autonomous evidence research (Stage 2's review always
requires a human or an explicit agent dispatch); autonomous product/
design decisions (a Decision is always human-authored, §14.3);
arbitrary natural-language database editing (every edit goes through the
anchor-based mechanism, or the one bounded candidate-region per file);
a rich UI; exhaustive ontology modelling; automatic acceptance of
AI-generated claims; automatic documentation rewriting across the full
repository; implementation of the separate, unfunded strict-isolation
backlog item.

---

## 19. Files expected to change

### This planning commit (now)

- **Amended**: this file,
  `planning/phase-81-intermediate-knowledge-layer.md`.
- **`planning/ROADMAP.md`**: Phase 81's own row text updated to reflect
  this second amendment.
- **`planning/CONTEXT.md`**: current-state section updated.

### Implementation (this session, staged per the governing prompt's own sequence)

1. `scripts/check_knowledge_base.py`: §1.3's two new `assertion_kind`
   enum values (no other schema changes); `check_anchor_integrity` and
   `check_requirement_cites_approved_decision` (§11) — each following
   the existing "reproduce the failure in a disposable fixture before
   fixing" discipline.
2. `src/codecompass/knowledge_intermediate.py` (new): rendering,
   anchor/candidate-region/grounding-marker parsing, the dual-hash
   detection logic, `derive_provenance_label`, the presentation cache,
   manifest read/write, the advisory grounding-coverage report.
3. `src/codecompass/cli.py`: new `knowledge_app` Typer sub-app with
   `render`/`select-candidates`/`apply`/`status` — **no
   `context-graph.db` schema change**.
4. `src/codecompass/spec_docs.py`: remove `CONTRIBUTING.md` from
   `_EXCLUDED_ROOT_NAMES`; `CLAUDE.md` stays excluded.
5. `docs/codecompass-knowledge-workflow.md` (new); `README.md`/
   `CONTRIBUTING.md` additions, including at least one real
   `codecompass-grounded-by` marker in each.
6. `planning/knowledge/codecompass-domain/intermediate/*.md` — the
   project-wide pilot slug, each file pre-populated with its own
   candidate-region markers.
7. One phase-scoped dogfood run against Ledgerkit, producing its own
   real `planning/knowledge/<slug>/intermediate/` content and
   `planning/knowledge/<slug>/reconciliation/` manifest trail.
8. `codecompass-template` — §15.1's new, separate
   `optional-intermediate-knowledge/` directory, a separate commit to
   that repository.
9. Tests: `tests/test_knowledge_intermediate.py` (§16.1).
10. New `decisions/` ADR(s): (a) recording the central architectural
    choice (§1 — canonical model stays `planning/knowledge/`); (b)
    recording why **zero** new persisted fields were added — both
    `provenance_dimension` and `reconciliation_state` were proposed and
    rejected, with the reasoning (§1.2) — and the dual-hash concurrency
    model, the detect/review/apply separation, and the Requirement/
    Decision invariant enforcement, as one coherent decision record.

### At closeout

- Standard closeout sequence (`CLAUDE.md` §5): retro, learning triage,
  per-phase drift audit, independent `release-phase-auditor` completion
  audit, terminal `roadmap-context-curator` reconciliation.
- If dogfooding surfaces a real design flaw, a corrective amendment
  follows this project's own established append-only-ADR convention —
  not a silent in-place fix to this plan file, since implementation will
  have begun by then.

---

## Risks and mitigations

- **Risk**: the dual-hash bidirectional loop is the one genuinely novel
  mechanism in this whole plan — everything else is reuse, but this part
  has no existing precedent beyond Git's own merge-base concept, borrowed
  by analogy. **Mitigation**: the vertical slice validates it against
  exactly one real project-wide slug and one real phase-scoped slug
  before any broader rollout; §16.1's unit tests pin the concurrency,
  presentation-independence, and no-fabricated-observation properties
  mechanically before any dogfood run.
- **Risk**: conflating "canonical knowledge model" with
  "`context-graph.db`" is the most likely way a reviewer could misread
  this plan's own intent. **Mitigation**: §0.2/§1 state the boundary
  explicitly and repeatedly; the new ADR (§19) makes it permanent.
- **Risk**: relying entirely on existing `status`/`evidence_support_state`
  fields for the epistemic-state vocabulary (rather than a dedicated
  reconciliation field) could prove too coarse in practice — e.g. two
  genuinely different "not yet confirmed" situations both landing on
  `status: proposed` with no way to distinguish them. **Mitigation**:
  the dogfood run (§16.2) is the first real test of this; if it proves
  too coarse, the follow-on path is an ADR proposing the one irreducible
  field the amendment's own fallback anticipates — not a silent schema
  change mid-phase.
- **Risk**: the presentation-vs-semantic classification is a genuine
  judgment call with no mechanical ground truth. **Mitigation**:
  honestly named as a dogfood-tunable judgment call; §16.2 scenarios 5/6
  are designed to catch both failure directions.
- **Risk**: splitting reconciliation into four stages adds real process
  overhead, and a maintainer could skip Stage 2 review under time
  pressure. **Mitigation**: `apply` mechanically re-validates from
  scratch regardless of what Stage 2 claims, so skipping genuine review
  degrades to "an unreviewed proposal was mechanically checked and still
  landed at `status: proposed`" rather than to "an unreviewed claim
  became canonical fact."
- **Risk**: strict isolation remains `UNMET`/`best-effort` for whatever
  dispatch performs Stage 2. **Mitigation**: a known, already-disclosed,
  already-accepted limitation (§0.4) — not a new risk this phase
  introduces, and not something it attempts to solve.

## Non-goals

A complete general-purpose knowledge graph; full MCP delivery;
autonomous conflict resolution; autonomous evidence research; autonomous
product/design decisions; arbitrary natural-language database editing
(outside recognised anchor/candidate-region boundaries); a rich UI;
exhaustive ontology modelling; automatic acceptance of AI-generated
claims as canonical fact; automatic documentation rewriting across the
full repository; implementing the separate strict-isolation backlog item.

## Follow-on roadmap/backlog candidates (not scoped into this phase)

- Extending `CONTRIBUTING.md`'s own grounding to a full live dogfood
  exercise, once README's own exercise has proven the mechanism.
- Migrating `docs/domain/invariants.md` to be a live projection.
- Extending the intermediate-document convention to every existing
  `planning/knowledge/<slug>/`.
- If the dogfood run proves the existing `status`/`evidence_support_state`
  vocabulary too coarse for some real reconciliation case, a follow-on
  ADR proposing exactly one irreducible canonical field, justified
  against that specific real case (not proposed again speculatively).
- A genuinely separate execution substrate closing the
  `best-effort`→`verified` isolation gap — the already-filed, unfunded
  backlog item's own scope.
- A future MCP surface consuming phase-knowledge packages directly.
- Richer concurrent-change conflict resolution tooling beyond this
  phase's own minimal "surface it, never auto-resolve it" behaviour.

---

## Decisions requiring explicit maintainer approval

**All resolved — none open.** Per both amendments' own explicit
dispositions, confirmed against repository evidence at each step:

1. **Canonical semantic knowledge remains outside `context-graph.db`
   — approved**, unchanged by either amendment (§0.2/§1).
2. **Zero new persisted canonical fields** — both `provenance_dimension`
   and `reconciliation_state` were proposed and, on review, found fully
   derivable from (or better represented by) existing fields; dropped
   (§1.2). If real dogfood experience later proves one field genuinely
   irreducible, that is a new, separately-justified ADR, not a reopening
   of this decision speculatively.
3. **`CONTRIBUTING.md` — brought into project-document grounding/
   reconciliation scope for Phase 81**, unchanged (§0.2/§9/§10).
   `CLAUDE.md` remains separately governed and excluded.
4. **Template organisation — a separate, lightweight
   `optional-intermediate-knowledge/` directory**, unchanged (§15.1).
5. **CLI namespace — `render`/`select-candidates`/`apply`/`status`**,
   directly mirroring `enrich select-candidates`/`enrich apply`,
   unchanged (§0.2/§11).
6. **The Requirement/Decision invariant is mechanically enforced**,
   using the real `decision:` field (not the first draft's incorrect
   `authorised_by`), via a new fail-closed validator check (§11/§14.3).

**This amendment introduces no new unresolved architectural blocker.**
Per the governing prompt's own instruction, implementation proceeds
immediately following this commit.
