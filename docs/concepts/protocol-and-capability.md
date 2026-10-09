# Concepts: protocol and capability

## Protocol

"Protocol" (in CodeCompass's own specific usage) names the **external adapter wire protocol** defined by the `codecompass-adaptor-protocol` repository (checked out at `protocol/codecompass-adaptor-protocol/`, MIT-licensed, a separate repository from CodeCompass itself) and governed internally by `decisions/0057`.

Key properties, all closed sets:

- **JSON-Lines framing** over a local subprocess's stdin/stdout — no length-prefixing, no multipart MIME.
- **One outstanding request at a time** (v1) — the host sends a request and waits for the matching response before sending the next.
- **Three methods**: `initialize`, `analyze_project`, `shutdown`. Any other `method` value must be rejected with an `unsupported_capability` error.
- **A four-value capability set** (see below), gating what `analyze_project` may return.
- **A four-value error-code set**: `not_found`, `parse_error`, `unsupported_capability`, `internal_error`.

It is deliberately **not** gRPC, not a network service, not a plugin registry, and not a versioned SDK — the protocol's own specification states this explicitly as a scope decision, not an oversight; none of those are justified by the protocol's own founding use case (one local subprocess, analyzing one project, at a time).

`protocol_version` (an integer, currently `1`, negotiated at `initialize`) identifies the **wire contract** and is distinct from the protocol repository's own semver release version, which can advance (documentation fixes, new examples) without the wire contract itself changing.

See `docs/reference/protocols.md` for the full message/schema reference.

## Capability

"Capability" is the external protocol's own specific, closed term: one of exactly four strings — `dependencies`, `symbols`, `observations`, `diagnostics` — declared once by an adapter at `initialize`, gating which of `analyze_project`'s result sections that adapter may legitimately return.

This is **not** interchangeable with the ordinary English word "feature." "Feature" has no formal role anywhere in CodeCompass — it's unscoped prose for "a thing CodeCompass does," with no enumeration, no handshake, and no schema constraint attached to it. Only the external adapter protocol has capabilities in this closed-set sense; calling something a CodeCompass "feature" is not wrong, but it is never the same claim as declaring a protocol "capability."

A real, now-closed gap: the protocol's own `ecosystem` field (reported by an adapter at `initialize`) is deliberately unconstrained free text at the specification level, distinct from CodeCompass's own closed `Ecosystem` enum. Earlier in the project's history, nothing checked this field against the `Ecosystem` value CodeCompass had configured the adapter under — a real, if narrow, validation gap. This was fixed: `ExternalAdapterProcess.initialize` (`src/codecompass/adapters/external_process.py`) now takes a required `expected_ecosystem` argument and raises `AdapterError` if the two disagree, and also rejects any `capabilities` entry outside the closed four-value set. `HaskellAdapter` — the one production call site — passes its own configured `core.Ecosystem` value as `expected_ecosystem`. The wire-reported `ecosystem` value is still never used for dispatch (dispatch is driven entirely by `VendorConfig.ecosystem`, fixed before the adapter process is even spawned) — this fix adds a *validation* check, not a new dispatch path.
