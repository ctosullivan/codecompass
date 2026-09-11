# Context health

A **forward-looking** assessment: for the roadmap phases coming up, is the
context CodeCompass holds adequate — fresh, grounded, complete, low-noise?
Distinct from:

- `roadmap-context-curator` — planning-doc *truth* (what's done, what's next);
- `context-evaluator` — per-task context *quality*, judged by direct
  inspection of a reference project;
- this file — *"is the graph in good enough shape for what we're about to
  do"*, judged by reading `context-graph.db` + `codecompass query` and
  cross-referencing `planning/ROADMAP.md`.

Introduced by Phase 43c. Prose + a table, refreshed at stage boundaries
and before any phase that leans on CodeCompass context. Not mechanised
(same posture as `milestone-closeout-checklist.md`).

**Owner:** the `context-health-planner` agent (`.claude/agents/context-health-planner.md`),
approved as the roster's 8th agent in Phase 43c. It may run `codecompass
query` (unlike `context-evaluator`, which is barred from using
CodeCompass).

Entries are dated; the current assessment replaces the previous one but
the "History" section keeps a one-line record.

---

## Assessment — 2026-09-11 (Phase 43c, ahead of Stage A close → Stage B)

**CodeCompass revision:** f47f3e2 · **graph:** `context-graph.db` last
rebuilt at `d34a486` (Phase 43, 2026-09-10) · **assessor:** lead (the
`context-health-planner` agent runs this for real during Phase 43c
execution and replaces this stub with its output).

### The graph today

| Dependency | Recorded | Installed | Fresh? | Used? | Enriched? | Notes |
|---|---|---|---|---|---|---|
| `anthropic` | 0.109.1 | 0.109.1 | ✅ | yes (15 sites) | yes | the enrichment-heavy one; API-surface + gotchas |
| `rich` | 15.0.0 | 15.0.0 | ✅ | yes | yes | — |
| `typer` | 0.27.1 | 0.27.1 | ✅ | yes | yes | — |
| `pipdeptree` | 4.2.1 | 4.2.1 | ✅ | **no** | no | correct — it's invoked as a subprocess, not imported; `Used: no` is accurate, not a gap |

- **Freshness:** all four recorded versions equal the installed versions
  (`pip show`), and lower-bound pins in `pyproject.toml` (`>=0.27`,
  `>=15`, `>=0.109`, `>=4.2`) are consistent (`decisions/0047`). No drift.
- **Grounding:** 3 of 4 enriched; `pipdeptree` correctly not (no usage).
- **Completeness:** `query skills` returns 9 agent-context artifacts
  (5 Skills + 3 `.cursor/rules/*.mdc` + `/discovery`), consistent with
  the Phase 43 change. Doc-mention edges present for the spec docs.
- **One caveat:** the committed `context-graph.db` predates the Phase 43
  `skill.py` prose change and will predate Phase 43b's tooling changes.
  The read-side `query skills` widening works without a rebuild (it's a
  SQL change in `graph.py`), but **before the graph is used as a
  demo/example artifact it should get one whole-project `codecompass
  sync`** to pick up the regenerated `SKILL.md` text. Low urgency — no
  upcoming phase reads it as ground truth.

### Do the upcoming phases lean on this graph?

| Phase | Leans on CodeCompass's own context? | Health verdict |
|---|---|---|
| 43b — `check_user_docs.py` standing-drift rules | No — a maintainer script, reads `src/`/`docs/` directly | n/a |
| 43c — this phase (planning) | No | n/a |
| 44 — reference-project protocol + eval spec → operational templates | No — writes templates + a registry | n/a |
| 45 — register Technical Clipper + baseline | No (CodeCompass's own graph); **yes** for Technical Clipper's | see below |
| 46 — CodeCompass during genuine Technical Clipper tasks | **Yes — Technical Clipper's graph**, not this repo's | see below |
| 47 — GATE DB consolidation | Reads the accumulated evidence, not the graph | n/a |

### The real forward-looking finding

**CodeCompass's own 4-dependency graph is healthy and will not be the
limiting factor in any Stage A→B phase.** The graph that matters from
Phase 45 on is **Technical Clipper's**, and the strongest prior
(`conditional-generalisation.md` §1.1) is that it will be **near-empty**:
Technical Clipper has ≈0 runtime package dependencies; its real technical
context is CommonMark, the DOM/Chromium API, and a CLI. CodeCompass's
`package → version → source → context` model has little to bite on there.

That is not a health problem to *fix* — it is the evidence Stage B exists
to gather. But it means:

1. Before Phase 45, run a `context-health` pass **on the Technical
   Clipper clone** (once registered) — expect the honest answer "the
   graph is nearly empty; here is what CodeCompass cannot represent",
   and file each un-representable dependency as a `planning/context-gaps/`
   entry (`decisions/0051`).
2. The Phase 46 `context-use-log.md` entries will mostly be LOW advantage
   for the same reason — record that honestly; it is a valid Stage B
   result, not a failure to hide.
3. A whole-project `codecompass sync` of this repo is worth doing before
   Phase 60's blank-slate docs reconstruction, not before Stage B.

### Recommended actions

| Action | Urgency | Owner |
|---|---|---|
| `codecompass sync` (whole project) to refresh `context-graph.db` past Phase 43/43b | Low — before Phase 60, not now | lead |
| `context-health` pass on the Technical Clipper clone once registered | **Before Phase 45** | `context-health-planner` |
| Nothing for `anthropic`/`rich`/`typer`/`pipdeptree` — all fresh and correctly classified | — | — |

---

## History

- **2026-09-11** (Phase 43c) — first assessment. Own graph healthy (4
  deps, all fresh, 3 enriched, `pipdeptree` correctly unused). Key
  finding: no Stage A→B phase is gated on CodeCompass's own context; the
  graph that matters next is Technical Clipper's, expected near-empty.
