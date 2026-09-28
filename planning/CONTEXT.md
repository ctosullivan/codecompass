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

**Phase 76 (Git repository topology awareness, Priority A) is `done`.**
It was originally implemented, independently rated by `context-evaluator`
(**PASS WITH GAPS, advantage MODERATE** — the strongest Priority A result
to date), audited by `release-phase-auditor` (**PASS WITH NON-BLOCKING
OBSERVATIONS**, `planning/retros/_audit-phase-76.md`), and marked `done`
the same day (`b3abe07`). A direct user post-closeout review then found
three real defects that closeout had missed, so the phase was reopened
the same day for a narrowly-scoped corrective pass. That corrective pass
is now itself complete: all three defects fixed, a fresh independent
`docs-reconstructor` drift audit found **NO DRIFT**
(`planning/retros/_drift-audit-phase-76-corrective.md`), `knowledge-
curator` triaged `L-065` to **promoted**, and a fresh independent
`release-phase-auditor` completion audit of the corrective pass itself
returned **PASS WITH NON-BLOCKING OBSERVATIONS**
(`planning/retros/_audit-phase-76-corrective.md`). `planning/ROADMAP.md`'s
Phase 76 row and `planning/phase-76-git-repository-topology.md`'s own
Status line both now read `done`. See "What was just completed" below
for the full corrective-pass history.

**Phase 77 (First-party source awareness (`CG-009`) + a usable
`codecompass-template`, Priority A + Priority D) is `in progress`**
(plan amended twice, 2026-09-28/29; implementation now underway per
direct instruction). The template repository already exists at
`https://github.com/ctosullivan/codecompass-template` (confirmed empty
at plan time) — Phase 77 delivers it populated, not merely designed.
See "Next concrete step" below for the full account.

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

**Phase 76 — Git repository topology awareness (worktrees + submodules),
originally `done`, reopened same-day for a corrective pass, now `done`
again with the corrective pass complete.**
New `git_topology.py` detection module (Git ≥2.7-compatible plumbing
only — corrected from an originally-claimed ≥2.5, see below — never
invoked outside `sync`); three new `context-graph.db` tables
(`git_repositories`, `git_worktrees`, `git_submodules`, schema version
9→10); `codecompass query topology` (`--json`, plus a narrow
not-yet-indexed path for brand-new projects via
`_open_graph_for_topology`, deliberately not touching the shared
`_open_graph_or_note` helper). Validated against this repository's own
real submodules and a disposable worktree/clone (all cleaned up).
Independently rated by `context-evaluator`: **PASS WITH GAPS, advantage
MODERATE** — the strongest Priority A result to date. New gaps `CG-010`
(submodule mismatch has no field distinguishing committed-parent-state
divergence from local uncommitted checkout state) and `CG-011` (a
sibling worktree's stale/unprobed dirtiness has no inline CLI signal)
filed, both `candidate`, triage confirmed by `knowledge-curator`.
Process learning `L-064` filed and **promoted**: a genuine recurrence of
`L-063` (one phase after it landed) — self-caught and disclosed by the
dispatched `context-evaluator`, filed honestly with root-cause analysis,
now landed as real text in `planning/agent-led-workflow.md` steps 5 and
7 (write referenced agent reports to disk immediately on receipt). Also
fixed a real, pre-existing bug found via live testing:
`_migrate_doc_artifacts_constraints` fired on any unrelated
`meta.schema_version` bump, not only when `doc_artifacts` itself needed
migration — confirmed via `git log` that Phases 60 and 62 both would
have triggered it unnecessarily; replaced with an introspection-based
check. Docs-reconstructor drift audit found and fixed two real gaps
(`README.md`/`ai-docs/README.md` never mentioned Git topology
awareness); re-audit confirmed **NO DRIFT**. Independent
`release-phase-auditor` completion audit against `644e818`: **PASS WITH
NON-BLOCKING OBSERVATIONS** (`planning/retros/_audit-phase-76.md`), all
13 checked conditions held, four cosmetic/process-precision observations
recorded, none requiring a fix; phase marked `done` at `b3abe07`
(same day).

**Reopened the same day (2026-09-28)** after a direct-user post-closeout
review found three real defects that closeout had missed: (1) the CLI
`query topology` text renderer collapsed several nullable/unresolved
topology facts (`is_dirty`, `revision_matches_pin`, submodule
`child_is_dirty`) into false-certainty negatives (e.g. an unresolved pin
comparison rendered as "differs from pin" instead of "comparison
unresolved"); (2) the documented Git minimum-version floor was wrong —
the real floor is Git 2.7, not 2.5, since `git worktree list`/`git
remote get-url` (both called unconditionally) were only introduced in
Git 2.7.0, confirmed against Git's own release notes; (3) `CLAUDE.md`
§5's own closeout rule was internally self-contradictory (the terminal
reconciliation commit it requires necessarily touches files the same
rule calls "audited scope," which would void the very audit that
authorizes it). All three now fixed on `main`: `feaaaa0` (CLAUDE.md §5
exemption, diff presented to and approved by the user per §0), `db33352`
(CLI rendering fix + 4 new regression tests), `bb21122` (Git version
floor fix, `decisions/0064` superseding `decisions/0063` point 8, doc
updates + 2 new regression tests), `6d668db` (operationalizing the
CLAUDE.md fix in `planning/agent-led-workflow.md` step 14 and
`.claude/agents/roadmap-context-curator.md`, plus filing `L-065` as
`candidate`), `a89920d` (plan-file corrective-pass amendment +
`CHANGELOG.md` entry), `48a5fea` (interim `ROADMAP.md`/`CONTEXT.md`
reopening reconciliation), `924bea5` (retro corrective-pass addendum),
`0db424a` (fresh `docs-reconstructor` drift audit, **NO DRIFT**),
`8ab36aa` (backfilled `L-065`'s `CLAUDE.md` §5 change into
`planning/v1-redefinition/proposed-governance-changes.md`), `f7016e9`
(`knowledge-curator` triage of `L-065` landed — **promoted**, confirmed
sound and complete against all three artifacts it names), `71231ea`
(fresh independent `release-phase-auditor` completion audit of the
corrective pass itself persisted — **PASS WITH NON-BLOCKING
OBSERVATIONS**, `planning/retros/_audit-phase-76-corrective.md`, its one
blocking precondition — committing the `L-065` triage — resolved before
this reconciliation). Full suite independently re-verified at this
reconciliation: 694 passed, 2 skipped; `ruff check .` clean;
`check_user_docs.py --strict` and `check_knowledge_base.py` both clean.
**Corrective pass complete — Phase 76 restored to `done`** by this
`roadmap-context-curator` reconciliation, per `CLAUDE.md` §5's narrow
three-target terminal-reconciliation exemption. Full plan (including
corrective-pass amendment): `planning/phase-76-git-repository-topology.md`.
Retro: `planning/retros/phase-76-git-repository-topology.md`.

**Phase 75 — Priority A Ledgerkit validation (real-task evaluation, no
`src/` change).** A genuine baseline-vs-CodeCompass-assisted comparison
on hledger's `cur:` query-term design/discovery task in Ledgerkit's own
query engine, independently rated by `context-evaluator`:
**PASS WITH GAPS, advantage LOW**. `CG-001` stays `candidate`; a new
gap `CG-009` (zero first-party-source symbol index, any ecosystem) was
filed and confirmed `candidate`; `CG-007` got a "no new evidence"
cross-reference. Two process learnings landed: `L-062`
(baseline/treatment dispatch prompts must state read-scope symmetry
explicitly, `reference-project-protocol.md` §2.2) and `L-063` (a
dispatch prompt must never claim a fresh subagent already has access to
conversation-only content, `agent-led-workflow.md` step 7). Full
report: `planning/reference-projects/ledgerkit/04-cur-query-priority-a-validation.md`.
Recommended next step: a second, differently-shaped Priority A
validation trial before any funding decision on `CG-001`/`CG-007` — this
was superseded by the direct user request that produced Phase 76 above,
not abandoned (see "Next concrete step" below).

**Undocumented-elsewhere decisions from this phase's closeout, now
recorded here:**

- `CG-001`'s status has a provisional-then-reversed history worth
  remembering exactly: the lead's own gap analysis first moved it
  `candidate` → `recurred` on this phase's evidence; `knowledge-curator`'s
  own independent same-phase triage reviewed that call and reversed it
  back to `candidate` (the evaluation report's own `context-evaluator`
  section had already recommended cross-reference-not-promotion using
  this entry's own established precedent); the lead reviewed and
  concurred with the reversal. The final, authoritative record is
  `planning/context-gaps/inbox.md`'s own `CG-001` entry. This reversal
  was not propagated to four other artifacts on the first closeout
  attempt (`planning/reference-projects/ledgerkit/04-cur-query-priority-a-validation.md`,
  `planning/ROADMAP.md` (both the Priority A row and the `CG-009` row),
  `CHANGELOG.md`, and the phase retro) — `release-phase-auditor`'s first
  completion-audit pass caught this as a real `FAIL` (a cross-document
  propagation defect, not a fabrication); the lead fixed all four plus
  one more, and the re-audit (`planning/retros/_audit-phase-75.md`)
  confirmed every fix landed and swept the repository for the same
  defect class, finding nothing further.
- **Phase 75 is the first phase closed under the corrected closeout
  process** (the `L-060`/`L-061` root-cause fix landed just before this
  phase, `d4f5e0a`, itself following the discovery that Phases 70-74 had
  been self-serving this exact reconciliation step). This
  `roadmap-context-curator` reconciliation is itself part of confirming
  that fix holds — the corrected sequence (drift audit → interim
  reconciliation → retro → learning triage → completion audit →
  only-on-`PASS` final reconciliation) caught a real, non-trivial defect
  on its very first real exercise (the `CG-001` propagation `FAIL`
  above) rather than rubber-stamping the phase, which is direct evidence
  the fix is working as intended rather than merely present in the
  process documents.
- Independently re-confirmed at this reconciliation (not re-derived from
  the audit's own word alone): `pytest` (641 passed, 2 skipped),
  `ruff check .` (clean), `check_user_docs.py --strict` and
  `check_knowledge_base.py` (both clean), `planning/context-gaps/inbox.md`'s
  `CG-001` entry is internally consistent, `L-062`/`L-063` are genuinely
  present at both of their claimed destinations, and no protected file
  (`CLAUDE.md`, `decisions/*`) was touched this phase.

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
- `symbols` has no path for a project's own first-party source, any
  ecosystem (`CG-009`, filed Phase 75) — `vendor_id NOT NULL` FK means
  only tracked vendor dependencies are indexed, never a project's own
  code.
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

**Phase 77 (First-party source awareness + a usable `codecompass-
template`) is planned (amended), not yet implemented** — direct user
request, `planning/phase-77-first-party-source-and-template.md`. Two
connected goals: (1) make a project's own first-party source files/
top-level symbols queryable, independent of `vendor.toml`, closing
`CG-009` (verified live and still accurate); (2) **deliver a genuinely
usable, populated, MIT-licensed `codecompass-template` repository** —
`https://github.com/ctosullivan/codecompass-template` **already exists**
(confirmed empty via direct inspection) — Priority D's first concrete,
delivered scaffold, not merely a design.

**Amended 2026-09-28** after direct user review found twelve issues in
the initial plan, all now fixed: `source_files` gains a first-party
**`language`** concept (Python/Rust/JavaScript/TypeScript/Haskell),
deliberately **not** a reuse of `core.Ecosystem` (whose single `npm`
value cannot distinguish JavaScript from TypeScript — a real ontology
mismatch, not a naming choice); `language`/`content_hash` and a new,
explicit four-state `symbol_index_status` (`indexed`/`unsupported`/
`parse_error`/`unreadable`, modeled on `git_topology.RepositoryTopology`'s
own status+reason precedent) are **nullable on both fresh and upgraded
databases identically** — no more "`NOT NULL` for new, nullable-until-
repopulated for old" divergence; `source_symbols`' identity is
**occurrence-based** (`UNIQUE(source_file_id, name, kind, line)`, not
name-only) after **live-verifying** that a name-only key crashes a real
`sync` on genuine function overloads — confirmed on both a real
`@typing.overload`-stacked Python function and a real overloaded
TypeScript function declaration, each producing 3 same-named rows;
first-party extraction now covers **implementation scope**, not an API
surface — non-exported/private top-level declarations are included, with
a new `visibility` property (`public`/`private`) recorded, never used to
filter a symbol out (Python needed no scope change at all — it already
had no export filter; Rust/JS/TS extractors are widened to match with-or-
without `pub`/`export`). New CLI commands (`query source`,
`query source-symbol`) apply Phase 76's own corrected tri-state-label
discipline from first implementation, not as a later fix. Three required
validations, now using the **real** template repository: populate and
push it (§8-§9 of the plan), then validate against a real clean clone of
it (the zero-vendor acceptance test), plus a fresh Ledgerkit clone
testing `Posting`/`Amount`/`Tag`, plus CodeCompass's own dogfooding, plus
an independent Priority A task-context evaluation. **Still explicitly
precedes, does not replace,** the second differently-shaped Priority A
Ledgerkit trial Phase 75 recommended — that trial's own `CG-001`
motivating shape needs first-party *relationships* (this phase's own
explicitly-deferred follow-on), unaffected by this amendment.
**Second amendment (2026-09-29, direct user instruction) adds five
further corrections and proceeds directly into implementation**: a
project-level `meta.source_index_version` marker distinguishing
never-indexed from indexed-but-empty (mirroring `git_topology_status`'s
own absence-means-never-synced precedent); `source_symbols.line INTEGER
NOT NULL` (a location-less occurrence is never emitted); a five-value
`exposure` concept (`public`/`restricted`/`internal`/
`conventional_private`/`unknown`) replacing the first amendment's own
public/private binary, capturing Rust's real three-tier visibility
model (live-verified against 8 representative forms); an honest
`indexed`/`indexed_partial` extraction-fidelity distinction (Python's
real AST parser vs. Rust/JS/TS's coarse line-scan/regex techniques); and
corrected `CG-009` roadmap wording ("reassess at Phase 77 closeout using
Ledgerkit validation and normal context-gap triage," not automatic
closure). Implementation is now underway — see below for progress.

Per `CLAUDE.md` §6, Phase 76 (including its corrective pass) is fully
closed and already pushed to `origin` — no further action needed on it.
