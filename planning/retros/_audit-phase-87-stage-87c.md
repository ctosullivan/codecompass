# Independent completion audit — Phase 87, Stage 87C

- **Auditor:** `release-phase-auditor` (independent dispatch)
- **Date:** 2026-11-10
- **Commit range audited:** `eb14a76..1d9d626` (HEAD at audit time:
  `1d9d62663d4f77a3f80d9fb7e5deb33e2d91e780`)
- **Scope:** Stage 87C only. Phase 87 overall and any later
  stage/phase are explicitly out of scope.

## Summary verdict

**FAIL.**

The real implementation work is sound — directly re-verified below —
but three DoD conditions (`CLAUDE.md` §5) are not met: the changelog
entry, the retro's completeness, and the learnings-triage step. None of
these are "not yet done because they wait for the terminal
`roadmap-context-curator` commit" (that exemption covers only
`ROADMAP.md`'s done-flip, `CONTEXT.md`'s current-state overwrite, and
the plan's own Status line — confirmed correctly *not* done yet, see
below). The changelog entry and the retro are supposed to land in the
same commits as the work itself, per `CLAUDE.md` §§2-3, and the
established precedent from Stage 87B's own audit
(`planning/retros/_audit-phase-87-stage-87b.md`, items 11-12) confirms
a changelog entry existed at that audit's time even though
`CONTEXT.md`/`ROADMAP.md` correctly did not yet reflect closure. Stage
87C has neither.

## What was independently re-verified (and found correct)

1. **`docs/concepts/context.md` decline is real and clean.**
   `git diff eb14a76..HEAD -- docs/concepts/context.md` is empty —
   byte-identical to its pre-stage content. No `context.md.schema.yaml`
   exists on disk. No entry for it exists in
   `planning/knowledge/.grounding-state.toml`. One harmless leftover
   artifact remains: `planning/retros/phase-87-pending-review/
   context-md/five-senses-of-context.json` (a pending-review manifest
   from the declined attempt) — not referenced by any live schema or
   `docs maintain` path, so it cannot cause drift; worth a cleanup pass
   but not a defect.

2. **The three successful migrations are real, correctly scoped, and
   read well.** Directly read `docs/concepts/adapter.md`,
   `vendor-and-ecosystem.md`, and `knowledge-model.md` in full: dense,
   accurate, genuinely useful compiled prose, consistent with the
   retro's account of what each region covers and what was deliberately
   excluded (the dispatch table extracted to a plain table outside the
   compiled region in `adapter.md`; the depth-toggle/`vendor.toml`
   file-format material kept human-authored in
   `vendor-and-ecosystem.md`; the record-kind table kept human-authored
   in `knowledge-model.md`). `check_doc_schema.py --strict` and
   `check_user_docs.py --strict` both ran clean against the real
   working tree.

3. **All five published, compiler-owned regions have real, matching
   dual review verdicts.** Read every
   `planning/retros/phase-87-published-evidence/**/*.json` file
   directly: `adapter-md/adapter-concept`,
   `adapter-md/adapter-term-ambiguity`,
   `knowledge-model-md/invariant-not-a-record-kind`,
   `knowledge-model-md/provenance-cross-cutting`,
   `vendor-and-ecosystem-md/ecosystem-vendor-adapter` each show
   `semantic_review.verdict: supported` and
   `editorial_review.verdict: pass`. The two regions republished after
   the `CL-ADPT-005` amendment (`adapter-concept`,
   `ecosystem-vendor-adapter`) carry a later `published_at` timestamp
   than the other three, consistent with the retro's account of a
   same-day recompile/review/republish cycle.

4. **The real multi-region maintenance demonstration reproduces
   exactly as claimed.** Ran `codecompass docs maintain` for real
   against the current HEAD:
   ```
   noop: readme-md-vendor-digest-concept, adapter-md-adapter-concept,
         adapter-md-adapter-term-ambiguity,
         knowledge-model-md-provenance-cross-cutting,
         vendor-and-ecosystem-md-ecosystem-vendor-adapter
   doc_candidates: intermediate-knowledge-layer,
         knowledge-model-md-invariant-not-a-record-kind
   claims_changed: []
   established_new: []
   ```
   This is an exact match to the task's own claim and the retro's
   account of the final, post-republication state. The
   `EV-ADPT-013.yaml` evidence record cites a real, resolvable
   repository revision (`f59331911db6f38eb5b33d266883cf227093c26c`,
   confirmed via `git rev-parse --verify` to be the real commit
   `f593319`, "compile and publish knowledge-model.md's two
   sections") — an honest, accurate pin, not a placeholder. The
   `CL-ADPT-005.yaml` diff is exactly the amendment the retro
   describes (one added boundary-case sentence, `supporting_evidence`
   extended with `EV-ADPT-013`, revision/timestamp updated). The
   reconciliation manifest
   (`planning/knowledge/codecompass-domain/reconciliation/
   20261109T180405Z-doc.toml`) correctly records the seeded
   `knowledge-model-md-invariant-not-a-record-kind` edit as a
   `doc_region_edit` candidate in `state = "pending"`,
   `decision = "undecided"` — matching the live `doc_candidate` state
   observed above.

5. **The comparator's own numbers are internally consistent, not
   inflated.** Arm B's four review-dispatch durations (26,585 +
   33,828 + 28,971 + 29,934 ms) sum to exactly 119,318 ms as stated;
   the four token counts (49,206 + 48,668 + 48,397 + 47,483) sum to
   exactly 193,754 as stated; 119,318 / 110,527 ≈ 1.08×, matching the
   retro's own "about 1.08×" framing. The retro's "CodeCompass
   advantage demonstrated: NOT DEMONSTRATED" verdict is the honest
   conclusion that these numbers actually support — the quality
   condition is met, the time condition is not, and the retro says so
   plainly rather than rounding to a favourable overall claim. This
   satisfies the task's own instruction to check the discarded-
   comparator-worktree's reported numbers for "internal consistency and
   plausibility" and "confirm the retro honestly reports a
   non-demonstrated advantage rather than inflating the result."

6. **`docs-reconstructor` fix (commit `1d9d626`) is accurate.** Read
   the current state of `docs/architecture/
   documentation-compilation-pipeline.md`, `docs/reference/cli.md`,
   `docs/architecture/components.md`, and `docs/open-questions.md`
   directly: all now correctly describe Stage 87C as implemented (not
   "planned, not authorised"), correctly describe the three migrated
   pages and the declined one, correctly describe the comparator's
   honest non-advantage result, and `open-questions.md`'s Invariant
   count is now consistently "at least two" (not three), matching the
   real, narrowed, migrated content of `knowledge-model.md`.

7. **Full regression suite and strict validators, re-run directly
   against HEAD, not trusted from the task's own claim:**
   `python -m pytest -q` → **1363 passed, 2 skipped** (run twice,
   identical). `ruff check .` → **176 findings** — independently
   confirmed to be the pre-existing baseline by running the identical
   command against a disposable `git worktree` pinned at `eb14a76`
   (pre-stage): also exactly 176 findings, same message, same location
   of the tail output. `check_doc_schema.py --strict` → no findings.
   `check_user_docs.py --strict` → no findings. `check_knowledge_base.py
   --strict` → 24 info-level-only findings (`knowledge-base-snapshot-
   current-divergence`, expected/healthy per the tool's own message).
   `check_knowledge_placement.py --strict` → 10 info-level-only findings
   (`decision-citation-superseded`, explicitly non-defect per the
   tool's own message). No `tests/` or `src/` files were touched by
   this stage's diff at all — consistent with the plan's own claim that
   Stage 87C adds zero new modules/pipeline code, and consistent with
   the regression-suite count being unchanged from the pre-stage
   baseline.

8. **No protected-file drift.** `git diff eb14a76..HEAD -- CLAUDE.md`
   is empty. No file under `decisions/` was touched (confirmed via
   `git diff --name-only`) — reasonable, since this stage introduced no
   new non-obvious architectural tradeoff beyond what the already-
   reviewed plan (§S.4a migration procedure, §S.6 proof design, §S.7
   comparator/threshold design) already recorded; I did not find a
   tradeoff this stage made that was owed a new ADR and didn't get one.

9. **Changed-file list matches the plan's own scope.** The full
   `git diff --name-only eb14a76..1d9d626` list (37 files) is exactly:
   the three migrated Concepts pages + their three new schema files,
   two architecture docs + one reference doc + one open-questions page
   (the docs-reconstructor fix), the knowledge files
   (`CL-ADPT-005.yaml`, `EV-ADPT-013.yaml`, `.grounding-state.toml`,
   one reconciliation manifest, one intermediate projection refresh),
   the pending-review/published-evidence JSON trail, and the retro
   itself. No scope creep into files the plan didn't name; no `src/`
   changes at all, consistent with "zero new modules."

## Blocking findings (must be fixed before re-audit)

1. **No `CHANGELOG.md` entry for Stage 87C exists anywhere.**
   `git log --oneline eb14a76..1d9d626 -- CHANGELOG.md` returns nothing
   — the file was never touched in this commit range. `CLAUDE.md` §3
   requires "Every phase adds an entry under `[Unreleased]` ... in the
   same commit as the change," and the established precedent for this
   exact stage-closure pattern (`_audit-phase-87-stage-87b.md`, items
   11-12) shows a changelog entry **did** exist at that audit's time
   even though `CONTEXT.md`/`ROADMAP.md` correctly did not yet reflect
   closure — i.e. the changelog entry is not part of the terminal
   `roadmap-context-curator` exemption and should already exist now.
   It does not. This is a straightforward gap, not an ambiguous one.

2. **The retro is substantially incomplete against
   `planning/retros/TEMPLATE.md`.** It has only four of the template's
   eleven sections (`Where we are`, `Goal`, `What was achieved` with
   subsections). It is missing: `Scope delivered vs planned`,
   `What worked`, `What didn't work`, `Lessons learnt`,
   `Process-improvement feedback`, `Candidate learnings filed`,
   `Where we're going`, and `Time / cost note`. This stage is
   demonstrably not trivial (real defects found and fixed during
   migration, a full comparator experiment, a usability exercise
   surfacing a genuine out-of-scope bug) — the release-phase-auditor's
   own governing brief is explicit that only a genuinely trivial phase
   may use a stub-length retro, and this one isn't that. The retro's
   own closing sentence ("Recorded as unresolved findings for the
   learning-lifecycle triage below") promises a "below" section that
   does not exist anywhere in the file — a dangling, unfulfilled
   reference, not merely a formatting gap.

3. **No candidate learnings were filed for this stage, and nothing was
   triaged.** `git diff --name-only eb14a76..1d9d626` touches no file
   under `planning/learnings/`; `planning/learnings/inbox.md`'s last
   touching commit (`e25cf35`) predates this stage's own commit range
   entirely; `planning/learnings/candidates/` contains only `.gitkeep`.
   Yet the retro's own "What was achieved" prose surfaces several real,
   generalizable findings that look exactly like candidate-learning
   material and were never filed: (a) the citation-scope checker not
   catching a required-Claim coverage gap until a human caught it
   (fixed by splitting a schema section); (b) markdown-table flattening
   when an LLM composes a grounded region around tabular content; (c)
   a forward-looking Claim's own framing being silently flattened to a
   present-tense fabricated claim about this specific repository,
   requiring two correction rounds before a reviewer caught it fully;
   (d) the blind comparative reviewer's own real methodological
   limitation around `citation_display: none` stripping visible
   citations from the rendered diff; (e) the real, reproducible
   `codecompass undo` first-run gap the usability exercise found. None
   of these reached `planning/learnings/inbox.md`, so
   `knowledge-curator` triage could not and did not happen. `CLAUDE.md`
   §5 requires this triage as a DoD condition, "including any surfaced
   by the retro" — it is not merely pending, it has no candidate
   material to act on at all.

## Correctly NOT yet done (not a finding — matches established practice)

- `planning/CONTEXT.md`'s current-state section still describes Stage
  87C as "implementation itself remains separately, explicitly
  unauthorised" — stale relative to the real state, but this is
  exactly the `roadmap-context-curator`'s terminal-commit job per
  `CLAUDE.md` §5's named exemption, to run only after this audit
  passes.
- `planning/ROADMAP.md`'s Phase 87 row still says "planned" and still
  describes Stage 87C as unauthorised — same reasoning; also correctly
  does **not** mark Phase 87 overall `done`, which the task explicitly
  forbids regardless.
- The phase plan file's own Status line is likewise unchanged — same
  terminal-commit reasoning.

## What must be fixed before re-audit

1. Add a `CHANGELOG.md` entry under `[Unreleased]`, categorized,
   describing Stage 87C's own real deliverables (the three successful
   Concepts-page migrations, the declined `context.md` migration, the
   real `CL-ADPT-005` multi-region maintenance demonstration, the
   matched-baseline comparator and its honest non-advantage result,
   the usability exercise and its one genuine out-of-scope finding,
   the `docs-reconstructor` fix commit) — in its own commit, separate
   from unrelated work, per this project's own established convention.
2. Complete the retro at
   `planning/retros/phase-87-stage-87c-knowledge-compiled-documentation.md`
   with all `TEMPLATE.md` sections filled substantively: `Scope
   delivered vs planned` (name the narrowing from the plan's original
   ambition — e.g. `knowledge-model.md` down to two sections, not the
   full nine-Claim cluster — and the declined `context.md` migration,
   explicitly as planned-vs-actual deltas); `What worked`; `What
   didn't work` (e.g. the blind recompile that lost hard-won specific
   identifiers, the two correction rounds needed for the fabricated-
   file-exists sentence); `Lessons learnt`; `Process-improvement
   feedback`; `Candidate learnings filed` (file the five items named
   above, or a reasoned subset, to `planning/learnings/inbox.md` first,
   then list their `L-NNN` ids here — "none" is not an honest answer
   given the real findings this stage surfaced); `Where we're going`;
   `Time / cost note`.
3. Dispatch `knowledge-curator` to triage whatever candidate learnings
   result from (2) once they exist in `planning/learnings/inbox.md`.
4. Optional, non-blocking cleanup noticed during this audit (fix or
   explicitly decline, either is fine): (a) remove the orphaned
   `planning/retros/phase-87-pending-review/context-md/
   five-senses-of-context.json` left over from the declined migration
   attempt; (b) `docs/concepts/knowledge-model.md.schema.yaml`'s own
   `acceptance_criteria` for the `invariant-not-a-record-kind` section
   still says "names at least three distinct things," which now
   disagrees with the actually-published, narrowed content ("at least
   two distinct artifacts") and with the just-fixed
   `docs/open-questions.md` ("at least two") — a schema-internal field,
   not a reader-facing doc, so not itself a DoD-blocking drift, but
   worth correcting for consistency.

Once (1)-(3) land, a fresh `release-phase-auditor` pass is required
before the terminal `roadmap-context-curator` reconciliation commit
(flipping `ROADMAP.md`'s row for Stage 87C, overwriting `CONTEXT.md`'s
current-state section, updating the plan file's Status line) may
proceed — this FAIL, and the commits that fix it, are new audited
scope themselves.
