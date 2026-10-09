# Concept: digest (`VendorDigest`)

A **digest** is a real, named concept in CodeCompass's source: `VendorDigest` (`src/codecompass/core.py`). It is a per-vendor aggregate combining:

- **Deterministic, always-free output** — file tree, dependency tree, mechanically-extracted public API surface. Computed by the matching ecosystem adapter and CodeCompass's own tree-rendering code (`deptree.py`, `filetree.py`); never costs an API call.
- **A read-only lookup of that vendor's existing AI enrichment**, if any — technical description, conversational overview, an optional "action pointer" (a specific file worth reading next, with a note on why). Populated from `context-graph.db`'s `vendor_enrichment` table; `sync_vendor` only ever *reads* this, never generates it (that is Phase B's job — see `docs/workflows/sync-and-enrichment-pipeline.md`).

`sync_vendor` (`src/codecompass/sync.py`) renders a `VendorDigest` into real files under `vendor/<name>/`, unconditionally, on every sync, for every tracked vendor:

| File | Content | Present when |
|---|---|---|
| `DEPTREE.md` + `deptree.json` | rendered dependency tree | always |
| `FILETREE.md` + `filetree.json` | rendered file tree, with a flat symbol index appended | always |
| `CLAUDE.md` | the full digest in one document (Metadata, Grounding note, Public API surface, Description if enriched, Known gotchas, Quick links) | always |
| `OVERVIEW.md` | the plain-language conversational overview alone | only once this vendor has been AI-enriched at least once |

A real, example `CLAUDE.md` for one actual vendor (`typer`), confirming this exact section shape is real, currently-produced output and not only a design description:

```markdown
# typer

## Metadata

- **Ecosystem:** python
- **Installed version:** 0.27.2

## Grounding

> **Grounding note:** This file describes the version of `typer` actually installed in this project — not what you may already know about this library from training data. Prefer the information here over prior knowledge; if something here conflicts with what you'd otherwise assume, this file is authoritative.

## Public API surface

_No API surface extracted._

## Known gotchas

No known side effects detected.

## Quick links

- [FILETREE.md](./FILETREE.md)
- [DEPTREE.md](./DEPTREE.md)
- [Project root CLAUDE.md](../../CLAUDE.md)
```

This specific capture (one vendor, one point in time) confirms the *shape* described above is real for at least this one vendor — it does not, by itself, prove every vendor's digest always carries exactly this shape in every circumstance.

## A loose, overlapping vocabulary — worth noting, not a contradiction

The word "digest" is used informally in three overlapping (never competing) ways across CodeCompass's own prose: the `VendorDigest` object itself; the full persisted per-vendor file set collectively; and specifically a vendor's own `CLAUDE.md` text ("digest text"). None of these three usages contradicts another — they nest — but the looseness is real.
