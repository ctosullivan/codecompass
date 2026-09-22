---
status: DRAFT — pending domain-skeptic review and actual-user approval
---

# Protocol

## Definition

**"Protocol," in this cluster's specific referent, names the external
adapter wire protocol** — the contract an external-process adapter
(currently only the Haskell reference adapter) speaks to CodeCompass
over `stdin`/`stdout`. Defined by `decisions/0057`, canonicalized by
`protocol/codecompass-adaptor-protocol/SCHEMA.md` (a checked-out git
submodule, which explicitly states it *supersedes* `decisions/0057`'s
own original inline description as the source of truth, `EV-ADPT-003`).

**Shape (v1, deliberately minimal):**

- **Framing**: JSON Lines (one JSON object per line) on `stdin`
  (requests) / `stdout` (responses); no length-prefixing, no multipart
  framing; every message carries an `id` echoed back unchanged; exactly
  one request outstanding at a time in v1.
- **Methods**: a **closed 3-method set** — `initialize`,
  `analyze_project`, `shutdown`. Any other `method` value must be
  rejected with an `unsupported_capability` error.
- **Capabilities**: a closed 4-value set (`dependencies`, `symbols`,
  `observations`, `diagnostics`) declared once by the adapter in its
  `initialize` response, gating which of `analyze_project`'s four
  result sections that adapter may return. See `capability.md`.
- **Errors**: a closed 4-value error-code set (`not_found`,
  `parse_error`, `unsupported_capability`, `internal_error`).
- **Versioning**: `protocol_version` (an integer negotiated at
  `initialize`, hard-error on mismatch, no negotiation range) is
  distinct from the protocol repository's own semver release version —
  the latter can advance (docs, examples, conformance vectors) without
  the wire contract itself changing.

## What it is NOT

- **Not gRPC, not a network service, not a plugin marketplace or
  registry, not remote/distributed execution, not a versioned SDK** —
  `decisions/0057` names each of these explicitly and rejects them for
  v1, revisitable only on real, demonstrated need.
- **Not the adapter itself.** The protocol is the *contract*; the
  adapter (`adapter.md`) is the *code* that speaks it (either the
  external process, or CodeCompass's own generic client,
  `external_process.py`).
- **Not the same repository-naming scheme it is shipped under.** The
  protocol's own repository is `codecompass-adaptor-protocol` (per
  `.gitmodules` and every in-repository code comment) — note the
  "adaptor" spelling, which conflicts with `decisions/0058`'s own prose
  ("codecompass-adapter-protocol", "adapter" spelling). See "Edge case"
  below; this is a naming-drift finding, not part of the protocol's own
  technical definition.
- **Not `context-graph.db`'s own schema.** `observations` (a protocol
  result section) is deliberately shaped to mirror Phase 54c's
  Observation-record field vocabulary on the wire, so a host can convert
  each element losslessly into a native record — but the protocol
  itself has no dependency on, or knowledge of, CodeCompass's own
  storage.

## Invariants

- A response carries **either** a `result` key **or** an `error` key —
  never both, never neither (`EV-ADPT-003`).
- `analyze_project`'s four result sections are each present **only if**
  the adapter declared the matching capability at `initialize`
  (`EV-ADPT-003`).
- The `ecosystem` field in an `initialize` response is **free text at
  the specification level** — the protocol "does not define a closed
  ecosystem enum" (SCHEMA.md, quoted verbatim). This is a deliberate
  design choice, not an oversight — see `ecosystem.md`'s own edge case
  for what this means in the current implementation.

## Example

A real, hand-written fake adapter process
(`tests/fixtures/fake_adapter.py`) implements this shape end to end:
its `initialize` response reports all four capabilities; its
`analyze_project` response returns a two-level dependency tree, one
symbols entry, one observation, and an empty diagnostics list; unknown
methods get `{"error": {"code": "unsupported_capability", ...}}`. A
real test suite (`tests/test_adapters_external_process.py`) exercises
this fixture through the generic Python client and passes (30/30,
`EV-ADPT-006`).

## Counterexample / edge case

**The received `capabilities` list is not itself validated against the
closed 4-value set by `external_process.py` at parse time** — it is
stored as `tuple(response.get("capabilities", []))` with no membership
check. Nothing in the current Python client would reject or even flag
an adapter reporting a fifth, unrecognized capability string; the
closed-set discipline currently rests entirely on the *specification*
(SCHEMA.md) and on well-behaved adapters, not on any enforcement code
in this repository (`OBS-ADPT-005`).

A second naming inconsistency, found and then resolved during
`domain-skeptic`'s own review: `decisions/0058`'s own prose consistently
spells the protocol repository "codecompass-**adapter**-protocol," but
the actually checked-out submodule (`.gitmodules`, the real directory
path, and every module docstring in `src/codecompass/adapters/*.py`)
consistently spells it "codecompass-**adaptor**-protocol." **Resolved
(`CL-ADPT-010`, superseding `CL-ADPT-008`)**: `git log` shows
`decisions/0058`'s own commit predates, by five hours the same day, the
commit that actually created the real repositories — the ADR's
"adapter" spelling was written aspirationally before either repository
existed. `git ls-remote` independently confirms both "adaptor"-spelled
repositories are real, live, public, and tagged `v0.1.0`, while the
"adapter"-spelled protocol URL behaves identically to a repository that
was never created. This is a pre-implementation drafting typo in
`decisions/0058`'s own prose, not a live product question — the real
repositories this project depends on are unambiguously
"adaptor"-spelled. Whether `decisions/0058` itself should receive a
corrective ADR entry is a separate editorial question, not decided by
this finding.

## Relationships

- **is-spoken-by** the external-process strategy of `adapter.md` only
  (in-process adapters never speak this protocol).
- **declares** `capability.md` values, a term this protocol itself
  defines and closes.
- **is-versioned-independently-of** its own hosting git repository's
  release version.
- **is-distinct-from** `connector.md` (not used by this protocol) and
  from CodeCompass's own `context-graph.db` schema (protocol
  `observations` mirror that schema's vocabulary on the wire but carry
  no dependency on it).

## References

- `EV-ADPT-003`, `EV-ADPT-006`, `EV-ADPT-008` —
  `planning/knowledge/codecompass-domain/`
- `CL-ADPT-003`, `CL-ADPT-008` (superseded), `CL-ADPT-010` (the
  resolution, citing `OBS-SKEP-001`, `OBS-SKEP-002`, `EV-SKEP-001`) —
  `planning/knowledge/codecompass-domain/`
- `decisions/0057-external-process-adapter-protocol.md`
- `decisions/0058-adapter-protocol-and-haskell-adapter-as-separate-repositories.md`
- `protocol/codecompass-adaptor-protocol/SCHEMA.md:1-172`
- `src/codecompass/adapters/external_process.py:1-171`
- `tests/fixtures/fake_adapter.py`,
  `tests/test_adapters_external_process.py`
