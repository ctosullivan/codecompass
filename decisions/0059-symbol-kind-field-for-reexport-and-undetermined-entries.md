# 0059. `analyze_project`'s `symbols` entries gain an optional `kind`/`note` pair

## Status

Accepted (2026-09-19).

## Context

`decisions/0057` defined `analyze_project`'s `symbols` wire shape as a
flat `{"name", "purpose", "module"}` array — every entry implicitly a
plain, confidently-resolved exported symbol. Phase 60's own Phase 54c
evidence-backed workflow for Haskell API-surface extraction
(`planning/knowledge/haskell-api-surface-extraction/`) approved
(`DEC-HSAPI-001`) a design that requires representing two entries that
are **not** plain confident exports:

- A `module <Name>` re-export entry (`REQ-HSAPI-002`) — names a
  re-export of another module's own surface, not a single symbol
  defined at that location.
- A build-conditional-gated (CPP) entry the adapter cannot evaluate
  (`REQ-HSAPI-003`) — detected, but its actual exported status is
  genuinely undetermined by a no-full-parser scanner.

The knowledge-curator's own context-packet-assembly pass for this
feature (`packet-sufficiency.md`) flagged this as a real, structural gap
before implementation began: the wire schema
(`codecompass-adaptor-protocol`'s `schemas/analyze_project-response.json`)
was never itself inspected during the Haskell-source research, so no
record in the knowledge base ever noticed it has no field to carry
either case — forcing either a silent, confidence-overstating
`"export"` entry, an unreviewed ad-hoc implementer choice, or a real
Decision. This ADR is that Decision.

## Decision

`codecompass-adaptor-protocol`'s `analyze_project-response.json` schema
gains two **optional** fields on each `symbols` array entry:

- `kind` — one of `"export"` (default when omitted), `"reexport"`, or
  `"undetermined"`.
- `note` — nullable free text, never machine-parsed by a host, for a
  human/agent-readable elaboration (which real modules a `"reexport"`
  alias covers; why an entry is `"undetermined"`).

This is an **additive, backward-compatible** schema change: every
existing valid message (every prior example, every prior conformance
vector) remains valid unchanged, since `kind`/`note` are not added to
`required`. No change to `protocol_version` (still `1`,
`decisions/0057`) — only the protocol repository's own release content
changes, before its first `0.1.0` tag is cut (Phase 60's own "tag `0.1.0`
only after successful validation" plan requirement, so this amendment
lands inside that same pre-release window, not as a breaking
after-the-fact change to something already tagged).

## Alternatives considered

- **Encode re-export/undetermined status only in `diagnostics`** (a
  free-text, per-project list, not per-symbol). Rejected — loses the
  association with the specific symbol name/module the entry concerns,
  forcing a host to string-match a diagnostic message back to a
  `symbols` entry to recover what it's about.
- **A separate top-level `analyze_project` result section** (e.g.
  `"reexports": [...]`, `"undetermined_symbols": [...]`) instead of
  widening `symbols` itself. Rejected — adds two more closed-set
  concepts (new capability-list-adjacent sections) for what is really a
  confidence/kind annotation on the same underlying concept
  (`symbols` entries), and would require every future adapter
  implementing the `symbols` capability to reason about three arrays
  instead of one plus an optional tag.
- **Do nothing; require the Haskell adapter to always emit a plain
  `"export"` entry.** Rejected — this is exactly the "confident-looking
  but sometimes silently wrong" outcome `DEC-HSAPI-001`'s own reasoning
  (and this project's own governing "an honest gap beats a confident
  guess" rule) rejects for the CPP case specifically; doing the same at
  the wire level would undo that decision one layer up.

## Consequences

- `codecompass-adaptor-haskell`'s `app/Main.hs` emits `kind: "reexport"`
  for a detected `module <Name>` entry (with `note` naming the real
  modules a file-local alias resolves to, when resolvable) and
  `kind: "undetermined"` for a CPP-gated entry (with `note` naming the
  guard), per `REQ-HSAPI-002`/`REQ-HSAPI-003`.
- Any host consuming `symbols` (CodeCompass's own `HaskellAdapter`, or
  a future host) MUST NOT treat a `"reexport"` or `"undetermined"` entry
  as equivalent in confidence to a plain `"export"` one — `HaskellAdapter`
  itself passes `kind`/`note` through into its own rendered API-surface
  text (`readme_and_api_surface()`) rather than silently dropping the
  distinction.
- `codecompass-adaptor-protocol`'s conformance vectors gained one new
  valid vector (`kind`/`note` used) and one new invalid vector (a `kind`
  value outside the closed three-value set) — both already verified
  against the schema locally before this commit.
