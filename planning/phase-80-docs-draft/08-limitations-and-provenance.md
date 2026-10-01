# Limitations and provenance

This file is the single place this draft's confidence boundaries are
mapped end-to-end, rather than scattered one caveat per page. See
`00-INDEX.md` for why this file exists as its own document.

## Genuine, confirmed implementation gaps

All of the following are stated directly, confirmed by reading or
running real code — not inferred or guessed — per
`phase80-implementation-reconstruction.md` §8 and the alignment report's
"new gaps surfaced" section.

- **`config.py` silently discards a legacy `depth` key** from
  `vendor.toml`, with no warning or migration. A user with a stale
  `depth = ...` entry gets no signal it is being ignored. See
  `03-configuration.md`.
- **`discover_python` does not scan `[project.optional-dependencies]`**
  — stated directly in its own docstring as a known, accepted
  limitation.
- **`discover_haskell` does not expand hpack's `when:`-block conditional
  dependencies** — likewise stated directly in its own docstring.
- **`PythonAdapter.dependency_tree()`'s `dev_only` field is always
  `False`** — confirmed live by a passing test
  (`test_dev_only_always_false`). This is a structural limitation of the
  underlying `pipdeptree` JSON tree output, which does not carry a
  dev/non-dev distinction at all, not an oversight CodeCompass's own code
  tries to hide — its docstring states this is an intentional "safe
  default over forced complexity."
- **Symbol names are not globally unique across vendors** — the `query
  symbol NAME` command's own behavior depends on this; see
  `02-cli-reference.md`.
- **The `promote` CLI command has been removed** — a confirmed,
  historical surface change (see `02-cli-reference.md`).
- **Schema-migration safety depends entirely on direct schema
  introspection**, because `meta.schema_version` was reportedly bumped
  twice historically for unrelated changes (per the code's own comments,
  not independently re-verified in this evidence base against project
  history) which would have falsely triggered migrations if trusted. The
  current introspection-based defense is directly confirmed by passing
  migration tests. See `04-architecture-persistence.md`.

## What could not be run, and why

The bounded export this draft's evidence was built from is not a
runnable whole. `src/codecompass/cli.py` and `src/codecompass/sync.py`
(and, transitively, the adapter package) import sibling modules that
were deliberately **not included** in that export:

`enrichment`, `relation_enrichment`, `chat`, `index`, `skill`,
`source_resolution`, `staleness`, `filetree`, `symbols`, `git_topology`,
`skill_scan`, `source_symbols`, `spec_docs`, `usage`, `claude_md`,
`deptree`, `doc_mapping`, and the `npm`/`cargo`/`haskell` adapter
modules.

Confirmed directly: `codecompass --help` and `python -c "import
codecompass.cli"` both fail with `ImportError`. Of 10 real test files
in the export, 5 fail to even import for the same transitive reason
(`test_cli.py`, `test_sync.py`, `test_adapters_base.py`,
`test_adapters_dispatch.py`, `test_adapter_python.py`); the other 5
(`test_commands.py`, `test_config.py`, `test_core.py`, `test_discovery.py`,
`test_graph.py`) collected and ran, producing 116 passed, 1 failed. That
one failure (`test_load_valid_vendor_config`) was traced to a missing
`tests/fixtures/` directory in the export — an export-completeness gap,
not a real code defect.

This is why this draft's files carry two distinct confidence tiers
rather than one: `graph.py`, `config.py`, `discovery.py`, `commands.py`,
and `core.py` are CONFIRMED-LIVE; `cli.py`, `sync.py`, and the adapter
layer are CONFIRMED-BY-READING only.

## Modules excluded from this draft entirely

Per the Stage 3 alignment report's own explicit guidance, this draft
says nothing about the actual internal behavior of the following — they
were deliberately excluded from the bounded export, and only the calling
code's own imports, call signatures, and docstring-stated expectations
of them are available:

`enrichment.py`, `relation_enrichment.py`, `chat.py`, `index.py`,
`skill.py`, `source_resolution.py`, `staleness.py`, `filetree.py`,
`symbols.py`, `git_topology.py`, `skill_scan.py`, `source_symbols.py`,
`spec_docs.py`, `usage.py`, `claude_md.py`, `deptree.py`,
`doc_mapping.py`, and the `npm`/`cargo`/`haskell` adapters.

Examples of inferred call contracts (not confirmed implementations) this
draft relies on where it must mention these modules at all: a cloning
helper is expected to raise a specific "source resolution" error on
failure; a symbol extractor is expected to return objects with
`.name`/`.purpose`/`.export_kind`/`.note` attributes; a usage-resolution
function is expected to yield path/import pairs with `.vendor`/
`.symbol_name`/`.line` attributes. None of this is guessed — it is read
directly from how the present, confirmed code calls these functions and
uses their results — but it is still one step removed from confirming
what the functions actually do internally.

## The domain-concept corpus's own coverage gap

The 25 active Claims in `codecompass-overview@v1` are almost entirely
meta-level knowledge-model concepts (adapter protocol, the
Evidence/Claim/Derivation/Decision/Requirement model, "context"'s five
senses, relationship/edge, reference, digest, provenance) plus two
project-process concepts. Only a minority have direct implementation-level
content to check against the reconstruction; the independent alignment
report found **zero real conflicts**, but it also found that 14 of the 25
Claims are `insufficiently_verified` against this specific bounded
evidence — not because anything is wrong, but because the Claim's subject
matter (an external protocol repository, planning/process documents,
ADR history) was simply outside what a `src/`+`tests/`-only export could
ever speak to. This draft cites only the Claims whose subject matter
genuinely overlaps product or architecture content; it does not promote
any Claim's status, and neither did the alignment report, per that
role's own hard rule that implementation conformance shows code matches
a stated assertion, not that the assertion itself is correct.

## Citation discipline this draft follows

Every substantive statement in this draft is tagged with one of the four
tiers defined in `00-INDEX.md` (CONFIRMED-LIVE, CONFIRMED-BY-READING,
CLAIM-CITED, OUT-OF-SCOPE/INFERRED), and domain-concept citations use the
form `codecompass-overview@v1#CL-XXX-NNN`, naming the exact Claim id in
the snapshot this draft was built from. This mirrors the same citation
discipline the knowledge-base records themselves use (every Claim cites
its own supporting Evidence and Derivation by id) — the point is that a
reader of this draft should never have to take an unsourced sentence on
faith, and should always be able to tell, from the sentence itself or
its immediate surrounding tier banner, exactly how sure the project can
currently be of it.
