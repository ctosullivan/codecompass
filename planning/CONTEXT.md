# Project context

This file reflects the *current* state of the project — overwritten at
each stopping point, not appended to. See `CHANGELOG.md` and git history
for the log of how it got here.

## Current phase

**A planning session has redefined what "CodeCompass v1" means.** Phases
0-38 are all `done` and unchanged — they are now framed as the
**foundation** (the npm/PyPI/Cargo package-source-grounding tool). The
former "v1.0" (Phase 23 = publish that tool to PyPI) is superseded:
**all publishing is held until the redefined v1** (user decision,
2026-09-09) — CodeCompass has never been published, and the first-ever
PyPI release will be the redefined v1 as `1.0.0`. "CodeCompass v1" is
redefined as a *product-validation milestone*: CodeCompass developed
agent-led, validated against real external reference-project work
(Technical Clipper, then Ledgerkit), improved from that evidence,
generalised only as far as evidence justifies, then released after
blank-slate doc reconstruction and an independent audit.

**Phases 39, 40 and 41 are `done` (Stage A of the redefined-v1 roadmap;
42–43 remain).**

- **39** ratified the redefinition: ADRs `decisions/0048`/`0049`
  `Accepted`; `pyproject.toml` `version` → `1.0.0.dev0`; ROADMAP's Stage
  A–F section ratified; Phase 23 Part B superseded; Phases 24/25
  `deferred` (not renumbered).
- **40** made the agent-led model operational: `.claude/agents/` roster
  of 7; `planning/agent-led-workflow.md`; `CLAUDE.md` §8/§1/§5/§6 changes
  approved (gate G4) + applied + mirrored to `CONTRIBUTING.md`. Forced
  fix to `scripts/check_user_docs.py::check_readme_phase_count` — captured
  as candidate learning **L-001**.
- **41** made `planning/learnings/` operational, added the phase-retro
  and per-phase docs-drift-audit closeout mechanisms (`CLAUDE.md` §5
  follow-on amendment + `decisions/0050`), and **ran the agent-led loop
  for real** — `knowledge-curator` (L-001 promoted+logged; L-002/L-003
  retained), `docs-reconstructor` per-phase drift audit (NO DRIFT),
  `roadmap-context-curator`, `release-phase-auditor` (**PASS WITH
  NON-BLOCKING OBSERVATIONS**, 4 advisory items addressed/filed). Retro:
  `planning/retros/phase-41-learning-lifecycle-and-retros.md`.

**No `src/codecompass/` change in any of these phases; no release/tag
(gate G2-b).**

**Next: Phase 42** ([`phase-42-documentation-lifecycle.md`](phase-42-documentation-lifecycle.md))
— the documentation lifecycle: the `docs-maintainer` brief, incremental
`docs/`/`architecture/` upkeep + a milestone closeout gate,
`scripts/check_user_docs.py` link/example/ADR-status checks, and a new
`planning/milestone-closeout-checklist.md`. No gate blocks it.

The `planning/v1-redefinition/` package + `planning/learnings/` (now live)
+ `planning/retros/` + `planning/agent-led-workflow.md` (14 steps) + Stage
A phase plans (`phase-39`…`phase-44`) are the governing plan for this
milestone group.

Everything below this line describes the **foundation** (phases 0-38) and
remains accurate.

Phases 30-38 (doc-graph precision, user-facing docs, docs-sync tooling,
redundancy cleanup) are all `done`.
`codecompass` now: auto-clones every tracked vendor; detects real
project-source usage (vendor- and symbol-level); maps docs/skills/
dependencies/spec-docs/vendor-docs into a SQLite graph with both
mechanical and AI-enriched relationship edges, now with real `(file,
line)` code-usage traversal, typed relation labels, and heading-scoped
doc chunking sharpening both; auto-triggers disclosed, confirmable
batched AI enrichment for usage-proven vendors *and* relationships;
exposes all of it via `codecompass query`, `/discovery`, and generated
Skills; can `undo` itself cleanly; frames chat as secondary. `promote` and
`Depth` are fully retired. Packaging is release-ready (real wheel
re-verified installable in a clean venv after Phase 38's dependency-pin
change; `version` is `1.0.0.dev0` as of Phase 39) but **nothing is
published to PyPI and no tag has been cut — and won't be until the
redefined v1, Phase 67 (gate G2-b).**
`README.md` now documents real setup requirements (Python version, `git`,
`ANTHROPIC_API_KEY`) and a plain free-vs-paid AI enrichment explainer; a new
`ai-docs/` folder gives an agent a capability/boundary overview distinct
from root `CLAUDE.md`'s process rules; a new maintainer-only
`scripts/check_user_docs.py` + `.claude/skills/docs-sync/` mechanically
flags future drift between this repo's own docs and its own code (not
shipped, not a `codecompass` feature). `pyproject.toml`'s 4 runtime
dependencies now carry lower-bound version pins (`decisions/0047`), and
`cli.py`'s query-command boilerplate/`vendor.toml`'s dead `depth` lines
were cleaned up (Phase 38).

## What was just completed

**Phase 41, done** (2026-09-10) — project-learning lifecycle + phase
retros + per-phase docs-drift gate; **first real exercise of the
agent-led loop** (the smoke delegation deferred from Phase 40).
- `planning/learnings/` is operational: new `candidates/` subdir;
  `README.md` marks it live; the `knowledge-curator` brief is finalised
  against the real files and now also mines phase retros. L-001 was
  triaged → **promoted** and logged in `planning/learnings/promoted.md`
  (it records `check_readme_phase_count`'s "highest done phase ≠ product
  completeness" fix + its regression test).
- New `planning/retros/` — `README.md` + `TEMPLATE.md`; every phase from
  here on gets a lead-authored `planning/retros/phase-N-<slug>.md`.
- `CLAUDE.md` §5 gained two DoD conditions (phase retro; independent
  per-phase `docs-reconstructor` drift audit), approved 2026-09-10 and
  mirrored into `CONTRIBUTING.md`; `decisions/0050` records both. The
  §0 diff-approval flow was followed.
- `scripts/check_user_docs.py`: new `Finding.strict` flag (blocking vs
  informational — `--strict` fails only on blocking); four new checks
  (learnings-candidate provenance fields, `promoted.md` consistency,
  stale `evidence-gathering` (info), per-phase retro presence for `done`
  phases ≥ 41) + tests (26 pass). `.claude/skills/docs-sync/SKILL.md`
  notes them.
- `.claude/agents/`: `docs-reconstructor` gains a scoped read-only
  per-phase drift-audit mode (milestone blank-slate mode unchanged);
  `release-phase-auditor` also checks retro + drift audit exist;
  `knowledge-curator` reads retros. `planning/agent-led-workflow.md`
  12 → 14 steps; `agent-led-development.md` / `documentation-lifecycle.md`
  / `proposed-governance-changes.md` updated.
- Agent-led closeout ran: `knowledge-curator` (L-001 → promoted+logged;
  L-002 "curator has no Bash", L-003 "no independent `planning/**` prose
  check" → both `retained`, Phase 47 backstop); `docs-reconstructor`
  per-phase drift audit → **NO DRIFT** (`planning/retros/_drift-audit-phase-41.md`);
  `release-phase-auditor` → **PASS WITH NON-BLOCKING OBSERVATIONS**
  (`planning/retros/_audit-phase-41.md`) — obs 1 (plan Files list) and
  obs 2 (verbatim §5 diff record) addressed this commit; obs 3 (retro
  commit hash) is a follow-up; obs 4 (workflow step inversion when a
  learning blocks verification) filed for GATE DA.
- Verified: `python scripts/check_user_docs.py --strict` clean; full
  `pytest` 532 passed / 1 skipped; `ruff` clean.

**Phase 40, done** (2026-09-09) — agent-led development model operational:
`CLAUDE.md` §8 + §1/§5/§6 changes (gate G4) mirrored into `CONTRIBUTING.md`;
`.claude/agents/` roster of 7; `planning/agent-led-workflow.md`. Forced
`check_user_docs.py` phase-count fix (excludes the redefined-v1 ROADMAP
section) + regression test; captured as L-001.

**Phase 39, done** (2026-09-09) — ratified the v1 redefinition.
`decisions/0048` (redefined v1 = product-validation milestone, not
packaging) and `decisions/0049` (agent-led development model) written and
`Accepted`. `pyproject.toml` `version` `1.0.0` → `1.0.0.dev0` (gate G1).
Gate G2 → **G2-b**: all publishing held until the redefined-v1 release
(Phase 67, first-ever publish, as `1.0.0`). `planning/ROADMAP.md`: the
Stage A–F section ratified; a reframing note added above the dated
"v1.0 scope notes" (left unedited — historical records); Phase 23 row →
"Part A done; Part B superseded"; Phases 24/25 → `deferred` (not
renumbered); `deferred`/`superseded` added to the status legend.
`README.md` Status section reframed. Verified: `pytest` 520 passed /
1 skipped, `ruff` clean, `check_user_docs.py --strict` clean, no `src/`
change, `git tag -l` still empty. `CLAUDE.md` untouched (its changes are
gate G4, Phases 40–42).

**Redefined-v1 planning session** (2026-09-09) — no code, no governance
change. Inspected the full repo, the release/version state (nothing
published; no tags; `v0.1`/`v0.2` never cut; `pyproject.toml` was at
`1.0.0` via Phase 23 Part A), and both proposed reference projects
(`technical-clipper` — TypeScript MV3 extension, **0 runtime deps**, ~7
build-only devDeps; `ledgerkit` — pure Python, **0 runtime deps**, real
context is the `hledger` executable + manuals + journal syntax). Key
finding: CodeCompass's package-source model produces near-empty output for
both real targets, so the current "publish the package tool = v1.0"
definition is a packaging milestone, not a validated-value milestone.

Produced [`planning/v1-redefinition/`](v1-redefinition/): README (overview
+ versioning assessment + risk analysis + human-decision gates), roadmap
(Stages A–F, phases 39–67, each labelled committed/experimental/
conditional), agent-led-development, learning-lifecycle,
documentation-lifecycle, reference-project-protocol, context-quality-
evaluation, ledgerkit-plan, conditional-generalisation, migration,
proposed-governance-changes (a proposed `CLAUDE.md` §8/§5/§1 diff + ADR
drafts 0048/0049 — NOT applied). Plus the `planning/learnings/` scaffold
(README, inbox, TEMPLATE, promoted log) and Stage A phase plans
(`phase-39` … `phase-43`, `phase-44`). `ROADMAP.md` got an additive
"Redefined CodeCompass v1" section.

**Everything below describes Phase 38 and the foundation (phases 0-38),
still accurate.**

**Phase 38, done** — a final-polish pass requested directly by the user
ahead of finishing Phase 23 Part B. Two research passes ran first: a full
roadmap/state review (confirmed the picture above; also caught that an
initial "README status line is stale" claim from that review was itself
wrong — re-checked directly against the real file, already accurate,
dropped), then a targeted 5-category redundancy/dead-code audit (dead
references to retired `Depth`/`promote`/`grounded_description`, duplicate
logic, unused/unpinned dependencies, doc staleness, test-suite overlap).
Three categories were clean; two had real findings, acted on:
- `cli.py`: extracted `_not_found_error()` (was duplicated verbatim across
  `query_vendor`/`query_relations`) and `_graph_session()`, a context
  manager collapsing the open/`if None: return`/try/finally scaffold that
  6 query commands each hand-repeated.
- `vendor.toml`: stripped 4 dead `depth = "surface"` lines (the retired
  `Depth` field, confirmed never read by `config.py`).
- `pyproject.toml`: added lower-bound pins to all 4 runtime dependencies
  (per user decision, over leaving them unpinned) — `decisions/0047`.
  Verified live, not just assumed: the fresh-venv smoke test resolved
  `anthropic` to a real `1.0.0`, a genuine breaking major version
  (`vendor/anthropic/src/MIGRATION.md`); checked all three of
  codecompass's own `_call_anthropic` implementations line-by-line against
  it — none touch any removed/changed API, so the pin is confirmed safe,
  not just SemVer-optimistic.
The word-boundary mention-regex duplication across `doc_mapping.py`/
`skill_scan.py`/`relation_enrichment.py` was investigated and deliberately
left alone — `decisions/0038` already documents this project's preference
for small, single-purpose modules over shared abstractions here.

Verified: `pytest` 520 passed, 1 skipped (Cargo, no toolchain — unchanged,
pre-existing). `ruff check .` clean. Manual smoke tests: `query vendor`/
`query relations` with a bad name still error identically; `query vendors`/
`query symbol` still work; `codecompass check` against this repo itself
runs clean post-`vendor.toml` edit; `python -m build` + fresh-venv install
+ `codecompass --help` re-verified after the pin change. `python scripts/
check_user_docs.py --strict` caught `README.md`'s phase count still
reading "0-37" once ROADMAP's phase-38 row landed — same catch category
Phase 37 hit — fixed inline, re-ran clean. Committed as `feat(phase-38)`
and pushed to `origin/main`.

**Phases 35-36, done** — requested directly by the user (not found via
`/discovery`), added to v1.0's blocking scope alongside the already-`done`
30-33 group. Full detail for phases 20-34 lives in `CHANGELOG.md` and git
history (per this file's own header — the log of how the project got here
isn't repeated here indefinitely).

- **35**: `README.md` restructured with a real **Setup** section (Python
  `>=3.11`, `git` required locally for vendor cloning, `ANTHROPIC_API_KEY`
  as the optional env var gating Phase B — all previously undocumented) and
  a standalone **"AI enrichment vs. no-AI usage"** section reusing
  `examples/README.md`'s real `--budget 0` transcript rather than a
  fabricated example. New `ai-docs/README.md` (capability/boundary overview
  for an agent, each "does NOT do" claim traced directly to the ADR text
  backing it — `decisions/0026`, `0031`, `0038`, `0040`, `0045` — plus 6
  example prompts) and `ai-docs/CLAUDE.md` (a short entrypoint, explicitly
  not a duplicate of root `CLAUDE.md`'s process rules). `CONTRIBUTING.md`'s
  stale "package has real modules" closing line removed.
- **36**: new maintainer-only `scripts/check_user_docs.py` (outside
  `src/codecompass/`, not a shipped feature — confirmed by the user this
  stays local tooling, never a `codecompass` subcommand) mechanically
  checks five things: every CLI command is mentioned in `docs/
  cli-reference.md`; `README.md`'s "phases 0-N" claim matches the highest
  `done` phase in `planning/ROADMAP.md`; `README.md` mentions
  `ANTHROPIC_API_KEY`; every `VendorConfig` field is mentioned in `docs/
  config-schema.md`; every file under `ai-docs/` exists and is non-empty.
  Report-only by default, `--strict` for an exit-code gate; never edits a
  file or calls AI — same mechanical-detection-only posture as `sync.py`/
  `doc_mapping.py`. New `.claude/skills/docs-sync/SKILL.md` instructs an
  agent to run it and apply fixes by judgment, never mechanically.

Verified: `pytest` 505→519 passed (1 skipped, unrelated — the Cargo smoke
test, no toolchain available), all 14 new tests for `check_user_docs.py`
covering every rule's positive/negative path plus `--strict`'s exit code
both ways. `ruff check .` clean. **Confirmed live**: `python scripts/
check_user_docs.py --strict` against this repo's real current state
reports zero findings and exits 0.

Both commits pushed... no — committed locally as `docs(phase-35)` and
`feat(phase-36)`, not yet pushed as of this update (see Next concrete step).
A whole-project `codecompass sync` was then run against this repo itself
(dogfooding): `--budget 0` first (Phase A only, confirmed the new README
Setup/AI-usage sections are already mechanically traced — `query relations
README.md` shows a new "Setup" heading linked to real `anthropic` usage
sites), then, at explicit user go-ahead, `--yes` for real — spent ~$0.02 to
AI-summarize 2 new relationships (`README.md` → the tool Skill, and →
`anthropic`'s new Setup mention), both spot-checked as accurately grounded.

**Phase 37, done** (a third small fix, found via this same dogfooding sync,
not originally planned): `spec_docs._DEFAULT_GLOBS` had no entry for
`ai-docs/`, so `query relations ai-docs/README.md` errored "not found in
context-graph.db" — neither new Phase 35 file was detected as a spec doc at
all. Fixed by adding `"ai-docs/**/*.md"` to the glob set (one line) plus a
regression test. `pytest tests/test_spec_docs.py` — 10 passed. `ruff check .`
clean. **Confirmed live**: re-synced after the fix; both `ai-docs/README.md`
and `ai-docs/CLAUDE.md` now resolve in `query relations` (5 new mechanical
relationships found, not yet AI-enriched — see Next concrete step).

## Next concrete step

**Finish closing out Phase 41.** Code is complete; before the ROADMAP row
flips to `done`, the lead needs to: author `planning/retros/phase-41-*.md`;
dispatch `docs-reconstructor` for the per-phase drift audit; dispatch
`knowledge-curator` to triage any retro-surfaced candidates (L-001 is
already promoted); then dispatch `release-phase-auditor` for the DoD
audit. On a PASS, mark Phase 41 `done` in ROADMAP + this file in the same
commit that carries the CHANGELOG entry (already drafted under
`[Unreleased]`).

**Then: Phase 42** ([`phase-42-documentation-lifecycle.md`](phase-42-documentation-lifecycle.md))
— documentation lifecycle: the `docs-maintainer` brief, incremental
`docs/`/`architecture/` upkeep + a milestone closeout gate, new
`scripts/check_user_docs.py` link/example/ADR-status checks, and a new
`planning/milestone-closeout-checklist.md`. No human-decision gate blocks
it; do not start it until Phase 41 is `done`.

Phase 41 was the first real run of the agent-led loop (the live smoke
delegation deferred from Phase 40) — `knowledge-curator` for L-001 and
`release-phase-auditor` for the DoD check exercise the roster's
frontmatter/tooling for real.

Open items carried from the foundation:

1. **The first-ever publish is Phase 67** (redefined v1, `1.0.0`) — gate
   G2-b holds everything until then. No `twine`, no git tag during Stages
   A–F.
2. **A one-line pointer from root `CLAUDE.md` to `ai-docs/README.md`** —
   still not done; a candidate target change for **Phase 43** (the
   agent-led dogfood run — doubles as a live test of the `CLAUDE.md` §0
   approval flow through an agent-led phase).
3. **Phase 37's fix surfaced 5 new mechanical relationships for
   `ai-docs/README.md`/`ai-docs/CLAUDE.md`** — still "mentioned, not yet
   enriched"; also a Phase 43 candidate target change.

The former open question of whether routing/rollup and MCP (24/25) should
be deferred is now settled: `decisions/0048` marks 24 a Stage C candidate
(conditional on reference-project evidence) and 25 post-redefined-v1, not
renumbered.

**Still outstanding, not a blocker but worth remembering:**
- Once a Rust toolchain is available anywhere in the pipeline,
  `decisions/0014` requires validating the Cargo adapter against real
  `cargo metadata` output and a real crate — currently entirely
  unverified.
- `extract_npm_symbols` (Phase 3) is untested against real-world `.d.ts`
  authoring styles beyond hand-written fixtures.
- `chat.py` has still never been run against the real Anthropic API in
  this environment.
- `staleness.py`'s version parser has no real PEP 440/semver correctness.
- A formal trigger-accuracy evaluation harness for per-vendor Skills
  (`decisions/0013`) remains outstanding.
- Cursor `.mdc` export has no `globs` field — documented future
  refinement, not implemented.
- `doc_chunks`' per-chunk `content_hash` (Phase 32) isn't yet consumed
  for cache-invalidation grain — `select_candidates` still hashes a
  relation's *full* source-doc text against the target's text, unchanged
  since Phase 22. Computed correctly and available for a future phase if
  chunk-grain cache invalidation is ever pursued (noted in
  `decisions/0046`), not wired up now.
- The fenced-code-block fix (Phase 34) only tracks ` ``` `/`~~~` fences,
  not indented (4-space) code blocks — not a gap in practice, since a
  heading regex requires `#` at column 0, which an indented block's
  content can never satisfy.
- `vendor/` exists in this checkout with real, enriched content — a live
  artifact of past validation runs, not a fixture. Still gitignored and
  freely regeneratable (`decisions/0010`).
- A local `.venv/` exists at the project root (gitignored) with
  `codecompass` installed editable, for local testing.
