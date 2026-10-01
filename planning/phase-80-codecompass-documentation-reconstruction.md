# Phase 80 — CodeCompass-wide documentation reconstruction + lightweight template refresh

**Status: approved, proceeding directly into implementation per direct
user instruction — no further planning round-trip.** Direct user
request, 2026-10-02. Full initiating prompt saved verbatim:
`planning/phase-80-documentation-reconstruction-prompt.md`. Builds on
and reuses Phase 79's own clean-room methodology
(`decisions/0066`/`0067`/`0068`) and its own established workflow
(`scripts/check_knowledge_base.py`, the frozen-snapshot format, the
isolation-tier labelling discipline) — this phase does not re-derive
that methodology, it applies it at project scope for the first time.

## 0. Scope, stated explicitly (read this first)

CodeCompass already has a mature, evidence-backed documentation corpus:
`README.md` (342 lines, including an 8-item honestly-disclosed
Limitations section from Phase 71), `docs/` (`cli-reference.md`,
`config-schema.md`, `quickstart.md`, `developer/`, `protocol-adapter/`,
and the already-approved `domain/` corpus — 19 concept pages, a
glossary, invariants, examples, open-questions, references, all traced
to real `planning/knowledge/codecompass-domain/` Observation/Evidence/
Claim/Derivation records, approved 2026-09-23 by the actual user/domain
owner), `architecture/` (7 files covering module map, schema, adapter
interface, sync pipeline, core data model), and `ai-docs/` (an
agent-oriented capability/boundary overview). This is **not** a
blank-slate project needing documentation written for the first time —
treating it as one would be wasteful and would risk silently discarding
already-reviewed, already-accurate material.

**What this phase actually does, concretely:**

1. Treats the existing `docs/domain/` corpus and `planning/knowledge/codecompass-domain/`
   records as primary input to a **freshness check**, not material to
   re-derive from zero — per the user's own explicit "reuse canonical
   knowledge records after checking their evidence and freshness"
   instruction. A record found still accurate is reused as-is, cited
   into the new frozen snapshot at its existing revision; a record found
   stale is re-derived for real.
2. Runs a genuine, fresh **model-blind implementation reconstruction**
   of CodeCompass's own core system — the CLI entry point and command
   surface, `sync.py`'s rebuild pipeline, `graph.py`'s schema, and the
   adapter pattern (`core.py`/the per-ecosystem adapters) — with zero
   access to any existing documentation, ADR, or the domain corpus. This
   is the genuinely new evidence-gathering activity this phase adds; the
   domain corpus's own prior research already covered the conceptual
   vocabulary (adapter/vendor/claim/evidence/etc.) in depth, but no prior
   phase has independently reconstructed "what does the system as a
   whole actually do" from primary implementation evidence alone, model-
   blind.
3. Compares the reconstruction against the (freshness-checked) knowledge
   foundation, surfacing any real drift between what the domain corpus
   says and what the code currently does.
4. Produces **one complete, freshly-structured documentation draft**,
   organized explicitly around the four named audiences (users,
   contributors, maintainers, coding agents) rather than inheriting the
   current file layout wholesale — committed to a staging location
   before any reconciliation step reads the existing active docs.
5. Reconciles the fresh draft against every existing active doc
   (`README.md`, `docs/**`, `architecture/**`, `ai-docs/**`), publishing
   the final result and removing or redirecting whatever the fresh
   structure supersedes.

**What this phase deliberately does not do**: it does not re-run
Phase 63D's own full project-wide Domain-stage research from scratch
(that already happened, was adversarially reviewed, and was approved by
the actual domain owner); it does not touch `src/codecompass/` (no
runtime/behavior change — this is Priority B territory, explicitly out
of scope); it does not touch Phase 78 (unchanged, untouched, per direct
instruction).

## 1. Two Phase 79 defects corrected first (same commit sequence, before this phase's own work)

Per direct user request, independently reproduced before fixing:

1. **Snapshot identity-absence gap**: `check_snapshot_completeness`'s
   identity/kind checks used a truthy guard (`if real_id and real_id !=
   expected_id`) that silently skipped validation when the historical
   content had no `id:`/`kind:` field at all — a committed, correctly-
   hashed, but completely unidentified file passed as if it correctly
   identified the record it claimed to. Reproduced in a disposable git
   fixture (an Assertion slot, then an Evidence slot, pointed at a
   plain, identity-less committed file with its own correct historical
   hash) — both produced zero findings against the unfixed code. Fixed
   by splitting each guard into an explicit "field absent entirely"
   check (new `knowledge-base-snapshot-identity-missing`/
   `-kind-missing` findings) and the existing "field present but
   different" check, generalized to the top-level assertion slot (which
   also gained a `kind` check it never had, and now checks historical
   content via `git show`, not the live file) and every nested
   `supporting_evidence`/`contradicting_evidence`/`derivation` entry.
2. **`template-usability-exercise-2`'s own ID-reuse explanation was
   overgeneralized**: `id-reuse-001`'s claim that reuse depends on
   "which task was most recently deleted and whether it held the
   current maximum id" was independently reproduced as false via both
   counterexamples named in the initiating prompt (`add 1,2,3 → delete
   2, then 3 → add` yields id `2`, not the rule's own predicted `3`,
   and id `3` is never reused in that sequence at all). A reference
   model tracking every id ever assigned (not inferring it from a
   single deletion event) confirms the real, simpler mechanism: one
   global `candidate = max(live ids)+1` (or `1`), reuse iff that
   specific candidate was ever assigned before — verified across 5
   independent sequences with zero deviation, then independently
   reviewed by a fresh dispatch explicitly tasked with trying to
   falsify it. Corrected via `id-reuse-002.md` superseding
   `id-reuse-001.md` (left with a dated correction notice, not
   rewritten), a new snapshot version, and corrected downstream
   documentation/packet — all inside `template-usability-exercise-2`'s
   own real git history (re-bundled afterward), not just a notice
   bolted onto the preserved evidence.

Full detail, evidence, and verification: see the actual commits (this
plan file doesn't duplicate the reproduction transcripts — they're
preserved as real evidence under
`planning/knowledge/first-party-source-symbols/template-usability-exercise-2/`
and in `tests/test_check_knowledge_base.py`).

## 2. Stage 1 — research + freshness review, frozen snapshot

**Freshness review** (not re-derivation): dispatch a fresh, independent
check of `planning/knowledge/codecompass-domain/`'s own existing Claims
against the current, live codebase — for each Claim, confirm its cited
evidence (file/line, test) still resolves and still shows what the Claim
says. A Claim found stale gets re-derived (this is a real,
evidence-gated decision, not a rubber stamp); a Claim confirmed still
accurate is reused as-is.

**New research**: for any of the named coverage categories (purpose,
concepts, architecture, installation, configuration, principal
workflows, CLI usage, source/dependency context, provenance,
limitations, extension points) not already backed by a real Claim
record, dispatch fresh research (full repository access, behavior-first
— run real examples before reading docs, per `context-researcher`'s own
standing charter) to produce one.

**Freeze**: once reviewed, freeze a new project-wide snapshot,
`codecompass-overview@v1.toml`, citing every Claim (reused-as-is or
newly-derived) this phase's documentation draft will cite — historical
git-blob hashes throughout, the same format `check_knowledge_base.py`
already validates.

## 3. Stage 2 — model-blind implementation reconstruction

Build an isolated export containing only primary implementation
evidence for CodeCompass's own core: `src/codecompass/cli.py`,
`sync.py`, `graph.py`, `core.py`, one representative adapter module, and
the real test files for each — explicitly excluding `README.md`,
`docs/`, `architecture/`, `ai-docs/`, `decisions/`, and
`planning/knowledge/`. Dispatch `implementation-reconstructor` (now
reliably dispatchable by name this session) against this export, with
no access to anything outside it. Mechanically verify its own isolation
afterward against its real transcript, the same way Phase 79's fifth
amendment did for the pilot topic.

## 4. Stage 3 — comparison

Dispatch a fresh `domain-skeptic` (comparison mode) to classify
alignment between the frozen snapshot and the model-blind
reconstruction. An `aligned` finding never by itself promotes a Claim's
own status. Any real conflict or gap becomes a named finding for Stage 5
to resolve, not silently smoothed over.

## 5. Stage 4 — fresh documentation draft, committed before reconciliation

Dispatch a fresh, isolated documentation-writing pass given only the
frozen snapshot (never the existing `README.md`/`docs/`/`architecture/`/
`ai-docs/`), instructed to select its own structure from what the
snapshot's own Claims actually are, organized around the four named
audiences. Commit the complete draft to a staging location
(`planning/v1-docs-reconstruction/phase-80-draft/`) before any
reconciliation step reads the existing active docs — the same
draft-before-reconciliation ordering Phase 79 established.

## 6. Stage 5 — reconciliation, publication, superseded-page cleanup

Dispatch `docs-maintainer` (legacy reconciliation mode) with both the
fresh draft and the real existing active docs, to classify every
existing claim (`supported`/`stale_or_contradicted`/
`rationale_requiring_verification`/`useful_example`/`obsolete`) and
produce the final, published structure — updating `README.md`, `docs/`,
`architecture/`, `ai-docs/` in place, and explicitly removing or
redirecting (a short "moved to X" stub, never a silent 404) any existing
page the fresh structure supersedes. `docs/domain/`'s own already-
approved corpus is reconciled, not replaced wholesale — a concept page
found still accurate keeps its own content; one found stale gets fixed
in place, following the corpus's own existing re-approval convention
rather than this phase inventing a new one.

## 7. Template refresh (lighter-weight)

Separately, in `codecompass-template`: a concise adoption `README.md`, a
small architecture/purpose page, and only essential workflow guidance —
consolidating overlapping instructions, with a short worked example.
Detailed evidence/drafts/audit records stay out of the everyday adoption
path (e.g. under a clearly-separate `evidence/` or similar directory,
not mixed into the top-level files a new adopter reads first). No
CodeCompass phase history, specialist-agent roster, or governance
ceremony imported. Validated via a fresh adopter exercise against both a
new and an existing project (preserving that project's own identity,
license choice, and existing instructions) — not by trusting the
template's own claims about itself.

## 8. Verification (both repositories)

- Frozen practical reader questions (CodeCompass and template,
  separately) answered independently from only the published docs,
  checked against primary evidence, with any factual error/omission/
  ambiguity fixed in the real published page.
- A bounded coding-context packet generated from the same CodeCompass
  snapshot, independently assessed by `context-evaluator` against real
  source — reported as a separate result from documentation accuracy,
  never merged into one verdict.
- Full test suite, `ruff`, both strict checkers (`check_knowledge_base.py`,
  `check_user_docs.py`).
- Independent `release-phase-auditor` completion audit; `roadmap-context-curator`
  terminal reconciliation.
- `planning/ROADMAP.md`/`CONTEXT.md`/`CHANGELOG.md`/retro reconciled with
  actual outcomes.
- Workflow-completion and strict-isolation verdicts reported separately,
  per Phase 79's own established discipline — isolation is expected to
  remain `best-effort`/`UNMET` for the same environment reasons already
  established; this phase does not re-attempt the Tier-1 preflight
  (already definitively failed, same environment).

## 9. Definition of done

Every condition in `CLAUDE.md` §5, applied to this phase: both defect
fixes merged and tested; the five-stage pipeline's own artifacts
(freshness review, frozen snapshot, reconstruction report, alignment
report, staged draft, reconciliation record) all real and committed;
published documentation live in both repositories; independent
verification (Q&A + coding-context packet, both repos' own fresh-adopter/
reader checks) complete and any finding fixed; full test suite and both
checkers clean; retro + learning triage + docs-drift audit + independent
completion audit + terminal reconciliation all complete; both
workflow-completion and strict-isolation verdicts reported separately
and honestly.
