# Phase 80 Part 4 — frozen reader-question verification

15 questions frozen in `planning/phase-80-frozen-reader-questions.md`
BEFORE this check ran. Answered using only the published documentation
(Phase 1), then independently checked against primary evidence — real
source, live CLI runs, tests, a fresh clone of the real template repo
(Phase 2). Kept as a result SEPARATE from the coding-context-packet
evaluation (see `_part4-coding-context-packet-evaluation.md`).

## Verdicts

1. Install + first digest — CORRECT
2. `sync` vs `sync <vendor>` — CORRECT
3. Where state is stored / what's committed — **INCOMPLETE**
4. `query vendors` before any sync — CORRECT
5. Adding a new ecosystem adapter — CORRECT
6. Adding a new graph table: wiring + test coverage — **INCOMPLETE**
7. Does `sync` ever lose paid enrichment — CORRECT
8. How schema migrations are decided — CORRECT
9. Symbol-name uniqueness — CORRECT
10. Documented limitations — CORRECT
11. Template: existing `CLAUDE.md` handling — CORRECT
12. Template: is clean-room workflow required — CORRECT
13. Template: first command after copying — CORRECT
14. Template: no dependency manifest yet — CORRECT
15. Template: GPL project using MIT template — CORRECT

13/15 CORRECT, 2/15 INCOMPLETE (material omission, not inaccuracy), 0
WRONG, 0 AMBIGUOUS.

## Q3 — where generated state lives / what's committed

`architecture/overview.md` correctly and fully answers the
generated/gitignored half (`context-graph.db`, `vendor/<name>/`, citing
`decisions/0010`). Missing: no published doc ever explicitly states that
`vendor.toml` itself *should* be committed — a reader can only infer
this by noticing it's absent from the gitignored-artifact lists.
`decisions/0024` states it explicitly ("a small, hand-edited, three-field
config file," not a generated-data target) but that's an ADR, not a
user-facing doc. **Fixed**: added an explicit sentence to `README.md`.

## Q6 — adding a new graph table: wiring + test coverage

`architecture/context-graph-schema.md` is accurate on the mechanics (the
three table categories, `rebuild_deterministic`'s fixed order,
introspection-gated migrations) but — unlike
`docs/developer/writing-an-adapter.md`'s own explicit numbered
checklist for a new adapter — has no equivalent checklist for a new
table, and no doc states what test coverage is expected (confirmed:
`grep -rln "new table" docs/ architecture/` found only the descriptive
schema page itself, no checklist). **Fixed**: added a "Checklist for a
new table" section to `architecture/context-graph-schema.md`, mirroring
the adapter checklist's own shape.

No WRONG or AMBIGUOUS findings across either repository's documentation.
