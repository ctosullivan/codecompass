# Independent DoD audit — Phase 43d (GPL-3.0-or-later relicensing) + Phase 43e (agent-led adoption blueprint)

**Auditor:** release-phase-auditor (independent; read-only; did not repair anything found).
**Base:** working tree vs `HEAD` (`411cda6`), nothing committed yet.
**Scope:** both phases audited together, per the closeout package's own framing (shared drift audit, shared triage).

## Verdict: PASS

No blocking gap found. One non-blocking observation below (already resolved by the time this report was finalized — noted for the record, not a required fix).

## Evidence — verification re-run independently

1. **`ruff check .`** — re-run: `All checks passed!` (clean; no `src/` touched, as scoped).
2. **`python scripts/check_user_docs.py --strict`** — re-run: `check_user_docs: no findings` (0 findings, including the ADR `Status:`/cross-reference check against the two new ADRs).
3. **`pip show codecompass`** — re-run: `License: GPL-3.0-or-later` (already reflected without a fresh `pip install -e .`, since the editable install re-reads `pyproject.toml` metadata; confirmed live, not just asserted).
4. **`python -m pytest -q`** — re-run in full: `554 passed, 1 skipped in 164.84s` — identical count to the last recorded baseline (Phase 43b), confirming no regression and no test change, consistent with "no `src/codecompass/` change, no test change" claimed by both plans.
5. **`pyproject.toml`** — `license = { text = "GPL-3.0-or-later" }`; classifier `License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)`. Matches plan.

## Evidence — LICENSE text is genuinely canonical, not paraphrased

Fetched `hledgerorg/hledger`'s own `LICENSE` file directly via `gh api repos/hledgerorg/hledger/contents/LICENSE` (674 lines). Extracted the GPL body from CodeCompass's `LICENSE` (everything from the "GNU GENERAL PUBLIC LICENSE / Version 3" heading to the file's end, i.e. excluding only the CodeCompass-specific notice block prepended above the `---` separator) and diffed the two byte-for-byte: **`diff` produced zero output, exit code 0 — the two texts are identical**, confirming the "fetched verbatim, not retyped" claim is literally true, not just asserted.

Confirmed the "-or-later" clause is present in two places: the prepended CodeCompass notice block ("either version 3 of the License, or (at your option) any later version") and inside the canonical text's own "How to Apply These Terms" template section (same wording). This is what makes the licence genuinely GPL-3.0-**or-later**, not plain GPL-3.0 — both the SPDX-style classifier and the actual license text agree.

Spot-checked distinctive passages independently against known GPLv3 text while doing the above (preamble, §7 "Additional Terms", §14 "Revised Versions of this License", the "How to Apply" section) — all present and unmodified.

## DoD conditions (CLAUDE.md §5, as amended)

- **Docs updated:** `README.md` `## License` section and `CONTRIBUTING.md`'s new `## License` section both read correctly and cross-link `decisions/0053` at its real path (verified: the file exists at exactly that path).
- **`decisions/0052`/`0053`:** both have complete Status/Context/Decision/Alternatives considered/Consequences sections. `decisions/0052`'s Context correctly notes it does **not** supersede `decisions/0048`, only narrows the reference-project ordering — accurate, `0048` is unrelated/unchanged. All `decisions/NNNN` cross-references in both ADRs resolve (confirmed by `check_user_docs.py`'s ADR check, 0 findings, and by direct inspection).
- **`CHANGELOG.md`:** carries its own dedicated `[Unreleased]` entry for this execution — a **"BREAKING (licensing): Phases 43d + 43e"** entry, distinct from the prior commit's planning-only entry (which remains, accurately, a historical record of what that earlier commit did). The execution entry correctly states the licence change, the verified `pip show` result, both ADRs' acceptance, the "nothing published/tagged is affected" fact, and the drift-audit/triage outcome. This satisfies CLAUDE.md §3's "every phase adds an entry, in the same commit as the change" — confirmed via `git diff HEAD -- CHANGELOG.md`, not just the file's final text.
- **`planning/CONTEXT.md`:** reflects the new state accurately and consistently in both places it's discussed (the top-of-file "Current phase" narrative and the "Next concrete step" section) — both correctly state all three gates (G11/G12/G13) approved, both phases `done`, and the immediate next step is Phase 44/Stage B, not "await gate resolution." No internal self-contradiction (the failure shape L-006 previously recorded and fixed) found in the version audited.
- **`planning/ROADMAP.md`:** rows 43d and 43e both flipped to `done` with accurate one-line summaries.
- **Retros:** `planning/retros/phase-43d-gpl-relicensing-plan.md` and `phase-43e-agent-led-adoption-blueprint.md` both exist and fill every `TEMPLATE.md` section substantively (Where we are / Goal / Scope delivered vs planned / What was achieved / What worked / What didn't work / Lessons learnt / Process-improvement feedback / Candidate learnings filed / Where we're going / Time-cost note). Not stubs. `Commit(s):` and `Auditor verdict:` are placeholders pending this closeout commit — expected and correct at this stage, not a gap.
- **Candidate learnings triaged:** `planning/learnings/inbox.md` contains **L-009** and **L-010**, both with every required field (origin, date, project_revision, observation, evidence, classification, status, recurrence, curation note, promoted_to) and a reasoned `retain` outcome (single-occurrence, no clean owning artifact yet, explicit revisit trigger named for each). Both retros correctly reference their respective learning IDs.

## Protected-file drift

`git diff HEAD -- CLAUDE.md` — **empty**. No governance-file change, consistent with both plans' explicit "no `CLAUDE.md` edit" scope. `decisions/0048`–`0051` (past ADRs) are untouched by this diff (confirmed via `git status`: only `0052`/`0053` are new, nothing else in `decisions/` is modified) — no past ADR's original content was edited.

## Scope creep

Full changed-file list (`git status --porcelain`): `CHANGELOG.md`, `CONTRIBUTING.md`, `LICENSE`, `README.md`, `planning/CONTEXT.md`, `planning/ROADMAP.md`, `planning/learnings/inbox.md`, `planning/phase-43d-*.md`, `planning/phase-43e-*.md`, `planning/v1-redefinition/{README.md, licence-migration.md, proposed-governance-changes.md, realignment-2026-09.md, roadmap.md}`, `pyproject.toml`, plus new `decisions/0052-*.md`, `decisions/0053-*.md`, `planning/retros/{_drift-audit-phase-43d-43e.md, phase-43d-*.md, phase-43e-*.md}`. Every file is explained by "the licence change" (LICENSE/pyproject.toml/README/CONTRIBUTING/decisions/0053/CHANGELOG), "the blueprint gate" (decisions/0052 note: no content changes needed beyond the already-amended planning docs; adoption-blueprint.md itself is unchanged from the prior commit), or "closeout bookkeeping" (ROADMAP/CONTEXT/plan-file status lines/v1-redefinition bookkeeping docs/retros/learnings inbox). Confirmed **no** `src/`, `tests/`, or `.claude/` diff exists (`git diff HEAD --stat -- .claude/ decisions/ src/ tests/` shows only the two new `decisions/` files, nothing else). No scope creep found.

## Historical-integrity check

`git tag -l` — empty. `git log --oneline -10` shows only the expected prior linear history (`411cda6` as the most recent commit, nothing amended or rewritten); this phase's changes are all uncommitted working-tree state, about to land as new commit(s). The plan's own claim "nothing published is affected" holds — no tag, no PyPI release, no historical commit rewritten.

## Non-blocking observation (for the record only — already resolved)

During this audit, `planning/CONTEXT.md` was observed transiently in a state where its "Next concrete step" section still described the pre-approval, pre-execution picture (gates open, phases pending), contradicting the already-updated "Current phase" section higher in the same file — the exact self-contradiction shape `L-006` previously recorded and fixed at Phase 43b. By the time this report was written, the file's current state (re-verified via `git diff HEAD`) had both sections consistent and correct, so this is **not** carried forward as a required fix. Flagging only so the lead is aware the file was mid-edit during audit — re-confirm `planning/CONTEXT.md` is internally consistent one more time immediately before the closeout commit lands.

## Summary

Both phases meet every checked DoD condition: verification commands pass live: `ruff check .` clean, `check_user_docs.py --strict` clean (0 findings), `pytest` 554 passed / 1 skipped (no regression), `pip show codecompass` confirms `License: GPL-3.0-or-later`. The `LICENSE` text is independently verified byte-identical to `hledgerorg/hledger`'s own canonical file (diff exit 0), with the "-or-later" clause genuinely present. `decisions/0052`/`0053` are well-formed and correctly cross-referenced. `CHANGELOG.md` carries a dedicated entry for this execution, distinct from the prior planning-only entry. `CONTEXT.md` and `ROADMAP.md` reflect the new state. Both retros are substantive and complete. `L-009`/`L-010` are properly triaged with all required fields. No `CLAUDE.md` drift, no past-ADR edit, no scope creep, no tag/commit-history rewrite.

**Verdict: PASS.**
