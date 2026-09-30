# 0066. Clean-room conceptual understanding is published directly into documentation from one shared, correctly-schemaed knowledge foundation, isolated by a verified mechanism, not prompt discipline alone

## Status

Accepted (2026-09-30, direct user instruction). **Amended in place,
same date, second revision, direct user instruction.** Not yet acted
upon by any implementation (Phase 79 remains planning-only), so this is
a pre-implementation correction, not a reversal of shipped work — edited
directly rather than superseded by a new numbered decision, consistent
with `CLAUDE.md` §2's append-only rule applying to decisions that have
already informed real, executed work. The amendment corrects six things
found wrong or missing in the first version, listed in the Context
section below; the Decision section reflects the corrected design
directly rather than layering an addendum on top of stale text.

## Context

`decisions/0060` formalized Scope → Plan → Domain → Design → Implement
and, at its Domain stage, built a real, working mechanism: `context-
researcher` derives Observation/Evidence/Claim/Derivation records from
evidence; `domain-skeptic` adversarially reviews them; the actual user/
domain owner approves a `docs/domain/` corpus (Phase 63D). Phase 64 then
derived a "blank-slate" documentation proposal from current project
reality, explicitly instructed (in its own dispatch prompt and in
`.claude/agents/docs-reconstructor.md`'s MODE 2 section) not to treat
`README.md`/`architecture/overview.md` as a starting structure.

Direct inspection of what Phase 64 actually built finds a real,
previously-undiagnosed gap: **the "don't read the old docs" instruction
was never mechanically enforced.** `docs-reconstructor` MODE 2's own
dispatch retains full `Read`/`Grep`/`Bash` access to every file in the
working tree; `agent-led-development.md`'s own write-boundary table
states `context-researcher`'s read scope as "everything" — no boundary
beyond the role's own stated methodology.

Separately, no phase to date has performed a genuinely **independent
implementation reconstruction** — recovering the as-built architecture
from primary evidence *before* consulting any conceptual model, then
classifying alignment against it in both directions.

**This decision's first version (2026-09-30) addressed both gaps but
itself contained six real defects**, found and corrected the same day,
also by direct user instruction, before any implementation began:

1. It invented a separate `understanding-review.md` artifact gated on a
   human-review event, contradicting the corrected objective that
   conceptual understanding should be published directly into project
   documentation, auditable by its own evidence citations, without a
   human-acceptance precondition.
2. It risked describing a parallel, documentation-only assertion store
   rather than making explicit that one shared knowledge foundation
   (the existing Observation/Evidence/Claim/Derivation records) must
   feed both a coding-context packet and topic-level documentation.
3. **It stated the wrong `Claim` status enum** — `current`/`superseded`
   — when the real, mechanically-enforced enum
   (`scripts/check_knowledge_base.py::_STATUS_ENUMS["claim"]`) is
   `proposed`/`supported`/`contradicted`/`superseded`/`verified`. It also
   proposed a mandatory `human_review_state` field, which the corrected
   design removes along with the review gate itself, and it did not
   scope checker changes or require `check_knowledge_base.py --strict`.
4. **It substantially overclaimed its own isolation mechanism.** A
   curated, `.git`-free export with an undisclosed source path is input
   packaging, not enforcement — the `Read` tool's own documented
   behaviour ("able to read all files on the machine") means an agent
   granted that tool is not stopped by a withheld path. No preflight
   test verified this before trusting a stage's output, and no indirect-
   leakage channel (a synced `context-graph.db` embedding narrative doc
   content; a real, confirmed editable install of `codecompass` that
   resolves to the actual checkout regardless of an export's own working
   directory; auto-loaded `CLAUDE.md` content; inherited conversation
   context via a `fork`-type dispatch) was checked.
5. It left `docs-reconstructor`'s old, unrestricted MODE 2 as a silent
   fallback whenever a topic's own prerequisites were missing, and had
   the lead (not a fresh, isolated dispatch) author the documentation-
   architecture outline. It also left the clean-room draft as a
   permanent shadow proposal rather than publishing the reconciled result
   into real, active project documentation.
6. Its template deliverable list still included the removed
   understanding-review/review-decision templates and had no coding-
   context-selection template, despite coding packets now being a
   co-equal derived output.

Direct user instruction (2026-09-30, second revision): correct all six,
consistently, throughout the ADR, the phase plan, and related planning
notes. Full specification:
`planning/phase-79-clean-room-understanding-and-documentation-reconstruction.md`.

## Decision

1. **Reuse the existing Claim record shape, extended with optional
   fields, using the real status enum — no new record kind, no new
   database, no graph subsystem.** `planning/knowledge/<topic-slug>/`
   Claim records keep their real, unmodified `status` lifecycle
   (`proposed`/`supported`/`contradicted`/`superseded`/`verified`) and
   gain optional `assertion_kind`
   (`definition`/`relationship`/`rule`/`invariant`/`state_transformation`/
   `boundary`), `basis`
   (`directly_stated`/`inferred`/`proposed_policy`/`observed_behaviour`),
   `examples`, `counterexamples`, `depends_on` (assertion IDs —
   validated by the existing, already-generic
   `check_cross_references_resolve` with no code change), `open_questions`,
   and a qualitative `evidence_support_state`
   (`supported`/`partially_supported`/`unsupported`/`conflicting`, never
   a number). **No `human_review_state` field** — there is nothing a
   human must act on before a record is usable. `Observation`/`Evidence`/
   `Derivation` are unchanged. `scripts/check_knowledge_base.py` gains one
   new, small closed-enum validator for the three new enum-shaped fields
   above (mirroring its existing `check_status_enums`); `--strict` passing
   is a Definition-of-Done condition.

2. **One shared knowledge foundation feeds two derived outputs — a
   task-specific coding-context packet (Phase 54c's existing mechanism,
   unchanged) and topic-level documentation (this decision's own
   contribution) — never a second, parallel store.** A documentation-time
   discovery becomes a canonical Observation/Evidence/Claim record before
   it appears in either derived output. Documentation prose is never
   itself treated as evidence for a claim — provenance always traces back
   through the record to its original source.

3. **Conceptual understanding is published directly into project
   documentation — no separate review-gated packet, no human-acceptance
   precondition for publication.** Definitions, relationships, rules,
   invariants, transformations, examples, counterexamples, assumptions,
   alternative interpretations, and unresolved questions are written into
   the topic's own documentation page, with source coverage and evidence
   citations inline so a reader can audit the understanding directly.
   `domain-skeptic`'s adversarial review (unsupported claims, internal
   contradictions, missing counterexamples) is retained — an agent-level
   quality check, not a human-approval gate. Any existing page-level
   review-metadata convention (`docs/domain/`'s own Phase-63D-era
   frontmatter) is preserved where it already exists and is not required
   of this phase's own new content. This does not relax this repository's
   ordinary planning/ADR review conventions (`CLAUDE.md` §0-§2), which
   this decision and its own phase plan continue to go through unchanged.

4. **Mechanical isolation uses a verified, tiered enforcement mechanism,
   with curated `.git`-free exports demoted to input packaging.** Tier 1
   (preferred): `Agent(isolation: "remote")`, a genuinely separate
   environment with no shared filesystem — used only after a preflight
   denial test (attempt to read a known-excluded absolute path; confirm
   failure) confirms it actually works, since its availability is gated
   and not assumed. Tier 2 (fallback): the curated export, on the same
   host, with the narrowest tool-category grant each role's job allows
   (no network tools, no `Agent`, per-role `.claude/agents/*.md`
   frontmatter — a genuinely enforceable boundary, unlike path-scoping
   within a granted `Read`/`Bash`) — every Tier-2 output is labelled
   `isolation: best-effort`, never `clean-room`, and "strict clean-room"
   acceptance is explicitly left unmet for that stage. A named
   indirect-leakage checklist is checked for every export: a synced
   `context-graph.db` (excluded — it structurally embeds narrative
   content from an ordinary `sync`), symlinks (dereferenced on copy),
   caches, a **confirmed** editable-install leak (`codecompass` resolves
   to the real checkout regardless of an export's own working directory
   — verified directly via `pip show`), auto-loaded `CLAUDE.md` content
   (each export gets a minimal, purpose-written one), and inherited
   conversation context (never a `fork`-type dispatch, never the lead
   itself, for an isolation-sensitive stage). A detected breach voids
   that stage's output and requires a fresh export and a fresh agent —
   never a retroactive claim that contamination "probably didn't matter."

5. **One new agent role, `implementation-reconstructor`**, unchanged from
   the first version: recovers the as-built architecture from the
   Implementation-reconstruction export alone, with no access to the
   published Understanding documentation at that stage. A **fresh**
   `domain-skeptic` dispatch (its own existing adversarial charter
   extended, not a second new role) classifies alignment
   (`aligned`/`partial`/`conflicting`/`not_implemented`/
   `insufficiently_verified`) against the published documentation, in
   both directions, without either side forced to match the other. An
   `aligned` finding is a legitimate basis for moving the cited Claim's
   own real `status` to `verified` — reusing the existing enum value
   rather than adding a new one.

6. **`docs-reconstructor`'s old, unrestricted MODE 2 is retired as a
   silent fallback.** The staged route (Understanding → Implementation
   reconstruction → comparison → a fresh, isolated dispatch that selects
   its own documentation architecture and writes the complete first
   draft → committed preservation → legacy reconciliation → publication
   into real, active documentation) is the **default** ground-up
   documentation path from this phase forward; a topic missing its own
   Understanding or Implementation-reconstruction prerequisite is a named
   blocker requiring those stages first, never a silent revert to
   unrestricted reading. `docs-maintainer`'s existing reconciliation
   charter (Phase 65's own precedent, no new role) gains the five-way
   historical-claim classification and a hard draft-before-reconciliation
   ordering rule, plus a requirement to fix (not merely record) a
   documentation-verification finding. `context-evaluator`'s existing
   charter is reused, unchanged, for that verification.

7. **Change propagation is minimal and file-based**: a `grep`-driven
   traversal from a changed source through Evidence, the affected Claim,
   its transitive `depends_on` dependents, and every citing coding
   packet or documentation page — no new dependency database. "Needs
   reassessment" and "proven incorrect" are distinguished explicitly. One
   explicitly labelled controlled test correction demonstrates
   propagation into both a coding-context artifact and a documentation
   page from the same underlying change — a real human correction is not
   required for this demonstration, but a synthetic one is never
   presented as if it were real or as human approval.

8. **This is not Priority B**, unchanged: `decisions/0062`'s Priority B is
   a future, not-yet-planned `src/`-level capability for a downstream
   user's own runtime project data. This decision and its phase make
   zero `src/codecompass/` changes — every artifact is a planning
   document, a `docs/domain/`/`docs/`/`architecture/` page, an agent
   brief, or a `codecompass-template` file.

9. **The template gets portable, CodeCompass-agnostic instructions and
   minimal templates** for shared knowledge/assertions, snapshots,
   writing conceptual understanding directly into documentation, coding-
   context selection, isolation (including the two-tier mechanism and an
   honest best-effort fallback for a project whose own tools cannot
   enforce it at all), implementation comparison, propagation,
   reconciliation, and documentation verification — the removed
   understanding-review/review-decision templates are not part of this
   list. Committed template files plus a fresh downstream usability
   exercise (not committed files alone) are required.

## Alternatives considered

- **Keep the first version's separate review-gated packet, only fix the
  schema and isolation defects.** Rejected per the user's own explicit
  revised objective: gating publication on a human-review event that may
  never occur was itself a defect, not a feature to preserve alongside
  the other fixes — the corrected design publishes understanding directly
  and audits it through its own evidence citations instead.
- **Treat curated `.git`-free exports as sufficient isolation, since they
  worked well enough as *input scoping* for the schema/role changes.**
  Rejected: this is precisely the overclaim the user's own review found —
  demoted to input packaging, paired with a verified tiered mechanism and
  a required preflight test, per Decision item 4.
- **Full OS-level sandboxing (containers, filesystem namespaces) for
  every dispatch, guaranteed present.** Rejected as still disproportionate
  to what this project's own tools can reliably build: `Agent(isolation:
  "remote")` is the strongest *available* primitive, and its own
  availability is gated, not guaranteed — the tiered design with an
  honest best-effort fallback is the most rigorous mechanism this
  environment can actually verify, not an aspirational claim of a stronger
  one.
- **A second new agent role for the implementation-vs-understanding
  comparison, instead of extending `domain-skeptic`.** Rejected, unchanged
  from the first version: `domain-skeptic`'s existing charter already
  generalizes to this job.
- **Fold this into Priority B's own future planning instead of a separate
  phase now.** Rejected, unchanged: this phase is methodology hardening
  plus a template deliverable, not a runtime capability of the shipped
  tool.

## Consequences

- Rewritten files: `planning/phase-79-clean-room-understanding-and-documentation-reconstruction.md`
  (full second revision), this decision record (amended in place), a new
  saved verbatim prompt file for this revision.
- `development-methodology.md` and `documentation-lifecycle.md`'s own
  forward-pointing amendment notes are updated to match the corrected
  design (no human-review gate; publication into real documentation; the
  corrected status enum).
- No `src/codecompass/` change. No `context-graph.db` schema change. No
  new database or graph subsystem.
- The phase's own implementation (the actual `.claude/agents/
  implementation-reconstructor.md` file, the extended `docs-reconstructor`/
  `domain-skeptic`/`docs-maintainer`/`context-researcher` operating modes,
  the `check_knowledge_base.py` checker change, the real dispatches, the
  real publication into `docs/domain/`/`docs/`/`architecture/` for the
  validation topic, and the `codecompass-template` additions) is that
  phase's own scoped work, not started by this decision, and requires its
  own plan-file review per `CLAUDE.md` §1 before implementation begins
  (already satisfied by the phase plan named above, rewritten in this
  same commit).
