# 0092: Phase 84 corrective pass — fail-closed consistency default, dangling-evidence gaps, uniform context bounds

**Status:** accepted (2026-10-29). Governing prompt: "CodeCompass
Orchestrator — Phase 84 Corrective Pass" (2026-10-29), responding to
three correctness defects an independent post-completion source review
identified in `src/codecompass/knowledge_api.py` (Phase 84, `decisions/
0084`/`0085`/`0091`). This is a post-completion correctness pass, not a
reopening of Phase 84's settled architecture — every decision below is a
bug fix within that architecture (one logical model, read-only access,
natural-key identity, reuse of `oracle.evaluate_result_precedence`/
`knowledge_intermediate.derive_epistemic_profile`), not a change to it.

## Context

Three defects survived Phase 84's own independent `release-phase-auditor`
pass (`planning/retros/_audit-phase-84.md`, PASS WITH NON-BLOCKING
OBSERVATIONS) because that audit verified the module's *stated* behaviour
against its own tests, not every retrieval path's *actual* default
behaviour under conditions those tests didn't exercise:

1. **Verification currency.** `get()` accepted a `repo_root` parameter but
   silently dropped it when resolving an oracle-result identity through
   `_get_result()`; `traverse()` had no `repo_root` parameter at all, so
   `_traverse_check_results()` could never thread one through either.
   `evaluate_result_precedence()` was consequently always called without
   `repo_root`, meaning the one check that recomputes a live digest never
   ran — a historically recorded `PASS` could be, and was, reported
   `ConsistencyEnvelope(status="current")` on the strength of its own
   recorded digest matching itself, never against the real current
   implementation. Separately, `ConsistencyEnvelope.status` itself
   defaulted to `"current"` — any retrieval path that built a
   `KnowledgeResult` without explicitly overriding `consistency` (several
   did: `_get_vendor`, `_get_doc`, `_get_check` before this pass, every
   `search()` hit, every `traverse()` field-relation neighbour) silently
   claimed "current" by construction, never because anything was actually
   confirmed.

2. **Missing-evidence gaps.** `trace_evidence()` resolved each id in a
   Claim/Requirement's own `supporting_evidence`/`contradicting_evidence`
   fields, silently `continue`-ing past any id that didn't resolve to a
   real record. Its one gap check — `if ... and not supporting_ids` — only
   fired when the field was *empty*, never when it was *non-empty but
   entirely unresolvable*. A Claim citing a single nonexistent
   `EV-MISSING-001` therefore returned `status="result"` with zero actual
   evidence — declared coverage reported as resolved coverage.

3. **Context bounds.** `get_context_packet()` applied `max_items`/
   `max_chars` only on the path where `topic` was itself a known
   knowledge-record id. A free-text `topic` resolving to a non-knowledge-
   record search hit (an oracle contract/check) took an early-return
   branch that wrapped that one item into a packet unconditionally,
   bypassing both bounds entirely regardless of their value.

All three share one root shape: a *correct* mechanism (`evaluate_result_
precedence`, `trace_evidence`'s own gap concept, the bounding loop) existed
and was exercised by at least one passing test, but a *second, less-common
path* into the same mechanism was never required to go through it.

## Decisions

### 1. `ConsistencyEnvelope.status` defaults to `"unconfirmed"`, never `"current"`

The single highest-leverage fix for defect 1's systemic half: every
retrieval path that does not explicitly compute and set `consistency`
now honestly reports "not evaluated" rather than accidentally claiming
"current." This fixes `_get_vendor`, `_get_doc`, `search()`, and every
`traverse()` field-relation neighbour without touching each call site
individually — the dataclass's own default is the one place the
optimism lived. `_knowledge_consistency()` (the mechanism `get()`/
`trace_evidence()`/`get_context_packet()` share for knowledge-record
items) was separately corrected at two points that had the same
optimistic-default shape at the function level: its final `else` branch
(a record citing no scope of its own slug's oracle contract at all) and
its `found is None` branch (no oracle contract for the slug at all) both
previously left the local `status` variable at its own then-default
`"current"`; both now start `"unconfirmed"` and are promoted only by the
one branch that positively confirms every applicable scope.

### 2. Oracle-result/check currency is only ever earned by a reachable `repo_root`

`repo_root` is now threaded through `get()` → `_get_result()`/`_get_check()`
and the new `traverse(..., repo_root=...)` parameter → `_traverse_check_
results()`. A shared helper, `_oracle_result_consistency(effective,
reason, repo_root, contract_revision)`, is the single place this
determination is made for both call paths (never two divergent
implementations): `effective == "INVALID"` is always `"stale"`, with or
without `repo_root` (contract-hash/id/raw-output/scope checks all run
unconditionally); `effective in ("PASS", "FAIL")` is `"current"` only
when `repo_root` was supplied (meaning the live digest recomputation
itself ran), else `"unconfirmed"` with an explicit reason. `_get_check()`
applies the identical rule to `aggregate_contract()`'s own `PASS` state.
The CLI's `knowledge get`/`trace`/`gaps`/`context` commands gained a
`--repo-root` option forwarding this through, since without it the CLI
could never actually report `"current"` for anything oracle-backed.
`_get_result()`'s own `details` dict gained an explicit `effective_outcome`
field (previously only embedded in `summary`'s free text) plus a
separately-named `effective_invalid_reason` — kept distinct from the
result's own recorded `invalid_reason` field (already present via
`asdict(result)`) so the historical-vs-fresh distinction `decisions/0089`
established is never collapsed by one field silently overwriting the
other.

### 3. `trace_evidence()`/`find_gaps()` report a `dangling_evidence_reference` gap per unresolved citation

A new `Gap.kind` value, `"dangling_evidence_reference"`, carries the
citing record's id, the citation's role (`"supporting"`/
`"contradicting"`), and the missing id itself. `trace_evidence()` now
resolves every citation independently: an id that resolves is appended to
`results` regardless of any sibling citation's own fate; an id that does
not resolve appends a gap instead of being silently dropped. The
pre-existing `"missing_evidence"` gap (zero citations at all) is
preserved unchanged and can co-occur with `"dangling_evidence_reference"`
gaps. `find_gaps()` gained the identical scan applied corpus-wide (every
record's own `supporting_evidence`/`contradicting_evidence`, not only the
one subject a direct `trace_evidence()` call names), so the two functions
never diverge on what counts as resolved.

### 4. `get_context_packet()`'s bounding is one function, applied to every path

A new `_bound_context_items(candidates, max_items, max_chars)` is the
single bounding implementation; both the knowledge-record path (subject +
its direct relation neighbours) and the free-text/non-knowledge-record
path (a single search hit) now build an ordinary `list[KnowledgeResult]`
of candidates in priority order and pass it through this one function.
Deterministic by construction: items are accepted in the candidates'
given order until either bound would be exceeded, so the very first
candidate failing to fit yields an empty `items` list with `truncated:
true`, never a silent over-budget return (defect 3's exact prior
behaviour on the non-knowledge-record path). Knowledge-record items in
both the context-packet path and `trace_evidence()`'s resolved-evidence
list now also carry a real `_knowledge_consistency()`-computed envelope
rather than an unexplained default, extending decision 2's currency
guarantee to these two call sites as the governing prompt's own "search(),
context packets, and other relevant API responses" instruction named.

## Consequences

- No change to `oracle.py`, `graph.py`, or `knowledge_intermediate.py` —
  every decision above is achieved by how `knowledge_api.py` calls their
  existing, unmodified public surface, and by one dataclass default.
- A caller that never supplies `repo_root` now sees `"unconfirmed"`
  wherever it previously saw an unearned `"current"` — any code
  downstream that happened to treat Phase 84's original "current" as a
  green light without itself checking `repo_root` availability will now
  see the honest answer instead. No such caller exists yet (Phase 84
  shipped one release ago); this is flagged here for Phase 85 planning.
- `trace_evidence()`/`find_gaps()` can now report `status="gap"` for a
  Claim/Requirement that `status="result"`-ed before this pass, for any
  corpus containing a dangling evidence citation. The real CodeCompass
  corpus itself has none at the time of this pass (confirmed by the
  dogfood re-run below) — this is a detection capability being added
  ahead of a known real occurrence, not a response to one.
- `tests/test_knowledge_api.py` grew from 47 to 65 tests (18 new,
  covering all three defects plus the shared helpers); none of the
  original 47 needed their own assertions changed, only (in one case)
  their consequence re-verified against the corrected default.

## Alternatives considered

- **Compute a full `_knowledge_consistency()`-style envelope for every
  `KnowledgeResult` this module ever constructs**, including `search()`
  hits and `traverse()` field-relation neighbours. Rejected as
  disproportionate: those paths can return many records per call, and
  recomputing a full epistemic profile for each would be real,
  unnecessary cost for information most callers of `search`/`traverse`
  are not asking for (they can call `get(id)` on any specific hit for a
  confirmed envelope). The fail-closed default (decision 1) gives the
  same honesty guarantee — "not current unless confirmed" — without that
  cost, and is the smaller, more maintainable change.
- **A full byte-for-byte literal comparison for `query relations`'s table
  output**, to close the Phase 84 audit's own non-blocking observation.
  Attempted and found genuinely infeasible at this command's own
  (deliberately untouched) default render width: Rich truncates several
  cells with an ellipsis rather than wrapping them, so even the current,
  correct output is not stable against a hardcoded full-table string
  without pinning a console width this command does not itself pin —
  which would itself be exactly the kind of CLI-output change §4 of the
  governing prompt rules out. The test's docstring was corrected instead
  to state precisely what it verifies (full JSON dict equality; targeted,
  verified-untruncated table substrings), per the governing prompt's own
  named alternative.
