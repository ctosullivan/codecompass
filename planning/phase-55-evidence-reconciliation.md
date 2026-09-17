# Phase 55 evidence reconciliation and next-phase plan

**Status:** planning complete, awaiting human decision on the gated
items in "H. Roadmap update proposal" and "23. Human decision gates"
below. **No implementation in this document.** Full verbatim request:
`planning/phase-55-evidence-reconciliation-prompt.md`.

This document is a reconciliation, not a phase plan for a single unit of
work — it produces one small, independently-justified next-phase
recommendation (§G) plus several explicitly-gated, not-yet-resolved
questions for later phases.

## A. Current-state reconciliation

- **CodeCompass revision inspected:** `e40d8d1` (HEAD, confirmed via
  `git fetch origin` — local and `origin/main` identical). No commits
  since Phase 54's closeout.
- **Ledgerkit revision inspected:** `d362bbb` (HEAD, confirmed via
  `git fetch origin` — local and `origin/main` identical). **This is
  five commits past `05218e3`, the revision every prior CodeCompass-side
  Ledgerkit evaluation (Phases 45/46/49/51/54) was pinned against** —
  Ledgerkit has genuinely advanced, exactly the situation this prompt's
  §3 warned against silently trusting a stale pin.
- **Latest completed CodeCompass phase:** Phase 54 (heterogeneous
  reference-material experiment) — `done`, `planning/retros/phase-54-heterogeneous-reference-material-experiment.md`.
- **Latest completed Ledgerkit phase:** Stage C Phase 3 ("wire `-q`/
  `--query` into `print`") — `dev-docs/retros/STAGE-C-PHASE-3.md`, done
  2026-09-17, no CodeCompass involvement. **The more evidentially
  important phase is Stage C Phase 2** ("CodeCompass adoption + query/
  report/CLI integration", `dev-docs/retros/STAGE-C-PHASE-2.md`,
  2026-09-16) — Ledgerkit's own first-ever real use of the `codecompass`
  CLI against its live repository, producing `validation/codecompass/findings/CC-LK-001`.
- **Next unresolved CodeCompass roadmap gate:** GATE DD (Phase 55,
  `planning/ROADMAP.md` row 55 / `v1-redefinition/roadmap.md`'s Phase 55
  stanza) — "is a generalised technical-dependency/provenance concept
  necessary for v1, informed by Phase 54's evidence." **Not resolved by
  this document** — this document assembles the evidence package and
  recommends one small, independently-justified action that does not
  require resolving GATE DD first (§F/§G), consistent with Phase 54's
  own findings.md recommendation ("each independently small and
  precedented... worth funding on their own narrow terms regardless of
  the broader ontology question").
- **Provisional observations** (`planning/context-observations/inbox.md`):
  `OBS-007` (`status: resolved`), `OBS-008`/`OBS-009` (`status: recorded`)
  — none investigated further, none promoted (this queue's items don't
  "promote," per its own lifecycle — they resolve or stay recorded).
- **Findings that have recurred:** `CG-002` (dev-docs glob coverage —
  recurred 3+ times, already `promoted-to-roadmap`, fix landed Phase 49,
  confirmed generalising to Ledgerkit's live repo by `CC-LK-001` command
  6-8 this cycle); `CG-003` (executable/behavioural evidence gap) — now
  independently corroborated a **second time** by `CC-LK-001`, see §D;
  `CG-004` (doc-to-doc relation gap, filed Phase 54) — now independently
  corroborated a **second time** by `CC-LK-001`, see §D.
- **Findings already promoted:** `L-020` (Phase 54, content-hash pinning
  vs. boundary-correctness) — `promoted`, regression test landed in
  `a4e58da`. `CG-002`/`L-016` — `promoted-to-roadmap`/`promoted`
  (Phase 49/51, pre-dates this cycle).
- **Ideas explicitly deferred:** the "External executable / behavioural
  context" sketch (displaced from Phase 54's slot, unclaimed number);
  Phase 48 (task-oriented retrieval, still not funded, no new evidence
  this cycle); MCP (`decisions/0048`, post-redefined-v1); the
  YAML-evidence-matching fallback's own generalisation beyond one
  feature family (Phase 54's own explicit deferral).
- **Roadmap items still conditional:** Stage E (Phases 56-59,
  conditional on GATE DD), Stage F (Technical Clipper, conditional on
  Stage E completing or being explicitly skipped).
- **Old assumptions superseded by newer experiments:** Phase 1's
  `LK-COMPAT-QUERY-DEPTH-001` classification (`compatible` →
  `intentional_divergence`, corrected by Ledgerkit's own executable
  testing, not by CodeCompass) — a live, real instance of exactly the
  "documentation/source said X, executable revealed Y" pattern this
  prompt's §5 asked me to recover from the repository itself, not assume.

## B. Latest CodeCompass phase summary (Phase 54)

- **Hypothesis:** can CodeCompass reproducibly pin and expose external
  hledger reference material so it materially improves an agent's
  context for a real Ledgerkit task, without prematurely committing to a
  new graph ontology?
- **Mechanism:** a real, tested Git-backed `references.toml → resolve →
  lock → fetch/cache → extract` pipeline, kept outside `src/codecompass/`
  deliberately (evidence-gathering, not a shipped feature).
- **Existing functionality reused:** `spec_docs.py`'s `dev-docs/**/*.md`
  glob (Phase 49) for detection; the `reference-project-protocol.md`/
  `context-quality-evaluation.md` evaluation instrument for rating;
  Phase 52's context-observation/context-gap queues for recording
  findings.
- **What worked:** detection (zero code change); the pipeline's own
  mechanics (resolve/lock/hash/idempotency, 13 passing tests); a
  YAML-evidence-citation-matching fallback, demonstrated real against
  Ledgerkit's own already-published `LK-COMPAT-QUERY-DATE-001.yaml`.
- **What failed:** the treatment run itself — `context-evaluator`
  independently rated it **FAIL** (baseline PASS WITH GAPS, advantage
  LOW), because a hand-drawn extraction line range silently excluded a
  documented rule its own description claimed to include (`L-020`).
- **What remained unsupported:** mechanical `mentions_artifact` relation
  detection produced zero edges for the ingested material — structurally
  incapable of relating two `spec_doc`-kind artifacts to each other,
  regardless of content (`CG-004`).
- **Graph/schema modification:** none made. Two candidates identified
  but not implemented: a `doc_artifacts.origin` value for externally-
  pinned material (`CG-005`); populating `doc_artifacts.name` for
  `spec_doc` rows (`CG-004`'s own smallest-fix suggestion).
- **Provenance limitations surfaced:** yes — `CG-005` (see above).
- **Relationship limitations surfaced:** yes — `CG-004` (see above).
- **Structured evidence vs. prose/name matching:** structured evidence
  won decisively. The YAML-evidence-matching fallback (parsing a
  compat-register entry's own `evidence.ref` field) succeeded exactly
  where prose-based `mentions_artifact` detection produced nothing.
- **Context quality:** did not materially improve on the one task tested
  (LOW advantage, treatment FAIL) — but the failure was a methodology
  defect in the experiment's own execution, not proof the mechanism
  can't work; the fix (a corrected line range + a regression test) was
  applied within the same phase.
- **Left to the next decision gate:** whether to generalise the ingestion
  pipeline into `src/codecompass/`, whether to fund `CG-004`/`CG-005`,
  and whether the YAML-evidence-matching mechanism should be tried
  against a second, richer evidence shape (a compat-register entry with
  `kind: executable` evidence, not just `manual`/`source` — **now
  available**, see §D).

Per this prompt's own instruction, this technically-partial prototype is
**not** treated as evidence the capability belongs in v1 — Phase 54's
own findings.md explicitly recommended keeping it experiment-scoped, and
that recommendation stands unchanged by this reconciliation.

## C. Ledgerkit consumer-evidence summary (Stage C Phase 2, `CC-LK-001`)

- **Genuine task:** integrating the already-built, previously-standalone
  `ledgerkit/query/` subpackage into `reports.py`/`cli.py` (a real `-q`/
  `--query` CLI flag) — Ledgerkit's own next unstarted piece of Stage C
  work, not a task shaped to flatter CodeCompass.
- **CodeCompass result:** bare `codecompass --budget 0` against the real,
  live Ledgerkit repository (never done before this phase) bootstrapped
  0 vendors, generated a generic tool Skill/`/discovery` command matching
  CodeCompass's own test-fixture boilerplate near-verbatim, and — **without
  being asked** — inserted an empty `<!-- codecompass:start/end -->`
  routing-table block into Ledgerkit's own `CLAUDE.md`. `query relations`
  on all three of the task's genuinely relevant docs (`hledger-compatibility.md`,
  `07-query-regex.md`, `17-query-semantics-brief.md`) returned tracked-
  but-empty (confirming Phase 49's fix generalises to files that didn't
  even exist at Phase 51's pin), including **zero relation between the
  two dev-docs files to each other**, despite one being the literal
  research brief the other was implemented from. `query relations` on a
  `.py` source file correctly returned the disambiguated "not a spec/
  vendor doc" message, not a false "not found."
- **Manual rediscovery:** the shared `_posting_matches` helper, `cli.py`'s
  argparse conventions, the relationship between `query/eval.py`'s
  matcher functions and which report delegates to which (found from a
  prior Ledgerkit retro/brief, not CodeCompass), a latent regex-parser
  bug, and — critically — **two real CLI bugs and one compat-register
  misclassification, found entirely through direct differential testing
  against the pinned hledger binary**, a category of evidence CodeCompass
  has no representation for.
- **Context advantage:** **LOW** — independently rated by Ledgerkit's
  own `context-curator` role (which mirrors CodeCompass's own
  `context-quality-evaluation.md` instrument exactly: PASS/PASS WITH
  GAPS/FAIL, strong/adequate/weak criteria). "A fresh competent agent
  doing this exact task would get materially the same (zero) starting
  advantage... as from simply opening `reports.py`/`cli.py` directly."
  Verdict: **PASS WITH GAPS** — explicitly not a defect (CodeCompass
  returned honest emptiness, not a confident wrong answer).
- **Important missing context:** doc-to-doc relations (matches `CG-004`);
  executable/behavioural verification as a representable evidence type
  (matches `CG-003`).
- **Process limitations, disclosed by Ledgerkit itself, not by this
  reconciliation:** the phase's own retro states plainly that the
  differential-testing step — designed in the phase's own plan to be a
  separately-dispatched `compat-differential-tester` agent, specifically
  for independence — was instead done directly by the lead session.
  Ledgerkit's retro treats this as a real gap, not a technicality: "the
  *process* the plan designed specifically to keep implementation and
  verification separate wasn't actually followed." **This reconciliation
  adopts the same distinction Ledgerkit itself drew**: evidence quality
  is high (the two bugs and the reclassification are objectively
  re-runnable against the same pinned binary by anyone), but process
  quality is lower than designed, so conclusion confidence for anything
  resting solely on "an independent evaluator confirmed this" should be
  read as *lead self-report, later spot-checkable*, not *independently
  witnessed at the time*.
- **Material influence on the implementation:** none from CodeCompass's
  own output; the real feature (the `-q` flag, the bug fixes, the
  reclassification) came entirely from direct source reading, the prior
  Ledgerkit retro/brief, and differential testing.
- **Most important technical evidence, and its representability:** the
  hledger binary's own observed behaviour (contradicting a
  source-reading-only classification) — **not currently representable
  in CodeCompass at all** (confirms `CG-003`).
- **Internal project-document relationships visible?** No — zero,
  confirmed directly (confirms `CG-004`).
- **External executable behaviour representable?** No (confirms `CG-003`).
- **Ledgerkit's own recommendation:** *"not yet warranted as a required
  step... six consistent data points now, across both directions of
  usage... all landing at the same structural ceiling (0 tracked
  vendors; no doc-to-doc relation mechanism; no executable-technical-
  dependency concept). Running it remains free, fast, and non-invasive...
  worth doing again on a future phase if the task shape differs enough...
  but not worth making mandatory per-phase overhead."*
- **Findings produced:** `CC-LK-001` (`.yaml`/`.md` + baseline-evidence
  transcript) — Ledgerkit's first-ever `CC-LK-NNN` finding.

## D. Combined evidence matrix

| Finding / pressure point | CodeCompass-phase evidence | Ledgerkit-phase evidence | Independent recurrence? | Impact on real agent work | Existing mechanism | Smallest plausible improvement | Graph/schema change? | New evidence/dependency concept? | Confidence | Recommendation |
|---|---|---|---|---|---|---|---|---|---|---|
| **Doc-to-doc relation gap** (`spec_doc` rows never get `name`, so `mentions_artifact` can never match them) | Phase 54: 6 ingested reference files ↔ Ledgerkit's own `dev-docs/hledger-compatibility.md`, zero edges, root-caused by direct code reading (`CG-004`) | `CC-LK-001`: 3 real, topically-obvious dev-docs (one is literally the implementation plan for another), zero edges — same root cause, independently confirmed by Ledgerkit's own inspection of `codecompass query relations`' output, on a live-repo real task Phase 54 never touched | **YES** — two independent tasks, two independent codebases-under-test (CodeCompass's own scratch copy vs. Ledgerkit's real live repo), two independent observation points; the *causal diagnosis* (root cause: `name` never populated) was cross-referenced by Ledgerkit's own finding against `CG-004`'s already-published text rather than independently re-derived from `spec_docs.py`'s source — the **raw observation** (zero relations among obviously-connected real docs) is fully independent; the **causal explanation** is not a second independent derivation. Treated as YES for the observation, noted as partial for the diagnosis. | High when it occurs — this is exactly the kind of relationship ("what does this brief implement, what implements this brief") a real development task needs and currently gets zero help with from CodeCompass | `doc_mapping.py::build_doc_relations_edges`'s existing `mentions_artifact` word-boundary matcher — unmodified logic, just currently starved of eligible targets | Populate `doc_artifacts.name` for `spec_doc` rows (e.g. from a Markdown H1 title, or a stable path-derived slug when no H1 exists) — no new relation kind, no new table, reuses the existing matcher exactly as `Ledgerkit`'s own `CC-LK-001` and `CodeCompass`'s own `CG-004` both independently proposed | NO — `name` is already a nullable `TEXT` column on `doc_artifacts` | NO | **HIGH** | **IMPLEMENT** (small, precedented, doubly-corroborated) |
| **Executable/behavioural evidence has no representation** | Phase 54: `match_compat_register_evidence` demonstrated real against `LK-COMPAT-QUERY-DATE-001.yaml`'s `manual`/`source` evidence kinds only — never touched `kind: executable` | `CC-LK-001`/Stage C Phase 2: `LK-COMPAT-QUERY-DEPTH-001` reclassified `compatible → intentional_divergence` **purely on executable evidence** contradicting a source-reading-only claim; 2 real CLI bugs found the same way — CodeCompass has no representation for any of it | **YES** — a materially different mechanism (executable differential testing vs. Phase 54's own manual-extraction pipeline) independently converges on the same gap CodeCompass's own `CG-003` (filed Phase 46, over a year of prior evidence) already named | High — this is the single technical-evidence class both projects agree is currently invisible to CodeCompass, and the one that most recently *changed a real, previously-wrong compatibility claim* | None — `doc_relation_enrichment`'s `RELATION_LABELS` has no executable-observation concept; `doc_artifacts` has no executable-artifact `kind` | Unknown until generalised beyond hledger — see §11/Risks | UNKNOWN | YES (a new evidence category, not just a relation) | **MODERATE** — real, recurring, but zero cross-domain evidence yet (only ever tested on hledger) | **DEFER** — do not architect from 2 same-domain instances; needs Technical Clipper or an isolated non-hledger check first (§17) |
| **YAML-evidence-citation-matching fallback is real and works** | Phase 54: `OBS-008`, tested against `LK-COMPAT-QUERY-DATE-001.yaml` (`manual`+`source` evidence only) | Not directly tested this cycle, but `LK-COMPAT-QUERY-DEPTH-001.yaml` (new/changed this cycle) has a **richer** evidence shape (`manual`+`source`+`executable`) available for a follow-up test | N/A (mechanism proof, not a gap) | Moderate — a more reliable relation source than prose-mention detection, demonstrated, not hypothetical | `reference_pipeline.py::match_compat_register_evidence` (outside `src/codecompass/`) | Re-run the exact same mechanism against `LK-COMPAT-QUERY-DEPTH-001.yaml` (now available, unlike at Phase 54's own writing) as the "second feature family" Phase 54's own retro said was needed before generalising | NO (still standalone script) | NO (reuses the compat-register's own existing structured fields) | **MODERATE** | **EXPERIMENT** — the concrete next validation step for this specific mechanism, cheap, already-scoped |
| **`origin` enum has no externally-pinned-reference value** | Phase 54: `CG-005`, one instance, CodeCompass's own experiment | None — Ledgerkit has not (and structurally cannot, without CodeCompass's ingestion feature) produce this class of content itself | NO — single occurrence, tied entirely to whether pinned-reference ingestion is ever productised | Low on its own — inert until something actually writes an `origin`-worthy row | `doc_artifacts.origin` CHECK enum, 5 closed values | Add one new value, following the exact one-value-per-phase precedent | Trivial (CHECK-enum addition) | NO | **LOW** (until §10's own gate resolves) | **DEFER** — pointless to fund standalone; bundle with a future pinned-references decision, not now |
| **Bare `codecompass` mutates a project's `CLAUDE.md` even for zero-value output** | Not tested this cycle (CodeCompass's own dogfooding never runs bare `codecompass` against a fresh 0-vendor project from a cold start the way Ledgerkit just did) | `CC-LK-001`/baseline-evidence: an empty routing-table block was inserted into Ledgerkit's real `CLAUDE.md` without being asked, reviewed, and manually reverted as zero-current-value | NO — first occurrence, not previously observed by CodeCompass's own dogfooding | Low-moderate — real, disclosed friction (a human/agent had to consciously decide to revert it), but not a correctness defect — this is `decisions/0017`'s zero-question-bootstrap design working exactly as specified | `index.py::update_root_claude_md`, `decisions/0017` | None proposed — this is intentional, disclosed, documented behaviour, not a bug; the new information is that a 0-vendor project makes the auto-insert's cost-benefit balance look worse than the design anticipated | NO | NO | **LOW** (single instance) | **RETAIN** (as an observation; file below, §19) |
| **Generated entry points (tool Skill, `/discovery`) are pure boilerplate for a 0-vendor project** | Not previously tested from a fresh real-project cold start | `CC-LK-001`: generated Skill/`/discovery` content "matched CodeCompass's own test-fixture template near-verbatim — nothing Ledgerkit-specific" | NO — first occurrence | Low — expected consequence of 0 tracked vendors, not a defect; consistent with every prior "0 vendors → LOW advantage" finding from both projects | `skill.py::render_tool_skill`, `commands.py::render_discovery_command` | None — this is the entry-point architecture behaving correctly for a project with nothing yet to route to; not a design flaw | NO | NO | **LOW** | **RETAIN** (confirms the lightweight entry-point → task-discovery → primary-evidence direction is *appropriate*, not broken, for this project shape) |

## E. Gate recommendations

| Candidate | Evidence | Recommendation |
|---|---|---|
| Populate `name` for `spec_doc` rows (fixes `CG-004`) | Two independent real-task corroborations (Phase 54, `CC-LK-001`); zero schema change; reuses an existing, unmodified matcher | **IMPLEMENT** — see §F/§G |
| Re-test `match_compat_register_evidence` against `LK-COMPAT-QUERY-DEPTH-001.yaml`'s executable evidence | One working prototype (Phase 54), a newly-available richer real test case | **EXPERIMENT** — small, cheap, directly answers Phase 54's own "second feature family" gap; not scoped as its own phase, but named as a follow-on validation step within §G |
| Add an `origin` value for pinned reference material (`CG-005`) | Single instance, no independent corroboration, no consumer for it yet | **DEFER** |
| Productise the Phase 54 ingestion pipeline into `src/codecompass/` | One experiment, one reference source, one FAIL verdict (methodology, not mechanism) — Phase 54's own retro already recommended against this | **DEFER** |
| Executable/behavioural evidence as a first-class graph concept | Two same-domain (hledger) instances; zero cross-domain evidence; prompt's own §11 requires proving generalisation first | **DEFER**, pending a cross-domain check (§17) |
| Structured-citation-based relationships generally (beyond the one fallback already built) | Directly evidenced twice now (Phase 54's fallback; Ledgerkit's own compat-register schema, independently confirmed stable and used across 25+ real entries) — but no schema/detection change has been built for it yet inside `src/codecompass/` | **EXPERIMENT** (the re-test above is the concrete next step) |
| Claude entry-point architecture (routing/`/discovery`/Skills) | Confirmed appropriate for a 0-vendor project; no evidence of a design flaw | **RETAIN** — no change |
| Mandatory per-phase CodeCompass usage in Ledgerkit's own workflow | Six consistent LOW-advantage data points, Ledgerkit's own explicit recommendation against | **RETAIN** (Ledgerkit's own call, not CodeCompass's to override) |

**Out-of-scope reassessment (§15):**

| Candidate | Current evidence | Decision |
|---|---|---|
| Embeddings / vector search / semantic similarity | NOT SUPPORTED — every real win this cycle (the YAML-evidence fallback) came from *more* structured, exact matching, not similarity search | **REJECT** |
| General RAG | NOT SUPPORTED | **REJECT** |
| Task-oriented retrieval | NOT SUPPORTED (no new evidence; Phase 48 remains unfunded, GATE DB's own prior call) | **DEFER** |
| Shared-agent memory/context | NOT SUPPORTED | **DEFER** |
| MCP | NOT SUPPORTED, out of the redefined-v1's own scope (`decisions/0048`) | **DEFER** |
| IDE integration | NOT SUPPORTED | **DEFER** |
| Automatic graph mutation by agents | NOT SUPPORTED — actively contradicted by `decisions/0051`/`0054`'s own settled invariant (agent output is never authoritative until curated) | **REJECT** (architectural invariant, not just unfunded) |
| Universal/broad technical-dependency ontology | NOT SUPPORTED — Phase 54 explicitly avoided this and found two independently-fundable *narrow* fixes instead | **REJECT** (for now — re-open only if Stage F/cross-domain evidence changes this) |
| Multi-repository graph | NOT SUPPORTED — the actual cross-project evidence exchange happening right now (Ledgerkit citing Phase 54's retro in its own `ROADMAP.md`/`CONTEXT.md`; this document citing `CC-LK-001`) works via **committed files read by a human/agent**, not a shared live graph | **DEFER** |
| Hosted service | NOT SUPPORTED | **DEFER** |
| General autonomous-development orchestration | NOT SUPPORTED, contradicts `CLAUDE.md` §8's own fixed point ("Claude Code orchestrates; CodeCompass never spawns agents") | **REJECT** (architectural invariant) |

## F. Minimum justified architecture change

- **Problem:** CodeCompass's existing, unmodified `mentions_artifact`
  relation-detection mechanism cannot relate two project-authored
  Markdown artifacts to each other, in any project, regardless of
  content — because `spec_docs.py::scan_spec_docs` never populates
  `doc_artifacts.name` for `spec_doc`-kind rows, and the matcher only
  considers named artifacts as targets.
- **Evidence:** two independent real-task instances (`CG-004`, Phase 54;
  `CC-LK-001`, Ledgerkit Stage C Phase 2) — see §D row 1. This is exactly
  the "does the problem recur/generalise" bar the prompt's own decision
  hierarchy (§22) sets for moving past "retain observation."
- **Smallest solution:** populate `name` for `spec_doc` rows in
  `spec_docs.py::scan_spec_docs` — read the file's first Markdown `#`
  heading if present, else derive a stable slug from the path (matching
  the existing fallback posture other detectors already use, e.g.
  `skill_scan.py`'s never-raises philosophy). No new table, no new
  `relation_kind`, no new CHECK-enum value, no change to
  `doc_relation_enrichment`/`RELATION_LABELS`. `build_doc_relations_edges`
  itself needs zero logic change — it already treats *any* named
  `doc_artifacts` row as an eligible `mentions_artifact` target.
- **Why a larger solution is unnecessary:** a generalised
  "project-artifact-relationship ontology" (research-brief→plan→
  implementation→ADR→compat-record→test, per the prompt's §8) is not
  evidenced yet at this granularity — both real instances found so far
  are specifically "two spec-doc-kind Markdown files should be able to
  mention each other," not a demand for typed relationship kinds
  (`IMPLEMENTED_BY`, `VERIFIED_BY`, etc. — the prompt's own §9 examples,
  explicitly not adopted here for lack of evidence they're needed yet).
  `mentions_artifact`'s existing single relation kind, once artifacts are
  actually named, already expresses "these two docs are connected" —
  sufficient for what's been observed twice.
- **Migration implications:** none. `doc_artifacts.name` is already
  nullable; existing rows with `name IS NULL` are simply excluded from
  the new matcher opportunities they'd now be eligible for, exactly as
  today. No existing row's meaning changes.
- **Trust/provenance implications:** none — this is a purely mechanical,
  deterministic detection change (a title-derived string, not an AI
  inference), fully consistent with `decisions/0031`/`0045`'s existing
  "mechanical detection, AI only interprets what's already proven"
  boundary. No new relation trust tier is introduced.

## G. Proposed next phase plan — implemented as Phase 55b, `done`

**Resolved (2026-09-17):** user approved implementation ("Approved");
numbered as a bridge phase, **"Phase 55b"** — option (b) below, this
document's own stated preference. Full account:
`planning/phase-55b-spec-doc-name-population.md`,
`planning/retros/phase-55b-spec-doc-name-population.md`. The rest of
this section is preserved as originally written (the plan as presented
for approval), not rewritten with hindsight.

**Numbering conflict, surfaced rather than silently resolved (per §23):**
this phase is independently justified without resolving GATE DD first
(Phase 54's own findings.md said as much), so it does not consume Phase
55's own slot. But unlike every prior retarget this session (Phases
52/53/54, each displacing exactly one adjacent sketch), **every integer
through 63 is already claimed by a pre-written, detailed sketch**:
Stage E occupies 56-59 (`v1-redefinition/roadmap.md`'s own "Phase 56 —
Technical-dependency abstraction," "57 — Provenance/evidence features,"
"58 — Migrate package/source," "59 — Re-validate against Ledgerkit"),
Stage F occupies 60-63. None of these four sketches matches this
phase's own content (a narrow, unconditional `spec_docs.py` fix, not
gated on GATE DD at all) — so, unlike Phase 54's clean single-slot
retarget, inserting this phase into the existing sequence would require
renumbering four already-detailed CONDITIONAL stages, not amending one.

**This document does not resolve that renumbering unilaterally.** Two
options, for the user to choose between (or reject in favour of a third):

- **(a) Renumber**: this phase becomes 56; Stage E's own four sketches
  shift to 57-60, Stage F's four shift to 61-64 — mechanical, but touches
  eight pre-written stanzas in `v1-redefinition/roadmap.md` for the sake
  of inserting one small phase ahead of them.
- **(b) Number it outside the main sequence**, analogous to the
  43d/43e "bridge phase" lettering precedent (the only prior instance of
  a phase not fitting the plain sequential count) — e.g. **Phase 55b** —
  leaving Stage E/F's own pre-written numbers completely untouched.
- **(c) Something else the user prefers** (e.g. holding this work until
  GATE DD resolves anyway, folding it into whichever Stage E phase ends
  up covering project-artifact relationships specifically, since it's
  genuinely adjacent to that stage's own subject matter even though it
  doesn't require waiting for the gate).

**This document's own recommendation, offered but not imposed:** (b) —
it's the smaller, less disruptive edit, has a direct precedent in this
project's own history, and correctly signals "this doesn't fit the
normal Stage sequence's own conditions" without pretending it's Stage
E/F work that happens to run early. The plan below refers to it as
"this phase" throughout, deliberately not pre-committing to a number.

- **Objective:** close `CG-004`/the doc-to-doc relation gap
  independently corroborated by Phase 54 and `CC-LK-001`, and use the
  fix to run a real before/after validation against the exact task shape
  `CC-LK-001` already documented as a live weakness.
- **Scope:** `spec_docs.py::scan_spec_docs` populates `doc_artifacts.name`
  for every `spec_doc` row (H1-derived, path-slug fallback); no other
  detector changed. As a secondary, small, separately-reported step: re-run
  `reference_pipeline.py::match_compat_register_evidence` (Phase 54's own
  fallback, still outside `src/codecompass/`) against
  `LK-COMPAT-QUERY-DEPTH-001.yaml`'s richer 3-evidence-kind shape, to
  answer Phase 54's own open "second feature family" question — reported
  as evidence for GATE DD, not implemented as a product feature this
  phase either.
- **Non-goals:** no new `relation_kind`, no new `origin` value, no
  pinned-external-reference productisation, no executable-evidence
  representation, no `vendor.toml` change, no CLAUDE.md change.
- **Affected architecture:** `src/codecompass/spec_docs.py` only (one
  function). `doc_mapping.py`, `graph.py`'s schema, and every enrichment
  table are untouched.
- **Agent roles:** lead implements (small, single-function change,
  `src/` — the lead's own domain per `CLAUDE.md` §8); `docs-maintainer`
  reconciles `architecture/overview.md`'s doc-artifact description if it
  currently asserts `spec_doc` rows never carry a name (verify, don't
  assume); `docs-reconstructor` per-phase drift audit; `reference-project-tester`
  + `context-evaluator` for the before/after Ledgerkit validation (§16);
  `knowledge-curator` triage; `release-phase-auditor` final pass.
- **Implementation sequence:** (1) implement + unit-test the `name`
  population in isolation (a title-extraction/slug function + tests
  against CodeCompass's own repo's spec docs); (2) re-run
  `codecompass query relations` against the **real, live Ledgerkit
  repository** (read-only, same discipline as every prior evaluation —
  never commit anything CodeCompass generates into Ledgerkit) on the
  exact three files `CC-LK-001` already tested, to produce a genuine
  before/after comparison against a *committed, real* prior weakness,
  not a synthetic re-test; (3) independent `context-evaluator` rating of
  the after-state; (4) the compat-register-evidence re-test (secondary,
  reported not productised); (5) normal closeout.
- **Tests:** unit tests for the title/slug extraction (H1 present, H1
  absent, multiple H1s, empty file); an integration test confirming a
  `spec_doc`-kind row with a real name now participates in
  `mentions_artifact` detection (reusing the existing `doc_mapping.py`
  test patterns, no new test infrastructure).
- **Independent evaluation:** `context-evaluator` rates the after-state
  against the same rubric `CC-LK-001` already used (PASS/PASS WITH GAPS/
  FAIL, strong/adequate/weak, LOW/MODERATE/HIGH advantage) — on the
  *same three files* `CC-LK-001` tested, for a clean, apples-to-apples
  before/after.
- **Reference-project validation:** **Ledgerkit again** (see §17) — the
  real, live repository, read-only, the exact same task shape
  `CC-LK-001` already documented. This is the textbook case for
  "Ledgerkit again": the improvement directly targets a well-documented
  Ledgerkit weakness and creates a clean before/after comparison,
  exactly the bar the prompt's §17 sets.
- **Definition of Done:** standard `CLAUDE.md` §5 DoD + the before/after
  `context-evaluator` rating shows a genuine change (or, honestly, does
  not — a null result here is reportable, per this project's own
  standing "treat negative results as valid evidence" posture) on the
  three real `CC-LK-001` files specifically + `CG-004` updated to
  `promoted-to-roadmap`/closed with the fix's commit + the compat-
  register-evidence re-test reported into this document's own evidence
  trail (or a follow-up note) for GATE DD's eventual benefit.

## H. Roadmap update proposal

- **Phase added:** Phase 55b (§G above), `done` — resolved as of
  2026-09-17, see §G's own update.
- **Phases reordered:** none — option (b) (bridge letter) was chosen;
  Stage E's/F's own pre-written stanzas are untouched.
- **Displaced work:** none — this was a genuinely new, independently-
  justified unit of work, not a retarget of an existing sketch (unlike
  Phases 52/53/54's own single-slot retargets).
- **Deferred work (unchanged from before this cycle, restated for
  completeness):** the "External executable / behavioural context"
  sketch (unclaimed number); `CG-005`; pinned-reference productisation;
  Phase 48; MCP; and now also `CG-006` (Phase 55b's own residual
  filename-vs-title matching gap), a new small, independently-fundable
  follow-on of the same shape as `CG-004` itself.
- **Unchanged work:** GATE DD (Phase 55) remains open, now with a
  materially richer evidence package (this document plus Phase 55b's own
  real-world validation) than it had after Phase 54 alone — still not
  resolved, per §23.
- **Human gates:**
  1. **GATE DD itself** (Stage E scope) — not resolved here or by Phase
     55b, evidence package updated.
  2. **The new phase's number** (§G) — resolved: "Phase 55b."
  3. **A `CLAUDE.md` §1 amendment** (`L-021`, drafted in
     `planning/v1-redefinition/proposed-governance-changes.md` §D,
     surfaced during Phase 55b's own triage) — a new gate this
     reconciliation didn't originally anticipate, not yet presented to
     or approved by the user, not yet applied.

## I. Risks

- **Overfitting to Ledgerkit:** actively mitigated in this document —
  every Ledgerkit-motivated finding is stated at two levels (§D's
  "Finding / pressure point" column uses general framing; the
  executable-evidence row explicitly requires cross-domain proof before
  funding, per §18). The one item recommended for IMPLEMENT (`CG-004`'s
  fix) is a generic "two Markdown artifacts should be relatable"
  capability, not "hledger-compatibility-doc support."
- **Premature ontology:** avoided — no new relation kind, table, or
  enum value is implemented this cycle; the executable-evidence and
  pinned-reference questions are both explicitly deferred pending
  broader evidence.
- **Graph noise:** the `name`-population fix could, in principle, produce
  false-positive `mentions_artifact` edges if two unrelated docs happen
  to share a generic title word — worth a real check during this phase's
  own implementation (e.g. is "Introduction" or "Overview" a common H1
  across unrelated docs?), not assumed safe.
- **Stale references:** N/A this cycle — no external reference material
  is being pinned by the recommended change.
- **Source/reference provenance:** unaffected by the recommended change;
  remains an open question for the deferred pinned-reference work.
- **Citation ≠ truth:** explicitly preserved in this document's own
  framing (§D's executable-evidence row: a citation is evidence a
  relationship is asserted, not proof the underlying claim is correct —
  matches `LK-COMPAT-QUERY-DEPTH-001`'s own history exactly, where a
  *correctly cited* source claim was still substantively wrong until
  executable evidence corrected it).
- **Schema churn:** none this cycle (§F).
- **Evaluation independence:** explicitly flagged, not laundered —
  Ledgerkit's own Stage C Phase 2 differential-testing step was done by
  the lead, not a separate agent, and this document says so plainly
  (§C) rather than treating the finding as equivalently strong to a
  genuinely independent evaluation. CodeCompass's own Phase 54 evaluation
  *was* independent (`context-evaluator`, a separate dispatch) — the two
  are not conflated.
- **Context overhead:** the recommended fix adds no new query surface,
  no new CLI command, no new documentation burden beyond a one-line
  `spec_docs.py` docstring update — minimal overhead by design.
- **Recreating cheaply-discoverable information:** the `name`-population
  fix specifically targets a case where the connection was *not* cheaply
  discoverable by a fresh agent in `CC-LK-001`'s own real task (the
  agent had to read the retro/brief directly, per §C) — this is exactly
  the "materially improve over cheap direct exploration" bar CodeCompass
  is supposed to clear, not one it's already clearing another way.

## Independence discipline, stated explicitly (per §6's own instruction)

What was **not** counted as independent corroboration in this document,
and why:

- `CC-LK-001`'s own text explicitly cites `CG-003`/`CG-004` by name and
  frames its finding as "corroborating," not "novel" — this document
  respects that self-characterization rather than inflating it, and the
  matrix (§D) marks the *causal diagnosis* half of `CG-004`'s
  corroboration as partial, not full, for exactly this reason.
- Stage C Phase 3's own retro mentioning Phase 54's reference-material
  experiment is a **citation of an existing finding for planning
  purposes**, not a new data point — not counted as a third
  corroboration of anything in §D.
- `OBS-007`'s "detection generalises" finding and `CC-LK-001`'s command
  6-8 confirming the same `dev-docs/**/*.md` glob fix both trace to the
  same underlying Phase 49 fix — counted as **one** piece of
  corroborating evidence (now doubly confirmed across two real,
  independent tasks), not treated as two separate findings needing
  separate rows.
