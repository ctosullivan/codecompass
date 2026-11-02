# Phase 85 — Independent DoD Audit (`release-phase-auditor`)

**Scope audited:** commit `6e987b0` on `main` (the real current HEAD at
audit time — three commits ahead of the `ff856d6` implementation commit
named in the dispatch prompt: `55f7008` "fix drift findings + promote
L-112/L-113 from closeout triage" and `6e987b0` "promoted.md pointers for
L-112/L-113" had already landed by the time this audit began). Per
`CLAUDE.md` §5 ("against the exact commit about to be marked done"),
this audit evaluates `6e987b0`, not the earlier `ff856d6`, since that is
the real current state of the tree. No commit after this audit's own
pass touches audited scope as of this writing.

**Verdict: FAIL** (one concrete, fixable, non-trivial gap; everything
else checked — including every item this project's own history treats as
historically hardest to get right in a self-curation phase — passed
independent reproduction cleanly). See the numbered fix list at the end.

---

## 1. Both real-dogfood exit gates — independently reproduced

**Positive outcome (`CL-FPSS-009`).** Read `CL-FPSS-009.yaml`,
`DE-FPSS-009.yaml`, `EV-FPSS-024.yaml`, `OBS-FPSS-022/023/024.yaml` in
full. Independently reproduced all three cited probes myself, from a
clean Python process (`python3 -I`, isolated mode, no planted
modules), against the real, unmodified
`src/codecompass/source_symbols.py`:

- Rust split-modifier (`pub\nfn foo()...`): my own run →
  `exposure='internal'` for both `foo`/`Bar` — **matches** `OBS-FPSS-022`
  exactly (including the stated root cause: `_RUST_ITEM_RE` only
  inspects the stripped line where `fn`/`struct` itself appears).
- TS split-export (`export\nfunction foo()...`): my own run →
  `exposure='internal'` for both `foo`/`Bar` — **matches** `OBS-FPSS-023`
  exactly.
- Rust `macro_rules!` template body containing `pub fn generated() -> i32
  { 42 }`: my own run → a genuine false-positive `generated` row,
  `exposure='public'`, `status=indexed_partial` — **matches**
  `OBS-FPSS-024` exactly.

`CL-FPSS-009.status` is `supported` (not left at `proposed`), consistent
with real, reproduced evidence — confirmed independently, not merely
asserted. `knowledge_api.get()`/`trace_evidence()`/`epistemic_status()`
against the live corpus all resolve cleanly with zero gaps for this
Claim (re-run directly, not trusted from the retro's own report).

**Negative outcome (`SCI-001`/`SCI-002`).** Independently reproduced
both cited probes:

- Rust `#[cfg(test)]`-gated fn/mod: my own run → both functions
  correctly classified `exposure='internal'` (neither carries `pub`),
  no misclassification — **matches** `SCI-001`'s own recorded output and
  falsification reasoning exactly.
- TS decorator immediately preceding `export class Foo`: my own run →
  `Foo` correctly classified `exposure='public'`, matching its genuine
  `export class` declaration — **matches** `SCI-002` exactly.

Confirmed via `git log --diff-filter=A -- planning/knowledge/first-party-
source-symbols/` and `git diff --stat` across this phase's full commit
range (`3d9eef5..6e987b0`) that **no** file was added under
`planning/knowledge/first-party-source-symbols/` beyond the six real
promoted records (`CL-FPSS-009`, `DE-FPSS-009`, `EV-FPSS-024`,
`OBS-FPSS-022/023/024`) — nothing orphaned for SCI-001/SCI-002, and the
working tree is clean (`git status --porcelain` empty).

**Both gates independently verified as real, not fabricated or
staged.**

## 2. Independent adjudication — artifact consistency, with a named limit

`CL-FPSS-009.yaml`'s `derived_by: "context-researcher agent dispatch
(Phase 85 self-curation)"`, `status: supported`,
`evidence_support_state: supported` are consistent with the plan's
two-step process (`context-researcher` writes at `proposed` →
`knowledge-curator` independently reproduces/recommends → the lead
applies). The investigation log's `SCI-001`/`SCI-002` `reviewer` fields
name `knowledge-curator`, with substantive, structural reasoning beyond
merely re-stating the probe output (e.g. direct re-reading of
`_RUST_ITEM_RE`'s own anchoring logic to explain *why* the hypothesis
failed, not only *that* it failed) — consistent with genuine independent
reproduction rather than rubber-stamping.

**Named limitation** (as the dispatch prompt itself anticipated):
`git log --follow -p` on `CL-FPSS-009.yaml` shows it was created once,
in `ff856d6`, already at `status: supported` — one atomic commit, not
two discrete stages. This is consistent with (but does not, by itself,
prove) the claimed two-step adjudication — it matches this project's own
established practice of batching a multi-agent dispatch sequence's
artifacts into one commit at the end (e.g. Phase 84's "comparison-mode
alignment pass" commits). Git history alone cannot distinguish "the
adjudication happened and then both were committed together" from "no
real adjudication happened" — the textual internal consistency above
(distinct authorial voices/concerns between `DE-FPSS-009`'s
first-person researcher narration and `SCI-001`/`SCI-002`'s
third-person independent-corroboration narration, each naming its own
distinct uncertainties) is the strongest evidence available to this
audit, and it is consistent with the claim, not merely silent on it.

## 3. The on-demand validator

Ran `python3 scripts/check_self_knowledge_quality.py --strict
--ledgerkit-root ~/projects/ledgerkit` myself (also with the default
`~/projects/ledgerkit` path, same result): **35 findings, exit 1**.
Confirmed every blocking finding is one of the retro's named
pre-existing, out-of-scope items (`CL-ADPT-008` contradiction;
`balance-from-spec` unverified-required-scope/stale-test-citation) or a
genuinely real, newly-surfaced-by-this-script corpus condition
(`missing-evidence` on `REQ-DOCORIGIN-*`/`REQ-HSAPI-*`, both decided
status, correctly blocking per the plan's own severity rule). Confirmed
`missing_contract` is `(info)` for all five contract-free slugs and
absent for `balance-from-spec` — matches §4.C's corrected severity rule
exactly, independently re-read from `decisions/0081` §3 for the stated
rationale.

Ran `tests/test_check_self_knowledge_quality.py` myself: **20/20 pass**.

**One deviation from the plan's own written text, found by direct
reading, not disclosed back into the plan document**: §4.C point 4 of
`planning/phase-85-self-curation-knowledge-quality-validation.md`
explicitly specifies the `test_ref`-file check runs "for every
`test`-kind Evidence record **across every slug**." The shipped
`check_test_ref_files()` (`scripts/check_self_knowledge_quality.py`
lines 200-252) instead scopes this check to **contract-bearing slugs
only** (`if not contract_path.is_file(): continue`), based on a real,
well-reasoned, well-tested discovery made during implementation (four
real, legitimate, pre-Phase-82 Evidence records in non-contract-bearing
slugs use an older plain-pytest-citation convention for `test_ref`, not
a file path, and would otherwise false-positive). This is honestly
disclosed in the retro ("a real scoping gap discovered while running it
against the live corpus, not anticipated by the plan"), in the
implementation commit message, and in `docs/development/
contributing.md`'s own updated catalog entry, and is explicitly covered
by its own regression test
(`test_non_resolving_test_ref_in_slug_without_contract_is_not_flagged`).
**It was never reflected back into the plan document itself** as a
fourth corrective note, unlike every other design change this plan made
during its own three independent review rounds (each of which added a
dated "Corrective note" section). Given this project's own consistent
practice of keeping the plan file in sync with "as-built" reality for
every other deviation in its history, this is a real, if narrow, process
gap — not a functional defect (the behavior is sound, tested, and
honestly documented elsewhere), and not blocking on its own, but named
explicitly as required for completeness (see fix list).

## 4. No change to canonical schemas/modules

`git diff 3d9eef5 6e987b0 -- src/codecompass/knowledge_api.py
src/codecompass/oracle.py src/codecompass/knowledge_intermediate.py` —
**empty**. Confirmed no `src/` file of any kind changed in this phase's
range (`git diff --stat` for `src/` is empty entirely).

## 5. Scope discipline

No file under Phase 86-92's own named territory (MCP, placement policy,
doc compiler, reconciliation, federation) was touched — confirmed by
`git diff --stat 3d9eef5 6e987b0`, 24 files total, all within this
phase's own named deliverables (plan, retro, investigation log, the one
new script + its test file, the workflow doc, two agent-brief additions,
two doc-catalog fixes, changelog, two learnings-lifecycle files, and the
six new knowledge records). No `decisions/*` file touched.

## 6. Full suite and strict validators

- `.venv/bin/python -m pytest -q`: **1158 passed, 2 skipped, 0 failed**
  (314.9s).
- `python scripts/check_user_docs.py --strict`: **no findings**, exit 0.
  (One transient run earlier in this audit showed 2
  `promoted_learnings_logged` findings for L-112/L-113; immediately
  re-run twice more, consistently "no findings" — `promoted.md` does
  contain both pointer lines; treated as audit-environment noise, not a
  real repository defect, since the working tree was confirmed clean
  throughout and the finding did not recur.)
- `python scripts/check_contracts.py --strict --ledgerkit-root
  ~/projects/ledgerkit`: 7 findings, all `(info)`, exit 0.
- `python scripts/check_knowledge_base.py --strict --ledgerkit-root
  ~/projects/ledgerkit`: 24 findings, all `(info)`
  (`knowledge-base-snapshot-current-divergence`), exit 0.
- `python scripts/check_self_knowledge_quality.py --strict
  --ledgerkit-root ~/projects/ledgerkit`: 35 findings, exit 1 (blocking
  findings pre-exist Phase 85 — confirmed below).

**Pre-existing-blocking-finding claim, independently verified**:
`git log --oneline -- planning/knowledge/codecompass-domain/
CL-ADPT-008.yaml` shows its only commit is `f39a986` (Phase 63d) — untouched
by Phase 85. `git log --oneline 3d9eef5..6e987b0 -- planning/contracts/
balance-from-spec/` is empty — nothing under `balance-from-spec`'s
contract/results directory was touched by this phase. Both claims
confirmed true.

## 7. Agent-brief changes stay within their own stated scope

Read `.claude/agents/context-researcher.md` and `.claude/agents/
knowledge-curator.md` in full, and diffed both against pre-phase state
(`3d9eef5..6e987b0`). Confirmed:

- Neither agent's `tools:` frontmatter line changed
  (`context-researcher`: `Read, Grep, Glob, Bash, Write`, unchanged;
  `knowledge-curator`: `Read, Grep, Glob, Edit, Write`, unchanged — no
  `Bash` added).
- `knowledge-curator`'s write boundary gained exactly one new, narrowly
  named path: `planning/retros/phase-85-self-curation-investigation-
  log.md`, outcome 2/3/4 entries only — confirmed by direct reading of
  the diff's own "Hard Rules" section edit.
- Both new mode sections are explicitly gated ("triggers only when a
  dispatch is explicitly framed as a Phase 85 self-curation
  investigation" / "A new, bounded mode — not an extension of the
  triage responsibilities above") — ordinary, non-Phase-85 behavior for
  both agents is unaffected by construction, not merely by claim.

`.claude/agents/release-phase-auditor.md` also gained one new "What to
check" item (13, on running a new validator against its real corpus
before finalizing its test suite) — directly traceable to the promoted
`L-113`, confirmed consistent with `planning/learnings/promoted.md`'s
own entry and `planning/v1-redefinition/agent-led-development.md`'s own
matching addition.

## 8. Protected-file drift

`git diff 3d9eef5 6e987b0 -- CLAUDE.md` — **empty**. No drift.

## 9. Candidate learnings triaged

`planning/learnings/promoted.md` carries real pointer lines for both
`L-112` (resume via `SendMessage`, not a fresh `Agent` call —
`planning/agent-led-workflow.md` step 5) and `L-113` (validator vs. real
corpus before finalizing tests — `agent-led-development.md` §1 +
`release-phase-auditor.md` item 13), both dated 2026-11-03 and pointing
at commit `55f7008`. `planning/learnings/inbox.md` carries both
candidates' full entries. `check_user_docs.py --strict` confirms no
pointer-line gap (see §6 above). **Triaged, not outstanding.**

---

## Additional observation: missing per-phase drift-audit report

Every phase from 41 through 84 in this project's history has a
persisted `planning/retros/_drift-audit-phase-N.md` (or a clearly
corrective-pass-suffixed variant) documenting the independent
`docs-reconstructor` pass's findings and final verdict — a 44-phase
unbroken convention, confirmed by `ls planning/retros/_drift-audit*`.
**No `planning/retros/_drift-audit-phase-85.md` (or equivalent) exists.**

This project's own `release-phase-auditor` brief (the governing document
for this very audit) names, as item 3 of "What to check": *"An
independent `docs-reconstructor` per-phase drift audit ran and its
verdict is `NO DRIFT` (or every finding it raised was fixed by
`docs-maintainer` and re-audited). **The audit report exists.**"*
`CLAUDE.md` §5 itself conditions "done" on "an independent
`docs-reconstructor` per-phase drift audit finds no current-truth doc...
left misdescribing the system" as one of the preceding conditions this
audit must verify, "against the exact commit about to be marked done,
rather than trusting the implementing agent's report."

The underlying audit substantively appears to have run: commit
`55f7008`'s own message states "docs-reconstructor found two
non-blocking drift findings: contributing.md's maintainer-tooling
catalog and testing.md's test-module enumeration both omitted
check_self_knowledge_quality.py. Fixed[.]" — and I independently
confirmed both fixes are real, accurate, and present in the current tree
(§3 above; `docs/development/contributing.md`'s own updated catalog
entry correctly and honestly documents the contract-bearing-only scoping
decision; `docs/development/testing.md`'s test-module list now includes
`tests/test_check_self_knowledge_quality.py` and is explicitly marked
non-exhaustive). **But there is no standalone, independently-checkable
artifact recording that pass's full scope and final verdict**, unlike
every other phase in this project's history. I cannot, from the commit
message alone, confirm the audit's full scope (e.g., whether
`architecture/`, `README.md`, `ai-docs/` were checked at all, not only
the two files whose fix is visible) the way a persisted report would let
a later reader confirm.

This is the one concrete, checkable gap driving this audit's **FAIL**
verdict — not a defect in the phase's actual implementation, evidence,
or test coverage (all of which independently reproduce cleanly), but a
missing DoD artifact this project's own governing documents require to
exist, with an unbroken 44-phase precedent of doing so.

---

## Required fixes before re-audit

1. **[Blocking]** Create `planning/retros/_drift-audit-phase-85.md`,
   matching this project's own established convention (see e.g.
   `planning/retros/_drift-audit-phase-84.md` for shape/depth), covering
   the real `docs-reconstructor` pass's full scope against everything
   Phase 85 touched (`docs/workflows/self-curation-loop.md`, the two
   agent briefs, `docs/development/contributing.md`/`testing.md`, and
   confirming no other current-truth doc was left misdescribing the
   system) and its final verdict (`NO DRIFT`, post-fix, given the two
   findings already fixed in `55f7008`). If re-running `docs-
   reconstructor` fresh against the current tree is preferred over
   reconstructing the already-completed pass's own record, that is
   equally acceptable — either way, the artifact must exist before this
   phase is marked `done`.
2. **[Non-blocking, but requested for completeness]** Add a fourth,
   dated "Corrective note" to `planning/phase-85-self-curation-
   knowledge-quality-validation.md` (matching the shape of its existing
   three) documenting the real, as-implemented scoping of the
   `test_ref`-file check (§4.C point 4) to contract-bearing slugs only,
   with the same rationale already given in the retro/commit
   message/`contributing.md` — so the plan's own written acceptance
   criteria match the as-built system, consistent with this project's
   practice for every other design deviation in this plan's own history.

Once (1) is in place (and, ideally, (2) alongside it), this phase's
substantive work — the real dogfood (both outcomes independently
reproduced by this audit), the validator's severity design and test
coverage, the agent-brief scope discipline, the absence of any
`src/`/`decisions/`/`CLAUDE.md` drift, and the learnings triage — is
solid and should re-audit cleanly on this one remaining point.

---

# RE-AUDIT — 2026-11-03, against commit `d59a6d7`

**Scope of this round**: `git diff 6e987b0 d59a6d7 --stat` — exactly
three files: `planning/phase-85-self-curation-knowledge-quality-
validation.md` (+39, the fourth corrective note), `planning/retros/
_drift-audit-phase-85.md` (new, 121 lines), and this file itself (the
lead committing my own prior report into git, no content change). No
`src/`, `tests/`, `scripts/`, or `planning/knowledge/**` file changed —
confirmed directly, not assumed. Per the lead's own suggestion and my
own judgement, the heavy verification already completed last round
(full suite, all four strict validators, both dogfood probes
re-executed by hand, agent-brief/scope/protected-file diffs) was **not**
re-run in full, since nothing in this round's diff could plausibly have
touched any of it — confirmed by the diff stat above, not merely taken
on trust. What follows is a direct, fresh check of the two new/changed
artifacts themselves.

## Fix 1 — `planning/retros/_drift-audit-phase-85.md`

Read in full. Compared directly against:

- **This project's own `_drift-audit-phase-N.md` convention**
  (cross-checked against `_drift-audit-phase-84.md`): same structure —
  a `**Scope:**` line, a `**Method:**` paragraph, a `## Verdict:` header
  naming finding count/severity, numbered findings each with file:line,
  a quoted claim, the real source contradicting it, and fix status, a
  "Checked, no drift found" section for the broader sweep, and (new
  here, appropriately) a "Note on this record's own provenance" section
  disclosing the reconstruction. Matches the convention's shape and
  depth — not a stub.
- **My own prior audit's independent findings**: I had already
  independently read the real `git diff 3d9eef5 6e987b0 --
  docs/development/contributing.md docs/development/testing.md` diff
  last round (quoted in my own handback). The reconstructed report's
  Finding 1 (`contributing.md`'s maintainer-tooling catalog omitted the
  new script) and Finding 2 (`testing.md`'s test-module enumeration
  omitted the new test file, now "e.g."-qualified) **match that diff
  exactly** — same files, same lines, same fix description, same
  "already fixed in `55f7008`" status. No invented or embellished
  finding, nothing contradicted by what I already independently
  verified.
- **Scope honesty**: the report explicitly names what it did *not*
  re-derive (the six new knowledge records' own correctness — correctly
  out of a narrative-drift audit's remit) and flags a pre-existing,
  not-this-phase's-fault gap (`tests/test_assess_change_impact.py`
  missing from the same enumeration, Phase 83) rather than silently
  absorbing it — consistent with how `_drift-audit-phase-84.md` also
  separates "this phase's drift" from "other things noticed along the
  way."
- **Provenance disclosure**: explicitly states this record was
  reconstructed same-day from the original dispatch's own full report
  rather than fabricated after the fact or re-run fresh, and names
  *why* (the original pass's method/findings were still fully
  available, not summarized or lossy) — matches exactly what the lead's
  message to me described, and is the honest, transparent framing this
  situation calls for, not a pretense that the file always existed.

**This is a faithful, complete, convention-matching reconstruction.**
It closes the gap my prior pass found: a real, persisted,
independently-checkable artifact now exists recording the
`docs-reconstructor` pass's full scope and `NO DRIFT` (post-fix)
verdict.

## Fix 2 — Fourth corrective note on the Phase 85 plan

Read the new section in full (`git diff 6e987b0 d59a6d7 --
planning/phase-85-...md`, the +39 lines). Matches the shape of the
plan's existing three corrective notes (dated header, what was
discovered, the as-built fix, the rationale, pointers to the real
evidence). Content cross-checked against what I independently confirmed
last round: the four cited Evidence ids (`EV-ADPT-006`, `EV-CTXT-011`,
`EV-SKEP-005`, `EV-DOCORIGIN-008`) match exactly the four ids already
named in `check_test_ref_files()`'s own module-level docstring comment
in `scripts/check_self_knowledge_quality.py` (unchanged this round,
confirmed by its absence from the diff stat above) — no new or
inconsistent claim introduced. The note correctly and explicitly scopes
itself to the one genuine deviation ("every other design element in
§4.C was implemented exactly as specified"), which matches my own prior
finding precisely. This is a non-blocking item that is now also closed.

## Nothing else re-litigated

No code, test, script, or knowledge-record file is part of this round's
diff, so §§1-9 and the "Additional observation" section of my prior
pass stand unchanged and are not re-verified here — they were already
independently reproduced against the real repository state in the first
pass, and nothing since could have altered that state.

## Final verdict: PASS WITH NON-BLOCKING OBSERVATIONS

Both of this audit's prior findings are now genuinely, faithfully, and
transparently closed:

1. The missing drift-audit artifact (previously blocking) now exists,
   faithfully reconstructed and convention-matching — confirmed by
   direct comparison against my own already-independently-verified
   findings, not merely re-read on trust.
2. The plan-vs-as-built sync gap for §4.C point 4 (previously
   non-blocking) is now folded back into the plan document, matching
   its own established practice.

**Non-blocking observation carried forward**: the drift-audit artifact
is a same-day *reconstruction* of a pass that ran before the artifact
existed, not a contemporaneous write — transparently disclosed as such
in the artifact's own text, and not, on the evidence available, a
reason to doubt its accuracy (every claim in it was independently
cross-checked against what I had already verified myself from the real
diff, not merely trusted from the reconstruction's own prose). Noted
for the record, not a blocker.

This phase is, as of commit `d59a6d7`, ready for the terminal
`roadmap-context-curator` reconciliation commit (`planning/ROADMAP.md`
→ `done`, `planning/CONTEXT.md` current-state overwrite, the plan file's
own Status line) per `CLAUDE.md` §5's narrow exemption — provided that
commit touches only those three named targets and nothing else, exactly
as every prior phase in this project's history has required.

---

## Re-audit (2026-11-03, corrective pass — contradiction severity + unreadable-OracleResult handling, commit `95309f1`)

**Scope audited:** commit `95309f1` on `main` ("fix(phase-85):
superseded-contradiction severity + unreadable-OracleResult handling"),
diffed against its parent `95309f1~1`. **However, the actual working
tree at audit time is not clean relative to `95309f1`** — see Finding 2
below, which is itself part of this verdict, not a side note.

### What I independently verified myself (commands run, output seen)

1. **Diff scope.** `git diff 95309f1~1 95309f1 -- src/codecompass/
   knowledge_api.py src/codecompass/oracle.py src/codecompass/
   knowledge_intermediate.py` — empty. `git diff 95309f1~1 95309f1 --
   planning/knowledge/first-party-source-symbols/` — empty. `git diff
   95309f1~1 95309f1 -- planning/ROADMAP.md planning/CONTEXT.md` —
   empty. All three protected-scope claims confirmed exactly as the
   dispatch prompt described. Full `git show 95309f1` reviewed; touches
   exactly `CHANGELOG.md`, `planning/learnings/inbox.md`, the plan file,
   the investigation log, the validator script, and its test file — no
   scope creep.

2. **Read the full script diff** (`scripts/check_self_knowledge_
   quality.py`). Confirmed: `_resolved_by_credible_supersession()` only
   downgrades severity when subject `status == "superseded"` AND is
   named in another same-kind record's own `supersedes` field AND that
   successor's own `status` is itself credible
   (`_CREDIBLE_SUCCESSOR_STATUSES`, excluding `contradicted` for a
   Claim). An orphaned `superseded` record or one named by a non-credible
   successor stays blocking. `check_test_ref_files` now catches `OSError`
   as its own distinct `except` clause (never a bare `except
   Exception`) alongside the pre-existing `oracle.OracleSchemaError`
   clause — confirmed by reading both clauses directly, not merely the
   docstring's claim about them.

3. **Reproduced both defects against the pre-fix source myself**,
   rather than taking the commit message's word for it. Extracted `git
   show 95309f1~1:scripts/check_self_knowledge_quality.py`, confirmed by
   direct `grep` that it has only one `except Exception` (an unrelated
   top-level guard, line 122) and only `except oracle.OracleSchemaError`
   (line 244) — no `OSError` handling. Then **swapped the live file for
   the pre-fix version and ran the 8 new regression tests against it**:
   all 4 defect-specific tests
   (`test_unreadable_result_file_is_blocking`,
   `test_unreadable_result_file_does_not_crash_the_whole_run`,
   `test_superseded_claim_with_genuine_successor_is_informational`,
   `test_real_cl_adpt_008_contradiction_is_now_informational`) **failed**
   against the pre-fix source, while the 4 fail-closed edge-case tests
   (active-contradicted, orphaned-superseded, unresolved-successor,
   non-superseded) **passed even pre-fix** (i.e., they test behaviour
   the old code already got right) — this is exactly the right shape for
   genuine regression tests (L-108) and confirms neither defect fix is
   vacuous. Restored the post-fix file afterward (`git diff` on the file
   came back empty, confirming a clean restore) and re-ran the full
   28-test file: all pass.

4. **Ran the full project test suite**: `.venv/bin/python -m pytest -q`
   → `1166 passed, 2 skipped in 326.65s` — matches the dispatch prompt's
   claim exactly.

5. **Ran the real strict-corpus baseline twice**:
   `.venv/bin/python scripts/check_self_knowledge_quality.py --strict
   --ledgerkit-root ~/projects/ledgerkit`, both runs exit 1, byte-
   identical output (`diff` on the two captured outputs is empty), 35
   findings total. Counted informational vs. blocking by hand from the
   real output: 9 informational (1 contradiction + 5 missing-contract +
   1 missing-evidence(Claim) + 1 needs-review + 1 possible-overlap), 26
   blocking — matches the claimed 35/26 exactly. Confirmed the 26
   blocking findings split exactly as claimed: 9 `missing-evidence`
   (`REQ-DOCORIGIN-001/002/003`, `REQ-HSAPI-001`-`006`) + 2
   `stale-test-citation` + 15 `unverified-required-scope` = 26.

6. **Independently re-derived the "no existing exemption covers the
   nine Requirements" claim** by reading `src/codecompass/
   knowledge_api.py`'s `trace_evidence()` docstring (confirms the
   zero-citation-Requirement → `missing_evidence` rule is pre-existing,
   unrelated design) and `decisions/0081` §3 directly — its "twelve
   pre-existing `status: verified` records" compatibility policy is
   textually scoped to `check_verified_status_cites_passing_oracle_
   result` only ("applies **only** to a record whose owning slug... has
   a `planning/contracts/<slug>/` directory"), never to this script's
   separate `missing_evidence`/citation-existence question. Confirmed
   the real `REQ-DOCORIGIN-001.yaml`/`REQ-HSAPI-001.yaml` have no
   `depends_on` field. Claim holds.

7. **Ran the three sibling scripts**: `check_user_docs.py --strict` (exit
   0, "no findings"), `check_contracts.py --strict --ledgerkit-root
   ~/projects/ledgerkit` (exit 0, informational-only findings), 
   `check_knowledge_base.py --strict` (exit 0, informational-only
   findings) — all unaffected, as claimed.

8. **Independently reproduced the investigation-log addendum's own two
   fixtures** (`sci-001-repro.rs`, `sci-002-repro.ts`) byte-for-byte from
   the addendum's own text, ran them against the live, unmodified
   `src/codecompass/source_symbols.py` myself, and got output
   byte-identical to what the addendum records for both SCI-001 and
   SCI-002. Confirmed via `diff` that the original `SCI-001`/`SCI-002`
   entries (first 150 lines of the log) are byte-identical before and
   after this commit (append-only honoured). Confirmed `git log -1
   --format=%H -- src/codecompass/source_symbols.py` →
   `03f8519...` (Phase 77), matching the addendum's own claim that the
   file is unchanged since well before the original dogfood.

9. **Read the `CHANGELOG.md` `[Unreleased]`/`### Fixed` entry** against
   the real diff — accurate; no overstatement found.

10. **Read the plan file's new "Corrective note (2026-11-03...)"
    section** against everything verified above — accurate on every
    technical claim (both defects, the fix mechanism, the 35/26 baseline,
    the two blocking-finding categories, the honest "`--strict` is not
    currently suitable as an unconditional CI gate" conclusion) **except
    one**: see Finding 1.

11. **Confirmed `L-114` exists in `planning/learnings/inbox.md`** as
    filed by the corrective pass — but see Finding 2: its live `status`
    is no longer `candidate` as the dispatch prompt describes.

### Finding 1 (blocking) — the plan file's own corrective note overstates what exists: no retro addendum exists for this corrective pass

The plan file's new section ends: *"Full detail: this corrective pass's
own retro addendum and audit addendum (same filenames as the original
phase, dated sections)."* This is **false** for the retro addendum. I
read `planning/retros/phase-85-self-curation-knowledge-quality-
validation.md` in full (both at `95309f1` and in the current working
tree — identical, untouched by this commit or by the uncommitted changes
described in Finding 2): it ends at "## Time / cost note" from the
*original* phase closeout, with no corrective-pass section at all — no
"## Corrective pass (2026-11-03...)" heading, no where-we-are/what-
worked/what-didn't-work addendum of any kind. `git diff 95309f1~1
95309f1 -- planning/retros/` touches only the investigation log, not
this file.

This is not a pedantic nitpick: this project has a clear, consistent,
already-established precedent for exactly this situation.
`planning/retros/phase-84-consolidated-knowledge-api.md` has a full
`## Corrective pass (2026-10-29, decisions/0092)` section (where we are /
what was achieved / what worked / what didn't work / candidate learnings
filed) and a further `## Final corrective amendment (2026-11-02,
decisions/0093)` section, each added in the same work that landed the
corresponding fix. `planning/retros/phase-81-intermediate-knowledge-
layer.md`'s own ROADMAP-row narrative likewise reflects each of its
three reopenings. Phase 85's corrective pass has no analogous addendum
anywhere in the repository, committed or uncommitted, despite its own
plan file asserting one exists. The audit addendum half of that sentence
is true only because *this very report* is what completes it — the
retro addendum has no equivalent author.

**Required fix:** add a `## Corrective pass (2026-11-03...)` section to
`planning/retros/phase-85-self-curation-knowledge-quality-validation.md`
(where we are / what was achieved / what worked / what didn't /
candidate learnings filed, mirroring the Phase 84 precedent), or correct
the plan file's own sentence to stop claiming one exists. Either is
acceptable; leaving the false claim in place is not.

### Finding 2 (blocking) — real, dated, substantive closeout work (a docs-reconstructor drift audit and a knowledge-curator triage of `L-114`) exists only as uncommitted working-tree changes, directly contradicting this dispatch's own framing

`git status` at audit time:

```
On branch main
Your branch is ahead of 'origin/main' by 1 commit.
Changes not staged for commit:
	modified:   docs/development/contributing.md
	modified:   docs/workflows/self-curation-loop.md
	modified:   planning/learnings/inbox.md
	modified:   planning/retros/_drift-audit-phase-85.md
```

None of this is part of commit `95309f1` — it sits uncommitted on top of
it. Reading the diffs: `planning/retros/_drift-audit-phase-85.md` gained
a full, dated "## Re-audit (2026-11-03, corrective pass — commit
`95309f1`)" section, independently scoped to this commit's own diff,
verdict **DRIFT — 2 findings, both non-blocking (stale-by-omission,
fixed same day)** — both findings were that `docs/development/
contributing.md` and `docs/workflows/self-curation-loop.md`'s own
descriptions of `check_self_knowledge_quality.py` hadn't yet been
updated to mention the new "unreadable" `test_ref` failure mode or the
new `contradiction`/supersession severity carve-out; both doc files'
uncommitted diffs are exactly those additive, accurate fixes — I read
both edits against the real code and confirm they are correct and not
overstated. Separately, `planning/learnings/inbox.md`'s uncommitted diff
shows a full `knowledge-curator` curation note on `L-114` dated
2026-11-03: **`L-114`'s own `status` field has already been changed from
`candidate` to `retained`**, with a reasoned, independently-structured
disposition splitting its two categories and cross-referencing `L-107`
(also updated with its own curation note).

This directly contradicts two specific claims in this dispatch's own
"What changed, and why" section: (a) that "Commit `95309f1` ... contains
the entire corrective pass" — it does not; real, dated, substantive
closeout work exists outside it, uncommitted; and (b) that `L-114`
triage "is a separate dispatch, not yet done — do not treat its absence
from `promoted.md` as a defect; it is expected to still be a candidate
at this point in the sequence" — the triage has, in fact, already run,
and `L-114` is no longer `status: candidate` in the live repository
state; it is `retained`. I flag this per my own instructions ("flag
explicitly anything in this prompt's own description that your own
independent verification contradicts") rather than silently auditing
against the prompt's stale description instead of the real tree.

On the substance, both pieces of uncommitted work are themselves
well-reasoned and accurate on independent reading — this is not a
quality problem with the work itself. The problem is procedural: per
`CLAUDE.md` §6 ("commit at logical intervals... a completed
sub-deliverable... is its own commit") and §5's own framing of "the
exact commit about to be marked done," there currently is no commit that
actually contains this corrective pass's own drift-audit-fix and
learning-triage sub-deliverables. Until they are committed, "done" has
no stable commit to attach to, and a future reader of `git log` alone
(without inspecting the dirty working tree) would wrongly conclude the
drift audit found nothing to fix and `L-114` was still an untriaged
candidate.

**Required fix:** commit the four currently-uncommitted files as their
own logical commit(s) (e.g. one commit for the docs-reconstructor fix +
its audit-addendum record, one for the knowledge-curator triage —
matching this project's own "one logical change per commit" convention)
before this corrective pass is treated as closed.

### Checked and confirmed correct (no finding)

- `planning/ROADMAP.md` / `planning/CONTEXT.md` genuinely untouched by
  `95309f1` itself — correct, matches the narrow in-commit scope. Note
  for the record: Phase 85's `ROADMAP.md` row (line 188) still reads
  exactly as it did at the original closeout (`311b5dd`) and does not
  yet narrate this corrective pass at all — unlike Phase 81's and Phase
  84's own rows, which *do* carry full corrective-pass narration inline.
  Per `CLAUDE.md` §5's own narrow exemption, that narration is the
  terminal `roadmap-context-curator` reconciliation commit's own job,
  not this corrective-fix commit's — so this is **not** a finding on its
  own, but it is a real, outstanding step still to come (and it should
  also fold in the `L-114`/`L-107` "Known standing gaps" draft text the
  knowledge-curator's own uncommitted curation note in `inbox.md`
  already proposes for `CONTEXT.md`).
- Branch is 1 commit ahead of `origin/main`, unpushed — correct per
  `CLAUDE.md` §6 (push is gated on a passing DoD audit, which this
  report does not yet grant).
- No protected-file drift: `CLAUDE.md` itself untouched; no edit to any
  past ADR's original content (`decisions/0081` only read, never
  written, by this corrective pass).
- Changed-file list for `95309f1` matches the plan's own described
  scope exactly — no scope creep.

### Final verdict: FAIL

Everything that is actually commit `95309f1`'s own content — both
defect fixes, all 8 new regression tests (confirmed to fail pre-fix and
pass post-fix, independently reproduced, not merely trusted), the
determinism and exact 35/26 strict-baseline reconciliation, the two
genuinely pre-existing (not validator-defect) blocking-finding
categories, the sibling-script non-interference, the protected-file and
dogfood-evidence non-interference, the investigation-log reproducibility
addendum (independently re-run byte-for-byte), and the `CHANGELOG.md`
entry — is correct, accurate, and exactly as described. If the audit
were scoped to that commit's code and tests alone, it would be a clean
**PASS**.

The verdict is **FAIL**, not on that work, but on two concrete, narrow,
fixable closeout-completeness gaps found during independent
verification: (1) the plan file's own corrective note asserts a retro
addendum exists that does not; (2) real, dated closeout work (a drift-
audit fix and a learnings triage) that the dispatch prompt itself
described as not-yet-done has, in fact, already run, but sits uncommitted
rather than landed — meaning there is currently no single commit that
represents this corrective pass as actually finished and closed out.

**What must be fixed before re-audit:**

1. Add a `## Corrective pass (2026-11-03...)` addendum to
   `planning/retros/phase-85-self-curation-knowledge-quality-
   validation.md` (mirroring the Phase 84/81 precedent: where we are /
   what was achieved / what worked / what didn't work / candidate
   learnings filed) — or correct the plan file's own sentence that
   currently asserts this addendum already exists.
2. Commit the four currently-uncommitted files (`docs/development/
   contributing.md`, `docs/workflows/self-curation-loop.md`,
   `planning/learnings/inbox.md`, `planning/retros/_drift-audit-
   phase-85.md`) as their own logical commit(s), per `CLAUDE.md` §6.
3. Once 1 and 2 land, a fresh `release-phase-auditor` pass is required
   (this one is voided the moment any further commit touches audited
   scope, per `CLAUDE.md` §5) before any terminal `roadmap-context-
   curator` reconciliation commit narrates this corrective pass in
   `planning/ROADMAP.md`/`planning/CONTEXT.md`.

No finding here concerns the production code, the regression tests, or
the strict-baseline reconciliation itself — all independently
re-verified correct. Re-audit should be quick once 1-2 above land.
