# Docs-drift audit — Phase 47 (Stage B decision phase, GATE DB)

**Mode:** Per-phase drift audit (independent, read-only).
**Diff inspected:** working-tree diff at time of audit (everything
uncommitted) — `git status` / `git diff` against `HEAD` (d0da097).

## Verdict: NO DRIFT

## What changed, per `git status`/`git diff`

- NEW `planning/reference-projects/ledgerkit/findings.md` (planning doc,
  not current-truth).
- NEW `planning/phase-49-spec-doc-coverage-and-error-disambiguation.md`
  (plan file, not yet implemented — confirmed no `src/codecompass/`
  diff exists in this change set).
- MODIFIED `planning/ROADMAP.md`, `planning/v1-redefinition/roadmap.md`,
  `planning/context-gaps/inbox.md`, `planning/learnings/inbox.md` —
  planning-process bookkeeping (GATE DB ratification, CG-002/CG-003/
  L-016/L-017 status updates). None of these are in the current-truth
  doc set audited here (`README.md`, `docs/`, `architecture/`,
  `ai-docs/`), so out of scope for a false-statement check, though I
  read them for context and found nothing that contradicts the
  code-truth findings below.
- MODIFIED `architecture/overview.md` — the one current-truth-doc
  change: the `scan_spec_docs` default-glob enumeration under "Spec-doc
  detection & relationship graph" gains `ai-docs/**/*.md` plus an
  explanatory clause ("the last added Phase 37, once this repo's own
  dogfooding sync showed `ai-docs/README.md`/`ai-docs/CLAUDE.md`
  invisible to detection").

No `src/codecompass/` change is present. Phase 49 (the actual `CG-002`
fix — adding `dev-docs/**/*.md` and disambiguating the "not found"
error) has not landed yet; only its plan file exists.

## Verification performed

**1. Independent comparison of the corrected glob-list prose against
the real code**, per the task's instruction not to trust the fix was
correct just because a diff exists.

Read `src/codecompass/spec_docs.py` lines 22-35:

```python
_DEFAULT_GLOBS = (
    "README.md",
    "ARCHITECTURE.md",
    "REQUIREMENTS.md",
    "PRD.md",
    "docs/**/*.md",
    "architecture/**/*.md",
    "decisions/**/*.md",
    "spec/**/*.md",
    "specs/**/*.md",
    "rfcs/**/*.md",
    "*.spec.md",
    "ai-docs/**/*.md",
)
```

Read the corrected `architecture/overview.md` (post-diff, lines
~1370-1373):

> globs a fixed default pattern set rooted at `project_root`
> (`README.md`, `ARCHITECTURE.md`, `REQUIREMENTS.md`, `PRD.md`,
> `docs/**/*.md`, `architecture/**/*.md`, `decisions/**/*.md`,
> `spec/**/*.md`, `specs/**/*.md`, `rfcs/**/*.md`, `*.spec.md`,
> `ai-docs/**/*.md` — the last added Phase 37, ...)

All 12 entries present, in the same order, verbatim. The fix is
correct — `architecture/overview.md` now matches `_DEFAULT_GLOBS`
exactly, item-for-item.

Also checked `_EXCLUDED_ROOT_NAMES` (`CHANGELOG.md`, `CONTRIBUTING.md`,
`CLAUDE.md`) against the doc's exclusion list — unchanged by this diff
and still accurate (not part of the diff, checked as part of "does the
surrounding untouched prose still hold" rather than the fix itself).

**2. Searched for false `dev-docs/**` coverage claims or premature
"not found already disambiguates" claims**, across `README.md`,
`docs/`, `architecture/`, `ai-docs/`:

- `grep -rn "dev-docs"` across those directories: zero hits. Nothing
  implies `dev-docs/**` is covered.
- `grep -rln "not found\|not_found\|disambiguat"`: only one hit,
  `architecture/overview.md:1855`, in an unrelated section (`_run_json`'s
  `shutil.which` subprocess-resolution note, about a nicer error when an
  npm/pipdeptree binary isn't found on `PATH` — nothing to do with
  spec-doc detection or `CG-002`). Confirmed by reading lines
  1840-1870 directly.
- `grep -rln "spec_doc\|scan_spec_docs\|_DEFAULT_GLOBS"` across
  `README.md docs/ ai-docs/ architecture/`: only `docs/cli-reference.md`
  (a single unrelated `graph.spec_docs_without_relations` mention, no
  glob-list content) and `architecture/overview.md` (the section
  audited above). No other doc duplicates or contradicts the glob
  enumeration.
- `README.md` and `ai-docs/{README,CLAUDE}.md` only reference each
  other for entrypoint navigation; none mention spec-doc glob coverage,
  `CG-002`, or `CG-003`.

No current-truth doc claims `dev-docs/**` is already scanned, and none
claims the "not found" error already disambiguates missing-vendor-doc
vs. missing-project-doc — both remain accurately *unclaimed*, matching
reality (Phase 49 hasn't landed).

## Scope note

Checked: the one current-truth-doc change (`architecture/overview.md`'s
glob-list correction) against the actual `_DEFAULT_GLOBS` source, plus a
repo-wide grep sweep of `README.md`, `docs/`, `architecture/`,
`ai-docs/` for `dev-docs`, disambiguation language, and any duplicate/
stale glob-list description.

Deliberately not treated as in-scope for false-statement checking:
`planning/ROADMAP.md`, `planning/v1-redefinition/roadmap.md`,
`planning/context-gaps/inbox.md`, `planning/learnings/inbox.md`,
`planning/reference-projects/ledgerkit/findings.md`, and the new
`planning/phase-49-*.md` plan file — all `planning/` process docs, not
in the current-truth set this audit governs. No code change (no
`src/codecompass/` diff) accompanies this phase, consistent with it
being a decision/consolidation phase rather than an implementation one.
