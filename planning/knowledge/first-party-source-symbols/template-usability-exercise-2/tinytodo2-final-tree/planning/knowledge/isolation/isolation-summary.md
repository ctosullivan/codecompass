# Isolation achieved, reported honestly per scope

Phase 79 sixth amendment, correction 3. This exercise's own Tier-1
preflight was not re-run — the main CodeCompass pilot already established
`Agent(isolation: "remote")` fails all five tested routes in this
environment (see `planning/knowledge/first-party-source-symbols/isolation/tier1-preflight.md`
in the main repository); the same environment and definitive failure
apply identically here.

## Per-dispatch isolation tier

| Stage | Dispatch | Mechanism | Tier |
|---|---|---|---|
| Research | context-researcher | Full project access | N/A by design — the research step is not isolation-sensitive |
| Adversarial review | domain-skeptic | Full project access | N/A by design |
| **Implementation reconstruction** | implementation-reconstructor | **Curated export directory** (source+tests only) | **Best-effort** — mechanically confirmed clean via real transcript analysis (`boundary-check-output.txt`), not self-report |
| Comparison | domain-skeptic (comparison mode) | Full project access | N/A by design |
| **Documentation draft** | docs-reconstructor | **Curated export directory** (snapshot+assertion only) | **Best-effort** — mechanically confirmed clean via real transcript analysis |
| Coding-context packet assembly | knowledge-curator | **Instruction-only** scoping, full tool access | Best-effort, weaker than a curated export — no mechanical check possible; relies entirely on the dispatch's own compliance |
| Documentation Q&A | general-purpose | **Instruction-only** scoping, full tool access | Best-effort, weaker tier — confirmed compliant this run (exactly 2 tool calls, both in scope), but this is one observed instance, not a guarantee |
| Coding-context packet evaluation | context-evaluator | Full project access | N/A by design — this role must inspect real source directly to establish ground truth |

## Final verdicts

**Workflow completion**: fully achieved. A valid, fully-committed frozen
snapshot; a real model-blind implementation reconstruction; a real
alignment comparison; real conceptual documentation; a real
task-specific coding-context packet; independent assessment of both
(PASS, PASS); and a real, mechanically-verified propagation
demonstration reaching both derived outputs through the shared snapshot
foundation — all via real git commits, none left `UNCOMMITTED`.

**Strict clean-room isolation**: **UNMET**, same as the main pilot. The
two genuinely isolation-sensitive dispatches (implementation
reconstruction, documentation draft) were mechanically confirmed, via
their own real transcripts, to have stayed within their assigned export
directories — but the mechanism itself (a curated directory the dispatch
is pointed at, not prevented from leaving) is not a mechanical
enforcement boundary, and this environment's own Tier 1 isolation
mechanism remains unavailable. Honest, verified best-effort compliance
is not the same claim as strict isolation having been achieved.
