# Phase 76 task-context evaluation — treatment agent report (verbatim)

Dispatched agent: `a5f0b0024e4d0e534`, CodeCompass installed and synced,
fixtures at
`/tmp/claude-1000/-home-cormac-projects-codecompass/phase76/eval/treatment-clone`
(+ `-feature`). Written to disk after the fact — see the phase retro's own
"What didn't work" for why (a recurrence of `L-063`).

Both tasks investigated. Full findings below.

## Task A — submodule scenario (`treatment-clone`)

**`codecompass query topology --json` output (submodules section):**
```
adapters/haskell:
  parent-pinned revision: dfd7a783667a91ba5a55a9f2b534cc0c1eb746ae
  checked_out_commit:     475bfe52e5bf78725377bc3fe2557b50fa74027e
  revision_matches_pin:   false
  child_is_dirty:         false
```

1. **Parent-pinned commit**: `dfd7a783667a91ba5a55a9f2b534cc0c1eb746ae` -- confirmed live via `git ls-tree HEAD adapters/haskell`, which shows the identical gitlink SHA.
2. **Actually checked out**: `475bfe52e5bf78725377bc3fe2557b50fa74027e` -- confirmed live via `cd adapters/haskell && git rev-parse HEAD` (submodule is HEAD-detached at that commit, its own working tree is clean).
3. **Do they differ?** Yes (`dfd7a78...` vs `475bfe5...`; `git diff --submodule=log` shows this as a "rewind," i.e. the checked-out commit is an ancestor of the pinned one, not a divergent/newer commit).
4. **Committed parent state, or only local checkout state?** Only local, uncommitted checkout state. `git status` on the parent shows `modified: adapters/haskell (new commits)` under **"Changes not staged for commit"** -- not staged, not committed. `git diff --cached -- adapters/haskell` (index vs. HEAD) is empty, confirming the parent's index and its last commit both still point at `dfd7a78...`. So the parent repository's committed history is unaffected; only the submodule's physically-checked-out working directory differs from what the parent expects. No parent-repo commit is needed to "fix" the pin itself -- running `git submodule update` inside the parent would realign the checkout to the pin (or, if the new commit were intentional, `git add adapters/haskell && git commit` would move the pin forward instead).

**What codecompass told me vs. what I had to verify myself:** `codecompass query topology` gave me the two SHAs and the `revision_matches_pin: false` verdict directly -- that answered items 1-3 completely. It did *not* tell me item 4 (committed vs. uncommitted) -- its JSON has no field distinguishing "differs because of an uncommitted local checkout" from "differs because the pin itself needs updating in a new commit." I had to determine that myself with `git status`, `git diff --cached`, and `git ls-tree HEAD`.

## Task B — worktree scenario

**`codecompass query topology --json` run from `treatment-clone`:**
```
worktrees:
  treatment-clone          (current) branch=main                        HEAD=46ab3c5... is_dirty=true
  treatment-clone-feature  (other)   branch=codecompass-phase76-eval-feature HEAD=46ab3c5... is_dirty=null  ["not probed"]
```

**Run again from `treatment-clone-feature`:**
```
worktrees:
  treatment-clone-feature  (current) branch=codecompass-phase76-eval-feature HEAD=46ab3c5... is_dirty=true
  treatment-clone          (other)   branch=main                        HEAD=46ab3c5... is_dirty=null  ["not probed"]
```

1. **Same repo, two worktrees -- not separate repos.** Evidence (live, not from codecompass): `treatment-clone-feature/.git` is a *file*, not a directory, containing `gitdir: .../treatment-clone/.git/worktrees/treatment-clone-feature`. `git rev-parse --git-common-dir` from `treatment-clone-feature` resolves to `treatment-clone/.git`. `git worktree list`, run from either directory, lists both paths under one repo. codecompass's own topology output pointed at this too (it lists both under one `repository.common_dir`), but I confirmed it independently with the commands above rather than trusting it alone.
2. **`treatment-clone-feature` as "current":** branch `codecompass-phase76-eval-feature`, HEAD `46ab3c573b759124445208d2c5726b00ec55c987`, **dirty** -- confirmed live: `git status` shows `modified: README.md` (unstaged; the diff adds the line `eval scenario edit`).
3. **`treatment-clone` as "the other worktree":** branch `main`, HEAD `46ab3c573b759124445208d2c5726b00ec55c987` (same commit as feature -- both branches currently point at the same SHA) -- confirmed live via `git rev-parse HEAD` and `git branch --show-current` run directly in that directory. Its dirtiness I already knew independently from Task A (it *is* dirty -- the submodule gitlink diff), but codecompass, when asked from the feature directory's own db, reported it as `null`/"not probed" rather than guessing.
4. **Live vs. cached, and does codecompass say which?** Yes -- explicitly. `codecompass query topology --help` states outright: *"Git repository topology (worktrees, submodules) as of the last `sync` -- never invokes `git` itself, on any code path."* This is a hard documented guarantee, not something I had to infer. Consistent with that: each checkout has its **own separate** `context-graph.db` file (`treatment-clone/context-graph.db` mtime 14:55, `treatment-clone-feature/context-graph.db` mtime 14:58 -- different files, different sync times, verified with `find`/`ls -la`). That's why `is_dirty` is populated for whichever worktree is "current" *relative to whichever db you're querying* (accurate as of that checkout's last sync) but shows `null`/"not probed" for the sibling worktree -- codecompass won't fabricate a live git-status read of a directory it isn't rooted in. Note the JSON payload itself carries no sync timestamp field, so you can't tell purely from the output *how* stale it might be, only that it's a snapshot in principle (from the `--help` text) -- everything I reported as "live" (branch names, HEADs, dirty flags, the README diff content, the worktree-vs-repo relationship) I re-verified with direct `git` commands rather than relying on codecompass for it.

## Assessment: how much codecompass actually helped

- It was a fast, correct **first-pass answer** for almost everything factual and static: both submodules' pinned vs. checked-out SHAs and match/mismatch verdict, the worktree list with branches and HEAD commits, and it correctly self-identified which directory was "current" in each invocation.
- It explicitly refused to guess at the non-current worktree's dirtiness (`null`/"not probed") rather than silently being wrong -- a good, honest signature, and its own `--help` text tells you up front it's a **sync-time snapshot that never shells out to git**, so you know not to trust it for "right now" facts.
- What it could **not** answer and required ordinary Git tools for: (a) whether a pin/checkout mismatch is committed-parent-state vs. purely local uncommitted state (needed `git status` + `git diff --cached`); (b) live confirmation that two directories are truly worktrees of one repo, via `.git` file contents and `git rev-parse --git-common-dir` (codecompass's claim was consistent but I verified it independently rather than take it on faith); (c) the actual live dirty content/diff (`git diff`) and the fact that the "other worktree" figure could be stale/unknown at all -- the `--help` text made this a documented gap rather than a silent one; (d) any sync-time metadata (there's no timestamp in the JSON) -- I had to find the two separate `context-graph.db` files and their mtimes myself to understand *why* the two invocations gave different completeness of information.

## Commands/tools actually run

```
codecompass query topology                              # in treatment-clone
codecompass query topology --json                        # in treatment-clone
codecompass query topology --help
codecompass --help
codecompass query topology --json                        # in treatment-clone-feature

git status                                                # treatment-clone
git submodule status                                      # treatment-clone
git ls-tree HEAD adapters/haskell                         # treatment-clone
git ls-tree HEAD protocol/codecompass-adaptor-protocol    # treatment-clone
git diff --submodule=log -- adapters/haskell              # treatment-clone
git diff --cached --submodule=log -- adapters/haskell     # treatment-clone
cd adapters/haskell && git rev-parse HEAD && git status   # submodule itself

git worktree list                                         # treatment-clone
cat .git ; ls -la .git                                    # treatment-clone (directory form)
git rev-parse --git-common-dir                            # treatment-clone
git branch --show-current && git rev-parse HEAD           # treatment-clone
git status --porcelain=v1 --branch                        # treatment-clone

cat .git                                                   # treatment-clone-feature (file form, gitdir: ...)
git rev-parse --git-common-dir                             # treatment-clone-feature
git branch --show-current && git rev-parse HEAD            # treatment-clone-feature
git status                                                  # treatment-clone-feature
git worktree list                                           # treatment-clone-feature
git diff README.md                                          # treatment-clone-feature

find . -iname "context-graph.db*" ; ls -la (each dir)      # to find per-checkout db files/mtimes
```
