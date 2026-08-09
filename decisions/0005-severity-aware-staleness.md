# 0005. Severity-aware staleness, not binary

## Status

Accepted

## Context

`depcompass check` compares a vendor digest's recorded "last verified
against installed version" line against the ecosystem adapter's live read
of the installed version. Some kind of drift is nearly always present in
an actively maintained project — the question is which drift actually
warrants attention.

## Decision

Staleness severity is derived from semantic version delta:

- **Patch** version delta — silent, ignored. Patch releases are near-never
  breaking for documentation purposes.
- **Minor** version delta — warns, but `check` still exits 0.
- **Major** version delta — hard-fails; `check --strict` exits non-zero,
  because a major bump may mean the digest describes removed or changed
  APIs.

Where practical, `check` also distinguishes whether the *vendor itself*
bumped version vs. only a *transitive dependency* bumped (DEPTREE drift
only) — the latter is lower risk and doesn't trigger the same urgency.

## Alternatives considered

- **Binary stale/fresh.** Rejected — gives no signal about urgency; a
  patch bump and a major bump would look identical in `check` output, when
  they warrant very different responses.
- **Always fail on any detected drift.** Rejected — in an actively
  maintained project, this would make `check` fail near-constantly on
  routine patch bumps, training users to ignore or bypass it (alert
  fatigue), which defeats its purpose as a CI gate.

## Consequences

- `check --strict` (CI gate) and `check --fix` (scheduled maintenance,
  regenerates stale digests, exits 0, batches into one PR) can both rely on
  the same severity classification rather than needing separate logic.
- Semantic version parsing must be correct per-ecosystem (npm/PyPI/Cargo
  version schemes aren't identical) for the patch/minor/major distinction
  to be trustworthy — this is an implementation detail to get right in the
  adapters, not a caveat on this decision itself.
