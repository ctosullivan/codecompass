# Drift audit — Phase 45 (Ledgerkit registration + baseline evaluation)

**Auditor:** docs-reconstructor (MODE 1, per-phase, read-only)
**Base:** working tree vs HEAD `e66f932` (everything below is uncommitted)
**Plan:** `planning/phase-45-ledgerkit-baseline.md`
**Date:** 2026-09-13

## Verdict

**NO DRIFT.**

## What actually changed about the system

Formed independently from `git status`/`git diff`, not from any other
agent's summary:

- New `planning/reference-projects/ledgerkit.md` (registration record),
  `planning/reference-projects/ledgerkit/00-baseline.md` (baseline
  context-quality report, 3 questions, one **FAIL** verdict),
  `planning/phase-46-ledgerkit-tasks.md`.
- Modified `planning/reference-projects/README.md` (registry row: Ledgerkit
  `not yet registered` → `registered, baseline evaluated`, pinned commit
  filled in), `planning/context-use-log.md` (+1 dated entry),
  `planning/context-gaps/inbox.md` (+CG-002), `planning/learnings/inbox.md`
  (+L-015, +L-016), `planning/context-health.md` (+ Ledgerkit-clone
  assessment, appended per its own new header exception, not replacing the
  2026-09-11 CodeCompass-own-repo assessment).
- `git diff --stat` confirms every changed/added path is under `planning/`.
  **No path under `src/codecompass/`, `tests/`, `docs/`, `architecture/`,
  `ai-docs/`, or `README.md`.**

This is a documentation/evaluation phase about an *external* project
(Ledgerkit); it does not touch CodeCompass's own CLI, config schema,
generated-file formats, module responsibilities, data model, defaults, or
user-facing error messages. There is therefore no CodeCompass system
behaviour for a current-truth doc to newly misdescribe.

## Verification performed (not trusting any prior agent's account)

- `git diff --stat` — full list of touched paths, confirmed none under the
  four current-truth doc roots.
- Read every diff hunk directly (`planning/reference-projects/README.md`,
  `planning/context-gaps/inbox.md`, `planning/learnings/inbox.md`,
  `planning/context-health.md`, `planning/context-use-log.md`) plus the
  full text of the three new files, rather than accepting `docs-maintainer`'s
  characterization of them.
- Independently checked the two claims about CodeCompass's *own* code that
  L-015/L-016/CG-002 rest on, against the actual source (since if these
  were wrong, the planning docs themselves would already be drift, even
  though planning/ is outside this audit's target-doc set):
  - `src/codecompass/spec_docs.py::_DEFAULT_GLOBS` — confirmed: no
    `dev-docs/**/*.md` entry (globs are `README.md`, `ARCHITECTURE.md`,
    `REQUIREMENTS.md`, `PRD.md`, `docs/**/*.md`, `architecture/**/*.md`,
    `decisions/**/*.md`, `spec/**/*.md`, `specs/**/*.md`, `rfcs/**/*.md`,
    `*.spec.md`, `ai-docs/**/*.md`). CG-002's premise holds.
  - `src/codecompass/discovery.py::discover_python()` — confirmed:
    reads only `data.get("project", {}).get("dependencies", [])`;
    docstring explicitly says `[project.optional-dependencies]` is "not
    scanned (documented ...)". L-015's premise holds.
  - `src/codecompass/cli.py::_resolve_relations` / `_not_found_error` —
    confirmed: `_resolve_relations` returns `None` (triggering the same
    `error: {name!r} not found in context-graph.db` message) whether the
    name was never scanned as a doc artifact or is a genuine typo — no
    differentiating signal. L-016's premise holds.
- `python scripts/check_user_docs.py --strict` → `no findings`.

## Current-truth product docs checked (README.md, docs/, architecture/, ai-docs/)

| Check | Result |
|---|---|
| Does any current-truth doc mention Ledgerkit, "reference project(s)", or `dev-docs/` in a way this phase's findings could falsify? | `grep -rniE "ledgerkit\|reference.project\|dev-docs" README.md docs/ architecture/ ai-docs/` → one hit: `README.md:16`, a generic clause ("validated against real external reference-project work") pointing at `planning/v1-redefinition/`. It names no specific project, phase, or finding — Ledgerkit's baseline result (LOW context advantage, one FAIL, CG-002) doesn't touch it either way. |
| `docs/cli-reference.md`'s description of `codecompass sync`'s manifest discovery (lines 64-78: `[project.optional-dependencies]` "is not scanned") vs. L-015's finding | Already accurately documents the scope boundary L-015 is about. L-015's actual gap is narrower and still true: the *silence at the `query vendors` / bare-discovery output layer* about that boundary, which is a distinct, undocumented spot — not a case of an existing sentence being contradicted. No current-truth doc claims `query vendors` surfaces optional-dependency caveats, so nothing is now false. |
| `docs/cli-reference.md`'s `query relations` section (lines 158-183: "Errors if `<name>` matches nothing in the graph at all.") vs. L-016's finding | Still literally true — it does error under exactly that condition. The doc doesn't claim the error message distinguishes *why* nothing matched, so L-016 (a UX ambiguity, filed as a future-improvement candidate) doesn't contradict it. |
| `architecture/overview.md`'s spec-doc-detection section (~line 1369-1373, prose enumeration of `_DEFAULT_GLOBS`) | Missing `ai-docs/**/*.md` from its prose list (code has it, Phase 37). Confirmed via `git log -1` on both files that neither `architecture/overview.md` (last touched `3b7f27a`) nor `src/codecompass/spec_docs.py` (last touched `7fea354`) appears anywhere in this phase's diff — this gap **predates Phase 45 and is untouched by it**. Agree with `docs-maintainer`: pre-existing, unrelated drift, not phase 45's to fix. (Also separately: this enumeration was already partial/non-exhaustive before Phase 45 — it doesn't claim completeness — so `dev-docs/`'s absence from the code's own glob list, CG-002's subject, isn't a new falsification of this sentence either; it was already silent on `dev-docs/` before this phase, same as it was already silent on the full list generally.) |
| Reverse check — did this diff make any existing current-truth-doc sentence false without anyone touching that doc? | None found. No current-truth doc makes a claim about Ledgerkit, `dev-docs/` glob coverage, the optional-dependencies query-layer silence, or the `query relations` error-message granularity that this diff's findings (CG-002, L-015, L-016) contradict. |

## Scope note

- Confirmed `docs-maintainer`'s "no current-truth doc needs an edit"
  finding independently, from the diff and source directly, not from its
  summary.
- Did not audit `planning/**` content itself (the new/changed files'
  internal correctness, template compliance, or whether CG-002/L-015/L-016
  are well-formed entries) beyond the two source-code cross-checks above —
  that's `release-phase-auditor` / `knowledge-curator` territory, not this
  drift audit's.
- Did not re-litigate the `architecture/overview.md:1369-1373` /
  `ai-docs/**/*.md` gap beyond confirming it is pre-existing and outside
  this diff — no action taken on it here, per the lead's framing.
- Did not touch `CLAUDE.md`/`CONTRIBUTING.md` (already committed
  separately in `e66f932`, an unrelated §6 governance amendment, out of
  scope for this audit).
