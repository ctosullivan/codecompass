# Context-use log

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
