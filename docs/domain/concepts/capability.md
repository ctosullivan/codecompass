---
status: DRAFT — pending domain-skeptic review and actual-user approval
---

# Capability

## Definition

**"Capability" is the external adapter wire protocol's own specific,
closed term** (`decisions/0057`, `protocol/codecompass-adaptor-protocol/SCHEMA.md`):
one of exactly four strings — `dependencies`, `symbols`, `observations`,
`diagnostics` — declared once by an adapter in its `initialize`
response, gating which of `analyze_project`'s four result sections that
adapter may legitimately return. `src/codecompass/adapters/external_process.py`'s
own `CAPABILITIES` constant is this closed 4-tuple, hard-coded there
(not imported from the protocol submodule) specifically so the Python
client has zero filesystem dependency on that submodule being checked
out to be importable (`EV-ADPT-009`).

## What it is NOT

- **Not the same as casually calling something a CodeCompass
  "feature."** `capability` has a closed enumeration, a declaration
  mechanism (the `initialize` handshake), and a real gating effect (an
  adapter cannot return a `symbols` section unless it declared the
  `symbols` capability). **"Feature" has none of this** — it is used
  throughout this project's own ADRs, plans, and roadmap prose as
  ordinary, unscoped English for "a thing CodeCompass does or
  delivers" (e.g. "as one feature spread across three modules,"
  `decisions/0051:21`; "one well-meaning feature away from unproven
  content look like fact," `decisions/0054:117`), with no enumeration,
  no handshake, and no schema constraint attached anywhere
  (`EV-ADPT-009`). Calling `symbols()` "a feature" is not wrong English,
  but it is a different, weaker claim than saying an adapter
  "declared the `symbols` capability."
- **Not validated against its own closed set by the receiving code.**
  See "Counterexample" below — this is a real, observed gap, not a
  hypothetical one.
- **Not itself a source/table/schema concept.** `capability` belongs
  entirely to the wire protocol layer; it has no `context-graph.db`
  counterpart and is never written to that database.

## Invariants

- Exactly four values exist in the closed set:
  `dependencies | symbols | observations | diagnostics`
  (`EV-ADPT-003`).
- An `analyze_project` response section is present **only if** the
  adapter declared the matching capability at `initialize`
  (`EV-ADPT-003`).

## Example

`HaskellAdapter.dependency_tree()` raises `AdapterError` with the
message "...external Haskell adapter did not report a 'dependencies'
capability" if the `dependencies` result section is absent from the
external process's response — a direct, real consumer of the
capability concept gating what the caller may rely on
(`src/codecompass/adapters/haskell.py:100-107`, `EV-ADPT-009`).

## Counterexample / edge case

**The received `capabilities` list is not itself validated against the
closed 4-value set at parse time.** `ExternalAdapterProcess.initialize()`
stores `tuple(response.get("capabilities", []))` directly — nothing in
`external_process.py` checks each entry is one of the four known
strings. An adapter reporting a fifth, unrecognized capability string
would be accepted uncomplainingly by the Python client; the closed-set
discipline currently rests entirely on the specification (SCHEMA.md)
and on well-behaved adapters, not on enforcement code in this
repository (`OBS-ADPT-005`).

A second, softer edge case: even the word "capability" itself is
sometimes used in this project's own prose in a looser, non-protocol
sense — `sync.py:244` describes `symbols()` itself as "the generic
adapter capability every ecosystem now implements," which does **not**
refer to the wire protocol's closed set at all (in-process adapters,
which never speak this protocol, have `symbols()` too). The Claim on
file (`CL-ADPT-006`) is scoped specifically to the wire-protocol sense
of "capability," not a blanket assertion that every English use of the
word in this codebase is the closed-set one.

## Relationships

- **is-declared-by** an `adapter.md` instance (the external-process
  strategy only) as part of speaking `protocol.md`.
- **gates** which `analyze_project` result sections a given adapter may
  return.
- **is-distinct-from** ordinary "feature" language used elsewhere in
  this project.

## References

- `EV-ADPT-003`, `EV-ADPT-009` — `planning/knowledge/codecompass-domain/`
- `CL-ADPT-003`, `CL-ADPT-006` — `planning/knowledge/codecompass-domain/`
- `src/codecompass/adapters/external_process.py:28-34, 53-84`
- `src/codecompass/adapters/haskell.py:99-107`
- `protocol/codecompass-adaptor-protocol/SCHEMA.md:34-58`
- `decisions/0051-agent-suggested-context-is-captured-not-graphed.md:21`
- `decisions/0054-agent-driven-enrichment-is-a-second-non-authoritative-producer.md:117`
