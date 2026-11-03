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
