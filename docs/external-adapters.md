# External adapters

CodeCompass's Haskell adapter (Phase 60) runs as a separate,
independent process rather than in-process Python — see
[`architecture/overview.md`](../architecture/overview.md)'s "External
adapters" section for why this exists and how the protocol works, and
[`decisions/0057`](../decisions/0057-external-process-adapter-protocol.md)/
[`decisions/0058`](../decisions/0058-adapter-protocol-and-haskell-adapter-as-separate-repositories.md)
for the full rationale.

This page is a short index — the substantive content lives in two
places, split by audience:

- **Cloning, building, and updating the Haskell submodules** (the
  day-to-day contributor workflow, including the "adaptor"/"adapter"
  spelling note) —
  [`developer/haskell-adapter-submodules.md`](developer/haskell-adapter-submodules.md).
- **The wire protocol itself** (`protocol_version` vs. repository
  semver, the version-compatibility matrix, the JSON-Lines message
  contract) —
  [`protocol-adapter/wire-protocol.md`](protocol-adapter/wire-protocol.md).
- **Writing a brand-new ecosystem adapter** (in-process or
  external-process) —
  [`developer/writing-an-adapter.md`](developer/writing-an-adapter.md).
- **Building a second external-process adapter** (a future ecosystem
  like Haskell's) —
  [`protocol-adapter/integrating-a-new-external-adapter.md`](protocol-adapter/integrating-a-new-external-adapter.md).
