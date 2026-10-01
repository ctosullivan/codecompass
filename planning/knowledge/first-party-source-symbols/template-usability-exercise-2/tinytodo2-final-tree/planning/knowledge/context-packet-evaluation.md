# Context-quality evaluation — fix `_next_id` id-reuse bug

## Setup

- **Reference project:** `tinytodo2` (local scratch project, not a public
  repo) — `/tmp/claude-1000/-home-cormac-projects-codecompass/0b2afcc0-cb03-48e4-8480-bf16722dc977/scratchpad/fresh-exercise/tinytodo2`
- **Pinned commit:** `2bcee49b677a6477c6a60079823900afce303cae` (the
  packet's own HEAD at evaluation time). Verified `git diff` of
  `src/tinytodo.py` and `tests/test_tinytodo.py` between this commit and
  the packet's cited freeze commit (`1d2e6b87b081baefa774382a87aa7c1baa42428d`)
  is empty — no drift between the snapshot and the file evaluated.
- **CodeCompass revision:** n/a — this packet is a hand-assembled
  "coding-context packet" artifact (`planning/knowledge/` format), not a
  live `codecompass query`/`check` output. Evaluated as a context
  artifact per the same rubric regardless.
- **Task:** Fix `_next_id` (`src/tinytodo.py`) so a deleted task's id is
  genuinely never reused (matching the docstring's claim), without
  breaking the two existing tests in `tests/test_tinytodo.py`.
- **Context CodeCompass supplied:** the full packet at
  `planning/knowledge/context-packet-fix-id-reuse.md` (reproduced/cited
  in full in this evaluation's working notes; see that file for verbatim
  text) — a root-cause statement, a proposed persisted-counter fix
  approach, three proposed new test cases, and an explicit non-goals
  section, all sourced from `id-reuse-001.md` and its review-evidence
  supplement.

## Independent ground-truth method

Read `src/tinytodo.py` and `tests/test_tinytodo.py` directly (not via
the packet or any `planning/knowledge/` record). Then, independently of
all cited assertion files, wrote and ran a standalone script against the
real module to reproduce the claimed defect (deleting the
current-maximum id causes reuse) and a second prototype implementing the
packet's proposed persisted-counter/`{"next_id", "tasks"}` fix, run
against equivalents of both existing tests plus the regression and
reload scenarios the packet proposes testing. Only after this did I read
`id-reuse-001.md` and `id-reuse-001-review-evidence.md` to check the
packet's grounding/citations.

Results:
- `_next_id` is confirmed, by direct reading, to be exactly
  `return 1 if not tasks else max(t.id for t in tasks) + 1` — a pure
  function of the currently-loaded task list, with no counter, no
  module-level state, and exactly one persisted file (`todo.json` via
  `STORE_PATH`). Matches the packet's stated root cause exactly.
- Independently reproduced the bug: `add` three tasks (ids 1,2,3),
  `delete(3)` (the current max, with 1 and 2 still live), `add` again →
  new id is **3**, reused, with two older tasks still present. Matches
  the packet's "Scenario B" exactly, including the detail that this is
  not limited to the fully-emptied-list case.
- Confirmed the packet's characterization of both existing tests:
  `test_ids_are_never_reused_after_delete` deletes id `1` (the
  *non-maximum* id) from `[1,2]` — the one case that was never broken —
  and `test_fresh_store_starts_at_one` never deletes anything. Neither
  would catch the real bug.
- Prototyped the packet's proposed fix (restructure `todo.json` to
  `{"next_id": N, "tasks": [...]}`, increment-and-persist on every
  `add`, never recompute from `max()`). Ran equivalents of both existing
  tests against it: both pass, confirming the restructuring does not
  break `test_fresh_store_starts_at_one`'s "fresh store starts at 1"
  requirement (the prototype bootstraps `next_id=1` when no store file
  exists, exactly as the packet specifies). Also confirmed it fixes
  Scenario B (new id `4`, not reused) and survives a simulated process
  restart (`importlib.reload`) without resetting the counter — the exact
  property the packet's third proposed test (`persistence-across-reload`)
  is designed to catch a regression of.
- Spot-checked the packet's line-level citations
  (`src/tinytodo.py:36-55` for `_next_id`, `tests/test_tinytodo.py:9-18`
  and `:21-25` for the two tests) against the real file — exact.

No incorrect or unverifiable claim was found anywhere in the packet.

## Criteria assessment

| Criterion | Rating | Notes |
|---|---|---|
| Accuracy | strong | Root cause, both test characterizations, the "no persisted state" claim, and the proposed fix's compatibility with both existing tests all verified correct by independent execution, not just by trusting the cited assertion files. |
| Relevance | strong | Every included fact is tied directly to this bounded task; the packet's own "what was left out" section correctly excludes topically-adjacent but task-irrelevant material (the docstring self-contradiction rewrite, 8 of 11 corroborating scenarios, unrelated knowledge records). |
| Completeness | adequate | Covers root cause, fix shape, and the needed new tests. Two things it doesn't surface: (1) no mention of backward-compatibility for a pre-existing on-disk `todo.json` in the old bare-list format once the store is restructured — immaterial to the stated task (neither existing test has a pre-existing store) but a real gap for shipping the fix; (2) it names `_next_id` as the locus of the fix but doesn't spell out that `delete()`'s own save call must also be updated to propagate the counter (confirmed necessary when prototyping) — inferable from "this is a format change," but not stated as a concrete call-site list. |
| Freshness | strong | `git diff` between the packet's cited freeze commit and the evaluated HEAD is empty for both `src/tinytodo.py` and `tests/test_tinytodo.py` — no drift. |
| Grounding / provenance | strong | Every material claim traces to `id-reuse-001.md` / its review-evidence supplement, both independently re-verified here; line-number citations are exact. |
| Noise | strong | Explicit, justified exclusions keep the packet to what the bounded task needs; no padding. |
| Safety / trustworthiness | strong | No claim is overstated; recommended-vs-required test cases are explicitly hedged, and open product questions (Scenario C's fate) are correctly flagged as unresolved rather than silently assumed. |

## Verdict: PASS

Every material claim in the packet was independently verified against
the real source, the real tests, and a working prototype of the proposed
fix, and every one checked out — the root-cause diagnosis, the test
coverage-gap claim, and the proposed fix's compatibility with both
existing tests are all correct. The two completeness gaps above
(migration of a pre-existing store file, and not naming `delete()` as a
second call site needing the format change) are minor and non-blocking:
neither would send an implementing agent to an incorrect conclusion, and
neither is required to satisfy the task's literal, bounded scope (don't
break the two named tests).

## Context advantage: LOW

**Could a competent fresh Claude session have obtained equivalent
context trivially through ordinary repository inspection? Yes.**

`src/tinytodo.py` is 115 lines; the function under scrutiny is 5 lines of
code with a 15-line docstring that all but states the bug itself ("the
module has no record of 'highest id ever assigned' beyond what's visible
in the current task list" — this sentence is one inferential step from
"so deleting the current max and re-adding will reuse its id"). Reading
the docstring against the one-line implementation
(`max(t.id for t in tasks) + 1`) surfaces the exact contradiction the
packet's root-cause section describes, and the two-test file (26 lines)
makes the coverage gap equally visible on a single read (one test
deletes id 1 out of `[1,2]`, never the max). I reproduced the entire bug
and validated a correct fix in a few minutes using nothing but the two
target files and a throwaway Python script — no advantage over that
baseline would have come from the packet except time saved re-deriving
test cases already obvious from reading the existing test file's gap.
This is exactly the "small repo, self-evident bug" case the rubric names
as an honest, expected LOW result, not a packet failure — the packet is
accurate and well-scoped, it just isn't solving a problem that was hard
to find in the first place.

## Material gaps / failures

- No mention of on-disk backward-compatibility: restructuring
  `todo.json` from a bare list to `{"next_id": N, "tasks": [...]}`
  will break loading for anyone with a pre-existing store file in the
  old format; the packet doesn't flag this as a consideration even
  though it's a direct, foreseeable consequence of its own recommended
  approach. Non-blocking for the stated task's literal scope (the two
  tests always start from an empty `tmp_path`), but a real-world
  shipping gap. — candidate learning: packets recommending an on-disk
  format change should default to naming migration/compatibility as an
  explicit consideration even when out of the literal task's test scope.
- The packet names `_next_id` as "the" fix locus but the actual change
  necessarily touches `_load`/`_save` and `delete()`'s save call too
  (confirmed by prototyping); this is inferable but not spelled out as
  a concrete list of call sites a diff would need to touch.
- (Not a packet defect, but worth recording for the aggregate corpus:)
  this task is a poor discriminator of context-quality advantage because
  the bug is close to self-disclosing in the docstring itself — future
  task selection for this kind of micro-repo exercise should prefer
  bugs where the defect is *not* already half-stated in a comment the
  agent would read anyway.

## Would this have misled the implementing agent? no

Every claim checked out against independent execution of the real code
and a working prototype of the proposed fix; nothing in the packet would
have sent an implementing agent toward an incorrect diagnosis, an
incorrect fix shape, or a test that fails to catch the regression.
