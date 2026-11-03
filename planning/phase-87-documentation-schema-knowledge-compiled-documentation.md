# Phase 87: Documentation Schema and Knowledge-Compiled Documentation — plan

**Status: planned, not started.** Awaiting independent planning review
before being marked `ready`; implementation not authorised by this
document alone (`CLAUDE.md` §1).

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

**Reused directly, unchanged**, exactly as `decisions/0085` §5 step 6
requires ("compose each section through the existing clean-room
broker"). Phase 87 adds nothing to this layer — it supplies this
layer's *inputs* (a schema-section-scoped evidence export, assembled by
a new, Phase-87-owned step) and consumes its *output* (generated prose
for one section), never touching the isolation/broker mechanism itself.

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
`evaluate_result_precedence`, `aggregate_contract` — deterministic
PASS/FAIL/GAP/INVALID precedence; `GAP` is always *computed*, never
self-reported) and `scripts/check_contracts.py`. Evidence-currency
logic (is this result still valid against live source, or stale/
INVALID) lives entirely in `evaluate_result_precedence`/
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
  (`_bound_context_items`). This is pipeline step 5 ("generate bounded,
  section-specific knowledge packets") almost exactly as specified —
  Phase 87 needs a thin **section → topic(s)** adapter mapping a schema
  section's required-knowledge declaration onto one or more
  `get_context_packet` calls, not a new bounding mechanism.
- `find_gaps(project_root, slug=None, *, repo_root=None) -> ApiResponse`
  — six existing rules (`unverified_required_scope`, `contradiction`,
  `stale_test_citation`, `missing_contract`, `dangling_evidence_reference`,
  `dangling_dependency_reference`). This is pipeline step 4 ("identify
  material knowledge gaps before writing") — reused directly, not
  reimplemented.

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
requirements demand for a reader-facing concept page. **The real gap
is editorial accessibility, not missing content** — Phase 87's own
editorial-quality assessment step (§C step 8) is what actually closes
this, not a from-scratch authoring task. This plan corrects
`decisions/0085` §5's framing accordingly rather than repeating it
uncritically.

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
    required_knowledge: ["topic:installation", "topic:dependencies"]  # mapped to get_context_packet topics, §C step 1
    depth: brief                            # brief | standard | detailed
    tone: instructional                     # instructional | reference | narrative
    requires_example: true
    requires_tested_example: true           # must be independently executed, §C step 7 — not just syntax-checked
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
required fields present and well-typed; `required_knowledge` topics
resolve to a real record or oracle check via `knowledge_api.get`/
`search` (blocking if not — a schema pointing at knowledge that does
not exist is itself a defect, not deferred to compile time);
`evidence_requirements.min_claim_status` is one of the valid
`learning-lifecycle.md`-style enum values; `document` path is unique
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
| 1 | Retrieve accepted knowledge through Phase 84's API only | `knowledge_api.get`/`search`/`traverse` | none — direct reuse |
| 2 | Resolve current source/verification evidence | `oracle.py` (`aggregate_contract`), `knowledge_intermediate.py` (`derive_epistemic_profile`) | none — direct reuse |
| 3 | Map knowledge to required schema sections | — | **new**: `doc_compiler.map_section_to_knowledge(schema_section) -> list[topic]`, a thin lookup reading the schema's own `required_knowledge` field |
| 4 | Identify missing/uncertain knowledge before generation | `knowledge_api.find_gaps`, Oracle currency (`unconfirmed_scopes`, `decisions/0082`) | **new**: a per-section gap-vs-requirement comparison (a section whose `evidence_requirements.min_claim_status` isn't met by anything `find_gaps`/`get` returns is a **generation-blocking gap**, reported, never silently generated around) |
| 5 | Build bounded, section-specific knowledge packets | `knowledge_api.get_context_packet` | **new**: the thin topic-list adapter from step 3 feeds one or more `get_context_packet` calls per section; multiple packets for one section are concatenated under the *same* `max_chars` budget, never each given their own separate budget (avoids a section silently ballooning past its declared depth by fanning out across many topics) |
| 6 | Compose each section through the existing clean-room broker | `cleanroom_prompt_assembler.assemble_evidence_blob`, `cleanroom_broker_client.call`, `cleanroom_broker.run_inference` | **new**: a section-scoped evidence export (reusing `prepare_cleanroom_branch.py`'s own allowlist/manifest mechanism, scoped to just this section's resolved knowledge packet rather than a whole-repo snapshot) feeding the assembler; the broker/isolation layer itself is untouched |
| 7 | Independently validate technical claims and executable examples | `oracle.py` (for any behavioural claim with a real contract), direct command execution (for `requires_tested_example` sections) | **new**: `doc_compiler.validate_section(generated_text, schema_section)` — checks every sentence presented as fact traces to a knowledge record/oracle result actually in this section's own packet (not merely "some record exists somewhere"), and independently re-executes every shown command/example, comparing real output against what the generated text claims |
| 8 | Assess usefulness, clarity, audience suitability — distinct from factual validation | — | **new**: a second, separate validation pass (never the same call/agent dispatch as step 7) scoring the generated section against the schema's own `audience`/`tone`/`depth`/`acceptance_criteria` fields; a section can pass step 7 (every claim true) and fail step 8 (true but unreadable, wrong register, or useless to the stated audience) — these are reported as two independent verdicts, never collapsed into one pass/fail |
| 9 | Preserve provenance on demand without cluttering ordinary prose | `codecompass-grounded-by` marker convention (`parse_grounding_markers`, §A.3) | none — direct reuse; emitted only when `schema.provenance` is `inline` or `on_demand` (and in the latter case, only behind a generation-time flag, never inline in the published file by default) |

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

Given one accepted knowledge change (a Claim/Requirement whose
`semantic_change: true` reconciliation already landed, `decisions/0074`,
§A.3), the compiler: (1) finds every schema section whose
`required_knowledge` references the changed record or its 1-hop
neighbours (reusing `knowledge_api.traverse`); (2) re-runs steps 4-8
for exactly those sections; (3) leaves every other section's published
text byte-for-byte untouched. `spec_docs.py::scan_spec_docs` (§A.8)
locates which real file currently holds a section lacking its own
schema entry yet (a pre-Phase-87 doc never regenerated), so the
maintenance run can report "this file has no governing schema" rather
than silently skipping it.

**Presentation vs. semantic changes**: a human editorial improvement
to a *previously generated* section (wording, example choice, added
caveat) that does not correspond to any `semantic_change: true`
knowledge update is preserved verbatim on the next maintenance run —
the compiler diffs the currently-published section against what it
would regenerate, and if the only knowledge inputs are unchanged since
last compilation, the human edit wins and is not overwritten. A
maintenance run triggered by a real knowledge change *does* regenerate
the section, but the human's surviving presentation-only edits to
*other*, unaffected sections are untouched by construction (§D.2 point
3). This reuses `decisions/0074`'s existing `semantic_change` field
rather than inventing a parallel diffing model.

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

## G. Implementation boundaries and acceptance tests

### G.1 Deliverables

- `scripts/check_doc_schema.py` — schema validator (§B).
- `src/codecompass/doc_compiler.py` — the compilation pipeline (§C):
  `map_section_to_knowledge`, `resolve_section_packet`,
  `validate_section` (step 7), `assess_section_quality` (step 8),
  `compile_document`, `maintain_document` (§D.2).
- A new `docs_app` Typer sub-app in `cli.py`: `codecompass docs
  schema init`, `codecompass docs compile <schema-path>`, `codecompass
  docs maintain <schema-path> --changed <record-id>`.
- Schema files for the bounded demonstrator (`README.schema.yaml`,
  `docs/getting-started.schema.yaml`) plus, at closeout, one schema per
  file in the §E table.
- A new `docs/concepts/epistemic-model-and-reconciliation.md`-style
  editorial pass **if** the step-8 assessment of the existing
  `knowledge-model.md` (§A.9) actually fails the unfamiliar-developer
  audience bar — not written unconditionally; the compiler's own
  validation decides whether a rewrite or a lighter edit is warranted.
- The matched-baseline comparison report (§F), retained under
  `planning/retros/phase-87-documentation-quality-baseline.md`.

### G.2 Interfaces, agents, permissions, write boundaries

- `doc_compiler.py` reads `knowledge_api`/`oracle.py`/
  `knowledge_intermediate.py` only — no direct `planning/knowledge/`
  file access bypassing the API (mirrors Phase 85's own
  `check_self_knowledge_quality.py` precedent, §A.6).
- Clean-room composition (step 6) runs through the existing
  `cleanroom_broker`/sandbox unchanged (§A.2) — no new credential or
  network path.
  No agent, including any new one this phase defines, gains write
  access to `CLAUDE.md`, `decisions/*`, or any file outside `docs/`/
  `README.md`/`CONTRIBUTING.md`/this phase's own `scripts/`/
  `src/codecompass/doc_compiler.py` — unchanged from `CLAUDE.md` §8's
  existing fixed points.
- A new, narrow `docs-editorial-reviewer`-style agent role performs
  step 8 only — read-only toward the generated section and the schema,
  never toward the knowledge base directly (it judges clarity/
  usefulness of text already produced, not whether the knowledge
  behind it is true — that is step 7's job, kept structurally separate
  per §C). If an existing agent role (`context-evaluator`) already
  covers this adequately on inspection during implementation, no new
  role is defined — decided at implementation time against real
  agent-roster evidence, not assumed here.

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
   diff.
7. **Schema-validation failure**: a schema file missing a required
   field, with an unresolvable `required_knowledge` topic, or
   duplicating another schema's `document` path → `check_doc_schema.py`
   reports it as blocking; compiler refuses to run against it.
8. **Manual editorial improvement survives incremental maintenance**:
   publish a section, hand-edit its wording (no knowledge change),
   trigger `maintain` for an unrelated knowledge change → the hand-edit
   is preserved byte-for-byte (§D.2's own false-positive control).
9. **Unrelated sections remain unchanged**: trigger `maintain` for one
   record's change → every section not referencing that record or its
   1-hop neighbours is byte-identical before/after (second half of the
   same test, asserted independently).
10. **Accurate, bounded provenance**: a section generated with
    `provenance: inline` carries a `codecompass-grounded-by` marker
    whose `region:<id>` resolves to the real record used; a section
    with `provenance: none` carries no marker at all — both checked,
    neither assumed.
11. **Documentation-quality comparison using the agreed baseline**
    (§F): the matched-baseline run itself, scored per the rubric above,
    is a required verification step, not an optional nice-to-have —
    the phase's exit gate (§G.6) depends on its having actually run.

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
blind rubric). The matched-baseline comparison (§F) has actually run
and its results are recorded, not merely planned. All eleven tests in
§G.5 pass. A documentation-drift audit (`docs-reconstructor`, scoped to
this phase's own diff) and an independent `release-phase-auditor` pass
both confirm every condition above against the real, final commit —
not the implementing agent's own report.

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

