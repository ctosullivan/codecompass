# Independent audit — Phase 87 Stage 87B, second post-closeout hardening pass (commit `cd81892`)

**Audited commit:** `cd81892d0210592d499ae7ad39935517aedea5bc`
("fix(phase-87): bind docs publish's review identity to top-level
schema fields"), parent `db33327` (clean pre-fix state).

**Verdict: PASS**

## What was audited

Commit `cd81892` claims to fix a fourth real defect in `docs publish`'s
publication-integrity mechanics (the same path already hardened twice
before, per this retro's own Addendum 1 and Addendum 2): the persisted
`schema_section_sha256` hash, which every recorded review and the
pending manifest are bound to, covered only the schema *section* dict
and never the schema's own top-level `document`, `audience`, or
`acceptance_criteria` fields — so a schema's `document` field could be
retargeted after both independent reviews already passed, with the
section dict left byte-identical, and `docs publish` would write the
already-reviewed draft into a different, never-reviewed-against
document.

## What I independently re-ran and confirmed

1. **Read the real diff directly** (`git show cd81892`), not the
   commit message's own account. Confirmed:
   - `doc_compiler.compute_schema_section_identity_sha256(schema,
     schema_section)` is new, purely additive (37 insertions, 0
     deletions in `doc_compiler.py` — no existing function touched),
     and binds `{"document", "audience", "acceptance_criteria",
     "section"}` into one hash.
   - `docs compile` (`cli.py`) now computes the persisted
     `schema_section_sha256` through this function, passing the full
     top-level `schema` dict parsed at the top of `docs_compile`
     (confirmed by direct read of the surrounding code, not assumed).
   - `docs publish`'s `_evidence_staleness_error` now returns `(error,
     live_document_path)` and recomputes the identical structure from
     a schema re-read fresh from disk on *every* call — both the
     pre-lock fast-path call (line ~2303) and the write-boundary call
     inside the lock (line ~2496) — mirroring Addendum 2's own
     Finding B double-check discipline, not merely calling the same
     stale-object function twice.
   - **The write target is genuinely re-resolved, not merely
     hash-checked.** At the write boundary, `document_path =
     live_document_path` (line 2508) reassigns the actual write target
     to the value freshly resolved from the live schema inside the
     second `_evidence_staleness_error()` call, and this reassigned
     `document_path` is what `doc_compiler.document_identity(
     document_path)` and `doc_compiler.publish_section(document_path,
     ...)` both subsequently use (lines 2531-2537) — confirmed by
     reading the full `docs_publish` function body end to end, not a
     sampled excerpt.

2. **Reproduced the original exploit myself**, independently, against
   parent commit `db33327`. Built a standalone script
   (`/tmp/.../scratchpad/exploit_repro.py`, kept outside the repo) that
   writes a knowledge claim, a schema targeting
   `docs/demo-original.md`, a pending manifest (bypassing the LLM
   broker, exactly as this project's own test helper does), records
   both passing reviews via the real `docs record-review` CLI command,
   then rewrites *only* the live schema's `document` field to
   `docs/demo-RETARGETED.md`, and invokes `docs publish` via
   `typer.testing.CliRunner`.
   - Used a disposable `git worktree` at `db33327`
     (`/tmp/.../scratchpad/worktrees/prefix`) with `PYTHONPATH`
     explicitly pointed at that worktree's own `src/`.
   - **Confirmed the venv's editable-install `.pth` footgun is real**:
     running the script with Python's `-I` (isolated mode) silently
     ignored `PYTHONPATH` and loaded `codecompass` from the main
     repo's `src/` (confirmed via `codecompass.__file__`) — which, at
     the time I ran it, was already the fixed `cd81892` tree, and the
     exploit was (correctly) refused. Caught this via the mandated
     `codecompass.__file__` check before trusting the result, dropped
     `-I`, and re-ran: `codecompass.__file__` then correctly resolved
     inside the pre-fix worktree.
   - **Result against the genuine pre-fix worktree: exploit
     succeeded.** `docs publish` exited 0, published into
     `docs/demo-RETARGETED.md`, and `docs/demo-original.md` was never
     created — exactly the claimed defect, reproduced directly, not
     taken on faith.

3. **Confirmed the fix closes it**, same script, against current HEAD
   (`codecompass.__file__` confirmed resolving to the live main-repo
   `src/`): `docs publish` exited 1 with "this section's schema
   definition (including its document/audience/acceptance_criteria)
   has changed since it was compiled -- recompile and re-review before
   publishing"; neither `docs/demo-original.md` nor
   `docs/demo-RETARGETED.md` was written.

4. **Ran a 5-test sample of the 11 new regression tests** (more than
   the minimum 3 asked) against both regimes:
   - `test_schema_section_identity_changes_when_document_changes`,
     `test_schema_section_identity_unaffected_by_unrelated_top_level_fields`
     (`tests/test_doc_compiler.py`)
   - `test_docs_publish_rejects_a_document_target_retargeted_after_both_reviews_passed`,
     `test_docs_publish_rejects_a_document_retargeted_at_the_write_boundary`,
     `test_docs_publish_accepts_unchanged_top_level_schema_fields_unaffected`
     (`tests/test_cli.py`)
   - Copied the post-fix `tests/test_doc_compiler.py` and
     `tests/test_cli.py` onto the disposable pre-fix worktree (source
     code left at `db33327`) and ran with `PYTHONPATH` overridden:
     **all 5 failed**, via `AttributeError: module
     'codecompass.doc_compiler' has no attribute
     'compute_schema_section_identity_sha256'` — consistent with the
     claimed pre-fix-failure pattern (the shared `_setup_demo_schema_and_pending`
     helper itself calls the new function).
   - Ran the identical 5 tests against current HEAD (real repo,
     editable install): **all 5 passed.**
   - This is a genuine fail→pass result for a representative sample,
     not merely trusted from the commit message.

5. **Ran the full regression suite** at current HEAD:
   `.venv/bin/python -m pytest -q` → **`1363 passed, 2 skipped`**,
   exactly matching the claim (1352 + 11 new = 1363).

6. **Ran the strict tooling** at current HEAD:
   - `ruff check .` → **176 findings**, matching the documented
     pre-existing baseline exactly; confirmed via direct grep that
     none of the 176 findings fall in `src/codecompass/cli.py`,
     `src/codecompass/doc_compiler.py`, `tests/test_cli.py`, or
     `tests/test_doc_compiler.py` (the four files this commit
     touches).
   - `scripts/check_doc_schema.py --strict` → "no findings".
   - `scripts/check_user_docs.py --strict` → "no findings".

7. **Spot-checked the three prior findings' guarantees are
   preserved**, by reading the full `docs_publish` function body
   (not sampled excerpts):
   - **Finding A** (`_reviewed_draft_integrity_error`,
     `_reread_pending_at_write_boundary`): present, unmodified in
     logic, still called once before the lock and once again at the
     write boundary.
   - **Finding B** (live schema re-read on every call): the exact
     mechanism this commit's own fix extends — `_evidence_staleness_error`
     still re-reads `schema_path` from disk on every call; this
     commit only changes what it hashes, not whether/when it re-reads.
   - **Finding C** (`document_identity`/`DocPublishConflictError`
     compare-and-swap, `_doc_publish_lock`): both present and
     unmodified — `expected_document_identity` is computed immediately
     before `publish_section` is called, same as before, now simply
     against the correctly-re-resolved `document_path`.
   - `doc_compiler.py`'s diff being purely additive (37/0) makes this
     conclusion structural, not just a reading judgment: none of the
     functions those three findings' fixes live in were touched at
     all by this commit.

8. **Confirmed no protected-file drift**: `git diff --name-only
   cd81892^ cd81892` → `CHANGELOG.md`,
   `planning/retros/phase-87-stage-87b-knowledge-change-demonstration.md`,
   `src/codecompass/cli.py`, `src/codecompass/doc_compiler.py`,
   `tests/test_cli.py`, `tests/test_doc_compiler.py`. No `CLAUDE.md`,
   no `decisions/*` file in the diff.

9. **Confirmed honest disclosure, specifically checked for the
   self-certification pattern this project was caught on once already
   this session** (Addendum 2's first audit FAIL): both the new
   `CHANGELOG.md` entry and the retro's own "Addendum 3" state closure
   is **pending** this audit — the changelog entry's final sentence
   reads "Stage 87B's technical closure against this correction is
   **pending** a fresh independent audit," and Addendum 3 says "see
   ... the independent audit this addendum's own fix requires for the
   exact, current figures." Neither document claims a PASS, cites a
   nonexistent audit file, or states an audit outcome that had not yet
   happened at commit time. No recurrence of the self-certification
   defect found.

## Non-blocking observation (not a defect in the audited commit)

During this audit session, an **unrelated, uncommitted** modification
to `planning/phase-87-documentation-schema-knowledge-compiled-documentation.md`
appeared in the working tree (confirmed via `git status`/`stat` —
mtime inside this audit's own session window, after `cd81892` was
already committed). This touches only Stage 87C planning-document
arithmetic/counts, has nothing to do with `schema_section_sha256` or
`docs publish`, was not introduced by any command I ran (I never wrote
to this path; all my writes went to a disposable `git worktree` and a
scratchpad script, both now removed), and is evidence of other,
concurrent work happening against this repository outside this
commit's own scope. Flagged for the lead's awareness; not evaluated
further here since it is unrelated to the commit under audit and the
mandate is read-only.

## Cleanup confirmation

The disposable `git worktree` used for pre-fix reproduction
(`/tmp/.../scratchpad/worktrees/prefix`, including its test-file
overwrites) was removed via `git worktree remove --force` after use;
its backing directory never coincided with any tracked path in the
main repository. `git status` in the main repository shows no change
to any file this audit touched (`src/codecompass/*`, `tests/*`,
`CHANGELOG.md`, the retro) — the only working-tree modification
present is the unrelated planning-doc edit described above, which I
did not make and did not restore (restoring it would itself be an
unrequested write to content I didn't touch and don't have grounds to
judge as wrong).

## Conclusion

Every claim in commit `cd81892`'s own message and the retro's
Addendum 3 held up under independent, from-scratch re-verification:
the mechanism is real and genuinely wired (write target re-resolved,
not merely hash-checked); the original exploit was reproduced for real
against the true pre-fix source (not the editable-installed main-repo
copy); the fix genuinely closes it; a sample of the new tests
demonstrably fail pre-fix and pass post-fix; the full suite and strict
validators are clean at the stated counts; the three prior hardening
findings are structurally undisturbed; no protected-file drift
occurred; and disclosure of pending-audit status was honest in both
the changelog and the retro, with no recurrence of the earlier
self-certification defect.

**Verdict: PASS.**
