# Context-use log (superseded)

**Superseded by `planning/context-observations/` as of Phase 52.** This
file's 4 real entries were migrated verbatim (as `OBS-001`…`OBS-004`,
reshaped into the new template — no content lost, including an explicit
edge-correctness/task-usefulness split the old format didn't have) into
`planning/context-observations/inbox.md`. New entries go there, not
here. Kept in place, not deleted, so any commit/ADR/retro that links to
a specific dated entry in this file still resolves.

One short entry **each time the lead or an agent retrieves CodeCompass
context during real work** — on CodeCompass's own development *and*, from
Stage B, on reference projects. Introduced by Phase 43c.

This is the **lightweight, high-volume complement** to the
`context-evaluator`'s per-task report (`context-quality-evaluation.md`).
Four lines, not a full evaluation. The point is volume: many small
honest datapoints about whether CodeCompass beat the default pathway.

## When to add an entry

- `planning/agent-led-workflow.md` **step 4** ("retrieve useful
  CodeCompass context"): if any context was retrieved this phase, add an
  entry before moving on. **If no CodeCompass context was used this
  phase, add a one-line "not used — <why>" entry** (that is also a
  datapoint — it says the graph didn't help here).
- `reference-project-tester` in Stages B/D: its friction log feeds this
  same format (one instrument, internal + external).
- Any other genuine retrieval (a `query`, reading a generated Skill,
  a `/discovery` read) during real work.

## Entry format

```
### <YYYY-MM-DD> · <phase> · <who> · <context source>

- **retrieved:** what was asked / what came back (concrete — the command,
  the row count, the artifact).
- **default pathway:** the grep / file read / `--help` an agent WITHOUT
  CodeCompass would have run — stated concretely, not hand-waved.
- **advantage: LOW | MODERATE | HIGH** — one sentence. (Definitions:
  `context-quality-evaluation.md` §5.)
- **wrong or misleading?** yes / no / partially — the highest-priority
  signal. Expand if yes/partially.
```

## Aggregation

Reviewed at each stage boundary and in bulk at Phases 47 and 55 (with the
`context-evaluator` reports and `planning/context-gaps/`). What matters:

- the LOW / MODERATE / HIGH distribution on CodeCompass's *own* small
  4-dependency graph (a prior: mostly LOW — the repo is small);
- **every "wrong or misleading? yes/partially"** — listed in full, these
  are the highest-priority findings (R3/R4);
- how the internal distribution compares to Technical Clipper's.

Entries are dated records — not rewritten.

---

## Entries (newest first)

### 2026-09-13 · Phase 46 (Ledgerkit genuine task — query semantics) · `reference-project-tester` · `codecompass query vendors` / `query relations` against Ledgerkit's own rebuilt `context-graph.db` (pinned `9c33e37`)

- **retrieved:** re-ran the exact retrieval attempt for the genuine task
  ("determine hledger 1.52's `acct:`/`desc:`/`date:`/`depth:`/`status:`/
  `not:` query-term semantics", already scoped by Ledgerkit's own
  `ROADMAP.md`/`CONTEXT.md` for Stage C Phase 1). `codecompass query
  vendors` → empty table (0 vendors — genuine, matches Phase 45).
  `codecompass query relations dev-docs/hledger-compatibility.md` and
  `codecompass query relations
  dev-docs/planning/core-redefinition/07-query-regex.md` → both
  `error: '<path>' not found in context-graph.db` — the second path is
  the file that actually contains the complete answer (§7.1's term
  table), and it is exactly as invisible as the first, for the identical
  `CG-002` reason (no `dev-docs/**/*.md` glob entry). CodeCompass
  contributed **zero** context to this task — not thin, a complete
  blank; no vendor, no doc relation, no Skill, nothing to read.
- **default pathway:** `grep -rn "query" dev-docs/planning/core-redefinition/`
  (seconds) found `07-query-regex.md` directly; reading its §7.1 table
  answered all 6 terms plus phasing, with no CodeCompass involvement at
  any point. Strictly faster and strictly more complete than the
  CodeCompass path, which returned nothing.
- **advantage: LOW** — and this instance is at the floor of LOW, not
  just an example of it: the definition's "marginal contribution" still
  implies *some* contribution. Here the contribution was exactly zero;
  the entire answer came from Ledgerkit's own prior planning work, found
  by one `grep`.
- **wrong or misleading?** no — an honest "not found" for both paths,
  not a false claim. But (per `L-016`, re-confirmed here) the "not
  found" error gives no signal that this is a known glob-coverage gap
  rather than a typo, which is itself the pre-existing finding this
  entry corroborates rather than a new wrinkle.

### 2026-09-12 · Phase 45 (Ledgerkit registration + baseline) · lead · bare `codecompass --budget 0` + `query vendors` / `query relations` against a fresh Ledgerkit clone (pinned `a3cf2a7`)

- **retrieved:** ran CodeCompass against Ledgerkit as-is for the first
  time — bare `codecompass --budget 0` (auto-discovery), `codecompass
  check`, `query vendors`, and `query relations` for `README.md`,
  `docs/journal-format.md`, and `dev-docs/hledger-compatibility.md`.
  Result: 0 vendors tracked (`dependencies = []` in `pyproject.toml`;
  `pandas` is a genuinely optional extra, correctly not auto-discovered);
  `README.md`/`docs/journal-format.md` indexed as spec docs but with zero
  relations (nothing to relate to); `dev-docs/hledger-compatibility.md`
  — the file that actually states what governs hledger-1.52
  compatibility — returned `error: not found in context-graph.db`
  entirely, not "no relations." Filed as **CG-002** (the entire
  `dev-docs/` tree is outside `spec_docs._DEFAULT_GLOBS`).
- **default pathway:** `grep -rn "dependencies" pyproject.toml` for the
  dependency question (one line, `dependencies = []`); `find dev-docs -name
  "*.md"` + reading `dev-docs/hledger-compatibility.md` directly for the
  compatibility question — both at least as fast as CodeCompass here,
  and the second one *strictly better*, since CodeCompass currently
  cannot see that file at all.
- **advantage: LOW** — for the dependency question, matches the honest
  expected outcome (`ledgerkit-plan.md`, `adoption-blueprint`-adjacent
  `dev-docs/planning/core-redefinition/04-codecompass-integration.md`
  both predicted this). For the compatibility-governance question,
  CodeCompass was **strictly worse than direct inspection** — it didn't
  just fail to add value, it returned nothing where the real answer
  (`dev-docs/hledger-compatibility.md`) was one `find`+`read` away. This
  is the first real Stage B datapoint of that shape.
- **wrong or misleading?** partially — not a false claim, but silently
  omitting an entire real spec-doc directory (vs. accurately reporting
  "no relations" for the docs it does see) could read as "nothing governs
  this" to an agent that doesn't know to check the glob list. Filed as
  CG-002, not just noted here.

### 2026-09-12 · Phase 44 (reference-project protocol) · lead · `codecompass sync --budget 0` + `query vendor typer` / `query symbol Typer` against the repo's own (freshly rebuilt) `context-graph.db`

- **retrieved:** this checkout had no `context-graph.db`/`vendor/` at all
  (fresh clone, gitignored artifacts absent); ran `codecompass sync
  --budget 0` (mechanical Phase A only — no `ANTHROPIC_API_KEY` set, and
  this was a sanity-check retrieval, not a task needing AI enrichment
  spend) to rebuild it, then `codecompass query vendor typer` (version
  `0.27.2`, usage count 43) and `codecompass query symbol Typer --json`
  (the `Typer` class, `usage_count: 2`, `used_at`:
  `src/codecompass/cli.py:51` and `:54`, with a mechanically-sourced
  purpose blurb from the vendored README) — the exact input for the
  Phase 44 instrument dry-run's "what does this project use `typer` for
  and at what version" question.
- **default pathway:** `grep -n "import typer\|typer\.Typer(" -r
  src/codecompass/` to find the two call sites, then `pip show typer` (or
  read `pyproject.toml`'s pin) for the version, then read `typer`'s own
  README/docstring for what `Typer` does. ~3 commands, all obvious for
  a repo this small.
- **advantage: LOW** — this is precisely the instrument's own self-test
  case (`_instrument-dry-run.md`), chosen because it's small and
  well-understood; CodeCompass packaged the same facts one command sooner
  but surfaced nothing a quick grep + `pip show` wouldn't have. Honest,
  expected result — see the dry-run report for the independent
  `context-evaluator` rating.
- **wrong or misleading?** no — version, usage count, and both `used_at`
  line numbers were independently re-verified against `src/codecompass/cli.py`
  and matched exactly.

### 2026-09-10 · Phase 43 (`43a`, `query skills` widen) · lead · `codecompass query skills` against the repo's own `context-graph.db`

- **retrieved:** ran `codecompass query skills` before and after the
  `graph.skills_index` change. Before: 5 rows (all `kind='skill'`).
  After: 9 rows (5 Skills + 3 Cursor `.mdc` + `/discovery`), each with
  its `kind`. Used as the fast confidence check that the widened SQL did
  what it should, before writing tests.
- **default pathway:** `grep -rn "doc_artifacts" src/codecompass/graph.py`
  to find the `skills_index` query, read it to see the `WHERE kind =
  'skill'` filter, then `sqlite3 context-graph.db "SELECT kind,
  count(*) FROM doc_artifacts GROUP BY kind"` to see what kinds actually
  exist. ~3 commands, all obvious.
- **advantage: LOW** — the default pathway is short and an agent touching
  this code would run it anyway; `query skills` packaged the same facts
  one command sooner. It did *not* surface anything the grep wouldn't
  have. (Honest expected result for a change *inside* CodeCompass's own
  query layer — dogfooding the tool on the tool is a hard case for it.)
- **wrong or misleading?** no — the row counts were accurate and matched
  the post-change test assertions (9 rows) exactly.

<!-- Phases 39–42 predate this log and are not backfilled (see the
     Phase 43c plan, "Explicitly deferred"). Stage B starts adding
     reference-project entries at Phase 46. -->
