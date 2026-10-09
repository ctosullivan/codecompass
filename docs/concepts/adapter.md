# Concept: adapter

An **adapter**, in CodeCompass's ecosystem-integration sense, is a concrete subclass of `EcosystemAdapter` (`src/codecompass/adapters/base.py`), constructed once per `(VendorConfig, project_root)` pair, implementing five abstract methods — `installed_version`, `source_location`, `readme_and_api_surface`, `repository_url`, `dependency_tree` — plus one concrete, overridable method, `symbols()` (added later, for structured API-surface extraction into the context graph).

Exactly one adapter class exists per `Ecosystem` enum member, selected by a single closed dispatch table (`get_adapter` in `src/codecompass/adapters/__init__.py`) — never by naming convention, plugin discovery, or a configuration string:

| Ecosystem | Adapter class | Strategy |
|---|---|---|
| `npm` | `NpmAdapter` | in-process |
| `python` | `PythonAdapter` | in-process |
| `cargo` | `CargoAdapter` | in-process |
| `haskell` | `HaskellAdapter` | external-process |

## Two coexisting implementation strategies

**In-process** (npm, Python, Cargo) — an ordinary importable Python class inside `src/codecompass/`, shelling out to the ecosystem's own native tooling via a shared subprocess seam (`_run_json` in `base.py`), which tests monkeypatch per-module to inject fixture JSON instead of invoking a real toolchain.

**External-process** (Haskell, the reference implementation) — `HaskellAdapter` is deliberately thin: it reads `package.yaml` directly (a small, mechanical, single-field read — not a full YAML parser; see `docs/reference/symbol-extraction.md`) and resolves which subdirectory of a possibly-monorepo project root is the actual target package. Every piece of real Haskell-specific *logic* — dependency-tree construction via `stack`, `.hs`-source API-surface extraction — is delegated to an independent OS subprocess (`codecompass-adaptor-haskell`) speaking a small JSON-Lines wire protocol (`src/codecompass/adapters/external_process.py`; see `docs/reference/protocols.md`).

Neither strategy supersedes the other — this is a stated, deliberate design, not a staged migration (`decisions/0002` governs the first strategy; `decisions/0057` adds the second, explicitly "not superseded"; the in-process strategy remains the default, lower-overhead one). The motivation for the second strategy is ecosystems whose real implementation cannot or should not live inside CodeCompass's own GPL-covered Python process.

## An edge case: "one vendor, one adapter instance" is not a filesystem guarantee

`HaskellAdapter`'s own monorepo resolution (`_resolve_package_dir`) shows that a single `project_root` can host multiple vendors' worth of source at once — e.g. `hledger-lib`, `hledger`, and `hledger-ui` all living inside one `hledger` checkout. The adapter *instance* is responsible for narrowing `project_root` down to the one subdirectory matching its own vendor's declared name before any other method call on it is meaningful. See `docs/edge-cases-and-compatibility.md`.

## A genuinely fuzzy term: "adapter" has two senses in this project

CodeCompass's own architecture documentation (not visible to this reconstruction, but independently confirmed to exist and to name this ambiguity, via source-and-evidence citations) uses "adapter" for two distinct things:

1. **Ecosystem adapter** — the real `EcosystemAdapter` ABC described above, with real subclasses.
2. **"Host-output adapter"** — a purely expository classification label sometimes applied to `src/codecompass/skill.py`, `commands.py`, and `index.py` (modules that adapt CodeCompass's own internal state into a specific *host tool's* expected output shape — an Agent Skill, a slash command, a `CLAUDE.md` routing table). There is **no corresponding class, interface, or shared base** for this second sense anywhere in the source.

If you encounter the bare word "adapter" in this project without a qualifying phrase, it is genuinely ambiguous which sense is meant — this is a real, known ambiguity in the project's own vocabulary, not something this reconstruction introduced.

## A related, but non-existent, term: "connector"

"Connector" names nothing in CodeCompass's source, tests, or configuration. If you encounter it in a CodeCompass context, the most likely intended referent is either the broader Claude/MCP ecosystem's own "connector" concept (a hosted integration CodeCompass has not implemented — no MCP-related code exists anywhere in `src/codecompass/`), or CodeCompass's own "adapter" (the actual, evidenced mechanism nearest in meaning).
