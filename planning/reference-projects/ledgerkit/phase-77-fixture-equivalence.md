# Phase 77 task-context evaluation — pre-dispatch fixture equivalence check

Both clones forked from one seed clone of Ledgerkit at the same commit,
before either was touched further — the same seed-then-fork design
Phase 76's own third amendment established, reused here rather than
reinvented.

- **Seed clone / both arms' commit:** `6c90b4ca3e6c10951cb400e43db4b90bfccc5909`
  (confirmed identical in both `baseline-clone` and `treatment-clone` via
  `git rev-parse HEAD`).
- **Directory diff** (`diff -rq baseline-clone treatment-clone`,
  excluding `.git`/`context-graph.db`/`vendor.toml`): the **only**
  difference is `treatment-clone/.claude/commands`/`.claude/skills` —
  CodeCompass's own generated `/discovery` slash command and tool Skill,
  produced by `codecompass sync` in the treatment clone only. No other
  file differs.
- **The distinction between arms is context availability only, not
  repository state** — confirmed directly, not assumed: both clones
  contain byte-identical Ledgerkit source; treatment additionally has a
  real, synced `context-graph.db` (first-party source fully indexed,
  `meta.source_index_version` present) and the generated Skill/slash-
  command artifacts that reference it; baseline has neither.
- **Read-scope symmetry** (`L-062`): both dispatched agents are scoped to
  read only their own assigned clone's own tree — stated explicitly in
  each dispatch prompt.
