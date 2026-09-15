# 0055. Contributor licensing terms preserve future re/dual-licensing options

## Status

Accepted (2026-09-15).

## Context

`decisions/0053` relicensed CodeCompass from MIT to GPL-3.0-or-later.
Until now, `CONTRIBUTING.md` stated plainly that "there is no separate
contributor licence agreement — this is a single-maintainer project,"
meaning any external contribution would arrive under the project's
then-current licence (GPL-3.0-or-later) with no separate grant back to
the project. That is fine for a project that will only ever ship under
one copyleft licence, but it forecloses two things the project owner may
want later: offering CodeCompass under alternative or commercial licence
terms to specific parties (a common dual-licensing model for
GPL-licensed projects), and doing so without needing to track down and
re-clear every external contributor's individual consent after the fact
— which becomes impractical once contributions with independent
copyright exist.

The project currently has exactly one committer (`git log`, unchanged
since `decisions/0053`'s own research), so there is no live contribution
to reconcile — this is a forward-looking preservation of optionality,
not a retroactive relicensing of anything that exists today.

## Decision

`CONTRIBUTING.md` gains an explicit contributor licensing term, replacing
the "no separate CLA" sentence: by submitting a contribution, the
contributor retains copyright in it but grants the project owner an
irrevocable, worldwide, royalty-free licence broad enough to relicense
that contribution — including under proprietary or other alternative
terms — while the contribution may continue to be distributed as part of
the GPL-licensed project. The exact grant text is specified verbatim (not
paraphrased) and must not be altered without a new ADR, the same
append-only discipline this file's own convention already applies to
itself.

`README.md` gains a short, prominent note pointing at this term from the
`## License` section, so a prospective contributor sees it before
`CONTRIBUTING.md`'s own fuller text, without needing a separate CLA-bot
or signing flow — a doc-level term is sufficient at this project's
current scale (still effectively pre-contribution, single committer).

This does not change CodeCompass's own current licence
(GPL-3.0-or-later, `decisions/0053`) or any existing user's rights under
it — it only shapes the terms under which a *future* external
contribution is accepted.

## Alternatives considered

- **Leave the status quo (no CLA).** Rejected: this is precisely the
  option that forecloses future dual/proprietary licensing once any
  external contribution with independent copyright exists — cheap to
  fix now, expensive or impossible to fix retroactively once
  contributors are numerous or unreachable.
- **A full formal CLA process** (a signing bot, a separate signed
  document per contributor, an org-level CLA management tool). Rejected
  as premature machinery for a project with zero external contributions
  to date — a clear, prominent doc-level term serves the same purpose at
  this scale; revisit if/when real external contribution volume
  justifies the added process weight.
- **Require copyright assignment** (contributor transfers copyright
  outright, rather than retaining it and granting a licence). Rejected:
  broader than needed for the stated goal (preserving relicensing
  optionality) and a meaningfully heavier ask of a contributor; a licence
  grant achieves the same practical outcome for the project owner while
  leaving the contributor's own copyright intact.

## Consequences

- `CONTRIBUTING.md`'s `## License` section is updated: the CLA grant
  text (verbatim, not paraphrased) replaces the "no separate CLA"
  sentence.
- `README.md`'s `## License` section gains a short note covering: the
  project is GPL-3.0-or-later; external contributions are subject to
  `CONTRIBUTING.md`'s licensing terms; this preserves future
  alternative/commercial licensing options; existing GPL rights for
  users of the project are unaffected.
- `CHANGELOG.md` gains an entry.
- No existing commit, release, or user right is affected — nothing has
  ever been contributed externally, and nothing already distributed
  under GPL-3.0-or-later stops being available under it.
- A future contributor's PR/patch submission is the point at which this
  term takes effect; it is not applied retroactively to the single
  existing committer's own past work (already owned outright).
