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
That amendment fixed all eight (committed `5c0705a`), grounded in
newly-gathered live evidence, while preserving every part of the
original direction confirmed sound.

**Second amendment note (2026-09-28, same day):** a further direct
review of `5c0705a` found six more concrete issues, all fixed here,
again grounded in newly-gathered live evidence: an implicit, undisclosed
Git ≥2.31 requirement introduced purely by using `--path-format=absolute`
for convenience; a missing, distinct "topology not yet indexed" state
(an upgraded-but-unsynced database is neither `detected`, `not_git`, nor
`unavailable`, but the previous amendment never said so); a genuine
internal contradiction between the plan's own primary discovery command
(which requires a working tree) and its own claim of bare-repository
support; a credential-sanitization guarantee ("credentials are never
persisted") that overclaimed relative to an implementation that only
ever touched `http(s)` URLs, leaving an `ssh://user:password@host/...`
form's password fully exposed; and a task-context evaluation whose
baseline/treatment fixtures were never actually verified equivalent
before dispatch, despite `codecompass sync` itself being able to alter
the treatment fixture's own tracked-file/dirty state relative to
baseline. §"Preserved from the original plan, unchanged by either
amendment" at the close of this document is re-confirmed, not reopened,
by this second amendment. No implementation code exists yet for this
phase — this remains a planning-only amendment.

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
  3.9) is safely available for §12.6's path-safety check. **This says
  nothing about the *Git* version available, only the *Python*
  version** — the two are unrelated (§5, second amendment).
- **Newly verified for the first amendment**: `git config -f .gitmodules
  --list -z`, piped through `tr '\0' '\n'` for display, returns the
  same four `submodule.<name>.path`/`.url` lines as the non-`-z` form on
  this repository's own two-entry `.gitmodules` — confirming the
  NUL-delimited form (§12.9) is a safe drop-in that additionally protects
  against a pathological embedded-newline value, at no cost.
- **Newly (re-)verified for the first amendment, the schema-migration
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
- **Newly verified for the second amendment — the version-floor
  finding (§5)**: run live, from `src/codecompass/` (a real
  subdirectory), `git rev-parse --show-toplevel` returns an **already
  absolute** path (`/home/cormac/projects/codecompass`) with no
  `--path-format` flag at all, while `git rev-parse --git-common-dir`
  (also no flag) returns a **relative** path (`../../.git`, relative to
  the `-C`/cwd directory the command was run against — confirmed by
  running the identical commands via `git -C src/codecompass rev-parse
  ...` from the repository root, producing the identical relative
  output). `--show-toplevel` has been part of Git since long before any
  version this project could plausibly encounter; `--git-common-dir`
  (and `git worktree` itself) was added in **Git 2.5** (July 2015) —
  `--path-format=absolute` (2.31, 2021) is a later convenience for
  resolving the second value automatically, never load-bearing for
  correctness. Manual resolution (`(worktree_root_or_project_root /
  raw_common_dir).resolve()`) is confirmed to produce the identical
  absolute path either way, with no version dependency beyond 2.5.
- **Newly verified for the second amendment — the bare-repository
  finding (§6)**: a disposable `git init --bare` fixture, created and
  destroyed during planning (never touching this repository), confirms
  `git rev-parse --show-toplevel` fails there with exit `128` and the
  distinctive stderr `"fatal: this operation must be run in a work
  tree"` — a message textually unrelated to and never confusable with
  `"not a git repository"` — while `git rev-parse --git-common-dir`
  *succeeds* there (`.`) and `git rev-parse --is-bare-repository` prints
  `true`. Confirmed this is a real, reproducible contradiction in the
  previous amendment's own text (§6 there listed the combined discovery
  command as the very first, unconditional step, which cannot succeed
  against a bare repository, while a separate edge-case note claimed
  bare-repository support) — not a hypothetical.
- **Newly verified for the second amendment — the credential-sanitizer
  finding (§8/§12.7)**: `urllib.parse.urlsplit` run live against
  `ssh://user:secret@example.com/repo.git` returns `scheme='ssh'`,
  `username='user'`, `password='secret'`, `hostname='example.com'` —
  structurally identical extraction to the `https://` case the previous
  amendment's own sanitizer already handled, confirming the previous
  sanitizer's `if parsed.scheme not in ("http", "https")` guard was the
  exact reason an SSH-form password would have passed through
  completely unredacted. A revised sanitizer (exact code in §12.7),
  tested live against eight cases — `https://user:password@host/repo.git`,
  `https://TOKEN@host/repo.git`, `ssh://user:password@host/repo.git`,
  `ssh://git@host/repo.git`, `git@host:org/repo.git` (this repository's
  own real submodule URL form), a plain credential-free HTTPS URL, an
  HTTPS URL with an explicit port, and this repository's own real,
  live `adapters/haskell` submodule URL — produces exactly: every
  password/token stripped from every case that had one (including the
  SSH case), a bare non-secret username preserved for the non-`http(s)`
  case (`ssh://user:password@host/repo.git` → `ssh://user@host/repo.git`,
  password gone, identity kept), and both SCP-like real submodule URLs
  left completely byte-for-byte unchanged.
- **Newly verified for the second amendment — the fixture-equivalence
  finding (§15)**: `git status --porcelain` on this repository's own real
  checkout, cross-referenced against `.gitignore` (`context-graph.db`
  and `vendor/` are both listed and confirmed `!!`-ignored via `git
  status --porcelain --ignored=matching`) and `git ls-files` (confirming
  `.claude/skills/codecompass/SKILL.md`, `CLAUDE.md`, and
  `.claude/commands/discovery.md` are all **tracked**, currently clean,
  files) — establishes the concrete mechanism the fixture-equivalence
  requirement guards against: `codecompass sync`/`index` regenerating
  those three *tracked* files with new, topology-aware content (once
  Phase 76 ships) would make `git status --porcelain` show them
  modified in the treatment fixture alone, a real, mechanical source of
  baseline/treatment asymmetry `context-graph.db`/`vendor/`'s own
  gitignore status does not protect against.

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

**Second amendment: a fifth, distinct state exists — "not yet
indexed" — represented by the *absence* of the `meta.git_topology_status`
key entirely, deliberately not a fifth `TopologyStatus` enum member**
(§6 gives the full reasoning). An existing schema-v9 database, opened
under Phase 76's own code (§11's introspection-based migration
guarantees this is safe and non-destructive) but not yet re-synced,
gains the three new `git_*` tables via plain `CREATE TABLE IF NOT
EXISTS` — but `meta.git_topology_status` is only ever written by
`rebuild_deterministic` (§12), which only runs on an actual `sync`. Its
absence is not an error and not ambiguous with any of the four real
detection outcomes above — it means, unambiguously, "Phase-76-aware
topology detection has never run against this graph." `TopologyStatus`
itself stays a 4-value enum, used only by `git_topology.py`/`sync.py`,
which by construction only ever run when detection is actually
happening; the query layer (§9) checks for the key's absence *before*
ever reading its value.

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
   --show-toplevel` (does not exist for a bare repository — §6's
   decision procedure covers this explicitly; see that section for why
   bare repositories are out of scope for this phase, not a case this
   root-resolution step needs to handle). **This, not `project_root`, is
   the root every topology operation below is actually relative to.**
3. **Git common directory** — `git -C <project_root> rev-parse
   --git-common-dir` — the repository's own canonical identity (§4),
   identical from every worktree.

**Second amendment: no version-specific flag is used to obtain either.**
The first amendment's design used `--path-format=absolute` (Git 2.31,
2021) to get both as pre-resolved absolute paths in one call — a
genuine, undisclosed minimum-Git-version requirement, introduced purely
for the convenience of skipping a manual resolution step, and one this
project has never required anywhere else (`pyproject.toml`'s
`requires-python = ">=3.11"` constrains the *Python* running CodeCompass,
not the *Git* binary CodeCompass shells out to — the two are unrelated,
confirmed by the fact that nothing else in this codebase's own git usage
today, e.g. `source_resolution.py`'s `git clone`, depends on any Git
flag younger than the mid-2000s).

**Revised approach — one combined call, no flag newer than the
`git worktree`/`--git-common-dir` feature itself (Git 2.5, July 2015),
manual resolution for the one output that needs it**:

```
git -C <project_root> rev-parse --show-toplevel --git-common-dir
```

Confirmed live (§0): `--show-toplevel`'s own output is **always already
absolute**, on every Git version that has ever supported it (long
predating 2.5) — no resolution needed. `--git-common-dir`'s own output
is **relative to the `-C` directory** when the two roots differ (e.g.
`../../.git` from a subdirectory) — resolved deterministically, with no
filesystem guessing, as `(Path(project_root) / raw_common_dir).resolve()`.
This is Git resolving the path (the raw string it returns is unambiguous
and fully Git-defined); CodeCompass's own `.resolve()` call is ordinary,
deterministic path-joining against a location Git itself just named, not
a heuristic search — "walk upward looking for a `.git` entry" remains
explicitly rejected as a parallel, redundant, and strictly worse
mechanism, unchanged from the first amendment's reasoning.

**The resulting, now-explicit minimum: Git 2.5** (the version that
introduced `git worktree`/`--git-common-dir` at all) — nine years old as
of this phase, and *unavoidable* rather than a convenience, since
worktree awareness has no meaning at all on a Git predating the feature
itself. **If the combined `rev-parse` call fails for a reason other than
"not a git repository" or "bare repository, no work tree"** (§6's
decision procedure) — including, on a sufficiently old Git, an
"unrecognized option" error for `--git-common-dir` itself — the result is
an honest `UNAVAILABLE` with the raw reason surfaced (§6), never a
default assumption of `not_git` or a silent, ambiguous failure. No
separate, dedicated `git --version` parsing/comparison step is added
purely to detect this ahead of time — the existing stderr-based
classification already produces a correct, honest outcome for a
too-old Git without one, and adding a second detection mechanism for the
same eventuality would be exactly the kind of complexity this phase's
own "smallest model that works" discipline (§16) argues against.

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

**New tests required by the first amendment** (§18): topology detection
invoked from the repository root, and from a real nested subdirectory of
the same repository, must both identify the same worktree root and the
same `common_dir`.

**New test required by the second amendment** (§18): the exact same
nested-directory test above *is* the version-tolerance regression test
— since the revised design (above) has exactly one code path for
resolving `common_dir`, used unconditionally on every supported Git
version, invoking it from a subdirectory (where `--git-common-dir`'s raw
output is relative, exercising the manual-resolution branch) is not a
"fallback" distinct from some other "modern" path; it is the only path.
A second, additional test simulates a Git old enough to reject
`--git-common-dir` outright (a mocked non-zero exit with an "unrecognized
option" stderr) and confirms the result is `UNAVAILABLE` with that
reason surfaced, never misclassified as `NOT_GIT`.

## 6. Topology status model (new section — amendment, was folded into
§8/§10 in the original plan)

Direct response to the first amendment's review finding that "not a Git
repository," "`git` executable unavailable," "a `git` command failed,"
and "partial/malformed topology" could previously collapse into the
same observable result.

```python
class TopologyStatus(str, Enum):
    DETECTED = "detected"
    NOT_GIT = "not_git"
    UNAVAILABLE = "unavailable"
    PARTIAL = "partial"
```

**Second amendment: deliberately still four values, not five.** A
"topology not yet indexed" state is real and distinct (§4/§9) but is
represented at the *query layer*, by the absence of
`meta.git_topology_status` entirely, never as a value this enum itself
takes — `TopologyStatus` is `detect_git_topology`'s own return-value
type, and detection, by construction, only ever runs *while sync is
actually happening*; there is no code path where `detect_git_topology`
itself needs to represent "I have not run yet." Expanding the enum to
cover a state its own producer can never actually produce was judged
the wrong fix, per the review's own explicit preference for the smallest
model that works.

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
2. `git -C project_root rev-parse --show-toplevel --git-common-dir`
   (§5's revised, version-tolerant form — no `--path-format` flag) — on
   failure, **the stderr text is pattern-matched** against two distinct,
   Git-documented, textually unrelated messages:
   - `"not a git repository"` → `NOT_GIT`, reason = `None` (an expected,
     unremarkable outcome — most projects using CodeCompass are not Git
     repositories at all; this is not an anomaly worth a diagnostic
     string).
   - **New (second amendment): `"this operation must be run in a work
     tree"`** — confirmed live (§0) to be the exact, distinctive message
     `--show-toplevel` produces against a bare repository, never
     confusable with the "not a git repository" message — → `UNAVAILABLE`,
     reason = `"no working tree (bare repository) — Git topology
     requires a checkout"`, additionally confirmed (not merely inferred
     from the message) via a second, cheap call, `git -C project_root
     rev-parse --is-bare-repository` (itself does *not* require a
     working tree, confirmed live, §0, to succeed against the same bare
     fixture where `--show-toplevel` failed), returning `true`. **This
     is the direct fix for the bare-repository contradiction**: Phase 76
     declares bare repositories out of scope (§16) rather than building
     a `--show-toplevel`-independent detection path for a scenario this
     project's own purpose (a project/source context tool, always
     operating against a real checkout) gives no evidence it needs — the
     `is_bare` column already in `git_worktrees`' own schema (§4) is not
     removed, since it remains meaningful for describing a *sibling*
     worktree in `worktree list`'s output (a real, legitimate topology:
     a bare "hub" repository with only linked, non-bare worktrees) —
     only the *current* worktree can never legitimately carry
     `is_bare=1` in this phase's own supported scope, since detection
     would already have stopped at `UNAVAILABLE` before any `git_worktrees`
     row for "self" is ever built.
   - Any other failure (permission error, a corrupted `.git`, an
     unrecognized-option error from a Git older than 2.5, an unexpected
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

**CLI/JSON must render all four states distinguishably, plus the
query-layer-only "not yet indexed" state ahead of all four (§4/§9)** —
`not_git` prints a plain, unremarkable "not a Git repository" line
(unchanged from the first amendment's intent, now actually correctly
gated only on a genuine `NOT_GIT` determination, and now also correctly
distinguished from the bare-repository case above, which is
`unavailable`, never `not_git`); `unavailable` prints "Git topology
could not be determined (<reason>)" (the bare-repository reason renders
here, plain and specific); `partial` prints whatever structure *was*
established, prefixed with a visible "topology partially determined:
<reason>" note rather than silently presenting incomplete data as if it
were complete; `detected` prints the full structure with no caveat
banner. §9 gives the exact rendering (including the "not yet indexed"
case, checked first, before any of the four); §18 tests all five
observable outcomes.

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
2. `git -C project_root rev-parse --show-toplevel --git-common-dir`
   (§5's version-tolerant form, no `--path-format` flag — supported
   since Git 2.5) — one call, two output lines: the first
   (`--show-toplevel`) always already absolute; the second
   (`--git-common-dir`) resolved via `(Path(project_root) /
   raw_output).resolve()` when relative (§5). Stderr pattern-matched per
   §6 step 2 (three distinguishable outcomes: not-a-repository,
   bare-repository, or any other failure).
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
- **Bare repository as the current checkout — second amendment,
  corrected from the previous text of this edge case, which
  contradicted §6's own decision procedure**: not supported by this
  phase (§6/§16) — `--show-toplevel` genuinely cannot succeed against a
  bare repository (confirmed live, §0), so detection stops at
  `UNAVAILABLE` with an explicit reason before any `git_worktrees` row
  for "self" is ever considered; there is no `is_bare=True` outcome for
  the *current* worktree in this phase's supported scope. `is_bare`
  remains a real, meaningful field for describing a *sibling* worktree
  a normal, non-bare current checkout observes via `worktree list` (a
  bare "hub" repository with linked, non-bare worktrees is a real,
  representable topology on the sibling side, even though CodeCompass
  itself can never be the one running *from* the bare one).
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
- **The precise guarantee (second amendment — corrected from an
  overclaim in the first amendment's own text, which said "credentials
  are never persisted or surfaced" while an implementation that only
  ever touched `http(s)` URLs left an `ssh://user:password@host/...`
  form's password fully exposed): CodeCompass never persists or prints a
  password/token component of a parseable, URI-form Git remote URL.**
  A bare, non-secret username on a non-`http(s)` URI form (`ssh://git@
  host/...`) is preserved, not stripped, since it is ordinary connection
  identity, not a credential — this is a narrower, more precisely-worded
  guarantee than "no credentials," and now actually matches the
  sanitizer's own real behaviour (§12.7) exactly, rather than
  overclaiming beyond it. `context-graph.db`, CLI text, `--json` output,
  the generated Skill, and any future agent-context surface all only
  ever see the sanitized form; sanitization happens once, at detection
  time, before a `RepositoryTopology`/`SubmoduleInfo` object is even
  constructed — there is no code path that holds an un-sanitized URL
  past the point of the raw `git remote`/`git config` subprocess call
  that produced it. SCP-like syntax (`git@host:org/repo.git`) has no
  parseable userinfo component at all (confirmed live, §0, via
  `urllib.parse.urlsplit`) and is left untouched, not because it is
  assumed safe, but because there is nothing in it `urlsplit` can even
  identify as a username/password pair to strip — the invariant above
  is scoped to what is mechanically parseable, stated honestly rather
  than implying a guarantee over a string format Python's own URL parser
  cannot decompose.
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
   to `cli.py`'s existing `query_app`, same `--json`-flag convention as
   `query vendors`/`query relations`, but **not** `_graph_session`/
   `_open_graph_or_note`'s own shared open-or-note helper. **Third
   amendment: this was a real, confirmed defect in the previous
   design, not a stylistic choice** — `_open_graph_or_note` (`cli.py`)
   returns early, printing its own generic `_NO_GRAPH_NOTE` and never
   calling `graph.open_graph()` at all, the moment `context-graph.db`
   doesn't exist on disk yet. A brand-new worktree (no `context-graph.db`
   file at all) would therefore never reach the topology-specific "not
   yet indexed" message this phase defines — it would print the shared,
   generic note instead, silently losing the distinction §4/§6 require.
   **A narrow, `query-topology`-specific resolution function is added
   instead** (`_open_graph_for_topology`, `cli.py`, deliberately not a
   change to the shared `_open_graph_or_note`/`_graph_session` helpers,
   since every other `query` subcommand's existing behaviour for a
   missing database is correct as-is and out of scope here — "do not
   change unrelated query commands unless a shared helper change is
   demonstrably cleaner," and it is not, since `query topology`'s
   "absent" and "present-but-unindexed" cases collapse to the *same*
   rendered outcome while every other command's "absent" case is
   properly a distinct, generic "no context-graph.db yet" note the other
   commands still need):

   ```python
   def _open_graph_for_topology(project_root: Path) -> sqlite3.Connection | None:
       """None if context-graph.db doesn't exist at all -- read-only,
       never creates the file as a side effect of a read-only command
       (matching _open_graph_or_note's own posture), but prints nothing
       itself: query_topology's own caller renders the specific "not yet
       indexed" outcome for a None result, not _NO_GRAPH_NOTE."""
       db_path = project_root / _GRAPH_DB_FILENAME
       if not db_path.exists():
           return None
       return graph.open_graph(project_root)
   ```

   `query_topology`'s own body: `conn = _open_graph_for_topology(...)`;
   if `conn is None` **or** `graph.get_meta(conn, "git_topology_status")
   is None`, render "not yet indexed" (closing `conn` first in the
   second case, since it was genuinely opened); otherwise render the
   normal four-state result. This gives the three required, individually
   distinguishable outcomes exactly as specified:
   - **`context-graph.db` file absent entirely** → "not yet indexed" —
     no file created, no `git` invoked.
   - **File present, `meta.git_topology_status` absent** (an existing
     schema-v9 database, opened under Phase 76's own code per §11, but
     never re-synced) → "not yet indexed" — same rendered outcome as
     above, via the same code path, distinguished from it only in that a
     real connection was opened and closed; no `git` invoked either way.
   - **`meta.git_topology_status` present** → the normal four-state
     result below.

   Both "not yet indexed" sub-cases render identically: plain text "Git
   topology has not been indexed yet; run `codecompass sync`.", exit
   code 0, not an error; `--json` → `{"indexed": false}` (top-level; no
   `status`/`repository`/`worktrees`/`submodules` keys at all, rather
   than any of them being present-but-`null`, so a consumer cannot
   mistake "never indexed" for "indexed and confirmed not a git
   repository"). **`query topology` never invokes `git` itself, on any
   code path, including both of these** — it does not silently perform
   live detection merely because the persisted state is missing or
   incomplete.
   - When `git_topology_status` is present → `{"indexed": true, "status":
     ..., ...}` in JSON, and for text output:
     - `not_git` → a plain "not a Git repository" line.
     - `unavailable` → "Git topology could not be determined (<reason>)."
       (the bare-repository reason — "no working tree (bare
       repository)" — renders here, plain and specific, distinct from
       both the `not_git` and the "not yet indexed" lines).
     - `partial` → a visible "topology partially determined: <reason>"
       banner, **followed by** whatever structure was established (never
       silently suppressed).
     - `detected` → the full structure: repository identity, the active
       checkout's full detail (path/branch-or-detached/HEAD/dirty), every
       other known worktree (branch-or-detached/HEAD only, plus an
       explicit **"workspace: not probed"** line, never a bare blank —
       §8), and every submodule (path; `is_path_safe=False` rendered as
       "path escapes repository — refused" with nothing else shown for
       that row; otherwise child repository URL — rendered exactly as
       persisted, i.e. already sanitized per §8/§12.7 — parent-pinned
       revision — or "unresolved" when `NULL` — checked-out revision +
       match/mismatch, child branch/dirty if initialized).
   `--json`'s `indexed: true` branch mirrors the text output exactly
   (`status`, `reason`, `repository`, `worktrees`, `submodules` keys —
   `repository` is `null` for `not_git`/`unavailable`).
2. **`skill.py::render_tool_skill`**: gains a `query topology` line in
   the Commands list and `git_repositories`/`git_worktrees`/
   `git_submodules` in the trailing table-name list — the exact spots
   `CG-001`'s own motivating example named. `check_cli_commands_documented`
   and `check_generated_artifacts_match_source` mechanically catch a
   miss here.
3. **`docs/cli-reference.md`**: a new `query topology [--json]` section,
   documenting the "not yet indexed" outcome plus all four `TopologyStatus`
   outcomes explicitly (not just the happy path), and the resulting,
   now-explicit **Git ≥2.5 minimum** for worktree/common-dir detection
   (§5) — the first documented Git version requirement anywhere in this
   project — required for `check_cli_commands_documented`.
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
   function, rendering the "not yet indexed" plus four-state output (§9).
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
   graph, or any output surface). **Second amendment: revised — the
   first amendment's version only ever inspected `http`/`https` schemes,
   which left a password embedded in a `ssh://user:password@host/...`
   form completely unredacted, confirmed live (§0). The scheme-blind
   guard below fixes this while still preserving a non-`http(s)` URL's
   own bare, non-secret username** (e.g. `ssh://git@host/...`), per the
   precise guarantee restated in §8:

   ```python
   from urllib.parse import urlsplit, urlunsplit

   def sanitize_git_url(url: str) -> str:
       parsed = urlsplit(url)
       if not parsed.scheme or not parsed.hostname:
           return url  # not a parseable URI (e.g. SCP-like git@host:path)
       if not parsed.username and not parsed.password:
           return url  # nothing to strip
       if parsed.scheme in ("http", "https"):
           # A bare username-as-token is a common, real credential leak
           # pattern for http(s) (GitHub PATs, GitLab CI job tokens) --
           # strip all userinfo, not merely a password component.
           netloc = parsed.hostname
       else:
           # Any other URI scheme (ssh, git, ...): a password, if
           # present, is always a real secret and is stripped; a bare
           # username is ordinary, non-secret connection identity
           # (almost always the public `git` convention) and is kept.
           netloc = f"{parsed.username}@{parsed.hostname}" if parsed.username else parsed.hostname
       if parsed.port:
           netloc += f":{parsed.port}"
       return urlunsplit((parsed.scheme, netloc, parsed.path, parsed.query, parsed.fragment))
   ```

   Verified live during planning (§0) against eight real/representative
   URLs: `https://user:password@host/repo.git` and the bare-token-as-
   username `https://TOKEN@host/repo.git` both lose their userinfo
   entirely (`https://host/repo.git`); **`ssh://user:password@host/repo.git`
   loses only its password, keeping identity**
   (`ssh://user@host/repo.git`) — the exact fix for the vulnerability
   this revision closes; `ssh://git@host/repo.git` (no password) is left
   completely unchanged; this repository's own real
   `git@github.com:org/repo.git` SCP-like submodule URLs are left
   completely unchanged (no parseable userinfo at all — `urlsplit`
   itself reports an empty scheme for this form, confirmed live, §0); a
   plain `https://host/repo.git` with no userinfo, and an
   `https://user:pass@host:8443/repo.git` port-bearing form, both behave
   as expected (unchanged; port-preserving credential strip,
   respectively).

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
   --show-toplevel`/`--git-common-dir` (machine-oriented plumbing output,
   §5 — one line each, no `--path-format` dependency, manually resolved
   when relative), and `git status --porcelain` (the already-planned,
   already-correct machine-stable form, explicitly not plain `git
   status`) are the only text-parsing surfaces this module has — each
   chosen specifically because it is a documented, script-stable format,
   not human-oriented prose.

12.10. **Git version compatibility (second amendment)**: no command
   used anywhere in this module depends on a Git feature newer than
   `git worktree`/`--git-common-dir` themselves (Git 2.5, July 2015) —
   `--path-format=absolute` (Git 2.31, 2021), used by the first
   amendment's own design purely for the convenience of skipping a
   manual path-join, is removed entirely (§5). The resulting minimum
   (Git 2.5) is unavoidable, not a convenience: `git worktree` has no
   meaning at all on an older Git, so there is nothing this phase's own
   worktree-awareness half could do on such a version regardless of
   implementation choices. A Git old enough to reject `--git-common-dir`
   outright surfaces as `UNAVAILABLE` with the raw stderr as its reason
   (§6) — an honest diagnostic, not a crash or a misclassification as
   `NOT_GIT` — with no separate, dedicated `git --version` parsing step
   added solely to detect this ahead of time (§5's own "smallest model"
   reasoning).

12.11. **Bare-repository detection (second amendment)**: `git -C
   project_root rev-parse --show-toplevel --git-common-dir` fails with
   the exact, distinctive stderr `"fatal: this operation must be run in
   a work tree"` against a bare repository (confirmed live, §0) —
   pattern-matched as its own branch in §6's decision procedure,
   independently confirmed (not merely inferred from the message text)
   via `git -C project_root rev-parse --is-bare-repository` (itself
   requires no working tree, confirmed live, §0, to succeed against the
   same bare fixture). Result: `UNAVAILABLE`, reason = `"no working tree
   (bare repository) — Git topology requires a checkout"` — never a
   `git_repositories`/`git_worktrees` row asserting the current checkout
   is bare, since no worktree row for "self" is ever built once
   detection has already stopped here.

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
1a. **New (second amendment) — demonstrate "not yet indexed"**: from the
   fresh disposable worktree, *before* running `codecompass sync` there
   for the first time, run `codecompass query topology` — with no
   `context-graph.db` at all in this brand-new worktree path, this
   exercises the same "not yet indexed" outcome as an upgraded-but-
   unsynced existing database (§4/§6/§9): "Git topology has not been
   indexed yet; run `codecompass sync`.", `--json` → `{"indexed": false}`.
   Confirms the query layer never performs live `git` detection as a
   fallback when the persisted state is simply absent.
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
4. **New: credential-bearing URLs** — a disposable fixture's
   `.gitmodules` declares two submodules: one with an
   `https://user:token@example.com/repo.git` URL, one with an
   `ssh://user:secret@example.com/repo.git` URL (the exact form the
   second amendment's own review named as unaddressed by the first
   amendment's sanitizer); confirm the persisted `child_repository_url`
   has no password/token component for either — the HTTPS row's
   userinfo is fully gone, the SSH row keeps `user@` but not `:secret`
   — both via direct database inspection and via `query topology
   --json` output.
5. **New: bare-repository fixture** — a disposable `git init --bare`
   fixture (never this repository); `codecompass sync` (or a direct
   `detect_git_topology` call) against it produces `status=unavailable`,
   reason mentioning "no working tree (bare repository)", no crash, and
   no `git_worktrees`/`git_submodules` rows asserting anything about a
   self that was never actually inspected.

## 14. Documentation / ADR / roadmap / context / changelog impacts

Unchanged in structure from the original plan; content requirements
expanded to cover both amendments' additions (§11's migration fix, §5's
three-root distinction and Git-version-floor disclosure, §6's status
model plus the bare-repository decision, §12.6/§12.7's path-safety/
sanitization mechanisms, §4/§9's "not yet indexed" state) wherever
`architecture/context-graph-schema.md`, `architecture/overview.md`/
`git-topology.md`, and `decisions/0063` describe the feature — these are
**content requirements on documents already named for updating**, not
new documents.

- `decisions/0063` — expanded scope per §12's own implementation-sequence
  item 9 (not the numbered subsection `§12.9`, which is the unrelated
  "robust parsing" note — a naming collision worth avoiding in the
  eventual ADR's own cross-references, noted here so a future reader of
  this plan isn't misled by it).
- `architecture/context-graph-schema.md`, `architecture/overview.md`/
  `git-topology.md` — expanded content per above, including the
  now-explicit Git ≥2.5 minimum and the bare-repository non-support
  decision.
- `docs/cli-reference.md` — the "not yet indexed" outcome and all four
  `TopologyStatus` outcomes (§9) documented explicitly, not just the
  happy path.
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

**Third amendment: replaced with a shared normalized seed, forked only
after normalization — the previous design's "treatment-only
normalization commit" and "identical worktree HEADs across both arms"
requirements directly contradicted each other** (a commit made in
treatment alone, after cloning, necessarily gives treatment a HEAD
baseline never shares). The fix moves normalization *before* the fork,
not after it:

```
normalized seed fixture (one clone, synced once, committed once)
       │
       ├── baseline clone/worktrees  — CodeCompass not installed/available
       │     (same commit as the seed; scenario constructed independently)
       │
       └── treatment clone/worktrees — CodeCompass installed, pre-synced
             (same commit as the seed; identical scenario constructed
             independently; a second, treatment-only sync afterward
             updates only its own gitignored context-graph.db)
```

1. **Build one seed clone** of this repository (`--recurse-submodules`),
   pinned at a fixed commit. Run `codecompass sync` in it **once** — this
   is what regenerates the *tracked* files
   (`.claude/skills/codecompass/SKILL.md`, `CLAUDE.md`,
   `.claude/commands/discovery.md` — confirmed live, §0, to be tracked,
   not gitignored) with Phase 76's own new, but scenario-independent,
   static content (the `query topology` command's own existence and the
   new table names — content that does not depend on any particular
   worktree/submodule *state*, only on the command existing at all).
   `git add -A && git commit -m "fixture: seed codecompass sync"` **in
   the seed clone itself** — one normalization commit, before either arm
   exists, not after either one is cloned.
2. **Clone the seed twice**, `baseline-clone` and `treatment-clone`, both
   `git clone --recurse-submodules <seed-path>` — **both necessarily
   start from the exact same commit**, because both are cloned from the
   same, already-normalized source after step 1 completed, not before
   it. This is what actually resolves the contradiction: there is no
   longer any step that mutates one arm's history after the point where
   the two arms' histories must match.
3. **Construct the identical intended scenario independently in each
   clone** — the same actions, run twice, once per clone, never
   committed to either (so this step cannot reintroduce a HEAD
   mismatch): checkout the same specific prior commit inside
   `adapters/haskell/` in both (Task A's divergence — a real, local,
   uncommitted-in-the-parent checkout change, exactly matching "someone
   ran `git submodule update --remote` locally without committing," the
   scenario Task A itself asks about); `git worktree add
   <path> -b codecompass-phase76-eval-feature` from the same starting
   branch in both (Task B's second worktree — deterministic, since both
   clones share the same HEAD to branch from); write the same edit to
   the same file in the new worktree in both (Task B's dirty state).
4. **Only now, in `treatment-clone` alone**, install CodeCompass and run
   `codecompass sync` a second time, in both of *its own* worktrees —
   this updates only `context-graph.db` (gitignored, confirmed live,
   §0) with the actual scenario's real topology facts; it does **not**
   re-touch `SKILL.md`/`CLAUDE.md`/`discovery.md` a second time, since
   their content is enrichment/vendor-count/static-command-list derived,
   not topology-data derived — confirmed by inspecting
   `skill.py::render_tool_skill`'s own new content (§9.2): it names the
   `query topology` command and the new table names unconditionally,
   never any specific worktree/submodule fact. `baseline-clone` never
   installs or runs CodeCompass at all.

**Mandatory pre-dispatch fixture-equivalence check, run by the lead,
after step 4, before either agent is dispatched** — independently
re-derive and compare ground truth for both clones, for every fact
either task tests, not assumed identical merely because both were built
from the same seed:

| Fact | How verified | Required outcome |
|---|---|---|
| Parent-pinned Haskell-adapter SHA | `git -C <clone> ls-tree HEAD -- adapters/haskell` | identical in both |
| Checked-out submodule SHA | `git -C <clone>/adapters/haskell rev-parse HEAD` | identical in both (identically diverged from the pin, per step 3 — never divergent in one clone only) |
| Intended pin/checkout match-or-mismatch state | derived from the two rows above | identical in both |
| Worktree count | `git -C <clone> worktree list` | identical in both (two: main + the `codecompass-phase76-eval-feature` worktree) |
| Worktree branches/HEADs | `git -C <clone> worktree list --porcelain`, both worktrees | identical in both |
| Intended dirty/clean state | `git -C <clone> status --porcelain`, both worktrees | identical in both — confirms step 4's treatment-only second sync did not reintroduce any tracked-file dirtiness the equivalence check would otherwise need to catch |
| Main-clone HEAD (the seed commit itself) | `git -C <clone> rev-parse HEAD` (main worktree only) | identical in both — the literal check that the previous design's contradiction made impossible to satisfy |
| Current-vs-sibling layout | which path each dispatched agent is told to start in | identical in both (same relative layout, same worktree named as "current" in the task prompt) |

**Persisted as evaluation evidence** — written to
`planning/reference-projects/codecompass-self/phase-76-fixture-equivalence.md`
(new directory, mirroring `planning/reference-projects/ledgerkit/`'s own
naming convention for a self-hosted evaluation rather than an external
reference project) before either agent is dispatched, not reconstructed
after the fact. If the check finds a genuine discrepancy, the fixtures
are fixed and the check re-run before dispatch — dispatching on a known
inequivalence is not an option this amendment leaves open.

**One disclosed, accepted limitation, not engineered around further**:
because both clones share the seed's own committed `SKILL.md` (which
names `codecompass query topology` as a real command, per step 1),
`baseline-clone`'s dispatched agent could in principle *read* that
static description without ever being able to *run* the command (no
`codecompass` binary installed/available in that environment) — this
gives it, at most, prose knowledge of the command's shape, never the
actual scenario data (real worktree/submodule state) the task asks
about, so it is not treated as invalidating the comparison. Stripping
`SKILL.md` differently between the two clones was considered and
rejected, since it would reintroduce exactly the "identical repository
state" violation this correction exists to remove.

**Two fresh, independent `general-purpose` agents** (neither the
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
discipline), **independently verified equivalent before dispatch** (the
fixture-equivalence check above — so any observed baseline/treatment
difference can be attributed to context availability, not to the two
agents starting from materially different repository states), the
comparison itself is genuinely independent (neither dispatched agent is
the lead, neither sees the other's work), and `context-evaluator`
provides the third-party verification the review specifically asked for.

**Explicit, unforced follow-up, not part of this phase's own DoD**: the
next external Priority-A Ledgerkit validation trial (recommended at
Phase 75's own closeout, still unclaimed by a phase number) should
separately consider a task where Git topology awareness might matter —
only if Ledgerkit's own real state ever presents one; none does today.

## 16. Explicit non-goals and deferrals

Restated from the original plan, with two additions from the first
amendment and three further additions from the second (all marked
**new**):

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
- **New (second amendment): bare-repository support as the current
  checkout.** §6/§12.11 declare this out of scope explicitly, detected
  honestly (`UNAVAILABLE`, specific reason), rather than built as a
  `--show-toplevel`-independent detection path — no evidence from this
  project's own real use (a project/source context tool, always
  operated against a real checkout) calls for it; `is_bare` remains
  meaningful for describing a sibling worktree, not removed from the
  schema.
- **New (second amendment): explicit, dedicated `git --version`
  detection/parsing as its own mechanism.** §5/§12.10's existing
  stderr-based `UNAVAILABLE` classification already produces an honest,
  correctly-attributed outcome for a Git too old to support
  `--git-common-dir` — a second, parallel version-checking mechanism
  solely to pre-empt the same outcome earlier is unnecessary complexity
  with no evidence it improves on the existing diagnostic.
- **New (second amendment): a general-purpose secret/token detector for
  arbitrary URL shapes beyond what `urllib.parse` can structurally
  decompose into scheme/userinfo/host.** The sanitizer's own invariant
  (§8/§12.7) is explicitly scoped to *parseable URI-form* remotes; a
  broader heuristic (e.g. regex-scanning an SCP-like string for
  anything password-shaped) is a different, weaker-grounded, and
  potentially false-positive-prone mechanism this phase's own evidence
  (no real instance of a credential-bearing SCP-like URL encountered
  anywhere in this project) does not call for.

## 17. Human decision gates

**None identified — re-confirmed for this second amendment too.** Every
design choice, old and new (the URL-sanitization scheme boundary now
including the ssh-password case, the path-safety check's exact
mechanism, the two-level uncertainty model, the migration introspection
predicate, the Git-2.5 version floor, the bare-repository non-support
decision, the "not yet indexed" absent-key representation, the
fixture-equivalence check's own required fact list) was resolved by
direct precedent already in this codebase, by live verification
performed during planning (§0), or by ordinary engineering judgement
with a stated, reversible rationale disclosed in the relevant section
above. If implementation surfaces a genuine ambiguity neither amendment
anticipated, work pauses and the lead asks before proceeding, per
`CLAUDE.md` §1 — none is manufactured here to be safe.

## 18. Unit / integration / real-repository tests

**`tests/test_git_topology.py`, new** — every test builds its own
disposable `git init`-ed fixture under `tmp_path`:

- Not a Git repository → `status=NOT_GIT`.
- `git` binary missing (monkeypatch `shutil.which`) → `status=UNAVAILABLE`,
  reason populated.
- A `rev-parse` failure with non-"not a git repository",
  non-"must be run in a work tree" stderr (simulated) →
  `status=UNAVAILABLE`, not `NOT_GIT`.
- **New (second amendment)**: a `rev-parse` failure with stderr
  containing an unrecognized-option message for `--git-common-dir`
  (simulated, standing in for a pre-2.5 Git) → `status=UNAVAILABLE`,
  reason surfaces the raw message, never misclassified as `NOT_GIT`
  (§5/§12.10's version-tolerance regression test).
- **New (second amendment)**: a real, disposable `git init --bare`
  fixture → `status=UNAVAILABLE`, reason mentions "no working tree
  (bare repository)"; independently cross-checked via a real
  `git rev-parse --is-bare-repository` call against the same fixture
  returning `true`; no `git_worktrees`/`git_submodules` rows produced
  for it at all (§6/§12.11).
- Single-worktree, clean repo → `status=DETECTED`; one `git_repositories`
  row, one `git_worktrees` row (`is_current=True`, `is_dirty=False`,
  correct `branch`/`head_commit`), zero `git_submodules` rows.
- **New**: `detect_git_topology` invoked from the fixture's own root,
  and separately from a real nested subdirectory of the same fixture —
  both calls identify the **same** `worktree_root` and `common_dir`,
  confirming the relative `--git-common-dir` output from the
  subdirectory case resolves correctly with no `--path-format` flag
  involved (§5's core regression test, doubling as the version-tolerance
  test — there is only one resolution code path, exercised identically
  either way).
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
- **New, expanded (second amendment)**: `sanitize_git_url` — all eight
  cases verified live during planning (§0/§12.7), now as permanent
  regression tests: `https://user:password@host/repo.git` (strip all
  userinfo); `https://TOKEN@host/repo.git` (strip all userinfo,
  bare-token-as-username); `ssh://user:password@host/repo.git` (strip
  password only, keep `user@` — the exact case the previous sanitizer
  missed); `ssh://git@host/repo.git` (no password, fully unchanged);
  `git@host:org/repo.git` (SCP-like, no parseable userinfo, fully
  unchanged); a plain credential-free `https://host/repo.git`
  (unchanged, idempotent); an HTTPS URL with an explicit port (port
  preserved after stripping); this repository's own real
  `adapters/haskell`/`codecompass-adaptor-protocol` submodule URLs
  (fully unchanged).

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

- **New (second amendment)**: `codecompass query topology` against a
  freshly-`init_schema`'d database (via `open_graph`, never synced) —
  no `meta.git_topology_status` key at all — prints "Git topology has
  not been indexed yet; run `codecompass sync`.", exit code 0; `--json`
  → exactly `{"indexed": false}`, no other top-level keys. A second
  variant simulates the specific "upgraded old database" case named by
  the requirement (a hand-built v9-shaped fixture per §11's own
  migration tests, opened under Phase 76 code, never synced) —
  identical outcome, confirming the two scenarios (brand-new vs.
  upgraded-but-unsynced) are correctly treated the same way. Confirmed,
  via a subprocess/monkeypatch spy, that **no `git` command is invoked**
  by `query topology` in either variant — the read-only-with-respect-to-
  live-detection requirement, tested directly, not merely asserted.
- `codecompass query topology` against a real synced fixture prints the
  expected structure for each of the four `TopologyStatus` values
  (constructed via fixtures/monkeypatching for `not_git`/`unavailable`/
  `partial`, real for `detected`); `--json` round-trips through
  `json.loads`; a `partial` result's structure is still shown alongside
  its banner, never suppressed.

**Real-repository validation** — §13 (submodules: real repo + divergence,
path-safety, and two-credential-URL-scheme disposable-clone scenarios,
plus a disposable bare-repository fixture; worktrees: the corrected,
sync-then-query ordering, including the "not yet indexed"
demonstration before the disposable worktree's own first sync).
**Task-context evaluation** — §15 (baseline/treatment/`context-evaluator`,
gated on the pre-dispatch fixture-equivalence check passing).

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

# New (second amendment): "not yet indexed" before this worktree's own first sync
(cd /tmp/codecompass-phase76-worktree-test && codecompass query topology)
(cd /tmp/codecompass-phase76-worktree-test && codecompass query topology --json)
# Expected: "Git topology has not been indexed yet; run `codecompass sync`.";
# --json => {"indexed": false}. No git_topology_status meta key exists yet
# (no context-graph.db exists yet in this brand-new worktree at all).

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

# New (second amendment): bare-repository handling (disposable, never this repository)
git init --bare /tmp/codecompass-phase76-bare-test
(cd /tmp/codecompass-phase76-bare-test && codecompass sync --yes --budget 0 2>&1 | tail -5)
(cd /tmp/codecompass-phase76-bare-test && codecompass query topology)
# Expected: sync completes without crashing (topology detection degrades
# gracefully; nothing else about sync depends on it); query topology
# reports status=unavailable, reason mentioning "no working tree (bare
# repository)".
rm -rf /tmp/codecompass-phase76-bare-test
```

## 20. Definition of Done

Per `CLAUDE.md` §5, unchanged process; amended to include both
amendments' own new requirements (items marked **new**; items marked
**new, 2nd** are specific to this second amendment):

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
7. **New, revised 2nd**: the URL sanitizer genuinely strips every
   password/token component from a parseable `http(s)` **or `ssh`/other
   URI-form** remote, genuinely preserves a bare, non-secret username on
   a non-`http(s)` form, and genuinely leaves SCP-like forms (including
   this repository's own real submodule URLs) fully unchanged — all
   eight cases (§18), not the previous four-case, `http(s)`-only
   guarantee.
8. **New, 2nd**: Git-topology detection genuinely depends on no Git
   feature newer than 2.5 (`--path-format=absolute` fully removed, §5/
   §12.10) — confirmed by the nested-directory test exercising the one,
   only, manual-resolution code path, and by the simulated-old-Git test
   producing an honest `UNAVAILABLE`, never a crash or a `NOT_GIT`
   misclassification (§18).
9. **New, 2nd**: the "topology not yet indexed" state (§4/§6/§9) is
   genuinely distinguishable, in both CLI text and `--json` output, from
   all four `TopologyStatus` outcomes — confirmed against both a
   brand-new and an upgraded-but-unsynced database (§18) — and `query
   topology` is confirmed, via a spy, to invoke no `git` command on
   either path.
10. **New, 2nd**: the bare-repository contradiction is genuinely
    resolved — `UNAVAILABLE` with the specific "no working tree"
    reason, confirmed against a real disposable bare-repository fixture
    (§18), no crash, no fabricated `git_worktrees` row for a self that
    was never inspected.
11. §18's full test suite passes, including the corrected real-repository
    worktree validation sequence, the "not yet indexed" demonstration,
    the bare-repository fixture, and all disposable submodule fixtures
    (divergence, path-safety, both credential-URL schemes).
12. `docs/`, `architecture/`, `decisions/` updated per §14, same commit
    as the code, including the now-explicit Git ≥2.5 minimum and the
    bare-repository non-support decision.
13. **New, revised 2nd**: §15's amended, independent baseline/treatment/
    `context-evaluator` task-context evaluation performed and recorded
    honestly (not the lead-self-comparison-only version) — **gated on
    the pre-dispatch fixture-equivalence check (§15) having actually run
    and passed, with its own evidence persisted at
    `planning/reference-projects/codecompass-self/phase-76-fixture-equivalence.md`
    before either agent was dispatched** — including if the task-context
    answer turns out to be "less advantage than hoped."
14. An independent `docs-reconstructor` per-phase drift audit finds no
    current-truth doc left misdescribing the system.
15. `CHANGELOG.md` entry added, same commit.
16. `planning/CONTEXT.md` reflects the new state.
17. A phase retro exists at
    `planning/retros/phase-76-git-repository-topology.md`, including
    §15's findings and the fixture-equivalence evidence.
18. Candidate learnings from the phase (if any) triaged by
    `knowledge-curator` — **the migration-safety finding in §11 is a
    strong candidate for its own learning entry**, distinct from this
    phase's own feature work, since it documents a real, pre-existing,
    twice-already-occurred defect class this phase's own review
    happened to surface; **the ssh-password sanitizer gap and the
    bare-repository contradiction (both this second amendment's own
    findings) are candidates too**, since both were real, shippable
    defects in an already-once-reviewed plan, worth a process learning
    about how many review passes a security-adjacent design choice
    actually needs.
19. An independent `release-phase-auditor` pass verifies every
    preceding condition against the exact commit about to be marked
    done, persisting `planning/retros/_audit-phase-76.md` — any
    post-audit commit touching audited scope voids that pass.
20. Disposable test worktrees/branches, scratch submodule-divergence/
    path-safety/credential-URL fixtures, and the disposable
    bare-repository fixture are fully cleaned up — no leftover trace on
    the real repository.
21. Only once every one of the above genuinely holds does a genuinely-
    dispatched `roadmap-context-curator` (never the lead self-serving
    it) perform final reconciliation and flip
    `planning/ROADMAP.md`'s Phase 76 row to `done`.

**Not done merely because Git metadata can be parsed** — it must be
correctly represented at both levels of uncertainty, including the "not
yet indexed" state (§4/§6/§8/§9), safe against a hostile or malformed
`.gitmodules` (§12.6), genuinely free of credential leakage across every
URI form CodeCompass can parse, not merely the `http(s)` subset (§12.7),
correct regardless of invocation directory and regardless of the host's
Git version down to a genuinely necessary, honestly-disclosed floor
(§5), honest about a repository with no working tree rather than
crashing or fabricating support for it (§6/§12.11), safe to open against
an existing production database (§11), reachable through `codecompass
query topology` and the generated Skill, and shown (§15), via genuinely
independent assessment against **verified-equivalent fixtures**, to
help at least one realistic task.

---

## Preserved from the original plan, unchanged by either amendment

Restated explicitly, per the user's own instruction on both amendments,
so nothing on this list is mistaken for having been reopened:

- Separate Git topology tables rather than reusing `vendors` (§4).
- Worktree identity kept distinct from repository identity (§4).
- Invocation root, worktree root, and Git common dir kept as three
  separate concepts (§5) — sharpened, not reopened, by the second
  amendment's own version-tolerant resolution of the latter two.
- Mechanical Git facts kept separate from semantic project relationships
  (§8).
- Parent-pinned submodule revision kept distinct from child checked-out
  revision (§4/§7).
- Unresolved-but-declared submodules remain represented, never silently
  omitted (§4/§7/§8).
- The explicit `detected`/`not_git`/`unavailable`/`partial` status
  model, **once topology has actually been indexed** (§6) — the second
  amendment adds a fifth, query-layer-only "not yet indexed" state for
  *before* that point (§4/§9), it does not touch the four-value model
  itself.
- Per-worktree `context-graph.db` isolation (§10).
- Topology queries read persisted sync state, never live Git state —
  reinforced, not merely repeated, by the second amendment's own
  explicit "`query topology` invokes no `git` command, on any path,
  including the 'not yet indexed' one" requirement (§9/§18/§20).
- Sibling worktree dirty state remains "not probed" (§4/§7/§8) — no
  evidence gathered in either amendment justifies changing this.
- One-level submodule scope (§7.6/§16).
- No recursive child-repository/submodule graph indexing (§4/§16).
- No generic multi-repository federation (§16).
- No semantic cross-repository symbol graph (§16).
- No worktree/branch lifecycle management — read-only observation only
  (§16).
- No Phase 24 implementation or redefinition (§2).
- Path-traversal protection for `.gitmodules`-declared paths (§12.6) —
  unchanged by the second amendment, which only added the bare-repository
  and version-floor fixes elsewhere.
- Independent baseline/treatment/`context-evaluator` assessment (§15) —
  strengthened, not reopened, by the second amendment's own added
  pre-dispatch fixture-equivalence check.
- Real CodeCompass protocol/Haskell submodules used as dogfood fixtures
  (§0/§13).
- Disposable worktree and scratch-clone validation, with mandatory
  cleanup (§13/§20) — extended, not reopened, to also cover the new
  bare-repository and dual-credential-scheme fixtures.
- Introspection-based migration safety (§11) — unchanged by the second
  amendment.
- The documentation/ADR/retro/drift-audit/release-audit/
  roadmap-context-curator closeout discipline established after the
  `L-060`/`L-061` fixes (§12/§20).
