# CodeCompass clean-room documentation handoff

You are a fresh documentation-writing agent (or human) with **no prior
knowledge of this project**. This directory is the entire basis for your
work — everything you need to write complete, accurate, current
documentation for CodeCompass is either here or in the allowlisted
source/test/config material alongside it in your own workspace.

## What CodeCompass is (one sentence, for orientation only — verify everything below)

CodeCompass is a tool that builds and maintains a structural knowledge
graph of a software project's dependencies and source, surfacing that
context to AI coding agents and generating project documentation —
**do not take this sentence as established fact; verify it against the
real evidence in `knowledge/overview.md` and the allowlisted source**.

## What you are being asked to do

Write a complete, fresh `README.md` and a complete, fresh `docs/` tree
for CodeCompass, from zero — see `DOCUMENTATION-TARGET.md` for the
required coverage and expected (not mandatory) structure. You are not
asked to paraphrase the files in this handoff mechanically; you are
asked to understand what they establish and then write documentation a
genuinely new user, contributor, maintainer, or AI coding agent would
need.

## Authoritative evidence hierarchy — see `SOURCE-OF-TRUTH.md`

In short: the `knowledge/` directory's own canonical Claims (each one
evidence-backed, each one traceable via `knowledge/source-and-evidence-map.md`)
are your primary conceptual evidence. The allowlisted current source,
tests, and configuration in your own workspace are your primary
technical/behavioural evidence — use them to verify and add detail the
knowledge layer doesn't carry (exact flag names, exact file paths,
current CLI `--help` text), never to override what the knowledge layer
says without your own real verification.

## How conflicts and uncertainty are handled

If two pieces of supplied evidence disagree, or if you cannot verify a
claim against real source/tests, **say so explicitly in the
documentation** — do not silently pick a side, and do not omit the
claim entirely. `OPEN-QUESTIONS.md` already names every currently-known
open question and conflict in this project's own knowledge base; add to
it, in your own output, any further uncertainty you genuinely cannot
resolve.

## What has intentionally been excluded from this handoff

No pre-existing project documentation (no old `README.md`, no old
`docs/`, no old `architecture/`, no old `ai-docs/`) is present anywhere
in your workspace, in any form — not the original files, not a summary of
them, not a paraphrase. This is deliberate. Do not attempt to recover,
infer the existence of, or search for previous project documentation —
there is nothing to find, and looking for it is not a productive use of
your own time. Every genuinely useful fact from that prior documentation
that survived independent verification is already present in
`knowledge/`, in its own evidence-backed form.

## Hard requirements

- Write a complete new `README.md` and `docs/` tree from zero.
- Every important technical statement must either (1) be supported by
  the supplied `knowledge/` material, or (2) be independently verified by
  you against the current, allowlisted source/tests/configuration in your
  own workspace.
- Do not use Git history, external repository search, internet search, or
  any other repository as a documentation source — none of these are
  reachable from your own workspace, and no instruction here asks you to
  find a way around that.
- Do not assume undocumented behaviour — if it isn't evidenced and you
  cannot verify it, say so rather than guessing.
- Do not simply paraphrase `knowledge/overview.md` mechanically into
  prose — synthesize genuine documentation a real reader needs.

See `CLEANROOM-INSTRUCTIONS.md` (at the root of your workspace, outside
this directory) for the complete, tool-independent writer contract.
