# Phase 78 — Priority A exit decision: independent `knowledge-curator` triage

Independent triage of the real Phase 78 trial
(`planning/phase-78-priority-a-closeout-and-second-ledgerkit-trial.md`
§7.2, the phase's own terminal decision gate — "made at closeout, by an
independent `knowledge-curator` triage of the trial's real report, not
by the lead's own assertion"). This is not a rubber-stamp of the Stage 2
`context-evaluator`'s own verdict — every load-bearing claim below was
independently re-derived by direct reading of the real reports and the
real source code, per this role's own non-rubber-stamp discipline
(the same discipline that reversed Phase 75's provisional `CG-001`
`recurred` call and resolved `CG-009` at Phase 77).

Inputs read in full: this plan's §3/§4/§7, the three trial artifacts
(`06-stage-d-reportspec-stage1-baseline-report.md`,
`...-stage1-treatment-report.md`,
`06-stage-d-reportspec-priority-a-validation.md`), `planning/context-gaps/inbox.md`'s
full `CG-001` history (Phase 43c/47/72/75 curation notes) and `CG-009`'s
Phase 77 closeout curation note (precedent for how this file's own
format records a closeout disposition), plus direct reads of
`src/codecompass/graph.py` (full `CREATE TABLE` block) and
`src/codecompass/cli.py::_resolve_relations`/`query_relations`.

---

## 1. Independent re-verification of the `CG-001` outcome classification

**Claim under test**: Stage 2's own verdict, `CG-001` outcome
`not-recurred`, applicability confirmed (not `task-not-applicable`).

### 1.1 Applicability (§4's precondition, checked first)

Independently confirmed **applicable**. Both Stage 1 reports' own §2
sections derive, independently, the identical real producer/consumer
chain for a genuine, currently-unimplemented Stage D task:
`ledgerkit/parser.py` (new producer — must intercept inside the existing
unconditionally-discarding comment-line branch) → `Journal`
(`ledgerkit/models.py`, new storage field) → `ledgerkit/reports.py::balance_from_spec`
(existing, unchanged consumer) → `ledgerkit/cli.py` (new consumer, does
not exist today). This is not a task that happened to skip the
relationship question — both arms had to, and did, reconstruct this
chain to answer the task's own framing (§5.1's seven numbered
sub-questions). Confirmed directly against `ledgerkit/parser.py`'s
comment-handling logic as described in both reports (I did not re-clone
Ledgerkit myself to re-read `parser.py` line-for-line, but both
independently-authored reports — one with zero shared context with the
other, per the read-scope-symmetry boundary checks — converge on the
identical structural fact about the comment-line branch's unconditional
discard, which is strong corroboration two agents did not simply copy
from each other).

### 1.2 The two load-bearing claims, independently re-derived by me

1. **"CodeCompass's existing surfaces genuinely cannot answer the
   relationship question."** Read `src/codecompass/graph.py`'s full
   `CREATE TABLE` block directly: `source_symbols` (lines 95-108) has no
   edge table referencing it in either direction anywhere in the schema;
   `uses_edges` (lines 122-131) joins `source_file_id` to `vendor_id`/
   `symbol_id` — vendor-package symbols, never `source_symbols` rows.
   Read `src/codecompass/cli.py::_resolve_relations` (lines 778-823)
   directly: it resolves exactly three lookup shapes — a
   `doc_artifacts.path` match, a `vendors.name` match, or a
   `doc_artifacts.name` match — and returns `None` (→
   `_not_found_error`, line 464) for anything else. `ReportSpec` and
   `balance_from_spec` match none of the three, so `query relations
   ReportSpec`/`query relations balance_from_spec` erroring
   `'...' not found in context-graph.db` is explained exactly and
   completely by the code, not an artifact of this particular database's
   state or a transient bug. This independently confirms the central
   negative claim both Stage 1 reports and the Stage 2 report make.
2. **"The treatment agent reconstructed the chain at no greater cost
   than the baseline."** Read the treatment report's own "Research
   trace" section directly (not the Stage 2 report's summary of it): its
   own file-read ordering lists full reads of `models.py`, `reports.py`,
   and the decisive `parser.py` 955-1240 range (items 4, 5, 8) *before*
   any `codecompass query relations` call (items 3, 4 of the
   "CodeCompass queries invoked" list, by the report's own numbering —
   the two lists are chronologically consistent: direct reads precede
   CodeCompass queries). More decisively, the treatment report's own
   "Duplicated-research note" states in its own words, independent of
   any later evaluator gloss: "none of [the CodeCompass queries] told me
   something I'd already fully established from direct source reading
   ... they functioned as independent confirmation ... rather than my
   primary discovery mechanism for this investigation, which was
   necessarily driven by direct reading." This is the agent's own
   contemporaneous record, not the evaluator's later characterization of
   it. Independently cross-checked against the baseline report (zero
   CodeCompass access): it derives the identical chain via the same
   files (`models.py`, `reports.py`, `parser.py`'s comment branches,
   `cli.py`) at comparable depth and structure. Two independently
   dispatched agents, one with and one without CodeCompass, reaching the
   same conclusion by the same means, is real evidence the tooling gap
   did not impose extra cost on the one that had it — not merely the
   evaluator's impression of report "polish."

### 1.3 My own classification

**Confirmed: applicable, `not-recurred`.** Both of Outcome 2's
(§4) requirements are independently supported by evidence I re-derived
myself, not merely accepted from the Stage 2 report: (a) existing
surfaces could not answer the relationship question (schema + code
confirmed), and (b) the chain-tracing cost was not worse than baseline's
own direct exploration (both agents' own contemporaneous traces
confirmed, not just the evaluator's narrative). I found no basis to
reclassify this as `recurred` (no material, avoidable cost traceable
specifically to the tooling gap was found — the two failed `query
relations` calls are a self-corrected, few-seconds mistake, explicitly
logged as such by the treatment agent itself before any evaluator ever
reviewed it) or as a mislabelled `task-not-applicable` (the task
genuinely required the chain, confirmed above). **I agree with the
Stage 2 report's own classification.**

---

## 2. §7.2 decision-logic application

- **§7.2.0 (applicability gate):** does not fire — outcome is
  applicable, not `task-not-applicable`.
- **Branch A (Priority A closed):** fires, per my own independent
  confirmation above matching Outcome 2's bar exactly, backed by the
  Stage 2 `context-evaluator`'s own independent assessment (never the
  dispatched agents' self-reports alone — confirmed both were
  cross-checked against live code/trace evidence, by the evaluator and
  again by me).
- **Branch B:** does not fire (outcome is not `recurred`).

**I confirm Branch A fires.** This is my own independent determination,
not an acceptance of the lead's or the Stage 2 report's framing by
default — I found no evidentiary gap or misapplication of §4's criteria
that would change the outcome.

---

## 3. `CG-001`'s own inbox status — what this trial does and does not change

Per `context-gaps/README.md`'s own recurrence bar as this entry's own
three prior triage passes (Phase 43c, 47, and the Phase 75 reversion)
have consistently applied it: **a different concrete edge, on a
different project, independently derived by a different observer, is
this entry's own broader §2.6 hypothesis being tested again — not this
entry's own founding A↔B↔C edge
(`graph.py::skills_index` ↔ `cli.py::query_skills` ↔
`skill.py::render_tool_skill`) recurring.** Applying that discipline
consistently in both directions (as the Phase 75 reversion note itself
insists on — no laxer standard for one instance than every prior pass
applied): this trial's `not-recurred` result does not move `CG-001`'s
own `status` field either. It stays `candidate`.

What *does* change, at the track level rather than this entry's own
status field: this is the first time the broader hypothesis was tested
by a trial **designed in advance, with its evidence bar fixed before the
trial ran** (§4's three-outcome model), specifically to decide whether
it justifies new Priority A capability — and it returned an applicable,
independently-evidence-checked negative result. That is the evidentiary
basis for Priority A's strategic closure (§7.2 Branch A), operating on
Priority A as a track (`decisions/0062`), not via a status transition on
this one backlog entry. The full disposition note, in `context-gaps/inbox.md`'s
own established format, has been written to the inbox (§4 below —
already landed, see "CG-001 closeout entry" section).

---

## 4. `CG-001` closeout entry — already written to `planning/context-gaps/inbox.md`

A new `curation (Phase 78 closeout — Priority A exit decision, ...)`
note was appended to `CG-001`'s existing entry in
`planning/context-gaps/inbox.md` (after the Phase 75 reversion note),
following that file's own established format and the `CG-009` Phase 77
closeout note's precedent for structure. Its content (reproduced here
for this report's own completeness, the inbox copy is authoritative):

- Independently re-verifies both load-bearing claims by direct code
  reading (schema + `_resolve_relations`) and by direct reading of both
  Stage 1 reports' own research traces (§1 above, same content).
- Confirms applicability and the `not-recurred` outcome.
- Leaves `CG-001`'s own `status` unchanged at `candidate` (§3 above),
  with an explicit rationale for why this trial's result is evidentiary
  for Priority A's track-level closure without changing this entry's own
  recurrence-bar status.
- States explicitly that `CG-001` is not discarded — it remains
  reopenable by a genuinely new, differently-shaped occurrence.
- Re-confirms §3's full backlog disposition table (below).
- Notes no `promoted.md` line is added for `CG-001` itself (it was not
  promoted), and flags that the lead/`roadmap-context-curator` may add
  one for the ADR once it lands, as the actual landed artifact of this
  evidence trail.

---

## 5. Backlog disposition re-confirmation (§3, DoD item 4)

Checked individually against this trial's real evidence, not assumed
unaffected (the same discipline `CG-009`'s own Phase 77 closeout triage
applied):

| Item | Did this trial's evidence bear on it? | Disposition |
|---|---|---|
| `CG-001` | Yes — directly, this is its own trial (§1-3 above). | See above. |
| `CG-003` (external hledger manual) | No. The trial never queried or needed the external hledger manual; the treatment report's own open question 6.1 ("is `; report` a real hledger construct?") was investigated via `dev-docs/hledger-compatibility.md`'s own absence of any matching entry — internal doc, not the external manual. | Unchanged — still `candidate`, revisit trigger unmet. |
| `CG-007` (symbol-level cross-refs between pinned reference-doc excerpts) | No. The trial ingested no pinned reference material (`dev-docs/hledger-reference/`) at all. | Unchanged — still `candidate`. |
| `CG-009` (first-party source symbol path, resolved Phase 77) | Re-confirmed *working*, not merely unaffected: `query source-symbol ReportSpec`/`balance_from_spec` both returned correct rows, independently cross-checked against live source by the Stage 2 evaluator and, for the schema/code path, by me. | Unchanged — `promoted-to-roadmap`, resolution holds. |
| `CG-010` (submodule staged-vs-checkout ambiguity) | No. No submodule involved in this trial. | Unchanged — independent maintenance-backlog funding (§3.1) unaffected (confirmed, §6 below). |
| `CG-011` (sibling worktree staleness) | No. No worktrees involved. | Unchanged — still `candidate`, first occurrence. |
| Phase 24 (project-root REPL routing) | No. No `codecompass chat`/REPL routing exercised. | Unchanged — `deferred`. |
| Phase 25 (MCP server) | No. Orthogonal transport concern, not touched. | Unchanged — `deferred`. |
| Phase 50 remainder (shared-agent context/entry points) | No. Dispatch shape used ordinary `general-purpose` agents, no shared-agent entry-point question exercised. | Unchanged — `not funded`. |

§3's table is re-confirmed accurate at closeout. No new context-gap
candidate was identified as warranted by this trial beyond what both
Stage 1 reports and the Stage 2 report already fold into `CG-001`'s own
existing evidence trail (the "material gaps" the Stage 2 report names —
`query relations <doc-path>` not surfacing doc *content* relevant to an
unimplemented feature — is consistent with, not additional to, the
already-tracked doc-relations boundary; it was not filed as a new
`CG-NNN`, and I agree with that call).

No new `context-observations/` (`OBS-NNN`) entries were identified as
warranted by this trial's evidence beyond what is already captured
above — the one candidate instance (CodeCompass's accurate-but-stale
echo of `ReportSpec`'s own "Milestone 3" docstring) is a first-occurrence
`EDGE_USEFUL`/accurate-reflection case per `context-observations/README.md`'s
own investigate-vs-record rule — record-only, no investigation
triggered, and not load-bearing for this triage's own four tasks, so I
have not filed it as a new `OBS-NNN` entry myself; flagged here for
whoever next does a routine triage pass over this trial's reports if
they judge it worth a formal record.

---

## 6. `CG-010` independent-funding confirmation (§3.1)

Confirmed, not assumed: `CG-010` (`git_submodules` staged-vs-checkout
ambiguity) is Git-topology maintenance backlog, entirely unrelated to
this trial's task (journal-comment `ReportSpec` parsing touches no
submodule or Git-topology code path at all). Its own Phase 76 triage
note already classifies it as independently fundable, "never gated on
Priority A's own strategic exit decision" — this trial's result (Branch
A firing, Priority A closing) does not touch, weaken, or strengthen that
classification in any way. Confirmed unaffected.

---

## 7. If Branch A fires — the three further things required (§9/§10)

Per my own confirmation above that Branch A fires:

**(a) `planning/ROADMAP.md`'s Priority A row** needs updating to record
closure and its rationale. **This is outside this role's own write
scope** (`planning/ROADMAP.md` is not among `knowledge-curator`'s
writable paths) — **flagged for the lead** to action, using the
rationale in §7.2 Branch A of the Phase 78 plan (three real trials at
LOW-to-MODERATE advantage, plus this trial's own applicable,
evidence-checked negative result on `CG-001`) plus this triage's own
independent confirmation above.

**(b) A new ADR under `decisions/`** recording the Priority A closure
decision and its evidentiary basis. **Also outside this role's own write
scope** — drafted below (§8) for the lead to land verbatim or amend.

**(c) `CG-010`'s own independent maintenance-backlog funding is
confirmed unaffected** — done, §6 above.

---

## 8. Drafted ADR content (for the lead — not landed by this role)

Suggested filename: `decisions/0069-priority-a-closed-cg-001-tested-and-not-recurred.md`

```markdown
# 0069. Priority A (task-context completeness) is closed; `CG-001`'s own
relationship hypothesis was tested for real and did not recur

## Status

Accepted (Phase 78, [date], [confirm: direct user request / lead
decision following independent knowledge-curator triage —
planning/reference-projects/ledgerkit/06-priority-a-exit-decision-triage.md]).

## Context

`decisions/0062` opened Priority A (task-context completeness) as the
first of six post-v1 priority tracks, naming `CG-001` (task-oriented
retrieval edges — "what matters for this task" cannot be built from
existing graph data) as its founding, still-uncorroborated evidence.
Four real validations followed:

- Phase 73 (`CG-006`, filename-matching) — a detection fix, Stage-C
  scale, unrelated to `CG-001` directly.
- Phase 75 (Ledgerkit `cur:` query-term design) — `context-evaluator`
  verdict PASS WITH GAPS, advantage LOW. A provisional `CG-001`
  `recurred` call was made and then independently reverted by a
  `knowledge-curator` re-verification: the instance was a different
  concrete edge, on a different project, from `CG-001`'s own founding
  A↔B↔C edge — per this entry's own established recurrence-bar
  discipline, a cross-reference to the broader hypothesis, not a
  recurrence of this entry itself.
- Phase 76 (Git repository topology) — PASS WITH GAPS, advantage
  MODERATE, the strongest Priority A result to date. New gaps `CG-010`/
  `CG-011` filed (Git-topology maintenance backlog, independently
  fundable, unrelated to `CG-001`).
- Phase 77 (first-party source/symbol awareness) — PASS WITH GAPS,
  advantage LOW. `CG-009` (zero first-party-source symbol path)
  resolved. Its own plan explicitly deferred first-party *relationship*
  edges as "the most likely path to a genuine `CG-001`-shaped trial" —
  not committed to, not built.

Phase 78 claimed that deferred follow-on: it defined, in advance of
running any trial, a precise three-outcome evidence bar for `CG-001`'s
own hypothesis (`recurred` / `not-recurred` / `task-not-applicable`,
Phase 78 plan §4), then ran a second, differently-shaped Ledgerkit trial
(a genuine, currently-unimplemented Stage D task — journal-comment
`ReportSpec` parsing) structured specifically to exercise a real
producer/consumer chain of the same shape `CG-001` originally named,
using current CodeCompass (including Phase 77's `query source`/`query
source-symbol`).

The trial produced an applicable result (not `task-not-applicable`):
both a baseline agent (no CodeCompass) and a treatment agent (full
current CodeCompass) independently derived the identical real
producer/consumer chain (`parser.py` → `Journal` → `reports.py::balance_from_spec`
→ `cli.py`). CodeCompass's existing surfaces genuinely could not answer
the relationship question (`query relations ReportSpec`/`balance_from_spec`
both error "not found in context-graph.db" — confirmed by the schema
itself: no edge table exists between two `source_symbols` rows, or
between a `source_symbol` and anything else, anywhere in
`context-graph.db`). Despite this, the treatment agent reconstructed the
chain at no greater cost than the baseline's own direct exploration
(confirmed by both agents' own contemporaneous research traces, not
self-report alone, and independently cross-checked by both the trial's
own Stage 2 `context-evaluator` and a further independent
`knowledge-curator` re-verification). This is Outcome 2
(`not-recurred`) exactly as Phase 78's plan defined it in advance.

`CG-001`'s own inbox entry is **not** moved to `recurred` by this result
— applying the same edge-recurrence discipline this entry's own three
prior triage passes have consistently held (a different concrete edge,
on a different project, is the broader hypothesis being tested again,
not this entry's own founding edge recurring). It stays `candidate`,
reopenable by a genuinely new, differently-shaped occurrence. What this
trial's result *does* establish, at the track level: the one remaining
open question behind Priority A's own continued investment — whether
`CG-001`'s hypothesis would, once actually tested on a real task with a
pre-registered evidence bar, justify building new relationship-graph
capability — has now been tested for real, and found not to clear its
own bar.

## Decision

**Priority A (task-context completeness) is closed as a strategic
capability-building track.** Its own success criterion is judged met: an
independent `context-evaluator` PASS-or-PASS-WITH-GAPS record now exists
across three structurally different capability areas (query semantics —
Phase 75; Git repository topology — Phase 76; first-party source — Phase
77), at LOW-to-MODERATE advantage, never a FAIL and never a misleading
claim — plus, now, an explicit, pre-registered, evidence-checked
negative result on the one remaining open hypothesis (`CG-001`,
Phase 78). No new Priority A capability is funded on narrative alone
going forward; Priority A is not reopened absent new evidence of a
different, not-yet-tested shape.

**This closure is strategic, not operational.** It does not affect:

- `CG-010`'s own independent, already-evidenced Git-topology
  maintenance-backlog funding (`decisions/0062`'s §3.1 distinction,
  Phase 78 plan — ordinary maintenance within a capability Priority A
  already shipped is never gated on whether the track that funded it
  originally is still open to *new* capability-building).
- `CG-011`, if it ever independently recurs — the same maintenance-class
  disposition would apply.
- Any already-shipped Priority A capability (Git topology, first-party
  source, filename-matching) — all continue to be maintained on their
  own ordinary evidence.
- Priorities B-F (`decisions/0062`), which proceed on their own,
  unrelated schedule.

## Alternatives considered

- **Fund the smallest `CG-001`-shaped relationship edge anyway, on the
  strength of three prior LOW/MODERATE/LOW results plus this trial's
  qualitative narrative.** Rejected: Phase 78's plan explicitly
  pre-registered the evidence bar before running the trial specifically
  to avoid deciding this by narrative or assertion after the fact
  (`conditional-generalisation.md`'s premature-generalisation discipline,
  the same one `decisions/0062` already applied). The trial's own
  applicable result is a `not-recurred` outcome by that pre-registered
  bar; funding anyway would repeat exactly the mistake the bar was
  designed to prevent.
- **Run a third trial before deciding.** Rejected: Phase 78's own plan
  names this as the second, differently-shaped trial explicitly
  requested to settle the question (Phase 75's own retro, and Phase 77's
  own deferred-item note, both called for exactly this before any
  funding decision); a third trial without new reason to doubt this
  one's result would not meet the bar of "new evidence of a different,
  not-yet-tested shape" this ADR itself sets for reopening Priority A.
- **Treat this trial's `not-recurred` result as moving `CG-001`'s own
  inbox status.** Rejected by the independent `knowledge-curator` triage
  (`planning/reference-projects/ledgerkit/06-priority-a-exit-decision-triage.md`):
  this trial is a different concrete edge on a different project, which
  this entry's own three prior triage passes have consistently treated
  as evidence for the broader hypothesis, not a transition of this
  entry's own status, in either direction.

## Consequences

- `planning/ROADMAP.md`'s Priority A row is updated to record closure
  and this rationale.
- `planning/context-gaps/inbox.md`'s `CG-001` entry carries this trial's
  closeout note, status unchanged at `candidate`.
- `CG-010`/`CG-011` continue on their own independent, already-stated
  maintenance-backlog disposition (`decisions/0062` §3.1 cross-reference),
  unaffected.
- If a future phase surfaces new evidence of a genuinely different,
  not-yet-tested shape bearing on task-context completeness, it
  supersedes this ADR with a new numbered one (`CLAUDE.md` §2
  append-only rule), per `decisions/0062`'s own precedent for how this
  priority track is revisited.
```

---

## Summary table

| Item | Outcome |
|---|---|
| `CG-001` outcome classification | Independently re-verified: applicable, `not-recurred`. Agree with Stage 2 report. |
| §7.2 branch | **Branch A fires** (independently confirmed, not assumed). |
| `CG-001` inbox status | Unchanged — `candidate`. Closeout note appended (landed). |
| `CG-003`/`CG-007`/`CG-009`/`CG-010`/`CG-011`/Phase 24/25/50 | All re-confirmed unaffected/unchanged by this trial's evidence (§5). |
| `CG-010` independent funding | Confirmed unaffected (§6). |
| `planning/ROADMAP.md` Priority A row | **Lead action required** (outside this role's write scope). |
| New ADR | **Drafted above (§8), lead to land** as `decisions/0069-...md` (outside this role's write scope). |
| `promoted.md` | No line added for `CG-001` (not promoted). Lead may add one for the ADR once landed. |
