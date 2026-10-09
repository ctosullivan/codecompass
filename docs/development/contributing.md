# Contributing (supplementary — development/tooling detail)

**For process, licensing, and the Contributor License Agreement, see the
root [`CONTRIBUTING.md`](../../CONTRIBUTING.md)** — the self-governing
process document this reconstruction was correctly never shown (it
mirrors the root `CLAUDE.md`, also out of scope here), so it is left
untouched rather than replaced. This page covers only the narrower,
product/tooling-level detail that *is* within the available evidence.

## Code style

`pyproject.toml`'s `[tool.ruff]` configuration: `line-length = 100`, `target-version = "py311"`, `select = ["E", "F", "I", "UP"]`. Two specific paths are excluded from lint (real, preserved evidence from two downstream template-usability exercises, not this project's own source, never meant to meet its lint conventions):
- `planning/knowledge/first-party-source-symbols/template-usability-exercise/tinytodo-after-adoption`
- `planning/knowledge/first-party-source-symbols/template-usability-exercise-2/tinytodo2-final-tree`

## Development dependencies

`pytest`, `ruff`, `jsonschema` (`pyproject.toml`'s `[project.optional-dependencies].dev`).

## Maintainer-only tooling (`scripts/`)

Not part of the installed `codecompass` package — each script's own module docstring says so explicitly.

- **`scripts/check_knowledge_base.py`** — a mechanical sanity check over CodeCompass's own `planning/knowledge/<slug>/` tree: required fields per record kind, cross-reference resolution, the Claim/Decision `supersedes` cross-kind hard rule, requirement-cites-approved-decision, anchor integrity, snapshot historical-integrity/completeness/current-divergence. Report-only by default; `--strict` exits non-zero on a blocking finding. Hard-coded to this one repository — not something an adopting project can simply point elsewhere (see `docs/concepts/knowledge-model.md`).
- **`scripts/check_user_docs.py`** — a mechanical sanity check that this repository's own narrative docs match its own code (CLI command coverage, `ANTHROPIC_API_KEY` mention, `VendorConfig` field coverage, internal link resolution, retired-identifier-as-live-prose detection, generated-artifact-vs-generator drift, and several project-process-specific checks). Report-only by default; `--strict` exits non-zero on a blocking finding.
- **`scripts/prepare_cleanroom_branch.py`** — builds and validates an explicitly allow-listed export of this repository's own source/tests/configuration, for a documentation-reconstruction exercise of the kind that produced this very `docs/` tree. Ordinary repository-maintenance tooling, not a runtime capability of the `codecompass` product. See [`clean-room-redocumentation.md`](clean-room-redocumentation.md) for the full, proven process this and the related `cleanroom_broker*`/`cleanroom_prompt_assembler.py` scripts implement.

## Governance records

`decisions/**` (an append-only ADR log) and `planning/retros/**`/`planning/ROADMAP.md`/`planning/CONTEXT.md`/`planning/learnings/**` (process history) exist as this project's own governance record, referenced throughout this documentation by number, but are not themselves part of the available evidence for this reconstruction — see `docs/decisions.md` for the mechanically-derived title+status index that *is* available.
