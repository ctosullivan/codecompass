# Phase 87 Stage 87D retro — deterministic reference assurance and final Phase 87 closeout

- **Date:** 2026-11-11
- **Commit(s):** Planning: `6e05aee`, `7d226d8`, `dc60e4c`, `f3651db`
  (three amendment rounds, each independently re-reviewed in §V).
  Implementation (Deliverable 1): `8cdb70c` (extended `scripts/
  check_user_docs.py`, fixed `docs/reference/cli.md`, 17 new tests),
  `cf30623` (§U.1 matrix update), `fd51c00` (`CHANGELOG.md`). Closeout
  commits follow this retro.
- **Agents used:** `Plan` (×3 independent planning reviews, §V's
  First/Second/Third review rounds, each READY WITH NON-BLOCKING
  OBSERVATIONS), `general-purpose` (×1, the Deliverable-1 audit
  checkpoint — real injected-drift reproduction in the live
  repository), `docs-reconstructor` (drift audit of the
  implementation), `release-phase-auditor` (the final, phase-wide
  Phase 87 audit).

## Where we are

Stages 87A, 87B, and 87C are implemented, independently audited, and
(Stage 87C) corrected through a post-closeout corrective pass — all
`done`, none reopened by this stage. Stage 87D is the fourth and, per
§U.1's own requirement-to-evidence matrix, final stage needed to close
Phase 87 overall: against the original, textually-traceable Phase 87
requirements (re-derived directly from `decisions/0085` §5-6 and
`planning/v2-roadmap.md`'s own Phase 87 section across three
independent planning reviews, never assumed from a prior stage's own
retro), exactly one item was genuinely outstanding — a deterministic
or mechanically-guarded CLI/configuration reference.

## Goal

Implement Stage 87D's exactly two mandatory deliverables (§U.8):
deterministic reference assurance (Deliverable 1, this stage's own
real implementation work) and final Phase 87 assurance and closeout
(Deliverable 2, verification/reconciliation/the final audit) — the
smallest credible amount of work that actually closes Phase 87,
without expanding into the deferred cross-document-consistency
checker (§U.3) or any later roadmap phase.

## Scope delivered vs planned

Delivered exactly what §U.8 scoped, nothing more. §U.3 (cross-document
semantic consistency) and the incremental-patching capability (§U.4)
were both explicitly deferred in planning and neither was touched
during implementation. The plan itself required three amendment
rounds before implementation began — each round fixed real,
independently-verified gaps a fresh governing task or planning review
found (a design contradiction in the default-checker; a genuinely
reproduced installed-wheel execution-boundary defect; a duplicate-
validator risk; a baseline-aware strict-validator policy correction;
a prose-form command-isolation test gap) — all resolved before a
single line of implementation code was written, matching this
project's own "plan before implementing" discipline (`CLAUDE.md` §1)
exactly, including its own explicit trigger for when a verification
section must cover a mechanism's *depth* as well as its *scope*.

## What was achieved

**Deliverable 1** (§U.2/§U.2a): `scripts/check_user_docs.py` extended
in place — `check_cli_commands_documented` now walks all five Typer
sub-apps (closing a real, pre-existing 19-of-27-subcommand coverage
gap that existed before this stage and was never previously found);
a new `check_cli_parameter_defaults_documented` implements the
four-point default-disclosure policy; `check_vendor_config_fields_
documented` gained the planned `Ecosystem`-enum check. Five real,
previously-undocumented CLI defaults fixed in `docs/reference/cli.md`.
Two accurate documentation disclosures added: `docs compile`'s real
installed-package execution-boundary requirement (independently
reproduced in a real isolated venv, both the failure and the
editable-install success case, including all four sibling commands
positively verified end-to-end), and `codecompass undo`'s own real
first-run limitation (`L-129`), disclosed, not fixed. 17 new
regression tests; full suite 1380 passed, 2 skipped.

**Deliverable 2** (§U.5/§U.7): verification steps run for real —
full regression suite green; every applicable validator checked
against §U.7a's own corrected, baseline-aware policy (clean-baseline
validators stayed clean; info-only-baseline validators stayed
byte-identical; `check_self_knowledge_quality.py --strict`'s own
pre-existing 26/35-blocking baseline, `L-114`/`L-107`, confirmed
unchanged, never treated as a Stage 87D regression nor silently
waived); `verify_cleanroom_isolation.py`'s preflight re-confirmed
passing unchanged; `docs maintain` re-confirmed all six compiler-
published regions `noop` and the one pre-existing README candidate
still correctly `doc_candidate`; a fresh `docs-reconstructor` drift
audit against the implementation; a fresh, phase-wide
`release-phase-auditor` dispatch (not scoped to Stage 87D's own diff
alone) against the complete Phase 87 Definition of Done.

## What worked

- **Three independent planning-review rounds before a line of
  implementation code was written**, each one genuinely re-deriving
  claims from scratch (two of the three built a real wheel and
  reproduced the installed-wheel/editable-install mechanics
  themselves, rather than trusting the plan's own prose) — this
  caught a genuine design contradiction (the default-checker could
  only catch a wrong default, never an omitted one) and a real
  test-design gap (prose-form command-isolation) before either
  reached the implementation stage, where fixing them would have cost
  more.
- **Writing the regression tests before trusting the implementation**
  surfaced two real false-negative bugs the plan's own design hadn't
  anticipated: a default value colliding with the synopsis line's own
  leading `codecompass <path>` tokens (`--project-id`'s "codecompass"
  default matching the command invocation itself), and a default
  value appearing in an unrelated enum-choices list rather than as a
  stated default (`--relation`'s "supporting_evidence" appearing as
  one of several listed *choices*). Both caught by running the real
  checker against the real repository immediately after writing it,
  not assumed correct from the design alone.
- **An independent audit checkpoint that genuinely injects drift and
  reverts it**, rather than only re-reading the test suite's own
  output, confirmed the implementation actually works against the
  live repository, not merely its own synthetic fixtures.

## What didn't work

- The first implementation pass of the default-disclosure check used
  bare substring matching (`value in synopsis_or_prose_text`) rather
  than the "narrow, explicit phrase match" the plan's own §U.2 text
  had already specified — a real gap between what was planned and
  what was first written, caught immediately by running the checker
  against the real repository rather than trusting the design.
- The None-default exemption (plan §U.2 point 2's own "non-`None`
  default" scoping) was likewise not implemented in the first pass,
  producing 12 spurious findings against the real repository before
  being fixed — a straightforward implementation oversight, not a
  plan gap (the plan text was already correct).

## Lessons learnt

- A design document's own careful wording ("narrow, explicit phrase
  match," "non-`None` default") is not self-enforcing — the first
  implementation pass of a check this precise needs to be run against
  the real repository immediately, not assumed correct from a careful
  reading of its own design, since a plausible-looking general
  substring match is the easiest wrong shortcut to reach for while
  implementing a check like this.
- A real, end-to-end audit checkpoint (inject real drift, confirm
  detection, confirm a clean revert) catches things a synthetic test
  suite alone cannot fully guarantee — in this case it didn't catch a
  *new* defect (the test suite itself was already correct by the time
  the checkpoint ran), but it is the only genuinely independent
  confirmation that the mechanism works against the real repository's
  own real structure, not merely against fixtures built to match the
  implementer's own mental model of that structure.

## Process-improvement feedback

- No friction found in the agent-boundary model this stage — three
  independent `Plan` reviews in sequence, each building directly on
  the last without re-litigating already-settled findings, worked
  cleanly; the `general-purpose` audit-checkpoint dispatch's own
  "inject, confirm, revert, confirm clean" structure is a reusable
  pattern worth naming for any future validator-extension work.

## Candidate learnings filed

None. The two implementation bugs found during this stage (substring-
matching false negatives; the missing `None`-exemption) were caught
and fixed within the same implementation pass, before any commit
landed — they never reached a state where filing them as a learning
would add information a future session doesn't already have from
reading this retro and the commit `8cdb70c` itself.

## Where we're going

This is Stage 87D's own retro — written before the final, phase-wide
`release-phase-auditor` dispatch (§U.7 step 5) has returned its
verdict. Phase 87's own final completion status (whether the complete
Definition of Done has genuinely passed) is recorded in this file's
own addendum below, once that audit actually runs — not asserted here
in advance of it. §U.3 (cross-document semantic consistency) and the
incremental-patching capability remain named, deferred future work for
a separately authorised phase; neither is Phase 88's own concern
either (Phase 88 is MCP/agent integration, unrelated).

## Time / cost note

Three independent planning-review dispatches (roughly 500-700s each,
100-160k tokens each) before implementation; one implementation pass
(iterative, with two real bugs caught and fixed via direct testing
against the live repository); one audit-checkpoint dispatch
(~90s, real wheel/drift reproduction); the full regression suite
(~400s per full run, run twice during this stage). Lead-side
orchestration time not separately instrumented, matching this
project's own established disclosed-unavailable discipline.
