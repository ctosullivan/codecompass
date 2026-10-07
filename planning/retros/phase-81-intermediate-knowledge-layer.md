# Phase 81 retro — persistent bidirectional intermediate knowledge layer

## Goal

Introduce a persistent, bidirectional intermediate knowledge layer so
humans and external AI tools (ChatGPT, Copilot, Claude Code, plain Git
PRs) can safely refine CodeCompass's own structured project knowledge
through ordinary, editable Markdown — reconciled back against evidence
before anything becomes canonical, never fabricating observed truth,
never bypassing human authorisation, never conflating presentation
wording with semantic meaning.

## Delivered vs. planned

The plan was amended twice, same day, before implementation began — both
amendments are preserved in full inside
`planning/phase-81-intermediate-knowledge-layer.md` itself, since
neither had yet informed any real executed work at the time of either
correction. The second amendment's own central finding (zero new
persisted canonical fields needed, not even the one the first amendment
had retained) materially simplified everything that followed: no schema
migration risk, no new validation surface beyond two small, additive
checks, and every record `knowledge apply` produces is schema-
indistinguishable from one authored any other way.

Delivered, per the amended plan's own nine-stage sequence:

1. **Schema/validator foundations** — two new `assertion_kind` enum
   values (`workflow`, `constraint`); two new fail-closed checks
   (`check_requirement_cites_approved_decision`, verified safe against
   all nine pre-existing Requirement records before being added;
   `check_anchor_integrity`) — 47 tests, all passing, including the
   required reproduce-before-fix fixtures.
2. **Intermediate rendering** — `src/codecompass/knowledge_intermediate.py`:
   deterministic `intermediate/*.md` generation, dual-hash anchors
   (`base_semantic_hash`/`base_projection_hash`, corrected from the
   plan's own first-amendment single-hash design — see "What went
   wrong" below), bounded candidate regions, and a presentation cache
   that keeps canonical semantics and projection wording genuinely
   independent.
3. **Candidate detection** — `knowledge select-candidates`: mechanical
   only, no AI call, writes a durable TOML manifest reusing the frozen-
   snapshot format's own shape, mutates nothing canonical.
4. **Review/apply boundary** — `knowledge apply`: the sole write path,
   re-validates mechanically regardless of Stage 2's own annotation,
   re-checks `base_semantic_hash` against the live record to catch an
   apply-time race, refuses any unresolved concurrent-change conflict,
   and enforces the Requirement→Decision invariant using the real
   `decision:` field.
5. **Project-document grounding** — explicit `codecompass-grounded-by`
   markers, `CONTRIBUTING.md` brought into `spec_docs.py`'s own scanning
   scope (which required a second, previously-unplanned fix — see
   below), an advisory-only grounding-coverage report.
6. **Phase knowledge packages** — reused the existing per-slug
   `intermediate/` rendering directly; no new mechanism needed beyond
   what stage 2 already built.
7. **Workflow guide** — `docs/codecompass-knowledge-workflow.md`,
   self-contained, written for a cold reader (human or AI tool).
8. **Template support** — `codecompass-template` gained a separate,
   lightweight `optional-intermediate-knowledge/` directory, committed
   locally; **could not be pushed** — the template's remote is HTTPS
   with no stored credentials in this environment (the main
   `codecompass` repo uses SSH). Flagged as an outstanding action for
   the maintainer, not a Phase 81 code defect.
9. **Dogfood validation** — the real, 182-record `codecompass-domain`
   slug was rendered and validated end to end; a real, pre-existing,
   evidence-backed Ledgerkit-relevant slug (`hledger-depth`) was used
   for a genuine external-knowledge-refinement dogfood run: a simulated
   external-tool candidate addition went through detect → review → apply
   for real, landing at `status: proposed` with zero fabricated
   Observation/Evidence records, confirmed by direct inspection. README
   was grounded against a new, real, evidence-backed Claim
   (`CL-KNOW-001`) describing the mechanism itself, and the grounding
   was confirmed live via `knowledge status`.

**Scope honestly not delivered as a full Ledgerkit *code* change**: the
dogfood run exercises the knowledge-reconciliation mechanism against
real, already-verified Ledgerkit domain research, not a brand-new
Ledgerkit implementation task driven end-to-end through this session.
The plan's own vertical-slice scope is about proving the knowledge
layer's own mechanism, which this does; a full "pick a fresh Ledgerkit
roadmap item and ship it via this workflow" exercise is a larger,
separately-scoped follow-on validation, not required by the plan's own
non-goals-bounded slice.

## What went wrong, and was caught before shipping

- **A real hash-consistency bug**, caught by this project's own test
  suite, not by inspection: `render_block`'s own `projection_hash` was
  computed over the body text alone, while `detect_anchor_changes` read
  back the body text *plus* the leading newline the render template
  actually writes to disk. A byte-for-byte no-op re-render was
  misclassified as an edit. Fixed by hashing exactly the same `between`
  string in both places, and the no-op-round-trip test now pins this
  directly.
- **A regex bug in the grounding marker**: `[^->]+?` excludes both `-`
  and `>`, which also excludes the `-` that appears in every record id
  (`CL-DEMO-001`) — so no grounding marker ever matched anything with a
  real id in it. Caught by four failing tests in the same run; fixed by
  using a plain non-greedy `.+?` up to the literal `-->` terminator.
- **`CONTRIBUTING.md`'s exclusion removal had no actual effect on its
  own**: `_EXCLUDED_ROOT_NAMES` only ever filtered paths that had already
  matched a glob pattern in `_DEFAULT_GLOBS` — and `CONTRIBUTING.md` was
  never in that glob list in the first place, so removing it from the
  exclusion set alone did nothing. `"CONTRIBUTING.md"` had to be added to
  `_DEFAULT_GLOBS` directly. Caught by the existing `test_spec_docs.py`
  test actually exercising the real scan, not by assuming the one-line
  exclusion-list edit was sufficient.
- **A cosmetic id-token inconsistency**, found during the real
  `hledger-depth` dogfood run, not a unit test: `_next_id`'s own slug-
  token derivation (`hledger-depth` → `HLEDGERDEPT`) produced a
  different id style than that slug's own pre-existing convention
  (`CL-DEPTH-*`). Not a correctness defect — the new id is unique, valid,
  and fully schema-conformant — but a real, honest finding about
  `_next_id`'s own naive truncation heuristic, logged below for triage.

## Lessons learnt

- Testing a hash-based concurrency mechanism purely by code review would
  have missed the render/detect hash-consistency bug entirely — it only
  surfaced once a real byte-for-byte round-trip was asserted, which is
  exactly why the plan's own §16.1 required that specific test rather
  than trusting the design on paper.
- A regex negated-character-class bug (`[^->]` instead of `[^>]` or
  `.+?`) is an easy, specific mistake to make when hand-writing an HTML-
  comment-terminator pattern whose own payload contains some of the same
  characters the terminator uses — worth a specific note for any future
  anchor/marker-syntax work in this codebase.
- "Remove X from an exclusion list" and "X is now included" are not the
  same claim when the underlying mechanism is a positive glob match
  gated by a separate negative filter — removing the negative gate does
  nothing if the positive list was never permissive enough to reach X in
  the first place. Worth checking both halves of a two-list filter
  mechanism, not just the one named in the instruction.
- CodeCompass's own `codecompass-template` and its own repository use
  different git remote protocols (SSH vs. HTTPS) with different
  credential availability in this environment — worth recording so a
  future session doesn't re-discover this by a failed push.

## Process-improvement feedback

- `_next_id`'s truncation-based slug-token derivation should ideally
  detect and reuse an existing slug's own established id-token
  convention (scan existing `CL-<TOKEN>-NNN.yaml` filenames in the same
  directory, reuse `<TOKEN>` if exactly one already exists) rather than
  deriving a fresh token from the slug name every time — logged as a
  candidate learning below, not fixed in this phase since it's cosmetic,
  not a correctness or safety defect, and fixing it speculatively
  without a second real slug to validate against risks overfitting to
  one example.
