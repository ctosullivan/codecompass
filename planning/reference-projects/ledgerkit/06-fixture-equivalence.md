# Phase 78 — pre-dispatch fixture-equivalence check

Per the plan's §5.2. Run before either Stage 1 agent is dispatched.

## Setup

- Seed clone: `git clone` of `/home/cormac/projects/ledgerkit`, checked
  out to the frozen commit `6c90b4ca3e6c10951cb400e43db4b90bfccc5909`
  (identical commit Phase 77's own trial used — unchanged, re-verified
  live before this trial: Ledgerkit's own upstream has not advanced).
- Forked into two scratch clones, `ledgerkit-baseline` and
  `ledgerkit-treatment`, before either was touched.
- `codecompass` (bare, zero-question bootstrap, `--budget 0`) run in
  `ledgerkit-treatment` only. Ledgerkit has zero third-party dependencies
  (`pyproject.toml`: `dependencies = []`), so `vendor.toml` bootstraps to
  0 vendors tracked — the deterministic project-graph rebuild (first-party
  source/symbol indexing, Phase 77) completed regardless, producing a
  real `context-graph.db` and the generated `.claude/commands/discovery.md`
  + `.claude/skills/codecompass/` artifacts. The subsequent AI-enrichment
  estimate (8 batches, ~$0.16, for 388 doc-relationship mentions) exceeded
  the `--budget 0` cap and was correctly declined — expected and
  irrelevant to this trial, which concerns first-party source/symbol
  indexing (`query source`/`query source-symbol`), not AI-written
  vendor/relation descriptions. `_refresh_generated_artifacts` ran
  regardless of the enrichment abort, confirmed live
  (`.claude/commands/discovery.md` and `.claude/skills/codecompass/`
  both exist).
- `ledgerkit-baseline` received no CodeCompass invocation of any kind.

## Equivalence checks (all passed)

1. **Both clones' `HEAD` matches the frozen SHA**: confirmed —
   `6c90b4ca3e6c10951cb400e43db4b90bfccc5909` in both, `git status --short`
   clean in both before any CodeCompass invocation.
2. **`diff -rq` of tracked files** (excluding `.git`, `context-graph.db`,
   `.claude`, `vendor.toml`): **empty** — the two clones' own tracked
   source is byte-identical.
3. **`.claude/agents/`** (Ledgerkit's own pre-existing, git-tracked agent
   roster — `.gitignore`'s own explicit `!.claude/agents/` exception):
   **`diff -rq` empty** — identical in both clones, confirming CodeCompass
   did not touch this pre-existing, tracked directory.
4. **`.claude/commands/` and `.claude/skills/`** (CodeCompass-generated,
   gitignored via `.claude/*`): present **only** in `ledgerkit-treatment`,
   absent from `ledgerkit-baseline` — confirmed via direct directory
   listing of both.
5. **`vendor.toml`/`context-graph.db`**: present only in
   `ledgerkit-treatment` (both gitignored in Ledgerkit's own `.gitignore`,
   confirmed directly), absent from `ledgerkit-baseline`.

**Conclusion: the two clones' own tracked content is verified identical;
the only difference is `ledgerkit-treatment`'s own CodeCompass-generated
artifacts (`vendor.toml`, `context-graph.db`, `.claude/commands/discovery.md`,
`.claude/skills/codecompass/`) — exactly Phase 77's own verified pattern.
Both clones are ready for Stage 1 dispatch.**
