# 05 — Phase 77 first-party source validation (principal `CG-009` evidence)

- **Reference project:** https://github.com/ctosullivan/ledgerkit
- **Pinned revision for this validation:** `6c90b4ca3e6c10951cb400e43db4b90bfccc5909`
  (2026-09-27, "docs: mark Stage C [DONE], archive its changelog
  history") — the real current `main` HEAD at validation time, confirmed
  live via a fresh clone (`git log -3`), not hardcoded from Phase 75's
  own earlier pin. Ledgerkit's own development had not advanced past
  this commit since Phase 75 — a genuine fact about the reference
  project's own pace, not an assumption.
- **CodeCompass revision:** `03f8519` (Phase 77 implementation).
- **Working copy discipline**: cloned fresh into a scratch location
  outside CodeCompass's own tree, never added to CodeCompass's own
  `vendor.toml`/`context-graph.db`; a throwaway, uncommitted, empty
  `vendor.toml` was added locally only to let `codecompass sync` run (no
  tracked vendors — deliberately zero, matching Phase 75's own
  zero-vendor state for this project); nothing was ever pushed back to
  Ledgerkit's own remote; the scratch clone was fully deleted after this
  validation completed.

## What this tests

`CG-009` (`planning/context-gaps/inbox.md`): "`context-graph.db`'s
`symbols` table has no path for a project's own first-party source at
all, in any ecosystem." Phase 75's own evaluation found this directly:
`codecompass query symbol Posting`/`Amount` returned empty against
Ledgerkit, even though both are real, central first-party classes.

## Real, current locations resolved live (not assumed)

```
$ grep -rn "^class Posting\|^class Amount\|^class Tag" --include="*.py" .
ledgerkit/models.py:19:class Amount:
ledgerkit/models.py:66:class Posting:
ledgerkit/query/ast.py:118:class Tag:
```

Identical to Phase 75's own recorded locations — Ledgerkit's own
structure has not moved since. Confirmed by resolving fresh, not by
trusting the earlier record.

## Result — `codecompass query source-symbol` against the real project

All three now return real, correct data:

| Symbol | File | Line | Kind | Exposure | Purpose (docstring) |
|---|---|---|---|---|---|
| `Posting` | `ledgerkit/models.py` | 66 | `class` | `public` | "One line within a transaction: an account name and an optional amount..." |
| `Amount` | `ledgerkit/models.py` | 19 | `class` | `public` | "A numeric quantity paired with a commodity symbol..." |
| `Tag` | `ledgerkit/query/ast.py` | 118 | `class` | `public` | "Matches an effective tag name (and, if given, value) — Stage C Phase 6..." (the real, full multi-paragraph docstring, correctly extracted in full) |

`--json` output for all three confirmed `"indexed": true` (the project's
first-party source has been indexed, `meta.source_index_version` was
written by this real sync) and every field populated correctly — no
placeholder, no truncation, no fabrication. The full real docstrings
(including `Tag`'s own long, cross-referenced one) were extracted
verbatim via Python's `ast.get_docstring`, not summarized or altered.

Zero tracked vendors throughout — `vendor.toml` was empty — confirming
first-party indexing is genuinely independent of dependency tracking,
the same zero-vendor architectural property Phase 75's own trial first
established as a requirement.

## Disposition

This is real, direct, live evidence that the structural gap `CG-009`
named is now mechanically closed for the exact motivating case that
originally surfaced it. **This finding alone does not close `CG-009`** —
per `planning/phase-77-first-party-source-and-template.md` §10.2/§21 and
this project's own established context-gap lifecycle discipline
(`planning/context-gaps/README.md`), closure is a `knowledge-curator`/
`context-evaluator`-mediated decision made during this phase's own
closeout, using this record as its evidence — not a status flip made by
the lead unilaterally because code shipped and a query returned data.
