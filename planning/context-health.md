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

## Assessment — 2026-09-27 (Phase 72, Stage C learnings capture + post-v1 roadmap realignment — stage-boundary check ahead of Priority A)

**Supersedes the 2026-09-24 assessment above (same target: CodeCompass's
own repo) per this file's own "current assessment replaces the previous
one" rule.** **CodeCompass revision:** `933579c` (2026-09-27, Phase 72's
own plan-file commit; no `src/` change since the last graph rebuild) ·
**graph:** this checkout's own `context-graph.db` (gitignored,
`decisions/0024`) · **assessor:** `context-health-planner`, dispatched by
Phase 72's plan (`planning/phase-72-stage-c-learnings-and-roadmap-realignment.md`
§2 step 2) — this realignment is exactly the kind of stage-boundary
moment `planning/agent-led-workflow.md` step 4 and this role's own
cadence (`L-041`) call for a fresh adequacy assessment, this time asked
forward against whatever **Priority A** (task-oriented context
completeness/discovery, most likely reviving Phase 48's own old scope)
turns into once a future session plans it.

### The graph today

| Dependency | Recorded | Installed (`.venv/bin/pip show`) | Fresh? | Used? | Enriched? |
|---|---|---|---|---|---|
| `anthropic` | 1.5.0 | 1.5.0 | ✅ | yes | no |
| `rich` | 15.0.0 | 15.0.0 | ✅ | yes | no |
| `typer` | 0.27.2 | 0.27.2 | ✅ | yes | no |
| `pipdeptree` | 4.2.5 | 4.2.5 | ✅ | no (correct — subprocess only) | no |

- **Freshness (package layer):** unchanged, clean — 4/4 match, same as
  every prior assessment. (Note for whoever reads this next: the
  system-wide `pip`/`pip show` in this environment resolves to a
  *different* interpreter than the project's own `.venv` — e.g. system
  `pip show rich` reports `13.9.4`, a stale unrelated environment. The
  correct comparison is always `.venv/bin/pip show`, which matches the
  graph exactly. Worth naming explicitly since it's an easy false-alarm
  trap for a future run of this same check.)
- **Completeness — the 2026-09-24 finding is resolved.** The re-sync that
  assessment recommended has visibly run: `meta.last_deterministic_rebuild_at`
  = `2026-09-24T00:28:40Z` (same day, after that assessment's own
  session), and `doc_artifacts` (145), `doc_chunks` (2237),
  `documents_edges` (605), `doc_relations_edges` (115),
  `skill_mentions_edges` (11), and `symbols` (2440) are all populated.
  `codecompass query skills` returns 9 rows again (matching the original
  2026-09-11 count, not the 0-row regression seen at Phase 67). The
  specific worked example that errored at the last assessment —
  `codecompass query relations architecture/overview.md` — now
  reproduces cleanly with real relation rows. This closes out the prior
  assessment's top recommended action; no further action needed on it.
- **Minor, non-blocking freshness footnote:** four commits landed after
  that `2026-09-24T00:28:40Z` rebuild (`40fc074`, `4d3a4f2`, `9dba747`,
  `b7d0bf3`) — three touch `docs/domain/**/*.md` content (spec-doc-glob
  covered: `connector.md`, `invariant.md`, `claim.md`, `decision.md`,
  `evidence.md`, `provenance.md`) and two touch `pyproject.toml`
  (version-string bumps only — package rename/`.dev0` drop — not
  dependency pins). Spot-checked: `codecompass query relations
  docs/domain/concepts/connector.md` still resolves without error. None
  of these four commits touch a vendor, a symbol, or CLI-observable
  behaviour, so this is not a re-sync trigger — flagged only so it isn't
  mistaken for a clean rebuild-matches-HEAD state if someone checks the
  commit hash literally.
- **Enrichment still 0 rows** across `vendor_enrichment`,
  `symbol_enrichment`, `doc_relation_enrichment` — unchanged since Phase
  67. Still correctly low-urgency: no phase between here and Priority A's
  eventual scoping reads enrichment text as evidence, and Priority A as
  currently understood (see below) is about *edges/relations*, not
  enrichment prose.
- **Noise:** none observed.

### Does the next Priority-relevant work lean on this graph?

| Item | Leans on CodeCompass's own context? | Note |
|---|---|---|
| Phase 72 itself (this synthesis/ADR/roadmap-realignment phase) | **No** — grounded in git history, existing planning docs, and the Ledgerkit evidence record, not the graph | n/a |
| **Priority A** (task-oriented context completeness/discovery — not yet a written `planning/phase-N-*.md`; Phase 72 §0 explicitly defers writing that plan to a future session) | **Yes, directly and unusually so** — unlike almost every prior internal/tooling phase this file has assessed, Priority A's own subject matter *is* a capability of this graph, not merely a task that happens to run inside this repo | see finding below |
| Priorities B–F (claim/evidence/contradiction model, gap-detection/research-task conversion, documentation-first workflow, independent evaluation, clean-environment reproducibility) | Not assessed here — none has a concrete near-term phase yet; each should get its own forward check when scoped, per this role's normal cadence | n/a |

### The real forward-looking finding

**Housekeeping is in good shape — the substantive finding is about a gap
this project already knows it has, not a new one.**
`planning/context-gaps/inbox.md`'s **CG-001** ("one feature spread across
three `src/` modules, with no edge joining them," filed 2026-09-11, Phase
43) is the founding, still-open evidence for exactly the hypothesis
Priority A would set out to test: *"task-oriented retrieval needs new
edges (not just new joins)"* (`conditional-generalisation.md` §2.6,
restated verbatim in `context-gaps/README.md`'s own hypothesis table,
which names CG-001 as "the first"). Re-confirmed today: CG-001's status
line still reads `candidate` — it has never recurred and was never
independently filed by a second agent, the project's own bar
(`context-gaps/README.md`: promoted `candidate` → `recurred` only on a
recurrence or two-agent independent filing) for treating a graph-schema
gap as load-bearing evidence rather than a single anecdote. Phase 72's
own plan (§0) already declines to resolve GATE DD's graph-schema funding
question on CG-001 (plus CG-003/CG-006/CG-007) for exactly this reason —
this assessment agrees with that call, on independent inspection of the
same entry, not merely by citing the plan.

This is directly load-bearing for however Priority A gets planned:

- The graph's current behavior on this exact task shape is not a defect
  — `codecompass query relations src/codecompass/skill.py` correctly
  returns "not found" because intra-`src` feature-grouping edges are
  genuinely outside today's schema (package/vendor/spec-doc mention
  edges only). A Priority A phase should expect this and not mistake a
  correct "no data" answer for a bug.
- Priority A's own first real task is the most plausible place a second,
  independent CG-001-shaped occurrence would surface. Whoever plans it
  should explicitly watch for that and file it as a new dated entry
  (`decisions/0051`'s process) if it recurs — including if it recurs in
  a form that *doesn't* end up justifying a schema change — rather than
  either (a) treating CG-001 alone as already-sufficient evidence to
  skip straight to a schema-generalisation design, or (b) letting a real
  second occurrence go unfiled because "it's basically the same as
  CG-001, no need to log it again." The recurrence-bar discipline only
  works if occurrences actually get logged.
- No concept for "task-context completeness" or CG-001's own
  graph-capability-gap framing exists yet in `docs/domain/concepts/`
  (checked: 19 concept files, none of this shape) — deliberately, per
  Phase 72 §5's own explicit deferral. Given this project's own
  precedent for "new capability + new concept" work (Phase 54c/60,
  formalised as the Scope → Plan → Domain → Design → Implement
  methodology, `decisions/0060`), whoever plans Priority A should expect
  to run it through that pipeline — including opening a
  `planning/knowledge/<feature-slug>/` directory — rather than jump
  straight from ADR 0062's prioritisation language to a design doc. None
  of the four existing `planning/knowledge/` directories
  (`codecompass-domain`, `doc-origin-pinned-reference`,
  `haskell-api-surface-extraction`, `hledger-depth`) currently cover this
  feature.

### Recommended actions

| Action | Urgency | Owner |
|---|---|---|
| No re-sync needed now — the 2026-09-24 recommendation was carried out and is confirmed live (doc/skill detection populated, worked example reproduces) | — | — |
| No re-enrichment action — still correctly low-urgency; no consumer reads enrichment text before Priority A is even scoped | Low | lead (cost/consent decision, if it ever becomes relevant) |
| When Priority A's own `planning/phase-N-*.md` is written: re-read this entry plus CG-001, `conditional-generalisation.md` §2.6, and `context-gaps/README.md`'s hypothesis table before scoping; treat "does this task's first real investigation reproduce CG-001's edge-shortfall independently" as a question the plan must explicitly answer (and log, either way) rather than an incidental discovery | Before that phase's plan file is written | whoever plans Priority A (lead, `CLAUDE.md` §1) + `context-researcher` once scoped |
| No new `context-gaps/` candidate filed this pass — nothing new observed beyond what CG-001/CG-003/CG-006/CG-007 already record; the "second occurrence" named above is a forward risk for the next phase to watch for, not something hit during this read-only pass | — | — |

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
- **2026-09-24** (Phase 67, final validation) — fresh re-check of
  CodeCompass's own graph: package-version freshness still clean (4/4
  match `pip show`), but **enrichment (all 3 tables) and doc/skill
  detection (`doc_artifacts`, `doc_chunks`, `documents_edges`,
  `doc_relations_edges`, `skill_mentions_edges`) all read 0 rows** —
  `meta.last_deterministic_rebuild_at` predates Phases 45-66 entirely.
  Live-reproduced: `ai-docs/README.md`'s own worked
  `query relations architecture/overview.md` example currently errors.
  Not a code defect and no phase 67-70 is gated on it, but a re-sync is
  recommended before this graph is used as a live demo again. Ledgerkit's
  CG-002 spot-checked live and reconfirmed still fixed (unchanged since
  Phase 51).
- **2026-09-27** (Phase 72, stage-boundary check ahead of Priority A) —
  own graph re-checked: the 2026-09-24 re-sync recommendation was carried
  out (doc/skill detection and doc-relations fully repopulated,
  `ai-docs/README.md`'s worked example now reproduces cleanly); package
  freshness still clean; enrichment still 0 rows (still low-urgency, no
  consumer). Key finding: CG-001 ("task-oriented retrieval needs new
  edges") — the founding, still-`candidate`, never-recurred evidence
  behind `conditional-generalisation.md` §2.6 — is directly load-bearing
  for however Priority A (task-oriented context discovery) gets planned;
  no new `context-gaps` candidate filed, but flagged that Priority A's
  own first task is the likeliest place a second, loggable occurrence
  would surface.
