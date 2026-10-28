# Phase 83 — Semantic Change Assurance — independent completion audit

> **This file now contains two passes.** The original pass (below, under
> "Original audit pass") was run against commit `b1a8447` and returned
> **FAIL** on two findings. This section records a full, independent
> re-audit run against the current `main` HEAD, `d076023`, after both
> findings were claimed fixed. Per `CLAUDE.md` §5, any commit touching
> audited scope voids a prior pass — so this re-audit re-ran everything,
> not just the two named findings. The original FAIL section is kept
> below, unedited, for the record.

---

## RE-AUDIT — commit `d076023` (current `main` HEAD)

**Auditor:** `release-phase-auditor` (independent pass, read-only)
**Audited commit:** `d076023` (HEAD, `main` branch)
**Commit range covered since prior pass:** `b1a8447` (prior audited
commit, verdict FAIL) → `23e90a0` (test fix for finding 2) → `d076023`
(knowledge-curator triage, fix for finding 1)
**Plan file:** `planning/phase-83-semantic-change-assurance.md` (§10-14)
**Governing ADRs:** `decisions/0086`, `0087`, `0088`
**Retro under review:** `planning/retros/phase-83-semantic-change-assurance.md`
**Prior audit:** this same file, "Original audit pass" section below
(audited `b1a8447`, verdict FAIL)

### Verdict

**PASS**

Both findings from the prior FAIL are genuinely fixed, not superficially
patched, and nothing else in the two new commits (`23e90a0`, `d076023`)
touches audited scope in a way that reopens any previously-PASSing
conjunct. I re-ran the full verification battery (not just the two
findings) against the exact current commit, confirmed no protected-file
or production-code drift, and independently checked the new test's call
path and the new learnings' factual claims against the actual code
rather than trusting the commit messages.

### What changed since the prior (FAIL) pass

```
git diff b1a8447..d076023 --stat
 planning/learnings/inbox.md                                |  159 ++
 planning/learnings/promoted.md                              |    1 +
 planning/retros/_audit-phase-83.md                          |  318 ++ (the prior FAIL report, committed by 23e90a0)
 planning/retros/phase-83-semantic-change-assurance.md       |   13 +-
 tests/test_assess_change_impact.py                          |   38 ++
```

No changes to `scripts/assess_change_impact.py`, `scripts/check_contracts.py`,
`src/codecompass/oracle.py`, `graph.py`, `knowledge_intermediate.py`, or
any other production code. Scope is exactly: one new test, two filed and
triaged learnings, one retro section update, and the prior audit report's
own commit (by `23e90a0`, which is how the prior FAIL report ended up
version-controlled).

### Finding 1 (prior, non-blocking-on-its-own): missing fresh-tampered-raw-output test — independently re-verified FIXED

Read the new test directly, `tests/test_assess_change_impact.py::TestRunCheckAssurance::test_fresh_tampered_raw_output_is_invalid_assessment`
(commit `23e90a0`):

- It defines a thin `_TamperingOracle` wrapper whose `__getattr__`
  delegates every attribute to the real `codecompass.oracle` module
  **except** `evaluate_check`, which it overrides to call the real
  `oracle.evaluate_check(...)` first and then overwrite the resulting
  `raw_output_ref` file's contents with `"TAMPERED"` before returning.
- It then calls `aci.run_check_assurance(_TamperingOracle(), contract_path,
  contract, "chk-a", repo, tmp_path / "raw", historical_results=[])` —
  i.e. it drives `run_check_assurance` itself, passing the tampering
  wrapper as the `oracle_mod` parameter `run_check_assurance` actually
  takes (confirmed the real signature: `def run_check_assurance(oracle_mod,
  contract_path, contract, check_id, target_repo_root, raw_output_dir,
  historical_results)`, `scripts/assess_change_impact.py` line 327).
- Inside `run_check_assurance`, `oracle_mod.evaluate_check(...)` resolves
  to the wrapper's own override (producing a tampered fresh result), and
  `oracle_mod.evaluate_result_precedence(fresh_result, ...)` resolves via
  `__getattr__` to the real, unmodified `oracle.evaluate_result_precedence`
  — which is where the actual tamper-detection logic lives (pre-existing,
  Phase 82 code). This means the test exercises `run_check_assurance`'s
  own real dispatch (`fresh_effective_outcome == "INVALID" → classification
  = "INVALID_ASSESSMENT"`) against a result that only became tampered
  *after* a real execution inside the real call path — not a hand-built
  `OracleResult` fed in isolation to `oracle.py` alone. This is exactly
  what the prior finding asked for: coverage through `run_check_assurance`'s
  own call path, not merely a re-test of `oracle.py`'s pre-existing
  detection.
- Ran it directly: `.venv/bin/python -m pytest tests/test_assess_change_impact.py -q -k tamper`
  → `1 passed, 27 deselected`. Also ran the whole `TestRunCheckAssurance`
  class and the whole file — all pass (see full-suite run below, which
  now shows `1036 passed` vs. the prior pass's `1035`, i.e. exactly one
  net new test, matching this commit).
- Assertions in the test are substantive, not shallow: it checks
  `classification == "INVALID_ASSESSMENT"`, `fresh_effective_outcome ==
  "INVALID"`, that `fresh_invalid_reason` names `raw_output_ref` and
  `"tampered or corrupted"`, and that `aggregate_state == "GAP"` — the
  same side-by-side-fact pattern every other test in this class uses.

**Verdict on this finding: genuinely fixed.** This is the one case
`decisions/0087` §2 named as missing, now present as its own
fixture-driven case, through the real call path.

### Finding 2 (prior, blocking): no `knowledge-curator` triage had occurred — independently re-verified FIXED

Checked `planning/learnings/inbox.md` for `L-104` and `L-105` (commit
`d076023`):

- **`L-104`** — "a 'historical facts are never deleted' discipline
  established for one consumer... does not automatically propagate to
  every other independent consumer." Read the full entry: it has every
  field this project's own convention requires (`origin`, `date`,
  `project_revision`, `observation`, `evidence`, `classification`,
  `status: retained`, `recurrence`, `moves forward when`) *plus* a
  `curation note (2026-10-28, knowledge-curator)` that is not boilerplate
  — it names and checks all four real call sites of
  `oracle.evaluate_result_precedence` (`oracle.py::aggregate_contract`,
  `knowledge_intermediate.py::derive_epistemic_profile`,
  `scripts/assess_change_impact.py::run_check_assurance`,
  `scripts/check_contracts.py::check_result_integrity`) one at a time,
  explaining concretely why each of the three that weren't the original
  bug is not exposed to the same gap, and concludes "no second live,
  unfixed instance exists today" with an explicit **retain** outcome.
  I independently read `scripts/check_contracts.py` lines ~287-327 and
  confirmed the `current_pass_check_ids` / `superseded` logic the note
  describes is exactly what's actually there (see "Fresh full-battery
  re-run" below, item 2, and the direct code read in the "Cross-checked
  factual claims" subsection).
- **`L-105`** — "a tool's distinct 'knowledge root'-style override
  parameter must be threaded through every internal path resolution."
  Same full schema, with a `curation note` that traces
  `scripts/assess_change_impact.py::classify_symbol`'s actual fix
  (`result_path = knowledge_root / _unquote(raw_ref)`, not the hardcoded
  `ROOT`), checks the file's other two `ROOT` references and confirms
  neither is a second instance of the same bug shape, and names the
  specific pre-existing regression test
  (`tests/test_assess_change_impact.py::TestClassifySymbol::test_behavioural_risk_when_claim_bridges_to_a_real_check`)
  that already exercises `knowledge_root != ROOT` and would catch a
  reversion. Concludes **promote**, with `promoted_to` naming the test +
  fix pair at `b1a8447`.
- **`planning/learnings/promoted.md`**: confirmed the new line —
  `L-105 | 2026-10-28 | invariant | scripts/assess_change_impact.py::classify_symbol
  (knowledge_root threading fix) + tests/test_assess_change_impact.py::
  TestClassifySymbol::test_behavioural_risk_when_claim_bridges_to_a_real_check
  @ b1a8447` — present, correctly formatted, matching every other row in
  the file (`L-089`, `L-090`, `L-097`, `L-101`, etc. — same pipe-delimited
  shape).
- **`planning/retros/phase-83-semantic-change-assurance.md`**'s
  "Candidate learnings filed" section: read it directly — it no longer
  says "None filed." It now reads: "Filed to `planning/learnings/inbox.md`:
  `L-104` (... assessed by `knowledge-curator` 2026-10-28, outcome
  **retain** ...) and `L-105` (... assessed by `knowledge-curator`
  2026-10-28, outcome **promote** ...)." This matches the phrasing
  convention of every prior phase's retro I compared against (e.g.
  Phase-81-third-corrective-pass's "assessed by `knowledge-curator`...
  and found adequately covered").

**Cross-checked factual claims, not just presence of the entries**: I
independently read the actual production code each curation note cites,
rather than trusting the note's own description:

- `scripts/check_contracts.py` lines 287-326 (`check_result_integrity`):
  confirmed `current_pass_check_ids` is computed once per contract by
  recomputing `evaluate_result_precedence` for every result and collecting
  `check_id`s that currently evaluate `PASS`; confirmed the `superseded`
  conditional (`result.check_id in current_pass_check_ids`) only downgrades
  `strict` to `False` when a *different*, currently-passing result exists
  for the same `check_id`; otherwise the finding stays `strict=True`
  (blocking). This matches L-104's description exactly, including the
  "the one real instance is already fixed with its own two regression
  tests" claim — ran
  `tests/test_check_contracts.py -k ResultIntegrity` → `5 passed, 16
  deselected`.
- `scripts/assess_change_impact.py` lines ~240-276 (`classify_symbol`):
  confirmed the docstring's own stated rule ("A `test_ref` is always
  resolved against `knowledge_root` (never the hardcoded CodeCompass
  checkout `ROOT`)") matches the actual code
  (`result_path = knowledge_root / _unquote(raw_ref)`), matching L-105's
  claim exactly — ran `tests/test_assess_change_impact.py -k
  ClassifySymbol` → `3 passed, 25 deselected`.

Both learnings' format, depth, and curation-note substance match this
project's own established convention (compared directly against
`L-101`, `L-103`, and the Phase-81 triage commits named in the prior
FAIL report) — this is not a superficial, audit-satisfying stub. Each
note does real work: it enumerates every call site rather than asserting
"checked," names concrete line numbers and test names, and reaches a
specific, justified promote/retain outcome rather than a generic "looks
fine."

**Verdict on this finding: genuinely fixed**, not merely formally
present.

### Fresh full-battery re-run (not limited to the two findings)

1. **Full suite**: `.venv/bin/python -m pytest -q` → **1036 passed, 2
   skipped** (298.72s) — exactly one more than the prior pass's `1035`,
   matching the one net-new test added in `23e90a0`.
2. **`scripts/check_contracts.py --strict`** → exit `0`, **7
   informational findings**, identical in kind and count to the prior
   pass (6 `contract-result-integrity-mismatch` + 1 `contract-check-gap`,
   each explicitly labelled superseded/known-gap, none newly blocking).
3. **`scripts/check_knowledge_base.py --strict`** → exit `0`, **24
   informational findings**, same pre-existing
   `knowledge-base-snapshot-current-divergence` entries as the prior
   pass — the two new `planning/learnings/` files are outside this
   script's scope (it validates `planning/knowledge/`, not
   `planning/learnings/`); confirmed no new finding appeared.
4. **`scripts/check_user_docs.py --strict`** → "no findings", exit `0`
   (this is also where the project's own learnings-schema/status
   conventions are mechanically checked — ran clean, confirming
   `L-104`/`L-105` conform).
5. **`src/codecompass/oracle.py`, `graph.py`, `knowledge_intermediate.py`
   unmodified**: `git diff b1a8447..HEAD -- <those three files>` is
   empty.
6. **`scripts/assess_change_impact.py`, `scripts/check_contracts.py`
   unmodified since `b1a8447`**: `git diff b1a8447..HEAD -- <those two
   files>` is empty — confirming neither new commit touched the
   production logic the prior pass's dogfood reproduction exercised, so
   that reproduction (prior pass item 7) remains valid evidence and did
   not need to be redone from scratch. I did re-read
   `run_check_assurance` and `classify_symbol` directly (above) as a
   lighter-touch confirmation that the code the dogfood run exercised is
   still exactly what's there.
7. **Protected-file drift**: `git diff b1a8447..HEAD -- CLAUDE.md` is
   empty. `decisions/0078`-`0087` show no changes in this range
   (`git diff b1a8447..HEAD --stat` touches only the five files listed
   above — no `decisions/*` file at all, so none of the historically
   protected ADRs were touched). `decisions/0088` has exactly one commit
   in its history (`b1a8447`, its own creation) — unedited since.
8. **`ROADMAP.md`/`CONTEXT.md`**: still correctly state Phase 83 `in
   progress` ("implemented; independent completion audit not yet run") —
   neither was flipped to `done` ahead of this audit, which would itself
   have been a process violation; this re-audit is what authorizes that
   transition going forward, not something already assumed.
9. **Working tree**: `git status` → clean, nothing uncommitted.

### Point-by-point findings (final)

1. Verification commands — PASS (re-run above, same findings as before).
2. `oracle.py`/`graph.py`/`knowledge_intermediate.py` unmodified — PASS.
3. Dogfood claim — PASS (not re-reproduced from scratch again, since
   neither new commit touches the exercised code; re-confirmed via
   direct code read that the exercised paths are unchanged, consistent
   with how much verification is warranted given the diff).
4. Two originally-required checks still PASS for real — PASS (unchanged;
   `check_contracts.py --strict` re-run confirms the same 2
   currently-PASSing checks, now also correctly not blocked by their 6
   superseded historical results per the `decisions/0088` fix).
5. Knowledge-base reconciliation — PASS (unchanged).
6. `decisions/0088`'s fix doesn't weaken the original guarantee — PASS
   (re-confirmed via direct re-read and the two regression tests' own
   re-run).
7. Outstanding item (Ledgerkit test not yet landed upstream) honestly
   reflected in ROADMAP/CONTEXT — PASS (unchanged, still explicit).
8. No protected-file drift — PASS (re-confirmed against the new HEAD).
9. Candidate learnings triaged — **PASS** (was the blocking FAIL; now
   genuinely fixed, see above).
10. Named missing test case (`decisions/0087` §2's fresh-tampered-raw-output
    case) — **PASS** (was the second, lower-severity finding; now
    genuinely fixed, see above).

### Why this is PASS and not PASS WITH NON-BLOCKING OBSERVATIONS

Every finding from the prior pass is closed, with independent evidence
behind each closure rather than trust in the commit messages, and
nothing newly introduced by the two fix commits raises a fresh concern:
the new test genuinely exercises the named call path with substantive
assertions; the two learnings are filed, triaged with real per-call-site
analysis, and consistent with the project's own established convention;
no protected file or production code was touched; the full verification
battery is clean at exactly the expected counts. I have no residual
observation worth flagging as non-blocking.

### What remains outside this audit's scope (unchanged, correctly so)

The one cross-repository item named throughout this phase — landing the
new Ledgerkit regression test
(`tests/test_reports.py::TestBalanceFromSpec::test_section_accounts_overlapping_patterns_no_double_count`)
in the real `~/projects/ledgerkit` checkout — remains explicitly
unresolved and separately gated, exactly as `ROADMAP.md`/`CONTEXT.md`
state. This was never a DoD conjunct for *this* phase (the phase's own
plan treats it as a deliberately deferred, separately-authorized
follow-on, consistent with `decisions/0086`/`0087`), so its absence does
not affect this verdict.

### Next step

Per `CLAUDE.md` §5, this PASS is what authorizes the terminal
`roadmap-context-curator` reconciliation commit (flipping
`planning/ROADMAP.md`'s Phase 83 row to `done`, overwriting
`planning/CONTEXT.md`'s current-state section, and updating the phase
plan file's own Status line — nothing else) — that commit itself is
exempted from re-voiding this audit per §5's own named carve-out, so no
further audit pass is needed purely for that commit landing. Any other
commit first touching audited scope would void this pass again.

---

## Original audit pass — commit `b1a8447` (superseded by the re-audit above; kept for the record)

**Auditor:** `release-phase-auditor` (independent pass, read-only)
**Audited commit:** `b1a8447` (HEAD at audit time, `main` branch)
**Commit range covered:** `bf60804` (first corrective amendment,
decisions/0086) → `597f819` (second corrective amendment,
decisions/0087) → `b1a8447` (implementation, decisions/0088, retro)
**Plan file:** `planning/phase-83-semantic-change-assurance.md` (§10-14)
**Governing ADRs:** `decisions/0086`, `0087`, `0088`
**Retro under review:** `planning/retros/phase-83-semantic-change-assurance.md`

### Verdict

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

### What I independently re-ran (not trusted from the retro alone)

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

### Point-by-point findings (against the task's 9 items)

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

### The blocking finding: no `knowledge-curator` triage actually occurred

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

### A second, narrower, lower-severity finding

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

### What must happen before re-audit

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

**Resolution (see re-audit above): both items landed — item 2 in
`23e90a0`, item 1 in `d076023` — and the re-audit against `d076023`
verdict is PASS.**

### Evidence trail (original pass)

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

---

## Corrective pass audit (2026-10-28, decisions/0089, against commit 057e59d)

**Auditor:** `release-phase-auditor` (independent pass, read-only)
**Audited commit:** `057e59d` (HEAD, `main` branch, at audit time)
**Commit range covered this pass:** `1e5c00c` (corrective planning
amendment, decisions/0089) → `365dec1` (fix implementation) → `057e59d`
(L-106 candidate-learning filing)
**Governing ADR:** `decisions/0089-phase-83-corrective-pass-identity-coverage-evidence.md`
**Governing prompt:** "CodeCompass Orchestrator — Phase 83 Corrective
Pass" (post-completion source review; does **not** reopen Phase 82, does
not expand Phase 83 into Phase 84 functionality)
**Scope note:** Phase 83 is already `done` and already independently
audited PASS (see the re-audit section above, against `d076023`). This
is a corrective pass *on top of* that done phase, not a re-opening of
its own DoD gate — this section answers "is this corrective pass itself
sound and fully closed out," not "should Phase 83's `done` status
change."

### Verdict

**PASS**

All three defects decisions/0089 claims to have fixed are genuinely
fixed, read directly in the function bodies rather than inferred from
passing tests. The untouched-module claim is exact (byte-for-byte empty
diffs, both against the immediate pre-pass commit and against the
original Phase 83 closeout commit). The new tests exercise each fix at
its real call path, including the specific regression shapes named by
the ADR (cross-file same-named-symbol, multi-symbol/EOF/partial-coverage
ranges, each of the five ways a referenced historical result can fail
real validation). The full suite, the two pre-existing Phase 82 test
modules, and all three strict validators are green at exactly the
expected counts, with the canonical `balance-from-spec` knowledge/
contract trees confirmed untouched. Documentation (CHANGELOG, ROADMAP,
CONTEXT, contributing.md) is mutually consistent and accurate against
the real current code. The one candidate learning this pass filed
(L-106) has, as of this audit, already been triaged by `knowledge-curator`
(a `retained` outcome with a substantive curation note, landed between
my starting this audit and finishing it) — so no outstanding DoD-style
gap remains even on that count, though see the note below on why that
triage was not, in any case, strictly load-bearing for this specific
pass's own closeout.

### 1. The three defects — read directly, not inferred from tests

Read `scripts/assess_change_impact.py` in full as it exists at `057e59d`
(630 lines) and confirmed each fix is genuinely present as code, not only
as a passing test:

- **Defect A (source-path-qualified identity).**
  `classify_symbol()` (line 308) now takes `source_path: str`, computes
  `normalized_source_path = _normalize_source_path(source_path)` (line
  326, `PurePosixPath(...).as_posix()`), and the citing-Evidence loop
  (lines 328-339) requires **both**
  `match.group("symbol") == symbol_name` **and**
  `_normalize_source_path(match.group("path")) == normalized_source_path`
  before adding to `citing_evidence_ids`. The single call site,
  `assess()` line 521, passes `c.path` (the `--changed` range's own
  path) as `source_path` — confirming the fix is actually wired into its
  one real caller, not merely available as an unused parameter
  (`CLAUDE.md` §1's `L-021` concern).
- **Defect B (multi-symbol resolution + end validation).**
  `resolve_enclosing_symbol` no longer exists in the file (confirmed by
  reading the whole file — only `resolve_intersecting_symbols`, line
  175, remains, built on `compute_symbol_spans`, line 164, exactly the
  "a symbol's span runs from its own line to one less than the next
  symbol's line, or EOF for the last symbol" convention the plan already
  named). `resolve_changed_range` (line 213) now validates
  `changed.start > line_count` (line 247) **and** separately
  `changed.end > line_count` (line 252) — two distinct checks, not one
  reused for both. `matched = resolve_intersecting_symbols(...)` (line
  258) can return more than one `SymbolSpan`; `RangeResolution.symbols`
  (line 210) is plural (`list[SymbolRow]`). A new `partially_resolved`
  status (line 208, 274-279) fires when `uncovered` (computed by set
  difference against every matched span's own coverage, lines 267-272)
  is non-empty, with `_describe_uncovered_lines` (line 186) naming the
  specific gap. `assess()` (lines 517-531) iterates `res.symbols`,
  classifies each independently, and deduplicates applicable checks per
  range via `check_contributors: dict[str, set[str]]` keyed by
  `check_id` (line 518, 529-530), with `AssuranceFinding.contributing_symbols`
  (line 412, populated line 546) preserving per-symbol provenance exactly
  as decisions/0089 §B describes.
- **Defect C (validated historical-result evidence).**
  `classify_symbol()` now takes `oracle_mod` (line 309) and, for each
  `test`-kind Evidence (lines 354-374), calls
  `oracle_mod.parse_oracle_result(result_path)` inside a
  `try/except oracle_mod.OracleSchemaError: continue` (lines 363-366) —
  no bare `yaml.safe_load` anywhere in this function. On successful
  parse, it additionally checks `result.contract_id != contract.contract_id`
  (367-368), `contract.check_by_id(result.check_id) is None` (369-371),
  and `result.scope != check.scope` (372-373) — all three reject-and-skip,
  matching decisions/0089 §C's three named identity/scope checks exactly.
  Confirmed `classify_symbol` has no `repo_root` parameter anywhere in
  its signature and never calls `evaluate_result_precedence` — the ADR's
  own "this must stay a structurally separate, historical-relationship-
  only check, never a current-execution-outcome one" design constraint
  holds in the actual code, not only in the ADR's prose.

All three fixes read exactly as decisions/0089 describes them, with no
daylight between the ADR's claimed design and the shipped code.

### 2. `oracle.py` / `graph.py` / `knowledge_intermediate.py` — confirmed genuinely untouched

```
git diff 1e5c00c^ 057e59d -- src/codecompass/oracle.py src/codecompass/graph.py src/codecompass/knowledge_intermediate.py
```
→ 0 lines (empty). Additionally confirmed byte-identical to the original
Phase 83 closeout commit:
```
git diff 5132529 057e59d -- src/codecompass/oracle.py   → 0 lines
git diff 5132529 057e59d -- src/codecompass/graph.py     → 0 lines
git diff 5132529 057e59d -- src/codecompass/knowledge_intermediate.py → 0 lines
```
Both comparisons are empty — the three modules are untouched by this
corrective pass under either reference point decisions/0089 and the
task named. Every fix really is achieved by `assess_change_impact.py`
using these modules' existing public surface more completely
(`oracle.parse_oracle_result`, `OracleContract.check_by_id`), exactly as
claimed.

### 3. `tests/test_assess_change_impact.py` — exercises each fix at the real call path

Read the relevant classes directly (not just their names):

- **`TestClassifySymbolSourceIdentity`** (3 tests): the first,
  `test_same_named_symbol_in_a_different_file_does_not_inherit_evidence`,
  is the exact regression shape the ADR names — an Evidence citing
  `other.py:5 def target_function` must not answer for `impl.py`'s own
  `target_function`; calls `classify_symbol(..., "target_function",
  "impl.py", tmp_path)` directly (the real function, real signature,
  real parameter) and asserts `no_recorded_relationship`. The second is
  a positive control with a same-named decoy present alongside a
  genuinely matching Evidence, asserting only the matching one's Claim
  surfaces. The third confirms `./impl.py`/`impl.py` normalise
  identically. All three call `classify_symbol` directly with real
  `oracle`, real `contract`, real loaded `records` — not a stub.
- **`TestClassifySymbolEvidenceValidation`** (7 tests): valid historical
  result → `behavioural_risk`; malformed YAML (`not: valid: yaml: [[[`
  ) → `relevant_no_coverage_link`; missing-required-fields ("the exact
  malformed shape the original defect accepted" — a bare `check_id`/
  `outcome` mapping, exactly what decisions/0089's Context section
  quotes as the original vulnerable shape) → rejected; wrong
  `contract_id` → rejected; wrong `scope` → rejected; unknown `check_id`
  → rejected; missing referenced file → rejected. All seven call
  `classify_symbol` directly and go through `_write_fake_result`, which
  builds a real `oracle.OracleResult` and writes it via
  `oracle.write_oracle_result` — genuine schema-valid-or-invalid fixture
  data, not hand-typed mappings bypassing the real writer.
- **`TestResolveChangedRange`** additions: `test_cannot_map_end_past_file_extent`
  (explicitly comments "previously only `start` was validated... must
  also be rejected"); `test_cannot_map_line_before_any_symbol`;
  `test_range_crossing_multiple_functions_resolves_all` (asserts both
  `helper` and `target_function` resolve from one range); `test_file_level_change_resolves_every_symbol`;
  `test_partially_resolved_when_range_extends_before_first_symbol`
  (asserts `partially_resolved` status, `symbols == ["helper"]`, and
  `"1-3"` named in the reason — the specific unmapped-lines message);
  `test_duplicate_applicable_checks_deduplicated_with_provenance` (two
  symbols bridging to the same check — asserts exactly one assurance
  entry, with both symbol names in `contributing_symbols`). Each calls
  `aci.resolve_changed_range` or `aci.assess` directly — the real
  functions, not reimplementations.

All three classes are genuine, substantive regression coverage against
the real call paths, not re-tests of something else dressed up as
coverage of the fix.

### 4. Full verification battery — independently re-run

- **Full suite**: `.venv/bin/python -m pytest -q` → **1054 passed, 2
  skipped** (295.01s) — exactly the expected count.
- **`tests/test_oracle.py` + `tests/test_check_contracts.py`**: `.venv/bin/python
  -m pytest -q tests/test_oracle.py tests/test_check_contracts.py` →
  **67 passed** — green, unmodified Phase 82 coverage.
- **`scripts/check_contracts.py --strict`** → exit `0`, **7 informational
  findings** (6 `contract-result-integrity-mismatch` + 1
  `contract-check-gap`) — identical in count and kind to both prior
  passes; no new finding from this corrective pass (it added no
  knowledge records or contract entries, as decisions/0089 states).
- **`scripts/check_knowledge_base.py --strict`** → exit `0`, **24
  informational findings** (counted via `grep -c`) — same pre-existing
  `knowledge-base-snapshot-current-divergence` shape as both prior
  passes.
- **`scripts/check_user_docs.py --strict`** → "no findings", exit `0`.
- **`git status --short planning/knowledge/balance-from-spec/
  planning/contracts/balance-from-spec/`** → empty. The real, canonical
  knowledge/contract trees for this slug are completely untouched by
  this corrective pass, consistent with the retro's claim that the
  Ledgerkit re-demonstration used only disposable scratch copies.

All counts match exactly what decisions/0089 and the retro's own
"Corrective pass" section claim.

### 5. Retro's "Corrective pass" section — internally consistent, cross-checked

Read `planning/retros/phase-83-semantic-change-assurance.md`'s final
section in full. Its factual claims (test counts, suite counts, strict-
validator counts, Ledgerkit pinned HEAD/hashes, the `935 passed, 1
warning, 14 subtests passed` baseline-reproduction number, the
`CONFIRMED_REGRESSION`/`VERIFIED_SCOPE` outcomes, the real-Ledgerkit
multi-symbol/`end`-validation spot-check against `reports.py:490-600`
and `reports.py:644-999999`) are all internally consistent with
decisions/0089's own account and with the diff I read directly. I did
not re-run the Ledgerkit scratch demonstration myself (per the task's
own instruction, since it depends on `~/projects/ledgerkit` and its own
`.venv`) but confirmed `~/projects/ledgerkit` exists on this machine and
that nothing in the real, canonical `planning/knowledge/balance-from-spec/`
or `planning/contracts/balance-from-spec/` trees was touched (item 4
above) — the retro's claim that the demonstration's artifacts (scratch
`EV-BFS-004`, patched contract, placeholder result) exist only under a
scratchpad path, never committed, is consistent with the actual `git
status` result and with the commit's own file list (`git diff --name-only`,
below) containing no `planning/knowledge/` or `planning/contracts/`
entries at all.

### 6. `L-106` triage status

`planning/learnings/inbox.md` lines 11-120: `L-106` carries a full
schema-conforming entry (`origin`, `date`, `project_revision`,
`observation`, `evidence`, `classification`, `recurrence`, `moves
forward when`) **and** a dated `curation note (2026-10-28,
knowledge-curator)` with `status: retained` — the curator's note is
substantive, not boilerplate: it independently re-reads decisions/0089
and the current fixed code, confirms the "reused only part of an
existing convention" framing holds cleanly for defects A and C but is a
"stretch" for defect B (nothing elsewhere in the codebase already
validated `end` or resolved multi-symbol ranges — B is the function's
own first-cut limitation, not reuse of a sibling convention), and names
this imprecision explicitly rather than silently waving it through. It
also checks for duplication against `L-105` and `L-075`/`CLAUDE.md` §1
and reasons concretely about why `retain` rather than `promote`/`merge`/
`discard` is the right call. This triage had **not yet landed** when I
began this audit (the task description flagged it as a possible, named,
non-blocking-by-default gap, dispatched in parallel) but had landed by
the time I checked — so there is, as of the audited state, no
outstanding triage gap at all.

Separately from whether it landed: per `CLAUDE.md` §5, the triage
conjunct is a condition of a phase's own `done` transition. This
corrective pass does not re-execute that transition — Phase 83 is
already `done` and stays `done` throughout (decisions/0089's own
Consequences section, the retro, and ROADMAP/CONTEXT all say so
explicitly) — so even had the triage still been outstanding at audit
time, it would not have blocked *this pass's own* closeout, only
anything that tried to re-invoke §5's `done`-marking gate against Phase
83 a second time (which nothing in this pass does). This distinction is
noted for the record rather than left ambiguous.

### 7. `docs/development/contributing.md` — accurate against the real current code

Read the `scripts/assess_change_impact.py` bullet (line 28) in full and
checked each clause against the code read in §1 above: "resolves each
range against **every** indexed first-party symbol whose own span
intersects it (not only the one enclosing the range's start)" —
matches `resolve_intersecting_symbols`; "both `start` and `end` lie
within the file's own extent" — matches the two separate validations;
"a range only partly covered by indexed symbols is reported
`partially_resolved`, naming the unmapped line(s) explicitly" — matches
`_describe_uncovered_lines`/the `partially_resolved` branch; "a
*path-and-symbol*-matching Evidence" — matches the Defect A fix; "a
Claim bridges it to a check-resolving test-evidence that itself parses
as a real, correctly-scoped `OracleResult` for the live contract" —
matches the Defect C fix; "each `behavioural_risk` check is freshly
re-executed exactly once per range (deduplicated across symbols that
share it, with every contributing symbol still named)" — matches the
`check_contributors`/`contributing_symbols` dedup logic. Every clause is
accurate against the actual shipped code, not a stale description of an
earlier version.

### 8. `CHANGELOG.md` / `ROADMAP.md` / `CONTEXT.md` — mutually consistent, accurate against `decisions/0089`

Read all three directly. `CHANGELOG.md`'s "Phase 83 corrective pass"
`[Unreleased]` entry describes all three fixes, the module-unmodified
claim, the 18-new-tests/46-total count, and the re-validation against
Ledgerkit scratch copies and real data — consistent with decisions/0089
and with the code I read. `planning/ROADMAP.md`'s Phase 83 row appends a
"**Corrective pass (2026-10-28...)**" clause to the existing `done` row
(rather than replacing or contradicting the original closeout
description), names the same three defects/fixes, the same 18/46 test
counts, and points to `decisions/0089` and the retro for full history —
the row still reads `done`, unchanged. `planning/CONTEXT.md`'s "Current
phase"/"What was just completed" sections describe the same three fixes
in the same terms, explicitly state "Independent audit of this
corrective pass is in progress. Phase 83 stays `done`; this was not a
reopening" — an accurate statement of exactly what was true on-disk
before this audit ran, and consistent with ROADMAP.md and decisions/0089
throughout. No contradiction found across any of the three documents or
against the ADR.

### Protected-file drift and scope-creep check

```
git diff 1e5c00c^ 057e59d -- CLAUDE.md          → 0 lines (empty)
git diff 1e5c00c^ 057e59d --stat -- decisions/  → only the new 0089 file added (200 insertions, 0 deletions to any existing ADR)
git diff --name-only 1e5c00c^ 057e59d:
  CHANGELOG.md
  decisions/0089-phase-83-corrective-pass-identity-coverage-evidence.md
  docs/development/contributing.md
  planning/CONTEXT.md
  planning/ROADMAP.md
  planning/learnings/inbox.md
  planning/phase-83-semantic-change-assurance.md
  planning/retros/phase-83-semantic-change-assurance.md
  scripts/assess_change_impact.py
  tests/test_assess_change_impact.py
```
No `CLAUDE.md` edit. No existing ADR's original content touched — only a
new, sequentially-numbered ADR added. No `src/` file touched. Every
changed file matches decisions/0089's own stated scope (fix +
tests + the governing ADR + the required doc-sync set + the phase plan's
own as-built update + the retro's closing section + the learnings
inbox). No scope creep.

### Why PASS and not PASS WITH NON-BLOCKING OBSERVATIONS

Every one of the eight items in the dispatch was independently checked
against the real commit, not trusted from the ADR's or retro's own
prose, and every one held up: the three defects are genuinely fixed as
described; the three excluded modules are byte-identical to both
reference points; the new tests are real, substantive, call-path-level
regression coverage for each fix; the full suite and both targeted test
modules are green at the exact expected counts; all three strict
validators exit 0 with unchanged finding counts; the canonical
knowledge/contract trees are untouched; the one candidate learning this
pass raised has already been triaged with a substantive, non-boilerplate
note; and all four governing/doc-sync artifacts (ADR, CHANGELOG,
ROADMAP, CONTEXT) are mutually consistent and accurate against the real
code. I found no gap, however minor, worth flagging as a residual
observation.

### Evidence trail (this pass)

- `scripts/assess_change_impact.py` read in full (630 lines) at
  `057e59d`; Defect A/B/C fixes confirmed present at the specific lines
  cited above, each wired into its one real call site.
- `git diff 1e5c00c^ 057e59d -- src/codecompass/oracle.py
  src/codecompass/graph.py src/codecompass/knowledge_intermediate.py`:
  empty (0 lines each).
- `git diff 5132529 057e59d` for the same three files: empty (0 lines
  each) — confirmed against the original Phase 83 closeout commit too.
- `tests/test_assess_change_impact.py`'s `TestClassifySymbolSourceIdentity`,
  `TestClassifySymbolEvidenceValidation`, and the new
  `TestResolveChangedRange` cases read in full and confirmed to call the
  real functions with the real regression shapes named by decisions/0089.
- `.venv/bin/python -m pytest -q` → `1054 passed, 2 skipped` (295.01s).
- `.venv/bin/python -m pytest -q tests/test_oracle.py
  tests/test_check_contracts.py` → `67 passed`.
- `scripts/check_contracts.py --strict` → exit 0, 7 informational
  findings.
- `scripts/check_knowledge_base.py --strict` → exit 0, 24 informational
  findings.
- `scripts/check_user_docs.py --strict` → no findings, exit 0.
- `git status --short planning/knowledge/balance-from-spec/
  planning/contracts/balance-from-spec/` → empty.
- `planning/learnings/inbox.md` `L-106`: schema-complete, status
  `retained`, curation note present and substantive.
- `docs/development/contributing.md` line 28 cross-read against the
  actual code; `CHANGELOG.md`, `planning/ROADMAP.md`, `planning/CONTEXT.md`
  all read in full for the Phase 83 corrective-pass content and found
  mutually consistent and accurate against `decisions/0089`.
- `git diff 1e5c00c^ 057e59d -- CLAUDE.md`: empty; `git diff --stat --
  decisions/` shows only the new `0089` file added, no existing ADR
  edited.
- `git diff --name-only 1e5c00c^ 057e59d`: 10 files, all within
  decisions/0089's own stated scope — no scope creep.

---

## FINAL AMENDMENT AUDIT — commit `2436e39` (2026-10-29)

**Auditor:** `release-phase-auditor` (independent pass, read-only)
**Audited commit:** `2436e39` (on top of `7e8c538`, the prior-audited
corrective-pass commit)
**Scope:** one narrowly scoped fourth corrective amendment,
`decisions/0090` — `classify_symbol()` in `scripts/assess_change_impact.py`
never compared a historical `OracleResult`'s own `oracle_contract_id`
against the live contract, only its `contract_id`.
**Plan file:** `planning/phase-83-semantic-change-assurance.md` (§0, §3.2,
§10.13, §12 final-amendment addendum)
**Governing ADR:** `decisions/0090-phase-83-oracle-contract-id-validation.md`
**Retro section under review:** `planning/retros/phase-83-semantic-change-assurance.md`,
"Final corrective amendment (2026-10-29, `decisions/0090`)"

### Verdict

**PASS**

This is a correctly scoped, correctly documented, genuinely-verified
one-line defect fix. I independently reproduced the defect myself (not
by trusting the new test or the commit message), confirmed the fix
closes it, re-ran the full required verification battery myself against
the actual commit, and found the commit's file-level scope, protected-file
boundaries, and documentation consistency all exactly as claimed.

### What I independently checked

**1. `decisions/0090` read in full.** Accurately documents: the defect
(`classify_symbol()`'s historical-evidence validation checks
`result.contract_id == contract.contract_id` but never
`result.oracle_contract_id`); the schema fact grounding it (`OracleResult`
carries both fields, both required by `_RESULT_REQUIRED`, confirmed
directly in `src/codecompass/oracle.py` lines 140-177); the precedent cited
(`evaluate_result_precedence` at `oracle.py:733-737` already compares
`result.contract_id != contract.contract_id or result.oracle_contract_id
!= contract.contract_id` — confirmed by direct read, line numbers match
exactly); and the "why not route through `evaluate_result_precedence`"
rationale (it also recomputes a live content-hash comparison, a
current-execution-outcome question, which would retroactively invalidate
historical results predating a later unrelated contract extension — this
is the same rationale `decisions/0089` §C already used for its own,
narrower structural check, and is consistent with it, not a new or
contradictory argument).

**2. `git show 2436e39` read in full.** The only functional change in
`scripts/assess_change_impact.py` is the two-line addition inside
`classify_symbol()`'s test-Evidence loop:
```python
if result.oracle_contract_id != contract.contract_id:
    continue
```
immediately after the pre-existing `contract_id` check, plus a
documentation-comment update above it (no other logic touched). Confirmed
`src/codecompass/oracle.py`, `src/codecompass/graph.py`,
`src/codecompass/knowledge_intermediate.py` are **not present** in this
commit's diff at all, and `git diff 7e8c538 2436e39 -- src/codecompass/oracle.py
src/codecompass/graph.py src/codecompass/knowledge_intermediate.py`
produced empty output — byte-identical to the state audited in the prior
`7e8c538` pass.

**3. Independently reproduced the defect myself**, not trusting the new
test. Temporarily reverted *only* the two added lines (via a scripted
`str.replace` on the exact needle text, restored afterward via `git
checkout --`), then ran
`tests/test_assess_change_impact.py::TestClassifySymbolEvidenceValidation::test_wrong_oracle_contract_id_never_establishes_coverage`
against the reverted code: it failed with
`AssertionError: assert 'behavioural_risk' == 'relevant_no_coverage_link'`
— confirming the defect is real (a result with a correct `contract_id`
but a wrong `oracle_contract_id` wrongly established `behavioural_risk`
coverage). Restored the fix via `git checkout -- scripts/assess_change_impact.py`
(confirmed clean via `git diff --stat`), re-ran the same test: 1 passed.
The regression test genuinely exercises the fixed code path — it is not
a test that merely passes against already-correct code.

**4. Re-ran, myself, the full required verification battery against
commit `2436e39`:**
- `tests/test_assess_change_impact.py` → **47 passed** (exact match).
- `tests/test_oracle.py` + `tests/test_check_contracts.py` → **67 passed**
  (Phase 82 regression untouched, exact match).
- Full suite, `.venv/bin/python -m pytest -q` → **1055 passed, 2 skipped**
  (exact match — one more pass than the prior `7e8c538` baseline of 1054,
  matching exactly the one new test added).
- `scripts/check_contracts.py --strict` → exit 0, **7** informational
  findings (unchanged from prior baseline).
- `scripts/check_knowledge_base.py --strict` → exit 0, **24** informational
  findings (unchanged from prior baseline).
- `scripts/check_user_docs.py --strict` → exit 0, **no findings**
  (unchanged from prior baseline).

**5. Doc-sync cross-read.** `planning/phase-83-semantic-change-assurance.md`
(status line, §3.2's corrected description, new §10.13 scenario, and the
new "Final corrective amendment, confirmed" verification note),
`planning/retros/phase-83-semantic-change-assurance.md` (new "Final
corrective amendment" section — goal, fix, regression test, verification,
closure statement all present and accurate), `CHANGELOG.md` (new
`[Unreleased]` entry, correctly distinct from the `decisions/0089` entry
below it, no batching of two amendments into one entry), `planning/ROADMAP.md`
(Phase 83 row's final-amendment sentence added, outstanding-item sentence
preserved unchanged), `planning/CONTEXT.md` (current-state section
overwritten, not appended-around; 47/1055/2 figures match what I
independently reproduced), and `docs/development/contributing.md` (the
`assess_change_impact.py` bullet's classification description now reads
"a real `OracleResult` whose `contract_id` **and** `oracle_contract_id`
both identify the live contract" — this is the corrected, current
behaviour, not the stale single-field description) — all read in full and
found mutually consistent and accurate against the actual code. No doc
anywhere in the repo was found describing the old, unfixed
single-field-check behaviour as current (checked via targeted grep across
`docs/`, `architecture/`, and the plan file for an unqualified "contract_id
matches the live contract" claim lacking the `oracle_contract_id`
companion — none found).

**6. Protected-file and cross-repository boundary checks.**
`git diff 7e8c538 2436e39 -- CLAUDE.md` → empty (no protected-file drift).
`git show 2436e39 --name-status -- decisions/` → only `decisions/0090-*.md`
added (`A`), no existing ADR edited. `git status --short planning/knowledge/
planning/contracts/` → empty (no canonical-corpus drift); confirmed the
commit's own file list contains no `planning/knowledge/` or
`planning/contracts/` path. The real `~/projects/ledgerkit` checkout has
pre-existing, unrelated uncommitted changes (`dev-docs/clean-room/`
material, from a separate clean-room reconstruction effort, tip commit
`7224bb5`) that predate and are untouched by this commit — commit `2436e39`
itself is entirely contained within the `codecompass` repository and
touches no file under `ledgerkit` at all.

**7. Scope check.** `git show 2436e39 --stat` lists exactly the 9 files
named in the task: `CHANGELOG.md`, `decisions/0090-phase-83-oracle-contract-id-validation.md`,
`docs/development/contributing.md`, `planning/CONTEXT.md`,
`planning/ROADMAP.md`, `planning/phase-83-semantic-change-assurance.md`,
`planning/retros/phase-83-semantic-change-assurance.md`,
`scripts/assess_change_impact.py`, `tests/test_assess_change_impact.py`.
No other file touched; no scope creep.

### Evidence trail (this pass)

- `decisions/0090-phase-83-oracle-contract-id-validation.md` read in full.
- `git show 2436e39` (full diff) read in full.
- `git diff 7e8c538 2436e39 -- src/codecompass/oracle.py src/codecompass/graph.py src/codecompass/knowledge_intermediate.py` → empty.
- `src/codecompass/oracle.py` lines 140-177, 321-406, 610-638, 733-737 read directly to confirm the `OracleResult` schema and `evaluate_result_precedence`'s own two-field comparison.
- `scripts/assess_change_impact.py` lines 300-400 (the full `classify_symbol` evidence-validation loop) read directly.
- `tests/test_assess_change_impact.py` lines 560-730 (the full `TestClassifySymbolEvidenceValidation` class plus `_write_fake_result` helper) read directly.
- Independent repro: reverted the two added lines via a standalone script, ran the new regression test (failed, `behavioural_risk` wrongly returned), restored via `git checkout --`, re-ran (1 passed).
- `.venv/bin/python -m pytest -q tests/test_assess_change_impact.py` → 47 passed.
- `.venv/bin/python -m pytest -q tests/test_oracle.py tests/test_check_contracts.py` → 67 passed.
- `.venv/bin/python -m pytest -q` (full suite) → 1055 passed, 2 skipped.
- `scripts/check_contracts.py --strict` → exit 0, 7 informational findings.
- `scripts/check_knowledge_base.py --strict` → exit 0, 24 informational findings.
- `scripts/check_user_docs.py --strict` → exit 0, no findings.
- `git status --short planning/knowledge/ planning/contracts/` → empty.
- `git -C ~/projects/ledgerkit status --short` / `log -1` → pre-existing, unrelated dirty state, untouched by this commit.
- `git diff 7e8c538 2436e39 -- CLAUDE.md` → empty.
- `git show 2436e39 --name-status -- decisions/` → only `0090` added.
- `git show 2436e39 --stat` / `--name-only` → exactly the 9 named files.

### Conclusion

All seven numbered checks in the task hold. This closes the Phase 83
corrective line of work: four corrective amendments (`decisions/0086`/
`0087`/`0088`/`0089`/`0090` — five ADRs across four passes), each
independently audited, the last (this one) with no residual findings of
any kind, blocking or non-blocking. The one still-outstanding,
separately-gated item (the real Ledgerkit overlapping-pattern test
landing in `~/projects/ledgerkit`) remains exactly as outstanding as
before — unaffected by this amendment, not a blocker to this verdict or
to Phase 84.
