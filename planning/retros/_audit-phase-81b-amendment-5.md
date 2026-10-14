# Independent completion audit — Phase 81B, Amendment 5 (corrective)

Auditor: `release-phase-auditor` (independent dispatch, read-only).
Audited commit: `40f8c8eba9316560070dca29298ba85dfc44b603` (HEAD on
`main` at audit time; confirmed via `git log --oneline -10` and
`git rev-parse HEAD` myself, not trusted from the dispatch prompt).

Scope: plan `planning/phase-81b-clean-room-redocumentation.md` §27
(corrected completion criteria §27.3), ADR `decisions/0077`, retro's
"Amendment 5 (corrective)" section, `CHANGELOG.md`'s new Amendment 5
entry, `scripts/prepare_cleanroom_branch.py`,
`scripts/verify_cleanroom_isolation.py`, their test modules, and the
eight falsification targets named in the dispatch.

## Verdict: PASS WITH NON-BLOCKING OBSERVATIONS

The corrective mechanism itself is real, independently verified by
re-running it (not merely reading it), and matches its own governing
documents on every functional claim. One genuine, confirmed numerical
inconsistency in the written record (not in the code) is reported below
as a non-blocking finding that should still be corrected.

## Falsification attempts against the eight claims

**1. Narrative isolation — attempted to falsify: could not.**
Enumerated every doc-shaped file (`.md`/`.rst`/`.txt`) actually tracked
beneath `src`, `tests`, `scripts` in the real repository at HEAD via
`git ls-tree -r --name-only HEAD -- src tests scripts | grep -iE
'\.(md|rst|txt)$'`. Result: exactly 8 files. Cross-checked every one
against `_CLASSIFIED_KEEP_DOC_PATHS` (3 entries:
`tests/fixtures/sample_readme.md`,
`tests/fixtures/ledgerkit_lifecycle_demo/.claude/commands/discovery.md`,
`tests/fixtures/ledgerkit_lifecycle_demo/.claude/skills/codecompass/SKILL.md`)
and `_CLASSIFIED_EXCLUDE_DOC_PATHS` (5 entries: `tests/README.md`,
`.../DEMO.md`, `.../dev-docs/architecture.md`,
`.../dev-docs/planning/README.md`, `.../dev-docs/retros/README.md`).
3 + 5 = 8 — every real doc-shaped file is classified; none would
silently ride through uncaught. Also ran
`test_cmd_build_fails_closed_end_to_end_for_an_unclassified_narrative_file`
(passes) confirming a genuinely new, unclassified file fails the whole
build closed through the real `cmd_build` entrypoint, not just the
inner helper. Also re-ran the same `git ls-tree` sweep against
`cleanroom/redoc-b939d23` (the actual Amendment 4 branch) — identical 8
files, identical 3/5 split, confirming the classification set is
complete against the real historical run, not just against today's
tree.

**2. Revision provenance — attempted to falsify: could not.**
Read `_export_path`, `_export_allowed`, `_require_commit_exists`,
`_git_object_type`, `_git_tracked_files_at_revision`,
`_export_file_at_revision` in full. All five read exclusively via `git
cat-file`/`git ls-tree` against an explicit `revision` argument, never
the working tree or `cwd` defaults. Ran the real test suite's own
`test_export_reads_committed_content_not_a_dirty_working_tree` and
`test_export_does_not_leak_a_later_commit_into_an_earlier_revisions_export`
— both pass, both construct a real scratch Git repo and assert the
dirty/later content never appears in the export. `_require_commit_exists`
fails closed via `git cat-file -e <rev>^{commit}` before any copy starts.

**3. Submodule provenance — attempted to falsify: could not.**
`_submodule_gitlink_sha` resolves the gitlink via `git ls-tree
<documented_revision> -- <submodule_rel>` on the *superproject*, never
reading the submodule's own checked-out HEAD. Ran
`test_submodule_export_uses_the_pinned_gitlink_not_the_checked_out_head`
— a real end-to-end scenario: a scratch submodule is advanced to a new
commit and its working copy is actually checked out to that new commit
locally, and the export still produces the pinned, older gitlink
content. Passes.

**4. Payload integrity — attempted to falsify: could not; ran the
exact adversarial cycle requested.**
```
python3 scripts/prepare_cleanroom_branch.py build /tmp/audit-staging \
  --documented-revision <HEAD> --slugs codecompass-domain
python3 scripts/prepare_cleanroom_branch.py validate /tmp/audit-staging   # PASS
# mutated an existing payload file's content (appended a line to
# src/codecompass/usage.py)
python3 scripts/prepare_cleanroom_branch.py validate /tmp/audit-staging   # FAIL:
#   hash mismatch for src/codecompass/usage.py: manifest says
#   91ccbfed5017..., fresh hash is 8c34e6d38936...
```
Separately also added a brand-new, untracked file into the staged tree
and re-validated: caught as `unlisted writer-visible path present`.
Both failure modes work. `/tmp/audit-staging` removed after the test.
`cmd_validate` reads `payload_file_hashes`/`payload_tree_sha256` purely
from the manifest and the staged tree — confirmed no `ROOT` reference
anywhere inside `cmd_validate` (see finding 6).

**5. Handoff identity — attempted to falsify: could not.**
`cmd_build`'s manifest dict (read in full) no longer contains
`handoff_commit` anywhere. Identity claims are `manifest_schema_version`,
`documented_revision`, `payload_tree_sha256`, `payload_file_hashes` — all
computable before any commit exists. Ran
`test_manifest_schema_version_and_no_self_referential_commit_field` —
passes, explicitly asserts `"handoff_commit" not in manifest`. No other
field in the manifest is self-referential (`generated_at`,
`codecompass_version`, `included_paths`, `excluded_paths`, policy
strings, and `invalidated_by: None` are all either external facts or
null placeholders, not self-referential identity claims).

**6. Validator independence — attempted to falsify: could not.**
`grep -n "ROOT"` restricted to the `cmd_validate` function body returns
zero hits — the function never touches `ROOT` or the live repository.
Ran `test_validate_never_reads_outside_the_staging_tree`, which
monkeypatches `ROOT` to `/nonexistent-parent-repo` and confirms
`cmd_validate` still returns 0 — passes.

**7. Isolation reproducibility — ran it for real, did not just confirm
the file exists.**
`unshare` and `pivot_root` are both available in this environment
(`/usr/bin/unshare`, `/usr/sbin/pivot_root`). Ran
`python3 scripts/verify_cleanroom_isolation.py` directly (not just
`pytest`). Output: all 11 named checks (`evidence_readable`,
`output_writable`, `parent_host_paths_unavailable`,
`sibling_repositories_unavailable`, `git_history_unavailable`,
`git_remotes_unavailable`, `environment_secrets_absent`,
`unapproved_network_unavailable`, `github_unavailable`,
`broker_boundary`, `parent_agent_context_absent`) reported `pass`, with
specific, non-generic detail strings per check (e.g. "its host-side TCP
listener (a deliberately-provided non-approved path) is unreachable"),
consistent with a real sandbox actually being built and probed, not a
hardcoded pass list. Final line: `PASS: every mechanically-testable
isolation condition held`. Read the probe implementation
(`_FakeUnixBroker`/`_FakeTCPBroker`, `_probe_evidence_readable`,
`_probe_output_writable`) — genuine socket servers and real
filesystem/env checks, not stubs.

**8. No-redoc scope — attempted to falsify: could not.**
```
git diff 2d01e2d..HEAD --stat -- README.md docs/ ai-docs/ architecture/ CONTRIBUTING.md
#  docs/development/clean-room-redocumentation.md | 107 ++++++++++++++---
#  1 file changed, 95 insertions(+), 12 deletions(-)
```
Exactly the one explicitly-scoped process doc, nothing else.
`codecompass-template` (`/home/cormac/projects/codecompass-template`):
`git status` clean, `git log -3` shows HEAD still `dff3f4d` (Amendment
4's own commit) — zero commits since. Full repo-wide diff
(`git diff 2d01e2d..HEAD --stat`, no path filter) confirms the complete
changed-file set matches §27.2's declared scope exactly: `CHANGELOG.md`,
`decisions/0077-...md` (new), `docs/development/clean-room-redocumentation.md`,
`planning/ROADMAP.md`, `planning/learnings/{inbox,promoted}.md`,
`planning/phase-81b-clean-room-redocumentation.md`,
`planning/retros/phase-81b-clean-room-redocumentation.md`,
`scripts/prepare_cleanroom_branch.py`,
`scripts/verify_cleanroom_isolation.py` (new), and the two test modules.
No scope creep into any other file.

## DoD checks re-run directly

- `tests/test_prepare_cleanroom_branch.py` + `tests/test_verify_cleanroom_isolation.py`
  + `tests/test_cleanroom_broker.py` + `tests/test_cleanroom_prompt_assembler.py`:
  **71 passed**, 0 failed.
- Full suite, `-k "not live"`: **917 passed, 12 deselected**, 0 failed
  (200.84s).
- `ruff check .`: **All checks passed!**
- `python3 scripts/check_user_docs.py --strict`: **no findings**.
- `python3 scripts/check_knowledge_base.py --strict`: **24 info-level
  `knowledge-base-snapshot-current-divergence` findings** — confirmed
  pre-existing and unrelated to this amendment: `git diff 2d01e2d..HEAD
  --stat -- planning/knowledge/` is empty (zero changes to any knowledge
  file across the whole amendment), so these findings existed
  identically before Amendment 5 began. Matches the "expected and
  healthy" framing the check itself prints and the general pattern of
  `planning/CONTEXT.md`'s "Known standing gaps" section.
- `planning/learnings/inbox.md` / `promoted.md`: **L-099 and L-100 are
  genuinely triaged**, not just filed — both have a `status: promoted`
  line, a `knowledge-curator` curation paragraph in `inbox.md` that
  verifies specific named code/test artifacts against commit `83d7e25`
  (not a rubber-stamp), and a corresponding `promoted_to` entry in
  `promoted.md`.

## Protected-file / scope-creep check

`git diff 2d01e2d..HEAD` touches no `CLAUDE.md`, no past ADR's original
content (0077 is new, not an edit to an existing one), and no file
outside §27.2's declared scope plus the expected `planning/ROADMAP.md`
status-line update. `planning/ROADMAP.md`'s Phase 81B row currently
reads "in progress (amendment 5, corrective)" — correctly **not**
flipped to `done` yet, consistent with CLAUDE.md §5's gate.
`planning/CONTEXT.md` still describes Amendment 4's "done" outcome with
no mention of Amendment 5 at all — this is **expected, not a defect**:
per CLAUDE.md §5's named exemption, overwriting `CONTEXT.md`'s
current-state section is explicitly reserved for the terminal
`roadmap-context-curator` reconciliation commit that follows a passing
audit, and the corrective-amendment commit sequence here (confirmed via
`git show --stat a6c42da`) already follows that same pattern used
throughout this phase's history (ROADMAP flips immediately to mark
in-progress state; CONTEXT.md is deferred to terminal reconciliation).

## Non-blocking finding: a numerical inconsistency in the written record

The plan and changelog describe the number of real narrative-leak files
Amendment 5 found inconsistently with the code and with the retro's own
(correct) count.

- **Ground truth** (re-derived independently, twice: against current
  HEAD and against the actual Amendment-4-era branch
  `cleanroom/redoc-b939d23`): exactly **5** narrative files were leaked
  — `tests/README.md` plus **4** `ledgerkit_lifecycle_demo` fixture docs
  (`DEMO.md`, `dev-docs/architecture.md`, `dev-docs/planning/README.md`,
  `dev-docs/retros/README.md`). This matches
  `_CLASSIFIED_EXCLUDE_DOC_PATHS`'s own 5 entries exactly, and matches
  the original defect-recording commit's own message (`a6c42da`:
  "tests/README.md and four ledgerkit_lifecycle_demo fixture docs"), and
  matches the retro's "What this corrective review discovered" section
  ("`tests/README.md` and four `ledgerkit_lifecycle_demo` fixture
  docs").
- **But** plan §27.3 item 2 says "the **six** confirmed real leaks from
  §27.1 item 1", and plan §27.4 says "**six** narrative Markdown files
  nested beneath the broadly allow-listed `tests/**` tree" — both
  overstate the count by one.
- **And** `CHANGELOG.md`'s Amendment 5 entry says "a test-suite README
  and **five** `ledgerkit_lifecycle_demo` fixture docs" (implying 6
  total) — also overstates by one.
- **And** learning `L-100`'s own `observation` field in
  `planning/learnings/inbox.md` repeats the same "five... fixture docs"
  overstatement, meaning this specific miscount has now been carried
  into a `promoted` learning's permanent record.

This does not affect the mechanism's actual correctness (independently
re-verified above: all 8 real doc-shaped files are correctly classified,
5 excluded + 3 kept, matching ground truth exactly) and does not change
the "fixture-scale, never the real `README.md`/`docs/`/`architecture/`/
`ai-docs/` tree" framing, which remains true either way. It is a factual
error specifically in the *count* used in plan §27.3 item 2, plan §27.4
(part of the plan's own "corrected historical claim," which §27.3 item 7
requires to be "qualified, not overstated and not understated" — this
narrow count is overstated by one), `CHANGELOG.md`, and `L-100`. It
should be corrected (four places) before or shortly after this phase
returns to `done`, but does not by itself invalidate the mechanism fix
or block the DoD gate, since: (a) the retro and the original
defect-recording commit already have the correct count, (b) the
underlying classification set used by the actual code is independently
confirmed complete and correct against real ground truth, and (c) no
functional claim in §27.3 depends on this specific number being exactly
six vs. five.

## Summary of what must be fixed (non-blocking; may be folded into the
terminal reconciliation commit or done as a quick separate commit)

1. Plan §27.3 item 2: change "the six confirmed real leaks" to "the
   five confirmed real leaks".
2. Plan §27.4: change "six narrative Markdown files" to "five narrative
   Markdown files".
3. `CHANGELOG.md`'s Amendment 5 entry: change "a test-suite README and
   five `ledgerkit_lifecycle_demo` fixture docs" to "...and four
   `ledgerkit_lifecycle_demo` fixture docs".
4. `planning/learnings/inbox.md`'s `L-100` observation field: same
   four/five correction (note: this is inside an already-`promoted`
   learning entry; correct the inbox record for accuracy even though
   the underlying promoted invariant itself is unaffected).

## Conclusion

Every one of the eight claims in the dispatch survived active
falsification attempts backed by direct code reading and real,
independently-run commands (not trust in commit messages or prior
agent reports). All nine corrected-completion-criteria in plan §27.3
hold, with the sole caveat that §27.3 item 7's "qualified, not
overstated" requirement is itself violated by a narrow, non-blocking
factual overstatement (six vs. the real five) in the plan's own §27.4
text and in `CHANGELOG.md`/`L-100`. Phase 81B may return to `done` once
the DoD's terminal `roadmap-context-curator` reconciliation commit runs
(flipping `planning/ROADMAP.md` back to `done`, overwriting
`planning/CONTEXT.md`'s current-state section to describe Amendment 5,
and updating the plan file's own Status line) — this audit does not
need to be re-run afterward provided that terminal commit touches only
those three named targets, per CLAUDE.md §5's own exemption. The
four-item count correction above is recommended but does not block that
transition.

## Narrow re-audit (commit 7dbad6c)

Auditor: `release-phase-auditor` (independent dispatch, read-only).
Scope: narrow re-check of commit `7dbad6c1ab00178fa9b851c9c912503178b42e1d`
(current `main` HEAD, confirmed via `git log --oneline -5` myself), the
single follow-up fix for this report's one non-blocking finding — not a
full re-run of the original eight-claim audit above.

### Verdict: PASS

### What was checked

1. **Diff contents.** `git show 7dbad6c --stat` and `git show 7dbad6c`
   read in full. Exactly 5 files changed, 9 insertions / 9 deletions:
   `CHANGELOG.md`, `docs/development/clean-room-redocumentation.md`,
   `planning/learnings/inbox.md`, `planning/phase-81b-clean-room-redocumentation.md`
   (2 edits), `planning/retros/phase-81b-clean-room-redocumentation.md`.
   Every hunk is a narrow six→five or five→four word substitution; no
   other prose, code, or structure changed.

2. **Count now consistent everywhere, cross-checked against the real
   mechanism.** `scripts/prepare_cleanroom_branch.py`'s
   `_CLASSIFIED_EXCLUDE_DOC_PATHS` frozenset (lines 163-171) has exactly
   5 entries: `tests/README.md` plus 4 `ledgerkit_lifecycle_demo` fixture
   docs (`DEMO.md`, `dev-docs/architecture.md`,
   `dev-docs/planning/README.md`, `dev-docs/retros/README.md`) —
   confirmed by direct read, matching ground truth from the original
   audit. Every post-fix mention of this count is now correct:
   - Plan `planning/phase-81b-clean-room-redocumentation.md` line 2431:
     "the five confirmed real leaks from §27.1 item 1" — correct.
     Line 2473: "found that five narrative Markdown files" — correct.
     Line 2481: "the five leaked files are fixture-scale" — correct.
   - `CHANGELOG.md` line 65 (context from the diff): "a test-suite
     README and four `ledgerkit_lifecycle_demo` fixture docs" — correct
     (1 + 4 = 5 total). Line 70: "naming the five real fixture-scale
     files found" — correct.
   - `docs/development/clean-room-redocumentation.md` line 177: "found
     five genuine narrative leaks this way: a test-suite README and
     four fixture docs" — correct.
   - `planning/learnings/inbox.md` L-100 observation (line 23):
     "`tests/README.md` and four `ledgerkit_lifecycle_demo` fixture
     docs" — correct. (Note: the same file's line 46/62 already said
     "five matching regression tests" pre-fix — a different, unrelated
     count of tests, not files; untouched and correctly so.)

3. **Retro's "six defects" correctly left alone.**
   `planning/retros/phase-81b-clean-room-redocumentation.md` line 382
   ("None of these six defects were about the *documentation content*")
   and line 451 ("All six defects corrected and regression-tested") were
   grepped directly post-fix: both still say "six," unchanged by
   `7dbad6c`. These correctly refer to the six distinct defect/claim
   categories the corrective review addressed (narrative isolation,
   revision provenance, submodule provenance, payload integrity,
   handoff identity, validator independence — the eight falsification
   targets collapse to six original defect classes per the retro's own
   framing), not to the file-leak count, and must not have been
   changed. Confirmed they were not accidentally touched: `7dbad6c`'s
   diff hunk against this file only touches line ~406 ("the five
   fixture-scale files found," correctly changed from "six"), nothing
   near lines 382/451.

4. **Lint and docs checks re-run on current HEAD.** `ruff check .`
   (via the project's `.venv/bin/ruff`, since a bare `ruff` binary isn't
   on `PATH` in this shell): **All checks passed!** `python3
   scripts/check_user_docs.py --strict`: **no findings**. Neither tool
   flagged anything new as a result of this commit.

5. **Scope.** `git show 7dbad6c --stat` and `git diff
   40f8c8e..7dbad6c --stat` both confirm the exact same 5 files listed
   above and nothing else — no `src/`, no `tests/`, no `scripts/`, no
   `README.md`, no other `docs/` file, no `ai-docs/`, no reference-project
   output. This matches the dispatch's named expected file set exactly.

### Conclusion

The follow-up commit does precisely what it claims: a narrow,
accurately-scoped word-level correction of the six→five miscount this
report's non-blocking finding identified, verified against the real
`_CLASSIFIED_EXCLUDE_DOC_PATHS` ground truth, with no collateral damage
to the retro's unrelated and correct "six defect classes" language, and
no new lint/doc-check findings. Phase 81B may now proceed to its
terminal `roadmap-context-curator` done-marking commit (flipping
`planning/ROADMAP.md` to `done`, overwriting `planning/CONTEXT.md`'s
current-state section, and updating the plan file's own Status line) —
per CLAUDE.md §5's named exemption, that terminal commit itself does not
require a further audit pass provided it touches only those three named
targets.
