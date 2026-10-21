# Post-v2 Cross-Project Semantic Overlay track — candidate stages, risks, and gates

Direct user request, 2026-10-21 ("CodeCompass v2 Planning Amendment —
Cross-Project Semantic Overlays"). Architectural rationale: `decisions/0079`.
**These are proposals, not authorised implementation phases** — none is
numbered into the mandatory Phase 82-88 sequence (`planning/v2-roadmap.md`),
none blocks Phase 88's v2.0 release, and none may begin without its own
future `CLAUDE.md` §1 plan file, scoped against evidence current at that
time, exactly as every prior phase in this project already requires.

**Amendment log**: 2026-10-21, same day, "CodeCompass v2 — Corrective
Planning Amendment" (`decisions/0080`) made three targeted corrections,
each at the point it applies below: Stage 2 clarifies hledger knowledge
construction without an implicit Haskell-adapter dependency; Stage 5 is
now design-only, with empirical comparison explicitly deferred to a
separate, not-yet-numbered future stage; Stage 7 separates accounting-
backend generalisation (Beancount) from the genuinely-unrelated-domain
validation actually required before any "domain-independent" claim.
The same amendment extended the project-identity envelope (§"Verified
vs. unverified prerequisites" references it below) with a `publisher_id`/
`authority` distinction — a snapshot's own existence never implies the
described project's maintainers endorsed it.

## Why PTA, why not an accounting-specific capability

Cross-project semantic overlay is a **generic CodeCompass capability**
(`decisions/0079` Layers A-C apply to any domain with multiple
independent implementations). Ledgerkit/hledger/Ledger/Beancount is the
**motivating use case** because all four already exist, three are
locally available or previously studied by this project
(`planning/ledgerkit-stage-c-learnings.md`, Phases 45-78), and Ledgerkit
is already CodeCompass's established reference project. Nothing in the
design below (Layer B Domain Concepts, Layer C mappings, the
project-identity envelope) is PTA-specific; a future unrelated-domain
trial (Stage 7) exists specifically to test that claim rather than
assert it.

## Verified vs. unverified prerequisites (honest baseline)

- **`ctosullivan/ledgerkit`**: real, local, actively developed
  (`~/projects/ledgerkit`, HEAD `7224bb5` at time of writing) — already
  CodeCompass's reference project.
- **`hledgerorg/hledger`**: real, local (`~/projects/hledger`, HEAD
  `33fa849e`, `LICENSE` present, remote confirmed
  `https://github.com/hledgerorg/hledger.git`) — GPL-licensed, already
  the basis for this project's own `decisions/0053`-era GPL relicensing
  rationale for Ledgerkit-facing source inspection.
- **`ledger/ledger`** (the C++ Ledger CLI): **no local checkout exists
  in this environment.** Its current repository state, version, licence
  terms, and contribution constraints are **not verified this session**.
  Stage 3 confirms these live, before any implementation, not from this
  document's own assumption.
- **Beancount**: **no local checkout exists in this environment.**
  Same caveat as Ledger — Stage 7 confirms live.

## Candidate stages

Each stage names its own falsifiable exit gate per the governing
prompt's explicit requirement — "falsifiable" here means a result that
could come back negative and be reported as such, not a checklist that
can only ever be satisfied.

### Stage 1 — Portable project snapshot and identity proof

**Goal**: build and validate `decisions/0079` §5's export format for
exactly one project (Ledgerkit) — a static JSON snapshot plus a
project-identity envelope (including `decisions/0080` §3's
`publisher_id`/`authority` fields, specified, not yet implemented, by
that ADR), consumable with no running `codecompass` process.

**Depends on**: Phase 82 `done` (needs real Claim/Requirement/contract
records, and `decisions/0080`'s derived epistemic view, to export).

**Exit gate (falsifiable)**: a Ledgerkit snapshot, exported once, can be
independently re-validated (schema-shape, content-hash integrity, no
access to the live `ledgerkit` checkout required) by a process given
only the exported files. **Failure condition**: the export requires the
live repository or CodeCompass's own database to validate — the stage
has not actually produced a portable artifact.

### Stage 2 — Ledgerkit/hledger semantic comparison

**Goal**: produce real Layer B Domain Concepts and Layer C mappings for
the narrow concept set in §"Accounting concept scope" below, between
Ledgerkit and hledger specifically (both locally available).

**Corrected, 2026-10-21 (corrective amendment): how a real hledger
knowledge snapshot is built before any Haskell source-analysis adapter
exists.** CodeCompass has no Haskell symbol indexer (`decisions/0065`
scopes first-party source indexing to Python/Rust/JavaScript/TypeScript
only) — **Stage 2 does not implicitly depend on one.** hledger evidence
is gathered through exactly the methods already available to this
project without one, each honestly labelled using the *existing*
`basis` enum (`check_knowledge_base.py`'s `_OPTIONAL_ENUM_FIELDS`,
no new value needed):

- **Externally observed behavioural claims** (`basis:
  observed_behaviour`) — running hledger's real CLI, reading its real
  output, executing its own published test cases
  (`~/projects/hledger`'s own `tests/`) — black-box, language-
  independent, and the **stronger** of the two evidence classes for
  this purpose, since Stage 2's own exit gate is defined in terms of
  verified *behaviour*, not verified *source structure*.
- **Source-derived architectural claims** (`basis: directly_stated`,
  citing a real `source_ref`) — a human or agent reading a specific,
  cited hledger source file/line range and recording what it says,
  exactly as Evidence already supports for any language via direct
  citation, with no symbol-level parser required. **This is explicitly
  weaker evidence than a behavioural observation** for the same claim,
  and the derived epistemic view (`decisions/0080` §1) will show it as
  such: `basis: directly_stated` without a resolving Observation stays
  `DECLARED`-strength, never silently promoted to `OBSERVED`.
- **Published specifications/manuals** — cited the same way as any
  other doc reference (`doc_ref`), never treated as more authoritative
  than an actual, executed behavioural check when the two disagree.

Every hledger snapshot produced this way carries `project_id: hledger`,
`publisher_id:` whoever actually ran the reconstruction (not an hledger
maintainer), and `authority: third-party-reconstruction`
(`decisions/0080` §3) — **never `self-published`** — regardless of how
rigorous the behavioural evidence is, since rigour of evidence and
maintainer endorsement are different questions (§"Verification and
reconciliation model" below; `decisions/0080`'s own project-identity
refinement).

**Depends on**: Stage 1 (needs two real portable snapshots — Ledgerkit's
and a new, equivalent hledger export).

**Exit gate (falsifiable)**: at least one real, evidenced
`equivalent_to` or `differs_from` mapping between a genuine Ledgerkit
behaviour and a genuine hledger behaviour, verified by actual execution
of both (not inferred from documentation or command-name similarity —
`decisions/0079`'s own explicit prohibition). **Failure condition**: no
mapping reaches `verification_status: equivalent_under_tested_conditions`
or `known_semantic_difference` — every candidate stays
`insufficient_evidence` — reported honestly as a negative/inconclusive
result, not reframed as success.

### Stage 3 — Ledger compatibility and differential verification

**Goal**: extend Stage 2's comparison to `ledger/ledger`, after first
verifying its real repository/licence/version state (named explicitly as
unverified above).

**Depends on**: Stage 2's mapping model proven against a real pair
first; a licence/contribution-constraint check specific to Ledger,
done live, not reused from this document.

**Exit gate (falsifiable)**: at least one real differential-execution
test comparing Ledgerkit, hledger, and Ledger on the same input produces
a mapping with a genuine `verification_status`, including the honest
possibility that the result is `known_semantic_difference` rather than
equivalence.

### Stage 4 — Backend-independent Ledgerkit API implications

**Goal**: using Stages 2-3's real evidence (not speculation), identify
which accounting operations belong in a small, coherent Ledgerkit
semantic core with explicit backend-specific extensions — never "one
giant API reproducing every backend's CLI" (the governing prompt's own
explicit non-goal).

**Depends on**: Stages 2 and 3 providing enough real mapping evidence to
distinguish genuinely shared semantics from implementation-specific
behaviour.

**Exit gate (falsifiable)**: a concrete, evidence-cited recommendation
(which operations are core, which are backend-specific extensions,
which are unsupported somewhere) that Ledgerkit's own maintainers could
act on — or an honest report that the evidence gathered so far is
insufficient to recommend an API shape yet.

### Stage 5 — Natural-language query model implications (design-only; empirical comparison explicitly deferred)

**Goal**: inform (not implement) the architecture named in the governing
prompt's §9 — natural-language intent → typed accounting operation →
deterministic semantic validation → backend capability/compatibility
resolution → adapter → execution — using Stage 4's semantic-core
findings as the typed-operation vocabulary's evidence base.

**Corrected, 2026-10-21 (corrective amendment): resolves a real
inconsistency between this stage's own design-only goal and its
originally-proposed empirical exit gate.** The prior exit gate ("a
documented comparison... measuring semantic correctness, ambiguity
handling, and unsupported-operation reporting") is genuinely empirical —
it requires running something — while the stage's own goal is explicitly
"inform, not implement." Claiming that comparison as Stage 5's own exit
gate would have let a design-only deliverable carry an empirical-
sounding claim it had not actually earned. **Stage 5 is now design-only,
with its own non-empirical, still-falsifiable exit gate; the empirical
comparison is explicitly a separate, later, not-yet-numbered future
stage, named but not scheduled here.**

**Depends on**: Stage 4's recommended semantic core existing in some
real form.

**Exit gate (falsifiable, design-only)**: the typed-operation schema
(natural-language intent → typed accounting operation) can represent
every operation Stage 4 actually identified as core, reviewed against
Stage 4's own evidence rather than invented fresh. **Failure condition**:
the schema cannot represent at least one Stage-4-identified core
operation without an ad hoc exception — a concrete, checkable failure,
not merely "the design feels incomplete."

**Explicitly deferred, not this stage's own exit gate**: a bounded
empirical comparison of schema-constrained intent translation against
direct model-generated backend commands, measuring semantic correctness,
ambiguity handling, and unsupported-operation reporting. If ever funded,
this runs as its own later stage, against Stage 5's own completed schema
— **CodeCompass would provide the semantic contracts/evidence such a
comparison needs; it would not execute accounting operations or own
Ledgerkit's runtime API** (`decisions/0079`'s non-goal list; the
governing prompt's explicit instruction), and a result showing no
measurable advantage over direct model-generated commands would be
reported as such, not reframed. **No claim of empirical validation is
made anywhere in this document for Stage 5** — only that its schema has
been designed and checked against Stage 4's own real findings.

### Stage 6 — Read-only federated Wiki visualisation

**Goal**: the actual visual interface — explicitly **not designed or
implemented in this amendment or by any stage before this one**. Loads
Stage 1-3's static exports (Ledgerkit, hledger, optionally Ledger) plus
a Stage 2/3 mapping dataset, distinguishes verified/candidate/
contradictory/unsupported mappings visually, and lets a viewer inspect
underlying evidence/source revisions — all from static JSON/Markdown,
no running CodeCompass process (the governing prompt's own explicit
requirement).

**Depends on**: the already-deferred, not-yet-scheduled Wiki track in
general (`planning/v2-roadmap.md`'s deferred-scope table), plus Stages
1-2 at minimum for real data to visualise.

**Exit gate (falsifiable)**: a viewer can distinguish a genuinely
verified mapping from a merely candidate one using only the visual
interface, without it implying authority a mapping's own
`verification_status` doesn't actually have (the governing prompt's own
named risk, §"Risks" below) — tested by showing a deliberately
`insufficient_evidence` mapping and confirming a reviewer does not
mistake it for an accepted one.

### Stage 7 — Beancount generalisation, and genuine cross-domain validation

**Goal**: test whether Layers A-C generalise beyond accounting at all.

**Corrected, 2026-10-21 (corrective amendment): Beancount alone does
not establish domain independence.** A fourth accounting-PTA backend is
useful evidence that the model generalises *within* accounting, but
every one of Ledgerkit/hledger/Ledger/Beancount shares the same domain
vocabulary (accounts, postings, balances, commodities) — succeeding on
a fourth instance of the same domain says nothing about whether Layers
A-C's design is actually domain-agnostic, only that it is accounting-
agnostic-within-accounting. **This stage is split into two explicitly
separate claims, both required before "domain-independent" is ever
said of this capability:**

- **Tier 1 — additional accounting-backend generalisation (Beancount,
  after its own repository/licence verification, per this document's
  own honest-baseline standard).** Exit gate (falsifiable): the
  existing Layer A/B/C model and export format accommodate Beancount
  **without a redesign of the core schema**. **This result alone
  licenses only an accounting-backend-generalisation claim** — it must
  not be cited, by itself, as evidence of general domain independence.
- **Tier 2 — validation against a genuinely unrelated software domain**
  (not accounting; a domain with its own distinct vocabulary and
  behavioural concerns entirely). Exit gate (falsifiable): the same
  Layer A/B/C model and export format accommodate a real project in
  that unrelated domain, again without a core-schema redesign.
  **Required — not optional — before any "domain-independent" or
  "generic capability" claim about this track is made anywhere**
  (`decisions/0079`'s own founding claim that overlay is "a generic
  CodeCompass capability" remains a design intent until Tier 2 actually
  runs, not yet a demonstrated fact).

**Depends on**: Stages 1-4 having produced a reusable-in-practice (not
just reusable-in-theory) Layer B/C design.

**Failure condition (either tier)**: a result requiring a ground-up
schema rewrite is reported as a falsification of the "generic
capability" claim for that tier specifically, not quietly absorbed as a
version 2 of the schema, and not allowed to retroactively validate the
other tier.

## Accounting concept scope (Stages 2-3's starting set)

Per the governing prompt's own named list, narrowed further if a
credible first proof needs fewer: account balances; posting and
transaction filtering; date and period queries; account hierarchy and
depth; running balances; commodity valuation. Stage 2's own plan
confirms the final subset against real, currently-passing test coverage
in both Ledgerkit and hledger before committing to it — not pre-decided
here.

## Dependencies on other deferred tracks

- **Haskell adapter** (`planning/v2-roadmap.md`'s deferred-scope table):
  Stage 3 (Ledger, written in C++) and any hledger-adapter work (hledger
  is Haskell) do not require CodeCompass's own deferred Haskell *source*
  adapter — comparing *behaviour* (black-box execution, differential
  testing) does not require CodeCompass to parse Haskell source. If a
  future stage's evidence shows source-level Haskell understanding is
  actually necessary, that is a new, separate funding decision, not an
  implicit dependency this track pre-commits to.
- **Wiki track**: Stage 6 depends on it directly, named as such; no
  other stage does.

## Verification and reconciliation model (governs Stages 2-3 onward)

Every mapping's `verification_status` (one of five, never collapsed
into a single compatibility score, `decisions/0079` §3):

1. **Equivalent under tested conditions** — differential execution (or
   an equally rigorous check) produced matching results under named,
   recorded conditions. Never "equivalent, full stop" — the conditions
   are part of the claim.
2. **Known semantic difference** — a real, evidenced difference, not a
   failure to test.
3. **Unsupported capability** — one side genuinely lacks the capability;
   not a stand-in for "we didn't check."
4. **Insufficient evidence** — the honest default until real evidence
   exists; never silently promoted by the mere passage of time or by
   repeated citation.
5. **Invalid comparison** — the comparison itself was methodologically
   unsound (mismatched versions, incompatible fixtures, a tool error) —
   distinct from "known semantic difference," which is a real finding.

**Invalidation**: a change to Project A's own source, tests, or
specification invalidates only mappings that cite the changed Claim/
Evidence — reusing Phase 85's own planned source-change-triggered
invalidation (`planning/v2-roadmap.md`'s Phase 85 entry), extended to
also re-check every Layer C mapping citing the changed reference. **A
change to one project's own Layer A records never directly rewrites
another project's own Layer A records** — only the shared Layer C
mapping's own status is touched, and only to flag it for re-review
(downgraded toward `stale`/`insufficient_evidence`), never to silently
"correct" the mapping's conclusion automatically.

## Risks (explicit, not implicitly accepted)

- **False semantic equivalence** — mitigated by requiring real
  differential execution or an equivalent rigorous check before
  `equivalent_to`/`equivalent_under_tested_conditions`, never inferred
  from naming/command/data-structure similarity (`decisions/0079`'s own
  explicit prohibition).
- **Stale cross-project evidence** — mitigated by the invalidation model
  above; a mapping's own `lifecycle_status` surfaces staleness rather
  than hiding it behind an unchanged-looking record.
- **Version and schema incompatibility** — mitigated by `revision`/
  `knowledge_schema_version` being mandatory, explicit fields in every
  project-identity envelope from Stage 1 onward.
- **Knowledge identity collisions** — mitigated by qualified references
  always being a `(project_id, revision, local_id)` triple, never a bare
  local ID assumed globally unique.
- **Excessive ontology complexity** — mitigated by Layer B staying
  minimal and populated only as Stage 2 actually needs specific
  concepts, never pre-built as a general ontology (explicit non-goal).
- **Unbounded maintenance overhead** — named, not yet mitigated with a
  mechanism; a real risk of any multi-project tracking system. Stage 2's
  own plan must address this directly (e.g. a staleness budget or
  review cadence) before being considered implementation-ready, since
  this backlog entry does not resolve it.
- **Cross-project trust and prompt-injection risks** — an external
  project's own README/docs/source is untrusted content the moment it
  crosses a project boundary into another project's context, exactly as
  `planning/v2-migration-assessment.md`'s MCP guidance already treats
  repository content generally; a Domain Concept or mapping candidate
  sourced from an external project's own prose is a *candidate* only,
  reconciled against primary evidence before acceptance, never auto-
  trusted (mirrors Phase 81's existing external-candidate discipline).
- **External source licensing and attribution** — named explicitly for
  Ledger/Beancount above (unverified); any future stage confirms licence
  compatibility for whatever it actually reads or redistributes before
  doing so, matching this project's own existing `decisions/0053`
  precedent for Ledgerkit/hledger.
- **Leakage of private project knowledge** — a mapping dataset published
  by a third party, or a project snapshot shared across an
  organisational boundary, must not leak either side's private/
  unpublished knowledge records; Stage 1's own export format must
  support an explicit, honest "excluded, not merely absent" marker for
  withheld records, not silently omit them in a way indistinguishable
  from "this project has no such record."
- **Premature accounting-specific coupling** — mitigated structurally:
  nothing in `decisions/0079`'s Layer A/B/C design or the project-
  identity envelope names accounting; Stage 7 exists specifically to
  test this claim against a real counter-example.
- **Visualisation giving unsupported claims apparent authority** —
  Stage 6's own exit gate is specifically a test of this risk, not an
  assumption it's handled.
- **Snapshot authority confusion** (added 2026-10-21, `decisions/0080`
  §3) — a third-party-generated snapshot (e.g. CodeCompass's own
  reconstruction of hledger, Stage 2) mistaken for knowledge the
  described project's own maintainers produced or endorsed. Mitigated
  by the project-identity envelope's `authority` field defaulting to
  `unknown`/`third-party-reconstruction` and never silently defaulting
  to `self-published`; Stage 6's Wiki is required to display `authority`
  wherever it displays the mapping/snapshot itself, not only on request.

## Explicit non-goals (unchanged by any stage above)

Per the governing prompt's own list: no global canonical database
replacing project ownership; no complete universal accounting ontology;
no accounting runtime inside CodeCompass; no new agent scheduler
(`CLAUDE.md` §8's fixed point, unaffected); no full Haskell adapter as a
side effect of this track; no visual Wiki built by this track alone
(Stage 6 depends on, does not replace, that separately-scheduled track);
no production natural-language accounting model (Stage 5 informs, does
not build, one).

## What must be designed now vs. deferred

**Designed now** (this document plus `decisions/0079`/`decisions/0080`):
the three-layer model, the project-qualified reference envelope shape
including the `publisher_id`/`authority` distinction, the mapping
record's field list and relationship-type enum, the five-value
verification-status taxonomy, the invalidation boundary rule, the
hledger evidence-sourcing approach (Stage 2), the design/empirical split
(Stage 5), the accounting-generalisation/domain-independence split
(Stage 7), and this stage sequence with its gates.

**Deferred** (no design work done, intentionally): the exact JSON
schema/file format for Stage 1's export (a schema sketch exists in
`decisions/0079` §5/`decisions/0080` §3; the binding schema is Stage 1's
own deliverable); which specific hledger/Ledger functions Stage 2/3 will
compare (decided against live test coverage at that stage's own planning
time); any Wiki visual design (Stage 6, explicitly out of scope here);
the natural-language intent grammar itself (Stage 5's own schema, though
now scoped as design-only); the empirical NL-comparison stage Stage 5's
correction named but did not number.
