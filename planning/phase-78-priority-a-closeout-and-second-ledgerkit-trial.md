# Phase 78 — Priority A backlog rationalisation + second Ledgerkit validation trial

**Status: done (2026-10-02).** The trial ran to an applicable result;
§7.2 Branch A fired (Priority A closed, `decisions/0069`); independent
`release-phase-auditor` completion audit PASS WITH NON-BLOCKING
OBSERVATIONS (`planning/retros/_audit-phase-78.md`). Retro:
`planning/retros/phase-78-priority-a-closeout-and-second-ledgerkit-trial.md`.
Implementation approved and begun 2026-10-02 at
direct user request ("Implement phase 78 plan"). §0's "verified current
state" was re-confirmed live at the start of implementation: CodeCompass
HEAD `d0d8709` (Phases 79/80 and the strict-isolation backlog item have
landed since this plan was written; none bear on this phase's own scope
or re-open it); Ledgerkit still at the identical frozen commit
`6c90b4ca3e6c10951cb400e43db4b90bfccc5909`, working tree clean, no
advance; the §5.1 task re-verified still unimplemented (`grep` for `;
report`/`end report` across `parser.py`/`reports.py`/`cli.py`: zero
matches; `balance_from_spec` still unwired from `cli.py`); Ledgerkit's
own test suite re-run directly, 906 passed / 29 skipped (pandas-optional,
pre-existing, unrelated).

Direct user request, 2026-09-29 (amended 2026-09-29, second revision, to
fix a real exit-gate contradiction, an unresolved backlog-classification
inconsistency, a methodological confound in the trial's own design, a
missing observable-evidence requirement, residual pre-judgment of the
trial's own result, and imprecise evaluation terminology — see the
change log at the very end of this file): audit every still-open
Priority A item and related backlog/context-gap entry, rationalise their
disposition, and design (not yet run) a second, differently-shaped
Priority A Ledgerkit validation trial that specifically tests whether the
first-party *relationship* capability Phase 77 deliberately deferred is
actually needed — closing with an explicit Priority A exit decision once
the trial produces an *applicable* result (§4, §7.2).

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
**LOW / MODERATE / LOW** context advantage — an accurate, trustworthy,
but so far modest track record, not a demonstrated ceiling. Every one of
the three trials' own PASS-WITH-GAPS verdicts traces to a boundary the
corresponding phase *already disclosed in advance*, not a surprise
defect — this is a genuinely different position than "Priority A hasn't
been tried yet." The open question is no longer "does CodeCompass help
at all" (yes, MODERATE at best, LOW typically, across Phases 73-77) but
**"has Priority A's own success criterion now been met well enough that
further machinery isn't justified, or does exactly one more concrete
piece of evidence — a second, differently-shaped trial specifically
targeting `CG-001`'s own motivating hypothesis — still change the
answer?"**

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

**None of the above pre-judges Phase 78's own result.** Phase 78's own
verdict (PASS / PASS WITH GAPS / FAIL), advantage rating (LOW / MODERATE
/ HIGH), and `CG-001` outcome (§4) all remain genuinely open until the
independent evaluation (§5, §6) actually runs. This plan defines *how*
that evaluation will be conducted and judged — not what it will find.

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
   end-states, the precise evidence each one requires, and the
   evidence-neutral (non-deciding) third outcome that must trigger a
   task substitution and re-run rather than either end-state (§4, §7.2).
5. Specify the exact `ROADMAP.md`/`CONTEXT.md` changes this planning
   commit makes now, and what further changes happen at closeout
   depending on which branch of §7.2 fires (§12).
6. Keep two genuinely different questions explicit and never conflated:
   Priority A's own *strategic* completion question (does the track need
   new capability-building machinery) versus *ordinary, already-scoped
   maintenance backlog* within capability Priority A already shipped
   (§3.1) — closing the former never implies the latter stops being
   fundable.

**Non-goals (explicitly out of scope for this planning phase):**

- No agent is dispatched, no Ledgerkit code is touched, and no
  CodeCompass code is written by this phase's own plan-commit. That
  begins only after this plan is reviewed and approved.
- No first-party relationship schema/capability is designed or built
  here. §4 defines the *test*, not the *implementation* — building it is
  explicitly conditional on §7.2's own evidence gate, and even then is a
  **separate, later, narrowly-scoped phase** (§7.2 Branch B), not part of
  Phase 78's own deliverable.
- `CG-010`/`CG-011` (Git-topology gaps) are dispositioned (§3, §3.1) but
  not implemented here — they are unrelated to the Ledgerkit trial's own
  task and folding them in would blur this phase's own single strategic
  question. This does **not** mean they are deferred *pending* Priority
  A's own exit decision: §3.1 classifies `CG-010` as independent,
  already-fundable maintenance backlog, fundable regardless of which way
  §7.2 resolves.
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
| **`CG-010`** — submodule staged-vs-checkout pin ambiguity | `candidate`, two-agent-same-instance corroboration (not yet `recurred` per this entry's own consistently-applied bar), `detection-improvement` — already recommended by `knowledge-curator`'s own Phase 76 triage as "a strong candidate for scheduling as a small phase on its own narrow terms... without needing to wait for a second occurrence" | **Bounded Git-topology maintenance/product-improvement item — independently fundable now, never gated on Priority A's own strategic exit decision (§3.1).** It is unrelated to the Ledgerkit Stage D task this phase's trial uses, so bundling it into Phase 78 would blur this phase's own single strategic question with an unrelated, already-decided, already-small fix. Not implemented by this plan; may be scheduled as its own small phase at any time — whether Priority A ultimately closes (§7.2 Branch A) or gains one more follow-on (Branch B) has no bearing on whether `CG-010` gets funded. |
| **`CG-011`** — sibling worktree staleness has no inline signal | `candidate`, first occurrence, `graph-capability` | **Explicitly deferred, unchanged revisit trigger** (a second, independent instance — a different repository or a different agent hitting the same staleness gap unprompted) — not evidenced yet, unlike `CG-010`. If it ever clears its own recurrence bar, the same maintenance-backlog classification as `CG-010` applies (§3.1): its funding, if any, would likewise never be gated on Priority A's own strategic exit decision. |
| **Phase 24** — project-root REPL routing | `deferred` (`decisions/0048`) | **Unchanged.** No evidence from Phases 75-77 touches project-root routing specifically; `pre-v1-disposition.md` §3's own trigger ("reference-project evidence showing project-root context routing is a recurring real need") is not met by this phase's own planned trial either (the chosen task does not involve `codecompass chat` or project-root session routing). |
| **Phase 25** — MCP server | `deferred` (`decisions/0048`) | **Unchanged.** Orthogonal (transport/protocol concern), per `pre-v1-disposition.md` §4. |
| **Phase 50 remainder** — shared-agent context/entry-point improvements | `not funded` | **Unchanged.** No new Stage-C-shaped evidence exists for this specific item; `pre-v1-disposition.md` §6's own trigger stands. |
| **`L-067`** (retained, not promoted) — binary-first-guess and live-verify-natural-key plan-design heuristics from Phase 77 | `retained` (process learning, not a Priority A capability item) | Not a Priority A backlog item — no disposition needed here; carried by the ordinary learning lifecycle (`planning/learnings/inbox.md`), unaffected by this phase. |

### 3.1 Strategic Priority A closure vs. ordinary maintenance backlog

Two different questions must not be conflated, and this plan keeps them
explicitly separate throughout:

- **Strategic Priority A closure** (§7.2) is the research question this
  phase's trial actually answers: does Priority A's own success
  criterion (task-context completeness) still need new *machinery* —
  specifically, first-party relationship edges (`CG-001`) — or has it
  been met well enough by what already shipped (Phases 73/76/77) that
  building more isn't justified? This is a track-level decision about
  whether to keep investing in *new* Priority A capability-building.
- **Ordinary maintenance/product-improvement backlog** (`CG-010`, and
  `CG-011` if it ever clears its own recurrence bar) is small, additive,
  already-scoped work *within a capability Priority A already shipped*
  (Git topology, Phase 76). This class of work is never gated on the
  strategic question above — a shipped capability keeps taking small,
  independently-evidenced fixes regardless of whether the track that
  originally funded it is still open to *new* capability-building.
  Closing Priority A strategically (§7.2 Branch A) does not mean Git
  topology (or first-party source, or filename-matching) stops being
  maintained; it means no *new* Priority A capability gets built on
  narrative alone going forward, absent fresh evidence of a different,
  not-yet-tested shape.

`CG-010` is dispositioned as ready-to-fund maintenance backlog under this
distinction (§3 table) — not implemented by this plan, not blocked by
§7.2's own outcome either way.

**Net effect of this audit:** every open Priority A item either (a) is
already resolved (no action), (b) genuinely needs a second occurrence
this phase's own trial cannot manufacture and should not manufacture
artificially (`CG-003`, `CG-007`, `CG-011`, Phase 24/25/50 — left alone,
unchanged triggers), (c) is already-evidenced maintenance backlog,
independently fundable regardless of Priority A's own strategic outcome
(`CG-010`, §3.1), or (d) is exactly the one hypothesis (`CG-001`) this
phase's own trial is designed to test for real (§4, §5). Nothing is
silently dropped; nothing is funded on narrative alone.

## 4. The `CG-001` / first-party-relationship hypothesis — what counts as evidence, defined before the trial runs

Per the user's explicit instruction, first-party relationship indexing
is **not** pre-built because it looks obviously useful. This section
defines, in advance, exactly what the trial (§5) would need to show to
justify it — so that whichever way the result falls, this section's own
criteria (not a post-hoc rationalisation) decide it. **Three outcomes are
possible, not two, and they are not symmetric**: two of them
(`recurred`/`not-recurred`) are outcomes of a trial that actually
exercised the hypothesis; the third (`task-not-applicable`) means the
trial did not test the hypothesis at all and therefore cannot be used to
decide anything about it, in either direction.

**The hypothesis, precisely stated** (from `CG-001`'s own filing,
`conditional-generalisation.md` §2.6): a real development task requires
tracing a producer/consumer or "one feature, several modules" chain that
CodeCompass's own graph has no edge for, and an agent must reconstruct
that chain by hand, at real cost, in a way that isn't already answered by
existing capabilities (`query source`/`query source-symbol`,
`query relations`, `query symbol`, the generated Skill).

**Outcome 1 — `recurred` (triggers Branch B, §7.2):**

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
- **This outcome only ever triggers the smallest evidence-supported
  follow-on capability** (§7.2 Branch B) — never a general
  relationship-graph capability, and never implemented as part of this
  phase's own closeout, per the user's own explicit instruction.

**Outcome 2 — `not-recurred` (a precondition for Branch A, §7.2 — subject
to the applicability requirement below):**

- The treatment agent completes the chain-tracing step with existing
  Phase-77 surfaces (`query source-symbol`, direct file reads guided by
  `symbol_index_status`/`exposure` metadata) at a cost the independent
  `context-evaluator` rates no worse than the baseline agent's own direct
  exploration — i.e. advantage LOW/no-material-difference on exactly the
  producer/consumer question `CG-001` names. This is an outcome the trial
  would need to actually produce and evidence for itself, not one assumed
  by precedent from Phase 75/77's own different tasks.
- **This outcome only counts if the task genuinely required tracing a
  producer/consumer chain in the first place** (i.e. it is distinguishable
  from Outcome 3 below). A `not-recurred` verdict reported on a task that
  never exercised the hypothesis at all is not this outcome — it is
  Outcome 3, mislabelled.

**Outcome 3 — `task-not-applicable` (evidence-neutral — does NOT close
Priority A, does NOT justify Branch A, per the user's own explicit
correction to this plan's first draft):**

- The task simply did not require tracing an intra-project
  producer/consumer chain at all (e.g. the design questions turned out to
  be self-contained within one or two files, or the producer/consumer
  relationship was trivial enough that neither arm needed to trace it).
- **This outcome settles nothing about `CG-001` either way.** It means
  this specific trial did not actually exercise the hypothesis it was
  designed to test — not that the hypothesis was tested and failed.
  `task-not-applicable` must **never** be treated as equivalent to
  `not-recurred` for §7.2's own purposes.
- **Required response, before any Priority A exit decision is made**: the
  trial is re-run against the fallback task (§5.1) or, if that has also
  moved or is unsuitable, a fresh, genuinely live-verified Ledgerkit task
  that does exercise a real producer/consumer chain — verified live the
  same way §5.1 verified the primary task's own applicability, never
  decided by assertion. The trial's other evaluation criteria (§6) remain
  valid and are still recorded regardless — only the `CG-001`-specific
  exit gate is blocked until an applicable result exists (§7.2.0).

**What would NOT be treated as evidence either way:** the trial's overall
advantage rating alone (LOW/MODERATE/HIGH). Priority A's last three
trials (75, 76, 77) rated LOW-to-MODERATE for reasons unrelated to
`CG-001` specifically (stale citation-chain, documented top-level-only
symbol scope, small-well-organised-corpus ceiling) — an undifferentiated
low/moderate score this time would not, by itself, tell us whether
`CG-001`'s specific hypothesis was tested and confirmed (Outcome 1),
tested and failed (Outcome 2), or never actually came up (Outcome 3).
§6's rubric requires the evaluator to answer the `CG-001` question
explicitly, as one of these three named outcomes, separately from the
overall verdict.

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

**Fallback candidate — used either if live re-inspection at trial time
finds the primary task has moved or is no longer suitable (per
`reference-project-protocol.md` §2.3's subordination rule), or if the
discovery/design stage itself shows the primary task does not actually
exercise a producer/consumer chain (§4 Outcome 3, which requires a
re-run before any Priority A exit decision can be made, §7.2.0):**
`stats: per-reporting-interval output, alongside report-engine
consolidation` — the other backlog item `ROADMAP.md` explicitly
reclassifies to Stage D. Weaker fit if used as the primary choice (it
touches fewer distinct producer/consumer seams), but real,
live-verified, currently-unimplemented work either way. If both the
primary and fallback tasks turn out inapplicable, a fresh, genuinely
live-verified Ledgerkit task exercising a real producer/consumer chain
is selected before the trial's evidence is treated as informing §7.2 in
any way.

**Task framing given to both agents at the discovery/design stage**
(§5.3.1 — identical wording for both arms; the only difference between
arms is CodeCompass's own availability, never the task text): "Ledgerkit's
own `dev-docs/api-spec.md` marks journal-comment-based `ReportSpec`
parsing (`; report` / `; end report` syntax) `[DEFERRED — Milestone 3]`;
`ROADMAP.md` reclassifies it to Stage D (Reporting), not yet started.
Investigate this repository and produce: (1) the relevant existing
source (models/parser/reports/cli) and how it currently relates; (2) the
producer/consumer relationships a real implementation would need to
respect or extend; (3) the execution path a comment-declared report would
need to follow end-to-end; (4) which existing tests already cover
adjacent behaviour and which are net-new; (5) the relevant docs
(`dev-docs/api-spec.md`, `ROADMAP.md`'s Stage D row); (6) any open design
questions or uncertainties you could not resolve with confidence (e.g.
how a comment-declared report should compose with the existing
`-q`/`--query` CLI flag); (7) a proposed design for the comment syntax's
grammar, how a malformed spec block is reported, and how the parsed
`ReportSpec` reaches a report. Do not implement code yet — this stage is
discovery and design only. Record your research trace per §5.3.4."

This produces a genuinely comparable design artifact from each arm,
without letting one arm's own arbitrary implementation choices (a
different grammar, a different CLI-wiring decision) become mistaken for
a measurement of context quality — exactly the conflation the plan's
first draft risked, corrected by the three-stage structure in §5.3.

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
- **Clone reuse across stages:** the Stage 1 discovery/design agents
  (§5.3.1) are instructed not to modify their own clone's tracked files
  (investigation and design only, no implementation) — so both clones
  remain valid, untouched fixtures if Stage 3 (§5.3.3) later dispatches
  fresh implementation agents against the same clones, without needing a
  second fork or a second fixture-equivalence check.

### 5.3 Three-part trial structure (discovery → evaluation → optional shared-contract implementation)

The plan's first draft risked a real methodological flaw: dispatching
both arms straight to "design-and-implement" independently would let
each arm invent its own implementation contract (its own grammar choice,
its own CLI-wiring decision), and a difference between the two final
implementations would then be indistinguishable from a difference in
*design taste* — never a clean measurement of *context quality*. This
plan is restructured into three explicit stages to prevent that, and to
respect Ledgerkit's own real design → human-approval →
fresh-agent-implementation → independent-verification workflow rather
than bypassing it inside a disposable experiment.

#### 5.3.1 Stage 1 — Discovery/design comparison (the primary comparison)

- **Baseline agent:** fresh `general-purpose` agent, dispatched against
  `ledgerkit-baseline`, ordinary repository/tool access (read files,
  `grep`, run the test suite, read `git log`/`git blame`) — **no
  CodeCompass** (no `codecompass` CLI invocation of any kind; the
  baseline clone has no synced `context-graph.db` to query even if it
  tried).
- **Treatment agent:** fresh `general-purpose` agent, dispatched against
  `ledgerkit-treatment`, the identical task framing (§5.1), the same
  ordinary access, **plus** current CodeCompass (`query source`/`query
  source-symbol`, `query relations`, `query symbol`, `query vendor`, the
  generated Skill/`/discovery` slash command — every surface Phase 77
  shipped, none disabled or restricted).
- Both agents investigate and design **only** (§5.1's task framing) —
  neither writes implementation code at this stage, and neither modifies
  their own clone's tracked files, keeping both clones valid, untouched
  fixtures for §5.3.3 if it runs.
- **Read-scope symmetry** (`L-062`, mandatory per the reference-project
  protocol §2.2): the dispatch prompt states explicitly, for **both**
  arms, that reads are scoped to the agent's own assigned clone's own
  tree only — no reading the other arm's clone, no reading this
  CodeCompass repository itself, no reading `planning/reference-projects/
  ledgerkit/` (which would leak Phase 75/77's own prior findings about
  this exact codebase). Both arms may run Ledgerkit's own test suite and
  read Ledgerkit's own `dev-docs/`/`ROADMAP.md` freely — that is ordinary
  access to the assigned clone's own tree, not a leak.
- **Observable research-trace requirements** apply to both reports — see
  §5.3.4.
- **Agent-report-to-disk discipline** (`L-064`/`agent-led-workflow.md`
  step 5, confirmed working at Phase 77 via `L-066`): both agents' full
  reports are written to disk immediately on receipt, before drafting
  the `context-evaluator` dispatch prompt (§5.3.2).

#### 5.3.2 Stage 2 — Independent evaluation

- **Independent `context-evaluator` assessment**, dispatched after both
  Stage 1 reports exist, inspecting the treatment clone directly (and,
  for the `CG-001` question specifically, re-deriving the
  producer/consumer chain itself by direct code reading, the same
  "establish ground truth directly" discipline Phase 77's own evaluator
  applied when it re-ran the failing `to_dataframe` query itself) — never
  trusting either agent's own self-report of how hard the task was.
- This is where §4's three-outcome `CG-001` determination (`recurred` /
  `not-recurred` / `task-not-applicable`) and §6's full rubric are
  actually decided. **This evaluation alone is sufficient to answer
  §7.2's exit question** — Stage 3 (below) is not required to reach a
  Priority A decision; it exists only to check whether context quality
  also matters at implementation time, a genuinely separate question the
  evaluator itself decides is worth answering (not the lead, §8).

#### 5.3.3 Stage 3 (optional) — Shared-contract implementation check

Run only if Stage 2's own independent evaluator judges that
implementation-time behaviour would add real, non-redundant evidence
beyond the discovery comparison (e.g. the design stage surfaced a genuine
ambiguity whose resolution materially affects how much context helps
during the actual coding). If run:

1. **One shared implementation contract is derived**, not invented fresh
   by whichever agent happens to implement it: the lead reviews both
   Stage 1 design reports and drafts a single, concrete contract (the
   comment syntax's exact grammar, the malformed-spec-block behaviour,
   how the parsed `ReportSpec` reaches a report, and its `-q`/`--query`
   composition) — informed by, but not necessarily identical to, either
   arm's own proposal.
2. **The contract is presented for human/user approval before any
   implementation agent is dispatched** — mirroring Ledgerkit's own real
   design → human-approval → fresh-agent-implementation →
   independent-verification workflow (`ROADMAP.md`'s own Stage C
   precedent, e.g. Phases 6-9), not a shortcut invented for this
   evaluation.
3. **Fresh implementation agents** (not the Stage 1 discovery agents, to
   avoid carrying over any Stage-1-specific advantage or disadvantage
   into the implementation comparison) are dispatched — one per arm, the
   same read-scope-symmetry rule, the same no-CodeCompass/with-CodeCompass
   split — given the **identical, already-approved contract**, and asked
   only to implement it, add tests, and update docs. Neither arm makes
   its own design choices at this stage; the contract is fixed.
4. **Independent verification** of both resulting implementations (test
   suite pass/fail, `context-evaluator` re-assessment of
   implementation-stage context use) follows the same discipline as
   Stage 2.
5. **Neither implementation is committed to Ledgerkit's own real
   repository, under any circumstance.** Both stay inside their own
   disposable scratch clone, evaluated and then deleted per §11 — this
   evaluation never silently lands real Stage D work in Ledgerkit from a
   disposable experiment clone. If either implementation is judged
   genuinely mergeable, offering it to the real Ledgerkit project is a
   separate decision, made afterward, through Ledgerkit's own real
   contribution process — never a side effect of this evaluation.

#### 5.3.4 Observable research-trace requirements (both stages)

Every dispatched agent's report (Stage 1, and Stage 3 if it runs) must
record, at minimum:

- every file read (path);
- every search/grep performed and its query;
- every CodeCompass query invoked and its output, verbatim (treatment arm
  only — the baseline arm has none to record, and states so explicitly,
  "n/a, no CodeCompass access", rather than leaving the section blank);
- every test/command run and its result;
- files revisited more than once, and why;
- each major discovery and the specific file/command/query it came from;
- any assumption made, then corrected, once contradicted by later
  evidence;
- any research the agent later realised duplicated work it had already
  done (or, for the treatment arm, duplicated something CodeCompass had
  already surfaced).

**This is an observable-behaviour trace, not private chain-of-thought.**
Agents are not asked to expose internal reasoning that produced no
observable action — only the actions themselves (reads, searches,
queries, commands, revisits) and their outcomes. `context-evaluator` uses
these traces, cross-checked against its own independent re-derivation of
the same task, to distinguish genuine context advantage from ordinary
agent-diligence variance (`L-027`) — the distinction Phase 75's own retro
already established as necessary, now given an explicit, checkable
evidentiary basis rather than resting on the evaluator's own impression
of a report's polish.

### 5.4 Reports/artifacts this trial produces

- `planning/reference-projects/ledgerkit/06-fixture-equivalence.md`
  (pre-dispatch check, §5.2).
- `planning/reference-projects/ledgerkit/06-stage-d-reportspec-stage1-baseline-report.md`
  and `...-stage1-treatment-report.md` (Stage 1 discovery/design reports,
  each including its own observable research trace, §5.3.4).
- `planning/reference-projects/ledgerkit/06-stage-d-reportspec-priority-a-validation.md`
  (the combined Stage 2 evaluation report, following the exact structure
  of `04-cur-query-priority-a-validation.md`/`05-phase-77-first-party-
  source-validation.md` — Setup, Criteria assessment against §6's
  rubric, an explicit `CG-001` three-outcome verdict per §4, overall
  Verdict, Context advantage, Material gaps/failures, "would this have
  misled the implementing agent," lead + independent-evaluator sections
  clearly divided).
- **If Stage 3 runs (§5.3.3):**
  `planning/reference-projects/ledgerkit/06-stage-d-reportspec-shared-contract.md`
  (the derived, approved implementation contract, §5.3.3 steps 1-2), plus
  `...-stage3-baseline-report.md`/`...-stage3-treatment-report.md` (fresh
  implementation agents' own reports and research traces) and a Stage 3
  evaluation addendum to the combined validation report above.
- `planning/reference-projects/ledgerkit.md`'s own registration record
  updated with this task's pinned commit and result summary
  (`reference-project-protocol.md` §2.1).

No implementation is committed to Ledgerkit's own real repository by this
trial under any circumstance (§5.3.3 step 5). The scratch clones are
disposable evaluation fixtures, per the working-copy discipline (§2.2),
not a channel for landing code in Ledgerkit's own real repository — if
Stage 3 runs and produces a genuinely mergeable result, offering it back
to the real Ledgerkit project is a separate decision, made afterward,
through Ledgerkit's own real contribution process, not decided by this
plan.

## 6. Evaluation criteria

Uses `context-quality-evaluation.md`'s own established rubric unchanged
(Accuracy / Relevance / Completeness / Freshness / Grounding-provenance /
Noise / Safety-trustworthiness, each rated strong/adequate/weak/n/a),
**plus** explicit, named sub-questions instantiating the user's own
requested dimensions for this specific task, so the evaluator addresses
each one directly rather than folding them into a single generic
"Completeness" rating:

| Context-completeness dimension | Concrete question for this task |
|---|---|
| Relevant source | Did CodeCompass correctly point at `ReportSpec`/`ReportSection`/`balance_from_spec` (via `query source-symbol`) as the existing consumer machinery, without the agent needing to discover it by grep first? |
| Relationships | Could the agent determine, via CodeCompass alone, which functions in `reports.py`/`cli.py` already reference `ReportSpec`, and which do not yet call `balance_from_spec`? (This is `CG-001`'s own question — §4's three-outcome model.) |
| Execution/behavioural paths | Did CodeCompass help trace how a report actually gets rendered end-to-end (`balance_from_spec` → `ReportSectionResult` → whatever `cli.py` does with it today, i.e. nothing) — or was this traced by reading code directly regardless of tooling? |
| Tests | Did CodeCompass help identify which existing tests (`test_reports.py`, `test_parser.py`) already cover adjacent behaviour and would need extending, versus which are genuinely new? |
| Docs/ADRs | Did CodeCompass surface `dev-docs/api-spec.md`'s own `[DEFERRED — Milestone 3]` note and `ROADMAP.md`'s Stage D row without the agent needing to grep for them independently? |
| Compatibility evidence | Not directly applicable to this task (no hledger-compatibility question is in scope) — record as `n/a`, not a forced score. |
| Explicit uncertainty | Did CodeCompass ever present a *genuinely unresolved* state honestly — e.g. `exposure: unknown`, `symbol_index_status: indexed_partial`/`parse_error`, or a `query source-symbol` lookup correctly reporting no match/an unresolved relationship — rather than silently omitting it or asserting false confidence? **Note:** an `internal`/`restricted`/`conventional_private` exposure is a resolved, confident classification, not an instance of uncertainty — only `unknown` and a partial/failed extraction state count here. |
| Duplicated research | Did the treatment agent (per its own §5.3.4 trace) re-derive something CodeCompass simply never surfaced? Classify as a **Completeness/efficiency gap** by default — an omission, not a false claim. Escalate to a **Safety/trustworthiness** failure only if CodeCompass had *affirmatively claimed* to already have that information and the claim was wrong. |
| Incorrect assumptions | Did any CodeCompass-supplied claim turn out to be *affirmatively wrong* (not merely incomplete) when checked against the real code? An affirmatively false or misleading claim presented as fact is a **Safety/trustworthiness** failure; an absent or incomplete claim is a **Completeness** gap, not Safety — the two are never conflated. |
| Overall context advantage | LOW / MODERATE / HIGH per `context-quality-evaluation.md` §5, **reported separately from** the `CG-001`-specific verdict (§4) — the two must not be conflated into one number. |

Verdict format matches precedent exactly: **PASS / PASS WITH GAPS /
FAIL**, **LOW / MODERATE / HIGH** advantage, plus this trial's own
required addition — an explicit **`CG-001` outcome: recurred /
not-recurred / task-not-applicable** line, citing the specific evidence
for whichever of the three it is (§4's own criteria). `task-not-applicable`
is evidence-neutral for the exit decision (§4 Outcome 3, §7.2.0) and
triggers task substitution/re-run before §7.2 can be applied — it is not
a verdict on whether CodeCompass "passed" or "failed."

## 7. Decision gates

### 7.1 Backlog-item gate (routine, per `context-gaps/README.md`)

For every deferred item in §3 (`CG-003`, `CG-007`, `CG-011`, Phase
24/25/50): unchanged unless this trial's own evidence happens to bear on
one of them directly (checked explicitly at closeout, not assumed not
to — matching the discipline `CG-009`'s own Phase 77 closeout triage
applied when checking the unrelated context-evaluation report before
declaring it didn't weigh against closure). `CG-010` is excluded from
this routine gate — per §3.1 it is already-evidenced, ready-to-fund
maintenance backlog, not waiting on a revisit trigger.

### 7.2 The Priority A exit decision (the phase's own terminal gate)

Made at closeout, by an independent `knowledge-curator` triage of the
trial's real report (the same non-rubber-stamp discipline that reversed
Phase 75's own provisional `CG-001` call and resolved `CG-009`), not by
the lead's own assertion. **This gate has three possible inputs (§4),
only two of which produce a decision:**

#### 7.2.0 Applicability gate (checked first, before either branch below)

If the trial's own `CG-001` outcome is **task-not-applicable** (§4
Outcome 3), **no Priority A exit decision is made from this trial.**
Neither branch below fires. Per §4 and §5.1's own fallback/re-run
requirement, the trial is re-run against the fallback task or a freshly
live-verified alternative before `planning/ROADMAP.md`'s Priority A row
is touched at all. Phase 78 is not closed as `done` (§10) while this
gate is unresolved.

#### Branch A — Priority A closed

Fires **only if** the trial's own `CG-001` outcome is **not-recurred**,
on a task independently confirmed applicable (Outcome 2, not Outcome 3
— §4), backed by the Stage 2 `context-evaluator`'s own independent
assessment (§5.3.2), never the dispatched agents' own self-reports. If
this branch fires, the recorded rationale is: three real trials (75, 76,
77) already showed CodeCompass materially helps at LOW-to-MODERATE
advantage without ever producing a FAIL or a misleading claim, and this
trial's own applicable, independently-evaluated result adds a genuine
fourth data point that specifically *tested* — rather than merely failed
to raise — the one remaining open hypothesis (`CG-001`), and found it
does not clear its own evidence bar. `planning/ROADMAP.md`'s Priority A
row is updated to record closure, its success criterion is stated as met
(a `context-evaluator` PASS-or-PASS-WITH-GAPS record now exists across
three structurally different capability areas — query semantics, Git
topology, first-party source — plus an explicit, evidence-checked
negative result on the one remaining open hypothesis), and Priority A is
not reopened absent new evidence of a different, not-yet-tested shape.
**Closing Priority A strategically does not affect `CG-010`'s own
independent maintenance-backlog funding (§3.1)** — that work continues
on its own evidence, unrelated to this gate.

#### Branch B — one narrowly-scoped final follow-on

Fires **only if** the trial's own `CG-001` outcome is **recurred** (§4
Outcome 1) — a second, genuinely separate edge instance, materially
costly, not beaten by ordinary diligence, confirmed by the Stage 2
evaluator. The follow-on is scoped to **exactly** the smallest concrete
edge shape the trial actually evidenced — not a general
relationship-graph capability, per the user's own explicit instruction
that a `recurred` result "still triggers only the smallest
evidence-supported follow-on capability." Candidate shape, informed by
Phase 77's own plan §13 but **not pre-committed**: a single new edge
table for the *specific* relationship kind the trial's own evidence names
(e.g. `source_symbol → references source_symbol` within one project,
detected the same way `uses_edges` already detects vendor usage — a
within-project reuse of an existing detection technique, not a new
ontology). The follow-on gets its own `planning/phase-N-*.md`
(`CLAUDE.md` §1) and its own validation, per the user's own instruction —
it is not implemented as part of Phase 78's own closeout.

**Exactly one of the three gates above applies to any given trial run —
7.2.0 is checked first and, if it fires, neither Branch A nor Branch B
is reached until a re-run produces an applicable result. This plan does
not presuppose which of the three will apply.**

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

**A second, related judgment call, also resolved rather than left
blocking:** whether to run Stage 3's implementation check at all (§5.3.3).
This is deliberately not the lead's own call — §5.3.2 assigns it to the
independent `context-evaluator`, so the decision to spend further trial
cost on an implementation comparison is made by the same non-self-interested
party who judges the discovery-stage evidence, not by whoever might be
motivated to see the trial produce a particular result.

**No other human-decision gate was found beyond the two named above.** In
particular, §7.2's own branch choice is explicitly *not* a gate requiring
a decision now — it is designed to be decided later, by real evidence the
trial itself produces, which is the entire point of running the trial
before committing to either outcome.

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

- The Stage 1 (and, if Stage 3 runs, Stage 3) report files named in §5.4.
- If Stage 3 runs: the shared implementation contract document (§5.3.3
  step 1), presented for and recording human/user approval (§5.3.3 step
  2) before implementation dispatch.
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
2. The trial (§5) has actually run **to an applicable result** (§4
   Outcome 1 or 2 — not left stalled at Outcome 3/§7.2.0): Stage 1
   dispatched for both arms, both reports (with observable research
   traces, §5.3.4) written to disk, fixture-equivalence confirmed,
   independent `context-evaluator` Stage 2 assessment completed and
   persisted, and — only if the evaluator judged it necessary (§5.3.2) —
   Stage 3's shared-contract implementation check completed with its own
   independent verification.
3. §7.2's decision gate has been applied by an independent
   `knowledge-curator` triage (not the lead's own assertion): either
   Branch A or Branch B fired on an applicable result, and the outcome is
   recorded with the evidence named in §4/§7.2.
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
   §5's own terminal-action rule. `CG-010`'s own maintenance-backlog
   disposition (§3.1) is unaffected either way and needs no DoD condition
   of its own here.

**This plan file's own Status line only reaches `done` when Phase 78
itself does — writing and approving this plan is not, by itself, the
phase's completion.**

## 11. Rollback / cleanup requirements

- Both Ledgerkit scratch clones (`ledgerkit-baseline`, `ledgerkit-treatment`)
  are disposable, outside this repository's own tree, never added to
  `vendor.toml`/`context-graph.db`/git, and never committed to
  Ledgerkit's own real upstream repository under any circumstance (§5.3.3
  step 5) — cleaned up (deleted) once the evaluation reports are
  persisted, per the working-copy discipline (§5.2) and this project's
  own established scratch-cleanup discipline (confirmed clean at every
  prior phase's completion audit).
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

## 13. Amendment log

**2026-09-29, second revision** (direct user request, before any trial
was dispatched — planning only, no code touched, no agent run). Six
corrections applied throughout, reconciled across every affected section:

1. **Exit-gate contradiction fixed** (§4, §7.2): `task-not-applicable`
   was originally treated as equivalent to `not-recurred` for closing
   Priority A. It is now explicitly evidence-neutral (§4 Outcome 3), gated
   by a new §7.2.0 applicability check that blocks both branches and
   requires a task substitution/re-run before any exit decision — Priority
   A can only close on an actually-applicable `not-recurred` result
   (Outcome 2), and `recurred` (Outcome 1) still triggers only the
   smallest evidence-supported follow-on, never a general capability.
2. **`CG-010`/Priority-A-closure inconsistency resolved** (§2, §3, §3.1,
   §7.2): `CG-010` was previously "ready to fund as a standalone Priority
   A phase" while Priority A could simultaneously close — an unreconciled
   status. New §3.1 makes the strategic-closure-vs-maintenance-backlog
   distinction explicit; `CG-010` (and `CG-011` if it ever recurs) is
   reclassified as bounded Git-topology maintenance, independently
   fundable regardless of §7.2's own outcome.
3. **Trial methodology corrected** (§5.3): the original single-stage
   "design-and-implement independently, then compare" design risked
   conflating differing implementation choices with differing context
   quality. Restructured into Stage 1 (discovery/design comparison, no
   code written), Stage 2 (independent evaluation — sufficient on its own
   to answer §7.2), and an optional Stage 3 (one shared, human-approved
   implementation contract given to fresh implementation agents in both
   arms) — respecting Ledgerkit's own real design→approval→
   implementation→verification workflow, and never landing real Ledgerkit
   work from a disposable clone (§5.3.3 step 5).
4. **Observable research-trace requirement added** (§5.3.4): both arms'
   reports must now record files read, searches/queries run, tests/
   commands executed, revisits, discoveries and their source, corrected
   assumptions, and duplicated research — observable actions only, never
   private chain-of-thought — so `context-evaluator` can distinguish
   genuine context advantage from ordinary diligence variance on evidence
   rather than impression.
5. **Pre-judgment removed** (§1): the problem statement previously read
   as implying Phase 78 would likely also rate LOW. Reworded to state
   Phases 75-77's own LOW/MODERATE/LOW history accurately while explicitly
   stating Phase 78's own verdict, advantage rating, and `CG-001` outcome
   remain genuinely open; §7.2's Branch A rationale reworded from
   presumptive ("three trials plus this one...") to conditional ("if this
   branch fires...").
6. **Evaluation terminology tightened** (§6): "uncertainty" examples no
   longer include `internal` exposure (a resolved classification, not
   uncertainty) — replaced with genuinely unresolved states (`unknown`
   exposure, `indexed_partial`/`parse_error` status, an unresolved
   relationship lookup). "Duplicated research" and "incorrect assumptions"
   no longer default to a Safety/trustworthiness failure for a mere
   omission — that classification is now reserved for an affirmatively
   false or misleading claim presented as fact; an omission is a
   Completeness/efficiency gap.

No change to this plan's overall strategy (audit the backlog, test
`CG-001` for real before building anything, define the exit gate in
advance) — only to the six specific defects named above and their
consequences elsewhere in the document.
