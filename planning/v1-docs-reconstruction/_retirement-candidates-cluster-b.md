# Retirement candidates — Cluster B (architecture + protocol/adapter)

Per Phase 64 §2: concepts the *current* docs spend words on that the
*current system* no longer justifies, scoped to this cluster's own area
(`architecture/`, `docs/external-adapters.md`). The lead consolidates
this with Cluster A's and Cluster C's own lists into one
`concepts-to-retire.md` — this file is Cluster B's own input to that
step, not a final decision.

## 1. `architecture/overview.md`'s "Grounded description — retired" section (lines 471-523)

The section's own title says "retired," and its content describes
`codecompass.grounded_description` — a module **deleted** as of Phase 16
(`decisions/0035`). A current-state-only architecture document (this
phase's own governing principle, `documentation-lifecycle.md` §3) has no
reason to devote 53 lines to explaining a mechanism that no longer
exists in `src/`, however carefully framed as history. This proposal's
own `architecture/sync-and-enrichment-pipeline.md` and `core-data-model.md`
describe the *current* mechanism (`sync_vendor`'s read-only enrichment
lookup) without any reference to what it replaced — everything a reader
needs to understand today's behavior is captured there. **Candidate for
removal, not retention-with-trimming** — unlike a genuinely load-bearing
historical caveat, nothing here is still true of the running system. Its
one substantively load-bearing paragraph (`description_error` is set
only by a clone failure, not a description failure, and is unrelated to
whether a vendor's Description section renders) already appears,
current-tense, in this proposal's own `core-data-model.md`'s
`VendorDigest` section.

## 2. Heavy per-ecosystem implementation prose in `architecture/overview.md`'s "Adapter interface" section

The current section (lines 85-233) carries substantial per-adapter
implementation detail — npm's exact `npm ls <name> --json --all` flag
requirement, the 5-file `.d.ts` cap, Python's `pipdeptree` invocation
path and `--json`-vs-`--output json-tree` distinction, Cargo's
"unverified against real cargo output" disclosure — that is **already
present, verbatim or near-verbatim, in each adapter module's own
docstring** (`adapters/npm.py`, `adapters/python.py`, `adapters/cargo.py`,
confirmed by reading each file directly during this phase's research).
This is not a factual staleness finding — the content agreed with the
code in every spot-checked case — but a **duplication** candidate: two
places that must be kept in sync by hand for no structural reason, since
one of them (the docstring) is unconditionally colocated with the code it
describes and can't drift silently the way a separate prose document can.
This proposal's own `architecture/adapter-interface.md` deliberately
keeps this section's the-same-facts thinner (contract + strategy + one
comparison table), pointing at the module docstrings for the ecosystem-
by-ecosystem detail rather than re-narrating each adapter's own internals
a second time. Candidate for **trim, not remove** — the *existence* of
each ecosystem's own quirks (dev_only handling differences, no
`rustdoc --output-format json` yet, etc.) is real signal worth a reader
knowing exists, even if the exact flag-level detail doesn't need a
second home.

## 3. `docs/external-adapters.md` itself — no drift found, name it as a non-finding

This proposal's `protocol-adapter/` set was written to check
`docs/external-adapters.md` against the real submodules/code, per this
phase's own instruction, not to duplicate it. What was found: this file
is **already current and accurate** — its cloning instructions, its
"Naming note" about the adaptor/adapter spelling discrepancy (matching
what `docs/domain/concepts/protocol.md` independently found), its
version-compatibility table, and its commit-independence rules all check
out against the real submodules and ADRs. **No retirement candidate
here** — recorded explicitly so the lead doesn't need to re-derive this
during Phase 65's reconciliation: this is one doc in this cluster's scope
that this proposal's own `protocol-adapter/wire-protocol.md` and
`integrating-a-new-external-adapter.md` should be checked *against* for
consistency, not assumed to supersede.

## Not a retirement candidate, but a boundary worth naming for Phase 65

`architecture/overview.md` itself already documents (in its own "Adapter
interface" opening lines) the two-unrelated-senses-of-"adapter" ambiguity
this phase's research also confirms independently
(`docs/domain/concepts/adapter.md`). This is a real, disclosed, existing
piece of self-awareness in the current doc, not a drift finding — noted
here only so Phase 65 doesn't need to re-discover that the current doc
already flags this itself.
