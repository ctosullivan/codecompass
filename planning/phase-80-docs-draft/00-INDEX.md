# CodeCompass documentation — fresh draft (Phase 80, Stage 4)

This is a blank-slate documentation proposal written from a bounded,
curated evidence export only: CodeCompass's own approved domain-concept
corpus (25 active Claims, snapshot `codecompass-overview@v1`), an
independent model-blind implementation reconstruction
(`phase80-implementation-reconstruction.md`), and an independent
alignment report comparing the two (`phase-80-alignment-report.md`). No
existing narrative documentation (`README.md`, `docs/`, `architecture/`,
`ai-docs/`) was read, searched, or used as a structural template. Any
resemblance to existing CodeCompass documentation structure is
coincidental, not inherited.

## Documentation architecture selected, and why

Four top-level sections, one per audience named in this dispatch — not
because "four audiences" is a template being filled in, but because the
evidence itself splits cleanly along exactly these lines: the CLI
surface and config schema are what a **user** needs; the extension
points are what a **contributor** needs; the graph schema, migration
strategy, and runtime call chains are what a **maintainer** needs; and
the mechanical trust-boundary/error-handling guarantees are what a
**coding agent** orienting to this codebase needs before it starts
calling things. A fifth, audience-neutral section holds the domain
vocabulary all four audiences share, and a sixth holds limitations and
the provenance/citation discipline that makes the other five
trustworthy.

Within that four-plus-two split, three established documentation ideas
are borrowed selectively — never adopted wholesale as a mandatory
template:

- **Diátaxis's reference / how-to / explanation distinction** (not its
  full four-quadrant grid — no **tutorial** section exists here
  deliberately; see below). The CLI command list is written as
  **reference** (terse, structural, one entry per command). The
  extension-points document is written as a set of **how-to** recipes
  (concrete steps against named files/tests). The concepts document is
  **explanation** (why the vocabulary is shaped the way it is, including
  where it is genuinely unsettled).
- **An arc42/C4-inspired split between a static "building block" view
  and a dynamic "runtime" view** for the maintainer-facing architecture
  material. This is not cosmetic: the static view (schema, tables,
  constraints) and the dynamic view (what actually calls what when a
  user runs `sync`) carry **different confidence levels** in this
  evidence base — the first was confirmed by actually running tests,
  the second was reconstructed by reading code that could not be
  executed in the sandbox that produced it. Separating them into two
  files lets each file carry its own honest confidence label instead of
  blending a run-verified fact and a read-only inference into one
  paragraph.
- **A dedicated provenance/limitations document**, instead of scattering
  caveats per-page or burying them in an appendix. This evidence base has
  unusually sharp and well-documented confirmed/inferred/out-of-scope
  boundaries (see the Stage 2 reconstruction's own §0 and §8); a reader
  deserves to see that whole map in one place, not rediscover it
  piecemeal.

**Why no "tutorial" (Diátaxis's fourth quadrant) is included**: a
tutorial implies a walked-through, narrated first run with real
observed output. `cli.py` could not be executed in the sandbox that
produced the implementation reconstruction (see every file's provenance
banner below) — writing a "first run" narrative would require
inventing output this evidence base cannot back. The CLI reference
(04) states the command surface precisely instead, with its
confirmed-by-reading caveat stated once, loudly, at the top, rather than
dressed up as a lived walkthrough.

## Provenance tiers used throughout this draft

Every file opens with one of these banners, and individual claims inside
a file may carry a tighter tag than the file's own banner:

| Tag | Meaning |
|---|---|
| **CONFIRMED-LIVE** | The reconstruction's Stage 2 agent actually ran this code (`pip install`, `pytest`) in an isolated venv and observed the result directly. |
| **CONFIRMED-BY-READING** | The reconstruction's Stage 2 agent read the real source directly but could not execute it (missing transitive dependencies in the bounded export). |
| **CLAIM-CITED** | Sourced from one of the 25 active Claims in `codecompass-overview@v1`, CodeCompass's own approved domain-knowledge corpus — citations use the form `codecompass-overview@v1#CL-XXX-NNN`. |
| **OUT-OF-SCOPE / INFERRED CONTRACT ONLY** | The module in question (`enrichment.py`, `relation_enrichment.py`, `chat.py`, `index.py`, `skill.py`, `source_resolution.py`, `staleness.py`, `filetree.py`, `symbols.py`, `git_topology.py`, `skill_scan.py`, `source_symbols.py`, `spec_docs.py`, `usage.py`, `claude_md.py`, `deptree.py`, `doc_mapping.py`, or the npm/cargo/haskell adapters) was deliberately excluded from the Stage 2 export. Anything said about it here is a caller-side inferred contract, not a confirmed implementation, and is labelled as such every time it is mentioned. |

## File map

| File | Audience | Primary provenance tier |
|---|---|---|
| `01-concepts.md` | All (shared vocabulary) | CLAIM-CITED |
| `02-cli-reference.md` | Users | CONFIRMED-BY-READING |
| `03-configuration.md` | Users | CONFIRMED-LIVE |
| `04-architecture-persistence.md` | Maintainers (static/building-block view) | CONFIRMED-LIVE |
| `05-runtime-pipelines.md` | Maintainers (dynamic/runtime view) | CONFIRMED-BY-READING |
| `06-extension-points.md` | Contributors | CONFIRMED-BY-READING, grounded in CONFIRMED-LIVE precedent |
| `07-agent-orientation.md` | Coding agents | Mixed, tagged per item |
| `08-limitations-and-provenance.md` | All | Mixed, the explicit map |

## What this draft deliberately does not cover

Per the Stage 3 alignment report's own "Stage 4 guidance" section, this
draft says nothing substantive about the actual behavior of
`enrichment.py`, `relation_enrichment.py`, `chat.py` (beyond the bare CLI
signature), `index.py`, `skill.py`, `source_resolution.py`,
`staleness.py`, `filetree.py`, `symbols.py`, `git_topology.py`,
`skill_scan.py`, `source_symbols.py`, `spec_docs.py`, `usage.py`,
`claude_md.py`, `deptree.py`, `doc_mapping.py`, or the npm/cargo/haskell
adapters' own internal implementations. Where the confirmed code calls
into one of these (it does, constantly), that call is named honestly as
"exists, calls into `<module>`, not independently verified in this
evidence base" rather than guessed at.
