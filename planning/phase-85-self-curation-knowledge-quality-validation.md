# Phase 85: Self-Curation and Knowledge-Quality Validation — plan

**Status: planned, not yet implemented (2026-11-02, "CodeCompass
Orchestrator — Final Phase 84 Closeout and Phase 85 Planning").** This
file is the `CLAUDE.md` §1 implementation-ready plan `planning/
v2-roadmap.md`'s Phase 85 sketch and `decisions/0084` §§2-3 require
before any implementation begins. **Implementation is explicitly not
authorised by the governing prompt that produced this plan** — a
separate, future approval is required before any code in this plan is
written.

Governing scope: `planning/v2-roadmap.md` "Phase 85 — Self-Curation and
Knowledge-Quality Validation" (10-point roadmap-depth sketch);
`decisions/0084` §2 ("Phase 83 is unchanged; Phases 84-88 are newly
inserted") and §3 ("Self-curation is dogfooded, never circular").
Prerequisite: Phase 84 (`done`, including both its corrective pass,
`decisions/0092`, and its final corrective amendment, `decisions/0093`
— see `planning/phase-84-consolidated-knowledge-api.md`).

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
3. **Examine current source/tests/decisions for candidate findings.**
   **Owner: `context-researcher`**, dispatched exactly as today, target
   set to CodeCompass's own `src/codecompass/`, `tests/`, `decisions/`
   instead of an external project's checkout.
4. **Determine new / already-known / contradictory / stale /
   insufficiently supported.** `context-researcher`'s own existing
   step 1-2 discipline (read what's on file; compare against the §4.A.2
   retrieval) decides this *before* writing anything — a finding
   matching an existing, unsuperseded Claim is not re-written; a
   finding contradicting one is written as a `status: contradicted`
   Claim citing the prior one, exactly as the role already does for
   external projects.
5. **Collect independently reproducible evidence.** `context-
   researcher`'s own existing `OBS-`→`EV-` discipline — a real
   executed command, a real file:line read, a real Phase 83 oracle
   result citation. No new evidentiary category.
6. **Submit through the established lifecycle.** The written `CL-`/
   `DE-` record pair *is* the candidate for a domain/implementation
   finding — there is no separate "submission" step, since
   `context-researcher`'s own write already places it in `planning/
   knowledge/<slug>/`, exactly where `knowledge-curator`'s triage (next
   step) and `knowledge_api`'s own retrieval already look. A *process*
   lesson the same investigation happens to surface (how the work was
   done, not what CodeCompass does) is filed separately, as a
   `planning/learnings/inbox.md` candidate, through the unchanged
   existing lifecycle — the same split this session's own Phase 84
   closeout used.
7. **Promote / retain / merge / discard, with recorded reasons — two
   sub-steps, never one.** **7a, owner `knowledge-curator`**: dispatched
   to independently re-verify the new Claim's own cited Evidence (never
   trusting `context-researcher`'s own say-so — the exact discipline
   `decisions/0084` §3 requires and this session's own `L-107`-`L-111`
   triage already demonstrated in practice) and *recommend* a
   disposition. **`knowledge-curator` never itself edits the Claim** —
   its own Hard Rules explicitly forbid writing a Claim/Evidence/
   Observation record (confirmed by direct reading of `.claude/agents/
   knowledge-curator.md`: "never a Claim/Evidence/Observation/Decision/
   Requirement record, those are `context-researcher`'s or the human
   reviewer's"). **7b, owner the lead**: applies the recommended
   disposition by editing the Claim's own `status` (`supported`/
   `contradicted`/`superseded`) and `evidence_support_state` — the
   *same* fields and the *same* decision space every existing Claim in
   the corpus already uses, not a new disposition vocabulary, and the
   same "recommends, lead disposes" split `knowledge-curator.md` already
   uses for every other write-restricted target. See §4.B for the full
   rationale and the real precedent (`CL-FPSS-007`'s own `status`
   history) this split is based on. A finding that does not hold up
   under independent re-check is **not** silently dropped: it is written
   as a `status: contradicted` Claim with the contradicting Evidence
   attached (a declined finding is itself a recorded, evidenced fact —
   "X was investigated and found false" — never erased), satisfying the
   exit gate's own negative-control requirement
   without inventing a new "rejected candidates" artifact.
8. **Requery to verify correct representation.** **Owner: the lead** (or
   whoever ran step 7), re-running the exact §4.A.2 queries against the
   now-updated slug — `get()` resolves the new id; `trace_evidence()`/
   `epistemic_status()` reflect the new evidence; `find_gaps()` no
   longer flags what the new finding resolved (if anything). This is
   the same "re-demonstrate against the real corpus" discipline this
   session's own Phase 84 corrective passes used throughout (e.g.
   re-running `trace_evidence(REPO_ROOT, "REQ-BFS-001")` after each
   fix) — applied here to confirm a *promoted finding*, not a *code
   fix*, landed correctly.

**Idempotency.** Re-running the same investigation when nothing has
changed produces no new Claim (step 4 recognises it as already known).
An existing Claim is never edited in place to change its own conclusion
— a changed understanding is a *new* Claim, `supersedes:` the old one
(the existing field every Claim schema already has), exactly like this
project's own append-only ADR convention (`CLAUDE.md` §2), applied at
the knowledge-record layer instead of the decision-record layer.

**Failure handling.** An investigation that cannot independently
reproduce its own working hypothesis writes no Claim at all (or a
`status: contradicted` one, if a plausible-looking but false hypothesis
is worth recording so it is not re-investigated identically next time —
`context-researcher`'s own existing discretion, unchanged). A `knowledge-
curator` dispatch that cannot independently re-verify a cited Evidence
record (the citation doesn't resolve, the file it points at doesn't say
what it claims) returns the Claim to `evidence-gathering`, not
`supported` — the same three-state discipline (`candidate`/
`evidence-gathering`/decided) `planning/learnings/` already uses,
reused at the Claim layer via its own existing `status: proposed`.

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
| 7b (apply the recommended disposition — edit the Claim's own `status`/`evidence_support_state`) | **lead** | No |
| 8 (requery/confirm) | lead | No |

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

1. `knowledge_api.find_gaps(project_root, slug=None)` for every slug
   that has an oracle contract — its own existing six rules, unchanged.
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
   corrected during this plan's own independent review — see §12).
   Closes the corpus-wide gap identified in §1 above (`find_gaps()`
   itself has no `missing_evidence` rule) by *reusing* `trace_evidence`
   externally, exactly how `check_knowledge_base.py` already composes
   `knowledge_intermediate`'s own public functions rather than adding
   to that module. **Why composition, not a `knowledge_api.py` edit**:
   Phase 84 (including its final corrective amendment) is closed; this
   plan's own explicit non-goal (§6) is "no further edit to the
   just-closed module." A future phase may decide this check belongs
   inside `find_gaps()` itself as a seventh rule — that is a separately-
   authorised decision, not pre-empted here.
4. **Deterministic-only duplicate/overlap detection** (the governing
   prompt's own §6.C point 6), scoped to what is mechanically
   detectable without semantic judgment: two Claims in the same slug
   whose `supporting_evidence` sets are identical (order-independent),
   or whose `statement` field is byte-identical after whitespace
   normalisation. Flagged `(info)`, never blocking — **true semantic
   overlap (two differently-worded Claims about the same underlying
   fact) is explicitly out of scope for mechanical detection** (it
   would require embedding similarity or an AI call, excluded by this
   project's own "no unnecessary AI inference," `planning/v2-roadmap.md`
   Phase 85 point 6/`decisions/0085`'s carried-forward exclusion) and is
   left to `knowledge-curator`'s own existing human/agent judgment at
   triage time, same as today.

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

The structural guarantee is not a new enforcement mechanism bolted on
top — it is that **the existing roles cannot produce an unevidenced
Claim even if asked to**: `context-researcher`'s own definition requires
Observations before Evidence before Claims (step 3 of its own brief);
a Claim record's own schema has no field for "the agent asserts this is
true" independent of `supporting_evidence` — the record format itself
has no slot for an un-evidenced assertion to occupy. `knowledge-curator`
independently re-checks that citation, not the Claim's own prose, before
recommending any disposition — demonstrated in practice, not merely
asserted, by this very session's own repeated independent re-
verification of findings (direct hash comparisons, direct source re-
reads, direct test re-execution) rather than trusting any prior agent's
or retro's self-report, including correctly overturning a prior
"no new candidate learning" self-report on two separate occasions this
session. A self-curation pass's own narrative is **never** cited as its
own evidence — the schema structurally cannot accept that citation
(`supporting_evidence` holds `EV-`/`OBS-` ids, never prose).

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
    CL-<slug>-NNN + DE-<slug>-NNN (the assertion + the reasoning path)
        │
        ├──► domain/implementation finding → stays in planning/knowledge/<slug>/
        │
        └──► process-lesson (if any) → planning/learnings/inbox.md (separate pipeline)
        ▼
knowledge-curator triage
    independently re-verifies EV-/OBS- citations directly
        │
        ├──► supported   (status: supported, evidence_support_state: supported)
        ├──► contradicted (status: contradicted, contradicting_evidence cited)
        └──► evidence-gathering (status: proposed, held — not yet decided)
        ▼
lead requeries knowledge_api against the updated slug
    confirms get()/trace_evidence()/find_gaps() reflect the outcome
```

Provenance is carried exactly as the existing schema already requires:
`derived_by` (which agent/process), `repository_revision` (the
CodeCompass git SHA the finding is *about*, pinned — not the SHA at
triage time), `timestamp`. A Claim's `supporting_evidence`/
`contradicting_evidence` are the only legitimate route to "this is
true" — never the Claim's own `statement` prose standing alone.

---

## 6. Exact deliverables and minimal interfaces

1. **A workflow document**, `docs/workflows/self-curation-loop.md`,
   describing the 8-step loop (§4.A) for a future lead/agent to follow
   — prose and a short checklist, not new code. (Matches the existing
   `docs/workflows/knowledge-reconciliation-loop.md`'s own role and
   placement for the Stage-1/2/3 manifest pipeline.)
2. **`scripts/check_self_knowledge_quality.py`** (§4.C) — the one new
   script this phase introduces, composing existing `knowledge_api`/
   `knowledge_intermediate` functions, following `check_knowledge_
   base.py`'s own exact `--strict`/report-only convention.
3. **A demonstrated dogfood pass** (§7) against a real, bounded,
   first-party slice of CodeCompass's own `planning/knowledge/`
   corpus — not a synthetic fixture — producing the two-sided result
   the exit gate (§9) requires: written up as its own section of this
   phase's retro, with real commit hashes and real record ids, not a
   narrative summary.
4. **No change** to `src/codecompass/knowledge_api.py`, `oracle.py`,
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

**Selected target: `planning/knowledge/first-party-source-symbols/`**
(Phase 77's `source_symbols.py` regex-based Rust/TypeScript extraction),
specifically extending `CL-FPSS-007`'s own already-recorded,
already-open question.

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

**Confirmed tractable corpus breadth** (not cherry-picked): three
further first-party self-knowledge slugs exist and were inspected —
`planning/knowledge/codecompass-domain/` (186 records, the adapter/
context-graph/evidence-model domain), `planning/knowledge/haskell-
api-surface-extraction/` (43 records, the Haskell adapter's own export-
list parsing), `planning/knowledge/doc-origin-pinned-reference/` (32
records, the `doc_artifacts.origin` schema field, resolving context-gap
`CG-005`). Any of these would also satisfy the exit gate; `first-party-
source-symbols` is preferred for its ready-made, already-proven
probe-based evidentiary convention and its explicit open question.

**Planned investigation shape** (not pre-invented findings — the
governing prompt's own explicit instruction): a bounded
`context-researcher` dispatch, scoped to "does a third or fourth
ordinary Rust/TypeScript construct (beyond the two `CL-FPSS-007`
already documents) defeat `_extract_rust_source_symbols`/`_extract_js_
family_source_symbols`'s own line-anchored regex approach (`_RUST_ITEM_
RE`/`_JS_FAMILY_ITEM_RE`, confirmed by direct reading of `src/
codecompass/source_symbols.py`), silently producing an `INDEXED_PARTIAL`
false positive or a missed true positive?" The dispatch runs real
probes against the real, unmodified extractor functions (`src/
codecompass/source_symbols.py`, confirmed to exist and be unchanged by
any Phase 83/84 work — last touched by its own Phase 77 implementation
commit, `03f8519`) — e.g. a Rust `#[cfg(test)]`-
gated or doc-comment-embedded declaration-like line, a TypeScript
decorator-prefixed declaration, a declaration split by a line
continuation inside a macro. **Two acceptable outcomes, both satisfying
the exit gate, neither pre-committed to:**

- **A genuine new false-positive/false-negative shape is found,
  independently reproduced, and promoted**: a new `OBS-FPSS-NNN`/
  `EV-FPSS-NNN` pair plus either a new `CL-FPSS-NNN` (if it's a
  genuinely distinct shape) or an update path for `CL-FPSS-007` itself
  via `supersedes` (if it's best understood as sharpening the same
  claim) — `knowledge-curator` decides which, same as any other
  triage.
- **The hypothesis is investigated and found not to hold** (the
  extractors turn out robust against the specific constructs tried, or
  a construct that looked plausible on paper doesn't actually reproduce
  when tried for real): recorded as a `status: contradicted` Claim (or
  an Evidence record noting a negative/robust result cited by nothing)
  with the real probe's own output — a genuine, honest negative result,
  satisfying the exit gate's own negative-control requirement.

If neither outcome is cleanly reached (the investigation is genuinely
inconclusive), **this plan requires that to be reported honestly as the
exit gate not met**, per the governing prompt's own explicit instruction
— not manufactured into an artificial PASS.

---

## 8. Tests, negative controls, and validation commands

| Control | How exercised |
|---|---|
| Evidence-based promotion | The dogfood's own positive-outcome branch (§7) — real, independently re-verified Evidence, a real `knowledge-curator` disposition. |
| Correct rejection of unsupported findings | The dogfood's own negative-outcome branch (§7), *or*, if the dogfood happens to land cleanly on the positive side, a separate, explicit synthetic negative control: a deliberately false hypothesis about the same extractor (e.g. "a tab-indented declaration is never matched") tried for real and found false, recorded as `status: contradicted`. |
| Duplicate detection and reconciliation | `scripts/check_self_knowledge_quality.py`'s own duplicate check (§4.C.4), tested against a constructed fixture with two Claims sharing an identical `supporting_evidence` set. |
| Contradictory and stale knowledge | `find_gaps()`'s existing `contradiction`/`stale_test_citation` rules, reused unchanged — no new test needed, already covered by `tests/test_knowledge_api.py`. |
| Cross-record provenance | `get_context_packet()` on the newly-promoted Claim, confirming `via_claim`/`role` detail (Phase 84 final amendment) correctly traces back to its own Evidence. |
| Current vs. historical verification | If the dogfood finding cites a Phase 83 oracle result, `evaluate_result_precedence(..., repo_root=...)` reused unchanged — never a new verification mechanism. |
| Repeated runs without duplicate promotions | Re-run the exact §4.A.2 retrieval after the dogfood completes; confirm a second, identical investigation (run again) recognises the finding as already-known (step 4) and writes nothing new — demonstrated, not merely asserted. |
| Safe handling of missing/inaccessible evidence | `scripts/check_self_knowledge_quality.py` run against a slug with a dangling `test_ref` (reuses `find_gaps()`'s existing `dangling_evidence_reference`/`dangling_dependency_reference` coverage — no new code path). |
| Preservation of existing canonical knowledge | `git diff --stat` after the dogfood run: every file outside the newly-added record(s) for the targeted slug is untouched; no *already-decided* Claim (one not freshly written by this same investigation) is edited in place — an already-decided Claim is only ever superseded, per §4.A's idempotency rule. (This is distinct from, and does not conflict with, step 7b's one-time disposition edit to the *freshly-written, not-yet-decided* `status: proposed` Claim from the same investigation — that edit happens exactly once, by the lead, as part of this same investigation's own disposition, never as a later reopening of a settled record.) |
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
   equivalent, if the dogfood lands on a different slug per §7's own
   two-sided design) record, `knowledge-curator`-triaged, with Evidence
   independently re-verified by someone/something other than the agent
   that wrote it.
2. **At least one real candidate is independently investigated and
   correctly declined, with a recorded reason** — a real
   `status: contradicted` Claim or an explicitly negative Evidence
   record, not a hypothetical "we could decline X."
3. **Both arise through the existing, unmodified lifecycle** — no new
   promotion path, no new record kind, no weaker bar.
4. **The on-demand quality check runs standalone and reports real
   findings against the real corpus**, with its one new rule (§4.C.3)
   demonstrated to detect at least one real `missing_evidence`-shaped
   gap if one genuinely exists in the corpus at implementation time (or
   an explicit, honest "none found" if it does not — never a staged
   positive).
5. **If 1 and 2 cannot both be genuinely achieved, this phase reports
   its exit gate as not met** — explicitly, in the closeout report,
   naming which half failed and why, per the governing prompt's own
   instruction. This is not treated as a planning failure; it is the
   honest outcome the gate exists to allow.

---

## 10. Risks, mitigations, trade-offs, and explicit non-goals

**Risks (named by the governing prompt itself):**

- **Circularity** — a self-curation agent's own assertion mistaken for
  verification. Mitigated structurally (§4.D), not procedurally: the
  record schema itself has no slot for an un-evidenced Claim, and
  `knowledge-curator`'s own re-verification discipline is demonstrated,
  not assumed.
- **The dogfood finding nothing genuinely new.** Mitigated by selecting
  a target with an already-declared open question (§7), not a slug
  believed fully settled; if it still yields nothing, §9 point 5
  applies honestly rather than forcing a result.
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
  §4.C.4) rather than semantic. Accepted — the alternative requires
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

---

## 11. Implementation sequence and independent audit procedure

1. Write `scripts/check_self_knowledge_quality.py` (§4.C) and its
   tests; run against the real corpus; confirm it reports real,
   plausible findings (or an honest "none") — never fabricated.
2. Write `docs/workflows/self-curation-loop.md` (§6.1).
3. Run the dogfood investigation (§7): dispatch `context-researcher`
   against `first-party-source-symbols` (or the declared fallback slug,
   if that investigation proves genuinely inconclusive — chosen before,
   not after, seeing the result, per §7's own two-sided design).
4. Dispatch `knowledge-curator` to independently triage whatever the
   dogfood produced, including the negative-control branch if that is
   what actually occurred.
5. Requery (§4.A step 8); write the retro's own dogfood section with
   real ids, real commit hashes, and the real (not idealised) outcome.
6. Run the complete CodeCompass test suite and all four strict
   validators (`check_user_docs.py`/`check_contracts.py`/`check_
   knowledge_base.py`/`check_self_knowledge_quality.py`, all `--strict`).
7. Independent `release-phase-auditor` pass against this exact plan's
   own §9 exit gate, the real commit(s), and the real dogfood outcome —
   re-deriving the verdict from the actual repository state, never
   trusting the implementing agent's own report (this plan's own
   `CLAUDE.md` §5 obligation, carried forward from every prior phase in
   this project's history).
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
