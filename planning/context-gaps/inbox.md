# Context-gaps inbox

The live queue. New entries at the top. Format: `TEMPLATE.md`.
Rules: `README.md`, `decisions/0051`. **Nothing here is ever written to
`context-graph.db`.**

Statuses: `candidate` → `recurred` → `promoted-to-roadmap` / `discarded`.

---

### CG-006 — `mentions_artifact` matches by target title text only, never by filename, so docs that cross-reference each other by filename in prose (a common real pattern) are missed

- **origin:** Phase 55b (spec-doc name population, closing `CG-004`),
  round-2 `context-evaluator` independent verification against the real
  Ledgerkit repository
- **date:** 2026-09-17
- **codecompass_revision:** working tree (Phase 55b's own uncommitted
  diff at filing time)
- **project:** ledgerkit, real live repository (read-only)
- **the edge:** `A → B` where A =
  `dev-docs/planning/core-redefinition/17-query-semantics-brief.md`, B =
  `dev-docs/planning/core-redefinition/07-query-regex.md` — the exact
  real-world relationship `CG-004`'s own original filing named as its
  motivating example ("one is literally the plan document another was
  implemented from"). Even after `CG-004`'s fix landed (spec docs now
  get a real `name`), this specific pair still produces **zero**
  `mentions_artifact` edge.
- **edge kind:** doc↔doc (a mechanical relation-*detection* gap distinct
  from `CG-004`: both artifacts are now named and eligible targets; the
  match still fails because of *what string* is being searched for, not
  *whether* the target is eligible)
- **agent's reasoning:** confirmed by direct inspection —
  `17-query-semantics-brief.md`'s own text cites the other file by its
  **filename** (`07-query-regex.md`) in prose, never by its H1 **title**
  text ("7. Query language and regex extension plan"). `mentions_artifact`
  (`doc_mapping.py::build_doc_relations_edges`) only word-boundary-matches
  a target's `name` field (its title, per `spec_docs.py::_extract_title`)
  — it has no path/filename-based matching mode at all. Referencing
  another doc by filename (`see 07-query-regex.md`) rather than by its
  full title is common, ordinary technical-writing practice — arguably
  *more* common than quoting a target's exact title text verbatim — so
  this isn't a rare edge case; it's a real, structural blind spot in the
  matching *strategy* itself, found live on the very first real pair this
  project's own evidence stream named as the motivating case for `CG-004`.
- **what the graph shows instead:** nothing — zero `mentions_artifact`
  edges for this pair, before or after `CG-004`'s fix.
- **could mechanical detection ever catch this?** yes-with-a-second-
  matching-mode — a target `doc_artifacts` row's own `path`/filename
  (already stored, no schema change) could be word-boundary-matched
  against source text the same way `name` already is, producing the same
  `relation_kind='mentions_artifact'` edge either way (no new relation
  kind needed) — filename-mentions and title-mentions are the same kind
  of evidence, just two different strings to search for.
- **smallest candidate that would fix it:** extend
  `build_doc_relations_edges`'s `named_artifacts` matching to also try
  each target's filename (basename, or basename-without-extension) as an
  additional pattern, alongside the existing `name` check — a
  `doc_mapping.py`-only change, no new table, no new relation kind, same
  self-mention exclusion already applies (path-based, unaffected by
  which string matched).
- **classification:** detection-improvement (Stage C / GATE DB-scale) —
  same class as `CG-002`/`CG-004`, not a Stage E ontology question.
- **status:** candidate
- **recurrence:** first occurrence
- **curation (Phase 55b triage, 2026-09-17, knowledge-curator):** template
  fields all present (origin, date, `codecompass_revision`, project, the
  edge, edge kind, reasoning, what-the-graph-shows-instead, "could
  mechanical detection ever catch this?", smallest candidate,
  classification, status, recurrence). Independently re-verified rather
  than taken on the entry's own word: read both real Ledgerkit files
  directly — `17-query-semantics-brief.md` line 4 cites `07-query-regex.md`
  by filename ("per `07-query-regex.md` §7.1's phasing note"), and two
  further citations at lines 383/387 do the same; grepped the full file
  for the target's actual H1 title text ("Query language and regex
  extension plan") and found zero occurrences — the claim "cited by
  filename, never by title text" holds exactly as written, not merely
  plausible. Read `src/codecompass/doc_mapping.py::build_doc_relations_edges`
  directly and confirmed it word-boundary-matches only `artifact.name`
  (the title, via `_extract_title`) with no path/filename-based matching
  mode at all — the mechanism gap is real, not a symptom of some other
  already-fixed bug. **Checked this is not a restatement of `CG-004`**:
  `CG-004` was "a `spec_doc` row has no `name` at all, so it can never be
  a match target regardless of *how* a source doc refers to it" —
  structurally fixed this same phase. `CG-006` is a different mechanism
  that survives that fix: both artifacts here are now named and eligible
  targets, and the match still fails, because the matching *strategy*
  (title-substring only) doesn't cover a real, ordinary citation style
  (by filename). This is exactly the entry's own "distinct from CG-004"
  framing, and it holds up under independent re-derivation, not just on
  the entry's say-so. Checked for any other pre-existing entry that might
  already cover this: `CG-001`/`CG-002`/`CG-003`/`CG-005` are about
  intra-`src` feature grouping, glob-scope coverage, an unrepresented
  external manual, and `origin`-enum provenance respectively — none
  addresses `mentions_artifact`'s matching *strategy*. Classification
  confirmed correct: the smallest candidate (word-boundary-match each
  target's filename/basename alongside its existing `name` check) is a
  `doc_mapping.py`-only change reusing the existing `mentions_artifact`
  relation kind and the same self-mention exclusion — no new table, no
  new relation kind, matching `detection-improvement (Stage C / GATE DB)`
  exactly, not a Stage E ontology question. **Outcome: stays `candidate`,
  not `recurred`** — genuinely first occurrence of this specific
  matching-strategy gap (the resemblance to `CG-004` is a shared origin
  task, not a shared mechanism, per the distinction confirmed above).
  Named for a future GATE DB input as a small, precedented,
  independently-fundable follow-on to `CG-004`'s own fix, per the retro's
  own "Where we're going" framing — not urgent, no forcing deadline. No
  entry made to `context-graph.db` — this queue never writes there, per
  `decisions/0051`.

### CG-005 — `doc_artifacts.origin='project'` is semantically wrong for externally-sourced, pinned reference material

- **origin:** Phase 54 (heterogeneous reference-material experiment),
  treatment run + `reference-project-tester`
- **date:** 2026-09-16
- **codecompass_revision:** `72961e0` (working tree;
  `planning/reference-projects/ledgerkit/reference-experiment/` is
  untracked, per this phase's own design decision to keep the ingestion
  pipeline outside `src/codecompass/`)
- **project:** ledgerkit, scratch copy + this experiment's own
  `references.lock`
- **the edge:** `A ↔ B` where A = the six ingested
  `hledger-tag-query-*.md` files (externally-sourced: hledger's own
  upstream manual text and `hledger-lib` source excerpts, pinned at
  commit `33fa849e7ae841968bd21c427094c4fb4a4ec38d`, never authored by
  Ledgerkit or CodeCompass), B = `doc_artifacts.origin` — the column that
  is supposed to record where a doc artifact came from.
- **edge kind:** doc↔code (a provenance/classification gap, not a
  missing relationship between two artifacts)
- **agent's reasoning:** `src/codecompass/spec_docs.py::scan_spec_docs`
  (line 82) hard-codes `origin="project"` for every `kind='spec_doc'` row
  it produces, with no branch for content that reached the
  `dev-docs/`-glob path via an extraction pipeline rather than a
  Ledgerkit contributor writing it by hand. `origin='project'` is
  accurate for Ledgerkit's own `dev-docs/hledger-compatibility.md`; it is
  not accurate for `dev-docs/hledger-reference/hledger-tag-query-manual.md`,
  whose actual origin is "an upstream Git repository
  (`simonmichael/hledger`), pinned at a specific commit, extracted with a
  content hash" — a fundamentally different provenance class the schema
  has no room to record. Independently confirmed:
  `src/codecompass/graph.py`'s `origin` CHECK enum (lines 111-115) is
  exactly five closed values (`codecompass_tool`, `codecompass_vendor`,
  `third_party`, `project`, `vendor_upstream`) — none of which
  distinguishes "hand-authored by this project" from "externally pinned
  reference text materialized into this project's tree by a tool."
- **what the graph shows instead:** `origin='project'` for all six
  ingested files, identical to every one of Ledgerkit's own hand-written
  `dev-docs/*.md` files — a reader of `context-graph.db` (or `query
  relations`' output) cannot tell these apart at all.
- **could mechanical detection ever catch this?** unsure —
  `vendor_upstream` already exists as a *candidate* reuse (the phase
  plan's own §3.1 considered it), but was designed for a vendor package's
  own embedded upstream docs, which carry a `vendor_name`; this material
  has no tracked `vendors` row at all (`vendor_id` is already `NULL` for
  `spec_doc` rows) and deliberately no `vendor.toml` entry ("No
  `vendor.toml` entry for hledger" — the phase plan's own Design
  decisions). Reusing `vendor_upstream` without a vendor to hang it on
  would itself be a misuse of an existing enum value's meaning; a clean
  fix needs either a new `origin` value or a provenance field this
  experiment's own frontmatter (commit SHA, content hash, source URL)
  could populate — neither exists today.
- **smallest candidate that would fix it:** one new
  `doc_artifacts.origin` CHECK-enum value (e.g. `pinned_reference`),
  following the exact one-value-per-phase precedent (Phase 17, 21, the
  `vendor_doc`-introducing phase) the phase plan itself names — the phase
  plan explicitly gated this on "the zero-schema-change hypothesis being
  empirically shown insufficient" (§3.1/Scope); this finding is the
  evidence that the hypothesis holds for *detection* (`OBS-007`) but
  fails for *provenance classification* specifically.
- **classification:** graph-capability (Stage E / GATE DD) — a new
  provenance distinction, not a detection heuristic; matches
  `conditional-generalisation.md` §2.4's "first-class provenance"
  hypothesis (a claim's source class should be visible, not just its
  content).
- **status:** candidate
- **recurrence:** first occurrence
- **curation (Phase 54 triage, 2026-09-16, knowledge-curator):** template
  fields all present. Independently re-verified rather than taken on the
  entry's own word: `src/codecompass/graph.py` lines 111-115 confirm the
  `origin` CHECK constraint is exactly the closed five-value enum this
  entry names (`codecompass_tool, codecompass_vendor, third_party,
  project, vendor_upstream`), and `src/codecompass/spec_docs.py::scan_spec_docs`
  line 82 hard-codes `origin="project"` for every `kind='spec_doc'` row
  with no branch for extraction provenance — confirming the six ingested
  files are indistinguishable by `origin` from Ledgerkit's own
  hand-authored `dev-docs/*.md` content. Checked the `vendor_upstream`
  reuse question the entry itself raises: `vendor_upstream` rows carry a
  `vendor_name` tied to a tracked `vendors` row (Phase 27's own
  vendor-doc precedent); this material deliberately has no `vendor.toml`
  entry (the phase plan's own Design decisions), so reusing
  `vendor_upstream` without a vendor to hang it on would misuse an
  existing enum value's established meaning, as the entry argues — this
  reasoning holds up under independent check, not just plausible on its
  face. Checked for a recurrence against every context-gaps entry filed
  before this phase (`CG-001` through `CG-003`): none addresses
  `doc_artifacts.origin`'s enum coverage — `CG-003` is "zero
  representation prior to ingestion" (a different gap, correctly
  distinguished in its own Phase-54 note added alongside this entry, not
  merged with it). **Outcome: stays `candidate`, not `recurred`** —
  genuinely a first occurrence. Classification `graph-capability (Stage E
  / GATE DD)` confirmed correct: a new CHECK-enum value is a schema
  change to a closed enum, not a detection heuristic — matches
  `conditional-generalisation.md` §2.4 exactly. Named alongside `CG-004`
  as Phase 55/GATE DD input (`findings.md`'s own Phase 54 section already
  reaches the same "two independently small, precedented fixes, fundable
  on their own narrow terms" framing). No entry made to `context-graph.db`
  — this queue never writes there, per `decisions/0051`.

### CG-004 — mechanical `mentions_artifact` detection cannot relate two `spec_doc`-kind artifacts to each other, in any project, regardless of content

- **origin:** Phase 54 (heterogeneous reference-material experiment),
  treatment run Step 1
- **date:** 2026-09-16
- **codecompass_revision:** `72961e0` (working tree;
  `reference-experiment/` untracked)
- **project:** ledgerkit, scratch copy (never the real clone)
- **the edge:** `A ↔ B` where A = the six ingested
  `dev-docs/hledger-reference/hledger-tag-query-*.md` files
  (`kind='spec_doc'`), B = every other `doc_artifacts` row in the scratch
  copy, including Ledgerkit's own real `dev-docs/hledger-compatibility.md`
  (also `kind='spec_doc'`) — zero `mentions_artifact` edges exist between
  any of them, in either direction.
- **edge kind:** doc↔code (a mechanical relation-*detection* gap between
  two already-indexed artifacts — distinct from `CG-002`, which was a
  detection-*scope* gap where one side wasn't tracked at all; here both
  sides are tracked and detection still produces nothing)
- **agent's reasoning:** per the treatment run's own report
  (`treatment-tag-query-brief.md` Step 1), after `codecompass sync
  --budget 0`, `doc_relations_edges` held exactly 8 rows, all
  `mentions_artifact` edges from various `dev-docs/*.md` files to the
  tool-level `codecompass` Skill (the same pattern independently
  confirmed in Phases 45/46/49/51/52) — none involving any of the six
  ingested files, and none originating from or targeting
  `dev-docs/hledger-compatibility.md` either. Root-caused by direct code
  reading, independently re-confirmed rather than taken on the treatment
  brief's own word (the scratch copy no longer exists to re-query
  directly, per this phase's own no-committed-scratch-copy discipline):
  `spec_docs.py::scan_spec_docs` (line 82) constructs every
  `kind='spec_doc'` `DocArtifactRow` with no `name=` argument, so it
  defaults to `None` (`graph.py`'s `DocArtifactRow.name: str | None =
  None`, line 276). `doc_mapping.py::build_doc_relations_edges`'s own
  docstring states the rule explicitly ("A doc artifact with no `name`
  set is never a match target — nothing to word-boundary-search for,"
  lines 296-297), and its code confirms it (`named_artifacts = [row for
  row in other_doc_artifact_rows if row.name]`, line 321) — every
  `spec_doc` row is therefore permanently excluded from ever being a
  `mentions_artifact` *target*, and since the source-side scan (lines
  345-355) only searches for *other* artifacts' names in the source
  doc's text, a `spec_doc` row can also never *produce* a
  `mentions_artifact` edge pointing at another `spec_doc`. This holds
  regardless of file content, project, or how distinctively either file
  is named — a structural property of `kind='spec_doc'` rows never
  getting a `name`, not a matching-heuristic weakness.
- **what the graph shows instead:** nothing — zero `mentions_artifact`
  edges among any `spec_doc`-kind rows, in either the ingested reference
  material or Ledgerkit's own pre-existing `dev-docs/` content.
- **could mechanical detection ever catch this?** yes-with-better-
  heuristics — populating `doc_artifacts.name` for `spec_doc` rows (e.g.
  from a Markdown title/H1, a frontmatter `title:` field, or a stable
  slug derived from the path) would make them eligible match targets
  under the exact same `mentions_artifact` word-boundary logic that
  already exists; no new relation kind or schema table is needed, only a
  name-population rule for one `kind`.
- **smallest candidate that would fix it:** a `scan_spec_docs`/
  frontmatter-reading change in `src/codecompass/spec_docs.py` to
  populate `name` for `spec_doc` rows, mirroring how Skills already get a
  `name` from their own frontmatter — a Stage C / GATE DB-scale fix, not
  a Stage E one.
- **classification:** detection-improvement (Stage C / GATE DB)
- **status:** promoted-to-roadmap — fix implemented Phase 55b (2026-09-17)
- **recurrence:** first occurrence
- **curation (Phase 54 triage, 2026-09-16, knowledge-curator):** template
  fields all present (origin, date, codecompass_revision, project, the
  edge, edge kind, reasoning, what-the-graph-shows-instead, "could
  mechanical detection ever catch this?", smallest candidate,
  classification, status, recurrence). Independently re-verified by
  direct code reading rather than taking the entry's own account:
  `src/codecompass/spec_docs.py::scan_spec_docs` line 82 constructs
  `DocArtifactRow(path=rel.as_posix(), kind="spec_doc",
  origin="project")` — no `name=` argument, so it takes the dataclass
  default `None` — and `src/codecompass/doc_mapping.py`'s
  `named_artifacts = [row for row in other_doc_artifact_rows if
  row.name]` (line 321) confirms any row with `name is None` is
  permanently excluded as a match target; since the source-side scan only
  searches for *other* artifacts' names in a doc's own text, a `spec_doc`
  row can also never *produce* a match against another `spec_doc` row.
  This is a structural property of every `kind='spec_doc'` row in every
  project, exactly as claimed — not scoped to Ledgerkit or to
  externally-ingested reference material specifically. Checked for a
  recurrence against every context-gaps entry filed before this phase:
  `CG-002` is a detection-*scope* gap (a whole directory never globbed at
  all, one side of the edge never even tracked); `CG-001` is about
  intra-`src` code-feature grouping; `CG-003` is about the manual having
  zero representation prior to ingestion — none is the same edge/mechanism
  as "two already-tracked `spec_doc` rows can never relate to each other."
  **Outcome: stays `candidate`, not `recurred`** — genuinely a first
  occurrence of this specific mechanism. Classification
  `detection-improvement (Stage C / GATE DB)` confirmed correct: the fix
  (populate `name` for `spec_doc` rows from a title/frontmatter/slug) is a
  `spec_docs.py`-only change reusing the existing `mentions_artifact`
  word-boundary logic — no new relation kind or table, matching the
  entry's own "smallest candidate" framing exactly. Named alongside
  `CG-005` as Phase 55/GATE DD input (`findings.md`'s own Phase 54
  section). No entry made to `context-graph.db`.
- **note added Phase 55 (2026-09-17, evidence reconciliation):**
  **independently corroborated a second time**, from a genuinely
  different angle — Ledgerkit's own `validation/codecompass/findings/CC-LK-001`
  (Stage C Phase 2, Ledgerkit revision `27c410d`/`d86f9b4`), its first-ever
  real use of the actual `codecompass` CLI against its own live
  repository (not a scratch copy, not from CodeCompass's own repo): three
  real, topically-obvious dev-docs files (`dev-docs/hledger-compatibility.md`,
  `07-query-regex.md`, `17-query-semantics-brief.md` — one is literally
  the plan document another was implemented from) produced zero
  `mentions_artifact` edges among them. Recorded as **independent for the
  raw observation** (a different task, a different real codebase, a
  different observer — Ledgerkit's own `context-curator` role, not
  CodeCompass's own agents); **not counted as an independent re-derivation
  of the causal diagnosis** — `CC-LK-001`'s own text explicitly
  cross-references this entry's root-cause explanation rather than
  independently re-deriving it from `spec_docs.py`'s source (see
  `planning/phase-55-evidence-reconciliation.md`'s own "Independence
  discipline" section for why this distinction is drawn explicitly, per
  that document's governing prompt's own strictness requirement). Net
  effect: still first-occurrence by this entry's own recurrence
  bookkeeping (one prior corroborating instance, not a second *filed*
  `CG-NNN` entry), but now backed by two independent real-task
  observations rather than one — the evidentiary bar
  `planning/phase-55-evidence-reconciliation.md`'s §F cites as
  justifying **IMPLEMENT** (a Phase 56 recommendation), not further
  deferral.
- **note added Phase 55b (2026-09-17), closure:** implemented and
  independently verified via a two-round `context-evaluator` audit
  (round 1 FAIL: the fix populated `doc_artifacts.name` but was never
  wired into `sync.py`'s real production call, so the real running tool
  still showed zero relations; round 2 PASS WITH NON-BLOCKING
  OBSERVATIONS, after the wiring was added and a self-mention exclusion
  plus a genericity guard — `_is_specific_enough`, rejecting a bare
  single-word title/stem like a project's own root README's `# ledgerkit`
  — were added to prevent the large-scale noise a naive wiring would
  have introduced, quantified live at 55 hypothetical edges, 50 of them
  "every doc mentions README"). **Confirmed working end-to-end against
  the real, live Ledgerkit repository**: 3 real `mentions_artifact`
  edges appear (`README.md` → `dev-docs/hledger-compatibility.md`;
  `dev-docs/compat-register/schema.md` → its own folder's `README.md`;
  a roadmap-migration doc → a real historical milestone doc), all
  independently confirmed genuine, none noise. **Honest residual
  limitation, not claimed to be fixed**: the original `CC-LK-001` three
  files still show zero relations to each other, because they
  cross-reference each other by *filename* in prose
  (`17-query-semantics-brief.md` cites `07-query-regex.md` by name), not
  by the target's H1 *title* text — the mechanism this phase built
  matches titles, not filenames, and that gap is real, separate, and
  unresolved. See `planning/retros/phase-55b-spec-doc-name-population.md`
  for the full account, including the retroactive process note (a
  dedicated plan file was written slightly after implementation began).
- **curation (Phase 55b closure, 2026-09-17, knowledge-curator):**
  closure claim independently re-derived from the real diff, not taken on
  the note's own word. Read `src/codecompass/spec_docs.py` directly:
  `_extract_title`/`_is_specific_enough`/`_H1_RE` exist exactly as
  described, and `scan_spec_docs` now calls `name=_extract_title(...)`
  for every row instead of leaving `name` unset — the original structural
  defect this entry named (every `spec_doc` row permanently excluded from
  `named_artifacts`) is gone. Read `src/codecompass/doc_mapping.py`
  directly: `build_doc_relations_edges` now has `if artifact.path ==
  row.path: continue` before the `named_artifacts` word-boundary check —
  the self-mention exclusion the closure note claims is real and present,
  not just described. Read `src/codecompass/sync.py` directly — this is
  the one claim most worth independently checking, since the note itself
  says round 1 shipped without it: `rebuild_project_graph`'s call to
  `build_doc_relations_edges` now passes
  `vendor_doc_rows + vendor_upstream_doc_rows + skill_doc_rows +
  spec_doc_rows` as the third (target) argument — `spec_doc_rows` is
  genuinely present, confirming the wiring fix landed, not just the
  population logic. Read `tests/test_sync.py` directly and confirmed the
  regression test that actually exercises this — not a unit test calling
  `build_doc_relations_edges` in isolation —
  `test_rebuild_project_graph_relates_two_spec_docs_to_each_other` calls
  `rebuild_project_graph` itself (the real production entry point) and
  asserts a genuine `mentions_artifact` edge between two spec docs; a
  sibling test,
  `test_rebuild_project_graph_excludes_a_generic_bare_project_name_readme_title`,
  covers the genericity-guard regression the closure note describes.
  `tests/test_doc_mapping.py` and `tests/test_spec_docs.py` both carry
  the matching unit-level coverage (title extraction, self-mention
  exclusion, cross-doc match) the retro's "Files" section claims.
  **Outcome: closure independently confirmed accurate** — this is not
  merely a plausible-sounding note, the diff genuinely closes what CG-004
  described (two already-tracked `spec_doc` rows can now mechanically
  relate to each other via `mentions_artifact`), through the real call
  site, with a real production-path regression test guarding the exact
  wiring gap round 1 missed. `status` stays
  `promoted-to-roadmap — fix implemented Phase 55b (2026-09-17)` — no
  further-terminal status exists per this queue's own status list (same
  reasoning `CG-002`'s Phase 49 closure note already applied). **Pending
  `promoted.md` line** (not yet added — Phase 55b's closeout commit has
  not landed as of this triage, per `git status`; the convention
  established at `CG-002`'s Phase 49 closure and `L-020`'s Phase 54
  triage is to add the pointer line once the commit exists, not before):
  `CG-004 | 2026-09-17 | detection-improvement |
  src/codecompass/spec_docs.py::_extract_title +
  src/codecompass/doc_mapping.py::build_doc_relations_edges
  (self-mention exclusion) +
  src/codecompass/sync.py::rebuild_project_graph (spec_doc_rows wiring)
  + tests/test_sync.py::test_rebuild_project_graph_relates_two_spec_docs_to_each_other
  @ <real short SHA>` — lead/`roadmap-context-curator` to add this line
  to `planning/learnings/promoted.md` once Phase 55b's own closeout
  commit lands.

### CG-003 — the external `hledger` reference manual (hledger.org) has zero representation, and unlike CG-002 no glob fix could ever cover it

- **origin:** Phase 46 (Ledgerkit genuine task — hledger 1.52 query-term
  semantics); observed by the lead attempting the task, verified by
  `reference-project-tester`.
- **date:** 2026-09-13
- **codecompass_revision:** b0717ee
- **project:** ledgerkit, pinned commit `9c33e37cf8a1eec057e1fb79a83e379d9413a189`
- **the edge:** `A ↔ B` where A = `https://hledger.org/1.52/hledger.html`
  (hledger's own external, versioned reference manual — the primary
  authority for hledger 1.52 query-term semantics), B = Ledgerkit's
  `context-graph.db` / any CodeCompass concept at all. A is not a
  package, not a file in the repository, not anything `discover_python()`
  or `spec_docs.py` could ever glob-match — it is an external web
  document CodeCompass has no representation for, in any form (not
  `doc_artifacts`, not `vendor`, not a Skill).
- **edge kind:** dependency↔local-code (the manual is Ledgerkit's actual
  compatibility authority for query semantics — see
  `dev-docs/planning/core-redefinition/07-query-regex.md`'s own citation
  of `hledger.org/1.52/hledger.html#queries`) — but of a *kind*
  CodeCompass's current model has no concept for at all: an external,
  versioned reference document that isn't a package and isn't in the
  repository.
- **agent's reasoning:** the task required hledger 1.52's `acct:`/`desc:`/
  `date:`/`depth:`/`status:`/`not:` query-term semantics. CodeCompass had
  zero representation of anything hledger-related (see `CG-002`).
  Ledgerkit's own internal planning doc happened to already have the
  answer (found by direct `grep`), but the *authoritative* source for
  this class of question is the external manual, not Ledgerkit's own
  prose about it — and CodeCompass could not point at it, fetch it,
  cache it, or relate it to anything, even in principle, with any
  mechanism that exists today.
- **what the graph shows instead:** nothing. There is no
  `doc_artifacts` row, no `vendor` row, no Skill, no edge of any kind
  referencing `hledger.org` or hledger's manual anywhere in
  `context-graph.db`.
- **could mechanical detection ever catch this?** no-conceptual-only —
  this is not a glob-coverage gap like `CG-002` (which a `_DEFAULT_GLOBS`
  entry could fix in one line, since `dev-docs/**/*.md` is a real path in
  the repository). An external manual is not on disk at all; representing
  it requires *fetching and vendoring external reference material*, a
  capability CodeCompass does not have in any form today
  (`decisions/0051`'s "graph capability" bucket, not "detection
  improvement").
- **smallest candidate that would fix it:** none at the detection level.
  This is squarely the open question a future Stage D/E phase (number
  unresolved — Phase 53 was retargeted to legacy-feature rationalisation
  on 2026-09-14; `ledgerkit-plan.md`) is designed to test — "can
  CodeCompass usefully index and relate reference material — the hledger
  manual (as fetched/vendored text) — to Ledgerkit's local
  implementation... as evidence nodes with provenance." This entry is the
  first concrete, evidenced instance of that hypothesis actually blocking
  a real task, ahead of that future phase's scheduled test.
- **classification:** graph-capability (Stage E / GATE DD) — matches
  `conditional-generalisation.md` §2.3's "reference-doc / spec / manual
  dependency kind" hypothesis row exactly.
- **status:** candidate
- **recurrence:** first occurrence
- **curation (Phase 46 triage, 2026-09-13, knowledge-curator):** template
  fields all present (origin, date, codecompass_revision, project, the
  edge, edge kind, reasoning, "what the graph shows instead", "could
  mechanical detection ever catch this?", smallest candidate,
  classification, status, recurrence) — independently checked rather than
  taken on the entry's own word: `context-graph.db`'s known schema
  (`doc_artifacts` rows of `kind='spec_doc'`, `vendor` usage/mention
  edges) has no table, column, or edge kind anywhere representing an
  external, non-package, non-repository reference document, confirming
  the "no-conceptual-only" claim. **Outcome: stays `candidate` — not
  `recurred`, and not `promoted-to-roadmap`.** Per
  `context-gaps/README.md`'s hard rule, a context-gap becomes
  authoritative only via promotion into either a mechanical-detection
  improvement (Stage C, GATE DB, Phase 47) or a new graph capability
  (Stage E, GATE DD, Phase 55) — CG-003's own classification
  (graph-capability) and its own "no glob fix could ever cover it"
  framing route it to the *latter*, so Phase 47's GATE DB has no lever to
  promote it even if it wanted to; that gate is scoped to Stage C /
  detection-improvements only (see `CG-002`, which *is* eligible there).
  Not `recurred` either: this is the first occurrence of *this specific*
  gap (an external reference manual with zero representation of any
  kind) — distinct in kind from `CG-002` (a detection-scope gap over
  material that already sits inside the repository) despite sharing an
  origin task and a hledger subject matter. Confirmed the two should stay
  separate, not merged: per CG-003's own reasoning, even a fixed CG-002
  "would only surface Ledgerkit's own prior *prose* about hledger" — the
  external manual itself remains unrepresented either way, so fixing one
  does not touch the other. `CG-002`'s independent re-confirmation by
  both agents in this same phase (noted in `CG-002`'s own entry, extended
  to nested `dev-docs/**` paths) is a separate signal and doesn't
  transfer to CG-003. This entry is treated as the first concrete,
  evidenced instance of the reference-doc/manual dependency-kind
  hypothesis already named in `conditional-generalisation.md` §2.3 and
  scheduled for a future Stage D/E phase's own test (number unresolved —
  Phase 53 was retargeted to legacy-feature rationalisation on
  2026-09-14) — real early evidence for that design question and for
  GATE DD's (Phase 55) eventual input, but not itself sufficient today to
  move past `candidate`. **Named for GATE DB's (Phase 47) input as
  context only, not as something GATE DB can act on**: Phase 47's
  findings should note CG-003 exists and explicitly why it is out of
  scope for any Stage C funding decision (it needs a Stage E ADR, not a
  detection heuristic), so the funding decision isn't misread as having
  addressed it. No entry made to `context-graph.db` — per the hard rule,
  a context-gap never enters there regardless of status. Revisit at that
  future Stage D/E phase, whenever it is scheduled (if the
  reference-manual-as-vendored-text test runs against this exact case) or
  on a second, independent occurrence (a different reference project
  hitting the identical "external manual, zero representation" shape) to
  move to `recurred`.
- **curation (Phase 47 GATE DB bulk review, 2026-09-13, knowledge-curator):**
  confirmed, as this entry's own prior triage already established, that
  GATE DB has no lever to act on this — it is squarely Stage E/GATE DD
  (Phase 55) territory (`planning/reference-projects/ledgerkit/findings.md`
  §5). No status change; named in the findings summary as context only.
- **note added Phase 54 (2026-09-16, `reference-project-tester`):**
  worth flagging as directly relevant context, not a new occurrence: the
  Phase 54 heterogeneous reference-material experiment
  (`planning/phase-54-heterogeneous-reference-material-experiment.md`)
  is exactly the future Stage D/E test this entry anticipated. It found
  that ingesting the manual as pinned, extracted text *is* detectable
  (`OBS-007`) but currently cannot be *related* to anything else in the
  graph (`CG-004`) nor correctly *classified* by provenance (`CG-005`) —
  i.e. CG-003's "zero representation of any kind" is no longer literally
  true once a project actually runs the ingestion experiment, but the
  practical result (no usable graph relationship reaching this material)
  is unchanged. Not merged with `CG-004`/`CG-005`: this entry is about
  the *raw external manual* having no representation path at all absent
  an ingestion step; `CG-004`/`CG-005` are about what happens *after*
  ingestion, a different pair of gaps this entry's own "smallest
  candidate" section correctly anticipated would need separate handling.
- **note added Phase 55 (2026-09-17, evidence reconciliation):** this
  entry's *sibling* claim — "no way to represent executable/behavioural
  technical dependencies" (named alongside the manual in this entry's
  own original framing, `conditional-generalisation.md` §2.3) — is now
  **independently corroborated from a real, live, non-CodeCompass-run
  instance**: Ledgerkit's own `validation/codecompass/findings/CC-LK-001`
  (Stage C Phase 2, 2026-09-16) reclassified a Stage C Phase 1
  compat-register entry (`LK-COMPAT-QUERY-DEPTH-001`, `compatible` →
  `intentional_divergence`) purely on executable evidence — running the
  pinned hledger 1.52.4 binary directly, not reading its manual or
  source — contradicting a claim that had looked correct from
  source-reading alone. Two real CLI bugs were also found the same way.
  CodeCompass has zero representation for any of this evidence class
  (no `doc_relations_edges`/`RELATION_LABELS` concept for "observed by
  running an executable," no `doc_artifacts.kind` for a reference
  executable). This is a **genuinely independent, different-mechanism**
  corroboration (real differential testing against a real binary, not
  CodeCompass-side reference-material ingestion) of the same underlying
  gap this entry already named — see
  `planning/phase-55-evidence-reconciliation.md`'s §D, which classifies
  this specific gap **DEFER pending cross-domain evidence**, not
  IMPLEMENT: two same-domain (hledger) instances are not yet sufficient
  to design a representation for, per that document's own §11 discipline
  (prove the abstraction generalises beyond hledger before building it).
  Status unchanged (`candidate`) — this is corroboration of an existing,
  already-classified gap, not grounds to promote past it on two
  same-project instances.

### CG-002 — Ledgerkit's entire `dev-docs/` tree is invisible to spec-doc detection, not merely under-related

- **origin:** Phase 45 (Ledgerkit registration + baseline); observed by the
  lead while running the baseline "what governs hledger-1.52 compatibility"
  question.
- **date:** 2026-09-12
- **codecompass_revision:** 6c3f34e (CodeCompass HEAD at the time)
- **project:** ledgerkit, pinned commit `a3cf2a77ca0075fabd4f7153d2a19f45c6e69b97`
- **the edge:** `A ↔ B` where A = the entire content of Ledgerkit's
  `dev-docs/**/*.md` tree (`architecture.md`, `api-spec.md`,
  `hledger-compatibility.md`, `SYNC.md`, and the whole
  `dev-docs/planning/core-redefinition/*.md` governance package — the
  documents that actually state what governs hledger-1.52 compatibility
  and the project's own development process), B = `context-graph.db`'s
  `doc_artifacts` table (`kind='spec_doc'`). A is **completely absent**
  from B, not merely unrelated to anything.
- **edge kind:** doc↔code (detection-scope gap, not a relationship gap
  between two already-indexed things)
- **agent's reasoning:** asked "what governs this project's hledger-1.52
  compatibility behaviour" as one of Phase 45's baseline questions.
  `codecompass query relations dev-docs/hledger-compatibility.md` → `error:
  'dev-docs/hledger-compatibility.md' not found in context-graph.db` —
  not "no relations found" (which is what `README.md` and
  `docs/journal-format.md` correctly returned), but "this file was never
  even considered a doc artifact." Confirmed by reading
  `src/codecompass/spec_docs.py::_DEFAULT_GLOBS` directly: the fixed glob
  list (`README.md`, `ARCHITECTURE.md`, `docs/**/*.md`,
  `architecture/**/*.md`, `decisions/**/*.md`, `spec/**/*.md`,
  `specs/**/*.md`, `rfcs/**/*.md`, `ai-docs/**/*.md`, a few root files) has
  no entry for a `dev-docs/` convention. This is the identical shape to
  the Phase 37 `ai-docs/` fix — "the module's own comment says it stays
  fixed until a real project shows it's wrong for it" — except this time
  the evidence comes from an *external* reference project (Ledgerkit),
  which is exactly Stage B's purpose.
- **what the graph shows instead:** nothing. `dev-docs/` produces zero
  `doc_artifacts` rows of any kind; every file under it is fully invisible
  to `query relations`, mechanical mention-detection, and any future
  AI enrichment pass alike.
- **could mechanical detection ever catch this?** yes-with-better-heuristics
  — add `"dev-docs/**/*.md"` to `_DEFAULT_GLOBS`, exactly the Phase 37
  precedent for `ai-docs/**/*.md`. A single-line, low-risk, deterministic
  fix if the pattern is judged general enough (not just a Ledgerkit
  special case — "dev docs" as a convention name is plausible across
  other real projects, unlike a Ledgerkit-specific term).
- **smallest candidate that would fix it:** a new glob entry in
  `spec_docs._DEFAULT_GLOBS`, no new table/edge kind, no ADR-level model
  change — a Stage C / GATE DB scale fix, not Stage E.
- **classification:** detection-improvement (Stage C / GATE DB)
- **status:** promoted-to-roadmap
- **recurrence:** second occurrence of the same failure shape.
  Independently re-verified against the module itself, not taken on this
  entry's own word: `src/codecompass/spec_docs.py`'s `_DEFAULT_GLOBS`
  comment reads "ship with this fixed default list, add configurability
  only once a real project shows it's wrong for it" (L19-21), and
  `CHANGELOG.md`'s "Fixed" section records "**Phase 37**:
  `spec_docs._DEFAULT_GLOBS` gains `\"ai-docs/**/*.md\"` — found live
  during this repo's own dogfooding sync right after Phase 35 created
  `ai-docs/README.md`/`ai-docs/CLAUDE.md`: neither was detected as a spec
  doc at all, so `query relations ai-docs/README.md` errored 'not found
  in…'" — the identical failure signature (a whole doc-directory
  convention absent from the fixed glob list → "not found", not "no
  relations") as this entry's Ledgerkit `dev-docs/` finding, confirmed
  line-for-line rather than assumed from the resemblance alone.
- **curation (Phase 45 triage, 2026-09-13, knowledge-curator):**
  template fields all present and independently checked (see recurrence
  verification above; `spec_docs.py::_DEFAULT_GLOBS` confirmed to still
  lack a `dev-docs/**/*.md` entry as of this triage). **Outcome:
  `candidate` → `recurred`, not `promoted-to-roadmap`.** Per
  `decisions/0051` / `context-gaps/README.md`'s hard rule, a context-gap
  "becomes authoritative only by promotion through the learning lifecycle
  into… a mechanical-detection improvement — a Stage C decision, gated on
  GATE DB (Phase 47)… Until then it is prose in this folder and nothing
  more" — so no glob-list edit is being made here, and the move to
  `recurred` is not a promotion, it is exactly the evidence-strengthening
  step `README.md`'s "How it feeds the gates" section describes ("A gap
  that recurs… is promoted from `candidate` to `recurred` and named in
  the GATE DB/DD input"). Judgment call flagged explicitly since the two
  occurrences differ in kind, not just in project: Phase 37's instance
  predates the `context-gaps/` mechanism entirely (introduced Phase 43c)
  and was fixed directly as ordinary dogfooding, not filed as a `CG-NNN`
  entry — so this is not a literal second `CG` filing of the same gap,
  it is the same underlying pattern (a hand-maintained fixed glob list
  blind to an as-yet-unseen doc-directory convention) demonstrated twice,
  once via CodeCompass's own dogfooding and once via an external
  reference project. Given Stage B's whole purpose is exactly this kind
  of external corroboration of a previously internal-only finding, and
  given the failure signature is verified identical rather than merely
  similar, this is treated as sufficient to strengthen the signal for
  GATE DB's Phase 47 review, without being over-read as two independent
  external occurrences. **Named for the GATE DB (Phase 47) input:** this
  supports funding a Stage C phase that generalises `_DEFAULT_GLOBS`
  handling (e.g. a `vendor.toml`-configurable spec-doc glob list, or a
  wider default set) rather than continuing to patch one hard-coded entry
  per newly-discovered project convention — see also `conditional-
  generalisation.md` §1.2's hypothesis table (no exact row match today;
  closest is the general "detection-improvement" bucket, not a specific
  named hypothesis — worth GATE DB considering whether it deserves one).
  **Not implementing the glob-list fix now** — that would pre-empt GATE
  DB's funding decision, which is explicitly Phase 47's job, not this
  triage's.
- **curation (Phase 47 GATE DB bulk review, 2026-09-13, knowledge-curator):**
  recurrence independently re-confirmed a third time beyond this entry's
  own two occurrences: Phase 37's `ai-docs/**/*.md` fix (this repo's own
  dogfooding, predating the `context-gaps/` mechanism) is the identical
  failure shape one phase earlier again — a hand-maintained glob list
  blind to an unanticipated doc-directory convention, demonstrated once
  internally (Phase 37) and now twice externally (Phase 45 + Phase 46, this
  entry). **GATE DB recommendation (full reasoning + evidence:
  `planning/reference-projects/ledgerkit/findings.md` §4/§7): fund a
  narrow Stage C phase adding a single `"dev-docs/**/*.md"` entry to
  `_DEFAULT_GLOBS`** — the smallest model that covers the demonstrated
  need, per `conditional-generalisation.md`'s discipline — **not** the
  more general `vendor.toml`-configurable glob list this entry's own
  Phase 45 note raised as a candidate; two hard-coded entries earned
  (`ai-docs/`, `dev-docs/`) does not yet justify building configurability
  infrastructure. Bundle with `L-016`'s fix (shared root cause/code
  path). **Status stays `recurred`, not `promoted-to-roadmap`** — this is
  a recommendation for the lead/user to ratify at GATE DB, not yet a
  Stage C phase that owns it; move to `promoted-to-roadmap` once that
  phase's plan file exists.
- **GATE DB ratified (lead, 2026-09-13):** user approved the
  recommendation as written. `planning/phase-49-spec-doc-coverage-and-error-disambiguation.md`
  now exists and owns this gap — status moved to `promoted-to-roadmap`
  accordingly. Per `context-gaps/README.md`'s "How it feeds the gates,"
  the `promoted.md` pointer (+ commit hash) is added once Phase 49's
  implementation actually lands, not at plan-file creation time.
- **curation (Phase 49 closure, 2026-09-13, knowledge-curator):** fix
  confirmed landed — independently verified by reading
  `src/codecompass/spec_docs.py::_DEFAULT_GLOBS` directly rather than
  taking the phase's own report on its word: `"dev-docs/**/*.md"` is now
  present, appended immediately after `"ai-docs/**/*.md"`, exactly the
  smallest-candidate fix this entry itself recommended. Regression
  coverage confirmed:
  `tests/test_spec_docs.py::test_scan_spec_docs_finds_dev_docs_directory`
  (asserts both a top-level and a nested `dev-docs/**` path resolve,
  covering this entry's own "independently re-confirmed to extend past
  top-level `dev-docs/` files" note). Also live-verified against the
  actual pinned Ledgerkit clone per
  `planning/phase-49-spec-doc-coverage-and-error-disambiguation.md`'s
  retro ("What was achieved" #4): `dev-docs/hledger-compatibility.md`
  and a nested `dev-docs/planning/core-redefinition/07-query-regex.md`
  now resolve to an honest empty "no relations" table instead of the
  "not found" this gap originally evidenced. **Status decision:** checked
  `context-gaps/README.md`'s status list carefully —
  `candidate` → `recurred` → `promoted-to-roadmap` / `discarded` — there
  is no further, more-terminal status defined for "the owning phase's
  implementation has actually landed"; `promoted-to-roadmap` already
  means "a Stage C/E phase now owns/owned this," which remains true and
  correct once that phase's fix ships. **Status stays
  `promoted-to-roadmap`** — this note records that the fix has landed,
  not a new state transition. `promoted.md` pointer added this same
  triage: `CG-002 | 2026-09-13 | detection-improvement |
  src/codecompass/spec_docs.py::_DEFAULT_GLOBS +
  tests/test_spec_docs.py::test_scan_spec_docs_finds_dev_docs_directory @
  780e97b`.
- **note added Phase 54 (2026-09-16, `reference-project-tester`):**
  independently re-confirmed the fix still holds and generalizes to a
  materially different content source: the Phase 54 heterogeneous
  reference-material experiment materialized six *externally-extracted*
  reference files (not Ledgerkit-authored prose) under
  `dev-docs/hledger-reference/*.md` in a scratch copy, and all six were
  detected with zero code change (`OBS-007`) — corroborating evidence
  this fix's benefit extends beyond its original motivating case.

### CG-001 — one feature spread across three `src/` modules, with no edge joining them

- **origin:** Phase 43 (`query skills` widen); observed by the lead while
  scoping `43a`. Re-surfaced as the motivating case for Phase 43c /
  `decisions/0051`.
- **date:** 2026-09-11
- **codecompass_revision:** f47f3e2 (observed against d34a486, the Phase 43 change)
- **project:** codecompass (own dev)
- **the edge:** `A ↔ B ↔ C` where
  A = `src/codecompass/graph.py::skills_index` (+ `_SKILLS_INDEX_KINDS`),
  B = `src/codecompass/cli.py::query_skills`,
  C = `src/codecompass/skill.py::render_tool_skill` (the generated
  tool-Skill's `query skills` description).
- **edge kind:** local-code↔local-code (one feature, three modules)
- **agent's reasoning:** widening `query skills` to surface `cursor_mdc` +
  `slash_command` rows meant a coordinated change in all three: the SQL +
  kind tuple in `graph.py`, the table column + `--json` field in
  `cli.py`, and the prose describing the command in `skill.py` (which is
  rendered into `.claude/skills/codecompass/SKILL.md`). Miss any one and
  the command drifts from its own documentation — which is exactly the
  Phase 17 gap that made `43a` necessary, and exactly the L-005 failure
  (`docs-maintainer` edited the generated file, not the generator). An
  agent picking up "change what `query skills` returns" has to
  *reconstruct* this trio by reading code; CodeCompass, whose whole
  pitch is "the context layer", cannot point at it.
- **what the graph shows instead:** none. `src/codecompass/*.py` files
  are not nodes in `context-graph.db` at all — it tracks
  vendor→code usage edges and spec-doc→dependency mention edges, not
  intra-`src` feature groupings. `codecompass query relations
  src/codecompass/skill.py` → `error: 'src/codecompass/skill.py' not
  found in context-graph.db` (verified, f47f3e2).
- **could mechanical detection ever catch this?**
  partially — **yes-with-better-heuristics** for the B↔C link (a
  generated artifact and its generator: `skill.py` writes
  `SKILL.md`, and the string it emits names `query skills`; a
  "generator emits a string naming a CLI command" scan is deterministic
  and is close to Phase 43b's planned
  `check_generated_artifacts_match_source`). The A↔B link (`cli.py`
  imports and calls `graph.skills_index`) *is* a plain import edge a
  code-graph would have — CodeCompass just doesn't build a code-graph of
  its own source. The "these three form one feature" framing is
  **no-conceptual-only**.
- **smallest candidate that would fix it:** `conditional-generalisation.md`
  §2.6 (task-oriented retrieval edges) for the feature-grouping framing;
  a narrower "generated-artifact ↔ generator ↔ named CLI command" heuristic
  (§2.1-adjacent) for the mechanical part. Unclear which is worth it —
  that is the GATE DB call.
- **classification:** unsure (detection-improvement for the mechanical
  part; graph-capability for the feature-grouping part)
- **status:** candidate
- **recurrence:** first occurrence (but note: the *pattern* — a
  coordinated multi-module change where the graph gave no help — is what
  L-005 and the Phase 17 gap were both about)
- **curation (Phase 43c triage, 2026-09-11, knowledge-curator):**
  Template fields all present (origin, date, codecompass_revision,
  project, the edge, edge kind, reasoning, what-the-graph-shows-instead,
  "could mechanical detection ever catch this?", smallest candidate,
  classification, status, recurrence). **Provenance verified
  independently by code-trace (no Bash):** `codecompass query relations`
  (`src/codecompass/cli.py:793`) accepts only "a spec-doc path, a vendor
  name, or a Skill/doc-artifact name"; `_resolve_relations` returns
  `None` for anything else, which calls `_not_found_error`
  (`cli.py:459`) printing exactly `error: 'src/codecompass/skill.py' not
  found in context-graph.db`. `src/codecompass/*.py` modules are not
  nodes in `context-graph.db` at all — the graph holds spec-doc / vendor
  / doc-artifact nodes and their mention + usage edges
  (`doc_relations_edges`, `doc_code_trace`), not intra-`src` code
  structure — so the "the graph cannot represent this" claim stands as
  written. The A↔B (`cli.py` → `graph.skills_index`) import edge and the
  B↔C (a generator emitting a string that names a CLI command) link are
  both real relationships; only the "these three are one feature"
  framing needs understanding rather than pattern-matching.
  **Outcome: `candidate`** — first occurrence, single observer; the
  L-005 / Phase 17 resemblance is a pattern echo, not a second
  context-gap. Needs a second occurrence, or an independent second
  observer, to move to `recurred` and be named in the GATE DB/DD input.
  **Classification: `unsure`, split confirmed** —
  (a) *detection-improvement (Stage C / GATE DB)* for the B↔C
  generated-artifact ↔ generator ↔ named-CLI-command link, which
  overlaps Phase 43b's planned `check_generated_artifacts_match_source`;
  and (b) *graph-capability (Stage E / GATE DD)* for the
  feature-grouping framing — `conditional-generalisation.md` §2.6
  (task-oriented retrieval edges). Recorded as the first datapoint for
  the `README.md` hypothesis-table row "the 'one feature, N modules' map
  can't be built from existing graph data" (§2.6).
- **curation (Phase 47 GATE DB bulk review, 2026-09-13, knowledge-curator):**
  cross-referencing across all Phase 44–46 evidence in bulk surfaced a
  weak, conceptually-adjacent echo: Ledgerkit task 01's
  `reference-project-tester` finding notes "no Skill mentions hledger or
  query semantics… no 'what matters for this task' retrieval yet" — the
  same §2.6 hypothesis (task-oriented retrieval edges) this entry's own
  classification already names, but a different concrete edge/kind, on a
  different project, from a different observation shape (an absence noted
  in passing while evaluating an unrelated FAIL, not an agent hitting a
  missing edge while doing multi-module work). Per `context-gaps/README.md`'s
  own standard ("recurs, or is filed independently by two agents"), this
  is judged **not sufficient** to move this entry to `recurred` — it is
  not the same edge recurring, only the same broader hypothesis being
  touched from a different angle. Recorded here as a cross-reference for
  Phase 55/GATE DD's benefit (`planning/reference-projects/ledgerkit/findings.md`
  §6), not a promotion. Status unchanged: `candidate`, still needs a
  genuine second occurrence or independent second observer of *this*
  edge shape.
