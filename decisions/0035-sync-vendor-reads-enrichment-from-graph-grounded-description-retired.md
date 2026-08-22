# 0035. `sync_vendor` reads enrichment from the graph; `grounded_description.py` retired

## Status

Accepted

## Context

Implementing Phase 16 (retire `Depth`, `planning/phase-16-retire-depth.md`)
surfaced that `Depth` was not, in fact, fully behaviorally inert after
Phase 15 as `decisions/0031`/`0033` and Phase 15's own plan assumed.
Four files still gated real behavior on it: `sync.py`'s `sync_vendor`
(`if config.depth is Depth.FULL and repo_root is not None:
generate_grounded_description(...)`), `claude_md.py`'s
`_render_description_section` (`if digest.config.depth is not
Depth.FULL: return None`), and `grounded_description.py`'s
`check_budget`. `enrichment.py` (Phase 14) also constructs a
`VendorConfig(..., depth=Depth.FULL)` placeholder in `apply_results`,
noting `Depth` isn't retired until Phase 15/16 — but Phase 14's own plan
said `grounded_description.py` "is only actually deleted once Phase 15
rewires `cli.py`/`sync.py` off it entirely," and Phase 15's plan never
actually scoped that rewiring — it scoped only `index.py`/`skill.py`'s
*display* logic. This was a real gap between the two phases' plans, not
a deliberate deferral.

Investigating this surfaced a second, more serious problem, already
shipped on `main` as of Phase 15: `sync_vendor` — called by `sync_all`
for *every* tracked vendor on a whole-project `sync`, not just newly
discovered ones — rebuilds each vendor's `CLAUDE.md` from scratch via
`render_vendor_claude_md(digest)`, and the `VendorDigest` it builds never
carries any of Phase B's enrichment output (that data lives in
`vendor_enrichment`/`symbol_enrichment`, written by
`enrichment.apply_results` via a *separate*, targeted
`claude_md.update_description_section` call, never fed back into
`sync_vendor`'s own digest-construction path). Since nothing in the
current, `promote`-free flow ever sets a vendor's `vendor.toml` `depth`
to `FULL`, `_render_description_section`'s gate returns `None` for every
enrichment-path vendor on every subsequent whole-project `sync` —
silently erasing the Description section Phase B just wrote, on the very
next ordinary `sync` run.

## Decision

`grounded_description.py` is retired — deleted, not just orphaned.
`sync_vendor` no longer calls it. Instead, `sync_vendor` looks up this
vendor's current enrichment record from the context graph
(`graph.vendor_profile`, read-only, no side effect) *before* building its
`VendorDigest`, and populates `technical_description`/
`conversational_overview`/`action_pointer_file`/`action_pointer_note`
from it when present. `claude_md._render_description_section`'s gate
drops the `Depth` check entirely, falling back to its own pre-existing
"nothing to show" pattern: `if not digest.technical_description: return
None`. This makes a `CLAUDE.md` regeneration idempotent with respect to
enrichment — re-running `sync` (whole-project or single-vendor) always
reproduces the *current* enrichment content from the graph, the same
source of truth `enrichment.apply_results` already writes to, rather than
either gating on a field nothing sets anymore or requiring `sync_vendor`
to somehow preserve file content it isn't re-deriving.

This absorbs into Phase 16 (retire `Depth`) rather than becoming its own
phase — the two are the same underlying problem (real code still
depending on `Depth` for behavior, discovered only once actually trying
to delete it), and Phase 16 was already going to touch `sync.py`'s
`Depth` references regardless.

## Alternatives considered

- **Have `enrichment.apply_results` also write the full deterministic
  digest fields it doesn't have** (api_surface, side_effects, trees),
  reconstructing a complete `VendorDigest` so `sync_vendor` never needs
  to. Rejected — `apply_results` deliberately never re-derives
  deterministic data it didn't just recompute (`decisions` around Phase
  14's minimal-digest design for Skill generation already established
  this posture); duplicating that logic here would mean two independent
  paths that can construct a `CLAUDE.md`, rather than one.
- **Leave `_render_description_section` gated on some new field instead
  of `Depth`** (e.g. a boolean `is_enriched` carried on `VendorDigest`).
  Rejected as unnecessary — `technical_description`'s own truthiness
  already means exactly "is there enrichment content to show," the same
  test the function already uses as its second check; adding a redundant
  first flag would just be another way to say the same thing.

## Consequences

- `grounded_description.py` and `tests/test_grounded_description.py` are
  deleted in Phase 16, not left as dead code.
- `sync_vendor` gains one new, read-only graph lookup per vendor per
  sync — cheap (a local SQLite read), and consistent with `check`/`index`
  already reading the graph read-only for display purposes.
- The `**Depth:**` metadata line in `CLAUDE.md` disappears (already
  planned, `decisions/0031`) with no further consequence, since nothing
  else in this render path depends on it once the section-gate no longer
  does.
- `enrichment.py`'s `apply_results` no longer needs its `Depth.FULL`
  placeholder `VendorConfig` construction (`decisions/0031` already made
  this value meaningless; Phase 16 removes the field it was set on
  entirely) — simplifies to a plain `VendorConfig(name, ecosystem)`.
