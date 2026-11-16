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
