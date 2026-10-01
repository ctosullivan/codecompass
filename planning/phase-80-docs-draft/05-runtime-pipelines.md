# Architecture: runtime pipelines

**Provenance tier: CONFIRMED-BY-READING ONLY — this entire file is lower
confidence than `04-architecture-persistence.md`.** Source:
`phase80-implementation-reconstruction.md` §0, §6. `cli.py` and
`sync.py` could not be executed in the Stage 2 sandbox: they import
sibling modules not present in that bounded export
(`enrichment`, `relation_enrichment`, `chat`, `index`, `skill`,
`source_resolution`, `staleness`, `filetree`, `symbols`, `git_topology`,
`skill_scan`, `source_symbols`, `spec_docs`, `usage`, `claude_md`,
`deptree`, `doc_mapping`, and the npm/cargo/haskell adapters), so
`codecompass --help` and `import codecompass.cli` both fail with
`ImportError` in that environment. Everything in this file was traced by
reading the present code's own call chains and the missing modules'
call-site contracts — it was never executed end-to-end. Treat it as a
careful read, not a verification.

## `codecompass sync` (whole-project)

Call chain, as read directly from `cli.py`:

```
cli.py::sync
  -> _load_config()
  -> sync_all(configs, cwd)           # loops sync_vendor per config
  -> rebuild_project_graph(configs, cwd)   # whole-project sync only
  -> _maybe_run_enrichment(...)
  -> _refresh_generated_artifacts(...)
```

This chain exists exactly as described above, confirmed by reading
`cli.py` directly — but it could not be executed end-to-end, since
`_maybe_run_enrichment`, `index`, `skill`, and
`commands.write_discovery_command` are only partially present (only the
last is actually in the bounded evidence base).

## `sync_vendor` (one vendor)

Read-only trace, not run:

1. Construct the adapter via `get_adapter`.
2. Read `installed_version`, `readme_and_api_surface`,
   `dependency_tree`, `source_location` from it.
3. Create `vendor/<name>/`.
4. Clone the vendor's upstream source (out of scope: this calls
   `resolve_and_clone`, not in this evidence base), falling back to a
   local-install copy on failure and recording a `description_error`.
   This is explicitly a **clone** failure, not a description failure —
   there is no AI call inside `sync_vendor` itself at all; its own
   docstring and code confirm no AI-call code path exists here.
5. Read-only-look up this vendor's existing `vendor_enrichment` row from
   the graph, if `context-graph.db` exists, to populate the digest's
   description fields.
6. Render `DEPTREE.md`/`deptree.json`/`FILETREE.md`/`filetree.json`/
   `CLAUDE.md` (plus `OVERVIEW.md` if an enrichment exists) —
   unconditionally, fully overwriting every file every call.
   Deterministic, no diffing.

## `rebuild_project_graph` (whole project)

Read-only trace, not run. For every configured vendor:

- Builds a vendor row plus that vendor's symbol rows via
  `adapter.symbols()`.
- Calls `usage.resolve_project_usage` (out of scope) to produce
  "uses" edges, resolving detected symbol names only against each
  vendor's own already-collected symbol-name set — falling back to a
  vendor-level edge with no specific symbol when a name can't be
  resolved that way.
- Calls source-file discovery/extraction functions (out of scope) over
  every recognized first-party file, regardless of what's in
  `vendor.toml`.
- Collects doc-artifact rows from four independent, out-of-scope
  sources (vendor doc mapping, vendor upstream doc mapping, skill
  scanning, spec-doc scanning), and derives chunk/edge rows from those.
- Calls git-topology detection (out of scope).
- Calls `graph.rebuild_deterministic` exactly once, with everything
  collected above.

A documented, accepted inefficiency, confirmed by reading: the
source-file walk for symbols and the vendor-usage walk each
independently traverse the project tree once, rather than being merged
into a single pass.

## `query` / `enrich` / `undo` / `check` commands

These are fully self-contained inside `cli.py` plus `graph.py`. They were
traced completely by reading, and — for the `graph.py` half of each —
confirmed by running the matching tests (see
`04-architecture-persistence.md`). The CLI-surface half of each command
(flags, output shape) is only CONFIRMED-BY-READING; see
`02-cli-reference.md`.

## What this file deliberately does not claim

This file does not describe the actual internal behavior of
`enrichment.py`, `relation_enrichment.py`, `chat.py`, `index.py`,
`skill.py`, `source_resolution.py`, `staleness.py`, `filetree.py`,
`symbols.py`, `git_topology.py`, `skill_scan.py`, `source_symbols.py`,
`spec_docs.py`, `usage.py`, `claude_md.py`, `deptree.py`, or
`doc_mapping.py`. Every reference to one of these above says only what
the *calling* code expects of it (a function name, an argument shape, a
return-type expectation inferred from how the result is used) — never
what it actually does internally. See
`08-limitations-and-provenance.md` for the full list of inferred call
contracts.
