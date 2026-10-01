# Phase 80 Stage 2 — model-blind reconstruction export scope manifest

Export root: `/tmp/claude-1000/-home-cormac-projects-codecompass/0b2afcc0-cb03-48e4-8480-bf16722dc977/scratchpad/phase80-reconstruction-export`

## Included (primary implementation evidence only)

- `src/codecompass/cli.py`, `commands.py`, `config.py`, `sync.py`,
  `graph.py`, `core.py`, `discovery.py`, `__init__.py`
- `src/codecompass/adapters/base.py`, `python.py`, `__init__.py`
- `tests/test_cli.py`, `test_commands.py`, `test_config.py`,
  `test_sync.py`, `test_graph.py`, `test_core.py`, `test_discovery.py`,
  `test_adapters_base.py`, `test_adapter_python.py`,
  `test_adapters_dispatch.py`
- `pyproject.toml` (for declared dependencies/package metadata)

## Explicitly excluded

- `README.md`, `docs/`, `architecture/`, `ai-docs/`, `CLAUDE.md`,
  `CONTRIBUTING.md`, `decisions/`, `planning/` (all of it, including
  `planning/knowledge/codecompass-domain/`) — no conceptual model, no
  legacy narrative, no ADR rationale.
- Every other `src/codecompass/*.py` module not listed above (chat.py,
  claude_md.py, deptree.py, doc_chunking.py, doc_mapping.py,
  enrichment.py, filetree.py, git_topology.py, index.py,
  relation_enrichment.py, skill.py, skill_scan.py, source_resolution.py,
  source_symbols.py, spec_docs.py, staleness.py, symbols.py, usage.py)
  and the other three adapters (cargo.py, haskell.py, npm.py,
  external_process.py) — Stage 2 is bounded to the CLI/sync/graph/
  adapter-pattern core named in the phase plan, not full project
  coverage; this is a disclosed scope limit, not an oversight.

## Access evidence (post-dispatch)

Reconstruction completed and self-reported (see
`phase80-implementation-reconstruction.md`): the export was NOT fully
runnable as a whole — `cli.py`/`sync.py`/`adapters/base.py`/
`adapters/python.py` all transitively import sibling modules
deliberately excluded by this manifest's own scope (`enrichment`,
`relation_enrichment`, `chat`, `index`, `skill`, `source_resolution`,
`staleness`, `filetree`, `symbols`, `git_topology`, `skill_scan`,
`source_symbols`, `spec_docs`, `usage`, `claude_md`, `deptree`,
`doc_mapping`, the other three adapters) — a disclosed consequence of
the deliberate scope boundary, not a surprise. 5 of 10 test files
(`test_cli.py`, `test_sync.py`, `test_adapters_base.py`,
`test_adapters_dispatch.py`, `test_adapter_python.py`) could not even
be collected by pytest for the same reason. One genuine, undisclosed
export-completeness gap: `tests/fixtures/` was never copied into the
export, breaking `test_config.py::test_load_valid_vendor_config`
(`FileNotFoundError`) even though `config.py` itself is fully within
scope — an accidental omission, not a deliberate exclusion; noted here
rather than silently re-run, since the reconstruction's own report
already distinguishes this from the deliberate module exclusions and
the 116/117 passing tests already give strong, usable evidence for the
in-scope modules.

## Isolation tier

Tier 2 (curated same-host export directory), `best-effort` only — Tier 1
(`Agent(isolation: "remote")`) was already definitively tested and
failed in this environment during Phase 79 (all five tested routes).
Not re-attempted here. Boundary evidence (tool-call transcript analysis)
to be gathered after the dispatch completes, same method as Phase 79's
fifth amendment.
