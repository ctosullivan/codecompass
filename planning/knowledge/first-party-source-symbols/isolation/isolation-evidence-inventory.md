# Isolation evidence inventory and corrected verdict (fifth amendment, 2026-10-01)

Written in response to a direct correction request: the original Phase
79 closeout reported "strict clean-room isolation: PASS" for Track 2,
when what had actually been achieved was best-effort isolation, honestly
labelled as such. **Honest labelling of a best-effort result is not the
same thing as the result itself being a pass on strict isolation.** This
document corrects that conflation, inventories what evidence actually
exists for each pilot dispatch, and states two separate, final verdicts.

## What "strict clean-room isolation" would require, and what exists instead

A genuine strict-isolation claim needs, per scope: a manifest of exactly
what was included/excluded, a raw tool-call transcript (not a
paraphrase), an access log independently confirming what was actually
touched, and a boundary check confirming nothing outside the manifest
was reached — ideally backed by a mechanism that makes violation
*impossible*, not merely unobserved.

**None of the pilot's dispatches had a mechanically-enforced boundary.**
Every one had either a curated export directory (content the dispatch
was *pointed at*, not prevented from leaving) or an instruction-only
scope (full tool access, told what to stick to). This was already
disclosed at the time (`tier1-preflight.md`'s own conclusion: "Tier 2 is
always best-effort regardless of any single probe's own outcome"), but
the Track 2 *verdict line* in the closeout reports still said "PASS" —
which reads as "isolation succeeded," not "the dispatches' own honesty
about not having succeeded was itself verified." That phrasing is the
defect being corrected here.

## Evidence inventory, per dispatch

All of the following was recovered from the *original* dispatches' real,
on-disk JSONL transcripts in this session's own local Claude Code state
(`~/.claude/projects/-home-cormac-projects-codecompass/0b2afcc0-cb03-48e4-8480-bf16722dc977/subagents/agent-<id>.jsonl`)
— not rerun, not reconstructed from memory, not fabricated. These
transcripts are tied to this specific local machine and session and are
not part of the published repository; what's committed here is a
mechanical analysis of them (a script plus its real output), not the raw
JSONL itself, both because it is not portable evidence outside this
session's own local state and because each file (252 KB–896 KB) is
mostly repeated harness-internal content (system prompts, full tool
schemas) rather than task-relevant material.

| Dispatch | Agent id | Scope mechanism | Manifest | Raw transcript | Access log / boundary check |
|---|---|---|---|---|---|
| Tier 1 preflight probe | `a067b85bd9ed05746` | N/A (the probe itself) | N/A | **Recovered**: real tool_use/tool_result pairs extracted and preserved — `tier1-preflight-raw-transcript-excerpt.txt` | N/A |
| Understanding reconstruction (context-researcher) | `aeb8e7f6db41e0547` | Curated export directory | Existed at dispatch time (`MANIFEST.md`, `TASK.md`, in the export) — **not preserved**: the scratch export was deleted after use, before this correction was requested, and its manifest's content is not reconstructable without re-deriving it, which would not be genuine original evidence | Original exists on disk; not republished (see rationale above) | **Recovered, mechanical**: `boundary_check.py` + its real output (`boundary-check-output.txt`) — zero out-of-scope Read/Glob/Grep/Bash references; one flagged item (a self-built test sandbox) manually traced and confirmed to only copy content *from* the assigned export, never from outside it |
| Implementation reconstruction, pass 1 | `ad03cd2cd0213f19e` | Curated export directory | Same as above, same preservation gap | Original exists on disk; not republished | **Recovered, mechanical**: zero out-of-scope references |
| Implementation reconstruction, pass 2 (re-run) | `a24159175726b88a7` | Curated export directory | Same as above, same preservation gap | Original exists on disk; not republished | **Recovered, mechanical**: zero out-of-scope references |
| Documentation draft (docs-reconstructor) | `a1d1d1a9168a90fb7` | Curated export directory | Same as above, same preservation gap | Original exists on disk; not republished | **Recovered, mechanical**: zero out-of-scope references |
| Coding-context packet assembly (knowledge-curator) | `a37d825bfe89a67bf` | **Instruction-only** — full repository tool access, no curated export at all | N/A (no export existed) | Original exists on disk; not republished | **Recovered, mechanical** (`packet-assembly-access-log.txt`): **two reads fall outside the stated scope** (a governing methodology doc, the checker script itself) — a real, disclosed boundary deviation, not a clean result. Neither leaked into the packet's own content (verified: neither file is referenced in `context-packet.md`), but the boundary itself did not hold. |
| Documentation-only Q&A | `a69beb73c95067561` | **Instruction-only** — full tool access, no curated export | N/A | Original exists on disk; not republished | **Recovered, mechanical** (`qa-verification-access-log.txt`): exactly two tool calls, both matching the instructed scope precisely — the boundary held for this one instance |

## What this corrects, concretely

- The original closeout's isolation evidence was, in substance, the
  *dispatching agent's own prose summary* of what it did — accurate as
  far as it was checked at the time, but not a raw transcript, access
  log, or independent boundary check. That gap is now closed for the
  dispatches whose original transcripts still existed on disk: real,
  mechanically-derived boundary checks now exist for all six
  isolation-sensitive pilot dispatches, not just a narrative summary of
  one of them (the Tier 1 preflight).
- One of those six independent checks **found a real boundary deviation**
  (the packet-assembly dispatch read two files outside its stated
  scope) that the original closeout's prose-only evidence had no way of
  catching, since it never mechanically inspected the transcript.
- No historical transcript was fabricated, and no later rerun is being
  presented as evidence of what the original dispatches did — every
  finding above traces to the *original* dispatch's own real, timestamped
  transcript, still present in this session's local state at the time
  this correction was written (2026-10-01).

## Corrected verdicts (final, superseding the original closeout's conflated language)

**Workflow completion: this is fully, separately satisfiable and was
achieved** — the pilot topic was researched, reviewed, frozen into a
snapshot, independently reconstructed, compared, published, reconciled,
and verified, in full, per the plan.

**Strict clean-room isolation: UNMET.** No pilot dispatch's isolation
boundary was mechanically enforced. Five of six isolation-sensitive
dispatches, checked mechanically against their own real transcripts,
show no evidence of a boundary crossing; one shows a real, disclosed
crossing (not reaching the packet's own output, but a crossing
nonetheless). None of this changes the verdict either way: **honest
compliance under an unenforced instruction is not strict isolation, by
definition, regardless of how many instances hold.** This finding stands
on its own, independent of and unaffected by anything in `planning/ROADMAP.md`
or any audit report's own wording — those are corrected separately to
match.
