# `domain-skeptic` review — Phase 63D domain reconstruction

Independent adversarial review of the draft `docs/domain/` corpus (19
concept pages) and its supporting 135+ records under
`planning/knowledge/codecompass-domain/`, per this role's charter
(`planning/phase-63d-domain-reconstruction.md` §4,
`planning/v1-redefinition/agent-led-development.md` §2.13,
`decisions/0060`).

## What was checked

- All 19 concept pages read in full: `evidence.md`, `observation.md`,
  `claim.md`, `derivation.md`, `decision.md`, `requirement.md`,
  `invariant.md`, `provenance.md`, `context.md`, `context-packet.md`,
  `relationship-edge.md`, `reference.md`, `digest.md`, `adapter.md`,
  `connector.md`, `protocol.md`, `vendor.md`, `ecosystem.md`,
  `capability.md`.
- Every internal `docs/domain/concepts/*.md` cross-link resolves (`grep`
  over all `](*.md)` links against the real file list — no broken
  links).
- `python scripts/check_knowledge_base.py` and
  `python scripts/check_user_docs.py --strict` both run directly.
- Direct source reads, independent of the concept pages' own prose, for
  every claim spot-checked below: `src/codecompass/graph.py` (schema,
  including the enrichment tables and edge tables),
  `src/codecompass/adapters/{base,external_process,haskell}.py`,
  `src/codecompass/enrichment.py`, `src/codecompass/sync.py`,
  `decisions/0054`, `decisions/0058`, `.gitmodules`,
  `tests/test_graph.py`, `scripts/check_knowledge_base.py`,
  `planning/context-observations/{inbox.md,TEMPLATE.md}`.
- `git log`/`git show`/`git ls-remote` investigation of the
  `decisions/0058` adapter/adaptor naming drift (item 1 below).
- Spot-checked underlying YAML records (`CL-ADPT-008`, `EV-ADPT-008`,
  `DE-ADPT-008`, `CL-EVID-002`, `EV-EVID-010`, `EV-ADPT-009`,
  `OBS-ADPT-009`) against the concept pages that cite them, and against
  the real source/decision content those records themselves cite.

## What I resolved myself

### 1. `decisions/0058` "adapter"/"adaptor" naming drift — resolved, not a genuine ambiguity

`protocol.md`'s `CL-ADPT-008` (status: `contradicted`) correctly
identified the drift but explicitly declined to determine which
spelling is canonical, deferring it. I investigated further and it
resolves cleanly:

- `git log` on `decisions/0058-*.md` and `.gitmodules` shows exactly one
  commit touches each, never renamed afterward. `decisions/0058`'s own
  commit (`886dc6e`, 2026-09-19 09:29:33 +0800, "adapter" spelling
  throughout) predates the commit that actually created and checked out
  the two real repositories (`41bae25`, 2026-09-19 14:29:49 +0800,
  "feat(phase-60): minimal external Haskell adapter") by five hours,
  same day, same author.
- `git ls-remote` against the real GitHub URLs confirms both
  "adaptor"-spelled repositories (`codecompass-adaptor-protocol`,
  `codecompass-adaptor-haskell`) are real, live, public repositories
  with genuine commit history and a real `v0.1.0` tag each. The
  "adapter"-spelled URL `decisions/0058`'s prose would imply
  (`codecompass-adapter-protocol`) returns the same generic
  credential-prompt failure a deliberately-fabricated, never-registered
  URL produces under identical anonymous-git conditions (confirmed by
  running the fabricated-URL control) — indistinguishable from "never
  created," not from "exists and is reachable."
- Every downstream artifact (`.gitmodules`, the real checked-out
  submodule directory, every module docstring in
  `base.py`/`external_process.py`/`haskell.py`) has used "adaptor"
  consistently since the single commit that introduced them.

**Conclusion**: this is a simple, pre-implementation drafting typo in
`decisions/0058`'s own prose (written before the real repositories it
describes existed), not a live product ambiguity about which spelling
the project intends. The real, functioning, pinned repositories this
project actually depends on are unambiguously "adaptor"-spelled. New
Observation/Evidence produced: `OBS-SKEP-001`, `OBS-SKEP-002`,
`EV-SKEP-001` (`planning/knowledge/codecompass-domain/`). **Handoff, not
mine to do**: `context-researcher` should write a new Claim that
`supersedes: CL-ADPT-008`, stating the "adaptor" spelling as the current
intended meaning and citing `EV-SKEP-001`; separately, whether
`decisions/0058` itself warrants a corrective/errata ADR entry (ADRs are
append-only, `CLAUDE.md` §2) is an editorial call for whoever owns
`decisions/*.md` — not something a Claim record or this role settles.

### 2. `OBS-NNN` id-prefix collision (`observation.md`, `CL-EVID-002`) — confirmed real, correctly not escalated

Directly confirmed both sides: `planning/context-observations/TEMPLATE.md:6`
literally uses `### OBS-NNN` as its own entry heading, and
`planning/context-observations/inbox.md` has real entries titled
`OBS-016`, `OBS-015`, `OBS-014`, etc. — a genuine textual collision with
Phase 54c's `OBS-<feature>-NNN` prefix, confirmed structurally distinct
in field shape (`EV-EVID-010`). This is correctly characterized as a
documentation cross-reference gap, not a genuine ambiguity — nothing
about *meaning* is actually unclear, only that neither directory's own
README warns a newcomer of the surface-level collision. No escalation
needed. (Recommended, not mine to do: a one-line cross-reference note in
each directory's own README — a documentation-polish item, not a domain
question.)

### 3. Two disclosed implementation gaps — confirmed accurate, routed as learnings candidates, not domain open questions

Both independently re-verified by reading the real source directly, not
trusting the concept pages' own citations:

- **`symbol_enrichment` has no provenance column at all**
  (`provenance.md`). Confirmed: `src/codecompass/graph.py:176-181`'s
  `CREATE TABLE symbol_enrichment` has exactly four columns (`id`,
  `symbol_id`, `purpose`, `generated_at`) — no `model` column, unlike
  `vendor_enrichment`/`doc_relation_enrichment`, which both have
  `model TEXT NOT NULL`. Independently confirmed `decisions/0054`'s own
  claim that all three enrichment tables uniformly distinguish producers
  "using a column that has existed since Phase 14" is **factually wrong
  for `symbol_enrichment` specifically** —
  `graph.record_symbol_enrichment` (`graph.py:1545-1556`) has no `model`
  parameter anywhere in its signature or its `INSERT`. `provenance.md`'s
  characterization is accurate.
- **The external protocol's wire-level `ecosystem` field and
  `capabilities` list are received but never validated against their own
  closed sets** (`ecosystem.md`, `capability.md`). Confirmed by grep:
  `ExternalAdapterProcess.ecosystem` (`external_process.py:51,83`) is
  assigned from the wire response and never read anywhere else in
  `src/codecompass/adapters/*.py` or `sync.py`. `self.capabilities =
  tuple(response.get("capabilities", []))` (`external_process.py:84`)
  performs no membership check against the closed 4-value set.

Both are real `src/codecompass/` gaps, correctly out of this phase's own
scope to fix. **These are implementation-gap candidates for
`planning/learnings/inbox.md`, not domain-corpus open questions** — the
domain *meaning* of "provenance"/"ecosystem"/"capability" is not in
question; the code simply doesn't yet enforce what the spec/design
implies it should. I have not written to `planning/learnings/inbox.md`
myself (outside my write boundary) — flagging here for the lead/
`knowledge-curator` to file.

### 4. Six disclosed terminology-looseness findings — judged, not escalated

For each, I looked for a current behavioural consequence (a place where
the looseness actually causes a wrong decision, a broken test, or
inconsistent code) and found none in every case. All six are correctly
disclosed, evidence-complete, and belong in `docs/domain/open-questions.md`
as open questions once that file exists (see Structural gap, below) —
none rises to a genuine ambiguity needing the user now:

- **Five senses of "context"** (`context.md`) — an umbrella-word
  looseness with no single mechanism it's blocking; the project's own
  closest-to-canonical statement (`ai-docs/README.md`) already treats
  "context graph" and "digest" as separate coordinate nouns, consistent
  with, not contradicted by, the five-way split.
- **Three informal senses of "digest"** (`digest.md`) — nested, not
  contradictory (sense 2 is the persisted form of sense 1; sense 3 is
  one file within sense 2).
- **Whether "relationship" is one concept or six** (`relationship-edge.md`)
  — a taxonomy question; every table already works correctly regardless
  of how the question is answered.
- **Whether the three senses of "invariant" should be unified**
  (`invariant.md`) — a documentation-design question; no code or process
  currently depends on the three senses being reconciled.
- **Whether Claim/Derivation's observed 1:1 shape is a real invariant or
  an untested coincidence** (`derivation.md`) — nothing in the schema or
  `scripts/check_knowledge_base.py` forbids a future 1:many pairing;
  confirmed by reading the checker directly. No current record violates
  either reading.
- **The Stage E graph-level vs. file-based Evidence/Observation/Claim/
  Decision naming collision** — already explicitly named and deferred to
  a future phase in `planning/v1-redefinition/roadmap.md`; this phase's
  own concept pages correctly re-state, not re-litigate, an
  already-managed deferral.

## Structural gap found (not a domain-meaning finding, but blocks calling this phase done)

**`docs/domain/` currently contains only `concepts/` — none of
`README.md`, `glossary.md`, `invariants.md`, `examples.md`,
`open-questions.md`, or `references.md` exist yet**, though the phase
plan's own §3 layout requires all of them, and several concept pages
(`context.md`, `relationship-edge.md`, `invariant.md`) explicitly cite
`docs/domain/open-questions.md` as where their own disclosed fuzzy
boundary is supposedly recorded — a citation to a file that does not yet
exist. This is squarely a completion gap for `context-researcher`/the
lead to close before Phase 63D's own DoD can be met, not a domain
ambiguity, and not something I write myself (`docs/domain/` is part of
my read-only write boundary, approved corpus or not).

## Minor finding: inconsistent draft-status marker formatting across clusters

The three parallel `context-researcher` dispatches used three different
conventions for the required "DRAFT" status marker: the `EVID` cluster
uses real YAML frontmatter (`---\nstatus: DRAFT...\n---`); the `CTXT`
cluster uses an inline Markdown blockquote (`> **status: DRAFT...**`);
the `ADPT` cluster uses a bare, non-delimited `status: DRAFT` line under
the H1 (not valid YAML frontmatter at all). Purely cosmetic — no content
is affected — but worth normalizing to one convention before
publication, since a future mechanical check (e.g. `check_user_docs.py`
extended per this phase's own optional suggestion) would need to handle
all three or none would be checkable uniformly.

## Tooling gap found: `check_knowledge_base.py`'s per-feature-directory scope produces false positives against this phase's legitimate cross-feature citations

Running `python scripts/check_knowledge_base.py` reports 11
`knowledge-base-dangling-reference` findings against
`planning/knowledge/codecompass-domain/*.yaml`, e.g. `EV-CTXT-008`
citing `EV-DOCORIGIN-001`/`EV-DOCORIGIN-008`. I checked every one of the
11 referenced ids directly: **all 11 are real, existing records** — just
in a different feature directory (`doc-origin-pinned-reference`,
`hledger-depth`, `haskell-api-surface-extraction`), cited intentionally
as this phase's own required "at least one concrete example"
(`phase-63d-domain-reconstruction.md` §2.2). The checker's
`check_cross_references_resolve`/`check_design_doc_citations_resolve`
were written for Phase 54c's original single-feature-directory model and
only look for a referenced id within the *same* `feature_dir` — an
assumption this phase's project-wide corpus, which deliberately cites
real examples from other features' knowledge folders, breaks. This is a
real, confirmed **false positive**, not a corpus defect — but it means
`check_knowledge_base.py` cannot currently be relied on to validate
`codecompass-domain/`'s own citations mechanically. Flagging for the
lead: either extend the checker to resolve ids against the union of all
`planning/knowledge/*/` directories (not just the current one), or
document this as a known, accepted checker limitation for
project-scoped corpora. Not something I fix myself (`scripts/` is
outside my write boundary).

## Escalations to the actual user/domain owner

**None.** Every finding above was either resolved with direct evidence
(item 1; new `OBS-SKEP-001`, `OBS-SKEP-002`, `EV-SKEP-001`), confirmed
as an already-correctly-disclosed non-escalation-worthy observation
(items 2, 4), or identified as an implementation gap/tooling gap/
structural completion gap outside this role's domain-ambiguity remit
(item 3, the structural gap, the tooling gap, the formatting
inconsistency). No genuine, unresolved domain/product ambiguity survived
real attempted resolution.

## New records written (this review's own write boundary)

- `planning/knowledge/codecompass-domain/OBS-SKEP-001.yaml`
- `planning/knowledge/codecompass-domain/OBS-SKEP-002.yaml`
- `planning/knowledge/codecompass-domain/EV-SKEP-001.yaml`

No Claim, Derivation, or Decision record written (outside this role's
write boundary, `decisions/0060`). No edit made to any
`docs/domain/concepts/*.md` page, any `src/codecompass/` file, or any
other approved/draft content.

## Recommended next actions (for the lead / `context-researcher` / `knowledge-curator`, not this role)

1. `context-researcher`: write a Claim superseding `CL-ADPT-008` citing
   `EV-SKEP-001`, resolving the adapter/adaptor question to "adaptor is
   the current intended spelling"; update `protocol.md`'s own
   counterexample section accordingly (this role does not edit concept
   pages).
2. Create the missing `docs/domain/{README,glossary,invariants,examples,
   open-questions,references}.md` files per the phase plan's own §3
   layout — several already-written concept pages cite
   `open-questions.md` specifically and it does not yet exist.
3. File the two confirmed implementation gaps (`symbol_enrichment`
   provenance column; unvalidated `ecosystem`/`capabilities` wire
   fields) to `planning/learnings/inbox.md` as future-improvement
   candidates.
4. Normalize the three clusters' differing DRAFT-status marker
   formatting to one convention.
5. Decide (lead's call, not a domain question) whether to extend
   `scripts/check_knowledge_base.py` to resolve cross-references across
   all `planning/knowledge/*/` directories, given this phase's
   legitimate cross-feature citation style, or document the limitation.
