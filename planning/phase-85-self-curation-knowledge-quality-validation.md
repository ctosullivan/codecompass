# Phase 85: Self-Curation and Knowledge-Quality Validation — plan

**Status: done (2026-11-03, "CodeCompass Orchestrator — Final Phase 85
Plan Amendment, Verification and Implementation").** Implemented per
this plan, independently reviewed three times before implementation and
audited PASS WITH NON-BLOCKING OBSERVATIONS after implementation. Retro:
`planning/retros/phase-85-self-curation-knowledge-quality-validation.md`.

Governing scope: `planning/v2-roadmap.md` "Phase 85 — Self-Curation and
Knowledge-Quality Validation" (10-point roadmap-depth sketch);
`decisions/0084` §2 ("Phase 83 is unchanged; Phases 84-88 are newly
inserted") and §3 ("Self-curation is dogfooded, never circular").
Prerequisite: Phase 84 (`done`, including both its corrective pass,
`decisions/0092`, and its final corrective amendment, `decisions/0093`
— see `planning/phase-84-consolidated-knowledge-api.md`).

**Amended 2026-11-02** ("CodeCompass Orchestrator — Amend Phase 85 Plan
and Revalidate"), before any implementation began — no code has been
written against either version, so every amendment below is made in
place, not as a separate reconciliation section. An independent review
of the original version found six material issues: (1) an internally
inconsistent dogfood exit gate — §§7-9 permitted either a positive *or*
a negative outcome alone to satisfy it, and permitted a synthetic
negative control to substitute for a real declined candidate; (2) a
conflation of a candidate rejected during review with a canonical Claim
whose substantive assertion is contradicted, which would record every
falsified hypothesis as a `status: contradicted` Claim and pollute the
knowledge model; (3) a proposed validator call that made `find_gaps()`'s
own `missing_contract` rule unreachable; (4) no specified check for an
Evidence record whose `test_ref` points at a missing or malformed result
file, as distinct from an unresolved Evidence id; (5) an underspecified
independent Claim-adjudication procedure (inputs, reproduction duty,
disagreement handling, who may write a canonical Claim); and (6) two
overstated claims — that the record schema structurally prevents an
unevidenced Claim, and that two Claims sharing identical evidence are
necessarily duplicates. All six are corrected in place below (§§4, 5, 6,
7, 8, 9, 10), with the independent review's own verdict recorded in
§12's dated corrective note.

---

## 1. Verified current state and dependencies

Read live for this plan, not assumed:

- **The knowledge-record model** (`planning/phase-54c-evidence-
  knowledge-workflow.md` §2, Phase 54c; unchanged since): six record
  kinds under `planning/knowledge/<slug>/*.yaml` — `OBS-` (Observation,
  one dated act of looking; never itself a claim), `EV-` (Evidence, a
  neutral package of Observations/citations; never tags itself
  supporting/contradicting anything), `CL-` (Claim, the behavioural
  assertion, carrying `supporting_evidence`/`contradicting_evidence`/
  `status`/`evidence_support_state`/`basis`/`assertion_kind`), `DE-`
  (Derivation, the reasoning *process* — not just the conclusion),
  `DEC-` (Decision, accepted intent), `REQ-` (Requirement, an accepted
  obligation, `depends_on` its own Claims). Stored as plain YAML, one
  file per record, git-diffable — `decisions/0051`'s own
  "staging-table blast radius" rejection applied at feature-knowledge
  scale.
- **Four independently-computed epistemic predicates**
  (`decisions/0080`): INTENDED (an accepted Requirement/Decision),
  OBSERVED (`derive_provenance_label`), VERIFIED-per-scope (a cited
  oracle result, Phase 82/83), CONTESTED (`status: contradicted` or
  non-empty `contradicting_evidence`). Computed at read time by
  `knowledge_intermediate.derive_epistemic_profile`, never persisted,
  never a fifth state or confidence score.
- **`context-researcher`** (`.claude/agents/context-researcher.md`,
  Phase 54c, EXPERIMENTAL): the existing role that directly writes
  `OBS-`/`EV-`/`CL-`/`DE-` records (`Tools: Read, Grep, Glob, Bash,
  Write`) for one named feature/behavioural question — **"never a graph
  fact and never a Decision."** Its own brief already requires: read
  what exists first; run real examples/edge cases before trusting
  documentation; trace every real implementation path, not the first
  plausible one; write Observations before Evidence before Claims;
  name contradictions/gaps explicitly. Nothing in its definition
  restricts it to an *external* reference project — `planning/
  knowledge/codecompass-domain/` (186 records), `planning/knowledge/
  first-party-source-symbols/` (74 records), and `planning/knowledge/
  haskell-api-surface-extraction/` (43 records) are **already**
  first-party self-knowledge about CodeCompass's own implementation,
  produced by this exact role run reflexively — confirmed by direct
  inspection (e.g. `CL-ADPT-001.yaml`'s `derived_by: "context-researcher
  agent dispatch"`, citing `src/codecompass/adapters/base.py` directly).
  **Self-curation is therefore not a new capability to build — it is
  this already-existing role, already used this way, formalised into a
  repeatable procedure and independently demonstrated once more.**
- **`knowledge-curator`** (`.claude/agents/knowledge-curator.md`): the
  existing triage role for `planning/learnings/` and `planning/
  context-gaps/`, independently re-verifying cited evidence before
  recommending promote/retain/merge/discard — demonstrated repeatedly,
  concretely, in this very session's own Phase 84 closeout (e.g.
  independently re-confirming `L-107` via direct hash comparison;
  disagreeing with this phase's own retro's self-report and filing
  `L-110`/`L-111` after independently re-reading the source and test
  files cited). `knowledge-curator`'s own write boundary confirmed
  (`.claude/agents/knowledge-curator.md`, direct reading): it may write
  `planning/learnings/**`/`planning/context-gaps/**`/`planning/
  context-observations/**`, and `planning/knowledge/**` only in
  packet-assembly mode — **never a Claim/Evidence/Observation/Decision/
  Requirement record directly.** Phase 85 therefore reuses its
  *recommendation* role unchanged for the knowledge-record side too
  (§4.A step 7a) — the *learnings* precedent above establishes that
  `knowledge-curator` independently re-verifies and recommends; it does
  not, by itself, establish that it may also perform a Claim's own
  disposition write, which it structurally cannot (§4.A step 7b names
  who does). Corrected during this plan's own independent review — see
  §12.
- **Two separate write paths for two separate purposes, neither
  reused for the other**: `context-researcher`'s direct `Write` (new
  research → new `OBS`/`EV`/`CL`/`DE` records, no manifest) vs.
  `knowledge apply`'s reconciliation-manifest pipeline (`knowledge_
  intermediate.apply_manifest`, "Stage 3: the only command that writes
  `planning/knowledge/*/*.yaml`" for *reconciling an already-existing
  record* against a detected change in its own grounding source,
  Stage 1 mechanical detection → Stage 2 review/annotation → Stage 3
  apply). Self-curation's *new-finding* path is the former; it never
  needs or touches the latter.
- **Reconciling `decisions/0084` §3's literal wording with this design**
  (flagged during this plan's own independent review — see §12):
  §3 states a candidate "enters the existing `planning/learnings/`/
  `planning/context-gaps/` lifecycle as a candidate." Read literally,
  this plan's actual design for a *domain/implementation* finding does
  not do that — the written `CL-`/`DE-` pair (`status: proposed`) is
  itself the candidate, exactly as `context-researcher` already does
  for external reference projects, never routed through `inbox.md`.
  This plan's own position: a Claim's own `status: proposed` **is** the
  functional candidate state §3 means for this kind of finding — the
  same evidence-gated, not-yet-accepted state `inbox.md`'s own
  `candidate` status represents for a *process* finding — and §3's own
  prose is describing the general principle (nothing becomes accepted
  knowledge merely because an agent recorded it) rather than mandating
  literally one specific file format for every finding kind. This is
  the plan's own explicit reconciliation, not a silent deviation; an
  implementer or auditor who reads §3 more literally should treat this
  paragraph as the plan's own answer to that reading, not an
  unaddressed gap.
- **`planning/context-gaps/README.md`**: explicitly scoped to
  relationships `context-graph.db` should hold but mechanical detection
  cannot produce (source/dependency/doc-mention graph only). Its own
  "What does NOT belong here" list excludes exactly what Phase 85
  produces (implementation-behaviour facts, process observations) —
  confirmed by direct reading, not assumed. Self-curation findings
  about CodeCompass's own implementation are knowledge-record
  candidates (above); process-lesson findings (about *how the work was
  done*, not *what CodeCompass does*) are `planning/learnings/`
  candidates, exactly the existing split this session's own Phase 84
  closeout used throughout (`L-107` through `L-111`).
- **Phase 84's consolidated API** (`src/codecompass/knowledge_api.py`,
  `done`): `search`/`get`/`traverse`/`trace_evidence`/`epistemic_
  status`/`find_gaps`/`get_context_packet`/`export_snapshot`, all
  read-only, all already multi-slug-capable (`find_gaps(project_root,
  slug=None)` already scans every slug when `slug` is omitted —
  confirmed by direct reading of `src/codecompass/knowledge_api.py`
  line ~1356).
- **`find_gaps()`'s current rule set** (confirmed by direct reading,
  not assumed): `unverified_required_scope`, `contradiction`,
  `stale_test_citation`, `missing_contract`, `dangling_evidence_
  reference`, `dangling_dependency_reference`. **Gap identified for
  this plan**: no existing rule flags an obligation-bearing record
  (`claim`/`requirement`) with *zero* resolved evidence anywhere,
  corpus-wide — `trace_evidence()` answers this per-record (its own
  `"gap"`/`missing_evidence` status), but nothing calls it across every
  record in every slug the way `find_gaps()`'s other rules do. Addressed
  in §4.C below, by composition, not a further edit to
  `knowledge_api.py` (Phase 84 is closed; see §6 Non-goals).
- **`knowledge_intermediate.knowledge_status()`**: an existing,
  separate on-demand check (contradicted/`proposed`-unchecked Claims/
  Requirements, unresolved concurrent-change conflicts, advisory
  doc-grounding coverage) — already exposed as `codecompass knowledge
  status [SLUG] [--strict]`.
- **`scripts/check_knowledge_base.py --strict`**: an existing,
  separate maintainer validator (structural hygiene + snapshot-
  divergence, Phase 54c/79) — confirmed currently reporting 24
  informational, non-blocking findings against the real corpus (run
  live during this plan's research: `knowledge-base-snapshot-current-
  divergence` entries for `CL-ADPT-*`/`CL-CTXT-*`/`CL-EVID-*`/
  `CL-FPSS-007`, each individually legitimate per that script's own
  "expected and healthy if this is a legitimate supersession" framing
  — not itself evidence of a defect, but confirms the corpus is real,
  live, and already being mechanically watched).
- **Phase 83's oracle** (`src/codecompass/oracle.py`, `done`,
  unchanged by Phase 84): `OracleContract`/`OracleResult`/
  `evaluate_result_precedence`/`aggregate_contract` — the mechanism any
  self-curation finding about CodeCompass's own *runtime behaviour*
  (as opposed to a static source-reading finding) would cite as
  independent evidence, exactly as `balance-from-spec`'s own Claims
  already do for Ledgerkit's `balance_from_spec`.
- **The learning lifecycle** (`planning/v1-redefinition/learning-
  lifecycle.md`): `inbox.md` candidate schema (origin/date/
  project_revision/observation/evidence/classification/status/
  recurrence), promote/retain/merge/discard → destination table,
  `promoted.md` append-only pointer log, hygiene checks in `scripts/
  check_user_docs.py`. Reused unchanged for any *process*-lesson
  Phase 85's own dogfood run itself surfaces (distinct from the
  *domain* finding the dogfood run is about — see §5).

---

## 2. Objectives and intended user value

CodeCompass develops and maintains an **independently substantiated**
understanding of its own implementation, architecture, behavioural
obligations, and limitations — using ordinary development work as the
source of new candidate knowledge, not a separate research exercise
run on a schedule. A developer or coding agent working on CodeCompass
itself gets the same kind of grounded, evidence-backed answer to "what
does this actually do, and how do we know" that CodeCompass already
gives about an external reference project (Phase 54c) or about
Ledgerkit's `balance_from_spec` (Phase 82/83) — turned reflexively on
CodeCompass itself, at the same evidence bar, through the same
lifecycle, with the same capacity to say "we don't actually know that"
or "that turned out to be wrong" as to say "yes, confirmed."

**Explicitly not the objective**: a continuously running background
process, a new knowledge-record kind, a weaker promotion bar for
self-knowledge specifically, or a demonstration engineered to always
succeed. The governing principle this plan is answerable to: CodeCompass
must be able to discover potentially useful knowledge about itself,
verify it, preserve its provenance, recognise uncertainty, and reject
unsupported conclusions — including its own.

---

## 3. Existing capabilities reused (nothing new is architected)

| Need | Reused capability | New? |
|---|---|---|
| Retrieve what's already known/uncertain before investigating | `knowledge_api.search`/`get`/`epistemic_status`/`find_gaps`/`get_context_packet` | No |
| Investigate and author new domain findings | `context-researcher` (run against `src/codecompass/`/`planning/knowledge/<self-slug>/` instead of an external project) | No — same role, same write path |
| Independently verify a behavioural claim | `oracle.evaluate_result_precedence`/`aggregate_contract` (Phase 83) | No |
| Triage/promote/retain/merge/discard a candidate | `knowledge-curator` | No |
| Record a process-lesson distinct from a domain finding | `planning/learnings/inbox.md` lifecycle | No |
| Detect missing/stale/contradictory knowledge on demand | `find_gaps`/`knowledge_status`/`check_knowledge_base.py --strict`, composed (§4.C) | No (composition only) |
| Portable export of a reconciled slug | `knowledge_api.export_snapshot` | No |

Nothing in this plan requires: a new agent role, a new record kind, a
new database/schema, a new write path, a weaker or self-curation-
specific promotion bar, or a modification to the just-closed `src/
codecompass/knowledge_api.py`/`oracle.py`/`knowledge_intermediate.py`.

---

## 4. Proposed workflow and component responsibilities

### 4.A The bounded self-curation workflow (8 steps, per the governing prompt's own §6.B)

1. **Identify a bounded investigation.** Arises from ordinary
   development work (exactly as `L-107`-`L-111` arose from this
   session's own Phase 84 closeout) — a specific, named question about
   one CodeCompass subsystem's actual behaviour, scoped the same way a
   `context-researcher` dispatch is already scoped today (§7 names the
   concrete first instance). **Owner: the lead** (or any agent
   mid-task, surfacing it to the lead — matches how `L-107` arose
   mid-Phase-84, not from a dedicated "find things to research" step).
2. **Retrieve existing knowledge/uncertainty via Phase 84's API.**
   `knowledge_api.search(project_root, <topic>)`, `get()` on any
   specific id already known, `find_gaps(project_root, <slug>)`, and
   `epistemic_status()` on the nearest existing Claim/Requirement —
   run *before* dispatching research, so the investigation starts from
   "here is what is already known/unconfirmed/missing," never
   re-deriving a picture a `grep` could have given faster. **Owner: the
   lead**, feeding the result into the dispatch prompt (mirroring how
   `context-researcher`'s own brief already says "read what exists
   first," now backed by a structured query instead of an ad hoc
   directory read).
3. **Examine current source/tests/decisions for candidate findings, in
   the bounded self-curation investigation mode (new, narrow, this
   plan's own third independent review — see §12).** **Owner:
   `context-researcher`**, dispatched exactly as today in every other
   respect, target set to CodeCompass's own `src/codecompass/`,
   `tests/`, `decisions/` instead of an external project's checkout.

   **The one behavioural difference from ordinary mode, and why it is
   needed**: `context-researcher`'s own existing brief (steps 3-4 of
   `.claude/agents/context-researcher.md`) unconditionally writes one
   `OBS-<feature>-NNN.yaml` per act of looking and converts it to a
   neutral `EV-<feature>-NNN.yaml` as it goes — a real conflict with this
   plan's own §4.A step 6/§4.E requirement that outcome 2/3/4 (duplicate/
   falsified/insufficient) leave **no** record under `planning/
   knowledge/` at all, since an ordinary dispatch would already have
   written the `OBS-`/`EV-` pair for a probe before its disposition is
   even known. **Resolved by one narrow, explicitly-scoped mode, not a
   new role and not a schema/permission change**: in this mode only,
   `context-researcher` performs the identical looking/probing/tracing
   work (steps 1-2, 4-5, 7-8 of its own brief, unchanged) but **defers
   committing `OBS-`/`EV-` files to disk** until the candidate's own
   §4.E disposition is known, keeping the full content (exact command/
   file:line, exact real output, repository revision) in its own working
   notes in the meantime — not a new, unrestricted scratch database,
   just the ordinary content of its own eventual report, reordered. Once
   the disposition is known (step 4, below):
   - **Outcome 1 (new) or 5 (genuine contradiction)**: writes the full
     `OBS-`/`EV-`/`CL-`/`DE-` set to `planning/knowledge/<slug>/` at
     `status: proposed`, exactly as ordinary mode already does — no
     content or write-boundary change, only the timing.
   - **Outcome 2/3/4 (duplicate/falsified/insufficient)**: writes
     **nothing** to `planning/knowledge/`. Instead, returns the complete
     reproducible content to the lead in its own report, in the exact
     shape the investigation log's own schema (§4.E) requires
     (hypothesis, investigation scope + repository revision, evidence,
     reason) — `knowledge-curator`, not `context-researcher`, is the one
     who writes the actual investigation-log entry (§4.A step 7a,
     unchanged), preserving the existing write-boundary split rather
     than letting `context-researcher` write outside `planning/
     knowledge/**` for the first time.
   This changes *when* a write happens and *whether* one happens for a
   declined candidate — it changes neither *what* `context-researcher`
   is allowed to write nor *where*, so it introduces no new permission,
   no new tool, and no new agent role, matching the governing prompt's
   own explicit constraint.

   **`context-researcher.md`'s own brief needs a small, compatible
   update** — at implementation time, one further, explicitly-named
   mode section ("Self-curation investigation, Phase 85, bounded"),
   describing exactly the deferred-write mechanic above and nothing
   else. Its ordinary feature-research mode (every other dispatch,
   including its own existing reflexive use against CodeCompass's own
   implementation prior to Phase 85, e.g. `first-party-source-symbols`'s
   own existing 74 records) is **completely unaffected** — this mode
   triggers only when a dispatch is explicitly framed as a Phase 85
   self-curation investigation, named as such in the dispatch prompt, not
   a default behavioural change. Idempotency is preserved exactly as
   before: a repeated, identical investigation that again lands on
   outcome 2 (already-known) writes nothing new under either mode, since
   step 4's classification — now run *before* any write, under this
   mode — recognises it as such.
4. **Determine which of five outcomes applies, per §4.E's own
   disposition procedure, before writing anything.** `context-
   researcher`'s own existing step 1-2 discipline (read what's on file;
   compare against the §4.A.2 retrieval) decides this: **(1) genuinely
   new** — proceed to write a Claim; **(2) duplicate/already-known** —
   matches an existing, unsuperseded Claim; nothing new is written, and
   the outcome is recorded only in the investigation log (§4.E); **(3)
   falsified hypothesis** or **(4) insufficiently supported** — the
   working hypothesis did not hold up, or could not be independently
   reproduced; recorded in the investigation log, **not** as a canonical
   Claim; **(5) genuine contradictory knowledge** — the narrower case
   where the negative result is itself a substantive fact overturning an
   existing, still-live Claim, written as a `status: contradicted` Claim
   citing the prior one, exactly as the role already does for external
   projects, but only this narrowly (§4.E's own test for "substantive").
   The default for "I tried a hypothesis and it turned out false" is the
   investigation log, not a new canonical record — recording every
   unsuccessful hypothesis as a Claim would pollute the knowledge model
   and generate persistent `find_gaps()` noise for assertions nobody
   needs to query again (flagged by this plan's own second independent
   review — see §12).
5. **Collect independently reproducible evidence.** `context-
   researcher`'s own existing `OBS-`→`EV-` discipline — a real
   executed command, a real file:line read, a real Phase 83 oracle
   result citation; content captured in working notes under step 3's
   deferred-write mode, same substance as ordinary mode, no new
   evidentiary category.
6. **Submit through the established lifecycle.** For outcome (1) (new)
   or (5) (genuine contradiction, §4.E), the written `CL-`/`DE-` record
   pair *is* the candidate — there is no separate "submission" step,
   since `context-researcher`'s own write (now committed to disk per
   step 3's deferred-write resolution) already places it in `planning/
   knowledge/<slug>/`, exactly where `knowledge-curator`'s triage (next
   step) and `knowledge_api`'s own retrieval already look. For outcome
   (2)/(3)/(4), **nothing is written under `planning/knowledge/` at
   all** — `context-researcher` never committed the deferred `OBS-`/
   `EV-` pair, and `knowledge-curator` writes the investigation-log
   entry (§4.E) from the reported content instead, itself the
   "submission" for a declined candidate; step 7's triage still runs
   against it (confirming the disposition and its evidence, not a
   Claim). A *process* lesson the same investigation happens to surface
   (how the work was done, not what CodeCompass does) is filed
   separately, as a `planning/learnings/inbox.md` candidate, through the
   unchanged existing lifecycle — the same split this session's own
   Phase 84 closeout used.
7. **Independently adjudicate, with recorded reasons — two sub-steps,
   never one, formalised in full (this plan's own second amendment, see
   §12).**

   **7a, owner `knowledge-curator`: independent review and
   recommendation, never promotion.**
   - **Inputs**: the complete investigation output — every new `CL-`/
     `DE-`/`EV-`/`OBS-` record written (outcome 1/5), or the
     investigation-log entry alone (outcome 2/3/4); every id those
     records cite; and the §4.A.2 retrieval the lead ran before
     dispatch, so the reviewer can independently confirm an
     "already-known" classification rather than trusting `context-
     researcher`'s own say-so.
   - **Evidence the reviewer must reproduce, not merely re-read.**
     **Corrected tool-boundary gap, found by this plan's own third
     independent review: `knowledge-curator`'s own real tool list is
     `Read, Grep, Glob, Edit, Write` — no `Bash` (confirmed by direct
     reading of `.claude/agents/knowledge-curator.md`'s own frontmatter
     and its own existing Hard Rule, "You have no Bash... trace the
     check logic by hand, then end your report with an explicit 'lead:
     run `<command>` to confirm' line. The lead runs it.") — so it
     cannot itself execute a command/grep/test-run `OBS-` record.**

     **Corrected Observation-`method` taxonomy (this plan's own fourth
     independent review — see §12).** The reproduction duty splits by
     Observation `method`, not by an incomplete two-bucket guess — the
     real corpus, re-inspected live for this amendment (`grep -rhoP
     '^method:\s*\K.*' planning/knowledge/*/*.yaml`), uses **nine**
     closed, enum-style values below, **plus at least one real record
     (`OBS-KNOW-001`) whose own `method` field is free prose rather than
     one of the nine** (confirmed by this plan's own third independent
     review — a verification-claim accuracy gap, not a design one: the
     table's own fail-closed "unrecognised value" row already covers
     exactly this case by construction, so no table row needed to change
     because of it). Every value this split must cover, recognised or
     not, is handled deterministically (never silently defaulting an
     unrecognised value to "verified"). **The Observation's own `method`
     field is the only signal consulted here — never confused with the
     separate Evidence `evidence_kind` field** (`source`/`documentation`/
     `executable`/`test`/`behavioural`, confirmed from `EV-*.yaml`'s own
     frontmatter — five values, not four; the exact enumeration is not
     load-bearing to this split, only the conceptual distinction from
     Observation's `method` is), which classifies the Evidence package's
     own *citation kind*, a different question this bullet does not
     re-derive:

     | Observation `method` | Reproduction bucket | Who reproduces, and how |
     |---|---|---|
     | `source_read`, `doc_read`, `code_read` | **Inspection** — reading a specific file:line, a cited existing record, or a cited Phase 83 oracle result resolved through `knowledge_api.get()`/`trace_evidence()`. No execution. | `knowledge-curator`, **directly itself** — needs only `Read`/`Glob`, both of which it already has. |
     | `grep_search` | **Inspection, via a literal text search** (confirmed real: `OBS-FPSS-012`'s own `location: 'grep -n "unknown" src/codecompass/source_symbols.py'`) — a deterministic, non-executing search over already-committed text, not a program run. | `knowledge-curator`, **directly itself**, via its own `Grep` tool against the exact search the Observation names — it already has `Grep`, so this needs no delegation. |
     | `executable`, `targeted_probe`, `test_run`, `test_execution` | **Execution** — running a real command, a real constructed probe, or a real test invocation (confirmed real: `EV-FPSS-008`/`OBS-FPSS-008`'s own `method: targeted_probe`, this plan's own chosen dogfood target's precedent evidence). | `knowledge-curator` **specifies the exact command/probe to re-run** — reusing its own existing Hard Rule's precedent verbatim, not inventing a new convention — and ends its own report with an explicit "lead: run `<command>` to confirm" line; **the lead** (who has `Bash`) executes it exactly as specified, without altering it to influence the outcome, and reports the real, unmodified output back. `knowledge-curator` incorporates that real output into its own recommendation — it still decides *what* to check and *how to interpret* the result (the independent-judgment content of this step); only the mechanical act of pressing the keys is delegated, under its own explicit direction, never silently absorbed by the lead under `knowledge-curator`'s name. |
     | `static_analysis` | **Execution, not inspection** — confirmed real: `OBS-FPSS-013`'s own `location` field is a literal, run command (`python3 -c "import ast; ast.parse(...)"`), not a passive read; "static analysis" names *what the command checks*, not *how it was obtained*. Classified into the Execution bucket above, same handling. |
     | Any other/unrecognised `method` value | **Unknown — never silently treated as reproduced or confirmed.** `knowledge-curator` explicitly reports it as "method not recognised, cannot classify reproduction path" and recommends holding the candidate (never "promote") until a human/the lead classifies it by direct inspection of what the Observation actually did — the fail-closed default this governing prompt's own point 6 requires, never an implicit default to either inspection or execution. |

     For outcome 2, the reviewer independently re-retrieves the
     supposedly-duplicate existing Claim itself (an inspection
     operation, `Read`/`Grep`, not execution), not merely `context-
     researcher`'s own citation of it.

     A reviewer that cannot reproduce a piece of cited evidence this way
     — the command, once actually run by the lead at its own direction,
     does not produce the claimed output; the cited file:line does not
     say what is claimed; the method is unrecognised — treats that
     evidence as unconfirmed, never
     confirmed by default.
   - **Recording findings and recommending a disposition**: returned to
     the lead in the same shape `knowledge-curator`'s own existing
     output already uses (candidate id → outcome → destination) plus,
     new for this mode, one reproduction note per independently-checked
     evidence id (confirmed / could not reproduce / disagrees) and one
     of the five §4.E outcome labels as the recommended disposition.
     **This recommendation is never itself a promotion.**
     `knowledge-curator` writes the recommendation and, for outcome
     2/3/4, **writes and finalises the investigation-log entry itself**
     (clarifying an ambiguity this plan's own third independent review
     flagged — see §12: `planning/retros/phase-85-self-curation-
     investigation-log.md` is added, explicitly and narrowly, to
     `knowledge-curator`'s own write boundary at implementation time,
     the same way `planning/knowledge/**` was added for packet-assembly
     mode at Phase 54c — not left as an ambiguous "draft" requiring lead
     finalisation, since a log entry for a *declined* candidate is
     never a canonical knowledge record in the first place). It still
     never writes `planning/knowledge/**` content directly for outcome
     1/5 (a Claim/Evidence/Observation/Decision/Requirement record);
     its Hard Rules on that point (confirmed by direct reading of
     `.claude/agents/knowledge-curator.md`: "never a Claim/Evidence/
     Observation/Decision/Requirement record, those are `context-
     researcher`'s or the human reviewer's") are unchanged by this
     amendment.
   - **Who may modify a canonical Claim record**: **only the lead**
     (7b, below) — never `knowledge-curator` (structurally forbidden,
     confirmed above), never `context-researcher` (it already wrote the
     record at `status: proposed` in step 3-6; adjudicating its own
     disposition would be exactly the self-grading `decisions/0084` §3
     forbids).
   - **Disagreement or insufficient evidence**: if `knowledge-curator`'s
     own independent reproduction disagrees with the Claim's own
     assertion, or cannot reproduce a piece of cited evidence at all, the
     recommended disposition is never "promote" — it is either held at
     `status: proposed` (or the investigation log's own open/
     `evidence-gathering`-equivalent state) with the specific
     unreproduced claim named explicitly, or recommended as outcome
     3/4 if the disagreement itself resolves the question. **The lead
     does not override a documented independent disagreement by simply
     picking the other side** — if the lead believes `knowledge-
     curator`'s own reproduction is itself mistaken, the lead must
     independently re-reproduce the disputed evidence itself (the same
     discipline this session's own Phase 84 closeout repeatedly used —
     direct hash comparisons, direct source re-reads, direct test
     re-execution) and record that re-reproduction's own result before
     disposing either way — silently siding with either agent's own
     say-so, without a third, independent check, is exactly the
     circularity risk (§4.D) this procedure exists to prevent.
   - **The upgrade direction** (named by this plan's own third
     independent review as a previously-unnamed corner case; not a
     flaw the deferred-write mechanism introduced, merely one it
     sharpens): if `knowledge-curator` independently concludes a
     candidate `context-researcher` classified as outcome 2/3/4
     (nothing committed to disk) should genuinely have been outcome
     1/5, it cannot itself write the missing `OBS-`/`EV-`/`CL-`/`DE-`
     set — that remains `context-researcher`'s or the human reviewer's
     alone. It instead recommends the upgrade to the lead, with the
     specific reproduced evidence that justifies it; the lead
     re-dispatches `context-researcher` (handing back the preserved
     report content from the original investigation, never asking it to
     redo work already done) to commit the record set under its own
     ordinary, non-deferred write path; that freshly-written record then
     goes through step 7a/7b exactly like any other outcome-1/5 finding,
     never written directly from `knowledge-curator`'s own
     recommendation.

   **7b, owner the lead: apply the recommended disposition.** For
   outcome 1/5, edits the Claim's own `status`
   (`supported`/`contradicted`/`superseded`) and `evidence_support_
   state` — the *same* fields and the *same* decision space every
   existing Claim in the corpus already uses, not a new disposition
   vocabulary. For a declined candidate (outcome 2/3/4), the
   investigation-log entry is already finalised by `knowledge-curator`
   itself (7a, above) — the lead's own role here is only to confirm it
   is present and complete before step 8's requery, and writes nothing
   under `planning/knowledge/` or `planning/retros/` for that outcome.
   See §4.B for the full rationale and the real precedent (`CL-FPSS-007`'s
   own `status` history) this split is based on.

   **How the final disposition is independently checked**: the §4.A.8
   requery (below) confirms the applied state matches the
   recommendation mechanically; the phase's own `release-phase-auditor`
   pass (§11) goes further, re-deriving the verdict from the real
   repository state rather than trusting either agent's report — for a
   promoted Claim, re-running the same evidence reproduction
   `knowledge-curator` performed; for a declined candidate, confirming
   the investigation-log entry's own required fields (§4.E) are present
   and its cited evidence actually resolves.

   **Whether `knowledge-curator.md`'s own brief needs a small update**:
   yes, at implementation time — mirroring the precedent its existing
   "Implementation context packets" section already establishes (added
   Phase 54c for a different, narrower mode), the brief gains one
   further, explicitly-scoped mode section describing: this
   independent-adjudication/reproduction duty, its own input/output
   contract (above); the `source_read`/`executable` reproduction split
   and the "lead: run `<command>` to confirm" handoff for executable
   evidence, reusing its own existing Hard Rule's wording rather than a
   new one; and the narrow, explicit addition of `planning/retros/
   phase-85-self-curation-investigation-log.md` to its write boundary
   for outcome 2/3/4 entries specifically. **This is not a new agent
   role, not a new tool grant, and not a general permission change** —
   `knowledge-curator` gains no `Bash` and no broadened write access to
   `planning/knowledge/**`; it gains one new, narrowly-named file path
   it may write (mirroring exactly how `planning/knowledge/**` was
   added, packet-assembly-mode-only, at Phase 54c) and a restated
   version of a Hard Rule it already has, not a capability it does not
   have today. The same reasoning `decisions/0054`/Phase 54c already
   used to decide when a genuinely new concern earns a new role versus
   a new mode on an existing one applies here to conclude the latter,
   exactly as it did for packet assembly.
8. **Requery to verify correct representation.** **Owner: the lead** (or
   whoever ran step 7), re-running the exact §4.A.2 queries against the
   now-updated slug — for outcome 1/5, `get()` resolves the new id;
   `trace_evidence()`/`epistemic_status()` reflect the new evidence;
   `find_gaps()` no longer flags what the new finding resolved (if
   anything). For outcome 2/3/4, confirms `planning/knowledge/` itself is
   unchanged (`git diff --stat` shows no new record under the
   investigated slug) and the investigation-log entry is present and
   complete. This is the same "re-demonstrate against the real corpus"
   discipline this session's own Phase 84 corrective passes used
   throughout (e.g. re-running `trace_evidence(REPO_ROOT,
   "REQ-BFS-001")` after each fix) — applied here to confirm a
   *disposition*, not a *code fix*, landed correctly.

**Idempotency.** Re-running the same investigation when nothing has
changed produces no new Claim and no new investigation-log entry
(step 4 recognises it as outcome 2, already known). An existing Claim
is never edited in place to change its own conclusion — a changed
understanding is a *new* Claim, `supersedes:` the old one (the existing
field every Claim schema already has), exactly like this project's own
append-only ADR convention (`CLAUDE.md` §2), applied at the
knowledge-record layer instead of the decision-record layer.

**Failure handling.** An investigation that cannot independently
reproduce its own working hypothesis writes no Claim at all — the
investigation-log entry (§4.E, outcome 3/4) is the record of what was
tried and why it didn't hold up, not a new canonical Claim. A `status:
contradicted` Claim is reserved for the narrower case where the
negative result is itself a substantive fact requiring preservation as
canonical knowledge (§4.E's own outcome 5) — never the default way to
record "a hypothesis turned out false," which would recreate exactly
the Claim-pollution/`find_gaps()`-noise problem this amendment exists
to avoid (flagged by this plan's own second independent review — see
§12). A `knowledge-curator` dispatch that cannot independently
re-verify a cited Evidence record (the citation doesn't resolve, the
file it points at doesn't say what it claims) recommends holding the
Claim at `evidence-gathering`/`proposed`, never `supported` — the same
three-state discipline (`candidate`/`evidence-gathering`/decided)
`planning/learnings/` already uses, reused at the Claim layer via its
own existing `status: proposed`.

**A finding that is itself a fixable defect, not an accepted
limitation** (flagged during this plan's own independent review — see
§12: this procedure is written to be reused indefinitely, and a future
self-curation finding may not resemble this phase's own dogfood target,
where new false-positive shapes are documented as a permanently-
accepted "honest, coarse" limitation rather than something to fix). In
that case, the Claim is still written and triaged exactly as above
(it is a true statement about current behaviour, regardless of whether
that behaviour is desirable) — but the disposition step (7a/7b) also
files a `planning/learnings/inbox.md` candidate, classified
`future-improvement` (routes to a `ROADMAP.md` row, per the lifecycle's
own existing destination table) or `invariant` (routes to a regression
test, if the defect is small enough to fix immediately) — never left to
sit as silently-accepted knowledge merely because it was *recorded*
accurately. This mirrors exactly how a `context-gaps` entry or a
`learnings` candidate already routes a genuine defect toward a fix
without that routing being invented new for this phase.

### 4.B Ownership summary

| Step | Owner | New role? |
|---|---|---|
| 1-2 (identify, retrieve) | lead | No |
| 3-6 (investigate, evidence, write) | `context-researcher` | No |
| 7a (independently re-verify + recommend a disposition) | `knowledge-curator` | No |
| 7b (apply the recommended disposition — edit the Claim's own `status`/`evidence_support_state`, or confirm a declined candidate's log entry) | **lead** | No |
| 8 (requery/confirm) | lead | No |

See §4.A step 7's own full specification above (inputs, reproduction
duty, disagreement handling, who may write a canonical Claim) — this
table is the summary; §4.A step 7 is the actual procedure, formalised in
full by this plan's own second amendment (see §12).

**Step 7 is two sub-steps, not one, and this split is load-bearing, not
cosmetic** — caught and fixed during this plan's own independent review
(see §12's own corrective note). `knowledge-curator.md`'s own Hard
Rules are explicit: it may write `planning/learnings/**`/`planning/
context-gaps/**`/`planning/context-observations/**`, and `planning/
knowledge/**` *only* in "packet-assembly mode" — "**never a Claim/
Evidence/Observation/Decision/Requirement record, those are
`context-researcher`'s or the human reviewer's**." `context-researcher`
already wrote the Claim (step 3-6, with `status: proposed`); it cannot
also be the one deciding its own disposition without the result being
exactly the self-grading `decisions/0084` §3 forbids. So `knowledge-
curator` independently re-verifies the cited Evidence and recommends
`supported`/`contradicted`/`retained` (step 7a) — mirroring its own
already-established `planning/learnings/` pattern exactly
("write the recommendation + a draft... the lead... finalises
high-stakes artifacts") — and **the lead** performs the actual
mechanical edit to the Claim's own `status`/`evidence_support_state`
fields (step 7b), never `context-researcher`, never `knowledge-curator`
itself. This matches this project's own real precedent, not merely a
theoretical design: `planning/knowledge/first-party-source-symbols/
CL-FPSS-007.yaml`'s own `status` field was changed to `verified` by a
real, human-reviewed commit (`73899f2`, "comparison-mode alignment
pass") — not by the comparison agent itself (`domain-skeptic.md`'s own
Hard Rules state the identical constraint: "You never write a Claim" —
confirmed by direct reading) — the lead applied that commit.

No step requires a role this project does not already have, confirmed
against the live agent roster (`ls .claude/agents/*.md` — **13** agent
definitions exist today, not the "twelve" `agent-led-development.md`
§2's own prose states; that count is itself stale and out of this
plan's own scope to correct. The substantive point — no new role is
needed — holds either way.).

### 4.C On-demand knowledge-quality validation

A new, maintainer-only, **report-only by default, `--strict` for
CI/pre-commit** script, `scripts/check_self_knowledge_quality.py`,
matching the exact existing convention and CLI shape of
`check_user_docs.py`/`check_contracts.py`/`check_knowledge_base.py`
(mechanical only, no AI call, `--strict` exits 1 on a *blocking*
finding, `(info)`-tagged findings never block). It **composes**, never
duplicates:

1. `knowledge_api.find_gaps(project_root, slug=None)`, called once,
   with **no `slug` filter** — its own existing six rules, unchanged,
   run across **every** slug in the corpus, not only slugs that already
   have an oracle contract (corrected during this plan's own second
   independent review: the original wording restricted this call to
   contract-bearing slugs, which would make `find_gaps()`'s own
   `missing_contract` rule structurally unreachable from this script).
   `find_gaps()`'s own trigger for this rule is unchanged and
   unmodified: a slug with at least one `claim`/`requirement` record at
   all and no `oracle-contract.yaml` (`has_obligations`, confirmed by
   direct reading of `src/codecompass/knowledge_api.py`).

   **`missing_contract` severity, corrected (this plan's own third
   independent review — see §12):** the real corpus, re-inspected live
   for this amendment, has **six** knowledge slugs and **one** oracle
   contract (`balance-from-spec`) — every one of the other five
   (`codecompass-domain`, `doc-origin-pinned-reference`, `first-party-
   source-symbols`, `haskell-api-surface-extraction`, `hledger-depth`)
   has `claim`/`requirement` records and no contract, so the original
   "blocking" severity would fail `--strict` against the real baseline
   immediately, including against this plan's own chosen dogfood target.
   **This script therefore reports every `missing_contract` finding as
   `(info)`, never blocking, as of today** — not as an invented
   exemption or a per-slug allowlist, but because no existing canonical
   record or accepted decision currently establishes that an oracle
   contract is a mandatory obligation for any subject other than the one
   this project has actually built one for. Confirmed by direct reading
   of `decisions/0081` §3 (Phase 82's own oracle-contract ADR): it
   explicitly defers this question — "a future phase may choose to
   require contracts project-wide once real use justifies that cost...
   not pre-committed here" — and ties its own, narrower compatibility
   exemption (for `check_verified_status_cites_passing_oracle_result`)
   to the identical mechanically-checkable condition this script reuses:
   "no contract directory exists for this slug," explicitly preferred
   there over "an ad hoc allow-list." The owning Requirement's own
   `status` (even `approved`/`implemented`/`verified`, i.e. an accepted
   obligation per `decisions/0080`'s own INTENDED predicate) is **not**,
   by itself, evidence of a contract *mandate* — confirmed directly:
   `doc-origin-pinned-reference` and `haskell-api-surface-extraction`
   both carry `status: verified`/`implemented` Requirements with no
   contract at all, and `decisions/0081` §3 names these as part of its
   own twelve-record compatibility class, not a defect. **The
   independently identifiable signal that would flip a specific finding
   to blocking**: a separately-authorised future decision (an ADR
   amending `decisions/0081` §3, or a new one) that names a specific
   subject's contract as mandatory — no such decision exists today for
   any slug, so no `missing_contract` finding is blocking today. This
   plan does not pre-build speculative machinery for that future
   decision (consistent with this plan's own "no future-proofing beyond
   what's demonstrated necessary" discipline elsewhere) — it documents,
   honestly, that the answer is currently uniform, and the script's own
   source comment states why, citing `decisions/0081` §3 directly, so a
   future reader revisiting this severity rule starts from the same
   evidence rather than re-deriving it. Still reported, never silenced
   entirely — `(info)` keeps every real contract-free obligation-bearing
   slug visible for a human/agent to judge, exactly as `check_
   knowledge_base.py`'s own 24 pre-existing informational findings
   already do for a different condition. Positive/negative test cases
   (a contract-bearing slug producing no finding at all; a
   non-contract-bearing slug with an accepted Requirement producing an
   `(info)`, non-blocking finding; a slug with only `observation`/
   `evidence` records producing no finding, since `find_gaps()`'s own
   `has_obligations` gate is unmodified): §8.
2. `knowledge_intermediate.knowledge_status(project_root)` for every
   slug — contradicted/unchecked-proposed records, concurrent-change
   conflicts, doc-grounding coverage.
3. **One genuinely new, deterministic check this script adds, by
   composition rather than a `knowledge_api.py` edit**: for every
   `claim`/`requirement` record across every slug, call `knowledge_api.
   trace_evidence()` and report any `Gap` whose own `kind ==
   "missing_evidence"` specifically — **not** every `status="gap"`
   response, since `trace_evidence()` also returns `"gap"` for
   `dangling_evidence_reference`/`dangling_dependency_reference`
   (already reported by point 1 above via `find_gaps()`'s own identical
   rules; filtering on bare `status` would double-report those,
   corrected during this plan's own first independent review — see
   §12). Closes the corpus-wide gap identified in §1 above (`find_gaps()`
   itself has no `missing_evidence` rule) by *reusing* `trace_evidence`
   externally, exactly how `check_knowledge_base.py` already composes
   `knowledge_intermediate`'s own public functions rather than adding
   to that module. **Why composition, not a `knowledge_api.py` edit**:
   Phase 84 (including its final corrective amendment) is closed; this
   plan's own explicit non-goal (§6) is "no further edit to the
   just-closed module." A future phase may decide this check belongs
   inside `find_gaps()` itself as a seventh rule — that is a separately-
   authorised decision, not pre-empted here. **Severity**: blocking
   (`--strict`) only when the subject record's own `status` is already
   decided (`supported`/`verified`/`contradicted` for a Claim;
   `approved`/`implemented`/`verified` for a Requirement) — **never**
   for `status: proposed`, which is normal, undecided workflow state,
   not yet a violation of anything (the governing prompt's own explicit
   instruction that `--strict` block only clearly established
   violations, never speculative gaps or legitimate historical
   uncertainty, applied here — corrected during this plan's own second
   independent review, see §12).
4. **A further genuinely new, deterministic check this script adds**
   (identified during this plan's own second independent review — see
   §12): an **unresolved Evidence id** (an existing record's
   `supporting_evidence`/`contradicting_evidence` citing an `EV-...` id
   that resolves to no real record anywhere — already covered,
   corpus-wide, by `find_gaps()`'s own `dangling_evidence_reference`
   rule, point 1 above) is a *different* failure from **an Evidence
   record whose own `test_ref` field points at a result file that is
   missing, unreadable, or fails `oracle.parse_oracle_result()`** — the
   Evidence record itself resolves fine; it is the *file it cites* that
   is broken. Confirmed by direct reading that no existing mechanism
   detects this specifically: `knowledge_api.find_gaps()`'s own
   `stale_test_citation` block and `derive_epistemic_profile()` both
   silently skip a missing or unparseable `test_ref` file rather than
   reporting it; `scripts/check_knowledge_base.py::check_verified_
   status_cites_passing_oracle_result` explicitly defers this to
   `check_contracts.py` in its own source comment, but `check_
   contracts.py`'s own result-schema check (`check_result_schema`)
   validates every file already present under `planning/contracts/
   <slug>/results/*.yaml` — it never walks *from* an Evidence's own
   `test_ref` field, so a `test_ref` pointing outside that glob, or at a
   path that was never created, is checked by nothing today. This
   script closes exactly that narrow gap: for every `test`-kind Evidence
   record across every slug, resolve its own `test_ref` path under
   `project_root`; report a finding (**blocking**, `--strict` — always a
   real, present problem regardless of the citing record's own status)
   if the path does not exist, or exists but raises `oracle.
   OracleSchemaError` when parsed. A `test_ref` that resolves and parses
   cleanly is unaffected by this check regardless of its own
   `outcome`/`effective_outcome` (that is `find_gaps()`'s own
   `stale_test_citation` concern, point 1, not this one). Positive/
   negative test cases: §8.
5. **Deterministic-only duplicate/overlap detection, refined** (the
   governing prompt's own §6.C point 6; **corrected during this plan's
   own second independent review — see §12**). The original version
   flagged any two Claims in the same slug sharing an identical
   `supporting_evidence` set, including when that set was **empty** —
   which would flag every pair of unrelated, not-yet-evidenced
   `status: proposed` Claims in a slug as "duplicates" on the strength
   of both having cited nothing yet. Corrected to the governing
   prompt's own explicit refinement, applied exactly:
   - **Normalised statement equality** (byte-identical `statement`
     field after whitespace normalisation) is a candidate-duplicate
     signal on its own, `(info)`, regardless of each Claim's own
     evidence.
   - **Non-empty, identical `supporting_evidence` sets** (order-
     independent) are a *possible-overlap* signal, `(info)` — never
     conclusive duplication on their own, since two Claims can cite the
     same Evidence for genuinely different assertions.
   - **Empty evidence sets never generate a duplicate/overlap finding
     by themselves** — two `status: proposed`, not-yet-evidenced
     Claims sharing nothing (because neither has cited anything yet)
     are not flagged; only the normalised-statement-equality signal
     above can fire for such a pair, and only if their `statement`
     fields are themselves identical.
   - **Two Claims that are semantically different despite sharing the
     same Evidence remain distinguishable** — the possible-overlap
     signal is explicitly advisory, never merged/auto-resolved by this
     script, precisely so this case is never silently collapsed.
   - **True semantic overlap** (two differently-worded Claims about the
     same underlying fact, sharing no evidence or a disjoint evidence
     set) stays out of scope for mechanical detection entirely — it
     would require embedding similarity or an AI call, excluded by this
     project's own "no unnecessary AI inference" (`planning/v2-
     roadmap.md` Phase 85 point 6/`decisions/0085`'s carried-forward
     exclusion), and is left to `knowledge-curator`'s own existing
     human/agent judgment at triage time (§4.A step 7a), same as today.
   Both signals are always `(info)`, never `--strict`-blocking — neither
   is a violation of an established obligation, only a prompt for
   human/agent judgment. Negative-control tests for every bullet above:
   §8.

**Finding identity, deduplication, and severity** (governing prompt
§4.C): every finding this script emits uses the exact `Finding(rule,
message, strict: bool)` dataclass shape `check_knowledge_base.py`/
`check_contracts.py` already use (confirmed by direct reading), never a
parallel shape. Deterministic finding identity is `(rule, subject_id, a
short, stable detail fingerprint)` — re-running the script against
unchanged corpus state reports exactly the same findings, byte-
identically, never a reshuffled or duplicated set (tested explicitly,
§8). **`--strict` blocks only clearly established violations of an
existing obligation**: `dangling_evidence_reference`/`dangling_
dependency_reference` (point 1 — a declared citation resolving to
nothing is always a real defect, regardless of contract status); the
new corpus-wide `missing_evidence` composition (point 3), gated to
decided-status records only, as specified there; and the new
missing/malformed `test_ref` file check (point 4), always blocking.
**`missing_contract` (also point 1) is the one exception, `(info)`
always, per this script's own corrected severity rule above** — unlike
the other five `find_gaps()` rules, it does not represent an
established violation today (no existing decision mandates a contract
for any subject but `balance-from-spec`), so this script downgrades it
from `find_gaps()`'s own undifferentiated gap-reporting into an
advisory finding rather than inventing a blocking condition the project
has never actually decided on. Every duplicate/overlap signal (point 5)
and every `knowledge_status()`-sourced finding (point 2, already
informational by that function's own existing design) also stays
`(info)`, never blocking. This mirrors `check_contracts.py`/`check_
knowledge_base.py`'s own existing severity convention exactly (both
already distinguish blocking from informational findings within one
rule's own output, e.g. `check_knowledge_base.py`'s own `knowledge-
base-snapshot-current-divergence` findings) — no new severity vocabulary
is introduced.

Discrepancies between an accepted Decision, a recorded implementation
fact, and current verification (the governing prompt's own §6.C last
bullet) are **already** covered by the existing four-predicate model
(§1) — `epistemic_status()` surfaces INTENDED≠VERIFIED directly per
record; this script adds no new predicate, only a corpus-wide scan
reporting every record where they disagree, via the same composition
pattern as point 3 above.

Runnable on demand (`python scripts/check_self_knowledge_quality.py
[--strict]`), outside any dedicated phase run, exactly like its three
siblings — satisfying the governing prompt's own explicit requirement
that this check not be tied to a phase-run cadence.

### 4.D Preserving epistemic independence (circularity)

**Corrected overstatement** (this plan's own second independent review
— see §12): the original wording claimed the record schema itself
structurally prevents an unevidenced Claim from existing. This is
inaccurate, confirmed by direct reading of `scripts/check_knowledge_
base.py`'s own `_REQUIRED_FIELDS["claim"]`: `supporting_evidence` must
be *present* as a field (and, per `check_list_fields_are_inline`, in
the inline-list form), but an empty list (`supporting_evidence: []`)
is syntactically and semantically valid — a `status: proposed` Claim
with zero cited evidence is a real, legitimate, existing corpus state
(the normal condition of a Claim that has not yet been through step 7's
adjudication), not a schema violation. The schema's own required-field
check cannot and does not, by itself, stop an agent from writing a
Claim whose `statement` asserts something true-sounding while its own
`supporting_evidence` stays empty.

**What actually provides the guarantee is procedural, not structural**:
`knowledge-curator`'s own independent re-verification (§4.A step 7a,
formalised in full there) checks the *citation*, not the Claim's own
prose, before recommending any disposition — and **no Claim is
promoted past `status: proposed` without that independent check having
run and reproduced real evidence**. `context-researcher`'s own
definition requires Observations before Evidence before Claims (step 3
of its own brief), which keeps an *honestly-written* Claim's own
evidence real, but does not, on its own, stop an un-evidenced or
dishonestly-evidenced Claim from being *written* — only the
adjudication step (7a/7b) stops it from being *accepted*. This
distinction is demonstrated in practice, not merely asserted, by this
very session's own repeated independent re-verification of findings
(direct hash comparisons, direct source re-reads, direct test
re-execution) rather than trusting any prior agent's or retro's
self-report, including correctly overturning a prior "no new candidate
learning" self-report on two separate occasions this session. A
self-curation pass's own narrative is never *accepted* as its own
evidence — not because the schema cannot hold prose (it can, in
`statement`), but because promotion requires an independent, reproduced
citation every time, with no exception for a self-curation finding
specifically.

### 4.E Candidate-disposition procedure (five outcomes, one
investigation log, no new record kind)

**Material defect, found by this plan's own first independent review**
(see §12's first corrective note) **and the subject of this plan's own
second, targeted amendment** (governing prompt: "CodeCompass
Orchestrator — Amend Phase 85 Plan and Revalidate"): the original
version conflated a **candidate rejected during review** with a
**canonical Claim whose substantive assertion is contradicted**,
directing every unsuccessful hypothesis toward a `status: contradicted`
Claim. Recording every unsuccessful hypothesis this way pollutes the
knowledge model (a Claim record for a hypothesis nobody needs to query
again) and generates persistent, meaningless `find_gaps()`/
`knowledge_status()` noise (a `contradiction` gap for a Claim whose
only content is "this specific guess didn't pan out").

**Five outcomes, not two:**

1. **Accepted new knowledge** — a genuinely new, previously-unrecorded,
   independently-reproduced fact. Written as a `CL-`/`DE-` pair (§4.A
   step 3-6), promoted via §4.A step 7.
2. **Duplicate or already-known** — the investigation confirms an
   existing, unsuperseded Claim already says this. Nothing new is
   written under `planning/knowledge/`; the investigation-log entry
   (below) records that the existing `CL-...` id was checked and
   matches.
3. **Falsified hypothesis** — a specific, testable guess was tried for
   real and found false (e.g. "a tab-indented declaration is never
   matched" — tried, and it is matched). Recorded in the investigation
   log only, with the real probe's own output as evidence. **Not** a
   Claim, unless outcome 5 applies.
4. **Insufficiently supported candidate** — the investigation could not
   independently reproduce enough evidence to conclude either way (a
   plausible-looking construct that, on inspection, cannot be
   constructed as a clean test case; an ambiguous result). Recorded in
   the investigation log with the specific gap in evidence named; never
   written as a Claim of any status, since there is nothing
   proposition-shaped yet to assert.
5. **Genuine contradictory knowledge requiring reconciliation** — the
   investigation's negative result is not merely "this guess was
   wrong" but **itself overturns or qualifies an existing, still-live
   Claim's own assertion** — a substantive fact the corpus would be
   wrong without. This is the *only* outcome written as a `status:
   contradicted` Claim, citing the prior Claim and the new
   contradicting Evidence, exactly as `context-researcher` already does
   for external projects. The test for "substantive": would a future
   reader of the prior Claim alone be actively misled without this
   correction? If the answer is no (the prior Claim already correctly
   says "unknown" or makes no claim this result bears on), the finding
   is outcome 3 or 4, not 5.

**The investigation log.** Outcomes 2-4 (and outcome 5's own negative
evidence, alongside the Claim it attaches to) are recorded in a
durable, append-only Phase 85 investigation log —
`planning/retros/phase-85-self-curation-investigation-log.md` — reusing
this project's own existing `planning/retros/` convention (the same
append-only discipline `_audit-phase-84.md` already demonstrates across
this session's own multiple audit passes) rather than introducing a new
canonical knowledge-record kind, per the governing prompt's own
explicit instruction. One entry per investigated candidate, in the same
spirit as `planning/learnings/inbox.md`'s own template, with these
required fields:

| Field | Required | Notes |
|---|---|---|
| `id` | yes | `SCI-NNN` (Self-Curation Investigation), stable, never reused |
| `hypothesis` | yes | the specific, falsifiable question investigated, in the researcher's own original words |
| `investigation_scope` | yes | what was examined (files, functions, constructs tried) and the CodeCompass `repository_revision` investigated against |
| `evidence` | yes | every command run / file:line read / probe constructed, with its real output — independently reproducible by a later reader, not paraphrased |
| `reviewer` | yes | who performed the independent §4.A step 7a reproduction (`knowledge-curator` dispatch, or the lead) |
| `disposition` | yes | one of: `accepted` / `duplicate` / `falsified` / `insufficient` / `contradicts:<CL-id>` |
| `reason` | yes | why this disposition, in one paragraph |
| `related_knowledge` | no | any existing `CL-`/`REQ-`/`EV-` id this investigation checked against or bears on |

**Provenance and idempotency.** A log entry is append-only, like every
sibling artifact this project already keeps this way (`promoted.md`,
`_audit-phase-84.md`) — never edited to change a past disposition; a
later investigation that revisits the same hypothesis adds a new entry
rather than rewriting the old one, and may cite the prior entry's own
`id` directly. Re-running the exact same investigation when nothing has
changed produces no new log entry at all (§4.A step 4's "duplicate/
already-known" check applies to a log entry exactly as it already does
to a Claim) — confirmed, not merely asserted, by this plan's own
verification table (§8).

**Never create unattached Evidence merely to make a rejection appear
represented in canonical knowledge.** An `EV-` record is only ever
written when it is cited by a real Claim (outcome 1/5) — a rejection
(outcome 2/3/4) is represented by the investigation log alone, never by
an orphaned Evidence record with nothing pointing at it, which would
itself be exactly the kind of knowledge-model pollution this procedure
exists to avoid.

---

## 5. Data flow and evidence/provenance handling

```
ordinary development work
        │
        ▼
lead identifies a bounded question  ──►  knowledge_api.search/get/
        │                                 find_gaps/epistemic_status
        │                                 (what's already known/unsure)
        ▼
context-researcher dispatch
    OBS-<slug>-NNN (dated act of looking: file read, command run)
        │
        ▼
    EV-<slug>-NNN (neutral package of Observations)
        │
        ▼
    working hypothesis, checked against §4.E's five outcomes
        │
        ├──► (1) new            → CL-<slug>-NNN + DE-<slug>-NNN (status: proposed)
        ├──► (2) duplicate      → investigation log only, cites existing CL- id
        ├──► (3) falsified      → investigation log only
        ├──► (4) insufficient   → investigation log only
        ├──► (5) contradicts    → CL-<slug>-NNN (status: contradicted) + DE-,
        │                          citing the prior CL- id and the new Evidence
        │
        └──► process-lesson (if any) → planning/learnings/inbox.md (separate pipeline)
        ▼
knowledge-curator independent adjudication (§4.A step 7a)
    reproduces source_read/doc_read evidence directly (Read/Grep/Glob);
    directs the lead to re-run executable/test_run evidence verbatim
    (no Bash of its own) and incorporates the real output; never trusts
    the citing record's own prose
        │
        ├──► recommend: promote  (CL- → status: supported/contradicted)
        ├──► recommend: hold     (CL- stays status: proposed /
        │                          investigation-log entry stays open)
        └──► recommend: confirm  (investigation-log entry for outcome 2-4
                                    is complete and evidenced)
        ▼
lead applies the recommended disposition (§4.A step 7b) -- the only role
that edits a canonical Claim's own status/evidence_support_state
        ▼
lead requeries knowledge_api against the updated slug
    confirms get()/trace_evidence()/find_gaps() reflect the outcome, and
    (for outcome 2-4) that planning/knowledge/ itself is untouched
```

Provenance is carried exactly as the existing schema already requires:
`derived_by` (which agent/process), `repository_revision` (the
CodeCompass git SHA the finding is *about*, pinned — not the SHA at
triage time), `timestamp`. A Claim's `supporting_evidence`/
`contradicting_evidence` are the only legitimate route to "this is
true" — never the Claim's own `statement` prose standing alone. The
investigation log (§4.E) carries the equivalent provenance for a
declined candidate: its `investigation_scope`'s own pinned revision,
`reviewer`, and `evidence` fields serve the identical purpose one layer
down, for a finding that never becomes a canonical record at all.

---

## 6. Exact deliverables and minimal interfaces

1. **A workflow document**, `docs/workflows/self-curation-loop.md`,
   describing the 8-step loop (§4.A), the five-outcome disposition
   procedure (§4.E), and the independent-adjudication contract (§4.A
   step 7) for a future lead/agent to follow — prose and a short
   checklist, not new code. (Matches the existing `docs/workflows/
   knowledge-reconciliation-loop.md`'s own role and placement for the
   Stage-1/2/3 manifest pipeline.)
2. **`planning/retros/phase-85-self-curation-investigation-log.md`**
   (§4.E) — the one new planning-doc artifact this phase introduces, an
   append-only investigation log, **not a canonical knowledge-record
   kind**, created empty and populated with real entries during the §7
   dogfood run.
3. **`scripts/check_self_knowledge_quality.py`** (§4.C) — the one new
   script this phase introduces, composing existing `knowledge_api`/
   `knowledge_intermediate`/`oracle` functions, following `check_
   knowledge_base.py`'s own exact `--strict`/report-only/`Finding`
   convention.
4. **A demonstrated dogfood pass** (§7) against a real, bounded,
   first-party slice of CodeCompass's own `planning/knowledge/`
   corpus — not a synthetic fixture — producing **both** required
   outcomes the exit gate (§9) demands: written up as its own section
   of this phase's retro, with real commit hashes, real record ids, and
   real investigation-log entry ids, not a narrative summary.
5. **No change** to `src/codecompass/knowledge_api.py`, `oracle.py`,
   `knowledge_intermediate.py`, or any canonical record schema.

Minimal interface for the new script (mirrors its three siblings):

```
python scripts/check_self_knowledge_quality.py [--strict]
```

No new CLI command under `codecompass knowledge *` — this is a
maintainer-only tool exactly like its siblings, not a shipped product
feature (consistent with `check_knowledge_base.py`'s own "Not shipped,
not a `codecompass` subcommand" framing).

---

## 7. Real CodeCompass dogfood design

**Both outcomes are independently mandatory** (corrected during this
plan's own second independent review — see §12: the original version
treated a genuine positive outcome *or* a genuine negative outcome as
individually sufficient, and allowed a synthetic negative control to
substitute for the real one if the investigation happened to land
positive. Neither is acceptable against the roadmap's own exit gate,
which requires both a promoted finding *and* a declined candidate, each
independently investigated.) **A synthetic negative control (e.g. a
deliberately false hypothesis tried only to exercise the validator/test
suite) can satisfy an automated unit test (§8) but never this real-
dogfood exit gate** — the gate exists specifically to prove self-
curation can say no to a *real* candidate that arose from genuine
investigation, not to a contrived one invented to be rejected.

**Selected target: `planning/knowledge/first-party-source-symbols/`**
(Phase 77's `source_symbols.py` regex-based Rust/TypeScript extraction),
specifically extending `CL-FPSS-007`'s own already-recorded,
already-open question — **preferred, unchanged from the original
version**, for the same three reasons already established below.

**Why this slug, against the governing prompt's own three criteria:**

- **Observable coverage.** 74 existing records, a real `DE-FPSS-007`
  derivation chain, and an already-established "real probe" evidentiary
  convention (`EV-FPSS-008`: "a Rust file containing `r#"...embedded_in_
  string()...}"#;` produces a real false-positive row" — a literal,
  reproducible, executable probe, not a hypothetical). A new
  investigation in this slug inherits a proven, concrete evidentiary
  pattern to follow rather than inventing one.
- **Tractability.** `source_symbols.py`'s two regex extractors are
  small, fast, deterministic, and directly runnable against a
  hand-written fixture file in minutes — no external checkout, no
  oracle contract, no network access needed (unlike, say, a Ledgerkit-
  dependent finding).
- **Opportunity for a genuinely new finding.** `CL-FPSS-007`'s own
  `open_questions` field, read directly, states: *"whether these two
  specific false-positive shapes (multi-line raw strings, plain block
  comments) are the ones `decisions/0065`'s own prose intended to
  describe, or merely two of possibly several unenumerated ones, could
  not be determined from the documents alone."* This is a live,
  self-declared, unresolved question already on file — not invented for
  this plan — inviting a bounded follow-up investigation: are there
  further ordinary (not contrived-adversarial) Rust/TypeScript
  constructs that defeat either extractor's coarse, line-anchored regex
  approach, beyond the two already-documented shapes?

**Planned investigation shape, scoped to produce both outcomes from
genuine investigation, pre-registered before either result is known**:
a bounded `context-researcher` dispatch tries **several** (not one)
ordinary Rust/TypeScript constructs against the real, unmodified
extractor functions (`_extract_rust_source_symbols`/`_extract_js_
family_source_symbols`, `_RUST_ITEM_RE`/`_JS_FAMILY_ITEM_RE`, confirmed
by direct reading of `src/codecompass/source_symbols.py`, unchanged by
any Phase 83/84 work — last touched by its own Phase 77 implementation
commit, `03f8519`) — e.g. a Rust `#[cfg(test)]`-gated declaration, a
doc-comment-embedded declaration-like line, a TypeScript decorator-
prefixed declaration, and a declaration split by a line continuation
inside a macro — precisely *because* trying several genuinely different
constructs makes it plausible, without pre-committing to which, that
some defeat the extractor (candidate outcome 1, §4.E) and others do not
(candidate outcome 3, §4.E) **within the same bounded investigation** —
each construct is a separate, independently falsifiable sub-question,
not a single pass/fail experiment.

**Bounded extension, scoped before the result is known.** If this one
investigation's own real results do not yield both a genuine outcome-1
finding and a genuine outcome-2/3/4 decline (e.g. every construct tried
turns out to defeat the extractor, or every one is handled correctly),
this plan pre-authorises exactly **one** further, equally bounded
`context-researcher` dispatch against one of the three confirmed-
tractable alternate slugs named below, with its own scope recorded in
the investigation log (§4.E) *before* that second dispatch runs and
*before* its outcome is known (the governing prompt's own explicit
instruction: "scope and rationale recorded before the outcome is
known") — never chosen or retargeted after seeing a disappointing first
result. No further extension beyond this second, pre-authorised one is
in scope; a second inconclusive result is reported honestly as the exit
gate not met (§9 point 5), not chased with a third attempt.

**Confirmed tractable corpus breadth** (not cherry-picked), available
for the one pre-authorised extension above: `planning/knowledge/
codecompass-domain/` (186 records, the adapter/context-graph/evidence-
model domain), `planning/knowledge/haskell-api-surface-extraction/`
(43 records, the Haskell adapter's own export-list parsing),
`planning/knowledge/doc-origin-pinned-reference/` (32 records, the
`doc_artifacts.origin` schema field, resolving context-gap `CG-005`).

**Positive outcome, independently auditable evidence**: a new
`OBS-FPSS-NNN`/`EV-FPSS-NNN` pair plus either a new `CL-FPSS-NNN` (if
it's a genuinely distinct shape) or an update path for `CL-FPSS-007`
itself via `supersedes` (if it's best understood as sharpening the same
claim) — `knowledge-curator` decides which, same as any other triage —
each citing the real probe's own reproducible output (a real file, a
real extractor invocation, a real resulting row), independently
re-run — at `knowledge-curator`'s own explicit direction, by the lead,
since the probe is `executable`-kind evidence and `knowledge-curator`
has no `Bash` of its own (§4.A step 7a's corrected tool-boundary split)
— at step 7a, not merely re-read, and re-run again by `release-phase-
auditor` at closeout (§11).

**Negative outcome, independently auditable evidence**: a real
investigation-log entry (§4.E, `SCI-NNN`) for a specific, named
construct that was genuinely tried and found *not* to defeat either
extractor (the extractor turns out robust against the specific
construct tried, or a construct that looked plausible on paper doesn't
actually reproduce when tried for real) — citing the real probe's own
output showing correct extraction, with the lead's own re-run of that
exact probe, at `knowledge-curator`'s own explicit direction, recorded
in the entry's `reviewer`/`evidence` fields. **This is an outcome-3
(falsified) or
outcome-4 (insufficient) disposition per §4.E, never a `status:
contradicted` Claim** — a robust extractor behaving correctly is not a
fact that contradicts any existing Claim; it is simply a tried
hypothesis that didn't pan out, recorded in the investigation log, not
a new canonical record (§4.E's own distinction, corrected by this
amendment).

If neither outcome is cleanly reached even after the one pre-authorised
extension, this plan requires that to be reported honestly as the exit
gate not met (§9 point 5), per the governing prompt's own explicit
instruction — not manufactured into an artificial PASS, and not patched
over with a synthetic negative control.

---

## 8. Tests, negative controls, and validation commands

| Control | How exercised |
|---|---|
| Evidence-based promotion | The dogfood's own positive-outcome branch (§7) — real, independently re-verified Evidence, a real `knowledge-curator` disposition, applied by the lead (§4.A step 7b). |
| Correct, genuine rejection of an unsupported finding | **The dogfood's own negative-outcome branch (§7) — mandatory, not optional.** A real investigation-log entry for a real, genuinely-tried construct that turned out not to defeat the extractor, independently re-run by the lead at `knowledge-curator`'s own explicit direction (§4.A step 7a's tool-boundary split). A synthetic negative control (a deliberately false hypothesis tried only to exercise the test suite) is retained **only** as an automated unit test for the script itself (next rows), never as a substitute for this real-dogfood control (corrected during this plan's own second independent review — see §12). |
| `missing_contract` reachability and corrected severity | A constructed fixture slug with a `claim`/`requirement` record and no `oracle-contract.yaml` → `find_gaps()` reports `missing_contract` through the unmodified script call (§4.C point 1), and the script reports it as `(info)`, never blocking under `--strict` (the corrected severity rule). **Real-baseline check**: run against the actual corpus, confirm all five real contract-free slugs (`codecompass-domain`, `doc-origin-pinned-reference`, `first-party-source-symbols`, `haskell-api-surface-extraction`, `hledger-depth`) each produce an `(info)` `missing_contract` finding and `--strict` still exits 0 for this rule specifically. **Negative control (reachability)**: a constructed fixture slug with only `observation`/`evidence` records and no contract → no `missing_contract` finding at all (confirms the `has_obligations` gate, not merely that the rule fires at all). **Negative control (contract-bearing)**: `balance-from-spec` (the one real contract-bearing slug) → no `missing_contract` finding. |
| Missing/malformed `test_ref`-cited result file | A constructed `test`-kind Evidence record whose `test_ref` points at a nonexistent file → the new check (§4.C point 4) reports it, blocking under `--strict`. A second fixture whose `test_ref` points at a file that exists but fails `oracle.parse_oracle_result()` → reported identically. **Negative control**: a `test_ref` pointing at a real, well-formed result file → no finding, regardless of that result's own `outcome`/`effective_outcome` (which is `find_gaps()`'s own `stale_test_citation` concern, not this check's). |
| Duplicate/overlap detection, refined (§4.C point 5) | Five fixtures, one per §4.C.5's sub-rule: (a) two Claims, identical normalised `statement`, different evidence → flagged `(info)`; (b) two Claims, non-empty identical `supporting_evidence` sets, different statements → flagged `(info)` as possible-overlap, not asserted as conclusive; (c) two Claims, both `supporting_evidence: []`, different statements → **no** finding from the empty-set rule (the statement-equality rule may still independently fire if the statements genuinely match); (d) two Claims, same non-empty evidence set, genuinely different statements → confirmed to remain two separate, undisturbed records (the possible-overlap signal is advisory only, never merges/auto-resolves them); (e) true semantic overlap with disjoint evidence and different wording → confirmed **not** flagged by this script at all (explicitly out of mechanical scope, left to `knowledge-curator` triage). |
| Independent Claim adjudication, disagreement handling | A constructed fixture where a cited `OBS-`/`EV-` record's own file no longer says what a draft Claim claims → the independent-reproduction step (§4.A step 7a) reports "could not reproduce," and the recommended disposition is "hold," never "promote" — exercised as a dry run against a deliberately stale fixture, distinct from the real dogfood run. |
| Observation-method reproduction classification (§4.A step 7a's taxonomy) | A dry-run procedure check, one fixture per real corpus method value: `source_read`/`doc_read`/`code_read` → reproduction path is "knowledge-curator, directly" (no "lead: run" line emitted); `grep_search` → reproduction path is "knowledge-curator, directly, via Grep" (no "lead: run" line emitted); `executable`/`targeted_probe`/`test_run`/`test_execution`/`static_analysis` → reproduction path emits an explicit "lead: run `<command>` to confirm" line, never executed by `knowledge-curator` itself. **Negative control**: a fixture Observation with a deliberately unrecognised `method` value (e.g. `method: inferred_from_memory`) → classified "unknown," recommended disposition is "hold," never silently treated as reproduced or promoted. |
| Context-researcher deferred-write mode (§4.A step 3) | A dry-run self-curation dispatch that lands on outcome 3 (falsified) → confirm no `OBS-`/`EV-` file appears under the investigated slug's own `planning/knowledge/<slug>/` directory at any point (`git status`/`git diff --stat` both empty for that path), and the full reproducible content (command, output, revision) is present in the agent's own returned report. **Contrast**: the same dispatch mechanics landing on outcome 1 (new) → the `OBS-`/`EV-`/`CL-`/`DE-` set *is* written, confirming the deferred-write mode only suppresses the write for a declined candidate, never for a genuine finding. |
| Finding identity and determinism | `scripts/check_self_knowledge_quality.py` run twice in immediate succession against unchanged corpus state reports byte-identical output both times — no reordering, no duplication, no spurious new finding from the act of running it. |
| Contradictory and stale knowledge | `find_gaps()`'s existing `contradiction`/`stale_test_citation` rules, reused unchanged — no new test needed, already covered by `tests/test_knowledge_api.py`. |
| Cross-record provenance | `get_context_packet()` on the newly-promoted Claim, confirming `via_claim`/`role` detail (Phase 84 final amendment) correctly traces back to its own Evidence. |
| Current vs. historical verification | If the dogfood finding cites a Phase 83 oracle result, `evaluate_result_precedence(..., repo_root=...)` reused unchanged — never a new verification mechanism. |
| Repeated runs without duplicate promotions or log entries | Re-run the exact §4.A.2 retrieval after the dogfood completes; confirm a second, identical investigation (run again) recognises the finding as already-known (outcome 2, §4.E) and writes neither a new Claim nor a new investigation-log entry — demonstrated, not merely asserted. |
| Safe handling of missing/inaccessible evidence | `scripts/check_self_knowledge_quality.py` run against a slug with a dangling `test_ref`/`supporting_evidence` id (reuses `find_gaps()`'s existing `dangling_evidence_reference`/`dangling_dependency_reference` coverage — no new code path for those two; the new `test_ref`-file check, above, is the one genuinely new path). |
| Preservation of existing canonical knowledge | `git diff --stat` after the dogfood run: every file outside the newly-added record(s)/investigation-log entry for the targeted slug is untouched; no *already-decided* Claim (one not freshly written by this same investigation) is edited in place — an already-decided Claim is only ever superseded, per §4.A's idempotency rule. (Distinct from, and not in conflict with, step 7b's one-time disposition edit to the *freshly-written, not-yet-decided* `status: proposed` Claim from the same investigation.) |
| On-demand check outside a phase run | `python scripts/check_self_knowledge_quality.py --strict` invoked standalone, in this plan's own verification section (§11), with no phase-specific setup. |

Validation commands for implementation time: `pytest tests/
test_check_self_knowledge_quality.py` (new, mirroring `tests/
test_check_knowledge_base.py`'s own existing structure — confirmed
present, by direct `ls tests/` during this plan's own research,
alongside `test_check_contracts.py`/`test_check_user_docs.py`; every
sibling validator has a dedicated test file, so this one does too, not
an open question); the complete CodeCompass suite; `scripts/check_
user_docs.py --strict` (hygiene for any new `planning/learnings/`
entries the dogfood's own retro surfaces).

---

## 9. Falsifiable acceptance criteria and exit gates

Reusing the roadmap's own exit gate verbatim, made concrete:

1. **At least one real, previously-unrecorded fact about CodeCompass's
   own implementation is correctly promoted into canonical knowledge
   with independent evidence** — a real new `CL-FPSS-NNN` (or
   equivalent, if the dogfood uses the one pre-authorised bounded
   extension, §7), `knowledge-curator`-triaged (independently
   reproducing the cited evidence, §4.A step 7a), applied by the lead
   (step 7b), with `release-phase-auditor` re-confirming the same
   reproduction at closeout. **Mandatory on its own — not satisfied by
   outcome 2 below.**
2. **At least one real, genuinely-investigated candidate is correctly
   declined, with a recorded reason, as a real investigation-log entry
   (§4.E)** — the candidate must have arisen from the same genuine
   investigation discipline as outcome 1 (a specific construct actually
   tried against the real extractor, not a hypothetical). **Mandatory
   on its own, independently of outcome 1, and never satisfiable by a
   synthetic negative control** (corrected during this plan's own
   second independent review — see §12).
3. **Both arise through the existing, unmodified lifecycle, correctly
   classified per §4.E's five outcomes** — no new promotion path, no
   new canonical record kind (the investigation log is a planning-doc
   artifact, not a knowledge-record kind), no weaker bar, and no
   contradicted-Claim pollution from a merely-falsified hypothesis
   (§4.E's own narrow exception for outcome 5 only).
4. **The on-demand quality check runs standalone and reports real
   findings against the real corpus**, with its new rules (§4.C points
   3-5) demonstrated to detect at least one real finding of each kind if
   one genuinely exists in the corpus at implementation time (or an
   explicit, honest "none found" if it does not — never a staged
   positive), and with severity correctly distinguishing blocking from
   advisory per §4.C's own closing severity spec.
5. **If 1 and 2 cannot both be genuinely achieved — including after the
   one pre-authorised bounded extension (§7) — this phase reports its
   exit gate as not met**, explicitly, in the closeout report, naming
   which half failed and why, per the governing prompt's own
   instruction. This is not treated as a planning failure; it is the
   honest outcome the gate exists to allow.

---

## 10. Risks, mitigations, trade-offs, and explicit non-goals

**Risks (named by the governing prompt itself):**

- **Circularity** — a self-curation agent's own assertion mistaken for
  verification. Mitigated procedurally (§4.D, corrected — not by a
  schema-level impossibility, which does not exist): **no Claim is
  promoted past `status: proposed` without `knowledge-curator`'s own
  independent reproduction of the cited evidence**, and the lead never
  overrides a documented disagreement without its own independent
  re-reproduction (§4.A step 7a).
- **Knowledge-model pollution from recording every falsified hypothesis
  as a canonical Claim.** Mitigated by §4.E's five-outcome disposition
  procedure and the investigation log — only a genuinely substantive
  contradiction (outcome 5) ever becomes a `status: contradicted` Claim;
  a merely-falsified or insufficiently-supported guess never enters
  `planning/knowledge/` at all (this plan's own second independent
  review finding — see §12).
- **The dogfood finding nothing genuinely new, or nothing genuinely
  rejectable.** Mitigated by selecting a target with an already-
  declared open question (§7), trying several genuinely different
  constructs (not one) within the bounded investigation so both a
  positive and a negative result are plausible from the same run, and
  by the one pre-authorised bounded extension if the first investigation
  doesn't yield both; if it still yields less than both, §9 point 5
  applies honestly rather than forcing a result or substituting a
  synthetic control.
- **Scope creep into Phase 86/87/88's own territory** (placement
  policy, documentation compilation, MCP). Mitigated by the explicit
  non-goals below, checked against this plan's own deliverables list
  (§6) before implementation begins.

**Trade-offs:**

- The new quality-check script (§4.C) duplicates *no* logic from
  `knowledge_api.py`/`knowledge_intermediate.py` by calling them
  externally, at the cost of being a thin, separate maintainer script
  rather than a first-class `codecompass knowledge` subcommand. Accepted
  — matches this project's own existing convention for this class of
  tool (`check_contracts.py`/`check_knowledge_base.py` are neither
  shipped nor subcommands either), and avoids reopening the just-closed
  `knowledge_api.py` module for a capability its own plan never
  originally scoped.
- Duplicate/overlap detection is deliberately shallow (exact-match only,
  §4.C.5) rather than semantic. Accepted — the alternative requires
  either an AI call (excluded) or a hand-rolled similarity heuristic
  with its own unbounded false-positive surface; `knowledge-curator`'s
  existing human/agent judgment already covers the semantic case at
  triage time.

**Explicit non-goals** (the governing prompt's own §7 list, restated
against this plan's actual deliverables so each is independently
checkable at closeout):

- No change to the evidence bar or promotion criteria — confirmed: §4.A
  step 7 uses the Claim's own existing `status`/`evidence_support_state`
  fields and `knowledge-curator`'s own existing triage discipline.
- No new canonical storage system or record kind — confirmed: §1/§3.
- No continuously running background-curation service — confirmed: §4.C
  is explicitly on-demand, invoked manually or at a phase/PR boundary,
  never a daemon.
- No automatic, unchecked promotion of agent-generated assertions —
  confirmed: §4.A step 7 is always a `knowledge-curator` dispatch, never
  auto-applied.
- No MCP server implementation (Phase 88) — confirmed: this plan
  introduces no server, no transport, no agent-facing network surface.
- No Knowledge Placement Policy implementation (Phase 86) — confirmed:
  this plan makes no placement-policy judgment; it only runs the
  existing lifecycle once more, reflexively.
- No documentation compiler (Phase 87) — confirmed: no doc-generation
  code is added.
- No incremental documentation reconciliation implementation
  (Phase 89, née merged-old-85) — confirmed: §4.C composes existing
  `knowledge_status()`'s own doc-grounding report, adding nothing to
  how it detects doc-grounding drift.
- No cross-project semantic federation — confirmed: every operation in
  this plan targets exactly one project (CodeCompass's own `planning/
  knowledge/`), matching `decisions/0091` §4's own single-project-scoped
  posture, carried forward unchanged.
- No general-purpose autonomous development framework — confirmed: the
  workflow (§4.A) is a documented procedure for a lead to follow when
  dispatching existing, bounded agent roles, not a new orchestration
  layer or a standing loop.
- No new canonical knowledge-record kind for a declined candidate —
  confirmed: §4.E's investigation log is a planning-doc artifact
  (`planning/retros/`), the same tier `_audit-phase-84.md` already
  occupies, never a seventh record kind alongside `OBS-`/`EV-`/`CL-`/
  `DE-`/`DEC-`/`REQ-`.
- No automatic or default use of a synthetic negative control to
  satisfy a real acceptance gate — confirmed: §7/§9 require a genuine,
  real investigation for both the positive and negative dogfood
  outcomes; a synthetic control is retained only for the validator's
  own automated unit tests (§8).

---

## 11. Implementation sequence and independent audit procedure

1. Write `scripts/check_self_knowledge_quality.py` (§4.C, including the
   new `missing_contract`-reachability fix, the new `test_ref`-file
   check, and the refined duplicate/overlap detection) and its tests;
   run against the real corpus; confirm it reports real, plausible
   findings (or an honest "none") — never fabricated.
2. Write `docs/workflows/self-curation-loop.md` (§6.1) and create the
   empty `planning/retros/phase-85-self-curation-investigation-log.md`
   (§4.E/§6.2).
3. Run the dogfood investigation (§7): dispatch `context-researcher`
   against `first-party-source-symbols`, trying several genuinely
   different constructs in one bounded dispatch. If, and only if, the
   real result does not yield both outcomes, pre-register the one
   bounded extension's own scope in the investigation log *before*
   dispatching it (§7's own explicit ordering).
4. Dispatch `knowledge-curator` to independently adjudicate (§4.A step
   7a) every candidate the dogfood produced — both the promotion
   candidate and the declined candidate — reproducing cited evidence
   directly, not re-reading `context-researcher`'s own prose.
5. The lead applies each recommended disposition (step 7b); requery
   (§4.A step 8); write the retro's own dogfood section with real ids,
   real commit hashes, real investigation-log entry ids, and the real
   (not idealised) outcome for *both* required halves.
6. Run the complete CodeCompass test suite and all four strict
   validators (`check_user_docs.py`/`check_contracts.py`/`check_
   knowledge_base.py`/`check_self_knowledge_quality.py`, all `--strict`).
7. Independent `release-phase-auditor` pass against this exact plan's
   own §9 exit gate, the real commit(s), and the real dogfood outcome —
   re-deriving the verdict from the actual repository state, including
   independently reproducing the evidence behind *both* the promoted
   Claim and the declined investigation-log entry, never trusting the
   implementing agent's own report (this plan's own `CLAUDE.md` §5
   obligation, carried forward from every prior phase in this project's
   history).
8. Independent `docs-reconstructor` drift pass over any `docs/`/
   `architecture/` touched by step 1-2.
9. Correct any blocking finding from 7-8 and re-run the affected checks
   before `planning/ROADMAP.md` marks Phase 85 `done` — the same
   terminal-commit discipline (`CLAUDE.md` §5's narrow exemption) this
   session's own Phase 84 closeout twice demonstrated in practice.

---

## 12. Genuinely unresolved decisions

- **Whether a genuinely new `missing_evidence`-shaped corpus-wide rule
  (§4.C.3) eventually belongs inside `find_gaps()` itself**, once this
  phase has real experience running it externally. Deferred — not
  decided here, since Phase 84 is closed and this plan's own non-goal
  is to avoid reopening it speculatively; revisit only if real use at
  implementation time shows the external-composition approach is
  insufficient (e.g. because `find_gaps()`'s own per-record consistency
  envelope would add real value to this specific rule that the external
  script cannot cheaply replicate).
- **Whether the dogfood should target `first-party-source-symbols` or
  one of the three alternate slugs named in §7**, if implementation-time
  re-inspection shows `CL-FPSS-007`'s own open question has since been
  resolved by other work (unlikely, but not re-confirmed as of this
  plan's own writing beyond the live read performed for §1/§7). The
  implementing session should re-check `CL-FPSS-007`'s current state
  before dispatching, exactly as this plan's own research did.

## Corrective note (2026-11-02, independent planning review)

An independent review of this plan, dispatched before declaring it
implementation-ready, found one material gap and three secondary ones,
all now fixed in place above (not a separate amendment section, since
this plan was never implemented against the flawed version — there is
no "as-built" to reconcile against, unlike a post-implementation
corrective pass):

1. **[Material, now fixed]** §4.A step 7 originally assigned both
   independent re-verification *and* the mechanical disposition edit to
   `knowledge-curator` alone — but `knowledge-curator.md`'s own Hard
   Rules explicitly forbid it from writing a Claim/Evidence record.
   Split into 7a (`knowledge-curator` recommends) / 7b (the lead
   applies), confirmed against both `knowledge-curator.md`'s and
   `domain-skeptic.md`'s own write-boundary text and the real precedent
   of `CL-FPSS-007`'s own `status` history (commit `73899f2`).
2. **[Fixed]** §4.C.3's quality-check filter was specified as "any
   `trace_evidence()` response with `status="gap"`," which would
   double-report gaps `find_gaps()` already covers. Narrowed to
   `Gap.kind == "missing_evidence"` specifically.
3. **[Fixed]** §1's write-paths bullet gained an explicit reconciliation
   of `decisions/0084` §3's literal "enters the... learnings/
   context-gaps lifecycle" wording against this plan's actual design
   (a Claim's own `status: proposed` functions as that candidate state
   for a domain/implementation finding).
4. **[Fixed]** §4.A's failure-handling paragraph gained an explicit
   path for a self-curation finding that turns out to be a fixable
   defect rather than an accepted limitation — filed as an additional
   `planning/learnings/` candidate alongside the Claim, never left to
   sit as silently-accepted knowledge.

The reviewer's independent fact-checking of this plan's own specific
citations (regex names, line numbers, record contents, validator
finding counts) found all of them accurate except the "twelve-agent
roster" count (13 exist today; `agent-led-development.md` §2's own
prose is itself stale on this point, out of this plan's scope to
correct) — corrected in §4.B.

## Corrective note (2026-11-02, second independent review — "CodeCompass
Orchestrator — Amend Phase 85 Plan and Revalidate")

A second, targeted amendment — triggered by a separate governing prompt
identifying six material issues in the then-current version — rewrote
§§4.A step 4/6/7, 4.B, 4.C, 4.D, added a new §4.E, and rewrote §§5, 6, 7,
8, 9, 10, 11 (full detail in the amendment itself, summarised at the top
of this file). A fresh independent review was dispatched against the
amended plan specifically to verify all six fixes and check for any new
contradiction. **Verdict on first pass: NOT READY** — all six original
issues were confirmed genuinely fixed, but the review found one new,
material issue this second amendment itself introduced:

5. **[Material, now fixed]** §4.A step 7a's "evidence the reviewer must
   reproduce" bullet assumed `knowledge-curator` could itself re-run a
   command/probe/test — but `knowledge-curator`'s own real tool list
   (`Read, Grep, Glob, Edit, Write`) has no `Bash`, confirmed against its
   own existing Hard Rule ("You have no Bash... trace the check logic by
   hand, then end your report with an explicit 'lead: run `<command>` to
   confirm' line. The lead runs it."). As written, this made the
   independent-adjudication step unexecutable for exactly the kind of
   evidence this plan's own chosen dogfood target actually has
   (`EV-FPSS-008`'s `method: targeted_probe`). **Fix**: split the
   reproduction duty by Observation `method` — `knowledge-curator`
   reproduces `source_read`/`doc_read` evidence directly itself (needs
   only `Read`/`Grep`/`Glob`); for `executable`/`test_run` evidence, it
   specifies the exact command and hands it to the lead with the same
   "lead: run `<command>` to confirm" convention its own brief already
   uses elsewhere, incorporating the lead's real, unmodified output into
   its own recommendation — the independent judgment stays with
   `knowledge-curator`; only the mechanical execution moves to a role
   that actually has `Bash`. Propagated through §4.A, §5's diagram, and
   §7/§8's own references to "re-run by `knowledge-curator`."

A secondary, non-blocking ambiguity the same review flagged was also
tightened: whether `knowledge-curator` may finalise an investigation-log
entry (outcome 2/3/4) unilaterally, or whether it is a "draft" the lead
must still finalise. Resolved: `planning/retros/phase-85-self-curation-
investigation-log.md` is added, narrowly, to `knowledge-curator`'s own
write boundary at implementation time (mirroring exactly how `planning/
knowledge/**` was added for packet-assembly mode at Phase 54c) — it
writes and finalises outcome 2/3/4 entries itself; the lead's own role at
7b for that outcome is confirmation before step 8's requery, not a
second write.

No other issue was found: all six original fixes were independently
reconfirmed against live code (`find_gaps()`'s real `has_obligations`
logic and `slug=None` scan, the real absence of any existing `test_ref`-
file-existence check, `check_knowledge_base.py`'s real field-presence-
only validation, `CL-FPSS-007`'s real git history), every explicit
non-goal still held, no new circularity was introduced beyond the one
fixed above, and no stale internal cross-reference was found. This plan
is implementation-ready as of this note, subject to the genuinely
unresolved decisions above (unchanged by this amendment) and to the
still-outstanding requirement that Phase 85 implementation itself
remains separately unauthorised.

## Corrective note (2026-11-03, third independent review — "CodeCompass
Orchestrator — Final Phase 85 Plan Amendment, Verification and
Implementation")

A third, final amendment — triggered by a separate governing prompt that
**explicitly authorises implementation once this round's review passes**
— fixed three further issues before implementation began:

1. **[Material, now fixed]** §4.C point 1's `missing_contract` severity
   was still "blocking," inherited unexamined from `find_gaps()`'s own
   undifferentiated gap-reporting. Re-inspecting the real corpus (six
   knowledge slugs, one oracle contract — `balance-from-spec`) showed
   this would fail `--strict` against the real baseline for five of six
   slugs, including this plan's own chosen dogfood target
   (`first-party-source-symbols`). **Fix**: `missing_contract` is now
   `(info)`, never blocking, grounded directly in `decisions/0081` §3's
   own explicit, already-accepted deferral ("a future phase may choose
   to require contracts project-wide... not pre-committed here") and its
   own preferred mechanical criterion ("no contract directory exists for
   this slug," not an allow-list) — reused, not reinvented, for this
   script's own severity question. Confirmed by direct inspection that
   neither `doc-origin-pinned-reference` nor `haskell-api-surface-
   extraction` (both carrying `status: verified`/`implemented`
   Requirements, no contract) is treated as a defect by this project's
   own existing conventions, so this script does not treat them as one
   either. No allow-list of slug names anywhere in the fix.
2. **[Material, now fixed]** §4.A step 3-6 directed `context-researcher`
   to leave no record under `planning/knowledge/` for a declined
   candidate (outcome 2/3/4), but its own existing brief unconditionally
   writes `OBS-`/`EV-` records as it looks, before any disposition is
   known — a genuine instruction conflict, not merely an omission.
   **Fix**: a new, narrowly-scoped "self-curation investigation" mode,
   triggered only when a dispatch is explicitly framed as such, defers
   committing `OBS-`/`EV-` files until the §4.E disposition is known —
   written to disk only for outcome 1/5, never for outcome 2/3/4, whose
   full reproducible content instead goes into `context-researcher`'s
   own report, for `knowledge-curator` (not `context-researcher`) to
   turn into an investigation-log entry. Changes *when*/*whether* a
   write happens, never *what* or *where* `context-researcher` may
   write — no new permission, tool, or role; its ordinary feature-
   research behaviour (and its own prior, reflexive self-knowledge work
   already on file) is unaffected.
3. **[Fixed]** §4.A step 7a's Observation-`method` reproduction split
   named only two example methods (`source_read`/`doc_read` vs.
   `executable`/`test_run`), but the real corpus (re-inspected live)
   uses **nine** distinct `method` values. **Fix**: a complete,
   deterministic taxonomy — `source_read`/`doc_read`/`code_read`
   (inspection, `knowledge-curator` directly) plus `grep_search`
   (inspection via its own `Grep` tool, directly) vs. `executable`/
   `targeted_probe`/`test_run`/`test_execution`/`static_analysis`
   (execution, delegated to the lead at `knowledge-curator`'s explicit
   direction — confirmed `static_analysis` is execution-based by direct
   reading of its one real corpus instance, `OBS-FPSS-013`, a literal run
   command, not a passive read) — plus an explicit, fail-closed "unknown
   method" path that never silently treats an unrecognised value as
   reproduced. The Observation's own `method` field is kept explicitly
   distinct from the unrelated Evidence `evidence_kind` field throughout.

All three were independently re-verified against live repository state
before being accepted as fixed (real corpus `method`/`evidence_kind`
value inventory; real slug/contract counts; `decisions/0081` §3's own
verbatim text; `doc-origin-pinned-reference`/`haskell-api-surface-
extraction`'s real Requirement statuses). **Verdict: READY.** The
independent reviewer found two further, explicitly non-blocking
inaccuracies, both fixed in place immediately rather than deferred:
the Observation-`method` census undercounted by one real record
(`OBS-KNOW-001`, free prose, not one of the nine enum values — already
covered by the taxonomy's own fail-closed "unrecognised value" row, so
no design change was needed, only the plan's own stated count); and the
Evidence `evidence_kind` parenthetical listed four values where the real
corpus has five (`behavioural` omitted) — not load-bearing anywhere in
the design, corrected for accuracy only. A third, genuinely open
question the same review named (how `knowledge-curator`'s own
disagreement is handled in the *upgrade* direction — believing a
not-yet-written outcome 2/3/4 candidate should actually be outcome 1/5)
is now answered explicitly in step 7a's own "Disagreement or
insufficient evidence" bullet, above. This plan is implementation-ready
as of this note. The governing prompt that produced this amendment
explicitly authorises Phase 85 implementation once this round's
independent review confirms the fixes — see the implementation record
below this plan's own sections for that review's verdict and the
resulting build.

## Corrective note (2026-11-03, as-built: §4.C point 4 scoped to contract-bearing slugs)

Discovered during implementation, not anticipated by any of this plan's
own three independent review rounds: running `scripts/check_self_
knowledge_quality.py`'s new `test_ref`-file-integrity check (§4.C point
4) against the real corpus for the first time, before finalising its own
test suite, found it would false-positive on four real, pre-existing
`test`-kind Evidence records (`EV-ADPT-006`, `EV-CTXT-011`, `EV-SKEP-005`
in `codecompass-domain`; `EV-DOCORIGIN-008` in `doc-origin-pinned-
reference`) — all in slugs with **no** oracle contract at all, all using
an older, legitimate, pre-Phase-82 `test_ref` convention (a plain
pytest file/file:line citation, e.g. `"tests/test_graph.py:1426-1436"`),
which was never intended to resolve as an oracle-result file path.

**As-built fix**: the check is scoped to **contract-bearing slugs
only** — `test_ref` only means "a path under `planning/contracts/
<slug>/results/*.yaml`" for a slug that actually has an oracle contract;
for a slug with none, `test_ref` legitimately uses the older convention,
and the check does not apply at all. This mirrors `find_gaps()`'s own
existing `stale_test_citation` rule, which already silently treats any
non-resolving `test_ref` as not-applicable for exactly this reason — the
new check narrows to the one population where "doesn't resolve" can only
mean "broken," never "a different, equally legitimate citation style."
Confirmed real and not an invented edge case: all four false positives
were in the two slugs with zero contracts; `balance-from-spec` (the one
contract-bearing slug) produces zero `test_ref`-file findings either way.

This is the one deviation from this plan's own literal §4.C point 4 text
("for every `test`-kind Evidence record across every slug") discovered
during implementation; every other design element in §4.C was
implemented exactly as specified. Full detail, tests, and real-baseline
confirmation: `planning/retros/phase-85-self-curation-knowledge-quality-
validation.md`'s own "What worked"/"What didn't work" sections;
`tests/test_check_self_knowledge_quality.py::TestTestRefFileCheck::
test_non_resolving_test_ref_in_slug_without_contract_is_not_flagged`.
Independently confirmed by the phase's own `release-phase-auditor` pass
as a real, well-reasoned, fully-tested, honestly-disclosed deviation —
requested to be folded back here, not found blocking on its own.
