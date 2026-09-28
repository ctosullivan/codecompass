# Phase 76: Git repository topology awareness (worktrees + submodules) — plan

**Status:** planned (2026-09-28, amended 2026-09-28).

Direct user request. An evaluation/implementation phase: CodeCompass
gains mechanical awareness of Git worktree and submodule topology, so a
fresh agent can tell "different checkout of the same repository" apart
from "different repository" and "parent-pinned commit" apart from
"actually checked-out commit" — without CodeCompass creating, managing,
or mutating any of that topology itself.

**Amendment note (2026-09-28, same day as initial commit `7ac9f34`):**
direct user review of the committed plan found eight concrete, evidenced
issues before implementation began — a real migration-safety bug latent
in existing code that this phase's own schema bump would have triggered
for the third time; a worktree-root/invocation-root conflation; failure
states collapsing into ambiguous silence; an inappropriately-rigid
`NOT NULL` constraint; a validation sequence inconsistent with the
plan's own stated freshness contract; a task-context evaluation too weak
to trust on its own; a path-traversal risk in trusting `.gitmodules`
content; and a credential-leakage risk in persisting raw remote URLs.
This amendment fixes all eight, grounded in newly-gathered live evidence
(quoted throughout), while preserving every part of the original
direction the review confirmed as sound (§"Preserved from the original
plan, unchanged" at the end of each amended section, and restated in
full at the close of this document). No implementation code exists yet
for this phase — this remains a planning-only amendment.

## 0. Verified current state and HEAD

Confirmed live, not assumed, immediately before writing this plan (and
re-confirmed for this amendment):

- `git log --oneline -1` → `694e4f0` (`docs(phase-75): backfill real
  closeout commit SHA into L-062/L-063 promoted.md lines`), on `main`,
  clean working tree, at original plan-writing time; `7ac9f34`
  (`plan(phase-76): ...`) is the committed, now-being-amended plan
  itself.
- `planning/ROADMAP.md`: highest phase row is **75, `done`**
  (Priority A Ledgerkit validation, `context-evaluator` verdict PASS
  WITH GAPS / advantage LOW). Phase 76's own row (this plan) is
  `planned`.
- `git worktree list` → exactly one worktree (`/home/cormac/projects/codecompass`,
  `[main]`). No linked worktree exists in the real checkout today —
  validation needs a disposable one (§13).
- `.gitmodules` → two real submodules, confirmed live:
  `protocol/codecompass-adaptor-protocol` →
  `git@github.com:ctosullivan/codecompass-adaptor-protocol.git`;
  `adapters/haskell` → `git@github.com:ctosullivan/codecompass-adaptor-haskell.git`.
  Both currently checked out **exactly at** their parent-pinned commit —
  the "checked-out differs from pin" case must be constructed in a
  disposable fixture (§13).
- Neither submodule is a `vendor.toml` entry — confirmed live
  (`vendor.toml` lists only `anthropic`, `pipdeptree`, `rich`, `typer`,
  all `ecosystem = "python"`).
- `git --version` → 2.47.3. `pyproject.toml`'s `requires-python =
  ">=3.11"` — confirmed live — so `pathlib.Path.is_relative_to` (added
  3.9) is safely available for §12.6's path-safety check.
- **Newly verified for this amendment**: `git -C <path> rev-parse
  --path-format=absolute --show-toplevel --git-common-dir`, run live
  from `src/codecompass/` (a real subdirectory of this repository's own
  worktree), returns two lines —
  `/home/cormac/projects/codecompass` (the worktree root) and
  `/home/cormac/projects/codecompass/.git` (the common dir) — in one
  subprocess call, both already absolute, confirming this is the right,
  minimal primitive for §5's fix (a plain `git rev-parse
  --git-common-dir` with no `--path-format` returns a *relative* path
  instead, e.g. `../../.git` from that same subdirectory — this is
  exactly the mechanism the original plan under-specified).
- **Newly verified for this amendment**: `git config -f .gitmodules
  --list -z`, piped through `tr '\0' '\n'` for display, returns the
  same four `submodule.<name>.path`/`.url` lines as the non-`-z` form on
  this repository's own two-entry `.gitmodules` — confirming the
  NUL-delimited form (§12.9) is a safe drop-in that additionally protects
  against a pathological embedded-newline value, at no cost.
- **Newly verified for this amendment**: a live Python `urllib.parse`
  sanitizer (exact code in §12.7) run against six real and representative
  URLs (`https://user:token@example.com/repo.git`, a bare-token-as-
  username HTTPS form, this repository's own real
  `git@github.com:...` SCP-like submodule URLs, `ssh://git@example.com/...`,
  and two credential-free HTTPS URLs) produces exactly the intended
  result on every one: credentials stripped from `http(s)` forms only,
  every SSH/SCP-like form (including this repository's own real
  submodule URLs) left byte-for-byte unchanged. Not theoretical —
  actually executed during planning.
- **Newly (re-)verified for this amendment, the schema-migration
  finding motivating §11**: `git log --all -p -- src/codecompass/graph.py`
  shows `_SCHEMA_VERSION` has already been bumped twice
  (`41bae257`, Phase 60, `7`→`8`, for `vendors.ecosystem`'s CHECK
  constraint; `96428a8c`, Phase 62, `8`→`9`, for `symbols.export_kind`/
  `note`) for changes that touch **neither** `doc_artifacts` nor
  `documents_edges`/`doc_relations_edges` — yet
  `_migrate_doc_artifacts_constraints` (`graph.py:374-430`) fires on
  **any** `meta.schema_version` mismatch, unconditionally, and
  unconditionally drops and recreates all three of those tables when it
  fires. This is a real, latent, pre-existing defect this phase's own
  naive `"9"`→`"10"` bump would have reproduced a third time — see §11.

## 1. Problem statement and evidence

CodeCompass has **zero Git-topology awareness today** — confirmed by
reading, not inferring:

- `src/codecompass/discovery.py`, `spec_docs.py`, `usage.py` all treat
  `project_root` as an opaque directory; every CLI entry point in
  `cli.py` resolves "the project" as `Path.cwd()`, with no call anywhere
  to `git rev-parse`/`git worktree`/`git submodule`.
- `filetree.py`/`usage.py`/`sync.py` all *prune* `.git` when walking the
  filesystem (so a `.git` directory or gitlink is invisible content,
  never inspected) — deliberate for their own purpose (skip VCS
  internals when scanning for source files), but it means nothing
  downstream ever looks at `.git` for what it actually contains.
- `context-graph.db`'s schema (`graph.py`, schema version `9`) has no
  table for repository, worktree, or submodule identity of any kind.
- This project's own real repository is a genuine, non-synthetic test
  fixture for exactly this gap: two real Git submodules
  (`decisions/0058`), mounted specifically *because* they are separately
  licensed, separately versioned repositories — `decisions/0058`'s own
  "Consequences" section already names the real, load-bearing need this
  phase addresses: *"A version-compatibility matrix (CodeCompass version
  ↔ minimum protocol version ↔ tested adapter version(s)) must be
  documented and kept current — real, necessary bookkeeping now that
  three independent version streams exist."* Today that bookkeeping is
  entirely manual/tribal — `docs/developer/haskell-adapter-submodules.md`
  tells a *human* how to run `git submodule status`/`update`; nothing
  tells *CodeCompass* what the current pin vs. checked-out state is.
- Worktrees are motivated by this project's own agent-led development
  model (`CLAUDE.md` §8): multiple isolated branches of the same
  repository checked out concurrently is exactly how `Agent(isolation:
  "worktree")` dispatches already work in this environment — CodeCompass
  itself has no way to recognize two such checkouts as the same
  repository rather than two unrelated projects.

**Evidence this is not merely "nice to have," concretely, for this
project's own dogfooding**: a contributor bumping the Haskell adapter
submodule to a new upstream release today must manually run
`git submodule status`, cross-reference `.gitmodules`, check whether the
working tree already ran `git submodule update --remote` without a
committed gitlink bump, and update the compatibility matrix
`decisions/0058` calls for — all invisible to `codecompass query`,
`.claude/skills/codecompass/SKILL.md`, and the generated root
`CLAUDE.md` today.

## 2. Relationship to post-v1 Priority A and to deferred Phase 24

Unchanged from the original plan — re-confirmed, not revised, by this
amendment.

**Priority A (`decisions/0062`, `planning/ROADMAP.md`).** This is a
**new, direct-user-requested Priority A capability**, not a promotion of
an existing `context-gaps` entry — `planning/context-gaps/README.md`'s
own scope is "a relationship an agent *observed missing* during other
work," and no existing entry (`CG-001`, `CG-003`, `CG-007`, `CG-008`,
`CG-009`) is about Git topology; none is retroactively filed here, since
doing so would misrepresent this as a promoted observation rather than
directly commissioned work. It fits Priority A's own charter squarely:
"which repository/revision is authoritative" and "what is committed
versus merely present in a working tree" are prerequisite task-context
questions to *any* of the producers/consumers/siblings/execution-path
work Priority A already names — an agent that doesn't know it's looking
at a stale worktree, or that a submodule's checkout has drifted from its
pin, cannot correctly answer those other questions either. Distinct from
`CG-001`'s "task-relevance ranking" hypothesis and `CG-009`'s "no
first-party symbol index" gap — this phase adds a different, more
foundational layer (checkout/revision identity), not a fix to either of
those.

**Deferred Phase 24** (`planning/pre-v1-disposition.md` §3,
`planning/phase-20-chat-project-root-routing-design.md`) is
**"`codecompass chat` with no vendor argument" REPL routing** — whether
a chat question should load vendor-specific digest context or
project-wide context, keyed on generated-Skill-description matching.
This phase does not touch `chat.py`, does not implement project-root
routing, and does not change Phase 24's own scope, revisit trigger, or
status in any way — **it neither satisfies, partially satisfies, nor
supersedes Phase 24.** It is recorded here explicitly, per the user's
own instruction not to silently redefine it. One genuine, narrow
overlap worth flagging for whenever Phase 24 is actually picked up (not
acted on now): Phase 24's design never considered what "the project
root" means when a submodule or a second worktree is present — should a
question asked from inside `adapters/haskell/` route as "this project"
or as "the parent project's own submodule"? This phase's own topology
detection (§4) answers "what is the relationship," not "how should chat
route because of it" — that remains Phase 24's own future design
question, now with a concrete, mechanically-available fact source (and,
per this amendment's §5, a concrete distinction between the invocation
root and the Git worktree root) to design against if/when it is
revisited. `planning/CONTEXT.md`/`planning/ROADMAP.md`'s Phase 24
backlog row is **not** changed by this phase beyond this cross-reference
note.

## 3. Relevant current architecture and files

Read in full before writing this plan, and re-read in full for this
amendment (not summarized from memory):

- `src/codecompass/graph.py` — schema (`_SCHEMA_VERSION = "9"`), row
  dataclasses, `rebuild_deterministic`, `open_graph`. **Amendment: read
  all five existing `_migrate_*` functions in full, not just skimmed**
  (`_migrate_doc_artifacts_constraints`, `_migrate_doc_relation_enrichment_relation_label`,
  `_migrate_symbols_export_kind_note_columns`,
  `_migrate_symbol_enrichment_model_column`,
  `_migrate_vendors_ecosystem_constraint`). **Four of the five already
  use direct schema introspection** (`PRAGMA table_info`, or
  `sqlite_master.sql` text inspection) to decide whether *their own*
  migration is needed, explicitly and self-documentedly *because*
  `meta.schema_version`-based triggering is unsafe for a table holding
  paid enrichment or requiring precision about what actually changed —
  `_migrate_vendors_ecosystem_constraint`'s own docstring states this
  reasoning outright ("matching `_migrate_doc_relation_enrichment_relation_label`'s
  own 'introspect the real thing' style rather than
  `_migrate_doc_artifacts_constraints`'s version-difference style").
  **`_migrate_doc_artifacts_constraints` is the one outlier still using
  the crude global-version-mismatch trigger** — confirmed via git
  history (§0) to have already fired unnecessarily on both prior
  version bumps. This is the concrete, in-repository precedent §11's
  fix generalizes, not a novel pattern invented for this phase.
- `tests/test_graph.py` — confirmed to already carry extensive
  migration-regression coverage for `_migrate_doc_artifacts_constraints`
  (schema versions `"1"` through `"8"` each individually simulated and
  migrated to `"9"`), each asserting the literal string `"9"` as the
  post-migration value — **these existing assertions must be updated to
  `"10"` as part of this phase's own implementation** (§12), a
  mechanical consequence of the version bump that has apparently
  recurred at every prior bump too.
- `src/codecompass/sync.py::rebuild_project_graph` — the one
  orchestration function every detection module feeds into; `cli.py`'s
  `_bootstrap`/`sync`/`index` all call it with `project_root`.
- `src/codecompass/discovery.py`, `spec_docs.py`, `usage.py`,
  `doc_mapping.py`, `skill_scan.py` — the existing "pure detection
  module, graph-agnostic, `sync.py` converts to `graph.py` row types"
  pattern this phase's own `git_topology.py` follows.
- `src/codecompass/source_resolution.py` — the existing precedent for
  shelling out to real `git` (`shutil.which("git")` guard,
  `subprocess.run`).
- `src/codecompass/cli.py` — `query_app` Typer sub-app, five existing
  `query` subcommands, each with a `--json` flag and a `_graph_session`
  context manager; `Path.cwd()` is the only "project root" resolution
  anywhere in the file today.
- `src/codecompass/skill.py::render_tool_skill` — the generated
  `.claude/skills/codecompass/SKILL.md`; lists every `query` subcommand
  by hand *and* the graph's own table names in prose — the exact
  multi-module coordination shape `CG-001` was originally filed against.
- `scripts/check_user_docs.py::check_cli_commands_documented` and
  `check_generated_artifacts_match_source` — already mechanically catch
  a `CG-001`-shaped coordination gap in this phase's own implementation.
- `decisions/0057`, `decisions/0058` — the real, load-bearing reason
  this project's own submodules exist.
- `docs/domain/concepts/vendor.md` — confirms `VendorConfig` is
  narrowly `(name: str, ecosystem: Ecosystem)`, ruling `vendors` out as
  a home for submodules.
- `planning/v1-redefinition/reference-project-protocol.md` §2.2 (as
  amended in Phase 75, `L-062`) — scratch-clone-only working-copy
  discipline, **including explicit read-scope-symmetry guidance for any
  baseline/treatment comparison** — directly reused for §15's amended,
  strengthened task-context evaluation.

## 4. Proposed data model and terminology

Unchanged reasoning for rejecting `vendors`/`doc_artifacts` reuse (§4 of
the original plan); the table shapes themselves are revised by this
amendment (nullability, path-safety, sanitization) and one new
mechanism (topology status) is added.

**Investigated and rejected: reusing `vendors`.** A submodule has no
`Ecosystem`, no `vendor.toml` entry, and (per `decisions/0058`) is
mounted specifically as a *Git-level* construct independent of any
package manager. Rejected.

**Investigated and rejected: a generic `doc_artifacts`/`other`-kind
row.** A worktree or submodule is neither a document nor addressable by
the `mentions_artifact`/`mentions_dependency` word-boundary matchers.
Rejected.

**Decision: three new tables** (schema version `9` → `10`, migration
strategy fully redesigned in §11), mirroring the conceptual model the
user specified, **plus two new `meta` keys for top-level topology
status** (no new table needed for that — `meta` is already the graph's
existing key/value bookkeeping mechanism, e.g. `schema_version`,
`last_deterministic_rebuild_at`):

```
git_repositories   -- one row per canonical repository this checkout
                      (or any of its worktrees/submodules) belongs to
git_worktrees      -- N rows per repository: this checkout, plus every
                      sibling worktree observed via `git worktree list`
git_submodules     -- N rows per repository: every submodule this
                      project's own `.gitmodules` declares, present even
                      when some or all of its own facts are unresolved
meta.git_topology_status  -- 'detected'|'not_git'|'unavailable'|'partial'
meta.git_topology_reason  -- diagnostic text; NULL for 'detected'/'not_git'
```

```sql
CREATE TABLE IF NOT EXISTS git_repositories (
  id          INTEGER PRIMARY KEY,
  common_dir  TEXT NOT NULL UNIQUE,  -- absolute path to the shared .git
                                      -- (or bare) directory: identical
                                      -- for every worktree of one
                                      -- repository, the canonical
                                      -- identity key this phase uses
  origin_url  TEXT                   -- `git remote get-url origin`,
                                      -- sanitized (§12.7) before storage;
                                      -- nullable (no remote configured)
);

CREATE TABLE IF NOT EXISTS git_worktrees (
  id            INTEGER PRIMARY KEY,
  repository_id INTEGER NOT NULL REFERENCES git_repositories(id) ON DELETE CASCADE,
  worktree_path TEXT NOT NULL,        -- absolute path, resolved via
                                       -- `git rev-parse --show-toplevel`
                                       -- (§5), NEVER the raw invocation
                                       -- root when they differ
  is_current    INTEGER NOT NULL DEFAULT 0,  -- 1 for the worktree this
                                              -- context-graph.db lives
                                              -- in; 0 for a sibling
  branch        TEXT,                 -- short name (`refs/heads/`
                                       -- prefix stripped, §12.8); NULL
                                       -- when detached
  is_detached   INTEGER NOT NULL DEFAULT 0,
  head_commit   TEXT,                 -- NULL only for a truly unborn
                                       -- branch (no commits yet)
  is_dirty      INTEGER,              -- NULL = not probed. Always NULL
                                       -- for a non-current (sibling)
                                       -- worktree — this is a stated,
                                       -- permanent limitation of the
                                       -- data contract (§7.4/§8), not
                                       -- a transient gap
  is_bare       INTEGER NOT NULL DEFAULT 0,
  is_locked     INTEGER NOT NULL DEFAULT 0,
  is_prunable   INTEGER NOT NULL DEFAULT 0,
  UNIQUE (repository_id, worktree_path)
);
CREATE INDEX IF NOT EXISTS idx_git_worktrees_repository ON git_worktrees(repository_id);

CREATE TABLE IF NOT EXISTS git_submodules (
  id                    INTEGER PRIMARY KEY,
  parent_repository_id  INTEGER NOT NULL REFERENCES git_repositories(id) ON DELETE CASCADE,
  path                  TEXT NOT NULL,     -- mount path exactly as
                                            -- .gitmodules declares it,
                                            -- relative to the worktree
                                            -- root (§5) — always present:
                                            -- this row exists as soon as
                                            -- .gitmodules declares the
                                            -- path, regardless of how
                                            -- much else is resolvable
  is_path_safe          INTEGER NOT NULL DEFAULT 1,  -- 0 = the resolved
                                            -- path escaped the worktree
                                            -- root (§12.6) — every field
                                            -- below is left NULL/0 and
                                            -- NEVER probed when this is 0
  child_repository_url  TEXT,              -- from .gitmodules, sanitized
                                            -- (§12.7); NULL if absent/
                                            -- unparseable
  pinned_commit         TEXT,              -- **now nullable** (amended
                                            -- from the original plan's
                                            -- `NOT NULL`, §8): the
                                            -- gitlink SHA recorded in
                                            -- the parent's own tree
                                            -- (`git ls-tree HEAD --
                                            -- <path>`); NULL when
                                            -- .gitmodules declares the
                                            -- path but no gitlink exists
                                            -- in HEAD's tree yet (a real,
                                            -- honestly-representable
                                            -- mid-edit state, not an
                                            -- error) — never omits the
                                            -- row itself
  is_initialized        INTEGER,           -- NULL only when
                                            -- is_path_safe = 0 (never
                                            -- checked); else 0/1
  checked_out_commit    TEXT,              -- NULL if not initialized or
                                            -- not path-safe
  revision_matches_pin  INTEGER,           -- NULL unless BOTH
                                            -- pinned_commit and
                                            -- checked_out_commit are
                                            -- known; else 1/0
  child_branch          TEXT,              -- short name; NULL if not
                                            -- initialized, detached, or
                                            -- not path-safe
  child_is_dirty        INTEGER,           -- NULL if not initialized or
                                            -- not path-safe
  UNIQUE (parent_repository_id, path)
);
CREATE INDEX IF NOT EXISTS idx_git_submodules_parent ON git_submodules(parent_repository_id);
```

**No `observed_at`/timestamp column on any of the three** — fully wiped
and reinserted every `rebuild_deterministic` call, same category as
`doc_artifacts`; `meta.last_deterministic_rebuild_at` already answers
"as of when."

**No `origin`-style provenance enum** — every fact here is mechanically
derived from `git`, with no second, less-authoritative source it could
have come from. Provenance here is the deterministic-only model (§8)
plus, new in this amendment, the explicit epistemic-status model below —
not a per-row enum field.

**New: `meta.git_topology_status`/`meta.git_topology_reason`** — a
top-level, whole-detection-pass status distinct from any individual
row's own nullable fields (§8 explains the two-level distinction in
full): `detected` (repository/worktree-list/submodule-list enumeration
all succeeded structurally — individual facts within that structure may
still be legitimately unknown, e.g. an unresolved `pinned_commit`, which
is a *row-level* fact, not a whole-pass failure); `not_git` (confidently
determined: `project_root` is not inside a Git repository); `unavailable`
(the `git` executable is missing, or the very first repository-identity
command failed for a reason *other than* "not a repository" — e.g.
permission denied, a corrupted `.git`); `partial` (repository identity
was established, but a subsequent structural step — enumerating
worktrees, or enumerating `.gitmodules` — failed unexpectedly). This is
the direct fix for the requirement that CodeCompass must never display
"not a Git repository" when it actually could not determine that fact.

**Terminology** (for `architecture/`/docs use, §14) — restated with two
amendments (worktree-root distinction, submodule non-recursion made
explicit per the user's own request to clarify it, §16):

- **Repository** — identified by its `common_dir`. Not the same as
  "project" (`project_root`, the CLI's invocation root, may be a git
  repo, a subdirectory inside one, or not a git repo at all).
- **Worktree** — one checkout of a repository, identified by its own
  root directory (`git rev-parse --show-toplevel`) — **not** the
  invocation root a command happened to be run from, when the two
  differ (§5). A path, a branch or detached HEAD, a HEAD commit, and
  (for the current one only) a workspace/dirty state. Two worktrees of
  the same repository share `common_dir` and are never represented as
  separate `git_repositories` rows.
- **Submodule** — a mount point recorded in the *parent's* tree (a
  gitlink) plus `.gitmodules`, distinct from the child's own actual
  checkout state. **A `git_submodules` row is a topology *relationship*
  fact about the parent repository being inspected — it is not, and this
  phase never makes it, a recursively materialized child
  `git_repositories` row of its own.** If a submodule's own directory is
  itself later inspected directly (`codecompass sync` run *inside*
  `adapters/haskell/`), that produces its own, entirely separate
  `git_repositories` row in its own `context-graph.db` — the two are
  never linked to each other by this phase (§16).

## 5. Discovery / root-resolution changes required

**Amended.** The original plan's §5 stated `project_root` stays
unchanged everywhere and topology detection "runs from `project_root`,"
but §6's own detection notes then treated `project_root.resolve()` as
if it were necessarily the worktree root when matching the current
worktree in `git worktree list`'s output. **This is wrong when
CodeCompass is invoked from a subdirectory of a worktree** — e.g. from
`repo/src/` while the worktree root is `repo/` — confirmed live during
this amendment (`git rev-parse --show-toplevel`, run from
`src/codecompass/`, correctly returns the repository root two directories
up, not the invocation directory itself; §0).

**No change to `project_root`'s own meaning or resolution anywhere
else in the codebase** — this remains exactly `Path.cwd()`, unchanged,
consistent with the original plan. What changes is that `git_topology.py`
now **explicitly establishes and keeps distinct three separate paths**,
never conflating any two of them:

1. **Invocation root** (`project_root`) — wherever `Path.cwd()` (or a
   future `--root` argument, if one is ever added) points. This is
   `context-graph.db`'s own location (§10, unchanged) and the value every
   other detection module already receives.
2. **Git worktree root** — `git -C <project_root> rev-parse
   --show-toplevel` (or, for a bare repository, the directory containing
   `.git` itself — §7's edge-case notes). **This, not `project_root`, is
   the root every topology operation below is actually relative to.**
3. **Git common directory** — `git -C <project_root> rev-parse
   --git-common-dir` — the repository's own canonical identity (§4),
   identical from every worktree.

Both (2) and (3) are obtained from **one combined subprocess call**,
`git -C <project_root> rev-parse --path-format=absolute --show-toplevel
--git-common-dir` (confirmed live, §0, to return both as absolute paths
on two lines, in git 2.47.3 — `--path-format=absolute` has been
supported since Git 2.31, comfortably below what any environment running
this project's own `requires-python = ">=3.11"`-era tooling would
realistically have) — never guessed via filesystem walking (e.g. "walk
upward looking for a `.git` entry" was **not** implemented and is
explicitly rejected as a parallel, redundant, and strictly worse
mechanism now that the real primitive is confirmed to exist and work).

**Every subsequent topology operation is now stated relative to the
resolved worktree root, not `project_root`** (§7 gives the exact
commands):

- **Identifying which worktree is current**: each block in `git
  worktree list --porcelain`'s output is compared, resolved, against
  the **worktree root**, not `project_root` — when they're the same
  directory (the common case: CodeCompass invoked from the repository's
  own top level) this makes no observable difference; when they differ
  (invoked from a subdirectory) this is the fix that makes current-worktree
  identification correct instead of silently failing to match any block
  at all.
- **Locating `.gitmodules`**: read at `<worktree_root>/.gitmodules`,
  never `<project_root>/.gitmodules` — `.gitmodules` is defined by Git
  to live at a worktree's own top level; reading it relative to
  `project_root` would silently find nothing (or, worse, a coincidental
  unrelated file) when invoked from a subdirectory.
- **Resolving submodule mount paths**: `.gitmodules`'s own `path` values
  are declared relative to the worktree root and are resolved as
  `<worktree_root> / declared_path` (then checked for safety, §12.6) —
  never relative to `project_root`.
- **Running parent-tree Git operations** (`git ls-tree HEAD --
  <path>`, `git remote get-url origin`, `git worktree list`): all
  invoked with `-C <worktree_root>`, not `-C <project_root>` — for
  correctness, not merely style: `git -C <subdirectory> ls-tree HEAD --
  <path-relative-to-repo-root>` can silently resolve the wrong tree
  entry or none at all if the two roots differ.

**`context-graph.db`'s own placement is unchanged** (§10) — it remains
rooted at `project_root`, exactly as today. This amendment is
specifically about not *semantically conflating* that storage location
with the Git worktree root when they happen to differ; it does not move
where the database file lives.

**Still true, restated from the original plan**: this phase does **not**
walk upward from the worktree root looking for an ancestor repository
that treats it as *its* submodule — only descend to detect
worktrees/submodules the worktree root's own repository declares (§16).

**New tests required by this amendment** (§18): topology detection
invoked from the repository root, and from a real nested subdirectory of
the same repository, must both identify the same worktree root and the
same `common_dir`.

## 6. Topology status model (new section — amendment, was folded into
§8/§10 in the original plan)

Direct response to the review's finding that "not a Git repository,"
"`git` executable unavailable," "a `git` command failed," and "partial/
malformed topology" could previously collapse into the same observable
result.

```python
class TopologyStatus(str, Enum):
    DETECTED = "detected"
    NOT_GIT = "not_git"
    UNAVAILABLE = "unavailable"
    PARTIAL = "partial"
```

**Two distinct levels of uncertainty, never conflated** (this is the
core design resolving the review's concern):

1. **Whole-pass structural status** (`TopologyStatus`, above) — "could
   repository identity, the worktree list, and the submodule list each
   be enumerated at all." Determined once per `detect_git_topology`
   call; stored as `meta.git_topology_status`/`meta.git_topology_reason`
   (§4).
2. **Per-row factual completeness** — for a structure that *was*
   successfully enumerated, individual facts about one of its rows may
   still be legitimately unknown (an unresolved `pinned_commit`, an
   unprobed `is_dirty` for a sibling worktree, a `child_branch` that's
   `None` because the submodule isn't initialized). These are ordinary
   nullable columns (§4), never a reason to downgrade the whole-pass
   `TopologyStatus`, and never a reason to omit the row itself.

**Decision procedure** (exact order, each step's failure mode named):

1. `shutil.which("git") is None` → `UNAVAILABLE`, reason = `"git
   executable not found on PATH"`. Nothing further attempted.
2. `git -C project_root rev-parse --path-format=absolute --show-toplevel
   --git-common-dir` — on failure, **the stderr text is pattern-matched**
   (`"not a git repository"`, Git's own stable, documented message for
   this exact case) to distinguish:
   - Matches → `NOT_GIT`, reason = `None` (an expected, unremarkable
     outcome — most projects using CodeCompass are not Git
     repositories at all; this is not an anomaly worth a diagnostic
     string).
   - Does not match (permission error, corrupted `.git`, an unexpected
     exception, a timeout) → `UNAVAILABLE`, reason = the captured
     stderr/exception text (truncated to a reasonable length for
     storage/display). **This is the literal fix for "must not display
     'not a Git repository' when it actually could not determine that
     fact."**
3. On success: worktree root + common dir now known.
   - `origin_url`: `git -C <worktree_root> remote get-url origin` — a
     non-zero exit (no `origin` remote configured) is **normal, not an
     anomaly** — `origin_url = None`, status unaffected.
   - `git -C <worktree_root> worktree list --porcelain` fails
     unexpectedly → overall status becomes `PARTIAL`, reason = `"could
     not enumerate worktrees: <stderr>"`; `worktrees = ()`; submodule
     detection still proceeds independently (a worktree-list failure
     doesn't imply a submodule-detection failure).
   - No block in a successful `worktree list` result resolves to
     `<worktree_root>` → also `PARTIAL` (a genuine anomaly — the current
     worktree should always appear in its own listing), reason =
     `"current worktree not found in its own worktree list"`.
   - `.gitmodules` absent at `<worktree_root>` → zero submodules,
     **normal, not an anomaly** (most projects have none).
   - `.gitmodules` present but `git config -f <worktree_root>/.gitmodules
     --list -z` fails unexpectedly (malformed file) → overall status
     becomes `PARTIAL` (or stays `PARTIAL` if worktree listing already
     set it), reason appended/first-reason-kept (documented as
     first-failure-only, not an exhaustive multi-reason log — the
     smallest model that still tells a fresh agent "something is
     incomplete, here's a starting point," not a full diagnostic
     report).
   - Otherwise → `DETECTED`.

**CLI/JSON must render all four states distinguishably** — `not_git`
prints a plain, unremarkable "not a Git repository" line (unchanged from
the original plan's intent, now actually correctly gated only on a
genuine `NOT_GIT` determination); `unavailable` prints "Git topology
could not be determined (<reason>)"; `partial` prints whatever structure
*was* established, prefixed with a visible "topology partially
determined: <reason>" note rather than silently presenting incomplete
data as if it were complete; `detected` prints the full structure with
no caveat banner. §9 gives the exact rendering; §18 tests all four.

**Non-fatal to ordinary `sync`, in every case**: nothing in this
decision procedure raises or aborts `rebuild_project_graph` — the
status itself, not an exception, is how uncertainty is communicated,
consistent with "failures should still generally remain non-fatal to
ordinary CodeCompass sync." No evidence gathered during this amendment
suggests any topology-detection failure mode should gate `sync` itself;
this is restated as a deliberate, evidence-based choice, not an
oversight.

## 7. New module: `src/codecompass/git_topology.py`

Mirrors the existing `discovery.py`/`usage.py`/`spec_docs.py` shape: a
pure, graph-agnostic detection module; `sync.py` is the only place that
converts its output into `graph.py` row types.

```python
@dataclass(frozen=True)
class WorktreeInfo:
    path: str                    # absolute; the worktree's own root
    is_current: bool
    branch: str | None           # short name (§12.8); None if detached
    is_detached: bool
    head_commit: str | None
    is_dirty: bool | None        # None = not probed (always None for
                                  # a non-current worktree — a permanent
                                  # data-contract limitation, see §8)
    is_bare: bool
    is_locked: bool
    is_prunable: bool

@dataclass(frozen=True)
class SubmoduleInfo:
    path: str
    is_path_safe: bool           # False = declared path escaped the
                                  # worktree root (§12.6); every field
                                  # below is unset/False when this is
                                  # False, and was never probed
    child_repository_url: str | None   # sanitized (§12.7) before this
                                        # dataclass is ever constructed
    pinned_commit: str | None    # None = declared, but no gitlink
                                  # resolvable in HEAD's tree right now
    is_initialized: bool | None  # None only when is_path_safe is False
    checked_out_commit: str | None
    revision_matches_pin: bool | None   # None unless both
                                         # pinned_commit and
                                         # checked_out_commit are known
    child_branch: str | None
    child_is_dirty: bool | None

@dataclass(frozen=True)
class RepositoryTopology:
    status: TopologyStatus
    reason: str | None
    invocation_root: str          # str(project_root), always present
    worktree_root: str | None     # None only for NOT_GIT/UNAVAILABLE
    common_dir: str | None
    origin_url: str | None        # sanitized
    worktrees: tuple[WorktreeInfo, ...]
    submodules: tuple[SubmoduleInfo, ...]

def detect_git_topology(project_root: Path) -> RepositoryTopology:
    """Always returns a RepositoryTopology — never None, never raises.
    `status` tells the caller how much of the rest to trust; see §6."""
```

**`detect_git_topology` never returns `None`** (amended from the
original plan) — this removes the `None`-special-casing the review
flagged as one more place a real distinction could get silently lost;
`sync.py` (§12) checks `.status`, not identity-vs-`None`.

**Exact commands** (§6 gives the decision procedure; this gives the
concrete `git` invocations, chosen and verified live, §0):

1. `shutil.which("git")`; absent → `UNAVAILABLE` immediately.
2. `git -C project_root rev-parse --path-format=absolute --show-toplevel
   --git-common-dir` — one call, two output lines, both already
   absolute (§0/§5). Stderr pattern-matched per §6 step 2.
3. `git -C <worktree_root> remote get-url origin`, sanitized (§12.7)
   before ever being placed in `origin_url`.
4. `git -C <worktree_root> worktree list --porcelain` — the stable,
   documented, blank-line-delimited block format (`worktree <path>`,
   `HEAD <sha>`, `branch <ref>` or `detached`, optional `bare`/
   `locked [reason]`/`prunable [reason]`). Each block's path is resolved
   and compared against `worktree_root` (§5) to find `is_current`.
   **Dirty state is computed only for the current worktree**
   (`git -C <worktree_root> status --porcelain`, non-empty → dirty,
   counting untracked files — this phase's own explicit, stated
   definition) — never for a sibling, a permanent limitation stated
   explicitly in the data contract and CLI output (§8), not merely an
   implementation shortcut left undocumented.
5. **Submodules**: `git config -f <worktree_root>/.gitmodules --list -z`
   (NUL-delimited — §0/§12.9's robustness note), grouping
   `submodule.<name>.path`/`.url` pairs. For each declared path:
   - Resolve `<worktree_root> / declared_path`, verify with
     `Path.is_relative_to(worktree_root)` after `.resolve()` (§12.6) —
     if it escapes, `is_path_safe = False` and **no `git` command is
     ever run against that path**; the row is still emitted (path +
     `is_path_safe=False`, everything else unset).
   - `pinned_commit`: `git -C <worktree_root> ls-tree HEAD -- <path>` →
     parse the `160000 commit <sha>\t<path>` gitlink line; absent
     (no gitlink in `HEAD`'s tree — e.g. added to `.gitmodules` but never
     `git add`-ed) → `pinned_commit = None`, **row still emitted**
     (amended from the original plan, which incorrectly omitted the row
     entirely in this case).
   - `is_initialized`: does `<resolved-path>/.git` exist (file or
     directory)?
   - If initialized: `checked_out_commit` = `git -C <resolved-path>
     rev-parse HEAD`; `child_branch` = `git -C <resolved-path>
     symbolic-ref --short HEAD` (non-zero → detached, `None`);
     `child_is_dirty` = non-empty `git -C <resolved-path> status
     --porcelain`; `revision_matches_pin` = equality, **only when both
     SHAs are actually known** (amended: previously implicitly assumed
     `pinned_commit` was always present).
   - If not initialized, or not path-safe: the remaining fields stay
     `None`/unset, never guessed.
6. **Never recurse into nested submodules-of-submodules** — `.gitmodules`
   is read at exactly the worktree root's own level; a submodule's own
   submodules are this phase's explicit non-goal (§16).

**Additional edge cases** (restated from the original plan's own
dedicated table, folded in here rather than kept as a separate section,
each confirmed to still be correctly handled by the decision procedure
above — no behaviour change from the original plan on any of these,
only relocated for this amendment):

- **Invoked from a linked (non-main) worktree, not the main one**:
  `worktree_root`/`common_dir` still resolve correctly — `--show-toplevel`/
  `--git-common-dir` are defined by Git to work identically regardless
  of which worktree they're run from (confirmed live, §0, from a
  subdirectory of this repository's own single worktree; the same
  primitive applies unchanged when the worktree itself is a linked one).
  That worktree's own row gets `is_current=True`; the *main* worktree
  appears as an ordinary sibling row — no special-casing required.
- **Bare repository**: `is_bare=True` on its own worktree row (from
  `worktree list --porcelain`'s own `bare` marker); `head_commit`/
  `branch` may be present or absent depending on whether a HEAD ref
  exists; no crash either way.
- **Truly unborn branch** (fresh `git init`, no commits yet):
  `head_commit=None`, `branch` = the unborn branch name if resolvable,
  no crash.
- **Two worktrees of the same repository, one mid-rebase (detached
  HEAD, no branch)**: `is_detached=True`, `branch=None`, `head_commit`
  still populated — detached HEAD is a first-class, correctly
  representable state for either the current or a sibling worktree, not
  an error case.
- **Submodule checked out at a commit not reachable from the pinned
  commit's history at all** (an entirely different branch): still just
  `revision_matches_pin=False` — no attempt to characterize *how*
  divergent; explicitly deferred (§16).

## 8. Deterministic provenance and explicit-uncertainty rules

**Amended**: restates and sharpens the original plan's provenance
section against the review's "honest gaps over fabricated certainty"
concern.

- **Every fact is mechanically derived from a real `git` subprocess
  call, never inferred or AI-generated.**
- **No semantic relationship is created between a submodule and
  anything else** — `git_submodules` rows never assert, e.g., that
  `codecompass-adaptor-haskell` implements `codecompass-adaptor-protocol`;
  that would need independent evidence and its own relation kind,
  exactly as `CG-007`'s own precedent establishes for keeping mechanical
  and semantic relationships separate.
- **Two-level uncertainty, never conflated (§6)**: a whole-pass
  `TopologyStatus` (`detected`/`not_git`/`unavailable`/`partial`)
  answers "could the structure be enumerated at all"; per-row nullable
  fields answer "for a structure that was enumerated, which specific
  facts about it remain unknown." Neither is used as a stand-in for the
  other — a `partial` whole-pass status is never silently represented as
  a clean `detected` result with some fields merely absent, and a
  single row's own unresolved fact (e.g. an uninitialized submodule's
  `checked_out_commit = NULL`) never downgrades the whole-pass status,
  since that row's *declaration itself* was successfully and completely
  observed.
- **A declared submodule is never silently omitted.** Every path
  `.gitmodules` names produces a `git_submodules` row, regardless of how
  much else about it is currently resolvable — `path` and `is_path_safe`
  are the only two fields guaranteed non-null; every other field is
  allowed to honestly be `NULL`/unset rather than forcing the row out of
  existence (§4's schema; §7.5's detection logic). This is the direct
  fix for "do not silently erase a submodule... represent the known fact
  honestly."
- **A sibling worktree's branch/HEAD is "as observed at this worktree's
  own last sync," not live** — the same staleness contract every other
  graph fact already carries (`decisions/0025`). Stated explicitly in
  `docs/cli-reference.md`'s new section and in `query topology`'s own
  output.
- **Dirty/uncommitted state is only ever claimed for the current
  worktree, and this limitation is stated explicitly, not merely
  implied by an absent value** (amended: the original plan left this as
  an implementation detail; this amendment requires the CLI/JSON output
  itself to say "workspace: not probed" for a sibling worktree — §9 —
  rather than presenting a bare `null`/blank that a reader could mistake
  for "clean" or "unknown for some other reason"). `head_commit`/
  `pinned_commit`/`checked_out_commit` remain committed-repository facts,
  safe to compare across worktrees/syncs; `is_dirty` never is.
- **Credentials embedded in a Git remote URL are never persisted or
  surfaced anywhere** — `context-graph.db`, CLI text, `--json` output,
  the generated Skill, and any future agent-context surface all only
  ever see the sanitized form (§12.7); sanitization happens once, at
  detection time, before a `RepositoryTopology`/`SubmoduleInfo` object
  is even constructed — there is no code path that holds an
  un-sanitized URL past the point of the raw `git remote`/`git config`
  subprocess call that produced it.
- **Graceful, non-fatal degradation, at both levels of uncertainty**: no
  single `git` command failure — missing binary, non-repository root,
  an inaccessible or pruned worktree path, an unsafe submodule path, a
  malformed `.gitmodules` entry — ever raises or aborts `sync`. It is
  represented as a `TopologyStatus`, a `None` field, or an
  `is_path_safe = False` row, per the rules above — never as an
  exception propagating out of `rebuild_project_graph`.

## 9. Context / query / packet integration points

**Amended** to render the four-state status model (§6) and the
sibling-dirty-state disclosure (§8); otherwise as originally planned.

1. **New CLI command**: `codecompass query topology [--json]` — added
   to `cli.py`'s existing `query_app`, same `_graph_session`/`--json`
   pattern as `query vendors`/`query relations`. Reads
   `meta.git_topology_status`/`reason` first:
   - `not_git` → a plain "not a Git repository" line.
   - `unavailable` → "Git topology could not be determined (<reason>)."
   - `partial` → a visible "topology partially determined: <reason>"
     banner, **followed by** whatever structure was established (never
     silently suppressed).
   - `detected` → the full structure: repository identity, the active
     checkout's full detail (path/branch-or-detached/HEAD/dirty), every
     other known worktree (branch-or-detached/HEAD only, plus an
     explicit **"workspace: not probed"** line, never a bare blank —
     §8), and every submodule (path; `is_path_safe=False` rendered as
     "path escapes repository — refused" with nothing else shown for
     that row; otherwise child repository URL, parent-pinned revision
     — or "unresolved" when `NULL` — checked-out revision + match/
     mismatch, child branch/dirty if initialized).
   `--json` mirrors this exactly (`status`, `reason`, `repository`,
   `worktrees`, `submodules` keys — `repository` is `null` for
   `not_git`/`unavailable`).
2. **`skill.py::render_tool_skill`**: gains a `query topology` line in
   the Commands list and `git_repositories`/`git_worktrees`/
   `git_submodules` in the trailing table-name list — the exact spots
   `CG-001`'s own motivating example named. `check_cli_commands_documented`
   and `check_generated_artifacts_match_source` mechanically catch a
   miss here.
3. **`docs/cli-reference.md`**: a new `query topology [--json]` section,
   documenting all four status outcomes explicitly (not just the happy
   path) — required for `check_cli_commands_documented`.
4. **Generated root `CLAUDE.md`**: not changed — unchanged reasoning
   from the original plan (§16 restates the deferral).
5. **`planning/knowledge/<feature-slug>/context-packet.md`**: not
   modified by `sync` — unchanged from the original plan.

## 10. Cache / index implications

Unchanged from the original plan; re-confirmed, not revised.
`context-graph.db` stays exactly `project_root / "context-graph.db"`.
Each worktree keeps its own separate database file; recognition (via
the shared `common_dir` identity), not consolidation, is what this
phase adds. A full merged/shared-storage design was considered and
rejected as unnecessary for this phase's minimum capability (§16).

## 11. Migration strategy — schema-version safety (amended; this is the
fix for the review's most severe finding)

**The problem, confirmed with real evidence (§0/§3), not hypothetical**:
`_migrate_doc_artifacts_constraints` (`graph.py:374-430`) fires
whenever `meta.schema_version != _SCHEMA_VERSION` — *any* mismatch,
regardless of whether the actual change has anything to do with
`doc_artifacts`. `git log` confirms this has already happened twice
(Phase 60's `vendors.ecosystem` widening, `7`→`8`; Phase 62's
`symbols.export_kind`/`note` addition, `8`→`9`) for changes touching
neither `doc_artifacts` nor `documents_edges`/`doc_relations_edges` at
all. The original plan's naive `"9"`→`"10"` bump for three entirely new,
unrelated tables would have reproduced this a third time. The concrete,
user-visible risk this creates: **`open_graph` runs on every `query`
invocation, not only on `sync`** (`_open_graph_or_note`/`_graph_session`,
`cli.py`) — so a user who upgrades CodeCompass and runs `codecompass
query relations <doc>` *before* their next `sync` would silently have
their previously-synced `doc_artifacts`/`documents_edges`/
`doc_relations_edges` content dropped and left empty, purely because an
unrelated version number changed, with no `sync` in between to
repopulate it yet. This is not a data-loss risk in the "paid enrichment
lost forever" sense (those three tables are always fully rewritten by
the next `rebuild_deterministic` regardless), but it is a real,
concrete "opening an upgraded database before a full sync does not
behave predictably" failure — exactly the case the review named.

**The fix, grounded in this file's own existing, better precedent
(§3)**: rewrite `_migrate_doc_artifacts_constraints` to introspect
whether `doc_artifacts`/`documents_edges`/`doc_relations_edges` *actually*
need reconstruction, the same way `_migrate_vendors_ecosystem_constraint`
already introspects `vendors`'s own stored `CREATE TABLE` text instead of
trusting the global version number:

```python
def _doc_artifacts_schema_is_current(conn: sqlite3.Connection) -> bool:
    """True iff doc_artifacts/documents_edges/doc_relations_edges are
    already shaped exactly as the current _SCHEMA_SQL expects — checked
    by direct introspection, never by comparing meta.schema_version,
    per the same reasoning _migrate_vendors_ecosystem_constraint already
    established for `vendors` (graph.py, Phase 60)."""
    table_exists = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'doc_artifacts'"
    ).fetchone()
    if not table_exists:
        return True  # nothing to migrate; init_schema creates it fresh
    (create_sql,) = conn.execute(
        "SELECT sql FROM sqlite_master WHERE type = 'table' AND name = 'doc_artifacts'"
    ).fetchone()
    if "'vendor_doc'" not in create_sql or "'pinned_reference'" not in create_sql:
        return False  # the newest kind/origin CHECK values are missing
    for table in ("documents_edges", "doc_relations_edges"):
        columns = {row[1] for row in conn.execute(f"PRAGMA table_info({table})")}
        if "chunk_id" not in columns:
            return False
    return True
```

`_migrate_doc_artifacts_constraints` itself becomes: if
`_doc_artifacts_schema_is_current(conn)`, return immediately (no drop,
no recreate, no `meta` write) — otherwise perform exactly the same
drop-and-recreate this function already performs today (that
*remediation* was never the problem; only the *trigger condition* was).
`meta.schema_version` is **decoupled from this decision entirely** — it
becomes a purely informational "last schema code version this database
has been opened under" marker, updated unconditionally by `open_graph`
on every open (a trivial, harmless `UPDATE`/`INSERT OR REPLACE`) with no
migration behaviour keyed off its value anywhere except this one
now-fixed function. Confirmed via `grep` (§0) that `meta.schema_version`
has no other functional reader anywhere in `src/codecompass/` — only
this migration function and test assertions ever read it — so this
decoupling changes no other behaviour.

**This satisfies every one of the review's stated requirements
directly**:

- *Opening an existing schema-v9 database under Phase 76 must not
  unnecessarily destroy/recreate unrelated tables* — confirmed: Phase
  76 touches none of `doc_artifacts`/`documents_edges`/
  `doc_relations_edges`'s shape, so `_doc_artifacts_schema_is_current`
  returns `True` immediately for a real, current v9 database, and no
  drop occurs.
- *The three additive Git topology tables must appear safely on
  upgrade* — unaffected by this change; `init_schema`'s existing
  `CREATE TABLE IF NOT EXISTS` already handles this regardless of
  `meta.schema_version`'s value (confirmed: the three new tables need no
  migration function at all, since they are purely additive — this part
  of the original plan's reasoning was already correct and is
  unchanged).
- *Existing paid/persistent enrichment must remain untouched* — already
  true and unaffected either way (`vendor_enrichment`/`symbol_enrichment`/
  `doc_relation_enrichment` have no foreign key to `doc_artifacts` and
  are never touched by this function); now doubly protected since the
  function fires strictly less often.
- *Opening an upgraded database before a full sync must behave
  predictably* — now genuinely true: a `query`-only invocation
  immediately after upgrading to Phase 76 sees its prior
  `doc_artifacts`/relations content completely undisturbed, exactly as
  a user would reasonably expect.
- *Migration regression tests specifically covering a real v9-shaped
  database upgraded to the Phase 76 schema* — §18.

**Not merely removing the version bump**: `_SCHEMA_VERSION` is still
bumped to `"10"` — the review's own instruction not to dodge the problem
this way is honoured; the version number remains useful, honest
bookkeeping ("what schema-code vintage last touched this database"),
it is simply no longer the *trigger* for a specific table's
reconstruction. This is judged the genuinely correct long-term fix
(not a stopgap) because it generalizes a pattern this file's own history
already converged on independently four separate times
(`_migrate_doc_relation_enrichment_relation_label`,
`_migrate_symbols_export_kind_note_columns`,
`_migrate_symbol_enrichment_model_column`,
`_migrate_vendors_ecosystem_constraint` — every migration added *after*
`_migrate_doc_artifacts_constraints` itself already uses direct
introspection) — `_migrate_doc_artifacts_constraints` was simply never
brought into line with its own file's own later, better precedent until
now.

**Existing test literal-value updates required** (§3): every
`assert schema_version == "9"` in `tests/test_graph.py` becomes `"10"`
— a mechanical consequence of the version bump, not a behavioural
change to what's being tested.

## 12. Exact implementation sequence

1. `src/codecompass/git_topology.py` — `TopologyStatus`, `WorktreeInfo`/
   `SubmoduleInfo`/`RepositoryTopology` dataclasses, `detect_git_topology`,
   the URL sanitizer (§12.7 below), the path-safety check (§12.6), and
   the private `_run_git`/parsing helpers (§6/§7). Unit-testable in
   total isolation from `graph.py`/`sync.py`.
2. `src/codecompass/graph.py`:
   - Bump `_SCHEMA_VERSION` to `"10"`.
   - Add the three `CREATE TABLE IF NOT EXISTS` blocks + indexes (§4),
     with `pinned_commit` nullable and `is_path_safe`/`is_initialized`
     as specified.
   - Add `GitRepositoryRow`/`GitWorktreeRow`/`GitSubmoduleRow`
     dataclasses (natural-key-based, mirroring every existing row type).
   - Extend `rebuild_deterministic` to delete-then-reinsert all three
     (children before parent, matching every other table's FK-respecting
     order), plus write `meta.git_topology_status`/`git_topology_reason`.
   - **Rewrite `_migrate_doc_artifacts_constraints` per §11** —
     introspection-based trigger, `meta.schema_version` decoupled from
     its decision, unconditional (harmless) `meta.schema_version` update
     moved into `open_graph` itself.
3. `src/codecompass/sync.py::rebuild_project_graph` — call
   `git_topology.detect_git_topology(project_root)` once; convert its
   result into the three row-dataclass lists (empty when `status` is
   `not_git`/`unavailable`) plus the status/reason strings; pass all
   into `rebuild_deterministic`.
4. `src/codecompass/cli.py` — new `@query_app.command("topology")`
   function, rendering the four-state output (§9).
5. `src/codecompass/skill.py::render_tool_skill` — §9.2.
6. `docs/cli-reference.md` — §9.3.
7. `architecture/context-graph-schema.md` — the three new tables +
   the two new `meta` keys, following that page's own exact format.
8. `architecture/overview.md` and/or a new `architecture/git-topology.md`
   (an ordinary editorial call during implementation, not a decision
   gate) — including an explicit statement of §4's "not recursively
   materialized" clarification and §8's sibling-dirty-state limitation.
9. `decisions/0063-git-worktrees-and-submodules-as-a-new-graph-capability.md`
   (number confirmed live at implementation time) — records the
   `vendors`-rejection reasoning, the per-worktree-database decision,
   the mechanical-facts-only posture, **and this amendment's own
   migration-safety fix, the invocation-root/worktree-root distinction,
   the credential-sanitization policy, and the submodule-path-safety
   check** — all genuinely non-obvious tradeoffs worth a durable record,
   written in the same commit as the schema change.
10. Tests (§18).
11. `CHANGELOG.md`, `planning/ROADMAP.md`, `planning/CONTEXT.md`, phase
    retro, learning triage, drift audit, completion audit, final
    reconciliation — the corrected closeout sequence from this session's
    own `L-060`/`L-061` fix, unchanged by this phase.

**New implementation notes from this amendment**:

12.6. **Submodule path safety**: before running *any* `git`/filesystem
   command inside a declared submodule path,

   ```python
   resolved = (worktree_root / declared_path).resolve()
   is_path_safe = resolved.is_relative_to(worktree_root.resolve())
   ```

   (`Path.is_relative_to`, stdlib since Python 3.9; `requires-python
   = ">=3.11"` confirmed live, §0 — no compatibility concern). When
   `False`, the row is emitted with `is_path_safe=False` and nothing
   else is ever probed for that path — no `git -C <resolved>`, no
   filesystem read of any kind at `<resolved>`. Covers an absolute path,
   a `../`-traversal path, and a symlink that resolves outside the
   worktree root (`.resolve()` follows symlinks, so a symlinked escape
   is caught the same way a textual `../../` escape is).

12.7. **Credential redaction** (`sanitize_git_url`, in `git_topology.py`,
   applied at detection time to `origin_url` and every
   `child_repository_url` before either ever reaches a dataclass, the
   graph, or any output surface):

   ```python
   from urllib.parse import urlsplit, urlunsplit

   def sanitize_git_url(url: str) -> str:
       parsed = urlsplit(url)
       if parsed.scheme not in ("http", "https") or not parsed.username:
           return url
       netloc = parsed.hostname or ""
       if parsed.port:
           netloc += f":{parsed.port}"
       return urlunsplit((parsed.scheme, netloc, parsed.path, parsed.query, parsed.fragment))
   ```

   Verified live during planning (§0) against six real/representative
   URLs: an `https://user:pass@host/repo.git` credential form and a
   bare-token-as-username `https://TOKEN@host/repo.git` form both lose
   their userinfo entirely (`https://host/repo.git`); this repository's
   own real `git@github.com:org/repo.git` SCP-like submodule URLs and a
   `ssh://git@host/repo.git` form are both left **byte-for-byte
   unchanged** (SSH/SCP-like forms never carry a password in the URL by
   protocol design — a bare `user@` there, almost always the
   non-secret, public convention `git`, is not a credential to strip);
   a plain `https://host/repo.git` with no userinfo is unchanged
   (idempotent). Only `http`/`https` schemes are ever touched.

12.8. **Branch name form**: `git worktree list --porcelain`'s own
   `branch` line gives a **full ref** (`refs/heads/main`), confirmed
   against Git's documented porcelain format. CodeCompass stores the
   **short name** (`main`) — stripping a literal `refs/heads/` prefix
   when present, and falling back to the raw value unstripped in the
   rare case a branch ref doesn't use that prefix (a real but
   exceedingly uncommon case, disclosed rather than silently assumed
   away). Matches the human-facing shape the acceptance example and the
   original plan's own CLI mockup already show (`branch: feature-x`),
   made an explicit, tested rule rather than an implicit assumption.

12.9. **Robust parsing, confirmed not merely asserted**: `git worktree
   list --porcelain` (stable block format, not human prose), `git config
   -f .gitmodules --list -z` (NUL-delimited — verified live, §0, to
   produce identical key/value pairs to the newline form on this
   repository's own real `.gitmodules`, with additional robustness
   against a pathological embedded-newline value), `git ls-tree`
   (stable, tab-delimited plumbing output), `git rev-parse
   --path-format=absolute` (machine-oriented, no manual path resolution
   needed, §5), and `git status --porcelain` (the already-planned,
   already-correct machine-stable form, explicitly not plain `git
   status`) are the only text-parsing surfaces this module has — each
   chosen specifically because it is a documented, script-stable format,
   not human-oriented prose.

## 13. Real-repository validation sequence (amended — ordering fixed)

**The problem the review found**: the original plan's §13.3/§18
implicitly expected `codecompass query topology`, run from the **main**
worktree, to already know about a **new** sibling worktree created
*after* the main worktree's own last sync — but §9 correctly states
`query topology` reads persisted, last-sync state, never live `git`. The validation sequence as originally written was inconsistent
with the plan's own architecture.

**Corrected sequence** (exact order, each step's purpose stated):

1. **Create** the disposable linked worktree first, before either
   database is touched: `git worktree add <scratchpad-path> -b
   codecompass-phase76-worktree-test` from the real checkout (additive,
   non-destructive to `main`'s own checkout).
2. **Sync the main worktree** (`codecompass sync --yes --budget 0` from
   `/home/cormac/projects/codecompass`) — *after* the sibling now
   exists, so `git worktree list` (run as part of this sync) has a
   chance to observe it.
3. **Sync the disposable worktree** (`codecompass sync --yes --budget 0`
   from the new worktree path) — its own, separate `context-graph.db`,
   observing the main worktree as its own sibling.
4. **Query from main**: `codecompass query topology` (from
   `/home/cormac/projects/codecompass`) — must show `is_current=1` for
   itself (`main`, its own real HEAD at the time of step 2's sync) and
   the disposable worktree as a sibling, with whatever branch/HEAD that
   worktree had *at the time of step 2's sync* (i.e., its initial state
   right after `git worktree add`, since step 3's sync hadn't run yet
   when step 2 ran — this ordering detail is itself a real, useful
   demonstration of the plan's own stated "as of this worktree's own
   last sync" freshness contract, not an inconvenience to hide).
5. **Query from the disposable worktree**: `codecompass query topology`
   — must show `is_current=1` for itself and `main` as a sibling, with
   whatever branch/HEAD `main` had *at the time of step 3's sync* (i.e.,
   reflecting step 2's already-run sync).
6. **Make an uncommitted edit** in the disposable worktree (dirty state),
   **re-sync** it, **re-query** it — `is_dirty=true` for itself.
   Additionally `git checkout --detach <sha>` in the disposable
   worktree, re-sync, re-query — `is_detached=true`, `branch=null`.
7. Confirm throughout: both databases report the **identical**
   `git_repositories.common_dir` — the literal acceptance test ("main
   checkout + feature worktree recognized as one repository, two
   checkout states, not two unrelated projects").
8. **Mandatory cleanup, before this phase closes**: `git worktree
   remove <scratchpad-path> --force` (force, since step 6 leaves it
   dirty) and `git branch -D codecompass-phase76-worktree-test` — the
   real repository returns to exactly one worktree, confirmed via `git
   worktree list`/`git branch` showing the pre-test state restored.

**Submodule validation** (unchanged reasoning from the original plan,
restated for completeness):

1. **Real, no fixture needed**: `codecompass sync` against this actual
   repository; confirm `git_submodules` holds exactly two rows, both
   `revision_matches_pin=true`, matching the real, live-confirmed pins
   (§0).
2. **Divergence, disposable clone required**: `git clone
   --recurse-submodules` this repository into the session scratchpad;
   inside the clone's `adapters/haskell/`, `git checkout HEAD~1` without
   touching the parent's gitlink; `codecompass sync` inside the clone;
   confirm `revision_matches_pin=false` with both SHAs correctly
   distinct and correctly attributed. Scratch clone discarded after.
3. **New: malformed/traversal submodule path** — a disposable fixture
   repository (not this repository) whose `.gitmodules` declares a path
   containing `../` or an absolute path; confirm `is_path_safe=false`,
   confirm (via a mock/spy on the subprocess layer) that **no** `git`
   command was ever invoked against the escaping path, and confirm the
   row is still present (not silently dropped) — tested in full at §18.
4. **New: credential-bearing URL** — a disposable fixture's
   `.gitmodules` declares a submodule URL of the form
   `https://user:token@example.com/repo.git`; confirm the persisted
   `child_repository_url` has no userinfo component, both via direct
   database inspection and via `query topology --json` output.

## 14. Documentation / ADR / roadmap / context / changelog impacts

Unchanged in structure from the original plan; content requirements
expanded to cover this amendment's additions (§11's migration fix, §5's
three-root distinction, §6's status model, §12.6/§12.7's safety/
sanitization mechanisms) wherever `architecture/context-graph-schema.md`,
`architecture/overview.md`/`git-topology.md`, and `decisions/0063`
describe the feature — these are **content requirements on documents
already named for updating**, not new documents.

- `decisions/0063` — expanded scope per §12.9.
- `architecture/context-graph-schema.md`, `architecture/overview.md`/
  `git-topology.md` — expanded content per above.
- `docs/cli-reference.md` — the four-state output (§9) documented
  explicitly, not just the happy path.
- Cross-references only (not rewrites) to
  `docs/developer/haskell-adapter-submodules.md`,
  `docs/protocol-adapter/*.md`, `architecture/adapter-interface.md` —
  unchanged from the original plan.
- **No new `docs/domain/concepts/*.md` page in this phase** — unchanged
  reasoning from the original plan.
- `CHANGELOG.md`, `planning/ROADMAP.md`, `planning/CONTEXT.md` — updated
  in this amendment where the amendment itself changes current truth
  (below); the phase's own `done`-flip entries still land at
  implementation-closeout time, unchanged process.

**This amendment's own effect on `planning/ROADMAP.md`/`planning/CONTEXT.md`**:
the Phase 76 row/section already describes the phase at the right level
of generality (worktrees + submodules, new Priority A capability) that
no rewording is required by this amendment — both already say "planned,"
neither asserts implementation details fine-grained enough to now be
wrong. Confirmed by re-reading both files during this amendment: no
edit needed beyond what this plan file itself now says. (If a
future reader compares this amended plan against those files and finds
a genuine discrepancy, that is a normal drift finding for the eventual
`docs-reconstructor` pass, not something this amendment silently
assumed away.)

## 15. Task-context evaluation methodology (amended — strengthened per
the review)

**The problem the review found**: a lead-only before/after command-count
comparison is real signal but weak evidence, since the same person
knows the intended answer in both passes — exactly the risk this
project's own `L-027` was filed to guard against in *external*
reference-project trials, and there is no principled reason it wouldn't
apply here too.

**Amended method**: keep the cheap command-count metric (§15's original
value, restated below), but add an **independent baseline/treatment
comparison**, run only once the CLI command exists (i.e., during
implementation, not before) — this is a DoD-gating step for Phase 76's
own closeout, not something performed during planning.

**Setup, applying `L-062`'s own newly-landed read-scope-symmetry rule
from Phase 75** (`reference-project-protocol.md` §2.2): both arms get
**scoped reads**, confined to their own assigned scratch clone —
deliberately the simpler of `L-062`'s two allowed options, chosen to
remove the read-access-asymmetry confound entirely rather than needing a
post-hoc `L-027` check to catch it, since (unlike Phase 75's Ledgerkit
trial) there is no legitimate reason either arm would need to look
outside its own assigned clone for this task.

- **Baseline clone**: a fresh clone of this repository (with
  `--recurse-submodules`), plus the same disposable two-worktree fixture
  §13 constructs, no CodeCompass installed.
- **Treatment clone**: an identical fixture, with CodeCompass installed
  and `codecompass sync` already run in both worktrees.
- **Two fresh, independent `general-purpose` agents** (neither the
  lead, neither told about the other or this evaluation's own
  hypothesis) — one dispatched into the baseline clone, one into the
  treatment clone, each asked the same fixed questions:

  **Task A — submodule scenario**: what commit does the parent
  repository pin for the Haskell adapter submodule? What commit is
  actually checked out? Do they differ? If they differ, does that
  represent committed parent state (a real gitlink change) or merely
  local child-checkout state (an uncommitted `git submodule update`)?

  **Task B — worktree scenario**: are the two worktree paths separate
  repositories or worktrees of the same repository? Which checkout is
  current? What is the current checkout's branch/HEAD/dirty state?
  What is the sibling's own observed branch/HEAD? Which of these facts
  is persisted (from a prior sync) versus live?

  The baseline agent uses ordinary repository/Git access only. The
  treatment agent is told CodeCompass is available and to try `codecompass
  query topology` as a first move, falling back to ordinary tools for
  anything it doesn't answer.

- **`context-evaluator`**, dispatched third, independently re-derives
  ground truth for both tasks by inspecting the fixtures directly —
  its own standing methodology ("does NOT use CodeCompass to validate
  CodeCompass") is about not trusting CodeCompass's *output* as its own
  ground-truth source, which applies here exactly as it does to an
  external target; the fact that the "target" is CodeCompass's own
  repository does not exempt either arm's report from independent
  verification, and this amendment judges (contrary to the original
  plan's own reasoning, which is superseded here) that the role's
  methodology fits fine without adaptation. It rates both reports for:

  - Factual completeness and factual errors, against its own
    independently-derived ground truth.
  - Whether pinned-vs-checked-out state was correctly distinguished (not
    conflated, the exact real mistake `git submodule status`'s own
    `--cached`-dependent single SHA column invites).
  - Whether repository-vs-worktree identity was correctly distinguished.
  - Commands/tool reads each arm actually used (both agents log their
    own raw tool-call history, per `L-027`'s standing requirement).
  - Any extra repository exploration the treatment arm still needed
    after consulting CodeCompass's own output.

**Efficiency indicator** (cheap, honestly measured, retained from the
original plan, not expanded into an unmeasured claim): number of
distinct `git`/config-reading commands the baseline pass needed vs. the
treatment pass's `query topology` call — reported as a plain count,
**never** converted into a token-savings or time-savings claim unless
tokens/time are actually, separately measured (per direct instruction).

**This is stronger than lead self-comparison alone** without requiring
the full external reference-project apparatus for a target that
genuinely isn't external — the fixtures are disposable scratch clones
(matching `reference-project-protocol.md` §2.2's own working-copy
discipline), the comparison is genuinely independent (neither dispatched
agent is the lead, neither sees the other's work), and `context-evaluator`
provides the third-party verification the review specifically asked for.

**Explicit, unforced follow-up, not part of this phase's own DoD**: the
next external Priority-A Ledgerkit validation trial (recommended at
Phase 75's own closeout, still unclaimed by a phase number) should
separately consider a task where Git topology awareness might matter —
only if Ledgerkit's own real state ever presents one; none does today.

## 16. Explicit non-goals and deferrals

Restated from the original plan, with two additions from this amendment
(marked **new**):

- Generic multi-repository federation, cross-clone/cross-machine
  identity.
- Cross-repository symbol-level graphs; no nested `context-graph.db` for
  a submodule's own content, no recursive sync (§4's "not recursively
  materialized" clarification is the amendment's own sharpening of this
  same point).
- Automatic branch creation, automatic worktree creation/removal, merge/
  rebase/conflict management, agent orchestration, generic Git hosting/
  GitHub management, Docker/container topology, MCP functionality.
- A complete monorepo/workspace abstraction.
- Detecting "is the worktree root itself someone else's submodule" (§5)
  — strictly downward detection only.
- Recursive submodules-of-submodules — one level only.
- Characterizing *how* a diverged submodule commit relates to its pin
  (ahead/behind/unrelated, `git merge-base` analysis) — a boolean only.
- A shared/consolidated `context-graph.db` across a repository's
  worktrees (§10).
- Cross-linking a `git_submodules` row to a `vendors` row — no real
  instance exists to design against.
- Any change to `chat.py`/Phase 24's own routing scope (§2).
- A new `docs/domain/concepts/*.md` page (§14).
- Semantic relationship edges between the two submodules, or between
  either submodule and anything else (§8).
- **New: any credential-scanning/redaction beyond a Git remote URL's own
  userinfo component** — e.g., scanning commit messages, file contents,
  or environment variables for embedded secrets is a materially larger,
  different problem this phase's own evidence (a real, narrow risk in
  `origin_url`/`child_repository_url` specifically) does not call for.
- **New: characterizing an `unavailable`/`partial` failure beyond a
  short, first-failure diagnostic string** — a structured, multi-cause
  error-reporting model is real additional scope with no evidence yet
  that a plain string is insufficient for the tasks this phase's own
  evaluation (§15) names.

## 17. Human decision gates

**None identified — re-confirmed for this amendment.** Every new design
choice (the URL-sanitization scheme boundary, the path-safety check's
exact mechanism, the two-level uncertainty model, the migration
introspection predicate) was resolved by direct precedent already in
this codebase, by live verification performed during planning (§0), or
by ordinary engineering judgement with a stated, reversible rationale
disclosed in the relevant section above. If implementation surfaces a
genuine ambiguity neither the original plan nor this amendment
anticipated, work pauses and the lead asks before proceeding, per
`CLAUDE.md` §1 — none is manufactured here to be safe.

## 18. Unit / integration / real-repository tests

**`tests/test_git_topology.py`, new** — every test builds its own
disposable `git init`-ed fixture under `tmp_path`:

- Not a Git repository → `status=NOT_GIT`.
- `git` binary missing (monkeypatch `shutil.which`) → `status=UNAVAILABLE`,
  reason populated.
- A `rev-parse` failure with non-"not a git repository" stderr
  (simulated) → `status=UNAVAILABLE`, not `NOT_GIT`.
- Single-worktree, clean repo → `status=DETECTED`; one `git_repositories`
  row, one `git_worktrees` row (`is_current=True`, `is_dirty=False`,
  correct `branch`/`head_commit`), zero `git_submodules` rows.
- **New**: `detect_git_topology` invoked from the fixture's own root,
  and separately from a real nested subdirectory of the same fixture —
  both calls identify the **same** `worktree_root` and `common_dir`
  (§5's core regression test).
- Dirty working tree (tracked edit) and untracked-only change → both
  `is_dirty=True`.
- Detached HEAD → `is_detached=True`, `branch=None`, `head_commit`
  populated.
- Unborn branch → `head_commit=None`, no crash.
- Two real worktrees (`git worktree add`) → both in `git_worktrees`,
  sharing one `common_dir`; exactly one `is_current=True` depending on
  which path was queried; the other has `is_dirty=None`.
- A `prunable` worktree → `is_prunable=True`.
- `git worktree list` failing despite a successful `rev-parse`
  (simulated) → `status=PARTIAL`, `worktrees=()`, reason populated.
- **New**: `branch` stores the short name even though `worktree list
  --porcelain`'s own raw output is a full `refs/heads/...` ref
  (confirms §12.8's stripping rule against real git output, not an
  assumption).
- One real submodule fixture (`git submodule add <local bare repo>`)
  fully in sync → `revision_matches_pin=True`.
- Same fixture, submodule one commit behind its pin (real divergence,
  constructed inside the fixture) → `revision_matches_pin=False`, both
  SHAs correctly attributed.
- Submodule declared, never initialized → `is_initialized=False`,
  `pinned_commit` still populated, child-state fields `None`.
- **New**: submodule declared in `.gitmodules` with **no** corresponding
  gitlink in `HEAD`'s tree (added to `.gitmodules`, never `git add`-ed)
  → the row **is still emitted**, `pinned_commit=None`,
  `revision_matches_pin=None` (amended: the original plan incorrectly
  dropped this row entirely).
- **New**: submodule path escaping the worktree root (`../etc`, or an
  absolute path) → `is_path_safe=False`; a mock/spy on the subprocess
  layer confirms **zero** `git`/filesystem calls were made against the
  escaping path; the row is still present.
- **New**: `sanitize_git_url` — credential-bearing HTTPS
  (`user:pass@host`), bare-token-as-username HTTPS, normal
  credential-free HTTPS, SCP-like `git@host:path`, and `ssh://git@host/path`
  — exactly the six cases verified live during planning (§0), now as
  permanent regression tests.

**`tests/test_graph.py`, extend**:

- **New, per §11**: a hand-built, real v9-shaped `doc_artifacts`/
  `documents_edges`/`doc_relations_edges` fixture (matching today's
  actual current schema — Phase 76 changes none of their columns), with
  `meta.schema_version = "9"` and a real pre-existing row inserted into
  `doc_artifacts` — opened under the Phase 76 code — asserts the
  pre-existing row **still exists afterward** (the core regression: this
  would previously have been dropped purely by the version bump) and
  that the three new `git_*` tables now exist.
- **New**: a genuinely pre-Phase-17-shaped `doc_artifacts` fixture
  (narrow `kind` CHECK, as the existing `test_open_graph_migrates_pre_phase_17_schema`
  test already builds) still correctly triggers the drop-and-recreate
  migration under the new introspection-based trigger — confirming the
  fix doesn't just always skip, it still correctly detects a genuinely
  stale schema.
- Every existing `assert schema_version == "9"` literal updated to
  `"10"` (§11/§3) — a mechanical, disclosed consequence of the version
  bump, not a behavioural change.
- `rebuild_deterministic` called with real `GitRepositoryRow`/
  `GitWorktreeRow`/`GitSubmoduleRow` fixtures round-trips correctly;
  called with all three defaulted to `()` behaves exactly as every
  pre-existing test already expects.

**`tests/test_sync.py`, extend**:

- `rebuild_project_graph`, run against a real disposable Git fixture,
  produces the expected rows via the actual production call path (the
  `L-021`-required real-call-site test, `CLAUDE.md` §1).

**`tests/test_cli.py`, extend**:

- `codecompass query topology` against a real synced fixture prints the
  expected structure for each of the four `TopologyStatus` values
  (constructed via fixtures/monkeypatching for `not_git`/`unavailable`/
  `partial`, real for `detected`); `--json` round-trips through
  `json.loads`; a `partial` result's structure is still shown alongside
  its banner, never suppressed.

**Real-repository validation** — §13 (submodules: real repo + two
disposable-clone scenarios + the new path-safety/credential-URL
fixtures; worktrees: the corrected, sync-then-query ordering).

## 19. Runnable verification commands and expected outcomes

```bash
# Unit + integration
.venv/bin/pytest tests/test_git_topology.py tests/test_graph.py \
  tests/test_sync.py tests/test_cli.py -q
# Expected: all pass, including the migration-regression, nested-
# directory, path-safety, and credential-sanitization cases (§18).

# Full regression
.venv/bin/pytest -q
# Expected: same pass count as this plan's own baseline (641 passed,
# 2 skipped) plus this phase's new tests, all passing.

.venv/bin/ruff check .
python3 scripts/check_user_docs.py --strict
python3 scripts/check_knowledge_base.py
# Expected: no findings on any of the three.

# Real-repository validation — submodules (this repository itself)
codecompass sync --yes --budget 0
codecompass query topology
codecompass query topology --json
# Expected: status=detected; two git_submodules rows, both
# revision_matches_pin=true; child_repository_url values match
# .gitmodules exactly (SCP-like, no credentials to strip in this
# repository's own real case).

# Real-repository validation — worktrees (corrected ordering, §13)
git worktree add /tmp/codecompass-phase76-worktree-test -b codecompass-phase76-worktree-test
codecompass sync --yes --budget 0   # main worktree, AFTER the sibling now exists
(cd /tmp/codecompass-phase76-worktree-test && codecompass sync --yes --budget 0)
codecompass query topology          # from main
(cd /tmp/codecompass-phase76-worktree-test && codecompass query topology)
# Expected: both report the identical git_repositories.common_dir; each
# correctly marks itself current and the other a sibling, per its own
# last sync (not live).

# Mandatory cleanup
git worktree remove /tmp/codecompass-phase76-worktree-test --force
git branch -D codecompass-phase76-worktree-test
git worktree list
# Expected: back to exactly one worktree, no leftover branch.
```

## 20. Definition of Done

Per `CLAUDE.md` §5, unchanged process; amended to include this
amendment's own new requirements (items marked **new**):

1. Code implemented per §12; `git_topology.py`, `graph.py`, `sync.py`,
   `cli.py`, `skill.py` all consistent with each other.
2. **New**: `_migrate_doc_artifacts_constraints` genuinely rewritten to
   introspection-based triggering (§11), confirmed by the new migration
   regression tests (§18), not merely by the version bump landing.
3. **New**: the invocation-root/worktree-root/common-dir distinction is
   genuinely implemented (§5) and tested from a real nested directory
   (§18), not merely documented.
4. **New**: the four-state `TopologyStatus` model (§6) is genuinely
   distinguishable in both persisted data and CLI/JSON output — not
   collapsed back into "empty result" for more than one underlying
   cause.
5. **New**: `pinned_commit` is genuinely nullable and a declared-but-
   unresolved submodule is genuinely represented, not omitted (§18).
6. **New**: the submodule path-safety check genuinely refuses to probe
   an escaping path (§18, confirmed via a subprocess-call spy, not only
   the resulting data).
7. **New**: the URL sanitizer genuinely strips credentials from
   `http(s)` forms and genuinely leaves SSH/SCP-like forms (including
   this repository's own real submodule URLs) unchanged (§18).
8. §18's full test suite passes, including the corrected real-repository
   worktree validation sequence and both disposable submodule fixtures.
9. `docs/`, `architecture/`, `decisions/` updated per §14, same commit
   as the code.
10. **New**: §15's amended, independent baseline/treatment/`context-evaluator`
    task-context evaluation performed and recorded honestly (not the
    lead-self-comparison-only version) — including if the answer turns
    out to be "less advantage than hoped."
11. An independent `docs-reconstructor` per-phase drift audit finds no
    current-truth doc left misdescribing the system.
12. `CHANGELOG.md` entry added, same commit.
13. `planning/CONTEXT.md` reflects the new state.
14. A phase retro exists at
    `planning/retros/phase-76-git-repository-topology.md`, including
    §15's findings.
15. Candidate learnings from the phase (if any) triaged by
    `knowledge-curator` — **the migration-safety finding in §11 is a
    strong candidate for its own learning entry**, distinct from this
    phase's own feature work, since it documents a real, pre-existing,
    twice-already-occurred defect class this phase's own review
    happened to surface.
16. An independent `release-phase-auditor` pass verifies every
    preceding condition against the exact commit about to be marked
    done, persisting `planning/retros/_audit-phase-76.md` — any
    post-audit commit touching audited scope voids that pass.
17. Disposable test worktree/branch and scratch submodule-divergence/
    path-safety/credential-URL fixtures are fully cleaned up — no
    leftover trace on the real repository.
18. Only once every one of the above genuinely holds does a genuinely-
    dispatched `roadmap-context-curator` (never the lead self-serving
    it) perform final reconciliation and flip
    `planning/ROADMAP.md`'s Phase 76 row to `done`.

**Not done merely because Git metadata can be parsed** — it must be
correctly represented at both levels of uncertainty (§6/§8), safe
against a hostile or malformed `.gitmodules` (§12.6), free of credential
leakage (§12.7), correct regardless of invocation directory (§5), safe
to open against an existing production database (§11), reachable
through `codecompass query topology` and the generated Skill, and shown
(§15), via genuinely independent assessment, to help at least one
realistic task.

---

## Preserved from the original plan, unchanged by this amendment

Restated explicitly, per the user's own instruction, so nothing on this
list is mistaken for having been reopened:

- Separate Git topology tables rather than abusing `vendors` (§4).
- Mechanical Git facts kept separate from semantic project relationships
  (§8).
- Parent-pinned revision kept distinct from child checked-out revision
  (§4/§7).
- Per-worktree `context-graph.db` isolation for now (§10).
- One-level submodule scope (§7.6/§16).
- No recursive submodule graph indexing (§4/§16).
- No generic multi-repository federation (§16).
- No cross-repository symbol graph (§16).
- No worktree/branch management — read-only observation only (§16).
- No Phase 24 implementation or redefinition (§2).
- Real CodeCompass protocol/Haskell submodules used as dogfood fixtures
  (§0/§13).
- Disposable worktree and scratch-clone validation, with mandatory
  cleanup (§13/§20).
- The documentation/ADR/retro/drift-audit/release-audit/
  roadmap-context-curator closeout discipline established after the
  `L-060`/`L-061` fixes (§12/§20).
