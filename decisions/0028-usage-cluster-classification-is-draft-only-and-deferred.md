# 0028. Usage-cluster classification is draft-only, never auto-written, and deferred to a future 9e

## Status

Accepted

## Context

Alongside Phase 9d's other enrichment (usage-purpose labels, clustering,
a `DOCUMENTS` quality delta, file-role summaries, the trigger-accuracy
proxy — all governed by `decisions/0026`), a further idea was brainstormed:
for a usage cluster where `EXPLAINS`/`DOCUMENTS` coverage is thin relative
to `USES` volume, classify the cluster as vendor-API-shaped vs.
project-domain-shaped, and — if domain-shaped — propose a project-level
Skill that doesn't belong to any single vendor (e.g. a project parses a
file format a tracked library implements but doesn't fully document as
its own concern).

This carries a different, higher risk than the rest of 9d. A mislabeled
usage-purpose or a slightly-off cluster label costs little — it's just a
somewhat-wrong annotation. A wrong Skill *suggestion* costs a person real
time if they act on it (building an unnecessary Skill). That asymmetry
means this feature needs its own artifact-location and confidence-gating
decisions, and shouldn't inherit 9d's general "optional, deterministic-
gated" posture (`decisions/0026`) as if it were a uniform bucket with
usage-purpose labeling.

Separately: no top-level `skills/` directory exists anywhere in this
repository, or in Claude Code's own convention. Skills live at
`.claude/skills/<name>/SKILL.md` — confirmed by the two Skills that
already exist here, `.claude/skills/depcompass/` (tool-level,
`decisions/0020`) and `.claude/skills/depcompass-rich/` (per-vendor,
`decisions/0013`). A brainstormed "top-level `skills/` directory
alongside `vendor/`" for a draft, non-vendor-specific Skill would invent
a location Claude Code doesn't look at.

## Decision

1. **Not part of 9d's initial pass.** This feature is scoped here as a
   future sub-phase, **9e**, sequenced strictly after 9d ships and
   produces real field data. The ratio-gate threshold (deciding when
   `EXPLAINS`/`DOCUMENTS` coverage is "thin enough" to warrant the
   classification call) and the confidence calibration both need actual
   usage patterns from a real 9d rollout to tune against, not a guess
   made before any of that data exists. No `planning/phase-9e-*.md` is
   written in this planning session — writing an implementation plan
   for it now would be planning ahead of the field data it depends on.
2. **Never written to disk by depcompass, at any confidence level.** A
   proposed Skill exists only as structured data inside
   `context-graph.json`'s `enrichment` block. It is not staged as a
   draft file anywhere — not under a top-level `skills/` directory, not
   under `.claude/skills/`, nowhere. Once a surfacing consumer exists
   (Phase 10), the suggestion is presented as a chat-level message; a
   human who wants to act on it creates `.claude/skills/<name>/SKILL.md`
   themselves, using the suggested `name`/`trigger_hint` as a starting
   point if they choose to.
3. **Confidence gates proactive surfacing, not computation.**
   Classification always runs when the deterministic ratio gate fires
   (per `decisions/0026`'s batching discipline — never on every cluster
   unconditionally) and its result is always stored. Once a surfacing
   consumer exists, proactive presentation requires confidence ≠ `low`.
   `low`-confidence results are computed and retained, queryable on
   request, but not pushed — they should read as "worth a look," never
   as "you should build this."

## Alternatives considered

- **A top-level `skills/` staging directory for drafts** (the
  brainstorm's own working assumption). Rejected — invents a location
  neither Claude Code nor this repository's existing convention
  recognizes; a draft sitting somewhere no tool reads provides no real
  value over not writing a file at all, while still adding filesystem
  clutter and a false sense of "this is a real artifact."
- **Auto-write the SKILL.md directly when confidence is `high`.**
  Rejected outright — this feature's entire risk profile is that a wrong
  suggestion costs a person real time; auto-writing removes the human
  decision point this ADR exists to preserve, regardless of confidence.
- **Fold this into 9d's initial pass since it was brainstormed
  alongside the same features.** Rejected — see Context above; treating
  it as a uniform part of 9d would understate its distinct risk and
  artifact-location requirements, which is exactly what this ADR and the
  brief's own instructions call out separately.

## Consequences

- 9d ships without this feature. `planning/ROADMAP.md` gets a 9e row
  (`not started`, no plan file) so the idea isn't lost, not silently
  dropped.
- When 9e is eventually planned, its plan file must cite this ADR for
  the artifact-location and draft-only constraints, and should record
  the actual ratio-gate threshold and confidence calibration chosen,
  informed by real 9d usage data rather than a guess.
