# Phase 87 Stage 87A — docs-reconstructor drift audit (2026-11-04)

Per-phase drift audit (not the milestone blank-slate reconstruction
mode) — independent, read-only, scoped to Stage 87A's own diff
(`a54be15`..`fe664b7`). Dispatched per `CLAUDE.md` §5's DoD requirement;
this file persists that dispatch's full report, which was originally
only relayed in-conversation and not saved to disk — an omission an
independent `release-phase-auditor` pass caught and required fixing
before Stage 87A's own DoD could be considered complete.

## Verdict

**DRIFT** — 1 non-blocking finding (fixed, see below); 1
explicitly-deferred (not-drift) item flagged for tracking; everything
else **NO DRIFT**.

## Scope and method

Verified against `src/codecompass/core.py`, `src/codecompass/sync.py`,
`src/codecompass/cli.py`, `scripts/compile_doc_section.py`,
`decisions/0085`, and current `README.md` / `docs/reference/cli.md` /
`docs/concepts/*.md` / `docs/development/clean-room-redocumentation.md`
/ `ai-docs/README.md`. This repository has no top-level `architecture/`
— it is `docs/architecture/`, also checked (no clean-room/broker
mentions there either way, before this stage's own new addition — see
below).

## Findings

1. **`README.md`'s "Understanding Digests" section — NO DRIFT.**
   Independently read `sync_vendor` in `src/codecompass/sync.py:107-207`
   directly rather than trusting the published text or the grounding
   citation's own prose. Every assertion checks out: `VendorDigest`
   combines deterministic file-tree/dep-tree/API-surface output (no AI
   call inside `sync_vendor`) with a read-only enrichment lookup
   (`_lookup_enrichment`, graceful no-op if no `context-graph.db`); it
   renders `DEPTREE.md`/`deptree.json`, `FILETREE.md`/`filetree.json`,
   `OVERVIEW.md` (conditional on `conversational_overview`),
   `CLAUDE.md`; and `sync_all`/`cli.py`'s `sync` command (lines
   294-320) call it unconditionally for every config on a whole-project
   sync. Matches `CL-CTXT-005.yaml` and the real code.

2. **`docs/reference/cli.md` does not document the new `codecompass
   docs schema-init/compile/publish/maintain` commands — NOT drift.**
   `decisions/0085` §5 explicitly reserves `cli.md`'s "accurate,
   deterministically generated" state for Phase 87's own closeout gate
   ("required before Phase 87's own closeout — not merely the
   demonstrator"), naming deterministic generation from the real Typer
   command tree as "this phase's own improvement opportunity, not
   assumed solved." `cli.md`'s own header makes no completeness claim.
   Flagged only so the lead tracks this explicitly toward the 87C
   closeout rather than losing track of it. **Resolution** (lead,
   same day, after this audit): a hand-written section for the new
   `docs` command group was added to `cli.md` anyway, matching this
   project's own established convention that every CLI group gets a
   documented section as it lands (confirmed: Phase 84's `knowledge`
   group has one) — `decisions/0085` §5's deferral is about the
   *generation method* becoming deterministic at 87C, not about the
   *content* going undocumented until then.

3. **`docs/concepts/knowledge-model.md` and
   `knowledge-placement-policy.md` — NO DRIFT.** No claim of "no
   compilation capability exists" is contradicted. The "not yet
   exposed through CLI" line in `knowledge-model.md` (line 31) concerns
   `derive_epistemic_profile`, a pre-existing Phase 82/84 matter
   unrelated to this phase's diff. `knowledge-placement-policy.md:22`
   already anticipated "Phase 87's compiled output lands here."

4. **NON-BLOCKING FINDING (fixed same day):**
   `docs/development/clean-room-redocumentation.md`'s "The broker,
   briefly" section and its trust-boundary framing described
   `cleanroom_broker.py` as reachable only from inside a verified Mode
   B namespace/`pivot_root` sandbox via `cleanroom_broker_client.py`.
   `scripts/compile_doc_section.py`'s `compose_section` calls
   `cleanroom_broker.run_inference` directly from the host process — a
   second, legitimate but structurally different (non-sandboxed)
   caller of the same broker. The doc did not state falsely that the
   sandbox path is exclusive, but was silent about this second caller
   — a reader using it to understand "how is the broker ever invoked"
   would get an incomplete picture. **Fixed** (commit `b81ace7`): a
   short note added explaining the deliberate, bounded exception and
   why it does not weaken Mode B's own guarantee.

5. **`ai-docs/README.md`, `docs/limitations.md`,
   `docs/open-questions.md` — NO DRIFT.** No stale "no documentation
   generation capability" claims found; "No dedicated documentation
   site" (`docs/limitations.md:36-38`) remains true, since publication
   still lands in the same `README.md`/`docs/*.md` tree.

## Not checked (no observable-behaviour claim implicated)

`README.md.schema.yaml`, `planning/knowledge/.grounding-state.toml`,
and the reconciliation/pending-review artifacts under
`planning/knowledge/codecompass-domain/reconciliation/` and
`planning/retros/phase-87-pending-review/` — pipeline state/schema, not
current-truth narrative docs. Test-file additions carry no docs
implications.

## Disposition

All findings closed same-day:

- Finding 4 (non-blocking): fixed, `b81ace7`.
- Finding 2 (explicitly deferred, not drift): `docs/reference/cli.md`
  given a hand-written section anyway (see Resolution above),
  reconciling the project's own documented-as-you-go convention with
  `decisions/0085` §5's deferral of the *deterministic-generation*
  improvement to 87C.

No remaining open drift from this audit.
