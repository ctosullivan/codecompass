# Phase 86 retro — Knowledge-Placement and Code-Quality Review

## Goal

Help a coding agent or human reviewer decide, with evidence rather than
taste, where a piece of project knowledge belongs; surface concrete,
previously-unflagged placement defects; demonstrate at least one real
one found and corrected in CodeCompass's own codebase, without turning
subjective structural preference into a merge-blocking gate.

## Delivered vs. planned

Delivered, matching the final (fourth-amendment) plan
(`planning/phase-86-knowledge-placement-code-quality-review.md`)
exactly:

- `docs/concepts/knowledge-placement-policy.md` — the eight-category
  policy, reproduced from `decisions/0085` §4.
- `docs/workflows/knowledge-placement-review.md` — the ad-hoc reviewer's
  full brief, dispatched inline each time, never a standing agent.
- `scripts/check_knowledge_placement.py` — two mechanical checks
  (`decision-citation-exists`, blocking; `decision-citation-superseded`,
  informational, scanning an ADR's title/`## Status`/`## Decision`/
  `## Consequences` sections) plus an always-blocking `knowledge-
  placement-unparseable-source-file` diagnostic for a per-file
  `SyntaxError`/`OSError`/`tokenize.TokenError`.
- `tests/test_check_knowledge_placement.py` — 32 tests: extraction
  boundaries, `decision-citation-exists`, fail-closed minimal-content
  edges, parse-failure handling, real-corpus supersession detection
  (`decisions/0027`/`0031`/`0032`/`0033`/`0043`/`0058`/`0061`/`0064`/
  `0070`/`0078`, including the disclosed `0024` conjunction-gap
  regression), determinism, and real-baseline pinning.
- `decisions/0094-knowledge-placement-policy-and-review.md` — records
  the five non-obvious tradeoffs this phase's own plan amendment rounds
  surfaced.
- Real dogfood fix: `src/codecompass/source_resolution.py`'s module
  docstring, rewritten to state current purpose/caller first and frame
  `decisions/0019` with explicit historical markers.
- `CHANGELOG.md`, `docs/decisions.md` (new `0094` row), `planning/
  ROADMAP.md`, `planning/CONTEXT.md` updated at closeout.

**One disclosed deviation from the plan's own literal CLI-shape
wording**: the plan's §6.A generically said to mirror `check_self_
knowledge_quality.py`'s "CLI shape (`--strict`, `--ledgerkit-root`)".
`--ledgerkit-root` is not implemented — this script has no functional
dependency on an external project checkout (unlike Phase 85's script,
which needs a live `repo_root` to reconfirm oracle-result currency);
adding an unused flag would be dead machinery, against this project's
own anti-bloat discipline (`CLAUDE.md`). `--files` (a bounded file-set
parameter) is implemented instead, matching the plan's own substantive
requirement for a bounded/diff-capable run. Flagged for the independent
audit to confirm this judgment call, not hidden.

## Real dogfood — independently reproducible

1. Mechanical script, bounded three-file set: one `decision-citation-
   superseded` (informational) finding, on `source_resolution.py:2`'s
   `decisions/0019` citation.
2. Ad-hoc reviewer dispatch (`docs/workflows/knowledge-placement-
   review.md`'s full text inline): independently judged this a genuine
   placement defect (category 2 misplaced as category 8), citing
   `sync.py`'s real current caller (`decisions/0021`/`0033`, never
   `0019`) and `decisions/0035`/`0033`'s own text confirming `0019`'s
   described mechanism (`grounded_description.py`, `promote`-gated) is
   deleted. Correctly declined to flag `oracle.py`/`staleness.py` (both
   negative controls), reached from full, independent reads, not
   assumed from the phase's own framing.
3. Lead-applied correction: rewrote the docstring to lead with current
   purpose/caller, framing `decisions/0019` explicitly as historical.
4. Post-fix verification: mechanical re-run confirms the citation
   remains correctly informational (never blocking) — the finding is
   *expected* to persist, since the historical citation is legitimately
   retained, not removed. A second, independent dispatch (forked from
   the lead's own session, so it retained full context) re-read the new
   docstring directly and confirmed, in the reverse direction, that a
   second independent reader would now correctly conclude the citation
   is historical, not current, justification — PASS.

Both required real-dogfood outcomes (a genuine finding; a corrected,
re-verified fix) demonstrated independently; no constructed fixture was
used for, or substituted into, this gate at any point.

## Lessons learnt

- **Three implementation-time bugs this phase's own plan had not
  caught, all caught by writing and running tests immediately rather
  than trusting the plan's prose**: (1) `tokenize.TokenizeError` does
  not exist (the real name is `tokenize.TokenError`) — a citation
  typo in the plan that would have crashed on first real malformed-
  source input had it gone untested; (2) `_Citation` needed `frozen=
  True` to be hashable for deduplication; (3) the plan's own hardcoded
  `path.relative_to(ROOT)` (a global repo-root constant) would have
  broken every `tmp_path`-based fixture test — fixed by threading
  `project_root` through `run_all` instead. None of these surfaced
  during the four independent *planning* review rounds, because none
  of those rounds executed the actual implementation — they verified
  the plan's own regex/logic claims in isolation, not an end-to-end
  running script. **Process implication**: a planning review, however
  thorough, cannot substitute for running the real implementation
  against real tests — both are needed, and this phase needed both.
- **The planning phase's own four review rounds were not wasted
  effort**: every real-corpus regex/scoping claim the plan made (the
  8-file supersession match set, the `0027`/`0058`/`0064`/`0032`
  negative controls and disclosed gaps, the `ast.get_docstring(clean=
  False)` line-provenance requirement) proved correct on first
  implementation, confirmed by the exact same tests the plan's own
  independent reviewers had specified. The planning-time regex
  verification work transferred directly into working, passing tests.
- **The dogfood's own honesty clause never had to be invoked** — the
  real `source_resolution.py` instance was still present, unchanged,
  at implementation time, confirmed by direct reading before any other
  implementation work began (not assumed from the planning session).

## Process-improvement feedback

- Worth formalising as a general practice (candidate learning, below):
  when a plan names a specific standard-library exception class by
  name, verify the name actually exists (`python3 -c "import X;
  X.ClassName"`) before relying on it in implementation, not only when
  writing the plan — a plan's own independent review can verify logic
  and regex behaviour exhaustively and still miss a simple naming typo
  if it never actually executes the code.
