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
  obligation-bearing record has no evidence at all, or when a declared
  citation doesn't resolve to a real record — `dangling_evidence_
  reference`, `decisions/0092`). For a Requirement specifically, whose
  own knowledge-record schema has no `supporting_evidence` field at all,
  this resolves one hop through its `depends_on` Claims instead —
  tagged `supporting_indirect`/`contradicting_indirect` with a
  `via_claim` detail — rather than reporting every Requirement as
  missing evidence (`decisions/0093`); a `depends_on` id that doesn't
  resolve is its own `dangling_dependency_reference` gap.
- **`gaps [SLUG]`** — missing, stale, or conflicting knowledge across
  record kinds in one call: an unverified required oracle scope, a
  contradicted record, a stale test-evidence citation (a cited result no
  longer valid against the live contract while a different, current
  `PASS` for the same check exists uncited — qualified as live-
  reconfirmed or contract-relative-only depending on whether a
  `--repo-root` was reachable, `decisions/0093`), a dangling evidence
  reference (a `supporting_evidence`/`contradicting_evidence` citation
  that resolves to no real record, `decisions/0092`), a dangling
  dependency reference (a `depends_on` citation that resolves to no real
  record, `decisions/0093`), or a slug with claims/requirements but no
  oracle contract at all. Omit `SLUG` to scan every slug.
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

## `codecompass docs schema-init|compile|record-review|publish|maintain` (Phase 87, Stages 87A-87C)

```
codecompass docs schema-init DOCUMENT [--section-id ID] [--output PATH]
codecompass docs compile SCHEMA_PATH [--repo-root PATH]
codecompass docs record-review SCHEMA_PATH SECTION_ID --kind semantic|editorial \
    --verdict V --reviewer NAME [--finding TEXT ...] [--evidence-ref ID ...]
codecompass docs publish SCHEMA_PATH SECTION_ID
codecompass docs maintain [SCHEMA_PATHS]...
```

Compiles documentation sections from canonical knowledge through
Phase 84's existing `knowledge_api` only — no second knowledge store.
Stage 87A established one schema-governed document (`README.md`) and
the compile/review/publish lifecycle; Stage 87B extended this to a
second schema-governed document (`docs/getting-started.md`),
project-wide `maintain` discovery, a narrow sandboxed execution
harness for a small, explicitly allow-listed set of tested examples
(`scripts/execute_doc_example.py` — never a general command runner),
and a publication-time concurrency guard (below). Stage 87C extended
compilation to three further Concepts pages, established a repeatable
migration procedure for pre-existing human-authored pages, and ran a
real multi-region knowledge-change demonstration plus a
matched-baseline comparator against a conventional agent — the
comparator found the pipeline scopes a multi-document change more
completely, but did not demonstrate a net time/cost advantage on that
one, small change; see
`planning/retros/phase-87-stage-87c-knowledge-compiled-documentation.md`
for the full result. See
`planning/phase-87-documentation-schema-knowledge-compiled-documentation.md`
for the full design and `docs/development/clean-room-redocumentation.md`
for how `compile`'s clean-room composition step relates to (and
deliberately differs from) the existing whole-repository clean-room
broker/isolation scripts.

- **`schema-init DOCUMENT`** — scaffolds a minimal `*.schema.yaml` file
  next to `DOCUMENT` (or at `--output`), with one placeholder section
  (`--section-id`, default `section-one`) ready for the lead to fill in
  with real `required_knowledge` record ids. `schema-init` itself does
  not validate `document` — the path-confinement policy is enforced
  the first time the resulting schema is actually checked, by `compile`
  (below) or `publish`, never by scaffolding alone.
- **`compile SCHEMA_PATH`** — validates the schema (`scripts/
  check_doc_schema.py`, fail-closed on any blocking finding, including
  an unsafe `document` path), then resolves/hydrates/gap-checks each
  section's required knowledge and composes it through an isolated
  clean-room broker call, built from the packet's own verified on-disk
  bytes (hardening pass §N.C — never from the in-memory object alone).
  A section that clears the deterministic citation-scope check reaches
  `pending_review` and is written to `planning/retros/
  phase-87-pending-review/<schema-slug>/<section-id>.json`, now
  including a `draft_sha256`/`evidence_sha256`/`schema_section_sha256`
  identity triple and the original citation-tagged draft text
  (hardening pass §N.A) — this command never dispatches the two
  still-required independent reviews itself (`CLAUDE.md` §8:
  CodeCompass never spawns or coordinates agents); that is the lead's
  own next step.
- **`record-review SCHEMA_PATH SECTION_ID --kind ... --verdict ... --reviewer ...`**
  (hardening pass §N.A) — persists one independent review's verdict,
  findings, and evidence references, bound by hash to the exact
  pending draft/evidence/schema-section it was run against, to
  `<section-id>.review-<kind>.json` next to the pending-review record.
  `--kind semantic` accepts `supported`/`unsupported`; `--kind
  editorial` accepts `pass`/`fail`. `--reviewer` is self-reported
  dispatch provenance, not a cryptographic attestation — dispatching
  the two independent reviews remains the lead's own responsibility
  (`CLAUDE.md` §8); this command only prevents a forged, stale, or
  mismatched review record from being accepted later by `publish`.
- **`publish SCHEMA_PATH SECTION_ID`** — publishes a `pending_review`
  section into its governed document only when **both** a persisted
  `semantic` review (`verdict=supported`) and a persisted `editorial`
  review (`verdict=pass`) exist, are well-formed, and are bound by
  hash to the section's *current* draft, evidence, and schema
  definition — a bare `--semantic-verdict`/`--editorial-verdict`
  string is no longer accepted (hardening pass §N.A: the old flags
  proved nothing beyond "someone typed a passing word"). Also
  confirms `SECTION_ID` belongs to the live schema and confines the
  write target via `doc_compiler.resolve_publication_target`
  (`README.md`, or a `docs/**/*.md` file, resolved and confirmed to
  stay inside the project root even through a symlink — hardening
  pass §N.B). **Stage 87B publication-time concurrency guard**: the
  whole command runs inside a cooperating-writer file lock
  (`_doc_publish_lock`, 30s timeout, released on any exit path
  including an exception) and checks the live region's grounded-region
  state (via `doc_compiler.decide_publish_safety`) and the cited
  knowledge/schema-section's own freshness **twice**: once before the
  lock is acquired (a fast, user-friendly early refusal) and again,
  inside the lock, immediately before the write itself. The
  region-state check: a region with no finding or a real
  `claims_changed`/`noop` finding may proceed; an existing region with
  a live `doc_candidate` or `concurrent_conflict` finding is refused
  outright (a human edit is never silently overwritten); a brand-new,
  never-baselined region is only allowed through when its live content
  hash already matches the new body exactly (an idempotent republish),
  and refused otherwise. The second, write-boundary run of both checks
  exists because the first check and the write are both plain,
  synchronous Python — nothing stops a concurrent, non-cooperating
  editor's own disk write, or a knowledge change, from landing in that
  gap (confirmed directly: without this second check, exactly such an
  edit was silently overwritten). The same write boundary also
  independently re-verifies the pending review manifest's own
  integrity (recomputing the reviewed draft's identity from its actual
  `tagged_draft` text, against a freshly re-read copy of the manifest
  file, never the in-memory snapshot) — a persisted `draft_sha256` or
  `draft_body` field is never trusted merely because it is present and
  internally consistent-looking; the body actually published is always
  this freshly recomputed value. Immediately before composing the new
  text, `publish_section` itself re-checks one further, closer-still
  snapshot: a compare-and-swap of the document's own exact content
  (`doc_compiler.document_identity`), refusing to write
  (`DocPublishConflictError`, surfaced as a normal exit-1 `error:` —
  re-run `docs publish` to retry against the new content) on any
  mismatch; the write itself is atomic (write-then-rename), so a
  reader or a crash mid-write never observes a partial file. This
  narrows, but does not fully close, the window between that identity
  re-check and the write itself a few lines later, with no OS-level
  cross-process file lock — closing that completely would need a full
  transactional write, deliberately not built here; the residual
  window is disclosed in both `_doc_publish_lock`'s and
  `publish_section`'s own docstrings rather than assumed away. The
  persisted baseline
  advances (`knowledge_intermediate.advance_region_baseline_after_publish`)
  **only after** the write itself actually succeeds — never on
  detection, a failed validation, or a rejected publication. Always
  emits the section's machine-readable `codecompass-grounded-by
  region:<id>` marker, regardless of the schema's own reader-visible
  `citation_display` setting. On success, the tagged draft and both
  review records are preserved permanently at `planning/retros/
  phase-87-published-evidence/<schema-slug>/<section-id>.json` for
  later audits. This lock/revalidation protects cooperating
  `docs publish`/`docs maintain` invocations against each other; it
  cannot and does not lock out a human editing the file directly in
  an editor — the live-content-hash revalidation at the write boundary
  catches that case regardless, by refusing the write rather than by
  any locking mechanism.
- **`maintain [SCHEMA_PATHS]...`** — runs the real five-state
  grounded-region reconciliation (`new`/`noop`/`doc_candidate`/
  `claims_changed`/`concurrent_conflict`) for one or more schema-
  governed documents at once. **Stage 87B**: with no arguments, it
  discovers every `**/*.schema.yaml` under the project root itself
  (mirroring `scripts/check_doc_schema.py`'s own discovery) and
  reconciles every document any of them governs in one call — one or
  more explicit `SCHEMA_PATH` arguments still works exactly as before,
  scoped to just those documents. Never regenerates a `doc_candidate`
  (a human edit with no knowledge change) or a `concurrent_conflict`
  (both changed) automatically — both are reported for the lead's own
  resolution. Writing a fresh `doc_region_edit` reconciliation item is
  idempotent against an already-pending, unresolved item for the same
  region at the same content hash — re-running `maintain` repeatedly
  against an unresolved `doc_candidate` does not pile up duplicate
  manifests.

## A retired command

`codecompass promote` **no longer exists** — removed entirely (referenced as `decisions/0033`). Its three former jobs (cloning, enrichment, Skill generation) are now automatic outcomes of the bootstrap/`sync` flow described above. Running `codecompass promote` produces Typer's standard "no such command" error.
