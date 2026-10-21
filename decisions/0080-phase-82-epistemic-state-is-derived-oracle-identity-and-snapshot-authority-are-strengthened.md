# 0080. Phase 82's epistemic state is a derived view, not a persisted field; oracle-result identity is bound to the exact tested subject; cross-project snapshot authority is distinguished from project identity

## Status

Accepted (2026-10-21, direct user request — "CodeCompass v2 — Corrective
Planning Amendment"). Corrects `decisions/0078`'s original
`epistemic_source` proposal and `decisions/0079` §4's own ordinal-scale
correction of it (both preserved unedited as the historical record of
what was proposed and why, per `CLAUDE.md` §2's append-only convention —
neither file is edited by this ADR). Extends, does not reverse,
`decisions/0079` §2's project-qualified reference envelope.

## Context

**Verified current state**: `HEAD` was exactly `47ab61c` before this
amendment, confirmed against the stated starting commit with zero
drift. Phase 82 remains `planned`, not implemented — no `src/
codecompass/` or `context-graph.db` change has been made by any v2
planning session to date.

Direct review of `decisions/0079` §4 (the prior correction) against
concrete examples found the correction itself still wrong, independent
of federation: an **ordinal** scale (`intended < observed < verified`)
still forces a single value where the real relationships are
independent, not merely non-exclusive-but-orderable. Three concrete
counter-examples, each expressible in real terms using this project's
own domain (Ledgerkit rounding behaviour):

- **Verified but not intended**: Ledgerkit's `reports.py` demonstrably
  rounds using a particular method, confirmed by a real, independently
  executed test — but no `REQ-`/`DEC-` record has ever accepted that
  rounding as the intended business rule. An ordinal scale would force
  this to read `verified` (correctly) but gives no way to also say
  "not actually intended by anyone" — the scale's own `intended <
  observed < verified` ordering implies `verified` *subsumes*
  `intended`, which this example directly falsifies.
- **Intended but contradicted**: a `REQ-` record specifies half-even
  rounding (`status: approved`); real implementation evidence shows
  half-up rounding instead. The requirement is genuinely intended; the
  observed behaviour contradicts it. No single ordinal value captures
  "intended AND contradicted" simultaneously.
- **Partially verified**: a contract passes under integer inputs,
  untested or failing under fractional inputs. A single field,
  ordinal or not, cannot represent "verified under scope A, not under
  scope B" without either losing the scope distinction or growing a
  second field anyway — at which point the field is not doing the job
  a derived, per-scope view already does better.

**Direct inspection of the actual Phase 81 implementation** (not only
its planning description, per this amendment's own instruction) finds
the overwhelming majority of what Phase 82 needs already exists and is
already exercised by a real, tested precedent for exactly this kind of
problem:

- `src/codecompass/knowledge_intermediate.py::derive_provenance_label`
  already computes a label (`OBSERVED`/`DECLARED`/`DECIDED`/`DERIVED`/
  `HISTORICAL`/`MIXED`/`UNCLASSIFIED`) **purely from existing kind/
  basis/status fields, as a read-time function, not a persisted field**
  — and was itself corrected twice (`decisions/0073` point 8,
  `decisions/0074`) specifically for guessing a relationship instead of
  walking the real `observations:`/`decision:` citation fields. This is
  the direct, already-proven precedent this ADR's own correction
  follows, not a new idea.
- `Requirement.status` already has the enum `proposed|approved|
  implemented|verified` (`scripts/check_knowledge_base.py`,
  `_STATUS_ENUMS`) — `approved` already *is* "accepted intent";
  `verified` already *is* a terminal state meaning "independently
  confirmed," already present on both Requirement and Claim records
  before this ADR. **Nothing about INTENDED or the general shape of
  VERIFIED needed inventing** — what was actually missing is a
  mechanical rule for *when* a record may legitimately reach
  `status: verified`, which today is open text an author can set by
  hand with no check at all.
- `Claim.evidence_support_state` already has the enum `supported|
  partially_supported|unsupported|conflicting` (`check_knowledge_base.py`
  `_OPTIONAL_ENUM_FIELDS`) — `conflicting` already *is* the
  "uncertain/conflicting" state the governing prompt asks for.
- `Evidence` already carries `source_ref`/`doc_ref`/`test_ref`
  (`docs/concepts/knowledge-model.md`) — a `test_ref` citing a real
  oracle-result file is a direct, zero-schema-change way to link a
  Claim's existing `supporting_evidence` chain to Phase 82's new oracle
  mechanism.
- `check_requirement_cites_approved_decision`
  (`scripts/check_knowledge_base.py:475`) is the direct, already-shipped
  precedent for *this ADR's own* new validator: a mechanical rule that a
  record's status field may only take a given value when a real, cited,
  correctly-stated linked record actually supports it — not a new kind
  of check, the same kind, on a new citation path.

**Root cause of both defects this ADR corrects**: Phase 82's original
design (`decisions/0078`) and its first correction (`decisions/0079`)
both treated "how grounded is this statement" as a single scalar
property of one record, when it is actually **three independent
predicates over three separable record relationships** (does an
approved Requirement/Decision exist; does supported Observation/Evidence
exist; does a passing, scope-bound oracle result exist) — a design error
the project's own `derive_provenance_label` precedent had already
solved for a structurally identical problem (provenance classification)
four phases earlier, which this amendment's review simply had not yet
connected to Phase 82's own, independently-invented field.

## Decision

### 1. `epistemic_source` is removed entirely. No new field is added to any existing or Phase-82-planned record.

INTENDED, OBSERVED, VERIFIED, and CONTESTED/UNCERTAIN are each computed,
on demand, from already-existing fields plus Phase 82's own new oracle-
result citations — never persisted as a single field on a Claim or
Requirement:

- **INTENDED** — true iff a `REQ-` record with `status` ∈
  `{approved, implemented, verified}` exists for this contract, or a
  `DEC-` record with `status: approved` exists and is cited (directly
  mirrors `derive_provenance_label`'s own existing `DECIDED` branch,
  `knowledge_intermediate.py:901-909`).
- **OBSERVED** — true iff a `CL-` record's `basis` is
  `observed_behaviour`, or `directly_stated` resolving through
  `supporting_evidence` → a real Evidence record's own `observations:`
  field → a real Observation record (the exact existing walk
  `derive_provenance_label` already performs, `knowledge_intermediate.py:
  925-955` — reused, not reimplemented, by the new function below).
- **VERIFIED** — true, **for a specific scope/condition set**, iff at
  least one `EV-` record cited via `supporting_evidence` has a
  `test_ref` resolving to a real `oracle-result.yaml` (§2 below) whose
  `outcome` is `PASS` and whose `tested_subject_digest` matches the
  contract's own current implementation digest. **Verification is
  always scope-qualified** — a Claim can be verified for scope A and
  unverified (or contradicted) for scope B simultaneously; there is no
  single "is this Claim verified" boolean.
- **CONTESTED/UNCERTAIN** — true iff `status: contradicted`,
  `evidence_support_state: conflicting`, or a non-empty
  `contradicting_evidence` list — all already-existing fields, unchanged.

**None of these four predicates implies another.** A Claim can be
VERIFIED and not INTENDED (the rounding example); INTENDED and
CONTESTED (the contradicted-requirement example); VERIFIED-for-scope-A
and not-VERIFIED-for-scope-B simultaneously (the partial example). This
is the structural fix: the prior two proposals each forced at least one
of these implications by construction; a set of independently-computed
predicates cannot.

**New code, not new schema**: `knowledge_intermediate.py` gains one new
function, `derive_epistemic_profile(record, records_by_id,
oracle_results) -> EpistemicProfile` (a small dataclass: `intended: bool`,
`observed: bool`, `verified_scopes: list[str]`,
`known_gap_scopes: list[str]`, `contested: bool`) — a sibling to
`derive_provenance_label`, reusing its existing id-resolution helpers
rather than duplicating them. This is a read-time projection function,
exactly like its sibling; it persists nothing.

### 2. Oracle-result identity is bound to the exact tested subject, not merely a commit reference

`oracle-result.yaml` (Phase 82's plan, §5) gains the following, beyond
what was previously proposed — each addresses one gap named by this
amendment's own governing instruction:

| Field | Purpose |
|---|---|
| `run_id` | Identifies this specific execution, independent of `baseline_id` (which may be cited by many runs) and `tested_subject_digest` (which may recur across runs against unchanged code). |
| `baseline_id` | Unchanged from the original proposal — the accepted reference state, minted only on explicit acceptance (`CLAUDE.md` §1 L-087, already specified). |
| `tested_subject_digest` | **The actual content hash of the exact files executed** — reusing Phase 81B's own `payload_tree_sha256`/`_canonical_digest_of_hashes` construction (`decisions/0077`, `scripts/prepare_cleanroom_branch.py`) applied to the oracle's own relevant source tree, **not a bare Git commit SHA**. A commit SHA alone cannot distinguish a clean checkout from a dirty worktree with uncommitted changes; a content digest of what was *actually read and executed* can, and fails closed if it cannot be computed. |
| `oracle_contract_id` + `oracle_contract_content_hash` | The accepted contract and checks actually executed, by content, not merely by name (direct continuation of the already-proposed tamper-detection mechanism, now made an explicit field on the result itself rather than only a side validation). |
| `test_input_digest` | Content hash of the exact fixture/input data used — a contract can stay unchanged while its fixture quietly drifts; this makes that drift independently detectable. |
| `environment_descriptor` | Optional — recorded only where material (e.g. a language/runtime version that could plausibly change the outcome). Never fabricated when not material; absence is not a defect. |
| `raw_output_sha256` | Content hash of the file `raw_output_ref` points to — the raw evidence itself must be tamper-evident, not just referenced. |
| `scope` | The specific conditions this result actually covers (already implied by the original design's "under recorded conditions" language; now an explicit, required field precisely because VERIFIED is now scope-qualified, §1). |
| `outcome`, `executed_at`, `invalid_reason` (when `INVALID`) | Unchanged from the original proposal. |

**New validator rule**: `check_verified_status_cites_passing_oracle_result`
(mirrors `check_requirement_cites_approved_decision`'s own existing
pattern exactly) — a Claim/Requirement's derived VERIFIED predicate for
a given scope is computed, never trusted from a hand-set field, so this
rule exists to catch a *different* problem: a stale or dangling
`test_ref` citation that no longer resolves to a real, matching
oracle-result is reported as a finding, not silently ignored.

**What Phase 82 does and does not protect against** (the governing
prompt's own required distinction): Phase 82 delivers the *schema* and
*mechanical cross-reference validation* — a result can be shown
internally inconsistent (digest mismatch, missing raw evidence,
dangling citation) after the fact. **Phase 82 does not, by itself,
prevent a sufficiently motivated author from hand-computing consistent-
looking hashes for a fabricated run** — nothing in Phase 82 executes
anything inside an environment the record's own author cannot write to.
That protection is Phase 83/84's own mechanically isolated execution
boundary (reusing Phase 81B's broker/sandbox precedent, where the
checker runs somewhere the evaluated agent cannot reach), not yet built.
**Content hashes establish internal consistency and tamper-evidence,
never independent execution or trusted authorship on their own** — this
sentence is now explicit in Phase 82's own plan (§5) precisely so a
future reader does not overclaim what Phase 82 alone delivers.

### 3. Project-identity envelope distinguishes identity from authority

`decisions/0079` §2's `(project_id, revision, local_id)` triple is
extended (not reversed) with:

- **`publisher_id`** — who produced *this snapshot*, distinct from
  `project_id` (the software project the snapshot is *about*). A
  snapshot of `hledger` published by someone who is not an `hledger`
  maintainer has `project_id: hledger`, `publisher_id:` whoever actually
  ran the reconstruction.
- **`authority`** — closed enum `self-published | third-party-
  reconstruction | unknown`, defaulting to `unknown` when not
  affirmatively established, **never silently defaulting to an
  authoritative-sounding value**. `self-published` requires an
  independently checkable fact (e.g. the snapshot was produced from
  inside the project's own repository, by its own maintainers' tooling,
  or carries the project's own explicit sign-off) — a CodeCompass-run
  reconstruction of a project CodeCompass does not maintain is
  `third-party-reconstruction` by construction, regardless of how
  rigorous the reconstruction's own evidence is.
- **`content_digest`** — unchanged in spirit from the original proposal,
  now named explicitly alongside `publisher_id`/`authority` so the four
  concerns (who published it, what it's about, what state it reflects,
  whether it's intact) are visibly four separate fields, not folded
  together.

**This refinement is specified now, implemented only when Post-v2 Stage
1 (portable snapshot export) is actually built** — no existing or
Phase-82-planned record changes; the envelope remains entirely external
to project-local knowledge, exactly as `decisions/0079` §2 already
established.

## Alternatives considered

- **Keep the ordinal scale, add a fourth "partial" value.** Rejected:
  "partial" still collapses an inherently per-scope property into one
  field; the moment two different scopes have different outcomes, a
  single value cannot represent both without losing information a
  derived, per-scope view preserves for free.
- **Add `epistemic_source` as a list of independent flags on the Claim
  itself (e.g. `epistemic_flags: [intended, verified]`), rather than
  removing the field.** Rejected: this still duplicates information
  already derivable from existing `status`/`basis`/linked-record fields
  for INTENDED and OBSERVED, violating this project's own
  `conditional-generalisation.md` "smallest model" discipline and this
  amendment's own explicit instruction to avoid duplicating `status`/
  `evidence_support_state`/`basis`/`contradicting_evidence`. Only
  VERIFIED's scope-qualified oracle linkage is genuinely new, and it is
  better represented by a citation (Evidence → oracle-result) than a
  flag, since a citation carries the actual supporting record, not just
  an assertion that one exists.
- **Make `authority` a property the publishing party can set to
  whatever they like.** Rejected: this would let a third-party
  reconstruction simply claim `self-published` — `authority` is useful
  only if establishing `self-published` requires an independently
  checkable fact, named above, deferred to Stage 1's own implementation
  to specify precisely.

## Consequences

- `planning/phase-82-contract-and-evidence-foundation.md` §4 is rewritten
  (not merely re-amended in place) to describe the derived-view design;
  §5 gains the oracle-result identity fields above; §9/§10/§11 updated
  to match; a new §13 records this amendment's own rationale and
  supersession chain.
- `planning/v2-roadmap.md`'s Phase 82 federation-review entry is updated
  to reflect the field's full removal.
- `planning/post-v2-cross-project-overlay-backlog.md` gains the
  `publisher_id`/`authority` distinction wherever the project-identity
  envelope is referenced, and Stage 2/5/7 corrections (recorded in that
  file directly, not restated here).
- No `src/codecompass/` file is modified by this ADR — `knowledge_
  intermediate.py::derive_epistemic_profile` and `check_knowledge_base.
  py::check_verified_status_cites_passing_oracle_result` are Phase 82's
  own future implementation work, specified here, not built now.
- `decisions/0078` and `decisions/0079` are not edited. A future reader
  encountering either should treat this ADR as the current, authoritative
  design for the epistemic dimension and the project-identity envelope's
  authority field; `decisions/0079`'s own mapping-type enum and Layer
  A/B/C structure are otherwise unaffected and remain current.
