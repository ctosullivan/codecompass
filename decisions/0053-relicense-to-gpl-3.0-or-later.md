# 0053. Relicense CodeCompass to GPL-3.0-or-later

## Status

Accepted (2026-09-12, gate G12). Full plan:
`planning/v1-redefinition/licence-migration.md`.

## Context

`hledger` — the compatibility reference Ledgerkit (and now, transitively,
CodeCompass's own evidence-relating work) targets — is
`GPL-3.0-or-later`, confirmed at the SPDX-field level in its own
`hledger/package.yaml` and `hledger-lib/package.yaml`
(`license: GPL-3.0-or-later`), not merely GitHub's coarse licence
detection. CodeCompass is currently MIT, with a single copyright holder
(`git log` shows exactly one committer across all commits), no bundled
third-party source (`vendor/` — the per-dependency cloned-upstream-source
directories CodeCompass itself generates — is entirely `.gitignore`d,
never tracked), and runtime dependencies (`typer`, `rich`, `anthropic`,
`pipdeptree`) that are all themselves MIT (no GPL-incompatibility risk).
Nothing has ever been published under any licence (`git tag -l` is
empty; no PyPI release exists).

Aligning CodeCompass's own licence with hledger's family removes the
need for an artificial clean-room boundary when a CodeCompass
development agent inspects `hledger` source, documentation, or tests to
understand behaviour it is helping relate for Ledgerkit's benefit — the
same source-assisted development model Ledgerkit itself is adopting for
its own hledger-compatibility work. This is not because CodeCompass
bundles or redistributes hledger code — it doesn't and won't.

## Decision

Relicense CodeCompass from MIT to GPL-3.0-or-later: `LICENSE` (the
canonical, unmodified GPL-3.0 text plus a standard notice block naming
CodeCompass, the copyright holder, and the "or (at your option) any
later version" clause), `pyproject.toml` (`license` field + Trove
classifier), `README.md` (`## License` section), `CONTRIBUTING.md` (a
short note on the licence and the absence of a separate CLA).

A source-assisted development policy is recorded alongside this
decision (`licence-migration.md` §4), distinguishing four activities —
source inspection, algorithm/architecture understanding, adapted
implementation, and directly translated material — each with its own
attribution requirement. Executable behavioural verification remains
independent of source inspection regardless of licence: reading
hledger's source explains intent; running the `hledger` executable and
comparing output is what verifies external compatibility.

## Alternatives considered

- **Stay MIT, maintain an explicit clean-room boundary for any
  hledger-facing work.** Rejected: adds process friction (a boundary to
  police) for a project whose stated direction is deeper source-assisted
  evidence-relating work, without a compensating benefit — CodeCompass
  has no reason to prefer permissive redistribution terms; it isn't a
  library others embed commercially in a way MIT specifically protects.
- **Dual-license (MIT + GPL).** Rejected: adds real ongoing maintenance
  complexity (every future contribution would need to be
  dual-licensable) for a single-maintainer project with no evidence of
  demand for the MIT option.
- **Relicense to a different copyleft licence** (e.g. AGPL, LGPL).
  Rejected: the specific goal is alignment with hledger's own licence
  family, not copyleft in general, and hledger's own choice
  (GPL-3.0-or-later, not AGPL/LGPL) is the natural match.

## Consequences

- `LICENSE`, `pyproject.toml`, `README.md`, `CONTRIBUTING.md` updated in
  one dated commit (this one).
- `CHANGELOG.md` gains an entry.
- No historical commit or release is rewritten — none exists under any
  licence to date; individual past commits remain, as a historical fact,
  made under MIT at the time.
- Future ADRs / `adoption-blueprint.md` inherit the source-assisted
  provenance policy (§4 of `licence-migration.md`) as the standing rule
  for any project adopting CodeCompass's agent-led development
  methodology against a copyleft upstream.
