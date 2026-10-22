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

- **`scripts/check_knowledge_base.py`** — a mechanical sanity check over CodeCompass's own `planning/knowledge/<slug>/` tree: required fields per record kind, cross-reference resolution, the Claim/Decision `supersedes` cross-kind hard rule, requirement-cites-approved-decision, anchor integrity, snapshot historical-integrity/completeness/current-divergence, and (Phase 82) `status: verified` citing a real, passing oracle result for every required check of its own contract — including (`decisions/0082`, corrective pass) failing closed when a required scope's only evidence is a historically recorded `PASS` that cannot currently be reconfirmed against the real implementation (`--ledgerkit-root PATH`, default `~/projects/ledgerkit`), and (`decisions/0083`, second corrective pass) failing closed — a blocking finding, not merely informational — when `codecompass`'s own oracle/knowledge_intermediate modules cannot be imported at all, so a broken environment can never report this check as silently skipped. Report-only by default; `--strict` exits non-zero on a blocking finding. Hard-coded to this one repository — not something an adopting project can simply point elsewhere (see `docs/concepts/knowledge-model.md`).
- **`scripts/check_user_docs.py`** — a mechanical sanity check that this repository's own narrative docs match its own code (CLI command coverage, `ANTHROPIC_API_KEY` mention, `VendorConfig` field coverage, internal link resolution, retired-identifier-as-live-prose detection, generated-artifact-vs-generator drift, and several project-process-specific checks). Report-only by default; `--strict` exits non-zero on a blocking finding.
- **`scripts/check_contracts.py`** (Phase 82) — a mechanical sanity check over `planning/contracts/<slug>/` oracle-contract/oracle-result files: schema shape, cross-reference resolution (`contract_id`/`check_id`), tamper-evidence (content-digest recomputation against a live Ledgerkit-style checkout when available), the computed PASS/FAIL/GAP/INVALID aggregate per check, and source-citation depth (a cited symbol must actually exist at the cited location, not merely a resolvable file path). Since `decisions/0082` (corrective pass), `--strict` also fails closed — not merely informationally — when a required check's only on-record evidence is a historically recorded `PASS` and the Ledgerkit checkout is unavailable to reconfirm it; since `decisions/0083` (second corrective pass), `--strict` also fails closed when `codecompass.oracle` itself cannot be imported, since every check in this script depends on it. Report-only by default; `--strict` exits non-zero on a blocking finding.
- **`scripts/run_balance_from_spec_oracle.py`** (Phase 82) — executes Phase 82's one real oracle contract (`planning/contracts/balance-from-spec/`) against a real Ledgerkit checkout and writes one new, permanent `<check_id>--<run_id>.yaml`/`.txt` result/raw-output file pair per execution (`decisions/0082`, corrective pass) — never overwriting a prior run's own evidence. An execution whose check reference resolves to only skipped tests is recorded `INVALID`, never `PASS` (`decisions/0083`). Not a shipped `codecompass` command.
- **`scripts/prepare_cleanroom_branch.py`** — builds and validates an explicitly allow-listed export of this repository's own source/tests/configuration, for a documentation-reconstruction exercise of the kind that produced this very `docs/` tree. Ordinary repository-maintenance tooling, not a runtime capability of the `codecompass` product. See [`clean-room-redocumentation.md`](clean-room-redocumentation.md) for the full, proven process this and the related `cleanroom_broker*`/`cleanroom_prompt_assembler.py` scripts implement.

## Governance records

`decisions/**` (an append-only ADR log) and `planning/retros/**`/`planning/ROADMAP.md`/`planning/CONTEXT.md`/`planning/learnings/**` (process history) exist as this project's own governance record, referenced throughout this documentation by number, but are not themselves part of the available evidence for this reconstruction — see `docs/decisions.md` for the mechanically-derived title+status index that *is* available.
