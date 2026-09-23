# Protocol / adapter integration (proposed, current-state-only)

**Status: shadow proposal, Phase 64 (Cluster B).** Not yet applied to
`docs/`. Comparing this against `docs/external-adapters.md`'s own current
content and deciding retain/rewrite/consolidate/split/replace/remove is
Phase 65's job.

This set is written for a different audience than
`../architecture/adapter-interface.md`: not someone reading CodeCompass's
own internals, but someone **integrating a new external-process adapter**
with CodeCompass, or auditing what the existing Haskell reference adapter
actually does over the wire. Everything here is grounded in the real,
checked-out submodules present in this working tree
(`protocol/codecompass-adaptor-protocol/`, `adapters/haskell/`) plus
`decisions/0057`-`0059` and `src/codecompass/adapters/external_process.py`
— not re-derived from `docs/external-adapters.md`'s own current prose
(which was read only afterward, to check it against the real code, and is
in fact already substantially accurate — see the note at the bottom of
`wire-protocol.md`).

**Domain terminology exception**: "adapter," "protocol," "capability,"
and "ecosystem" are not redefined here — see `docs/domain/concepts/`
(`adapter.md`, `protocol.md`, `capability.md`, `ecosystem.md`) for their
settled meaning.

## Contents

1. [`wire-protocol.md`](wire-protocol.md) — the actual message shapes
   (`initialize`, `analyze_project`, `shutdown`), the closed
   method/capability/error-code sets, versioning, and where the
   canonical specification now lives.
2. [`integrating-a-new-external-adapter.md`](integrating-a-new-external-adapter.md)
   — a practical guide: what `src/codecompass/` expects from a new
   external-process adapter, what `ExternalAdapterProcess` does and
   doesn't do for you, and how the reference Haskell adapter is wired in
   as a worked example.

## What this set deliberately does not cover

- The in-process adapter strategy (npm/Python/Cargo) — that's
  `../architecture/adapter-interface.md`.
- CLI-level instructions for cloning/building the Haskell submodule as an
  end user — that already exists, is current, and is not being
  reconstructed here: `docs/external-adapters.md`. See the note in
  `wire-protocol.md` for what this proposal found when checking that
  file against the real code.
- Any change to the protocol's own schemas or the Haskell adapter's own
  source — both are separate, independently-versioned public
  repositories (`decisions/0058`); this proposal only describes their
  current, already-released (`0.1.0`) content.
