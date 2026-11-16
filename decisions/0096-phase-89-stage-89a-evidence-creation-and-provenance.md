# 0096. Phase 89 Stage 89A: Evidence-creation path, in-place Claim-field
mutation exception, `check_id` Requirement field, and the
`on_fresh_result` provenance-capture mechanism

## Status

Accepted (2026-11-16, direct user request — "CodeCompass Orchestrator —
Implement Phase 89A with Additional Acceptance Tests"). Implementation,
not planning-only: this ADR documents the tradeoffs already decided in
`planning/phase-89-incremental-knowledge-documentation-reconciliation.md`
(six independently reviewed rounds, READY WITH NON-BLOCKING
OBSERVATIONS) plus three narrow implementation-contract resolutions the
plan itself left ambiguous, made during Stage 89A's own implementation
against real source. Governed by `decisions/0085` §3 (Phase 89's own
split-and-scope decision), which this ADR does not reopen.

## Context

Stage 89A adds a change-driven trigger — two sibling detectors plus one
new manifest item kind — layered on the *existing* Phase 81
reconciliation flow, Phase 82 oracle, and Phase 83 change-impact
classifier. Four tradeoffs are genuinely new, previously-untaken
decisions in this codebase, not routine extensions of an existing
mechanism (`CLAUDE.md` §2's "non-obvious tradeoff" trigger):

### 1. A disclosed, narrowly-scoped in-place Claim-field mutation

Every existing `apply_manifest` item kind (`anchor_edit`,
`candidate_addition`, `doc_region_edit`) follows this project's own
explicit convention: a semantic edit never overwrites the original
record directly — it always creates a new, competing candidate record
instead (`_apply_anchor_edit`'s own docstring). That convention exists
to protect against *semantic reinterpretation* — different wording for
what a Claim asserts.

**Decided**: the new `source_reconciliation` item kind deliberately
does *not* follow this convention. `_apply_source_reconciliation`
(`knowledge_intermediate.py`) appends to the target Claim's own
`contradicting_evidence`/`supporting_evidence` fields and recomputes
`evidence_support_state` in place. `statement`/`derivation`/`timestamp`/
every other field is never touched. This is justified on a narrower
ground than "reuse": humans already make exactly this edit by hand
today, routinely and without controversy, whenever new evidence for an
existing Claim arrives — a citation-list/derived-status update is
bookkeeping this project's own authors already treat as safe to make
directly, never a reinterpretation of what the Claim asserts. The
self-conflict risk this would otherwise create (two pending items
racing the same Claim's own content hash) is closed at the source:
`write_source_reconciliation_manifest` merges every finding against the
same Claim into that Claim's own single manifest item.

### 2. The first mechanized Evidence-creation path, with its own identity convention

Confirmed by direct grep before this implementation: zero existing call
sites created a new Evidence record programmatically anywhere in this
codebase (`_next_id(sdir, "EV"` never appeared). `_find_existing_
promoted_record` is typed to match `kind="claim"`/`"requirement"`
records against their own `statement` field; Evidence records have no
`statement` field (they have `what_it_shows`), so that helper cannot be
reused for Evidence identity under any parameterisation.

**Decided**: a new, narrow, Evidence-specific identity helper,
`_find_existing_evidence_for_run(project_root, records, contract_id,
check_id, run_id)` (`knowledge_intermediate.py`), keyed on the real
oracle run's own identity tuple — never a prose/content match, since
two separate real runs of the same check can legitimately produce
byte-identical raw output while still being two distinct,
independently-citable runs (`decisions/0082` §C). Checked before every
individual Evidence write inside a merged item's own multi-finding
apply, not once per item, because `apply_manifest`'s own per-item
`state="applied"` flag is buffered for the whole batch and only written
once the entire item loop completes — a crash partway through one
item's own internal multi-write is only ever safe to retry via this
exact, fresh-on-every-call, disk-state check.

### 3. The new, optional, additive `check_id` Requirement field

`oracle-contract.yaml`'s own `contract_id` resolves to exactly one
governing Requirement for the *whole contract*, never per-check.
Nothing machine-checkable linked a specific `check_id` to the specific
Requirement/Claim it is pinned for, when more than one check shares one
contract — only informal, inconsistently-used prose.

**Decided**: one small, additive, optional field, `check_id`, on the
Requirement record (purely additive YAML — confirmed no schema-code
change needed: `scripts/check_knowledge_base.py` has no "reject unknown
field" check, only required-field and optional-enum-field validators).
`REQ-BFS-002.yaml` backfilled with `check_id:
overlapping-account-patterns-no-double-count`. `detect_newly_coverable_
checks` enforces a fail-closed guard: before resolving `check_id` →
Requirement → Claim, it confirms that Requirement's own `depends_on` has
length exactly 1, refusing (a reported configuration error, never a
silent multi-Claim resolution) otherwise — nothing in `check_knowledge_
base.py` would otherwise reject a human mistakenly adding `check_id` to
a multi-check Requirement.

### 4. The additive `on_fresh_result`/`raw_output_dir` capture parameters on `change_impact.assess`/`run_check_assurance`

`run_check_assurance` computes a real, fully-populated `OracleResult`
(`oracle.evaluate_check`) but returns only an `AssuranceFinding` summary
with no `run_id`/`raw_output_ref`/digest fields at all — the data
detector (a) needs to persist durable Evidence provenance was
structurally unrecoverable from this pathway's own return shape, by
design (the summary is deliberately thin — Phase 83's own concern was
classification, never provenance).

**Decided**: two new, additive, default-`None`/`None` parameters —
`run_check_assurance(..., on_fresh_result: Callable[[OracleResult],
None] | None = None)` and `assess(..., on_fresh_result:
Callable[[int, OracleResult], None] | None = None, raw_output_dir: Path
| None = None)`. Every existing call site is unaffected: the one real
existing caller of `assess()` outside `change_impact.py` itself
(`src/codecompass/mcp/tools.py:342`) neither passes either parameter nor
reaches the code path that would invoke the callback (it passes
`run_checks=False`) — confirmed unaffected on two independent counts,
not merely "doesn't pass the new parameter." `run_check_assurance` has
zero call sites outside `change_impact.py`.

**Final callback signature, resolving an inconsistency in the plan's
own text** (the plan's §4.4 said `Callable[[OracleResult], None]` in
one place and `Callable[[str, OracleResult], None]` in another):
`run_check_assurance`'s own callback takes the `OracleResult` alone — a
second parameter is redundant, since `OracleResult` already carries its
own `check_id` field. `assess()` is the only level in this call chain
with *range* context (it iterates `changed: list[ChangedRange]`), so it
alone takes a zero-based range index as a first argument, wrapping the
single-arg form before passing it down to each `run_check_assurance`
call for that range.

**Multi-range capture, simplified from the plan's own "list per
check_id, consumed in range order" design**: within one `assess()` call,
`run_check_assurance` runs at most once per `(range, check_id)` pair —
`check_contributors` is freshly re-initialized inside the per-range loop
(`change_impact.py`'s `for c in changed:` / `for check_id in
sorted(check_contributors):`). `source_reconciliation.propose_
reconciliation`'s own `_capture` closure is therefore a **flat dict**
keyed by `(range_index, check_id)`, never a list — every key is
unique by construction, so there is no "consume in order" ambiguity to
get wrong. A dedicated regression test (two different `ChangedRange`s
in one call contributing the same `check_id`) confirms both captured
results are retained independently and each finding is paired with the
result from its own range.

## Two further implementation-contract resolutions (not named by the plan)

### 5. The durable raw-output convention

Phase 83's own `assess()` computed its internal `raw_output_dir` as
`knowledge_root / "planning" / "contracts" / slug / "scratch-
assessments"` — an absolute, explicitly-named-disposable path, never
intended to be durable. The existing Phase 88 MCP tool
(`oracle_execute_check`, `mcp/tools.py:452-466`) already establishes the
real durable convention this codebase uses elsewhere: a
**project-relative** `raw_output_dir` (`planning/contracts/<slug>/
results/raw`), with the whole `evaluate_check`/`write_oracle_result`
sequence run under a scoped `chdir(project_root)` so the stored
`raw_output_ref` ends up a stable, portable, relative path.

**Decided**: `source_reconciliation.py` reuses this exact convention
(its own `_durable_raw_output_dir`/`_chdir` helpers, duplicated locally
rather than importing `mcp.tools`'s private `_chdir`, since this module
has no other dependency on `mcp/`) for every real check execution it
performs — both through `assess(raw_output_dir=...)` for detector (a)
and via direct `oracle.evaluate_check(raw_output_dir=...)` calls for
the test-input-change and newly-coverable pathways. Every persisted
`OracleResult` is round-trip-verified immediately after being written
(`_persist_and_verify`): re-parsed, its `raw_output_ref` file confirmed
to exist with a matching hash, under the same scoped chdir. A result
that fails this check is never cited by any manifest item — fail-closed,
never a reconciliation proposal referencing a result that cannot be
independently re-read from disk.

### 6. Test-input-path contract-dependency mapping for test-only changes

`change_impact.classify_symbol` maps changed *source symbols* to
Claims; it has no path for "only a test file changed, no production
symbol changed at all." Existing Evidence records' own `test_ref` field
points to a *result file*, never to the actual test source file, so
there was no existing per-Evidence pointer to track test-file content
changes either.

**Decided**: `detect_source_changes` additionally tracks, for every
check with at least one existing citing `test`-kind Evidence record,
every file named in that check's own `oracle-contract.yaml`
`test_input_paths` list — compared against `source-baseline.toml`
through the identical graph-freshness-then-baseline sequence used for
source files. A drifted test-input file is reported as its own distinct
finding (`resolution="test_input_change"`), resolved directly via a new
`check_id → Claim` bridge lookup (`_claims_bridged_by_check_id`, reusing
`classify_symbol`'s own `test_evidence_check_id` bridge logic, inverted
to start from a `check_id` rather than a symbol) — never through
`classify_symbol`, since there is no symbol to resolve. This can never
be confused with detector (b)'s own scope (zero existing Evidence):
the two detectors' gates are provably mutually exclusive by
construction (a check either has existing citing Evidence or it does
not).

## Consequences

- `change_impact.py`'s public surface grows by two additive parameters;
  no existing behaviour changes for any caller that omits them.
- `oracle.py` gains one new function, `run_pytest_collect_only` — a
  collection probe, duplicating `run_pytest_check`'s own bounded-
  subprocess pattern in full rather than a shared-helper extraction
  (the two functions classify outcomes on genuinely different bases —
  junit-xml parsing vs. bare return code — and the extraction risk for
  a timeout/process-group-sensitive function was judged higher than the
  cost of controlled duplication, matching this project's own stated
  `scripts/`-duplicates-`scripts/` tolerance).
- `knowledge_intermediate.py` gains one new Evidence-identity helper and
  one new `apply_manifest` branch — the dispatch table's only other
  change.
- A known, disclosed limitation: baseline advancement for a
  `source_reconciliation` item is **not** wired automatically inside
  `apply_manifest` itself (that function has no `repo_root` in its
  generic signature). It is a separate, explicit function,
  `source_reconciliation.advance_baselines_for_applied_item`, which the
  CLI (`cli.py::knowledge_apply_manifest`) calls only after confirming a
  real, successful apply for that exact item — consistent with
  `CLAUDE.md` §1 L-087 (a baseline never advances on detection alone),
  but requiring the CLI layer, not the generic apply dispatch, to own
  this specific orchestration step.
