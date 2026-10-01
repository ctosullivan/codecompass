# Phase 80 Stage 5 — Reconciliation report

**Role**: `docs-maintainer`, legacy reconciliation mode.

**Inputs compared**: the fresh, isolated Stage 4 draft
(`planning/phase-80-docs-draft/00-INDEX.md` through
`08-limitations-and-provenance.md`), the Stage 3 alignment report
(`planning/knowledge/codecompass-domain/phase-80-alignment-report.md`),
against the real, live, published documentation (`README.md`, `docs/`
including `docs/domain/`, `architecture/`, `ai-docs/`).

## Method

For every substantive claim the fresh draft makes, grepped the full
repository (not just one file) for the governing symbol name, test name,
or exact phrasing, then read the matching existing-doc passage in full
to classify it. Checked, specifically: the `promote` removal, the legacy
`depth` key, `dev_only` always `False` for `PythonAdapter`, schema
migrations gated by introspection not `meta.schema_version`, symbol
names not globally unique across vendors, the six content-edge tables
vs. the three git-topology tables, `Ecosystem`/`VendorConfig`/adapter
definitions, `VendorDigest` vs. context-packet, the `_graph_session`
"open-or-note" pattern, `enrich apply`'s trust-boundary check, and both
named manifest-discovery limitations (`optional-dependencies`, hpack
`when:`-blocks).

## Findings and classification tally

| Classification | Count |
|---|---|
| `supported` | 11 |
| `stale_or_contradicted` | 0 |
| `rationale_requiring_verification` | 0 (out of scope by design) |
| `useful_example` (acted on) | 1 |
| `obsolete` | 0 |

This matches Stage 3's own independent finding of zero real conflicts
between the knowledge-base snapshot and the model-blind reconstruction.
Everywhere the fresh draft and the existing docs overlap, they already
agree — `README.md`, `docs/cli-reference.md`, `docs/config-schema.md`,
`architecture/context-graph-schema.md`, `architecture/adapter-interface.md`,
`architecture/core-data-model.md`, and `architecture/overview.md` already
state, in their own existing words: the `promote` removal (Phase 15,
`decisions/0033`); the legacy `depth` key's silent-discard behavior
(`decisions/0031`); `PythonAdapter.dependency_tree()`'s `dev_only` always
`False` (stated nearly word-for-word, including the "structural
difference from npm, not an oversight" framing); the six-content-edge-
table / three-git-topology-table architectural split; the
introspection-over-`schema_version` migration strategy, including the
"bumped twice historically" rationale and all three migration-strategy
variants; symbol names not being globally unique across vendors (stated
for both `query symbol` and `query source-symbol`); and the
`optional-dependencies` discovery gap. `architecture/overview.md:69`
already states "five abstract methods" correctly, so the reconstruction's
own internal "four" miscount (flagged by Stage 3 as a note for Stage 4,
not a finding against the snapshot) never propagated into any published
doc — nothing to fix.

One genuine, narrow gap (`useful_example`, acted on): the existing
`init --scan` limitations bullet in `docs/cli-reference.md` documented
the Python `[project.optional-dependencies]` discovery gap but had no
parallel bullet for the structurally identical Haskell gap — hpack's
`when:`-block conditional dependencies are not expanded by
`discover_haskell`, a limitation stated directly in that function's own
docstring (`src/codecompass/discovery.py`) but never surfaced in any
user-facing doc. This affects both `init --scan` and bare `codecompass`'s
auto-discovery (both route through the same discoverer).

## File changed

- `docs/cli-reference.md` — added one bullet, immediately after the
  existing Python optional-dependencies bullet in the `init --scan`
  section, documenting the Haskell `package.yaml`/hpack `when:`-block
  conditional-dependency gap, framed consistently with its sibling
  bullet ("documented, accepted gaps ... not bugs").

No other file was touched. `docs/domain/`'s concept corpus was not
touched — every concept the draft's `01-concepts.md` states is itself
cited directly from that same already-approved corpus (`CL-ADPT-*`,
`CL-CTXT-*`, `CL-EVID-*`), so there was nothing independent to reconcile
it against; no disagreement was found to flag.

## Verification

`python scripts/check_user_docs.py --strict` → `check_user_docs: no
findings` (run after the edit).

## Architecture/overview.md split candidates for Phase 65-style work

None newly surfaced by this pass. The draft's own arc42/C4-style static/
dynamic split (`04-architecture-persistence.md` vs.
`05-runtime-pipelines.md`) is a Stage-4 structural choice for the
isolated draft, not a finding that `architecture/overview.md` itself
currently narrates history inline in a way this pass is positioned to
judge — out of scope for Stage 5, no action taken.
