# Phase 66: Roadmap + context reconciliation — plan

**Status:** planned (2026-09-24).

**Stage G, third phase** (`planning/v1-redefinition/roadmap.md`). Gated
on Phase 65 completing — **done 2026-09-23, PASS**, unblocked. Not
gated on GATE DD (a separate axis, per `decisions/0056`).

## 0. What this phase is, and isn't

Per the roadmap's own Phase 66 entry: `roadmap-context-curator`
reconciles `planning/ROADMAP.md` and `planning/CONTEXT.md` against
actual project state, and every deferred/not-funded/conditional item is
clearly parked with a stated revisit trigger, not silently ambiguous.

This phase does **not** decide GATE DD (Phase 55's own job, a genuine
strategic decision reserved for the actual user) or fund/un-fund any
conditional work — it only confirms each already-made decision is
*accurately and legibly recorded*, and that nothing reads as
accidentally still-open when it's actually already resolved (or
vice versa). **No `src/codecompass/` change.**

## 1. Scope

### 1.1 `ROADMAP.md` full-table audit

Read every row. For each, confirm the status column matches reality
(cross-check against `git log`, the phase's own retro if one exists,
and its own plan file's Status line) — not just the recently-touched
rows from this session, the full table back to Phase 0. Specifically
verify:

- Every `done` phase has a retro at `planning/retros/phase-N-*.md` and,
  where applicable, an audit report.
- Every `deferred`/`not funded`/`CONDITIONAL` row states its own revisit
  trigger in plain language (Phases 24/25, 48, 50 already do this —
  confirm the wording is still accurate and current, not stale).
- Stage E (56–59) and GATE DD (55) are recorded as intentionally,
  legitimately open pending a decision that may never come before v1
  ships — not as an oversight or a silently-abandoned commitment. Cite
  the roadmap's own existing "if Stage D/E were skipped per GATE DD,
  Stage G runs against the Stage C product instead" text as the already-
  settled design for this case (`planning/v1-redefinition/roadmap.md`,
  Phase 64's entry) — this phase records that clearly, it doesn't
  re-litigate it.
- No row's own prose contradicts its own status column (the exact class
  of gap `L-034`/`L-038` both named — a status field flipped without
  the accompanying prose catching up, or vice versa).

### 1.2 `CONTEXT.md` compaction

**The real, substantial work of this phase.** `planning/CONTEXT.md` has
grown to ~2449 lines by appending each phase's own narrative to "What
was just completed" indefinitely, contradicting `CLAUDE.md` §4's own
explicit instruction ("Overwrite the current-state section each time —
don't append indefinitely") — flagged as a non-blocking observation by
Phase 65's own `release-phase-auditor` audit
(`planning/retros/_audit-phase-65.md`), a standing, multi-phase drift
this phase is the deliberate, planned place to fix (named in
`planning/CONTEXT.md`'s own "Next concrete step" at Phase 65's
closeout).

**Approach**: rewrite `CONTEXT.md` from scratch as a genuinely
current-only document. The full historical record is not lost —
`CHANGELOG.md` (every phase, categorized), `planning/retros/` (every
phase's own full retro + audit reports), and git log/history already
preserve it in full; `CONTEXT.md`'s own stated purpose (§4) is
session-resumption state, not a project history. The rewritten file
keeps:

- **Current phase + status**: what's actually true right now (Stage G
  in progress, Phases 60–65 done, 66 in progress, 67–70 ahead).
- **What was just completed**: 2–3 sentences, per `CLAUDE.md` §4's own
  literal instruction — not a running log of every phase since Phase 0.
- **Any decisions made that weren't already documented**: only
  genuinely still-live ones (e.g. GATE DD's own open status, the
  attribution-trailer correction) — not a re-narration of every
  already-closed decision from Stage A onward, which `CHANGELOG.md`/ADRs
  already own.
- **The next concrete step**: unchanged in spirit, just not padded with
  historical justification for steps already taken.

**What gets removed**: the phase-by-phase narrative history for every
`done` phase back through the project's start — each already has its
own retro (goal, delivered vs planned, lessons, process feedback) that
is the actual durable record of that phase, per `CLAUDE.md` §5's own
DoD requirement. `CONTEXT.md` re-narrating it a second time was always
redundant with the retro it sits alongside; the redundancy just
compounded silently for many phases before Phase 65's audit named it.

**What must not be lost**: any information that exists *only* in
`CONTEXT.md`'s own narrative and nowhere else (a retro, an ADR, or
`CHANGELOG.md`) — checked explicitly before deletion, not assumed safe.
Given this project's own established discipline (a retro exists for
every `done` phase, an ADR for every non-obvious decision), this is
expected to be rare, but the check is real, not skipped.

## 2. Dispatch strategy

1. **`roadmap-context-curator`**, given this plan: audit `ROADMAP.md`'s
   full table (§1.1) and produce a findings list (any stale row, any
   missing retro reference, any status/prose mismatch) — its own
   established role for exactly this kind of check.
2. **Lead**, informed by 1's findings: fix any real `ROADMAP.md` issue
   found, then do the `CONTEXT.md` rewrite (§1.2) directly — this is a
   judgment-heavy compression task (deciding what's genuinely still
   load-bearing vs. safely redundant with an existing retro), better
   suited to the lead's own direct work than a delegated summary, matching
   this phase's own "the lead does the compaction" framing above.
3. **A fork**, in parallel with 1, to cross-check: for every phase
   `CONTEXT.md`'s pre-rewrite text narrates that is *not* also covered
   by an existing retro/ADR/CHANGELOG entry, flag it before the lead's
   rewrite deletes anything — a genuine "don't lose information" safety
   check, not just trusting the lead's own read-through.

## 3. Files created/changed

- **`planning/ROADMAP.md`** — any stale row/status fixed per §1.1's
  audit findings (expected to be minimal; this table has been kept
  current phase-by-phase throughout this session).
- **`planning/CONTEXT.md`** — rewritten in full per §1.2.
- Standard closeout: `planning/retros/phase-66-roadmap-context-reconciliation.md`
  (retro — note: this phase's own retro is *not* subject to the
  compaction it performs on `CONTEXT.md`; retros are the permanent
  per-phase record `CONTEXT.md` is explicitly allowed to stop
  duplicating), `planning/retros/_drift-audit-phase-66.md` (per-phase
  drift audit — expected `NO DRIFT`, since no current-truth doc or
  `src/` is touched), `planning/retros/_audit-phase-66.md`
  (`release-phase-auditor`), `planning/learnings/inbox.md` (any
  candidates), `CHANGELOG.md`.

**Explicitly not touched**: `docs/`, `README.md`, `architecture/`,
`ai-docs/`, `src/codecompass/`, `decisions/*`, `CLAUDE.md`.

## 4. Verification

1. **`ROADMAP.md` accuracy**: every row's status independently
   re-confirmed against `git log`/retros, not just carried forward from
   this session's own recent edits.
2. **`CONTEXT.md` no genuine information loss**: the fork's own
   cross-check (§2 item 3) confirms nothing narrated only in the old
   `CONTEXT.md` and nowhere else was silently dropped.
3. **`CONTEXT.md` now complies with `CLAUDE.md` §4**: current phase +
   status, 2–3 sentence "what was just completed," next concrete step —
   checked directly against the file's own literal instruction, not
   just "shorter than before."
4. **Standard mechanical checks**: `python scripts/check_user_docs.py
   --strict` (checks internal links/ADR cross-references — a large
   `CONTEXT.md` rewrite risks breaking links other docs point at),
   `python scripts/check_knowledge_base.py`, full `pytest` (expect 623
   passed / 2 skipped, no `src/` change this phase).
5. **Per-phase drift audit**: confirm `NO DRIFT` (no current-truth doc
   touched; `planning/CONTEXT.md`/`planning/ROADMAP.md` aren't in that
   audit's own checked category per `documentation-lifecycle.md` §2.5,
   but the per-phase audit still runs as standard practice).
6. **Closeout**: retro, `knowledge-curator` learning triage,
   `release-phase-auditor` DoD pass.

## 5. Deferred (explicitly out of scope for this phase)

- Deciding GATE DD (Phase 55's own job).
- Funding/un-funding any conditional work (Stage E, Phases 48/50).
- Final self-dogfood + Ledgerkit + Stage F smoke-test re-confirmation
  (Phase 67).
- Any `src/codecompass/` change.
