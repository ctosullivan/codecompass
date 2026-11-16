# Phase 89: Incremental Knowledge and Documentation Reconciliation — plan

## 0. Status

**Planning only. Implementation not authorised.** Drafted 2026-11-16,
independently of MCP transport, as the Phase 88 acceptance-exercise
dispatch's own §3-§6 instructions require.

**Amended once** (2026-11-16), after an independent `Plan`-type review
(`planning/retros/_review-phase89-plan.md`) returned **NOT READY** on
two blocking findings: (1) §4.4/§5.3's original draft claimed the new
reconciliation-apply step "reuses" `_apply_requirement_proposal`'s own
field-update pattern — false by direct reading; every existing
apply-path function in `knowledge_intermediate.py` only ever creates a
brand-new competing record, never mutates an existing one in place,
and the codebase's own documented convention says so explicitly. The
original draft also left an unaddressed self-conflict risk (two
accepted reconciliation items against the same Claim in one batch would
spuriously trip the reused whole-file-hash conflict check against each
other, not only against a genuine human edit). Fixed in §4.4/§4.8/§5.1/
§5.3 below: the deviation from "never mutate in place" is now narrowly
scoped (exactly two machine-derived fields, never `statement`/
`derivation`), explicitly disclosed and justified rather than
mischaracterised as reuse, and the self-conflict risk is closed by
merging same-Claim findings into one manifest item at proposal time
rather than ever producing two. (2) `apply_manifest` has one real
production call site (`cli.py::knowledge_apply_manifest`, `codecompass
knowledge apply`) and `CLAUDE.md` §1's L-021 requires this plan's own
verification section to name and test through it directly — the
original Stage 89A test list did not; fixed in §7 below. Two
non-blocking inventory inaccuracies in the original §1.1 (undercounting
`apply_manifest`'s real recognised kinds and `find_gaps`'s real gap-kind
taxonomy) are also corrected in place.

**Re-reviewed** (2026-11-16, fresh independent `Plan`-type dispatch,
full re-verification from scratch against real source, not taken on
trust from either the plan's or the first review's own account):
**READY WITH NON-BLOCKING OBSERVATIONS** (`planning/retros/
_review-phase89-plan.md`, "Re-review" section). Both blocking findings
confirmed genuinely resolved. The re-review also caught that the first
correction's own `find_gaps` gap-kind count (said "seven") was itself
still wrong — the real count `find_gaps` itself emits is six, now
corrected in §1.1 below — and surfaced two further, real, non-blocking
write-semantics gaps the merge-based fix introduced (a merged item
with disagreeing fresh outcomes never specified which field(s) to
write; a merged item's own multi-record write had no idempotency guard
against a crash-and-retry duplicating an already-written Evidence
record) — both resolved in place in §4.8/§5.3/§9 below by reusing two
more already-existing project mechanisms (`evidence_support_state:
"conflicting"`; the same `_find_existing_promoted_record` idempotency
check every other apply-path function already uses), per the
reviewer's own recommendation, rather than triggering a third full
review round. **This plan is READY.** Implementation remains
unauthorised pending a separate, explicit go-ahead.

**Amended a third time** (2026-11-16, fresh independent-orchestrator
dispatch, "Phase 89 Final Planning Amendment"): a from-scratch,
line-by-line source re-verification — not trusting either prior round's
own account — found that this plan's own §6.1 Task A walkthrough rested
on an assumption that **does not hold**, plus a more fundamental reason
the Evidence-identity design in the second amendment above was still
unsound, a real exit-gate overclaim, and a real baseline/sync-ordering
gap. See §0.1 immediately below for exactly what was found and why;
§1.2, §3, §4.1-§4.4, §4.8, §5.1-§5.4, §6, and §9 are rewritten in place
accordingly. **This plan is NOT YET re-reviewed following this
amendment** — a fresh independent `Plan`-type dispatch against the
amended text (§9) is required before READY can be re-claimed; the
second amendment's own READY verdict above applied to the plan as it
stood *before* this round and no longer describes the plan's current
text.

### 0.1 What this amendment found, and why the prior draft was wrong

**A. The Task A walkthrough's core assumption is false, source-verified
directly.** §6.1's prior text assumed `change_impact.assess(run_checks=
True)` would, on its own, discover the newly-added Ledgerkit test and
propose upgrading `CL-BFS-004`. Tracing `classify_symbol`/`assess`
line-by-line (`change_impact.py:318-415`, `510-586`) against the real
`CL-BFS-004.yaml` (`supporting_evidence: [EV-BFS-001]`, a **source**-kind
Evidence only) and the real `oracle-contract.yaml` (a `required: true`
third check whose `check_reference` names a test that does not yet
exist) proves this mechanism **structurally cannot** do what the prior
walkthrough assumed: `assess()`'s own `check_contributors` (line
549-561) is populated *exclusively* from `behavioural_risk`-tier
`ClaimFinding`s, and a finding only reaches `behavioural_risk` when
`classify_symbol`'s own `test_evidence_check_id` bridge (line 371-394)
already has an entry for it — built *exclusively* from **pre-existing**
test-kind Evidence records that already cite a resolvable
`OracleResult`. `CL-BFS-004` has no such Evidence yet — that is the
entire, real, previously-documented point of the gap this task exists
to close (`DEC-BFS-002`'s own rationale). So `assess(run_checks=True)`
classifies `CL-BFS-004` as `relevant_no_coverage_link` (exactly as it
already is today) and **never calls `run_check_assurance` for the new
check at all** — not a hypothetical edge case, a structural
precondition the prior walkthrough never actually traced. §4.1-§4.3,
§5.1, §6.1 below are rewritten around a second, genuinely new detector
this gap requires.

**B. The Evidence-identity/idempotency design was unsound, for a reason
more fundamental than the one the second amendment already disclosed.**
Direct grep across `src/codecompass/*.py` confirms **zero existing call
sites** create a new Evidence record programmatically (`_next_id(sdir,
"EV")` never appears anywhere) — every existing apply-path function
only ever creates a new *Claim*. `_find_existing_promoted_record`
(`knowledge_intermediate.py:2103-2145`) is explicitly typed: it matches
by `kind` (`"claim"` by default) against a record's own `statement`
field — Evidence records have no `statement` field at all (they have
`what_it_shows`), so this helper cannot be reused for Evidence identity
under any parameterisation; this is a type mismatch, not merely an
imperfect fit. Separately, and newly discovered this round:
`apply_manifest`'s own per-item `state: "applied"` persistence (the
mechanism the second amendment's §4.8 leaned on for crash safety) is
**buffered for the whole manifest, not written per item** —
`manifest_path.write_text(...)` runs exactly once, after the entire
`for item in data.get("items", [])` loop completes
(`knowledge_intermediate.py:2542-2543`) — so a crash partway through a
multi-item batch leaves **every** item in that run's own `state` field
exactly as it was before the run started, including items that had
already been successfully applied earlier in the very same crashed run.
The real, load-bearing crash-safety guarantee in this codebase today is
therefore never "the manifest's own persisted state flag" — it is each
individual `_apply_*` function's own idempotent, content-based dedup
against the canonical records themselves (`_find_existing_promoted_
record`, safe to re-run because it is re-checked fresh on every call,
against disk state, not against the manifest's own bookkeeping).
Phase 89's new apply branch must provide the equivalent guarantee for
Evidence from scratch, there being no existing Evidence-identity
convention to mirror. §4.4, §4.8, §5.3 below are rewritten accordingly.

**C. The exit-gate / negative-result question was a real, confirmed
inaccuracy, not a defensible interpretation.** `planning/v2-roadmap.md`
§9 (line 702-705, re-read directly) states the exit gate in one
sentence: "The second task measurably benefits from the first,
evidenced... not asserted — achieved without any dependency on an MCP
server." No clause there, or in `decisions/0085` §3, permits an
honestly-reported negative result to satisfy this gate. §6.3/§8/§9
below now distinguish three genuinely separate questions the prior §8
conflated into one.

**D. The baseline/sync-ordering gap is real, with a concrete failure
mode.** §4.1's prior detector reads a file's hash from `repo_root`'s own
`context-graph.db` (`source_files.content_hash`) and compares it against
the persisted baseline. `change_impact.py::resolve_changed_range` (line
206-290), re-read directly, already has to guard against exactly this
value going stale — it independently recomputes the *live* on-disk hash
(`oracle_mod.sha256_file(live_path)`) and reports a distinct
`"stale_index"` status whenever it disagrees with the graph's own
recorded value, precisely because `codecompass sync` populates that
column and nothing keeps it current automatically. §4.1's prior detector
**never performed this same live-vs-graph check before trusting the
graph's own recorded hash as "current"** — a source file edited after
the last `sync` but before detection runs would be compared against the
baseline using a *stale* graph-recorded hash, silently reporting
"unchanged" even though the file genuinely changed on disk. §4.1, §5.1,
§5.2 below close this by requiring the same live-hash cross-check
`resolve_changed_range` already performs, reused directly, before any
baseline comparison is trusted.

**Two further semantic corrections (dispatch §3), independently
verified:**

- `change_impact.py::run_check_assurance` (line 436-478) labels *any*
  fresh effective `FAIL` `CONFIRMED_REGRESSION` unconditionally — it
  never checks whether a historical `PASS` for the same `check_id` ever
  existed. Every existing use of this classification in `decisions/
  0086`/`0087`/`planning/phase-83-semantic-change-assurance.md`
  (re-read directly) is written for the scenario where a prior `PASS`
  did exist and a mutation broke it — the term is accurate there.
  `decisions/0087` §1 deliberately fixes *historical PASS never masking
  a fresh FAIL*, not the reverse question this amendment raises (a fresh
  FAIL with **no** historical PASS at all — a newly discovered failure,
  not a demonstrated regression). Per this amendment's own governing
  dispatch, Phase 83's own classification is left **completely
  unmodified** — relabelling `CONFIRMED_REGRESSION` itself would be
  exactly the kind of Phase-83-semantics change this plan must not make,
  and it is not Task A's own scenario, which expects a `PASS`, not a
  `FAIL` — instead, §4.3 below adds a narrow, additive, Phase-89-level
  distinction, read from data `change_impact.py` already returns
  unchanged (`AssuranceFinding.observed_outcomes`/`aggregate_state`),
  surfaced alongside the unmodified classification, never in place of
  it.
- A disposable, schema-governed document proves the *mechanism*
  (`detect_grounded_region_changes` correctly fires `claims_changed`)
  but proves nothing about whether real documentation content a real
  Ledgerkit task would actually consult got measurably better. §6.2/§6.3
  below now require both pieces of evidence separately, never one
  standing in for the other.

## 1. Verified current state (re-confirmed this session, not assumed)

- Phase 88 (Agent Integration and MCP) is `done` (`planning/ROADMAP.md`,
  `planning/CONTEXT.md`). A real-agent MCP acceptance exercise for Phase
  88 was completed in this same session —
  `planning/retros/phase-88-mcp-real-client-acceptance.md` — independent
  of this plan; Phase 89 does not depend on it or on MCP at all.
- Phase 84 (knowledge API) and Phase 87 (documentation schema/
  compilation) are both `done` — the two real prerequisites named by
  `decisions/0085` §3 and `planning/v2-roadmap.md`'s own Phase 89
  section (lines ~115-155 there). **Phase 89 does not depend on Phase
  88** — confirmed independently deliverable, re-verified directly
  against `planning/v2-roadmap.md` rather than assumed from this
  dispatch's own framing.
- `decisions/0085` §3 is the governing split decision: the old merged
  Phase 88 was split into Phase 88 (MCP, done) and Phase 89 (this plan),
  "independently deliverable... carries forward the former Phase 85's
  full original content." §3 names the architectural constraint this
  plan must honour: build a **change-driven trigger** layered on the
  **existing** reconciliation flow — never a new scheduler, event bus,
  competing knowledge store, or documentation compiler, and never a
  redesign of Phase 87's own compiler.

### 1.1 Source-verified capability inventory (direct source reading this
session, not assumed from any plan's own prior description)

- **`src/codecompass/knowledge_intermediate.py`** (Phase 81, packaged):
  - `detect_anchor_changes`/`write_manifest`/`apply_manifest` — the
    existing three-stage reconciliation flow (detect → human-reviewed
    manifest with `decision: "accept"/"reject"` → apply, the *only*
    stage allowed to write a canonical record, re-validating
    mechanically rather than trusting the review stage's own say-so).
    Today this flow's only detector is `detect_anchor_changes` (dual-
    hash: canonical-record hash vs. rendered-Markdown-projection hash,
    §1.5 of Phase 81's own plan) — triggered by a human/tool edit to an
    `intermediate/*.md` projection, **never** by a source-code or test
    change. This is the flow Phase 89 extends with a *second* detector,
    not replaces.
  - `detect_grounded_region_changes` — the Phase 87 five-state
    (`new`/`noop`/`doc_candidate`/`claims_changed`/`concurrent_conflict`)
    documentation-region reconciliation. Critically: `claims_changed`
    already fires whenever a cited Claim/Evidence/Decision record's own
    **file content hash** (`_current_cited_hashes`,
    `knowledge_intermediate.py:315-320`) differs from the hash recorded
    in `.grounding-state.toml` at the region's last baseline — it has
    **no dependency on MCP, on `docs maintain`'s own caller, or on how
    the Claim's content came to change**. This means: once a Claim's own
    file is correctly updated by anything, this *already-shipped,
    unmodified* mechanism correctly cascades that into documentation
    invalidation. Phase 89 therefore needs **zero new doc-reconciliation
    code** — only a correct way to get the Claim's file updated in the
    first place, on a real source/test change, with human approval.
  - **Corrected by independent review**: `apply_manifest`'s real
    dispatch already recognises **three** kinds today, not two —
    `write_manifest`'s own `"anchor_edit"`/`"candidate_addition"`, plus
    a third, `"doc_region_edit"`, written not by `write_manifest` but by
    a separate, already-existing **sibling writer function**,
    `write_doc_candidates_to_manifests` (called from `docs maintain`).
    This is the real precedent §9's own "sibling writer vs. extend
    `write_manifest`" question needed and the original draft missed
    citing: Phase 89 adds its fourth kind, `"source_reconciliation"`
    (§5.3), via its own new sibling writer function,
    `write_source_reconciliation_manifest` — mirroring `write_doc_
    candidates_to_manifests`'s own already-production pattern exactly,
    not extending `write_manifest` itself (§9's open question, now
    resolved by this precedent rather than left undecided).
- **`src/codecompass/change_impact.py`** (Phase 83, relocated/packaged
  at Phase 88): `classify_symbol` resolves a changed `(symbol, path)`
  pair against citing `source`-kind Evidence, then against Claims whose
  `supporting_evidence` cites that Evidence, tiered
  `no_recorded_relationship`/`relevant_no_coverage_link`/
  `behavioural_risk` — and, for `behavioural_risk` findings with a
  resolvable `test`-kind Evidence bridging to a real oracle check,
  `assess(..., run_checks=True)` re-executes that check fresh and
  classifies `CONFIRMED_REGRESSION`/`VERIFIED_SCOPE`/`VERIFICATION_GAP`/
  `INVALID_ASSESSMENT` from the **fresh result's own effective outcome
  alone** (`decisions/0087` §1, never the aggregate). **This already is
  the "source/test change → affected canonical knowledge, staleness
  distinguished from unrelated change" primitive** (planning decisions
  #1-#3 below) for a change whose `changed[path:start-end]` range is
  already known. What it does **not** do: discover *which* ranges
  changed on its own (it is handed an explicit range, by design — no
  `git diff` parsing, Phase 83's own stated non-goal), and it never
  writes anything back to `planning/knowledge/` (by design — read-only
  classification).
- **`src/codecompass/graph.py`**: `source_files.content_hash` (Phase 77,
  confirmed present in the schema this session,
  `graph.py:77/139/238/794-795`) is already populated by `codecompass
  sync` for any project (including a target repo like Ledgerkit, once
  *that* repo has its own synced `context-graph.db` — already a stated
  precondition of `change_impact.assess`, unchanged here). This is the
  one new primitive's own data source (§5.1) — no new schema, no new
  table.
- **`src/codecompass/knowledge_api.py`** (Phase 84): `find_gaps`'s `Gap`
  taxonomy is the existing, extensible gap-reporting shape. **Corrected
  twice by independent review** (the first correction's own count was
  itself still wrong, caught by a fresh re-review that traced every
  `Gap(kind=...)` append directly): `find_gaps` itself (plus its own
  helper, `_find_gaps_for_slug_contract`) actually emits **six** kinds —
  `contradiction`/`dangling_evidence_reference`/`dangling_dependency_
  reference`/`missing_contract`/`unverified_required_scope`/
  `stale_test_citation` — not the four named in the original draft nor
  the seven claimed in the first correction. The shared `Gap` dataclass's
  own type-comment (`knowledge_api.py:140-141`) documents a seventh
  value, `missing_evidence`, but that one is emitted only by a
  *different*, sibling function, `trace_evidence` — never by
  `find_gaps` itself; the original and first-corrected drafts both
  conflated "kinds the shared `Gap` type names across every producer"
  with "kinds `find_gaps` itself emits." Independently re-verified,
  twice, that Phase 89's proposed new kind,
  `claim_contradicted_by_fresh_check` (§5.4), is genuinely distinct from
  the two adjacent existing ones, not duplicative: `"contradiction"`
  fires on an *already-recorded, already-promoted*
  `contradicting_evidence`/`status=contradicted` state; `"stale_test_
  citation"` fires on a *cited* result being digest-invalid while an
  *uncited* current result passes. Neither covers this phase's own new
  condition — a *pending, unapplied* manifest item proposing a fresh
  `CONFIRMED_REGRESSION` that nobody has reviewed yet. Phase 89 reuses
  the same `Gap` dataclass and `find_gaps`'s existing scan loop — not a
  parallel report format.
- **Phase 87 `docs` CLI sub-app** (`cli.py`): `compile`/`maintain`/
  `publish`/`record-review` are **unchanged by this plan** — Phase 89
  never touches `doc_compiler.py`, `spec_docs.py`'s own section-mapping
  logic, or the clean-room composition step. `docs maintain`'s existing
  discovery (every `**/*.schema.yaml`) and its existing five-state
  reconciliation already do the documentation half of this phase's own
  objective, for free, once a Claim's file is correctly updated.

### 1.2 Newly verified this round (direct source/record tracing, not
assumed from either prior amendment's own account)

- **`apply_manifest`'s per-item `state: "applied"` write is buffered for
  the whole batch, not persisted per item.** `manifest_path.write_text
  (_serialize_manifest(data), ...)` (`knowledge_intermediate.py:
  2542-2543`) runs exactly once, *after* the entire `for item in
  data.get("items", [])` loop finishes — every item's in-memory `state`
  mutation (line 2535-2538) before that point is lost if the process
  crashes mid-loop, even for items already successfully applied earlier
  in the same run. The real, already-existing crash-safety guarantee in
  this codebase is each `_apply_*` function's own idempotent,
  content-based dedup against the canonical records on disk
  (`_find_existing_promoted_record`), re-checked fresh on every call —
  never the manifest's own bookkeeping field. §4.4/§4.8/§5.3 are
  rewritten to provide the equivalent guarantee for the new Evidence-
  writing branch, since no existing convention already does.
- **No existing code path creates a new Evidence record.** Grepped
  directly: `_next_id(sdir, "EV"` has zero matches anywhere in `src/
  codecompass/`. Every existing `apply_manifest` branch
  (`_apply_anchor_edit`/`_apply_candidate_addition`) only ever creates a
  new *Claim*. Phase 89's `"source_reconciliation"` branch is the first
  mechanized Evidence-creation path this codebase will have — stated
  plainly, not characterised as extending an existing pattern.
- **`classify_symbol`/`assess(run_checks=True)` cannot discover a check
  that no Evidence record has ever yet cited.** Traced directly against
  the real `CL-BFS-004`/`oracle-contract.yaml` records (§0.1.A): the
  `behavioural_risk` tier — the only tier `assess()`'s own
  `check_contributors` reads from (`change_impact.py:559-561`) — is only
  reached via `classify_symbol`'s own `test_evidence_check_id` bridge
  (line 371-394), built exclusively from Evidence records that already
  cite a resolvable `OracleResult`. A required check with **zero**
  citing Evidence (today's real state for `overlapping-account-
  patterns-no-double-count`) is invisible to this entire pathway. This
  pathway remains fully valid, unchanged, and still Phase 89's own
  primary mechanism for its *other*, already-working case — a source
  change to a scope that **already has** a test-Evidence bridge (e.g.
  `CL-BFS-001`/`CL-BFS-002`, both already bridged via `EV-BFS-002`/
  `EV-BFS-003`) — see §4.1/§6.2's "re-verification" scenario below.
- **No structural field links a specific oracle `check_id` to the
  specific Requirement/Claim it is pinned for, when more than one check
  shares one contract.** `oracle-contract.yaml`'s own `contract_id`
  (`scripts/check_contracts.py::check_contract_id_resolves`, line
  127-148) resolves to exactly one governing `REQ-` record **for the
  whole contract** (here, `REQ-BFS-001`) — not per-check. `REQ-BFS-002`
  governs the contract's *third* check, but nothing machine-checkable
  says so today; the only existing link is informal prose (`REQ-BFS-002.
  yaml`'s own statement happens to embed the literal string
  `"overlapping-account-patterns-no-double-count"`, which happens to
  equal that check's `check_id` — a convention, not a schema field,
  and not even used consistently: `CL-BFS-001`/`CL-BFS-002`'s own
  equivalent prose embeds the check's `scope` text, not its `check_id`).
  §4.2/§5.1 add one small, additive, optional field to close this
  specific, real gap.
- **`oracle.py`'s own `evaluate_result_precedence`** (line 865-929,
  re-read directly) already recomputes `test_input_digest` against
  `check.test_input_paths` (which already lists `tests/test_reports.py`)
  for an *existing* result, and already reports `INVALID` when it
  disagrees with what is currently on disk — this is the already-shipped
  mechanism for "an existing result's own test file changed under it,"
  genuinely distinct from "no result has ever existed for this check at
  all" (Task A's real scenario, §0.1.A). Phase 89 reuses the former
  unchanged for the re-verification scenario and adds the latter as a
  new, narrow, separate detector (§4.1/§5.1).

## 2. Objective

A real source or test change to a target repository (Ledgerkit) is
**detected**, the canonical knowledge it affects is **identified** and,
on explicit human approval, **reconciled** (new Evidence added, a
Claim's `evidence_support_state` updated — never silently overwritten),
and the documentation sections that depend on that knowledge are
correctly **invalidated and selectively regenerated** — while every
unrelated document, Claim, and previously accepted editorial change is
left untouched. A second genuine Ledgerkit development task then
measurably benefits from the knowledge reconciled during a first one.
Matches `planning/v2-roadmap.md`'s Phase 89 section and `decisions/0085`
§3 exactly; this plan operationalises it, corrects nothing in it.

## 3. Architecture

Two sibling detectors feed one shared manifest writer — not one
detector trying to cover both cases, since §0.1.A proves they are
genuinely different conditions with different evidence shapes:

```
Target repo source/test change (Ledgerkit, or any CodeCompass-indexed
project)
      │
      ├─────────────────────────────────────────────────────────┐
      ▼                                                           ▼
[NEW] detect_source_changes()                      [NEW] detect_newly_
  -- re-verification of an            coverable_checks()
  ALREADY test-Evidence-bridged         -- a required check (oracle-
  scope (e.g. CL-BFS-001/002 via        contract.yaml) with ZERO citing
  EV-BFS-002/003). For each               Evidence yet, whose own
  tracked source file: FIRST            check_reference test now
  cross-checks the graph's own          genuinely collects in
  recorded source_files.content_hash    repo_root (a `pytest
  against the LIVE on-disk hash         --collect-only` probe, never a
  (reusing oracle.sha256_file exactly   full run) -- i.e. a previously-
  as change_impact.resolve_changed_     uncovered, REQUIRED obligation
  range already does, §0.1.D) --        has just become coverable by a
  reports a distinct "stale_graph_      genuine new test. Resolves the
  index" finding and refuses to         check_id -> governing Claim via
  compare against the baseline at all   REQ-*.check_id (NEW, optional,
  if they disagree (never silently      additive Requirement field,
  trusting a graph not yet re-synced    §4.2/§5.1) -> REQ's own
  by that repo's own `codecompass       depends_on. This is Task A's own
  sync`). Only once confirmed fresh     real scenario (§0.1.A) --
  does it compare the graph's own       assess()'s existing
  content_hash against the persisted   behavioural_risk/
  per-slug baseline                     check_contributors pathway
  (source-baseline.toml, §5.2).         cannot reach an uncovered check,
  produces: list[(path,start,end)]      by construction (§1.2).
  candidate changed ranges              produces: list[(check_id,
      │                                 claim_id)] newly-coverable pairs
      ▼                                         │
change_impact.assess(changed=...,               ▼
  run_checks=True)  (Phase 83,          oracle.evaluate_check(...) run
  REUSED, UNCHANGED)                     directly (Phase 82, REUSED,
      │  produces: per-range            UNCHANGED) -- the check's own
      │  Claim/Requirement findings,     fresh OracleResult
      │  tiered no_recorded_
      │  relationship /
      │  relevant_no_coverage_link /
      │  behavioural_risk, and for
      │  behavioural_risk with a
      │  bridging check, a fresh
      │  CONFIRMED_REGRESSION /
      │  VERIFIED_SCOPE /
      │  VERIFICATION_GAP /
      │  INVALID_ASSESSMENT
      │  classification -- each
      │  additionally annotated
      │  (NEW, §4.3) with whether a
      │  historical PASS for this
      │  exact check_id existed
      │  BEFORE this fresh result
      │  (observed_outcomes, Phase
      │  83's own existing return
      │  data, unchanged) --
      │  distinguishing a genuine
      │  regression from a newly
      │  discovered failure, never
      │  relabelling Phase 83's own
      │  classification itself
      └─────────────────────┬─────────────────────┘
                             ▼
[NEW, narrow] write_source_reconciliation_manifest(...)
      — a new SIBLING WRITER function (mirroring the already-production
        write_doc_candidates_to_manifests exactly, §1.1's corrected
        inventory — not an extension of write_manifest itself). Takes
        findings from EITHER detector above, uniformly. ONE manifest
        item PER CLAIM (never per-finding): every CONFIRMED_REGRESSION/
        qualifying VERIFIED_SCOPE finding against the SAME Claim in one
        detection run is merged into that one item's own list of
        proposed new-Evidence citations, closing the self-conflict risk
        below by construction (never two pending items racing the same
        Claim's own hash). Each contributing finding carries its own
        oracle run's full identity (contract_id, check_id, run_id,
        raw_output_ref — §4.4/§5.3's new Evidence-identity mechanism).
        state="pending", decision="undecided" (Phase 81's existing
        3-stage review convention, REUSED)
      │
      ▼  (human sets decision: "accept"/"reject", exactly as today)
apply_manifest()   (Phase 81, REUSED — one new recognised `kind`, §5.3;
                     writes one new Evidence record PER contributing
                     finding, append-only, FIRST checking a new, narrow
                     Evidence-identity helper keyed on (contract_id,
                     check_id, run_id) — not _find_existing_promoted_
                     record, which is typed for claim/requirement
                     statement-text matching and cannot represent
                     Evidence identity at all (§0.1.B/§4.4) — so a crash
                     partway through a merged item's own multi-record
                     write is safe to retry without duplicating evidence
                     already written, exactly the same real guarantee
                     every existing _apply_* function already provides
                     for its own record kind, provided here for the
                     first time for Evidence specifically + a narrowly-
                     scoped, EXPLICITLY DISCLOSED deviation from this
                     flow's own "never mutate, always create a
                     competing record" convention: appends to the
                     Claim's own contradicting_evidence/
                     supporting_evidence fields ONLY (each append itself
                     idempotency-checked, §4.8) and RECOMPUTES
                     evidence_support_state from the Claim's own FULL,
                     accumulated contradicting_evidence/
                     supporting_evidence contents after the append —
                     never merely from this batch's own findings, so an
                     earlier batch's contradiction can never silently
                     disappear (§4.4/§4.7) — statement/derivation/
                     timestamp/every other field is never touched; see
                     §4.4 for why this specific, narrow exception is
                     justified rather than built around. Only ever runs
                     after explicit human "accept")
      │
      ▼  (the Claim's own file content hash has now genuinely changed)
detect_grounded_region_changes() → docs maintain → docs compile/publish
      (Phase 87, COMPLETELY UNCHANGED — already reacts correctly to any
       cited Claim's content hash changing, regardless of cause)
```

No new scheduler, event bus, knowledge store, or documentation
compiler. The one new module (`src/codecompass/source_reconciliation.py`,
§5) is two thin sibling detectors plus one shared new sibling manifest
writer plus one new `apply_manifest` branch; everything else in the
diagram above is Phase 81/82/83/87/84 code, unmodified.

## 4. Required planning decisions

### 4.1 How source/test changes are detected, identified, and compared
with known baselines

**Two genuinely different conditions (§0.1.A), two sibling detectors —
not one trying to cover both:**

**(a) `detect_source_changes(project_root, slug, *, repo_root)`
(§5.1) — re-verifying an already-covered scope.** For every `source`/
`test`-kind Evidence record under `slug` whose `source_ref`/`test_ref`
names a file under `repo_root`: **first**, confirm `repo_root`'s own
`context-graph.db` is actually fresh for that file — recompute the
*live* on-disk hash (`oracle.sha256_file`, reused directly, exactly the
function `change_impact.resolve_changed_range` already calls for this
same purpose) and compare it against the graph's own recorded
`source_files.content_hash`; a disagreement is reported as a distinct
`"stale_graph_index"` finding and that file is **excluded from this
run's comparison entirely** (never compared against the baseline using
a hash already known to be stale — §0.1.D). Only once confirmed fresh
is the graph's own `content_hash` compared against the hash persisted in
`source-baseline.toml` the last time this slug was reconciled. A file
with no baseline entry is reported `new` (first-ever reconciliation for
that file) and its baseline is *not* established by detection alone
(mirrors `detect_grounded_region_changes`'s own `"new"`-is-read-only
rule exactly — establishing a baseline is a separate, explicit act,
`establish_source_baseline`, never a side effect of looking). The
required order is therefore always: edit source/test → `codecompass
sync` (in `repo_root`) → `detect_source_changes` — stated explicitly as
a documented precondition, and fail-closed (a `"stale_graph_index"`
finding, never a silent false negative) when violated, rather than
trusted to always happen in that order. No `git diff` parsing — content-
hash comparison only, Phase 83's own already-established technique.
Feeds into `change_impact.assess(changed=..., run_checks=True)`
unchanged — valid for a scope **already** bridged by test-Evidence (e.g.
`CL-BFS-001`/`CL-BFS-002`), not for a never-yet-covered one (§0.1.A).

**(b) `detect_newly_coverable_checks(project_root, slug, *, repo_root)`
(§5.1) — a required check closing real coverage for the first time.**
For every `required: true` check in the slug's own `oracle-
contract.yaml` with **zero** currently-valid historical `OracleResult`
(computed exactly as `scripts/check_contracts.py`'s own existing
`current_pass_check_ids` logic already does, reused not reinvented,
§1.2): probe whether `check.check_reference`'s named test now actually
collects in `repo_root` (`pytest --collect-only -q <check_reference>`,
a new, narrow, read-only use of the existing subprocess machinery
`oracle.run_pytest_check` already uses — a collection probe, never a
run, so a collecting-but-still-failing test is distinguished from a
test that does not exist at all). A check that now collects is "newly
coverable" — this is Task A's own real scenario (§0.1.A, §6.1).
`detect_source_changes` (a) and `detect_newly_coverable_checks` (b) are
never run against the same check in the same way: (a) only ever
re-verifies a check that test-Evidence already bridges; (b) only ever
fires for a check with no bridging Evidence at all yet. A check cannot
be in both states at once, so the two detectors' own outputs never
overlap or need reconciling against each other.

### 4.2 How changes map to Claims/Requirements/Evidence/Decisions and
dependent documentation regions

**For detector (a) (an already-bridged scope)**: reused unchanged —
`change_impact.classify_symbol` (Claim/Requirement mapping, via existing
`source_ref`/`supporting_evidence` citations) and `detect_grounded_
region_changes` (documentation-region mapping, via existing `cited_ids`
grounding markers). No new mapping table for this case — both already
exist and already key off the same canonical record ids.

**For detector (b) (a newly-coverable, previously-uncovered required
check)**: `classify_symbol`'s own bridge cannot be used — that is
exactly what is missing (§0.1.A/§1.2). **One small, additive, optional
field** closes this, rather than a new mapping table or a prose-matching
heuristic: `check_id` on a Requirement record, naming the exact
`oracle-contract.yaml` `check_id` that Requirement pins (set once, by a
human, at the same moment a Decision pins a new required scope — e.g.
`REQ-BFS-002.yaml` would carry `check_id: overlapping-account-patterns-
no-double-count`, backfilled as a narrow, editorial, non-semantic
addition to an already-existing record, the same class of safe
bookkeeping addition §4.4 below already justifies for Evidence
citations). `detect_newly_coverable_checks` resolves `check_id` → every
Requirement naming it → that Requirement's own existing, unchanged
`depends_on` → the governing Claim(s) — three already-existing,
structural lookups chained together, with exactly one new field added
to make the first link machine-checkable instead of informal prose.
This field is optional and additive to the Requirement schema
(`knowledge_intermediate.py`'s requirement field table, §5.1) — a
Requirement naming no `check_id` is unaffected, and `contract_id`'s own
existing one-contract-to-one-REQ mapping (`scripts/check_contracts.py::
check_contract_id_resolves`) is untouched, continuing to answer a
different question (which Requirement a contract as a whole is *for*)
from the one `check_id` now answers (which Requirement a specific check
*within* that contract is for).

### 4.3 Distinguishing genuine staleness from unrelated changes, missing
evidence, newly-closed coverage, and contradictions

**For detector (a)**, reusing `change_impact`'s existing tiers with no
new semantics:
- **Unrelated**: `no_recorded_relationship` — no citing Evidence found
  for the changed symbol. Not reported as a reconciliation candidate.
- **Missing evidence**: `relevant_no_coverage_link` — a Claim cites the
  changed symbol but no test-kind Evidence bridges to a real check.
  Reported via the existing `relevant_no_coverage_link` gap-adjacent
  classification (unchanged) — a coverage gap, not staleness; Phase 89
  never fabricates a check to close this. (This is also exactly
  `CL-BFS-004`'s own current tier, §0.1.A — which is precisely why
  detector (a) can never be the mechanism that closes it; only detector
  (b) can.)
- **Genuine contradiction (real staleness)**: a `behavioural_risk`
  finding whose fresh, re-executed outcome is `CONFIRMED_REGRESSION`,
  **and** a historical `PASS` for this exact `check_id` is present in
  `AssuranceFinding.observed_outcomes` (Phase 83's own existing return
  data, read, never recomputed) — i.e. the checked behaviour genuinely
  used to pass and a fresh run now fails. This is the only tier this
  plan's own manifest ever proposes writing back as a **contradiction**
  (§4.4).
- **Newly discovered failure, not a regression (§0.1's semantic
  correction)**: a `CONFIRMED_REGRESSION` finding (Phase 83's own
  classification, left completely unmodified) whose `observed_outcomes`
  contains **no** historical `PASS` for this `check_id` — i.e. this
  check has never yet been confirmed passing at all; a fresh `FAIL` is
  real and still proposed as contradicting Evidence (the Claim it
  bears on genuinely is unconfirmed-or-worse), but the manifest item
  and the new `find_gaps` kind (§5.4) label it `"newly_discovered_
  failure"` rather than `"regression"`, so a human reviewer is never
  told something broke that was never shown to have worked. `change_
  impact.py` itself is not touched — this label is computed once, in
  `source_reconciliation.py`, from data `assess()` already returns.
- A fresh `VERIFICATION_GAP` (no fresh result yet) or `INVALID_
  ASSESSMENT` (the check itself errored) is reported as a finding but
  never proposed as a reconciliation, since neither establishes a real
  contradiction or confirmation.
- **Re-confirmation, not staleness**: a fresh `VERIFIED_SCOPE` against a
  Claim whose `evidence_support_state` was already `supported` is a
  no-op for reconciliation purposes (nothing contradicted, nothing to
  write) — but a fresh `VERIFIED_SCOPE` against a Claim previously
  `partially_supported`/`unconfirmed` (i.e. closing a real, previously
  recorded gap) **is** proposed, since that is new, materially useful
  evidence a human should be able to accept into the record.

**For detector (b)**: a "newly coverable" check that, once actually
executed (§5.1), evaluates `PASS` is proposed as new **supporting**
Evidence for the check's own governing Claim (via §4.2's `check_id`
bridge) — this is Task A's own real scenario (§6.1), genuinely new
knowledge, not a contradiction of anything. A "newly coverable" check
that evaluates `FAIL` on its first-ever real execution is reported via
the same `"newly_discovered_failure"` label immediately above (there
being, by definition, no historical `PASS` for a check detector (b)
only ever fires on in the first place) — proposed as contradicting
Evidence against the Claim, never silently discarded just because the
check is new.

### 4.4 How canonical knowledge is reconciled without silently
overwriting previously accepted facts

Only through the existing, append-only `apply_manifest` flow (§3's
diagram), extended with one new item `kind`.

**Evidence identity (rewritten this round, §0.1.B)**: a new Evidence
record's own identity for idempotency purposes is the tuple
`(contract_id, check_id, run_id)` — the oracle run that produced it,
never a prose-text match. `_find_existing_promoted_record` is **not**
used here and cannot be: it is typed to match `kind="claim"` (or
`"requirement"`) records against their own `statement` field; Evidence
records have no `statement` field, and there is no existing Evidence-
creation call site anywhere in this codebase to mirror (§1.2) — this is
new, stated plainly, not characterised as reuse of an existing pattern.
A new, narrow helper, `_find_existing_evidence_for_run(records, slug,
contract_id, check_id, run_id)`, scans the slug's existing `evidence_
kind="test"` records, resolves each one's `test_ref` to its cited
`OracleResult` (`oracle.parse_oracle_result`, unmodified — the same
parse `classify_symbol` already performs) and compares `run_id`
directly — an exact-identity check, not a content/statement match,
because two separate real runs of the same check can legitimately
produce byte-identical raw output while still being two distinct,
independently-citable runs (`decisions/0082` §C's own immutable
per-run naming already establishes this is expected, not an edge case
to collapse away). This is checked **before every individual Evidence
write** inside a merged item's own multi-finding apply (§5.3) — not
once per item — because (§0.1.B, newly discovered this round)
`apply_manifest`'s own per-item `state: "applied"` flag is buffered for
the whole manifest and only written to disk once the entire batch's
loop completes (`knowledge_intermediate.py:2542-2543`); a crash midway
through one merged item's own multiple internal writes is not covered
by that flag at all, exactly the same way a crash between two *separate*
existing items is already only ever safe because of each item's own
record-level dedup, never the manifest's own bookkeeping. The Claim-
side append (below) gets its own, second, independent idempotency
check for the identical reason — a crash can land between the Evidence
write and the Claim update, or between the Claim update and the next
finding's Evidence write, and each must be independently safe to retry.

**A disclosed, narrowly-scoped deviation, not a mischaracterisation
(corrected after independent review found the original draft's "reuse"
claim false)**: every existing `apply_manifest` item kind today
(`"anchor_edit"`, `"candidate_addition"`, `"doc_region_edit"`) follows
this project's own explicit, established convention — "a semantic edit
never overwrites the original record directly... it always creates a
new, competing candidate [record] instead" (`_apply_anchor_edit`'s own
docstring, `knowledge_intermediate.py`). That convention exists to
protect against *semantic reinterpretation*: a human or tool proposing
different *wording* for what a Claim asserts (its `statement`/
`derivation` fields) must never silently overwrite the original — a
reviewer must see the new wording as a distinct, competing proposal.
**This is deliberately not what a `"source_reconciliation"` item
does.** It never touches `statement`/`derivation`/`timestamp`/any
authored prose field. It writes a **new** Evidence record per
contributing finding (next available `EV-<slug>-NNN` id, via the
existing `_next_id` helper, unmodified, guarded by the identity check
above — itself fully consistent with the existing append-only
convention, no deviation needed there) citing the fresh oracle
`run_id`/`raw_output_ref`, and then, for the *same* existing Claim,
appends each new Evidence id to exactly one of `contradicting_evidence`/
`supporting_evidence` (guarded by its own idempotency check: skip the
append if that exact Evidence id is already present in the target
field) and **recomputes** `evidence_support_state` **in place** — from
the Claim's own full, post-append `contradicting_evidence`/
`supporting_evidence` contents (mirroring exactly the existing CONTESTED
derivation already at `knowledge_intermediate.py:1211-1215`: non-empty
`contradicting_evidence` and non-empty `supporting_evidence` both ⇒
`"conflicting"`; non-empty `contradicting_evidence` alone ⇒
`"contradicted"`; non-empty `supporting_evidence` alone, with every
required contract scope now covered ⇒ `"supported"`, otherwise
`"partially_supported"`), **never from only this batch's own new
findings** — so a contradiction accepted in an earlier batch can never
be silently dropped just because the current batch's own findings
happen to all be supporting (dispatch's own explicit "historical
contradictions must not silently disappear" requirement). This is new,
previously-unmechanized behaviour for this codebase (no existing
apply-path function does this — confirmed directly, §1.2) and this
plan states that plainly rather than citing a non-existent precedent.
It is justified, not merely asserted, on a narrower ground than "reuse":
humans already make exactly this edit by hand today, routinely and
without controversy, whenever new evidence for an existing Claim
arrives (e.g. `CL-BFS-004.yaml`'s own `evidence_support_state:
partially_supported` field was itself set this way, by a human, outside
any tool) — a citation-list/derived-status update is bookkeeping this
project's own authors already treat as safe to make directly, never a
reinterpretation of what the Claim asserts. Phase 89 mechanizes an
already-accepted human editing pattern; it does not invent a new class
of record mutation this project has never tolerated. Every item starts
`decision: "undecided"`; only a human-set `"accept"` causes
`apply_manifest` to write anything, and `apply_manifest` re-validates
every cited fresh result against the live contract (re-running nothing,
just re-checking file state) before writing, exactly as it already does
for `"anchor_edit"` items — never trusting the manifest's own say-so.
The self-conflict risk this deviation would otherwise create (§4.8) is
closed at the source, by construction: §3's writer merges every finding
against the *same* Claim into that Claim's own single manifest item, so
`apply_manifest` never processes two pending items racing the same
Claim's own content hash within one run.

### 4.5 How generated documentation is invalidated and selectively
regenerated

Entirely by the existing, unmodified §1.1 cascade: once §4.4's apply
step changes a Claim's file content, `detect_grounded_region_changes`
reports `claims_changed` for every region citing it (and only those
regions — an unrelated region's own cited Claims are untouched, so its
case is `noop`); `docs maintain` writes the resulting `doc_region_edit`
manifest items; `docs compile`/`publish` regenerate only those specific
sections, through the existing citation-scope/review/publish gates
(semantic + editorial review, hash-bound publish, publication-lock),
all completely unchanged. Phase 89 contributes no code to this half at
all — it only ever gets a Claim's file to change, correctly and with
provenance, for a new kind of reason.

### 4.6 Preserving user-approved editorial changes, unrelated regions,
and manually maintained content

Guaranteed by §4.5's reuse: a `concurrent_conflict`/`doc_candidate`
region (a prior human edit) is still refused from automatic
regeneration by `docs maintain`'s own existing, unmodified refusal rule
— this plan introduces no new write path that could bypass it. A
manually maintained (non-schema-governed) document is never discovered
by `docs maintain` at all (unchanged discovery scope) and is therefore
categorically unreachable by this entire reconciliation chain.

### 4.7 Provenance, version identity, conflict states, reproducibility

Every new artefact (the source baseline file, the new manifest kind,
the new Evidence record(s), the one new `check_id` field on a
Requirement) carries the same provenance conventions already
established elsewhere in this project — a full `(contract_id, check_id,
run_id)` identity plus `raw_output_ref` for every triggering oracle
result (Phase 82's existing `OracleResult` schema, unmodified — §4.4's
own Evidence-identity mechanism reads exactly these fields, never a
narrower subset), the target repo's own git HEAD via the same
`_git_head_revision`-style helper `knowledge_api.py` already uses
(Phase 88's own pattern, reused independently of MCP), and the
manifest's own `manifest_id`/`created` fields (Phase 81's existing
convention, unmodified format). No new provenance scheme.

### 4.8 Behaviour after interrupted, repeated, ambiguous, or conflicting
reconciliation attempts

- **Interrupted**: the source baseline only advances
  (`advance_source_baseline_after_apply`, mirroring `advance_region_
  baseline_after_publish`'s own "only after the write itself actually
  succeeds" rule, `CLAUDE.md` §1's L-087) after `apply_manifest` reports
  a real, successful write for every accepted item in the batch — a
  crash or partial failure mid-apply leaves the baseline exactly where
  it was, so a re-run of detection reports the same findings again
  rather than silently treating an unfinished reconciliation as done.
  **Item-internal partial write — rewritten this round (§0.1.B): this is
  not a narrow edge case solved by reusing `_find_existing_promoted_
  record`, which cannot represent Evidence identity at all (no
  `statement` field), and relying on the manifest's own `state:
  "applied"` flag is not a safety net either — that flag is buffered
  for the *whole batch* and only ever written to disk once, after the
  entire item loop completes (`knowledge_intermediate.py:2542-2543`,
  §0.1.B) — so a crash can lose that flag's own update for an item that
  already fully, successfully applied earlier in the very same run, not
  only for a merged item's own internal multi-write.** The real
  guarantee (§4.4) is two independent, content-based re-checks against
  the canonical records on disk themselves, run on every attempt
  regardless of what the manifest's own bookkeeping claims: (1) before
  writing a new Evidence record for a contributing finding,
  `_find_existing_evidence_for_run` (§4.4, new) checks whether an
  Evidence record already exists citing this exact `(contract_id,
  check_id, run_id)`, skipping the write if found; (2) before appending
  an Evidence id to the target Claim's `contradicting_evidence`/
  `supporting_evidence` field, the apply step checks whether that exact
  id is already present, skipping the append if found. Together these
  make every one of a merged item's own internal writes independently
  safe to retry, in any order of partial completion, with or without
  the manifest's own `state` flag having been persisted at all.
- **Repeated**: re-running detection against an already-pending,
  unresolved manifest item reports the same findings again (by design —
  detection is read-only, §4.1) rather than silently suppressing them; a
  *second* `write_source_reconciliation_manifest` call for a check/run
  already named in an existing pending item does not create a duplicate
  manifest entry, mirroring `docs maintain`'s own existing idempotency
  guarantee for `doc_region_edit` items.
- **Ambiguous, across different Claims** (a changed symbol maps to more
  than one *distinct* Claim): every distinct Claim gets its own,
  independently-decided manifest item — this plan never collapses
  findings against different Claims into one silent resolution.
- **Ambiguous, against the SAME Claim** (a Claim maps to more than one
  behavioural_risk check, with agreeing or disagreeing fresh outcomes):
  deliberately **not** reported as separate items — §3/§4.4's writer
  merges every finding against one Claim into that Claim's own single
  manifest item (listing each contributing check/run_id), closing by
  construction the self-conflict risk an original draft of this plan
  left open (independent review, Blocking Finding 1's second part):
  two items racing the same Claim's own content hash within one
  `apply_manifest` batch could otherwise spuriously trip the reused
  whole-file-hash conflict check against each other, not only against a
  genuine human edit. One Claim, one item, one hash check, by
  construction — no race is possible. **Disagreeing-outcomes case,
  found by independent re-review (non-blocking, resolved here rather
  than left open)**: when a merged item's own contributing findings
  disagree (one `CONFIRMED_REGRESSION`, one qualifying `VERIFIED_SCOPE`,
  against the same Claim in the same batch), the apply step (§5.3)
  writes to **both** `contradicting_evidence` and `supporting_evidence`
  and sets `evidence_support_state` to the existing, already-used
  `"conflicting"` value (`knowledge_intermediate.py:1211-1214`, the same
  value that already feeds the existing CONTESTED classification
  elsewhere in this codebase) — reused, not invented, for exactly the
  case it already exists to name. A merged item is never silently
  resolved toward whichever outcome happens to be listed first.
- **Conflicting** (a human has directly hand-edited the same Claim's
  file between detection and apply): `apply_manifest`'s existing
  re-validation (unchanged) already detects this the same way it
  already detects a concurrent `"anchor_edit"` conflict — reported, not
  silently overwritten. This is now the *only* way a `"source_
  reconciliation"` item's conflict check can genuinely fire, since the
  bullet above already closes the self-inflicted version of the same
  symptom.

### 4.9 Deterministic vs. judgement vs. human-approval operations

- **Deterministic**: content-hash comparison (§4.1), graph-freshness
  cross-check (§4.1/§5.1), the `pytest --collect-only` coverability
  probe (§5.1 — collects or does not, no judgement involved), symbol/
  Claim mapping (§4.2), tier classification (§4.3), fresh check
  execution and its own outcome (reused, unmodified Phase 82/83 code),
  the `evidence_support_state` recomputation (§4.4 — a pure function of
  the Claim's own accumulated citation fields, never a choice).
- **Requires human judgement, surfaced not resolved**: whether an
  ambiguous multi-Claim/multi-check finding should be split, merged, or
  deferred — this plan reports every such case explicitly rather than
  guessing; which second Ledgerkit task genuinely exercises Task A's
  reconciled knowledge (§6.3, pre-registered by a human before Task A
  runs).
- **Requires explicit human approval before any write**: every single
  `"source_reconciliation"` manifest item's `decision` field (§4.4) —
  there is no `--yes`/auto-accept mode in this plan's own MVP scope
  (named explicitly as a non-goal, §10); the one-time `check_id`
  backfill onto a Requirement record (§4.2/§5.1) is itself always a
  human edit, never written by any tool this plan introduces.

### 4.10 Modularity and CLI/API callability, independent of MCP

One new, thin CLI subcommand under the existing `codecompass knowledge`
sub-app, plus reuse of one already-existing one (not a new top-level
command, not an MCP tool — `decisions/0085` §3's own exclusion,
re-confirmed; wording corrected per independent review — only
`detect-changes` below is actually new):

- `codecompass knowledge detect-changes SLUG --repo-root PATH [--json]`
  — read-only; runs **both** detectors (a) and (b) (§4.1/§5.1) and, for
  (a), `change_impact.assess(run_checks=True)`; writes the `"source_
  reconciliation"`-kind manifest (§3) if anything is genuinely
  proposable from either, exactly as `knowledge select-candidates`
  already does for its own anchor/candidate findings today (a sibling
  command, not a replacement).
- `codecompass knowledge apply MANIFEST_PATH` — **already exists**
  (Phase 81/84); recognises the new `kind` automatically once §5.3 adds
  it to `apply_manifest`'s own dispatch, no new CLI surface needed here
  at all.

Every one of these is a plain, synchronous library call
(`src/codecompass/source_reconciliation.py` + `knowledge_intermediate.
apply_manifest`) — callable from a script, a test, or a future MCP tool
exactly the same way `knowledge_api`'s existing functions already are,
with no MCP dependency anywhere in the import graph.

## 5. New primitives (genuinely missing, narrowly scoped)

### 5.1 `src/codecompass/source_reconciliation.py` (new module)

**Two sibling detectors (§0.1.A, §4.1) — never one trying to cover
both:**

- `detect_source_changes(project_root, slug, *, repo_root) ->
  list[SourceChangeFinding]` — §4.1(a)'s baseline-diff detector, for
  an **already** test-Evidence-bridged scope. For each tracked source/
  test file: **first**, `_check_graph_index_fresh(repo_root, path)`
  (new, narrow — recomputes `oracle.sha256_file(repo_root / path)` and
  compares it against the graph's own recorded `source_files.
  content_hash`, exactly the comparison `change_impact.resolve_
  changed_range` already performs for the identical purpose) — a
  disagreement is reported as `"stale_graph_index"` and that file is
  excluded from this run, never silently compared against the baseline
  using a value already known to be stale (§0.1.D). Only once confirmed
  fresh does it read `source-baseline.toml` via the existing `_read_
  simple_toml_tables` (imported from `knowledge_intermediate`, not
  duplicated) and compare the graph's own `content_hash` against the
  persisted baseline; for each drifted file, resolves a `changed[path:
  start-end]` range (the file's own full line range if no finer-grained
  range is recorded — Phase 83's own existing line-range convention)
  and returns it, annotated with the record(s) that cite it.
- `detect_newly_coverable_checks(project_root, slug, *, repo_root) ->
  list[NewlyCoverableCheck]` — §4.1(b)'s new detector, for a **never
  yet covered** required check (Task A's own real scenario, §0.1.A). For
  every `required: true` check in the slug's `oracle-contract.yaml`
  with no currently-valid historical `OracleResult` (reusing `scripts/
  check_contracts.py`'s own existing `current_pass_check_ids`-style
  computation against `oracle.evaluate_result_precedence`, not
  reinvented — §1.2): probes `pytest --collect-only -q <check.
  check_reference>` against `repo_root` (new, narrow, read-only use of
  the subprocess pattern `oracle.run_pytest_check` already establishes
  — a collection probe, zero test execution, so an exit code of `0`
  means only "this node id now resolves to a real test," never
  anything about its outcome). A check that now collects is returned,
  resolved to its governing Claim(s) via the new `check_id` → `REQ.
  check_id` → `REQ.depends_on` chain (§4.2/below).
- `propose_reconciliation(project_root, slug, findings, *, repo_root,
  knowledge_root) -> Path | None` — for detector (a)'s findings: calls
  `change_impact.assess(changed=[f.range for f in findings], run_checks=
  True, ...)` (Phase 83, verbatim signature reuse), re-walks `assess()`'s
  own returned `range_reports[].symbol_classifications[].claims[]`
  (each `ClaimFinding` already carries `check_id`) to recover the
  claim↔check link, and for each `CONFIRMED_REGRESSION`/qualifying
  `VERIFIED_SCOPE` finding annotates it with whether a historical `PASS`
  for that `check_id` already existed before this fresh result
  (`AssuranceFinding.observed_outcomes`, read not recomputed — §4.3's
  "newly discovered failure" distinction). For detector (b)'s findings:
  calls `oracle.evaluate_check` directly (Phase 82, unmodified) against
  each newly-coverable check — this is the one point in this whole
  module where a check is executed for a reason *other than* re-walking
  an existing `assess()` call, because detector (b)'s own findings, by
  definition, have no existing `assess()`-reachable bridge to re-walk
  (§0.1.A). Both detectors' own findings are then grouped by `claim_id`
  (§4.8's "ambiguous, same Claim" rule — never one item per finding,
  always one item per distinct Claim) and passed, uniformly, to
  `write_source_reconciliation_manifest` (§5.3, a new **sibling writer
  function**, mirroring the real, already-production `write_doc_
  candidates_to_manifests` exactly, §1.1's corrected inventory;
  `write_manifest` itself is left untouched).
- `establish_source_baseline(...)` /
  `advance_source_baseline_after_apply(...)` — mirror
  `establish_new_region_baselines`/`advance_region_baseline_after_publish`
  exactly (§4.8). A file reported `new` (no baseline entry, detector
  (a)) and a check reported newly-coverable (detector (b)) are both
  read-only findings on their own — neither establishes or advances any
  baseline as a side effect of being observed (`CLAUDE.md` §1 L-087).
- **One small, additive, optional field on the Requirement record
  schema**: `check_id` (§4.2) — added to `knowledge_intermediate.py`'s
  existing requirement field table alongside `decision`/`depends_on`,
  optional, defaulting to absent for every existing Requirement that
  does not name one. `REQ-BFS-002.yaml` is backfilled with `check_id:
  overlapping-account-patterns-no-double-count` as part of this stage's
  own deliverables — a narrow, editorial, non-semantic addition to an
  already-existing record (the statement/derivation/every other field
  is untouched), the same class of safe bookkeeping change §4.4 already
  justifies for Evidence citations.

### 5.2 `source-baseline.toml` (new, per-slug persisted file)

`planning/knowledge/<slug>/reconciliation/source-baseline.toml` — same
directory Phase 81's manifests already live in, same TOML read/write
helpers, a sibling format to `.grounding-state.toml`
(`{path: {content_hash: str, last_reconciled: iso8601}}`). Not a
canonical record; not committed-knowledge content — exactly the same
classification `.grounding-state.toml` already has. A file present in
the baseline but now absent on disk (deleted/renamed) is reported as
its own distinct finding, `"deleted"` — never silently dropped from the
baseline and never conflated with `"new"` (the opposite condition). A
file outside `oracle-contract.yaml`'s own `tested_paths`/
`test_input_paths`/Evidence `source_ref`/`test_ref` set is never
tracked at all (no baseline entry is ever created for it) — this
detector's own scope is exactly the files this slug's existing records
already name, never a repository-wide scan. The graph-freshness check
(§5.1) is always evaluated before baseline comparison, per file, never
once for the whole repository — a graph that is fresh for one tracked
file and stale for another (a partial `sync`) must not let the stale
one's comparison borrow the fresh one's result.

### 5.3 `write_source_reconciliation_manifest` (new sibling writer),
`_find_existing_evidence_for_run` (new Evidence-identity helper), and
one new `apply_manifest` item kind: `"source_reconciliation"`

`write_source_reconciliation_manifest(project_root, slug, findings_by_
claim)` — a new function in `source_reconciliation.py`, structurally
mirroring the real, already-production `write_doc_candidates_to_
manifests` (called from `docs maintain`, §1.1's corrected inventory),
not an addition to `write_manifest` itself. One item per **Claim**
(§4.8), each listing every contributing finding's own full `(contract_
id, check_id, run_id, raw_output_ref)` identity, its `"newly_discovered_
failure"`/`"regression"`/`"newly_covered"` label (§4.3), and target
`contradicting_evidence` vs. `supporting_evidence` field,
`state="pending"`, `decision="undecided"`.

`_find_existing_evidence_for_run(records, contract_id, check_id, run_id)
-> str | None` (§4.4, new, in `knowledge_intermediate.py` alongside
`_find_existing_promoted_record` as a sibling, not a replacement) —
scans existing `evidence_kind="test"` records, resolves each one's
`test_ref` to its cited `OracleResult` (`oracle.parse_oracle_result`,
unmodified) and returns the first whose `(contract_id, check_id,
run_id)` matches exactly, or `None`. This is the genuinely new
Evidence-identity mechanism §0.1.B's finding requires — stated plainly
as new, not a parameterisation of the existing, differently-typed
helper.

A small, additive change to `knowledge_intermediate.apply_manifest`'s
existing dispatch (currently `"anchor_edit"` / `"candidate_addition"` /
`"doc_region_edit"`, §1.1's corrected inventory) — a new `elif
item["kind"] == "source_reconciliation":` branch that, on `decision ==
"accept"`: (a) re-validates every cited fresh oracle result still
parses and still belongs to the named contract/check (reusing `oracle.
parse_oracle_result` + the same contract-identity checks `classify_
symbol` already applies — never trusting the manifest's own cached
fields); (b) for each contributing finding, in order, **first** calls
`_find_existing_evidence_for_run` — if it already returns an id, this
finding's own Evidence write is skipped (already applied, safe retry);
otherwise writes one new Evidence record via the existing `_write_
record`/`_next_id` helpers, unmodified (fully consistent with this
project's own append-only convention); (c) for each newly-written **or**
already-existing Evidence id from (b), checks whether it is already
present in the target Claim's `contradicting_evidence`/`supporting_
evidence` field before appending — a second, independent idempotency
check, since (b) and (c) can each independently have already completed
or not on a prior crashed attempt (§0.1.B/§4.4/§4.8); (d) **the one
disclosed, narrowly-scoped deviation named in §4.4**: after every
contributing finding's own append (if any) is applied, **recomputes**
`evidence_support_state` from the Claim's own full, post-append
`contradicting_evidence`/`supporting_evidence` contents (§4.4's exact
rule — never from this batch's findings alone). The Claim's own
`statement`/`derivation`/every other field is never touched, and (per
§4.8) this is always the *only* pending item for this Claim in this
batch, so the existing whole-file-hash conflict check, re-run once
immediately before this write, can only ever genuinely fire against a
real, independent human edit — never against this item's own sibling.
On `decision == "reject"`: no write, item state becomes `"rejected"`,
mirroring the existing `"anchor_edit"` reject path exactly.

### 5.4 One new `find_gaps` gap kind: `"claim_contradicted_by_fresh_check"`

A Claim with a *pending, unapplied* `"source_reconciliation"` manifest
item proposing contradicting Evidence against it (labelled, per §4.3,
either `"regression"` — a historical `PASS` for that check existed
before the fresh `FAIL` — or `"newly_discovered_failure"` — it did not)
is reported by `find_gaps` as this new gap kind, carrying that label —
surfacing "this canonical fact is believed true but a fresh check
already disagrees and nobody has reviewed it yet," and *which* of the
two it is, without requiring a caller to separately know to go look in
`reconciliation/*.toml`. Reuses the existing `Gap` dataclass and `find_
gaps`'s existing scan loop/response shape verbatim; the label is a new
field on the `Gap` payload, additive, never a change to an existing
`Gap` kind's own shape.

## 6. Two-task Ledgerkit evaluation (the real-world exit gate)

Runs against **disposable scratch copies** by default (§6.4) — matching
Phase 88's own already-established, pre-authorised convention and this
dispatch's own instruction to distinguish evidentiary strength by
authorisation level, never assuming it.

### 6.1 Task A — a genuine development change produces new/changed
knowledge (source-verified walkthrough, rewritten this round — §0.1.A)

Reuse the exact, real, already-identified Ledgerkit gap this project's
own knowledge already names: `ledgerkit/reports.py::balance_from_spec`'s
`overlapping-account-patterns-no-double-count` scope (`REQ-BFS-002`/
`DEC-BFS-002`/`CL-BFS-004`/`EV-BFS-001`). This is **detector (b)'s own
scenario** (§4.1/§5.1), traced here concretely, input by input:

1. **Starting state (real, re-read this round)**: `CL-BFS-004.yaml`:
   `supporting_evidence: [EV-BFS-001]`, `contradicting_evidence: []`,
   `evidence_support_state: partially_supported`. `REQ-BFS-002.yaml`:
   no `check_id` field yet. `oracle-contract.yaml`'s third check,
   `overlapping-account-patterns-no-double-count`, `required: true`,
   `check_reference: tests/test_reports.py::TestBalanceFromSpec::
   test_section_accounts_overlapping_patterns_no_double_count` — no
   result file for this `check_id` exists anywhere under `planning/
   contracts/balance-from-spec/results/`.
2. **Backfill (Stage 89A's own deliverable, §4.2/§5.1)**: add
   `check_id: overlapping-account-patterns-no-double-count` to
   `REQ-BFS-002.yaml`.
3. **Set-up**: a fresh, disposable Ledgerkit scratch copy pinned at the
   real checkout's current HEAD; `codecompass sync` run against it
   (populating `source_files.content_hash` in its own `context-graph.
   db`); the new test function added to `tests/test_reports.py` in
   *this scratch copy only* (never the real `~/projects/ledgerkit`,
   §6.4), reusing Phase 88's own already-documented procedure for
   writing exactly this test.
4. **`detect_newly_coverable_checks(project_root, "balance-from-spec",
   repo_root=<scratch copy>)`**: iterates `oracle-contract.yaml`'s
   checks; for `overlapping-account-patterns-no-double-count`, confirms
   zero valid historical results (true); probes `pytest --collect-only
   -q tests/test_reports.py::TestBalanceFromSpec::
   test_section_accounts_overlapping_patterns_no_double_count` against
   the scratch copy — now collects (exit `0`), where it would have
   failed to collect before step 3. Resolves `check_id` →
   `REQ-BFS-002` (via step 2's new field) → `depends_on: [CL-BFS-004]`.
   Returns one `NewlyCoverableCheck(check_id=..., claim_id=CL-BFS-004)`.
5. **`propose_reconciliation`**: calls `oracle.evaluate_check` directly
   against the scratch copy for this check — a real pytest run,
   producing a fresh `OracleResult` with a real `run_id` and
   `outcome: PASS` (the test genuinely passes against the unmodified,
   correct `reports.py`). Labels this finding `"newly_covered"` (§4.3 —
   a `PASS` is never a "regression" or a "newly discovered failure").
6. **`write_source_reconciliation_manifest`**: one new manifest item,
   `kind="source_reconciliation"`, `record_id=CL-BFS-004`, one
   contributing finding (`contract_id=REQ-BFS-001`, `check_id=
   overlapping-account-patterns-no-double-count`, this run's `run_id`,
   label `"newly_covered"`, target field `supporting_evidence`),
   `state="pending"`, `decision="undecided"`.
7. **Human review**: `decision` set to `"accept"`.
8. **`apply_manifest`**: `_find_existing_evidence_for_run` finds
   nothing (first time) → writes a new Evidence record, `EV-BFS-004`
   (`evidence_kind: test`, `test_ref` naming this run's own result
   file, `repository_revision` the scratch copy's pinned HEAD) → checks
   `CL-BFS-004`'s own `supporting_evidence` for `EV-BFS-004` (absent) →
   appends it, giving `supporting_evidence: [EV-BFS-001, EV-BFS-004]`
   → recomputes `evidence_support_state` from the full, now-updated
   field contents (§4.4's rule): `contradicting_evidence` is empty,
   `supporting_evidence` is non-empty, every one of the contract's
   `required` checks now has a qualifying result cited somewhere in
   `CL-BFS-004`/sibling Claims under the same Requirement family → sets
   `"supported"` (a real change from `"partially_supported"`).
9. **Result**: `CL-BFS-004.yaml` has genuinely new, changed knowledge —
   a new Evidence record exists on disk, a Claim's own
   `evidence_support_state` field changed, and (§4.5) `CL-BFS-004`'s own
   content hash has changed, ready for `detect_grounded_region_changes`
   to react to, unchanged, on whatever documentation cites it.

### 6.2 Reconciliation — precision checks (the true-positive and
false-positive controls)

- **True-positive control, detector (b) (Task A itself, §6.1)**: steps
  1-9 above, confirmed end to end against a real scratch copy.
- **True-positive control, detector (a) (the already-working
  re-verification path, §0.1.A/§4.1)**: separately, confirm the
  *other*, already-functional pathway: mutate `ledgerkit/reports.py`'s
  `balance_from_spec` in a second scratch copy (reproducing Phase 83's
  own already-documented OR-union double-counting mutation, the exact
  change `DEC-BFS-002` already describes), run `codecompass sync`,
  confirm `detect_source_changes` reports the changed range, confirm
  `change_impact.assess(run_checks=True)` reaches `behavioural_risk`
  for `CL-BFS-001`/`CL-BFS-002` (already bridged via `EV-BFS-002`/
  `EV-BFS-003`) and produces a fresh `CONFIRMED_REGRESSION` — labelled
  `"regression"`, not `"newly_discovered_failure"` (§4.3), since a
  historical `PASS` for these checks already exists. This is the
  scenario the prior draft's walkthrough conflated with Task A's own —
  kept here, explicitly, as its own separate control, since it
  genuinely does exercise detector (a) end to end.
- **Documentation-invalidation control**: confirm `docs maintain`
  subsequently reports `claims_changed` for any doc region citing
  `CL-BFS-004` (none exist today per the Phase 88 plan's own §18.2
  finding — if still none at demonstration time, this control runs
  against a temporary, disposable schema-governed document created for
  this demonstration alone, citing `CL-BFS-004`, so the invalidation
  pathway is genuinely exercised end to end, not merely asserted to
  exist in principle). This proves the *mechanism* fires — §6.3 below
  separately requires evidence the resulting documentation content is
  actually better for a real task, per §0.1's second semantic
  correction.
- **False-positive control**: make a second, genuinely unrelated,
  disposable-scratch-copy-only change to Ledgerkit (e.g. a comment-only
  edit or a change to an unrelated report function with no citing
  Evidence) and confirm both detectors report nothing proposable
  (`no_recorded_relationship`/no newly-coverable check found), and that
  every unrelated Claim and doc region's own case remains `noop` — the
  false-positive control is exactly as load-bearing as the
  true-positive ones, per `planning/v2-roadmap.md`'s own Phase 89 §7.

### 6.3 Task B — three separate questions, pre-registered before Task A
even runs (§0.1.C — rewritten this round)

**Three genuinely separate gates, never conflated into one (dispatch
§2.C)**:

1. **Technical completion**: the mechanism (detectors, manifest,
   apply branch, doc cascade) runs end to end without error on Task A
   and Task B. This alone is a Stage 89A/89B deliverable, not the
   phase's own exit gate.
2. **A valid, completed evaluation**: Task B's own controlled
   comparison (below) actually ran, both arms were genuinely assessed,
   and no contamination occurred (below). This can be true even if (3)
   is not — a well-run experiment that finds no effect is still a valid
   evaluation, honestly reported.
3. **The roadmap's own positive exit gate** (`planning/v2-roadmap.md`
   §9, quoted exactly, re-read directly this round): "The second task
   measurably benefits from the first, evidenced... not asserted." This
   gate is satisfied **only** when the treatment arm beats the control
   arm by at least the pre-registered minimum improvement below — **a
   negative or inconclusive result, however honestly reported, does
   not satisfy it.** §8 below states plainly what happens if (3) is
   not met.

**Pre-registered now, before Task A's own outcome is examined (dispatch
§2.C)**:
- **The genuine second Ledgerkit task**: the next real, already-named
  gap in `balance-from-spec`'s own knowledge at Stage 89C's
  implementation time (named and committed to this file *before* Task A
  runs, not selected retroactively to fit a result — if no such gap
  exists at that time, a comparably-scoped real task is named and
  committed here first, still before Task A runs).
- **The reconciled knowledge expected to matter**: `CL-BFS-004`'s own
  upgraded `evidence_support_state`/new `EV-BFS-004` citation (§6.1) —
  stated explicitly so contamination (below) can be checked against a
  named fact, not a vague "the reconciled state."
- **Treatment/control**: (treatment) a context packet for Task B drawn
  from the post-reconciliation knowledge state; (control) an otherwise
  byte-identical packet drawn from the pre-reconciliation snapshot,
  withholding exactly `EV-BFS-004`/`CL-BFS-004`'s updated field — never
  withholding anything else, so the comparison isolates Task A's own
  effect.
- **Measurable, independently assessable success criterion and minimum
  improvement**: Task B's own verification outcome (does Task B's
  check pass/fail correctly) **and** a `context-evaluator`-style
  correctness/completeness score against the reconciled fact, reusing
  `planning/v2-evaluation-methodology.md`'s existing method (Phase 90's
  own document, consulted, not reimplemented). Minimum improvement:
  the treatment arm's own verification outcome must be correct where
  the control arm's is not, **or** the treatment arm's correctness/
  completeness score must exceed the control arm's by the methodology
  document's own existing minimum-meaningful-difference threshold —
  whichever applies to the specific task named above; recorded here, in
  this exact form, before Task A runs.
- **Evaluation procedure and contamination controls**: a fresh,
  independent `context-evaluator` dispatch (never the implementing
  session) assembles and scores both arms without being told which is
  treatment/control (blinded ordering); the control arm's own packet is
  mechanically generated by re-running the same packet-assembly code
  against a checked-out pre-reconciliation commit/snapshot, never
  hand-edited to remove the fact (removing hand-editing risk of
  accidentally also removing something else); zero unrelated content
  may differ between arms (checked mechanically, a diff of the two
  packets outside the one named field is a contamination finding, not
  a pass).
- **No productivity/time claim** is made from this comparison alone —
  matching this dispatch's own instruction and this project's own
  established precedent (Phase 87C's comparator found scope
  completeness without claiming a net time/cost advantage; Phase 90 is
  the only phase authorised to attempt that broader claim).

### 6.4 Authorisation and evidentiary strength

Entirely feasible, and run by default, on **disposable scratch copies**
only — no real Ledgerkit commit is required for Task A, the
reconciliation, or Task B's controlled comparison; every control named
above is independently reproducible from a fresh scratch copy pinned at
a stated revision, exactly as Phase 88's own demonstration was. If, at
implementation time, landing Task A's own new Evidence/oracle-result
pair in the **real** `~/projects/ledgerkit` checkout is desired for
stronger evidentiary weight, that is a **separate, explicit,
cross-repository authorisation** this plan does not request and must
not assume — named here as a possible future strengthening, not a
precondition of this phase's own exit gate, which the scratch-copy
version alone already satisfies per `planning/v2-roadmap.md`'s own
Phase 89 §9 ("achieved without any dependency on an MCP server" — and,
by the same reasoning, without any dependency on a real cross-repository
write either).

## 7. Staged implementation plan

**Stage 89A — Detection and the manifest extension** (§5.1-§5.3, §4.1-
§4.4, §4.7-§4.9). Deliverables: `source_reconciliation.py`
(`detect_source_changes`/`detect_newly_coverable_checks`/
`propose_reconciliation`/`write_source_reconciliation_manifest`/
baseline helpers); `source-baseline.toml` format; the new, optional,
additive `check_id` field on the Requirement schema (plus the
`REQ-BFS-002.yaml` backfill, §5.1); `_find_existing_evidence_for_run`
(new Evidence-identity helper, §5.3); the new `"source_reconciliation"`
`apply_manifest` branch; `codecompass knowledge detect-changes` CLI
command; the Stage 89A ADR (§9) covering all three genuinely new
tradeoffs (the in-place-mutation deviation, the first-ever Evidence-
creation path, and the new Requirement field). Tests: the true-positive
(both detector (a) and detector (b), §6.2) and false-positive controls
run against disposable Ledgerkit scratch copies, standalone (not yet
wired to documentation); a stale-graph-index test (a file edited
without an intervening `codecompass sync`, confirmed `detect_source_
changes` reports `"stale_graph_index"` and excludes that file, never
silently comparing a stale hash — the direct regression test for
§0.1.D); a newly-coverable-check test (a required check with zero
historical results whose test now collects, confirmed `detect_newly_
coverable_checks` finds it and resolves it to the correct Claim via the
new `check_id` field — the direct regression test for §0.1.A); an
interrupted-apply test (§4.8, crash mid-batch leaves the baseline
unchanged, confirmed by re-running detection and seeing the same
findings again); a multi-Claim-mapping test (one changed symbol → two
distinct Claims, each its own independently-decided item); a
same-Claim-merge test (two findings against one Claim, confirmed merged
into that Claim's own single item, never two racing items); a
disagreeing-outcomes test (a merged item whose contributing findings
include both a `CONFIRMED_REGRESSION` and a qualifying `VERIFIED_
SCOPE`, confirmed written to both `contradicting_evidence` and
`supporting_evidence` with `evidence_support_state` recomputed to
`"conflicting"`); a cumulative-state test (a Claim with an *existing*
`contradicting_evidence` entry from an earlier batch; a *new* batch
adds only supporting Evidence; confirmed `evidence_support_state` is
recomputed to `"conflicting"`, never silently reset to `"supported"` —
the direct regression test for §0.1's "historical contradictions must
not silently disappear" requirement); an Evidence-identity-retry test
(`_find_existing_evidence_for_run` confirmed to find an already-written
Evidence record by `(contract_id, check_id, run_id)` and skip
re-creating it on a simulated retry — the direct regression test for
§0.1.B, replacing the prior, unsound reliance on `_find_existing_
promoted_record`); a Claim-append-retry test (the same Evidence id
already present in `contradicting_evidence`/`supporting_evidence`,
confirmed the append is skipped rather than duplicated, independently
of whether the Evidence record itself was newly written or already
existed); a conflicting-edit test (a Claim hand-edited between
detection and apply, confirmed refused, mirroring the existing
`"anchor_edit"` conflict test). **`CLAUDE.md` §1's L-021, explicitly
satisfied**: `apply_manifest` has exactly one real production call
site, `cli.py::knowledge_apply_manifest` (`codecompass knowledge apply
MANIFEST_PATH`) — at least one Stage 89A test invokes that real CLI
command directly against a manifest containing a `"source_
reconciliation"` item (via this project's own existing `typer`
CLI-testing convention), not only `apply_manifest()` called in
isolation as a library function. Independent audit checkpoint:
`release-phase-auditor` (stage-level — persisted report at `planning/
retros/_audit-phase-89-stage-89a.md` before this stage is treated as
closed).

**Stage 89B — The new gap kind and the documentation-cascade
demonstration** (§5.4, §6.1-§6.2's doc-invalidation leg, §4.5-§4.6).
Deliverables: `find_gaps`'s new `claim_contradicted_by_fresh_check`
gap kind (carrying the `"regression"`/`"newly_discovered_failure"`
label, §4.3); the end-to-end Task-A demonstration including the
documentation-invalidation control (§6.2, including its own
disposable-schema-governed-document fallback if no real grounded
region exists yet). Tests: the new gap kind's own unit tests,
including one asserting the `"regression"` vs `"newly_discovered_
failure"` label is correct in each of the two cases (a historical
`PASS` present vs absent for the check); an end-to-end scratch-copy run
of the full §3 diagram, start to finish, for both detectors. Independent
audit checkpoint: stage-level `release-phase-auditor` pass, persisted
per the same convention.

**Stage 89C — Task B and the pre-registered controlled comparison**
(§6.3). Deliverables: the pre-registered Task B success criteria
(written and committed *before* Task B runs, not after); the controlled
comparison itself; `planning/retros/phase-89-ledgerkit-two-task-
demonstration.md`. Independent verification: a fresh `context-evaluator`
dispatch reproducing the comparison's own control/treatment packets
directly (never trusting the implementing session's own report),
exactly as Phase 88's own Ledgerkit demonstration was independently
re-verified.

**Terminal closeout**: learnings triage, phase retro (full
`TEMPLATE.md` structure, per the `L-134`/Phase-88-retro precedent of
what "complete" actually means here), whole-phase `release-phase-auditor`
pass against the exact commit to be marked done, then — and only then —
`planning/ROADMAP.md`'s Phase 89 row flips to `done` (`CLAUDE.md` §5,
unchanged).

## 8. Definition of Done (mapped to the governing exit gate — three
gates, never conflated, §0.1.C/§6.3)

Matches `CLAUDE.md` §5, plus `planning/v2-roadmap.md`'s own Phase 89 §9
exit gate specifically, with the three questions kept explicitly
separate throughout:

1. **Technical completion** (a Stage 89A/89B gate, not the phase's own
   exit gate): every stage's own tests pass (including the detector
   (a)/detector (b) true-positive controls and the false-positive
   control, §6.2); the Task-A walkthrough (§6.1) runs end to end
   against a disposable scratch copy with no error; no new doc-
   compilation/scheduler/knowledge-store code exists anywhere in the
   diff (an independent auditor confirms this directly against the
   real diff); `docs/`, `architecture/`, `decisions/*` updated for the
   Stage 89A ADR (§9); phase retro filed; learnings triaged.
2. **A valid, completed Task B evaluation** (§6.3): the pre-registered
   criteria (named *before* Task A ran) were followed exactly, both
   arms were genuinely assessed by an independent `context-evaluator`
   dispatch, and the contamination controls (§6.3) held — a fresh,
   independent `release-phase-auditor`/`context-evaluator` pass
   confirms this directly, never trusting the implementing session's
   own account.
3. **The roadmap's own positive exit gate**: the pre-registered minimum
   improvement (§6.3) was actually met. **If it was not**: this plan's
   own closeout states that plainly (no overclaim, matching this
   project's own Phase 87C precedent) and `planning/ROADMAP.md`'s Phase
   89 row does **not** flip to `done` on that basis alone — gates 1 and
   2 being satisfied closes the *implementation* work (and may be
   recorded as such, e.g. "implemented, exit gate not yet met"), but
   `CLAUDE.md` §5's "only once every one of the above genuinely holds"
   rule means a roadmap exit gate stated in `planning/v2-roadmap.md`
   itself is one of "the above" for *this* phase specifically, and a
   negative result on it is a new, separate, explicit decision point
   (redesign Task B, pick a different reconciled fact, or defer/amend
   the exit gate itself via a new ADR) — never silently absorbed into
   "done" by the mere fact that the mechanism itself worked.

A fresh, independent `release-phase-auditor` pass against the exact
commit about to be marked done is required regardless of which of the
three gates above the phase actually reaches.

## 9. Risks and unresolved decisions

- **§6.3's Task B selection** is pre-registered at Stage 89C's own
  start, *before Task A itself runs* (sharpened this round, §0.1.C) —
  fixing it any later would be a form of picking the result before the
  experiment, the opposite of what pre-registration is for.
- **A negative Task B result is a real, open risk, not hand-waved
  away** (§0.1.C/§8): this plan does not know, and cannot know in
  advance, whether the pre-registered minimum improvement will actually
  be met. §8 states explicitly what happens if it is not — a new
  decision point, never a silent downgrade of the exit gate's own
  wording.
- **Resolved by independent review** (no longer open): `write_manifest`
  itself is left untouched; a new sibling writer, `write_source_
  reconciliation_manifest`, is introduced instead, mirroring the real,
  already-production `write_doc_candidates_to_manifests` precedent
  rather than a hypothetical either/or.
- **Resolved by a second independent review round** (no longer open):
  a merged item's own disagreeing-outcome write uses the existing
  `evidence_support_state: "conflicting"` value, never an invented one.
- **Superseded this round (§0.1.B)**: the second amendment's own fix for
  merged-item retry safety (reusing `_find_existing_promoted_record`)
  is replaced — that helper cannot represent Evidence identity at all
  (no `statement` field). The real mechanism is now `_find_existing_
  evidence_for_run`, a new, narrow, Evidence-specific identity helper
  (§4.4/§5.3), plus a second, independent idempotency check on the
  Claim-side append — not because the second amendment's instinct
  (idempotent retry) was wrong, but because the specific helper it
  named was never capable of doing this.
- **Superseded this round (§0.1.A)**: the original/second amendment's
  own Task A walkthrough, relying solely on `change_impact.assess
  (run_checks=True)`, is replaced by a second, genuinely new detector,
  `detect_newly_coverable_checks` (§4.1/§5.1), for exactly the class of
  scenario (a required check with zero prior citing Evidence) that
  pathway structurally cannot reach. `detect_source_changes`/`assess()`
  remain valid, unchanged, for the re-verification scenario they were
  always actually capable of (§6.2's second true-positive control).
- **Whether an ADR is required**: **yes**, one Stage 89A ADR covering
  **three** genuinely new tradeoffs together (widened this round, was
  previously framed as covering one): (a) the disclosed, narrowly-
  scoped in-place-mutation deviation (§4.4) from this project's
  otherwise-universal "never mutate, always create a competing record"
  convention; (b) this codebase's first-ever mechanized Evidence-
  creation path, with its own new, narrow identity convention (§4.4/
  §5.3) rather than reuse of an existing one (§0.1.B); (c) the new,
  optional, additive `check_id` field on the Requirement schema and the
  informal-prose-matching gap it closes (§4.2/§5.1). All three are
  genuinely new, previously-untaken decisions in this codebase, not
  routine extensions of an existing mechanism — `CLAUDE.md` §2's
  "non-obvious tradeoff" trigger applies to each. Drafting it is Stage
  89A's own first task, not assumed or pre-written here.
- **The `pytest --collect-only` probe's own failure modes** (new risk,
  this round, §5.1) are not yet exhaustively enumerated here (a
  genuinely malformed `check_reference`, a collection error unrelated
  to the target test's own existence, a `conftest.py`-level import
  error elsewhere in the target repo) — Stage 89A's own test list
  (§7) must cover at least "does not yet exist" (exit non-zero,
  reported as "not yet coverable", never conflated with the check
  itself failing) and "exists and collects cleanly" (§6.1 step 4); a
  third case (collection errors for an unrelated reason) is named here
  as a known gap for Stage 89A's own implementer to close with a
  fail-closed "cannot determine coverability" finding, never a silent
  false negative.

## 10. Explicit non-goals

- Phase 90 (comparative development trials) — not implemented,
  attempted, or anticipated beyond borrowing its already-published
  methodology document for §6.3's measurement design, exactly as this
  dispatch's own instruction requires.
- Any reopening of Phase 88's MCP architecture, trust model, or tool
  surface — Phase 89 is independently deliverable and touches none of
  `src/codecompass/mcp/`.
- Any reopening of Phase 87's clean-room reconstruction mode or manual
  incremental-maintenance mode — both remain exactly as they are;
  `docs compile`/`maintain`/`publish` gain a new *trigger* for their
  existing, unmodified behaviour, never new behaviour of their own.
- A `git diff`-parsing change-detection mechanism — content-hash
  comparison only, matching Phase 83's own already-settled choice.
- An automatic (`--yes`/no-review) reconciliation-apply mode — every
  write requires explicit human `"accept"`, no exception, in this
  phase's own MVP scope.
- Landing anything in the real `~/projects/ledgerkit` checkout — the
  two-task demonstration runs on disposable scratch copies only unless
  a separate, explicit cross-repository authorisation is given (§6.4).
- Any change to `change_impact.py::run_check_assurance`'s own
  `CONFIRMED_REGRESSION`/`VERIFIED_SCOPE`/`VERIFICATION_GAP`/
  `INVALID_ASSESSMENT` classification (§0.1's semantic correction) —
  the `"regression"`/`"newly_discovered_failure"`/`"newly_covered"`
  distinction is computed entirely in `source_reconciliation.py`, from
  data Phase 83 already returns unchanged, never by modifying Phase
  83's own classification function or its return shape.
