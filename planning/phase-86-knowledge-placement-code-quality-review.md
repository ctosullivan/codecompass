# Phase 86: Knowledge-Placement and Code-Quality Review — plan

**Status: planned, not started.** Written per `CLAUDE.md` §1. Does not
implement Phase 86 — see `planning/retros/phase-86-knowledge-placement-
code-quality-review.md` for the (not-yet-existing) implementation retro,
created only once implementation begins.

Governing scope: `planning/v2-roadmap.md` §"Phase 86 — Knowledge-
Placement and Code-Quality Review" (10-point roadmap-depth sketch,
`decisions/0084` §2); `decisions/0085` §4 (the formal eight-category
Knowledge Placement Policy table and the three named enforcement
classes — the authoritative, later-dated source this plan's own §4
reproduces verbatim rather than re-deriving).

---

## 1. Verified current state and dependencies

Directly inspected this session, HEAD `b434b9d`, before writing a
single word of design below — per this project's own established
discipline (`L-113`) of grounding a new validator's design in the real
corpus before finalising anything, applied here one step earlier, at
plan-writing time itself.

**Phase 85 is `done`**, corrective pass closed, both independently
confirmed PASS WITH NON-BLOCKING OBSERVATIONS (three audit passes in
total across the corrective pass). Its real-corpus `--strict` baseline
(`scripts/check_self_knowledge_quality.py`) currently reports 35
findings, 26 blocking, 9 informational — re-confirmed this session
(`.venv/bin/python scripts/check_self_knowledge_quality.py --strict
--ledgerkit-root ~/projects/ledgerkit`, exit 1, same split). The 26
blocking findings are two categories of pre-existing knowledge-quality
debt (missing evidence citations on nine `status: verified`
Requirements; `balance-from-spec`'s own unverified-scope/stale-citation
findings), filed as `L-114` (retained) and cross-referenced into the
pre-existing `L-107` (retained) — see §2 below for this plan's own
disposition review. **None of these 26+9 findings concerns knowledge
*placement*** (where something should live, whether structure/ownership
is appropriate) — every one concerns evidence *completeness* or oracle
*verification currency*, both squarely Phase 84/85's own domain. This
plan's own §2 confirms, rather than assumes, that none is Phase-86-
relevant.

**Phase 86's one stated prerequisite (`decisions/0084` §2 point 86) is
Phase 85** — satisfied. Phase 86 does not depend on Phase 83
(Semantic Change Assurance) functionally, though it reuses the same
`Finding`-with-`strict`-flag convention Phase 82/83 hardened.

**The real artifact surface this phase operates on**, confirmed by
direct inspection this session:

- `src/codecompass/` — 29 top-level modules (`ls src/codecompass/*.py`),
  excluding `adapters/`. 45 distinct `decisions/NNNN` citation strings
  found across them (`grep -rho 'decisions/[0-9]\{4\}' src/codecompass/
  *.py | sort -u | wc -l`).
- `decisions/` — 92 ADR files. 10 of them announce, in their own title,
  that they supersede an earlier-numbered ADR (`grep -lE "superseded by|
  is superseded" decisions/*.md`), including `decisions/0061` ("`0019`
  is superseded by `0035`").
- `docs/decisions.md` (the existing, already-committed mechanical
  title+status index) **already documents, in its own prose, the exact
  failure mode this phase's mechanical check formalises**: "the Status
  column is read mechanically from each ADR's own first-line status
  field only, never cross-checked against whether some *later*,
  higher-numbered ADR's own title announces that it supersedes an
  earlier one by title alone. A real, confirmed example: `0019` shows
  `Accepted` below, but `0061`'s own title states it is superseded by
  `0035`." This is independent, pre-existing, already-committed project
  self-knowledge that this exact gap exists — not an assumption this
  plan introduces.
- **A real, independently confirmed instance of that exact gap
  materialising in actual source code**, found this session by directly
  reading the file, not assumed: `src/codecompass/source_resolution.py`'s
  own module docstring (lines 1-2) reads "Upstream repository resolution
  and shallow clone, for grounded-description generation. See
  decisions/0019 and decisions/0021." `decisions/0019`'s own title is
  "Grounded description replaces gap analysis for FULL-depth
  generation"; `decisions/0035`'s own title is "`sync_vendor` reads
  enrichment from the graph; `grounded_description.py` retired" and its
  own body states plainly: "`grounded_description.py` is retired —
  deleted, not just orphaned." `decisions/0061` (Accepted, unedited)
  confirms `0019` is superseded by `0035`. The module's own *real,
  current* caller (`sync.py:66,147`, via `sync_vendor`'s vendor-source-
  cloning-for-enrichment path) never cites `decisions/0019` at all —
  only `decisions/0021`, which remains live and accurate. This is a
  genuine, pre-existing, previously-unflagged placement defect: a
  module docstring presents a superseded, now-dead rationale
  ("grounded-description generation") as if it still justified the
  module's current purpose. **This finding is used to ground this
  plan's own dogfood design (§9) — it is not fixed by this planning
  task**, per this task's own explicit "do not implement" instruction;
  it is re-verified, not merely assumed, at implementation time, since
  something could change it between now and then (§9 states this
  honestly).
- Two real, independently confirmed **negative controls**, also found
  this session, not asserted on faith: `src/codecompass/oracle.py:92`'s
  own `decisions/0081` citation (`compute_tree_digest`'s docstring,
  describing `tested_subject_digest`/`test_input_digest` construction)
  is accurate and current — `decisions/0081` is `Accepted`, not
  superseded, and the citation correctly describes real, unchanged
  behaviour. `src/codecompass/staleness.py`'s four `decisions/0005`
  citations are likewise accurate and current — `decisions/0005` is
  `Accepted`, not superseded. `decisions/0085` §4 itself already names
  `oracle.py`'s own "non-obvious subprocess/digest-handling comments" as
  the project's own chosen positive-control exemplar for "extensive
  implementation comments... legitimately appropriate" — this plan
  reuses that exact file, not a substitute.
- **No existing script parses `decisions/*.md` for citation/supersession
  validity from source comments.** Confirmed by grep across `scripts/*.py`
  and `src/codecompass/*.py` for any such parsing — `check_knowledge_
  base.py::check_requirement_cites_approved_decision` checks a
  *canonical* `Decision` record (`DEC-xxx`, one of the six knowledge-
  record kinds, living under `planning/knowledge/<slug>/`), a completely
  different artifact from a `decisions/*.md` ADR file — the two share
  the English word "decision" but nothing else. This is genuinely new,
  justified machinery (§7).
- The current specialist agent roster is 13 files (`ls .claude/agents/`).
  **This plan's final design (§6.B) adds none** — the semantic/
  editorial reviewer is an ad-hoc `general-purpose` dispatch carrying a
  committed workflow-doc brief, not a 14th standing agent file; this
  was a genuine design change made during this plan's own independent
  review, not the original intent — see §6.B/§12/§13.

## 2. Preserving Phase 85's outstanding findings (retention/disposition review)

Per this task's own governing instruction, **no change is made** to
`L-114`, `L-107`, `planning/learnings/inbox.md`, `planning/learnings/
promoted.md`, or any Phase 85 record — existing records already
satisfy every requirement this task's §2 names, confirmed by direct
re-reading this session, not by assumption:

- **Discoverable, traceable, actionable**: both entries are in
  `planning/learnings/inbox.md` with full `TEMPLATE.md`-conformant
  fields (origin, date, project_revision, observation, evidence,
  classification, status, recurrence) plus a dated curation note each,
  cross-referenced to each other and to the real finding IDs they cover
  (`REQ-DOCORIGIN-001/002/003`, `REQ-HSAPI-001`-`006` for `L-114`
  category 1; `EV-BFS-002`/`EV-BFS-003` for `L-107`/`L-114` category 2).
- **Evidence, scope, severity, provenance preserved**: unedited since
  the Phase 85 corrective pass's own closeout; `L-114`'s own
  `classification: open-work`/`status: retained` and `L-107`'s own
  `status: retained` are both unchanged.
- **Resolution criterion and future-work destination recorded**:
  `L-114` names two explicit alternatives for its category 1 (a
  `context-researcher` evidence-finding dispatch, or a new, explicitly-
  named ADR exemption mirroring `decisions/0081` §3's own precedent);
  `L-107`'s own resolution path (re-citing `EV-BFS-002`/`EV-BFS-003` to
  the live-reconfirmed passing results) is unchanged and still named.
  `planning/CONTEXT.md`'s "Known standing gaps" section already carries
  both as current-state facts (added by the Phase 85 corrective pass's
  own terminal reconciliation commit).
- **No duplication, no unnecessary new backlog entries**: confirmed by
  re-reading both entries and `planning/CONTEXT.md`'s own standing-gaps
  section — nothing here needs a third entry.
- **Informational findings not escalated**: the 9 informational
  findings (5 `missing_contract`, 1 `contradiction` [the genuinely
  resolved `CL-ADPT-008`], 1 `needs-review`, 1 `possible-evidence-
  overlap`, 1 `missing-evidence` on a `status: proposed` Claim) remain
  informational — this task does not convert any of them into mandatory
  work. Each is informational for the same, already-documented reason
  it was classified that way during Phase 85 (e.g. `missing_contract`'s
  own grounding in `decisions/0081` §3's explicit deferral) — re-
  confirmed, not re-argued, this session.
- **`--strict` remains truthful**: re-ran this session (§1) — still
  exit 1, same 26 blocking findings, nothing suppressed, downgraded, or
  waived. `--strict` remains, as the Phase 85 corrective pass's own
  retro already concluded, **not currently suitable as an unconditional
  CI gate** against this corpus — unchanged conclusion, not revisited.
- **Phase-86 relevance assessed, not assumed**: neither category is
  about knowledge *placement* (where information belongs, whether
  structure is appropriate) — both are evidence-*completeness*/oracle-
  *verification-currency* concerns, squarely Phase 84/85's domain.
  Retained for their own, already-named future-work destinations; not
  absorbed into Phase 86's scope.

**Disposition summary**: no backlog or learning-record changes made or
required. `L-114` (retained, `planning/learnings/inbox.md`) and `L-107`
(retained, `planning/learnings/inbox.md`, cross-referenced from `L-114`)
remain the complete, accurate, non-duplicated record of all 26 blocking
findings' disposition; the 9 informational findings remain informational
by the same reasoning already on record. See `planning/CONTEXT.md`
"Known standing gaps" for the current-state summary a future session
would read first.

## 3. Objectives and user value

Help a coding agent or human reviewer decide, with evidence rather than
taste, **where a piece of project knowledge belongs**, and surface
concrete, previously-unflagged placement defects — a stale rationale
citation masquerading as live justification; an architecturally-
significant decision buried only in a code comment with no ADR; an
undocumented invariant a Requirement record should capture — without
turning subjective structural preference into a merge-blocking gate.
Distinct user value from Phase 85 (which asks "is this canonical
knowledge well-evidenced and non-contradictory") and Phase 83 (which
asks "does a code change still satisfy an accepted behavioural
contract"): Phase 86 asks "is this information in the right place, and
does its own citation of another artifact (an ADR, a contract, a
Requirement) still hold."

## 4. Scope and explicit non-goals

**In scope**: the Knowledge Placement Policy document (§5); a mechanical
+ behavioural validator script (§6.A); one new, narrowly-scoped,
read-only advisory reviewer agent for the semantic/editorial class
(§6.B); the three enforcement classes, precisely defined and enforced
exactly as `decisions/0085` §4 specifies (§7); one real dogfood against
a bounded, representative subsystem, demonstrating a genuine, previously
unflagged defect fixed as a direct result (§9).

**Explicit non-goals** (per the governing roadmap's own §6 "Excluded"
and this task's own §8 instruction):

- Any new mandatory verbosity/length rule.
- Treating knowledge placement as a single-location-only rule — a
  critical invariant may legitimately live in a comment, a contract,
  and documentation simultaneously with one consistent meaning; this
  phase flags *inconsistency*, never mere repetition.
- Any mechanism making an LLM/agent judgment a merge-blocking gate on
  its own say. Semantic/editorial findings are **always** advisory.
- A general-purpose code-style linter — `ruff` already exists and is
  unmodified by this phase.
- Resolving any of Phase 85's 26/9 outstanding findings (§2 above) —
  explicitly out of scope for this planning task and, on inspection,
  not Phase-86-relevant work either way.
- Implementing Phase 87 (documentation compiler), 88 (MCP), 89
  (incremental reconciliation), or 90 (comparative trials) — Phase 86
  produces reusable foundations for each (§8) without building any of
  their own functionality.
- Automatic knowledge promotion, code changes, or documentation
  rewrites from this phase's own review output alone — every
  correction (including the one dogfood fix, §9) is applied by the
  lead, reviewed exactly like any other source change, never auto-
  applied by an agent.
- A new canonical knowledge-record kind, a new write path, or a second
  competing knowledge authority — none introduced; see §8.

## 5. Knowledge Placement Policy and category mapping

Reproduced from `decisions/0085` §4 (the later, "formalised" source
`planning/v2-roadmap.md` itself points to) — **not re-derived or
re-worded**, per this task's own instruction to verify the exact eight
categories "rather than inventing a replacement taxonomy," **with one
disclosed correction, not a silent one**: row 5's artifact column
reads `planning/knowledge/<slug>/*.yaml` below; `decisions/0085` §4's
own literal text says `planning/knowledge/<slug>/*.md`. Confirmed by
direct inspection this session (`find planning/knowledge -maxdepth 2
-type f`) that every real Requirement record in this corpus is a
`.yaml` file (e.g. `planning/knowledge/doc-origin-pinned-reference/
REQ-DOCORIGIN-001.yaml`) — `.md` is a pre-existing typo in `decisions/
0085` §4 itself (ADRs are append-only and not corrected in place,
`CLAUDE.md` §2, so this is not itself fixed here). This single cell is
corrected to the real, verified extension rather than reproduced
literally wrong; every other cell is byte-for-byte unaltered — found
during this plan's own independent review, not self-identified.

| # | Category | This project's artifact |
|---|---|---|
| 1 | Implementation logic | `src/codecompass/*.py` source itself |
| 2 | Interface documentation and docstrings | module/function docstrings |
| 3 | Non-obvious local comments | inline code comments — this project's own existing comment discipline (comment only when the WHY is non-obvious, never restate the WHAT) is the placement rule for this category, not a new one |
| 4 | Architectural rationale and approved decisions | `decisions/*.md` (ADRs) |
| 5 | Behavioural requirements and invariants | `planning/knowledge/<slug>/*.yaml` Requirement records (`decisions/0085` §4 literally says `*.md` — corrected above) and `planning/contracts/<slug>/` oracle contracts |
| 6 | Verification evidence | `planning/contracts/<slug>/*.yaml` oracle-result files and `planning/knowledge/<slug>/` Evidence records |
| 7 | Human-oriented project documentation | `docs/**`, `README.md`, `ai-docs/**` (Phase 87's compiled output lands here) |
| 8 | Historical design context | `decisions/*.md` (append-only), `planning/retros/`, `architecture/historical-notes.md` where it exists |

For each category, the per-category detail this task's §4.A requires:

### 1. Implementation logic
- **Purpose/examples**: the actual behaviour of the system — a
  function body, a regex, a control-flow branch.
- **Authoritative source of truth**: itself. No other artifact can
  override what the code actually does; every other category either
  *describes*, *justifies*, or *verifies* this one.
- **Location**: `src/codecompass/*.py` (and `adapters/*.py`).
- **Relationship to canonical knowledge**: a Claim's `supporting_
  evidence` may cite a `source` or `executable`-kind Evidence pointing
  here (`Observation.method: source_read`/`code_read`/`executable`,
  Phase 85's own taxonomy); the code itself never cites a Claim back.
- **Relationship to tests/contracts/decisions**: tests exercise it;
  an oracle contract's `check_reference` may name a test that exercises
  it; a `decisions/*.md` ADR may record *why* it is shaped this way
  (category 4) but the ADR is never itself executable.
- **Relationship to intermediate knowledge/generated docs**: never
  itself intermediate or generated — it is the ground truth those
  layers describe.
- **Ownership/change procedure**: the lead, or an ad-hoc implementer
  subagent under the lead's direction, per existing write-boundary
  rules (`CLAUDE.md` §8). No specialist agent writes `src/`.
- **Conflict/duplication/misplacement identification**: this category
  is never itself "misplaced" — misplacement is a question about
  *other* categories citing or describing it incorrectly (e.g. a
  docstring, category 2, misdescribing it).

### 2. Interface documentation and docstrings
- **Purpose/examples**: what a caller needs to know to use a module/
  function correctly — parameters, return shape, side effects, the
  *current* rationale for a non-obvious interface choice.
- **Authoritative source of truth**: the real implementation (category
  1) it describes; a docstring is authoritative only insofar as it
  matches current behaviour.
- **Location**: the module/function docstring itself, in `src/
  codecompass/*.py`.
- **Relationship to canonical knowledge**: may cite a `decisions/NNNN`
  ADR (category 4) as rationale, or (rarely, today) a Requirement
  record (category 5) as the accepted obligation it implements. This
  citation is exactly what this phase's mechanical check (§6.A)
  verifies for existence and currency.
- **Relationship to tests/contracts/decisions**: should remain
  consistent with any ADR it cites and any contract-backed behaviour it
  describes; this phase's behavioural check (§6.A) is the mechanism
  that can catch a drift between the two, where evidence exists.
- **Relationship to intermediate/generated docs**: a legitimate
  *source* for Phase 87's documentation compiler to draw from, never
  itself compiled output.
- **Ownership/change procedure**: the lead/implementer, same as
  category 1 — a docstring is part of the source file.
- **Conflict/duplication/misplacement identification**: **this is this
  phase's own primary target.** A docstring citing a superseded,
  no-longer-applicable ADR as if it were still live current-state
  justification (the real `source_resolution.py` instance, §1/§9) is
  exactly this category's own characteristic defect — information that
  belongs in category 8 (historical design context) being presented as
  if it were still category 2 (current interface rationale).

### 3. Non-obvious local comments
- **Purpose/examples**: a hidden constraint, a subtle invariant, a
  workaround for a specific bug, behaviour that would surprise a reader
  — never a restatement of what well-named code already says
  (`CLAUDE.md`'s own, pre-existing, unchanged comment discipline).
- **Authoritative source of truth**: same as category 2 — the real
  implementation it annotates.
- **Location**: inline comments in `src/codecompass/*.py`.
- **Relationship to canonical knowledge**: same citation pattern as
  category 2, at finer grain (one `decisions/NNNN` reference per
  comment, not per module).
- **Relationship to tests/contracts/decisions**: same as category 2.
- **Relationship to intermediate/generated docs**: not itself a
  documentation source Phase 87 compiles from (too fine-grained/
  implementation-specific) — stays in `src/`.
- **Ownership/change procedure**: same as category 1/2.
- **Conflict/duplication/misplacement identification**: an
  *architecturally significant* rationale (the kind that should survive
  a rewrite of the function it's attached to) living *only* in an
  inline comment, never promoted to a `decisions/*.md` ADR, is this
  category's own characteristic misplacement — flagged as semantic/
  editorial (§6.B), since "architecturally significant" is a judgment
  call, never mechanically provable from the comment's text alone.

### 4. Architectural rationale and approved decisions
- **Purpose/examples**: *why* a non-obvious, cross-cutting choice was
  made — the kind of content an ADR exists for.
- **Authoritative source of truth**: itself, once `Accepted` — `CLAUDE.md`
  §2's append-only convention means an ADR's own original text is never
  edited; a later, superseding ADR is a *new* numbered file.
- **Location**: `decisions/NNNN-slug.md`.
- **Relationship to canonical knowledge**: a Requirement record's own
  `decision:` field cites a *canonical* `DEC-xxx` record (a different
  thing — see §1's clarification), never a `decisions/*.md` ADR number
  directly; the two "decision" concepts are structurally distinct and
  this phase does not conflate them.
- **Relationship to code/tests/contracts**: code (categories 1-3) may
  cite an ADR as rationale; the ADR itself never cites code by line
  number (too fragile) — only by module/concept name, consistent with
  existing practice.
- **Relationship to intermediate/generated docs**: `docs/decisions.md`
  (an existing, already-committed, mechanically-derived title+status
  index) is a legitimate *projection* of this category, not a
  duplicate authority — it already discloses its own known limitation
  (§1) honestly rather than silently.
- **Ownership/change procedure**: the lead only, via the ADR process
  (`CLAUDE.md` §2) — no specialist agent writes `decisions/*.md`.
- **Conflict/duplication/misplacement identification**: this phase's
  mechanical check (§6.A) — a citation to a non-existent ADR number
  (blocking, mechanical); a citation to a *superseded* ADR, unflagged
  as such (informational, mechanical fact; whether it is *misleading in
  context* is semantic/editorial, §6.B).

### 5. Behavioural requirements and invariants
- **Purpose/examples**: an accepted, testable obligation — "the system
  must do X under condition Y."
- **Authoritative source of truth**: the Requirement record itself,
  once `approved`/`implemented`/`verified` (Phase 81's own canonical
  status enum, unchanged).
- **Location**: `planning/knowledge/<slug>/REQ-*.yaml`; the matching
  oracle contract (if any) at `planning/contracts/<slug>/oracle-
  contract.yaml`.
- **Relationship to canonical knowledge**: this *is* canonical
  knowledge — one of the six existing record kinds (Phase 81),
  unchanged by this phase.
- **Relationship to code/tests/contracts**: a contract's own `checks:`
  collection (Phase 82) names the test/execution path that verifies it;
  code implements it; this phase never re-implements or duplicates
  that verification — it only checks whether a *comment* claiming
  behaviour is consistent with what an existing Requirement/contract
  already says, via Phase 84's read-only API.
- **Relationship to intermediate/generated docs**: Phase 87's
  documentation compiler draws human-readable prose from this category
  (and category 6) without this phase needing to do anything new —
  Phase 86 only needs the category→artifact mapping to exist, which
  this table already is.
- **Ownership/change procedure**: `context-researcher` proposes
  (`status: proposed`); the lead decides/approves; unchanged by this
  phase.
- **Conflict/duplication/misplacement identification**: an
  architecturally significant invariant that exists only as prose in a
  code comment, with no Requirement record at all, is this category's
  own characteristic *absence* — flagged as semantic/editorial (whether
  something rises to "should be a Requirement" is a judgment call), and
  explicitly **never auto-promoted** into a real Requirement by this
  phase's own machinery (§4 non-goals) — only ever a recommendation for
  the lead/`context-researcher` to act on through the existing,
  unchanged approval path.

### 6. Verification evidence
- **Purpose/examples**: a real, reproducible confirmation (or
  disconfirmation) that a Requirement/Claim holds against the actual
  implementation.
- **Authoritative source of truth**: the oracle-result file / Evidence
  record itself, scoped by `tested_subject_digest`/content hash (Phase
  82).
- **Location**: `planning/contracts/<slug>/results/*.yaml`; `planning/
  knowledge/<slug>/EV-*.yaml`.
- **Relationship to canonical knowledge**: this *is* canonical
  knowledge (Evidence, one of the six kinds) — unchanged.
- **Relationship to code/tests/contracts**: produced by actually
  running a contract's named check against the real implementation
  (Phase 82/83's own, unmodified machinery).
- **Relationship to intermediate/generated docs**: a legitimate source
  for Phase 87's compiler ("this behaviour is independently verified,"
  not merely asserted); never itself generated from docs.
- **Ownership/change procedure**: produced by running the oracle
  (`run_balance_from_spec_oracle.py` or equivalent); cited by
  `knowledge-curator`/`context-researcher` into an Evidence record;
  unchanged by this phase.
- **Conflict/duplication/misplacement identification**: a docstring
  (category 2) asserting a behaviour a *real, current* oracle result
  contradicts is this category's own characteristic conflict — this
  phase's **behavioural** enforcement class (§6.A, §7) exists
  specifically for this, reusing Phase 84's `trace_evidence`/
  `epistemic_status` unchanged, never re-deriving oracle logic.

### 7. Human-oriented project documentation
- **Purpose/examples**: `docs/getting-started.md`, `README.md`,
  `ai-docs/README.md` — material written for a human or an orienting
  agent to read directly.
- **Authoritative source of truth**: the real, current implementation
  it describes (categories 1-2) and, for behaviour claims, categories
  5-6 — a doc page is never itself authoritative over what the system
  does.
- **Location**: `docs/**`, `README.md`, `ai-docs/**`.
- **Relationship to canonical knowledge**: a legitimate *consumer*/
  projection of canonical knowledge (Phase 81's own existing
  "projection, not a second source of truth" principle); `docs-
  maintainer`'s existing, unchanged write boundary.
- **Relationship to code/tests/contracts**: reconciled against VERIFIED
  implementation by the existing `docs-maintainer` role and the
  per-phase `docs-reconstructor` drift audit — both unchanged by this
  phase.
- **Relationship to intermediate/generated docs**: this *is* the
  landing zone for Phase 87's own compiled output, once Phase 87
  exists — this phase does not build that pipeline, only confirms the
  category→location mapping Phase 87 will need.
- **Ownership/change procedure**: `docs-maintainer` (incremental) /
  `docs-reconstructor` (audit, never repairs) — unchanged.
- **Conflict/duplication/misplacement identification**: already
  Phase 85/84/83's own per-phase drift-audit discipline, unmodified;
  this phase adds no new mechanism here — it is named in the table for
  completeness of the eight-category mapping, not because this phase
  changes how it is enforced.

### 8. Historical design context
- **Purpose/examples**: *why something used to be true, and what
  changed* — a superseded ADR's own original text (never edited,
  `CLAUDE.md` §2), a phase retro, a dated corrective note.
- **Authoritative source of truth**: itself, as a historical record —
  never current-state justification once superseded. The distinction
  between "this is why we did X, and it's still why" (category 4) and
  "this is why we used to do X, before Y changed it" (category 8) is
  exactly what this phase's mechanical+semantic check pair (§6)
  exists to police.
- **Location**: `decisions/*.md` (the superseded ADR's own, unedited
  text), `planning/retros/**`, `architecture/historical-notes.md`
  where it exists (confirmed, this session: no such file currently
  exists in this checkout — the category is named for completeness per
  `decisions/0085` §4's own table, not because this phase creates it).
- **Relationship to canonical knowledge**: a superseded Claim
  (`status: superseded`) is this category's canonical-knowledge analog
  — Phase 85's corrective pass already established the precise
  "historical, not active" severity treatment for exactly this
  distinction (`knowledge_intermediate.derive_provenance_label`'s own
  `"superseded" -> "HISTORICAL"` classification), reused, not
  re-derived, by this phase's own design (§6.A).
- **Relationship to code/tests/contracts**: a comment/docstring
  *legitimately* citing superseded context ("this used to work
  differently, see `decisions/0019`, superseded by `0035`") is
  correctly placed; the same citation presented as if it still
  justified *current* behaviour is misplaced into category 2 instead.
- **Relationship to intermediate/generated docs**: never itself
  compiled into human-facing docs as current-state fact; a retro may be
  *referenced* by a doc as historical context, never presented as
  current.
- **Ownership/change procedure**: append-only, by construction
  (`CLAUDE.md` §2) — no agent edits a past ADR's original content; a
  new, superseding ADR is the lead's own, separate act.
- **Conflict/duplication/misplacement identification**: this phase's
  own §6.A mechanical `decision-citation-superseded` check plus the
  §6.B reviewer's semantic/editorial judgment of *whether a given
  citation's own surrounding prose still reads as current-state
  justification* — exactly the real `source_resolution.py` case (§1).

**Explicitly avoiding a second competing knowledge system**: this
policy introduces **no new record kind, no new storage location, and
no new write path**. Every category maps onto an artifact that already
exists and is already owned by an existing role; this phase's own new
artifacts (§10) are the policy document itself, a validator script, and
one advisory-only agent report — never a parallel ledger of "where
things should go" that could drift from the real `src/`/`decisions/`/
`planning/` layout it describes.

## 6. Proposed reviewer workflow, interfaces and ownership

### 6.A Mechanical and behavioural checks — `scripts/check_knowledge_placement.py` (new)

A new, maintainer-only, on-demand script, mirroring `scripts/check_
self_knowledge_quality.py`'s own exact `Finding(rule, message, strict)`
convention, CLI shape (`--strict`, `--ledgerkit-root`), and report-only-
by-default posture. **Composes** `knowledge_api`/`knowledge_
intermediate`/`oracle` unchanged; adds no logic already present there.
Not a `codecompass` subcommand, like its siblings.

**Checks** (mechanical unless noted):

1. `decision-citation-exists` — every `decisions/[0-9]{4}` substring
   found in a `src/codecompass/**/*.py` docstring or comment must
   resolve to a real file under `decisions/`. **Blocking.** Purely
   mechanical: deterministic regex extraction + filesystem existence
   check, no judgment involved.
2. `decision-citation-superseded` — for every citation that does
   resolve, if some *other*, real ADR file's own title or body text
   matches a `superseded by|is superseded` pattern naming the cited
   ADR's number, report it. **Informational, never blocking** — citing
   a superseded ADR for legitimate historical context (category 8) is
   explicitly correct, not a defect in itself; this check's own job is
   only to make every such citation *visible* for the semantic/
   editorial reviewer (§6.B) to judge in context, exactly mirroring
   this project's own `missing_contract`-always-informational
   precedent (Phase 85) for a mechanical fact that is not, by itself,
   proof of a defect.
3. `decision-citation-status-mismatch` — for every citation, if the
   comment's own text makes an *explicit*, parseable status assertion
   about the cited ADR (e.g. a parenthetical like `decisions/0057
   (rejected)`) that contradicts the ADR's real first-line `## Status`
   field, report it. **Blocking** — this is fully mechanical only
   because it is scoped to an explicit, literal textual assertion, never
   an inferred one. **Disclosed honestly, not manufactured**: a
   corpus-wide grep this session found no real source comment using
   this bracketed-status-assertion convention today — this check is
   designed and tested (§11) against constructed fixtures, and may
   report zero real findings against the current corpus. This mirrors
   Phase 83's own `overlapping-account-patterns-no-double-count` check
   and Phase 86's own §6.A point 4 below — a correctly-designed check
   with a currently-thin real trigger surface is not a design defect.
4. `docstring-contradicted-by-oracle-result` (**behavioural**) — for
   any module/function docstring that names a specific `check_id` from
   a real oracle contract (a citation convention this check recognises,
   not invents — e.g. `` `check_id: <name>` ``-shaped text), cross-
   reference via `knowledge_api.trace_evidence`/`epistemic_status`
   (Phase 84, unchanged) for a currently-passing result. If the only
   currently-passing result for that `check_id` is `FAIL`/`INVALID`
   against the live implementation, report it. **Blocking only on real,
   live-reconfirmed evidence, never on assertion** — identical severity
   discipline to Phase 84/85's own `stale_test_citation`/`unverified_
   required_scope`. **Disclosed honestly**: the real corpus has one
   contract (`balance-from-spec`); no source docstring currently uses
   this citation convention, so this check, too, is designed/tested
   against fixtures and may report zero real findings today — it exists
   so the moment a second contract-backed module exists, this
   enforcement path is already live, not added retroactively.

None of these four checks duplicate `check_self_knowledge_quality.py`'s
own five checks — confirmed by re-reading that script in full this
session: it has no `decisions/*.md` parsing of any kind.

### 6.B Semantic/editorial review — `docs/workflows/knowledge-placement-review.md` (new workflow brief) dispatched ad hoc, **no new standing agent**

**Revised during this plan's own independent review.** The original
draft of this section proposed a 14th standing specialist agent,
`.claude/agents/knowledge-placement-reviewer.md`, arguing from
independence alone (separation of *context*, so the review is not
biased by the lead's own editing state — exactly the property
`release-phase-auditor`/`docs-reconstructor`/`domain-skeptic` already
share, per `planning/v1-redefinition/agent-led-development.md` §1's
"independent means independent" principle). The independent review
correctly identified that this argues for **a separate, independent
dispatch**, not specifically for **a permanent roster file** — those
are two different questions the original draft conflated. Both
properties this capability actually needs — independence, and a
stable, precisely-repeatable charter — are already satisfiable by this
project's own existing, documented pattern, applied here as the
*primary* mechanism rather than as a one-session fallback: a
`general-purpose` subagent, dispatched fresh each time, carrying
`docs/workflows/knowledge-placement-review.md`'s own full text inline
as its brief. This is the identical substitution `planning/v1-
redefinition/agent-led-development.md` §2.14 already documents for
`implementation-reconstructor` (`L-023`: "a `general-purpose` dispatch
carrying this role's own full charter inline substitutes for a true
[name]-typed one") — there, it is a disclosed workaround for a same-
session naming limitation; here, it is adopted as the considered,
permanent design, because §2.15's own stated principle ("a standing
role adds nothing" where the capability is "an activity within a
phase, not a separation of authority") applies more cleanly to this
capability than to `release-phase-auditor`/`docs-reconstructor`, both
of which are dispatched as a mandatory step of *every single phase's*
own DoD (`CLAUDE.md` §5) — a reuse frequency this capability does not
yet have. Per `decisions/0081` §3's own repeated pattern in this
project ("a future phase may choose to require X project-wide once
real use justifies that cost... not pre-committed here"), **this
plan deliberately does not pre-commit to a standing file**: if a later
phase (most plausibly Phase 89's own change-driven reconciliation
trigger, §8) ends up dispatching this review routinely enough that
brief-drift between dispatches becomes a real, observed risk —
evidence, not assumption — promoting `docs/workflows/knowledge-
placement-review.md`'s content into a genuine `.claude/agents/*.md`
roster entry at that point is a small, mechanical, low-risk change
(copy the brief verbatim into the standard frontmatter shape; add one
roster-table row) that does not require revisiting any of this plan's
own §5-§9 design. `domain-skeptic` remains considered and rejected as
an alternative *host* for this capability regardless of which
dispatch mechanism is chosen: its own charter (`.claude/agents/
domain-skeptic.md`) is explicitly and narrowly scoped to a domain-
corpus draft or `design.md`, plus its Phase-79 snapshot-vs-as-built
comparison mode — general source-tree comment/docstring placement
review is a materially different question from "does this *domain*
claim have a citable Observation/Evidence record," and stretching its
charter to cover both would blur, not sharpen, its own existing
separation of responsibility.

**Brief** (the full text of `docs/workflows/knowledge-placement-
review.md`, §10 — this is the document pasted inline as the dispatch
prompt every time this review runs, exactly as a `.claude/agents/*.md`
frontmatter body would be loaded automatically for a named agent;
summarised here per this task's §4.B structure):

- **Question**: given a bounded target (one file, a small named set of
  files, or a real diff), which knowledge items in it are placed
  correctly per §5's policy, and which are not — distinguishing a
  genuine, evidence-backed placement defect from a legitimate
  multi-location invariant or a subjective structural preference?
- **Method**: for each knowledge-bearing unit (docstring, comment,
  structural choice) in the target: (1) classify it into one of the
  eight categories; (2) for any `decision-citation-superseded`
  informational finding `check_knowledge_placement.py` already
  surfaced for this target, independently judge — using the real,
  current callers/behaviour as contradicting or confirming evidence,
  exactly as this plan's own §1/§9 dogfood example does — whether the
  citation's surrounding prose still reads as live, current-state
  justification (misplaced: category 8 content presented as category
  2) or as legitimate historical framing (correctly placed); (3)
  separately scan for the roadmap's own named defect patterns: an
  architecturally significant invariant/rationale that exists only in
  a comment with no `decisions/*.md` ADR or Requirement record; an
  unnecessary abstraction; missing interface documentation. **Never
  re-derives a mechanical fact by eye** — a citation's existence or
  supersession status is always taken from the script's own output,
  never independently re-judged from raw text.
- **Finding shape** (every recommendation, per this task's §4.B list):
  artifact + exact location (`file:line`, quoted text); independently
  checkable evidence (the script's own mechanical finding it builds
  on, where one exists, or the specific contradicting real-callsite/
  real-behaviour evidence it found itself); the applicable policy
  category + enforcement class; whether mechanically established or
  judgment-based (explicit, never ambiguous); recommended correction +
  rationale; potential consequences/trade-offs of both fixing and not
  fixing.
- **Distinguishing a genuine defect from subjective preference**
  (this task's own explicit §4.B requirement): a finding is only ever
  escalated as *mechanical* or *behavioural* when it rests on a
  citable, reproducible fact the script itself already computed —
  never on the reviewer's own say-so. A finding resting on taste
  (verbosity, abstraction elegance, naming style) is **always**
  semantic/editorial, explicitly labelled as such in the report, and
  **never** phrased using defect language ("bug", "wrong") — phrased
  as "worth considering," with the trade-off of leaving it as-is
  stated plainly. The reviewer's own report must, for every finding,
  answer one explicit question: *"would a second, independent reader,
  given only this artifact and the cited policy category, reach the
  same conclusion without relying on stylistic preference?"* — a
  finding that fails this test is downgraded to semantic/editorial (or
  dropped) even if the reviewer's first instinct was stronger.
- **Write boundary** (instructed explicitly in the dispatch prompt,
  enforced by the lead's own review of the returned report rather than
  by a tool-level restriction, since a `general-purpose` dispatch has
  no bespoke `tools:` scoping of its own): its own review report only.
  Never edits `src/`, `decisions/*.md`, any canonical knowledge record,
  or any other agent's own write-boundary file. Never promotes a
  comment's own content into a Requirement/Claim itself — any such
  escalation is a recommendation for the lead/`context-researcher` to
  act on through the existing, unmodified approval path (§5, category
  5). The lead confirms, after each dispatch, that nothing outside the
  review report itself was touched (`git status`/`git diff`) — the
  same discipline already applied after every subagent dispatch in
  this project, not a new control invented for this one.
- **Dispatch instructions, carried in the brief itself** (since this
  is not a standing agent with its own `tools:` frontmatter, the
  dispatch prompt must say explicitly): read-only toward `src/`,
  `decisions/*.md`, `planning/knowledge/**`, and `planning/contracts/
  **; no `sync --yes`, no `enrich apply`; write nothing but the review
  report text returned in the dispatch's own final message (or, if the
  target is large enough to warrant a file, one report file named
  explicitly in the dispatch prompt — never an open-ended write grant).
- **Hard rule, carried in the brief itself** (drafted to already
  include the Phase 85 corrective pass's own `L-115` lesson from day
  one, not retrofitted later): if this dispatch ever materializes a
  prior git revision into a live, tracked working-tree path for its
  own before/after comparison, it must restore that path and confirm a
  clean diff before returning its report, or use a disposable scratch
  copy instead — verbatim reuse of the same rule just added to
  `release-phase-auditor.md`'s own "Hard rules".
- **Active in**: an explicit lead dispatch (`general-purpose` subagent
  type, `docs/workflows/knowledge-placement-review.md`'s full text
  pasted as the prompt) against a named, bounded target — never run
  unscoped against the whole repository in one pass (cost/focus
  reasons, and because a bounded target is what makes independent
  audit of its own output tractable, §11). Each dispatch is independent
  of every other — no session memory of a prior review carries forward
  implicitly; anything that should persist across dispatches (an
  accepted finding, a correction made) is captured in a committed
  artifact (the fix itself, a learning entry), never in agent memory.

## 7. Enforcement and independent-verification rules

Reproduced and applied precisely per `decisions/0085` §4 (not
re-interpreted):

- **Mechanical** — objective, deterministic, independently reproducible.
  `decision-citation-exists` and `decision-citation-status-mismatch`
  (§6.A) are this phase's two mechanical checks; both **may block**
  under `--strict`, exactly where the policy explicitly requires (a
  citation must resolve; an explicit status assertion must be
  accurate) — never more broadly.
- **Behavioural** — a violation demonstrated through an accepted
  executable contract or independently verifiable evidence.
  `docstring-contradicted-by-oracle-result` (§6.A) is this phase's one
  behavioural check; blocks only on a real, live-reconfirmed
  contradiction, never on an assertion alone — identical discipline to
  every oracle-backed check this project already has.
- **Semantic/editorial** — AI-assisted judgment of verbosity,
  abstraction quality, placement appropriateness, architectural
  consistency. **Always advisory.** The ad-hoc reviewer dispatch's own
  output (§6.B) is entirely in this class by construction,
  with one explicit exception matching `decisions/0085` §4's own
  stated escalation path: if a specific semantic/editorial finding is
  subsequently converted into an independently testable Requirement
  (the lead's own, separate, existing-process act — category 5, §5),
  *that resulting Requirement* becomes enforceable through the
  existing behavioural path, not through this phase's own reviewer
  gaining new authority.
- **`decision-citation-superseded` (§6.A point 2) is deliberately
  informational, never mechanical-blocking**, precisely because
  whether a given superseded-citation instance is a genuine defect or
  legitimate historical framing is a semantic/editorial question —
  **a prose contradiction with an accepted ADR is never classified
  mechanically proven merely because an agent judges it
  contradictory**, this task's own explicit, unmodified constraint.
- **No blind merge blocking on subjective judgment**: `--strict`'s own
  exit code, for this script, is a function of exactly the two
  mechanical checks and the one behavioural check — never of anything
  the ad-hoc reviewer dispatch concludes. Its report is a
  recommendation artifact, read by the lead, exactly like `release-
  phase-auditor`'s own report is read, never a gate the lead's own
  commit/merge is mechanically blocked on.
- **No circular self-assessment**: the reviewer never assesses code or
  comments the lead wrote *in the same dispatch* that wrote them — it
  is always a separate, later, independent dispatch against already-
  committed (or at minimum already-written-and-reviewable) content,
  matching `release-phase-auditor`'s own established independence
  posture.

## 8. Reuse of existing components (explicit, per phase)

- **Phase 81** (canonical/intermediate knowledge model): zero new
  record kinds; categories 5-6 of §5's table map directly onto the
  existing Requirement/Evidence kinds, unchanged. `knowledge_
  intermediate.parse_record`/`load_slug_records` reused unmodified by
  §6.A's behavioural check's own evidence-resolution path (via Phase
  84's API, never re-implemented).
- **Phase 82** (contract and evidence foundation): `oracle.
  parse_oracle_result`/the `Finding(rule, message, strict)` pattern
  reused unmodified; §6.A's behavioural check never re-implements
  outcome precedence or digest logic.
- **Phase 83** (semantic change assurance): the `Finding`-with-`strict`-
  flag convention `decisions/0082`/`0083` hardened in `check_contracts.
  py`/`check_knowledge_base.py` reused identically; `assess_change_
  impact.py`'s own established pattern of composing Phase 84's API
  rather than hand-rolling fresh graph-walking logic is this phase's
  own explicit model for §6.A. **Not a functional dependency** — Phase
  86's own one stated prerequisite (`decisions/0084` §2) is Phase 85
  only.
- **Phase 84** (read-only knowledge API): `trace_evidence`/
  `epistemic_status`/`find_gaps` reused unchanged by §6.A's behavioural
  check and by the reviewer's own evidence-gathering in §6.B; no new
  write path, no bypass of the existing read-only contract.
- **Phase 85** (self-curation lifecycle and knowledge-quality
  validator): `scripts/check_self_knowledge_quality.py`'s own exact
  `Finding`/CLI/report conventions reused verbatim by §6.A's new
  script — explicit continuity, not reinvention. **Phase 85's five-
  outcome candidate-disposition procedure and investigation log are
  deliberately NOT reused** — Phase 86 is not about discovering new
  *canonical* knowledge (a Claim/Evidence pair), it is about *placement*
  of knowledge that already exists in some form; no investigation log
  is needed, consistent with this plan's own non-goal (§4) of no
  automatic knowledge promotion from this phase's review output.

**Foundations this phase creates for later phases, without implementing
their own functionality** (this task's own §4.D requirement):

- **Phase 87** (knowledge-compiled documentation): §5's category→
  artifact mapping is exactly the input Phase 87's compiler needs to
  decide which categories compile into `docs/**` (category 7) versus
  stay elsewhere (categories 1-6, 8) — Phase 86 produces this mapping
  as a committed, reusable document; Phase 87 consumes it, never
  re-derives it.
- **Phase 88** (Agent Integration and MCP): the `Finding` shape this
  phase's script and agent both produce (artifact, evidence, policy
  category, enforcement class, severity) is already the same shape
  Phase 84's API returns — exposable later via MCP's own read surface
  with no redesign.
- **Phase 89** (Incremental Knowledge and Documentation Reconciliation):
  §6.A's mechanical script already supports running against "a real
  diff or a real slice of the codebase" (this task's own §4.B wording,
  honoured by design — the script takes a file-set parameter, not only
  "the whole repository"); Phase 89 only needs to wire a change-driven
  trigger onto an already-diff-capable check, not redesign it.
- **Phase 90** (Comparative Development Trials): this phase's own
  real-corpus baseline finding count (§11) gives a concrete, pre-
  existing "before" measurement a comparative trial could cite without
  Phase 90 needing to construct one from scratch.

**Phase 86 is independently deliverable without implementing any of
87-90's own functionality** — confirmed: nothing in §6-§9 below writes
a documentation compiler, an MCP surface, a change-driven trigger, or a
trial harness.

## 9. Real dogfood design

**Bounded, representative subsystem** (chosen, not the whole `src/
codecompass/` tree, per this task's own §5 instruction to select a
*bounded* subsystem): three files, already directly inspected this
session (§1) —

- `src/codecompass/source_resolution.py` — the file independently
  confirmed, this session, to contain one real, previously-unflagged
  placement defect (its own module docstring cites `decisions/0019`,
  superseded by `decisions/0035` per `decisions/0061`, as if still
  live justification for "grounded-description generation," a feature
  `decisions/0035` explicitly retired; the module's real current
  caller, `sync.py`'s `sync_vendor` path, never cites `decisions/0019`
  at all).
- `src/codecompass/oracle.py` — `decisions/0085` §4's own named
  positive-control exemplar ("extensive implementation comments... are
  legitimately appropriate"); its `decisions/0081` citation (line 92)
  confirmed live and accurate this session.
- `src/codecompass/staleness.py` — an ordinary module with four
  `decisions/0005` citations, confirmed live and accurate this session,
  serving as the second, "ordinary comment" negative control this
  task's own §4.B/`decisions/0085` §4 both require.

**Honesty clause** (this task's own explicit instruction: "do not
predetermine findings or manufacture a defect... if no genuine defect
is discovered, require an honest outcome"): the `source_resolution.py`
finding above is real and independently confirmed *as of this planning
session* (`b434b9d`). **It is re-verified, not assumed, at
implementation time** — if some other work has already touched that
docstring by then, the implementation phase's own first step is to
re-scan `src/codecompass/` with the new mechanical check (§6.A point 2)
for a currently-real instance before proceeding with this exact
example, and to report honestly if none currently exists rather than
constructing one. The acceptance gate (below) is written against
"a genuine, currently-real instance," not against this specific file
by name, for exactly this reason — though this file remains the
expected, most-likely case.

**Trial steps**:

1. Run `scripts/check_knowledge_placement.py` against the three-file
   bounded set. Expect: `decision-citation-superseded` (informational)
   on `source_resolution.py`'s `decisions/0019` citation; zero mechanical
   findings on `oracle.py`/`staleness.py`.
2. Dispatch a `general-purpose` subagent, carrying `docs/workflows/
   knowledge-placement-review.md`'s full text as its brief (§6.B),
   against the same bounded set, given the script's own output as
   input evidence.
3. Independently audit the dispatch's own report (`release-phase-
   auditor`, read-only, per this project's own established pattern for
   judging an agent's output rather than trusting its self-report).

**Acceptance criteria** (mirroring `decisions/0084`/`0085`'s own named
Phase 86 test requirements exactly):

1. The mechanical script correctly reports the real `decision-
   citation-superseded` informational finding on whichever file
   currently carries it (expected: `source_resolution.py`) — a true
   positive, mechanically reproducible by anyone re-running the exact
   command.
2. The reviewer independently judges that finding as a genuine,
   actionable placement defect (not merely restating "superseded" —
   explaining *why* it is misleading in context, citing the real
   current caller as contradicting evidence), correctly classified
   **interface documentation (category 2) misplaced as historical
   design context (category 8)** — not merely flagged, but correctly
   *categorised*.
3. The reviewer correctly **declines** to flag `oracle.py`'s own
   extensive subprocess/digest-handling comments (negative control 1,
   the named exemplar) as a verbosity/placement problem.
4. The reviewer correctly **declines** to flag `staleness.py`'s
   ordinary `decisions/0005` citations (negative control 2).
5. Neither the script's own `--strict` exit code nor any other
   mechanism treats the `source_resolution.py` finding as blocking —
   it remains advisory/informational throughout, exactly as `decisions/
   0085` §4 requires, **until and unless it is actually fixed** (the
   dogfood's own required correction — this task's own §5 point 2 and
   the roadmap's own exit gate both require *at least one real defect
   found and corrected*, so the implementation phase does fix the
   docstring itself, as an ordinary source edit by the lead, not an
   auto-applied agent action).
6. No finding from this phase duplicates anything `check_self_
   knowledge_quality.py` already reports — confirmed in §6.A, re-
   confirmed at implementation time by running both scripts and
   diffing their rule names.
7. If step 1 finds no currently-real instance (the honesty clause
   above), the dogfood instead demonstrates the full pipeline (steps
   1-3) against a **deliberately constructed** fixture pair — one real
   defect shape, one of each negative control — with the real-corpus
   run still performed and its honest "zero real findings currently"
   outcome disclosed, never silently substituted for without
   disclosure.

## 10. Exact deliverables and expected files

| File | Status | Purpose |
|---|---|---|
| `docs/concepts/knowledge-placement-policy.md` | new | §5's full policy, in the established `docs/concepts/` style (alongside `knowledge-model.md`) |
| `docs/workflows/knowledge-placement-review.md` | new | **the full ad-hoc reviewer brief** (§6.B) — dispatched inline via a `general-purpose` subagent each time this review runs, not a `.claude/agents/*.md` frontmatter body; mirrors `docs/workflows/self-curation-loop.md`'s own precedent in style, not in hosting mechanism |
| `scripts/check_knowledge_placement.py` | new | §6.A's four checks |
| `tests/test_check_knowledge_placement.py` | new | §11 |
| `src/codecompass/source_resolution.py` (or the currently-real equivalent, §9's honesty clause) | amended | the one real dogfood fix |
| `decisions/00NN-knowledge-placement-policy-and-review.md` | new | the ADR recording this phase's own design choices, per `CLAUDE.md` §2 ("write a new ADR whenever a phase involves a non-obvious tradeoff") — the ad-hoc-dispatch-not-a-new-standing-agent choice (§6.B/§12) alone warrants one |
| `CHANGELOG.md`, `planning/ROADMAP.md`, `planning/CONTEXT.md` | amended, at implementation closeout only | per `CLAUDE.md` §3/§5, not touched by this planning commit beyond adding Phase 86's own `planned` row (this commit) |

## 11. Tests, negative controls, and acceptance gates

- `tests/test_check_knowledge_placement.py`, mirroring `tests/test_
  check_self_knowledge_quality.py`'s own structure and determinism
  test:
  - `decision-citation-exists`: a fixture citing a real, existing
    `decisions/NNNN` (unflagged) and a fixture citing a non-existent
    one (blocking finding).
  - **Fail-closed minimal-content edge case** (`CLAUDE.md` §1,
    L-070/L-075, required for every validation mechanism this project
    adds): an empty `src/` tree (no findings, no crash); a comment
    containing the bare substring `"decisions/"` with no following
    digits (must not false-positive as a citation); a comment citing
    `decisions/0000` (a well-formed-looking but non-existent number —
    confirms the *depth* of the existence check, not merely that *some*
    check ran, per L-075's own depth-vs-scope distinction).
  - `decision-citation-superseded`: a fixture ADR pair (one superseded-
    by-title, one not) with a `src/`-fixture citation to each —
    confirms the informational, never-blocking severity.
  - `decision-citation-status-mismatch`: a constructed fixture with an
    explicit, literal status assertion contradicting the cited ADR's
    real status (blocking) and one where the assertion matches
    (unflagged) — since §1 confirms no real instance exists today,
    this is fixture-only, disclosed honestly in the test module's own
    docstring (matching `check_self_knowledge_quality.py`'s own
    precedent of disclosing when a test deliberately does not assert
    zero real-corpus findings).
  - `docstring-contradicted-by-oracle-result`: a constructed fixture
    with a real contract + a docstring citing its `check_id` + a
    result file that `FAIL`s, confirming the blocking behavioural
    path; a second fixture where the only result `PASS`es, confirming
    it stays silent; `repo_root` threading confirmed exactly like
    `check_self_knowledge_quality.py`'s own `--ledgerkit-root` tests.
  - Determinism: two consecutive runs, byte-identical output.
  - **Real-corpus run, not asserting zero findings** (same disclosed
    posture as `check_self_knowledge_quality.py`'s own test suite) —
    pins the specific real finding(s) present at implementation time
    by name, or honestly records their absence (§9's honesty clause).
- **Independent audit** (this task's §7 requirement, applied at
  implementation time, not during this planning task): `release-phase-
  auditor` re-runs `scripts/check_knowledge_placement.py` and its test
  suite independently; separately reviews the ad-hoc reviewer
  dispatch's own dogfood report transcript against the five acceptance
  criteria in §9, the same way Phase 85's own dogfood adjudication
  evidence was independently reviewed rather than merely trusted.
- **No circular self-assessment**: `release-phase-auditor` never wrote
  any of the content it audits here; the ad-hoc reviewer dispatch
  never reviews content from the same dispatch that wrote it (§7).

## 12. Risks, trade-offs, and failure handling

- **Scope creep into a general code-style linter** — explicitly
  excluded (§4); `ruff` already covers deterministic style/quality and
  is unmodified by this phase.
- **Subjective LLM judgment mistaken for an objective gate** —
  mitigated structurally: `--strict`'s own exit code is a pure function
  of the two mechanical checks + the one behavioural check; the
  reviewer's own output can never affect it (§7).
- **A legitimate multi-location invariant mistaken for duplication** —
  mitigated by §4/§5's explicit "not single-location" clarification,
  stated in both the policy document and the reviewer's own brief, not
  only in this plan.
- **Roster growth avoided, not merely minimised** — the design settled
  on in §6.B (ad-hoc `general-purpose` dispatch, `docs/workflows/
  knowledge-placement-review.md` as the inline brief) adds **zero**
  new `.claude/agents/*.md` files, resolving what the plan's own first
  draft had flagged as its most consequential open risk. The
  independent planning review scrutinized this choice directly and
  found the original draft's "new agent" argument (independence alone)
  did not, by itself, justify a *standing* file over an ad-hoc
  dispatch — both achieve the same independence property; the project's
  own `L-023` precedent (`implementation-reconstructor`, §2.14) already
  establishes the substitution mechanism this plan now adopts as
  primary rather than as a fallback. Residual risk, honestly disclosed:
  a brief pasted inline on every dispatch carries a theoretical
  consistency risk a loaded-by-the-harness agent file would not — the
  mitigation is dispatching from the one committed file (`docs/
  workflows/knowledge-placement-review.md`) verbatim each time, never
  retyped or paraphrased, and promoting it to a true roster entry the
  moment real reuse frequency (most plausibly via Phase 89, §8) makes
  that drift risk material rather than theoretical — an evidence-based
  trigger, not a pre-commitment (`decisions/0081` §3's own repeated
  pattern in this project).
- **The pre-identified dogfood finding could be coincidentally fixed or
  changed before implementation begins** — mitigated by §9's explicit
  honesty clause (re-verify, never assume).
- **A behavioural/status-mismatch check with no real trigger today
  could look like manufactured machinery** — mitigated by disclosing
  this honestly in §6.A/§11 rather than omitting the checks or
  inventing a fixture presented as real; this mirrors Phase 83's own
  existing precedent for a correctly-designed, currently-thin-trigger
  check (`overlapping-account-patterns-no-double-count`).
- **Failure handling**: if a later phase's real usage pattern shows the
  ad-hoc-dispatch design (§6.B) is insufficient (brief drift observed
  in practice, or dispatch frequency high enough that a standing file
  clearly earns its cost), promoting `docs/workflows/knowledge-
  placement-review.md` into a genuine `.claude/agents/*.md` roster
  entry is the named, low-risk escalation path (§6.B) — this plan is
  written so that promotion does not require redesigning §5-§9, only
  §6.B/§10's own deliverable and one new roster-table row at that
  later time.

## 13. Genuinely unresolved decisions

1. **Resolved during this plan's own independent review**: new,
   standing agent vs. an ad-hoc dispatch for the semantic/editorial
   reviewer (§6.B). The first draft proposed a 14th specialist agent
   and flagged this as the one choice most worth independent scrutiny;
   the review found the independence argument alone did not justify a
   standing file over an ad-hoc `general-purpose` dispatch carrying the
   same brief, and the plan now adopts the ad-hoc design as primary,
   with promotion to a true roster entry named as an explicit,
   evidence-gated future escalation (§12) rather than a pre-commitment.
   `domain-skeptic` remains considered and rejected as an alternative
   *host*, independent of this question.
2. **Whether `decision-citation-status-mismatch` is worth shipping now**
   given zero real trigger instances found this session (§6.A point 3,
   §11) — kept, disclosed honestly, not pre-decided against; a future
   reviewer may conclude it should be deferred until a real instance
   exists, mirroring how Phase 83's own thinly-triggered check
   (`overlapping-account-patterns-no-double-count`) was still shipped,
   named, and disclosed rather than withheld.
3. **Exact new-ADR number and filename** (§10) — assigned at
   implementation time, once the real next-available number is
   confirmed against the live `decisions/` directory (currently 92
   files, highest number 0093 per this session's own `_DECIDED_*`
   constants' own citations) — not pre-assigned here to avoid a stale
   number if other work lands first.
