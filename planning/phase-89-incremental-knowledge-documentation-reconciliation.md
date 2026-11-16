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

```
Target repo source/test change (Ledgerkit, or any CodeCompass-indexed
project)
      │
      ▼
[NEW, narrow] source_reconciliation.detect_source_changes()
      — compares each tracked source_files.content_hash (already
        populated by that repo's own `codecompass sync`) against a
        persisted per-slug baseline (planning/knowledge/<slug>/
        reconciliation/source-baseline.toml — same TOML read/write
        helpers §1's _read_simple_toml_tables/_write_simple_toml_tables
        already use for .grounding-state.toml; a sibling file, not a
        new format)
      │  produces: list[(path, start, end)] candidate changed ranges
      ▼
change_impact.assess(changed=..., run_checks=True)   (Phase 83, REUSED,
                                                        UNCHANGED)
      │  produces: per-range Claim/Requirement findings, tiered
      │  no_recorded_relationship / relevant_no_coverage_link /
      │  behavioural_risk, and — for behavioural_risk with a bridging
      │  check — a fresh CONFIRMED_REGRESSION / VERIFIED_SCOPE /
      │  VERIFICATION_GAP / INVALID_ASSESSMENT classification
      ▼
[NEW, narrow] write_source_reconciliation_manifest(...)
      — a new SIBLING WRITER function (mirroring the already-production
        write_doc_candidates_to_manifests exactly, §1.1's corrected
        inventory — not an extension of write_manifest itself).
        ONE manifest item PER CLAIM (never per-finding): every
        CONFIRMED_REGRESSION/qualifying VERIFIED_SCOPE finding against
        the SAME Claim in one detection run is merged into that one
        item's own list of proposed new-Evidence citations, closing the
        self-conflict risk below by construction (never two pending
        items racing the same Claim's own hash). state="pending",
        decision="undecided" (Phase 81's existing 3-stage review
        convention, REUSED)
      │
      ▼  (human sets decision: "accept"/"reject", exactly as today)
apply_manifest()   (Phase 81, REUSED — one new recognised `kind`,
                     §5.3; writes one or more new Evidence records
                     (append-only, never edits/deletes an existing
                     record — unchanged convention) + a narrowly-scoped,
                     EXPLICITLY DISCLOSED deviation from this flow's own
                     "never mutate, always create a competing record"
                     convention: appends to the Claim's own
                     evidence_support_state/contradicting_evidence/
                     supporting_evidence fields ONLY — statement/
                     derivation/timestamp/every other field is never
                     touched — see §4.4 for why this specific, narrow
                     exception is justified rather than built around.
                     Only ever runs after explicit human "accept")
      │
      ▼  (the Claim's own file content hash has now genuinely changed)
detect_grounded_region_changes() → docs maintain → docs compile/publish
      (Phase 87, COMPLETELY UNCHANGED — already reacts correctly to any
       cited Claim's content hash changing, regardless of cause)
```

No new scheduler, event bus, knowledge store, or documentation
compiler. The one new module (`src/codecompass/source_reconciliation.py`,
§5) is a thin detector plus one new sibling manifest writer plus one
new `apply_manifest` branch; everything else in the diagram above is
Phase 81/83/87/84 code, unmodified.

## 4. Required planning decisions

### 4.1 How source/test changes are detected, identified, and compared
with known baselines

`detect_source_changes(project_root, slug, *, repo_root)` (§5.1): for
every `source`/`test`-kind Evidence record under `slug` whose
`source_ref`/`test_ref` names a file under `repo_root`, read that file's
*current* `source_files.content_hash` from `repo_root`'s own
`context-graph.db` (requires `repo_root`'s own prior `codecompass sync`
— an explicit precondition, reported as a GAP if absent, never silently
skipped) and compare it against the hash persisted in
`source-baseline.toml` the last time this slug was reconciled. A file
with no baseline entry is reported `new` (first-ever reconciliation for
that file) and its baseline is *not* established by detection alone
(mirrors `detect_grounded_region_changes`'s own `"new"`-is-read-only
rule exactly — establishing a baseline is a separate, explicit act,
`establish_source_baseline`, never a side effect of looking). No `git
diff` parsing — this is content-hash comparison only, Phase 83's own
already-established, explicitly chosen technique, not a new one.

### 4.2 How changes map to Claims/Requirements/Evidence/Decisions and
dependent documentation regions

Reused unchanged: `change_impact.classify_symbol` (Claim/Requirement
mapping, via existing `source_ref`/`supporting_evidence` citations) and
`detect_grounded_region_changes` (documentation-region mapping, via
existing `cited_ids` grounding markers). Phase 89 adds no new mapping
table — both already exist and already key off the same canonical
record ids.

### 4.3 Distinguishing genuine staleness from unrelated changes, missing
evidence, and contradictions

Reusing `change_impact`'s existing tiers with no new semantics:
- **Unrelated**: `no_recorded_relationship` — no citing Evidence found
  for the changed symbol. Not reported as a reconciliation candidate.
- **Missing evidence**: `relevant_no_coverage_link` — a Claim cites the
  changed symbol but no test-kind Evidence bridges to a real check.
  Reported via the existing `relevant_no_coverage_link` gap-adjacent
  classification (unchanged) — a coverage gap, not staleness; Phase 89
  never fabricates a check to close this.
- **Genuine contradiction (real staleness)**: a `behavioural_risk`
  finding whose fresh, re-executed outcome is `CONFIRMED_REGRESSION` —
  the checked behaviour used to pass and a fresh run now fails against
  the *same* check. This is the only tier this plan's own manifest ever
  proposes writing back (§4.4) — a fresh `VERIFICATION_GAP` (no fresh
  result yet) or `INVALID_ASSESSMENT` (the check itself errored) is
  reported as a finding but never proposed as a reconciliation, since
  neither establishes a real contradiction.
- **Re-confirmation, not staleness**: a fresh `VERIFIED_SCOPE` against a
  Claim whose `evidence_support_state` was already `supported` is a
  no-op for reconciliation purposes (nothing contradicted, nothing to
  write) — but a fresh `VERIFIED_SCOPE` against a Claim previously
  `partially_supported`/`unconfirmed` (i.e. closing a real, previously
  recorded gap) **is** proposed, since that is new, materially useful
  evidence a human should be able to accept into the record.

### 4.4 How canonical knowledge is reconciled without silently
overwriting previously accepted facts

Only through the existing, append-only `apply_manifest` flow (§3's
diagram), extended with one new item `kind`.

**A disclosed, narrowly-scoped deviation, not a mischaracterisation
(corrected after independent review found the original draft's
"reuse" claim false)**: every existing `apply_manifest` item kind
today (`"anchor_edit"`, `"candidate_addition"`, `"doc_region_edit"`)
follows this project's own explicit, established convention — "a
semantic edit never overwrites the original record directly... it
always creates a new, competing candidate [record] instead"
(`_apply_anchor_edit`'s own docstring, `knowledge_intermediate.py`).
That convention exists to protect against *semantic reinterpretation*:
a human or tool proposing different *wording* for what a Claim asserts
(its `statement`/`derivation` fields) must never silently overwrite the
original — a reviewer must see the new wording as a distinct, competing
proposal. **This is deliberately not what a `"source_reconciliation"`
item does.** It never touches `statement`/`derivation`/`timestamp`/any
authored prose field. It writes a **new** Evidence record (next
available `EV-<slug>-NNN` id, via the existing `_next_id` helper,
unmodified) citing the fresh oracle `run_id`/`raw_output_ref` — itself
fully consistent with the existing append-only convention, no
deviation needed there — and then, for the *same* existing Claim,
appends that new Evidence id to exactly one of
`contradicting_evidence`/`supporting_evidence` and updates
`evidence_support_state` **in place**. This is new, previously-
unmechanized behaviour for this codebase (no existing apply-path
function does this — confirmed by independent review) and this plan
states that plainly rather than citing a non-existent precedent. It is
justified, not merely asserted, on a narrower ground than "reuse":
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
the fresh result against the live contract (re-running nothing, just
re-checking file state) before writing, exactly as it already does for
`"anchor_edit"` items — never trusting the manifest's own say-so. The
self-conflict risk this deviation would otherwise create (§4.8) is
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
the new Evidence record) carries the same provenance conventions
already established elsewhere in this project — a `run_id`/
`raw_output_ref` for the triggering oracle result (Phase 82's existing
`OracleResult` schema, unmodified), the target repo's own git HEAD via
the same `_git_head_revision`-style helper `knowledge_api.py` already
uses (Phase 88's own pattern, reused independently of MCP), and the
manifest's own `manifest_id`/`created` fields (Phase 81's existing
convention, unmodified format). No new provenance scheme.

### 4.8 Behaviour after interrupted, repeated, ambiguous, or conflicting
reconciliation attempts

- **Interrupted**: the source baseline only advances
  (`advance_source_baseline_after_apply`, mirroring
  `advance_region_baseline_after_publish`'s own "only after the write
  itself actually succeeds" rule, `CLAUDE.md` §1's L-087) after
  `apply_manifest` reports a real, successful write for every accepted
  item in the batch — a crash or partial failure mid-apply leaves the
  baseline exactly where it was, so a re-run of detection reports the
  same findings again rather than silently treating an unfinished
  reconciliation as done. **Item-internal partial write, found by
  independent re-review (non-blocking, resolved here)**: a merged
  item's own apply step writes one new Evidence record per contributing
  finding (§5.3) — a crash after writing finding 1's own Evidence but
  before finding 2's would otherwise risk a duplicate Evidence record
  for finding 1 on retry. Closed the same way every existing apply-path
  function already closes this exact class of problem: before writing
  a new Evidence record, the apply step checks `_find_existing_
  promoted_record` (the same helper `_apply_anchor_edit`/`_apply_
  candidate_addition` already use) for a record already citing this
  exact `run_id`, and skips re-creating it if found — mirroring, not
  inventing, this project's own established idempotent-apply pattern.
- **Repeated**: re-running detection against an already-pending,
  unresolved manifest item for the same `(record_id, run_id)` pair is
  idempotent — mirrors `docs maintain`'s own existing idempotency
  guarantee for `doc_region_edit` items (no duplicate manifest entries
  pile up).
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

- **Deterministic**: content-hash comparison (§4.1), symbol/Claim
  mapping (§4.2), tier classification (§4.3), fresh check execution and
  its own outcome (reused, unmodified Phase 82/83 code).
- **Requires human judgement, surfaced not resolved**: whether an
  ambiguous multi-Claim/multi-check finding should be split, merged, or
  deferred — this plan reports every such case explicitly rather than
  guessing.
- **Requires explicit human approval before any write**: every single
  `"source_reconciliation"` manifest item's `decision` field (§4.4) —
  there is no `--yes`/auto-accept mode in this plan's own MVP scope
  (named explicitly as a non-goal, §12).

### 4.10 Modularity and CLI/API callability, independent of MCP

One new, thin CLI subcommand under the existing `codecompass knowledge`
sub-app, plus reuse of one already-existing one (not a new top-level
command, not an MCP tool — `decisions/0085` §3's own exclusion,
re-confirmed; wording corrected per independent review — only
`detect-changes` below is actually new):

- `codecompass knowledge detect-changes SLUG --repo-root PATH [--json]`
  — read-only; runs §4.1 + `change_impact.assess(run_checks=True)`;
  writes the `"source_reconciliation"`-kind manifest (§3) if anything
  is genuinely proposable, exactly as `knowledge select-candidates`
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

- `detect_source_changes(project_root, slug, *, repo_root) ->
  list[SourceChangeFinding]` — §4.1's baseline-diff detector. Reads
  `source-baseline.toml` via the existing `_read_simple_toml_tables`
  (imported from `knowledge_intermediate`, not duplicated); for each
  tracked source/test file with a drifted `content_hash`, resolves a
  `changed[path:start-end]` range (the file's own full line range if no
  finer-grained range is recorded — Phase 83's own existing line-range
  convention, not a new one) and returns it, annotated with the
  record(s) that cite it.
- `propose_reconciliation(project_root, slug, findings, *, repo_root,
  knowledge_root) -> Path | None` — calls `change_impact.assess(changed=
  [f.range for f in findings], run_checks=True, ...)` (Phase 83, verbatim
  signature reuse). `assess()`'s own `AssuranceFinding` objects are keyed
  by `check_id`, not `claim_id` — recovering the claim↔check link this
  function needs means re-walking `assess()`'s own returned
  `range_reports[].symbol_classifications[].claims[]` (where each
  `ClaimFinding` does carry `check_id`), not a new lookup table (a real,
  moderate implementation detail an independent review confirmed is
  recoverable from `assess()`'s existing return shape, not hand-waved).
  For each `CONFIRMED_REGRESSION`/qualifying `VERIFIED_SCOPE` finding
  (§4.3), groups by `claim_id` (§4.8's "ambiguous, same Claim" rule —
  never one item per finding, always one item per distinct Claim) and
  calls `write_source_reconciliation_manifest` (§5.3, a new **sibling
  writer function**, resolved — not left as an either/or — mirroring the
  real, already-production `write_doc_candidates_to_manifests` exactly,
  §1.1's corrected inventory; `write_manifest` itself is left untouched).
- `establish_source_baseline(...)` /
  `advance_source_baseline_after_apply(...)` — mirror
  `establish_new_region_baselines`/`advance_region_baseline_after_publish`
  exactly (§4.8).

### 5.2 `source-baseline.toml` (new, per-slug persisted file)

`planning/knowledge/<slug>/reconciliation/source-baseline.toml` — same
directory Phase 81's manifests already live in, same TOML read/write
helpers, a sibling format to `.grounding-state.toml`
(`{path: {content_hash: str, last_reconciled: iso8601}}`). Not a
canonical record; not committed-knowledge content — exactly the same
classification `.grounding-state.toml` already has.

### 5.3 `write_source_reconciliation_manifest` (new sibling writer) and
one new `apply_manifest` item kind: `"source_reconciliation"`

`write_source_reconciliation_manifest(project_root, slug, findings_by_
claim)` — a new function in `source_reconciliation.py`, structurally
mirroring the real, already-production `write_doc_candidates_to_
manifests` (called from `docs maintain`, §1.1's corrected inventory),
not an addition to `write_manifest` itself. One item per **Claim**
(§4.8), each listing every contributing finding's own `run_id`/
`raw_output_ref`/target `contradicting_evidence` vs.
`supporting_evidence` field, `state="pending"`, `decision="undecided"`.

A small, additive change to `knowledge_intermediate.apply_manifest`'s
existing dispatch (currently `"anchor_edit"` / `"candidate_addition"` /
`"doc_region_edit"`, §1.1's corrected inventory) — a new `elif
item["kind"] == "source_reconciliation":` branch that, on `decision ==
"accept"`: (a) re-validates every cited fresh oracle result still
parses and still belongs to the named contract/check (reusing
`oracle.parse_oracle_result` + the same contract-identity checks
`classify_symbol` already applies, §1.1 — never trusting the manifest's
own cached fields); (b) writes one new Evidence record per contributing
finding via the existing `_write_record`/`_next_id` helpers, unmodified
(fully consistent with this project's own append-only convention — no
deviation here at all) — **first checking `_find_existing_promoted_
record` (the same helper `_apply_anchor_edit`/`_apply_candidate_
addition` already use, found by independent re-review, non-blocking)
for a record already citing this exact `run_id`, skipping re-creation
if found, so a crash partway through a multi-finding merged item's own
writes is safe to retry without duplicating the findings already
written**; (c) **the one disclosed, narrowly-scoped deviation named in
§4.4**: appends each newly-written Evidence id to the target Claim's
`contradicting_evidence` (for a `CONFIRMED_REGRESSION`) and/or
`supporting_evidence` (for a qualifying `VERIFIED_SCOPE`) field and
updates `evidence_support_state` — to the existing `"conflicting"`
value (`knowledge_intermediate.py:1211-1214`, found by independent
re-review to already exist for exactly this case, non-blocking) when a
merged item's own contributing findings disagree, otherwise to
`"contradicted"`/`"supported"` as appropriate. The Claim's own
`statement`/`derivation`/every other field is never touched, and (per
§4.8) this is always the *only* pending item for this Claim in this
batch, so the existing whole-file-hash conflict check, re-run once
immediately before this write, can only ever genuinely fire against a
real, independent human edit — never against this item's own sibling.
On `decision == "reject"`: no write, item state becomes `"rejected"`,
mirroring the existing `"anchor_edit"` reject path exactly.

### 5.4 One new `find_gaps` gap kind: `"claim_contradicted_by_fresh_check"`

A Claim whose `evidence_support_state` still says `supported`/
`partially_supported` while a *pending, unapplied* `"source_
reconciliation"` manifest item exists proposing a `CONFIRMED_REGRESSION`
against it is reported by `find_gaps` as this new gap kind — surfacing
"this canonical fact is believed true but a fresh check already
disagrees and nobody has reviewed it yet" without requiring a caller to
separately know to go look in `reconciliation/*.toml`. Reuses the
existing `Gap` dataclass and `find_gaps`'s existing scan loop/response
shape verbatim.

## 6. Two-task Ledgerkit evaluation (the real-world exit gate)

Runs against **disposable scratch copies** by default (§6.4) — matching
Phase 88's own already-established, pre-authorised convention and this
dispatch's own instruction to distinguish evidentiary strength by
authorisation level, never assuming it.

### 6.1 Task A — a genuine development change produces new/changed
knowledge

Reuse the exact, real, already-identified Ledgerkit gap this project's
own knowledge already names and has evidence for: `ledgerkit/reports.py
::balance_from_spec`'s `overlapping-account-patterns-no-double-count`
scope (`REQ-BFS-002`/`DEC-BFS-002`/`CL-BFS-004`/`EV-BFS-001`) — the exact
check this session's own Phase 88 real-agent acceptance exercise
exercised, via `oracle_execute_check`, to a fresh `PASS`. **Corrected by
independent review**: that result was written only into a disposable,
session-scratchpad project-root
(`planning/retros/phase-88-mcp-real-client-acceptance.md`'s own "Session
2" account) and will almost certainly no longer exist by Stage 89C's
implementation time — Task A does not reuse a persisted artifact sitting
ready; it **regenerates this PASS result fresh**, following the exact,
already-documented procedure that acceptance exercise recorded (a
disposable Ledgerkit scratch copy, the same new test, the same
`oracle_execute_check` call), then proceeds from there. Task A is: run
`codecompass knowledge detect-changes balance-from-spec --repo-root
<the freshly re-created scratch copy with the new test and its fresh
PASS result>`, confirm it proposes a `"source_reconciliation"` item
upgrading `CL-BFS-004`/
`REQ-BFS-002` from their current gap state to a genuinely supported
state (citing the real, already-produced oracle `PASS` result as new
Evidence), accept it, and run `apply_manifest`.

### 6.2 Reconciliation — precision checks (the true-positive and
false-positive controls)

- **True-positive control**: confirm `detect-changes` correctly flags
  `REQ-BFS-002`/`CL-BFS-004` (the actually-affected records) and that
  `docs maintain` subsequently reports `claims_changed` for any doc
  region citing them (none exist today per the Phase 88 plan's own
  §18.2 finding — if still none at demonstration time, this control is
  instead run against a temporary, disposable schema-governed document
  created for this demonstration alone, citing `CL-BFS-004`, so the
  invalidation pathway itself is genuinely exercised end to end, not
  merely asserted to exist in principle).
- **False-positive control**: make a second, genuinely unrelated,
  disposable-scratch-copy-only change to Ledgerkit (e.g. a comment-only
  edit or a change to an unrelated report function with no citing
  Evidence) and confirm `detect-changes` reports it `no_recorded_
  relationship`/proposes nothing, and that every unrelated Claim and
  doc region's own case remains `noop` — the false-positive control is
  exactly as load-bearing as the true-positive one, per
  `planning/v2-roadmap.md`'s own Phase 89 §7.

### 6.3 Task B — a second task measurably benefits from Task A's
reconciled knowledge

**Pre-registered before Task B runs** (per this dispatch's own
instruction): a second, genuine Ledgerkit development task
(candidate: the next real, already-named gap in `balance-from-spec`'s
own knowledge, or a comparably-scoped real task selected at
implementation time and recorded here before Task B starts — not
selected retroactively to fit a result). Reusing `planning/
v2-evaluation-methodology.md`'s existing context-quality-evaluation
method (Phase 90's own methodology document, consulted, not
reimplemented): a `context-evaluator`-style **controlled comparison**
between (arm 1) a context packet for Task B drawn from the
post-reconciliation knowledge state, and (arm 2, the control) an
otherwise-identical packet drawn from the pre-reconciliation snapshot
(i.e. withholding exactly what Task A's reconciliation added) —
measuring: context correctness, presence/absence of the now-reconciled
fact, verification outcome (does Task B's own check pass/fail
differently depending on which packet informed it), editorial
preservation (zero unrelated content differs between arms), and token/
context-size overhead of the reconciliation machinery itself. **No
productivity/time claim** is made from this comparison alone — matching
this dispatch's own instruction and this project's own established
precedent (Phase 87C's comparator found scope completeness without
claiming a net time/cost advantage; Phase 90 is the only phase
authorised to attempt that broader claim).

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
(`detect_source_changes`/`propose_reconciliation`/
`write_source_reconciliation_manifest`/baseline helpers);
`source-baseline.toml` format; the new `"source_reconciliation"`
`apply_manifest` branch; `codecompass knowledge detect-changes` CLI
command. Tests: the true-positive and false-positive controls (§6.2)
run against disposable Ledgerkit scratch copies, standalone (not yet
wired to documentation); an interrupted-apply test (§4.8, crash
mid-batch leaves the baseline unchanged, confirmed by re-running
detection and seeing the same findings again); a multi-Claim-mapping
test (one changed symbol → two distinct Claims, each its own
independently-decided item); a same-Claim-merge test (two findings
against one Claim, confirmed merged into that Claim's own single item,
never two racing items — the direct regression test for Blocking
Finding 1's self-conflict risk); a disagreeing-outcomes test (a merged
item whose contributing findings include both a `CONFIRMED_REGRESSION`
and a qualifying `VERIFIED_SCOPE`, confirmed written to both
`contradicting_evidence` and `supporting_evidence` with
`evidence_support_state` set to `"conflicting"` — the regression test
for the second review round's finding (a)); a retry-idempotency test
(a simulated crash between writing two contributing findings' own
Evidence records within one merged item, confirmed a retry does not
duplicate the already-written one — the regression test for the second
review round's finding (b)); a conflicting-edit test (a Claim
hand-edited between detection and apply, confirmed refused, mirroring
the existing `"anchor_edit"` conflict test). **`CLAUDE.md` §1's L-021,
explicitly satisfied (independent review, Blocking Finding 2)**:
`apply_manifest` has exactly one real production call site,
`cli.py::knowledge_apply_manifest` (`codecompass knowledge apply
MANIFEST_PATH`) — at least one Stage 89A test invokes that real CLI
command directly against a manifest containing a `"source_
reconciliation"` item (via this project's own existing `typer`
CLI-testing convention, matching how other `knowledge` subcommands are
already tested), not only `apply_manifest()` called in isolation as a
library function. Independent audit checkpoint: `release-phase-auditor`
(stage-level, per `L-134`'s own now-landed fix — persisted report at
`planning/retros/_audit-phase-89-stage-89a.md` before this stage is
treated as closed).

**Stage 89B — The new gap kind and the documentation-cascade
demonstration** (§5.4, §6.1-§6.2's doc-invalidation leg, §4.5-§4.6).
Deliverables: `find_gaps`'s new `claim_contradicted_by_fresh_check`
gap kind; the end-to-end Task-A demonstration including the
documentation-invalidation control (§6.2's first bullet, including its
own disposable-schema-governed-document fallback if no real grounded
region exists yet). Tests: the new gap kind's own unit tests; an
end-to-end scratch-copy run of the full §3 diagram, start to finish.
Independent audit checkpoint: stage-level `release-phase-auditor` pass,
persisted per the same convention.

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

## 8. Definition of Done (mapped to the governing exit gate)

Matches `CLAUDE.md` §5 exactly, plus `planning/v2-roadmap.md`'s own
Phase 89 §9 exit gate specifically: every stage's own tests pass
(including both the true-positive and false-positive controls, §6.2);
the Task-A/Task-B two-task demonstration is complete with its
pre-registered Task B criteria met or honestly reported unmet (never
retroactively loosened); the controlled comparison shows the measurable
benefit **or** this plan's own closeout explicitly says it did not and
why (no overclaim, matching this project's own Phase 87C precedent); no
new doc-compilation/scheduler/knowledge-store code exists anywhere in
the diff (an independent auditor confirms this directly against the
real diff, not against this plan's own claim of it); `docs/`,
`architecture/`, `decisions/*` updated for whatever ADR this plan's own
genuinely new tradeoffs require (§5's new manifest kind and gap kind
are candidates — resolved at Stage 89A); phase retro filed with every
`TEMPLATE.md` section substantively filled; learnings triaged; a fresh,
independent `release-phase-auditor` pass against the exact commit about
to be marked done.

## 9. Risks and unresolved decisions

- **§6.3's Task B selection** is deliberately left to be named at
  Stage 89C's own start (pre-registered then, before Task B runs) rather
  than fixed now — fixing it in this plan would itself be a form of
  picking the result before the experiment, the opposite of what
  pre-registration is for.
- **Resolved by independent review** (no longer an open decision):
  `write_manifest` itself is left untouched; a new sibling writer,
  `write_source_reconciliation_manifest`, is introduced instead,
  mirroring the real, already-production `write_doc_candidates_to_
  manifests` precedent (§1.1's corrected inventory) rather than a
  hypothetical either/or.
- **Resolved by a second independent review round** (no longer open):
  a merged item's own disagreeing-outcome write (§4.8/§5.3) uses the
  existing `evidence_support_state: "conflicting"` value, never an
  invented one; a merged item's own multi-record partial-write-on-retry
  risk (§4.8/§5.3) is closed by the same `_find_existing_promoted_
  record` idempotency check every other apply-path function already
  uses. Both fold into the Stage 89A ADR below rather than requiring
  their own separate design document.
- **Whether an ADR is required** for (a) the new manifest `kind`/gap
  `kind` additions and (b) the disclosed, narrowly-scoped in-place-
  mutation deviation (§4.4) from this project's otherwise-universal
  "never mutate, always create a competing record" convention: **yes**
  for (b) specifically, under `CLAUDE.md` §2's "non-obvious tradeoff"
  trigger — a deliberate, reviewed exception to a convention this
  significant is exactly the kind of decision an ADR exists to record,
  separately from (a)'s more routine extension-of-an-existing-mechanism
  choice. Drafting it is Stage 89A's own first task, not assumed or
  pre-written here.

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
