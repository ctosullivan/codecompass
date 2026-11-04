# Phase 87: Documentation Schema and Knowledge-Compiled Documentation — plan

**Status: amended, ready for implementation review.** The first
planning pass (§I) returned READY WITH NON-BLOCKING OBSERVATIONS
(2026-11-04) but a second, implementation-focused independent review
identified six implementation-contract gaps (§J below records the
finding list and resolution). This amendment (2026-11-04, same day)
resolves all six by replacing the affected parts of §A.2/§A.4/§A.5,
§C, §D.2, §F, and §G with implementation-ready contracts grounded in
direct re-inspection of the real code (not re-assumed from the first
pass's own prose). §K records the post-amendment independent
planning-review verdict. Strategic architecture (§A.1/A.3/A.6-A.9),
the minimum publication suite (§E), and the matched-baseline
evaluation's overall shape (§F) are preserved, not reopened, except
where a finding required a correction named explicitly below.

Governing scope: `planning/v2-roadmap.md` §"Phase 87 — Documentation
Schema and Knowledge-Compiled Documentation" (10-point roadmap-depth
sketch); `decisions/0084` §2 (Phase 87 row — new phase, objective
summary); `decisions/0085` §5 (minimum publication suite, user-defined
schema, 9-step compilation pipeline, editorial requirements) and §6
(corrected documentation-quality baseline methodology). Prerequisites:
Phase 84 (Consolidated Knowledge API — `done`) and Phase 86
(Knowledge-Placement and Code-Quality Review — `done`, both corrective
passes closed, `8b915ac`/`e98c207`).

## 0. Objective and value

Professional project documentation — clear, concise, genuinely useful
to its stated audience, not merely technically accurate Markdown —
becomes an explicit, repeatable *output* of the canonical knowledge
system, via a user-defined, versioned schema (audience, purpose,
required sections, depth/verbosity, tone/style, required examples,
evidence requirements, acceptance criteria), rather than a one-off
clean-room exercise repeated by hand each time a doc goes stale
(`decisions/0084` §2, `decisions/0085` §5).

**No second source of project truth.** The compiler reads Phase 84's
`knowledge_api` and `planning/knowledge/` only. It does not cache,
duplicate, or independently assert canonical facts. Every generated
claim must trace to a real knowledge record or be flagged as a gap —
never fabricated to fill a schema section.

## A. Verified architecture map — what exists, what's reused, what's new

Each subsection below was independently verified against the real
current implementation, not assumed from roadmap/decision prose, per
this phase's own instruction not to mistake a planned capability for an
implemented one (two cases below found the opposite error too — real
capability that the roadmap had described as if it still needed
building).

### A.1 Phase 79/80 clean-room documentation reconstruction — real, agent-based

`planning/phase-80-codecompass-documentation-reconstruction.md` §2-6
defines a 5-stage pipeline: frozen snapshot → dispatch
`implementation-reconstructor` (model-blind: no narrative docs, source/
tests/schema/config only) → dispatch `domain-skeptic` in its comparison
mode (classify alignment between the reconstruction and a frozen
knowledge snapshot, both directions, never forcing either side to
match) → fresh draft → reconciliation/publication. This is **agent
orchestration**, not a reusable script or library call. Phase 87 reuses
its *discipline* — model-blind reconstruction, independent comparison
before trusting a gap claim — as the precedent for the clean
reconstruction mode (§D.1), not as a callable component.

### A.2 Phase 81B clean-room isolation and broker — real, mechanically enforced

Under `scripts/`, four real, independently-runnable components:

- `prepare_cleanroom_branch.py` — exports an explicit, manifest-bound,
  allowlisted set of files at a pinned revision into a staging tree via
  real git-object extraction (`_export_path`, `_git_tracked_files_at_revision`,
  `_export_file_at_revision`), content-hashed for later integrity
  verification (`sha256_file`/`_canonical_digest_of_hashes`). Critically,
  `UnclassifiedNarrativeShapedFileError` makes narrative-shaped content
  (anything that reads like existing prose documentation) a **hard
  export failure** unless explicitly allow-listed — this is the
  mechanical enforcement of "the clean-room writer does not access
  existing narrative documentation," not merely a documented convention
  the compiler could accidentally violate.
- `verify_cleanroom_isolation.py` — a real sandbox preflight (actual
  `unshare`/`pivot_root`, not a simulated check) with named probes:
  evidence readable, output writable, parent-host-paths unavailable,
  sibling-repositories unavailable, git-history unavailable, git-remotes
  unavailable.
- `cleanroom_broker.py` — runs on the trusted host, holds real model
  credentials, exposes exactly one operation over a Unix socket:
  `run_inference(system_prompt: str, messages: list[dict]) -> dict`
  (`{ok, output, usage}`). No credential, tool, filesystem path, or
  shell access crosses into the sandbox.
- `cleanroom_broker_client.py` — the only thing bind-mounted into the
  sandbox; a minimal socket client calling the broker's one operation.
- `cleanroom_prompt_assembler.py` — runs *inside* the sandbox;
  `assemble_evidence_blob(evidence_root: Path) -> str` builds one prompt
  from the isolated, exported tree, then calls the broker client.

**Reused directly, unchanged, with one corrected assumption** (amendment
finding B): `prepare_cleanroom_branch.py`'s export is **whole-repository
and hardcoded** — `ALLOW_PATHS`/`EXCLUDED_PATHS` are module-level
globals (`:66-124`), not parameters, and `cmd_build` always walks the
full allow-list. There is no existing way to ask it for a narrower,
section-specific export. Critically, `EXCLUDED_PATHS` already excludes
`planning/knowledge`, `planning/CONTEXT.md`, `planning/ROADMAP.md`,
`planning/learnings`, and `planning/retros` unconditionally (`:101-105`)
— the raw knowledge store never crosses into any clean-room export
today. What *does* cross is `planning/documentation-handoff`
(`:84`) — a **separately lead-curated handoff package**, prepared
*outside* this script by a trusted process, then exported verbatim like
any other allow-listed path. This is the real, load-bearing precedent
Phase 87 follows (§C step 6, new): the lead-side compiler resolves and
hydrates a section's knowledge packet entirely outside the sandbox,
writes it to a new staging file under a new
`planning/documentation-handoff/section-packets/` directory, and only
*that* file — never raw `planning/knowledge/*.yaml` — is allow-listed
for export. `UnclassifiedNarrativeShapedFileError` (`:54`, raised
`:199`) does **not** automatically cover this new path: it triggers
only for `.md`/`.rst`/`.txt` files swept in under three broad,
pre-existing allow-paths requiring classification (`src`, `tests`,
`scripts`, `:134`) — a new payload directory is simply unprotected by
it. Phase 87 therefore adds exactly one new, narrow allow-list entry
(`planning/documentation-handoff/section-packets/**`, JSON files only,
new explicit classification check mirroring the existing one's shape)
to `prepare_cleanroom_branch.py` — a stated, justified, minimal
extension, not an unexamined claim that the unchanged interface already
supports this. Everything else in this layer (the manifest-hash
pattern, `verify_cleanroom_isolation.py`'s preflight, the broker's one
`run_inference` operation, the assembler) is reused as-is — see §C
step 6 for the adapter this phase actually owns.

### A.3 Phase 81 canonical/intermediate knowledge — real

`src/codecompass/knowledge_intermediate.py`: six record kinds
(Observation/Evidence/Claim/Derivation/Decision/Requirement, id
prefixes `OBS`/`EV`/`CL`/`DE`/`DEC`/`REQ`), flat hand-rolled YAML
parsing (deliberately not imported by `scripts/`, by this project's own
established separation). `semantic_change: bool` already exists on
reconciliation candidates (`decisions/0074`) and is the existing,
reusable mechanism for Phase 87's presentation-vs-semantic split (§D.3)
— no new field or model needed. The `codecompass-grounded-by` HTML
comment marker convention (`parse_grounding_markers`, a `region:<id>`
token that survives reorder/insertion) is real and already supports
exactly Phase 87's own "provenance on demand without cluttering
ordinary prose" requirement — reused directly.

### A.4 Phase 82/83 contracts, Oracle, evidence currency — real

`src/codecompass/oracle.py` (`OracleContract`, `OracleResult`,
`parse_oracle_contract`, `parse_oracle_result`,
`evaluate_result_precedence`, `aggregate_contract`). **Correction
(amendment finding D)**: `OracleResult.outcome` is constrained to
exactly `{"PASS", "FAIL", "INVALID"}` (`oracle.py:186`) — `GAP` is
never a value of one result's own outcome. `GAP` exists only as
`CheckAggregate.state ∈ {"PASS", "GAP", "NOT_REQUIRED"}`, computed by
`aggregate_contract` *across every result for one check* — a separate,
aggregate-level concept from a different function than
`evaluate_result_precedence`, which returns only PASS/FAIL/INVALID for
one result. The plan's own claim-verification workflow (§C step 7)
distinguishes these explicitly rather than treating them as one flat
enum. A contract's check identifies *what* is verified through a
free-text `scope: str` field on `OracleCheck`, matched against an
Evidence record's own cited result (`evaluate_result_precedence:767-771`
requires an exact string match) — **there is no structured link from a
specific generated sentence to a specific check**; that connection is
by `scope`-string convention only, decided by whoever authored the
citing Evidence/Claim record. Phase 87's claim-to-evidence mapping (§C
step 7) cannot assume anything finer-grained exists already — matching
one generated sentence to one `scope` string is new judgment work.
Evidence-currency logic (is this result still valid against live
source, or stale/INVALID) lives entirely in `evaluate_result_precedence`/
`aggregate_contract` — reused as-is by the compilation pipeline's own
gap/staleness step (§C step 4) for any schema section whose evidence
requirement cites a behavioural claim.

### A.5 Phase 84 read-only knowledge API — real, substantial, already closely matches the pipeline's own shape

`src/codecompass/knowledge_api.py` (1660 lines): typed `get`/`search`/
`traverse`/`trace_evidence`/`epistemic_status`/`find_gaps`/
`get_context_packet`. Two functions are load-bearing for Phase 87, and
both already do most of what `decisions/0085` §5's pipeline steps 4-5
require:

- `get_context_packet(project_root, topic, *, max_items=20, max_chars=6000, repo_root=None) -> ApiResponse`
  — bounded, deterministic, fixed-priority (subject → 1-hop `depends_on`/
  `depends_on_reverse`/`supporting_evidence`/`contradicting_evidence` →
  gaps), deduplicated-by-id context assembly, with explicit
  `details.bounds.truncated` reporting rather than silent overflow
  (`_bound_context_items`).
- `find_gaps(project_root, slug=None, *, repo_root=None) -> ApiResponse`
  — six existing rules (`unverified_required_scope`, `contradiction`,
  `stale_test_citation`, `missing_contract`, `dangling_evidence_reference`,
  `dangling_dependency_reference`). This is pipeline step 4 ("identify
  material knowledge gaps before writing") — reused directly, not
  reimplemented.

**Correction (amendment finding A) — `get_context_packet` does not, by
itself, supply source material suitable for compiling grounded prose,
and the plan's first pass overstated what it returns.** Direct
re-inspection of `knowledge_api.py`:

- Every candidate item `get_context_packet` and `search()` return
  carries only `summary` — `_summarize_record` (`:389-394`):
  `" ".join(value.split())[:280]`, a **280-character truncation of the
  first non-empty `statement`/`decides`/`what_it_shows`/`what_was_done`
  field**, never the record's full content. `_bound_context_items`
  budgets `max_chars` against `len(candidate.summary)` — against the
  truncated string, not real evidence size.
- When `topic` is not an exact existing record id, `get_context_packet`
  falls back to `search(project_root, topic)` and uses **only
  `results[0]`** (`:1560-1569`) — a free-text topic can silently resolve
  to the wrong single record with no disambiguation signal surfaced to
  the caller.
- **No code anywhere interprets a `topic:`-prefixed string** (confirmed:
  zero matches for `"topic:"`-prefix parsing in `knowledge_api.py`,
  `knowledge_intermediate.py`, or `cli.py`). A schema's
  `required_knowledge: ["topic:installation"]` as drafted in §B below is
  fed literally into `search()`'s plain substring match and will almost
  certainly resolve to nothing.
- The only way to obtain a record's **complete, untruncated** content is
  `get(project_root, record_id) -> ApiResponse`, whose
  `details["fields"] = dict(record.fields)` (`:382`) is the real,
  full-hydration path — `record.fields` *is* the complete record content
  as authored (`KnowledgeRecord` has no separate raw/summary field at
  the storage layer; truncation is purely an API-response-shaping step).

**Corrected retrieval contract, replacing the first pass's "thin
topic adapter" claim**:

1. **`required_knowledge` resolves to real record ids, never
   `topic:`-prefixed strings.** The schema format (§B) is corrected:
   `required_knowledge` is a list of concrete record ids (`CL-0123`,
   `REQ-0045`, …) or, where the exact id is not yet known at
   schema-authoring time, a `discover:` -prefixed free-text query that
   the compiler resolves **once, at schema-validation time**
   (`check_doc_schema.py`), never silently at compile time — see point 2.
2. **Deterministic record selection.** For a `discover:<query>` entry,
   `check_doc_schema.py` calls `search(project_root, query)` and
   requires **exactly one** matching record id; zero matches is a
   blocking schema-validation failure (§G.5 test 7); more than one match
   is also a blocking failure (an ambiguous `discover:` query must be
   narrowed by the schema's author into an explicit record id or a more
   specific query — the compiler never guesses via `results[0]` the way
   `get_context_packet`'s own fallback does). A section's
   `required_knowledge` is therefore always a closed, concrete set of
   record ids by the time compilation runs — "what constitutes a
   complete required topic" is answered structurally: every id the
   schema names, resolved and present, is required; the compiler never
   decides partial coverage is good enough.
3. **Full hydration via `get()`, never bare summaries.** `doc_compiler
   .resolve_section_packet(schema_section)` calls `knowledge_api.get(id)`
   for every resolved id and uses `details["fields"]` — the complete
   record — as the evidence unit. `search()`/`get_context_packet()` are
   used only for **discovery** (resolving a `discover:` query, or
   surfacing 1-hop related records as *candidate* additional context,
   clearly labelled as such and never substituted for a required id's
   own full content).
4. **Real source evidence, relationships, and Oracle results** are
   reached the same way every other consumer reaches them — `get()` for
   the record, `find_gaps`/`traverse` for its relationships, and for any
   record whose `supporting_evidence` cites an Oracle result,
   `oracle.py::evaluate_result_precedence`/`aggregate_contract` for that
   result's real, current PASS/FAIL/INVALID/GAP status (§A.4, corrected)
   — never a cached or re-derived judgement.
5. **Evidence currency, authority, revision, and scope checks**: before
   a resolved record is added to a section's packet, the compiler checks
   (a) `derive_epistemic_profile`'s `unconfirmed_scopes`/
   `known_gap_scopes` for that record (stale/no-evidence, §A.4), (b) for
   any Oracle-backed claim, that the cited result's
   `oracle_contract_content_hash` still matches the live contract
   (`check_contracts.py`'s own `contract-result-integrity-mismatch`
   rule, reused, not reimplemented), and (c) the record's own `kind`
   against the schema section's declared `min_claim_status` bar — a
   record failing any of these is **not silently dropped**: it is
   recorded as a named gap for that section (§C step 4).
6. **Deduplication and budgeting against real serialized evidence.** The
   packet handed to the clean-room writer (§C step 6) is the
   deduplicated-by-id concatenation of every resolved record's full
   `fields` content, truncated only if the *serialized, hydrated* total
   exceeds the schema section's own declared budget (a new
   `max_evidence_chars` schema field, §B) — never budgeted against
   `summary` length, and never silently dropping a *required* record to
   fit the budget (exceeding the budget with required content present is
   a blocking schema/compile-time error — "widen the budget or narrow
   the section," never "silently truncate required material").
7. **Explicit handling of truncated packets, ambiguous search results,
   missing records, and incomplete evidence**: every one of these is a
   named, reported outcome (§C step 4's gap report), never a silent
   partial success — required knowledge never disappears because a
   retrieval budget or search heuristic selected too little material, per
   this phase's own governing requirement.

No competing knowledge API or canonical store is introduced — every
point above calls only `knowledge_api`'s existing public functions
(`get`, `search`, `find_gaps`, `traverse`) plus `oracle.py`'s existing
functions; `doc_compiler.py` adds a resolution/hydration/budgeting
*policy* on top, never a second storage or query layer.

Note for the plan's own accuracy: `cli.py`'s `knowledge_app` already
exposes `get`/`search`/`trace`/`gaps` as thin CLI wrappers over this
API (`cli.py:1726-1783`), but the older, pre-Phase-84 `query_app`
sub-verbs (`vendors`/`vendor`/`symbol`/`skills`/`relations`/`topology`/
`source`/`source-symbol`) remain independent, un-migrated
(`decisions/0085` §2 narrowed this scope deliberately). Irrelevant to
Phase 87's own design, since the compiler calls `knowledge_api`'s
Python functions directly, never shells out through the CLI — noted
here only so this plan does not imply a false "unified CLI" state.

### A.6 Phase 85 curation and knowledge-quality validation — real

`scripts/check_self_knowledge_quality.py` composes `knowledge_api`'s
`find_gaps`/`knowledge_intermediate` functions directly, adding no
independent logic of its own — the established precedent for how a
Phase-87-owned script should be built on top of Phase 84's API rather
than re-deriving traversal/gap logic. `docs/workflows/
self-curation-loop.md` documents the human/agent review discipline
Phase 87's own incremental-maintenance mode (§D.2) follows.

### A.7 Phase 86 Knowledge Placement Policy — real (this session's own prior work)

`scripts/check_knowledge_placement.py`'s two diagnostics
(`decision-citation-exists`, `decision-citation-superseded`) govern
where a `decisions/NNNN` citation may legitimately live in *source
code* docstrings/comments. Directly relevant to Phase 87's editorial
requirements (§E): generated documentation must not misplace knowledge
the same way Phase 86's own real dogfood (`source_resolution.py`)
originally did — citing superseded context as if still current. The
compiler's gap/staleness step (§C step 4, reusing `find_gaps`/Oracle
currency) is this same discipline applied to *generated prose* instead
of source comments.

### A.8 `spec_docs.py` and existing doc-tracking conventions — real, but narrower than "compiler machinery"

`src/codecompass/spec_docs.py::scan_spec_docs(project_root) -> list[DocArtifactRow]`
is a **mechanical detector** of existing human-authored doc files
(kind=`spec_doc`), used only to populate relationship-graph rows — not
a generator, not a drift auditor, not anything resembling compilation.
Reusable only as an input signal for incremental-maintenance mode's
"which existing file does this section live in" lookup (§D.2); the
compiler itself is genuinely new on top of it. `docs-reconstructor`
(per-phase drift audit) and `docs-maintainer` (reconciliation) are real
existing agent roles (`.claude/agents/`) whose write boundaries and
independence requirements Phase 87 does not alter — the compiler is a
new generation capability, not a replacement for either.

### A.9 Existing documentation suite — real coverage already substantial; the named gap is accessibility, not absence

Direct inspection (not assumed from `decisions/0085` §5's own
description) found every file in the minimum suite table (§E) already
exists: `README.md` (101 lines), `docs/getting-started.md` (114
lines), `docs/reference/cli.md` (252 lines), `docs/reference/
configuration.md` (38 lines), `CONTRIBUTING.md` (266 lines), `docs/
development/contributing.md` (35 lines), seven files under `docs/
concepts/`, three under `docs/architecture/`. `decisions/0085` §5
named "an explicit page on epistemic distinctions and the
reconciliation loop" as "a named gap, not assumed already covered" —
direct reading of `docs/concepts/knowledge-model.md` (41 lines) shows
this is **substantially covered already** (INTENDED/OBSERVED/VERIFIED/
CONTESTED, the dual-hash reconciliation loop, a pointer to `docs/
workflows/knowledge-reconciliation-loop.md`), but written in this
project's own dense, citation-heavy internal-documentation register
(`decisions/0082`, `derive_epistemic_profile`, etc.), not in the
plain, example-led register `decisions/0085` §5's own editorial
requirements demand for a reader-facing concept page, and contains
**zero worked examples** — itself a genuine content gap, not purely a
register/tone issue, since Phase 87's own editorial bar requires
example-led writing. **The real gap is editorial accessibility plus
missing examples, not missing conceptual content** — Phase 87's own
editorial-quality assessment step (§C step 8) identifies both; closing
the example gap may require new worked-example prose even where no new
concept needs explaining. This plan corrects `decisions/0085` §5's
framing accordingly rather than repeating it uncritically.

## B. Documentation schema

**Format**: YAML, `schema_version: <int>` top-level field — matching
this project's own existing schema-file convention (e.g.
`oracle-contract.yaml`'s own `schema_version: 1`), not a new format
convention invented for this phase. One schema file per generated
document, stored alongside its target: `docs/<path>.schema.yaml` for a
file at `docs/<path>.md` (e.g. `docs/getting-started.schema.yaml` for
`docs/getting-started.md`); `README.schema.yaml` at the repo root.

**Fields** (per `decisions/0085` §5, each required unless noted):

```yaml
schema_version: 1
document: docs/getting-started.md          # the file this schema governs
audience: "a developer new to CodeCompass, has not read any other doc"
purpose: "get a working CodeCompass installation and run a real first query within 10 minutes"
sections:
  - id: install
    title: "Installation"
    required_knowledge: ["CL-0031", "discover:dependency installation requirements"]
      # concrete record ids, OR a one-time `discover:<query>` resolved to
      # EXACTLY one id at schema-validation time (check_doc_schema.py) --
      # never a `topic:` string (nothing in knowledge_api interprets one,
      # amendment finding A) and never resolved freshly on every compile run
    max_evidence_chars: 4000                 # budget against REAL hydrated record content (knowledge_api.get()),
                                              # never against get_context_packet's own 280-char `summary` field
    depth: brief                            # brief | standard | detailed
    tone: instructional                     # instructional | reference | narrative
    requires_example: true
    requires_tested_example: true           # must be independently executed in the sandboxed harness, §C step 7
    example_comparison_mode: exact          # exact | normalized_whitespace | regex -- how real vs. expected output is compared
    evidence_requirements:
      min_claim_status: verified             # candidate | supported | verified -- generation refuses below this bar
      allow_unconfirmed_scopes: false        # decisions/0082's unconfirmed_scopes -- refuse by default, not silently promote
  - id: first-query
    ...
acceptance_criteria:
  - "An unfamiliar developer can install and run one real query without external help."
  - "Every command shown is independently executed against this repo and its real output used, not invented."
verification_method: "clean-environment onboarding exercise (§F) + independent reader evaluation"
provenance: on_demand                        # on_demand | inline | none -- codecompass-grounded-by marker usage (§A.3)
owner: lead                                   # who may edit this schema file; default "lead" per CLAUDE.md §1/§2
```

**Diátaxis** (tutorial/how-to/reference/explanation) is offered as a
*default value* for `sections[].tone`/`depth` combinations in a
starter schema template, never enforced structurally — a project
(including this one) may define sections that don't map onto any of
the four Diátaxis modes, and the schema format imposes no such
requirement.

**Versioning**: `schema_version` bumps only on a breaking field
change (a field removed, renamed, or its meaning changed); an additive
field change does not bump it. The compiler refuses to run against a
`schema_version` it does not recognise (fail closed, matching this
project's own `check_contracts.py`/Oracle precedent), rather than
guessing at a forward-compatible interpretation.

**Validation**: a new `scripts/check_doc_schema.py` (mirroring
`check_contracts.py`'s own `Finding`-with-`strict`-flag convention):
required fields present and well-typed; every `required_knowledge`
entry that is a concrete record id resolves via `knowledge_api.get`
(blocking if not); every `discover:<query>` entry resolves via
`knowledge_api.search` to **exactly one** record id (blocking if zero
or more than one — amendment finding A's deterministic-selection rule;
a resolved `discover:` entry is rewritten in place to the concrete id
it resolved to, so re-running the validator is idempotent and later
compiler runs never re-resolve a free-text query); a schema pointing at
knowledge that does not exist, or that is ambiguous, is itself a defect,
never deferred to compile time; `evidence_requirements.min_claim_status`
is one of the valid `learning-lifecycle.md`-style enum values;
`example_comparison_mode` (when `requires_tested_example: true`) is one
of `exact`/`normalized_whitespace`/`regex`; `document` path is unique
across all schema files (two schemas may never govern the same file).

**Sensible defaults**: a `codecompass docs schema init <path>` CLI
command (new, under a new `docs_app` Typer sub-app) scaffolds a schema
file with `depth: standard`, `tone: instructional`,
`requires_tested_example: false`, `min_claim_status: supported`,
`provenance: on_demand` — the common case for an internal concept page,
overridden explicitly for README/Getting Started's stricter
requirements (`requires_tested_example: true`, `min_claim_status:
verified`).

**Ownership**: schema files are edited by the lead (or an ad-hoc
implementer subagent under the lead's direction), same as any other
`planning/`-adjacent configuration — not independently owned by the
compiler or any generation agent. This mirrors `CLAUDE.md` §1's own
plan-before-implementing discipline: the schema *is* the plan for one
document's content, reviewed before compilation runs against it.

## C. Knowledge-compilation pipeline

Interfaces, in the 9-step order `decisions/0085` §5 specifies, each
step named against the real module/function it is built on (§A) or,
where genuinely new, named as new:

| # | Step | Built on | New work |
|---|---|---|---|
| 1 | Retrieve accepted knowledge through Phase 84's API only | `knowledge_api.get`/`search`/`find_gaps`/`traverse` | **new** (amendment finding A, corrected from the first pass): `doc_compiler.resolve_section_ids(schema_section) -> list[record_id]` — resolves every `required_knowledge` entry to a concrete, validated record id (concrete ids pass through; `discover:` queries were already resolved to exactly one id at schema-validation time, §B) — never calls `get_context_packet`'s own free-text fallback, which silently takes only the first search result |
| 2 | Resolve current source/verification evidence | `oracle.py` (`evaluate_result_precedence`/`aggregate_contract`), `knowledge_intermediate.py` (`derive_epistemic_profile`), `check_contracts.py` (`contract-result-integrity-mismatch`) | **new**: `doc_compiler.check_record_currency(record) -> CurrencyStatus` — per-record currency/authority/scope check (§A.5 point 5): unconfirmed/stale/contradicted records are flagged, not silently included |
| 3 | Map knowledge to required schema sections | — | **new**: `doc_compiler.map_section_to_knowledge(schema_section) -> list[record_id]` — identity function over step 1's already-resolved id list (the mapping *is* the schema's own `required_knowledge` field; no additional inference) |
| 4 | Identify missing/uncertain knowledge before generation | `knowledge_api.find_gaps`, step 2's currency checks | **new**: `doc_compiler.find_section_gaps(schema_section, resolved_ids) -> list[Gap]` — a section whose `evidence_requirements.min_claim_status` isn't met by every one of its own resolved ids (not "some" id anywhere in the project) is a **generation-blocking gap**, reported, never silently generated around; this is the depth check (L-075) applied to documentation — scope alone (the id resolves) is insufficient, the record's own currency/status must also clear the bar |
| 5 | Build bounded, section-specific knowledge packets | `knowledge_api.get` (full hydration, never `summary`) | **new**: `doc_compiler.resolve_section_packet(schema_section) -> EvidencePacket` — calls `get(id)` for every resolved id, concatenates the full `details["fields"]` content (deduplicated by id), truncates only if the *real serialized* total exceeds `max_evidence_chars` — and only among non-required supplementary context, never a required record (§A.5 point 6); `get_context_packet`'s 1-hop relation expansion may supply *additional*, clearly-labelled optional context beyond the schema's own required set, but never substitutes for it |
| 6 | Compose each section through the existing clean-room broker | `cleanroom_broker.run_inference`, `cleanroom_broker_client`, `cleanroom_prompt_assembler.assemble_evidence_blob`, `prepare_cleanroom_branch.py`'s manifest-hash pattern | **new** (amendment finding B) — the section-compilation adapter, `scripts/compile_doc_section.py` (new, sits alongside the other clean-room scripts rather than inside `src/codecompass/`, matching this project's existing convention that security-sensitive clean-room infrastructure lives under `scripts/`): (a) writes the hydrated `EvidencePacket` from step 5 to a new staging file under `planning/documentation-handoff/section-packets/<schema-slug>/<section-id>.json`, with a manifest recording the schema section, source revision, and a content hash of the packet (reusing `prepare_cleanroom_branch.py`'s existing hash-and-manifest *pattern*, §A.2 — not its hardcoded `ALLOW_PATHS`, which gains exactly one new, justified allow-list entry for this new path); (b) in clean-reconstruction mode, confirms no existing narrative documentation file is included in the export (the existing `UnclassifiedNarrativeShapedFileError` path plus the one new explicit check for the new payload directory, §A.2); (c) runs `verify_cleanroom_isolation.py` as a subprocess once per `compile_document` invocation (not re-run per section — its own preflight is a sandbox-construction check, not a per-call content check) and fails closed (aborts the whole compile run) on a non-zero exit; (d) invokes `cleanroom_broker_client`/`cleanroom_broker.run_inference` through its existing one-operation interface, unchanged; (e) the system prompt is a new, section-specific writing contract (below) naming the allowed output shape, the schema's `audience`/`tone`/`depth`, and a mandatory per-sentence citation convention; (f) **the adapter parses and validates the returned text itself** — `run_inference` performs no structural validation of its own output (confirmed: `cleanroom_broker.py` checks only transport-level shape, `cleanroom_prompt_assembler.py` prints the raw output), so trusting a model's own "I only used supported evidence" claim is never sufficient; (g) rejects (does not publish, reports instead) any returned content referencing a file path, section id, or citation outside what the adapter's own manifest declared as available |
| 7 | Independently validate technical claims and executable examples | `oracle.py` currency checks (step 2), a new constrained execution harness (below) | **new** (amendment findings C+D) — `doc_compiler.validate_section(generated_text, schema_section, packet)`, the full claim-verification workflow below, plus independent re-execution of every `requires_tested_example` section's shown commands inside the new sandboxed harness (§C's "Constrained execution harness" subsection) |
| 8 | Assess usefulness, clarity, audience suitability — distinct from factual validation | An ad-hoc `general-purpose` dispatch, never the generating model itself | **new**: a second, separate dispatch (never the same call/agent as step 6 or step 7) scoring the generated section against the schema's own `audience`/`tone`/`depth`/`acceptance_criteria` fields, briefed from a new written brief document (`docs/workflows/section-editorial-review.md`), mirroring `decisions/0094`'s existing precedent for Phase 86's own semantic/editorial reviewer (an ad-hoc dispatch, never a new standing roster agent — amendment finding F; no existing roster agent is a drop-in match, confirmed by direct inspection of `context-evaluator`/`docs-maintainer`/`docs-reconstructor`'s write boundaries, but a new standing agent is not justified by a single phase's reuse frequency, same reasoning `decisions/0094` point 1 already applied); a section can pass step 7 (every claim true) and fail step 8 (true but unreadable, wrong register, or useless to the stated audience) — reported as two independent verdicts, never collapsed into one |
| 9 | Preserve provenance on demand without cluttering ordinary prose | `codecompass-grounded-by` marker convention (`parse_grounding_markers`, §A.3) | none — direct reuse; emitted only when `schema.provenance` is `inline` or `on_demand` (and in the latter case, only behind a generation-time flag, never inline in the published file by default); every published section also always carries a `region:<section-id>` marker regardless of `provenance` setting, since §D.2's reconciliation (corrected below) depends on `detect_grounded_region_changes` being able to address it |

**The section-specific writing contract (step 6e, new)**: the system
prompt handed to `run_inference` requires the model to tag every
sentence presented as a factual claim with an inline marker citing the
specific record id(s) in its own evidence packet that support it (e.g.
`Installation requires Python 3.11+ {{cite:REQ-0045}}.`), and forbids
asserting anything without such a tag. This is what makes step 7's
claim-to-evidence mapping mechanical rather than a fresh fuzzy-matching
problem for every generated sentence — Oracle's own `scope`-string
convention (§A.4) already establishes that this project links a claim
to its evidence by an explicit, author-supplied token, not by free-text
inference; the writing contract applies the same discipline to
generated prose. The adapter (step 6g) strips `{{cite:...}}` tokens
from the published text (converting them to `codecompass-grounded-by`
markers when `provenance` warrants it, §A.3/§C step 9) and rejects any
tag citing a record id not present in the section's own resolved
packet — closing finding D's "a citation's existence is not proof the
statement is true" concern at the *scope* level; step 7's own
verification (below) closes it at the *depth* level.

**Technical claim verification workflow (step 7, amendment finding D,
in full)**:

1. **Identify factual assertions.** The writing contract's own
   `{{cite:...}}` tags (above) *are* the identified set — any sentence
   lacking a tag is treated as non-factual (heading, transition,
   instruction) by construction, and the editorial step (step 8, not
   step 7) is where a tagless sentence that reads as a factual claim
   anyway is caught and reported as a writing-contract violation, fed
   back as a rejection (never silently published, never auto-retried
   with a "fixed" re-prompt — §C "Constrained execution harness" point
   below applies the same no-silent-retry discipline to broken
   examples).
2. **Map each assertion to permitted evidence.** Deterministic: the
   tagged record id(s) must be a subset of `schema_section`'s own
   resolved `required_knowledge` set (step 1) — a tag citing anything
   else is an unsupported claim by definition, regardless of whether
   the cited id exists *somewhere* in the project (L-075's depth
   distinction, applied here: scope is "a record exists," depth is
   "this section was actually permitted to use it").
3. **Verify the evidence actually supports the claim.** Two
   sub-checks, kept structurally separate:
   - **Deterministic**: the cited record's own currency/status (step 2)
     clears the section's `min_claim_status` bar; for an Oracle-backed
     citation, the real, current `evaluate_result_precedence`/
     `aggregate_contract` outcome for the matching `scope` string is
     PASS (never INVALID/FAIL/GAP) at verification time, not merely at
     some historical recording time.
   - **AI-assisted semantic check**: does the cited record's own
     `fields` content, read directly, actually support the *specific
     wording and qualifiers* of the generated sentence (e.g. a record
     saying "supported on Linux" does not license a generated sentence
     claiming "supported on Linux and macOS"). This is dispatched as
     an **independent adjudication**, never the generating model
     self-certifying its own output — reusing the same ad-hoc-dispatch
     pattern as step 8, but a structurally distinct call scoring a
     different question (truth, not usefulness) against different
     input (the cited record's raw content, not the schema's
     audience/tone fields).
4. **Classify each tagged assertion**: `supported` (clears 2 and 3),
   `contradicted` (the cited record is itself flagged by `find_gaps`'s
   `contradiction` rule, or the matching Oracle outcome is FAIL),
   `unsupported` (fails 2, or the semantic check in 3 finds no genuine
   support), or `uncertain` (`unconfirmed_scopes`, or the Oracle
   aggregate state is GAP for that scope).
5. **Deterministic vs. semantic, explicitly separated**: steps 2-3's
   first sub-check (record resolution, currency, Oracle outcome lookup)
   is pure code, zero model involvement, fully reproducible; step 3's
   second sub-check is the only place an AI judgment enters, and it is
   never conflated with or allowed to override a deterministic
   `contradicted` finding.
6. **Retain an inspectable report.** `validate_section` returns (and
   the CLI command persists) a structured, per-sentence verification
   report — tag, cited id(s), classification, and (for the semantic
   check) the independent adjudicator's own stated reasoning — under
   `planning/retros/phase-87-documentation-quality-baseline/
   <schema-slug>/<section-id>-verification.json`. This report is
   evidence to inspect, never treated as its own final verdict (§4 of
   the governing task — a PASS from this log is not, by itself,
   grounds to score the arm as factually correct in the comparative
   trial, §F).
7. **Block publication.** Any `unsupported` or `contradicted`
   classification blocks that section's publication; it is reported
   (per-sentence, with its classification) in the compiler's own run
   report, never silently patched, never silently dropped from the
   assembled document without a visible "pending" marker (§C data-flow,
   unchanged from the first pass).

**Constrained execution harness (step 7's executable-example check,
amendment finding C, entirely new work)**: direct re-inspection
confirmed **no existing infrastructure in this repository runs an
untrusted, model-generated shell command safely** — every real
`subprocess` call site (`source_resolution.py`, `git_topology.py`,
`oracle.py::run_pytest_check`, the various `adapters/*.py`) runs
trusted, developer-authored commands with no isolation, and
`verify_cleanroom_isolation.py`'s `unshare`/`pivot_root` sequence is
wired to one fixed, synthetic probe script, not a general-purpose
"run this command safely" utility. A new module,
`scripts/run_example_command.py`, is required:

- **Disposable, isolated environment**: reuses the same
  `unshare --user --map-root-user --mount --pid --fork` + `pivot_root`
  *technique* `verify_cleanroom_isolation.py` already uses
  (`main_outer:386-443`) to construct a fresh mount namespace per
  invocation, discarded after; no new generic sandboxing library
  dependency introduced.
- **No developer credentials, private files, or unrelated
  repositories**: the sandbox's filesystem view is a read-only bind
  mount of exactly the pinned repository revision's working tree (the
  same `documented_revision` concept §A.2/A.4 already use), nothing
  else bind-mounted in — mirrors the broker sandbox's own
  "parent-host-paths unavailable"/"sibling-repositories unavailable"
  probes, applied to command execution instead of model inference.
- **Denied network by default**: `unshare --net` with no interface
  brought up (not even loopback where a shown command doesn't need
  it) — the same real guarantee the broker sandbox already provides
  for inference (confirmed: no bind-mounted network path exists for it
  either), extended to command execution, which has no precedent to
  extend from and must build this check itself.
- **Explicit command allowlisting**: the schema section declares,
  per example, the exact command it shows (not a pattern) — the harness
  parses it into an argv list itself (never `shell=True`, never passed
  through a shell for interpretation) and refuses to execute anything
  whose `argv[0]` is not in a small, explicit allowlist checked into
  the repo (`codecompass`, `python3 -m pytest`, `python3 --version`,
  and similarly narrow, explicitly-approved entries — extended only by
  an explicit, reviewed change to the allowlist file itself, never by
  the compiler at runtime).
- **Controlled filesystem writes, resource limits, timeouts**: a
  scratch directory, discarded after the run; `resource.setrlimit` for
  CPU time, memory, and open file descriptors; a wall-clock timeout
  (default 10s, overridable per schema section with an explicit upper
  bound) enforced via `subprocess.run(..., timeout=...)` plus a process-
  group kill on expiry.
- **Accurate capture**: the real command (as parsed), a minimal, scrubbed
  environment, exit code, stdout, stderr, and wall time — all persisted
  alongside the claim-verification report (above).
- **Expected-vs-actual comparison**: per the schema section's
  `example_comparison_mode` (§B) — `exact` (byte-identical), 
  `normalized_whitespace` (collapse runs of whitespace before
  comparing), or `regex` (the schema's own declared pattern must
  match) — decided and recorded in the schema at authoring time, never
  invented post-hoc to make a failing example pass.
- **Failure reporting without automatic re-execution of a "fixed"
  command**: a mismatch or non-zero exit is reported and blocks
  publication (step 7 point 7, same discipline); the harness never
  substitutes a corrected command and retries — a human or a fresh,
  explicit compiler invocation decides what changes, never the harness
  itself.
- **Negative tests** (§G.5): an attempted network call from inside the
  sandbox is denied; an attempt to read outside the pinned revision's
  bind-mounted tree is denied; a command whose `argv[0]` is not
  allowlisted is rejected *before* any process is spawned; a command
  designed to exceed its resource limit is killed and reported, not
  silently truncated.

**Data flow, end to end**: `schema.yaml` (one document) → for each
`sections[]` entry, steps 1-5 produce one bounded knowledge packet →
step 6 composes that section's prose in isolation (one broker call per
section, never one call for the whole document — keeps each
composition's context bounded and auditable, and lets a later
incremental-maintenance run regenerate exactly one section without
touching the others, §D.2) → steps 7-8 validate the result
independently of each other → a section that fails step 4 (gap),
step 7 (ungrounded claim/broken example), or step 8 (unclear/
off-audience) is held back from publication and reported, never
silently patched with invented content or silently dropped from the
assembled document. The assembled document is the concatenation of
every section that passed all gates, in schema order, plus an explicit
"pending" marker (visible only in the compiler's own run report, never
published inline) for any section still blocked.

**Handling unsupported, conflicting, stale, and unverified
information** (per this phase's own governing requirement, not
optional): a knowledge gap (step 4) blocks that section's generation
entirely — never filled with plausible-sounding filler (`CLAUDE.md`
§1's L-070, the fail-closed validation precedent this project already
established at Phase 79). A genuine contradiction (`find_gaps`'s own
`contradiction` rule) is surfaced as a reported conflict, never
resolved by the compiler picking a side. Stale implementation/Oracle
evidence (`decisions/0082`'s `unconfirmed_scopes`, a result whose
`oracle_contract_content_hash` no longer matches the live contract,
`check_contracts.py`'s own `contract-result-integrity-mismatch` rule)
is treated exactly as `find_gaps`/Oracle already treat it — never
promoted to "currently verified" prose on the strength of a historical
pass alone. None of this is new epistemic machinery; it is Phase 82-85's
existing fail-closed discipline, applied to documentation generation
as one more consumer of `knowledge_api`, not a parallel judgment layer
with looser standards.

## D. Operating modes

### D.1 Clean reconstruction

The clean-room writer (step 6) never receives existing narrative
documentation as input — mechanically enforced by
`prepare_cleanroom_branch.py`'s `UnclassifiedNarrativeShapedFileError`
(§A.2), the same guarantee Phase 79/80 already rely on, applied here to
a section-scoped export rather than a whole-repo one. Existing
documentation may be used, by the **lead**, outside the clean-room
boundary, only as a *candidate-gap detector* — "the current README
claims X, does the knowledge base actually support X" — and every such
candidate gap must be independently re-established as fact (a real
`knowledge_api.get`/`find_gaps` call, a real re-executed example) before
it changes what the compiler generates. A legacy doc's own prose is
never itself evidence of current implementation state, matching
`decisions/0084` §3's identical rule for self-curation.

### D.2 Manual incremental maintenance

**Correction (amendment finding E)**: the first pass's plan claimed
`semantic_change: true` is a field "already on" an accepted Claim/
Requirement — direct re-inspection of `knowledge_intermediate.py`
shows this is false. `semantic_change` exists only as a field on a
`doc_region_edit`/`anchor_edit` **reconciliation-candidate** manifest
item (grep-confirmed: every occurrence is inside candidate-manifest
read/write/apply functions), set once by the reviewer *at accept
time* to decide whether accepting the candidate creates a new Claim or
merely advances a baseline — and it is consumed and discarded the
moment the candidate is applied. No accepted Claim or Requirement
carries this field afterward. §D.2 below is rewritten to use the real
mechanism this project already has for exactly this problem, rather
than a field that does not persist long enough to be read back later.

**The real, reusable mechanism — corrected to its actual five states**
(a post-amendment independent review caught the first draft of this
section understating it as four states and silently dropping the one
most relevant to "preserve human editorial improvements," the governing
concern this finding exists to resolve). Direct re-read of
`knowledge_intermediate.py:324-420`: `GroundedRegionFinding.case` is
typed as exactly `"new" | "noop" | "doc_candidate" | "claims_changed" |
"concurrent_conflict"`. `detect_grounded_region_changes` (`:338`)
computes `structural_changed` (the region's own text hash OR its
cited-id *set* changed since baseline — membership is order-insensitive
but add/remove is a real change, `decisions/0075` point 2) and
`claims_changed` (a still-cited record's own content hash changed)
independently, then classifies:

| `structural_changed` | `claims_changed` | `case` | Meaning |
|---|---|---|---|
| no | no | `noop` | Nothing changed since baseline. |
| yes | no | **`doc_candidate`** | **The section's own text or citation set was edited; the knowledge it cites did not change.** This is the human-editorial-improvement case. |
| no | yes | `claims_changed` | Cited knowledge changed; the section's own text is untouched since baseline. Safe to regenerate — no human edit at risk. |
| yes | yes | `concurrent_conflict` | Both changed since baseline — a genuine three-way conflict. |

(a region never yet baselined is `new`, checked first, before any of
the above.) Three existing, already-implemented resolution functions —
not new work — close each non-trivial case: `establish_new_region_
baselines` (bootstraps a `new` region's first baseline — the only
automatic baseline write, since there is no prior state to lose);
`acknowledge_stale_grounded_region` (explicit human confirmation that a
`claims_changed` region's existing prose still reads accurately,
without regenerating it); `write_doc_candidates_to_manifests` (routes
every `doc_candidate` finding into the *existing* reconciliation-
candidate manifest pipeline, attached to the owning slug of its first
cited id — this is where `semantic_change` is actually decided, at
accept time, exactly as `decisions/0074` specifies; the first pass's
original finding-E text had the right *field*, just the wrong claim
about when it is readable). `concurrent_conflict` has no automatic
resolution function at all — `detect_grounded_region_changes` simply
keeps reporting it on every run until the underlying facts change.

1. **Stable section identity**: every compiled section is published
   with its own `codecompass-grounded-by ... region:<schema-slug>.
   <section-id>` marker (§C step 9, now unconditional) — the same
   `region:<id>` identity convention already proven to survive
   reorder/insertion (§A.3), reused directly, not a new identity
   scheme.
2. **Recorded generation baseline**: at publication,
   `establish_new_region_baselines` is called on the freshly-generated
   (`new`-state) section, exactly as any other grounded region's first
   baseline is established — no Phase-87-specific baseline mechanism.
3. **`codecompass docs maintain <schema-path> --changed <record-id>`**
   runs `knowledge_api.traverse` to find every section whose
   `required_knowledge` references the changed record or its 1-hop
   neighbours (a reporting/scoping filter — `detect_grounded_region_
   changes` itself scans every grounded region in the schema's target
   document regardless), then calls `detect_grounded_region_changes`
   and branches on the real five-state table above:
   - **`noop`**, or a section not referencing the changed record at
     all → **no action**, byte-for-byte untouched (§G.5 test 9).
   - **`new`** → runs the normal generation path (§C steps 1-9), then
     `establish_new_region_baselines`.
   - **`claims_changed`** → regenerates safely by default (steps 4-9
     re-run; no human edit is at risk, since the section's own text
     has not diverged from its baseline) — or, if the lead explicitly
     chooses not to regenerate this run, `acknowledge_stale_grounded_
     region` records that the existing prose was reviewed and kept.
     Either way requires an explicit action; `maintain` never silently
     leaves a `claims_changed` section un-reported.
   - **`doc_candidate`** → **never regenerated, never overwritten.**
     `write_doc_candidates_to_manifests` writes a manifest item into
     the existing reconciliation-candidate pipeline for human review
     (the same path, and the same `semantic_change` decision point,
     `decisions/0074` already defines for every other kind of
     candidate); the section's published text is untouched by
     `maintain` itself — any eventual change happens only through the
     existing, separate `apply` path, on the lead's own decision, never
     as a side effect of running `maintain`.
   - **`concurrent_conflict`** → **blocks automatic action entirely**;
     reports the conflict (current published text, the baseline it
     diverged from, and what regeneration would produce) for
     **lead-controlled resolution**. Note `write_doc_candidates_to_
     manifests` structurally excludes `concurrent_conflict` findings
     (it only accepts `doc_candidate`) — there is no existing function
     that resolves this state directly; the lead resolves it by
     deciding, outside any automatic path, which side wins (e.g.
     regenerating, which re-establishes a clean baseline, or hand-
     editing the record/text until the state reverts to
     `doc_candidate` or `claims_changed`, each of which *does* have an
     existing resolution path). It is kept being reported on every
     future `maintain` run until the lead's own action changes the
     underlying facts; the compiler never auto-resolves this state,
     matching the governing
     task's explicit "no automatic conflict resolution" requirement.
4. **Unrelated sections** (not referencing the changed record or its
   1-hop neighbours, and genuinely `noop`) are never regenerated by
   `maintain` — untouched by construction, not merely by a passing diff
   check.

`spec_docs.py::scan_spec_docs` (§A.8) locates which real file currently
holds a section lacking its own schema entry yet (a pre-Phase-87 doc
never regenerated), so the maintenance run can report "this file has
no governing schema" rather than silently skipping it.

**Explicitly excluded**: automatic, change-*triggered* maintenance (no
hook, watcher, or CI step invokes this mode automatically) — that is
Phase 89's own, later, distinct capability. Phase 87 builds the
maintenance mode as a manually-invoked `codecompass docs maintain
<schema-path> --changed <record-id>` command only.

## E. Minimum publication suite

| Document | Required outcome | Existing file | Current state (§A.9) | Phase 87 action |
|---|---|---|---|---|
| `README.md` | Problem, value, capabilities, installation, first steps | yes (101 lines) | Real, but not schema-governed or compiler-verified; the **bounded first demonstrator** (below) | Regenerate via compiler, clean reconstruction mode |
| `docs/getting-started.md` | Practical, independently tested tutorial | yes (114 lines) | Real; tested-example status not independently re-verified by any mechanism yet | New schema (`requires_tested_example: true`); regenerate or validate-in-place |
| `docs/concepts/*.md` | Core concepts, epistemic distinctions, reconciliation loop | yes (7 files, incl. `knowledge-model.md`) | Substantially covers the content (§A.9); editorial register is dense/internal, not reader-facing | Editorial-quality pass (step 8) against a new schema targeting an unfamiliar-developer audience; content largely reused, not re-derived from scratch |
| `docs/architecture/*.md` | Components, responsibilities, flows | yes (3 files) | Real | Schema + validation pass; extension only where `find_gaps` surfaces a genuine staleness |
| `docs/reference/cli.md`, `configuration.md` | Accurate, deterministic where practical | yes (252 + 38 lines) | Hand-maintained today | New: a deterministic-generation path reading the real Typer command tree (`cli.py`'s `app`/sub-apps) directly, replacing hand-maintenance for this one file only — the plan's own improvement opportunity named in `decisions/0085` §5 |
| `CONTRIBUTING.md` / `docs/development/contributing.md` | Contributor workflow, testing, verification | yes (266 + 35 lines) | Real | Schema + validation pass |

The bounded first demonstrator (§G.4) is `README.md` plus
`docs/getting-started.md` only, in clean reconstruction mode — the
complete table above is a **closeout requirement**, not a demonstrator
requirement, per `decisions/0085` §5's own explicit framing.

## F. Measurable documentation-quality improvement

A reproducible baseline, defined now (at planning time), not
retrofitted after generation:

- **Matched conditions**: the baseline run and the compiled-output run
  use the same pinned repository revision, the same document
  requirements (the same schema files), and the same evaluation
  criteria/rubric — never a baseline run against an older revision or a
  looser requirement set.
- **Baseline arm**: a conventional documentation pass — a developer (or
  a general-purpose agent with no access to `knowledge_api`/clean-room
  machinery, just the raw repository) writes or updates the same
  document set from scratch, under a time box, with no knowledge of
  this phase's own schema files beyond the plain-English requirement
  list they encode.
- **Phase 80's historical effort is not reused as this baseline**,
  per `decisions/0085` §6's own correction: Phase 80's retro was never
  designed with pinned-revision/fixed-rubric comparison discipline.
  Checked directly this planning pass: `planning/retros/
  phase-80-codecompass-documentation-reconstruction.md`'s own recorded
  correction count has no pinned baseline revision or fixed evaluation
  rubric attached — confirming `decisions/0085` §6's own judgment that
  it cannot be reliably reconstructed against this phase's standard.
  Phase 87 runs the fresh, matched comparison above instead.
- **Independently scored, per document**:
  - factual accuracy / evidence grounding (did every claim trace to a
    real record, counted directly against the compiler's own step-7
    validation log for the compiled arm; manually checked for the
    baseline arm)
  - unsupported/fabricated statements (count, both arms)
  - required-information coverage (schema's own `acceptance_criteria`,
    scored independently of the arm that produced the document)
  - tested usability of instructions/examples (every example actually
    executed, both arms, pass/fail)
  - clarity/organisation/audience suitability (a fixed rubric, scored
    by a reviewer blind to which arm produced which document —
    feasible here since both arms produce ordinary Markdown with no
    distinguishing artifact)
  - human correction effort (minutes of human edit time to bring each
    arm's output to publishable state, both arms, same reviewer)
  - generation/maintenance cost (wall-clock + token cost for the
    compiled arm; wall-clock for the baseline arm)
  - preservation of human editorial improvements across one simulated
    incremental-maintenance round (§D.2's own test, run on the compiled
    arm only — the baseline arm has no such mode to test)
  - reconciliation accuracy after a real knowledge change (compiled arm
    only, same test)
- **No historical correction count is treated as a directly comparable
  experimental measurement** — if a number cannot be reproduced under
  the matched conditions above, it is reported as context, not as part
  of the scored comparison.
- **Independent/blind assessment**: the clarity/organisation rubric
  scoring is performed by a reviewer (an agent dispatch, e.g.
  `context-evaluator` or a fresh `general-purpose` dispatch briefed
  only with the rubric and the two documents, not told which arm
  produced which) without visibility into which pipeline produced which
  document, where practically achievable (both outputs are plain
  Markdown, so this is achievable for every rubric-scored item above).
- **At least one successful clean-environment onboarding exercise** —
  a fresh environment, no prior context, following only
  `docs/getting-started.md` (compiled arm) to a real working first
  query — required, not optional, per `decisions/0085` §6.

**Amendment, finding/point 4 of the governing task — predefined
thresholds and honest reporting, added rather than left implicit**:

- **The step-7 validation log is evidence to inspect, never an
  independent final verdict.** A compiled-arm document is scored
  `factually correct` on the comparative rubric only after the same
  independent factual-checking process applied to the baseline arm
  (direct, human/independent-dispatch verification against the real
  repository) is *also* applied to the compiled arm's published
  claims — the compiler's own PASS is a input to that check (it tells
  the checker where to look and what was claimed-and-verified
  internally), never a substitute for it. This closes the specific
  risk the governing task names: "do not score the compiled arm as
  factually correct merely because its own validator produced a PASS."
- **Predefined success criteria and improvement threshold**, fixed
  now rather than chosen after seeing results: the compiled arm is
  reported as showing a **material improvement** over the baseline
  arm only if, on the matched comparison, it (a) has a factual-
  accuracy/grounding score (independently checked, per above) at least
  as high as the baseline arm's, **and** (b) requires materially less
  human correction time (a ≥25% reduction, chosen as a round,
  pre-registered threshold large enough to be visible above ordinary
  measurement noise between two single-run arms) to reach a
  publishable state, **and** (c) shows zero unsupported/fabricated
  statements surviving to the published document (the baseline arm's
  own count on this dimension is whatever it genuinely is — no
  equivalent zero-tolerance bar is retroactively imposed on it for
  comparison purposes, since it is not the system under test). Any
  other outcome — including the compiled arm matching but not
  exceeding the baseline, or exceeding it on some dimensions while
  trailing on others — is reported as **neutral or mixed**, explicitly
  not as a material improvement, per the governing task's own
  instruction to report negative/neutral/mixed results honestly.
- **Functional acceptance is separate from comparative performance.**
  Phase 87's own exit gate (§G.7) is satisfied by the compiler working
  correctly — generating, validating, and maintaining documentation
  per its own tests (§G.5) — regardless of which way the comparison in
  this section lands. A compiler that passes every test in §G.5 but
  does not clear the material-improvement threshold above is still a
  complete, done deliverable; it is reported as "functional, not yet
  demonstrated to outperform conventional documentation," never
  silently reclassified as a failed phase, and never silently
  upgraded to "demonstrates a quality or productivity advantage" if
  the threshold was not actually met.

## G. Implementation boundaries and acceptance tests

### G.1 Deliverables

- `scripts/check_doc_schema.py` — schema validator (§B), including
  one-time `discover:` resolution (§A.5/§C step 1).
- `scripts/compile_doc_section.py` — the clean-room section-compilation
  adapter (§C step 6, amendment finding B): staging-file export,
  manifest/hash, isolation preflight invocation, broker invocation, and
  returned-content parsing/validation. Lives under `scripts/`, not
  `src/codecompass/`, matching this project's existing convention that
  security-sensitive clean-room infrastructure (`prepare_cleanroom_
  branch.py`, `verify_cleanroom_isolation.py`, `cleanroom_broker.py`)
  lives there, separate from the importable library.
- `scripts/run_example_command.py` — the constrained execution harness
  (§C step 7, amendment finding C): sandboxed, allowlisted, no-network
  command execution with resource limits, timeouts, and expected-vs-
  actual comparison. Also under `scripts/`, same reasoning.
- `src/codecompass/doc_compiler.py` — the compilation pipeline logic
  that is *not* itself security-sensitive sandboxing (§C): `resolve_
  section_ids`, `check_record_currency`, `map_section_to_knowledge`,
  `find_section_gaps`, `resolve_section_packet`, `validate_section`
  (step 7's deterministic + report-assembly half; the AI-assisted
  semantic check and step 8 are ad-hoc dispatches the CLI command
  orchestrates, not functions inside this module), `compile_document`,
  `maintain_document` (§D.2, built on `knowledge_intermediate.
  detect_grounded_region_changes`).
- A narrowly-scoped addition to `scripts/prepare_cleanroom_branch.py`:
  one new allow-list entry plus its own explicit classification check
  for `planning/documentation-handoff/section-packets/**` (§A.2) — the
  one justified, stated extension to this existing script; nothing else
  in it changes.
- A new `docs_app` Typer sub-app in `cli.py` (wired immediately after
  the existing `knowledge_app` block, `cli.py:~66`, same pattern):
  `codecompass docs schema init`, `codecompass docs compile
  <schema-path>`, `codecompass docs maintain <schema-path> --changed
  <record-id>`.
- A new written brief, `docs/workflows/section-editorial-review.md`
  (§C step 8, amendment finding F) — the ad-hoc dispatch prompt for
  the editorial-quality assessment, mirroring `docs/workflows/
  knowledge-placement-review.md`'s existing precedent and `decisions/
  0094` point 1's reasoning.
- Schema files for the bounded demonstrator (`README.schema.yaml`,
  `docs/getting-started.schema.yaml`) plus, at closeout, one schema per
  file in the §E table.
- A new `docs/concepts/epistemic-model-and-reconciliation.md`-style
  editorial pass **if** the step-8 assessment of the existing
  `knowledge-model.md` (§A.9) actually fails the unfamiliar-developer
  audience bar — not written unconditionally; the compiler's own
  validation decides whether a rewrite or a lighter edit is warranted.
- The matched-baseline comparison report (§F), retained under
  `planning/retros/phase-87-documentation-quality-baseline.md`, plus
  per-section verification reports under `planning/retros/
  phase-87-documentation-quality-baseline/<schema-slug>/
  <section-id>-verification.json` (§C step 7 point 6).

### G.2 Interfaces, agents, permissions, write boundaries

- `doc_compiler.py` reads `knowledge_api`/`oracle.py`/
  `knowledge_intermediate.py` only — no direct `planning/knowledge/`
  file access bypassing the API (mirrors Phase 85's own
  `check_self_knowledge_quality.py` precedent, §A.6); a direct test
  (§G.5) asserts this by import-graph inspection, not merely by
  convention.
- `scripts/compile_doc_section.py` and `scripts/run_example_command.py`
  are the only two components with elevated system access (namespace
  construction, subprocess execution); both run read-only against
  `planning/documentation-handoff/section-packets/**` and the pinned
  revision's exported tree respectively, and neither gains any new
  credential or network path — the broker's existing one, unchanged,
  for inference; none at all for command execution.
- Clean-room composition (step 6) runs through the existing
  `cleanroom_broker`/sandbox with exactly the one stated, justified
  extension named in §A.2/§G.1 (the new allow-list entry) — no other
  weakening of its isolation guarantees.
- No agent, including the ad-hoc dispatch below, gains write access to
  `CLAUDE.md`, `decisions/*`, or any file outside `docs/`/`README.md`/
  `CONTRIBUTING.md`/this phase's own `scripts/`/`src/codecompass/
  doc_compiler.py`/`planning/documentation-handoff/`/`planning/
  retros/phase-87-*` — unchanged from `CLAUDE.md` §8's existing fixed
  points.
- **Corrected (amendment finding F): no new standing roster agent.**
  Direct inspection of `.claude/agents/*.md` confirmed `context-
  evaluator`, `docs-maintainer`, and `docs-reconstructor`'s write
  boundaries are each either too broad (write access to docs directly)
  or scoped to a different judgment (drift against *existing*
  current-truth docs, not clarity/audience/tone scoring of one freshly
  generated section against its own schema) — none is a drop-in match,
  but this does not by itself justify a 14th roster entry. Step 8 (and
  step 7's AI-assisted semantic check) are each performed by an ad-hoc
  `general-purpose` dispatch, briefed inline from a written document
  (`docs/workflows/section-editorial-review.md` for step 8; the claim-
  verification brief, §C step 7, for the semantic check) — exactly
  `decisions/0094` point 1's precedent for Phase 86's own semantic/
  editorial reviewer, which found independence and a stable charter
  both already satisfiable without a standing agent, with promotion
  left as a named, evidence-gated future escalation if real reuse ever
  makes brief-drift a material risk. Both dispatches are read-only
  toward their inputs and write only a report, mirroring
  `docs-reconstructor`'s existing read-only/report-only shape (the
  template copied, per the research finding, rather than inventing a
  new write-boundary pattern).

### G.3 Migration concerns

Existing hand-maintained files (§E table) are not deleted or replaced
wholesale on day one. Each gains a schema file and is regenerated or
validated-in-place one at a time; a file with no schema yet is left
exactly as it is (status quo is the safe default, never implicitly
"compiler-owned" until a schema actually exists for it).

### G.4 Dependencies

Phase 84 (knowledge API), Phase 86 (placement policy — informs what
belongs in generated documentation vs. elsewhere, already-done). No
dependency on Phase 88 (MCP) or Phase 89 (automatic reconciliation).

### G.5 Tests (plan-file verification section, `CLAUDE.md` §1)

1. **Missing evidence**: a schema section whose `required_knowledge`
   resolves to nothing via `knowledge_api.get`/`search` → generation
   refuses that section, reports a gap, does not fabricate content
   (direct test of §C step 4's fail-closed behaviour, and of `CLAUDE.md`
   §1's own L-070 minimal-content edge case — an empty/near-empty
   knowledge base for a section, not only the "some knowledge exists
   but is wrong" case).
2. **Contradictory knowledge**: a fixture with two `Claim`s in a real
   `contradiction` relationship (reusing `find_gaps`'s existing rule) →
   the section reports the conflict, does not silently pick a side.
3. **Stale implementation/Oracle evidence**: a fixture oracle result
   whose `oracle_contract_content_hash` no longer matches a live
   contract → treated as `check_contracts.py`'s own
   `contract-result-integrity-mismatch`, never promoted to "verified"
   prose.
4. **Clean-room isolation breach (negative control)**: attempt to feed
   an existing narrative doc into the section-scoped export →
   `UnclassifiedNarrativeShapedFileError` (reusing §A.2's own existing
   mechanism; this test confirms the *section-scoped* export path
   still triggers it, not merely the whole-repo path Phase 81B's own
   tests already cover).
5. **Unsupported technical claim**: a generated section asserting
   something not present in its own resolved knowledge packet → step 7
   rejects it (depth test, not just scope — confirms the validator
   checks the claim is actually grounded in *this section's own*
   packet, not merely that *some* record exists in the project
   matching similar words, per this project's own established L-075
   depth-vs-scope distinction).
6. **Broken executable example**: a `requires_tested_example: true`
   section whose shown command fails or whose output doesn't match
   real execution → rejected, reported with the real command/output
   diff (via `run_example_command.py`'s own comparison, §C step 7).
7. **Schema-validation failure**: a schema file missing a required
   field, with an unresolvable `required_knowledge` entry (a concrete
   id that doesn't exist, or a `discover:` query resolving to zero or
   more than one record — both cases, amendment finding A), or
   duplicating another schema's `document` path → `check_doc_schema.py`
   reports it as blocking; compiler refuses to run against it.
8. **Manual editorial improvement survives incremental maintenance**:
   publish a section, hand-edit its wording (no knowledge change),
   trigger `maintain` for an unrelated knowledge change → the hand-edit
   is preserved byte-for-byte (§D.2's own false-positive control).
   **Corrected expected state** (a post-amendment review caught the
   first draft asserting `clean`/`noop` here, which contradicts the
   real `detect_grounded_region_changes`'s own documented behaviour):
   the section's real state is `doc_candidate` (its own text hash
   changed; no cited record's content changed) — the test asserts
   exactly that state is reported, that `write_doc_candidates_to_
   manifests` records it as a pending reconciliation candidate, and
   that `maintain` itself never writes to the section's published
   text regardless of that state (preservation here is structural —
   `maintain` has no code path that regenerates a `doc_candidate`
   section — not merely an observed absence of change on this one
   run).
9. **Unrelated sections remain unchanged**: trigger `maintain` for one
   record's change → every section not referencing that record or its
   1-hop neighbours is byte-identical before/after (second half of the
   same test, asserted independently).
10. **Accurate, bounded provenance**: a section generated with
    `provenance: inline` carries a `codecompass-grounded-by` marker
    whose `region:<id>` resolves to the real record used; a section
    with `provenance: none` carries no `{{cite:...}}`-derived marker
    but still carries its own unconditional `region:<section-id>`
    marker for §D.2's reconciliation to address — both checked,
    neither assumed.
11. **Documentation-quality comparison using the agreed baseline**
    (§F): the matched-baseline run itself, scored per the rubric above
    including the predefined improvement threshold, is a required
    verification step, not an optional nice-to-have — the phase's exit
    gate (§G.7) depends on its having actually run, and on the result
    being reported honestly regardless of which way it lands.
12. **Unsupported claim surviving the deterministic check alone
    (amendment finding D, depth test)**: a generated sentence tagged
    `{{cite:X}}` where `X` is in the section's own resolved packet and
    clears the currency bar, but whose specific wording is not actually
    supported by `X`'s real content (e.g. overgeneralising a
    platform-scoped claim) → the independent semantic-check dispatch
    classifies it `unsupported` and blocks publication; the deterministic
    check alone (which would pass it, since `X` is a legitimate,
    current, in-scope citation) is confirmed insufficient on its own —
    this is the "a citation's existence is not proof the statement is
    true" scenario the governing task names, exercised directly.
13. **Clean-room section-export breach via the new payload path
    (amendment finding B, negative control)**: attempt to place an
    existing narrative-shaped file under `planning/documentation-
    handoff/section-packets/` → the new, narrowly-scoped classification
    check added to `prepare_cleanroom_branch.py` (§A.2/§G.1) rejects it;
    confirms the new allow-list entry did not accidentally create an
    unclassified, unprotected path into the sandbox.
14. **Unsafe generated command rejected before execution (amendment
    finding C)**: a schema-declared example command whose `argv[0]` is
    not in `run_example_command.py`'s allowlist → rejected before any
    process is spawned, not merely sandboxed-and-then-killed.
15. **Sandbox boundary violation attempts, negative controls (amendment
    finding C)**: a command attempting a network connection is denied
    (no interface available); a command attempting to read a path
    outside the bind-mounted pinned revision is denied (path does not
    exist inside the sandbox); a command designed to exceed its
    CPU/memory/time limit is killed and reported as a resource-limit
    failure, not silently truncated or hung.
16. **Isolation or broker failure blocks publication, not silent
    fallback**: `verify_cleanroom_isolation.py`'s preflight exiting
    non-zero, or `run_inference` returning `{ok: false, ...}`, aborts
    the whole `compile_document` run for that document — confirmed no
    code path falls back to an un-isolated or un-validated generation
    attempt.
17. **Concurrent human and knowledge edits produce a reported conflict,
    never an automatic merge (amendment finding E)**: hand-edit a
    published section's text *and* separately change a record it cites,
    then trigger `maintain` for that record → `detect_grounded_region_
    changes` reports `concurrent_conflict`; the section's published
    text is unchanged until the lead explicitly resolves it; no code
    path silently regenerates or silently keeps the stale text without
    reporting the conflict.
18. **Clean-environment onboarding exercise** (§F): a fresh environment
    with no prior context, following only the compiled `docs/getting-
    started.md`, reaches a real working first query — required, not
    optional, per `decisions/0085` §6; failure here blocks the exit
    gate regardless of how the rest of the test matrix scores.

### G.6 Risks

- **An accurate-but-unhelpful "investigation report disguised as
  documentation."** Mitigated structurally: step 8 is a separate
  verdict from step 7, scored against the schema's own `audience`/
  `tone` fields, and the baseline comparison's clarity rubric is blind
  to which arm produced which document — a technically-correct but
  dense/audit-log-styled output fails step 8 and the rubric
  independently of its factual correctness.
- **Drift toward this project's own internal planning-prose register**
  (`CONTEXT.md`/`ROADMAP.md`'s own style). Mitigated by explicitly
  excluding internal planning/audit documents from the clean-room
  writer's own evidence packets (step 5 only ever resolves
  `knowledge_api` records, never `planning/CONTEXT.md`/`ROADMAP.md`/
  `retros/*` text directly) and by the editorial requirements (§C
  step 8) scoring against "no unsupported claims, minimal internal
  development history, consistent terminology."
- **Schema sprawl / excessive configuration complexity.** Mitigated by
  the sensible-defaults scaffold (`docs schema init`) and by keeping
  the schema format's field list exactly the set `decisions/0085` §5
  names — no speculative fields added "for future flexibility."
- **False "second knowledge store" drift over time** if `doc_compiler.py`
  is ever extended carelessly to cache resolved packets. Mitigated by
  the explicit §G.2 write-boundary rule and a direct test (not listed
  above, added during implementation) asserting `doc_compiler.py`
  imports nothing from `planning/knowledge/` except through
  `knowledge_api`.
- **The new execution harness (`run_example_command.py`) becomes a
  general-purpose "run arbitrary commands" utility over time**,
  reused carelessly outside the narrow, allowlisted, pinned-revision
  documentation-example use case it is built for. Mitigated by keeping
  the allowlist file static and reviewed (never writable by the
  compiler or any agent at runtime) and by scoping its only caller to
  `doc_compiler.py`'s `validate_section` — no other module imports it.
- **The clean-room adapter's one new `prepare_cleanroom_branch.py`
  allow-list entry is widened over time** into a general "export
  anything under `planning/documentation-handoff/`" path, eroding the
  existing guarantee that raw `planning/knowledge/` never crosses the
  sandbox boundary. Mitigated by scoping the new entry to exactly
  `section-packets/**` (JSON manifest-bound files only, never a
  directory a future phase could repurpose for raw record export
  without its own explicit classification review).

### G.7 Exit gate

Per `decisions/0085` §6: the demonstrator (§E's bounded first pair) and
the complete minimum suite (§E's full table) both meet an independent
assessment that: an unfamiliar developer can understand what
CodeCompass does and why; install/quick-start instructions demonstrably
work (the clean-environment onboarding exercise, §F); current
functionality is distinguished from future plans; technical claims
trace to legitimate evidence (step 7's own validation log, spot-checked
independently); unsupported claims/contradictions are identified, not
hidden; no generated document resembles an audit report (step 8 +
blind rubric). The matched-baseline comparison (§F), including its
predefined improvement threshold, has actually run and its results are
recorded honestly — whether the result is material improvement,
neutral, or mixed — not merely planned. All eighteen tests in §G.5
pass, including the amendment's new executable-command-safety,
semantic-claim-depth, clean-room-export, and three-way-reconciliation
negative controls (tests 12-17). A documentation-drift audit
(`docs-reconstructor`, scoped to this phase's own diff) and an
independent `release-phase-auditor` pass both confirm every condition
above against the real, final commit — not the implementing agent's
own report, and not the compiler's own internal validation logs taken
at face value (§F).

**Explicitly out of scope / phase boundaries preserved**: Phase 88
(MCP integration) is not touched or assumed by anything here. Phase 89
(automatic, change-*triggered* reconciliation) owns upgrading §D.2's
manually-invoked `maintain` command into an automatic trigger — Phase
87 deliberately builds `maintain` as a standalone command precisely so
Phase 89 can wire a trigger to it later without redesigning this
phase's own compiler. Phase 90 (comparative development trials) owns
the broader, cross-arm comparative methodology; §F's baseline here is
scoped narrowly to documentation quality alone, not a restatement of
Phase 90's own evaluation design.

## H. Independent planning review

Per `CLAUDE.md` §1 and this phase's own governing instruction, an
independent planning-reviewer dispatch assesses this document against:
fidelity to `decisions/0084`/`0085`; verified (not assumed) reuse of
existing architecture (§A); confirmation of no second knowledge
authority; clean-room isolation and evidence-currency controls;
separation of technical correctness (step 7) from editorial quality
(step 8); realistic schema/compiler/maintenance interfaces; the
complete minimum-suite exit gate; the matched-baseline methodology's
reproducibility; testable, non-circular acceptance criteria (§G.5);
feasible scope. Material findings are corrected and the review repeated
until an evidence-backed `READY` verdict is reached — recorded as a new
section below this line, once performed; this plan does not claim
`READY` on its own say-so.

## I. Independent planning-review verdict (2026-11-04)

**READY WITH NON-BLOCKING OBSERVATIONS.** An independent reviewer
(dispatched separately from this plan's own authoring) spot-checked
every load-bearing citation directly against the real repository
rather than trusting this document's own prose:

- Confirmed `decisions/0084` §2's Phase 87 row and `decisions/0085`
  §§5-6 are reproduced faithfully in §B/§C/§F, and that Phase 88/89/90
  numbering/scope in §G.4/§G.7 correctly follows the final roadmap
  (`decisions/0085` §3/§7/§8's split/renumbering), not the earlier,
  superseded `decisions/0084` §2 table.
- Independently re-read `knowledge_api.py`'s `get_context_packet`
  (line 1507) and `find_gaps` (line 1318), `prepare_cleanroom_branch.py`'s
  `UnclassifiedNarrativeShapedFileError` (declared line 54, raised line
  199), and `cleanroom_broker.py`'s `run_inference` (line 135) — all
  confirmed to behave exactly as §A.2/§A.5 describe.
- Independently re-counted every file-existence/line-count claim in
  §A.9/§E (exact matches) and read `knowledge-model.md` directly,
  confirming the "editorial accessibility" framing is defensible and
  not used to undersell a real gap — while flagging that the file's
  zero worked examples should be named as a content gap, not only a
  register issue (addressed above, §A.9).
- Confirmed no second knowledge store in the design, correct exclusion
  of Phase 88/89/90 scope, and that §G.5's tests 1/5/8/9 are genuinely
  non-circular (each checks an externally observable fact, never the
  compiler self-certifying its own success).
- Confirmed §F's baseline is reproducible as specified and its blind
  rubric review is feasible (both arms produce ordinary Markdown),
  while flagging one asymmetry worth naming explicitly in the eventual
  retro: factual-accuracy scoring is automated (the step-7 validation
  log) for the compiled arm but manual for the baseline arm — reasonable
  given the log is an independent-validation byproduct rather than
  self-grading, but worth stating plainly so it is never read as having
  put a thumb on the scale.
- Confirmed overall scope, while large, traces every component to a
  specific `decisions/0085` §5/§6 requirement — no unrequested
  infrastructure (no new scheduler, no speculative schema fields, no
  second query surface) found.

No blocking inaccuracy, circularity, or scope-creep finding. The one
substantive observation (the examples gap) was corrected in §A.9/§E
above in the same pass that received this verdict; the asymmetry note
above is carried forward as a reporting requirement for the eventual
baseline retro (§F), not a plan defect. No second review round is
required before implementation may be authorised by the lead.


## J. Amendment (2026-11-04): six implementation-contract gaps resolved

A second independent review, conducted after §I's READY verdict but
before implementation began, found that the first pass's planning-depth
treatment of several interfaces had not been checked against the real
implementation closely enough to be implementation-ready — each gap
below is a corrected assumption, not a reopening of the plan's
strategic architecture (§A.1/A.3/A.6-A.9, §E, §F's overall shape, none
of which this amendment revisits).

| Finding | Severity | Resolved in |
|---|---|---|
| A. Knowledge retrieval and compilation contract | HIGH | §A.5 (rewritten), §B (`required_knowledge`/`max_evidence_chars` fields), §C step 1/5 |
| B. Clean-room section-compilation adapter | HIGH | §A.2 (rewritten), §C step 6, §G.1/G.5 test 13 |
| C. Safe executable-documentation verification | HIGH | §C "Constrained execution harness" (new), §G.1/G.5 tests 14-16 |
| D. Operationalised technical-claim verification | HIGH | §A.4 (Oracle correction), §C step 7 (full workflow, new), §C "writing contract" (new), §G.5 test 12 |
| E. Three-way incremental-maintenance reconciliation | MEDIUM | §D.2 (rewritten around `detect_grounded_region_changes`), §G.5 tests 8/9/17 |
| F. Implementation/agent write boundaries | MEDIUM | §G.1 (new deliverables named), §G.2 (ad-hoc dispatch, not a new agent) |

Each finding's resolution is grounded in direct re-inspection of the
real current implementation (`knowledge_api.py`, `oracle.py`,
`knowledge_intermediate.py`, the five `scripts/*cleanroom*`/`*broker*`
files, `cli.py`, `.claude/agents/*.md`), not re-assumed from the first
pass's own prose — citations are inline at each correction above. §F's
measurable-improvement section additionally gained a predefined
material-improvement threshold and an explicit separation of functional
acceptance from comparative-performance conclusions, per the governing
task's own point 4 (not a numbered finding, but addressed in the same
pass).

No finding required reopening the minimum publication suite (§E), the
nine-step pipeline's own ordering (§C's table structure, only its cell
contents), or either operating mode's basic shape (§D.1 unchanged;
§D.2's mechanism is corrected, not its "manual, not automatic" scope).
Phase 88/89/90 boundaries (§G.7) are unchanged and re-confirmed, not
reopened, by this amendment.

## K. Post-amendment independent planning-review verdict (2026-11-04)

**First round: NOT READY.** An independent reviewer, re-deriving every
load-bearing citation directly rather than trusting this document's own
prose, confirmed every correction in §J except one genuine remaining
defect: §D.2's own first draft asserted `detect_grounded_region_changes`
has "exactly four states," omitting the real fifth state,
`doc_candidate` (`knowledge_intermediate.py:331`,
`GroundedRegionFinding.case: "new" | "noop" | "doc_candidate" |
"claims_changed" | "concurrent_conflict"`) — the state meaning
"the section's own text or citation set changed; the knowledge it
cites did not," i.e. exactly the human-editorial-improvement case
finding E exists to protect. §G.5 test 8 inherited the same error
(asserting the hand-edited section's state would be `clean`/`noop`,
contradicted by the real function's own docstring warning: "becomes
`doc_candidate`, never silently `noop`"). Everything else the reviewer
checked — `knowledge_api.get`/`search`/`get_context_packet` behaviour,
`prepare_cleanroom_branch.py`'s hardcoded allow-list and exclusions,
`oracle.py`'s PASS/FAIL/INVALID-vs-GAP split, `semantic_change`'s real
scope, the agent-roster comparison, Phase 88/89/90 boundary
preservation, and all other test-matrix entries — held up under direct
re-verification with no further defect found.

**Resolution, same pass**: §D.2 rewritten to name and handle all five
real states, using the three *already-implemented* resolution
functions this project has for exactly this problem
(`establish_new_region_baselines`, `acknowledge_stale_grounded_region`,
`write_doc_candidates_to_manifests` — the last of which is where
`semantic_change` is actually decided, confirming the original
finding-E field citation was never wrong, only its claim about *when*
it is readable was). §G.5 test 8 corrected to assert the real
`doc_candidate` state and the structural (not merely observed)
preservation guarantee that follows from `maintain` having no code
path that regenerates a `doc_candidate` section.

**Second round, independent re-check of the correction only** (narrow
scope — confirms the §D.2/§G.5-test-8 fix is faithful to the real
function and introduces no new defect, not a full re-review of the
whole document): **READY WITH NON-BLOCKING OBSERVATIONS.** The
reviewer independently re-read `knowledge_intermediate.py:324-422` and
confirmed the five-state table, the three resolution functions'
real trigger conditions and effects (`establish_new_region_baselines`
only for `new`; `acknowledge_stale_grounded_region` only for
`claims_changed`, never touching doc text; `write_doc_candidates_to_
manifests` only for `doc_candidate`, writing a `pending`/`undecided`
manifest item, no text mutation), and test 8's corrected expected
state and preservation claim — all accurate. No remaining "four
states" or stale `clean`-as-a-state-name reference found outside the
§J/§K narrative describing the error that was corrected. One non-
blocking observation: the `concurrent_conflict` bullet's resolution
description was imprecise (it is *not* resolved via `write_doc_
candidates_to_manifests`, which structurally excludes that case) —
corrected in the same pass, above, before this verdict was recorded.

**Both review rounds are now closed with no remaining blocking
finding.** This plan is implementation-ready.
