# Phase 89 Stage 89C — independent procedural-fidelity audit

Performed by a fresh, independent `release-phase-auditor` dispatch, separate
from the implementing agents (control arm, treatment arm) and from the
`context-evaluator`. Per plan §8.6, this audit verifies the pinned
procedure (`planning/phase-89-stage-89c-task-b-controlled-comparison.md`
§§1, 4.1/4.2, 5-10, 14) was actually followed, against the exact commit
`b0b2ef8`, and audits every evaluator-visible artifact for accidental
allocation disclosure. Everything below was independently re-derived from
raw artifacts under
`/tmp/claude-1000/-home-cormac-projects-codecompass/0b2afcc0-cb03-48e4-8480-bf16722dc977/scratchpad/stage89c-exec/`
and the subagent dispatch transcripts (`~/.claude/projects/.../subagents/`)
— no prior report's self-description was taken on faith.

## Verdict

**PASS WITH NON-BLOCKING OBSERVATIONS.**

The trial was executed faithfully to the pinned plan on every dimension
checked, with one genuine, confirmed blinding-violation finding (the
oracle-raw-transcript path leak, detailed below) that does not invalidate
Outcome 3's own substantive conclusion given the tied result, but which is
reported here honestly as a real procedural-fidelity defect — not
administratively excused — plus a small number of other non-blocking
observations.

## 1. Pre-registration match (plan §2, pre-registration file)

Confirmed by direct read of both documents:
- Task B's exact shape (`with_combined_section` signature, union-of-
  accounts/exclude, shared-invert/shared-depth validation, zero-section
  `ValueError`) matches pre-registration §2 and plan §3 verbatim — reused
  identically in both dispatch prompts (below).
- The honest disclosure ("This is a controlled-comparison exercise, not a
  live Ledgerkit maintainer request...") is present **verbatim, word for
  word** at the top of both the control (`agent-a486f3cac7f01594b.jsonl`)
  and treatment (`agent-a3f1bf77988e88a20.jsonl`) dispatch prompts —
  confirmed by direct read of the actual persisted subagent transcripts,
  not inferred from either arm's own report.
- Success criterion (plan §2 invariant 5 / pre-registration §6) was not
  modified anywhere — no document found anywhere in the repository or
  scratch state that restates or loosens it.

## 2. Ledgerkit SHA pinning (plan §1, §4.2)

Directly re-verified, this audit, against every clone:

| Clone | `git rev-parse HEAD` |
|---|---|
| `ledgerkit-seed` | `a7740fd04fe1814d2a557bfcb67a9a775a4a22f9` |
| `ledgerkit-control` | `a7740fd04fe1814d2a557bfcb67a9a775a4a22f9` |
| `ledgerkit-treatment` | `a7740fd04fe1814d2a557bfcb67a9a775a4a22f9` |
| `ledgerkit-reference` | `a7740fd04fe1814d2a557bfcb67a9a775a4a22f9` |
| `ledgerkit-verify-control` | `a7740fd04fe1814d2a557bfcb67a9a775a4a22f9` |
| `ledgerkit-verify-treatment` | `a7740fd04fe1814d2a557bfcb67a9a775a4a22f9` |
| real `~/projects/ledgerkit` | `a7740fd04fe1814d2a557bfcb67a9a775a4a22f9` |

Every clone pinned identically; the real checkout's own `HEAD` still equals
the pinned SHA (no drift), and was never substituted anywhere. No clone
required the §1 blocker path.

## 3. Packet generation and contamination check (plan §5.3/§5.4)

Independently re-derived (not copied from the fixture-equivalence report):
`diff <(jq -S .) <(jq -S .)` of `control-packet.json`/`treatment-packet.json`
produces exactly three differences, matching the plan's own four-category
allowlist (category 4, unchanged fields, confirmed empty of differences):

1. One additional item in the treatment packet: `EV-BALANCEFROMS-004`
   (`kind: evidence`), with a `+dirty (tested_subject_digest=...,
   test_input_digest=...)` `source_revision`.
2. `CL-BFS-004`'s `consistency.knowledge_revision`: `ca41ecd3...` (control)
   vs. `4c2653a1...` (treatment).
3. `CL-BFS-004`'s `consistency.reasons`: `"3 required scope(s)..."`
   (control) vs. `"2 required scope(s)..."` (treatment).

Nothing else differs. This matches the persisted fixture-equivalence
report's own claim exactly, now independently confirmed rather than
trusted.

`EV-BALANCEFROMS-004`'s own YAML record (`project-post/planning/knowledge/
balance-from-spec/EV-BALANCEFROMS-004.yaml`) cites `test_ref:
".../results/overlapping-account-patterns-no-double-count--
20261120T155655085992Z-6078d152.yaml"`; the corresponding persisted
`OracleResult` (found at that path) independently confirms `outcome: PASS`,
`tested_subject_digest: 7a2c2d03...` — matching the Evidence record's own
embedded digest exactly. **Task A's Evidence is genuine, not fabricated.**

## 4. Dispatch-prompt symmetry (plan §4.1/§7.2/§7.3) — re-derived directly from the real subagent transcripts

Retrieved and diffed the actual persisted dispatch prompts
(`agent-a486f3cac7f01594b.jsonl` = control, `agent-a3f1bf77988e88a20.jsonl`
= treatment) with the arm-identifying directory names normalised out
before diffing. Result: the **only** differences between the two full
prompts are (a) the assigned working directory
(`ledgerkit-control`/`ledgerkit-treatment`) and (b) the attached packet's
own JSON content — exactly the three JSON-level differences named in §3
above. The task text, the "most important sentence" framing, the
symmetric packet-delivery sentence ("Attached is a CodeCompass context
packet... You may use it, ignore it, or verify its contents against the
source."), and the read-scope statement are byte-identical (modulo
directory name) in both prompts, both present verbatim as pinned by plan
§4.2/§7.2/§7.3 item 4. This directly confirms plan item 3 ("appropriately
generated packets... nothing else differs") at the level of the actual
dispatch, not merely the packet files in isolation.

## 5. Initial clone equivalence (plan §4.2) and isolation (plan §7, §12)

- `diff -rq --exclude=.git --exclude=.venv --exclude=__pycache__
  --exclude=.pytest_cache ledgerkit-control ledgerkit-treatment` (re-run
  this audit, post-dispatch): exactly the two files either arm was
  expected to touch differ (`ledgerkit/models.py`, `tests/
  test_reports.py` — the latter each arm's own added unit tests, which
  the dispatch prompt explicitly permits). No other file differs.
- `control-report.md`/`treatment-report.md` re-checked directly (not only
  trusting the boundary-check reports): neither report names the other
  arm's clone, this CodeCompass repository, the real `~/projects/
  ledgerkit`, or `reference-projects/ledgerkit`. Each report's own
  self-stated working-directory path is the only occurrence of its own
  arm-name string; this is the arm correctly stating its own assignment,
  not a leak.
- Real `~/projects/ledgerkit` and real `/home/cormac/projects/codecompass`
  `git status --short`: the Ledgerkit checkout is fully clean; the
  CodeCompass checkout shows only the five new, untracked
  `planning/reference-projects/ledgerkit/08-stage-89c-*.md` report files
  this trial itself produces — no modification to `planning/knowledge/
  balance-from-spec` or `planning/contracts/balance-from-spec` (confirmed
  via `git diff --stat` on both paths: empty). **No real Ledgerkit or
  production CodeCompass canonical-knowledge write occurred.**

## 6. Implementation correctness (plan §3, §6)

Both arms' `with_combined_section` diffs read directly: both correctly
reuse `balance_from_spec`'s existing `any(...)`-based OR-matching gate and
add **no** extra deduplication/aggregation logic of their own, both with
explicit docstring reasoning to that effect. Both raise `ValueError` on
mismatched `invert`/`depth` and on zero sections; neither mutates inputs.
This is independently confirmed, not merely asserted, by the acceptance
suite results below — and is the direct explanation for the tie (both
arms reached the single correct design answer).

Re-run directly, this audit (not merely trusted from the acceptance-
verification report):
- `pytest tests/test_combined_section_acceptance.py` against both verify
  clones: **11/11 PASS, both arms** (my own re-run matches the persisted
  report exactly).
- Full regression suite (`pytest tests/`) against both verify clones:
  **957 passed** (control), **958 passed** (treatment), 14 subtests
  passed both — my own re-run matches the persisted report exactly. The
  one-test difference is each arm's own disclosed number of added unit
  tests, not a behavioural difference.
- The disposable `STAGE89C-TASKB-VERIFY` oracle contract
  (`stage89c-verify-contract.yaml`) names only the one
  `combined-section-no-double-count` check, `required: true`,
  `check_reference` pointing at the one primary-scope test method, exactly
  matching plan §6 step 4's pinned YAML. The real `balance-from-spec`
  contract under `planning/contracts/balance-from-spec/` contains no trace
  of this check — confirmed by direct grep, no hits. `run_oracle.py`'s own
  recorded `evaluate_check`/`write_oracle_result`/`parse_oracle_result`/
  `evaluate_result_precedence` sequence matches the real Phase 82 API
  signature exactly; both `run_id`s and digests in the two persisted
  `oracle-result-{control,treatment}.json` files match the acceptance-
  verification report's own table exactly.

## 7. Blinding audit (plan §8.6) — the required finding

**Confirmed independently, by direct grep of the raw artifacts, a genuine
stage-one blinding violation**, matching exactly what the
`context-evaluator`'s own report (`08-stage-89c-evaluation.md`) disclosed:

```
blinded/draft-1/draft-1-verify/oracle-raw/combined-section-no-double-count--...-4e61a8f1.txt:
  $ .../scratch/.../ledgerkit-verify-control/.venv/bin/python -m pytest ...
  (cwd=.../scratch/.../ledgerkit-verify-control)

blinded/draft-2/draft-2-verify/oracle-raw/combined-section-no-double-count--...-6506946d.txt:
  $ .../scratch/.../ledgerkit-verify-treatment/.venv/bin/python -m pytest ...
  (cwd=.../scratch/.../ledgerkit-verify-treatment)
```

The literal strings `ledgerkit-verify-control` and `ledgerkit-verify-
treatment` appear, unredacted, inside both raw pytest-subprocess
transcript `.txt` files under each draft's own `oracle-raw/` directory.
These two strings are **named explicitly in plan §8.6's own stage-one
automatic-violation list** ("the literal filenames... or
`ledgerkit-verify-control`/`ledgerkit-verify-treatment`") — this is a
stage-one-caliber hit, not a stage-two contextual judgment call, exactly
as the dispatch instructed me to assess it.

**Root cause of the miss, confirmed directly**: `redaction-log.md`'s own
"Verification" section records its post-redaction re-scan as searching
for the literal strings `ledgerkit-control`, `ledgerkit-treatment`,
`oracle-raw-control`, `oracle-raw-treatment`, `control-packet`,
`treatment-packet`, `control-report`, `treatment-report` — **it never
included `ledgerkit-verify-control`/`ledgerkit-verify-treatment` in that
re-scan's own string list**, despite the plan's own §8.6 stage-one list
naming exactly those two strings. Because `"ledgerkit-verify-control"`
does not contain `"ledgerkit-control"` as a contiguous substring (there is
a `-verify-` in between), a grep for the shorter string silently misses
the longer one. This is a genuine execution gap against the plan's own
explicit checklist, not merely an unlucky miss — the redaction pass
implemented a plausible-looking but incomplete version of plan §8.6's own
named stage-one list.

The `oracle-result.json` files in both draft-verify directories **were**
correctly redacted (`raw_output_ref` rewritten to `draft-N-oracle-raw/...`,
confirmed by direct read) — the leak exists only in the raw `.txt`
transcript files, a second, separate occurrence of the same path the
redaction log's own item 1 explicitly targeted in the JSON field but
missed in the sibling raw-text file.

**My own independent full re-sweep of `blinded/draft-1/` and
`blinded/draft-2/`** for both the stage-one list (verbatim) and a broader
stage-two case-insensitive `control|controls|controlling|treatment` sweep
found:
- The one confirmed leak above (stage-one caliber), present once per
  draft, confined to the raw oracle-transcript `.txt` files.
- No other stage-one-list string (literal clone names, packet/report
  filenames, the allocation key or its contents) appears anywhere in
  either draft directory.
- Every other case-insensitive `control`/`treatment` hit (253 total, e.g.
  `ledgerkit/models.py`'s own pre-existing comment "a ReportSpec
  controls sign presentation") is byte-identical between `draft-1` and
  `draft-2` (ordinary, pre-existing Ledgerkit source/docs prose,
  unconnected to allocation) or, in one case (`draft-1-report.md`:
  "traced the control flow by hand"), ordinary English present in only
  one report but carrying no allocation-identifying content — both
  categories match plan §8.6 stage two's own "harmless" carve-out
  exactly, and I independently confirm this characterization rather than
  trusting the redaction log's own claim of it.

**Materiality assessment (the dispatch's own specific question)**: this
leak does **not** taint Outcome 3's own substance. Reasoning:
1. The actual result is a **tie** on every signal — acceptance-test
   outcome (11/11 PASS both), `context-evaluator` verdict (PASS WITH GAPS
   both), and context-advantage rating (LOW both). There is no asymmetric
   outcome for allocation knowledge to have produced or biased toward; a
   biased-toward-treatment verdict would need to look asymmetrically
   favorable to the arm the evaluator could have inferred was
   "treatment," and it does not.
2. The evaluator's own report explicitly discloses the leak, explicitly
   states it did not act on or infer from it, and its own stated
   reasoning path for every criterion score and the final verdict/rating
   is traceable to genuine content (the real source code, the real packet
   diff, the real test re-runs) — never to "because this is the
   treatment/control arm." I independently confirm this by reading the
   evaluator's own reasoning end to end: every advantage credited to
   "Draft 2" (the one extra Evidence item, its grounding/provenance) is
   justified by a content difference I also independently verified exists
   in the packet (§3 above) — not by name-based inference.
3. The point in the evaluator's own workflow where the leak was observed
   (reading `oracle-raw/*.txt` to confirm the primary-scope result) is a
   verification step performed in service of, not prior to, forming the
   substantive verdict — the disclosure itself states this was
   "incidental," consistent with the report's own structure (the
   disclosure appears after the verdict-relevant criteria assessment, as
   a late confirmatory step).

**Disposition, stated explicitly per the dispatch's own instruction**:
this is a **real, confirmed blinding-violation finding** under plan
§8.6's own stage-one rule — it genuinely "voids that run's own blinding
claim" in the narrow sense that this run cannot honestly be described as
perfectly allocation-blind to the evaluator throughout its entire
process. It is reported here as such, not silently excused. It does
**not**, however, invalidate Outcome 3's substantive conclusion, because
the result is a tie regardless of allocation knowledge, and the
evaluator's own reasoning shows no dependence on that knowledge. This
finding is a process defect in the redaction sweep's own completeness
(item 1 below), to be fixed before any future re-use of this blinding
procedure — it is not grounds to re-run this specific trial, since
re-running would not change a result that is already a documented tie on
every signal and the leak did not produce it.

## 8. Evaluator blindness at verdict-formation time (plan §8.6, dispatch item 9)

Read the evaluator's dispatch prompt directly
(`agent-a658e8325d02ec2c8.jsonl`): it refers to the two drafts only as
"Draft 1"/"Draft 2" throughout, explicitly instructs the evaluator not to
guess or act on allocation, and supplies no control/treatment-labelled
path anywhere. Read the evaluator's own report end to end: verdict and
rating are reported identically for both drafts with parallel,
symmetrically-applied reasoning; the one place the two drafts are
assessed asymmetrically (Completeness/Grounding, favoring Draft 2) is
justified by the genuine, independently-verified extra Evidence item —
exactly the kind of "substantive Evidence content may reveal which
snapshot is more recent" asymmetry plan §8.3/§8.6 already discloses as
acceptable and expected, not a blinding failure. No sentence in the
report's own reasoning chain depends on, or could only be explained by,
already knowing which draft was which before scoring it.

## 9. The three outcome gates

- **Outcome 1 (technical completion)**: MET. Both arms produced a
  complete, buildable, passing implementation (§6 above); full
  regression suite green for both; real repositories untouched (§5
  above).
- **Outcome 2 (evaluation validity)**: MET, with one disclosed,
  non-blocking procedural-fidelity finding (the oracle-raw blinding leak,
  §7 above) that this audit assesses as not having tainted the
  evaluator's actual verdict, and with the redaction-sweep process gap
  named as a finding to fix going forward (§7, §10 below).
- **Outcome 3 (positive comparative advantage)**: **GATE NOT MET.**
  Acceptance-test outcome: tied (11/11 PASS, both arms — signal (i) not
  met). `context-evaluator` verdict: tied (PASS WITH GAPS, both —
  signal (ii) not met). Context-advantage rating: tied (LOW, both —
  signal (iii) not met). Per plan §10's own explicit instruction ("a tie
  does not satisfy the gate... do not search for a tie-breaking metric
  among §9's own exploratory numbers to manufacture a different
  conclusion"), this reads plainly as **GATE NOT MET** — confirmed, no
  document anywhere in the repository or scratch state currently claims
  otherwise (checked directly: no "GATE MET" string exists anywhere in
  the persisted reports, `CONTEXT.md`, or `ROADMAP.md`).

The `context-evaluator`'s own report additionally names a genuine design
confound (G4: both arms' task specification itself states the correct
design answer, independent of either packet) — this is itself a material,
honestly-disclosed reason the tie should not be surprising, and should be
carried into the final §9 composite report's own "Explicit scope
statement" / Outcome 3 narrative, not treated as a separate defect of
this audit's own scope.

## 10. Process gaps to fix (non-blocking, but should not be silently absorbed)

1. **The blinding-redaction verification sweep's own string list did not
   match plan §8.6's own stage-one list** — it omitted
   `ledgerkit-verify-control`/`ledgerkit-verify-treatment` even though
   the plan names them explicitly, and as a direct result missed a real
   leak this audit found by implementing the plan's own list literally.
   Any future execution of this blinding procedure should grep for the
   plan's own stage-one list verbatim, not a hand-rederived approximation
   of it.
2. **Plan §9's own final composite report
   (`<NN>-stage-89c-task-b-controlled-comparison.md`) has not yet been
   written** as of this audit. This is expected sequencing per plan §11's
   own table (procedural audit before final report), not a defect — but
   it means Stage 89C is not yet closable; the final report, once
   written, must state Outcome 3 as GATE NOT MET per §9 above, and must
   name the oracle-raw blinding leak in its own Outcome 2 section (plan
   §9's schema explicitly routes "any read-scope violation, contamination,
   or isolation failure" there).
3. None of the trial's five persisted reports
   (`08-stage-89c-fixture-equivalence.md`,
   `08-stage-89c-{control,treatment}-boundary-check.md`,
   `08-stage-89c-acceptance-verification.md`, `08-stage-89c-evaluation.md`)
   nor this audit report are committed yet (`git status --short` shows
   them untracked). Expected at this point in the sequence, named here
   only so the final commit does not omit this audit file alongside the
   others.

## 11. Scope/governance check

No edit to `CLAUDE.md`, no edit to any past ADR's original content
(`git diff` on the real CodeCompass repo shows only new, untracked
`planning/reference-projects/ledgerkit/08-stage-89c-*.md` files — no
modified tracked file at all). `planning/ROADMAP.md`/`planning/
CONTEXT.md` both still correctly describe Phase 89 as `in progress`,
Stage 89C as "underway," consistent with gate 3 not yet being resolved —
no premature `done` marking found anywhere.

## Summary for the lead

Re-verified independently: task/framing/success-criterion fidelity to
pre-registration; exact SHA pinning across every clone including the real
checkout; packet generation and the three-category contamination
allowlist (re-derived from the actual JSON, not trusted); the real
dispatch-prompt transcripts for both arms (byte-identical apart from
directory name and packet content); initial-clone equivalence and
post-dispatch isolation (no cross-arm or real-repository leakage in
either report); genuine Task A Evidence; both arms' correct, equivalent
implementations; the full acceptance suite and full regression suite,
re-run directly by this audit with identical results to the persisted
report; the oracle result provenance chain; real-repository
non-contamination.

**The one real finding requiring explicit sign-off**: a stage-one-caliber
blinding leak (literal `ledgerkit-verify-control`/`ledgerkit-verify-
treatment` strings, unredacted, inside both drafts' own raw oracle-
transcript `.txt` files) is confirmed real by my own independent grep,
exactly as the `context-evaluator` itself disclosed. It is named here as
a genuine procedural-fidelity defect, not minimized or administratively
excused. It does not, on the evidence available (a tied result on every
signal; an evaluator reasoning chain traceable entirely to content, not
allocation knowledge), appear to have produced or biased the tie — but
this is an assessment made because the result happens to be symmetric,
not a claim that the leak was harmless in principle. Before the final §9
composite report is written, it must state Outcome 3 as **GATE NOT MET**
(the honest reading of a genuine triple tie) and must name this blinding
finding in its own Outcome 2 section.
