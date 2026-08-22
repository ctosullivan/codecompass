# Phase 26: Symbol-level resolution for `module.attr` usage

## Scope

Found during a `/discovery` exploration session against this repo itself
(not a pre-planned phase — a real gap surfaced by actually using the
tool's own output and reading real query results, not guessed at).

`usage.detect_python_imports` deliberately treats a plain `import X`
statement as vendor-level only (`symbol_name=None`) — its own docstring
says so: "`import rich` binds no specific symbol." That's correct as far
as it goes, but nothing *upgrades* a vendor-level usage to symbol-level
once the imported module is actually used via attribute access
(`anthropic.Anthropic(...)`, `anthropic.AnthropicError`), which is a very
common Python style and, empirically, this project's *own* dominant style
for `anthropic` specifically (`import anthropic` at the top of `chat.py`/
`enrichment.py`/`relation_enrichment.py`, then `anthropic.Anthropic`/
`anthropic.AnthropicError`/`anthropic.AnthropicError` used throughout).

Confirmed directly against this repo's own `context-graph.db`: all 6
`uses_edges` rows for `anthropic` have `symbol_id = NULL`. Consequence,
also confirmed directly: `codecompass check`'s "Documented but unused"
section lists `Anthropic`, `AnthropicError`, and 33 other real,
definitely-used `anthropic` symbols as unused — because there is no
symbol-level edge for any of them, even though the vendor-level grounding
(what the technical description draws from) works fine. `rich`/`typer`
aren't affected the same way in this repo, because this codebase happens
to import a few of their symbols via `from rich import X` style, which
`detect_python_imports` already resolves correctly — this is a real gap
in the `import X` + attribute-access path specifically, not a wholesale
failure of usage detection.

**Covered:**
- `usage.detect_python_imports`: after recording a vendor-level `import X`
  (or `import X as alias`) `DetectedImport`, walk the *same file's* AST for
  `ast.Attribute` nodes whose value chain resolves back to `X` (or its
  alias) as a bare `ast.Name` — e.g. `X.Y` → an additional
  `DetectedImport(vendor=X, symbol_name="Y", line=<attribute's line>)`.
  Only the immediate attribute off the bound name counts (`anthropic.
  Anthropic` → symbol `Anthropic`; `anthropic.types.SomeType` → symbol
  `types`, not `SomeType` — matching how `from X import types` would
  itself resolve, i.e. treating the first dotted attribute the same way
  `ImportFrom` treats the first dotted import component, not attempting a
  deeper attribute-chain resolution that would need real type inference
  to get right).
- Handle the aliasing case (`import anthropic as a` then `a.Anthropic`) by
  tracking the bound local name (`alias.asname or alias.name`), not
  assuming the bound name always equals the vendor name.
- Emit the attribute-level `DetectedImport` *in addition to* the existing
  vendor-level one from the `import` statement itself, not instead of it —
  both are real signal (the plain `import` line is still real evidence the
  vendor is used, independent of which specific attributes get resolved).
  A file that imports a vendor but is later found to use zero of its
  attributes still correctly keeps its vendor-level `uses_edges` row.
- A symbol resolved this way must still match a real symbol name already
  known to `symbols.py`'s extraction for that vendor (the existing
  `sync.py` resolution step that turns `DetectedImport.symbol_name` into a
  `symbol_id` already does this lookup and already tolerates an unresolved
  name falling back to vendor-level — reuse that, don't duplicate it) —
  this phase only needs `usage.py` to *emit more candidate symbol names*,
  not to change how those names get resolved to `symbol_id`s.

**Explicitly deferred / out of scope:**
- Deeper attribute-chain resolution (`anthropic.types.something.Deep`) —
  only the first attribute off the bound import name is resolved, matching
  the existing `ImportFrom` precedent's own depth (first dotted
  component only).
- Any equivalent upgrade for the npm/Rust detectors (`detect_npm_imports`/
  `detect_rust_imports`) — this phase is scoped to the concrete gap found
  (Python `import X` + attribute access), not a general audit of every
  ecosystem's detector. Worth a follow-up look if a similar gap turns up
  there, not assumed to exist without evidence the way this one now has.
- Re-running real usage-driven enrichment against this repo to see the
  improved symbol coverage — natural manual verification step (see below),
  not a reason to touch `enrichment.py` itself, which is unaffected by
  this phase.

## Design decisions

**Resolve via a second AST pass over `ast.Attribute` nodes, not by
rewriting `ast.Import`'s handling.** The existing vendor-level `import X`
detection is correct and shouldn't change — attribute resolution is
additive, layered on top, so a regression here can't silently stop
recording the vendor-level fact that `import X` already proved.

**Only resolve the immediate attribute, not walk deeper chains.**
Considered resolving arbitrarily deep attribute chains
(`anthropic.resources.messages.Messages`) to their leaf name. Rejected:
without real type information, a deep chain's leaf attribute is often not
actually the name of a top-level exported symbol at all (it could be a
sub-module, an instance attribute, anything) — the *first* attribute off
the imported name is the one place this is reliably a plausible top-level
symbol candidate, mirroring exactly how `ImportFrom` already only takes
the first dotted component of `module` as the vendor name, not a deeper
guess. Consistent, not a new precedent.

## Files

- `src/codecompass/usage.py` — `detect_python_imports` (or a small new
  helper it calls) gains the attribute-resolution pass.
- `tests/test_usage.py` — new fixture cases: `import X` + `X.Attr(...)`
  resolves an attribute-level `DetectedImport`; `import X as y` + `y.Attr`
  resolves via the alias; a deep chain (`X.sub.Attr`) resolves only to the
  first attribute (`sub`), not `Attr`; a file with `import X` but no
  attribute access still keeps its existing vendor-level-only detection
  unchanged (no regression).
- `architecture/overview.md` — "Usage detection" section gets a short
  note on this resolution step, alongside the existing description of
  `ImportFrom`'s first-dotted-component rule.
- `decisions/` — a new ADR is likely not warranted (this is a bug-fix-
  shaped detection improvement to an already-documented mechanism, not a
  new architectural tradeoff) — confirm at implementation time whether
  the actual diff turns out to involve a real non-obvious call, and write
  one only if it does.

## Verification

- `pytest`/`ruff check .` — full suite passes, new fixture cases included.
- Manual, against this repo itself (the established dogfooding pattern):
  re-run a whole-project `sync`, then confirm via `sqlite3 context-graph.
  db` or `codecompass query vendor anthropic --json` that at least
  `Anthropic`/`AnthropicError` now have real `symbol_id`-backed
  `uses_edges` rows; confirm `codecompass check`'s "Documented but unused"
  section for `anthropic` shrinks to reflect genuinely-unused symbols only
  (the SDK's error subclasses codecompass doesn't itself construct, e.g.
  `RateLimitError`, `NotFoundError`, are expected to still legitimately
  show as unused — the fix should narrow the list, not necessarily empty
  it).
