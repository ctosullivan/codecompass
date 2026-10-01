# Alignment report: id-reuse@v1 snapshot vs. model-blind implementation reconstruction

**Mode**: comparison (domain-skeptic, `decisions/0066`)
**Date**: 2026-10-01
**Inputs compared**:
- Frozen snapshot: `planning/knowledge/snapshots/id-reuse@v1.toml`
  (`repository_revision_at_freeze = 1d2e6b87b081baefa774382a87aa7c1baa42428d`)
- Cited assertion: `planning/knowledge/assertions/id-reuse-001.md`
- Cited corroborating evidence: `planning/knowledge/assertions/id-reuse-001-review-evidence.md`
- Independent as-built reconstruction: `planning/knowledge/implementation-reconstruction.md`
  (produced from only `src/tinytodo.py` + `tests/test_tinytodo.py`, with no
  access to the snapshot, the assertion, the review evidence, or any other
  documentation)

## Pre-check: are the two artifacts actually looking at the same code?

Verified directly rather than assumed: `git log --oneline -- src/tinytodo.py
tests/test_tinytodo.py` shows exactly one commit (`b6a1bb5`, the initial
commit) ever touched either file; `git diff b6a1bb5 HEAD -- src/tinytodo.py
tests/test_tinytodo.py` is empty. Both files are byte-identical from the
initial commit through current `HEAD` (`c5a56a3`). So the reconstruction's
export (said to be exactly these two files) and the assertion's cited
evidence (`src/tinytodo.py` at `b6a1bb5`/`641daf6`) are the same source
content — the comparison is apples-to-apples, not an artifact of code
having drifted between when each artifact was produced.

I also re-read `src/tinytodo.py` and `tests/test_tinytodo.py` myself in
full (not just trusting either artifact's quotation of them) to confirm
both documents' transcriptions of the code are accurate. They are.

## Classification: `aligned`

Every behavioral claim the assertion (`id-reuse-001`) makes about
`_next_id`/`add`/`delete` is independently reproduced, without being fed
the assertion, by the reconstruction:

| Claim in `id-reuse-001.md` | Reconstruction's independent finding | Match |
|---|---|---|
| `_next_id` computes `max(current ids) + 1` (or 1 if empty), with no separate high-water-mark record | §9: "computes `max` over the ids **currently present** ... no stored high-water mark, counter file, or any other record of ids that have ever existed" | exact |
| Docstring's headline claim ("ids are never reused, even after a task is deleted") is false as a general statement | §9 bottom line: "the headline sentence ... is false as a general statement about the code, confirmed by direct execution" | exact |
| Docstring's final-paragraph caveat (full-list-emptying resets the counter) is accurate and the one case it *does* cover | §9 item 1: "Disclosed case, confirmed real" | exact |
| Reuse also occurs whenever the deleted task held the *current maximum* id, even with other (older) tasks still present — not only in the fully-emptied case (assertion's "Scenario B") | §9 item 2: "deleting the task that currently holds the maximum id — while other, older tasks still remain — causes the very next add to reuse that exact id, with no list-emptying involved at all" + worked example reproducing exactly this | exact |
| No reuse when the deleted task is not the current maximum (assertion's "Scenario A") | §9 item 4: "deleting a task that is not the current maximum ... leaves `max()` unchanged, so the next id is correctly fresh" | exact |
| The project's existing test (`test_ids_are_never_reused_after_delete`) only exercises the non-maximum-delete path and does not cover the maximum-delete reuse case | §8: "Both existing tests only exercise the specific 'delete a non-max-id task, then add' case — they do not test deleting the current maximum-id task, which is exactly where the real behavior diverges most sharply from the stated guarantee" | exact |
| `test_fresh_store_starts_at_one` does not test the reset-after-full-deletion path either (it never deletes anything) | Implicit in §8's "no test covers ... JSON persistence format" framing and explicit body-read of the test (no `delete` call) | exact (reconstruction read the test body directly and shows no delete call) |

The review evidence's eight extra scenarios (D–L) — generalized multi-step
delete/add cycles, no-op deletes of nonexistent ids, reused ids being
reused again — are not individually replicated by the reconstruction
(different dispatch, different scenario choices), but the reconstruction's
own item 3 (deleting two tasks in sequence, `3` then `2`, from `[1,2,3]`,
then reusing `2` while `1` survives) is an independently-constructed
multi-delete scenario that confirms the same general rule the review
evidence's scenarios D/G/L were built to stress-test: "reuse iff the
deleted task held the current maximum id at the moment of deletion."
No scenario in either artifact contradicts this rule; none found a case
the rule fails to predict.

I did not find any point of disagreement, partial divergence, or
unverifiable claim between the assertion (plus its review evidence) and
the reconstruction on the id-reuse behavior itself. There is nothing here
that resolves to `partial`, `conflicting`, `not_implemented`, or
`insufficiently_verified` — both artifacts, produced independently (one
with the docstring/assertion in hand, one blind to both), describe the
exact same conditional behavior with the exact same boundary condition.

## Hard-rule note: alignment is not further verification

`id-reuse-001`'s `status` is already `contradicted` (of the docstring) and
its `evidence-support-state` is already `conflicting`, both set after its
own prior adversarial review (`id-reuse-001-review-evidence.md`). This
reconstruction is a *third*, independently-produced data point (original
research → adversarial review → now a model-blind as-built
reconstruction) that is **consistent with** that already-reviewed state —
it does not, by itself, move `status` or `evidence-support-state` to
anything stronger, and I am not recommending any such edit. The
assertion's own `status`/`evidence-support-state` fields are unchanged by
this report. If the lead believes three convergent independent checks now
warrant promoting `status` toward something like `verified`, that is a
separate, claim-specific decision for whoever owns the assertion record,
not a conclusion this comparison pass is entitled to assert on its own.

No new Observation/Evidence record was needed from me: every claim in the
assertion was already independently reproduced by the reconstruction, and
I re-confirmed the source-identity precondition myself (the `git log`/`git
diff` check above) rather than producing new behavioral evidence of my
own. (If a new record were warranted, it would be a new Evidence record
under `planning/knowledge/`, never an edit to the assertion, the review
evidence, or the reconstruction — none of which I touched.)

## Real gaps the reconstruction found that the assertion does not cover

These are **not** alignment conflicts — the assertion never claims
anything about them, so there is nothing to agree or disagree with. They
are genuine additional findings, scoped entirely outside
`id-reuse-001`'s own statement, and are named here as candidates for a
**future, separate assertion** (`context-researcher`'s job to draft, not
mine):

1. `main(["complete"])` / `main(["delete"])` with no id argument raise an
   uncaught `IndexError` (from `rest[0]`) — no argument-count validation
   anywhere in `main`.
2. `main(["complete", "abc"])` (non-numeric id) raises an uncaught
   `ValueError` from `int(rest[0])` — no input validation or
   `try/except` in `main`.
3. `_load` raises an uncaught `TypeError` if `todo.json` contains a
   record with an unrecognized key (`Task(**t)` fails), since
   `Task.__init__` rejects unknown kwargs — no schema check, no
   corruption recovery, and every public operation (`add`/`complete`/
   `delete`/`list_tasks`) propagates this uncaught since all of them call
   `_load` first.
4. `delete` removes tasks via a list-comprehension *filter*
   (`[t for t in tasks if t.id != task_id]`), not a single find-and-
   remove; if the on-disk store ever contained duplicate ids (nothing in
   the module prevents this for a hand-edited file), one `delete` call
   would silently remove all of them, not just one.
5. CLI exit codes do not distinguish "operation succeeded" from
   "operation reported not found" for `complete`/`delete` — both paths
   return `0`; only the no-args/unknown-command paths return `1`.
6. Zero test coverage for `complete`, `list_tasks`, or the CLI
   (`main`) at all — the two existing tests only exercise `add`/`delete`
   through direct Python calls, never through `main`, and never touch
   `complete` or `list_tasks` in any way.
7. No concurrency protection: `_load`/`_save` is read-modify-write with
   no locking, so two racing processes would silently lose one writer's
   update (whole-file overwrite, last `_save` wins).

## What I checked myself (independent of both artifacts)

- Read `src/tinytodo.py` and `tests/test_tinytodo.py` in full, directly,
  and confirmed both artifacts' quotations/line-number references match
  the real file content exactly (no misquotation in either direction).
- Ran `git log --oneline -- src/tinytodo.py tests/test_tinytodo.py` and
  `git diff b6a1bb5 HEAD -- src/tinytodo.py tests/test_tinytodo.py` to
  confirm the source code both artifacts analyzed is identical across the
  commits each artifact cites — a precondition for the comparison being
  meaningful at all, not merely assumed.
- Did not re-run the Python scenarios myself a fourth time: the assertion,
  its review evidence, and the reconstruction already each independently
  executed (not just read) the same code and reported matching, specific,
  falsifiable outputs (exact ids, exact exception types). A fourth
  from-scratch re-execution would not add information beyond confirming
  arithmetic on an unchanged, already-quoted `max()+1` function three
  independent parties have already run.

## Outcome

- **Classification**: `aligned`.
- **Escalations to the user**: none. There is no genuine ambiguity here —
  three independent executions (original assertion, its adversarial
  review, and this model-blind reconstruction) converge exactly on the
  same conditional rule, with no contradiction to adjudicate.
- **Record changes made**: none (no new Observation/Evidence needed; see
  above). The assertion's `status`/`evidence-support-state` fields are
  left exactly as they were.
- **Recommended follow-up for `context-researcher`**: draft a new,
  separate assertion (or assertions) covering the seven CLI/persistence/
  test-coverage gaps listed above, none of which `id-reuse-001` makes any
  claim about.
