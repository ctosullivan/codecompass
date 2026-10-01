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
`codecompass-template`, Priority A + Priority D) is `done`,** including
its independent `release-phase-auditor` completion audit (**PASS**,
`planning/retros/_audit-phase-77.md`, against final HEAD `d74ee47`) and
its terminal `roadmap-context-curator` reconciliation. Fully closed and
pushed to `origin`.

**Phase 78 (Priority A backlog rationalisation + second Ledgerkit
validation trial) is `planned`, direct user request, 2026-09-29, amended
same day — planning only, not yet implemented.** The amendment fixed six
real issues in the first draft: an exit-gate contradiction
(`task-not-applicable` was wrongly treated as equivalent to
`not-recurred` for closing Priority A — now evidence-neutral, triggers a
re-run via a new applicability gate, §7.2.0), a `CG-010`/Priority-A-closure
inconsistency (now resolved by an explicit strategic-closure-vs-
maintenance-backlog distinction, §3.1), a trial-design confound (both
arms independently inventing different implementation contracts and
comparing the implementations, not the context — restructured into a
discovery/design comparison, an independent evaluation, and an optional
shared-contract implementation check, §5.3), a missing observable-
evidence requirement (both arms' reports must now record files read,
queries run, commands executed — never private chain-of-thought, §5.3.4),
residual pre-judgment of the trial's own likely result (removed, §1), and
imprecise evaluation terminology (`internal` exposure is not uncertainty;
an omission is a completeness gap, not automatically a safety failure,
§6). Full amendment log: the plan's own §13.

Audits every still-open Priority A item/context gap
(`CG-001`/`CG-003`/`CG-007`/`CG-010`/`CG-011`, Phase 24/25/50) and
dispositions each against real evidence; designs (does not run) a second,
differently-shaped Ledgerkit trial against a genuine,
currently-unimplemented Stage D task (journal-comment `ReportSpec`
parsing, verified live as `[DEFERRED — Milestone 3]` in Ledgerkit's own
`dev-docs/api-spec.md`), specifically to test whether `CG-001`'s
first-party-relationship hypothesis (Phase 77's own explicitly-deferred
follow-on, §13 of that plan) is a real blocker before any such capability
is built. This is the second, differently-shaped Priority A Ledgerkit
trial Phase 75's own closeout recommended and Phase 77's own plan
explicitly deferred (precedes, does not replace) — now finally claimed
and scoped, not abandoned. Full plan:
`planning/phase-78-priority-a-closeout-and-second-ledgerkit-trial.md`.

**Phase 79 (Clean-room conceptual understanding + documentation
reconstruction, methodology hardening + Priority D template delivery) is
`done`** (direct user request, 2026-09-30, amended five times,
`decisions/0066`/`decisions/0067`, approved 2026-10-01 and executed the
same day). The phase's own prior terminal `done` flip is not reopened by
any of this — each amendment corrects that already-`done` result's own
output in place. A **fifth amendment** (`decisions/0067`), landed the
day after the original `done` flip via direct review of the delivered
result, implemented four further corrections: snapshot validation now
genuinely fails closed against a minimal-content fixture (not merely
against entries already present in a table), previously-dropped
documentation citations were restored and content-matched, the Track 2
isolation verdict was corrected with real new mechanical evidence (a
boundary-check script run against all six original pilot dispatches'
own still-extant transcripts, finding one real, previously-undetected
boundary deviation), and the template usability "exercise" — previously
only a link-integrity check — was replaced with a real downstream
adoption attempt by a fresh, context-free agent (found and fixed a real
`README.md`/`LICENSE` collision in the adoption instructions, pushed to
the real `codecompass-template` remote). An independent
`release-phase-auditor` audit of this fifth amendment
(`planning/retros/_audit-phase-79-fifth-amendment.md`, against
`b95a1f1`, re-confirmed in an appended addendum against the amendment's
own final commit `0e1c63a`) returned **Track 1 (workflow/template
completion): PASS WITH NON-BLOCKING OBSERVATIONS** — two trivial
narrative-only gaps (a "13 new tests" miscount, actually 11;
`CONTRIBUTING.md` not yet mirroring `CLAUDE.md`'s new `L-070` sentence)
were both fixed in the immediately following commit (`0e1c63a`) and
re-confirmed closed by the audit's own addendum. **Track 2 (strict
clean-room isolation validation) is confirmed, final, and honestly
reported as `UNMET`** — not a defect, the amendment's own intended
outcome: honest `best-effort` labelling throughout is not the same as
strict isolation actually being achieved; see
`planning/knowledge/first-party-source-symbols/isolation/isolation-evidence-inventory.md`
for the real, mechanically-derived evidence behind this verdict. This
terminal reconciliation (this commit) is the fifth amendment's own
closeout — the phase's `done` status on `planning/ROADMAP.md` is
unchanged by it. Does not touch, reorder, or depend on Phase 78. Fully
closed and pushed to `origin`. See "What was just completed" below for
the pre-fifth-amendment delivered result; the summary immediately
following this paragraph describes the pre-implementation,
fourth-revision plan and is retained for its own amendment history, not
as a description of current state.

**Revised objective (unchanged since the first amendment)**: one
evidence-backed knowledge foundation supplies both coding context and
project documentation — conceptual understanding is incorporated
directly into documentation, mechanical context separation is preserved.

**Third-revision corrections, same day, found by direct technical
inspection before any implementation began:**

1. **Isolation verification was too weak; completion criteria now split
   honestly.** A single self-reported failed read is not proof of a
   boundary — replaced with observed (raw tool-call transcript, not
   self-report) probes across filesystem, search, command, network, and
   delegation routes. **Most consequential finding: CodeCompass is a
   public GitHub repository, so network egress through a granted `Bash`
   can reach the "excluded" narrative content regardless of local
   filesystem isolation** — omitting `WebFetch`/`WebSearch` does not
   close this. Tier 2 (same-host export) is now *always* `best-effort`,
   never upgraded by an incidental probe result. The Definition of Done
   is split into two separately-reported tracks: workflow/template
   completion (fully satisfiable) and strict clean-room validation
   (honestly expected to remain **unmet** for the network dimension) —
   removing the human-review gate does not relax this.
2. **The pipeline was circular** — comparison needed "published
   documentation," writing needed that plus comparison, publication
   happened only after writing. Replaced with a linear chain: canonical
   assertions → a new **frozen knowledge snapshot** (versioned, hash-
   integrity-checked, cited as `<topic-slug>@v<N>#<id>`) → independent
   implementation reconstruction (model-blind — no access to the
   snapshot at this stage) → comparison → documentation architecture/
   draft (comparison and writing are what actually consume the
   snapshot, not not-yet-existing prose) → legacy reconciliation →
   publication. Understanding still lands directly in the final
   published documentation — once, at the real end of the chain.
3. **Dependency validation was verified false, not merely restated.**
   Direct, empirical testing confirms `scripts/check_knowledge_base.py`'s
   parser cannot see a YAML *block*-style list — `depends_on:` in that
   form parses as empty, silently passing validation with zero ids
   checked. The inline `[a, b]` form (this project's own universal
   existing convention) works correctly. This project's own prior claim
   that `depends_on` "already validates with zero code change" is
   corrected: true for inline, false in general — a new check now rejects
   the block form outright.
4. **Alignment no longer auto-promotes to `verified`.** An `aligned`
   comparison finding is recorded in the alignment report only — moving a
   Claim to `verified` needs its own claim-specific check against primary
   evidence, since implementation conformance never by itself proves a
   domain rule or proposed policy is correct.
5. **Coding context is now independently validated, not just cited.** A
   frozen, bounded task generates a real packet from the same snapshot
   the documentation uses; a fresh `context-evaluator` dispatch assesses
   it with this project's own existing `context-quality-evaluation.md`
   rubric (LOW/MODERATE/HIGH advantage) — reused, not invented.
6. **The propagation demonstration now runs in a disposable fixture**,
   deleted afterward — never leaving a synthetic `CONTROLLED TEST`
   contradiction in real canonical knowledge or real published
   documentation. Propagation also now starts from a changed *source
   file* (via Evidence's own citation fields), not an assertion already
   identified by hand, and the transitive `depends_on` walk is explicitly
   cycle-safe.

Everything else (the schema's field set minus `human_review_state`, the
`implementation-reconstructor` role, the draft-before-reconciliation
ordering, the Priority-B boundary, the validation topic) carries forward
unchanged. **Explicitly not Priority B** (no `src/codecompass/` change at
all). Full plan:
`planning/phase-79-clean-room-understanding-and-documentation-reconstruction.md`.

See "Next concrete step" below.

Backlog, each with its own revisit trigger: Phases 24/25, Phase 50's
remainder, `CG-003`, `CG-007`, `CG-011`, the `browser_api`/`platform_api`
kind — full detail `planning/pre-v1-disposition.md` and Phase 78's own §3
disposition table. `CG-010` is tracked separately as already-evidenced,
ready-to-fund Git-topology maintenance backlog (Phase 78's own §3.1) —
not waiting on a revisit trigger, and not gated on Priority A's own
strategic exit decision either way.

## What was just completed

**Phase 79 — Clean-room conceptual understanding + documentation
reconstruction — implementation complete, closeout finishing.**

Four checker functions landed in `scripts/check_knowledge_base.py`
(`check_optional_enum_fields`, `check_list_fields_are_inline` — fail-
closed, immediately found and fixed 15 real pre-existing YAML
block-list violations — `check_snapshot_historical_integrity`,
`check_snapshot_current_divergence`), 14 new tests, all passing
(`b42e6c8`/`38c8d7a`-range). New agent role `implementation-reconstructor`
plus extensions to `domain-skeptic` (comparison mode), `context-researcher`
(isolated mode), `docs-reconstructor` (hardened topic-scoped route),
`docs-maintainer` (legacy reconciliation mode), and
`planning/v1-redefinition/agent-led-development.md`'s own catalogue/
write-boundary table.

A live Tier-1 isolation preflight (`Agent(isolation: "remote")`) was run
for real and **failed all five tested routes** in this environment —
filesystem, search, command, network, and environment-identity all
reached content it was supposed to exclude (a same-host git worktree,
not a separate environment). Every downstream stage used Tier 2 and is
labelled `best-effort`, never `verified`, accordingly
(`planning/knowledge/first-party-source-symbols/isolation/tier1-preflight.md`).

Validated end to end on the real pilot topic (Phase 77's first-party
source/symbol subsystem, previously undocumented): 8 reviewed Claims
(`context-researcher` → `domain-skeptic` adversarial review, which
independently resolved all five of the research dispatch's own disclosed
open questions), a frozen-then-re-frozen snapshot (v1→v2, both with
passing historical-integrity/zero-divergence checks against real git
history), a model-blind `implementation-reconstructor` report (one
export-curation bug found and fixed mid-phase, disclosed rather than
silently corrected), a fresh comparison-mode `domain-skeptic` alignment
pass (promoted one Claim to `verified` via a real separate check, found
one genuine new knowledge-base gap), a disposable propagation-
demonstration fixture proving the full source→evidence→assertions→
transitive-dependents→snapshots→both-outputs chain including real
two-node cycle-safety (deleted afterward, zero survivors), published
documentation merged into `architecture/overview.md`/
`architecture/context-graph-schema.md` (not a new `docs/domain/` page —
that corpus turned out to be a separate, already-approved one for
CodeCompass's own meta-level concepts, not implementation subsystem
detail), a legacy-reconciliation pass (all 7 pre-existing claims
`supported`, one real documentation-verification gap fixed directly),
and two independent verification passes — one (coding-context packet)
**PASS, LOW advantage**; one (documentation Q&A) **5/6 confirmed, 1/6
wrong-and-fixed** (a real, pre-existing `core.Ecosystem`-cardinality
defect in `architecture/overview.md`, unrelated to this phase's own new
content, caught only by this independent check).

Nine portable workflow/guide templates delivered to
`https://github.com/ctosullivan/codecompass-template` and pushed
(confirmed via `git log origin/main..HEAD` empty), verified via a fresh-
clone link-integrity check before pushing.

Full test suite: 747 passed, 2 skipped. `ruff check .`: clean.
`check_knowledge_base.py --strict` / `check_user_docs.py --strict`:
clean (one expected, disclosed informational snapshot-divergence
finding). Retro: `planning/retros/phase-79-clean-room-understanding-and-documentation-reconstruction.md`.
Learning triage landed `L-068`/`L-069`, refined `L-023`. A docs-drift
audit found and fixed 4 non-blocking findings (a stale line-citation in
`docs/domain/concepts/claim.md`, two `agent-led-development.md` staleness
gaps, `CONTRIBUTING.md`'s incomplete agent roster) — persisted at
`planning/retros/_drift-audit-phase-79.md`.

An independent `release-phase-auditor` audit against the pre-CHANGELOG/
pre-CONTEXT.md-update commit (`cbf3582`) returned **Track 1 (workflow/
template completion): FAIL** — three real gaps (no `CHANGELOG.md` entry,
this file not updated past the pre-implementation plan state, no
persisted `_drift-audit-phase-79.md`) — and (at the time) reported
**Track 2 (strict isolation validation): "PASS"**, language a fifth
amendment the same day corrected: that audit genuinely confirmed the
`best-effort` labelling was honest throughout, but honest labelling of
an unenforced boundary is not the same as strict isolation being
achieved — the corrected verdict is **Track 2: UNMET**, unaffected by
and independent of any Track 1 fix (see the isolation-evidence-inventory
document cited above). All three Track 1 gaps were fixed (`d9b9175`). A
re-audit against `d9b9175` (`planning/retros/_audit-phase-79-reaudit.md`)
returned **Track 1: PASS** (all three fixes independently verified
genuinely closed, not merely present) and reconfirmed the same Track 2
language, since corrected identically; two further trivial, non-blocking
observations (the `claim.md` citation off-by-2, this file's own
duplicated Phase 78 paragraph) were fixed in the following commit
`a119f4c`. The terminal `roadmap-context-curator` reconciliation (this
commit) flips `planning/ROADMAP.md`'s Phase 79 row to `done`, per
`CLAUDE.md` §5's
narrow three-target exemption.

**Phase 77 — First-party source awareness (`CG-009`) + a usable
`codecompass-template` — `done`.**

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

Independent `release-phase-auditor` completion audit against final HEAD
`d74ee47`: **PASS** (`planning/retros/_audit-phase-77.md`), all 17
checked conditions held with real, independently-gathered evidence
(full 733-passed/2-skipped test run, `ruff check .` clean, both doc-check
scripts clean, the prior FAIL audit's own trip-wire defect confirmed
genuinely fixed, schema/ADR/docs cross-checked directly against live
code, the real `codecompass-template` repository independently confirmed
via the GitHub API, protected-file boundaries and commit hygiene clean,
no scope creep, scratch clones confirmed cleaned up), independently
re-confirmed by this `roadmap-context-curator` reconciliation. Full plan
(amended twice): `planning/phase-77-first-party-source-and-template.md`.

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

**Phase 78's twice-drafted plan awaits direct user review** (per its own
explicit instruction: "planning only... do not execute the trial or
implement CodeCompass/Ledgerkit code"). Once approved (or amended and
re-approved), the next concrete step is executing its §5 trial in stages:
Stage 1 — dispatch fresh baseline/treatment agents against seed-then-fork
Ledgerkit scratch clones (frozen at
`6c90b4ca3e6c10951cb400e43db4b90bfccc5909`) for discovery/design only (no
implementation) on the journal-comment `ReportSpec` parsing task, with
mandatory observable research traces (§5.3.4); Stage 2 — an independent
`context-evaluator` assessment producing the three-outcome `CG-001`
verdict (`recurred`/`not-recurred`/`task-not-applicable`, §4); if
`task-not-applicable`, re-run against the fallback task before proceeding
(§7.2.0); Stage 3 (optional, evaluator's own call) — a shared,
human-approved implementation contract given to fresh implementation
agents in both arms; then an independent `knowledge-curator` triage
applying Phase 78's own §7.2 exit gate (Priority A closure only on an
applicable `not-recurred` result, or the smallest evidence-supported
follow-on on `recurred`) — full detail:
`planning/phase-78-priority-a-closeout-and-second-ledgerkit-trial.md`.

Per `CLAUDE.md` §6, Phases 75, 76 (including its corrective pass), 77,
and 79 are fully closed and already pushed to `origin` — no further
action needed on any of them.
