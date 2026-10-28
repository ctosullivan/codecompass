# Phase 84 retro — Consolidated Knowledge API and Query CLI

- **Date:** 2026-10-29
- **Commit(s):** `0b4f321` (implementation), `decisions/0091` (same
  commit). Preceded in the same session by `2436e39`/`fad3a89` (Phase
  83's own final corrective amendment and its independent audit —
  unrelated in content, sequenced first by the governing prompt).
- **Agents used:** `release-phase-auditor` (Phase 83's final amendment,
  and this phase's own closeout, dispatched separately — see below),
  `knowledge-curator` (pending, this phase's own learnings triage).

## Where we are

This is the first phase of the v2-redefinition roadmap's second real
deliverable group (`planning/v2-roadmap.md`), built directly on Phase
82's oracle/contract foundation and Phase 81's intermediate-knowledge
layer — both already `done` and, per `decisions/0084`/`0085`'s own
explicit sequencing, independent of Phase 83 (which this session also
closed out, in the same prompt, immediately before this phase began).
After this phase, CodeCompass has one stable, read-only, typed query
surface over its three previously-separate knowledge stores
(`context-graph.db`, `planning/knowledge/`, `planning/contracts/`) —
the shared read interface later phases (85's self-curation, 88's MCP
surface) are meant to build on rather than re-deriving graph SQL or a
`planning/knowledge/` file walk themselves each time.

## Goal

Build one read-only, typed interface consolidating access to mechanical
graph facts, reconciled knowledge records, and behavioural-contract
verification, preserving the differences between stated intent,
accepted obligation, observed behaviour, and scoped verification — and
prove it with new CLI operations, one real migrated command, and a
real-corpus dogfood demonstration, per the plan's own nine-point logical
model and three mandatory architectural considerations (stable
identities, snapshot consistency, authority separation).

## Scope delivered vs planned

Delivered exactly the plan's §4 deliverables: `src/codecompass/
knowledge_api.py` (`get`/`search`/`traverse`/`trace_evidence`/
`epistemic_status`/`find_gaps`/`get_context_packet`/`export_snapshot`);
six new read-only CLI commands under the existing `knowledge` sub-app;
`query relations` migrated onto the same API's own `doc_mentions`
relation, confirmed byte-identical output before and after (both via
the project's own 14 pre-existing tests, unmodified, and one new
dedicated full-string-comparison test). The plan's own §10 "unresolved
decision" (the exact `ContextPacket` shape) was resolved during
implementation and recorded in `decisions/0091`, exactly as the plan
itself anticipated — not a deviation.

One addition beyond the plan's own letter, within its spirit: the plan
named `graph.open_graph`/`rebuild_deterministic` only implicitly as
"existing storage readers... reused" (§6 names only `knowledge_
intermediate.py`/`oracle.py` explicitly in its own no-mutation-path
test). Because `graph.open_graph` itself creates the database file and
runs schema migrations as a side effect of *opening* it — a mutation
this module must never cause incidentally — `knowledge_api.py`
deliberately never calls it, connecting to `context-graph.db` read-only
via a `file:...?mode=ro` URI instead (`decisions/0091` §3). This is a
stricter reading of §6's own intent, not a narrower one.

No scope was dropped. No architecture named by `decisions/0084`/`0085`
was reopened.

## What was achieved

A working, tested, documented module and CLI surface, demonstrated
against this project's own real `balance-from-spec` knowledge and the
real `~/projects/ledgerkit` checkout (never the real checkout's own
files touched) — not merely asserted. The dogfood independently
recomputed every claim it made (a real oracle PASS via `oracle.
evaluate_result_precedence`, a real `source_symbols` row via direct
SQL, a real zero-results check for the still-outstanding overlapping-
pattern check) rather than trusting the API's own report of itself.
`find_gaps`, run for real, surfaced a genuine, pre-existing knowledge-
currency gap in this project's own corpus (`L-107`) — the one concrete
piece of evidence that this phase's "genuinely new cross-cutting
capability" claim (plan §3.0 point 6, the thin-wrapper risk's own
mitigation) is real, not aspirational.

## What worked

- **Grounding the identity scheme in a real, already-shipped precedent**
  (`decisions/0038`'s `doc_relation_enrichment` natural-key table) made
  the §3.A design essentially mechanical to implement and test — no
  genuinely new concept, just a consistent string encoding applied to
  facts the schema already exposes.
- **Testing the "wholesale-rebuilt-edge-table" identity-instability
  claim directly against `graph.py`, rather than trusting its own
  docstring**, caught a real subtlety: a plain `INTEGER PRIMARY KEY`
  (no `AUTOINCREMENT`) reuses the lowest free rowid after a full-table
  `DELETE`, so a single-row fixture rebuilt twice in a row can
  deceptively get the *same* id back both times. The eventual test
  (two relations, swapped insertion order between rebuilds) demonstrates
  the real risk properly; the first draft's naive `id_after > id_before`
  assertion would have been a flaky, misleading pass/fail depending on
  row count.
- **Running the real dogfood before writing the final report**, not
  after, caught two real implementation gaps on the way: `traverse(...,
  "checks")` didn't strip the `contract:` prefix from a qualified id
  (worked only for a bare `contract_id`), and `traverse(..., "results")`
  rendered a result's own recorded `outcome` without computing its
  *effective* outcome — which would have silently presented three
  historically-PASS-but-now-INVALID results as current verification,
  the exact failure mode `decisions/0085`'s own governing principle
  rules out. Both were fixed before this retro was written, not after.

## What didn't work

- The no-mutation-path static test's first draft matched forbidden
  writer-function *names* as bare substrings (`"graph.open_graph"`,
  `"rebuild_deterministic"`), which the module's own docstring
  legitimately mentions while explaining *why* it avoids them — a false
  positive against the module's own prose, not its code. Fixed by
  matching the call form (`"open_graph("`) instead, which cannot appear
  in prose describing the function without also being an actual call.
- Two of the first-draft consistency-envelope tests used hand-rolled
  "fake" digests (`"d" * 64`) for a result meant to demonstrate the
  `repo_root`-reachable "current" case — which, correctly, `evaluate_
  result_precedence` rejects as `INVALID` the moment a real `repo_root`
  is supplied, since the digest was never going to match a live
  recomputation. Fixed by computing real digests via `oracle.
  compute_tree_digest` against the fixture's own real files. A
  reasonable mistake in isolation, but one that cost a full extra
  debugging pass — a test meant to prove "current" needs to actually
  earn that outcome through the same mechanism a real result would,
  not merely assert a hardcoded status.

## Lessons learnt

A static source-text scan for "does this module call forbidden function
X" needs to match the call form, not the bare identifier — a
well-documented module will legitimately name the thing it avoids in
its own rationale, and a substring match can't tell the difference
between "calls X" and "explains why it doesn't call X." More generally:
when a test's own purpose is to demonstrate a *mechanism* working
correctly (digest recomputation, row-id volatility), build the fixture
through that exact mechanism's own real inputs rather than a
hand-picked stand-in value — a stand-in only proves the code path was
reached, never that it reached the *intended* outcome for the right
reason.

## Process-improvement feedback

None beyond the above — this phase ran as a single, long implementation
session with no agent-handoff friction (the one subagent dispatch
tracked in this retro, `release-phase-auditor`, was for the preceding
Phase 83 amendment, not this phase itself; this phase's own audit is
dispatched separately after this retro is written, per the normal
sequencing).

## Candidate learnings filed

`L-107` (`planning/learnings/inbox.md`, status `candidate`) — extending
an oracle contract with a new required check can leave pre-existing
Evidence citing now-invalid historical results, with nothing prompting
a re-citation to the fresh confirming results Phase 83 itself generated;
`knowledge_api.find_gaps`'s own `stale_test_citation` rule is the first
mechanism in this project that names this condition. Pending
`knowledge-curator` triage.

## Where we're going

This phase unblocks Phase 85 (Self-Curation and Knowledge-Quality
Validation, which the roadmap already names as consuming "Phase 84's
API and Phase 83's oracle") and Phase 88 (Agent Integration and MCP,
which the roadmap names as building its own surface "on Phase 84's
API"). Neither is authorised to begin under this phase's own governing
prompt. This phase's own outcome **confirms** the planned trajectory —
no scope shift, no finding that reshapes a later stage. The one
cross-cutting, non-blocking finding (`L-107`) does not gate Phase 85;
it is exactly the kind of knowledge-quality observation Phase 85's own
self-curation dogfooding is meant to eventually act on.

## Time / cost note

One extended session (continuing from the prior Phase 83 corrective-
pass session in the same conversation). No AI API spend — this phase
makes no model call anywhere in its own code (consistent with plan §6's
"no unnecessary AI inference" exclusion); all development/test cost was
this session's own tool use.
