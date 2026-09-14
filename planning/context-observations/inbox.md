# Context-observations inbox

The live queue. New entries at the top. Format: `TEMPLATE.md`.
Rules: `README.md`. Supersedes `planning/context-use-log.md` (Phase 43c)
as of Phase 52 — see that file for its own pointer note.

Statuses: `recorded` → `investigating` → `resolved`.

---

### OBS-006 — Phase 52 lifecycle demo, cycle 2: new mechanical edge enriched, cache-hit rejection proven, cycle 1's audit trail confirmed untouched by rebuild

- **origin:** Phase 52 (context edge lifecycle demonstration, local fixture), `context-enrichment-agent` + lead
- **date:** 2026-09-14
- **codecompass_revision:** working tree at Phase 52 (pre-commit)
- **project:** codecompass (own dev) — local fixture, cycle 2 (a third `dev-docs/*.md` file added and re-synced)
- **edge identity:** `dev-docs/architecture.md -- mentions_artifact --> .claude/skills/codecompass/SKILL.md` (new this cycle); `dev-docs/retros/README.md -- mentions_artifact --> .claude/skills/codecompass/SKILL.md` (re-tested for cache-hit rejection)
- **observation type:** EDGE_USEFUL (the new edge's enrichment); the cache-hit rejection test is a mechanism-correctness check, not itself an edge-quality observation
- **edge correctness:** correct — the new edge and its enrichment were independently verified against the real source text.
- **task usefulness:** useful.
- **default pathway:** n/a — this cycle's purpose was verifying the lifecycle mechanism itself (queue → agent enrichment → `enrich apply`'s trust-boundary enforcement → audit persistence across a rebuild), not a retrieval-speed comparison.
- **advantage:** MODERATE — same reasoning as `OBS-005`: the value is durable, attributed interpretation surviving a graph rebuild, confirmed directly (byte-identical `doc_relation_enrichment` rows for the two untouched cycle-1 edges after `rebuild_deterministic` ran again).
- **wrong or misleading?** no, **with one honest complication recorded, not hidden**: an intermediate step (resubmitting `dev-docs/retros/README.md`'s already-enriched edge) was unexpectedly *accepted* rather than rejected, due to a one-time content-hash difference traced to this fixture's own bootstrap order (a hand-placed placeholder Skill file mechanically overwritten mid-sync) — filed as `L-019`. Not a defect in `enrich apply`'s enforcement: `select_candidates` correctly judged the edge genuinely changed given the real `target_text` difference at that moment. A clean re-submission once the transient settled correctly produced `applied 0, rejected 2`, exit code 1 — the trust boundary demonstrated working as designed.
- **status:** resolved
- **investigation:** root-caused live, not deferred (`DEMO.md` step 9); classification `retrieval_issue`-adjacent but scoped to test methodology, not the graph/detection layer — hence filed as a learning (`L-019`), not a `context-gaps` entry.
- **resolution:** `L-019` filed (`scoped-rule`, candidate). No CodeCompass code change warranted — the mechanism behaved correctly given real, if unintentional, input differences.
- **curation (Phase 52 triage, 2026-09-14, knowledge-curator):** field
  completeness confirmed against `TEMPLATE.md` (origin, date,
  `codecompass_revision`, project, edge identity, observation type, edge
  correctness/task usefulness kept as two separate fields as required,
  status, investigation, resolution — all present). `status: resolved`
  independently confirmed correct, not just accepted as pre-filled: the
  new-edge enrichment half is a plain `EDGE_USEFUL` (record-only per this
  agent's own investigate-vs-record table — no investigation obligation);
  the honest complication was already root-caused live in the same
  session (`DEMO.md` step 9) and correctly routed to `L-019` as a
  process/fixture-methodology finding rather than an edge/detector defect
  — re-opening an investigation here would duplicate, not strengthen,
  that root-cause trace. `L-019` itself independently re-verified this
  same phase (see `planning/learnings/inbox.md`'s L-019 curation note) —
  no discrepancy between the two records. No further action.

### OBS-005 — Phase 52 lifecycle demo, cycle 1: mechanical edge → agent-driven enrichment → visible, correctly attributed

- **origin:** Phase 52 (context edge lifecycle demonstration, local fixture — `tests/fixtures/ledgerkit_lifecycle_demo/`), `context-enrichment-agent` (invoked by the lead, no `ANTHROPIC_API_KEY` available in this environment — `decisions/0054`)
- **date:** 2026-09-14
- **codecompass_revision:** `cea0b1c` (pre-Phase-52 HEAD; this cycle ran against the working tree containing Phase 52's own `enrich apply` addition)
- **project:** codecompass (own dev) — a local fixture mimicking Ledgerkit's real, independently-confirmed Stage A content (two `dev-docs/**/*.md` files mentioning the `codecompass` Skill by name, the same pattern Phases 45/46 found real in the actual Ledgerkit clone)
- **edge identity:** `dev-docs/retros/README.md -- mentions_artifact --> .claude/skills/codecompass/SKILL.md`; `dev-docs/planning/README.md -- mentions_artifact --> .claude/skills/codecompass/SKILL.md`
- **observation type:** EDGE_USEFUL
- **edge correctness:** correct — both mechanical edges accurately reflect real word-boundary mentions in the fixture's own files, confirmed by direct inspection of the source text before writing enrichment.
- **task usefulness:** useful — `codecompass query relations` correctly went from "mentioned, not yet enriched" to showing a grounded `ai_summary` explaining *how* each doc relates to the Skill (a process/governance citation, not a runtime dependency), which is exactly the interpretive value enrichment is meant to add.
- **default pathway:** reading each file directly (as done here to ground the enrichment) is always available and was in fact used *to produce* the enrichment — this observation isn't claiming CodeCompass beat direct inspection, it's confirming the enrichment *mechanism itself* (queue → agent-authored content → `enrich apply` → visible) works end-to-end, per `decisions/0054`.
- **advantage:** MODERATE — the value here isn't retrieval speed, it's that the interpretive summary now persists in the graph for a *future* agent to read via `query relations` without re-deriving it from scratch each time, and is clearly attributed (`model = 'agent:context-enrichment-agent'`) so a reader can tell it apart from automated-API enrichment.
- **wrong or misleading?** no — both summaries were independently re-verifiable against the real source text at write time and remained accurate when re-read via `query relations` afterward.
- **status:** resolved
- **investigation:** none needed — this is a successful mechanism demonstration, not a friction report.
- **resolution:** no action — recorded as evidence that `decisions/0054`'s agent-driven enrichment pathway works as designed. See `tests/fixtures/ledgerkit_lifecycle_demo/DEMO.md` for the full transcript, including cycle 2.
- **curation (Phase 52 triage, 2026-09-14, knowledge-curator):** field
  completeness confirmed against `TEMPLATE.md` (all fields present,
  edge-correctness/task-usefulness kept separate as required).
  `status: resolved` confirmed correct: `EDGE_USEFUL` is a record-only
  case per this agent's own investigate-vs-record rule — no investigation
  was owed, and none was skipped improperly. No further action.

### OBS-004 — `query vendors`/`query relations` against Ledgerkit returned a complete zero for the genuine query-semantics task, not a thin result

- **origin:** Phase 46 (Ledgerkit genuine task — hledger 1.52 query-term semantics), `reference-project-tester`
- **date:** 2026-09-13
- **codecompass_revision:** `9c33e37` (Ledgerkit pinned commit; CodeCompass HEAD at the time)
- **project:** ledgerkit, pinned `9c33e37cf8a1eec057e1fb79a83e379d9413a189`
- **edge identity:** `dev-docs/hledger-compatibility.md -- (any) --> (absent from graph)`; `dev-docs/planning/core-redefinition/07-query-regex.md -- (any) --> (absent from graph)` — both files existed on disk and answered the task, neither was a tracked `doc_artifacts` row at all (`CG-002`'s root cause: no `dev-docs/**/*.md` glob entry).
- **observation type:** EDGE_MISLEADING
- **edge correctness:** incorrect — the "not found" response implied non-existence for files that demonstrably exist and are load-bearing.
- **task usefulness:** n/a (nothing was returned to be useful or not).
- **default pathway:** `grep -rn "query" dev-docs/planning/core-redefinition/` (seconds) found `07-query-regex.md` directly; reading its §7.1 table answered all 6 terms plus phasing, with no CodeCompass involvement at any point. Strictly faster and strictly more complete than the CodeCompass path, which returned nothing.
- **advantage:** LOW — at the floor: the contribution was exactly zero, not merely marginal; the entire answer came from Ledgerkit's own prior planning work, found by one `grep`.
- **wrong or misleading?** partially at filing time; confirmed **yes** once cross-referenced against `context-quality-evaluation.md`'s "incorrect outranks incomplete" rule — an honest "not found" for both paths is not a false claim in the strict sense, but per `L-016`, re-confirmed here, the "not found" error gives no signal that this is a known glob-coverage gap rather than a typo.
- **status:** resolved
- **investigation:** root cause traced to `spec_docs.py::_DEFAULT_GLOBS` (`CG-002`, already `recurred` at time of filing — this observation is corroborating evidence for that entry, not a separate investigation). Classification: `detector_gap`.
- **resolution:** `CG-002` → `promoted-to-roadmap` → Phase 49 (`src/codecompass/spec_docs.py::_DEFAULT_GLOBS` gained `"dev-docs/**/*.md"`) → re-verified fixed at Phase 51 (GATE DC).

### OBS-003 — Ledgerkit baseline: 0 vendors correctly reported, but the hledger-compatibility doc was invisible, not just unrelated

- **origin:** Phase 45 (Ledgerkit registration + baseline), lead
- **date:** 2026-09-12
- **codecompass_revision:** `6c3f34e`
- **project:** ledgerkit, pinned `a3cf2a77ca0075fabd4f7153d2a19f45c6e69b97`
- **edge identity:** `README.md -- (any) --> (none)`, `docs/journal-format.md -- (any) --> (none)` (correctly tracked, zero relations — honest); `dev-docs/hledger-compatibility.md -- (any) --> (absent from graph)` (the real problem).
- **observation type:** EDGE_MISLEADING (for the `dev-docs/` case only — the `README.md`/`docs/journal-format.md` results were honest `EDGE_USEFUL`-adjacent non-findings, not recorded as separate entries here since nothing was wrong with them).
- **edge correctness:** incorrect (for `dev-docs/hledger-compatibility.md`'s "not found" specifically).
- **task usefulness:** n/a.
- **default pathway:** `grep -rn "dependencies" pyproject.toml` for the dependency question (one line, `dependencies = []`); `find dev-docs -name "*.md"` + reading `dev-docs/hledger-compatibility.md` directly for the compatibility question — both at least as fast as CodeCompass here, and the second one strictly better, since CodeCompass currently cannot see that file at all.
- **advantage:** LOW — for the dependency question, an honest expected outcome. For the compatibility-governance question, CodeCompass was strictly worse than direct inspection — the first real Stage B datapoint of that shape.
- **wrong or misleading?** partially — not a false claim in isolation, but silently omitting an entire real spec-doc directory (vs. accurately reporting "no relations" for the docs it does see) could read as "nothing governs this" to an agent that doesn't know to check the glob list. Filed as `CG-002` at the time.
- **status:** resolved
- **investigation:** this is `CG-002`'s original filing occurrence.
- **resolution:** `CG-002` → Phase 49 fix → Phase 51 GATE DC confirmed working.

### OBS-002 — own-dev instrument dry-run: `query symbol Typer` was accurate but undersold the vendor's real usage breadth

- **origin:** Phase 44 (reference-project protocol, instrument dry-run), lead
- **date:** 2026-09-12
- **codecompass_revision:** freshly-rebuilt `context-graph.db` at Phase 44's own HEAD
- **project:** codecompass (own dev)
- **edge identity:** `typer -- symbol_usage --> Typer` (`src/codecompass/cli.py:51`,`:54`) — correct and grounded, but only 2 of the vendor's 43 total real usages.
- **observation type:** EDGE_UNHELPFUL (incomplete relative to the actual question, "what does this project use `typer` for," though accurate for what it did show).
- **edge correctness:** correct — version, usage count, and both `used_at` line numbers were independently re-verified against `src/codecompass/cli.py` and matched exactly.
- **task usefulness:** irrelevant-to-this-task in the sense of "insufficient" — a single-symbol query cannot answer a whole-vendor-usage question by design.
- **default pathway:** `grep -n "import typer\|typer\.Typer(" -r src/codecompass/` to find the two call sites, then `pip show typer` (or read `pyproject.toml`'s pin) for the version, then read `typer`'s own README/docstring for what `Typer` does. ~3 commands, all obvious for a repo this small.
- **advantage:** LOW — the instrument's own self-test case (`_instrument-dry-run.md`), chosen because it's small and well-understood; CodeCompass packaged the same facts one command sooner but surfaced nothing a quick grep + `pip show` wouldn't have.
- **wrong or misleading?** no.
- **status:** resolved
- **investigation:** filed as candidate learning `L-012` at the time (self-test only, not a reference-project finding).
- **resolution:** `L-012` retained through Phase 47, discarded at Phase 51 (7 phases old, three unclaimed reference-project corroboration opportunities, self-test-only by design — lifecycle's "~3 phases, no new evidence" norm applied).

### OBS-001 — `query skills` widen: mechanical row-count check, no CodeCompass involvement issue

- **origin:** Phase 43 (`43a`, `query skills` widen), lead
- **date:** 2026-09-10
- **codecompass_revision:** own-repo HEAD at Phase 43
- **project:** codecompass (own dev)
- **edge identity:** `graph.skills_index` query output (5 rows → 9 rows after the `kind IN (...)` widen) — not a single edge, a query-shape check.
- **observation type:** EDGE_USEFUL (as a fast confidence check during development, not a context-quality claim).
- **edge correctness:** correct — the row counts were accurate and matched the post-change test assertions (9 rows) exactly.
- **task usefulness:** useful (as a quick self-check while implementing the change itself).
- **default pathway:** `grep -rn "doc_artifacts" src/codecompass/graph.py` to find the `skills_index` query, read it to see the `WHERE kind = 'skill'` filter, then `sqlite3 context-graph.db "SELECT kind, count(*) FROM doc_artifacts GROUP BY kind"` to see what kinds actually exist. ~3 commands, all obvious.
- **advantage:** LOW — the default pathway is short and an agent touching this code would run it anyway; `query skills` packaged the same facts one command sooner. Honest expected result for a change inside CodeCompass's own query layer — dogfooding the tool on the tool is a hard case for it.
- **wrong or misleading?** no.
- **status:** resolved (no further action was ever warranted).
- **investigation:** none needed.
- **resolution:** no action — recorded as evidence.

<!-- Phases 39–42 predate this instrument entirely (introduced Phase
     43c) and are not backfilled, per that phase's own "Explicitly
     deferred" scope. Migrated verbatim from planning/context-use-log.md
     at Phase 52 — see that file's own pointer note for provenance. -->
