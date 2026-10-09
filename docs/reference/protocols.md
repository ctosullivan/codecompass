# Reference: the external adapter wire protocol

This is a summary of `protocol/codecompass-adaptor-protocol/SCHEMA.md` and its accompanying JSON Schemas/conformance vectors — the canonical specification lives in that submodule, which is **MIT-licensed**, independently of CodeCompass itself and the reference Haskell adapter (both GPL-3.0-or-later). CodeCompass's own `src/codecompass/adapters/external_process.py` implements the host side of this protocol and carries zero ecosystem-specific knowledge of its own.

## Purpose

Lets a host tool (CodeCompass, or any other tool choosing to speak this protocol) request structured analysis of a software project from an independent adapter process, with no host-side import of ecosystem-specific code and no adapter-side dependency on the host's internals.

## Transport and framing

- The adapter runs as a **local subprocess**. The host writes requests to its stdin and reads responses from its stdout, **one complete JSON object per line** — JSON Lines, no length-prefixing, no multipart MIME.
- The adapter's stderr is free-form human-readable text, never parsed.
- **Exactly one request is outstanding at a time** in v1.
- Every message carries an `id` (string or integer), echoed back unchanged.
- A response has **either** `result` **or** `error` — never both, never neither.

## Methods — a closed set of three

### `initialize`

Always the first message. Request: `{"id", "method": "initialize", "params": {"protocol_version": <int>}}`.

Response `result` fields: `protocol_version` (int — a mismatch with the host's own requested version is a hard error in v1, no negotiation range), `adapter_name`, `adapter_version` (the adapter's own semver release — distinct from `protocol_version`), `ecosystem` (free text — this protocol defines no closed ecosystem enum), `capabilities` (array drawn from the closed set `dependencies`/`symbols`/`observations`/`diagnostics`).

### `analyze_project`

Request: `{"id", "method": "analyze_project", "params": {"project_root": <absolute path, already resolved by the host>, "package_name": <string>}}`. If the host's own project is a monorepo, the host — not the adapter — resolves which subdirectory is the real target package before ever invoking the adapter.

Response `result` — up to four sections, present only if the matching capability was declared at `initialize`:

- **`dependencies`** — a recursive tree: `{"name", "version", "dev_only", "children": [...]}`. A plain wire schema, not a serialization of any host-internal structure.
- **`symbols`** — a flat array of `{"name", "purpose", "module"}`, plus two optional fields: `kind` (`"export"` default | `"reexport"` | `"undetermined"`) and `note` (nullable free text). A host must not treat `"reexport"`/`"undetermined"` entries as equivalent in confidence to `"export"` ones.
- **`observations`** — neutral, provenance-preserving findings: `{"method", "what_was_done", "location", "raw_result", "tool", "tool_version"}` — deliberately mirroring the field vocabulary CodeCompass's own knowledge-record model uses for an Observation, so a host with such a workflow can losslessly convert each element.
- **`diagnostics`** — `{"severity": "warning"|"error", "message"}`.

### `shutdown`

Request: `{"id", "method": "shutdown"}`. Response `result`: `{}`. The host then closes stdin and waits (with a timeout, then a hard kill) for the adapter process to exit.

## Errors

```json
{"id": <same id>, "error": {"code": "<one of the closed set>", "message": "<human-readable>"}}
```

Closed error-code set: `not_found`, `parse_error`, `unsupported_capability` (includes any unknown `method`), `internal_error`.

## Versioning

`protocol_version` (the integer in `initialize`) identifies the wire contract and changes only on a backward-incompatible specification change. The protocol repository's own release version is a separate semver number that can advance independently.

## What this protocol deliberately is not

Not gRPC, not a network service, not a plugin marketplace/adapter registry, not remote/distributed execution, not a versioned SDK or client library — stated explicitly in the specification as premature given the protocol's own founding use case.

## Conformance

The protocol repository ships `conformance/manifest.json` plus `valid/`/`invalid/` message fixtures and JSON Schemas (draft 2020-12) — no executable harness of its own (schemas and documentation only, language-agnostic). CodeCompass's own test suite (`tests/test_protocol_conformance.py`) validates every vector against the real schemas via `jsonschema`, skipping cleanly if the submodule isn't checked out.

## The reference implementation: `codecompass-adaptor-haskell`

A real, independent, publicly-hosted (confirmed reachable, with real commit history and a real `v0.1.0` tag) GPL-3.0-or-later repository, checked out as the `adapters/haskell/` git submodule. Built with Haskell Stack; implements `Adapter.Protocol` (the generic JSON-Lines loop — zero CodeCompass-specific or Haskell-analysis-specific knowledge of its own), `Adapter.Scanner` (the export-list symbol scanner — see `docs/reference/symbol-extraction.md`), `Adapter.Deps` (dependency-tree construction via real `stack dot --external`/`stack ls dependencies --external` subprocess calls — `stack ls dependencies` has no JSON output mode, confirmed live, so `stack dot`'s GraphViz DOT output supplies the tree structure, combined with `stack ls dependencies`'s flat name→version map for labelling), and `Adapter.Manifest` (minimal, single-field `package.yaml`/`.cabal` reads).

**Setup, as far as the available evidence confirms:** `git submodule update --init` to check out the submodule, then `stack build` inside `adapters/haskell/`. No minimum Stack/GHC version is documented anywhere in the available evidence (the submodule's own `stack.yaml` pins `resolver: nightly-2026-09-01`, but that is a snapshot pin, not a stated minimum-tool-version requirement). Platform-specific Stack installation/build troubleshooting is general Stack/GHC knowledge, not something specific to this project.

### A real naming inconsistency, resolved in favour of what's actually live

An older decision record's own text refers to these two repositories using the spelling "adapter" (`codecompass-adapter-protocol`, `codecompass-adapter-haskell`). Every real, live artifact — `.gitmodules`, the checked-out directory paths, every module docstring in the current source — consistently uses "**adaptor**" instead (`codecompass-adaptor-protocol`, `codecompass-adaptor-haskell`), and these are the real, live, publicly reachable repositories. This is understood as a pre-implementation drafting typo in the older decision text (it predates, by several hours on the same day, the commit that actually created the two repositories), not a live, unresolved naming question — but no corrective edit to that older decision text's own wording is confirmed to exist in the available evidence.
