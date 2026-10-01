---
role: domain-skeptic
mode: freshness reconciliation (Phase 80, Stage 1)
date: 2026-10-02
scope: all 28 Claim records backing the 19 approved docs/domain/ concept pages
---

# Phase 80 domain-corpus freshness review

## Method

For each Claim cluster (ADPT / CTXT / EVID), read every `CL-*.yaml`, resolved
every `source_ref`/`doc_ref`/`test_ref` in its `supporting_evidence` chain
against the **current working tree** (not the corpus's own word for its own
freshness), re-ran the cited test suites with `.venv/bin/python -m pytest`,
and grepped the corpus directly for the fragile-term-classes named in this
role's own brief (`Stage E`, `GATE DD`, Priority A–F). Then specifically
probed the three named post-approval change points (Phase 76 git-topology
tables, Phase 77 first-party source/symbol tables, Phase 79 Claim-schema
extension) for drift the corpus hadn't yet absorbed.

## Per-concept verdicts (19 pages)

| # | Concept | Verdict | Note |
|---|---|---|---|
| 1 | adapter | fresh (1 trivial citation drift) | `EV-ADPT-007`'s `architecture/overview.md:87-92, 344-359` citation has drifted — the "two senses of adapter" text now lives at lines ~63-67, and the "HOST-OUTPUT ADAPTERS" module-tier heading at ~165-188. Fact unchanged, confirmed still stated verbatim at the new location. |
| 2 | capability | fresh | `CL-ADPT-006`'s 4-value capability set confirmed against current `SCHEMA.md`; page's own Phase 74 fix (see concept 9 below) already reflected correctly in-page. |
| 3 | claim | fresh, with a real content gap | See "Phase 79 Claim-schema extension" below — not false, but incomplete against the current schema. |
| 4 | connector | fresh | Re-grepped `src/ docs/ architecture/ ai-docs/ decisions/*.md tests/` for "connector" — zero real hits outside this corpus's own pages and `decisions/0060`'s meta-reference to this research effort. MCP (Phase 25) still `deferred`, unstarted, confirmed in `planning/ROADMAP.md`. |
| 5 | context | fresh | Five-sense enumeration still accurate; sense 1's "vendors, symbols, usage, docs, and their edges" phrasing is non-exhaustive prose, not contradicted by Phase 76/77 additions. |
| 6 | context-packet | fresh | Gating/shape description unchanged; no Phase 76-79 change touches this mechanism. |
| 7 | decision | fresh | Decision-record model (`supersedes` only ever names a prior Decision) matches `decisions/0067`/`0068` (Phase 79), which follow exactly this pattern (new ADR, not in-place edit). |
| 8 | derivation | fresh | 1:1 Claim↔Derivation pairing still holds; the one deliberately-left-open question (#5 in open-questions.md) is unaffected. |
| 9 | digest | fresh | `VendorDigest` docstring and `vendor/typer/CLAUDE.md`'s real generated output both confirmed current. |
| 10 | ecosystem | fresh (record-level staleness carried from capability/protocol, see below) | |
| 11 | evidence | fresh | `CL-EVID-001`'s neutral-package model unaffected by any later phase. |
| 12 | invariant | fresh | Three-sense account (`learnings/`, design.md subsection, `invariants.md`) unaffected. |
| 13 | observation | fresh | No change to this mechanism since approval. |
| 14 | protocol | fresh | Page already correctly updated at Phase 74 (see below); SCHEMA.md re-checked directly, matches. |
| 15 | provenance | fresh | `CL-EVID-013` (superseding `CL-EVID-008`) already correctly reflects Phase 74's `symbol_enrichment.model` column; re-verified `graph.py:1583-1608`, `enrichment.py:427` directly. |
| 16 | reference | fresh | Three-sense account unaffected by any later phase. |
| 17 | relationship-edge | **stale — needs re-derivation (real content gap)** | See below. |
| 18 | requirement | fresh | Prior corrected file-path reference (noted in corpus `README.md` Status section) confirmed still correct. |
| 19 | vendor | fresh | `VendorConfig(name, ecosystem)` shape unchanged. |

**Summary: 17 of 19 fresh (one of those, "adapter," carries one trivial citation-line drift; "claim" carries a real-but-minor content gap, counted as fresh since nothing it states is false). 1 concept ("relationship-edge") is stale and needs re-derivation. 1 further cross-cutting record-level staleness (not a concept-page problem — the published pages are already correct) affects the ADPT cluster's own `CL-ADPT-009` record directly (concept 10, "ecosystem," and by extension "capability"/"protocol").**

## Real findings requiring action

### Finding 1 — `CL-ADPT-009` itself is stale and was never superseded, even though the published pages already reflect the fix (real record-level staleness)

`CL-ADPT-009`'s own statement asserts the external adapter protocol's wire-level
`ecosystem` field is "currently-inert" and that "nothing currently prevents an
external adapter from reporting an `ecosystem` string that disagrees with the
`Ecosystem` value CodeCompass configured it under, and no observed behaviour
would currently detect or surface that disagreement." This was true on
2026-09-23 but has been **false since Phase 74** (`L-032`,
`decisions`-adjacent, landed `050e366`): `ExternalAdapterProcess.initialize`
now takes a required `expected_ecosystem` keyword argument and raises
`AdapterError` on mismatch (`src/codecompass/adapters/external_process.py:53-98`),
with `HaskellAdapter._analyze` (the one production call site,
`haskell.py:184-195`) supplying the real `core.Ecosystem` value. Confirmed
directly by reading the current source and re-running
`tests/test_adapters_external_process.py` (`.venv/bin/python -m pytest` — 32
passed).

The published pages (`capability.md`, `protocol.md`, `ecosystem.md`,
`open-questions.md` item 10) were all correctly updated at Phase 74 by a prior
`domain-skeptic` pass, citing new evidence `EV-ADPT-011`/`EV-ADPT-012` and
observations `OBS-ADPT-018`–`020` (already on file). But that pass's own
retro (`planning/retros/_domain-skeptic-review-phase-74.md`) explicitly named
`CL-EVID-008` for `context-researcher` to supersede (which happened:
`CL-EVID-013` supersedes `CL-EVID-008`, 2026-09-27) but **never named the
exact analogous fix for `CL-ADPT-009`** — no retro, no later pass, and no
`CL-ADPT-011`/`012` file exists. This inverts this corpus's own stated
authority rule ("if this page and a cited record ever disagree, the record is
authoritative, and the page has a bug") for this one record: here the page is
right and the record is wrong.

**Not something I resolve myself** (write boundary — I cannot write a Claim).
**Name for `context-researcher`**: file a new Claim (e.g. `CL-ADPT-011`)
superseding `CL-ADPT-009`, using exactly the replacement text the Phase 74
retro already drafted for `ecosystem.md`'s Counterexample section, citing
`EV-ADPT-012`/`OBS-ADPT-018`–`020` (all already on file, no new research
needed — this is a mechanical supersession, not new investigation).

### Finding 2 — `relationship-edge.md`'s own "precisely six edge tables" Definition is now incomplete against Phase 76's git-topology schema (real content gap, not yet researched)

`relationship-edge.md`'s Definition states a "relationship," precisely, is
"a real, typed row in one of `context-graph.db`'s **six** edge tables," all
wiped and reinserted by `rebuild_deterministic` on every sync — and uses
exactly that "current, mechanically re-provable fact, never a standing
record" property as the defining criterion distinguishing a real edge from
the two neighbouring things it explicitly excludes (an agent-suggested
relationship, an enrichment comment).

Phase 76 (`decisions/0063`, git-repository-topology) added three new tables —
`git_repositories`, `git_worktrees`, `git_submodules` — confirmed directly in
`src/codecompass/graph.py:251-287`. Two of these carry real foreign-key
relationships between typed entities exactly analogous in shape to an edge:
`git_worktrees.repository_id REFERENCES git_repositories(id)` and
`git_submodules.parent_repository_id REFERENCES git_repositories(id)`. I
confirmed directly (`graph.py:1024-1026, 1052-1054`) that all three tables are
**also** unconditionally `DELETE`d and reinserted by `rebuild_deterministic`
on every sync — the identical "current, mechanically re-provable, never a
standing record" lifecycle the page uses as its own defining test for what
counts as a relationship.

Grepped the entire `docs/domain/` corpus for `git_worktrees`, `git_submodules`,
`git_repositories`, and "Phase 76" — zero hits anywhere. No domain-skeptic
freshness pass ran against Phase 76 (only ordinary drift-audits:
`_drift-audit-phase-76.md`, `_audit-phase-76.md` — neither is a domain-corpus
freshness check). This is a genuine gap the corpus hasn't yet addressed either
way, not something I can resolve by inspection alone — it is a real
disambiguation question (is a `git_worktrees`/`git_submodules` row a
"relationship" in this page's own precise sense, just not named `*_edges`, in
which case the Definition's "six" undercounts and needs updating to name why
these are excluded if they should be; or is there a substantive reason git
topology rows are a structurally different thing — e.g. "self-describing the
project's own repository structure" vs. "connecting two first-class graph
entities a vendor/doc/symbol query would traverse" — that the corpus has
simply never stated).

**Name for `context-researcher`**: research whether `git_worktrees`/
`git_submodules` rows meet `relationship-edge.md`'s own stated criteria for a
"relationship," and either (a) extend the Definition's table list with a
stated reason these three are additional relationship rows outside the
`*_edges` naming convention, or (b) add an explicit "What this is NOT" entry
disambiguating git-topology rows from `context-graph.db` edges with a stated
rule, matching this page's existing treatment of the other two neighbouring
exclusions. This is a genuine product/documentation-design question I am not
positioned to settle by inspection alone (unlike Finding 1, which is a
mechanical supersession) — it needs real investigation of intent, not just a
citation fix.

### Minor, non-blocking: Phase 79 Claim-schema extension not yet documented on `claim.md`

Phase 79 (`decisions/0066`) added optional `assertion_kind`/`basis`/
`evidence_support_state`/`examples`/`counterexamples`/`depends_on`/
`open_questions` fields to the Claim record shape (confirmed directly in
`scripts/check_knowledge_base.py:159-194`), explicitly as an **optional**
extension ("Absent entirely for an ordinary feature-scoped Claim — no
existing record needs to gain any of these"). `claim.md` and `CL-EVID-003`/
`CL-EVID-012` describe the pre-Phase-79 schema only (status enum,
supersedes-only-a-Claim rule) and say nothing false, but no concept page
anywhere documents these new optional fields exist. Not treated as
"stale" (nothing it currently says is contradicted), but worth naming as a
real documentation-coverage gap for whoever next revises `claim.md` —
low urgency since no existing record in this corpus uses the new fields yet.

## Fragile-term-class grep (Stage E / GATE DD / Priority A-F)

Grepped the full corpus and `docs/domain/` for "Stage E" and "GATE DD"
directly (not just diff-touched files). Both remain live, unresolved terms
in `planning/v1-redefinition/roadmap.md` and `planning/ROADMAP.md` as of
today — GATE DD is explicitly still open (`planning/ROADMAP.md:56`,
`decisions/0062`'s own words: "GATE DD is not resolved by this decision").
The corpus's own prior self-correction (`CL-EVID-009`→`CL-EVID-011`,
`CL-EVID-003`→`CL-EVID-012`, both already correctly retiring the old "Stage
E" label in favour of "Priority B" per `decisions/0062`/`pre-v1-disposition.md`
§7) is itself still accurate — re-verified `pre-v1-disposition.md`'s own
Priority B disposition row directly. No new fragile-term staleness found.

## Documentation-coverage categories: what `docs/domain/` addresses vs. elsewhere vs. nowhere

| Category | `docs/domain/` | Elsewhere | Nowhere (gap) |
|---|---|---|---|
| Purpose | partial (concept pages explain *what things mean*, not *why the project exists*) | `README.md`, `ai-docs/README.md` ("What it is"/"What it does") | — |
| Concepts | **yes, this is its primary job** (19 pages + glossary + invariants + examples) | — | — |
| Architecture | no (explicitly out of scope — "answers what, not how," per its own README) | `architecture/*.md` | — |
| Installation | no | `README.md`, `docs/quickstart.md` | — |
| Configuration | no | `docs/config-schema.md` | — |
| Principal workflows | no | `docs/quickstart.md`, `docs/cli-reference.md` | — |
| CLI usage | no | `docs/cli-reference.md` | — |
| Source/dependency context | partial (adapter/ecosystem/vendor/digest pages explain the *concepts* behind it) | `vendor/<name>/` generated digests, `architecture/overview.md` | — |
| Provenance | **yes** (`provenance.md`, `evidence.md`, `decision.md`, etc. are evidence-backed treatments of this exact topic) | — | — |
| Limitations | no | `ai-docs/README.md`'s "What it does NOT do" section | — |
| Extension points | no (connector.md documents the *absence* of a plugin concept, not how to extend) | `architecture/overview.md`'s "Adding a new ecosystem means writing one adapter class" (also `adapters/base.py`'s own class docstring) | — |

No named category is entirely without real, evidence-backed coverage
somewhere in the repository; `docs/domain/` itself only ever claimed to own
"concepts" and "provenance" (per its own README's explicit scope statement),
and that claim held up under direct inspection.

## New Observation/Evidence records

None written this pass — every check either confirmed an existing citation
(trivial drift noted in place, no new record needed) or produced a finding
whose fix is a Claim-level action outside my write boundary (named above for
`context-researcher`, not resolved by a new Evidence record of my own).
