# Phase 82: Contract and Evidence Foundation — plan

**Status:** done (2026-10-21, direct user request — "CodeCompass
Orchestrator — Correct Phase 82 Plan and Proceed with Implementation").
Implementation explicitly authorised by that same governing prompt
(`decisions/0081` §5) — §9's prior approval gate was satisfied, not
bypassed. Independently audited: `release-phase-auditor` returned PASS
WITH NON-BLOCKING OBSERVATIONS (`planning/retros/_audit-phase-82.md`);
`docs-reconstructor`'s per-phase drift audit found and the lead fixed
three non-blocking doc-sync gaps (`planning/retros/_drift-audit-
phase-82.md`). Retro: `planning/retros/phase-82-contract-and-evidence-
foundation.md`.

**Amendment history** (full rationale in each amendment's own ADR — this
plan's own current content already reflects every correction below; §14
records the fullest, most recent one):

1. 2026-10-21, "CodeCompass v2 Planning Amendment — Cross-Project
   Semantic Overlays" (`decisions/0079`): §4's original four-value
   `epistemic_source` enum (`intended|observed|verified|uncertain`)
   corrected to an ordinal three-value scale — itself superseded by
   amendment 2.
2. 2026-10-21, "CodeCompass v2 — Corrective Planning Amendment"
   (`decisions/0080`, §13): the ordinal scale found still incorrect
   (intent/observation/verification are independent, not orderable) —
   `epistemic_source` **removed entirely**, replaced by a derived,
   read-time view over already-existing Phase 81 records (§4). Oracle-
   result identity strengthened to bind to the exact tested subject,
   not a bare commit reference (§5).
3. 2026-10-21, "CodeCompass Orchestrator — Correct Phase 82 Plan and
   Proceed with Implementation" (`decisions/0081`, §14): the single
   `check_reference`/`scope`/`required` design replaced by an explicit
   `checks:` collection (§5); PASS/FAIL/GAP/INVALID given a deterministic
   precedence/aggregation rule (§5a); vacuous verification (empty
   required-check set, absent contract, unresolvable evidence) is now
   structurally rejected, with a named, explicit compatibility policy for
   twelve pre-existing `status: verified` records this phase does not
   touch (§4); `tested_subject_digest`/`test_input_digest` scoped to
   named, reviewable file lists (§5b). Implementation proceeds in this
   same work session.

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
links to canonical knowledge and implementation evidence → an
independently-derivable INTENDED/OBSERVED/VERIFIED/CONTESTED view → a
minimal oracle contract/result schema → a pinned reference scenario → a
baseline run identity → deterministic validation/provenance checks.
Every later v2 phase cites this slice as its concrete substrate — if it
does not work end to end here, nothing downstream has anything real to
build on.

**In scope:**

- A behavioural-contract record format (§3).
- A derived, read-time INTENDED/OBSERVED/VERIFIED/CONTESTED view,
  computed from existing Phase 81 records plus Phase 82's own new
  oracle-result citations — **no new field on any Claim/Requirement
  record** (§4, `decisions/0080`).
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
no new file format, no new parser, and (per `decisions/0080`'s
correction) **no new field on any of these three record kinds at all** —
only a new derived view (§4) and a new validation rule (§8).

## 4. INTENDED / OBSERVED / VERIFIED / CONTESTED — a derived view, not a persisted field

**Corrected 2026-10-21 (`decisions/0080`) — this section replaces, not
amends, both the original four-value `epistemic_source` proposal and its
first, still-incorrect ordinal-scale correction.** Direct review against
concrete counter-examples (a legacy behaviour verified by test but never
accepted as intended; an accepted requirement contradicted by real
implementation evidence; a contract verified under some inputs and not
others) established that intent, observation, and verification are
**independent predicates over independent records**, not degrees of one
scale — no single field, ordinal or not, can represent "verified but not
intended" and "intended but contradicted" and "verified for scope A,
untested for scope B" all at once without losing information.

**No new field is added to any Claim, Requirement, Evidence, or
Observation record.** Direct inspection of
`src/codecompass/knowledge_intermediate.py` (not only its planning
description) found the needed structure already exists, already
exercised by a real, tested precedent for exactly this problem shape:
`derive_provenance_label` (`knowledge_intermediate.py:877-956`) already
computes a classification (`OBSERVED`/`DECLARED`/`DECIDED`/`DERIVED`/
`HISTORICAL`/`MIXED`/`UNCLASSIFIED`) purely from existing `kind`/`basis`/
`status` fields, as a read-time function — not a persisted field —
having itself been corrected twice (`decisions/0073`/`0074`) for
exactly the mistake of guessing a relationship instead of walking the
real citation fields. This phase's own correction follows that same,
already-proven pattern rather than repeating the mistake it fixed.

**The four predicates, each computed independently:**

- **INTENDED** — true iff a `REQ-` record exists with `status` ∈
  `{approved, implemented, verified}` (an enum this project's schema
  already has — `check_knowledge_base.py`'s `_STATUS_ENUMS["requirement"]`
  — unmodified by this phase), or a cited `DEC-` record has
  `status: approved`. This is the exact existing `DECIDED` branch
  `derive_provenance_label` already computes (`knowledge_intermediate.py:
  901-909`) — reused, not reimplemented.
- **OBSERVED** — true iff a Claim's `basis` is `observed_behaviour`, or
  `directly_stated` resolving through `supporting_evidence` to a real
  Evidence record whose `observations:` field resolves to a real
  Observation record — the exact existing walk
  `derive_provenance_label` already performs
  (`knowledge_intermediate.py:925-955`).
- **VERIFIED** — true **for a specific `scope`** iff at least one
  Evidence record cited via `supporting_evidence` has a `test_ref`
  resolving to a real `oracle-result.yaml` (§5) with `outcome: PASS`,
  matching `scope`, and a `tested_subject_digest` matching the
  contract's current implementation. **There is no single "is this
  Claim verified" boolean** — the view reports a set of verified scopes
  and a set of known-gap scopes separately, so a contract verified under
  some inputs and untested or contradicted under others is represented
  exactly as that, never collapsed to one answer.
- **CONTESTED** — true iff `status: contradicted`,
  `evidence_support_state: conflicting`, or a non-empty
  `contradicting_evidence` list — all pre-existing fields, unchanged.

**None of these four implies another.** VERIFIED does not imply
INTENDED (a legacy behaviour can be oracle-confirmed with no `REQ-`
record ever having accepted it as intended). INTENDED does not imply
OBSERVED or VERIFIED (an approved `REQ-` with zero linked Claims is
intended and nothing else). INTENDED and CONTESTED can both be true at
once (an accepted requirement a real observation contradicts). This is
the structural property the prior two designs each failed to have, by
construction — a derived view over independent sources cannot force an
implication a single field inevitably does.

**New code, not new schema**: Phase 82 adds one function,
`derive_epistemic_profile(record, records_by_id, oracle_results) ->
EpistemicProfile` — a small dataclass (`intended: bool`, `observed:
bool`, `verified_scopes: list[str]`, `known_gap_scopes: list[str]`,
`contested: bool`) — placed alongside and reusing
`derive_provenance_label`'s existing id-resolution helpers in
`knowledge_intermediate.py`, not duplicating them. It persists nothing;
it is called wherever a contract's epistemic state needs to be shown
(the eventual `codecompass knowledge` CLI surface, the rendered
Markdown projection) and recomputed each time, exactly like its sibling.

**`evidence_support_state` keeps its existing meaning, entirely
unchanged** — the derived view reads it, it does not reinterpret or
replace it.

**A real naming collision this review found, named explicitly rather
than papered over**: `Claim.status` and `Requirement.status` already
had a `verified` enum value *before* Phase 82 (`check_knowledge_base.py`
`_STATUS_ENUMS`), and `check_knowledge_base.py` has never checked what
that value actually requires — it is open, hand-set text today. Phase 82
**closes that previously-unenforced gap** rather than inventing a
second, differently-named concept: going forward, `status: verified` on
a record Phase 82's own validation reaches is only valid when it is
*fully* earned — **every `required: true` check in that contract's own
`oracle-contract.yaml` has a matching, current, `PASS` oracle-result**.
A Claim verified for some but not all of its own required scopes keeps
`status: supported` (or whatever `status` its evidence otherwise
earns), with the derived view's own `verified_scopes`/`known_gap_scopes`
split (above) surfacing the partial picture precisely — `status:
verified` is reserved for the case with no remaining required gap.

**Validator change**: `check_knowledge_base.py` gains one new check,
`check_verified_status_cites_passing_oracle_result`, mirroring the
existing `check_requirement_cites_approved_decision`
(`scripts/check_knowledge_base.py:475`) exactly in shape: for any
record whose `status` is `verified`, every `required: true` check named
in the contract's `oracle-contract.yaml` must resolve, via some Evidence
citation's `test_ref`, to a current, matching-scope, `PASS`
`oracle-result.yaml` — a record claiming `status: verified` with a
missing, stale, mismatched-scope, or non-`PASS` required check is a
validation finding, exactly as `check_requirement_cites_approved_decision`
already treats an unapproved cited Decision.

**Corrected 2026-10-21 (`decisions/0081` §3) — vacuous verification and
pre-existing records.** The check above fails closed, not vacuously
passes, on an empty or absent required-check set and on any `test_ref`
that fails to resolve to a real, schema-valid `oracle-result.yaml`.
**This check applies only to a record whose owning slug has a
`planning/contracts/<slug>/` directory at all.** Twelve pre-existing
`status: verified` records predate this phase and have no contract
directory (`REQ-DOCORIGIN-001/002/003`, `REQ-HSAPI-001` through `-006`,
`CL-DEPTH-001`, `CL-FPSS-006/007`) — a **named, explicit compatibility
exemption** (`decisions/0081`'s own Context section lists them), not a
silent grandfather clause: none is touched, downgraded, or reinterpreted
by this phase. `balance-from-spec` (§2/§6) is the only slug this check
gates today.

## 5. Oracle contract and result schema

Two new, minimal, machine-readable file formats under
`planning/contracts/<slug>/`, read/written as real YAML (`pyyaml`, an
existing dependency — not CodeCompass's own hand-rolled flat-record
parser, which is deliberately scoped to the six canonical knowledge-
record kinds only, not every new file format this phase introduces).
**Corrected twice**: `decisions/0080` bound `oracle-result.yaml` to the
exact tested subject, not merely a commit reference; `decisions/0081`
replaced the singular `check_reference`/`scope`/`required` design below
with an explicit `checks:` collection and a deterministic PASS/FAIL/GAP/
INVALID precedence rule.

- **`oracle-contract.yaml`** — `schema_version` (integer, `1`),
  `contract_id` (the `REQ-` id this contract belongs to — the single,
  unambiguous identity; a result's own `oracle_contract_id` always means
  "this `contract_id`," never a second, independent name),
  `tested_paths` (an explicit, committed list of implementation file
  paths this contract's `tested_subject_digest` covers — named precisely,
  not a directory glob, so its own scope is reviewable and does not
  silently grow or shrink), and `checks:` — a list, each entry carrying
  its own `check_id` (stable, contract-local), `scope` (the specific
  conditions this one check covers, e.g. "single-section expense
  aggregation" — required precisely because VERIFIED is scope-qualified,
  §4), `execution_provider` (a closed, named value; Phase 82 implements
  exactly `pytest`, not a provider-plugin system — a second provider kind
  is a future phase's decision, made when a second real need exists),
  `check_reference` (a pytest node id), `test_input_paths` (an explicit
  list of fixture/test-code files this one check's own `test_input_digest`
  covers — per-check, since two checks against the same implementation
  can legitimately read different fixtures), and `required` (bool —
  whether this check's absence of a passing result produces a `GAP`, as
  opposed to an optional, non-gating check).
- **`oracle-result.yaml`** — one per run, naming exactly one `check_id`
  (never the whole contract), with the following fields:

  | Field | Purpose |
  |---|---|
  | `run_id` | Identifies this specific execution — distinct from `baseline_id` (may be cited by many runs) and `tested_subject_digest` (may recur across runs against unchanged code). |
  | `contract_id` | The `REQ-` id this result addresses. |
  | `check_id` | The exact check (within the contract's own `checks:` list) this result addresses — not the whole contract. |
  | `baseline_id` | §7 — the accepted reference state, nullable (a run against no yet-accepted baseline is still valid, just not "the" reference result). |
  | `tested_subject_digest` | The content hash of the contract's own `tested_paths`, as they exist at run time — reusing Phase 81B's own `payload_tree_sha256`/`_canonical_digest_of_hashes` construction (`decisions/0077`). **Not a bare Git commit SHA.** A named path that cannot be read makes the digest computation itself fail, and the run is recorded `INVALID` with an `invalid_reason` naming the unresolvable path (`decisions/0081` §4) — never computed over a partial file set. |
  | `oracle_contract_id` + `oracle_contract_content_hash` | The accepted contract's own `contract_id` and a content hash of the live `oracle-contract.yaml`, continuing the tamper-detection mechanism below. |
  | `test_input_digest` | Content hash of the named check's own `test_input_paths` (fixture data *and* the test file itself, since both define what the check actually exercises) — a contract can stay unchanged while its own fixture or test code quietly drifts; this makes that drift independently detectable. |
  | `environment_descriptor` | Optional, recorded only where material (e.g. a language/runtime version that could plausibly change the outcome) — never fabricated when not material. |
  | `scope` | Must equal the named check's own `scope` for this result to count toward it at all (precedence rule 2, below) — never "close enough." |
  | `outcome` | `PASS\|FAIL\|INVALID` — a per-result field; **`GAP` is never written by a run about itself** (§5a). |
  | `raw_output_ref` + `raw_output_sha256` | A path to the captured raw tool output, for independent re-inspection, plus a content hash of that file — the raw evidence itself must be tamper-evident, not merely referenced. |
  | `executed_at`, `execution_provider` | Unchanged from the original proposal. |
  | `invalid_reason` | Mandatory when `outcome: INVALID` — the environment, configuration, or evidence that made the run unreliable; `INVALID` without a reason is itself a validation failure (§8.4). |

### 5a. PASS/FAIL/GAP/INVALID — deterministic precedence and aggregation (`decisions/0081` §2)

**Per-result precedence**, evaluated in this fixed order — the first
matching rule wins:

1. `tested_subject_digest`, `test_input_digest`,
   `oracle_contract_content_hash`, or `raw_output_sha256` cannot be
   independently recomputed to match what is recorded → **INVALID**,
   regardless of the run's own recorded `outcome`.
2. `scope` does not match the named check's own `scope` → **INVALID**.
3. Otherwise, the recorded `outcome` (`PASS`/`FAIL`/`INVALID`, as the
   execution itself determined) stands.

**`GAP` is an aggregate, never a per-result outcome**: for a given
`(contract_id, check_id)`, `GAP` holds iff the check is `required: true`
and no result satisfies precedence rule 3 with `outcome: PASS`. A `FAIL`
result for that check does not change this to something worse than
`GAP` — both facts coexist and are both reported (a regression was
observed, *and* the required check currently has no passing evidence). A
`FAIL` or `INVALID` result is never silently reclassified as merely
`GAP`: it remains a distinct, retained fact (Phase 81's own existing
conflict-retention discipline, reused unchanged for oracle-sourced
Evidence).

**Aggregate assurance for a contract is the union of its own per-check
states, never collapsed to one value** — "2/2 required checks PASS,"
"1/2 PASS + 1/2 GAP," and "1/2 PASS + 1/2 FAIL" are three distinct,
separately reported outcomes, mirroring §4's own
`verified_scopes`/`known_gap_scopes` split.

**Protection from the evaluated agent, and its real limit**:
`oracle-contract.yaml` files are the "accepted checks" the governing
prompt requires be protected — Phase 82's own deterministic validation
(§8) includes a check that an `oracle-contract.yaml`'s own content hash
(recorded at authoring time by a human/maintainer-approved commit, not
by the coding agent under evaluation) is unchanged at result-recording
time; a changed contract with no corresponding new maintainer-approved
commit fails validation closed. **This, and every digest field above,
establishes internal consistency and tamper-evidence after the fact —
it does not, by itself, prove independent execution or trusted
authorship.** Nothing in Phase 82 stops a sufficiently motivated author
from hand-computing consistent-looking digests for a fabricated run; the
schema can only show a result internally inconsistent, never
affirmatively prove it was produced honestly. **The mechanism that
actually prevents this** — running the oracle check somewhere the agent
under evaluation cannot write to, closer to Phase 81B's own broker/
sandbox model, where the checker is outside the evaluated agent's own
reach — is Phase 83/84's concern, not yet built. Phase 82 proves the
schema can represent and mechanically detect tampering after the fact;
it does not yet prevent a motivated fabrication before the fact.

## 6. Pinned Ledgerkit reference scenario and negative controls

**Corrected 2026-10-21 (`decisions/0081` §1)** — two real, already-
passing Ledgerkit tests, confirmed against the live
`~/projects/ledgerkit` checkout this session, pinned as `balance-from-
spec`'s two `checks:`:

- **`check_id: single-section-expense-subtotal`**, `scope: "single-
  section expense aggregation"` —
  `tests/test_reports.py::TestBalanceFromSpec::test_single_section_rows_and_subtotal`
  (asserts the `expenses` section's own subtotal against the pinned
  `tests/fixtures/filtered.journal` fixture: `1359.00`).
- **`check_id: multi-section-income-expense-subtotal`**, `scope: "multi-
  section income/expense aggregation with sign inversion"` —
  `tests/test_reports.py::TestBalanceFromSpec::test_multi_section_correct_values`
  (asserts both the `income` section, inverted, and the `expenses`
  section's own subtotals in the same report).

Both `required: true`. Running the oracle against the current,
unmodified checkout must produce `PASS` for both.

- **Negative control (original, preserved unchanged)**: a deliberately,
  minimally incorrect version of `balance_from_spec` (or an equivalent
  fixture mutation) must cause the same oracle contract to report
  `FAIL` — proving the oracle actually discriminates, not merely echoes
  a cached green result. This mutation is applied to a disposable
  scratch copy of the Ledgerkit checkout, never committed to the real
  `~/projects/ledgerkit` repository.

**Five further negative controls, added 2026-10-21 (`decisions/0080`),
each targeting one way §5's identity fields could otherwise be
misapplied**:

1. **A passing result cannot verify a modified candidate that was not
   tested.** After a real `PASS` run, mutate the scratch copy (any
   change, not necessarily one that breaks the behaviour) and confirm
   the stale `tested_subject_digest` no longer matches — the old result
   must not be treated as covering the new state.
2. **A result obtained under different accepted checks cannot be reused
   as equivalent evidence.** Change the `oracle-contract.yaml`'s own
   `check_reference` (a genuinely different check, same `contract_id`)
   and confirm an old result citing the prior
   `oracle_contract_content_hash` is not silently treated as satisfying
   the new contract.
3. **A result with mismatched or unverifiable test inputs fails
   closed.** Alter the fixture/input data a `check_reference` reads
   without updating `test_input_digest`, and confirm the mismatch is
   detected rather than silently accepted.
4. **Tampered or missing raw evidence cannot establish verification.**
   Edit the file `raw_output_ref` points to after the fact (or delete
   it) and confirm the `raw_output_sha256` mismatch (or missing-file
   condition) fails validation.
5. **A passing result for one scenario does not imply verification of
   untested scenarios.** Produce a real `PASS` for `scope: "integer
   inputs"` and confirm the derived view (§4) reports that scope
   verified while a distinct, never-run `scope: "fractional inputs"`
   stays in `known_gap_scopes` — never silently folded into an
   overall "verified" answer.

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

**Distinct from, not a substitute for, §5's `run_id`/`tested_subject_digest`**
(added by `decisions/0080`): `baseline_id` identifies *which accepted
reference state* a result is measured against — one baseline may be
cited by many runs over time. `run_id` identifies *one specific
execution*. `tested_subject_digest` identifies *what was actually
executed*, independent of how many times or when. Three separable
concerns, three separate fields — collapsing any two would reintroduce
exactly the kind of identity ambiguity §5 exists to close.

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
   `oracle-contract.yaml`; its `check_id` resolves to a real entry in
   that contract's own `checks:` list; every `INVALID` outcome has a
   non-empty `invalid_reason`. `GAP` is never a field the validator reads
   from a result at all (`decisions/0081` §2) — it is computed solely by
   the validator itself, per `(contract_id, check_id)`, from "required
   and no matching `PASS` survives the §5a precedence rule."
5. **Contract tamper detection**: an `oracle-contract.yaml` whose
   content hash does not match the hash recorded at its last
   maintainer-approved commit fails closed (§5's protection mechanism,
   checked mechanically here).
6. **Tested-subject/input/output integrity** (added 2026-10-21,
   `decisions/0080`, §6's five new negative controls): an
   `oracle-result.yaml` whose `tested_subject_digest`,
   `oracle_contract_content_hash`, `test_input_digest`, or
   `raw_output_sha256` does not match an independently recomputed value
   fails closed; a `scope` on a result that does not match any `scope`
   named in its own `oracle-contract.yaml` fails closed rather than
   being silently accepted as "close enough."
7. **`status: verified` earns its own claim, and cannot be earned
   vacuously** (§4, `decisions/0081` §3): a record whose `status` is
   `verified` but which does not have a current, matching-scope `PASS`
   for every `required: true` check in its own `oracle-contract.yaml` is
   a validation finding (`check_verified_status_cites_passing_oracle_
   result`) — including when the required-check set is empty or the
   contract is absent entirely (never vacuously satisfied). Applies only
   to a slug with a `planning/contracts/<slug>/` directory; the twelve
   pre-existing `status: verified` records with no contract directory
   are an explicit, named exemption (§4's own compatibility-policy
   paragraph), not silently reinterpreted.

## 9. Open decisions — resolved by explicit authorisation (`decisions/0081` §5)

All items below were previously gated on maintainer approval; the
governing prompt that produced `decisions/0081` explicitly authorised
proceeding with all of them, so none blocks implementation. Recorded here
for audit trail, not as an open gate:

1. **The derived-view design (§4, `decisions/0080`)** — confirmed:
   computing INTENDED/OBSERVED/VERIFIED/CONTESTED at read time from
   existing records, including repurposing the pre-existing,
   previously-unenforced `status: verified` value, proceeds as designed.
2. **The oracle-result identity fields (§5, `decisions/0080`, extended by
   `decisions/0081`)** — `run_id`, `check_id`, `tested_subject_digest`,
   `oracle_contract_content_hash`, `test_input_digest`,
   `environment_descriptor`, `raw_output_sha256`, `scope` — confirmed as
   specified.
3. **`balance_from_spec` is the pinned scenario** — confirmed against the
   live `~/projects/ledgerkit` fixture set this session (§2/§6): both
   named checks are real, currently-passing tests.
4. **The MCP SDK/licence check** named in Phase 84's roadmap entry
   remains Phase 84's own decision, not this phase's — still flagged here
   so it is not forgotten when Phase 82 hands off.

## 10. Verification (how this phase is confirmed done)

**Epistemic-view tests (§4), demonstrating the six scenarios the
governing prompt named by example, each against real or realistic
fixture records — not assumed, constructed and checked:**

1. An approved `REQ-` record with zero linked Claims: `derive_epistemic_
   profile` reports `intended=True`, `observed=False`,
   `verified_scopes=[]`.
2. A Claim with `basis: observed_behaviour`, real supporting Evidence,
   and a cited `test_ref` resolving to a real `PASS` oracle-result, with
   **no** `REQ-`/`DEC-` record referencing it at all:
   `intended=False`, `observed=True`, `verified_scopes` non-empty.
3. An approved `REQ-` whose linked Claim is `status: contradicted` with
   real `contradicting_evidence`: `intended=True`, `contested=True`
   simultaneously — neither suppresses the other.
4. A contract with two `oracle-contract.yaml` checks, different
   `scope`s, one with a real `PASS` result and one with none:
   `verified_scopes` contains the first, `known_gap_scopes` contains the
   second — `status: verified` on the governing record is rejected by
   `check_verified_status_cites_passing_oracle_result` (§8.7) while any
   required scope remains a gap.
5. A real `PASS` oracle-result whose `tested_subject_digest` no longer
   matches the current implementation after a relevant source change:
   demonstrates staleness is mechanically detectable (a raw digest
   recomputation and comparison) — the actual *trigger* that acts on
   this automatically is Phase 85's own reconciliation machinery, not
   built in Phase 82; this test confirms the data Phase 85 will need is
   present and correctly computed, not that Phase 85's trigger exists
   yet.
6. A new, conflicting Evidence record (e.g. a second oracle result
   disagreeing with a prior one) is added via the existing apply path:
   confirms both records persist, cited via `contradicting_evidence`,
   and neither is silently deleted or overwritten — exercising Phase
   81's already-existing conflict-retention behaviour against a new,
   oracle-sourced Evidence record for the first time.

**Oracle-identity tests (§5/§6)**: the five negative controls listed in
§6 (stale `tested_subject_digest`, mismatched `oracle_contract_content_
hash`, mismatched `test_input_digest`, tampered/missing
`raw_output_sha256`, scope non-generalisation), each demonstrated to
fail closed, not merely asserted possible.

**Schema-validator tests (§8)**: the oracle-contract/oracle-result
schema validators, including the minimal-content edge case (§8.2) and
the depth check (§8.3); the baseline-identity non-auto-advance rule
(§7) — a test that runs the oracle twice without an explicit acceptance
step and confirms no `baseline_id` was minted either time.

**End-to-end Ledgerkit tests (§6)**:

- The real Ledgerkit positive scenario produces `PASS` when run against
  the current, unmodified `~/projects/ledgerkit` checkout.
- The real Ledgerkit negative control produces `FAIL` when run against a
  deliberately mutated scratch copy — this is the exit gate's own named
  requirement and must be demonstrated, not merely asserted possible.

**Project-wide checks**:

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
actual, re-inspectable, scope-matching, tested-subject-bound oracle
result (`decisions/0080`).

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

## 13. Second amendment (corrective): epistemic model fully corrected, oracle-result identity strengthened (2026-10-21)

Direct user request ("CodeCompass v2 — Corrective Planning Amendment"),
same day as §12. Full rationale: `decisions/0080`. Confirmed before
amending: `HEAD` was exactly `47ab61c` (§12's own commit), zero drift.

**§12's own ordinal-scale correction was itself still wrong.** Reviewing
it against three concrete counter-examples (Ledgerkit rounding behaviour
verified by test but never accepted as intended; an accepted requirement
contradicted by real evidence; a contract verified under some inputs and
not others) found that `intended < observed < verified` still forces a
single value where the real relationships are independent predicates,
not an orderable scale — `verified` does not actually subsume
`intended`, contrary to §12's own stated reasoning. **`epistemic_source`
is now removed entirely** (§4) — not corrected a third time, replaced —
by a derived, read-time view that computes each of INTENDED/OBSERVED/
VERIFIED/CONTESTED independently from records Phase 81 already has, plus
Phase 82's own new oracle-result citations.

**This correction, too, is independent of federation** — like §12's own
first finding, it would have surfaced the moment Phase 82 tried to
record a Claim that was simultaneously verified and not intended,
regardless of any cross-project concern.

**Direct inspection of the actual Phase 81 implementation** (not only
its planning description, per this amendment's own governing
instruction) found the correction did not need inventing: `knowledge_
intermediate.py::derive_provenance_label` already solves the identical
problem shape (classify a record's epistemic standing purely from
existing fields, as a read-time function) for a different label set, and
had itself been corrected twice before for guessing instead of walking
real citation fields — the same mistake this ADR's predecessor
(`decisions/0079`) made for a new field, one phase layer up. This
amendment's own §4 reuses that function's existing helpers rather than
re-deriving them.

**Oracle-result identity was also strengthened** (§5/§6/§8): `run_id`,
`tested_subject_digest` (a content digest, not a bare commit SHA —
accounting for uncommitted worktree changes, reusing Phase 81B's own
`payload_tree_sha256` precedent), `oracle_contract_content_hash`,
`test_input_digest`, `environment_descriptor`, `raw_output_sha256`, and
an explicit `scope` field, plus five new negative controls and one new
validator rule (`check_verified_status_cites_passing_oracle_result`).
Phase 82's plan now states explicitly what it does and does not protect
against: internal consistency and tamper-evidence after the fact, never
independent execution or trusted authorship on their own — that
protection is named as Phase 83/84's own future mechanically-isolated
execution boundary, not claimed here.

**Nothing else in this plan changed.** The contract record format (§3),
the pinned Ledgerkit scenario and its original negative control (§6),
the baseline-identity non-auto-advance rule (§7, now explicitly
distinguished from `run_id`/`tested_subject_digest`), and the exit gate
(§11, reworded for precision, not weakened) are unchanged in substance.
Phase 82 is not broadened — every addition above is either a derived
view (no persisted schema) or a field on the already-new, not-yet-
implemented oracle-result file, never a change to an existing canonical
record.

**No further maintainer approval gate beyond §9's own two line items**
(the derived-view approach, and the oracle-result identity field set) —
both already restated to reflect this amendment, not additional to it.

## 14. Third amendment: oracle checks collection, outcome precedence, vacuous-verification prevention, tested-subject scoping (2026-10-21) — implementation proceeds

Direct user request ("CodeCompass Orchestrator — Correct Phase 82 Plan
and Proceed with Implementation"). Full rationale: `decisions/0081`.
Confirmed before amending: `HEAD` was exactly `2750752` (this plan's own
prior commit), zero drift.

**Four corrections, all already folded into §4-§9 above:**

1. **A. Multiple oracle checks.** §5's singular `check_reference`/
   `scope`/`required` replaced by an explicit, versioned `checks:`
   collection on `oracle-contract.yaml`, each with its own stable
   `check_id`, `scope`, `execution_provider`, `check_reference`,
   `test_input_paths`, and `required` flag. `contract_id` is the single,
   unambiguous identity; `oracle_contract_id` on a result always means
   "this `contract_id`," resolving the earlier duplication. §6 names the
   two real, already-passing checks this phase pins
   (`single-section-expense-subtotal`,
   `multi-section-income-expense-subtotal`). No execution-provider-plugin
   system is introduced — `pytest` remains the one closed, named value.
2. **B. Unambiguous verification outcomes.** §5a adds a deterministic
   per-result precedence rule (digest/scope validity checked before an
   `outcome` is trusted) and an aggregation rule making `GAP` strictly an
   aggregate ("required, no surviving `PASS`"), never a per-result field
   and never a reclassification of a `FAIL`/`INVALID` result — both
   remain distinct, retained facts.
3. **C. Vacuous verification is prevented.** §4/§8.7's
   `check_verified_status_cites_passing_oracle_result` now fails closed
   on an empty required-check set or an absent contract, rather than
   vacuously passing. Twelve pre-existing `status: verified` records
   (`REQ-DOCORIGIN-001/002/003`, `REQ-HSAPI-001` through `-006`,
   `CL-DEPTH-001`, `CL-FPSS-006/007`) predate this mechanism and have no
   contract directory — named explicitly as a compatibility exemption,
   not silently grandfathered and not retroactively rewritten
   (`decisions/0081` §3).
4. **D. Tested-implementation precision.** `tested_subject_digest` is
   now scoped to the contract's own explicit `tested_paths` list (named:
   `reports.py`, `models.py`, `parser.py`, and the four `query/` modules
   `balance_from_spec` actually imports — confirmed by direct inspection
   of `reports.py`'s own import statements, not Ledgerkit's entire
   package); `test_input_digest` is scoped per-check to its own
   `test_input_paths` (the fixture journal *and* the test file itself,
   since both define what the check exercises). An unresolvable named
   path fails the digest computation itself, recording the run `INVALID`
   with a named reason — never a partial-file-set digest presented as
   complete. A dirty worktree needs no special detection: the digest is
   always computed from whatever bytes exist on disk, so a dirty
   checkout simply produces a different, equally valid digest than a
   clean one (`decisions/0080`'s own original reasoning for a content
   digest over a commit SHA, now stated as this rule's own mechanism).

**Implementation is explicitly authorised and proceeds in this same work
session** (`decisions/0081` §5) — §9 above is rewritten from an open gate
into a resolved-decisions record; this is not a fifth planning-only
amendment.
