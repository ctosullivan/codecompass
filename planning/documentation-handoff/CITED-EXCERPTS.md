# Cited excerpts from paths excluded by the clean-room allowlist

**Added 2026-10-09, Phase 81B Amendment 4, cold-reader finding #1.**
`CL-CTXT-002` and `CL-CTXT-005` (`knowledge/overview.md`) cite
`vendor/typer/CLAUDE.md` as confirming evidence that a per-vendor digest
is "real, currently-produced output (not only a design description)."
`vendor/` is excluded from your workspace (it is large, fully
regeneratable, and not something a documentation rewrite needs to browse
wholesale) — but a citation you cannot open at all is not independently
verifiable, which defeats the purpose of citing it. This file exists so
you *can* verify this specific citation, without the rest of `vendor/`
being exposed.

This is the complete, real, current content of that exact file — copied
verbatim, not summarised or reconstructed — so you can judge for
yourself whether it matches what the Claims above say it shows.

## `vendor/typer/CLAUDE.md` (full file, as of `documented_revision` `47c9ce7`)

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

Note what this excerpt does and does not establish: it confirms the
*shape* the Claims describe (a `## Metadata` / `## Grounding` /
`## Public API surface` / `## Known gotchas` / `## Quick links`
structure, generated per-vendor) is real and present on disk for at
least this one vendor. It does not, by itself, prove every vendor's
digest always has this exact shape, or that `FILETREE.md`/`DEPTREE.md`
(referenced but not themselves excerpted here) exist and match — if your
own documentation makes a broader claim than "this specific file, for
this specific vendor, looks like this," say so explicitly rather than
generalising past what this excerpt actually shows.
