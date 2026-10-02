# `CG-001` corrective re-evaluation — Phase 78 Ledgerkit Stage D trial

**Nature of this document.** This is a pure re-analysis of evidence already
on disk. No agent was dispatched, no repository (CodeCompass or Ledgerkit,
real or scratch) was touched, and no `codecompass` command was run to
produce this report. Ground truth is drawn exclusively from the three
existing artifacts named below, read in full before this analysis began:

- `planning/phase-78-priority-a-closeout-and-second-ledgerkit-trial.md` §4
  (the original `CG-001` evidence-bar definition — treated here as the
  object under correction, not as authority).
- `planning/reference-projects/ledgerkit/06-stage-d-reportspec-stage1-baseline-report.md`
  (Stage 1 baseline report + its own research trace).
- `planning/reference-projects/ledgerkit/06-stage-d-reportspec-stage1-treatment-report.md`
  (Stage 1 treatment report + its own research trace — primary evidence
  source for this re-analysis).
- `planning/reference-projects/ledgerkit/06-stage-d-reportspec-priority-a-validation.md`
  (original Stage 2 `context-evaluator` report — analysed here, not
  inherited).
- `planning/reference-projects/ledgerkit/06-priority-a-exit-decision-triage.md`
  (the downstream `knowledge-curator` triage that acted on Stage 2's
  verdict — read for completeness; its own reasoning is shown below to
  **inherit the same flaw** being corrected here, which matters for how
  much weight the existing Branch A closure should be read as resting on).

## The flaw being corrected, restated precisely

Phase 78 plan §4 Outcome 2 required only that the treatment agent's cost be
"no worse than the baseline agent's own direct exploration." Both Stage 2
and the `knowledge-curator` triage applied exactly this relative-parity
test as their decisive evidence (Stage 2: "a cost no worse than the
baseline's own direct exploration... satisfies §4 Outcome 2's bar
exactly"; triage §1.2 point 2: "the treatment agent reconstructed the
chain at no greater cost than the baseline" cited as one of the "two
load-bearing claims"). Parity between two arms that both lack the
capability is uninformative about whether the capability, if built, would
help — it only shows the two arms were equally (un)helped. This
re-analysis instead asks the absolute question directly.

---

## Part 1 — Two separated questions

### 1a. `CG-001` outcome under the corrected (absolute) test

**Question**: did the treatment agent incur material, avoidable manual
effort specifically because current CodeCompass could not supply a
first-party relationship fact it needed?

**What the treatment agent actually did, in trace order** (treatment
report, "Research trace" section):

1. Full/targeted reads of `dev-docs/api-spec.md`, `ROADMAP.md`,
   `models.py` (full, 535 lines), `reports.py` (full, 697 lines),
   `06-core-architecture.md` (full), `docs/python-api.md` (targeted),
   `parser.py` (targeted, offsets 955-1185 and 1195-1240), `cli.py` (full,
   509 lines) — items 1-11 of "Files read," **all completed before any
   CodeCompass query is invoked** (confirmed by the report's own
   "CodeCompass queries invoked" list, items 1-12, which comes after and
   is explicitly framed by the agent as confirmation, not discovery).
2. Only after this direct-reading pass does the agent run
   `codecompass query source-symbol ReportSpec`, `query source-symbol
   balance_from_spec`, `query source ledgerkit/reports.py`, `query source
   ledgerkit/cli.py` (items 1, 2, 10, 11) — each returns information the
   agent's own trace says duplicates what the preceding full-file reads
   already established ("no new facts, but confirmed the index is
   current," item 1; "no new facts, confirmed index currency a second
   time," item 10).
3. The agent then runs `query relations ReportSpec` and `query relations
   balance_from_spec` (items 3-4) — **this is the one place the agent
   directly tested whether CodeCompass could answer the actual
   relationship question** ("which functions in `reports.py`/`cli.py`
   already reference `ReportSpec`, and which do not yet call
   `balance_from_spec`" — Phase 78 plan §6's own named sub-question). Both
   error `'...' not found in context-graph.db`. The agent's own
   "Duplicated-research note" records this cost explicitly: it was a
   mistaken assumption about `query relations`'s scope, corrected within
   two calls by reading `--help`, described by the agent itself as
   "redundant with each other" but otherwise immaterial — no further
   investigative path was blocked or re-walked because of it.

**Where did the agent actually get the relationship answer?** From
`reports.py`'s full-file read (item 5 of "Files read") — a read the agent
needed regardless, to write §3 ("execution path") and §7 ("proposed
design"), both of which require deep understanding of `balance_from_spec`'s
internals (`_matches_pattern`, the Stage C Phase 8 query-convergence
comments, `ReportSectionResult`'s shape). The marginal cost of also
noting, while reading that file anyway, "this is the only function here
that touches `ReportSpec`/`ReportSection`" is not separable from the cost
already paid for the design task's other requirements — there is no
observable point in the trace where the agent stopped, searched
specifically and only for "who else uses `ReportSpec`," and paid an
additional, avoidable cost beyond the two cheap, self-corrected
`query relations` calls. The same holds for `cli.py` (509 lines, already
needed to understand the CLI dispatch pattern for §3/§7's CLI-wiring
proposal; confirming "no `report`-related code exists" falls out of that
same full read for free, independently reconfirmed by `query source
ledgerkit/cli.py`'s six-symbol list).

**The one substantial, separately-identifiable investigative cost in the
trace** is the `parser.py` 955-1240 read, which the agent itself calls
"the single most important read for the whole investigation" and whose
correction of an initial wrong assumption (that `comment`/`end comment`
is directly reusable scaffolding) is called "the single most significant
correction in this investigation." This is real, non-trivial cost. But it
is **not** a first-party relationship-indexing question at all: what the
agent needed was the *execution order of branches inside one existing
function* (`_parse_string_impl`'s if/elif dispatch chain) — a
control-flow fact internal to a single function body, not an edge between
two first-party symbols, files, tests, or docs of the kind Phase 77's
plan named as the candidate relationship-edge shapes
(`source_file → imports`, `source_symbol → references/calls`,
`test → tests`, `doc → documents`). No plausible version of a
relationship-indexing capability — including the hypothetical ones named
in this task's own framing ("what calls/references symbol X," "what does
function Y's own parameter type connect to") — would expose branch
dispatch order inside one function. The baseline agent paid the
structurally identical cost for the structurally identical reason (its
own report, §1, independently derives the same "comment-line branch
unconditionally discards" fact from the same file, at comparable length),
confirming this cost is intrinsic to the codebase's complexity, not
attributable to a CodeCompass capability gap of any kind.

**Conclusion (1a): `not-recurred`**, under the corrected, absolute-cost
test — not merely re-affirming the original relative-parity conclusion,
but independently re-derived from it: the one existing relationship a
capability could have exposed (`ReportSpec`/`ReportSection` ↔
`balance_from_spec`) was obtainable at effectively zero marginal cost on
top of reads the task already required for other reasons, and the one
materially costly investigation in the trace (`parser.py`'s dispatch
order) is outside the scope of what any first-party relationship-indexing
capability — real or hypothetical — could have shortened. No instance of
material, avoidable manual effort specifically attributable to the
missing capability was found in the treatment agent's own trace.

**Caveat on confidence**: the trace records *what* was read and in what
order, and the agent's own contemporaneous characterization of which
reads "added new facts," but it does not record wall-clock time or token
cost per read. The "effectively zero marginal cost" conclusion above is
inferred from trace structure (the relevant fact was obtainable from a
read already necessitated by other, unavoidable parts of the task), which
is a reasonable basis for the conclusion but not a stopwatch measurement
— flagged honestly rather than overstated.

### 1b. Context advantage (independent rating, may use baseline parity)

**LOW — unchanged from the original Stage 2 verdict**, and this rating is
legitimately informed by baseline comparison (unlike 1a): the treatment
report's own chronological ordering (direct reads first, CodeCompass
queries after and explicitly self-described as confirmatory) combined
with the baseline report independently reaching the same
producer/consumer chain, same open design questions (8 vs. 6, substantial
overlap in substance), and comparable depth (treatment 772 lines vs.
baseline ~744) with zero CodeCompass access, is direct evidence that
CodeCompass's working queries (`source-symbol`, `source`) did not move
the treatment agent's outcome measurably relative to baseline. The one
query type that could have differentiated the arms (`query relations`)
returned nothing usable. A fresh Claude session with only `grep`/`Read`
access would have obtained everything CodeCompass's working queries
supplied, via the same 2-3 full-file reads both arms actually performed.
This is a genuine LOW, not a rounded-up LOW — consistent with Phase 75/77
precedent for this same small, well-organised codebase.

---

## Part 2 — Applicability: existing vs. proposed relationships

The derived chain: `parser.py` (new producer) → `models.py`'s `Journal`
gaining a new field (new) → `loader.py::merge_journals` extension (new) →
`reports.py::balance_from_spec` (**existing, unchanged** — both reports
confirm its signature `balance_from_spec(journal, spec, query=None)` is
untouched, treatment report line ~42-53, baseline report line ~29-41) →
`cli.py` gaining a new `report` command (new — both reports independently
confirm via direct read of the `COMMANDS` tuple, treatment report line
~101, baseline report line ~89-93, that no such command exists today).

**The one existing-to-existing relationship in this chain**:
`ReportSpec`/`ReportSection` (`models.py:198-237` per the task's own
citation, confirmed by both reports' line citations: treatment "line
~219," baseline "line ~219") ↔ `balance_from_spec` (`reports.py:600`,
confirmed by both reports' identical line citation). Both of these
entities exist today, and the relationship between them (the function
already consumes the dataclass as a parameter) is already live in the
codebase — this is the only part of the chain a first-party
relationship-indexing capability, present or hypothetical, could in
principle have exposed, since indexing can only describe relationships
between code that already exists.

**Everything else** — the new parser-side comment-block recognition
logic, the new `Journal` storage field, the new `loader.py::merge_journals`
extension, the new CLI `report` command — involves at least one
not-yet-existing entity on one side of the relationship. No
relationship-indexing capability, however complete, can expose an edge
whose destination or source has not been written. Tracing these was
inherent design effort (deciding *how* the new code should relate to the
old), not a retrieval task any graph could have shortened.

**Measuring where the agents' own effort actually went** (by section,
both reports have near-identical structure):

- §1 (existing source) and the existing-relationship-specific portion of
  §2 (the `balance_from_spec`-is-the-only-consumer finding, the
  `_matches_pattern` validation-routing note): a compact fraction of each
  report, resolved quickly via full-file reads already required for other
  purposes (Part 1a above).
- §2's remaining diagram content (3 of 4-5 boxes marked "NEW"), §3
  (execution path — almost entirely "NEW" steps 1-2, 6 in the treatment
  report's own numbering), §6 (8 of 8 / 6 of 6 open questions in both
  reports concern grammar design, CLI composition, error-handling
  strategy, and field shape — none of these are answerable by any
  relationship capability, because none of the entities in question
  exist yet), and §7 (an entirely invented grammar proposal): this is the
  dominant share of both reports by length and by the agents' own
  framing of where the real uncertainty lay.
- The `parser.py` dispatch-order investigation (Part 1a above): real,
  substantial cost, but — as established above — orthogonal to the
  relationship-indexing question entirely (an intra-function
  control-flow fact, not a symbol/file/test/doc edge).

**Applicability verdict: partial.** The task did exercise a genuine,
existing, discoverable relationship (`ReportSpec`/`ReportSection` ↔
`balance_from_spec`) — this was not skipped, and both agents explicitly
attempted to query it via `query relations`, producing real, checkable
evidence of absence. But this was a thin slice of the agents' total
effort. The substantial majority of what both reports present as
"producer/consumer chain tracing" is, on inspection, either (a) design
work for relationships that do not yet exist (unaffected by any
relationship-indexing capability, present or future) or (b) an
intra-function control-flow investigation that falls outside the
relationship-indexing hypothesis's own scope (edges between first-party
symbols/files/tests/docs, not branch order within one function body).
This was not flagged as a distinction anywhere in the original Stage 2
report or the `knowledge-curator` triage — both treated "the
relationship question" as a single undifferentiated thing spanning the
whole chain, which overstates how much of the trial's apparent
chain-tracing cost actually bears on `CG-001`'s hypothesis.

---

## Part 3 — Corrected decision tree applied

Per the task's tree: not-"did-not-exercise" (→ inconclusive), but also
not a full, undiluted exercise of the hypothesis — a **partial** exercise
is the honest middle finding from Part 2. Applying the tree to the thin
slice that *was* genuinely exercised (not to the chain as a whole, which
would overcredit the result): that slice was exercised, and its
discovery was **not materially costly** in absolute terms (Part 1a) — the
answer was obtainable at near-zero marginal cost from reads the task
required regardless, and the two failed `query relations` calls cost a
self-corrected few seconds.

**Resulting classification: `not-recurred`**, but held with **markedly
lower confidence than either the original Stage 2 report or the
`knowledge-curator` triage expressed**, because:

1. The classification rests on the same final label the flawed
   relative-parity test produced, but for a different and narrower reason
   — a genuine absolute-cost finding on a thin slice of real evidence,
   not a parity claim over the whole chain.
2. Because applicability is only *partial*, this trial supplies
   meaningfully weaker evidence for `CG-001`'s hypothesis than a trial
   whose task required more first-party existing-relationship tracing
   relative to new-code design would have. A reader of the original Stage
   2 report or the ADR draft in the `knowledge-curator` triage (§8) could
   reasonably come away believing the *entire* producer/consumer chain
   was put to the test and found not to matter — that overstates what
   actually happened. Only one link in a five-link chain was a genuine
   existing-relationship test; the other four links' design cost would
   have been identical with or without any conceivable relationship
   capability.
3. This re-analysis does **not** recommend reopening Branch A/Priority A
   closure on this basis alone — the final label (`not-recurred`) is
   unchanged — but it is a material correction to the *strength* and
   *precision* of the evidentiary claim underlying that closure, which
   should be reflected if the governing ADR (`decisions/0069`, drafted in
   the `knowledge-curator` triage §8) is ever revisited or cited as
   precedent for a future Priority A question. In particular, the ADR
   draft's own Context section — "the treatment agent reconstructed the
   chain at no greater cost than the baseline's own direct exploration"
   — is the same relative-parity formulation this corrective
   re-evaluation set out to replace; the corrected framing (this
   document) should be the basis for any future reliance on this trial
   result, not the original ADR language.

---

## Evidence summary with citations

| Finding | Citation |
|---|---|
| Existing relationship: `ReportSpec`/`ReportSection` ↔ `balance_from_spec` | `06-stage-d-reportspec-stage1-treatment-report.md` §1 ("`ReportSpec` (frozen dataclass, line ~219)"), §1 ("`balance_from_spec(...)` (line 600) is the only consumer of `ReportSpec`/`ReportSection` today"); corroborated independently by baseline report §1, same line citations. |
| New/not-yet-existing links: parser producer, `Journal` field, `merge_journals` extension, CLI command | Treatment report §2 diagram (3 of 4 stages marked "NEW"); §3 steps 2-4, 6; `cli.py` `COMMANDS` tuple confirmed to lack `report` (treatment §1, line ~101; baseline §1, line ~89-93). |
| CodeCompass could not answer the relationship question directly | Treatment report, CodeCompass queries 3-4: `query relations ReportSpec` / `query relations balance_from_spec` both `error: '...' not found in context-graph.db`. |
| Relationship answer obtained at near-zero marginal cost from reads already required | Treatment report "Files read" items 4-5 (`models.py`, `reports.py` full reads) precede CodeCompass queries 1-2/10 chronologically; queries 1/10 self-described as adding "no new facts." |
| Substantial but out-of-scope cost: `parser.py` dispatch order | Treatment report "Files read" item 8 ("the single most important read for the whole investigation") and "Assumptions made, then corrected" #2 ("the single most significant correction in this investigation"); baseline report independently performs the equivalent read (its own "Files read" items 3, 5) and reaches the same structural conclusion with zero CodeCompass access, confirming this cost is intrinsic to the codebase, not tooling-attributable. |
| Original evaluation's relative-parity framing, now superseded | `06-stage-d-reportspec-priority-a-validation.md`, `CG-001` verdict §2: "a cost no worse than the baseline's own direct exploration... satisfies §4 Outcome 2's bar exactly." |
| Downstream triage inherited the same framing | `06-priority-a-exit-decision-triage.md` §1.2 point 2 ("the treatment agent reconstructed the chain at no greater cost than the baseline" listed as a "load-bearing claim"); ADR draft §8 Context section, same language. |

---

## Bottom line

- **`CG-001` outcome (corrected rule): `not-recurred`.**
- **Context advantage: LOW (unchanged).**
- **Applicability: partial** — one genuine existing-relationship test
  (thin), four new-design links (not testable by any relationship
  capability) plus one out-of-scope control-flow cost, both inflating the
  apparent size of "the relationship question" without actually bearing
  on it.
- The final label matches the original evaluation's conclusion, but the
  original's own reasoning (and the downstream ADR language) rests on a
  test (relative parity) this re-analysis does not accept as valid, and
  overstates how much of the trial actually exercised the hypothesis. The
  corrected, narrower reasoning in this document — not the original
  framing — should be treated as authoritative if this trial result is
  ever cited again.
