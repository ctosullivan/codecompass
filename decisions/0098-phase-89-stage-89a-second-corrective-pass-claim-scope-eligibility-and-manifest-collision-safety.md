# 0098. Phase 89 Stage 89A second corrective pass: Claim-scope
eligibility for automatic Evidence updates, and collision-resistant
reconciliation-manifest creation

## Status

Accepted (2026-11-18, direct user request — "CodeCompass Orchestrator —
Phase 89A Knowledge-Integrity Correction and Independent Re-Audit").
Corrective, not a reopening of `decisions/0096`/`decisions/0097`'s own
tradeoffs, which stand unchanged. This ADR documents two further,
independently identified defects in Stage 89A's reconciliation
implementation — one in the single-check Evidence-update/support-state
mechanism's own Claim-scope assumption, one in reconciliation-manifest
filename uniqueness — found by a source-level review after `decisions/
0097`'s own corrective pass had already landed and been independently
audited. Governed by `decisions/0085` §3 and `decisions/0096`/`0097`,
neither of which this ADR reopens.

## Context

### 1. Whole-contract/aggregate Claims could be silently promoted by a
single check's own result

`source_reconciliation._claims_bridged_by_check_id` resolves every
Claim whose `supporting_evidence`/`contradicting_evidence` cites
Evidence already bridged to a drifted check — by design, this includes
not only a Claim whose *own* assertion is specifically governed by that
one check, but also any broader Claim that happens to cite the same
bridging Evidence alongside other citations. The real Ledgerkit
`balance-from-spec` knowledge base already has exactly this shape:
`CL-BFS-001`/`CL-BFS-002` are genuinely single-check-scoped Claims;
`CL-BFS-003` is a superseded, whole-contract Claim; `CL-BFS-005`
(`CL-BFS-003`'s own successor) is a whole-contract Claim whose own
`depends_on` field explicitly names `CL-BFS-001`/`CL-BFS-002` — its own
truth is established by *combining* those two Claims, not by either
check's result in isolation, and its `evidence_support_state` is
deliberately `partially_supported` (the contract's third required
check, `overlapping-account-patterns-no-double-count`, has no passing
result yet).

`_recompute_evidence_support_state`'s own docstring already asserted
this mechanism is "scoped correctly to a single-check Claim... never a
whole-contract-scoped Claim like `CL-BFS-003`/`CL-BFS-005`, which this
write path never reaches" — but nothing in the code actually enforced
that invariant. `_apply_source_reconciliation` would append new
Evidence to, and recompute `evidence_support_state` for, *any* Claim a
manifest item named, including `CL-BFS-005` — a single re-verified
check passing would have silently moved a whole-contract Claim's own
support state, even though the contract's third required check
remained genuinely uncovered. The comment described an invariant; it
was never actually checked.

**Decided**: a new function, `knowledge_intermediate.claim_scope_
category(claim, *, bridging_check_ids=None)`, reused at two points:

- **Proposal time** (`source_reconciliation.propose_reconciliation`,
  all three pathways — `symbol_change`, `test_input_change`, and
  detector (b)'s own newly-coverable pathway): every Claim a drifted
  check's bridging Evidence reaches is categorised before a
  `ContributingFinding` is ever created for it.
- **Apply time** (`knowledge_intermediate._apply_source_reconciliation`,
  as a defensive, fail-closed backstop — never trusting the upstream
  gate alone for the one write path that mutates a Claim in place).

Four categories, in priority order:

1. **`"superseded"`** (`claim.status == "superseded"`) — a historical
   assertion (`CL-BFS-003`), excluded entirely: never mutated, and
   (at proposal time) never even reported as affected. There is
   nothing actionable to report for a record this project's own
   convention already treats as dead.
2. **`"aggregate"`** — `claim`'s own `depends_on` field names one or
   more other Claim records (`CL-BFS-005`'s own real shape). This
   reuses an **existing**, already-authored, unambiguous structural
   signal — no new scope metadata was introduced, since this field
   already exists and already expresses exactly the relationship that
   matters here (`CLAUDE.md` §2's "non-obvious tradeoff" judgment:
   reuse before invention, confirmed possible by direct inspection of
   the real records before any new field was considered).
3. **`"ambiguous"`** — only evaluated when the caller supplies
   `bridging_check_ids` (the set of distinct `check_id`s a Claim's own
   *existing* `supporting_evidence`/`contradicting_evidence` already
   bridges to): no `depends_on` of its own, but citing more than one
   distinct check's worth of bridging Evidence. Nothing structural
   establishes this Claim is genuinely scoped to a single check, so
   this fails closed rather than guessing — the real knowledge base
   never constructs this shape today, but nothing prevents a future
   contract from doing so, and the mechanism must not silently assume
   single-check scope merely because no `depends_on` was authored.
4. **`"eligible"`** — none of the above; the only category the
   automatic mutation path may ever act on.

A Claim found `"aggregate"`/`"ambiguous"` is never turned into a
`ContributingFinding`/manifest item — `write_source_reconciliation_
manifest` instead records it in a new, purely informational
`[[affected_claims]]` array, parallel to but never read by
`apply_manifest`'s own dispatch (which only ever reads
`data["items"]`): visible, never silently discarded, but reachable only
through a separately justified, human-reviewed mechanism this
corrective pass does not build. `knowledge verify-changes` prints each
one (`affected, not auto-reconciled: ...`).

This is deliberately **not** a general-purpose dependency-reasoning
engine (the dispatch's own explicit constraint): `claim_scope_category`
answers one narrow question — may this specific write path touch this
specific Claim — using only fields the Claim record already carries,
never attempting to resolve what a broader Claim's own correct support
state *should* be from its dependencies' states.

### 2. Reconciliation-manifest filenames could collide within one
second, overwriting a still-pending review

`write_source_reconciliation_manifest` names its file
`{YYYYMMDDTHHMMSSZ}-source.toml` — one-second precision — and wrote it
unconditionally. Two `verify-changes` calls for the same slug landing
in the same wall-clock second would target the same path; the second
write would silently replace the first, discarding any review decision
already recorded against it.

**Decided**: a new, narrow helper, `knowledge_intermediate._write_
manifest_exclusive(dir_path, base_stem, render, *, suffix=".toml")`.
`render(stem)` returns the full manifest text for a candidate `stem`,
called fresh per attempt so a disambiguated filename's own embedded
`manifest_id` always matches it. Exclusivity is enforced at the
filesystem level: the text is first written to a private temp file in
the same directory, then atomically **linked** (`os.link`, which raises
`FileExistsError` rather than silently replacing an existing
destination the way `os.rename` would on POSIX) to the real candidate
path. On a genuine collision, a new, short, random disambiguating
suffix is appended to the stem and the whole attempt (render +
temp-write + link) is retried from scratch, bounded to 1000 attempts.
A crash while writing the temp file leaves only an orphaned,
never-linked `.tmp-` file behind — never a partial, readable file at a
real manifest path (every existing reader globs `*.toml` specifically).

This is scoped to `write_source_reconciliation_manifest` alone, per the
dispatch's own instruction not to introduce a new manifest-management
subsystem — `write_manifest`/`write_doc_candidates_to_manifests`
(Phase 81/87's own manifest writers) are untouched; their own
timestamp-collision exposure, if any, is out of scope for this pass.

`_serialize_manifest` is extended, additively, to also serialize
`data.get("affected_claims", [])` as its own `[[affected_claims]]`
array-of-tables — a manifest with no such key (every one written
before this corrective pass) round-trips identically; `apply_manifest`'s
own read-modify-write preserves it unchanged across an apply, since its
own loop only ever reads/writes `data["items"]`.

## Consequences

- `knowledge_intermediate.claim_scope_category` is new, public (no
  leading underscore — this module's own convention for a helper
  reused across module boundaries), pure, and reads only fields already
  present on a `KnowledgeRecord` plus a caller-supplied bridging set.
- `source_reconciliation.ReconciliationProposal` gains one new field,
  `affected_claims: list[AffectedClaim]` — additive; `propose_
  reconciliation`'s existing callers (`cli.py::knowledge_verify_changes`,
  every test call site) were updated to read `.findings` exactly as
  before, now alongside `.affected_claims`.
- `write_source_reconciliation_manifest` gains one new optional
  parameter, `affected_claims`; omitting it writes an empty
  `[[affected_claims]]` section, a harmless no-op for any caller that
  does not thread it through.
- `_apply_source_reconciliation` refuses, fail-closed, any manifest item
  naming a non-`"eligible"` Claim — including one that never went
  through `propose_reconciliation`'s own gate at all (a hand-edited or
  otherwise malformed manifest item), confirmed by a dedicated
  regression test.
- No change to `OracleResult`'s schema, `oracle.py`'s existing
  precedence logic, `decisions/0096`/`0097`'s own four-plus-three
  original tradeoffs, or the shared-test-input baseline-eligibility
  mechanism `decisions/0097` introduced (which operates per-*check*,
  via `required_by_path`/`accounted_by_path`, never per-Claim — an
  aggregate Claim being excluded from mutation does not and must not
  block a shared path's baseline from advancing once every check
  sharing it is genuinely, validly accounted for; confirmed by a
  dedicated regression test and by the real Ledgerkit demonstration
  below).

## Real Ledgerkit demonstration (summary)

Against a disposable copy of the real `balance-from-spec` knowledge
base and a disposable copy of `~/projects/ledgerkit` (never the real
checkout of either), with `CL-BFS-001`/`CL-BFS-002` temporarily set to
`partially_supported`/`proposed` in the scratch copy only (so a fresh
re-verification produces a genuine finding rather than a documented
no-op, `decisions/0096` §4.3): editing only `tests/test_reports.py` and
re-syncing correctly produced two independent `test_input_change`
findings (one per check sharing the file); `verify-changes` proposed
exactly two actionable items (`CL-BFS-001`, `CL-BFS-002`) and reported
`CL-BFS-005` as `affected, not auto-reconciled` (category `aggregate`)
for both checks; `CL-BFS-003` never appeared anywhere. Accepting and
applying both items correctly moved `CL-BFS-001`/`CL-BFS-002` to
`supported` with new Evidence citations, left `CL-BFS-003`/`CL-BFS-004`/
`CL-BFS-005` byte-for-byte unchanged, and — because *both* checks
sharing the file were successfully, validly accounted for — correctly
advanced the shared `tests/test_reports.py` baseline. A subsequent
newly-coverable-check demonstration (adding the real, pinned
`test_section_accounts_overlapping_patterns_no_double_count` test named
by `REQ-BFS-002`'s own example) confirmed detector (b)'s own
reconciliation of `CL-BFS-004` remains fully functional, unaffected by
this corrective pass. See `planning/retros/phase-89-stage-89a-second-
corrective-ledgerkit-demonstration.md` for the full log.
