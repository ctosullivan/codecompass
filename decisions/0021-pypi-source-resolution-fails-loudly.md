# 0021. PyPI packages without a resolvable repository URL fail `promote` rather than falling back to a source tarball

## Status

Accepted

## Context

`decisions/0019`'s grounded description generation requires retrieving a
vendor's actual source as its sole grounding material — the "grounded"
guarantee depends on that material being real, current, and traceable.
Registries expose repository information with very different reliability
per ecosystem. npm and Cargo both carry a structured `repository` field
reliably enough to trust directly (npm additionally sometimes carries a
`directory` field scoping a specific package within a monorepo, which
must be respected when present, or retrieval grabs the wrong, unrelated
scope of a larger repo). PyPI is the weak link: `project_urls` keys
aren't standardized across packages — "Source", "Repository", "Code",
"GitHub", and "Homepage" all appear in the wild — and a meaningful
fraction of published packages declare no VCS URL at all. `promote`
needs a decided, explicit answer for what happens when no repository
resolves for a PyPI package, rather than leaving it to be discovered
mid-implementation.

## Decision

Source resolution checks, per ecosystem: npm/Cargo's `repository` field
(npm additionally reading `directory` to scope a monorepo package
correctly); PyPI's `project_urls`, checking a fixed list of common key
variants (`Source`, `Repository`, `Code`, `GitHub`, `Homepage`). When no
repository URL resolves for a PyPI package, `promote` fails for that
vendor with a clear error — the vendor stays at its current depth
(`SURFACE`) — rather than falling back to the registry's own hosted
source tarball (sdist), which is available independent of any declared
repository URL.

## Alternatives considered

- **Fall back to the PyPI-hosted sdist tarball when no repository URL
  resolves.** Rejected — a tarball snapshot loses commit history and
  (often) the README/docs context a repository checkout provides,
  undermining the "grounded, traceable" property `decisions/0019` exists
  to guarantee. It would also add a second retrieval code path
  (tarball-fetch-and-extract vs. repository-clone-or-fetch) to design,
  implement, and test, for uncertain benefit. Revisit only if real usage
  shows this failure case is common enough to be a significant adoption
  blocker on its own.
- **Prompt the user interactively for a repository URL when resolution
  fails.** Rejected — contradicts `promote`'s design as a single
  confirm-then-run action (`decisions/0018`); a mid-command interactive
  prompt for one input is a worse experience than a clear failure
  message the user can act on however they choose.

## Consequences

- The source-resolution module needs per-ecosystem functions returning
  either a resolved `(repository_url, subdirectory | None)` pair or a
  clear failure reason, not a single generic "try everything" function.
  npm/Cargo vendors lacking a `repository` field also fail loud under
  this decision — expected to be rare enough not to need their own
  fallback discussion, but not special-cased to behave differently from
  PyPI's failure mode.
- `promote`'s test plan (`planning/phase-7-bootstrap-and-promote.md`)
  must include a PyPI vendor with no resolvable `project_urls` entry as
  an explicit case.
- No manual override mechanism (e.g. a user-supplied repository URL in
  `vendor.toml`) is introduced by this decision — if the fail-loud case
  turns out to be common in practice, that's a natural, separate
  follow-up decision, not implied by this one.
