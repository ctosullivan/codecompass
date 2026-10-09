# Workflow: the knowledge-intermediate reconciliation loop

This covers `codecompass knowledge ...`, grounded directly in `src/codecompass/knowledge_intermediate.py`. No captured end-to-end terminal transcript exists in the available evidence for this specific workflow (unlike the sync/enrichment pipeline) — this page describes it accurately from the source and its own extensive test suite, without presenting a worked session that wasn't actually captured.

## The three stages

**Stage 1 — detect (`codecompass knowledge select-candidates <slug>`)**: mechanical only, read-only, no AI call. Every rendered anchor in `planning/knowledge/<slug>/intermediate/*.md` carries two hashes in its own opening comment: `semantic-sha256` (over the canonical YAML record at render time) and `projection-sha256` (over the rendered Markdown block at render time). Detection recomputes both fresh and classifies each anchor into one of four cases — **crucially, the two hashes are never compared against each other**, only each against its own current recomputation:

| Canonical record changed? | Projection edited? | Case |
|---|---|---|
| no | no | `noop` |
| no | yes | `candidate` — a human/tool edit with no corresponding canonical change; needs review |
| yes | no | `refresh` — safe, automatic; no review needed |
| yes | yes | `concurrent_conflict` — neither side touched; needs human resolution |

Any still-un-reviewed, not-yet-canonicalized text sitting between `<!-- codecompass-candidates:start -->` / `<!-- codecompass-candidates:end -->` markers in any rendered file is also detected as a **candidate addition** — plain prose by default (an unclassified factual hypothesis), unless it begins with an exact `Type: Requirement` or `Type: Intent` header (see below).

`refresh` cases are applied immediately and automatically, by **targeted, single-block substitution** — never a whole-file re-render, so a refresh of one record can never accidentally erase an unrelated, still-pending human edit sitting in the same file. Everything else (genuine `candidate`s and `concurrent_conflict`s) is written into a durable, committed TOML **reconciliation manifest** under `planning/knowledge/<slug>/reconciliation/`.

**Stage 2 — review**: a human or an agent annotates each manifest item's `decision` field (`accept`/`reject`) and, for a semantic edit, explicitly marks `semantic_change = true` (the default is `false` — a presentation-only wording change never creates a new canonical record on its own).

**Stage 3 — apply (`codecompass knowledge apply <manifest_path>`)**: the **only** function in the codebase allowed to write a canonical `planning/knowledge/*/*.yaml` record. It never trusts Stage 2's own annotation at face value — every item is mechanically re-checked (the canonical record's hash is re-verified against the manifest's own recorded `base_semantic_hash`; a stale or already-applied item is skipped, never silently re-applied or silently treated as success without genuine confirmation).

## What a presentation-only edit produces

No new canonical record at all — only a presentation-cache entry (`planning/knowledge/<slug>/intermediate/.presentation-cache.toml`) mapping the record's id to the accepted wording, keyed to the exact semantic hash it was accepted against. The canonical record's own statement is retrievable even while this override is in effect, via an invisible `<!-- codecompass-canonical-statement: ... -->` HTML comment embedded in the rendered block (never visible to an ordinary reader, always present in the raw file for any agent/dev-context consumer).

## What a genuine semantic edit produces

A **new, competing** Claim record — never an overwrite of the original. The original record is left untouched; the new Claim's `depends_on` field cites the original.

## The Requirement invariant

Merely *mentioning* an approved Decision id anywhere in ordinary candidate prose is never enough to create a Requirement. Only a candidate block beginning with the exact line `Type: Requirement`, followed by `Decision:`/`Statement:`/`Example:` lines, where the named Decision resolves to a real, **already-approved** Decision record and the `Example:` text structurally reads as Given/When/Then, produces a Requirement. Anything short of that — an unapproved Decision, a missing/malformed example — falls back to an ordinary Claim using the submitted Statement text, never a fabricated placeholder example.

## Declared intent vs. factual hypothesis

A candidate block beginning with the exact line `Type: Intent` is recorded with `basis: proposed_policy` (a declared project policy, not yet a fact about the system). Ordinary prose with no such header stays an unclassified factual hypothesis — merely using the word "should" or "must" in prose does **not** make it declared intent on its own.

## Explicit document grounding (`<!-- codecompass-grounded-by: ... -->`)

A project document (currently `README.md` and `CONTRIBUTING.md`) can mark a specific prose region as explicitly grounded in one or more knowledge-record ids, optionally with a stable `region:<id>` token that survives the region being moved or reordered within the document. `codecompass knowledge doc-select-candidates` detects, independently: a factual edit to the grounded region's own prose (becomes a real reconciliation candidate, routed through the owning record's own slug); a cited record changing on its own (surfaced as "potentially stale, worth a look," with **no mutation** — dismissed only via the dedicated `codecompass knowledge doc-acknowledge-stale` command); or both changing at once (an explicit, unresolved conflict). Detection alone never advances any baseline — only a successful `apply` or an explicit acknowledgement does.

## Advisory, never-blocking coverage reporting

`codecompass knowledge status [slug] [--strict]` reports records needing review (`contradicted`, or `proposed` with no evidence assessment yet) and any unresolved concurrent-change conflict (`--strict` fails only on the latter — a genuine reconciliation-mechanism failure, never a coverage gap). It also reports a purely advisory grounding-coverage summary — grounded-region counts, which ones changed, and which *ungrounded* document chunks changed and might be worth a look — none of this is ever auto-converted into a canonical record.
