# Phase 76 docs-drift audit (MODE 1 — per-phase) — RE-AUDIT

**Scope audited this pass:** commit `0db8c12` (`docs(phase-76): fix
drift audit findings -- README.md/ai-docs/README.md never mentioned Git
topology awareness`), applied on top of the state this file's own first
pass (superseded below) already audited (`46ab3c5`, `92e6e8e`). This is
a re-audit, not a fresh from-scratch pass: it (a) independently verifies
both fixes' claims against the real `src/codecompass/git_topology.py`,
`sync.py`, and `cli.py` source directly — not against the fix commit's
own summary — and (b) confirms nothing else drifted as a side effect of
the edit, and that the first pass's other findings still hold.

**Verdict: NO DRIFT.** Both prior blocking findings are fixed and their
fix text is accurate. No new drift introduced by the edit itself. The
first pass's "verified accurate" set is unchanged (no commits have
touched those files since).

## Re-verification of the two fixes

### Finding 1 (was blocking) — `ai-docs/README.md` "It doesn't touch git" — FIXED, verified accurate

New text (`ai-docs/README.md:74-80`):

> **It never mutates git state.** No commits, no `git add`/`rm`, ever —
> including in `undo`. As of Phase 76, it does *read* Git worktree/
> submodule topology (`codecompass query topology`) — always read-only
> plumbing commands (`rev-parse`, `worktree list`, `ls-tree`, `status
> --porcelain`, `config -f .gitmodules`), never a command that changes
> repository state, and only during `sync` — `query topology` itself
> reads the persisted graph, never invoking `git` at all.

Checked directly against source, not the fix commit's own message:

- **No write operation anywhere in `git_topology.py`** — confirmed by
  reading the full file (479 lines): every one of its 8 `git`
  subprocess invocations (`rev-parse --show-toplevel --git-common-dir`,
  `remote get-url origin`, `worktree list --porcelain`,
  `status --porcelain` ×2 call sites, `config -f .gitmodules --list -z`,
  `ls-tree HEAD -- <path>`, `rev-parse HEAD`, `symbolic-ref --short
  HEAD`) is a read. No `commit`, `add`, `rm`, `push`, `checkout`, or any
  other mutating verb appears in the file.
- **"only during `sync`"** — confirmed: `detect_git_topology` is called
  from exactly one call site in the entire `src/` tree,
  `src/codecompass/sync.py:354`; `grep -n detect_git_topology
  src/codecompass/*.py` returns only that one call plus its own
  definition.
- **"`query topology` itself reads the persisted graph, never invoking
  `git` at all"** — confirmed directly in `src/codecompass/cli.py`: the
  `query_topology` command (`cli.py:914`) calls only
  `_open_graph_for_topology` (opens `context-graph.db`, or returns
  `None` if absent) and `graph.topology_profile(conn)` — no `git`
  subprocess call, no import of `git_topology` in the render path. The
  command's own docstring states this explicitly and the code matches.
- **Minor, non-blocking observation:** the parenthetical command list
  (`rev-parse`, `worktree list`, `ls-tree`, `status --porcelain`,
  `config -f .gitmodules`) omits two of the module's eight real
  subprocess calls — `remote get-url origin` and `symbolic-ref --short
  HEAD` — both also read-only. The governing sentence ("always
  read-only plumbing commands... never a command that changes
  repository state") is not falsified by this omission since it doesn't
  claim the parenthetical is exhaustive, but a slightly more careful
  reader could momentarily wonder whether `remote get-url` (which does
  touch network config, unlike the others) is covered. Not blocking;
  not re-flagging as drift — noted for `docs-maintainer` only if this
  file is touched again for another reason.
- **New "What it does" bullet** (`ai-docs/README.md:44-49`) — content
  ("mechanical worktree and submodule facts... persisted at the last
  `sync`... a submodule's parent-pinned commit from what's actually
  checked out... Requires Git 2.5+") matches `git_topology.py`'s own
  `WorktreeInfo`/`SubmoduleInfo` dataclasses (`pinned_commit` vs.
  `checked_out_commit` vs. `revision_matches_pin` fields) and its
  module docstring's own claim that no Git feature newer than
  `git worktree`/`--git-common-dir` (Git 2.5, July 2015) is required —
  confirmed, no `--path-format` or other post-2.5 flag anywhere in the
  file.

### Finding 2 (was blocking) — `README.md` "Core idea" missing Git topology bullet — FIXED, verified accurate

New bullet (`README.md:150-154`):

> **Git repository topology awareness** (`codecompass query topology`):
> distinguishes a worktree of *this* repository from a genuinely
> separate project, and a submodule's parent-pinned commit from what's
> actually checked out — read-only, persisted at the last `sync`, never
> a live `git` call. Requires Git 2.5+.

Checked directly:

- "distinguishes a worktree of *this* repository from a genuinely
  separate project" — matches `TopologyStatus.DETECTED` vs. `NOT_GIT`
  and the `worktree_root`/`common_dir` identity fields
  (`git_topology.py:104-112`).
- "a submodule's parent-pinned commit from what's actually checked
  out" — matches `SubmoduleInfo.pinned_commit` vs.
  `checked_out_commit`/`revision_matches_pin` (`git_topology.py:92-100`,
  `428-432`).
- "read-only, persisted at the last `sync`, never a live `git` call" —
  same two facts re-verified above (single call site in `sync.py`;
  `query_topology` never shells to `git`).
- "Requires Git 2.5+" — same as above, confirmed.
- Formatting/placement: sits correctly inside the existing "Running
  codecompass gets you, for every tracked dependency:" bulleted
  enumeration (`README.md:112-154`), consistent bullet style with its
  siblings, no markdown breakage introduced.

## No new drift introduced by the edit

- `git diff 46ab3c5..HEAD -- docs/cli-reference.md
  architecture/overview.md architecture/context-graph-schema.md
  .claude/skills/codecompass/SKILL.md` is empty — none of these four
  files (independently verified accurate in the first pass) were
  touched by the fix commit or anything since; that verification still
  holds unchanged.
- `grep`-checked `README.md`, `ai-docs/README.md`, `docs/*.md`,
  `architecture/*.md`, `.claude/skills/codecompass/SKILL.md` for any
  remaining "doesn't touch git" / "zero Git awareness" / "no Git
  awareness" style sentence: none found anywhere.
- No other section of either edited file was touched by the diff beyond
  the two additions/one reword shown in `git show 0db8c12`; the
  surrounding "What it does NOT do" / "Core idea" list structure,
  numbering, and adjacent bullets are unchanged and still accurate.

## Not re-checked (out of scope for this pass, unchanged since first pass)

- `CHANGELOG.md`, `planning/ROADMAP.md` — outside this audit's named
  scope (`README.md`, `docs/`, `architecture/`, `ai-docs/`).
- Domain-claim staleness check (step 5) — still skipped; `docs/domain/`
  does not exist yet.
- `92e6e8e` (evaluation commit) — already out of scope per the first
  pass; untouched since.
