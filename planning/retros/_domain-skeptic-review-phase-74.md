# Domain-skeptic review — Phase 74 freshness reconciliation (real behavior fix, not a citation restructure)

## Scope

The lead reports Phase 74 (`L-031` + `L-032`, plan:
`planning/phase-74-provenance-hardening.md`) landed two real `src/`
fixes closing gaps `docs/domain/`'s own approved corpus documents as
currently-open. Asked to independently verify five cited locations
against the current code — not the lead's summary — and, for any
genuinely stale claim, name the exact replacement text following this
corpus's own established "gap now closed" convention (distinct from
Phase 72's citation-restructure case).

## What I checked

- Read `src/codecompass/graph.py` in full (schema, both migration
  functions, `record_symbol_enrichment`), `src/codecompass/adapters/
  external_process.py` in full, `src/codecompass/adapters/haskell.py`
  in full, and `src/codecompass/enrichment.py`'s `apply_results` — the
  **current working tree** (these are uncommitted changes atop
  `38d577c`, not yet a landed commit).
- Ran `git diff` against each of the five changed `src/`/`tests/` files
  to confirm the lead's summary matches the real diff line-by-line, not
  just the docstrings.
- Ran `grep -rn "ExternalAdapterProcess(" src/codecompass/`, `grep -rn
  "\.initialize(" src/codecompass/`, and `grep -rn
  "record_symbol_enrichment(" src/codecompass/` to confirm each fix's
  one production call site actually supplies the new required
  argument, not just that the function signature changed in isolation.
- Ran the full relevant test suite directly against this working tree:
  `tests/test_adapters_base.py`, `test_adapters_dispatch.py`,
  `test_adapters_external_process.py`, `test_adapter_haskell.py`,
  `test_graph.py`, `test_enrichment.py` — 130 passed, 0 failed/errored/
  skipped (`pytest 9.1.1`).
- Read all five cited `docs/domain/` locations in full page context:
  `concepts/capability.md`, `concepts/protocol.md`,
  `concepts/ecosystem.md`, `concepts/provenance.md`,
  `open-questions.md`.
- Read the cited prior Observation/Evidence records in full:
  `OBS-ADPT-005`, `OBS-ADPT-017`, `EV-ADPT-010`, `OBS-EVID-011`,
  `CL-EVID-008`, `EV-EVID-013` — to confirm exactly what gap each
  documents, so my new records supersede the right claim precisely.
- Read `planning/phase-74-provenance-hardening.md` in full to confirm
  the implementation matches its own plan (it does — no undisclosed
  scope drift).
- Grepped `docs/domain/` for every other reference to the two now-fixed
  gaps (`OBS-ADPT-005`, `OBS-ADPT-017`, `EV-ADPT-010`, `OBS-EVID-011`,
  and characteristic phrases like "not itself validated" / "never
  subsequently read") — confirmed the five cited locations are the
  complete set; nothing else in the corpus cites either gap.
- Ran `scripts/check_knowledge_base.py` after appending new records —
  no findings.

## Verdict: both fixes are real and confirmed; four of five locations are genuinely, fully stale; the fifth (`provenance.md`) is stale but NOT fully closed — a real, narrower residual asymmetry remains and must be stated, not silently closed over

### Fix 1 (`L-031`, `symbol_enrichment.model`) — confirmed real, tested, wired to its one production call site

`src/codecompass/graph.py`'s `symbol_enrichment` table now has a
nullable `model TEXT` column (lines 176-182); `_migrate_symbol_
enrichment_model_column` (lines 515-549) adds it via `ALTER TABLE`
(never drop/recreate) on an old on-disk database, backfilling `NULL`
for pre-existing rows; `record_symbol_enrichment` (lines 1583-1608) now
requires a real `model: str` argument for every write, no default.
`enrichment.py:427`'s one production call site was updated to pass
`model=_MODEL`. Two new tests
(`test_open_graph_migrates_pre_phase_74_symbol_enrichment_preserves_rows`,
`test_open_graph_symbol_enrichment_migration_is_idempotent`) pass, and
the pre-existing `test_rebuild_deterministic_never_touches_symbol_
enrichment` was updated and still passes.

**Important nuance the lead's summary and a naive "gap closed" edit
would both miss**: `vendor_enrichment.model`/`doc_relation_enrichment.
model` are `NOT NULL` from their own first schema version;
`symbol_enrichment.model` is nullable, and every row written *before*
this migration is honestly `NULL`. The three enrichment tables are no
longer asymmetric in *whether* they carry a producer column, but they
remain asymmetric in *nullability*, and a pre-Phase-74 `symbol_
enrichment` row genuinely still cannot be attributed to a producer —
only new rows can. This is a real, narrower residual gap, not fully
resolved, and my replacement text for `provenance.md` below states it
explicitly rather than declaring blanket closure.

### Fix 2 (`L-032`, ecosystem/capabilities validation) — confirmed real, tested, wired to its one production call site

`ExternalAdapterProcess.initialize` now takes a required keyword-only
`expected_ecosystem: str`; after storing the wire response's
`ecosystem`/`capabilities` exactly as before, it now raises
`AdapterError` on an ecosystem mismatch and separately on any
`capabilities` entry outside the module's own closed `CAPABILITIES`
set. `haskell.py:188`'s one production call site passes
`expected_ecosystem=self.config.ecosystem` (a real `core.Ecosystem`
value, not a placeholder). Two new tests
(`test_ecosystem_mismatch_raises_adapter_error`,
`test_unrecognized_capability_raises_adapter_error`) pass, and every
pre-existing `.initialize()` call site across the test suite was
updated to supply `expected_ecosystem=` and still passes.

This one is fully closed as stated by both `capability.md`/
`protocol.md`'s and `ecosystem.md`'s own Counterexample claims — no
residual narrower gap found. (Adapter *dispatch* is, and remains,
driven entirely by `VendorConfig.ecosystem`, never the wire value —
that was never the claim at issue and is unchanged by this fix.)

## Resolved myself (no escalation — researchable facts, not a genuine ambiguity)

New records appended to `planning/knowledge/codecompass-domain/`:

- **`OBS-ADPT-018.yaml`** — direct read of current `initialize`/
  `_analyze` confirming both new checks exist and their shape.
- **`OBS-ADPT-019.yaml`** — grep confirming the one production call
  site for `ExternalAdapterProcess`/`initialize`.
- **`OBS-ADPT-020.yaml`** — test run confirming both new tests pass.
- **`EV-ADPT-011.yaml`** — conclusion: the `capability.md`/`protocol.md`
  capabilities-validation gap is closed, superseding `OBS-ADPT-005`.
- **`EV-ADPT-012.yaml`** — conclusion: the `ecosystem.md` ecosystem-
  comparison gap is closed, superseding `OBS-ADPT-017`/`EV-ADPT-010`;
  notes the unchanged dispatch-is-`VendorConfig.ecosystem`-only point.
- **`OBS-EVID-017.yaml`** — direct read of current `symbol_enrichment`
  schema/migration/writer, including the nullability nuance.
- **`OBS-EVID-018.yaml`** — grep confirming the one production call
  site for `record_symbol_enrichment` and that it supplies a real
  `model` value.
- **`OBS-EVID-019.yaml`** — test run confirming the new migration tests
  pass.
- **`EV-EVID-015.yaml`** — conclusion: the "no provenance column at
  all" gap is closed, but the narrower nullability/pre-existing-`NULL`
  asymmetry is explicitly **not** closed; `CL-EVID-008`'s broader
  cross-cutting-provenance claim is unaffected either way.

All ran cleanly through `scripts/check_knowledge_base.py`. No Claim,
Derivation, or Decision record written — my write boundary.

### Exact fix needed, per location (for the lead / whoever holds `docs/domain/` write access)

**1. `docs/domain/concepts/capability.md`, Counterexample section
(~lines 62-71), first paragraph only** — replace:

> **The received `capabilities` list is not itself validated against the
> closed 4-value set at parse time.** `ExternalAdapterProcess.initialize()`
> stores `tuple(response.get("capabilities", []))` directly — nothing in
> `external_process.py` checks each entry is one of the four known
> strings. An adapter reporting a fifth, unrecognized capability string
> would be accepted uncomplainingly by the Python client; the closed-set
> discipline currently rests entirely on the specification (SCHEMA.md)
> and on well-behaved adapters, not on enforcement code in this
> repository (`OBS-ADPT-005`).

with:

> **Closed as of Phase 74 (`L-032`) — the received `capabilities` list
> IS now validated against the closed 4-value set at parse time.**
> `ExternalAdapterProcess.initialize()` computes `unrecognized = [c for
> c in self.capabilities if c not in CAPABILITIES]` immediately after
> storing the tuple, and raises `AdapterError` if any entry falls
> outside the four known strings — an adapter reporting a fifth,
> unrecognized capability string now aborts `initialize` with a
> diagnostic error before `analyze_project` is ever reached, rather
> than being accepted uncomplainingly. The closed-set discipline no
> longer rests solely on the specification (SCHEMA.md) and well-behaved
> adapters; enforcement code now exists in this repository
> (`src/codecompass/adapters/external_process.py:99-104`,
> `EV-ADPT-011`, superseding the prior `OBS-ADPT-005`-documented gap).

(Leave the second paragraph — the "capability" word-usage looseness in
`sync.py:244` — unchanged; unaffected by this fix.) Update References
to add `EV-ADPT-011`, `OBS-ADPT-018`–`020`.

**2. `docs/domain/concepts/protocol.md`, Counterexample section (~lines
87-96), first paragraph only** — replace:

> **The received `capabilities` list is not itself validated against the
> closed 4-value set by `external_process.py` at parse time** — it is
> stored as `tuple(response.get("capabilities", []))` with no membership
> check. Nothing in the current Python client would reject or even flag
> an adapter reporting a fifth, unrecognized capability string; the
> closed-set discipline currently rests entirely on the *specification*
> (SCHEMA.md) and on well-behaved adapters, not on any enforcement code
> in this repository (`OBS-ADPT-005`).

with the same replacement text given for `capability.md` above (same
claim, same fix, same citation). Leave the second paragraph (the
"adaptor"/"adapter" spelling finding, already resolved via
`CL-ADPT-010`) unchanged. Update References to add `EV-ADPT-011`,
`OBS-ADPT-018`–`020`.

**3. `docs/domain/concepts/ecosystem.md`, Counterexample section
(~lines 55-73), in full** — replace:

> **The wire protocol's `ecosystem` field and CodeCompass's own
> `Ecosystem` enum are two independent, currently-unreconciled values.**
> `ExternalAdapterProcess.ecosystem` (set from an external adapter's
> `initialize` response) is stored but **never subsequently read,
> compared against `core.Ecosystem`, or used for any dispatch or
> validation decision anywhere in `src/codecompass/`** — confirmed by a
> direct grep of every `.ecosystem` attribute access in
> `src/codecompass/adapters/*.py` and `sync.py` (`OBS-ADPT-017`,
> `EV-ADPT-010`). Adapter dispatch is driven entirely by
> `VendorConfig.ecosystem` (fixed on the CodeCompass side, via
> `vendor.toml`, before any adapter process is even spawned). This means:
> nothing in the current implementation would detect or surface an
> external adapter reporting an `ecosystem` string that disagrees with
> the `Ecosystem` value CodeCompass configured it under — the wire field
> is currently write-only telemetry from CodeCompass's own perspective.
> This is a real, observed gap in the current implementation, not merely
> a specification looseness.

with:

> **Closed as of Phase 74 (`L-032`) — the wire protocol's `ecosystem`
> field IS now read and compared against the `Ecosystem` value
> CodeCompass configured the adapter under.**
> `ExternalAdapterProcess.initialize()` now takes a required
> `expected_ecosystem: str` keyword argument, and raises `AdapterError`
> ("external adapter ecosystem mismatch: CodeCompass configured this
> adapter under `{expected_ecosystem!r}`, adapter responded with
> `{self.ecosystem!r}`") if the wire-reported `self.ecosystem`
> disagrees. `HaskellAdapter._analyze` — the one production call site —
> passes `expected_ecosystem=self.config.ecosystem`, the real
> `core.Ecosystem` value fixed via `vendor.toml` before the adapter
> process is even spawned (`src/codecompass/adapters/
> external_process.py:53-98`, `src/codecompass/adapters/haskell.py:
> 184-195`, `EV-ADPT-012`, superseding the prior `OBS-ADPT-017`/
> `EV-ADPT-010`-documented gap). The wire field is no longer write-only
> telemetry — it is validated on every `initialize` call, before
> `analyze_project` is reached.
>
> **Narrower point preserved unchanged**: adapter *dispatch* (`get_
> adapter`) is still driven entirely by `VendorConfig.ecosystem`, never
> by the wire-reported value — this fix adds a validation check, not a
> new dispatch path. The two values remain independently-typed things
> (one free text, one closed enum); they are now compared for equality
> at one point, not unified into one type.

Update References to add `EV-ADPT-012`, `OBS-ADPT-018`–`020`.

**4. `docs/domain/concepts/provenance.md`** — two spots, both
substantive content (not mechanical citation swaps), and **neither
should be written as unqualified full closure**:

**4a. Definition, point 2 (~lines 21-28)** — replace:

> 2. **Two of the three enrichment tables** — `vendor_enrichment` and
>    `doc_relation_enrichment` — each carry a single `model` `TEXT`
>    column (a real Anthropic model id, or `agent:<agent-name>` for
>    agent-driven output, per `decisions/0054`). **`symbol_enrichment`
>    carries no provenance column at all** — a real asymmetry within the
>    same mechanism, not a uniform property of "the enrichment tables" as
>    a group (`src/codecompass/graph.py:165-182`; see "Counterexample"
>    below).

with:

> 2. **All three enrichment tables** — `vendor_enrichment`, `doc_
>    relation_enrichment`, and (as of Phase 74, `L-031`) `symbol_
>    enrichment` — now carry a `model` `TEXT` column (a real Anthropic
>    model id, or `agent:<agent-name>` for agent-driven output, per
>    `decisions/0054`). **A narrower asymmetry remains**: `vendor_
>    enrichment.model`/`doc_relation_enrichment.model` are `NOT NULL`
>    from their own first schema version, while `symbol_enrichment.
>    model` is nullable — a pre-Phase-74 row's real producer was never
>    recorded and honestly backfills `NULL` rather than a fabricated
>    value, so a `symbol_enrichment` row written before this migration
>    remains provenance-unknown in a way no sibling-table row can be
>    (`src/codecompass/graph.py:164-182, 515-549`; see "Counterexample"
>    below; `EV-EVID-015`).

**4b. Counterexample section (~lines 72-88), in full** — replace:

> `symbol_enrichment` (`src/codecompass/graph.py:177-182`) has **no
> provenance column at all** — `id, symbol_id, purpose, generated_at`,
> four columns, none naming a producer. This is a real, structural
> asymmetry within the *same* enrichment mechanism decisions/0054
> describes as uniformly distinguishable "using a column that has existed
> since Phase 14" — that statement is accurate for
> `vendor_enrichment`/`doc_relation_enrichment`, but not, on direct
> inspection, for `symbol_enrichment`, which has no `model` column to
> read at all (`OBS-EVID-011`). Whether this is a genuine gap
> (`symbol_enrichment` rows currently cannot be attributed to a specific
> producer at all, agent or automated) or an intentional simplification
> this research did not find a stated rationale for is left as an
> observed, unresolved fact — not something this research resolves,
> since resolving it would require deciding whether to add a column,
> which is a `src/codecompass/` change out of this phase's own scope.

with:

> **Closed as of Phase 74 (`L-031`) — `symbol_enrichment` now has a
> `model` column.** `src/codecompass/graph.py:176-182` shows five
> columns, not four: `id, symbol_id, purpose, model, generated_at`. The
> column was added via `_migrate_symbol_enrichment_model_column` (an
> `ALTER TABLE ... ADD COLUMN`, never a drop-and-recreate — this table
> holds paid enrichment output that must survive migration). `record_
> symbol_enrichment`, the table's only writer, now requires a real
> `model` argument for every new write; its one production call site
> (`enrichment.py:427`) supplies the real Anthropic model id used for
> that batch (`EV-EVID-015`, `OBS-EVID-017`, `OBS-EVID-018`). It is no
> longer accurate that a row written from this migration forward cannot
> be attributed to a specific producer.
>
> **Residual, narrower, still-real asymmetry**: unlike `vendor_
> enrichment.model`/`doc_relation_enrichment.model` (both `TEXT NOT
> NULL` from their own first schema version), `symbol_enrichment.model`
> is nullable, and every row written before this migration backfills
> `NULL` — an honest "producer unknown, predates this column," not a
> retroactively fabricated value. A pre-Phase-74 `symbol_enrichment` row
> therefore remains provenance-unknown in a way no `vendor_enrichment`/
> `doc_relation_enrichment` row (`NOT NULL` since inception) can be.
> Whether this residual nullability is itself worth resolving further
> (e.g. a one-time backfill heuristic, or simply accepting it as
> permanent history) was not investigated here and is not decided by
> this record either way.

Update References to add `EV-EVID-015`, `OBS-EVID-017`–`019`.

**Not something I resolve myself**: `CL-EVID-008`'s own filed
`statement` text (`planning/knowledge/codecompass-domain/
CL-EVID-008.yaml`) contains the identical now-stale parenthetical
("absent entirely on `symbol_enrichment`") baked into a Claim record's
own prose — I cannot edit a Claim (write boundary). **Name for
`context-researcher`**: revise `CL-EVID-008`'s statement (or file a
superseding Claim) to say the three enrichment tables now all carry a
`model` column, with the nullability caveat, citing `EV-EVID-015`. The
Claim's *conclusion* (provenance is a cross-cutting concern with no
shared schema unifying the three mechanisms) is unaffected and does not
need re-deriving — only the specific enrichment-table sub-fact embedded
in its prose does.

**5. `docs/domain/open-questions.md`, items 9 and 10 (~lines 113-129)**
— per this file's own re-entry rule ("never removed silently, only
marked resolved with a pointer to what resolved it"), and matching
`protocol.md`'s own established in-place "**Resolved** (`CL-ADPT-010`)"
convention for an analogous case, keep both items in place under their
current numbers and prefix each with its resolution. Replace item 9:

> 9. **`symbol_enrichment` has no provenance column at all** — unlike
>    `vendor_enrichment`/`doc_relation_enrichment`, which both carry a
>    `model TEXT NOT NULL` column. `decisions/0054`'s own claim that all
>    three enrichment tables uniformly distinguish producers "using a
>    column that has existed since Phase 14" is factually wrong for
>    `symbol_enrichment` specifically, independently re-confirmed by
>    `domain-skeptic` against the real schema. See
>    [`concepts/provenance.md`](concepts/provenance.md).

with:

> 9. **RESOLVED (Phase 74, closes `L-031`) — `symbol_enrichment` now has
>    a provenance column.** Previously: `symbol_enrichment` carried no
>    provenance column at all, unlike `vendor_enrichment`/`doc_relation_
>    enrichment` (`model TEXT NOT NULL`). As of Phase 74, `symbol_
>    enrichment.model` exists (`src/codecompass/graph.py:176-182`), and
>    `record_symbol_enrichment` requires a real `model` argument for
>    every new write (its one production call site, `enrichment.py:427`,
>    supplies it). Residual, narrower point not closed by this fix:
>    `symbol_enrichment.model` is nullable and every pre-Phase-74 row
>    backfills an honest `NULL`, unlike the two sibling `NOT NULL`
>    columns — see [`concepts/provenance.md`](concepts/provenance.md)'s
>    own Counterexample section. *(`EV-EVID-015`, `OBS-EVID-017`–`019`,
>    superseding the prior `OBS-EVID-011`-documented gap.)*

Replace item 10:

> 10. **The external protocol's wire-level `ecosystem` field, and its
>     `capabilities` list, are received but never validated against their
>     own closed sets** — `ExternalAdapterProcess.ecosystem` is set and
>     never subsequently read/compared anywhere in `src/codecompass/`; the
>     `capabilities` tuple is stored with no membership check against the
>     protocol's own closed 4-value set. Both independently re-confirmed
>     by `domain-skeptic` via direct grep. See
>     [`concepts/ecosystem.md`](concepts/ecosystem.md) and
>     [`concepts/capability.md`](concepts/capability.md).

with:

> 10. **RESOLVED (Phase 74, closes `L-032`) — the external protocol's
>     wire-level `ecosystem` field and `capabilities` list ARE now
>     validated against their own closed sets.** Previously:
>     `ExternalAdapterProcess.ecosystem` was set and never subsequently
>     read/compared anywhere in `src/codecompass/`, and the
>     `capabilities` tuple was stored with no membership check. As of
>     Phase 74, `initialize()` requires an `expected_ecosystem` argument
>     and raises `AdapterError` on a mismatch, and separately raises
>     `AdapterError` on any `capabilities` entry outside the module's own
>     closed `CAPABILITIES` set. `HaskellAdapter`'s one production call
>     site passes the real `core.Ecosystem` value. Fully closed — no
>     residual gap found. See
>     [`concepts/ecosystem.md`](concepts/ecosystem.md) and
>     [`concepts/capability.md`](concepts/capability.md)'s own
>     Counterexample sections. *(`EV-ADPT-011`, `EV-ADPT-012`,
>     `OBS-ADPT-018`–`020`, superseding the prior `OBS-ADPT-005`/
>     `OBS-ADPT-017`-documented gaps.)*

These both currently sit under the "## Known implementation gaps, not
domain-meaning ambiguities" heading, whose own intro sentence describes
its contents as gaps "routed to `planning/learnings/inbox.md` as
future-improvement candidates... not resolved here." That intro is now
slightly imprecise for items 9/10 specifically (they *were* routed
there, as `L-031`/`L-032`, and have *since* been resolved) — a
one-line addendum to the section intro, or simply leaving the two
RESOLVED-prefixed items as the self-explanatory exception, are both
reasonable; this is a structural/editorial call for whoever applies the
edit, not a domain-meaning question, so I'm not naming one exact
required wording for it.

## Escalations

**None.** Both fixes are real, independently verified against current
source and a passing test suite tied to real production call sites.
Four of the five locations are fully, mechanically closed by the fix as
described. The fifth (`provenance.md`, and open-questions item 9) is
**not** a case of full closure — I found and am reporting a genuine
residual asymmetry (nullability, honest historical `NULL`) that the
replacement text states explicitly rather than glossing over. This is a
researchable fact I already resolved myself by reading the schema
directly, not a product ambiguity requiring the user's judgment call —
so it is stated as a caveat in the replacement text, not escalated.

## Write-boundary compliance

- No edits made to `docs/domain/`, `decisions/`, or any `src/`/test
  content — read-only, as required. Exact replacement text named above
  for whoever holds `docs/domain/` write access to apply.
- Nine new records appended under `planning/knowledge/codecompass-domain/`
  (`OBS-ADPT-018`–`020`, `EV-ADPT-011`, `EV-ADPT-012`, `OBS-EVID-017`–
  `019`, `EV-EVID-015`) — Observation/Evidence only, no Claim,
  Derivation, or Decision record written.
- One revision named for `context-researcher` to make
  (`CL-EVID-008`'s own stale statement text), not made by me.
- `scripts/check_knowledge_base.py` run after appending — no findings.
