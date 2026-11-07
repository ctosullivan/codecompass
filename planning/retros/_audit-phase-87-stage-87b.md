# Independent completion audit — Phase 87, Stage 87B

- **Auditor:** `release-phase-auditor` (independent dispatch)
- **Date:** 2026-11-07
- **Scope audited:** commit `0f6a26894beab77e097ba726468d8622ebc262a9`
  ("feat(phase-87): implement Stage 87B — two-document governance,
  execution harness, concurrency guard") **plus** the real, uncommitted
  working-tree changes present at audit time (doc-drift fixes to
  `docs/reference/cli.md`, `docs/architecture/components.md`,
  `docs/architecture/documentation-compilation-pipeline.md`,
  `docs/architecture/overview.md`; `CHANGELOG.md`; `planning/learnings/
  inbox.md`/`promoted.md`; the new retro
  `planning/retros/phase-87-stage-87b-knowledge-change-demonstration.md`).
  Governing plan: `planning/phase-87-documentation-schema-knowledge-
  compiled-documentation.md` §O, as amended through §O.J, reviewed READY
  WITH NON-BLOCKING OBSERVATIONS at §R (2026-11-07).

## Verdict: **FAIL**

One concrete, specifically-named regression test the plan's own
verification section (§O.D.3) calls "required" — surviving three
independent planning-review rounds, the most recent of which (§R) ran
the same day as implementation and re-confirmed the concurrency-guard
design was sound and necessary — was never written. Everything else
audited (code correctness, documentation-drift fixes, changelog,
retro, learnings triage, protected-file integrity, scope boundaries,
the full regression suite, and the real sandboxed execution) held up
to direct, independent re-verification. This is reported as a FAIL,
not softened, per this role's own standing instruction not to round a
real gap up to "PASS WITH OBSERVATIONS."

## What was re-run and independently re-verified (passed)

1. **Full regression suite, run directly**: `.venv/bin/python -m
   pytest -q` → `1334 passed, 2 skipped in 388.95s` — matches the
   commit message's own claim exactly. The 2 skips are the
   pre-existing npm/cargo-toolchain-dependent skips (confirmed by
   `grep` across `tests/`, unrelated to this stage).
2. **The real, sandboxed execution harness genuinely runs, not
   skipped**: `tests/test_execute_doc_example.py` → `14 passed` with no
   skips (confirmed `unshare`/`pivot_root`/`git`/`bash` present on this
   host and the one-time fixture cache
   `/tmp/codecompass-doc-example-cache/{wheels,git-mirrors,venv}`
   already populated with timestamps matching the implementation
   session). This confirms the four real scenarios (`pip install`
   offline, bare `codecompass` against the new `no-candidates-project`
   fixture, `codecompass --budget 0` against `toy-project`, `codecompass
   query vendors`) actually executed inside the real namespace sandbox,
   not merely as mocked unit tests.
3. **`check_doc_schema.py --strict`** against the real, now-two-schema
   repository → `no findings`.
4. **`ruff check .`** → 176 findings, **all** pre-existing and
   unrelated to this diff (confirmed by running the identical check
   against the pre-implementation commit `4a9cdb9` via a disposable
   `git worktree`, which reports the identical 176; none touch any file
   this stage's diff changed — all are `E501`/`F841`/`I001`/`F401` in
   `knowledge_api.py`/`assess_change_impact.py`/
   `check_self_knowledge_quality.py` and their tests). **Non-blocking
   observation**: the commit message's own claim ("Ruff clean (6
   pre-existing, unrelated findings only)") materially understates the
   real count (176, not 6) — the *conclusion* ("pre-existing, unrelated,
   not a regression") is correct, but the implementer's own self-report
   is numerically wrong by a wide margin and should not be trusted at
   face value in a future closeout.
5. **The real, pre-existing `intermediate-knowledge-layer` fixture
   manifest** (`planning/knowledge/codecompass-domain/reconciliation/
   20261104T081241Z-doc.toml`) still exists, exactly one file, matching
   the real-repository idempotency regression test's own assertion.
6. **CLAUDE.md untouched** — last change to it predates this work
   entirely (`git log -1 -- CLAUDE.md` → an unrelated prior commit).
   No `decisions/*` file touched by `0f6a268` or the uncommitted diff.
7. **Changed-file list matches the plan's own scope exactly** — the
   full set of files touched (committed + uncommitted) is: schema/doc
   files (`docs/getting-started.md`,
   `docs/getting-started.md.schema.yaml`), the four doc-drift fixes,
   `CHANGELOG.md`, the retro, the two learnings files,
   `examples/no-candidates-project/pyproject.toml`,
   `scripts/check_doc_schema.py`, `scripts/execute_doc_example.py`
   (new), `src/codecompass/{cli,doc_compiler,knowledge_intermediate}.py`,
   and five `tests/test_*.py` files. No scope creep into anything
   Stage 87C's own separately-planned scope would touch (no
   deterministic CLI-reference generator, no matched-baseline rubric —
   confirmed by grep for both terms, finding nothing outside the plan
   file itself).
8. **Core implementation pieces read in full and confirmed correct**:
   - `doc_compiler.compute_schema_slug` (moved from `cli.py`'s private
     `_schema_slug`, now shared with `check_doc_schema.py`'s new
     `_check_cross_document_region_id_uniqueness`).
   - `doc_compiler.decide_publish_safety` — the five-case
     proceed/refuse decision table matches §O.D.3's spec exactly,
     including the corrected `"new"`-case content-hash comparison.
   - `knowledge_intermediate.advance_region_baseline_after_publish` and
     `write_doc_candidates_to_manifests`'s idempotency guard
     (`_existing_pending_doc_region_edit_keys`) — both match spec, both
     have real-repository regression tests
     (`test_real_repository_doc_candidate_manifest_write_is_idempotent`)
     that pass against the actual `planning/knowledge/` tree.
   - `cli.py`'s `_doc_publish_lock` / `docs_publish` / `docs_maintain`
     (project-wide `**/*.schema.yaml` discovery, mirroring
     `check_doc_schema.py`'s own `_discover_schema_files` exactly —
     confirmed identical glob pattern and confirmed it finds exactly
     the two real schema files on disk today).
   - `scripts/execute_doc_example.py` — allow-list design, negative
     controls (`test_unauthorised_command_is_rejected_before_the_
     sandbox_is_entered`, `test_paid_api_triggering_commands_are_never_
     in_the_allow_list`), and the `--classify` exit-code/pattern logic
     all match §O.C.
   - `## After the first run`'s factual-verification test
     (`test_after_the_first_run_claims_match_the_real_repository`)
     checks every claimed artefact (vendor `CLAUDE.md`, the root
     routing table and its five columns, the Skill, the slash command,
     a genuinely-openable `context-graph.db`) against the real
     repository, exactly as §O.B specifies.
   - The self-contradicting "## First run" prose in
     `docs/getting-started.md` is fixed exactly as described (steps
     1-4 unconditional, step 5 conditionally interactive/billable).
9. **The real knowledge-change demonstration (retro) is internally
   consistent and its cited evidence is real**: `CL-CTXT-005.yaml`'s
   real, current, production statement says nothing about the
   clone-failure fallback (confirmed by direct read); `sync.py:128-133`
   is exactly the docstring paragraph describing the fallback;
   `tests/test_sync.py:275-298` is exactly
   `test_sync_vendor_source_resolution_failure_falls_back_to_local_
   snapshot`, a real, passing test exercising it. The amendment was
   genuinely never merged into production knowledge (confirmed: the
   live `CL-CTXT-005.yaml` has no `EV-CTXT-021` and no fallback
   language) — the worktree-discard claim holds up.
10. **Learnings triage genuinely happened**: `L-121` (the four
    namespace-sandbox construction footguns) is marked `promoted` in
    `inbox.md`, has a `promoted.md` line, and its promoted text is
    present verbatim in the uncommitted `docs/architecture/overview.md`
    diff's new "Known footguns" entry — independently confirmed
    line-for-line against `scripts/execute_doc_example.py`'s own real
    code (device-node touches, real-absolute-path venv mount, mirror
    data bind-mount, `env -i` setup-step ordering). `L-122` (the
    uncaptured broker usage/cost figures) is honestly left `candidate`,
    explicitly handed off to `roadmap-context-curator` for a backlog
    line in `ROADMAP.md` — not yet landed, consistent with the task's
    own framing and with CLAUDE.md §5's exemption for the terminal
    reconciliation step.
11. **`CONTEXT.md`/`ROADMAP.md` correctly NOT yet updated** — both
    still describe Stage 87B as planned/not-authorised, consistent with
    CLAUDE.md §5's explicit carve-out that this reconciliation happens
    *after* this audit, not before.
12. **CHANGELOG.md entry** (uncommitted) accurately and completely
    describes all seven numbered deliverables, names the real
    docs-reconstructor findings fixed, and correctly states Phase 87
    overall remains not done.

## Blocking finding

**§O.D.3's own explicit, six-item "Regression tests required" list is
only four-sixths covered; the most safety-critical item is entirely
untested:**

> "two concurrent `docs publish` invocations against the same project
> serialise correctly through the lock (one succeeds, the other either
> waits and then re-evaluates, or times out cleanly — never corrupts
> the document or double-writes)"

No test anywhere in the diff (`tests/test_cli.py`,
`tests/test_doc_compiler.py`, `tests/test_knowledge_intermediate.py`)
exercises two genuinely concurrent `docs publish` invocations against
the same project. Confirmed by direct search (grep for
`Popen|ProcessPoolExecutor|fork\(\)|threading|racing` across every new
test file: zero matches outside one unrelated comment). The three
lock-related tests that do exist
(`test_doc_publish_lock_times_out_cleanly_when_already_held`,
`test_doc_publish_lock_is_released_after_use`,
`test_doc_publish_lock_is_released_after_an_exception_inside_it`) only
exercise the `_doc_publish_lock` context manager **in isolation** —
they pre-seed or inspect the lock file directly from a single thread,
never launch a second, genuinely concurrent `docs publish` process/
thread that waits for the first to release the lock and then
correctly re-evaluates against the now-current state. This is exactly
the "one succeeds, the other waits and then re-evaluates" behaviour
the plan names as the thing that must be demonstrated, not merely
reasoned about from the code's structure — and this project's own
established precedent (e.g. `L-087`/`L-088`, and this role's own
standing instructions) treats a reasoned-but-undemonstrated safety
claim for a fail-closed/concurrency mechanism as insufficient.

Related, narrower, same-root-cause gap in the same required-tests list:
"an intervening edit between the initial detect call and a
deliberately delayed write is caught by the write-boundary
revalidation (a test that monkeypatches/injects a document mutation
between the two steps)" and "a cited-knowledge change between detect
and write is caught the same way" are also not literally present as
specified. The actual implementation collapsed the plan's envisioned
two-step detect→(gap)→revalidate-at-write design into a single
detect-decide-write sequence that runs entirely inside the lock (see
`cli.py`'s real `docs_publish`, where `detect_grounded_region_changes`
is called exactly once, already inside `with _doc_publish_lock(...)`,
immediately before the write) — which structurally removes the window
the plan's test was written to probe, and the *practical* risk this
specific pair of tests targeted is reasonably (though not completely)
covered in spirit by
`test_docs_publish_refuses_to_overwrite_a_doc_candidate_human_edit`
and `test_docs_publish_refuses_an_unbaselined_region_with_mismatched_
live_content`. This pair is a secondary, weaker finding — the primary,
blocking one is the missing real-concurrency test above, which has no
equivalent coverage anywhere, in-spirit or otherwise.

**No disclosure of either gap was found** in the retro, the
`CHANGELOG.md` draft entry, or the commit message — this was not an
honestly-flagged, deliberately-deferred limitation; it is an
unflagged shortfall against the plan's own mandatory verification
list.

## Non-blocking observations (for the record, not independently
## blocking)

1. The commit message's self-reported ruff-finding count ("6
   pre-existing, unrelated findings only") is off by two orders of
   magnitude from the real count (176) — the real content and
   conclusion of the claim holds (all pre-existing, none a regression),
   but the number itself should not have been trusted without the
   independent re-run this audit performed.
2. The commit message's self-reported new-test count ("47 new
   regression tests") does not match the real count: `grep -cE
   "^\+\s*def test_"` across the commit's test-file diff returns 40,
   consistent with the commit's own "1334 passed... up from 1294" delta
   (40, not 47).

## What must be fixed before re-audit

1. Add a real test that launches two genuinely concurrent `docs
   publish` invocations against the same project/schema/section and
   confirms: exactly one succeeds and writes the document; the other
   either blocks until the lock is released and then correctly
   re-evaluates against the now-current state (succeeding or refusing
   based on that fresh state, never a stale decision), or times out
   cleanly; the document is never corrupted and never double-written.
   A `threading.Thread`-based test with a deliberately-inserted delay
   (e.g. monkeypatching `doc_compiler.publish_section` to sleep briefly
   while holding the lock) is sufficient and matches this project's own
   existing testing idioms — a real subprocess-based test is not
   required if a same-process, two-thread test genuinely exercises the
   same lock file and the same code path.
2. Either add the two more narrowly-scoped tests the plan also names
   (an edit/knowledge-change injected strictly between the detect call
   and the write, exercised via monkeypatching since the collapsed
   single-step design leaves no natural gap to exploit otherwise), or
   explicitly amend the plan's own §O.D.3 to record that the collapsed
   single-critical-section design supersedes the two-step revalidation
   those two tests assumed, and name which existing test(s) now cover
   the equivalent risk — don't leave the mismatch between the plan's
   literal test list and the real implementation's shape unreconciled
   and undisclosed.
3. (Optional, not blocking re-audit, but worth doing in the same pass
   for intellectual honesty) Correct the implementation commit's own
   closeout numbers if it is amended for the above, or note the real
   figures (176 ruff findings, 40 new tests) in the retro/CHANGELOG
   rather than carrying the commit message's inaccurate figures forward
   unchallenged.

Once item 1 (and, ideally, item 2) is addressed and the full suite
still passes, this stage should be re-audited against the new commit
before `planning/ROADMAP.md`/`planning/CONTEXT.md` are updated to mark
Stage 87B done.

---

## Re-audit (2026-11-07, same day, independent dispatch)

- **Auditor:** `release-phase-auditor` (fresh independent dispatch, no
  memory of the FAIL pass above — everything below was re-verified
  directly against the real repository state, not trusted from this
  file's own prior account or from the task prompt's background
  summary).
- **Scope audited:** commit `0f6a268` (unchanged since the FAIL pass)
  plus the real, uncommitted working-tree diff present at this
  dispatch's start (`CHANGELOG.md`; `docs/architecture/components.md`;
  `docs/architecture/documentation-compilation-pipeline.md`;
  `docs/architecture/overview.md`; `docs/reference/cli.md`;
  `planning/learnings/inbox.md`/`promoted.md`;
  `src/codecompass/cli.py`; `tests/test_cli.py`; plus the two retro
  files, one of them this very file). `git status`/`git diff` were run
  directly at the start of this dispatch to establish the real state
  before anything else.

### Verdict: **PASS**

Every item the prior FAIL pass required, and every item this re-audit
was separately asked to independently re-confirm, held up under direct
re-verification — including deliberately trying to break the fix
myself, not merely reading it.

### What was independently re-run and confirmed

1. **The real concurrency test genuinely races two threads and
   genuinely fails if the lock is defeated** —
   `test_docs_publish_two_concurrent_invocations_serialise_through_the_lock`
   read in full: it launches two real `threading.Thread`s calling
   `cli_module.docs_publish` directly (not through `CliRunner`, for the
   stated reason — `CliRunner`'s stdout redirection is not thread-safe),
   monkeypatches `doc_compiler.publish_section` to sleep 0.3s while
   holding a counting lock, and asserts `max_concurrent == 1` plus a
   real timing gate (`entry_times[1] - entry_times[0] >= 0.25`) so the
   two threads are proven to have genuinely overlapped in time, not
   accidentally run sequentially. **Verified by actually defeating the
   lock**: in a disposable script, `codecompass.cli._doc_publish_lock`
   was monkeypatched to `contextlib.nullcontext()` and the real test
   was run against this sabotaged state via `pytest.main(...)` in the
   same process — it failed exactly as the mechanism predicts
   (`assert 2 == 1`), with the captured stdout showing `demo-s1`
   published twice into the same file. Running the unmodified suite
   confirms it passes with the lock intact (`1 passed`). No live
   tracked file was ever modified to do this — the monkeypatch lived
   only in a throwaway script and the test process's own in-memory
   module object; `git diff --quiet -- src/codecompass/cli.py
   tests/test_cli.py` before and after this experiment shows only the
   real, intended uncommitted diff, confirmed unchanged by the
   experiment.
2. **The real fix genuinely re-runs both checks a second time, inside
   the lock, immediately before the write** — read directly in
   `src/codecompass/cli.py::docs_publish`: both
   `_evidence_staleness_error()` (schema-section + cited-knowledge
   freshness) and `_detect_and_decide()` (grounded-region live-state
   check) are each defined once and called twice — once before the
   lock is acquired (fast, user-friendly early refusal), and again
   inside `with _doc_publish_lock(project_root):`, immediately before
   `doc_compiler.publish_section(...)` is called. The baseline-advance
   call sits strictly after the write, inside the same `with` block,
   confirming it still only fires on a genuine successful write.
3. **Both new write-boundary regression tests genuinely reproduce the
   original clobber against the pre-fix code, and pass against the
   real current fix** — confirmed by a disposable comparison: the
   pre-fix `cli.py` (`git show HEAD:src/codecompass/cli.py`, i.e.
   commit `0f6a268` itself, the version the FAIL pass's gap was found
   against) was copied to a scratch package directory
   (`/tmp/.../scratchpad/prefix_src/codecompass/cli.py`) and shadowed
   onto `sys.path` ahead of the real `src/` in a throwaway script —
   never writing into the live tracked `src/codecompass/cli.py` at any
   point. Running
   `test_docs_publish_catches_an_intervening_document_edit_at_the_write_boundary`
   and
   `test_docs_publish_catches_an_intervening_cited_knowledge_change_at_the_write_boundary`
   against that shadowed pre-fix module both **failed** exactly as
   expected (`assert 0 == 1` in each — the clobbered edit/knowledge
   change was silently published over, no refusal). Running the same
   two tests against the real, unshadowed, current working tree both
   **pass**. `git diff --quiet -- src/codecompass/cli.py
   tests/test_cli.py` reconfirmed clean of any experiment side-effect
   throughout (the live tracked file was never touched by this
   comparison — only a scratch copy was).
4. **Full real regression suite, run directly**: `.venv/bin/python -m
   pytest -q` → `1337 passed, 2 skipped in 383.77s` — matches the
   `CHANGELOG.md`/retro-addendum claim exactly (up from the FAIL pass's
   own confirmed `1334 passed, 2 skipped`; +3, matching the three new
   regression tests this fix round added).
5. **`ruff check .`** → `176` findings, confirmed identical in count
   and in file-set to the FAIL pass's own independently-verified
   figure; confirmed **zero** findings in `src/codecompass/cli.py` or
   `tests/test_cli.py` specifically (`ruff check . | grep -E
   "^(src/codecompass/cli\.py|tests/test_cli\.py)"` → no output) — the
   fix round introduced no new lint findings in the files it touched.
   **`scripts/check_doc_schema.py --strict`** → `no findings`.
   **`scripts/check_user_docs.py --strict`** → `no findings`.
6. **Both secondary numeric corrections are now accurate, and the
   original commit message is genuinely unamended**: `CHANGELOG.md`'s
   Stage 87B entry states "40 net new tests from this stage's
   implementation commit, plus 3 more from this fix" and "176 real
   pre-existing, unrelated findings" — both independently re-confirmed
   above. `git show --no-patch --format='%B' 0f6a268` still reads "47
   new regression tests" and "Ruff clean (6 pre-existing, unrelated
   findings only)" verbatim — confirmed the already-written commit was
   never rewritten; the correction lives only in `CHANGELOG.md` and the
   retro addendum, exactly as this project's own established practice
   (carry a discovered inaccuracy forward as a correction, never
   amend/rewrite a landed commit) requires.
7. **The docstring and both doc updates honestly disclose a narrowed,
   not eliminated, race window** — `_doc_publish_lock`'s own docstring
   (`src/codecompass/cli.py`), `docs/reference/cli.md`, and
   `docs/architecture/documentation-compilation-pipeline.md` were each
   read in full: all three state the second check narrows but does not
   fully close the window between the final check and the write, name
   what would close it completely (a full transactional write) and why
   it was deliberately not built (smallest-coherent-change instruction),
   and none overclaims the fix as a complete, airtight solution.
8. **Full DoD re-check against the current state, not re-trusting
   the FAIL pass's own prior "passed" list**:
   - **CLAUDE.md**: `git log -1 --format='%H %ci' -- CLAUDE.md` → an
     unrelated commit from 2026-10-07, long before this stage — no
     drift.
   - **`decisions/`**: `git diff --stat -- decisions/ CLAUDE.md` →
     empty — no change to either.
   - **Changed-file list matches plan scope, no 87C creep**: the full
     set of touched files (committed in `0f6a268` + the real
     uncommitted diff) is exactly the fix-round's own expected set
     (`src/codecompass/cli.py`, `tests/test_cli.py`, the three
     `docs/architecture/*.md` + `docs/reference/cli.md` pages
     describing the fix, `CHANGELOG.md`, two retro files, two learnings
     files) — confirmed via `git diff --numstat`/`git status
     --porcelain`. Grepping the full diff for "deterministic CLI-
     reference generat" / "matched-baseline rubric" finds only
     passing mentions correctly describing Stage 87C as separately
     planned/unauthorised, never implemented scope — no creep.
   - **`CONTEXT.md`/`ROADMAP.md` correctly still NOT updated** to mark
     Stage 87B done — both still describe it as planned/not-yet-closed,
     consistent with `CLAUDE.md` §5's explicit carve-out that this
     reconciliation is the terminal step, done only after this audit
     passes.
   - **Learnings triage genuinely happened and is unchanged by this fix
     round**: `L-121` (namespace-sandbox footguns) is `promoted`, with
     a `promoted.md` line and the promoted text verified present
     verbatim in `docs/architecture/overview.md`'s "Known footguns"
     section. `L-122` (uncaptured broker usage/cost figures) is
     honestly left `candidate`, explicitly handed to
     `roadmap-context-curator` for a backlog line — not yet landed,
     consistent with the task's own framing. Neither needed any new
     entry for this specific fix round (the concurrency gap and its
     fix are documented in the retro addendum and `CHANGELOG.md`
     directly, not as a separate learnings-log candidate — reasonable,
     since it is a direct FAIL-fix-reaudit cycle on this stage's own
     already-filed scope, not a new generalisable cross-project
     observation).
   - **`CHANGELOG.md` entry accuracy**: read in full; accurately
     describes all seven original deliverables, the FAIL finding, the
     fix, the three new regression tests, the corrected numeric
     figures, and correctly states Phase 87 overall remains not done
     and Stage 87C remains unauthorised.

### Non-blocking observations

None beyond what the FAIL pass already recorded and this fix round
already addressed. No new observations found in this re-audit.

### Disposition

**PASS.** Stage 87B's closure may now proceed to the terminal
`roadmap-context-curator` reconciliation step (flipping
`planning/ROADMAP.md`'s row, overwriting `planning/CONTEXT.md`'s
current-state section, and updating the plan file's own Status line)
per `CLAUDE.md` §5's named exemption — provided that commit touches
only those three targets and nothing else, which would void this pass
and require a fresh one.
