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
(§3 above; `docs/development/contributing.md`'s new catalog entry
correctly and honestly documents the contract-bearing-only scoping
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
