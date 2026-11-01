# 0093: Phase 84 final corrective amendment — Requirement indirect-evidence tracing, live-revision validation in find_gaps()

**Status:** accepted (2026-11-02). Governing prompt: "CodeCompass
Orchestrator — Final Phase 84 Closeout and Phase 85 Planning"
(2026-11-02). Phase 84 is already `done`, including its first
corrective pass (`decisions/0092`). This ADR records a second, final,
narrowly scoped corrective amendment to the same, unchanged architecture
— neither reopens `decisions/0084`/`0085`/`0091`/`0092`'s own settled
decisions.

## Context

An independent post-completion source review identified two further
defects in `src/codecompass/knowledge_api.py`:

1. **`trace_evidence()` did not recognise a Requirement's indirect
   evidence.** This project's own established knowledge model has no
   `supporting_evidence` field on a Requirement at all — a Requirement's
   evidence is always indirect, through the Claims named in its own
   `depends_on` (`epistemic_status()` already resolves this correctly
   for oracle-verification purposes, selecting those dependent Claims as
   its own `subjects`). `trace_evidence()` instead checked only the
   Requirement's own (always-absent) `supporting_evidence` field,
   reporting `status="gap"`/`"missing_evidence"` for every Requirement
   unconditionally — confirmed against the real corpus:
   `trace_evidence(REPO_ROOT, "REQ-BFS-001")` reported this false gap
   despite `REQ-BFS-001` depending on three Claims (`CL-BFS-001/002/003`)
   that each carry real, resolvable `supporting_evidence`.

2. **`find_gaps()`'s `stale_test_citation` detection dropped `repo_root`.**
   `find_gaps()` accepts `repo_root` and already forwards it to
   `derive_epistemic_profile()` for `unverified_required_scope` detection,
   but its separate `stale_test_citation` block called both
   `oracle.aggregate_contract()` and `oracle.evaluate_result_precedence()`
   without it. Consequently, a result that satisfies only *contract-
   relative* integrity (hash/raw-output/scope) could be described as
   "currently passing" — and used to justify flagging a different,
   cited, historical result as a "stale citation" against it — without
   ever confirming that fresher result was itself live-reconfirmed
   against the current implementation. Reproduced directly: a
   constructed fresher result with a deliberately wrong
   `tested_subject_digest` was still reported as the "currently passing"
   result justifying a `stale_test_citation` finding, identically
   whether or not a `repo_root` was supplied — proof the parameter had
   no effect on this code path at all.

## Decisions

### 1. `trace_evidence()` resolves a Requirement's evidence one hop through `depends_on`

For a Requirement specifically, each `depends_on` id is resolved; a
dependent Claim's own direct `supporting_evidence`/`contradicting_
evidence` is then resolved and returned with `role` `"supporting_
indirect"`/`"contradicting_indirect"` and a `via_claim` detail naming
the Claim — preserving the complete relationship path and provenance,
never collapsing a Requirement's evidence into an undifferentiated list
indistinguishable from direct Claim-level evidence. A dependent Claim
with no `supporting_evidence` of its own is its own `missing_evidence`
gap, keyed to the Claim (not the Requirement) — the Requirement itself
is `missing_evidence` only when it has no evidence at all, direct or
indirect, across every dependent Claim. A `depends_on` id that does not
resolve is a new, distinct `dangling_dependency_reference` gap (a broken
*Claim* reference, never conflated with `dangling_evidence_reference`, a
broken *Evidence* reference).

**Deliberately one hop, not recursive.** This project's real corpus has
at least one Claim that itself `depends_on` another Claim
(`CL-BFS-003` depends on `CL-BFS-001`/`CL-BFS-002`) — but `CL-BFS-003`
already carries its own direct `supporting_evidence`, so this never
needed to matter in practice. The established model this amendment
reuses (`epistemic_status()`'s own existing Requirement → dependent-
Claims selection) only ever walks one hop; recursively chasing a
Claim's own `depends_on` from inside `trace_evidence()` would duplicate
a question that function does not otherwise need to answer (whether a
Claim's own assertion is itself evidenced) and risks scope creep into
general graph traversal this module's own plan (§6) excludes. Claim-
level tracing (calling `trace_evidence()` directly on a Claim) is
completely unaffected — a Claim's own `depends_on` is never walked by
this function at all, only a Requirement's.

### 2. `find_gaps()` threads `repo_root` through `aggregate_contract()`/`evaluate_result_precedence()` for `stale_test_citation`, with qualified wording

Both calls now receive `repo_root`, matching the already-established
pattern `_oracle_result_consistency()` (`decisions/0092`) and `_get_check()`
use elsewhere in this module — no new digest or precedence mechanism,
purely reusing `oracle.py`'s own existing, unmodified functions. The
`stale_test_citation` gap's own `reason` text is now qualified: when
`repo_root` was supplied, it states the fresher result was "live-
reconfirmed against the current implementation"; when it was not, it
states "contract-relative only -- not live-reconfirmed; no repo_root
supplied" — never an unqualified "currently passing" claim that could be
mistaken for a live-confirmed one. The historical result's own
contract-hash-mismatch INVALID determination is unaffected either way
(that check never needed `repo_root` to begin with).

## Consequences

- No change to `oracle.py`, `graph.py`, or `knowledge_intermediate.py` —
  both fixes are achieved entirely by how `knowledge_api.py` calls their
  existing, unmodified public surface.
- `epistemic_status()` is unchanged (it already resolved this correctly)
  and remains the single place oracle-verification "is this scope
  actually confirmed" is decided — `trace_evidence()`'s new indirect-
  evidence walk answers a narrower, different question ("does citable
  evidence exist and resolve at all") and never re-derives or duplicates
  `derive_epistemic_profile`'s own logic, per the governing prompt's
  own instruction to keep the three functions semantically consistent
  without duplicating validation logic.
- `find_gaps()`'s `dangling_evidence_reference` corpus-wide scan gained
  an equivalent `dangling_dependency_reference` scan over every record's
  own `depends_on` field, for the same consistency reason
  (`decisions/0092`'s own precedent: a `trace_evidence()`-level detection
  gets a corpus-wide `find_gaps()` equivalent).
- A Requirement's own `get_context_packet()` (which calls
  `trace_evidence()` internally for its gaps) now also benefits from
  the corrected indirect-evidence resolution with no further code
  change needed there.

## Alternatives considered

- **Give Requirements their own `supporting_evidence` field.** Rejected
  outright — this would be a canonical knowledge-record schema change,
  explicitly out of scope ("no new canonical storage system or record
  kind," and this amendment's own governing prompt: "Do not... alter
  previously accepted architectural decisions").
- **Recursively resolve an arbitrary `depends_on` chain (Claim →
  Claim → ... → Evidence).** Rejected — see Decision 1's own "one hop"
  rationale; the real corpus never requires it, and resolving an
  arbitrary depth reintroduces exactly the kind of general graph-walk
  this module's plan (§6) and `decisions/0091` §5 (fixed relation
  vocabulary) already excluded.
- **Compute a single combined "verification confidence" score across
  `trace_evidence`/`find_gaps`/`epistemic_status`.** Rejected — the
  governing principle (preserving the distinction between intent,
  evidence, and verification) requires these to stay three separately
  retrievable, non-collapsed answers; a combined score would merge them.

## Correction (2026-11-02, same-day independent re-audit)

The implementation's first commit (`23f6826`) introduced an undisclosed
regression this ADR's own Decision 1 explicitly claimed did not exist:
"Claim-level tracing ... is completely unaffected." The shared
`has_any_support` signal computing whether `missing_evidence` fires was
accidentally switched from the pre-amendment, purely *declared*-list-
based check (`not supporting_ids`) to a *resolution*-based one (whether
`_resolve()` actually resolved at least one id) — a change that applies
to the Claim path too, since both paths shared the one signal. A Claim
with a single declared-but-dangling `supporting_evidence` citation
(e.g. `supporting_evidence: [EV-MISSING-001]`) consequently reported
**two** gaps (`dangling_evidence_reference` *and* `missing_evidence`)
instead of the one this ADR's own §Context section's cited principle
("a declared citation is never conflated with a resolved one") and the
pre-amendment behavior both require.

Caught by the independent `release-phase-auditor` re-audit of this same
amendment (`planning/retros/_audit-phase-84.md`'s "FINAL CORRECTIVE
AMENDMENT AUDIT" section, verdict FAIL), independently reproduced by the
lead before fixing, and not caught by this amendment's own 14 new
tests: the one test whose name claims to cover this
(`test_claim_level_tracing_is_unaffected_by_requirement_indirection`)
used a Claim with *literally empty* `supporting_evidence: []`, never a
*declared-but-dangling* one, so it could not see the regression its own
name claims to guard against.

**Fix:** reverted the shared signal to purely declared-list-based
(`has_any_declared`, never resolution-based) for *both* paths — a
Claim's own top-level `missing_evidence` trigger is restored to exactly
its pre-amendment behavior (`bool(direct_supporting_ids)`), and the
Requirement's own analogous signal is extended the same way: a non-
empty `depends_on` list, even one whose target doesn't resolve or whose
Claim lacks its own evidence, counts as "something was declared,"
suppressing a redundant top-level Requirement gap in favour of the
narrower, already-reported gap that names the real problem
(`dangling_dependency_reference`, or the dependent Claim's own
`missing_evidence`). This is symmetric with the Claim-level invariant
by construction, not merely restored for Claims and separately
re-decided for Requirements — one declared-vs-resolved rule, applied
uniformly, is what this ADR's own `decisions/0092` lineage already
established and this correction returns to.

Two test changes: `test_requirement_with_unsupported_dependent_claim_
is_a_gap_keyed_to_the_claim` updated (the Requirement no longer also
gets a redundant top-level gap when its only dependent Claim lacks
evidence — only the Claim-keyed gap fires, matching the symmetric rule
above); `test_requirement_with_dangling_dependency_reference_is_a_gap`
gained an explicit total-gap-count assertion. One new regression-guard
test added, `test_exclusively_dangling_supporting_evidence_produces_
exactly_one_gap`, asserting the *total* gap set for the exact scenario
the audit found broken — guarding against this exact regression
recurring in either direction. Re-verified: full suite, `tests/
test_knowledge_api.py` (80 passed), all three strict validators, and
the real corpus (`REQ-BFS-001` still correctly resolves with zero
gaps) all green after the fix. See `planning/retros/_audit-phase-84.md`
for the auditor's own re-verification of this correction.
