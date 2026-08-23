# Phase 37: Register `ai-docs/` in spec-doc detection

## Status

`done`

## Context

Found live during Phase 35/36's dogfooding sync (this repo's own whole-project
`codecompass sync`, run right after Phase 35 created `ai-docs/README.md` and
`ai-docs/CLAUDE.md`): `codecompass query relations ai-docs/README.md` errored
`'ai-docs/README.md' not found in context-graph.db`. `spec_docs.py`'s
`_DEFAULT_GLOBS` — the fixed pattern set that classifies a project's own
hand-authored docs as `spec_doc` graph nodes — has no entry for `ai-docs/`, so
neither new file is detected at all: invisible to `query relations`, and never
a candidate for Phase 22/29's mechanical-then-AI relationship detection.

`spec_docs.py`'s own comment states the list ships fixed "until a real project
shows it's wrong for it" — this repo, tracking its own `ai-docs/` folder, is
exactly that evidence.

## Scope

**Covers:**
- Add `"ai-docs/**/*.md"` to `spec_docs._DEFAULT_GLOBS`.
- One new regression test in `tests/test_spec_docs.py` confirming an
  `ai-docs/*.md` file is detected.

**Explicitly does not cover:**
- Any other change to spec-doc detection's exclusion rules or prune logic —
  unaffected; `ai-docs/CLAUDE.md` is correctly *not* excluded by the existing
  root-level-only `CLAUDE.md` exclusion (`_is_excluded` only fires for
  `rel_path.parent == Path(".")`, and `ai-docs/CLAUDE.md`'s parent is
  `ai-docs`, not `.`) — verified, not assumed.
- `vendor.toml`-level configurability of the glob set — still explicitly
  deferred per the module's own existing design note.

## Design decisions

- **One glob pattern, no other change.** Smallest fix that closes the actual
  gap; consistent with this project's posture of fixing exactly the found
  problem (Phase 26-29, 33, 34 precedent) rather than expanding scope.

## Files

- `src/codecompass/spec_docs.py` — add `"ai-docs/**/*.md"` to `_DEFAULT_GLOBS`.
- `tests/test_spec_docs.py` — new regression test.
- `planning/ROADMAP.md`, `CHANGELOG.md`, `planning/CONTEXT.md` — per usual.

## Verification

- `pytest tests/test_spec_docs.py` passes, including the new test.
- `ruff check .` clean.
- **Confirmed live**: re-ran `codecompass sync --budget 0` against this repo
  after the fix; `codecompass query relations ai-docs/README.md` and
  `ai-docs/CLAUDE.md` both now resolve (no longer "not found").
