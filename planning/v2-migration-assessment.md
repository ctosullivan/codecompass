# CodeCompass v2 — compatibility, migration, and adoption-surface assessment

Direct user request, 2026-10-21, part of the v2 strategic realignment
(`decisions/0078`, `planning/v2-roadmap.md`). Covers the governing
prompt's §7 requirements for a compatibility/migration assessment,
`codecompass-template` implications, public API/MCP/schema versioning
considerations, and documentation maintenance requirements, consolidated
into one document since they are all instances of the same underlying
question — how v2 lands without breaking what v1 already shipped.

**Updated 2026-10-23** (`decisions/0084`, "CodeCompass Orchestrator — v2
Strategic Roadmap Realignment"): phase numbers below are updated to
match the realigned sequence (Agent Integration/MCP and Persistent
Knowledge/Reconciliation merged and renumbered from 84/85 to 88; External
Validation renumbered from 87 to 90; v2.0 Hardening and Release
renumbered from 88 to 91). The substantive compatibility posture —
additive-only through Phase 88, no `context-graph.db` migration, no
existing CLI command removed — is unchanged, and if anything
strengthened: the four newly-inserted phases (84-87) add new library
code, new files, and new CLI surfaces, never new fields on an existing
canonical record.

**Updated again, same day** (`decisions/0085`, "CodeCompass Orchestrator
— Corrective Amendment to v2 Knowledge-Driven Development Roadmap"): the
merged Phase 88 is split back into Phase 88 (Agent Integration and MCP)
and Phase 89 (Incremental Knowledge and Documentation Reconciliation);
the former Phase 89 (Comparative Development Trials) is renumbered 90;
the former Phase 90 (External Validation and Adoption) is renumbered 91;
the former Phase 91 (v2.0 Hardening and Release) is renumbered 92. The
substantive compatibility posture is unchanged again — the split adds a
second new module/surface (the reconciliation trigger, alongside the MCP
server), still no new field on any existing canonical record and no
`context-graph.db` schema change.

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

## Compatibility posture through Phase 82-89

**Additive only — now even more so after `decisions/0080`'s
correction, and unaffected by either the 2026-10-23 realignment or its
same-day corrective amendment.** Phase 82's only genuinely new schema
surface is the `oracle-contract.yaml`/`oracle-result.yaml` file pair
(new files, not new fields on any existing record). The epistemic
dimension originally proposed as a new `epistemic_source` field on
Claim/Requirement records was first corrected to an ordinal scale, then
found still conceptually wrong and **removed entirely** (`decisions/
0080`) in favour of a derived, read-time view computed from fields
Phase 81 already has — meaning **zero existing canonical record field
changes at all** through Phase 82. Phases 84-87 (Consolidated Knowledge
API — now read-only by design, `decisions/0085` §1-2 — Self-Curation,
Knowledge-Placement Review, Documentation Compiler) and the now-split
Phase 88 (MCP)/89 (Reconciliation) add new library code, a new CLI
surface, a new MCP server, and new generated-documentation files — no
new field on any existing canonical record, and no `context-graph.db`
schema change. No `context-graph.db` migration is proposed before Phase
83 at the earliest, and even then only if real use demonstrates a
genuine gap (`conditional-generalisation.md`'s standing discipline).

**No CLI command is removed or changed in incompatible ways** by
anything in Phases 82-89. Phase 84's knowledge API adds new, read-only
CLI operations and migrates an existing `query`/`knowledge`/`enrich`
command onto the shared interface only where doing so demonstrably
removes duplicated logic — never wholesale — without changing any
migrated command's observable output (`planning/v2-roadmap.md`'s own
Phase 84 exit gate requires this explicitly, narrowed by `decisions/
0085` §2). Phase 88's MCP server is a new, separate surface alongside
the existing CLI, not a replacement for it.

## Versioning considerations (Phase 84 onward)

- **Consolidated knowledge API** (Phase 84): an internal library surface
  initially — versioned alongside the `codecompass` package's own
  SemVer until/unless Phase 92 decides it needs independent versioning,
  a decision deferred to that phase rather than pre-committed here.
- **MCP server** (Phase 88): versioned independently of the
  `codecompass` PyPI package's own SemVer, following whatever versioning
  convention the chosen MCP SDK itself establishes as idiomatic —
  decided at Phase 88 planning time, not pre-committed here.
- **Oracle-contract/oracle-result schema** (Phase 82): the
  `manifest_schema_version`-style explicit version field convention
  Phase 81B's Amendment 5 established for the clean-room manifest
  (`decisions/0077`) is the direct precedent to reuse — an explicit
  integer schema-version field on both new file formats from the start,
  even though Phase 82 only ever produces version 1 of each.
- **Documentation schema** (Phase 87): the same explicit-version-field
  convention applies to the new documentation-schema format from its
  first version — adding the field now costs nothing and avoids the
  exact "the field didn't exist for the first N documents" retrofit
  problem Phase 81B's Amendment 5 had to correct after the fact.
- **Behavioural contract / knowledge API / MCP public interface** (what
  a downstream MCP client or external tool can rely on): not finalised
  until Phase 92's own "public contract, knowledge-API, MCP and
  assurance-result interface stabilisation" deliverable — Phases 82-91
  are explicitly allowed to change the contract/oracle/API/documentation
  schema shape as real use informs it, provided every change stays
  additive per the posture above. Phase 92 is where backward-incompatible
  changes, if any are still needed, get made deliberately and
  documented, not where they are discovered.

## `codecompass-template` implications

- **No change required through Phase 87.** Phases 82-87's capabilities
  are internal to `codecompass`'s own package and this repository's own
  `planning/` conventions; nothing yet exists for a template adopter to
  use differently.
- **Phase 88 (MCP)** is the first point `codecompass-template` might
  reasonably gain a documented "how to point an MCP-capable agent at a
  CodeCompass-indexed project" section — scoped at Phase 88 planning
  time, not now.
- **Phase 91 (external validation)** is where `codecompass-template`'s
  own onboarding content gets its first real adoption-level update under
  v2, informed by whatever friction the external-project trial actually
  finds — matching Phase 77's own precedent of writing the template from
  proven workflow shape, not speculative design.
- **Adoption levels (Advisory / Assurance / Governed autonomy,
  `v2-roadmap.md`)** should eventually be documented in
  `codecompass-template` as the three concrete ways a downstream project
  can opt in — but only once Level 2 (the v2 product target) is real
  enough to document honestly, i.e. no earlier than Phase 88's
  completion.

## Documentation maintenance requirements

- `docs/`, `ai-docs/`, and `architecture/`-equivalent current-truth
  documentation (`docs/architecture/overview.md` per the post-Phase-81B
  layout) describe **current state only** (`CLAUDE.md` §2) — none of it
  is touched by this planning pass, since nothing it describes has
  changed yet. Each of Phases 82-92 updates these in the same commit as
  its own implementation, per the existing same-commit doc-sync rule,
  exactly as every prior phase already has.
- `docs/development/clean-room-redocumentation.md` (Phase 81B) is
  unaffected — Phase 87's documentation compiler reuses the same broker
  and isolation mechanism, citing this document rather than duplicating
  its content; Phase 90's own optional source-blind arm cites it too.
- No blank-slate documentation reconstruction is implied or scheduled by
  this roadmap — the clean-room reconstruction already completed
  (Phase 81B) stays the current, accepted documentation baseline Phase
  87's compiler builds on incrementally (incremental-maintenance mode)
  or supersedes in full only via an explicit clean-reconstruction run,
  per `CLAUDE.md` §5's own distinction between per-phase drift audits and
  milestone-level full reconstruction.

## Cross-project overlay compatibility (amendment, 2026-10-21, `decisions/0079`; phase numbers updated 2026-10-23, `decisions/0084`, and again the same day, `decisions/0085`)

Reviewed per direct user request: does anything in Phases 82-89's
planned schema preclude a future, generic cross-project semantic overlay
capability? **No existing or planned canonical record changes as a
result of this review, through Phase 89 or the newly-inserted Phases
84-87.** Federation identity (`decisions/0079` §2) is carried by a new,
external, per-project **project-identity envelope** — never injected
into `REQ-`/`CL-`/`EV-`/`OBS-`/`DE-`/`DEC-` records themselves. This is
additive in exactly the same sense §"Compatibility posture" above
already establishes for the rest of v2: a project that never exports a
knowledge snapshot for federation is entirely unaffected, and nothing
about Phase 82's own schema — or Phase 84's consolidated API, which is
project-local by design (`decisions/0084` §1) — needs a migration to
become federation-capable later; only a new, separate export step
(Post-v2 Stage 1, `planning/post-v2-cross-project-overlay-backlog.md`)
needs to be built, whenever it actually is.

One Phase 82 schema correction *was* made by an earlier review (the
`epistemic_source` field's ordinal redesign,
`planning/phase-82-contract-and-evidence-foundation.md` §12) — found
independent of federation, surfaced by reviewing the field against the
INTENDED/OBSERVED/VERIFIED separation requirement. A same-day follow-on
review (`decisions/0080`) found the ordinal redesign itself still
conceptually wrong and removed the field entirely in favour of a derived
view — an even stronger additive posture than this paragraph originally
described, since there is now no new field on any existing record at
all, only new oracle-result files and new, read-only code.
`decisions/0080` §3 also extends the project-identity envelope itself
with a `publisher_id`/`authority` distinction, still external to every
project-local record, still deferred to Post-v2 Stage 1's own
implementation.

**`codecompass-template` implications, unchanged**: nothing in this
amendment, in the 2026-10-23 realignment, or in its same-day corrective
amendment, adds template content — a federated overlay has no
adopter-facing surface before at least Post-v2 Stage 1 exists.

## Security/isolation posture carried forward

- MCP responses and any repository content a v2 capability retrieves are
  treated as potentially untrusted instructions (governing prompt §6),
  never auto-executed — the same trust-boundary discipline Phase 81B's
  broker protocol already enforces for the clean-room writer (a fixed
  `{system_prompt, messages} -> {output}` protocol with no syntax for a
  file path, shell command, or tool/MCP config) is the direct model for
  Phase 88's own MCP tool-result handling, and for Phase 87's
  documentation-compiler composition step, which reuses the same broker.
- No coding agent gains authority to redefine its own acceptance
  criteria at any point in Phases 82-92 — enforced structurally in Phase
  82 already (§5's oracle-contract tamper-detection check) and carried
  forward unchanged through Phase 88's MCP exposure.

## Summary

Through Phase 89, v2 is additive and non-breaking to every existing v1
surface; no migration is required for an existing `codecompass` user or
for `codecompass-template`. The first points requiring real
compatibility decisions are Phase 88 (MCP versioning, a new dependency's
licence compatibility) and Phase 92 (public interface stabilisation,
where any necessary breaking change is made deliberately). This
assessment itself requires no maintainer approval beyond what each named
phase's own plan will separately ask for — it recorded no new commitment
of its own.
