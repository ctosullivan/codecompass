# 0072. The Phase 81 reconciliation loop adds zero new persisted fields
to canonical records; concurrency uses two independent hashes, never
one compared across representations

## Status

Accepted (Phase 81, 2026-10-07, direct user request, following two
same-day amendments to the Phase 81 plan).

## Context

Phase 81's own planning went through three designs for how a knowledge
record's reconciliation state should be tracked:

1. **Original draft**: a persisted `provenance_dimension` field
   (`OBSERVED`/`DECLARED`/`DECIDED`/`DERIVED`/`HISTORICAL`) plus a
   persisted `reconciliation_state` field (`CONFIRMED`/`INTENT_ONLY`/
   `CONFLICT`/`UNVERIFIED`/`STALE`) on Claim/Requirement.
2. **First amendment**: dropped `provenance_dimension` as redundant with
   the existing `basis`/`status` fields, computable at render time
   instead; retained `reconciliation_state` as a genuinely new field.
3. **Second amendment (this decision)**: on closer analysis,
   `reconciliation_state` is *also* unnecessary. Every value it was
   meant to carry is already fully expressible via Phase 54c/79's
   existing `status`, `evidence_support_state`, `basis`, and
   `contradicting_evidence` fields:

   | Proposed value | Already expressed by |
   |---|---|
   | `CONFIRMED` | `status: supported`/`verified`, reached only through the existing evidence-gated promotion discipline |
   | `INTENT_ONLY` | `status: proposed` with `basis: proposed_policy` |
   | `UNVERIFIED` | `status: proposed` with `evidence_support_state: unsupported` |
   | `CONFLICT` (a record's own evidence disagrees) | `status: contradicted` + `evidence_support_state: conflicting` + the existing `contradicting_evidence` citation |
   | `CONFLICT` (two separate records disagree, e.g. declared intent vs. observed reality) | A disconfirming Evidence record, cited from the `DECLARED` record's own `contradicting_evidence` — no new relationship type |
   | `STALE` | Never persisted — derived mechanically, the same way `check_snapshot_current_divergence` already detects drift for a frozen snapshot |

   `contradicting_evidence` and Claim-`supersedes` had, by the project's
   own documentation, never once been exercised with real content across
   the whole corpus before Phase 81 — this reconciliation loop is their
   first genuine exercise, rather than a reason to add a parallel field
   instead of using them.

A related, independent correction concerns concurrency identity. The
first amendment proposed a single BASE/CURRENT/EDITED hash per anchor —
but this compared a canonical YAML record's own content hash directly
against a rendered Markdown block's own content hash: two different
representations of the same knowledge that will almost never byte-match
even when nothing meaningful changed, since rendering reformats the
content (headings, citations, status lines, cached presentation
wording). That comparison could never actually answer "was this
edited."

## Decision

**Zero new fields are persisted on any canonical record for Phase 81.**
The governing distinction: canonical records describe what the project
knows, intends, requires, and why; the reconciliation manifest alone
(`planning/knowledge/<slug>/reconciliation/*.toml`, a new, non-canonical
artefact) describes the lifecycle of a *proposed edit* — `pending`,
`presentation_only`, `semantic_candidate`, `concurrent_conflict`,
`reviewed`, `accepted`, `rejected`, `applied` — and is never written
onto a `.yaml` record.

Concurrency uses **two independent baseline hashes per rendered block**,
each compared only against its own kind of current value:

```
canonical_changed  = current_semantic_hash   != base_semantic_hash
projection_edited  = current_projection_hash != base_projection_hash
```

`base_semantic_hash`/`current_semantic_hash` hash the canonical record's
own full raw file text (the same method `check_snapshot_current_divergence`
already uses for drift detection). `base_projection_hash`/
`current_projection_hash` hash the rendered Markdown text strictly
between a block's own anchor markers. The two are never compared against
each other.

A further, related invariant closed in the same amendment: a Requirement
must cite a real, already-`approved` Decision via its actual schema
field, `decision:` (not `authorised_by`, which does not exist in the
real schema) — enforced by a new fail-closed validator check,
`check_requirement_cites_approved_decision`
(`scripts/check_knowledge_base.py`), verified safe against all nine
pre-existing Requirement records.

## Consequences

- `scripts/check_knowledge_base.py`'s schema surface is unchanged except
  for two new `assertion_kind` enum values (`workflow`, `constraint`)
  and one new cross-reference check — no migration of existing records
  is ever required.
- A record written through `knowledge apply` is schema-indistinguishable
  from one authored any other way; `check_knowledge_base.py`'s existing
  fail-closed checks validate it with no special-casing.
- If real dogfood experience later proves this vocabulary too coarse for
  some genuine reconciliation case, the correct response is a new,
  separately-justified ADR proposing exactly the one irreducible field
  that case demonstrates is needed — not a speculative reopening of this
  decision, and not a silent schema change.
- The dual-hash concurrency model is the one genuinely novel mechanism
  Phase 81 introduces (see `planning/phase-81-intermediate-knowledge-layer.md`
  §1.5/§8) — bidirectional Markdown↔record reconciliation with
  concurrent-edit safety does not exist anywhere else in CodeCompass.
