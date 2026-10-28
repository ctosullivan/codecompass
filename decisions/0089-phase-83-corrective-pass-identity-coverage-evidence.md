# 0089: Phase 83 corrective pass — source identity, range coverage, evidence validation

**Status:** accepted (2026-10-28). Governing prompt: "CodeCompass
Orchestrator — Phase 83 Corrective Pass" (2026-10-28, post-completion
source review). Phase 83 itself was marked `done` earlier the same day
(`5132529`, see `decisions/0086`/`0087`/`0088`); this ADR documents three
further correctness defects found by direct inspection of the shipped
`scripts/assess_change_impact.py`, after it had already passed an
independent audit — the audit exercised the scenarios the plan named, not
every code path, and none of the three defects below were among them.

## Context

Three suspected defects were named in the governing prompt. All three are
confirmed real by direct reading of `scripts/assess_change_impact.py` as
committed at `5132529`, not merely asserted:

**A. `classify_symbol()` matches Evidence by symbol name alone.** Line
260 (as shipped): `match.group("symbol") == symbol_name` — the regex's
own `path` capture group is parsed but never compared to the symbol
actually being assessed. Two first-party files that each happen to
declare a function with the same name (a real, ordinary occurrence —
`main()`, `__init__()`, a shared helper name) would have one's Evidence
silently answer for the other's behaviour.

**B. `resolve_changed_range()` identifies only one symbol, and never
validates `changed.end`.** The function calls `resolve_enclosing_symbol`
once, against `changed.start` only, returning a single `SymbolRow`. A
`--changed` range crossing two or more top-level declarations (the
ordinary shape of a real diff touching more than one function) silently
reports only whichever symbol encloses the range's own first line —
every other symbol touched by the same range is never resolved,
classified, or assessed at all, with no finding or reason recorded for
the gap. Separately, only `changed.start > line_count` is checked; a
`changed.end` past the file's own extent is never rejected — a
`--changed path:10-99999` against a 20-line file resolves exactly as if
`end` had been in range, because `end` is never consulted after being
parsed.

**C. `classify_symbol()` accepts a referenced result without validating
it as a real `OracleResult`.** Lines 279-287 (as shipped) call
`yaml.safe_load` directly on the referenced path, then check only that
the resulting mapping has a `check_id` key naming a real check in the
contract. No schema validation (`parse_oracle_result`'s own required-
field/type/outcome-enum checks), no `contract_id`/`oracle_contract_id`
match against the *live* contract, no `scope` match against the named
check's own `scope`. A malformed historical result (missing required
fields, entirely the wrong schema version), or one belonging to an
unrelated contract whose `check_id` happens to collide with a check_id
in the contract under assessment, or one recorded against the wrong
scope, would all currently be accepted as establishing a verified
coverage link (`behavioural_risk`) — manufacturing a *recorded
relationship* that was never actually curated.

## Decision

Fix all three in place, in `scripts/assess_change_impact.py` only.
`oracle.py`, `graph.py`, `knowledge_intermediate.py` are **not** touched —
every fix is achieved by `assess_change_impact.py` using those modules'
existing, unmodified public surface more completely than it already does
(`parse_oracle_result`, `OracleContract.check_by_id`, the existing
`source_symbols` table), exactly as Phase 83's own original design
required and as this pass's governing prompt repeats.

### A — source-path-qualified Evidence matching

`classify_symbol()` gains a `source_path: str` parameter — the path of
the file the symbol being assessed actually lives in (in practice,
`assess()`'s own `--changed` argument's own `path`, the same convention
`check_contracts.py::check_source_ref_symbol_depth` already resolves
`source_ref`'s own `path` group against). A `source`-kind Evidence now
only counts as citing the symbol under assessment when **both** its
`source_ref`'s `symbol` group matches the symbol name **and** its `path`
group, normalised via `PurePosixPath(...).as_posix()` on both sides
(matching this existing convention's own always-relative-POSIX-style
form; no filesystem resolution, no attempt to canonicalise against a
different repository root), matches `source_path`. No new identity
concept — reuses the Evidence's own existing `source_ref` convention
completely, where before it was read only partially.

### B — all intersecting symbols, and end-of-range validation

`resolve_enclosing_symbol` (single-point, single-result) is replaced by
`resolve_intersecting_symbols(symbols, line_count, start, end) ->
list[SymbolSpan]`, built on the same existing convention this plan
already names (§5 of the Phase 83 plan: "a symbol's span runs from its
own line to one less than the next symbol's line [or EOF for the last
symbol]") — generalised from a single lookup at `start` to every symbol
whose own span intersects the full `[start, end]` interval. `changed.end`
is now validated against the file's own line count exactly as
`changed.start` already was (`cannot_map` if either is past the file's
own extent). `RangeResolution.symbol` (singular) becomes `.symbols`
(plural, possibly containing more than one `SymbolRow`). A new status,
`partially_resolved`, is added alongside the existing `resolved` /
`stale_index` / `cannot_map`: when the matched symbols' own spans do not
cover the *entire* requested range (e.g. the range's own start lies in a
module's top-of-file region before any indexed top-level symbol),
`assess()` still classifies and assesses every symbol that *was* matched
— it does not discard the whole range — while the report's own `reason`
names exactly which line(s) remain unmapped, so a partial match is never
silently presented as if it were complete. A request matching zero
symbols at all (wholly outside every indexed span) remains `cannot_map`,
unchanged.

`assess()` now classifies every resolved symbol independently and
deduplicates the resulting applicable-check set *per range* — a check
triggered by two different touched symbols in the same range is
executed exactly once, with an added `AssuranceFinding.contributing_
symbols` field naming every symbol that made it applicable, so
deduplication never erases which symbol(s) actually triggered which
check (§2.B's own "without losing per-symbol provenance").

This remains bounded, declaration-based symbol localisation — no
interprocedural analysis, no call graph, no notion of control flow
inside a symbol's own span. A span is still exactly what Phase 83's
plan already defined it to be.

### C — validated historical-result evidence, never a parallel parser

`classify_symbol()` gains an `oracle_mod` parameter (the already-loaded
`codecompass.oracle` module, exactly as `run_check_assurance` already
receives it) and now calls `oracle_mod.parse_oracle_result(result_path)`
instead of a bare `yaml.safe_load`. A `parse_oracle_result` failure
(`OracleSchemaError` — malformed YAML, missing required fields, an
unsupported schema version, an invalid `outcome` value) causes that
`test`-kind Evidence to be treated exactly as if its `test_ref` had not
resolved at all — it contributes nothing towards `behavioural_risk`, the
citing `source`-kind Evidence (if any) still stands on its own as
`relevant_no_coverage_link`. A result that parses successfully is then
checked for genuine contract/check identity: `result.contract_id` must
equal the *live* contract's own `contract_id`; `contract.check_by_id
(result.check_id)` must resolve to a real check; and `result.scope` must
equal that check's own `scope`. Any mismatch is rejected on the same
terms — a structurally well-formed `OracleResult` belonging to a
different contract, or naming an unknown check, or recorded against the
wrong scope, never establishes a coverage link here.

This is deliberately **not** `evaluate_result_precedence` — that
function additionally recomputes live digests and raw-output integrity
against a `repo_root`, which is a *current execution outcome* question,
not a *recorded-relationship* question. `classify_symbol` has no
`repo_root` and must not acquire one for this purpose: §2.C's own
explicit requirement ("a structurally valid historical result may
establish a recorded check relationship, but must never manufacture
current verification") is only true if the two stay structurally
separate functions, called at separate times, for separate questions.
`run_check_assurance`'s own fresh-result precedence (`decisions/0087`)
is completely unchanged by this fix — `CONFIRMED_REGRESSION`/
`INVALID_ASSESSMENT`/`VERIFIED_SCOPE` still derive solely from a fresh
execution, never from whether a historical result happened to validate.

## Consequences

- `classify_symbol`'s signature changes (`oracle_mod`, `source_path`
  added) — every call site (`assess()`, and every existing unit test)
  updates in the same commit. This is an internal, maintainer-script-only
  function with exactly one real caller; no external compatibility
  surface exists to preserve.
- `RangeResolution`/`RangeReport`'s shape changes: `symbol`/
  `resolved_symbol` (singular) become `symbols`/`resolved_symbols`
  (plural); `RangeReport` gains `symbol_classifications` (one entry per
  resolved symbol, each with its own three-tier classification and
  claim findings) in place of the single top-level `classification`/
  `claims` pair. `AssuranceFinding` gains `contributing_symbols`. The
  JSON report's own shape changes accordingly — `docs/development/
  contributing.md`'s own description of this script is updated in the
  same pass to match (no other doc describes the JSON shape at this
  level of detail).
- No change to `oracle-contract.yaml`, no new knowledge records, no
  change to the real or scratch Ledgerkit checkouts' own test files —
  this pass is confined to `assess_change_impact.py` and its own test
  module, per the governing prompt's explicit "Do not reopen Phase 82 or
  expand Phase 83 into Phase 84 functionality."
- The one still-outstanding, separately-gated item named at Phase 83's
  own closeout (the real Ledgerkit test landing in `~/projects/
  ledgerkit`) is unaffected and remains exactly as outstanding as before.

## Alternatives considered

- **Leave `resolve_enclosing_symbol` in place and additionally scan
  forward for more symbols**, rather than replacing it with a proper
  interval-intersection function. Rejected: the forward-scan version
  would still need its own notion of each symbol's span to know *where*
  to stop scanning, which is exactly what `SymbolSpan` already is —
  keeping both would be two implementations of the same concept, one of
  them redundant.
- **For defect C, validate against `evaluate_result_precedence` with
  `repo_root=None`.** Considered, rejected: even with `repo_root=None`,
  that function still recomputes the live `oracle-contract.yaml` file's
  own hash (`sha256_file(contract_path)`) and compares it to the
  *historical* result's recorded `oracle_contract_content_hash` — which
  for any result predating a later contract extension (exactly the
  state Phase 83 itself left the real `balance-from-spec` contract in)
  would always report `INVALID`, collapsing "this result predates a
  content hash change" (a current-outcome fact, correctly volatile) into
  "this Evidence never validly cited this check" (a historical-
  relationship fact, which must not retroactively flip false merely
  because the contract gained an unrelated check later). Using the
  narrower, purely-structural identity/scope check keeps these two
  genuinely different questions answered by two different functions.
