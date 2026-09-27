# Completion audit — Phase 74 (Priority B provenance hardening, closes `L-031` + `L-032`)

**Auditor:** `release-phase-auditor`, independent pass.
**Audited state:** current `main` HEAD at audit time (`9a14753`),
covering Phase 74's own commits `1dc228f` (plan), `050e366`
(implementation), `40e7718` (documentation closeout), `3d0ed30`
(learnings/ROADMAP landing), plus the shared closeout commit `76c441f`
and the later `901512d` (retro + `knowledge-curator` triage, lands
`L-058`) and `da1b56b` (fix of two remaining `CL-EVID-008` citations in
`provenance.md`, found by a prior `release-phase-auditor` pass).

**Verdict: FAIL.** Two concrete, evidenced gaps below must be fixed
before this phase can cleanly re-pass. Neither concerns the underlying
`src/` behavior change (`L-031`/`L-032` are both real, tested, correctly
wired to their production call sites) — both are documentation-integrity
gaps this audit exists to catch.

This is a fresh, independent re-audit dispatched because no
`_audit-phase-74.md` had ever been persisted (`L-060`); Phase 74's
`ROADMAP.md`/plan-file `done` flip (`76c441f`) happened before any
`release-phase-auditor` pass ran, and that pass's own real verdict (once
obtained) was never itself persisted, and its own follow-up fix
(`da1b56b`) was never re-audited before being pushed. This report closes
that gap for real.

## 1. Plan file re-read and Verification section re-run

Plan: `planning/phase-74-provenance-hardening.md`.

1. New migration test (`symbol_enrichment.model`, pre-migration row
   backfills `NULL`, post-migration write stores real value) — present
   in `tests/test_graph.py`, passes.
2. `test_rebuild_deterministic_never_touches_symbol_enrichment` updated
   with `model=` — passes.
3. `enrichment.py::apply_results`'s own coverage
   (`tests/test_enrichment.py`) — passes, confirms the real call site.
4. Two new `test_adapters_external_process.py` tests (ecosystem
   mismatch, unrecognized capability) — present, pass; all 7 pre-existing
   tests in that file pass with `expected_ecosystem=` added.
5. `tests/test_adapter_haskell.py`'s existing `_analyze` coverage —
   passes, confirms the real call site supplies a valid
   `expected_ecosystem`.
6. `scripts/check_user_docs.py --strict` / `check_knowledge_base.py` —
   re-run now (§2); see Finding 2 below for the one genuine gap found
   (not flagged by either script — they don't check domain-corpus prose
   consistency).
7. Full `pytest`, `ruff check .` — re-run now (§2).
8. `docs-reconstructor` per-phase drift audit — ran
   (`planning/retros/_drift-audit-phase-74.md`), found 4 blocking
   findings (`README.md` x3, `architecture/context-graph-schema.md`) plus
   2 more sub-findings (`docs/developer/writing-an-adapter.md`,
   `docs/protocol-adapter/integrating-a-new-external-adapter.md`), all
   fixed in `40e7718`. **Independently re-verified all six fixes against
   the current code** (§3) — all six confirmed correctly closed.
9. `L-031`/`L-032` flipped with real commit SHAs (not the placeholder) —
   confirmed (§5).
10. Standard closeout — retro, `knowledge-curator` triage,
    `release-phase-auditor` pass present; this report is that pass.

## 2. Commands re-run against the current working tree

- `pytest -q`: `1 failed, 640 passed, 2 skipped`. The one failure
  (`tests/test_check_user_docs.py::test_no_false_positives_against_real_repo`)
  is not itself a new Phase 74 regression — it's the same
  `done_phases_have_audit_report`/`context_not_stale_about_pending_audit`
  gap named in this dispatch's own brief, being closed across two
  parallel audit dispatches (71/72 and this one) plus a lead
  `CONTEXT.md` reconciliation pass. This report's own existence closes
  the "phase 74" half of that check.
- `ruff check .`: `All checks passed!`
- `python scripts/check_user_docs.py --strict`: 5 findings, all
  attributable to phases 71/72 and `CONTEXT.md`'s stale pending-audit
  language — no finding attributable to Phase 74's own `src/` change or
  its `docs/`/`architecture/` fixes. (The `docs/domain/` gap in Finding 1
  below is real but is not something this script checks — it has no
  general prose-consistency check over `docs/domain/`.)
- `python scripts/check_knowledge_base.py`: no findings.

## 3. Independent re-verification of the 6 drift-audit fixes (`40e7718`)

Re-read each fixed location directly against current code, not trusting
the retro's or drift audit's own claim of "fixed":

- `README.md` (symbol_enrichment producer-attribution bullet, evidence &
  provenance section, ecosystem/capabilities limitation bullet) — grepped
  for the old stale phrasing (`no producer/model attribution`, `not
  validated`, `uncomplainingly`) — zero hits. **Confirmed fixed.**
- `architecture/context-graph-schema.md:94-98` — now lists `model`
  (nullable — Phase 74; ...) in `symbol_enrichment`'s column enumeration.
  **Confirmed fixed**, and confirmed accurate against
  `src/codecompass/graph.py`'s actual current schema.
- `docs/developer/writing-an-adapter.md:153-166` — code block now reads
  `process.initialize(expected_ecosystem=self.config.ecosystem)`,
  matching `haskell.py:188`'s real current call site exactly. **Confirmed
  fixed** — copying this code verbatim would no longer raise `TypeError`.
- `docs/protocol-adapter/integrating-a-new-external-adapter.md` (both
  sub-findings: the `.initialize()` call-site instruction, and the
  "ecosystem (free text)" characterization) — now correctly instructs
  `.initialize(expected_ecosystem=...)` and explicitly names the
  `AdapterError` raised on mismatch/unrecognized capability, crediting
  "(Phase 74)". **Confirmed fixed.**

All six confirmed genuinely closed, not merely claimed closed.

## 4. `docs/domain/` staleness re-check — independent, against current HEAD (this audit's own required step, per `L-040`)

This is the specific check this role's own checklist item 9 exists for:
re-running the domain-staleness term check against the **full current
repository state**, not only the mid-phase diff a per-phase drift audit
already covered. The mid-phase `domain-skeptic` dispatch
(`planning/retros/_domain-skeptic-review-phase-74.md`) explicitly scoped
itself to **five** cited locations (`capability.md`, `protocol.md`,
`ecosystem.md`, `provenance.md`, `open-questions.md`) — but the Phase 74
drift audit's own "Domain-claim staleness candidates" section (which fed
that dispatch) had actually named **more** locations for `L-031` alone:
`provenance.md`, `evidence.md` (~108, 114), `observation.md` (~60),
`relationship-edge.md` (~119), `open-questions.md` item 9. Three of those
five — `evidence.md`, `observation.md`, `relationship-edge.md` — were
never included in the `domain-skeptic` dispatch's actual scope and were
never fixed in `40e7718`.

Independently re-read all three against current code:

- `observation.md:56-64` and `relationship-edge.md:110-122` — both cite
  `symbol_enrichment` only as one of three enrichment-table names in a
  list, making no claim about whether it carries a `model` column.
  **Not stale** — unaffected by this phase's fix.
- **`docs/domain/concepts/evidence.md:106-115` — genuinely stale, still
  present at current HEAD:**

  > "Two of the three enrichment tables (`vendor_enrichment`,
  > `doc_relation_enrichment`) carry one `model` provenance column each;
  > **`symbol_enrichment` carries none** — see
  > [`provenance.md`](provenance.md)'s own Definition/Counterexample for
  > the full asymmetry, not restated here (`decisions/0054`,
  > `EV-EVID-008`, `EV-EVID-014`)."

  This is now false: as of this phase, `symbol_enrichment` has a
  `model` column (nullable) and every new write supplies a real value
  (`src/codecompass/graph.py:176-182`, `enrichment.py:427`). This is
  exactly the same underlying fact `provenance.md`'s own now-corrected
  Definition point 2 and Counterexample section state accurately (all
  three tables now carry `model`, with a narrower nullability residual)
  — `evidence.md`'s cross-reference sentence was never updated to match,
  because it fell outside the narrower five-location scope the mid-phase
  `domain-skeptic` dispatch was given, and the per-phase drift audit that
  correctly named it as a candidate explicitly deferred it to
  `domain-skeptic` rather than resolving it itself (correct per that
  audit's own write-boundary, but nobody closed the loop on all of its
  named candidates before closeout).

  **This is precisely the timing/scope gap this checklist item exists to
  catch** (`L-040`'s own precedent: a domain-corpus staleness term that
  survives the mid-phase reconciliation and is only caught by the final,
  independent, full-repository re-check).

No other stale `symbol_enrichment`/`ecosystem`/`capabilities` provenance
claim found anywhere else in `docs/domain/` (grepped for `carries none`,
`no provenance column`, `has no.*model`, `not validated`,
`uncomplainingly`, `free text` across the full `docs/domain/` tree — the
only remaining `free text` hits, in `ecosystem.md`/`protocol.md`,
correctly describe the wire *specification* level, which this phase did
not change, and are accurate).

## 5. Retro accuracy — genuinely incomplete

`planning/retros/phase-74-provenance-hardening.md`'s own "Commit(s)"
line lists only `1dc228f`, `050e366`, `40e7718`, `3d0ed30`. It does not
mention `da1b56b` — the commit that fixed two remaining `CL-EVID-008`
citations in `provenance.md`, found by a prior `release-phase-auditor`
pass, per that commit's own message ("release-phase-auditor's final DoD
pass found two inline citations ... still pointed at `CL-EVID-008`
present-tense after it was superseded"). The retro predates that commit
and was never updated afterward, so it does not "accurately reflect the
full final sequence" as this dispatch's own instructions require. This
must be fixed (append `da1b56b` to the commit list, with a one- or
two-sentence note on what it fixed and why) before this phase can
cleanly re-pass.

## 6. `L-031`/`L-032`/`L-058` tracking accuracy

`planning/learnings/promoted.md`:

- `L-031 | 2026-09-23 | future-improvement | ... @ 050e366` — real SHA,
  correct, matches plan Verification item 9's explicit requirement (not
  the placeholder).
- `L-032 | 2026-09-23 | future-improvement | ... @ 050e366` — same,
  correct.
- `L-058 | 2026-09-27 | scoped-rule | ... @ (this phase's own closeout
  commit)` — uses the placeholder convention, but this matches this
  file's own long-established, consistent pattern for every learning
  promoted within its own closing commit batch (compare `L-036`, `L-035`,
  `L-040`–`L-056`, all identical placeholder form) — the Phase 74 plan's
  explicit "use a real SHA, not the placeholder" instruction was scoped
  to `L-031`/`L-032` specifically (because a real prior SHA already
  existed for them by closeout time), not a general ban on the
  placeholder for every learning. **Not a finding** — consistent with
  established convention.

## 7. Protected-file drift / changed-file scope check

`git show --stat` on `1dc228f`, `050e366`, `40e7718`, `3d0ed30`: no
`CLAUDE.md`, no `decisions/*` touched. Changed files match the plan's
"Files created/changed" section for the `src/`/`tests/` core
(`graph.py`, `enrichment.py`, `external_process.py`, `haskell.py`,
`test_graph.py`, `fake_adapter.py`, `test_adapters_external_process.py`)
exactly. The additional files touched in `40e7718`
(`README.md`, `architecture/context-graph-schema.md`,
`docs/developer/writing-an-adapter.md`,
`docs/protocol-adapter/integrating-a-new-external-adapter.md`,
`docs/domain/concepts/{capability,ecosystem,protocol,provenance}.md`,
`docs/domain/open-questions.md`, and the new
`planning/knowledge/codecompass-domain/*.yaml` Observation/Evidence
records plus `CL-EVID-013`/`DE-EVID-013`) are not individually named in
the plan's own narrow Files list, but are exactly the same-commit
doc-sync updates `CLAUDE.md` §2 requires as a direct consequence of the
phase's own behavior change — not scope creep into unrelated work.
`.claude/agents/docs-maintainer.md` (touched in `901512d`, landing
`L-058`) is the standard learning-lifecycle promotion mechanism, also not
scope creep. **No protected-file drift; no unexplained scope creep.**

## 8. Reference-project / context-evaluator applicability

Not applicable — Phase 74 is not a reference-project or
context-evaluation phase.

## Summary and required fixes

Phase 74's actual `src/` deliverable is real, correctly tested through
both production call sites, and the great majority of its documentation
closeout (11 of 12 affected locations, all 6 `docs-reconstructor`
findings) is genuinely, verifiably fixed. Two concrete gaps remain,
however, and per this role's hard rule a real gap is not softened to a
clean pass:

1. **`docs/domain/concepts/evidence.md:106-115`** still asserts
   `symbol_enrichment` "carries none" (no `model` column) — false as of
   this phase. Fix: replace with text matching `provenance.md`'s own
   now-correct framing (all three tables now carry `model`; note the
   narrower nullability asymmetry), following `domain-skeptic`'s own
   established replacement-text convention used for the other five
   locations. Re-run the domain-corpus staleness grep across all of
   `docs/domain/` afterward to confirm no further sibling instance
   remains (`observation.md`/`relationship-edge.md` already independently
   checked clean in §4 above).
2. **`planning/retros/phase-74-provenance-hardening.md`** must be
   updated to include `da1b56b` in its commit list, with a brief note on
   what it fixed (the two remaining stale `CL-EVID-008` citations found
   by a prior `release-phase-auditor` pass) and why the retro didn't
   originally include it (it landed after the retro was written).

Both are documentation-integrity fixes, not `src/` changes, and neither
calls the underlying `L-031`/`L-032` implementation into question. Once
both are fixed, this phase should be re-audited (a fresh pass, not a
reuse of this report, per `CLAUDE.md` §5's "any commit after the
auditor's own pass ... voids that pass" rule) before `planning/ROADMAP.md`
and the plan file's `done` status stand as fully verified.

**Verdict: FAIL** (two required fixes above; not a soft "PASS WITH
OBSERVATIONS" — both are real, current-truth-doc-affecting defects this
audit exists to catch, not cosmetic).
