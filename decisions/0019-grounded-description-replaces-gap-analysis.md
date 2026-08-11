# 0019. Grounded description replaces gap analysis for FULL-depth generation

## Status

Accepted

## Context

`FULL`-depth generation currently works via `depcompass.gap_analysis`
(`decisions/0003`, Phase 5): a single forced-tool-use Haiku call
comparing a vendor's extracted API surface against how the *consuming
project* describes its own needs, supplied via a project-provided
`context_path` (typically its README or a spec file) — see
`architecture/overview.md`'s "Gap analysis" section and
`planning/phase-5-gap-analysis.md`. The call requires `context_path`;
without it, "the model has no basis to judge what counts as a 'gap'"
(`architecture/overview.md`), so `FULL` depth is currently unavailable
for any vendor in a project that doesn't already have a well-written
`context_path` pointed at it.

This is a real adoption blocker for depth escalation via `promote`
(`decisions/0018`): the reactive-promotion story — "run `promote` when
you actually need more" — shouldn't additionally require the consuming
project to already have a spec document written and wired up. Separately,
gap analysis's output is inherently project-specific narrative ("gaps
for this project's stated usage"), which fits poorly with per-vendor
Skills (`decisions/0013`) and the REPL (`decisions/0012`), both of which
want a vendor-general description of what a dependency actually does,
not a comparison scoped to one consuming project's README.

*Note on an earlier framing of this reversal:* drafting for this
decision initially assumed gap analysis compared a dependency's source
against the model's own training-knowledge self-assessment. No such
mechanism exists anywhere in this codebase — the Context above describes
the actual mechanism being replaced.

## Decision

`promote` (`decisions/0018`) generates `FULL`-depth content as a
description grounded entirely in material retrieved at promote time —
via source resolution (`decisions/0021`) — rather than a `context_path`
comparison. The generated content covers: what the dependency does, its
core concepts and data model, and explicit references into the retrieved
source and docs, in the existing dual-audience (technical +
conversational, `decisions/0012`) format. `context_path` is no longer
required for `FULL` depth and is removed from `vendor.toml`'s schema.
The AI call's task narrows from "compare X against Y" to "describe what
was retrieved" — same model tier (`decisions/0003`, unaffected), same
cost posture, different prompt, different (vendor-general rather than
project-specific) inputs and outputs.

## Alternatives considered

- **Keep gap analysis's `context_path`-gated comparison as-is, adding
  grounded description as a separate, additional output.** Rejected —
  running both doubles AI cost per `FULL` vendor for overlapping value,
  and keeping `context_path` around as an optional add-on preserves the
  exact adoption friction this decision removes.
- **Retain `context_path` as optional, used to bias grounded description
  toward what the consuming project needs when supplied.** Deferred, not
  rejected — a reasonable future refinement, but it adds a second
  input-shape/prompt variant to design and test in the same phase that's
  already introducing the core mechanism change. Worth revisiting once
  grounded description ships and is validated on its own.

## Consequences

- `vendor.toml`'s `context_path` field is removed. No external
  `vendor.toml` files exist yet outside this repo's own use, so this is
  a clean removal with no migration story needed.
- `gap_analysis.py` is retired and replaced by a new module for grounded
  generation (naming decided in `planning/phase-7-bootstrap-and-
  promote.md`) — the `_call_anthropic` seam and `decisions/0016`'s
  never-call-the-live-API testing constraint carry forward unchanged.
- `architecture/overview.md`'s "Cost model" and "Gap analysis" sections
  need rewriting to describe the new mechanism and its trigger point
  (`promote`, not `sync`).
- `decisions/0003` (Haiku model tier) stays Accepted, unmodified — this
  decision does not touch model choice, only what the model is asked to
  do and what it's given to work with.
- `decisions/0005` (severity-aware staleness) and `check`'s staleness
  logic are unaffected — staleness is a separate semver-diff mechanism,
  unrelated to `FULL`-depth generation's content mechanism.
