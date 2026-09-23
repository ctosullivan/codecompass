# CodeCompass docs — proposed set (Cluster A: user + developer)

**This is a shadow proposal, not live documentation.** It lives under
`planning/v1-docs-reconstruction/` per Phase 64
(`planning/phase-64-blank-slate-documentation-reconstruction.md`) and
does not replace anything under the real `docs/`. Deciding whether/how
to fold this into the real `docs/` is Phase 65's job.

Everything here was derived fresh from the running system in this
checkout, not from the existing `docs/`/`README.md` — see each file's
own citations (a file path, a real `--help` transcript, a test) for
where each claim comes from. Domain terminology (*adapter*, *vendor*,
*digest*, *context packet*, etc.) is **not** re-derived here — it is
cited from the already-approved `docs/domain/concepts/*.md` corpus
(Phase 63D) and used exactly as that corpus defines it.

## Contents

**User-facing:**

- [`quickstart.md`](quickstart.md) — install, run, read the output, in
  under five minutes.
- [`cli-reference.md`](cli-reference.md) — every real command,
  subcommand, and flag, captured from actually running `codecompass
  --help`/`codecompass <subcommand> --help` in this checkout.
- [`config-schema.md`](config-schema.md) — the real `vendor.toml`
  schema, derived from `src/codecompass/config.py` and
  `src/codecompass/core.py`'s `VendorConfig`.

**Developer-facing** (kept in this same `docs/` tree, under
`developer/`, rather than a separate top-level category — CodeCompass
has no separately-versioned "contributor docs" product; a developer
reading this material is reading the same repository a user installs
from, just a different section of it):

- [`developer/writing-an-adapter.md`](developer/writing-an-adapter.md)
  — the real `EcosystemAdapter` interface contract and how to implement
  a new one, grounded in `src/codecompass/adapters/base.py` and the two
  real implementation strategies (`NpmAdapter`, `HaskellAdapter`).
- [`developer/workflow.md`](developer/workflow.md) — the real test/
  lint/release workflow, from `pyproject.toml`, `CONTRIBUTING.md`'s
  factual process content, and this repository's own commit/tag
  conventions.

## What this covers and what it doesn't

This cluster (Cluster A) covers **user** and **developer** content
only. It does not cover:

- **Architecture** (internal module design, the context-graph schema)
  or the **protocol/adapter wire format** (the external-process JSON
  protocol itself, `decisions/0057`–`0059`) — Cluster B's scope. Where
  this cluster's developer content needs to gesture at the wire
  protocol (writing an *external-process* adapter), it links out to
  Cluster B's protocol-adapter section rather than re-describing it.
- **Domain** (what CodeCompass's own concepts mean) or **development-
  process** (the Scope → Plan → Domain → Design → Implement
  methodology) — Cluster C's scope.

## Real gaps observed while deriving this content

Recorded here as plain observations, not fixed by this phase (no
`src/` change is in scope):

- `pipdeptree` is declared in `vendor.toml` (a project dependency) but
  has **no** `codecompass-pipdeptree` Skill or `.cursor/rules/
  codecompass-pipdeptree.mdc` file, unlike `anthropic`/`rich`/`typer` —
  confirmed by `codecompass query vendors` showing `pipdeptree` as
  `Used: no` in this exact checkout. This is correct, documented
  behaviour (Skills are only generated for usage-proven vendors,
  `decisions/0031`), not a bug — but it means a new user skimming
  `.claude/skills/` for "one Skill per tracked dependency" would be
  confused without this being stated plainly, which the real
  `docs/cli-reference.md` does not currently say as directly as this
  proposal's quickstart does.
- No `.github/workflows/` CI configuration exists in this repository
  itself (only the two submodules — `adapters/haskell/` and
  `protocol/codecompass-adaptor-protocol/` — have their own `ci.yml`).
  The "test/lint/release workflow" developer doc below is therefore
  necessarily derived from `pyproject.toml` + `CONTRIBUTING.md` +
  `CLAUDE.md`'s stated conventions, not from an executable CI
  definition — worth flagging as a real gap if this project ever wants
  a machine-enforced gate rather than a documented convention.
- `codecompass check`'s coverage-gap sections and `query
  vendors`/`query skills` all require `context-graph.db` to exist first
  (`codecompass sync` or bare `codecompass`); there is no single `--help`
  string anywhere that says this up front for a brand-new user — each
  subcommand instead degrades gracefully with a one-line runtime note.
  Fine at runtime, but means a static reading of `--help` alone
  slightly undersells the "run this first" dependency; the quickstart
  below states it explicitly.
