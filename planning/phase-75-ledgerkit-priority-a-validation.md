# Phase 75: Priority A Ledgerkit validation — real task, baseline vs. CodeCompass-assisted — plan

**Status:** in progress (2026-09-27).

Direct user request, following Phase 73/74's own implementation work
and a separate root-cause investigation/fix into a phase-closeout
defect (`planning/retros/_root-cause-closeout-defect.md`). This phase
is an **evaluation/research phase, not an implementation phase** — its
job is to determine, with real evidence, whether current CodeCompass
(post-Phase-73) gives a fresh agent a material task-context advantage
on a genuine Ledgerkit development task, and to decide from that
evidence — not from Phase 72's own anticipation — whether `CG-001`,
`CG-007`, or something smaller is the actual next justified capability.

## 0. What this phase is, and isn't

**Not implementation.** No new CodeCompass capability is built in this
phase unless the experiment itself reveals a genuinely tiny, necessary
correction required to make the evaluation valid — and if so, that
correction is documented explicitly as an evaluation-enabling fix, not
silently folded into the treatment being measured.

**Follows the project's own established reference-project protocol**
(`planning/v1-redefinition/reference-project-protocol.md` §2) and
context-quality-evaluation discipline
(`planning/v1-redefinition/context-quality-evaluation.md`), reusing the
Phase 54b baseline-vs-treatment shape (two independent fresh agents,
neither the lead) rather than §2.4's "lead attempts the task" shape —
because the explicit question here is context-quality comparison, the
exact case Phase 54b's own shape was designed for, and because the
lead already has extensive prior knowledge of Ledgerkit's own codebase
from this session's own research (task selection below), which would
contaminate a lead-attempts-the-task run in a way it doesn't
contaminate two agents dispatched fresh with no access to this
conversation.

**Explicit acknowledgment of `L-027`'s own limitation up front**: a
single-trial (N=1-per-condition) baseline/treatment comparison cannot,
by construction, separate "the tool's real contribution" from "one
agent read more carefully than the other." Both dispatched agents are
required to log their own raw file-access history (not just their
final report), so `context-evaluator` can check this explicitly per
`context-quality-evaluation.md` §1's own standing rule, rather than
crediting CodeCompass for anything either agent could equally have
found by reading the same raw source.

## 1. Task selection

**Selected task: implement hledger's `cur:` query term in Ledgerkit's
query engine** (`ledgerkit/query/`).

### 1.1 Why this task is genuine, not invented

Confirmed live against the real local checkout (`/home/cormac/projects/ledgerkit`,
`HEAD` = `6c90b4c`, dated 2026-09-27 — today):

- Ledgerkit's own `ROADMAP.md` shows Stage C (Query system) marked
  `[DONE]` (2026-09-27, user-confirmed) — the query engine (`ledgerkit/query/`:
  AST, parser, evaluator, regex handling) is real, complete, and already
  wired into `balance`/`register`/`accounts`/`stats`/`print` via `-q`/`--query`.
  Stage D (Reporting) is `[PLANNED]`, not yet scoped into its own phase
  plan — there is no already-named "next task" for Stage D to prefer
  over a real, explicitly-deferred Stage C backlog item.
- `cur:` is named, explicitly and repeatedly, across Ledgerkit's own
  planning corpus as deferred, unimplemented work: `dev-docs/hledger-compatibility.md:276`
  ("`cur:REGEX` ... Not implemented — Stage C follow-on work"),
  `dev-docs/planning/core-redefinition/07-query-regex.md:19,27`, and
  named alongside the already-completed `tag:` term family as a
  "separate, unstarted" item in `23-tag-query-matching-design.md:850`.
- **Not already exhaustively documented**: unlike `tag:` (which has its
  own dedicated design docs `19`/`20`/`23`/`24` and five compat-register
  entries), `cur:` has no dedicated design document and exactly one,
  tangential compat-register entry (`LK-UNSUP-MULTICURRENCY-001.yaml`,
  about valuation/conversion, not commodity matching). Real design and
  discovery work is genuinely still needed — this task does not
  trivialise the comparison.
- **Real upstream hledger behaviour exists to discover**: real hledger
  (`/home/cormac/projects/hledger`, `hledger-lib/Hledger/Query.hs:320`)
  implements `cur:` as a literal alias for `sym:` (`Sym` constructor,
  case-insensitive regex anchored `^...$`) — a real, non-obvious
  semantic fact (`cur:` and `sym:` are synonyms upstream) a fresh agent
  must discover, not something either baseline or treatment is handed.
  Ledgerkit itself has no `sym:` term at all yet — confirmed by grep —
  so the task also requires deciding whether `cur:` needs its own
  independent implementation or should establish `sym:` as the primary
  term with `cur:` as an alias, mirroring upstream's own choice.
- **A real, sibling implementation exists to learn from**: `tag:`'s own
  nine-phase implementation arc (Stage C Phases 4-9) is the closest
  analog — a real precedent for how a new query-term family gets
  designed, parsed, evaluated, and compat-registered in this codebase.

### 1.2 Why this task exercises the right dimensions

Matches most of the user's own preferred dimensions: source
implementation (`ledgerkit/query/ast.py`, `parser.py`, `eval.py`,
`regex.py`), tests (the query test suite, plus whatever compat-register
entries a real implementation would need), behavioural semantics (what
"commodity" means for a multi-commodity `Posting`/`Amount`, and whether
`cur:` inherits `tag:`'s own precedence/combination rules), command/query
paths (`balance`/`register`/`accounts`/`stats`, exactly where `tag:`
and `depth:` already integrate), compatibility expectations (the real
`cur:`≡`sym:` upstream aliasing fact), sibling implementations (`tag:`'s
own nine-phase arc as the direct precedent), and upstream hledger
behaviour (real `Query.hs` source, real `hledger.1` man-page text).

### 1.3 What the two dispatched agents are actually asked to do

**Not** to implement `cur:` (that would make this an implementation
phase and cross baseline/treatment contamination risk). Both agents are
asked to produce the same artifact a real Ledgerkit contributor would
produce *before* writing code: **a grounded understanding of what `cur:`
needs to do, backed by evidence** — equivalent to the design/discovery
work `19-tag-query-semantics-brief.md`/`20-tag-parsing-syntax-brief.md`
represent for `tag:`'s own arc. Concretely, each agent answers:

1. What does `cur:` need to match against (a `Posting`'s commodity? An
   `Amount`'s commodity? Every amount in a multi-commodity posting, or
   just one)?
2. Is `cur:` its own term, or an alias for a new `sym:` term (matching
   upstream), or something else — and what's the evidence either way?
3. Where in `ledgerkit/query/` would the new predicate live, and which
   existing query-term family (`tag:`'s own AST node/parser rule/eval
   function shape) is the right structural precedent to follow?
4. What test cases would prove the implementation correct, and what do
   they need to cover (case-insensitivity, regex vs. substring, multiple
   commodities per posting, interaction with `depth:`/other terms)?
5. What's genuinely uncertain or would need a human/design decision
   before implementation could start for real?

This keeps both runs to a bounded, comparable, non-destructive research
task — real design/discovery work, not implementation — while still
exercising every context-completeness dimension Part 6 of the user's
own request names.

## 2. Setup — clean, independent environments

- Both agents work from a **fresh scratch clone** of the real local
  Ledgerkit checkout, pinned at `6c90b4c` — never the real
  `/home/cormac/projects/ledgerkit` directory itself (read-only source
  only), matching `reference-project-protocol.md` §2.2's own working-copy
  discipline. Each agent gets its **own separate clone** (not a shared
  one), so neither can observe the other's edits/scratch notes even
  accidentally.
- **Baseline agent**: works in its own clone with ordinary tools (`Read`,
  `Grep`, `Glob`, `Bash`, `WebFetch` for upstream hledger docs if
  needed) — no CodeCompass installed/available in that environment, no
  knowledge this evaluation exists.
- **Treatment agent**: works in its own clone with CodeCompass installed
  and already synced against it (`codecompass sync` run once, before
  dispatch, so the treatment agent's own first action can be a query,
  not a sync wait) — instructed to use `codecompass query`/`/discovery`/
  generated Skills as its first move, falling back to ordinary tools
  only where CodeCompass doesn't help.
- Neither agent is told about the other, the hypothesis being tested, or
  this phase's own existence beyond "investigate this task."
- Both agents log their own raw tool-call/file-read history as part of
  their report (per `L-027`'s own requirement) — not just a polished
  final summary.

## 3. Dispatch strategy

1. **Lead** confirms the task selection live (done, §1) and prepares
   both scratch clones + the treatment clone's CodeCompass sync.
2. **Baseline agent** (fresh, general-purpose, no CodeCompass) —
   dispatched first, runs to completion independently.
3. **Treatment agent** (fresh, general-purpose, CodeCompass available) —
   dispatched second, with no access to the baseline's own report.
4. **`context-evaluator`** — independently inspects the real Ledgerkit
   repository directly (establishing its own ground truth, never via
   CodeCompass) and rates the treatment agent's own supplied/discovered
   context per `context-quality-evaluation.md`'s full report structure,
   explicitly checking the `L-027` agent-diligence-variance question
   against both agents' own file-access logs.
5. **Lead**, informed by all three: explicit gap analysis against Part 6's
   dimensions (docs/tests/producers-consumers/siblings/execution-path/
   task-relevance/uncertainty/rediscovery-burden), reassessment of
   `CG-001`/`CG-007`, and the next-phase recommendation.
6. **`docs-reconstructor`** (MODE 1, per-phase drift audit) — likely
   `NO DRIFT` expected (no CodeCompass behaviour changes), confirmed not
   assumed.

## 4. Files created/changed

- `planning/phase-75-ledgerkit-priority-a-validation.md` — this file.
- `planning/reference-projects/ledgerkit/04-cur-query-priority-a-validation.md`
  (or similar, numbered after the existing `00`-`03` files) — the full
  evaluation report: task, baseline result, treatment result,
  `context-evaluator` verdict, gap analysis, `CG-001`/`CG-007`
  disposition.
- `planning/context-gaps/inbox.md` — any new context-gap entries the
  experiment surfaces.
- `planning/learnings/inbox.md` — any candidate learnings.
- `planning/ROADMAP.md` — Phase 75 row; Priority A/B status cells
  updated per the evidence-backed recommendation; `CG-001`/`CG-007`
  dispositions updated in the "Backlog, not absorbed into A-F" table.
- Standard closeout: retro, drift audit report, DoD audit.

**Explicitly not touched**: `ledgerkit/` itself (read-only source for
both agents; no PR, no commit, nothing written back to the real
Ledgerkit checkout or its scratch clones survives past this phase's own
evidence-gathering) — `cur:` is not implemented by this phase.
`src/codecompass/` — no implementation this phase, per §0, unless a
tiny evaluation-enabling correction proves necessary (documented
explicitly if so).

## 5. Verification

1. Both baseline and treatment reports exist, are genuinely independent
   (no cross-contamination — checked by the lead reading both for any
   sign one referenced the other), and include raw file-access logs.
2. `context-evaluator`'s report exists, follows
   `context-quality-evaluation.md`'s own structure, gives an explicit
   PASS / PASS WITH GAPS / FAIL verdict and LOW / MODERATE / HIGH
   advantage rating, and explicitly addresses the `L-027`
   agent-diligence-variance question.
3. The gap analysis explicitly addresses every Part 6 dimension the
   user's own request named (docs/design material, tests-as-evidence,
   producers/consumers, sibling implementations, execution/behavioural
   path, task-oriented relevance, explicit uncertainty, rediscovery
   burden) — not merely a subset.
4. `CG-001` and `CG-007` each receive an explicit, evidence-justified
   disposition (promote/fund, retain, narrow, merge, or reject) — never
   promoted merely because Phase 72 anticipated they might matter.
5. The next-phase recommendation follows from the observed evidence, not
   from roadmap momentum — the plan's own closing section names which
   of Outcomes A-E (per the user's own request) actually occurred.
6. `scripts/check_user_docs.py --strict`, `scripts/check_knowledge_base.py`,
   full `pytest`, `ruff check .` all pass (expected: no `src/` change
   this phase, so no regression risk — but confirmed, not assumed).
7. Reproducibility: another fresh session could re-run this same
   experiment from this plan file's own §1-§3 alone, without needing
   this conversation's own context.
8. Standard closeout: retro, `knowledge-curator` triage,
   `release-phase-auditor` DoD pass — dispatch prompt explicitly
   restates the required persisted report path (`planning/retros/_audit-phase-75.md`),
   per this session's own just-landed `L-060` fix.

## 6. Deferred (explicitly out of scope for this phase)

- Actually implementing `cur:` in Ledgerkit — a genuine follow-up for
  Ledgerkit's own development, not this evaluation.
- Actually implementing whichever CodeCompass capability the evidence
  points toward — that's the *next* phase's own job, planned only after
  this phase's evidence is in.
- Re-litigating Phase 73/74's own already-fixed closeout process (a
  separate, already-completed piece of work this session,
  `planning/retros/_root-cause-closeout-defect.md`).
