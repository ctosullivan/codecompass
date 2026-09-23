---
status: DECIDED (Phase 65, lead, 2026-09-23) — every row's recommendation
  accepted as drafted, plus the two open items resolved below. Execution
  (`docs-maintainer`) dispatched from this decided state.
---

## Lead decisions on the two open items

1. **B.12 / B.12b overlap** — confirmed: these are two distinct,
   non-overlapping passages (`## Per-vendor CLAUDE.md structure` vs.
   `## Adapter interface`'s per-ecosystem prose). Treated as two
   separate rows/decisions, not merged, per the draft's own flagged
   reading.
2. **§7's open structural question** — **Option (b), a retained,
   substantially shortened `architecture/overview.md`** (not a 6th new
   architecture file). It stays the "system at a glance" entry point:
   after all §1/§2/§3 rewrite/remove/consolidate decisions are applied,
   it directly covers what has no home in Phase 64's 5-file set (B.13
   Two consumption modes, B.14 Staleness checking, B.15 Multi-tool
   export, B.16 `/discovery`, B.17/B.18 Chat REPL, B.30 `undo`, B.31
   Cost model, B.32 Known footguns — all current-state, rewritten per
   their own rows) and points into the 5 adopted Phase 64 files
   (`module-map.md`, `core-data-model.md`, `adapter-interface.md`,
   `context-graph-schema.md`, `sync-and-enrichment-pipeline.md`,
   landing under `architecture/`) for what they cover in depth. A new
   `architecture/historical-notes.md` captures B.19's routing-table/
   Skill refresh-timing bug story and B.28's relationship-enrichment
   excerpt-centering evolution — the two genuinely load-bearing pieces
   of history with no ADR of their own. Rationale: adding a 6th
   brand-new file for miscellaneous remaining topics would just
   recreate the "one document doing too much" problem in a different
   shape; keeping `overview.md` as the always-present index + the
   content Phase 64 didn't scope for is less disruptive and matches
   this project's own "don't add abstraction beyond what's needed"
   default.

# Reconciliation table — Phase 65

Compares Phase 64's blank-slate proposal (`planning/v1-docs-reconstruction/`)
against the current active documentation, document by document / passage
by passage. Covers:

- **§1** — `architecture-split-candidates.md` §A, the 5 section-level
  candidates (item 1 consolidated with `concepts-to-retire.md` item 1).
- **§2** — `architecture-split-candidates.md` §B, the 27 passage-level
  candidates (item 12 cross-referenced, not merged, with
  `concepts-to-retire.md` item 2 — see the note at that row; my own
  reading finds these two describe **different** sections of
  `architecture/overview.md`, not overlapping ones — flagged for the
  lead to confirm).
- **§3** — one new finding: a Phase 55b section added to
  `architecture/overview.md` after the Phase 42 catalogue was written,
  which is history-shaped in the same way as the catalogued items but
  isn't in either input file.
- **§4** — `concepts-to-retire.md`'s remaining 3 items (`docs/config-schema.md`,
  `docs/cli-reference.md`, `docs/external-adapters.md`).
- **§5** — one new finding in the explicitly-permitted `docs/domain/`
  presentation-adoption question (§2.3 of the phase plan: "decide only
  whether any of that reorganization is worth adopting alongside the
  existing `docs/domain/` corpus").
- **§6** — `README.md` / `ai-docs/` — checked directly against Phase 64's
  own account and against current content; no divergence found beyond
  what's already covered.
- **§7** — the net shape: how §1–§4's row decisions, taken together,
  produce the phase's own expected large outcome (`architecture/overview.md`
  split into a lean current-state set + a historical note).

Every row cites the current file/section by its **present** heading (line
numbers drift; anchor phrases don't) and gives one decision:
**retain / rewrite / consolidate / split / replace / remove / historical**
(shorthand for "preserve only in historical state").

## §1. Section-level candidates (`architecture-split-candidates.md` §A)

| # | Section (current `architecture/overview.md`) | Decision | Rationale |
|---|---|---|---|
| A.1 | `## Grounded description — retired; sync_vendor now reads it back (Phase 16)` | **remove** | Subject is a deleted module. The one load-bearing fact — `description_error` is set only by a clone failure, never a description failure — is already current-tense in Phase 64's `architecture/core-data-model.md` and can be folded into the retained `## Grounded description`-successor content in **Batched enrichment** / **Per-vendor CLAUDE.md structure**. Consolidates `concepts-to-retire.md` item 1 (same section, independently identified) — one decision, not two. |
| A.2 | `### Vendor docs as relationship sources (Phase 29, extended codecompass.doc_mapping)` | **consolidate** | Written entirely as a changelog entry (widened kind filter, renamed table, "supersedes `decisions/0041`"). Consolidate its current-truth content (what `vendor_doc` sources do in `build_documents_edges`/`build_doc_relations_edges`, the self-mention exclusion) into the retained **Vendor-embedded upstream docs** section (item B.29 below) as one present-tense description of "a vendor doc as both a relation target and a relation source" — these are the same underlying mechanism at two points in its own history and read better merged than as two separate phase-stamped sections. Supersession of `decisions/0041`'s narrower claim stays in `decisions/0043`, not restated here. |
| A.3 | Chat REPL — "No vendor specified (project-root mode)" subsection | **split** | ~75 lines (grown from ~55) of **unbuilt** design (explicitly "not yet implemented, post-MVP Phase 20"). This is forward-looking design, not current architecture, and doesn't belong in a current-state document regardless of history-narration concerns. Move to a dedicated design note (e.g. `planning/phase-20-chat-project-root-routing-design.md` if one doesn't already exist, or fold into the existing Phase 20 plan file) and leave one sentence + a pointer in the retained Chat REPL section. |
| A.4 | `## Context graph` opening paragraph | **rewrite** | The densest phase-chronology block in the file ("Phase 10 built it... Phase 11... Phase 21 adds... Phase 27 widens... Phase 29 widens..."). Collapse to a present-tense description of the schema and rebuild orchestration; the sequence is already in `decisions/0024→0032`, `0025`, `0037`, `0041`, `0043` and git. Matches Phase 64's `architecture/context-graph-schema.md`, which describes the same schema with zero phase narration. |
| A.5 | `### Batched enrichment` opening paragraph | **rewrite** | Describes a transitional state (two modules "coexisting through Phase 14") that has been over for many phases. Delete the transition narrative outright; state only that `enrichment.py` is the current, sole generator. |

## §2. Passage-level candidates (`architecture-split-candidates.md` §B)

Grouped by target section. Each is **rewrite** unless noted — the common
pattern is: strip the `(Phase N)` / `(as of Phase N)` / "since Phase N"
stamps and "used to X, now Y" chronology, keep the present-tense
mechanism, and rely on the cited ADR (already present in almost every
one of these) for the "why."

| # | Section | Decision | Rationale |
|---|---|---|---|
| B.6 | Intro, second paragraph | **rewrite** | Phase-stamped status snapshot ("As of Phase 19...", "neither a v0.1 nor v0.2 tag has been cut yet", a renumbering note). Replace with a plain present-tense inventory of implemented modules/commands + one pointer to `planning/ROADMAP.md`/`planning/CONTEXT.md` for status — status drifts every phase and doesn't belong hard-coded here regardless of the history question. |
| B.7 | Core data model — `VendorConfig` bullet | **rewrite** | "`context_path` (a Phase 5 field) was removed in Phase 7...; the per-vendor `depth` toggle... was removed in Phase 16" → "There is no depth toggle; a legacy `depth = "..."` line still parses without error." Same trim `docs/config-schema.md` needs (§4, item 3) — apply the identical wording so the two files don't drift into subtly different accounts of the same removed field. |
| B.8 | Core data model — `VendorDigest` bullet | **rewrite** | Strip the rename-from-`gap_analysis`/removed-`is_stale`-stub history; state the current fields and that `check` reads persisted `CLAUDE.md` files directly rather than building a digest. |
| B.9 | Symbol/purpose extraction — "generalized from... Phase 2" | **rewrite** | One clause of pure history; drop it, state the current shared-module fact plainly. |
| B.10 | Tree generation — clone-or-fallback root | **rewrite** | "**since Phase 13**, that root is..." / "wired into `sync.py` (Phase 4)" → describe the clone-or-fallback root and its wiring in the present tense, unconditionally (it is unconditional now, not a recent change). |
| B.11 | Tree generation — action-pointer bullet | **rewrite** | Drop "(implemented in Phase 5..., mechanism unchanged by Phase 7's swap)" and the bare `(Phase 16, decisions/0035)` stamp; keep the mechanism description and the one `decisions/0035` citation without the phase number attached to it. |
| B.12 | Per-vendor CLAUDE.md structure | **rewrite** | Collapse the entire "**Phase 14 adds a second, narrower write path**" paragraph and the removed-`**Depth:**`-line aside into: both write paths (from-scratch render, targeted enrichment rewrite) use the same "is there enrichment content" test. **Cross-reference note**: `concepts-to-retire.md` item 2 is framed by the Phase 65 plan as overlapping this item, but item 2's own text targets the separate `## Adapter interface` section's per-ecosystem npm/Python/Cargo/Haskell prose (lines 85–233), not this section (`codecompass.claude_md`, ~L525–576). Direct reading finds no actual content overlap between the two — they are unrelated passages that happen to both involve the word "adapter"/"vendor." Treating both here for completeness, but the lead should confirm this reading before treating them as one merged decision; see B.12b below for `concepts-to-retire.md` item 2 in its own right. |
| B.12b | `## Adapter interface` — per-ecosystem prose (npm/Python/Cargo bullets, `concepts-to-retire.md` item 2) | **rewrite** | Duplicates each adapter module's own docstring almost verbatim — a duplication risk (docstring can't drift silently from its own code; separate prose can). Trim to a contract-level summary + a pointer to each adapter's own docstring for per-ecosystem detail, matching Phase 64's `architecture/adapter-interface.md` shape (contract + strategy + one comparison table). Keep signalling real per-ecosystem quirks exist (dev_only handling differences, no `rustdoc --output-format json` yet) without restating flag-level detail in two places. |
| B.13 | Two consumption modes | **rewrite** | "for every tracked vendor since Phase 13's universal cloning"; "Since Phase 7, the snapshot is..."; "falls back to the original Phase 4 behavior"; "As of Phase 4: `index` reads..." — all four are "used to differ, now doesn't" framing for behavior that has been unconditional for many phases. State both modes as unconditional current behavior; the one ADR citation per fact (`decisions/0004`, `0021`) stays. |
| B.14 | Staleness checking | **rewrite** | "same reasoning `index.py` (Phase 4) already established"; "As of Phase 16, this makes no AI call" → present-tense: "the same reasoning `index.py` already established"; "`--fix` makes no AI call." |
| B.15 | Multi-tool export | **rewrite** | "Originally implemented in Phase 7 as part of `promote`... since Phase 15... `promote` is retired..." is a full changelog entry for a command (`promote`) that no longer exists at all. State plainly that a vendor's Skill/`.mdc` pair is written by `enrichment.apply_results` the moment enrichment succeeds — no "originally X, now Y" framing needed once X doesn't exist. The "**retained, not replaced**" framing on the Cursor `.mdc` export and the routing table (both correct facts, worded for a reader expecting a replacement) should become a plain statement of what each export is for — not "retained, not replaced," which only makes sense against a superseded expectation. **Not covered by any of Phase 64's 5 proposed architecture files** — needs a home in whatever current-state document(s) the split lands on; see §7. |
| B.16 | `/discovery` custom slash command | **rewrite** | Drop "**New in Phase 17**" and the migration-history clause ("`schema_version` bumped from `"1"` to `"2"`... migrating an already-existing pre-Phase-17 `context-graph.db`..." — a one-time migration event, not an ongoing property of the schema). The "as of this phase... see `planning/CONTEXT.md` for the current status of this gap" open-TODO language should be replaced with a one-line current-state fact (whole-project `sync` does not also regenerate `/discovery`) rather than sending the reader elsewhere for a "status" that this doc itself should just state; if the gap is now closed, delete the sentence outright. |
| B.17 | Chat REPL — misc phase citations | **rewrite** | "what changed in Phase 19 is framing, not behavior"; "**implemented (Phase 8).**"; the renumbering aside; "Phase 20's REPL routing reads..." — all chronology. State current behavior only. |
| B.18 | Chat REPL — `> **Historical note**` blockquote | **remove** | Explicitly self-labelled historical narration recording that `decisions/0012` is superseded by `decisions/0034`. That supersession is already `decisions/0034`'s own job to state. Replace with one plain sentence: chat is secondary, per `decisions/0034`. |
| B.19 | Retrofitting to existing projects | **rewrite + historical** | The largest single passage-level item. Most of it ("This is Phase 15's rewiring of `decisions/0031`/`0033`...", "Phase A (`decisions/0017`, Phase 7; extended Phase 15...)", "the CLI reference's earlier draft syntax was corrected... in Phase 4", "`requirements.txt` (Phase 7 addition)") is pure chronology — rewrite to present-tense flow description. The **"Routing table / tool Skill refresh timing (Phase 20)"** paragraph is different in kind: it records a genuine confirmed bug/behavior-change ("earlier phases regenerated them before Phase B ran... confirmed directly during this project's first live enrichment run") with no ADR of its own (only a plan-file pointer, `planning/phase-20-refresh-generated-artifacts-after-enrichment.md`). This is load-bearing history not captured in an ADR — per `documentation-lifecycle.md` §1.3, move it to the historical note rather than deleting it; leave one present-tense sentence in the main flow ("artifacts are refreshed once, unconditionally, at the end of the invocation, after Phase B returns"). |
| B.20 | Context graph — schema bullets | **rewrite + historical** | Per-column phase stamps throughout ("`spec_doc`/`project` added in Phase 21", "`vendor_doc`/`vendor_upstream` added in Phase 27", etc.) — rewrite to a plain schema description (matches Phase 64's `context-graph-schema.md`, which already does this with zero phase stamps). The one substantive design note worth keeping verbatim, not merely trimming — "**Not** the `DocChunk`/`EXPLAINS` tables from the former phase-9d design that `decisions/0032` explicitly excluded" — is a disambiguation a future reader could plausibly need (same name, different design); keep it but drop the "phase-9d" label, which is otherwise unexplained here, in favor of a pointer to `decisions/0032`/`0046` directly. |
| B.21 | Context graph — row-dataclass paragraph | **rewrite** | "This is a deliberate Phase 10 design choice... Phases 11–13..." — written from a past vantage point. State the natural-key design choice and its avoided-circular-import rationale in the present tense; the "why keyed this way" reasoning is worth keeping (it's not pure history, it's a still-true design rationale), just not phase-stamped. |
| B.22 | Context graph — query-function bullets | **rewrite** | Systematic `(Phase 30)`/`(Phase 32)`/`(Phase 21)`/`(Phase 22, extended Phase 28)` stamps on every function. Strip all of them; each function's own docstring-equivalent description stands without a phase citation. Matches `context-graph-schema.md`'s "Read/query functions" section, which already does this. |
| B.23 | Batched enrichment (body) | **rewrite** | "the whole point of `decisions/0031`, already reflected in Phase 10's... even though `Depth` itself isn't removed until later"; "reworked from the old per-vendor formula" — chronology. Keep the `decisions/0031` citation, drop the phase-sequencing narrative. |
| B.24 | Project-source usage detection | **rewrite** | "**New in Phase 11**..."; the "**Phase 26** adds an attribute-resolution upgrade" paragraph's own history framing. The substantive fact (attribute-style `import anthropic`-then-`anthropic.Foo` usage now resolves to symbol-level `uses_edges`, closing a real `/discovery`-found gap) is worth keeping — state it as current capability, not as "this phase closed that gap." |
| B.25 | Populating the graph | **rewrite** | "added to `sync.py` in Phase 11"; "Phase 12 adds real data (below)" — drop; state current call graph directly. |
| B.26 | Doc & wide skill mapping | **rewrite** | "**New in Phase 12 — still not CLI-visible...this phase only populates the five tables `rebuild_project_graph` previously passed empty lists for.**"; "(Phase 29 widened...)"; "(beyond the phase plan's originally sketched two-arg signature)" — all transitional-state or plan-vs-actual framing with no current relevance. Rewrite to present-tense function descriptions. |
| B.27 | Spec-doc detection & relationship graph | **rewrite** | "**New in Phase 21 — part 1 of...; Phase 22 adds...**"; "(originally `spec_doc` only; Phase 29 widens it...)" — chronology. Keep the one genuinely useful confirmed-behavior detail (fenced-code-block state tracking, "confirmed live against this repo's own `docs/cli-reference.md`") as a present-tense fact, drop its `(Phase 34)` stamp. |
| B.28 | Relationship enrichment | **rewrite + historical** | "**New in Phase 22 — part 2...**" plus three bold phase-headed paragraphs (Phase 28 excerpt-centering, Phase 31 taxonomy, Phase 32 excerpt preference) — each describes a real behavior change over time. The **current** behavior (excerpt centered on the actual mention; closed-taxonomy `relation_label`; Phase 28's fixed-window logic retained as fallback) belongs in the rewritten present-tense section. The **superseded intermediate behaviors** (the original fixed `source_text[:4_000]` window that could miss the mention entirely) are a genuine "this used to produce worse output, here's what changed and why" story with real value for understanding today's fallback logic's existence — move that specific narrative to the historical note rather than delete it outright, since it explains why a present-day fallback exists at all. |
| B.29 | Vendor-embedded upstream docs | **consolidate** | "**New in Phase 27**..."; "at this phase, only spec docs scan outward... Phase 29 below changes this"; forward/backward phase cross-references throughout. Consolidate with A.2 (`### Vendor docs as relationship sources`, Phase 29) into one present-tense section: a vendor's own embedded upstream docs are indexed, can be documented-about, and can themselves mention other tracked vendors/docs (with the self-mention exclusion). One section, not two, and no "at this phase X, Y below changes it" framing once both phases are long done. |
| B.30 | `undo` | **rewrite** | "**New in Phase 18 (`decisions/0036`).**" — drop the phase stamp, keep the ADR citation and the description of what `undo` does. |
| B.31 | Cost model | **rewrite** | "As of Phase 15..."; "As of Phase 16, there is no other cost path" — state plainly, present tense: "Phase B is the sole AI cost center" and "there is no other cost path," full stop, no "as of" qualifier implying a possible future change already covered. Keep the `decisions/0031`/`0035` citations. |
| B.32 | Known footguns — history stamps | **rewrite + remove** | Most bullets need only their phase stamp stripped (e.g. "`VendorDigest.is_stale` was removed in Phase 6" → "`VendorDigest` has no `is_stale` field; use `staleness.check_vendor`/`check_all`"). One bullet — "`_load_config` and `render_vendor_claude_md` are both implemented (Phases 1 and 4) — the CLI skeleton's old `_write_claude_md` stub was removed in Phase 4" — is, by the catalogue's own note, "no current footgun at all — pure history": **remove** that bullet outright rather than rewrite it, since nothing about it is a current limitation for anyone to be warned about. |

## §3. New finding: Phase 55b section (not in either input file)

| # | Section | Decision | Rationale |
|---|---|---|---|
| new-1 | `### Spec docs become relationship targets of each other (Phase 55b, extended codecompass.spec_docs and codecompass.doc_mapping)` | **rewrite** | Added to `architecture/overview.md` after Phase 42's catalogue was written, so it's absent from `architecture-split-candidates.md` — but it is history-shaped in exactly the same way as the catalogued items: "**Every `spec_doc` row had `name=None` before this phase**", "Closes `CG-004`... surfaced independently by... a real finding against the Ledgerkit reference project", forward-framed "found live testing against the real Ledgerkit repository." Same treatment as B.19/B.29: state the current mechanism (title extraction with a specificity guard, self-mention exclusion by path) in the present tense; the Ledgerkit-finding provenance is a good `CG-004`/learnings-log fact but doesn't need re-narration here — it is presumably already in `planning/context-gaps/inbox.md` and/or a learnings entry. |

## §4. `docs/` reconciliation (`concepts-to-retire.md` items 3–5)

| # | Doc | Decision | Rationale |
|---|---|---|---|
| ret-3 | `docs/config-schema.md` — `depth`/`context_path` legacy-field history | **rewrite** | Confirmed accurate against `config.py`'s real `_parse_entry`, but ~150 words ahead of the "what every tracked vendor gets" section a first-time reader needs more. Compress to the one-sentence footnote `concepts-to-retire.md` itself proposes ("historical fields removed in Phase 7/16, safely ignored if present — see `decisions/0031`"), matching B.7's identical trim to `architecture/overview.md`'s own copy of this fact so the two files state it identically rather than with independent wording that could drift. |
| ret-4 | `docs/cli-reference.md` / `docs/config-schema.md` — per-command "Status: implemented (Phase N, decisions/NNNN)" framing | **retain** (existing files) **+ split/add** (`docs/quickstart.md`) | Not a retirement — this density has real infrastructure value for `docs-reconstructor`'s per-phase drift audit and `check_adr_status_and_supersedes`, and every documented command is in fact fully current (none partial/planned). **Adopt Phase 64's `docs/quickstart.md`** (152 lines, phase-annotation-free, install-run-read-output in under 5 minutes) as a new real file for the first-time-user need this project currently has no answer for — `docs/README.md` doesn't list one, and `docs/cli-reference.md`'s own citation density is the wrong entry point for that reader. This is the one item in this table that's a net **addition**, not a trim. |
| ret-5 | `docs/external-adapters.md` — mixes developer-workflow and protocol/wire content | **split** | Both Cluster A (developer-workflow overlap with `docs/developer/writing-an-adapter.md`) and Cluster B (wire-contract overlap with `protocol-adapter/wire-protocol.md`) independently flagged this, and both confirmed the file's own content is currently accurate — a structural finding, not a correctness one. Phase 64 has now produced real target documents for both halves (`planning/v1-docs-reconstruction/docs/developer/writing-an-adapter.md`, `.../protocol-adapter/wire-protocol.md`, `.../protocol-adapter/integrating-a-new-external-adapter.md`), so the split candidate's own precondition ("once both exist as real candidates to migrate content into") is now met. Recommend: adopt those two/three proposed docs as new real files, and split `docs/external-adapters.md`'s current content between them (cloning/submodule/build instructions → developer docs; `protocol_version`-vs-repo-semver and the version-compatibility matrix → protocol-adapter docs). **Preserve the "Naming note" (adaptor/adapter spelling) verbatim wherever its content lands** — it independently matches `docs/domain/concepts/protocol.md`'s own finding and would be a real loss if dropped in the split. |

## §5. New finding: `docs/domain/` presentation adoption (in scope per §2.3's exception)

| # | Item | Decision | Rationale |
|---|---|---|---|
| dom-1 | Phase 64's `domain/quick-reference.md` (one-line-per-term table, all 19 terms, sourced verbatim from `docs/domain/glossary.md`) | **split/add** (as a new page under the existing `docs/domain/` corpus, not a rewrite of it) | This is presentation reorganization only — every row is a direct quote from the already-approved glossary, not a new definition (explicitly out of scope to re-derive per this phase's own boundary). It answers a real, different need from the glossary's "one paragraph per concept" ("I met this word in CLI output, what does it mean" — scannable, not read-through). Recommend adding it as `docs/domain/quick-reference.md`, generated/reviewed as a direct-quote compression of `glossary.md` so the two can't silently diverge. Its own "Note on 'adapter' specifically" section is worth keeping too — it's the same two-senses-of-'adapter' disambiguation `concepts-to-retire.md`'s own "Boundary worth naming for Phase 65" section already flags as existing self-awareness, not a new finding, corroborating rather than duplicating it. |
| dom-2 | Phase 64's `domain/reading-paths.md` / `domain/cross-links.md` | **retain as-is (not adopted)** | Both are navigation aids over the existing 19-page corpus, not new content. Lower value than `quick-reference.md` (which serves a use case `docs/domain/` doesn't currently cover at all) and duplicates what `docs/domain/README.md` likely already does or could easily be extended to do. Not recommended for adoption as separate files — if `docs/domain/README.md`'s own navigation is found lacking, that's a smaller, targeted edit to the existing README, not a new file. |

## §6. `README.md` / `ai-docs/` — checked directly, no divergence found

| # | Doc | Decision | Rationale |
|---|---|---|---|
| ro-1 | `README.md` | **retain** | Already present-tense and economical. Its few phase citations ("Phase 52 added `enrich apply`", "Haskell/Stack is a fourth, added in Phase 60") are load-bearing facts explaining *why* a feature works the way it does (why Haskell is handled differently), not accretive "Phase N added X, later Phase M changed it" chronology — they read as a single fact each, not a history. No change recommended. |
| ro-2 | `ai-docs/README.md`, `ai-docs/CLAUDE.md` | **retain** | Both are current-tense capability/boundary summaries with ADR citations for "why," no phase chronology at all. Matches Phase 64's own account (no `ai-docs/` proposal exists because Cluster A/B/C found nothing to reconstruct there beyond what's already current). No change recommended. |
| ro-3 | `CONTRIBUTING.md` | **retain** (out of this phase's named scope, checked anyway) | Not named in `architecture-split-candidates.md` or `concepts-to-retire.md`, and not in the phase plan's explicit §2.3 list (`docs/`, `docs/external-adapters.md`, `README.md`, `ai-docs/`). Checked directly against Phase 64's `development-process/` proposal and its own `docs/developer/workflow.md`: `CONTRIBUTING.md` restates `CLAUDE.md` for humans (as designed) and is current; no divergence found. No action needed. |

## §7. Net shape: does this table produce the expected split?

`documentation-lifecycle.md` §4 names the expected large outcome in
advance: **`architecture/overview.md` splits into a lean current-state
document plus a historical/superseded note.** Checking the above against
that target:

- **Lean current-state target** — Phase 64's 5 proposed files
  (`module-map.md`, `core-data-model.md`, `adapter-interface.md`,
  `context-graph-schema.md`, `sync-and-enrichment-pipeline.md`) absorb
  the rewritten content from A.4, A.5, B.7–B.9, B.20–B.28 (core data
  model, adapter interface, context graph schema/queries, the sync/
  enrichment pipeline) cleanly — those sections map onto the proposal's
  own scope almost one-to-one once phase-stamped chronology is stripped.
- **Gap the proposal does not cover**: B.15 (Multi-tool export), B.16
  (`/discovery`), B.17/B.18 (Chat REPL), B.13 (Two consumption modes),
  A.3's retained one-sentence pointer, B.14 (Staleness checking), B.30
  (`undo`), B.31 (Cost model), and B.32 (Known footguns) have **no**
  corresponding file in Phase 64's 5-file architecture set — that set
  deliberately scoped out "CLI flags/usage... from the user's point of
  view" (its own README, quoted above), but several of these sections
  are genuinely architecture-level rationale (e.g. *why* Skills are
  reliability-preferred over the routing table, *why* chat is secondary,
  the cost-center model), not CLI usage — they'd read wrong moved
  wholesale into `docs/cli-reference.md`. **Recommendation for the
  lead**: after rewriting each per this table, these sections need
  either (a) a 6th current-state architecture file (e.g. covering
  export/consumption surfaces and known footguns) that Phase 64's own
  scope didn't anticipate, or (b) a retained, substantially shortened
  `architecture/overview.md` that stays as the "system at a glance"
  entry point, pointing into the 5 detailed files for what they cover
  and keeping the rest directly. Either shape is consistent with "lean
  current-state document(s)" — the row-level decisions above don't
  presuppose which, but every row that would otherwise have nowhere to
  go is flagged as such above (B.15) so the decision isn't accidentally
  dropped during execution.
- **Historical note target** — genuinely load-bearing history not
  already captured in an ADR, flagged at B.19 (routing-table/Skill
  refresh-timing bug, `planning/phase-20-...md` only, no ADR) and B.28
  (relationship-enrichment excerpt-centering's superseded fixed-window
  behavior, explains why today's fallback exists). These two are
  concrete candidates for the new historical note; everything else
  either has an existing ADR to point to instead (the overwhelming
  majority of items above) or has no standalone value once the current
  behavior is stated (most B.6–B.12, B.20–B.27, B.29–B.32) and should
  simply be **removed**, not relocated — consistent with this phase's
  own instruction to fix or delete, never annotate.
- No row in this table recommends "retain in place" for a passage
  individually flagged as history-shaped in either input file — every
  §1/§2/§3 row above resolves to rewrite/consolidate/split/remove/
  historical, matching the phase's own instruction not to let a
  passage slip through as "not individually a section-level candidate"
  once its content is squarely historical.

## Count

- §1: 5 rows (A.1–A.5).
- §2: 28 rows (B.6–B.32, plus B.12b split out from B.12's
  cross-reference note — 27 catalogue items, 28 table rows).
- §3: 1 row (new finding, Phase 55b section).
- §4: 3 rows (`concepts-to-retire.md` items 3–5).
- §5: 2 rows (new finding, domain presentation adoption).
- §6: 3 rows (`README.md`, `ai-docs/`, `CONTRIBUTING.md`).

**42 rows total**, covering all 32 `architecture-split-candidates.md`
items (consolidated to 34 rows per the A.1/concepts-to-retire-1 merge and
the B.12/B.12b split), all 5 `concepts-to-retire.md` items, and 3 new
findings not named in either input file.
