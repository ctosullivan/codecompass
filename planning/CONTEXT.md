# Project context

This file reflects the *current* state of the project — overwritten at
each stopping point, not appended to. See `CHANGELOG.md` and
`planning/retros/` for history; per `CLAUDE.md` §4, this file is for
session-resumption, not a project history.

## Current phase

**CodeCompass v1.0.0 is released.** The redefined-v1 milestone group
(`decisions/0048`, Phases 0–70) is complete and closed: published to
PyPI as the `codecompass-context` distribution (CLI command and Python
import package both stay `codecompass`), tagged `v1.0.0`. Current-state
description of what CodeCompass does: `README.md`,
`architecture/module-map.md`, `docs/quickstart.md` — not this file.
Full status: `planning/ROADMAP.md`. Closeout record:
`planning/v1-closeout.md`.

Post-v1 work is organised into six priorities (A-F,
`planning/ROADMAP.md`'s "Post-v1 priorities" section, `decisions/0062`),
not lettered stages. Priority A's first concrete deliverable
(Phase 73, `CG-006`), Priority B's first hardening step (Phase 74,
`L-031`/`L-032`), and Priority A's first real-task validation trial
(Phase 75) are all **done**, audited, and closed.

**Phase 76 (Git repository topology awareness, Priority A) is `done`,**
including its same-day post-closeout corrective pass (three real
defects found and fixed, fresh drift audit **NO DRIFT**, fresh
`release-phase-auditor` **PASS WITH NON-BLOCKING OBSERVATIONS**). Fully
closed and pushed to `origin`; no further action needed. Full history in
`planning/retros/phase-76-git-repository-topology.md` and prior
`CONTEXT.md` git history if needed.

**Phase 77 (First-party source awareness (`CG-009`) + a usable
`codecompass-template`, Priority A + Priority D) is `in progress` —
implementation and every pre-audit closeout step complete; only the
independent `release-phase-auditor` completion audit and the terminal
done-flip reconciliation remain.** See "What was just completed" and
"Next concrete step" below for the full account.

Backlog, each with its own revisit trigger: Phases 24/25, Phase 50's
remainder, `CG-003`, the `browser_api`/`platform_api` kind — full detail
`planning/pre-v1-disposition.md`. Separately, a **second, differently-
shaped Priority A Ledgerkit validation trial** was recommended at
Phase 75's own closeout — this remains a live, valid recommendation, but
it was never actually numbered (no plan file was ever written for it, so
per `CLAUDE.md` §1 no phase number was ever reserved); Phase 76 went to
the git-topology phase instead, at direct user request, and Phase 77
goes to first-party source awareness next, also at direct user request.
Phase 77's own plan explicitly analyses this: it **precedes, does not
replace,** the second trial, since that trial's own `CG-001` motivating
shape needs first-party *relationships* (Phase 77's own explicitly-
deferred follow-on) to even be attemptable. The Ledgerkit trial
recommendation is not abandoned, just not yet phase-numbered.

## What was just completed

**Phase 77 — First-party source awareness (`CG-009`) + a usable
`codecompass-template` — implementation and every pre-audit closeout step
now complete; the phase itself remains `in progress`, not `done`.**

Implementation (`03f8519`): new `source_files.language`/`content_hash`/
`symbol_index_status`/`symbol_index_diagnostic` columns (nullable
identically on fresh or migrated databases, `_migrate_source_files_columns`,
`ALTER TABLE ADD COLUMN` only — `source_files.id` is referenced by
`uses_edges ON DELETE CASCADE`); a `Language` concept (python/rust/
javascript/typescript/haskell) deliberately distinct from `core.Ecosystem`
(whose single `npm` value cannot distinguish JS from TS); new
`source_symbols` table with occurrence-based identity
(`UNIQUE(source_file_id, name, kind, line)`, `line NOT NULL`) after
live-verifying a name-only key crashes real `sync` on genuine function
overloads (Python `@typing.overload` and TypeScript both reproduced); a
five-value `exposure` (public/restricted/internal/conventional_private/
unknown, live-verified against 8 real Rust visibility forms); a new
`source_symbols.py` module; `codecompass query source`/
`query source-symbol`; `meta.source_index_version` distinguishing
never-indexed from indexed-but-empty; `decisions/0065`.

`codecompass-template` (`https://github.com/ctosullivan/codecompass-template`,
confirmed empty at plan time) is now **populated and pushed to its own
real remote**, cross-linked from `README.md`/`ai-docs/README.md`
(`5993113`).

Three real validations persisted: the template repository's own clean
clone (zero-vendor acceptance test), Ledgerkit, and CodeCompass's own
dogfooding (`planning/reference-projects/codecompass-self/phase-77-validation.md`,
`planning/reference-projects/ledgerkit/05-phase-77-first-party-source-validation.md`,
`910fb35`).

An independent Priority A task-context evaluation was persisted for both
reference projects — verdict **PASS WITH GAPS, advantage LOW**
(`planning/reference-projects/codecompass-self/phase-77-context-evaluation.md`,
`planning/reference-projects/ledgerkit/phase-77-{fixture-equivalence,baseline-report,treatment-report}.md`,
`b473e84`, `f75bd99`).

`CG-009` was reassessed and resolved by independent `knowledge-curator`
triage, re-verified by direct code reading (not taken on the entry's own
or `context-evaluator`'s word) — **promoted-to-roadmap**
(`planning/context-gaps/inbox.md`, `5398eb3`).

Independent `docs-reconstructor` drift audit ran twice: the first pass
found three real findings (stale migration count, incomplete CORE module
list, incomplete exposure enumeration), all fixed (`04b87c2`); the
re-audit confirmed **NO DRIFT** (`planning/retros/_drift-audit-phase-77.md`,
`490ce4d`). An independent `domain-skeptic` citation-currency review of
five `docs/domain/` pages found stale citations; all fixes applied
(`68e80b3`, `41ed6aa`).

A phase retro exists
(`planning/retros/phase-77-first-party-source-and-template.md`, `4fb9483`).
Two new learnings triaged: `L-066` (confirms `L-064`'s already-landed
`agent-led-workflow.md` fix worked cleanly on its first real exercise —
**discarded**, no new gap) and `L-067` (two schema/plan-design
heuristics from the second plan amendment — binary-first-guess is often
wrong for a cross-language concept; live-verify a natural key against
ordinary real code before committing to schema — real and evidenced but
single-phase, **retained** as a candidate, not yet promotable to one
specific artifact) (`planning/learnings/inbox.md`, `f92d3f2`).

**Still pending, blocking `done`:** an independent `release-phase-auditor`
completion audit (not yet dispatched) and, only after its own `PASS` or
`PASS WITH NON-BLOCKING OBSERVATIONS`, the terminal done-flip
reconciliation (`ROADMAP.md`'s phase row, this file's current-state
section, and the plan file's own Status line only, per `CLAUDE.md` §5's
narrow terminal-reconciliation exemption). Full plan (amended twice):
`planning/phase-77-first-party-source-and-template.md`.

**Phase 76 — Git repository topology awareness (worktrees + submodules)
— `done`,** including its same-day post-closeout corrective pass (three
real defects found and fixed; fresh `docs-reconstructor` audit **NO
DRIFT**; `L-065` **promoted**; fresh `release-phase-auditor` **PASS WITH
NON-BLOCKING OBSERVATIONS**, `planning/retros/_audit-phase-76-corrective.md`).
Fully closed and pushed to `origin`. Full history:
`planning/retros/phase-76-git-repository-topology.md`.

**Phase 75 — Priority A Ledgerkit validation — `done`.** Real-task
evaluation (hledger's `cur:` query term in Ledgerkit's own query
engine); `context-evaluator` verdict **PASS WITH GAPS, advantage LOW**;
`CG-001` stayed `candidate`; `CG-009` filed (now resolved by Phase 77
above). Full report:
`planning/reference-projects/ledgerkit/04-cur-query-priority-a-validation.md`.

## Known standing gaps (current-state facts, not phase history)

- Cargo adapter (`decisions/0014`) never validated against real `cargo
  metadata` output or a real crate — no Rust toolchain available yet.
- `extract_npm_symbols` untested against real-world `.d.ts` authoring
  styles beyond hand-written fixtures.
- `chat.py` never run against the real Anthropic API in this
  environment.
- `staleness.py`'s version parser has no real PEP 440/semver
  correctness — string comparison only.
- No formal trigger-accuracy evaluation harness for per-vendor Skills.
- Cursor `.mdc` export has no `globs` field.
- A pre-Phase-74 `symbol_enrichment` row's producer remains honestly
  unknown (`NULL`) — new rows are attributed, historical ones cannot be
  retroactively.
- A submodule pin/checkout mismatch has no field distinguishing
  committed-parent-state divergence from purely local uncommitted
  checkout state (`CG-010`, filed Phase 76) — `codecompass query
  topology` gives the two SHAs and a match/mismatch verdict, but
  determining *why* they differ still requires `git status`/`git diff
  --cached` directly.
- A sibling worktree's dirtiness, when unprobed/stale, is honestly
  reported as such but carries no inline CLI signal that this could be
  the case — only `--help` text documents the sync-time-snapshot
  guarantee (`CG-011`, filed Phase 76).
- `vendor/` and a local `.venv/` exist in this checkout (both
  gitignored, freely regeneratable) — live artifacts, not fixtures.

## Next concrete step

**Dispatch an independent `release-phase-auditor` completion audit of
Phase 77**, against the exact commit at the top of this file
(`f92d3f2`), checking every `CLAUDE.md` §5 condition against real
evidence (not the implementing/curating agents' own word): code
implemented and its plan file's verification steps pass; `docs/`/
`architecture/`/`decisions/` updated (`decisions/0065`); independent
`docs-reconstructor` drift audit found no remaining drift (confirmed
twice, second pass **NO DRIFT**); changelog entry present; this file
reflects current state (just done); phase retro exists; candidate
learnings (`L-066`, `L-067`) triaged; `codecompass-template` genuinely
populated, pushed, and validated by a real clean clone; `CG-009`
triaged using real evidence (done — **promoted-to-roadmap**); an
independent Priority A task-context evaluation exists and is linked
(done — **PASS WITH GAPS, advantage LOW**); all disposable scratch
clones/fixtures confirmed cleaned up.

**Only after that audit returns `PASS` or `PASS WITH NON-BLOCKING
OBSERVATIONS`** does the terminal done-flip reconciliation happen — a
narrowly-scoped `roadmap-context-curator` dispatch touching only
`planning/ROADMAP.md`'s Phase 77 row, this file's current-state section,
and `planning/phase-77-first-party-source-and-template.md`'s own Status
line, per `CLAUDE.md` §5's narrow terminal-reconciliation exemption — no
other file, even a genuinely correct one, in that specific commit.

Separately, still live and unclaimed (not superseded by Phase 77): a
**second, differently-shaped Priority A Ledgerkit validation trial**
recommended at Phase 75's closeout, needing first-party *relationships*
that Phase 77 explicitly deferred as its own follow-on.

Per `CLAUDE.md` §6, Phases 75 and 76 (including Phase 76's corrective
pass) are fully closed and already pushed to `origin` — no further
action needed on either.
