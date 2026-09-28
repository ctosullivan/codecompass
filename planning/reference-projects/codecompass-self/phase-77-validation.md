# Phase 77 validation — template zero-vendor acceptance test + CodeCompass dogfooding

## 1. Template / zero-vendor acceptance test

- **Repository:** https://github.com/ctosullivan/codecompass-template
  (populated by this phase — previously confirmed empty, see the plan's
  own §0).
- **Working copy:** a genuinely fresh clone (distinct from the working
  copy that pushed the template's initial content), into a scratch
  location outside CodeCompass's own tree — never added to CodeCompass's
  own `vendor.toml`/`context-graph.db`, fully deleted after this
  validation.
- **Fixture added** (uncommitted, local to the scratch clone only, never
  pushed back to the template's own remote): `ledger/models.py`
  (`Posting`, `Amount` classes; `_normalize_commodity` a leading-
  underscore private function) and `tests/test_models.py` (one test
  function) — **zero entries in `vendor.toml`**.

**Result** (`codecompass sync`, then `query source`/`query source-symbol`):

- `source_files` rows exist for both added files, correctly classified
  `language: python`.
- `source_symbols` rows exist for all top-level declarations, including
  the private one — `Posting`/`Amount` both `exposure: public`,
  `_normalize_commodity` correctly `exposure: conventional_private`
  (never filtered out).
- `tests/test_models.py`'s own `test_posting_holds_amount` function is
  indexed too — tests preserved as source, not pruned.
- `vendors`/`symbols` tables: **0 rows each**, confirmed by direct
  `sqlite3` inspection — **no fake/self vendor row was created anywhere**
  to represent the project's own code.
- `meta.source_index_version = "1"`, confirmed present.
- Template repository hygiene: `git status` in the fresh clone showed no
  `context-graph.db` (confirmed `.gitignore`d via `git check-ignore -v`);
  the only tracked-file change was the root `CLAUDE.md` gaining
  CodeCompass's own documented, intentional `<!-- codecompass:start -->`/
  `<!-- codecompass:end -->` routing-table marker block — expected,
  reversible (`codecompass undo`) behaviour, not generated runtime state.

**Independent readability assessment**: dispatched a genuinely fresh,
context-free `general-purpose` agent to clone the real, published
template and assess it with no knowledge of this plan or of CodeCompass
itself. **Verdict: READY** (no blocking issues) — confirmed: adoption
steps are concrete and runnable; the workflow shape reads as real habit,
not empty ceremony; the MIT/GPL license relationship is stated clearly
and honestly in three places; `decisions/`/`planning/ROADMAP.md`/
`CONTEXT.md`/`retros/`/`knowledge/`/`context-gaps/` are all distinct and
cross-reference their own boundaries. One non-blocking nit: the MIT/GPL
relationship note is stated near-identically in both `README.md` and
`docs/architecture.md` — harmless redundancy, not a contradiction.

This is the architectural acceptance test the plan's own §2 named: a
downstream project with zero tracked vendors gets a durable, queryable
representation of its own source, with no fake vendor required.

## 2. CodeCompass dogfooding

- **Fixture:** this repository's own real working tree — no clone
  needed.
- Ran the real, actual `codecompass sync` against CodeCompass's own
  checkout (aborted at the AI-enrichment cost-confirmation prompt, by
  design — the deterministic rebuild, which includes first-party
  indexing, already completed before that prompt).
- **Result**: `source_files` — 91 rows; `source_symbols` — 1,165 rows;
  `meta.source_index_version = "1"`.
- `codecompass query source-symbol detect_git_topology` and
  `rebuild_project_graph` both return real, correct data — right file
  (`src/codecompass/git_topology.py`/`sync.py`), right line, the real
  docstring text, `exposure: public`.
- `codecompass query symbol Anthropic` (an existing, already-tracked
  vendor symbol) still returns its own real usage sites — confirming
  vendor and first-party symbol data coexist in the same
  `context-graph.db` with no interference between the two namespaces.
- `git status` after the sync: clean — `context-graph.db` remains
  correctly gitignored in this repository too.
