# Ledgerkit — Journal-Comment `ReportSpec` Parsing: Discovery & Design Treatment

Scope: discovery and design only, per instructions. No tracked file in the
Ledgerkit clone was modified. All reads stayed inside
`.../scratchpad/ledgerkit-treatment`, plus invocations of the CodeCompass
executable (never its own source).

---

## 1. Relevant existing source and how it currently relates

**`ledgerkit/models.py`**
- `ReportSpec` (frozen dataclass, line ~219): `name`, `sections: tuple[ReportSection,...]`,
  `show_subtotals=True`, `show_total=True`, `total_label="Net"`. Its docstring says
  verbatim: *"Journal-comment-based spec parsing (the '; report' / '; end report'
  syntax) is deferred to Milestone 3."* — this is now stale prose (ROADMAP.md has
  since reclassified the work to Stage D; CodeCompass's own indexed symbol digest for
  `ReportSpec` still echoes the old "Milestone 3" wording verbatim, confirming the
  docstring itself, not just the roadmap, needs a rewrite whenever this phase lands —
  see §5).
- `ReportSection` (frozen dataclass): `name`, `accounts: tuple[str,...]` (OR-matched),
  `exclude: tuple[str,...]=()`, `label: str|None=None`, `depth: int|None=None`,
  `invert: bool=False`.
- `ReportSectionResult` (mutable dataclass): `section`, `rows: dict[str, Decimal]`,
  `subtotal: Decimal`, plus a private `_commodity_styles` used only by its own
  `to_dataframe()`.
- `Journal` (dataclass): currently has no field for report specs at all —
  `declared_accounts`/`declared_commodities`/`declared_payees`/`declared_tags`/
  `declared_account_tags`/`declared_commodity_tags` are the only "declared-from-
  directives" containers. A comment-declared `ReportSpec` has nowhere to land today;
  a new field (e.g. `declared_report_specs: list[ReportSpec]`) would be additive,
  matching the project's own repeatedly-stated guardrail (`knowledge/DECISIONS.md`,
  2026-09-13 guardrail, reiterated in `dev-docs/planning/core-redefinition/
  16-model-review.md`): never change an existing declared-* field's shape, only add
  new ones alongside it.
- `Query` is a separate, unrelated filter dataclass — "which transactions/postings to
  include"; `ReportSpec` answers "how to lay out what's included." The module's own
  comment block (lines ~183-195) states this separation explicitly and that "Neither
  knows about the other" — a design invariant any comment-grammar work must preserve.

**`ledgerkit/reports.py`**
- `balance_from_spec(journal, spec, query=None) -> list[ReportSectionResult]` (line 600)
  is the only consumer of `ReportSpec`/`ReportSection` today. It is a pure function:
  given an already-constructed `ReportSpec` object, it walks `journal.transactions`,
  applies the outer `Query`/AST filter via the Stage C Phase 8 canonical engine, then
  applies each section's own `accounts`/`exclude` patterns via the private
  `_matches_pattern` helper (the one construct deliberately NOT converged onto
  `ledgerkit.query.eval` — see `dev-docs/architecture.md` and `api-spec.md`'s own
  `balance_from_spec` entry). It has **no knowledge of where a `ReportSpec` came
  from** — a comment-parsed spec and a hand-built one are indistinguishable to it.
  This means the comment-grammar work is purely a **producer**-side change
  (parser → `Journal` → caller-assembled `ReportSpec`); `balance_from_spec` itself
  needs no change to support it.
- `Journal.commodity_styles` is read by `balance_from_spec` for `ReportSectionResult`'s
  `to_dataframe()` but plays no role in spec *parsing*.

**`ledgerkit/parser.py`** (1721 lines) — the file that must do essentially all of the
new work:
- Column-0, non-indented `;`/`#` lines are **unconditionally and silently discarded**
  today (the "Comment-only line" branch, parser.py lines ~1045-1109). This is
  confirmed both by the inline documentation block directly above that code and by a
  dedicated test class, `TestCommentSpec` (`tests/test_parser/test_parser.py`,
  T-series tests at lines ~756-830), which explicitly asserts that a column-0 `;`/`#`
  comment line is swallowed and contributes to **no** model field anywhere.
  **This is the key architectural fact for this feature**: because the proposed
  syntax is `; report` / `; end report` (both are ordinary `;`-prefixed top-level
  comment lines), they are *already being matched and discarded* by this exact
  branch, before the parser ever reaches the later special-case directives (`~`,
  `=`, `comment`/`end comment`, transaction headers). A real implementation must
  intercept these two forms **inside or ahead of** that comment-only-line branch —
  it cannot be bolted on afterward the way `~`/`=`/`comment` are, because those three
  are *not* `;`/`#`-prefixed and so fall through to later, separate branches.
- The existing `comment` / `end comment` **block-comment directive** is the closest
  structural precedent, but it is a different grammar family: `comment` is a bare,
  non-`;`-prefixed keyword at column 0 (matched at parser.py line 1222,
  `line.split()[0] == "comment"`), entered via `in_block_comment = True`, and consumes
  every line verbatim until `end comment` (or EOF) with **zero content extraction** —
  it is pure skip, by design (see the inline doc block at lines ~990-1007: a `comment`
  block that never closes "is silently accepted" and the parser "simply consumes the
  rest of the file"). `; report` / `; end report`, by contrast, must both (a) stay
  inside `;`-led top-level-comment territory, syntactically, and (b) actually extract
  structured content (section definitions) from the lines in between, not discard it —
  so the `comment`/`end comment` state-machine pattern (an `in_block_X: bool` flag
  threaded through the main loop, matched before the blank-line/transaction-header
  checks) is reusable as *scaffolding*, but its "skip and discard" body is not.
- `ParseError`/`ParseWarning` (parser.py, both re-exported) are the two error types
  already in play for malformed-but-recoverable input. `parse_string_lenient`'s
  `errors_out` accumulation pattern — hard `ParseError` vs. non-fatal `ParseWarning`,
  distinguished via `isinstance` — is the established mechanism for "this construct is
  present but broken": the `~`/`=`/nested-`apply account` precedent (parser.py
  ~1111-1168) appends a `ParseWarning` and skips the block without halting the parse,
  exactly the behaviour a malformed `; report` block should plausibly follow (see §7).
- `ledgerkit/tags.py`'s `parse_tags(comment)` is the other close structural precedent
  for "a small inline grammar embedded in comment text": name:value pairs,
  comma-terminated values, no escaping, "a space before the colon voids the candidate
  tag entirely." It demonstrates the project's established tolerance for a
  deliberately minimal, non-escaping grammar for comment-embedded data — a useful
  precedent for how permissive/strict a report-spec mini-grammar should be (§7).

**`ledgerkit/cli.py`**
- `COMMANDS = ("balance", "register", "accounts", "print", "stats", "check")` — **there
  is no `report` command today**, and `balance_from_spec` is not wired into the CLI at
  all; it is Python-API-only (confirmed directly in source and independently by
  `codecompass query source ledgerkit/cli.py`, whose full symbol list contains only
  `_fmt_amount`, `_fmt_balance`, `_abbreviate_account`, `_build_parser`,
  `_resolve_files`, `main` — no report-spec-aware code path of any kind).
  This means a comment-declared `ReportSpec` currently has **no CLI execution path at
  all**, even once parsed and stored on `Journal` — a new CLI command (most likely
  `report [NAME]`, see §3/§6) is a second, separate piece of required scope beyond
  parser changes, not implied by "parsing support" alone.
- `-q`/`--query` (`query_text` → `ledgerkit.query.parse` → `QueryPlan.predicate`/
  `.depth`) is wired to `balance`/`register`/`accounts`/`stats`/`print`, never to
  `balance_from_spec` — composing the CLI's `-q` flag with a future `report` command
  is therefore an open design question, not an existing wiring to preserve (§6).

---

## 2. Producer/consumer relationships a real implementation must respect or extend

```
 journal text (; report / ; end report lines)
        │
        ▼
 ledgerkit/parser.py  (producer — NEW responsibility)
   - must special-case ';'-prefixed "report"/"end report" top-level lines
     INSIDE the existing comment-only-line branch, before it unconditionally
     discards them
   - extracts structured section data from the lines between the markers
   - on success: builds a ReportSpec, appends it somewhere reachable
   - on malformure: ParseError (strict) / ParseWarning + skip (lenient) —
     mirroring the ~ / = / apply-account precedent
        │
        ▼
 ledgerkit/models.py  (NEW storage — Journal gains a field)
   - e.g. Journal.declared_report_specs: list[ReportSpec] = field(default_factory=list)
   - additive only; declared_accounts/commodities/payees/tags untouched
        │
        ▼
 ledgerkit/reports.py  (EXISTING consumer — unchanged)
   - balance_from_spec(journal, spec, query=None) already accepts any ReportSpec,
     comment-sourced or hand-built, with zero awareness of provenance
        │
        ▼
 ledgerkit/cli.py  (NEW consumer — does not exist yet)
   - no "report" command exists; must be added to look up a spec (by name?
     by position? — open question, §6) from journal.declared_report_specs
     and call balance_from_spec, then format ReportSectionResult list for
     terminal output (cli.py has zero existing formatting code for this
     shape — balance/register formatting code is not reusable as-is since
     ReportSectionResult's rows are single-commodity, unlike balance()'s
     dict[str, dict[str, Decimal]])
```

Relationships that must NOT be disturbed (frozen/stable-API constraints found in
`dev-docs/api-spec.md` and `dev-docs/planning/core-redefinition/06-core-architecture.md`
§6.5):
- `ReportSpec`/`ReportSection` are **frozen** dataclasses already in the stable v1
  surface (re-exported from `ledgerkit/__init__.py`); the comment-parsing work should
  *produce* instances of the existing shape, not redesign the dataclasses themselves,
  unless a genuine gap is found (e.g. `ReportSection.label`/`.depth`/`.invert` all need
  a textual representation in the comment grammar — see §7's grammar proposal).
- `balance_from_spec`'s signature and behaviour are explicitly called out in
  `api-spec.md` as `[IMPLEMENTED — Milestone 2; outer query converged — Stage C Phase 8]`
  — no indication anywhere that this phase should touch it.
- The parser's "each module imports only from modules below it" rule
  (`dev-docs/architecture.md`, restated in `06-core-architecture.md` §6.1) means
  `parser.py` must not import `reports.py` to build a `ReportSpec` — it already
  imports `models.py` (where `ReportSpec`/`ReportSection` live), so this is naturally
  satisfied by building `ReportSpec`/`ReportSection` objects directly from
  `models.py`, exactly as it already does for `Transaction`/`Posting`/`PriceDirective`.

---

## 3. Execution path a comment-declared report must follow end-to-end

1. **Load**: `ledgerkit.load()` / `loader.load_journal()` / `parser.parse_string()` /
   `parser.parse_string_lenient()` read the journal text line-by-line (parser.py's
   main loop, `_parse_string_impl`).
2. **Detection** (NEW): when a non-indented line's stripped-of-`;` content begins with
   `report` (case? — open question, §6), the parser must recognise this *before*
   falling into the existing "Comment-only line… ALWAYS silently skipped" branch
   (parser.py ~1069-1109). This is the single most load-bearing structural fact
   uncovered: today that branch runs unconditionally for every `;`/`#`-led line
   regardless of transaction-open state, so a naive implementation that adds the
   `; report` check *after* this branch (the way `comment`/`~`/`=` are added after it)
   would never be reached — those three are matched specifically because they are
   **not** `;`/`#`-prefixed.
3. **Block accumulation**: lines between `; report ...` and `; end report` are
   consumed in a new parser state (`in_report_block: bool`, following the
   `in_block_comment` precedent's shape) and parsed into section definitions per
   whatever grammar is approved (§7) — most plausibly one `; section ...` line per
   `ReportSection`, by analogy with how `account`/`commodity` directives' own
   follow-on `;`-led lines are tag-scanned today (parser.py's
   `account_comment_target`/`commodity_comment_target` mechanism is a structural
   precedent for "accumulate structured data from a sequence of comment lines tied
   to one opening directive").
4. **Materialise**: on a well-formed block, build one `ReportSpec(name=..., sections=
   tuple(...), ...)` and append it to `journal.declared_report_specs` (new field).
   On a malformed block: raise `ParseError` in strict mode (`parse_string`), or append
   a `ParseWarning`-category error and skip the rest of the block in lenient mode
   (`parse_string_lenient`), mirroring the `~`/`=`/`apply account` nested-directive
   precedent exactly (`ParseWarning` subclasses `ParseError`; `errors_out` collects it;
   the surrounding journal content is otherwise preserved).
5. **Consume via `reports.balance_from_spec`**: no change needed — it already accepts
   any `ReportSpec` value. A caller (CLI or library user) picks one of
   `journal.declared_report_specs` (by name, by index — open question, §6) and passes
   it, plus an optional `Query`, to `balance_from_spec(journal, spec, query=...)`.
6. **CLI surfacing** (NEW, does not exist today): `cli.py` needs (a) a new `report`
   entry in `COMMANDS`, (b) argument handling for selecting which declared spec to run
   when a journal declares more than one, (c) new output-formatting code for
   `list[ReportSectionResult]` (nothing in `cli.py` today formats this shape — the
   `balance` command's formatter is built around `dict[str, dict[str, Decimal]]`,
   not `ReportSectionResult.rows: dict[str, Decimal]` with a per-section subtotal and
   `show_subtotals`/`show_total`/`total_label` from the spec itself, which currently
   has no consumer anywhere that renders them — `balance_from_spec`'s own docstring
   and `ReportSectionResult` never mention subtotal/total *display*, only computation;
   `show_subtotals`/`show_total`/`total_label` are read by nothing in `reports.py`
   today, a latent gap this CLI work would be the first to actually exercise).

---

## 4. Existing test coverage: adjacent vs. net-new

**Adjacent (would inform/need-to-keep-passing, but don't exercise the new behaviour):**
- `tests/test_parser/test_parser.py::TestBlockComments` (lines ~238-310) — the
  `comment`/`end comment` state-machine precedent; a new `in_report_block` state must
  not interact badly with `in_block_comment` (e.g. a `; report` line *inside* an open
  `comment` block must stay inert, per the existing "lines inside a block comment are
  not parsed" guarantee — tests at ~912-933 assert exactly this for other directive-
  looking content, so an equivalent assertion for `; report` would be a natural
  extension, not fully new).
- `tests/test_parser/test_parser.py::TestCommentSpec` (lines ~741-1080, the T-/F-/I-
  series) — directly documents and tests the "column-0 `;`/`#` is always silently
  skipped" behaviour this feature must carve an exception into. Several of these
  tests (e.g. `test_T02`/`test_T04`-equivalent column-0-comment assertions) encode the
  *current* behaviour that a correct implementation must deliberately diverge from
  for lines starting with `; report`/`; end report` specifically, while leaving every
  *other* column-0 `;` comment's current behaviour unchanged — any new test suite
  should include a regression test that an ordinary `; some unrelated comment` line
  is still silently skipped exactly as before.
- `tests/test_reports.py::TestReportSpecDataclasses` (lines 642-686) and
  `TestBalanceFromSpec`/`TestBalanceFromSpecOuterQueryConvergence`/
  `TestReportSectionHledgerRegexValidation` (lines 692-980+) — exercise
  `ReportSpec`/`ReportSection`/`balance_from_spec` thoroughly, but only ever via
  programmatic construction (`ledgerkit.ReportSpec(...)` literals in every test). None
  of these touch parsing from text at all — confirming the "producer" side (parser →
  model) has **zero** existing test coverage and is purely net-new.
- `tests/test_cli/test_cli.py` — `TestQueryFlag`/`TestTagQueryFlag` (lines 340-557+)
  are the closest precedent for "CLI flag parses something and routes it to a report
  function," but there is no `TestReportCommand`-equivalent class, and `COMMANDS`
  itself is never asserted against by name in any test I found (`grep` for
  `COMMANDS`/`"report"` inside `test_cli.py` returned nothing) — so adding a `report`
  command subcommand does not risk breaking an existing literal-tuple assertion, but
  also receives zero existing protection against regressions.

**Net-new (no existing coverage at all):**
- Parsing `; report` / `; end report` from text — zero tests exist today (confirmed by
  grep across `tests/` for `end report`/`; report`: no hits anywhere in the test
  suite or fixtures).
- `Journal.declared_report_specs` (or whatever the chosen field name is) — does not
  exist, so no test references it.
- Malformed-block handling (unterminated `; report`, unknown directive inside the
  block, duplicate section names, bad `depth=`/`invert=` tokens, an *empty* `; report`
  / `; end report` pair with zero sections — the CLAUDE.md §1 fail-closed-mechanism
  edge case explicitly required for this project's own DoD) — zero coverage.
- A CLI `report` command and its output formatting — zero coverage (command does not
  exist).
- Interaction with `parse_string_lenient`'s `errors_out` (does a malformed report
  block produce a `ParseWarning`, consistent with the `~`/`=` precedent, or a hard
  `ParseError`? — currently undecided, see §6) — zero coverage either way.
- Interaction between a comment-declared spec and the CLI's `-q`/`--query` flag
  (§6) — zero coverage, since no such composition point exists yet.

---

## 5. Relevant docs

- `dev-docs/api-spec.md` — `ReportSpec`'s own entry (line ~366) carries the literal
  `[DEFERRED — Milestone 3]` note quoted in the task; this is the most load-bearing
  doc reference and is stale relative to `ROADMAP.md`'s reclassification.
- `ROADMAP.md` — two separate places: the Milestone 2 "Deferred to Milestone 3" list
  (line 126), the Milestone 3 "Deferred to future milestones" list (line 165), and the
  "Future / Backlog — reclassified into Stages" table (line 263): *"Journal-comment
  `ReportSpec` parsing | `[BACKLOG]` | Stage D (Reporting)"*. Stage D itself (line 286)
  is `[PLANNED]`, pointing to `core-redefinition/06-core-architecture.md` §6.1, which
  — read in full — says only that the report engine should "consume `query/` instead
  of the `Query` dataclass directly" (a different, already-in-flight concern: routing
  `balance_from_spec`'s outer filter through the query AST, not the comment-grammar
  feature) and does **not** contain any grammar/design detail for `; report` parsing
  itself. `dev-docs/planning/core-redefinition/12-roadmap-migration.md` (line 34) adds
  one line of colour: *"natural fit once the report engine consolidation happens; not
  blocking Stage D's exit"* — i.e. this feature is explicitly **not** a hard
  prerequisite for closing Stage D, just a natural companion to it.
- `docs/python-api.md` (lines 180-238) — the only other place the feature is
  mentioned; its "Custom Report Layouts with ReportSpec" section ends with: *"Report
  specs are currently constructed programmatically. Journal-file comment-directive
  syntax (`; report` / `; end report`) is on the roadmap but not yet supported."* No
  grammar detail here either.
- `dev-docs/architecture.md` — the "reports don't print" / module-layering
  description; relevant as a constraint (§2 above), not as design detail for this
  feature.
- No design brief exists anywhere under `dev-docs/planning/core-redefinition/` (the
  numbered-brief pattern used for every other Stage C/D-adjacent feature — query
  regex, tag matching, depth semantics, etc. — has no counterpart numbered `.md` for
  report-spec comment parsing). This is itself a notable finding: every other
  comparably-sized parsing feature in this project's recent history was preceded by a
  dedicated design brief before implementation; this one currently has none.

---

## 6. Open design questions / uncertainties (could not resolve with confidence)

1. **Is this even a real hledger feature, or a Ledgerkit invention?** I found no
   evidence anywhere in this repository (`dev-docs/hledger-compatibility.md`, the
   compat register under `dev-docs/compat-register/`, or any planning doc) that real
   hledger has a `; report` / `; end report` journal-comment directive. Every other
   deferred/planned parser feature in this codebase traces to a genuine hledger
   construct (periodic rules, auto-postings, lot annotations, etc.), each with its own
   `dev-docs/hledger-compatibility.md` row and/or compat-register entry. This one has
   neither. My reading is that this is a **Ledgerkit-native convenience syntax**
   layered on top of `;`-comments specifically because hledger's own comment syntax
   gives a natural, already-ignored-by-real-hledger place to embed Ledgerkit-specific
   metadata (similar in spirit to how some tools embed config in comments) — but I
   could not confirm this intent from any document, and it changes the compatibility
   posture significantly: if so, it should probably get an `LK-UNSUP-*` or new
   `LK-EXT-*`-style compat-register entry (see `dev-docs/compat-register/schema.md`'s
   categories) rather than being treated as "implementing a deferred hledger feature."
   **This should be confirmed with the user/lead before design work proceeds.**
2. **Exact grammar is completely unspecified.** Neither `ROADMAP.md` nor
   `api-spec.md` nor `docs/python-api.md` gives anything beyond the two marker
   strings. Every field on `ReportSection` (`accounts`, `exclude`, `label`, `depth`,
   `invert`) and `ReportSpec` (`show_subtotals`, `show_total`, `total_label`) needs a
   textual representation decided from scratch. §7 proposes one, but it is a proposal,
   not a recovered intent.
3. **CLI composition with `-q`/`--query`**: `balance_from_spec` already accepts an
   outer `query: Query | None` applied uniformly across all sections. Once a `report`
   CLI command exists, should `-q`/`--query` on the command line compose with (AND
   into) that outer query, exactly as it does today for `balance`/`register`/
   `accounts`/`stats`? That seems the natural, consistent answer, but note
   `balance_from_spec` takes a legacy `Query`, not a `QueryNode`/`_query_ast` — it was
   explicitly *not* included in Stage C Phase 8's full convergence onto
   `ledgerkit.query.compat._query_to_ast` for section-level matching (only the outer
   query was converged — `api-spec.md`'s `balance_from_spec` entry is explicit that
   `ReportSection.accounts`/`.exclude` remain on `_matches_pattern`, "the one construct
   with no `Query` equivalent, deliberately kept separate"). So wiring `-q` into a new
   `report` command means either (a) converting the CLI's parsed `QueryPlan.predicate`
   into a legacy `Query` for the outer filter (lossy/awkward — `QueryNode`s like
   `Tag`/`Status`/arbitrary `And`/`Or`/`Not` trees have no `Query` representation), or
   (b) extending `balance_from_spec`'s outer-query parameter to accept a `QueryNode`
   directly alongside/instead of `Query` (a bigger, Stage-C-flavoured change this
   phase's plan would need to scope explicitly). **I could not determine which of
   these the project intends; the CLAUDE.md-mandated plan file for this phase should
   settle it before implementation**, per the task's own framing of this as an
   explicit open question.
4. **Selecting which declared spec to run.** A journal could plausibly declare more
   than one `; report ... ; end report` block (e.g. "Income Statement" and "Net
   Worth"). Is the new CLI command `report NAME` (positional spec name, parallel to
   `check [CHECK...]`'s positional check names), or does it run all declared specs in
   sequence, or only the first? Nothing in any doc addresses this.
5. **Multiple specs with the same name; duplicate/missing name handling.** Should two
   `; report Foo` blocks with the same name be a `ParseError`, silently both stored
   (ambiguous lookup later), or last/first-wins? No precedent in the comment-tag
   system (`declared_account_tags` *merges* same-key entries across multiple
   directives) directly answers this, since a `ReportSpec` is a whole structured
   object, not an accumulating tag list.
6. **Strict vs. lenient malformed-block handling.** Does a malformed `; report` block
   raise `ParseError` immediately in `parse_string` (strict), the way a bad `date:`/
   `date2:` tag value does (per `api-spec.md`'s `Posting.date_override` entry), or does
   it degrade to a `ParseWarning` + skip, the way `~`/`=`/nested `apply account` do?
   Both precedents exist in this codebase for different kinds of "recognised but
   unsupported/malformed construct," and the task's own CLAUDE.md §1 fail-closed
   verification requirement (amendments on L-070/L-075) means this choice has real
   consequences for how thoroughly the eventual test suite must probe the minimal/
   empty-but-well-formed edge case (an `; report X` / `; end report` pair with zero
   section lines between them — technically well-formed markers, zero content).
7. **Case-sensitivity and whitespace tolerance of the markers themselves** (`; report`
   vs `;report` vs `; Report`; `; end report` vs `;end report`) — no existing
   precedent directly answers this; `comment`/`end comment` are matched via
   `line.split()[0] == "comment"` (exact, case-sensitive, first-token match) and
   `line.strip() == "end comment"` (exact, case-sensitive, whole-line match after
   stripping) respectively — different precision levels for the open vs. close
   marker, interestingly. A `; report` analogue would need its own explicit decision,
   not an inherited one.
8. **Does a comment-declared spec interact with `EditorDocument`/`writer.py` at all?**
   (E.g., does `journal_to_text`/`transaction_to_text` need to re-serialise declared
   report specs on save?) `dev-docs/api-spec.md`'s `journal_to_text` entry already
   states directives are *not* serialised in v1 ("Directives (account, commodity,
   payee, P) are not serialised in v1") — by extension a report-spec block would
   presumably fall under the same non-serialisation rule, but this was not stated
   anywhere explicitly for this specific construct, and `EditorDocument`'s own
   `update_transaction`/`save` methods operate on `self.lines` (raw text), so a
   comment-declared block would likely survive editor round-trips automatically
   (it's literal text, not a parsed-and-regenerated directive) — this seems low-risk
   but is inferred, not confirmed by any doc.

---

## 7. Proposed design (for discussion — not implemented)

**Framing**: given finding §6.1 (likely a Ledgerkit-native convenience, not a real
hledger construct) and the complete absence of a grammar anywhere, I propose the
following as a *starting* design, explicitly provisional pending the plan-file
process CLAUDE.md §1 already mandates for this repository.

### 7.1 Grammar

```
report-block    ::= report-open section-line* report-close
report-open     ::= ";" WS* "report" WS+ name WS* EOL
report-close    ::= ";" WS* "end" WS+ "report" WS* EOL
name            ::= <rest of report-open line, trimmed>
section-line    ::= ";" WS* "section" WS+ section-name WS+ attr-pair* EOL
attr-pair       ::= key "=" value   (space-separated; no embedded spaces in value,
                                     matching the existing HledgerRegex-dialect
                                     patterns already used elsewhere, which also
                                     never need embedded-space tolerance)
key             ::= "accounts" | "exclude" | "label" | "depth" | "invert"
```

Example:
```
; report Income Statement
; section Income accounts=income invert=true
; section Expenses accounts=expenses exclude=expenses:transfers
; end report
```

- `accounts=`/`exclude=` accept a single pattern per `attr-pair`, repeatable
  (`accounts=income accounts=investments` → OR-combined, matching
  `ReportSection.accounts`'s existing OR-tuple shape) — avoids inventing a
  comma/pipe-separated sub-syntax inside one value, consistent with `tags.py`'s own
  precedent of deliberately avoiding escaping rules for comment-embedded grammars.
- `depth=N` → `ReportSection.depth`; `invert=true`/`invert=false` → `ReportSection
  .invert` (absent = `False`, matching the dataclass default).
- `label=` → `ReportSection.label` (absent = `None`, so `balance_from_spec`'s/
  CLI's own `f"Total {name}"` default fallback — once that fallback is actually
  implemented somewhere; today nothing computes it, see §3's final bullet).
- Top-level `ReportSpec.show_subtotals`/`.show_total`/`.total_label` would need their
  own optional `; report NAME show_total=false total_label=...` attributes on the
  `report-open` line itself, by the same `key=value` convention.
- Markers matched case-sensitively, first-token-after-`;` exact match (`report`/`end
  report`), mirroring `comment`'s own precision level, trimming only leading/trailing
  whitespace — resolves open question §6.7 as a concrete default, not a confirmed
  decision.

### 7.2 How a malformed spec block is reported

- **Unterminated block** (`; report X` with no matching `; end report` before EOF or
  before another `; report` opens): mirrors the `comment`/`end comment` precedent’s
  "silently accepted, consumes the rest" behaviour for *block-comment* bodies — but
  since a report block's content is meaningful (not discarded), I propose this
  specific case be a **hard `ParseError`** in strict mode (`parse_string`) and a
  `ParseWarning` + spec dropped in lenient mode (`parse_string_lenient`), rather than
  silently swallowing the rest of the file the way `comment` does — silently
  discarding an unknown amount of subsequent journal content (transactions!) because
  a report block never closed would be a much more dangerous failure mode than
  "report metadata is incomplete," since it directly risks hiding real transactions
  from every other report.
- **Unrecognised line inside an open block** (anything other than `; section ...` or
  `; end report`): `ParseError`/`ParseWarning` (strict/lenient, respectively),
  naming the offending line number — consistent with `CheckError.line_number`'s
  established "always populate when a single clear source line exists" convention.
- **Bad attribute value** (`depth=abc`, unknown `key=`, `invert=maybe`): same
  strict/lenient split, at the specific line.
- **The fail-closed minimal-edge case CLAUDE.md §1 requires explicit coverage
  for**: `; report X` immediately followed by `; end report` with **zero**
  `section-line`s in between. This is syntactically well-formed per the grammar
  above (a `ReportSpec` with `sections=()` is a legal, already-tested value —
  `TestBalanceFromSpec` has `test_empty_section_has_zero_subtotal`, though that's an
  empty *section*, not an empty *spec*; no existing test constructs
  `ReportSpec(sections=())`). The open design question is whether the parser should
  (a) accept this and store a zero-section `ReportSpec` (consistent with "well-formed
  but vacuous" being accepted elsewhere, e.g. `Query()`'s all-`None` "no filter"
  convention), or (b) treat zero sections as itself a `ParseError`/`ParseWarning`
  (since a reportable spec with no sections can never produce useful output). I lean
  towards (a) for consistency with the rest of the codebase's "empty-but-well-formed
  is accepted, not rejected" pattern (e.g., `Query()`, `And(())` matching everything in
  `ledgerkit/query/parser.py`'s `parse("")` docstring) — but explicitly flag this as
  the required "minimal-content edge case" test CLAUDE.md §1's fifth/sixth amendments
  mandate verifying either way, whichever the plan ultimately decides.

### 7.3 How the parsed `ReportSpec` reaches a report

1. Parser builds a `ReportSpec` per well-formed block and appends it to a new
   `Journal.declared_report_specs: list[ReportSpec]` field (additive, matching every
   other `declared_*` field's own precedent of being a flat accumulation in source
   order, with same-name duplicates simply both present — resolving open question §6.5
   towards "both stored, lookup-time ambiguity is the caller's problem," the same
   posture `declared_accounts`/`declared_payees` already take for duplicate
   declarations).
2. `reports.py` needs **no change** — `balance_from_spec(journal, spec, query=...)`
   already accepts any `ReportSpec` instance regardless of provenance.
3. A new `report` CLI command (added to `cli.py`'s `COMMANDS` tuple) resolves a name
   argument against `journal.declared_report_specs` (by `.name`, first match), calls
   `reports.balance_from_spec(journal, spec, query=<composed Query/QueryNode, per
   open question §6.3>)`, and formats the returned `list[ReportSectionResult]` —
   this formatter is itself net-new code (no existing `cli.py` formatter handles this
   shape, per §3's final bullet) and should actually honour `spec.show_subtotals`/
   `.show_total`/`.total_label`, which no code anywhere currently reads.
4. Programmatic (non-CLI) consumers get this "for free" the moment
   `Journal.declared_report_specs` exists — `ledgerkit.load(path).declared_report_specs`
   plus `ledgerkit.balance_from_spec(journal, journal.declared_report_specs[0])` works
   with no further wiring, matching the "every report function must be callable and
   useful from pure Python without going through cli.py" invariant
   `core-redefinition/06-core-architecture.md` §6.6 states explicitly for this exact
   kind of feature.

---

## Research trace

**Files read (in order), each read in full unless noted:**
1. `/…/ledgerkit-treatment` — `find . -type f -not -path './.git/*'` (full repo file
   listing; not a file read, listed here as the first discovery action).
2. `dev-docs/api-spec.md` (full file, 1430 lines) — primary source for all
   `[IMPLEMENTED]`/`[DEFERRED]`/`[STUB]` status markers, `ReportSpec`/`ReportSection`/
   `ReportSectionResult`/`balance_from_spec` signatures, CLI command table (confirming
   no `report` command documented either).
3. `ROADMAP.md` (full file, 315 lines) — Milestone 2/3 deferred-items lists, the
   "Future / Backlog — reclassified into Stages" table, Stage D row, "Deciding What
   Goes Into a Milestone or Stage" process section.
4. `ledgerkit/models.py` (full file, 535 lines) — `ReportSpec`, `ReportSection`,
   `ReportSectionResult`, `Journal` (all `declared_*` fields), `Query`.
5. `ledgerkit/reports.py` (full file, 697 lines) — `balance_from_spec`,
   `_matches_pattern`, the Stage C Phase 8 convergence comments explaining why
   `ReportSection.accounts`/`.exclude` stayed on the old matcher.
6. `dev-docs/planning/core-redefinition/06-core-architecture.md` (full file,
   165 lines) — Stage D's own linked plan source; confirmed it contains no
   report-comment-grammar detail, only the general "reports.py extend to consume
   query/" note (a different, already-separately-scoped concern).
7. `docs/python-api.md`, lines 160-250 (targeted read via offset/limit) — the
   user-facing "Custom Report Layouts with ReportSpec" section and its own
   "on the roadmap but not yet supported" note.
8. `ledgerkit/parser.py`, lines 955-1240 (targeted reads via two offset/limit calls:
   955-1185 and 1195-1240) — the full main parse loop's comment/block-comment/
   periodic-rule/auto-posting-rule/transaction-header branches, in exact execution
   order. This was the single most important read for the whole investigation: it
   established that column-0 `;`/`#` lines are matched and discarded *before* the
   `comment`/`~`/`=`/transaction-header branches are ever reached.
9. `dev-docs/architecture.md`, `dev-docs/hledger-compatibility.md`,
   `knowledge/*.md` — targeted via grep only (see below), not full reads; relevant
   matched lines inspected in grep output context.
10. `tests/test_reports.py`, lines 642-731 (targeted read) — `TestReportSpecDataclasses`
    and the start of `TestBalanceFromSpec`, confirming all existing `ReportSpec` tests
    construct specs programmatically, never from text.
11. `ledgerkit/cli.py` (full file, 509 lines) — `COMMANDS` tuple, `_build_parser`,
    `main`'s full command dispatch (`balance`/`register`/`accounts`/`print`/`stats`/
    `check`), confirming no `report` command and no `ReportSectionResult` formatter
    exist anywhere.
12. `ledgerkit/query/parser.py`, lines 1-40 (targeted read) — `QueryParseError`/
    `parse()`'s own docstring, as the closest existing precedent for how a
    comment/query mini-grammar documents its own combination/error semantics.

**Files revisited more than once, and why:**
- None required a second full read. `ledgerkit/parser.py` was read via two
  *different, non-overlapping* offset ranges (955-1185, then 1195-1240) to see the
  full main loop in order — not a revisit of the same content, but noted here since
  it's the same file touched twice.

**Searches/greps performed (query → purpose):**
- `grep -n "comment" ledgerkit/parser.py` → locate every comment-handling code
  region before reading any of them in full; this is what directed the two targeted
  `Read` calls at offsets 955 and 1195.
- `grep -n "6.1\|Stage D\|report" dev-docs/planning/core-redefinition/
  06-core-architecture.md` → confirm whether Stage D's linked plan doc contains
  report-comment-grammar detail (it does not).
- `grep -rn "end report\|; report\|report.*comment\|comment.*report\|ReportSpec"
  --include=*.md . | grep -v compat-register` → sweep every Markdown doc in the repo
  for any mention of the feature or its grammar, beyond the two files already
  identified; surfaced every doc reference used in §5, and confirmed (by absence) that
  no numbered `core-redefinition/*.md` design brief exists for this feature, unlike
  every comparable Stage C feature.
- `grep -n "in_block_comment = True\|== \"comment\"\|startswith(\"comment\")"
  ledgerkit/parser.py` → find the exact line where the `comment` directive is
  recognised, to read its surrounding context precisely (led to the offset-1195 read).
- `grep -rn "report" knowledge/*.md dev-docs/architecture.md
  dev-docs/hledger-compatibility.md` → check whether the project's own domain-rules/
  decisions/edge-cases knowledge files record any prior reasoning about this feature
  (they do not — all hits were unrelated uses of the word "report", e.g. Pylance's
  `reportOptionalMemberAccess`, `CheckError`'s "reports it", etc.).
- `grep -n "COMMANDS\|report" tests/test_cli/test_cli.py` → check whether any test
  references a `report` CLI command or asserts the exact `COMMANDS` tuple contents
  (neither exists — confirmed net-new, §4).
- `grep -n "^class Test\|def test_" tests/test_reports.py | grep -i "spec\|section"`
  → enumerate every existing `ReportSpec`/`ReportSection`/`balance_from_spec` test
  class/method name, for the coverage inventory in §4.
- `grep -n "class Test\|comment\b" tests/test_parser/test_parser.py | grep -i
  "comment\|block"` → enumerate every comment/block-comment-related test class, for
  the same §4 inventory (found `TestComments`, `TestBlockComments`, `TestCommentSpec`).
- `grep -n "^class" tests/test_cli/test_cli.py` → full list of CLI test classes,
  confirming no `TestReportCommand`-equivalent exists.
- `grep -n "COMMANDS\|choices=COMMANDS\|unimplemented\|not yet implemented"
  tests/test_cli/test_cli.py` → double-check for any indirect `report`-command
  reference (none found).

**CodeCompass queries invoked, verbatim output (abridged only where noted — full
docstring bodies that duplicate text already quoted in §1 are shown in full below
since the task requires verbatim capture):**

1. `codecompass query source ledgerkit/reports.py`
   → returned full symbol index (`BalanceResult`, `RegisterResult`, `AccountsResult`,
   `JournalStats`, `_matches_pattern`, `_effective_depth_spec`,
   `_aggregate_posting_amounts`, `_build_balance_tree`, `accounts`, `balance`,
   `register`, `stats`, `balance_from_spec`), each with its full docstring, content
   hash, and "indexed (full parse)" status. Full text matched what direct file-reading
   already showed — no new facts, but confirmed the index is current (content hash
   consistent with the file I'd just read) and that `balance_from_spec` is the only
   ReportSpec-shaped symbol CodeCompass tracks in this file.

2. `codecompass query source-symbol ReportSpec`
   → one row: `ledgerkit/models.py`, class, line 219, public, purpose text ending in
   *"Journal-comment-based spec parsing (the '; report' / '; end report' syntax) is
   deferred to Milestone 3."* — this is the discovery noted in §1 that CodeCompass's
   own indexed digest still echoes the stale "Milestone 3" wording verbatim (matching
   the live docstring exactly, i.e. CodeCompass is accurately reflecting current
   source, which is itself what's stale relative to `ROADMAP.md`).

3. `codecompass query relations ReportSpec`
   → `error: 'ReportSpec' not found in context-graph.db` (exit 1). Expected once I
   read `query relations --help`'s full description (see entry 6 below): `relations`
   only resolves spec-doc paths, vendor names, or Skill/doc-artifact names — not
   arbitrary first-party symbols. This was my own initial wrong assumption
   (I expected `relations` to behave like a general symbol-relationship lookup); I
   corrected it after reading `query relations --help` and re-targeted the next query
   at an actual doc path instead (entry 7).

4. `codecompass query relations balance_from_spec`
   → `error: 'balance_from_spec' not found in context-graph.db` (exit 1). Same
   corrected misunderstanding as entry 3 — ran before I'd checked `--help`; superseded
   by entry 7's correctly-scoped query. Recording this as a documented "assumption
   corrected once contradicted by evidence," per the task's trace requirements.

5. `codecompass query symbol ReportSpec`
   → `no symbol named 'ReportSpec' found in context-graph.db` (exit 0, not an error).
   Confirms the task's own stated expectation: `query symbol`/`query vendor` only
   resolve *third-party* dependency symbols, and Ledgerkit has zero third-party
   dependencies, so first-party symbols like `ReportSpec` correctly return nothing
   here — this is the documented not-a-bug case, verified directly rather than taken
   on faith.

6. `codecompass query vendor hledger`
   → `error: 'hledger' not found in context-graph.db` (exit 1). Same category as
   entry 5 — "hledger" is not a Python package dependency of this project (Ledgerkit
   is an independent Python reimplementation, not a binding to the real hledger
   binary), so there is no vendor entry for it. Confirms zero-third-party-deps
   framing a second, independent way.

7. `codecompass query relations dev-docs/api-spec.md`
   → returned a `mentions_a…`-relation table (column names truncated by the terminal
   renderer: `Relation`/`Other`/`Heading`/`Label`/`AI summary`) with ~10 rows, each
   showing `dev-docs/api-spec.md` mechanically mentioning other doc artifacts
   (`dev-docs/hledger-compatibility.md`, `dev-docs/planning/...` files, `docs/
   journal-format.md`), every one annotated `"mentioned, not yet enriched"` (no
   AI-enrichment pass has run on these edges yet) — plus an empty "Package code"
   table (no first-party source-usage trace attached to this doc specifically).
   This confirmed `relations` is scoped to doc-to-doc/vendor/Skill mechanical
   mentions, not symbol-level relationships — consistent with entries 3/4's error
   once correctly understood, and I did not re-run entries 3/4 with a different
   target since `dev-docs/api-spec.md` already is the authoritative doc for this
   feature (§5).

8. `codecompass check`
   → returned five empty/`(none)` tables (`Vendor`/`Recorded`/`Live`/`Severity`/
   `Notes` staleness table — empty; "Unused vendors" — none; "Documented but unused"
   — none; "Used but undocumented" — none; "Third-party skill mentions with no
   backing vendor/symbol" — none) plus two non-empty tables: "Spec docs with no
   detected relations" (`dev-docs/planning/core-redefinition/05-context-curator.md`,
   `dev-docs/planning/milestone-4-downstream-changes.md`,
   `dev-docs/pypi-trusted-publishing.md`,
   `dev-docs/retros/STAGE-C-PHASE-2-PLAN-AMENDMENT.md`) and an empty "Vendor docs with
   no detected relations" table. None of the four "no detected relations" docs is
   `dev-docs/api-spec.md`/`ROADMAP.md`/`docs/python-api.md` (the three docs actually
   relevant to this feature), so this surfaced no new leads for this specific
   investigation, but confirmed the overall graph is self-consistent/clean (zero
   coverage gaps) at the time of this research.

9. `codecompass query symbol ReportSpec` — see entry 5 (not duplicated here; listed
   once).

10. `codecompass query source-symbol balance_from_spec`
    → one row: `ledgerkit/reports.py`, function, line 600, public, full docstring
    (identical text to what direct file-reading already showed in §1/§3 — no new
    facts, confirmed index currency a second time on a different symbol).

11. `codecompass query source ledgerkit/cli.py`
    → full symbol index: `_fmt_amount`, `_fmt_balance`, `_abbreviate_account`,
    `_build_parser`, `_resolve_files` (with full docstring), `main` (with full
    docstring) — six symbols total, confirming independently (not just by direct
    source reading) that `cli.py` has no report-command-related code anywhere.

12. `codecompass query source ledgerkit/parser.py` (output truncated to first ~60
    lines via `| head -60` on my end, not by the tool)
    → symbol index for `_ParseContext`, `ParseError`, `ParseWarning`,
    `_parse_simple_date`, `_parse_txn_header`, `_strip_cost_annotation`,
    `_strip_lot_annotations`, `_normalise_space_separators`, `_parse_amount`,
    `_strip_directive_comment` (list continues beyond what I captured — I had
    already read the relevant main-loop logic directly in full via `Read`, so I did
    not request the remainder of this listing; recording this truncation explicitly
    since the task requires noting where I stopped short of exhaustive capture).

**Duplicated-research note**: entries 3 and 4 above (`query relations ReportSpec`,
`query relations balance_from_spec`) were redundant with each other once the first
one's error surfaced the actual tool semantics — running the second before checking
`--help` duplicated the same wrong assumption rather than learning from the first
failure. I corrected course by reading `query relations --help` before any further
`relations` calls, then used it correctly in entry 7. No other duplication identified:
each other CodeCompass query targeted a different symbol/file/doc, and none of them
told me something I'd already fully established from direct source reading — they
functioned as independent confirmation (content-hash/index-currency checks) rather
than as my primary discovery mechanism for this investigation, which was necessarily
driven by direct reading given how new/undocumented this specific feature is.

**Tests/commands run:**
- `/home/cormac/projects/codecompass/.venv/bin/python -m pytest tests/ -q` →
  `906 passed, 29 skipped, 1 warning, 14 subtests passed` (the 29 skips are the
  existing pandas-optional-dependency skips elsewhere in the suite, unrelated to this
  feature; the one warning is a pre-existing `SyntaxWarning` in
  `ledgerkit/query/eval.py`'s own docstring, also unrelated). Confirms a clean,
  fully-passing baseline before any design work — nothing in this investigation
  required or caused any code change.

**Assumptions made, then corrected:**
1. Initially assumed `codecompass query relations <symbol-name>` would behave like a
   general "what references this symbol" lookup (analogous to `query source-symbol`
   but relationship-oriented). Corrected after the first two calls errored and I read
   `query relations --help` in full: it is scoped specifically to the
   spec-doc ↔ vendor ↔ Skill mechanical-mention graph (`doc_relations_edges`), not
   arbitrary first-party symbol relationships. No first-party-symbol-to-symbol
   relationship query exists in this tool's surface at all (consistent with
   `source-symbol`'s own description: "first-party top-level implementation symbol,"
   i.e., lookup only, not graph traversal).
2. Initially treated the `comment`/`end comment` directive as a strong structural
   precedent for implementing `; report`/`; end report` (same "block opens, content
   consumed until a close marker" shape). After reading parser.py's main loop in
   exact execution order (offsets 955-1185 and 1195-1240), I corrected this: the two
   are matched at structurally different points in the loop — `comment` is a
   non-`;`-prefixed bare keyword matched *after* the general `;`/`#` comment-skip
   branch already returns/continues, whereas `; report` *is* `;`-prefixed and would
   already be consumed and discarded by that earlier branch before ever reaching a
   `comment`-style check placed in the same relative position. This reclassified the
   `comment`/`end comment` precedent from "directly reusable pattern" to "reusable
   state-machine *scaffolding* only, wrong insertion point" — the single most
   significant correction in this investigation, and the basis for §1/§3's emphasis
   on where in the loop the new logic must live.
