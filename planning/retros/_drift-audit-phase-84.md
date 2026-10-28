# Phase 84 drift audit

**Auditor:** docs-reconstructor (independent, MODE 1 per-phase drift
audit).
**Scope:** `git diff 7e8c538..447ba2b -- src/codecompass/knowledge_api.py
src/codecompass/cli.py docs/
decisions/0091-phase-84-knowledge-api-implementation-resolutions.md
planning/phase-84-consolidated-knowledge-api.md`, cross-referenced
against the real, live code (`src/codecompass/knowledge_api.py`,
`src/codecompass/cli.py`) and the actual running CLI (`.venv/bin/
codecompass knowledge <cmd> --help`, confirmed the editable install
resolves to this checkout's own `src/`), plus a broad grep of
`README.md`, `docs/**`, `ai-docs/README.md`, `CONTRIBUTING.md` for
`knowledge`/`knowledge_api`/shared-schema language. `docs/domain/` does
not exist in this repo yet, so the domain-claim-staleness step was
skipped per the role's own standing instructions.

**Verdict: DRIFT — 3 findings, all in the same new section of
`docs/reference/cli.md`, all blocking (user-facing false statements a
reader would act on and get a CLI error, or a dead link).** Everything
else checked (the `components.md` row, the two `overview.md` bullets,
the plan file, `decisions/0091`, and the reverse-direction check across
other existing docs) is accurate.

## Findings (all in `docs/reference/cli.md`, new "`codecompass knowledge
get|search|trace|gaps|context|export` (Phase 84)" section)

1. **`docs/reference/cli.md:217-219`** — "Every command accepts `--json`
   (`export` always prints a one-line confirmation; its actual output is
   the file at `OUT_PATH`) for machine-readable consumption." This is
   false for `export`: `knowledge_export` (`src/codecompass/cli.py`,
   `@knowledge_app.command("export")`) takes only `slug`, `out_path`,
   `--project-id` — no `json_output` parameter, no `--json` option at
   all. Confirmed two ways: (a) reading the function signature directly;
   (b) running the real CLI —
   `.venv/bin/codecompass knowledge export some-slug /tmp/out.json --json`
   exits 2 with `Error: No such option: --json`, and
   `codecompass knowledge export --help` lists only `--project-id`/
   `--help`. The doc's own synopsis two lines above (`codecompass
   knowledge export SLUG OUT_PATH [--project-id ID]`, line 171) correctly
   omits `--json` — only this later summary sentence contradicts it.
   **Blocking** — a reader following this sentence hits a CLI error.

2. **`docs/reference/cli.md:181-182`** — "Namespaced apart from this
   app's existing mutation verbs (`apply`, `select-candidates`,
   `doc-acknowledge-*`) — none of these six commands writes anything,
   ever." This is self-contradicted a few lines later in the same
   section: the `export` bullet (line 211-215) correctly says it "writes
   exactly `OUT_PATH`" — confirmed in code,
   `export_snapshot()`'s `out_path.write_text(...)` at
   `src/codecompass/knowledge_api.py:1402`. The blanket "writes nothing,
   ever" is true only for the five read-only commands and only true for
   `export` with respect to *canonical* project knowledge
   (`planning/knowledge/`/`planning/contracts/`), not for "anything" —
   `export` does write a real file. **Blocking** (self-contradictory
   within the same doc section; a reader can't tell which of the two
   sentences governs).

3. **`docs/reference/cli.md:179`** — "See `architecture/knowledge-api.md`
   for the full design." No file named `knowledge-api.md` exists
   anywhere in the repository (`find . -iname "knowledge-api.md"` —
   nothing; `ls docs/architecture/` has no such file either). This is
   the only `architecture/`-prefixed reference in this file; every other
   cross-reference in `docs/reference/cli.md` uses the `docs/`-prefixed
   form (e.g. `docs/workflows/knowledge-reconciliation-loop.md`, two
   lines above at line 233 pre-diff). `scripts/check_user_docs.py`'s own
   internal-link-resolution check does not catch this (it checks
   `[text](path)` markdown links, not inline-code path mentions in
   prose), so it's a real gap this tool's own mechanical check won't
   surface on its own. **Blocking** (dangling reference to a document
   that was apparently intended but never written, in the section meant
   to be this new feature's primary CLI-reference entry point).

## Checked and found accurate (no action needed)

- **`docs/reference/cli.md`'s command synopses and per-command bullets**
  (lines 163-215, apart from finding 1/2 above) — verified against the
  real Typer command signatures in `src/codecompass/cli.py` *and* by
  running `.venv/bin/codecompass knowledge {get,search,trace,gaps,
  context,export} --help` directly: flag names (`--kind`, `--relation`,
  `--depth`, `--evidence`, `--max-items`, `--max-chars`, `--project-id`),
  defaults (`--relation` default `supporting_evidence`; `--depth`
  default `1`, `min=1`; `--max-items` default `20`; `--max-chars`
  default `6000`), and the `trace --relation` vocabulary
  (`depends_on`/`supporting_evidence`/`contradicting_evidence`/
  `observations`/`decision` + `_reverse`, `cites`/`cited_by`,
  `checks`/`results`, `doc_mentions`) all match `knowledge_api.py`'s
  real `traverse()` dispatch exactly, including that `_reverse` is only
  documented (correctly) for the first five, never implied for
  `cites`/`checks`/`doc_mentions`.
- **`docs/reference/cli.md`'s pre-existing, unchanged `query relations`
  section** (lines 86-94) — genuinely untouched by this diff (confirmed
  against the diff directly); accurate as-is since the migration is
  claimed byte-identical and the CLI's own output path
  (`knowledge_api.resolve_doc_mentions`) is a verbatim relocation of the
  removed `_resolve_relations`/`_incoming_doc_relations`/
  `_relation_enrichment_row` — read side by side, the moved functions are
  unchanged apart from where they live.
- **`docs/architecture/overview.md`'s new "four main subsystems" bullet
  and new "logical consolidation" bullet** — both accurate against
  `knowledge_api.py`'s real behaviour and module docstring (read-only;
  reads `context-graph.db`/`planning/knowledge/`/`planning/contracts/`
  through existing readers; no new database/persisted identifier/
  mutation path; natural-key example given,
  `source_file.path`+`name`+`kind`+`line`, matches `symbol_identity()`'s
  real signature). The pre-existing, untouched "primary interface is
  generated artifacts, not a live API" bullet is not contradicted by
  this —  that bullet's "live API" means a reachable server/MCP
  endpoint (per the surrounding "no server component" framing at the
  top of the file); `knowledge_api.py` is an in-process library called
  per-CLI-invocation, not a running service, so no tension.
- **`docs/architecture/components.md`'s new `knowledge_api.py` row** —
  the eight listed functions (`get`/`search`/`traverse`/
  `trace_evidence`/`epistemic_status`/`find_gaps`/`get_context_packet`/
  `export_snapshot`) all exist with those exact names; the seven listed
  authority tags match the seven `AUTHORITY_*` constants exactly, in the
  same order; "never through `graph.open_graph`" confirmed — the module
  uses its own `_open_ro()` (`sqlite3.connect(..., mode=ro, ...)`
  URI), never imports/calls `graph.open_graph`.
- **Reverse-direction check (did Phase 84 make an existing doc sentence
  false?)** — `docs/concepts/knowledge-model.md:27`'s "No shared schema
  unifies these [provenance mechanisms]" is about *schema*, not read
  access; `knowledge_api.py` introduces a shared *read interface*, no
  new schema, so still true. `docs/concepts/knowledge-model.md:31`'s
  "[`derive_epistemic_profile`] is not yet exposed through any
  `codecompass` CLI surface — library-only" is also still literally true
  post-Phase-84: `knowledge_api.epistemic_status()` wraps it but is
  itself never wired to any `@knowledge_app.command` (confirmed by
  grepping `cli.py` and `knowledge_api.py` — only `get`/`search`/
  `trace`/`gaps`/`context`/`export` are registered commands;
  `epistemic_status` is exercised only directly by
  `tests/test_knowledge_api.py`). `README.md`'s "`codecompass knowledge
  apply` is the sole, mechanically-revalidating write path" and
  `docs/workflows/knowledge-reconciliation-loop.md`'s "the **only**
  function in the codebase allowed to write a canonical
  `planning/knowledge/*/*.yaml` record" both remain true — Phase 84 adds
  no new write path to canonical knowledge (`export_snapshot` writes
  only an arbitrary external `OUT_PATH`, explicitly refusing to write
  inside either canonical tree).
- **`planning/phase-84-consolidated-knowledge-api.md`** — the added
  "Status: implemented" header and the removal of the old "Planning
  only — no implementation begins..." sentence are accurate (this phase
  is in fact implemented); the §10 "Unresolved decisions" edit correctly
  marks the `ContextPacket` shape resolved via `decisions/0091` §6 and
  correctly leaves the `assess_change_impact.py` rewrite question
  genuinely unresolved (confirmed: `scripts/assess_change_impact.py` was
  not touched by this diff at all).
- **`decisions/0091`** — spot-checked its concrete claims against the
  real source rather than trusting its own prose: the `ApiResponse`
  shape (`status`/`results`/`gaps`/`message`) matches the dataclass
  exactly; the `ContextPacket` priority order in §6 (subject → direct
  `depends_on`/`depends_on_reverse`/`supporting_evidence`/
  `contradicting_evidence` → `trace_evidence`'s gaps) matches
  `get_context_packet()`'s real loop exactly (note: this matches §6's
  *own* description, but not `get_context_packet()`'s own, more
  elaborate module-level docstring inside `knowledge_api.py` itself,
  which describes a 5-step order including a step for "scoped
  verification (oracle checks/results)" the real loop never executes —
  a source-file docstring-vs-implementation mismatch, not a
  README/docs/architecture/ai-docs claim, so out of this audit's own
  scope; flagged below for the lead); `max_items`/`max_chars` defaults
  (20/6000) confirmed live via `--help`; the "read-only ... never
  through `graph.open_graph`" claim confirmed in code; "47 tests"
  confirmed via `pytest tests/test_knowledge_api.py --collect-only -q`;
  `TestNoMutationPath::test_get_does_not_create_a_missing_
  context_graph_db` confirmed to exist by that exact name.
- **`README.md`, `ai-docs/README.md`, `CONTRIBUTING.md`,
  `docs/workflows/knowledge-reconciliation-loop.md`,
  `docs/architecture/data-and-control-flow.md`** — broadly grepped for
  `knowledge`/subcommand-list/shared-schema language; nothing in any of
  these claims an exhaustive `knowledge` subcommand list or a "no shared
  interface" statement that Phase 84 would falsify.

## Non-docs notes (out of this audit's own scope, flagged for the lead)

- `src/codecompass/knowledge_api.py::get_context_packet`'s own module
  docstring (not a README/docs/architecture/ai-docs claim) describes a
  5-step priority order including a dedicated "scoped verification
  (oracle checks/results)" step the real implementation never executes
  (the loop only ever traverses `depends_on`/`depends_on_reverse`/
  `supporting_evidence`/`contradicting_evidence`, then appends
  `trace_evidence`'s gaps — no separate checks/results fetch). The
  simpler, accurate description lives in `decisions/0091` §6 and in
  `docs/reference/cli.md`'s own `context` bullet, so no *doc* is wrong,
  but the source's own docstring overclaims relative to its own
  function body.
- `src/codecompass/cli.py::query_relations`'s migration docstring cites
  the backward-compatibility test as
  `tests/test_cli.py::test_query_relations_backward_compatible`; the
  real test name is
  `test_query_relations_backward_compatible_after_knowledge_api_migration`
  (confirmed via `grep -n` in `tests/test_cli.py`). A source-code
  docstring, not a doc file, so outside this audit's own scope, but
  worth a one-line fix alongside the three findings above.
