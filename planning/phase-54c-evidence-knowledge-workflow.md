# Phase 54c: Evidence-backed, knowledge-based, documentation-first workflow — plan

**Status:** plan only, not started. Do not begin implementation until
this plan is reviewed — per the governing prompt's own explicit "do not
begin implementation during this planning task," and this project's
established two-step pattern (Phase 54, Phase 54b). Full verbatim
request:
`planning/phase-54c-evidence-knowledge-workflow-prompt.md`.

Numbered as a bridge phase (43d/43e, 55b, 54b precedent) immediately
after Phase 54b and before Phase 55's own still-open GATE DD decision —
not a Stage E phase itself. This is deliberate: Stage E (Phases 56-59)
is *conditional* on GATE DD, which is not yet resolved, and this phase
must not pre-empt that gate. It is instead exactly the kind of
evidence-gathering `conditional-generalisation.md` §3's own decision
procedure calls for ("List every 'cannot represent' ... confirmed
finding... name the smallest candidate... take the union") — run as a
real, bounded, reversible experiment rather than a desk decision. Its
own retrospective's "durable vs. experimental" recommendation is GATE
DD's most concrete evidence input yet, not a substitute for the gate.

**Amended 2026-09-18** (direct user request, before implementation
began — no code has been written against the original version): made
Evidence records strictly neutral (§2.2 — support/contradict now lives
only on the Claim); made the Decision↔Claim boundary structural (§5.2's
hard rule — a Decision never supersedes a Claim); made user-run tests
first-class Observation/Evidence rather than a special case (§3); made
`design.md`'s citation obligation one-directional (§4 — every assertion
resolves to knowledge, not every stored Claim need appear); resolved §6
to two new agent roles plus an extended `knowledge-curator` mode, not
three new roles; added a context-packet sufficiency log (§6.1); reframed
§7's two proving cases as testing workflow mechanics and documentation
fidelity respectively, explicitly not final proof of the methodology,
with Phase 60/61 named as the first genuine-uncertainty test; and fixed
the prompt/plan filename mismatch this note's own predecessor
introduced. The original committed version remains in git history
(`9932b7d`) per this project's own preserve-don't-silently-overwrite
convention (§2.4 below is now this plan's own stated rule, applied to
itself).

## 0. Why this phase, and why now

The governing prompt asks for something bigger than any single Stage E
candidate design in `conditional-generalisation.md` §2: not just "a
`technical_dependency` kind" or "a `source_kind` enum," but an entire
**development workflow** (research → design doc → review → approval →
packet → implementation → revalidation) built around a **shared
evidence/knowledge vocabulary** (Observation, Evidence, Claim,
Derivation, Decision, Requirement) that spans both CodeCompass's own
development and downstream projects like Ledgerkit.

This is not invented from nothing. Three things already exist, proven,
that this phase generalises rather than replaces:

1. **`decisions/0051`**: agent-suggested relationships already live as
   reviewable, provenance-carrying **prose observations** in
   `planning/context-gaps/`/`planning/context-observations/` —
   explicitly **never** in `context-graph.db` — promoted only through
   the learning lifecycle once evidence justifies it. This is already
   "an agent-derived claim must not silently become a fact," just
   scoped to graph *edges* specifically, not general behavioural
   knowledge.
2. **`decisions/0054`**: agent-driven enrichment already writes through
   the *existing* enrichment tables (`vendor_enrichment`,
   `symbol_enrichment`, `doc_relation_enrichment`) — content an AI
   *produces*, tagged by producer (`model` column), never a fact
   CodeCompass *proves* — via a narrow, single-purpose agent
   (`context-enrichment-agent`) rather than folding the concern into an
   existing broader role.
3. **Ledgerkit's own `dev-docs/compat-register/*.yaml`** (studied in
   depth this session, Phase 54/54b): a real, working, human-authored
   instance of almost exactly the evidence shape this prompt asks for —
   `evidence: [{kind: manual|source|executable|test, ref, pinned_at}]`,
   `status: proposed|self-verified|verified|final`, a `reason` narrative
   citing what superseded what. It is not CodeCompass's own mechanism,
   but it is real, proven, and directly informs the shape below.

**The smallest useful move, per the prompt's own instruction ("favour
empirical discovery over speculative architecture"), is to generalise
(1)+(2)'s existing `planning/`-not-`context-graph.db` boundary and (3)'s
proven YAML shape into a slightly richer, feature-scoped knowledge store
— not to design a new database schema, ontology, or RDF model.** Every
design choice below follows from this.

## 1. Current-state inspection (what exists, what extends, what's new)

| Concern | Existing mechanism | This phase's relationship to it |
|---|---|---|
| Deterministic structural facts (symbols, imports, uses, doc artifacts, doc-relation edges) | `context-graph.db` (`graph.py`, 10 tables) | **Untouched.** No schema change. This phase's knowledge store never writes here, matching `decisions/0051`'s "no staging table" rejection reasoning applied to the same conclusion at a larger scope. |
| AI-derived interpretation of an already-proven fact | `vendor_enrichment`/`symbol_enrichment`/`doc_relation_enrichment`, keyed by content hash, tagged by producer (`model` column, `decisions/0054`) | **Precedent, not extended.** These stay exactly as-is — they enrich a fact that already exists. The new model is for *behavioural* claims that may have no corresponding graph fact at all (e.g. "`depth:` clips rather than excludes" has no `symbols`/`uses_edges` row to attach to). |
| Agent-suggested graph relationship, not yet proven | `planning/context-gaps/inbox.md` (prose + fixed field template, never in the DB) | **Direct precedent for the storage boundary** (planning/, not the DB) — but scoped to *graph edges* specifically. This phase generalises the *boundary*, not this specific queue. |
| Process/behavioural lesson | `planning/learnings/` (`decisions/0050`, `learning-lifecycle.md`) | **Sibling, not merged.** A learning is "how we should work"; a Claim/Observation is "what we currently believe about this feature's behaviour" — different lifecycles, same curator (`knowledge-curator`) already reviews both. |
| Reference-project evaluation | `context-evaluator`, `reference-project-tester`, `context-quality-evaluation.md` | **Reused for the "behavioural revalidation" step** (§8) — re-running examples/experiments after implementation is exactly what these roles already do; no new evaluation mechanism needed. |
| Reference-material ingestion with provenance | `planning/reference-projects/ledgerkit/reference-experiment/` (Phase 54, extended Phase 54b) | **Reused as one *evidence-gathering* input**, not superseded — a Context Researcher may reuse this pipeline's resolve/lock/extract shape when a feature's evidence includes pinned external source, exactly as it already did for the `depth:` case. |
| A real, external, proven "evidence + status" schema | Ledgerkit's `dev-docs/compat-register/*.yaml` | **The direct template** for this phase's own record shape (§2), adapted to be project-agnostic and to add the categories (Observation, Claim-with-contradicting-evidence, Decision, Requirement) Ledgerkit's own schema doesn't need for its narrower compatibility-classification purpose. |
| Documentation reconciliation | `docs-maintainer` (reconciles *existing* current-truth docs against *verified* implementation, post-hoc) | **Not reused directly** — this phase's Documentation Agent (§3) writes a *pre-implementation proposal* from research, a different purpose at a different point in the lifecycle. Kept as a distinct role rather than overloading `docs-maintainer`'s brief, per `decisions/0054`'s own "a new, minimal agent... owns this one job" reasoning when a genuinely different concern arises. |
| Planning-state truth | `roadmap-context-curator` | **Not reused for packet assembly** (§6, now a `knowledge-curator` mode instead) — a different concern (implementation-ready compaction of *approved* feature knowledge, not planning-doc reconciliation). |

**Conclusion:** no `src/codecompass/graph.py` schema change, no new
`context-graph.db` table, no MCP work, no new relation-detection
mechanism. The new material is entirely additive, file-based, under
`planning/knowledge/`, plus a small number of new experimental agent
roles and one new lightweight validation script — the same "try the
cheapest path first" discipline Phase 54's own §3 already used for
reference-material ingestion, applied here to the knowledge model
itself.

## 2. The minimal evidence/knowledge model

### 2.1 Storage: `planning/knowledge/<feature-slug>/`, not `context-graph.db`

One directory per researched feature (e.g.
`planning/knowledge/doc-origin-pinned-reference/` for this phase's own
proving case, §7). Inside it, one YAML file per record, id-prefixed
(`OBS-`, `EV-`, `CL-`, `DE-`, `DEC-`, `REQ-`) so cross-references are
plain strings, not database joins — exactly Ledgerkit's own
compat-register convention, generalised. A single `design.md` (§3) and
`context-packet.md` (§5) live alongside the records for that feature.

**Why not `context-graph.db`:** `decisions/0051` already rejected a
staging table for a narrower version of this exact problem ("it puts
unproven relationships one `JOIN` typo... away from being shown as
fact... a `planning/` file has none of that blast radius and is just as
reviewable"). That reasoning applies with more force here, since this
model spans whole behavioural claims, not just edges. If the experiment
succeeds and GATE DD later decides a graph-backed version is worth the
schema cost, that is Phase 56/57's own, separately-gated decision
(§2.4's "provenance / evidence" hypothesis row already anticipates
exactly this) — not pre-empted by this phase's own file-based choice.

**Why not a new database at all (e.g. a second SQLite file):** a
per-feature YAML directory is human-readable and diffable in plain git
history (matching this project's whole documentation-first ethos),
requires no migration machinery, and is trivially reversible (delete the
directory) if the experiment fails — properties a database file doesn't
give you for free. Revisit only if the experiment's own retro finds
YAML's lack of query-ability is a real, demonstrated cost, not a
hypothetical one.

### 2.2 The six record kinds

Each kind is a **small, closed set of required fields** — not a class
hierarchy, not inheritance, not a generic `Node`/`Edge` supertype. Every
kind below is deliberately narrower than a full ontology; each is
justified by one specific need the governing prompt names.

```yaml
# --- Observation (OBS-<feature>-NNN) ---
# A single, dated, reproducible act of looking — running a command,
# reading a specific file, fetching a specific URL. Never itself a
# claim about behaviour; several Observations are what an Evidence
# record or a Claim cites.
id: OBS-DEPTH-001
kind: observation
method: executable        # executable | source_read | doc_read | test_run
what_was_done: >
  Ran `hledger balance --depth 2` and `hledger balance depth:2` against
  a hand-built fixture (assets:bank:checking, :sub, :sub:deepest at
  depths 2-4) and compared output.
tool: hledger
tool_version: "1.52.4-g33fa849e7-20260910"
repository_revision: "33fa849e7ae841968bd21c427094c4fb4a4ec38d"
location: null             # or file:line for a source_read observation
raw_result: >
  Both commands print one aggregated `assets:bank` row totalling $135
  (=50+80+5) -- identical output.
timestamp: "2026-09-18T00:00:00Z"
performed_by: "general-purpose agent dispatch (baseline run)"
status: recorded           # recorded is the only status an Observation has --
                            # it does not get promoted/contradicted itself,
                            # only the Evidence/Claims built on it do

# --- Evidence (EV-<feature>-NNN) ---
# A NEUTRAL package of one or more Observations (or a direct doc/source/
# test citation) describing what was found. An Evidence record never
# asserts that it supports or contradicts anything -- that relationship
# belongs to whichever Claim cites it (supporting_evidence/
# contradicting_evidence, below). The same Evidence record can be cited
# as supporting one Claim and contradicting a different, competing Claim
# without being rewritten either way -- keeping the observation itself
# stable while interpretations built on it can differ or change.
id: EV-DEPTH-001
kind: evidence
evidence_kind: executable   # executable | source | documentation | test
what_it_shows: >
  hledger `balance --depth 2` and `balance depth:2` both aggregate every
  posting at or below the given depth into one row at that depth; no
  posting is excluded from either command's computed total.
observations: [OBS-DEPTH-001]     # or a direct source/doc/test citation, e.g.:
source_ref: "hledger-lib/Hledger/Reports/MultiBalanceReport.hs:205-238"
doc_ref: null                # e.g. "hledger.1:7054-7098" for a manual citation
test_ref: null
repository_revision: "33fa849e7ae841968bd21c427094c4fb4a4ec38d"
status: current               # current | superseded -- superseded only if a
                                # LATER OBSERVATION (e.g. at a newer pinned
                                # revision) shows this one no longer holds.
                                # Never used to mean "supports"/"contradicts"
                                # a Claim -- that distinction lives only on
                                # the Claim side, never here.

# --- Claim (CL-<feature>-NNN) ---
# An agent's interpretation, built from one or more Evidence records --
# THIS is where "does this evidence support or contradict the claim"
# lives (never on the Evidence record itself, per its own comment
# above). NEVER promoted to fact silently -- a Claim's own status field
# is the only place "how sure are we" is recorded, and contradicting
# evidence is retained, not discarded, even once a Claim is marked
# supported.
id: CL-DEPTH-001
kind: claim
statement: >
  Across balance/register/accounts, depth:/--depth is a display-only
  clip/aggregate operation and never excludes data from computation;
  stats is a genuine, partial exception (postings excluded, transactions
  not); print ignores depth entirely.
derivation: DE-DEPTH-001      # the Derivation record explaining HOW this
                               # claim was reached from the evidence below
supporting_evidence: [EV-DEPTH-001, EV-DEPTH-002, EV-DEPTH-003]
contradicting_evidence: []     # populated, not deleted, if evidence disagrees
derived_by: "general-purpose agent dispatch (treatment run)"
repository_revision: "33fa849e7ae841968bd21c427094c4fb4a4ec38d"
timestamp: "2026-09-18T00:00:00Z"
status: supported             # proposed | supported | contradicted | superseded | verified
supersedes: null              # a prior CL-... id this claim revises, if any --
                                # ALWAYS another Claim, never a Decision. A
                                # factual claim about observed behaviour is
                                # only ever revised by a new Claim backed by
                                # new/reinterpreted Evidence or Derivation --
                                # see §5.2's hard rule.

# --- Derivation (DE-<feature>-NNN) ---
# The reasoning PROCESS, not just its result -- what the prompt calls
# "the derivation process that produced them." Deliberately a narrative
# field, not a formal proof object (avoiding the "complex probabilistic
# confidence system" the prompt explicitly warns against).
id: DE-DEPTH-001
kind: derivation
claim: CL-DEPTH-001
method: >
  Traced every real command module that consumes a Query value
  (MultiBalanceReport.hs, PostingsReport.hs, Accounts.hs,
  AccountTransactionsReport.hs, EntriesReport.hs, Ledger.hs) rather than
  stopping at Query.hs's own matchesAccount definition -- the specific
  trap a prior, now-superseded claim (see supersedes) fell into.
  Confirmed each source-level finding with a live binary run.
inputs: [EV-DEPTH-001, EV-DEPTH-002, EV-DEPTH-003]
performed_by: "general-purpose agent dispatch (treatment run)"
timestamp: "2026-09-18T00:00:00Z"

# --- Decision (DEC-<feature>-NNN) ---
# A user/project-owner decision -- the ONLY record kind a human, not an
# agent, authors (or explicitly ratifies). Records CHOSEN TARGET-PROJECT
# BEHAVIOUR -- never a revision of what was factually observed upstream.
# Names what it agrees with, deliberately deviates from, or (if
# applicable) supersedes, per the prompt's explicit requirement -- but
# `supersedes` here ALWAYS names a prior DEC-... id (a Decision may
# revise an earlier Decision), NEVER a CL-... id. A Decision does not
# and cannot make a Claim wrong; it can only choose to build on it, or
# to deliberately diverge from it for the target project (§5.2/§5.3).
id: DEC-DEPTH-001
kind: decision
decides: >
  Ledgerkit's -q "depth:N" adopts hledger's clip/exclude/ignore split
  exactly (Requirement REQ-DEPTH-001-004), including the stats
  exception, rather than a simplified uniform-clip approximation.
rationale: >
  Ledgerkit's own compatibility goal is behavioural fidelity to hledger,
  not a simplified reinterpretation; the stats exception is small and
  already well-evidenced (CL-DEPTH-001).
agrees_with_claim: CL-DEPTH-001   # the Claim this decision builds on --
                                    # left in place, untouched, unquestioned
                                    # by this record
supersedes: null              # a prior DEC-... id this decision revises, if
                                # any -- never a CL-... id (see comment above)
decided_by: "project owner"
timestamp: "2026-09-18T00:00:00Z"
status: approved            # proposed | approved | rejected | superseded

# --- Requirement (REQ-<feature>-NNN) ---
# Implementation-facing, testable. The thing a coding agent actually
# implements against -- always traceable back to the Decision (and
# through it, the Claim/Evidence) that justifies it.
id: REQ-DEPTH-001
kind: requirement
statement: >
  `balance -q "depth:N"` MUST clip/aggregate display names at depth N
  and MUST NOT exclude any posting from the computed totals.
example: |
  Given a journal with assets:bank:checking:sub:deepest = $5
  When running `ledgerkit balance -q "depth:2"`
  Then the output includes one "assets:bank" row whose total includes
  that $5, and no row is silently dropped.
decision: DEC-DEPTH-001
status: proposed             # proposed | approved | implemented | verified
```

**Deliberately excluded from this list**, per the prompt's own §7
constraints: no confidence *score* (a float/probability) anywhere —
only closed `status` enums, one per kind and no two alike: `recorded`
(Observation), `current | superseded` (Evidence — neutral, §2.2's own
comment), `proposed | supported | contradicted | superseded | verified`
(Claims), `proposed | approved | rejected | superseded` (Decisions), or
`proposed | approved | implemented | verified` (Requirements). **No
automatic conflict resolution, and no Decision-level resolution
either** — contradicting evidence sits beside supporting evidence on a
Claim until a **new Claim**, backed by new or reinterpreted Evidence/
Derivation, resolves it (or doesn't, and the Claim's status stays
`contradicted` honestly). A Decision never resolves a factual
contradiction between Claims — it can only choose which
already-evidenced Claim the project builds on, or deliberately diverge
from an accurately-observed one for target-project purposes (§5.2).
No inheritance hierarchy, no generic base "Node" type — six flat,
independently-defined record shapes, each only as rich as this phase's
own proving case (§7) proves necessary. Deterministic structural facts
(symbols, imports, calls) are **not** re-represented here at all — a
Requirement's `relevant_symbols` field (§5) references them by
name/path, read-only, never duplicating `context-graph.db`'s own
content.

### 2.3 Provenance fields actually adopted (from the prompt's candidate list)

| Candidate field (prompt's list) | Adopted? | Where |
|---|---|---|
| source/artifact | yes | `source_ref`/`doc_ref`/`test_ref` (Evidence) |
| repository revision/commit | yes | `repository_revision` (Observation, Evidence, Claim) |
| location/symbol | yes | `location` (Observation), `relevant_symbols` (Requirement, via the context packet, §5) |
| method of observation | yes | `method` (Observation: `executable\|source_read\|doc_read\|test_run`) |
| tool/adapter used | yes | `tool`/`tool_version` (Observation) |
| timestamp | yes, where relevant | `timestamp` (Observation, Claim, Derivation, Decision) — omitted from Evidence/Requirement, which are keyed by revision/status instead, per "only the fields demonstrated to be useful" |
| agent/process responsible | yes | `performed_by`/`derived_by`/`decided_by` — deliberately the **same** field shape whether the actor is an agent dispatch or the user/project owner running a test themselves (§3's "user-run tests are first-class" rule) — nothing about the record shape changes based on who performed it, only the value of this field |
| parent evidence/claims | yes | `observations` (Evidence — neutral, no support/contradict flag), `supporting_evidence`/`contradicting_evidence`/`derivation` (Claim — the *only* place a support/contradict relationship is recorded), `inputs` (Derivation), `agrees_with_claim` (Decision), `decision` (Requirement) |
| status | yes | closed enum per kind, §2.2 — deliberately *different* enums per kind (Evidence's own `current\|superseded` carries no support/contradict meaning at all) |

No field is added that this phase's own proving case (§7) doesn't
exercise at least once — if a field goes unused, the retro should say so
plainly rather than the plan padding the schema speculatively.

### 2.4 Historical preservation, not overwriting

A superseded Claim or Decision is never deleted or edited in place — a
new record of the **same kind** is written with `supersedes: <old-id>`
(a Claim only ever supersedes a prior Claim; a Decision only ever
supersedes a prior Decision — never across kinds, per §5.2's hard rule),
and the old record's own `status` is updated to `superseded` (a
one-line, mechanical edit, not a rewrite of its content). This mirrors
`decisions/`'s own append-only ADR convention (`CLAUDE.md` §2) exactly,
applied one level down from
project-wide architecture decisions to per-feature behavioural claims.

## 3. Behaviour-first Context Researcher

New experimental role: `context-researcher` (draft `.claude/agents/
context-researcher.md`, written at implementation time, not now).

**Given** a roadmap goal or a named feature/behavioural question, **it**:

1. Identifies what's actually being asked (the roadmap goal or the
   specific question), explicitly, before doing anything else.
2. If executable behaviour exists (a real binary, a real test suite),
   **starts there** — runs representative examples and edge cases
   itself, records exact inputs/outputs/environment/commit as
   Observation records (§2.2) — rather than starting from documentation.
   This directly operationalises the prompt's "existing documentation
   should be treated as evidence rather than unquestioned ground truth"
   and Phase 54b's own hard-won lesson (a documentation-only reading is
   exactly how Ledgerkit's real Stage C Phase 1 reached its wrong
   conclusion).
3. Converts each Observation into one or more neutral Evidence records
   (what was found — never itself tagged as supporting or contradicting
   anything, §2.2). Whether a given Evidence record ends up supporting
   or contradicting a specific Claim is decided later, when the Claim
   itself is written (step 6) — the same Evidence may support one Claim
   and contradict a different, competing one without being rewritten.
4. Traces every real implementation path that could plausibly explain
   the observed behaviour — not stopping at the first plausible one
   (Phase 54b's own named failure mode, §5's execution-path-completeness
   criterion generalised into a standing research discipline rather than
   a one-off evaluation addendum).
5. Traces relevant tests, documentation, dependencies, and prior
   Claims/Decisions already on file for this feature (if any).
6. Synthesises Evidence into one or more Claim + Derivation record pairs,
   explicitly naming contradictions/ambiguities/gaps it could not
   resolve — as their own Claim records with `status: contradicted`, or
   as an explicit "open questions" note in the eventual design doc (§3
   below is deliberately allowed to say "I don't know" rather than
   guessing to fill the template).
7. Iterates (**observe ↔ trace ↔ test ↔ refine**, per the prompt) rather
   than running once and stopping — a targeted follow-up experiment is
   explicitly in scope if source inspection raises a new question (e.g.
   Phase 54b's own real mid-investigation revision on `stats`).

**A user/project-owner actually running an example or test is a first-
class Observation, not a special case.** Whether the `method: test_run`
Observation behind a given Evidence record was performed by a dispatched
agent or by the reviewer themselves changes only `performed_by`'s value
— never the record kind, and never routed through a Decision instead.
A Decision is reserved for simple approval or a preference among
already-evidenced options with **no new observation involved**; the
moment the reviewer actually runs something and sees a real result, that
result is an Observation/Evidence pair like any other (§5.2 restates
this from the reviewer's side).

**Tools:** `Read`, `Grep`, `Glob`, `Bash`, `Write` (writes only under
`planning/knowledge/<feature-slug>/`, never `src/`, `context-graph.db`,
or another project's repository — same read-only-elsewhere discipline
`reference-project-tester` already follows). **Never** writes a Claim
directly to `status: verified` — only `context-evaluator`-style
independent re-derivation, or an explicit user Decision, can move a
Claim past `supported` into `verified`, mirroring
`compat-differential-tester`'s own "only I may write `status: verified`"
rule (studied directly in Ledgerkit's Stage C Phase 5 material this
session) — a second, independent confirmation that this exact discipline
generalises cleanly.

## 4. Documentation-first phase gate

New experimental role: `documentation-agent` (draft `.claude/agents/
documentation-agent.md`, at implementation time) — **distinct from**
`docs-maintainer`, which reconciles *existing* current-truth docs
against *verified* implementation, post-hoc. This role authors a
*pre-implementation* proposal, at a different point in the lifecycle,
from a different input (the knowledge base, not the shipped code).

**Input:** every record under `planning/knowledge/<feature-slug>/`.
**Output:** one file, `planning/knowledge/<feature-slug>/design.md`,
in ordinary language, with (only the sections relevant to the feature —
not every section is mandatory for every feature):

- feature purpose and concepts
- observed current/upstream behaviour (cites `EV-`/`OBS-` ids)
- syntax/API forms
- behavioural rules and precedence
- important interactions and dependencies
- architecture/implementation concepts
- examples (Given/When/Then where the underlying Claim/Requirement
  supports it — see §2.2's `REQ-DEPTH-001` for the exact shape)
- edge cases
- known uncertainties (cites any `status: contradicted` Claim honestly)
- contradictions between behaviour/source/tests/docs
- proposed behaviour for the target project
- intentional differences from upstream behaviour
- non-goals
- acceptance criteria

**Every substantive assertion in `design.md` carries an inline citation**
(`CL-DEPTH-001`, `EV-DEPTH-003`, etc.) back to the knowledge base that
resolves to a real record — `design.md` is **a human-readable projection
of the knowledge base, not an independent source of truth** (the
prompt's own words, adopted verbatim as this role's operating rule). A
future `check_knowledge_base.py` (§9) mechanically verifies **this one
direction only**: every id cited from `design.md`/`context-packet.md`
actually exists. **The reverse is explicitly not required** — a stored
Claim, Evidence, or Derivation record has no obligation to appear in
`design.md` at all. Superseded Claims, contradicted Claims, rejected
Derivation paths, and intermediate research dead-ends are expected to
stay internal to the knowledge base, cited by nothing in the design
document, without that being treated as a gap — `design.md`'s job is to
faithfully project what's currently believed and approved, not to
exhaustively enumerate the research history behind it.

**Tools:** `Read`, `Grep`, `Glob`, `Write` (writes only `design.md` and
sets its own frontmatter `status:` to `RESEARCHED`, §5.1 — never
`APPROVED`, which only the human reviewer/lead can set).

## 5. User review and knowledge correction

### 5.1 Lifecycle (as `design.md`'s own YAML frontmatter `status:` field)

```
DRAFT → RESEARCHED → USER REVIEW → APPROVED → IMPLEMENTING → VERIFIED
```

- `DRAFT`: the Context Researcher has started but not finished; no
  design doc exists yet, or it exists but is known-incomplete.
- `RESEARCHED`: the Documentation Agent has produced a complete
  `design.md` from the current knowledge base.
- `USER REVIEW`: explicitly handed to the user/project owner (for
  CodeCompass's own dogfooding case, the lead stands in for this role
  and should say so plainly in the retro, per §8's "who actually did
  the reviewing" honesty this project already applies elsewhere).
- `APPROVED`: the reviewer has tested the examples, resolved open
  questions, and the resulting Decision record(s) exist.
- `IMPLEMENTING`: a context packet (§6) has been generated and handed
  to a coding agent/the lead.
- `VERIFIED`: post-implementation revalidation (§7) confirms the
  approved behaviour actually shipped.

A transition backward (e.g. `IMPLEMENTING → RESEARCHED`, if
implementation reveals the approved design was wrong) is explicitly
allowed and expected to happen sometimes — this is a real workflow
state, not a failure of the lifecycle, matching the prompt's own §6
"identify whether discrepancies represent implementation bugs, incorrect
design assumptions, or incomplete upstream understanding."

### 5.2 What the reviewer can do, and how it lands in the knowledge base

**Hard rule, stated once and enforced by every row below: a Decision
must never supersede a Claim.** A Claim is a factual proposition about
observed behaviour; only a new Claim, backed by new or reinterpreted
Evidence/Derivation, can revise it (§2.2's own `supersedes` field on
Claim is scoped to other Claims only, likewise Decision's own
`supersedes` to other Decisions only). This is the structural expression
of the prompt's own instruction that "a user Decision must not supersede
a factual Claim about observed upstream behaviour" — a correction to
*what actually happens upstream* is a factual-track action (new
Observation/Evidence, and a replacement Claim/Derivation if the overall
understanding changes); a Decision is reserved for *what the target
project chooses to do about it*, which can agree with, or deliberately
diverge from, an unchanged, still-valid Claim.

| Reviewer action | Structured effect |
|---|---|
| Tests an example themselves, confirms it | A new Observation + Evidence record, first-class exactly like an agent-run test (§3) — no Decision needed; the example's underlying Requirement moves toward `approved`. |
| Tests an example themselves, finds it factually wrong | A new Observation + Evidence record capturing what was actually seen, and — if this changes the overall behavioural understanding — a new Claim + Derivation that `supersedes` the prior Claim. A **factual correction**, on the same track a Context Researcher's own follow-up experiment would use — never routed through a Decision record. |
| Disputes the researcher's interpretation of evidence already on file (no new test run) | If the dispute reveals the existing Evidence was misread, a new Derivation (and, if warranted, a new Claim superseding the old one) reinterpreting the same Evidence — not a Decision, since no new fact is in play, only a correction to reasoning. |
| Chooses between two already-evidenced, non-contradictory readings, or simply approves the design as researched | A Decision record only — naming the chosen option (and, if relevant, the rejected one(s)) with rationale, the ADR-style "alternatives considered" discipline. **Neither Claim is marked wrong or superseded** — both stay valid observations; the Decision only says which one the project builds `Requirement`s on. |
| Identifies a desired deviation from upstream | A Decision record explicitly choosing target-project behaviour that differs from an accurately-observed-and-unchanged Claim, citing which Claim it deliberately deviates from (`agrees_with_claim`, or a parallel `deviates_from_claim` field if the distinction is worth making explicit for a given feature) — the Claim is never edited, marked wrong, or superseded by this Decision, per the prompt's explicit four-way distinction (§5.3 below). |
| Adds a constraint/non-goal | A Requirement record (`status: proposed`) or a `design.md` "non-goals" bullet, whichever is more natural for the specific case. |

**User corrections update structured knowledge, not just `design.md`
prose**, per the prompt's explicit instruction — `design.md` is
regenerated (by the Documentation Agent, re-run) from the corrected
knowledge base, rather than hand-edited out of step with it, keeping the
"projection, not source of truth" property honest over time.

### 5.3 The four-way distinction, made structurally real

> Observed upstream behaviour ≠ interpreted behaviour ≠ desired
> target-project behaviour ≠ implementation decision

This maps directly onto four different record kinds, not four
adjectives on one record:

- **Observed upstream behaviour** → Evidence (§2.2), always citing a
  real Observation.
- **Interpreted behaviour** → Claim, always citing the Evidence and
  Derivation that produced it.
- **Desired target-project behaviour** → Decision, always naming what
  Claim (if any) it agrees with or deliberately deviates from — **never**
  supersedes; a Decision can only supersede a prior Decision (§5.2's
  hard rule).
- **Implementation decision** → Requirement, always citing the Decision
  that authorises it.

A reader can always ask "is this a fact about hledger, an agent's
reading of that fact, what Ledgerkit's owner actually wants, or what
gets built" and get a different-kind-of-record answer — the structural
property the prompt calls out as "particularly important for Ledgerkit."

## 6. Approved context packet for coding agents

**Decided: a new, clearly-bounded mode of `knowledge-curator`, not a
third new agent role.** This phase introduces exactly two genuinely new
roles — Context Researcher (§3) and Documentation Agent (§4), each
justified by a role `knowledge-curator`'s own brief cannot naturally
absorb (behaviour-first primary research; pre-implementation proposal
authorship). Packet assembly is different in kind: it is a bounded,
largely mechanical compaction of records `knowledge-curator` already has
every reason to be looking at — read every record reachable from
`design.md`'s own `APPROVED` state for a feature, compact it into
`context-packet.md`. This is much closer to `knowledge-curator`'s
existing job (triage and consolidation across a queue of structured
records) than to either of the two genuinely new roles, and a fourth
brief this session's own work does not yet clearly need is a heavier
first step than the evidence calls for. `knowledge-curator.md` gains one
new, explicitly-scoped mode/section (not a rewrite of its existing
triage responsibilities) describing exactly this packet-assembly job,
its own input/output contract (below), and the same write boundary
every other mode already has (`planning/**` only). If the retro finds
this blurs "investigate an observation" and "assemble a packet"
unhelpfully, splitting it into its own role at that point is a small,
reversible follow-up — not a cost paid for guessing wrong now.

**Input:** only records reachable from `design.md`'s own
`APPROVED`-lifecycle state, plus any `status: approved`/`implemented`
Requirement. **Output:**
`planning/knowledge/<feature-slug>/context-packet.md`:

- goal (one paragraph, from the roadmap goal that started this)
- approved semantics (compacted from `design.md`'s own approved sections
  — not a copy of the whole design doc)
- requirements (every `REQ-` id in scope, verbatim)
- behavioural examples (the Given/When/Then set, verbatim)
- invariants (things that must stay true — a `design.md` subset)
- relevant architecture (a short pointer list, not an essay)
- relevant symbols/files/dependencies (plain names/paths — reads from
  `context-graph.db` read-only if useful, e.g. `query symbol`/`query
  relations` output, but never writes there)
- existing tests (paths, if any already exist)
- non-goals
- deliberate upstream differences (from the relevant Decision records)
- unresolved questions, if any (honestly disclosed, not hidden to make
  the packet look more finished than it is)
- provenance references: every `REQ-`/`DEC-`/`CL-` id the packet draws
  from, so a coding agent (or a later auditor) can always walk back to
  primary evidence.

**Explicitly not included:** the full research narrative, rejected
alternatives, raw Observation/Evidence detail, or anything not reachable
from an `APPROVED` record — the whole point (per the prompt) is that
"the coding agent should not need to independently rediscover the entire
feature," which requires the packet to be **smaller** than `design.md`,
not a renamed copy of it.

### 6.1 Sufficiency log: does the packet actually reduce rediscovery?

Word/line count comparisons are a weak proxy for whether a packet is
*actually* sufficient — this phase measures it directly instead. During
implementation (§8), the coding agent (the lead, per `CLAUDE.md` §8)
keeps a running `planning/knowledge/<feature-slug>/packet-sufficiency.md`
log: every time it has to read, grep, or otherwise consult something
**not already in `context-packet.md`** to make progress, that gap is
logged — what was needed, why the packet didn't already have it, and
whether that's a one-off omission (the packet-assembly mode simply
missed something reachable from an `APPROVED` record) or a structural
gap (the knowledge base itself never captured it, because the Context
Researcher/Documentation Agent never asked the right question). This
log is the retro's own primary evidence for "is the resulting
coding-agent context smaller **and more actionable** than raw repository
context" (§10) — a packet that is small only because it is incomplete is
not a success, and this log is what would show that, rather than a
line-count comparison hiding it.

**Not applied to the secondary proving case** (§7) — the retroactive
`hledger-depth` design doc has no implementation step to generate a
sufficiency log against.

## 7. Bounded proving case

**The two proving cases below validate two different, narrower
properties — neither, and not even both together, constitutes final
proof that this methodology works.** `CG-005` validates **workflow
mechanics**: can the six record kinds, the lifecycle, the packet
contract, and the two new agent roles actually operate end to end on a
real (if small) change without breaking down. The retroactive `depth:`
case validates **knowledge→documentation fidelity**: given rich,
already-verified evidence, does the Documentation Agent's projection of
it match reality. Neither tests the methodology's value under **genuine
uncertainty** — a real, currently-unanswered question, researched fresh,
where the workflow's actual payoff (avoiding a wrong turn nobody has
already caught) would show up. That test is deliberately deferred: Phase
60/61's own Haskell-adapter/Ledgerkit work, once it exists, is the first
opportunity to run this workflow on a question this project doesn't
already know the answer to. This phase's own retro (§10) must not
overreach past what its own two bounded cases can actually support —
"the mechanics worked" and "the projection was faithful" are real,
useful findings; "the methodology is proven" is not a claim either case
alone, or both together, can honestly make.

**Primary (full loop, real implementation, tests workflow mechanics):
`CG-005`** — add a new
`doc_artifacts.origin` CHECK-enum value for externally-sourced, pinned
reference material (currently misclassified as `origin='project'`),
correctly reclassifying Phase 54/54b's own `dev-docs/hledger-reference/*`
extracted files. Chosen over `CG-006` (mentions-by-filename) and `CG-007`
(symbol-level cross-references) because:

- It is small and genuinely boundable within one experimental phase
  (`CLAUDE.md` §1's "keep the implementation incremental and
  reversible" — a real `src/codecompass/graph.py` CHECK-enum change plus
  the code path that assigns `origin`, not a large feature).
- It still carries enough real interpretive content to exercise the
  workflow honestly — naming the new value, deciding whether it
  applies retroactively, whether a `vendor_doc` that happens to be
  externally-pinned should share it or stay `vendor_upstream` — genuine
  small design questions worth a real design doc and review gate, unlike
  a purely mechanical one-line fix.
- It already has a real, evidenced context-gap filing (`CG-005`,
  Phase 54) to seed the Context Researcher's work — the researcher does
  not start from nothing, matching this phase's own "reuse existing
  evidence" discipline.
- It is entirely within this repository — no cross-repository
  coordination with the live Ledgerkit project is needed to complete
  the *implementation* half of the loop, lowering this first
  experiment's own risk, while `CG-005`'s own subject matter (Ledgerkit
  reference material) still keeps Ledgerkit meaningfully in the loop.

**Secondary, low-cost validation (no new implementation, tests
knowledge→documentation fidelity): re-derive Phase 54b's own `depth:`
findings through this model, retroactively.**
Since Phase 54b already produced rich, independently-verified evidence
(two full investigation reports, an independent `context-evaluator`
report, and Ledgerkit's own real, shipped Stage C Phase 5 outcome as
ground truth), this is a near-free way to test whether the
Documentation Agent, given that evidence reorganised into Observation/
Evidence/Claim records, would produce a `design.md` that **matches
Ledgerkit's actual shipped behaviour** — graded against a known-correct
answer, the same evaluation-design strength Phase 54b's own methodology
already established. This does **not** re-run agents or produce new
Observations; it repackages Phase 54b's own already-collected evidence
into the new record shapes and checks whether the resulting design doc
holds up.

Both proving cases stay inside this repository and its already-studied
sibling (Ledgerkit, read-only) — no new external project is registered
for this phase.

## 8. Implementation and verification loop (for the primary proving case)

1. Implement `CG-005`'s approved Requirement(s) (the coding
   agent step is the lead, per `CLAUDE.md` §8 — no new role), working
   from `context-packet.md` as the primary input and logging every
   consulted-but-not-in-the-packet gap to `packet-sufficiency.md` as it
   happens (§6.1) — not reconstructed from memory afterward.
2. Normal `pytest`/`ruff`/`check_user_docs.py --strict` review, per
   every other phase.
3. **Behavioural revalidation**: re-run the Observations that
   established the original understanding (e.g., re-query
   `context-graph.db` for the `dev-docs/hledger-reference/*` rows'
   `origin` value, confirm it now reads the new value, confirm
   `doc_artifacts`'s CHECK constraint accepts it and rejects an invalid
   one) — reusing `context-evaluator`'s existing "inspect the target
   directly, don't trust the implementer's own report" discipline,
   scoped down to this phase's own small feature.
4. Compare actual vs. approved: update the relevant Requirement's
   `status` to `implemented` then `verified` (or `contradicted`, if the
   implementation reveals the approved design was itself wrong — a real,
   expected, non-failure outcome per §5.1's backward-transition
   allowance).
5. Refresh `docs/`/`architecture/` (existing `docs-maintainer`,
   unchanged role) and this phase's own `design.md`/knowledge records —
   preserving history per §2.4, never overwriting a superseded Claim's
   own content.
6. Retro, per §10.

**Traceability** (`Requirement → documented by design section →
demonstrated by example → tested by test → implemented by symbol/change
→ verified by behaviour`) is captured this phase **only as plain-text
cross-references** (a Requirement cites the `design.md` heading it came
from; a test file path is noted in the packet; nothing more formal) —
**no new graph edges, no new table, no automated link-checking beyond
what `check_knowledge_base.py` (§9) already does for id existence.**
Building the fuller relationship graph the prompt sketches is
explicitly **deferred** to a future phase, contingent on this one's own
evidence, per the prompt's own "do not over-engineer this traceability
in the first phase."

## 9. New tooling (deliberately minimal)

`scripts/check_knowledge_base.py` — mirrors `scripts/check_user_docs.py`'s
existing precedent and CI-friendly shape exactly: for every
`planning/knowledge/<feature-slug>/*.yaml` file, checks required fields
are present per its `kind`, every cross-referenced id
(`observations`/`supporting_evidence`/`derivation`/`decision`/etc.)
resolves to a real file in the same feature directory, `status` values
come from the closed set for that kind, and every id referenced from
`design.md`/`context-packet.md` actually exists. **No YAML schema
library dependency added** unless `tomllib`-style hand-rolled checking
(already this project's own precedent, `reference_pipeline.py`'s
`load_references_toml`) proves insufficient — checked, not assumed, at
implementation time. Lives in `scripts/`, not `src/codecompass/` (same
tier `check_user_docs.py` already occupies — a repo-maintenance tool,
not a shipped CLI feature).

## 10. Retro and durable-vs-experimental recommendation

Standard `CLAUDE.md` §5 retro, **plus a dedicated section answering
every one of the prompt's §9 questions explicitly, one by one, not
folded into prose**:

- What forms of evidence were actually useful?
- Which provenance fields were necessary? (cross-check against §2.3's
  adopted list — did every field earn its place, or should some be
  dropped?)
- Can another agent explain why an important claim is believed? (a real
  test: dispatch a fresh agent to read only `CL-DEPTH-001`'s citation
  chain and explain the `stats` exception back, without access to the
  original investigation reports — pass/fail, not a vibe check.)
- Can claims be traced back to primary evidence?
- Can contradictory evidence be retained without silently resolving it?
  (checked directly: does any Claim's `contradicting_evidence` field
  ever get quietly emptied rather than explicitly resolved by a
  Decision?)
- Can user corrections update the knowledge model cleanly?
- Does the design-document review catch misunderstandings before
  implementation? (checked against the secondary proving case, §7 — did
  the retroactively-assembled `design.md` for `depth:` correctly
  anticipate the `stats` exception, or would a naive version have missed
  it the way Stage C Phase 1 did?)
- Is the resulting coding-agent context packet smaller and more
  actionable than raw repository context? (measured primarily from
  `packet-sufficiency.md`, §6.1 — how many real gaps were logged, and
  were they one-off omissions or structural knowledge-base gaps — not
  merely a word/line count of `context-packet.md` against the raw
  `CG-005` filing, which a small-but-incomplete packet would win
  trivially and misleadingly.)
- Can implementation results update the knowledge model without losing
  historical provenance?
- Does this improve development quality enough to justify making the
  model permanent?

**The retro's own explicit recommendation** — which pieces (the record
shapes, the file-based storage boundary, each new agent role, the
lifecycle states, the packet contract) become durable CodeCompass
architecture (feeding Phase 55/GATE DD and, if approved, Phase 56/57)
versus which stay experimental or get discarded — is this phase's single
most important deliverable, per the prompt's own explicit framing. It is
a recommendation for the user to ratify, not a decision this phase makes
unilaterally (the same posture `phase-47-consolidate-findings.md`
already established for GATE DB, and `conditional-generalisation.md` §3
already established for GATE DD). **That recommendation must be scoped
honestly to what §7's two bounded cases can actually support** —
mechanics-worked and fidelity-held findings, not a general verdict on
whether the methodology improves development quality under real,
unresolved uncertainty. Where the recommendation goes beyond what this
phase's own evidence supports, it should say so explicitly and name
Phase 60/61's own real-uncertainty test as the open question, not paper
over the gap.

## 11. Roadmap update, conditional on success

**Not applied now** (this is a planning-only commit) but recorded here
as the intended follow-on, per the prompt's own §10 instruction: if this
phase's retro recommends the model as durable, `planning/v1-redefinition/
roadmap.md` gains:

- A note on Phase 60 (Haskell adapter): the adapter should emit
  Observation/Evidence records for whatever it discovers about hledger's
  own behaviour, not assert Claims directly — directly satisfying the
  prompt's §7 "language adapters should eventually emit observations/
  evidence rather than directly asserting semantic truth."
- A note on Phase 61 (hledger cross-language experiment): reruns this
  phase's own workflow on a real Haskell-side feature, this time with
  genuine cross-language Decision records (does Ledgerkit's Python
  implementation need to match hledger's Haskell behaviour exactly, or
  deviate deliberately — the four-way distinction, §5.3, exercised for
  real across languages) — and, per §7's own hedge, framed explicitly as
  the workflow's **first genuine-uncertainty test**: a real, currently
  open question, not a retrospective check against a known-correct
  answer. This is where the methodology's actual value (not just its
  mechanics or its documentation fidelity) gets a real test.
- GATE DD's own decision procedure (`conditional-generalisation.md` §3)
  gains this phase's retro as a named evidence input, alongside
  `CG-007`'s still-open promotion-bar status.

If the retro instead recommends discarding or substantially revising the
model, this section is itself superseded by that retro's own account —
per §2.4's own preserve-don't-overwrite discipline, applied to this plan
document's own eventual outcome.

## Scope

**In scope:**

- The six record-kind YAML shapes (§2.2), under
  `planning/knowledge/<feature-slug>/`, for exactly two feature
  directories: `doc-origin-pinned-reference` (primary, `CG-005`) and a
  retroactive `hledger-depth` directory (secondary, reusing Phase 54b's
  already-collected evidence, no new agent dispatch).
- Two new draft agent briefs: `context-researcher.md`,
  `documentation-agent.md` — marked EXPERIMENTAL in their own
  frontmatter/header, matching `context-enrichment-agent.md`'s own
  establishment precedent. Plus one new, explicitly-scoped mode added to
  the existing `knowledge-curator.md` (§6) — not a new file.
- `scripts/check_knowledge_base.py` (§9).
- The real `CG-005` implementation: one new `doc_artifacts.origin` CHECK-
  enum value in `src/codecompass/graph.py`, the code path that assigns
  it (wherever `spec_docs.py`/the reference-ingestion pipeline currently
  hard-codes `origin='project'` for this material), a migration
  consistent with every prior enum extension's own precedent (Phase 17,
  21), and doc/architecture updates via the existing `docs-maintainer`.
- The review-gate lifecycle (§5.1) as `design.md` frontmatter, for both
  feature directories.
- The context packet (§6) for `doc-origin-pinned-reference` only (the
  retroactive `hledger-depth` case has no implementation to hand a
  packet to), plus its `packet-sufficiency.md` log (§6.1).
- The retro (§10), including the explicit durable-vs-experimental
  recommendation.

**Explicitly deferred / out of scope:**

- Any `context-graph.db` schema change beyond the one CHECK-enum value
  `CG-005` itself already calls for (unrelated to the new knowledge
  model's own storage, which stays file-based throughout).
- A universal ontology, RDF/OWL, a probabilistic confidence system,
  automatic conflict resolution, distributed graph architecture, generic
  enterprise ingestion, or any MCP-specific work — all explicitly named
  as premature in the governing prompt's §7.
- The fuller `Requirement → design section → example → test → symbol →
  behaviour` traceability graph (§8's own explicit deferral).
- Running this workflow against the live Ledgerkit repository for a
  real, currently-unimplemented Ledgerkit feature — a natural next step
  if this phase succeeds, but not this phase's own proving case (§7's
  reasoning for staying inside this repository first).
- Making any new agent role's write access to `context-graph.db`
  possible, even indirectly — every new role in this phase writes only
  under `planning/knowledge/`, same hard boundary `decisions/0051`/`0054`
  already establish for every existing non-authoritative producer.
- Retiring or replacing `planning/context-gaps/`, `planning/
  context-observations/`, or `planning/learnings/` — they continue
  exactly as before; this phase's knowledge base is a sibling structure
  for *feature behavioural knowledge* specifically, not a replacement
  for those three existing queues' own, narrower purposes.

## Design decisions

- **No new ADR at plan time.** This phase's own infrastructure is
  explicitly reversible and non-committing (file-based, outside
  `context-graph.db`, new agent roles marked EXPERIMENTAL) — consistent
  with Phase 54/54b's own precedent of not writing a new ADR for
  reversible experimental infrastructure. If the retro recommends making
  any part durable, that recommendation is what triggers an ADR (likely
  more than one — the record-model choice and the agent-role choices are
  separable decisions), not this plan.
- **`CG-005`, not `CG-006` or `CG-007`, as the primary proving case** —
  reasoned in §7; the smaller, more boundable choice for a first
  experimental phase, at the cost of a slightly less dramatic design
  question than `CG-006`'s real matching-strategy nuance.
- **Two new agent roles, not three** — Context Researcher and
  Documentation Agent apply `decisions/0054`'s own reasoning (a
  genuinely different concern deserves its own narrow role); packet
  assembly instead extends `knowledge-curator` (§6), deliberately not
  applying that same reasoning a third time until evidence says a
  dedicated role is actually needed. If the retro finds the extended
  `knowledge-curator` mode awkward or overloaded, splitting it out is a
  small, reversible follow-up — cheaper than guessing a third role was
  needed now and finding it wasn't.
- **The secondary `hledger-depth` proving case is deliberately
  retroactive and cheap**, not a new agent dispatch — reuses Phase 54b's
  own already-verified evidence specifically because a known-correct
  answer already exists to grade the Documentation Agent's output
  against, which a fresh, currently-open question could not offer as
  cheaply.

## Files

- `planning/phase-54c-evidence-knowledge-workflow-prompt.md` — the
  governing prompt, verbatim.
- `planning/phase-54c-evidence-knowledge-workflow.md` — this plan.
- `planning/knowledge/doc-origin-pinned-reference/*.yaml`,
  `design.md`, `context-packet.md`, `packet-sufficiency.md` (§6.1) —
  new, at implementation time.
- `planning/knowledge/hledger-depth/*.yaml`, `design.md` — new, at
  implementation time (retroactive, secondary proving case).
- `.claude/agents/context-researcher.md`,
  `.claude/agents/documentation-agent.md` — new, at implementation time,
  marked EXPERIMENTAL.
- `.claude/agents/knowledge-curator.md` — amended in place with the new
  packet-assembly mode (§6); not a new file.
- `scripts/check_knowledge_base.py` — new, at implementation time.
- `src/codecompass/graph.py` — one new `doc_artifacts.origin` CHECK-enum
  value (`CG-005`'s own implementation).
- Whichever module currently assigns `origin='project'` to reference-
  ingestion output (confirmed at implementation time — `spec_docs.py`
  or the reference-experiment pipeline's own materialisation step) —
  updated to assign the new value instead.
- `docs/`, `architecture/`, `ai-docs/` — updated by `docs-maintainer` if
  `CG-005`'s implementation changes anything user-visible.
- `planning/retros/phase-54c-evidence-knowledge-workflow.md` — the
  phase retro, including the durable-vs-experimental recommendation.

## Verification

- `scripts/check_knowledge_base.py` clean against both feature
  directories' own records.
- `CG-005`'s own implementation: `pytest`/`ruff check .`/`python
  scripts/check_user_docs.py --strict` all clean; a real
  `context-graph.db` rebuild confirms the new `origin` value is accepted
  and the reclassified rows actually carry it (not merely that the
  CHECK constraint compiles).
- The retroactive `hledger-depth` design doc is checked against
  Ledgerkit's own real, shipped Stage C Phase 5 outcome (already fully
  documented, `planning/reference-projects/ledgerkit/findings.md`'s
  Phase 54b section) — does it correctly anticipate the `stats`
  exception, or does it need a correction, and if so, is that correction
  itself traceable through the model rather than silently patched.
- The "can another agent explain an important claim" test (§10) is run
  for real, not merely asserted — a fresh dispatch, no access to this
  phase's own working notes.
- `packet-sufficiency.md` (§6.1) exists and was populated live during
  implementation, not reconstructed afterward — checked by confirming
  its entries' own timestamps/ordering are consistent with the
  implementation's actual commit history, not merely that the file is
  present.
- `release-phase-auditor` PASS or PASS WITH NON-BLOCKING OBSERVATIONS.

## Done when

Standard DoD (`CLAUDE.md` §5) + both proving cases (primary:
implemented, revalidated, `Requirement` status reaches `verified` or
honestly `contradicted`; secondary: retroactive design doc produced and
graded against known-correct ground truth) + every one of the prompt's
§9 questions answered in the retro with real findings, not placeholders
+ an explicit durable-vs-experimental recommendation per record
kind/agent role/lifecycle mechanism, individually, not as one blanket
verdict + `knowledge-curator` triage of any candidate learnings this
phase itself surfaces (a phase about knowledge management is likely to
surface at least one) + `release-phase-auditor` PASS or PASS WITH
NON-BLOCKING OBSERVATIONS.

**Not done merely because the six record kinds exist and one small
feature got implemented** — done only once the retro can answer, with
real evidence, whether this workflow measurably helped, not merely
whether it ran to completion.

---

## Review gate

Per the governing prompt's own explicit "do not begin implementation
during this planning task": this plan is presented for review now.
Judgment calls worth explicit attention before implementation starts:

1. **The phase number and its relationship to GATE DD** (start of this
   document) — numbered as a bridge phase (54c) that *informs* GATE DD
   without pre-empting it, exactly like Phase 54/54b. If the intent was
   instead for this phase to *constitute* GATE DD's own resolution
   directly (skipping a separate future decision write-up), say so —
   that would change how the retro's recommendation gets ratified.
2. **`CG-005` over `CG-006`/`CG-007` as the primary proving case** (§7)
   — chosen for boundedness over dramatic design content. If a richer
   design question is preferred even at the cost of a larger first
   experiment, `CG-006` (real matching-strategy nuance, still fully
   inside this repository) is the next-best candidate.
3. **Resolved**: two new agent roles (Context Researcher, Documentation
   Agent), plus a new bounded mode on the existing `knowledge-curator`
   for packet assembly, not a third new role (§6). Flagged here only so
   the resolution itself is visible at review time, not because it's
   still open.
4. **File-based storage under `planning/knowledge/`, not any database**
   (§2.1) — the plan's strongest-argued choice, but worth explicit
   confirmation given how central it is to every other design decision
   in this plan.
