# Phase 76: Git repository topology awareness (worktrees + submodules) — plan

**Status:** planned (2026-09-28).

Direct user request. An evaluation/implementation phase: CodeCompass
gains mechanical awareness of Git worktree and submodule topology, so a
fresh agent can tell "different checkout of the same repository" apart
from "different repository" and "parent-pinned commit" apart from
"actually checked-out commit" — without CodeCompass creating, managing,
or mutating any of that topology itself.

## 0. Verified current state and HEAD

Confirmed live, not assumed, immediately before writing this plan:

- `git log --oneline -1` → `694e4f0` (`docs(phase-75): backfill real
  closeout commit SHA into L-062/L-063 promoted.md lines`), on `main`,
  clean working tree.
- `planning/ROADMAP.md`: highest phase row is **75, `done`**
  (Priority A Ledgerkit validation, `context-evaluator` verdict PASS
  WITH GAPS / advantage LOW). No phase 76 row exists yet — **76 is the
  next valid phase number**, not assumed from a stale recollection.
- `planning/CONTEXT.md`'s own "Next concrete step" *recommends* "a
  second, differently-shaped Priority A validation trial" as what it
  calls "Phase 76" — but no `planning/phase-76-*.md` file was ever
  written for that recommendation, so per `CLAUDE.md` §1 ("add the
  phase's row/status to ROADMAP.md in the same commit as the plan
  file") that number was never actually allocated; it was prose, not a
  reservation. This plan claims 76 for the git-topology phase instead
  (direct, explicit user request, arriving after that recommendation
  was written); the Ledgerkit second-trial idea is not abandoned, it
  simply becomes "whichever number comes after this phase" if/when it's
  picked up — `planning/CONTEXT.md` is corrected below to say this
  plainly instead of naming two different things "Phase 76."
- `git worktree list` → exactly one worktree (`/home/cormac/projects/codecompass`,
  `694e4f0`, `[main]`). No linked worktree exists in the real checkout
  today — validation needs a disposable one (§12).
- `.gitmodules` → two real submodules, confirmed live:
  `protocol/codecompass-adaptor-protocol` →
  `git@github.com:ctosullivan/codecompass-adaptor-protocol.git`;
  `adapters/haskell` → `git@github.com:ctosullivan/codecompass-adaptor-haskell.git`.
  `git submodule status` (no `+`/`-` prefix on either line) confirms
  both are currently initialized and checked out **exactly at** their
  parent-pinned commit (`dfd7a783...` / `596fb94f...`) — the "checked-out
  differs from pin" case does not occur naturally in the real repo right
  now and must be constructed in a disposable fixture (§12).
- Neither submodule is a `vendor.toml` entry (`vendor.toml` lists only
  `anthropic`, `pipdeptree`, `rich`, `typer`, all `ecosystem = "python"`)
  — confirmed live. This is real, load-bearing evidence for §4's schema
  decision, not an assumption.
- `git --version` → 2.47.3 (supports every subcommand/flag this plan
  uses; no minimum-version gate needed).

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
question, now with a concrete, mechanically-available fact source to
design against if/when it is revisited. `planning/CONTEXT.md`/
`planning/ROADMAP.md`'s Phase 24 backlog row is **not** changed by this
phase beyond this cross-reference note.

## 3. Relevant current architecture and files

Read in full before writing this plan (not summarized from memory):

- `src/codecompass/graph.py` — schema (`_SCHEMA_VERSION = "9"`), row
  dataclasses, `rebuild_deterministic` (full wipe-and-reinsert per
  table, `vendors`/`symbols` upserted by natural key to preserve
  enrichment; everything else — including every edge table and
  `doc_artifacts` — fully cleared and reinserted every rebuild, no
  cross-rebuild identity to preserve), `open_graph` (four in-place
  migrations then idempotent `CREATE TABLE IF NOT EXISTS`).
- `src/codecompass/sync.py::rebuild_project_graph` — the one
  orchestration function every detection module feeds into; `cli.py`'s
  `_bootstrap`/`sync`/`index` all call it with `project_root`.
- `src/codecompass/discovery.py`, `spec_docs.py`, `usage.py`,
  `doc_mapping.py`, `skill_scan.py` — the existing "pure detection
  module, graph-agnostic, `sync.py` converts to `graph.py` row types"
  pattern this phase's own `git_topology.py` follows.
- `src/codecompass/source_resolution.py` — the existing precedent for
  shelling out to real `git` (`shutil.which("git")` guard,
  `subprocess.run`, explicit `SourceResolutionError` only for a genuine
  vendor-clone failure — topology detection is supplementary, not
  gating, so it degrades silently rather than raising, see §8).
- `src/codecompass/cli.py` — `query_app` Typer sub-app, five existing
  `query` subcommands (`vendors`, `vendor`, `symbol`, `skills`,
  `relations`), each with a `--json` flag and a `_graph_session`
  context manager; `Path.cwd()` is the only "project root" resolution
  anywhere in the file today.
- `src/codecompass/skill.py::render_tool_skill` — the generated
  `.claude/skills/codecompass/SKILL.md`; lists every `query` subcommand
  by hand *and* the graph's own table names in prose — the exact
  multi-module coordination shape `CG-001` was originally filed against
  (`graph.py` ↔ `cli.py` ↔ `skill.py`, three places a new capability
  must land consistently).
- `scripts/check_user_docs.py::check_cli_commands_documented` — already
  mechanically fails the build if a new `@query_app.command(...)` isn't
  named in `docs/cli-reference.md`. `check_generated_artifacts_match_source`
  already mechanically fails the build if `.claude/skills/codecompass/SKILL.md`
  drifts from `skill.render_tool_skill(...)`'s real output. **Both
  checks already exist and will catch a `CG-001`-shaped coordination
  gap in this phase's own implementation for free** — confirmed by
  reading both functions directly, not assumed.
- `decisions/0057` (external-process adapter protocol),
  `decisions/0058` (adapter protocol + Haskell adapter as separate
  submodule repositories) — the real, load-bearing reason this
  project's own submodules exist; `docs/developer/haskell-adapter-submodules.md`,
  `docs/protocol-adapter/*.md`, `architecture/adapter-interface.md`,
  `architecture/overview.md` — existing **human-facing** developer docs
  describing the same submodules this phase makes **mechanically**
  legible to CodeCompass itself; not rewritten, cross-referenced (§14).
- `docs/domain/concepts/vendor.md` — confirms `VendorConfig` is
  narrowly `(name: str, ecosystem: Ecosystem)`, sourced from
  `vendor.toml`, "not itself a package in some general sense... tied to
  this project's `vendor.toml` schema" — direct evidence that a
  submodule (no `vendor.toml` entry, no `Ecosystem`, no package-manager
  identity) does not fit the `vendors` table and should not be forced
  into it (§4).
- `planning/v1-redefinition/reference-project-protocol.md` §2.2 (as
  amended this session, `L-062`) — scratch-clone-only working-copy
  discipline, now including explicit read-scope guidance; reused
  directly for §12's disposable worktree/submodule-divergence fixtures.

## 4. Proposed data model and terminology

**Investigated and rejected: reusing `vendors`.** A submodule has no
`Ecosystem`, no `vendor.toml` entry, and (per `decisions/0058`) is
mounted specifically as a *Git-level* construct independent of any
package manager — forcing it into `vendors` would misrepresent it as a
package dependency it is not, and would require relaxing the
`ecosystem` CHECK constraint for something that isn't one. Rejected.

**Investigated and rejected: a generic `doc_artifacts`/`other`-kind
row.** `doc_artifacts` models *documents* (Markdown, generated Skills,
spec docs) with a `path`/`name`/`description` shape; a worktree or
submodule is neither a document nor addressable by the
`mentions_artifact`/`mentions_dependency` word-boundary matchers that
give `doc_artifacts` rows their whole reason for existing. Rejected.

**Decision: three new tables, a new graph-capability addition (schema
version `9` → `10`)**, mirroring the exact conceptual model the user
specified:

```
git_repositories   -- one row per canonical repository this checkout
                      (or any of its worktrees/submodules) belongs to
git_worktrees      -- N rows per repository: this checkout, plus every
                      sibling worktree observed via `git worktree list`
git_submodules     -- N rows per repository: every submodule this
                      project's own `.gitmodules` declares
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
                                      -- nullable (no remote configured)
);

CREATE TABLE IF NOT EXISTS git_worktrees (
  id            INTEGER PRIMARY KEY,
  repository_id INTEGER NOT NULL REFERENCES git_repositories(id) ON DELETE CASCADE,
  worktree_path TEXT NOT NULL,        -- absolute path
  is_current    INTEGER NOT NULL DEFAULT 0,  -- 1 for the worktree this
                                              -- context-graph.db lives
                                              -- in; 0 for a sibling
  branch        TEXT,                 -- NULL when detached
  is_detached   INTEGER NOT NULL DEFAULT 0,
  head_commit   TEXT,                 -- NULL only for a truly unborn
                                       -- branch (no commits yet)
  is_dirty      INTEGER,              -- NULL for a non-current (sibling)
                                       -- worktree — see §8 for why this
                                       -- is never populated for siblings
  is_bare       INTEGER NOT NULL DEFAULT 0,
  is_locked     INTEGER NOT NULL DEFAULT 0,
  is_prunable   INTEGER NOT NULL DEFAULT 0,  -- `git worktree list`'s own
                                              -- "directory is gone" flag
  UNIQUE (repository_id, worktree_path)
);
CREATE INDEX IF NOT EXISTS idx_git_worktrees_repository ON git_worktrees(repository_id);

CREATE TABLE IF NOT EXISTS git_submodules (
  id                    INTEGER PRIMARY KEY,
  parent_repository_id  INTEGER NOT NULL REFERENCES git_repositories(id) ON DELETE CASCADE,
  path                  TEXT NOT NULL,     -- mount path, relative to the
                                            -- parent repo root, e.g.
                                            -- "adapters/haskell"
  child_repository_url  TEXT,              -- from .gitmodules; nullable
                                            -- if .gitmodules is malformed
                                            -- for this entry
  pinned_commit         TEXT NOT NULL,     -- the gitlink SHA recorded in
                                            -- the PARENT's own tree
                                            -- (`git ls-tree HEAD -- <path>`)
                                            -- — never the child's own
                                            -- working state
  is_initialized        INTEGER NOT NULL DEFAULT 0,
  checked_out_commit    TEXT,              -- NULL if not initialized
  revision_matches_pin  INTEGER,           -- NULL if not initialized;
                                            -- else 1/0 — the mechanical
                                            -- fact the user's own
                                            -- required-capability list
                                            -- names explicitly
  child_branch          TEXT,              -- NULL if not initialized or
                                            -- detached
  child_is_dirty        INTEGER,           -- NULL if not initialized
  UNIQUE (parent_repository_id, path)
);
CREATE INDEX IF NOT EXISTS idx_git_submodules_parent ON git_submodules(parent_repository_id);
```

**No `observed_at`/timestamp column on any of the three** — these
tables are fully wiped and reinserted every `rebuild_deterministic`
call, in the same transaction as everything else (no cross-rebuild
identity to preserve, same category as `doc_artifacts`/every edge
table), so `meta.last_deterministic_rebuild_at` (already the graph's
one shared freshness signal) already answers "as of when" without a
redundant per-row column.

**No `origin`-style provenance enum** (contrast `doc_artifacts.origin`):
every fact in these three tables is *mechanically derived from `git`
commands with no AI/agent involvement and no ambiguity about producer*
— there is no second, less-authoritative source these facts could have
come from the way a doc could be `project`-authored vs.
`vendor_upstream`-sourced. Provenance here is the deterministic-only
model itself (§8), not a field.

**Terminology** (for `architecture/`/docs use, §14):

- **Repository** — identified by its `common_dir` (the one `.git`
  directory shared by every worktree of it). Not the same as "project"
  (`project_root` may be a git repo, a subdirectory inside one, or not a
  git repo at all — this phase adds repository awareness *when
  applicable*, never requires it).
- **Worktree** — one checkout of a repository: a path, a branch or
  detached HEAD, a HEAD commit, and (for the current one only) a
  workspace/dirty state. Two worktrees of the same repository share
  `common_dir` and are never represented as separate `git_repositories`
  rows, satisfying the user's own hard requirement directly at the
  schema level (a worktree literally cannot become "its own project" —
  there is no column path for it to acquire a second `git_repositories`
  identity).
- **Submodule** — a mount point recorded in the *parent's* tree (a
  gitlink) plus `.gitmodules`; distinct from the child's own actual
  checkout state, which may or may not be initialized, and may or may
  not match the parent-pinned commit.

## 5. Discovery / root-resolution changes required

**None to existing `project_root` resolution.** `project_root` stays
exactly `Path.cwd()` everywhere it is today — this phase adds a new,
independent detection pass (`git_topology.py`, §6) that runs *from*
`project_root`, it does not change what `project_root` means or how any
existing command resolves it. `discover_manifest_paths`/`discover_all`
(dependency-manifest discovery) are untouched; this is a parallel
concern (Git structure, not dependency manifests).

**One explicit non-change worth stating**: this phase does **not**
walk upward from `project_root` looking for an ancestor repository that
treats `project_root` itself as *its* submodule — only descend from
`project_root` to detect worktrees/submodules `project_root`'s own
repository declares. Detecting "am I someone else's submodule" is a
different, upward-facing question the user's own acceptance model
doesn't ask for (the model is `Repository → Worktree*,Submodule*`,
strictly downward) and is named as an explicit deferral (§16).

## 6. New module: `src/codecompass/git_topology.py`

Mirrors the existing `discovery.py`/`usage.py`/`spec_docs.py` shape: a
pure, graph-agnostic detection module; `sync.py` is the only place that
converts its output into `graph.py` row types (matching the existing
`usage.DetectedImport` → `graph.UsesEdgeRow` pattern).

```python
@dataclass(frozen=True)
class WorktreeInfo:
    path: str            # absolute
    is_current: bool
    branch: str | None
    is_detached: bool
    head_commit: str | None
    is_dirty: bool | None
    is_bare: bool
    is_locked: bool
    is_prunable: bool

@dataclass(frozen=True)
class SubmoduleInfo:
    path: str
    child_repository_url: str | None
    pinned_commit: str
    is_initialized: bool
    checked_out_commit: str | None
    revision_matches_pin: bool | None
    child_branch: str | None
    child_is_dirty: bool | None

@dataclass(frozen=True)
class RepositoryTopology:
    common_dir: str
    origin_url: str | None
    worktrees: tuple[WorktreeInfo, ...]
    submodules: tuple[SubmoduleInfo, ...]

def detect_git_topology(project_root: Path) -> RepositoryTopology | None:
    """None if `git` isn't installed, or project_root isn't inside a
    Git repository (or working tree). Never raises — see §8."""
```

**Implementation notes** (exact commands, chosen for the reasons
below):

1. **`git` availability + repo check**: `shutil.which("git")` (mirrors
   `source_resolution._git_clone`'s own guard); if absent, return
   `None` immediately. Then `git -C <project_root> rev-parse
   --git-common-dir` — a non-zero exit (not a git repo) → return
   `None`. Resolve the (possibly relative) output against
   `project_root` and `.resolve()` it to an absolute path — this
   absolute common-dir path is `common_dir`, chosen specifically
   because it is **identical from every worktree of the same
   repository** (that is its literal git-defined purpose), unlike
   `--git-dir` (which differs per worktree) or the worktree's own path
   (which is the thing we're trying to *distinguish from* identity).
2. **`origin_url`**: `git -C <project_root> remote get-url origin`;
   non-zero exit (no `origin` remote) → `None`, not an error.
3. **Worktrees**: `git -C <project_root> worktree list --porcelain` —
   a stable, documented, blank-line-delimited block format
   (`worktree <path>`, `HEAD <sha>`, `branch <ref>` or `detached`,
   optional `bare`/`locked [reason]`/`prunable [reason]` lines). Mark
   `is_current` by comparing each block's resolved path against
   `project_root.resolve()`. **Dirty state is computed only for the
   current worktree** (`git -C <project_root> status --porcelain`,
   non-empty output → dirty; this counts untracked files as dirty,
   matching the plain-English "workspace: dirty" framing, documented
   explicitly as this phase's own definition) — never for a sibling,
   for the reason given in §8/§9 (avoiding N extra subprocess calls
   against paths that may be stale/unmounted/removed, and avoiding any
   appearance of authoritative live knowledge about another checkout's
   mutable state beyond what `worktree list` itself already reports).
4. **Submodules**: enumerate `.gitmodules` via
   `git config -f .gitmodules --list` (real git-config parsing, not a
   hand-rolled `.gitmodules` reader — same "prefer the real parser"
   posture `decisions/0057` already established for `package.yaml`),
   grouping `submodule.<name>.path`/`.url` pairs. For each path:
   - `pinned_commit`: `git -C <project_root> ls-tree HEAD -- <path>` →
     parse the `160000 commit <sha>\t<path>` gitlink line. This is
     **the parent's own tree entry** — deliberately not derived from
     `git submodule status`'s single SHA column, which shows the
     *checked-out* commit unless `--cached` is passed; reading the
     gitlink directly is unambiguous and needs no flag-dependent
     interpretation.
   - `is_initialized`: does `<project_root>/<path>/.git` exist (file or
     directory — git uses a gitfile for a normal submodule, a full
     `.git` directory only in unusual manually-`git init`'d cases;
     either way `git -C <path> ...` works transparently, no
     special-casing needed)?
   - If initialized: `checked_out_commit` = `git -C <path> rev-parse
     HEAD`; `child_branch` = `git -C <path> symbolic-ref --short HEAD`
     (non-zero exit → detached, `child_branch = None`);
     `child_is_dirty` = non-empty `git -C <path> status --porcelain`;
     `revision_matches_pin` = `checked_out_commit == pinned_commit`.
   - If not initialized: all four fields `None`/`False` as documented
     above — never attempt a git command inside an uninitialized
     submodule directory (it may not even exist on disk).
   - **Cross-check used only in testing, not production code** (§13):
     `git submodule status`'s leading character (space = in sync, `+` =
     checked-out differs from pin, `-` = not initialized) independently
     corroborates `revision_matches_pin`/`is_initialized` without being
     the primary derivation.
5. **Never recurse into nested submodules-of-submodules** — `.gitmodules`
   is read at exactly one level (`project_root`'s own), matching the
   "minimum capability" scope; a submodule's *own* submodules (if any)
   are not this phase's concern (§16).

## 7. Context / query / packet integration points

1. **New CLI command**: `codecompass query topology [--json]` — added
   to `cli.py`'s existing `query_app`, same `_graph_session`/`--json`
   pattern as `query vendors`/`query relations`. Reads the persisted
   `git_repositories`/`git_worktrees`/`git_submodules` tables (not a
   live `git` re-invocation — consistent with `decisions/0025`'s
   "graph reflects state as of last full sync" contract, the same
   contract every other `query` subcommand already honours). Renders
   the exact shape the user's own acceptance example names:
   repository identity, the active checkout's full detail
   (path/branch-or-detached/HEAD/dirty), every other known worktree
   (branch-or-detached/HEAD only, no dirty claim — see §6.3), and every
   submodule (path, child repository URL, parent-pinned revision,
   checked-out revision + match/mismatch, child branch/dirty if
   initialized). When no `git_repositories` row exists (not a Git
   project, or `git` unavailable), prints a plain "not a Git
   repository" line — matching every other `query` command's graceful
   empty-state posture, never an error.
2. **`skill.py::render_tool_skill`**: gains a `query topology` line in
   the existing hand-written Commands list (alongside `query vendors`/
   `query relations`/etc.) **and** `git_repositories`/`git_worktrees`/
   `git_submodules` added to the trailing "query context-graph.db
   directly" table-name list — the exact two spots `CG-001`'s own
   motivating example named as easy to miss. `check_cli_commands_documented`
   and `check_generated_artifacts_match_source` (§3) mechanically catch
   a miss here at `check_user_docs.py --strict` time.
3. **`docs/cli-reference.md`**: a new `## `codecompass query topology
   [--json]`` section, same shape as the five existing `query`
   subcommand sections — required for `check_cli_commands_documented`
   to pass, not optional polish.
4. **Generated root `CLAUDE.md`**: **not changed** — `update_root_claude_md`/
   `render_routing_table` render *per-vendor* routing rows; repository
   topology is not a per-vendor concept and does not belong in that
   table. (Considered and rejected: a new always-present "Repository"
   section in the root `CLAUDE.md` alongside the routing table — deferred,
   §16, since the routing table's own generation path is more invasive
   to extend correctly than adding one CLI surface + one Skill section,
   and the Skill is already the established "orientation" surface for
   exactly this kind of tool-level fact, per `decisions/0020`.)
5. **`planning/knowledge/<feature-slug>/context-packet.md`** (Phase
   54c's own narrowly-scoped artifact): not modified by `sync` — this
   phase does not touch the knowledge-packet pipeline. A future
   `knowledge-curator` packet for a feature that genuinely depends on
   submodule/worktree state (e.g., "bump the Haskell adapter pin") can
   now cite `codecompass query topology --json` as a real evidence
   source; this phase makes that possible, it does not wire it in
   automatically.

## 8. Deterministic provenance rules

- **Every fact in `git_repositories`/`git_worktrees`/`git_submodules`
  is mechanically derived from a real `git` subprocess call, never
  inferred or AI-generated** — matching the user's own explicit
  instruction to keep `SUBMODULE → pinned_revision = <SHA>` as a
  stronger, structurally distinct fact from any inferred "depends on"
  semantic relationship.
- **No semantic relationship is created between a submodule and
  anything else.** In particular, this phase does **not** assert
  `codecompass-adaptor-haskell IMPLEMENTS codecompass-adaptor-protocol`
  or any similar edge — that would need independent evidence
  (`decisions/0057`'s protocol conformance story is the closest existing
  candidate, but it is out of this phase's scope entirely). The two
  submodules appear in `git_submodules` purely as "both are mount
  points this parent repository declares," with no claim about their
  relationship *to each other* beyond both being real. If a future
  phase wants that semantic edge, it needs its own evidence and its own
  relation kind, exactly as `CG-007`'s own precedent already
  establishes for keeping mechanical and semantic relationships
  separate.
- **A sibling worktree's branch/HEAD is "as observed at this worktree's
  own last sync," not live** — the same staleness contract every other
  graph fact already carries (`decisions/0025`). This is stated
  explicitly in `docs/cli-reference.md`'s new section and in `query
  topology`'s own output (a one-line freshness note, reusing
  `meta.last_deterministic_rebuild_at`), so a fresh agent is never
  misled into treating a sibling worktree's shown branch as
  necessarily current.
- **Dirty/uncommitted state is only ever claimed for the current
  worktree** (§6.3) — this is the direct mechanism satisfying "clearly
  distinguish committed repository evidence from uncommitted worktree
  state": `head_commit`/`pinned_commit`/`checked_out_commit` are all
  committed-repository facts (safe to compare across worktrees/syncs);
  `is_dirty` is explicitly scoped to "this one checkout, right now, as
  of this sync" and never extrapolated to any other worktree.
- **Graceful, silent degradation on any single `git` command failure**:
  a missing `git` binary, a non-git `project_root`, an inaccessible or
  pruned worktree path, or a malformed `.gitmodules` entry each
  degrade the affected field(s)/row to `None`/absence — never raises,
  never aborts the rest of `sync`. This matches `discovery.py`'s own
  posture (a malformed manifest degrades that one manifest, not the
  whole discovery pass) rather than `source_resolution.py`'s (a vendor
  clone failure *is* a hard, surfaced error) — topology detection is
  supplementary orientation, not a gating operation.

## 9. Cache / index implications

**No change to where `context-graph.db` lives** — still exactly
`project_root / "context-graph.db"` (`open_graph`, unchanged). This is
the deliberate, investigated answer to "how should cache/index identity
behave when the same repository appears through multiple worktrees":
**each worktree keeps its own separate database file, as it already
does today** — this is not "duplicating a graph per worktree" in the
sense the user's own constraint warns against, because a worktree can
genuinely hold different file content (different branch, different
dirty state) at any moment, so per-worktree isolation is already the
*correct* behaviour for the vendor/symbol/doc content those files
describe, not an accidental duplication this phase introduces.

What this phase adds is **recognition, not consolidation**: worktree A's
own `context-graph.db` records `common_dir` (shared identity) plus its
own worktree row (`is_current=1`) plus whatever sibling worktrees
(including B) `git worktree list` reported *as of A's own last sync*.
Worktree B's own separate `context-graph.db`, when it syncs, records the
mirror image (`is_current=1` for itself, A as a sibling). There is no
shared file, no write contention, and therefore no risk of "conflating
two different HEAD revisions" — each database is unambiguous about
which row describes *itself*. A full merged/shared-storage design
(one `context-graph.db` per repository rather than per worktree) was
considered and rejected as unnecessary for this phase's minimum
capability: it would require relocating `open_graph`'s db path to the
common-dir (a change touching every call site in `cli.py`/`sync.py`/
`skill.py` that currently does `project_root / _GRAPH_DB_FILENAME`
directly) for a benefit (deduplicating identical vendor/symbol/doc
content across worktrees) this phase's own evidence does not yet call
for — named as a deferral (§16), not built speculatively.

## 10. Edge cases and failure behaviour

| Case | Behaviour |
|---|---|
| `project_root` is not inside a Git repository at all | `detect_git_topology` returns `None`; zero rows in all three tables; `query topology` prints a plain "not a Git repository" line; every other `sync`/`query` command is completely unaffected (matches today's non-git-project behaviour exactly). |
| `git` binary not on `PATH` | Same as above — degrades identically to "not a Git repository," no error surfaced (topology is supplementary; `sync` must not fail because `git` is missing when a project has no vendors needing source resolution either). |
| `project_root` is itself a linked worktree (not the main one) | `common_dir` still resolves correctly (it is defined to be identical across every worktree); this worktree's own row gets `is_current=1`; the *main* worktree appears as a sibling row. No special-casing required — confirmed this is git's own designed behaviour, not an assumption. |
| `project_root` is a bare repository | `is_bare=1` on its own worktree row (from `worktree list --porcelain`'s own `bare` marker); `head_commit`/`branch` may be present or absent depending on whether a HEAD ref exists; no crash. |
| Sibling worktree's directory was deleted without `git worktree remove` | `git worktree list --porcelain` reports it `prunable` — `is_prunable=1` on that row, surfaced directly in `query topology` output as e.g. "prunable (directory missing)" rather than a silent stale entry. |
| Truly unborn branch (fresh `git init`, no commits yet) | `head_commit=None`, `branch` = the unborn branch name if resolvable, no crash. |
| `.gitmodules` exists but a path was never `git submodule init`'d | `is_initialized=0`, `checked_out_commit`/`revision_matches_pin`/`child_branch`/`child_is_dirty` all `None` — `pinned_commit` is still populated (it comes from the parent's own tree, independent of the child's init state). |
| `.gitmodules` references a path with no corresponding gitlink in `HEAD` (e.g. added to `.gitmodules` but never `git add`-ed) | `pinned_commit` lookup fails; that submodule is skipped from `git_submodules` entirely (no fabricated/`NOT NULL`-violating row) with no error — a genuinely malformed/mid-edit state, not this phase's job to repair or flag beyond omission. |
| Submodule checked out at a commit not reachable from the pinned commit's history at all (e.g. an entirely different branch) | Still just `revision_matches_pin=0` — no attempt to characterize *how* divergent (ahead/behind/unrelated); that finer distinction is explicitly deferred (§16). |
| Two worktrees of the same repository synced independently, one mid-way through a rebase (detached HEAD, no branch) | `is_detached=1`, `branch=None`, `head_commit` still populated — detached HEAD is a first-class, correctly-representable state, not an error case. |

## 11. Backwards-compatibility considerations

- **Schema version bump `"9"` → `"10"`**, new tables only
  (`CREATE TABLE IF NOT EXISTS`) — no existing table's columns change,
  so **no `_migrate_*` function is needed** for this phase (the existing
  four migrations remain exactly as they are; a fifth is only ever
  needed for an *altered* table, not a new one — confirmed against
  every existing `_migrate_*` function's own docstring pattern).
- An on-disk `context-graph.db` created under schema `9` opens fine
  under the new code: `init_schema`'s `CREATE TABLE IF NOT EXISTS`
  creates the three new empty tables in place; the next `sync` populates
  them normally. No data loss, no forced re-sync.
- `rebuild_deterministic`'s signature gains three new keyword-only
  parameters (`git_repositories`, `git_worktrees`, `git_submodules`),
  each defaulting to `()` — mirroring `doc_chunks`'s own
  Phase-32-added-with-a-default precedent exactly, so any existing
  caller (including every current test) that doesn't pass them keeps
  working unchanged.
- `query topology`'s absence of a `--json` result when there's no Git
  repository is a *new*, previously-impossible response shape for a
  `query` subcommand (every existing one either errors "not found" for
  a bad name or returns real data) — documented explicitly in
  `docs/cli-reference.md` as this command's own distinct empty-state,
  not assumed to be self-evident.
- No `vendor.toml` schema change, no `VendorConfig` change — confirmed
  unnecessary since submodules are deliberately not vendors (§4).

## 12. Exact implementation sequence

1. `src/codecompass/git_topology.py` — `WorktreeInfo`/`SubmoduleInfo`/
   `RepositoryTopology` dataclasses, `detect_git_topology`, and the
   private `_run_git`/parsing helpers (§6). Unit-testable in total
   isolation from `graph.py`/`sync.py`.
2. `src/codecompass/graph.py` — bump `_SCHEMA_VERSION` to `"10"`; add
   the three `CREATE TABLE IF NOT EXISTS` blocks + indexes (§4); add
   `GitRepositoryRow`/`GitWorktreeRow`/`GitSubmoduleRow` dataclasses
   (natural-key-based: `GitWorktreeRow`/`GitSubmoduleRow` carry the
   parent's `common_dir` as a plain field, resolved to the integer
   `git_repositories.id` inside `rebuild_deterministic`, exactly like
   every existing natural-key row type); extend `rebuild_deterministic`
   to delete-then-reinsert all three (children before parent:
   `git_worktrees`/`git_submodules` before `git_repositories`, same
   FK-respecting order every other table already follows).
3. `src/codecompass/sync.py::rebuild_project_graph` — call
   `git_topology.detect_git_topology(project_root)` once; convert its
   result (if not `None`) into the three row-dataclass lists; pass them
   into `rebuild_deterministic`. A `None` result means "pass three empty
   tuples," not a special code path.
4. `src/codecompass/cli.py` — new `@query_app.command("topology")`
   function, `_graph_session`-based, `--json` flag, rendering per §7.1;
   a `_render_topology_table`/`_render_topology_json` helper pair
   mirroring `query_vendors`'s own existing shape.
5. `src/codecompass/skill.py::render_tool_skill` — add the `query
   topology` line to the Commands list and the three new table names to
   the trailing schema-table list (§7.2).
6. `docs/cli-reference.md` — new `query topology` section (§7.3).
7. `architecture/context-graph-schema.md` — add the three new tables to
   the existing node-table listing, following that page's own exact
   format.
8. `architecture/overview.md` and/or a new
   `architecture/git-topology.md` (decide during implementation based on
   how large the addition is relative to `overview.md`'s own existing
   "keep current-truth docs from growing unbounded" discipline,
   `decisions/0060`'s own precedent for splitting out design content —
   not a decision gate, an ordinary editorial call `docs-maintainer`
   makes same as any other phase).
9. `decisions/0063-git-worktrees-and-submodules-as-a-new-graph-capability.md`
   (exact number confirmed live at implementation time, not assumed —
   `0062` is the highest existing ADR as of this plan) — records the
   `vendors`-rejection reasoning (§4), the per-worktree-database
   decision (§9), and the "mechanical fact only, no semantic edge"
   posture (§8), written in the **same commit** as the schema change
   per `CLAUDE.md` §2.
10. Tests (§13).
11. `CHANGELOG.md` `[Unreleased]` entry, `planning/ROADMAP.md` status
    flip, `planning/CONTEXT.md` update, phase retro, learning triage,
    drift audit, completion audit, final reconciliation — the
    now-corrected closeout sequence this session's own `L-060`/`L-061`
    fix established, unchanged by this phase.

## 13. Tests

**Unit (`tests/test_git_topology.py`, new)** — every test builds its own
disposable `git init`-ed fixture under `tmp_path` (no dependency on this
repository's own real state, matching every other detection module's
existing test style, e.g. `tests/test_discovery.py`):

- Not a Git repository → `detect_git_topology` returns `None`.
- Single-worktree, clean repo → one `git_repositories` row, one
  `git_worktrees` row (`is_current=1`, `is_dirty=False`, correct
  `branch`/`head_commit`), zero `git_submodules` rows.
- Dirty working tree (an uncommitted edit) → `is_dirty=True`.
- Untracked-only change (no edits to tracked files) → `is_dirty=True`
  (confirms the stated "untracked counts as dirty" definition, §6.3).
- Detached HEAD (`git checkout --detach <sha>`) → `is_detached=True`,
  `branch=None`, `head_commit` still populated.
- Unborn branch (fresh `git init`, no commit yet) → `head_commit=None`,
  no crash.
- Two real worktrees of one fixture repo (`git worktree add`) → both
  appear in `git_worktrees`, sharing one `git_repositories.common_dir`;
  exactly one has `is_current=1` depending on which path
  `detect_git_topology` was called against; the other has `is_dirty=None`.
- A `prunable` worktree (create one, delete its directory without
  `git worktree remove`) → `is_prunable=1`.
- One real submodule fixture (`git submodule add <local bare repo>
  sub`) fully in sync → `pinned_commit == checked_out_commit`,
  `revision_matches_pin=True`.
- Same fixture, submodule checked out one commit behind the pin (a real
  divergence constructed inside the fixture, `git -C sub checkout
  HEAD~1` without updating the parent) → `revision_matches_pin=False`,
  both SHAs correctly distinct and correctly attributed (pinned vs.
  checked-out never swapped).
- Submodule declared in `.gitmodules` but never initialized →
  `is_initialized=False`, `pinned_commit` still populated, every
  child-state field `None`.
- `git` binary missing (monkeypatch `shutil.which` to return `None`) →
  `detect_git_topology` returns `None`, no exception.

**Integration (`tests/test_graph.py`, `tests/test_sync.py` — extend
existing test files, matching their own established pattern)**:

- `rebuild_deterministic` called with real `GitRepositoryRow`/
  `GitWorktreeRow`/`GitSubmoduleRow` fixtures persists and round-trips
  correctly; called with all three defaulted to `()` behaves exactly as
  every pre-this-phase test already expects (backwards-compatibility
  confirmed by not having to touch any existing test).
- `rebuild_project_graph`, run against a real disposable Git fixture
  (not a mock), produces the expected `git_repositories`/`git_worktrees`/
  `git_submodules` rows via the actual production call path — the
  `L-021`-required "test through the real call site," not only the
  isolated function (`CLAUDE.md` §1's own standing rule for a phase that
  adds behaviour to an existing function with a real call site).

**CLI (`tests/test_cli.py`, extend)**:

- `codecompass query topology` against a real synced fixture prints the
  expected structure; `--json` output round-trips through `json.loads`;
  against a non-git fixture prints the graceful empty-state line, exit
  code 0 (not an error).

**Real-repository validation (this repository itself, plus disposable
scratch fixtures — required by the user, run during implementation, not
merely in unit tests with synthetic data)**:

1. **Submodules, real, no fixture needed**: run `codecompass sync`
   against this actual repository's own working tree; confirm
   `git_submodules` holds exactly two rows
   (`protocol/codecompass-adaptor-protocol`,
   `adapters/haskell`), each with the real `.gitmodules` URL, the real
   pinned SHA (cross-checked against `git ls-tree HEAD`, confirmed
   live at plan-writing time: `596fb94f...`/`dfd7a783...`), and
   `revision_matches_pin=True` (confirmed live: both currently match).
2. **Submodule divergence, real, disposable clone required** (the real
   checkout's submodules currently match their pins, so this case must
   be constructed, never by editing the real checkout): `git clone
   --recurse-submodules` this repository into the session scratchpad;
   inside the clone's `adapters/haskell/`, `git checkout HEAD~1`
   (a real, valid prior commit in that submodule's own real history) —
   *without* touching the parent's gitlink; run `codecompass sync`
   inside the scratch clone; confirm `revision_matches_pin=False` with
   both the pinned and the (different) checked-out SHA correctly shown.
   Scratch clone discarded after — never a change to the real
   `adapters/haskell` submodule or its pin.
3. **Worktrees, real, disposable required** (the real checkout currently
   has exactly one worktree): from the real checkout, `git worktree add
   <scratchpad-path> -b codecompass-phase76-worktree-test` (additive,
   non-destructive — does not touch `main`'s own checkout); run
   `codecompass sync` from **both** the main checkout and the new
   worktree; confirm both `context-graph.db`s report the **same**
   `git_repositories.common_dir` and correctly mark themselves
   `is_current=1` while showing the other as a sibling — this is the
   literal acceptance test: "main checkout + feature worktree recognized
   as one repository, two checkout states, not two unrelated projects."
   Additionally test from the new worktree: make an uncommitted edit
   (dirty), then `git checkout --detach <sha>` (detached HEAD) — confirm
   `query topology` reflects each state correctly. **Cleanup, mandatory
   before this phase closes**: `git worktree remove
   <scratchpad-path>` (or `--force` if a dirty test edit blocks it) and
   `git branch -D codecompass-phase76-worktree-test` — the real
   repository must return to exactly one worktree, no disposable branch
   left behind, confirmed via `git worktree list`/`git branch` showing
   the pre-test state restored.

## 14. Documentation / ADR / roadmap / context / changelog impacts

- **`decisions/0063`** (§12.9) — new ADR, required (a genuinely
  non-obvious tradeoff: rejecting `vendors` reuse, choosing per-worktree
  database isolation over consolidation, choosing mechanical-only
  facts over semantic edges).
- **`architecture/context-graph-schema.md`**, **`architecture/overview.md`**
  (or a new `architecture/git-topology.md`, decided during
  implementation, §12.8) — current-truth updates, same commit as the
  schema change (`CLAUDE.md` §2).
- **`docs/cli-reference.md`** — new command section (§7.3), required for
  `check_cli_commands_documented`.
- **Cross-references only, not rewrites**, to
  `docs/developer/haskell-adapter-submodules.md`,
  `docs/protocol-adapter/*.md`, `architecture/adapter-interface.md`: a
  one-line pointer ("CodeCompass can now also show this mechanically via
  `codecompass query topology`") added where each already discusses
  manual `git submodule` workflow — these pages' own purpose (how a
  *human* clones/updates) is unchanged and not restated.
- **No new `docs/domain/concepts/*.md` page in this phase** — a
  considered, explicit call, not an oversight: this project's existing
  domain-corpus pages (`vendor.md`, `provenance.md`, etc.) each carry a
  `status: APPROVED (date, actual user/domain owner)` header, meaning
  they went through `domain-skeptic` adversarial review *and* the real
  domain owner's own sign-off (`decisions/0060`) — a heavier process
  than this phase's own well-defined, standard-Git-semantics scope
  needs or than the user's own request asks for. If `docs-reconstructor`'s
  per-phase drift audit (§17) finds the domain corpus is now materially
  incomplete without one, that becomes a normal DoD finding to act on
  same as any other phase, not a decision pre-made here either way.
- **`CHANGELOG.md`** — `[Unreleased]` → `Added` entry, this phase only.
- **`planning/ROADMAP.md`** — new Phase 76 row (`planned`, this plan
  file linked), added in this same commit per `CLAUDE.md` §1.
- **`planning/CONTEXT.md`** — corrected in this same commit: Phase 76 is
  now named as this git-topology phase (direct user request), and the
  prior "recommended second Priority A Ledgerkit trial" text is
  reworded to no longer claim the "Phase 76" number for itself (§0) —
  it remains a live, valid backlog recommendation, just not
  pre-numbered.

## 15. Task-context evaluation methodology

Two realistic, concretely-grounded scenarios (not invented to flatter
the feature — both trace to real, already-documented project needs):

- **Task A — submodule pin bump** (grounded in `decisions/0058`'s own
  "version-compatibility matrix must be kept current" requirement): *"Is
  the `adapters/haskell` submodule's checked-out commit the same as
  what CodeCompass's own `main` branch has pinned? If a contributor ran
  `git submodule update --remote` locally without committing, would that
  be visible?"*
- **Task B — worktree-vs-main review** (the user's own named scenario,
  matching real `Agent(isolation: "worktree")` usage in this
  environment): *"I'm in a linked worktree on `feature-x`. Is this the
  same repository as the `main` checkout elsewhere on this machine, or
  a separate clone? Is my working tree dirty? What's `main`'s own HEAD,
  as last observed?"*

**Method**: for each task, the lead performs (and records, in the phase
retro, not a separate reference-project-style report — this validates
CodeCompass's *own* new capability against CodeCompass's *own* repository,
which does not need `reference-project-protocol.md`'s external-target
ground-truthing machinery or a fresh-agent dispatch to avoid
prior-knowledge contamination the way an *external* reference-project
trial does) a **before** pass (ordinary tools only: `git submodule
status`, `git config -f .gitmodules --list`, `git ls-tree`, `git
worktree list`, `git status`, manually cross-referencing which SHA is
which) and an **after** pass (`codecompass query topology [--json]`
alone), recording for each:

- Which of the required facts (pinned SHA, checked-out SHA, match/
  mismatch, repository identity, current vs. sibling worktree, dirty
  state) were obtained, and via how many distinct commands.
- Any point where the *before* pass risked conflating pinned vs.
  checked-out (a real, easy mistake — `git submodule status`'s own
  single SHA column changes meaning with `--cached`, confirmed
  directly, §6.4) that the *after* pass's explicit two-column output
  cannot make.
- Whether the *after* pass surfaced anything the *before* pass would
  have missed entirely without deliberately knowing to check for it
  (e.g., a `prunable` worktree, or an uninitialized submodule).

**Efficiency indicator** (cheap, honestly measured, not invented):
number of distinct `git`/config-reading commands the *before* pass
needed vs. the single `query topology` call — reported as a plain count
in the retro, explicitly **not** converted into a token-savings or
time-savings claim, per the user's own instruction.

**Relationship to the existing `context-evaluator` discipline**: this
phase does not dispatch `context-evaluator` — that role's entire
methodology is built around independently ground-truthing an *external*
reference project (`context-quality-evaluation.md` §1's own "inspect the
target repository directly" framing presumes CodeCompass and the target
are different projects). Using it here, on CodeCompass validating a
capability against itself, would not add independent ground-truthing
value the lead's own direct git-command verification doesn't already
provide. **Explicit follow-up, not part of this phase's own DoD**: the
next external Priority-A Ledgerkit validation trial (recommended at
Phase 75's own closeout, still unclaimed by a phase number, §0) should
deliberately pick a task where Git topology awareness could plausibly
matter (Ledgerkit itself has no submodules or multi-worktree workflow
today, per its own real state — this would need to be a genuinely
existing need there, not manufactured, matching that trial's own
"genuine task only" discipline).

## 16. Explicit non-goals and deferrals

Restating the user's own list, plus this plan's own additions, each
with its concrete reason:

- Generic multi-repository federation, cross-clone/cross-machine
  identity (only `common_dir`, a single-machine concept, is used —
  `origin_url` is captured but not used as an identity key this phase).
- Cross-repository symbol-level graphs (no attempt to index a
  submodule's own source content at all — `git_submodules` is pure
  topology metadata, no nested `context-graph.db`, no recursive sync).
- Automatic branch creation, automatic worktree creation/removal, merge/
  rebase/conflict management, agent orchestration, generic Git hosting/
  GitHub management, Docker/container topology, MCP functionality — none
  touched; this phase is read-only observation of existing topology.
- A complete monorepo/workspace abstraction — three narrow tables, not a
  general workspace model.
- Detecting "is `project_root` itself someone else's submodule" (§5) —
  the acceptance model is strictly downward (repository → its own
  worktrees/submodules); upward ancestry detection is a different
  question with its own real ambiguities (which of possibly several
  on-disk ancestor repositories, if any, actually declares this
  directory as a submodule — not answerable by a simple upward walk the
  way `--git-common-dir` cleanly answers the downward case).
- Recursive submodules-of-submodules (§6.5) — one level only.
- Characterizing *how* a diverged submodule commit relates to its pin
  (ahead/behind/unrelated, `git merge-base` analysis) — `revision_matches_pin`
  is a boolean only; finer characterization is real, additional scope
  with no evidence yet that the boolean isn't sufficient for the tasks
  this phase's own evaluation (§15) names.
- A shared/consolidated `context-graph.db` across a repository's
  worktrees (§9) — per-worktree isolation is kept, consolidation
  deferred pending evidence it's actually needed.
- Cross-linking a `git_submodules` row to a `vendors` row on path/name
  match, for the (currently nonexistent in this repository) case of a
  submodule that is *also* a declared `vendor.toml` dependency — no real
  instance exists to design against; deferred until one does.
- Any change to `chat.py`/Phase 24's own routing scope (§2) — explicitly
  not silently redefined.
- A new `docs/domain/concepts/*.md` page (§14) — deferred pending a real
  drift-audit finding that one is needed.
- Semantic relationship edges between the two submodules, or between
  either submodule and anything else (§8) — mechanical facts only.

## 17. Human decision gates

**None identified.** Every design choice above was resolved by direct
precedent already established in this codebase (the `discovery.py`/
`usage.py` detection-module pattern; `source_resolution.py`'s `git`
subprocess conventions; `vendors`'s own documented narrow scope ruling
it out for submodules; `rebuild_deterministic`'s existing
default-to-`()` backwards-compatibility precedent; `decisions/0025`'s
existing sync-freshness contract), by the non-goals list, or by ordinary
engineering judgement with a stated, reversible rationale (e.g., "dirty"
counting untracked files; per-worktree database isolation). If
implementation surfaces a genuine ambiguity this plan didn't
anticipate, work pauses and the lead asks before proceeding, per
`CLAUDE.md` §1 — but none is manufactured here to be safe.

## 18. Runnable verification commands and expected outcomes

```bash
# Unit + integration
.venv/bin/pytest tests/test_git_topology.py tests/test_graph.py \
  tests/test_sync.py tests/test_cli.py -q
# Expected: all pass, including every real-git-fixture case in §13.

# Full regression (no unrelated breakage)
.venv/bin/pytest -q
# Expected: same pass count as this plan's own baseline (641 passed,
# 2 skipped) plus this phase's new tests, all passing.

.venv/bin/ruff check .
# Expected: all checks passed.

python3 scripts/check_user_docs.py --strict
# Expected: no findings — in particular check_cli_commands_documented
# and check_generated_artifacts_match_source both pass, confirming the
# new command landed consistently in cli.py + docs/cli-reference.md +
# skill.py's generated SKILL.md.

python3 scripts/check_knowledge_base.py
# Expected: no findings.

# Real-repository validation (this repository itself)
codecompass sync --yes --budget 0
codecompass query topology
codecompass query topology --json
# Expected: two git_submodules rows (protocol/codecompass-adaptor-protocol,
# adapters/haskell), both revision_matches_pin=true; one git_worktrees
# row, is_current=true, branch=main, is_dirty reflecting real working-
# tree state at the time.

# Disposable worktree validation (see §13.3 for full sequence + mandatory cleanup)
git worktree add /tmp/codecompass-phase76-worktree-test -b codecompass-phase76-worktree-test
cd /tmp/codecompass-phase76-worktree-test && codecompass sync --yes --budget 0 && codecompass query topology
cd /home/cormac/projects/codecompass && codecompass query topology
# Expected: both invocations report the same git_repositories.common_dir;
# each correctly marks itself is_current and the other as a sibling.
git worktree remove /tmp/codecompass-phase76-worktree-test --force
git branch -D codecompass-phase76-worktree-test
git worktree list
# Expected: back to exactly one worktree, no leftover branch.
```

## 19. Definition of Done

Per `CLAUDE.md` §5, unchanged process, all of the following genuinely
hold (not merely asserted) before `planning/ROADMAP.md` marks Phase 76
`done`:

1. Code implemented per §12; `git_topology.py`, `graph.py`, `sync.py`,
   `cli.py`, `skill.py` all consistent with each other (mechanically
   confirmed, §3/§18).
2. §13's full test suite passes, including the real-repository and
   disposable-fixture validation (submodule divergence, two-worktree
   recognition, detached HEAD, dirty/clean) — not only synthetic
   isolated-function tests, satisfying `CLAUDE.md` §1's real-call-site
   requirement.
3. `docs/`, `architecture/`, `decisions/` updated per §14, same commit
   as the code.
4. §15's task-context evaluation performed and recorded honestly
   (including if the answer turns out to be "less advantage than
   hoped") — not skipped, not assumed positive in advance.
5. An independent `docs-reconstructor` per-phase drift audit finds no
   current-truth doc left misdescribing the system, scoped to this
   phase's diff.
6. `CHANGELOG.md` entry added, same commit.
7. `planning/CONTEXT.md` reflects the new state.
8. A phase retro exists at `planning/retros/phase-76-git-repository-topology.md`,
   including §15's before/after findings.
9. Candidate learnings from the phase (if any) triaged by
   `knowledge-curator`.
10. An independent `release-phase-auditor` pass verifies every
    preceding condition against the exact commit about to be marked
    done, persisting `planning/retros/_audit-phase-76.md`, per this
    session's own `L-060` fix — any post-audit commit touching audited
    scope voids that pass and requires re-audit.
11. Disposable test worktree/branch and scratch submodule-divergence
    clone are fully cleaned up — `git worktree list`/`git branch`/
    `git status` on the real repository show no leftover trace (§13.3,
    §18).
12. Only once every one of the above genuinely holds does a genuinely-
    dispatched `roadmap-context-curator` (never the lead self-serving
    it, per this session's own `L-060` fix) perform final reconciliation
    and flip `planning/ROADMAP.md`'s Phase 76 row to `done`.

**Not done merely because Git metadata can be parsed** — it must be
correctly represented, provenance-grounded, reachable through
`codecompass query topology` and the generated Skill, and shown (§15)
to help at least one realistic task.
