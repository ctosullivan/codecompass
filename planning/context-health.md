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
the "History" section keeps a one-line record. **Exception:** when an
assessment targets a different graph entirely (a registered reference
project's own `context-graph.db`, not CodeCompass's own repo), it is
appended alongside rather than replacing — the two are not in competition
for "current."

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

## Assessment — 2026-09-13 (Phase 45, Ledgerkit baseline — first genuine solo run)

**Target:** Ledgerkit reference-project clone (scratch location, not this
repo), pinned commit `a3cf2a77ca0075fabd4f7153d2a19f45c6e69b97` ·
**CodeCompass revision:** 6c3f34e · **graph:** the clone's own
`context-graph.db`, built by the `codecompass --budget 0` /
`codecompass check` run that set up this clone (same session, same
checkout — built directly against the pinned commit, not stale relative
to it) · **assessor:** `context-health-planner` (this is its first solo
run, tracked forward from the Phase 43c retro; the 2026-09-11 assessment
above was lead-authored).

This assessment is **appended**, not a replacement — it judges a
different project's graph, per this file's header exception.

### The graph today

| Signal | Result |
|---|---|
| `codecompass query vendors` | **0 rows.** No vendors recorded. |
| `codecompass query skills` | **0 rows.** No Skills / cursor rules / slash commands attributed to the project. |
| `codecompass check` (unused / documented-but-unused / used-but-undocumented / third-party-skill-mentions) | all **(none)** |
| `codecompass check`'s "Spec docs with no detected relations" | `README.md`, `docs/getting-started.md`, `docs/journal-format.md`, `docs/python-api.md`, `docs/usage.md` — i.e. **every spec doc CodeCompass indexed**, all with zero relations |
| `codecompass query relations dev-docs/hledger-compatibility.md` | `error: 'dev-docs/hledger-compatibility.md' not found in context-graph.db` — this is CG-002 |

**Freshness:** trivially fresh — the graph was built in the same session
against the same pinned checkout it's being judged against, so there is
no recorded-vs-installed or recorded-vs-live drift to check. The one
freshness caveat that *does* carry forward: if Phase 46 makes real edits
to the clone (a genuine Stage B task will touch `models.py` / `parser.py`
/ `checks.py`), this graph will not reflect them without a re-sync. Given
how little the graph currently holds, a re-sync's *marginal* value is low,
but the *evaluator's* "freshness" criterion in Phase 46's
context-quality report should still be checked against whatever commit
the graph was actually built from, not assumed.

**Grounding:** nothing to ground — zero vendors means zero enrichment
targets. This is architecturally correct, not a gap: `pyproject.toml`
declares `dependencies = []` (`pandas` is a genuinely optional extra,
correctly not surfaced as a mandatory vendor). CodeCompass's
`package → version → source → context` model has nothing to attach to in
a stdlib-only project, exactly as predicted for this project shape
(`conditional-generalisation.md` §1.1, the same prior that shaped the
2026-09-11 assessment's Technical Clipper prediction — confirmed here
first, on Ledgerkit, per the 2026-09-12 `realignment-2026-09.md`
reordering).

**Completeness:** this is where the finding sharpens beyond "empty is
fine." The five `docs/**/*.md` + `README.md` files *are* indexed as spec
docs (glob coverage is working as designed for that tree) but carry zero
relations — expected, since there are no vendors to relate them to. The
substantive problem is different in kind: **the entire `dev-docs/` tree —
`architecture.md`, `api-spec.md`, `hledger-compatibility.md`, `SYNC.md`,
`editor-readiness-decisions.md`, the whole
`dev-docs/planning/core-redefinition/*.md` governance package, and
`dev-docs/compat-register/*.yaml` — is not merely unrelated, it is
entirely absent from `doc_artifacts`.** `_DEFAULT_GLOBS`
(`src/codecompass/spec_docs.py`) has no `dev-docs/**/*.md` entry, so none
of it was ever considered. This is filed as **CG-002**.

**Noise:** none observed — an empty graph cannot be noisy. `query skills`
correctly returns nothing: the two `.claude/` artifacts codecompass wrote
into the clone during setup (`.claude/skills/codecompass/SKILL.md`,
`.claude/commands/discovery.md`) are CodeCompass's own generated output,
not a pre-existing project convention, and appropriately aren't counted
as the project's "own" Skills — Ledgerkit has no project-authored Skills,
cursor rules, or slash commands of its own, so zero is the honest number
here too.

### Do the upcoming phases lean on this graph?

| Phase | Leans on CodeCompass's own context? | Health verdict |
|---|---|---|
| 46 — CodeCompass during a genuine Ledgerkit task (Stage B, once its task is re-picked post-redefinition) | **Yes — this graph** | **Not adequate for the substance of a Stage B task** (see below) |
| 47 — GATE DB consolidation | Reads accumulated evidence (this assessment, the baseline eval, CG-002), not the graph directly | n/a |

### The real forward-looking finding

**The near-total absence of package-level content is the expected,
honest result and is not the risk.** Ledgerkit has 0 runtime dependencies
by design; a package-graph tool has nothing to say about a project like
this, and that is Stage B's own hypothesis being confirmed, not a defect.
No action should be taken to make this graph look fuller than the project
warrants.

**The actual risk is `dev-docs/` invisibility landing exactly where
Stage B's genuine task lives.** Stage B's focus per `ROADMAP.md` is "Core
model — journal/accounting model review, Editor-compatibility
confirmation," and its plan (`dev-docs/planning/core-redefinition/06-core-architecture.md`)
is written entirely in terms of the pipeline described in
`dev-docs/architecture.md`, the non-obvious judgment calls recorded in
`dev-docs/editor-readiness-decisions.md`, and the compatibility contract
in `dev-docs/hledger-compatibility.md` — i.e. **precisely the tree
CodeCompass cannot see.** Whatever Phase 46's task turns out to be once
re-picked, if it asks CodeCompass anything shaped like "what governs this
model / this field / this compatibility behaviour," the honest current
answer is either silence (a spec doc query against `docs/` returns "no
relations," correctly but unhelpfully) or a hard `not found` (against
`dev-docs/`, per CG-002) — not a wrong answer, but also not the answer
that exists in the repository. A fresh Claude session doing an ordinary
`ls dev-docs/` would find all of this in seconds; CodeCompass currently
would not surface it at all. Per the context-advantage scale
(`context-quality-evaluation.md` §5), the honest prediction for Phase
46's eval report is **LOW** — not because Ledgerkit lacks real governing
documentation (it has an unusually rich `dev-docs/` corpus for a project
this size) but because none of it is reachable through the mechanism
being evaluated.

One further thing worth naming now rather than being surprised by later:
`dev-docs/compat-register/*.yaml` (25+ structured compatibility-register
entries — the artifact Stage H is specifically about) is a **different**
un-representable category from CG-002's markdown-glob gap — it's
structured data, not prose, so even the smallest CG-002 fix (adding
`dev-docs/**/*.md` to `_DEFAULT_GLOBS`) would not reach it. Not
immediately material to a Stage B task, but worth a fresh
`context-health` look once Stage H work is scheduled, since a `.md`-glob
fix could otherwise be mistaken for "the `dev-docs/` gap is closed."
Not filed as a separate `context-gaps` entry yet — this is a forward
prediction, not an observed query miss, and CG-002 already covers the
category of gap (detection-scope, not relationship-quality) it belongs
to.

### Recommended actions

| Action | Urgency | Owner |
|---|---|---|
| No action to enrich or "fill out" the package graph — 0 runtime deps is the honest, correct state for this project | — | — |
| Treat CG-002 as directly load-bearing for Phase 46, not a background finding — whatever task is re-picked for Stage B should be understood to get **no CodeCompass-sourced context from `dev-docs/`** until/unless CG-002 is triaged and (if promoted) fixed | **Before Phase 46's task is run** | lead / `knowledge-curator` (triage), `context-evaluator` (must independently confirm ground truth from `dev-docs/` directly, not rely on the graph, for exactly this reason) |
| Re-run this `context-health` pass on the Ledgerkit clone if/when Phase 46 makes real code edits to it, before treating the graph as current for the after-task evaluation | Low now; before any *later* phase reads this same clone's graph as ground truth | `context-health-planner` |
| Re-check `dev-docs/compat-register/*.yaml` representability specifically when Stage H is scheduled — a CG-002-only fix will not cover it | Low — Stage H is several stages out | `context-health-planner` |

---

## History

- **2026-09-11** (Phase 43c) — first assessment. Own graph healthy (4
  deps, all fresh, 3 enriched, `pipdeptree` correctly unused). Key
  finding: no Stage A→B phase is gated on CodeCompass's own context; the
  graph that matters next is Technical Clipper's, expected near-empty.
- **2026-09-13** (Phase 45, first genuine solo run) — Ledgerkit clone
  assessed: 0 vendors, 0 skills (both correct for this project shape);
  `dev-docs/` entirely undetected as spec docs (CG-002). Key finding:
  Stage B's actual task material lives in `dev-docs/`, which this graph
  cannot see at all — predicted LOW context advantage for Phase 46, not
  because Ledgerkit lacks governing docs but because none are reachable
  through CodeCompass.
