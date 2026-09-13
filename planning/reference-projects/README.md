# Reference-projects registry

The home for all Stage B/D (and later Stage F) reference-project
evaluation output — kept out of `planning/v1-redefinition/` (which is the
*plan*) and out of the repo root. Operationalises
[`reference-project-protocol.md`](../v1-redefinition/reference-project-protocol.md)
and
[`context-quality-evaluation.md`](../v1-redefinition/context-quality-evaluation.md).

## Registered reference projects

| Name | URL | Starting revision | Status | Record |
|---|---|---|---|---|
| Ledgerkit | https://github.com/ctosullivan/ledgerkit | `a3cf2a7` (2026-09-12) | baseline + 1 genuine task evaluated (Phases 45-46); GATE DB fix (Phase 49) confirmed working at GATE DC (Phase 51, re-pinned `05218e3`) | [`ledgerkit.md`](ledgerkit.md) |
| Technical Clipper | https://github.com/ctosullivan/technical-clipper | *(pinned at Phase 60)* | not yet registered | — (`technical-clipper.md`, Phase 60) |

`_instrument-dry-run.md` in this directory is a **self-test of the
instrument itself** (CodeCompass evaluated against its own repo, Phase
44), not a reference-project entry, and is never aggregated into either
row above.

## How a reference-project evaluation runs

1. **Register** the project: clone it at a pinned commit into a scratch
   location outside this repo (never into `vendor.toml` or
   `context-graph.db`); fill in `TEMPLATE-registration.md` and commit it
   as `<name>.md` in this directory, added to the table above.
2. **Pick a genuine task** from the project's own roadmap, deferred-work
   list, or a real open bug — never a task invented to exercise
   CodeCompass.
3. **Run the per-task procedure**
   (`reference-project-protocol.md` §2.4): the lead attempts the task
   using CodeCompass context; `reference-project-tester` records
   friction live; `context-evaluator` independently inspects the target
   repo (never via CodeCompass) and rates the supplied context.
4. **File the report** as `<name>/<NN>-<task-slug>.md`, filled in from
   `TEMPLATE-evaluation.md`. Every friction instance and material gap
   becomes a candidate learning
   (`../v1-redefinition/learning-lifecycle.md`).
5. **Consolidate** at the stage's findings phase — recurring friction
   becomes a confirmed finding, which maps to a roadmap implication
   (`reference-project-protocol.md` §2.6). A single observation never
   directly changes CodeCompass.

The central question every evaluation answers
(`reference-project-protocol.md` §2.5):

> Is CodeCompass supplying context that another development agent can
> safely trust, and is that context materially useful compared with
> cheap direct project exploration?
