<!-- Copy to `<name>.md` in this directory when a reference project is
     registered (reference-project-protocol.md §2.1). Add a row to
     README.md's registry table at the same time. -->

# Reference project — <name>

- **Repository URL:** <https://...>
- **Starting revision:** <exact commit SHA the baseline was taken at —
  never "latest">
- **CodeCompass revision:** <short SHA or version used at registration>
- **Working copy location:** <scratch path — never inside this repo,
  never added to `vendor.toml` or `context-graph.db`>

## Inspection findings (at the starting revision)

<Established by reading the live repository directly — purpose,
language/build, structure, runtime dependencies, governance shape, current
roadmap state, why this project is a genuine test case. One table or a
short prose block; link to a fuller write-up in
`planning/v1-redefinition/` if one exists (e.g. `ledgerkit-plan.md`).>

## Evaluations

<One row per task evaluation. Each links to its full report at
`<name>/<NN>-<task-slug>.md` (`TEMPLATE-evaluation.md`).>

| # | Pinned revision | Task | CodeCompass revision | Verdict | Advantage | Report |
|---|---|---|---|---|---|---|
| 01 | <sha> | <one-line task> | <sha/version> | <PASS/PASS WITH GAPS/FAIL> | <LOW/MODERATE/HIGH> | [`01-<slug>.md`](<name>/01-<slug>.md) |

## Non-invasiveness check (per phase, reference-project-protocol.md §2.7)

<Confirmation, per phase that used this project, that no change was made
to its working copy beyond what its own maintainers would want on its own
merits, and no CodeCompass repair was made by the tester to make an
evaluation pass. One line per phase.>

- Phase <N>: <confirmed / n/a — reason>
