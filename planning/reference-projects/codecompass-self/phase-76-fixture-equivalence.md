# Phase 76 task-context evaluation — pre-dispatch fixture-equivalence check

Per `planning/phase-76-git-repository-topology.md` §15 (third amendment):
independently re-derived and compared, by the lead, for both evaluation
clones, **before either agent was dispatched**. All facts identical —
the only difference between the two arms is CodeCompass's own
availability, confirmed below.

## Setup sequence actually run

1. Seed clone: `git clone --recurse-submodules
   /home/cormac/projects/codecompass` (real repository, at implementation
   commit `46ab3c5`) into a scratch seed directory.
2. `codecompass sync --yes --budget 0` run once in the seed.
   `git status --porcelain` in the seed was **already clean** after this
   sync — no normalization commit was needed, since `SKILL.md`'s own
   regenerated content had already been committed as part of `46ab3c5`
   itself (the implementing session ran `codecompass index` before that
   commit). The seed's own HEAD (`46ab3c5`) is therefore already the
   correct, fully-synced, clean baseline both arms fork from.
3. `baseline-clone` and `treatment-clone`: both `git clone
   --recurse-submodules <seed>` — both necessarily at the identical
   commit.
4. Identical scenario constructed independently in each clone, never
   committed to either:
   - Task A (submodule divergence): `git -C
     <clone>/adapters/haskell checkout 475bfe5` (the adapter's own real,
     prior commit — one before the real, current pin `dfd7a78`).
   - Task B (second worktree): `git -C <clone> worktree add
     <clone>-feature -b codecompass-phase76-eval-feature`.
   - Task B (dirty state): the same one-line append to `README.md` in
     each `<clone>-feature` worktree.
5. Treatment-only: `codecompass sync --yes --budget 0` run a second time,
   in both of treatment's own worktrees (main and `-feature`) —
   `baseline-clone` never has CodeCompass installed or run at all.

## Equivalence check (run after step 5, before any dispatch)

| Fact | `baseline-clone` | `treatment-clone` | Equal? |
|---|---|---|---|
| Parent-pinned `adapters/haskell` SHA (`git ls-tree HEAD`) | `dfd7a783667a91ba5a55a9f2b534cc0c1eb746ae` | `dfd7a783667a91ba5a55a9f2b534cc0c1eb746ae` | yes |
| Checked-out submodule SHA (`git -C adapters/haskell rev-parse HEAD`) | `475bfe52e5bf78725377bc3fe2557b50fa74027e` | `475bfe52e5bf78725377bc3fe2557b50fa74027e` | yes |
| Pin/checkout match-or-mismatch | mismatch (intentional divergence) | mismatch (intentional divergence) | yes |
| Worktree count | 2 (`main`, `-feature`) | 2 (`main`, `-feature`) | yes |
| Worktree branches | `main`, `codecompass-phase76-eval-feature` | `main`, `codecompass-phase76-eval-feature` | yes |
| Main HEAD | `46ab3c573b759124445208d2c5726b00ec55c987` | `46ab3c573b759124445208d2c5726b00ec55c987` | yes |
| Main `git status --porcelain` | ` M adapters/haskell` | ` M adapters/haskell` | yes |
| Feature worktree `git status --porcelain` | ` M README.md` | ` M README.md` | yes |
| Feature worktree HEAD | `46ab3c573b759124445208d2c5726b00ec55c987` | `46ab3c573b759124445208d2c5726b00ec55c987` | yes |
| Current-vs-sibling layout (main = current for the "main" dispatch, `-feature` = current for the "feature" dispatch) | same convention used in both dispatch prompts | same convention used in both dispatch prompts | yes |
| CodeCompass availability | not installed, no `context-graph.db` | installed, synced twice, real `context-graph.db` present (gitignored — confirmed absent from `git status` output above) | **the one, intended difference** |

**Result: equivalent on every fact either task tests.** The only
difference between the two clones is context availability, per the
requirement this check exists to satisfy. No discrepancy was found;
no fixture rebuild was needed.

## One disclosed, accepted limitation

Both dispatched agents run in the same host shell environment, so the
`codecompass` binary (`.venv/bin/codecompass`, this project's own
editable install) is technically invocable from either clone regardless
of which one an agent is told to treat as "its own." The baseline
dispatch prompt does not mention CodeCompass's existence at all and
explicitly instructs the agent to use only ordinary repository/Git
tools — a normal, low-risk instruction-following expectation for a
cooperative fresh agent, not a hard technical sandbox. This is the same
category of accepted limitation `planning/phase-76-git-repository-topology.md`
§15 already discloses for the seed's own shared `SKILL.md` content
(static command description, never live scenario data).
