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
  bears directly on the "hledger manual as fetched/vendored text" design
  question (`ledgerkit-plan.md` §1 item 2,
  `conditional-generalisation.md` §2.3), which is Stage B/D territory
  well downstream of this gate. Funding a Stage C phase around it would
  be premature: the finding says nothing about what CodeCompass's
  *detection* layer should do differently, only about the cost profile of
  one fallback CodeCompass doesn't currently implement at all. It stays
  `retained`, feeding whichever future Stage D/E phase takes this question
  up directly rather than a `ROADMAP.md` row of its own — **not
  necessarily Phase 53**, whose slot was retargeted to legacy-feature
  rationalisation on 2026-09-14 (see `v1-redefinition/roadmap.md`'s Phase
  53 amendment note); the exact phase number is unresolved along with the
  rest of Stage D's own scheduling.

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
| `L-012` | `retained` → `discarded` (Phase 51 closure) | 7 phases old (44→51), three unclaimed corroboration opportunities, self-test-only per own exclusion — lifecycle's "~3 phases, no new evidence" norm applied |
| `L-015` | stays `retained` | single occurrence; no phase since filing (45, 46, 47, 49, 51) has been in a position to corroborate it — revisit trigger updated to the next phase touching dependency discovery |
| `L-016` | stays `retained` | recurrence confirmed (2 independent instances); GATE DB recommends bundling its fix with `CG-002`'s (§4) |
| `L-017` | stays `retained` | confirmed out of scope for GATE DB (§5); feeds a future Stage D/E phase directly (not Phase 53 — retargeted 2026-09-14) |
| `L-013`, `L-018` | no change | already `promoted`, not this gate's concern |

No new candidate learnings or context-gaps were surfaced by this bulk
review beyond the cross-reference note added to `CG-001`. The other
cross-cutting pattern visible only in aggregate — "100% LOW advantage
across every Ledgerkit instance evaluated so far" — is not a new finding;
it is `conditional-generalisation.md` §1.1's own prior being confirmed
twice over, already tracked there and in `context-health.md`'s two
assessments.

---

## GATE DC (Phase 51) — did Phase 49's fix work?

Per Phase 49's own deferral note, this section is appended here rather
than reopening the Stage B findings above. Re-pinned Ledgerkit at
`05218e3` (2026-09-13); CodeCompass at `cea0b1c` (includes the Phase 49
fix). `context-evaluator` independently re-ran both original FAIL cases
— same questions, same instrument — plus a generalisation check against
a brand-new file that didn't exist at the original pin.

| | Baseline Q2 | Task 01 |
|---|---|---|
| Before (Phase 45/46) | FAIL / LOW (negative) / misled: yes | FAIL / LOW (negative) / misled: yes |
| After (Phase 51) | PASS WITH GAPS / LOW / misled: no | PASS WITH GAPS / LOW / misled: no |

**Answer: yes, context quality improved — but only on the dimension the
fix targeted, and the advantage ceiling did not move.** The specific,
evidenced, high-severity failure (`query relations` returning a
confidently-authoritative "not found" for real, load-bearing project
docs) is gone, independently reconfirmed by direct inspection and by the
evaluator's own tool runs — not assumed from the fix landing. Generalises
correctly: `17-query-semantics-brief.md`, written by Ledgerkit's own
process *after* the original evaluations ran, is also now correctly
tracked, confirming this is a real mechanism fix, not a two-file patch.

**What did not improve, and structurally cannot with this fix alone:**
`doc_relations_edges` is built purely from literal vendor/Skill
name-mention detection. With 0 tracked vendors, `query relations` on any
Ledgerkit spec doc returns `(none)` regardless of the doc's actual
content — it can never surface *why* a doc matters, only *whether* it's
tracked. `17-query-semantics-brief.md` is, by both evaluators' own
assessment, the single most valuable artifact encountered in any
Ledgerkit evaluation to date, and `query relations` surfaces none of it.
This is not a regression or a new gap — it's the same limitation `CG-003`
and the original baseline already named, now directly demonstrated on a
concrete artifact rather than argued abstractly.

**Verdict on Phase 49's fix, on its own terms: success.** It closed
exactly what it was scoped to close (`CG-002`/`L-016`), did not
over-claim, and the narrow-fix discipline (`findings.md` §4's rejection
of a more general glob-configurability mechanism) is validated — nothing
about this re-run suggests the earlier "smallest justified fix" judgment
was wrong.

**Implication for Stage D (Phases 52-55):** the redefined-v1 plan's own
honest-exit language applies here (`v1-redefinition/roadmap.md` Phase
51's own text): "a measured improvement over the foundation baseline,
re-validated on a real external project, is a defensible redefined v1."
Phase 49 *is* a measured improvement, validated here. Whether to continue
into Stage D's deeper dogfooding (testing whether CodeCompass can usefully
relate heterogeneous content — docs, executable behaviour, compatibility
tests — a materially harder problem than glob coverage) or treat this as
sufficient and proceed toward Stage F/G is a genuine strategic call, not
a technical one this file resolves — see the retro for the lead's
framing of that choice.

Full per-question detail: `planning/reference-projects/ledgerkit/00-baseline.md`
and `01-query-semantics.md`'s "Phase 51 re-run" sections (independently
authored by `context-evaluator`, appended, not overwriting the originals).

---

## Phase 54 — heterogeneous reference-material experiment (2026-09-16)

Full plan: `planning/phase-54-heterogeneous-reference-material-experiment.md`.
Answers the question that section's own framing left open: can
CodeCompass pin and expose external hledger reference material so it
materially improves an agent's context for a real Ledgerkit task,
without prematurely committing to a new graph ontology? **Not primarily
by generalisation-readiness verdict** (that's this section's own closing
recommendation) but by real evidence from a genuine, live two-run
comparison task.

### Setup

A real ingestion pipeline
(`planning/reference-projects/ledgerkit/reference-experiment/`,
deliberately outside `src/codecompass/` this phase) pinned hledger at
tag `1.52.4` (resolved to commit `33fa849e7ae841968bd21c427094c4fb4a4ec38d`,
confirmed live against the already-pinned local hledger clone
Ledgerkit's own `hledger-researcher`/`compat-differential-tester`
tooling already references by convention), extracted eight file/
line-range selections with content-hash provenance, and materialized six
of them into `dev-docs/hledger-reference/*.md` in a **scratch copy** of
Ledgerkit (never the real clone — read-only throughout, same discipline
as Phase 46). The chosen task: produce an `hledger-researcher`-shaped
semantics brief for Ledgerkit's own next explicitly-deferred Stage C
query feature, `tag:` — run twice, once as today's real baseline
(live `WebFetch` + local grep, no CodeCompass involved) and once as the
treatment (CodeCompass query + the ingested material only).

### Results — a genuine, useful negative/mixed result, not a clean win

**Detection: positive, zero-code-change.** All six ingested files were
tracked with no "not found" error, via `spec_docs.py`'s pre-existing
`dev-docs/**/*.md` glob (Phase 49's own `CG-002` fix) — confirmed to
generalise beyond its original Ledgerkit-authored-docs motivation to a
materially different content class (externally-extracted, commit-pinned
reference text). Filed `OBS-007`.

**Relation: negative.** Mechanical `mentions_artifact` detection
produced **zero** edges between the ingested material and anything else
in the project, including Ledgerkit's own real
`dev-docs/hledger-compatibility.md` — root cause confirmed by direct
code reading: `spec_docs.py::scan_spec_docs` never populates
`doc_artifacts.name` for `spec_doc`-kind rows, and `mentions_artifact`
only matches named artifacts. This is a structural property of every
`spec_doc` row in *any* project, not specific to this content. Filed
`CG-004` (detection-improvement, Stage C/GATE-DB-scale — populate `name`
for `spec_doc` rows from a title/frontmatter, no new relation kind or
table needed).

**A working relation *fallback* exists, demonstrated real, not wired
into CodeCompass.** Parsing a compat-register YAML's own structured
`evidence.ref` citations and matching them against the pinned
extraction's file+line-range succeeded, real, against the actual,
already-published `LK-COMPAT-QUERY-DATE-001.yaml`
(`reference_pipeline.py::match_compat_register_evidence`, 12/12 tests
passing). More reliable than prose-mention inference because it reads
already-structured data rather than inferring a relationship — but this
mechanism currently lives entirely outside `src/codecompass/`. Filed
`OBS-008`.

**Provenance: a real classification gap.** The ingested material is
recorded as `origin='project'` — identical to Ledgerkit's own
hand-authored docs — because the existing 5-value `origin` CHECK enum
has no value for "externally-sourced, commit-pinned, content-hashed"
material. Filed `CG-005` (graph-capability, Stage E/GATE-DD-scale — a
new `origin` value, following the exact one-value-per-phase precedent
every prior enum extension used).

**A real, honest methodological defect, independently caught by
`context-evaluator`.** The `tag-query-manual` selection's hand-chosen
line range silently excluded the third of three tag-inheritance rules
while its own frontmatter description confidently claimed all three
were present — a false completeness claim inside the very artifact
whose value proposition is "trust this without re-checking it
yourself." `context-evaluator` independently verified this against the
real pinned manual and rated the **treatment run FAIL** (baseline: PASS
WITH GAPS; context advantage: **LOW**, not because the mechanism has no
value but because this specific defect gave the manual workflow's own
disclosed imprecision a cleaner track record on this task). Full report:
`planning/reference-projects/ledgerkit/reference-experiment/54-tag-query-semantics-reference-experiment-evaluation.md`.
Filed `L-020` (invariant: content-hash pinning proves an excerpt hasn't
silently changed; it does not prove the excerpt's boundary covers what
its own description claims). Fixed in the same phase (corrected line
range, regenerated artifact, new regression test) — the fix does not
retroactively change the FAIL verdict, which stands as the accurate
record of what the treatment run actually produced and claimed.

### Evidence for Phase 55/GATE DD (the plan's §7 checklist, answered)

1. Zero-schema-change hypothesis: **worked for detection, failed for
   relation.** A minimal schema addition (`origin` value) is warranted
   for provenance classification specifically, not a broad ontology.
2. Mechanical `mentions_artifact`: **found nothing**; the YAML-evidence
   fallback **worked**, demonstrated against real data.
3. Treatment evidence precision vs. `hledger-researcher`'s own hand-
   gathered citations: **not established as superior this run** — the
   treatment's own extraction had a real accuracy defect the baseline's
   more manual process did not (though the baseline had its own
   disclosed, different imprecision).
4. Context-advantage: **LOW**, verdict **FAIL** (treatment) / **PASS
   WITH GAPS** (baseline) — both from `context-evaluator`'s independent,
   ground-truth-checked report, not self-assessed.
5. `OBS-007`, `OBS-008`, `OBS-009`, `CG-004`, `CG-005`, `L-020` all filed
   this phase; none recurred from a prior phase (all first occurrences).
6. **Recommendation** (not a decision): the ingestion pipeline's core
   shape (resolve/lock/fetch/extract/hash) is sound and reusable: keep it
   Ledgerkit-specific and outside `src/codecompass/` for now, rather than
   generalising into a shipped feature. The two concrete graph gaps found
   (`CG-004`/`CG-005`) are each independently small and precedented
   (a `name` field, an `origin` value) and worth funding on their own
   narrow terms regardless of the broader ontology question — matching
   this project's own "smallest justified fix" precedent (Phase 47/49).
   The YAML-evidence-matching fallback is the single most promising path
   toward real provenance-based relation (more reliable than prose
   mention-detection), but should not be generalised until it's proven
   against a *second* real feature (not just `date:`/`tag:`, both from
   the same query-semantics family) — a genuine "not yet enough evidence
   to generalise" conclusion, not a rejection.

**This phase resolves the Stage D-vs-Stage-F/G decision's own open
question by having actually run the Stage D test** (Phase 51's retro)
— the answer is mixed/negative on the specific mechanism tried, not a
clean win, which is itself valid, reportable evidence per the plan's own
explicit "treat negative or inconclusive results as valid evidence"
instruction. Full retro: `planning/retros/phase-54-heterogeneous-reference-material-experiment.md`.
