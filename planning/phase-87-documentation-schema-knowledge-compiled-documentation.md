# Phase 87: Documentation Schema and Knowledge-Compiled Documentation — plan

**Status: restructured into three stages (87A/87B/87C), amended for
four integration defects, independently re-reviewed.** This is a
**scope-management correction**, not an architectural redesign — the
strategic objective (§0), the verified architecture map (§A), and the
shared schema/pipeline contract (§B/§C) are preserved. What changes:
the previous single ~1400-line implementation scope is split into
three separately planned, implemented, and independently assessed
stages (§D/§E/§F), each with its own deliverables, exclusions, tests,
and stage gate; and four real integration defects found during this
restructuring pass are corrected (§G). The full, pre-restructuring
planning-review history (§H-§K) is preserved unchanged below as the
historical record — nothing in it is deleted, only superseded in
scope assignment. §L records this pass's own independent review
verdict.

Governing scope: `planning/v2-roadmap.md` §"Phase 87"; `decisions/0084`
§2; `decisions/0085` §5 (minimum publication suite, user-defined
schema, 9-step compilation pipeline, editorial requirements) and §6
(documentation-quality baseline methodology). Prerequisites: Phase 84
(`done`) and Phase 86 (`done`).

**Authorisation for this pass**: amend and independently verify this
plan; implement **Stage 87A only** if its planning review passes.
Stages 87B/87C require their own subsequent authorisation. Phase 87
itself is marked `done` only once 87C's own exit gate — the complete
Phase 87 Definition of Done, unchanged from the original plan — is
met; a passing 87A or 87B does not constitute Phase 87 completion.

## 0. Objective and value

Professional project documentation — clear, concise, genuinely useful
to its stated audience, not merely technically accurate Markdown —
becomes an explicit, repeatable *output* of the canonical knowledge
system, via a user-defined, versioned schema, rather than a one-off
clean-room exercise repeated by hand each time a doc goes stale
(`decisions/0084` §2, `decisions/0085` §5).

**No second source of project truth.** The compiler reads Phase 84's
`knowledge_api` only. It does not cache, duplicate, or independently
assert canonical facts. Every generated claim must trace to a real
knowledge record or be flagged as a gap — never fabricated to fill a
schema section.

**Governing design principle for this restructuring pass**: prove the
smallest useful knowledge-compilation workflow before engineering the
complete documentation platform. Each additional layer of
infrastructure earns its place through demonstrated value at the end
of the stage that introduces it, not through comprehensiveness.

## A. Verified architecture map — what exists, what's reused, what's new

Each subsection was independently verified against the real current
implementation, not assumed from roadmap/decision prose.

### A.1 Phase 79/80 clean-room documentation reconstruction — real, agent-based

`planning/phase-80-codecompass-documentation-reconstruction.md` §2-6
defines a 5-stage pipeline (frozen snapshot → model-blind
reconstruction → independent comparison → fresh draft →
reconciliation). This is **agent orchestration**, not a reusable
script or library call. Phase 87 reuses its *discipline* — model-blind
composition, independent comparison before trusting a gap claim — not
a callable component.

### A.2 Phase 81B clean-room isolation and broker — real, mechanically enforced

Under `scripts/`, four real, independently-runnable components:

- `prepare_cleanroom_branch.py` — exports an explicit, manifest-bound,
  allow-listed set of files **at a pinned git revision**, via real
  git-object extraction. `_export_file_at_revision` runs `git cat-file
  -p <revision>:<rel>` — it reads from git's object database, **never
  from working-tree disk**. This is a structural fact a correction
  below (§G.B) depends on: this script cannot export a freshly
  written, uncommitted file no matter what is added to its allow-list,
  because its export mechanism has no path to uncommitted content at
  all. `UnclassifiedNarrativeShapedFileError` makes narrative-shaped
  content a hard export failure under three broad, pre-reviewed
  allow-paths (`src`, `tests`, `scripts`) unless explicitly
  allow-listed.
- `verify_cleanroom_isolation.py` — a real sandbox preflight (actual
  `unshare`/`pivot_root`, not simulated), confirmed to actually pass in
  this project's own environment (`unshare --user --map-root-user
  --mount --pid --fork` and the full real-sandbox preflight test both
  verified directly this session). Named probes: evidence readable,
  output writable, parent-host-paths/sibling-repositories/git-history/
  git-remotes unavailable.
- `cleanroom_broker.py` — runs on the trusted host, holds real model
  credentials, exposes exactly one operation:
  `run_inference(system_prompt: str, messages: list[dict]) -> dict`
  (`{ok, output, usage}`), via a sanitised-env, neutral-cwd, no-tool
  (`--restricted --tools ""`) subprocess call to the `claude` CLI. It
  performs **zero structural validation of its own output** — the
  caller must never trust a model's own compliance claim.
- `cleanroom_broker_client.py` — a minimal Unix-socket client calling
  the broker's one operation, used when the caller itself runs inside
  an isolated sandbox and must cross that boundary to reach the
  broker.
- `cleanroom_prompt_assembler.py` — runs *inside* a sandbox;
  `assemble_evidence_blob(evidence_root: Path) -> str` builds one
  prompt from an isolated, exported tree, then calls the broker
  client.

**Reused directly, unchanged, for Stage 87A's bounded case — see §G.B
for the corrected, section-scoped runtime-evidence handoff this phase
actually uses** (not `prepare_cleanroom_branch.py`'s git-revision
export, which cannot serve a freshly-generated, uncommitted evidence
packet).

### A.3 Phase 81 canonical/intermediate knowledge — real

`src/codecompass/knowledge_intermediate.py`: six record kinds
(Observation/Evidence/Claim/Derivation/Decision/Requirement). The
`codecompass-grounded-by` HTML-comment marker convention
(`parse_grounding_markers`) carries an optional `region:<id>` token —
**`_REGION_ID_RE = re.compile(r"\bregion:([A-Za-z0-9_-]+)\b")`
(`knowledge_intermediate.py`), which does *not* include `.`** — a
dotted id (`region:readme.install`) silently truncates at the first
dot (confirmed directly: `region:readme.install` parses as region id
`readme`, discarding `.install`). §G.A corrects this. `semantic_change:
bool` exists **only** on a `doc_region_edit`/`anchor_edit`
reconciliation-candidate manifest item — never on an accepted Claim or
Requirement (confirmed by direct grep: every occurrence is inside
candidate-manifest read/write/apply functions) — consumed and
discarded the moment the candidate is applied.

`detect_grounded_region_changes` (`:338`) classifies a region's real
state as exactly one of five: `new` (no baseline yet), `noop` (nothing
changed), `doc_candidate` (the region's own text or cited-id *set*
changed; the knowledge it cites did not — the human-editorial-
improvement case), `claims_changed` (cited knowledge changed; region
text untouched — safe to regenerate), `concurrent_conflict` (both
changed — a genuine three-way conflict, never auto-resolved). Three
already-implemented resolution functions close the non-trivial cases:
`establish_new_region_baselines` (bootstraps `new`, the only automatic
baseline write), `acknowledge_stale_grounded_region` (explicit human
confirmation for `claims_changed`, never touches doc text),
`write_doc_candidates_to_manifests` (routes `doc_candidate` into the
*existing* reconciliation-candidate pipeline — this is where
`semantic_change` is actually decided, at accept time). No function
resolves `concurrent_conflict` automatically; it is reported until the
underlying facts change. `_check_no_duplicate_region_ids` enforces
project-wide uniqueness **across exactly the `doc_names` tuple passed
to it** — a caller that only passes the one document being compiled
will not catch a duplicate against a different schema-governed
document; Phase 87's own `compile_document`/`maintain_document` must
pass every schema-governed document's name, not just the current one.

### A.4 Phase 82/83 contracts, Oracle, evidence currency — real

`src/codecompass/oracle.py`: `OracleResult.outcome` is constrained to
exactly `{"PASS", "FAIL", "INVALID"}` — `GAP` is never one result's own
outcome; it exists only as `CheckAggregate.state` (`PASS`/`GAP`/
`NOT_REQUIRED`), computed by `aggregate_contract` across every result
for one check — a separate, aggregate-level concept from a different
function than `evaluate_result_precedence` (one result). A contract's
check identifies *what* is verified through a free-text `scope: str`
field on `OracleCheck`, matched by exact string against a cited
result — there is no structured link from a specific generated
sentence to a specific check; that connection is `scope`-string
convention only, decided by whoever authors the citing record.

### A.5 Phase 84 read-only knowledge API — real, substantial

`src/codecompass/knowledge_api.py`: `get(project_root, record_id) ->
ApiResponse` resolves one record to its **complete, untruncated**
`details["fields"]` (`:382`) — the real full-hydration path.
`search()`/`get_context_packet()` return only `summary`
(`_summarize_record`: `" ".join(value.split())[:280]`, a 280-character
truncation) — never full content, and `get_context_packet`'s free-text
fallback uses **only `results[0]`** when `topic` is not an exact
record id. **No code anywhere interprets a `topic:`-prefixed string.**
`find_gaps(project_root, slug=None) -> ApiResponse` returns six
existing rules (`unverified_required_scope`, `contradiction`,
`stale_test_citation`, `missing_contract`, `dangling_evidence_
reference`, `dangling_dependency_reference`).

**Retrieval contract** (unchanged from the prior amendment,
foundational to every stage below):

1. `required_knowledge` resolves to concrete record ids, never a
   `topic:` string — nothing interprets one.
2. A `discover:<query>` entry is resolved to **exactly one** record id
   once, at schema-validation time (`check_doc_schema.py`); zero or
   multiple matches is a blocking schema defect, never a silent
   `results[0]` guess.
3. Full hydration via `get()`, never bare `summary`.
4. A record failing a currency/status/scope check is reported as a
   named gap, never silently dropped or silently included.
5. The evidence packet handed to the writer is budgeted against *real
   serialized* hydrated content, never `summary` length; a required
   record exceeding the budget is a blocking compile-time error, never
   a silent truncation.

No competing knowledge API or canonical store is introduced anywhere
in this plan — every point above calls only `knowledge_api`'s existing
public functions; `doc_compiler.py` adds a resolution/hydration/
budgeting *policy* on top, never a second storage or query layer.

### A.6-A.9 Phase 85/86, `spec_docs.py`, existing documentation suite — real

`scripts/check_self_knowledge_quality.py` is the established precedent
for building a Phase-87-owned script on `knowledge_api` directly.
`scripts/check_knowledge_placement.py` is the precedent for mechanical
placement enforcement generated prose should mirror.
`spec_docs.py::scan_spec_docs` is a mechanical detector of existing
doc files, reusable as an input signal for "which file does this
section live in," not compilation machinery. Direct inspection
confirms every file in the minimum-suite table (§F) already exists;
the "epistemic distinctions" gap `decisions/0085` §5 named is real but
is editorial-accessibility-plus-missing-worked-examples, not missing
conceptual content — `docs/concepts/knowledge-model.md` substantially
covers the concepts already, in a dense internal register with zero
worked examples.

## B. Documentation schema (shared across all three stages)

**Format**: YAML, `schema_version: <int>`, matching this project's own
existing schema-file convention (`oracle-contract.yaml`). One schema
file per generated document: `docs/<path>.schema.yaml` for
`docs/<path>.md`; `README.schema.yaml` at the repo root.

**Minimum field set Stage 87A actually uses** (deliberately small — a
project maintainer must be able to read and edit this directly; fields
Stage 87B/87C need are added when those stages are authorised, not
pre-built now):

```yaml
schema_version: 1
document: README.md
audience: "a developer new to CodeCompass, has not read any other doc"
sections:
  - id: install                           # [a-z0-9-]+ only -- §G.A
    required_knowledge: ["CL-0031"]       # concrete record ids, or a one-time
                                           # discover:<query> resolved to exactly
                                           # one id at schema-validation time
    max_evidence_chars: 4000              # budget against REAL hydrated content
    audience: "a developer new to the project"
    tone: instructional
    depth: brief
    min_claim_status: supported           # candidate | supported | verified
    citation_display: none                # inline | none -- §G.C: reader-visible
                                           # citation phrasing ONLY; machine-readable
                                           # grounding is always emitted regardless
acceptance_criteria:
  - "An unfamiliar developer understands what CodeCompass does and why."
owner: lead
```

**Deferred to Stage 87B/87C, named here so nothing silently
disappears, not built now**: `requires_tested_example`/
`example_comparison_mode` (87B, needs the execution harness);
per-document `verification_method` and full `acceptance_criteria`
richness (87C); Diátaxis-default scaffolding templates (87C, cosmetic
convenience); deterministic CLI/configuration-reference generation
schema variant (87C).

**Versioning**: `schema_version` bumps only on a breaking field
change. The compiler refuses to run against an unrecognised
`schema_version` (fail closed), never guessing at a forward-compatible
interpretation.

**Validation**: `scripts/check_doc_schema.py` (mirrors
`check_contracts.py`'s `Finding`/`--strict` convention) — required
fields present/well-typed; every concrete `required_knowledge` id
resolves via `get()`; every `discover:` entry resolves to exactly one
record (rewritten in place to the concrete id, idempotent); `min_claim_
status` is a valid enum value; `document` path unique across every
schema file in the run; **`id` and `document`-derived region ids
validated against `[a-z0-9-]+` (§G.A)** — a schema using a dot,
underscore-as-separator, or any character outside this set in a
section `id` is a blocking validation failure, never silently accepted
and truncated later by the parser.

**Ownership**: schema files are edited by the lead (or an ad-hoc
implementer subagent under the lead's direction) — not independently
owned by the compiler or any generation agent.

## C. Knowledge-compilation pipeline (shared contract, all stages)

The 9 steps `decisions/0085` §5 specifies, with the four corrections
(§G) folded directly into the step definitions rather than described
separately:

| # | Step | Built on | Stage |
|---|---|---|---|
| 1 | Retrieve accepted knowledge through Phase 84's API only | `knowledge_api.get`/`search` | 87A |
| 2 | Resolve current source/verification evidence | `oracle.py`, `derive_epistemic_profile` | 87A |
| 3 | Map knowledge to required schema sections | (identity function over step 1) | 87A |
| 4 | Identify missing/uncertain knowledge before generation | `knowledge_api.find_gaps` + step 2 | 87A |
| 5 | Build bounded, section-specific knowledge packets | `knowledge_api.get` (full hydration) | 87A |
| 6 | Compose each section through the existing clean-room broker | `cleanroom_broker.run_inference` + §G.B's corrected runtime handoff | 87A |
| 7 | Independently validate technical claims (citation scope + evidence depth + untagged-claim completeness, §G.D) and executable examples (87B's execution harness) | ad-hoc independent dispatch | 87A (claims) / 87B (examples) |
| 8 | Assess usefulness, clarity, audience suitability — distinct from factual validation | ad-hoc independent dispatch | 87A |
| 9 | Preserve machine-readable grounding always; reader-visible citation on demand (§G.C) | `codecompass-grounded-by` marker | 87A |

**The section-specific writing contract** (step 6): the system prompt
handed to `run_inference` requires the model to tag every sentence
presented as a factual claim with `{{cite:RECORD-ID}}`, naming only a
record id present in the section's own resolved packet, and to write
only the section's own prose (no file markers, no claims about a
different output path). The adapter never trusts the model's own
compliance claim with this contract — step 7 independently checks it.

**Technical claim verification (step 7) — three distinct questions,
kept structurally separate, per §G.D**:

1. **Does the claim cite permitted evidence?** Deterministic: every
   `{{cite:X}}` tag's `X` must be a member of this section's own
   resolved packet (not merely exist somewhere in the project —
   scope, not depth).
2. **Does the cited evidence genuinely support the claim?**
   AI-assisted, independently dispatched (never the generating model
   grading itself): does the cited record's real content actually
   support the sentence's specific wording and qualifiers.
3. **Are there factual claims without citations?** The same
   independent dispatch as question 2 is also asked this — "list any
   sentence that states a fact about the project with no `{{cite:...}}`
   tag" — a bounded addition to one existing review, not a new
   sentence-classification subsystem (§G.D rejects building one).

Any `unsupported`, `contradicted`, or untagged-factual finding blocks
that section's publication — reported, never silently patched, never
promoted to published fact on the strength of an unresolved question.

**Data flow**: for each `sections[]` entry, steps 1-5 produce one
bounded packet → step 6 composes that section's prose in isolation
(one broker call per section) → step 7 validates independently of
step 8 → a section failing step 4, 7, or 8 is held back and reported,
never silently patched or silently dropped without a visible pending
marker.

**Handling unsupported, conflicting, stale, and unverified
information**: a knowledge gap (step 4) blocks generation entirely —
never filled with plausible filler (`CLAUDE.md` §1 L-070). A genuine
contradiction is surfaced, never resolved by the compiler picking a
side. Stale evidence is treated exactly as `find_gaps`/Oracle already
treat it. None of this is new epistemic machinery — it is Phase 82-85's
existing fail-closed discipline, applied to documentation generation.

## D. Stage 87A — Prove knowledge compilation

**Objective**: demonstrate that CodeCompass can generate one genuinely
useful documentation section from canonical knowledge, with traceable
evidence and independent verification.

### D.1 Deliverables

1. The minimal schema format (§B).
2. `doc_compiler.resolve_section_ids`/`check_record_currency`/
   `find_section_gaps`/`resolve_section_packet` — deterministic
   resolution, full hydration, currency/scope checks, bounded packets
   (already implemented and tested, commit `b2fbc23` — reused as-is;
   this stage's new work is everything from step 6 onward).
3. `scripts/check_doc_schema.py` — schema validator (already
   implemented and tested, commit `b2fbc23`; corrected during this
   restructuring pass's own review, which found the originally-
   committed validator required the *pre-restructuring* field set
   — `purpose`/`verification_method`/`provenance` at top level,
   `title`/`requires_example`/`requires_tested_example`/a nested
   `evidence_requirements` dict per section — none of which matches
   §B's new minimal schema, confirmed by actually running the
   validator against §B's own example and getting blocking findings.
   Corrected: required-field lists now match §B's flat minimal shape
   (`min_claim_status`/`allow_unconfirmed_scopes` as flat per-section
   fields, never nested); the top-level `provenance` enum check is
   replaced by §G.C's per-section `citation_display` check; §G.A's
   `[a-z0-9-]+` section-id validation is added; `requires_tested_
   example`/`example_comparison_mode` validation is kept but no longer
   required (checked only if present, so the same script stays valid
   for 87B's schemas without needing to change again). `doc_compiler.
   find_section_gaps` (same commit) is corrected identically — it also
   read a nested `evidence_requirements` dict and is now flat to match.
4. `scripts/compile_doc_section.py` — section-level clean-room
   composition using the corrected runtime-evidence handoff (§G.B):
   writes the packet to an ephemeral, hash-verified staging directory,
   runs the isolation preflight, invokes `cleanroom_broker.
   run_inference` directly (its own existing sanitised subprocess
   call is the real isolation boundary for a bounded text prompt with
   no filesystem/tool access of its own — no new sandbox is
   constructed, since there is no broad export to protect; see §G.B's
   explicit justification), and independently parses/validates the
   returned text (never trusting the model's own compliance claim).
5. The three-question claim-verification workflow (§C step 7, §G.D) —
   a deterministic scope check in `doc_compiler.py`, plus one ad-hoc
   independent dispatch answering questions 2 and 3 together and
   producing an inspectable report.
6. A separate, lightweight ad-hoc editorial-quality dispatch (step 8) —
   reusing `decisions/0094`'s "ad-hoc dispatch, not a new standing
   agent" precedent; no new `.claude/agents/*.md` role.
7. `doc_compiler.publish_section`/`maintain_document` using the
   corrected five-state grounded-region mechanism and the corrected
   `region:<id>` format (§G.A) — enough machinery to publish one
   section with a stable, reconciliation-ready identity, not the full
   87B maintenance workflow.
8. A complete, real, end-to-end demonstration: one selected `README.md`
   section, compiled from real canonical knowledge, independently
   verified, and actually published.

### D.2 Explicitly excluded from 87A

Full-document generation (only one bounded section); manual
incremental maintenance beyond establishing one baseline (87B); a
general-purpose generated-command execution sandbox (87B); schemas for
the entire documentation suite (87C); deterministic CLI reference
generation (87C); a full matched-baseline experiment (87C); new
standing agents or a second knowledge store (never).

### D.3 Tests

1. Missing required record → generation refuses, reports a gap, never
   fabricates (L-070's minimal-content edge case).
2. Ambiguous `discover:` knowledge selection (zero or multiple matches)
   → blocking schema-validation failure, never a guessed first match.
3. Stale or contradictory evidence → reported, never promoted to
   "verified" prose, never silently resolved by picking a side.
4. Packet truncation/integrity failure → a required record exceeding
   `max_evidence_chars` is a blocking error, never silent truncation;
   a runtime evidence packet whose content hash no longer matches its
   own manifest (altered between writing and use) is rejected before
   the broker is invoked.
5. Narrative-documentation contamination (negative control) → the
   ephemeral staging directory used for the broker call is asserted to
   contain *exactly* the packet and its manifest and nothing else
   before every invocation; a planted extra file is rejected.
6. Clean-room isolation failure → `verify_cleanroom_isolation.py`'s
   preflight exiting non-zero aborts the whole compile run; no
   fallback to an un-isolated attempt.
7. Incorrect grounding ids → a dotted or otherwise out-of-pattern
   section `id` is rejected at schema-validation time (§G.A); multiple
   sections each get distinct, stable ids; a section's identity
   survives reordering within its document; a duplicate id across two
   schema-governed documents is rejected
   (`DuplicateGroundingRegionIdError`, project-wide per §A.3's
   corrected `doc_names` scope).
8. Unsupported or untagged factual claims (§G.D) → a citation outside
   the section's own packet is rejected (scope); a citation to a
   legitimate record whose content doesn't actually support the
   sentence's specific wording is rejected (depth, independently
   dispatched); an untagged sentence that reads as a factual claim is
   caught by the same dispatch's third question, not silently waved
   through.
9. Unsupported citations despite valid record ids → a `{{cite:X}}`
   where `X` is real and current but outside *this section's own*
   resolved packet is rejected (L-075's depth-vs-scope distinction,
   applied at the scope level this time).
10. Unexpected model output or publication paths → a returned section
    declaring a different file/section via an embedded marker is
    rejected, never published, never silently reinterpreted.

### D.4 Stage gate — independent assessment, not an automatic pass-through

At the end of Stage 87A, independently assess (not a formal two-arm
comparative experiment — that is 87C's):

- Actual documentation quality of the one published section.
- Coverage and grounding accuracy.
- Unsupported-claim detection working as designed (tests 8-9 passing
  is necessary but not sufficient — spot-check the real demonstration
  run's own verification report).
- Technical complexity introduced (lines of new code, new
  dependencies, new failure modes).
- Runtime and model cost of one real compilation.
- Manual correction effort to make the published section genuinely
  publication-ready.
- Whether the architecture remains suitable for Stage 87B/87C, or
  whether real friction found here should change their design first.

**Mandatory stage gate**: one real README section compiled from
canonical knowledge, independently verified, useful to its audience,
and safely publishable. **Proceeding to Stage 87B requires an explicit
go/no-go decision based on demonstrated value, not merely "tests
pass."**

## E. Stage 87B — Prove usability and maintenance (not authorised by this pass)

**Objective**: extend the working compiler to two useful, complete
documents and demonstrate safe ongoing maintenance.

Deliverables (named here so the full requirement survives, not built
now): schema-governed `README.md` and `docs/getting-started.md`;
independently tested installation/first-use examples via a narrowly
scoped, safe execution harness reusing `verify_cleanroom_isolation.py`'s
`unshare`/`pivot_root` *technique* (a new module, since no existing
component runs an untrusted, model-generated command safely — no
network, allow-listed `argv[0]`, resource limits, no auto-retry on
failure); stable section identities and knowledge dependencies (built
directly on 87A's corrected `region:<id>` mechanism, not a parallel
scheme); manual section-level maintenance using the real five-state
`detect_grounded_region_changes` reconciliation (87A's `maintain_
document`, extended to real multi-section documents); preservation of
human editorial changes (`doc_candidate` state, never auto-
regenerated); explicit reporting of `concurrent_conflict`, never an
automatic merge; a successful clean-environment onboarding exercise.
No automatic change-triggered reconciliation — that remains Phase 89.

**Mandatory stage gate**: two useful documents, verified onboarding,
and a demonstrated manual maintenance cycle that preserves a real
human edit.

## F. Stage 87C — Publication suite and evaluation (not authorised by this pass)

**Objective**: bring the complete required publication suite into
compliance and demonstrate measurable documentation quality.

Deliverables (named here so the full requirement survives, not built
now): the complete minimum suite per `decisions/0085` §5 — README,
Getting Started, Concepts (including example-led epistemic-distinctions
and reconciliation-loop content, closing §A.9's real gap), Architecture,
Reference (deterministic CLI/configuration generation from the real
Typer command tree where practical), Contributor Guide; validation-in-
place for already-accurate documentation, regeneration only where
beneficial (status quo is the safe default per the original plan's
§G.3 migration discipline); a reproducible, matched-baseline
documentation-quality experiment (both arms same pinned revision, same
requirements, same rubric; a predefined material-improvement
threshold, not chosen after seeing results; the compiler's own
step-7 validation log is evidence to inspect, never an independent
final verdict for the compiled arm either); independent, where
practical blind, evaluation of factual accuracy, editorial quality,
tested usability, human correction effort, and generation/maintenance
cost; final `docs-reconstructor` drift audit and `release-phase-
auditor` pass against the complete implementation.

**This stage carries the original plan's full exit gate** — the
complete minimum suite, the matched-baseline comparison (run and
reported honestly regardless of outcome), and every applicable test
from the original 18-test matrix (preserved in full at §K's own
historical record below, reassigned across 87A/87B/87C by this
restructuring). **Phase 87 is marked `done` only when 87C's own exit
gate is met.**

## G. Four integration-defect corrections (this pass)

### G.A Grounded-region identifiers

**Defect**: the existing parser's `_REGION_ID_RE =
re.compile(r"\bregion:([A-Za-z0-9_-]+)\b")` does not include `.`. The
plan's own proposed `region:readme.install`-style dotted convention
silently truncates to `readme`, discarding `.install` — confirmed by
direct execution, not assumed.

**Correction**: section `id`s (and the composed region id,
`<schema-slug>-<section-id>`) are restricted to `[a-z0-9-]+` —
hyphen-separated, matching the existing parser exactly, no competing
identity scheme introduced. `check_doc_schema.py` rejects any section
`id` outside this pattern at validation time (§D.3 test 7).

**Tests required**: multiple sections in one document each receive
distinct, correctly-parsed ids; a region's identity survives physical
reordering within its document (the existing `region:<id>`-over-
positional-index guarantee, exercised, not merely assumed); a duplicate
id — including across two different schema-governed documents, per
§A.3's corrected `doc_names`-scope finding — is rejected via the
existing `DuplicateGroundingRegionIdError`, never silently accepted.

### G.B Runtime clean-room evidence packets

**Defect**: the original plan assumed adding an allow-list entry to
`prepare_cleanroom_branch.py` would make a newly generated, uncommitted
section-evidence packet exportable into the sandbox. Confirmed false
by direct inspection (§A.2): that script's export mechanism reads from
`git cat-file -p <revision>:<path>` — git's object database at a
pinned revision — never from working-tree disk. No allow-list change
can make it see a file that was never committed. The task is explicit:
do not commit transient evidence packets merely to export them.

**Correction**: a minimal, explicit, hash-verified handoff purpose-
built for runtime evidence, **not** a modification to
`prepare_cleanroom_branch.py` (which is dropped entirely from this
plan's scope — it solves a different problem and gains no new
allow-list entry):

1. `compile_doc_section.write_section_packet` writes the hydrated
   `EvidencePacket` and a manifest (schema section id, **pinned source
   revision** — the project's real `git rev-parse HEAD`, recorded
   honestly as dirty/clean — and a `sha256` content hash of the packet)
   to a fresh, ephemeral staging directory (`tempfile.mkdtemp`,
   mirroring `verify_cleanroom_isolation.py`'s own established scratch-
   directory convention) — never a git-tracked path, never committed.
2. Immediately before invoking the broker, the packet's current
   on-disk content hash is re-verified against the manifest's own
   recorded hash — a mismatch (the file altered between writing and
   use) is rejected, fail-closed, never used anyway (§D.3 test 4).
3. The staging directory's contents are asserted to be *exactly* the
   packet and its manifest — nothing else — immediately before each
   broker call, preserving the existing narrative-documentation-
   exclusion discipline without reusing `UnclassifiedNarrativeShapedFileError`
   (which is wired to git-tracked exports specifically); a planted
   extra file fails this assertion (§D.3 test 5).
4. `run_isolation_preflight` still runs the real, existing
   `verify_cleanroom_isolation.py` as a subprocess before every
   `compile_document` invocation and fails closed on non-zero exit —
   this remains a mechanism self-test, unchanged.
5. The broker is invoked directly via `cleanroom_broker.run_inference`
   — its own existing sanitised-env, neutral-cwd, no-tool subprocess
   call is the real isolation boundary for this bounded, self-contained
   text prompt (no credentials, no unrestricted host access, by the
   broker's own existing, already-audited design — nothing new added
   here). **No new clean-room broker is created.** This is a narrower
   isolation posture than Phase 79/80's whole-repository sandbox, and
   that narrowing is deliberate and stated, not an unexamined
   shortcut: Phase 79/80's sandbox protects a *broad git-tracked
   export* against accidental narrative-content inclusion; this
   module's evidence is never a broad export — it is a small JSON
   blob built field-by-field exclusively from `knowledge_api.get()`'s
   own resolved content for a section's explicitly resolved record
   ids, with no file sweep for a classification gate to protect
   against in the first place.

### G.C Provenance and knowledge dependencies

**Defect**: the original plan's `provenance: on_demand | inline | none`
schema field conflated two different concepts — whether a human
reader sees a citation, and whether the compiler's own reconciliation
machinery can find a section's knowledge dependencies at all. A
section published with `provenance: none` risked losing its
machine-readable grounding entirely, which would silently break
`detect_grounded_region_changes`'s ability to reconcile it later.

**Correction**: two separated concepts, never one field conflating
both:

- **Reader-visible citation preference** (schema field
  `citation_display: inline | none`) — controls only whether a
  human-visible citation phrase is woven into the *rendered* prose.
  Purely cosmetic.
- **Machine-readable grounding** — the `codecompass-grounded-by
  ... region:<id>` HTML-comment wrapper and its full cited-record-id
  list. **Always emitted for every compiler-owned, published section,
  unconditionally**, regardless of `citation_display` — because
  `detect_grounded_region_changes`/`maintain_document` structurally
  require it to exist for every section they must be able to
  reconcile. An HTML comment is already invisible in rendered
  Markdown/HTML by construction, so "always present, machine-readable"
  and "a reader's rendered view stays uncluttered" are not in tension —
  this was true of the existing marker convention already; the
  correction is removing the schema's own option to omit the marker
  entirely, which the old three-value field implied `none` could do.

**Reuses the existing `codecompass-grounded-by` convention directly —
no second dependency store.** Required test: a published section,
under both `citation_display` values, is correctly round-tripped by
the real `parse_grounding_markers` (cited ids, region id, body all
recovered exactly) — compatibility confirmed by direct test, not
assumed.

### G.D Untagged factual statements

**Defect**: the original writing contract assumed every factual
sentence would carry a `{{cite:...}}` tag and left detecting an
untagged factual claim to the separate editorial-quality step (step
8) — but step 8 judges clarity/usefulness, not factual grounding; an
untagged assertion could reach publication without either step
actually being responsible for catching it.

**Correction**: three distinct questions, kept structurally separate
(reproduced here and in §C for clarity, since this is the correction's
own core content):

1. Does the claim cite permitted evidence? (deterministic, scope)
2. Does the cited evidence genuinely support it? (AI-assisted, depth)
3. Are there factual claims without citations? (completeness)

Question 3 is answered by the **same** independent dispatch that
answers question 2 — one bounded addition to an existing ad-hoc review
("list any sentence stating a fact with no `{{cite:...}}` tag"), per
the task's own explicit preference for bounded independent review over
a new, elaborate sentence-classification subsystem. Any finding from
question 3 blocks publication exactly as an `unsupported` finding from
questions 1-2 does — uncertain or unsupported material is never
published as established fact, and an untagged claim is never silently
deferred to step 8's different, non-factual judgment.

## H. Independent planning review

*(Preserved unchanged from the pre-restructuring plan — see below.)*

Per `CLAUDE.md` §1, an independent planning-reviewer dispatch assesses
this document against: fidelity to `decisions/0084`/`0085`; verified
reuse of existing architecture; no second knowledge authority;
clean-room isolation and evidence-currency controls; separation of
technical correctness from editorial quality; realistic interfaces;
the complete minimum-suite exit gate; reproducible baseline
methodology; testable, non-circular acceptance criteria; feasible
scope. Material findings are corrected and the review repeated until
an evidence-backed `READY` verdict is reached.

## I. Independent planning-review verdict (2026-11-04, first pass)

**READY WITH NON-BLOCKING OBSERVATIONS.** (Full detail preserved as
historical record: fidelity to `decisions/0084`/`0085` confirmed;
`knowledge_api`/clean-room citations independently re-read and
confirmed accurate; no second knowledge store; one substantive
observation on the `knowledge-model.md` examples gap, corrected in
§A.9 in the same pass; one asymmetry noted for the eventual baseline
retro.)

## J. Amendment (2026-11-04): six implementation-contract gaps resolved

*(Historical record, preserved in full — the six findings this
amendment resolved, A-F, are listed in the table below. Three of them
— A, B (partially), D — are the same areas this restructuring pass's
§G corrections further refine with implementation-time precision; C
(execution harness) and the agent-write-boundary finding F are
reassigned to Stage 87B/87A respectively by this restructuring, not
reopened.)*

| Finding | Severity | Original resolution |
|---|---|---|
| A. Knowledge retrieval and compilation contract | HIGH | §A.5 (reused unchanged by this pass) |
| B. Clean-room section-compilation adapter | HIGH | Superseded by this pass's §G.B (the original resolution's assumption about `prepare_cleanroom_branch.py` allow-listing was itself found incorrect) |
| C. Safe executable-documentation verification | HIGH | Reassigned to Stage 87B (§E) |
| D. Operationalised technical-claim verification | HIGH | Refined by this pass's §G.D (the three-question framing) |
| E. Three-way incremental-maintenance reconciliation | MEDIUM | Reused unchanged by this pass (§A.3, §E) |
| F. Implementation/agent write boundaries | MEDIUM | Reused unchanged (ad-hoc dispatch, no new agent, §D.1 point 6) |

## K. Post-amendment independent planning-review verdict (2026-11-04)

**READY WITH NON-BLOCKING OBSERVATIONS**, after one NOT READY round
that found and fixed a real defect in the amendment's own description
of `detect_grounded_region_changes` (understated as four states,
omitting `doc_candidate`) — full detail preserved as historical
record. This restructuring pass's §A.3/§G corrections reuse the
corrected five-state understanding this verdict confirmed; it is not
reopened.

**The original plan's full 18-test matrix (G.5, pre-restructuring)**
is preserved here for traceability and reassigned across stages by
this restructuring pass (§D.3 for 87A's subset; 87B/87C own the rest
per §E/§F):

1. Missing evidence → 87A. 2. Contradictory knowledge → 87A. 3. Stale
evidence → 87A. 4. Clean-room isolation breach (negative control) →
87A, redesigned per §G.B. 5. Unsupported technical claim (depth) →
87A. 6. Broken executable example → 87B (needs the execution harness).
7. Schema-validation failure → 87A. 8. Manual editorial improvement
survives maintenance → 87A (one section) / 87B (real multi-section
documents). 9. Unrelated sections unchanged → 87B (needs multiple
real sections). 10. Accurate, bounded provenance → 87A, redesigned per
§G.C. 11. Documentation-quality comparison → 87C. 12. Unsupported
claim surviving the deterministic check alone (depth) → 87A. 13.
Clean-room section-export breach (negative control) → 87A, redesigned
per §G.B. 14-16. Unsafe generated command / sandbox boundary
violations / isolation-or-broker failure → 87B (14-15 need the
execution harness) / 87A (16, broker failure already in scope). 17.
Concurrent human/knowledge edits → 87B (needs real maintenance
cycles). 18. Clean-environment onboarding → 87B.

## L. This pass's scope-reduction amendment — summary

This pass restructured the plan (§D/§E/§F replacing the prior
monolithic §B-§G scope split) and corrected four integration defects
(§G), each found by direct re-inspection of the real implementation
during this restructuring, not assumed from the prior plan's own
prose:

- **§G.A** — a real parser-truncation bug in the plan's own proposed
  region-id convention, proven by direct execution.
- **§G.B** — a real, structural misunderstanding of how
  `prepare_cleanroom_branch.py` exports files (git-revision-based,
  never working-tree-based), requiring a genuinely different runtime-
  evidence-handoff design, not a one-line fix.
- **§G.C** — a real design gap (provenance and machine-readable
  grounding conflated in one field) that could have silently broken
  reconciliation for any section published with the most minimal
  citation-display setting.
- **§G.D** — a real coverage gap (no step actually owned detecting an
  untagged factual claim), closed by extending an existing dispatch
  rather than building new infrastructure.

No correction reopens the strategic architecture (§A), the schema/
pipeline contract's basic shape (§B/§C), or the original plan's full
exit-gate requirements (§F/§K) — each is a scope/sequencing/
implementation-contract correction, consistent with this being a
scope-management correction, not an architectural redesign.

## M. Independent planning-review verdict for this restructuring pass (2026-11-04)

**First round: NOT READY.** An independent reviewer, re-deriving every
load-bearing citation directly against the real source (not trusting
this document's own prose), confirmed §G.A-D's four corrections and
every other check requested (ADR fidelity, no premature 87B/87C
infrastructure, accurate API/isolation citations, non-circular §D.3
tests, clear stage gates, preserved exit criteria at §F/§K, no Phase
88-90 creep, a reasonable 87A scope). One genuine, directly-verified
blocking finding outside the four named corrections: §D.1 point 3
understated the real work needed in the already-committed `scripts/
check_doc_schema.py` — the reviewer ran the validator against §B's own
minimal schema example and got blocking findings, because the
committed script still required the pre-restructuring field set
(`purpose`/`verification_method`/`provenance` at top level; `title`/
`requires_example`/`requires_tested_example`/a nested `evidence_
requirements` dict per section), none of which matches §B's new flat
minimal shape.

**Resolution, same pass**: `scripts/check_doc_schema.py` corrected —
required-field lists now match §B exactly; `min_claim_status`/
`allow_unconfirmed_scopes` read as flat per-section fields; the old
`provenance` enum check replaced by §G.C's `citation_display` check;
§G.A's `[a-z0-9-]+` section-id pattern check added;
`requires_tested_example`/`example_comparison_mode` validated only if
present (forward-compatible with Stage 87B, never required for 87A).
`src/codecompass/doc_compiler.py`'s `find_section_gaps` corrected
identically (flat fields, not nested). §D.1 point 3 above rewritten to
describe the real scope. Tests updated/added in both `tests/
test_check_doc_schema.py` and `tests/test_doc_compiler.py` (31 tests
total across the two files, all passing); full suite 1241 passed, 2
skipped (L-114/L-107 baseline unchanged).

**Second round, independent re-check of the correction only** (narrow
scope, matching this project's own established practice for a single
mechanically-verifiable fix): **READY WITH NON-BLOCKING
OBSERVATIONS.** The reviewer independently rebuilt §B's own literal
example as a fixture and ran the real validator directly, confirming
zero findings; confirmed `find_section_gaps` reads the flat fields
consistently; ran the two affected test files directly (31 passed);
confirmed §D.1 point 3's text now matches the real diff; grepped the
whole repository and found no other remaining nested-`evidence_
requirements`-or-`provenance` assumption. One non-blocking observation:
`doc_compiler.strip_citation_tags`'s own docstring still referenced
the old top-level `schema.provenance` field name in a code comment —
corrected in the same pass (now describes the current per-section
`citation_display` field and clarifies that machine-readable grounding
is unaffected by it, per §G.C).

**Both review rounds are now closed with no remaining blocking
finding. This restructured plan is implementation-ready for Stage
87A.**

## N. Stage 87A hardening pass (2026-11-04) — four corrections to the
publication path

Stage 87A was implemented, demonstrated three times against the real
repository, and independently audited to PASS WITH NON-BLOCKING
OBSERVATIONS (§M above; `planning/retros/_audit-phase-87-stage-87a.md`).
A follow-up governing task then found four further integration defects
in the **publication path specifically** — not in the compiled
content, the knowledge resolution, or the real demonstration's own
output, all of which were independently reconfirmed sound before this
pass began.

### N.A Publication bound to manually-typed verdict strings

**Defect**: `docs publish` accepted `--semantic-verdict supported
--editorial-verdict pass` as plain CLI arguments. This proved only
that the invoking process supplied those two words — not that an
independent review had actually run, nor that its findings related to
the exact draft, evidence, or schema section being published. A typo,
a copy-paste from an unrelated review, or a deliberately forged
verdict would all have been accepted identically.

**Correction**: a new command, `docs record-review --kind
semantic|editorial --verdict V --reviewer NAME [--finding ...]
[--evidence-ref ...]`, persists each review to
`<section-id>.review-<kind>.json`, bound by a `draft_sha256`/
`evidence_sha256`/`schema_section_sha256` identity triple copied
directly from the pending-review manifest at record time.
`docs publish` now: (1) recomputes the schema section's and the
required knowledge's *live* hashes and rejects if either has changed
since compile; (2) requires both persisted review-record files to
exist, parse, carry every required field, and match the pending
manifest's current identity triple exactly; (3) requires the expected
passing verdict per kind; (4) on success, writes the tagged draft and
both review records permanently to `planning/retros/
phase-87-published-evidence/<schema-slug>/<section-id>.json`. No new
agent, database, or approval framework was introduced — the two
independent reviews are still dispatched by the lead exactly as
before (`CLAUDE.md` §8); this correction only makes the *persisted
record* of that dispatch load-bearing, where previously a bare label
string was. `--reviewer` is explicitly documented as self-reported
provenance, not a cryptographic attestation of independence — this
pass does not claim a capability it does not have.

**Tests**: full success cycle; absent review (both missing, one
missing); failing verdict; a forged review record with a
non-matching `draft_sha256`; a review bound to a draft that was since
recompiled (hash no longer matches); a review whose cited knowledge
changed after recording (re-hydration at publish time produces a
different `evidence_sha256`); an unresolved `section_id` not declared
in the live schema; an invalid verdict for a review's own kind.

### N.B Unconfined publication write target

**Defect**: `docs_publish` resolved `project_root / schema["document"]`
with no validation. An absolute path, a `..` traversal, or a `document`
value routed through a symlinked intermediate directory would all have
been followed exactly as given.

**Correction**: `doc_compiler.resolve_publication_target(project_root,
document)` — one reusable policy, called from both `check_doc_schema.py`
(schema-validation time) and `docs publish` (publication time). Rejects
an absolute path or a `..` component outright; restricts `document` to
`README.md` or a `docs/**/*.md` Markdown file; resolves both the
project root and the candidate target with `Path.resolve()` (following
any symlink) and confirms the resolved target is still contained within
the resolved root — never a string-prefix check on the unresolved path,
which a symlinked directory can defeat. `docs publish` also now
confirms `section_id` names a section actually declared in the live
schema before doing anything else.

**Tests**: `..` traversal; an absolute path; a symlinked `docs/`
directory pointing outside the repository; an unresolved section id;
a legitimate `README.md` publication (positive control).

### N.C Broker input not provably the verified bytes

**Defect**: `compose_section` wrote the evidence packet to an ephemeral
staging directory and re-verified its on-disk content hash — but then
built the broker's system prompt from the `packet` argument still held
in memory, not from what was actually re-read and verified on disk.
The hash check and the broker's actual input were two independent
values that happened to agree only because nothing between the write
and the prompt-building step mutated either one; the check proved
nothing about what the broker was actually given.

**Correction**: `compose_section` now reads the packet and manifest
back from the verified files themselves and builds the system prompt
from that re-read content — the hash verification and the broker's
input are now the same bytes by construction, not by two values
coincidentally agreeing. The staging directory is created and owned
by `compose_section` itself and removed in a `finally` block, so it is
never left behind on either the success or the failure path. No new
sandbox or broker was introduced; the existing isolation posture (§G.B)
is unchanged.

**Tests**: a regression test that mutates the in-memory packet after
its verified bytes are written and confirms the mutation never reaches
the broker prompt; staging-directory absence after both a successful
and a failed `compose_section` call.

### N.D Audit-sequencing gap closed procedurally

**Defect observed**: the Stage 87A re-audit (§M; `planning/retros/
_audit-phase-87-stage-87a.md`) inspected commit `61182a8`; `df4a806`
(a `planning/CONTEXT.md` fix for one of that re-audit's own
non-blocking observations) landed afterward and touches audited scope
without matching `CLAUDE.md` §5's narrow terminal-reconciliation
exemption (that exemption covers one specific commit flipping
`ROADMAP.md`'s phase row to `done` plus `CONTEXT.md`'s current-state
section plus the plan's own Status line, together, and only when
marking a phase/stage fully done — Stage 87A's own closeout commit did
none of that, since Phase 87 overall was correctly never marked done).
Strictly, this voided that re-audit pass under §5's letter, even though
the fix was trivial and the finding it addressed was itself
non-blocking.

**Correction**: no retroactive fix to the already-closed Stage 87A
audit record — it is preserved as historical evidence, not rewritten
(`CLAUDE.md` §5's own append-only spirit for a completed pass). Instead,
this hardening pass's own final `release-phase-auditor` dispatch (see
this pass's own retro/audit record once written) is required to audit
the actual final commit of *this* pass, covering the hardened
implementation, the corrected controls, `df4a806` itself, and every
applicable documentation/learning disposition — closing the gap going
forward by auditing real final state rather than a stale snapshot. The
learning-triage step for this pass is performed *before* that final
audit runs (not after), specifically to avoid repeating the same
sequencing mistake a second time.

### N.E Stage boundary and scope, unchanged

This pass corrects defects in Stage 87A's own publication mechanism.
It does not advance Stage 87A's own stage gate (§D.4), does not begin
Stage 87B or 87C, and does not mark Phase 87 `done`. Stage 87B's own
implementation-ready plan is drafted separately below (§O), reviewed
independently, and committed separately from this hardening pass, per
the governing task's own sequencing — Stage 87B implementation itself
is explicitly not authorised by either pass.

