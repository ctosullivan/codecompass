# 0057. A second adapter-implementation strategy: external-process adapters over a small JSON protocol

## Status

Accepted (2026-09-19).

## Context

`decisions/0002` established that every `EcosystemAdapter` implements a
common Python interface (`installed_version`, `source_location`,
`readme_and_api_surface`, `repository_url`, `dependency_tree`) using
whatever native tooling its ecosystem provides — but every adapter to
date (npm, Python, Cargo) is an **in-process Python class**, imported
directly by `src/codecompass/adapters/__init__.py` and running inside
CodeCompass's own process.

Phase 60 (the minimal Haskell adapter, `planning/phase-60-minimal-haskell-adapter.md`)
was initially planned this way too. Direct user instruction changed the
architecture before implementation began: the Haskell adapter should
instead be the **reference implementation of a genuinely external
adapter** — a separate process, communicating over a small,
language-neutral protocol — explicitly to validate that CodeCompass's
core never needs to import ecosystem-specific implementation code for a
new adapter, motivated by a real future case: a potentially
**proprietary COBOL/mainframe adapter suite**, which could never be
distributed as importable GPL-licensed Python code inside
`src/codecompass/` even if CodeCompass wanted to ship one.

This is a genuinely new architectural axis, not a refinement of
`decisions/0002` — both strategies (in-process native-tooling adapters,
external-process protocol adapters) are valid and expected to coexist.

## Decision

**A second `EcosystemAdapter` implementation strategy is accepted:** an
adapter may run as an independent OS process, communicating with
CodeCompass over a small, versioned, JSON-based protocol on stdin/stdout,
rather than being an in-process Python class with ecosystem-specific
logic.

### Protocol shape (v1 — deliberately minimal)

**Framing**: one JSON object per line (JSON Lines) on stdin (requests)
and stdout (responses) — no length-prefixing, no multipart framing.
Every message carries an `id` (string or integer) the adapter echoes
back, so a synchronous request/response pair is always unambiguous even
though this version never sends more than one outstanding request at a
time.

**Methods** (a small, closed set — not open-ended RPC):

- `initialize` — the handshake. CodeCompass sends its own supported
  `protocol_version`; the adapter responds with its own
  `protocol_version` (an integer; a mismatch is a hard error this
  version, no negotiation range), `adapter_name`, `adapter_version`,
  `ecosystem`, and a `capabilities` list drawn from a small closed set:
  `dependencies`, `symbols`, `observations`, `diagnostics`. CodeCompass
  uses this to know what to expect from `analyze_project` without
  hard-coding per-adapter assumptions.
- `analyze_project` — CodeCompass sends an absolute `project_root` (the
  **already-resolved** package directory — see "monorepo package roots"
  below, resolution happens on the CodeCompass side, never inside the
  adapter) and the target `package_name`. The adapter responds with a
  single result object containing up to four sections, each present
  only if the adapter declared the matching capability:
  - `dependencies` — a tree (`{"name", "version", "dev_only", "children": [...]}`,
    recursively) — structurally similar to CodeCompass's own internal
    `DepNode` dataclass by necessity (a tree needs a tree shape), but
    defined as its own plain-JSON wire schema, never "`DepNode`
    serialized" — the adapter has no dependency on CodeCompass's Python
    code and never could.
  - `symbols` — a flat list of `{"name", "purpose", "module"}` objects.
  - `observations` — a list of neutral, Phase-54c-shaped findings
    (`{"method", "what_was_done", "location", "raw_result", "tool",
    "tool_version"}` — the same field vocabulary
    `planning/phase-54c-evidence-knowledge-workflow.md` §2.2 already
    defines for an Observation record, expressed as JSON instead of
    YAML on the wire). CodeCompass's own ingestion code (not the
    adapter) converts these into real
    `planning/knowledge/<feature>/OBS-...yaml` records, preserving
    provenance across the process boundary.
  - `diagnostics` — a list of `{"severity": "warning"|"error",
    "message"}` non-fatal findings (e.g. "no `stack.yaml` found, using
    default resolver").
- `shutdown` — a clean termination request; CodeCompass then closes
  stdin and waits (with a timeout, then a hard kill) for the process to
  exit.

**Errors**: a response carries either a `result` key or an `error` key
(`{"code": "not_found"|"parse_error"|"unsupported_capability"|"internal_error",
"message"}`), never both — mapped directly onto the existing
`AdapterError` exception every adapter method already raises, so calling
code doesn't need to know whether the adapter behind it is in-process or
external.

**What this protocol deliberately is not**: not gRPC, not a network
service, not a plugin marketplace or registry, not remote execution, not
a versioned SDK. A future phase may need one of these if real evidence
demands it (per this project's own standing "smallest justified fix"
discipline) — none is justified by anything this phase's real, bounded
proving case (one local subprocess, one project) actually requires.

### Where the boundary actually falls

Not every `EcosystemAdapter` method needs the external process. Reading
`package.yaml` for `installed_version`/`repository_url` (simple
manifest-key lookups) is the same class of generic, ecosystem-adjacent
code `discovery.py` already does directly for npm/Python/Cargo's own
manifests (`package.json`/`pyproject.toml`/`Cargo.toml`) — using
`yaml.safe_load()` on a YAML file is not "Haskell-specific
implementation code" any more than `tomllib.load()` on a TOML file is
"Rust-specific." What genuinely requires isolation, because it embodies
real ecosystem-specific *logic* rather than manifest-key lookup, is:
resolving `stack`'s own build-plan/dependency-tree semantics, and
parsing real `.hs` source files to determine a module's exported API
surface. Those two are what the external process actually does; the
Python-side `HaskellAdapter` class stays a thin dispatcher (manifest
reads + the protocol client call), not a reimplementation of the
adapter's own logic in two places.

### Monorepo package roots

The path passed to `analyze_project` is always the package's own
directory (e.g. `hledger-lib/` within the `hledger` monorepo), resolved
by CodeCompass **before** invoking the adapter — by searching the
configured project root's immediate subdirectories for the one whose own
`package.yaml` declares the matching `name`, not by handing the adapter
the whole monorepo root and expecting it to figure this out. This keeps
monorepo-awareness a generic, reusable capability of the protocol client,
not something every future external adapter has to reimplement.

## Alternatives considered

- **Keep the Haskell adapter in-process** (the original Phase 60 plan).
  Rejected by direct instruction — does not test or prove anything about
  a future differently-licensed adapter, since in-process Python code is
  definitionally importable GPL-covered code.
- **gRPC or another RPC framework.** Rejected for v1 — adds a real
  dependency and generated-code build step for a phase whose own proving
  case is one local subprocess exchanging a handful of small JSON
  messages; revisit only if a real, demonstrated need (e.g. streaming,
  bidirectional push, cross-machine execution) appears.
- **A plugin/marketplace discovery mechanism** (auto-discovering
  installed adapters via some registry). Rejected for v1 — Phase 60 has
  exactly one external adapter to run; a fixed, explicit invocation path
  is simpler and the registry question can wait for a second real
  adapter to exist.
- **JSON-RPC 2.0, adopted wholesale.** Rejected — its batch-request and
  notification (no-response) features aren't needed by a synchronous,
  one-adapter-at-a-time first version; this protocol borrows JSON-RPC's
  `id`/`result`/`error` shape (a well-proven, minimal pattern) without
  importing a JSON-RPC library or its fuller feature set.

## Consequences

- `src/codecompass/adapters/external_process.py` (new): a fully generic
  JSON-Lines subprocess client (`spawn` → `initialize` → `analyze_project`
  → `shutdown`) with **zero ecosystem-specific knowledge** — reusable by
  any future external-process adapter (a COBOL one, or a second Haskell
  variant), not rewritten per ecosystem.
- `src/codecompass/adapters/haskell.py` becomes a thin dispatcher: reads
  `package.yaml` directly (via `yaml.safe_load()`) for simple fields,
  computes the resolved monorepo package path, and delegates to
  `external_process.py` for the dependency-tree/API-surface halves.
- A new, small Haskell program (a single-file `stack script`, using
  `aeson` for JSON — confirmed working in this development environment:
  a cold build succeeds, `aeson` resolves and compiles against the
  already-pinned snapshot resolver, and a warm re-run completes in
  ~3 seconds) lives in a new top-level `adapters/haskell/` directory,
  **outside** `src/codecompass/` entirely — no Python code imports
  anything from it, and nothing in `src/codecompass/`'s own build/test
  process depends on it existing to run CodeCompass's own test suite
  (its own tests are skip-if-unavailable, matching `decisions/0014`'s
  existing posture for the Cargo adapter).
- `decisions/0002` is **not superseded** — in-process native-tooling
  adapters remain the default, lower-overhead strategy for an ecosystem
  whose tooling can be shelled out to safely and whose license poses no
  concern; this ADR adds a second, deliberately heavier-weight strategy
  for the specific case that motivates it (a future adapter that cannot
  or should not be in-process Python code).

## Explicit non-claim: this does not settle the GPL licensing question

**Process separation and a documented wire protocol are an architectural
property, not a legal conclusion.** Running as a separate OS process
communicating over a narrow, generic JSON protocol is a reasonable
technical design for modularity and future flexibility — it does **not**
by itself establish that a proprietary adapter distributed this way
would qualify as GPL's "mere aggregation" or an independent program under
the GPL-3.0-or-later license CodeCompass ships under
(`decisions/0053`), rather than a combined/derivative work subject to
GPL's own copyleft terms. Factors a court or a qualified reviewer would
actually weigh (how tightly the two are distributed together, how
CodeCompass's own installation/packaging bundles or depends on a
specific adapter, whether the protocol itself embeds anything derived
from CodeCompass's own copyrighted code, and more) are outside this
ADR's competence to resolve and outside this project's own established
practice of treating licensing questions as engineering decisions.
**Any future proprietary or alternatively-licensed adapter distribution
model must receive review from a qualified open-source/IP legal
specialist before being relied upon** — this ADR documents a real,
useful architectural boundary and explicitly does not claim it is a
substitute for that review.
