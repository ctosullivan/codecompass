# Phase 89 plan — independent review

Reviewer: `Plan`-type agent (read-only, no write access — this report
was handed back to the lead for persistence since the reviewer could
not write it directly itself).

## VERDICT: NOT READY (blocking findings)

Two blocking findings, both centered on the plan's new `apply_manifest`
mutation path (§4.4/§5.3). The plan's overall architecture-reuse
strategy is sound and well-grounded in real code for everything except
the one new mutation path it introduces, which is where both blocking
findings live.

---

## BLOCKING FINDING 1 — §4.4/§5.3's safety argument cites a
non-existent precedent; the plan introduces the first-ever in-place
mutation of an existing canonical record, undisclosed as a new
precedent

§4.4 and §5.3 claim the new `"source_reconciliation"` apply step
"appends to (never replaces) the Claim's `contradicting_evidence`/
`supporting_evidence` field and updates its `evidence_support_state`
field only... via the same flat-record rewrite helper
`_apply_requirement_proposal` already uses for its own field updates
(reused, not reinvented)."

This is false by direct reading of `_apply_requirement_proposal`
(`knowledge_intermediate.py:2298-2330`) and every other apply-path
function in that module (`_apply_anchor_edit:2207`,
`_apply_candidate_addition:2372`). The reviewer read all three in full.
None of them ever mutates an *existing* record's fields in place. Each
one only ever creates a **brand-new** record via `_write_record(sdir /
f"{new_id}.yaml", fields)` with a freshly `_next_id`-allocated id.
`_apply_anchor_edit`'s own docstring/comment states the project's
actual, deliberate convention explicitly: *"A semantic edit never
overwrites the original record directly (§7) — it always creates a
new, competing candidate Claim instead."* A grep across the whole
codebase for any write to `evidence_support_state`/
`contradicting_evidence` as an assignment (not a read) found none —
these fields are set once, by a human, at initial record authoring
(confirmed directly in `CL-BFS-004.yaml`'s own
`evidence_support_state: partially_supported` line), never
written-to programmatically anywhere today.

So Phase 89's actual design need — append an Evidence id to an
*existing* Claim's list field and change one other field on that same
existing record, while leaving its `statement`/`derivation`/
`timestamp`/etc. untouched — is **genuinely new behavior** for this
codebase: the first-ever in-place mutation of a canonical knowledge
record, where the established, repeatedly-applied project convention
everywhere else is "never mutate an existing record directly, always
create a new, competing one instead." The plan did not disclose this
as a new precedent, did not weigh it against the existing convention,
and incorrectly described it as reuse of an existing mechanism.

A second, directly connected gap this creates: `apply_manifest`'s
existing conflict detection (reused unchanged per the plan, §4.8) works
by comparing a manifest item's own `base_semantic_hash` (captured once,
at detection/write_manifest time) against the *whole file's* live hash
at apply time — any drift refuses the write as a conflict. The plan's
own §4.8 "Ambiguous" scenario explicitly allows **multiple
`source_reconciliation` items against the same Claim** (e.g. one
`CONFIRMED_REGRESSION` via one check, one qualifying `VERIFIED_SCOPE`
via a different check), each reported and decided independently. If
both are accepted in the same manifest/apply run, applying the first
item changes the Claim's file content (and hash); when `apply_manifest`
reaches the second item for the *same* Claim, its own earlier-captured
`base_semantic_hash` no longer matches — not because a human edited
anything, but because Phase 89's *own* first write did. Under the
reused whole-file-hash conflict check, this would be indistinguishable
from a genuine concurrent-edit conflict and would spuriously refuse the
second, equally legitimate item. §4.8's "Conflicting" bullet described
only the human-hand-edit case and did not address this self-inflicted
scenario, even though its own "Ambiguous" bullet described exactly the
situation that produces it.

**What would need to change**: the plan needs to (a) honestly identify
this as new, previously-unused mutation behavior for canonical
records, not a reuse of `_apply_requirement_proposal`'s pattern; (b)
explicitly weigh it against the project's existing "never mutate,
always create a new competing record" convention and either justify
the deviation or redesign around it; and (c) if direct mutation is
kept, design and test for the same-Claim multiple-pending-item scenario
explicitly rather than silently inheriting a conflict check that was
designed for a different threat model.

---

## BLOCKING FINDING 2 — CLAUDE.md §1 L-021 is not satisfied

`apply_manifest` has exactly one real production call site, confirmed
by grep: `cli.py`'s `knowledge_apply_manifest` (the `codecompass
knowledge apply MANIFEST_PATH` command — the plan's own §4.10 names
this same command as the mechanism through which the new kind becomes
reachable, "no new CLI surface needed here at all"). The plan does add
behavior to `apply_manifest` (§5.3's new `elif item["kind"] ==
"source_reconciliation"` branch). But §7 Stage 89A's test list never
named `knowledge_apply_manifest`/`codecompass knowledge apply` as a
call site to be exercised, nor committed to at least one test that
drives the new branch through that real CLI entry point rather than by
calling `apply_manifest()` directly as a library function. This is a
concrete, checkable, currently-unmet requirement from CLAUDE.md §1
(L-021), not a stylistic nit.

**What would need to change**: §7's Stage 89A test list should
explicitly name `codecompass knowledge apply`
(`knowledge_apply_manifest` in `cli.py`) as the call site under test
and include at least one test that invokes the CLI command against a
manifest containing a `source_reconciliation` item, not only a test
against `apply_manifest()` in isolation.

---

## Criterion-by-criterion findings (kept, not kept, and why)

**1. Architectural feasibility / component reuse.**
- KEPT (true, verified): `detect_grounded_region_changes`'s
  `claims_changed` case genuinely fires off any content-hash drift in a
  cited record's own file, regardless of cause — confirmed by direct
  reading of `_current_cited_hashes`
  (`knowledge_intermediate.py:315-321`), which does nothing but
  `record.path.read_text()` + hash, with zero dependency on *how* the
  file changed. The plan's central claim here is correct.
- FINDING (non-blocking, factual inaccuracy in the plan's own
  "source-verified" inventory, §1.1): the plan states `write_manifest`'s
  two kinds (`anchor_edit`/`candidate_addition`) are "the two kinds
  `apply_manifest` recognises today." Verified false: `apply_manifest`'s
  real dispatch already recognises a **third** kind, `doc_region_edit`
  (written not by `write_manifest` but by a separate, already-existing
  sibling function, `write_doc_candidates_to_manifests`, called from
  `docs maintain`). This doesn't break the plan's actual proposal (a 4th
  kind, not a 2nd "extra" one, is still just extending the same
  dispatch), but it actually *strengthens* the case for the plan's own
  undecided §9 item ("whether `write_manifest` grows a parameter or a
  sibling writer is introduced instead") — `write_doc_candidates_to_
  manifests` is exactly the sibling-writer precedent already in
  production, and the plan missed citing it despite needing exactly
  that precedent.

**2. Completeness of the change→knowledge→documentation chain (§3
diagram).**
- Every arrow checked against real code: no arrow is pure hand-waving.
- NON-BLOCKING gap: `assess()`'s own `AssuranceFinding` objects are
  keyed by `check_id`, not by `claim_id`. To build "one manifest item
  per `CONFIRMED_REGRESSION`/qualifying `VERIFIED_SCOPE` finding...
  against the Claim" (§5.1), `propose_reconciliation` must recover the
  claim_id↔check_id link by re-walking
  `range_reports[].symbol_classifications[].claims[]` (where each
  `ClaimFinding` does carry `check_id`). A real, recoverable, moderate
  implementation detail the plan doesn't spell out, but not hand-waved
  to the point of infeasibility.

**3. Preservation of human edits / canonical-knowledge integrity.**
See Blocking Finding 1 — this is where the real problem is. Everything
else in §4.6 (concurrent_conflict/doc_candidate regions refused from
auto-regeneration, manually-maintained docs unreachable by `docs
maintain`'s discovery) is accurately described and verified against
real `docs maintain`/`publish` behavior.

**4. Conflict/staleness semantics (§4.3) vs. decisions/0087 §1.**
KEPT as accurate, no conflation found. The precedence (fresh FAIL →
CONFIRMED_REGRESSION; fresh INVALID → INVALID_ASSESSMENT; fresh PASS →
VERIFIED_SCOPE; no fresh result → VERIFICATION_GAP) matches the plan's
§4.3 description exactly, including correctly excluding
`VERIFICATION_GAP`/`INVALID_ASSESSMENT` from ever being proposed as
reconciliation, and correctly treating a `VERIFIED_SCOPE` against an
already-`supported` Claim as a no-op while treating the same outcome
against a `partially_supported`/`unconfirmed` Claim as proposable. This
is the strongest, most carefully-grounded section of the plan.

**5. Real-world Ledgerkit evaluation feasibility (§6).**
- KEPT: scratch-copy-only execution is concretely feasible and doesn't
  require the real `~/projects/ledgerkit` checkout or new
  cross-repository authorization.
- KEPT: §6.3's Task B pre-registration design is genuine, not quietly
  fixed now — legitimate pre-registration practice, not an evasion.
- NON-BLOCKING observation: §6.1's characterization of the Phase-88
  fresh `PASS` oracle result as "already-produced," ready for direct
  reuse, is imprecise — that result was written only into a disposable
  session-scratchpad project-root, explicitly never into this
  repository's own committed `planning/contracts/balance-from-spec/
  results/`. That scratchpad will almost certainly not exist by the time
  Phase 89 is actually implemented. Not a feasibility blocker, but the
  plan should say "regenerate this PASS result fresh, following the
  already-documented procedure" rather than implying a persisted
  artifact is sitting ready to reuse.

**6. False-positive control adequacy (§6.2).** KEPT as adequate.

**7. Scope discipline / Phase 88/90 independence.** KEPT — no MCP
dependency introduced; `planning/v2-evaluation-methodology.md` citation
accurate.

**8. CLAUDE.md §1 precedent rules.**
- L-021: **not satisfied** — Blocking Finding 2.
- L-087: **satisfied, genuinely, not merely asserted** — verified
  against the real `establish_new_region_baselines`/`advance_region_
  baseline_after_publish` precedent.
- L-070/L-075: considered, not applicable.
- L-088: considered, not applicable.
- L-131: considered and rejected as a finding — the new CLI command
  follows the same `--repo-root` convention every other `knowledge ...`
  command already uses; not a new invocation paradigm.

## Other findings considered and rejected (preserved per project
practice)

- Whether `find_gaps`'s new `claim_contradicted_by_fresh_check` kind
  duplicates the existing `"contradiction"`/`"stale_test_citation"`
  kinds — verified genuinely distinct, not duplicative. The plan's own
  §1.1 inventory does undercount the existing gap taxonomy (cites only
  4 of the real 7 kinds `find_gaps` already emits) — real but
  non-blocking, since it doesn't change the new kind's validity; the
  plan should explicitly distinguish the new kind from these two
  adjacent ones before Stage 89B.
- Whether the new `detect-changes` CLI command needs its own
  execution-opt-in gate mirroring Phase 88 MCP's `--enable-execution` —
  rejected; that separation exists for MCP's remote/untrusted-caller
  threat model, not applicable to a local, human-invoked CLI tool whose
  subprocess hardening already lives in `oracle.py` itself.
- Whether `decisions/0085` §3's "no new scheduler/event bus/competing
  knowledge store/documentation compiler" constraint is violated
  anywhere — verified clean.
- Whether `source_files.content_hash` is genuinely populated by
  `codecompass sync` — verified true (`graph.py`'s real upsert).
- Whether `docs/reference/cli.md`'s description of the reused
  `docs`/`knowledge` commands matches what the plan claims — verified
  accurate in full.

---

## Re-review (2026-11-16, amended plan)

Reviewer: `Plan`-type agent (read-only, fresh dispatch — no access to
the first round's own conversation; re-verified both blocking findings
from scratch against real source, not taken on trust).

### VERDICT: READY WITH NON-BLOCKING OBSERVATIONS

**Blocking Finding 1 — RESOLVED, verified sound.** Checked
`_apply_anchor_edit`/`_apply_candidate_addition`/`_apply_requirement_
proposal`/`_apply_doc_region_edit` in full. The quoted convention text
in the amended §4.4 is an exact, verbatim match to `_apply_anchor_
edit`'s own in-code comment. Every existing `apply_manifest` kind only
ever creates a brand-new record or mutates a documentation
grounding-marker header — never an existing canonical record's own
fields — confirming the amended plan's "genuinely new, unprecedented
behavior" claim holds up under direct reading. `CL-BFS-004.yaml`'s own
`evidence_support_state: partially_supported` field is confirmed
present and human-authored exactly as cited. The semantic-wording vs.
machine-derived-bookkeeping distinction is real and defensible, not
hand-waving. The self-conflict/race fix (merge by `claim_id` before
writing) is structurally sound and traced through concretely: it
cannot occur by construction once every item is per-Claim.

**Blocking Finding 2 — RESOLVED, verified sound.** `apply` is
confirmed the one real production call site
(`knowledge_apply_manifest`, `cli.py:1569-1570`).
`tests/test_knowledge_intermediate.py:632` already uses
`runner.invoke(app, ["knowledge", "apply", ...])`, confirming the
CLI-testing convention the amended §7 commits to reusing is real. §7's
test list now explicitly names this call site and commits to a test
through it, directly satisfying `CLAUDE.md` §1 L-021.

**Inventory corrections**: `apply_manifest`'s 3 real kinds (citing
`write_doc_candidates_to_manifests` as the `doc_region_edit` writer) —
**verified accurate**. `find_gaps`'s gap-kind count — **the amended
plan's "7" is itself still inaccurate**: direct tracing of every
`Gap(kind=...)` append inside `find_gaps` and its own helper
`_find_gaps_for_slug_contract` found only **six** kinds actually
emitted by `find_gaps` itself (`contradiction`,
`dangling_evidence_reference`, `dangling_dependency_reference`,
`missing_contract`, `unverified_required_scope`,
`stale_test_citation`). The "seventh," `missing_evidence`, belongs to
a different, sibling function, `trace_evidence` — not `find_gaps`. The
new 8th/9th kind `claim_contradicted_by_fresh_check`'s distinctness
from `contradiction`/`stale_test_citation` was independently
re-confirmed regardless; only the inventory count needs correcting.

**No new inconsistency found** from the amendment itself (grepped all
`write_manifest`/`source_reconciliation`/`write_source_reconciliation_
manifest` occurrences — all consistent, no stale "one item per
finding" language survives). One pre-existing, non-blocking wording nit
unrelated to either blocking finding: §4.10 says "two new... CLI
subcommands" when only one (`detect-changes`) is actually new (`apply`
already exists) — harmless.

**ADR trigger** — confirmed a correct, narrowly-targeted application
of `CLAUDE.md` §2's actual "non-obvious tradeoff" text, not an over- or
under-claim.

### New findings from this round's own walkthrough (non-blocking but
material; not raised in the first round)

**(a) Unspecified semantics for a merged item with disagreeing
outcomes.** §4.8 anticipates a Claim mapping to multiple checks "with
agreeing or disagreeing fresh outcomes," merged into one item — but
§5.3(c)'s write-step description is single-direction only
(`contradicting_evidence` **or** `supporting_evidence`, never both at
once) and never addresses a merged item whose own contributing
findings require writing to both. `evidence_support_state ==
"conflicting"` is confirmed a real, pre-existing, already-used value
(`knowledge_intermediate.py:1211-1214`, feeding the existing CONTESTED
classification) — tailor-made for exactly this case — but the plan
never cites or commits to using it. A genuine, concrete specification
gap, not hypothetical.

**(b) No stated idempotency guard against partial-write duplication on
retry.** Every existing apply-path function explicitly checks
`_find_existing_promoted_record` before creating a new record — exactly
what makes a crash-and-retry safe. §5.3's new branch description never
mentions an analogous pre-check. For a merged item with more than one
contributing finding, a crash after writing Evidence for finding 1 but
before finding 2 (and before the item is marked `"applied"`) would, on
retry, risk creating a duplicate Evidence record for finding 1 while
finding 2 is processed correctly. §4.8's "Interrupted" bullet addresses
only the source-baseline's own advancement, not this item-internal
multi-record partial-write case.

Both (a) and (b) are resolvable within the plan's existing framework
(reuse the existing `conflicting` enum value for (a); add an
existing-citation idempotency check mirroring `_find_existing_
promoted_record` for (b)) and are recommended to be folded into the
Stage 89A ADR drafting step and test list, rather than treated as
grounds for a third full review round — the core architectural fix
(closing the literal hash-race) is sound and verified complete; these
are corner-case write-semantics gaps naturally in scope for the ADR
Stage 89A already commits to drafting first.

### Considered and rejected (this round)

- Treating the find_gaps 6-vs-7 inaccuracy as blocking — rejected; an
  inventory bookkeeping inaccuracy that doesn't change the new gap
  kind's own validity or any design decision.
- Treating findings (a)/(b) as a third blocking finding — rejected;
  non-blocking corner-case write-semantics gaps naturally in scope for
  the already-committed Stage 89A ADR, not evidence the amendment's
  central claims are false.
- Re-litigating the first round's own Finding 1/2 disposition — did
  not reopen either; both independently re-verified from scratch.
- `classify_symbol`'s contract-identity checks (§5.3(a)) — spot-checked
  and confirmed accurate; `ClaimFinding` already carries both
  `claim_id` and `check_id` on the same object, even more directly than
  the plan implies.
- §4.10's "two new... subcommands" wording — noted as a minor,
  pre-existing (non-amendment) nit, not worth blocking on.

## Re-review (second amendment round, 2026-11-16, "Phase 89 Final Planning Amendment")

Reviewer: `Plan`-type agent (read-only, fresh dispatch — no access to any
prior round's own conversation; every claim below re-verified from
scratch against real source/records, not taken on trust from the plan's
own account or from either prior review round's own account).

### VERDICT: NOT READY (blocking findings)

Both prior review rounds' own findings (Blocking Findings 1/2 from round
1, the find_gaps-count correction and findings (a)/(b) from round 2) are
re-confirmed resolved and remain resolved — re-verified independently
below, not merely re-asserted. This round's own third amendment's new
work (§0.1, the two new detectors, the Evidence-identity mechanism, the
three-gate exit framework) is, on the whole, carefully source-grounded
and a real improvement over the text it replaced — confirmed point by
point below. But a new, genuinely new (introduced by *this* amendment's
own rewrite of §4.4), concrete, falsifiable pair of defects was found in
§4.4's `evidence_support_state` recomputation rule — the one piece of
this plan every round so far has had to correct at least once — and
those defects are blocking.

### BLOCKING FINDING 1 (new this round) — §4.4's recomputation rule writes
an enum value, `"contradicted"`, that does not exist for
`evidence_support_state`

§4.4 states the recomputation rule in full: "non-empty
`contradicting_evidence` and non-empty `supporting_evidence` both ⇒
`'conflicting'`; non-empty `contradicting_evidence` alone ⇒
**`'contradicted'`**; non-empty `supporting_evidence` alone, with every
required contract scope now covered ⇒ `'supported'`, otherwise ⇒
`'partially_supported'`."

Verified directly against `scripts/check_knowledge_base.py`'s own
`_OPTIONAL_ENUM_FIELDS["claim"]["evidence_support_state"]`
(lines 209-214): the real, closed, already-enforced set of valid values
for this exact field is `{"supported", "partially_supported",
"unsupported", "conflicting"}`. **`"contradicted"` is not a member of
this set.** `"contradicted"` *is* a valid value for a different field —
`_STATUS_ENUMS["claim"]` (line 170), the Claim's own `status` field,
never `evidence_support_state`. The correct value for "contradicting
evidence only, no supporting evidence" is `"unsupported"`.

### BLOCKING FINDING 2 (new this round) — §4.4's "every required contract
scope now covered" condition is internally self-contradictory, and its
only worked application (§6.1) does not follow from §4.4's own stated
rule

§4.4 states the recomputation reads **only** this one Claim's own
`contradicting_evidence`/`supporting_evidence` contents — explicitly
scoped to this one Claim, nothing else. §6.1 step 8 then reaches
`"supported"` for `CL-BFS-004` by reasoning about "every one of the
contract's required checks... cited somewhere in CL-BFS-004/sibling
Claims under the same Requirement family" — invoking *other* Claims'
own citations, directly contradicting §4.4's own stated single-Claim
scope. Independently falsified against this project's own pre-existing
ground truth: `CL-BFS-001.yaml`/`CL-BFS-002.yaml` are already
`evidence_support_state: supported` today, each citing only **one** of
the contract's three required checks' own evidence — neither covers
"every required contract scope." `CL-BFS-003.yaml` is a separate,
dedicated record for the "every required check" assertion
(`status: superseded`), confirming this project's own existing
convention already keeps "this one scope is covered" separate from
"the whole contract is covered" — §4.4/§6.1 blur this without resolving
it, and "sibling Claims under the same Requirement family" names no
actual, implementable grouping mechanism anywhere in this codebase or
this plan.

### Confirmed resolved / confirmed sound (re-verified from scratch)

- Round 1's Blocking Finding 1 (false "reuse" claim) — still resolved;
  `_apply_anchor_edit`/`_apply_candidate_addition`/`_apply_requirement_
  proposal` re-read in full, confirmed each only ever creates a new
  record.
- Round 1's Blocking Finding 2 (L-021) — still resolved;
  `cli.py:1570`/`knowledge_apply_manifest` confirmed as the one real
  call site, named in §7's test list.
- Round 2's find_gaps-count correction — now exactly right; every
  `Gap(kind=...)` call site grepped directly, six kinds confirmed,
  `missing_evidence` confirmed to belong only to `trace_evidence`.
- §0.1.A's core claim — verified true, independently, by tracing
  `classify_symbol`/`assess` line by line and confirming `CL-BFS-004`'s
  real current state (`supporting_evidence: [EV-BFS-001]` only,
  source-kind) and `REQ-BFS-002.yaml`'s real absence of any `check_id`
  field, and the absence of any result file for the third check.
- §0.1.B's core claim — verified true, independently; `apply_manifest`'s
  `manifest_path.write_text(...)` confirmed at line 2543, strictly after
  the whole-batch loop; zero `_next_id(sdir, "EV"` call sites confirmed;
  `_find_existing_promoted_record`'s `statement`-field matching confirmed.
- §0.1.D's core claim — verified true; `resolve_changed_range`'s live-
  hash-vs-graph-hash cross-check confirmed to exist exactly as cited.
- `evaluate_result_precedence`'s digest recomputation (§1.2) — confirmed
  true and genuinely distinct from the "never yet run" scenario.
- `decisions/0086`/`0087`'s classification semantics — confirmed left
  completely unmodified; the new `"regression"`/`"newly_discovered_
  failure"` label confirmed additive, read from `AssuranceFinding.
  observed_outcomes`, logically sound given the fresh-outcome-is-already-
  FAIL precondition of that branch.
- §4.2's `check_id` field — confirmed genuinely additive and safe; no
  allowlist/unknown-field rejection exists anywhere in `check_knowledge_
  base.py`. Minor terminology nit: it is one shared `_RECORD_FIELD_ORDER`
  list, not a kind-specific "requirement field table" — non-blocking.
- The sibling-writer precedent (`write_doc_candidates_to_manifests`) and
  its own existing idempotency precedent (`_existing_pending_doc_region_
  edit_keys`) — confirmed real and accurately cited.
- Evidence-identity provenance fields (`run_id`, `decisions/0082` §C) —
  confirmed real.
- `contract_id`'s existing one-contract-to-one-REQ mapping — confirmed
  genuinely distinct from the new `check_id` field's purpose.
- The exit-gate quote (§0.1.C) — confirmed verbatim-accurate against
  `planning/v2-roadmap.md` line 702-705; the three-gate framework in
  §6.3/§8 confirmed a faithful, non-overclaiming operationalisation.
- §4.10's wording nit flagged in round 2 — confirmed now actually fixed.
- `decisions/0085` §3 — confirmed accurately cited throughout.

### Non-blocking observations

- §5.1's "existing requirement field table" phrase is a minor
  imprecision (one shared `_RECORD_FIELD_ORDER` list, not kind-specific).
- The `pytest --collect-only` probe's own disclosed open risk (§9) is
  honestly flagged as unresolved, not hidden — acceptable to leave for
  Stage 89A's own implementer.
- `Gap` dataclass's new label field (§5.4) is additive with no existing
  allowlist-style validation found elsewhere for this type — no issue.

### Considered and rejected (this round)

- Re-litigating round 1/round 2's own already-resolved findings as if
  still open — rejected; both independently re-verified from scratch.
- Treating the `_RECORD_FIELD_ORDER` terminology nit as blocking —
  rejected; purely descriptive imprecision, no behavioural consequence.
- Treating the disclosed `pytest --collect-only` residual risk as a
  third blocking finding — rejected; already honestly named as an open
  Stage-89A-level risk in §9, not presented as solved.
- Considering whether the two new Blocking Findings above might be
  "merely" wording issues — rejected for both: Finding 1 is a mechanical
  enum-validity bug with a concrete, checkable failure mode; Finding 2
  is a self-contradiction directly falsifiable against this project's
  own pre-existing, already-approved records (`CL-BFS-001`/`CL-BFS-002`/
  `CL-BFS-003`), not a matter of interpretation.

### Summary for the orchestrator

This amendment's own stated motivation (§0.1.A/B/C/D) is confirmed sound
in every particular checked, and the architecture built around it is
well-grounded in real source and real records throughout — a materially
better plan than the text it replaced. But §4.4's `evidence_support_
state` recomputation rule and its own worked application in §6.1 still
contain two new, concrete, falsifiable defects: an invalid enum value,
and a self-contradictory/undefined notion of which "required... scope[s]"
govern a single Claim's own recomputation. Both are narrowly scoped to
§4.4/§6.1 specifically — no other section is implicated. Recommend a
fourth, narrow amendment scoped to exactly these two points, followed by
a further review pass focused specifically on re-verifying the corrected
§4.4/§6.1 text.

## Re-review (fourth amendment, focused)

Reviewer: `Plan`-type agent (read-only, fresh dispatch — no access to any
prior round's own conversation; every claim below re-verified from
scratch against real source/records). Scope, per the dispatch
instructions: §0's new "Amended a fourth time" paragraph, §4.4 (the
corrected recomputation rule), §6.1 step 8 (the corrected walkthrough),
§7's new Stage 89A test-list items, and §9's risk-register update.
Round 3's own "Confirmed resolved / confirmed sound" list was not
re-litigated except where noted below.

### VERDICT: READY WITH NON-BLOCKING OBSERVATIONS

Both of round 3's two blocking findings are genuinely fixed,
independently re-verified from scratch. One new, real, but
currently-unreachable soundness gap was found in this round's own
rewrite (reported below, in the spirit of round 2's own findings
(a)/(b)), plus one test-adequacy gap and one unenforced-invariant
observation. None rise to blocking.

### Blocking Finding 1 (round 3) — RESOLVED, verified sound

`scripts/check_knowledge_base.py` lines 167-214 confirmed: the real,
closed `evidence_support_state` enum is exactly `{"supported",
"partially_supported", "unsupported", "conflicting"}`; `"contradicted"`
belongs only to `Claim.status`. The corrected rule's `"unsupported"`
replacement is a real, valid value. No stray `"contradicted"`-as-
evidence_support_state usage survives anywhere in the document.

### Blocking Finding 2 (round 3) — RESOLVED, verified sound

The corrected rule reads only one Claim's own fields plus each cited
Evidence record's own `evidence_kind` — no cross-Claim reasoning
anywhere. Directly re-validated against every real record it names:
`CL-BFS-001`/`CL-BFS-002` (test-kind Evidence present ⇒ `supported`,
matches real state); `CL-BFS-004` pre-Task-A (`EV-BFS-001` source-kind
only ⇒ `partially_supported`, matches real state exactly); `CL-BFS-004`
post-Task-A (hypothetical test-kind `EV-BFS-004` added ⇒ `supported`,
matches §6.1's intended result). The "never reaches CL-BFS-003/
CL-BFS-005" claim holds, confirmed two independent ways: (1) the stated
check_id→REQ→depends_on chain genuinely cannot reach them (`REQ-BFS-001`
is a real two-check Requirement, confirmed by its own statement,
`depends_on: [CL-BFS-001, CL-BFS-002, CL-BFS-003]`; `CL-BFS-005` is
named by no Requirement's `depends_on` at all, only by its own
`supersedes` field); (2) independently, detector (a)'s own
`classify_symbol` also cannot reach them (`CL-BFS-003`/`CL-BFS-005`
never cite the slug's one source-kind Evidence, `EV-BFS-001`). §6.1
step 8 now follows directly from the corrected rule, with no gap.
§9's risk-register update is accurate and does not overclaim.

### New findings this round (non-blocking, but material)

**(c) The corrected rule's two-branch partition over `supporting_
evidence`'s evidence-kind composition is not exhaustive over this
project's own real `evidence_kind` taxonomy (5 real values in use:
`source` 56, `test` 9, `documentation` 29, `executable` 13,
`behavioural` 1 — grepped directly), and is independently falsified, if
ever (counterfactually) applied, against several real, pre-existing
Claims in `planning/knowledge/first-party-source-symbols/` (a different
slug) — e.g. `CL-FPSS-008.yaml` cites only source-kind Evidence and is
already `evidence_support_state: supported`, which the corrected rule
would recompute to `partially_supported`; several others
(`CL-FPSS-001/004/005/007/009`) cite only `documentation`/`executable`-
kind Evidence and fall into neither of the rule's two defined branches
at all. **Why non-blocking**: confirmed structurally unreachable by
Phase 89's own mechanism today — `change_impact.assess()` short-circuits
before `classify_symbol` whenever a slug has no `oracle-contract.yaml`
(`change_impact.py:510-546`), `detect_newly_coverable_checks` likewise
requires one, and `planning/contracts/` contains exactly one
subdirectory, `balance-from-spec` — `first-party-source-symbols` has no
contract at all. This is a real latent gap in the rule *as general-
purpose prose* (§4.4 doesn't currently scope the rule to contract-
governed Claims only), not a defect in anything Phase 89 will actually
do. Recommended: fold an explicit scoping note into the Stage 89A ADR
rather than a fifth review round.

**(d) Stage 89A's test list has no explicitly-named test for the exact
branch that caused Blocking Finding 1** (contradicting-evidence-only ⇒
`"unsupported"`). The "enum-validity test" as currently worded is
ambiguous — it may or may not actually drive the recomputation function
through this specific branch. Recommended: name a distinct
"contradicting-evidence-only test" explicitly in §7, mirroring the
"source-vs-test-Evidence test" naming already used there.

### Non-blocking observation

**(e) The "never reaches CL-BFS-003/CL-BFS-005" guarantee rests partly
on an unenforced human convention** — nothing in `check_knowledge_
base.py` would reject a human mistakenly adding `check_id` to
`REQ-BFS-001` (a multi-check Requirement), which would make the
resolution chain return all three of its `depends_on` Claims at once,
including the whole-contract-scoped `CL-BFS-003`. Not falsifiable
against any current real record. Recommended: a one-line defense-in-
depth note in the Stage 89A ADR (validate that a Requirement carrying
`check_id` has `depends_on` of length exactly 1).

### Confirmed sound (re-verified this round)

`scripts/check_knowledge_base.py`'s real enums; `find_gaps`'s real
`"contradiction"` implementation (reads `status`, never `evidence_
support_state`, confirming the plan's own §1.1 distinction is correctly
grounded); every one of `REQ-BFS-001`/`REQ-BFS-002`/`CL-BFS-001` through
`CL-BFS-005`/`EV-BFS-001` through `EV-BFS-003` read in full and matching
every plan citation; `change_impact.assess()`/`classify_symbol` read in
full. The diff between this amendment and the prior one is confirmed
confined exactly to §0/§4.4/§6.1 step 8/§7/§9. This amendment also
removed a previously-inaccurate "mirrors the existing CONTESTED
derivation" citation — that logic is read-only, not a write-rule the
new recomputation could soundly claim to mirror — a genuine,
uncredited improvement.

### Considered and rejected (this round)

- Re-litigating rounds 1-3's own already-resolved findings — rejected,
  explicitly out of scope and nothing new contradicts them.
- Treating (c) as a third blocking finding — rejected; independently
  confirmed structurally unreachable by Phase 89's own mechanism today.
- Treating (d)/(e) as blocking — rejected; a naming/specificity gap and
  an unfalsified defense-in-depth suggestion respectively.

### Summary for the orchestrator

Both of round 3's blocking findings are genuinely, verifiably fixed.
This round's own hunt for new defects turned up one real, material, but
currently-unreachable soundness gap, plus a minor test-list specificity
gap and a minor unenforced-invariant observation — all three
recommended for Stage 89A's own ADR/test-list drafting rather than a
fifth review round. **This plan is READY**, with these three
non-blocking items to carry forward into Stage 89A. Implementation
remains unauthorised pending a separate, explicit go-ahead.

## Independent review — fifth amendment (2026-11-16, "Phase 89 Planning Corrections and Independent Verification")

### VERDICT: NOT READY

One new, genuinely blocking, self-contradiction was found in the fifth amendment's own text (§4.10 vs. §7), directly undermining Finding E's own fix. Findings A-D are substantively sound in design but contain real factual errors in their own stated verification. Full detail below.

### A. OracleResult provenance — CONFIRMED BUT STILL DEFECTIVE
`AssuranceFinding` (`change_impact.py:424-433`) confirmed to carry only `check_id`/`classification`/`fresh_effective_outcome`/`fresh_invalid_reason`/`aggregate_state`/`observed_outcomes`/`contributing_symbols` — no `run_id`/`raw_output_ref`. `run_check_assurance` (line 436-478) confirmed to compute `fresh_result` (line 445) and discard it on return. The core diagnosis and the additive `on_fresh_result` callback design are sound in principle.

But two of the plan's own verification claims in this exact paragraph are **false**:
- "`oracle.write_oracle_result` has zero call sites anywhere in `src/codecompass/`" — false. `src/codecompass/mcp/tools.py:466` (`oracle_execute_check`) calls it directly, in production code (not a maintainer script). This is in fact a real existing precedent for "evaluate_check → write_oracle_result" that detector (b)'s design mirrors.
- "there are none [call sites of `assess`] in `src/` today" — false. `src/codecompass/mcp/tools.py:342` calls `_ci.assess(..., run_checks=False)`. Backward compatibility is not actually broken by this (it's `run_checks=False`, so `on_fresh_result` never fires), but the stated grep result is wrong.

A further, independently-found design gap: `assess()`'s `check_contributors`/`run_check_assurance` call is nested **inside** `for c in changed:` (change_impact.py:526-574), re-initialized per range, not once per check_id globally. If the same `check_id` is contributed by findings from two different ranges in one `propose_reconciliation` call (plausible once detector (a) batches multiple drifted files), `run_check_assurance` runs twice for that check_id, and the plan's own described `_capture` mechanism ("a local closure appending each real `OracleResult` it receives, **keyed by `check_id`**, to a dict") silently overwrites the first result with the second — a redundant subprocess execution and a possible run_id/finding mismatch, never discussed anywhere in §4.4/§5.1/§9. Not exercised by the plan's own worked walkthroughs (CL-BFS-001/002 map to distinct check_ids there), so non-blocking in isolation, but a real, material specification gap that should be closed (accumulate a list per check_id, or key by `(range_index, check_id)`) before Stage 89A.

### B. Detector gate — CONFIRMED SOUND
`scripts/check_contracts.py` lines 212-300 (`current_pass_check_ids`) confirmed to ask only "does any result currently evaluate PASS," independent of whether any Evidence cites it. `classify_symbol`'s `test_evidence_check_id` bridge (change_impact.py:352-394) confirmed to require the Evidence's `test_ref` to resolve to a parseable, contract/scope-matching result. The corrected gate (zero citing test-kind Evidence) is well-defined, correctly distinguishes never-covered from previously-covered-now-stale, and is genuinely mutually exclusive with detector (a)'s scope.

### C. Mutation control — CONFIRMED SOUND
Verified directly against `/home/cormac/projects/ledgerkit/tests/test_reports.py:706-751` and `_income_expenses_spec` (line 697-704): both sections in both named tests use exactly one account pattern. `reports.py`'s matching gate (`if not any(_matches_pattern(...) for pat in section.accounts): continue`, ~line 661) is confirmed a single boolean check — the OR-union mutation genuinely cannot fail either test. The sign-inversion guard (`if section.invert: rows = {k: -v ...}`, ~line 685) confirmed: removing it negates Expenses's subtotal from `1359.00` to `-1359.00`, failing both named tests' assertions; Income (already `invert=True`) is unaffected, as claimed. Arithmetic independently reproduced and matches.

### D. Task B threshold — CONFIRMED SOUND
`planning/v2-evaluation-methodology.md` read in full: line 234, "It does not set a numeric target for any metric" — no threshold exists anywhere in the document. `.claude/agents/context-evaluator.md` confirmed to really produce PASS/PASS WITH GAPS/FAIL plus LOW/MODERATE/HIGH context-advantage (lines 7-8, 52-53), as cited. §7's Stage 89A deliverables list now explicitly includes "Task B's own pre-registration record... written and committed... before Stage 89B's Task-A demonstration runs" — genuinely earlier than Stage 89B (§7), closing the previously-cited sequencing defect.

### E. CLI boundaries — CONFIRMED BUT STILL DEFECTIVE (new blocking finding)
§4.10's five-layer design is sound on its own terms: layer 1 (`detect-changes`, no flag) genuinely calls neither `assess()` nor any subprocess; layer 2 (`--probe-coverage`) explicitly, honestly states it adds a real `pytest --collect-only` subprocess call ("not read-only in any meaningful sense," §4.10/§9) and names the collection-time-code-execution risk.

But §7's own Stage 89A test-list description directly contradicts this: "a CLI-boundary test (`detect-changes`, **with and without `--probe-coverage`**, confirmed to spawn **zero subprocesses** and write zero files... on every code path...)" (line ~1957). This is a direct, falsifiable self-contradiction between §4.10 (which says `--probe-coverage` spawns a subprocess) and §7 (which says the same command, with that same flag, spawns zero subprocesses). Implemented literally, this regression test either (a) cannot pass against code that correctly implements §4.10's own design, or (b) would be satisfied only by silently making `--probe-coverage` a no-op that never actually probes test collection — defeating detector (b)'s entire coverability check and reintroducing exactly the read-only/side-effect-boundary conflation Finding E exists to fix. This is analogous in character to the third review round's blocking findings (an internal contradiction between two sections of the plan's own text, falsifiable without external facts) and should be treated as blocking.

### Cross-cutting (item 6)
No inconsistency found with rounds 1-4's settled results: the Evidence-identity mechanism, `evidence_support_state` recomputation rule, ADR list (now 4 items, consistent throughout), and risk register are internally consistent. No new scheduler/event bus/knowledge store/doc compiler/MCP dependency introduced (§4.10's closing paragraph, §10 non-goals, confirmed accurate). Append-only Evidence convention preserved outside the one disclosed exception (§4.4, confirmed narrowly scoped to two machine-derived fields). Explicit human approval before every canonical mutation confirmed (§4.9, §10). Phase 83's `CONFIRMED_REGRESSION`/etc. classification confirmed untouched — §10's own closing paragraph correctly distinguishes the additive `on_fresh_result` parameter from a classification change.

### Item 7 — other independent checks
`ReportSpec`/`ReportSection` (ledgerkit/models.py:197-222) confirmed real, frozen dataclasses; the Task-B fallback ("combined section" constructor merging two sections' account-pattern tuples) is a coherent, concretely-scoped feature given this real data model. Stage 89A's scope (§7) is large but the added Task-B pre-registration deliverable does not obviously overflow it; no second contradiction of that kind found elsewhere.

### Recommendation
A sixth, narrow amendment is needed, scoped to: (1) fix §7's CLI-boundary test description so it asserts zero subprocesses only for `detect-changes` **without** `--probe-coverage`, and separately asserts that **with** `--probe-coverage` exactly one `pytest --collect-only` subprocess per uncovered check occurs (never a full test run, never a file write); (2) correct the two factually-wrong "zero call sites" claims in §0.2.A/§4.4; (3) specify `_capture`'s behavior when the same `check_id` is contributed by more than one range in a single `assess()` call (accumulate, don't overwrite). None of these require revisiting B, C, or D.

### Disposition (same session, sixth amendment)

All three recommended items applied directly to the plan, not deferred: (1) §7's CLI-boundary test split into two independent, non-contradictory assertions (without `--probe-coverage`: zero subprocesses/zero files; with it: exactly one collection-only subprocess, still zero files) — the "with and without" contradiction removed. (2) §0.2.A/§4.4 corrected with the real call-site facts (`mcp/tools.py:466`/`:342`, the latter's `run_checks=False` independently confirmed to make the real caller unaffected by the new parameter for a second, structural reason beyond simply not passing it) — independently re-verified via a corrected, recursive grep before accepting the reviewer's correction. (3) `_capture` redesigned to accumulate a `list[OracleResult]` per `check_id`, matched to its own finding by `(range index, check_id)`, with a new, dedicated multi-range regression test added to §7. A fresh, focused independent review of this sixth amendment is required before READY can be re-claimed.

## Independent review — sixth amendment (2026-11-16, narrow verification of three targeted fixes)

### VERDICT: READY WITH NON-BLOCKING OBSERVATIONS

All three recommended fixes from the fifth-round review were independently re-verified against the plan's own corrected text and, where applicable, directly against real source. No new self-contradiction or factual error was introduced.

### 1. CLI-boundary test self-contradiction — FIXED, CONFIRMED

`planning/phase-89-incremental-knowledge-documentation-reconciliation.md:2057-2074` now states two separate, non-contradictory assertions: (i) `detect-changes` **without** `--probe-coverage` spawns zero subprocesses and writes zero files on every code path (line 2061-2064); (ii) `detect-changes` **with** `--probe-coverage` spawns **exactly one** `pytest --collect-only` subprocess per uncovered check (never a full run, verified via invocation arguments) and still writes zero files (line 2064-2070). This matches §4.10's own layer descriptions verbatim: layer 1 (lines 1401-1416) "spawns zero subprocesses and writes zero files," layer 2 (lines 1417-1427) "adds detector (b)'s own `pytest --collect-only` step... still writes no result/manifest file." No remaining contradiction between §4.10 and §7.

### 2. "Zero call sites" factual correction — FIXED, INDEPENDENTLY RE-VERIFIED

Ran `grep -rn "write_oracle_result(" src/codecompass/` and `grep -rn "_ci\.assess(\|change_impact\.assess(" src/codecompass/` directly: confirms exactly one real call site each — `src/codecompass/mcp/tools.py:466` (`_oracle.write_oracle_result(out_path, result)`) and `src/codecompass/mcp/tools.py:342` (`report = _ci.assess(`). Matches the plan's corrected text at §0.2.A exactly, including the line numbers. `src/codecompass/mcp/tools.py:342-349` confirmed: `run_checks=False` is passed (line 348; the plan previously cited "line 347," off by one — now corrected to 348). The plan's reasoning that this caller is unaffected by `on_fresh_result` for two independent reasons (doesn't pass the parameter; `run_checks=False` means the callback's code path never executes) is sound and matches `assess()`'s own `if run_checks: ... else: finding = AssuranceFinding(...)` branch at `change_impact.py:566-576`.

### 3. Multi-range `_capture` fix — FIXED, COHERENT, CLOSES THE GAP

`change_impact.py:510-586`: `check_contributors` (line 549) and the `assurance`/`run_check_assurance` loop (lines 563-578) are both inside `for c in changed:` (line 529), re-initialized per range — confirms the prior review's diagnosis exactly. The plan's fix (§4.4; §5.1) now specifies `_capture` accumulates a `list[OracleResult]` per `check_id` (never overwrites) and `propose_reconciliation` matches each finding to its captured result by `(range index, check_id)`, consuming entries in range order — coherent given `assess()`'s deterministic range-then-sorted-check_id iteration order. §7 has a distinctly-named "multi-range capture test" exercising exactly this scenario.

### Targeted cross-check

No stray uncorrected "zero call sites" claims remain (both remaining occurrences are self-referential, describing the historical error being corrected). §9's risk register did not originally call out the multi-range `(range, check_id)` accumulation redesign as its own entry — non-blocking, not a contradiction. No other location still references the old "keyed by `check_id` alone" design or the old "re-walk `assess()`'s own return value" design as current.

### Disposition (same session)

Both non-blocking observations folded in directly: the "line 347" citation corrected to "line 348"; a new "Resolved by a fifth independent review round" entry added to §9's risk register documenting the `_capture` multi-range redesign and the two factual/contradiction fixes. No seventh review round triggered, per this project's own established practice for non-blocking editorial observations. **This plan is READY.** Implementation remains unauthorised pending a separate, explicit go-ahead.
