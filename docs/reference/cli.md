# CLI reference

All commands are subcommands of the `codecompass` Typer application (`src/codecompass/cli.py`), except the bare command itself.

## `codecompass` (no subcommand)

```
codecompass [--yes] [--budget USD]
```

Zero-question deterministic bootstrap + auto-triggered, cost-gated AI enrichment. See `docs/getting-started.md` and `docs/workflows/sync-and-enrichment-pipeline.md`.

- `--yes` — skip Phase B's confirmation prompt.
- `--budget USD` — cap estimated Phase B spend; aborts before any API call if the estimate exceeds it. Omit for no cap.

## `codecompass init --scan <manifest>`

```
codecompass init --scan package.json [--scan pyproject.toml ...] [--output vendor.toml]
```

Explicit, scripted/CI-friendly bulk discovery from named manifests. `--scan` repeats for multiple files. **Errors if `vendor.toml` already exists** — unlike the bare command's idempotent-refresh behaviour, this never appends.

## `codecompass sync [vendor]`

```
codecompass sync [VENDOR] [--yes] [--budget USD]
```

- With a `VENDOR` argument: regenerates just that vendor's digest. Never rebuilds the graph, never triggers Phase B.
- With no argument: regenerates every vendor's digest, rebuilds `context-graph.db`, and (same as the bare command) auto-triggers cost-gated Phase B enrichment.

## `codecompass index`

```
codecompass index
```

Regenerates the root `CLAUDE.md` routing table and the tool-level Skill from already-persisted state. Cheap and side-effect-free by design — never triggers a sync.

## `codecompass check [--strict] [--fix]`

```
codecompass check [--strict] [--fix]
```

Compares each vendor's persisted digest version against a fresh live read, classifying the delta as `none`/`patch`/`minor`/`major`/`unknown` (`none`/`patch` never fail anything; `major`/`unknown` are the strict-fail cases). Also prints report-only context-graph coverage-gap sections (unused vendors, documented-but-unused symbols, used-but-undocumented symbols, orphaned third-party Skill mentions, spec/vendor docs with no detected relations) when `context-graph.db` exists.

- With no flags: always exits `0` — a human-facing report.
- `--strict`: exits non-zero if any vendor has major/unclassifiable drift, or a failed live-version read. Governed by version-drift severity **alone** — coverage gaps never affect this exit code. Never regenerates anything.
- `--fix`: regenerates every stale vendor's digest in place (same logic as `sync`).
- `--strict` and `--fix` are mutually exclusive.

## `codecompass query vendors`

```
codecompass query vendors [--unused] [--json]
```

Every tracked vendor's usage/enrichment status. `--unused` filters to vendors with zero detected usage anywhere.

## `codecompass query vendor <name>`

```
codecompass query vendor NAME [--json]
```

One vendor's full profile: symbols (with `export_kind`/`note` when not a plain confident export), usage count, documenting artifacts, routed Skills, `depends_on` vendors, and every usage site (file + line).

## `codecompass query symbol <name>`

```
codecompass query symbol NAME [--json]
```

Every symbol named `NAME` across *all* vendors (symbol names are not globally unique) — purpose, usage count, documenting artifacts, usage sites.

## `codecompass query skills`

```
codecompass query skills [--unused-mentions] [--json]
```

Every agent-context artifact in the project — Agent Skills, Cursor `.mdc` rules, the `/discovery` slash command — kind, origin, and what it mechanically mentions. `--unused-mentions` filters to artifacts mentioning no known vendor or source file.

## `codecompass query relations <name>`

```
codecompass query relations NAME [--json]
```

Given a spec-doc path: what it mechanically mentions. Given a vendor or Skill/doc-artifact name: which spec docs mechanically mention it. Shows an AI-enriched summary ("mentioned, not yet enriched" otherwise) and a "Package code" trace of real project-source usage sites.

If `NAME` is a real on-disk file that was simply never detected as a spec/vendor doc (outside `spec_docs.py`'s glob coverage), the error message says so explicitly rather than reporting a plain, misleading "not found."

## `codecompass query topology`

```
codecompass query topology [--json]
```

Persisted Git repository topology (worktrees, submodules) as of the last `sync` — **never invokes `git` itself**, purely reads `context-graph.db`. Distinguishes "never indexed" from "not a Git repository" from "detected" explicitly; a nullable fact (e.g. an unprobed sibling worktree's dirty state) renders as an honest "unknown"/"not probed," never a false `clean`.

## `codecompass query source <path>`

```
codecompass query source PATH [--json]
```

Every first-party fact known about one recognized source file: language, content hash, symbol-index status, its own top-level implementation symbols (with exposure classification), and any recorded vendor usage. Works independent of `vendor.toml` — no tracked vendor required. See `docs/reference/symbol-extraction.md`.

## `codecompass query source-symbol <name>`

```
codecompass query source-symbol NAME [--json]
```

Every first-party top-level implementation symbol named `NAME` across every recognized source file.

## `codecompass chat <vendor>`

```
codecompass chat VENDOR
```

A terminal REPL grounded entirely on `vendor/<vendor>/CLAUDE.md` (and `OVERVIEW.md` if enriched) — never regenerates or re-clones anything. Requires `ANTHROPIC_API_KEY`. Exit with `exit`, `quit`, or Ctrl-D.

## `codecompass undo`

```
codecompass undo [--yes] [--dry-run]
```

Best-effort cleanup of everything CodeCompass generated in the project: every tracked vendor's `vendor/<name>/` directory, `vendor.toml`, `context-graph.db`, every CodeCompass-generated Skill/`.mdc`/slash-command artifact, and the root `CLAUDE.md` routing-table marker block (stripped in place; hand-written surrounding content is preserved). Never removes a hand-written or third-party Skill/`.mdc` file, and never runs any `git` command. Not a transactional rollback — a best-effort filesystem cleanup; committing the result is left to you.

## `codecompass enrich apply <entries_file> --agent <name>`

```
codecompass enrich apply ENTRIES_FILE --agent AGENT_NAME
```

Writes agent-authored relationship enrichment. See `docs/workflows/sync-and-enrichment-pipeline.md`. `ENTRIES_FILE` is a JSON file: a list of `{source_doc_path, target_vendor_name?, target_doc_path?, ai_summary, relation_label}` objects.

## `codecompass knowledge ...`

```
codecompass knowledge render [SLUG]
codecompass knowledge select-candidates SLUG [--dry-run]
codecompass knowledge apply MANIFEST_PATH
codecompass knowledge status [SLUG] [--strict]
codecompass knowledge doc-select-candidates [--dry-run]
codecompass knowledge doc-acknowledge-stale DOC_NAME REGION
codecompass knowledge doc-acknowledge-chunks
```

See `docs/workflows/knowledge-reconciliation-loop.md` for full mechanics.

## A retired command

`codecompass promote` **no longer exists** — removed entirely (referenced as `decisions/0033`). Its three former jobs (cloning, enrichment, Skill generation) are now automatic outcomes of the bootstrap/`sync` flow described above. Running `codecompass promote` produces Typer's standard "no such command" error.
