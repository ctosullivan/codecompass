---
status: PROPOSAL (Phase 64, Cluster C — grounded in the current repository, not the other two dispatches' proposed output)
---

# Cross-links: where domain terms already appear outside `docs/domain/`

This dispatch does not read Cluster A's (user + developer) or Cluster
B's (architecture + protocol/adapter) proposed output — per the phase's
own dispatch strategy, the three clusters run independently and in
parallel. What follows is grounded instead in a direct `grep` of the
**current, real** `docs/`, `architecture/`, and `ai-docs/` files (not
the proposal each other cluster is producing), so the lead's
cross-cluster consistency pass has a concrete, evidenced starting point
for checking whether the new proposals use these terms consistently
with `docs/domain/`'s own definitions.

## Recommendation

Wherever the architecture category (Cluster B) or the user/developer
category (Cluster A) introduces one of these terms for the first time,
it should link to the matching `docs/domain/concepts/*.md` page rather
than silently assuming the reader already knows the CodeCompass-specific
sense — several of these terms (adapter, capability, digest, context)
are also ordinary English words or carry a second, unrelated sense
already documented on their own concept page.

## Terms with real, current usage outside `docs/domain/`

| Term | Where it's already used today | What that usage should link to |
|---|---|---|
| **adapter** | `architecture/overview.md` (108 case-insensitive hits — both the `EcosystemAdapter` sense and its own separate "host-output adapter" label for `skill.py`/`commands.py`/`index.py`) | [`concepts/adapter.md`](../../../docs/domain/concepts/adapter.md) — and specifically its "What it is NOT" section disambiguating the two senses, since `architecture/overview.md` is the one place that ambiguity is already flagged in current docs |
| **capability** | `architecture/overview.md:276-278,1466` — the closed 3-method/4-capability/4-error-code protocol shape | [`concepts/capability.md`](../../../docs/domain/concepts/capability.md) — note the concept page's own caution that `sync.py:244` uses "capability" in a looser, non-protocol sense for `symbols()`; a proposed architecture doc should not conflate the two |
| **digest** | `docs/cli-reference.md`, `ai-docs/README.md`, `architecture/overview.md` (48 combined hits) | [`concepts/digest.md`](../../../docs/domain/concepts/digest.md) — especially its digest-vs-context-packet comparison table, since a user-facing CLI reference describing `codecompass chat` as "digest-only, grounded on persisted digest files" is exactly the sentence the concept page's own "Counterexample / fuzzy boundary" section discusses (three informal senses of "digest" in this same set of files) |
| **ecosystem** | `docs/config-schema.md`, `docs/cli-reference.md`, `architecture/overview.md` (47 combined hits) | [`concepts/ecosystem.md`](../../../docs/domain/concepts/ecosystem.md) — a user-facing config-schema doc describing `vendor.toml`'s `ecosystem` field should note it is the closed, CodeCompass-internal enum, not the external protocol's own free-text `ecosystem` wire field (a real, documented divergence) |
| **vendor** | `docs/config-schema.md`, `docs/cli-reference.md`, `architecture/overview.md` (508 combined hits — the most heavily used term in current docs, expected since it names the CLI's own primary unit) | [`concepts/vendor.md`](../../../docs/domain/concepts/vendor.md) — mainly for the "carries no path information at all" invariant, easy to get wrong when writing user-facing config docs |
| **protocol** | `docs/external-adapters.md`, `architecture/overview.md` (31 combined hits) | [`concepts/protocol.md`](../../../docs/domain/concepts/protocol.md) — the protocol/adapter category (Cluster B's own scope) is the most natural home for the full wire-contract description; it should point back to this concept page rather than re-describing the concept's own boundary from scratch |
| **context-graph** | `architecture/overview.md` and others (30 hits) | [`concepts/context.md`](../../../docs/domain/concepts/context.md) sense 1, and [`concepts/relationship-edge.md`](../../../docs/domain/concepts/relationship-edge.md) for the six edge tables specifically |

## Terms with no current usage outside `docs/domain/` (checked, not assumed)

- **"context packet"** — zero hits in `docs/`, `architecture/overview.md`,
  or `ai-docs/README.md`. This is expected: a context packet
  (`concepts/context-packet.md`) is an internal `planning/knowledge/`
  development-process artifact, not something a CodeCompass *user* or
  the current architecture doc would ever need to mention. The
  development-process category (this same dispatch's other half) is its
  only natural home outside `docs/domain/` itself.
- **"invariant"** — zero hits in the same four files, for the same
  reason: it is a documentation/process-vocabulary word
  (`concepts/invariant.md`'s own three senses), not a CLI or
  architecture-level term a current-truth doc would use.

## A caution for the lead's cross-cluster consistency pass

Do not read the raw hit counts above as "this term is well-covered
already" — several of the current-docs occurrences may themselves use a
term loosely, in ways `docs/domain/`'s own corpus explicitly flags as
imprecise (e.g. `docs/cli-reference.md`'s "digest-only" phrasing,
already named on `concepts/digest.md`'s own counterexample section as
one of three informal, un-cross-referenced senses of "digest" in this
exact set of files). Cluster A and Cluster B's own proposals inherit
these files as source material; whether their proposed rewrites keep or
resolve that existing looseness is worth a specific look in the lead's
synthesis pass, not assumed either way here.
