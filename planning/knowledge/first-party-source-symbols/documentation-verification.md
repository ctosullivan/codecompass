# Documentation verification: first-party-source-symbols

Frozen per `codecompass-template`'s `documentation-verification/TEMPLATE.md`
shape. Questions written now, **before** the topic's documentation is
published, so the fresh Q&A dispatch's answers can't be shaped by having
watched the doc get written.

## Documentation-only Q&A — frozen questions

1. What is `Language`, and why is it a separate concept from the
   pre-existing `core.Ecosystem`?
2. What are the five possible values of `symbol_index_status`, and what
   is the practical difference between `indexed` and `indexed_partial`?
3. What are the five possible values of a first-party symbol's
   `exposure`, and give one real example of each that the documentation
   cites.
4. A function is declared twice in the same file via `@overload`. Does
   this project's first-party symbol tracking record one row or two for
   it? Why?
5. If `meta.source_index_version` has never been set for a project, what
   does that mean, and how would a caller find out?
6. Name one thing this subsystem is documented as NOT handling (a
   limitation), and what actually happens when that case is hit.

## Coding-context task — frozen scope

**Task**: "Add support for extracting first-party symbols from a new
language the project doesn't currently support." Using only a
coding-context packet generated from this topic's frozen snapshot (not
the full documentation, not the source code directly), identify: which
existing extractor function is the right template to copy, what the
`SymbolIndexStatus` value should be set to for a naive/coarse first
implementation, and what the minimum schema-relevant fact is that must be
true of every symbol row this new extractor produces.

## Results

(Filled in after documentation is published and both dispatches run —
see `documentation-verification.md`'s own Results section once complete.)
