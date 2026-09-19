# 0058. The adapter protocol and the Haskell adapter are separate, differently-licensed public repositories, checked out as submodules

## Status

Accepted (2026-09-19).

## Context

`decisions/0057` established the external-process/JSON-protocol
architecture for the Haskell adapter, but deliberately deferred real
multi-repository distribution as premature for Phase 60's own bounded
proving case: "a distribution/versioning/discovery mechanism for the
external adapter beyond it existing as a file in this same repository...
is not built out as a real separate-repository/package-registry
mechanism yet." That deferral is superseded by direct instruction —
Phase 60 must now build exactly this, as three real, separately
licensed, publicly hosted repositories.

This also closes a real gap `decisions/0057`'s own "explicit non-claim"
left open: with the adapter script living *inside* the main CodeCompass
repository's own working tree (even if never imported by Python code),
its own licensing status relative to CodeCompass's repo-level
GPL-3.0-or-later notice was genuinely ambiguous — exactly the kind of
thing that ADR said needed specialist legal review before relying on.
Moving the adapter into its own repository, under its own explicit
license file, is a materially stronger, cleaner realization of
"separately licensed component" than co-locating it ever could be — the
caveat about needing real legal review before relying on any of this
for an actual proprietary adapter still stands, restated below, not
weakened by this improvement.

## Decision

**Three repositories, three licenses, one local workspace:**

1. **`codecompass`** (this repository) — GPL-3.0-or-later, unchanged
   (`decisions/0053`). CodeCompass core.
2. **`codecompass-adapter-protocol`** (new, standalone, public) —
   **MIT license.** Contains *only* the language-neutral contract:
   - `SCHEMA.md` — the human-readable protocol specification (the
     canonical version of what `decisions/0057` first documented inline;
     that ADR's own protocol description becomes a historical snapshot
     once this repository exists, cross-referenced, not deleted).
   - `schemas/*.json` — real, validatable JSON Schema documents for
     every message shape (`initialize` request/response,
     `analyze_project` request/response, `shutdown` request/response,
     the shared `error` shape).
   - `examples/` — worked example request/response pairs (the same
     shapes `decisions/0057`/the Phase 60 plan already show inline).
   - `conformance/` — a small, standalone test harness (schema
     validation against recorded example messages; any implementation,
     in any language, can point its own real output at these schemas) —
     deliberately minimal, no CodeCompass code, no Haskell code.
   - Its own `LICENSE` (MIT), `README.md`, `CHANGELOG.md`, and a
     semver-versioned release history (e.g. `0.1.0` for Phase 60) —
     **distinct from the wire-level `protocol_version` integer** the
     protocol itself negotiates at runtime (`decisions/0057`); a repo
     release can patch documentation/examples/conformance tests without
     bumping `protocol_version`, and only bumps `protocol_version` when
     the wire contract itself changes.
   - **Contains no CodeCompass internals** (no `DepNode`/`Symbol`/
     `graph.py` knowledge) **and no Haskell code** — schemas and
     documentation only, so any future adapter, in any language, under
     any license, can depend on it without inheriting anything from
     either CodeCompass or the Haskell adapter.
3. **`codecompass-adapter-haskell`** (new, standalone, public) —
   **GPL-3.0-or-later**, matching CodeCompass's own license. A real,
   small Stack project (`package.yaml`/`stack.yaml`/`app/Main.hs` —
   superseding this plan's own prior "bare `stack script`" sketch, which
   remains valid, confirmed-working *technical* grounding for "`stack`
   + `aeson` builds here," now packaged as a proper standalone project
   since a real public repository needs its own `LICENSE`, `README.md`,
   CI configuration, and release process, not just one script file). It
   **implements** `codecompass-adapter-protocol`'s schemas — it does not
   need a Haskell-code-level (`stack.yaml` `extra-deps`) dependency on
   the protocol repository at all, since the protocol repository ships
   no Haskell code to depend on; conformance is validated by running the
   protocol repo's own conformance tests against this adapter's real
   output, in this adapter's own CI. Runs as an independent executable/
   process, per `decisions/0057`, unchanged.

**Local workspace layout — git submodules:**

```
codecompass/                              (this repository, main)
├── protocol/
│   └── codecompass-adapter-protocol/     (git submodule)
└── adapters/
    └── haskell/                          (git submodule)
```

`codecompass`'s own `.gitmodules` records both submodules' remote URLs
and CodeCompass commits *only* a pinned commit SHA per submodule
(a "gitlink" — git's own native mechanism for this), never the
submodules' own file content directly. Updating which protocol/adapter
version CodeCompass is pinned to is `git submodule update --remote` (or
a manual checkout to a specific tag/commit) followed by a normal commit
in `codecompass`'s own history recording the new gitlink — a real,
disclosed pointer bump, not a content merge.

## Alternatives considered

- **Git subtree**, merging each sub-repository's history into
  `codecompass`'s own commit log. Rejected — this is the opposite of
  "separate repository with its own commit history": a subtree merge
  makes every commit from the sub-repo appear as CodeCompass's own,
  undermining the very separation this decision exists to establish.
- **A package-manager-resolved dependency with no local checkout**
  (e.g. the Haskell adapter build fetching the protocol repo at build
  time via a Git URL, with nothing checked out in the CodeCompass
  workspace at all). Rejected as the *primary* mechanism for this
  phase specifically because the user's own required layout is a real,
  locally-checked-out subfolder — but this remains the natural,
  idiomatic way a *Haskell* project would reference a Git-hosted
  dependency internally, and is not precluded by anything here; it's
  simply not what the CodeCompass-workspace-level submodule layout
  itself is for.
- **Keep everything in one repository** (`decisions/0057`'s own
  original, deferred position). Rejected by direct instruction — does
  not deliver a real, separately-licensed, independently-releasable
  component, which is the entire point of this decision.
- **A monorepo tool** (e.g. a virtual-monorepo layer over multiple
  repos, sparse-checkout tricks, or a custom fetch script instead of
  submodules). Rejected — submodules are native, zero-new-dependency,
  well-understood Git tooling; a custom mechanism would need its own
  justification this phase's real, bounded need doesn't provide.

## Consequences

- `codecompass-adapter-protocol` and `codecompass-adapter-haskell` are
  created as real, separate, publicly hosted repositories (their own
  remotes, their own commit histories, their own CI, their own release
  tags) — not folders that merely *look* separate inside one repository.
- `codecompass`'s own `.gitmodules` and gitlink commits are the only
  place these two repositories' *existence* is recorded inside
  CodeCompass's own history — their own file content is never committed
  directly to `codecompass`.
- **Commits to each repository stay independent**: a change to the
  protocol's own schemas commits to `codecompass-adapter-protocol`'s own
  history; a change to the adapter's own Haskell code commits to
  `codecompass-adapter-haskell`'s own history; a change to CodeCompass
  core (including a submodule pointer bump) commits to `codecompass`'s
  own history. No single commit spans more than one repository's own
  tracked content.
- A version-compatibility matrix (CodeCompass version ↔ minimum
  protocol version ↔ tested adapter version(s)) must be documented and
  kept current — real, necessary bookkeeping now that three independent
  version streams exist where one repository's own history used to
  suffice.
- `decisions/0057`'s own protocol-shape decision (JSON Lines,
  `initialize`/`analyze_project`/`shutdown`, the four response sections)
  is **unchanged** by this ADR — this decision is about *where the code
  lives and how it is licensed and versioned*, not what the protocol
  itself says.
- **Still not a plugin marketplace, a registry, or a generalized SDK.**
  Exactly one protocol repository and exactly one adapter repository
  exist after this phase, at a fixed, known, hand-configured submodule
  path — auto-discovery of arbitrary third-party adapters remains
  explicitly out of scope, per the user's own repeated instruction
  across every amendment to this phase.

## Restated: this still does not settle the GPL licensing question

`decisions/0057`'s own closing section applies with unchanged force,
and more concretely now that real separate repositories and real
separate license files are actually being created: **giving the
Haskell adapter its own repository and its own `LICENSE` file is a
materially stronger architectural realization of "separately licensed
component" than co-location ever was, but it is still not, by itself, a
legal determination that a *future, proprietary* adapter distributed the
same way would be lawfully independent of CodeCompass's own GPL
obligations.** The protocol repository's own MIT license is chosen
specifically so that a future proprietary adapter could depend on the
*contract* without that dependency alone triggering GPL's copyleft —
but whether the *overall* arrangement (protocol negotiation, process
lifecycle, any data interchange) constitutes lawful independence for a
real proprietary adapter remains a question for a qualified open-source/
IP legal specialist, not something this ADR — or the act of creating
separate repositories — resolves on its own.
