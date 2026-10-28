# Phase 84: Consolidated Knowledge API and Query CLI — plan

**Status: implemented (2026-10-29, "CodeCompass Orchestrator — Close
Phase 83 and Implement Phase 84").** `src/codecompass/knowledge_api.py`
plus six new read-only `knowledge *` CLI commands and the `query
relations` migration are built against this plan. `decisions/0091`
records the implementation-time resolutions this plan's own §10
deliberately deferred (the `ContextPacket` shape) plus the concrete
response/identity encodings the plan described only at a conceptual
level — see that ADR for the full rationale; nothing in it reopens
`decisions/0084`/`0085`'s own settled architecture.

Governing prompt: "CodeCompass Orchestrator — Approve v2 Roadmap and Plan
Phases 83–84" (2026-10-24). Roadmap-depth scope: `planning/v2-roadmap.md`
§"Phase 84"; architecture: `decisions/0084` §1-2, formalised by
`decisions/0085` §1-2. This file is the `CLAUDE.md` §1 implementation-ready
plan those sections sketched, resolving the governing prompt's three
mandatory architectural considerations (A: stable identities, B: snapshot
consistency, C: primary authority vs. derived indexes) against the real,
directly-inspected implementation rather than assumption.

## 0. Verified current state (read live, not assumed)

- **CLI structure** (`src/codecompass/cli.py`): `query_app`, `enrich_app`,
  `knowledge_app` are three independent `typer.Typer()` sub-apps (lines
  54/56/60), confirmed unchanged since `decisions/0084`/`0085`. Real
  commands: `query {vendors,vendor,symbol,skills,relations,topology,
  source,source-symbol}`; `enrich {apply}`; `knowledge {render,
  select-candidates,apply,status,doc-select-candidates,
  doc-acknowledge-stale,doc-acknowledge-chunks}`. The only mutation
  commands anywhere in this surface are `enrich apply`, `knowledge apply`,
  `knowledge doc-acknowledge-stale`, `knowledge doc-acknowledge-chunks`,
  and `oracle.py::accept_baseline` (no CLI wrapper yet) — every `query *`
  command and `knowledge status` are already read-only today.
- **`context-graph.db` rebuild behaviour** (`graph.py::rebuild_
  deterministic`, confirmed by reading its real `DELETE`/upsert
  statements): `doc_relations_edges`, `depends_on_edges`, `routes_via_
  edges`, `skill_mentions_edges`, `documents_edges`, `uses_edges`,
  `doc_chunks`, `doc_artifacts`, `git_worktrees`, `git_submodules`,
  `git_repositories` are **wholesale deleted and reinserted every sync** —
  their own `INTEGER PRIMARY KEY` ids are not stable across a rebuild,
  confirmed directly, not inferred. `vendors`, `symbols`, `source_files`,
  `source_symbols` are upserted/deleted **incrementally by natural key**
  (per-row `DELETE ... WHERE` on the stale subset only) — their ids are
  comparatively durable but are **not** treated as an external identity by
  this plan regardless (§3A), to keep one identity discipline project-wide.
  `source_symbols` already carries a real natural key in its own schema:
  `UNIQUE (source_file_id, name, kind, line)` (`graph.py:107`).
- **A directly reusable precedent already exists for exactly this
  problem**: `doc_relation_enrichment` (`graph.py:231-242`, `decisions/
  0038`) is keyed by plain natural-key `TEXT` columns
  (`source_doc_path`, `target_vendor_name`, `target_doc_path`) specifically
  *because* `doc_artifacts.id` is wholesale-reinserted every rebuild and a
  foreign key to it would cascade this table's own content away — the
  exact failure mode Mandatory Consideration A warns about, already
  solved once, for one table. Phase 84 generalises this existing pattern
  rather than inventing a new one.
- **`meta` key/value table** (`graph.py`, confirmed via live query against
  `~/projects/ledgerkit/context-graph.db`) already carries exactly the
  graph/index-revision fields Mandatory Consideration B asks for:
  `schema_version`, `last_deterministic_rebuild_at`,
  `source_index_version`, `git_topology_status`. No new field needed.
- **Presentation/evidence currency mechanism already exists**:
  `knowledge_intermediate.py`'s `PresentationEntry` dual-hash anchor and
  `_current_cited_hashes` (line 314: recomputes a cited record's current
  content hash fresh, for comparison against what was last cited) are the
  direct precedent for "is this evidence still current" — reused, not
  reinvented.
- **Epistemic/evidence-currency distinction already exists**:
  `derive_epistemic_profile` (`decisions/0080`) already separates
  `verified_scopes` (confirmed current), `unconfirmed_scopes` (a
  historical PASS that could not be reconfirmed live), and
  `known_gap_scopes` (no evidence at all) — reused unchanged, per
  `decisions/0085` §1 point 5.
- **Portable export envelope already specified**: `decisions/0079` §5's
  project-identity envelope (`project_id`/`source_locator`/`revision`/
  `knowledge_schema_version`/`exported_at`) and qualified-reference triple
  `(project_id, revision, local_id)` — reused directly as this phase's own
  export target, per `decisions/0085` §1's own instruction not to invent a
  second format.
- **Canonical-vs-derived distinction already decided**:
  `decisions/0084` §1 / `decisions/0085` §1 point 2: canonical =
  `context-graph.db`, `planning/knowledge/`, `planning/contracts/`,
  accepted ADRs; derived/presentation = rendered Markdown projections, the
  presentation cache, generated documentation. Reused unchanged.

## 1. Objective / user value

One stable, **read-only**, typed query/traversal interface over
CodeCompass's existing knowledge (mechanical graph facts, reconciled
Observation/Evidence/Claim/Derivation/Decision/Requirement records,
behavioural contracts/oracle results) so a caller — a test, a script, or
eventually an agent — can ask "what does this project know about X, how
confident are we, and is that confidence still current" through one
interface, instead of independently reconstructing `context-graph.db` SQL
or a `planning/knowledge/` file walk. No consolidation of physical
storage; no mutation path.

## 2. Reused capabilities and components (verified, §0)

`knowledge_intermediate.py`'s record model, `derive_provenance_label`,
`derive_epistemic_profile`, `PresentationEntry`/`_current_cited_hashes`;
`graph.py`'s existing schema and `meta` table; `oracle.py`'s contract/
result parsing, `evaluate_result_precedence`, `aggregate_contract`;
`decisions/0038`'s natural-key-table pattern; `decisions/0079` §5's export
envelope; every existing `query`/`knowledge` command as the
backward-compatibility baseline for the one command this phase migrates
(§4).

## 3. Architectural changes

### 3.0 The logical model (nine points, `decisions/0085` §1 — bound to real mechanisms)

1. **Identity**: existing `REQ-`/`CL-`/`EV-`/`OBS-`/`DE-`/`DEC-` ids and
   `context-graph.db`/oracle-contract ids. No new id scheme for canonical
   records.
2. **Canonical vs. derived/presentation-only**: per §0, unchanged.
3. **Authoritative sources per knowledge kind**: §3C's table.
4. **Provenance**: existing `oracle_contract_content_hash`/
   `tested_subject_digest`/`repository_revision`/clean-room manifest
   digests — exposed, not duplicated.
5. **Epistemic dimensions**: `derive_epistemic_profile`, unchanged.
6. **Contradictions/gaps**: existing `contradicting_evidence`/
   `open_questions`/`unconfirmed_scopes`/`known_gap_scopes` fields, newly
   queryable *across* record kinds in one call — this phase's one new
   cross-cutting capability (risk #10's own "genuinely new value" bar).
7. **Read-only vs. mutation**: §6 — structural, not a stated intention.
8. **Missing-knowledge handling**: a typed three-way response
   (`result` / `empty` / `gap`) for every API call — `gap` is reserved for
   "a specific obligation exists but no evidence resolves it," distinct
   from `empty` ("no matching record at all").
9. **Versioned export**: `decisions/0079` §5's envelope, reused.

### 3.A Mandatory Consideration A — stable identities

| Identity class | What it is | Stability |
|---|---|---|
| Internal DB key | `*.id INTEGER PRIMARY KEY` on any table | Volatile for every wholesale-rebuilt table (`doc_relations_edges`, `depends_on_edges`, `routes_via_edges`, `skill_mentions_edges`, `documents_edges`, `uses_edges`, `doc_chunks`, `doc_artifacts`, `git_*`); incidentally durable (incremental upsert) for `vendors`/`symbols`/`source_files`/`source_symbols`, but **never exposed by this API as an identity either way** |
| Stable canonical knowledge-record id | `REQ-`/`CL-`/`EV-`/`OBS-`/`DE-`/`DEC-` ids; oracle `contract_id`/`check_id` | Already durable, human-assigned; reused unchanged |
| Durable source/relationship fact identity | A deterministic tuple of existing natural-key columns, computed at query/export time — **never a new persisted column** | Survives rebuild by construction (see below) |
| Project-qualified export identifier | `decisions/0079` §5's `(project_id, revision, local_id)` | Reused unchanged |

The new piece is the third row, generalising `decisions/0038`'s own
precedent to every fact kind this API exposes:

- source symbol: `(source_file.path, name, kind, line)` — already the
  table's own `UNIQUE` constraint (§0).
- uses-edge: `(source_file.path, vendor.name, symbol.name, line)`.
- doc-relation: `(source_doc.path, target_vendor.name | target_doc.path,
  relation_kind)` — literally `doc_relation_enrichment`'s own existing key.
- git fact: `(repository.common_dir, worktree_path | submodule.path)`.

Each is a pure function over columns that already exist; **no new
persisted identifier anywhere**, matching the instruction to avoid
unnecessary new ids.

**Required test** (graph-rebuild survival, §7): using the real `tests/
fixtures/ledgerkit_lifecycle_demo/context-graph.db` fixture (already
exists in this repository), record a real `source_symbols` row's raw `id`
and this phase's computed natural-key identity; call `rebuild_
deterministic` again against the same unchanged source; assert the raw
`id` **may** differ (proving the risk is real) while the computed
identity is **byte-identical**. A second test does the same for a
wholesale-rebuilt edge table (`uses_edges` or `doc_relations_edges`, via
a fixture vendor/doc so the table is non-empty) — this is the table class
where the raw id is *guaranteed*, not merely permitted, to change.

### 3.B Mandatory Consideration B — snapshot consistency

A response-time **consistency envelope** (an in-memory dataclass the API
attaches to every response — never a new persisted concept) bundling
five already-existing values:

1. Source revision — `repository_revision`/`tested_subject_digest`
   (oracle.py, knowledge records).
2. Knowledge revision — a cited record's current content hash,
   recomputed via `_current_cited_hashes`'s own existing method.
3. Graph/index revision — `meta.last_deterministic_rebuild_at` +
   `meta.schema_version` + `meta.source_index_version`.
4. Contract/verification identity — `oracle_contract_content_hash`/
   `run_id`/`baseline_id`.
5. Evidence currency — `derive_epistemic_profile`'s existing
   `verified_scopes`/`unconfirmed_scopes`/`known_gap_scopes`.

**Rule**: if all five cannot be established for a given response (e.g. the
target `repo_root` is unreachable to confirm a digest), the response's own
status is `stale`/`unconfirmed` — reusing `derive_epistemic_profile`'s
existing vocabulary rather than inventing a second one — never silently
presented as current.

**Required tests**: (a) positive — a consistent-snapshot query against
real `balance-from-spec` data with `repo_root` reachable resolves all
five and reports current; (b) negative/stale — mutate a target checkout's
file without re-syncing its graph, confirm the API reports `stale` for
the affected fact rather than silently serving the old `source_symbols`
row as current; (c) negative/incompatible — construct an oracle-result
whose `tested_subject_digest` does not match its own claim's
`repository_revision`, confirm the API surfaces the mismatch explicitly,
reusing `evaluate_result_precedence`'s existing INVALID-on-mismatch logic
rather than re-implementing digest comparison a second time.

### 3.C Mandatory Consideration C — primary authority vs. derived indexes

| Source | Authority tag | What it can prove |
|---|---|---|
| Source code / config in the target repo | `primary_evidence` | Current real behaviour, directly |
| `context-graph.db` | `derived_index` | What the index *last recorded*, timestamped by `meta.last_deterministic_rebuild_at` — never current behaviour on its own |
| Accepted ADR | `stated_intent` | What was *decided*, not what was *built* |
| Requirement | `accepted_obligation` | What behaviour is expected, not that it holds |
| Oracle result | `scoped_verification` | Verification within its exact tested scope and revision only (`evaluate_result_precedence`'s existing digest-bound scoping) |
| Intermediate Markdown (`planning/knowledge/*.md` projections) | `editable_projection` | A human-editable view, subject to reconciliation |
| Generated documentation | `presentation_artifact` | Presentation only, never evidence |

This is a pure classification function over the record kind a datum
came from — no new storage. Every API response item carries its own
`authority` tag; the API **never lets a `derived_index` fact stand in for
`scoped_verification`** — a caller asking "does X still behave as
claimed" gets both layers, visibly distinct, never conflated into one
answer.

**Required tests**: a symbol with no oracle verification at all is
tagged `derived_index`/`stated_intent` only, never implying
`scoped_verification`; the real `balance_from_spec` response shows both
an `accepted_obligation` (`DEC-BFS-001`'s own intent) and a
`scoped_verification` (the real oracle PASS) as visibly separate items,
never merged into a single "verified" claim.

## 4. Deliverables

1. **`src/codecompass/knowledge_api.py`** (new, read-only library module):
   - `search(text, kinds=None) -> list[KnowledgeResult]`
   - `get(record_id) -> KnowledgeView | Gap`
   - `traverse(record_id, relation, depth=1) -> list[KnowledgeResult]`
   - `trace_evidence(record_id) -> EvidenceTrace`
   - `epistemic_status(scope_or_id) -> EpistemicProfile` (wraps `derive_
     epistemic_profile` unchanged)
   - `find_gaps(slug=None) -> list[GapReport]` (the one genuinely new
     cross-record-kind capability, §3.0 point 6)
   - `get_context_packet(topic, bound=...) -> ContextPacket`
   - `export_snapshot(slug, out_path) -> PortableSnapshot` (writes
     `decisions/0079` §5's envelope format)
   Every function returns the typed three-way `result`/`empty`/`gap`
   shape (§3.0 point 8) and attaches the §3.B consistency envelope and
   §3.C authority tag to every item.
2. **New, read-only CLI operations**, added under the **existing**
   `knowledge_app` typer sub-app (no new top-level app — avoids
   gratuitous surface growth): `knowledge get`, `knowledge trace`,
   `knowledge search`, `knowledge gaps`, `knowledge context`,
   `knowledge export`. Clearly namespaced apart from the existing
   mutation verbs (`apply`, `select-candidates`, `doc-acknowledge-*`).
3. **One existing command migrated onto the API**, as this phase's own
   concrete proof it is not a redundant wrapper (risk #10):
   `query relations` is re-implemented in terms of `knowledge_api.
   traverse`, with a backward-compatibility test asserting byte-identical
   output against a representative input set before and after. No other
   existing command is migrated this phase — `decisions/0085` §2 makes
   this explicitly optional and case-by-case, not a wholesale migration.

## 5. Dependencies and prerequisites

Phase 82, complete. Does not require Phase 83 (sequenced after it by the
governing prompt's own explicit ordering, not a hard dependency — §9 of
Phase 83's own plan records this as true in both directions).

## 6. Explicit exclusions / non-goals

- **No mutation path of any kind.** `knowledge apply`, `enrich apply`,
  `knowledge doc-acknowledge-*`, and `oracle.py::accept_baseline` remain
  the only ways to write, structurally unreachable through `knowledge_
  api.py` — no function in that module issues an `INSERT`/`UPDATE`/
  `DELETE` or writes a `planning/knowledge/`/`planning/contracts/` file.
  Enforced by a dedicated test (§7) asserting the module imports no
  writer function from `knowledge_intermediate.py`/`oracle.py` beyond
  `derive_epistemic_profile`/parsing helpers.
- **No new `context-graph.db` schema change, no new database.**
- **No MCP exposure** (Phase 88 consumes this API; does not rebuild it).
- **No wholesale migration** of every existing `query`/`knowledge`/
  `enrich` command (§4.3's single, deliberate exception).
- **No Layer B/C federation constructs** (`decisions/0079`) — the
  traversal shape must not *preclude* a future federated caller (the
  qualified-reference reuse in §3.A already keeps this door open), but
  building federation support now is out of scope.
- **No `git diff` ingestion or call-graph** (that is Phase 83's own
  excluded scope too, for the same proportionality reason).

## 7. Tests and negative controls

- Backward-compatibility: `query relations`'s migrated output is
  byte-identical to its pre-migration output across a representative
  input set (reuses whatever fixture `query relations`'s own existing
  tests already use).
- Negative-path tests for every new API operation: a malformed query, a
  non-existent id, a traversal with no results — each returns the
  defined `empty`/`gap` shape, never collapses into the other or raises
  uncaught.
- §3.A's two graph-rebuild-survival tests (natural-key-table class and
  wholesale-rebuilt-edge-table class).
- §3.B's three consistency tests (current, stale, incompatible-revision).
- §3.C's two authority-tagging tests (unverified symbol; real
  `balance-from-spec` dual-layer response).
- The no-mutation-path static check (§6).
- New traversal/contradiction/gap-detection tests against this project's
  own real `planning/knowledge/`/`context-graph.db` corpus, not a
  synthetic fixture only (per the roadmap's own §7 requirement),
  supplemented by constructed negative cases for edge conditions the real
  corpus doesn't happen to contain yet.

## 8. Dogfood scenario

A fresh caller retrieves `DEC-BFS-001` (approved intent), `REQ-BFS-001`'s
real implementation facts (`reports.py::balance_from_spec`, via `source_
symbols`' natural-key identity), its real Phase 82 oracle contract and
PASS results, and its full provenance — all through `knowledge_api.py`
alone — and the response visibly distinguishes `stated_intent`
(`DEC-BFS-001`) from `scoped_verification` (the real oracle PASS) for
this one real case, per §3.C's own acceptance requirement.

## 9. Acceptance criteria / exit gate (the governing prompt's seven, each addressed)

1. Retrieve knowledge about a real subsystem — §8.
2. Identify associated source, ADRs, requirements, contracts — §8,
   `trace_evidence`.
3. Trace supporting and contradictory evidence — `trace_evidence`,
   §3.0 point 6.
4. Distinguish approved intent from observed/verified behaviour — §3.C,
   §8.
5. Identify missing, stale, or conflicting knowledge — `find_gaps`,
   §3.B's `stale` status.
6. Retrieve a coherent, bounded context packet — `get_context_packet`.
7. Export with durable identifiers and revision metadata —
   `export_snapshot`, §3.A/§0's `decisions/0079` §5 reuse.

A fresh caller (a test, not a human narrating intent) demonstrates all
seven against real project data before this phase is considered done —
demonstrated, not merely asserted (matching `planning/v2-roadmap.md`'s own
Phase 84 exit-gate wording).

## 10. Risks, alternatives, and unresolved decisions

**Risks.**
- Thin-wrapper risk (roadmap's own risk #10) — mitigated by §3.0 point 6
  (cross-record-kind contradiction/gap detection, which no existing
  command provides today) and §4.3's real migration proof.
- The consistency envelope (§3.B) adds a small amount of per-call
  overhead (several existing-mechanism calls per response) — acceptable
  for a read-only, non-hot-path library; revisit only if real use shows a
  performance problem.

**Alternatives considered.**
- *A new persisted "stable id" column on every table.* Rejected —
  contradicts "avoid unnecessary new persisted identifiers"; the natural-
  key approach (§3.A), already proven by `decisions/0038`, needs none.
- *A new independent knowledge database consolidating the three physical
  stores.* Rejected — this is exactly `decisions/0084` §1's own already-
  settled architectural decision (one logical model, unchanged physical
  storage), not reopened here.
- *Migrating every existing command onto the API immediately.* Rejected
  by `decisions/0085` §2 explicitly; §4.3 does the minimum needed to prove
  the API isn't redundant.

**Unresolved decisions (recorded, not invented).**
- Whether `scripts/assess_change_impact.py` (Phase 83) should be rewritten
  onto `knowledge_api.py` once this phase exists — a natural follow-on,
  **still not committed here**; Phase 83 remains independently functional
  and unmodified by this phase, exactly as sequenced.
- ~~The exact shape of `ContextPacket`...~~ **Resolved during
  implementation — `decisions/0091` §6**: a fixed, non-ranked priority
  order (subject → direct relations → gaps), deduplicated, bounded by
  `max_items`/`max_chars` with explicit `truncated` reporting, informed
  by real queries against this project's own `balance-from-spec` corpus.

## 11. Verification (how this phase is confirmed done)

`.venv/bin/python -m pytest tests/test_knowledge_api.py` (new) plus every
existing `tests/test_knowledge_intermediate.py`/`tests/test_oracle.py`/
`tests/test_check_knowledge_base.py`/`tests/test_cli.py`-equivalent
suite re-run green (confirming no migrated-command regression); `docs/`/
`architecture/` updated to describe the new module and CLI surface;
`CHANGELOG.md` entry; `planning/ROADMAP.md`/`planning/CONTEXT.md`
updated; a `planning/retros/phase-84-consolidated-knowledge-api.md`
retro; `release-phase-auditor` PASS against this exact plan's own
verification steps before `planning/ROADMAP.md` marks Phase 84 `done`
(`CLAUDE.md` §5).
