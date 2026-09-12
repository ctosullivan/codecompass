# Docs-drift audit — Phase 43d (GPL-3.0-or-later relicensing) + Phase 43e (agent-led adoption blueprint)

**Mode:** 1 — per-phase drift audit (read-only).
**Base:** working tree vs `HEAD` (`411cda6`), nothing committed yet.
**Auditor:** docs-reconstructor (independent of docs-maintainer; findings
formed directly from diff + code/file inspection, not from any
implementer's summary).

## Verdict: NO DRIFT

## What changed about the system (observable)

- Project licence: MIT → GPL-3.0-or-later. This is the only
  system-observable change in this diff (43e's "blueprint" content is a
  planning artefact, not a system-behaviour change — no CLI, config
  schema, or generated-file-format change occurred). Confirmed no
  `src/codecompass/` or test diff exists.
- `pyproject.toml` `license` field and Trove classifier changed to match.
- `LICENSE` replaced with canonical GPL-3.0 text + notice block.

## Checks performed

**1. README `## License` section vs. `decisions/0053` path/content.**
`decisions/0053-relicense-to-gpl-3.0-or-later.md` exists at exactly the
path/filename README links to
(`decisions/0053-relicense-to-gpl-3.0-or-later.md`). README's text
("GPL-3.0-or-later — see `LICENSE`. Previously MIT; see `decisions/0053`
for the relicensing rationale...") accurately reflects both the `LICENSE`
file's content (verified: header says "GNU General Public License...
version 3... or (at your option) any later version" — i.e. genuinely
"or-later", matching the SPDX identifier used everywhere) and the ADR's
Decision section. No mismatch.

**2. Grep for "MIT" (and separately `licen[cs]e|GPL|MIT|copyleft`,
case-insensitive) across `docs/`, `architecture/`, `ai-docs/`.**
Zero genuine hits. Broader regex initially surfaced lines in
`architecture/overview.md` and `docs/cli-reference.md`, but on
inspection every one was a false positive from `-C 2` context lines
containing unrelated words (e.g. "limitation," "--budget") — re-run with
a word-boundary `\bMIT\b` against `docs/cli-reference.md` and
`docs/config-schema.md` confirmed **no matches at all**. Also checked
`examples/README.md` (linked from the main README) — no licence mentions
there either. None of the four current-truth doc trees say anything
about the licence being MIT, so none needed updating, and none now
contradict the new GPL-3.0-or-later state.

**3. `CONTRIBUTING.md` new `## License` section vs. rest of the file.**
Read the full file. No conflict: the new section ("licensed under
GPL-3.0-or-later... previously MIT — `decisions/0053`... no separate
contributor licence agreement — this is a single-maintainer project")
is consistent with the ADR's own stated facts (single copyright holder,
confirmed via `git log`) and doesn't contradict anything earlier in the
file (agent-led model, DoD, commit conventions sections are all
licence-agnostic).

**4. Other current-truth doc claims a licence change could falsify —
specifically `ai-docs/README.md`'s capability/boundary description.**
Read `ai-docs/README.md` in full. Its "What it does" / "What it does
NOT do" sections describe runtime behaviour (enrichment gating, graph
scope, git-touching posture, relationship-detection determinism) — none
of it makes a claim about redistribution rights, embedding permissions,
or licence terms that a GPL relicensing would falsify. No finding.

## Also checked (reverse direction)

- `pyproject.toml` diff: `license = { text = "GPL-3.0-or-later" }` +
  classifier `License :: OSI Approved :: GNU General Public License v3
  or later (GPLv3+)` — matches the "-or-later" LICENSE text exactly (not
  a plain-GPL-3.0/no-later-version mismatch, which would have been a
  real finding).
- Vendor dependency table in root `CLAUDE.md` (anthropic/rich/typer/
  pipdeptree, all MIT) — untouched by this diff and not a "current-truth
  doc misdescribing the system" concern: those vendors' own licences
  are unaffected by CodeCompass's relicensing, and CLAUDE.md is outside
  this audit's scope by project convention (§0 protected file) as well
  as factually still correct.
- CHANGELOG.md already carries an Unreleased entry naming 43d/43e and
  `decisions/0053` — not itself in scope for this audit (not one of
  README/docs/architecture/ai-docs) but noted as consistent.

## Scope note

Checked: `README.md`, `CONTRIBUTING.md`, `LICENSE`, `pyproject.toml`,
`decisions/0053`, all of `docs/`, `architecture/`, `ai-docs/` (grepped
and, where hits appeared, read in full), `examples/README.md`.

Deliberately not re-checked: `planning/**` bookkeeping edits (ROADMAP,
CONTEXT, v1-redefinition/* status files) — these are process/status
docs, not current-truth docs about the *system* per this audit's remit,
and the lead's diff summary already scoped them as closeout bookkeeping.
`decisions/0052` (Ledgerkit-first reorder) — no licence content, out of
scope for this specific drift question.

## Summary

No current-truth doc (`README.md`, `docs/`, `architecture/`,
`ai-docs/`) misdescribes the system after this relicensing. The only
places that mention the licence (README, CONTRIBUTING) were the ones
`docs-maintainer` edited, both are accurate and correctly cross-link
`decisions/0053` at its real path, and no other current-truth doc had
any latent MIT/GPL claim that the change could have made stale.
