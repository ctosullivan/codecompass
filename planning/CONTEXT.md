# Project context

This file reflects the *current* state of the project — overwritten at
each stopping point, not appended to. See `CHANGELOG.md` and git history
for the log of how it got here.

## Current phase

**A planning session has redefined what "CodeCompass v1" means.** Phases
0-38 are all `done` and unchanged — they are now framed as the
**foundation** (the npm/PyPI/Cargo package-source-grounding tool). The
former "v1.0" (Phase 23 = publish that tool to PyPI) is superseded:
**all publishing is held until the redefined v1** (user decision,
2026-09-09) — CodeCompass has never been published, and the first-ever
PyPI release will be the redefined v1 as `1.0.0`. "CodeCompass v1" is
redefined as a *product-validation milestone*: CodeCompass developed
agent-led, validated against real external reference-project work
(**Ledgerkit, then Technical Clipper** — reordered 2026-09-12, see
below; **the Technical Clipper leg was itself retargeted 2026-09-17,
`decisions/0056` — see "Next concrete step"**), improved from that
evidence, generalised only as far as evidence justifies, then released
after blank-slate doc reconstruction and an independent audit.

**2026-09-12 realignment** (`planning/v1-redefinition/realignment-2026-09.md`)
reassessed and reordered the remaining roadmap, then **all three gates
were approved the same day** ("Proceed as recommended"). **Ledgerkit is
now Stage B** (was Technical Clipper) — its dependency shape (hledger
executable, manuals, journal syntax, compatibility tests) is the
stronger test of CodeCompass's distinctive value, confirmed by live
re-inspection (hledger: `GPL-3.0-or-later`, stable 1.52.4; Ledgerkit:
MIT, single-copyright, Milestone 5 "CLI Filter Flags" `[PLANNED]` next).
**Technical Clipper moves to a new Stage F** (cross-ecosystem
regression, run after Ledgerkit-driven changes land). Phases 39–43c
unchanged/`done`/not renumbered; phases 45–67 (none started) renumbered
45–70. **`decisions/0052`** (the reorder, gate G11) is `Accepted`.
**Two new Stage-A bridge phases, both `done`: 43d and 43e.** Phase 43d
executed the GPL-3.0-or-later relicensing (gate G12): CodeCompass is now
licensed **GPL-3.0-or-later** (was MIT) — `LICENSE` (canonical text,
fetched verbatim from `hledgerorg/hledger`'s own file), `pyproject.toml`,
`README.md`, `CONTRIBUTING.md` updated; `decisions/0053` `Accepted`;
verified live (`pip show codecompass` → `License: GPL-3.0-or-later`).
Phase 43e approved `adoption-blueprint.md` as the version handed to
Ledgerkit (gate G13) — content unchanged from the prior commit, only the
gate resolved. Both phases' closeout: `docs-reconstructor` drift audit →
**NO DRIFT**; `knowledge-curator` triage filed **L-009** (fetch
canonical upstream text for byte-fidelity, retained) and **L-010** (a
reusable document should cite its justifying incidents + state a
revision policy, retained). New planning artifacts:
`licence-migration.md`, `adoption-blueprint.md`,
`codecompass-feedback-ingestion.md`. **No `src/` change either time.**

**Phase 44 is `done` (2026-09-12) — Stage B has begun.** The
reference-project protocol and context-quality evaluation spec are now
operational, not just prose: new `planning/reference-projects/README.md`
(registry), `TEMPLATE-registration.md`, `TEMPLATE-evaluation.md`, and a
real instrument dry-run (`_instrument-dry-run.md`, CodeCompass's own
`typer` usage evaluated against itself — verdict **PASS WITH GAPS**,
advantage **LOW**: no incorrect/misleading content, but single-symbol
`query symbol` scope undersold `typer`'s actual usage breadth, filed as
**L-012**, retained). The `context-evaluator`/`reference-project-tester`
briefs were verified already consistent with the new templates (a side
effect of Phase 43c's own brief updates — no edit needed).
`planning/phase-45-ledgerkit-baseline.md` written, retargeted to
Ledgerkit's real current state (Milestone 5 "CLI Filter Flags"
`[PLANNED]` next). **No `src/codecompass/` change.** Closeout:
`docs-reconstructor` drift audit → **NO DRIFT**; `knowledge-curator`
triage of L-012 (retained), **L-013** (promoted), L-014 (discarded);
`release-phase-auditor` → **PASS WITH NON-BLOCKING OBSERVATIONS** (no
blocking gap). Verified: `pytest` 554 passed / 2 skipped, `ruff check .`
clean, `check_user_docs.py --strict` clean. **Undocumented decision
surfaced this phase, now recorded:** L-013's promotion amended
`planning/agent-led-workflow.md` steps 10 and 14 — step 10 is now an
explicit *interim* roadmap/context reconciliation (it never flips
`ROADMAP.md` to `done`, since the retro/triage/audit steps that DoD
requires haven't run yet at that point); step 14 is the *final*
done-flipping reconciliation, run once per phase after the retro (11),
triage (12), and completion audit (13). This dispatch is the first real
exercise of the amended step 14. Retro:
`planning/retros/phase-44-reference-project-protocol.md`. `ROADMAP.md`
row 44, the `v1-redefinition/roadmap.md` Phase 44 stanza, and the phase's
own plan-file status line all now read `done`. **No gate blocks Phase
45** — Stage B continues.

**Phase 45 is `done` (2026-09-13) — CodeCompass's first external
reference-project datapoint, and its first-ever FAIL verdict.**
Registered **Ledgerkit** at a pinned commit
(`a3cf2a77ca0075fabd4f7153d2a19f45c6e69b97`) into a scratch location
outside this repo (`planning/reference-projects/ledgerkit.md`), reconfirmed
live rather than trusting the stale 2026-09-12 desk assessment — Ledgerkit
had undergone its own "Core redefinition" the same day, superseding
Milestone 5 "CLI Filter Flags" (the task the desk assessment and Phase
46's own draft plan were built around) into a new Stage C. `context-evaluator`
produced a 3-question baseline report (`ledgerkit/00-baseline.md`): Q1
(runtime dependencies) and Q3 (roadmap state) both PASS WITH GAPS / LOW
advantage, honest expected-thin results; **Q2 (what governs hledger-1.52
compatibility) is a FAIL** — `codecompass query relations
dev-docs/hledger-compatibility.md` returned a confident "not found in
context-graph.db" for a real, current, 238-line file that is precisely
Ledgerkit's own designated compatibility-governance document, rather than
an honest empty result. Root cause (`spec_docs.py::_DEFAULT_GLOBS` has no
`dev-docs/**/*.md` entry) filed as **CG-002** (triaged to `recurred` — the
same failure shape as Phase 37's `ai-docs/` fix, this time surfaced by an
external reference project, not promoted to a roadmap row — that's Phase
47/GATE DB's job). A distinct symptom-layer finding — `query relations`'s
"not found" is indistinguishable from a genuine typo — filed as **L-016**
(retained); Q1's optional-dependencies-silence finding filed as **L-015**
(retained). `context-health-planner`'s first genuine solo run
(`planning/context-health.md`, tracked forward from Phase 43c) predicted
LOW context-advantage for Phase 46, with CG-002 directly load-bearing.
**No `src/codecompass/` change.** Verified: `pytest` 554 passed / 2
skipped, `ruff check .` clean, `check_user_docs.py --strict` clean.
Closeout: `docs-reconstructor` drift audit
(`planning/retros/_drift-audit-phase-45.md`) → **NO DRIFT**;
`knowledge-curator` triage → CG-002 (`recurred`), L-015 (`retained`),
L-016 (`retained`); `release-phase-auditor`
(`planning/retros/_audit-phase-45.md`) → **PASS WITH NON-BLOCKING
OBSERVATIONS** (no blocking gap; three advisory notes — the step-10
interim reconciliation had nothing substantive to add this single
continuous session; the plan file's own status header, now fixed to
`done (2026-09-13)`; CG-002's context-gap-vs-candidate-learning
classification is a defensible judgment call the entry itself already
flags, worth GATE DB inheriting explicitly). Retro:
`planning/retros/phase-45-ledgerkit-baseline.md`.
`planning/phase-46-ledgerkit-tasks.md` written, explicitly hedged: the
candidate task (a compat-register migration follow-up named by
Ledgerkit's own Stage A closeout) requires live reconfirmation at Phase
46's own start, since Ledgerkit's roadmap already moved once mid-Phase-45.
**No gate blocks Phase 46.**

**Phase 46 is `done` (2026-09-13) — the full per-task procedure ran for
the first time against genuinely live Ledgerkit work, and produced
CodeCompass's second FAIL verdict.** Reconfirmed live at phase start, as
hedged: Ledgerkit's own Stage B closed to `[DONE]` and Stage C opened
within a day of Phase 45's pinned commit, so the task actually run was
hledger 1.52 query-term semantics, not the plan's named
compat-register-migration candidate. Because a real, concurrently-running
Ledgerkit development session was producing the task's exact deliverable,
the attempt was conducted as a read-only evaluation exercise — no file
was written into the Ledgerkit clone.
`planning/reference-projects/ledgerkit/01-query-semantics.md`:
**second FAIL verdict**, LOW (negative) advantage, and the first on
genuinely in-progress work rather than a spot-check question — CodeCompass
returned a complete blank (0 vendors, "not found" for both `dev-docs/`
files), while Ledgerkit's own
`dev-docs/planning/core-redefinition/07-query-regex.md` §7.1 already had
the complete answer, found by one `grep` + file read. **`CG-002`**
re-confirmed independently by both `reference-project-tester` and
`context-evaluator`, extended to nested `dev-docs/**` paths. **`CG-003`**
filed (new, `candidate`): the external hledger.org manual itself has zero
CodeCompass representation — no glob fix could ever cover it (a Stage
E/GATE DD question, not Stage C/GATE DB). **`L-017`** filed (retained): a
live `WebFetch` fallback against hledger.org needed two attempts and
still couldn't reliably extract the relevant section. A process incident
— two agents dispatched to `Write` (not `Edit`) the same shared report
file concurrently, silently clobbering one agent's output — was filed as
**`L-018`** and **promoted the same phase**: `planning/agent-led-workflow.md`
step 5 now explicitly forbids two agents `Write`-ing one shared path
concurrently. **No `src/codecompass/` change.** Verified: `pytest` 554
passed / 2 skipped, `ruff check .` clean, `check_user_docs.py --strict`
clean. Closeout: `docs-reconstructor` drift audit
(`planning/retros/_drift-audit-phase-46.md`) → **NO DRIFT**;
`knowledge-curator` triage → CG-003 (`candidate`), L-017 (`retained`),
L-018 (`promoted`); `release-phase-auditor`
(`planning/retros/_audit-phase-46.md`) → **PASS WITH NON-BLOCKING
OBSERVATIONS** (no blocking gap; two cosmetic observations — stale
curation prose next to L-018's already-`promoted` status field, and a
missing blank line in `context-use-log.md` — both fixed before this
closeout). Retro: `planning/retros/phase-46-ledgerkit-tasks.md`.
`planning/phase-47-consolidate-findings.md` written — Stage B's decision
phase, **GATE DB** (gate G6), with a full evidence inventory from Phases
44–46.

**Phase 47 is `done` (2026-09-13) — Stage B's fourth and final phase, and
GATE DB is resolved. Stage B (Phases 44–47) is now fully complete.**
Pure synthesis, no new evaluation: `knowledge-curator` bulk-reviewed every
Phase 44–46 candidate learning and `context-gaps` entry and wrote
`planning/reference-projects/ledgerkit/findings.md` — 5 evaluated
question/task instances, **2 formal FAIL verdicts**, **100% LOW context
advantage** (two explicitly negative), and the `_DEFAULT_GLOBS` blind spot
confirmed at **3 independent occurrences** (Phase 37 own-dev, Phase 45 +
46 externally on Ledgerkit). **GATE DB ratified by the user** ("Ratify as
recommended"): fund one narrow Stage C phase closing **`CG-002`**
(`dev-docs/**/*.md` glob coverage) + **`L-016`** (`query relations`
not-found disambiguation) —
`planning/phase-49-spec-doc-coverage-and-error-disambiguation.md`,
matching the roadmap's own pre-written Phase 49 sketch, not Phase 48's;
**Phase 48** (task-oriented context retrieval) and **Phase 50**
(shared-agent context/entry points) explicitly **not funded** — no
corroborating evidence in the Phase 44–46 dataset; a more general
`vendor.toml`-configurable glob list explicitly rejected as premature;
`CG-003`/`L-017` explicitly routed to Stage E/Phase 53, not this gate.
`CG-002` moved to `promoted-to-roadmap`; `L-016` stays `retained` until
Phase 49's fix actually lands. A genuine, unrelated pre-existing
doc-drift fix landed as a side effect: `architecture/overview.md`'s
`_DEFAULT_GLOBS` enumeration was missing the Phase 37 `ai-docs/**/*.md`
addition (flagged-but-deferred by two prior phases' `docs-maintainer`
reviews), corrected here and verified item-for-item against the real
code. **No `src/codecompass/` change this phase** — Phase 49 is
CodeCompass's first `src/` change driven by external reference-project
evidence. Verified: `pytest` 554 passed / 2 skipped, `ruff check .`
clean, `check_user_docs.py --strict` clean. Closeout:
`docs-reconstructor` drift audit
(`planning/retros/_drift-audit-phase-47.md`) → **NO DRIFT**;
`release-phase-auditor` (`planning/retros/_audit-phase-47.md`) → **PASS
WITH NON-BLOCKING OBSERVATIONS** (no blocking gap; four advisory notes,
all either already addressed or explicitly non-blocking — see the
audit's own text). Retro:
`planning/retros/phase-47-consolidate-findings.md`. **No gate blocks
Phase 49.**

**Stage A of the redefined-v1 roadmap is complete: Phases 39–43 are
`done`.** Phase 43 dogfooded the full 14-step agent-led loop on a real
`src/codecompass/` change (`query skills` widen, 43a) and **passed GATE
DA** — the model works, roster stays at 7, no pruning; **4 amendments**
landed (L-002 curator/knowledge-curator "lead runs the confirming check"
handoff; `docs-maintainer` "check if a file is generated before editing"
from L-005; `docs-maintainer` "fix, don't caveat" may mean *delete the
paragraph*; `agent-led-workflow.md` step 11 + `roadmap-context-curator`
brief "re-dispatch the curator after a plan-changing retro, reconcile
*every* planning doc" from **L-006**) + 2 `check_user_docs.py` rules
scheduled as **Phase 43b**. The `release-phase-auditor` ran a 3-round
trail — **FAIL → FAIL → PASS** (first pass: 3 planning-doc bookkeeping
gaps — missing 43b ROADMAP row, `v1-redefinition/roadmap.md` GATE DA
outcome, 43b absent from the CONTEXT forward path; re-audit #1: the
CONTEXT fix left the file self-contradictory on Phase 43's status;
re-audit #2 PASS WITH NON-BLOCKING OBSERVATIONS) — every gap planning-doc
bookkeeping, none a code defect (the evidence behind L-006). Candidate
learning **L-006** filed this phase.

**Both Stage A→B bridge phases are now `done` (2026-09-11): Phase 43b's
closeout landed** (`knowledge-curator` triage of L-003/L-004/L-005's
invariant half + a follow-up dispatch closing L-006's outstanding
disposition; `release-phase-auditor` **PASS WITH NON-BLOCKING
OBSERVATIONS**). `ROADMAP.md` row `43b`, the `v1-redefinition/roadmap.md`
Phase 43b stanza, and the phase's own plan-file status line all read
`done`. **No gate blocked Phase 44** — Stage B began next (Phase 44 is
now also `done`; see above).

**Phase 43c is `done` (2026-09-11).** The Stage A→B
bridge phase (user request 2026-09-11) instrumented the agent-led
development process to produce context-quality signal from CodeCompass's
own development, with **no `src/` or test change**: new
`planning/context-gaps/` (a capture pathway for relationships an agent
believes the graph should hold but mechanical detection can't produce;
first entry `CG-001`), `planning/context-use-log.md` (a 4-line per-use
CodeCompass-context-vs-default-pathway record, LOW/MODERATE/HIGH —
`agent-led-workflow.md` step 4 now requires an entry), and
`planning/context-health.md` owned by the roster's new **8th agent**
`context-health-planner` (user-approved, Option A). `decisions/0051`
(Accepted): agent-suggested context is captured as reviewable candidates,
**never written to `context-graph.db`** — it becomes authoritative only
via the learning lifecycle into a Stage C detection heuristic (GATE DB)
or a Stage E graph capability (GATE DD), each with its own ADR.
Verification: `pytest` 545 passed / 1 skipped, `ruff` clean,
`check_user_docs.py --strict` clean. Closeout: `docs-reconstructor`
drift audit → **NO DRIFT**; `knowledge-curator` triage → `CG-001`
`candidate` (provenance verified by code-trace) + **L-007** filed
`retained` (from a retro lesson: "a mechanism existing" ≠ "the mechanism
produced output this phase" — `context-health.md`'s first assessment was
lead-written, not run by the new agent); `release-phase-auditor` →
**PASS WITH NON-BLOCKING OBSERVATIONS**. One tracked follow-up: the
`context-health-planner`'s first genuine solo run is before Phase 45
(pinned into the Phase 45 stanza of `v1-redefinition/roadmap.md`).

**Phase 43b is `done` (2026-09-11).** The other Stage A→B bridge phase
(GATE-DA-scheduled, not user-requested — independent of 43c, either
order): both `check_user_docs.py` rules GATE DA decided on are live —
`check_no_deleted_names_as_live` (promotes L-003+L-004, a
prose-unit-granularity check against a small hand-maintained
retired-names list, tuned to zero false positives against this repo's
own historically-narrated `architecture/overview.md`) and
`check_generated_artifacts_match_source` (promotes L-005's invariant
half — `.claude/skills/codecompass/SKILL.md` /
`.claude/commands/discovery.md` byte-match their generators). 46 tests in
that module (+9). The plan's open judgment call resolved **in favour of
fixing now**: `architecture/overview.md` §C's 4 self-contradictory
passages (items 33-36) were corrected directly, verified against `src/`,
closing that part of L-004's Phase-61 obligation early
(`architecture-split-candidates.md` §C, 36→32 outstanding). **Undocumented
decision surfaced this phase, worth recording:** verifying GATE DA's own
proposed retired-names list against `src/` before implementing it found
the list itself was partly wrong — `_RAW_TEXT_CHAR_CAP` and
`_DOCS_FILE_CAP` were never deleted (they still exist unchanged in
`enrichment.py`, only re-attributed from the deleted
`grounded_description.py`); only `_ESTIMATED_COST_PER_CALL_USD` was
actually renamed (to `_ESTIMATED_COST_PER_BATCH_USD`). The check's
retired-names list uses the corrected facts, not GATE DA's original
phrasing. Independently re-verified this session: `pytest` 554 passed / 1
skipped (was 545, +9), `ruff check .` clean,
`check_user_docs.py --strict` clean (0 findings, including 0 from the 2
new checks); `docs-reconstructor` drift audit → **NO DRIFT**
(`planning/retros/_drift-audit-phase-43b.md`).
**Closeout complete:** `knowledge-curator` triaged L-003 (retained,
flagged for the Phase 47 bulk review), L-004 and L-005's invariant half
(both promoted, `promoted.md` lines added), and L-008 (new, retained); a
follow-up dispatch also closed **L-006**'s outstanding disposition
(promoted — the amendment landed in commit `f6cc86d`, Phase 43's own
follow-up commit, not this phase's). `release-phase-auditor` →
**PASS WITH NON-BLOCKING OBSERVATIONS**
(`planning/retros/_audit-phase-43b.md`) — no blocking gap; 4 non-blocking
observations (stale "triage has not yet run" wording across `CONTEXT.md`
/ the plan / `v1-redefinition/roadmap.md`; the retro's "Where we're
going" pre-empting the verdict; L-006 missed by the first triage pass;
commit-hash placeholders), all addressed in this closeout commit. Retro:
`planning/retros/phase-43b-standing-doc-drift-checks.md`. `ROADMAP.md`
row 43b and the `v1-redefinition/roadmap.md` Phase 43b stanza both now
read `done`.

**Stage B is fully complete: 43b, 43c, 43d, 43e, 44, 45, 46, and 47 are
all `done`. GATE DB is resolved (see Phase 47 above).**

**Stage C is now fully complete: 49 and 51 are `done` (48 and 50 not
funded). GATE DC is resolved.**
([`phase-49-spec-doc-coverage-and-error-disambiguation.md`](phase-49-spec-doc-coverage-and-error-disambiguation.md),
[`phase-51-rerun-ledgerkit-evaluation.md`](phase-51-rerun-ledgerkit-evaluation.md)).
Phase 49 was the actual `src/codecompass/` fix GATE DB funded: added
`"dev-docs/**/*.md"` to `_DEFAULT_GLOBS` (closes `CG-002`) and
disambiguated `query relations`'s "not found" error via a new
`_relations_not_found_error`, scoped to `query_relations` only (closes
`L-016`), plus 3 new tests and a live smoke-test re-check against the
real Ledgerkit clone. Phase 51 (2026-09-14) then re-ran Phase 45's
baseline Q2 and Phase 46's genuine task against Ledgerkit re-pinned at
`05218e3` to measure whether the fix actually worked: **both original
FAIL verdicts moved to PASS WITH GAPS**, independently re-verified by
`context-evaluator`, and the fix was confirmed to generalise (a
brand-new file, `17-query-semantics-brief.md`, that didn't exist at
Phase 46's pin is also correctly tracked). **Advantage stayed LOW** —
`query relations` only does literal name-mention detection and Ledgerkit
has 0 tracked vendors, a structural ceiling this fix was never scoped to
raise. Phase 49's fix is judged a success on its own narrow terms.
`CG-002` stays `promoted-to-roadmap`; `L-016` stays `promoted`; the
Phase-47-committed `L-012`/`L-015` revisit decision was resolved as part
of Phase 51's closeout (`L-015` stays `retained`, `L-012` moved
`retained` → `discarded`). **No gate blocks a next phase — but there
isn't one queued.** Whether to continue into Stage D (deeper Ledgerkit
dogfooding, Phases 52–55) or treat GATE DC's result as sufficient and
proceed toward Stage F/G (Technical Clipper, then blank-slate doc
reconstruction and release) is a genuine strategic decision for the
user, not a technical call this reconciliation resolves — see "Next
concrete step" below.

**Phase 52 is `done` (2026-09-14) — additive infrastructure, not a
resolution of Stage C's still-open next-step decision.** Scoped by a
direct user request during Phase 51's own retro window (not by resuming
the Stage D-vs-Stage-F/G fork), it implemented
`planning/context-edge-lifecycle-plan.md` in full: the
`planning/context-observations/` lifecycle generalising
`context-use-log.md` (migrated 4 entries verbatim as `OBS-001`–`004`,
reshaped with an explicit edge-correctness/task-usefulness split), and
**agent-driven enrichment as a second, non-authoritative producer**
(`decisions/0054`) alongside the existing batched-API path —
`relation_enrichment.py::apply_results` gained a backward-compatible
`model` parameter, a new `codecompass enrich apply` CLI command
mechanically enforces the trust boundary (only accepts entries matching
a currently-pending `select_candidates()` row), and a new ninth agent,
`context-enrichment-agent`, produces the grounded content. **Demonstrated
live, twice, against a local fixture** (`tests/fixtures/ledgerkit_lifecycle_demo/`,
`DEMO.md`) — deliberately not the live Ledgerkit clone, per explicit
user direction — proving the trust-boundary rejection, the enrichment
cache surviving a byte-identical graph rebuild, and a genuine stale-edge
rejection; one honestly disclosed complication (a fixture-bootstrap
content-hash artifact) was root-caused live and filed as **L-019**
(candidate). `pytest` 567 passed / 2 skipped, `ruff check .` clean,
`check_user_docs.py --strict` clean. Closeout: `docs-reconstructor`
drift audit (`planning/retros/_drift-audit-phase-52.md`) → DRIFT, 2
non-blocking findings, both fixed before commit; `release-phase-auditor`
(`planning/retros/_audit-phase-52.md`) → **PASS WITH NON-BLOCKING
OBSERVATIONS**, including independently live-reproducing the two-cycle
demonstration itself in an isolated copy; the two actionable
observations (a defensive `isinstance` check in `enrich apply` + a
`DEMO.md` wording correction) were fixed before this closeout. Retro:
`planning/retros/phase-52-context-edge-lifecycle.md`. **The Stage
D-vs-Stage-F/G strategic decision (Phase 51's retro) remains open and
unaffected — this phase's scope did not come from resuming that fork,
and its fixture demonstration deliberately produced no new evidence
toward it.** No phase is queued next; see "Next concrete step" below.

- **39** ratified the redefinition: ADRs `decisions/0048`/`0049`
  `Accepted`; `pyproject.toml` `version` → `1.0.0.dev0`; ROADMAP's Stage
  A–F section ratified; Phase 23 Part B superseded; Phases 24/25
  `deferred` (not renumbered).
- **40** made the agent-led model operational: `.claude/agents/` roster
  of 7; `planning/agent-led-workflow.md`; `CLAUDE.md` §8/§1/§5/§6 changes
  approved (gate G4) + applied + mirrored to `CONTRIBUTING.md`. Forced
  fix to `scripts/check_user_docs.py::check_readme_phase_count` — captured
  as candidate learning **L-001**.
- **41** made `planning/learnings/` operational, added the phase-retro
  and per-phase docs-drift-audit closeout mechanisms (`CLAUDE.md` §5
  follow-on amendment + `decisions/0050`), and **ran the agent-led loop
  for real** — `knowledge-curator` (L-001 promoted+logged; L-002/L-003
  retained), `docs-reconstructor` per-phase drift audit (NO DRIFT),
  `roadmap-context-curator`, `release-phase-auditor` (**PASS WITH
  NON-BLOCKING OBSERVATIONS**, 4 advisory items addressed/filed). Retro:
  `planning/retros/phase-41-learning-lifecycle-and-retros.md`.
- **42** built the everyday documentation-lifecycle machinery: 3 new
  deterministic checks in `scripts/check_user_docs.py` (internal-link
  resolution, fenced `codecompass` example validity, ADR `Status:` /
  cross-reference integrity) + 11 tests (37 in that module; full suite
  543 passed / 1 skipped), the finalised `docs-maintainer` brief,
  `planning/milestone-closeout-checklist.md` (the Phase 66 gate), and
  `planning/v1-redefinition/architecture-split-candidates.md` (Phase 61
  input, 36 catalogued passages incl. 4 self-contradictions). Agent-led
  closeout: `docs-maintainer` first real use (no product doc affected;
  produced the catalogue), drift audit **NO DRIFT**, `knowledge-curator`
  triaged **L-004** (retained, clustered with L-003 as the "standing-rot
  blind-spot" pair for GATE DA), `release-phase-auditor` **PASS WITH
  NON-BLOCKING OBSERVATIONS** (3 advisory items folded into the closeout
  checklist / auditor brief). Retro:
  `planning/retros/phase-42-documentation-lifecycle.md`.
- **43** (`done`) dogfooded the full 14-step agent-led loop on one
  real `src/codecompass/` change — **43a**
  ([`phase-43a-query-skills-widen-kinds.md`](phase-43a-query-skills-widen-kinds.md)),
  the **first `src/` change since the redefinition began**:
  `graph.skills_index` / `codecompass query skills` widened from
  `WHERE kind = 'skill'` to `kind IN ('skill', 'cursor_mdc',
  'slash_command')` (`_SKILLS_INDEX_KINDS`) + a `kind` per row / a "Kind"
  table column / `--json kind`, with `skill.py`'s generated tool-Skill
  description and `.claude/skills/codecompass/SKILL.md` regenerated to
  match — so Cursor `.mdc` rules and `/discovery` now surface in `query
  skills` (verified live: 9 rows vs 5), closing the documented Phase 17
  gap. +2 tests (545 suite); `docs-maintainer` reconciled
  `docs/cli-reference.md` + `architecture/overview.md`. Dogfood outcome:
  `docs-maintainer`'s first *editing* use surfaced **L-005** (it edited
  the generated `SKILL.md` directly — the fix belongs in `skill.py`; its
  brief gained a "check if generated before editing" rule this phase);
  `docs-reconstructor` per-phase drift audit
  (`planning/retros/_drift-audit-phase-43.md`) → **NO DRIFT**, the first
  phase where it verified real current-truth doc *edits*, not just "nothing
  changed". No `CLAUDE.md` change, no ADR, no release/tag (G2-b).
  **GATE DA passed** (`planning/retros/phase-43-dogfood-agent-led-workflow.md`):
  model works, roster stays at 7, no pruning; **4 amendments** landed —
  (1) `agent-led-workflow.md` step 12 + `knowledge-curator` brief: curator
  "lead runs the confirming check" handoff (from L-002); (2)
  `docs-maintainer` brief "check if a file is generated before editing"
  (from L-005); (3) `docs-maintainer` brief "fix, don't caveat" may mean
  *delete the paragraph* (retro lesson 3); (4) `agent-led-workflow.md`
  step 11 + `roadmap-context-curator` brief: re-dispatch the curator after
  a plan-changing retro and reconcile *every* planning doc incl.
  `v1-redefinition/roadmap.md` (from **L-006**, filed this phase as a
  `candidate` — its disposition confirmed at Phase 43b triage). 2
  `check_user_docs.py` rules scheduled as **Phase 43b**.
  `release-phase-auditor` ran a 3-round trail — **FAIL → FAIL → PASS**
  (first pass: 3 planning-doc bookkeeping gaps — 43b ROADMAP row,
  `v1-redefinition/roadmap.md` GATE DA outcome, 43b absent from the
  CONTEXT forward path; re-audit #1: the CONTEXT fix left the file
  self-contradictory on Phase 43's status; re-audit #2: PASS WITH
  NON-BLOCKING OBSERVATIONS) — every gap planning-doc bookkeeping, none a
  code defect.

**Phase 43 (43a) is the first and only `src/codecompass/` change in Stage
A** — Phases 39–42 changed no `src/`. No `CLAUDE.md` change in Phase 42 or
43 (§5 was already amended in Phases 40–41). No release or tag anywhere in
Stage A (gate G2-b).

**43c is `done`** ([`phase-43c-agent-context-pathways.md`](phase-43c-agent-context-pathways.md),
user request 2026-09-11) — the Stage A→B bridge that instrumented the
agent-led dev process to capture context-quality signal from
CodeCompass's own development (`planning/context-gaps/` + `CG-001`,
`planning/context-use-log.md` + a step-4 amendment, `context-health.md` +
the 8th agent `context-health-planner`, `decisions/0051`). Capture +
evidence only, no `src/` change.

*(Historical snapshot, as of Phase 44's completion — superseded by the
Stage B/Stage C summary above: Phases 45, 46, 47, and 49 have since all
landed and are `done` too.)*

The `planning/v1-redefinition/` package + `planning/learnings/` (now live)
+ `planning/retros/` + `planning/agent-led-workflow.md` (14 steps) + Stage
A phase plans (`phase-39`…`phase-43e`) + Stage B's opening phase plans
(`phase-44`, `phase-45`) are the governing plan for this milestone group.

Everything below this line describes the **foundation** (phases 0-38) and
remains accurate.

Phases 30-38 (doc-graph precision, user-facing docs, docs-sync tooling,
redundancy cleanup) are all `done`.
`codecompass` now: auto-clones every tracked vendor; detects real
project-source usage (vendor- and symbol-level); maps docs/skills/
dependencies/spec-docs/vendor-docs into a SQLite graph with both
mechanical and AI-enriched relationship edges, now with real `(file,
line)` code-usage traversal, typed relation labels, and heading-scoped
doc chunking sharpening both; auto-triggers disclosed, confirmable
batched AI enrichment for usage-proven vendors *and* relationships;
exposes all of it via `codecompass query`, `/discovery`, and generated
Skills; can `undo` itself cleanly; frames chat as secondary. `promote` and
`Depth` are fully retired. Packaging is release-ready (real wheel
re-verified installable in a clean venv after Phase 38's dependency-pin
change; `version` is `1.0.0.dev0` as of Phase 39) but **nothing is
published to PyPI and no tag has been cut — and won't be until the
redefined v1, Phase 67 (gate G2-b).**
`README.md` now documents real setup requirements (Python version, `git`,
`ANTHROPIC_API_KEY`) and a plain free-vs-paid AI enrichment explainer; a new
`ai-docs/` folder gives an agent a capability/boundary overview distinct
from root `CLAUDE.md`'s process rules; a new maintainer-only
`scripts/check_user_docs.py` + `.claude/skills/docs-sync/` mechanically
flags future drift between this repo's own docs and its own code (not
shipped, not a `codecompass` feature). `pyproject.toml`'s 4 runtime
dependencies now carry lower-bound version pins (`decisions/0047`), and
`cli.py`'s query-command boilerplate/`vendor.toml`'s dead `depth` lines
were cleaned up (Phase 38).

## What was just completed

**Phase 60's plan is amended, still not started (2026-09-19) —
external-process adapter architecture.** Direct user instruction, before
implementation began: the Haskell adapter is no longer an in-process
Python class — it is now the **reference implementation of a genuinely
external adapter**, a separate OS process communicating over a small,
versioned JSON-Lines protocol on stdin/stdout, so CodeCompass core never
imports ecosystem-specific implementation code. Motivated by a real
future case: a potentially proprietary COBOL/mainframe adapter suite
that could never ship as importable GPL Python code inside
`src/codecompass/`. New ADR: `decisions/0057-external-process-adapter-protocol.md`
— protocol shape (`initialize`/`analyze_project`/`shutdown`, a
`capabilities` list, `result`/`error` response shapes), where the
boundary actually falls (simple manifest-key reads stay in
CodeCompass-core via real `PyYAML`; only `stack`'s own dependency-tree
resolution and real `.hs`-source API-surface extraction move into the
external process), and an explicit, disclosed non-claim that
process/protocol separation is architectural, not a legal conclusion
about GPL compatibility for a future proprietary adapter — real
specialist legal review named as necessary before relying on it. **A
real smoke test this session confirmed the mechanism is genuinely
buildable, not just theoretically sound**: a single-file `stack script`
(no separate `package.yaml`/`stack.yaml` needed for the adapter itself)
using `aeson` compiled and ran successfully against the pinned snapshot
resolver this environment already uses (`nightly-2026-09-01`) — ~5 min
cold (compiling `aeson` from source), ~3s warm. Per direct instruction,
two prior review-gate judgment calls are now settled, not open: hand-
rolled `package.yaml` parsing is replaced by real `PyYAML`
(`yaml.safe_load()`); the Haskell API-surface/export-list extraction
question is **mandatorily** routed through Phase 54c's evidence-backed
workflow (its own first real test under genuine uncertainty), not left
as a recommendation. Monorepo package-root resolution (`hledger-lib/`
within the `hledger` repo, resolved on the CodeCompass side before the
adapter is ever invoked, never the whole repo) is now an explicit,
tested requirement. Explicitly avoids gRPC, network services, a plugin
marketplace, remote execution, or a versioned SDK — a local subprocess
exchanging JSON Lines is the whole of this phase's own protocol. The
original in-process plan is preserved at the plan file's own §A, not
deleted, available as a fallback if the external-process architecture's
real overhead proves not worth it. Full amended plan:
`planning/phase-60-minimal-haskell-adapter.md`. Still planning only —
no `src/` change.

**Phase 60 is a plan, not started (2026-09-19) — minimal Haskell
adapter.** Direct user request ("Plan next phase"): the next unstarted
Stage F phase, gated on nothing (Stage F is a separate axis from Stage
E/GATE DD, per `decisions/0056`). Full plan:
`planning/phase-60-minimal-haskell-adapter.md`. Real environment
re-verification (not assumed from the npm/Python/Cargo adapters' own
JSON-tooling precedent) found `stack ls dependencies` has **no JSON
output mode** — `stack dot`'s real GraphViz DOT graph output (checked
live against the real hledger project this session: `"Cabal" ->
"base";`-shaped edges, confirmed working) is the actual
`dependency_tree()` source instead, cross-referenced against `stack ls
dependencies`'s flat name→version map for each node's version. Every
real touchpoint traced directly (not assumed): `core.py::Ecosystem`
gains `HASKELL`; `graph.py`'s `vendors.ecosystem` CHECK widens
(`_SCHEMA_VERSION` 7→8, mirroring Phase 54c's own just-completed
`origin`-enum-widening precedent exactly); `discovery.py` gains a
`package.yaml` (hpack) manifest entry; `symbols.py` gains
`extract_haskell_symbols`; a new `adapters/haskell.py` implements all
five `EcosystemAdapter` methods. `usage.py`'s Haskell import detection
explicitly deferred to Phase 61 (not this phase's scope). Two judgment
calls flagged for review, not decided unilaterally: (1) hand-roll
`package.yaml` parsing vs. add a `PyYAML` dependency — recommendation:
hand-roll, scoped narrowly, per this project's "smallest justified fix"
discipline; (2) whether the one genuinely open design question
(Haskell module export-list/API-surface extraction — a real ambiguity,
unlike Rust's simpler `pub`-keyword precedent) should be routed through
Phase 54c's evidence-backed workflow, scoped only to that sub-question
— recommendation: yes, since Phase 54c's own retro explicitly named
exactly this kind of genuinely-uncertain, real pre-implementation
question as the methodology's next needed test. Testing strategy:
fixture-based (primary, `decisions/0014`) plus `stack`-availability-gated
live smoke tests — this environment has `stack` 3.11.1 confirmed
working, making this the second adapter (after npm/Python) to get real
toolchain coverage from day one, unlike Cargo's still-open gap. No `src/`
change yet — this is planning only.

**Phase 54c is `done` (2026-09-18) — evidence-backed, knowledge-based,
documentation-first development workflow, implemented and run for
real.** Full plan (amended once before implementation, per direct user
feedback — see git history at `9932b7d`/`ae165e5`):
`planning/phase-54c-evidence-knowledge-workflow.md`. **Primary proving
case (`CG-005`, tests workflow mechanics)**: the full loop ran —
`context-researcher` (11 Observation/9 Evidence/4 Claim/4 Derivation
records, dispatched as `general-purpose` with the role embedded, since
a newly-created agent type isn't immediately dispatchable mid-session —
`L-023`) → `documentation-agent` (`design.md`) → lead-as-reviewer
(disclosed: `DEC-DOCORIGIN-001` + 3 Requirements) →
`documentation-agent` regeneration (not hand-patched) →
`knowledge-curator`'s new packet-assembly mode (`context-packet.md`) →
real implementation: `doc_artifacts.origin` gains `pinned_reference`
(`_SCHEMA_VERSION` 6→7), `spec_docs.py::scan_spec_docs` gains automatic
YAML-frontmatter-based detection → real end-to-end revalidation (an
actual `codecompass sync` against Phase 54b's own scratch Ledgerkit copy
confirms all 19 real ingested files now correctly read
`origin='pinned_reference'`, closing `CG-005`'s real motivating instance
for real, not just a synthetic test). `CG-005` promoted. **Secondary
proving case (retroactive `hledger-depth`, tests knowledge→documentation
fidelity)**: built entirely from Phase 54b's already-verified evidence,
no new dispatch — the resulting `design.md` correctly and completely
matches Ledgerkit's real, shipped Stage C Phase 5 outcome. **A real,
independently-verified traceability test passed**: a fresh agent, given
only one Claim's five-record citation chain, correctly reconstructed a
`KeyError`-crash mechanism without guessing. Two real process gaps found
and promoted: `L-023` (agent-registry activation timing, into
`agent-led-workflow.md`) and `L-024` (a context packet's own "existing
tests" section must check for schema/migration test files, not just
feature-code tests, into `context-researcher.md`'s own brief). **Two of
the plan's ten evaluation questions honestly left unanswered, not
claimed positive**: `contradicting_evidence`/Claim-`supersedes` machinery
was never exercised with real content in either proving case, and
neither case presented a genuine pre-implementation misunderstanding for
review to catch. Retro's own durable-vs-experimental recommendation, per
record kind/agent role/lifecycle mechanism individually:
`planning/retros/phase-54c-evidence-knowledge-workflow.md`. **Whether
this workflow improves development quality generally remains explicitly
undecided** — deferred to Phase 60/61's own genuine-uncertainty test,
exactly as the amended plan anticipated before implementation began. 587
tests pass (6 new); `ruff`/`check_user_docs.py --strict`/new
`scripts/check_knowledge_base.py --strict` all clean. No new ADR.

**Phase 54b is `done` (2026-09-18) — LedgerKit behavioural-understanding
experiment.** Expanded from a one-paragraph placeholder into a concrete
experiment using Ledgerkit's real Stage C Phase 5 `depth:` investigation
(`c6168b2`), per the user's explicit prompt (saved verbatim,
`planning/phase-54b-ledgerkit-behavioural-understanding-prompt.md`).
Extended Phase 54's reference-ingestion pipeline with 11 new manual/
source selections (line ranges reconfirmed live against the pinned
hledger clone). **Two fresh, independently-dispatched agents** (never
the lead, who had already read the answer to write the plan) ran the
identical real task — determine hledger's `depth:`/`--depth` behaviour
across `balance`/`register`/`accounts`/`stats`/`print` — one with no
CodeCompass, one using the new material indexed into a scratch Ledgerkit
copy (pinned at real `HEAD` `c6168b2`). **Both reached the fully
correct, complete answer** (clip/aggregate for three commands, genuine
partial exclusion for `stats`, total inertness for `print`).
`context-evaluator` independently re-derived ground truth from the
pinned source/manual/binary and rated **baseline PASS, treatment PASS
WITH GAPS, context advantage LOW**: the curated set omitted `Stats.hs`
entirely (the one file covering the task's genuine exception), forcing
a disclosed fallback exactly where it mattered most, while the baseline
never hit that gap. Mechanical `query relations` again found **zero**
edges for all 19 indexed files, even with `CG-004`'s fix live. **Both
runs rated `complete`** on the new execution-path-completeness criterion
— neither reproduced Stage C Phase 1's real premature-conclusion
mistake, an honestly-reported negative result for the specific failure
mode this phase was designed to catch. **A real methodological near-miss
was self-caught before either agent ran**: an early draft of the
extracted material's own labels/notes stated the correct answer
directly (e.g. "THE TRAP", "THE EXCEPTION"), which would have silently
invalidated the entire comparison — caught by rereading the pipeline's
own rendering function, fixed, promoted as `L-022` into
`reference-project-protocol.md` §2.4. Filed `CG-007` (symbol-level
cross-references between pinned reference excerpts have no
representable relation kind), `OBS-013`, `OBS-014`. No `src/codecompass/`
change. Full results: `planning/reference-projects/ledgerkit/findings.md`'s
"Phase 54b" section; evaluation:
`planning/reference-projects/ledgerkit/02-depth-behavioural-reconstruction-evaluation.md`;
retro: `planning/retros/phase-54b-ledgerkit-behavioural-understanding.md`.

**Phase 55b is `done` (2026-09-17) — populated `doc_artifacts.name` for
`spec_doc` rows, closing `CG-004`.** User approved
`phase-55-evidence-reconciliation.md` §G's recommendation ("Approved"),
numbered as a bridge phase (43d/43e precedent) rather than disturbing
Stage E's (56-59)/Stage F's (60-63) own pre-written, unrelated sketches.
**A genuine mid-phase failure, caught by independent evaluation and
honestly retained, not smoothed over**: the first implementation
attempt added real, meaningful unit tests, all green — and was still
completely non-functional in the real running tool, because `sync.py`'s
own production call to `build_doc_relations_edges` never included the
new `spec_doc_rows` argument. `context-evaluator`'s round-1 pass caught
this by re-running the real tool against the live Ledgerkit repository
rather than trusting the green suite; that same pass quantified a
second problem a naive fix would have caused (55 hypothetical
false-positive edges, 50 of them "every doc mentions README" purely
because its own H1 is the bare project name `# ledgerkit`). Both fixed:
the `sync.py` wiring landed, and a genericity guard
(`_is_specific_enough`) rejects single bare words with no digit/hyphen.
Round 2: **PASS WITH NON-BLOCKING OBSERVATIONS**, confirmed via a real,
read-only before/after against the live Ledgerkit repository — 3
genuine `mentions_artifact` edges now appear, all independently verified
real, zero reintroduced noise. Honestly disclosed, not claimed fixed:
the original `CC-LK-001` three files still show zero relations to each
other, because they cross-reference by filename, not by title text —
filed as `CG-006`, a small, independently-fundable follow-on of the same
shape as `CG-004` itself, not urgent. `release-phase-auditor` found 4
non-blocking gaps in the planning/retro paper trail itself (a stale
"no stoplist needed" design note, an incomplete Files list, a factual
misstatement about what the originally-approved plan actually scoped,
a missing recorded drift-audit verdict) — all fixed before this
closeout, none affecting the shipped code. `docs-reconstructor` drift
audit (`planning/retros/_drift-audit-phase-55b.md`) → NO DRIFT, 1
non-blocking finding, fixed. A process-lesson candidate (`L-021`)
recommends a `CLAUDE.md` §1 amendment (drafted in
`planning/v1-redefinition/proposed-governance-changes.md` §D) — **filed,
not yet approved**, to be presented separately per §0. `pytest` 581
passed / 2 skipped, `ruff check .` clean, `check_user_docs.py --strict`
clean throughout. `planning/ROADMAP.md` row `55b` and
`v1-redefinition/roadmap.md`'s new Phase 55b stanza both `done` as of
this commit.

**Evidence-reconciliation planning session complete (2026-09-17),
no implementation.** `planning/phase-55-evidence-reconciliation.md`
reconstructs current state from both repositories fresh (CodeCompass
`e40d8d1`, unchanged since Phase 54; Ledgerkit `d362bbb`, **five commits
past the `05218e3` pin every prior CodeCompass-side evaluation used** —
confirmed live via `git fetch`, not assumed). Recovered Ledgerkit's own
first-ever real consumer-side evidence:
`validation/codecompass/findings/CC-LK-001` (Stage C Phase 2,
2026-09-16) — Ledgerkit's own `codecompass` CLI run against its real,
live repository for the first time ever, verdict **PASS WITH GAPS**,
advantage **LOW**, independently corroborating two of Phase 54's own
findings from a genuinely different angle: `CG-004` (doc-to-doc relation
gap — 3 real, obviously-connected dev-docs files, zero relations) and
`CG-003` (executable/behavioural evidence gap — a real compat-register
entry, `LK-COMPAT-QUERY-DEPTH-001`, reclassified `compatible` →
`intentional_divergence` purely via differential testing against the
pinned hledger binary, a category CodeCompass has no representation for
at all). Ledgerkit's own retro honestly discloses a process gap (the
"independent" differential testing was done by the lead, not a separate
agent) — recorded as a process-quality caveat, not used to discard the
evidence. Built a full reconciliation matrix (`§D`), being strict about
independence (the causal *diagnosis* half of `CG-004`'s corroboration is
marked partial, since Ledgerkit's own finding cross-references
`CG-004`'s text rather than independently re-deriving the root cause;
the raw *observation* is fully independent). **One small, doubly-
corroborated, independently-justified fix recommended for
implementation**: populate `doc_artifacts.name` for `spec_doc` rows
(closes `CG-004`, zero schema change, reuses the existing unmodified
`mentions_artifact` matcher) — validated via a real before/after
comparison against Ledgerkit's own live repository, using `CC-LK-001`'s
own three test files. Everything bigger (executable-evidence
representation, pinned-reference productisation, the `origin` enum
extension) stays explicitly **DEFER**red pending broader/cross-domain
evidence, per the plan's own §11 discipline — Technical Clipper (Stage
F) is the natural place that evidence would come from, not invented now.
**A real numbering conflict surfaced and was NOT silently resolved**:
every integer through 63 is already claimed by a pre-written Stage
E (56-59)/Stage F (60-63) sketch, none matching this new phase's content
— `planning/ROADMAP.md` records it with a `—` placeholder row; three
numbering options are presented in the plan's §G for the user to choose
between (renumber Stage E/F; a 43d/43e-style bridge letter, e.g. "Phase
55b"; fold into a future Stage E phase), with a stated but non-binding
preference for the bridge-letter option. Two new context-observations
filed from reading Ledgerkit's own real evidence (`OBS-010`: bare
`codecompass` mutated Ledgerkit's real `CLAUDE.md` unprompted for
zero-value output, reverted; `OBS-011`: generated entry points were pure
boilerplate for a 0-vendor project, confirming — not undermining — the
existing lightweight entry-point architecture). `check_user_docs.py
--strict` clean throughout. **No code implemented, no `CLAUDE.md`
change, no GATE DD resolution** — this is a planning/evidence session
exactly as scoped.

**Phase 54 is `done` (2026-09-16) — heterogeneous reference-material
experiment, implemented and run for real.** The user's own prompt
resolved the open Stage D-vs-Stage-F/G strategic decision (Phase 51's
retro) in Stage D's favour; "Implement the plan" approved both named
judgment calls (the Phase 54 slot renumbering; keeping the ingestion
pipeline outside `src/codecompass/`) without redirection. Built and ran
a real, tested Git-backed resolve/lock/fetch/extract pipeline
(`planning/reference-projects/ledgerkit/reference-experiment/`, 13
passing tests), pinned live against the real, already-confirmed local
hledger clone (`33fa849e...`, tag `1.52.4`), and a genuine two-run
comparison task (Ledgerkit's own Stage C `tag:` query-semantics brief)
against a scratch copy of Ledgerkit, never the real clone.
**Independently evaluated by `context-evaluator`: baseline PASS WITH
GAPS, treatment FAIL, context-advantage LOW** — the FAIL traces to a
real, caught-and-fixed extraction-boundary defect (a hand-drawn line
range silently excluded one of three documented tag-inheritance rules
while its own description claimed all three present), not a mechanism
defect; the pipeline's hashes, idempotency, and its YAML-evidence-
matching relation fallback (demonstrated real against Ledgerkit's own
already-published `LK-COMPAT-QUERY-DATE-001.yaml`) all independently
confirmed sound. Filed: `OBS-007` (detection generalises, zero schema
change), `CG-004` (mechanical `mentions_artifact` structurally cannot
relate two `spec_doc` artifacts — root cause: `spec_doc` rows never get
a `name`), `CG-005` (`origin`'s closed enum has no externally-pinned-
reference value), `OBS-008` (the YAML-evidence fallback, real but
unwired), `OBS-009` (corrected by `knowledge-curator`'s own triage —
caught restating the same false claim that produced the FAIL), `L-020`
(content-hash pinning proves an excerpt hasn't changed, not that its
boundary matches its own claimed content — `knowledge-curator`
recommends promotion). No `src/codecompass/` change — pure
evidence-gathering. `release-phase-auditor` → **PASS** (first round).
Retro: `planning/retros/phase-54-heterogeneous-reference-material-experiment.md`.
**This phase resolves the Stage D-vs-Stage-F/G decision's own open
question by having actually run the test — the result is genuinely
mixed, not a clean mandate either way**, itself valid evidence per the
plan's own "treat negative or inconclusive results as valid evidence"
instruction. `planning/ROADMAP.md` row `54` and
`v1-redefinition/roadmap.md`'s Phase 54 stanza both flipped to `done`
in this commit.

**Contributor licensing terms added (2026-09-15), standalone
user-requested change, not a roadmap phase.** `decisions/0055` records
the decision: `CONTRIBUTING.md`'s `## License` section gains an explicit
contributor grant (verbatim text, per the user's own instruction — the
contributor retains copyright, grants the project owner an irrevocable,
worldwide, royalty-free licence broad enough to relicense the
contribution including under proprietary terms), replacing the prior
"no separate CLA — single-maintainer project" sentence, which had become
the thing actually blocking the goal (preserving future dual/proprietary
licensing optionality once external contributions exist).
`README.md`'s `## License` section gains a short, prominent pointer note
covering all four things the user asked for: GPL-3.0-or-later status,
the new contributor term, why it exists (preserves future
alternative/commercial licensing), and that existing GPL rights are
unaffected. No other current-truth doc needed a change (`ai-docs/README.md`
has no licensing mention at all; no `decisions/` index file exists to
update). `check_user_docs.py --strict` clean. Documentation-only; no
`src/` change, no `CLAUDE.md` change (not a protected-file edit — this
touched `CONTRIBUTING.md`/`README.md`/`decisions/`, not `CLAUDE.md`
itself).

**README.md reconciled with current state (2026-09-15), standalone
user-requested fix, not a roadmap phase.** `docs-maintainer` brought
`README.md` up to date with two real, previously-undocumented gaps: (1)
the "Status" command list never mentioned `codecompass enrich apply`
(Phase 52); (2) the "Core idea" spec-doc-relationship bullet and the
`ANTHROPIC_API_KEY` setup note both described relationship enrichment as
having only the batched-Anthropic-API path, with no mention of Phase
52's second, non-authoritative agent-driven producer
(`decisions/0054`) — a real functionality gap since Phase 52's own
docs-maintainer pass touched `docs/cli-reference.md`/`architecture/
overview.md`/`ai-docs/README.md` but never `README.md` itself. Fixed,
phrasing aligned with `ai-docs/README.md`'s existing equivalent bullet.
`check_user_docs.py --strict` clean; no other current-truth doc,
`src/`, or `CLAUDE.md` change.

**Phase 53 is `done` (2026-09-14) — legacy feature rationalisation,
review-gate passed, implemented.** Retargets this roadmap slot
(originally Stage D's "heterogeneous doc/reference/manual dependencies"
sketch) to a full legacy-feature-rationalisation review, per direct user
request — same findings/decision-driven-scope precedent as Phases 49 and
52. `planning/phase-53-legacy-feature-rationalisation-plan.md` classifies
every runtime feature (CORE / AGENT / HOST-OUTPUT ADAPTER), maps three
real overlaps, and reached one unambiguous action plus five
product-direction recommendations presented to the user via
`AskUserQuestion`. **All three recommended options were approved**: keep
direct-API vendor/symbol/relation enrichment unchanged (real
end-user-project value Phase 52's fixture demo doesn't touch); keep
`chat.py` unchanged (`decisions/0034`'s reasoning found no new evidence
to unseat); defer the two doc-only findings (Skill/`/discovery`/
CLI-docs command-list duplication; `adapters/`-package-vs-"adapter"-tier
naming collision) to a documentation note rather than new tooling. The
prompt's "initial-chat"/project-entry-point candidate was confirmed to
correspond to no shipped code at all (Post-MVP Phase 20/24,
`decisions/0048`, never built) — no action needed. **Implemented**:
`discovery.py::rewrite_vendor_toml` removed (dead since `promote`'s
Phase 15 retirement, zero callers, zero doc references) + its test;
`architecture/overview.md` gained a new "Module tiers: CORE, AGENT,
HOST-OUTPUT ADAPTERS" section + the adapter-terminology disambiguation +
the command-list-duplication caveat. **Produces no evidence toward the
still-open Stage D-vs-Stage-F/G decision** — orthogonal to it, exactly as
Phase 52 was. Verified: `pytest` 567 passed / 2 skipped (569 collected,
-1 from the removed test), `ruff check .` clean, `check_user_docs.py
--strict` clean. Closeout: `docs-reconstructor` drift audit
(`planning/retros/_drift-audit-phase-53.md`) → **NO DRIFT**;
`knowledge-curator` confirmed no new candidate learnings/gaps/
observations from this phase, and fixed stale "Phase 53" pointers left
over from before this slot's retarget (`context-gaps/inbox.md` `CG-003`,
`learnings/inbox.md` `L-017`, alongside two the lead fixed earlier in
this file and `planning/reference-projects/ledgerkit/findings.md`);
`release-phase-auditor` → a multi-round trail; **see
`planning/retros/_audit-phase-53.md` for the exact round-by-round record
and final verdict** (that file is the authoritative source — this
sentence deliberately makes no claim about round count, verdicts, or
pattern, since every prior attempt to characterize the trail inline here
was itself immediately falsified by the next round). Retro:
`planning/retros/phase-53-legacy-feature-rationalisation.md` — answers
all 9 of the governing prompt's specific retrospective questions.
`planning/ROADMAP.md` row `53` and `v1-redefinition/roadmap.md`'s Phase
53 stanza (+ its retarget amendment note) are both `done` as of this
closeout (landed across more than one commit, not all in one — see the
audit report for which fix landed when).

**Phase 52, `done`** (2026-09-14) — context edge lifecycle: the
`planning/context-observations/` queue (generalising `context-use-log.md`,
migrated verbatim) + agent-driven enrichment as a second producer
(`decisions/0054`: `apply_results`'s new `model` param, `codecompass
enrich apply`, the new ninth agent `context-enrichment-agent`) +
a real, live, two-cycle demonstration against a local fixture
(`tests/fixtures/ledgerkit_lifecycle_demo/`) — not the live Ledgerkit
clone, per explicit user direction. Proved the `enrich apply` trust
boundary, the enrichment cache surviving a byte-identical graph rebuild,
and a genuine stale-edge rejection; one complication root-caused live and
filed as `L-019`. `docs-reconstructor` → DRIFT (2 non-blocking, both
fixed); `release-phase-auditor` → **PASS WITH NON-BLOCKING OBSERVATIONS**
(independently live-reproduced the demonstration itself). `pytest` 567
passed / 2 skipped, `ruff check .` clean, `check_user_docs.py --strict`
clean. Retro: `planning/retros/phase-52-context-edge-lifecycle.md`.
**This phase's scope came from a direct user request, not from resuming
Stage D — the Stage D-vs-Stage-F/G decision (Phase 51's retro) remains
open, unaffected.** ROADMAP row `52`, the `v1-redefinition/roadmap.md`
Phase 52 stanza (+ a new Stage D amendment note), and the plan file's own
status line all flipped to `done` in this commit.

**Phase 51, `done`** (2026-09-14) — Stage C's closing phase, **GATE DC**.
Re-ran Phase 45's baseline Q2 and Phase 46's genuine task — same
questions, same instrument — against Ledgerkit re-pinned at `05218e3`
(Ledgerkit had, in the interim, finished the exact Stage C task Phase 46
evaluated, producing a brand-new file that strengthened rather than
complicated the re-run). **Both original FAILs moved to PASS WITH
GAPS**, and "would this have misled the agent" moved from yes to no for
both — independently re-verified by `context-evaluator` via direct
inspection and its own `codecompass`/`sqlite3` commands, not assumed
from the fix landing. **Confirmed the fix generalises**: the new
`17-query-semantics-brief.md` (didn't exist at Phase 46's pin) is also
correctly tracked now — this wasn't a two-file patch, it's a real
mechanism change. **Honestly identified what didn't improve, and why it
structurally can't with this fix**: `query relations` only does literal
vendor/Skill name-mention detection; with 0 tracked vendors, advantage
stayed LOW across both re-runs — the ceiling on this class of question
wasn't raised, and the fix was never scoped to raise it. Phase 49's fix
is judged a success **on its own, narrow terms** — the earlier "smallest
justified fix" judgment (rejecting a more general configurable-glob
mechanism) is validated by this result, not called into question. No
`src/codecompass/` change this phase (measurement only). **Closeout
addendum**, caught by `release-phase-auditor`'s audit: Phase 47's
`findings.md` §6 had committed `L-012`/`L-015` to a promote/discard/
retain decision "at Phase 51's re-run," which this phase's actual scope
(re-running two specific hledger-content questions) never touched.
Resolved rather than left dangling: `L-015` stays `retained` (genuinely
never in scope across five intervening phases — a "no opportunity
existed" case, not a "no evidence found" case; revisit trigger updated
to the next phase that actually exercises dependency discovery); `L-012`
moved `retained` → `discarded` (now 7 phases old, three unclaimed
corroboration opportunities, self-test-only by its own design — the
lifecycle's "~3 phases, no new evidence" norm applied for real).
`planning/reference-projects/ledgerkit/findings.md`'s own triage table
updated to match. Verified: `pytest` 557 passed / 2 skipped, `ruff
check .` clean, `check_user_docs.py --strict` clean. Closeout:
`docs-reconstructor` drift audit
(`planning/retros/_drift-audit-phase-51.md`) → **NO DRIFT**;
`release-phase-auditor` (`planning/retros/_audit-phase-51.md`) → **PASS
WITH NON-BLOCKING OBSERVATIONS** (the one genuine gap it flagged — the
dangling `L-012`/`L-015` commitment — is the addendum resolved above; the
rest were the pending `roadmap-context-curator` reconciliation this
closeout performs). Retro:
`planning/retros/phase-51-rerun-ledgerkit-evaluation.md`. **This
completes Stage C in full** (Phase 48/50 not funded, 49 done, 51 done).
**The retro explicitly frames the next step as a genuine strategic
decision for the user** (continue into Stage D's deeper dogfooding, vs.
treat GATE DC's result as sufficient and proceed toward Stage F/G) — not
a technical call this reconciliation resolves or defaults on.

**Phase 49, `done`** (2026-09-13) — Stage C's first phase, spending
GATE DB's funded fix. `spec_docs.py::_DEFAULT_GLOBS` gained
`"dev-docs/**/*.md"` (closes `CG-002`, the Phase 37 `ai-docs/`
precedent applied a second time from external evidence);
`cli.py::query_relations`'s not-found branch gained
`_relations_not_found_error`, scoped to `query_relations` only — a real
on-disk file not detected as a spec/vendor doc now gets an explicit
message pointing at spec-doc glob coverage instead of a bare "not
found" indistinguishable from a genuine typo (closes `L-016`). **This is
CodeCompass's first `src/codecompass/` change driven by external
reference-project evidence** — the redefined v1's central hypothesis
(`decisions/0048`) made concrete for the first time since Phase 43a's
own-repo dogfood. 3 new tests. Live-verified against the real Ledgerkit
clone, independently reproduced from scratch by both the lead and the
`release-phase-auditor`: `dev-docs/` files (including a nested path) now
resolve to an honest empty relations table instead of "not found"; a
genuinely nonexistent name keeps the plain message; a still-uncovered
real file (`knowledge/DOMAIN_RULES.md`) correctly triggers the new
disambiguated message, confirming the fix generalises beyond the one
directory it was evidenced against. One self-correction: the drift audit
caught a mistaken ADR citation (`decisions/0051`, unrelated) in
`_relations_not_found_error`'s docstring, fixed before commit.
`docs-maintainer` reconciled `architecture/overview.md` and
`docs/cli-reference.md`. Verified: `pytest` 557 passed / 2 skipped (+3),
`ruff check .` clean, `check_user_docs.py --strict` clean. Closeout:
`docs-reconstructor` drift audit
(`planning/retros/_drift-audit-phase-49.md`) → **NO DRIFT**;
`release-phase-auditor` (`planning/retros/_audit-phase-49.md`) → **PASS
WITH NON-BLOCKING OBSERVATIONS** (the only observations were the pending
`roadmap-context-curator` reconciliation this closeout performs). Retro:
`planning/retros/phase-49-spec-doc-coverage-and-error-disambiguation.md`.
`knowledge-curator` finalized: `CG-002` stays `promoted-to-roadmap` with
a closing note confirming the fix landed; `L-016` flipped `retained` →
`promoted`. **Stage C now has one completed phase; Phase 48/50 remain
not funded.**

**Phase 47, `done`** (2026-09-13) — Stage B's fourth and final phase,
**GATE DB**. Pure synthesis of Phases 44–46's evidence, no new
evaluation: `knowledge-curator` bulk-reviewed every candidate learning and
`context-gaps` entry from those phases and produced
`planning/reference-projects/ledgerkit/findings.md` — 5 evaluated
instances, 2 formal FAIL verdicts (both listed in full per the
aggregation rule), 100% LOW advantage (two negative), and the
`_DEFAULT_GLOBS` blind spot confirmed at 3 independent occurrences (Phase
37 own-dev, Phase 45 + 46 externally on Ledgerkit). **GATE DB ratified by
the user** ("Ratify as recommended"): fund one narrow Stage C phase
closing `CG-002` + `L-016`
(`planning/phase-49-spec-doc-coverage-and-error-disambiguation.md`,
matching the roadmap's own pre-written Phase 49 sketch); Phase 48
(task-oriented context retrieval) and Phase 50 (shared-agent context) not
funded — no corroborating evidence; `CG-003`/`L-017` routed to Stage
E/Phase 53. `CG-002` → `promoted-to-roadmap`; `L-016` stays `retained`
until Phase 49's fix lands. An unrelated pre-existing doc-drift fix
landed as a side effect: `architecture/overview.md`'s `_DEFAULT_GLOBS`
enumeration was missing the Phase 37 `ai-docs/**/*.md` addition,
corrected and verified item-for-item against the real code. **No
`src/codecompass/` change this phase.** Verified: `pytest` 554 passed / 2
skipped, `ruff check .` clean, `check_user_docs.py --strict` clean.
Closeout: `docs-reconstructor` drift audit
(`planning/retros/_drift-audit-phase-47.md`) → **NO DRIFT**;
`release-phase-auditor` (`planning/retros/_audit-phase-47.md`) → **PASS
WITH NON-BLOCKING OBSERVATIONS** (no blocking gap). Retro:
`planning/retros/phase-47-consolidate-findings.md`.
`planning/phase-49-spec-doc-coverage-and-error-disambiguation.md` written —
Stage C's funded phase, CodeCompass's first `src/codecompass/` change
driven by external reference-project evidence. **Stage B (Phases
44–47) is now fully complete.**

**Phase 46, `done`** (2026-09-13) — Stage B's third phase, and the first
run of the full per-task procedure (`reference-project-protocol.md`
§2.4) against a genuine, live Ledgerkit task. Reconfirmed live at phase
start, exactly as the plan hedged: Ledgerkit's own Stage B closed to
`[DONE]` and Stage C opened (Phase 1 `[IN PROGRESS]`) within a day of
Phase 45's pinned commit, so the task actually run was hledger 1.52
query-term semantics, not the plan's named compat-register-migration
candidate. A real, concurrently-running Ledgerkit development session was
producing the task's exact deliverable, so the attempt was conducted as a
read-only evaluation exercise — no file was written into the Ledgerkit
clone. `planning/reference-projects/ledgerkit/01-query-semantics.md`:
**CodeCompass's second FAIL verdict**, LOW (negative) advantage, and the
first on genuinely in-progress work rather than a spot-check question —
CodeCompass returned a complete blank (0 vendors, "not found" for both
`dev-docs/` files); Ledgerkit's own
`dev-docs/planning/core-redefinition/07-query-regex.md` §7.1 already had
the complete answer, found by one `grep` + file read. **`CG-002`**
re-confirmed independently by both `reference-project-tester` and
`context-evaluator`, extended to nested `dev-docs/**` paths. **`CG-003`**
filed (new, `candidate`): the external hledger.org manual has zero
CodeCompass representation, no glob fix could ever cover it — a Stage
E/GATE DD question, not Stage C/GATE DB. **`L-017`** filed (retained): a
live `WebFetch` fallback against hledger.org needed two attempts and
still couldn't reliably extract the relevant section. A process
incident — two agents dispatched to `Write` (not `Edit`) the same shared
report file concurrently, silently clobbering one agent's output — filed
as **`L-018`** and **promoted the same phase**: `planning/agent-led-workflow.md`
step 5 now explicitly forbids two agents `Write`-ing one shared path
concurrently. **No `src/codecompass/` change.** Verified: `pytest` 554
passed / 2 skipped, `ruff check .` clean, `check_user_docs.py --strict`
clean. Closeout: `docs-reconstructor` drift audit
(`planning/retros/_drift-audit-phase-46.md`) → **NO DRIFT**;
`knowledge-curator` triage → CG-003 (`candidate`), L-017 (`retained`),
L-018 (`promoted`); `release-phase-auditor`
(`planning/retros/_audit-phase-46.md`) → **PASS WITH NON-BLOCKING
OBSERVATIONS** (no blocking gap; two cosmetic observations, both fixed
before this closeout). Retro: `planning/retros/phase-46-ledgerkit-tasks.md`.
`planning/phase-47-consolidate-findings.md` written — Stage B's decision
phase, **GATE DB** (gate G6), with a full evidence inventory from Phases
44–46.

**Phase 45, `done`** (2026-09-13) — Stage B's second phase, and
CodeCompass's first external reference-project datapoint. Registered
**Ledgerkit** at a pinned commit
(`a3cf2a77ca0075fabd4f7153d2a19f45c6e69b97`) into a scratch location
outside this repo, reconfirmed live rather than trusting the stale
2026-09-12 desk assessment — Ledgerkit had undergone its own "Core
redefinition" the same day, superseding Milestone 5 "CLI Filter Flags"
into a new Stage C. `context-evaluator`'s 3-question baseline report
(`planning/reference-projects/ledgerkit/00-baseline.md`) found Q1
(runtime dependencies) and Q3 (roadmap state) both PASS WITH GAPS / LOW
advantage, and **Q2 (what governs hledger-1.52 compatibility) FAIL — the
redefined-v1 effort's first-ever FAIL verdict**: `codecompass query
relations dev-docs/hledger-compatibility.md` returned a confident "not
found in context-graph.db" for a real, current, 238-line file that is
precisely Ledgerkit's own designated compatibility-governance document.
Root cause (`spec_docs.py::_DEFAULT_GLOBS` has no `dev-docs/**/*.md`
entry) filed as **CG-002** (triaged to `recurred`, not promoted — that's
Phase 47/GATE DB's job); the distinct symptom-layer finding that `query
relations`'s "not found" is indistinguishable from a genuine typo filed
as **L-016** (retained); Q1's optional-dependencies-silence finding filed
as **L-015** (retained). `context-health-planner`'s first genuine solo
run predicted LOW context-advantage for Phase 46, CG-002 directly
load-bearing. **No `src/codecompass/` change.** Verified: `pytest` 554
passed / 2 skipped, `ruff check .` clean, `check_user_docs.py --strict`
clean. Closeout: `docs-reconstructor` drift audit
(`planning/retros/_drift-audit-phase-45.md`) → **NO DRIFT**;
`knowledge-curator` triage → CG-002 (`recurred`), L-015 (`retained`),
L-016 (`retained`); `release-phase-auditor`
(`planning/retros/_audit-phase-45.md`) → **PASS WITH NON-BLOCKING
OBSERVATIONS** (no blocking gap; three advisory notes, none requiring
rework — see the Next concrete step section). Retro:
`planning/retros/phase-45-ledgerkit-baseline.md`.
`planning/phase-46-ledgerkit-tasks.md` written, explicitly hedged since
Ledgerkit's own Stage B isn't yet scoped/approved.

**Phase 44, `done`** (2026-09-12) — Stage B's first phase. Turned
`reference-project-protocol.md` + `context-quality-evaluation.md` into
operational machinery: `planning/reference-projects/README.md`
(registry + "how an evaluation runs"), `TEMPLATE-registration.md`,
`TEMPLATE-evaluation.md`, and a real self-test dry-run
(`_instrument-dry-run.md` — CodeCompass's own `typer` usage evaluated
against itself, verdict **PASS WITH GAPS**, advantage **LOW**: every
claim checked out on direct inspection, but a single-symbol `query
symbol` call materially undersold `typer`'s actual usage breadth — the
option/argument/exit/confirm surface, not just the two `Typer()`
construction sites). The `context-evaluator`/`reference-project-tester`
briefs were verified already consistent with the new templates (a side
effect of Phase 43c's own brief updates; no edit needed — recorded
explicitly as a correction to the plan's stale "placeholder method
sections" premise, rather than silently treated as nothing to do).
`planning/phase-45-ledgerkit-baseline.md` written, retargeted to
Ledgerkit's real current state (Milestone 5 "CLI Filter Flags"
`[PLANNED]` next). **No `src/codecompass/` change.** Running the
instrument dry-run on this fresh checkout (no `context-graph.db`/`vendor/`
existed) required `codecompass sync --budget 0` first, which mechanically
regenerated `CLAUDE.md`'s vendor table and
`.claude/skills/codecompass/SKILL.md`'s vendor table to reflect this
environment's real installed versions and its correct "0 enriched" state
(no `ANTHROPIC_API_KEY` set) — a real §0-governed diff, disclosed to and
confirmed by the user, not a manual edit. Verified: `pytest` 554 passed /
2 skipped, `ruff check .` clean, `check_user_docs.py --strict` clean.
Closeout: `docs-reconstructor` drift audit
(`planning/retros/_drift-audit-phase-44.md`) → **NO DRIFT**;
`knowledge-curator` triage → **L-012** (retained: `query symbol`'s
single-symbol scope and the unreproducible `usage_count` figure),
**L-013** (promoted: the `agent-led-workflow.md` step 10/14 amendment
below), L-014 (discarded); `release-phase-auditor`
(`planning/retros/_audit-phase-44.md`) → **PASS WITH NON-BLOCKING
OBSERVATIONS** (no blocking gap; both notes resolved — the CLAUDE.md/
SKILL.md regeneration confirmed fine to include, and the changed-file
list beyond the plan's literal "Files" section accounted for by normal
per-phase mechanics, not scope creep). Retro:
`planning/retros/phase-44-reference-project-protocol.md`.
**Process amendment (from L-013):** `planning/agent-led-workflow.md`
step 10 is now an explicit *interim* reconciliation (`CONTEXT.md` +
`CHANGELOG.md` only, never flips `ROADMAP.md` to `done`); step 14 is the
*final* done-flipping reconciliation, run once per phase after the retro
(11), triage (12), and completion audit (13) all exist. This phase's own
closeout is the first real exercise of the amended step 14.

**Phase 43b, `done`** (2026-09-11). The second Stage A→B bridge phase
(GATE-DA-scheduled): implemented `check_no_deleted_names_as_live`
(promotes L-003+L-004) and `check_generated_artifacts_match_source`
(promotes L-005's invariant half) in `scripts/check_user_docs.py` + 9 new
tests (46 in that module), and fixed `architecture/overview.md` §C's 4
self-contradictory passages directly (verified against `src/`), resolving
the plan's open judgment call in favour of fixing now rather than
deferring to Phase 61. Surfaced a correction to GATE DA's own proposed
retired-names list: `_RAW_TEXT_CHAR_CAP`/`_DOCS_FILE_CAP` were never
actually deleted (still live in `enrichment.py`, only re-attributed from
the deleted `grounded_description.py`); only
`_ESTIMATED_COST_PER_CALL_USD` was renamed. No `src/codecompass/` change
(this phase touches only `scripts/`, `tests/`, and docs). Verified:
`pytest` 554 passed / 1 skipped, `ruff` clean, `check_user_docs.py
--strict` clean; `docs-reconstructor` drift audit → NO DRIFT
(`planning/retros/_drift-audit-phase-43b.md`). Closeout: `knowledge-curator`
triaged L-003 (retained), L-004 + L-005's invariant half (both promoted),
L-008 (new, retained), and — via a follow-up dispatch the auditor's
observation 3 prompted — closed L-006's outstanding disposition
(promoted, landed in Phase 43's own follow-up commit `f6cc86d`).
`release-phase-auditor` → **PASS WITH NON-BLOCKING OBSERVATIONS**
(`planning/retros/_audit-phase-43b.md`; no blocking gap). Retro:
`planning/retros/phase-43b-standing-doc-drift-checks.md`.

**Phase 43c, `done`** (2026-09-11) — a Stage
A→B bridge phase (user request) instrumenting the agent-led development
process to produce context-quality signal, **no `src/codecompass/` or
test change**:
- NEW `planning/context-gaps/` (`README.md`, `TEMPLATE.md`, `inbox.md`) —
  a capture pathway for relationships an agent believes the graph should
  hold but mechanical detection can't produce. First entry `CG-001` (the
  Phase 43 `graph.skills_index` ↔ `cli.py::query_skills` ↔
  `skill.py::render_tool_skill` "one feature, three modules" relationship;
  `query relations src/codecompass/skill.py` errors — verified).
- NEW `planning/context-use-log.md` — a 4-line record per CodeCompass
  context retrieval (what it gave vs. the grep/read/`--help` default
  pathway, LOW/MODERATE/HIGH advantage, anything misleading). First entry:
  the live Phase 43 `query skills` use, rated **LOW** (dogfooding the
  query layer on itself is a hard case). `planning/agent-led-workflow.md`
  step 4 amended to require an entry (or a "not used — why" line).
- NEW `planning/context-health.md` + NEW
  `.claude/agents/context-health-planner.md` — the roster's **8th agent**
  (user approved Option A over keeping it a lead/curator function): a
  forward-looking "is the graph adequate for upcoming phases" assessment,
  runs `codecompass query` read-only, writes only that one file. First
  assessment: CodeCompass's own 4-dependency graph is healthy (all fresh,
  3/4 enriched, `pipdeptree` correctly unused); no Stage A→B phase is
  gated on it; the graph that matters next is Technical Clipper's,
  expected near-empty.
- NEW `decisions/0051` (Accepted) — agent-suggested context is captured
  as reviewable candidates, **never written to `context-graph.db`**;
  authoritative only via learning-lifecycle promotion into a Stage C
  detection heuristic (GATE DB) or a Stage E graph capability (GATE DD),
  each with its own ADR. Extends the `decisions/0031`/`0037`/`0045`
  determinism-first boundary to a new input source; does not supersede
  them.
- MODIFIED (append-only / additive): `decisions/0049` Consequences
  (roster-extension note), `.claude/agents/knowledge-curator.md` +
  `reference-project-tester.md` briefs (own / feed the new pathways),
  `planning/v1-redefinition/agent-led-development.md` (§2.9 new, §3 table,
  §7 step 4, roster 7→8), `conditional-generalisation.md` §1.2
  (agent-suggested-edge evidence collection started).
- Verified: `pytest` 545 passed / 1 skipped, `ruff check .` clean,
  `python scripts/check_user_docs.py --strict` clean. **No release or tag
  (gate G2-b).**
- Closeout: `docs-reconstructor` per-phase drift audit
  (`planning/retros/_drift-audit-phase-43c.md`) → **NO DRIFT**;
  `knowledge-curator` triage → `CG-001` `candidate` (provenance verified
  by code-trace) + **L-007** filed `retained` ("a mechanism existing" ≠
  "the mechanism produced output" — `context-health.md`'s first
  assessment was lead-written, not the new agent's run);
  `release-phase-auditor` (`planning/retros/_audit-phase-43c.md`) →
  **PASS WITH NON-BLOCKING OBSERVATIONS** (no blocking gap; all re-run
  verification matched). Retro:
  `planning/retros/phase-43c-agent-context-pathways.md`.
- **Tracked follow-up:** the `context-health-planner`'s first genuine
  solo run is before Phase 45, on the Technical Clipper clone — pinned
  into the Phase 45 stanza of `v1-redefinition/roadmap.md`.

**Phase 43, done** (2026-09-10) — dogfooded the agent-led loop on one
real change (Stage A's last phase; exit = **GATE DA, passed**). The code
change (**43a**): `graph.skills_index` `WHERE kind = 'skill'` →
`WHERE kind IN ('skill', 'cursor_mdc', 'slash_command')` +
`_SKILLS_INDEX_KINDS` + a `kind` per returned row;
`cli.py::query_skills` gains a "Kind" column and `kind` in `--json`;
`skill.py::render_tool_skill`'s `query skills` description reworded and
`.claude/skills/codecompass/SKILL.md` regenerated (not hand-edited).
`codecompass query skills` now surfaces Cursor `.mdc` rules and
`/discovery`, not just Skills — verified live against this repo (9 rows
vs 5). Closes the gap the Phase 17 CHANGELOG entry recorded. +2 tests
(`test_graph.py`, `test_cli.py`; full suite 545). The **first
`src/codecompass/` change since the v1 redefinition began**.
- The full 14-step agent-led loop ran for real. `docs-maintainer`'s first
  *editing* use surfaced **L-005**: it edited the generated
  `.claude/skills/codecompass/SKILL.md` directly instead of fixing
  `skill.py` and regenerating. Fixed this phase — the `docs-maintainer`
  brief gained a hard rule to check whether a file is generated from
  `src/` before editing it.
- `docs-reconstructor` per-phase drift audit
  (`planning/retros/_drift-audit-phase-43.md`) → **NO DRIFT** — the first
  phase where the audit verified real current-truth doc *edits* (to
  `docs/cli-reference.md` + `architecture/overview.md`), not just
  confirmed nothing changed.
- **No `CLAUDE.md` change, no new ADR** (43a is a bug fix — the command
  did not match its own docstring — not a non-obvious tradeoff), **no
  release or tag** (gate G2-b).
- **Closeout complete:** GATE DA retro
  (`planning/retros/phase-43-dogfood-agent-led-workflow.md`) — model
  works, roster stays at 7, no pruning; **4 amendments** landed: (1)
  `agent-led-workflow.md` step 12 + `knowledge-curator` brief — curator
  "lead runs the confirming check" handoff (from L-002); (2)
  `docs-maintainer` brief — "check if a file is generated before editing"
  (from L-005); (3) `docs-maintainer` brief — "fix, don't caveat" may mean
  *delete the paragraph* (retro lesson 3); (4) `agent-led-workflow.md`
  step 11 + `roadmap-context-curator` brief — re-dispatch the curator
  after a plan-changing retro and reconcile *every* planning doc incl.
  `v1-redefinition/roadmap.md` (from **L-006**). 2 `check_user_docs.py`
  rules → Phase 43b. `docs-reconstructor` drift audit NO DRIFT.
  `knowledge-curator` triaged L-005 (promoted the `docs-maintainer` brief
  rule; the check → 43b), moved L-002 → promoted (GATE DA chose the "lead
  runs the check" handoff), L-003/L-004 → Phase 43b; **L-006** filed this
  phase as a `candidate` (disposition confirmed at Phase 43b triage, since
  it post-dates step 12). `release-phase-auditor` ran a 3-round trail —
  **FAIL → FAIL → PASS** (first pass: 3 planning-doc bookkeeping gaps;
  re-audit #1: the CONTEXT fix left the file self-contradictory on Phase
  43's status; re-audit #2: PASS WITH NON-BLOCKING OBSERVATIONS) — every
  gap planning-doc bookkeeping, none a code defect. ROADMAP row 43 →
  `done`; **Stage A complete**.

**Phase 42, done** (2026-09-10) — the everyday documentation lifecycle
plus the milestone documentation-closeout gate. `release-phase-auditor`:
PASS WITH NON-BLOCKING OBSERVATIONS.
- `scripts/check_user_docs.py` gained 3 deterministic checks + 11 tests
  (37 in that module; full suite 543 passed / 1 skipped; `--strict`
  clean): `check_internal_links_resolve` (relative Markdown links across
  README/`docs/`/`ai-docs/`/`architecture/`/`examples/`/`CONTRIBUTING.md`;
  `#anchor` fragments informational), `check_fenced_codecompass_examples`
  (fenced `codecompass` example lines use a real subcommand / `query`
  subcommand, cross-checked against `cli.py` incl.
  `app.add_typer(name="query")`), `check_adr_status_and_supersedes`
  (every ADR has a `Status:`; every `decisions/NNNN` cross-ref resolves).
  Docstring updated.
- `.claude/agents/docs-maintainer.md` finalised (runs the new checks;
  flags `architecture/overview.md` split candidates for Phase 61 without
  restructuring; "no current-truth doc affected" is a valid output for a
  non-product phase). `.claude/skills/docs-sync/SKILL.md` and
  `planning/v1-redefinition/documentation-lifecycle.md` §5 updated.
- NEW `planning/milestone-closeout-checklist.md` — the 11-step Phase 66
  documentation-closeout gate (owner + "done" signal per step).
- NEW `planning/v1-redefinition/architecture-split-candidates.md` — the
  `docs-maintainer`'s catalogue of 36 history-shaped passages in
  `architecture/overview.md`, incl. 4 self-contradictions describing
  deleted code (`grounded_description.py` regeneration on every `sync`,
  `_RAW_TEXT_CHAR_CAP` and sibling constants, `depth = full` /
  `Depth.FULL`) as live. Input for Phase 61; not actioned now.
- Candidate learning **L-004** filed (`planning/learnings/inbox.md`): the
  per-phase drift audit is diff-scoped, so pre-existing standing rot is
  invisible to it — the 4 `architecture/overview.md` self-contradictions
  are the evidence. Likely merge-shape with L-003 at triage.
- **No `CLAUDE.md` change** (§5 was amended in Phases 40–41; Phase 42's
  plan said "apply A2 if not already applied" — it was). **No
  `src/codecompass/` change.**
- Phase 42 closeout completed: `release-phase-auditor` PASS WITH
  NON-BLOCKING OBSERVATIONS, `planning/retros/phase-42-documentation-lifecycle.md`,
  and the `docs-reconstructor` per-phase drift-audit verdict (NO DRIFT)
  all landed; ROADMAP row 42 is `done`.

**Phase 41, done** (2026-09-10) — project-learning lifecycle + phase
retros + per-phase docs-drift gate; **first real exercise of the
agent-led loop** (the smoke delegation deferred from Phase 40).
- `planning/learnings/` is operational: new `candidates/` subdir;
  `README.md` marks it live; the `knowledge-curator` brief is finalised
  against the real files and now also mines phase retros. L-001 was
  triaged → **promoted** and logged in `planning/learnings/promoted.md`
  (it records `check_readme_phase_count`'s "highest done phase ≠ product
  completeness" fix + its regression test).
- New `planning/retros/` — `README.md` + `TEMPLATE.md`; every phase from
  here on gets a lead-authored `planning/retros/phase-N-<slug>.md`. The
  template includes **Where we are** (arc/previous-phase context) and
  **Where we're going** (next-phase context) sections (user request,
  same-day `docs(phase-41)` follow-up) so retros form a running
  narrative, not isolated reports.
- `CLAUDE.md` §5 gained two DoD conditions (phase retro; independent
  per-phase `docs-reconstructor` drift audit), approved 2026-09-10 and
  mirrored into `CONTRIBUTING.md`; `decisions/0050` records both. The
  §0 diff-approval flow was followed.
- `scripts/check_user_docs.py`: new `Finding.strict` flag (blocking vs
  informational — `--strict` fails only on blocking); four new checks
  (learnings-candidate provenance fields, `promoted.md` consistency,
  stale `evidence-gathering` (info), per-phase retro presence for `done`
  phases ≥ 41) + tests (26 pass). `.claude/skills/docs-sync/SKILL.md`
  notes them.
- `.claude/agents/`: `docs-reconstructor` gains a scoped read-only
  per-phase drift-audit mode (milestone blank-slate mode unchanged);
  `release-phase-auditor` also checks retro + drift audit exist;
  `knowledge-curator` reads retros. `planning/agent-led-workflow.md`
  12 → 14 steps; `agent-led-development.md` / `documentation-lifecycle.md`
  / `proposed-governance-changes.md` updated.
- Agent-led closeout ran: `knowledge-curator` (L-001 → promoted+logged;
  L-002 "curator has no Bash", L-003 "no independent `planning/**` prose
  check" → both `retained`, Phase 47 backstop); `docs-reconstructor`
  per-phase drift audit → **NO DRIFT** (`planning/retros/_drift-audit-phase-41.md`);
  `release-phase-auditor` → **PASS WITH NON-BLOCKING OBSERVATIONS**
  (`planning/retros/_audit-phase-41.md`) — obs 1 (plan Files list) and
  obs 2 (verbatim §5 diff record) addressed this commit; obs 3 (retro
  commit hash) is a follow-up; obs 4 (workflow step inversion when a
  learning blocks verification) filed for GATE DA.
- Verified: `python scripts/check_user_docs.py --strict` clean; full
  `pytest` 532 passed / 1 skipped; `ruff` clean.

**Phase 40, done** (2026-09-09) — agent-led development model operational:
`CLAUDE.md` §8 + §1/§5/§6 changes (gate G4) mirrored into `CONTRIBUTING.md`;
`.claude/agents/` roster of 7; `planning/agent-led-workflow.md`. Forced
`check_user_docs.py` phase-count fix (excludes the redefined-v1 ROADMAP
section) + regression test; captured as L-001.

**Phase 39, done** (2026-09-09) — ratified the v1 redefinition.
`decisions/0048` (redefined v1 = product-validation milestone, not
packaging) and `decisions/0049` (agent-led development model) written and
`Accepted`. `pyproject.toml` `version` `1.0.0` → `1.0.0.dev0` (gate G1).
Gate G2 → **G2-b**: all publishing held until the redefined-v1 release
(Phase 67, first-ever publish, as `1.0.0`). `planning/ROADMAP.md`: the
Stage A–F section ratified; a reframing note added above the dated
"v1.0 scope notes" (left unedited — historical records); Phase 23 row →
"Part A done; Part B superseded"; Phases 24/25 → `deferred` (not
renumbered); `deferred`/`superseded` added to the status legend.
`README.md` Status section reframed. Verified: `pytest` 520 passed /
1 skipped, `ruff` clean, `check_user_docs.py --strict` clean, no `src/`
change, `git tag -l` still empty. `CLAUDE.md` untouched (its changes are
gate G4, Phases 40–42).

**Redefined-v1 planning session** (2026-09-09) — no code, no governance
change. Inspected the full repo, the release/version state (nothing
published; no tags; `v0.1`/`v0.2` never cut; `pyproject.toml` was at
`1.0.0` via Phase 23 Part A), and both proposed reference projects
(`technical-clipper` — TypeScript MV3 extension, **0 runtime deps**, ~7
build-only devDeps; `ledgerkit` — pure Python, **0 runtime deps**, real
context is the `hledger` executable + manuals + journal syntax). Key
finding: CodeCompass's package-source model produces near-empty output for
both real targets, so the current "publish the package tool = v1.0"
definition is a packaging milestone, not a validated-value milestone.

Produced [`planning/v1-redefinition/`](v1-redefinition/): README (overview
+ versioning assessment + risk analysis + human-decision gates), roadmap
(Stages A–F, phases 39–67, each labelled committed/experimental/
conditional), agent-led-development, learning-lifecycle,
documentation-lifecycle, reference-project-protocol, context-quality-
evaluation, ledgerkit-plan, conditional-generalisation, migration,
proposed-governance-changes (a proposed `CLAUDE.md` §8/§5/§1 diff + ADR
drafts 0048/0049 — NOT applied). Plus the `planning/learnings/` scaffold
(README, inbox, TEMPLATE, promoted log) and Stage A phase plans
(`phase-39` … `phase-43`, `phase-44`). `ROADMAP.md` got an additive
"Redefined CodeCompass v1" section.

**Everything below describes Phase 38 and the foundation (phases 0-38),
still accurate.**

**Phase 38, done** — a final-polish pass requested directly by the user
ahead of finishing Phase 23 Part B. Two research passes ran first: a full
roadmap/state review (confirmed the picture above; also caught that an
initial "README status line is stale" claim from that review was itself
wrong — re-checked directly against the real file, already accurate,
dropped), then a targeted 5-category redundancy/dead-code audit (dead
references to retired `Depth`/`promote`/`grounded_description`, duplicate
logic, unused/unpinned dependencies, doc staleness, test-suite overlap).
Three categories were clean; two had real findings, acted on:
- `cli.py`: extracted `_not_found_error()` (was duplicated verbatim across
  `query_vendor`/`query_relations`) and `_graph_session()`, a context
  manager collapsing the open/`if None: return`/try/finally scaffold that
  6 query commands each hand-repeated.
- `vendor.toml`: stripped 4 dead `depth = "surface"` lines (the retired
  `Depth` field, confirmed never read by `config.py`).
- `pyproject.toml`: added lower-bound pins to all 4 runtime dependencies
  (per user decision, over leaving them unpinned) — `decisions/0047`.
  Verified live, not just assumed: the fresh-venv smoke test resolved
  `anthropic` to a real `1.0.0`, a genuine breaking major version
  (`vendor/anthropic/src/MIGRATION.md`); checked all three of
  codecompass's own `_call_anthropic` implementations line-by-line against
  it — none touch any removed/changed API, so the pin is confirmed safe,
  not just SemVer-optimistic.
The word-boundary mention-regex duplication across `doc_mapping.py`/
`skill_scan.py`/`relation_enrichment.py` was investigated and deliberately
left alone — `decisions/0038` already documents this project's preference
for small, single-purpose modules over shared abstractions here.

Verified: `pytest` 520 passed, 1 skipped (Cargo, no toolchain — unchanged,
pre-existing). `ruff check .` clean. Manual smoke tests: `query vendor`/
`query relations` with a bad name still error identically; `query vendors`/
`query symbol` still work; `codecompass check` against this repo itself
runs clean post-`vendor.toml` edit; `python -m build` + fresh-venv install
+ `codecompass --help` re-verified after the pin change. `python scripts/
check_user_docs.py --strict` caught `README.md`'s phase count still
reading "0-37" once ROADMAP's phase-38 row landed — same catch category
Phase 37 hit — fixed inline, re-ran clean. Committed as `feat(phase-38)`
and pushed to `origin/main`.

**Phases 35-36, done** — requested directly by the user (not found via
`/discovery`), added to v1.0's blocking scope alongside the already-`done`
30-33 group. Full detail for phases 20-34 lives in `CHANGELOG.md` and git
history (per this file's own header — the log of how the project got here
isn't repeated here indefinitely).

- **35**: `README.md` restructured with a real **Setup** section (Python
  `>=3.11`, `git` required locally for vendor cloning, `ANTHROPIC_API_KEY`
  as the optional env var gating Phase B — all previously undocumented) and
  a standalone **"AI enrichment vs. no-AI usage"** section reusing
  `examples/README.md`'s real `--budget 0` transcript rather than a
  fabricated example. New `ai-docs/README.md` (capability/boundary overview
  for an agent, each "does NOT do" claim traced directly to the ADR text
  backing it — `decisions/0026`, `0031`, `0038`, `0040`, `0045` — plus 6
  example prompts) and `ai-docs/CLAUDE.md` (a short entrypoint, explicitly
  not a duplicate of root `CLAUDE.md`'s process rules). `CONTRIBUTING.md`'s
  stale "package has real modules" closing line removed.
- **36**: new maintainer-only `scripts/check_user_docs.py` (outside
  `src/codecompass/`, not a shipped feature — confirmed by the user this
  stays local tooling, never a `codecompass` subcommand) mechanically
  checks five things: every CLI command is mentioned in `docs/
  cli-reference.md`; `README.md`'s "phases 0-N" claim matches the highest
  `done` phase in `planning/ROADMAP.md`; `README.md` mentions
  `ANTHROPIC_API_KEY`; every `VendorConfig` field is mentioned in `docs/
  config-schema.md`; every file under `ai-docs/` exists and is non-empty.
  Report-only by default, `--strict` for an exit-code gate; never edits a
  file or calls AI — same mechanical-detection-only posture as `sync.py`/
  `doc_mapping.py`. New `.claude/skills/docs-sync/SKILL.md` instructs an
  agent to run it and apply fixes by judgment, never mechanically.

Verified: `pytest` 505→519 passed (1 skipped, unrelated — the Cargo smoke
test, no toolchain available), all 14 new tests for `check_user_docs.py`
covering every rule's positive/negative path plus `--strict`'s exit code
both ways. `ruff check .` clean. **Confirmed live**: `python scripts/
check_user_docs.py --strict` against this repo's real current state
reports zero findings and exits 0.

Both commits pushed... no — committed locally as `docs(phase-35)` and
`feat(phase-36)`, not yet pushed as of this update (see Next concrete step).
A whole-project `codecompass sync` was then run against this repo itself
(dogfooding): `--budget 0` first (Phase A only, confirmed the new README
Setup/AI-usage sections are already mechanically traced — `query relations
README.md` shows a new "Setup" heading linked to real `anthropic` usage
sites), then, at explicit user go-ahead, `--yes` for real — spent ~$0.02 to
AI-summarize 2 new relationships (`README.md` → the tool Skill, and →
`anthropic`'s new Setup mention), both spot-checked as accurately grounded.

**Phase 37, done** (a third small fix, found via this same dogfooding sync,
not originally planned): `spec_docs._DEFAULT_GLOBS` had no entry for
`ai-docs/`, so `query relations ai-docs/README.md` errored "not found in
context-graph.db" — neither new Phase 35 file was detected as a spec doc at
all. Fixed by adding `"ai-docs/**/*.md"` to the glob set (one line) plus a
regression test. `pytest tests/test_spec_docs.py` — 10 passed. `ruff check .`
clean. **Confirmed live**: re-synced after the fix; both `ai-docs/README.md`
and `ai-docs/CLAUDE.md` now resolve in `query relations` (5 new mechanical
relationships found, not yet AI-enriched — see Next concrete step).

## Next concrete step

**Phase 60's amended plan awaits review before implementation begins.**
The former two review-gate judgment calls are now settled by direct
instruction (`PyYAML`, mandatory Phase 54c workflow routing) — the
plan's own "Review gate" section now mostly flags scope/architecture
points for visibility rather than open decisions (the external-process
architecture itself; `stack script` vs. a full Stack project for the
reference adapter; the GPL/legal-separation non-claim). Once reviewed,
implementation proceeds per the amended plan's own §2-§7: build
`external_process.py` (generic protocol client) → `adapters/haskell.py`
(thin dispatcher) → `adapters/haskell/adapter.hs` (the real external
adapter, its API-surface logic specified by Phase 54c's own workflow
output) → fixture + `stack`-gated live smoke tests → a real end-to-end
confirmation via `codecompass sync`, checking all seven capabilities the
governing instruction named explicitly.

GATE DD (Phase 55's own gate, Stage E's precondition) remains open,
with Phase 54b's and Phase 54c's own results as evidence inputs — still
not resolved, still not forced either way; Phase 60 is not gated on it
(Stage F is a separate axis, per `decisions/0056`).

`CG-006` (Phase 55b's own residual filename-matching gap) and `CG-007`
(Phase 54b's own symbol-level cross-reference gap, not yet past the
≥2-occurrence promotion bar) remain small, independently-fundable, not
urgent. `L-021`, `L-022`, `L-023`, `L-024` are all fully applied; no
human gate is outstanding from any of them.

**Phase 52 closeout (done):** `docs-reconstructor` drift audit
(`planning/retros/_drift-audit-phase-52.md`) → **DRIFT — 2 non-blocking
findings** (a stale two-argument `apply_results` signature quote left
behind a second, already-updated quote in the same `architecture/overview.md`
paragraph; `docs/cli-reference.md` overstating the success path as a
per-entry summary when only the rejection side is per-entry) — both fixed
by the lead before commit, independently re-confirmed fixed by
`release-phase-auditor`. `release-phase-auditor`
(`planning/retros/_audit-phase-52.md`) → **PASS WITH NON-BLOCKING
OBSERVATIONS**, after independently re-running the full test suite
(567 passed / 2 skipped) and live-reproducing the two-cycle fixture
demonstration itself in an isolated copy — confirmed the rejection-path
proof and the rebuild-survives-untouched proof both genuinely reproduce.
6 minor observations total; the two actionable ones (a defensive
`isinstance(entry, dict)` check for `enrich apply` + a `DEMO.md` wording
correction about `SKILL.md` being tool-regenerated, not hand-authored)
were fixed before this closeout; the other four were non-blocking/
informational (a stricter-than-planned `RELATION_LABELS` validation
choice, arguably better than the plan's literal `_normalize_relation_label`
wording; a triage-cadence phrasing generalisation; a reproduction that
correctly didn't reproduce a one-time transient already past;
`enrich apply`'s malformed-input hardening flagged for the future, not
blocking). `knowledge-curator` triaged `L-019` (`retained` — no
generalised destination exists yet). ROADMAP row `52`, the
`v1-redefinition/roadmap.md` Phase 52 stanza + its new Stage D amendment
note, and the plan file's own status line all flipped to `done` in this
commit. Retro: `planning/retros/phase-52-context-edge-lifecycle.md`.

**Phase 51 closeout (done):** `docs-reconstructor` drift audit
(`planning/retros/_drift-audit-phase-51.md`) → **NO DRIFT**;
`release-phase-auditor` (`planning/retros/_audit-phase-51.md`) → **PASS
WITH NON-BLOCKING OBSERVATIONS** (one genuine gap flagged — the dangling
Phase-47 `L-012`/`L-015` revisit commitment Phase 51's own scope hadn't
touched — resolved as this closeout's addendum: `L-015` stays
`retained`, revisit trigger updated; `L-012` moved `retained` →
`discarded`, 7 phases old with no corroboration). GATE DC: both original
FAILs (Phase 45 Q2, Phase 46 genuine task) moved to PASS WITH GAPS;
advantage stayed LOW (structural ceiling, 0 tracked Ledgerkit vendors).
ROADMAP row `51` / the `v1-redefinition/roadmap.md` Phase 51 stanza (+
Stage C's own header, now "COMPLETE") / the plan file's own status line
(`done (2026-09-14)`) all flipped to `done` in this commit. Retro:
`planning/retros/phase-51-rerun-ledgerkit-evaluation.md`.

**Phase 49 closeout (done):** `docs-reconstructor` drift audit
(`planning/retros/_drift-audit-phase-49.md`) → **NO DRIFT** (also caught,
and the lead fixed before commit, a mistaken ADR citation in
`_relations_not_found_error`'s docstring); `release-phase-auditor`
(`planning/retros/_audit-phase-49.md`) → **PASS WITH NON-BLOCKING
OBSERVATIONS** (the only observations were exactly the pending
`CHANGELOG.md`/`ROADMAP.md`/`CONTEXT.md` reconciliation this closeout now
performs — no defect in the phase's engineering work). `src/codecompass/spec_docs.py::_DEFAULT_GLOBS`
gained `"dev-docs/**/*.md"` (closes `CG-002`); `src/codecompass/cli.py`
gained `_relations_not_found_error`, wired into `query_relations`'s
not-found branch only (closes `L-016`); 3 new tests. **This is
CodeCompass's first `src/codecompass/` change driven by external
reference-project evidence** — the redefined v1's central hypothesis
(`decisions/0048`) made concrete for the first time since Phase 43a's
own-repo dogfood. Live-verified against the real Ledgerkit clone,
independently from scratch by both the lead and the auditor: `dev-docs/`
files (including a nested path) resolve to an honest empty relations
table instead of "not found"; a genuinely nonexistent name keeps the
plain message; a still-uncovered real file
(`knowledge/DOMAIN_RULES.md`) correctly triggers the new disambiguated
message — confirming the fix generalises beyond the one directory it was
evidenced against. `docs-maintainer` reconciled `architecture/overview.md`
and `docs/cli-reference.md`. Verified: `pytest` 557 passed / 2 skipped
(+3), `ruff check .` clean, `check_user_docs.py --strict` clean.
`knowledge-curator` finalized: `CG-002` stays `promoted-to-roadmap` with
a closing note confirming the fix landed; `L-016` flipped `retained` →
`promoted`. ROADMAP row `49` / the `v1-redefinition/roadmap.md` Phase 49
stanza (+ Stage C's own header, now "in progress, one phase done") / the
plan file's own status line (`done (2026-09-13)`) all flipped to `done`
in this commit. Retro:
`planning/retros/phase-49-spec-doc-coverage-and-error-disambiguation.md`.

*(Historical, superseded by "No phase is queued next" above: at Phase
49's own closeout, Phase 51 — re-run Ledgerkit's evaluation, GATE DC —
was named the natural next step, contingent on a live re-check of
Ledgerkit's current state first. Phase 51 has since run and completed;
see "What was just completed" and the top of this section.)*

**GATE DB outcome (for reference):** fund one narrow Stage C phase
closing `CG-002` + `L-016` (Phase 49, now done); Phase 48 and Phase 50
not funded; `CG-003`/`L-017` routed to a future Stage D/E phase (**not
Phase 53** — that slot was retargeted to legacy-feature rationalisation,
2026-09-14, see below) — full reasoning in
`planning/reference-projects/ledgerkit/findings.md` §4/§7.

**Phase 47 closeout (done):** `docs-reconstructor` drift audit
(`planning/retros/_drift-audit-phase-47.md`) → **NO DRIFT**;
`release-phase-auditor` (`planning/retros/_audit-phase-47.md`) → **PASS
WITH NON-BLOCKING OBSERVATIONS** (no blocking gap; four advisory
notes — doc-file-scope disclosure, a one-step-stale triage table in
`findings.md` fixed by the lead, and an inherent limit on verifying the
`AskUserQuestion` event itself directly — all either already addressed or
explicitly non-blocking). ROADMAP row `47` / the
`v1-redefinition/roadmap.md` Phase 47 stanza / the plan file's own status
line (`done (2026-09-13)`) all flipped to `done` in that commit. Retro:
`planning/retros/phase-47-consolidate-findings.md`.

**Phase 43c closeout (done):** `docs-reconstructor` drift audit → **NO
DRIFT**; `knowledge-curator` triage → `CG-001` `candidate` + **L-007**
`retained` (L-006 stayed scheduled for Phase 43b's own triage, closed
there via a follow-up dispatch); `release-phase-auditor` → **PASS WITH
NON-BLOCKING OBSERVATIONS**. ROADMAP row `43c` / `v1-redefinition/roadmap.md`
/ plan-file status all flipped to `done` in the phase's own commit. One
tracked follow-up: the `context-health-planner`'s first genuine solo run
is before Phase 45 (pinned into the Phase 45 stanza of
`v1-redefinition/roadmap.md`).

**Phase 43b closeout (done):** `knowledge-curator` triaged L-003
(retained), L-004 + L-005's invariant half (both promoted), L-008 (new,
retained), and a follow-up dispatch closed L-006's outstanding
disposition (promoted). `release-phase-auditor` → **PASS WITH
NON-BLOCKING OBSERVATIONS** (`planning/retros/_audit-phase-43b.md`; no
blocking gap — 4 non-blocking observations, all addressed in the
closeout commit). ROADMAP row `43b` / `v1-redefinition/roadmap.md` /
the plan file's own status line all flipped to `done` in this commit.

**2026-09-12 realignment (`411cda6`) + Phases 43d/43e execution
(same day, gates G11/G12/G13 all approved):** `realignment-2026-09.md`,
`licence-migration.md`, `adoption-blueprint.md`,
`codecompass-feedback-ingestion.md`; amended `roadmap.md`,
`ledgerkit-plan.md`, `reference-project-protocol.md`,
`conditional-generalisation.md`, `context-quality-evaluation.md`,
`migration.md`, `README.md`; `decisions/0052`/`0053` `Accepted`;
`LICENSE`/`pyproject.toml`/`README.md`/`CONTRIBUTING.md` updated to
GPL-3.0-or-later. **All Stage-A work (39–43e) is now `done`.**

**Phase 44 (done, 2026-09-12) turned Stage B on:** the reference-project
protocol + context-quality evaluation spec are now operational templates
+ a registry, `context-evaluator` + `reference-project-tester` briefed
(verified already current), and it wrote the Phase 45 plan (register
**Ledgerkit** + baseline — Milestone 5, "CLI Filter Flags", is the
confirmed genuine next task). See "Immediate next step" above for
Phase 45.

Phase 41 was the first real run of the agent-led loop (the live smoke
delegation deferred from Phase 40); Phase 42 was the `docs-maintainer`'s
first real use; Phase 43 was the first full end-to-end loop and the first
`src/` change of the milestone.

Open items carried from the foundation:

1. **The first-ever publish is Phase 67** (redefined v1, `1.0.0`) — gate
   G2-b holds everything until then. No `twine`, no git tag during Stages
   A–F.
2. **A one-line pointer from root `CLAUDE.md` to `ai-docs/README.md`** —
   done (commit `0cce314`, foundation); `CLAUDE.md` now ends with a
   "See `ai-docs/README.md`" pointer. No longer outstanding.
3. **Phase 37's fix surfaced 5 new mechanical relationships for
   `ai-docs/README.md`/`ai-docs/CLAUDE.md`** — still "mentioned, not yet
   enriched". Was a Phase 43 dogfood candidate; option 2 (`query skills`
   widen) was chosen instead, so this remains an open future
   enrichment-run candidate.

The former open question of whether routing/rollup and MCP (24/25) should
be deferred is now settled: `decisions/0048` marks 24 a Stage C candidate
(conditional on reference-project evidence) and 25 post-redefined-v1, not
renumbered.

**Still outstanding, not a blocker but worth remembering:**
- ~~4 self-contradictions in `architecture/overview.md`~~ — **resolved in
  Phase 43b** (2026-09-11), not deferred to Phase 61 after all: the plan's
  in-implementation judgment call went the other way once the fix proved
  independently verifiable against `src/` for all 4 items. See
  `planning/v1-redefinition/architecture-split-candidates.md` §C
  ("Resolved in Phase 43b") — 32 broader §A/§B history-shaped trims still
  await Phase 61.
- Once a Rust toolchain is available anywhere in the pipeline,
  `decisions/0014` requires validating the Cargo adapter against real
  `cargo metadata` output and a real crate — currently entirely
  unverified.
- `extract_npm_symbols` (Phase 3) is untested against real-world `.d.ts`
  authoring styles beyond hand-written fixtures.
- `chat.py` has still never been run against the real Anthropic API in
  this environment.
- `staleness.py`'s version parser has no real PEP 440/semver correctness.
- A formal trigger-accuracy evaluation harness for per-vendor Skills
  (`decisions/0013`) remains outstanding.
- Cursor `.mdc` export has no `globs` field — documented future
  refinement, not implemented.
- `doc_chunks`' per-chunk `content_hash` (Phase 32) isn't yet consumed
  for cache-invalidation grain — `select_candidates` still hashes a
  relation's *full* source-doc text against the target's text, unchanged
  since Phase 22. Computed correctly and available for a future phase if
  chunk-grain cache invalidation is ever pursued (noted in
  `decisions/0046`), not wired up now.
- The fenced-code-block fix (Phase 34) only tracks ` ``` `/`~~~` fences,
  not indented (4-space) code blocks — not a gap in practice, since a
  heading regex requires `#` at column 0, which an indented block's
  content can never satisfy.
- `vendor/` exists in this checkout with real, enriched content — a live
  artifact of past validation runs, not a fixture. Still gitignored and
  freely regeneratable (`decisions/0010`).
- A local `.venv/` exists at the project root (gitignored) with
  `codecompass` installed editable, for local testing.
