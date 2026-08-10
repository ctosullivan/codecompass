# 0013. Agent Skills as the shared context-selection source for multi-tool export, REPL routing, and REPL escalation

## Status

Accepted

## Context

Phase 9 originally scoped multi-tool export as: `CLAUDE.md` (source of
truth) plus a generated Cursor `.mdc` sibling, since Cursor doesn't read
`CLAUDE.md` natively. Separately, a reliability concern was raised about
Claude Code's project-root consumption mode
(`architecture/overview.md`'s "Two consumption modes" section): the root
`CLAUDE.md` routing table's "consult this vendor's digest first"
instruction is a soft instruction competing for attention with everything
else in context — the agent may answer from training knowledge without
reading the digest at all, especially for well-known libraries it feels
confident about. This is precisely the failure mode depcompass exists to
prevent, and instruction-following alone doesn't guarantee it won't happen.

Investigating Claude Code's Skills system surfaced a mechanism that
addresses this directly rather than relying on softer prompting:

- Skills live at `.claude/skills/<name>/SKILL.md`, auto-discovered by
  Claude Code with no per-request registration needed.
- Loading is progressive across three levels: every skill's name and
  short description is loaded into context automatically at session
  start (cheap — a handful of tokens per skill); the full body loads only
  once Claude judges the skill relevant to the current task (or it's
  invoked directly); any bundled supporting files load only when actually
  referenced.
- Content that isn't accessed costs nothing — a skill can bundle large
  reference material with zero token penalty for the unused parts.
- Skills follow the Agent Skills open standard (released as a public spec),
  which other tools beyond Claude Code have begun adopting — making it a
  potentially more portable export target than a Cursor-specific format.

The key structural difference from the `CLAUDE.md` routing table: a
skill's description is mechanically part of how Claude decides what's
relevant to load, not one instruction sentence among many competing for
attention in a large context. That's a stronger (though not absolute)
guarantee of being considered than the current routing-table approach
alone provides.

**A second, related problem surfaced separately**: the REPL (Phase 8) has
its own independent Tier 1/Tier 2 context-selection logic — custom
name/alias matching, then AI-classification fallback — solving the same
underlying "what context is relevant to this question" problem that
Skills triggering solves for Claude Code natively. Built and tuned
independently, these two systems will drift: refining a vendor's Skill
description during Phase 9's trigger-accuracy evaluation wouldn't
automatically improve the REPL's Tier 1 matching, since they'd be reading
separate data with separate logic. Additionally, the REPL has no defined
behavior when a question genuinely exceeds what a digest covers — it would
currently just answer confidently from incomplete context, the same
over-trust risk already flagged for digest-only answers generally.

## Decision

1. Generate one Skill per `depth = FULL` vendor, at
   `.claude/skills/depcompass-<vendor>/SKILL.md`. The trigger description
   is built from data depcompass already generates — the routing table's
   "Consult when" column plus a condensed form of the gap-analysis summary
   — not new content generation from scratch. **Description length is a
   real tuning knob, not free**: every skill's name+description loads into
   every session's context unconditionally, for every vendor, so a long
   description that maximizes one vendor's trigger accuracy has a real
   (if small) per-vendor cost that compounds across a project with many
   `FULL`-depth vendors. Aim for the shortest description that still names
   concrete, specific trigger surfaces (API methods, file/function names,
   the exact situations that matter) rather than vague category language —
   specificity, not length, is what drives triggering accuracy; a first
   real example (`depcompass-turndown`) ran to roughly 80 words to hit
   that bar, which is a starting reference point, not a hard target.
2. Bundle `FILETREE.md` and `DEPTREE.md` as `references/` files inside the
   skill folder rather than inlining them into the main body — this maps
   directly onto progressive disclosure: the trees only cost tokens when
   Claude actually needs to navigate source, not on every trigger.
3. Optionally bundle a small wrapper script that shells out to
   `depcompass check <vendor>` at trigger time, so a live staleness read
   backs the skill's answer rather than a potentially stale cached line —
   deferred to a later phase, not required for the initial Skills export.
4. Skills become the **primary** multi-tool export target going forward,
   given the open-standard portability. The Cursor `.mdc` export is
   **retained, not replaced** — Cursor's glob-scoped file-pattern
   activation is a different (and in some cases more precise) trigger
   model than Skills' description-matching, and some Cursor users may not
   have Skills support depending on version/configuration.
5. The `CLAUDE.md` root routing table is **retained, not replaced** —
   it remains the fallback for any tool or context that doesn't support
   Skills at all (including the Mode-1 standalone `cd`-into-vendor
   scenario, which isn't a "current task the agent judges relevant"
   situation the way Skills triggering assumes).
6. **The REPL's Tier 1 routing (Phase 8) consumes the same generated
   Skill description text as its match corpus**, rather than maintaining
   independently-authored keyword/alias lists. One source of truth for
   "what fires on what," tuned once via Phase 9's trigger-accuracy
   evaluation, benefiting both Claude Code's native triggering and the
   REPL's routing. Practically: Phase 8's Tier 1 implementation should be
   written to read from the same underlying digest data structure that
   Phase 9's Skill-description generation reads from — whichever phase is
   built first, the other should refactor to share that source rather than
   duplicate it. This is a real sequencing consideration for the two
   phases' plan files (see Consequences).
7. **The REPL gets an explicit escalation path** for questions judged to
   exceed digest-only scope (deep source inspection, execution, reasoning
   beyond what a digest captures) — rather than answering confidently from
   incomplete context. On escalation, the REPL states the limitation and
   points at the already-generated `.claude/skills/depcompass-<vendor>/`
   folder as the handoff artifact for a full Claude Code session, which
   is already grounded via the same Skill. This reuses Phase 9's output
   rather than inventing a separate context-packaging mechanism — the
   escalation is "go use this skill in a fuller session," not "assemble
   and transmit context somewhere new."

## Alternatives considered

- **Rely solely on the `CLAUDE.md` routing table.** Rejected — this is the
  status quo the reliability concern was raised against; instruction-
  following alone is probabilistic, not guaranteed.
- **Cursor `.mdc` as the primary export target.** Rejected — tool-specific
  by construction, whereas Skills is an open standard with broader
  adoption potential.
- **Generate Skills for all vendors regardless of depth.** Deferred, not
  rejected outright — `depth = SURFACE` vendors have no gap-analysis
  content to build a meaningful trigger description from; worth
  revisiting with a templated (non-AI-generated) description once the
  `FULL`-depth version is validated.
- **Keep the REPL's Tier 1 routing independently authored.** Rejected —
  the drift risk (two systems answering the same relevance question
  differently over time) outweighs the marginal simplicity of not sharing
  a data source across two phases.
- **Have the REPL call a more powerful model directly when a question
  exceeds digest scope, instead of escalating to a full session.**
  Rejected — this duplicates what Claude Code's own tool-use loop already
  does well (reading source, running commands, deeper reasoning) and
  breaks the REPL's cost/speed model, which depends on staying
  digest-only and Haiku-only. Escalating to an already-grounded session is
  cheaper to build and doesn't compromise the REPL's core tradeoff.

## Consequences

- Phase 9 is broadened in scope (see `planning/ROADMAP.md`) to cover
  Skills generation as well as the Cursor `.mdc` export, not Cursor alone.
- A new evaluation step is needed: auto-generated trigger descriptions
  aren't guaranteed to trigger reliably on relevant questions out of the
  box. Phase 9's plan file (not yet written) should include a
  verification step — a battery of test questions per vendor, checked
  against whether the corresponding skill actually loads — mirroring the
  kind of eval loop skill-authoring guidance recommends generally.
- **Description length becomes a tunable cost parameter, not a one-time
  writing task.** Since every skill's name+description loads
  unconditionally into every session regardless of relevance, the
  generation step should treat description length as something to
  optimize down (specificity over verbosity) rather than something to
  maximize for trigger recall. Worth tracking as a metric alongside
  trigger-accuracy in the Phase 9 evaluation step, not just checked once
  at launch — the tradeoff shifts as a project's `FULL`-depth vendor count
  grows.
- This adds a third generated-content type per `FULL`-depth vendor
  (`CLAUDE.md`, `.mdc`, and now `SKILL.md` + its `references/` bundle),
  which increases `sync`'s output surface but not its AI-call cost — the
  trigger description is derived from already-generated content, not a
  new model call.
- **Phase 8 and Phase 9 now have a real dependency, not just topical
  overlap.** Whichever is implemented first must expose its
  context-selection data (Skill description text) in a form the other
  phase's plan file can consume without duplicating it — this should be
  called out explicitly in whichever phase's plan file is written first,
  as a note for the other phase rather than assumed implicit.
- The REPL's startup disclaimer (already required — "this only knows
  what's in the digest") should be extended to mention the escalation
  path exists, so a user hitting the boundary of digest-only scope knows
  there's a next step rather than just receiving a lower-confidence
  answer.
