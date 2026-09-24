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

## Assessment — 2026-09-24 (Phase 67, final validation — self-dogfood re-check)

**Supersedes the 2026-09-11 assessment above (same target: CodeCompass's
own repo) per this file's own "current assessment replaces the previous
one" rule.** **CodeCompass revision:** `abc1186` (2026-09-24) ·
**graph:** this checkout's own `context-graph.db` (gitignored,
`decisions/0024`) · **assessor:** `context-health-planner`, dispatched by
Phase 67 sub-task 1 (`planning/phase-67-final-validation.md` §1) —
explicitly checking whether the Phase 45 snapshot still holds after
Phases 46–66 (21 phases, none of which touched this repo's own graph
directly).

### The graph today

| Dependency | Recorded | Installed (`pip show`) | Fresh? | Used? (uses_edges) | Enriched? | Notes |
|---|---|---|---|---|---|---|
| `anthropic` | 1.5.0 | 1.5.0 | ✅ | yes (15) | **no** | deterministic-only `vendor/anthropic/CLAUDE.md` ("Known gotchas: No known side effects detected." — the placeholder, not real AI text) |
| `rich` | 15.0.0 | 15.0.0 | ✅ | yes (6) | **no** | same pattern |
| `typer` | 0.27.2 | 0.27.2 | ✅ | yes (43) | **no** | same pattern |
| `pipdeptree` | 4.2.5 | 4.2.5 | ✅ | **no** | no | correct — invoked as a subprocess, never imported (unchanged since 2026-09-11) |

- **Freshness (package layer):** all four recorded versions match both
  `pip show` and `pyproject.toml`'s lower-bound pins (`>=0.27`, `>=15`,
  `>=0.109` — n.b. the pin floor is stale relative to the now-installed
  1.5.0 but that's a pin-floor question, not a graph-freshness one, and
  outside this file's remit) — **no drift**, same clean result as
  2026-09-11.
- **Enrichment — materially changed, and not for the better.** `SELECT
  count(*)` against `vendor_enrichment`, `symbol_enrichment`, and
  `doc_relation_enrichment` all return **0** in this checkout's graph
  right now. The 2026-09-11 assessment recorded anthropic/rich/typer as
  enriched ("the enrichment-heavy one; API-surface + gotchas"); that
  state is **not present** in the graph as it currently sits on disk.
  `codecompass check`'s "Used but undocumented" list confirms this from
  the query side: 13 real symbols across all three used vendors
  (`Anthropic`, `AnthropicError`, `Console`, `Markdown`, `Prompt`,
  `Table`, `Argument`, `CliRunner`, `Context`, `Exit`, `Option`, `Typer`,
  `confirm`) show as undocumented.
- **Completeness — the more significant finding.** `doc_artifacts`,
  `doc_chunks`, `documents_edges`, `doc_relations_edges`, and
  `skill_mentions_edges` are **all 0 rows** — despite this repository
  genuinely having 5 Skills + 1 slash command + 3 Cursor rules on disk
  (`.claude/skills/{codecompass,codecompass-anthropic,codecompass-rich,codecompass-typer,docs-sync}/`,
  `.claude/commands/discovery.md`, `.cursor/rules/*.mdc`) and a full set
  of real spec docs (`README.md`, `architecture/`, `decisions/`,
  `ai-docs/`, `docs/domain/`, etc.) — exactly the machinery Phases
  21/27/29/30/31/32/37/49/55b built and repeatedly verified working
  against this same repo. Live-reproduced, not inferred: `codecompass
  query skills` returns **0 rows** (2026-09-11 recorded 9), and running
  `ai-docs/README.md`'s own worked example verbatim —
  `codecompass query relations architecture/overview.md` — **errors**:
  `'architecture/overview.md' exists as a file but was not detected as a
  spec/vendor doc, so it has no relations recorded — check whether it's
  covered by spec_docs's glob coverage, then re-run sync`. That
  disambiguation message is itself Phase 49/L-016's own correct fix
  working as designed — it's not a crash, and it correctly diagnoses the
  cause — but the underlying condition it's warning about is real right
  now, in this checkout, for a doc example the project publishes as
  literally reproducible.
- **Root cause, as far as read-only inspection can tell:** `meta.last_deterministic_rebuild_at`
  = `2026-09-12T14:01:32Z` — i.e. whatever last ran the deterministic
  rebuild path predates Phase 45 through Phase 66 entirely (including
  the Haskell external-adapter work at 60–62 and the Phase 63D–66
  domain/docs reconstruction). Since spec-doc detection (Phase 21),
  skill scanning (Phase 12), and `ai-docs/` glob coverage (Phase 37) all
  predate that timestamp too, a genuine whole-project `codecompass sync`
  run at that point should have populated `doc_artifacts`/skills — their
  absence suggests whatever produced the *current* file's content either
  ran narrower than a real whole-project sync, or this checkout's graph
  file has since been touched (its mtime, 2026-09-23 21:12, postdates the
  meta timestamp) without a corresponding rebuild. I cannot determine
  which without running `sync`, which is outside this role's remit
  (read-only, per the agent's own operating rules) — I'm reporting the
  discrepancy, not diagnosing or fixing the pipeline itself.
- **Noise:** none observed — same posture as 2026-09-11; an incomplete
  graph isn't a noisy one, and the "used but undocumented" list above is
  a real, correctly-surfaced finding, not noise.

### Do the upcoming phases lean on this graph?

| Phase | Leans on CodeCompass's own context? | Health verdict |
|---|---|---|
| 67 (this phase), sub-task 4 — fresh-agent acceptance test | **No** — the dispatch protocol gives the agent repository access only; discovery is meant to happen by reading `README.md`/`CLAUDE.md`/`docs/domain/` directly, never via `codecompass query` (`phase-67-final-validation.md` §4) | n/a |
| 68–70 — independent release audit, milestone closeout, release | **No** — process/audit phases grounded in git history, ADRs, and direct doc review, matching every other internal/tooling phase's pattern to date | n/a |
| A reader following `ai-docs/README.md`'s own worked examples today | **Yes, incidentally** — one of its three example prompts (`query relations architecture/overview.md`) currently errors against this checkout's live graph, as reproduced above | see below |

### The real forward-looking finding

**No phase between here and v1 (68–70) is gated on this graph** — the
pattern holds exactly as it did at every prior assessment: internal and
process phases don't lean on CodeCompass's own context. That is the
honest, low-urgency half of this finding.

**The higher-urgency half is about credibility, not blocking:** Phase
67's own title is "self-dogfood," and this checkout's graph — the thing
a curious reader or auditor would actually run `codecompass query`
against right now — does not reflect the doc/skill-detection and
enrichment capability this project spent Phases 21–38, 49, and 55b
building and proving. A worked example from the project's own
`ai-docs/README.md` fails when tried today. This is a **staleness/re-sync
finding about a local generated artifact**, not a code defect (the
underlying mechanisms are exercised and passing in the test suite; this
checkout's graph simply hasn't had a genuine whole-project sync run
against current `HEAD` recently) and not an un-representable
relationship, so it does **not** belong in `context-gaps/inbox.md`
(`decisions/0051`) — filing it there would misclassify a sync-freshness
problem as a modelling gap. It belongs here, as a recommended action.

**Ledgerkit spot-check (CG-002), done live for this assessment:** the
live Ledgerkit clone at `/home/cormac/projects/ledgerkit` (pinned
`c6168b2`, its own `context-graph.db` rebuilt 2026-09-24 08:19) still
resolves `codecompass query relations dev-docs/hledger-compatibility.md`
cleanly (an empty-relations table, not the old `'...' not found` error)
— **CG-002 remains fixed**, unchanged since Phase 51's GATE DC
confirmation. `codecompass query vendors` on that clone still returns 0
rows (0 runtime deps, still the honest, correct number for that
project's shape) and `check`'s "spec docs with no detected relations"
still lists the full real `dev-docs/**`/`docs/**` tree, relation-less —
matching Phase 51's own PASS WITH GAPS / LOW-advantage, structural-ceiling
finding exactly. This is a reconfirmation, not a new assessment; the
2026-09-13 section below remains the full current record for that
target and is not rewritten.

### Recommended actions

| Action | Urgency | Owner |
|---|---|---|
| Run a full deterministic `codecompass sync` (no `--budget`, no AI cost) in this checkout to restore `doc_artifacts`/skills/doc-relations from current `HEAD` — the deterministic path needs no cost consent (`decisions/0031`/`0033`) | **Before this repo's own graph is used as a live demo again** — e.g. before any reader is pointed at `ai-docs/README.md`'s worked examples expecting them to run as published, and worth doing ahead of Phase 68's independent release audit in case it spot-checks self-dogfooding claims | lead |
| Separately consider re-running AI enrichment (paid, needs consent) for `anthropic`/`rich`/`typer` — the 2026-09-11-recorded enriched state is gone from this checkout's graph | Low — no upcoming phase (67–70) reads enrichment text as evidence | lead (cost/consent decision) |
| No `context-gaps/` candidate filed — this is a re-sync/staleness finding about a local generated artifact, not an un-representable relationship | — | — |
| Ledgerkit CG-002 — no action; confirmed fixed via today's live spot-check | — | — |

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
