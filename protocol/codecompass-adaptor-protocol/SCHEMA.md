# CodeCompass external adapter protocol — v1

This is the canonical specification. It supersedes the inline
description originally written in CodeCompass's own
`decisions/0057-external-process-adapter-protocol.md`, which remains a
valid historical snapshot but is no longer the source of truth once this
repository exists.

## Purpose

Lets a host tool (CodeCompass, or any other tool that chooses to speak
this protocol) request a structured analysis of a software project from
an independent adapter process, without the host needing to import any
ecosystem-specific code, and without the adapter needing any dependency
on the host's internals.

## Transport and framing

- The adapter is invoked as a **local subprocess**. The host writes
  requests to the adapter's `stdin` and reads responses from its
  `stdout`, one complete JSON object per line (**JSON Lines** — no
  length-prefixing, no multipart MIME, no other framing).
- The adapter's `stderr` is free-form human-readable diagnostic text —
  never parsed by the host.
- Exactly one request is outstanding at a time in v1: the host sends a
  request and waits for the matching response before sending the next.
  Every message carries an `id` (a JSON string or integer) that the
  adapter echoes back unchanged, so a future version could allow
  multiple outstanding requests without changing this version's own
  message shapes.
- A response object has **either** a `result` key **or** an `error` key
  — never both, never neither.

## Methods

Exactly three methods exist in v1. This is a **closed set** — an
adapter must reject any other `method` value with an `unsupported_capability`
error (see "Errors" below).

### `initialize`

The handshake. Always the first message the host sends.

Request: `{"id", "method": "initialize", "params": {"protocol_version": <int>}}`

Response `result`:

| Field | Type | Meaning |
|---|---|---|
| `protocol_version` | integer | The protocol version this adapter speaks. A mismatch with the host's own requested version is a hard error in v1 — no negotiation range. |
| `adapter_name` | string | A short, stable adapter identifier (e.g. `"codecompass-adaptor-haskell"`). |
| `adapter_version` | string | The adapter's own semver release version — distinct from `protocol_version`. |
| `ecosystem` | string | The package ecosystem this adapter analyzes (e.g. `"haskell"`). Free text — this protocol does not define a closed ecosystem enum. |
| `capabilities` | array of string | Which of `analyze_project`'s four result sections this adapter can actually produce. Drawn from the **closed set**: `"dependencies"`, `"symbols"`, `"observations"`, `"diagnostics"`. |

See [`schemas/initialize-request.json`](schemas/initialize-request.json) /
[`schemas/initialize-response.json`](schemas/initialize-response.json).

### `analyze_project`

Request a real analysis of one already-resolved package directory.

Request: `{"id", "method": "analyze_project", "params": {"project_root": <string>, "package_name": <string>}}`

- `project_root` is an **absolute filesystem path** to the specific
  package's own directory — already resolved by the host. If the host's
  own project is a monorepo (multiple packages under one root), the
  host resolves which subdirectory is the target package **before**
  invoking the adapter. The adapter is never handed a monorepo root and
  asked to figure out which subdirectory is the real package.
- `package_name` is the name the host expects to find at that location,
  for the adapter's own sanity-checking if it chooses to use it.

Response `result` — up to four top-level sections, **present only if the
adapter declared the matching capability** in `initialize`:

- **`dependencies`** — a tree: `{"name", "version", "dev_only", "children": [...]}`,
  recursively. Structurally tree-shaped by necessity, but this is its
  own plain-JSON wire schema — not a serialization of any host-internal
  data structure.
- **`symbols`** — a flat array of `{"name", "purpose", "module"}`
  objects — the adapter's own best mechanical (non-AI) extraction of
  the analyzed package's public API surface. `purpose` is nullable.
  Two further fields are **optional**, for languages whose visibility
  model can't always mechanically resolve to a plain, confident "this
  name is exported" — added for the reference Haskell adapter, where
  some real export-list entries name what they cover only ambiguously
  without deeper (out of scope for a no-full-parser scanner) analysis:
  - `kind` — one of `"export"` (the default when omitted — an ordinary,
    confidently-resolved exported name), `"reexport"` (this entry names
    a re-export of another module's own surface rather than a single
    symbol defined here — `name` in this case is the re-export's own
    alias/target, not a definition), or `"undetermined"` (the adapter
    detected this entry but could not confidently resolve whether it is
    actually exported — e.g. a name gated by a build-time conditional
    the adapter can't evaluate). A host should not treat `"reexport"`
    or `"undetermined"` entries as equivalent in confidence to
    `"export"` ones.
  - `note` — nullable free-text elaboration (e.g. which real modules a
    `"reexport"` entry's alias covers, or why an entry is
    `"undetermined"`). Never machine-parsed by a host; for a human or an
    agent reading the result.
- **`observations`** — an array of neutral, provenance-preserving
  findings: `{"method", "what_was_done", "location", "raw_result",
  "tool", "tool_version"}`. This mirrors the field vocabulary
  CodeCompass's own evidence-backed knowledge workflow uses for an
  "Observation" record, expressed as JSON on the wire instead of YAML —
  so a host that has such a workflow can losslessly convert each
  element into its own native record, preserving provenance across the
  process boundary. `location` and `tool`/`tool_version` are nullable.
- **`diagnostics`** — an array of non-fatal findings:
  `{"severity": "warning" | "error", "message"}`.

See [`schemas/analyze_project-request.json`](schemas/analyze_project-request.json) /
[`schemas/analyze_project-response.json`](schemas/analyze_project-response.json).

### `shutdown`

Request: `{"id", "method": "shutdown"}`
Response `result`: `{}`

The host then closes `stdin` and waits (with a timeout, then a hard
kill) for the adapter process to exit. See
[`schemas/shutdown-request.json`](schemas/shutdown-request.json) /
[`schemas/shutdown-response.json`](schemas/shutdown-response.json).

## Errors

Any response may carry an `error` object instead of `result`:

```json
{"id": <same id as the request>, "error": {"code": "<one of the closed set>", "message": "<human-readable>"}}
```

Closed error-code set:

| Code | Meaning |
|---|---|
| `not_found` | The requested project/package could not be located or read. |
| `parse_error` | The adapter could not make sense of the project's own files (a malformed manifest, unparseable source, etc). |
| `unsupported_capability` | The request asked for something this adapter doesn't support — including any `method` outside the closed set. |
| `internal_error` | Anything else that prevented the adapter from producing a result. |

See [`schemas/error.json`](schemas/error.json).

## What this protocol deliberately is not

Not gRPC. Not a network service. Not a plugin marketplace or adapter
registry. Not remote/distributed execution. Not a versioned SDK or
client library. A future version may introduce one of these if a real,
demonstrated need appears — none is justified by this protocol's own
founding proving case (one local subprocess, analyzing one project, at a
time).

## Versioning

- `protocol_version` (the integer in `initialize`) identifies the **wire
  contract** — it changes only when a change to this document is not
  backward compatible with an existing implementation.
- This repository's own release version (this file lives at a specific
  git tag/release, e.g. `0.1.0`) is a **separate, semver** version that
  can advance (documentation fixes, new examples, new conformance
  vectors) without `protocol_version` changing at all.

## Conformance

An implementation (host or adapter) is conformant with a given
`protocol_version` if every message it sends validates against this
repository's `schemas/*.json` for that version, and it correctly
recognizes every vector under `conformance/invalid/` as invalid. See
[`conformance/README.md`](conformance/README.md).
