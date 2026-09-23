# Retirement candidates — Cluster A (user + developer)

Per Phase 64 (`planning/phase-64-blank-slate-documentation-reconstruction.md`
§2): concepts/framing the *current* `docs/`/`README.md` spend real words
on that the *current system* doesn't justify spending them on anymore —
not factual errors (this repo's own mechanical drift checks
(`scripts/check_user_docs.py`) already keep the current docs largely
accurate; I found no live false statement in my own area while deriving
this proposal). These are **presentation/scope** candidates for the
lead to weigh at Phase 65, not blocking findings.

## 1. Pervasive per-command "Status: implemented (Phase N, decisions/NNNN)" framing

`docs/cli-reference.md` opens nearly every command section with a
`**Status:** implemented (Phase N...)` line, and the same phase/decision
citation density runs through `docs/config-schema.md`'s "Fields" and
"Notes" sections. This makes complete sense for a project whose docs
must stay synchronized with an in-progress roadmap (`CLAUDE.md` §2's
same-commit rule) — a maintainer or `docs-reconstructor` audit benefits
from knowing exactly which phase/ADR justifies a given behaviour. But
for a **first-time user** reading the CLI reference to learn what
`codecompass sync` does today, "Phase 4, Phase 7, Phase 15" is
provenance noise, not information they need to use the tool — every
command in this reference is, in fact, simply real and current; none is
partial, planned, or experimental. A blank-slate user-facing reference
(this proposal's own `cli-reference.md`) states behaviour as plain
present-tense fact and cites a decision only where the *why* materially
helps (e.g. "`sync <vendor>` never triggers Phase B — decisions/0025"),
not as a blanket status annotation on every heading.

**Recommendation for Phase 65's consideration**: keep the phase/decision
citation density in `docs/cli-reference.md` (it serves the
docs-drift-audit and ADR cross-reference machinery that
`scripts/check_user_docs.py` mechanically checks —
`check_adr_status_and_supersedes`, `check_fenced_codecompass_examples`
etc. — real infrastructure this proposal doesn't want to break), but
consider whether a genuinely user-facing quickstart/CLI-summary (this
proposal's own `quickstart.md`) should exist as a *separate*,
phase-annotation-free document rather than only the single dense
reference doing double duty for both audiences. This proposal treats
that as the answer already (a new `quickstart.md`), rather than a
retirement of `docs/cli-reference.md`'s own existing style.

## 2. `docs/config-schema.md`'s two-paragraph `depth`/`context_path` history

The "Fields" section's own final paragraph ("No other fields are read...
`context_path` (a Phase 5 field) was removed in Phase 7... `depth` (the
original per-vendor `surface`/`full` toggle)...") spends roughly 150
words narrating two long-retired fields, including which phase and
which two ADRs removed the second one, and that a stray `depth =` line
in a legacy file is silently ignored. This is accurate (confirmed
against `config.py`'s real `_parse_entry`, which genuinely never reads a
`depth` key) and useful **once**, for someone migrating an old
`vendor.toml` — but it currently sits inline in the primary schema
reference a brand-new user reads to learn the *current* two-field
schema, ahead of the "What every tracked vendor gets" section that
actually matters more to that reader.

**Recommendation for Phase 65's consideration**: compress to one
sentence in the main schema table's footnote ("historical fields removed
in Phase 7/16, safely ignored if present — see `decisions/0031`") and,
if the fuller migration narrative is worth preserving at all, move it to
a dedicated "legacy vendor.toml" note rather than the primary schema
walkthrough. Not a factual retirement (the fact is true and worth
keeping *somewhere*) — a placement/length one.

## 3. `docs/external-adapters.md`'s adapter-*build* content overlapping developer scope

`docs/external-adapters.md` (currently under `docs/`, Cluster A's own
tracked directory) mixes two audiences: **user-facing** operational
content (cloning with `--recurse-submodules`, fixing an existing clone,
`stack build`) and what is really **protocol/wire-contract** content
(the `protocol_version` vs. repo-semver distinction, the
version-compatibility matrix) — the latter squarely Cluster B's
protocol-adapter category per this phase's own dispatch split (§2 of
the phase plan). This isn't a factual problem with the existing file,
but it means the real `docs/external-adapters.md` currently serves two
different reader intents in one document, one of which (the wire
contract) this reconstruction places in a different category entirely.

**Recommendation for Phase 65's consideration**: not a removal — a
possible split, once Cluster B's own protocol-adapter proposal exists,
between "how to clone/build the Haskell adapter locally" (developer
workflow, arguably belongs alongside this proposal's own
`developer/workflow.md`/`writing-an-adapter.md`) and "what the wire
protocol guarantees" (Cluster B's territory). Flagged here rather than
acted on, since Cluster B's own proposal isn't this dispatch's to read
or shape.

## What I did *not* find

No command, flag, or config field described in `docs/cli-reference.md`
or `docs/config-schema.md` was found to be stale, removed, or
behaviourally different from what a real `--help` transcript or a direct
`config.py`/`core.py` read confirmed. `README.md`'s "Setup" and "AI
enrichment vs. no-AI usage" sections likewise matched real, currently
running behaviour (the `ANTHROPIC_API_KEY` implicit-env-read claim, the
Phase A/Phase B free/paid split) exactly. This repository's own
mechanical `check_user_docs.py` (`check_cli_commands_documented`,
`check_vendor_config_fields_documented`, `check_fenced_codecompass_
examples`, `check_no_deleted_names_as_live`) is doing real, effective
work here — my own independent derivation corroborates rather than
contradicts it.
