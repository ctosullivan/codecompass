# Component map

One paragraph per module under `src/codecompass/`, grounded in that module's own docstring/behaviour.

| Module | Role |
|---|---|
| `cli.py` | The Typer CLI entry point. Wires every other module together; implements the bare-command bootstrap, `sync`, `index`, `check`, the `query`/`enrich`/`knowledge` subcommand groups, `chat`, and `undo`. |
| `core.py` | Ecosystem-agnostic data models: `Ecosystem` enum, `VendorConfig`, `RepositoryLocation`, `DepNode` (a mutable dependency-tree node), `VendorDigest`. |
| `config.py` | Parses `vendor.toml` into `VendorConfig` objects; fail-fast validation. |
| `discovery.py` | Manifest-based dependency discovery (`package.json`, `pyproject.toml`, `requirements.txt`, `Cargo.toml`, `package.yaml`) and `vendor.toml` bootstrap/append. |
| `adapters/` | `base.py` (the `EcosystemAdapter` ABC and the shared subprocess seam), `npm.py`, `python.py`, `cargo.py` (in-process adapters), `external_process.py` (the generic JSON-Lines external-adapter client, zero ecosystem-specific knowledge), `haskell.py` (the thin external-process dispatcher). |
| `symbols.py` | Per-ecosystem, no-AI symbol/purpose extraction for a *vendor's own* installed source (Rust `pub` items, Python `ast`-based top-level defs, npm `.d.ts` export declarations). Shared by adapters' API-surface rendering and `filetree.py`'s per-file purpose annotations. |
| `source_symbols.py` | The *first-party* counterpart to `symbols.py` — extracts the *consuming project's own* top-level implementation symbols (not a dependency's), independent of any tracked vendor. See `docs/reference/symbol-extraction.md`. |
| `usage.py` | Detects the consuming project's own imports of tracked vendors (Python `ast`, npm/Rust regex-based), the opposite direction from `symbols.py`. |
| `deptree.py` | Deterministic `DEPTREE.md`/`deptree.json` rendering from a `DepNode` tree — diamond-dependency dedup, dev-only collapsing, depth-capped with an explicit truncation notice. |
| `filetree.py` | Deterministic `FILETREE.md`/`filetree.json` rendering, plus a flat greppable symbol index, from a vendor's source directory. |
| `claude_md.py` | Renders/updates a per-vendor `CLAUDE.md` (the `VendorDigest` → Markdown template), including the in-place Description-section rewrite enrichment uses. |
| `sync.py` | Per-vendor sync orchestration (`sync_vendor`, `sync_all`) and whole-project context-graph rebuild orchestration (`rebuild_project_graph`). |
| `graph.py` | The SQLite schema, migrations, `rebuild_deterministic` (the full-rebuild transaction), and every read/write query function. See `docs/architecture/data-and-control-flow.md`. |
| `source_resolution.py` | Resolves and shallow-clones a vendor's upstream repository from locally-available package metadata only (no registry network lookup for *resolution*; cloning itself needs network access to `git`). |
| `staleness.py` | `codecompass check` — severity-aware (patch/minor/major) version-drift comparison against each vendor's persisted digest. |
| `enrichment.py` | Batched, usage-driven AI enrichment of vendors/symbols — the "Phase B" pipeline. See `docs/workflows/sync-and-enrichment-pipeline.md`. |
| `relation_enrichment.py` | The sibling AI-enrichment pipeline for spec-doc ↔ dependency/Skill relationships, with a structural, non-negotiable boundary against ever writing into a spec doc file. |
| `spec_docs.py` | Detects a project's own human-authored spec documentation (README, `docs/**`, `decisions/**`, etc.) as `doc_artifacts` rows, distinct from CodeCompass's own generated docs. |
| `doc_mapping.py` | Pure transformations over already-generated artifacts into context-graph edge rows — documents/routes/depends-on/doc-relation edges. |
| `doc_chunking.py` | Deterministic heading-based Markdown chunking, sharpening mention-detection attribution to a specific section rather than a whole file. |
| `skill_scan.py` | Indexes every Agent Skill and Cursor `.mdc` rule in the project (not just CodeCompass's own) and their mechanical mentions of vendors/source files. |
| `skill.py` | Generates the tool-level Skill, per-vendor Skills, and Cursor `.mdc` rules. |
| `commands.py` | Generates the `/discovery` slash command. |
| `index.py` | Idempotent routing-table injection into the project root `CLAUDE.md`, reading already-synced state only — never triggers a sync itself. |
| `git_topology.py` | Git repository topology detection (worktrees, submodules) — mechanical facts only, no network/AI involvement; never invoked at query time, only at sync time. |
| `usage.py` | (see above). |
| `chat.py` | A secondary, digest-only chat REPL grounded entirely on already-persisted files. |
| `knowledge_intermediate.py` | The intermediate knowledge layer — rendering, dual-hash change detection, manifest-based review, and the sole canonical-record write path. See `docs/concepts/knowledge-model.md` and `docs/workflows/knowledge-reconciliation-loop.md`. |
