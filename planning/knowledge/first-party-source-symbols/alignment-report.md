# Alignment report: first-party-source-symbols@v1 vs. implementation-reconstruction.md

**Mode:** comparison (per `decisions/0066`), not adversarial review. Frozen
snapshot: `snapshots/snapshot-v1.toml` (repository_revision_at_freeze
`98c3fba`). As-built artifact: `implementation-reconstruction.md`, produced
with zero access to the snapshot, the ADR, or the phase plan — only
`src/codecompass/source_symbols.py`, `src/codecompass/graph_schema_fragment.py`,
`tests/test_source_symbols.py`, and `pyproject.toml`.

**Hard rule observed throughout:** an `aligned` finding never by itself
promotes a Claim's own `status` to `verified`. Where alignment here is
consistent with a status the adversarial review already set independently
(e.g. CL-FPSS-006's `verified`), that is noted as a fact about the existing
record, not as something this pass causes or justifies on its own.

---

## Per-claim classification

### CL-FPSS-001 — `Language`, a new five-value concept distinct from `core.Ecosystem`

**Classification: `aligned`** (for the part the reconstruction's evidence
base can reach; the `core.Ecosystem` comparison itself is outside that
evidence base, not contradicted by it).

The reconstruction independently confirms, from `source_symbols.py` alone:
a `Language` `StrEnum` with exactly five members (`PYTHON`, `RUST`,
`JAVASCRIPT`, `TYPESCRIPT`, `HASKELL`), defined in `source_symbols.py`
(§1), and its Dependencies section (§4) lists every import of that module
— `ast`, `re`, `dataclasses`, `enum.StrEnum`, `pathlib.Path`,
`codecompass.filetree.iter_source_files`,
`codecompass.usage._PROJECT_PRUNE_DIR_NAMES` — with no `core.py` import at
all, independently corroborating "not imported... within this module."

The claim's other half — that `core.Ecosystem` itself collapses JS/TS to a
single NPM value — cannot be checked by the reconstruction, since
`core.py` was never part of its evidence base (explicitly not read, per
the reconstruction's own opening statement). This is not a conflict; it is
outside scope for that artifact. Separately, and prior to this dispatch,
`EV-FPSS-016`/`OBS-FPSS-014` already independently confirmed this exact
point by direct reading of `core.py` (`Ecosystem` has exactly four
members, NPM covering both JS and TS) — so the claim's full statement is
independently corroborated overall, just not by this comparison's own
artifact pair.

### CL-FPSS-002 — Five-value exposure classification, strict per-language disjoint subsets, `unknown` never produced

**Classification: `aligned`.**

The reconstruction's §5 and §8 independently describe, from source and
the 16 real tests: Python emits only `public`/`conventional_private`
(binary, from leading-underscore check); Rust emits `public` (bare `pub`),
`restricted` (any `pub(...)` form — reconstruction explicitly notes all
four modifier forms collapse to one value), or `internal` (no modifier);
JS/TS emit only `public` (export-prefixed) or `internal`. §9 explicitly
states: "`exposure: 'unknown'` is schema-legal but never produced ...
none of the three extractors ever assign it (or `None`)." This matches
CL-FPSS-002's statement of the claim, including its most specific
sub-claim, word for word in substance.

### CL-FPSS-003 — Five-state `SymbolIndexStatus`, `indexed` vs `indexed_partial` by technique fidelity, `parse_error` Python-only

**Classification: `aligned`**, with one genuine knowledge-base gap
surfaced alongside it (see "Gaps," item 3 below).

The reconstruction's §5 independently traces exactly this: Python's real
`ast.parse` path returns `INDEXED` even with zero symbols, `PARSE_ERROR`
on `SyntaxError`, `UNREADABLE` on read failure; Rust/JS/TS "always return
`INDEXED_PARTIAL` on a successful read (never `INDEXED` — that status is
Python-only in this code)... Neither has a `PARSE_ERROR` path at all";
Haskell "falls through to `UNSUPPORTED` ... without ever touching the
filesystem." This matches CL-FPSS-003's statement exactly, including the
"file is never even opened" detail for Haskell.

One nuance, not a conflict: the reconstruction also independently notes
(§9) that a suffix *absent from `_LANGUAGE_BY_SUFFIX` entirely* (e.g.
`.go`, `.java`) is filtered out even earlier, inside `discover_source_files`
itself, and never reaches `extract_source_symbols_for_file`'s `UNSUPPORTED`
branch at all — a distinct mechanism from Haskell's case, which CL-FPSS-003
does not state or contradict (it describes only the Haskell/UNSUPPORTED
case). I independently re-confirmed this distinction by direct source
read (`OBS-FPSS-021`, item 3) — see "Gaps" below.

### CL-FPSS-004 — Occurrence-based identity `(source_file_id, name, kind, line)`, motivated by overloading

**Classification: `aligned`.**

The reconstruction's §8 independently reports both overload tests exactly
as the claim's examples describe: three `def foo` declarations (two
`@overload` + one real) → three rows, three distinct lines; three
TS `function foo` signatures → three rows, three distinct lines. The
reconstruction adds a nuance that reinforces rather than contradicts the
claim: neither extractor is actually overload-*aware* — Python "simply
records every top-level `FunctionDef` node regardless of decorators" and
the TS case is "regex line matching, not signature-aware overload
resolution." This is consistent with CL-FPSS-004's own statement, which
never claims special-case overload detection — only that the
occurrence-based identity scheme is what *prevents* these three
independently-real declarations from colliding. If anything, the
reconstruction's finding that the extractors are overload-*agnostic*
strengthens the claim's own rationale: without line-based identity,
collision would be inevitable, not merely likely.

### CL-FPSS-005 — `meta.source_index_version`, absence-based signal, unconditional write, `cli.py` gate

**Classification: `insufficiently_verified`** (by this artifact pair
specifically — not a conflict, and not newly in doubt).

`sync.py`, `graph.py`'s `rebuild_deterministic`, and `cli.py` are entirely
outside the reconstruction's evidence base (only `source_symbols.py`,
`graph_schema_fragment.py`, `tests/test_source_symbols.py`, and
`pyproject.toml` were read for it), and the reconstruction text never
mentions `source_index_version` at all. This comparison genuinely cannot
classify CL-FPSS-005 as `aligned`, `partial`, or `conflicting` — the
reconstruction simply has no evidence reaching this claim's subject
matter. This is a scope gap in the artifact pair, not a defect in either
artifact: CL-FPSS-005 was already independently checked, separately from
this comparison, by `OBS-FPSS-016`/`EV-FPSS-018` (direct reads of
`sync.py:417-438`, `graph.py:1071-1076`, `cli.py:1094/1157`), which
confirmed it directly and is why its `status` is already `supported` (not
`verified` — the claim's own text is explicit that the write/read path
matches "documented intent," while treating full verification as resting
on that direct-code check, which stands independent of this comparison
pass).

### CL-FPSS-006 — `_migrate_source_files_columns`'s nullable-everywhere contract

**Classification: `aligned`**, for the code-structure portion; the
test-existence sub-claim is outside the reconstruction's scope (already
separately verified, `status: verified` pre-existing).

The reconstruction's §3 independently confirms, from `graph_schema_fragment.py`
directly: all four Phase-77 columns nullable with no default on both the
`CREATE TABLE` and the migration's `ALTER TABLE` statements; the migration
is gated by `PRAGMA table_info`, additive-only, "the code matches its own
stated rationale (protecting `uses_edges.source_file_id ON DELETE CASCADE`
from an accidental cascade-delete via table recreation)"; it "returns
early (no-op) if `source_files` doesn't exist yet at all." This matches
CL-FPSS-006's statement of the migration's mechanics precisely.

The reconstruction explicitly could not corroborate the claim's
"verified directly (`test_graph.py`)" sub-statement — its own §8 states
plainly that "No test in this export exercises `graph_schema_fragment.py`
at all ... a separate `test_graph.py` is referenced ... but that file is
not part of this export and was not read." That sub-claim was already
independently confirmed by the adversarial review (which did read and run
`test_graph.py`, per the claim's own text and its `verified` status) —
this comparison neither adds to nor detracts from that; it simply cannot
reach that specific sub-claim with this artifact pair.

### CL-FPSS-007 — `indexed_partial`'s "honest, coarse" fidelity boundary, four specific sub-shapes

**Classification: `insufficiently_verified` by the reconstruction alone**,
but **independently confirmed `aligned`** by a direct source-code check I
ran myself during this pass (`OBS-FPSS-020`/`EV-FPSS-022`).

The reconstruction's own description of the Rust/JS/TS limitation (§9) is
general — "a single anchored regex... any declaration whose keyword and
name don't appear together on one line... is silently not matched" — and
does not address the claim's four specific sub-shapes at all (raw-string
literals, plain block comments). It is silent, not contradictory, on (a)
multi-line parameter lists, (b) single-line comments/strings, (c) Rust
raw-string false positives, or (d) JS/TS plain-block-comment false
positives.

Because this was a researchable, code-level question, I read
`_extract_rust_source_symbols` and `_extract_js_family_source_symbols`
directly (source_symbols.py:221-293) rather than leave it as an open gap.
All four sub-claims check out exactly as CL-FPSS-007 states: neither
extractor tracks any "inside a raw string" or "inside a plain block
comment" state (Rust tracks only `///`-doc-line state; JS/TS tracks only
JSDoc `/** */` state), so both false-positive shapes are real and silent,
while both non-defeating shapes (multi-line signatures, single-line
comments/strings) are also confirmed correct, per `^`-anchored,
single-line matching. See `OBS-FPSS-020`/`EV-FPSS-022` for the full
line-by-line reasoning.

Per the hard rule governing this mode: this direct check is a genuine,
claim-specific verification, not a comparison-derived inference — but I
am not myself moving CL-FPSS-007's `status` to `verified` on that basis.
I recommend it as a candidate for the lead/context-researcher to formally
promote, citing `EV-FPSS-022`, if that is desired — this pass only
performs and records the check, not the promotion.

---

## Gaps: reconstruction findings no Claim covers

Per the task's explicit ask, all five limitations the reconstruction names
in its §9 were checked against the seven Claims:

1. **Haskell falls through to `UNSUPPORTED`** — covered by CL-FPSS-003
   directly (its own worked example). Not a gap.
2. **Python extraction is top-level-only** (no nested function/method
   symbols) — **a genuine gap.** No Claim states or qualifies this.
   Independently re-confirmed by direct source read: `_extract_python_source_symbols`
   walks only `ast.iter_child_nodes(tree)`, with no recursive descent into
   a class or function body anywhere in the function (`OBS-FPSS-021`,
   item 1). **Recommend:** a new Claim (or an amendment to CL-FPSS-004's
   scope note) stating this as a real, source-confirmed extraction-scope
   limitation.
3. **`exposure: 'unknown'` is schema-legal but never produced** —
   already covered by CL-FPSS-002 verbatim ("`unknown` is never produced
   by any of the three real extractors this module ships"). Not a gap.
4. **Rust/JS/TS have no `PARSE_ERROR` path** — already covered by
   CL-FPSS-003 verbatim ("parse_error is Python-specific ... since
   Rust/JS/TS have no real parse step to fail"). Not a gap.
5. **JS/TS `const`-arrow-function `kind` misclassification** (`kind`
   recorded as `"const"`, never `"function"`, since the regex only
   captures the leading keyword) — **a genuine gap.** No Claim mentions
   this. Independently re-confirmed by direct source read: `_JS_FAMILY_ITEM_RE`'s
   `kind` group is one of the literal keywords
   `function|class|interface|const|type|enum`, and
   `_extract_js_family_source_symbols` assigns `kind=kind` straight from
   the match with no right-hand-side inspection (`OBS-FPSS-021`, item 2).
   **Recommend:** a new Claim documenting this as a named fidelity
   limitation, in the same spirit as CL-FPSS-007's own boundary treatment.

A sixth, narrower nuance surfaced during verification of item 1/3 above
(not one of the task's five named items, but adjacent to CL-FPSS-003):
Haskell's `UNSUPPORTED`-via-fallthrough and a wholly-unrecognized suffix's
earlier invisibility inside `discover_source_files` are two distinct
mechanisms at two different pipeline stages (`OBS-FPSS-021`, item 3).
This supplements, but does not contradict, CL-FPSS-003. Lower priority —
offered as a possible refinement to that claim's own scope note rather
than a standalone claim.

---

## New records written this pass (Observation/Evidence only — no Claim, Derivation, or edit to any existing record)

- `OBS-FPSS-020` / `EV-FPSS-022` — direct source verification of
  CL-FPSS-007's four sub-claims (a)-(d), resolving what the reconstruction
  itself left silent.
- `OBS-FPSS-021` / `EV-FPSS-023` — direct source verification of two
  genuine knowledge-base gaps (Python top-level-only scope; JS/TS
  `const`-as-literal-kind) the reconstruction named and no existing Claim
  covers, plus the narrower Haskell-vs-unrecognized-suffix nuance.

No existing Claim, Derivation, Observation, or Evidence record was edited.
No `status` field was changed on any existing record.

---

## Summary table

| Claim | Classification | Notes |
|---|---|---|
| CL-FPSS-001 | aligned | `core.Ecosystem` half outside reconstruction's evidence base; separately confirmed pre-existing (`EV-FPSS-016`) |
| CL-FPSS-002 | aligned | exact match, including `unknown`-never-produced |
| CL-FPSS-003 | aligned | exact match; adjacent discovery-level nuance noted, not a conflict |
| CL-FPSS-004 | aligned | overload-agnostic mechanism reinforces, doesn't contradict, the claim |
| CL-FPSS-005 | insufficiently_verified | subject matter entirely outside reconstruction's evidence base; separately already confirmed elsewhere |
| CL-FPSS-006 | aligned | code-structure portion confirmed; test-existence sub-claim outside reconstruction's scope, separately already `verified` |
| CL-FPSS-007 | insufficiently_verified by reconstruction alone; aligned by a direct check I ran myself | see `OBS-FPSS-020`/`EV-FPSS-022`; promotion to `verified`, if wanted, is a separate action for the lead |

**Recommended new Claims** (for context-researcher/lead to draft — not
drafted by this role): (1) Python's top-level-only extraction scope; (2)
JS/TS `const`-as-literal-`kind` capture. Both are real, source-confirmed,
evidence-based limitations with no existing Claim coverage.
