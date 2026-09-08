# Conditional technical-dependency / evidence plan (required output 10)

Candidate approaches for generalising CodeCompass's model beyond
`package → pinned version → upstream source → generated context`, with a
strict separation of what is **evidenced**, what is **hypothesis**, and
what is **deferred**.

**Nothing in this document is committed.** Stage E (Phases 56–58) is
`CONDITIONAL` on GATE DD (gate G7). This file structures that gate's
decision and pre-loads candidate designs so the deciding session isn't
starting cold.

## 1. Evidence status of each idea (as of this planning session)

### 1.1 Already supporting the need — nothing yet
No reference-project evaluation has run. Zero findings exist. Every idea
below is at best a hypothesis until Stage B/D produces evidence.

The **strongest prior signal** (not yet a finding, but concrete): both
chosen reference projects have ≈0 runtime package dependencies, and their
real technical context is executables / specs / manuals / browser APIs.
If Stage B/D confirm that CodeCompass produces near-empty, low-advantage
output for both, *that* is the evidence — recorded via
`context-quality-evaluation.md`, consolidated at Phases 47 and 55.

### 1.2 Hypotheses awaiting reference-project validation

| Hypothesis | Would be confirmed by | Candidate design (§2) |
|---|---|---|
| v1 needs a generalised **technical-dependency** concept | recurring "CodeCompass cannot represent dependency X" findings across ≥2 tasks and ≥1 project | §2.1 |
| v1 needs an **executable** dependency kind | Ledgerkit Phase 54 shows relating hledger-behaviour evidence is materially useful | §2.2 |
| v1 needs a **reference-doc / spec / manual** dependency kind | Technical Clipper (CommonMark) *and/or* Ledgerkit (hledger manual) Phase 53 show indexed+related reference material beats direct reading | §2.3 |
| v1 needs first-class **provenance** (distinct source kinds) | recurring "context was misleading because a doc-statement / agent-inference was shown like a source-fact" findings | §2.4 |
| v1 needs a **browser/platform-API** dependency kind | Technical Clipper tasks recurringly need DOM/Chromium-API context CodeCompass can't give | §2.5 |
| task-oriented retrieval needs new **edges** (not just new joins) | Phase 48 scoping shows the "what matters for this task" map can't be built from existing graph data | §2.6 |

### 1.3 Explicitly deferred (not v1 regardless of Stage B/D)

- A **universal dependency ontology** covering every kind in the vision
  doc's list (protocol, standard, file format, behavioural contract, …)
  adopted because it's architecturally elegant. Forbidden by the task:
  *"Do not implement a universal dependency ontology merely because it
  appears architecturally elegant."*
- The full **`Dependency` / `Evidence` / `Observation` / `Claim` /
  `Verification` / `Decision`** class hierarchy as named concepts, unless
  Stage D demonstrably requires that many distinctions. Default to
  something simpler.
- CodeCompass running experiments (hledger, a browser, fuzzers) — a hard
  non-goal (`README.md` §1.9).
- MCP server (existing Phase 25) — deferred independently.

## 2. Candidate designs (sketches for the GATE DD session)

All designs share two constraints: **additive schema change** (the
context graph rebuilds deterministically — new tables/columns, then a
migration, never a big-bang rewrite; `migration.md`), and **`package`
stays a first-class, unchanged-behaviour kind**.

### 2.1 Generalised `technical_dependency`
- New table `technical_dependencies(id, name, kind, ...)` where `kind` is
  a **small closed set** — starts `{package}`, gains only kinds that
  earned it at GATE DD (likely `executable`, `reference_doc`).
- Existing `vendors` becomes a view / the `kind='package'` rows, or
  `vendors` stays and `technical_dependencies` references it — decided by
  which is less migration risk (Phase 56).
- Existing `uses_edges`, `documents_edges`, `doc_relations_edges` gain a
  nullable `technical_dependency_id` alongside their existing
  `vendor_id`, so package behaviour is untouched.

### 2.2 `executable` kind
- Identity: a command name + a resolved version (`hledger --version`).
- Grounded by: its `--help` / man page / manual text (fetched or
  vendored, registered like `vendor_doc`), **not** by running it inside
  CodeCompass.
- Relates to: local code that shells out to it (mechanical detection —
  `subprocess`/`Popen`/`execa` call-site scan, same shape as import
  detection), and to behavioural-evidence records supplied by external
  tooling.

### 2.3 `reference_doc` kind
- Identity: a named spec/manual + a version/revision (CommonMark 0.31.2;
  hledger 1.52 manual).
- Content: vendored text, chunked by the existing `doc_chunking`
  mechanism (Phase 32).
- Relates to: local implementation (mention detection + the existing
  `doc_relations_edges`), tests, and ADRs. This is the **smallest** new
  kind — it mostly reuses Phase 21/27/29/32 machinery pointed at a new
  source.

### 2.4 Provenance / evidence
- Minimal version: a `source_kind` enum column on the enrichment / claim
  tables — `source_fact` / `doc_statement` / `spec_requirement` /
  `observed_behaviour` / `test_result` / `decision` / `agent_inference` —
  plus `evidence_ref` (a file:line or URL + revision) and `confidence`
  (`verified` / `stated` / `inferred`).
- Consumers (`query`, generated Skills, "what matters for this task")
  render the kind + confidence so a low-confidence claim is never shown
  like a source-derived fact.
- The full named-class ontology is only reached if GATE DD shows the enum
  is genuinely insufficient.

### 2.5 `browser_api` / `platform_api` kind
- Lower priority — MDN-style reference text as a `reference_doc`
  specialisation may cover it. Only its own kind if Technical Clipper
  findings show DOM/Chromium context is both recurringly needed and
  poorly served by a generic `reference_doc`.

### 2.6 Task-oriented retrieval edges
- If existing joins suffice (Phase 48 finds the map is
  `local impl + callers/callees + tests + dep + version + APIs used +
  docs + ADRs + gaps`, all already in the graph): **no schema change**,
  just a new query + entry point.
- If not: the specific missing edge, backed by the specific finding,
  with an ADR.

## 3. The GATE DD decision procedure (Phase 55)

1. List every "cannot represent" / "misleading source kind" / "no better
   than direct reading" confirmed finding from Phases 47 and 55.
2. For each, name the **smallest** candidate (§2) that would fix it.
3. Take the **union** of those smallest candidates — that is the Stage E
   scope. If the union is empty → Stage E is skipped; redefined v1 = the
   Stage C product.
4. Write one ADR per adopted abstraction, each arguing the specific gap +
   the false-positive/cost tradeoff (the rigor every AI-boundary decision
   in this project has had — `doc-graph-precision-roadmap.md` §"The
   boundary all three phases share").
5. Gate G7: user approves the scope + ADRs before Phase 56 starts.

## 4. Non-negotiables carried into Stage E

- Determinism-first boundary holds: any new kind's *relationships* are
  mechanically detected; AI only describes them.
- `package` / npm / PyPI / Cargo keep working with no behaviour change
  (`migration.md` §3; Phase 58 + Phase 59 regression check).
- Every abstraction is independently revertible (phase-per-commit).
- CodeCompass still does not run anything it's grounding.
