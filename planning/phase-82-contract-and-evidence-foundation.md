# Phase 82: Contract and Evidence Foundation — plan

**Status:** planned (2026-10-21, direct user request, part of the v2
strategic realignment — `decisions/0078`, `planning/v2-roadmap.md`).
**Planning only. Implementation is not begun and requires explicit
maintainer approval of §4's schema delta (as corrected by §12), §9's
open decisions, and §12's own federation-review finding before any code
is written**, per the governing prompt's own instruction ("Do not begin
Phase 82 implementation") and `CLAUDE.md` §1. **Amended same day,
2026-10-21, direct user request** ("CodeCompass v2 Planning Amendment —
Cross-Project Semantic Overlays," `decisions/0079`): §4's
`epistemic_source` design is corrected (§12) after review found its
four values were not actually mutually exclusive; no other section of
this plan changes.

## 0. Verified current state (read live, not assumed)

- `src/codecompass/knowledge_intermediate.py` (Phase 81) implements the
  only existing epistemic-record machinery: a flat-record parser for
  `planning/knowledge/<slug>/` canonical Observation (`OBS-`)/Evidence
  (`EV-`)/Claim (`CL-`)/Derivation (`DE-`)/Decision (`DEC-`)/Requirement
  (`REQ-`) records. Claim fields today: `status`
  (`proposed|supported|contradicted|superseded|verified`),
  `assertion_kind`
  (`definition|relationship|rule|invariant|state_transformation|
  boundary|workflow|constraint`), `basis`, `examples`,
  `counterexamples`, `depends_on`, `open_questions`,
  `evidence_support_state` — confirmed by direct read of
  `knowledge_intermediate.py`'s own module docstring and
  `scripts/check_knowledge_base.py`'s field-validation table this
  session, not assumed from prior planning prose.
- No `src/codecompass/` module, test, or `pyproject.toml` dependency
  implements or references a contract, an oracle, or a change-impact
  concept — confirmed by `grep -r` across `src/` this session (zero
  matches).
- No MCP dependency exists in `pyproject.toml`'s `dependencies` list
  (`typer`, `rich`, `anthropic`, `pipdeptree`, `pyyaml` only) — Phase 82
  does not need one; Phase 84 will.
- `~/projects/ledgerkit` is a real, independent sibling checkout with
  its own `tests/`, `dev-docs/`, `knowledge/`, `ledgerkit/reports.py`,
  `ledgerkit/query/parser.py`, `ledgerkit/cli.py` — confirmed present
  and non-empty this session. Already CodeCompass's established
  reference project (Phases 45-78).
- Current ADR count: `0077`. Next: `0078` (consumed by `decisions/0078`,
  the strategic ADR this plan implements under). No further ADR number
  is pre-reserved by this plan; schema-delta decisions below each name
  whether they need their own ADR at implementation time.
- No `context-graph.db` schema version change is proposed by this plan
  (schema stays at whatever version Phase 77/76 last left it — not
  independently re-verified here since nothing in this plan touches
  that database).

## 1. Scope

Establish, for exactly **one real Ledgerkit function**, the smallest
complete vertical slice of: a versioned behavioural contract record →
links to canonical knowledge and implementation evidence → explicit
INTENDED/OBSERVED/VERIFIED/UNCERTAIN status → a minimal oracle contract/
result schema → a pinned reference scenario → a baseline run identity →
deterministic validation/provenance checks. Every later v2 phase cites
this slice as its concrete substrate — if it does not work end to end
here, nothing downstream has anything real to build on.

**In scope:**

- A behavioural-contract record format (§3).
- The INTENDED/OBSERVED/VERIFIED/UNCERTAIN dimension, as a genuinely
  separate axis from the existing `status` field (§4).
- A minimal oracle-contract schema (what must be checked) and
  oracle-result schema (what was found: PASS/FAIL/GAP/INVALID) (§5).
- One pinned Ledgerkit reference scenario, with a real, demonstrably
  failing negative control (§6).
- Baseline run identity and the minimal telemetry needed to tell "this
  oracle run used this accepted baseline" apart from "a run happened"
  (§7).
- Deterministic validation (schema-shape, cross-reference integrity,
  provenance) for every new artifact kind (§8).

**Explicitly deferred (not this phase):**

- Any traversal from source changes to affected contracts (Phase 83).
- Any MCP exposure of any of this (Phase 84).
- Any multi-contract aggregate report (Phase 83).
- Any new `context-graph.db` table or column (this phase is file-based,
  mirroring how Phase 81's own knowledge layer stayed file-based before
  any graph integration was shown necessary).
- Any actual execution-provider integration beyond a manual/scripted
  `pytest` invocation (property tests, golden tests, static checkers —
  Phase 83/84 territory once the schema is proven against one provider).
- Picking the final oracle contract/result file location as anything
  other than `planning/contracts/<slug>/` — the directory name is not
  binding on later phases if a better convention emerges from real use.

## 2. Why Ledgerkit's `balance_from_spec`

`ledgerkit/reports.py::balance_from_spec` is already a known, previously
studied real function (Phase 78's second Ledgerkit trial independently
derived the real `parser.py → Journal → reports.py::balance_from_spec →
cli.py` producer/consumer chain, confirmed against the real schema).
Reusing an already-understood function means Phase 82's own evidence-
citation work is checking a contract-authoring mechanism, not
re-discovering Ledgerkit's architecture from zero — a different, already
largely de-risked, question. The exact chosen scenario (which report
spec, which expected balance) is confirmed against the real
`tests/test_reports.py` fixtures at implementation time, not invented
here; if `balance_from_spec` turns out unsuitable on closer inspection,
substituting a different, equally-real Ledgerkit function is an
implementation-time adjustment that does not require re-planning this
phase, provided the substitute is named and justified in the same way.

## 3. Behavioural contract record format

A contract is a **new Claim/Requirement pairing convention**, not a new
record kind — reusing the existing `REQ-`/`CL-` ID prefixes and parser
(`conditional-generalisation.md`'s "smallest model" discipline, already
applied at Phase 54c's original design and Phase 79's extension). A
contract is:

- One `REQ-<slug>-NNN` record carrying the contract's own identity:
  stable slug, human name, version-applicability (which Ledgerkit
  revision(s) this applies to — reuses the existing `depends_on`
  field's list form for any sub-requirements), the obligation statement
  itself.
- One or more `CL-<slug>-NNN` Claims hung off it via existing
  `depends_on` back-references, each carrying one specific precondition,
  expected outcome, constraint, or edge case — not one giant Claim
  trying to say everything, matching how Claims are already used
  elsewhere in `planning/knowledge/`.
- Evidence (`EV-<slug>-NNN`) records citing the exact `source_ref`
  (file path, and — new requirement this phase adds, see §8.3 — a line
  range or symbol-occurrence identifier, not a bare file path) backing
  each Claim.

This reuses the existing flat-record text format
`check_knowledge_base.py`/`knowledge_intermediate.py` already parse —
no new file format, no new parser, only new optional fields (§4) and a
new validation rule (§8).

## 4. INTENDED / OBSERVED / VERIFIED — the schema delta (corrected 2026-10-21, §12)

**Decision required from the maintainer before implementation**
(`decisions/0078`'s Decision point 1 established *that* this must be a
separate axis from `status`; this plan proposes the concrete mechanism.
**This section was corrected same-day, pre-implementation, by the
federation-review amendment — see §12 for why**: the original four-value
closed enum treated `intended`/`observed`/`verified` as mutually
exclusive, which they are not — a Claim can be all three at once.):

Add one new optional field, `epistemic_source`, to Claim and Requirement
records — **an ordinal scale, not an exclusive pick**, recording the
*strongest grounding reached so far*: `intended < observed < verified`.
`verified` subsumes `observed` subsumes `intended` by construction (a
verified behaviour is necessarily also observed; a Requirement's
behaviour cannot be verified without the Requirement itself already
being `intended` by definition of being a Requirement at all) — so a
single ordinal value correctly represents "at least this much grounding
exists," never forcing a false choice between states that actually
compose.

- `intended` — an accepted maintainer/product requirement, nothing more
  yet. A `REQ-`-prefixed record with no linked passing oracle result
  defaults here implicitly if the field is absent (backward-compatible
  with every existing Requirement record — **zero migration required**,
  matching Phase 81's own "zero new persisted fields on existing
  records" discipline as closely as this genuinely new concept allows).
- `observed` — behaviour the implementation or a runtime trace exhibits,
  with no accepted check yet confirming it under defined conditions.
- `verified` — behaviour a named oracle-result record (§5) demonstrates
  PASS for, under recorded conditions. **This value may only be set by
  a reconciliation step that reads a real oracle-result record** — never
  hand-set by an agent, mirroring `decisions/0072`'s existing rule that
  an `aligned` comparison finding never auto-promotes a Claim's `status`
  to `verified` on its own. The same non-conflation rule applies here:
  an AI-generated statement never becomes `epistemic_source: verified`
  through reconciliation alone, only through a cited, real,
  independently-executed oracle result.

**`uncertain` is not a value of this field** (removed by the §12
amendment). Contested or conflicting evidence already has a home: the
existing `status` field (`proposed|supported|contradicted|superseded|
verified`, unchanged) — a Claim can be `epistemic_source: verified`
(grounded under the specific conditions an oracle checked) while
`status: contradicted` (some other evidence now disputes it, or disputes
whether those conditions generalise). Keeping both an `epistemic_source:
uncertain` value and `status: contradicted` would double-encode the same
concern in two places, inviting drift between them.

**`epistemic_source` is scoped to project-local grounding only.** It
says nothing about whether this project's behaviour is compatible with
another project's — that question belongs entirely to a future
cross-project mapping record's own `verification_status`
(`decisions/0079`), never to this field. This scoping statement costs
Phase 82 nothing to add now and avoids the field being silently
overloaded later.

`status` keeps its existing meaning (confidence given current evidence)
entirely unchanged — `epistemic_source` and `status` are orthogonal and
both required to read a Claim correctly going forward (e.g. a Claim can
be `status: supported` + `epistemic_source: observed` — well-evidenced,
but nobody has run an accepted check against it yet).

**Validator change**: `check_knowledge_base.py` gains one new
closed-enum check for `epistemic_source` when present (now a 3-value
enum, `intended|observed|verified`), following the existing pattern at
its own `assertion_kind` validation
(`scripts/check_knowledge_base.py:172` area) — additive, not a rewrite
of existing checks.

## 5. Oracle contract and result schema

Two new, minimal, machine-readable file formats under
`planning/contracts/<slug>/`:

- **`oracle-contract.yaml`** — what must be checked for this contract:
  `contract_id` (the `REQ-` id), `execution_provider` (e.g. `pytest`,
  named explicitly rather than assumed — Phase 82 supports exactly one
  provider kind to prove the shape, not a provider-plugin system),
  `check_reference` (how to invoke it — a test node ID for `pytest`),
  `required` (bool — is this check mandatory for the contract to be
  considered checked at all, distinguishing a `GAP` from a merely
  optional nice-to-have check).
- **`oracle-result.yaml`** — one per run: `contract_id`, `baseline_id`
  (§7), `outcome` (`PASS|FAIL|GAP|INVALID` — the governing prompt's
  exact four values), `executed_at`, `execution_provider`,
  `raw_output_ref` (a path to the captured raw tool output, for
  independent re-inspection — never only a summary string), and, for
  `INVALID`, a mandatory `invalid_reason` field (the environment,
  configuration, or evidence that made the run unreliable — `INVALID`
  without a reason is itself a validation failure, see §8.4).

**`GAP` vs `FAIL` vs `INVALID`, concretely, so the distinction is
checkable, not just prose**: `FAIL` requires the check to have actually
run and produced a negative result; `GAP` requires the check to be
`required: true` in the oracle contract but to have no corresponding
`oracle-result.yaml` at all, or one whose `outcome` the validator cannot
itself confirm matches a real run (§8.4); `INVALID` requires an explicit,
named reason the *environment* (not the code under test) is untrusted.
A successful run is never presented as proof of an untested behaviour —
concretely, the oracle-result schema has no field that could be
mistaken for "everything is fine" in the absence of a contract-specific
`PASS`.

**Protection from the evaluated agent**: `oracle-contract.yaml` files
are the "accepted checks" the governing prompt requires be protected —
Phase 82's own deterministic validation (§8) includes a check that an
`oracle-contract.yaml`'s own content hash (recorded at authoring time by
a human/maintainer-approved commit, not by the coding agent under
evaluation) is unchanged at result-recording time; a changed contract
with no corresponding new maintainer-approved commit fails validation
closed. (The *mechanism* enforcing this at execution time — e.g. running
the oracle check outside the coding agent's own working tree, closer to
Phase 81B's broker/sandbox model — is Phase 83/84's concern once there
is a real agent-facing execution path; Phase 82 proves the schema can
represent and detect tampering, not that an agent has been kept away
from it yet.)

## 6. Pinned Ledgerkit reference scenario and negative control

- **Positive scenario**: one real, currently-passing Ledgerkit test (or
  a new, equally-real fixture scenario if none currently isolates
  `balance_from_spec` cleanly enough — confirmed/chosen at
  implementation time against the real `tests/test_reports.py`) is
  named as `balance-from-spec`'s `check_reference`. Running the oracle
  against it today must produce `PASS`.
- **Negative control** (the exit gate's own explicit requirement): a
  deliberately, minimally incorrect version of `balance_from_spec` (or
  an equivalent fixture mutation) must cause the same oracle contract to
  report `FAIL` — proving the oracle actually discriminates, not merely
  echoes a cached green result. This mutation is applied to a disposable
  scratch copy of the Ledgerkit checkout, never committed to the real
  `~/projects/ledgerkit` repository.

## 7. Baseline run identity and telemetry

A `baseline_id` (content hash of the pinned reference scenario's own
input: the exact Ledgerkit revision + the oracle-contract's own content
hash) identifies which "known-good" state an oracle result is measured
against. Per `CLAUDE.md` §1's L-087 (a persisted last-known-state may
advance only on an explicit apply/acknowledgement action, never merely
because a detection/scan step ran): **a `baseline_id` is recorded only
when a human or an explicit, separately-logged "accept this baseline"
step approves it — never automatically from the first oracle run that
happens to pass.** Running the oracle does not, by itself, mint or
advance a baseline; it only produces an `oracle-result.yaml` that may
later be cited by a baseline-acceptance action. This is the one place
in this phase most structurally similar to the class of mechanism L-087
was written about, so it is named explicitly rather than left implicit.

Minimal telemetry recorded per run: `executed_at`, `execution_provider`,
`baseline_id` (nullable — a run against no yet-accepted baseline is
still a valid, recordable run, just not yet "the" reference result),
wall-clock duration. Nothing beyond what §5/§8 already need — no new
metrics framework.

## 8. Deterministic validation and provenance checks

All additive to `scripts/check_knowledge_base.py` and a new, narrow
`scripts/check_contracts.py` (mirrors `check_knowledge_base.py`'s own
existing `--strict` convention rather than inventing a different CLI
shape):

1. **Schema-shape**: every `oracle-contract.yaml`/`oracle-result.yaml`
   has every required field, correctly typed, closed-enum fields
   restricted to their named values.
2. **Minimal-content edge case** (`CLAUDE.md` §1's L-070 requirement):
   an oracle-result file containing only the bare-minimum required
   fields and no optional content (e.g. `outcome: INVALID` with the
   shortest possible non-empty `invalid_reason`) must still validate
   successfully as well-formed, and a file missing even one required
   field must fail closed — both directions tested, not only the
   failure direction.
3. **Depth, not just scope** (`CLAUDE.md` §1's L-075 requirement): it is
   not sufficient that a Claim's `source_ref` field is merely present —
   the validator confirms the cited file path exists in the Ledgerkit
   checkout *and* the cited line range/symbol actually contains
   content consistent with what the Claim asserts (at minimum: the
   named function/symbol exists at that location) — a citation to a
   real file that doesn't actually contain the cited symbol must fail
   validation, not pass because the path merely resolves.
4. **Cross-reference integrity**: every `oracle-result.yaml`'s
   `contract_id` resolves to a real `REQ-` record and a real
   `oracle-contract.yaml`; every `INVALID` outcome has a non-empty
   `invalid_reason`; every `GAP` determination is independently
   re-derivable by the validator itself from "required but no matching
   result," never trusted from a self-reported `outcome: GAP` value
   alone (the validator computes GAP, it does not merely echo it).
5. **Contract tamper detection**: an `oracle-contract.yaml` whose
   content hash does not match the hash recorded at its last
   maintainer-approved commit fails closed (§5's protection mechanism,
   checked mechanically here).

## 9. Open decisions requiring explicit maintainer approval

1. **The `epistemic_source` field name and its ordinal three-value
   enum** (§4, corrected by the §12 federation-review amendment from an
   originally-proposed, incorrectly-exclusive four-value design) — the
   single genuinely new schema concept this phase introduces.
   Alternative names considered: `provenance_kind` (rejected — collides
   in spirit with the already-established, differently-scoped
   mechanical-vs-inferred "provenance" vocabulary from `decisions/0051`/
   `0054`, which is about *how a fact was produced*, not *what kind of
   claim it is*); `claim_source`. Proceeding with `epistemic_source`
   unless the maintainer prefers otherwise.
2. **Whether `balance_from_spec` is the right pinned scenario**, or a
   different real Ledgerkit function should anchor Phase 82 instead —
   confirmed against the live fixture set at implementation time (§2).
3. **The MCP SDK/licence check named in Phase 84's roadmap entry** is
   not this phase's decision, but is flagged here so it is not
   forgotten when Phase 82 hands off.

## 10. Verification (how this phase is confirmed done)

- Deterministic unit tests for: the `epistemic_source` enum validator
  (valid values accepted, invalid rejected, absent field defaults
  correctly per record kind); the oracle-contract/oracle-result schema
  validators, including the minimal-content edge case (§8.2) and the
  depth check (§8.3); the baseline-identity non-auto-advance rule (§7) —
  a test that runs the oracle twice without an explicit acceptance step
  and confirms no `baseline_id` was minted either time.
- The real Ledgerkit positive scenario (§6) produces `PASS` when run
  against the current, unmodified `~/projects/ledgerkit` checkout.
- The real Ledgerkit negative control (§6) produces `FAIL` when run
  against a deliberately mutated scratch copy — this is the exit gate's
  own named requirement and must be demonstrated, not merely asserted
  possible.
- `check_contracts.py --strict` and `check_knowledge_base.py --strict`
  both report no findings against the one real contract this phase
  produces.
- Full existing test suite and `ruff` remain clean (no regression to
  anything Phase 81/81B already shipped).
- Standard `CLAUDE.md` §5 Definition of Done: retro, `knowledge-curator`
  triage of any candidate learnings this phase surfaces, independent
  `release-phase-auditor` pass against the exact commit, before
  `planning/ROADMAP.md` marks Phase 82 `done`.

## 11. Exit gate

A real Ledgerkit behavioural contract (`balance_from_spec`, or its
confirmed substitute) is traceable end-to-end — Requirement → Claims →
Evidence citing real source locations → an oracle contract → a real
`PASS` oracle result against the unmodified checkout → a real,
demonstrated `FAIL` against a deliberately introduced defect — with
every artifact passing deterministic validation, and with no claim of
`verified` status anywhere in the record set that isn't backed by an
actual, re-inspectable oracle result.

## 12. Amendment: federation-compatibility review and epistemic-model correction (2026-10-21)

Direct user request, same day as this plan's original authoring
("CodeCompass v2 Planning Amendment — Cross-Project Semantic
Overlays," `decisions/0079`). Two findings, both already folded into
§4/§9 above — this section records the amendment's own rationale and
audit trail, per this project's established convention of recording why
a pre-implementation correction happened, not only what changed.

**1. The `epistemic_source` correction is independent of federation.**
Reviewing §4 against the requirement that INTENDED/OBSERVED/VERIFIED
stay genuinely separate found that the original four-value closed enum
(`intended|observed|verified|uncertain`) treated these as mutually
exclusive states, when they are not: a Claim can simultaneously be an
accepted intent, exhibited by the implementation, and confirmed by a
passing oracle result. This would have surfaced as a real defect the
first time Phase 82 tried to record exactly that Claim, with or without
any cross-project concern — federation review simply found it first.
Corrected to an ordinal scale (§4); `uncertain` removed, its concern
already covered by the existing `status` field.

**2. Nothing else in this plan needed to change for federation-
readiness.** `decisions/0079`'s project-qualified reference envelope is
external to every record this phase creates — `REQ-`/`CL-`/`EV-` IDs,
the oracle-contract/oracle-result schema (§5), and the baseline-identity
model (§7) all stay exactly as originally designed. The only addition is
one scoping sentence in §4 (`epistemic_source` describes project-local
grounding only, never cross-project compatibility) — not a new field,
not a new file format, not a change to the exit gate. This confirms the
governing instruction was met: Phase 82 is not broadened, and its
one-contract vertical slice is not invalidated.

**3. No further maintainer approval gate is added** — the corrected
`epistemic_source` design falls under the same approval §9 already
requires for the field's original proposal.
