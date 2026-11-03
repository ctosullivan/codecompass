# Phase 86: Knowledge-Placement and Code-Quality Review — plan

**Status: done (2026-11-03), corrective pass applied (2026-11-03).**
Implemented per this plan's own final (fourth-amendment) design, after
four independent planning-review rounds reached READY. A subsequent
narrow corrective pass (§14 below) fixed two implementation defects and
one test-fragility issue found by independent review after the initial
PASS, and closed one missing-artifact gap; none of this reopens the
plan's own design. Retro: `planning/retros/phase-86-knowledge-
placement-code-quality-review.md`. Independent DoD audit: `planning/
retros/_audit-phase-86.md` (PASS WITH NON-BLOCKING OBSERVATIONS,
corrective-pass addendum appended). Drift audit: `planning/retros/
_drift-audit-phase-86.md`.

Governing scope: `planning/v2-roadmap.md` §"Phase 86 — Knowledge-
Placement and Code-Quality Review" (10-point roadmap-depth sketch,
`decisions/0084` §2); `decisions/0085` §4 (the formal eight-category
Knowledge Placement Policy table and the three named enforcement
classes — the authoritative, later-dated source this plan's own §4
reproduces verbatim rather than re-deriving).

**Amended a fourth time (2026-11-03, "CodeCompass Orchestrator — Phase
86 Final Amendment, Verification and Implementation")**, correcting
four further independently identified design issues in the plan
committed at `9afabcc`, sections edited in place:

A. **`decision-citation-status-mismatch` deferred (mandatory)** — the
   real `decisions/0019`/`0061` relationship itself proves the risk:
   `0019`'s own `## Status` field has stood `Accepted`, unedited, since
   it was written (`CLAUDE.md` §2's append-only rule), while `0061`
   independently records that `0019` is, in effect, dead — the
   project's own real corpus already contains the exact "recorded
   status" vs. "effective status" conflict this check could not have
   told apart, which would have made a source comment candidly noting
   `decisions/0019 (historical rationale)` look like a literal status
   assertion contradicting `Accepted`, and blocked on it. Deferred,
   mirroring the oracle-contradiction check's own prior deferral: no
   new mandatory annotation convention is invented merely to justify
   shipping it. See §6.A, §7, §10, §11, §12, §13.
B. **Supersession-detection coverage widened, and its real limits
   disclosed** — the previous round's two-location scope (an ADR's own
   title line, `## Status` section) missed this project's own
   dominant real pattern: `decisions/0031`, `0032`, `0033`, `0034`,
   `0070`, `0078`, `0043` all record supersession in `## Consequences`
   or `## Decision`, not `## Status`. Widened to four sections (title,
   `## Status`, `## Decision`, `## Consequences`), with two patterns
   (passive "`decisions/NNNN` is/are superseded [by `decisions/MMMM`]";
   active "supersedes `decisions/NNNN`"), explicitly excluding
   `## Context`/`## Alternatives considered` (confirmed, from a real
   example — `decisions/0058`'s own Context section — to be where
   exploratory, not-yet-decided discussion legitimately lives) and
   explicitly excluding "partially superseded" language (a real,
   genuine qualifier this project uses, `decisions/0033`, that is
   deliberately **not** matched — a scoped, partial claim is not an
   unambiguous "treat the whole citation as dead" signal). Verified
   against the real `decisions/0027` text, "`decisions/0023` is **not**
   superseded by this ADR," as a critical negative control. Known,
   disclosed (not silent) gaps: a conjunction ("`decisions/0024` and
   `decisions/0025` are superseded," the real `decisions/0032` text)
   only captures the number immediately adjacent to the verb phrase.
   See §6.A, §11.
C. **Real-dogfood acceptance criteria generalised explicitly** — §9
   already (from the prior round) permitted widening to a different
   real subsystem if the primary candidate disappeared; criterion 2 is
   now rewritten so it does not hard-code the primary candidate's own
   expected category/enforcement classification onto a genuinely
   different replacement defect. See §9.
D. **Safe source parsing specified** — a per-file `SyntaxError`/
   `OSError` during `ast.parse`/`tokenize` now produces an explicit,
   always-blocking diagnostic finding (never silent skip, never
   crashing the whole run — the same discipline Phase 85's own
   corrective pass already established for an unreadable `test_ref`
   file); a citation inside a multiline docstring/comment reports the
   *exact* line the citation text itself appears on, not merely the
   construct's own starting line; output is sorted by `(file, line,
   rule)` for determinism; scope is confirmed bounded to
   `src/codecompass/**/*.py` (or an explicit, narrower file-set
   parameter), never the whole repository, `tests/`, or `vendor/`. See
   §6.A, §11.

Re-verified directly against the live repository before editing
anything: the `source_resolution.py` dogfood candidate still cites
`decisions/0019` at current HEAD (`9afabcc`), `sync.py`'s real caller
still never cites it, and both negative controls (`oracle.py`,
`staleness.py`) are still accurate.

---

Earlier amendment history, preserved below rather than rewritten:

1. **Behavioural verification semantics (HIGH)** — §6.A's proposed
   `docstring-contradicted-by-oracle-result` mechanical+behavioural
   script check is **deferred, not shipped**. It would have treated the
   absence of a currently-passing result (including `INVALID`, stale,
   or missing evidence) as proof a docstring's claim is false, and
   treated a bare `check_id` citation as if it established that the
   docstring asserts the check's own behaviour — both are semantic
   inferences this project's own Oracle semantics (`decisions/0081`-
   `0083`) never license mechanically. Behavioural review remains one
   of the three enforcement classes (§7) but is performed through
   existing Phase 82-84 capabities during the §6.B ad-hoc review, never
   through a new checker. See §6.A, §7, §9, §11, §12, §13.
2. **Real-dogfood exit gate (HIGH)** — §9/§11 now state explicitly that
   a constructed fixture may never satisfy or substitute for the
   mandatory real-dogfood requirement; it widens the search to another
   bounded real subsystem, or reports the gate honestly unmet, never
   both skipped and silently papered over with a fixture demo.
3. **Mechanical citation parsing (MEDIUM)** — §6.A's three remaining
   checks now specify a bounded, syntax-aware extraction method (Python
   `ast` + `tokenize`), not an unscoped regex over raw file text, so a
   citation is only ever recognised inside an actual docstring or
   comment, never an ordinary string literal or incidental prose
   mention. See §6.A, §11.
4. **Reviewer-role consistency (LOW)** — §4's "one new... advisory
   reviewer agent" wording is corrected to match §6.B's already-settled
   ad-hoc `general-purpose`-dispatch design; no other section used the
   inconsistent phrasing (confirmed by a project-wide grep sweep of this
   file for "new agent"/"reviewer agent" after editing).

Re-verified directly against the live repository before editing
anything (not assumed from the prior round): the `source_resolution.py`
dogfood candidate (§1, §9) still cites `decisions/0019` at its current
HEAD, `sync.py`'s real caller still never cites it, and both negative
controls (`oracle.py`, `staleness.py`) are still accurate — nothing
changed underneath this plan since `2bd4fcc`. §2, §3, §5, §8, and §10
(besides the files list reflecting the narrower three-check script)
required no substantive change — none of the four corrections touches
Phase 85's findings disposition, the eight-category policy table, or
this phase's reuse-of-existing-components accounting.

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
- `decisions/` — 92 ADR files. 10 of them contain the literal substring
  "superseded by" or "is superseded" somewhere (`grep -lE "superseded
  by|is superseded" decisions/*.md`), including `decisions/0061`
  ("`0019` is superseded by `0035`") — this raw-text grep is a loose
  superset, not the check's own actual match set (it also catches
  `decisions/0027`'s negated "is **not** superseded" and `decisions/
  0088`'s unrelated "a historical **result** superseded by a... PASS,"
  neither an ADR-supersession declaration at all). **Corrected this
  round** (an earlier draft of this correction miscounted): running
  §6.A's own final, section-scoped, two-pattern design directly against
  every real file this session (not estimated, executed) yields exactly
  **8** files with a genuine match — `decisions/0031`, `0032`, `0033`,
  `0034`, `0043`, `0061`, `0070`, `0078` — none of `0027`/`0058`/`0064`/
  `0081`/`0088` (correctly excluded: negation, `## Context`-only,
  broken adjacency, and two unrelated "superseded" substrings,
  respectively). §6.A's own design section lists every one of the 8
  with its exact section/pattern, not merely this aggregate count.
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
validator script covering two deterministic checks plus a parse-failure
diagnostic (§6.A); an ad-hoc, narrowly-scoped, read-only advisory
placement review —
dispatched as a `general-purpose` subagent carrying a committed
workflow-doc brief, **not a new standing agent** — for the
semantic/editorial class, with behavioural-class findings reached
through existing Phase 82-84 capabilities during the same dispatch,
never a new checker (§6.B); the three enforcement classes, precisely
defined and enforced exactly as `decisions/0085` §4 specifies (§7); one
real dogfood against a bounded, representative subsystem, demonstrating
a genuine, previously unflagged defect fixed as a direct result,
never satisfied by a constructed fixture (§9).

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
  describes; the behavioural enforcement class (§7) — the §6.B
  reviewer's own direct, correctly-precedenced reading of real oracle
  evidence, not a dedicated script check (§6.A) — is the mechanism
  that can catch a drift between the two, where real evidence exists.
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
  phase's **behavioural** enforcement class (§7) exists specifically
  for this, applied by the ad-hoc §6.B reviewer directly (never a
  dedicated §6.A script check — `docstring-contradicted-by-oracle-
  result` was deferred in an earlier round, §6.A/§13 item 3), reusing
  Phase 84's `trace_evidence`/`epistemic_status` unchanged, never
  re-deriving oracle logic.

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

### 6.A Mechanical checks — `scripts/check_knowledge_placement.py` (new)

A new, maintainer-only, on-demand script, mirroring `scripts/check_
self_knowledge_quality.py`'s own exact `Finding(rule, message, strict)`
convention, CLI shape (`--strict`, `--ledgerkit-root`), and report-only-
by-default posture. **Composes** `knowledge_api`/`knowledge_
intermediate`/`oracle` unchanged; adds no logic already present there.
Not a `codecompass` subcommand, like its siblings. **Two checks, both
mechanical** — a third (`decision-citation-status-mismatch`) and a
fourth (`docstring-contradicted-by-oracle-result`), both originally
proposed, are deferred (see the note at the end of this subsection and
§7/§9/§12/§13).

**Extraction method (amended twice now — originally an unscoped regex
over raw file text; this round widens supersession-detection coverage
and specifies failure handling)**: citations are recognised only
inside text the parser can independently prove is a real comment or a
real docstring, never inside an arbitrary string literal, f-string,
byte string, or test fixture.

1. Parse each `src/codecompass/**/*.py` file with `ast.parse` (source
   text, not bytecode). For every `Module`/`ClassDef`/`FunctionDef`/
   `AsyncFunctionDef` node, take its docstring via the same test
   `ast.get_docstring` already uses internally (the first statement, a
   bare `Expr(Constant(str))`) — never any other string literal in the
   body, however similarly shaped. This is precisely what distinguishes
   a real docstring from an ordinary string constant, an f-string, or a
   string used as test fixture data elsewhere in the same file.
2. Independently tokenize the same file with `tokenize.generate_tokens`
   and collect every `COMMENT` token (a real `#`-prefixed comment, with
   its own exact line number) — never a string literal that happens to
   contain a `#` character, which `tokenize` already does not misclassify.
3. Within each docstring's text and each comment token's text only
   (never the rest of the file), apply a single bounded regex,
   `decisions/([0-9]{4})\b`, to extract citation strings. **Line
   provenance is exact, not approximate (this round's correction)**:
   for a comment, the token's own line is already exact (a `#` comment
   is always single-line). For a docstring, which may span many lines,
   the reported line is the docstring's own starting line **plus the
   number of newline characters in the docstring's *raw* text before
   the citation's own match offset** — never uniformly "the docstring's
   starting line" regardless of where inside it the citation actually
   sits. **"Raw" is load-bearing, not incidental** (a follow-up
   independent review caught this as a real, silent bug in an earlier
   draft of this same correction): `ast.get_docstring(node)` defaults
   to `clean=True`, which runs `inspect.cleandoc`-style whitespace
   stripping and silently discards leading blank lines before counting
   begins — confirmed by direct execution this round against a
   docstring with a blank line right after the opening `"""` (this
   project's own common style): the cleaned text undercounts newlines
   by exactly the number of stripped leading blank lines, so a citation
   on line 5 of a real docstring was reported as line 3 using the
   cleaned text, silently wrong. The implementation **must** call
   `ast.get_docstring(node, clean=False)` (or equivalently read the raw
   string constant, `node.body[0].value.value`, for the node's first
   statement) for this offset calculation specifically — the project's
   own existing, unrelated use of bare `ast.get_docstring(node)` in
   `source_symbols.py`/`symbols.py` (for descriptive "purpose" text,
   which never needed exact line provenance) is correctly *not* the
   precedent to follow here, and this plan does not change those two
   existing, unrelated call sites. A bare `"decisions/"` substring with
   no following four digits is never a match (confirmed by the
   fail-closed minimal-content test, §11).
4. **Parse-failure handling (added this round, per the governing
   review's explicit safety requirement)**: if `ast.parse` raises
   `SyntaxError` on a `src/codecompass/*.py` file (malformed Python —
   should not occur in this project's own real, lint-checked source,
   but must never be assumed), or reading the file raises `OSError`,
   report `knowledge-placement-unparseable-source-file` (**always
   blocking** — an unreadable or unparseable source file is never
   silently treated as "zero citations, nothing to report," which
   would be indistinguishable from a genuinely clean file) and continue
   to the next file — one bad file never aborts the whole run, exactly
   the discipline Phase 85's own corrective pass already established
   for an unreadable `test_ref` file (`self-knowledge-quality-
   unreadable-test-ref-file`, `except OSError`, never a bare `except
   Exception`). `tokenize.generate_tokens` can independently raise
   `tokenize.TokenError`/`IndentationError` on malformed source even
   where `ast.parse` already failed first — both are caught by the same
   `knowledge-placement-unparseable-source-file` finding for that file,
   never a second, differently-named finding for the same root cause.
   **Line convention (made explicit, not left implicit)**: this finding
   carries `line=1` (the file exists and has a first line even when its
   syntax does not parse; `1` is never ambiguous with a real citation
   line, since no citation can be extracted from an unparsed file) —
   the same `(file, line, rule)` sort key below places it deterministically
   first among that file's own findings, before any real citation the
   file might otherwise have produced had it parsed.
5. **Determinism (made explicit this round)**: every finding is sorted
   by `(file, line, rule)` before output — the same tuple-sort
   discipline `check_self_knowledge_quality.py` already uses, not a new
   convention.
6. **Bounded scope (confirmed, not assumed, this round)**: the script
   walks exactly `src/codecompass/**/*.py` by default (never `tests/`,
   `vendor/`, `.venv/`, or the repository root) and accepts an explicit,
   narrower file-list parameter for a bounded dogfood/diff run (§9),
   never a free-text glob or an unscoped "everything under this commit"
   default.
7. Supersession attribution is scoped the same way, applied to
   `decisions/*.md` files rather than `src/`: `ast`/`tokenize` do not
   apply to Markdown, so this step instead regex-matches **four**
   locations per ADR file — its own first line (`# NNNN. <title>`),
   `## Status`, `## Decision`, and `## Consequences` — **widened this
   round** from the prior two-location scope (title + `## Status`
   only), which missed this project's own dominant real pattern:
   `decisions/0031`/`0033`/`0034`/`0043` record supersession in `##
   Consequences`; `decisions/0070`/`0078` record it in `## Decision`.
   `## Context` and `## Alternatives considered` (and any other section
   name) are **never** scanned — confirmed, not assumed, against a real
   example: `decisions/0058`'s own `## Context` section contains "That
   deferral is superseded by direct instruction," discussing a past
   deferral decision, not declaring this ADR's own supersession of
   another — exploratory/background discussion, exactly what this
   check must not treat as an accepted declaration. Two patterns, both
   literal, both matched **case-insensitively on the verb only** (the
   citation itself, `decisions/NNNN`, is lowercase-literal always) —
   required precisely because this project's own real text capitalises
   the verb at sentence-start (`decisions/0070`'s own Status section:
   "**Supersedes** `decisions/0069`"; `decisions/0043`'s own
   Consequences: "**Supersedes** `decisions/0041`'s..."); a
   case-sensitive-only match would silently miss both real instances —
   confirmed by direct execution this round, not assumed:
   - **Passive**: `` decisions/([0-9]{4})`?\s+(?:is|are)\s+
     (?:fully\s+)?superseded(?:\s+by\s+`?decisions/[0-9]{4}`?)?\b ``
     — captures the ADR number immediately preceding "is"/"are"
     [fully] superseded". Deliberately excludes "partially" from the
     qualifier alternation — "`decisions/0017` is **partially**
     superseded" (the real `decisions/0033` text) does **not** match,
     a genuine negative control: a scoped, partial claim is not an
     unambiguous "this whole citation is now dead" signal, and this
     check does not attempt to judge whether a given source citation
     relies on the superseded part or the surviving part.
   - **Active (self-declaration)**: `` \bsupersedes\s+`?decisions/
     ([0-9]{4})`? `` — captures the ADR number immediately following
     "supersedes" (the real `decisions/0070` Status-section text,
     "**Supersedes** `decisions/0069`," and `decisions/0078`'s Decision
     section, "**This ADR supersedes** `decisions/0062`," both match).
   Both verified empirically against the real corpus this round, not
   merely by inspection (§11 lists the exact fixtures): `decisions/
   0061`'s title (captures `0019`); `decisions/0064`'s title (no match
   — "point 8" breaks immediate adjacency, a narrower, point-level
   claim this check correctly does not parse); `decisions/0027`'s own
   `## Consequences` text, "`decisions/0023` **is not** superseded by
   this ADR — both remain in force" (no match — "not" is not in the
   optional qualifier alternation, so the literal phrase "is... not...
   superseded" never satisfies "is [fully] superseded"); `decisions/
   0031`'s Consequences, "`decisions/0001` is superseded by this ADR"
   (matches, captures `0001`, "by this ADR" unconsumed and not
   required); `decisions/0033`'s Consequences, "`decisions/0018` is
   fully superseded" (matches, captures `0018`) alongside "`decisions/
   0017` is partially superseded" (correctly no match, above).
   **Disclosed, not silent, limitations**: a conjunction — the real
   `decisions/0032` Consequences text, "`decisions/0024` and
   `decisions/0025` are superseded by this ADR" — only captures `0025`
   (immediately adjacent to the verb); `0024` is not captured, a known
   gap in conjunction handling this check does not attempt to close (a
   general-purpose natural-language parser would be needed, which this
   check deliberately is not); a differently-inflected verb ("has
   superseded," "superseding") is not recognised; an active-voice
   declaration naming a specific *quoted claim* within a cited ADR as
   superseded rather than the whole ADR (the real `decisions/0043`
   Consequences text, "Supersedes `decisions/0041`'s '...' claim
   specifically") still matches and is still surfaced — acceptable
   because this check's own output (below) is **informational only**,
   never blocking, and the §6.B reviewer is the backstop for judging
   whether a given source citation actually relies on the superseded
   portion.

**Checks**:

1. `decision-citation-exists` — every citation extracted per the method
   above must resolve to a real file under `decisions/`. **Blocking.**
   Fully deterministic: bounded extraction (above) + filesystem
   existence check, no judgment involved, no natural-language parsing.
2. `decision-citation-superseded` — for every citation that does
   resolve, if some *other*, real ADR file's title line or `##
   Status`/`## Decision`/`## Consequences` section matches either
   attribution pattern above naming the cited ADR's number, report it.
   **Informational, never blocking** — citing a superseded ADR for
   legitimate historical context (category 8) is explicitly correct,
   not a defect in itself; this check's own job is only to make every
   such citation *visible* for the semantic/editorial reviewer (§6.B)
   to judge in context, exactly mirroring this project's own
   `missing_contract`-always-informational precedent (Phase 85) for a
   mechanical fact that is not, by itself, proof of a defect.

**Deferred, not shipped: `decision-citation-status-mismatch`
(mandatory, this round).** The prior round's design reported a
blocking finding whenever a comment's own bracketed status assertion
(`decisions/0057 (rejected)`) literally disagreed with the cited ADR's
real, current `## Status` field. The governing review correctly
identified that this conflates a citation's own **recorded** `##
Status` field with its **effective** status — and the project's own
real corpus already demonstrates the conflict: `decisions/0019`'s own
`## Status` field has stood `Accepted`, unedited, since it was written
(`CLAUDE.md` §2's append-only rule means it is never corrected in
place), while `decisions/0061` independently records that `0019` is,
in effect, superseded. A source comment candidly noting `decisions/0019
(historical rationale)` or `decisions/0019 (superseded)` — an accurate
description of *effective* status — would have literally disagreed
with the recorded `Accepted` field and been blocked as if it were
wrong, when it would in fact be the comment that is right and the
append-only field that (correctly, by design) never changed. Shipping
this check would require either (a) resolving recorded-vs-effective
status first — which is exactly `decision-citation-superseded`'s own
job, already informational, never blocking — before any status
assertion could be safely compared, or (b) inventing a new, mandatory
annotation convention distinguishing the two (e.g. a
`decisions/NNNN (status: rejected)` vs. `decisions/NNNN (effectively:
superseded)` split) solely to make this check safe to ship — exactly
what the governing review instructs against. **Resolution**: this
check is not implemented. It remains deferrable, not prohibited: a
future round may ship it once (i) a real use case demonstrates comments
actually use a bracketed status-assertion convention in practice (none
does today, confirmed by corpus-wide grep, as the prior round already
disclosed) and (ii) an unambiguous, independently testable annotation
distinguishes recorded from effective status — both conditions
evidence-gated, neither pre-committed here. Removed consistently from
§7's enforcement description, §10's deliverables, and §11's test
commitments — not merely unlisted in one place while implied elsewhere.

**Deferred, not shipped: `docstring-contradicted-by-oracle-result`.**
The original draft proposed a fourth, behavioural check: cross-
referencing a docstring's cited `check_id` against `knowledge_api.
trace_evidence`/`epistemic_status` for a currently-passing result, and
reporting a contradiction whenever the only result found was `FAIL` or
`INVALID`. The independent review correctly identified two defects in
this design, both genuine, not stylistic: (a) it treated `INVALID`,
stale evidence, a missing result, and an unresolved verification path
as equivalent to a demonstrated `FAIL` — but per `oracle.py`'s own
documented outcome semantics (`_OUTCOME_VALUES = {"PASS", "FAIL",
"INVALID"}`, module docstring), `INVALID` means the check itself could
not establish a verdict (a bad fixture, an unreadable path, a digest
mismatch) and is evidence of *uncertainty*, never of a false claim — a
mechanical check that reports it as a contradiction would be reporting
a gap as if it were a disproof; (b) it treated a docstring's bare
`check_id` citation as if that alone established that the docstring
*asserts* the check's own behaviour holds — but a citation is, at most,
a pointer to related verification, not a parseable assertion of a
specific claim, and the project has no existing, independently
verifiable grammar mapping a docstring's natural-language sentence onto
one specific contract check's own pass/fail scope. Inventing one now
(a new `` `assert: check_id` `` annotation convention, say) would be
introducing a new mandatory convention solely to manufacture a trigger
for this check — exactly what the governing review instructs against.
**Resolution**: this check is not implemented. Behavioural review is
preserved as one of the three enforcement classes (§7) and remains
real and usable — through the ad-hoc §6.B reviewer directly reading
Phase 82-84's existing evidence (a real oracle-result file, `trace_
evidence`, `epistemic_status`) with the correct precedence (PASS
confirms the tested obligation within its verified scope; a valid,
current FAIL demonstrates that specific check failed, nothing broader;
INVALID/stale/missing/unresolved are gaps, never contradictions) —
without a new checker, and without a new annotation convention. If a
genuine, unambiguous instance is ever found this way, the lead's
existing, unmodified path (converting the finding into an
independently testable Requirement, §5 category 5, §7) is how it
becomes enforceable, not a script addition.

Neither of these two checks duplicates `check_self_knowledge_quality.py`'s
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
  never independently re-judged from raw text. (4) **Behavioural
  findings (added this round — §6.A's deferred check's replacement
  path, §7)**: if the target docstring/comment cites a specific
  oracle `check_id` or otherwise makes a claim a real contract result
  could confirm or disconfirm, the reviewer reads the real,
  live-reconfirmed result directly (`knowledge_api.trace_evidence`/
  `epistemic_status`, or the raw result file) and applies the same
  precedence an oracle-backed check always applies: a current `PASS`
  confirms the tested obligation within its own verified scope; a
  valid, current `FAIL` demonstrates that specific check failed, never
  automatically that the docstring's own (often broader, natural-
  language) claim is false; `INVALID`, stale evidence, a missing
  result, or an unresolved verification path is reported as a gap or
  open uncertainty, never phrased as a demonstrated contradiction. Such
  a finding is reported in the **behavioural** class only when the
  docstring's own claim and the check's own scope are the same
  obligation by construction (e.g. the docstring states the check's own
  described behaviour near-verbatim) — any looser mapping, however
  plausible, is semantic/editorial, exactly per the "would a second,
  independent reader... without relying on stylistic preference" test
  below, and is never escalated to blocking on the reviewer's own say.
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
  `decision-citation-exists` (§6.A) is this phase's one blocking
  mechanical check — a citation must resolve to a real ADR file, never
  more broadly. `knowledge-placement-unparseable-source-file` (§6.A
  point 4) also blocks, for a different, narrower reason: an unreadable
  or unparseable source file is a diagnostic failure, not a placement
  judgment. `decision-citation-status-mismatch` is deferred this round
  (above) — recorded-vs-effective ADR status (the real `decisions/
  0019`/`0061` relationship) makes a literal status-assertion
  comparison unsafe without either resolving that distinction first or
  inventing a new annotation convention, neither acceptable.
- **Behavioural** — a violation demonstrated through an accepted
  executable contract or independently verifiable evidence. **No new
  mechanical/behavioural script check implements this class** (§6.A's
  `docstring-contradicted-by-oracle-result` is deferred, not shipped —
  it would have required inferring that a bare `check_id` citation
  asserts specific behaviour, and treating `INVALID`/stale/missing
  evidence as if it were a demonstrated `FAIL`, neither of which this
  project's own Oracle semantics license). Behavioural findings instead
  arise, when real evidence actually supports one, through the ad-hoc
  §6.B reviewer directly reading a real oracle result/`trace_evidence`/
  `epistemic_status` response and applying the exact precedence every
  oracle-backed check in this project already applies: current `PASS`
  confirms the tested obligation within its verified scope; a valid,
  current `FAIL` demonstrates that one check failed, never by itself
  that a docstring's own claim is false; `INVALID`, staleness, or a
  missing/unresolved result is a gap or uncertainty, never a
  contradiction. Such a finding blocks nothing on its own — it is
  reported in the reviewer's advisory output (semantic/editorial by
  default) and becomes enforceable only via the existing conversion
  path below (converting it into an independently testable
  Requirement), never via a new script.
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
  exit code, for this script, is a function of exactly
  `decision-citation-exists` and `knowledge-placement-unparseable-
  source-file` (the two blocking checks) — `decision-citation-
  superseded` is always informational, `decision-citation-status-
  mismatch` is deferred (above), and there is no new behavioural check
  at all (above) — never of anything the ad-hoc reviewer dispatch
  concludes. Its report is a
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
  the §6.B reviewer's own behavioural-class evidence-resolution path
  (via Phase 84's API, never re-implemented, and never via a dedicated
  §6.A script check — §7).
- **Phase 82** (contract and evidence foundation): `oracle.
  parse_oracle_result`/the `Finding(rule, message, strict)` pattern
  reused unmodified; the behavioural enforcement class (§7) applies
  Oracle's own outcome precedence directly, via the ad-hoc reviewer's
  read-only use of a real result file/`trace_evidence`, never
  re-implementing precedence or digest logic in a new checker.
- **Phase 83** (semantic change assurance): the `Finding`-with-`strict`-
  flag convention `decisions/0082`/`0083` hardened in `check_contracts.
  py`/`check_knowledge_base.py` reused identically; `assess_change_
  impact.py`'s own established pattern of composing Phase 84's API
  rather than hand-rolling fresh graph-walking logic is this phase's
  own explicit model for §6.A. **Not a functional dependency** — Phase
  86's own one stated prerequisite (`decisions/0084` §2) is Phase 85
  only.
- **Phase 84** (read-only knowledge API): `trace_evidence`/
  `epistemic_status`/`find_gaps` reused unchanged by the reviewer's own
  evidence-gathering in §6.B, including its behavioural-class findings
  (§7); no new write path, no bypass of the existing read-only
  contract.
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

**Honesty clause, strengthened this round** (this task's own explicit
instruction, and the independent review's own point 3: a constructed
fixture must never satisfy or substitute for the mandatory real-
dogfood gate): the `source_resolution.py` finding above is real and
independently confirmed **twice now** — at planning time (`b434b9d`)
and again, directly, during this round's amendment (re-read this
session: lines 1-2 still cite `decisions/0019`; `sync.py`'s real
caller, `sync_vendor`, still never cites it; both negative controls
still hold). It is **re-verified a third time, not assumed, at
implementation time itself** — the implementation phase's own first
step is to re-scan `src/codecompass/` with the mechanical script
(§6.A point 2) for a currently-real `decision-citation-superseded`
instance before proceeding with this exact example.

**If the pre-identified instance is gone** (fixed by unrelated work in
the interim): widen the search to another bounded, representative
subsystem within `src/codecompass/` — rerun the same mechanical script
against progressively larger file sets (starting from the next most
central modules by citation count, §1) until either a genuine,
previously-unflagged instance of *any* real placement defect (not
limited to `decision-citation-superseded` specifically — the roadmap's
own exit gate names "a placement defect," not this one check's output)
is found, independently confirmed by direct reading (not taken from
the script's output on faith), and independently adjudicated by the
§6.B reviewer as genuine; or every bounded, representative subsystem
reasonably available has been checked. **If no genuine defect is found
after that honest search, the real-dogfood exit gate is reported
unmet, and Phase 86 is not marked done** — per the roadmap's own
mandatory requirement (`planning/v2-roadmap.md` Phase 86 point 9) and
this round's own explicit instruction that a synthetic finding must
never satisfy this gate. A constructed fixture pair (§11) remains valid
for the *unit/integration test suite only* — it never appears in, or
is cited as satisfying, this acceptance section.

**Trial steps**:

1. Re-verify the candidate directly (above), then run `scripts/
   check_knowledge_placement.py` against the three-file bounded set.
   Expect: `decision-citation-superseded` (informational) on
   `source_resolution.py`'s `decisions/0019` citation; zero mechanical
   findings on `oracle.py`/`staleness.py`.
2. Dispatch a `general-purpose` subagent, carrying `docs/workflows/
   knowledge-placement-review.md`'s full text as its brief (§6.B),
   against the same bounded set, given the script's own output as
   input evidence — this is the **independent semantic adjudication**
   this round's review requires: the script's mechanical fact (a
   citation is superseded) is never, by itself, treated as proof of a
   genuine placement *defect*; only the reviewer's independent
   judgment, backed by the real current-caller evidence it cites, does.
3. The lead reads the reviewer's report, confirms the finding is real
   and correctly reasoned (not merely restated), and **applies the
   correction itself** — an ordinary source edit to the docstring,
   never auto-applied by any agent (§4 non-goals).
4. **Post-fix verification** (added this round — the original draft
   stopped at "fix it" with no confirmation step): re-run `scripts/
   check_knowledge_placement.py` against the same three-file set after
   the fix and confirm the `source_resolution.py` finding is gone (or,
   if the fix retains a legitimate historical citation worded as such,
   confirm the finding is still correctly informational, never
   blocking); re-run `tests/test_check_knowledge_placement.py` and the
   full existing suite to confirm no regression.
5. Independently audit the whole trial (`release-phase-auditor`,
   read-only, per this project's own established pattern for judging
   an agent's output rather than trusting its self-report) — covering
   steps 1-4, not merely the reviewer's own dispatch.

**Acceptance criteria** (mirroring `decisions/0084`/`0085`'s own named
Phase 86 test requirements exactly; renumbered and tightened this
round):

1. The mechanical script correctly reports a real `decision-citation-
   superseded` (or other real placement-defect) informational finding
   on whichever file currently carries it (expected: `source_
   resolution.py`) — a true positive, mechanically reproducible by
   anyone re-running the exact command, independently re-confirmed by
   direct reading, not merely by the script's own say.
2. The reviewer independently judges that finding as a genuine,
   actionable placement defect (not merely restating the mechanical
   script's own output — explaining *why* it is misleading in context,
   citing real contradicting evidence it found itself), correctly
   classified against its own actual policy category and enforcement
   class (§5/§7) — not merely flagged, but correctly *categorised*.
   **Generalised this round**: the primary candidate's own expected
   classification is interface documentation (category 2) misplaced as
   historical design context (category 8); this is the expected, not
   the required, outcome. If the honesty clause (below) substitutes a
   genuinely different real instance, this criterion is satisfied
   against *that* defect's own real category/enforcement
   classification, whatever it actually is — never forced to match
   the primary candidate's shape.
3. The reviewer correctly **declines** to flag `oracle.py`'s own
   extensive subprocess/digest-handling comments (negative control 1,
   the named exemplar) as a verbosity/placement problem.
4. The reviewer correctly **declines** to flag `staleness.py`'s
   ordinary `decisions/0005` citations (negative control 2).
5. Neither the script's own `--strict` exit code nor any other
   mechanism treats the finding as blocking before it is fixed — it
   remains advisory/informational throughout, exactly as `decisions/
   0085` §4 requires.
6. **The finding is actually corrected by the lead, and the correction
   is independently re-verified** (trial step 4) — a found-but-unfixed
   defect, or a fix that is never re-checked, does not satisfy this
   gate. This is the roadmap's own mandatory requirement (`planning/
   v2-roadmap.md` Phase 86 point 9: "at least one real placement defect
   ... found **and corrected**"), made explicit and checked, not merely
   asserted.
7. No finding from this phase duplicates anything `check_self_
   knowledge_quality.py` already reports — confirmed in §6.A, re-
   confirmed at implementation time by running both scripts and
   diffing their rule names.
8. **If the pre-identified instance is gone, criteria 1-6 are satisfied
   against a genuinely different real instance found via the honesty
   clause's widened search above — never against a constructed
   fixture.** If, after an honest, documented search, no real instance
   exists anywhere reasonable, this gate is reported **unmet**, and
   Phase 86 does not reach `done` until it is — this is the one
   criterion a constructed fixture (§11) can never retroactively
   satisfy, by design.

## 10. Exact deliverables and expected files

| File | Status | Purpose |
|---|---|---|
| `docs/concepts/knowledge-placement-policy.md` | new | §5's full policy, in the established `docs/concepts/` style (alongside `knowledge-model.md`) |
| `docs/workflows/knowledge-placement-review.md` | new | **the full ad-hoc reviewer brief** (§6.B) — dispatched inline via a `general-purpose` subagent each time this review runs, not a `.claude/agents/*.md` frontmatter body; mirrors `docs/workflows/self-curation-loop.md`'s own precedent in style, not in hosting mechanism |
| `scripts/check_knowledge_placement.py` | new | §6.A's two checks (`decision-citation-exists`, `decision-citation-superseded`) plus the always-blocking `knowledge-placement-unparseable-source-file` diagnostic |
| `tests/test_check_knowledge_placement.py` | new | §11 |
| `src/codecompass/source_resolution.py` (or the currently-real equivalent, §9's honesty clause) | amended | the one real dogfood fix |
| `decisions/00NN-knowledge-placement-policy-and-review.md` | new | the ADR recording this phase's own design choices, per `CLAUDE.md` §2 ("write a new ADR whenever a phase involves a non-obvious tradeoff") — the ad-hoc-dispatch-not-a-new-standing-agent choice (§6.B/§12), the deferral of `docstring-contradicted-by-oracle-result` (§6.A/§7/§12/§13), the deferral of `decision-citation-status-mismatch` over the real recorded-vs-effective-status conflict the `decisions/0019`/`0061` relationship demonstrates (§6.A/§7/§12/§13, added this round — omitted from an earlier draft of this same row), and the real-dogfood gate's no-synthetic-substitute rule (§9/§12) each independently warrant one |
| `CHANGELOG.md`, `planning/ROADMAP.md`, `planning/CONTEXT.md` | amended, at implementation closeout only | per `CLAUDE.md` §3/§5, not touched by this planning commit beyond adding Phase 86's own `planned` row (this commit) |

## 11. Tests, negative controls, and acceptance gates

- `tests/test_check_knowledge_placement.py`, mirroring `tests/test_
  check_self_knowledge_quality.py`'s own structure and determinism
  test:
  - **Extraction-method boundary tests**:
    - A normal string literal (not a docstring, not a comment,
      e.g. a plain assigned variable or a test-fixture data string)
      containing the exact text `decisions/0019` — must **never** be
      extracted as a citation, confirming `ast`-scoped docstring
      detection and `tokenize`-scoped comment detection correctly
      exclude ordinary string literals.
    - A citation to a real, current (non-superseded) ADR — unflagged
      by `decision-citation-superseded`.
    - A multiline docstring with a citation on a line other than the
      docstring's own first line — confirms the reported line number
      is the citation's own exact line, not the docstring's starting
      line (this round's line-provenance correction). **The fixture
      must include a blank line immediately after the opening `"""`**
      (this project's own common style) before the citation — a
      fixture whose text starts immediately after `"""` with no blank
      line would not distinguish a correct `clean=False` (raw)
      implementation from the buggy `clean=True` (default) one a
      follow-up independent review caught, since the two give the same
      count when there is nothing to strip; this fixture shape is what
      makes the test actually load-bearing rather than coincidentally
      passing.
  - **Supersession-detection tests (widened this round — real-corpus
    fixtures, not only constructed ones, per the governing review's
    explicit request to use actual repository examples)**:
    - `decisions/0061`'s real title (`decisions/0019` is superseded by
      `decisions/0035`) — citing `decisions/0019` from a `src/`
      fixture is flagged informational; the attributing statement
      living in a *separate* file (`0061`, not `0019` or `0035`
      themselves) confirms attribution is not required to come from
      either endpoint's own text.
    - `decisions/0064`'s real title ("`decisions/0063` point 8 is
      superseded") — citing `decisions/0063` is **not** flagged; "point
      8" breaks immediate adjacency, confirming the narrower, partial
      claim is correctly excluded.
    - `decisions/0031`'s real `## Consequences` text (passive, "by
      this ADR" self-reference) and `decisions/0033`'s real `##
      Consequences` text (both "fully superseded" matched and
      "partially superseded" **not** matched, in the same file) —
      confirms `## Consequences` is scanned and the "partially"
      exclusion is a genuine negative control, not merely asserted.
    - `decisions/0070`'s real text — the active "**Supersedes**
      `decisions/0069`" in `## Status` **and** the passive "`decisions/
      0069` is superseded." in `## Decision` both independently fire,
      confirming both patterns and both of the two newly-added
      sections.
    - `decisions/0027`'s real `## Consequences` text, "`decisions/0023`
      is **not** superseded by this ADR" — **critical negative
      control**: citing `decisions/0023` is never flagged, confirming
      the literal "is...superseded" match does not fire across an
      intervening "not."
    - `decisions/0058`'s real `## Context` text ("That deferral is
      superseded by direct instruction") — citing whatever it refers
      to is never flagged on this basis; confirms `## Context` is never
      scanned, even when it contains the literal phrase.
    - An ADR file containing "superseded"/"supersede" language only in
      a non-standard section name (neither title, `## Status`, `##
      Decision`, nor `## Consequences`) — never flagged, confirming the
      four-section scope is exhaustive, not merely illustrative.
    - **Disclosed-limitation regression test**: `decisions/0032`'s real
      `## Consequences` text, "`decisions/0024` and `decisions/0025`
      are superseded by this ADR" — citing `0025` is flagged; citing
      `0024` is honestly **not** flagged — this test asserts the
      documented gap exists exactly as disclosed (§6.A), rather than
      silently relying on undocumented behaviour.
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
  - **Parse-failure handling (added this round)**: a fixture `.py` file
    with a deliberate `SyntaxError` — produces exactly one blocking
    `knowledge-placement-unparseable-source-file` finding for that
    file, the run completes (does not crash), and every other,
    well-formed fixture file in the same run is still fully checked
    (not skipped as collateral damage); a fixture file made unreadable
    via a monkeypatched `Path.read_text` raising `OSError` — same
    finding, same no-crash guarantee, mirroring `check_self_knowledge_
    quality.py`'s own `test_unreadable_result_file_does_not_crash_the_
    whole_run` precedent exactly.
  - Determinism: two consecutive runs, byte-identical output, including
    the `(file, line, rule)` sort order across a fixture set large
    enough that an unsorted or differently-sorted run would be
    detectable.
  - **Real-corpus run, not asserting zero findings** (same disclosed
    posture as `check_self_knowledge_quality.py`'s own test suite) —
    pins the specific real finding(s) present at implementation time
    by name, or honestly records their absence (§9's honesty clause).
- **No `decision-citation-status-mismatch` or `docstring-contradicted-
  by-oracle-result` tests** — both deferred with the checks themselves
  (§6.A); nothing to test until either ships.
- **Independent audit** (this task's §7 requirement, applied at
  implementation time, not during this planning task): `release-phase-
  auditor` re-runs `scripts/check_knowledge_placement.py` and its test
  suite independently; separately reviews the ad-hoc reviewer
  dispatch's own dogfood report transcript **and the lead's own
  applied fix and post-fix re-verification** against all eight
  acceptance criteria in §9 (not the reviewer dispatch alone) — the
  same way Phase 85's own dogfood adjudication evidence was
  independently reviewed rather than merely trusted. If §9's honesty
  clause was invoked (the original instance gone, a different real
  instance used, or the gate reported unmet), the audit explicitly
  confirms no constructed fixture was substituted for any of the eight
  criteria.
- **No circular self-assessment**: `release-phase-auditor` never wrote
  any of the content it audits here; the ad-hoc reviewer dispatch
  never reviews content from the same dispatch that wrote it (§7).

## 12. Risks, trade-offs, and failure handling

- **Scope creep into a general code-style linter** — explicitly
  excluded (§4); `ruff` already covers deterministic style/quality and
  is unmodified by this phase.
- **Subjective LLM judgment mistaken for an objective gate** —
  mitigated structurally: `--strict`'s own exit code is a pure function
  of `decision-citation-exists` and the diagnostic `knowledge-
  placement-unparseable-source-file` finding only (§6.A/§7) — there is
  no new behavioural check, and `decision-citation-status-mismatch` is
  deferred (above); the reviewer's own output can never affect it.
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
  honesty clause (re-verify, never assume; widen the search to another
  bounded real subsystem if needed; report the gate honestly unmet
  rather than ever substituting a constructed fixture).
- **Deferring `decision-citation-status-mismatch` could leave a real
  recorded-vs-effective status assertion unflagged** — mitigated
  structurally, not merely disclosed: `decision-citation-superseded`
  already surfaces the underlying recorded-vs-effective conflict
  informationally for every citation this corpus actually has; the
  §6.B reviewer remains the backstop for judging a specific comment's
  own status-assertion wording in context. Shipping this check later,
  once a real bracketed-status-assertion convention and an
  unambiguous recorded/effective distinction both exist, is the same
  evidence-gated escalation pattern this plan already uses elsewhere
  (`decisions/0081` §3) — not foreclosed, just not pre-committed.
- **Widened supersession-section scanning (`## Decision`/`##
  Consequences`) could pick up exploratory discussion mistaken for a
  real decision** — mitigated by scoping strictly to section *name*,
  not content-sniffing: `## Context` and `## Alternatives considered`
  are never scanned regardless of their content (the real `decisions/
  0058` Context-section counterexample, §6.A/§11, confirms this
  exclusion is load-bearing, not redundant); the real corpus's own
  `## Decision`/`## Consequences` sections consistently record adopted
  conclusions, not weighed-and-rejected alternatives, in every instance
  checked this round.
- **A conjunction (`decisions/0024` and `decisions/0025` are
  superseded...) only partly recognised** — disclosed, not silently
  incomplete (§6.A/§11): the real `decisions/0032` instance is used as
  a regression test asserting the gap exists exactly as documented,
  not papered over.
- **A constructed fixture could be mistaken for, or quietly substituted
  as, satisfaction of the real-dogfood exit gate** — the original
  draft's §9 point 7 allowed exactly this ambiguity (a fixture-based
  "full pipeline demonstration" sat alongside the real criteria without
  clearly being excluded from them). Corrected this round: §9's
  acceptance criteria now state explicitly that a constructed fixture
  can satisfy nothing in that section, only the unit/integration test
  suite (§11); an honest, searched-for absence of any real defect is
  now itself a valid, disclosed outcome that keeps Phase 86 from being
  marked done, rather than a gap papered over with synthetic evidence.
- **Deferring `docstring-contradicted-by-oracle-result` could leave a
  real docstring/evidence contradiction permanently undetected** —
  mitigated structurally, not merely disclosed: behavioural review
  stays available every time the ad-hoc §6.B reviewer runs, through
  direct, correctly-precedenced reading of real oracle evidence (§7);
  what is removed is only a dedicated, always-on mechanical scan for
  this one pattern, not the enforcement class itself. If real usage
  later shows this gap matters (a genuine instance is found this way
  more than once), the named escalation path is the same one §5/§7
  already provide: convert the specific instance into an independently
  testable Requirement, which is then enforced through the existing,
  unmodified behavioural path — not a bespoke new checker invented
  after the fact.
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
2. **Resolved this round (mandatory per the governing review)**: whether
   `decision-citation-status-mismatch` is worth shipping now. The prior
   round left this genuinely open, noting zero real trigger instances.
   This round found the real reason to defer is not merely thin
   triggering (as with Phase 83's own `overlapping-account-patterns-
   no-double-count`, correctly still shipped despite thin triggering)
   but a structural recorded-vs-effective status conflict the real
   `decisions/0019`/`0061` relationship demonstrates — deferred (§6.A/
   §7/§12), pending a real bracketed-status-assertion use case and an
   unambiguous recorded/effective annotation convention, neither
   pre-committed.
3. **Resolved during this round's independent review**: whether
   `docstring-contradicted-by-oracle-result` should ship as a fourth
   mechanical/behavioural script check (§6.A). Deferred — it would have
   inferred that a bare `check_id` citation asserts specific behaviour,
   and treated `INVALID`/stale/missing evidence as if it were a
   demonstrated `FAIL`, neither licensed by this project's own Oracle
   semantics. Behavioural review remains available through the ad-hoc
   §6.B reviewer's own direct, correctly-precedenced reading of real
   evidence (§7); a genuine instance found this way escalates only
   through the existing Requirement-conversion path, never a new
   checker.
4. **Exact new-ADR number and filename** (§10) — assigned at
   implementation time, once the real next-available number is
   confirmed against the live `decisions/` directory (92 files,
   highest number 0093 — one numbering gap, already a confirmed
   historical artefact per `decisions/0085`'s own Alternatives section,
   re-confirmed this session) — not pre-assigned here to avoid a stale
   number if other work lands first.

## 14. Corrective pass (2026-11-03) — narrow, post-completion

Five findings from an independent closeout review of the already-`done`
Phase 86, addressed without reopening the plan's own design (no new ADR
written — this pass fixes implementation defects and closeout gaps, not
a design-level tradeoff, matching Phase 85's own identical-shape
corrective-pass precedent, commit `95309f1`, which likewise fixed an
uncaught-exception handling gap without a new ADR).

1. **Missing drift-audit artifact (HIGH, fixed).** No `planning/
   retros/_drift-audit-phase-86.md` had ever been committed (confirmed
   by full `git log --all --diff-filter=A` search — every other phase
   has one). The release audit's own §4 only independently re-checked
   one specific finding secondhand; it never contained the original
   dispatch's full scope/method/verdict, so nothing reliable existed to
   reconstruct from (contrast Phase 85's own `d59a6d7`, where the full
   original report genuinely was still available). A fresh, independent
   `docs-reconstructor` dispatch was run and persisted as `planning/
   retros/_drift-audit-phase-86.md`.
2. **Invalid-UTF-8 source file could crash the validator (MEDIUM,
   fixed).** `_extract_file_citations` caught `OSError` on a source
   read but not `UnicodeDecodeError` (not an `OSError` subclass).
   Reproduced directly; fixed by widening the caught exception set;
   regression tests added.
3. **Unreadable/undecodable ADR silently weakened supersession
   detection (MEDIUM, fixed).** `_build_superseded_map` caught `OSError`
   on an ADR read and silently `continue`d — a citation to an ADR
   actually superseded *by* the unreadable file would report as clean,
   misrepresenting a partially-examined corpus as complete.
   `UnicodeDecodeError` escaped entirely, crashing the run. Both
   reproduced directly; fixed with a new, always-blocking
   `knowledge-placement-unreadable-decision-file` diagnostic; every
   other readable ADR still processed; `decision-citation-superseded`'s
   own informational severity unaffected; regression tests added.
4. **Fragile real-dogfood regression test (MEDIUM, fixed).**
   `test_source_resolution_dogfood_finding_is_present` required the
   corrected `source_resolution.py` to retain its specific historical
   `decisions/0019` citation forever — but that citation is now
   legitimate retained historical context, not an outstanding defect; a
   future, unrelated edit removing or relocating it should not break an
   otherwise-correct implementation. Refactored (renamed
   `test_real_corpus_run_produces_only_well_formed_informational_
   findings`) to assert the detector's general correctness against the
   real corpus without pinning one specific finding; the detector's own
   correct behaviour remains independently established by
   `TestRealCorpusSupersessionDetection`'s controlled, real-ADR-text
   fixtures. The original dogfood finding, its adjudication, correction,
   and re-verification remain recorded, unaltered, in this phase's own
   retro (`planning/retros/phase-86-knowledge-placement-code-quality-
   review.md`, "Real dogfood" section) — historical evidence, not a
   permanent test invariant.
5. **L-116 disposition left as bare `candidate` (LOW, fixed).**
   `knowledge-curator`'s own earlier recommendation (promote to
   `CLAUDE.md` §1) had not been approved by the user (§0) and was never
   going to resolve on its own by staying `candidate`. Flipped to
   `status: retained` — curation and recommendation complete, blocked
   only on user approval, not on further investigation — per `planning/
   v1-redefinition/learning-lifecycle.md`'s own valid-status enum. `CLAUDE.md`
   itself was not touched; the draft diff remains in `planning/
   v1-redefinition/proposed-governance-changes.md` §L, awaiting the
   user's own explicit decision.

A sixth, optional point from the same review (bounded, not a design
change) found a real line-provenance bug in multiline-docstring citation
extraction: an escaped `\n` sequence *within* one physical source line
decodes to a real newline character in `ast.get_docstring`'s own string
value, overcounting the physical line of any citation appearing after
it. Reproduced directly; fixed by slicing the raw source text via the
string literal's own `lineno`/`col_offset`/`end_lineno`/`end_col_offset`
rather than the decoded value; one regression test added.

Verification: 7 new regression tests (40 total in `tests/
test_check_knowledge_placement.py`, from 32), each independently
confirmed failing against the pre-fix code before any fix landed. Full
suite 1206 passed / 2 skipped (was 1198/2 — net +8 matches the new
dedicated tests). `ruff` clean. Real-corpus `--strict` run: 10
informational findings, exit 0, byte-identical across two consecutive
runs. `check_contracts.py`, `check_knowledge_base.py`, and
`check_self_knowledge_quality.py --strict` re-run clean against their
already-documented pre-existing baselines (the last: 35 findings, 26
blocking / 9 informational, unchanged — no Phase 85 finding suppressed
or altered).
