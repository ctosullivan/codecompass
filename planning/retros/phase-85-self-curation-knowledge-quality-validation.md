# Phase 85 retro — Self-Curation and Knowledge-Quality Validation

- **Date:** 2026-11-03
- **Commit(s):** this phase's own implementation commit (see `planning/
  CONTEXT.md`), preceded by the plan's own three amendment commits
  (`df99496`, `20a274c`, and the preceding `b3ef5c5`).
- **Agents used:** `context-researcher` (the real dogfood investigation,
  self-curation mode), `knowledge-curator` (independent adjudication of
  all four findings, twice-dispatched/resumed), `release-phase-auditor`
  and `docs-reconstructor` (closeout, below), `knowledge-curator` again
  (learnings/context-gap triage, below).

## Where we are

Phase 84's read-only knowledge API and Phase 83's oracle are both
`done`. This phase dogfoods the existing learning/curation lifecycle
against CodeCompass's own implementation for the first time as a
repeatable, documented procedure — not a new capability, but the
existing `context-researcher`/`knowledge-curator` roles, already used
reflexively against CodeCompass's own source before this phase (confirmed
by direct inspection of `first-party-source-symbols`'s own 74
pre-existing records), formalised into the loop `planning/phase-85-
self-curation-knowledge-quality-validation.md` describes.

## Goal

Demonstrate that CodeCompass can discover, investigate, independently
verify, curate, and preserve useful knowledge about its own
implementation — including correctly *rejecting* unsupported candidate
findings — without confusing a self-curation pass's own assertion with
established knowledge, per the roadmap's own stated circularity risk
(`decisions/0084` §3).

## Scope delivered vs planned

Delivered exactly the final amended plan's deliverables:

1. `docs/workflows/self-curation-loop.md` — the eight-step loop, the
   five-outcome disposition procedure, and the independent-adjudication
   contract, written for a future lead/agent to follow.
2. `planning/retros/phase-85-self-curation-investigation-log.md` — the
   new, append-only, non-canonical investigation log, populated with two
   real entries (`SCI-001`, `SCI-002`) from the real dogfood run.
3. `scripts/check_self_knowledge_quality.py` + `tests/test_check_self_
   knowledge_quality.py` (20 tests) — composing `knowledge_api.
   find_gaps()`/`knowledge_intermediate.knowledge_status()`/
   `trace_evidence()`/`oracle.parse_oracle_result()`, with a corrected
   `missing_contract` severity (always informational, grounded in
   `decisions/0081` §3), a new `test_ref`-file-integrity check (scoped
   to contract-bearing slugs only — a real scoping gap discovered while
   running it against the live corpus, not anticipated by the plan),
   and refined duplicate/overlap detection.
4. A real dogfood pass against `planning/knowledge/first-party-source-
   symbols/`, producing both required, independently-adjudicated
   outcomes (below).
5. Two narrowly-scoped, compatible agent-brief amendments
   (`.claude/agents/context-researcher.md`'s "Self-curation investigation
   mode," `.claude/agents/knowledge-curator.md`'s "Self-curation
   independent adjudication" mode) — no new role, no new tool grant, one
   narrow write-boundary addition (the investigation log) for
   `knowledge-curator` specifically.
6. **No change** to `src/codecompass/knowledge_api.py`, `oracle.py`,
   `knowledge_intermediate.py`, or any canonical record schema —
   confirmed by `git diff --stat` against this phase's own commit(s).

## What was achieved: the real dogfood, both outcomes

`context-researcher`, dispatched in its new self-curation mode, tried
four genuinely different, pre-registered constructs against the real,
unmodified `src/codecompass/source_symbols.py` extractors, each an
independent, falsifiable sub-question:

- **Positive outcome (promoted)**: two of the four constructs —
  (e) a visibility/export keyword on its own physical line (Rust `pub`,
  TS `export`), and (f) a `macro_rules!` template body containing a
  declaration-shaped line — genuinely defeated the extractors. Written
  as `OBS-FPSS-022/023/024` → `EV-FPSS-024` → `CL-FPSS-009`/`DE-FPSS-009`
  at `status: proposed`. `knowledge-curator`, independently reproducing
  (by directing the lead to re-run the exact probes, since it has no
  `Bash`, and by independently re-deriving the mechanism from the real
  regex source directly) and finding no disagreement, recommended
  promotion; the lead applied it (`status: supported`). Requeried via
  `knowledge_api.get()`/`trace_evidence()`/`epistemic_status()` —
  resolves with zero gaps.
- **Negative outcome (declined)**: the other two constructs — a Rust
  `#[cfg(test)]`-gated declaration, and a TS decorator-prefixed
  declaration — were both genuinely tried and found *not* to defeat
  either extractor. `knowledge-curator` independently corroborated both
  falsifications via direct source reading (not merely the probe's own
  report) and wrote `SCI-001`/`SCI-002` into the investigation log,
  citing the lead's own real, unmodified command output. **Nothing was
  written under `planning/knowledge/` for either** — confirmed by
  `git status`.

Neither outcome was pre-invented: both were genuinely unknown before the
dispatch ran, and the investigation tried enough genuinely different
constructs in one bounded dispatch that both halves of the gate were
satisfied without needing the plan's own pre-authorised second
extension.

## What worked

- **The declared-scope, try-several-constructs design** (§7 of the
  amended plan) paid off exactly as intended: trying four independent
  sub-questions in one dispatch produced both a genuine positive and a
  genuine negative from a single bounded investigation, with no need for
  the pre-authorised extension.
- **The tool-boundary split for executable evidence** (`knowledge-
  curator` specifies the exact command; the lead executes verbatim;
  `knowledge-curator` incorporates the real output) worked cleanly in
  practice, across two separate resumption rounds, and `knowledge-
  curator` went further than the minimum — independently re-deriving the
  mechanism from the real regex source directly, not merely trusting the
  lead's pasted output, for every one of the four findings.
- **The deferred-write mode** worked exactly as designed: `context-
  researcher` tried all four constructs, wrote nothing for the two that
  didn't pan out, and committed only the two that did — no orphaned or
  unintended canonical record appeared anywhere.
- **Running the new validator against the real corpus before writing its
  own tests** (rather than only against constructed fixtures) caught a
  real design gap immediately: the original `test_ref`-file check would
  have false-positived on four pre-existing, legitimate, pre-Phase-82
  Evidence records in non-contract-bearing slugs. Fixed by scoping the
  check to contract-bearing slugs only, and written up as the governing
  prompt's own explicit instruction ("independently investigate any new
  strict-validation failures rather than automatically suppressing
  them") was followed in practice, not just stated.

## What didn't work / was harder than expected

- **A resumption mistake**: after knowledge-curator's first dispatch
  asked the lead to report back command output, the lead re-dispatched
  a *fresh* `knowledge-curator` agent (a new `Agent` call) instead of
  resuming the same one via `SendMessage` — losing that agent's own
  working context (though not its already-written investigation-log
  draft content, since the fresh dispatch re-read the same source files
  and reconstructed equivalent, arguably stronger, independent
  corroboration). No incorrect output resulted, but it was less
  efficient than resuming the original dispatch would have been, and is
  exactly the mistake this project's own tooling guidance warns against.
  Filed as a candidate learning, below.
- **`--strict` genuinely fails against the real baseline**, and by
  design: `self-knowledge-quality-contradiction` (a real, pre-existing,
  accepted `CONTESTED` Claim, `CL-ADPT-008`), `self-knowledge-quality-
  unverified-required-scope`/`stale-test-citation` (a real, pre-existing
  gap in `balance-from-spec`'s own oracle coverage, independently
  cross-confirmed against `check_contracts.py`'s own `contract-check-
  gap` finding for the identical `check_id`) all predate Phase 85 and
  are explicitly out of its own scope to fix (fixing them would mean
  resolving Phase 82/83/84-era oracle/domain questions unrelated to
  self-curation). The test suite deliberately does not assert zero
  blocking findings against the real corpus, unlike `check_contracts.
  py`'s/`check_knowledge_base.py`'s own sibling tests — documented
  explicitly in the new test file's own module docstring, not silently
  diverged from the established convention.

## Lessons learnt

1. **A validator's severity design must be checked against the real
   corpus before, not after, writing its own test suite** — a design
   that looks correct in the abstract (every `find_gaps()` rule except
   `missing_contract` stays blocking) can still misfire on a real,
   pre-existing population the plan's own authors didn't anticipate (the
   four pre-Phase-82 `test_ref` citations using an older, legitimate
   convention). Running the real script against the real corpus
   immediately, before the test suite locks in assumptions, caught this
   in minutes rather than as a later false-positive bug report.
2. **Resuming a dispatched agent via `SendMessage` matters, not just as
   an efficiency nicety** — a fresh re-dispatch can still reconstruct
   correct output (as it did here), but it forfeits the original
   session's own accumulated independent-verification state and risks
   subtly different framing on a second pass. Candidate learning filed.

## Process-improvement feedback

None beyond the above — the amended plan's own three-review cycle
(original authoring, post-amendment review, post-second-amendment
review) meant implementation itself surfaced only one genuinely new
design gap (the `test_ref`-file scoping issue), caught and fixed
immediately rather than discovered later.

## Candidate learnings filed

See `knowledge-curator`'s own triage, below (this retro's own "Lessons
learnt" §1/§2 are the source candidates).

## Where we're going

Phase 85 is the last phase before Phase 86 (Knowledge-Placement and
Code-Quality Review) becomes next-eligible. Phase 86 is **not**
authorised by this phase's own governing prompt and is not started —
each remaining phase (86-92) still requires its own `CLAUDE.md` §1 plan
file, scoped against evidence current when it is actually next.

## Time / cost note

Three independent-review rounds on the plan amendment (one before this
session, two during it), one real dogfood dispatch (four constructs
tried), two `knowledge-curator` adjudication dispatches (one fresh, by
the mistake noted above, functionally equivalent in outcome), and one
real design fix discovered by running the new validator against the
real corpus before finalising its test suite.
