# Integrating a new external-process adapter

A practical guide, grounded in what the reference Haskell adapter
actually does, for anyone building a **second** external-process adapter
(the motivating future case named in `decisions/0057` is a proprietary
COBOL/mainframe adapter suite that could never be distributed as
importable GPL-licensed Python code inside `src/codecompass/`). See
[`wire-protocol.md`](wire-protocol.md) for the message shapes this guide
assumes.

## What CodeCompass provides for free

`src/codecompass/adapters/external_process.py`'s `ExternalAdapterProcess`
is a **fully generic JSON-Lines subprocess client** — confirmed by its
own docstring and by grep: it never mentions Haskell, `stack`, or
`package.yaml` anywhere in its own source, and has no import dependency
on either submodule's content. It is reusable, unmodified, by any future
external-process adapter. It handles:

- Spawning the subprocess (`subprocess.Popen`, pipes on
  `stdin`/`stdout`/`stderr`).
- The `initialize` handshake, including the `protocol_version` mismatch
  check.
- Framing every request/response as one JSON-Lines message, with
  auto-incrementing `id`s.
- Mapping a protocol `error` response onto `AdapterError` — the same
  exception every in-process adapter method already raises, so calling
  code never needs an `if external: ... else: ...` branch.
- `shutdown()`'s timeout-then-kill sequence.

**What it does not do**: resolve which directory to hand `analyze_project`
(that's the adapter's own job, per the monorepo rule below), locate or
build the external executable, or know anything about your specific
ecosystem.

## What your own Python-side adapter class must do

Following `HaskellAdapter`'s own shape
(`src/codecompass/adapters/haskell.py`) as the worked template:

1. **Subclass `EcosystemAdapter`** (`adapters/base.py`), implement the
   five abstract methods. Simple manifest-key lookups
   (`installed_version`, `repository_url`) can stay in-process — reading
   a config file with your ecosystem's native format
   (`yaml.safe_load`, `tomllib.load`, whatever fits) is not "ecosystem-
   specific implementation code" in the sense `decisions/0057` cares
   about; it's the same class of code `discovery.py` already does for
   every other ecosystem's manifest.
2. **Delegate real logic to the external process.** Anything that
   embodies actual ecosystem-specific *logic* — build-tool dependency-
   tree resolution, source-file API-surface extraction — belongs in the
   external process, not reimplemented in Python. Construct one
   `ExternalAdapterProcess([executable_path])` per `analyze_project` call
   site (not reused across projects), call `.initialize()`, then
   `.analyze_project(project_root, package_name)`, then `.shutdown()`.
3. **Resolve monorepo package roots yourself, before calling
   `analyze_project`.** If your ecosystem can have multiple packages
   under one `project_root` (the way Haskell's Stack monorepos do), your
   adapter — not the external process — must search for the right
   subdirectory. Set `RepositoryLocation.subdirectory` when the resolved
   directory differs from `project_root` itself, so
   `source_resolution.resolve_and_clone` knows the cloned repository
   root isn't itself the package's own source tree.
4. **Convert the wire response into CodeCompass's own types**, in your
   adapter class, not in `external_process.py`:
   `dependencies` → `DepNode` (recursively), `symbols` → `Symbol`
   (mapping the wire's `kind` field onto `Symbol.export_kind` 1:1 — see
   [`../../architecture/core-data-model.md`](../../architecture/core-data-model.md)
   for why that field is deliberately narrow).
5. **Consider a per-instance cache** if more than one of your adapter's
   methods needs `analyze_project`'s result — `HaskellAdapter`'s own
   `_cached_analysis` avoids re-running the full external request three
   times per vendor per call site, at the cost of one still-open,
   disclosed inefficiency: the cache is per-instance, not per-project, so
   `sync_vendor` and `rebuild_project_graph` (which each construct their
   own adapter instance) still each pay for the external process once.
6. **Register in the dispatch table** (`adapters/__init__.py`'s
   `_ADAPTER_BY_ECOSYSTEM`) and add the new value to `core.Ecosystem`.
   Both are closed, total mappings — there is no plugin-discovery
   mechanism to hook into instead.

## What the external process itself must do

Independent of language, per [`wire-protocol.md`](wire-protocol.md):

- Read one JSON object per line on `stdin`, write one per line on
  `stdout`, exactly one outstanding request at a time.
- Respond to `initialize` with your `protocol_version` (currently `1`),
  `adapter_name`, `adapter_version`, `ecosystem` (free text), and the
  subset of the four capabilities you can actually produce.
- Only return an `analyze_project` result section you declared as a
  capability.
- Reject any method outside `initialize`/`analyze_project`/`shutdown`
  with `{"error": {"code": "unsupported_capability", ...}}`.
- Use `kind`/`note` on a `symbols` entry honestly if your extraction
  can't always resolve confident export status — don't silently emit
  `"export"` for something you're not sure about; `decisions/0059`'s own
  reasoning ("an honest gap beats a confident guess") is a project-wide
  posture, not a Haskell-specific one.

## Licensing — read this before choosing your adapter's license

Process separation and a documented wire protocol are an **architectural
property, not a legal conclusion**. `decisions/0057`'s own "Explicit
non-claim" section and `decisions/0058`'s own restatement both say
plainly: this design does not by itself establish that a proprietary
adapter distributed this way is GPL's "mere aggregation" or an
independent program under CodeCompass's own GPL-3.0-or-later license.
**Any future proprietary or alternatively-licensed adapter distribution
model needs review from a qualified open-source/IP legal specialist**
before being relied upon — this is not something either ADR, or this
guide, resolves.

If your new adapter is intended to ship under a different license than
CodeCompass's own (GPL-3.0-or-later), the reference pattern —
demonstrated, not merely described — is `codecompass-adaptor-haskell`:
its own separate public repository, its own `LICENSE` file (in that
case, matching GPL since the reference adapter has no reason to differ),
checked out as a git submodule, never imported by Python code, only
invoked as an opaque subprocess.

## Worked example: how the pieces actually fit together for Haskell

| Layer | Repository | License | What lives there |
|---|---|---|---|
| CodeCompass core | `codecompass` (this repo) | GPL-3.0-or-later | `HaskellAdapter` (thin dispatcher), `ExternalAdapterProcess` (generic client) |
| Protocol contract | `codecompass-adaptor-protocol` (submodule at `protocol/codecompass-adaptor-protocol/`) | MIT | `SCHEMA.md`, `schemas/*.json`, `examples/`, `conformance/` — no code from either side |
| Reference adapter | `codecompass-adaptor-haskell` (submodule at `adapters/haskell/`) | GPL-3.0-or-later | The real Stack project implementing the protocol against real `.hs`/`package.yaml`/`stack` semantics |

Three independent commit histories, three independent version streams —
a version-compatibility matrix (which combinations were actually tested
together) is expected to be kept current as any of the three advances;
see [`wire-protocol.md`](wire-protocol.md)'s own table for the current
entry (Phase 60: CodeCompass this commit, protocol `0.1.0`, adapter
`0.1.0`, `protocol_version` `1`).

For step-by-step clone/build/submodule-update instructions as an end
user (not an adapter *implementer*), see
[`../developer/haskell-adapter-submodules.md`](../developer/haskell-adapter-submodules.md)
directly.
