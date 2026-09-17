# Docs-drift audit — Phase 55b (populate `doc_artifacts.name` for `spec_doc` rows, closes CG-004)

**Scope:** the phase's implementation diff (`src/codecompass/spec_docs.py`,
`doc_mapping.py`, `sync.py`) plus `docs-maintainer`'s own doc
reconciliation (`architecture/overview.md`, `docs/cli-reference.md`),
checked against current-truth docs. Independent re-derivation from
source and a live, isolated `codecompass sync` run — not from
`docs-maintainer`'s summary of what it changed.

**Verdict: NO DRIFT — 1 non-blocking finding (fixed before commit).**

## What was checked

- Diffed the four touched source files directly.
- Built and synced an isolated copy of the working tree (`rsync` to a
  scratch dir, not a git worktree/stash) to run `codecompass sync` +
  `codecompass query relations` for real and inspect `context-graph.db`
  directly — confirming behavior rather than trusting any doc's claims
  about it.
- Live-tested `codecompass query relations "CLI reference"` against
  this repo's own real sync — confirmed the real edge
  `architecture/overview.md --[mentions_artifact]--> docs/cli-reference.md`
  (target name "CLI reference") appears, heading-attributed correctly,
  matching `docs/cli-reference.md`'s own updated description of spec
  docs as reverse-lookup targets.
- Confirmed live, after a real sync, that `SELECT count(*) FROM
  doc_relations_edges dre JOIN doc_artifacts s/t ... WHERE s.path =
  t.path` returns `0` — the self-mention exclusion holds in the real
  running tool, not just in a unit test.
- Grepped `README.md`, `ai-docs/README.md`, and every file under
  `docs/` for `spec_doc`/`mentions_artifact`/`doc_relations` — no other
  current-truth doc makes a claim this phase's diff could contradict.
- Confirmed `planning/context-gaps/inbox.md`'s `CG-004` entry's own
  status/closure note is honest — doesn't overclaim resolution beyond
  what the diff supports (correctly names the residual `CG-006` gap
  rather than implying total resolution).

## Finding (non-blocking, fixed before commit)

`architecture/overview.md`'s `scan_spec_docs` description compressed the
real fallback chain ambiguously: it read as if the filename-stem
fallback only applied when there's no H1 at all, when the real code
(`spec_docs.py::_extract_title`) also falls through to the stem when an
H1 *is* present but fails the specificity check. The file's own fuller
"Spec docs become relationship targets of each other (Phase 55b...)"
subsection stated the chain correctly elsewhere in the same file — an
internal-consistency gap, not a claim a user would act on incorrectly.
**Fixed** (this closeout, before commit): the `scan_spec_docs`
description now states the chain explicitly — H1-if-present-and-specific,
else stem-if-specific, else `None` — matching the fuller subsection
exactly.

## Verified as accurate (no drift)

- `architecture/overview.md`'s new "Spec docs become relationship
  targets of each other (Phase 55b...)" subsection: `_extract_title`/
  `_is_specific_enough` logic, the `sync.py` third-argument widening,
  and the path-based self-mention exclusion all match the real code
  exactly.
- `doc_mapping.py`'s own updated docstring (the self-mention exclusion
  explanation) matches its own real logic.
- `docs/cli-reference.md`'s `query relations <name>` reverse-lookup
  description, live-verified as above.
- `planning/context-gaps/inbox.md`'s `CG-004` closure note and new
  `CG-006` entry, both independently re-derived from the real diff and
  the real Ledgerkit files they cite (not taken on trust).

## Scope note

Checked: `README.md`, `ai-docs/README.md`, `docs/cli-reference.md`,
`docs/config-schema.md`, `architecture/overview.md`,
`planning/context-gaps/inbox.md`'s `CG-004`/`CG-006` entries, and the
three changed source files, against a real live `sync` + `query
relations` run in an isolated scratch copy of the working tree. Not
audited (out of this phase's stated scope, not current-truth docs under
`CLAUDE.md` §5): `planning/context-observations/inbox.md` (a
learning-lifecycle log, not a user-facing doc), and Ledgerkit-repo
content itself (a different repository, not verifiable as a CodeCompass
documentation-accuracy question). `decisions/0043` untouched, correctly
— nothing in this phase reverses or falsifies it.
