# Phase 80 Stage 3 — Alignment report: snapshot vs. model-blind implementation reconstruction

**Role**: domain-skeptic, comparison mode (`decisions/0066`).

**Inputs compared**:
- Snapshot: `planning/knowledge/codecompass-domain/snapshots/snapshot-codecompass-overview-v1.toml`
  (`snapshot_id = "codecompass-overview@v1"`, 25 active Claims — `CL-ADPT-{001-007,010,011}`,
  `CL-CTXT-{001-006}`, `CL-EVID-{001,002,004,005,006,007,010,011,012,013}`). Read directly
  from the cited `CL-*.yaml` files, not the snapshot's own metadata.
- As-built: `phase80-implementation-reconstruction.md`, produced by `implementation-reconstructor`
  from a bounded source+test export with zero doc/KB access.

**Scope note, stated up front**: the 25 Claims are almost entirely meta-level knowledge-model
concepts (adapter protocol, Claim/Evidence/Derivation/Decision/Requirement, context's five senses,
relationship/edge, reference, digest, provenance) plus two project-process concepts (naming
collisions, record lifecycle). The reconstruction is implementation-level (literal `graph.py`
schema, `cli.py` command surface, `sync.py` call chain, `adapters/base.py`+`python.py`). Only
a minority of Claims have any implementation-level content to check against; this is expected
and is reported honestly as `insufficiently_verified` rather than forced into a verdict.

## Verdict tally

| Verdict | Count | Claims |
|---|---|---|
| `aligned` | 3 | CL-ADPT-001, CL-CTXT-005, CL-CTXT-006 |
| `partial` | 8 | CL-ADPT-002, CL-ADPT-005, CL-CTXT-001, CL-CTXT-002, CL-CTXT-003, CL-CTXT-004, CL-EVID-011, CL-EVID-012 |
| `insufficiently_verified` | 14 | CL-ADPT-003, CL-ADPT-004, CL-ADPT-006, CL-ADPT-007, CL-ADPT-010, CL-ADPT-011, CL-EVID-001, CL-EVID-002, CL-EVID-004, CL-EVID-005, CL-EVID-006, CL-EVID-007, CL-EVID-010, CL-EVID-013 |
| `conflicting` | 0 | — |
| `not_implemented` | 0 | — |

No real conflicts found. No Claim's status is recommended for promotion by this pass alone
(alignment is not verification, per this role's own hard rule).

## Per-claim findings

### aligned

**CL-ADPT-001** (adapter = concrete `EcosystemAdapter` subclass; 5 abstract methods +
1 concrete `symbols()`; `get_adapter` closed dispatch, one class per `Ecosystem` member).
Reconstruction §4 independently confirms, via direct reading plus the one adapter that
actually runs in its sandbox (`PythonAdapter`): the same 5 method names
(`installed_version`, `source_location`, `readme_and_api_surface`, `repository_url`,
`dependency_tree`), `symbols()` concrete/overridable (confirmed via
`test_ecosystem_adapter_rejects_incomplete_subclass` passing — abstractness is real,
enforced by `ABC`/`TypeError`), and `adapters/__init__.py::get_adapter(config,
project_root)` as "the single construction point, keyed by a `dict[Ecosystem,
type[EcosystemAdapter]]`." Direct match.
*Minor reconciliation note*: the reconstruction's own prose says "requires four abstract
methods" immediately before listing five — an internal miscount in the reconstruction's
own wording, not a conflict with the snapshot (whose "five" is the one that's actually
correct against the method list both documents give). Not actionable against the snapshot;
flagged only so Stage 4 doesn't copy the "four" miscount forward.

**CL-CTXT-005** (`VendorDigest`, `src/codecompass/core.py`; combines deterministic
free output with a read-only enrichment lookup; renders DEPTREE/FILETREE/CLAUDE.md/
OVERVIEW.md under `vendor/<name>/` on every whole-project sync). Reconstruction's
`core.py` entry describes `VendorDigest` as "the aggregate per-vendor sync output
struct," and its `sync_vendor` trace (§6) independently reconstructs the identical
behaviour: "read-only-looks-up this vendor's existing `vendor_enrichment` row from the
graph (if `context-graph.db` exists) to populate the digest's description fields, renders
DEPTREE.md/deptree.json/FILETREE.md/filetree.json/CLAUDE.md (+OVERVIEW.md if an
enrichment exists) unconditionally, fully overwriting every file every call —
deterministic, no diffing." Direct match on the technical core. (The claim's own
secondary point — that "digest" is used informally in three overlapping ways in project
*prose* — isn't implementation-checkable and the reconstruction had no doc access; this
doesn't weaken the aligned verdict since the prose-looseness observation isn't
implementation-level to begin with.)

**CL-CTXT-006** (relationship-edge.md's "six edge tables" definition is literally
incomplete against Phase 76 git-topology rows, which satisfy the same wipe/reinsert
lifecycle test; `git_worktrees`/`git_submodules` are architecturally separate from the
six content-edge tables because they connect only to `git_repositories`, never to a
content entity). Reconstruction's schema section independently lists the same six edge
tables by name (`uses_edges`, `documents_edges`, `skill_mentions_edges`,
`routes_via_edges`, `depends_on_edges`, `doc_relations_edges`) and separately,
unprompted, calls out "`git_repositories`, `git_worktrees`, `git_submodules` (Git
topology — fully clear-and-reinsert each rebuild, no cross-rebuild identity)" — and its
`rebuild_deterministic` description explicitly includes "all three git_* tables" in the
same unconditional wipe-and-reinsert set as the six edge tables. This is a strong,
independently-arrived-at confirmation of exactly the schema fact the Claim's whole
argument rests on (same lifecycle, different entity family) — produced by a reconstruction
that had no access to `relationship-edge.md` or this Claim's own reasoning.

### partial

**CL-ADPT-002** (two adapter strategies by design: in-process npm/Python/Cargo vs.
external-process Haskell; decisions/0002 "not superseded" by decisions/0057). The
in-process half is strongly confirmed: `PythonAdapter` is exactly "an importable Python
class inside `src/codecompass/` shelling out to native ecosystem tooling" (pipdeptree,
`importlib.metadata`). The external-process half (Haskell adapter, JSON-Lines subprocess
protocol) has **zero** coverage — `adapters/haskell.py` and `adapters/external_process.py`
were excluded from the export; reconstruction §8 states this explicitly ("npm/cargo/haskell
adapters... deliberately excluded... only inferred call contracts"). No conflict, just an
export gap on one half of the claim.

**CL-ADPT-005** (Ecosystem/vendor/adapter three distinct concepts; `Ecosystem` closed
4-member enum; `VendorConfig(name, ecosystem)`; adapter instance per vendor). The
core-definitions half matches exactly: reconstruction's `core.py` entry: "`Ecosystem`
(`StrEnum`: npm/python/cargo/haskell)," "`VendorConfig` (frozen `name`+`ecosystem`,
nothing else — confirmed by `test_core.py::test_vendor_config_narrowed_to_name_and_ecosystem`
and its frozen-ness test)." The claim's own stated edge case (Haskell monorepo
`_resolve_package_dir` narrowing one `project_root` to multiple vendors) is entirely
outside the export's visibility (haskell.py missing) — insufficiently_verified for that
specific sub-claim only.

**CL-CTXT-001** ("context" has 5 irreducible senses). Sense (1), `context-graph.db` as
"the deterministic SQLite persistence layer of vendors/symbols/edges," is not merely
confirmed but is the reconstruction's single most load-bearing, test-verified finding
(`graph.py`, 2428 lines, 75 passing tests). Senses (2)-(5) (the informal "context
CodeCompass supplies" umbrella, context-packet.md, context-health/use-log/quality-eval,
and the `roadmap-context-curator` agent-name sense) are planning/doc-level concepts the
reconstruction's export never touched — insufficiently_verified for those four, aligned
for the one sense that is implementation-level.

**CL-CTXT-002** (context packet vs. digest: digest is unconditional/every-sync/every-vendor,
context packet is gated/once/human-reviewed). The digest half is the same strong match as
CL-CTXT-005 above. The context-packet half (`planning/knowledge/<slug>/context-packet.md`,
knowledge-curator mode, `design.md` APPROVED gating) is a planning-process artifact with no
`src/` counterpart at all — not something the reconstruction's export could ever confirm or
deny, by design of what was exported. insufficiently_verified for that half.

**CL-CTXT-003** (relationship/edge precisely means one of six typed edge-table rows;
context-gaps entries and doc_relation_enrichment commentary are deliberately NOT edges).
The six-edge-table half is directly confirmed (same table list as CL-CTXT-006 above,
independently named and described as deterministically rebuilt). The two neighbouring-tier
claims — that `planning/context-gaps/` entries never reach `context-graph.db`
(decisions/0051), and that `doc_relation_enrichment` carries no FK to `doc_artifacts` by
design (decisions/0038) — are outside the export: `context-gaps/` isn't `src/`, and while
the reconstruction independently confirms `doc_relation_enrichment` is one of three tables
`rebuild_deterministic` "never touches," it does not specifically discuss (nor was asked to
check) the FK-constraint detail. insufficiently_verified for those two sub-points.

**CL-CTXT-004** ("reference" has 3 senses incl. `doc_artifacts.origin = 'pinned_reference'`
as a graph-level provenance enum value). Sense (a) is directly confirmed: reconstruction's
schema section lists `doc_artifacts`' `origin` CHECK constraint verbatim as "IN
codecompass_tool/codecompass_vendor/third_party/project/vendor_upstream/pinned_reference" —
an exact, independently-arrived-at match including the literal enum value. Senses (b)
(reference projects like Ledgerkit) and (c) (Evidence record citation fields) are
planning/process concepts outside `src/` — insufficiently_verified for those two.

**CL-EVID-011 / CL-EVID-012** (graph-level Evidence/Claim/Observation entity-kind naming
collision with the file-based Phase 54c records; the graph-level candidate design is "not
yet built, not funded, conditional on GATE DD/Priority B"). The claims' own central subject
— a naming collision inside planning documents (`roadmap.md`'s old "Stage E" section,
`conditional-generalisation.md` §2.4) — is not implementation-checkable and the
reconstruction never touched those files, so the collision itself is insufficiently_verified.
However, one load-bearing sub-fact both claims rely on — that these graph-level
Evidence/Claim/Observation-style entity *tables* do not currently exist in `context-graph.db`
— is independently corroborated: the reconstruction's exhaustive, test-confirmed enumeration
of every real table in `_SCHEMA_SQL` (meta, vendors, source_files, source_symbols, symbols,
uses_edges, doc_chunks, doc_artifacts, documents_edges, skill_mentions_edges,
routes_via_edges, depends_on_edges, doc_relations_edges, vendor_enrichment,
symbol_enrichment, doc_relation_enrichment, git_repositories, git_worktrees,
git_submodules) contains nothing resembling a graph-level "claim," "evidence," or
"observation" entity kind. This is a genuine, if narrow, corroboration of the "not yet
built" portion of both claims, surfaced by a process that had no access to either claim's
own reasoning — worth recording as supporting evidence, but it doesn't touch the collision
itself, hence `partial` rather than `aligned`.

### insufficiently_verified (no implementation-level counterpart in the export)

- **CL-ADPT-003** (external adapter wire protocol, JSON-Lines, decisions/0057) —
  `adapters/external_process.py` and the protocol repo were excluded from the export.
- **CL-ADPT-004** ("connector" names nothing in this project) — a corpus-wide absence
  claim covering `docs/`, `architecture/`, `decisions/*`, which the reconstruction's
  export (bounded to `src/`+`tests/`) cannot speak to either way.
- **CL-ADPT-006** ("capability" vs. "feature"; capability is the protocol's own closed
  4-value term) — same `external_process.py`/protocol exclusion as CL-ADPT-003.
- **CL-ADPT-007** ("adapter" itself is ambiguous between `EcosystemAdapter` and a
  "host-output adapter" label in `architecture/overview.md`) — a documentation-terminology
  claim; reconstruction never read `architecture/overview.md` and never applies the
  "adapter" label to `commands.py`/`skill.py`/`index.py` one way or the other (it just
  describes `commands.py`'s actual behaviour factually).
- **CL-ADPT-010** (decisions/0058's "adapter"-spelled repo names are a pre-implementation
  typo vs. the real "adaptor"-spelled repos/submodules) — about ADR/`.gitmodules` history,
  outside the export entirely.
- **CL-ADPT-011** (`ExternalAdapterProcess.initialize`'s `expected_ecosystem` mismatch
  check, `HaskellAdapter._analyze`'s call site) — both named files
  (`adapters/external_process.py`, `adapters/haskell.py`) are confirmed absent from the
  export; reconstruction's own §8 lists exactly these as "could not determine."
- **CL-EVID-001, 002, 004, 005, 006, 007, 010, 013** — the Phase 54c record-model claims
  (Evidence/Observation/Derivation/Decision/Requirement/Invariant definitions, the "five
  noticing mechanisms," the cross-cutting-provenance-shapes claim). All of these concern
  `planning/knowledge/` and `planning/learnings/` record schemas and process — the
  reconstruction's bounded export contained none of `planning/`, by design (it was given
  only a source+test export, specifically to stay model-blind toward documentation/process
  content). Zero subject-matter overlap, not a disagreement.

## Real conflicts found

**None.** Every place the two artifacts cover the same underlying fact, they agree
(the six edge tables, `VendorDigest`'s rendering behaviour, `pinned_reference` as a real
origin-enum value, `EcosystemAdapter`'s method set, git-topology tables' lifecycle). No
case was found where the reconstruction's own run-tested evidence contradicts a Claim's
assertion.

## New gaps surfaced by the reconstruction (not covered by any of the 25 Claims)

These are solid, often test-confirmed findings with no existing knowledge-base counterpart.
None of them contradicts anything in the snapshot; they are simply outside its 25 Claims'
scope (which is weighted toward meta-level concepts, not implementation minutiae). Named
here for `context-researcher`/`knowledge-curator` to consider as fresh Claim candidates if
judged material, not resolved by this report:

1. **`config.py` silently discards a legacy `depth` key from `vendor.toml`** with no
   warning or migration — confirmed by direct code reading, not inferred from a comment.
   A user with a stale config field gets no signal it's ignored.
2. **`discover_python` does not scan `[project.optional-dependencies]`**, and
   **`discover_haskell` does not expand hpack's `when:`-block conditional deps** — both
   stated directly in their own docstrings as known, accepted limitations.
3. **`PythonAdapter.dependency_tree()`'s `dev_only` field is always `False`** — a
   structural ecosystem-tooling limitation (pipdeptree's JSON tree doesn't carry the
   distinction), confirmed live by a passing test (`test_dev_only_always_false`).
4. **Schema migrations are gated by direct introspection (`PRAGMA table_info`,
   `sqlite_master.sql` text), deliberately not by `meta.schema_version`**, because the
   version string was reportedly bumped twice historically for unrelated changes and
   would have falsely triggered migrations. All six migration functions are exercised and
   pass against hand-built pre-migration fixtures.
5. **Symbol names are not globally unique across vendors** — `query symbol NAME`'s own
   behaviour depends on this; no existing Claim states it.
6. **The `promote` CLI command has been removed** (`test_cli.py::test_promote_command_removed`)
   — a confirmed historical surface change with no corresponding Claim.

## What Stage 4 should draw on as primary evidence

The reconstruction is strong, often test-verified primary evidence for implementation-level
documentation the existing 25-Claim corpus simply doesn't cover at this granularity (it was
never meant to — it's meta-level). Recommended for Stage 4 fresh-draft use, organized by the
phase's named audiences:

- **Users**: §2's CLI command surface (bare `codecompass`, `init`, `sync [VENDOR]`,
  `index`, `check`, `query {vendors,vendor,symbol,skills,relations,topology,source,
  source-symbol}`, `chat`, `undo`, `enrich apply`) — read directly from Typer
  decorators/signatures, internally consistent, good basis for a command reference. Pair
  with the config.py `depth`-key gap (item 1 above) as a documented quirk.
  **Caveat for Stage 4**: `cli.py` itself could not be executed in Stage 2's sandbox
  (missing transitive deps); the command surface is confirmed by reading, not running —
  flag this provenance distinction in the draft rather than presenting it as run-verified.
- **Contributors**: §7's extension points (new ecosystem adapter, new CLI command, new
  graph row/table, new manifest discoverer) are concrete, actionable, and grounded in real
  precedent cited by file/test name — strong basis for a CONTRIBUTING-adjacent "how to
  extend" doc.
- **Maintainers**: §3's migration-safety architecture (introspection over version
  comparison, the two migration strategies by data-loss risk, the three
  survives-every-rebuild enrichment tables) — all test-confirmed, none of it currently
  documented anywhere the compared Claims reach. High-value, low-risk material to draft
  fresh from.
- **Coding agents**: the `_graph_session`/`_open_graph_or_note` "graceful note, no
  traceback" pattern and the `enrich apply` mechanical trust-boundary check (rejects any
  entry not matching a currently-pending candidate) are both solid, agent-relevant
  behavioural guarantees worth stating plainly for an agent orienting to this codebase.

Anything touching `enrichment.py`, `relation_enrichment.py`, `chat.py`, `index.py`,
`skill.py`, `source_resolution.py`, `staleness.py`, `filetree.py`, `symbols.py`,
`git_topology.py`, `skill_scan.py`, `source_symbols.py`, `spec_docs.py`, `usage.py`,
`claude_md.py`, `deptree.py`, `doc_mapping.py`, or the npm/cargo/haskell adapters should
**not** be drafted from this reconstruction alone — the reconstruction itself labels these
as inferred call contracts only, not confirmed implementations, since they were deliberately
excluded from Stage 2's export.

## Write-boundary note

No Claim, Derivation, or Decision record was written by this pass. No existing Claim's
`status` was changed or recommended for promotion on the strength of an `aligned`/`partial`
verdict alone — per this role's hard rule, implementation conformance shows the *code*
matches the *stated* assertion, not that a domain rule is itself correct. No new
Observation/Evidence record was produced either: every finding above was resolved by
reading the two already-produced artifacts directly, not by running a new check of my own
against `src/`, so there was nothing to newly attest.
