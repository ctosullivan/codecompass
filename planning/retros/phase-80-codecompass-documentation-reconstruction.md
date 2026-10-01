# Phase 80 retro — CodeCompass-wide documentation reconstruction + lightweight template refresh

## Goal

Correct two further Phase 79 defects found by direct user review, then
apply Phase 79's own clean-room methodology at project scope for the
first time across two repositories: a full, bounded reconstruction for
CodeCompass itself, and a deliberately lighter-weight application to
`codecompass-template`, closing with independent verification of both
documentation accuracy and coding-context usefulness, kept as two
separate results.

## Delivered vs. planned

All four parts of the governing prompt delivered:

- **Part 1**: both defects reproduced before fixing (a disposable git
  fixture for the snapshot identity-absence gap; the real pre-fix
  `tinytodo2` implementation for the id-reuse overgeneralization) and
  corrected with dated correction notices, new assertion/snapshot
  versions where required, and an independent falsification attempt
  that found no counterexample.
- **Part 2**: the full five-stage pipeline run once at project scope —
  freshness review (found and fixed two genuine pre-existing staleness
  issues neither defect-correction nor any prior phase had caught),
  frozen snapshot, model-blind reconstruction, comparison (zero real
  conflicts), a fresh draft staged before reconciliation, and
  reconciliation against the real live docs (one genuine gap found and
  fixed).
- **Part 3**: a genuine fresh-adopter exercise (not just inspection)
  into both a new and an existing project found four real usability
  defects in the template, all fixed and pushed to the real remote.
- **Part 4**: 15 frozen reader questions verified against primary
  evidence (13 correct, 2 incomplete, both fixed); a bounded
  coding-context packet independently evaluated and found to **FAIL**
  with **LOW** advantage — a real, consequential finding, not a
  rubber stamp — kept strictly separate from the documentation-accuracy
  result throughout.

Not delivered as originally imagined, by design: Part 2's Stage 1 did
not re-derive CodeCompass's entire domain corpus from scratch. The
existing `docs/domain/` corpus was already approved and evidence-backed;
re-deriving it wholesale would have discarded good work to manufacture
busywork. This was a deliberate, disclosed scoping decision (see the
plan's own §0), not a shortfall.

## What actually went wrong, and what it taught

**The coding-context packet FAIL is the single most important result
of this phase, methodologically.** The packet's own factual error (a
real helper-function conflation, `_open_graph_or_note`/`_graph_session`
vs. the actually-used `_open_graph_if_exists`) originated in the Stage 2
model-blind reconstruction's own summary prose, survived Stage 3's
comparison untouched, and survived Stage 5's reconciliation against the
real live docs untouched — not because either check was performed
carelessly, but because **neither check's own scope covered this level
of detail**: Stage 3 compares against the snapshot's conceptual Claims
(which don't describe internal helper-function names), and Stage 5
compares against real published docs (which, correctly, also don't
describe internal helper-function names at that granularity — that's
appropriate for a README/CLI-reference, just not for a coding-context
packet meant to hand an implementer a literal code skeleton). The error
only surfaced when the packet was actually put to its real, intended
use and independently evaluated against raw source. This is direct,
first-party evidence for exactly the design decision the governing
prompt insisted on: keeping documentation-accuracy and coding-context-
advantage as two separate, independently-run results is not
belt-and-suspenders redundancy — a documentation-accuracy pass
genuinely cannot catch every error a coding-context pass will, because
their own evidentiary standards operate at different levels of detail.

**A near-miss, caught before it became a real mistake**: Stage 4's
fresh documentation draft was briefly written into
`planning/v1-docs-reconstruction/phase-80-draft/` before being noticed
and moved to its own `planning/phase-80-docs-draft/` — that directory
turned out to be Phase 64's own, already-closed, differently-named
shadow-documentation deliverable from an earlier milestone. Nothing was
overwritten (a new subdirectory was added, not an existing file
touched), but nesting one phase's artifact inside another, differently-
named, already-historical phase's own tree would have been genuinely
confusing to a future reader. Caught by reading that directory's own
`README.md` before committing anything into it — a concrete instance of
this project's own standing discipline (investigate unfamiliar existing
state before writing into it) paying off in a case that had nothing to
do with destructive risk, just naming clarity.

**A tooling mishap, not a methodology one**: a multi-line `git commit
-m` message containing backtick-quoted code identifiers
(`` `codecompass query source-stats` ``) was shell-interpreted as command
substitution, silently corrupting the landed commit message (the
backticked span was replaced by a failed command's own error text).
Caught by reading the commit back with `git log -1 --format=%B`
immediately after committing — not a habit to drop. Fixed via
`git commit --amend -F <file>` since the commit hadn't been pushed yet;
would have needed a follow-up corrective commit instead had it already
reached `origin`. Filed as product feedback (not a project learning,
since it's a Claude Code tool-usage pitfall, not a CodeCompass
development-process one): write multi-line commit messages to a file
and use `-F`, never inline `-m` with backtick-quoted content.

## Process-improvement feedback

- **Verify a "fresh" dispatch's own evidence citations are specific
  enough to be independently checked, before trusting them downstream.**
  The Stage 2 reconstruction's CLI-pattern claim was phrased with
  complete confidence ("a consistent... pattern") and cited real,
  correct file-level evidence for the *parts* it got right, which made
  the overgeneralized part easy to miss on a first read. The fix isn't
  "trust reconstructions less" — Stage 2's own confirmed-live findings
  (75/75 graph tests, the migration behavior, the enrichment-survival
  guarantee) were all independently reconfirmed accurate — it's that a
  summary sentence spanning multiple call sites ("every X does Y") is
  exactly the shape of claim most worth spot-checking against at least
  one of the cited call sites directly, even when the broader pattern
  the sentence describes is real.
- This phase's own scale (two repositories, five pipeline stages, a
  template fresh-adopter exercise, 15 frozen reader questions, a
  separate coding-context evaluation) worked because each stage was
  dispatched as its own bounded, isolated unit with an explicit scope
  manifest and a clear single deliverable — no single dispatch tried to
  do more than one stage's worth of work. Worth keeping as the default
  shape for any future whole-project reconstruction, rather than
  attempting fewer, larger dispatches to save overhead.

## Candidate learnings

Filed to `planning/learnings/inbox.md` for `knowledge-curator` triage:

- **L-079** (process, likely promotable): documentation-accuracy checks
  and coding-context-advantage checks are not substitutes for each
  other even when both pass through the same two-stage (compare, then
  reconcile) process — their own respective "ground truth" (published
  prose vs. literal call-site behavior) operates at different
  granularities, and an error below a documentation check's own
  granularity can still mislead a coding-context packet. Already
  structurally enforced by this phase's own explicit separate-results
  instruction; this learning generalizes the *why*, for future phases
  that might be tempted to merge the two checks for efficiency.
- **L-080** (tooling, Claude-Code-specific, not a CodeCompass
  development-process rule): never construct a multi-line `git commit
  -m` message containing backtick-quoted code identifiers as an
  interpolated shell string — the backticks execute as command
  substitution. Use `git commit -F <file>` for any commit message
  containing backticks.

## Links

- Plan: `planning/phase-80-codecompass-documentation-reconstruction.md`
- Initiating prompt: `planning/phase-80-documentation-reconstruction-prompt.md`
- Frozen reader questions: `planning/phase-80-frozen-reader-questions.md`
- Stage artifacts, verification reports, correction notices:
  `planning/phase-80-docs-draft/`
- Template fixes: `codecompass-template@68bae8e`
