# Legacy reconciliation: first-party-source-symbols

Reconciles the fresh clean-room draft
(`planning/knowledge/first-party-source-symbols/draft.md`, built solely
from `snapshots/snapshot-v2.toml`'s 8 cited claims) against the
already-published, real legacy architecture documentation on this exact
topic:

- `architecture/overview.md`, "## First-party source awareness
  (`codecompass.source_symbols`)"
- `architecture/context-graph-schema.md`, "## First-party source tables
  (Phase 77)" plus the `source_files`/`symbols` schema-table rows and the
  `_migrate_source_files_columns` mention
- `architecture/module-map.md`'s `source_symbols.py` entry

Per this role's charter, the draft was read only after being committed;
nothing below retroactively reshaped it.

## Decision: merge, not a new page

The fresh content is folded directly into the two existing
`architecture/` pages that already own this topic
(`overview.md`/`context-graph-schema.md`), not split into a standalone
page. Rationale: every other Phase-76/77-era subsystem (Git topology,
vendor schema) documents its full definitions/invariants/limitations
inline in these same two files at comparable length and detail; the
draft's own "definitions / invariants / supporting contract / known
limitations" structure maps directly onto material these two pages
already carry in the same order, and the *only* content the draft adds
that the existing pages didn't already have at all is the two Known
Limitations claims (CL-FPSS-007, CL-FPSS-008) — not enough net-new
material to justify a third architecture page plus its own cross-links,
and `module-map.md`'s one-paragraph module entry needed no change at
all.

## Classification of existing legacy claims

| Legacy claim (location) | Classification | Disposition |
|---|---|---|
| `core.Ecosystem` can't distinguish JS/TS; `source_symbols.Language` exists for that reason (`overview.md`, "A first-party *language*...") | `supported` | Unchanged — matches CL-FPSS-001 exactly, including the "NPM collapses both" detail. |
| Implementation-scope vs. API-surface-scope framing; `exposure` as a non-filtering property (`overview.md`, "Implementation scope, not API-surface scope.") | `supported` | Unchanged — matches CL-FPSS-002. Left at its existing level of generality (no per-language example rows added); CL-FPSS-002's own worked examples (`pub(crate)`, leading-underscore, etc.) are already present near-identically in `context-graph-schema.md`'s `source_symbols.exposure` closed-set paragraph, so no duplication was added. |
| Occurrence-based `(source_file, name, kind, line)` identity; `line NOT NULL`; overload live-verification (`overview.md` + `context-graph-schema.md` `source_symbols` table row) | `supported` | Unchanged — matches CL-FPSS-004 exactly, including the "no row emitted when location can't be determined" detail. |
| Explicit extraction-outcome model: `indexed`/`indexed_partial`/`unsupported`/`parse_error`/`unreadable`, modeled on `git_topology.RepositoryTopology` (`overview.md` + `context-graph-schema.md` closed-set paragraph) | `supported` | Unchanged in substance (matches CL-FPSS-003) — **but the phrase "never implied to be as complete as a real parser" was a general gesture at a fidelity gap with no specifics**, which is the documentation-verification gap called out below. Fixed, not merely flagged (see next section). |
| Two-level uncertainty: whole-project `meta.source_index_version` (present/absent) vs. per-file `symbol_index_status`, modeled on `git_topology_status`'s own precedent (`overview.md` + `context-graph-schema.md`) | `supported` | Unchanged — matches CL-FPSS-005's confirmed-implementation half exactly (unconditional write, including zero-first-party-files case; CLI gates on key absence). |
| `_migrate_source_files_columns`: four nullable columns, `ALTER TABLE ADD COLUMN`, gated by introspection, never drops `source_files` (`context-graph-schema.md` migrations section + `source_files` schema-table row) | `supported` | Unchanged — matches CL-FPSS-006 exactly, including the "identical column definitions on fresh vs. migrated database" and "confirmed by a passing test suite, not just asserted" framing. |
| CLI surface (`query source`, `query source-symbol`, read-only, never invokes a rebuild) (`overview.md`) | `supported` | Unchanged — no claim in the snapshot touches the CLI surface directly; nothing contradicts it. |

No legacy claim was found `stale_or_contradicted`, `useful_example`
(as a standalone illustration needing re-grounding), or `obsolete` — the
existing prose was already accurate everywhere it made a claim at all;
its only defect was *omission* (see below), not error.

## `rationale_requiring_verification` flag (not a doc fix — a follow-up)

CL-FPSS-005's own open question is carried forward, unchanged, as a
`context-researcher` follow-up candidate: whether
`meta.git_topology_status` (the precedent `source_index_version`'s
two-level design is explicitly modeled on) actually behaves the way its
own design assumes has never itself been checked under this or any prior
topic's research. This is not a claim inside the first-party-source-symbols
legacy docs to fix — nothing in `overview.md`/`context-graph-schema.md`
asserts `git_topology_status` has been verified beyond its own Phase 76
DoD — but it's a real, unresolved gap worth flagging for whoever next
touches the Git-topology knowledge-base topic.

## Documentation-verification gap: fixed, not just noted

`context-graph-schema.md`'s "First-party source tables" section and
`overview.md`'s matching subsection both previously gestured at
`indexed_partial`'s fidelity limit only in general prose ("never implied
to be as complete as a real parser" / a bare cross-reference to
`decisions/0065`'s own general "a multi-line signature, an unusual
formatting style, or (rarely) a false match... can defeat them"
language). CL-FPSS-007 and CL-FPSS-008 supply the fresh, real, evidenced
content this gap needed and the existing docs did not have *at all*:

- **CL-FPSS-007** (evidence: `EV-FPSS-008/009/021/022`, live probes,
  `status: verified`) — the two real, reproducible `indexed_partial`
  false-positive shapes (a multi-line Rust raw-string literal whose
  interior line matches the anchored pattern; a plain `/* ... */` JS/TS
  block comment, not specially recognized the way `/**` JSDoc is) versus
  the two shapes that do **not** actually defeat the extractors despite
  looking like they should (multi-line parameter lists; single-line
  comments/strings). Both false positives are silent (status stays
  `indexed_partial`, diagnostic stays unset).
- **CL-FPSS-008** (evidence: `EV-FPSS-023`, real source read,
  `status: supported`) — two structural scope gaps neither `decisions/0065`
  nor the Phase 77 plan mention at all: Python extraction is top-level-only
  (no recursive descent into class/function bodies, so methods and nested
  functions are never emitted as their own rows), and a JS/TS `const`
  binding's `kind` is always recorded literally as `"const"` (never
  `"function"`), regardless of what it's bound to.

**Fixed directly in the published docs** (both real, evidenced,
`supported`/`verified` claims — safe to state as fact, not merely
flagged):

- `architecture/context-graph-schema.md` — added a new "### Known
  fidelity limitations of `indexed_partial` and Python extraction"
  subsection at the end of "First-party source tables (Phase 77)",
  spelling out all four CL-FPSS-007 shapes and both CL-FPSS-008 scope
  gaps, and softened the `symbol_index_status` closed-set paragraph's own
  "never implied to be as complete as a real parser" aside into a pointer
  at the new subsection.
- `architecture/overview.md` — the "Explicit extraction-outcome model"
  paragraph no longer carries the bare "never implied to be as complete
  as a real parser" gesture; it now names the fidelity limits as
  "specific and reproducible, not a diffuse 'unusual formatting' risk"
  and cross-references `context-graph-schema.md`'s new subsection for the
  concrete shapes.
- `architecture/module-map.md` — no change; its one-paragraph
  `source_symbols.py` entry makes no fidelity claim to correct.

## Verification

`python scripts/check_user_docs.py --strict` passes after these edits
(internal links, ADR cross-references, fenced-example validity all
clean).
