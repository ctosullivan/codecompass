# Orienting to CodeCompass as a coding agent

**Provenance tier: mixed, tagged per item.** This file collects the
behavioral guarantees most relevant to a coding agent calling CodeCompass
programmatically or editing its source — drawn from the same evidence
base as the rest of this draft, with each item's own tag.

## Guarantees you can rely on when calling the CLI

- **CONFIRMED-LIVE**: `context-graph.db`'s `rebuild_deterministic` never
  touches the three AI-enrichment tables
  (`vendor_enrichment`/`symbol_enrichment`/`doc_relation_enrichment`).
  If you write enrichment through the proper channel and a mechanical
  `sync` runs afterward, your enrichment survives byte-identical. See
  `04-architecture-persistence.md`.
- **CONFIRMED-BY-READING**: every `query`/`enrich` subcommand that needs
  the graph uses a consistent "open-or-note" pattern — a missing
  `context-graph.db` produces a one-line note and a clean return, never
  a traceback and never a silently-created empty database. If you are
  scripting against this CLI, you can treat "graph absent" as a
  distinguishable, calm failure mode rather than something you need to
  pre-check yourself.
- **CONFIRMED-BY-READING**: `enrich apply` has a real mechanical trust
  boundary, not merely an instruction. An entry you submit is accepted
  only if it exactly matches a currently-pending candidate from the
  project's own candidate-selection mechanism (itself out of scope for
  this draft). A non-matching or already-resolved entry is rejected and
  reported, and the whole command exits non-zero if anything was
  rejected. Do not assume submitting well-formed JSON is sufficient —
  the content must match a real pending candidate.
- **CONFIRMED-BY-READING**: `codecompass sync <vendor-name>` (a named
  vendor) never touches the graph and never triggers enrichment; only a
  whole-project `sync` (no vendor name) does either. If you need the
  graph rebuilt, you need the whole-project form.
- **CONFIRMED-LIVE**: symbol names are not globally unique across
  vendors. If you call `query symbol NAME` programmatically, be prepared
  for more than one vendor's symbol to match.

## What you should not assume

Per this draft's scope (`00-INDEX.md`), the following modules' actual
behavior is an **inferred call contract only**, not a confirmed
implementation, because they were deliberately excluded from the bounded
evidence export this draft was built from: `enrichment.py`,
`relation_enrichment.py`, `chat.py`, `index.py`, `skill.py`,
`source_resolution.py`, `staleness.py`, `filetree.py`, `symbols.py`,
`git_topology.py`, `skill_scan.py`, `source_symbols.py`, `spec_docs.py`,
`usage.py`, `claude_md.py`, `deptree.py`, `doc_mapping.py`, and the
npm/cargo/haskell adapters. If a task depends on exactly what one of
these does — not just that it exists and is called from somewhere —
read that module's real source directly rather than relying on anything
in this draft, including `02-cli-reference.md`'s and
`05-runtime-pipelines.md`'s descriptions of the commands that call into
them.

Similarly, `cli.py` and `sync.py` themselves were never executed in the
evidence base this draft was built from. Their call chains and flag
names are a careful read, not a verification. If you are about to make a
behavioral decision (e.g. "will `sync VENDOR` definitely skip
enrichment") that matters for correctness rather than orientation, run
`codecompass --help` / the relevant subcommand's `--help` yourself first.

## If you are asked to write or extend CodeCompass's own documentation

CodeCompass's own project team tracks the provenance of every substantive
claim it makes about itself using a small, named vocabulary (Evidence,
Observation, Claim, Derivation, Decision, Requirement — see
`01-concepts.md`'s second half). If you are asked to add to or revise
this project's documentation, the same discipline this draft follows is
the expected standard: say plainly which of "I ran this and watched it
work," "I read this code and it says this," "this is a cited domain
claim from the approved corpus," and "this is someone's stated future
intent, not current behavior" applies to each thing you write — and
never upgrade one tier into another by omission. See
`08-limitations-and-provenance.md` for the full tier legend this draft
uses, which is a reasonable starting point for that discipline rather
than something you need to invent from scratch each time.
