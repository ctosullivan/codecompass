# Phase 87: Documentation Schema and Knowledge-Compiled Documentation — plan

**Status: restructured into three stages (87A/87B/87C), amended for
four integration defects, independently re-reviewed. Stage 87A done.
Stage 87B implemented and done (2026-11-07), independently audited
through a real FAIL→fix→PASS cycle (see
`planning/retros/_audit-phase-87-stage-87b.md`); Stage 87B's own
post-closeout hardening pass (2026-11-09) then fixed three further
publication-path integration defects (reviewed-draft integrity, live
schema freshness, a narrower write-boundary race), survived a first
re-audit FAIL on a self-certification defect, and closed on a fresh
re-audit **PASS** (see `planning/retros/_audit-phase-87-stage-87b-
hardening.md`, `planning/retros/_audit-phase-87-stage-87b-hardening-
reaudit.md`); a fourth integration defect (`schema_section_sha256`
never bound to the schema's own top-level `document`/`audience`/
`acceptance_criteria` fields) was then found and fixed the same day,
independently audited **PASS** (see `planning/retros/
_audit-phase-87-stage-87b-second-hardening-pass.md`) — Stage 87B is
now hardened against four found-and-fixed defects total. Stage 87C's
plan (§S) was independently reviewed **READY WITH NON-BLOCKING
OBSERVATIONS** (2026-11-09), then amended the same day for several
real factual/scope corrections (counts, migration gap, dependency
proof, comparator rigour) and independently re-reviewed a second time:
**READY WITH NON-BLOCKING OBSERVATIONS**. Stage 87C was then
implemented (three further `docs/concepts/` pages migrated into
knowledge-compiled regions, one migration honestly declined, a real
`CL-ADPT-005` multi-region maintenance demonstration, a matched-
baseline comparator with an honest non-advantage result, five
candidate learnings filed and triaged) and, after a first independent
audit FAIL on three missing DoD artifacts fixed in the same session,
independently re-audited **PASS** (2026-11-10, see
`planning/retros/_audit-phase-87-stage-87c.md`). **Stage 87C is
done.** A deterministic `docs/reference/cli.md` generator and a
semantic cross-document consistency checker remain explicitly deferred
from Stage 87C's own scope (§S.11), requiring their own separate
authorisation. Phase 87 overall remains not done.** This is a
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

## O. Stage 87B plan — prove usability and maintenance

**Authorisation**: planning only. This section is implementation-ready
but Stage 87B implementation itself is **not authorised** by the
governing task that produced it ("CodeCompass Orchestrator — Stage 87A
Hardening, Final Closeout and Stage 87B Planning"). Nothing below is
built until a separate, explicit authorisation is given.

### O.0 Objective

Demonstrate that CodeCompass can maintain two genuinely useful
documents — `README.md` and `docs/getting-started.md` — through a real
knowledge change, while preserving legitimate human editorial
improvements and keeping evidence-backed technical accuracy. The
primary outcome is **maintainability and usefulness**, not another
infrastructure milestone — Stage 87B adds no new persisted state, no
new agent, and no new knowledge store; everything below is either
direct reuse of Stage 87A's own mechanisms or a small, explicitly
justified extension of one of them.

### O.A What Stage 87A actually delivered, and exactly what extends

Verified directly against the real, hardened implementation (not
assumed from the plan's own prose):

| Stage 87A component | Reused as-is | Extended for 87B, and how |
|---|---|---|
| `doc_compiler.resolve_section_ids`/`check_record_currency`/`find_section_gaps`/`resolve_section_packet`/`hydrate_records`/`hash_evidence` | Yes, unchanged | No extension needed — these already operate per-section, independent of how many documents/sections exist. |
| `check_doc_schema.py` | Partially — it already validates N schema files in one run, and `_check_document_uniqueness` already scans `all_data` across every schema file given | **Must gain a new check** (§O.D point 4, third corrective amendment, finding A) — `_check_document_uniqueness` checks duplicate *document paths* only, confirmed by direct reading (`scripts/check_doc_schema.py:233-248`); nothing in this script checks duplicate composed `region:<id>` tokens across schema files, which only ever mattered once a second schema-governed document existed. |
| `compile_doc_section.py` (clean-room composition adapter) | Yes | No extension needed — one call per section, regardless of which document it belongs to. |
| `doc_compiler.publish_section` | Core write mechanism reused unchanged | **Must gain a caller-side concurrency guard** (§O.D.3 below) — confirmed by direct reading that `publish_section` itself unconditionally replaces whatever existing region matches `region_id` (`src/codecompass/doc_compiler.py:523-571`), with no check of any kind against the live region's own content or baseline. |
| `docs record-review`/`docs publish`'s hash-bound review validation (hardening pass §N.A) | Yes | No extension needed — identity is already per-`(schema_slug, section_id)`, not per-document. |
| `doc_compiler.resolve_publication_target` (hardening pass §N.B) | Yes | No extension needed — `docs/getting-started.md` already matches the existing `docs/**/*.md` allow pattern; no schema change needed to publish into it. |
| `doc_compiler.maintain_document`/`knowledge_intermediate.detect_grounded_region_changes` (five states: `new`/`noop`/`doc_candidate`/`claims_changed`/`concurrent_conflict`) and its three resolution functions (`establish_new_region_baselines`/`acknowledge_stale_grounded_region`/`write_doc_candidates_to_manifests`) | Core mechanism reused unchanged | **Two real defects the Stage 87A audit already named must be fixed** (§O.D.1/.2 below) — the CLI layer around `maintain_document`, not the function itself, which already accepts a `doc_names: tuple[str, ...]` and already treats duplicate-id detection as spanning every name given to it. |
| `knowledge_intermediate._apply_doc_region_edit`'s own re-verification pattern (region-hash + cited-id-membership + per-id content-hash, re-checked immediately before every reconciliation write, fail-closed on drift, then `_write_region_baseline` on success — `knowledge_intermediate.py:627-748`) | Pattern reused, one new small public wrapper added | **This is the exact existing precedent for finding B's publication-time concurrency guard** (§O.D.3) — `docs publish` needs the identical check-then-advance-baseline shape this function already uses for human-edit reconciliation, applied instead to a compiler-generated replacement. One new, narrow function in `knowledge_intermediate.py` (not a new concurrency system) exposes the existing private `_write_region_baseline` call for this one additional caller. |
| `verify_cleanroom_isolation.py`'s `unshare --user --map-root-user --mount --net --pid --fork` + `pivot_root` sandboxing **technique** | Technique reused, not the script itself | A new, narrow module applies the same technique to a different payload (a generated shell command, not a fake broker probe) — see §O.C. |

No parallel persistence, diffing, provenance, or approval mechanism is
introduced anywhere in this plan.

### O.B Two-document publication

**Three independent questions, kept structurally separate** (corrective
amendment, 2026-11-05, finding D) — the original draft conflated them
into one compiled/validated/manual split, which hid that a section can
be human-authored and never regenerated while still making a testable
factual claim:

1. **Compiled?** Is the section's prose generated from canonical
   knowledge through the clean-room pipeline (§C steps 1-9), or
   human-authored?
2. **Schema-governed?** Does a `*.schema.yaml` section entry name this
   content's required sections/depth/tone/acceptance criteria at all —
   independent of whether it's compiled, since a schema can require a
   human-authored section to meet a bar without ever regenerating it?
3. **Factually verified?** Does this content make a technical claim
   (a CLI flag, a generated file path, an integration, a behaviour)
   that must be checked against the real, current implementation —
   independent of both of the above, since a compiled section's claims
   are already covered by claim-verification (§C step 7) but a
   human-authored section's claims are not, unless something else
   checks them?

**`README.md.schema.yaml`** (already exists from the Stage 87A real
demonstration): the existing `## Understanding Digests` section and its
`codecompass-grounded-by region:readme-md-vendor-digest-concept` marker
are **validated in place, never regenerated** — Stage 87A's own real
content stays exactly as published. **No further README sections are
added by this plan** (corrective amendment, finding F — see §O.F.1
below for why: no real, already-accepted canonical knowledge record
supports any further README content, confirmed by directly searching
the corpus, and this plan does not invent one to hit a generation
target). Any section of `README.md` that is pure human-authored
narrative with no evidence-bearing claim (e.g. badges, a license line)
is explicitly out of schema scope — the schema governs only the
section it names, never the whole file.

**`docs/getting-started.md.schema.yaml`** (new — the file itself
already exists as hand-written prose, per `decisions/0085` §5's own
mapping table; the schema governs select sections of it, not a
wholesale rewrite). The file's real structure, confirmed by direct
reading (exactly six real `## `-level sections, unchanged since the
single commit that created it — an earlier draft of this plan wrongly
listed five further "sections" that are actually just text inside
`## A real captured example`'s own fenced code-block illustration, not
independent sections at all): `## Install`, `## First run`, `## A real
captured example`, `## Proceeding past the budget cap`, `## After the
first run`, `## Where to go next`. Classified against all three
questions above, not one combined axis:

| Section | Compiled? | Schema-governed? | Factually verified? |
|---|---|---|---|
| `## Install` | No — no real, citable knowledge record exists for it (§O.F.1) | Yes — the execution harness (§O.C) asserts `pip install codecompass-context` actually succeeds | Yes — by real execution (§O.C) |
| `## First run` | No, same reason | Yes — the harness asserts bare `codecompass` (no-candidate fixture) and `codecompass --budget 0` (`toy-project`) each produce their own documented outcome (§O.C) | Yes — by real execution, **and a real prose fix** (third corrective amendment, finding D): this section's own bold claim "It never asks you anything and never makes an AI call on its own" directly contradicts its own very next point 5 ("...asks for confirmation before calling the Anthropic API") — a genuine, pre-existing internal contradiction, confirmed by reading the live file. Corrected at implementation time to state plainly that steps 1-4 are unconditionally deterministic and non-interactive, and step 5 conditionally transitions to an interactive, potentially billable confirmation only when real, eligible candidates exist — never claiming the whole command is unconditionally non-interactive. |
| `## A real captured example` | No, same reason | Yes — the harness's own pattern-matched expected output *is* this section's content | Yes — by real execution, pattern-matched for the known-nondeterministic version/cost figures (§O.C) |
| `## Proceeding past the budget cap` | No | Yes — this section's own two commands (`--yes`, `--budget 1.00`) are real CLI contracts; verified by a mocked/unit-level test of the CLI's own confirmation-skip/budget-comparison code path (§O.C — never a live, credentialed, billed execution; `--yes`/`--budget 1.00` are **removed from the real-execution allow-list** for exactly this reason) | Yes — by the mocked test, not live execution |
| `## After the first run` | No | **Newly added to schema governance** (corrective amendment, finding D) — this section lists concrete implementation facts (`vendor/<name>/CLAUDE.md`; the root `CLAUDE.md` marker-delimited routing table; `.claude/skills/codecompass/SKILL.md`; `.claude/commands/discovery.md`; `context-graph.db`), previously and wrongly classified as "pure navigation/editorial content with no factual claim to ground or verify" | **Yes — newly required.** Each listed file/path/mechanism is checked to actually exist and behave as described against the real repository (a direct filesystem/behavioural check, not a knowledge-compiled claim — no citable record exists for this either, so this is validation-in-place, never generation) |
| `## Where to go next` | No | No | No — pure navigation to other docs by relative path; no technical claim of its own beyond "this file exists," which the broken-link class of check (if any exists elsewhere in this project) already covers, not this plan's own concern |

**`## After the first run`'s own check, named concretely** (the
independent review of this amendment found the table cell above named
*that* this section needs factual verification without naming *where*
that check lives, unlike its sibling corrections in §O.C/§O.D.3, which
are both fully specified): a new, small assertion set — in `tests/
test_check_doc_schema.py` if it fits that file's own per-rule-test
convention, or a short new script otherwise — checks, against the real
repository, that `vendor/<name>/CLAUDE.md` exists for at least one
tracked vendor, that the root `CLAUDE.md`'s own `<!-- codecompass:start
-->`/`<!-- codecompass:end -->` markers and table columns match this
section's own description, and that `.claude/skills/codecompass/
SKILL.md` and `.claude/commands/discovery.md` both exist with the
described content. **`.claude/commands/discovery.md` specifically
cannot be invoked headlessly** — it is a Claude-Code-specific slash
command trigger, not a CLI command `execute_doc_example.py`'s harness
could run — so "behave as described" for this one item means a
filesystem/content check of the generated file itself, never a true
runtime invocation; the other four items may be checked the same way
or, where practical, by actually exercising the real command/path.

**Explicitly not done**: regenerating either document wholesale, and
generating any section this table doesn't name. The Stage 87A plan's
own §G.3-successor discipline (status quo is the safe default;
regenerate only where it is demonstrably beneficial, validate in place
otherwise) governs every row above.

### O.C Safe executable-example verification

**Corrective amendment, 2026-11-05 (finding C)**: the original draft's
offline-mirror and allow-list design was underspecified to the point of
infeasibility. Two concrete problems, confirmed by direct code reading,
not assumption:

1. `source_resolution._git_clone` (`src/codecompass/source_resolution.py:86-111`)
   runs `git clone --depth 1 --quiet <url> <dest>` where `url` is
   resolved from the installed package's own real `Project-URL`
   metadata (`adapters/python.py:43-52`) — a real, public upstream URL
   (e.g. `click`/`requests`'s real GitHub repositories). Mounting a
   local mirror directory into the sandbox does nothing on its own:
   nothing in this code path reads an environment variable, a config
   file, or any other redirection knob to point `url` somewhere else.
   The original draft's "pre-populated, read-only local mirror ...
   never fetched live" was a destination with no mechanism connecting
   the real command to it.
2. The original allow-list included `codecompass --yes` and
   `codecompass --budget 1.00` — both can trigger a real, paid
   Anthropic API call (`enrichment.check_budget`'s own disclosed-cost
   gate, `src/codecompass/enrichment.py:593-619`, is a pre-call
   estimate; a budget *above* the estimate lets the call proceed). A
   sandbox that deliberately excludes credentials (as this one must)
   cannot make that call succeed — it can only time out or fail, which
   is not a meaningful verification of anything the document claims.

**Correction, in order (per the governing task's own instruction to
reconsider whether new sandboxing is needed at all before specifying
it)**:

- **Container/established-isolation check, performed, not assumed**:
  this host has no `docker`/`podman`/`bwrap`/`firejail` installed
  (confirmed: `which docker podman bwrap firejail` all report nothing
  found). `unshare` is present and is the exact mechanism
  `verify_cleanroom_isolation.py` already builds on and has a real,
  passing preflight for in this repository today. There is no simpler,
  already-established, already-verified isolation mechanism available
  in this environment to prefer over it — reusing its *technique*
  remains the right call, confirmed by checking rather than assumed
  from the prior draft's own say-so.
- **The git-clone redirection problem is solved at the `git` transport
  layer, not in application code** — no change to
  `source_resolution.py` at all. A sandbox-local `~/.gitconfig` (or a
  file pointed to by `GIT_CONFIG_GLOBAL`, prepared once, out of band)
  contains one `url.<base>.insteadOf` entry per fixture vendor's real,
  resolved upstream URL (`click`, `requests` — the same two
  `examples/toy-project/` already depends on), rewriting it to a
  `file://` path onto a locally-prepared bare mirror of that exact
  repository. `git clone <real-url>` inside the sandbox then
  transparently resolves to the local mirror through `git`'s own,
  long-established URL-rewriting feature — the real command the user
  would type, the real code path `source_resolution.py` already runs,
  with zero application-code change and zero live network fetch. The
  two real upstream URLs are resolved the same way the running code
  already resolves them (`adapter.repository_url()` against the
  toy-project's own installed metadata) — confirmed directly at
  implementation time, not hardcoded as an assumption in this plan.
- **Paid/API-triggering commands are removed from the real-execution
  allow-list entirely** — `codecompass --yes` and `codecompass
  --budget 1.00` are verified through a mocked/unit-level test of the
  CLI's own confirmation-skip (`--yes`) and budget-comparison
  (`--budget`) code paths (`cli.py`'s `_bootstrap`/
  `_maybe_run_enrichment`, `enrichment.check_budget`), with a stubbed
  broker/enrichment call exactly like `tests/test_cleanroom_broker.py`'s
  own existing mocked-subprocess convention — never a live, credentialed,
  billed call, inside or outside the sandbox. **Three distinct scenarios
  required (finding D), each its own test, never conflated**: (1) bare
  `codecompass`/no eligible candidates — no confirm, no budget check,
  no API call reached at all (`_maybe_run_enrichment`'s own early
  `return` at the "no candidates" branch); (2) `codecompass --budget 0`/
  real candidates — `check_budget` raises and aborts *before*
  `typer.confirm` is ever reached (confirmed directly,
  `_maybe_run_enrichment`'s own docstring: "Budget is checked *before*
  the confirmation prompt"); (3) `--yes` or a mocked `typer.confirm`
  returning `True`, sufficient budget, real candidates — the code path
  genuinely reaches the stubbed enrichment/broker call, confirming
  `--yes`/an accepted interactive confirmation really do authorise the
  call they claim to, with the call itself mocked, never live. This
  also resolves §O.B's reclassification of "## Proceeding past the
  budget cap" above.

**Existing mechanisms assessed first, per the governing task's own
instruction, before specifying anything new**:

- `scripts/check_contracts.py`/`oracle.py`'s pytest execution provider
  (Phase 82) executes a *named, pre-written* test file against a
  pinned revision — not a free-form, AI-generated shell command. Not
  reusable as-is: `docs/getting-started.md`'s own install/first-run
  sequence is shell commands (`pip install codecompass-context`, bare
  `codecompass`), not a pytest invocation.
- `scripts/verify_cleanroom_isolation.py` (Phase 81B Amendment 5)
  already builds a disposable Linux-namespace sandbox (`unshare
  --user --map-root-user --mount --net --pid --fork` + `pivot_root`)
  and runs a probe inside it — but that probe is a fixed, fake,
  content-neutral stand-in; it was never designed to run an arbitrary
  command and report its real stdout/exit code back.
- `scripts/prepare_cleanroom_branch.py`'s clean-room export mechanism
  and `scripts/cleanroom_broker.py`'s sanitised-subprocess model both
  isolate *what the model can read*, not what a *generated command*
  can do once produced — a different problem (untrusted generated
  output, not untrusted generation input).

**Conclusion**: no existing mechanism safely executes an untrusted,
possibly-AI-touched shell command end to end. A narrow, new harness is
justified — reusing the proven `unshare`/`pivot_root` *technique*
directly (not a new sandboxing approach), applied to a different,
narrower payload.

**Specification** (`scripts/execute_doc_example.py`, new, Stage 87B
only):

- **Input**: one command from a small, explicit, hand-maintained
  allow-list derived directly from `docs/getting-started.md`'s own
  real, current command blocks, **narrowed again by this corrective
  amendment** to exclude anything that cannot genuinely complete inside
  a credential-less sandbox: `pip install codecompass-context`; bare
  `codecompass` **against a fixture with zero eligible enrichment
  candidates**; `codecompass --budget 0` **against the real
  `examples/toy-project/` fixture, which genuinely has eligible
  candidates** (`click`/`requests`, both imported and unenriched); and
  `codecompass query vendors` (a pure local `sqlite3` read, no network,
  no API). `codecompass --yes`/`codecompass --budget 1.00` are
  **removed** from this list (see above) — verified by a mocked unit
  test instead, never by this harness. No other command, until this
  document is extended to demonstrate one. Widening the allow-list is a
  deliberate, reviewed, future edit to this script, never a runtime
  decision the harness makes for itself.

  **Third corrective amendment, finding D**: the prior draft treated
  bare `codecompass` and `codecompass --budget 0` as interchangeable,
  both implicitly run against `examples/toy-project/`. That is unsafe
  as specified — `toy-project` genuinely has eligible candidates, and
  the real CLI's own deterministic bootstrap (`cli.py`'s `_bootstrap`)
  conditionally transitions to an **interactive** confirmation prompt
  when eligible candidates exist and no `--budget`/`--yes` already
  resolved the question (confirmed directly: `docs/getting-started.md`
  own "## First run" text already states this, at odds with its own,
  immediately-preceding bold claim that the command "never asks you
  anything" — a real, pre-existing internal contradiction in this
  document, corrected below). A harness with no interactive stdin and
  no credentials running bare `codecompass` against `toy-project` would
  not deterministically complete at all. **Fix**: bare `codecompass`
  runs against a **new, minimal, dedicated fixture**
  (`examples/no-candidates-project/` or equivalent — a project with a
  real manifest file, so the deterministic scan/clone/graph-rebuild
  steps 1-4 all genuinely run, but whose own source code imports
  nothing CodeCompass can detect, so step 5 structurally never
  triggers), confirming the truly-unconditional half of the bootstrap
  completes deterministically with no prompt and no API call — a
  different, genuinely-safe scenario from `--budget 0` against
  `toy-project`, not a stand-in for it. `codecompass --budget 0`
  against the real `toy-project` fixture is kept exactly as already
  specified — `check_budget` raises and aborts *before* the
  interactive-confirmation step is ever reached regardless of how many
  real candidates exist (confirmed directly,
  `src/codecompass/enrichment.py:593-619` — the budget check runs
  strictly before `_maybe_run_enrichment`'s own confirm/`--yes` gate),
  so this remains genuinely deterministic and safe for the harness.
- **Package/environment availability**: a Python virtual environment
  is created once, out of band, inside the sandbox-visible scratch
  tree; `pip install --no-index --find-links=<local-wheel-cache-dir>
  codecompass-context` (and its own declared dependencies, all present
  in the same local wheel cache — `typer`/`rich`/`pyyaml`/etc., the
  project's own real runtime dependency set) runs fully offline against
  that pre-populated cache, never PyPI's own index. This is the actual
  command under test for `## Install`, run for real, not mocked.
- **Fixture-vendor clone redirection**: the `~/.gitconfig`
  `insteadOf`-rewrite mechanism above, prepared once, out of band,
  mounted read-only into the sandbox at the path `git` itself reads
  global config from (`GIT_CONFIG_GLOBAL`, set in the sandboxed
  process's own environment).
- **Isolation**: the same `unshare --user --map-root-user --mount --net
  --pid --fork` + `pivot_root` construction `verify_cleanroom_
  isolation.py` already uses and already has a working, tested
  preflight for — reused directly, not reinvented.
- **Restrictions, all enforced, all tested**: no credentials or host
  environment passed through (`cleanroom_broker._sanitize_env()`'s own
  convention, reused — in particular, no `ANTHROPIC_API_KEY`, which
  also structurally guarantees `--yes`/`--budget 1.00` could never
  succeed even if mistakenly allow-listed, a second, independent
  reason they're excluded); the sandbox's own `--net` unshare blocks
  any network reachability the `git`/`pip` redirections above don't
  already make moot; a fresh, disposable scratch tree created per run
  (`tempfile.mkdtemp()`-style, mirroring `compile_doc_section.py`'s own
  convention) as the one writable project directory, distinct from
  both the real project checkout and `$HOME`; a wall-clock timeout per
  command; bounded stdout/stderr capture size; no auto-retry on
  failure (a failing command is reported exactly once, never silently
  re-attempted hoping for a different result — the Stage 87A plan's
  own "no silent re-prompting to force a pass" principle, extended
  here from AI generation to command execution).
- **Expected-outcome classification**: each allow-list entry's own
  manifest entry (not a new schema concept — `check_doc_schema.py`'s
  already-defined, previously-unused `_VALID_COMPARISON_MODE` enum,
  `{"exact","normalized_whitespace","regex"}`, now actually consumed)
  carries an **`expected_exit_code`** (so `codecompass --budget 0`'s
  own documented non-zero exit is the *passing* outcome, not a harness
  failure) and a comparison pattern. `pip install`/`codecompass query
  vendors` use `exact`/`normalized_whitespace` where output is stable;
  `codecompass`/`codecompass --budget 0` use `regex`, with the real
  captured example's own nondeterministic figures (`click 8.4.2` →
  `click \d+\.\d+\.\d+`; `requests 2.34.2` → `requests \d+\.\d+\.\d+`;
  `~$0.02`/`$0.02` → `\$\d+\.\d\d`) replaced by narrow numeric-shape
  patterns, never a blanket wildcard that would also pass a materially
  wrong output.
- **Negative controls**: a command string not present in the allow-list
  is rejected before the sandbox is even entered (no process spawned at
  all); a deliberately broken or absent isolation preflight aborts the
  whole harness run before any command runs, mirroring
  `compile_doc_section.py`'s own `run_isolation_preflight` pattern
  exactly (fail closed, never an un-isolated fallback attempt).
- **Output**: exit code, stdout/stderr (bounded size), and a pass/fail
  classification against the documentation's own claimed outcome.
  Never executed unrestricted on the host; never given a
  model-generated command that didn't come from the fixed allow-list;
  never asked to complete a paid or credentialed operation.

### O.D Genuine manual-maintenance reconciliation

Both items below were named directly by the Stage 87A `release-phase-
auditor`'s own non-blocking observations (`planning/retros/
_audit-phase-87-stage-87a.md` §10) — not new findings, carried forward
and now in scope to fix because 87B is the first stage where they
would otherwise actually bite:

1. **Project-wide document discovery.** `docs maintain` currently takes
   one `SCHEMA_PATH` argument and passes `(schema["document"],)` — a
   single-element tuple — into `doc_compiler.maintain_document`, even
   though `detect_grounded_region_changes`'s own duplicate-region-id
   check is only genuinely project-wide when every schema-governed
   document is passed in the same call. Harmless today (exactly one
   schema-governed document exists); with two (87B), a real duplicate
   `region:<id>` between `README.md` and `docs/getting-started.md`
   would go undetected by two separate single-document `docs maintain`
   invocations. **Fix**: `docs maintain` takes zero or more
   `SCHEMA_PATH` arguments; given zero, it discovers every
   `*.schema.yaml` under the project root itself (mirroring
   `check_doc_schema.py`'s own existing `_discover_schema_files`
   convention exactly, not a new discovery mechanism), reads each
   one's own `document` field, and calls `maintain_document` once with
   every discovered document name in one `doc_names` tuple. No change
   to `doc_compiler.maintain_document`'s own signature or to
   `knowledge_intermediate.detect_grounded_region_changes` — both
   already support this; only the CLI's own call-site behaviour
   changes.
2. **Idempotent reconciliation-candidate handling.**
   `write_doc_candidates_to_manifests` writes a fresh, timestamped
   manifest file on every call for every `doc_candidate` finding, with
   no check against an already-pending, unresolved manifest item
   covering the exact same region in the exact same state — confirmed
   empirically in the Stage 87A audit (a second `docs maintain` run on
   an untouched `doc_candidate` region produced a near-duplicate
   manifest). **Fix, specified for 87B's own implementation, not built
   now**: before writing a new `doc_region_edit` item for a given
   `(doc_name, region_id-or-index)`, scan that slug's own
   `reconciliation/*.toml` manifests for an existing item with
   `"state": "pending"` whose own `region_id`/`region_index`,
   `base_region_hash`, and `cited_hashes_at_detection` already match
   the newly detected finding's values exactly; skip writing a new item
   when such a match exists, write a new one only when no pending match
   exists or the matched item's own recorded values differ (meaning the
   underlying facts changed again since the last unresolved manifest).
   This reuses the manifest's own existing `state`/fields — no new
   schema field, no new store, no change to how an item is actually
   resolved (`_apply_doc_region_edit` and friends, unchanged). **A
   real, already-existing fixture tests this directly, confirmed
   present on disk right now**:
   `planning/knowledge/codecompass-domain/reconciliation/
   20261104T081241Z-doc.toml`, the real, still-unresolved
   `doc_region_edit` manifest `write_doc_candidates_to_manifests`
   already wrote for `intermediate-knowledge-layer` during Stage 87A's
   own real demonstration — this fix's own test runs `docs maintain`
   against the live repository and asserts **zero** new manifest files
   appear for that region (not a synthetic stand-in), since this exact
   candidate already exists, unresolved, in its exact current state.
   **This candidate is never artificially acknowledged merely to make
   a test report `noop`** — it stays a real, open `doc_candidate`
   throughout 87B, exactly as §O.D.0 below states.
3. **Publication-time concurrency guard, strengthened (corrective
   amendment finding B; fail-closed hardening, third corrective
   amendment finding C).** `docs publish` validates draft, evidence,
   and schema-section identity (hardening pass §N.A) but never checks
   whether the *live* target region has drifted from what was last
   known before overwriting it — confirmed directly: `publish_section`
   (`doc_compiler.py:523-571`) unconditionally replaces whatever
   existing region matches `region_id`. A human could edit that exact
   region between compile-time and publish-time and have it silently
   clobbered.

   **The second corrective amendment's own first design had two
   further fail-open gaps, found by a later review and fixed here**:
   (1) it treated "no marker exists yet" and "a marker exists with
   `.case == \"new\"`" as the same, unconditionally-safe case — but
   `"new"` means the marker's own text is **already present** in the
   live document (parsed from it directly), simply never yet baselined;
   if that text is genuinely human-authored (e.g. hand-written before
   `docs maintain` ever ran), treating it as automatically safe to
   overwrite is exactly the same silent-clobber risk the guard exists
   to prevent — only for an unbaselined region instead of a baselined
   one. (2) the check-then-write sequence has a time-of-check-to-
   time-of-use gap: nothing re-verifies the live region between
   `detect_grounded_region_changes` returning and `publish_section`
   actually writing, and nothing prevents two concurrent `docs
   publish`/`docs maintain` invocations from interleaving their own
   detect-then-write steps against each other.

   **Fix, addressing both**:
   - Immediately before calling `publish_section`, `docs publish` runs
     `knowledge_intermediate.detect_grounded_region_changes(project_root,
     (schema["document"],))` and locates the one finding matching this
     `region_id`, reusing the exact same re-verification shape
     `_apply_doc_region_edit` already performs for human-edit
     reconciliation (region-hash, cited-id-set membership, per-id
     content-hash — `knowledge_intermediate.py:627-748`), never a new,
     separately-invented concurrency check:
     - **No finding at all for this `region_id`** (no marker exists in
       the document at all) → proceed. Genuinely nothing to overwrite.
     - **A finding whose own `.case` is `"new"`** (the marker's text
       already exists, unbaselined) → **not** automatically safe.
       Compare the live region's own current text hash
       (`GroundedRegionFinding.region_hash`, already computed by
       `detect_grounded_region_changes`) against the hash of the body
       about to be published. Equal → proceed (this is a legitimate
       idempotent re-publish/baseline-catch-up of content already
       there, e.g. a previous run that published successfully but was
       interrupted before the baseline-advance step below ran).
       Unequal → **refuse**, exit non-zero, name the drift explicitly
       — the live content is not provably the compiler's own prior
       output, so it is never assumed safe to discard.
     - `noop` (live region matches its recorded baseline exactly) →
       proceed; the new, reviewed draft replaces content that hasn't
       independently drifted.
     - `claims_changed` (live region's prose still matches baseline;
       only its cited knowledge moved) → proceed — `docs publish`'s own
       existing evidence-hash check already proves the draft being
       published reflects the *current* knowledge state, so this
       publish **is** the "current, independently verified replacement"
       a `claims_changed` state requires; it is never read as blanket
       permission to overwrite on its own (a `claims_changed` state
       with a *stale* draft — one compiled before the knowledge
       changed — would already be rejected by the existing
       evidence-hash check, independent of this new guard).
     - `doc_candidate` (the live region's own prose has drifted from
       baseline, no matching knowledge change) → **refuse**, exit
       non-zero, name the drift explicitly; this is exactly "the
       region contains unacknowledged human changes."
     - `concurrent_conflict` (both drifted) → **refuse**, exit
       non-zero; requires explicit lead-controlled reconciliation,
       never an automatic merge either direction.
   - **Revalidation at the write boundary, and a cooperating-writer
     lock** — the entire sequence above (detect → decide → write →
     advance baseline) runs while holding one simple, process-external
     lock: an exclusive, `O_CREAT|O_EXCL`-created lock file at a fixed
     path (e.g. `.codecompass-docs-publish.lock` at the project root),
     released (removed) in a `finally` block covering success and
     every failure path, with a bounded wait/timeout before giving up
     rather than blocking forever. This is a plain mutex around one
     critical section, not a transaction framework, new persisted
     state, or a version-control system — the lock file's own content
     is irrelevant and it is never read for any purpose beyond "does
     it exist." Immediately after acquiring the lock, the live
     region's own current text hash is **re-read and re-compared**
     against the same decision made above — closing the
     check-then-write gap to the smallest window a single process can
     achieve, never trusting a decision made before the lock was held.
     **Documented limit, explicitly, not left implicit**: this lock
     only serialises *cooperating* callers — other `docs publish`/
     `docs maintain` invocations against the same project root, which
     is the only concurrent writer this stage's own design needs to
     protect against (a human editing the file in a text editor holds
     no lock and never will; the hash re-check immediately above is
     what catches *that* case, with or without the lock, which is why
     both mechanisms exist rather than either alone).
   - **Baseline advances only after the write itself genuinely
     succeeds** — if `publish_section` raises for any reason, the
     baseline is never advanced (unchanged from before: baseline
     advancement was always sequenced strictly after a successful
     write, never before or regardless of outcome). Detection
     (`detect_grounded_region_changes`) itself remains read-only, as
     it always was — it is the *caller*'s own responsibility, not this
     function's, to never advance a baseline merely because detection
     ran. A **rejected** publish (any `refuse` branch above) never
     reaches the write step at all, so no baseline write is even
     attempted.
   - On a successful publish, one new, narrow, explicitly-justified
     public function in `knowledge_intermediate.py` (not a new
     concurrency system — a thin wrapper around the existing private
     `_write_region_baseline`, the same call `establish_new_region_
     baselines`/`acknowledge_stale_grounded_region`/
     `_apply_doc_region_edit` already each make on their own successful
     path) advances this region's baseline to the newly-published
     body's hash and the cited records' current content hashes —
     without this, the *next* `docs maintain` run would wrongly see the
     just-published content as having drifted from a now-stale
     baseline and misreport `concurrent_conflict` or `doc_candidate`
     for a change that was actually a correct, reviewed republish.

   **Regression tests required** (third corrective amendment, finding
   C's own explicit list): an unbaselined region whose live text does
   **not** match the body about to be published is refused, never
   silently overwritten (the new, previously-missing case); an
   intervening edit between the initial detect call and a deliberately
   delayed write is caught by the write-boundary revalidation (a test
   that monkeypatches/injects a document mutation between the two
   steps); a cited-knowledge change between detect and write is caught
   the same way; a `publish_section` write failure leaves the baseline
   untouched; a legitimate republish (the `claims_changed`/matching-
   `"new"` cases) succeeds and the baseline advances correctly
   afterward; two concurrent `docs publish` invocations against the
   same project serialise correctly through the lock (one succeeds,
   the other either waits and then re-evaluates, or times out cleanly
   — never corrupts the document or double-writes).
4. **Cross-document grounded-region-ID validation at schema-validation
   time (new finding, second corrective amendment, finding A).**
   `check_doc_schema.py::_check_document_uniqueness` (confirmed by
   direct reading, `scripts/check_doc_schema.py:233-248`) checks that
   two schemas never govern the *same document path* — it has nothing
   to do with region ids. The only existing duplicate-`region:<id>`
   protection, `knowledge_intermediate._check_no_duplicate_region_ids`,
   reads already-*published* document text at reconciliation time
   (`detect_grounded_region_changes`/`docs maintain`) — it cannot catch
   a collision before either section is ever compiled or published.
   Today, with one schema-governed document, this gap is unreachable;
   with two (87B), two different schema files could each declare a
   section `id` that composes into the identical `region:<schema_slug>-
   <section_id>` token (e.g. both naming a section `id: install`) with
   nothing catching it until an actual publish happens to collide.
   **Fix**: a new `check_doc_schema.py` check,
   `_check_cross_document_region_id_uniqueness`, computes every
   section's own composed region id (`f"{schema_slug}-{section['id']}"`
   — the exact same composition `docs publish` already uses) across
   *every* schema file passed to one `run_all` invocation, flagging any
   value that repeats, whether across two different schema files or
   twice within one. This requires the slug computation itself to stop
   being private to `cli.py`'s own `_schema_slug` — moved to
   `doc_compiler.compute_schema_slug(schema_path)`, one canonical
   function, with `cli.py`'s three existing call sites updated to use
   it directly (removing the private copy, never two independently-
   maintained slug computations that could drift apart — the same
   discipline `hash_evidence` already established in the hardening
   pass). **Tests required, both directions**: two schema files
   declaring the identical section `id` for *different* documents is
   blocking; two sections with the same `id` inside *one* schema file
   is blocking; two schema files with genuinely distinct section ids
   (the real `README.md.schema.yaml`/`docs/getting-started.md.schema.yaml`
   pair) produce zero findings — a real positive control, not only a
   synthetic negative one. **Corrects §O.F criterion 9 below, which
   previously and wrongly claimed this was "already covered" by
   `_check_document_uniqueness`.**

**End-to-end negative test, required** (governing task's own explicit
scenario): compile a section → independently review it (both
dispatches pass) → a human edits the *target* section's live text in
the document (simulating an edit arriving after compilation, before
publication) → `docs publish` is invoked → publication is **refused**
(the `doc_candidate` branch above fires) → the human's edit is
confirmed byte-identical afterward, and the reviewed draft is not
silently applied on top of it or anywhere else.

### O.D.0 Corrected initial-state assumption (finding G)

The original draft assumed both pre-existing `README.md` grounded
regions report `noop`. **Confirmed wrong by directly running
`detect_grounded_region_changes` against the live repository right
now**: `intermediate-knowledge-layer` (citing `CL-KNOW-001`) reports
**`doc_candidate`** — a real, pre-existing, unresolved candidate,
predating Phase 87 entirely; only `readme-md-vendor-digest-concept`
(citing `CL-CTXT-005`, Stage 87A's own real demonstration) reports
`noop`. Every `noop`-case test and every acceptance criterion below is
written against this real, corrected state — the `intermediate-
knowledge-layer` region's own `doc_candidate` status is preserved and
explicitly asserted to remain open throughout 87B, used as the real
fixture for §O.D.2's idempotency test, never resolved merely to make a
different test pass.

**Five real cases planned** (the mandatory acceptance criteria, §O.F
below, name the concrete fixtures/commits each will use):

- **`new`** — a freshly schema-governed, freshly compiled
  `docs/getting-started.md` section's first publish (there being no
  real compiled-knowledge README section to add, per §O.B/§O.F.1 — if
  `docs/getting-started.md` itself ends up with zero compiled sections
  too, this case is instead demonstrated against a second, newly
  schema-governed `README.md` section once/if §O.F.1's knowledge
  search turns one up at implementation time; if genuinely none
  exists, this case is demonstrated as a synthetic negative-control
  fixture only, explicitly labelled as such, never conflated with the
  real end-to-end demonstration in §O.E).
- **`noop`** — running `docs maintain` a second time with nothing
  changed reports `noop` for `readme-md-vendor-digest-concept`
  (`CL-CTXT-005`) — a real, pre-existing fixture, reused rather than
  fabricated — and **continues to report `doc_candidate`**, not
  `noop`, for `intermediate-knowledge-layer` (§O.D.0).
- **`doc_candidate`** — the real, pre-existing `intermediate-
  knowledge-layer` candidate (§O.D.0) demonstrates detection directly;
  a second, deliberate, real human edit to a *compiled* section's own
  prose (no knowledge change) demonstrates the never-auto-regenerated
  guarantee — confirmed by running `docs compile` again afterward and
  confirming it does not overwrite the human edit (compilation and
  maintenance are separate commands; maintenance alone never calls
  compilation), and by the end-to-end negative test above (`docs
  publish` refusing to overwrite it).
- **`claims_changed`** — a real, accepted knowledge update (§O.E's own
  knowledge-driven-update demonstration) to a record a compiled
  section cites (`CL-CTXT-005`, in an isolated worktree per §O.E — not
  production canonical knowledge) is detected and reported, resolved
  either by `acknowledge_stale_grounded_region` (when independent
  evidence confirms the existing prose remains accurate) or by a real
  recompile-review-republish cycle through the new concurrency guard
  above (when it doesn't) — never silently absorbed either way.
- **`concurrent_conflict`** — both the region's own prose and its cited
  knowledge change between two `docs maintain` runs; reported, with no
  automatic resolution function at all (none exists today, and 87B
  does not add one) — an explicit, lead-controlled decision every time.

Unrelated sections of both documents must remain byte-identical across
every one of the above operations — not asserted, tested directly (a
file-content diff against a pinned copy, scoped to every byte outside
the one touched region's own marker span).

No automatic source-change trigger of any kind — that is Phase 89's
own, explicitly separate scope, unchanged by this plan.

### O.E Genuine knowledge-change demonstration, bounded cost/value assessment, and a corrected comparator

**Corrective amendment, 2026-11-05 (finding E)**: `acknowledge_stale_
grounded_region` is the resolution for a `claims_changed` finding
*when independent evidence confirms the existing prose is still
accurate* — it is not, and must not be read as, "how documentation
gets updated after a material knowledge change." The original draft's
own §O.D case list cited it as if it demonstrated a maintenance
*update*, which it structurally cannot: it never touches the document's
own text. Stage 87B's real demonstration therefore requires an actual
knowledge change that makes an existing grounded statement genuinely
outdated, run end to end:

1. **The change enters canonical knowledge through the established
   controlled lifecycle** — **a genuine, already-identified gap, not a
   hypothetical placeholder (third corrective amendment, finding E)**:
   `CL-CTXT-005`'s own current statement describes `sync_vendor`
   rendering the digest "unconditionally on every whole-project sync
   for every tracked vendor," but says nothing about what happens when
   the underlying clone fails. Read directly,
   `sync_vendor`'s own docstring and body (`src/codecompass/sync.py:
   107-153`) state a real, already-implemented, already-tested
   fallback: "If source resolution/cloning fails, `description_error`
   is set... and `vendor/<name>/src/` falls back to the old
   local-install-sourced snapshot (`decisions/0004`)... `FILETREE.md`/
   `filetree.json`/the symbol index fall back to rendering from
   `source_location()` too" — confirmed independently exercised today,
   not merely claimed, by `tests/test_sync.py:282-293` (a real test
   that forces `SourceResolutionError` and asserts
   `digest.description_error` is set). This is a genuine, currently-
   true, independently-verifiable fact about the real `VendorDigest`/
   `sync_vendor` behaviour that `CL-CTXT-005` has simply never
   captured — not a source-behaviour *change* manufactured for this
   demonstration, but exactly the kind of "isolated source-behaviour
   fact, independently established" the governing task's own §E
   permits as a legitimate correction target. The amendment: extend
   `CL-CTXT-005`'s own statement (or add a new, directly-related Claim)
   to state this fallback plainly, with `EV-CTXT-*`-style evidence
   citing `sync.py:128-133` and `tests/test_sync.py:282-293` directly
   — found and adjudicated the same way any other candidate is (a
   `context-researcher`-style investigation producing this exact real
   evidence, `knowledge-curator` adjudication, promotion to
   `supported`) — never a knowledge record fabricated, weakened, or
   arbitrarily rewritten to force a passing test. **If this specific
   investigation does not actually confirm the amendment is warranted
   once genuinely attempted at implementation time** (e.g. the
   fallback turns out to already be adequately captured elsewhere, or
   the evidence doesn't hold up to the same scrutiny Stage 87A's own
   real demonstration applied), **this plan requires reporting that
   limitation honestly and either finding a second legitimate
   candidate or substituting a synthetic, explicitly-labelled
   negative-control fixture for this one acceptance criterion alone —
   never manufacturing a successful demonstration to avoid reporting
   a gap.**
2. **The dependency relationship correctly identifies the affected
   section** — `README.md`'s `vendor-digest-concept` region, the only
   real compiled section that cites `CL-CTXT-005` today.
3. **Existing maintenance correctly detects the changed knowledge** —
   `docs maintain` reports `claims_changed` for exactly this region.
4. **A revised section is compiled or manually corrected** — `docs
   compile` regenerates the section against the new knowledge state
   (or, if compilation isn't warranted, a manual correction is made
   and schema-validated the same way).
5. **Independent semantic and editorial reviews validate the
   replacement** — both dispatches, persisted via `docs
   record-review`, exactly as Stage 87A's own real section was.
6. **Publication respects the concurrency guard** — `docs publish`'s
   §O.D.3 check confirms this is a legitimate `claims_changed`
   republish, not a drifted overwrite.
7. **The updated section and baselines reconcile correctly** — a
   subsequent `docs maintain` reports `noop` for this region
   afterward, never a stale `concurrent_conflict`.
8. **Unrelated sections remain byte-identical** — including
   `intermediate-knowledge-layer`'s own, still-open `doc_candidate`
   state (§O.D.0), which this experiment must not touch at all.

**Run in an isolated worktree or disposable test repository, never
against production canonical knowledge** (the governing task's own
explicit instruction) — a `git worktree` (or an equivalent disposable
clone) seeded from the real, current repository state, so the
knowledge-amendment step, the compile/review/publish cycle, and the
reconciliation check all run against a real copy of the real corpus,
without risking or requiring any change to the actual
`planning/knowledge/codecompass-domain/` the live project depends on.
The worktree is discarded after the demonstration; only the retro/log
documenting what happened is kept.

**Bounded value-and-cost assessment**, captured for every real
compilation/maintenance run in this stage (a structured log, not a new
persisted knowledge record — a scratch artifact under `planning/
retros/`, matching Stage 87A's own real-demonstration record-keeping
convention):

- Model and review-dispatch call counts (one entry per real clean-room
  composition call and per independent review dispatch, mirroring
  Stage 87A's own retro, which already recorded "three real generation
  attempts and six independent review dispatches" but not a cost
  figure — named explicitly as a gap by this governing task).
- Actual token/API cost where available from the dispatch's own
  reported usage; explicitly disclosed as unavailable where it isn't,
  never estimated and presented as measured.
- Wall-clock time per compilation/review/maintenance cycle.
- Human correction effort — a plain count of edits the lead made to a
  draft before it passed review, and why.
- Rejected drafts and their causes (Stage 87A's own three-round
  pattern, continued here if it recurs).
- Factual errors found before publication (by the independent semantic-
  support dispatch), counted and classified.
- Resulting documentation's own usefulness — the onboarding exercise's
  own pass/fail plus any friction noted during it (acceptance criterion 2, §O.F).
- Effort required to maintain documentation after the real knowledge
  change above, timed end to end (steps 1-7).

**Corrected conventional-agent comparator (finding A)**: the original
draft's own comparator task — "update `docs/getting-started.md`'s
`## Known gotchas` section" — targets a section that does not exist;
`## Known gotchas` is text inside a fenced illustration, not a real
section of this document (§O.B). **Corrected**: the comparator performs
the *exact same task* as the real demonstration above — given the same
real, accepted `CL-CTXT-005` amendment (worktree-isolated, identical
pinned starting revision, identical evidence access, identical task
requirements), a separate, ad-hoc `general-purpose` dispatch (no new
agent) updates `README.md`'s real `vendor-digest-concept` region
directly, with no schema, no compiler, no publication pipeline. Its
own output is independently reviewed by the same two-question
(factual, editorial) process the compiled arm uses, so both arms are
judged by the same bar; its own effort/time/correction count is
recorded in the same log. **This is not the matched-baseline
experiment** — one real task, not a reproducible rubric-scored trial;
no blinding, no fixed rubric pre-registered before results, no
statistical claim; Stage 87C carries that full discipline (plan's own
§F, `decisions/0085` §6). 87B's comparator exists only to give the
cost/value report a point of reference, and the report states plainly
whether the compiler's extra verification/maintenance machinery
justified its cost on this one real case, without presuming an
advantage either way.

### O.F Verified knowledge coverage and strengthened acceptance criteria

**O.F.1 Knowledge coverage audit (finding F).** The original draft
proposed compiling "further sections for install and first-steps
content" into `README.md` without identifying which accepted records
would support them. Checked directly against the real corpus
(`knowledge_api.search` for "install"/"budget"/"bootstrap"/"CLI
command"/"zero-question," then every `CL-ADPT-*`/`CL-CTXT-*` statement
read in full): every real, accepted Claim in `planning/knowledge/
codecompass-domain/` is a terminology/concept clarification (what
"adapter," "context," "connector," "capability," "relationship," and
similar terms mean in this project) — none describes the installation
procedure, the zero-question deterministic bootstrap (`decisions/0017`),
or any other install/first-step fact `README.md`/`docs/
getting-started.md` would compile prose from. **Conclusion, per the
governing task's own explicit instruction to adjust scope rather than
weaken evidence requirements**: no new compiled sections are added to
either document by this plan (§O.B's own table already reflects this —
zero rows there are "Compiled: Yes"). The mandatory real
knowledge-driven update (§O.E) is instead demonstrated against the one
real compiled section that already exists and is already
evidence-backed (`README.md`'s `vendor-digest-concept`, citing
`CL-CTXT-005`) — satisfying the governing task's own requirement that
this stage's demonstration "must still include one real
knowledge-driven documentation update, not merely two schema files or
additional prose generation" without inventing knowledge to get there.
If Stage 87B's own implementation-time work turns up a genuinely new,
evidence-backed record worth compiling (e.g. through the same
controlled lifecycle §O.E's demonstration already uses), it is added
at that point, re-derived from the real record — never assumed here.

**Mandatory acceptance criteria** (strengthened; each distinguishes a
synthetic negative-control test from the real end-to-end demonstration
explicitly, per the governing task's own instruction):

1. Both documents pass schema validation and the factual-verification
   requirements appropriate to their own governed sections (§O.B's
   table) — `tests/test_check_doc_schema.py` (extended: two real schema
   files together pass `check_doc_schema.py --strict` with zero
   blocking findings; `_check_document_uniqueness` exercised with a
   real two-schema-file case) is the synthetic/mechanical half; the
   `## After the first run` factual-verification check (§O.B) run for
   real against the live repository is the real half.
2. A real, clean-environment onboarding exercise: a fresh checkout,
   following only `docs/getting-started.md`'s own instructions (the
   validated-in-place sections plus the harness's own confirmation),
   genuinely succeeds — recorded as real transcript evidence, not
   asserted. **Real demonstration, not a synthetic control.**
3. Unsupported commands, unauthorised network access, and attempted
   filesystem escapes are all rejected by the harness — `tests/
   test_execute_doc_example.py` (new): a command outside the allow-list
   is rejected before the sandbox is even entered; a command matching
   the allow-list but producing output that doesn't match its
   documented expected outcome (including exit code, §O.C) is reported
   as a failure, never silently passed; a deliberately broken isolation
   preflight aborts the whole run. **Synthetic negative controls.**
4. A real, accepted knowledge change (§O.E's own worktree-isolated
   `CL-CTXT-005` amendment) materially alters a documented fact and
   correctly produces a `claims_changed` finding for exactly the
   section that cites it (`vendor-digest-concept`) — **corrected,
   third corrective amendment, finding B**: this criterion previously
   and wrongly required "no finding at all" for `intermediate-
   knowledge-layer`, when that region already carries its own real,
   pre-existing `doc_candidate` finding regardless of this change
   (§O.D.0) — "no finding at all" was never achievable and was never
   the actual guarantee being tested. The real guarantee: this
   unrelated change neither suppresses, alters, nor flips
   `intermediate-knowledge-layer`'s own pre-existing `doc_candidate`
   finding to any other state — it stays exactly `doc_candidate`,
   checked explicitly before and after this scenario runs, and the
   region-by-region correctness check scopes narrowly to
   `vendor-digest-concept` alone transitioning through its own real
   lifecycle (`noop` → `claims_changed` → recompiled/republished →
   `noop` again). **Real demonstration.**
5. The correct grounded section (`vendor-digest-concept`) becomes
   stale and is subsequently recompiled/corrected and independently
   re-verified (both review dispatches) before republication — §O.E
   steps 3-5. **Real demonstration.**
6. A human edit arriving after compilation but before publication
   blocks replacement — the §O.D.3 end-to-end negative test (compile →
   review → human edit → publish refused → human edit preserved
   byte-for-byte). **Real demonstration of a deliberately constructed
   scenario** (the human edit itself is deliberately introduced, since
   the point being tested is the guard's own behaviour, not whether an
   edit happens to occur).
7. A concurrent knowledge-and-document edit (`concurrent_conflict`)
   requires explicit lead resolution, never an automatic merge either
   direction. **Synthetic negative control** (deliberately constructed
   — both the region's prose and its cited record are changed between
   two `docs maintain` runs).
8. A byte-for-byte diff of both documents, scoped to every region *not*
   involved in a given test case (including `intermediate-knowledge-
   layer`'s own untouched `doc_candidate` state throughout), is
   identical before and after every test case and the real
   demonstration above runs.
9. A duplicate composed `region:<id>` across `README.md` and `docs/
   getting-started.md` is detected and rejected by `check_doc_schema.py`
   at schema-validation time — **corrected, third corrective amendment,
   finding A**: this is `_check_cross_document_region_id_uniqueness`
   (§O.D point 4), a genuinely new check, never "already covered" by
   `_check_document_uniqueness` (which only ever checked duplicate
   *document paths*, confirmed by direct reading — a materially
   different, pre-existing check this criterion previously and wrongly
   conflated with region-id uniqueness). `L-118`'s own
   schema-slug-must-be-tested-against-a-real-separator lesson still
   applies to this new check's own slug computation
   (`doc_compiler.compute_schema_slug`), exercised here with a genuine
   two-document case for the first time.
10. Running `docs maintain` twice in a row with nothing changed between
    the runs produces zero new reconciliation-candidate manifest files
    on the second run — tested against the real, already-existing
    `intermediate-knowledge-layer` candidate (§O.D.0/§O.D.2), not a
    fabricated stand-in. **Real demonstration.**
11. Both independent review records (`docs record-review --kind
    semantic`/`--kind editorial`) are bound by hash to the exact
    published draft and evidence for every section this stage actually
    publishes — no exception for the real `CL-CTXT-005` update's own
    republish, exactly as Stage 87A's own hardening pass (§N.A)
    requires.
12. The comparator (§O.E) performs the exact same task, against the
    exact same real `CL-CTXT-005` change, on the exact same section
    (`vendor-digest-concept`), with identical pinned starting revision
    and evidence access — never a different, easier, or fabricated
    section.
13. Actual cost, elapsed time, review effort, and corrections are
    recorded in the cost/value log (§O.E) for every real compilation/
    maintenance cycle this stage actually runs — a real, filled-in
    artifact, not a template left blank — with any unavailable
    measurement (e.g. a dispatch that doesn't report token usage)
    explicitly disclosed as unavailable, never silently omitted or
    estimated and presented as measured.

### O.G Stage gate

**Mandatory stage gate** (strengthened, corrective amendment): the
gate is **maintained documentation accuracy and preserved human work**,
not successful generation or successful stale-state detection alone —
per the governing task's own explicit caution, additional
infrastructure, additional generated text, or a detector correctly
reporting `claims_changed` are none of them, by themselves, evidence
that documentation was actually kept accurate and useful. Concretely:

- Both documents genuinely pass their own governed sections' schema
  and factual-verification requirements (§O.B/§O.F.1-3).
- A real clean-environment onboarding exercise genuinely succeeds
  (§O.F.2).
- At least one real, evidence-backed knowledge change was made, was
  detected, produced a correctly re-verified and republished section,
  and reconciled cleanly afterward — not merely a synthetic fixture
  (§O.E, §O.F.4-5/10-11).
- A real human edit was genuinely preserved against a reviewed,
  ready-to-publish draft that would otherwise have overwritten it
  (§O.D.3, §O.F.6).
- A genuine concurrent conflict was reported, not silently resolved
  either direction (§O.F.7).
- Every unrelated section, across every operation above, is confirmed
  byte-identical (§O.F.8).
- The cost/value log and comparator (§O.E) exist as real, filled-in
  artifacts, not templates (§O.F.12-13).

As with Stage 87A's own gate (§D.4), this is an explicit go/no-go
judgment on demonstrated value, not an automatic pass-through from
tests alone — and, per the point above, not from successful detection
or generation alone either.

### O.H Stage 87B's own, separate DoD

Per `CLAUDE.md` §5, unchanged by this plan: Stage 87B implementation
(whenever separately authorised) requires its own retro, its own
`docs-reconstructor` drift audit, and its own independent
`release-phase-auditor` pass against the exact commit before it is
considered closed — exactly the same discipline this plan's own §D.4/
§N already applied to Stage 87A, not a lighter bar because 87B reuses
more existing machinery.

### O.I Corrective amendment summary (2026-11-05)

A code-level review of this plan (independent of the planning review
recorded at §P) found seven further findings, all corrected in place
above rather than narrated here at length:

- **A (comparator invalid)** — `## Known gotchas` doesn't exist as a
  real section; superseded by a corrected comparator targeting the
  real `vendor-digest-concept` region (§O.E).
- **B (no publication-time concurrency check)** — `publish_section`
  unconditionally overwrites; superseded by a new guard reusing
  `_apply_doc_region_edit`'s own existing re-verification pattern,
  plus a baseline-advance step after every successful publish (§O.A,
  §O.D.3).
- **C (infeasible execution harness)** — the original mirror/allow-list
  design had no actual redirection mechanism and included two
  paid-API-triggering commands a credential-less sandbox can never
  complete; superseded by a `git insteadOf`-based redirect, an offline
  `pip` install, a narrowed real-execution allow-list, and a mocked
  test for the removed paid commands (§O.C).
- **D (classification conflated three questions)** — compiled,
  schema-governed, and factually-verified were one axis; superseded
  by three independent questions and a corrected per-section table,
  newly requiring factual verification of `## After the first run`
  (§O.B).
- **E (acknowledgment mistaken for maintenance)** — `acknowledge_
  stale_grounded_region` was cited as if it demonstrated an update;
  superseded by a real, worktree-isolated, evidence-backed knowledge
  change compiled/reviewed/republished end to end (§O.E).
- **F (no identified knowledge coverage)** — proposed README additions
  had no real supporting record; superseded by an honest, searched
  conclusion that no new compiled sections are added, with the
  mandatory real demonstration anchored on the one section that
  already exists and is already evidence-backed (§O.F.1).
- **G (wrong initial-state assumption)** — both README regions were
  assumed `noop`; superseded by the real, directly-confirmed state
  (`intermediate-knowledge-layer` is `doc_candidate`, pre-existing and
  preserved throughout; only `vendor-digest-concept` is `noop`) (§O.D.0).

No change to Stage 87B's own objective, four-deliverable scope (§3 of
the governing task, reflected throughout §O), or deferred-scope list.
No Stage 87C material pulled in. No new agent, knowledge store, or
general-purpose execution framework introduced by any of the seven
corrections above.

### O.J Third corrective amendment summary (2026-11-07)

A further review of the already-READY, twice-amended plan found five
more findings, all corrected in place above:

- **A (cross-document region-id gap)** — `check_doc_schema.py::
  _check_document_uniqueness` checks duplicate document *paths* only,
  confirmed by direct reading; §O.F criterion 9 previously and wrongly
  claimed this already covered duplicate *region ids*. Superseded by a
  new `_check_cross_document_region_id_uniqueness` check and a shared
  `doc_compiler.compute_schema_slug` (§O.D point 4).
- **B (acceptance-criteria wording error)** — criterion 4 required "no
  finding at all" for `intermediate-knowledge-layer` after an unrelated
  knowledge change, impossible given its own real, pre-existing
  `doc_candidate` state (§O.D.0). Corrected to require the finding
  stays unchanged, never suppressed or altered by an unrelated change
  (§O.F criterion 4).
- **C (concurrency guard still fail-open in two ways)** — the
  guard's own `"new"`-case branch treated an unbaselined-but-existing
  region as automatically safe to overwrite, and nothing re-verified
  the live target between the initial check and the actual write.
  Superseded by a content-hash comparison for the `"new"` case, a
  write-boundary revalidation inside a simple cooperating-writer lock
  (documented limits: it protects concurrent `docs publish`/`docs
  maintain` invocations, not a human editor, which the hash re-check
  catches regardless), and explicit baseline-advance-only-on-success
  rules (§O.D point 3).
- **D (interactive/billable bootstrap conflated with deterministic
  bootstrap)** — bare `codecompass` and `codecompass --budget 0` were
  treated as interchangeable against the same candidate-bearing
  fixture, which would make bare `codecompass` non-deterministic
  inside the harness. Superseded by three distinct scenarios against
  two distinct fixtures (a new no-candidates fixture for bare
  `codecompass`; `toy-project` for `--budget 0`; a mocked test for the
  interactive-confirm/authorised-enrichment path), plus a real
  correction to `docs/getting-started.md`'s own self-contradictory
  "never asks you anything" claim (§O.B, §O.C).
- **E (knowledge-change scenario was still a placeholder)** — §O.E
  named `CL-CTXT-005` as the amendment target without identifying an
  actual, evidence-backed gap. Superseded by a concrete, independently
  verified one: `sync_vendor`'s own real clone-failure fallback
  (`decisions/0004`, already exercised by `tests/test_sync.py:
  282-293`) is genuinely true, current behaviour `CL-CTXT-005` has
  never captured — with an explicit instruction to report the
  limitation honestly, never substitute a fabricated change, if this
  specific investigation doesn't hold up once genuinely attempted
  (§O.E point 1).

No change to Stage 87B's own objective or four-deliverable scope. No
Stage 87C material pulled in. No new agent, knowledge store, or
general-purpose execution framework. This amendment authorises
implementation to proceed immediately following a READY verdict on
this corrected plan (§R below) — unlike the prior two amendments, this
governing task explicitly authorises Stage 87B implementation itself,
not planning alone.

## P. Independent planning review of the Stage 87B plan (§O)

**First round: NOT READY.** An independent reviewer, re-deriving §O's
own empirical claims directly against the real files on disk rather
than trusting its prose, found every structural/scope claim sound
(§O.A's reuse table, §O.D's two fixes against `planning/retros/
_audit-phase-87-stage-87a.md` §10's own two named observations, §O.E's
retro citation, the 87B/87C scope boundary against `decisions/0085`
§5/§6) but two blocking factual errors in §O.B/§O.C specifically,
plus one related unresolved design gap and one minor naming slip:

1. §O.B's original draft listed `## Public API surface`/`## Known
   gotchas`/`## Quick links`/`## Metadata`/`## Grounding` as if they
   were real top-level sections of `docs/getting-started.md`. They are
   not — they are literal text inside `## A real captured example`'s
   own fenced code block, illustrating a generated per-vendor
   `vendor/click/CLAUDE.md` file. The document's real structure is six
   sections, not nine.
2. §O.C's original draft named `pip install codecompass`, `codecompass
   init --scan ...`, and `codecompass sync` as the allow-list's source
   command blocks. None of the three is real: the actual PyPI
   distribution name is `codecompass-context` (not `codecompass`,
   which is the import/CLI name only — confirmed to differ
   deliberately per `README.md`'s own Quick Start); `init --scan` and
   `sync` are real CLI commands but neither appears as an executed
   command block anywhere in this document.
3. (Related, not independently blocking) the "no network" restriction
   as originally drafted had no stated mitigation for bare
   `codecompass`/`codecompass --budget 0`, which genuinely clones
   vendor source over the network per the document's own "## First
   run" step 3 — only `pip install`'s network need had a mitigation
   (a pre-populated wheel cache).
4. (Minor) §O.F named `scripts/test_check_doc_schema.py`/
   `scripts/test_execute_doc_example.py`; this project's own
   consistent convention is `tests/`, not `scripts/`, for every test
   file (confirmed: `tests/test_check_doc_schema.py` already exists
   there).

**Resolution, same pass**: §O.B rewritten to list the real six
sections and to say honestly that no section currently has a real
citable knowledge record behind it (the "compiled from knowledge"
category is empty today, not backfilled with an invented example to
avoid saying so); §O.C's allow-list corrected to the real command set
(`pip install codecompass-context`; bare `codecompass`/`codecompass
--budget 0`; `codecompass query vendors`; `codecompass --yes`/
`codecompass --budget 1.00`) and given an explicit network-isolation
resolution for the vendor-cloning command (a pre-populated, read-only
local mirror of the two real fixture vendors' upstream source,
`click`/`requests`, prepared once out of band — the same "pre-staged
content instead of a live fetch" discipline already used for `pip
install`, not a second, differently-shaped exception); §O.F's two test
paths corrected to `tests/`.

**Second round, independent re-check of the correction only** (narrow
scope, matching this project's own established practice for a single,
mechanically-verifiable fix — see §M's own identical pattern): **READY.**
A fresh dispatch, with no memory of the first round, independently
re-verified all four corrections against the real files on disk rather
than trusting §P's own account above: confirmed `docs/getting-started.md`
has exactly six real `## `-level sections, matching §O.B's corrected
list exactly; confirmed the real command blocks (`pip install
codecompass-context` at line 6; bare `codecompass`/`codecompass
--budget 0` at lines 16/34; `codecompass query vendors` at line 79;
`codecompass --yes`/`codecompass --budget 1.00` at lines 96/98), and
cross-checked the real PyPI distribution name directly against
`pyproject.toml`'s own `name = "codecompass-context"`; confirmed §O.C's
network-isolation paragraph gives a concrete, named mitigation for both
`pip install` and the vendor-cloning command, not blanket silence;
confirmed §O.F now reads `tests/test_check_doc_schema.py`/`tests/
test_execute_doc_example.py`, with the only remaining `scripts/test_*`
occurrences being §P's own historical record of what the first round's
draft said, not a live error.

**Both review rounds are now closed with no remaining blocking
finding. This Stage 87B plan is implementation-ready**, subject to the
same unchanged constraint as every other stage: Stage 87B
implementation itself requires a further, separate, explicit
authorisation before any of §O's own specification is built.

## Q. Independent planning review of the corrective amendment (2026-11-05)

**READY WITH NON-BLOCKING OBSERVATIONS.** A fresh dispatch, with no
reliance on §P's prior verdict, independently re-verified all seven
§O.I corrections directly against the real repository — reading the
actual cited functions, running `detect_grounded_region_changes`
itself, independently re-searching the real knowledge corpus, and
checking actual host tooling (`which docker podman bwrap firejail
unshare`) — rather than trusting this plan's own prose for any of
them. All seven held up exactly as described:

- **A** — confirmed `docs/getting-started.md` has no `## Known
  gotchas` section (it's inside a fenced illustration) and that
  `vendor-digest-concept` is real (`README.md:103-107`).
- **B** — confirmed `publish_section` (`doc_compiler.py:523-571`)
  unconditionally overwrites with no drift check; confirmed
  `_apply_doc_region_edit`'s own re-verification pattern
  (`knowledge_intermediate.py:627-748`) exactly matches what the new
  guard reuses; independently re-derived the five-case proceed/refuse
  mapping from `detect_grounded_region_changes` itself and confirmed
  it correct; confirmed no live-region drift check exists in `docs
  publish` today.
- **C** — confirmed `_git_clone` has no redirection knob of its own
  (necessitating the `git`-level fix); confirmed `check_budget`/
  `_call_anthropic` really can trigger a real, billed API call when
  budget is sufficient (justifying `--yes`/`--budget 1.00`'s removal);
  confirmed this host genuinely lacks docker/podman/bwrap/firejail and
  has `unshare`, independently verifying the "no simpler option
  available" claim rather than accepting it as an unexamined default.
- **D** — confirmed `## After the first run` genuinely names all five
  claimed implementation facts verbatim, and independently confirmed
  each one is real on disk (vendor digests, the root `CLAUDE.md`
  table, the Skill, the slash command, `context-graph.db`).
- **E** — confirmed `acknowledge_stale_grounded_region` never touches
  a document's own text, only the baseline — the original draft's
  citation was structurally wrong, exactly as the correction states.
- **F** — independently re-read all 31 real Claim records' full
  statements and re-ran the corpus search itself; confirmed none
  supports README install/first-step content, matching §O.F.1's own
  conclusion.
- **G** — reproduced `detect_grounded_region_changes`'s real output
  directly: `intermediate-knowledge-layer doc_candidate` /
  `readme-md-vendor-digest-concept noop`, matching §O.D.0 exactly; also
  confirmed the real, unresolved fixture manifest `20261104T081241Z-
  doc.toml` exists on disk.

Two non-blocking, narrow specification gaps were found and fixed in
this same pass: (1) §O.D.3's guard table conflated "no finding exists
for this region" with a finding whose own `.case` is literally `"new"`
— both are legitimate proceed-cases but were only partly enumerated;
fixed by naming both explicitly. (2) the newly-required `## After the
first run` factual-verification check (finding D) named *that* a check
was needed without naming *where* it lives, unlike its fully-specified
siblings in §O.C/§O.D.3; fixed by adding a concrete mechanism
(extending `tests/test_check_doc_schema.py` or a short new script) and
clarifying that `.claude/commands/discovery.md` specifically can only
be checked by its own file content, never a true runtime invocation,
since it is a Claude-Code-specific trigger, not a CLI command.

Structural checks also confirmed: no Stage 87C scope creep (no full
publication suite, no matched-baseline experiment, no MCP, no new
standing agent); `execute_doc_example.py` is explicitly not a
general-purpose command runner; the plan's own four-deliverable scope
is preserved; acceptance criteria are concrete and tied to named test
files/demonstration steps; the stage gate tests maintained accuracy and
human-edit preservation, not mere successful generation or detection.

**This corrective amendment is implementation-ready.** Stage 87B
implementation itself still requires a further, separate, explicit
authorisation — unchanged by this review.

## R. Independent planning review of the third corrective amendment (2026-11-07)

**READY WITH NON-BLOCKING OBSERVATIONS.** A fresh dispatch, with no
reliance on §P/§Q's prior verdicts, independently re-verified all five
§O.J findings directly against the real repository — reading the
actual cited functions in full, running `detect_grounded_region_
changes` and `tests/test_sync.py`'s own real fallback test directly,
and checking `examples/toy-project/`'s real dependency set — rather
than trusting this plan's own prose for any of them. All five held up
exactly as described:

- **A** — confirmed `_check_document_uniqueness` (`check_doc_schema.py:
  233-248`) tracks document paths only; confirmed
  `_check_no_duplicate_region_ids` only fires at reconciliation time
  against already-published text; confirmed the `compute_schema_slug`
  precedent (`hash_evidence`, already shared between `doc_compiler.py`
  and `cli.py`) is real.
- **B** — reproduced `intermediate-knowledge-layer doc_candidate` /
  `readme-md-vendor-digest-concept noop` directly; confirmed "no
  finding at all" was genuinely unachievable and the corrected wording
  is right.
- **C** — read `detect_grounded_region_changes` and
  `_apply_doc_region_edit` in full, confirmed the former is genuinely
  read-only and the latter's re-verification pattern is real and
  precisely as cited (after a citation-range fix, `627-748`, applied
  in this same pass); confirmed `docs publish`'s real current code has
  no drift check or lock today, so the gap and the fix are both real;
  confirmed the proposed lock is a plain mutex, not a new concurrency
  system.
- **D** — confirmed `docs/getting-started.md`'s real, live
  self-contradiction (line 19 vs. line 25); confirmed `_maybe_run_
  enrichment`'s own docstring states budget is checked before the
  confirmation prompt, matching its real code; confirmed
  `examples/toy-project/` genuinely has real, imported, unenriched
  dependencies, making the original one-fixture design genuinely
  unsafe for a no-stdin harness.
- **E** — confirmed `CL-CTXT-005`'s real current statement says
  nothing about the clone-failure fallback; confirmed `sync_vendor`'s
  real fallback behaviour and ran `tests/test_sync.py`'s own real,
  passing test for it directly — a genuine, independently-verifiable,
  currently-true gap, not a manufactured scenario.

One non-blocking, pre-existing citation imprecision was found (not one
of the five findings) — `_apply_doc_region_edit`'s own cited line
range was `627-698` in two places, when the function actually runs to
line 748 — fixed in this same pass (now `627-748` everywhere, matching
§Q's own already-correct citation).

Structural checks also confirmed: no Stage 87C scope creep; the plan's
own four-deliverable scope and deferred-scope list are unchanged; no
new agent, knowledge store, or general-purpose framework; every
renumbered cross-reference (`§O.D.0`, `§O.D` points 1-4, `§O.F`
criteria 4/9) points to the content it claims to.

**This third corrective amendment is implementation-ready.** Per the
governing task's own explicit authorisation, Stage 87B implementation
now proceeds directly.

## S. Stage 87C plan — complete knowledge-compiled documentation proof

**Authorisation boundary, restated**: this section is a plan only.
Nothing in it is implemented by this authorisation. Stage 87C begins
implementation only once separately, explicitly authorised, following
this plan's own independent planning review reaching `READY`.

**Objective** (`decisions/0085` §5/§6, unchanged by this plan):
demonstrate that CodeCompass can produce and maintain a coherent,
useful, substantially knowledge-grounded documentation set from
reconciled canonical knowledge, using deterministic generation and
constrained model inference where appropriate, while preserving
human-authored material and independently verifying factual accuracy.
Not maximising generated prose or schema count.

### S.1 Actual current-state assessment (verified directly this session, not assumed from the roadmap)

The real documentation tree, read in full or substantially this
session, against `decisions/0085` §5's minimum-suite table:

| Required document | Real file(s) | Current state |
|---|---|---|
| README | `README.md` (107 lines) | **Two** grounded regions exist today, verified by direct inspection, not one: `region:readme-md-vendor-digest-concept` (`CL-CTXT-005`) is the Stage 87B-era, schema-compiled section this plan's own prior draft already knew about; `region:intermediate-knowledge-layer` (`CL-KNOW-001`) is a second, **pre-existing, unrelated** grounded region from Phase 81's own direct document-grounding mechanism (`knowledge_intermediate.py`'s grounded-document reconciliation, predating Stage 87's schema/compiler pipeline entirely, never routed through `doc_compiler.publish_section`/`docs compile`/`docs publish`). Only the first is this plan's own concern. The rest of README — problem statement, capability list, installation — is human-authored prose, not schema-governed at all. |
| Getting Started | `docs/getting-started.md` | Schema-governed (`docs/getting-started.md.schema.yaml`), **five** sections total, corrected from this plan's own prior, inaccurate "5 of 6" count (verified by direct re-read of the schema file): `install`, `first-run`, and `a-real-captured-example` each declare `requires_tested_example: true` (deterministically verified by `scripts/execute_doc_example.py`'s real sandboxed harness) — **three** sections, not five. `proceeding-past-the-budget-cap` has no `requires_tested_example` field at all — verified instead by a mocked CLI test (`test_bare_bootstrap_sufficient_budget_with_interactive_confirm_reaches_enrichment`), since a real `--budget`-exceeding paid API call cannot run inside a credential-less sandbox. `after-the-first-run` also has no `requires_tested_example` field — verified instead by a direct filesystem/content check against this real repository (`test_after_the_first_run_claims_match_the_real_repository`). All five are schema-*listed* for `check_doc_schema.py`'s own structural validation; **none is knowledge-compiled, and none has ever been run through `docs compile`/`docs publish` at all** — confirmed directly: `docs/getting-started.md` contains zero `codecompass-grounded-by` markers, and no `planning/retros/phase-87-pending-review/getting-started-md/` directory exists. This is correct, not a gap: `decisions/0085` requires "a tested, practical first-use tutorial," which direct execution/repository-fact verification satisfies more directly than a Claim-grounded citation would, for prose with no citable knowledge record behind it in the first place. No further knowledge-compilation needed here; this document is essentially done. |
| Concepts | `docs/concepts/{adapter,context,digest,knowledge-model,knowledge-placement-policy,protocol-and-capability,vendor-and-ecosystem}.md` (7 files, 272 lines total) | **Read in full this session.** All seven are accurate, substantive, human-authored prose — not schema-governed, no citation markers, zero `{{cite:...}}` or `codecompass-grounded-by` markers anywhere in `docs/concepts/`. Critically, several closely paraphrase real, existing Claims almost verbatim: `context.md`'s five-sense enumeration mirrors `CL-CTXT-001` near word-for-word; `adapter.md`/`vendor-and-ecosystem.md` mirror `CL-ADPT-001`/`CL-ADPT-005`/`CL-ADPT-007`. `decisions/0085`'s own stated gap — "a new page explicitly covering epistemic distinctions and the reconciliation loop" — is **already substantially closed** by existing prose: `knowledge-model.md`'s own "INTENDED / OBSERVED / VERIFIED / CONTESTED" section (citing `decisions/0080`/`0081`) and its "intermediate projection and the reconciliation loop" section (cross-referencing `docs/workflows/knowledge-reconciliation-loop.md`). This is a real, verified correction to `decisions/0085`'s own framing, not an assumption carried forward from it: the content gap it named no longer exists, confirmed by reading the file directly, not by trusting the roadmap's own age. What remains open is narrower and different: this accurate prose is not knowledge-compiled (no grounding, no automatic maintenance against a future Claim change) and is backed by only **one** formal Claim (`CL-KNOW-001`) for the reconciliation-loop/workflow material specifically — everything else in `knowledge-model.md` beyond the record-kind table is asserted without a citable record at all. **Of these seven, exactly four are this plan's own compilation candidates** (`context.md`, `adapter.md`, `vendor-and-ecosystem.md`, `knowledge-model.md`'s record-kind table) — see §S.2 for why `protocol-and-capability.md` and `digest.md`/`knowledge-placement-policy.md` are deliberately excluded from this stage's own compiled scope, corrected from this plan's own prior draft, which inconsistently listed `protocol-and-capability.md` as a compiled target in §S.2 while §S.3 had already found its own backing Claims insufficient and §S.5 had already sequenced only four pages. |
| Architecture | `docs/architecture/{overview,components,data-and-control-flow,documentation-compilation-pipeline}.md` | Read substantially this session. Dense, accurate, well-maintained human-authored prose (e.g. `overview.md`'s "Foundational design choices," a "Known footguns" section citing real learnings like `L-109`/`L-121`). No Claims back this content at all — it describes current implementation structure directly, which is exactly what `decisions/0085` calls "major components, responsibilities, data flows" and does not itself require knowledge-compilation for. |
| Reference | `docs/reference/{cli,configuration,protocols,symbol-extraction}.md` | Hand-maintained prose, not generated from the real Typer command tree (`cli.md`'s own structure manually mirrors `cli.py`'s commands). `decisions/0085` names deterministic generation here as "this phase's own improvement opportunity, not assumed solved" — confirmed still open: no generator exists anywhere in `scripts/` or `src/` that reads `app.registered_commands`/`typer.main.get_command` and emits this file. |
| Contributor Guide | `CONTRIBUTING.md` (root, 266 lines) + `docs/development/{contributing,testing}.md` | Explicitly, deliberately out of clean-room/knowledge-compilation scope — `docs/development/contributing.md`'s own first line: "the self-governing process document this reconstruction was correctly never shown... so it is left untouched." Process/licensing/CLA content; not a knowledge-compilation candidate by design, confirmed still correct. |

**Honest summary**: Stage 87B delivered exactly what it claimed — one
compiled README section (plus one unrelated, pre-existing Phase-81
grounded region in the same file), a schema-governed but not
knowledge-compiled Getting Started (five sections, three execution-
verified, two verified by other direct means, zero published through
the compiler at all). Stage 87C's real, verified opportunity is
narrower than a naive reading of `decisions/0085` §5 would suggest:
**Concepts** is the one document category with both (a) a genuine,
current absence of knowledge-compilation and (b) existing Claims that
already substantiate most of its content — the highest-value,
lowest-risk target, bounded to exactly four of its seven pages (see
§S.2). Architecture and Reference have no compilation gap of the kind
Concepts has (no backing Claims exist or are needed); their own real
gap is either none (Architecture) or a deterministic-generation gap
unrelated to knowledge-compilation (Reference).

**Final governed-document/region count this plan targets** (stated
explicitly, not left implicit, since an earlier draft of this section
left this arithmetic inconsistent): **2 schema files exist today**
(`README.md.schema.yaml`, `docs/getting-started.md.schema.yaml`); this
plan proposes **4 new** schema files, one per compiled Concepts page
— **6 schema-governed documents in total**, not "five," the stray
figure an earlier draft used in §S.5. Of these, **grounded-region-
marker-published** sections (the actual knowledge-compiled output
`doc_compiler.publish_section` writes) number **1 today** (README's
`readme-md-vendor-digest-concept`) and **5 after this stage**
(+1 per new Concepts page, one section each, per §S.2's own one-
section-per-page scope) — across **5 documents** (README plus the
four compiled Concepts pages), not 6, since Getting Started's own five
schema-listed sections are deliberately never published through this
mechanism at all (see the table above).

### S.2 Document/section ownership and generation matrix

Classifying every section of the minimum suite into the four
categories the governing task names — not generating anything
unsupported merely to raise a coverage number:

**1. Knowledge-compiled** (generated from accepted canonical records):
- README's existing `vendor-digest-concept` section (`CL-CTXT-005`) — unchanged, already done.
- New: `docs/concepts/context.md` → `CL-CTXT-001` (the five-sense enumeration already mirrors it almost exactly — converting this is the lowest-risk, highest-confidence first real section).
- New: `docs/concepts/adapter.md` → `CL-ADPT-001`, `CL-ADPT-002`, `CL-ADPT-007`, **and `CL-ADPT-005`** (adapter definition, two-strategy design, fuzzy-boundary honesty, and — confirmed by direct reading of the page's own existing prose, not assumed — "exactly one adapter class exists per Ecosystem enum member, selected by a single closed dispatch table," which is a direct instance of `CL-ADPT-005`'s own ecosystem/vendor/adapter relationship, not merely adjacent to it).
- New: `docs/concepts/vendor-and-ecosystem.md` → `CL-ADPT-005` (ecosystem/vendor/adapter distinction — this page's own entire subject), `CL-ADPT-004` ("connector" is not a real concept — a genuinely useful negative claim for a concepts page to state plainly).

**`CL-ADPT-005` is a real, shared dependency of both pages above** —
confirmed by direct reading, not manufactured for §S.6's own
incremental-change proof below. This is the one genuine cross-document
Claim dependency this plan's own compiled scope produces.
- New: `docs/concepts/knowledge-model.md`'s record-kind table and Provenance section → `CL-EVID-001`, `002`, `004`, `005`, `006`, `007`, `010`, `012`, `013` (the `status: supported` subset of the Observation/Evidence/Claim/Derivation/Decision/Requirement/Invariant/Provenance claim cluster — **excluding** `CL-EVID-003`/`008`/`009`, all `status: superseded`, and `CL-EVID-011`, a different topic — maps almost one-to-one onto this page's existing structure; see §S.3 for the authoritative per-Claim readiness list this section's own compilation must use).

**Exactly four pages, corrected from an earlier, inconsistent draft**:
this plan's own §S.3 already found `protocol-and-capability.md`'s
backing Claims (`CL-ADPT-003`/`006`/`010`/`011`) insufficiently
granular for compilation in this stage ("not yet backed by a citable
Claim at the needed granularity," option (b) chosen: leave it human-
authored-and-validated-in-place) — an earlier draft of this list
nonetheless named it as a fifth compiled target, while §S.5's own
implementation sequence correctly sequenced only the four pages above.
That inconsistency is resolved here in §S.3's favour: `protocol-and-
capability.md` moves to category 3 below, unchanged for this stage.

**2. Deterministically generated** (derived directly from CLI, code, schemas, tests, or other mechanical evidence):
- Getting Started's five sections, **corrected from a remaining stale
  reference in this bullet** (the real schema has five sections total:
  three — `install`, `first-run`, `a-real-captured-example` —
  `requires_tested_example: true` and execution-harness-verified by
  `scripts/execute_doc_example.py`; the other two —
  `proceeding-past-the-budget-cap`, `after-the-first-run` — have no
  such field and are verified instead by two specifically-named other
  tests, per §S.1's own already-corrected table) — unchanged, already
  done.
- New opportunity, not built by this plan's own minimum scope but named as a real option: a `docs/reference/cli.md` generator reading the live `app` object's `registered_commands`/`registered_groups` (Typer's own introspection) and each command's own docstring/options, emitting a mechanically-verified-current reference page. Named in §S.9 as an explicit non-goal for this stage's own minimum scope (real, valuable, but a second, separable piece of infrastructure — see §S.8) with a path for a future phase to pick up, not abandoned.

**3. Human-authored and validated in place** (retained, not regenerated):
- All of `docs/architecture/*.md` — accurate, dense, well-maintained; converting to AI-composed knowledge-compiled prose would risk exactly the register/density loss the clean-room writing contract's own "never resembles an audit report" constraint exists to catch, for no corresponding accuracy gain (no competing Claim exists to ground it against).
- `CONTRIBUTING.md`/`docs/development/{contributing,testing}.md` — explicitly out of scope by design, unchanged.
- README's problem-statement/capability-list/installation prose — editorial/marketing judgment a Claim cannot substantiate ("this is valuable") stays human-authored; installation itself is already execution-verified via the existing `execute_doc_example.py` harness pattern (reused, not rebuilt).
- `docs/concepts/digest.md`/`knowledge-placement-policy.md` — read this session; both are accurate and specific to this one repository's own placement rules and category/mapping content, with no corresponding formal Claim corpus to ground against yet (see §S.3) — retained as-is for this stage; a future enrichment pass (§S.3's own backlog note) could change this later. (Corrected by this amendment: an earlier draft misattributed a "hard-coded to this repository" quote to this page's own text — that exact phrase actually appears in `src/codecompass/knowledge_intermediate.py`'s own docstring, describing `scripts/check_knowledge_base.py`'s module boundary, an unrelated statement about a different artifact entirely. Removed; the substantive point above does not depend on it.)
- `docs/concepts/protocol-and-capability.md` — its own backing Claims (`CL-ADPT-003`/`006`/`010`/`011`) are real and `status: supported`, but §S.3 found them insufficiently granular for a clean, single-section compile at this stage without a bounded `context-researcher` pass first (deferred, §S.3 option (b)) — retained as-is for this stage, named explicitly here rather than silently included in or excluded from either list.

**4. Unsupported or knowledge-gap-blocked** (not eligible for compilation until evidence or accepted intent exists):
- None identified in the minimum suite itself. Every section examined either already has a backing Claim, is correctly deterministic/human-authored by design, or (knowledge-model.md's non-table prose, protocol-and-capability.md's thinner corners) needs a small, named knowledge-enrichment pass before compilation — tracked in §S.3, not silently compiled around.

### S.3 Knowledge and evidence prerequisites

**Mandatory compilation-readiness preflight, added by this amendment**
— `status: supported` alone does not establish that a Claim actually
passes the compiler's own evidence-currency requirements; this plan's
earlier draft asserted the Claims below are "sufficient as-is" from a
direct read of their own YAML, without separately running the real
currency/gap mechanism the compiler itself uses at compile time. Before
writing any of the four new schema files for real, Stage 87C
implementation must run this preflight for every one of the four
planned schemas' own `required_knowledge` lists, reusing existing code
only, never a new check:

1. **Resolve** each planned section's actual required record ids via
   `doc_compiler.resolve_section_ids` (or by simply listing them, since
   they are already fixed ids here, not `discover:` queries).
2. **Check status and evidence currency** for every one of them through
   `doc_compiler.find_section_gaps` (which itself calls `knowledge_api.
   get()` for each id and reads its `ConsistencyEnvelope.status` —
   `"current"`/`"stale"`/`"unconfirmed"` — directly; no second,
   independently-computed currency check) against each page's own
   proposed `min_claim_status`/`allow_unconfirmed_scopes` schema
   fields.
3. **Confirm the evidence-packet budget**: `doc_compiler.
   resolve_section_packet`'s own real serialized-size check against
   each schema's proposed `max_evidence_chars` — a required record
   whose hydrated content would exceed the budget is a `DocCompilerError`
   at compile time, never silently truncated; the preflight surfaces
   this before, not during, implementation.
4. **Identify** any `stale_or_unconfirmed_evidence`, `below_min_claim_
   status`, `contradiction`, or `unresolved_required_knowledge` gap
   `find_section_gaps` reports for any of the four schemas' own ids —
   reported honestly, not compiled around, exactly as `doc_compiler.
   compile_document` itself already refuses to do.
5. **Record any use of `allow_unconfirmed_scopes: true`** with a
   concrete, independently reviewed justification — reusing
   `README.md.schema.yaml`'s own existing precedent and justification
   comment for `CL-CTXT-005` (no `oracle-contract.yaml` applies to
   `codecompass-domain`, so `knowledge_api`'s currency check honestly
   reports `"unconfirmed"` rather than a false `"current"` or a
   misleading `"stale"`) as the template for what a concrete
   justification looks like — a bare `true` with no comment is not
   acceptable for any of the four new schemas either.
6. **Never weaken evidence requirements merely to obtain a successful
   compilation** — a genuine gap found by this preflight for any of
   the **fifteen** Claims below (`CL-CTXT-001` [1] +
   `CL-ADPT-001/002/004/005/007` [5] + the nine `CL-EVID-*` ids [9] —
   corrected from an earlier draft's own "nine," which only counted
   the `CL-EVID-*` sub-cluster and omitted the other six — the same
   species of stale-count error this amendment's own Finding C fixed
   elsewhere) is resolved the same way any other knowledge gap is
   (§S.3's own evidence → candidate → reconciliation workflow, or
   explicitly deferring that specific page/section), never by
   lowering `min_claim_status` or adding an unjustified
   `allow_unconfirmed_scopes: true` to make a failing preflight pass.

**Preflight actually run this session, not merely specified** — real
results, confirming the preflight surfaces genuine, actionable
findings rather than a hypothetical exercise: all fifteen Claims
report `consistency.status == "unconfirmed"` (`codecompass-domain` has
no `oracle-contract.yaml` at all — every one of the four new schemas,
not only one, needs `allow_unconfirmed_scopes: true` with the concrete
justification point 5 above requires, not just `context.md`'s); no
`unresolved_required_knowledge`, `below_min_claim_status`, or
`contradiction` gap for any of the fifteen; and a genuine, measured
budget finding: `knowledge-model.md`'s own nine-Claim `CL-EVID-*`
cluster serializes to **18,552 real characters** — roughly 4.6× the
only existing `max_evidence_chars` precedent in this repository
(`README.md.schema.yaml`'s `4000`, for one Claim). **This page's own
schema must set `max_evidence_chars` to at least ~20,000**, stated
here explicitly rather than left for an implementer to discover via a
`DocCompilerError` mid-compile — the preflight's own stated purpose
(surface this before, not during, implementation) only holds if the
plan itself states the number the preflight actually found, not merely
that a preflight exists.

This preflight is a **read-only verification step**, not new pipeline
code — every function it calls already exists and is already exercised
by `docs compile` itself; running it *before* writing the schema files
only moves the same check earlier, so a currency problem is a planning-
time finding, not a surprise discovered mid-implementation.

Minimum knowledge-enrichment work necessary to make the compiled-
Concepts scope above meaningful, assessed claim-by-claim, not assumed
sufficient — **subject to the preflight above actually confirming
each one before implementation, not merely asserted from a direct
YAML read as this list originally was**:

- `CL-CTXT-001`, `CL-ADPT-001/002/004/005/007`, `CL-EVID-001/002/004/005/006/007/010/012/013` — **sufficient as-is**, `status: supported`, read and confirmed accurate against current `src/` this session. No new research needed for the sections named in §S.2's "knowledge-compiled" list.
- `knowledge-model.md`'s "Invariant is not a seventh record kind" closing section and `protocol-and-capability.md`'s thinner material — **not yet backed by a citable Claim** at the needed granularity. Two options, decided at Stage 87C implementation time rather than presupposed here: (a) a bounded `context-researcher` dispatch produces one or two new Claims closing this gap before compilation is attempted for that specific subsection, following the existing evidence → candidate → reconciliation workflow unchanged; or (b) that specific subsection is left human-authored-and-validated-in-place for this stage, with the gap named explicitly rather than compiled around. Preference: (b) for Stage 87C's own minimum scope — new Claim research is a real cost or Stage 87B's own schema-restraint did; (a) is the natural next step for a later maintenance pass, not a Stage 87C blocker.
- `docs/workflows/knowledge-reconciliation-loop.md`'s own mechanics are backed by exactly one Claim (`CL-KNOW-001`) for the entire reconciliation loop — thin, but accurate and sufficient for compiling `knowledge-model.md`'s one paragraph that cross-references it (the paragraph itself makes no claim beyond "see this other file for the mechanics," which `CL-KNOW-001` supports).
- `EV-CTXT-021` (filed this session, Stage 87B's own post-closeout hardening pass, `L-123`) remains outstanding, uncited by any Claim — its own reconciliation (amend `CL-CTXT-005` or explicitly decline) is a real prerequisite only if Stage 87C recompiles the `vendor-digest-concept` README section; it is not a blocker for any new Concepts section named above, none of which cite `CL-CTXT-005`.
- No new knowledge-record kind, schema field, or competing knowledge store is proposed or needed — every prerequisite above is satisfied through the existing evidence → candidate → reconciliation workflow (`decisions/0073`), reused unchanged.

### S.4 Proposed architecture — reused components, one real addition

**Reused, unchanged**: the full Stage 87A/87B pipeline —
`doc_compiler.py` (resolution/hydration/gap-detection/citation-scope-
checking/publish/maintain, including this session's own hardening),
`scripts/compile_doc_section.py` (clean-room composition adapter),
`scripts/check_doc_schema.py` (schema validation, cross-document
region-id uniqueness), `knowledge_intermediate.py`'s five-state
grounded-region reconciliation, the `_doc_publish_lock` concurrency
guard, `scripts/execute_doc_example.py` (the real sandboxed example-
execution harness, Stage 87B). Stage 87C adds **zero** new modules to
this list — every mechanism a new Concepts section needs already
exists and was exercised for real by Stage 87B's own demonstration.

**One real addition, narrowly scoped**: exactly **four** new per-
document schema files, one per compiled Concepts page
(`docs/concepts/context.md.schema.yaml`, `adapter.md.schema.yaml`,
`vendor-and-ecosystem.md.schema.yaml`, `knowledge-model.md.schema.yaml`
— matching §S.2's own four-page list, not five) — the same
`*.schema.yaml` mechanism README/Getting Started already use, not a
new schema format or a new validation path. `check_doc_schema.py`
already discovers every `*.schema.yaml` under the project root
(`scripts/check_doc_schema.py::_discover_schema_files`) and
`docs_maintain` already reconciles every schema-governed document in
one call — adding more schema files is pure configuration, not new
code. This brings the project to **6 schema-governed documents total**
(2 existing + 4 new), not "five schemas," an arithmetic slip an
earlier draft of this plan made in §S.5.

**Cross-document consistency** (a real, named requirement this plan
must address, not assume free): a term defined once (e.g. "adapter" in
`adapter.md`) and used again in another compiled section (e.g.
`vendor-and-ecosystem.md`'s own cross-reference to it) must not drift
into a second, inconsistent definition. Reused mechanism, not new:
each section's own schema already names its `required_knowledge` ids
explicitly, so two sections citing the same Claim (e.g. both `adapter.
md` and `vendor-and-ecosystem.md` citing `CL-ADPT-005`) are
structurally grounded in the identical source of truth — true
consistency comes from both compiling against one shared Claim, not
from a new cross-document consistency checker. A genuinely new
cross-document check is **not** proposed: `check_doc_schema.py`'s
existing cross-document region-id-uniqueness check (Stage 87B) already
runs project-wide across every `*.schema.yaml`; extending it to flag
two different sections asserting incompatible facts about the *same*
Claim id would require semantic comparison this plan does not propose
building — flagged honestly as unaddressed rather than silently
assumed solved (see §S.9).

### S.4a Existing-document migration procedure (new subsection, added by this amendment)

**The real risk, confirmed by direct inspection, not assumed**: none
of the four target Concepts pages carry any `codecompass-grounded-by`
marker today (confirmed: zero matches across `docs/concepts/`).
`doc_compiler.publish_section` **replaces** an existing marker-
delimited region by its own `region:<id>` identity, but **appends** a
brand-new region to the end of the file when no matching marker exists
yet. Naively running `docs compile` → `docs publish` against a
Concepts page with no marker, for a section whose schema happens to
cover the same ground as that page's own existing prose, would
therefore not replace that prose at all — it would append a second,
compiler-generated explanation of the same concept underneath the
original, untouched human-authored paragraph, duplicating content
rather than governing it.

**Determination**: the existing mechanism *can* perform this safely,
without any new code, provided migration follows a specific sequence
that uses the "new"-region and "noop"-region branches of `decide_
publish_safety` exactly as already built — but the sequence is
non-obvious enough that it must be specified explicitly as its own
procedure, not left to an implementer's own improvisation. One
optional, narrow convenience addition is named at the end (not
required for safety).

**Procedure**, per target page/section, each step its own reviewed
action, never batched silently into the next:

1. **Identify the exact boundary.** The lead reads the target page and
   names the precise span of existing prose (by heading, or by exact
   line range) that the proposed section is meant to govern —
   recorded in the schema's own section id and, informally, in the
   implementation commit's own message. For `context.md`, this is the
   entire five-sense enumeration (currently the page's whole body);
   for `knowledge-model.md`, it is specifically the record-kind table
   plus the Provenance section, **not** the whole file (the page's
   other sections — INTENDED/OBSERVED/VERIFIED/CONTESTED, the
   reconciliation-loop cross-reference, the Invariant closing note —
   stay human-authored-and-validated-in-place per §S.2/§S.3, outside
   any governed boundary).
2. **Compute the region id in advance.** `doc_compiler.compute_schema_
   slug(schema_path)` + the section's own id, exactly as `docs publish`
   will later construct it — the manually-inserted marker below must
   use this exact id, or the later real publish would treat it as a
   second, different region instead of replacing it.
3. **Wrap the identified span with an explicit marker, as its own
   reviewed edit** — `<!-- codecompass-grounded-by: region:<id> -->`
   / `<!-- /codecompass-grounded-by -->`, with an empty cited-id list
   (the original hand-written prose cites no formal record; the first
   real publish, step 6 below, naturally rewrites this header with the
   real `record_ids` anyway, since `publish_section` always rewrites
   the whole header it replaces).
4. **Establish this existing prose as the region's own baseline** —
   `docs maintain` (`knowledge_intermediate.establish_new_region_
   baselines`, already-existing code, the same path every brand-new
   region already takes) run immediately after step 3, in the same or
   the very next commit. This is the step that makes the rest of this
   procedure safe: the region is no longer "new and unbaselined" (where
   `decide_publish_safety` would correctly refuse any non-byte-
   identical replacement) — it is now a **properly baselined, `noop`**
   region, whose existing, human-authored text is the known-good state
   a future compiled draft will be compared against, exactly like any
   other already-governed region in this project.
5. **Compile and review as normal, with one bounded addition to the
   existing editorial-quality review** (never a new, third reviewer
   role — reusing the same bounded-addition convention §C step 7's
   own "question 3" already established): the editorial reviewer is
   also shown the original prose this draft is replacing and must
   explicitly confirm no factual regression (a true fact the original
   stated is not lost or contradicted), no structural regression (an
   organisation a reader relied on is not broken), and no editorial
   regression (the new prose does not read as lower quality than what
   it replaces). Any "no" to any of these is an ordinary failing
   editorial verdict — no new verdict category.
6. **Publish as normal.** Because step 4 already baselined the region,
   `detect_grounded_region_changes` reports `noop` (nothing has
   drifted since that baseline), and `decide_publish_safety`'s
   existing `noop` branch permits the write unconditionally — this
   *is* the controlled, approved replacement Part 4's own requirement
   asks for, with the approval having happened at step 5's review,
   backed by step 4's baseline. If anything touches the same region
   between steps 4 and 6 (a human edit, a second migration attempt),
   `detect_grounded_region_changes` correctly reclassifies it
   `doc_candidate` or `concurrent_conflict` first, and the existing,
   already-hardened refusal logic blocks the write automatically —
   satisfying point 8's "refuse ambiguous or conflicting replacements"
   with zero new code.
7. **Verify.** A direct diff confirms every byte of the page outside
   the governed span is unchanged (the same standard Stage 87B's own
   "preserves unrelated regions" tests already establish); a
   subsequent `docs maintain` run reconciles to `noop`; no duplicate
   explanation of the same concept exists anywhere in the page.

**Preservation of material outside the boundary** (point 3) needs no
new mechanism at all — `publish_section`'s existing text-splicing
already only ever touches its own marker-delimited span, proven
directly by Stage 87B's own existing regression tests.

**One optional, narrow convenience addition, not required for
safety**: a thin `docs adopt-existing <schema_path> <section_id>
--span START:END` wrapper performing steps 2-4 together in one
reviewed operation, for operator ergonomics only (it calls existing
functions in sequence; it introduces no new safety logic). Named here
as a real option for 87C implementation to add if the manual
three-step sequence proves error-prone in practice — not a
precondition for this plan's own acceptance criteria.

### S.5 Concrete implementation sequence

1. Reconcile the two outstanding `L-122`/`L-124` backlog items and the
   `L-123` knowledge-reconciliation hand-off (all filed this session)
   before or alongside Stage 87C's own work, not folded silently into
   it — each is independently dispositioned already (§ see this
   session's commits).
2. **Run §S.3's mandatory compilation-readiness preflight** against all
   four planned schemas' own `required_knowledge` ids, before writing
   any schema file for real — a planning-time check, added by this
   amendment, that must pass (or have every finding explicitly
   resolved, never compiled around) before step 3 begins.
3. Write `docs/concepts/context.md.schema.yaml` (one section, citing
   `CL-CTXT-001`) — the lowest-risk first real compile, given the
   existing prose already near-verbatim matches the Claim. **Run
   §S.4a's migration procedure steps 1-4 first** (identify the
   boundary, compute the region id, insert the marker, establish the
   existing prose as the region's own baseline) — `context.md` has
   real, valuable existing prose this step must govern, not overwrite
   blind.
4. Run `docs compile` → both independent reviews (semantic-support,
   editorial-quality **plus §S.4a step 5's own bounded
   regression-against-original-prose addition**) → `docs
   record-review` → `docs publish`, exactly Stage 87B's own real
   workflow, reused unchanged, now safely replacing the baselined
   original prose per §S.4a step 6. If either review fails, iterate
   the schema's own `tone`/`depth`/audience fields (not the pipeline
   code) — Stage 87A's own three-round writing-contract hardening is
   the precedent for how many iterations is normal.
5. Repeat for `adapter.md`, `vendor-and-ecosystem.md`,
   `knowledge-model.md`'s record-kind table, in that order (increasing
   structural complexity: single-claim → multi-claim → table-shaped
   content) — **§S.4a's migration procedure runs first for each page**,
   same as step 3 above; each compile independently reviewed, never
   batched into one unreviewed pass.
6. Run `docs maintain` across the full, now-**six**-schema project
   (corrected from an earlier draft's "five" — 2 existing + 4 new, per
   §S.1/§S.4) after all four are published, confirming project-wide
   duplicate-region-id and five-state reconciliation still hold with
   more schemas in play than Stage 87B ever exercised at once — a real
   scale check Stage 87B's own two-document demonstration could not
   provide.
7. Only then: the incremental-change proof (§S.6) and the comparator
   experiment (§S.7), in either order — independent of each other.
8. Final `docs-reconstructor` drift audit + `release-phase-auditor`
   pass against the complete Stage 87C diff, mirroring every prior
   stage's own closeout discipline exactly.

### S.6 Incremental-change proof (one real, multi-section-crossing change)

**Corrected by this amendment**: the prior draft's candidate (a legacy
`vendor.toml` `depth` key) was real and evidenced, but its own second
affected region, `docs/reference/configuration.md`, is **not**
scheduled for compilation anywhere in this plan's own §S.2 — it
depends on a page that stays human-authored-and-validated-in-place,
so it could never actually demonstrate maintenance propagating across
two *compiled, governed* regions, only one compiled region plus one
page that was never going to be touched by `docs maintain` in the
first place. That candidate is withdrawn.

**Replacement candidate, verified against the real, actually-compiled
dependency graph first, not chosen then rationalised**: §S.2's own
correction above establishes that `CL-ADPT-005` is a real, already-
existing shared dependency of **two sections this plan actually
compiles** — `adapter.md`'s section (citing it for "one adapter class
per Ecosystem, selected by a single closed dispatch table") and
`vendor-and-ecosystem.md`'s section (citing it as that page's own
entire subject). An amendment to `CL-ADPT-005` itself is therefore
guaranteed, structurally, to affect both compiled regions — not
"potentially," the prior draft's own hedge.

**The real, evidenced fact to add, confirmed directly this session**:
`CL-ADPT-005` describes the ecosystem/vendor/adapter relationship and
`get_adapter`'s own closed dispatch table, but never states what
happens when a `vendor.toml` entry names an ecosystem string outside
the closed 4-member enum. `src/codecompass/config.py::_require_enum`
(lines 62-71) fails closed at config-*load* time — before `get_adapter`
is ever reached — with a `ConfigError` naming every valid ecosystem
value, confirmed by the real, already-passing
`tests/test_config.py::test_invalid_ecosystem_raises_config_error`
(asserts `ConfigError` matching `"invalid ecosystem 'deno'"`). This is
a genuine, currently-true, currently-untested-by-any-Claim fact about
the *boundary* of the ecosystem/vendor/adapter relationship `CL-ADPT-005`
otherwise describes in detail — relevant to both pages: `adapter.md`'s
own dispatch-table discussion (the table's completeness is only safe
*because* invalid values are rejected upstream, at config load, never
reaching the dispatch itself) and `vendor-and-ecosystem.md`'s own
`vendor.toml` field-validation discussion.

**Demonstration sequence** (mirrors Stage 87B's own real demonstration
exactly, reused procedure, now genuinely crossing two compiled, live
regions rather than one compiled region and one untouched page):

1. **Evidence** the real fact (source + the already-passing test
   named above) as a new `EV-ADPT-0XX` record, same convention as
   `EV-CTXT-021` this session.
2. **Propose** the `CL-ADPT-005` amendment through the ordinary
   evidence → candidate → reconciliation workflow (`decisions/0073`)
   — never silently merged, same discipline `EV-CTXT-021`/`L-123`
   established this session.
3. **Controlled acceptance, with its own explicit branch — corrected by
   this amendment** (the prior draft let the amendment be "declined,
   honestly reported either way," then unconditionally required steps
   4-8's own `claims_changed` demonstration regardless — a direct
   contradiction, since nothing to detect exists if nothing was
   accepted): a human/lead reconciliation decision either **(a)
   accepts** the amendment, in which case steps 4-8 below proceed
   exactly as written against real production knowledge; or **(b)
   declines** it — acceptable on its own evidential merits, never
   forced — in which case Stage 87C's own mandatory multi-region
   maintenance proof is **not excused**, and proceeds by one of two
   named paths, decided and recorded explicitly at implementation
   time, never left ambiguous: (i) a **different**, evidence-backed
   Claim change, re-verified at that point to genuinely affect two
   compiled regions the same way `CL-ADPT-005` was verified to here; or
   (ii) an **explicitly authorised, isolated demonstration**, run in a
   disposable `git worktree` exactly as Stage 87B's own real knowledge-
   change demonstration was (production `planning/knowledge/` never
   touched), with its narrower evidential basis — a demonstration, not
   a production change — stated plainly in the retro, never silently
   presented as equivalent to path (a) or (i).
4. **`docs maintain`** (run across the full six-schema project —
   clarified by this amendment: if path (b)(ii) applies, **every** step
   from here through step 8 runs inside that same disposable worktree,
   not only the knowledge change's own landing; "the full six-schema
   project" means that worktree's own copy in that case, exactly as
   Stage 87B's own real demonstration ran its entire compile→review→
   publish→reconcile cycle inside one isolated worktree, never only
   its first step), once the knowledge change from step 3 has actually
   landed (production or isolated-worktree, per whichever branch above
   applies) **and** the step-6 seeded human edit below has already
   been made, must report:
   `claims_changed` for **both** `adapter.md`'s and `vendor-and-
   ecosystem.md`'s own regions; `doc_candidate` for whichever region
   step 6 deliberately edits (`context.md`, fixed here rather than left
   as either-or, as the simpler, single-Claim page); `noop` for
   `knowledge-model.md`'s own untouched region and for README's
   `vendor-digest-concept`; and the **pre-existing** README `region:
   intermediate-knowledge-layer` candidate (confirmed, by direct
   `detect_grounded_region_changes` call this session, to already be
   `doc_candidate` in real production state right now, from Phase 81's
   own unrelated history) reported exactly as it already was —
   untouched, unresolved, unacknowledged by anything in this
   demonstration. Confirmed by reading `docs maintain`'s own structured
   output directly, not inferred.
5. **Recompile, independently re-review, and re-publish only the two
   genuinely affected regions** (`adapter.md`, `vendor-and-ecosystem.
   md`) — two separate `docs compile`/`docs record-review`/`docs
   publish` cycles, each independently reviewed (semantic-support,
   editorial-quality), never a single unreviewed batch update across
   both, and **never** touching `context.md`'s own `doc_candidate`
   region — a `doc_candidate` is never auto-regenerated, by this
   project's own standing rule, reused unchanged here.
6. A prior human edit to `context.md` (the region named in step 4
   above), seeded deliberately **before** step 4's own `docs maintain`
   call, survives untouched throughout steps 4-7 and after — confirmed
   by direct diff, not merely by absence of an error, and confirmed to
   remain `doc_candidate` (never silently reconciled, resolved, or
   discarded) at every `docs maintain` call that follows it, including
   the final one in step 7.
7. **A second `docs maintain` run, after both affected regions are
   republished — corrected by this amendment** (the prior draft
   required this run to "reconcile to `noop` for all six schemas'
   worth of regions," directly contradicting step 6's own requirement
   that the seeded edit survive as `doc_candidate` — this was a real
   defect in the plan's own acceptance criteria, not a typo, since the
   two requirements as originally written could never both be true at
   once): must report `noop` for exactly the two regions that were
   legitimately republished (`adapter.md`, `vendor-and-ecosystem.md`)
   and for `knowledge-model.md` (genuinely untouched throughout); must
   report `doc_candidate`, unchanged, for `context.md` (step 6's own
   seeded edit, correctly never auto-reconciled); and must report the
   pre-existing README `intermediate-knowledge-layer` candidate in its
   own genuine, unrelated state, exactly as before — **not** `noop`.
   No unrelated candidate is acknowledged, applied, or discarded simply
   to make this run's own output look uniformly clean; a mixed result
   (some regions `noop`, one region still genuinely `doc_candidate`, a
   pre-existing unrelated candidate untouched) is the *correct*,
   expected outcome of this demonstration, not a loose end to tidy away.
8. **Reconciliation**: the published-evidence audit records for the
   two republished regions, and the accepted (or honestly-declined,
   per step 3's own branch) `CL-ADPT-005` amendment (or its named
   replacement/isolated substitute), are the permanent record —
   mirroring Stage 87B's own real demonstration's own closing step
   exactly. `context.md`'s own seeded `doc_candidate` and README's own
   pre-existing `intermediate-knowledge-layer` candidate are **not**
   reconciled as part of this closing step — both remain genuinely
   open, exactly as the five-state model requires for an unresolved
   human edit, and are reported as such in the retro, not silently
   dropped from the account.

If, at Stage 87C implementation time, direct re-inspection finds
`CL-ADPT-005` no longer legitimately supports a two-region change (for
instance, if `adapter.md`'s own drafted compiled section ends up not
actually citing `CL-ADPT-005` once genuinely composed and reviewed),
this plan requires selecting a different, better-supported real change
rather than forcing this one — the two-region *structure* of the proof
is the requirement; this specific Claim is this plan's own best
current candidate for it, re-verified at the point of use, not assumed
permanent.

### S.7 Comparator methodology and measurement rubric

Reuses Stage 87B's own real comparator design (arm A: conventional
agent, same starting revision, same task, no compiler infrastructure;
arm B: the compiled pipeline) — **not** re-invented, extended to a
larger, more realistic task: maintaining the **full, four-page**
compiled Concepts set (corrected from an earlier draft's "five" — see
§S.1/§S.2), across the §S.6 knowledge change, for both arms, from the
identical pinned starting revision.

**Total cost, not merely generation cost** — this amendment's own
central strengthening, per the governing task's explicit instruction
not to let the comparison conceal the cost of preparing the canonical
knowledge arm B depends on. Measured for **both arms**, split
explicitly into two phases, never collapsed into one figure:

- **Initial setup cost** (arm B only, since arm A has none of this):
  knowledge discovery and record preparation for whatever Claims the
  four compiled pages actually end up citing (§S.3's own prerequisite
  list); evidence research for the §S.6 amendment specifically
  (`EV-ADPT-0XX`); the §S.4a migration procedure's own effort per page
  (boundary identification, marker insertion, baseline establishment);
  schema design/authoring time for the four new `*.schema.yaml` files.
  Reported once, up front, not amortised or hidden inside a per-page
  average.
- **Ongoing marginal maintenance cost** (both arms): the §S.6
  incremental-change proof's own cost specifically — evidence →
  propose → reconcile → `docs maintain` → recompile → review →
  publish → reconcile, for arm B; the equivalent conventional-agent
  maintenance pass, from the same starting point, for arm A. This is
  the figure a reproducible baseline (`decisions/0085` §6) actually
  needs to compare, since it is what recurs on every future knowledge
  change — the initial setup cost, by contrast, is paid once.
- **Historical knowledge-preparation cost, a third, separate category
  — added by this amendment** (the prior draft's two-way split
  risked implying arm B's own total cost starts at "initial setup,"
  silently treating the Claims this plan compiles against —
  `CL-CTXT-001`, the `CL-ADPT-*`/`CL-EVID-*` cluster, all originally
  produced by earlier `context-researcher` dispatches in Phase 79/80,
  well before Stage 87 existed — as a free, pre-existing resource).
  These Claims' own original research cost (agent time, review effort,
  reconciliation) is a real prerequisite for arm B's approach to be
  possible at all, but **reliably reconstructing it now is not
  possible** — no bounded cost/value log exists for that much earlier
  work, unlike Stage 87B's own real demonstration, which logged its
  own costs as they happened. This is reported as **an explicit,
  disclosed-unavailable figure**, not treated as zero and not
  estimated — the same discipline Stage 87B's own bounded cost/value
  log already established for its own two uncaptured steps, applied
  here to a category the prior draft omitted entirely rather than to
  an individual measurement. Arm A's own equivalent (whatever general
  understanding of the codebase a conventional agent would need to
  rebuild from scratch, absent any canonical knowledge base at all) is
  reported the same way, for the same reason, so the comparison is not
  one-sidedly honest about only one arm's own hidden cost.

**Predeclared rubric** (fixed before either arm runs, per `decisions/
0085` §6 — never adjusted after seeing results):

- Factual correctness and unsupported-claim count (independent
  reviewer, blind to which arm produced which draft where practical).
- Coverage of the four compiled Concepts pages' own existing required
  facts.
- Cross-document terminology/factual consistency (the same reviewer
  checks "adapter"/"ecosystem"/"vendor" are used identically across
  whichever pages each arm touches, and specifically that `CL-ADPT-005`'s
  own amended fact reads consistently in both `adapter.md` and
  `vendor-and-ecosystem.md` for arm B).
- Editorial register and general readability/usability for the stated
  audience (the same "resembles an audit report" check Stage 87A's own
  hardening established, plus a plain readability pass — not solely a
  defect-detection exercise).
- Human correction effort: count and severity of changes a reviewer
  required before either arm's own output would be publishable.
- Human reviewer/editing time actually spent reaching that publishable
  state, **tracked separately from agent/tool elapsed time**
  (`decisions/0085` §6 names both as distinct required baseline
  components, not one line covering both).
- Agent execution time and total elapsed time, for each phase
  separately (initial setup vs. marginal maintenance, per above).
- Actual model usage/token cost, when observable — reusing Stage 87B's
  own precedent of disclosing an unavailable figure honestly rather
  than estimating it (two of that stage's own seven logged steps were
  disclosed as "not captured," not guessed); `L-122`'s own named gap
  (the clean-room broker's `usage` field not currently surfaced by
  `docs compile`'s CLI output) is a live input here, not a resolved
  prerequisite — if still unresolved at Stage 87C implementation time,
  this measurement for arm B's own compile steps is disclosed as
  unavailable, honestly, not invented.
- Response to the §S.6 knowledge change specifically: does each arm's
  own maintenance pass correctly scope its edit to the two genuinely
  affected regions, or does it touch unrelated content.
- Preservation of the seeded human edit from §S.6 step 6.
- Failed attempts, retries, and any unresolved finding from either
  arm — reported, never silently dropped from the final account (Stage
  87B's own rate-limit retry and the comparator's own one genuine
  editorial failure are the precedent for reporting this honestly).

**Predeclared material-improvement threshold**, fixed before either
arm runs, not chosen after seeing results. **Corrected citation (this
amendment)**: an earlier draft of this paragraph, and the matching row
in §S.9a, both claimed this threshold was mandated by `decisions/0085`
§6 itself and that its absence was "a gap against" that section. Direct
re-reading of §6 (lines 396-419) shows the opposite: §6 explicitly
**withdraws** `decisions/0084`'s own original threshold-based success
criterion ("materially less human correction than Phase 80") as "a
stand-alone success criterion," calling it "methodologically weak,"
and requires a *reproducible baseline methodology* instead (pinned
revisions, a fixed rubric, correction count/severity, review time —
all already reflected elsewhere in this section) — it never mandates
a predeclared numeric threshold. The threshold below is therefore this
amendment's **own voluntary methodological strengthening**, added
because the governing task that requested this amendment explicitly
asked for one ("predeclare a material-improvement threshold... before
running either arm"), not because `decisions/0085` §6 required it —
and it is applied consistently with §6's own actual spirit (a rigorous
experiment still passes regardless of outcome; the threshold gates
only the separate, harder, "advantage demonstrated" verdict below,
never the completion verdict). Arm B demonstrates a
material advantage only if, on the §S.6 marginal-maintenance task
specifically, it requires **strictly fewer human-reviewer corrections
of at least "major" severity** than arm A **and** does not cost more
than **1.5×** arm A's own total marginal-maintenance time (agent
elapsed + human review, combined) — both conditions, not either
alone, since a faster-but-less-accurate or more-accurate-but-much-
slower result is not the claimed advantage. This specific threshold is
itself a Stage 87C implementation-time decision to confirm or revise
before either arm runs (per the governing task's own instruction to
predeclare, not to lock in today's own choice of number) — named here
so a threshold exists in the plan rather than being invented after
results are seen.

**Two separate verdicts, never conflated**:

1. **Experiment completed rigorously** — both arms ran to completion
   against the identical pinned revision and task, every rubric line
   was measured or its unavailability honestly disclosed, and the
   §S.6 proof's own eight steps were independently verified. This can
   and should **PASS even if arm B performs worse than arm A** — a
   neutral or negative result, rigorously obtained and honestly
   reported, is a successful completion of the experiment per the
   governing task's own explicit framing.
2. **CodeCompass advantage demonstrated** — PASS only when the
   predeclared material-improvement threshold above is actually met.
   Distinct from, and strictly harder to earn than, verdict 1.

**What this is not**: a statistically powered trial. One real case per
arm, same discipline as Stage 87B's own single comparator run — honest
single-case evidence, with Stage 87B's own precedent (editorial-review
failure on the conventional arm) as the only prior data point, not
assumed to repeat. Neither verdict above licenses a claim of
statistically established superiority from this one comparison.

### S.8 Real-world documentation quality (§D of the governing task)

A genuinely independent read (a fresh dispatch with no prior context
of this plan or Stage 87A/B's own work) attempts, from the published
documentation alone: install and complete first run (Getting Started,
already execution-verified — confirm a human reading it, not only the
harness, finds it sufficient); explain in their own words what an
"adapter"/"ecosystem"/"vendor"/"digest" is, compared against the real
Claims to check for comprehension drift the compiled prose itself
might introduce; locate the CLI reference for one named command;
describe the reconciliation loop's own five states; identify one
planned-but-not-implemented capability versus one real, current one
(a direct test of the "no unsupported claims" editorial requirement).
Failures are findings, not something to explain away.

### S.9 Acceptance criteria (go/no-go gates)

1. Every Concepts page named in §S.2 is either genuinely knowledge-
   compiled (grounded marker present, citing a real `status: supported`
   or better Claim) or explicitly left human-authored-and-validated-in-
   place with a stated reason — no page silently stays "mostly prose,
   partly compiled" without that split being visible in its own schema
   file or an explicit note.
2. Every compiled section passes both independent reviews
   (semantic-support, editorial-quality) — no manually-typed verdict,
   reusing Stage 87B's own hardened `docs record-review`/`docs publish`
   integrity checks unchanged (including this session's own
   reviewed-draft-integrity fix).
3. The §S.6 incremental-change proof completes all eight steps for
   real (corrected from an earlier draft's "six" — the amended
   sequence adds explicit controlled-acceptance and reconciliation
   steps), with direct-diff confirmation of both the detected-change
   scope (both, and only both, of the two genuinely dependent regions
   reach `noop` after republication) and the unrelated-content
   preservation — **and** with the seeded, deliberately-unresolved
   `context.md` edit and the pre-existing README `intermediate-
   knowledge-layer` candidate both still, correctly, `doc_candidate`
   after the final `docs maintain` run, never silently reconciled,
   acknowledged, or discarded to make the output look uniformly clean
   (corrected by this amendment — the plan's own prior acceptance
   criterion here required "`noop` with every unrelated byte
   unchanged," which is internally correct for bytes but had, in an
   earlier draft of §S.6 itself, conflicted with that same demonstration
   requiring a region to stay `doc_candidate`; this criterion is now
   explicit that a mixed final state is the correct, required outcome,
   not asserted from a tool's own summary).
4. The §S.7 comparator runs to completion for both arms against the
   identical task, measures initial-setup cost and marginal-
   maintenance cost separately, reports every rubric line (including
   any disclosed-unavailable measurement) and reaches an explicit
   verdict on each of §S.7's own two separate questions (experiment
   completed rigorously; CodeCompass advantage demonstrated against
   the predeclared threshold) — and draws no "statistically superior"
   claim from one case regardless of either verdict.
5. `docs-reconstructor` finds no blocking drift in any touched
   document; `release-phase-auditor` returns PASS or PASS WITH
   NON-BLOCKING OBSERVATIONS against the complete implementation diff.
6. No fabricated or automatically-accepted knowledge: every new Claim
   amendment this stage's own demonstration proposes goes through the
   ordinary evidence → candidate → reconciliation workflow, same as
   `EV-CTXT-021`/`L-123` this session, never silently merged.
7. No regression of clean-room isolation: `verify_cleanroom_isolation.
   py`'s existing preflight still passes unchanged; no new sandbox
   construction, no new broker.
8. Reproducible from a pinned project/knowledge revision: the §S.7
   comparator and §S.8 independent read both record the exact git
   revision and knowledge-record state they ran against.
9. Explicitly **not** required for this stage's own go/no-go: the
   `docs/reference/cli.md` deterministic generator named in §S.2 as a
   real but separable opportunity, and the semantic cross-document
   consistency checker named in §S.4 as unaddressed. Both are named
   explicitly as deferred, not silently dropped — see §S.11.

**Honest framing, restated from the governing task's own wording**: a
neutral or negative result from §S.7's comparator — the compiled arm
costing more, or not clearly outperforming the conventional arm on
this particular task — would still mean this stage completed
successfully, if run rigorously and reported honestly. Completion of
the experiment and validation of a claimed advantage are different
things; only the former is required to close Stage 87C.

### S.9a Original Phase 87 exit gate — requirement-to-disposition mapping (new subsection, added by this amendment)

Cross-checking §F (this plan file's own original Stage 87C scope
sketch) and `decisions/0085` §5-§6 against §S.9's own acceptance
criteria, so nothing in the original Definition of Done is silently
weakened. Each requirement classified as **implemented already**,
**delivered by 87C** (this plan), **validated in place** (retained,
not regenerated, but confirmed accurate), or **explicitly deferred**
(named, with a reason, never silently dropped):

| Requirement (`decisions/0085` §5/§6, §F) | Disposition | Detail |
|---|---|---|
| README: problem, value, capabilities, installation, first steps | **Validated in place** (mostly) + **implemented already** (one section) | One section (`vendor-digest-concept`) knowledge-compiled since Stage 87B; the rest is accurate human-authored prose, confirmed this session (§S.1) — not regenerated, since no competing Claim exists to ground it against. |
| Getting Started: tested, practical first-use tutorial | **Implemented already** | Fully schema-governed, three of five sections execution-verified, two verified by other direct means (§S.1, corrected this amendment) — `decisions/0085`'s own requirement ("tested") is satisfied more directly by execution-verification than a Claim citation would be, confirmed sufficient as-is. |
| Concepts: canonical knowledge, evidence, contracts, epistemic distinctions, reconciliation | **Delivered by 87C** (4 of 7 pages, knowledge-compiled) + **validated in place** (3 of 7: `digest.md`, `knowledge-placement-policy.md`, `protocol-and-capability.md`) | §S.1's own correction to `decisions/0085`'s framing stands: the "epistemic distinctions and reconciliation loop" content gap it named is already closed by existing prose (`knowledge-model.md`); 87C's own contribution is grounding four pages' worth of already-accurate content, not writing new coverage from nothing. |
| Architecture: components, responsibilities, data flows, design principles | **Validated in place** | Confirmed accurate, dense, human-authored prose this session (§S.1) — no compilation gap of the kind Concepts has; deliberately not regenerated (§S.2 category 3's own register-risk reasoning). |
| Reference: accurate CLI/configuration info, generated deterministically where practical | **Explicitly deferred** | A deterministic `cli.md` generator from the live Typer command tree remains a real, named, separable opportunity (§S.2 category 2, §S.9 point 9) — consistent with `decisions/0085`'s own framing of this as "this phase's own improvement opportunity, not assumed solved," not a weakening of it: the decision never mandated this be built in any *specific* stage, and 87A/87B/87C's own scope-management precedent (§D/§E/§F's original stage split) already establishes that naming a real deferral, with a path for a future phase, is consistent with this project's own governance, not a silent drop. |
| Contributor Guide: conventions, workflow, testing, verification, knowledge-placement expectations | **Validated in place** | Explicitly, deliberately out of clean-room scope by design (confirmed unchanged, §S.1/§S.2) — the guide itself is current and accurate; not a knowledge-compilation candidate under this project's own established discipline (`docs/development/contributing.md`'s own stated reason, unchanged). |
| Factual and editorial validation, distinct steps | **Implemented already** + **delivered by 87C** | The two-question independent-review mechanism (semantic-support, editorial-quality) is Stage 87A/87B's own existing infrastructure, reused unchanged for every new compiled section this stage adds, plus §S.4a step 5's own bounded addition for migrated pages specifically. |
| Practical onboarding and usability, tested | **Delivered by 87C** | §S.8's own independent, fresh-dispatch read — not previously performed for the Concepts-page content specifically. |
| Cross-document consistency | **Delivered by 87C** (structural) + **explicitly deferred** (semantic checker) | Structural consistency (two sections citing the identical Claim id) is delivered via §S.4's own shared-Claim-grounding design; a *semantic* cross-document consistency checker (catching two sections asserting incompatible facts about the same Claim) is named explicitly as unaddressed (§S.4, §S.9 point 9) — the governing task's own §6 confirms this need not automatically become a new implementation requirement, and this plan does not silently claim it is solved. |
| Deterministic generation where appropriate | **Implemented already** (Getting Started) + **explicitly deferred** (CLI reference) | See the two rows above — already split correctly, not conflated. |
| Knowledge-grounded compilation and provenance | **Delivered by 87C** | Four new compiled pages, machine-readable grounding unconditional (§G.C's own standing requirement, unchanged), reusing Stage 87A/87B's own provenance mechanics exactly. |
| Safe incremental maintenance | **Delivered by 87C** | §S.6's own corrected, genuinely two-region incremental-change proof. |
| Human-edit preservation | **Implemented already** (mechanism) + **delivered by 87C** (migration-specific proof) | `publish_section`'s own region-splicing preserves unrelated content unchanged, proven by Stage 87B's own existing tests; §S.4a's own migration procedure extends this guarantee to the specific, previously-unaddressed case of adopting a page with pre-existing, unmarked human prose. |
| Matched-baseline quality evaluation | **Delivered by 87C** | §S.7's own corrected comparator, now measuring total cost (setup + marginal) rather than generation cost alone. |
| Material-improvement threshold, predeclared | **Delivered by 87C** | §S.7's own predeclared threshold, added by this amendment at the governing task's own explicit request — **not**, corrected from an earlier draft's own mischaracterization, something `decisions/0085` §6 itself mandates: §6 in fact explicitly withdraws a threshold-based success criterion as "methodologically weak," requiring a reproducible baseline methodology instead (already reflected elsewhere in this table/§S.7). This row's threshold is a voluntary strengthening consistent with §6's own spirit, not a restoration of a requirement §6 ever stated. |
| Independent audits and original applicable tests | **Delivered by 87C** | §S.5 step 8's final `docs-reconstructor`/`release-phase-auditor` pass; the original 18-test matrix's own Stage-87C-assigned items (test 11, documentation-quality comparison) are covered by §S.7/§S.8. |

**No silent weakening**: every deferral above (Reference's generator;
the semantic cross-document checker) was already named as deferred in
this plan's own prior draft (§S.2, §S.9 point 9, §S.11) — this mapping
makes the *disposition* of every other requirement explicit and
auditable against `decisions/0085` directly, rather than leaving a
reviewer to infer it from scattered mentions across §S.1-§S.11.

### S.10 Risks and explicit non-goals

**Risks**: (a) compiled Concepts prose reading worse than the already-
good existing human-authored prose it replaces — mitigated by keeping
the existing file as the schema's own implicit quality bar (the
editorial reviewer is told the audience/tone this page already
achieves) and by Stage 87A's own three-round hardening precedent for
what to do if the first attempt underperforms; (b) a Claim amendment
proposed by §S.6 being declined on reconciliation — an acceptable,
honestly-reported outcome, not a stage failure, exactly as `EV-CTXT-
021`'s own framing this session already establishes; (c) the §S.7
comparator's single-case result not replicating Stage 87B's own
editorial-review-failure finding — also an acceptable, honestly-
reported outcome per §S.9 point 9's own framing.

**Explicit non-goals** (per the governing task's own §6, restated
against this specific plan, not generically): no MCP server; no
autonomous multi-agent development system; no new canonical knowledge
database (every prerequisite in §S.3 reuses the existing evidence →
candidate → reconciliation workflow); no general-purpose documentation
CMS; no UI; no unrestricted automatic knowledge acceptance (every
Claim amendment is proposed, never auto-applied); no redesign of the
clean-room infrastructure (§S.4's "reused, unchanged" list is
exhaustive); no requirement to generate every paragraph with an LLM
(§S.2's categories 2-4 are deliberately retained, not converted).

### S.11 Backlog and roadmap implications

Deferred, named explicitly rather than silently dropped, each a
candidate for its own future phase/backlog row, not Stage 87C's own
scope:
- A deterministic `docs/reference/cli.md` generator from the live
  Typer command tree (§S.2 category 2, §S.9 point 9).
- A semantic cross-document consistency checker beyond shared-Claim-id
  grounding (§S.4).
- Closing `knowledge-model.md`'s thinner-cited corners and `protocol-
  and-capability.md` with new, purpose-written Claims (§S.3's option
  (a), deferred in favour of option (b) for this stage).
- `L-122` (surface the clean-room broker's own usage/cost figures in
  `docs compile`'s CLI output) and `L-124` (the residual `docs publish`
  write-boundary race, narrowed twice, not fully closed) — both already
  filed this session, both real inputs to this stage's own cost
  accounting and safety-margin assessment respectively, neither
  blocking it.

### S.12 Independent planning review

**First review round (2026-11-09) — preserved unchanged as the
historical record for the plan as it stood before this amendment; not
reopened or edited.**

**Verdict: READY WITH NON-BLOCKING OBSERVATIONS** (2026-11-09). An
independent dispatch re-derived every factual claim in this section
directly against the real repository rather than trusting its prose —
`decisions/0085` §5/§6's own text; the `context.md`↔`CL-CTXT-001`,
`vendor-and-ecosystem.md`↔`CL-ADPT-005`, and `knowledge-model.md`↔
`CL-EVID-*` mappings (including confirming `CL-EVID-003`/`008`/`009`/
`011`'s correct exclusion); `check_doc_schema.py`'s/`docs_maintain`'s
real `**/*.schema.yaml` discovery; `resolve_publication_target`'s
already-generic `docs/**/*.md` allowance; the absence of scope creep
against the governing task's §6 non-goals; and every cross-referenced
commit/file from this session's own prior work. Found the plan's
dependency structure, scope boundaries, and acceptance criteria sound
and non-circular. Three narrow, non-blocking findings — §S.6's
backward-compatibility fact was deferred as "confirmed at
implementation time" when it was already directly confirmable;
§S.7's rubric folded `decisions/0085` §6's two distinct required
baseline components (correction count/severity, and separately human
review/editing time) into one line; §S.2's Claim-id range loosely
included two already-excluded superseded ids — all three corrected in
place above (§S.6 now states the confirmed fact directly with its own
citations; §S.7 now measures human review/editing time as its own
line; §S.2 now names the exact Claim-id list, cross-referencing §S.3's
authoritative version). No further review round required unless this
plan's content changes again before Stage 87C's own separate
implementation authorisation.

**This plan was implementation-ready as of the first review round.**
Stage 87C implementation itself remains separately, explicitly
unauthorised by this planning pass, per the governing task's own
instruction.

**Amendment (2026-11-09, same day): §S.1, §S.2, §S.4, §S.5, §S.6, §S.7
amended; new §S.4a, §S.9a added.** A fresh governing task found and
required correction of several real factual/scope inconsistencies in
the plan as it stood after the first review round: Getting Started's
own section/verification counts were stated inaccurately (§S.1); the
Concepts compilation list named five pages while the implementation
sequence (§S.5) and the knowledge-readiness assessment (§S.3) had
already, inconsistently, settled on four (§S.2); the schema-count
arithmetic referenced "five schemas" when the real total is six
(§S.4/§S.5); the incremental-change proof's own second affected region
was a page never scheduled for compilation, failing to guarantee a
genuine two-*compiled*-region demonstration (§S.6, replaced with a
verified, already-shared `CL-ADPT-005` dependency between `adapter.md`
and `vendor-and-ecosystem.md`); the comparator measured generation
cost without a predeclared material-improvement threshold or a
setup-vs-marginal cost split (§S.7); and the plan had no explicit
existing-document migration procedure despite `publish_section`'s own
append-not-replace behaviour for an unmarked page, a real risk of
silently duplicating existing Concepts prose rather than governing it
(new §S.4a). A new §S.9a cross-checks every original Phase 87 exit-
gate requirement (`decisions/0085` §5-§6, §F) against this amended
plan's own disposition, confirming no requirement was silently
weakened in the course of these corrections.

**Second review round (2026-11-09, same day).**

**Verdict: READY WITH NON-BLOCKING OBSERVATIONS.** An independent
dispatch, instructed explicitly to inspect actual repository files
rather than assess the plan's own internal coherence alone and to
challenge the multi-section dependency proof, migration safety,
coverage counts, and consistency with `decisions/0085` specifically,
independently re-derived: the exact Getting Started section/
verification counts (5 sections, 3 execution-verified, 2 verified by
two specifically-named other tests, both confirmed to exist); README's
two real grounded regions; the exact schema-file count (2 real files
on disk); that `adapter.md`'s own real prose genuinely states a direct
instance of `CL-ADPT-005` (not a reach) and that `vendor-and-ecosystem.
md` independently states the same relationship, establishing a real
shared dependency; `publish_section`'s real append-vs-replace
behaviour and the full `new`/`noop`/`doc_candidate`/`concurrent_
conflict` branching §S.4a's own safety argument depends on, finding no
hole in it; the real source lines and real, passing test behind
§S.6's replacement incremental-change candidate; and `decisions/0085`
§5/§6's own actual text. Found the corrected four-page scope, the
six-schema arithmetic, and the one-to-five grounded-region count
consistent everywhere across §S.1-§S.11 and §S.9a, and found no
recurrence of the five-vs-four-page inconsistency or an
insufficiently-dependent incremental-change candidate the first review
round had missed.

Two non-blocking defects found, both corrected in place above: (A) a
fabricated quote — an earlier draft attributed "hard-coded to this
repository" to `knowledge-placement-policy.md`'s own text; that exact
phrase is real but belongs to an unrelated docstring in `knowledge_
intermediate.py`, describing a different artifact's module boundary —
removed, the substantive point rewritten to stand on the page's
actual, real content instead; (B) a mischaracterised citation,
repeated in §S.7 and §S.9a — both claimed `decisions/0085` §6 itself
mandates a predeclared material-improvement threshold, when §6 in fact
explicitly withdraws a threshold-based criterion as "methodologically
weak" and requires a reproducible baseline methodology instead; both
occurrences corrected to frame the threshold as this amendment's own
voluntary strengthening, requested by the governing task, applied
consistently with §6's actual spirit rather than attributed to §6 as a
restored requirement.

**This amended plan was implementation-ready as of the second review
round.** Stage 87C implementation itself remained separately,
explicitly unauthorised through that point, per the governing task's
own instruction.

**Amendment (2026-11-09, same day): §S.2, §S.3, §S.5, §S.6, §S.7
further amended; the first two review rounds above preserved
unchanged as historical record.** A fresh governing task found five
further real findings in the plan as it stood after the second review
round: (A) §S.6's own acceptance criteria contradicted the five-state
reconciliation model — it required a deliberately-seeded human edit to
survive as `doc_candidate` while also requiring the final `docs
maintain` run to report `noop` everywhere, which cannot both be true;
corrected so the final state is explicitly mixed (two regions `noop`,
one seeded edit and the pre-existing README candidate both still
`doc_candidate`). (B) §S.6 let the `CL-ADPT-005` amendment be declined
while still unconditionally requiring the `claims_changed`
demonstration that depends on it being accepted — corrected with an
explicit accept/decline branch, naming two concrete fallback paths if
declined (a different evidence-backed change, re-verified; or an
explicitly-named isolated worktree demonstration). (C) §S.2 still
contained one remaining stale "five... sections" reference for Getting
Started (corrected). (D) No preflight existed to confirm the four
planned Concepts schemas' own Claims genuinely pass the compiler's
real evidence-currency/budget checks, as opposed to merely reading
`status: supported` from their own YAML — new §S.3 preflight added,
reusing only existing `doc_compiler`/`knowledge_api` functions,
inserted as implementation step 2 in §S.5. (E) §S.7's comparator split
cost into "initial setup" and "marginal maintenance" but silently
treated the Claims' own original historical research cost (Phase
79/80) as free — a third, explicitly disclosed-as-unavailable cost
category added for both arms.

**Third review round (2026-11-09, same day).**

**Verdict: READY WITH NON-BLOCKING OBSERVATIONS.** An independent
dispatch, instructed to verify the corrected assumptions against
actual code and records — particularly reconciliation-state logic,
knowledge currency, migration procedure, and comparative methodology —
ran real code rather than reading prose for consistency alone:
executed `detect_grounded_region_changes` directly against the real
repository and confirmed `region:intermediate-knowledge-layer` is
genuinely `doc_candidate` right now; read `maintain_document`/`decide_
publish_safety`/`write_doc_candidates_to_manifests` and confirmed no
code path exists by which publishing the two affected regions could
ever advance or "fix" `context.md`'s own seeded-edit baseline,
directly validating Finding A's own safety argument rather than
merely its prose; confirmed the declined-amendment branch (Finding B)
genuinely resolves the prior contradiction, with one minor clarity gap
(now fixed above: the isolated-worktree path's own scope extended
explicitly across all of steps 4-8, not only the knowledge change's
own landing); re-confirmed Getting Started's corrected counts (Finding
C); independently **ran** the new compilation-readiness preflight
(Finding D) against all real, current Claims rather than trusting its
own specification, confirming every function it calls is real and
behaves as described, and surfacing two further, concrete findings of
its own — a stale "nine Claims" count (this amendment's own new text
repeating the exact species of error Finding C had just fixed
elsewhere, now corrected to the accurate fifteen) and a real, measured
budget requirement for `knowledge-model.md` (18,552 characters against
the repository's only existing precedent of 4,000 — now stated
explicitly, ≥20,000, rather than left for implementation to discover
mid-compile); and confirmed Finding E's "disclosed as unavailable"
framing is an honest characterisation of Phase 79/80's own retros
(searched directly for any numeric cost figure; none exist), not a
loophole concealing a reconstructable number. Both findings from this
round are corrected in place above.

**This amended plan is implementation-ready.** Stage 87C implementation
may now proceed, per this session's own separate authorisation to do so.
