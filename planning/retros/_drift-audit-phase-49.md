# Docs-drift audit — Phase 49 (spec-doc coverage + error disambiguation)

**Mode:** 1 (per-phase drift audit), independent of `docs-maintainer`.
**Diff inspected:** uncommitted working tree (`git diff`) touching
`src/codecompass/spec_docs.py`, `src/codecompass/cli.py`,
`tests/test_spec_docs.py`, `tests/test_cli.py`,
`architecture/overview.md`, `docs/cli-reference.md`.

**Verdict: NO DRIFT**

## What actually changed (verified from code, not from any agent's summary)

1. `spec_docs.py::_DEFAULT_GLOBS` gained one entry, `"dev-docs/**/*.md"`,
   appended after `"ai-docs/**/*.md"` (13th entry overall, not counting
   from zero — see note below on an off-by-one in the task framing that
   does *not* originate in any doc).
2. `cli.py` gained `_relations_not_found_error(name)`, called only from
   `query_relations`'s `relations is None` branch (replacing the prior
   `_not_found_error(name)` call there). It checks
   `(Path.cwd() / name).is_file()`: if true, prints a distinct message
   ("exists as a file but was not detected as a spec/vendor doc ...
   check whether it's covered by spec_docs's glob coverage, then
   re-run sync") and exits 1; otherwise it falls through to the
   original `_not_found_error(name)` ("not found in context-graph.db").
   `query_vendor` and `query_symbol` still call the plain
   `_not_found_error` (vendor) or print their own unrelated
   "no symbol named ... found" message (symbol) — neither call site was
   touched by this diff.

## Checks performed

**(1) `_DEFAULT_GLOBS` vs. `architecture/overview.md`'s enumeration —
compared side by side, in order:**

Code (`spec_docs.py`): `README.md`, `ARCHITECTURE.md`, `REQUIREMENTS.md`,
`PRD.md`, `docs/**/*.md`, `architecture/**/*.md`, `decisions/**/*.md`,
`spec/**/*.md`, `specs/**/*.md`, `rfcs/**/*.md`, `*.spec.md`,
`ai-docs/**/*.md`, `dev-docs/**/*.md`.

Doc (`architecture/overview.md` post-edit, `scan_spec_docs` bullet):
identical list, identical order, `ai-docs/**/*.md` annotated "(added
Phase 37, ...)" and `dev-docs/**/*.md` annotated "(added Phase 49,
closing CG-002 ...)". Exact match — no drift.

Note: the task framing described this as "the 12th entry"; by literal
position it's the 13th (README.md is #1). This is an off-by-one in the
audit request's own phrasing, not a doc defect — neither
`architecture/overview.md` nor `spec_docs.py` asserts a count anywhere,
so there's nothing in the doc to be wrong about.

**(2) `_relations_not_found_error`/`query_relations` vs.
`docs/cli-reference.md`'s new sentence:**

Doc's new sentence: "Errors if `<name>` matches nothing in the graph at
all; if `<name>` is a real file on disk that simply wasn't detected as a
spec/vendor doc, the error says so explicitly and points at spec-doc
glob coverage, rather than reading as if the file doesn't exist."

This is accurate to the code: the `is_file()` check is generic
(any real file relative to cwd, described in the doc as "a real file on
disk"), the message text does say "was not detected as a spec/vendor
doc" and does point at "glob coverage" (matching the code's literal
string), and the fallback (no such file) does keep the original bare
"not found" wording (doc's "rather than reading as if the file doesn't
exist" correctly implies the alternative path is unchanged). Ran the two
new tests independently
(`test_query_relations_unscanned_file_gets_disambiguated_error`,
`test_query_relations_genuinely_nonexistent_name_keeps_not_found_message`)
plus the full targeted suite — 76 passed — confirming the doc's claim
against actual runtime behaviour, not just the source read.

**(3) `query vendor` / `query symbol` "not found" behaviour, confirmed
unaffected and still accurately documented:**

- `query_vendor`: unchanged call site, still `_not_found_error(name)` on
  `profile is None`. `docs/cli-reference.md`'s line ("Errors if `<name>`
  isn't a known vendor in the graph") is untouched by this diff and
  remains accurate.
- `query_symbol`: does not call `_not_found_error` at all (pre-existing;
  prints its own yellow "no symbol named ... found" line, no
  `typer.Exit`). `docs/cli-reference.md`'s `query symbol` bullet has no
  "Errors if ..." sentence at all (pre-existing), correctly not implying
  the new disambiguation applies there. Neither bullet was edited by
  `docs-maintainer`, and neither needed to be — verified the docs don't
  now imply the fix touched these paths.

## Reverse check (did the change make an existing doc sentence false
without anyone touching it?)

Searched `README.md`, `ai-docs/README.md`, `docs/cli-reference.md`,
`architecture/overview.md` for other mentions of the glob list or
`query relations`'s error behaviour. Found only the illustrative
"(README, `ARCHITECTURE.md`, `docs/**/*.md`, `decisions/**/*.md`,
etc.)" lists in `README.md` and `docs/cli-reference.md`, and
`ai-docs/README.md`'s "(README, `architecture/`, `decisions/`, etc.)" —
all deliberately elided with "etc." and never enumerated the full glob
list, so `dev-docs/`'s addition doesn't falsify them. Confirmed this
matches the Phase 37 precedent: `git show 7fea354` (Phase 37's
`ai-docs/**/*.md` addition) touched only `spec_docs.py`,
`tests/test_spec_docs.py`, and planning/changelog files — it did not
touch `README.md`, `docs/cli-reference.md`, or `ai-docs/README.md`
either, so leaving those "etc." lists alone now is consistent, not a
new omission.

## Scope note

Checked: `spec_docs.py`'s glob list, `cli.py`'s `query relations`
not-found path and its two sibling not-found paths (`query vendor`,
`query symbol`), and every current-truth doc location (`README.md`,
`docs/cli-reference.md`, `ai-docs/README.md`, `architecture/overview.md`)
that a `grep` for the glob patterns, `_not_found_error`/"not found", or
`query relations` surfaced. Did not re-audit doc sentences unrelated to
spec-doc detection or `query relations`'s error behaviour — out of this
phase's diff. Test/lint/strict-docs-check claims were independently
re-run rather than trusted: `.venv/bin/pytest tests/test_spec_docs.py
tests/test_cli.py -q` → 76 passed; `python scripts/check_user_docs.py
--strict` → "no findings" (exit 0).

## One non-blocking, out-of-scope observation for the lead (not a docs
finding — flagged for completeness)

`cli.py::_relations_not_found_error`'s docstring cites
`decisions/0051` alongside `CG-002`/`L-016` as backing for "a spec-doc
glob-coverage gap." Read `decisions/0051`
(`decisions/0051-agent-suggested-context-is-captured-not-graphed.md`):
it is about whether agent-suggested relationships get written to the
context graph (Phase 43c), unrelated to spec-doc glob coverage or
`query relations` error messages. This looks like a mistaken ADR
citation in a `src/` docstring, not `decisions/0051`'s own content
being wrong, and it is not referenced by name from any of README.md,
docs/, architecture/, or ai-docs/ — so it does not constitute doc drift
under this audit's scope, but the lead may want it corrected before this
diff is committed (it will otherwise mislead future readers of the
docstring tracing that citation).
