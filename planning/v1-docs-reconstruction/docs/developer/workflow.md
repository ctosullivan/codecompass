# Test, lint, and release workflow

Derived from `pyproject.toml`, this repository's own `CONTRIBUTING.md`
(factual process content, not narrative product documentation) and
`CLAUDE.md`, and a direct check of what CI configuration actually exists
in this repository (none — see the note at the end).

## Local development setup

```bash
pip install -e ".[dev]"
```

`pyproject.toml`'s `[project.optional-dependencies].dev` group:
`pytest`, `ruff`, `jsonschema`.

## Running tests

```bash
pytest
```

`pyproject.toml`'s `[tool.pytest.ini_options]` sets `testpaths =
["tests"]` and defines one custom marker:

```
smoke: exercises a real external tool (npm/cargo) — network/toolchain
dependent, skipped automatically when the tool isn't present.
```

Test layout mirrors `src/codecompass/`'s own module structure — one test
module per source module, minimum (`tests/README.md`'s stated
convention, confirmed by the real file list: `test_adapters_base.py`,
`test_config.py`, `test_graph.py`, `test_sync.py`, etc., one per
`src/codecompass/*.py`). Adapter tests specifically use **fixture
mocking, never live subprocesses**, by design (`decisions/0014`) — see
[`writing-an-adapter.md`](writing-an-adapter.md)'s testing notes for the
concrete pattern. A smoke-marked test is skipped automatically rather
than failing when its real external tool (`npm`, `cargo`) isn't on
`PATH` — check a test file's own skip condition
(`pytest.mark.skipif`/marker registration) rather than assuming it always
runs.

Gap analysis / AI-enrichment tests never call the live Anthropic API
(`decisions/0016`) — they exercise `enrichment.py`/`relation_
enrichment.py`'s batching, cost-estimation, and result-application logic
against fixture responses, not a real model call.

## Linting

```bash
ruff check .
```

`pyproject.toml`'s `[tool.ruff]`: `line-length = 100`, `target-version =
"py311"`. `[tool.ruff.lint]` selects rule sets `E`, `F`, `I`, `UP`
(pycodestyle errors, pyflakes, import sorting, pyupgrade).

## Maintainer-only doc-sync checks (not shipped, not a `codecompass`
subcommand)

Two scripts under `scripts/`, checking **this repository's own** docs
against **this repository's own** code — never a consuming project's:

```bash
python scripts/check_user_docs.py [--strict]
python scripts/check_knowledge_base.py
```

`check_user_docs.py` is report-only by default (always exits 0);
`--strict` exits 1 if any *blocking* finding exists (an `(info)`-tagged
finding never fails `--strict`). Its checks include: every CLI command
mentioned in `docs/cli-reference.md`, every `VendorConfig` field
mentioned in `docs/config-schema.md`, internal Markdown link resolution,
fenced `codecompass` example commands using real subcommands, ADR
Status/cross-reference integrity, retired names appearing as live prose
(not history), and generated-artifact-vs-generator drift (`
scripts/check_user_docs.py`'s own module docstring lists the current
full set — reproduced faithfully above from that docstring, current as
of Phase 43b).

## Definition of done, per phase (governs commits, not just code)

This project develops via a phase-by-phase roadmap
(`planning/ROADMAP.md`), each gated by `CLAUDE.md` §5's Definition of
Done: plan file exists before implementation
(`planning/phase-N-<name>.md`); code implemented and its plan's
verification step passes; `docs/`/`architecture/`/`decisions/` updated
in the **same commit** as the change that affects them; an independent
per-phase drift audit finds no current-truth doc left misdescribing the
system; a `CHANGELOG.md` entry lands in the same commit; `planning/
CONTEXT.md` and `planning/ROADMAP.md` reflect the new state; a phase
retro exists; and an independent audit pass confirms all of the above
rather than trusting the implementing agent's own report. A phase is
not "done" — and its commits are not pushed — until every one of these
holds (`CLAUDE.md` §5).

## Commit conventions

- One logical change per commit: `type(phase-N): summary` (e.g.
  `feat(phase-3): dedupe diamond dependencies in DEPTREE.md`).
- `CHANGELOG.md` follows [Keep a Changelog](https://keepachangelog.com)
  + [SemVer](https://semver.org); every phase adds one categorized entry
  under `[Unreleased]`, in the same commit as the change — never batched
  across phases.
- **No AI attribution in commits** — a fixed project convention
  (`CLAUDE.md` §7), regardless of how much of a change was AI-authored.
- Push to `origin` happens automatically once a phase's commits land and
  its Definition-of-Done gate passes (`CLAUDE.md` §6) — not a
  per-push confirmation for that specific action.

## Releases

Milestones are **roadmap phase groups**, not individual phases (e.g.
MVP v0.1 = phases 0–8; MVP v0.2 = phases 9–19; the whole
`planning/v1-redefinition/` effort is one further milestone group).
Only once a milestone's *last* phase is marked `done` does
`[Unreleased]` get promoted to a dated `CHANGELOG.md` release section
and a version tag get cut — not after every phase. `pyproject.toml`'s
`version = "1.0.0.dev0"` is explicitly **distinct** from "CodeCompass v1"
as a product milestone (`CLAUDE.md` §6) — don't conflate the two.

**Observed gap**: as of this checkout, `git tag` returns no tags at
all, despite this being the stated release mechanism (`CLAUDE.md` §6,
`CONTRIBUTING.md`) — worth noting as a real gap between the documented
convention and this repository's actual tag history, though it may
simply reflect that no milestone has completed and been tagged yet at
this point in the roadmap (this proposal does not investigate which).

**No CI configuration exists in this repository itself** — `pytest`/
`ruff check .`/the two `scripts/check_*.py` scripts above are all run
manually or via a pre-commit habit, per `CONTRIBUTING.md`'s "Local
development" section, not enforced by any `.github/workflows/` file in
`codecompass` itself (confirmed: no `.github/` directory exists at this
repository's root). The two adapter-protocol submodules
(`adapters/haskell/`, `protocol/codecompass-adaptor-protocol/`) each
carry their *own* `.github/workflows/ci.yml` — those are independent
repositories with their own CI, not `codecompass`'s.
