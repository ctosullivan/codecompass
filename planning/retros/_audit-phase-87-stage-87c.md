# Independent completion audit — Phase 87, Stage 87C (RE-AUDIT)

- **Auditor:** `release-phase-auditor` (independent dispatch, fresh)
- **Date:** 2026-11-10
- **Commit range audited:** `eb14a76..3e425c5` (HEAD at audit time:
  `3e425c527bd7c071373b5958e0e352fe0a16037a`)
- **Scope:** Stage 87C only. Phase 87 overall and any later
  stage/phase are explicitly out of scope.
- **Context:** This is a full, from-scratch re-audit against the
  current commit, superseding this auditor's own prior FAIL pass
  (against `1d9d626`, preserved verbatim in the Appendix below) — per
  `CLAUDE.md` §5, any commit after an audit voids it and requires a
  fresh one against the new state in full, not merely a check of the
  named gaps. The three blocking findings and two non-blocking
  observations from that prior pass are re-verified below as part of a
  complete audit, not assumed closed.

## Summary verdict

**PASS.**

All three previously-blocking DoD gaps are now genuinely closed with
real, substantive content — not stubs, not rubber stamps. Both
non-blocking observations are addressed. Every item from the prior
PASS-equivalent findings (full regression suite, `docs maintain`
five-state outcome, protected-file non-drift, scope-match,
ROADMAP/CONTEXT correctly not yet updated) was independently re-run
against the current HEAD and still holds. No regression found.

## What was independently re-verified

### 1. `CHANGELOG.md` entry (previously missing — now present and accurate)

`CHANGELOG.md`'s `[Unreleased]` → `### Added` section now carries a
dedicated Stage 87C entry (added in commit `3e425c5`), separate from
the existing Stage 87B entries, not batched with them. Read it in full
and checked every claim against the real artifacts:

- "three further `docs/concepts/` pages... `adapter.md` (two compiled
  regions), `vendor-and-ecosystem.md` (one), and `knowledge-model.md`
  (two, deliberately narrowed scope)" — confirmed against the real
  schema files and the retro's own table.
- "`context.md`... attempted and honestly declined... reverted to its
  original content unchanged" — confirmed: `git diff eb14a76..HEAD --
  docs/concepts/context.md` is empty; no `context.md.schema.yaml`
  exists on disk.
- "a new evidence record and a `CL-ADPT-005` Claim amendment correctly
  triggered `claims_changed` in exactly the two regions that cite it...
  a deliberately seeded unrelated human edit and a pre-existing
  unrelated candidate both correctly remained `doc_candidate`" —
  confirmed by re-running `codecompass docs maintain` myself (below).
- "a matched-baseline comparator... no net time/cost advantage was
  demonstrated... reported honestly as a predeclared-threshold miss" —
  confirmed against the retro's own cost-accounting table and verdict
  language; matches.
- "an independent, no-prior-context documentation-usability exercise...
  surfaced one genuine, out-of-scope `codecompass undo` first-run gap,
  filed as a learning rather than fixed" — confirmed: this is `L-129`,
  filed and triaged (see below), not fixed in this stage's diff.

The entry is accurate, not inflated, and correctly scoped to Stage 87C
alone (no Stage 87B content folded in).

### 2. Retro completeness against `TEMPLATE.md` (previously 4 of 11 sections — now all 11)

Read `planning/retros/TEMPLATE.md` and
`planning/retros/phase-87-stage-87c-knowledge-compiled-documentation.md`
side by side. All eleven required headings are present, in order:
`Where we are`, `Goal`, `Scope delivered vs planned`, `What was
achieved`, `What worked`, `What didn't work`, `Lessons learnt`,
`Process-improvement feedback`, `Candidate learnings filed`, `Where
we're going`, `Time / cost note`. Each has real, specific, non-stub
content:

- `Scope delivered vs planned` names the concrete deviations (declined
  `context.md`, five vs. the plan's "six overall" compiled-document
  target, the §S.6 demonstration's fallback region swap) rather than a
  generic "shipped as planned."
- `What worked` / `What didn't work` give specific, falsifiable claims
  (the append-one-sentence vs. full-blind-recompile finding; the
  retro's own first draft being incomplete, named honestly as a
  "didn't work" item about this very retro).
- `Lessons learnt` draws a generalizable takeaway distinct from the
  "what worked/didn't" bullets themselves (the structural-vs-cost
  distinction in incremental-maintenance advantage; the citation-scope
  checker's blind spot; a retro's completeness itself being a DoD
  artifact).
- `Candidate learnings filed` names real ids (`L-125`-`L-129`) with a
  one-line description of each, plus "all filed to `planning/
  learnings/inbox.md`, status `candidate`, pending `knowledge-curator`
  triage" — matching the real inbox state (see below; triage has since
  completed with dispositions, consistent with "pending" being the
  retro's own snapshot at the time it was written within the same
  closeout work).
- `Where we're going` and `Time / cost note` are both substantive, not
  one-liners.

This retro is not trivial-length and the stage is not a trivial phase
(real defects found/fixed during migration, a full comparator
experiment, a usability exercise with a genuine finding) — correctly
not using the stub-length carve-out.

### 3. Candidate learnings filed and triaged (previously none — now `L-125`-`L-129`, each independently re-verified by `knowledge-curator`)

Read `planning/learnings/inbox.md` directly (not trusting the retro's
or commit message's account). All five entries exist with every
required `TEMPLATE.md`-format field (`origin`, `date`,
`project_revision`, `observation`, `evidence`, `classification`,
`status`, `recurrence`) plus a `**curation note**`/`**Disposition:**`
block attributed to `knowledge-curator`, dated `2026-11-10`:

- **`L-125`** (citation-scope checker validates existence, not
  completeness, of `required_knowledge`). Curator note independently
  re-reads `src/codecompass/doc_compiler.py` lines 336-368 and 149-212
  directly, confirms the described blind spot by function-level code
  inspection rather than trusting the filed text, and reaches
  **promote** with a specific destination
  (`docs/architecture/documentation-compilation-pipeline.md` step 6)
  and drafted addition text. Reasonable and well-evidenced.
- **`L-126`** (markdown-table flattening under clean-room composition).
  Curator note is honest about a real limitation of its own
  verification: the original pre-fix flattened draft is no longer on
  disk, so byte-for-byte reproduction wasn't possible from the curator's
  own tools; it discloses this rather than silently certifying, and
  flags a `lead` follow-up to confirm via `git log -p`. A **lead
  follow-up note dated the same day** then supplies direct,
  contemporaneous corroboration (commit `4a661b8`'s own message,
  written at the time the defect was found) and confirms the disposition
  stands. This is a well-handled instance of a triage note disclosing
  its own evidentiary gap rather than overclaiming, with a visible
  resolution — exactly the rigor this process should show, not a rubber
  stamp.
- **`L-127`** (forward-looking Claim framing flattened to a
  fabricated-sounding present-tense claim). Curator note independently
  reads `CL-EVID-007.yaml` directly, confirms its clause (c) names a
  file written against Phase 63D's own forward-looking context, and
  independently confirms via `Glob` that the named file genuinely does
  not exist in the current repository — i.e. re-derives the underlying
  factual claim itself, not just trusting the retro's narrative.
  Promote, with a specific destination and drafted text.
- **`L-128`** (blind review cannot see `citation_display: none`
  citations). Curator note confirms the mechanism directly
  (`doc_compiler.strip_citation_tags` lines 375-393, and which schemas
  set `citation_display: none`), then **actively disagrees with and
  overrides the filed `classification: workflow`**, giving a specific,
  reasoned argument (no standing "comparator protocol" skill/doc exists
  to receive a `workflow` classification; a repo-wide grep found none)
  and reclassifies to `architecture`, with an explicit note on when a
  `workflow` reclassification would become appropriate (second
  recurrence). This is a real, independent, non-rubber-stamp judgment
  call, not an agreement-by-default.
- **`L-129`** (`codecompass undo` first-run `doc_artifacts`-ordering
  gap). Curator note independently reads `src/codecompass/cli.py`
  (`_bootstrap` lines 130-178, `_refresh_generated_artifacts` line 178
  calling `rebuild_project_graph` again at line 262 before
  `write_tool_skill`/`write_discovery_command` at lines 265-266) and
  `skill_scan.py` directly to confirm the described ordering bug by
  code inspection, confirms `docs/reference/cli.md:138`'s exact
  unqualified sentence, and **disagrees with and overrides the filed
  `classification: user-visible`**, reclassifying to `open-work` with a
  specific citation to `learning-lifecycle.md` §4's definitions and a
  precedent (`L-123`'s own prior reclassification by this same role).
  Honestly discloses it did not itself reproduce the live
  `undo --dry-run`/`sync` behavior (no Bash tool in that role),
  recommending the lead re-run it if further confirmation is wanted —
  disclosed limitation, not silently assumed.

All five dispositions are **promote**, each with a drafted, specific
destination and `status` correctly left `candidate` pending the
destination artifact actually landing — the retro's own text confirms
this is "the same convention as `L-122`/`L-124`," which I independently
confirmed by reading those two entries directly: both show `status:
promoted` now, with a `promoted_to` pointer to a `ROADMAP.md` row that
landed in a *later* commit than their own initial triage — i.e. the
"candidate, pending landing" state for `L-125`-`L-129` is the correct,
consistent snapshot at this point in the lifecycle, not a shortcut.
This triage is real: it re-derives underlying facts independently in
three of five cases, discloses an evidentiary limit in a fourth (with a
same-day lead follow-up closing it), and substantively overrides two of
the filer's own classifications with reasoned, cited arguments rather
than accepting them by default. This is a defensible, non-rubber-stamp
triage pass.

### 4. Both non-blocking observations addressed

- **`docs/concepts/knowledge-model.md.schema.yaml`'s `acceptance_criteria`.**
  Diff confirms the second bullet changed from "at least three distinct
  things" to "at least two distinct things." Cross-checked against the
  real published content of `docs/concepts/knowledge-model.md` (the
  Invariant paragraph): "the term is used across the codebase to name
  at least two distinct artifacts" — now consistent on both sides.
- **Orphaned `context-md` pending-review JSON.** Still present on disk
  at `planning/retros/phase-87-pending-review/context-md/
  five-senses-of-context.json` (confirmed via `ls`) — i.e. deliberately
  kept, not deleted. The choice and its rationale are explained in the
  fix commit's own message ("the declined context.md migration's own
  pending-review JSON is kept, not deleted, as legitimate historical
  evidence of the attempt, matching Stage 87A/87B's own established
  precedent"). Independently confirmed the cited precedent is real:
  `planning/retros/phase-87-pending-review/readme-md/
  vendor-digest-concept.json` (Stage 87A's own analogous artifact) is
  likewise still present on disk, matching "Stage 87A/87B's own
  established precedent" rather than an invented justification.

### 5. Everything from the prior pass's PASS-equivalent findings, re-confirmed against current HEAD

- **Full regression suite:** ran `.venv/bin/python -m pytest -q`
  myself against the current working tree → **1363 passed, 2 skipped**
  (432.06s). Exact match, no regression.
- **Strict validators:** `scripts/check_user_docs.py --strict` → no
  findings. `scripts/check_doc_schema.py --strict` → no findings.
  `scripts/check_knowledge_base.py --strict` → info-level-only findings
  (`knowledge-base-snapshot-current-divergence`), same as before,
  explicitly non-defect per the tool's own message.
  `scripts/check_knowledge_placement.py --strict` → info-level-only
  findings (`decision-citation-superseded`), same as before, explicitly
  non-defect.
- **`ruff check .`** → 176 findings — the same pre-existing baseline
  count confirmed in the prior audit pass (the prior pass already
  independently isolated this as pre-existing via a disposable
  worktree at `eb14a76`; no new ruff findings were introduced by the
  fix commit, since it touches no `src/`/`tests/` files at all).
- **`codecompass docs maintain`**, run for real against current HEAD:
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
  Exact match to the prior pass's own re-run. The fix commit (CHANGELOG/
  retro/inbox/schema-comment changes only) could not plausibly have
  changed this, and didn't.
- **No protected-file drift:** `git diff eb14a76..HEAD -- CLAUDE.md` is
  empty (0 lines) — note the diff base is still `eb14a76`, the
  pre-Stage-87C commit, as instructed, not `1d9d626`. `git diff
  --name-only eb14a76..HEAD -- decisions/` is empty — no ADR touched.
- **`planning/ROADMAP.md` / `planning/CONTEXT.md` still correctly *not*
  updated.** Both still describe Stage 87C as "planned" /
  "implementation itself remains separately, explicitly unauthorised" —
  stale relative to the real, now-audited-PASS state, but this is
  exactly the `roadmap-context-curator`'s terminal-commit job per
  `CLAUDE.md` §5's named exemption, correctly deferred until after this
  PASS. Phase 87 overall is not marked done anywhere. The phase plan
  file's own Status line (`planning/phase-87-documentation-schema-
  knowledge-compiled-documentation.md`, line 3) is likewise unchanged.
- **Changed-file list matches the plan's own scope, including the fix
  commit.** `git diff --name-only eb14a76..HEAD` (restricted to the
  categories that could plausibly be touched) shows exactly:
  `CHANGELOG.md`, the three migrated Concepts pages + their three
  schema files, four docs-reconstructor-fixed architecture/reference/
  open-questions pages, `planning/learnings/inbox.md`, the audit report
  itself, the retro, and the full pending-review/published-evidence
  JSON trail (including `context-md`'s, deliberately kept). No `src/`
  or `tests/` file is touched anywhere in the range — consistent with
  "zero new modules/pipeline code." No scope creep.

## Verdict

**PASS.** All three previously-blocking gaps are genuinely closed with
real, independently-verified substance, not stubs or rubber stamps.
Both non-blocking observations are addressed. Nothing regressed. The
terminal `roadmap-context-curator` reconciliation commit (flipping
`ROADMAP.md`'s row, overwriting `CONTEXT.md`'s current-state section,
updating the plan file's Status line — nothing else) may now proceed
for Stage 87C.

---

## Appendix: prior FAIL-returning pass, preserved verbatim

The text below is this auditor's own prior pass against commit
`1d9d626`, preserved unmodified as the historical record of what was
found and what was required to fix it. Superseded by the PASS verdict
above. (This report file itself was first persisted to disk at the time
of that original pass, then committed to git for the first time as
part of the fix commit `3e425c5` alongside the fixes it names — hence
the file has no separate pre-`3e425c5` git history of its own, even
though the audit pass it records predates that commit.)

### Independent completion audit — Phase 87, Stage 87C

- **Auditor:** `release-phase-auditor` (independent dispatch)
- **Date:** 2026-11-10
- **Commit range audited:** `eb14a76..1d9d626` (HEAD at audit time:
  `1d9d62663d4f77a3f80d9fb7e5deb33e2d91e780`)
- **Scope:** Stage 87C only. Phase 87 overall and any later
  stage/phase are explicitly out of scope.

#### Summary verdict

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

#### What was independently re-verified (and found correct)

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

#### Blocking findings (must be fixed before re-audit)

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

#### Correctly NOT yet done (not a finding — matches established practice)

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

#### What must be fixed before re-audit

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
