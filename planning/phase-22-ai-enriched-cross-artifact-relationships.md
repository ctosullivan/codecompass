# Phase 22: AI-enriched cross-artifact relationships

## Scope

Part 2 of the three-way relationship feature (see `planning/v1.0-initial-
release-roadmap.md` and Phase 21). Phase 21 mechanically detects *that* a
spec doc relates to a dependency or a skill (word-boundary presence, zero
cost). This phase asks an AI call to explain, in a sentence or two, *how* —
the same "mechanical detection first, AI enrichment only over what it
proved" gating this project already applies to vendor/symbol enrichment
(`decisions/0031`/`0033`), generalized from vendors to relationships.

**Covered:**

- New table `doc_relation_enrichment` — survives every `rebuild_
  deterministic` call, same intent as `vendor_enrichment`/`symbol_
  enrichment`, but keyed by **plain natural-key strings, not foreign
  keys** (see Design decisions for why this differs from the vendor/symbol
  precedent):
  ```sql
  CREATE TABLE IF NOT EXISTS doc_relation_enrichment (
    id                INTEGER PRIMARY KEY,
    source_doc_path   TEXT NOT NULL,
    target_vendor_name TEXT,
    target_doc_path    TEXT,
    ai_summary        TEXT NOT NULL,
    content_hash      TEXT NOT NULL,
    model             TEXT NOT NULL,
    generated_at      TEXT NOT NULL,
    UNIQUE (source_doc_path, target_vendor_name, target_doc_path)
  );
  ```
  No `ON DELETE CASCADE`, no FK at all — a `rebuild_deterministic` call
  that deletes-and-reinserts `doc_artifacts` (which it does, unlike
  `vendors`/`symbols`) can't cascade away a row keyed purely by path
  strings. `record_relation_enrichment(conn, source_doc_path,
  target_vendor_name, target_doc_path, ai_summary, content_hash, model,
  generated_at)` — the only writer, kept separate from `rebuild_
  deterministic` for the same reason `record_enrichment`/`record_symbol_
  enrichment` are (Phase 10).
- New `graph.py` query `relation_enrichment_candidates(conn) -> list[dict]`
  — every `doc_relations_edges` row (Phase 21) joined to its source/target
  text file paths, plus whether a `doc_relation_enrichment` row already
  exists with a matching `content_hash` (sha256 of the source doc's text +
  the target's text, concatenated — same cache-key *shape* as `enrichment.
  py`'s `symbol_set_hash`, different inputs). `graph.py` doesn't decide
  staleness itself, same division of responsibility `enrichment_
  candidates` already has — the enrichment module diffs the hash.
- New module `relation_enrichment.py` (sibling to `enrichment.py`, not
  folded into it — see Design decisions): `select_candidates`, `plan_
  batches`, `run_enrichment_batches`, `apply_results`, mirroring `enrichment
  .py`'s structure and its batched forced-tool-use call pattern (reuse the
  same Anthropic client setup/retry logic, not reimplemented). Per-item
  input: the target's existing digest text (a dependency doc's
  `technical_description`/Skill's `description`) plus a capped excerpt of
  the spec doc's own text (a fixed character cap, tuned from real output
  quality later — same "start simple, tune from real usage" posture as
  Phase 14's batch-size constant). Output: one sentence or two explaining
  the relationship — e.g. "This section requires calling the Anthropic API
  directly; `vendor/anthropic/CLAUDE.md` documents the retry/backoff
  behav0000r this design assumes."
- `enrichment.py`'s `estimate_cost`/`check_budget` extended to include
  relation-candidate count alongside vendor/symbol candidates — **one
  unified cost disclosure and one `--yes`/`--budget` gate**, not a second
  separate prompt. Preserves MVP spec point 6's consent model without
  doubling the interruption.
- `cli.py`: `query relations <name>` (Phase 21) now shows `ai_summary` when
  a matching `doc_relation_enrichment` row exists, otherwise "mentioned,
  not yet enriched" — same two-state display `query vendor` already uses
  for `has_enrichment`.
- `skill.py`/`/discovery` template: one more line noting AI-enriched
  relationship summaries are available via `query relations`.

**Non-negotiable boundary, stated explicitly because it's easy to get
wrong by default:** the AI-generated summary is written **only** to
`doc_relation_enrichment` (the gitignored graph). It is never written into
the spec doc's own file. Spec docs are the user's own hand-authored
content — codecompass reads them (same as it already reads a consuming
project's source files for usage detection) but has never had, and must
not gain here, any path that edits them. This mirrors the root `CLAUDE.md`
boundary (§0: only touched via presented-diff approval) but is actually
stricter — codecompass has *no* write path to a spec doc at all, approved
or not.

**Explicitly deferred / out of scope:**

- A committed-file cache fallback (the way vendor enrichment survives a
  fresh clone via a hash line inside the committed `vendor/<name>/
  CLAUDE.md`, Phase 14). `doc_relation_enrichment` has no equivalent —
  spec docs are never written to (see boundary above), so there's no
  codecompass-owned file to embed a cache-hash line into. A fresh clone
  re-pays for relationship enrichment once. Accepted for v1: these are
  short summaries over a small, usage-proven candidate set, not full
  vendor digests — much cheaper to regenerate than the description Phase
  14 originally solved this problem for. Revisit only if real cost
  complaints surface.
- Per-item excerpt character budget tuning / `vendor.toml` configurability
  — ship a fixed constant first.
- Enriching Phase 21's deferred bidirectional edges — none exist yet to
  enrich.

## Design decisions

**`doc_relation_enrichment` is keyed by natural-key strings with no FK at
all, unlike `vendor_enrichment`/`symbol_enrichment`'s FK-to-upserted-row
approach.** This is the central design call of this phase, and it departs
from the Phase 10 precedent on purpose. Phase 10 solved "enrichment
survives a rebuild" by upserting `vendors`/`symbols` *by natural key*
instead of delete-and-reinsert, so an FK referencing their `id` stays
valid across a rebuild. The same fix does not transplant cleanly here:
`rebuild_deterministic` deletes and unconditionally reinserts every
`doc_artifacts` row on every call (`DELETE FROM doc_artifacts` with no
upsert branch) — because doc artifacts churn far more than vendors/symbols
do (a spec doc can be renamed, split, or deleted between syncs in a way a
tracked dependency rarely is), switching `doc_artifacts` to upsert-by-path
purely to support this one new table would be a real, higher-risk change
to code four other tables (`documents_edges`, `skill_mentions_edges`,
`routes_via_edges`, and Phase 21's `doc_relations_edges`) already cascade
from. Rejected in favor of the simpler fix: don't reference `doc_
artifacts.id` at all. `doc_relation_enrichment` keys on the same path
strings `graph.py`'s own module docstring already says every row
dataclass prefers ("Row dataclasses reference each other by natural key
... rather than by pre-assigned integer id") — a path surviving a rename
is not this table's problem to solve; a path that disappears just leaves
an orphaned enrichment row that no query ever surfaces (harmless, matches
`vendor_enrichment`'s own tolerance of an eventually-orphaned row if a
vendor is removed from `vendor.toml` outside a rebuild — never actively
pruned by this project's existing code either).

**A separate `relation_enrichment.py` module, not folded into `enrichment
.py`.** Considered adding relationship-batching functions directly into
the existing module. Rejected: `enrichment.py`'s candidate shape (a vendor
plus its used symbols) and this phase's candidate shape (a doc-pair plus
two text excerpts) are different enough that sharing one module's
functions would mean threading a type-discriminated candidate through
every function. A sibling module reusing the *call machinery* (client
setup, retry, forced-tool-use schema pattern) but with its own candidate
type stays closer to this project's existing preference for small,
single-purpose modules (`usage.py`, `doc_mapping.py`, `skill_scan.py`,
`spec_docs.py` are each scoped to one concern already).

## Files

- `src/codecompass/graph.py` — new `doc_relation_enrichment` table,
  `record_relation_enrichment`, `relation_enrichment_candidates`.
- `src/codecompass/relation_enrichment.py` — new module.
- `src/codecompass/enrichment.py` — `estimate_cost`/`check_budget` extended
  to fold in relation candidates.
- `src/codecompass/cli.py` — `query relations` enrichment display; Phase B
  wiring calls `relation_enrichment.run_enrichment_batches` alongside the
  existing vendor/symbol enrichment call.
- `src/codecompass/skill.py`, discovery-command template — one-line
  additions.
- `architecture/overview.md` — "Context graph" and "Cost model" sections
  updated.
- `decisions/` — new ADR for the natural-key-only enrichment table design
  and the "never write to a spec doc" boundary, written at implementation
  time.
- `tests/test_relation_enrichment.py` (new, fixture-mocked API calls per
  `decisions/0016` — no live calls in tests), `tests/test_graph.py`,
  `tests/test_enrichment.py` (cost-estimate extension), `tests/test_cli.py`.

## Verification

- `pytest` — full suite passes, including new/extended cases above,
  specifically including a regression test asserting `apply_results` never
  opens a spec-doc path for writing.
- `ruff check .` — clean.
- Manual, live run against this repo itself (the established "run full
  enrichment on the codecompass project itself" pattern from this
  project's first live validation session): trigger Phase B with real
  relationship candidates present (e.g. `architecture/overview.md`'s
  mechanically-detected mention of `rich`), confirm a real `ai_summary`
  appears via `query relations architecture/overview.md`, and confirm
  `architecture/overview.md`'s file content is byte-identical before and
  after (`git diff` shows nothing) — the concrete proof the non-negotiable
  boundary holds in practice, not just in code review.
