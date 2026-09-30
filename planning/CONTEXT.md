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
`in progress`, direct user request, 2026-09-30, amended three times
(`decisions/0066`), approved 2026-10-01 and now executing. Does not
touch, reorder, or depend on Phase 78.**

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

**Phase 79's three-times-drafted plan also awaits direct user review**,
independently of Phase 78 (neither touches, reorders, or depends on the
other). Once approved, the next concrete step is: confirm the validation
topic (§14, proposed: the first-party source/symbol subsystem) live
against the repository; **run the full §6.3 multi-route preflight probe
set first** (filesystem, search, command, network, delegation), using
the observed raw tool-call transcript for each — not self-report — to
determine live which isolation label (`verified` / `filesystem-only,
network-exposed` / `best-effort`) each scope actually earns, **expecting
the network probe to succeed given CodeCompass's own public-repository
status**; produce the assertion records (`context-researcher`) and
adversarially review them (`domain-skeptic`, no human-review gate
follows); freeze the reviewed assertions into a versioned, hash-
integrity-checked snapshot (§5.2) — the shared input everything else
consumes; in parallel, build the Implementation-reconstruction export
(excluding `context-graph.db`) and dispatch the new
`implementation-reconstructor` role (model-blind, legacy-blind); once
both exist, dispatch a fresh `domain-skeptic` instance to classify
alignment against the snapshot (never auto-promoting a Claim to
`verified`); a fresh, isolated documentation dispatch selects its own
architecture and drafts the complete first version from the snapshot
(committed before reconciliation begins); legacy reconciliation;
**publication into real `docs/domain/`/`docs/`/`architecture/` content
for the topic**; frozen-question documentation-only Q&A + independent
verification, with findings fixed; a new frozen coding-context task,
packet, and independent `context-evaluator` assessment against the same
snapshot; the propagation demonstration in a disposable fixture (deleted
afterward, never touching real canonical knowledge or documentation);
and the `codecompass-template` deliverables plus a fresh downstream
usability exercise — per
`planning/phase-79-clean-room-understanding-and-documentation-reconstruction.md`'s
own §12 gate sequence, whose two tracks (workflow/template completion,
and strict clean-room validation) are reported separately — the second
is honestly expected to remain unmet for at least the network dimension,
which is not a human-decision gate and not grounds to delay reporting
the first track's own real completion.

Per `CLAUDE.md` §6, Phases 75, 76 (including its corrective pass), and 77
are fully closed and already pushed to `origin` — no further action
needed on any of them.
