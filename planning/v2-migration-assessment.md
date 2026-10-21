# CodeCompass v2 — compatibility, migration, and adoption-surface assessment

Direct user request, 2026-10-21, part of the v2 strategic realignment
(`decisions/0078`, `planning/v2-roadmap.md`). Covers the governing
prompt's §7 requirements for a compatibility/migration assessment,
`codecompass-template` implications, public API/MCP/schema versioning
considerations, and documentation maintenance requirements, consolidated
into one document since they are all instances of the same underlying
question — how v2 lands without breaking what v1 already shipped.

## Current v1 surface (what must not silently break)

- **CLI**: `codecompass` entry point (`src/codecompass/cli.py`),
  `sync`/`query ...`/`chat`/`discovery`/`undo` commands, published to
  PyPI as `codecompass-context` `1.0.0`.
- **`context-graph.db` schema**: currently at version "10" or later
  (confirmed not independently re-verified for this document — Phase
  82's own plan explicitly makes no schema change, so this number is not
  load-bearing here).
- **`planning/knowledge/<slug>/` canonical record format**: Observation/
  Evidence/Claim/Derivation/Decision/Requirement, consumed by
  `knowledge_intermediate.py` and `check_knowledge_base.py`.
- **`codecompass-template`**: a separate, MIT-licensed repository
  (`https://github.com/ctosullivan/codecompass-template`), populated at
  Phase 77, lightly re-documented at Phase 81B Amendment 4, currently
  unmodified since (`dff3f4d`, confirmed this session).

## Compatibility posture through Phase 82-85

**Additive only — now even more so after `decisions/0080`'s
correction.** Phase 82's only genuinely new schema surface is the
`oracle-contract.yaml`/`oracle-result.yaml` file pair (new files, not new
fields on any existing record). The epistemic dimension originally
proposed as a new `epistemic_source` field on Claim/Requirement records
was first corrected to an ordinal scale (still a new field,
`decisions/0079`), then found still conceptually wrong and **removed
entirely** (`decisions/0080`) in favour of a derived, read-time view
computed from fields Phase 81 already has — meaning **zero existing or
Phase-82-planned canonical record field changes at all**, an even
stronger zero-migration posture than the original proposal, matching
Phase 81's own "zero new persisted fields on any canonical record"
discipline exactly rather than only approximately. No `context-graph.db`
migration is proposed before Phase 83 at the earliest, and even then
only if real use demonstrates a genuine gap
(`conditional-generalisation.md`'s standing discipline).

**No CLI command is removed or changed in incompatible ways** by
anything in Phases 82-85. Phase 84's MCP server is a new, separate
surface alongside the existing CLI, not a replacement for it.

## Versioning considerations (Phase 84 onward)

- **MCP server**: versioned independently of the `codecompass` PyPI
  package's own SemVer, following whatever versioning convention the
  chosen MCP SDK itself establishes as idiomatic — decided at Phase 84
  planning time, not pre-committed here.
- **Oracle-contract/oracle-result schema** (Phase 82): the
  `manifest_schema_version`-style explicit version field convention
  Phase 81B's Amendment 5 just established for the clean-room manifest
  (`decisions/0077`) is the direct precedent to reuse — an explicit
  integer schema-version field on both new file formats from the start,
  even though Phase 82 only ever produces version 1 of each. Adding the
  field now costs nothing and avoids the exact "the field didn't exist
  for the first N documents" retrofit problem Phase 81B's Amendment 5
  had to correct after the fact.
- **Behavioural contract public interface** (what a downstream MCP
  client or external tool can rely on): not finalised until Phase 88's
  own "public contract, MCP and assurance-result interface
  stabilisation" deliverable — Phases 82-85 are explicitly allowed to
  change the contract/oracle schema shape as real use informs it,
  provided every change stays additive per the posture above. Phase 88
  is where backward-incompatible changes, if any are still needed, get
  made deliberately and documented, not where they are discovered.

## `codecompass-template` implications

- **No change required through Phase 85.** Phase 82-85 capabilities are
  internal to `codecompass`'s own package and this repository's own
  `planning/` conventions; nothing yet exists for a template adopter to
  use differently.
- **Phase 84 (MCP)** is the first point `codecompass-template` might
  reasonably gain a documented "how to point an MCP-capable agent at a
  CodeCompass-indexed project" section — scoped at Phase 84 planning
  time, not now.
  - **Phase 87 (external validation)** is where `codecompass-template`'s
  own onboarding content gets its first real adoption-level update
  under v2, informed by whatever friction the external-project trial
  actually finds — matching Phase 77's own precedent of writing the
  template from proven workflow shape, not speculative design.
- **Adoption levels (Advisory / Assurance / Governed autonomy,
  `v2-roadmap.md`)** should eventually be documented in
  `codecompass-template` as the three concrete ways a downstream project
  can opt in — but only once Level 2 (the v2 product target) is real
  enough to document honestly, i.e. no earlier than Phase 84/85's
  completion.

## Documentation maintenance requirements

- `docs/`, `ai-docs/`, and `architecture/`-equivalent current-truth
  documentation (`docs/architecture/overview.md` per the post-Phase-81B
  layout) describe **current state only** (`CLAUDE.md` §2) — none of it
  is touched by this planning pass, since nothing it describes has
  changed yet. Each of Phases 82-88 updates these in the same commit as
  its own implementation, per the existing same-commit doc-sync rule,
  exactly as every prior phase already has.
- `docs/development/clean-room-redocumentation.md` (Phase 81B) is
  unaffected — v2's own isolation reuse (Phase 86's optional source-
  blind arm) cites it rather than duplicating its content.
- No blank-slate documentation reconstruction is implied or scheduled by
  this roadmap — the clean-room reconstruction already completed
  (Phase 81B) stays the current, accepted documentation baseline for
  every Phase 82-88 doc update to build on incrementally, per
  `CLAUDE.md` §5's own distinction between per-phase drift audits and
  milestone-level full reconstruction.

## Cross-project overlay compatibility (amendment, 2026-10-21, `decisions/0079`)

Reviewed per direct user request: does anything in Phases 82-85's
planned schema preclude a future, generic cross-project semantic overlay
capability? **No existing or Phase-82-planned canonical record changes
as a result of this review.** Federation identity (`decisions/0079` §2)
is carried by a new, external, per-project **project-identity envelope**
— never injected into `REQ-`/`CL-`/`EV-`/`OBS-`/`DE-`/`DEC-` records
themselves. This is additive in exactly the same sense §"Compatibility
posture" above already establishes for the rest of v2: a project that
never exports a knowledge snapshot for federation is entirely unaffected,
and nothing about Phase 82's own schema needs a migration to become
federation-capable later — only a new, separate export step (Post-v2
Stage 1, `planning/post-v2-cross-project-overlay-backlog.md`) needs to be
built, whenever it actually is.

One Phase 82 schema correction *was* made by this same review (the
`epistemic_source` field's ordinal redesign,
`planning/phase-82-contract-and-evidence-foundation.md` §12) — found
independent of federation, surfaced by reviewing the field against this
amendment's own INTENDED/OBSERVED/VERIFIED separation requirement. A
same-day follow-on review (`decisions/0080`) found the ordinal redesign
itself still conceptually wrong and removed the field entirely in
favour of a derived view (§4/§13 of the Phase 82 plan) — an even
stronger additive posture than this paragraph originally described,
since there is now no new field on any existing record at all, only new
oracle-result files and new, read-only code. `decisions/0080` §3 also
extends the project-identity envelope itself with a `publisher_id`/
`authority` distinction (self-published vs. third-party reconstruction)
— still external to every project-local record, still deferred to
Post-v2 Stage 1's own implementation.

**`codecompass-template` implications, unchanged**: nothing in this
amendment adds template content — a federated overlay has no adopter-
facing surface before at least Post-v2 Stage 1 exists.

## Security/isolation posture carried forward

- MCP responses and any repository content a v2 capability retrieves are
  treated as potentially untrusted instructions (governing prompt §6),
  never auto-executed — the same trust-boundary discipline Phase 81B's
  broker protocol already enforces for the clean-room writer (a fixed
  `{system_prompt, messages} -> {output}` protocol with no syntax for a
  file path, shell command, or tool/MCP config) is the direct model for
  Phase 84's own MCP tool-result handling.
- No coding agent gains authority to redefine its own acceptance
  criteria at any point in Phases 82-88 — enforced structurally in Phase
  82 already (§5's oracle-contract tamper-detection check) and carried
  forward unchanged through Phase 84's MCP exposure.

## Summary

Through Phase 85, v2 is additive and non-breaking to every existing v1
surface; no migration is required for an existing `codecompass` user or
for `codecompass-template`. The first points requiring real
compatibility decisions are Phase 84 (MCP versioning, a new dependency's
licence compatibility) and Phase 88 (public interface stabilisation,
where any necessary breaking change is made deliberately). This
assessment itself requires no maintainer approval beyond what each
named phase's own plan will separately ask for — it recorded no new
commitment of its own.
