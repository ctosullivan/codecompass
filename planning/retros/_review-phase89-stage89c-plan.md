# Phase 89 Stage 89C plan — independent review

Reviewer: `fork`/`general-purpose`-type independent reviewer, dispatched
explicitly to review `planning/phase-89-stage-89c-task-b-controlled-
comparison.md` (committed at `6530d09`) before any implementation
authorisation, per `CLAUDE.md` §1/§5 and this project's established
plan-review convention. Read-only toward Ledgerkit and canonical
knowledge: all verification below was performed either by direct,
read-only inspection of the real repositories, or inside disposable
scratch clones under the session scratchpad, deleted before this report
was written. The real `~/projects/ledgerkit` checkout was confirmed
clean and unmodified (`a7740fd04fe1814d2a557bfcb67a9a775a4a22f9`) both
before and after this review. The real CodeCompass canonical knowledge
(`planning/knowledge/balance-from-spec/`, `planning/contracts/
balance-from-spec/`) was read but never written.

## VERDICT: NOT READY (one blocking finding)

The plan's overall architecture-reuse strategy is sound, its source-
verified inventory (§1) is accurate in every item I independently
re-derived, and its pre-registration fidelity (§2) is faithful. One
genuine, concrete feasibility gap in §5.3 (missing project-root
selection between the two packet-generation calls) blocks a future
implementer from executing the plan's own text as written, and one
factual imprecision in the plan's own central, already-once-corrected
claim about `consistency.evidence_currency` (§1, §5.4) should be fixed
before implementation, even though it does not by itself invalidate the
contamination check. Both are described in full below, with the exact
correction needed.

---

## BLOCKING FINDING 1 — §5.3's packet-generation procedure never
selects which project root (`project_root_pre`/`project_root_post`) a
given `codecompass knowledge context` invocation reads, so both
commands as literally written would read whichever directory happens
to be the current working directory, not two different snapshots

**Verified directly**: `src/codecompass/cli.py`'s `knowledge_context`
command (and every other `knowledge_app`/`app` command — confirmed by
grep across the whole file) takes no `--project-root`/`-C` option and
has no environment-variable override (`grep -n "os.environ\|getenv"
src/codecompass/cli.py` → no results). Every one of these commands
calls `knowledge_api.get_context_packet(Path.cwd(), topic, ...)`
(confirmed at `cli.py`'s `knowledge_context`, line ~2068) — `Path.cwd()`
literally, not a parameter. The *only* way to point the CLI at a
different `project_root` is to change the process's own working
directory before invoking it.

§5.3's code block defines, in comments only, `project_root_pre` and
`project_root_post` as two different disposable roots, then runs:

```
codecompass knowledge context CL-BFS-004 --repo-root $REPO_ROOT_REFERENCE \
    --json  > control-packet.json     # against project_root_pre
codecompass knowledge context CL-BFS-004 --repo-root $REPO_ROOT_REFERENCE \
    --json  > treatment-packet.json   # against project_root_post
```

Both invocations are written identically apart from the output
filename and a trailing comment — there is no `cd`, no `--project-root`
flag (none exists), and no other mechanism shown anywhere in §5.3 that
would make the first command actually read `project_root_pre`'s
`planning/knowledge/`/`planning/contracts/` and the second actually read
`project_root_post`'s. As literally written, a future implementer who
runs this block verbatim from a single shell session gets **both**
packets generated against whatever directory the shell happened to be
in at the time — almost certainly producing two byte-identical files
(the exact "indistinguishable packet pair" failure mode §5.4/§10 are
designed to catch, but here caused by the generation step itself, not a
reconciliation-pipeline bug). This is the same class of defect
`CLAUDE.md` §1 (L-131, Phase 88) already names and requires plans to
guard against: a relative/implicit-root convention ("whichever
directory you happen to be in") that is enforced only by informal
habit, not by anything in the written procedure, for a step a future,
differently-situated implementer will execute without the author's own
unstated assumptions in mind. §11's own summary table repeats the same
unqualified phrasing ("against both roots") without resolving it either.

**I independently confirmed the underlying mechanism (not just the
CLI gap) by reproducing §5.2's pipeline against a real disposable
scratch copy**: cloning `~/projects/ledgerkit` (read-only source),
adding the pinned `test_section_accounts_overlapping_patterns_no_
double_count` test, confirming it passes, then running the real
`detect-changes`/`verify-changes`/`apply` sequence against a scratch
copy of `balance-from-spec`'s knowledge. This genuinely worked exactly
as the plan describes (see Finding 2 below for what it revealed about
`evidence_currency`) — `codecompass knowledge context` only ever
produced output for whichever directory I had `cd`'d into at the time.
Confirmed empirically, not just by reading the CLI source.

**What would need to change**: §5.3 must name the actual mechanism —
either two literal `cd "$PROJECT_ROOT_PRE" && codecompass ... >
control-packet.json` / `cd "$PROJECT_ROOT_POST" && codecompass ... >
treatment-packet.json` invocations (simplest, matches how §5.2 already
treats `$LK`/`$KN`/`$CT` as real shell variables), or an explicit note
that `get_context_packet`'s underlying Python call (already named as
the fallback spec in the surrounding prose) must be invoked directly
with `project_root=` set explicitly rather than going through the CLI
at all. Either fix is small, but the plan as committed does not specify
it, and a future implementer following the text literally will not
produce two genuinely different packets.

---

## FINDING 2 (non-blocking, but should be fixed before implementation)
— §1's and §5.4's "central correction" about `consistency.
evidence_currency` is itself imprecise: `evidence_currency` does not
actually change value between the pre- and post-Task-A packets when
`repo_root` is supplied symmetrically to both, as the plan's own §5.3
does; only `reasons`' embedded **count** changes, and that count never
names the overlapping-pattern scope the way the plan's prose describes

The dispatch specifically asked for real scrutiny here, since this is a
claim the plan's own §1 says was already corrected once after an
earlier audit caught a different version of it wrong. I re-derived it
myself, both statically (`knowledge_api._knowledge_consistency` /
`knowledge_intermediate.derive_epistemic_profile`, read in full) and
empirically, by reproducing all four pre/post × with/without
`repo_root` combinations against the real, current `CL-BFS-004.yaml`
(pre-Task-A, genuinely unchanged since `b1a8447`/Phase 83 — confirmed:
`evidence_support_state: partially_supported`, `supporting_evidence:
[EV-BFS-001]`, `EV-BFS-001` is source-kind with `test_ref: null`) and a
disposable post-Task-A snapshot I generated myself via the real
`detect-changes`/`verify-changes`/`apply` pipeline against a scratch
Ledgerkit clone with the pinned overlapping-pattern test added:

| | `--repo-root` omitted | `--repo-root <reference clone>` supplied |
|---|---|---|
| **pre-Task-A** (real, current) | `evidence_currency: "absent"`, `reasons: ["3 required scope(s) have no passing evidence at all"]` | **identical**: `"absent"`, `["3 required scope(s)…"]` |
| **post-Task-A** (my own disposable reproduction) | `evidence_currency: "unconfirmed"`, `reasons: ["1 scope(s) have only a historically recorded PASS, not live-reconfirmed…"]` | `evidence_currency: "absent"`, `reasons: ["2 required scope(s) have no passing evidence at all"]` |

`status` is `"unconfirmed"` in all four cells — the plan's correction of
the *original* first-draft error (that `status` would discriminate
pre/post) is right, and this part of §1/§5.4 is sound.

But in the one cell the plan's own §5.3 procedure actually produces for
**both** packets (repo_root supplied symmetrically to both) —
`evidence_currency` is **"absent" in both pre- and post-Task-A**, not a
genuinely differing value as §1 states ("The field that genuinely,
visibly differs pre/post … is `evidence_currency` and `reasons`") and
§5.4 restates ("If `evidence_currency`/`reasons` are also byte-
identical between the two packets, this is the real blocking setup
error"). The only thing that actually differs is the **count embedded
in `reasons`** (`"3 required scope(s)…"` → `"2 required scope(s)…"`),
and that text is a generic count — confirmed directly from
`_knowledge_consistency`'s source (`reasons.append(f"{len(profile.
known_gap_scopes)} required scope(s) have no passing evidence at
all")`) — it never names `"overlapping-account-patterns-no-double-
count"` or any other scope by name anywhere. §1's own description
("pre-Task-A, `reasons` names the required-scope gap … post-Task-A,
that same gap closes … that specific gap's own wording is gone") and
§5.4's matching description both describe a scope-naming mechanism that
does not exist in the real code — the actual, real difference is a
decrementing integer in an otherwise-fixed sentence.

This does not make §5.4's actual mechanical check wrong in practice —
`reasons` genuinely is non-identical between the two packets (3 vs 2),
so the literal `diff` the plan specifies will show a real difference
and the contamination check will correctly not fire a false blocker.
But a future implementer who takes §1/§5.4's own prose at face value and
manually inspects `evidence_currency` specifically, expecting to see it
change, will find it unchanged ("absent" both times) and may reasonably
read this as *the* "blocking setup error" §5.4 names, even though
nothing is actually wrong — exactly the kind of self-inflicted
confusion this project's own review culture (`CLAUDE.md` §1's repeated
amendments on precision of fail-closed/depth-vs-scope claims) treats as
worth catching before execution, not after.

**What would need to change**: rewrite §1's and §5.4's description to
state precisely that `evidence_currency` stays `"absent"` in both
packets when `repo_root` is supplied symmetrically (unchanged, by
construction — two of the three required scopes remain uncited gaps
either way), and that the only mechanically-verifiable pre/post
difference for `CL-BFS-004` is `reasons`' embedded count (and the new
`items` entry for the newly-cited Evidence record, already correctly
named in §5.4 item 1). Drop the "that specific gap's own wording is
gone" framing — no such named-scope wording exists anywhere in
`reasons`.

---

## FINDING 3 (non-blocking, illustrative-only inaccuracy) — §6's own
worked example in the primary test's comment ("a naive implementation
that sums each original section's own already-computed subtotal,
150+159=309") describes a bug that cannot actually be produced by any
implementation conforming to the pinned `with_combined_section(...) ->
ReportSection` signature; the test's real discriminating power is
against a different, but equally real, class of bug (unneeded
`exclude`-based or pattern-level deduplication)

I verified this empirically. I implemented the pinned signature three
ways against disposable Ledgerkit scratch clones, and ran the plan's
own pinned `tests/test_combined_section_acceptance.py` verbatim against
each:

1. **A correct implementation** (union `accounts`/`exclude`, same-
   invert/depth check, raise on zero sections) — all 7 tests pass, as
   the plan requires.
2. **A "buggy" implementation that tries to deduplicate at the pattern-
   string level** (excluding any pattern that is a literal substring of
   an earlier one) — all 7 tests still pass. `"food"` and `"groceries"`
   are not substrings of each other even though they match an
   overlapping *posting* (`expenses:food:groceries`), so this
   particular wrong heuristic is a silent no-op and the test correctly
   cannot distinguish it from a correct implementation — not a flaw in
   the test, just evidence that pattern-string-level dedup heuristics
   are a dead end, which is itself consistent with CL-BFS-004's own
   point.
3. **A buggy implementation that (plausibly) tries to prevent double-
   counting by moving every section-after-the-first's own patterns into
   `exclude` while still listing them in `accounts`** — genuinely fails
   3 of 7 tests, including the primary
   `test_overlapping_patterns_across_combined_sections_counted_once`
   (gets `9.00`, not `159.00`) and `test_three_or_more_sections_
   combine_correctly` (gets `1200.00`, not `1359.00`). This confirms
   the test **does** genuinely discriminate a realistic "added
   unnecessary dedup logic" implementation decision — the actual
   decision under test per the pre-registration §2 — just not via the
   specific "sum of two independently-computed subtotals = 309"
   mechanism the comment describes. That specific mechanism is
   structurally unreachable: `with_combined_section` is pinned to
   return one `ReportSection` (never a number, never a `ReportSpec`),
   and the test itself — not the implementation under test — is what
   constructs the final `ReportSpec` and makes the one `balance_from_
   spec` call; there is no path by which the production code could
   "sum two subtotals" without violating its own required return type
   in an obviously broken way (which the test's set-equality assertion
   would also catch immediately, just not for the stated reason).

**What would need to change (optional, cosmetic)**: rephrase the
`test_overlapping_patterns_across_combined_sections_counted_once`
comment's illustrative "naive implementation" example to describe a
reachable bug (e.g. "an implementation that tries to prevent double-
counting by moving an overlapping section's own pattern into `exclude`
while still listing it in `accounts`") rather than the literally
unreachable "sum of independently-computed subtotals" framing. This is
cosmetic — the test's actual pass/fail behaviour already does the right
thing, confirmed empirically above — so it does not block
implementation, but a future reader relying on the comment to
understand *why* the test exists would be misled about the mechanism.

---

## Verified correct — the other five review areas

**1. Pre-registration fidelity (§2).** Cross-checked §2's six numbered
invariants against `planning/retros/phase-89-ledgerkit-two-task-
demonstration.md` directly, line by line. All six are reproduced
faithfully, including the exact wording of the success criterion ("A
tie does not satisfy it") and the fallback task's honest-disclosure
framing (§8 of the pre-registration, reproduced in this plan's §3
opening). Nothing in §3-§14 weakens or silently drifts from any of the
six — §3's pinned signature/behaviour matches the pre-registration's
§2 description exactly; §4's equivalence table matches invariant 6's
contamination control; §8's success-criterion restatement in the
blinded-evaluation methodology matches invariant 5 verbatim including
"never ... a tie-breaking metric ... to manufacture a different
conclusion" in §10.

**2. Source-verified facts (§1).** Independently re-derived every one:
- Ledgerkit `HEAD` = `a7740fd04fe1814d2a557bfcb67a9a775a4a22f9`, clean —
  confirmed, matches the plan's pin exactly.
- `ledgerkit/models.py`: zero `@classmethod`/`@staticmethod` anywhere,
  zero `combined_section`/`with_combined` references anywhere in the
  tree — confirmed via direct grep.
- `planning/knowledge/balance-from-spec/CL-BFS-004.yaml`: confirmed
  unchanged since `b1a8447` (`git log --oneline` on the file shows
  exactly one commit), `evidence_support_state: partially_supported`,
  `supporting_evidence: [EV-BFS-001]` only, no `EV-BFS-004` anywhere —
  confirmed exactly as claimed.
- `knowledge_api.get_context_packet` and `codecompass knowledge
  context` (`cli.py`'s `knowledge_context`): signatures confirmed
  verbatim, including `max_items`/`max_chars`/`repo_root`/`--json`.
- The fixture amounts the plan's acceptance test relies on (groceries
  150.00, coffee 9.00, rent/housing 1200.00, income 6000.00) and its own
  arithmetic (159.00, 1350.00, 1359.00, 6000.00) all confirmed exactly
  against the real `tests/fixtures/filtered.journal` and `tests/
  test_reports.py`'s own pre-existing `test_multi_section_correct_
  values`/`test_single_section_rows_and_subtotal` assertions.
- `oracle.run_pytest_check`/`OracleCheck`/`OracleContract`/
  `parse_oracle_contract`/`write_oracle_result`/`evaluate_result_
  precedence`: all confirmed present with the signatures/behaviour the
  plan describes (junit-based PASS/FAIL/INVALID classification per
  `decisions/0082` §B; live digest reconfirmation when `repo_root` is
  supplied).
- `planning/reference-projects/ledgerkit/06-fixture-equivalence.md` and
  the `06-stage-d-reportspec-stage1-*-boundary-check.md` files exist and
  follow exactly the seed-clone/fork/`diff -rq`/per-arm-boundary-audit
  pattern this plan reuses; the Phase 78 plan's own §5.3.3 step 1 "one
  shared implementation contract is derived, not invented fresh" quote
  is accurate, not paraphrased-into-a-different-meaning.
- The real `balance-from-spec` `oracle-contract.yaml` has exactly three
  required checks (`single-section-expense-subtotal`, `multi-section-
  income-expense-subtotal`, `overlapping-account-patterns-no-double-
  count`), confirming the plan's "three required scopes" framing in §1.
- All cited ADRs/governing docs (`decisions/0082`, `0092`, `0096`,
  `0097`, `0098`; `context-quality-evaluation.md`'s `L-027`/`L-133`;
  `reference-project-protocol.md`'s `L-062`/`L-022`) exist with content
  matching the plan's citations.

**3. Internal consistency/completeness (§4/§5/§6).** §4's equivalence
table genuinely satisfies "equivalent task/baseline/model/tools/limits/
acceptance/instructions/initial-state" from first principles — the only
deliberate, disclosed asymmetry is the context-packet file itself,
which is the independent variable under test, not a confound. §6's
acceptance test, verified empirically (Finding 3 above): a correct
implementation passes all seven; a realistic wrong-dedup-logic
implementation genuinely fails the primary test and others, which is
the real decision this trial is testing. §5.1-§5.4's procedure, modulo
Finding 1's missing `cd`/root-selection step, produces exactly the
artifacts §7/§8 consume (I reproduced §5.2's detect/verify/apply
sequence myself end to end against a disposable scratch clone, and it
behaves exactly as described: `EV-BALANCEFROMS-004` created, test-kind,
statement byte-identical, `evidence_support_state` → `supported`).

**4. Governance/safety (§12/§13).** No step anywhere authorises writing
to the real `~/projects/ledgerkit` or real canonical knowledge — every
mutation in §5/§6/§7 is explicitly scoped to a disposable scratch clone
or copy, consistent with every prior Phase 89 demonstration's own
established discipline. §13's cleanup procedure and §12's governance
statements match this project's own established conventions for
disposable multi-clone trials (Phase 78, Stage 89A/89B) with nothing
novel or under-specified.

**5. Feasibility (§5-§11), apart from Finding 1.** Every other step
names a concrete command or Python call with no undefined variable or
artifact referenced before it exists. `<NN>` resolution (§11, "currently
the highest used is `07`") confirmed correct against `planning/
reference-projects/ledgerkit/`'s real directory listing (highest prefix
is genuinely `07`).

---

## Summary of required changes before this plan is implementation-ready

1. **(Blocking)** Fix §5.3 to name the actual mechanism for pointing
   `codecompass knowledge context`/`get_context_packet` at
   `project_root_pre` vs `project_root_post` (e.g. explicit `cd` before
   each invocation, or a direct Python call with `project_root=` set) —
   as written, both commands read whatever directory is current, which
   defeats the entire packet-generation step.
2. **(Should fix, non-blocking to the mechanical check's own
   correctness, but a real factual error in the plan's own prose)**
   Correct §1's and §5.4's description of what actually differs between
   the pre/post packets: `evidence_currency` itself is unchanged
   ("absent" in both, when `repo_root` is supplied symmetrically as
   this plan's own §5.3 does); only `reasons`' embedded count changes,
   and it never names the overlapping-pattern scope by name.
3. **(Optional, cosmetic)** Rephrase §6's "sum of independently-
   computed subtotals = 309" comment to describe a reachable bug (e.g.
   the `exclude`-based variant verified above), since the stated
   mechanism cannot actually occur under the pinned signature.

Finding 1 alone is sufficient for NOT READY under this project's own
three-point scale, since it is a concrete step a future implementer
cannot execute correctly from the plan's own text as committed. Once
fixed (and Finding 2 corrected — not strictly required for correctness
of the mechanical check, but required for the plan's own prose to be
true), this plan would be READY WITH NON-BLOCKING OBSERVATIONS at
worst (Finding 3 remains optional/cosmetic either way).

---

## 2026-11-20 — Re-check of the three fixes (uncommitted edits on top of `6530d09`)

Re-dispatched to verify only that the three findings above were
genuinely closed by the working-tree edits to
`planning/phase-89-stage-89c-task-b-controlled-comparison.md`
(`git diff HEAD` against that file). Did not re-review anything else
in the plan (per dispatch scope — the rest stands as this report
already found it).

**Finding 1 (blocking) — FIXED.** Re-confirmed independently against
the current source: `src/codecompass/cli.py`'s `knowledge_context`
(line 2060) still calls `knowledge_api.get_context_packet(Path.cwd(),
topic, max_items=max_items, max_chars=max_chars, repo_root=repo_root)`
literally — no `--project-root`/`-C` option on that command, no
`os.environ`/`getenv` override anywhere in the file. §5.3 now wraps
each of the two calls in its own explicit subshell —
`( cd "$PROJECT_ROOT_PRE" && codecompass knowledge context CL-BFS-004
--repo-root "$REPO_ROOT_REFERENCE" --json ) > control-packet.json`
and the equivalent for `$PROJECT_ROOT_POST` / `treatment-packet.json`
— immediately preceded by a comment correctly naming the exact
mechanism this report flagged (quotes `Path.cwd()`, cites this
review file by name). Immediately after, a `cmp control-packet.json
treatment-packet.json  # must report a difference` verification
step is present as an explicit instruction (commented, but
unambiguous as a required check). This closes the gap exactly as
Finding 1's "what would need to change" asked for (the `cd`-subshell
option, the simpler of the two named fixes). §11's summary-table row
("against both roots") is unchanged, but that phrasing is no longer
inaccurate now that §5.3 actually defines the mechanism — not a
defect.

**Finding 2 (should-fix) — FIXED.** §1, §5.4, §5.5, and §10 (via the
"§5.4/§5's own instruction" cross-reference) all now state that
`evidence_currency` stays unchanged ("absent" in both pre- and
post-Task-A packets, when `repo_root` is supplied symmetrically) and
that the only mechanically-differing field is `consistency.reasons`'s
own embedded count (3 pre-Task-A vs 2 post-Task-A), which never names
the overlapping-pattern scope by name. The previous "that specific
gap's own wording is gone" framing is gone from every location grepped
(`evidence_currency` appears only in now-consistent contexts: §1's
corrected prose, §5.4 item 2, and the two §5.4 "never ... alone"
warnings). Independently re-confirmed against
`src/codecompass/knowledge_api.py::_knowledge_consistency` (lines
601-627): the `elif profile.known_gap_scopes:` branch sets
`evidence_currency = "absent"` and appends only
`f"{len(profile.known_gap_scopes)} required scope(s) have no passing
evidence at all"` to `reasons` — no scope name anywhere in that
string — matching the plan's corrected claim exactly, including the
"only reached when `unconfirmed_scopes` is empty" precondition the
plan's corrected text relies on for both pre/post states to land in
the same `"absent"` branch.

**Finding 3 (cosmetic) — FIXED.** The
`test_overlapping_patterns_across_combined_sections_counted_once`
comment no longer asserts the unreachable "naive sum of subtotals =
309" scenario. It now describes an implementation that "distrusts the
existing [OR-]gate and adds its own defensive deduplication (e.g.
filtering or excluding a pattern it believes is now 'redundant')" —
the same realistic exclude-based dedup failure mode this review's
Finding 3 verified independently fails 3 of 7 pinned tests — and
explicitly notes the earlier framing was "flagged and corrected by
independent plan review" with a citation to this file. Matches the
"what would need to change" suggestion in substance (slightly more
general phrasing — "filtering or excluding a pattern," not the exact
"moving into `exclude`" wording — but accurate and non-misleading).

**New problems introduced by these specific edits: none found.**
Checked for: stray/inconsistent variable naming between
`PROJECT_ROOT_PRE`/`PROJECT_ROOT_POST`/`REPO_ROOT_REFERENCE` (newly
introduced) and the rest of §5's `$LK`/`$KN`/`$CT` convention — no
collision, used consistently and only within §5.3 as intended; no
leftover `evidence_currency`-changes-pre/post claim anywhere else in
the file (grepped every occurrence); the `reasons`-count framing is
applied consistently across §1, §5.4 (twice), and §5.5; the §6 comment
edit does not introduce any new unreachable-mechanism claim in its
place.

**Updated overall verdict: READY WITH NON-BLOCKING OBSERVATIONS.** All
three findings from the original review are now genuinely closed to
the standard that review asked for; §11's unchanged "against both
roots" phrasing is noted above as a non-issue, not a new observation
requiring further action.

---

## 2026-11-20 — Independent review of the SECOND amendment (control-arm
packet omission / reference-checkout digest incompatibility /
`OracleResult` API correction)

Dispatched separately from both reviews above, to independently
re-derive and skeptically re-check the three further, distinct defects
a second dispatch ("Phase 89C Plan Corrections and Independent
Re-Review") found and fixed in the working tree — none of which the
first review (immediately above) was scoped to catch. Read-only toward
Ledgerkit and this project's real canonical knowledge throughout: every
mutation below ran inside disposable scratch clones/copies under a
session-scratch directory, deleted before this report was written.
`~/projects/ledgerkit` was confirmed clean at
`a7740fd04fe1814d2a557bfcb67a9a775a4a22f9` both before and after this
review; `planning/knowledge/balance-from-spec/` and `planning/
contracts/balance-from-spec/` were read but never written (`git status
--porcelain` against both paths empty before and after). This project's
own working tree showed only the expected pre-existing uncommitted
changes (`CHANGELOG.md`, `planning/ROADMAP.md`, the plan file itself)
both before and after.

### VERDICT: READY WITH NON-BLOCKING OBSERVATIONS

All three defects this amendment claims to fix are genuinely fixed —
each independently reproduced from scratch against real disposable
state, not merely re-read in the plan's own prose. No new defect was
introduced by these specific edits. One pre-existing, non-blocking
observation (already flagged, unrelated to this amendment) is repeated
below for completeness; nothing here is new or blocking.

---

### Defect 1 — control-arm packet omission (§4.1/§7/§8) — FIXED, confirmed by direct reading

Read §4.1's equivalence table, §7.2/§7.3 (arm-dispatch prompts), and
§8.2-§8.3 directly, not just the amendment's own framing text.
Confirmed:

- §4.1's "Tool access" row now reads, for **control**: "`Read`, `Grep`,
  `Glob`, `Bash` ... **plus the one pre-generated `control-packet.json`
  context packet** ..."; for **treatment**: "identical, **plus** the
  one pre-generated `treatment-packet.json` context packet ...
  **neither** arm gets live `codecompass` CLI access ... **Both arms
  receive a packet, via the identical delivery method and the identical
  one-sentence framing**." Both arms genuinely receive a packet; the
  only intended difference is which file.
- §7.2 (control dispatch) and §7.3 (treatment dispatch) use the
  **identical** symmetric sentence: *"Attached is a CodeCompass context
  packet for the knowledge record relevant to this task. You may use
  it, ignore it, or verify its contents against the source."* Neither
  prompt uses a longer or differently-worded sentence for one arm only
  (the defect the amendment's own text says an earlier draft had).
  Neither prompt tells its own arm whether its packet is "control" or
  "treatment," or that a differently-sourced packet exists for the
  other arm.
- §7.4's observable-research-trace requirement no longer lets either
  arm write "n/a" — both are now required to report whether and how
  their own packet informed the dedup decision.
- §7.7's boundary check now audits, for **both** arms, that neither read
  the other arm's clone/report/packet — not scoped to the treatment arm
  only as an earlier draft's text implied.
- Grepped the whole file for every literal `"control"`/`"treatment"`
  occurrence (`grep -n '"control"\|"treatment"'`): every hit is in this
  plan's own internal/author-facing prose (§5.1/§5.2's section headers,
  §1's own narration, §7.2's "never told ... 'control'" sentence, §8.2's
  blinding-hardening narration) — never inside text that would actually
  reach either arm's own dispatch prompt or the evaluator's own
  material. Confirms the fix is genuine, not cosmetic.

**Independent judgment**: this is the correct fix for the defect as
described, and it is actually present in the committed working-tree
text, not merely asserted in the amendment's own narration of itself.

### Defect 2 — reference-checkout digest incompatibility (§5.2/§5.3/§5.4) — FIXED, confirmed by direct, live reproduction of both the fix and the original bug

This is the one claim this dispatch most needed hands-on verification
for, since it concerns a mechanism (`oracle.compute_tree_digest`/
`evaluate_result_precedence`) whose failure mode is silent by
construction. Built a disposable project-pre/project-post pair (copies
of the real `planning/knowledge/balance-from-spec`/`planning/contracts/
balance-from-spec`, real paths never touched), and two disposable
Ledgerkit scratch copies pinned at the real, current
`a7740fd04fe1814d2a557bfcb67a9a775a4a22f9`: one (`ledgerkit-reference`)
with the pinned `test_section_accounts_overlapping_patterns_no_
double_count` test added (confirmed passing directly via its own
`.venv/bin/pytest` first), one (`ledgerkit-pristine`) left untouched.

Ran the real pipeline against `ledgerkit-reference`, exactly as §5.2
specifies: re-synced `tests/test_reports.py`'s content hash into that
clone's own `context-graph.db` (direct sqlite3 `UPDATE`, the established
lighter-weight technique) → `codecompass knowledge detect-changes
balance-from-spec --repo-root ledgerkit-reference --probe-coverage
--json` → `"newly_coverable": [{"check_id":
"overlapping-account-patterns-no-double-count", "claim_id":
"CL-BFS-004"}]` → `codecompass knowledge verify-changes` → a one-item
manifest, `record_id = "CL-BFS-004"`, `contributing_labels =
["newly_covered"]`, citing a real fresh PASS `OracleResult` → accepted
and `codecompass knowledge apply`'d → `CL-BFS-004.yaml`'s
`evidence_support_state` → `supported`, `supporting_evidence` →
`[EV-BFS-001, EV-BALANCEFROMS-004]`, and the new `EV-BALANCEFROMS-004`
record is genuinely `evidence_kind: test`. Confirmed the Claim's own
`statement` text is unchanged byte-for-byte modulo YAML folding
(`" ".join(text.split())`-normalised, identical word-for-word between
pre/post copies) — exactly as §5.2 claims.

Generated both packets via §5.3's now-corrected procedure (explicit
per-call `cd` subshells against `$PROJECT_ROOT_PRE`/`$PROJECT_ROOT_POST`,
both against the single shared `ledgerkit-reference` as
`--repo-root`). `cmp` reported a genuine difference, as required. Ran
the exact §5.4 check (`diff <(jq -S . control-packet.json) <(jq -S .
treatment-packet.json)`); the real output was:

```
30c30
<               "knowledge_revision": "ca41ecd3de586bd22a1b3acec374bde8897858b90b6189eb2251bfe393a3ab29",
---
>               "knowledge_revision": "4c2653a119b05ef9d37405a6f7f9b57e15a6d8b0aad60fba5a3e325beae45e46",
32c32
<                 "3 required scope(s) have no passing evidence at all"
---
>                 "2 required scope(s) have no passing evidence at all"
82a83,102
>           },
>           {
>             "authority": "scoped_verification",
>             ... (EV-BALANCEFROMS-004's own item, consistency, summary) ...
>             "id": "EV-BALANCEFROMS-004",
>             "kind": "evidence",
>             "summary": "A real, independently executed oracle run of the
>             newly-coverable check 'overlapping-account-patterns-no-double-count'
>             passes (newly_covered)."
```

This is **exactly** the three differences §5.4's allowlist names
(category 1: the new `EV-BALANCEFROMS-004` item; category 2: `CL-BFS-
004`'s own `knowledge_revision`; category 3: `reasons`' embedded count,
3 → 2) and nothing else. Independently confirmed category 4 holds:
`CL-BFS-004`'s own `consistency.status` ("unconfirmed") and
`consistency.evidence_currency` ("absent") are byte-identical in both
packets; its own `summary` field is byte-identical; both packets' own
top-level `gaps` arrays are empty in both.

**Then reproduced the original bug directly**, to confirm the fix
actually matters and isn't fixing a phantom problem: re-ran the
identical §5.3 packet-generation calls with `--repo-root` pointed at
the untouched `ledgerkit-pristine` clone instead (same `project-post`
knowledge snapshot, already correctly reconciled — this isolates the
packet-*generation*-time live-reconfirmation failure from the
reconciliation step itself). Result: `CL-BFS-004`'s own
`consistency.reasons` read `["3 required scope(s) have no passing
evidence at all"]` in **both** the pre- and post-Task-A packets —
wrongly stuck at 3, exactly as the plan's own corrected §5.2/§10 text
predicts (the newly-cited `EV-BALANCEFROMS-004`'s `OracleResult`
evaluates `INVALID` against a checkout whose `test_input_digest` for
`tests/test_reports.py` doesn't match what was recorded, so
`matched_pass` never flips and the gap count never drops). Confirmed
the sharper, more dangerous part of the claim too: a `diff <(jq -S .)
<(jq -S .)` between these two *broken* packets still shows real
differences (the new `EV-BALANCEFROMS-004` item is still present in the
treatment packet; `knowledge_revision` still differs, since that's a
hash of the Claim file's own content, unrelated to live
re-confirmation) — so a mechanical check that only asserts "no
unexpected differences outside the allowlist" would see nothing wrong
and **wrongly pass**, exactly as §5.4 item 3 and §10's failure-handling
bullet now explicitly warn. This is precisely why §5.4's own check must
positively assert that `reasons` *differs*, not merely that nothing
unexpected appears — confirmed this requirement is pulling real weight,
not decorative caution.

**One disclosed methodological divergence in my own reproduction, not a
plan defect**: I built `ledgerkit-reference`/`ledgerkit-pristine` via
`cp -r` with `.git` subsequently removed, rather than the `git clone`
§4.2 specifies for the seed clone (§5.2 itself does not pin a mechanism
for `$LK_REF` specifically). Because of this, `_repo_revision`'s own git
probe found no repository at all and fell back to its documented
"working tree (tested_subject_digest=..., test_input_digest=...)"
branch, so my own `EV-BALANCEFROMS-004.repository_revision` reads
`"working tree (...)"` rather than the plan's own stated `"a7740fd0...+dirty
(...)"`. This is a direct, foreseen consequence of `source_reconciliation.
_repo_revision`'s own documented behavior (confirmed by reading the
function: `git rev-parse HEAD` failing/returning nonzero falls through
to the same `"working tree (...)"` string whether that's because of an
`OSError` or a plain non-zero exit) and affects only this one cosmetic
string's exact spelling — every structural claim under test (digest
mismatch → `INVALID`, the fix, the allowlist categories, `reasons`'
count) reproduced identically regardless. Noted for transparency, not
as a finding.

### Defect 3 — `OracleResult` API correction (§6 step 5) — FIXED, confirmed by direct, live reproduction of the exact corrected sequence

Confirmed by direct source read (`src/codecompass/oracle.py`) that the
plan's own characterization of the bug is accurate: `run_pytest_check`
(line 570) really does return `tuple[str, str | None, str]` — bare
`(outcome, invalid_reason, raw_output_text)` — with no `OracleResult`,
no digests, no persistence of any kind; `evaluate_check` (line 833) is
the real API that executes the check internally and returns a
fully-populated `OracleResult` (`run_id`, `tested_subject_digest`,
`test_input_digest`, `oracle_contract_content_hash`, `outcome`,
`raw_output_ref`/`raw_output_sha256`). `write_oracle_result` (line 425),
`parse_oracle_result` (line 341), and `evaluate_result_precedence`
(line 978) all exist with the exact signatures the corrected §6 step 5
names.

Reproduced the corrected sequence directly: implemented
`ReportSpec.with_combined_section` for real (union `accounts`/
`exclude`, same-invert/same-depth check raising `ValueError`, zero-
section raise, no mutation) in a disposable Ledgerkit scratch copy;
added the plan's own pinned, unmodified §6 `tests/
test_combined_section_acceptance.py` (all 11 methods) verbatim; wrote a
disposable `STAGE89C-TASKB-VERIFY` oracle-contract.yaml naming only
`combined-section-no-double-count`; ran:

```
result = oracle.evaluate_check(contract, check, contract_path=..., repo_root=..., raw_output_dir=...)
# -> outcome="PASS", run_id="20261120T144306375671Z-8173f249",
#    tested_subject_digest/test_input_digest/oracle_contract_content_hash all real, non-empty hashes
oracle.write_oracle_result(result_path, result)
reparsed = oracle.parse_oracle_result(result_path)   # reparsed.outcome == result.outcome: True
effective, reason = oracle.evaluate_result_precedence(reparsed, contract, check, contract_path=..., repo_root=...)
# -> ("PASS", None)
```

Exactly as the plan's own text claims. Separately ran `pytest
tests/test_combined_section_acceptance.py -v`: all 11 tests pass
against the correct implementation, and the full pre-existing Ledgerkit
suite (`pytest -q`, 946 tests) shows no regression.

**Acceptance-test completeness gap (the four new §6 methods) — also
independently confirmed discriminating.** Built a second, deliberately
"incorrect" implementation that unions `accounts` but never touches
`exclude` at all. Result: `pytest tests/test_combined_section_
acceptance.py -v` → **exactly one failure**,
`test_union_of_exclude_patterns` (`AssertionError: Items in the second
set but not the first: 'coffee'`), all other 10 methods still pass. Ran
the full suite against this buggy implementation too (`pytest -q`): 1
failed, 945 passed — confirming the new test fails *specifically and
only* the scenario it's designed to catch, not some unrelated
collateral breakage. This matches the amendment's own claim in §6's
comment block precisely.

---

### Verified correct — the remaining items this dispatch was asked to check

- **§3 (Task B's pinned signature/scope/behaviour) is byte-for-byte
  unchanged by this amendment.** Confirmed via `git diff HEAD`'s own
  hunk boundaries: the diff jumps from a hunk ending before §3's own
  text to one starting well after §4 begins — no hunk touches any line
  inside §3. Independently re-read §3 in the current working-tree file
  anyway: the pinned signature, the union/invert/depth-raise rules, the
  "performs no aggregation" sentence, and the honest-fallback framing
  are all identical to what the first review (above) already verified.
- **The pre-registration
  (`planning/retros/phase-89-ledgerkit-two-task-demonstration.md`) is
  unmodified**: `git log --oneline` on that file shows exactly one
  commit (`7dcae8f`), `git status --porcelain` on it is empty. Re-read
  it in full and cross-checked the plan's §2 six invariants against it
  line by line again, independently of the first review's own earlier
  pass — still faithful, including the exact "A tie does not satisfy
  it" wording and the honest-disclosure framing in §3/§8 of the
  pre-registration.
- **§8's blinding hardening genuinely covers filenames, clone paths, and
  report filenames, not only the framing sentence.** §8.2's text
  explicitly specifies `draft-N-packet.json`, `draft-N-report.md`, and
  `draft-N-verify/` (a copy of that arm's own `ledgerkit-verify-*`
  clone) as the neutral material the evaluator receives, with the
  allocation key withheld in a separate file. §8.3 states the one real
  limitation plainly — Evidence content itself (e.g.
  `EV-BALANCEFROMS-004` existing in only one draft's packet) may reveal
  which snapshot is more recent, and this is **not** concealed, since
  the evaluator needs it to do its job — explicitly declining to
  overclaim "perfectly blinded," only "allocation-blinded where
  practically achievable." This is honest, not overclaiming.
- **Section cross-references are internally consistent after the
  renumbering.** §8 now has six numbered items (the hardened blinding
  step inserted as item 2 pushed the former items 2-5 to 3-6); both
  citing locations — §9's "Outcome 2" ("cites the release-phase-
  auditor's own §8.6 report") and §14 item 1 ("including the
  blinding-disclosure audit (§8.6)") — were updated together and both
  correctly point at item 6, the release-phase-auditor dispatch that
  now also does the blinding-disclosure grep. No stale `§8.5` reference
  remains anywhere in the file (grepped).
- **No Stage 89C implementation, Task B execution, or controlled
  comparison was run by this amendment.** §0's status text explicitly
  states the plan remains a planning deliverable, not authorised for
  execution by either dispatch; nothing in the diff adds any claim of
  having actually dispatched either development arm or the
  context-evaluator for real. (My own reproduction work above ran
  entirely in disposable scratch, outside both repositories, exactly as
  the dispatch instructed, and was deleted before this report was
  written — it is this review's own verification activity, not Stage
  89C execution.)
- **Success criterion, scoring scales, and the tie rule are unchanged.**
  Grepped the full `git diff` for any hunk touching §2 invariant 5, §8's
  verdict-production instructions, §9's "Outcome 3" gate text, or §10's
  "Tie" bullet — none appear in the diff; all are verbatim the same as
  the first review already verified. The PASS/PASS WITH GAPS/FAIL and
  LOW/MODERATE/HIGH three-point scales and "never 'partially met'" / "do
  not search for a tie-breaking metric" language are untouched by this
  amendment.
- **No new problems introduced by these specific edits.** Checked
  variable-naming consistency between `$LK_REF`/`$KN`/`$CT` (§5.2) and
  `PROJECT_ROOT_PRE`/`PROJECT_ROOT_POST`/`REPO_ROOT_REFERENCE` (§5.3) —
  consistent and non-colliding, and I exercised them literally via real
  shell variables in my own reproduction with no ambiguity. Grepped for
  leftover "fourth clone"/"fifth clone"/"pristine" references outside
  the deliberate "an earlier draft used..." explanatory passages — none
  found; every occurrence is either explaining the old bug or is my own
  reproduction's intentional negative-control clone. §11's summary table
  was updated consistently with §5.2/§5.3/§6/§8's own corrected text (no
  stale row left describing the old 4-clone/`run_pytest_check`-only
  procedure).

### Summary

All three defects named in this dispatch — control-arm packet omission,
reference-checkout digest incompatibility, and the `OracleResult`
creation API — are genuinely fixed in the current working-tree text,
each confirmed by direct, independent reproduction against real
disposable scratch state (not by re-reading the plan's own narration of
its own fixes). The one originally-bugged behavior (packets silently
staying indistinguishable, or — worse — superficially "clean" under a
naive contamination check, when a pristine reference checkout is used)
was itself reproduced and confirmed to actually occur absent the fix,
establishing the fix is substantive rather than cosmetic. No new defect
was introduced by these specific edits. Combined with the first
review's own already-confirmed "READY WITH NON-BLOCKING OBSERVATIONS"
re-check (above), this plan remains **READY WITH NON-BLOCKING
OBSERVATIONS** — no outstanding blocking finding against the plan as it
now stands in the working tree.

---

## 2026-11-20 — Focused independent review of the THIRD amendment
(two-stage blinding-violation check in §8 item 6; Ledgerkit SHA-pinning
correction in §1/§4.2 step 1/§11)

Dispatched narrowly, per instruction, to review only these two
corrections — not to re-litigate anything the two prior review passes
above already settled. Read-only toward the real `~/projects/ledgerkit`
checkout and this project's real canonical knowledge throughout.

### VERDICT: READY WITH NON-BLOCKING OBSERVATIONS

Both corrections are genuinely sound, correctly worded, and consistent
with the rest of the plan. One minor, non-blocking observation on
stage-one's fixed list (below); no blocking defect found.

### Correction 1 — two-stage blinding-violation check (§8 item 6)

Re-read the exact committed text of item 6 directly (not the amendment's
own narration of it). Confirmed:

- **Stage one's fixed list** — `ledgerkit-control`/`ledgerkit-treatment`
  clone names/scratch paths; `control-packet.json`/`treatment-
  packet.json`; `control-report.md`/`treatment-report.md`;
  `ledgerkit-verify-control`/`ledgerkit-verify-treatment`; the
  allocation-key file; any sentence identifying which draft got which
  snapshot; plus a catch-all for "any other string that names or
  implies the assigned experimental arm specifically." Cross-checked
  against every control/treatment-specific filename or clone name
  actually named elsewhere in the plan (§4.1's tool-access row, §4.2.2's
  fork step, §5.2/§5.3's `$LK_REF`/packet-generation vars — these are
  generic, not control/treatment-labelled, so correctly out of scope —
  §7.2/§7.3/§7.5's dispatch/report paths, §8.1's verify-clone names,
  §9/§11's table rows): every control/treatment-labelled artifact name
  I found is on the list, **except** the per-arm boundary-check report
  filenames (`<NN>-stage-89c-control-boundary-check.md`/
  `<NN>-stage-89c-treatment-boundary-check.md`, §7.7/§11). This is not a
  blocking gap: item 6's own stated scope is auditing "every
  evaluator-visible artifact and instruction" specifically, and the
  boundary-check reports are consumed by the `release-phase-auditor`
  itself (the same dispatch doing this check), never handed to the
  `context-evaluator` (§8.4's evaluator instructions never reference
  them) — so they are outside this check's own declared scope, not a
  missed allocation-bearing path within it. Worth a one-line
  clarification if this plan is amended again, but not worth blocking
  on, and the catch-all clause would flag it anyway if it ever were
  shown to the evaluator.
- **Stage two's wording cannot be read as license to wave away a real
  leak.** The exact text: "A hit **is** a genuine violation, exactly as
  serious as a stage-one hit, when read in context it discloses or
  implies which draft is control versus treatment — stage two exists to
  catch a disclosure stage one's own fixed string list did not
  anticipate, not to relax the standard once a hit looks suspicious.
  **Narrowing the automatic check in stage one must never excuse a
  genuine leak found in stage two**." This is unambiguous in the
  direction the dispatch was worried about — the contextual-judgment
  language is scoped to excluding *harmless* hits, never to excusing a
  confirmed one.
- **Nothing else in §8 is weakened.** The final bullet of item 6
  explicitly preserves, unchanged: neutral `draft-1`/`draft-2` naming,
  random per-run allocation, the allocation key held separate from
  evaluator-visible material, and item 3's own residual-limitation
  disclosure (Evidence content, e.g. `EV-BALANCEFROMS-004`, may still
  reveal which snapshot is more recent — explicitly not itself a
  blinding violation). Re-read items 2-5 directly: all unchanged from
  the prior review's own already-confirmed text.

### Correction 2 — Ledgerkit SHA pinning (§1, §4.2 step 1, §11 "Pin check")

Re-read the exact text in all three locations. The "never silently
substitute" instruction is unambiguous in each: §1 states it four
separate ways (fixed baseline language, the five-step verify/record/
pin/never-substitute/stop-as-blocker sequence, and the parenthetical
confirming no drift as of the amendment session); §4.2 step 1 repeats
the same sequence inline at the point it's actually executed; §11's
"Pin check" row states "confirm the pinned SHA is checkoutable;
separately ... record real `HEAD` for transparency only — never re-pin
to it." All three say the same thing and none leaves room for a future
implementer to read "re-pin" as acceptable.

**Commands verified to actually work**, run independently against the
real checkout:

```
$ git -C ~/projects/ledgerkit cat-file -e a7740fd04fe1814d2a557bfcb67a9a775a4a22f9^{commit}
(exit code 0 — commit exists and is checkoutable)
$ git -C ~/projects/ledgerkit rev-parse HEAD
a7740fd04fe1814d2a557bfcb67a9a775a4a22f9
```

**Grep for stale re-pinning language**: searched the whole file for
`re-pin`, `HEAD`, `advanced` (22 hits total). Every hit is consistent
with the corrected convention — either explaining the old (now-fixed)
bug's own narration ("an earlier draft... instructed a future
implementer to silently re-pin..."), restating the fixed-baseline rule,
or the governance-decision escape hatch ("re-pinning to a different
commit is a separately justified governance decision... never a silent
substitution"). No leftover instruction anywhere tells a future
implementer that advancing to a newer real `HEAD` is an acceptable
default.

**Real checkout state, independently confirmed right now**: `git -C
~/projects/ledgerkit rev-parse HEAD` → `a7740fd04fe1814d2a557bfcb67a9a775a4a22f9`
(exact match to the pinned SHA); `git -C ~/projects/ledgerkit status
--short` → empty (clean). No drift has occurred; this is not currently a
blocking fact.

**Sanity-check of assumed Ledgerkit content at the pinned commit** (not
a full re-derivation — the prior two reviews already did that):
`planning/contracts/balance-from-spec/oracle-contract.yaml` has exactly
three `required: true` checks (`single-section-expense-subtotal`,
`multi-section-income-expense-subtotal`,
`overlapping-account-patterns-no-double-count`), all three sharing
`test_input_paths: [tests/test_reports.py, tests/fixtures/
filtered.journal]` — matches the plan's digest-compatibility claim
exactly. `ledgerkit/models.py`'s `ReportSection`/`ReportSpec` remain
frozen dataclasses with no `@classmethod`/`@staticmethod` and no
`combined_section`/`with_combined` reference anywhere. `tests/
test_reports.py` has no `test_section_accounts_overlapping_patterns_
no_double_count` method defined (only cited by the contract's
`check_reference`, consistent with "Task A's test has never been added
to the real checkout"). `tests/fixtures/filtered.journal` confirms
groceries £150.00, coffee £9.00, housing/rent £1,200.00, two £3,000.00
salary postings (£6,000.00 income) — matches every fixture amount the
plan's §6 acceptance test and its worked arithmetic (159.00, 1350.00,
1359.00, 6000.00) depend on. Nothing has drifted since the prior two
reviews.

### Conclusion

Both corrections are real fixes, correctly and unambiguously worded,
and consistent with the rest of the plan. The real Ledgerkit checkout's
current `HEAD` matches the pinned SHA exactly as of this review, so
there is no blocking fact outside the plan text either. **Verdict: READY
WITH NON-BLOCKING OBSERVATIONS** (the boundary-check-filename omission
from stage one's fixed list, noted above, is the only observation, and
it is non-blocking).
