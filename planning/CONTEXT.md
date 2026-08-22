# Project context

This file reflects the *current* state of the project — overwritten at
each stopping point, not appended to. See `CHANGELOG.md` and git history
for the log of how it got here.

## Current phase

**Phase 14: Batched enrichment (Phase B) — done.** Phases 0-13 remain
`done`. Executing MVP (v0.2) per
`planning/v0.2-implementation-execution-plan.md`: one implementation
subagent per phase, independently re-verified, one commit per phase,
strictly in order.

## What was just completed

Implemented `planning/phase-14-batched-enrichment.md`: new
`src/codecompass/enrichment.py` (`select_candidates` — two-tier
DB-hash + file-hash cache check, per `decisions/0032`; `plan_batches`;
the batched `_TOOL_SCHEMA`/`run_enrichment_batches`; `apply_results` —
writes `graph.record_enrichment`/`record_symbol_enrichment`, calls the
new `claude_md.update_description_section` for an in-place `CLAUDE.md`
rewrite, generates per-vendor Skill/`.mdc` via a minimal `VendorDigest`;
`estimate_cost`/`check_budget` reworked to scale with batch count, not
vendor count). New `claude_md.update_description_section`/
`read_enrichment_hash`. **Library only, like Phase 10** — nothing wired
into `cli.py`/`sync.py` yet (Phase 15). `grounded_description.py`
untouched, still in active use for `depth = full` vendors until Phase
15/16 retire it.

Correctly reused the Phase 13 fix rather than reintroducing it: the new
in-place `CLAUDE.md` write path never checks `Depth` at all (matching
`decisions/0031` — enrichment eligibility is usage-driven), which is
safe specifically because `apply_results` only ever calls it for a
vendor that was just actually enriched, never for an ineligible one the
way a from-scratch `render_vendor_claude_md` re-render could. Documented
in both `claude_md.py`'s module docstring and `architecture/overview.md`.

Verified independently, including reading `enrichment.py`'s core logic
in full (not just trusting green tests, per Phase 13's lesson): `pytest`
336 passed/1 skipped, `ruff check .` clean, `git diff --stat` matches
exactly. One judgment call worth remembering: `EnrichmentCandidate`
gained an `installed_version` field beyond the plan's literal 3-field
sketch — genuinely required, since `run_enrichment_batches` must
recompute the cache-key hash with the *exact* same inputs
`select_candidates` used, or the cache silently breaks (a written hash
that never matches next run, re-purchasing enrichment every time).

## Next concrete step

Implement `planning/phase-15-cli-rewire.md` next — the integration
phase, the largest remaining one: wires together everything phases
10-14 built as libraries (`promote` removed, bare `codecompass` gains
`--yes`/`--budget` for Phase B's auto-triggered consent, new `query`
command group, `check`/`index`/`skill.py` migrated to graph-backed
enrichment status). Same pattern: dispatch, re-verify independently
(read the diff, don't just trust tests), doc-sync, commit, push. Then
16 through 19, strictly in that order.

**Still outstanding, not a blocker but worth remembering:**
- Once a Rust toolchain is available anywhere in the pipeline,
  `decisions/0014` requires validating the Cargo adapter against real
  `cargo metadata` output and a real crate — currently entirely
  unverified. Relevant to Phase 13's universal cloning.
- `extract_npm_symbols` (Phase 3) is untested against real-world `.d.ts`
  authoring styles beyond hand-written fixtures.
- `grounded_description.py`/`chat.py` have never been run against the
  real Anthropic API in this environment — a human must do this manually
  at least once, specifically against Phase 14's *batched* call shape,
  before trusting output quality (`decisions/0016`). Phase 15's manual
  verification step is the first point this becomes reachable end-to-end.
- `staleness.py`'s version parser has no real PEP 440/semver correctness
  — flag if it misclassifies a real-world version string.
- A formal trigger-accuracy evaluation harness for per-vendor Skills
  (`decisions/0013`) remains outstanding.
- Cursor `.mdc` export has no `globs` field — documented future
  refinement, not implemented.
- Whether/when to cut the `v0.1` tag is a separate, not-yet-made decision
  (`decisions/0022`); `v0.2`'s tag is not before Phase 19 is `done`
  (`decisions/0030`).
- This repo's own `rich` vendor never got its `depth = full`
  promotion/per-vendor Skill regenerated after an earlier session's
  file-loss incident (fully resolved otherwise, see git history around
  commit `f2f92bd` if the full account is ever needed) — harmless for
  phases 10-13's purposes, becomes relevant once Phase 14/15's manual
  enrichment verification step needs a real usage-proven vendor to test
  against (any of the four currently-tracked ones will do, once this
  repo's own source actually imports them somewhere `usage.py` can see).
