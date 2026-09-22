---
status: DRAFT — pending domain-skeptic review and actual-user approval
---

# Digest

## Definition

A **digest** is a real, named code concept: `VendorDigest`
(`src/codecompass/core.py:66-103`), "the aggregate output of generating
a single vendor's documentation" — combining deterministic, always-free
fields (`file_tree`, `dep_tree`, `api_surface`, populated by tree
generation and adapters, no AI involved) with a read-only lookup of that
vendor's *existing* AI enrichment (`technical_description`,
`conversational_overview`, `action_pointer_file`, `action_pointer_note`
— sourced from `vendor_enrichment`, never generated fresh inside digest
construction itself).

`sync.py`'s `sync_vendor` constructs exactly one `VendorDigest` per
vendor per whole-project `sync`, unconditionally, for every tracked
vendor, and renders it into a fixed set of files under
`vendor/<name>/`: `DEPTREE.md`/`deptree.json`, `FILETREE.md`/
`filetree.json` (with an embedded Symbol index section),
`OVERVIEW.md` (only if `conversational_overview` is set), and
`CLAUDE.md` (via `render_vendor_claude_md(digest)`) — six fixed
sections: Metadata, Grounding preamble, Public API surface, Description
+ action pointer, Known gotchas, Quick links (`CL-CTXT-005`,
`EV-CTXT-009`). This is confirmed as real, currently-produced output —
not only a design description — by a real generated file on disk in
this exact repository, `vendor/typer/CLAUDE.md`, matching the described
rendering section-by-section for a vendor with no enrichment yet
(`EV-CTXT-014`).

This project's own root `CLAUDE.md` literally uses the phrase
"**generated reference digest**" for this artifact (`EV-CTXT-010`) — a
real, in-the-wild co-occurrence of two of this cluster's own concepts
describing the exact same thing.

## What this is NOT — specifically vs. a context packet

**This is the distinction Phase 63D's own brief explicitly requires a
dedicated page for.** A digest and a context packet
(see [`context-packet.md`](context-packet.md)) are both, informally,
"a bundle of context for an agent" — but produced by very different
mechanisms, for different purposes, at different points in the
project's own lifecycle:

| | Digest | Context packet |
|---|---|---|
| Produced by | `sync_vendor` (deterministic rendering + a read-only enrichment lookup) | `knowledge-curator` (a curation/compaction step over structured records) |
| Trigger | Every whole-project `sync`, unconditionally, for every tracked vendor | Once per feature, only after that feature's `design.md` reaches `status: APPROVED` |
| Storage | `vendor/<name>/CLAUDE.md`, `FILETREE.md`, `DEPTREE.md`, `OVERVIEW.md` (+ JSON sidecars) | `planning/knowledge/<feature-slug>/context-packet.md` |
| Cost | Free (deterministic parts); enrichment parts are pre-existing, cached, AI-authored content it reads, never generates fresh | Free (compaction of already-written records) |
| Gate | None — regenerated every sync, no review step | Gated on human/lead `APPROVED` review of `design.md` |
| Audience | Any agent working with this vendor as a dependency | A coding agent implementing one specific, already-designed feature |
| Regeneration | Automatic, every sync | Manual/curated, once, unless the feature's own knowledge base changes |

Neither is a generalisation of the other. A digest never carries a
`REQ-`/`DEC-`/`CL-` citation trail; a context packet never renders a
dependency tree or an API surface.

## Other things "digest" is NOT

- **Not the project-root `CLAUDE.md`'s vendor routing table.**
  `index.py`'s own module docstring self-describes as "Idempotent
  routing-table injection into the project root `CLAUDE.md`" — a
  string-injection mechanism that lists each tracked vendor and links to
  its already-written digest, never itself constructing or rendering a
  `VendorDigest`. The project-root `CLAUDE.md`'s vendor table and a
  per-vendor `vendor/<name>/CLAUDE.md` are two different mechanisms that
  happen to share a filename (`EV-CTXT-013`).
- **Not `context-graph.db`.** A digest reads one row of
  `vendor_enrichment` for its enrichment fields, but is otherwise
  rendered from tree-walk/adapter output, never a database export of the
  graph itself.

## Invariants

- A digest is regenerated on every `sync` for every tracked vendor,
  unconditionally — there is no "stale digest, skip regeneration" path.
- The deterministic portion of a digest (`file_tree`/`dep_tree`/
  `api_surface`) never depends on whether AI enrichment has ever run for
  that vendor; the enrichment portion is read-only and never generated
  as part of digest construction itself (that is `codecompass.
  enrichment`'s own, separately-triggered job).
- `VendorDigest` never carries staleness information itself —
  `codecompass.staleness` reads persisted per-vendor `CLAUDE.md` files
  directly rather than building a `VendorDigest` for that purpose.

## Example

`vendor/typer/CLAUDE.md` (this exact repository, this exact revision):
Metadata (`Ecosystem: python`, `Installed version: 0.27.2`), Grounding
preamble (fixed instructional text), Public API surface
(`_No API surface extracted._`), Known gotchas
(`No known side effects detected.`), Quick links
(`./FILETREE.md`, `./DEPTREE.md`, `../../CLAUDE.md`) — a real digest for
a vendor with no enrichment record yet.

## Counterexample / fuzzy boundary

**Genuinely fuzzy — the word "digest" itself, informally.** Across
`CLAUDE.md`, `docs/cli-reference.md`, and `architecture/overview.md`,
"digest" is used in at least three overlapping-but-not-identical
informal ways, with no single passage defining all three side by side
(`EV-CTXT-010`):

1. the `VendorDigest` dataclass itself (an in-memory Python object);
2. the full persisted per-vendor file set collectively (`CLAUDE.md` +
   `FILETREE.md` + `DEPTREE.md` + `OVERVIEW.md` + JSON sidecars) — e.g.
   root `CLAUDE.md`'s "generated reference digest under `vendor/<name>/`";
3. specifically the vendor's own `CLAUDE.md` file's *text* — e.g.
   architecture/overview.md's "vendor's own digest text", and
   `docs/cli-reference.md`'s description of `codecompass chat` as
   "digest-only," "grounded on persisted digest files
   (`vendor/<name>/CLAUDE.md`, plus `OVERVIEW.md`...)".

None of these three usages contradicts another — they are nested (2 is
the persisted form of 1; 3 is one file within 2) — but the looseness is
real. Whether the project wants to tighten this informal vocabulary is a
style/terminology question, not a factual one, and is left open rather
than resolved here (`docs/domain/open-questions.md`).

## Relationships

- **Distinct from**: [`context-packet.md`](context-packet.md) (see
  table above), [`context.md`](context.md) (a digest is one concrete
  instance of "the context CodeCompass supplies to an agent," sense 2 —
  never a synonym for the whole umbrella).
- **Reads from (read-only)**: `vendor_enrichment`
  (`context-graph.db`) for its enrichment fields.
- **Adjacent to, but not the same as**: the project-root `CLAUDE.md`'s
  own vendor routing table (`index.py`).

## References

- `CL-CTXT-005` / `DE-CTXT-005` — `planning/knowledge/codecompass-domain/`
- `EV-CTXT-006`, `EV-CTXT-009`, `EV-CTXT-010`, `EV-CTXT-013`,
  `EV-CTXT-014` — `planning/knowledge/codecompass-domain/`
- `src/codecompass/core.py:66-103` (`VendorDigest`)
- `src/codecompass/sync.py:160-202` (`sync_vendor`)
- `src/codecompass/claude_md.py` (`render_vendor_claude_md`)
- `src/codecompass/index.py:1,77,117` (project-root routing-table
  injection — the adjacent-but-distinct mechanism)
- `architecture/overview.md:397-576`
- `CLAUDE.md:167` (this session's own governing file)
- `docs/cli-reference.md:9,320-330`
- `vendor/typer/CLAUDE.md:1-25` (real worked example)
