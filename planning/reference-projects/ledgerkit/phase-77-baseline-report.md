# Phase 77 task-context evaluation — baseline agent report (verbatim)

Dispatched agent: `a81e3cde645ee8041`, no CodeCompass access, scoped to
`baseline-clone` only. Written to disk immediately on receipt, before
the treatment agent was dispatched (per `agent-led-workflow.md` step 5's
own `L-063`/`L-064`/`L-065`-derived rule).

Task: locate where DataFrame export of a report result is implemented;
identify where and how an external dependency is used to implement it;
list every report-result type supporting DataFrame export.

## 1. Principal first-party files/symbols implementing DataFrame export

The feature is implemented as a `to_dataframe()` method on several
result/container classes, spread across two files:

- **`ledgerkit/models.py`**
  - `Journal.to_dataframe(self, query: Query | None = None)` (method
    starts at line 479, class `Journal` starts line 296) — exports the
    *entire journal's postings* (one row per posting), with optional
    `Query`-based filtering. Flagged as conceptually not a "report
    result" class — see item 3.
  - `ReportSectionResult.to_dataframe(self)` (line 252, class starts
    line 244) — exports one structured-report section's computed rows
    plus a synthesized total row.
- **`ledgerkit/reports.py`**
  - `BalanceResult.to_dataframe(self)` (line 65, class starts line 39).
  - `RegisterResult.to_dataframe(self)` (line 116, class starts line
    93).
  - `AccountsResult.to_dataframe(self)` (line 171, class starts line
    149).
- **`ledgerkit/_pandas_compat.py`** — the shared helper all five
  `to_dataframe()` methods funnel through; its one function,
  `require_pandas()` (lines 11-21), does the actual `import pandas as
  pd` and raises a friendly `ImportError` if pandas isn't installed.

## 2. How the external dependency (pandas) is used

- **Which dependency**: `pandas` (`pyproject.toml`
  `[project.optional-dependencies] pandas = ["pandas>=1.3"]`).
- **Mechanism**: optional, lazily-imported, not a hard requirement.
  `dependencies = []` (pandas absent from unconditional deps); every
  `to_dataframe()` method imports pandas inside the method body via
  `_pandas_compat.require_pandas()`, so importing `ledgerkit`/
  `ledgerkit.models`/`ledgerkit.reports` never requires pandas at all —
  cost/failure deferred until `to_dataframe()` is actually called.
  `_pandas_compat.py` additionally imports pandas only under
  `TYPE_CHECKING` at module level, for type hints only.

## 3. Every report-result type supporting DataFrame export

1. **`BalanceResult`** (`reports.py`, extends `Mapping`) — return type
   of `Journal.balance()` flat mode; account → commodity → quantity.
2. **`RegisterResult`** (`reports.py`, extends `Sequence`) — return type
   of `Journal.register()`; chronological posting entries.
3. **`AccountsResult`** (`reports.py`, extends `Sequence`) — return type
   of `Journal.accounts()`; unique account names.
4. **`ReportSectionResult`** (`models.py`, `@dataclass`) — one computed
   section of a structured `ReportSpec`.
5. **`Journal`** (`models.py`, `@dataclass`) — the top-level parsed-
   journal container itself, flagged as not strictly a "report result."

Did not find `to_dataframe()` on `JournalStats` (`reports.py` line 182)
— journal statistics do not support DataFrame export.

## Tool-call log (in order, 13 calls)

1. `find` directory-tree listing.
2. `grep -rl "pandas\|DataFrame\|to_dataframe\|as_dataframe"` repo-wide.
3. `Read ledgerkit/_pandas_compat.py` (full).
4. `grep -n "pandas\|DataFrame\|def \|^class " ledgerkit/reports.py`.
5. `Read ledgerkit/reports.py` (offset 1, limit 185).
6. `grep -n "pandas\|DataFrame\|def \|^class " ledgerkit/models.py`.
7. `Read ledgerkit/models.py` (offset 198, limit 100).
8. `Read ledgerkit/models.py` (offset 460, limit 80).
9. `find pyproject.toml`.
10. `grep -n "pandas" ledgerkit/query/compat.py`.
11. `grep -n "DataFrame\|pandas" ledgerkit/query/compat.py` + `grep -n "pandas" pyproject.toml`.
12. `Read pyproject.toml` (full).
13. `grep -n "to_dataframe\|class Test\|def test_" tests/test_dataframe.py`.

## Self-disclosed limitation

Did not individually open every file the initial broad grep matched
incidentally (`cli.py`, `checks.py`, `commodity_style.py`,
`editor_model.py`, `loader.py`, `parser.py`, `tags.py`, `writer.py`,
`query/ast.py`, `query/depth.py`, `query/eval.py`, `query/parser.py`,
`query/regex.py`) — none showed up in the targeted `class`/`def` scans
of `reports.py`/`models.py`, but the agent did not verify with full
certainty that no sixth `to_dataframe` exists in those unread files.
