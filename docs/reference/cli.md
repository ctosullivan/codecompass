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

The *how* behind this cleanup depends on whether `context-graph.db` exists yet, via two structurally different enumeration strategies, each with a different precision guarantee:

- **Graph-backed (precise)** — when `context-graph.db` already exists: `undo` queries it directly for every `doc_artifacts` row tagged `origin IN ('codecompass_tool', 'codecompass_vendor')` (`third_party`-origin rows are never selected, by construction, not by a filter applied after the fact), resolves each to a real path, and adds every tracked vendor's own `vendor/<name>/` directory from the `vendors` table. This correctly distinguishes a CodeCompass-generated artifact from a third-party one by its real, recorded origin.
- **Pattern-based (fallback)** — when no `context-graph.db` exists yet (e.g. only `init --scan` has run, with no whole-project sync): `undo` instead matches a fixed set of path globs against the exact naming conventions `skill.py`/`commands.py` use (`.claude/skills/codecompass*`, `.cursor/rules/codecompass-*.mdc`, `.claude/commands/discovery.md`, plus each tracked vendor's `vendor/<name>/` directory from `vendor.toml`). This is **less precise**: because it has no recorded origin to check against, it cannot distinguish a hand-renamed third-party artifact that happens to match the same naming pattern from a real CodeCompass-generated one — a real, disclosed precision gap this fallback mode accepts in exchange for working without a prior sync.

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

## `codecompass knowledge get|search|trace|gaps|context|export` (Phase 84)

```
codecompass knowledge get RECORD_ID [--repo-root PATH] [--json]
codecompass knowledge search TEXT [--kind KIND ...] [--json]
codecompass knowledge trace RECORD_ID [--relation RELATION] [--depth N] [--evidence] [--repo-root PATH] [--json]
codecompass knowledge gaps [SLUG] [--repo-root PATH] [--json]
codecompass knowledge context TOPIC [--max-items N] [--max-chars N] [--repo-root PATH] [--json]
codecompass knowledge export SLUG OUT_PATH [--project-id ID]
```

A **read-only** CLI surface over `src/codecompass/knowledge_api.py` — one
stable, typed interface over `context-graph.db`, `planning/knowledge/`,
and `planning/contracts/`, so a caller (a script, or a coding agent) can
ask "what does this project know about X, how confident are we, and is
that still current" without independently reconstructing any of those
three storage formats. See `docs/architecture/overview.md` and
`docs/architecture/components.md` for the full design. Namespaced apart
from this app's existing mutation verbs (`apply`, `select-candidates`,
`doc-acknowledge-*`) — none of these six commands ever writes to
canonical project knowledge (`export`, the one exception, writes only
the explicitly requested `OUT_PATH`, detailed below).

- **`get RECORD_ID`** — one item by its own stable identity: a
  `REQ-`/`CL-`/`EV-`/`OBS-`/`DE-`/`DEC-` id, or a natural-key identity
  (`symbol:<path>:<name>:<kind>:<line>`, `vendor:<name>`, `doc:<path>`,
  `contract:<contract_id>`, `check:<contract_id>:<check_id>`,
  `result:<contract_id>:<check_id>:<run_id>`).
- **`search TEXT`** — free-text discovery across knowledge-record fields
  and oracle contract/check ids; `--kind` (repeatable) restricts to one
  or more record/oracle kinds.
- **`trace RECORD_ID`** — follows one recorded relationship outward:
  `--relation` is one of `depends_on`/`supporting_evidence`/
  `contradicting_evidence`/`observations`/`decision` (any with a
  `_reverse` counterpart), `cites`/`cited_by`, `checks`/`results`, or
  `doc_mentions` (the exact mechanical web `query relations` itself now
  reads); `--evidence` instead runs `trace_evidence` (supporting +
  contradicting evidence, reporting an explicit **gap** when an
  obligation-bearing record has no evidence at all).
- **`gaps [SLUG]`** — missing, stale, or conflicting knowledge across
  record kinds in one call: an unverified required oracle scope, a
  contradicted record, a stale test-evidence citation (a cited result no
  longer valid against the live contract while a different, current
  `PASS` for the same check exists uncited), or a slug with claims/
  requirements but no oracle contract at all. Omit `SLUG` to scan every
  slug.
- **`context TOPIC`** — a bounded, deterministic development-context
  packet: the subject record, its direct relations, and its own gaps, in
  a fixed priority order, truncated at `--max-items`/`--max-chars` with
  truncation reported explicitly, never silently.
- **`export SLUG OUT_PATH`** — a portable, versioned export of one
  slug's canonical knowledge (`decisions/0079` §5's own project-identity
  envelope). Refuses to write inside `planning/knowledge/`/`planning/
  contracts/` — writes exactly `OUT_PATH`, never touches canonical
  project knowledge.

`get`/`search`/`trace`/`gaps`/`context` all accept `--json` for
machine-readable consumption. `export` has no `--json` option — it
always prints a one-line human-readable confirmation; its actual output
is the file it writes at `OUT_PATH`. `query relations` (above) is now
implemented in terms of this same API's own `doc_mentions` relation —
its own output is unchanged.

**`--repo-root PATH`** (`get`/`trace`/`gaps`/`context`; not `search`,
which does no oracle-result verification) — a live target checkout to
reconfirm oracle-result/check currency against. Every oracle-backed
result/check is only ever reported `current` when it was positively
(re)confirmed against this live checkout; without it, a historically
recorded `PASS` is reported `unconfirmed`, never `current` — real,
preserved evidence, just not currently reconfirmed (corrective pass,
`decisions/0092`). An actively disagreeing result (e.g. a contract that
has since changed, or a changed implementation) is reported `stale`
regardless of `--repo-root`.

## A retired command

`codecompass promote` **no longer exists** — removed entirely (referenced as `decisions/0033`). Its three former jobs (cloning, enrichment, Skill generation) are now automatic outcomes of the bootstrap/`sync` flow described above. Running `codecompass promote` produces Typer's standard "no such command" error.
