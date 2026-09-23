---
status: PROPOSAL (Phase 64) — consolidated by the lead from the three
  parallel dispatches' own `_retirement-candidates-cluster-{a,b,c}.md`
  reports. A retirement candidate, not a decision: Phase 65's own
  reconciliation (`documentation-lifecycle.md` §4) makes the actual
  retain / rewrite / consolidate / split / replace / remove call per
  document, weighing these candidates against the full proposal.
---

# Concepts to retire — consolidated candidates

Content the *current* `docs/`/`architecture/overview.md` spend real
words on that the *current system* no longer justifies spending them
on — found by three independent blank-slate dispatches (Cluster A:
user+developer; Cluster B: architecture+protocol/adapter; Cluster C:
domain+development-process), each deriving its own area fresh from
`src/`/tests/real command output rather than from the existing docs'
own structure, then checking the existing docs afterward only for
retirement candidates. **No live factual error was found in any
cluster's own area** — this repository's own mechanical drift checks
(`scripts/check_user_docs.py`) are doing real, effective work, and this
independent re-derivation corroborates rather than contradicts them.
Every candidate below is a **presentation/scope** question, not a
correctness one.

## Removal candidates

### 1. `architecture/overview.md`'s "Grounded description — retired" section (lines 471-523)

Describes `codecompass.grounded_description`, a module deleted at Phase
16 (`decisions/0035`). A current-state-only architecture document has no
structural reason to spend 53 lines on a mechanism no longer in `src/`,
however carefully the section is framed as history. Its one
substantively load-bearing fact (`description_error` is set only by a
clone failure, not a description failure) already appears, current-tense,
in this proposal's own `architecture/core-data-model.md`. *(Cluster B.)*

**Recommendation**: remove at Phase 65, not trim — nothing in the
section remains true of the running system, and the one fact worth
keeping is already captured elsewhere in this proposal.

## Trim candidates (keep the fact, shrink or relocate the prose)

### 2. Per-ecosystem implementation prose in `architecture/overview.md`'s "Adapter interface" section (lines 85-233)

Duplicates content already present, verbatim or near-verbatim, in each
adapter module's own docstring (`adapters/npm.py`, `adapters/python.py`,
`adapters/cargo.py` — confirmed by direct read). Not stale — a
duplication risk, since the docstring is unconditionally colocated with
the code it describes and can't drift silently the way separate prose
can. This proposal's own `architecture/adapter-interface.md` keeps this
thinner (contract + strategy + one comparison table), pointing at the
docstrings for per-ecosystem detail. *(Cluster B.)*

**Recommendation**: trim at Phase 65 to a contract-level summary plus a
pointer to each adapter's own docstring; keep signalling that
per-ecosystem quirks exist (dev_only handling differences, no `rustdoc
--output-format json` yet), just not at flag-level detail in two places.

### 3. `docs/config-schema.md`'s `depth`/`context_path` legacy-field history (~150 words, inline in "Fields")

Accurate (confirmed against `config.py`'s real `_parse_entry`) and
useful once, for someone migrating an old `vendor.toml` — but it
currently sits ahead of the "what every tracked vendor gets" section
that matters more to a first-time reader. *(Cluster A.)*

**Recommendation**: compress to one footnote sentence in the main
schema table ("historical fields removed in Phase 7/16, safely ignored
if present — see `decisions/0031`"); if the fuller narrative is worth
keeping, move it to a dedicated "legacy vendor.toml" note rather than
the primary schema walkthrough.

### 4. Pervasive per-command "Status: implemented (Phase N, decisions/NNNN)" framing in `docs/cli-reference.md`/`docs/config-schema.md`

Real infrastructure value for a maintainer or `docs-reconstructor`
per-phase drift audit (`check_adr_status_and_supersedes` and friends
mechanically depend on this density) — but provenance noise for a
first-time user, since every documented command is in fact fully
current, none partial/planned/experimental. *(Cluster A.)*

**Recommendation**: not a retirement of the existing style — keep
`docs/cli-reference.md`'s citation density for the audience it serves,
but adopt this proposal's own separate `docs/quickstart.md`
(phase-annotation-free) as the answer for the first-time-user need,
rather than asking one document to serve both audiences.

## Split candidate

### 5. `docs/external-adapters.md` mixes developer-workflow and protocol/wire content

Cloning/building instructions (`--recurse-submodules`, `stack build`) sit
alongside wire-contract content (`protocol_version` vs. repo-semver, the
version-compatibility matrix) in one file — two different reader
intents this reconstruction places in different categories (developer
vs. protocol/adapter). **Both clusters independently flagged this same
file from opposite sides** (Cluster A: the developer-workflow half
overlaps `docs/developer/writing-an-adapter.md`; Cluster B: the
wire-contract half overlaps `protocol-adapter/wire-protocol.md`) —
**and both independently confirmed the file itself is currently
accurate, not stale.** This is a structural split candidate, not a
correctness finding.

**Recommendation**: at Phase 65, once both this proposal's
`developer/writing-an-adapter.md` and `protocol-adapter/wire-protocol.md`
exist as real candidates to migrate content into, consider splitting
`docs/external-adapters.md` along that same line rather than retiring
it outright — it may become two shorter, single-audience documents, or
stay one document with clearer internal section headers. Either way,
its "Naming note" about the adaptor/adapter spelling discrepancy should
be preserved verbatim wherever the split content lands (it independently
matches `docs/domain/concepts/protocol.md`'s own finding).

## Explicitly checked, not retirement candidates

- **Domain corpus (`docs/domain/`)**: none found. Approved the same day
  as this dispatch; too recent to have accreted anything the current
  system doesn't justify. *(Cluster C, full read of all 19 concept pages
  plus the six integration files.)*
- **Development-process planning docs**
  (`planning/v1-redefinition/agent-led-development.md`, `README.md`,
  `roadmap.md`, `planning/phase-54c-evidence-knowledge-workflow.md`):
  checked directly for a competing or superseded process description
  predating `development-methodology.md`'s own naming — none found;
  every hit is a citation *to* the methodology, and Phase 54c's own plan
  remains a live dependency (`development-methodology.md` explicitly
  points to it rather than restating its record-shape mechanics).
  *(Cluster C.)*
- **`docs/external-adapters.md`'s own factual content**: already
  current and accurate (cloning steps, naming note, version-compatibility
  table) — a structural split candidate (#5 above), not a correctness
  one. *(Cluster B.)*
- **Every CLI command/flag/config field** in the existing
  `docs/cli-reference.md`/`docs/config-schema.md`: none found stale,
  removed, or behaviourally different from a real `--help` transcript or
  direct `config.py`/`core.py` read. *(Cluster A.)*

## Boundary worth naming for Phase 65 (not a retirement candidate)

`architecture/overview.md` already documents, in its own words, the
two-unrelated-senses-of-"adapter" ambiguity that this phase's own
research (and `docs/domain/concepts/adapter.md`, from Phase 63D)
independently confirms. This is existing self-awareness in the current
doc, not a drift finding — recorded so Phase 65 doesn't need to
re-discover it. *(Cluster B.)*
