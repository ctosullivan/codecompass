# 0026. Context-graph enrichment (9d) is optional, deterministic-gated, and does not close decisions/0013's harness item

## Status

Accepted

## Context

9a–9c (`planning/phase-9a-vendor-presence-graph.md` through
`phase-9c-doc-skill-mapping.md`) build the context graph entirely
deterministically — no AI calls anywhere in construction, reproducible
offline, safe in CI with no `ANTHROPIC_API_KEY`. Phase 9d
(`planning/phase-9d-llm-enrichment.md`) adds a materially different kind
of value on top: usage-purpose labels per symbol, concept clustering per
vendor, a `DOCUMENTS` quality delta, file-role summaries, and a
trigger-accuracy proxy for Skills — all of which trade reproducibility
for semantic value, the same tradeoff `depth = full`'s grounded
description already makes (`decisions/0019`) but for a new class of
graph-level content rather than one vendor's digest.

Separately, `decisions/0013`'s Consequences section flags a real,
still-outstanding gap: "a battery of test questions per vendor, checked
against whether the corresponding skill actually loads" — a real
Claude-Code-session triggering evaluation, not yet built anywhere in this
project (confirmed still open as of `planning/CONTEXT.md`'s "still
outstanding" list). 9d's brainstormed trigger-accuracy proxy (generate
realistic questions per heavily-used symbol, ask the same model class
whether the Skill description would plausibly route them) risks being
mistaken for a resolution of that item if this ADR doesn't say otherwise
explicitly — it is a self-judgment by the same tier of model doing the
routing, not an independent measurement of Claude Code's actual
triggering behavior.

## Decision

9d is a separate, off-by-default layer relative to 9a–9c, invoked only by
an explicit new command/flag, `depcompass graph --enrich [--budget X]` —
cost-disclosed before any API call, requiring confirmation unless
`--yes`, mirroring `promote`'s existing pattern (`decisions/0018`) rather
than `sync --budget`'s abort-the-whole-run pattern, since enrichment is
itself the action being confirmed, not a side effect of another one.
Its output lives entirely inside `context-graph.json`'s `enrichment` key
(`decisions/0024`), which is `null`/absent whenever 9d hasn't run. Bare
`depcompass graph` (no `--enrich`) and bare `depcompass sync`/`depcompass`
never populate or require this key.

Every 9d LLM call follows `grounded_description`'s single forced-tool-use
pattern (`src/depcompass/grounded_description.py`'s `_TOOL_SCHEMA` +
`tool_choice` forced to that tool + dict read-back) — never `chat.py`'s
freeform multi-turn loop. Calls are batched per unit of graph structure
(one call per symbol-per-file for usage-purpose labels, one call per
vendor for clustering, one call per doc artifact for `EXPLAINS` in
`decisions/0027`) — cost must scale with graph nodes, never with raw
project size or call-site count. All enrichment is gated by a threshold
(e.g. `depth = full` vendors only, or a usage-count floor); nothing is
enriched by default just because it exists in the deterministic graph.

**The trigger-accuracy proxy is an explicit interim stopgap for
`decisions/0013`'s Consequences item, not a resolution of it.** A real
eval harness — actual Claude-Code-session triggering behavior, checked
against real questions, not a same-model plausibility judgment — remains
an outstanding gap after 9d ships. `decisions/0013`'s Consequences entry
stays open.

## Alternatives considered

- **Fold enrichment into bare `sync`.** Rejected — would silently bill
  every `sync` invocation once enabled once, contradicting
  `decisions/0018`'s "promote is the sole reactive, cost-disclosed
  action" ethos; this ADR extends that ethos to a second cost center
  rather than letting `sync` accumulate a second implicit one.
- **Treat the trigger-accuracy proxy as closing out `decisions/0013`'s
  harness item.** Rejected — a self-judged plausibility check by the same
  model class is a materially weaker signal than observing real Claude
  Code triggering behavior; conflating the two would cause a future
  session to believe a real gap is closed when it isn't.
- **Gate 9d behind a global on/off setting in `vendor.toml` instead of a
  per-invocation flag.** Rejected — `VendorConfig`'s three-field schema
  (`decisions/0011`) has no project-level settings surface today, and
  adding one only for this would be new scope beyond what 9d needs; a
  command flag is sufficient and matches `promote`/`sync --budget`'s
  existing per-invocation cost-control pattern.

## Consequences

- A project with no `ANTHROPIC_API_KEY`, or one that wants
  CI-reproducible graphs, gets 9a–9c in full, unaffected, with 9d simply
  never invoked.
- Testing 9d follows `decisions/0016` directly (not 9a–9c's simpler
  "zero LLM calls in construction" posture): monkeypatch each new
  enrichment function's `_call_anthropic` seam per-module, plus a fake
  `anthropic.Anthropic` client for SDK-shape tests — the same two-tier
  pattern already used in `tests/test_chat.py` and
  `tests/test_grounded_description.py`. No test makes a live API call.
- `architecture/overview.md`'s Cost model section gains a second,
  opt-in cost center distinct from `promote`'s, and must state plainly
  that it is optional and separately budgeted.
- Future work on a real trigger-accuracy eval harness is not blocked or
  implied by 9d shipping — it remains a separate, not-yet-scoped effort.
