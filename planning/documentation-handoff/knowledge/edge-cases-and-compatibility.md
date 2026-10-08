# Edge cases and compatibility (curated synthesis)

A curated selection of already-existing canonical Claims whose own
content explicitly discusses an edge case or a compatibility boundary,
across the selected handoff slugs. **No `assertion_kind` enum value maps
directly to this category** — selection here is by content, not by a
closed-enum field, per the handoff-selection criteria in `INDEX.md`.

## From `codecompass-domain`

### CL-ADPT-005 — one vendor, one adapter instance is not a filesystem guarantee

> Edge case: the "one vendor, one adapter instance" relationship is not a
> structural filesystem guarantee — `HaskellAdapter`'s own monorepo
> resolution (`_resolve_package_dir`) shows a single `project_root` can
> host multiple vendors' worth of source (e.g. `hledger-lib`/`hledger`/
> `hledger-ui` all inside one `hledger` checkout), and the adapter
> instance itself is responsible for narrowing `project_root` down to the
> one subdirectory matching its own vendor's name before any other method
> call is meaningful.

(Full Claim, including the ecosystem/vendor/adapter relationship this
edge case qualifies, is reproduced in `interfaces-and-behaviours.md`.)

### CL-ADPT-009 — an unenforced boundary in the external adapter protocol (historical; see CL-ADPT-011 for the current state)

> This is a genuine edge case worth naming on the ecosystem/protocol
> concept pages: nothing currently prevents an external adapter from
> reporting an `ecosystem` string that disagrees with the `Ecosystem`
> value CodeCompass configured it under, and no observed behaviour would
> currently detect or surface that disagreement.

**This Claim is superseded by CL-ADPT-011** (reproduced in full in
`invariants-and-constraints.md`), which records that Phase 74 closed
this exact gap: `ExternalAdapterProcess.initialize` now raises
`AdapterError` on a mismatch. Both are surfaced here together so the
writer sees the edge case's own history (identified, then closed), not
only its current, already-resolved state.
