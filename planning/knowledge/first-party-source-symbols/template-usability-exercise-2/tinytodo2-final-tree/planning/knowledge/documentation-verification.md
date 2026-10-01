# Documentation verification: `planning/knowledge/assertions/id-reuse-001.md` vs. real `_next_id` behaviour

Independent, adversarial review of a single Claim/Assertion record
(`planning/knowledge/assertions/id-reuse-001.md`), conducted with no
memory of the research dispatch that wrote it, against the real
repository at commit `641daf64be3e6ef7daec0d57c08ac17fd52bc708` (branch
`main`, clean working tree, tinytodo2). Reviewer read `src/tinytodo.py`
and `tests/test_tinytodo.py` directly and ran the code itself; nothing
here is taken on the assertion's own say-so.

## What was checked

1. Every file/line citation in the assertion
   (`src/tinytodo.py:36-55`, `:58-63`, `:76-82`;
   `tests/test_tinytodo.py:9-18`) against the real file contents —
   all citations resolve exactly, with no drift.
2. The commit hash cited as the evidence's "as of" point
   (`d287ee7889279198d1e0d94675af6c8240396bd9`) — confirmed by
   `git rev-parse d287ee7` to be the exact full hash of that commit.
3. Literal re-derivation of all three cited scenarios (A, B, C) in a
   fresh scratch environment, Python 3.13.5, against the real `add` /
   `delete` / `_next_id` functions — not by reading the assertion's
   reported outputs and trusting them.
4. Eight additional scenarios not in the original record (labelled
   D-L below), specifically targeting the two things this review was
   asked to hunt for: other deletion orderings and task counts that
   might behave differently, and whether three scenarios were actually
   exhaustive of the behaviour classes that matter.
5. Literal execution of both of the project's existing test functions'
   real bodies (not a paraphrase, and not the assertion's own "by hand"
   reproduction) against the live module, to double-check the
   assertion's claim about test coverage gaps.
6. A direct source re-read for any hidden state (a counter, a second
   persisted file, module-level state) that might contradict the
   assertion's "no separate counter or high-water-mark record" claim.
7. Whether the assertion's `Kind`, `Basis`, `Evidence-support state`,
   and `Status` fields are internally consistent with its own content
   and with the template's defined vocabulary
   (`planning/knowledge/assertions/TEMPLATE.md`).
8. Whether the assertion contradicts itself anywhere (statement vs.
   justification vs. examples vs. counterexamples vs. status).

## What was resolved (new evidence produced)

New Evidence record added (append-only; the existing Claim's own
`Statement` was not touched):
`planning/knowledge/assertions/id-reuse-001-review-evidence.md`.

Findings:

- **Scenarios A, B, C reproduce exactly as reported.** A → new id 4 (no
  reuse). B → new id 3, equal to the just-deleted id (reuse). C → new id
  1 (reuse, the fully-emptied case). No discrepancy of any kind from the
  assertion's own reported numbers.
- **All eight additional scenarios (D-L) — different deletion orderings,
  different task counts, middle-id deletion, repeated/cascading
  max-deletion, deletion of a nonexistent id, deletion of an id that was
  itself the product of an earlier reuse — are fully consistent with the
  assertion's stated general rule** ("reuse occurs iff the deleted task
  held the current maximum id at the moment of its own deletion;
  otherwise the surviving maximum determines a strictly new id").
  Deliberately hunted for: a case where a previously-reused id behaves
  differently on a second reuse (K — it doesn't: it reuses again,
  exactly as predicted, confirming `_next_id` really does carry no
  memory at all beyond the current list); a case where reuse and
  no-reuse might interact across two deletes in one run (J, L — they
  don't, each fires independently per the same rule); a case where
  deleting a middle id (neither min nor current max) in a 4-task list
  might behave like max-deletion (E — it doesn't; no reuse, confirming
  the rule is specifically about the *current maximum*, not about
  deletion in general). No scenario surfaced a counterexample to the
  rule, and no missed behaviour class was found. Three scenarios turned
  out to be a representative, not exhaustive, set, but the two
  behaviour classes they represent (max-delete → reuse; non-max-delete →
  no reuse) are in fact exhaustive of all deletion cases this
  single-counter-free, max()-based implementation can produce — there is
  no third class to find, and extensive further probing didn't find one.
- **"No separate counter" claim re-confirmed directly from source**:
  grepped for `counter`/`global`/any second persisted path; confirmed
  `_next_id` takes only the just-`_load()`-ed task list, `STORE_PATH` is
  the only persisted state, and the two `counter`/`high-water mark`
  hits in the file are inside the docstring's own prose, not actual
  code.
- **Both existing tests re-run literally (not hand-reproduced), with
  pytest confirmed still unavailable** in this review's own environment
  too (`No module named pytest`, matching the original record's
  environment note — this review did not install pytest, to keep the
  check apples-to-apples with the original dispatch's own constraint,
  and because the literal-body execution below is a strictly more
  direct check than installing a test runner around it). Both pass
  exactly as asserted, and `test_ids_are_never_reused_after_delete`
  does in fact exercise only the non-maximum-delete path (Scenario A),
  confirming the record's claim that this test would pass unchanged
  even with the max-delete reuse defect present.
- **All file/line citations and the commit hash check out exactly** —
  no drift, no stale reference.
- **No internal contradiction found** between the assertion's
  `Statement`, `Justification`, `Examples`, `Counterexamples`, or
  `Status`/`Evidence-support state` sections. Each reads consistently
  with the others: the headline docstring claim is contradicted
  (Scenario B), the docstring's own final-paragraph caveat about the
  fully-emptied case is not contradicted (Scenario C), and the one case
  the project's own test suite actually covers (Scenario A) is
  correctly identified as the non-reuse case.

## Minor observation (not escalated — does not change the verdict)

The `Kind` field reads `boundary` "with a `rule`-kind component" — the
template (`planning/knowledge/assertions/TEMPLATE.md`) asks for "the one
[kind] that best describes what kind of statement this is," implying a
single value, not a blended one. This is a cosmetic template-conformance
nit, not a factual problem: the assertion's own text makes clear exactly
why both aspects apply (it characterizes a boundary condition on an
id-uniqueness guarantee, while also testing a stated rule/invariant
directly), and picking `boundary` alone would have been equally
defensible without the added note. Not worth escalating; noted only
because the review charter asks for precision about field justification.

## Escalations

**None.** This review found no genuine unresolved ambiguity requiring
the actual user/domain owner's judgment. The one open question the
assertion itself correctly leaves open — "is 'ids are never reused' a
real product requirement, or dead/aspirational docstring text?" — is
exactly the kind of question this role must not answer on the user's
behalf, but it is not a new finding from this review; the assertion
already correctly frames it as outside its own scope and does not
attempt to resolve it itself. No new escalation-worthy ambiguity was
found.

## Verdict

**The assertion holds up fully to independent adversarial review.**
Every cited scenario reproduces exactly; eight additional, deliberately
adversarial scenarios (different orderings, different task counts,
repeated and cascading reuse, deletion of a previously-reused id,
deletion of a nonexistent id, middle-id deletion) found no
counterexample to its stated general rule and no missed behaviour
class; every citation (file/line, commit hash, test behaviour) checks
out against the real repository; and the record is internally
consistent across all of its own sections.

- `status: contradicted` is the correct call. The docstring's own
  headline sentence ("Task ids are never reused, even after a task is
  deleted") and its "highest id *ever* assigned" reasoning are false as
  a description of the real implementation — directly and repeatedly
  falsified (Scenario B and this review's D/F/G/J/K/L). "Contradicted"
  is the right status rather than, say, `proposed` (there is abundant
  evidence, not an absence of it) or `verified` (per the template's own
  note, `verified` is reserved for a rule actually confirmed to hold,
  not for one that's been actively disproven).
- `evidence_support_state: conflicting` is the correct call, not
  `unsupported` or `partially_supported`. The evidence doesn't
  uniformly fail the docstring's claim — it confirms one part of it
  (the fully-emptied-list caveat, Scenario C) while directly
  contradicting another part of it (the headline "never reused"
  claim and its stated reasoning, Scenario B and this review's further
  cases). That split-decision pattern is exactly what `conflicting` is
  for, as distinct from a claim that is simply wrong everywhere it's
  tested (`unsupported`) or one that holds in its core but is
  incomplete at the margins (`partially_supported`). Here the
  docstring's *headline* claim is the one that's wrong, and its
  *caveat* is the one that's right — the reviewer agrees with the
  original record that "conflicting" best captures that the docstring's
  own text is internally inconsistent about which conditions it
  covers, not that the real behaviour itself is inconsistent (the real
  behaviour is in fact fully deterministic and rule-governed, as this
  review's additional scenarios confirm).

No fix to the assertion itself is needed or was made (write boundary:
the existing Claim's `Statement` was not edited). The only output of
this review beyond this report is the new, purely corroborating Evidence
record at
`planning/knowledge/assertions/id-reuse-001-review-evidence.md`.
