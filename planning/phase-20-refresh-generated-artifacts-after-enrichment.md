# Phase 20: Refresh generated artifacts after enrichment

## Scope

Fixes the graph/enrichment ordering gap first flagged after Phase 18 and
confirmed with two concrete, reproduced symptoms during this project's
first live enrichment run (see `planning/CONTEXT.md`'s account of that
session): generated project-level artifacts (the root `CLAUDE.md`
routing table, the tool-level Skill, and the context graph's own
knowledge of what Phase B just wrote) lag one whole sync cycle behind a
vendor's first enrichment.

This is actually **two related gaps**, not one, both fixed by the same
change:

1. **Ordering, in bare `codecompass`/`_bootstrap`**: `rebuild_project_graph`
   → `update_root_claude_md`/`write_tool_skill` → `_maybe_run_enrichment`
   — the routing table and tool Skill are regenerated *before* Phase B
   runs, so they show pre-enrichment state (`Enriched: no`) for a vendor
   that gets enriched in that same invocation. Confirmed directly: after
   this project's own first enrichment run, `CLAUDE.md`'s routing table
   still showed all four vendors as unenriched until a separate,
   manually-run `codecompass index`.
2. **Missing entirely, in `sync`'s whole-project branch**: `sync` never
   calls `update_root_claude_md`/`write_tool_skill` at all — confirmed by
   grep during Phase 17's implementation (its plan incorrectly assumed a
   third trigger point there). So a whole-project `sync` — with or
   without enrichment — never refreshes the routing table or tool Skill,
   only `index()` or `_bootstrap` do.

Both gaps also mean `context-graph.db` itself doesn't know about
Skill/`.mdc` files Phase B just wrote (`skill_scan.scan_skills` hasn't
re-run since), so `codecompass undo`'s graph-backed enumeration and
`codecompass query skills` also miss a vendor's brand-new per-vendor
Skill until the next whole-project sync.

**Covered:**
- New `cli._refresh_generated_artifacts(project_root, configs) -> None`:
  `rebuild_project_graph(configs, project_root)` (a second pass — see
  Design decisions for why re-running this specific function, not a
  lighter partial update, is the right fix) → `load_routing_rows` →
  `update_root_claude_md` → `write_tool_skill` → `write_discovery_command`.
- Called **once, unconditionally, at the very end** of both `_bootstrap`
  and `sync`'s whole-project branch — *after* `_maybe_run_enrichment`
  returns, whether or not it actually enriched anything (see Design
  decisions on why unconditional, not conditional on "did enrichment do
  something").
- The *existing* `rebuild_project_graph`/`update_root_claude_md`/
  `write_tool_skill`/`write_discovery_command` calls that currently run
  *before* `_maybe_run_enrichment` in `_bootstrap` are **not removed** —
  the graph must still exist before `enrichment.select_candidates` can
  read usage-proven candidates from it. Only the routing-table/tool-Skill/
  discovery-command regeneration moves to the new post-enrichment step;
  the pre-enrichment graph rebuild stays exactly where it is.
- `sync`'s whole-project branch gains the post-enrichment refresh call
  for the first time — closing gap 2 above, not just gap 1.
- Resolve, by reading the actual current code (not guessing): what should
  happen to the post-enrichment refresh if `_maybe_run_enrichment` itself
  raises (a budget-exceeded abort, `typer.Exit(code=1)`) — should the
  routing table/tool Skill still refresh to reflect whatever Phase A
  alone accomplished, or should the command exit without refreshing them
  at all? Today's behavior (refresh happens *before* the budget check can
  fail) means a budget-exceeded bootstrap still leaves a freshly-generated
  (pre-enrichment) routing table behind. Preserving "the routing table is
  always left in a consistent, freshly-generated state after any
  `codecompass`/`sync` invocation, success or budget-abort" is the
  recommended bar — implement whichever control-flow (try/finally, a
  returned status instead of a raised exception, etc.) achieves that
  most simply given the actual current `_maybe_run_enrichment` code.
- Tests: `tests/test_cli.py` — a whole-project `sync`/bare `codecompass`
  run that triggers enrichment leaves the routing table and tool Skill
  showing post-enrichment `Enriched: yes` status in the *same*
  invocation (the direct regression test for gap 1); a whole-project
  `sync` with zero enrichment candidates still refreshes the routing
  table/tool Skill at least once (closing gap 2, previously untested
  since it never happened); `codecompass undo --dry-run` run immediately
  after a triggering enrichment sees the newly-written per-vendor
  Skill/`.mdc` (the direct regression test for the `undo`-freshness
  symptom this phase also closes).

**Explicitly deferred / out of scope:**
- Any optimization to skip the second `rebuild_project_graph` pass when
  nothing was actually enriched (it's deterministic and free — a
  redundant pass costs CPU time, not correctness or money — this phase
  prioritizes a simple, uniformly-correct "always refresh at the end"
  model over that micro-optimization; revisit only if the redundant pass
  proves slow on a large real project).
- Any change to `enrichment.py`, `graph.py`, or the enrichment
  cost/consent flow itself — this phase is purely about *when* already-
  correct generation logic re-runs, not what it does.

## Design decisions

**A second full `rebuild_project_graph` pass, not a lighter targeted
update.** Considered adding a narrower "just re-scan skills" function
instead of re-running the whole graph rebuild (usage detection, doc
mapping, symbol collection, skill scanning). Rejected: `graph.
rebuild_deterministic` (Phase 10) was deliberately designed as a single
wipe-and-rewrite transaction with no partial-update mode — introducing
one now, just for this one caller, would be new surface area and a new
way for the graph to drift from a full, consistent rebuild, for a
performance concern that doesn't yet have evidence behind it (a
whole-project sync's usage-detection/doc-mapping work has never been
reported as slow in this project's own testing).

**Unconditional refresh, not gated on "did Phase B do anything."**
Simpler to reason about and test: every whole-project `codecompass`/
`sync` invocation ends in the same, predictable state — routing table,
tool Skill, and graph all freshly consistent with whatever just happened,
Phase A alone or Phase A+B together. A conditional "only refresh again if
enrichment actually ran" would save one redundant rebuild in the common
case (nothing new to enrich) at the cost of a second code path to keep
correct.

## Files

- `src/codecompass/cli.py` — new `_refresh_generated_artifacts`; call
  sites added to `_bootstrap` and `sync`'s whole-project branch; the
  existing pre-enrichment `rebuild_project_graph` call in `_bootstrap`
  stays, its adjacent `update_root_claude_md`/`write_tool_skill` calls
  move to the new post-enrichment step.
- `tests/test_cli.py` — three new/extended cases per Scope above.
- `architecture/overview.md` — "Retrofitting to existing projects" and/or
  "Cost model" sections updated to describe the corrected refresh timing.
- `planning/ROADMAP.md`, `planning/CONTEXT.md`, `CHANGELOG.md`.

## Verification

- `pytest` — full suite passes, including the three new/extended cases.
- `ruff check .` — clean.
- Manual, against a **scratch project** with a real, small dependency
  actually imported in its source (real API cost): run bare `codecompass`
  with a confirmed/`--yes` enrichment trigger; in that *same* invocation's
  output, confirm the printed routing table (or a follow-up `cat
  CLAUDE.md`) already shows the enriched vendor as `Enriched: yes` —
  no separate `codecompass index` required. Immediately run `codecompass
  undo --dry-run` and confirm the vendor's per-vendor Skill/`.mdc` paths
  are listed (previously omitted at this exact point).
- Manual: whole-project `sync` in a project with zero enrichment
  candidates still visibly refreshes `CLAUDE.md`'s routing table (e.g.
  touch its mtime, or change a vendor's installed version and confirm the
  table's Version column updates from a `sync` alone, not requiring a
  separate `index` call).
