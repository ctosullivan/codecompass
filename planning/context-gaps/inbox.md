# Context-gaps inbox

The live queue. New entries at the top. Format: `TEMPLATE.md`.
Rules: `README.md`, `decisions/0051`. **Nothing here is ever written to
`context-graph.db`.**

Statuses: `candidate` → `recurred` → `promoted-to-roadmap` / `discarded`.

---

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
