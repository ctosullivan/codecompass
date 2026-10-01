# Independent audit — Phase 79 fifth amendment (`decisions/0067`)

**Auditor:** `release-phase-auditor` (independent, read-only). This is a
direct-review correction pass on already-`done` work, not a from-scratch
re-audit of Phase 79's original scope (already covered by
`_audit-phase-79.md` / `_audit-phase-79-reaudit.md`).

**Audited against:** `b95a1f1e009c5294c473f3df081cc484a66c1769` (HEAD,
confirmed via `git log -1`). Amendment diff: `git diff 1ca49a3..HEAD
--stat` — 59 files changed, +3926/-62, spanning `4ca2d88` through
`b95a1f1` (7 commits): `4ca2d88`, `c42d255`, `36986d3`, `caf8ca1`,
`9dc1b77`, `9c73589`, `b95a1f1`.

---

## 0. L-070's own requirement, applied to this audit's own verification

Per `CLAUDE.md` §1 (the `L-070` rule this amendment landed), ran the new
`check_snapshot_completeness` against a disposable fixture reduced to
the minimal-content edge case myself, independent of the test suite:

Built a fresh throwaway git repo
(`/tmp/claude-1000/.../scratchpad/kb-fixture/repo`) with one real
`CL-MYTOPIC-001.yaml` committed, then a sidecar containing *only*
`snapshot_id = "my-topic@v1"` (nothing else). Called
`check_knowledge_base.check_snapshot_completeness` directly against it:

```
4 findings
  [knowledge-base-snapshot-missing-metadata] strict=True ... missing required top-level field 'created'
  [knowledge-base-snapshot-missing-metadata] strict=True ... missing required top-level field 'repository_revision_at_freeze'
  [knowledge-base-snapshot-missing-metadata] strict=True ... missing required top-level field 'excluded_assertions'
  [knowledge-base-snapshot-missing-metadata] strict=True ... missing required top-level field 'assertions'
```

All four findings `strict=True`. Confirms the function genuinely fails
closed against the exact minimal-content shape named, independent of the
test file's own `test_gutted_snapshot_reduced_to_only_snapshot_id`
assertions (which I also ran and confirm pass, separately).

---

## 1. Fail-closed snapshot validation

- `check_snapshot_completeness` exists in `scripts/check_knowledge_base.py`
  (lines 597-808), registered in `CHECKS` (line 959) and dispatched from
  `run_all` (lines 977-988) with the `root` parameter threaded through
  correctly alongside the other three `root`-aware checks.
- `.venv/bin/python -m pytest tests/test_check_knowledge_base.py -v` →
  **25 passed**, including a 10-test `TestSnapshotCompleteness` class
  (gutted-to-`snapshot_id`, missing assertion, excluded assertion,
  post-freeze claim, omitted evidence/derivation closure, malformed
  assertions table, malformed `excluded_assertions`, identity mismatch,
  complete-snapshot-clean) plus one new test in `TestSnapshotIntegrity`
  (`test_legitimate_supersession_is_also_completeness_clean`).
- My own independent fixture (§0 above) confirms the real function
  behaves as claimed, not merely the test file's own assertions.
- **Minor factual discrepancy (non-blocking):** the commit message
  (`4ca2d88`), the plan's own §0 "Fifth revision" entry 1, and the
  `CHANGELOG.md` entry all state "13 new disposable-git-fixture tests."
  Counting actual added `def test_` lines via `git diff 1ca49a3..HEAD --
  tests/test_check_knowledge_base.py`, I find **11** new test functions
  (10 in `TestSnapshotCompleteness` + 1 in `TestSnapshotIntegrity`), not
  13. The tests themselves are real, well-targeted, and all pass — this
  is a miscount in the narrative text, not a shortfall in actual
  coverage. Noted for a trivial follow-up fix, not a blocker.

## 2. Restored citations

- Read `architecture/overview.md` and `architecture/context-graph-schema.md`
  directly. `first-party-source-symbols@v2#CL-FPSS-NNN`-style citations
  are present throughout both files; every one of the 8 captured
  assertions (`CL-FPSS-001` through `008`) is cited at least once across
  the two files (confirmed by `grep -oE "CL-FPSS-[0-9]+" ... | sort -u`),
  including the two newly-documented limitations (`CL-FPSS-007`/`008`).
- Spot-checked three citations against their backing files in full:
  `CL-FPSS-001` (`core.Ecosystem` vs. `source_symbols.Language`),
  `CL-FPSS-003` (five-state `SymbolIndexStatus`), `CL-FPSS-004`
  (occurrence-based identity / overload handling). In all three cases the
  architecture-doc prose accurately reflects the cited Claim's own
  `statement`/`examples` fields — content matches, not just a resolving
  link.

## 3. Corrected isolation verdict

- `planning/knowledge/first-party-source-symbols/isolation/isolation-evidence-inventory.md`
  states Track 2 as **UNMET** with real, structured reasoning (a
  dispatch-by-dispatch evidence inventory table, an explicit distinction
  between "honestly labelled" and "actually achieved," and a named,
  real boundary deviation found in one of six dispatches) — not a bare
  assertion.
- `planning/CONTEXT.md`: both the live "Current phase" narrative (lines
  83-93) and the "What was just completed" historical account (lines
  246-261) carry the correction — neither asserts a bare uncorrected
  "Track 2: PASS." Grep confirms no standalone "Track 2 ... PASS" line
  survives outside of text explicitly marked as what the *original*
  report said before correction.
- `planning/ROADMAP.md`'s Phase 79 row: corrected in place — now reads
  "Both audit reports' own 'Track 2: PASS' language was corrected by a
  fifth amendment the same day ... the corrected, final verdict is
  **Track 2: UNMET**."
- Both `_audit-phase-79.md` and `_audit-phase-79-reaudit.md` carry a
  **non-destructive correction notice at the top**, explicitly stating
  the corrected verdict and pointing to the isolation-evidence-inventory
  document, while leaving the original report text unedited below as a
  historical record. This is exactly the "correction notice plus
  unedited historical text" pattern required — not a bare uncorrected
  PASS claim.
- `isolation/boundary_check.py` is a real, inspectable script (reads
  original JSONL subagent transcripts, flags any absolute path outside
  a dispatch's assigned export directory). `isolation/boundary-check-output.txt`
  is real output (21 lines, concrete tool-call counts and one flagged
  scratch-sandbox path per dispatch) — not empty or a placeholder.
  `packet-assembly-access-log.txt` similarly lists ~30 concrete `Read`/
  `Glob` calls with real repository paths, consistent with the
  inventory's own claim of "two reads fall outside the stated scope."

## 4. Template usability exercise

- `planning/knowledge/first-party-source-symbols/template-usability-exercise/report.md`
  exists (234 lines) and describes a real adoption attempt: a
  step-by-step log of copying the template into an invented `tinytodo`
  project, a real README/LICENSE collision found and fixed, a real
  pytest-unavailable sandbox workaround, a genuine snapshot-freezing
  tension (uncommitted file vs. "freeze historical content") handled
  honestly (partial freeze, labelled `UNCOMMITTED`, not fabricated), and
  an explicit "was this more honest than a links-resolve check" section
  naming three concrete defect classes a link-checker could not have
  found. This is a substantive usability exercise, not a link check.
- Verified the `codecompass-template` clone still present in this
  session's own scratchpad
  (`.../scratchpad/codecompass-template`): `git log --oneline -3` shows
  `70f0a12` ("fix: warn against blindly overwriting README.md/LICENSE on
  adoption") on top of `8868ba9`/`76211e3`; `git status` clean; `git log
  origin/main..HEAD` empty and `git diff origin/main -- README.md` empty
  — the fix commit is genuinely pushed to the real
  `git@github.com:ctosullivan/codecompass-template.git` remote, not just
  committed locally. `git show 70f0a12 -- README.md` confirms the actual
  diff matches the report's own description (an explicit callout against
  blindly overwriting an adopting project's `README.md`/`LICENSE`).

## 5. ADR / CLAUDE.md / CHANGELOG / retro hygiene

- `decisions/0067-phase-79-post-implementation-corrections-are-a-new-adr-not-an-in-place-edit.md`
  exists, is substantive (Context/Decision/Alternatives/Consequences),
  and correctly defers technical detail to the plan's own §0 rather than
  duplicating it.
- `decisions/0066-*.md`: `git show 36986d3 -- decisions/0066-*.md` shows
  only a **6-line addition** (a "Post-implementation note" pointing to
  `0067`) — no edit to the ADR's existing four-revision content. No
  destructive rewrite.
- `CHANGELOG.md`: `grep -n "Phase 79"` shows exactly one `[Unreleased]`
  → `### Added` block (line 131) containing both the original Phase 79
  summary and a **"Fifth amendment, direct review of the delivered
  result"** paragraph appended to the same entry — extended, not
  duplicated into a second entry.
- Retro: `planning/retros/phase-79-clean-room-understanding-and-documentation-reconstruction.md`
  has a new `## Addendum: fifth amendment (2026-10-01, the day after
  \`done\`)` section (lines 141-207) with five substantive, generalized
  lessons (one per defect, plus the transcript-recoverability one) — not
  a stub.
- `CLAUDE.md`'s own L-070 sentence: `9c73589` ("project-rule(L-070):
  require a minimal-content edge-case test for any fail-closed
  validation mechanism") touches **only `CLAUDE.md`** (12 lines,
  11 insertions) — a dedicated, separate commit, not folded into an
  unrelated change, per §0.
- **Real, non-blocking gap found:** `CONTRIBUTING.md`'s own header note
  says "The two should stay conceptually identical — if you change one,
  check the other," and the `knowledge-curator`'s own filed record
  (`planning/v1-redefinition/proposed-governance-changes.md` §G,
  "Consequences if approved") explicitly states: *"CONTRIBUTING.md's
  mirrored 'plan before implementing' section gets the same addition in
  the same commit (existing decisions/0022/0030 precedent for keeping
  the two in sync)."* This did not happen: `9c73589`'s diff touches only
  `CLAUDE.md`; `CONTRIBUTING.md`'s "Plan before implementing" section
  still ends at "(Phase 55b — L-021.)" with no `L-070` sentence anywhere
  in the file. (Established precedent confirmed directly: `L-021`'s own
  landing commit `899449d` genuinely touched both `CLAUDE.md` and
  `CONTRIBUTING.md` together, exactly as this amendment's own governance
  record promised to repeat but didn't. Note `L-050`'s landing commit did
  *not* mirror `CONTRIBUTING.md` either, so this isn't an absolute,
  universal rule for every CLAUDE.md change — but it is a specific,
  written commitment this amendment's own paper trail made for this
  specific change and then didn't keep.) `CONTRIBUTING.md` is now
  silently out of sync with `CLAUDE.md` §1. Not a DoD-blocking condition
  (`CONTRIBUTING.md` sync is not one of §5's named conditions), but a
  real, concrete, checkable documentation-consistency gap worth a
  trivial follow-up commit.
- Learning triage: `L-070` through `L-074` all have recorded outcomes in
  `planning/learnings/promoted.md` (all five `promoted`, each with a
  concrete landing target and commit reference) — matches the retro
  addendum's five candidates exactly. `L-070`'s own landing was correctly
  gated on explicit user diff-approval before touching `CLAUDE.md`
  (`9dc1b77` files it `status: proposed, pending approval`; `9c73589`
  lands the CLAUDE.md edit; `b95a1f1` flips it to `promoted`) — consistent
  with established `L-021`/`L-050`/`L-065` precedent for this specific
  gate, modulo my own inability to directly witness the actual
  user-approval exchange (an inherent limitation of auditing after the
  fact, not evidence of a skipped step — the commit messages and the
  `proposed-governance-changes.md` §G status line are consistent with it
  having happened).

## 6. Full verification re-run

- `.venv/bin/python -m pytest -q` → **758 passed, 2 skipped** (205.52s),
  exit 0.
- `.venv/bin/ruff check .` → **All checks passed!**, exit 0.
- `.venv/bin/python scripts/check_user_docs.py --strict` → no findings,
  exit 0.
- `.venv/bin/python scripts/check_knowledge_base.py --strict` → 1
  informational finding (`knowledge-base-snapshot-current-divergence` for
  `CL-FPSS-007`, `snapshot-v1` vs. current `verified` status) — the same
  expected, non-blocking note both prior Phase 79 audits already
  identified; `strict=False`, exit 0.

## 7. Scope / protected-file check

- `git diff 1ca49a3..HEAD -- src/` → empty. Confirms "Explicitly not
  Priority B (no `src/codecompass/` change at all)" held.
- `git diff 1ca49a3..HEAD -- CLAUDE.md` → exactly the L-070 sentence
  addition, nothing else; no other `CLAUDE.md` drift.
- `git diff 1ca49a3..HEAD -- decisions/` → only `0066` (6-line pointer
  note) and the new `0067` file — no edit to any other ADR's original
  content.
- `pyproject.toml`'s new `ruff` `extend-exclude` entry (scoping out the
  preserved `tinytodo-after-adoption/` evidence tree, which is an
  invented project's own code, not this project's source) is a
  reasonable, disclosed, narrowly-targeted addition, not scope creep.
- The full 59-file diff is consistent with the plan's own §0 "Fifth
  revision" entry's four named corrections plus their natural
  closeout trail (learnings, retro addendum, ADR, CHANGELOG, agent-file
  updates for `L-071`/`L-072`/`L-073`/`L-074`) — no unexplained file
  touched.
- Phase 79's original `done` status on `planning/ROADMAP.md` is correctly
  *not* reopened or reversed by this amendment (confirmed: `git log
  --oneline 1ca49a3..HEAD -- planning/ROADMAP.md` shows only `4ca2d88`,
  which corrects the Track 2 narrative text in place — it does not touch
  the `done` status cell). This matches the plan's own explicit framing
  ("the phase's own prior terminal reconciliation ... is not reopened or
  reversed by this amendment").

---

## Verdicts

### Track 1 (workflow/template completion): **PASS WITH NON-BLOCKING OBSERVATIONS**

All four corrections are genuinely, substantively delivered and
independently re-verified: fail-closed snapshot validation confirmed
against my own disposable fixture (not just the test suite); citations
restored and content-matched; the isolation verdict corrected with real
new mechanical evidence and non-destructive correction notices on both
prior audit reports; a genuine downstream usability exercise replaced
the link-check, with its fix verified pushed to the real template
remote. Full suite (758 passed/2 skipped), `ruff`, and both strict
checker scripts all clean. ADR/CHANGELOG/retro/CLAUDE.md hygiene all
hold. Two non-blocking observations:

1. The "13 new disposable-git-fixture tests" figure in the commit
   message, plan §0, and `CHANGELOG.md` is a miscount — actual count is
   11. The tests themselves are real and all pass; only the narrative
   number is wrong. Trivial follow-up.
2. `CONTRIBUTING.md` was not updated to mirror `CLAUDE.md` §1's new
   `L-070` sentence, despite the `knowledge-curator`'s own filed record
   (`proposed-governance-changes.md` §G) explicitly committing to update
   it "in the same commit," and despite `CONTRIBUTING.md`'s own
   "if you change one, check the other" instruction and the directly
   comparable `L-021` precedent that did mirror both files together.
   `CONTRIBUTING.md`'s "Plan before implementing" section is now
   silently stale relative to `CLAUDE.md`. Not a named `CLAUDE.md` §5 DoD
   condition, so not blocking, but a real, concrete gap worth a small
   follow-up commit mirroring the same sentence into `CONTRIBUTING.md`.

### Track 2 (strict clean-room isolation validation): **UNMET** (unchanged, correctly reported)

This track's own expected, honest outcome. The fifth amendment's entire
point on this track was to correctly *report* UNMET rather than achieve
isolation — which it did, backed by genuinely new mechanical evidence
(the boundary-check script and its real output against all six original
pilot dispatches' own still-extant transcripts, finding one real,
previously-undetected boundary deviation) rather than merely relabelling
the same thin evidence. No gap found in this track's own honesty
requirement; nothing here is a defect to fix.

---

## What should be fixed before this amendment is considered fully closed (non-blocking, does not require re-audit)

1. Correct "13 new disposable-git-fixture tests" to "11" (or recount and
   use the accurate figure) in `CHANGELOG.md` and the plan's own §0
   "Fifth revision" entry 1. The commit message itself is historical and
   need not be rewritten.
2. Mirror the `L-070` sentence from `CLAUDE.md` §1 into `CONTRIBUTING.md`'s
   "Plan before implementing" section, in its own small commit, matching
   the `L-021` precedent and fulfilling the commitment already recorded
   in `proposed-governance-changes.md` §G.

Neither of these reopens Track 1's PASS or requires a fresh audit pass —
they are small, independently fixable follow-ups.

---

Relevant file paths (all absolute):
- `/home/cormac/projects/codecompass/scripts/check_knowledge_base.py`
- `/home/cormac/projects/codecompass/tests/test_check_knowledge_base.py`
- `/home/cormac/projects/codecompass/architecture/overview.md`
- `/home/cormac/projects/codecompass/architecture/context-graph-schema.md`
- `/home/cormac/projects/codecompass/planning/knowledge/first-party-source-symbols/isolation/isolation-evidence-inventory.md`
- `/home/cormac/projects/codecompass/planning/knowledge/first-party-source-symbols/isolation/boundary_check.py`
- `/home/cormac/projects/codecompass/planning/knowledge/first-party-source-symbols/isolation/boundary-check-output.txt`
- `/home/cormac/projects/codecompass/planning/knowledge/first-party-source-symbols/template-usability-exercise/report.md`
- `/home/cormac/projects/codecompass/decisions/0066-clean-room-reconstruction-needs-mechanical-isolation-and-independent-implementation-comparison.md`
- `/home/cormac/projects/codecompass/decisions/0067-phase-79-post-implementation-corrections-are-a-new-adr-not-an-in-place-edit.md`
- `/home/cormac/projects/codecompass/CHANGELOG.md`
- `/home/cormac/projects/codecompass/CLAUDE.md`
- `/home/cormac/projects/codecompass/CONTRIBUTING.md` (stale — see Observation 2)
- `/home/cormac/projects/codecompass/planning/CONTEXT.md`
- `/home/cormac/projects/codecompass/planning/ROADMAP.md`
- `/home/cormac/projects/codecompass/planning/retros/phase-79-clean-room-understanding-and-documentation-reconstruction.md`
- `/home/cormac/projects/codecompass/planning/retros/_audit-phase-79.md`
- `/home/cormac/projects/codecompass/planning/retros/_audit-phase-79-reaudit.md`
- `/home/cormac/projects/codecompass/planning/learnings/promoted.md`, `inbox.md`
- `/home/cormac/projects/codecompass/planning/v1-redefinition/proposed-governance-changes.md`

---

## Addendum: re-confirmation against `0e1c63a` (follow-up fix commit)

**Re-audited against:** `0e1c63a417ae1eed87a8bac7774383f413b0de2e`
("fix(phase-79): two non-blocking observations from the fifth-amendment
audit"), one commit on top of `b95a1f1` (the commit this report was
originally audited against above).

- `git diff b95a1f1..0e1c63a --stat` touches exactly four files:
  `CHANGELOG.md` (1 line), `CONTRIBUTING.md` (+10/-1),
  `planning/learnings/inbox.md` (1 line), and
  `planning/phase-79-clean-room-understanding-and-documentation-reconstruction.md`
  (1 line). No `src/`, `scripts/`, `tests/`, `decisions/`, `CLAUDE.md`,
  `planning/ROADMAP.md`, or `planning/CONTEXT.md` touched — genuinely
  scoped to fixing exactly the two named observations, no scope creep.
- **Observation 1 (test-count miscount) confirmed fixed:** all three
  prose occurrences of "13 new disposable-git-fixture tests" now read
  "11" — `CHANGELOG.md`, `planning/learnings/inbox.md`, and the phase
  plan file's own §0 "Fifth revision" entry 1. A corpus-wide grep for
  "13 new disposable-git-fixture" at the new HEAD returns matches only
  inside this audit report's own historical narrative text (lines 60,
  259, 289 above, describing the original finding) — correctly left
  unedited as a historical record, not live prose elsewhere.
- **Observation 2 (`CONTRIBUTING.md` mirroring) confirmed fixed:**
  `CONTRIBUTING.md`'s "Plan before implementing" section now carries a
  sentence conceptually identical to `CLAUDE.md` §1's `L-070` sentence
  (same fail-closed-validation / minimal-content-edge-case content,
  same "(Phase 79 fifth amendment — L-070.)" citation; only trivial
  phrasing difference consistent with `CONTRIBUTING.md`'s own stated
  purpose of restating `CLAUDE.md` rules for human contributors — e.g.
  "the plan's verification section" vs. "the 'Verification' section").
  `CLAUDE.md`'s own sentence (lines 32-42) is unchanged by this commit
  (not in the diff), confirming this was a pure one-way mirror fix, not
  a re-edit of the already-approved `CLAUDE.md` text.
- Re-ran `.venv/bin/python scripts/check_user_docs.py --strict` → no
  findings, exit 0. Re-ran
  `.venv/bin/python scripts/check_knowledge_base.py --strict` → 1
  informational finding (`knowledge-base-snapshot-current-divergence`,
  `CL-FPSS-007`), `strict=False`, exit 0 — identical, expected finding
  already noted in §6 above; no new or regressed findings.
- No `src/`, `scripts/`, or `tests/` file is touched by `0e1c63a`, so the
  full pytest/ruff/disposable-fixture technical verification from the
  original audit (§0, §6 above) does not need to be re-run; it still
  applies unchanged to this state.

**Conclusion:** the original Track 1 verdict —
**PASS WITH NON-BLOCKING OBSERVATIONS** — still applies, now against
`0e1c63a`. Both of the two observations that qualified it have been
genuinely and narrowly fixed, with no scope creep and no regression.
Track 2 remains **UNMET (correctly reported)**, unchanged, as this
commit touches none of Track 2's evidence. The phase is ready for
terminal `roadmap-context-curator` reconciliation.
