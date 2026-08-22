# Project context

This file reflects the *current* state of the project — overwritten at
each stopping point, not appended to. See `CHANGELOG.md` and git history
for the log of how it got here.

## Current phase

**Phase 13: Universal source cloning — done.** Phases 0-12 remain `done`.
Executing MVP (v0.2) per `planning/v0.2-implementation-execution-plan.md`:
one implementation subagent per phase, independently re-verified, one
commit per phase, strictly in order.

## What was just completed

Implemented `planning/phase-13-universal-source-cloning.md`:
`sync.sync_vendor` restructured so cloning (`resolve_and_clone`, falling
back to `_copy_source_snapshot` on failure) runs unconditionally for
every vendor, independent of grounded-description generation (still
gated on `depth is FULL`, and now additionally on this run's own clone
having succeeded). `FILETREE.md`/`filetree.json`/the symbol index now
render from the clone root when available, falling back to
`source_location()` — for every vendor, not just previously-`FULL` ones.

**A real bug was caught during independent verification (not by the
implementing subagent) and fixed before committing**: `VendorDigest.
description_error` is now set for a `depth = surface` vendor whenever
*its clone* fails — a legitimate, planned field reuse (the phase-13 plan
explicitly called for it) — but `claude_md._render_description_section`
didn't previously know the difference between "clone failed" and
"description generation failed," so a surface vendor with a failed clone
would have shown a misleading "## Description — Description unavailable:
`<clone error>`" section for an AI step it was never eligible for in the
first place. Fixed by gating that function on `config.depth is
Depth.FULL` *before* checking `description_error` at all — a surface
vendor now never shows a Description section, regardless of clone
outcome, matching the section's original "omitted entirely for surface"
design intent. New regression test:
`test_description_section_omitted_for_surface_vendor_even_with_error_set`
in `tests/test_claude_md.py`. This is exactly the kind of thing the
execution plan's "never trust the report alone" independent-verification
step exists to catch — worth remembering as a concrete example, not just
policy.

Verified independently (post-fix): `pytest` 299 passed/1 skipped, `ruff
check .` clean. `git diff --stat` matches the plan's Files list plus
`claude_md.py`/`test_claude_md.py` (the bug fix above — a direct,
necessary correction to this phase's own change, not scope creep) and
one pre-existing test's mock data (`test_sync_vendor_full_depth_writes_
overview`'s `action_pointer_file` no longer matched any file once
FILETREE.md started rendering from the clone root instead of
`source_location()` — a one-line fixture fix, flagged by the implementer).

## Next concrete step

Implement `planning/phase-14-batched-enrichment.md` next (same pattern:
dispatch, re-verify independently — including reading the actual diff,
not just trusting a clean test run, per this phase's lesson — doc-sync,
commit, push). Then 15 through 19, strictly in that order.

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
