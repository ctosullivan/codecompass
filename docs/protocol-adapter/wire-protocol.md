# The external adapter wire protocol

**Canonical source**: `protocol/codecompass-adaptor-protocol/SCHEMA.md`
(a checked-out git submodule at
`git@github.com:ctosullivan/codecompass-adaptor-protocol.git`, real
directory content confirmed present in this working tree). That file
itself states it *supersedes* `decisions/0057`'s own original inline
protocol description as the source of truth — this page follows
`SCHEMA.md`, cross-referenced against the actual Python client
(`src/codecompass/adapters/external_process.py`) and the actual Haskell
implementation (`adapters/haskell/`), not `decisions/0057`'s prose alone.

## Transport and framing

- The adapter runs as a **local subprocess**. CodeCompass writes JSON
  requests to its `stdin`, reads JSON responses from its `stdout` — one
  complete JSON object per line (**JSON Lines**; no length-prefixing, no
  multipart framing). Confirmed directly in
  `ExternalAdapterProcess._request`
  (`external_process.py:116-162`): `stdin.write(json.dumps(message) +
  "\n")`, `stdout.readline()`.
- The adapter's `stderr` is free-form human-readable text, never parsed
  — only read as a truncated diagnostic tail
  (`_stderr_tail`, `external_process.py:164-170`) when something else
  already failed.
- Exactly **one request outstanding at a time** in this version — the
  client waits for a matching response before sending the next.
- Every message carries an `id` (string or integer) the adapter echoes
  back unchanged; a mismatched `id` in the response raises `AdapterError`
  (`external_process.py:146-150`).
- A response has **either** a `result` key or an `error` key, never
  both, never neither — the client raises `AdapterError` if a response
  has neither (`external_process.py:157-161`).

## The closed 3-method set

Any `method` value outside this set must be rejected by the adapter with
an `unsupported_capability` error.

### `initialize` — the handshake, always first

Request: `{"id", "method": "initialize", "params": {"protocol_version": <int>}}`

`PROTOCOL_VERSION = 1` (`external_process.py:34`) is what CodeCompass
currently sends. Response `result` fields:

| Field | Type | Meaning |
|---|---|---|
| `protocol_version` | int | Hard mismatch with CodeCompass's own value raises `AdapterError` immediately — no negotiation range in v1 (`external_process.py:75-80`). |
| `adapter_name` | string | e.g. `"codecompass-adaptor-haskell"`. |
| `adapter_version` | string | The adapter's own semver release — distinct from `protocol_version`. |
| `ecosystem` | string | Validated against the `core.Ecosystem` value CodeCompass configured this adapter under (`initialize(expected_ecosystem=...)`, Phase 74) — a mismatch raises `AdapterError` immediately, the same posture as `protocol_version`. |
| `capabilities` | array of string | Drawn from the closed 4-value set below, validated by membership at parse time (Phase 74) — an unrecognized entry raises `AdapterError` immediately. |

`CAPABILITIES = ("dependencies", "symbols", "observations",
"diagnostics")` (`external_process.py:32`) — hard-coded in the Python
client, deliberately **not imported from the protocol submodule** (which
ships no code at all, only schemas/docs), so this module has zero
filesystem dependency on the submodule being checked out to be
importable.

### `analyze_project` — request a real analysis

Request: `{"id", "method": "analyze_project", "params": {"project_root": <absolute path>, "package_name": <string>}}`

`project_root` is **already resolved** by CodeCompass before this call —
for a monorepo, CodeCompass has already searched immediate subdirectories
for the one whose own manifest declares the matching package name (see
[`architecture/adapter-interface.md`](../../architecture/adapter-interface.md)'s
"Monorepo package-root resolution" section). The adapter is never handed
a monorepo root and asked to figure out which subdirectory is the real
package.

Response `result` — up to four sections, **present only if the adapter
declared the matching capability** at `initialize`:

- **`dependencies`** — `{"name", "version", "dev_only", "children": [...]}`,
  recursively. Its own plain-JSON wire schema, not a serialization of
  CodeCompass's internal `DepNode`.
- **`symbols`** — flat array of `{"name", "purpose", "module"}`, plus two
  **optional** fields added by `decisions/0059` (an additive,
  backward-compatible schema change — every prior valid message stays
  valid):
  - `kind` — `"export"` (default when omitted) | `"reexport"` (this
    entry names a re-export of another module's own surface, not a
    definition here) | `"undetermined"` (detected but the adapter can't
    confidently resolve whether it's actually exported, e.g. a
    CPP-gated name).
  - `note` — nullable free text, never machine-parsed by CodeCompass;
    for a human/agent reading the result (which real modules a
    `"reexport"` covers, or why an entry is `"undetermined"`).

  **A host MUST NOT treat `"reexport"`/`"undetermined"` as equivalent in
  confidence to `"export"`.** `HaskellAdapter` itself honours this:
  `_render_symbol_line` (`adapters/haskell.py:198-211`) appends `[kind]`
  to the rendered line whenever `kind != "export"`, and surfaces `note`
  explicitly rather than dropping it.
- **`observations`** — array of `{"method", "what_was_done", "location",
  "raw_result", "tool", "tool_version"}` — deliberately shaped to mirror
  CodeCompass's own Phase 54c Observation-record field vocabulary on the
  wire, so a host with that workflow can convert each element losslessly
  into a native record. The protocol itself has **no dependency on or
  knowledge of** CodeCompass's own storage — this is a shape convention,
  not a coupling.
- **`diagnostics`** — array of `{"severity": "warning"|"error",
  "message"}`.

### `shutdown` — clean termination

Request: `{"id", "method": "shutdown"}`. Response `result`: `{}`.
CodeCompass then closes `stdin` and waits, with a
`_SHUTDOWN_TIMEOUT_SECONDS = 5.0` timeout
(`external_process.py:26,97-114`), before a hard `kill()`.
`ExternalAdapterProcess.shutdown()` is safe to call even if
`initialize()` was never called or already failed (`_process is None`
check first), and swallows any `AdapterError` from the shutdown request
itself as best-effort.

## The closed error-code set

`{"code": "not_found"|"parse_error"|"unsupported_capability"|"internal_error", "message"}`
— mapped by the Python client directly onto `AdapterError`
(`external_process.py:151-156`), so calling code never needs to know
whether the adapter behind it is in-process or external.

## Versioning — two independent numbers, do not conflate them

- **`protocol_version`** (currently `1`) — the wire contract itself.
  Changes only on a backward-incompatible change to the message shapes.
  Negotiated fresh on every `initialize` call; a mismatch is a hard
  error in this version.
- **The protocol repository's own semver release** (currently `0.1.0`)
  — can advance for documentation fixes, new examples, or new
  conformance vectors without `protocol_version` changing at all.
  `decisions/0059`'s own `kind`/`note` addition is exactly this:
  additive, backward compatible, landed inside the pre-`0.1.0`-tag
  window, `protocol_version` unchanged.

## Version-compatibility matrix

| CodeCompass | `codecompass-adaptor-protocol` | `codecompass-adaptor-haskell` | `protocol_version` |
|---|---|---|---|
| Phase 60 (this commit) | `0.1.0` | `0.1.0` | `1` |

Extend this table as future phases/releases advance any of the three
independently — it exists to answer "which combinations were actually
tested together," not to be populated speculatively ahead of real use.

## What this protocol deliberately is not

Not gRPC, not a network service, not a plugin marketplace or adapter
registry, not remote/distributed execution, not a versioned SDK
(`decisions/0057`). Revisit only on a real, demonstrated need — none of
these is justified by the protocol's own founding proving case (one local
subprocess, analyzing one project, at a time).

## Handshake validation (closed, Phase 74)

Two gaps this page used to document as open (`L-032`, filed at Phase
63D's own `domain-skeptic` review) are now closed, both raising
`AdapterError` immediately, matching `protocol_version`'s own existing
posture:

1. **The received `capabilities` list is validated** against the closed
   4-value set (`external_process.py::CAPABILITIES`) — an adapter
   reporting a fifth, unrecognized string is rejected at `initialize`,
   not accepted uncomplainingly.
2. **The `ecosystem` field is validated against the value CodeCompass
   configured this adapter under** —
   `HaskellAdapter._analyze` passes `expected_ecosystem=self.config.ecosystem`
   (the same `VendorConfig.ecosystem`/`core.Ecosystem` value that drives
   adapter dispatch via `vendor.toml`) to
   `ExternalAdapterProcess.initialize`, which compares it against the
   response's own `ecosystem` field. A new adapter reporting a mismatched
   `ecosystem` string is now caught at the handshake, not silently
   accepted.

Any future external-process adapter must pass its own real
`expected_ecosystem` to `initialize` — the parameter is required, not
optional, so this validation can't be silently skipped by a new call
site.

## Naming note (already resolved, not a live ambiguity)

`decisions/0057` and `decisions/0058`'s own prose spell the two
repositories "codecompass-**adapter**-protocol"/"codecompass-**adapter**-
haskell." The real, live, checked-out repositories (`.gitmodules`, every
module docstring in `src/codecompass/adapters/*.py`, and `git ls-remote`
against both URLs) are unambiguously spelled "codecompass-**adaptor**-
protocol"/"codecompass-adaptor-haskell." This is a pre-implementation
drafting typo in the ADRs' own prose (the ADR commits predate the real
repositories by hours, per `git log`), not a second, different pair of
repositories — `docs/domain/concepts/protocol.md` documents the same
finding independently, and
[`developer/haskell-adapter-submodules.md`](../developer/haskell-adapter-submodules.md)
carries the same note for anyone cloning/building the repositories
directly.
