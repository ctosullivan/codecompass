# Phase 77 task-context evaluation — treatment agent report (verbatim)

Dispatched agent: `ae65dd22891237e4b`, CodeCompass installed and synced,
scoped to `treatment-clone` only. Written to disk immediately on
receipt.

Task: identical to the baseline agent's own task (see
`phase-77-baseline-report.md`), plus access to
`codecompass query source`/`source-symbol`/`symbol`/`vendor`/`vendors`.

## 1. Principal first-party files/symbols implementing DataFrame export

Two files, five `to_dataframe()` methods:

- **`ledgerkit/reports.py`** (lines 36-178, a block explicitly commented
  `# Transparent result wrappers with to_dataframe() support`):
  `BalanceResult.to_dataframe()` (line 65), `RegisterResult.to_dataframe()`
  (line 116), `AccountsResult.to_dataframe()` (line 171).
- **`ledgerkit/models.py`**: `ReportSectionResult.to_dataframe()` (line
  252); `Journal.to_dataframe(query=None)` (line 479) — a convenience
  method on the top-level `Journal` container itself, routed through the
  same canonical query-to-AST path other report functions use (Stage C
  Phase 8 convergence, per the docstring).

All five follow the identical pattern: lazy-import `require_pandas()`,
build row-dicts, construct `pd.DataFrame(...)`, force `amount` back to
`dtype=object` to preserve `Decimal` precision.

## 2. External dependency mechanism

`pandas` — optional, lazily-imported, not a hard requirement.
`dependencies = []`; `pandas = ["pandas>=1.3"]` only under
`[project.optional-dependencies]`. The indirection lives in
`ledgerkit/_pandas_compat.py`'s one function, `require_pandas()` — a
`try`/`except ImportError` wrapper raising a clear, actionable message
(`pip install ledgerkit[pandas]`). Every `to_dataframe()` method imports
pandas inside the method body via this helper, never at module import
time; a `TYPE_CHECKING`-only import exists purely for type hints.

## 3. Every report-result type supporting DataFrame export

Same five as the baseline agent's own list: `BalanceResult`,
`RegisterResult`, `AccountsResult`, `ReportSectionResult`, `Journal`
(flagged, like the baseline report, as not strictly a "report result").
`JournalStats` confirmed unsupported by both agents independently.

## Tool-call log, in order (17 calls)

1. `ls` + `find . -iname "*.py" | xargs grep -l "dataframe\|DataFrame"`.
2. `codecompass query source ledgerkit/reports.py`.
3. `codecompass query source-symbol to_dataframe` — no result.
4. `codecompass query symbol DataFrame` — no result.
5. `codecompass query source ledgerkit/_pandas_compat.py`.
6. `codecompass query source ledgerkit/models.py`.
7. `grep -n -i "dataframe\|pandas" ledgerkit/reports.py ledgerkit/models.py`.
8. `codecompass query symbol to_dataframe`, `query symbol require_pandas`,
   `query vendor pandas`, `query vendors` — confirmed pandas is not a
   tracked vendor at all (empty vendors table).
9. `codecompass query --help`.
10. `codecompass query symbol ledgerkit._pandas_compat.require_pandas`
    (dotted-path attempt, no result) then
    `codecompass query source-symbol require_pandas` (succeeded — bare
    names only).
11. `grep -n -i "pandas" vendor.toml pyproject.toml`.
12. `Read pyproject.toml` (lines 1-50).
13. `Read ledgerkit/_pandas_compat.py` (full).
14. `Read ledgerkit/reports.py` (lines 36-235).
15. `Read ledgerkit/models.py` (lines 198-297).
16. `Read ledgerkit/models.py` (lines 460-534).
17. `grep -n "to_dataframe\|class \|def balance_from_spec" tests/test_dataframe.py`.

## Additional investigation after consulting codecompass, and why (self-disclosed)

**Yes — a real, honest, load-bearing finding.** `codecompass query
source`/`source-symbol` only surface **top-level** symbols per file
(classes and top-level functions), never descending into class bodies.
Since every `to_dataframe()` implementation is a *method*, CodeCompass
correctly told the agent the five containing classes exist (with good
docstring-level descriptions) but could **not** tell it:

- that `to_dataframe()` methods exist on them at all, or their line
  numbers/signatures/columns/behavior;
- the exact optional-pandas mechanism (needed `_pandas_compat.py`'s
  literal source and `pyproject.toml`'s real dependency declarations,
  not just `require_pandas`'s own one-line docstring summary);
- that `Journal` (not obviously a "report result" by name) also has a
  `to_dataframe()` method — this only turned up via `grep`.

The agent therefore fell back to direct `grep`/`Read` of `reports.py`,
`models.py`, `_pandas_compat.py`, `pyproject.toml`, and
`tests/test_dataframe.py` for every method-level detail. All final
findings are grounded in direct source reads, not CodeCompass's own
output alone.
