# Docs-drift audit — Phase 75 (Priority A Ledgerkit validation)

**Mode:** 1 — per-phase drift audit (`documentation-lifecycle.md` §2.5).

**Diff audited:** working-tree changes against `HEAD` (`d4f5e0a`), i.e.
Phase 75's own uncommitted work: `CHANGELOG.md`, `planning/ROADMAP.md`,
`planning/agent-led-workflow.md`, `planning/context-gaps/inbox.md`,
`planning/learnings/inbox.md`, `planning/learnings/promoted.md`,
`planning/v1-redefinition/context-quality-evaluation.md`,
`planning/v1-redefinition/reference-project-protocol.md` (all modified),
plus two new files:
`planning/reference-projects/ledgerkit/04-cur-query-priority-a-validation.md`
and `planning/retros/phase-75-ledgerkit-priority-a-validation.md`.
Confirmed the full change set myself via `git status --porcelain` and
`git diff --stat` rather than trusting the dispatch prompt's own list —
it matches exactly.

**Verdict: NO DRIFT** against `README.md`/`docs/**`/`architecture/**`/
`ai-docs/**`. No `src/codecompass/` file changed this phase (confirmed:
none of the changed paths above are under `src/`), and no current-truth
doc's claim about CodeCompass's own observable behaviour was made false
by this phase's findings. Two protected files (`CLAUDE.md`,
`decisions/*`) are untouched — confirmed, no approval-gate violation.

## What actually changed (system-observable, not just planning prose)

Nothing in `src/codecompass/`. This was a pure evaluation/research
phase: a real baseline-vs-treatment trial against Ledgerkit, a new
context-gap (`CG-009`), a status change for an existing one (`CG-001`:
`candidate` → `recurred`, not funded), two new process learnings
(`L-062`, `L-063`, both about evaluation-methodology hygiene — read-scope
symmetry in dispatch prompts, and never claiming a fresh subagent can
see conversation-only content), and a `planning/ROADMAP.md` status-cell
update. None of these change what CodeCompass *does*; they change what
is *known and evidenced* about what it already does. That distinction is
exactly why the default expectation was NO DRIFT — confirmed, not
assumed, by the checks below.

## Checks performed

### 1. Does any current-truth doc overclaim relative to this phase's evidence?

Specifically checked for claims that CodeCompass indexes a project's own
first-party source symbols, or that overstate context-completeness/
task-relevance beyond PASS WITH GAPS / LOW advantage.

- `README.md` "Core idea", `docs/cli-reference.md`'s `query symbol`
  entry, `docs/quickstart.md`'s `query symbol Anthropic` example, and
  `ai-docs/README.md`'s "What it is"/"What it does" sections all
  consistently scope symbols to **vendors** ("every symbol named
  `<name>`, across every vendor (symbol names aren't globally unique)",
  `docs/cli-reference.md:150-151`; "a SQLite context graph of your
  project's vendors, symbols, and actual usage", `README.md:50`). None
  of these claim or imply first-party-source symbol indexing — `CG-009`'s
  finding (`symbols.vendor_id NOT NULL` FK, no code path walking the
  project's own tree) is **consistent with**, not contradicted by, every
  one of these sentences. No drift.
- `README.md`'s "Core idea" describes spec-doc relationship detection as
  "mechanically linked to the vendors and Skills they mention" — already
  correctly scoped as a citation/mention mechanism, not a task-relevance
  ranker. `docs/domain/concepts/relationship-edge.md` likewise describes
  `doc_relations_edges` as populated only by "mechanical detection
  (import/usage scanning, doc/Skill mapping, doc-mention regex/keyword
  matching)". This matches exactly what `context-evaluator`'s Phase 75
  report found (`query relations` is a citation-graph surface, missed
  the one document with no citation string to match on) — the doc
  already disclosed the limitation inherent in the mechanism; nothing
  newly false. No drift.
- `README.md`'s "Status" section already states the headline
  context-advantage finding at the right level of generality: "The
  measured result is **PASS WITH GAPS, LOW context advantage** — real
  and repeatable, but not dramatic... The remaining ceiling is
  structural (see 'Limitations' below), not a defect." Phase 75's result
  (also PASS WITH GAPS, LOW advantage, on a different task/gap) is a
  **second, independent data point in the same direction** as what's
  already disclosed, not a contradiction of it. The existing sentence
  doesn't claim "measured exactly once" or "measured only at these two
  points" in a way this second trial falsifies — it points at
  `planning/v1-closeout.md §5` for "full results," and Phase 75 is later
  than that closeout. This is a candidate for `docs-maintainer` to
  *enrich* (cite the new trial alongside the existing one) but not a
  case of an existing sentence being made **false** — no blocking
  finding.

### 2. Does `README.md`'s "Limitations" section need a new bullet?

Not required to avoid a false statement — nothing in the current six
bullets asserts or implies first-party-source symbol indexing exists.
This is a **non-blocking observation, not a drift finding**: the
Limitations list is explicitly disclosed as "not exhaustive" (`README.md:282`,
"Full, current list ... `planning/ROADMAP.md`'s 'Future-improvement
backlog'"), and `CG-009` already lives in that backlog table
(`planning/ROADMAP.md`, added this phase). A future docs pass could
reasonably add a bullet like "no symbol-level index exists for a
project's own first-party source, only tracked vendor dependencies
(`CG-009`)" for a reader who might otherwise assume `query symbol`
covers their own code — but the current text is not wrong, just
terser than it could be. Not counted toward the DRIFT verdict.

### 3. `docs/domain/` staleness re: `query relations`/`query symbol`/task-context completeness

Checked every `docs/domain/concepts/*.md` page mentioning `query
relations`, `query symbol`, or completeness/task-relevance language
(`context-packet.md`, `relationship-edge.md`). Both describe these
surfaces in terms already consistent with Phase 75's findings (graph
citation only, read-only consultation, never a completeness guarantee).
No staleness from this phase's *findings* on these two pages' own
substantive claims.

However, per the domain-claim staleness check (step 5, this phase's
diff *touching* files a concept page's references block cites — a
citation-currency question, separate from whether the page's claim
itself is still true):

**Domain-claim staleness candidates (not drift findings — flagged for `domain-skeptic`):**

- **`docs/domain/concepts/reference.md:127`** cites
  `planning/context-gaps/inbox.md:267-363` for `CG-005`. This phase's
  diff inserts ~142 lines before that point in the file (new `CG-009`
  entry plus surrounding edits, first hunk `@@ -8,6 +8,148 @@`). `CG-005`'s
  actual content now starts at line 601, not 267 — confirmed by grep. The
  citation's line range is now stale by a wide enough margin that anyone
  following it lands in the wrong section entirely (the middle of an
  unrelated later entry, not `CG-005`). This is a citation-currency issue
  caused directly by this phase's diff to the cited file, not a claim
  about the page's own substantive correctness — flagged for
  `domain-skeptic`/next reconciliation, not counted as drift here.
- **`docs/domain/concepts/context.md:131`** cites
  `planning/v1-redefinition/context-quality-evaluation.md:1-60`. This
  phase's diff inserts 7 lines at line 53 (the new L-062 cross-reference
  note), within that cited range. The range still points at
  substantively the same §1 material; this is a much smaller/likely
  harmless shift than the `reference.md` case above, but named here for
  completeness since the diff does touch the exact file and line-window
  cited.
- **`docs/domain/concepts/reference.md:124`** cites
  `planning/v1-redefinition/reference-project-protocol.md:1-30`. This
  phase's diff inserts new content after line 93 (the new §2.2 read-scope
  rule, `L-062`) — outside the cited `1-30` range, so this specific
  citation is unaffected by line-shift. Named only because the file was
  touched; no actual staleness risk identified.
- More substantively (not a line-citation issue): `reference.md`'s prose
  description of "(b) a reference project" and `context.md`'s prose
  citing `context-quality-evaluation.md` both describe the
  baseline/treatment protocol narratively. This phase added a real new
  rule to that protocol (`reference-project-protocol.md` §2.2: dispatch
  prompts must state read-scope symmetry explicitly for comparison
  trials). Neither concept page's prose is now *wrong*, but a future
  domain-skeptic pass reconciling `docs/domain/` against the current
  protocol text may want to confirm the concept page's summary of "the
  protocol" still doesn't omit anything now load-bearing.

### 4. Protected-file check

`git diff --name-only` for this phase touches no file under `decisions/`
and does not touch `CLAUDE.md`. Confirmed directly (empty result for
`git diff --name-only -- CLAUDE.md 'decisions/*'`). No approval-gate
violation.

## Scope note

**Checked:** the full working-tree diff for this phase (`git status`,
`git diff --stat`, and per-file `git diff` for every changed/new file);
grepped `README.md`, `docs/**`, `architecture/**`, `ai-docs/**` for
symbol/query-relations/completeness/first-party-source language and
verified each hit against the phase's own evaluation report
(`04-cur-query-priority-a-validation.md`) and the underlying code shape
it cites (`symbols.vendor_id NOT NULL`, `sync.py::rebuild_project_graph`
iterating `VendorConfig` only); read `docs/domain/concepts/context-packet.md`
and `relationship-edge.md` (the two pages whose own text discusses
`query relations`/`query symbol`) plus `reference.md` and `context.md`
(the two pages whose references blocks cite files this phase's diff
touched) for the domain-claim staleness check.

**Not checked / deliberately out of scope:** the substantive correctness
of any other `docs/domain/concepts/*.md` page not implicated by this
phase's diff or findings (full domain-corpus reconciliation is a
separate, later activity); `planning/agent-led-workflow.md`,
`planning/learnings/*`, `planning/context-gaps/inbox.md`'s own prose
accuracy as *process* documents — these are planning/process docs, not
"current-truth docs describing CodeCompass's own system behaviour" in
this audit's sense, and are governed by the learning/context-gap
lifecycle's own review, not this drift audit; whether `CG-001`'s
`recurred` status or `CG-009`'s filing themselves are well-justified —
that is `knowledge-curator`'s and the lead's own call, not a docs-drift
question.
