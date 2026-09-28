# 0063. Git repository topology (worktrees, submodules) is a new, separate graph-capability addition — mechanical facts only, per-worktree database isolation, no schema-version-diff migration triggering

## Status

Accepted (2026-09-28).

## Context

Phase 76 (direct user request, `planning/phase-76-git-repository-topology.md`)
adds mechanical Git worktree and submodule awareness so a fresh agent can
tell "different checkout of the same repository" apart from "different
repository" and "parent-pinned commit" apart from "actually checked-out
commit." This project's own real repository is the genuine, non-synthetic
proving fixture: two real Git submodules
(`protocol/codecompass-adaptor-protocol`, `adapters/haskell`,
`decisions/0058`), mounted specifically because they are separately
licensed, separately versioned repositories — `decisions/0058`'s own
"Consequences" section already names the real bookkeeping need this
phase addresses ("a version-compatibility matrix... must be documented
and kept current"), today entirely manual.

Several genuinely non-obvious design questions came up during planning
and two rounds of direct review, recorded here rather than left as
implicit code-level choices.

## Decision

**1. Three new tables (`git_repositories`, `git_worktrees`,
`git_submodules`), not a widened `vendors` or `doc_artifacts`.** A
submodule has no `Ecosystem`, no `vendor.toml` entry, and is a
Git-level construct independent of any package manager
(`docs/domain/concepts/vendor.md`'s own narrow definition of `VendorConfig`
confirms this); a worktree/submodule is neither a document nor
addressable by `doc_artifacts`'s word-boundary mention matchers. Rejected
both.

**2. Mechanical facts only — no semantic relationship edges.** A
`git_submodules` row never asserts, e.g., that `codecompass-adaptor-haskell`
*implements* `codecompass-adaptor-protocol` — that would need independent
evidence and its own relation kind, the same posture `CG-007`'s own
precedent already establishes for keeping mechanical and semantic
relationships separate. Parent-pinned revision (`pinned_commit`, read
from the parent's own tree via `git ls-tree`) is kept structurally
distinct from the child's actual checked-out revision
(`checked_out_commit`) — never conflated, never derived from
`git submodule status`'s own single, `--cached`-dependent SHA column.

**3. `pinned_commit` is nullable; a declared-but-unresolved submodule is
never silently omitted.** A `.gitmodules` entry with no corresponding
gitlink in `HEAD`'s tree yet (a real, mid-edit state) still produces a
row — `path` and `is_path_safe` are the only fields guaranteed
non-null. This is a direct application of this project's own "honest
gaps over fabricated certainty" discipline
(`planning/ledgerkit-stage-c-learnings.md`) to a case a naive `NOT NULL`
constraint would otherwise have forced into silent deletion.

**4. Two levels of uncertainty, never conflated**: a whole-pass
`git_topology.TopologyStatus` (`detected`/`not_git`/`unavailable`/
`partial`, persisted to `meta.git_topology_status`/`git_topology_reason`)
answers "could the structure be enumerated at all"; per-row nullable
columns answer "for a structure that was enumerated, which specific
facts remain unknown." `unavailable` covers both a missing `git` binary
and a bare repository as the current checkout (§7 below) — pattern-matched
from `git`'s own distinctive stderr text, never conflated with `not_git`.
A fifth, "topology not yet indexed" state (an existing database opened
under this phase's code but never re-synced) is represented by the
*absence* of `meta.git_topology_status` entirely — deliberately not a
fifth enum member, since `TopologyStatus` is `detect_git_topology`'s own
return type and detection, by construction, only ever runs while a sync
is actually happening; the query layer (`cli.py::query_topology`) checks
for the key's absence before ever reading its value, and never invokes
`git` itself on any path, including this one.

**5. `git_topology.py` is a separate, graph-agnostic detection module.**
Mirrors `discovery.py`/`usage.py`/`spec_docs.py`'s own shape exactly;
`sync.py::rebuild_project_graph` is the only place its plain dataclasses
are converted into `graph.py` row types, the same pattern
`usage.DetectedImport → graph.UsesEdgeRow` already establishes. No new
architectural pattern introduced.

**6. `_migrate_doc_artifacts_constraints`'s schema-version-diff trigger
is replaced with direct introspection — a real, pre-existing defect this
phase's own schema bump would otherwise have reproduced a third time.**
`git log` confirms `_SCHEMA_VERSION` has already been bumped twice for
changes touching neither `doc_artifacts` nor `documents_edges`/
`doc_relations_edges` at all (Phase 60's `vendors.ecosystem` widening,
Phase 62's `symbols.export_kind`/`note` addition) — yet
`_migrate_doc_artifacts_constraints` fired, unconditionally dropping and
recreating all three tables, on *any* `meta.schema_version` mismatch,
regardless of relevance. Since `open_graph` runs on every `query`
invocation, not only `sync`, this meant a user upgrading CodeCompass and
running a read-only `query` command *before* their next `sync` would
have silently lost their previously-synced `doc_artifacts`/relations
content, for a reason unrelated to anything actually changing about that
data's own shape. The fix (`_doc_artifacts_schema_is_current`, direct
`sqlite_master`/`PRAGMA table_info` introspection) generalizes a pattern
this file's own other four migrations already independently converged on
— `_migrate_doc_artifacts_constraints` was simply the one never brought
into line with that precedent until now. `meta.schema_version` itself
becomes purely informational bookkeeping, updated unconditionally by
`open_graph` on every open, read by no migration's own trigger condition
any more.

**7. Bare repositories are out of scope, declared honestly rather than
specially supported.** `git rev-parse --show-toplevel` genuinely cannot
succeed against a bare repository (confirmed live, a distinctive,
`not-a-git-repository`-unrelated stderr message) — building a
`--show-toplevel`-independent detection path for a scenario this
project's own purpose (a project/source context tool, always operated
against a real checkout) gives no evidence it needs was rejected as
unnecessary special-case complexity. Result: `unavailable`, with an
explicit "no working tree (bare repository)" reason — never a crash,
never a fabricated `git_worktrees` row for a self that was never
inspected. `is_bare` remains a real, meaningful column for describing a
*sibling* worktree (a bare "hub" repository with linked, non-bare
worktrees is a real, representable topology on the sibling side).

**8. No Git feature newer than `git worktree`/`--git-common-dir`
themselves (Git 2.5, July 2015) is ever required.** An earlier design
used `--path-format=absolute` (Git 2.31, 2021) purely for the convenience
of skipping a manual path-join — an undisclosed minimum-Git-version
requirement this project has never required anywhere else, and unrelated
to the Python-version floor (`requires-python = ">=3.11"`) the two are
sometimes conflated with. Removed entirely: `--show-toplevel`'s own
output is always already absolute on any Git version that has ever
supported it; `--git-common-dir`'s relative output (when the invocation
directory differs from the worktree root) is resolved manually against
the known directory — ordinary, deterministic path-joining against a
location Git itself just named, not filesystem guessing. The resulting
Git 2.5 floor is genuinely unavoidable (worktree awareness has no
meaning at all on an older Git), not a convenience choice, and is now
the first explicitly documented Git version requirement anywhere in this
project.

**9. Credential sanitisation is scheme-aware, not scheme-blind.** Every
Git remote URL (`origin_url`, `child_repository_url`) is sanitised before
it ever reaches a dataclass, the graph, or any output surface. For
`http`/`https`, the entire userinfo component is stripped (a bare
username used as a token is a common, real credential-leak pattern for
these schemes). For any other recognized URI scheme (`ssh`, `git`, ...),
only an actual password component is stripped — a bare username is
ordinary, non-secret connection identity (`ssh://git@host/...`) and is
preserved. SCP-like syntax (`git@host:org/repo.git`) has no parseable
userinfo at all under `urllib.parse.urlsplit` and is left completely
untouched — not assumed safe, but genuinely unparseable into a
username/password pair to strip. The guarantee this exists to provide:
CodeCompass never persists or prints a password/token component of a
*parseable* Git remote URL — deliberately narrower than an unbounded
"no credentials ever," which an earlier, `http(s)`-only version of this
sanitiser had implicitly (and, for an `ssh://user:password@host/...`
form, incorrectly) claimed.

**10. `.gitmodules`-declared paths are resolved and verified against the
worktree root before any command ever runs against them.** A path that
resolves outside the worktree root (`Path.is_relative_to`, after
`.resolve()` — catching both textual `../` traversal and a symlink
escape) is refused: the row still records that the path was declared,
but `is_path_safe=False` and no `git`/filesystem command is ever invoked
against the escaping location. `.gitmodules` content is not trusted as a
safe filesystem-traversal target merely because Git itself would follow
it during a real `git submodule` operation.

**11. Per-worktree `context-graph.db` isolation is kept — recognition,
not consolidation.** Each worktree of a repository keeps its own,
separate database file, exactly as before this phase. A worktree can
genuinely hold different file content (different branch, different
dirty state) at any moment, so per-worktree isolation is already correct
behaviour for the vendor/symbol/doc content those files describe, not an
accidental duplication. What this phase adds is recognition: each
worktree's own database records the shared `common_dir` identity plus
its own worktree row (`is_current=1`) and whatever sibling worktrees
`git worktree list` reported *as of this worktree's own last sync* — the
same staleness contract every other graph fact already carries
(`decisions/0025`). A fully consolidated, one-database-per-repository
design was considered and rejected as unnecessary for this phase's
minimum capability; it would require relocating `open_graph`'s own db
path to the common directory, a change touching every call site that
currently does `project_root / _GRAPH_DB_FILENAME` directly, for a
benefit (deduplicating identical content across worktrees) no evidence
yet calls for.

## Alternatives considered

- **Recursively materialising a submodule's own directory as a nested
  `context-graph.db`/`git_repositories` row.** Rejected — a
  `git_submodules` row is a topology *relationship* fact about the
  parent repository being inspected, never a recursively materialized
  child repository graph of its own. If a submodule's own directory is
  later inspected directly, that produces its own, entirely separate
  `git_repositories` row in its own database; the two are never linked
  by this phase.
- **A structured, multi-cause diagnostic model for `unavailable`/
  `partial` beyond a single reason string.** Rejected — no evidence from
  this phase's own real-repository validation or task-context evaluation
  suggests a plain, first-failure string is insufficient for the tasks
  this capability targets.
- **A general-purpose secret/token detector for URL shapes beyond what
  `urllib.parse` can structurally decompose.** Rejected — the sanitiser's
  own invariant is explicitly scoped to parseable URI-form remotes; a
  broader heuristic (e.g. regex-scanning an SCP-like string) is a
  different, weaker-grounded, more false-positive-prone mechanism with
  no real instance in this project calling for it.
- **A dedicated, separate `git --version` detection/parsing step**, to
  pre-empt an old-Git failure ahead of the ordinary stderr-based
  classification. Rejected — the existing classification already
  produces an honest, correctly-attributed `unavailable` outcome for a
  Git too old to support `--git-common-dir`; a second, parallel
  version-checking mechanism for the same eventuality is unnecessary
  complexity.

## Consequences

- Schema version `9` → `10`; three new tables, two new `meta` keys, no
  change to any existing table's columns or constraints.
- `_migrate_doc_artifacts_constraints` is meaningfully safer for every
  future schema change, not only this one — an unrelated future bump
  can no longer accidentally trigger a `doc_artifacts`/`documents_edges`/
  `doc_relations_edges` reconstruction.
- `codecompass query topology [--json]` is a new, permanent CLI surface;
  `.claude/skills/codecompass/SKILL.md`'s generated content names it
  unconditionally, regardless of any project's own actual topology (the
  same "present unconditionally" posture `decisions/0020` already
  established for the tool Skill overall).
- Git 2.5 is now this project's first explicitly documented minimum Git
  version requirement, disclosed in `docs/cli-reference.md` and
  `architecture/overview.md` — narrower in scope than it might first
  appear, since it gates only the worktree/submodule-awareness half of
  CodeCompass, never `sync`/`query` as a whole.
- No change to `vendor.toml`'s schema, `VendorConfig`, or any existing
  `query` subcommand's own missing-database behaviour —
  `query topology`'s narrow `_open_graph_for_topology` resolution
  function is deliberately not a change to the shared
  `_open_graph_or_note`/`_graph_session` helpers every other subcommand
  still uses unmodified.
