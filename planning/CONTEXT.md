# Project context

This file reflects the *current* state of the project — overwritten at
each stopping point, not appended to. See `CHANGELOG.md` and git history
for the log of how it got here.

## Current phase

**Phase 11: Project-source usage detection — done.** Phases 0-9 and 10
remain `done`. Executing MVP (v0.2) per
`planning/v0.2-implementation-execution-plan.md`: one implementation
subagent per phase, independently re-verified, one commit per phase,
strictly in order.

## What was just completed

Implemented `planning/phase-11-project-source-usage-detection.md`: new
`src/codecompass/usage.py` (`detect_python_imports`/`detect_npm_imports`/
`detect_rust_imports`/`detect_imports_for_file`/`resolve_project_usage`,
`DetectedImport`), `filetree._iter_files` made public as
`iter_source_files` with configurable `prune_dirs`/`prune_globs` (zero
behavior change for existing callers), new `sync.rebuild_project_graph`
wired into `cli.py` at exactly two whole-project call sites (`_bootstrap`
with the full tracked vendor list, `sync`'s no-vendor-arg branch only).

Verified independently: `pytest` 270 passed/1 skipped, `ruff check .`
clean, `git diff --stat` matches the plan's Files list plus one
necessary, minimal test fix outside it (`tests/test_cli.py` — an
existing test faked `sync_all` but not the new `rebuild_project_graph`
call site, needed one line stubbing it; read the diff directly, confirmed
it's exactly that and nothing more). Manually reviewed `usage.py` in
full: sound design, correctly handles mixed-ecosystem projects (tries
every ecosystem's suffix-gated detector per file), Rust `use crate::X`
pattern generalized sensibly to real crate names, relative Python imports
correctly excluded (can never name an external vendor). One reasoned
judgment call worth remembering: `rebuild_project_graph` lets
`AdapterError` propagate uncaught rather than isolating it per-vendor —
deliberate, because `rebuild_deterministic` deletes any vendor absent
from the incoming list, cascading away its `vendor_enrichment` rows;
silently swallowing a transient adapter error would permanently destroy
paid enrichment data, so a hard failure was judged safer than silent data
loss.

Manually confirmed against this repo itself: `rich`/`typer`/`anthropic`
all show real usage edges with correct symbol-level resolution (e.g.
`from rich.console import Console` in `chat.py` resolves to `rich`'s own
`Console` symbol); `pipdeptree` correctly shows zero uses (invoked as a
subprocess, never imported); single-vendor `sync rich` left
`context-graph.db`'s mtime unchanged, confirming `decisions/0025`'s
posture holds under the new storage backend.

## Next concrete step

Implement `planning/phase-12-doc-and-wide-skill-mapping.md` next (same
pattern: dispatch, re-verify independently, doc-sync, commit, push).
Then 13 through 19, strictly in that order.

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
