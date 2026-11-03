# Independent DoD audit — Phase 86 (Knowledge-Placement and Code-Quality Review)

**Auditor**: `release-phase-auditor` (independent dispatch)
**Audited commit**: `86fb495` (HEAD at dispatch time, `main`, working tree clean before and after this audit)
**Plan**: `planning/phase-86-knowledge-placement-code-quality-review.md`
**Retro**: `planning/retros/phase-86-knowledge-placement-code-quality-review.md`

## Verdict: **PASS WITH NON-BLOCKING OBSERVATIONS**

No blocking gap found. Every DoD condition in `CLAUDE.md` §5 holds against
the actual commit, independently re-run rather than taken on any report's
say-so. One clerical inaccuracy in the audit dispatch's own prompt (not a
phase defect) is noted below as an observation, plus one process
observation about the ad-hoc §6.B reviewer dispatch not being
independently re-creatable by this audit.

## 1. Code implemented + plan's verification step passes

Re-ran directly, matching the retro's claims exactly:

- `python scripts/check_knowledge_placement.py --strict` (full real
  `src/codecompass/` + `decisions/` corpus): **10 findings, all
  `decision-citation-superseded` (informational), exit 0.** Confirmed
  `source_resolution.py:7` → `decisions/0019`/`0061` is one of them.
- `python scripts/check_knowledge_placement.py --files
  src/codecompass/source_resolution.py src/codecompass/oracle.py
  src/codecompass/staleness.py`: **exactly 1 finding** —
  `decision-citation-superseded` on `source_resolution.py:7`
  (`decisions/0019`, attributed by `decisions/0061`'s title section) —
  zero findings on `oracle.py`/`staleness.py`. Exit 0.
- `pytest tests/test_check_knowledge_placement.py -v`: **32 passed.**

Read `scripts/check_knowledge_placement.py` in full
(`/home/cormac/projects/codecompass/scripts/check_knowledge_placement.py`).
Confirmed it implements exactly:
- `decision-citation-exists` (blocking)
- `decision-citation-superseded` (informational)
- `knowledge-placement-unparseable-source-file` (always-blocking parse
  diagnostic, `line=1`, triggered on `SyntaxError`/`OSError`/
  `tokenize.TokenError`/`IndentationError`)

No `decision-citation-status-mismatch` and no
`docstring-contradicted-by-oracle-result` anywhere in the script. The
module docstring (lines 65-74) and `TestDecisionCitationStatusMismatchIsDeferred`
in the test file explicitly assert the first deferred rule name never
appears in a real run. This matches the plan's final (fourth-amendment)
design exactly.

## 2. Real dogfood — independently re-verified (the most important check)

`git diff 9afabcc..86fb495 -- src/codecompass/source_resolution.py`
shows the *entire* change is the module docstring (lines 1-13); nothing
else in the file was touched. Full diff text:

```
-"""Upstream repository resolution and shallow clone, for grounded-
-description generation. See decisions/0019 and decisions/0021.
+"""Upstream repository resolution and shallow clone, building the
+`vendor/<name>/src/` snapshot `sync_vendor` clones unconditionally for
+every vendor (decisions/0033), independent of any enrichment decision —
+see decisions/0021 for the fail-loud-on-unresolvable-repository
+semantics this module implements. (Originally introduced to feed
+promote-time, `Depth.FULL`-gated grounded-description generation,
+decisions/0019 — that mechanism, `grounded_description.py`, was retired
+and deleted, decisions/0035; cloning was retained and generalised to
+run for every vendor, decisions/0033, independent of `promote`, which
+decisions/0033 itself also removed.)
```

Independently judged the new docstring's accuracy by reading, myself,
the artifacts it cites rather than trusting the retro's narrative:

- `src/codecompass/sync.py`'s own module docstring and `sync_vendor`'s
  own docstring independently confirm: cloning via
  `codecompass.source_resolution` happens unconditionally for every
  vendor "since Phase 13 (`decisions/0033`)" and `resolve_and_clone`
  implements `decisions/0021`'s fail-loud semantics. This matches
  `source_resolution.py`'s rewritten docstring claim exactly.
- `decisions/0019` ("Grounded description replaces gap analysis for
  FULL-depth generation") — read in full: its own Decision section
  introduces `grounded_description.py`, gated on `promote`/`Depth.FULL`.
- `decisions/0035` — read in full: explicitly retires and deletes
  `grounded_description.py`.
- `decisions/0061` ("`decisions/0019` is superseded by `decisions/0035`")
  — read in full: formally records the supersession, confirms `0019`'s
  own `## Status` field has stood `Accepted`, unedited, describing a
  mechanism that "has not existed since Phase 16."
- `decisions/0033` — read in full: retires `promote`, generalises
  cloning to every vendor unconditionally, and explicitly states
  "`decisions/0021`'s substantive rule is carried forward unchanged,
  only re-triggered from Phase A instead of `promote`."

Conclusion: the new docstring is **substantively accurate, not
cosmetic** — it correctly leads with the real current purpose/caller,
cites `decisions/0021`/`0033` for current-state justification, and
explicitly reframes `decisions/0019` as historical ("Originally
introduced to feed... that mechanism... was retired and deleted"). This
is a genuine fix of a real placement defect (category-8 content that
had been masquerading as category-2 justification), not a reword that
leaves the problem in place.

`git diff 9afabcc..86fb495 -- src/codecompass/oracle.py
src/codecompass/staleness.py` is empty — confirmed both negative
controls are untouched throughout the implementation commit and all
four planning-amendment commits.

## 3. Plan's own test coverage (§11)

Read `tests/test_check_knowledge_placement.py` in full. Confirmed
present, not merely counted from the retro:
- Extraction-boundary tests: ordinary string literal never a citation;
  real docstring/comment citation detection; multiline-docstring exact
  line provenance (with the load-bearing blank-line-after-`"""`
  fixture shape that specifically distinguishes `clean=False` from the
  buggy `clean=True` default).
- Fail-closed minimal-content edge cases: bare `"decisions/"` substring
  with no digits (`test_bare_decisions_substring_with_no_digits_is_never_a_match`)
  and the depth-vs-scope companion
  (`test_wellformed_but_nonexistent_number_is_caught`, `decisions/0000`).
- Negative controls named in the task: `decisions/0027`'s "is **not**
  superseded" (`test_0027_negation_is_a_critical_negative_control`) and
  `decisions/0058`'s `## Context`-only mention
  (`test_0058_context_section_mention_is_never_scanned`) — both present,
  both read against the real repository files (`REPO_ROOT`), not
  constructed copies.
- Two parse-failure tests: `SyntaxError`
  (`test_syntax_error_produces_blocking_diagnostic_and_does_not_crash`)
  and unreadable file via `monkeypatch`
  (`test_unreadable_file_produces_blocking_diagnostic_not_a_crash`), plus
  a third confirming one broken file doesn't block the rest of the run.
- Determinism (byte-identical repeated runs; sorted by `(file, line,
  rule)`).
- Real-baseline pinning that deliberately does **not** assert zero
  findings against the real repo (so the dogfood's own finding is pinned
  by name, never suppressed).

All 32 tests independently re-run and pass (§1 above).

## 4. Docs/architecture/decisions + drift audit

- `docs/concepts/knowledge-placement-policy.md` and
  `docs/workflows/knowledge-placement-review.md`: both read in full,
  both substantive (82 and 125 lines respectively) — the eight-category
  table, the three enforcement classes, the full ad-hoc-reviewer brief
  with method/finding-shape/write-boundary/hard-rule/dispatch
  sections. Not stubs.
- `decisions/0094-knowledge-placement-policy-and-review.md`: read in
  full. `## Status` is `Accepted`. Records exactly the five tradeoffs
  the plan's amendment rounds surfaced (ad-hoc reviewer design; two
  deferred checks; no-synthetic-substitute dogfood rule; `ast`/`tokenize`
  extraction with four-section supersession scope). Append-only
  consistent — no prior ADR's original text was touched (confirmed via
  `git diff 9afabcc..86fb495 -- decisions/` showing only the new
  `0094` file added).
- Independently re-checked the one actionable finding the prior
  `docs-reconstructor` pass flagged as fixed: `git show 86fb495 --
  docs/development/contributing.md docs/development/testing.md`
  confirms a new `scripts/check_knowledge_placement.py` bullet was
  added to `contributing.md` and `tests/test_check_knowledge_placement.py`
  was added to `testing.md`'s module list — both present in the actual
  diff, not merely claimed.
- `docs/decisions.md` now has a `0094` row (confirmed via diff and via
  `grep`). The pre-existing `0089`-`0093` gap is real but independently
  confirmed to predate this phase: `git log --oneline -- decisions/0089*
  decisions/0090* decisions/0091* decisions/0092* decisions/0093*` shows
  all five were introduced by Phase 83/84 commits (`1e5c00c`, `2436e39`,
  `0b4f321`, `45a3ca8`, `23f6826`, `7ba8950`), all well before Phase 86's
  own planning commits — not something this commit introduced or needed
  to fix.

## 5. Changelog

`CHANGELOG.md`'s `[Unreleased]` section has one substantive,
Phase-86-specific entry (read directly) — not batched with any other
phase, matches the commit's own content.

## 6. `planning/CONTEXT.md` — confirmed still pending, as expected

`git show 86fb495 --stat` lists the 13 files this commit actually
touches: `planning/CONTEXT.md` and `planning/ROADMAP.md` are **not**
among them. `planning/ROADMAP.md` row 86 still reads `planned` (not
`done`) at HEAD. This is exactly the one remaining step the lead's plan
defers to the terminal `roadmap-context-curator` reconciliation commit
per `CLAUDE.md` §5's own named exemption — confirmed pending, not
forgotten, not already (prematurely) done.

## 7. Phase retro

`planning/retros/phase-86-knowledge-placement-code-quality-review.md`
read in full: Goal, Delivered vs. planned (including the one disclosed
CLI-shape deviation — no `--ledgerkit-root`, reasoned explicitly), the
full real-dogfood evidence chain, Lessons learnt (three genuine
implementation-time bugs the planning rounds didn't catch, each with
a stated process implication), and Process-improvement feedback (the
stdlib-exception-name-verification practice that became `L-116`). Not a
stub; substantively matches every TEMPLATE.md section this phase's
scope requires.

## 8. Candidate learnings triaged

`planning/learnings/inbox.md` diff (`git show 86fb495 --
planning/learnings/inbox.md`) is **pure addition** — no `-` lines at
all beyond the diff header, confirming `L-114`/`L-107` (Phase 85) were
not touched. New `L-116` entry present: `status: candidate`, full
`TEMPLATE.md`-conformant fields (origin, date, project_revision,
observation, evidence, classification, status, recurrence), with real,
independently-checkable evidence (the exact file:line, the exact
`AttributeError` that would occur, confirmed this session via `python3
-c "import tokenize; tokenize.TokenizeError"` → `AttributeError`, `import
tokenize; tokenize.TokenError` → succeeds). Correctly **not yet**
triaged by `knowledge-curator` (status is `candidate`, not
`promoted`/`retained`/`discard`/`merge`) — matches the stated next step.

## 9. Protected-file / scope-discipline checks

- `git diff b434b9d..86fb495 -- CLAUDE.md`: empty. Not touched.
- `git diff b434b9d..86fb495 -- planning/knowledge/`: empty. No
  canonical knowledge record written by this phase.
- `.claude/agents/`: `git diff b434b9d..86fb495 -- .claude/agents/` is
  empty; `ls .claude/agents/ | wc -l` = 13, unchanged. No 14th standing
  agent file created — confirms the ad-hoc-dispatch design was actually
  followed, not merely described.
- `git show 86fb495 --name-only` (the commit's own full file list):
  `CHANGELOG.md`, `decisions/0094-*.md`, `docs/concepts/knowledge-
  placement-policy.md`, `docs/decisions.md`, `docs/development/
  contributing.md`, `docs/development/testing.md`, `docs/workflows/
  knowledge-placement-review.md`, `planning/learnings/inbox.md`,
  `planning/phase-86-*.md`, `planning/retros/phase-86-*.md`, `scripts/
  check_knowledge_placement.py`, `src/codecompass/source_resolution.py`,
  `tests/test_check_knowledge_placement.py`. None of Phase 85's files
  (`scripts/check_self_knowledge_quality.py`,
  `tests/test_check_self_knowledge_quality.py`) appear. Nothing from
  Phases 87-90's own named deliverables (documentation compiler, MCP,
  incremental reconciliation, comparative trials) appears. Matches the
  plan's own §10 deliverables table exactly — no scope creep.

## Full-suite / lint / pre-existing-validator re-run (independent)

- `pytest -q`: **1198 passed, 2 skipped** in 341.59s — matches exactly.
- `ruff check scripts/check_knowledge_placement.py
  tests/test_check_knowledge_placement.py
  src/codecompass/source_resolution.py`: **All checks passed!**
- `python scripts/check_contracts.py --strict --ledgerkit-root
  ~/projects/ledgerkit`: exit 0, 7 findings, all informational (6
  `contract-result-integrity-mismatch` historical-superseded-by-fresh-
  PASS instances, 1 `contract-check-gap` for the known, pre-existing
  `overlapping-account-patterns-no-double-count` gap) — matches the
  already-documented Phase 83/88 baseline, no new finding.
- `python scripts/check_knowledge_base.py --strict`: exit 0, all
  findings informational `knowledge-base-snapshot-current-divergence`
  entries — matches the pre-existing, already-documented baseline.
- `python scripts/check_self_knowledge_quality.py --strict
  --ledgerkit-root ~/projects/ledgerkit`: exit 1, **35 findings, 26
  blocking, 9 informational** — counted directly: 9 blocking
  `missing-evidence` (`REQ-DOCORIGIN-001/002/003`,
  `REQ-HSAPI-001`-`006`) + 2 blocking `stale-test-citation`
  (`EV-BFS-002`/`003`) + 15 blocking `unverified-required-scope`
  (`CL-BFS-001`-`005` × 3 scopes each) = 26 blocking; 5
  `missing_contract` + 1 `contradiction` + 1 `needs-review` + 1
  `possible-evidence-overlap` + 1 `missing-evidence` (on the
  `status: proposed` `CL-HLEDGERDEPTH-002`) = 9 informational. This
  **exactly matches** the Phase 85 corrective pass's own documented
  baseline (26 blocking / 9 informational, `L-114`/`L-107`) — no
  regression, nothing suppressed, nothing newly excluded.

**Observation (non-blocking, not a phase defect)**: the audit dispatch
prompt's own phrasing ("5 `self-knowledge-quality-unverified-required-
scope` findings, same as always") undercounts — the real, current,
already-documented baseline is **15** `unverified-required-scope`
findings (not 5), within a 26-blocking/9-informational total that
matches exactly. This is an inaccuracy in the audit instructions
themselves, not a drift introduced by Phase 86 — independently
confirmed the actual blocking/informational split is byte-for-byte the
documented Phase 85 baseline either way.

## Other notes

- `git status` / `git diff --quiet`: clean before and after this audit;
  no scratch comparison materialized onto a live tracked path at any
  point in this audit (all comparisons used `git diff`/`git show`
  read-only, never a checkout-over-working-tree).
- This audit could not itself re-run the ad-hoc §6.B reviewer dispatch
  (a one-time, now-historical subagent invocation) to re-verify its own
  internal reasoning; it instead independently re-derived the same
  conclusion from the primary sources (`sync.py`, `decisions/0019/0021/
  0033/0035/0061`) myself, per the task's own instruction, and found the
  retro's account consistent with what those sources actually say. This
  is as close to independent re-verification of that one step as a
  single read-only audit pass can get without re-dispatching a fresh
  subagent at comparable cost; noted for completeness, not as a gap.

## Conclusion

Every DoD condition in `CLAUDE.md` §5 holds against commit `86fb495`:
code implemented exactly per the plan's final (fourth-amendment) design
(2 mechanical checks + 1 diagnostic, 2 checks correctly deferred);
plan's verification step passes; real dogfood is genuine, independently
confirmed accurate, and re-verified post-fix; test coverage matches
§11's own requirements including fail-closed/negative-control cases;
docs/decisions updated and consistent, append-only; changelog entry
present and scoped to this phase only; `CONTEXT.md`/`ROADMAP.md`
correctly still pending (not forgotten, not prematurely flipped);
retro substantive; one new candidate learning filed, correctly
untriaged; no protected-file drift; no scope creep. Full suite (1198
passed, 2 skipped), ruff, and all three pre-existing strict validators
re-run clean against the documented baseline.

**PASS WITH NON-BLOCKING OBSERVATIONS.**

---

## Corrective-pass re-audit (2026-11-03)

**Auditor**: `release-phase-auditor` (independent dispatch, second,
narrower audit)
**Audited range**: `483d24f..HEAD` — four commits applied on top of the
original terminal-reconciliation commit: `e796b08` (fix), `06598bf`
(L-116 disposition), `4e016e8` (plan/retro §14 addendum), `0fe4326`
(persisted drift audit + 2 doc fixes).
**Scope**: this is an audit of the narrow corrective-closeout pass
itself, not a re-audit of the original Phase 86 implementation (which
retains its own `PASS WITH NON-BLOCKING OBSERVATIONS` verdict above,
unmodified).

### Verdict: **PASS WITH NON-BLOCKING OBSERVATIONS**

Every claim made about the corrective pass was independently reproduced
against the actual commits — not taken on the summary's or the
commit messages' own say-so. No blocking gap found. Two small,
non-blocking inaccuracies are noted in the commit messages/plan
addendum's own prose (not in the code or tests), and one pre-existing,
correctly-untouched ADR staleness item is confirmed as an observation
only, per instruction.

### 1. Both fixed defects independently reproduced against pre-fix code

Confirmed `issubclass(UnicodeDecodeError, OSError)` is `False` directly.
Built three isolated fixtures and ran `483d24f`'s script
(`git show e796b08~1:scripts/check_knowledge_placement.py`) against
each via `importlib`, then the current (`e796b08`) script against the
same fixtures:

- **Invalid-UTF-8 source file**: pre-fix `run_all` raised an uncaught
  `UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff...` — a
  genuine crash, not a diagnostic. Post-fix: 2 clean findings
  (`knowledge-placement-unparseable-source-file` /
  `knowledge-placement-unreadable-decision-file`, both `strict=True`),
  no crash.
- **Unreadable (`PermissionError`, an `OSError` subclass) ADR that would
  itself have supersession-attributed a real citation**: pre-fix
  `run_all` **succeeded silently with 0 findings** — the citation to the
  would-be-superseded ADR read as clean, exactly the misleadingly-clean
  result the commit message describes. Post-fix: 1 blocking
  `knowledge-placement-unreadable-decision-file` finding, correctly
  naming the unreadable file.
- **Escaped-`\n`-inside-one-physical-line docstring overcount**: built a
  module docstring containing a literal `\n` escape before a citation
  on physical line 1. Called `_docstring_citations` directly on both
  versions: pre-fix reported `line=2` (wrong — an escaped-newline-caused
  overcount); post-fix reported `line=1` (correct, matching the real
  physical source line).

All three defects are real, correctly characterized by the commit
message, and genuinely fixed. (Scratch fixtures and `chmod 000`/removed
files were confined to the session scratchpad directory, never the live
repository tree; no live file was ever overwritten by this
reproduction step.)

### 2. Revised tests and real-corpus validator independently re-run

- `pytest tests/test_check_knowledge_placement.py -v`: **40 passed**,
  exactly as claimed. Test count confirmed via direct diff: 32 test
  functions at `483d24f`, 40 at `e796b08` (`git show <rev>:... | grep
  -oP 'def \Ktest_\w+'`).
- `python scripts/check_knowledge_placement.py --strict` run twice
  consecutively: **10 informational findings, exit 0, byte-identical**
  (`diff` of the two captured outputs is empty).

### 3. Historical dogfood record confirmed unaltered

`git diff 483d24f..HEAD -- planning/retros/phase-86-knowledge-placement-
code-quality-review.md` is a **pure addition** — the diff contains only
a new `## Corrective pass (2026-11-03)` section appended at the end; no
line within the pre-existing "Real dogfood" section (confirmed present,
unchanged, at its original location) was touched. The real finding
(`source_resolution.py:7` citing `decisions/0019`, attributed by
`decisions/0061`'s title section) is present in both of the two
consecutive real-corpus runs above, confirmed even though
`test_real_corpus_run_produces_only_well_formed_informational_findings`
(the renamed test — confirmed via diff that
`test_source_resolution_dogfood_finding_is_present` no longer exists and
this is its replacement) deliberately no longer pins it by name; read
the new test's own body and docstring directly, confirming it asserts
general well-formedness (`strict is False`, `file`/`line` populated,
`"decisions/" in message`) over whatever `decision-citation-superseded`
findings the real corpus produces, not a specific one.

### 4. Original real finding and both negative controls re-confirmed

`python scripts/check_knowledge_placement.py --strict --files
src/codecompass/source_resolution.py src/codecompass/oracle.py
src/codecompass/staleness.py`: **exactly 1 finding**
(`decision-citation-superseded` on `source_resolution.py:7`), **zero**
on `oracle.py`/`staleness.py`. Matches exactly.

### 5. Persisted drift-audit artifact verified

`planning/retros/_drift-audit-phase-86.md` read in full: exists, is
substantive (43 lines — scope, method, verdict, two findings each with
its own fix note, a "checked, no drift found" list, an out-of-scope ADR
cross-check, a scope note, and a provenance note explaining why this is
a fresh dispatch rather than a reconstruction). Not a stub. Both
findings' fixes independently verified via `git diff 0fe4326~1 0fe4326
-- docs/development/contributing.md
docs/concepts/knowledge-placement-policy.md`: `contributing.md` gained
the second diagnostic (`knowledge-placement-unreadable-decision-file`)
and the widened exception list; `knowledge-placement-policy.md`'s "How
this is enforced today" section was rewritten from "an always-blocking
parse-failure diagnostic" (singular) to naming both diagnostics'
distinct scopes. Both diffs match the artifact's own description of
what it found and what was fixed, exactly.

### 6. No protected-file drift; `inbox.md` change scoped to L-116 only

`git diff 483d24f..HEAD -- CLAUDE.md` is empty. `git diff
483d24f..HEAD -- planning/learnings/inbox.md` shows exactly two
hunks, both inside `L-116`'s own entry (the last `### L-NNN` heading in
the file, confirmed via `grep -n "^### L-" ... | tail -5`): the
`status: candidate` → `status: retained` line change, and an appended
"Corrective-closeout note" explaining the disposition. No other
`L-NNN` entry's text was touched.

### 7. No scope creep into Phase 85 or Phases 87-90

`git show --stat --format="" <commit>` for each of the four commits:

- `e796b08`: `scripts/check_knowledge_placement.py`,
  `tests/test_check_knowledge_placement.py`
- `06598bf`: `planning/learnings/inbox.md`
- `4e016e8`: the Phase 86 plan file and retro file only
- `0fe4326`: `docs/concepts/knowledge-placement-policy.md`,
  `docs/development/contributing.md`,
  `planning/retros/_drift-audit-phase-86.md`

`scripts/check_self_knowledge_quality.py` and
`tests/test_check_self_knowledge_quality.py` (Phase 85) appear in none
of the four commits. No plan files exist yet for Phases 87-90
(confirmed via `ls planning/phase-8[7-9]*.md planning/phase-90*.md` →
no such file), so there is nothing named for those future phases that
could have been touched; independently confirmed moot, not merely
assumed absent.

### 8. Full suite, lint, and all pre-existing strict validators re-run

- `pytest -q`: **1206 passed, 2 skipped** in 315.29s — exactly the
  claimed figure, +8 over the documented Phase 85 baseline (1198),
  matching the net +8 new test functions in `tests/
  test_check_knowledge_placement.py`. No regression.
- `ruff check scripts/check_knowledge_placement.py
  tests/test_check_knowledge_placement.py`: **All checks passed!**
- `python scripts/check_contracts.py --strict --ledgerkit-root
  ~/projects/ledgerkit`: exit 0, 7 informational findings — matches the
  pre-existing, already-documented baseline.
- `python scripts/check_knowledge_base.py --strict`: exit 0, all
  findings informational `knowledge-base-snapshot-current-divergence`
  entries — matches the pre-existing baseline.
- `python scripts/check_self_knowledge_quality.py --strict
  --ledgerkit-root ~/projects/ledgerkit`: exit 1, **35 findings — counted
  directly: 26 blocking, 9 informational** — exactly the documented
  Phase 85 baseline. Nothing suppressed, nothing newly excluded from the
  test suite's own assumptions to force this match.
- `python scripts/check_user_docs.py --strict`: **no findings**, exit 0.

### 9. `decisions/0094` staleness — observation only, correctly left untouched

`decisions/0094-knowledge-placement-policy-and-review.md` line 82 still
reads "docstring (`ast.get_docstring(node, clean=False)` — the raw
text..." — now factually stale against the corrective pass's
raw-source-slice rewrite (the current code never calls
`ast.get_docstring` at all). This is correctly **not** a defect: `
decisions/*.md` ADRs are append-only historical records
(`CLAUDE.md` §2), and the drift-audit artifact (§5 above) already
independently identified and logged this exact same item as an
"out-of-scope cross-check, noted but not counted toward the verdict."
Confirmed left untouched, as it should be; flagged here again only per
this audit's own explicit instruction to note it, not to require a fix.

### 10. `ROADMAP.md`/`CONTEXT.md`/`CHANGELOG.md` confirmed not yet touched

`git diff 483d24f..HEAD -- planning/ROADMAP.md`,
`-- planning/CONTEXT.md`, and `-- CHANGELOG.md` are all **empty**. The
terminal reconciliation and changelog entry for this corrective pass
have correctly **not** landed yet — consistent with this audit running
before that final commit, as expected. (If this audit had found any of
these three touched already, that would have been flagged as premature;
it did not.)

### Non-blocking observations

1. **Minor test-count inaccuracy in the commit message and the plan's
   own §14 addendum.** Both state "7 new regression tests (40 total...
   from 32)". Direct diff of test function names between `483d24f` and
   `e796b08` shows **8** new `test_` functions were added (one existing
   test was renamed, net zero from the rename itself), which is what
   actually accounts for 32 → 40. The plan's own §14 addendum even
   states "net +8 matches the new dedicated tests" in the same
   paragraph that says "7 new" two sentences earlier — an internal,
   if minor, inconsistency. Does not affect correctness: all 40 tests
   independently collected and passed, and the 8 new tests were
   independently confirmed substantive (§11 below).
2. Confirmed by direct pre-fix re-run (not merely accepting the commit
   message's claim) that 6 of the 8 new tests fail against the pre-fix
   script — the two that pass unchanged either way
   (`test_informational_severity_of_superseded_findings_is_unaffected`,
   `test_no_unreadable_decision_file_findings_on_real_corpus`) are
   defensive/baseline-shaped tests that were never expected to
   distinguish pre-fix from post-fix behavior on their own, not evidence
   of a weak regression test. (Comparison performed by temporarily
   overwriting the live, tracked `scripts/check_knowledge_placement.py`
   with `e796b08~1`'s content via `git show ... >` to run the test
   suite against it, then restoring: `git checkout --
   scripts/check_knowledge_placement.py`, confirmed via `git diff
   --quiet -- scripts/check_knowledge_placement.py` and a clean `git
   status --short` immediately after, and a full re-run of
   `tests/test_check_knowledge_placement.py` — all 40 passing again —
   as an extra sanity check that the restore was genuine.)

### Conclusion

Every claim made about this corrective pass holds against the actual
commits, independently reproduced rather than trusted: both genuine
pre-fix defects (uncaught `UnicodeDecodeError` on source read; silent
`continue` on an unreadable/`OSError`-raising ADR masking a real
supersession attribution) were reproduced against `483d24f`'s own code
and confirmed fixed at `e796b08`; the line-provenance bug was reproduced
and confirmed fixed by direct function-level comparison; the revised
40-test suite and real-corpus `--strict` run (determinism, exact
finding, two negative controls) were independently re-run and match;
the historical "Real dogfood" retro section is a pure, unaltered
addition; the drift-audit artifact exists, is substantive, and both its
findings are verifiably fixed in `0fe4326`; `CLAUDE.md` is untouched and
`inbox.md`'s only change is scoped to `L-116`; no file belonging to
Phase 85 or to any (currently nonexistent) Phase 87-90 plan was touched;
the full suite (1206 passed/2 skipped), ruff, and all four strict
validators (`check_contracts.py`, `check_knowledge_base.py`,
`check_self_knowledge_quality.py`, `check_user_docs.py`) re-run clean
against their documented baselines with nothing suppressed;
`decisions/0094`'s own now-stale point 5 is correctly left untouched per
the append-only ADR rule; and `ROADMAP.md`/`CONTEXT.md`/`CHANGELOG.md`
are confirmed not yet touched, correctly deferred to the terminal
reconciliation commit this audit is meant to authorize.

**PASS WITH NON-BLOCKING OBSERVATIONS.**

---

## Second corrective-pass re-audit (2026-11-04)

**Auditor**: `release-phase-auditor` (independent dispatch)
**Audited commit**: `648be97` (HEAD at dispatch time, `main`, working
tree clean before and after this audit)
**Scope**: the full corrective scope end-to-end — not only the second
corrective pass's own two commits (`305d3e1`, `648be97`), re-verified
against the final state produced by all of `e796b08` through `648be97`.

### Why this audit exists

A follow-up review found two problems with the prior closeout recorded
immediately above (the "Corrective-pass re-audit (2026-11-03)"
section): (1) a genuine, previously-missed byte-vs-character-offset
defect in `_docstring_citations()`, plus a silent-empty-`--files`
usability gap, both fixed in `305d3e1`; and (2) that prior re-audit's
own point 7 commit list (`e796b08`, `06598bf`, `4e016e8`, `0fe4326`)
omits `e682994` and `2ac5dd4`, even though both chronologically landed
*before* the audit itself was recorded in `64dba3c` (`e682994`
22:57:55, `2ac5dd4` 22:58:24, `64dba3c` 22:59:59) — meaning that audit's
own verification work was anchored to an earlier tree state than the
one it was ultimately committed against. Per `CLAUDE.md` §5, any commit
after an audit pass that touches audited scope voids that pass; the
recorded verdict was therefore never actually supported with respect to
the state marked `done`. This audit re-verifies everything, fresh,
against the true final state.

### 1. Byte-offset bug independently reproduced against pre-fix code, confirmed fixed

Extracted `scripts/check_knowledge_placement.py` as it existed at
`8b915ac` via `git show 8b915ac:scripts/check_knowledge_placement.py >
<scratch path>` (never written over the live tracked file for this
step). Running `_docstring_citations()` directly against
`'def 非常非常(): """decisions/9999"""\n'` returned **`[]`** — the
citation is silently lost entirely, not merely misreported, confirming
the defect exactly as described. Running the same input through the
current, post-fix function returns `[(1, '9999')]` — correct.

A second, separate reproduction was done directly at the real tracked
path: temporarily overwrote the live `scripts/check_knowledge_placement.py`
with `8b915ac`'s content (`git show 8b915ac:... >
scripts/check_knowledge_placement.py`), ran the test suite, then
restored and confirmed clean:

```
git checkout -- scripts/check_knowledge_placement.py
git diff --quiet && echo "RESTORED - clean"   # => RESTORED - clean
git status --short                            # => (empty)
```

Against that pre-fix state, `pytest tests/test_check_knowledge_placement.py
-k "test_non_ascii_identifier_preceding_inline_docstring_is_not_lost or
test_multiple_citations_on_multibyte_prefixed_line_are_all_found or
test_explicit_empty_files_selection_is_rejected_not_a_silent_clean_pass
or test_omitted_files_flag_still_defaults_to_whole_tree_scan"` gave:

- `test_non_ascii_identifier_preceding_inline_docstring_is_not_lost`: **FAILED** (`assert 0 == 1`)
- `test_multiple_citations_on_multibyte_prefixed_line_are_all_found`: **FAILED** (`assert 0 == 1`)
- `test_explicit_empty_files_selection_is_rejected_not_a_silent_clean_pass`: **FAILED** (`DID NOT RAISE SystemExit`)
- `test_omitted_files_flag_still_defaults_to_whole_tree_scan`: **PASSED**

The fourth test correctly passes pre-fix too — it is a non-regression
sanity check (confirming the *unaffected* default-scan path still
works), not one of the three tests meant to distinguish pre/post-fix
behavior; its pass against pre-fix code is expected, not a sign of a
weak regression test. All four pass against the current, post-fix code
(confirmed in the full 44-test run below). Working tree restored and
verified clean before proceeding.

### 2. CLI `--files` fix confirmed directly

```
$ python scripts/check_knowledge_placement.py --files
usage: check_knowledge_placement.py [-h] [--strict] [--files FILES [FILES ...]]
check_knowledge_placement.py: error: argument --files: expected at least one argument
exit: 2

$ python scripts/check_knowledge_placement.py   # --files omitted entirely
exit: 0
```

### 3. Full suite, targeted suite, lint — all re-run independently

- `pytest tests/test_check_knowledge_placement.py -q`: **44 passed**.
- `pytest -q` (full suite): **1210 passed, 2 skipped** in 318.63s —
  exactly the expected figure (+4 over the first corrective pass's
  1206, matching the net +4 new test functions).
- `ruff check scripts/check_knowledge_placement.py
  tests/test_check_knowledge_placement.py`: **All checks passed!**

### 4. Real-corpus `--strict` run — determinism and no latent real defect

Two consecutive runs of `python scripts/check_knowledge_placement.py
--strict` produced **byte-identical** output (`diff` empty): **10
finding(s)**, all `decision-citation-superseded` (informational), exit
0.

To confirm the byte-offset fix found no previously-masked real defect
in this project's own source tree, the same `--strict` run was
performed against `8b915ac`'s pre-fix script (again via a temporary
`git show`-overwrite-then-`git checkout --`-restore cycle, confirmed
clean with `git diff --quiet` afterward) and diffed against the
post-fix run's output: **identical**, exit 0 both times. No real file
under `src/codecompass/` was affected by the byte-offset bug.

### 5. Negative control / dogfood files re-confirmed

```
$ python scripts/check_knowledge_placement.py --strict --files \
    src/codecompass/source_resolution.py src/codecompass/oracle.py src/codecompass/staleness.py
check_knowledge_placement: 1 finding(s)
  [decision-citation-superseded] (info) src/codecompass/source_resolution.py:7: cites decisions/0019, ...
```

Exactly 1 informational finding, on `source_resolution.py` only;
`oracle.py` and `staleness.py` remain clean negative controls.

### 6. Pre-existing strict validators — all baselines re-counted directly

- `python scripts/check_self_knowledge_quality.py --strict
  --ledgerkit-root ~/projects/ledgerkit`: exit 1, **35 findings — counted
  directly: 26 blocking, 9 informational** — exactly the documented
  Phase 85 baseline.
- `python scripts/check_contracts.py --strict --ledgerkit-root
  ~/projects/ledgerkit`: exit 0, **7 informational findings** — matches
  the pre-existing, already-documented baseline (6
  `contract-result-integrity-mismatch`, 1 `contract-check-gap`, all
  informational).
- `python scripts/check_knowledge_base.py --strict`: exit 0, **24
  findings, all informational** (`knowledge-base-snapshot-current-divergence`)
  — matches the pre-existing baseline shape.
- `python scripts/check_user_docs.py --strict`: **no findings**, exit 0.

### 7. Audit-sequencing gap — confirmed real, and now closed

Re-reading the "Corrective-pass re-audit (2026-11-03)" section's own
point 7 confirms the gap exactly as described: its commit list names
only `e796b08`, `06598bf`, `4e016e8`, `0fe4326` — omitting `e682994`
(22:57:55) and `2ac5dd4` (22:58:24), both of which chronologically
landed *before* that audit was itself recorded in `64dba3c` (22:59:59).
That audit's own verification work was therefore anchored to the tree
state as of `0fe4326`, not the state it was ultimately committed
against — a genuine instance of the gap `CLAUDE.md` §5 is meant to
prevent.

This audit's own verification work (all of sections 1-6 above) was
performed with `HEAD` at `648be97` — after `e682994`, `2ac5dd4`,
`305d3e1`, and `648be97` had all already landed. This is therefore the
first audit of this phase whose own checks genuinely reflect the true
final state, closing the gap.

### 8. Protected-file / scope-creep checks

- `git diff 483d24f..HEAD -- CLAUDE.md`: **empty**. No `CLAUDE.md`
  change anywhere across either corrective pass.
- No `planning/phase-8[7-9]*.md` or `planning/phase-9[0-2]*.md` files
  exist yet — nothing for either corrective pass to have touched.
- `decisions/0094-knowledge-placement-policy-and-review.md`:
  `git diff 86fb495..HEAD -- decisions/0094-knowledge-placement-policy-and-review.md`
  is **empty** — byte-identical to its state at its own creation
  commit (`86fb495`), confirming the append-only ADR rule held through
  both corrective passes. (Its point 5's now-stale `ast.get_docstring`
  reference, already correctly logged as an out-of-scope observation
  in the first re-audit, remains correctly untouched.)

### 9. `L-116` disposition unaffected by the second corrective pass

`git diff 8b915ac..HEAD -- planning/learnings/inbox.md`: **empty**.
`status: retained` (confirmed directly, not `candidate`, not
`promoted`) is unchanged by `305d3e1`/`648be97`.

### 10. `_drift-audit-phase-86.md` — only the documented "+8" correction changed

`git diff 8b915ac..HEAD -- planning/retros/_drift-audit-phase-86.md`
shows exactly one changed line: the stale "+7 tests" reference in the
`docs/development/testing.md` entry corrected to "+8", with an
explanatory parenthetical pointing at `e682994` and this audit file's
own corrective-pass re-audit section. The file (42 lines, five
sections) remains substantive, not a stub. No other line changed.

### 11. Required follow-ups — not yet done, confirmed needed

The following are **not** covered by `CLAUDE.md` §5's narrow
terminal-reconciliation exemption (that exemption names only
`planning/ROADMAP.md`'s phase row, `planning/CONTEXT.md`'s
current-state section, and the plan file's own Status *line* — nothing
else) and are currently genuinely silent about the second corrective
pass:

1. **`planning/ROADMAP.md`'s Phase 86 row** documents only the first
   corrective pass (32→40 tests) and the first re-audit. It does not
   yet mention the byte-offset fix, the `--files` usage-error fix, the
   44-test total, the audit-sequencing-gap finding, or this second
   re-audit. **Needs updating** — confirmed by `grep` showing no
   mention of `305d3e1`/`648be97`/"byte-offset"/"44" in the relevant row.
2. **`planning/CONTEXT.md`** still states (line 893) "No further Phase
   86 corrective work is open" — now stale; a second corrective pass
   did in fact occur after that sentence was written. **Needs
   updating.**
3. **The phase plan file's own Status line** (line 3) and its §14
   section document only the first corrective pass. Unlike items 1-2,
   §14's *body content* is not one of the three narrowly-exempted
   targets (only the Status *line* itself is) — a §14 addendum
   describing the second corrective pass's two findings should be
   added, following the precedent the first corrective pass itself set
   (`4e016e8`, landed as its own commit before that pass's audit ran).
   **Needs updating**, and arguably before the terminal reconciliation
   commit, not as part of it.
4. **The retro file**
   (`planning/retros/phase-86-knowledge-placement-code-quality-review.md`)
   has no addendum for the second corrective pass — its own
   "Corrective pass (2026-11-03)" section covers only the first.
   Per the pattern the first pass itself established, a dated addendum
   (findings, root cause, lessons learnt) is expected for the second
   pass too. **Needs adding.**
5. **No candidate learning has been filed for the second corrective
   pass's own defects.** A plausible candidate: `ast`'s
   `col_offset`/`end_col_offset` being UTF-8 *byte* offsets rather than
   character offsets is a genuine, non-obvious Python stdlib gotcha for
   any code slicing source text using those offsets directly — a
   different specific shape from `L-116` (an invalid stdlib *exception
   class name* not verified by direct execution) but the same general
   family (a stdlib API's real semantics not verified by direct
   execution against a representative, non-trivial fixture before
   shipping). `planning/learnings/inbox.md` has no `L-117` (or any)
   entry for this. **Needs knowledge-curator triage** before this
   phase's learnings condition (`CLAUDE.md` §5) can be considered met
   for the second corrective pass.

None of items 1-5 reflect any doubt about the correctness of the
shipped fix, its tests, or any re-run result above — every mechanical
check in sections 1-10 passed cleanly and was independently reproduced,
not taken on trust. They are documentation/triage completion gaps, open
at the moment this audit was dispatched, that must close before the
phase can be considered fully reconciled.

### Verdict: **PASS WITH NON-BLOCKING OBSERVATIONS**

The second corrective pass's own newly-written code (`305d3e1`) was
scrutinized at the same depth as original implementation, per this
role's own standing instruction that a corrective pass's fix code is
never granted a presumption of correctness: the byte-offset defect was
independently reproduced against the real pre-fix source (not merely
accepted from the commit message), the fix was independently confirmed
correct by direct function-level testing, all four new regression tests
were independently confirmed to fail pre-fix / pass post-fix (with the
one exception correctly identified as a non-regression sanity check),
and the full suite, lint, and every pre-existing strict validator baseline
were independently re-run and matched with nothing suppressed. The
audit-sequencing gap that motivated this dispatch is independently
confirmed as having genuinely existed, and is independently confirmed
closed by this very audit, which is the first to verify the state after
all of `e682994`, `2ac5dd4`, `305d3e1`, and `648be97` had landed. No
protected-file or scope-creep violation was found.

**Required before this phase can be marked fully reconciled** (listed
in full in section 11 above, not repeated here): (1) `ROADMAP.md`'s
Phase 86 row, (2) `CONTEXT.md`'s current-state section, (3) the plan
file's own Status line *and* a new §14 addendum, (4) a retro addendum
for the second corrective pass, and (5) knowledge-curator triage of a
candidate learning about `ast`'s byte-offset semantics. Items (1)-(2)
and the Status-line part of (3) are the lead's own terminal-
reconciliation commit per `CLAUDE.md` §5's narrow exemption; the §14
body addendum, the retro addendum, and the learning triage are not
covered by that exemption and should land in their own commit(s)
first, mirroring how the first corrective pass handled the same
sequence (`4e016e8` before `64dba3c`/`8b915ac`).
