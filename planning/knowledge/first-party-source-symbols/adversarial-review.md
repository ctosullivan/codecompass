# Adversarial review: `first-party-source-symbols` (Phase 79 clean-room draft)

Reviewer: domain-skeptic. Scope: 7 Claims (`CL-FPSS-001`–`007`) and their
supporting Observation/Evidence/Derivation records, produced by a
`context-researcher` dispatch working from a curated, isolated export
(`decisions/0065`, the Phase-77 plan, `source_symbols.py`, a curated
`graph_schema_fragment.py`, and the real test suite). Unlike that
dispatch, I have full repository access and used it: every finding below
was checked against the real `src/codecompass/` and `tests/` files, not
against the corpus's own citations of them.

Method: for each of the five things flagged for attention, I read the
real, uncurated source directly, and where executable, ran it (real
pytest runs against the real, unmodified modules; a fresh ad hoc probe
script against the real `source_symbols.py`). No claim's `statement` was
edited. Nine new Observation records (`OBS-FPSS-014`–`019`... actually
14–019) and six new Evidence records (`EV-FPSS-016`–`021`) were appended
to this directory, each citing the real file/line and the exact command
run. No Claim, Derivation, or Decision record was written by me.

## 1. `CL-FPSS-001` — `Language` vs `core.Ecosystem`

**Open question:** whether `core.Ecosystem`'s real definition matches
the ADR/plan's description (the dispatch never had `core.py`).

**Checked directly:** `src/codecompass/core.py:13-19` —
`class Ecosystem(StrEnum)` has exactly four members: `NPM`, `PYTHON`,
`CARGO`, `HASKELL`. `NPM` is indeed the single value covering both
JavaScript and TypeScript — there is no separate JS/TS split anywhere in
`core.py`. `source_symbols.py` contains no import of, or reference to,
`core.Ecosystem`, confirmed by grep.

**Resolution:** the claim's description of `core.Ecosystem` is accurate.
The open question is **closed** — not by inference from the ADR's own
prose (which is all the original dispatch had), but by direct
inspection of the real module. New evidence: `OBS-FPSS-014`,
`EV-FPSS-016`.

**Recommendation:** `CL-FPSS-001`'s `evidence_support_state` can move
from `partially_supported` to `supported`, and its open question can be
removed/closed (the one substantive gap it named — "core.Ecosystem's own
real current definition... could not be independently verified" — no
longer holds). I did not find a basis for `status: verified` here: this
is a definitional/naming claim, not a rule whose correctness depends on
anything beyond "the two enums have the values they're said to have,"
so `supported` is the right ceiling, not a materially higher bar.

## 2. `CL-FPSS-004` — occurrence-based symbol identity, and the
`SourceSymbolRow` field-list discrepancy

**Open question:** whether `graph_schema_fragment.py`'s apparently
incomplete 3-field `SourceSymbolRow` (flagged in `EV-FPSS-013`) reflects
the real `graph.py`, and whether the occurrence-based-identity claim
holds against the real schema.

**Checked directly:** `src/codecompass/graph.py:327-342`. The real
`SourceSymbolRow` has **six** fields: `source_file_path: str, name: str,
kind: str, line: int, purpose: str | None = None, exposure: str | None =
None` — matching its own docstring ("keyed by (source_file_path, name,
kind, line)... line is never None") exactly, and matching what
`_sync_source_symbols`'s real body (`graph.py:1207-1253`) actually reads
(`s.line`, `s.purpose`, `s.exposure` as real attributes). The `CREATE
TABLE source_symbols` statement (`graph.py:95-109`) declares `line
INTEGER NOT NULL` and `UNIQUE(source_file_id, name, kind, line)` exactly
as the claim states.

**Resolution:** `graph_schema_fragment.py`'s 3-field dataclass body was a
curation/transcription artifact in the export given to the original
dispatch — not a real property of `graph.py`, and not (as the dispatch
correctly refused to assume) something that should have been silently
smoothed over without checking. The open question is **closed**: the
4-field-key reading the dispatch inferred from indirect evidence (schema
constraint + function body) is now directly confirmed against the real
dataclass itself. New evidence: `OBS-FPSS-015`, `EV-FPSS-017`.

**Recommendation:** `CL-FPSS-004`'s `evidence_support_state` can move
from `partially_supported` to `supported`; its open question can be
closed. The `contradicting_evidence: ["EV-FPSS-013"]` entry should stay
on the record as history (it documents a real discrepancy the dispatch
correctly caught in the material it had), but a note should be added
(or `EV-FPSS-017` cited alongside it) making clear the discrepancy was
export-local and does not survive contact with the real `graph.py`. I
did not find grounds for `status: verified` — this is an invariant claim
about a design rationale ("why line is part of the key"), and while the
mechanical schema/dataclass facts are now fully confirmed, "verified"
per this role's charter requires a claim-specific check that the
*rationale* itself is sound, not just that the code matches the
description. The mechanical facts are about as solid as they get, though
— this is a strong `supported`.

## 3. `CL-FPSS-005` — `meta.source_index_version`

**Open question:** the claim was graded `unsupported`/`proposed`
specifically because the dispatch had no code for the write path
(`rebuild_deterministic`, via `sync.py`) or read/gate path (`cli.py`).

**Checked directly:**
- Write path: `sync.py:417-438` — `rebuild_project_graph` calls
  `rebuild_deterministic(..., source_index_version="1")`
  **unconditionally** — the literal string `"1"` is passed on every real
  call, never conditioned on `source_file_rows`/`source_symbol_rows`
  being non-empty. `graph.py:1071-1076` — `rebuild_deterministic` then
  runs `INSERT INTO meta (key, value) VALUES ('source_index_version', ?)
  ON CONFLICT(key) DO UPDATE...` whenever the argument is not `None`.
  The function's own docstring (`graph.py:998-1010`) states exactly the
  claim: "every real production call... always supplies a real value,
  regardless of whether any first-party source files were actually
  found... its absence is what `cli.py::query_source`/
  `query_source_symbol` treat as 'first-party source has never been
  indexed'."
- Read/gate path: `cli.py:1094` (`query_source`) and `cli.py:1157`
  (the equivalent `query_source_symbol` command) both guard with `if
  conn is None or graph.get_meta(conn, "source_index_version") is
  None:` before ever reading `source_files`/`source_symbols`, rendering
  an explicit "not indexed yet" message instead of a bare "not found."
  Both commands are read-only — no rebuild is triggered by either.

**Resolution:** this is not merely "documented intent" any more — the
mechanism exists, in exactly the shape decisions/0065 point 7 describes,
including the specific detail (written even when zero first-party files
are found) that most needed checking. New evidence: `OBS-FPSS-016`,
`EV-FPSS-018`.

**Recommendation:** this is the one Claim where I think an upgrade is
warranted beyond `supported`. `CL-FPSS-005` should move from
`basis: proposed_policy` / `evidence_support_state: unsupported` /
`status: proposed` to `basis: observed_behaviour` /
`evidence_support_state: supported` / `status: supported` — its own
open questions about the write/read path being absent from the export
are now closed with real code evidence. I stop short of recommending
`status: verified`: the claim's remaining sub-clause about
`meta.git_topology_status` being "the precedent this design is
explicitly modeled on" and behaving analogously is still unverified
(`git_topology.py` was not read as part of this pass — out of the five
specific things I was asked to check, this sub-clause wasn't one of
them, and I did not want to overreach into territory outside the scoped
check). If `context-researcher` or a future pass confirms
`git_topology.py`'s own absence-means-never-synced behavior directly,
that specific sub-clause could then support `verified`; until then,
`supported` is the honest ceiling.

## 4. `CL-FPSS-006` — nullable-everywhere migration contract and the
ADR's self-citation

**Open question:** the ADR's own "verified directly (`test_graph.py`)"
self-citation — unchecked because `tests/test_graph.py` wasn't in the
export.

**Checked directly:** `tests/test_graph.py:2073-2099` —
`test_fresh_and_upgraded_source_files_schema_are_identical` genuinely
exists, and its own docstring states exactly the fact the ADR cites:
"`PRAGMA table_info(source_files)` must return identical column
names/types/nullability whether the database was created fresh or
migrated from a pre-Phase-77 shape." It builds a fresh database via
`open_graph`, builds a second database seeded with a bare pre-Phase-77
`source_files(id, path)` table, opens it via `open_graph` (triggering
migration), and asserts `_column_shape(fresh_conn) ==
_column_shape(upgraded_conn)` where `_column_shape` returns `(name,
type, notnull)` triples. I ran it, along with
`test_migrate_source_files_columns_preserves_uses_edges_and_enrichment`
(the ADR's other cited safety property — no cascade-delete of
`uses_edges`/enrichment on migration): **both passed** against the real,
unmodified codebase.

**Resolution:** the ADR's self-citation is accurate, not merely
asserted. The open question is **closed**. New evidence:
`OBS-FPSS-017`, `EV-FPSS-019`.

**Recommendation:** `CL-FPSS-006`'s `evidence_support_state` can move
from `partially_supported` to `supported`, open question closed. This is
a case where I did run the exact claim-specific test named in the
citation and confirmed it passes against the real, current code —
per this role's charter that is closer to `status: verified` territory
than most findings here, since the claim's own residual gap ("the ADR's
self-report... could not be independently confirmed") is precisely what
a real, specific, primary-evidence check (not "it looks reasonable")
closes. I recommend `status: verified` for `CL-FPSS-006` specifically —
both the schema/migration code itself and the cited test's existence,
content, and pass status are now independently confirmed against
primary evidence, with no remaining gap the claim itself names.

## 5. `CL-FPSS-007` (extractor blind spots) and `CL-FPSS-004`'s
`EV-FPSS-013` counterexample — sanity-checked against the real
repository

**`EV-FPSS-013`:** addressed under item 2 above — resolved as an
export-local curation artifact, not a real inconsistency in `graph.py`.

**`CL-FPSS-007`:** ran a fresh probe script directly against the real,
unmodified `_extract_rust_source_symbols`/`_extract_js_family_source_symbols`
(`src/codecompass/source_symbols.py`), independent of the dispatch's own
sandboxed probes:

- (a) Rust multi-line raw string (`r#"...pub fn embedded_in_string()
  {}..."#`) → real, silent false positive: `embedded_in_string` at line
  2, status stayed `INDEXED_PARTIAL`, `diagnostic` stayed `None`.
  **Confirms** the claim.
- (b) genuinely multi-line Rust function signature → exactly one
  correct row, no false positive or omission. **Confirms** the
  claim's counterexample.
- (c) Rust `//` comment containing decl-like text → correctly excluded
  (only the real declaration produced a row). **Confirms** the
  counterexample.
- (d) JS/TS plain `/* ... */` block comment (not JSDoc `/**`)
  containing a commented-out `export function` → real, silent false
  positive: `commented_out` produced alongside the genuine declaration.
  **Confirms** the claim.
- (e) JS/TS single-line string literal containing decl-like text →
  correctly excluded. **Confirms** the counterexample.

All five outcomes match `CL-FPSS-007`'s stated claim exactly, now
against the real production module. New evidence: `OBS-FPSS-019`,
`EV-FPSS-021`. (I also re-ran the real `tests/test_source_symbols.py`
— all 17 tests pass against the real, unmodified module with no
stubbing needed, corroborating `CL-FPSS-002`/`CL-FPSS-003` beyond the
dispatch's own sandboxed run: `OBS-FPSS-018`, `EV-FPSS-020`. I also
independently confirmed, by reading `extract_source_symbols_for_file`
directly, that the dispatch table exactly matches `CL-FPSS-003`'s
statement: Python dispatches to a real `ast.parse`-based extractor that
can return `INDEXED`/`PARSE_ERROR`/`UNREADABLE` but never
`INDEXED_PARTIAL`; Rust/JS/TS dispatch to line-scan extractors that can
return `INDEXED_PARTIAL`/`UNREADABLE` but never `PARSE_ERROR`; any other
language returns `UNSUPPORTED` unconditionally without the file ever
being opened — `source_symbols.py:172-199`.)

**Recommendation:** `CL-FPSS-007` needs no status change — it was
already `status: supported` with `evidence_support_state: supported`,
and this pass adds confirming (not contradicting) primary evidence, plus
resolves nothing that was actually in doubt. Its own open question
("whether these two specific false-positive shapes... are the ones
decisions/0065's own prose intended... could not be determined") is a
genuine, unresolvable-by-code-reading ambiguity about *authorial intent*
of prior prose, not a researchable fact — it should stay open, not be
forced closed. I looked for a third or fourth false-positive shape
beyond the two named (e.g., nested block comments, a Rust doc-comment
`///` immediately followed by a raw string, an escaped-quote edge case
in a JS template literal) and did not find one that changes the
picture; I'm not escalating this, since it isn't a product/domain
ambiguity for the user to decide — it's a "how thorough was the
original prose" question with no operational consequence either way
(the coarseness itself, not its exact enumeration, is the actionable
fact).

## Claims not specifically flagged (`CL-FPSS-002`, `CL-FPSS-003`)

Both were already `status: supported` with no open questions. I
independently re-ran the real `tests/test_source_symbols.py` against
the real, unmodified module (see above) and separately read
`extract_source_symbols_for_file`'s dispatch logic directly — both
confirm the claims exactly. No changes recommended; no new
contradictions or missing edge cases found. I looked specifically for a
real extractor call that could produce `exposure='unknown'` (grepped the
whole module) — the string appears exactly once, in a comment
documenting the vocabulary, never in executable code — confirming
`CL-FPSS-002`'s "never produced by any of the three real extractors"
claim directly rather than trusting the dispatch's own probe count.

## Internal-contradiction and missing-edge-case sweep

Beyond the five flagged items, I checked for:
- **Claim vs. claim conflicts** across the seven Claims: none found —
  `CL-FPSS-001` (Language vocabulary), `002` (exposure per-language),
  `003` (status per-language), `004` (identity key), `005` (index
  version marker), `006` (migration nullability), `007` (coarse
  extractor blind spots) each name a disjoint slice of the subsystem and
  none states anything the others contradict.
- **A single record's own sections against each other** (per this
  role's charter, e.g. the Phase 63D `provenance.md` precedent): checked
  each Claim's `statement` against its own `examples`/`counterexamples`/
  `open_questions` — no internal contradiction found in any of the
  seven.
- **Missing edge cases a stated "X is always Y" would predict**: for
  `CL-FPSS-002`'s "never the full five values by any one language,"
  checked Rust's three `pub(...)` forms individually
  (`pub(crate)`/`pub(super)`/`pub(in path)`) plus `pub(self)`
  (mentioned in the regex but not in the claim's own examples) — the
  regex (`source_symbols.py:99-102`) does include `pub(self)` in its
  alternation, and it maps to `restricted` exactly like the other three
  `pub(...)` forms via the `else: exposure = "restricted"` branch — this
  is consistent with, not a counterexample to, `CL-FPSS-002`'s claim
  (`pub(self)` is simply an unenumerated fourth example of the same
  `restricted` bucket, not a new value), so no finding here worth
  escalating.

## Escalations

**None.** Every item flagged for attention, and every additional check
I ran on my own initiative, resolved cleanly against primary evidence
(real source, real tests, a real probe run) — no genuine, unresolved
product/domain ambiguity requiring the user's own decision was found.
The one open question I deliberately left open (`CL-FPSS-007`'s "did the
ADR's prose intend exactly these two shapes") is not escalation-worthy:
it is a question about historical authorial intent with no operational
consequence, not a decision the user needs to make.

## Summary of recommended status/state changes (not applied by me)

| Claim | Current | Recommended | Basis |
|---|---|---|---|
| `CL-FPSS-001` | `evidence_support_state: partially_supported`, open question present | `evidence_support_state: supported`, open question closed | `core.py` read directly (`EV-FPSS-016`) |
| `CL-FPSS-004` | `evidence_support_state: partially_supported`, open question present | `evidence_support_state: supported`, open question closed (note `EV-FPSS-013` as export-local, resolved by `EV-FPSS-017`) | `graph.py` read directly (`EV-FPSS-017`) |
| `CL-FPSS-005` | `basis: proposed_policy`, `evidence_support_state: unsupported`, `status: proposed` | `basis: observed_behaviour`, `evidence_support_state: supported`, `status: supported` | `sync.py`/`graph.py`/`cli.py` read directly (`EV-FPSS-018`) |
| `CL-FPSS-006` | `evidence_support_state: partially_supported`, open question present | `evidence_support_state: supported`, open question closed, **`status: verified`** | `tests/test_graph.py` read and run directly, cited test confirmed accurate (`EV-FPSS-019`) |
| `CL-FPSS-002`, `003`, `007` | `supported` | no change | corroborating evidence only, nothing was in doubt |

New records appended (never edited an existing Claim):
`OBS-FPSS-014` through `OBS-FPSS-019`, `EV-FPSS-016` through
`EV-FPSS-021`. No Claim, Derivation, or Decision record was written.
