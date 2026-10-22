# Phase 82 corrective-pass retro

**Date:** 2026-10-22. **Trigger:** direct user request ("CodeCompass
Orchestrator — Phase 82 Corrective Pass"), an independent review of the
already-`done` Phase 82's *shipped code* (not only its plan), four
sessions after the original implementation (`c2902ec`).

## Goal

Investigate and correct four named assurance weaknesses in the real
oracle/epistemic-profile/validator code, with real negative controls for
each, without reopening Phase 82's design (`decisions/0080`/`0081`) or
expanding into Phase 83/84 scope.

## Delivered vs. planned

All four defects named in the governing prompt were reproduced directly
against the real shipped code before being fixed — not assumed from the
prompt's own description:

- **A** (current vs. historical verification): reproduced by direct
  inspection (`check_knowledge_base.py:677`'s hardcoded `repo_root=None`,
  `check_contracts.py`'s unconditional `strict=False` checkout-
  unavailable finding). Fixed via a new `unconfirmed_scopes` field and
  two new fail-closed call sites, exactly as planned.
- **B** (execution-failure classification): reproduced via real
  experimentation against pytest 9.1.1 (genuine failure, collection
  error, invalid node id, nonexistent file, missing dependency — five
  real runs, five distinct exit codes and junit-xml shapes measured
  directly, not assumed). Fixed via `--junit-xml` + `ElementTree`, no new
  dependency.
- **C** (destructive overwrite): reproduced by reading
  `run_balance_from_spec_oracle.py`'s own `f"{check.check_id}.yaml"`
  naming directly. Fixed via `<check_id>--<run_id>` naming; migrated the
  two pre-existing committed results with `git mv` plus an `EV-`
  `test_ref` update, and demonstrated the fix with a real second run
  against the unmodified checkout (both files preserved, two new ones
  added).
- **D** (schema validation gaps): reproduced by direct inspection
  (`bool(entry["required"])`) and a standalone Python REPL check
  (`bool("false") is True`, confirmed). Fixed via explicit type/value
  validators for every required field.

Nothing was descoped or deferred beyond what the governing prompt itself
named out of scope (Phase 83 impact analysis, Phase 84 MCP, cross-project
federation, agent orchestration — none touched).

## Lessons learnt

1. **A validator's own default argument can silently reintroduce the
   exact bug its design was meant to prevent.** `evaluate_result_
   precedence`'s own `repo_root: Path | None = None` was correctly
   documented ("trusted as recorded" when omitted) — the actual defect
   was two call sites (`check_knowledge_base.py`, `derive_epistemic_
   profile`'s own un-threaded default) treating "omitted" as an
   acceptable steady state for a *production* validator, rather than a
   caller's explicit, visible choice. The fix was not to change the
   low-level function's contract at all — it was to make the two
   call sites that matter pass something real.
2. **Bare exit codes are not a reliable success/failure signal for any
   subprocess-based oracle mechanism, even for a tool as well-behaved as
   pytest.** Direct experimentation (not documentation-reading) was
   necessary to discover pytest reuses exit code 1 for both a real
   failure and nothing else distinguishing, while separately using 2/4/5
   for three different non-behavioural conditions — this would have been
   easy to get wrong again from pytest's own docs alone. Filed as a
   candidate learning below.
3. **A unique identifier inside a record does not, by itself, protect
   against the file that stores it being overwritten.** `run_id` was
   already correctly designed in the original Phase 82 implementation;
   the defect was entirely in the *filename* choosing not to use it. Any
   future evidence-writing mechanism in this codebase should name its
   output file from its own unique id, not a coarser grouping key.
4. **A `(path, result)` pairing, not a reconstructed path, is the only
   safe way to report findings once a storage key stops being 1:1 with a
   filename.** Fixing defect C exposed a latent assumption in
   `check_contracts.py` (`result_path = slug_dir / "results" /
   f"{result.check_id}.yaml"`) that silently broke the moment multiple
   files could share one `check_id` — caught by reasoning through the
   consequence before writing any test, not discovered via a failing
   test.
5. **A corrective pass over an already-`done`, already-audited phase
   still benefits from the same discipline as the original phase**: ADR
   first, plan amendment, real negative controls (not simulated), full
   regression, independent docs-drift and release-phase audits. Treating
   "already done" as license to patch quietly would have been a mistake.

## Process-improvement feedback

- Worth promoting into a durable check for any future oracle/execution-
  provider work: **"classify a subprocess's outcome from its own
  structured report when one exists (`--junit-xml`, `--json`, etc.),
  never from exit code alone"** — a generalizable invariant, not
  specific to pytest.
- No process friction encountered this session beyond the ordinary cost
  of re-deriving context for an already-closed phase — mitigated by
  reading the governing ADRs (`0080`/`0081`) and the real code directly
  rather than trusting the prior session's own summary.

Candidate learnings filed to `planning/learnings/inbox.md` for
`knowledge-curator` triage: see that file's newest entry.
