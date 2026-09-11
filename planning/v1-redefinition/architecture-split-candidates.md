# `architecture/overview.md` split candidates — input for Phase 61

**Status: input for Phase 61 (the `architecture/overview.md`
reconciliation / split), NOT a Phase 42 deliverable to action.**

Phase 42 (documentation-lifecycle, Stage A) does not restructure
`architecture/overview.md` — that is Phase 61's job. This note is the raw
material: a catalogue of passages in the current `architecture/overview.md`
(~1,954 lines) that narrate *decision history* or *"how it got here"*
rather than describe *current state*, produced by the `docs-maintainer`
while reconciling the Phase 42 diff.

Line numbers are as of commit `cd433f9` + the Phase 42 working tree and
**will drift**; each item quotes an anchor phrase so Phase 61 can relocate
it. Nothing here has been edited.

**Update (Phase 43b):** Section C's 4 now-self-contradictory items
(33-36) were fixed directly — L-004's Phase-61 obligation for *those
specific 4 items* is closed early; see §C below for the resolution. The
broader §A/§B history-shaped trims remain Phase 61's job, unedited.

## How Phase 61 should use this

Per `planning/v1-redefinition/documentation-lifecycle.md` §1.1
(current-truth principle) and the `docs-maintainer` / `docs-reconstructor`
briefs:

- Rationale ("why we chose X over Y", "superseded by") belongs in an ADR
  under `decisions/`, referenced by a short pointer — not narrated inline.
- "Phase N added… Phase M widened… Phase P renamed…" chronology should
  collapse to a single present-tense description of the thing as it is
  now. Git history and the ADRs already hold the sequence.
- Transitional-state descriptions ("the two modules coexist through Phase
  14", "not yet CLI-visible") should be deleted outright once the
  transition is complete.
- A few passages are not merely historical but **now inconsistent with
  the rest of the same file** (see section C) — Phase 61 should treat
  those as corrections, not just trimming.

## A. Section-level candidates (whole sections that are history-shaped)

1. **`## Grounded description — retired; sync_vendor now reads it back
   (Phase 16)` (currently ~L247–299).** The section's *subject* is a
   deleted module (`codecompass.grounded_description`). Opening: "the
   original one-call-per-vendor, `depth = FULL`-gated AI description step
   this section used to document — is **deleted** as of Phase 16". The
   genuinely current content — that `sync_vendor` makes no AI call and
   reads enrichment back from the context graph, the failure-handling
   semantics, "no more `sync`-level AI budget gate" — should be folded
   into **Batched enrichment** and **Per-vendor CLAUDE.md structure** as
   present-tense description. Everything phrased as "used to", "that gate
   is deleted along with the generation it was guarding", "`sync_all` used
   to run `check_budget` once" is history for an ADR / git.

2. **`### Vendor docs as relationship sources (Phase 29, extended
   codecompass.doc_mapping)` (currently ~L1631–1685).** Written entirely
   as a changelog entry: "**A vendor's own embedded upstream doc … was
   wired into the graph as passive, indexed content only** … Two gaps,
   both closed this phase:", then "widens from `("claude_md", "overview")`
   to `("claude_md", "overview", "vendor_doc")`", "is renamed
   `spec_doc_rows` → `source_doc_rows`", and "how this supersedes
   `decisions/0041`'s … claim specifically". Should become a plain
   present-tense description of what `vendor_doc` sources do in
   `build_documents_edges` / `build_doc_relations_edges`, plus the
   self-mention exclusion, with the supersession noted only in
   `decisions/0043`.

3. **Chat REPL — "No vendor specified (project-root mode)" subsection
   (currently ~L657–710).** ~55 lines describing an explicitly
   *unimplemented* feature ("**not yet implemented (post-MVP Phase 20)**,
   renumbered from the original Phase 9 during this rework"). Future
   design, not current architecture. Phase 61 should decide whether
   unbuilt design lives in `architecture/overview.md` at all or moves to
   the phase plan / a dedicated design doc.

4. **`## Context graph` opening paragraph (currently ~L829–875).** The
   densest chronology block in the file: "Phase 10 built it as a
   standalone library; Phase 11 was the first phase to actually populate
   it…; Phase 12 extends…; Phase 15 is the first phase to read it back…;
   Phase 21 adds a tenth deterministic table…; Phase 27 widens…; Phase 29
   widens both…". Collapse to a present-tense description of the schema
   and the rebuild orchestration; the sequence is in the ADRs
   (`0024→0032`, `0025`, `0037`, `0041`, `0043`) and git.

5. **`### Batched enrichment` opening paragraph (currently ~L1089–1101).**
   Describes a transitional state that no longer exists: "**New in Phase
   14 — library only… nothing here is called from `cli.py`/`sync.py` yet
   (Phase 15's job).** … that module stays in place, unmodified, and
   still the one `sync_vendor` actually calls … The two modules coexist
   through Phase 14; `grounded_description.py` is only deleted once Phase
   15 rewires …". All of this is obsolete now that the transition is
   complete.

## B. Passage-level candidates (trim within an otherwise-current section)

6. **Intro, second paragraph (currently ~L10–44).** "As of Phase 19 …"
   through the renumbering note. A phase-stamped status snapshot ("Both
   are now `done`", "neither a `v0.1` nor a `v0.2` tag/release has been
   cut yet", "renumbered from the original Phase 9 during this rework").
   Replace with a plain inventory of implemented components + a pointer to
   `planning/ROADMAP.md` / `planning/CONTEXT.md` for status.

7. **Core data model — `VendorConfig` bullet (currently ~L49–59).**
   "`context_path` (a Phase 5 field) was removed in Phase 7 …; the
   per-vendor `depth` toggle … was removed in Phase 16 once usage-driven
   enrichment … made it meaningless". Current-truth: "There is no depth
   toggle; a legacy `depth = "…"` line still parses without error."

8. **Core data model — `VendorDigest` bullet (currently ~L70–81).**
   "renamed from Phase 5's `gap_analysis` field in Phase 7", "the same
   pattern `index.py` established in Phase 4", "An earlier `is_stale` stub
   on this class, speculatively added in Phase 1, was removed in Phase 6".

9. **Symbol/purpose extraction (currently ~L181).** "generalized from
   private per-adapter helpers in Phase 2".

10. **Tree generation (currently ~L191–204).** "**since Phase 13**, that
    root is …", "This is a real, visible output change: `FILETREE.md` now
    reflects …", "wired into `sync.py` (Phase 4)". Describe the
    clone-or-fallback root in the present tense.

11. **Tree generation — action-pointer bullet (currently ~L236–245).**
    "implemented in Phase 5 via the `action_pointer` parameter above
    (mechanism unchanged by Phase 7's gap-analysis-to-grounded-description
    swap)", "(Phase 16, `decisions/0035`)".

12. **Per-vendor CLAUDE.md structure (currently ~L307–351).** "(the
    `**Depth:**` line was removed in Phase 16 along with the field)";
    "both `staleness.py` (Phase 6) and `index.py` (Phase 4, …)"; "As of
    Phase 16 … this section no longer consults it at all"; the entire
    "**Phase 14 adds a second, narrower write path**" paragraph, esp.
    "Section 4's from-scratch render path used to differ (gated on `depth
    is FULL` …); Phase 16 … drops that gate too". Reduce to: both write
    paths use the same "is there enrichment content" test.

13. **Two consumption modes (currently ~L359–390).** "for every tracked
    vendor since Phase 13's universal cloning"; "Since Phase 7, the
    snapshot is a shallow `git clone` … rather than a copy of the local
    install"; "falls back to the original Phase 4 behavior"; "As of Phase
    4: `index` **reads each vendor's already-synced `CLAUDE.md`** … even
    after Phase 5 adds an AI-gated step to `sync`".

14. **Staleness checking (currently ~L413, ~L436).** "same reasoning
    `index.py` (Phase 4) already established"; "As of Phase 16, this makes
    **no AI call**".

15. **Multi-tool export (currently ~L477–507, ~L518, ~L538).**
    "Originally implemented in Phase 7 as part of `codecompass promote` …;
    since Phase 15 …, `promote` is retired and a vendor's Skill/`.mdc`
    pair is instead written by `enrichment.apply_results`"; "no longer
    gated on a `depth = FULL` toggle, which no longer exists"; "the same
    category of manual-verification gap Phase 5 accepted"; the "retained,
    not replaced" framing on both the Cursor `.mdc` export and the
    `CLAUDE.md` routing table (implies a reader who expected a
    replacement).

16. **`/discovery` slash command (currently ~L546, ~L563–568, ~L588,
    ~L593–609).** "**New in Phase 17.**"; "as of this phase … see
    `planning/CONTEXT.md` for the current status of this gap" (twice —
    open-gap / TODO narration that points readers out of the doc);
    "`skill_scan.scan_skills` (Phase 12's mapping module — the name
    predates this phase …)"; "`doc_artifacts.kind`'s CHECK constraint was
    widened for this, `schema_version` bumped from `"1"` to `"2"`, with
    `open_graph` migrating an already-existing pre-Phase-17
    `context-graph.db` by dropping and recreating …" (migration history).

17. **Chat REPL (currently ~L621–623, ~L652, ~L657–659, ~L684).** "what
    changed in Phase 19 is framing, not behavior"; "**implemented (Phase
    8).**"; "renumbered from the original Phase 9 during this rework — see
    `planning/ROADMAP.md`'s renumbering notes"; "Phase 20's REPL routing
    reads …".

18. **Chat REPL — the `> **Historical note**` blockquote (currently
    ~L625–630).** Explicitly labelled a historical note. It records that
    `decisions/0012`'s "the REPL is the actual product" framing is
    superseded by `decisions/0034`. That supersession belongs in / is
    already in the ADRs; the current-truth doc should just state that chat
    is secondary.

19. **Retrofitting to existing projects (currently ~L738–825).** "This is
    Phase 15's rewiring of `decisions/0031` … and `decisions/0033` … into
    the actual CLI"; "**Phase A** (`decisions/0017`, Phase 7; extended
    Phase 15 with universal cloning …)"; the entire "**Routing table /
    tool Skill refresh timing (Phase 20).**" paragraph ("Earlier phases
    regenerated them *before* Phase B ran, so a vendor enriched in that
    same invocation still showed `Enriched: no` … confirmed directly
    during this project's first live enrichment run. `sync`'s
    whole-project branch previously never called this regeneration at
    all"); "the CLI reference's earlier draft syntax was corrected to
    match in Phase 4"; "`requirements.txt` (Phase 7 addition)"; "**Phase
    B** (`decisions/0031`, `decisions/0033`, wired in Phase 15)"; "`sync`
    had already had a `--budget` flag before Phase 15, guarding its
    then-existing `depth = FULL` per-vendor regeneration path; that path …
    is gone as of Phase 16"; "`promote` is retired (`decisions/0033`) —
    its three former jobs … are these two phases' automatic outcomes".

20. **Context graph — schema bullets (currently ~L887–951).** Per-column
    phase stamps throughout: "`spec_doc`/`project` added in Phase 21",
    "`vendor_doc`/`vendor_upstream` added in Phase 27", "`doc_relations_
    edges` (Phase 21, widened Phase 29 …)", "`doc_chunks` (Phase 32)",
    "**Not** the `DocChunk`/`EXPLAINS` tables from the former phase-9d
    design that `decisions/0032` explicitly excluded", "`doc_relation_
    enrichment` (Phase 22)", "`relation_label` (Phase 31, `decisions/0045`
    …)", "Added to an existing on-disk database via `ALTER TABLE … ADD
    COLUMN`, not the drop-and-recreate approach `doc_artifacts`'s own
    migration uses".

21. **Context graph — row-dataclass paragraph (currently ~L958–973).**
    "This is a deliberate Phase 10 design choice … the detection logic
    that will construct these rows in Phases 11–13 …" — written from a
    past vantage point about work now long done.

22. **Context graph — query-function bullets (currently ~L997–1085).**
    "`used_at`, Phase 30 — surfaces `uses_edges`' existing file/line data,
    previously collapsed to just `usage_count`"; "`doc_code_trace` …
    (Phase 30)"; "`heading` (Phase 32)"; "`doc_relations` … (Phase 21)";
    "`relation_enrichment_candidates` … (Phase 22, extended Phase 28)";
    "`target_doc_artifact_name` (Phase 28) is …"; "`record_relation_
    enrichment(… relation_label=None)` (Phase 22; `relation_label` added
    Phase 31)".

23. **Batched enrichment (currently ~L1102–1167).** "**Selection is
    usage-driven, not `Depth`-driven** — the whole point of
    `decisions/0031`, already reflected in Phase 10's
    `graph.enrichment_candidates` even though `Depth` itself isn't removed
    until later"; "flagged for empirical tuning once Phase 15 makes a real
    multi-vendor batched call reachable"; "reworked from the old
    per-vendor formula (`grounded_description.estimate_cost`)".

24. **Project-source usage detection (currently ~L1171, ~L1187–1218).**
    "**New in Phase 11 — the first module to inspect the *consuming
    project's* source at all.**"; the entire "**Phase 26** adds an
    attribute-resolution upgrade …" paragraph including "This closed a
    real gap found via `/discovery` against this repo itself: `import
    anthropic`-style usage … never resolved to symbol-level `uses_edges`";
    "This is exactly why `filetree._iter_files` became the public,
    parameterizable `iter_source_files(…)` in this same phase".

25. **Populating the graph (currently ~L1228, ~L1241–1254).** "added to
    `sync.py` in Phase 11"; "Phase 12 adds real `doc_artifacts`/… data
    (below)"; "matching `decisions/0025`'s existing rebuild-trigger
    posture, carried into `decisions/0032`".

26. **Doc & wide skill mapping (currently ~L1261–1300).** "**New in Phase
    12 — still not CLI-visible (Phase 15's job); this phase only populates
    the five tables `rebuild_project_graph` previously passed empty lists
    for.**"; "`build_doc_chunks(…)` (Phase 32)"; "(Phase 29 widened the
    kind filter to include `vendor_doc` …)"; "Phase 32 additionally
    attempts to attribute each match …"; "Takes `project_root` (beyond the
    phase plan's originally sketched two-arg signature)".

27. **Spec-doc detection & relationship graph (currently ~L1359–1426).**
    "**New in Phase 21 — part 1 of a new three-way relationship feature …;
    Phase 22 adds AI enrichment over the edges this phase detects,
    deliberately separate.**"; "`doc_mapping.py` gains one function (Phase
    29 later widens its source argument …)"; "(originally `spec_doc` only;
    Phase 29 widens it to `{spec_doc, vendor_doc}`)"; "Phase 32
    additionally attempts chunk attribution …"; "Phase 32 adds one more
    call, `build_doc_chunks(…)`"; "Tracks fenced-code-block … state and
    never treats a line inside one as a heading candidate (Phase 34) —
    confirmed live against this repo's own `docs/cli-reference.md` and
    `vendor/anthropic/src/MIGRATION.md`".

28. **Relationship enrichment (currently ~L1444–1563).** "**New in Phase
    22 — part 2 of the three-way relationship feature …**" plus the
    sibling-module aside ending "the same way `enrichment.py` itself
    ported that shape from the deleted `grounded_description.py`"; the
    three bold phase-headed change paragraphs — "**Phase 28 — the excerpt
    is centered on the actual mechanical mention …** Each candidate's
    `source_excerpt` used to be a fixed `source_text[:4_000]` … the model
    never saw the sentence … and filled in a plausible-sounding but
    ungrounded summary"; "**Phase 31 — a closed-taxonomy `relation_label`
    …**" including the `ALTER TABLE` note and "leaving every pre-existing
    row with `relation_label = NULL` until its next natural
    re-enrichment"; "**Phase 32 — the excerpt prefers the matched chunk's
    own text over Phase 28's fixed-window guess …** Phase 28's
    needle-re-derivation-plus-fixed-window logic is otherwise completely
    unchanged and remains the fallback … not deleted, not made
    unreachable"; "No file-level fallback cache the way vendor enrichment
    has (Phase 14)".

29. **Vendor-embedded upstream docs (currently ~L1567–1624).** "**New in
    Phase 27 — … that had no `doc_artifacts` row at all before this phase,
    since every project-tree scanner … deliberately prunes `vendor/`
    (Phase 15, …)**"; "at this phase, only spec docs scan outward,
    `decisions/0037` — Phase 29 below changes this"; "At this phase, no
    changes to `build_documents_edges`/… themselves were needed … — Phase
    29 below is the first phase to actually change either of the first
    two"; "At this phase a vendor doc is never a relation source … — Phase
    29 below adds a vendor doc's *outgoing* mentions too".

30. **`undo` (currently ~L1689–1691, ~L1741–1744).** "**New in Phase 18
    (`decisions/0036`).** … is the first command whose job is to *remove*
    generated output rather than produce it"; the aside "unlike
    `skill.py`'s/`sync.py`'s locally-duplicated `_open_graph_readonly`,
    drift between two independent copies of *this* regex would be …".

31. **Cost model (currently ~L1764–1814).** "As of Phase 15, **Phase B is
    the sole AI cost center in this codebase**"; "Unlike the retired
    `promote`, Phase B is **cached**"; "reworked from the old per-vendor
    formula `grounded_description.estimate_cost` used"; "same
    abort-before-any-spend contract the retired `promote`/`sync --budget`
    guaranteed"; "`cli._refresh_generated_artifacts` still runs once at
    the end of the invocation (Phase 20; …)"; "**Phase 22 folds spec-doc
    relationship enrichment … into this same cost center, not a second
    one.** `relation_batch_count`/`relation_candidates` — both optional,
    defaulting to `0`/`None` so pre-Phase-22 callers are unaffected";
    "**As of Phase 16, there is no other cost path.** The old `depth =
    FULL` per-vendor grounded-description regeneration … is fully deleted,
    along with the `Depth` field that gated it".

32. **Known footguns — history stamps throughout (currently ~L1818–1953).**
    "**`VendorDigest.is_stale` was removed in Phase 6**, not left as a
    stub"; "`_load_config` and `claude_md.render_vendor_claude_md` are
    both implemented (Phases 1 and 4) — the CLI skeleton's old
    `_write_claude_md` `NotImplementedError` stub was removed in Phase 4"
    (no current footgun at all — pure history); "**`CargoAdapter.readme_
    and_api_surface()`'s output format changed in Phase 3**"; "the module
    that replaced `grounded_description.py` in Phase 16"; "not yet
    actually exercised against a live key as of Phase 19"; "(every vendor,
    since Phase 13 — no longer gated on a now-removed `FULL` toggle)";
    plus scattered "as of Phase 2" / "Documented limitation, not solved in
    Phase 2" / "(added in Phase 4)" stamps.

## C. Passages that are not just historical but now self-contradictory

**Resolved in Phase 43b** (`planning/phase-43b-standing-doc-drift-checks.md`)
— all 4 items below were fixed directly in `architecture/overview.md`,
verified against `src/` (not merely trimmed): item 33 deleted (no
equivalent behaviour survives — `sync_vendor` never makes an AI call);
item 34 re-attributed from the deleted `grounded_description.py` to
`enrichment.py` (which still carries the same constants, one renamed);
item 35 had its `depth = full`/`FULL` qualifier removed (the underlying
full-overwrite behaviour is unconditional, universal per Phase 13); item
36 rewritten to match `enrichment.py`'s own already-correct docstring
(`VendorConfig` no longer has a `depth` field at all). Kept below as the
historical record of what was wrong and why — Phase 61 needs no further
action on these 4.

33. **Known footguns — "Grounded description is fully regenerated
    (re-cloned and re-purchased) on every `sync` run" (currently
    ~L1903–1907).** Directly contradicts `## Grounded description —
    retired` and `## Cost model` ("`sync`/`check --fix` make no AI call at
    all"). `codecompass.grounded_description` no longer exists. This bullet
    is now false, not stale-but-true.

34. **Known footguns — "`grounded_description.py`'s `_RAW_TEXT_CHAR_CAP`
    (50,000), `_DOCS_FILE_CAP` (5), and `_ESTIMATED_COST_PER_CALL_USD` …"
    (currently ~L1908–1913).** Describes constants in a deleted module.

35. **Known footguns — "`sync_vendor` fully overwrites `vendor/<name>/` on
    every call … (for `depth = full`) the entire `vendor/<name>/src/`
    snapshot is deleted and recopied each time" (currently ~L1949–1953).**
    References `depth = full`, which the same file says was removed in
    Phase 16. The underlying behaviour (full overwrite, no incremental
    update) is still current; the `depth = full` qualifier is not.

36. **Batched enrichment — "`VendorConfig.depth` has no real meaning on
    this path … it's set to `Depth.FULL` as the closest existing label, a
    value `skill.py` never actually reads" (currently ~L1157–1160).**
    References `VendorConfig.depth` / `Depth.FULL` as live code, while
    Core data model says the `depth` toggle "was removed in Phase 16".
    Phase 61 should confirm against `src/` which is accurate and reconcile.

## Count

**36 candidate passages** (5 section-level, 27 passage-level trims, 4
now-self-contradictory corrections — **the 4 corrections were resolved in
Phase 43b**, leaving 32 still outstanding for Phase 61).
