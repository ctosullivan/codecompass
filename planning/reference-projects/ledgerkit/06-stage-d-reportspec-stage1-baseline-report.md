# Ledgerkit — Journal-Comment-Based `ReportSpec` Parsing: Discovery & Design Report

Scope: discovery + design only, per task instructions. No tracked file in
`ledgerkit-baseline` was modified. All reads stayed inside the assigned
repository clone.

---

## 1. Relevant existing source and how it currently relates

**`ledgerkit/models.py`**
- `Query` (line ~128): selection filter dataclass (`account`, `not_account`,
  `payee`, `date_from`, `date_to`, `depth`) — "which postings/transactions to
  include."
- `ReportSection` (frozen, line ~198): one named section — `name`,
  `accounts: tuple[str,...]` (OR-matched), `exclude: tuple[str,...]`,
  `label`, `depth`, `invert`.
- `ReportSpec` (frozen, line ~219): `name`, `sections: tuple[ReportSection,...]`,
  `show_subtotals`, `show_total`, `total_label`. Its own docstring says
  plainly: *"Journal-comment-based spec parsing (the `; report` / `; end
  report` syntax) is deferred to Milestone 3."* Today it is only ever
  constructed **programmatically** by a Python caller.
- `ReportSectionResult` (line ~244): mutable result of running a spec —
  `section`, `rows: dict[account, Decimal]`, `subtotal`, plus
  `to_dataframe()`.
- `Journal` (line ~296): the top-level container. It has no field for
  report specs today (no `report_specs` list/dict of any kind).

**`ledgerkit/reports.py`**
- `balance_from_spec(journal, spec, query=None) -> list[ReportSectionResult]`
  (line ~600) is the only consumer of `ReportSpec`. For each section it:
  applies the outer `query` via the canonical `query.compat._query_to_ast` +
  `query.eval.matches_posting` path (posting-level, Stage C Phase 8
  convergence), then OR-matches `section.accounts` / subtracts
  `section.exclude` via the private `_matches_pattern` helper (the **one**
  remaining matcher not yet converged onto the `query/` AST — documented
  as a deliberate, disclosed exception), applies `section.depth` (overrides
  `query.depth`), aggregates via `_aggregate_posting_amounts`, inverts sign
  if `section.invert`, and returns one `ReportSectionResult` per section in
  `spec.sections` order.
- No other function in `reports.py` reads or writes `ReportSpec`/`ReportSection`.

**`ledgerkit/parser.py`**
- `_parse_string_impl` (line ~939) is a single large line-oriented loop with
  one branch per directive kind. Directly relevant precedents for a new
  comment-introduced block directive:
  - **`comment` / `end comment`** (lines ~990-1012, ~1215-1230): a
    non-indented top-level directive (not comment-introduced — the keyword
    `comment` itself opens the block) that sets `in_block_comment = True`
    and then *silently discards every line* until a line stripped equals
    `"end comment"` or EOF. This is the closest **block-scanning** precedent,
    but it discards content rather than parsing it into a structure, and its
    start keyword is not itself inside a `;`/`#` comment.
  - **Standalone top-level comment lines** (lines ~1045-1109): the branch
    that currently handles any line whose stripped text starts with `;` or
    `#`. Critically: **a column-0 `;`/`#` line outside an open transaction
    and outside an `account`/`commodity` directive's subdirective block is
    silently skipped today** — nothing is captured, no hook exists. This is
    exactly the code path a `"; report"` / `"; end report"` line would hit
    right now: it vanishes with no trace. (Verified by reading the branch
    directly — `if current_txn is None and is_indented and (...account/
    commodity target...): ... continue` is the only non-discard sub-case;
    every other combination of column-0 `;`/`#` just `continue`s.)
  - **`account`/`commodity` directive's follow-on `;`-tag-scanning**
    (lines ~1072-1094, and `account_comment_target`/
    `commodity_comment_target` state): the only existing place where
    *indented* `;`-led lines following a directive are parsed into
    structured data (`parse_tags` → `declared_account_tags`/
    `declared_commodity_tags`) rather than discarded. This is the closest
    precedent for "a comment line that is actually syntax with meaning,"
    but it is driven by indentation under a non-comment directive, not by a
    `;`-prefixed keyword at column 0.
  - Directive dispatch order matters: block-comment check → lenient
    skip-mode → blank line → comment-line branch → `~`/`=` rule headers →
    transaction header → `comment` block start → subdirective consumption →
    `account`/`commodity`/`payee`/`tag`/`decimal-mark`/`P`/`alias`/
    `end aliases`/`Y`/`D`/`apply account`/`end apply account` → posting line.
    A new `; report` block would need to be recognized in the **comment-line
    branch** (before the generic "skip this comment" fallback), since by the
    time a `;`-led line is seen, it has already matched that branch.
  - `ParseError`/`ParseWarning` (lines ~79-95): `ParseError(message,
    line_number)`, with `ParseWarning` as a non-fatal subclass collected in
    `errors_out` in lenient mode (`parse_string_lenient`) or raised
    immediately in strict mode (`parse_string`). This is the existing
    two-tier error-reporting convention a new malformed-spec diagnostic
    should reuse rather than inventing a third error channel.

**`ledgerkit/cli.py`**
- `COMMANDS = ("balance", "register", "accounts", "print", "stats",
  "check")` (line 23) — **there is no `report` command today.** `-q`/
  `--query` (lines 106-115) is documented as applying to "balance, register,
  accounts, stats, and print" — `report` is conspicuously and correctly
  absent from that list, since the command doesn't exist.
- Every existing command follows the same shape in `main()`: parse
  `-q`/`--query` once into `(query_ast, query_depth)` (lines 233-251), run
  the basic/strict check gate, then call the matching `reports.*` function
  and format its structured return value for stdout. A `report` command
  would plug into this same `if args.command == "..."` chain.

**`ledgerkit/tags.py`**
- `parse_tags(comment)` is the general-purpose `name:value`
  comment-tag extractor, grounded in a hledger-fidelity brief
  (`dev-docs/planning/core-redefinition/20-tag-parsing-syntax-brief.md`).
  Not a grammar a `; report` block can reuse directly (different shape —
  key:value pairs vs. a structured block with named sections), but it is
  the project's existing template for "derive a grounded, documented
  mini-grammar from a brief before writing the scanner."

**`ledgerkit/loader.py`**
- `merge_journals` (line 216) concatenates `transactions`/`prices`/
  `declared_accounts`/`declared_commodities`/`declared_payees`/
  `declared_tags` across included files, **but does not propagate
  `declared_account_tags`/`declared_commodity_tags`** (both already exist
  on `Journal` and are simply omitted from the `Journal(...)` constructor
  call built by `merge_journals`). This is a **pre-existing gap**, not
  something this investigation introduces — but it is directly relevant:
  any new `Journal.report_specs`-shaped field would need `merge_journals`
  support added explicitly, and the fact that two prior dict fields were
  never added here is a concrete cautionary precedent (§6 below).

**`dev-docs/api-spec.md`**
- Line ~380: *"Journal-comment-based spec parsing (`; report` / `; end
  report` syntax) is `[DEFERRED — Milestone 3]`."* This line is now
  **stale relative to `ROADMAP.md`**, which reclassified the same item to
  Stage D (see §5). Not something to silently fix per this task's
  discovery-only scope, but worth flagging since a future implementation
  phase's docs-sync step will need to update this exact line.

---

## 2. Producer/consumer relationships a real implementation would need to respect or extend

```
 text (journal file)
      │
 [ parser.py ]  ─────────────────▶ produces Journal.report_specs (NEW)
      │                             (parallel to declared_accounts etc.)
      ▼
 [ models.py ]  Journal, ReportSpec, ReportSection  (ReportSpec/ReportSection
      │          dataclasses themselves need NO shape change — a
      │          comment-parsed spec is just another way to construct the
      │          exact same frozen dataclasses library callers already build
      │          by hand)
      ▼
 [ loader.py ]  merge_journals must concatenate report_specs across
      │          included files (currently would silently drop them,
      │          exactly as it silently drops declared_account_tags/
      │          declared_commodity_tags today — see §6)
      ▼
 [ reports.py ] balance_from_spec(journal, spec, query=None) — UNCHANGED.
      │          A comment-declared spec is just a ReportSpec instance;
      │          it is consumed identically to a hand-built one. No new
      │          report function is needed for the computation itself.
      ▼
 [ cli.py ]     NEW: a way to select a comment-declared spec by name and
                 invoke balance_from_spec with it, format ReportSectionResult
                 list for stdout. This is the one genuinely new consumer.
```

Key relationship constraints already established elsewhere in the codebase
that a comment-parsed-spec feature must respect:

- **`ReportSpec`/`ReportSection` are frozen dataclasses** (hashable,
  immutable, compared by value). A comment-parsed spec must still produce
  genuine instances of these same types — not a parallel "yaml-ish" dict
  shape — so that `balance_from_spec`, `to_dataframe()`, and existing tests
  that construct `ReportSpec` by hand keep working unchanged and so library
  callers can round-trip (parse from comments, inspect/modify
  programmatically — though frozen-ness limits modification to
  `dataclasses.replace`).
- **`reports.py` never prints** (`dev-docs/architecture.md`'s stated
  invariant, reinforced by `06-core-architecture.md` §6.6: "every report
  function must be callable and useful from pure Python without going
  through `cli.py`"). A comment-declared report must still be fully usable
  as `balance_from_spec(journal, journal.report_specs["Budget"])` from a
  pure-Python caller, with the CLI `report` command as just one more
  consumer, not the only way to reach it.
- **The parser never discards structural information silently when it
  doesn't have to** — contrast `comment`/`end comment` (genuinely discarded,
  by hledger's own design) with `account`'s follow-on tag comments (kept,
  structured). A `; report` block is semantically much closer to the latter:
  it's meaningful content wrapped in comment syntax specifically so
  hledger/other tools ignore it, not content the user wants thrown away.
- **Lenient vs. strict error handling is already bifurcated**
  (`parse_string` raises immediately; `parse_string_lenient` collects into
  `errors_out`). A malformed `; report` block must plug into both paths
  identically to every other directive, not invent a third error-handling
  style.
- **`_matches_pattern`/HledgerRegex validation is the project's single
  account-pattern dialect** (Stage C Phase 8 convergence, documented at
  length in `reports.py`'s own module-level comments and
  `_matches_pattern`'s docstring). `ReportSection.accounts`/`.exclude`
  patterns from a parsed `; report` block must be validated the same way
  programmatically-built ones already are — i.e. still routed through
  `_matches_pattern`/`compile_hledger_regex` at `balance_from_spec` call
  time, not given a second, parser-level regex dialect.
- **Stable-API discipline** (`06-core-architecture.md` §6.4,
  `dev-docs/versioning.md`): adding `Journal.report_specs` is an additive
  field on an existing public dataclass — fine under today's SemVer
  convention — but exposing a *new* public parsing entry point (e.g.
  `ledgerkit.parse_report_spec_comment`) would need to be deliberately
  declared, not silently added, per that section's stated process.

---

## 3. Execution path a comment-declared report would need to follow end-to-end

1. **Parse time** (`parser.py`, inside `_parse_string_impl`'s per-line loop):
   a column-0 line whose stripped text starts with `;` (never `#` — matching
   the project's existing "only `;` ever carries structured meaning in a
   comment, `#` never does" rule used throughout `tags.py`/directive
   tag-scanning) and whose content after the `;` matches a `report` keyword
   enters a new accumulation mode (parallel sibling to `in_block_comment`,
   e.g. `in_report_spec_block` / `report_spec_lines: list[str]`). Subsequent
   `;`-led lines are appended (content captured, not discarded) until a line
   whose content is exactly `end report` (mirroring `_END_ALIASES`'s
   lenient-whitespace-matching style) or EOF is reached. A non-`;`-led line,
   a blank line, or a new transaction header while inside the block is a
   malformed-spec condition (see §7) rather than silently closing it, since
   hledger comment syntax has no other natural terminator.
2. **Grammar parse**: the accumulated lines are handed to a new, isolated
   function (e.g. `_parse_report_spec_block(lines, start_lineno) ->
   ReportSpec`) that turns the structured-comment mini-language into real
   `ReportSpec`/`ReportSection` instances — see §7 for the proposed grammar.
   This function should live in `parser.py` (it's text → structured-object
   work, the parser's job) and import `ReportSpec`/`ReportSection` from
   `models.py`, exactly as the rest of `parser.py` already does for
   `Posting`/`Transaction`/etc.
3. **Attachment to `Journal`**: the resulting `ReportSpec` is appended to a
   new `Journal.report_specs: list[ReportSpec]` field (or
   `dict[str, ReportSpec]` keyed by `spec.name` — see §6 open question),
   populated the same way `declared_accounts` etc. are today (a local list
   threaded through `_parse_string_impl`, passed into the final
   `Journal(...)` constructor call at line ~1655).
4. **Merge across included files**: `loader.merge_journals` must explicitly
   concatenate/merge `report_specs` the same way it already does for
   `transactions`/`prices`/`declared_accounts` — and, per §6, should also
   close the pre-existing gap for `declared_account_tags`/
   `declared_commodity_tags` while touching this function, or at minimum
   not repeat the same omission for the new field.
5. **Selection**: a CLI `report` command (new entry in `COMMANDS`) takes a
   spec name (likely as the existing `journal` positional argument's role,
   analogous to how `check`'s positional argument means something different
   from every other command — precedent already exists in `cli.py` for a
   command repurposing the positional slot) and looks it up in
   `journal.report_specs`.
6. **Computation**: unchanged — `reports.balance_from_spec(journal, spec,
   query=query)` is called exactly as it is today for a hand-built spec,
   with `query` built from `-q`/`--query` exactly as every other command
   already does (see §6's open question about `-q` composition).
7. **Formatting**: `cli.py` formats the returned `list[ReportSectionResult]`
   for stdout — new formatting code, but following the existing per-command
   pattern (compute structured data in `reports.py`, format only in
   `cli.py`).
8. **Library-level access**: a pure-Python caller never needs the CLI at
   all — `journal.report_specs["Monthly Budget View"]` (or equivalent) plus
   `balance_from_spec` is sufficient, preserving the §6.6 invariant.

---

## 4. Existing test coverage: adjacent vs. net-new

**Already covered (adjacent, reusable as regression anchors):**
- `tests/test_reports.py` — `TestReportSpecDataclasses` (frozen-ness of
  `ReportSection`/`ReportSpec`, mutability of `ReportSectionResult`),
  `TestBalanceFromSpec` (basic section computation, depth override,
  invert, empty-section edge cases), `TestBalanceFromSpecQueryConvergence`
  (outer `query.account`/`.not_account`/`.payee` interacting with a spec),
  `TestReportSectionHledgerRegexValidation` (section `accounts`/`exclude`
  pattern validation via `compile_hledger_regex`). All of this exercises
  `balance_from_spec`'s computation given an already-constructed
  `ReportSpec` — i.e. everything **downstream** of parsing. None of it
  constructs a spec from journal text.
- `tests/test_dataframe.py` — `TestReportSectionResultToDataFrame`:
  `to_dataframe()` on `balance_from_spec` output. Also downstream-only.
- `tests/test_parser/test_parser.py` — `TestBlockComments`,
  `TestCommentSpec` (the T-series): the closest *structural* precedent for
  testing a new comment-triggered block-parsing mode (open/close markers,
  EOF-without-close behaviour, malformed/no-blank-line interactions,
  lenient-vs-strict error collection). These are a template to imitate, not
  tests that exercise the new feature.
- `tests/test_directives/test_directives.py` — directive-inside-
  `comment`-block tests (an `account`/`commodity`/`payee`/`tag`/`P`
  directive placed inside a `comment`/`end comment` block is ignored).
  Relevant as a precedent for what should happen if a `; report` block is
  nested inside (or overlaps) a `comment`/`end comment` block — an edge
  case the new grammar must define explicitly (see §6).
- `tests/test_cli/test_cli.py` — per-command CLI integration test pattern
  (building argv, capturing stdout, checking exit codes) that a new
  `report` command's tests should follow.

**Entirely net-new (no existing test exercises any of this):**
- Any test that parses `; report` / `; end report` text and asserts a
  `ReportSpec` comes out the other end — **does not exist anywhere in the
  suite**. Confirmed by `grep -rn "ReportSpec\|ReportSection\|balance_from_spec\|report"` across `ledgerkit/` and `tests/` (full results in the research
  trace) turning up zero hits combining `; report`/comment-parsing with
  `ReportSpec`.
- `Journal.report_specs` (or equivalent field) does not exist, so no test
  references it.
- The CLI `report` command does not exist — `COMMANDS` tuple confirmed via
  direct read of `cli.py` line 23 — so no CLI-level test for it exists,
  and no test exercises `-q`/`--query` composed with a comment-declared
  report.
- `merge_journals` + `report_specs` across `include`d files — net-new,
  and should be designed with the existing `declared_account_tags`/
  `declared_commodity_tags` omission in mind (§6).
- Malformed-spec diagnostics (unterminated block, unknown keyword inside
  the block, duplicate section name, etc.) — net-new; no precedent
  diagnostic exists for a *structured* comment block failing to parse
  (the closest analogue, `comment`/`end comment`, cannot fail to parse by
  construction — it has no internal grammar to violate).

Per `CLAUDE.md` §1's phase-planning rule (Phase 55b / L-021 and the Phase 79
amendments), a future implementation phase's plan must name
`balance_from_spec` and the (to-be-added) CLI `report` command as real call
sites and include tests that exercise a parsed `ReportSpec` through both —
not only unit tests of the new parsing function in isolation — and must
separately test the minimal-but-well-formed malformed-input edge case
(e.g. `"; report\n; end report\n"` with zero sections) in addition to a
descriptively-broken block, given the depth-gap lesson (L-075) about
checking that a found entry's own value is well-formed, not just that
"a spec was found."

---

## 5. Relevant docs

- **`dev-docs/api-spec.md`** line ~380: marks the syntax
  `[DEFERRED — Milestone 3]` inside the `ReportSpec` entry. This is the
  line the task description points at; confirmed verbatim.
- **`ROADMAP.md`**:
  - Line 126 (Milestone 2's "Deferred to Milestone 3" list) and line 165
    (Milestone 3's own "Deferred to future milestones" list) both repeat
    the same deferred item, i.e. it was deferred twice before being
    reclassified.
  - Line 263, the Future/Backlog reclassification table (dated 2026-09-12):
    `| Journal-comment ReportSpec parsing | [BACKLOG] | Stage D (Reporting) |`.
  - Line 286, the Stage table: `| D | Reporting — shared primitives,
    structured output, render/semantics separation | [PLANNED] |
    core-redefinition/06 §6.1 |` — confirms Stage D has **not been started**
    (no Stage D plan file exists under `dev-docs/planning/` — only
    `core-redefinition/06-core-architecture.md`, which is a
    cross-stage architecture plan, not a Stage D-specific phase plan).
- **`dev-docs/planning/core-redefinition/06-core-architecture.md`** §6.3's
  table row for "Report engine": *"Extend to consume `query/` instead of the
  `Query` dataclass directly; keep the 'reports don't print' principle
  unchanged."* No mention of comment-based parsing specifically — Stage D's
  detailed design does not exist yet anywhere in this repository's
  `dev-docs/planning/`. This investigation is accordingly genuine
  green-field design work, not a reconstruction of an already-decided plan.
- **`dev-docs/architecture.md`**: the pipeline diagram and "reports don't
  print" / "each module imports only from modules below it" principles,
  both directly load-bearing constraints on where new parsing/formatting
  code may live (confirmed: parsing → `parser.py`; computation →
  `reports.py`; printing → `cli.py` only).
- **Staleness note (observation, not a fix):** `dev-docs/api-spec.md`'s
  "Milestone 3" label for this item is now inconsistent with `ROADMAP.md`'s
  "Stage D" reclassification (dated 2026-09-12, per the Future/Backlog
  table's own header). A future implementation phase's docs-sync step
  (`CLAUDE.md` §2/§5) will need to update that exact line, not just add new
  content elsewhere in `api-spec.md`.

---

## 6. Open design questions / uncertainties not resolved with confidence

1. **`-q`/`--query` composition with a comment-declared report.**
   `balance_from_spec` already accepts an outer `query` parameter
   orthogonal to the spec's own sections (§1/§2 above), and `cli.py`
   already parses `-q` into `(query_ast, query_depth)` for every other
   command. The natural extension is `report NAME -q "..."` passing that
   same `query_ast`/`query_depth` through to `balance_from_spec` as the
   outer filter — but `balance_from_spec`'s signature takes `query: Query |
   None`, **not** `_query_ast`/`_query_depth` the way `balance`/`register`/
   `accounts`/`stats` do. Those four functions were converged onto the
   `query/` AST specifically via private `_query_ast`/`_query_depth`
   parameters (Stage C Phases 2-8); `balance_from_spec` was **not**
   included in that convergence's private-parameter surface — it still
   only takes the legacy `Query` dataclass. I could not determine from the
   source alone whether this is (a) an intentional, disclosed scope
   boundary of Stage C Phase 8 that Stage D is expected to close, or (b) an
   oversight. `dev-docs/api-spec.md`'s own `balance_from_spec` entry
   confirms the "outer query converged" phrasing refers only to the
   `Query` dataclass's own account/not_account/payee/date fields
   (`ledgerkit.query.compat._query_to_ast` applied to `query`, not to a
   separate `_query_ast` parameter) — so a CLI `report` command wired via
   `-q` would need `balance_from_spec` to either (i) gain `_query_ast`/
   `_query_depth` parameters mirroring the other four report functions, or
   (ii) have the CLI translate `query_ast`/`query_depth` back into a
   `Query` object, which is lossy for anything beyond the `Query`
   dataclass's five fields (e.g. `tag:` terms, `not:`, OR-combinations).
   This is a real design fork Stage D must resolve explicitly, not an
   implementation detail.
2. **`Journal.report_specs` shape: `list` or `dict[str, ReportSpec]`?**
   A CLI `report` command needs to select a spec **by name** —
   `ReportSpec.name` already exists and is presumably meant to be the
   lookup key (it's documented as a *display* name, e.g. `"Monthly Budget
   View"`, not obviously intended as a unique identifier). A `dict` keyed by
   name is more ergonomic for lookup but raises an immediate question with
   no existing precedent to resolve it: what happens when two `; report`
   blocks declare the same `name` (within one file, or across `include`d
   files via `merge_journals`)? hledger-fidelity isn't a guide here since
   this syntax is a Ledgerkit-specific extension with no hledger analogue
   to replicate — this is a genuinely open product decision, not something
   derivable from the codebase.
3. **Interaction with `comment`/`end comment` blocks.** Existing tests
   (`tests/test_directives/test_directives.py`) establish that directives
   placed *inside* a `comment`/`end comment` block are inert. Should a
   `; report` ... `; end report` block that happens to fall inside a
   `comment`/`end comment` region also be inert (consistent), or does its
   own comment-syntax wrapper make nesting meaningless/undefined? I could
   not find any basis in the existing grammar to decide this either way —
   it needs an explicit design ruling.
4. **`merge_journals` gap.** `merge_journals` already silently drops
   `declared_account_tags`/`declared_commodity_tags` when merging multiple
   journals (confirmed by reading its `Journal(...)` constructor call —
   those two fields are simply absent from the keyword arguments passed,
   even though both exist on `Journal` and are populated by `parse_string`/
   `parse_string_lenient`). This is a **pre-existing bug independent of
   this task**, but any new `report_specs` field added to `Journal` is at
   direct risk of the same omission unless `merge_journals` is deliberately
   audited and fixed as part of implementing this feature (or the gap is
   explicitly carried forward as a documented, separate pre-existing
   issue — the plan should say which).
5. **Does the grammar need nested/structured keys beyond
   `ReportSection`'s existing fields**, e.g. a way to express
   `show_subtotals`/`show_total`/`total_label` (today `ReportSpec`-level,
   not `ReportSection`-level) from inside the comment block? The proposed
   grammar in §7 covers this, but it's a judgment call about how much of
   `ReportSpec`'s full surface the comment syntax needs to expose on day
   one versus deferring some fields (e.g. `total_label`) to a later
   iteration — I have no strong signal from the codebase either way.
6. **One spec per block vs. multiple `; report` blocks per file** — assumed
   multiple (consistent with `account`/`commodity`/`P` all being
   freely-repeatable directives throughout the file) — but this is an
   assumption, not something confirmed by any existing text or design doc.

---

## 7. Proposed design

This section is a discovery-stage design proposal only — intentionally
conservative, reusing existing project idioms rather than inventing new
ones, and flagging where a future plan file must make an explicit decision
(cross-referencing §6).

### 7.1 Grammar

```
; report NAME
; section SECTION-NAME
;   account PATTERN
;   account PATTERN          (repeatable — OR-combined, matches ReportSection.accounts)
;   exclude PATTERN          (repeatable — matches ReportSection.exclude)
;   depth N
;   invert
;   label TEXT
; end section
; section SECTION-NAME-2
;   ...
; end section
; end report
```

Rationale for this shape:
- Every line is `;`-prefixed (never `#`), consistent with the project's
  single existing rule that only `;` ever carries structured meaning in a
  comment (`tags.py`, account/commodity directive tag-scanning).
- `report NAME` / `end report` are the two markers the task explicitly
  names; `section NAME` / `end section` is a new but minimal addition
  needed because `ReportSpec.sections` is itself a collection of
  structured records, not a flat list of scalars — there's no way to
  express "which fields belong to which section" without *some* nesting
  marker, and `section`/`end section` mirrors the existing `comment`/
  `end comment`, `apply account`/`end apply account`, `alias`/`end
  aliases` naming convention (`KEYWORD` ... `end KEYWORD`) already used
  four times elsewhere in this exact parser.
- Each `; section` line's body-keywords (`account`, `exclude`, `depth`,
  `invert`, `label`) map 1:1 onto `ReportSection`'s existing fields — no
  new semantic concept is introduced, only a textual encoding of fields
  that already exist and are already fully specified by
  `ReportSection`'s own docstring.
- `invert` is a bare keyword (boolean flag), matching how `-s`/`--strict`
  etc. are bare flags elsewhere in this project's CLI, rather than
  `invert true`/`invert yes`.
- Top-level `ReportSpec` fields other than `name`/`sections`
  (`show_subtotals`, `show_total`, `total_label`) are proposed as optional
  `; KEYWORD VALUE` lines directly under `; report NAME`, before the first
  `; section`:
  ```
  ; report NAME
  ; show_subtotals false
  ; total_label Net Worth
  ; section ...
  ```
  This keeps the common case (just sections, all defaults) minimal while
  not foreclosing the less common case. (Flagged in §6.5 as a judgment call
  that a plan should confirm, not something I'm asserting is definitely
  right.)
- Account/exclude patterns are taken as raw, unescaped strings — identical
  treatment to how `ReportSection.accounts`/`.exclude` patterns are already
  validated at `balance_from_spec`-call time via `_matches_pattern`/
  `compile_hledger_regex` (§2). The parser does **not** need to validate
  HledgerRegex syntax at parse time — it only needs to extract the string;
  `balance_from_spec` already raises `UnsupportedRegexConstructError` for a
  bad pattern at the point it's actually used, exactly as a
  programmatically-built `ReportSpec` with a bad pattern does today. This
  keeps the new parsing code simple and avoids a second place regex
  validity rules can drift.

### 7.2 How a malformed spec block is reported

Reuse the existing two-tier `ParseError`/`ParseWarning` + `errors_out`
convention exactly as every other directive in `parser.py` already does —
no new error-reporting mechanism:

- **Unterminated block** (`; report NAME` reaches EOF or a blank line or a
  non-`;` line without `; end report`): a `ParseError` at the block's start
  line (mirroring how `_ALIAS_DIRECTIVE`/`_P_DIRECTIVE` report errors at
  the directive's own start, not where they discover the problem) — raised
  immediately in strict mode (`parse_string`), appended to `errors_out` in
  lenient mode (`parse_string_lenient`), with the malformed block's partial
  content discarded (no partial `ReportSpec` is added to `Journal.
  report_specs`) — matching the existing convention that a malformed
  transaction block is fully discarded in lenient mode, not partially kept.
  Unlike `comment`/`end comment` (where reaching EOF is explicitly
  *silently accepted* per that directive's own documented edge case), a
  `; report` block reaching EOF unterminated should be a hard error: its
  content is meant to be parsed into something structurally complete, so
  "silently truncated" is a real data-loss risk the inert `comment` block
  doesn't share.
- **Unknown keyword inside the block** (e.g. `; frobnicate x` inside an
  open `; section`): `ParseError`/`ParseWarning` at that line's number,
  same strict/lenient split. (Judgment call: a `ParseWarning`, not a hard
  `ParseError`, seems more consistent with this project's general
  leniency toward unrecognized directive-adjacent content elsewhere in the
  parser — e.g. unindexed Ledger-style subdirectives are silently
  consumed — but an unrecognized keyword *inside a block whose entire
  purpose is this specific grammar* is arguably different from an
  unrelated subdirective. This should be an explicit decision in the
  implementation plan, not assumed.)
- **`account`/`exclude` with no value, `depth` with a non-integer value,
  a `; section` with zero `account` lines**: `ParseError`, following the
  same pattern as `decimal-mark`'s own value-validation
  (`decimal-mark must be '.' or ','`) and `Y`'s int-parsing
  (`invalid Y directive year`).
- **The mechanism's own minimal-content edge case** (per `CLAUDE.md`'s
  Phase 79 fifth/sixth amendments, §1): a syntactically well-formed but
  empty spec — `"; report Empty\n; end report\n"` (zero sections) — must be
  a named, explicitly-tested case, not merely implied by the "malformed
  block" tests. `ReportSpec(name="Empty", sections=())` is already a
  value `balance_from_spec` accepts (see
  `tests/test_reports.py`'s own `test_empty_sections_with_query` case,
  confirmed in the earlier search) — so the open design question is
  whether a *parsed* zero-section spec should be accepted identically
  (consistent with the existing programmatic-construction behavior) or
  rejected at parse time as almost-certainly a user mistake. Given L-075's
  "depth, not just scope" lesson, a future plan's verification step should
  test both: that a zero-section block is *found and attributed a real,
  correctly-named `ReportSpec`* (not just that "parsing succeeded"), and
  separately whatever rejection/acceptance decision is made for it.

### 7.3 How the parsed `ReportSpec` reaches a report

1. `parser._parse_string_impl` accumulates parsed specs into a local
   `report_specs: list[ReportSpec]` (parallel to `declared_accounts` etc.),
   appended to the `Journal(...)` call at the end of `_parse_string_impl`.
2. `models.Journal` gains `report_specs: list[ReportSpec] = field(default_factory=list)`
   (list form, pending the dict-vs-list decision in §6.2; a list is the
   conservative, decision-deferring choice since converting list→dict
   later is additive, while shipping a dict now and later discovering
   duplicate-name semantics were wrong is not).
3. `loader.merge_journals` gains explicit `report_specs=[s for j in journals
   for s in j.report_specs]` in its `Journal(...)` call — and, while this
   function is being touched for this feature, the pre-existing
   `declared_account_tags`/`declared_commodity_tags` omission (§6.4) should
   at minimum be flagged to the implementing phase's author even if fixing
   it is out of this feature's own scope.
4. `cli.py` gains a `report` entry in `COMMANDS`, and a new code path
   (mirroring `check`'s precedent of repurposing the positional `journal`
   argument for a different meaning) where the first positional argument
   after `report` is the spec name, looked up via
   `next((s for s in journal.report_specs if s.name == NAME), None)`,
   erroring (`ledgerkit: no report named 'NAME'`, exit 1) if absent —
   matching the existing `ledgerkit: <message>` stderr + exit-1 convention
   used by every other CLI error path in `main()`.
5. `reports.balance_from_spec` itself needs **no change** to serve the CLI
   path, *unless* §6.1's `-q` composition question is resolved in favor of
   adding `_query_ast`/`_query_depth` parameters to it — in which case that
   is the one required change to `reports.py`, and it should be scoped and
   tested exactly as Stage C Phase 8 scoped the equivalent convergence for
   `balance`/`register`/`accounts`/`stats`.
6. No change to `ReportSpec`/`ReportSection`/`ReportSectionResult`
   themselves — the entire feature is additive at the parser/`Journal`/
   `cli.py` layers, which is the direct, verifiable consequence of
   `ReportSpec` already being a complete, usable, frozen dataclass today
   with only its *construction route* missing.

---

## Research trace

**Files read (in order), with purpose:**
1. `ledgerkit/reports.py` (full) — understand `balance_from_spec`, the
   `_query_ast`/`_query_depth` convergence pattern used by every other
   report function, and `_matches_pattern`.
2. `ledgerkit/models.py` (full) — understand `Query`, `ReportSection`,
   `ReportSpec`, `ReportSectionResult`, `Journal`, and find the exact
   "deferred to Milestone 3" docstring line.
3. `ledgerkit/parser.py`, offset 1 limit 1246 (truncated by tool output cap;
   first ~1246 of 1722 lines) — regex definitions, `_parse_posting`,
   `_parse_txn_header`, `_flush_txn`, start of `_parse_string_impl`'s
   directive-dispatch loop (block comments, lenient skip mode, blank-line
   handling, standalone/follow-on comment-line branch, `~`/`=` rule
   skipping, transaction-header detection, `comment` block start).
4. `ledgerkit/cli.py` (full) — confirm `COMMANDS` tuple has no `report`
   entry, understand the `-q`/`--query` parse-once pattern, the per-command
   `if args.command == ...` dispatch shape, and the CLI's error-reporting
   convention (`ledgerkit: <msg>` to stderr, exit 1).
5. `ledgerkit/parser.py`, offset 1247 limit 480 (remainder of the file) —
   subdirective consumption, `account`/`commodity`/`payee`/`tag`/
   `decimal-mark`/`P`/`alias`/`end aliases`/`Y`/`D`/`apply account`/
   posting-line branches, end-of-loop journal construction,
   `parse_string`/`parse_string_lenient` wrappers.
6. `ledgerkit/tags.py`, limit 90 — `parse_tags`'s grammar and the
   project's convention of grounding a parsing brief before implementing
   (precedent for how a `; report` grammar brief should be written).
7. `ledgerkit/__init__.py` (full) — confirm the public re-export surface;
   confirmed `ReportSpec`/`ReportSection`/`ReportSectionResult`/
   `balance_from_spec` are all already public, nothing new needs exporting
   except whatever new `Journal.report_specs` access pattern is chosen.
8. `ROADMAP.md`, offset 90 limit 190 — Milestone 2/3's "Deferred to..."
   lists, the Future/Backlog reclassification table (confirmed Stage D
   disposition), and the Stage A-I summary table (confirmed Stage D is
   `[PLANNED]`, not started).
9. `dev-docs/planning/core-redefinition/06-core-architecture.md` (full) —
   confirmed no Stage-D-specific detailed design exists yet; §6.3's
   "Report engine" row, §6.4's API-stability rules, §6.6's
   "every report function must be callable without the CLI" invariant.
10. `dev-docs/api-spec.md`, offset 360 limit 40 — the exact `ReportSpec`
    entry and its `[DEFERRED — Milestone 3]` note (verbatim text captured
    above).
11. `dev-docs/api-spec.md`, offset 845 limit 150 — `balance_from_spec`'s
    full documented signature/behavior, and confirmation that its "outer
    query converged" note refers only to the `Query` dataclass's own
    fields, not a `_query_ast` parameter (this is what surfaced open
    question §6.1).
12. `ledgerkit/parser.py`, offset 1247 limit 480 was read before I'd
    finished grepping — revisited implicitly via the same read; no
    duplicate read needed since the earlier read already covered it (see
    "Any duplicated work" below).
13. `dev-docs/planning/core-redefinition/06-core-architecture.md` grep hit
    then full read (see item 9).
14. `tests/test_parser/test_parser.py`, offset 741 limit 60 — read
    `TestCommentSpec`'s class docstring and a sample T-series test, to
    confirm the "three comment forms" taxonomy and the column-0 `;`/`#`
    "always top-level, never captured" invariant that a `; report` block
    must hook into rather than bypass.
15. `ledgerkit/checks.py`, limit 70 — `CheckError` dataclass shape and the
    basic/strict/other check-tier convention, to evaluate whether a
    malformed-report-spec diagnostic belongs here (concluded: no — it's a
    parse-time structural problem, not a semantic/validation one, so
    `ParseError`/`ParseWarning` is the right fit, not a new `CheckError`
    tier).
16. `dev-docs/architecture.md`, lines 1-40 — the pipeline diagram and
    module-responsibility principles ("reports don't print", "each module
    imports only from modules below it") cited in §2.

**Searches/greps performed, with query and purpose:**
1. `find . -type f -name "*.py" -not -path "./.git/*"` — full Python source
   inventory.
2. `find . -maxdepth 3 -type d -not -path "./.git*"` — directory layout
   (`dev-docs/`, `docs/`, `knowledge/`, `validation/`, `tests/`).
3. `grep -rn "ReportSpec\|ReportSection\|balance_from_spec\|report" --include="*.py" ledgerkit/ tests/`
   — the single most important search: enumerated every source/test
   reference to the feature's own types, confirming (a) `balance_from_spec`
   is the only consumer, (b) `cli.py` has zero `report`-command code,
   (c) all `tests/test_reports.py`/`tests/test_dataframe.py` coverage is
   downstream-of-parsing only.
4. `find dev-docs -maxdepth 2 -type f` and `find . -maxdepth 1 -type f` —
   doc/top-level-file inventory, located `ROADMAP.md`, `dev-docs/api-spec.md`,
   `dev-docs/architecture.md`, the `core-redefinition/` planning set.
5. `grep -n "Stage D\|report\|Report" ROADMAP.md` — located all three
   ROADMAP mentions of this feature (Milestone 2 deferral, Milestone 3
   deferral, Backlog reclassification table, Stage D summary row).
6. `grep -n "Stage D\|6\.1\|Reporting" dev-docs/planning/core-redefinition/06-core-architecture.md`
   — located §6.1 (the only hit), confirming no dedicated Stage D section
   exists in this file beyond the cross-stage architecture table already
   covered.
7. `find dev-docs/planning -type f` — confirmed no `dev-docs/planning/
   stage-d*.md` or similar phase-plan file exists anywhere (Stage D truly
   unstarted).
8. `grep -n "ReportSpec\|DEFERRED\|Milestone 3\|report" dev-docs/api-spec.md`
   — located every api-spec.md line touching this feature, including the
   `[DEFERRED — Milestone 3]` note and the `balance_from_spec` section
   references, to target the two full-section reads that followed.
9. `grep -rn "report" dev-docs/hledger-compatibility.md knowledge/` plus
   `find knowledge -type f` and `find validation -type f` — checked whether
   any hledger-compatibility note, domain rule, decision record, or
   validation finding already discusses `; report` comment syntax or any
   related prior art. Result: no hits beyond unrelated uses of the English
   word "report" (e.g. "report-display option", "reports it with file path
   and line number"). Confirmed no hidden prior design exists in
   `knowledge/` or `validation/`.
10. `grep -n "def merge_journals\|def load_journal" -A 40 ledgerkit/loader.py`
    — read `merge_journals`'s and `load_journal`'s full bodies; this is
    where the pre-existing `declared_account_tags`/`declared_commodity_tags`
    merge omission was discovered (§6.4).
11. `grep -n "^class\|^def \|CheckError\b" ledgerkit/checks.py` — surveyed
    `checks.py`'s structure before the targeted read above.
12. `git log --oneline -15` (inside `ledgerkit-baseline`) — confirmed the
    most recent commits are all Stage C closeout work (query-engine
    convergence, docs reconciliation), with nothing Stage-D or
    report-spec-related in recent history — Stage D genuinely hasn't been
    touched yet.
13. `python -m pytest tests/ -q` (via the provided venv python) — baseline
    full test-suite run: **906 passed, 29 skipped, 1 warning, 14 subtests
    passed**, confirming the repository is in a clean, fully-passing state
    before any design work, and establishing the exact baseline count a
    future implementation phase's new tests would be added on top of.
14. `grep -n "end comment\|in_block_comment\|class.*Comment" tests/test_parser/test_parser.py tests/test_directives/test_directives.py`
    — located `TestBlockComments`/`TestCommentSpec` and the
    directive-inside-`comment`-block tests, used as the structural/testing
    precedent in §4 and the nesting open question in §6.3.

**Files revisited more than once, and why:**
- `ledgerkit/parser.py`: read in two sequential chunks (offset 1, then
  offset 1247) purely because of the tool's single-read line/token cap on
  a 1722-line file — not a re-read of the same content, but flagged here
  since the system reminder explicitly warned the first read was partial
  and I want that transition to be traceable as "continuation," not
  "duplicate effort."
- `dev-docs/planning/core-redefinition/06-core-architecture.md`: first
  located via grep (confirming §6.1 was the only ROADMAP-cited anchor),
  then read in full — not a re-read, a grep-then-read sequence recorded
  separately above since the grep result by itself was insufficient to
  write §5 responsibly (it only confirms a heading exists, not what it
  says about Stage D's scope).
- `dev-docs/api-spec.md`: read in two non-overlapping offset windows
  (360-400 for the `ReportSpec` entry, 845-995 for the `reports.py`
  section including `balance_from_spec`) — both needed, no overlap, not a
  duplicate.

**Assumptions made, then corrected or confirmed by later evidence:**
- Initial assumption (before reading `cli.py`): that a `report` CLI command
  might already exist in skeletal/`NotImplementedError` form, analogous to
  how some report functions sometimes ship as stubs ahead of CLI wiring.
  Corrected immediately on reading `cli.py`'s `COMMANDS` tuple (line 23) —
  confirmed no `report` entry exists at all, skeletal or otherwise.
- Initial assumption (before reading `balance_from_spec`'s api-spec.md
  entry closely): that `balance_from_spec` had already been fully converged
  onto the `_query_ast`/`_query_depth` private-parameter pattern alongside
  `balance`/`register`/`accounts`/`stats` during Stage C Phase 8, since the
  entry's heading says "outer query converged — Stage C Phase 8." Reading
  the full `reports.py` source (its actual parameter list:
  `balance_from_spec(journal, spec, query=None)`, no `_query_ast`/
  `_query_depth`) and then the api-spec.md prose carefully (which
  specifically scopes the convergence to `query.account`/`.not_account`/
  `.payee`/date fields via `_query_to_ast`, not to a new private-parameter
  surface) corrected this — leading directly to open question §6.1, which
  I would have missed entirely had I trusted the section heading alone.
- Initial assumption (before reading `merge_journals`): that all of
  `Journal`'s declared-X list/dict fields were merged uniformly across
  included files. Reading `merge_journals`'s actual `Journal(...)` call
  corrected this — `declared_account_tags`/`declared_commodity_tags` are
  omitted, a real pre-existing gap now documented in §6.4/§1.

**Research that turned out to duplicate earlier work:**
- None identified. The one place duplication might have occurred (the
  two-part `parser.py` read) was a forced continuation due to the tool's
  size cap, not a redundant re-read of already-seen content, and is noted
  above for transparency rather than omitted.
