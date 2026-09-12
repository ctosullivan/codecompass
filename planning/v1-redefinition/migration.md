# Migration plan (required output 11)

How CodeCompass's existing, working capabilities stay functional as the
product evolves through Stages A–G. **Prefer migration over rewrite.**

**Amended 2026-09-12** (`realignment-2026-09.md`, gate G11): stage
letters/phase numbers below follow the reordered roadmap (Ledgerkit is
Stage B/D; Technical Clipper is the new Stage F). The licence migration
(MIT → GPL-3.0-or-later, Phase 43d) is planned separately —
`licence-migration.md` — since it is a legal/governance change, not a
capability-preservation one; cross-referenced here for completeness.

## 1. Versioning realignment (Phase 39) — mechanical steps

Gate G2 → **G2-b (hold all publishing until redefined v1)**. So Phase 39
does steps 1–5 only; **no build, no `twine`, no tag, no dated CHANGELOG
section** until Phase 67.

| Step | Action | Reversible? |
|---|---|---|
| 1 | `pyproject.toml`: `version = "1.0.0"` → `"1.0.0.dev0"` (in development toward the 1.0.0 Phase 67 ships — not a phantom `0.4.0` that never gets released) | yes (pre-publish) |
| 2 | `README.md` Status line, `docs/cli-reference.md` header, `ai-docs/` — replace "v1.0.0 in progress / phases 0-38" framing with "phases 0–38 (the foundation) done; CodeCompass v1 redefined as a product-validation milestone, in progress — see `planning/v1-redefinition/`; not yet released" | yes |
| 3 | `ROADMAP.md` — append the Stage A–F milestone table; retitle "v1.0 scope note" blocks → "foundation-release scope note" (wording only); mark Phase 23 row "Part A done; Part B superseded — first publish is redefined v1 (Phase 67)"; mark 24/25 deferred | yes |
| 4 | `CHANGELOG.md` — `[Unreleased]` content stays, **not** promoted to a dated section (G2-b — nothing is released) | n/a |
| 5 | move approved ADR drafts `0048`/`0049` from `proposed-governance-changes.md` into `decisions/` (`Status: Accepted`) | append-only |

The first-ever publish is Phase 67: `1.0.0.dev0` → `1.0.0`, `twine
upload`, `v1.0.0` tag, `[Unreleased]` → dated `1.0.0` section (gate G9).
**PyPI upload is irreversible** — same pause posture the old Phase 23
Part B had.

## 2. Stage A — no `src/` changes

Stage A adds `.claude/agents/`, `planning/` files, `scripts/check_user_docs.py`
extensions, and (gated) `CLAUDE.md` §8. It does **not** touch
`src/codecompass/`. Zero migration risk to the shipped tool.

## 3. Stage C / E — keeping the package/source pipeline working

The capabilities that must not regress, and how each is protected:

| Capability | Module(s) | Protection |
|---|---|---|
| npm / PyPI / Cargo discovery | `discovery.py`, `adapters/` | `kind='package'` stays the default, unchanged code path; adapter interface (`base.py`) untouched unless a new *kind* needs a sibling interface (additive) |
| pinned vendor source clone | `source_resolution.py`, `sync.py` | unchanged; a new dependency kind that isn't cloneable simply doesn't invoke it |
| source usage analysis | `usage.py`, `symbols.py` | unchanged for imports; a new kind (e.g. `executable`) adds a *new* detector (subprocess-call-site scan) alongside, not replacing |
| context graph | `graph.py` | **additive schema only** — new tables / nullable columns; `rebuild_deterministic` is a full rebuild every whole-project sync, so a schema bump is drop-and-recreate for deterministic tables (the established pattern — Phase 17, 21, 27, 32) and `ALTER TABLE ADD COLUMN` for paid-AI tables (Phase 31 pattern) |
| generated AI docs / enrichment | `enrichment.py`, `relation_enrichment.py` | unchanged call shape; new kinds reuse the batched forced-tool-use pattern; determinism boundary held |
| generated Skills / `.mdc` / `/discovery` / routing table | `skill.py`, `commands.py`, `index.py` | unchanged; new kinds either get analogous generated artifacts or are surfaced through `query` only (decided per kind) |
| `query` / `check` / `undo` | `cli.py` | additive subcommands / sections; existing subcommand output stays shape-compatible, or a breaking change goes through gate G8 + an ADR (the `query relations --json` precedent, Phase 30) |
| `chat` | `chat.py` | secondary already (`decisions/0034`); untouched unless a finding demands it |
| `vendor.toml` format | `config.py` | already tolerant of unknown keys (`decisions/0031` legacy `depth=`); a new kind adds an optional field, old files keep parsing |

### Migration mechanics for a schema change (Phase 56/57)

1. New table(s) / nullable column(s) added to `graph.py` schema; `_SCHEMA_VERSION` bumped.
2. `open_graph` migration path: drop-and-recreate for deterministic
   tables (safe — rebuilt every sync), `ADD COLUMN` for enrichment
   tables (preserve paid AI spend).
3. New data populated by a new builder function called from the **same
   two whole-project call sites** every other builder uses
   (`decisions/0025` — `sync <vendor>` and `init --scan` never rebuild).
4. Existing queries unchanged; new queries added.
5. Regression: Phase 59 re-runs the full Ledgerkit task suite — any
   movement in the numbers vs Phase 46 that isn't an improvement is a
   blocker. Phase 61 (Stage F, Technical Clipper) is the separate,
   later cross-ecosystem regression check.

## 4. What "rewrite" would look like, and why to avoid it

A tempting-but-wrong path: introduce `technical_dependency` as the new
root concept and reshape `vendors` / `uses_edges` / everything around it
in one phase. Rejected because: (a) it breaks the phase-per-commit
revertibility property; (b) it puts the entire shipped pipeline at risk
for a generalisation whose exact shape is still being decided at GATE DD;
(c) `graph.rebuild_deterministic` already gives us cheap additive
migration, so there's no technical forcing function for a big-bang.

Stage E is therefore: **add the new concept alongside; point new sources
at it; leave `package` on its existing rails; migrate the *naming* only
at Phase 58 once the new concept has proven itself in Phase 56–57.**

## 5. Rollback story per stage

- **Stage A:** revert the planning/agents commits; `src/` never changed.
- **Stage C:** each improvement is its own phase/commit; Phase 51
  re-evaluation is explicitly allowed to conclude "revert phase 49".
- **Stage E:** each abstraction is its own phase/commit; additive schema
  means reverting a phase = drop the new table + revert the builder;
  `package` path is unaffected throughout.
- **No intermediate release exists (G2-b):** nothing to roll back on
  PyPI; the redefined-v1 `1.0.0` is the first and only published version
  until v1.x.
