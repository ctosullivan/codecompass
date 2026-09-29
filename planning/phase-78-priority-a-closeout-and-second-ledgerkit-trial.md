# Phase 78 — Priority A backlog rationalisation + second Ledgerkit validation trial

**Status: planned. Planning only — implementation (dispatching agents,
touching Ledgerkit, changing CodeCompass code) does not begin until this
plan is reviewed and approved.**

Direct user request, 2026-09-29: audit every still-open Priority A item
and related backlog/context-gap entry, rationalise their disposition, and
design (not yet run) a second, differently-shaped Priority A Ledgerkit
validation trial that specifically tests whether the first-party
*relationship* capability Phase 77 deliberately deferred is actually
needed — closing with an explicit Priority A exit decision once the
trial's real evidence exists.

---

## 0. Verified current state (read live for this plan, not assumed)

- **CodeCompass HEAD:** `012a92a` on `main`, working tree clean. Phases
  73, 74, 75, 76 (incl. corrective pass), and 77 are all `done` in
  `planning/ROADMAP.md`, independently audited (`release-phase-auditor`
  PASS or PASS WITH NON-BLOCKING OBSERVATIONS on each), and pushed to
  `origin`. Full suite 733 passed / 2 skipped, `ruff check .` clean,
  `check_user_docs.py --strict` / `check_knowledge_base.py` clean
  (re-confirmed at Phase 77's own completion audit,
  `planning/retros/_audit-phase-77.md`).
- **`decisions/0062`** (Phase 72) is the live governing ADR for post-v1
  priorities: task-context completeness first (Priority A), ordered
  A-F, GATE DD explicitly *not* resolved by that ADR — individual
  `context-gaps` candidates stay exactly at their evidence status, no
  promotion on qualitative narrative alone.
- **Priority A's evidentiary history**, read directly from
  `planning/ROADMAP.md`/`CONTEXT.md`/`planning/context-gaps/inbox.md`,
  not summarised from memory:
  - Phase 73: `CG-006` (filename-matching) — **done**, detection fix,
    Stage-C/GATE-DB scale.
  - Phase 75: real Ledgerkit task (hledger `cur:` query-term design),
    baseline vs. treatment, independent `context-evaluator` verdict
    **PASS WITH GAPS, advantage LOW**. `CG-001`'s provisional `recurred`
    call was made, then reverted back to `candidate` by an independent
    `knowledge-curator` re-verification (the report's own
    `context-evaluator` section had already recommended
    cross-reference-not-promotion using `CG-001`'s own established
    precedent — a second instance of the *same broader hypothesis* on a
    *different concrete edge* is not the same as this entry's own edge
    recurring). New gap `CG-009` filed.
  - Phase 76: Git repository topology (worktrees + submodules) — **done**
    including its corrective pass. Independent `context-evaluator`
    verdict **PASS WITH GAPS, advantage MODERATE** — the strongest
    Priority A result to date. New gaps `CG-010`/`CG-011` filed.
  - Phase 77: first-party source/symbol awareness (`CG-009`'s own fix) +
    `codecompass-template` — **done**. Independent `context-evaluator`
    verdict **PASS WITH GAPS, advantage LOW** (Ledgerkit + CodeCompass
    dogfooding). `CG-009` reassessed and resolved
    (`promoted-to-roadmap`). Plan's own §13 names the deferred follow-on
    explicitly: first-party *relationships*
    (`source_file → imports`, `source_symbol → references/calls`,
    `test → tests`, `doc → documents`) — "the most likely path to a
    genuine `CG-001`-shaped trial", **not committed to, not scoped, not
    started**.
- **Verified directly in the real schema** (`src/codecompass/graph.py`,
  read for this plan): `source_files`/`source_symbols` exist, both with
  no `vendor_id` FK, occurrence-based symbol identity, five-value
  `exposure`, five-value `symbol_index_status`. **No edge table of any
  kind exists between two `source_symbols` rows, or between a
  `source_file`/`source_symbol` and anything else, anywhere in the
  schema.** `uses_edges`, `documents_edges`, `skill_mentions_edges`,
  `routes_via_edges`, `depends_on_edges`, `doc_relations_edges` remain
  exactly the six edge tables that existed before Phase 77 — confirmed
  by reading the full `CREATE TABLE` block, not inferred from the
  Phase 77 retro's own account.
- **Ledgerkit** (the reference project): cloned at
  `/home/cormac/projects/ledgerkit`, `HEAD` =
  `6c90b4ca3e6c10951cb400e43db4b90bfccc5909` ("docs: mark Stage C
  [DONE], archive its changelog history"), working tree clean — the
  **same commit** Phase 77's own trial used
  (`planning/reference-projects/ledgerkit/phase-77-fixture-equivalence.md`).
  Ledgerkit has not advanced since. `ROADMAP.md` (Ledgerkit's own,
  read directly): Stage C (Query system) is `[DONE]`, user-confirmed,
  2026-09-27. **Stage D (Reporting — "shared primitives, structured
  output, render/semantics separation") is `[PLANNED]`, zero phases
  started.**
- **Ledgerkit's own test baseline**, run directly for this plan (not
  assumed): `test_commodity_style`/`test_reports`/`test_tags`/
  `test_editor_model`/`test_checks`/`test_cli`/`test_loader`/
  `test_parser`/`test_query` all pass (459+ tests across the modules run
  individually; `test_dataframe`'s 29 are skipped — optional `pandas`
  dependency not installed in this environment, pre-existing and
  unrelated to this plan).

## 1. Problem statement

Priority A (`decisions/0062`) has now run three real-task validations
(Phases 75, 76, 77) plus one detection fix (Phase 73), scoring
LOW/MODERATE/LOW context advantage. Every one of the three trials'
own PASS-WITH-GAPS verdicts traces to a boundary the corresponding
phase *already disclosed in advance*, not a surprise defect — this is a
genuinely different position than "Priority A hasn't been tried yet."
The open question is no longer "does CodeCompass help at all" (yes,
MODERATE at best, LOW typically) but **"has Priority A's own success
criterion now been met well enough that further machinery isn't
justified, or does exactly one more concrete piece of evidence — a
second, differently-shaped trial specifically targeting `CG-001`'s own
motivating hypothesis — still change the answer?"**

Phase 75's own retro explicitly recommended this second trial before any
`CG-001`/`CG-007` funding decision; Phase 77's own plan explicitly
deferred first-party relationships as "the most likely path to a
genuine `CG-001`-shaped trial" without committing to building it. Both
of those recommendations are still live and unclaimed. This phase claims
them, on the condition — stated explicitly by the user commissioning
it — that the relationship capability is **not** pre-built on the
strength of "it sounds useful." It is tested for first, using
current CodeCompass, and only funded afterward if the trial's own real
evidence requires it.

## 2. Goals and non-goals

**Goals:**

1. Produce a complete, evidence-based disposition for every currently
   open Priority A item, `context-gaps` candidate, and related
   deferred/backlog entry (§3).
2. Design (not run) a second, differently-shaped Priority A Ledgerkit
   trial against a genuine, currently-unimplemented Stage D task (§5).
3. Define, in advance of running the trial, exactly what evidence would
   or would not justify building first-party relationship edges — so the
   decision is made by the trial's real result, not decided here by
   assertion (§4, §7).
4. Define the Priority A exit-decision gate itself: the two possible
   end-states and the precise evidence each one requires (§7.2).
5. Specify the exact `ROADMAP.md`/`CONTEXT.md` changes this planning
   commit makes now, and what further changes happen at closeout
   depending on which branch of §7.2 fires (§12).

**Non-goals (explicitly out of scope for this planning phase):**

- No agent is dispatched, no Ledgerkit code is touched, and no
  CodeCompass code is written by this phase's own plan-commit. That
  begins only after this plan is reviewed and approved.
- No first-party relationship schema/capability is designed or built
  here. §4 defines the *test*, not the *implementation* — building it is
  explicitly conditional on §7.2's own evidence gate, and even then is a
  **separate, later, narrowly-scoped phase** (§7.2 Branch B), not part of
  Phase 78's own deliverable.
- `CG-010`/`CG-011` (Git-topology gaps) are dispositioned (§3) but not
  implemented here — they are unrelated to the Ledgerkit trial's own
  task and folding them in would blur this phase's own single question.
- No Priority B-F capability is pulled forward. Where a backlog item's
  evidence genuinely points at another priority, it is re-homed by
  citation, not implemented (§3, per `decisions/0062`'s own re-homing
  table).
- The chosen Ledgerkit task (§5.1) is picked because it is genuinely
  useful, currently-unimplemented Stage D work Ledgerkit's own roadmap
  already calls for — not invented to flatter CodeCompass. If running the
  trial surfaces that the task needs a Ledgerkit-side change *in order to
  make evaluation easier*, the task is abandoned in favour of a
  different one, per the reference-project protocol's own subordination
  rule (`reference-project-protocol.md` §2.3).

## 3. Priority A backlog / context-gap disposition audit

Every entry below was re-read in full from `planning/context-gaps/inbox.md`
and `planning/pre-v1-disposition.md` directly for this plan, not taken
from a prior summary.

| Item | Current status (verified) | Disposition this phase | Rationale |
|---|---|---|---|
| **`CG-001`** — one feature spread across `src/` modules with no joining edge (Phase 43's own founding Priority A case) | `candidate`, single-edge/single-observer, after Phase 75's provisional `recurred` call was independently reverted (Phase 75 `knowledge-curator` triage) | **Incorporated into this phase's own trial (§5.1).** The chosen Ledgerkit task is structurally the same shape (parser.py as producer, reports.py/models.py/cli.py as consumers, no mechanical edge joining them) on a different concrete instance, different project, different observer — if the trial's `context-evaluator` independently confirms this specific edge shape recurs, that is this entry's own second, genuinely-separate instance (not a broader-hypothesis echo, which this entry's own three prior triage passes have consistently declined to count). If it does not recur (e.g. the agents don't need to trace the producer/consumer chain by hand, or CodeCompass's existing `query source`/`query source-symbol` already makes the chain easy to find), that is equally real evidence the other way. |
| **`CG-002`** — `dev-docs/` glob coverage | `promoted-to-roadmap`, resolved Phase 62 | No action — already closed, unrelated to this phase. |
| **`CG-003`** — external hledger manual has zero representation (fetch/vendor a whole new capability class) | `candidate`, single occurrence, `graph-capability` (GATE DD) | **Explicitly deferred, unchanged revisit trigger** ("a second independent occurrence, or independent second filing"). The chosen trial task (§5.1) is pure internal-model work — it does not need the external hledger manual at all, so this trial cannot produce new evidence for or against it. Funding an external-fetch capability on this phase's own narrow evidence would repeat exactly the premature-generalisation `decisions/0062` already declined to do. |
| **`CG-004`/`CG-005`** — `mentions_artifact` spec-doc-to-spec-doc / pinned-reference provenance | `promoted-to-roadmap`, resolved Phases 54c | No action — already closed. |
| **`CG-006`** — filename-based `mentions_artifact` matching | `promoted-to-roadmap`, resolved Phase 73 | No action — already closed. |
| **`CG-007`** — symbol-level cross-references between *pinned reference-doc excerpts themselves* | `candidate`, single occurrence, `graph-capability` (GATE DD) | **Explicitly deferred, unchanged revisit trigger** (second independent occurrence — a different pair of pinned excerpts, or a different reference project). Distinct from `CG-001`: this concerns two `spec_doc` rows referencing each other by *shared code-symbol vocabulary inside pinned reference material*, not first-party project source. The chosen trial task ingests no pinned reference material, so it cannot produce new evidence here either. |
| **`CG-008`** — external-adapter symbol ingestion | `promoted-to-roadmap`, resolved Phase 62 | No action — already closed. |
| **`CG-009`** — zero first-party-source symbol path | `promoted-to-roadmap`, resolved Phase 77 | No action — already closed. Its own forward-looking note (method-level/class-body symbol extraction is a real but currently-disclosed, non-blocking limitation) is carried forward unchanged, not re-opened — the chosen trial task (§5.1) is itself top-level-declaration work (a new parser function, a new dataclass-consuming function, a CLI command), so it does not depend on method-level extraction and cannot by itself force that question either way. |
| **`CG-010`** — submodule staged-vs-checkout pin ambiguity | `candidate`, two-agent-same-instance corroboration (not yet `recurred` per this entry's own consistently-applied bar), `detection-improvement` — already recommended by `knowledge-curator`'s own Phase 76 triage as "a strong candidate for scheduling as a small phase on its own narrow terms... without needing to wait for a second occurrence" | **Ready to fund now; recommend as its own small, standalone Priority A phase, separate from Phase 78.** It is Git-topology-shaped (Phase 76's own capability), unrelated to the Ledgerkit Stage D task this phase's trial uses, and bundling it in would blur Phase 78's single question (does Priority A need first-party relationships) with an unrelated, already-decided, already-small fix. Not implemented by this plan. |
| **`CG-011`** — sibling worktree staleness has no inline signal | `candidate`, first occurrence, `graph-capability` | **Explicitly deferred, unchanged revisit trigger** (a second, independent instance — a different repository or a different agent hitting the same staleness gap unprompted). Same reasoning as `CG-010` for why it is out of this phase's own scope even once evidenced — not evidenced yet regardless. |
| **Phase 24** — project-root REPL routing | `deferred` (`decisions/0048`) | **Unchanged.** No evidence from Phases 75-77 touches project-root routing specifically; `pre-v1-disposition.md` §3's own trigger ("reference-project evidence showing project-root context routing is a recurring real need") is not met by this phase's own planned trial either (the chosen task does not involve `codecompass chat` or project-root session routing). |
| **Phase 25** — MCP server | `deferred` (`decisions/0048`) | **Unchanged.** Orthogonal (transport/protocol concern), per `pre-v1-disposition.md` §4. |
| **Phase 50 remainder** — shared-agent context/entry-point improvements | `not funded` | **Unchanged.** No new Stage-C-shaped evidence exists for this specific item; `pre-v1-disposition.md` §6's own trigger stands. |
| **`L-067`** (retained, not promoted) — binary-first-guess and live-verify-natural-key plan-design heuristics from Phase 77 | `retained` (process learning, not a Priority A capability item) | Not a Priority A backlog item — no disposition needed here; carried by the ordinary learning lifecycle (`planning/learnings/inbox.md`), unaffected by this phase. |

**Net effect of this audit:** every open Priority A item either (a) is
already resolved (no action), (b) genuinely needs a second occurrence
this phase's own trial cannot manufacture and should not manufacture
artificially (`CG-003`, `CG-007`, `CG-011`, Phase 24/25/50 — left alone,
unchanged triggers), (c) is a small, already-fundable, unrelated fix
correctly kept out of this phase's own scope (`CG-010`), or (d) is
exactly the one hypothesis (`CG-001`) this phase's own trial is designed
to test for real (§4, §5). Nothing is silently dropped; nothing is
funded on narrative alone.

## 4. The `CG-001` / first-party-relationship hypothesis — what counts as evidence, defined before the trial runs

Per the user's explicit instruction, first-party relationship indexing
is **not** pre-built because it looks obviously useful. This section
defines, in advance, exactly what the trial (§5) would need to show to
justify it — so that whichever way the result falls, this section's own
criteria (not a post-hoc rationalisation) decide it.

**The hypothesis, precisely stated** (from `CG-001`'s own filing,
`conditional-generalisation.md` §2.6): a real development task requires
tracing a producer/consumer or "one feature, several modules" chain that
CodeCompass's own graph has no edge for, and an agent must reconstruct
that chain by hand, at real cost, in a way that isn't already answered by
existing capabilities (`query source`/`query source-symbol`,
`query relations`, `query symbol`, the generated Skill).

**Evidence that would justify a follow-on (Branch B, §7.2):**

- The treatment agent (with current CodeCompass, including Phase 77's
  `query source`/`query source-symbol`) is independently confirmed by
  `context-evaluator` to have spent material, avoidable effort
  reconstructing a real producer→consumer chain among Ledgerkit's own
  first-party modules that CodeCompass's *existing* surfaces could not
  answer even in combination (e.g. `query source-symbol ReportSpec`
  correctly locates the dataclass, but nothing tells the agent which
  functions in `reports.py`/`cli.py` are its real callers/consumers, and
  the agent had to `grep`/read by hand to find out) — **and** this cost
  was not merely "one grep away" (Phase 75's own `L-027`
  diligence-variance and Phase 77's own advantage-LOW precedent both
  show that a well-organised, well-named codebase can make a manual
  trace cheap regardless of tooling; the bar is *material* difficulty,
  not "the graph theoretically doesn't have this edge").
- This is the **second, independent, genuinely-separate-edge** occurrence
  of `CG-001`'s own hypothesis (a different project, a different concrete
  producer/consumer chain, a different phase) — satisfying
  `context-gaps/README.md`'s own recurrence bar as this entry's own three
  prior triage passes have consistently applied it (same edge/hypothesis
  recurring, not a broader-theme echo).

**Evidence that would close/narrow the hypothesis (Branch A, §7.2):**

- The treatment agent completes the chain-tracing step with existing
  Phase-77 surfaces (`query source-symbol`, direct file reads guided by
  `symbol_index_status`/`exposure` metadata) at a cost the independent
  `context-evaluator` rates no worse than the baseline agent's own direct
  exploration — i.e. advantage LOW/no-material-difference on exactly the
  producer/consumer question `CG-001` names, the same honest outcome
  Phase 75 and Phase 77 both already produced on their own different
  tasks.
- Or: the task simply does not require tracing an intra-project
  producer/consumer chain at all (possible if the design questions turn
  out to be self-contained within one or two files) — in which case the
  trial is evidence-neutral on `CG-001` specifically (still valid
  evidence for the trial's other evaluation criteria, §6).

**What would NOT be treated as evidence either way:** the trial's overall
advantage rating alone (LOW/MODERATE/HIGH). Priority A's last three
trials all rated LOW-to-MODERATE for reasons unrelated to `CG-001`
specifically (stale citation-chain, documented top-level-only symbol
scope, small-well-organised-corpus ceiling) — an undifferentiated
low/moderate score this time would not, by itself, tell us whether
`CG-001`'s specific hypothesis was tested and failed, or never actually
came up. §6's rubric requires the evaluator to answer the `CG-001`
question explicitly and separately from the overall verdict.

## 5. Ledgerkit trial design

### 5.1 Task selection — verified real, currently-unimplemented Stage D work

**Selected task: implement journal-comment-based `ReportSpec` parsing**
(`; report` / `; end report` syntax), the exact item Ledgerkit's own
`dev-docs/api-spec.md` names as `[DEFERRED — Milestone 3]` and its own
`ROADMAP.md` reclassifies to **Stage D (Reporting)**, `[PLANNED]`, zero
phases started.

**Why this task, verified directly against the live repository (not
assumed from the roadmap's own prose):**

- `ledgerkit/models.py` already defines `ReportSpec`/`ReportSection`
  (frozen dataclasses, stable since Milestone 2) and
  `reports.py::balance_from_spec(journal, spec, query=None)` already
  consumes a `ReportSpec` to produce a real `list[ReportSectionResult]`
  — the **consumer side already exists and is stable**.
  `dev-docs/api-spec.md`'s own `ReportSpec` entry states explicitly: "In
  Milestone 2, specs are constructed programmatically only" — confirmed
  live: grepping `ledgerkit/parser.py`, `reports.py`, and `cli.py` for
  `; report`/`end report`/journal-comment spec parsing found **zero**
  matches anywhere. The **producer side (parsing the comment syntax out
  of a journal file into a real `ReportSpec`) does not exist at all.**
- `balance_from_spec` is also **not wired into the CLI at all** —
  grepping `cli.py` found no reference to it. A real implementation of
  this task therefore genuinely spans: `parser.py` (new comment-directive
  recognition — the producer), `models.py` (validating the parsed
  `ReportSpec`/`ReportSection` shape, if any adjustment is needed),
  `reports.py` (the existing consumer, `balance_from_spec` — does it need
  any change to accept comment-declared specs, e.g. around error
  handling for a malformed spec?), `cli.py` (a new way to invoke a
  comment-declared report — the CLI-integration/consumer-of-the-consumer
  side, and the genuine open design question of how it composes with the
  already-wired `-q`/`--query` flag: does a journal-comment-declared
  report also accept command-line filtering on top?), `tests/`
  (`test_parser`, `test_reports`, `test_cli`), and `docs/`
  (`dev-docs/api-spec.md`'s own `[DEFERRED]` note, `ROADMAP.md`'s Stage D
  row).
- This is a genuine multi-module producer/consumer task with a real,
  currently-undecided design question at the seam (query-flag
  composition) — not a synthetic benchmark, and not a task invented to
  flatter CodeCompass. It is real, currently-blocking, already-scheduled
  Ledgerkit work that both arms would plausibly be asked to do in the
  ordinary course of Stage D.
- It is structurally the same shape as `CG-001`'s own founding case
  (a feature spread across producer/consumer modules with no mechanical
  edge joining them, §4) — chosen deliberately for this reason, not
  incidentally.

**Fallback candidate, if live re-inspection at trial time finds this task
has moved or is no longer suitable** (per
`reference-project-protocol.md` §2.3's subordination rule): `stats:
per-reporting-interval output, alongside report-engine consolidation` —
the other backlog item `ROADMAP.md` explicitly reclassifies to Stage D.
Weaker fit (it touches fewer distinct producer/consumer seams) — used
only if the primary task turns out to be blocked or already claimed by
real Ledgerkit development between now and trial dispatch.

**Task framing given to both agents** (design-through-implementation,
matching Phase 75's own precedent of real code landing, not a design-doc
exercise): "Implement journal-comment-based `ReportSpec` parsing per
Ledgerkit's own Scope→Plan→Domain→Design→Implement methodology
(`CLAUDE.md`), closing the `[DEFERRED — Milestone 3]` note in
`dev-docs/api-spec.md`'s own `ReportSpec` section and Stage D's
`ROADMAP.md` backlog row. Decide and implement: the comment syntax's
exact grammar, how a malformed/incomplete spec block is reported (parser
error vs. silent skip — matching `parser.py`'s existing `ParseWarning`
convention), how the parsed `ReportSpec` reaches a report (a new CLI
subcommand/flag vs. an implicit auto-run), and whether/how it composes
with the existing `-q`/`--query` CLI filter. Add tests. Update
`dev-docs/api-spec.md` and `ROADMAP.md`'s Stage D row."

### 5.2 Frozen commit and scratch-clone design

- **Frozen Ledgerkit commit:** `6c90b4ca3e6c10951cb400e43db4b90bfccc5909`
  — the current real `HEAD`, unchanged since Phase 77's own trial used
  the identical commit. No advance needed; re-verify at dispatch time
  that Ledgerkit's own upstream has not moved (if it has, re-pin and
  record the new SHA before dispatch, per the reference-project
  protocol's own "always recorded, never latest" rule).
- **Seed-then-fork design** (Phase 76/77 precedent, not reinvented): one
  seed clone at the frozen commit, forked into `ledgerkit-baseline` and
  `ledgerkit-treatment` before either is touched further. `codecompass
  sync` (Phase 77's first-party-source-aware version) is run in the
  treatment clone only, producing a real, synced `context-graph.db` plus
  the generated `.claude/skills`/`.claude/commands` artifacts; the
  baseline clone gets neither.
- **Pre-dispatch fixture-equivalence check**, persisted as
  `planning/reference-projects/ledgerkit/06-fixture-equivalence.md`
  before either agent is dispatched: confirm both clones' `HEAD` matches
  the frozen SHA, and `diff -rq` (excluding `.git`/`context-graph.db`/
  the generated `.claude/` artifacts) shows the treatment clone's own
  CodeCompass artifacts as the *only* difference — exactly Phase 77's
  own verified pattern.

### 5.3 Dispatch design

- **Baseline agent:** fresh `general-purpose` agent, dispatched against
  `ledgerkit-baseline`, ordinary repository/tool access (read files,
  `grep`, run the test suite, read `git log`/`git blame`) — **no
  CodeCompass** (no `codecompass` CLI invocation of any kind; the
  baseline clone has no synced `context-graph.db` to query even if it
  tried).
- **Treatment agent:** fresh `general-purpose` agent, dispatched against
  `ledgerkit-treatment`, the same task framing (§5.1), the same ordinary
  access, **plus** current CodeCompass (`query source`/`query
  source-symbol`, `query relations`, `query symbol`, `query vendor`, the
  generated Skill/`/discovery` slash command — every surface Phase 77
  shipped, none disabled or restricted).
- **Read-scope symmetry** (`L-062`, mandatory per the reference-project
  protocol §2.2): the dispatch prompt states explicitly, for **both**
  arms, that reads are scoped to the agent's own assigned clone's own
  tree only — no reading the other arm's clone, no reading this
  CodeCompass repository itself, no reading `planning/reference-projects/
  ledgerkit/` (which would leak Phase 75/77's own prior findings about
  this exact codebase). Both arms may run Ledgerkit's own test suite and
  read Ledgerkit's own `dev-docs/`/`ROADMAP.md` freely — that is ordinary
  access to the assigned clone's own tree, not a leak.
- **Agent-report-to-disk discipline** (`L-064`/`agent-led-workflow.md`
  step 5, confirmed working at Phase 77 via `L-066`): both the baseline
  and treatment agents' full reports are written to disk immediately on
  receipt, before drafting the `context-evaluator` dispatch prompt.
- **Independent `context-evaluator` assessment**, dispatched after both
  reports exist, inspecting the treatment clone (and, for the `CG-001`
  question specifically, re-deriving the producer/consumer chain itself
  by direct code reading, the same "establish ground truth directly"
  discipline Phase 77's own evaluator applied when it re-ran the failing
  `to_dataframe` query itself) — never trusting either agent's own
  self-report of how hard the task was.

### 5.4 Reports/artifacts this trial produces

- `planning/reference-projects/ledgerkit/06-fixture-equivalence.md`
  (pre-dispatch check, §5.2).
- `planning/reference-projects/ledgerkit/06-stage-d-reportspec-baseline-report.md`.
- `planning/reference-projects/ledgerkit/06-stage-d-reportspec-treatment-report.md`.
- `planning/reference-projects/ledgerkit/06-stage-d-reportspec-priority-a-validation.md`
  (the combined evaluation report, following the exact structure of
  `04-cur-query-priority-a-validation.md`/`05-phase-77-first-party-
  source-validation.md` — Setup, Criteria assessment against §6's
  rubric, an explicit `CG-001` verdict per §4, Verdict, Context advantage,
  Material gaps/failures, "would this have misled the implementing
  agent," lead + independent-evaluator sections clearly divided).
- `planning/reference-projects/ledgerkit.md`'s own registration record
  updated with this task's pinned commit and result summary
  (`reference-project-protocol.md` §2.1).

Whether Ledgerkit's own real implementation (if the treatment/baseline
agents produce a mergeable result) is offered back to the real Ledgerkit
project is a separate question from this evaluation and is not decided
by this plan — the scratch clones are disposable evaluation fixtures,
per the working-copy discipline (§2.2), not a channel for landing code
in Ledgerkit's own real repository.

## 6. Evaluation criteria

Uses `context-quality-evaluation.md`'s own established rubric unchanged
(Accuracy / Relevance / Completeness / Freshness / Grounding-provenance /
Noise / Safety-trustworthiness, each rated strong/adequate/weak/n/a),
**plus** explicit, named sub-questions instantiating the user's own
requested dimensions for this specific task, so the evaluator addresses
each one directly rather than folding them into a single generic
"Completeness" rating:

| Dimension (user's Objective 5) | Concrete question for this task |
|---|---|
| Relevant source | Did CodeCompass correctly point at `ReportSpec`/`ReportSection`/`balance_from_spec` (via `query source-symbol`) as the existing consumer machinery, without the agent needing to discover it by grep first? |
| Relationships | Could the agent determine, via CodeCompass alone, which functions in `reports.py`/`cli.py` already reference `ReportSpec`, and which do not yet call `balance_from_spec`? (This is `CG-001`'s own question, §4.) |
| Execution/behavioural paths | Did CodeCompass help trace how a report actually gets rendered end-to-end (`balance_from_spec` → `ReportSectionResult` → whatever `cli.py` does with it today, i.e. nothing) — or was this traced by reading code directly regardless of tooling? |
| Tests | Did CodeCompass help identify which existing tests (`test_reports.py`, `test_parser.py`) already cover adjacent behaviour and would need extending, versus which are genuinely new? |
| Docs/ADRs | Did CodeCompass surface `dev-docs/api-spec.md`'s own `[DEFERRED — Milestone 3]` note and `ROADMAP.md`'s Stage D row without the agent needing to grep for them independently? |
| Compatibility evidence | Not directly applicable to this task (no hledger-compatibility question is in scope) — record as `n/a`, not a forced score. |
| Explicit uncertainty | Did CodeCompass ever present a symbol/relationship it could not resolve (e.g. an `unknown`/`internal` exposure, an `indexed_partial` status) honestly, rather than silently omitting it? |
| Duplicated research | Did the treatment agent re-derive anything the baseline agent also had to derive from scratch, despite CodeCompass claiming to already have it (a real safety/trustworthiness failure, not just noise)? |
| Incorrect assumptions | Did any CodeCompass-supplied claim turn out to be wrong when checked against the real code (a real Safety criterion failure)? |
| Overall context advantage | LOW / MODERATE / HIGH per `context-quality-evaluation.md` §5, **reported separately from** the `CG-001`-specific verdict (§4) — the two must not be conflated into one number. |

Verdict format matches precedent exactly: **PASS / PASS WITH GAPS /
FAIL**, **LOW / MODERATE / HIGH** advantage, plus this trial's own
required addition — an explicit **`CG-001` outcome: recurred /
not-recurred / task-not-applicable** line, citing the specific evidence
for whichever of the three it is (§4's own criteria).

## 7. Decision gates

### 7.1 Backlog-item gate (routine, per `context-gaps/README.md`)

For every deferred item in §3 (`CG-003`, `CG-007`, `CG-011`, Phase
24/25/50): unchanged unless this trial's own evidence happens to bear on
one of them directly (checked explicitly at closeout, not assumed not
to — matching the discipline `CG-009`'s own Phase 77 closeout triage
applied when checking the unrelated context-evaluation report before
declaring it didn't weigh against closure).

### 7.2 The Priority A exit decision (the phase's own terminal gate)

Made at closeout, by an independent `knowledge-curator` triage of the
trial's real report (the same non-rubber-stamp discipline that reversed
Phase 75's own provisional `CG-001` call and resolved `CG-009`), not by
the lead's own assertion:

**Branch A — Priority A closed.** Fires if the trial's own `CG-001`
outcome (§6) is **not-recurred** or **task-not-applicable**, consistent
with §4's "evidence that would close/narrow the hypothesis." Rationale
recorded: three real trials (75, 76, 77) plus this one all independently
confirm CodeCompass materially helps (MODERATE once, LOW three times,
never FAIL, never a fabricated/misleading claim), and the one
concretely-scoped candidate for a fourth capability build (`CG-001`'s
relationship edges) was tested for real and did not clear its own
evidence bar even on a task chosen specifically to give it the best
chance. `planning/ROADMAP.md`'s Priority A row is updated to record
closure, its success criterion is stated as met (a `context-evaluator`
PASS-or-PASS-WITH-GAPS record now exists across three structurally
different capability areas — query semantics, Git topology, first-party
source — with an explicit, evidence-checked negative result on the one
remaining open hypothesis), and Priority A is not reopened absent new
evidence of a different, not-yet-tested shape.

**Branch B — one narrowly-scoped final follow-on.** Fires only if the
trial's own `CG-001` outcome is **recurred**, per §4's own explicit
evidence bar (a second, genuinely separate edge instance, materially
costly, not beaten by ordinary diligence). If it fires, the follow-on is
scoped to **exactly** the smallest concrete edge shape the trial actually
evidenced — not a general relationship-graph capability. Candidate
shape, informed by Phase 77's own plan §13 but **not pre-committed**: a
single new edge table for the *specific* relationship kind the trial's
own evidence names (e.g. `source_symbol → references source_symbol`
within one project, detected the same way `uses_edges` already detects
vendor usage — a within-project reuse of an existing detection technique,
not a new ontology). The follow-on gets its own `planning/phase-N-*.md`
(`CLAUDE.md` §1) and its own validation, per the user's own instruction —
it is not implemented as part of Phase 78's own closeout.

**Either branch is a legitimate, planned outcome of this phase — this
plan does not presuppose which one fires.**

## 8. Human decision gates

**One real judgment call was made in writing this plan, not a blocking
ambiguity:** the choice of §5.1's specific task (journal-comment
`ReportSpec` parsing) over the fallback (`stats` per-interval output).
This was resolved by direct evidence (live-reading Ledgerkit's own
`api-spec.md`/`ROADMAP.md`/`parser.py`/`reports.py`/`cli.py`, confirming
the producer side genuinely does not exist and the consumer side is
genuinely stable) rather than by assertion, and is presented here for
review rather than treated as requiring a stop before the plan could be
written — consistent with `CLAUDE.md` §1's own "pause only if an
assumption not already settled is surfaced" bar. If reviewed and
rejected, the fallback task (or a fresh one, re-verified live at dispatch
time per §2.3's subordination rule) is substituted without otherwise
changing this plan's design.

**No other human-decision gate was found.** In particular, §7.2's own
branch choice is explicitly *not* a gate requiring a decision now — it is
designed to be decided later, by real evidence the trial itself produces,
which is the entire point of running the trial before committing to
either outcome.

## 9. Files expected to change

### This planning commit (now)

- **New:** this file,
  `planning/phase-78-priority-a-closeout-and-second-ledgerkit-trial.md`.
- **`planning/ROADMAP.md`:** new Phase 78 row (status `planned`); Priority
  A's own status cell gains a pointer to this phase as the currently
  planned closeout step (not yet resolved either direction).
- **`planning/CONTEXT.md`:** current-state section updated — Phase 78
  planned, pending review; next concrete step named explicitly (user
  review, then §5's trial dispatch).

### At trial-execution time (a later commit, not this one)

- The five report files named in §5.4.
- `planning/reference-projects/ledgerkit.md` registration update.
- Candidate learnings filed as they occur (`planning/learnings/inbox.md`).

### At closeout (a later commit, not this one), branch-dependent

- **Branch A:** `planning/ROADMAP.md`'s Priority A row updated to record
  closure and its rationale; `CG-001`'s own inbox entry gets its
  closeout triage note (either a genuine `recurred`→`not-recurred`-style
  final disposition, if that vocabulary fits, or a closing cross-reference
  matching its own established precedent for declining promotion);
  `decisions/` gains a new ADR recording the Priority A closure decision
  and its evidentiary basis (a genuine non-obvious tradeoff — closing an
  entire priority track — per `CLAUDE.md` §2).
- **Branch B:** a new `planning/phase-79-<slug>.md` (or next free number)
  is written for the narrowly-scoped follow-on, per `CLAUDE.md` §1 — not
  implemented inside Phase 78's own closeout commit.
- Either branch: phase retro, learning triage, docs drift audit,
  independent `release-phase-auditor` completion audit, terminal
  `roadmap-context-curator` reconciliation — the full standard closeout
  sequence (`CLAUDE.md` §5), unchanged by this plan.

## 10. Definition of Done for Phase 78

Phase 78 is **not** implementation of a new CodeCompass capability — its
own "done" state is reached once:

1. This plan is reviewed and approved (or amended and re-reviewed).
2. The trial (§5) has actually run: both agents dispatched, both reports
   written to disk, fixture-equivalence confirmed, independent
   `context-evaluator` assessment completed and persisted.
3. §7.2's decision gate has been applied by an independent
   `knowledge-curator` triage (not the lead's own assertion), and its
   outcome (Branch A or B) is recorded with the evidence named in §4/§7.2.
4. §3's backlog disposition table has been re-confirmed still accurate at
   closeout (no new evidence from the trial silently contradicts a
   disposition made here without updating it).
5. The standard per-phase closeout sequence (`CLAUDE.md` §5) has run in
   full against whichever branch fired: docs drift audit, phase retro,
   learning triage, independent `release-phase-auditor` completion audit
   (PASS or PASS WITH NON-BLOCKING OBSERVATIONS), terminal
   `roadmap-context-curator` reconciliation.
6. `planning/ROADMAP.md` reflects the real outcome (Priority A closed, or
   Priority A still open pending the named follow-on phase) — not marked
   `done` until every one of the above genuinely holds, per `CLAUDE.md`
   §5's own terminal-action rule.

**This plan file's own Status line only reaches `done` when Phase 78
itself does — writing and approving this plan is not, by itself, the
phase's completion.**

## 11. Rollback / cleanup requirements

- Both Ledgerkit scratch clones (`ledgerkit-baseline`, `ledgerkit-treatment`)
  are disposable, outside this repository's own tree, never added to
  `vendor.toml`/`context-graph.db`/git — cleaned up (deleted) once the
  evaluation reports are persisted, per the working-copy discipline
  (§5.2) and this project's own established scratch-cleanup discipline
  (confirmed clean at every prior phase's completion audit).
- No generated CodeCompass runtime artifacts (`context-graph.db`,
  `.claude/skills/`, `.claude/commands/`) are committed anywhere by this
  phase, in either this repository or Ledgerkit's own.

## 12. Verification commands

- `.venv/bin/pytest -q` (CodeCompass's own suite — unaffected by this
  planning-only commit, expected unchanged at 733 passed / 2 skipped).
- `.venv/bin/ruff check .`
- `python3 scripts/check_user_docs.py --strict`
- `python3 scripts/check_knowledge_base.py`
- At trial time: Ledgerkit's own test suite run in both scratch clones
  independently, both expected to pass before and after either arm's own
  implementation work (a regression in either arm is itself a finding,
  not silently ignored).
