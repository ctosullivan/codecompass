# Phase 81B Amendment 4 — legacy-document gap review

Per the governing instruction's §7. Run only after the first complete
clean-room writer result was preserved (`cleanroom/result-8325272`,
commit `0085cc2`) — the writer itself never saw any legacy documentation
at any point.

## Method

1. A fork (no persistent memory of this task beyond its own dispatch)
   compared the writer's 24-file output against the full legacy
   documentation corpus (`README.md`, `CONTRIBUTING.md`, `docs/**`,
   `architecture/**`, `ai-docs/**` — 40+ files) and reported candidate
   gaps: specific, concrete legacy claims not reflected in the new set.
   The fork was explicitly instructed it was a gap *detector* only, not
   a decision-maker — it never recommends copying legacy prose anywhere.
2. The lead independently re-verified every candidate gap against real
   primary source (grepping/reading the actual `src/codecompass/*.py`
   files cited) before taking any action — one candidate (the symbol-
   indexing-states finding) turned out to be a false positive on
   recount and was correctly dropped.
3. For the remaining real findings, a second, fresh, isolated writer
   context (never the same context as the first draft, never shown any
   legacy prose) was given only the real, verified facts with their real
   source locations, plus the first draft's own current content for the
   affected files, and asked to verify each fact against its cited
   source itself before revising. It revised exactly the files that
   needed it and left the rest unchanged.
4. The lead reviewed every resulting diff before merging it into the
   preserved result.

## Findings

| # | Claim | Verified? | Action |
|---|---|---|---|
| 1 | `SymbolIndexStatus` has 5 real states, only `unreadable` documented | **False positive** — `docs/reference/symbol-extraction.md` already documents all 5 (confirmed by direct read) | None — writer correctly declined to change this file |
| 2 | `discovery.py`: `[project.optional-dependencies]` never scanned; hpack `when:`-blocks never expanded | Confirmed (`discovery.py` lines 46, 97) | Added to `docs/limitations.md` |
| 3 | `/discovery`'s real `allowed-tools` access control | Confirmed (`commands.py` line 28+) | Added to `docs/architecture/components.md`, with an additional real nuance (the restriction's single-turn scope, `decisions/0040`) the writer itself found and correctly grounded |
| 4 | `undo`'s two enumeration strategies, different precision | Confirmed (`cli.py` `undo` docstring, line 1225+) | Added to `docs/reference/cli.md` |
| 5 | Migrations never gate on `meta.schema_version` | Confirmed (`graph.py` schema_version comments) | Added to `docs/architecture/data-and-control-flow.md` |
| 6 | `_SHUTDOWN_TIMEOUT_SECONDS = 5.0` | Confirmed (`external_process.py` line 26) | Added to `docs/reference/protocols.md` |

## No contradictions found

The fork's comparison found zero cases where the new docs actively
contradicted a legacy claim — everywhere both covered the same topic,
the content agreed (the new docs being more concise, not different in
substance).

## Scope note

`CONTRIBUTING.md` was not compared in depth — it is CodeCompass's own
self-governing development-process document, the same category
correctly excluded from the writer's own workspace by design (matching
`CLAUDE.md`'s own exclusion), and the resulting thinness of
`docs/development/contributing.md` is already disclosed as an accepted
limitation in the handoff's own `OPEN-QUESTIONS.md` — not a new finding
from this review. `architecture/overview.md` (1186 lines) and
`architecture/sync-and-enrichment-pipeline.md` were spot-checked, not
read end-to-end, given time proportionality; no further findings
surfaced from the spot-checks performed.

## Tooling added

`scripts/cleanroom_prompt_assembler.py` gained a third role, `revise`
— reads an additional revision-instructions file (the verified facts
and their target files), includes the current draft of the affected
files in the evidence blob (under `current-draft/<path>`), and asks a
fresh writer context to verify-and-incorporate only what's missing,
outputting only files that actually changed. This is the mechanism the
plan's own §7 flow ("a targeted fresh clean-room update through an
isolated writer context") now has a concrete, reusable implementation
for, rather than being a one-off manual process.
