# 0003. Use claude-haiku-4-5 for gap analysis

## Status

Accepted

## Context

Gap analysis (comparing a vendor's API surface against how the consuming
project actually uses it) is the only step in depcompass that makes an AI
call. It runs only when `depth = FULL`, and only when a project's own
`context_path` (README/spec) is supplied. The task is a Q&A/summarization
job over a bounded amount of text (API surface + project context), not an
agentic coding task requiring tool use or multi-step reasoning.

## Decision

Use `claude-haiku-4-5` for gap analysis generation.

## Alternatives considered

- **Sonnet or Opus.** Rejected for this specific step — the cost model
  targets well under $2/month at realistic project scale (dozens of
  dependencies, a handful at `FULL`, weekly refresh); a larger model would
  break that target for a task that doesn't need the extra capability.
  Larger models remain the right choice elsewhere (e.g. driving Claude
  Code itself in a vendor folder) — this decision is scoped to the
  gap-analysis step only.

## Consequences

- Gap analysis quality is bounded more by whether `context_path` is
  supplied and how well it describes the consuming project than by model
  choice — a missing or thin `context_path` will produce generic output
  regardless of model tier.
- If a future revision needs gap analysis to reason over substantially
  larger context (e.g. whole-codebase usage analysis instead of a single
  README/spec), that's a case to revisit this decision explicitly, not
  silently swap models.
