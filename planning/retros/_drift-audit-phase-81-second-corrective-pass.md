# Phase 81 second corrective-pass drift audit

**Auditor:** docs-reconstructor (independent, MODE 1 per-phase drift audit)
**Scope:** commit `7a0e270` ("fix(phase-81): second corrective pass") —
`docs/codecompass-knowledge-workflow.md`, `docs/cli-reference.md`,
`README.md`'s grounding-marker migration — cross-checked against the real
implementation (`src/codecompass/knowledge_intermediate.py`,
`src/codecompass/cli.py`), `architecture/module-map.md`,
`architecture/overview.md`, `architecture/context-graph-schema.md`, and
`ai-docs/README.md`.

**Verdict: NO DRIFT** for the scope this pass's own diff touched, plus
one pre-existing, non-blocking completeness gap found and fixed in the
same sitting (see below).

## Method

Read `docs/codecompass-knowledge-workflow.md`'s "Project documentation"
section and `docs/cli-reference.md`'s knowledge-command section in full,
independent of `decisions/0074`'s own prose description of intent. Cross-
checked every claim against the real code: `_region_state_key`,
`parse_grounding_markers`, `acknowledge_stale_grounded_region`,
`advance_doc_chunk_baseline` in `knowledge_intermediate.py`; the
`doc-select-candidates`/`doc-acknowledge-stale`/`doc-acknowledge-chunks`
command definitions and live `knowledge --help` output in `cli.py`.
Checked `README.md`'s real grounded region (the migrated
`codecompass-grounded-by: CL-KNOW-001 region:intermediate-knowledge-layer`
marker) and its surrounding prose for any contradiction with the new
syntax or the corrected baseline-advancement behaviour. Ran a broad grep
across `docs/`, `architecture/`, `ai-docs/`, and `README.md` for every
named stale pattern: the pre-`decisions/0073` "cite an approved Decision
id" wording, automatic-baseline-advancement language, unconditional-
Claim-creation-on-`doc_region_edit` language, and positional-only
identity presented as the only option. Checked every `docs/domain/concepts/*.md`
page's own References block for any citation of a touched symbol,
`decisions/0071`-`0074`, or `planning/phase-81-*`.

## Finding-by-finding verification

### 1. `docs/codecompass-knowledge-workflow.md` — accurate

Covers the `region:<id>` syntax and its optionality/fallback-to-
positional/duplicate-fail-closed behaviour; states explicitly "detecting
a change is never the same as acknowledging it" with the three real
trigger conditions (first sighting, actual apply, explicit acknowledge
command); describes the `semantic_change` true/false branching correctly
(presentation vs. semantic, reviewer judgment, never mechanically
proven); describes the post-apply `grounded-by: CL-OLD, CL-NEW` marker
update; documents both `doc-acknowledge-stale`/`doc-acknowledge-chunks`
with correct semantics. Matches `acknowledge_stale_grounded_region`/
`advance_doc_chunk_baseline`'s real behaviour.

### 2. `docs/cli-reference.md` — accurate

Lists `doc-select-candidates`, `doc-acknowledge-stale <doc> <region>`,
`doc-acknowledge-chunks` with correct arguments/behaviour (verified
against the real `typer.Argument` signatures in `cli.py` and live
`--help` output), and correctly describes the corrected `apply`
concurrency check (region text + every cited record's hash, both
re-verified pre-write) and the `semantic_change` field default/effect on
a `doc_region_edit` item. The top-of-file command summary line and the
`knowledge` command's own header both list all seven subcommands.

### 3. `README.md` — accurate, migration clean

The real grounded region's marker is correctly migrated to
`<!-- codecompass-grounded-by: CL-KNOW-001 region:intermediate-knowledge-layer -->`.
Surrounding prose makes no claim about marker syntax or baseline
behaviour at all (it points to the workflow guide), so nothing to
contradict. No old-format or automatic-advancement language found
anywhere else in `README.md`.

### 4. `architecture/module-map.md` — still accurate, no update needed

Its `knowledge_intermediate.py` entry (renders/detects-via-dual-hash/
reconciles through detect-review-apply) doesn't assert anything about
baseline timing, dedup kind-awareness, or region identity that this pass
changed — accurate at its own level of detail.

### 5. `ai-docs/README.md` — pre-existing gap, FIXED (not new drift)

Mentions the knowledge layer but its command list was still the
pre-*first*-corrective-pass form (`render|select-candidates|apply|status`),
missing `doc-select-candidates` (introduced by the first corrective pass,
commit `8b43e38`) and this pass's `doc-acknowledge-stale`/
`doc-acknowledge-chunks`. Confirmed via `git blame` that this predates
commit `7a0e270` — not new drift caused by this pass. Fixed in the same
sitting: commit `42f9486` completes the command list and adds a sentence
noting that detecting documentation drift never by itself acknowledges
it.

### 6. Broad grep sweep — clean

Zero hits for "cite an approved Decision" (old wording) anywhere in
current docs; zero hits for automatic-baseline-on-detection language (the
only "baseline" references found are the new, correct statements that it
does *not* auto-advance); zero hits implying `doc_region_edit` always
creates a Claim unconditionally; zero hits presenting positional identity
as the only option (both `docs/codecompass-knowledge-workflow.md` and
`docs/cli-reference.md` correctly present `region:<id>` as primary with
positional fallback). The corrected `_CANDIDATE_INSTRUCTIONS` constant in
code and `docs/codecompass-knowledge-workflow.md`'s "How to add new
material" section (untouched by this diff, since it already matched)
agree word-for-word, consistent with `decisions/0074` point 5's own
claim.

## Domain-claim staleness check

Checked every `docs/domain/concepts/*.md` page's References block for any
citation of `knowledge_intermediate.py`, any touched symbol
(`_find_existing_promoted_record`, `_apply_candidate_addition`,
`_apply_doc_region_edit`, `parse_grounding_markers`, `CandidateFinding`),
`decisions/0071`-`0074`, or `planning/phase-81-*`. No matches in any
concept page — no domain-claim staleness candidates from this pass.

## Scope note

Did not re-verify the pre-existing (untouched-by-this-diff) parts of
`docs/codecompass-knowledge-workflow.md`'s rendering/anchor/status
sections, or re-audit the original Phase 81 feature end-to-end — scoped
strictly to what commit `7a0e270` changed plus the explicit checks named
above. `codecompass-template`'s public repo (`decisions/0074` point 6) is
a separate repository, not a current-truth doc folder in this one, and
was out of this audit's own scope (verified separately, by the lead, via
a direct `git fetch` against the real remote). `planning/` files are not
current-truth docs under this audit's rubric and were not checked.
