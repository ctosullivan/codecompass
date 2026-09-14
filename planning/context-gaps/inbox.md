# Context-gaps inbox

The live queue. New entries at the top. Format: `TEMPLATE.md`.
Rules: `README.md`, `decisions/0051`. **Nothing here is ever written to
`context-graph.db`.**

Statuses: `candidate` → `recurred` → `promoted-to-roadmap` / `discarded`.

---

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
