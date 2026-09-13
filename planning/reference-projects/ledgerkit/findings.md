# Ledgerkit findings — GATE DB (Phase 47)

Consolidates every Phase 44–46 candidate learning, `context-gaps` entry,
and evaluation report per `planning/phase-47-consolidate-findings.md`.
Written by `knowledge-curator`; the GATE DB decision below is a
**recommendation for the lead/user to ratify**, not a decision made
unilaterally (`phase-47-consolidate-findings.md`'s own "Design decisions"
section).

This file is also `planning/reference-projects/ledgerkit/findings.md`,
the same path Phase 55 (GATE DD) writes its own decision to
(`roadmap.md`, `ledgerkit-plan.md` §"Phase 55"). Per `context-health.md`'s
own precedent for a file that accumulates dated decisions against a
moving target, **Phase 55 should append a new `## GATE DD (Phase 55)`
section below this one, not overwrite it** — the two gates answer
different questions (detection-improvement vs. graph-capability) from an
overlapping but not identical evidence base.

**Re-inspected Ledgerkit live at this phase's start:** no material change
since Phase 46's pinned commit (`9c33e37c`) that would affect these
findings' currency — confirmed by re-reading the evidence inventory
below directly rather than trusting prior phases' summaries alone.
`validation/codecompass/findings/` re-checked live: still empty, no
external findings to incorporate.

---

## 1. Aggregate verdict count (`context-quality-evaluation.md` §6)

**5 total evaluated question/task instances** across Phases 45–46:

| # | Instance | Verdict | Advantage |
|---|---|---|---|
| 1 | Baseline Q1 — runtime dependencies (`00-baseline.md`) | PASS WITH GAPS | LOW |
| 2 | Baseline Q2 — hledger-1.52 compatibility governance (`00-baseline.md`) | **FAIL** | LOW (negative) |
| 3 | Baseline Q3 — development-stage/roadmap state (`00-baseline.md`) | PASS WITH GAPS | LOW |
| 4 | Task 01 — query-term semantics, `reference-project-tester`'s friction log (`01-query-semantics.md`) | (no formal verdict — friction-log instrument, not a `context-evaluator` verdict; independently corroborates #5) | LOW (at the floor: zero actual contribution — `context-use-log.md`) |
| 5 | Task 01 — query-term semantics, `context-evaluator`'s independent verdict (`01-query-semantics.md`) | **FAIL** | LOW (negative) |

**Counting basis, stated explicitly so it's independently checkable:**
only the `context-evaluator` role assigns the formal PASS / PASS WITH
GAPS / FAIL verdict under `context-quality-evaluation.md` §1/§2 — the
`reference-project-tester` role produces a friction log and
`context-use-log.md` entries, a different instrument, not a duplicate
verdict. Task 01's two write-ups are both counted as separate evaluated
instances (they are two independent agents assessing the same task, per
the protocol's own design) but only instance 5 carries a template
"Verdict:" line. **2 formal FAIL verdicts exist across the 5 instances**
(#2 and #5) — listed in full below per the aggregation rule's instruction
to list every "would this have misled the agent? yes/partially" case in
full, since a FAIL is the highest-priority category regardless of count.

### FAIL #1 (Baseline Q2 — `00-baseline.md`)

> `codecompass query relations dev-docs/hledger-compatibility.md` →
> `error: 'dev-docs/hledger-compatibility.md' not found in
> context-graph.db'`. The file exists, is current, is 238 lines, and is
> exactly Ledgerkit's own designated hledger-1.52-compatibility governance
> document, cited as a Milestone 1/4 exit criterion in Ledgerkit's own
> `ROADMAP.md`. Root cause: `spec_docs.py::_DEFAULT_GLOBS` has no
> `dev-docs/**/*.md` entry, so the file was never registered as a
> `doc_artifacts` row at all — `_resolve_relations` returns `None` and the
> CLI raises `_not_found_error`, the identical code path a genuine typo
> would hit. Rated FAIL, not PASS WITH GAPS, because an authoritative-
> sounding "not found" for a real, load-bearing file is judged more
> serious than an honest "no relations found" (governing rule 3,
> `context-quality-evaluation.md` §1). Context advantage: LOW, and
> **negative** — `ls dev-docs/` or `grep -ril hledger dev-docs/` finds the
> file in seconds; CodeCompass's answer here is actively worse than doing
> nothing. Would this have misled the implementing agent? **Yes** — an
> agent trusting "not found" would either invent parser/directive
> behaviour from scratch or fall back to general hledger knowledge
> contradicting Ledgerkit's own documented deviations (e.g. alias/`include`
> non-propagation).

### FAIL #2 (Task 01 — `01-query-semantics.md`, `context-evaluator` section)

> Same live-repo query, re-run on a real in-progress task (hledger 1.52
> `acct:`/`desc:`/`date:`/`depth:`/`status:`/`not:` query-term semantics)
> rather than a spot-check question: `query vendors` returned 0 rows
> (correct — 0 runtime deps), `query relations` returned "not found" for
> **both** `dev-docs/hledger-compatibility.md` and the nested
> `dev-docs/planning/core-redefinition/07-query-regex.md` — the second
> path independently confirming `CG-002` extends to arbitrarily nested
> `dev-docs/**` paths, not just top-level files. `07-query-regex.md` §7.1
> already contained a complete, on-topic answer table for all six query
> terms, found by one `grep` + file read. Rated FAIL for the identical
> reason as Baseline Q2 — an authoritative "not found" for a real,
> directly load-bearing, in-progress-relevant file. Context advantage: LOW
> (negative) — `grep -rn "query" dev-docs/planning/core-redefinition/`
> finds the answer in seconds. Would this have misled the implementing
> agent? **Yes** — same reasoning as Q2: an agent trusting "not found"
> would either duplicate Ledgerkit's own in-flight `hledger-researcher`
> brief from scratch or fall back to general hledger training-data
> knowledge, missing Ledgerkit's own already-recorded scoping decisions.

## 2. Advantage distribution

**100% LOW across all 5 instances.** Two of those five are explicitly
**negative** (the tool's answer was actively worse than doing nothing,
not merely unhelpful) — Baseline Q2 and Task 01's `context-evaluator`
verdict, both above. The other three (Baseline Q1, Q3, and Task 01's
`reference-project-tester` friction log) are honest LOW results — no
incorrect claim, just marginal-to-zero contribution over a cheap direct
read, which is the *expected*, non-defect outcome for a package-relationship
tool pointed at a project with 0 required runtime dependencies
(`conditional-generalisation.md` §1.1's own prior, confirmed twice now:
once by `context-health.md`'s Phase 45 prediction, once by the actual
Phase 46 result).

No MODERATE or HIGH advantage instance exists yet in the Ledgerkit
evidence base.

## 3. Recurring gap category — the `_DEFAULT_GLOBS` blind spot

The identical failure shape has now occurred **three times**, across two
projects and three phases, independently confirmed each time by direct
inspection of `src/codecompass/spec_docs.py` rather than assumed from
resemblance alone:

1. **Phase 37** (this repo, own dogfooding) — `ai-docs/README.md` /
   `ai-docs/CLAUDE.md` created, neither detected as a spec doc;
   `query relations ai-docs/README.md` errored "not found in…". Fixed
   directly (pre-dates the `context-gaps/` mechanism, introduced Phase
   43c) by adding `"ai-docs/**/*.md"` to `_DEFAULT_GLOBS`.
2. **Phase 45** (Ledgerkit, baseline Q2) — `dev-docs/hledger-compatibility.md`
   invisible to spec-doc detection for the identical reason. Filed as
   `CG-002`, status `recurred` (this being the second occurrence of the
   underlying pattern).
3. **Phase 46** (Ledgerkit, task 01, live in-progress work) — the same
   `dev-docs/` blind spot re-confirmed independently by both
   `reference-project-tester` and `context-evaluator`, and *extended*:
   nested paths (`dev-docs/planning/core-redefinition/07-query-regex.md`)
   are equally invisible, not just top-level files under `dev-docs/`.

`spec_docs.py`'s own module comment already anticipates exactly this:
"ship with this fixed default list, add configurability only once a real
project shows it's wrong for it" (L19–21). One real project (Ledgerkit)
has now shown it wrong, in the same way Phase 37's own dogfooding did —
**the third occurrence of the identical shape**, this time external
corroboration of what was previously only an internal-dogfooding finding.

A structurally identical symptom-layer finding, **`L-016`**, recurred
alongside it: `query relations`'s "not found" error is indistinguishable
between "never scanned as a doc artifact" (a glob-coverage gap) and
"genuine typo/misspelling" (real user error) — both baseline Q2 and task
01 hit this exact ambiguity, confirmed by tracing
`cli.py::_resolve_relations`/`_not_found_error` directly. This recurs the
*consequence* of the same root architecture, not a separate mechanism.

## 4. Roadmap implication — does this justify a Stage C phase?

**Yes, a narrow one.** Three independent occurrences of the identical
failure shape (one internal, two external, the external ones now
including a live in-progress-work instance) is exactly the kind of
recurrence `planning/context-gaps/README.md` and
`context-quality-evaluation.md` §6 treat as GATE DB input, and
`conditional-generalisation.md`'s "smallest model that covers the
demonstrated need" discipline applies directly to *which* fix is
justified.

**Smallest justified fix, not the more general one:**

- **Recommended: a single new glob entry** — `"dev-docs/**/*.md"` added to
  `spec_docs._DEFAULT_GLOBS`, mirroring the Phase 37 `ai-docs/**/*.md`
  precedent exactly. This closes `CG-002` at its root.
- **Not recommended yet: a `vendor.toml`-configurable spec-doc glob
  list.** `CG-002`'s own Phase 45 curation note raised this as a
  candidate more-general fix, and it is worth naming as the discipline
  this project already applies elsewhere (`_DEFAULT_GLOBS`'s own comment:
  "add configurability only once a real project shows it's wrong for
  it") — but the evidence today is **two** conventions needing a
  hard-coded entry each (`ai-docs/`, `dev-docs/`), not a pattern of
  ever-growing, hard-to-anticipate conventions that would justify
  building general configurability infrastructure. `conditional-
  generalisation.md`'s explicit non-negotiable — "do not implement a
  universal dependency ontology merely because it appears
  architecturally elegant" — generalises to detection heuristics too:
  a second hard-coded glob entry is the smaller model, and it is what
  the module's own documented policy already commits to doing at exactly
  this evidence threshold. **Revisit configurability if a third,
  distinct project/convention recurs** — that would be the point where
  hard-coding starts to look like an ongoing maintenance tax rather than
  a one-line fix applied twice.
- **Bundle `L-016`'s fix into the same phase** — it shares the identical
  root cause and code path (`_resolve_relations`/`_not_found_error`), has
  independently recurred twice (Phase 45 baseline, Phase 46 live task),
  and is cheap: distinguish "path exists on disk but was never scanned as
  a doc artifact" from "path does not exist at all" (e.g. via
  `Path.exists()` before erroring), with a different message/hint for
  each. Fixing `CG-002` alone would still leave the *next* unanticipated
  doc-directory convention producing the identical misleading "not found"
  — `L-016`'s fix is what keeps that residual risk bounded going forward.

**What this phase should explicitly *not* also take on** (keeping it
narrow, per the task's own framing): `L-015` (optional-dependency CLI
silence) is a different code path (`discovery.py`, not `spec_docs.py`)
with only a single occurrence (Phase 45 Q1, not re-confirmed by task 01,
which was a query-semantics task unrelated to dependency discovery) — it
should stay `retained`, not bundled in, to keep this phase's scope to what
is actually evidenced. `L-012` (single-symbol query breadth) is a
self-test finding only, explicitly excluded from aggregation by its own
phase's design and still uncorroborated by any real reference-project
finding — stays `retained`.

## 5. `CG-003` and `L-017` — explicitly out of scope for this gate

Both point toward **Stage E (GATE DD)** or **Stage D** territory, not
Stage C, and neither should be read as addressed by the funding decision
below:

- **`CG-003`** (external hledger.org manual has zero representation) is,
  by its own classification and its own Phase 46 curation note,
  **graph-capability**, not detection-improvement — "no glob fix could
  ever cover it" is the entry's own reasoning, since the manual isn't a
  file in the repository at all. `context-gaps/README.md`'s hard rule is
  explicit that this class of gap is only ever promoted via a Stage E ADR
  at GATE DD (Phase 55), never a Stage C detection heuristic. GATE DB
  (this gate) has no lever to act on it even if it wanted to. It is named
  here as context for GATE DD's own Phase 47/55 input, not as something
  this decision resolves.
- **`L-017`** (a live `WebFetch` of a large external manual is an
  expensive, unreliable fallback) is a **retrieval-cost finding**, not a
  detection-improvement or a graph-capability decision by itself — it
  bears directly on Phase 53's already-scheduled design question ("the
  hledger manual as fetched/vendored text," `ledgerkit-plan.md` §1 item
  2, `conditional-generalisation.md` §2.3), which is Stage B/D territory
  well downstream of this gate. Funding a Stage C phase around it would
  be premature: the finding says nothing about what CodeCompass's
  *detection* layer should do differently, only about the cost profile of
  one fallback CodeCompass doesn't currently implement at all. It stays
  `retained`, feeding Phase 53 directly rather than a `ROADMAP.md` row of
  its own.

## 6. Not yet actionable (stays as-is)

- **`CG-001`** (own-dev, one feature across three `src/` modules) —
  single occurrence, own-dev only, no Ledgerkit corroboration. Task 01's
  finding 3 ("no Skill mentions hledger or query semantics… no 'what
  matters for this task' retrieval yet") is a *weak, conceptually
  adjacent* echo of the same `conditional-generalisation.md` §2.6
  hypothesis (task-oriented retrieval edges) but is not the same concrete
  edge/kind CG-001 names, and per `context-gaps/README.md`'s own
  standard ("recurs, or is filed independently by two agents") this is
  not read as a second occurrence sufficient to move CG-001 to
  `recurred` — noted as a cross-reference in CG-001's own entry (see
  triage below) for Phase 55/GATE DD's benefit, not promoted now.
- **`L-015`** (optional-dependency CLI silence) — single occurrence,
  stays `retained`; revisit at Phase 51's re-run or a second occurrence.
- **`L-012`** (single-symbol query undersells breadth) — self-test only,
  stays `retained`; now 3 phases old with no reference-project
  corroboration (filed Phase 44, no update since) — flagged for a
  promote/discard decision at Phase 51's re-run if still uncorroborated
  by then, per the lifecycle's own "~3 phases without new evidence" norm
  (not yet forced, since its status is `retained` rather than
  `evidence-gathering`, but worth naming so it isn't silently carried
  forever).

## 7. GATE DB recommendation (gate G6) — for the lead/user to ratify

**Recommended: fund one narrow Stage C phase, not the full Stage C
roadmap group.**

- **Fund:** a `_DEFAULT_GLOBS` + not-found-disambiguation phase —
  add `"dev-docs/**/*.md"` (closing `CG-002`) and fix
  `_resolve_relations`/`_not_found_error` to distinguish "never scanned"
  from "genuinely doesn't exist" (closing `L-016`). This is evidenced by
  three independent recurrences of the identical failure shape (one
  internal, two external — including one on live in-progress work) and
  two independent FAIL verdicts of that shape specifically. Scope: the
  smallest model shown to be needed — a single glob entry, not a
  `vendor.toml`-configurable mechanism.
- **Do not fund (yet):** Phase 48 (task-oriented context retrieval) —
  the only supporting signal is `CG-001`, single-occurrence and own-dev
  only, with task 01's finding a weak echo rather than a genuine second
  occurrence. Phase 50 (shared-agent context / entry-point improvements)
  has no supporting finding in this evidence base at all.
- **Re-run after the fix lands:** Phase 51 (re-run Ledgerkit evaluation)
  should re-attempt baseline Q2 and task 01 specifically, to measure
  whether the fix actually moves either result off FAIL/LOW(negative).
  If it does not, that is itself GATE DC input on whether to revert/defer
  the change.
- **This is not** the "advantage is LOW across the board — fund no Stage
  C improvements, go straight to Stage D dogfooding" outcome, because a
  specific, cheap, well-evidenced fix exists and doing nothing would
  leave two confirmed FAIL-producing code paths in place for the next
  reference project or the next Ledgerkit task alike. **It is also not**
  "fund the full Stage C roadmap group" — Phases 48 and 50 have no
  evidence behind them yet in this dataset.

**This is a funding/scope call, not a technical judgment the curator
resolves alone** (`phase-47-consolidate-findings.md`'s own "Design
decisions" section) — the lead/user should ratify or amend this
recommendation before a `planning/phase-48-*.md` (or equivalently
renumbered) plan file is written. If ratified, `roadmap-context-curator`
is the agent that finalises the actual `ROADMAP.md` row per
`learning-lifecycle.md` §4's classification table.

---

## Bulk-review triage summary (this phase)

| ID | Disposition | Notes |
|---|---|---|
| `CG-001` | stays `candidate` | single occurrence; cross-reference note added pointing at task 01's weak §2.6 echo, for GATE DD's benefit — not promoted |
| `CG-002` | `recurred` → `promoted-to-roadmap` | GATE DB ratified by the user; `planning/phase-49-spec-doc-coverage-and-error-disambiguation.md` now owns this gap (see `planning/context-gaps/inbox.md` for the ratification note) |
| `CG-003` | stays `candidate` | confirmed out of scope for GATE DB (§5); Stage E/GATE DD territory only |
| `L-012` | stays `retained` | flagged as 3-phases-old with no new evidence (§6) |
| `L-015` | stays `retained` | single occurrence; explicitly kept out of the narrow Stage C fix's scope (§4) |
| `L-016` | stays `retained` | recurrence confirmed (2 independent instances); GATE DB recommends bundling its fix with `CG-002`'s (§4) |
| `L-017` | stays `retained` | confirmed out of scope for GATE DB (§5); feeds Phase 53 directly |
| `L-013`, `L-018` | no change | already `promoted`, not this gate's concern |

No new candidate learnings or context-gaps were surfaced by this bulk
review beyond the cross-reference note added to `CG-001`. The other
cross-cutting pattern visible only in aggregate — "100% LOW advantage
across every Ledgerkit instance evaluated so far" — is not a new finding;
it is `conditional-generalisation.md` §1.1's own prior being confirmed
twice over, already tracked there and in `context-health.md`'s two
assessments.
