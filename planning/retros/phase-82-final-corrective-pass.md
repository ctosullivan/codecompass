# Phase 82 final corrective-pass retro

- **Date:** 2026-10-22
- **Commit(s):** `65840ca` (ADR `decisions/0083` + plan §16),
  `04c0ed2` (implementation + tests + docs + fresh real oracle evidence)
- **Agents used:** `knowledge-curator` (L-103 triage), `docs-reconstructor`
  (per-phase drift audit), `release-phase-auditor` (completion audit,
  instructed to attempt falsification of all three corrections)

## Where we are

This pass sits directly downstream of the first Phase 82 corrective pass
(`decisions/0082`, `planning/retros/phase-82-corrective-pass.md`), which
itself sat downstream of Phase 82's own original implementation
("Contract and Evidence Foundation," `c2902ec`). That first corrective
pass fixed four assurance defects and was independently audited to a
PASS (`e3917ad`) — but its own audit explicitly recorded two non-blocking
residuals it found while falsification-testing, outside that pass's own
named scope: a labelling imprecision in `derive_epistemic_profile`
(`known_gap_scopes` vs. `unconfirmed_scopes` for a decoy-but-real
directory) and an all-skipped pytest run still classifying `PASS`. This
pass is triggered by a further, separate independent post-completion
review — again a direct governing prompt, not this session's own
initiative — that named three weaknesses, one of which (all-skipped
execution) is exactly the second residual the prior audit had already
flagged as a candidate for "whoever next touches `oracle.py`'s
execution-provider logic." The project state after this pass: Phase 82's
design (`decisions/0080`/`0081`) remains unreopened; the first corrective
pass's own four fixes (`decisions/0082`) remain unreopened; enforcement
is now three defects stronger (`decisions/0083`), one of which closes a
gap the prior pass's own audit had already surfaced but correctly left
out of that pass's scope. Phase 83 ("Semantic Change Assurance") remains
the next phase, still not phase-planned.

## Goal

Investigate and correct three named assurance weaknesses in the real
oracle/strict-validator code — an all-skipped pytest execution
incorrectly establishing `PASS`, both strict validators failing open
when required verification modules cannot be imported, and malformed
`outcome`/optional-field values in `parse_oracle_result` escaping
controlled schema validation — each with real negative controls, without
reopening Phase 82's design or either prior pass's own fixes, and without
expanding into Phase 83/84 scope.

## Scope delivered vs planned

All three findings named in the governing prompt were delivered, matching
scope exactly:

- **A** (all-skipped execution): `_classify_pytest_junit` gains a
  `tests - skipped <= 0` check, placed after the existing `tests == 0`
  check, before `errors`/`failures`. Delivered as scoped; confirmed a
  partially-skipped run (skip+pass, skip+fail) is unaffected.
- **B** (strict validators fail open on missing verification machinery):
  both named locations (`check_contracts.py::run_all`,
  `check_knowledge_base.py::check_verified_status_cites_passing_oracle_result`)
  changed from `strict=False` to `strict=True` on their own
  `oracle is None`/`ki is None` branch. Delivered as scoped — no other
  informational finding in either validator was touched, since the
  governing prompt explicitly required preserving genuinely-optional
  informational behaviour (the Ledgerkit-checkout-unavailable finding,
  the expected-`GAP` finding, and `check_no_pending_reconciliation`'s own
  unrelated `ki is None` branch all remain informational, correctly).
- **C** (malformed result fields escape validation): `outcome`'s type is
  now validated before its enum-membership check; `baseline_id`/
  `environment_descriptor`/`invalid_reason` now each require
  `str | None`; `run_pytest_check`'s `subprocess.run` launch is now
  wrapped in `try`/`except OSError`. Delivered as scoped, including the
  prompt's own explicitly-named "review subprocess-launch failure
  handling" sub-item, which the prompt's own text separated from the
  schema-validation sub-items but grouped under the same finding letter.

Explicitly out of scope, per the governing prompt, and untouched: Phase
83 semantic-impact analysis, Phase 84 MCP integration, any additional
execution provider, cross-project federation, agent orchestration. No
schema framework was introduced; `_SUPPORTED_EXECUTION_PROVIDERS` remains
`{"pytest"}`, unchanged.

## What was achieved

Three real, independently-confirmed fixes against already-shipped,
already-once-corrected code:

- A pytest check reference that resolves only to skipped tests (every
  collected test individually marked `@pytest.mark.skip`, or a `skipif`
  condition unmet in the current environment) can no longer silently
  satisfy `PASS` — confirmed directly against real pytest 9.1.1 both
  before the fix (a two-skip file reported `PASS`) and after (the same
  file now reports `INVALID`, with the skip-vs-pass/skip-vs-fail mixed
  cases both confirmed unaffected).
- `check_contracts.py --strict` and `check_knowledge_base.py --strict`
  can no longer report a clean pass while silently unable to run their
  own required oracle-verification logic — confirmed by monkeypatching
  each validator's own import helper to `None` and observing the exit
  code flip from 0 to 1.
- A result file with a malformed `outcome` (a YAML list or mapping) now
  produces the same controlled `OracleSchemaError` every other malformed
  field in this schema already produces, instead of an uncaught
  `TypeError` escaping the parser — confirmed directly, both before (a
  raw `TypeError` surfaced) and after (a named `OracleSchemaError`) the
  fix. A subprocess-launch failure (confirmed via a nonexistent `cwd`,
  which the OS itself refuses to launch into) is now `INVALID` with
  diagnostic evidence preserved, rather than an uncaught exception
  propagating out of `run_pytest_check`/`evaluate_check`.

## What worked

- **Treating the prior pass's own audit-recorded residuals as a live
  lead, not an archived footnote.** Finding A in this pass's governing
  prompt is exactly the all-skipped-execution gap
  `planning/retros/_audit-phase-82-corrective-pass.md` had already named
  as a non-blocking residual — recognising this (rather than treating it
  as a coincidentally similar, unrelated new finding) confirmed quickly
  that the fix belonged in the same function (`_classify_pytest_junit`)
  the first corrective pass had just finished hardening, placed in the
  same ordered-check structure, not as a bolt-on special case.
- **Reproducing all three findings with real tool behaviour before
  writing any fix**, continuing the discipline the first corrective pass
  established: a real two-skip pytest file was run against real pytest
  9.1.1 and its junit-xml inspected directly (`tests="2" skipped="2"
  errors="0" failures="0"`) before touching `_classify_pytest_junit`;
  `hash(['x'])` was confirmed to raise `TypeError` directly in a Python
  REPL-style check before touching `parse_oracle_result`; both strict
  validators' fail-open behaviour was confirmed by monkeypatching before
  any `strict=False` → `strict=True` edit was made.
- **A genuine disposable, git-cloned, deliberately mutated scratch
  checkout for the real Ledgerkit negative control** (never the real
  `~/projects/ledgerkit`), reusing the exact mutation
  (`if section.invert:` → `if not section.invert:`) the first corrective
  pass's own `test_deliberately_broken_implementation_produces_fail`
  established as this project's own precedent — confirmed a genuine
  `FAIL`, then discarded (not committed, correctly disposable).

## What didn't work

No wasted approach or dropped-context handoff this pass. The one
avoidable inefficiency: the first attempt at a real Ledgerkit negative
control used a plain `git clone` without first confirming the scratch
copy would need its own `.venv` — this was caught and corrected
immediately (symlinking the real Ledgerkit `.venv`, the same convention
`tests/test_oracle.py::_copy_ledgerkit_scratch` already established) once
checked, costing a few minutes rather than a wrong result; no finding or
fix was affected.

## Lessons learnt

1. **An independent audit's own non-blocking residuals are a real
   backlog, not noise to be forgotten once a pass closes.** This pass's
   Finding A is proof: the exact gap the first corrective pass's audit
   flagged as "a candidate for whoever next touches `oracle.py`'s
   execution-provider logic" was picked up by name in a *separate*,
   later independent review — had it been silently dropped instead of
   recorded, there would have been nothing linking the two.
2. **A Python `in`/`not in` check against a `set` is not safe to run
   before the checked value's own type is confirmed** — `hash()` runs
   first, and an unhashable value raises before the membership check
   ever evaluates. Filed as `L-103` (candidate).
3. **An "import-or-None, informational finding" pattern reused across
   multiple checks in the same validator script is not uniformly safe to
   default to informational** — whether a failed import should block
   `--strict` depends on whether the specific check it disables is itself
   assurance-critical (every oracle-contract check, here) or merely one
   optional convenience among several (projection-staleness detection,
   left informational, correctly, in the same script).
4. **"Fail closed" and "preserve every genuinely-optional informational
   finding" are not in tension when scoped precisely** — this pass
   changed exactly two `strict=False` → `strict=True` flips, in the two
   named locations, and left every other informational finding in both
   validators untouched; a blanket "make everything strict" pass would
   have been both out of scope and wrong (e.g. `contract-check-gap` is
   an expected, healthy state, not a failure).

## Process-improvement feedback

- No process friction this pass. The `knowledge-curator`/
  `docs-reconstructor`/`release-phase-auditor` sequencing from the first
  corrective pass needed no adjustment; `L-103`'s candidate-stage framing
  (explicitly asking the curator to grep for the same `not in <set>`
  pattern elsewhere before deciding promote vs. discard) follows the same
  shape the curator's own prior triage work has already handled well.

## Candidate learnings filed

`L-103` — filed to `planning/learnings/inbox.md`, pending
`knowledge-curator` triage.

## Where we're going

Phase 83 ("Semantic Change Assurance") remains the next phase and is
still not phase-planned — this pass does not change that trajectory.
`decisions/0083`'s own Consequences section states explicitly that none
of Phase 82's exit gate, its one pinned Ledgerkit contract, or
`decisions/0080`/`0081`/`0082`'s design is reopened by this pass; Phase
83 still needs its own `planning/phase-83-*.md` plan file (`CLAUDE.md`
§1) before any implementation begins. With both of the first corrective
pass's own audit-recorded residuals now resolved (the all-skipped-tests
gap by this pass; the `known_gap_scopes`-vs-`unconfirmed_scopes`
labelling imprecision for a decoy-but-real directory remains open — it
was not named by this pass's own governing prompt, and is not reopened
or touched here), whoever next scopes Phase 83/84's own execution-
provider work starts from a strictly smaller known-gaps list than before
this pass.

## Time / cost note

One session, two commits for the corrective-pass work itself (ADR+plan,
then implementation+tests+docs+fresh real evidence), plus closeout
commits to follow (this retro, learnings triage, and the terminal
reconciliation commit). Time was concentrated in direct experimentation
(the real all-skipped pytest run, the real disposable mutated-checkout
negative control, the real unhashable-value `TypeError` confirmation)
and the independent `release-phase-auditor` pass, which re-ran the full
regression suite, `ruff`, both strict validators, and was instructed to
attempt genuine falsification of all three corrections rather than
merely re-run the shipped tests. No AI-spend anomalies; nothing ran
unexpectedly long relative to that scope.
