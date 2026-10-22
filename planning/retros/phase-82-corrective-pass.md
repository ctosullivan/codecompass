# Phase 82 corrective-pass retro

- **Date:** 2026-10-22
- **Commit(s):** `078196c` (ADR + plan §15), `098b312` (implementation),
  `8fc066e` (retro + L-102), `ae3731d` (L-102 regression tests),
  `5aebe10` (promoted.md hash fill)
- **Agents used:** `knowledge-curator` (L-102 triage), `docs-reconstructor`
  (per-phase drift audit), `release-phase-auditor` (completion audit)

## Where we are

This corrective pass sits inside the v2 dependency-root arc
(`decisions/0078`), directly downstream of Phase 82 ("Contract and
Evidence Foundation," `done` at `c2902ec`). Phase 82's original
implementation established the real, working substrate every later v2
phase depends on: a versioned oracle-contract/oracle-result schema, a
derived INTENDED/OBSERVED/VERIFIED/CONTESTED epistemic view, and one real
Ledgerkit behavioural contract (`balance_from_spec`). That phase was
independently audited and marked `done` — but "done" did not mean "free
of defects an independent review could still find in the shipped code,"
and this pass is exactly that check: a second, later, more adversarial
look at the same code, triggered by a direct governing prompt rather than
by this session's own initiative. The project state after this pass:
Phase 82's design (`decisions/0080`/`0081`) is unchanged and unreopened;
its enforcement is now four defects stronger (`decisions/0082`); Phase 83
("Semantic Change Assurance") remains the next phase, still not
phase-planned, unaffected by anything this pass found.

## Goal

Investigate and correct four named assurance weaknesses in the real
oracle/epistemic-profile/validator code — current-vs-historical
verification conflation, execution-failure misclassification,
destructive evidence overwrite, and insufficient schema validation —
each with real negative controls, without reopening Phase 82's design or
expanding into Phase 83/84 scope.

## Scope delivered vs planned

All four defects named in the governing prompt were delivered, matching
scope exactly — nothing added, nothing dropped:

- **A** (current vs. historical verification): `EpistemicProfile` gains
  `unconfirmed_scopes`; `check_knowledge_base.py`/`check_contracts.py`
  both fail closed when current verification is claimed but
  unconfirmable. Delivered as scoped.
- **B** (execution-failure classification): `run_pytest_check`
  reclassified via pytest's own `--junit-xml` report. Delivered as
  scoped — plus one deviation, below.
- **C** (destructive overwrite): immutable `<check_id>--<run_id>` naming;
  the two pre-existing committed results migrated via `git mv`.
  Delivered as scoped.
- **D** (schema validation gaps): explicit type/value enforcement for
  every required field. Delivered as scoped.

**One deviation, caught by the independent `knowledge-curator` triage,
not by this session's own planning**: the initial implementation commit
(`098b312`) verified defect B's fix correctly via direct, ad hoc
interactive invocations of `run_pytest_check` during the session, but
did not land that verification as an actual regression test exercising
`run_pytest_check` itself — the two pre-existing tests that happened to
touch it only cover a genuine PASS and a genuine FAIL, neither of which
would catch a revert of the fix. `knowledge-curator` found this gap
during L-102's triage and drafted two of the three tests that closed it
(`ae3731d`). This was corrected within the same corrective pass, not
deferred.

Explicitly out of scope, per the governing prompt, and untouched: Phase
83 impact analysis, Phase 84 MCP integration, cross-project federation,
agent orchestration.

## What was achieved

Four real, independently-confirmed fixes against already-shipped code,
not a plan-only correction:

- `derive_epistemic_profile` and both strict validators now distinguish
  "evidence exists but cannot currently be reconfirmed" from both "no
  evidence at all" and "confirmed current" — three states, not two.
- `run_pytest_check` reliably tells a genuine behavioural failure apart
  from four distinct infrastructure/configuration failure modes, using a
  structured signal pytest already provides, confirmed against the real
  tool (pytest 9.1.1) rather than assumed from its documentation.
- Every oracle execution from this point forward is permanently,
  individually inspectable — re-running the real oracle against the real
  Ledgerkit checkout during this pass produced two new, genuinely fresh
  `PASS` results without disturbing either of the two results Phase 82's
  original implementation had committed.
- A contract author can no longer accidentally invert a check's
  `required` flag via a YAML string, use an unsupported schema version or
  execution provider, or crash the parser with malformed YAML — all four
  now produce a named, controlled `OracleSchemaError`.

## What worked

- **Reproducing every claimed defect directly against the real shipped
  code before writing any fix** — not trusting the governing prompt's own
  description of the bug. This caught one real subtlety immediately: the
  existing `check_contracts.py` already correctly gated `repo_root` on
  `is_dir()` before calling into `oracle.py`, so defect A's fix only
  needed to touch the two call sites that actually lacked that gate
  (`derive_epistemic_profile`'s own default, `check_knowledge_base.py`'s
  hardcoded `None`) — a narrower, more precise fix than "add the gate
  everywhere" would have been.
- **Direct experimentation over trusting a tool's own documented
  behaviour.** Defect B's fix depended on knowing pytest's exact exit
  codes and `--junit-xml` shapes for five distinct conditions. Five real
  `pytest` invocations were run and measured directly this session before
  any classification logic was written — this is what let the fix be
  precise (distinguishing "zero tests collected" from "collection error"
  from "no junit-xml produced at all") rather than a guess that might
  have missed a case, exactly as later confirmed when the independent
  auditor re-ran the same five scenarios and got identical results.
- **Dispatching `knowledge-curator` to triage the candidate learning
  rather than self-grading it.** The curator caught a real, concrete test-
  coverage gap in this session's own just-landed work (defect B's fix had
  no regression test of its own) that a self-review would have been more
  likely to wave through as "already verified, I ran it by hand."
- **The independent `release-phase-auditor` pass attempting genuine
  falsification**, per the governing prompt's own explicit instruction,
  rather than re-running the shipped tests and calling it done. It found
  a real adversarial case outside the shipped test suite (an existing-
  but-wrong decoy directory for defect A) and a real residual gap outside
  this pass's own named scope (an all-skipped pytest file still
  classifying as PASS) — neither blocks this pass, but both are now on
  record rather than undiscovered.

## What didn't work

No wasted approach or dropped-context handoff this pass. The one real
misfire was process, not technical: the corrective-pass retro was
initially written in a condensed, non-template shape (a short intro plus
Goal/Lessons-learnt/Process-feedback only), which the independent
`release-phase-auditor` correctly rejected as insufficiently populated
against `planning/retros/TEMPLATE.md` given this pass's real size (25
files, four distinct defects, a new ADR) — the "a few lines suffice for a
trivial phase" carve-out does not apply here, and treating it as if it
did was the actual mistake, caught by the audit exactly as that gate is
supposed to catch it. This file is the corrected version.

## Lessons learnt

1. **A validator's own default argument can silently reintroduce the
   exact bug its design was meant to prevent.** `evaluate_result_
   precedence`'s own `repo_root: Path | None = None` was correctly
   documented ("trusted as recorded" when omitted) — the actual defect
   was two call sites treating "omitted" as an acceptable production
   steady state rather than a caller's explicit, visible choice.
2. **Bare exit codes are not a reliable success/failure signal for any
   subprocess-based oracle mechanism, even for a well-behaved tool like
   pytest.** Filed as `L-102` (promoted).
3. **A unique identifier inside a record does not, by itself, protect
   against the file that stores it being overwritten.** `run_id` was
   already correctly designed; the defect was entirely in the filename
   choosing not to use it.
4. **A `(path, result)` pairing, not a reconstructed path, is the only
   safe way to report findings once a storage key stops being 1:1 with a
   filename.** Caught by reasoning through the consequence of defect C's
   fix on `check_contracts.py` before writing any test.
5. **A corrective pass over an already-`done`, already-audited phase still
   requires the retro to carry the same weight as the original phase's
   own retro** — "we already closed this phase once" is not a reason to
   write a thinner one the second time. This pass's own retro gap (above)
   is the concrete instance.
6. **An independent audit instructed to falsify, not just confirm, finds
   things a confirm-only pass would miss** — the decoy-directory case and
   the all-skipped-tests residual in defect B were both found specifically
   because the auditor was told to actively try to break the claims, not
   merely re-run what already existed.

## Process-improvement feedback

- Worth stating explicitly in a future corrective-pass brief (or in
  `release-phase-auditor`'s own standing instructions): a corrective-pass
  retro is held to the *same* `TEMPLATE.md` completeness bar as an
  original phase's retro, scaled to the corrective pass's own real size —
  not a lighter one by default. This pass's own first retro draft is a
  concrete example of getting that wrong on the first attempt.
- No other process friction this pass. The knowledge-curator's write-
  boundary (no `tests/` access) worked exactly as designed: it produced a
  concrete, correct, call-site-accurate draft test rather than either
  silently skipping the gap or attempting to write the test itself
  outside its own role.

## Candidate learnings filed

`L-102` — filed to `planning/learnings/inbox.md`, triaged by
`knowledge-curator`, promoted (`planning/learnings/promoted.md`) once its
recommended regression tests landed in `ae3731d`.

## Where we're going

Phase 83 ("Semantic Change Assurance") remains the next phase and is
still not phase-planned — this corrective pass does not change that
trajectory. `decisions/0082`'s own Consequences section states explicitly
that none of Phase 82's exit gate, its one pinned Ledgerkit contract, or
`decisions/0080`/`0081`'s design is reopened by this pass; Phase 83 still
needs its own `planning/phase-83-*.md` plan file (`CLAUDE.md` §1) before
any implementation begins, scoped against evidence current at that time.
Two non-blocking residuals surfaced by the independent audit are left as
explicit candidates for whoever scopes future oracle/execution-provider
work (noted in `planning/retros/_audit-phase-82-corrective-pass.md` §§1-2,
not re-litigated here): a minor `known_gap_scopes`-vs-`unconfirmed_scopes`
labelling case for a decoy-but-real directory, and an all-tests-skipped
pytest run still classifying as `PASS` — neither undermines any of the
four named defects' own fixes, and neither is this pass's own scope to
fix.

## Time / cost note

One session, five commits across the corrective-pass work itself (plus
closeout commits to follow). The bulk of the time went to direct
experimentation (five real pytest invocations measured by hand before
writing defect B's classification logic) and to the independent
`release-phase-auditor` pass, which ran the full regression suite,
`ruff`, both strict validators, a falsification check on the new
regression tests, and several adversarial cases beyond the shipped tests
— a deliberately expensive pass, consistent with the governing prompt's
own explicit instruction to attempt to falsify the current-verification
claims rather than merely confirm them. No AI-spend anomalies; nothing
ran unexpectedly long relative to that scope.
