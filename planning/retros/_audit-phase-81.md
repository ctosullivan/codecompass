# Phase 81 — independent completion (DoD) audit

**Auditor**: `release-phase-auditor` (independent pass, read-only).
**Audited commit (HEAD at audit time)**: `4db620b7df86486c6dab8b4d9296f968efc38e58`
("chore(phase-81): learning triage -- promote L-085, retain L-084,
L-083 already covered").
**Range audited**: `d7a7b6f..4db620b` (10 commits: b72c709, e4bceef,
5c81abd, 8ed4296, f5a6195, 216e252, e74788f, 1af2cd2, 9e4fab4, 4db620b).
**Plan**: `planning/phase-81-intermediate-knowledge-layer.md` (amended
twice before implementation, both amendments preserved in place).
**Retro**: `planning/retros/phase-81-intermediate-knowledge-layer.md`.

## Verdict

**PASS WITH NON-BLOCKING OBSERVATIONS**

Every condition in `CLAUDE.md` §5 genuinely holds against the real,
current state of the repository at the audited commit. Two small,
genuinely non-blocking factual-accuracy findings below should be fixed
in a trivial follow-up commit (or at the start of the next phase) but do
not misstate the mechanism's existence, behaviour, or safety properties,
and do not require reopening any of this phase's actual design or code.

## What I re-ran myself (not trusted from the session's own report)

1. **Full test suite**: `.venv/bin/python -m pytest -q` → **810 passed,
   2 skipped, 0 failed** (208.95s). No failures, no new skips introduced
   by this phase (the 2 skips are pre-existing and unrelated).
2. **Lint**: `.venv/bin/python -m ruff check .` → **All checks passed.**
3. **`scripts/check_user_docs.py --strict`** → **no findings.**
4. **`scripts/check_knowledge_base.py --strict`** → **1 finding**,
   exactly the expected pre-existing informational
   `knowledge-base-snapshot-current-divergence` on `CL-FPSS-007`
   (unrelated to Phase 81, already known-and-healthy per its own
   message). No Phase-81-caused finding.

## Plan §16.1/§16.2 verification — spot-checked, not just counted

- `tests/test_knowledge_intermediate.py` has **30** test functions
  (matches the file's own scope: the original 26 from §16.1's list plus
  4 added by the `phase-brief.md` fix in `1af2cd2`). I read the no-op
  round-trip, projection-only-edit, canonical-only-change,
  concurrent-conflict, apply-time-race, presentation-independence
  (including the "two different presentations survive independently"
  case), no-fabricated-observation, and CLI tests in full. Every one
  asserts real file-byte state (`yaml_after == _CLAIM` byte-identical,
  direct reads of `overview.md`/`README.md` after mutation, explicit
  `fabricated = [rid for rid in records if rid.startswith(("OBS-",
  "EV-"))]` checks), not merely "the call didn't raise." These are
  genuine behavioural assertions, matching what each test's own name
  claims.
- `tests/test_check_knowledge_base.py`'s two new check-specific classes
  (`check_requirement_cites_approved_decision`,
  `check_anchor_integrity`) total **47** tests project-wide (matches the
  retro's own count exactly) and include the required edge cases per
  `CLAUDE.md` §1's own amendments: proposed/rejected/superseded Decision
  (not just "missing"), cross-directory fallback-map resolution,
  dangling-reference/missing-field **not double-reported**, and a
  dedicated `test_real_repository_satisfies_this_check`/
  `test_real_repository_has_no_dangling_anchors` regression against the
  live corpus. Both new checks are genuinely wired into the main
  `_CHECKS` dispatch list in `scripts/check_knowledge_base.py` (not just
  defined and unit-tested in isolation) — confirmed by direct grep.
- Both new `assertion_kind` enum values (`workflow`, `constraint`) are
  genuinely present in `_OPTIONAL_ENUM_FIELDS["claim"]["assertion_kind"]`
  in the live validator, not only described in the plan.
- `codecompass knowledge --help` (run directly against the shipped CLI)
  shows exactly the four subcommands the plan's §11 specifies
  (`render`, `select-candidates`, `apply`, `status`) with docstrings
  matching the plan's own stage descriptions almost verbatim.
- `knowledge_intermediate.py` contains no Anthropic/model call of any
  kind (confirmed by grep) — Stage 1/4 (detect/render) are genuinely
  mechanical as claimed; the only judgment stage (Stage 2, review) lives
  outside this module, as designed.

## Drift-audit findings (9e4fab4, 1af2cd2) — independently re-verified fixed

I did not trust the commit messages' own claims. Re-read the real files
against the real code:

- `docs/cli-reference.md` — now documents `knowledge
  render|select-candidates|apply|status` in full, with a worked example
  referencing the real `hledger-depth` manifest path, and the top
  summary line correctly lists it among implemented commands. Confirmed
  by direct read.
- `architecture/overview.md` (~line 705) — no longer claims
  `CONTRIBUTING.md` is excluded from `spec_docs.py`'s scan; now correctly
  states it "is scanned like any other spec doc now." Confirmed against
  the real `src/codecompass/spec_docs.py`: `CONTRIBUTING.md` is present
  in `_DEFAULT_GLOBS` and absent from `_EXCLUDED_ROOT_NAMES`, and a live
  `spec_docs.scan_spec_docs(Path("."))` call actually returns it.
- `architecture/module-map.md` — `cli.py` (1,662 lines) and
  `knowledge_intermediate.py` (1,047 lines) line counts verified via
  `wc -l` against the real files: **exact match**, including after the
  later `phase-brief.md` addition (which landed before this drift-fix
  commit, so the numbers already account for it).
- `docs/codecompass-knowledge-workflow.md` — re-read in full. The
  render→detect→review→apply→render-again sequence is internally
  consistent with the actual four-stage pipeline (render is correctly
  named as the step that produces the editable projection in the first
  place); the `MIXED` provenance value is present and consistent with
  `derive_provenance_label`'s real implementation (confirmed: `"MIXED"`
  literal appears in `knowledge_intermediate.py` at the exact ambiguous
  `directly_stated` branch the docs describe).
- `ai-docs/README.md` — now has a `knowledge render|...` capability
  bullet linking the workflow guide. Confirmed present.
- `README.md` doc index — links `docs/codecompass-knowledge-workflow.md`.
  Confirmed present, in addition to the pre-existing inline link.

## Dogfood artifacts — verified real, not merely narrated

- `planning/knowledge/codecompass-domain/` has **186** `.yaml` records
  (claimed "182+") — confirmed by direct count.
- `CL-KNOW-001`/`DE-KNOW-001`/`EV-KNOW-001`/`OBS-KNOW-001` read in full:
  internally consistent (Observation describes a real, reproducible
  action that was actually performed — CLI invocations and direct file
  reads — Evidence summarizes it faithfully, Derivation cites both,
  Claim correctly uses `basis: observed_behaviour`/`status: supported`,
  not fabricated or hand-waved). No field contradicts another record in
  the same chain.
- `README.md`'s `<!-- codecompass-grounded-by: CL-KNOW-001 -->` marker
  was resolved against the **real shipped code path**, not assumed:
  ```
  ki.find_grounded_doc_regions(Path('.'), 'CL-KNOW-001')
  ```
  returns exactly one hit, in `README.md`, containing the grounded
  prose. `codecompass knowledge status codecompass-domain` (the real CLI,
  invoked directly) reports `README.md: grounded regions: 1`,
  `CONTRIBUTING.md: grounded regions: 0` — consistent with the plan's own
  §18 scope decision that `CONTRIBUTING.md`'s live grounding dogfood is
  explicitly deferred, not silently skipped.
- `planning/knowledge/hledger-depth/CL-HLEDGERDEPTH-002.yaml` and its
  matching `reconciliation/20261007T054415Z.toml` manifest: read in
  full. `status: proposed`, `basis: proposed_policy`,
  `supporting_evidence: []`, `contradicting_evidence: []`,
  `derived_by: "external:unknown"` — exactly matching the retro's claim
  of "zero fabricated Observation/Evidence records," and consistent with
  an honestly-unsupported external candidate, never silently promoted.
  This slug's pre-existing `CL-DEPTH-001.yaml` vs. the new
  `CL-HLEDGERDEPTH-002.yaml` id-token mismatch is real and present on
  disk — confirms the retro's own disclosed `_next_id` cosmetic finding
  (`L-084`) is a genuine, not invented, observation.
- The slug passes `check_knowledge_base.py --strict` with zero findings
  of its own (only the unrelated pre-existing `CL-FPSS-007` informational
  finding appears project-wide).

## Protected-file / provenance checks

- `git diff d7a7b6f..HEAD -- CLAUDE.md` → **empty**. `CLAUDE.md` was
  never touched by this phase.
- `git diff d7a7b6f..HEAD -- decisions/` → only two new files added
  (`0071`, `0072`); no existing ADR's original content was edited.
- All ten commit messages (`b72c709` through `4db620b`) checked directly
  for `claude|anthropic|co-authored|generated` (case-insensitive) — the
  only matches are ordinary prose references to "Claude Code" as a
  third-party AI tool users might edit Markdown with, and to
  `CLAUDE.md` the governing file. **No AI-attribution trailer appears in
  any of the ten commits.**
- Changed-file list (`git diff --name-only d7a7b6f..HEAD`, 39 files)
  matches the plan's own §19 "Files expected to change" list, plus the
  standard closeout set (`CHANGELOG.md`, `planning/CONTEXT.md`,
  `planning/ROADMAP.md`, `planning/retros/*`, `planning/learnings/*`,
  `planning/agent-led-workflow.md`) and the drift-audit's own corrective
  set (`docs/cli-reference.md`, `architecture/overview.md`,
  `architecture/module-map.md`, `ai-docs/README.md` — all legitimately
  "applicable `architecture`/`docs` updates" under §2, not scope creep).
  No file outside this union was touched.

## Learning triage — genuinely happened, artifact is coherent

`4db620b` shows real `knowledge-curator` triage output, not a mechanical
rubber stamp: L-083 correctly marked "already covered" by existing
regression tests (verified: the hash-consistency and regex bugs are in
fact pinned by `TestNoOpRoundTrip`/`TestExplicitDocumentGrounding` et
al.); L-084 retained with an explicit, reasoned "wait for a second data
point" rationale matching the project's own stated precedent
(`L-082`); L-085 promoted with a real destination. I read the landed
paragraph in `planning/agent-led-workflow.md` step 5 in context — it
sits naturally after the existing `L-069` paragraph, names the specific
Phase 81 bug precisely, and states the generalizable procedural rule
clearly. `planning/learnings/promoted.md` carries matching pointer lines
for both L-083 and L-085; L-084 correctly has no `promoted.md` line
since its status is `retained`, not `promoted`.

## ROADMAP.md / CONTEXT.md — accurately describe current (not-yet-done) state

- `planning/ROADMAP.md` row 81: status is **`planned`** (not `done`) —
  correct; flipping it is explicitly this audit's own gate to authorize,
  not something already claimed done.
- `planning/CONTEXT.md`'s "Next concrete step" explicitly names the
  remaining closeout sequence (drift audit → learning triage →
  independent completion audit → terminal `roadmap-context-curator`
  reconciliation) as not-yet-complete at the time it was written, and
  correctly flags the `codecompass-template` push as an outstanding,
  non-blocking maintainer action. Both read as accurate for the
  commit they describe.

## `codecompass-template` sibling-repo commit

`/home/cormac/projects/codecompass-template`, commit `a429f04` ("feat:
lightweight optional-intermediate-knowledge/ directory"), confirmed
**committed locally, not pushed** (`git status`: "ahead of 'origin/main'
by 1 commit"). Read `optional-intermediate-knowledge/README.md` and
`worked-example.md` in full: accurate against the real shipped CLI
(command names, flags, record shape, workflow steps all match
`codecompass knowledge --help`'s real output), clearly scoped as
optional/separate from the template's existing `planning/knowledge/`
lessons log per the plan's own §0.4/§15.1 decision, no broken links or
invented commands. A reasonable, non-broken addition. Cannot verify the
push itself (no credentials in this environment, as disclosed) — this is
an honest, correctly-flagged outstanding action for the maintainer, not
a Phase 81 defect.

## Non-blocking findings (fix recommended, does not block `done`)

1. **Stale test-count claim in three places.** `CHANGELOG.md`'s Phase 81
   entry, `planning/knowledge/codecompass-domain/EV-KNOW-001.yaml`, and
   `OBS-KNOW-001.yaml` all say "26" tests/"26 passing disposable-fixture
   tests." At the time `e74788f` (retro/changelog/closeout) was written,
   this was accurate (confirmed: `git show e74788f:tests/test_knowledge_intermediate.py`
   has exactly 26 `def test_` matches). `1af2cd2`, landed immediately
   after, added 4 more tests for `phase-brief.md` (30 total today), and
   neither `1af2cd2` nor the later drift-fix commit (`9e4fab4`) updated
   this specific numeric claim in `CHANGELOG.md` or in the two dogfood
   knowledge records that cite it as their own evidentiary basis. This
   is a minor, non-substantive drift (a count, not a behavioural claim —
   the underlying claim "a real, tested mechanism exists, covering these
   named safety properties" remains fully true and independently
   reproducible), but it is worth noting precisely because `OBS-KNOW-001`/
   `EV-KNOW-001` are this phase's own flagship example of
   `basis: observed_behaviour` grounding — the one place in this entire
   phase where internal accuracy of an evidentiary record matters most on
   principle. Recommend a one-line follow-up fix (26 → 30) in a trivial
   subsequent commit; does not require reopening the phase.
2. **§16.2's own 8 named dogfood scenarios are not individually
   itemized as run/deferred in the retro.** The retro documents real
   execution of what maps onto scenario 1 (external knowledge
   refinement, landing honestly at `status: proposed` rather than
   `status: supported`, with the shortfall explicitly disclosed) and
   implicitly scenario 6/7 (README grounding, phase promotion via the
   `codecompass-domain` pilot), while scenarios 2-5 and 8 are covered
   only by the deterministic unit-test suite (itself fully adequate
   evidence for the underlying property, per §16.1) rather than a
   separate real-Ledgerkit run each. This reconciles cleanly against the
   plan's own §18 "Scope discipline" section, which narrows the
   mandatory bar to "[the phase knowledge workflow] validated once, end
   to end, against a real Ledgerkit task" plus "one real semantic-edit
   reconciliation exercised against a grounded README region" — both of
   which did happen for real — rather than requiring all 8 of §16.2's
   illustrative scenarios to each be run against a live Ledgerkit clone.
   Scenario 8 specifically (`boundary_check.py` against the Stage 2
   review dispatch) was never run or mentioned; this is consistent with
   — not a new instance of — the already-disclosed, already-accepted
   `best-effort` isolation limitation the plan's own Risks section (§0.4)
   says this phase does not attempt to close. Not blocking, but worth a
   one-line retro addendum next time this area is touched, naming which
   of the 8 scenarios were exercised live vs. covered only by unit tests,
   so a future reader doesn't have to reconstruct this mapping themselves.

## Conclusion

Code implemented and genuinely wired in (not just defined-but-uncalled);
`docs/`/`architecture/`/`decisions/` updated accurately, independently
re-verified against real current code behaviour, not assumed from commit
messages; an independent `docs-reconstructor` drift audit ran mid-phase,
found real drift, and every finding was genuinely fixed (re-verified
directly, not trusted); `CHANGELOG.md` carries one correctly-scoped
Phase-81-only entry (with the stale count noted above); `planning/CONTEXT.md`
and `planning/ROADMAP.md` accurately reflect that the phase is implemented
and dogfooded but not yet marked `done`; a substantive, non-stub retro
exists; `knowledge-curator` triage genuinely happened with a coherent
promoted artifact; no protected-file drift and no AI attribution in any
commit; the changed-file list matches the plan's own scope with no creep;
the sibling-repo template commit is real and reasonable, honestly flagged
as unpushed.

**This audit authorizes the terminal `roadmap-context-curator`
reconciliation** (flipping `planning/ROADMAP.md`'s Phase 81 row to
`done`, overwriting `planning/CONTEXT.md`'s current-state section, and
updating the phase plan file's own Status line) as the one explicit,
narrow exemption `CLAUDE.md` §5 describes — that commit itself is not
"audited scope" and does not require a fresh audit pass, provided it
touches nothing beyond those three named targets.

---

# Re-audit after commit 08a5a50 (fresh pass per CLAUDE.md §5)

**Auditor**: `release-phase-auditor` (independent pass, read-only).
**Trigger**: `08a5a509c4ee53b138088ee2b5d00d74a9e84f9a`
("fix(phase-81): correct stale test-count claim (26 -> 30)") landed
after the original audit's `4db620b` pass, touching exactly the three
files that pass's own non-blocking finding #1 named. Per `CLAUDE.md` §5,
any commit after an auditor's pass that touches audited scope voids that
pass and requires a fresh one before the terminal `roadmap-context-curator`
reconciliation can happen. This is that fresh pass.
**Audited commit (HEAD at re-audit time)**: `08a5a50`.
**Scope of this pass**: fast confirmatory re-pass, not a repeat of the
full first audit (per explicit instruction) — verifies the new commit
does only what it claims, re-confirms the corrected count is actually
correct, and re-runs the full test suite / lint / both doc checkers
against current HEAD since the tree changed.

## What I checked

1. **`git show 08a5a50` read in full.** Diff touches exactly three files
   — `CHANGELOG.md`, `planning/knowledge/codecompass-domain/EV-KNOW-001.yaml`,
   `planning/knowledge/codecompass-domain/OBS-KNOW-001.yaml` — 3 insertions,
   3 deletions, one line changed per file, each changing the digit string
   "26" to "30" in a test-count prose claim. `git show --stat` confirms no
   other file touched. No unrelated edits smuggled in.
2. **Verified the new "30" is actually correct**, not just internally
   consistent with itself: counted `def test_` occurrences in
   `tests/test_knowledge_intermediate.py` directly (`grep -c`) — **30**,
   matching both the two numeric-literal spots fixed and the earlier
   audit's own independent count of this same file.
3. **Confirmed no other stale "26" remains** in the three touched files
   or elsewhere in `CHANGELOG.md` that should have been part of this fix:
   `grep -n "26" CHANGELOG.md` shows only unrelated hits (years like
   "2026-10-02", "Phase 26/27" references, "~2449 lines... to ~126") —
   none is the fixed claim re-appearing stale elsewhere. `EV-KNOW-001.yaml`
   and `OBS-KNOW-001.yaml` now contain no remaining "26" digit-string at
   all (only an unrelated ISO-timestamp year "2026" in `OBS-KNOW-001.yaml`,
   not a test count).
4. **Full test suite re-run against current HEAD**: `.venv/bin/python -m
   pytest -q` → **810 passed, 2 skipped, 0 failed** (207.95s) — identical
   result to the original pass; this commit is docs/data-only and
   correctly caused zero test-outcome change.
5. **Lint re-run**: `.venv/bin/python -m ruff check .` → **All checks
   passed.**
6. **`scripts/check_user_docs.py --strict`** → **no findings.**
7. **`scripts/check_knowledge_base.py --strict`** → **1 finding**, the
   same pre-existing, already-known-healthy informational
   `knowledge-base-snapshot-current-divergence` on `CL-FPSS-007`
   (unrelated to Phase 81) as the original pass found. No new finding
   introduced by the YAML edits — confirms the two touched knowledge
   records remain schema-valid and internally consistent after the edit.
8. **Changed-file scope since the previously-audited commit**:
   `git diff 4db620b..HEAD --name-only` → exactly the same three files
   `git show 08a5a50` reported. Nothing else moved since the original
   audit's commit.
9. **No AI-attribution trailer** in `08a5a50`'s commit message (checked
   directly).
10. Re-confirmed the original audit's two non-blocking findings:
    finding #1 (stale test count) is now resolved by this commit;
    finding #2 (§16.2 scenario itemization in the retro) was not touched
    by this commit and remains exactly as the original audit described
    it — still non-blocking, still not requiring reopening the phase.

I did not re-run the full first-pass audit (ADR checks, grounding
verification, learning-triage review, dogfood-artifact re-reads,
protected-file diff, etc.) since this commit gives no reason to doubt any
of those prior findings — it touches none of the files or mechanisms
those checks covered.

## Verdict

**PASS WITH NON-BLOCKING OBSERVATIONS**

Commit `08a5a50` genuinely and *only* does what it claims: corrects a
stale "26" to the actually-correct "30" in exactly the three places the
original audit named, and nowhere else. The new count is independently
verified correct against the real test file. The full test suite, lint,
and both doc checkers all pass identically to the original audit's run,
confirming the tree's behavioural state is unchanged by this doc-only
fix. The original audit's sole other non-blocking finding (§16.2 scenario
itemization) is untouched and still stands as a non-blocking observation
for a future retro addendum, not a blocker.

This re-audit supersedes the original `4db620b`-scoped pass for the
purpose of CLAUDE.md §5's gate. **This audit authorizes the terminal
`roadmap-context-curator` reconciliation** (flipping `planning/ROADMAP.md`'s
Phase 81 row to `done`, overwriting `planning/CONTEXT.md`'s current-state
section, and updating the phase plan file's own Status line) as the one
explicit, narrow exemption `CLAUDE.md` §5 describes — that commit itself
is not "audited scope" and does not require a further fresh audit pass,
provided it touches nothing beyond those three named targets.
