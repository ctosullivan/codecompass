# Proposal: add a `model` provenance column to `symbol_enrichment`

Status: **investigation / proposal only — no code changed.** Written in
response to a direct ask to investigate and propose a fix; this is not a
`planning/phase-N-*.md` plan file and does not itself start
implementation (`CLAUDE.md` §1). If the proposed approach is accepted, it
still needs a real phase plan, a `planning/ROADMAP.md` row, and to move
through the normal DoD gate (`CLAUDE.md` §5) before landing.

## 0. This is already a tracked, known gap — not a new finding

Before writing this up as if it were newly discovered: it isn't. This
exact gap was already surfaced by `domain-skeptic` during Phase 63D
(2026-09-23) and is recorded as **`L-031`** in
`planning/learnings/inbox.md:923-1004`, promoted into
`planning/ROADMAP.md`'s "Future-improvement backlog (unscheduled)" table
(`planning/ROADMAP.md:387`), status `not started`. It is also documented
as a live "Counterexample" in the domain corpus at
`docs/domain/concepts/provenance.md:72-88` and referenced from
`docs/domain/open-questions.md`, `docs/domain/concepts/observation.md`,
and `docs/domain/concepts/evidence.md`.

What this document adds beyond L-031's existing note: a fuller trace of
the actual write path (who produces `symbol_enrichment` rows today, and
under what model), a concrete migration design following this
codebase's own established pattern, and an explicit list of what stays
open even after the column is added. L-031 already names the right
migration precedent; this document works out the details and the edge
cases.

## 1. The gap, confirmed directly against the code

`src/codecompass/graph.py:164-201` defines all three enrichment tables.
`vendor_enrichment` and `doc_relation_enrichment` both carry a
provenance column:

```sql
-- vendor_enrichment (graph.py:164-174)
model                   TEXT NOT NULL,

-- doc_relation_enrichment (graph.py:190-201)
model              TEXT NOT NULL,
```

`symbol_enrichment` does not:

```sql
-- graph.py:176-181
CREATE TABLE IF NOT EXISTS symbol_enrichment (
  id           INTEGER PRIMARY KEY,
  symbol_id    INTEGER NOT NULL UNIQUE REFERENCES symbols(id) ON DELETE CASCADE,
  purpose      TEXT NOT NULL,
  generated_at TEXT NOT NULL
);
```

The sole writer, `graph.record_symbol_enrichment` (`graph.py:1544-1561`),
has no `model` parameter and its `INSERT` statement has no `model`
column to populate. No `SELECT`/`JOIN` anywhere in `src/codecompass/`
reads `symbol_enrichment` back at all (confirmed by grep — the only
matches are the `CREATE TABLE`, the writer, docstrings, and cascade
comments), so today this is a write-side gap with no read-side symptom
yet — but it becomes a real problem the moment anything needs to
distinguish rows by producer, which is exactly what's about to happen
(see §3).

## 2. Why the asymmetry exists — traced through the actual call sites

**`vendor_enrichment.model`** is populated in
`enrichment.py:410-420` (`apply_results`), passed the module constant
`_MODEL = "claude-haiku-4-5-20251001"` (`enrichment.py:43`). Confirmed
via `git log -p -S "_MODEL = " -- src/codecompass/enrichment.py` that
this constant has never changed since it was introduced in Phase 14
(`dc41f13`) — there is exactly one literal value it has ever held.

**`symbol_enrichment` rows are produced in the exact same function, the
same loop iteration, from the same batched-API `result` object**
(`enrichment.py:422-427`):

```python
graph.record_enrichment(conn, vendor_row["id"], ..., model=_MODEL, generated_at=generated_at)
symbol_ids_by_name = {symbol["name"]: symbol["id"] for symbol in profile["symbols"]}
for symbol_name, purpose in result.symbol_purposes.items():
    symbol_id = symbol_ids_by_name.get(symbol_name)
    if symbol_id is None:
        continue
    graph.record_symbol_enrichment(conn, symbol_id, purpose, generated_at)
```

So the model that produced a given `symbol_enrichment` row is **already
sitting in a local variable (`_MODEL`) at the exact call site that writes
the row** — this was never a "we don't know the value" gap, only a "the
column and the plumbing to carry it weren't added" gap. This makes the
fix mechanical, not investigative.

**`doc_relation_enrichment.model`** additionally has a *second* real
producer today: `relation_enrichment.apply_results` (`relation_enrichment.py:506-544`)
accepts a `model: str = _MODEL` keyword, and `cli.py`'s `enrich apply`
command (`cli.py:1108-1180`, wired per `decisions/0054`, Phase 52) calls
it with `model=f"agent:{agent}"` for agent-authored rows. This is the
precedent `decisions/0054` leans on when it asserts (§Decision, point 1)
that "`vendor_enrichment.model` / `symbol_enrichment` (via its shared
write path) / `doc_relation_enrichment.model` are already `TEXT NOT
NULL` columns recording provenance" — **that parenthetical is factually
wrong for `symbol_enrichment`** (confirmed directly against
`graph.py:176-181` and `record_symbol_enrichment`'s signature, same as
`domain-skeptic`'s L-031 finding). There is no join that recovers this
transitively either: `symbol_enrichment.symbol_id → symbols.vendor_id →
vendor_enrichment.vendor_id` would let you *guess* a symbol's producer
from its vendor's current `vendor_enrichment.model`, but that guess can
be wrong — see §4.3.

Separately: `decisions/0054`'s hard boundary (§4) explicitly anticipates
agent-driven enrichment reaching "`uses_edges`, symbol-level" rows, i.e.
a second producer for `symbol_enrichment` was already imagined when that
ADR was written. In the actual code today, `enrich apply` only ever
calls `relation_enrichment.apply_results` — there is no agent-driven
writer for `symbol_enrichment` yet. So right now there is exactly **one**
real producer for this table (the automated batched-API path), which
somewhat lowers the urgency, but the ADR's own stated intent is for a
second producer to exist eventually, and that can't be built cleanly
without this column existing first.

## 3. Proposed fix

### 3.1 Schema

Add `model TEXT NOT NULL` to `symbol_enrichment`, matching the other two
tables' column name and type exactly (no new naming convention):

```sql
CREATE TABLE IF NOT EXISTS symbol_enrichment (
  id           INTEGER PRIMARY KEY,
  symbol_id    INTEGER NOT NULL UNIQUE REFERENCES symbols(id) ON DELETE CASCADE,
  purpose      TEXT NOT NULL,
  model        TEXT NOT NULL,
  generated_at TEXT NOT NULL
);
```

### 3.2 Migration for existing on-disk databases

Follow `_migrate_symbols_export_kind_note_columns`'s exact pattern
(`graph.py:473-511`) — the closest real precedent, both because it's the
most recent enrichment-adjacent migration and because L-031 itself names
it: a new, self-contained, idempotent function,
`_migrate_symbol_enrichment_model_column`, checking
`PRAGMA table_info(symbol_enrichment)` directly (not
`meta.schema_version`), doing `ALTER TABLE symbol_enrichment ADD COLUMN
model TEXT NOT NULL DEFAULT '<historical literal>'` only if the column
is absent, called from `open_graph` (`graph.py:601-616`) alongside the
other four migrations, before `init_schema`. `_SCHEMA_VERSION` bumps
"9" → "10" per this file's established one-bump-per-schema-change
convention (confirmed by `git log`: every prior column addition bumped
this constant, even ones — like Phase 62's `export_kind`/`note` — that
touched a table other than the one `_migrate_doc_artifacts_constraints`
gates on). Bumping it is not free: it also triggers that function's
drop-and-recreate of `doc_artifacts`/`documents_edges`/
`doc_relations_edges` on every existing database's next `open_graph`
call — harmless by that function's own docstring (those tables are
fully rewritten by the next `rebuild_deterministic` regardless), and
that's exactly what happened for the unrelated Phase 62 change too, but
worth stating explicitly rather than treating the version bump as a
side-effect-free formality.

### 3.3 Writer signature

`record_symbol_enrichment(conn, symbol_id, purpose, model, generated_at)`
— add the parameter in the same position `record_enrichment` and
`record_relation_enrichment` use relative to `generated_at` (model
before `generated_at` in both existing signatures), and thread it
through the `INSERT ... ON CONFLICT DO UPDATE` the same way `purpose`
and `generated_at` already are.

### 3.4 Call site

`enrichment.py:427`'s one call becomes:

```python
graph.record_symbol_enrichment(conn, symbol_id, purpose, _MODEL, generated_at)
```

This is the only production call site today (confirmed by grep — no
other module calls `record_symbol_enrichment`). Per `CLAUDE.md` §1's
rule for a phase that changes an existing function's behavior at a real
call site, the phase's verification step must exercise this exact call
path, not just `record_symbol_enrichment` in isolation — the existing
test at `tests/test_enrichment.py` (`~line 505-570`, asserts
`apply_results` writes `symbol_enrichment.purpose` correctly for the
`turndown` fixture) already exercises this call site end-to-end and is
the natural place to extend the assertion to also check
`symbol_enrichment.model == "claude-haiku-4-5-20251001"`.

## 4. Open questions — genuinely unsure, not clear-cut

### 4.1 Backfill value for pre-existing rows

Because `_MODEL` has never changed since Phase 14 and
`symbol_enrichment` has exactly one historical producer, backfilling
every pre-existing row to the literal `"claude-haiku-4-5-20251001"` (not
a live import of `enrichment._MODEL`, which could itself change in the
future and would then make the migration retroactively wrong) is
factually accurate for every row that predates this migration, on any
database that has ever existed. I'm fairly confident this is correct,
but it does mean hard-coding a historical literal into `graph.py`
forever — the same shape of decision `_migrate_symbols_export_kind_note_columns`
made for `export_kind DEFAULT 'export'`, so there's real precedent, but
it's still a judgment call someone should sign off on rather than treat
as mechanical.

An alternative is backfilling to `NULL` and dropping the `NOT NULL`
constraint (the same choice `_migrate_doc_relation_enrichment_relation_label`
made for `relation_label`, "filled on next natural re-enrichment cycle"
rather than reconstructed). That's more conservative — it doesn't assert
a historical fact via a migration default — but it means *this* column,
unlike `vendor_enrichment.model`/`doc_relation_enrichment.model`, would
have a "value or NULL" shape rather than always being populated, which
somewhat undercuts the "matches the other two tables exactly" goal that
motivated the fix in the first place. I lean toward the literal-backfill
approach given how confident the git-history check makes me, but I
would not call this settled.

### 4.2 Should `decisions/0054` get a correction?

`decisions/0054`'s Decision §1 states the "already `TEXT NOT NULL`"
claim for all three tables' provenance columns, which is now
demonstrably false for `symbol_enrichment` as written (it was false
when written too, per L-031's finding, not something this fix would make
false). `CLAUDE.md` §2 makes ADRs append-only — "a reversed decision
gets a *new* numbered file that supersedes the old one; never edit a
past ADR's original content." A schema column being added doesn't
"reverse" 0054's actual decision (agent-driven enrichment as a second,
non-authoritative producer, distinguished by a `model`-style column) —
it just makes the parenthetical's premise true where it was previously
false. Whether that warrants (a) a new superseding ADR, (b) a lighter
non-ADR errata note somewhere, or (c) nothing beyond the fix itself
making the sentence retroactively accurate, is explicitly called out in
L-031's own curation note as "an editorial call for whoever owns
`decisions/*.md` (the lead), not something this future-improvement
promotion resolves or should be blocked on." I'm surfacing it again here
rather than deciding it.

### 4.3 Does this fix's existence quietly invite a *wrong* transitive-join shortcut?

Once `vendor_enrichment.model` and `symbol_enrichment.model` both exist,
it will be tempting for some future reader to assume they're always
equal for symbols belonging to the same vendor and skip joining
`symbol_enrichment` directly. They are *not* guaranteed equal:
`apply_results` only calls `record_symbol_enrichment` for symbol names
actually present in `result.symbol_purposes` for that batch
(`enrichment.py:423-427`) — a vendor can be re-enriched (updating
`vendor_enrichment.model`/`generated_at`) without every one of its
symbols being redescribed in that same batch, leaving some
`symbol_enrichment` rows with an older producer/timestamp than their
vendor's current row. This is exactly why the column needs to live on
`symbol_enrichment` itself rather than being left as "recoverable via
join" — but it's worth stating explicitly in whatever docstring/architecture
update lands with the fix, so nobody "simplifies" it away later.

### 4.4 Should this also finally wire up the agent-driven producer for symbols?

`decisions/0054` explicitly anticipated a second, agent-driven producer
reaching "`uses_edges`, symbol-level" rows, using the same
`agent:<name>` convention. Today `enrich apply` doesn't do this — it's
relation-enrichment-only. Adding the `model` column is a prerequisite
for that but doesn't itself require building it. I'd treat that as a
separate, later piece of work (possibly its own future-improvement
entry) rather than scope creep onto this fix, but flagging it since an
implementer reading this proposal might reasonably wonder why the ADR's
"symbol-level" mention isn't being addressed at the same time.

### 4.5 Is a CLI/query surface expected once the column exists?

Confirmed by grep: **nothing** currently displays `model` from any of
the three enrichment tables through `codecompass query` — `vendor_profile`/
`symbol_profile` (the functions backing `query vendor`/`query symbol`)
read `symbols.purpose`/`vendors.*` directly and never join any
enrichment table at all; `vendor_enrichment`'s AI content is consumed
only by `claude_md.update_description_section`/`skill.write_vendor_skill`
to render `CLAUDE.md`/Skill files, not by any query command. So adding
`symbol_enrichment.model` with no accompanying display change is
consistent with the existing (lack of) precedent for the other two
tables' `model` columns — I don't think this fix needs to add a display
surface to be complete, but it's a design choice worth naming rather
than assuming silently.

## 5. Blast radius — files that would need touching

- `src/codecompass/graph.py` — schema (§3.1), new migration function
  (§3.2), `open_graph`'s migration call list, `record_symbol_enrichment`
  signature (§3.3), module docstring/comments that currently describe
  `symbol_enrichment` as having no provenance column.
- `src/codecompass/enrichment.py` — the one call site (§3.4).
- `tests/test_graph.py` — extend or add: a migration test mirroring
  `test_open_graph_migrates_pre_phase_62_symbols_schema_preserves_enrichment`
  (`tests/test_graph.py:1116-1182`) for the new column plus backfill
  value, an idempotency test mirroring
  `test_open_graph_symbols_migration_is_idempotent`, and a
  `record_symbol_enrichment` unit test asserting the new parameter
  round-trips.
- `tests/test_enrichment.py` — extend the existing `apply_results`
  end-to-end test (~line 505-570) per §3.4's CLAUDE.md §1 requirement.
- `architecture/context-graph-schema.md` — the `symbol_enrichment` bullet
  (currently lines 94-96) needs its column list and "written only by"
  description updated; same-commit per `CLAUDE.md` §2.
- `docs/domain/concepts/provenance.md` — its "Counterexample" section
  (lines 72-88) documents the *current* asymmetry as a fact; once fixed,
  this becomes stale and needs updating or retiring (it's part of the
  Phase 63D domain corpus, not `docs/` proper, but it's still
  current-truth content a `docs-reconstructor` audit would flag).
  `docs/domain/open-questions.md`, `concepts/observation.md`, and
  `concepts/evidence.md` also reference this gap and likely need at
  least a pointer update.
- `decisions/0054-...md` — see §4.2; no change is forced, but the lead
  should make an explicit call rather than this being silently
  overlooked.
- `planning/ROADMAP.md` — L-031's backlog row (`planning/ROADMAP.md:387`)
  gets removed in the same commit a real phase row/plan file is added
  for this work, per that file's own "How this file is kept in sync"
  section.
- `CHANGELOG.md` — an `[Unreleased]` entry, per `CLAUDE.md` §3.

## 6. Process note (not part of the technical proposal)

Per `CLAUDE.md` §1, actually implementing this requires a
`planning/phase-N-<name>.md` plan file (naming the exact verification
test at the real call site, per §1's own explicit rule) and a
`planning/ROADMAP.md` row added in the same commit, before any code
changes — this document is deliberately not that plan file. This also
looks like a small, low-risk, mechanical, single-column additive
migration with clear precedent (§3.2) — a plausible "trivial phase"
candidate for `CLAUDE.md` §5's lighter DoD path (explicit lead
confirmation in place of a full `release-phase-auditor` pass), but
that's the lead's call to make when it's actually scheduled, not
something this investigation should presume.
