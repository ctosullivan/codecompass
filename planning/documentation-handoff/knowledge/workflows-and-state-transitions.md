# Workflows and state transitions (curated synthesis)

A curated selection of already-existing canonical Claims whose own
`assertion_kind` is `state_transformation` (or whose content otherwise
describes a real state machine/workflow), across the selected handoff
slugs. **No canonical render target exists for this category today**
(the renderer folds `state_transformation`/`workflow`-tagged Claims into
`interfaces-and-behaviours.md`) — this file is a reorganization, not a
re-derivation, of content already present there.

Only one Claim across all four selected slugs carries this
`assertion_kind` as of this handoff. This is reported honestly rather
than padded with unrelated content to look more complete than the
underlying knowledge base currently is.

## From `first-party-source-symbols`

### CL-FPSS-003 — the five-state `SymbolIndexStatus` model

> The five-state SymbolIndexStatus model (indexed/indexed_partial/
> unsupported/parse_error/unreadable) exists to prevent a bare empty
> symbols list from ambiguously standing in for more than one real
> cause. `indexed` and `indexed_partial` are distinguished purely by
> extraction *technique fidelity*, never by whether anything was found:
> `indexed` means a real structural parser (Python's `ast.parse`) ran and
> either succeeded (possibly finding zero symbols) or the extractor
> never reaches this status if parsing itself failed; `indexed_partial`
> means a coarse line-scan/regex heuristic ran (Rust, JS, TypeScript) —
> a technique with no real parse step, so it can never fail
> structurally the way `ast.parse` can, and is dispatched unconditionally
> on successful file read regardless of what (if anything) it finds.
> `unsupported` means no extractor exists for the file's language at all
> (Haskell today) — the file is never even opened. `parse_error` is
> Python-specific (`ast.parse` raising `SyntaxError`) since Rust/JS/TS
> have no real parse step to fail. `unreadable` applies to any language
> (`OSError` or `UnicodeDecodeError` on read). No code path in this
> module ever returns `indexed_partial` for Python or `indexed` for
> Rust/JS/TS — the mapping from language to indexed-vs-indexed_partial is
> fixed, not content-dependent.

Real test-confirmed examples (from the Claim's own `examples` field):
a syntactically valid, symbol-free Python file → `INDEXED` with
`symbols=()`; a Python file with a genuine `SyntaxError` → `PARSE_ERROR`
with a populated diagnostic; a Haskell file, however well-formed →
`UNSUPPORTED` without ever being opened.

Supporting evidence: `EV-FPSS-006`, `EV-FPSS-007`, `EV-FPSS-020` — see
`source-and-evidence-map.md`.
