# Project context

This file reflects the *current* state of the project — overwritten at
each stopping point, not appended to. See `CHANGELOG.md` and git history
for the log of how it got here.

## Current phase

**Phase 12: Doc & wide skill mapping — done.** Phases 0-11 remain `done`.
Executing MVP (v0.2) per `planning/v0.2-implementation-execution-plan.md`:
one implementation subagent per phase, independently re-verified, one
commit per phase, strictly in order.

## What was just completed

Implemented `planning/phase-12-doc-and-wide-skill-mapping.md`: new
`src/codecompass/doc_mapping.py` (`collect_vendor_doc_artifacts`,
`build_documents_edges`, `build_routes_via_edges`,
`build_depends_on_edges`) and new `src/codecompass/skill_scan.py`
(`scan_skills` — globs `.claude/skills/**/SKILL.md` +
`.cursor/rules/*.mdc`, minimal custom frontmatter extractor, no YAML
dependency; `build_skill_mentions_edges` — word-boundary matching, not
substring). `sync.rebuild_project_graph` (Phase 11) extended to call all
four new functions and pass real data into `rebuild_deterministic`'s
five previously-empty parameters.

Verified independently: `pytest` 296 passed/1 skipped, `ruff check .`
clean, `git diff --stat` matches the plan's Files list exactly (only
`sync.py` + `architecture/overview.md` modified, two new modules + two
new test files — no test-file touches were needed this time). Manually
reviewed both new modules in full: word-boundary regexes correctly
`re.escape`d, self-dependency edges correctly excluded in
`build_depends_on_edges`, doc artifacts for a not-yet-synced vendor
correctly skipped rather than pointing at a nonexistent file.

Two signature deviations from the plan's literal prose, both reasoned
and correct: `build_documents_edges`/`build_skill_mentions_edges` gained
an explicit `project_root: Path` parameter (the plan's prose omitted it,
but both functions must read artifact file text off disk, and
`DocArtifactRow.path` is a natural-key relative path per `graph.py`'s
existing convention — there's no way to satisfy "read its file text"
without it). `skill_scan.py` imports `_TOOL_SKILL_DIR_NAME`/
`_vendor_skill_name` directly from `skill.py` (a private cross-module
import) rather than duplicating codecompass's own naming-convention
literals locally — a deliberate single-source-of-truth choice, diverging
from the deptree-flattener precedent (which the plan explicitly says to
duplicate) but avoiding two independent copies of the same naming rule.

Manually confirmed against this repo itself: the tool Skill shows up as
a `doc_artifacts` row with `origin='codecompass_tool'`, mentioning all
four tracked vendors; every vendor currently routes to it (none
promoted, expected); `depends_on_edges` correctly shows `typer → rich`
(a real transitive relationship, both tracked); 58 `documents_edges` rows
populated from real `CLAUDE.md` text.

## Next concrete step

Implement `planning/phase-13-universal-source-cloning.md` next (same
pattern: dispatch, re-verify independently, doc-sync, commit, push).
Then 14 through 19, strictly in that order.

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
