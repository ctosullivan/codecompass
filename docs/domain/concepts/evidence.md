---
status: APPROVED (2026-09-23, actual user/domain owner, subject to corrections applied same day)
---

# Evidence

## Definition

An **Evidence** record (`EV-<feature>-NNN`) is a **neutral package**
describing what was found by one or more Observations, or by a direct
citation of source code, documentation, or a test. It states *what is
true about what was looked at* — never whether that finding supports or
contradicts any particular Claim. The same Evidence record can be cited
as `supporting_evidence` on one Claim and `contradicting_evidence` on a
competing Claim without being rewritten either way; the support/
contradict judgment lives only on the Claim (`CL-EVID-001`).

This is a **deliberate, dated design choice**, not the model's original
shape: `planning/phase-54c-evidence-knowledge-workflow.md`'s own
amendment note (2026-09-18, before any implementation) records that the
pre-amendment draft let Evidence itself carry a support/contradict tag,
and the user asked for it to be made "strictly neutral" instead
(`DE-EVID-001`).

## What Evidence is NOT

- **Not an Observation.** An Observation (`OBS-<feature>-NNN`) is the
  single act of looking; Evidence is the synthesized statement of what
  that act (or several) showed. One Evidence record cites one or more
  Observations via its own `observations:` field, or cites source/doc/
  test directly (`source_ref`/`doc_ref`/`test_ref`) when no discrete
  Observation exists to point at.
- **Not a Claim.** Evidence never says "this shows X is true about the
  feature"; it says "this is what was found." Interpretation —
  including which Claim(s) it supports or contradicts — is the Claim's
  own job, never the Evidence record's.
- **Not the informal, ordinary-English use of "evidence" already in this
  repository.** `decisions/0051` (Phase 43c, predates Phase 54c) speaks
  of "reviewable, provenance-carrying prose observations" and an
  "evidence trail" in `planning/context-gaps/` — a real, working
  mechanism, and a direct conceptual ancestor Phase 54c's own plan cites
  explicitly, but not built from this schema and not itself a `kind:
  evidence` record (`EV-EVID-001`, `DE-EVID-001`).
- **Not the graph-level "Evidence" entity kind** Phase 57's own
  candidate design sketches for `context-graph.db` (see "Relationships"
  below and `decision.md`'s matching section) — same word, a genuinely
  different, not-yet-built mechanism for a different purpose.

## Invariants

- **Evidence's own `status` field (`current | superseded`) carries no
  support/contradict meaning at all** — it is superseded only when a
  *later Observation* (e.g. at a newer pinned revision) shows the
  original finding no longer holds, never merely because a Claim built
  on it changed (`planning/phase-54c-evidence-knowledge-workflow.md`
  §2.2's own comment, confirmed against every real record,
  `EV-EVID-002`).
- Every real Evidence record found in this corpus cites at least one
  Observation, or a direct `source_ref`/`doc_ref`/`test_ref` — never
  both absent (`EV-EVID-002`).
- No Evidence record in the current corpus has ever actually been
  cited as `contradicting_evidence` on any Claim — the neutrality
  property is real and structurally checkable, but has never yet been
  exercised the "contradicts" direction with real content
  (`EV-EVID-004`; see Claim's own counterexample section for the fuller
  account).

## Example

`EV-DEPTH-001` (`planning/knowledge/hledger-depth/EV-DEPTH-001.yaml`)
states: "hledger's balance/register/accounts commands strip depth from
the query used to select/gather underlying postings and accounts, and
re-derive depth only afterward as a display-time clip/aggregate
operation; no posting or account is excluded from the computation" —
citing two Observations (`OBS-DEPTH-001`, `OBS-DEPTH-002`) and a direct
source citation
(`hledger-lib/Hledger/Reports/MultiBalanceReport.hs:205-238`). Nothing
in the record says "this supports CL-DEPTH-001" — that citation exists
only on `CL-DEPTH-001` itself, in its own `supporting_evidence` list.

## Counterexample / edge case

No real instance exists yet of the same Evidence record being cited as
`supporting_evidence` on one Claim and `contradicting_evidence` on a
*different, competing* Claim — the property the schema was explicitly
designed to allow (`phase-54c-evidence-knowledge-workflow.md` §2.2's own
comment: "The same Evidence record can be cited as supporting one Claim
and contradicting a different, competing Claim... without being
rewritten either way"). Every Evidence record produced under this model
to date has been cited as supporting exactly one Claim and contradicting
none. This is an honestly-untested part of the design, not a
disconfirmed one (`EV-EVID-004`).

## Relationships

- **Cites → Observation** (`observations:` field), or a direct source/
  doc/test citation when no Observation record exists.
- **Cited by → Claim** (`supporting_evidence`/`contradicting_evidence`)
  — the only direction a support/contradict judgment is ever recorded.
- **Distinct from, same-word collision with → the graph-level
  `Evidence` entity-kind candidate** named in Phase 57's Stage E design
  sketch (`v1-redefinition/roadmap.md`), which would represent
  provenance about *other projects'* technical dependencies inside
  `context-graph.db` — a queryable database row, not a file-based
  development-process record, and not yet built or funded
  (`CL-EVID-009`).
- **Thinner/different-shaped analogue → AI-authored graph enrichment**
  (`vendor_enrichment`/`symbol_enrichment`/`doc_relation_enrichment`).
  Enrichment content is also "what an AI found/produced," but it is a
  flat single-row value, never a chain of Observation→Evidence→Claim,
  and it describes an already-proven graph fact rather than a
  behavioural claim that may have no graph fact at all. Two of the
  three enrichment tables (`vendor_enrichment`, `doc_relation_enrichment`)
  carry one `model` provenance column each; `symbol_enrichment` carries
  none — see [`provenance.md`](provenance.md)'s own Definition/
  Counterexample for the full asymmetry, not restated here
  (`decisions/0054`, `EV-EVID-008`, `EV-EVID-014`).

## References

- `planning/knowledge/codecompass-domain/CL-EVID-001.yaml`,
  `DE-EVID-001.yaml`, `EV-EVID-001.yaml`, `EV-EVID-002.yaml`,
  `EV-EVID-004.yaml`, `EV-EVID-013.yaml`.
- `planning/phase-54c-evidence-knowledge-workflow.md:108-349` (the six
  record kinds, Evidence's own schema and neutrality comment),
  `:22-39` (the 2026-09-18 amendment note making Evidence neutral).
- Real example records: `planning/knowledge/hledger-depth/EV-DEPTH-001.yaml`
  through `EV-DEPTH-003.yaml`;
  `planning/knowledge/doc-origin-pinned-reference/EV-DOCORIGIN-001.yaml`.
- `decisions/0051-agent-suggested-context-is-captured-not-graphed.md`
  (the pre-Phase-54c, informal "evidence"/"observation" language).
- `planning/retros/phase-54c-evidence-knowledge-workflow.md:164-178`
  (the untested support/contradict-both-ways property, disclosed
  honestly).
- `planning/v1-redefinition/roadmap.md:1061-1087` (the graph-level
  naming-collision note).
