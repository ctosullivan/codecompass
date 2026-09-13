# Context Edge Lifecycle and Audit Loop — planning package

**Status: planning only. No implementation until reviewed and a phase
number/plan file is created per `CLAUDE.md` §1.** Source prompt:
[`context-edge-lifecycle-prompt.md`](context-edge-lifecycle-prompt.md)
(saved verbatim, per its own instruction).

**Headline finding, stated up front because it should shape every
decision below:** this system substantially already exists, is already
governed by an accepted ADR, and has already been run end-to-end for
real, once, this milestone — not as a hypothetical, as `CG-002`'s actual
history (Phases 45→47→49→51): a mechanical edge-detection gap was
observed on Ledgerkit, recorded as a candidate, independently
re-confirmed twice (`recurred`), consolidated at a gate (`GATE DB`),
turned into a scoped deterministic fix, implemented, and the fix was
independently re-verified against the original failing cases (`GATE
DC`) — with a durable, append-only, planning-folder audit trail the
whole way, none of which ever touched `context-graph.db`. That is the
prompt's own required lifecycle, already working. The job of this phase
is **not** to build a new system next to it. It is to (a) name what
already satisfies the prompt's requirements, (b) generalise the one real
gap — structured, edge-identified *experience* observations, which today
exist only as unstructured prose in `context-use-log.md` — to the same
rigor `context-gaps/` already has, and (c) tighten the shared vocabulary
so both queues plug into the same triage step consistently.

---

## 1. Current-state assessment

### 1.1 Graph edges (`context-graph.db`) — mechanical, deterministic, unchanged by this phase

Schema (`src/codecompass/graph.py::_SCHEMA_SQL`): `vendors`,
`source_files`, `symbols`, `uses_edges`, `doc_chunks`, `doc_artifacts`,
`documents_edges`, `skill_mentions_edges`, `routes_via_edges`,
`depends_on_edges`, `doc_relations_edges` — every one populated only by
`rebuild_deterministic`, which is called only from mechanical detector
modules (`usage.py`, `doc_mapping.py`, `skill_scan.py`, `spec_docs.py`,
discovery). No AI call anywhere upstream of a graph-fact table.
`doc_relations_edges.relation_kind` is a closed `CHECK` enum
(`mentions_dependency`, `mentions_artifact`) — the detector
(`doc_mapping.py::build_doc_relations_edges`) is a literal
`\b{name}\b` regex match against tracked vendor names and other doc
artifacts' `name` fields, nothing probabilistic (`decisions/0043`).
**This already is the "authoritative edges only from mechanical rules"
invariant the prompt asks for — it predates this phase and needs no
change.**

### 1.2 Enrichment — already has its own queue, staleness detection, and non-authority guarantee

Three enrichment tables, all explicitly commented `-- Survive every
rebuild_deterministic call`: `vendor_enrichment` (keyed by `vendor_id`
FK, since vendors are upserted by natural key, never deleted-and-
reinserted), `symbol_enrichment` (same), and `doc_relation_enrichment`
(keyed by **natural-key TEXT columns**, `(source_doc_path,
target_vendor_name, target_doc_path)`, deliberately *not* an FK —
`decisions/0038` explains why: `doc_artifacts` rows are fully deleted
and reinserted on every whole-project sync, so an FK here would cascade
every AI-written summary away on every sync).

**The "enrichment queue" and "same edge unchanged vs. changed"
fingerprint the prompt asks me to design already exist, in production,
today:** `relation_enrichment.py::select_candidates` calls
`graph.relation_enrichment_candidates(conn)` (every `doc_relations_edges`
row), recomputes `_compute_content_hash(source_text, target_text)` for
each, and skips any row whose hash matches the cached
`doc_relation_enrichment.content_hash` — i.e. it already answers "new or
changed edge needing (re-)enrichment" without touching anything the edge
detector wrote. `vendor_enrichment.symbol_set_hash` is the equivalent
fingerprint on the vendor side. This selection only ever runs when
usage-proven candidates exist and the run is disclosed/confirmable
(`decisions/0033`) — never silent, never automatic authority.
Enrichment output (`ai_summary`, `relation_label`) is additive metadata
alongside the edge, never a replacement for it, and every query surface
(`query relations`, `/discovery`) shows enrichment as a labelled,
distinct field, never merged into the fact.

**Conclusion:** requirement "review/enrichment queue" + "stable
identity/fingerprint to recognise same-edge-unchanged" = **already
built, reuse as-is.** No new hashing mechanism, no new queue table.

### 1.3 Context gaps (`planning/context-gaps/`) — already almost exactly the "edge request" lifecycle

`decisions/0051` (Accepted, Phase 43c) is, functionally, this prompt's
"Requested edge lifecycle" and "key invariant" sections already ratified
as project policy:

> "An agent's suggested relationship is an observation with provenance.
> It is captured in `planning/context-gaps/` and nowhere else... It
> becomes authoritative only by promotion through the learning lifecycle,
> into one of two destinations, each with its own gate: a
> mechanical-detection improvement (Stage C, GATE DB, own ADR) or a new
> graph capability (Stage E, GATE DD, own ADR)."

Current shape (`planning/context-gaps/{README,TEMPLATE,inbox}.md`):
- **Status states:** `candidate` → `recurred` → `promoted-to-roadmap` /
  `discarded`. Maps directly onto the prompt's `requested → investigating
  → {unsupported|duplicate|already_represented|retrieval_issue|
  detector_gap} → proposed_change → resolved`, just coarser — `recurred`
  conflates "investigating" and "evidence gathered"; the terminal states
  don't yet distinguish *why* something was discarded (unsupported vs.
  duplicate vs. retrieval issue) as separate values, only as prose in the
  curation note.
- **Template fields:** origin, date, `codecompass_revision`, project,
  "the edge" (`A ↔ B`), edge kind, agent's reasoning, "what the graph
  shows instead", **"could mechanical detection ever catch this?"**
  (yes-with-heuristics / no-conceptual-only / unsure — this *is* the
  investigation-outcome classification, just phrased as a question
  rather than an enum), smallest candidate, classification
  (detection-improvement vs. graph-capability — this *is* "Stage C fix
  vs. Stage E capability"), status, recurrence, curation (free text).
- **Real, run history:** `CG-001` (own-dev, `candidate`, single
  occurrence — a local-code↔local-code gap, no edge exists to request
  yet). `CG-002` (Ledgerkit `dev-docs/` glob-coverage gap — filed,
  `recurred` via two independent agent confirmations, `promoted-to-
  roadmap` at GATE DB, implemented Phase 49, verified working at GATE
  DC — **the full lifecycle, closed**). `CG-003` (external hledger.org
  manual, zero representation — correctly kept `candidate`,
  classification `graph-capability`, explicitly routed to Stage E/GATE
  DD since "no glob fix could ever cover it").
- **Who triages it:** `knowledge-curator` already owns this, explicitly,
  as a documented "sibling queue" to `planning/learnings/` (see 1.5).

**Conclusion:** requirement "edge requests, investigation, evidence,
authority boundary, detector-change path" = **already built and
battle-tested once for real.** The gap is *precision of the state
machine's terminal values* and *linking to a formal per-request
observation-type taxonomy* (§3 below), not the mechanism itself.

### 1.4 Context-use log (`planning/context-use-log.md`) — the real gap: unstructured, not edge-identified

Introduced Phase 43c as "the lightweight, high-volume complement to
`context-evaluator`'s per-task report." Format: a free-text heading
(`### <date> · <phase> · <who> · <context source>`) plus four prose
bullets (`retrieved`, `default pathway`, `advantage: LOW/MODERATE/HIGH`,
`wrong or misleading? yes/no/partially`). Real entries exist from
Phases 43–51 (11 entries as of this writing), including the two
FAIL-then-fixed Ledgerkit cases.

**This is the prompt's "observation model" (`EDGE_USEFUL`,
`EDGE_UNHELPFUL`, `EDGE_MISLEADING`, `EDGE_STALE`) — but only as prose.**
It has no:
- stable identifier per entry (can't be referenced from an ADR or a
  later investigation the way `CG-NNN` can);
- a field naming *which specific edge* (or absence of edge) the
  observation is about — "retrieved" is a sentence, not a
  `(source, relation_kind, target)` tuple;
- an explicit split between **edge correctness** ("was the claim true?")
  and **task usefulness** ("did it help *this* task?") — the prompt's
  own worked example (`README.md MENTIONS click`, true but irrelevant to
  a transaction-validation task) has no field to express in the current
  format; "advantage: LOW" today conflates "correct but unhelpful" with
  "actively wrong," which is exactly the distinction the prompt's §
  "Context observation model" calls out as a common modelling mistake;
- a `status` field or any indication of whether a "wrong or misleading:
  yes" entry has actually been investigated yet — today that happens
  informally, only at the Phase 47/55 bulk reviews, driven by the lead
  re-reading the whole file.

**Conclusion:** this is the one piece genuinely worth redesigning — not
replacing the file, but giving each entry the same structural rigor
`context-gaps/`'s `TEMPLATE.md` already has, including a stable ID, an
edge-identity field, and a correctness/usefulness split.

### 1.5 Agent roles — the investigation role already exists

Current roster (`.claude/agents/`, 8 agents): `context-evaluator`,
`reference-project-tester`, `docs-maintainer`, `roadmap-context-curator`,
`knowledge-curator`, `docs-reconstructor`, `release-phase-auditor`,
`context-health-planner`. `knowledge-curator`'s brief already states,
verbatim, almost the entire "context curator" job description this
prompt asks for:

- "own the project-learning lifecycle... for each candidate, decide:
  promote / retain / merge / discard";
- explicitly owns `context-gaps/` as "a sibling queue... you triage it
  too... at every phase's triage step and in bulk at Phases 47 and 55";
- explicit **prohibitions** matching the prompt's list almost word for
  word: "an agent observation is not authoritative because an agent
  recorded it," "never `CLAUDE.md`, `decisions/*`, `src/`, or `docs/`
  directly — propose, the lead disposes," "you have no Bash" (can't even
  mechanically verify its own recommendation, must hand off);
- already produces exactly the artifact the prompt calls a
  "recommendation, not a decision" (see the real GATE DB dispatch this
  session: the curator drafted `findings.md`'s content and an explicit
  funding recommendation; the lead ratified it via `AskUserQuestion`
  before any code changed).

`context-evaluator` already independently rates whether a piece of
context was accurate/relevant/complete/fresh/grounded/noisy/trustworthy
and whether it "would have misled the implementing agent" — this is the
prompt's observation-*production* step (an agent classifying an
edge/context experience), distinct from `knowledge-curator`'s
observation-*investigation* step. `reference-project-tester` is the
other observation producer, for live friction during real tasks.

**Conclusion:** requirement "review the roster before introducing
another role; prefer evolving knowledge-curator" — **already exactly
true.** No new agent. `knowledge-curator`'s remit needs a documented
(not structural) extension: today it triages `learnings/` and
`context-gaps/`; it should also triage the newly-structured
edge-experience observations (§3), using the same investigate-vs-record
judgement the prompt describes, formalised as an explicit rule set
(§4.3) rather than left to the lead's ad hoc bulk-review judgement (which
is what happens today, informally, at Phase 47/55).

### 1.6 Context-health (`planning/context-health.md`) — forward-looking, distinct, unaffected

`context-health-planner`'s output answers "is the graph adequate for
*upcoming* phases" — a prediction, not a record of past experience. It
is explicitly distinguished in existing docs from `roadmap-context-curator`
(planning-doc truth) and `context-evaluator` (per-task quality by direct
inspection). This phase does not touch it; it's an input the curator can
cite during investigation, not a queue this lifecycle needs to
generalise.

### 1.7 `check`'s coverage-gap sections — a fourth, older, adjacent mechanism, worth naming

`codecompass check` already reports (mechanically, no AI, report-only)
four structural gap categories: unused vendors, documented-but-unused
symbols, used-but-undocumented symbols, orphaned third-party Skill
mentions. These are **graph self-consistency checks**, not agent
observations — they don't belong in this lifecycle's observation model,
but they're worth naming so the plan doesn't accidentally reinvent a
fifth "gap" concept. **Kept as-is, out of scope.**

### 1.8 Overlap and fragmentation, summarised

| Existing mechanism | Prompt's ask it already satisfies | Real gap |
|---|---|---|
| `context-graph.db` schema + detectors | Authoritative mechanical edges | None — don't touch |
| `*_enrichment` tables + `select_candidates` | Enrichment queue + change fingerprint | None — reuse as-is |
| `planning/context-gaps/` + `decisions/0051` | Edge-request lifecycle, authority boundary, investigation, detector-change path | Terminal-state precision only |
| `planning/context-use-log.md` | Observation model (useful/unhelpful/misleading/stale) | **Real gap** — unstructured, no stable ID, no edge identity, no correctness/usefulness split |
| `knowledge-curator` | Investigation/context-curator role | Remit needs explicit extension + an investigate-vs-record rule set |
| `planning/learnings/` | "Validated observation → detector improvement" destination table | Already routes here (§4 classification table); no change |
| `check`'s coverage-gap sections | (adjacent, not asked for) | None — leave alone |

**No new files, schemas, commands, or agents are justified by "it would
be architecturally cleaner."** The one justified change is generalising
`context-use-log.md` into a structured, `context-gaps`-shaped sibling.

---

## 2. Proposed architecture

```
                    MECHANICAL SYNC (unchanged)
              usage.py / doc_mapping.py / skill_scan.py / spec_docs.py
                              │
                              ▼
                    AUTHORITATIVE GRAPH  (context-graph.db)
              vendors, symbols, uses_edges, doc_artifacts,
              doc_relations_edges, ...  ← unchanged, untouched by
                                            anything below this line
                              │
                              ▼
              ENRICHMENT QUEUE (existing, unchanged)
        relation_enrichment.select_candidates() / content_hash diff
                              │
                              ▼
              ENRICHED EDGE (doc_relation_enrichment / vendor_enrichment)
                    additive metadata, never authoritative
                              │
                              ▼
                    AGENT CONSUMES CONTEXT
           (query relations / query vendor / /discovery / a generated
            Skill — existing surfaces, unchanged)
                              │
              ┌───────────────┼────────────────────┐
              ▼               ▼                     ▼
      EDGE EXPERIENCE   EDGE REQUEST          (nothing notable —
      (NEW, generalised  (EXISTING,            majority case, no
       from context-use- planning/context-      record needed beyond
       log.md)            gaps/, unchanged      the routine
                           in mechanism)         context-use-log
                                                  "not used" entry)
              │               │
              └───────┬───────┘
                      ▼
        knowledge-curator TRIAGE  (existing agent, extended remit)
        — the ONLY place observations of either kind are read together
                      │
                      ▼
              INVESTIGATION (existing: curator's "curate" step,
              now with an explicit investigate-vs-record rule, §4.3)
                      │
        ┌─────────────┼──────────────────────┐
        ▼             ▼                      ▼
   no action    retrieval/ranking      DETECTOR / GRAPH-CAPABILITY
   (recorded,   note (recorded,        CHANGE PROPOSAL
   status:      status: retained,      (existing: promote → Stage C/
   discarded    revisit trigger)       GATE DB or Stage E/GATE DD,
   or retained)                        own ADR, decisions/0051 unchanged)
                                              │
                                              ▼
                                    NORMAL DEV IMPLEMENTATION
                                    (lead / implementer subagent,
                                     tests, docs-maintainer, audit —
                                     the existing 14-step workflow,
                                     unchanged)
                                              │
                                              ▼
                                       MECHANICAL SYNC
                                  (edge becomes authoritative —
                                   loop closes)
```

**What's new, precisely:** one generalised template + inbox
(`planning/context-observations/`, replacing/absorbing
`context-use-log.md`'s job — see §8 Migration for why this is a rename +
restructure, not a new parallel system) and a small, explicit extension
to `knowledge-curator`'s brief. **What's unchanged:** every graph table,
every detector, the enrichment queue, `context-gaps/`'s mechanism and
`decisions/0051`'s boundary, the agent roster's membership, the 14-step
workflow, and every CLI command.

---

## 3. Data model

Following this project's own established convention throughout
`planning/` (`context-gaps/`, `learnings/`): **structured Markdown
records with a fixed key-list, one inbox file, an ID scheme, a status
enum** — not JSONL, not a second SQLite database, not YAML frontmatter.
This repo has never used either of the former for planning artifacts,
and introducing one here would be exactly the "sophisticated for its own
sake" mistake the prompt warns against. Markdown records are already
diffable, human-inspectable, agent-writable with `Edit`, and git gives
free timestamps/attribution/history — the three deterministic-audit
properties requested come from git + a stable ID convention, not from a
database engine.

### 3.1 Edge identity (fingerprint) — reuse existing natural keys, don't invent a new one

An edge that **already exists** in the graph is identified exactly the
way `doc_relation_enrichment` already identifies it: the natural-key
tuple the detector itself used —
- doc-relation edges: `(source_doc_path, relation_kind, target_vendor_name
  | target_doc_path)` — literally `doc_relation_enrichment`'s own primary
  natural key, already stable across rebuilds.
- usage edges: `(source_file_path, vendor_name, symbol_name)`.
- vendor-level facts: `vendor_name`.

An edge that **does not yet exist** (a request) has no row to key off —
its identity is the *proposed* natural-key tuple stated in the request
record itself (source path/symbol, target vendor/doc/concept name,
in prose if the target isn't a tracked name yet — e.g. `CG-003`'s target
is `https://hledger.org/1.52/hledger.html`, not anything
`context-graph.db` has ever heard of). No new "pending edge" table is
needed; the natural-key tuple *is* the fingerprint, written as plain
fields in the record, exactly as `context-gaps/TEMPLATE.md`'s "the edge:
`A ↔ B`" field already does today.

**Change-detection fingerprint** (needed to avoid re-flagging an
unchanged edge for re-enrichment, or re-recording an unchanged
observation): reuse `doc_chunks.content_hash` /
`relation_enrichment._compute_content_hash` verbatim. No second hashing
scheme.

### 3.2 Edge observation record (NEW — generalises `context-use-log.md`)

Location: `planning/context-observations/inbox.md` (live queue, newest
first — mirrors `context-gaps/inbox.md` exactly) +
`planning/context-observations/TEMPLATE.md` +
`planning/context-observations/README.md`. (Directory name is this
plan's proposal, not the prompt's suggested filename, per the planning
constraints — chosen to sit as a visible sibling of
`context-gaps/`/`learnings/` in `planning/`, not nested under a
tool-owned dotfolder, since these are agent/human-authored planning
records, not something `codecompass sync` generates or reads.)

```
### OBS-NNN — <one-line: what was retrieved, was it used, outcome>

- **origin:** <phase/task — e.g. "Phase 46, Ledgerkit task 01">
- **date:** <YYYY-MM-DD>
- **codecompass_revision:** <short SHA>
- **project:** <codecompass (own dev) | ledgerkit | technical-clipper> (+
  target commit if external)
- **edge identity:** <the natural-key tuple this observation is about —
  e.g. `dev-docs/hledger-compatibility.md -- mentions_dependency --> (none: absent from graph)`
  or, once tracked, `... -- mentions_artifact --> .claude/skills/codecompass/SKILL.md`.
  If the observation is about the *absence* of an edge rather than an
  existing one, say so explicitly here rather than leaving it implicit.>
- **observation type:** <EDGE_USEFUL | EDGE_UNHELPFUL | EDGE_MISLEADING |
  EDGE_STALE | EDGE_REDUNDANT> — (EDGE_REQUESTED / EDGE_MISSING route to
  `context-gaps/` instead, per §8; not duplicated here)
- **edge correctness:** <correct | incorrect | not-assessed> — was the
  mechanical claim itself true, independent of whether it helped
- **task usefulness:** <useful | irrelevant-to-this-task | n/a> — did it
  help *this* task, independent of correctness. A correct-but-irrelevant
  edge (the prompt's `README.md MENTIONS click` example) is
  `correct` + `irrelevant-to-this-task` — two separate fields, never
  collapsed into one "advantage" rating the way `context-use-log.md`
  currently does.
- **default pathway:** <what a fresh agent without CodeCompass would
  have done — kept from the existing format, still valuable>
- **advantage: LOW | MODERATE | HIGH** (`context-quality-evaluation.md`
  §5 definitions, unchanged)
- **status:** <recorded | investigating | resolved> — new: makes it
  possible to tell, without re-reading the whole file, which
  observations still need `knowledge-curator` attention
- **investigation:** <filled only if status ≥ investigating — findings,
  evidence, outcome>
- **resolution:** <pointer to the CG-NNN / L-NNN / ADR / commit this
  fed, once one exists, or "no action — recorded as evidence">
```

This is a **strict superset** of `context-use-log.md`'s current four
fields (`retrieved` → folded into the one-line title + edge identity;
`default pathway`, `advantage`, `wrong or misleading?` → kept, the last
one now split into `observation type` + `edge correctness`). No
information is lost; every field context-use-log.md has today maps onto
a field here.

### 3.3 Edge request record — `context-gaps/`, extended in place, not replaced

Keep `planning/context-gaps/{README,TEMPLATE,inbox}.md` and its `CG-NNN`
IDs exactly where they are (real history exists, don't churn IDs).
**Extend `TEMPLATE.md`'s existing fields**, don't add new files:

- **status** enum widened from `candidate / recurred / promoted-to-roadmap
  / discarded` to include the prompt's finer investigation outcomes as
  the value recorded in the *existing* free-text `curation` field's
  first line, formalised as a controlled vocabulary rather than prose:
  `unsupported | duplicate | already_represented | retrieval_issue |
  detector_gap | graph_capability_gap`. (`detector_gap` →
  `promoted-to-roadmap` via GATE DB; `graph_capability_gap` →
  `promoted-to-roadmap` via GATE DD; the other four → `discarded`, but
  now with *which kind* of discard recorded, not just a one-line reason
  — useful for GATE DB/DD's own aggregate view of "how often is this
  retrieval vs. detection vs. duplicate.")
- No change to `candidate`/`recurred`/`promoted-to-roadmap`/`discarded`
  as the primary status field — that state machine is proven and
  shouldn't be widened for its own sake.

### 3.4 What belongs in `context-graph.db` vs. the durable audit history

**Nothing new belongs in `context-graph.db`.** This is not a close call —
`decisions/0051` already considered and rejected a staging table for
exactly this class of data, for reasons (blast radius of one bad `JOIN`,
schema/migration cost for what is fundamentally a list of prose records)
that apply identically to the prompt's "edge review state" question.
Review-state metadata (`unreviewed`/`enriched`/`used`/`questioned`) is
**derivable at read time**, not stored: "enriched" = a matching row
exists in `*_enrichment`; "used" = a matching `edge identity` appears in
`context-observations/inbox.md`; "questioned" = the latest matching
observation has `observation type` in
`{EDGE_UNHELPFUL,EDGE_MISLEADING,EDGE_STALE}` and `status !=
resolved`. No column, no migration, no risk of the derived state
drifting from the two source-of-truth files it's computed from.

**Durable audit history = the planning-folder Markdown files
themselves**, exactly as `context-gaps/`/`learnings/` already are.
`context-graph.db` is fully deleted and rebuilt on `sync`
(`rebuild_deterministic`); `planning/**` is untouched by `sync` and lives
in git. This already satisfies "the audit trail must survive graph
regeneration" — it's a property of *where the file lives*, not of a
special append-only format. No `.codecompass/context-audit/` directory
is needed; that would be a second, parallel location for exactly the
same kind of record `planning/context-gaps/`/`planning/context-observations/`
already hold, contradicting "consolidate existing mechanisms rather than
creating parallel systems."

---

## 4. State machines

### 4.1 Edge review/enrichment lifecycle (existing, unchanged — documented here for completeness)

```
new/changed doc_relations_edges row (content_hash differs from cache)
        │
        ▼
  enrichment candidate (relation_enrichment.select_candidates)
        │
        ▼
  usage-proven? ──no──> stays unenriched, re-checked next sync
        │yes
        ▼
  disclosed/confirmable batch run (decisions/0033)
        │
        ▼
  doc_relation_enrichment row written (content_hash cached)
        │
        ▼
  "enriched" (derived, §3.4) — until content_hash next diverges
```

### 4.2 Edge-request lifecycle (existing `context-gaps/` state machine, terminal values sharpened per §3.3)

```
candidate  (CG-NNN filed: origin, edge, reasoning, evidence)
    │
    ▼
recurred  (2nd independent occurrence, or 2 agents — decisions/0051 §"how it feeds the gates")
    │
    ▼
knowledge-curator classifies the underlying cause:
    │
    ├─ unsupported / duplicate / already_represented / retrieval_issue
    │        → discarded (with the specific reason recorded, §3.3)
    │
    └─ detector_gap / graph_capability_gap
             → promoted-to-roadmap  (GATE DB or GATE DD names the owning phase)
                     │
                     ▼
             normal dev implementation (existing 14-step workflow)
                     │
                     ▼
             mechanical sync → edge becomes authoritative
                     │
                     ▼
             (optional) re-evaluation phase confirms it worked — GATE DC-style,
             as CG-002/Phase 51 already did for real
```

### 4.3 Edge-experience (observation) lifecycle (NEW, generalising `context-use-log.md`)

```
agent retrieves/consumes context for a real task
        │
        ▼
OBS-NNN recorded (status: recorded) — always, per the existing
agent-led-workflow.md step 4 rule ("if no context was used, log a
one-line 'not used — why' entry too")
        │
        ▼
knowledge-curator triage — investigate-vs-record rule (see below):
        │
        ├─ EDGE_USEFUL                          → record only, done
        ├─ EDGE_UNHELPFUL, first occurrence      → record only, done
        ├─ EDGE_UNHELPFUL, recurring (same edge  → status: investigating
        │   or same detector, ≥2 instances)         → file/link a CG-NNN
        │                                             or L-NNN as appropriate
        ├─ EDGE_MISLEADING                       → status: investigating
        │                                             immediately (highest
        │                                             priority per
        │                                             context-quality-
        │                                             evaluation.md §1's
        │                                             existing "incorrect
        │                                             outranks incomplete"
        │                                             rule — this phase
        │                                             doesn't invent that
        │                                             priority, it already
        │                                             exists)
        └─ EDGE_STALE                            → status: investigating
                                                        immediately
        │
        ▼
investigation (curator gathers evidence, classifies — same categories
as §4.2's edge-request outcomes, since "investigate a bad edge" and
"investigate a missing edge" converge on the same six outcomes)
        │
        ▼
status: resolved — resolution field points at whatever landed
(a CG-NNN promoted, an L-NNN promoted, "no action — recorded as
evidence", or a direct retrieval/ranking note for a future phase)
```

This mirrors the prompt's own suggested rule set almost exactly
(`useful → record only`, `single irrelevant → record only`, `repeated
irrelevant → investigate`, `misleading → investigate immediately`,
`stale → investigate immediately`) — the only change from the prompt's
draft is folding `requested`/`missing` out of this lifecycle entirely,
since those already have a better-developed home in `context-gaps/`
(§3.3), and duplicating the state machine across two files would
reintroduce the fragmentation this phase exists to remove.

---

## 5. Agent responsibilities

No new agent. Two existing agents get their briefs extended (documented
change, not a capability change — both already do the adjacent work
informally):

### `knowledge-curator` (extended)

**Newly explicit responsibilities:**
- Triage `planning/context-observations/inbox.md` at every phase's
  triage step and in bulk at Phase 47/55-equivalent consolidations,
  using the exact same cadence it already applies to `learnings/` and
  `context-gaps/`.
- Apply the investigate-vs-record rule (§4.3) rather than leaving that
  judgement to the lead's ad hoc bulk-review reading (what happens
  today).
- When an investigation's outcome is `detector_gap` or
  `graph_capability_gap`, **write the finding into a `context-gaps/`
  entry** (or link an existing one) rather than resolving it purely
  within `context-observations/` — keeps exactly one place
  (`context-gaps/`) as the input to GATE DB/DD, per `decisions/0051`'s
  existing "one curator, two queues" design, now three queues sharing
  one curator, still one gate-input path.

**Unchanged prohibitions** (already in the brief, restated because
they're exactly the prompt's "must not" list): no Bash, no direct
`context-graph.db` write of any kind (was never possible — the agent has
no code-execution tool), no `src/`/`decisions/*`/`CLAUDE.md` writes,
propose-only for anything requiring the lead's or `docs-maintainer`'s
hand.

### `context-evaluator` / `reference-project-tester` (unchanged mechanism, brief gets a one-line pointer)

Both already produce exactly the raw material `context-observations/`
records are made from (a verdict + advantage rating; a live friction
log). Add one line to each brief: "file a `context-observations/OBS-NNN`
entry for each retrieval this task made, using the template" — replacing
the current informal instruction to add a `context-use-log.md` line,
same information, new location/format.

### Everyone else (`docs-maintainer`, `roadmap-context-curator`,
`docs-reconstructor`, `release-phase-auditor`, `context-health-planner`)

**Unaffected.** None of them read or write `context-use-log.md` or
`context-gaps/` as their primary job today, and none need to for this
lifecycle either.

### The lead (unchanged role, restated for completeness)

Implements approved deterministic detector changes (directly or via an
ad hoc implementer subagent) — the only party that ever turns a
`detector_gap` classification into actual `src/codecompass/` code,
exactly as Phase 49 did for `CG-002`. Ratifies GATE DB/DD-scale funding
decisions the curator can only recommend (per the real precedent this
session: `AskUserQuestion` before Phase 49 started).

---

## 6. Repository changes (proposed — none implemented by this planning package)

### New

- `planning/context-observations/README.md` — registry/instructions,
  mirroring `context-gaps/README.md`'s structure (what belongs here,
  what doesn't, statuses, how it feeds triage).
- `planning/context-observations/TEMPLATE.md` — the record format, §3.2.
- `planning/context-observations/inbox.md` — the live queue, seeded by
  migrating `context-use-log.md`'s existing 11 entries (§8) into the new
  format, oldest-format-preserving (don't rewrite history's *content*,
  just its structure).

### Modified (documentation/process only — no schema, no `src/` change)

- `planning/context-gaps/TEMPLATE.md` — add the controlled-vocabulary
  discard-reason values (§3.3) to the existing free-text `curation`
  field's guidance; no field renamed, no existing entry needs editing.
- `.claude/agents/knowledge-curator.md` — add the `context-observations/`
  triage responsibility + the investigate-vs-record rule (§4.3/§5).
- `.claude/agents/context-evaluator.md`,
  `.claude/agents/reference-project-tester.md` — one-line pointer change
  from `context-use-log.md` to `context-observations/`, per §5.
- `planning/agent-led-workflow.md` step 4 — currently says "add a
  `context-use-log.md` entry"; retarget the same instruction at
  `context-observations/`, no other change to the step.
- `CLAUDE.md` — **only if** anything in §8's migration needs a policy
  statement beyond what §8 in isolation covers (unlikely; flag for
  explicit review under §0's diff-approval rule if it turns out to be
  needed — this plan doesn't currently see a required `CLAUDE.md`
  change).

### Explicitly NOT changed

- `src/codecompass/graph.py` schema — zero new tables/columns.
- `src/codecompass/relation_enrichment.py`,
  `src/codecompass/enrichment.py` — zero changes; the existing
  content-hash queue already satisfies the requirement.
- `src/codecompass/cli.py` — no new subcommand (§6.1).
- `.claude/agents/` roster membership — no agent added or removed.
- `decisions/0051` — not superseded; this phase extends its "sibling
  queue" pattern to a third queue, consistent with, not contradicting,
  its reasoning.

### 6.1 CLI / agent interface — recommend adding nothing this phase

Every operation the prompt sketches (`context audit`, `context
observations`, `context review`, `context request`) is already directly
achievable by an agent with `Read`/`Grep`/`Edit` against
`planning/context-gaps/` and `planning/context-observations/` — exactly
how `context-gaps/` already works today, with zero CLI surface. Adding a
`codecompass context ...` command family would mean **auditing
non-authoritative planning documents through the same CLI that promises
"authoritative, mechanically-derived facts only"** — a framing risk the
prompt's own key invariant warns against, and unjustified complexity
against "recommend only the minimum surface required." If a real need
emerges (e.g., a human wants a one-command summary without opening
files), that's a candidate learning to file *after* this phase ships and
gets used, not something to pre-build now.

### 6.2 ADRs

No new ADR is required to *ship the record-format generalisation and the
curator brief extension* — this is documentation/process, the same
category Phase 43c's `context-use-log.md` introduction itself didn't
need a dedicated ADR for (`decisions/0051` covers the request side; the
observation side was never a boundary question, just a format one).
**An ADR *is* required later, per existing policy, the moment any
specific `detector_gap`/`graph_capability_gap` is actually implemented**
— that's `decisions/0045`'s and `conditional-generalisation.md` §3's
existing standing requirement, unchanged by this phase.

---

## 7. Test plan

### Unit tests

- `context-gaps/TEMPLATE.md`'s widened discard-reason vocabulary: extend
  `scripts/check_user_docs.py`'s existing learnings-field-presence check
  pattern (`check_learnings_candidate_fields`) with an equivalent
  `check_context_gap_fields`/`check_context_observation_fields` (mirror,
  don't duplicate logic) verifying every `CG-NNN`/`OBS-NNN` entry has its
  full required-field set — this project already has exactly this shape
  of check for `learnings/inbox.md`; the test plan for this phase is
  "add the same check for the other two queues," not invent a new
  testing approach.
- Natural-key edge-identity round-trip: given a `doc_relations_edges` row
  and its `doc_relation_enrichment` counterpart, confirm the tuple
  written into an `OBS-NNN`/`CG-NNN` "edge identity" field matches
  exactly what `relation_enrichment.py` already uses as its own natural
  key — a pure data-consistency test, no new code path, just confirming
  the plan's §3.1 claim holds against the real schema.
- `_compute_content_hash` reuse: confirm no second hash function is
  introduced anywhere in this phase's diff (a grep-based regression
  test, the same spirit as `check_generated_artifacts_match_source`).

### Integration tests

- End-to-end walk of §4.3's state machine against a synthetic
  `OBS-NNN` entry: `recorded` → (simulate `EDGE_MISLEADING`) →
  `investigating` → `resolved`, confirming the resolution field ends up
  pointing at a real `CG-NNN`/`L-NNN`, not a dangling reference.
- Confirm `codecompass sync`/`check` behaviour is **completely
  unaffected** by anything in `planning/context-observations/` —
  i.e. a regression test that runs `sync` against a repo containing a
  populated `context-observations/inbox.md` and asserts the resulting
  `context-graph.db` is byte-identical to a run without it. This is the
  single most important test in the whole plan: it's the mechanical
  proof of the "planning-folder observations never touch the graph"
  invariant, not just a doc claim.
- `check_user_docs.py --strict` clean against a repo with both old-style
  (pre-migration) and new-style entries present simultaneously, to cover
  the migration window (§8) without forcing an atomic cutover.

### Regression tests

- Full existing suite (currently 557 passed / 2 skipped) must stay
  green — this phase touches no `src/codecompass/` runtime path other
  than possibly `scripts/check_user_docs.py`'s check list, so the
  existing `test_check_user_docs.py` module is where new tests land,
  following its own established per-check-class pattern.
- `agent-led-workflow.md` step 4's existing tests/expectations (if any
  exist as doc-checks) re-verified against the retargeted
  `context-observations/` pointer.

### LedgerKit re-evaluation

Not a separate new evaluation type — **reuse Phase 51's own precedent
directly**: once the record-format migration lands, re-file Phase
45/46/49/51's own historical Ledgerkit findings *as* `context-observations/`
entries (not a new evaluation, a format migration of already-true
history, §8), and confirm the resulting file passes the new
`check_context_observation_fields` check. This is the cheapest possible
"does the new format actually hold real data" test, using data that's
already known-correct rather than manufacturing a fresh scenario.

---

## 8. Migration plan

| Existing mechanism | Disposition | Detail |
|---|---|---|
| `context-graph.db` schema/detectors | **keep, unchanged** | Zero schema change. |
| `*_enrichment` tables + `select_candidates` | **keep, unchanged** | Already satisfies the "enrichment queue" requirement; explicitly documented as such (§1.2) so a future session doesn't try to rebuild it. |
| `planning/context-gaps/` | **keep, generalise in place** | Same files, same IDs, same primary status enum; only the discard-reason vocabulary inside the existing `curation` field gets a controlled list (§3.3). No `CG-NNN` is renumbered or moved. |
| `planning/context-use-log.md` | **merge into new `context-observations/`, then deprecate** | The file's 11 existing entries are individually re-filed as `OBS-001`…`OBS-011` (chronological, preserving their real dates/phases/content verbatim, just reshaped into the new fields) into `planning/context-observations/inbox.md`. The old file gets a one-line pointer ("superseded by `planning/context-observations/`, see there for anything after `<date>`") rather than being deleted outright — preserves git history's readability for anyone diffing an old commit. |
| `planning/context-health.md` | **keep, unchanged** | Different question (forward-looking adequacy vs. past experience); not part of this lifecycle. |
| `planning/learnings/` | **keep, unchanged** | Already the correct destination for "how we should work" observations; this phase doesn't touch its classification table (`learning-lifecycle.md` §4). |
| `.claude/agents/knowledge-curator.md` | **extend** | §5/§6. |
| `.claude/agents/context-evaluator.md`, `reference-project-tester.md` | **retarget one pointer line each** | §5/§6. |
| `agent-led-workflow.md` step 4 | **retarget one pointer** | §6. |
| `decisions/0051` | **keep, cited, not superseded** | This phase's own record explicitly extends its "sibling queue, one curator" pattern; worth a short note in `decisions/0051`'s own Consequences section (an append, per this project's append-only-ADR convention) rather than a new ADR, since no boundary changes — **flag this specific edit for explicit review**, since ADR files are otherwise treated as historical and this would be the first addition to `0051` since Accepted. |

**No mechanism is removed.** The only rename/restructure is
`context-use-log.md` → `context-observations/`, justified specifically
because it's the one piece the current-state assessment (§1.4) found
genuinely under-structured relative to its own stated job.

---

## 9. Phased implementation sequence

Smaller and more consolidated than the prompt's own sketch (A–I),
because inspection found several of those steps already done:

**Phase N.1 — Data model + migration (no agent-brief changes yet)**
- Create `planning/context-observations/{README,TEMPLATE}.md`.
- Migrate `context-use-log.md`'s 11 real entries into
  `context-observations/inbox.md` as `OBS-001`…`OBS-011`, verbatim
  content reshaped into the new fields (§8) — this is a genuine
  test of the schema against real data before any agent brief depends
  on it.
- Add the discard-reason controlled vocabulary to
  `context-gaps/TEMPLATE.md`.
- `scripts/check_user_docs.py`: new `check_context_observation_fields`
  (mirrors `check_learnings_candidate_fields`).
- Verification: `pytest`/`ruff`/`check_user_docs.py --strict` clean;
  the sync-byte-identity regression test (§7) passes.

**Phase N.2 — Agent brief + workflow updates**
- Extend `knowledge-curator.md` (§5).
- Retarget `context-evaluator.md`/`reference-project-tester.md`/
  `agent-led-workflow.md` step 4 pointers.
- No `src/` change.

**Phase N.3 — First real exercise + documentation consolidation**
- The next reference-project phase (whichever comes next after this
  milestone's own Stage-D-vs-Stage-F/G decision) files its observations
  directly into the new format — the genuine end-to-end proof, following
  this project's own established practice of proving a mechanism on real
  work rather than a synthetic fixture (see Phase 43's dogfood, Phase
  43c's own first exercise).
- `decisions/0051` gets its Consequences-section append (§8), reviewed
  explicitly per this file's own note above.
- `architecture/overview.md` / `ai-docs/README.md` reconciled if either
  describes `context-use-log.md` by name (a `docs-maintainer` pass).

Three phases, not nine — the prompt's A–I sketch assumed more net-new
construction than inspection found necessary. If review disagrees and
wants finer-grained phases (e.g. splitting N.1's migration from its
schema-check addition), that's a cheap re-split at review time, not a
reason to over-plan now.

---

## 10. Success criteria

Restating the prompt's own ten criteria against what this design
actually produces:

1. **A mechanical edge is synchronised.** ✅ already true today, unchanged.
2. **Its enrichment lifecycle is traceable.** ✅ already true
   (`select_candidates` + `content_hash`), unchanged.
3. **An agent consumes it.** ✅ already true (`query relations` etc.),
   unchanged.
4. **Agent feedback can be recorded without mutating graph truth.** ✅
   already true today (`context-use-log.md` never touches
   `context-graph.db`); this phase makes the record *structured* rather
   than changing the guarantee.
5. **A missing relationship can be requested.** ✅ already true
   (`context-gaps/`), unchanged mechanism.
6. **An investigation can document why it's missing.** ✅ already true
   (curator's `curation` field), sharpened vocabulary only.
7. **A deterministic detector improvement can be linked to that
   request.** ✅ already proven for real (`CG-002` → Phase 49).
8. **A later sync establishes the new authoritative edge.** ✅ already
   proven for real (Phase 49's `_DEFAULT_GLOBS` entry + Phase 51's live
   re-check).
9. **The complete history remains auditable.** ✅ already true (git +
   `planning/**`); the migration (§8) makes one previously-unstructured
   part of that history queryable the same way the rest already is.
10. **A graph rebuild does not erase that history.** ✅ mechanically
    guaranteed by file location (`planning/` is untouched by `sync`),
    proposed as an explicit regression test (§7) so it's asserted, not
    just assumed.

**Additional, phase-specific success criterion this plan adds:** every
one of `context-use-log.md`'s 11 existing entries migrates into
`context-observations/inbox.md` with zero information loss and passes
the new field-presence check — the concrete, checkable proof that the
generalisation (§1.4/§3.2) actually closes the one real gap this
assessment found, rather than just restating what already worked.

---

## Answering the final design question

> Can CodeCompass learn from the context agents actually need, without
> ever confusing an agent's opinion about a relationship with
> mechanically established project truth?

**Yes, and it already does** — `decisions/0051` drew that line before
this prompt was written, and `CG-002`'s real history (this milestone) is
the proof: an agent's opinion ("`dev-docs/` should be visible") went
through `candidate → recurred → promoted-to-roadmap → implementation →
sync`, and only *after* a mechanical detector change and a real
`codecompass sync` did the underlying content become reachable via
`query relations` — the opinion itself never became a graph row, at any
point, and the two independent audits this session ran (`docs-reconstructor`,
`release-phase-auditor`) each independently re-verified that boundary
held. This plan's job is to make sure the *other* half of "context
experience" (not just "what's missing" but "was what's there any good")
gets the same discipline — nothing more, nothing less.
