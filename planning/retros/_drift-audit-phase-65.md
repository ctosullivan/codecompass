# Drift audit — Phase 65 (architecture + ADR reconciliation)

**Auditor:** `docs-reconstructor`, MODE 1 (per-phase docs-drift audit).
**Diff audited:** `b95078c..HEAD` (7 commits, 28 files changed).
**Verdict: DRIFT — 1 finding** (blocking, isolated, trivially fixable).

## Scope note

This phase is documentation-only apart from 3 docstring-only `src/`
edits (`core.py`, `enrichment.py`, `graph.py` — confirmed no behavioural
change: full `pytest` run on this checkout after the phase's commits
gives **623 passed, 2 skipped**, identical to the plan's stated
pre-phase baseline). Because the phase's own "changes" are almost
entirely to the current-truth docs themselves, this audit's method was:
(1) spot-check factual claims in the new/rewritten `architecture/*.md`
and `docs/**` files directly against real `src/codecompass/` and real
repo state (not against Phase 64's proposal or `docs-maintainer`'s own
summary), (2) manually follow every internal link between the new/
changed files plus run the mechanical link checker, (3) grep `README.md`
and `ai-docs/` for stale references to anything Phase 65 moved/renamed,
(4) confirm `docs/domain/quick-reference.md` is additive only, not an
edit to any of the 19 concept pages.

I did **not** re-derive or second-guess Phase 64's own blank-slate
proposal content (out of scope for this audit — that was Phase 64's own
`docs-reconstructor` job) or re-litigate the reconciliation table's
retain/rewrite/split *decisions* themselves (a lead + `docs-maintainer`
judgment call, not a drift question) — only whether the *resulting text*
is accurate.

## Method detail / facts verified (representative sample, not exhaustive)

Checked and found **accurate**, against real `src/codecompass/` and a
real generated checkout of this repo itself:

- `architecture/core-data-model.md`: `core.py` is 103 lines; every
  dataclass's line-range citation (`Ecosystem` 13-19, `VendorConfig`
  22-34, `RepositoryLocation` 37-49, `DepNode` 52-63, `VendorDigest`
  66-103) matches the real file; `Symbol` at `symbols.py:26-47` exact.
- `architecture/adapter-interface.md`: `EcosystemAdapter` contract
  (`base.py:25-97`), `_run_json` (`base.py:100-138`), dispatch table
  (`adapters/__init__.py:18-31`) — all confirmed by direct read.
- `architecture/context-graph-schema.md`: schema version `"9"` matches
  `graph.py`'s `_SCHEMA_VERSION`; `doc_artifacts.kind`'s 7-value CHECK
  set and `.origin`'s 6-value CHECK set both match the literal SQL in
  `graph.py` exactly, value-for-value.
- `architecture/sync-and-enrichment-pipeline.md`: `sync_vendor`
  (`sync.py:102`), `rebuild_project_graph` (`sync.py:234`), `_bootstrap`
  (`cli.py:102`... confirmed at real absolute line 102),
  `_maybe_run_enrichment` (`cli.py:153`), `_refresh_generated_artifacts`
  (`cli.py:219-238`, exact end line confirmed) all match; model name
  `claude-haiku-4-5-20251001` matches all four real call sites
  (`chat.py`, `cli.py`, `enrichment.py`, `relation_enrichment.py`).
- `docs/quickstart.md`: the worked `codecompass query vendors` table
  (anthropic/pipdeptree/rich/typer, versions, Used/Enriched columns) was
  checked directly against this repo's real `vendor.toml` and
  `context-graph.db` — matches exactly, including which vendors show
  `Used: yes`/`no`.
- `docs/protocol-adapter/wire-protocol.md`: `PROTOCOL_VERSION = 1`,
  `CAPABILITIES` 4-tuple, `_SHUTDOWN_TIMEOUT_SECONDS = 5.0`, and every
  `external_process.py` line-number citation match the real file
  exactly; submodule URLs match `.gitmodules` exactly; both submodules'
  checked-out tags (`v0.1.0-1-g...`) confirm the version-compatibility
  matrix's `0.1.0` entries are current.
- `docs/developer/writing-an-adapter.md` and
  `docs/developer/haskell-adapter-submodules.md`: checklist, registration
  snippet, and submodule clone/build instructions all match real
  `adapters/__init__.py`, `core.py`, `discovery.py` structure.
- `decisions/0061` (`0019` superseded by `0035`): confirmed
  `grounded_description.py` is genuinely absent from `src/codecompass/`
  and `0019`'s described mechanism (promote-time, `Depth.FULL`-gated
  generation) has no live code path — the supersession claim is
  accurate, and neither ADR's original body was edited (append-only
  convention honoured).
- `docs/domain/quick-reference.md`: `git diff --name-status` confirms
  this phase touched only `docs/domain/README.md` (index pointer,
  additive) and added `docs/domain/quick-reference.md` — none of the 19
  `docs/domain/concepts/*.md` pages were edited. The new file's own
  frontmatter (`status: derived ... no new domain content, no separate
  domain-owner review`) is an accurate self-description.
- Mechanical check: `python scripts/check_user_docs.py --strict` → no
  findings. `python scripts/check_knowledge_base.py` → no findings.

## Finding (blocking)

**`architecture/module-map.md:11`** — self-contradictory module count
for the `adapters/` package.

> `src/codecompass/` is 23 top-level modules plus a **5-module**
> `adapters/` package (8,624 lines total).

Real `src/codecompass/adapters/` (excluding `__init__.py`) has **6**
modules, not 5: `base.py`, `cargo.py`, `external_process.py`,
`haskell.py`, `npm.py`, `python.py` — confirmed by direct `ls`. This
count contradicts the very next section of the same file (lines 38-41),
which correctly lists all six: "the `EcosystemAdapter` contract [i.e.
`base.py`] and four concrete adapters (`npm.py`, `python.py`, `cargo.py`,
`haskell.py`) plus the generic external-process client
(`external_process.py`)" — that's 1 + 4 + 1 = 6, not 5. So the page
disagrees with itself, not just with reality.

This is user/contributor-facing (anyone reading the module map to
understand package shape gets a wrong headline number two lines before
the correct one), but trivially fixable — a one-word/one-digit edit
(`5-module` → `6-module`). Not a design or behavioural claim, purely a
count error. Total line count "8,624" is also slightly off (real total
excluding `__init__.py` files is 8,592; including both package
`__init__.py` files is 8,623) — off by one either way, almost certainly
a stale/rounded figure from an earlier pass; non-blocking on its own,
but flagging alongside the module-count fix since both are in the same
sentence and a re-count would naturally fix both together.

## Everything else checked and found consistent

- Every internal link between the new/changed `architecture/*.md` and
  `docs/**` files that I followed manually resolves to the stated
  heading/file (mechanical link checker agrees: zero findings).
- `docs/external-adapters.md` is now a thin, accurate index page — the
  content it used to hold moved to
  `docs/developer/haskell-adapter-submodules.md`,
  `docs/protocol-adapter/wire-protocol.md`,
  `docs/developer/writing-an-adapter.md`, and
  `docs/protocol-adapter/integrating-a-new-external-adapter.md`; all
  four links from the index resolve, and `architecture/overview.md`'s
  and `architecture/adapter-interface.md`'s own pointers into
  `docs/external-adapters.md` still land somewhere true (one extra hop
  through the new index, not stale).
- `README.md` and `ai-docs/{README.md,CLAUDE.md}` (untouched by this
  phase) — grepped for `architecture/overview.md` references and
  section-anchor references (`overview.md#...`): none found pointing at
  a section that moved out of `overview.md` or was renamed. README's
  "How it works" summary sentence (data model / ecosystem adapters /
  tree generation / usage-driven enrichment / the context graph /
  generated Skills / consumption modes / staleness / chat REPL) still
  matches `overview.md`'s remaining table of contents — every one of
  those topics still has a heading in the post-split `overview.md`
  (as a current-state summary plus a pointer into the relevant
  companion file), so this sentence isn't stale.
- `docs/config-schema.md`'s trim (removing the `context_path`/`depth`
  historical narrative in favor of a one-line pointer to
  `decisions/0031`) — the retained sentence and the linked ADR both
  check out.
- `docs/cli-reference.md`'s only change (a 3-line pointer to the new
  `quickstart.md`) — link resolves, `quickstart.md` exists.

## Domain-claim staleness check

`docs/domain/quick-reference.md` is new but does not itself constitute a
domain-claim staleness candidate — it is a direct-quote compression of
`glossary.md` (self-declared, verified: every row is traceable to an
existing `glossary.md`/`concepts/*.md` sentence), not new domain content
and not an edit to a concept page's own references block.

Checked whether anything else in this phase's diff touches a file/
symbol/behaviour cited in any `docs/domain/concepts/*.md` page's own
references block: the phase's only `src/` edits are docstring-only, in
`core.py`, `enrichment.py`, `graph.py` — none of the docstring wording
changed touches a symbol or file *path* a concept page cites (concept
pages cite file/symbol identity, not docstring prose). No new staleness
candidates found. This matches `domain-skeptic`'s own parallel Phase 65
freshness-reconciliation pass (`planning/retros/_domain-freshness-reconciliation-phase-65.md`),
which independently found nothing to flag since Phase 63D's approval.
