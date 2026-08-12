# 0027. `EXPLAINS` chunk retrieval coexists with, does not replace, decisions/0023's whole-file chat grounding

## Status

Accepted

## Context

`decisions/0023` deliberately chose whole-file `CLAUDE.md`/`OVERVIEW.md`
concatenation, with no reconstructed digest structure and no structured
read-back path, for the one consumer that existed at the time:
`depcompass chat <vendor>`. Its Alternatives-considered section rejected
building a structured `VendorDigest` read-back "for this phase" on the
grounds that nothing needed it yet, explicitly leaving room for "a later
phase" to decide differently if a real need arose.

Phase 9d (`planning/phase-9d-llm-enrichment.md`) introduces exactly that
kind of need, but for a genuinely different consumer and query shape:
`DocChunk` nodes (a deterministic, heading-level split of each
`DocArtifact`) and `EXPLAINS` edges (`DocChunk → Symbol`, one forced-
tool-use Haiku call per doc artifact, mapping chunks to the symbols they
actually explain and carrying the real excerpt). This is targeted
explanation retrieval — "what does the vendor's own documentation say
about this specific symbol" — a different query shape from `chat
<vendor>`'s general, whole-vendor grounding. Without an explicit decision
here, a future session could read `EXPLAINS`'s existence as silently
superseding `decisions/0023`, which it does not and should not.

## Decision

`chat.py` and `depcompass chat <vendor>`'s behavior are **not modified**
by this plan or by anything in Phase 9. `_build_system_prompt`'s
whole-file `read_text()` concatenation of `CLAUDE.md` + optional
`OVERVIEW.md` remains exactly as `decisions/0023` specified.

`EXPLAINS`/`DocChunk` data is produced and stored inside
`context-graph.json`'s `enrichment` block (`decisions/0024`,
`decisions/0026`) for a **future, not-yet-built** consumer: Phase 10's
project-root chat routing and digest-exceeded escalation (the work
currently described in `planning/ROADMAP.md`'s Phase 10 row, née Phase
9). When that phase is planned, its plan file must state explicitly which
query types use whole-file grounding (unchanged, `decisions/0023`) and
which use chunk-scoped `EXPLAINS` retrieval (new, this ADR) — the two
mechanisms coexist by design, scoped to different consumers, not merged
or chosen-between generically.

## Alternatives considered

- **Retrofit `chat <vendor>` to use `EXPLAINS` chunks instead of
  whole-file text.** Rejected — out of scope for this plan (no request
  to change Phase 8's already-shipped, tested behavior), and would reopen
  a settled ADR (`decisions/0023`) without a settled reason to do so;
  `decisions/0023`'s own Consequences section already anticipated this
  kind of question and left it for "a new, separate design decision," not
  an implicit override.
- **Treat `EXPLAINS` as obsoleting whole-file grounding project-wide once
  it exists.** Rejected — `EXPLAINS` is scoped to targeted-explanation
  queries; general "tell me about this vendor" questions are still
  better served by whole-file context, and forcing every chat consumer
  through chunk retrieval would lose that.

## Consequences

- Two grounding mechanisms exist in the codebase after 9d ships, by
  design: whole-file (`decisions/0023`, `chat <vendor>` only) and
  chunk-scoped (`EXPLAINS`, this ADR, for a future Phase 10 consumer
  only). Any future phase's plan file touching either must state which
  query types it uses, rather than assuming the distinction is obvious.
- `decisions/0023` is not superseded by this ADR — both remain in force,
  governing different consumers.
