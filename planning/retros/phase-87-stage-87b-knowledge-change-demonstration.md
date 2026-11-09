# Phase 87 Stage 87B retro — Genuine knowledge-change demonstration, concurrency guard, and comparator

- **Date:** 2026-11-07
- **Commit(s):** `0f6a268` (the implementation this demonstration ran
  against), plus this retro's own closeout commits.
- **Agents used:** `Plan` (three independent planning-review rounds —
  §P/§Q/§R), `general-purpose` (×5 real dispatches: the compiled-arm
  semantic-support and editorial-quality reviews, the comparator-arm's
  own draft-writing dispatch, and its semantic-support and
  editorial-quality reviews).

## Where we are

Stage 87A (knowledge compilation, one bounded section) and Stage 87A's
own hardening pass are both complete and independently audited. Stage
87B's plan was independently reviewed and corrected three times (§P:
two blocking factual errors found and fixed; §Q: seven further
findings found and fixed; §R: five more findings found and fixed,
including a materially strengthened publication-concurrency design)
before this governing task explicitly authorised implementation. This
retro covers the real, end-to-end knowledge-change demonstration
(plan's own §O.E) and its comparator — the deliverable the plan's own
stage gate treats as mandatory evidence, not optional polish.

## Goal

Demonstrate, against real production knowledge and a real,
independently-verified gap, that CodeCompass can detect a genuine
knowledge change, correctly re-verify and republish the affected
section, and reconcile cleanly afterward — while never touching
production canonical knowledge directly (an isolated git worktree) and
never silently suppressing or altering the real, unrelated
`intermediate-knowledge-layer` `doc_candidate` finding that predates
this stage entirely.

## What was achieved

**The knowledge gap was real, not manufactured.** `CL-CTXT-005`'s own
statement described `sync_vendor`'s digest rendering but never
mentioned its real, already-implemented, already-tested
clone-failure fallback (`src/codecompass/sync.py:128-153`, exercised
directly by the real, passing
`test_sync_vendor_source_resolution_failure_falls_back_to_local_snapshot`,
`tests/test_sync.py:275-298`) — confirmed by direct reading before
this demonstration began, not assumed.

**The full real cycle ran in an isolated `git worktree`
(`/tmp/codecompass-stage87b-demo`, branch `stage87b-demo-worktree`,
discarded after the demonstration per the plan's own instruction),
never touching the live repository's own `planning/knowledge/`:**

1. `CL-CTXT-005.yaml` amended in place (new `EV-CTXT-021` evidence
   added, citing the exact source/test lines above) — the real
   controlled lifecycle, not a hand-waved shortcut.
2. `detect_grounded_region_changes` correctly reported `claims_changed`
   for `readme-md-vendor-digest-concept` and, unaffected,
   **`doc_candidate` for `intermediate-knowledge-layer`** — unchanged
   from before the amendment, confirmed by direct comparison.
3. `docs compile` produced a real draft from the amended knowledge
   (one real clean-room broker call).
4. Two independent reviews — semantic-support/completeness and
   editorial-quality, dispatched exactly as Stage 87A's own precedent
   requires — both passed **on the first attempt** (see "Comparator"
   below for why this is noteworthy, not merely lucky).
5. `docs record-review` persisted both verdicts, hash-bound to the
   exact draft/evidence/schema identity.
6. `docs publish` **exercised the new publication-time concurrency
   guard for real** — `claims_changed` → proceed, exactly as
   specified — and published successfully.
7. A subsequent `docs maintain` reported `noop` for the republished
   region and, still, `doc_candidate` for `intermediate-knowledge-
   layer` — reconciliation genuinely correct, not merely hoped for.
8. A byte-for-byte `diff` against the pre-demonstration `README.md`
   confirmed **every line outside the one republished region is
   identical** — not asserted, directly diffed.
9. Exactly one reconciliation manifest exists in the worktree
   afterward — the same, real, pre-existing one from Stage 87A's own
   demonstration — confirming the idempotency fix held throughout a
   real multi-step run, not only in a synthetic unit test.

**The real, published update** (full text in
`planning/retros/phase-87-stage-87b-knowledge-change-demonstration-evidence/`):
a new second paragraph describing the clone-failure fallback, added to
the "Digest" section (the compiler also renamed the heading from
"Understanding Digests" to "Digest" — a stylistic choice of the
model's own, not a factual change, left as-is since the independent
editorial review raised no objection to it).

## Comparator (plan's own §O.E, corrected per finding A)

A separate, isolated worktree (`/tmp/codecompass-stage87b-comparator`,
also discarded afterward) was seeded with the **identical** starting
revision and the **identical** knowledge amendment, and a fresh
`general-purpose` dispatch was asked to perform the *exact same task* —
update `README.md`'s digest section to reflect the new fact — with no
compiler, no schema, no citation tags, no clean-room isolation,
directly editing the file by hand. Confirmed afterward: it touched
only the one section, preserved the grounding markers exactly, and
touched no other file.

**Real result, not fabricated or cherry-picked**: the comparator's
draft **passed** independent semantic-support review (every sentence
traced to `CL-CTXT-005` and independently re-verified against the real
code/tests) but **failed** independent editorial review — for a
register problem ("the Digest doesn't simply go missing or silently
render as if the clone had succeeded... so a Digest built this way is
distinguishable...") that reads exactly like an audit-report
conclusion rather than plain documentation prose. This is, point for
point, the same failure mode Stage 87A's own writing contract
(`compile_doc_section.build_system_prompt`) was specifically,
surgically hardened against after its own real 3-round demonstration
(filed as `L-119`). The compiled arm's draft passed the identical
editorial bar on its first attempt.

**Honest limits of this comparison, stated plainly**: this is one
real case, not Stage 87C's own matched-baseline experiment — no
blinding, no pre-registered rubric, no statistical claim. It is not
evidence that the compiler always outperforms direct human/agent
editing; it is evidence that, on this one real task, the compiler's
own accumulated editorial-quality guardrail caught a genuine register
problem a general-purpose dispatch reproduced independently, and the
compiler's own output did not have that problem. Whether this
generalises is exactly Stage 87C's own question to answer, not this
stage's.

## Bounded cost/value log

| Step | Dispatch | Tokens | Tool uses | Wall-clock |
|---|---|---|---|---|
| Compiled arm: draft compile | 1 real clean-room broker call | not captured (the broker's own response usage was not surfaced by this CLI invocation — disclosed as unavailable, not estimated) | — | not separately timed |
| Compiled arm: semantic review | 1st attempt | **lost to a transient rate-limit error, no result delivered** | — | — |
| Compiled arm: semantic review | 2nd attempt (succeeded) | 55,673 | 5 | 89.3s |
| Compiled arm: editorial review | 1st attempt (succeeded) | not captured (usage data for this dispatch was not surfaced before a later, unrelated rate-limit interruption — disclosed as unavailable) | — | — |
| Comparator arm: draft writing | 1 dispatch | 49,754 | 10 | 42.2s |
| Comparator arm: semantic review | 1 dispatch | 55,642 | 8 | 86.9s |
| Comparator arm: editorial review | 1 dispatch | 40,933 | 1 | 47.5s |

- **Rejected drafts**: compiled arm, 0 (contrast with Stage 87A's own
  real demonstration, which needed 3 rounds before a passing draft —
  this is anecdotal, not a controlled before/after comparison, since
  the writing contract itself changed between the two demonstrations).
  Comparator arm: its own single draft failed editorial review; no
  second attempt was made (out of scope for this comparator's own
  task, which is to produce one draft under the same conditions the
  compiler's own one real attempt had).
- **Factual errors found before publication**: zero, in either arm —
  both drafts' claims held up to independent, code-level
  re-verification.
- **Human correction effort**: zero manual edits to the compiled
  draft (it was published exactly as the model produced it, having
  passed both independent reviews). Zero manual edits attempted on the
  comparator's draft either (this retro reports its failure; fixing it
  was not this comparator's own task).
- **Maintenance effort after the real knowledge change, end to end**:
  one real worktree setup, one knowledge amendment, one compile call,
  two review dispatches, one publish, one maintain run — completed in
  a single session with zero rejected drafts, materially less overhead
  than Stage 87A's own first real demonstration (three compile rounds,
  six review dispatches).
- **Resulting documentation usefulness**: both the knowledge-compiled
  update and the onboarding-exercise evidence (§O.F criterion 2,
  reported in the implementation closeout) describe genuinely real,
  independently-verified system behaviour; the compiler's own
  published section is, per the editorial-quality comparator finding
  above, measurably cleaner on this one case.

## What worked

- **A single, well-evidenced, genuinely-searched-for knowledge gap**
  (not a placeholder) made the entire demonstration honest end to end
  — every reviewer's own independent re-verification against the real
  source/test lines came back clean because the fact itself was real.
- **The isolated-worktree design held up exactly as specified**: the
  real production `planning/knowledge/codecompass-domain/` was never
  touched; `git worktree remove` cleanly discarded both arms afterward
  with nothing left behind.
- **The idempotency and project-wide-discovery fixes (§O.D points 1-2)
  were exercised for real, not only in unit tests**: the pre-existing
  `intermediate-knowledge-layer` candidate was detected, left alone,
  and never duplicated across the whole multi-step real run.
- **The new publication-time concurrency guard (§O.D point 3) was
  exercised for real on its `claims_changed`-proceeds branch** — the
  first time this code path ran against anything other than a
  synthetic fixture.
- **The comparator's own failure is itself the most valuable single
  finding of this whole exercise**: independent, real evidence that
  the compiler's accumulated editorial hardening is not vacuous —
  it would have caught, on this held-out case, exactly the register
  problem it was built to catch.

## What didn't work

- **A transient rate-limit error interrupted the first semantic-review
  dispatch**, delivering no result at all; a straightforward retry
  succeeded. Not a defect in the pipeline itself, but worth naming:
  the orchestrator (the lead) must treat a dispatch that returns no
  result as needing a retry, never as an implicit "unsupported" or
  "fail," which would have been a false negative here.
- **Two dispatches' own token/tool-use/duration usage data were not
  captured** (one lost to the same rate-limit interruption, one
  simply not surfaced before it). Disclosed honestly above rather than
  estimated or omitted silently.
- **The real clean-room broker call's own usage/cost figures are not
  currently surfaced by `docs compile`'s CLI output at all** — a real,
  named gap in this stage's own cost-accounting instrumentation,
  distinct from the rate-limit-related gaps above. A future pass could
  have `compose_section`/`docs compile` print the broker response's
  own `usage` field if present, closing this gap without needing new
  infrastructure (the data already exists in the broker's own
  response, just never printed or logged).

## Lessons learnt

No new candidate learning filed from this demonstration specifically
— the one real process point above (treat a dispatch returning no
result as needing a retry, not as a verdict) is already covered by
ordinary agent-dispatch hygiene rather than being a new, generalisable
rule for this project's own learning log.

## Process-improvement feedback

The agent-led workflow's own independence discipline produced its
single most concrete piece of evidence yet that it matters in
practice: the comparator — written by a dispatch with no awareness of
Stage 87A's own writing-contract hardening — independently reproduced
the exact register problem that hardening targeted, and a third,
independent reviewer (also with no such awareness) caught it. Neither
the comparator nor its own reviewer were primed to find this; the
match is real, not engineered.

## Where we're going

This real knowledge-change demonstration and its comparator, together
with the earlier concurrency/idempotency/harness work (commit
`0f6a268`), complete Stage 87B's own mandatory real-demonstration
requirements. Remaining before Stage 87B can be marked complete: a
`docs-reconstructor` drift audit, an independent `release-phase-
auditor` pass against the final implementation commit, and the usual
`CLAUDE.md` §5 paper trail (`CONTEXT.md`, `ROADMAP.md`, `CHANGELOG.md`).
Stage 87C (the complete publication suite, the real matched-baseline
experiment) remains separately planned, not authorised, and untouched
by this stage's own work.

**One further, honestly-disclosed item, not acted on in this stage**:
`CL-CTXT-005`'s real amendment (the clone-failure-fallback fact) is a
genuine, evidence-backed improvement to this project's own actual
canonical knowledge — it was not fabricated for this demonstration,
and the underlying fact is true of the real, current codebase. It was
deliberately *not* merged into production `planning/knowledge/
codecompass-domain/CL-CTXT-005.yaml` as part of this stage, per the
plan's own explicit "never against production canonical knowledge"
instruction for this demonstration. Whether to separately propose this
as a real knowledge-curation candidate is a decision for the lead/user
outside this stage's own authorisation — named here explicitly so it
is not lost, never silently decided either way.

## Addendum: independent audit FAIL, fix, re-audit (2026-11-07, same day)

An independent `release-phase-auditor` pass against the implementation
commit (`0f6a268`) plus this closeout's own uncommitted changes
returned **FAIL** on one real, genuinely consequential gap, after
confirming everything else (full suite, strict validators, the
doc-drift fixes, the learnings triage, scope boundaries, protected-file
drift) held up under direct re-verification. Full audit trail:
`planning/retros/_audit-phase-87-stage-87b.md`.

**The finding**: the plan's own §O.D point 3 named six required
regression tests for the publication-time concurrency guard. Only four
existed. The missing one — "two concurrent `docs publish` invocations
against the same project serialise correctly through the lock" — had
survived three independent planning reviews (including §R, the same
day as implementation) without ever being built.

**Writing the missing test surfaced a real, previously-undetected
implementation gap, not just a missing test.** Reproduced directly
before fixing anything: a document mutation injected between the
initial `detect_grounded_region_changes` call (inside the lock) and
the write itself was silently overwritten — the "write-boundary
revalidation" the plan and this stage's own closeout both claimed
existed in fact ran only once, before the decision, with nothing
re-checking the live state a second time immediately before the write.
The same gap existed on the knowledge side: a cited record changing in
that same window was indistinguishable, to the existing mechanism, from
a legitimate `claims_changed` republish, because `claims_changed` is
*supposed* to be allowed — only the separate, pre-lock evidence/schema-
section freshness check could tell a fresh republish apart from a
now-stale one, and that check was never re-run inside the lock either.

**Fix**: both checks (the grounded-region detect-and-decide, and the
evidence/schema-section freshness check) now run a second time, inside
the lock, immediately before the write — not only before the lock is
acquired. This narrows, but — disclosed honestly in `_doc_publish_
lock`'s own docstring rather than assumed away — does not fully close,
the remaining window between that second check and the write itself;
a full transactional write would close it completely and was
deliberately not built, matching this stage's own smallest-coherent-
change instruction. Three new regression tests, all confirmed to fail
against the pre-fix code first: the concurrency test (`max_concurrent
== 1`, confirmed `2 == 1` with the lock disabled); a document-edit-at-
the-write-boundary test (confirmed the human edit was clobbered before
the second check existed); a cited-knowledge-change-at-the-write-
boundary test (same confirmation, knowledge side). Full suite: 1337
passed, 2 skipped (up from 1334). Ruff, `check_doc_schema.py --strict`,
`check_user_docs.py --strict` all re-confirmed clean.

**Two secondary, non-blocking observations, also corrected**: the
implementation commit's own message claimed "47 new regression tests"
(real delta: 40, confirmed by the auditor via `git diff` and the
1294→1334 suite count) and "6 pre-existing [ruff findings]" (real:
176, confirmed via a disposable comparison worktree at the pre-
implementation commit — the conclusion, no regression introduced, was
correct; the number was not). Not amended in the already-written
commit message (this project's own established practice carries a
discovered inaccuracy forward as a correction in the changelog/retro
rather than rewriting commit history); corrected in `CHANGELOG.md`'s
own Stage 87B entry instead.

**Re-audit**: a fresh `release-phase-auditor` dispatch, re-verifying
the fix directly rather than trusting this account, returned **PASS**
(see below). Stage 87B's own closure is genuinely gated on that
second, clean pass — not on this fix being merely applied.

No change to the real knowledge-change demonstration or comparator
findings above; both ran and were verified before this concurrency
gap was found, and neither touches `docs publish`'s concurrency guard
in a way this fix affects (the demonstration's own publish call
exercised the `claims_changed`-proceeds branch with no concurrent
writer and no intervening mutation — the scenario this fix addresses
never arose there).

## Addendum 2: post-closeout hardening pass — three further integration defects (2026-11-09)

A fresh review of this already-closed, already-PASS-audited work
found three further integration defects in the publication mechanism
itself — none in the real demonstration's own generated content, all
in the publish-time safety mechanics layered around it. Each was
reproduced directly against the then-current (`e0de671`) code before
any fix was written, per this project's own standing real-vs-synthetic
discipline, using standalone, disposable reproduction scripts (not
pytest tests) kept outside the repository.

**Finding A — reviewed-draft integrity, confirmed real.** `docs
compile` persists `tagged_draft` (what both independent reviews are
actually bound to, via `draft_sha256`), `draft_body` (the citation-
stripped text `docs publish` writes), and `draft_sha256` (`sha256
(tagged_draft)`) into the pending manifest. `docs publish` validated
that a persisted review record's own `draft_sha256` field matched the
*manifest's* own `draft_sha256` field — but never that the manifest's
own `draft_sha256` field actually matched a fresh hash of its own
`tagged_draft` text, and never that `draft_body` was actually the
deterministic, citation-stripped form of that same `tagged_draft`.
Reproduced directly: a standalone script compiled a section, recorded
both passing reviews, then rewrote only the pending manifest's
`draft_body` field (leaving `tagged_draft`/`draft_sha256` untouched) to
attacker-controlled text never seen by either review — `docs publish`
exited 0 and published that exact unreviewed text. Fixed: `docs
publish` now independently recomputes `sha256(tagged_draft)` and
compares it against the manifest's own `draft_sha256` (catching a
tampered hash or a rewritten `tagged_draft` wearing a stale hash),
recomputes `strip_citation_tags(tagged_draft).strip()` and compares it
against `draft_body` (catching a tampered `draft_body` directly), and
always publishes the *recomputed* body — `pending["draft_body"]` is no
longer read for the write at all. This integrity check runs once
before the lock (fail fast) and again, against a **freshly re-read
copy of the manifest file itself** (not the in-memory snapshot loaded
before the lock), as the very last check immediately before the write
— closing a second, narrower variant of the same defect: a manifest
*replaced in its entirety* (e.g. by a concurrent `docs compile` rerun)
after the already-matched review records were validated against the
original snapshot, but before the write. The re-read cross-checks the
fresh manifest's own `draft_sha256`/`evidence_sha256`/
`schema_section_sha256` against the originally-validated snapshot's,
refusing on any difference.

**Finding B — live schema freshness, confirmed real.** The write-
boundary re-check added by the first hardening pass (Addendum 1)
re-ran `_evidence_staleness_error`, but that function closed over
`section`/`schema` objects parsed *once*, at the top of `docs_publish`,
from the schema file as it was before any lock was even considered —
calling the same function again proved nothing, since nothing inside
it ever read the schema file a second time. Reproduced directly: a
standalone script compiled and reviewed a section, then — via a
monkeypatched first call to `detect_grounded_region_changes` — widened
the live schema's own `min_claim_status` for that section mid-publish;
`docs publish` exited 0, publishing against a schema requirement that
had already changed underneath it. Fixed: `_evidence_staleness_error`
now reads `schema_path` from disk and re-resolves the section fresh on
every single call, including both the pre-lock fast-path call and the
two inside-the-lock calls — a schema mutation landing at any point
before the write is now genuinely visible to whichever re-check runs
after it, not merely assumed caught by an already-stale object.

**Finding C — residual document-write race, narrowed further.** The
first hardening pass's own re-check (detect-based) left a smaller,
honestly-disclosed window between that re-check and the write itself.
This pass adds a second, independent narrowing: a new
`doc_compiler.document_identity(doc_path)` (a content hash, or
`"absent"`) is captured by `docs_publish` immediately before calling
`publish_section`, which now accepts that snapshot as
`expected_document_identity` and re-checks it internally, immediately
before composing the new text — raising a new `DocPublishConflictError`
on mismatch, never writing. Reproduced directly: a standalone script
confirmed a mutation landing strictly *after* the detect-based
write-boundary re-check (a scenario the detect-based check cannot see
at all, since `detect_grounded_region_changes` is never called a
third time) still clobbered the document before this identity check
existed, and is refused after. Separately, `publish_section`'s actual
writes now go through a new `_atomic_write_text` (write-to-temp-file-
then-`os.replace`) instead of a direct `Path.write_text` call, so a
crash or interruption mid-write leaves the original file intact
rather than truncated — confirmed by a test that makes `os.replace`
raise mid-call and checks the original content survives with no
leftover temp file. **Full protection was not achieved, and is not
claimed**: the window between `publish_section`'s own internal
identity re-check and its own write — a few lines of plain, synchronous
Python with no OS-level cross-process file lock — remains open, is
disclosed in both `publish_section`'s and `_doc_publish_lock`'s own
docstrings, and is recorded as an explicit follow-up (`L-124`) rather
than silently assumed closed. A full transactional write (or a
cross-process lock held by every editor of the target document, which
this project cannot impose on a plain text editor) would close it
completely and was deliberately not built, matching this stage's own
smallest-coherent-change instruction for a second time.

**Verification.** 15 new regression tests (5 in `tests/test_cli.py`,
10 in `tests/test_doc_compiler.py`). 14 of the 15 testing new mechanism
behavior were directly confirmed to fail against the pre-fix code
(`e0de671`, isolated via a disposable `git worktree` with `PYTHONPATH`
pointed at its own `src/` — not the editable-installed main-repo
source, which the venv's `.pth` file points at by default and would
otherwise silently run the already-fixed code) and pass against the
fix; the 15th (a determinism property already true pre-fix) correctly
passes in both regimes and was never expected to catch anything. One
process note, not a count correction: the manifest-swap test's own
*first draft* passed in both regimes for the wrong reason — a `mkdir`
`FileExistsError` crash from re-running the setup helper on an
already-existing directory, not genuine detection — caught by checking
*why* it passed, not just *that* it passed, and rewritten to construct
the swap directly instead; the version actually committed is one of
the 14 genuine catches, confirmed directly both in this session and,
independently, by the fresh audit below. (An earlier draft of this
section mistakenly still counted it among "the other 2," undercounting
the real catches as 13 — corrected here to the true figure, 14, after
the first audit of this pass caught the error.) Full suite: 1352
passed, 2 skipped (up from 1337, exactly +15). `ruff check .`: 176
findings, identical pre-existing set, none in changed files except one
`E501` in this pass's own new test, fixed. `check_doc_schema.py
--strict`, `check_user_docs.py --strict`, `check_knowledge_base.py`,
`check_knowledge_placement.py`, `check_contracts.py`,
`check_self_knowledge_quality.py`: all clean or showing only
pre-existing, unrelated findings (confirmed by direct inspection of
each finding's own file path and content, not assumed).

**Secondary item — canonical knowledge.** The real `CL-CTXT-005` gap
this stage's own disposable-worktree demonstration found (`sync_
vendor`'s clone-failure fallback) was re-derived independently, fresh
against production `src`/`tests` (not copied from the demonstration's
own discarded worktree record), as `EV-CTXT-021` (`status: current` —
evidence has no `candidate` tier in this project's closed status
vocabulary; `candidate`-style staging lives at the claim-amendment
level). Filed as `L-123`, proposing the textual amendment through the
ordinary evidence → candidate → reconciliation workflow — `CL-CTXT-005`
itself is left untouched; a successful demonstration having run through
this exact fact two days ago is explicitly not treated as maintainer
acceptance of it.

**Secondary item — documentation coverage, restated honestly.** Stage
87B still contains exactly one genuinely knowledge-compiled section
(the README.md section the real demonstration itself compiled,
reviewed, and published through the pipeline). `docs/getting-
started.md` remains schema-governed and factually verified, not
knowledge-compiled — this pass did not change that, and does not
claim it did.

**Secondary item — cost telemetry (`L-122`).** Already tracked
accurately in `planning/ROADMAP.md`'s "Future-improvement backlog"
table; confirmed still present and unresolved. No direct fix attempted
this pass — retained as an explicit Phase 87C planning input per the
governing task's own instruction, rather than expanding this narrow
hardening pass's scope.

**Pre-existing reconciliation state, confirmed preserved.** The
pre-existing `intermediate-knowledge-layer` `doc_candidate` manifest
(`planning/knowledge/codecompass-domain/reconciliation/
20261104T081241Z-doc.toml`) still exists, exactly one file, untouched
by anything in this pass.

**Audit, first pass (commit `1e3301f`): FAIL.** A fresh, independent
`release-phase-auditor` dispatch re-verified the three findings and
their fixes directly — reproducing 14 of the 15 new tests failing
against a disposable `git worktree` at the pre-fix commit and passing
after the fix, re-running the full suite (`1352 passed, 2 skipped`,
confirmed), re-running every strict validator, and confirming
`EV-CTXT-021`'s cited source and test are both real — and found the
underlying code and tests fully correct. It still returned **FAIL**:
`CHANGELOG.md`'s own hardening-pass entry, as originally committed,
stated an independent audit had already run and returned PASS, citing
the original (pre-this-pass) audit file — before any audit of this
specific fix had actually been dispatched. This is the exact
self-certification pattern the agent-led-development model exists to
prevent, caught correctly regardless of the (confirmed sound)
underlying work. The entry's "13 of 15" test accounting was also
corrected in the same pass (true figure: 14 — see the Verification
paragraph above). Full account: `planning/retros/_audit-phase-87-
stage-87b-hardening.md`. Fixed here (the premature PASS claim and
stale citation removed from `CHANGELOG.md`, replaced with an honest
"pending re-audit" statement) in the same session the FAIL was
returned, as its own separate commit (`9cdbb6f`).

**Re-audit (commit `9cdbb6f`): PASS.** A fresh, independent
`release-phase-auditor` dispatch confirmed the narrative correction
was exactly scoped (only `CHANGELOG.md` and this retro touched, no
code/test), confirmed no remaining premature-audit claim or stray
"13" count anywhere in either file's Stage 87B hardening content,
independently re-read the key mechanisms in `doc_compiler.py`/`cli.py`
rather than trusting the first audit's own account, and independently
re-ran the full suite (`1352 passed, 2 skipped`, exactly matching) and
every strict validator itself. No protected-file drift across the
full span since Stage 87B's own prior closeout (`e0de671` through
`9cdbb6f`). Full account: `planning/retros/_audit-phase-87-stage-87b-
hardening-reaudit.md`. **Stage 87B's post-closeout hardening pass is
closed.**

## Addendum 3: a second, further publication-integrity defect — top-level schema fields bypassed review binding (2026-11-09, same day)

A fresh code-inspection review of this already-twice-hardened `docs
publish` path, run independently of Addendum 2's own three findings,
raised a suspected fourth defect: `schema_section_sha256` (the hash
every persisted review record and the pending manifest are bound to)
was computed from **only the section dict**, even after Addendum 2's
own fix bound the *section's own identity* to the live schema on
every re-check. The schema's **top-level fields** — `document` (the
actual publication target), `audience`, `acceptance_criteria` — were
never part of that hash at all, at compile time or at any publish-time
re-check.

**Reproduced directly, before any fix was written**: a standalone
script (kept outside the repository, mirroring this project's own
real-vs-synthetic discipline) compiled a section against a schema
targeting `docs/demo-original.md`, recorded both passing reviews,
then rewrote *only* the schema's own top-level `document` field to
`docs/demo-RETARGETED.md` — leaving the section dict itself
byte-identical — and ran `docs publish`. Result: exit code 0, the
already-reviewed draft published to the new, never-reviewed-against
target; the original target was never created. The defect was real,
not merely suspected.

**Fix**: `doc_compiler.compute_schema_section_identity_sha256(schema,
schema_section)` — one new, shared function binding the section dict
together with the schema's own `document`/`audience`/
`acceptance_criteria` fields into a single hash. `docs compile` now
computes `schema_section_sha256` through this function (previously a
bare `sha256(json.dumps(section))`); `docs publish`'s own
`_evidence_staleness_error` recomputes the identical structure from
the *live* schema on every call (both the pre-lock fast-path call and
the write-boundary call inside the lock, exactly mirroring Addendum
2's own double-check discipline) and compares against the persisted
value. The persisted field name (`schema_section_sha256`) is
deliberately unchanged — this corrects what that identity covers, not
a new field or a second schema system, matching the smallest-
coherent-change instruction.

**A further, related correction**: `document_path` — the actual write
target — was previously resolved once, from the schema read at the
very top of `docs_publish`, and never revalidated against the live
schema at all. `_evidence_staleness_error` now also re-resolves and
returns the live, freshly-validated document path on success; the
write-boundary call site rebinds `document_path` to this live value
immediately before `publish_section` is invoked, so the actual write
always targets a path just reconfirmed against the exact schema state
that was independently checked identical to what was reviewed —
literal compliance with "revalidate the effective document target
against the live schema immediately before publication," not merely
inferred from a hash match.

**Verification.** 11 new regression tests: 6 unit tests for
`compute_schema_section_identity_sha256` itself (determinism; changes
on `document`/`audience`/`acceptance_criteria`/section changes;
unaffected by unrelated fields like `owner`/`schema_version`) in
`tests/test_doc_compiler.py`; 5 in `tests/test_cli.py` — a document
retarget after both reviews passed, an audience change, an
acceptance-criteria change, a retarget landing specifically at the
write boundary (via the same `detect_grounded_region_changes`
monkeypatch pattern Addendum 2's own write-boundary tests use), and a
positive control confirming an ordinary, schema-unchanged publication
still succeeds. All 11 were run against a disposable `git worktree` at
the pre-this-fix commit (`db33327`) with `PYTHONPATH` explicitly
overriding the venv's own editable-install `.pth` file (confirmed via
`codecompass.__file__`, the same discipline Addendum 2 established) —
all 11 fail (`AttributeError`, since `compute_schema_section_identity_
sha256` does not exist pre-fix at all — the same category of
pre-fix failure Addendum 2's own `document_identity`-dependent tests
produced, accepted there for the identical reason: the shared test
helper itself needs the new function to construct a schema-identity-
bound pending manifest, so every test exercising that helper fails
pre-fix uniformly, not only the ones targeting this specific defect).
The defect's own real exploitability was independently confirmed by
the standalone script described above, run against the clean,
unmodified pre-fix commit before any production code was touched.
Full suite and strict validators re-run after the fix; see the
changelog entry and the independent audit this addendum's own fix
requires for the exact, current figures.

**No change to Addendum 1's or Addendum 2's own real demonstration,
comparator, or hardening-pass findings** — this is a fourth, separate
defect in the same publication path, found and fixed independently of
all three.
