# Chat project-root routing — deferred design

**Status: not yet implemented.** This is design content only, relocated
out of `architecture/overview.md` (Phase 65, GATE DA — a current-truth
document should not carry unbuilt design at length; see
`architecture-split-candidates.md` item A.3). `codecompass chat <vendor>`
(explicit-vendor mode) is the only mode `codecompass.chat` implements
today — see `architecture/overview.md`'s "Chat REPL" section for current
behavior. Everything below describes `codecompass chat` with **no vendor
argument** ("project-root mode"), plus a related escalation idea, neither
of which exist in `src/codecompass/chat.py` as of this writing.

This content was originally numbered "Phase 9" during early planning and
renumbered "Phase 20" during the v0.2 rework; neither number denotes a
scheduled, committed roadmap phase — see `planning/ROADMAP.md` for actual
phase status. It is retained here as a design sketch to build from if
this feature is ever picked up, not as a commitment that it will be.

## No vendor specified (project-root mode)

Will load a **project-wide dependency rollup unconditionally at session
start**, before any routing happens. The rollup is synthesized once per
`sync` (not per query) from the already-generated per-vendor
conversational overviews: dependency count, a staleness rollup by
severity, notable side-effect flags, and a short narrative. No new
per-dependency AI calls — one cheap summarization pass over data that's
already paid for. This exists because a large share of realistic casual
usage ("anything risky in my deps right now," "why do we even use X,"
"what changed recently") doesn't cleanly signal either "vendor" or
"project" the way keyword/phrase matching expects — waiting for a
routing match before loading *any* project-level context would miss
these. The REPL's startup banner would state that the rollup is loaded,
once, up front.

Vendor-specific escalation would still use two-tier routing **on top of**
that baseline rollup, across three possible context targets (a specific
vendor, several vendors, or the project itself), sourced from the SQLite
context graph (`decisions/0032`) rather than inventing ad hoc heuristics
inline:

- **Tier 1** (free, instant) — match against the **same generated Skill
  description text** that usage-driven AI enrichment
  (`enrichment.apply_results`) produces for Claude Code's native Skills
  triggering (see
  [`decisions/0013`](../../decisions/0013-agent-skills-as-shared-context-selection-source.md)),
  not an independently-authored keyword/alias list — one source of truth
  for "what fires on what." If nothing matches, check for project-level
  signal instead (question references architecture, a roadmap phase, a
  past decision, or general "how does this project..." phrasing) and
  load **project context** (root `CLAUDE.md` + `architecture/` +
  relevant `decisions/` entries + `planning/CONTEXT.md`'s current-state
  section) rather than any vendor digest.
- **Tier 2** (fallback, only if Tier 1 is ambiguous) — pass both the
  vendor routing table and a summary of available project-context
  sources, and let the model itself judge relevance (no extra API call),
  escalating to a one-shot Haiku classification call only if that's
  insufficient.
- **Always print a visible context indicator line before answering** —
  e.g. `→ loaded turndown digest (exact match)` or `→ using project
  context (architecture/overview.md, decisions/0003-*.md)`. This tells
  the user what *additional* context, beyond the baseline rollup,
  grounded a given answer — the rollup itself isn't re-announced every
  turn, only at session start. If a question pulls in both a vendor
  digest and project context, the indicator line would list both
  explicitly rather than picking one to display.

Loaded context (the baseline rollup, plus anything Tier 1/2 escalation
adds) would persist in the system prompt for the rest of the session
(cheap to keep, cache-friendly); a soft cap (~3-4 loaded context sources
beyond the rollup, LRU eviction) would prevent a long mixed session from
letting the system prompt grow unbounded.

## Escalation when a question exceeds digest-only scope

See
[`decisions/0013`](../../decisions/0013-agent-skills-as-shared-context-selection-source.md)
— deep source inspection, execution, or reasoning beyond what a digest
captures. Rather than answering confidently from incomplete context (the
same over-trust risk that applies to digest-only answers generally), the
REPL would state the limitation and point at the already-generated
`.claude/skills/codecompass-<vendor>/` folder as the handoff artifact for
a full Claude Code session, already grounded via the same Skill — reusing
that already-generated Skill (written automatically by enrichment, not a
manual step) rather than inventing a separate context-packaging
mechanism. The REPL's startup disclaimer ("this only knows what's in the
digest") would be extended to mention this escalation path exists, so a
user hitting the boundary knows there's a next step rather than just
receiving a lower-confidence answer.

This escalation idea is not specific to project-root mode — it would
apply equally to today's explicit-vendor `chat <vendor>` — but is
recorded here alongside project-root routing since neither is
implemented and both were originally sketched together.
