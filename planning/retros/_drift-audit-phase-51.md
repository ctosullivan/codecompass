# Drift audit — Phase 51 (re-run Ledgerkit evaluation, GATE DC)

**Verdict: NO DRIFT**

## What changed (per `git diff`, everything uncommitted)

Planning/reference-project files only:

- `planning/reference-projects/ledgerkit/00-baseline.md` — +136/-0
- `planning/reference-projects/ledgerkit/01-query-semantics.md` — +191/-0
- `planning/reference-projects/ledgerkit/findings.md` — +61/-0
- `planning/reference-projects/ledgerkit.md` — +16/-0
- `planning/reference-projects/README.md` — +1/-1 (registry row)
- `planning/ROADMAP.md` — +2/-1 (splits the old "50-51" combined row into
  separate 50/51 rows)
- `planning/v1-redefinition/roadmap.md` — +1/-0 (adds a `Plan:` link line)

No change to `src/codecompass/`, `CHANGELOG.md`, `docs/`, `architecture/`,
`ai-docs/`, or `README.md`. Confirmed directly with `git diff --stat --
src/codecompass/ CHANGELOG.md docs/ architecture/ ai-docs/ README.md`,
which returns empty.

## Append-only claim — verified

Checked `git diff --stat` per-file for the five files named in the task:

| File | Insertions | Deletions |
|---|---|---|
| `ledgerkit/00-baseline.md` | 136 | 0 |
| `ledgerkit/01-query-semantics.md` | 191 | 0 |
| `ledgerkit/findings.md` | 61 | 0 |
| `ledgerkit.md` | 16 | 0 |
| `reference-projects/README.md` | 1 | 1 |

Four of the five are strictly append-only (new dated sections/rows only,
verified by reading the diffs in full — no existing table row or
paragraph was edited or removed). `ledgerkit.md`'s new content is two new
table rows (`00.Q2` and `01`, Phase 51 re-run) plus a new "GATE DC"
narrative paragraph — original Q1/Q2/Q3/01 rows and surrounding prose are
untouched.

**One nuance on `reference-projects/README.md`:** its single row for
Ledgerkit is not append-only in the literal sense — the "Status" cell's
text was replaced (`registered, baseline evaluated (Phase 45)` →
`baseline + 1 genuine task evaluated (Phases 45-46); GATE DB fix (Phase
49) confirmed working at GATE DC (Phase 51, re-pinned 05218e3)`). This is
a same-line edit, not a pure addition, so the "no original content
deleted" framing doesn't hold letter-for-literal for this one file. In
substance this is a registry's *current-status* field — by its own
column header and by every other row in that table — being updated to
reflect current status, which is the correct and expected behavior for a
"current state" summary cell, not a historical record. It's not
misleading: the new text is a strict superset of information (adds the
Phase 46/49/51 history, doesn't erase or contradict anything the old text
asserted) and the pinned starting-revision column is untouched. Flagging
as a minor terminology mismatch (the task's "append-only" framing doesn't
literally apply to this one cell) rather than a drift finding — nothing
in the replaced text is now false or missing information a reader needed.

The second overall deletion in the working tree (`planning/ROADMAP.md`,
"50–51" combined row split into two rows) is not one of the five files
the append-only claim was made about, and is itself an accurate,
non-destructive split (old row's content is fully preserved, just
divided across two rows with 51 updated to reflect its plan file and new
status). Not a `docs-drift` concern either way — `ROADMAP.md` isn't in
MODE 1's current-truth-doc scope (`README.md`/`docs/`/`architecture/`/
`ai-docs/`).

## `query relations` doc-content-surfacing claim — independently checked

Read (not grepped-and-trusted) every `query relations` description in the
four current-truth doc locations:

- `README.md:110-117` ("Spec-doc relationship detection ... mechanically
  linked to the vendors and Skills they mention — no AI call ... for any
  relationship that mention-detection proves real, usage-driven AI
  enrichment can add a one- or two-sentence summary of *how* the two
  relate").
- `ai-docs/README.md:73-74` (example-prompts table: "Does anything in
  this repo mention `typer`?" / "How does `architecture/overview.md`
  relate to my dependencies?").
- `docs/cli-reference.md:158-183` (full flag reference: "what it
  mechanically mentions," "which spec docs mechanically mention it").
- `architecture/overview.md:856, 1433-1444, 1564` ("mechanically
  mentions," "mechanically mention," "prints what it mechanically
  mentions").

Every one of these is already scoped to *mention-detection status*, never
to *surfacing a doc's subject-matter content*. None overclaims.

Cross-checked this against the actual mechanism in
`src/codecompass/doc_mapping.py::build_doc_relations_edges` (word-boundary
regex match of vendor/artifact *names* against doc text —
`re.search(rf"\b{re.escape(name)}\b", text)`) and
`src/codecompass/graph.py`'s `doc_relations_edges` table/query functions.
The code matches the docs' "mechanically mentions" framing exactly: it is
literal name-mention detection with no content extraction or summarization
step beyond the separate, explicitly-gated AI-enrichment `ai_summary`
field (which the docs already describe as a distinct, opt-in step). No
current-truth doc needed a change as a result of Phase 51's finding that
0-tracked-vendor projects get a structural `(none)` ceiling — that's a
property of Ledgerkit's dependency graph interacting with an
already-accurately-described mechanism, not a new or newly-false claim
about the mechanism itself.

## Content spot-check of the new sections

Read the new "Phase 51 re-run" sections in full (`00-baseline.md`,
`01-query-semantics.md`) and the new "GATE DC" section in `findings.md`.
Spot-verified two of their technical claims directly against source
rather than trusting the write-up:

- Claim: `_DEFAULT_GLOBS` in `src/codecompass/spec_docs.py` now includes
  `"dev-docs/**/*.md"` — confirmed at `spec_docs.py:35`.
- Claim: `doc_relations_edges` construction is pure literal name-mention
  matching with no content representation — confirmed against
  `doc_mapping.py::build_doc_relations_edges`'s docstring and
  implementation.

Both check out. The PASS-WITH-GAPS / LOW-not-negative verdicts and the
"structurally cannot move higher with 0 tracked vendors" framing are
consistent with what the code actually does.

## Scope note

Checked: the full working-tree diff (all 7 modified/untracked files),
the append-only claim on all 5 named files, all four current-truth doc
locations' `query relations` prose, and the underlying mechanism in
`doc_mapping.py`/`graph.py`. Deliberately not re-litigated: Phase 51's
overall GATE DC strategic conclusion (that's a lead/retro-level call, not
a docs-drift question), and the `planning/ROADMAP.md`/plan-file "Status:
planned" vs. "phase already executed" wording mismatch noticed in
passing — that's a process/DoD-sequencing observation for the lead, not
a current-truth-doc (README/docs/architecture/ai-docs) drift finding, so
it's out of this audit's scope.
