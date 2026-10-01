# Independent completion audit: Phase 79's sixth amendment (`decisions/0068`)

**Auditor:** `release-phase-auditor` (independent, read-only pass).
**Audited against:** HEAD `9982d22` (`chore(phase-79): mark L-075 promoted
after user-approved CLAUDE.md landing; mirror into CONTRIBUTING.md`).
**Amendment range:** `1e7d3d5` (fifth amendment's own final closeout) ..
`9982d22` (8 commits, 61 files changed per `git diff --stat`).

This is a direct-review correction pass on the fifth amendment's own
already-reconciled result — the user independently reproduced three
further defects and asked for corrections without another planning
round-trip. Phase 79 itself remains `done`; this amendment corrects its
delivered result again, per the same append-only-ADR reasoning
`decisions/0067` established and `decisions/0068` reapplies.

## Scope note on `planning/CONTEXT.md` / `planning/ROADMAP.md`

Neither file mentions the sixth amendment anywhere (`git log -p
1e7d3d5..HEAD -- planning/CONTEXT.md` is empty; `grep -n "0068" planning/ROADMAP.md`
finds nothing). **This is not treated as a finding against this audit.**
The plan file's own §0 "Sixth revision" entry explicitly names the
expected sequence: "a fresh `release-phase-auditor` pass against this
amendment's own final commit, then `roadmap-context-curator`
reconciliation updating `planning/ROADMAP.md`'s Phase 79 row,
`planning/CONTEXT.md`'s current-state section, and this file's own
Status line to reflect the amendment's own completion" — identical to
how the fifth amendment's own terminal reconciliation (`8911be1`)
happened only after that amendment's own audit passed. `CLAUDE.md` §5's
own named exemption covers exactly this: the terminal
`roadmap-context-curator` reconciliation commit is not "audited scope"
since the audit exists to authorize it. **This audit's PASS verdict below
is what authorizes that terminal commit — it has not yet happened and
should follow next**, updating `ROADMAP.md`'s Phase 79 narrative,
`CONTEXT.md`'s current-state section, and the plan file's own Status
line, per the fifth amendment's own precedent.

---

## Correction 1 — nested snapshot-entry validation gaps closed

**Re-ran directly, did not trust the report.**

- `_validate_nested_entries` (scripts/check_knowledge_base.py:604-682) and
  the new `knowledge-base-snapshot-kind-mismatch` finding
  (line 673) exist and are wired into `check_snapshot_completeness`'s own
  Evidence/Derivation closure logic (lines 884, 916) — closure now uses
  `_validate_nested_entries`'s returned `valid_ids` set, not raw dict
  keys.
- `.venv/bin/python -m pytest tests/test_check_knowledge_base.py -v`:
  **31 passed**, including all 6 `TestNestedEntryValidation` tests
  (baseline-complete-passes, scalar-in-place-of-evidence-table,
  evidence-identity-swap, derivation-scalar-in-place-of-table,
  derivation-identity-swap, kind-mismatch) — all pass.
- **Independent throwaway fixture** (per `CLAUDE.md` §1's `L-070`/`L-075`
  rules this very amendment landed), built fresh, testing two shapes
  *not* in the committed test file:
  - An **empty-dict `{}`** nested `supporting_evidence` entry (not a
    scalar, not a correctly-shaped-but-mismatched table — just `{}`).
    Result: `check_snapshot_completeness` → 1
    `knowledge-base-snapshot-incomplete-closure` finding;
    `check_snapshot_historical_integrity` → 1
    `knowledge-base-snapshot-incomplete-entry` finding (the dict is
    yielded by `_iter_snapshot_entries` since it is still a dict, then
    caught by the missing `path`/`repository_revision`/`content_hash`
    check). No silent pass, no crash.
  - A **list `["EV-TEST-001"]`** standing in for the entire
    `supporting_evidence` sub-table (not a per-entry malformation, a
    whole-table-shape malformation). Result: `check_snapshot_completeness`
    → `knowledge-base-snapshot-malformed-structure` ("must be a table,
    got list") **plus** the resulting
    `knowledge-base-snapshot-incomplete-closure` finding. No silent pass,
    no crash.
  - Both results independently confirm the fix generalizes beyond the
    two attack shapes the committed tests exercise, not merely passing
    its own named scenarios.

**Verdict: PASS.**

## Correction 2 — false conceptual claim corrected

Read `planning/knowledge/first-party-source-symbols/template-usability-exercise/corrections/task-ids-reproduction.md`
in full, then independently re-ran its central reproduction directly
against the real, unmodified
`template-usability-exercise/tinytodo-after-adoption/src/tinytodo.py`
(fresh disposable directory, `add("first")`, `add("second")`,
`delete(2)`, `add("third")`):

```
new task: Task(id=2, description='third', done=False)
reused id-2 == True
all tasks: [(1, 'first'), (2, 'third')]
```

This exactly matches the correction file's own reported output — the new
task reused id 2 (the just-deleted id) while task 1 remained live and the
list was never emptied, directly falsifying the original "never reused"
claim.

Checked all three affected files plus the snapshot sidecar:

- `planning/knowledge/assertions/task-ids-001.md` — dated correction
  notice at the top (2026-10-01, Phase 79 sixth amendment), original
  Statement/Evidence/Counterexamples sections preserved unedited below a
  `---` separator, explicitly marked as "preserved unedited as the
  historical record."
- `docs/task-ids.md` — same pattern: dated correction notice at top,
  original "The guarantee"/"The limit" sections preserved below.
- `decisions/0001-task-ids-are-never-reused.md` — correction inserted
  inline in the Decision section, original incorrect paragraph preserved
  immediately above/below the notice, Status line updated to flag the
  factual correction without reversing the ADR's own title/intent.
- `planning/knowledge/snapshots/task-ids@v1.toml` — correction comment
  header added, sidecar left unedited as historical freeze (consistent
  with its own pre-existing, disclosed `UNCOMMITTED` limitation — this
  file was never claimed to be re-frozen).

All four files are dated, preserve original text, and are internally
consistent with each other and with the independently-reproduced reality.

**Verdict: PASS.**

## Correction 3 — complete, commit-permitting exercise

```
$ git bundle verify planning/knowledge/first-party-source-symbols/template-usability-exercise-2/tinytodo2-full-history.bundle
...is okay
The bundle contains these 2 refs: refs/heads/main, HEAD (6c9331e...)
The bundle records a complete history.
```

Cloned the bundle to a scratch location (`git clone` the bundle file
directly — not a path reference, a real `.bundle` artifact):

- `git log --oneline` → **13 commits**, exactly as claimed, from
  `b6a1bb5` ("initial tinytodo2 project...") through `6c9331e` ("add
  isolation evidence and honest per-scope verdicts for this exercise").
- `git log --all -p | grep -i UNCOMMITTED` → only two hits, both prose
  *confirming the opposite* ("all via real git commits, none left
  `UNCOMMITTED`"; "freeze snapshot id-reuse@v1 (fully committed, real
  historical hashes -- not UNCOMMITTED)") — no record actually carries an
  `UNCOMMITTED` state marker.
- Final `src/tinytodo.py` has a real, working fix: a persisted `next_id`
  high-water-mark counter replacing the buggy `max(current ids) + 1`
  recomputation, with an honest, disclosed legacy-migration limitation
  (a pre-fix bare-list store restarts the counter at 1 rather than
  guessing a prior high-water mark).
- `.venv/bin/python -m pytest tests/` from the cloned bundle (using this
  repo's own `.venv`): **5 passed** — the original two tests plus three
  new ones (`test_deleting_the_current_maximum_id_does_not_reuse_it`,
  `test_persisted_counter_survives_a_second_max_delete_cycle`,
  `test_counter_is_durable_across_a_fresh_process_reload`), directly
  exercising the case the original exercise's narrower test missed.
- Spot-checked `planning/knowledge/isolation/isolation-summary.md` and
  `planning/knowledge/propagation-deltas.md` inside the clone: both are
  substantive, not stubs. The isolation summary honestly reconfirms
  **Track 2: UNMET** even within this fresh exercise's own final state
  ("Honest, verified best-effort compliance is not the same claim as
  strict isolation having been achieved"). The propagation-deltas report
  documents a real three-step mechanical demonstration (historical
  integrity unaffected → current divergence detected on the real source
  fix → both derived outputs — `docs/id-reuse.md` and
  `context-packet-fix-id-reuse.md` — correctly flagged `needs
  reassessment` through the one shared snapshot foundation), with an
  explicit, honest "what this does not do" scope boundary.

**One trivial non-blocking observation**: the bundle's own git history
tracks two compiled bytecode cache files
(`src/__pycache__/tinytodo.cpython-313.pyc`,
`tests/__pycache__/test_tinytodo.cpython-313-pytest-9.1.1.pyc`),
introduced in two of the 13 commits. The template's own `.gitignore`
explicitly leaves language-specific ignores (including `__pycache__/`)
to the adopter rather than assuming one — so this is a real, minor
hygiene slip in the exercise's own history, not a defect in the template
itself, and it does not affect test correctness, the fix's validity, or
any of the three corrections' own claims. Does not block PASS.

**Verdict: PASS WITH ONE NON-BLOCKING OBSERVATION** (as above).

---

## Cross-cutting checks

- **`decisions/0067` left unedited in substance**: confirmed by direct
  diff — only a 7-line "Post-implementation note" inserted under Status,
  pointing to `decisions/0068`; the rest of the file (Context, Decision,
  Alternatives, Consequences) is byte-identical to before. Same pattern
  as `0066`→`0067`.
- **`CHANGELOG.md`'s Phase 79 entry extended, not duplicated**: confirmed
  — the sixth amendment's description is appended as a new paragraph
  inside the *same* `### Added` → `- **Phase 79**` bullet that already
  carried the original delivery and the fifth-amendment paragraph; no
  second `Phase 79` bullet exists anywhere in the file.
- **Retro has a new "Addendum 2" section**: confirmed —
  `planning/retros/phase-79-clean-room-understanding-and-documentation-reconstruction.md`
  has both "Addendum: fifth amendment" (line 141) and "Addendum 2: sixth
  amendment" (line 208), the latter substantive (three concrete lessons,
  not a stub) plus a "Governing-ADR lineage note" discussing the
  `0066`→`0067`→`0068` pattern.
- **`CLAUDE.md`'s `L-075` sentence landed in its own dedicated commit**:
  confirmed — commit `6dd1b31` ("project-rule(L-075): a fail-closed
  check's own verification must cover depth, not only scope") touches
  only `CLAUDE.md` (10 lines, 1 file). The prior commit
  (`94410c5`) and the following commit (`9982d22`) are both separate,
  non-overlapping changes (learnings-inbox status updates, then the
  `promoted.md`/`CONTRIBUTING.md` mirror). Diff itself is exactly the
  one sentence quoted in `planning/learnings/inbox.md`'s own
  `promoted_to` field — no unrelated drift.
- **Mirrored in `CONTRIBUTING.md`**: confirmed — commit `9982d22`'s diff
  shows the identical sentence added to `CONTRIBUTING.md` in the same
  commit that flips `L-075`'s inbox status to `promoted` and appends it
  to `planning/learnings/promoted.md`.
- **Learnings triage complete**: `L-075` (project-rule, promoted to
  `CLAUDE.md` §1 + `CONTRIBUTING.md`), `L-076` (scoped-rule, promoted to
  `.claude/agents/context-researcher.md` step 2 — confirmed landed by
  direct diff), `L-077` (workflow, retained, cross-referenced with
  `L-076`), `L-078` (workflow, promoted to
  `planning/v1-redefinition/agent-led-development.md` §1 — confirmed
  landed by direct diff). All four have full curation notes with
  evidence citations, duplicate/merge checks, and explicit outcomes.
  `planning/v1-redefinition/proposed-governance-changes.md` §H records
  `L-075`'s own proposed-diff/approval trail consistent with `CLAUDE.md`
  §0's protected-file process.
- **No protected-file drift**: `CLAUDE.md`'s only change across the whole
  amendment range is the single `L-075` sentence (confirmed by full
  `git diff 1e7d3d5..HEAD -- CLAUDE.md`), user-approved per the inbox
  entry and the retro. No ADR's original content was edited — `0067`
  only gained a pointer note (above); `0068` is new.
- **Changed-file list matches plan scope**: `git diff 1e7d3d5..HEAD --stat`
  shows 61 files touched. All map cleanly to the plan's §0 "Sixth
  revision" entry's three corrections (check_knowledge_base.py + its
  tests; the tinytodo-after-adoption correction files; the full
  template-usability-exercise-2 tree + bundle) plus two legitimate ripple
  fixes: `pyproject.toml` (ruff `extend-exclude` entry for the new
  exercise-2 tree, matching the fifth amendment's own existing pattern
  for exercise-1) and `docs/domain/concepts/claim.md` (a line-number
  citation fix, `419-449`→`427-457`, caused by
  `check_knowledge_base.py` growing by the new validation code —
  verified the new line numbers are correct against the actual file).
  No file outside this footprint was touched. No scope creep.
- **Full test suite**: `.venv/bin/python -m pytest -q` — **764 passed, 2
  skipped** (both skips are pre-existing, environment-dependent
  `npm`/`cargo`/`stack`-not-installed markers, unrelated to this
  amendment), run twice with identical results.
- **`ruff check .`**: **All checks passed.**
- **`python scripts/check_user_docs.py --strict`**: **no findings.**
- **`python scripts/check_knowledge_base.py --strict`**: **1 finding**,
  `knowledge-base-snapshot-current-divergence` (severity `info`, exit
  code 0 — non-blocking), reporting `CL-FPSS-007`'s current status
  (`verified`) differing from its snapshot-frozen status (`supported`) —
  explicitly described by the finding's own message as "expected and
  healthy if this is a legitimate supersession" (it is: a lifecycle
  status progression, pre-existing, unrelated to this amendment's three
  corrections). Does not block.

---

## Verdicts

**Track 1 (workflow/template completion): PASS WITH NON-BLOCKING OBSERVATIONS.**

All three corrections independently re-verified to genuinely close the
reported gaps, using fresh, independent checks beyond what the committed
test suite already covers (a novel fixture shape for correction 1; a
from-scratch reproduction for correction 2; a real bundle clone + test
run for correction 3). Process hygiene (ADR append-only, changelog,
retro, learnings triage, dedicated CLAUDE.md commit + CONTRIBUTING.md
mirror, no scope creep) all hold. The one non-blocking observation is the
two tracked `.pyc` files inside the exercise-2 bundle's own history — a
trivial artifact-hygiene slip in a disposable downstream exercise, not a
defect in the corrections themselves or in CodeCompass's own source.

**Track 2 (strict clean-room isolation validation): UNMET — honestly and
correctly reported as such, not newly assessed by this amendment.** This
amendment did not reopen or re-attempt strict isolation validation; it
reconfirms, within the fresh exercise-2 isolation summary, the same
honest `UNMET` verdict the fifth amendment already established (the
environment's Tier 1 isolation mechanism remains unavailable; curated
export directories and instruction-only scoping are mechanically
confirmed `best-effort`, never a strict enforcement boundary). This is
the expected, intended answer per the fifth amendment's own established
verdict — not a gap introduced or left unaddressed by this amendment.

## Next step (not part of this audit — recorded for the lead)

This PASS authorizes the terminal `roadmap-context-curator` reconciliation
the plan's own §0 "Sixth revision" entry names: update
`planning/ROADMAP.md`'s Phase 79 row and `planning/CONTEXT.md`'s
current-state section to narrate the sixth amendment
(`decisions/0068`, the three corrections, this audit's verdict), and
update this plan file's own Status line — nothing else, per `CLAUDE.md`
§5's named exemption for that specific commit.
