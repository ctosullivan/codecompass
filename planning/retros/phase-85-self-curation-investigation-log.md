# Phase 85 self-curation investigation log

Append-only, like `promoted.md`/`_audit-phase-84.md` — never edited to
change a past disposition. Full design: `planning/phase-85-self-
curation-knowledge-quality-validation.md` §4.E. **Not a canonical
knowledge-record kind** — records a candidate finding about
CodeCompass's own implementation that `context-researcher`'s self-
curation investigation mode (`.claude/agents/context-researcher.md`)
classified as outcome 2 (duplicate/already-known), 3 (falsified), or 4
(insufficiently supported), per the plan's own five-outcome procedure
(§4.E). Outcome 1 (accepted new knowledge) and outcome 5 (genuine
contradictory knowledge) are canonical `CL-`/`DE-`/`EV-`/`OBS-` records
under `planning/knowledge/<slug>/` instead — they never appear here.

Each entry is written by `knowledge-curator`, within its own write
boundary (`.claude/agents/knowledge-curator.md`'s "Self-curation
independent adjudication" mode), after independently reproducing the
candidate's own cited evidence — never written by `context-researcher`
itself, and never a canonical record.

New entries go at the bottom, oldest first, so the log reads as a plain
history. Fields per entry:

| Field | Required | Notes |
|---|---|---|
| `id` | yes | `SCI-NNN`, stable, never reused |
| `hypothesis` | yes | the specific, falsifiable question investigated, in the researcher's own original words |
| `investigation_scope` | yes | what was examined (files, functions, constructs tried) and the CodeCompass `repository_revision` investigated against |
| `evidence` | yes | every command run / file:line read / probe constructed, with its real, reproduced output |
| `reviewer` | yes | who performed the independent adjudication reproduction (`knowledge-curator` directly, or the lead at its explicit direction, for executable evidence) |
| `disposition` | yes | one of: `duplicate` / `falsified` / `insufficient` |
| `reason` | yes | why this disposition, in one paragraph |
| `related_knowledge` | no | any existing `CL-`/`REQ-`/`EV-` id this investigation checked against or bears on |

---

## SCI-001

- **id**: SCI-001
- **hypothesis**: A Rust item gated behind a `#[cfg(test)]` attribute
  (an attribute line immediately preceding the `fn`/`mod` keyword, on
  its own physical line, same general "something precedes the item
  keyword on a separate line" shape as CL-FPSS-009(e)'s split-modifier
  defect) causes `_RUST_ITEM_RE` to misclassify or miss the following
  declaration, because the regex only inspects a single stripped line's
  own start.
- **investigation_scope**: `_extract_rust_source_symbols`
  (`src/codecompass/source_symbols.py`, line 221) called directly against
  a disposable fixture containing a `#[cfg(test)]`-gated top-level `fn`
  (`helper_test_only`) and a `#[cfg(test)]`-gated nested item
  (`inner_test`), neither carrying a `pub` modifier. CodeCompass
  `repository_revision`: `20a274c`.
- **evidence**: Lead-executed probe (method: `targeted_probe`,
  Execution bucket, run by the lead at `knowledge-curator`'s direction
  per `.claude/agents/knowledge-curator.md`'s Hard Rules — `knowledge-
  curator` has no `Bash`), real reported output: `indexed_partial None
  (SourceSymbol(name='helper_test_only', kind='fn', line=2, purpose=None,
  exposure='internal'), SourceSymbol(name='inner_test', kind='fn',
  line=8, purpose=None, exposure='internal'))`. Independently
  corroborated by `knowledge-curator` itself via direct source reading
  (no execution needed for this part): `_RUST_ITEM_RE`
  (`src/codecompass/source_symbols.py` lines 99-102) requires
  `fn|struct|enum|trait` to appear on the *same* stripped line as any
  `pub(...)` prefix it recognizes; it has no concept of `#[...]`
  attribute lines at all. A `#[cfg(test)]` line simply fails to match
  the regex (starts with `#`, not `pub`/`fn`/`struct`/`enum`/`trait`)
  and is silently skipped (`_extract_rust_source_symbols`'s loop, lines
  231-251), exactly like any other non-matching line — doc-comment
  handling (`///`) is the only special-cased prefix. The following real
  `fn` line is then matched on its own, with `modifier=None` since
  neither fixture function carries `pub`, correctly yielding
  `exposure='internal'` for both — the classification is correct
  for this input, not a defect.
- **reviewer**: `knowledge-curator` (own direct source reading;
  probe execution delegated to the lead per the Execution-bucket
  convention, output incorporated as above)
- **disposition**: falsified
- **reason**: The hypothesis predicted a misclassification analogous to
  CL-FPSS-009(e)'s split-modifier defect, but `#[cfg(test)]` (and any
  other Rust attribute line) is not a visibility/export keyword the
  regex ever attempts to capture in the first place — it is simply an
  unrecognized line that falls through unmatched, the same as a blank
  line or any other non-item text. Both fixture functions, having no
  `pub` modifier, are correctly classified `internal`; no row is
  misclassified or missing. Direct re-reading of `_RUST_ITEM_RE` and the
  extraction loop confirms this is not merely the probe's own report but
  a structural fact about the regex's scope — it was never going to
  inspect an attribute line regardless of fixture content. This
  construct was pre-registered in `DE-FPSS-009`'s own dispatch scope as
  hypothesis (1) and explicitly reported there as not reproducing any
  defect; this entry is the investigation-log record of that
  falsification, per the deferred-write mode's own rule that outcome 3
  commits nothing under `planning/knowledge/`. Not tried: a `#[cfg(test)]`-gated
  item that also carries `pub` — left as an explicitly open question,
  not asserted to behave identically.
- **related_knowledge**: CL-FPSS-009, DE-FPSS-009, OBS-FPSS-022

## SCI-002

- **id**: SCI-002
- **hypothesis**: A TypeScript decorator-prefixed declaration (a
  `@Decorator(...)` line immediately preceding `export class ...`, on
  its own physical line) causes `_JS_FAMILY_ITEM_RE` to misclassify or
  miss the following declaration, same general shape as CL-FPSS-009(e)'s
  split-export defect, because the regex only inspects a single
  stripped line's own start.
- **investigation_scope**: `_extract_js_family_source_symbols`
  (`src/codecompass/source_symbols.py`, line 257) called directly
  against a disposable fixture containing a decorator line immediately
  preceding `export class Foo { ... }`. CodeCompass
  `repository_revision`: `20a274c`.
- **evidence**: Lead-executed probe (method: `targeted_probe`, Execution
  bucket, run by the lead at `knowledge-curator`'s direction), real
  reported output: `indexed_partial None (SourceSymbol(name='Foo',
  kind='class', line=5, purpose=None, exposure='public'),)`.
  Independently corroborated by `knowledge-curator` via direct source
  reading: `_JS_FAMILY_ITEM_RE` (lines 109-112) requires
  `function|class|interface|const|type|enum` on the same stripped line
  as any `export`/`default`/`declare` prefix it recognizes, and has no
  concept of a decorator line. A `@Decorator(...)` line does not start
  with `/**`/`*` (so it is not treated as doc text) and does not match
  `_JS_FAMILY_ITEM_RE` (starts with `@`), so it falls through unmatched
  — the loop (lines 267-290) resets `pending_doc` to `None` and moves
  on, the same as for any other unrecognized line. The following
  `export class Foo` line is then matched on its own, `exported="export
  "`, correctly yielding `exposure='public'` — the classification is
  correct for this input, not a defect (the decorator's own argument
  text is simply never captured as symbol metadata, a separate,
  un-investigated observation not covered by this hypothesis).
- **reviewer**: `knowledge-curator` (own direct source reading; probe
  execution delegated to the lead per the Execution-bucket convention,
  output incorporated as above)
- **disposition**: falsified
- **reason**: The hypothesis predicted a misclassification analogous to
  CL-FPSS-009(e)'s split-export defect, but a decorator line is not an
  `export`/`default`/`declare` keyword the regex ever attempts to
  capture — it is an unrecognized line that falls through unmatched,
  exactly as for any other non-item text. `Foo` is correctly classified
  `public`, matching its genuine `export class` declaration; no row is
  misclassified or missing. Direct re-reading of `_JS_FAMILY_ITEM_RE`
  and the extraction loop confirms this is a structural fact about the
  regex's scope, not an artefact of this one fixture. This construct was
  pre-registered in `DE-FPSS-009`'s own dispatch scope as hypothesis (3)
  and explicitly reported there as not reproducing any defect; this
  entry is the investigation-log record of that falsification, per the
  deferred-write mode's own rule that outcome 3 commits nothing under
  `planning/knowledge/`. Not tried: a decorator whose own argument text
  itself contains a declaration-shaped substring — left as an explicitly
  open question, not asserted to behave identically.
- **related_knowledge**: CL-FPSS-009, DE-FPSS-009, OBS-FPSS-023
