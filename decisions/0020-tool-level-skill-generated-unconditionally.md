# 0020. Tool-level Skill, generated unconditionally

## Status

Accepted

## Context

`decisions/0013` established per-vendor Skills, gated to `depth = FULL`
vendors only, since a `SURFACE` vendor has no gap-analysis (now grounded-
description, `decisions/0019`) content to build a meaningful trigger
description from. That leaves a gap: a project with zero `FULL` vendors —
the common case immediately after `decisions/0017`'s zero-question
bootstrap, before anyone has run `promote` — has no Skill at all
describing depcompass itself. There is no mechanical signal to an agent
working in the project that depcompass exists, what commands it offers,
or that `promote` is the tool's own escalation/cost entry point. The
root `CLAUDE.md` routing table (`index`, Phase 4) already carries this
information for tools that read `CLAUDE.md`, but per `decisions/0013`'s
own reasoning, a routing-table instruction competes for attention with
everything else in context, whereas a Skill's name+description is
mechanically part of Claude Code's own relevance-loading logic.

## Decision

Generate one tool-level Skill (distinct from any per-vendor Skill) at a
fixed location, `.claude/skills/depcompass/SKILL.md`, unconditionally —
regardless of vendor count or depth, including immediately after a
zero-question bootstrap with every vendor at `SURFACE`. Content is
templated, not AI-generated: depcompass's own commands (`sync`, `index`,
`check`, `promote`) and the current vendor list (name, ecosystem, depth)
read from `vendor.toml`. Regenerated on every `index` run — the same
trigger as the root `CLAUDE.md` routing table — so it never goes stale
relative to `vendor.toml`'s actual state.

## Alternatives considered

- **Only generate the tool-level Skill once at least one vendor is
  `FULL`**, mirroring per-vendor Skill gating. Rejected — the tool-level
  Skill's whole purpose is to be the mechanical signal that depcompass
  exists *before* anyone has promoted anything; gating it the same way
  as per-vendor Skills defeats that purpose for exactly the zero-question
  bootstrap state `decisions/0017` makes the common case.
- **Fold this into the root `CLAUDE.md` routing table instead of a
  separate Skill file.** Rejected — `decisions/0013`'s reasoning (Skills
  load progressively and are mechanically part of relevance-selection;
  routing-table text is a soft instruction) applies identically here;
  there's no reason to give depcompass's own discoverability a weaker
  mechanism than vendor discoverability gets.

## Consequences

- `index.py` gains a new templated-generation responsibility alongside
  its existing routing-table update; no AI call, so no cost or
  test-mocking implications beyond ordinary unit tests.
- Naming collision risk: the tool-level Skill's directory
  (`.claude/skills/depcompass/`) must not collide with any per-vendor
  Skill's `.claude/skills/depcompass-<vendor>/` naming (`decisions/0013`)
  — it doesn't, since every per-vendor Skill name carries a `-<vendor>`
  suffix, but this is a naming invariant to preserve deliberately, not
  incidentally.
- `docs/cli-reference.md` gains a short description of this file's
  existence and regeneration trigger.
