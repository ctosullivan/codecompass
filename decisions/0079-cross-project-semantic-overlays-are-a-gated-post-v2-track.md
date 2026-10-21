# 0079. Cross-project semantic overlays are a generic, explicitly-gated post-v2 track — not a Phase 82-88 scope expansion

## Status

Accepted (2026-10-21, direct user request — "CodeCompass v2 Planning
Amendment — Cross-Project Semantic Overlays"). Amends `decisions/0078`;
does not supersede it.

## Context

`decisions/0078` and `planning/v2-roadmap.md` (committed `bb10927`,
confirmed this session as still current `HEAD`, zero drift) establish
CodeCompass v2 as an evidence-backed change-assurance layer for *one*
project at a time. The user now asks CodeCompass to eventually support
**independently constructed project knowledge models that can be
overlaid and compared** — e.g. a federated view comparing Ledgerkit,
hledger, Ledger, and (later) Beancount's shared accounting concepts.
PTA (Ledgerkit's own domain) is named explicitly as the *motivating use
case, not an architectural dependency* — the capability itself must stay
generic.

**Verified current state** (re-inspected this session, not assumed):
`HEAD` is `bb10927`, identical to the prior session's final commit — no
intervening changes to reconcile. `~/projects/ledgerkit` and
`~/projects/hledger` are real, independent local checkouts (`hledger`
confirmed at `33fa849e`, remote `hledgerorg/hledger`, `LICENSE` present
— GPL, matching this project's own `decisions/0053`-era relicensing
rationale for Ledgerkit-facing work). **No local checkout of
`ledger/ledger` (the C++ Ledger CLI) or Beancount exists in this
environment** — their repository state, exact licence terms, and
contribution constraints are **not independently verified this session**
and must not be asserted as known; any future stage touching them
confirms this first, live, rather than reusing this ADR's own
unverified assumption.

Phase 82 (`planning/phase-82-contract-and-evidence-foundation.md`,
`planned`, not implemented) proposes one schema delta, `epistemic_source`
(`intended|observed|verified|uncertain`), reusing the Phase 81
Requirement/Claim record model. Reviewing it against this amendment's
own requirement — INTENDED/OBSERVED/VERIFIED must be genuinely
non-conflated — finds a real design gap, corrected in §3 below.

## Decision

### 1. Three conceptual layers, never merged

- **Layer A — project-specific knowledge.** Exactly what Phase 81/82
  already are: each project's own reconciled Observation/Evidence/
  Claim/Derivation/Decision/Requirement records, owned, versioned, and
  reconciled entirely within that project. **Unchanged by this ADR.**
- **Layer B — shared domain concepts.** A new, optional record kind,
  **Domain Concept** (`DC-<slug>-NNN`), living outside any single
  project's own `planning/knowledge/` tree (e.g.
  `planning/overlays/<domain-slug>/concepts/`). A Domain Concept names
  and defines a term ("account balance," "posting") in plain language.
  **It never asserts that any project implements it, let alone
  identically** — it is vocabulary, not a claim about any
  implementation.
- **Layer C — cross-project semantic relationships.** A new record
  kind, **Cross-Project Mapping** (`XREL-<slug>-NNN`), §4 below. A
  mapping cites project-qualified references into Layer A (and
  optionally a Layer B concept) and carries its own, independent
  evidence, provenance, and verification status. **A mapping never
  promotes a statement about one project into verified knowledge about
  another** — the single hardest non-negotiable constraint this ADR
  establishes, directly enforced by keeping verification status a
  property of the mapping record itself, never written back onto either
  project's own Layer A records.

The Wiki (deferred, Phase 82-88's own standing deferral unchanged)
remains a read-only projection/proposal interface over Layers A-C,
never a fourth, competing canonical store.

### 2. Project-qualified reference envelope, not per-record global IDs

**Existing `REQ-`/`CL-`/`EV-`/`OBS-`/`DE-`/`DEC-` IDs are untouched and
remain project-local** — zero migration to any existing or Phase
82-planned record. Federation identity is carried externally, in a new,
small **project-identity envelope** (one per project, not one per
record — directly reusing Phase 81B's own precedent of recording
identity externally rather than self-referentially, `decisions/0077`'s
`payload_tree_sha256` scheme and its explicit "the actual branch/commit
holding a payload is recorded externally... where self-reference isn't
circular" principle):

```
project_id:        <stable, human-chosen slug — not derived from
                     hosting platform, so it works for a project not on
                     GitHub, or one that moves host>
source_locator:     <a tagged union: {scheme: "git", remote: <url>} |
                     {scheme: "package", registry: <name>, name: <pkg>} |
                     {scheme: "local-only", note: <string>} — never a
                     bare assumption of "GitHub">
revision:           <a tagged union: {scheme: "git-commit", sha: <sha>} |
                     {scheme: "package-version", value: <string>} |
                     {scheme: "unknown", as_of: <date>} — fail-closed:
                     an unresolvable revision is recorded as explicitly
                     "unknown," never silently omitted, matching Phase
                     81B's own fail-closed export discipline>
knowledge_schema_version: <the Layer-A record schema version this
                     project's export was produced under>
exported_at:        <timestamp>
```

A fully **qualified reference** is `(project_id, revision, local_id)` —
e.g. `ledgerkit @ git-commit:7224bb5 # REQ-BAL-001`. Only Layer C
mapping records and the portable export boundary (§5) ever construct or
store this triple; Layer A records never need to know it exists. This
satisfies the instruction directly: "do not prematurely introduce
globally unique identifiers into every existing canonical record if a
qualified export/reference envelope can provide the necessary identity."

**Renamed/relocated objects**: a qualified reference pins a `local_id`
at a specific `revision`; if a project later renames or relocates the
referent, the mapping's own revision-pinning already makes the old
reference auditable against history rather than silently following the
rename — reconciliation (Phase 85's machinery, §11 below) is what
decides whether a mapping should be updated to a new local_id, never an
automatic rewrite.

**Missing/stale/unavailable external projects**: the project-identity
envelope and every mapping's verification status (§10) have an explicit
"insufficient evidence" / "stale" path — a project becoming unreachable
degrades a mapping's status, it never silently drops the mapping or
leaves it looking current.

### 3. Cross-project mapping model (Layer C record shape)

Relationship-type enum, deliberately smaller than the illustrative list
in the governing prompt — two of the suggested names were found, on
inspection, to overlap with other fields rather than naming a distinct
relationship shape, and are **not adopted as types**:

- `depends_on` — **not reused as a Layer C type.** Claims and
  Requirements already have a `depends_on` field with established,
  intra-project meaning (Phase 81); reusing the same name across a
  project boundary for a different kind of relationship risks exactly
  the ambiguity this ADR exists to prevent. A genuine cross-project
  dependency, if evidenced, is represented as `extends` (directional) or
  left as a named future gap — not invented here without a real case to
  ground it.
- `unverified_against` — **not a relationship type.** "Unverified" is
  not a *shape* of relationship, it is the *absence* of verification
  evidence for whatever relationship is actually being claimed —
  represented by `verification_status: insufficient_evidence` (§10),
  orthogonal to `relationship_type`. Keeping it as a type would let a
  record claim a relationship shape and its own absence of evidence in
  the same field, which is the "collapse into a misleading score" the
  governing prompt explicitly warns against.

**Adopted types**, each with explicit directionality:

| Type | Directionality | Meaning |
|---|---|---|
| `equivalent_to` | symmetric (one record, ordered pair, independently evidenced — never inferred from terminology) | Outcomes match under the stated tested conditions. |
| `partially_equivalent_to` | symmetric | Outcomes match under some conditions; `permitted_differences` is a **mandatory** field when this type is used. |
| `differs_from` | symmetric | A purely descriptive, non-judgemental recorded difference. |
| `extends` | directional (A extends B) | A's semantics are a strict superset of B's, evidenced, not assumed. |
| `implements_concept` | directional, **target must be a Layer B Domain Concept, never another project's Layer A record** | Disambiguates "project implements abstract concept" from "project A's behaviour matches project B's behaviour," which is `equivalent_to`/`differs_from` instead. |
| `unsupported_by` | directional (capability of A is unsupported_by B) | B has no analogous capability; a negative claim, not a hidden "insufficient evidence." |

**No assumed symmetry or transitivity beyond what's listed above as
symmetric by definition.** A chain (A `equivalent_to` B, B
`equivalent_to` C) never auto-implies A `equivalent_to` C — a derived
third mapping, if ever produced, is its own record, independently
evidenced or explicitly flagged `derived` with correspondingly weaker
confidence, never silently assumed.

Every mapping record also carries: `source_ref`/`target_ref` (qualified
references, §2), `concept_ref` (optional, Layer B), `version_applicability`
(per side), `scope`, `preconditions`, `permitted_differences` (mandatory
for `partially_equivalent_to`), `evidence` (list, cites both sides),
`verification_results` (oracle references, §10), `lifecycle_status`
(`candidate|accepted|conflicting|stale` — the review-workflow state) and
`verification_status` (§10's own five-value epistemic result — kept
**separate from** `lifecycle_status`, since a mapping can be `accepted`
as the team's working position while its `verification_status` is
honestly `insufficient_evidence`), plus ordinary provenance/review
history fields matching Phase 81's existing conventions.

### 4. Phase 82's `epistemic_source` field is corrected, not broadened

Reviewing §4 of `planning/phase-82-contract-and-evidence-foundation.md`
against this amendment's own requirement finds a real, pre-existing
design gap, independent of federation: **intended, observed, and
verified are not mutually exclusive.** A single Claim can simultaneously
be an accepted maintainer intent, exhibited by the implementation, *and*
confirmed by a passing oracle result under specified conditions — the
original four-value closed enum forced a single pick among states that
actually compose.

**Smallest backward-compatible correction** (Phase 82 is not yet
implemented — this corrects the plan before any code exists, so there is
no live migration, only a plan amendment):

- `epistemic_source` becomes a value on an **ordinal scale**
  (`intended < observed < verified`), recording **the strongest
  grounding reached so far**, not an exclusive pick — `verified`
  already subsumes `observed` subsumes `intended` by construction (you
  cannot verify a behaviour that isn't also observed; you cannot verify
  a Requirement's own behaviour without that Requirement already being
  `intended` by definition of being a Requirement at all). No new field
  is added; the enum's fourth value changes.
- **`uncertain` is removed from this enum.** It was never a peer value
  — a Claim can be `verified` under one set of conditions while still
  being contested about whether those conditions generalise, which the
  original four-value design could not express at all. Uncertainty and
  conflict already have a home: the existing `status` field
  (`proposed|supported|contradicted|superseded|verified`, unchanged).
  Keeping both an `epistemic_source: uncertain` value and a `status:
  contradicted` value invites exactly the double-encoding ambiguity this
  whole amendment exists to prevent.
- **`epistemic_source` is explicitly scoped to project-local grounding
  only.** It says nothing about cross-project compatibility — that
  question lives entirely in a Layer C mapping's own
  `verification_status` (§10/§3). This scoping statement is the one
  genuinely new sentence Phase 82's plan needs; no schema change is
  otherwise required for federation-readiness.
- **This is a material schema decision requiring explicit maintainer
  approval before Phase 82 implementation begins**, same as the
  original `epistemic_source` proposal already required
  (`planning/phase-82-contract-and-evidence-foundation.md` §9).

Phase 82's own one-contract vertical slice, pinned Ledgerkit scenario,
oracle schema, and exit gate are **unchanged** by this correction — it
touches exactly one enum's values and their documented meaning.

### 5. Portable export boundary (designed now, not built)

A stable, versioned, static-file export format — JSON, consumable
without a running `codecompass` process (the Wiki's own stated
requirement) — carrying: one project-identity envelope (§2) + that
project's Layer A records (or stable references to them) + Phase 81's
already-existing rendered Markdown projections + an explicit schema
version field from the start (this project's own established Phase
81B/Amendment-5 lesson: add the version field on day one, never retrofit
it after multiple undated exports already exist, `decisions/0077`).
Mapping datasets (Layer C) export **separately** from any single
project's own snapshot — a third party can publish a Ledgerkit↔hledger
mapping dataset without write access to, or even a current checkout of,
either project's own repository. **This format is specified at the
level of a schema sketch by this ADR; it is not implemented** — building
it is Post-v2 Stage 1 (§6).

### 6. Post-v2 Cross-Project Semantic Overlay track — explicitly gated

Full stage detail, dependencies, risks, and falsifiable exit gates:
`planning/post-v2-cross-project-overlay-backlog.md`. Seven candidate
stages (portable snapshot/identity proof → Ledgerkit/hledger comparison
→ Ledger compatibility/differential verification → backend-independent
Ledgerkit API implications → natural-language query model implications
→ read-only federated Wiki visualisation → Beancount/unrelated-domain
generalisation) are **proposals, not authorised implementation phases**.
None is numbered into the mandatory Phase 82-88 sequence; none blocks
Phase 88's own v2.0 release.

## Alternatives considered

- **Add a global UUID to every existing and planned canonical record
  now**, so any record is federation-addressable from day one. Rejected:
  the governing prompt explicitly asks this be avoided if a qualified
  export envelope can do the job, and it can — per §2, zero existing or
  Phase-82-planned record needs to change.
- **Keep `epistemic_source` as a single exclusive four-value enum and
  add a separate new field for the cross-project dimension instead.**
  Rejected: the real defect (intended/observed/verified are not
  mutually exclusive) exists independent of federation and would
  surface the first time Phase 82 tried to record a Claim that was both
  `observed` and `verified` — fixing the ordinality is the smaller,
  more defensible change than bolting on a second field to work around
  an already-wrong first one.
- **Merge Layer A projects into one shared ontology immediately for
  Ledgerkit/hledger**, since both are already locally available.
  Rejected: explicitly prohibited by the governing prompt's own §3 and
  §12 ("do not create... a complete universal accounting ontology");
  Layer B's Domain Concepts stay optional and minimal, populated only as
  Post-v2 Stage 2 actually needs them.
- **Treat Ledger/Beancount's repository and licence state as already
  known**, reusing general knowledge instead of verifying. Rejected: no
  local checkout of either exists in this environment; this ADR
  explicitly records that gap rather than asserting unverified licence
  terms.

## Consequences

- `planning/v2-roadmap.md` gains federation-compatibility review notes
  on Phases 82-88 (none change scope or exit gate) and a pointer to the
  new Post-v2 track.
- `planning/phase-82-contract-and-evidence-foundation.md` gains an
  amendment section correcting `epistemic_source` per §4 above —
  requires the same maintainer approval its original proposal already
  required, not a new, separate approval gate.
- `planning/post-v2-cross-project-overlay-backlog.md` is a new file
  recording the seven-stage track, its risks, and its non-goals.
- No `src/codecompass/` or `context-graph.db` change is made by this
  ADR. No repository is created. No Phase 82-88 phase is renumbered,
  expanded, or implemented.
- If a future stage's real evidence shows the Layer C type enum, the
  qualified-reference envelope shape, or the epistemic-scale correction
  is wrong, that stage's own plan supersedes the relevant part of this
  ADR with a new numbered decision, per `CLAUDE.md` §2's append-only
  convention — this ADR does not pre-commit the eventual implementation
  to its own current sketch.
