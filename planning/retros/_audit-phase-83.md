# Phase 83 — Semantic Change Assurance — independent completion audit

**Auditor:** `release-phase-auditor` (independent pass, read-only)
**Audited commit:** `b1a8447` (HEAD at audit time, `main` branch)
**Commit range covered:** `bf60804` (first corrective amendment,
decisions/0086) → `597f819` (second corrective amendment,
decisions/0087) → `b1a8447` (implementation, decisions/0088, retro)
**Plan file:** `planning/phase-83-semantic-change-assurance.md` (§10-14)
**Governing ADRs:** `decisions/0086`, `0087`, `0088`
**Retro under review:** `planning/retros/phase-83-semantic-change-assurance.md`

## Verdict

**FAIL**

The implementation itself is genuinely strong — I independently
reproduced the dogfood scenario end to end (not merely re-read the
retro's numbers) and it holds up exactly as claimed. But one explicit
`CLAUDE.md` §5 Definition-of-Done condition does not hold against the
exact commit under audit: **no `knowledge-curator` triage of this
phase's candidate learnings has actually occurred**, and the retro's own
text concedes this rather than disputing it. A second, narrower gap (a
named test case missing from the phase's own corrective ADR's required
coverage) is also real, though lower severity. Neither finding is about
the tool's correctness — both are about whether every DoD conjunct is
actually satisfied yet, which is the one question this audit exists to
answer honestly rather than soften.

## What I independently re-ran (not trusted from the retro alone)

1. **Full suite**: `.venv/bin/python -m pytest -q` — ran it twice
   independently (once directly, once to a log file) — **1035 passed, 2
   skipped** both times, matching the retro's and the implementation
   commit message's own claim exactly.
2. **`scripts/check_contracts.py --strict`** — exit `0`, **7
   informational findings**: 6 `contract-result-integrity-mismatch`
   (the six Phase-82 historical results, each explicitly labelled
   "superseded historical evidence... decisions/0088" in its own
   message) + 1 `contract-check-gap` for the new, not-yet-passing-for-real
   check. Matches the retro's claimed "7 informational contract
   findings" exactly; none blocking.
3. **`scripts/check_knowledge_base.py --strict`** — exit `0`, **24
   informational findings**, all pre-existing
   `knowledge-base-snapshot-current-divergence` entries (lifecycle-status
   drift already present before this phase) — confirmed none are new or
   of a different kind. Matches the retro's claimed "24 pre-existing...
   unchanged" exactly.
4. **`scripts/check_user_docs.py --strict`** — "no findings", exit `0`.
5. **`src/codecompass/oracle.py`, `graph.py`, `knowledge_intermediate.py`
   unmodified**: `git diff bf60804^..HEAD -- <those three files>` is
   empty. Confirmed.
6. **Two fresh `OracleResult`s for the two originally-required checks**
   — loaded each file and called `oracle.evaluate_result_precedence`
   directly against the live `~/projects/ledgerkit` checkout (HEAD
   `7224bb5c1`, confirmed dirty only in `dev-docs/clean-room/` files, not
   `ledgerkit/` package code): both independently recompute to **PASS**.
7. **The dogfood scenario, reproduced from scratch, not re-read**:
   - Cloned real Ledgerkit at the pinned SHA into a disposable scratch
     copy; confirmed `sha256(reports.py)` = `97e22d58...` and
     `sha256(tests/test_reports.py)` = `44d803f2...` — both byte-for-byte
     identical to the retro's recorded hashes (verified independently via
     `git show <sha>:<path> | sha256sum` against the real
     `~/projects/ledgerkit` repo).
   - Applied an OR-union double-counting mutation to `balance_from_spec`
     (counting a posting once per matching pattern rather than once per
     posting) — **before any new test file existed in the tree**, ran
     the real, unmodified `pytest tests/`: **935 passed, 1 warning, 14
     subtests passed** — exact match to the retro's claimed baseline,
     independently reproduced twice (I share the mutation hadn't been
     named verbatim anywhere I could just copy from — I derived it fresh
     from the plan's own description and it produced the identical
     count).
   - Added a new regression test file (never merged into
     `test_reports.py`) asserting
     `rows["expenses:food:groceries"] == Decimal("150.00")`: failed
     against the mutation with **`AssertionError: Decimal('300.00') !=
     Decimal('150.00')`** — character-for-character the same failure the
     retro records; passed (`1 passed`) against a second, clean scratch
     copy of the same file.
   - `codecompass sync --budget 0 --yes` against the mutated scratch copy
     built a real `context-graph.db` and aborted before any AI spend
     (confirms the retro's "no AI API spend" claim for this step).
   - Built a disposable scratch knowledge-root (copies of the real
     `balance-from-spec` knowledge/contract records, with a scratch-only
     `EV-BFS-004` bridging `CL-BFS-004` to a check_reference pointing at
     the scratch test file's real node id — exactly the `decisions/0087`
     §3 pattern of "the scratch copy's own temporary file... not required
     to match the contract's own `check_reference` string"). Ran
     `oracle.evaluate_check` against the mutated scratch copy for the new
     check directly: real **`FAIL`**. Ran
     `scripts/assess_change_impact.py --run-checks` against the mutated
     scratch copy: classified the touched range `behavioural_risk` and
     reported **`CONFIRMED_REGRESSION (fresh_effective_outcome=FAIL,
     aggregate_state=GAP, observed_outcomes=['FAIL', 'FAIL'])`** —
     exactly the retro's claimed output, independently produced, not
     copied.
   This is as close to "redo the whole demonstration from scratch" as a
   read-only audit can get, and it holds up in every particular I
   checked, including the exact numbers.
8. **Read `scripts/assess_change_impact.py::run_check_assurance` directly**
   and confirmed its precedence implements `decisions/0087` §1 correctly:
   `fresh_effective_outcome == "FAIL" → CONFIRMED_REGRESSION`, `elif
   == "INVALID" → INVALID_ASSESSMENT`, `elif == "PASS" → VERIFIED_SCOPE`,
   `else → VERIFICATION_GAP` — read purely from the one fresh
   `evaluate_result_precedence` call, with the aggregate (`aggregate_contract`
   over `[*historical_results, fresh_result]`) attached to the finding
   only as a separate, non-determining field. This is the exact shape
   `decisions/0087` requires and the exact shape I observed produce the
   correct output in the live reproduction above.
9. **`decisions/0088`'s own fix** (`check_contracts.py::check_result_integrity`):
   read the implementation directly — `current_pass_check_ids` is
   computed once per contract via `evaluate_result_precedence` on every
   result, and a mismatching result is downgraded to `strict=False` only
   when a *different* result for the same `check_id` is in that set;
   otherwise unchanged (`strict=True`). Read
   `tests/test_check_contracts.py::TestResultIntegrity::test_mismatch_with_no_superseding_pass_stays_blocking`
   and `::test_mismatch_superseded_by_fresh_pass_is_informational` — both
   real, meaningful, and exercise opposite directions correctly. The fix
   is also exercised through its real production call site
   (`check_contracts.py::run_all`), both by my own direct re-run of
   `check_contracts.py --strict` against the real repo (item 2 above)
   and by the pre-existing `tests/test_check_contracts.py::TestRealRepository::test_real_repository_has_no_blocking_findings`
   test, which ran as part of the 1035-passed suite — satisfying
   `CLAUDE.md` §1's `L-021` call-site requirement.
10. **Knowledge-base reconciliation**: read `CL-BFS-003.yaml`
    (`status: superseded`, unchanged `supersedes: null` — correct, since
    it is the one *being* superseded, not the superseding record) and
    `CL-BFS-005.yaml` (`supersedes: CL-BFS-003`, `status: supported`) —
    this is exactly this project's own established Claim-supersession
    convention (`check_supersedes_never_crosses_kind`, Claim→Claim).
    `REQ-BFS-002.yaml`/`DEC-BFS-002.yaml` read cleanly and consistently
    with `decisions/0086` §4's design; `REQ-BFS-002`'s `status:
    implemented` matches the same convention `REQ-BFS-001` already uses
    (an `implemented` Requirement describes real target-code behaviour,
    not a CodeCompass-side verified-check claim — `status: verified`
    would require the latter, and nothing here claims it).
11. **Protected-file drift**: `git diff bf60804^..HEAD -- CLAUDE.md` is
    empty. `decisions/0078`-`0085` show no changes in this phase's commit
    range (confirmed via `git diff --stat`). `decisions/0086`/`0087` each
    appear exactly once in `git log` (their own creation commits) — never
    touched again by the implementation commit, which only adds the new
    `decisions/0088`.
12. **`ROADMAP.md`/`CONTEXT.md` honesty**: both explicitly state Phase 83
    is `in progress` ("implemented; independent completion audit not yet
    run"), not `done`, and both separately and consistently name the
    real outstanding item (the Ledgerkit test not yet landed in
    `~/projects/ledgerkit`) as unresolved, cross-repository, and
    separately gated — never silently treated as satisfied.

## Point-by-point findings (against the task's 9 items)

1. **Verification commands** — PASS. All four re-run above; no
   unexpectedly-blocking finding in any of them.
2. **`oracle.py`/`graph.py`/`knowledge_intermediate.py` unmodified** —
   PASS. Confirmed empty diff across the whole corrective-amendment →
   implementation commit range.
3. **Dogfood claim, re-verified by direct reproduction, not trust** —
   PASS. See item 7 above — this is the strongest part of the phase, and
   I verified it about as independently as a read-only audit can.
4. **Two originally-required checks still PASS for real** — PASS.
   Independently recomputed via `evaluate_result_precedence` against the
   live `~/projects/ledgerkit` checkout; both PASS.
5. **Knowledge-base reconciliation** — PASS. Convention-correct
   supersession; `check_knowledge_base.py --strict` genuinely reports the
   same 24 pre-existing, unrelated informational findings, nothing new.
6. **`decisions/0088`'s fix doesn't weaken the original guarantee** —
   PASS. Both directions are real, meaningful tests; the "stays blocking
   when nothing supersedes it" guarantee is explicitly locked in by its
   own test, unweakened.
7. **Outstanding item honestly reflected in ROADMAP/CONTEXT** — PASS.
   Both files are explicit and consistent; nothing is silently treated as
   resolved or overstated.
8. **No protected-file drift** — PASS. Confirmed on all three axes
   (`CLAUDE.md`, ADRs 0078-0085 unedited, 0086/0087 unedited since their
   own creation).
9. **Candidate learnings triaged** — **FAIL.** This is the blocking
   finding (detail below).

## The blocking finding: no `knowledge-curator` triage actually occurred

The retro's "Lessons learnt" section states two genuinely generalizable
observations: (a) a "historical facts are never deleted" discipline
needs *every* validator consuming `evaluate_result_precedence` to
independently account for supersession, not just the aggregation layer
that originally established the discipline; (b) a tool accepting a
distinct "knowledge root" input must thread that parameter through every
internal path resolution, or a single hardcoded fallback silently
defeats the whole feature.

Its "Candidate learnings filed" section then states:

> None filed to `planning/learnings/inbox.md` as new entries — the two
> lessons above are recorded in this retro and in `decisions/0087`/`0088`
> directly; promoting them further is the `knowledge-curator`'s own
> triage call, not pre-empted here.

This is a departure from this project's own, so-far-universal
convention. I checked every retro back through Phase 81: every one of
them — including every "nothing new to file" case — explicitly records
that `knowledge-curator` itself performed the assessment, e.g.
Phase-81-third-corrective-pass: *"Both retro-surfaced observations...
were assessed by `knowledge-curator` (2026-10-08) and found adequately
covered by existing learnings — no new candidates filed."* `git log` has
a matching commit for essentially every phase's triage (`63f4d84`,
`40f8c8e`, `4db620b`, `9dc1b77`, etc.). For Phase 83, **no such commit
exists** — `b1a8447` is the only commit after `597f819`, and it is the
implementation commit itself, authored by the implementing agent, not an
independent curator pass. `planning/retros/TEMPLATE.md`'s own instruction
for this section is explicit: *"L-NNN ids filed to
`planning/learnings/inbox.md` from this phase, or 'none'. **The
`knowledge-curator` will triage these.**"* — i.e. filing is the
precondition for triage, and the retro's own phrasing ("promoting them
further is the knowledge-curator's own triage call, not pre-empted
here") concedes outright that this hand-off has not happened yet, rather
than asserting it has.

`CLAUDE.md` §5 lists as its own, separate Definition-of-Done conjunct:
*"candidate learnings from the phase — including any surfaced by the
retro — have been triaged by the `knowledge-curator` (promote / retain /
merge / discard, per `planning/learnings/`)"*. Against the exact commit
under audit, this conjunct is not satisfied: there is nothing in
`inbox.md`, `promoted.md`, or anywhere under `planning/learnings/` for
either lesson, and no curator pass has run. This is not a matter of
degree or interpretation — the retro's own text and the commit history
agree it hasn't happened. Per the audit's own hard rule ("A verdict token
answers exactly one question" / "A FAIL blocks completion... do not
soften"), I'm not treating this as a non-blocking observation: it is a
named, explicit DoD conjunct, it demonstrably does not hold, and the
phase is not "done" by `CLAUDE.md`'s own terms until it does.

**What would fix this**: dispatch `knowledge-curator` for real against
this retro (and `decisions/0087`/`0088`) and either (a) file the two
lessons above to `planning/learnings/inbox.md` and triage them
(promote/retain/merge/discard), or (b) have the curator make and record
the "already adequately covered by an existing learning" call explicitly
— matching every prior phase's own convention — rather than leaving that
judgment unmade in the retro's own prose.

## A second, narrower, lower-severity finding

`decisions/0087` §2 names exactly four fixture-driven cases
`tests/test_assess_change_impact.py` "must exercise... each as its own
fixture-driven case": a fresh genuine `FAIL`; a fresh digest mismatch
(tested-subject or test-input); **a fresh corrupted/tampered raw output
(`raw_output_sha256` mismatch)**; a fresh all-skipped execution; plus the
no-fresh-result/`VERIFICATION_GAP` case. I read `tests/test_assess_change_impact.py::TestRunCheckAssurance`
directly: it has `test_fresh_fail_is_confirmed_regression`,
`test_fresh_pass_is_verified_scope` (bonus, not required),
`test_fresh_invalid_unresolvable_node_id_is_invalid_assessment` (a
`check_reference`-doesn't-resolve case, not one of the four named),
`test_fresh_invalid_all_skipped_is_invalid_assessment`,
`test_fresh_invalid_test_input_digest_mismatch` (a missing
`test_input_paths` entry causing digest *computation* to fail — a
reasonable proxy for, but not quite, the "digest mismatch between two
computed values" `decisions/0087` names), and
`test_historical_pass_never_masks_a_fresh_fail`. **There is no test
anywhere in the file for a fresh corrupted/tampered raw output** — grep
for `tamper`/`raw_output_sha256` in this file returns nothing relevant to
`run_check_assurance`.

I checked whether this is a real behavioural gap or purely a missing
regression test: `evaluate_result_precedence`'s raw-output-tamper branch
is pre-existing, unmodified `oracle.py` code, already covered generically
by Phase 82's own `tests/test_oracle.py::test_tampered_raw_output_produces_invalid`,
and `run_check_assurance`'s own dispatch for `INVALID` is a single,
reason-agnostic branch already exercised via three other
INVALID-producing paths. So the underlying mechanism is sound and this
is not a correctness defect I could find — it is a literal, named gap
against `decisions/0087` §2's own explicit test-coverage requirement,
which this phase's own governing ADR committed to and the implementation
did not fully deliver. I flag it because `CLAUDE.md` §1's `L-070`/`L-075`
amendments exist precisely to stop a fail-closed mechanism's
verification from being scoped-but-not-depth-complete, and because the
task's own framing names those lessons as applicable here. On its own,
given the mechanism's demonstrated correctness elsewhere, I would treat
this as a non-blocking observation; combined with the knowledge-curator
gap above it reinforces the overall FAIL rather than changing it.

## What must happen before re-audit

1. Dispatch `knowledge-curator` for real against
   `planning/retros/phase-83-semantic-change-assurance.md` and
   `decisions/0087`/`0088`; either file and triage the two retro-surfaced
   lessons, or have the curator explicitly record (in the retro or a
   follow-up note) that they are already adequately covered by an
   existing learning — matching this project's own established
   convention, not merely asserted by the implementing agent.
2. Add a fixture-driven test to `tests/test_assess_change_impact.py`
   exercising a fresh, corrupted/tampered `raw_output_sha256` through
   `run_check_assurance`, asserting `INVALID_ASSESSMENT` specifically —
   the one named case from `decisions/0087` §2 currently missing.
3. Once 1-2 land, re-run this audit against the new commit (this pass is
   voided by any further commit touching audited scope, per `CLAUDE.md`
   §5's own rule).

## Evidence trail

- Full-suite output (two independent runs): `1035 passed, 2 skipped`.
- `check_contracts.py --strict`: exit 0, 7 informational findings (6
  superseded-result + 1 contract-check-gap).
- `check_knowledge_base.py --strict`: exit 0, 24 pre-existing
  informational findings.
- `check_user_docs.py --strict`: no findings.
- Independent dogfood reproduction (disposable scratch clone of
  `~/projects/ledgerkit` at `7224bb5c113cd3aad7e86e994365703cd0070154`):
  baseline hashes matched; mutated-tree full suite `935 passed, 1
  warning, 14 subtests passed`; new test `FAIL` with
  `Decimal('300.00') != Decimal('150.00')` against the mutation, `PASS`
  against clean code; `assess_change_impact.py --run-checks` reported
  `CONFIRMED_REGRESSION (fresh_effective_outcome=FAIL,
  aggregate_state=GAP, observed_outcomes=['FAIL', 'FAIL'])`.
- `git diff bf60804^..HEAD -- src/codecompass/oracle.py
  src/codecompass/graph.py src/codecompass/knowledge_intermediate.py`:
  empty.
- `git diff bf60804^..HEAD -- CLAUDE.md`: empty;
  `decisions/0078`-`0085` unedited this phase.
- No `planning/learnings/inbox.md` entry, no `knowledge-curator` commit,
  for Phase 83, as of `b1a8447`.
