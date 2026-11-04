# Independent completion audit — Phase 87, Stage 87A hardening pass

- **Audited commit:** `57dab8f` ("fix(phase-87): harden Stage 87A
  publication path -- three integration defects corrected"), confirmed
  via `git log --oneline -1` to be the real current `HEAD` at audit
  time, not a stale description.
- **Scope:** Stage 87A's publication-path hardening pass (plan's own
  §N; retro: `planning/retros/phase-87-stage-87a-hardening.md`).
  Phase 87 overall remains `not done`; this audit covers only the
  hardening pass, per the dispatch.
- **Auditor role:** `release-phase-auditor`, read-only.

## Verdict

**FAIL.**

The three corrected integration defects (§N.A/§N.B/§N.C) are real,
correctly implemented, and substantially well-tested — this part of
the pass is solid. But the commit under audit itself contains two
independently-verifiable inaccuracies in the governing DoD documents
it introduces, plus a material test-coverage gap relative to what the
pass claims about its own verification. Per this role's hard rules, a
real FAIL is not softened to PASS WITH OBSERVATIONS.

## What was re-verified and found correct

1. **`doc_compiler.resolve_publication_target`** (`src/codecompass/doc_compiler.py:469-514`)
   — read directly. Rejects an absolute path, a `..` component, any
   target outside `README.md`/`docs/**/*.md`, and resolves both root
   and candidate via `Path.resolve()` before an `is_relative_to` check
   (never a string-prefix check) — matches §N.B's claim exactly.
   Wired into `check_doc_schema.py::_check_document_path` (schema-
   validation time) and `cli.py::docs_publish` (publish time) — both
   call sites confirmed by direct `grep`/read.
2. **`hydrate_records`/`hash_evidence`/`find_schema_section`**
   (`doc_compiler.py:218-245`, `447-455`) — read directly; match their
   docstring claims and are the single shared definitions used by both
   compile-time and publish-time code paths (no independent duplicate
   computation found).
3. **`cli.py`'s `docs record-review` and rewritten `docs publish`**
   (`cli.py:2049-2264`) — read directly. `record-review` persists a
   review bound to `draft_sha256`/`evidence_sha256`/`schema_section_sha256`
   copied from the pending manifest; `publish` re-derives live schema-
   section and evidence hashes, requires both review files to exist,
   parse, carry every required key, match the pending identity triple
   exactly, and carry the expected passing verdict — matches §N.A's
   claim exactly. Confirmed `section_id` is validated against the live
   schema (`find_schema_section`) before any path resolution.
4. **`scripts/compile_doc_section.py::compose_section`**
   (lines 242-306) — read directly. The system prompt is built from
   `verified_packet` (constructed from `packet_path.read_text()`/
   `manifest_path.read_text()`, i.e. the on-disk, hash-verified bytes),
   never from the `packet` argument held in memory. The staging
   directory is created and removed inside a `try`/`finally`, on every
   path. Matches §N.C's claim exactly.
5. **Regression tests, spot-checked directly (not merely assumed real):**
   - `test_docs_publish_rejects_a_forged_review_with_wrong_draft_hash`
     (`tests/test_cli.py:2852`) — writes a review record with a
     deliberately wrong `draft_sha256` claiming a passing verdict;
     asserts rejection. Real, exercises the claimed scenario.
   - `test_docs_publish_rejects_when_knowledge_revision_changed_since_review`
     (`tests/test_cli.py:2903`) — records both passing reviews, then
     mutates the underlying knowledge record; asserts publish is
     rejected because live `evidence_sha256` no longer matches. Real.
   - `test_docs_publish_rejects_a_symlink_escape` (`tests/test_cli.py:3008`)
     — symlinks `docs/` to an external directory, asserts publish is
     rejected and nothing is written outside. Real; exercises the
     resolved-path (not string-prefix) check specifically.
   - `test_compose_section_builds_broker_prompt_from_verified_bytes_not_memory`
     (`tests/test_compile_doc_section.py:267`) — monkeypatches
     `write_section_packet` to mutate the in-memory packet immediately
     *after* its verified bytes are written to disk, then asserts the
     mutation never reaches the broker's prompt while the original
     content does. This is a genuinely strong test: it positively
     proves the prompt is sourced from the verified read, not merely
     that the hash check ran. Real, non-trivial, not vacuous.
   None of the spot-checked tests are skipped, xfail-marked, or
   assertion-free.
6. **Full test suite, re-run independently:** `.venv/bin/python -m
   pytest -q` → `1290 passed, 2 skipped in 324.47s` — matches the
   claimed count exactly.
7. **`ruff check` on every touched file, re-run independently:**
   `src/codecompass/cli.py`, `src/codecompass/doc_compiler.py`,
   `scripts/compile_doc_section.py`, `scripts/check_doc_schema.py`,
   `tests/test_cli.py`, `tests/test_compile_doc_section.py` → 6
   findings total, all `E501` line-length, all outside the touched
   functions (`cli.py` lines 1764/1782/1787/1797/1804 — the pre-existing
   `knowledge traverse`/`knowledge gaps` commands; `test_cli.py` line
   1460 — an unrelated pre-existing assertion comment). Matches the
   claimed "5-6 known findings in cli.py and one in test_cli.py, all
   outside the touched functions" exactly.
8. **Validators re-run independently, all exit 0 / unchanged:**
   `check_doc_schema.py --strict` (no findings), `check_knowledge_placement.py
   --strict` (informational only), `check_knowledge_base.py --strict`
   (informational only), `check_contracts.py --strict` (7 informational
   findings, pre-existing), `check_user_docs.py --strict` (no findings),
   `check_self_knowledge_quality.py --strict` — counted exactly **35**
   `self-knowledge-quality-*` findings, matching the retro's claimed
   "Phase 85 baseline (35 informational/known findings) ... unchanged."
9. **Protected-file drift:** `git show 57dab8f --stat -- CLAUDE.md
   decisions/` produces no output — neither changed. Confirmed no drift.
10. **README's "Understanding Digests" section / `codecompass-grounded-by`
    marker:** present and untouched (`git show 57dab8f --stat` lists no
    `README.md` change at all).
11. **`planning/retros/phase-87-pending-review/readme-md/
    vendor-digest-concept.json`:** confirmed untouched by this commit
    (`git show 57dab8f --stat` lists no change to this path; its own
    git history shows only the original demonstration commit `a9667b5`
    ever wrote it). The architecture doc's own new prose explicitly and
    correctly describes it as pre-dating the hardening pass and never
    retroactively rewritten.
12. **Candidate learning `L-120`:** filed to `planning/learnings/inbox.md`
    with a full `knowledge-curator` curation note (independent
    reproduction of both cited pieces of evidence by direct reading);
    draft promotion recorded in `planning/v1-redefinition/
    proposed-governance-changes.md` §P, correctly marked "proposed, not
    yet presented to the user" and awaiting `CLAUDE.md` §0 approval —
    this is the correct, not-yet-approved state, not a defect.
    Confirmed both the inbox entry and §P landed in the audited commit
    itself (`git show 57dab8f -- planning/v1-redefinition/
    proposed-governance-changes.md` shows the new §P content; `git log
    --oneline` confirms no later, separate commit introduced it) —
    satisfying the requirement that learning triage land in the same
    commit as the audited state, not a later step.
13. **Working tree:** clean throughout and after this audit's own
    verification runs (`git status --porcelain` empty).

## Findings that drive the FAIL verdict

### Finding 1 — `planning/CONTEXT.md` and `planning/ROADMAP.md` assert this pass's own independent re-audit as an already-completed, dated fact, when no such audit had actually run

Both files, **committed in `57dab8f` itself**, state:

- `planning/CONTEXT.md:55-56`: *"**Stage 87A hardening pass — closed,
  independently re-audited (2026-11-04)**, plan's own §N."*
- `planning/ROADMAP.md:190` (Phase 87 row): *"...then hardened against
  three publication-path integration defects found by a follow-up
  review (...) and **re-audited PASS WITH NON-BLOCKING OBSERVATIONS
  (2026-11-04)**..."*

Both assert, in the past tense, that an independent re-audit of this
hardening pass has already happened and passed. It had not: no
persisted audit report for the hardening pass exists anywhere in the
repository. `find`/`ls planning/retros/` turns up only
`_audit-phase-87-stage-87a.md` (dated before the hardening pass,
auditing commit `61182a8`, i.e. the *pre-hardening* re-audit) and
`_drift-audit-phase-87-stage-87a.md` (same, pre-hardening). There is
no `_audit-phase-87-stage-87a-hardening.md` or equivalent predating
this dispatch — this dispatch is the first one. The plan's own §N.D
text, written in the very same commit, correctly uses future/pending
phrasing: *"this hardening pass's own final `release-phase-auditor`
dispatch (**see this pass's own retro/audit record once written**)"*
— i.e. the plan's own author knew, at commit time, that no such record
existed yet. `CONTEXT.md`/`ROADMAP.md` contradict the plan's own §N.D
within the same commit by asserting the opposite as settled fact.

This is exactly the failure mode `CLAUDE.md` §5 and this role exist to
prevent: an audit's conclusion recorded before an independent audit
ran, rather than after. It directly fails audit task item 5 ("confirm
... `planning/CONTEXT.md`, `planning/ROADMAP.md`'s Phase 87 row ...
accurately reflect this commit's real state, not an earlier or
aspirational one") — this is not an earlier state, it is a
not-yet-true, aspirational one asserted as already true.

**Fix required:** correct `planning/CONTEXT.md`'s Stage-87A-hardening
paragraph and `planning/ROADMAP.md`'s Phase 87 row so that "re-audited"
claims are made only once a real, persisted `release-phase-auditor`
report exists for the hardening pass and its actual verdict is known —
not pre-written in anticipation. Given this audit's own verdict is
FAIL, both documents currently overstate the state twice over (claiming
an audit occurred, and claiming it passed, neither of which is true as
of `57dab8f`).

### Finding 2 — the claimed "21 new regression tests" overstates the actual, measurable test-count change by roughly a third, repeated across four governing documents

`CHANGELOG.md`, `planning/CONTEXT.md`, the retro
(`planning/retros/phase-87-stage-87a-hardening.md`), and the commit
message itself all state "21 new regression tests" (13 of them
confirmed failing pre-fix). Measured directly against the real diff:

- `tests/test_cli.py`: 104 → 116 test functions (+12 net); 13
  `+def test_` lines added, 1 removed
  (`test_docs_publish_refuses_without_both_verdicts_passing`, the old
  manually-typed-verdict flow's own test, deleted because that flow no
  longer exists).
- `tests/test_compile_doc_section.py`: 15 → 18 test functions (+3 net);
  4 `+def test_` lines added, 1 removed/renamed
  (`test_compose_section_returns_raw_output_on_success` →
  `test_compose_section_returns_raw_output_and_manifest_on_success`).
- Net new test functions across both files: **15** (matches the full
  suite's own measured delta: 1275 → 1290 passed, exactly +15).
  Gross added test-function definitions: **17**, of which one is a
  rename/modification of a pre-existing test rather than a genuinely
  new scenario, giving **16** genuinely new test functions by any
  reasonable count — not 21.
- Cross-checked against the plan's own §N "Tests" bullets (which do
  not themselves state a total): manually enumerating every scenario
  named under §N.A (9, once "absent review (both missing, one
  missing)" is correctly counted as the 2 separate tests it actually
  is), §N.B (4, excluding the "unresolved section_id" scenario already
  counted under §N.A), and §N.C (3) totals exactly **16** — matching
  the actual code, not the claimed 21.

No `21 * 1 = 1275 + 21 = 1296` reconciliation is possible against the
claimed, and independently reconfirmed, `1290` final passing count —
the arithmetic in the governing documents does not hold.

**Fix required:** correct the test-count claim in `CHANGELOG.md`,
`planning/CONTEXT.md`, and the retro to the actual, reconcilable
figure (16 genuinely new test functions / 15 net test functions after
accounting for the one rename / +15 net passing tests, 1275→1290).

### Finding 3 — §N.B's claimed "enforced at both schema-validation time (`check_doc_schema.py`) and publish time" has zero regression-test coverage for the schema-validation-time half

`scripts/check_doc_schema.py::_check_document_path` (lines 217-230)
wires the new `doc-schema-unsafe-document-path` blocking finding into
`run_all`. This project has an established, consistently-followed
convention of unit-testing each `check_doc_schema.py` rule
individually in `tests/test_check_doc_schema.py` (14 existing tests,
one per rule, e.g. `test_duplicate_document_path_across_schemas_is_blocking`
immediately adjacent in spirit to this new rule). The diff for `57dab8f`
does not touch `tests/test_check_doc_schema.py` or
`tests/test_doc_compiler.py` at all (confirmed via `git show 57dab8f
--stat`), and a direct grep for `_check_document_path`,
`doc-schema-unsafe-document-path`, or `resolve_publication_target`
across the entire `tests/` tree returns nothing. The only coverage of
`resolve_publication_target` is indirect, through `docs publish`'s CLI
integration tests (`test_docs_publish_rejects_a_traversal_document_path`
etc.) — genuinely good tests, but they exercise only the publish-time
call site, never the schema-validation-time call site the retro itself
calls out as a design strength ("`check_doc_schema.py` catching an
unsafe `document` field at authoring time is strictly better than only
catching it when a publish is actually attempted").

I independently verified the schema-validation-time mechanism *does*
work correctly by direct invocation (constructing a schema with
`document: "../outside.md"` and calling `check_doc_schema.run_all`
directly — it correctly returns a blocking
`doc-schema-unsafe-document-path` finding) — so this is a real
test-coverage gap in an otherwise-working mechanism, not a second
hidden functional defect. But nothing in the committed suite would
catch a future regression here (e.g. `_check_document_path` silently
dropped from `run_all`'s own finding list), despite this exact
scenario being the established per-rule-test pattern this file already
follows for every one of its other 14 rules.

**Fix required:** add at least one regression test in
`tests/test_check_doc_schema.py` exercising `_check_document_path`/the
`doc-schema-unsafe-document-path` finding directly (e.g. a schema with
an absolute or traversal `document` field, asserting the blocking
finding is produced), matching this file's own established convention.

## Non-blocking observations (would not by themselves change the verdict)

- Stray `§2.A`/`§2.B`/`§2.C` citation-label comments remain in
  `tests/test_cli.py` (lines ~2717, 2803, 2949) and
  `tests/test_compile_doc_section.py` (lines ~215, 241, 268) — the
  commit's own stated citation-label fix (`§2.x` → `§N.x`) was applied
  to the current-truth docs (`docs/reference/cli.md`, the architecture
  doc) but not to these test-file comments. Cosmetic only — test
  comments are not "current-truth docs" in `docs-reconstructor`'s
  audited scope — but worth folding into the same correction pass for
  internal consistency.
- The retro's own "Agents used" line lists `release-phase-auditor` in
  the past tense without a citation to a persisted report for this
  pass — consistent with Finding 1, and should be corrected alongside
  it once a real audit report exists.

## What must be fixed before re-audit

1. Correct `planning/CONTEXT.md`'s Stage-87A-hardening paragraph and
   `planning/ROADMAP.md`'s Phase 87 row: do not assert "independently
   re-audited" / "re-audited PASS WITH NON-BLOCKING OBSERVATIONS" for
   the hardening pass until a real, persisted `release-phase-auditor`
   report exists and its actual verdict (this one, or a later one once
   re-fixed) is known. Reference this report's actual file path and
   verdict once corrected.
2. Correct the "21 new regression tests" claim in `CHANGELOG.md`,
   `planning/CONTEXT.md`, and `planning/retros/phase-87-stage-87a-hardening.md`
   to the actual, reconcilable figure (16 genuinely new test functions;
   full-suite delta 1275 → 1290, i.e. +15).
3. Add a direct regression test for `check_doc_schema.py`'s new
   `_check_document_path`/`doc-schema-unsafe-document-path` rule in
   `tests/test_check_doc_schema.py`, matching this file's own
   established per-rule-test convention.
4. (Non-blocking, fold in if convenient) Update the remaining
   `§2.A`/`§2.B`/`§2.C` comment labels in `tests/test_cli.py` and
   `tests/test_compile_doc_section.py` to `§N.A`/`§N.B`/`§N.C`.

Once 1-3 are fixed and committed, a fresh `release-phase-auditor`
dispatch must run against the new final commit (this pass's own
voided-scope rule applies: any commit touching audited scope after
this report requires a new audit before the hardening pass can be
considered closed) — not reuse this report's verdict by
cross-reference.

---

# Re-audit — Phase 87, Stage 87A hardening fix round

- **Audited commit:** `a656e0c` ("fix(phase-87): correct Stage 87A
  hardening pass's own three process defects -- FAIL fix round"),
  confirmed via `git log --oneline -1` to be the real current `HEAD`
  at audit time, not a stale description.
- **Scope:** the three process-defect fixes this commit claims to make
  to the prior FAIL (above), re-verified independently against the
  real current state — not by reusing the first audit's verdict by
  cross-reference.
- **Auditor role:** `release-phase-auditor`, read-only. This is a
  fresh, independent pass (a new dispatch, no shared memory with the
  first).

## Verdict

**PASS WITH NON-BLOCKING OBSERVATIONS.**

All three FAIL-driving findings from the first audit are genuinely
fixed, independently re-verified against the real current state
(including by directly reproducing the pre-fix/post-fix test behaviour
myself, not merely re-reading the claim). Two small, non-blocking
wording/clarity issues remain, neither of which asserts an event that
hasn't happened or misstates a material fact.

## What was re-verified and found correct

1. **`planning/CONTEXT.md` / `planning/ROADMAP.md` no longer claim a
   completed re-audit.** Read both files as they exist now. `CONTEXT.md`
   (lines 11-13, 55-96): "Stage 87A implemented and hardened, hardening
   fix-round complete, fresh independent re-audit of the fix pending"
   / "**A fresh independent audit of this corrected state is the next
   step before Stage 87A's hardening is considered closed** — not yet
   run as of this entry." `ROADMAP.md`'s Phase 87 row: "...a fresh
   independent re-audit of the corrected state is pending as of
   2026-11-04". Both correctly describe the fix as done and this
   re-audit as the pending next step, not an already-settled fact.
   `git diff 57dab8f a656e0c -- planning/CONTEXT.md planning/ROADMAP.md`
   read in full — no new instance of the "claims an event before it
   happens" defect anywhere in either diff. `CHANGELOG.md`'s diff
   likewise reads correctly in tense ("a fresh independent audit of
   this exact revision is the next step before Stage 87A's hardening
   can be considered closed").
2. **Test count reconciled, independently re-measured, not merely
   re-read:**
   - `tests/test_cli.py`: 103 (at `61182a8`) -> 115 (now) def-count
     delta = +12; direct diff shows 13 new `def test_` lines added, 1
     removed (`test_docs_publish_refuses_without_both_verdicts_passing`,
     superseded by the hash-bound-review redesign).
   - `tests/test_compile_doc_section.py`: 15 -> 18, delta +3.
   - `tests/test_check_doc_schema.py`: 14 -> 18, delta +4.
   - Total net new across the three files: **19**, matching
     `CHANGELOG.md`/`CONTEXT.md`/the retro's own claimed "19 new
     regression tests" and "15 -> 19" narrative exactly.
   - Reproduced the "13 confirmed failing pre-fix" claim directly: used
     a disposable `git worktree` checked out at `61182a8` (pre-hardening
     source), copied the current `tests/test_cli.py` into it, and ran
     the 13 newly-written `docs_publish`/`docs_record_review` test
     functions with `PYTHONPATH` pointed at the worktree's own `src/`+
     `scripts/` — all 13 fail against the pre-hardening source (11 via
     `AttributeError`/missing command, 2 via assertion), and all 13
     pass against the current `a656e0c` tree. Worktree removed after
     use; `git status --short` and `git diff --quiet` on the main
     checkout confirmed clean before and after (no live tracked file
     was ever overwritten — the sandbox itself declined a direct
     overwrite attempt on a tracked path, so a worktree was used
     instead, which achieves the same comparison without the
     restore-afterward risk).
3. **`tests/test_check_doc_schema.py` now has direct, real tests for
   `doc-schema-unsafe-document-path`** — read each of the 4 new test
   bodies directly, not merely grepped for the rule name:
   `test_traversal_document_path_is_blocking` (`document: "../outside.md"`),
   `test_absolute_document_path_is_blocking` (`document: "/etc/evil.md"`),
   `test_document_path_outside_approved_targets_is_blocking`
   (`document: "CONTRIBUTING.md"`), and
   `test_legitimate_readme_document_path_produces_no_path_finding`
   (`document: "README.md"`, positive control). Cross-checked each
   against `doc_compiler.resolve_publication_target`'s own real logic
   (`src/codecompass/doc_compiler.py:469-514`): absolute-path check,
   `..`-in-`parts` check, then an allow-list check against
   `_ALLOWED_ROOT_FILES = ("README.md",)` / `_ALLOWED_DOC_ROOT_DIRS =
   ("docs",)` — each of the 4 tests exercises a genuinely distinct
   branch (traversal, absolute, out-of-allowlist via a real root file
   that isn't `README.md`, and the one legitimate root file). Ran
   `pytest tests/test_check_doc_schema.py -v`: 18/18 pass.
4. **`ruff check` on every touched file, re-run independently:**
   `src/codecompass/cli.py`, `src/codecompass/doc_compiler.py`,
   `scripts/check_doc_schema.py`, `scripts/compile_doc_section.py`,
   `tests/test_cli.py`, `tests/test_compile_doc_section.py`,
   `tests/test_check_doc_schema.py` -> exactly 6 findings, all `E501`,
   all in `src/codecompass/cli.py` (the pre-existing `knowledge
   traverse`/`knowledge gaps` commands) and `tests/test_cli.py` line
   1460 (an unrelated pre-existing comment). Independently confirmed
   these same 6 findings exist identically against the `61182a8`
   pre-hardening baseline (ran `ruff check` against a `git show
   61182a8:...` snapshot of both files) — none are new, none are in
   touched functions.
5. **Full test suite, re-run independently twice:** `1294 passed, 2
   skipped` both times (326.62s and 323.68s) — matches the claimed
   count exactly.
6. **The three actual publication-path fixes, re-confirmed still
   present and unchanged:** `git diff 57dab8f a656e0c -- src/codecompass/cli.py
   src/codecompass/doc_compiler.py scripts/compile_doc_section.py
   scripts/check_doc_schema.py` is empty — byte-identical to what the
   first audit already independently re-confirmed sound by direct
   read (`resolve_publication_target`'s absolute/traversal/allow-list/
   resolved-path logic; `docs record-review`/`docs publish`'s
   hash-bound review validation; `compose_section`'s verified-bytes
   sourcing and always-removed staging directory). Re-read
   `resolve_publication_target` and `_check_document_path` directly
   myself as part of verifying item 3 above — matches the first
   audit's description exactly.
7. **No `CLAUDE.md`/`decisions/*`/`README.md` drift:** `git show
   a656e0c --stat -- CLAUDE.md decisions/ README.md
   planning/retros/phase-87-pending-review/` produces no output — none
   touched by this commit.
8. **`planning/retros/phase-87-pending-review/readme-md/
   vendor-digest-concept.json` still untouched:** `git log --oneline
   -- <path>` shows only the original demonstration commit `a9667b5`;
   no commit since (including `a656e0c`) has touched it.
9. **`L-120` filed and triaged in the same commit lineage as the
   implementation, not a later separate step:** confirmed via `git
   show 57dab8f -- planning/learnings/inbox.md` (the entry and its
   curation note land in the same commit as the three publication-path
   fixes); `a656e0c` does not touch `planning/learnings/inbox.md` or
   `planning/v1-redefinition/proposed-governance-changes.md` at all
   (correct — nothing about L-120's own disposition changed in the fix
   round). `L-120`'s `status:` field reads `retained`, matching
   `CONTEXT.md`'s claim.
10. **Changed-file list matches exactly what three process-defect
    fixes need, no scope creep:** `CHANGELOG.md`, `planning/CONTEXT.md`,
    `planning/ROADMAP.md`, the new `_audit-phase-87-stage-87a-hardening.md`
    (first FAIL report, persisted here for the first time — not a
    retroactive rewrite, this is its original write), the retro, and
    the three test files. No `src/` or `scripts/` production-code
    change (correct — none of the three findings were implementation
    bugs).
11. **Stray `§2.x` citation labels corrected to `§N.x`:** `grep -n
    "§2\.[ABC]\b" tests/test_cli.py tests/test_compile_doc_section.py`
    returns nothing; `§N.A`/`§N.B`/`§N.C` labels present at the
    expected lines. The non-blocking observation from the first audit
    was folded in as promised.
12. **Validators and the Phase 85 self-knowledge-quality baseline,
    all re-run independently:** `check_doc_schema.py --strict` (no
    findings); `check_knowledge_placement.py --strict` (10
    informational, exit 0); `check_knowledge_base.py --strict` (10
    informational, exit 0); `check_contracts.py --strict` (7
    informational, exit 0, matching the pre-existing baseline exactly);
    `check_user_docs.py --strict` (no findings, exit 0);
    `check_self_knowledge_quality.py --strict` (35 findings — 26
    blocking, 9 informational, exit 1 as expected — matching the
    documented, unchanged Phase 85 baseline exactly).
13. **Working tree:** clean before, during (worktree-isolated, never
    touching the live tracked path), and after this audit
    (`git status --short` empty; `git worktree list` shows no leftover
    worktree from this audit).

## Non-blocking observations (would not by themselves change the verdict)

- **`CHANGELOG.md`'s own new sentence is confusing on first read, though
  not actually false.** It says "19 new regression tests
  (`tests/test_cli.py` +12, ...; **13** of the `tests/test_cli.py`
  additions confirmed failing..." — juxtaposing a net delta ("+12")
  with a raw-addition count ("13 of") for the same file in the same
  breath invites a reader to conclude 13 can't be a subset of 12. It
  is not actually an error: `tests/test_cli.py` has 13 freshly-written
  `def test_` functions in this diff, one of which replaces (nets
  against) one deleted pre-hardening test, giving a net delta of +12
  while all 13 raw new functions are the ones that were confirmed
  failing pre-fix (independently reproduced above). Worth rewording
  (e.g. "13 newly-written `test_cli.py` functions" instead of "13 of
  the `test_cli.py` additions") so the net/gross distinction isn't
  left for a reader to reconstruct themselves.
- **The retro's "Lessons learnt" section points to "Where we're going"
  below for `L-120`'s detail, but "Where we're going" doesn't mention
  `L-120` at all** — it only discusses Stage 87B's plan being drafted
  next. A dangling cross-reference, introduced by this same commit's
  rewrite of that section; harmless since `L-120`'s actual detail lives
  correctly in `planning/learnings/inbox.md` and is correctly
  summarized elsewhere in this same retro ("Candidate learnings
  filed"), but the specific "see ... below" pointer resolves to nothing
  relevant.
- **The retro's "Where we're going" section does not itself restate
  that the fresh independent audit (this one) is the immediate next
  step** before Stage 87B's plan is drafted — it is accurate (Stage
  87B is genuinely next after this audit), but `CONTEXT.md`/
  `ROADMAP.md`/`CHANGELOG.md` all state the immediate next step more
  precisely than the retro's own "Where we're going" does. Not a
  factual error, just a less complete trajectory statement in one of
  the four governing documents relative to the other three.

## What must be fixed before the phase can be marked done

Nothing blocking. The three optional wording clarifications above may
be folded in at the lead's discretion but do not require a further
audit cycle on their own. Per the `release-phase-auditor` role's own
voided-scope rule, any further commit touching this audited scope
(including a purely cosmetic fix to the above) would require a fresh
audit before this hardening pass's state can be relied upon again —
the lead should weigh that cost against the cosmetic benefit before
deciding whether to make that commit at all.

Phase 87 overall remains `not done` (Stage 87B/87C unauthorised and
unstarted) — this verdict closes only the hardening-pass re-audit
`CONTEXT.md`/`ROADMAP.md` name as pending, not Phase 87 as a whole.
