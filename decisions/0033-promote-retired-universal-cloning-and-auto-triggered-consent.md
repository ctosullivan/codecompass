# 0033. `promote` retired; universal cloning + auto-triggered, disclosed consent is the sole cost point

## Status

Accepted

## Context

`decisions/0017` guarantees bare bootstrap never spends money or asks
anything. `decisions/0018` made `promote <vendor>` the single, manually
invoked, single-vendor escalation point for both source cloning and paid
AI generation. `decisions/0021` made source resolution fail loudly (no
sdist fallback) when a vendor has no resolvable repository URL, scoped to
`promote`'s clone step.

`decisions/0031` (this rework) removes the `Depth` field that `promote`
existed to set, and moves enrichment eligibility to automatic,
usage-detection-driven selection across the whole project rather than a
human naming vendors one at a time. Source cloning itself costs nothing
(no AI call) and is not a reason to gate behind a manual command.

## Decision

The `promote` command is removed from the CLI entirely. Its three former
responsibilities become automatic, whole-project outcomes:

1. **Source cloning** happens for every vendor during Phase A (the
   deterministic, always-free part of `sync`/bootstrap) — extending
   `decisions/0004`/`0010`'s "clone the upstream repo, don't reference a
   local install" posture from `FULL`-only vendors to all of them.
   `decisions/0021`'s fail-loud, no-fallback rule for a vendor with no
   resolvable repository URL is **preserved unchanged in substance** — a
   vendor without one simply doesn't get a clone during Phase A (falls
   back to the existing local-install copy) rather than a `promote`
   invocation failing outright. Only the trigger point moves.
2. **AI enrichment** (`decisions/0031`) is selected automatically from
   usage-proven vendors and runs as Phase B, batched across several
   vendors per call rather than one call per `promote` invocation.
3. **Skill/`.mdc` generation** fires automatically at the end of Phase B
   for whichever vendors newly qualify (≥1 enriched symbol), rather than
   from a retired command.

Phase B still discloses estimated cost and requires confirmation (or
`--yes`) before spending — `decisions/0017`'s "no silent AI spend"
guarantee is preserved at the level of the whole bootstrap/sync flow, even
though it no longer describes bootstrap *in isolation* (Phase A is still
unconditionally free and prompt-free; Phase B, which now runs
automatically right after it, is the disclosed/confirmable step).
`--budget` continues to guard the ongoing-cost case exactly as it does
today, now scoped to Phase B's batched calls.

## Alternatives considered

- **Keep `promote` as an optional manual override alongside automatic
  Phase B**, for a user who wants to force one specific vendor's
  enrichment outside the batched flow. Explicitly considered and rejected
  during this rework's planning interview in favor of fully retiring it —
  no concrete need for a manual override has surfaced, and it would
  reintroduce exactly the per-vendor manual-toggle surface
  `decisions/0031` removes for enrichment eligibility. If a real need for
  targeted re-enrichment emerges, that's future, evidence-driven work.
- **Make Phase A's universal cloning itself cost/consent-gated**, since
  it's a new default behavior change. Rejected — cloning triggers no AI
  call and no billed cost; gating it would misrepresent what actually
  costs money and dilute the meaning of the one real consent prompt
  (Phase B).

## Consequences

- `decisions/0017` is partially superseded (bootstrap's zero-question
  guarantee now describes Phase A specifically, not the combined
  Phase A+B flow) and `decisions/0018` is fully superseded; neither is
  edited (append-only).
- `decisions/0021`'s substantive rule is carried forward unchanged, only
  re-triggered from Phase A instead of `promote`.
- `source_resolution.py`'s `resolve_and_clone`/fallback logic is reused
  without modification — only its caller changes (`sync_vendor`, called
  for every vendor instead of gated on `depth is FULL`).
- `cli.py` loses the `promote` command; `chat.py`'s one user-facing hint
  string that referenced `promote` is reworded (Phase 9's rename phase
  already touches that string mechanically; its wording is finalized
  once `promote` is actually removed in Phase 16).
