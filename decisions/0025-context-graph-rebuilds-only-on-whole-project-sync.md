# 0025. Context graph rebuilds only on whole-project `sync`, never incrementally

## Status

Accepted

## Context

Every existing generated artifact in this project goes stale on exactly
one axis: the tracked vendor's version or upstream content changes, and
the fix is re-running `sync` (or `check --fix`). The context graph
(`decisions/0024`) introduces a second, independent staleness axis: its
`uses` edges (`SourceFile → Vendor`/`Symbol`, `planning/
phase-9a-vendor-presence-graph.md`, `phase-9b-symbol-usage-graph.md`)
depend on the *consuming project's own source*, which can change far more
often than any vendor's version, and with no relationship to `sync`
being run at all.

Separately, 9b's extraction (an `ast`/regex walk over the whole project
source tree, `src/depcompass/usage.py`) is the one step in this design
with a real, non-zero cost — still no AI calls, but the first
project-source-wide walk anything in this pipeline does (every existing
walk, e.g. `filetree.py`'s `_iter_files`, is scoped to one vendor's
source snapshot, not the consumer's whole project).

## Decision

`build_context_graph()` runs, and `context-graph.json` is (fully)
overwritten, only by two entry points: bare `depcompass sync` (no vendor
argument) and bare `depcompass` (zero-question bootstrap, which calls the
same whole-project path, `decisions/0017`). `sync <vendor>`, `promote
<vendor>`, and `check --fix`'s internal per-vendor resync loop do **not**
touch the context graph at all — even though they resync one vendor's own
digest files, the project-wide graph is left exactly as it was after the
last whole-project sync.

Both staleness axes — project-source changes and vendor-sync changes —
collapse onto this single trigger point. Neither is tracked separately,
and there is no mtime- or hash-based incremental recomputation in this
plan: every rebuild is a full rebuild, matching the "deterministic,
always fully recompute, no incremental diffing" posture already
established by `sync_vendor` (which fully overwrites `vendor/<name>/`
every call) and `filetree.py`'s unconditional `root.rglob("*")` walk.

## Alternatives considered

- **mtime/hash-based incremental recompute**, rebuilding only for
  changed files. Rejected for v1 — no existing precedent for incremental
  diffing exists anywhere in this pipeline, and introducing one here
  would be a new caching mechanism (with its own invalidation-bug
  surface) justified only by a performance problem nobody has measured
  yet at real project scale. Revisit if profiling a real large project
  shows the full-walk cost is actually a problem.
- **Rebuild on every command that reads the graph** (e.g. every
  `depcompass check` invocation, or lazily inside a future `chat`
  session-start). Rejected — `check` is meant to be a cheap, frequently
  run command (its bare form always exits 0 and is meant for casual
  status checks); making it carry an O(project-size) walk on every
  invocation would change its cost profile. `chat.py` doesn't consume
  this graph at all in this plan, so there is no session-start hook to
  attach to yet regardless.
- **Rebuild on every `sync` call, including `sync <vendor>`.** Rejected
  — `check --fix` resyncs each stale vendor independently in a loop;
  rebuilding the whole-project graph after every single vendor's resync
  would mean redundant full rebuilds proportional to the number of stale
  vendors, for a graph whose value is aggregate/coverage signal, not
  moment-to-moment per-vendor accuracy.

## Consequences

- A single-vendor `sync <name>` (or `promote <name>`, or a `check --fix`
  resync) leaves `context-graph.json` stale relative to that vendor's
  latest state until the next whole-project `sync` is run. This is an
  accepted, explicitly documented gap — not a silent inconsistency — and
  should be stated in user-facing docs wherever the graph's freshness
  matters (`docs/cli-reference.md`'s `sync` entry).
- `depcompass check` **reads** the persisted `context-graph.json`; it
  never rebuilds it. If the file doesn't exist (project never synced with
  graph support), `check`'s coverage-gap section is silently skipped
  with a one-line note pointing at `sync`.
- If a future phase's profiling shows the whole-project walk is too slow
  for very large consuming projects, that's a follow-up optimization
  decision, not implied or precluded by this one.
