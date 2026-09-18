---
status: VERIFIED
feature: doc-origin-pinned-reference
context_gap: CG-005
approved_by: "project owner (lead standing in for this dogfooding run — see retro)"
approved_at: "2026-09-18T00:00:00Z"
verified_at: "2026-09-18T00:00:00Z"
---

# Design: a `doc_artifacts.origin` value for externally-sourced, pinned reference material

## 1. Feature purpose and concepts

`doc_artifacts.origin` is supposed to record where a documentation
artifact indexed by CodeCompass actually came from (`OBS-DOCORIGIN-001`,
`CG-005`). Today it cannot distinguish a project's own hand-authored
docs from external reference material that a tool pinned at a specific
upstream commit and materialized into the project's tree — both currently
read `origin='project'` (`EV-DOCORIGIN-001`, `EV-DOCORIGIN-002`). The
concrete real-world instance driving this research is the six
`hledger-tag-query-*.md` files under
`planning/reference-projects/ledgerkit/reference-experiment/extracted/`:
upstream hledger manual text and `hledger-lib` source excerpts, pinned at
commit `33fa849e7ae841968bd21c427094c4fb4a4ec38d`, never authored by
Ledgerkit or CodeCompass (`CG-005`, `OBS-DOCORIGIN-001`). This is the
knowledge base for CodeCompass Phase 54c's primary proving case; the
underlying problem statement is `CG-005` in
`planning/context-gaps/inbox.md:267-363`.

**Lifecycle note (updated):** the research phase (Observation, Evidence,
Claim, Derivation records) is unchanged from the prior version of this
document. Since then, the project's Phase 54c user-review gate ran (the
lead standing in for the user/project-owner role for this dogfooding run,
disclosed explicitly — `DEC-DOCORIGIN-001`), producing one Decision
(`DEC-DOCORIGIN-001`) and three ratified Requirements
(`REQ-DOCORIGIN-001`, `REQ-DOCORIGIN-002`, `REQ-DOCORIGIN-003`). The two
open questions the prior version of this document flagged in §9 are now
resolved by that Decision; this document has been regenerated in full
against the corrected knowledge base rather than hand-patched, per this
role's own rule. §9 below preserves an honest record of what was
unresolved and how it was resolved, rather than silently deleting the
history of the open question.

## 2. Observed current behaviour

- `doc_artifacts.origin` is a closed, five-value CHECK enum
  (`codecompass_tool`, `codecompass_vendor`, `third_party`, `project`,
  `vendor_upstream`), unchanged since Phase 27, with no value
  distinguishing hand-authored project content from externally-pinned,
  tool-ingested content (`EV-DOCORIGIN-001`, `OBS-DOCORIGIN-002`).
- `src/codecompass/spec_docs.py::scan_spec_docs` assigns
  `origin="project"` unconditionally — a literal string constant, no
  branch of any kind — to every file it matches via the `dev-docs/**/*.md`
  glob (and its sibling default globs) (`EV-DOCORIGIN-002`,
  `OBS-DOCORIGIN-003`). The only signal this function uses to decide
  whether a file becomes a `spec_doc` row at all is its path (glob +
  prune/exclude rules); nothing about a matched file's *content* affects
  the `origin` it receives (`EV-DOCORIGIN-002`).
- `_extract_title` (used for the row's display name, not its origin)
  only searches for a level-1 ATX heading or falls back to the filename
  stem; a YAML frontmatter block at the top of a file is inert to it —
  frontmatter lines don't match the H1 regex, so title extraction falls
  through to the body's real heading or the stem, exactly as for any
  other file (`OBS-DOCORIGIN-003`, `DE-DOCORIGIN-002`). Nothing in
  `spec_docs.py` reads YAML frontmatter today.
- The real ingested files each already carry a uniform, mechanically
  parseable YAML frontmatter block (`reference`, `source_url`,
  `requested_ref`, `resolved_commit`, `fetch_method`, `path`, `lines`,
  `content_hash`, `extracted_at`) distinguishing them from ordinary
  hand-authored prose — but this signal exists only in the ingested
  files themselves, not in anything CodeCompass's sync path reads
  (`EV-DOCORIGIN-006`, `OBS-DOCORIGIN-007`).
- The documented path that gets this material into a project
  CodeCompass indexes is a plain filesystem copy of `extracted/*.md`
  into a project's `dev-docs/` subdirectory followed by an ordinary
  `codecompass sync`. The copy preserves the frontmatter byte-for-byte;
  nothing in the documented pipeline or in CodeCompass's own sync path
  strips, transforms, or reads it. Detection of the material already
  works today with zero CodeCompass code changes, purely because of the
  pre-existing generic `dev-docs/**/*.md` glob (Phase 49) — the gap is
  classification, not detection (`EV-DOCORIGIN-007`, `OBS-DOCORIGIN-008`).

## 3. Behavioural rules: every other `origin` consumer, and whether a new value affects it

`CL-DOCORIGIN-001` (derivation `DE-DOCORIGIN-001`) traces every real
`origin` write and read site in `src/codecompass/`, not just the
definition site CG-005 itself named, specifically to check whether
adding a sixth enum value could silently break anything:

| Site | Behaviour | Affected by a new enum value? |
|---|---|---|
| `spec_docs.py::scan_spec_docs` | writes `origin="project"` unconditionally | write site — never reads the enum's value set (`EV-DOCORIGIN-002`) |
| `doc_mapping.py::collect_vendor_doc_artifacts` | writes `origin="codecompass_vendor"` unconditionally | write site — same reasoning (`EV-DOCORIGIN-003`, `OBS-DOCORIGIN-004`) |
| `doc_mapping.py::collect_vendor_upstream_doc_artifacts` | writes `origin="vendor_upstream"` + `vendor_name` unconditionally, for an already-tracked vendor | write site (`EV-DOCORIGIN-003`, `OBS-DOCORIGIN-004`) |
| `doc_mapping.py::build_doc_relations_edges` skill-preference branch | reads `origin == "codecompass_vendor"`/`"codecompass_tool"` to choose between two Skill-kind rows | scoped to Skill/`claude_md` rows, not `spec_doc` rows; falls through unchanged for any value it doesn't name, including a new one (`EV-DOCORIGIN-003`, `OBS-DOCORIGIN-004`) |
| `cli.py::_print_coverage_gap_sections` | filters `entry["origin"] == "third_party"` for an orphaned-skill report | Skill-kind rows from `skills_index` only, not `spec_doc` (`EV-DOCORIGIN-004`, `OBS-DOCORIGIN-005`) |
| `cli.py::query_skills` | prints `origin` verbatim for `skills_index` rows | same scope restriction (`EV-DOCORIGIN-004`, `OBS-DOCORIGIN-005`) |
| `cli.py::_graph_backed_undo_paths` | deletes on-disk paths only where `origin` is exactly `'codecompass_tool'` or `'codecompass_vendor'` (explicit two-value `IN` list) | a `spec_doc` row is never in that list regardless of its `origin` string, old or new (`EV-DOCORIGIN-004`, `OBS-DOCORIGIN-005`) |
| `graph.py::spec_docs_without_relations` / `vendor_docs_without_relations` | coverage-gap queries filtering on `doc_artifacts.kind` only | never reference `origin` at all (`EV-DOCORIGIN-005`, `OBS-DOCORIGIN-006`) |

**Rule (`CL-DOCORIGIN-001`, status: supported):** the smallest correct
schema-level fix for `CG-005` is one new closed `doc_artifacts.origin`
CHECK-enum value, added through the existing generic
`_migrate_doc_artifacts_constraints` mechanism (one more
`_SCHEMA_VERSION` bump, following the exact Phase 17/21/27 precedent),
with **no change required to any other origin consumer** in
`src/codecompass/`. This traced-consumer conclusion is now also ratified
directly as `REQ-DOCORIGIN-001` (§7, §11, §14).

## 4. Important interaction: detection has no automatic signal today

`CL-DOCORIGIN-002` (derivation `DE-DOCORIGIN-002`, status: supported): a
real, mechanically-checkable, content-level signal for "this
`spec_doc`-glob-matched file is externally-pinned, tool-ingested
reference material" **already exists** in the one implemented ingestion
pipeline (the uniform YAML frontmatter block, `EV-DOCORIGIN-006`), but
`scan_spec_docs` reads none of it. No path-based or configuration-based
signal is available at `scan_spec_docs`'s call site either: the
directory this material lands in (`dev-docs/hledger-reference/`) is an
ordinary, arbitrarily-named subdirectory reached only via the
pre-existing generic `dev-docs/**/*.md` glob, indistinguishable in shape
from a project's own hand-authored `dev-docs/` content, and there is no
`vendor.toml` or other config entry marking it as external
(`EV-DOCORIGIN-002`, `EV-DOCORIGIN-007`).

**Consequence, now decided:** the project has chosen to close this gap
by teaching `scan_spec_docs` to parse a leading YAML frontmatter block
and check for both a `resolved_commit` key and a `source_url` key —
exactly the two-field signal `CL-DOCORIGIN-002` confirmed is real,
uniform, and structurally absent from ordinary hand-authored prose —
rather than a manual/config-driven override (`DEC-DOCORIGIN-001`,
`REQ-DOCORIGIN-002`). This is a real, new capability `spec_docs.py` does
not have today (frontmatter parsing); it could not have been assembled
from the existing glob/title logic alone (`CL-DOCORIGIN-002`).

## 5. Important interaction: why `vendor_upstream` cannot simply be reused

`CG-005`'s own filing already rejected reusing `vendor_upstream` for this
material on semantic grounds (designed for a vendor's own embedded
upstream docs, tied to a `vendor_name`; this material has no tracked
`vendors` row and deliberately no `vendor.toml` entry). `CL-DOCORIGIN-003`
(derivation `DE-DOCORIGIN-003`, status: supported) goes further and
empirically confirms the actual failure mode is worse than a design-taste
argument:

- `DocArtifactRow.vendor_name` is resolved via a bare dict subscript
  (`vendor_ids[d.vendor_name]`) inside `_insert_doc_artifacts`, with no
  `.get()`/default and no surrounding `try`/`except` anywhere in the
  insert path (`OBS-DOCORIGIN-004`, `OBS-DOCORIGIN-011`).
- A `vendor_name` naming a vendor with no corresponding `vendors` row
  (i.e., no `vendor.toml` entry — exactly this material's situation)
  **raises an uncaught `KeyError` at sync time** — a hard crash, not a
  silent `NULL` or soft failure (`EV-DOCORIGIN-003`, `OBS-DOCORIGIN-011`).
- Omitting `vendor_name` while still using `origin='vendor_upstream'`
  would silently violate that value's only real-world invariant observed
  in this codebase (every current `vendor_upstream` row has a non-null,
  resolvable `vendor_name`) without CodeCompass enforcing that invariant
  at the schema level at all (`CL-DOCORIGIN-003`).

**Rule:** reusing `vendor_upstream` for this material is not merely
semantically wrong, it is empirically confirmed to crash the sync if
attempted the way this material is actually shaped today. `DEC-DOCORIGIN-001`
confirms this: `vendor_upstream` stays exactly as it is, and
`vendor_doc`-kind rows are explicitly out of scope for this phase (§13).

## 6. Architecture / implementation concepts

- The `origin` (and `kind`) CHECK enum has been widened exactly twice
  before via one generic, version-comparison-driven migration function,
  `_migrate_doc_artifacts_constraints`: Phase 21 added `'project'`
  (alongside `kind` gaining `'spec_doc'`); Phase 27 added
  `'vendor_upstream'` (alongside `kind` gaining `'vendor_doc'`). Each
  widening is a single `_SCHEMA_VERSION` bump plus a drop-and-recreate of
  `doc_artifacts` (safe because `rebuild_deterministic` repopulates it
  fully on every whole-project sync) — not a bespoke per-value migration
  path (`EV-DOCORIGIN-001`, `OBS-DOCORIGIN-002`). A new value,
  `pinned_reference`, follows this exact precedent (`DEC-DOCORIGIN-001`,
  `REQ-DOCORIGIN-001`). Because of this drop-and-recreate mechanism, no
  explicit backfill/migration step is needed for already-synced
  databases: the new classification applies automatically the next time
  affected files are synced (`DEC-DOCORIGIN-001`).
- The reference-ingestion pipeline that produces this material
  (`planning/reference-projects/ledgerkit/reference-experiment/`) is
  entirely Git-commit-pinned today: `references.toml`'s only declared
  `source` is `"git"`; `ReferenceSource.source` is typed as an
  unvalidated free string, but `resolve_ref`/`_read_source_root` are
  written exclusively in terms of Git concepts (clone, tag-to-commit
  resolution) with **no conditional branch on `reference.source`'s value
  at all** — there is no implemented non-Git fetch method anywhere in the
  pipeline (`EV-DOCORIGIN-009`, `OBS-DOCORIGIN-010`).

## 7. Examples (Given/When/Then)

These are now the ratified Requirement examples, not merely
Claim-derived illustrations:

**Example 1 — schema accepts the new value (`REQ-DOCORIGIN-001`):**
> Given a fresh context-graph.db at the previous schema version,
> When `codecompass sync` runs against a project containing at least one
> file that will be classified with `origin='pinned_reference'`,
> Then the database migrates to the new schema version and the row is
> inserted successfully, with no CHECK constraint violation.

**Example 2 — automatic frontmatter detection (`REQ-DOCORIGIN-002`):**
> Given a file under a project's `dev-docs/` tree beginning with:
> ```
> ---
> reference: hledger
> source_url: https://github.com/simonmichael/hledger
> resolved_commit: 33fa849e7ae841968bd21c427094c4fb4a4ec38d
> ---
> ```
> When `scan_spec_docs` processes it,
> Then the resulting `doc_artifacts` row has `origin='pinned_reference'`.
>
> Given an ordinary hand-authored `dev-docs/*.md` file with no
> frontmatter,
> When `scan_spec_docs` processes it,
> Then the resulting row has `origin='project'`, exactly as today.

**Example 3 — new test coverage (`REQ-DOCORIGIN-003`):**
> Given the existing `test_spec_docs.py` test suite,
> When the new frontmatter-detection branch is added,
> Then a new test (e.g. `test_scan_spec_docs_pinned_reference_frontmatter`)
> asserts `origin='pinned_reference'` for a frontmatter-bearing fixture,
> and every pre-existing `origin='project'` assertion still passes.

For context, the two illustrative examples the prior (pre-Decision)
version of this document constructed directly from Claims/Evidence
remain accurate background and are retained below since they describe
behaviour still true today (the "before" state the Requirements above
change):

**Prior example A — current mis-detection before the fix (supports
`CL-DOCORIGIN-002`, `EV-DOCORIGIN-002`, `EV-DOCORIGIN-006`,
`EV-DOCORIGIN-007`):** given a file matched by `spec_docs.py`'s
`dev-docs/**/*.md` glob that carries a YAML frontmatter block with
`reference`, `source_url`, and `resolved_commit` fields, when
`scan_spec_docs` runs *today* (i.e., before `REQ-DOCORIGIN-002` is
implemented), the resulting row still has `origin="project"`.

**Prior example B — the `vendor_upstream`-reuse crash (supports
`CL-DOCORIGIN-003`, `EV-DOCORIGIN-003`, `OBS-DOCORIGIN-011`):** given a
`DocArtifactRow` constructed with `origin='vendor_upstream'` and a
`vendor_name` naming a vendor with no corresponding `vendors` row, when
`_insert_doc_artifacts` runs during sync, it raises an uncaught
`KeyError` and the sync aborts.

## 8. Edge cases

- A file matched by the `dev-docs/**/*.md` glob with no frontmatter at
  all is genuinely project-authored-shaped content; the existing
  `test_spec_docs.py` assertions (`origin == "project"`) are run only
  against such frontmatter-free fixtures and would remain correct under
  a fix that branches on frontmatter presence (`EV-DOCORIGIN-008`,
  `OBS-DOCORIGIN-009`) — this is now the explicit "unchanged" half of
  `REQ-DOCORIGIN-002`'s statement.
- No test in the current suite exercises `scan_spec_docs` against a
  frontmatter-bearing fixture file or asserts any specific `origin`
  value for externally-ingested content — this was a real, untested
  path, now the subject of the new-test requirement `REQ-DOCORIGIN-003`
  (`EV-DOCORIGIN-008`).
- `test_doc_mapping.py`'s `origin="project"` occurrences are
  hand-constructed `DocArtifactRow` test inputs exercising
  `doc_mapping.py`'s matching logic, not `scan_spec_docs`'s own
  origin-assignment behaviour — they provide no coverage either way for
  a change scoped to `scan_spec_docs` (`OBS-DOCORIGIN-009`).
- `references.toml`'s `source` field would accept a string like `"url"`
  today without a parse error, since it is unvalidated — but attempting
  to actually use such a value would silently do nothing different, since
  no code path branches on it; this is a latent trap for anyone assuming
  the schema's permissiveness implies working non-Git support
  (`EV-DOCORIGIN-009`, `DE-DOCORIGIN-004`). `DEC-DOCORIGIN-001`'s naming
  choice (§9) is deliberately written so this latent gap, if ever closed,
  would not require a further schema change.
- A frontmatter block that contains `source_url` but not
  `resolved_commit` (or vice versa) is not covered by any record in this
  knowledge base beyond the Requirement's own statement that *both* keys
  must be present for the new classification to apply
  (`REQ-DOCORIGIN-002`) — a partial-key frontmatter block keeps
  `origin='project'` per that same statement, but no Evidence or Claim
  discusses whether such partial frontmatter actually occurs anywhere in
  practice.

## 9. Known uncertainties / open questions — history and resolution

The prior version of this document, written before the Phase 54c
user-review gate ran, correctly flagged two genuinely unresolved
judgment calls at this point. Both are now resolved by
`DEC-DOCORIGIN-001`. This section is kept, not deleted, so a reader can
see that the uncertainty was real and got resolved — not that it never
existed.

- **Naming and scope of the new enum value — RESOLVED.** The open
  question was whether the name/semantics should be scoped narrowly to
  "Git-commit-pinned" or written more broadly to anticipate a future
  non-Git-sourced pinned reference (`CL-DOCORIGIN-004`,
  `DE-DOCORIGIN-004`). `DEC-DOCORIGIN-001` resolves this: the value is
  named `pinned_reference` and scoped deliberately broadly — a
  provenance *class* ("externally-sourced reference material,
  revision-pinned and materialized into the project tree by a tool"),
  not tied to "git" in the name, even though only a git-backed pipeline
  exists today (`DEC-DOCORIGIN-001`). The rationale given is that the
  fetch mechanism (git vs. a future url source) is a separate concern
  from the provenance class the `origin` column records, so no further
  schema change would be needed later if a non-git source is ever
  implemented (`DEC-DOCORIGIN-001`).
- **How `scan_spec_docs` should decide when to assign the new value —
  RESOLVED.** The open question was whether the smallest acceptable fix
  was (a) teaching `scan_spec_docs` to parse frontmatter and branch on
  it, (b) a config-driven/manual override outside `scan_spec_docs`
  entirely, or (c) some other mechanism (`CL-DOCORIGIN-002`).
  `DEC-DOCORIGIN-001` resolves this as (a): detection is automatic, via
  frontmatter parsing inside `scan_spec_docs`, checking for both a
  `resolved_commit` key and a `source_url` key in a leading YAML
  frontmatter block — not a manual/config-driven override
  (`DEC-DOCORIGIN-001`, `REQ-DOCORIGIN-002`). The stated rationale is
  that the two-field signal is real, mechanical, and uniquely present in
  ingested content per `CL-DOCORIGIN-002`, and that a manual/config-driven
  path would be more code for a weaker guarantee, since a human could
  forget to flag a file while the frontmatter check cannot
  (`DEC-DOCORIGIN-001`).
- **No Claim in this knowledge base carries `status: contradicted`.**
  All four Claims (`CL-DOCORIGIN-001` through `CL-DOCORIGIN-004`) are
  `status: supported`, with empty `contradicting_evidence` lists, and
  `DEC-DOCORIGIN-001` explicitly states it does not question or revise
  any of them — it only chooses among the evidenced options they left
  open. This design doc has nothing to honestly flag in the
  "contradicted claim" sense — worth stating plainly rather than
  silently omitting the category.
- **Remaining genuine unknown.** No record in this knowledge base
  addresses what happens for a frontmatter block containing only one of
  the two required keys in practice (see §8's edge case) — this is not
  something `DEC-DOCORIGIN-001` was asked to resolve, and no Requirement
  goes beyond stating the both-keys rule itself.

## 10. Contradictions between behaviour/source/tests/docs

None found. The research explicitly checked test coverage against
source behaviour (`EV-DOCORIGIN-008`) and found the existing
`origin == "project"` test assertions are consistent with — not
contradicted by — the source's actual unconditional-constant behaviour,
because they only exercise frontmatter-free fixtures. The gap is a
missing test for an untested path, now closed by `REQ-DOCORIGIN-003`,
not a test asserting something the source contradicts.

## 11. Proposed behaviour for the target project (ratified)

`DEC-DOCORIGIN-001` and its three Requirements now state ratified
project behaviour, superseding the prior "candidate, pending a
Decision" framing:

- Add one new closed value, `pinned_reference`, to the `doc_artifacts.origin`
  CHECK enum via the existing `_migrate_doc_artifacts_constraints`
  mechanism, following the Phase 17/21/27 precedent exactly. No other
  `origin` consumer in `src/codecompass/` needs to change for this
  addition alone (`REQ-DOCORIGIN-001`, `CL-DOCORIGIN-001`).
- `scan_spec_docs` MUST assign `origin='pinned_reference'` (instead of
  `'project'`) to a `dev-docs/**/*.md`-glob-matched file whose leading
  content is a YAML frontmatter block (delimited by `---` lines)
  containing both a `resolved_commit` key and a `source_url` key. A file
  with no such frontmatter, or frontmatter missing either key, MUST keep
  the existing `origin='project'` behaviour unchanged (`REQ-DOCORIGIN-002`).
  This is implemented as automatic, mechanical detection — not a
  config-driven or manual override (`DEC-DOCORIGIN-001`).
- Do **not** reuse `vendor_upstream` for this material — doing so risks
  a real, confirmed `KeyError` crash at sync time given this material's
  actual shape (no tracked vendor) (`CL-DOCORIGIN-003`; unchanged by the
  Decision, which explicitly leaves `vendor_upstream` untouched).
- A new test fixture MUST exercise the new `origin='pinned_reference'`
  branch directly, and every existing `origin='project'` assertion for
  frontmatter-free fixtures MUST continue to pass unchanged
  (`REQ-DOCORIGIN-003`).
- No explicit backfill/migration step is needed for already-synced
  databases: `doc_artifacts` is dropped and fully repopulated on every
  whole-project sync, so the new classification applies automatically
  the next time affected files are synced (`DEC-DOCORIGIN-001`).
- The naming/scope question and the detection-mechanism question — both
  open in the prior version of this document — are resolved; see §9.

## 12. Intentional differences from upstream behaviour

Not applicable to this feature. Unlike, e.g., `hledger depth:` semantics
(a different feature under this project's Phase 54c work), this feature
has no external "upstream" whose behaviour CodeCompass is choosing to
match or deviate from — it is an internal CodeCompass schema/classification
gap. No record in this knowledge base addresses an upstream-vs-target
divergence for this feature, so this section is intentionally left as a
non-applicable note rather than populated with invented content.

## 13. Non-goals

- Changing any `origin` consumer other than the write site itself —
  `CL-DOCORIGIN-001`/`DE-DOCORIGIN-001` traced every real consumer and
  found none needs to change for a new enum value alone; `REQ-DOCORIGIN-001`
  ratifies this.
- Extending `pinned_reference` (or any equivalent classification) to
  `vendor_doc`-kind rows in this phase — `vendor_upstream` stays exactly
  as it is, and whether a `vendor_doc` that happens to be
  externally-pinned should ever share `pinned_reference` is left an
  explicit non-goal, unrelated to `CG-005`'s own real-world instance,
  which is `spec_doc`-kind only (`DEC-DOCORIGIN-001`).
- Implementing a non-Git ("url"-sourced) fetch method in the reference
  pipeline — no such capability exists today and no record in this
  knowledge base proposes building one; the naming decision deliberately
  keeps the enum value's *name* general enough to not require a further
  schema change if this is ever built, but building it is explicitly not
  part of this work (`EV-DOCORIGIN-009`, `CL-DOCORIGIN-004`,
  `DEC-DOCORIGIN-001`).
- Reusing `vendor_upstream` for this material in any form — ruled out on
  both semantic and crash-risk grounds (`CL-DOCORIGIN-003`).
- A manual/config-driven override mechanism for assigning
  `pinned_reference` — considered and explicitly rejected in favour of
  automatic frontmatter detection (`DEC-DOCORIGIN-001`).
- An explicit backfill/migration step for already-synced databases — not
  needed, since `doc_artifacts` is fully repopulated on every
  whole-project sync (`DEC-DOCORIGIN-001`).
- Retroactively auditing or fixing every file in the repository for
  correct `origin` classification beyond the `CG-005` material itself —
  out of scope for this research, which traced consumers and detection
  feasibility, not a full-repository audit.

## 14. Acceptance criteria (ratified)

These now state ratified, testable Requirements directly, rather than
candidate criteria pending a Decision:

- The new `doc_artifacts.origin` CHECK-enum value `pinned_reference` can
  be added via `_migrate_doc_artifacts_constraints` and accepted by the
  constraint, with a fresh database migrating and inserting successfully
  with no CHECK violation (`REQ-DOCORIGIN-001`).
- `scan_spec_docs` assigns `origin='pinned_reference'` to a
  frontmatter-bearing file containing both a `resolved_commit` key and a
  `source_url` key, and continues to assign `origin='project'` to a file
  with no such frontmatter or with frontmatter missing either key
  (`REQ-DOCORIGIN-002`).
- No existing test in `test_spec_docs.py`/`test_doc_mapping.py` breaks —
  all pre-existing `origin='project'` assertions for frontmatter-free
  fixtures continue to pass unchanged (`REQ-DOCORIGIN-002`,
  `REQ-DOCORIGIN-003`, `EV-DOCORIGIN-008`).
- A new test fixture and test (e.g.
  `test_scan_spec_docs_pinned_reference_frontmatter`) exercises the new
  branch directly, asserting `origin='pinned_reference'` for a
  frontmatter-bearing fixture — closing the real, previously-missing
  test-coverage gap this research identified (`REQ-DOCORIGIN-003`,
  `EV-DOCORIGIN-008`).
- No other `origin` consumer in `src/codecompass/` requires any code
  change for this addition alone (`REQ-DOCORIGIN-001`, `CL-DOCORIGIN-001`).

This list is now grounded in ratified Requirement records
(`REQ-DOCORIGIN-001` through `-003`) rather than being provisional
candidate criteria; no further Decision is needed to treat it as
acceptance-testable. Implementation and its own test run against these
criteria are outside this document's scope (design, not implementation
sign-off).

## 15. Post-implementation verification (Phase 54c §8)

Implemented and independently re-verified against real behaviour, not
just unit tests (per `L-021`'s own "test through the real production
call site" rule):

- `REQ-DOCORIGIN-001`/`-002` implemented in `src/codecompass/graph.py`
  (`_SCHEMA_VERSION` "6" → "7", `origin` CHECK gains `'pinned_reference'`)
  and `src/codecompass/spec_docs.py` (`_has_pinned_reference_frontmatter`,
  `_detect_origin`, wired into `scan_spec_docs`'s real `DocArtifactRow`
  construction — the actual call site, not an isolated helper).
- `REQ-DOCORIGIN-003`: four new tests added to `tests/test_spec_docs.py`
  (frontmatter present, missing one key, no frontmatter, and the
  detector function directly); two new tests added to `tests/test_graph.py`
  mirroring the established Phase 17/21/27 fresh-DB-acceptance +
  migration pattern. All 587 tests pass; `ruff check .` and
  `check_user_docs.py --strict` clean.
- **Real end-to-end confirmation**, not just unit tests: ran an actual
  `codecompass sync` against a scratch project with a synthetic
  frontmatter-bearing file (correctly classified `pinned_reference`)
  and a hand-written file (correctly stayed `project`), confirming the
  schema migrated to version `7` for real. Separately re-ran
  `codecompass sync` against Phase 54b's own real scratch Ledgerkit copy
  and confirmed **all 19 real ingested `dev-docs/hledger-reference/*.md`
  files** now read `origin='pinned_reference'`, while Ledgerkit's own
  hand-authored `dev-docs/*.md` files correctly stayed `origin='project'`
  — this is the real, original `CG-005` instance, now closed for real,
  not merely by a synthetic test.
- **Packet sufficiency**: two real gaps found and logged
  (`packet-sufficiency.md`) — the packet's own "existing tests" section
  never named `tests/test_graph.py`, which needed both a mechanical
  update (6 hard-coded schema-version assertions) and two new tests
  following an established pattern the packet didn't point at.

All three Requirements moved `approved` → `verified`. No discrepancy
between approved design and actual implementation was found —
`REQ-DOCORIGIN-001/002/003` shipped exactly as specified, not revised.
