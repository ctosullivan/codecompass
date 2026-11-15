# Phase 88 retro: Agent Integration and MCP

- **Date:** 2026-11-15
- **Commit(s):** `7a96d89` (Stage 88A), `a554d52` (Stage 88B +
  Ledgerkit demonstration), `4763fcb` (learnings triage L-131-L-134),
  `65ab8d9` (terminal-audit corrective pass — drift fixes and
  `CONTEXT.md` reconciliation)
- **Agents used:** `knowledge-curator` (two dispatches: Stage
  88A/88B/demonstration independent audits were performed by
  `release-phase-auditor` directly rather than a separate curator pass;
  the phase-wide learnings triage was `knowledge-curator`'s own),
  `release-phase-auditor` (Stage 88A, Stage 88B, the terminal pass —
  FAIL, then a re-audit — PASS), `docs-reconstructor` (one per-phase
  drift audit, NO DRIFT), `context-evaluator` (independent verification
  of the Ledgerkit demonstration's negative control and context
  relevance).

## Where we are

Phase 88 is the first phase of the v2-redefinition roadmap's third real
deliverable group (`planning/v2-roadmap.md` lines 115-128), built
directly on three already-`done` foundations: Phase 83's change-impact
analysis, Phase 84's consolidated knowledge API, and Phase 87's
documentation-grounding surface. It is a split-out half of what used to
be one merged "Phase 88" (`decisions/0084`/`0085`) — the sibling half,
Phase 89 (incremental knowledge/documentation reconciliation), is
independently deliverable and untouched by this phase's own work. After
this phase, CodeCompass has a working, 12-tool MCP stdio server
(`codecompass mcp-serve`) that a real coding-agent client can connect
to for read-only knowledge/context/documentation retrieval and, opt-in,
controlled oracle-check execution — the first time any of Phase
82/83/84/87's existing logic has been exposed to a connected agent
through a transport other than the CLI. Phase 90 (comparative
development trials) needs this phase's MCP surface genuinely operable,
alongside 83/84/87/89, before its own methodology can run.

## Goal

Deliver a minimal, model-neutral, read-mostly MCP server exposing
CodeCompass's existing knowledge, provenance, contextual retrieval,
change-impact analysis, documentation grounding, and controlled
verification to a real coding agent, and prove its usefulness through
a genuine Ledgerkit development task — without duplicating Phase
82/83/84's own existing logic or expanding into Phase 89/90 scope.

## Scope delivered vs planned

**Planning** (five independently-reviewed amendment rounds, 2026-11-12
through 2026-11-15; full history: `planning/
phase-88-agent-integration-mcp.md` §15-§19, `decisions/0095`):
implementation-ready plan for a 12-tool stdio MCP server. Every
planning round found and fixed real defects before implementation
began, rather than discovering them in code — a genuine example of
planning review earning its cost (§17/§17.9's symlink/TOCTOU findings,
§18.1's descriptor-persistence correction, §18.3's oracle-schema
correction all predate any line of `src/codecompass/mcp/`).

**Stage 88A** (committed `7a96d89`): all nine read-only tools, as
planned. The §17/§17.9/§18.1 filesystem-confinement designs — specified
but not yet coded when planning closed — were implemented exactly as
designed (`_read_confined_bytes`, `_open_confined_dir_fd`/
`_open_confined_subdir_fd`, the `confined_dir_fd` parameter threaded
through `load_slug_records`/`_load_slug_results`/
`_results_by_test_ref`/`_find_contract_for_slug`), verified by a genuine
directory-substitution-after-open adversarial test, and independently
audited PASS WITH NON-BLOCKING OBSERVATIONS (one gap, closed same day).

**Stage 88B** (committed `a554d52`): all three assurance tools, as
planned. `change_impact.py`'s relocation and `oracle.py`'s §5.3
hardening both matched the plan's own design exactly. Independently
audited PASS WITH NON-BLOCKING OBSERVATIONS (one gap, closed same day;
one process-evidence gap — no persisted Stage 88A audit record — also
closed same day).

**Demonstration** (`planning/retros/
phase-88-ledgerkit-demonstration.md`, committed `a554d52`): run against
disposable scratch copies, not the real `~/projects/ledgerkit`
checkout, per this task's own cross-repository constraint — the
**weaker**, not equivalent, variant named in the plan's own §12.2
fallback. All three of its claims (a correct new regression test;
genuinely relevant, materially-used knowledge context; the real
checkout left untouched) independently verified by a fresh reviewer.
The real Ledgerkit gap itself (`overlapping-account-patterns-no-double-
count` has no passing result against the real checkout) remains open,
honestly, pending a separate cross-repository authorisation this task
was not given.

**Not delivered / deferred, matching the plan's own exclusions, never
silently dropped**: a real sandbox/container for `oracle_execute_check`
(named future work, §5.2); landing the new test in the real Ledgerkit
checkout (requires separate authorisation); Phase 89 (incremental
knowledge/documentation reconciliation) and Phase 90 (comparative
development trials) — both explicitly out of this phase's scope and
untouched.

## What was achieved

A working `codecompass mcp-serve` CLI command and `src/codecompass/
mcp/` package (`security.py`, `tools.py`, `server.py`) exposing 12
MCP tools over the standard stdio transport to any connected MCP
client. Nine read-only tools cover knowledge retrieval, provenance,
context packets, gap-finding, and documentation grounding; three
assurance tools cover change-impact classification and controlled,
opt-in oracle-check execution. Every tool is a thin, validating,
confining wrapper over an already-shipped function — no new knowledge
store, impact engine, or verification framework was created. A real,
latent cross-cutting defect (the `cwd`-dependent `oracle.py` relative-
path convention, affecting six already-shipped tools) was found and
fixed uniformly. A genuine, independently-verified Ledgerkit
development demonstration proved the full MCP chain (discovery →
context → impact classification → oracle execution) works end to end
against real knowledge and a real behavioural gap, on a disposable
scratch copy.

## What worked

- The plan's own extensive, repeatedly-amended security-finding history
  (§17 through §19) made implementation materially faster and more
  confident: every confinement fix at implementation time was "build
  exactly what §17.9.3/§18.1 already specified," not a fresh design
  decision. The cost of five amendment rounds before any code existed
  was real but front-loaded and bounded; it is hard to imagine the
  equivalent confinement bugs being found this precisely after the fact,
  across six call sites, without that planning investment.
- Stage-level audits (88A, then 88B) before the terminal phase audit
  caught stage-specific gaps (test-coverage completeness, a malformed-
  input edge case) while the relevant code was still fresh and small,
  rather than accumulating into one large terminal-audit finding list.
- The scratch-copy Ledgerkit demonstration, done rigorously (fresh HEAD
  pin, byte-identical reapplication of an already-documented mutation,
  independent reviewer reproduction), delivered genuinely strong
  evidence for the MCP chain's correctness without ever touching the
  real checkout — the plan's own §12.2 pre-authorisation of this
  fallback paid off exactly as designed when real-checkout authorisation
  wasn't available.

## What didn't work

- An audit's own verdict was reported accurately in the moment (Stage
  88A) but not written to `planning/retros/` until Stage 88B's own
  audit flagged the absence days later — the record had to be
  reconstructed retroactively from the original reviewing agent's
  hand-back report rather than captured live.
- The terminal, whole-phase audit FAILed twice before reaching PASS:
  first because no independent `docs-reconstructor` drift audit had
  ever run for this phase (which, once run, found real live drift —
  a stale "once Stage 88B lands" conditional that outlived the
  condition becoming true), and because `planning/CONTEXT.md`'s
  current-state section had gone stale relative to real git history;
  second because this phase's own retro was missing several of
  `TEMPLATE.md`'s required sections (`Where we are`/`Where we're
  going`/separately-framed `What worked`/`What didn't work`/`Candidate
  learnings filed`) — accepted by the first terminal-audit pass on the
  strength of `CLAUDE.md` §5's narrower four-item list alone, caught
  only by a second, independent re-audit holding the retro to
  `release-phase-auditor`'s own fuller governing checklist.
- The learnings-triage dispatch failed mid-run once on a session-level
  rate limit, independent of this session's own token budget — cost a
  delay, not a defect, but worth noting since it wasn't immediately
  obvious it wasn't a real failure.

## Lessons learnt

1. **A relative-path convention that only ever ran from one well-known
   working directory (the CLI) had a latent defect that only a
   different kind of caller (a long-running server) could expose.**
   `oracle.evaluate_result_precedence`'s `Path(raw_output_ref).is_file()`
   check implicitly depended on the process's own cwd matching
   `project_root` — true for every CLI invocation by convention, never
   actually enforced in code, and never visibly wrong until Stage 88B's
   own `tmp_path`-based tests (which deliberately use a project_root
   *different* from pytest's own cwd) exercised it. Six of Stage 88A's
   own already-shipped, already-audited tools carried this same latent
   defect. Found and fixed only because Stage 88B's testing happened to
   be more rigorous about cwd independence than Stage 88A's own
   real-corpus tests (which, run from the repository root, never
   revealed it). **Generalisable lesson**: a convention enforced only by
   "how we always happen to invoke this" is not actually enforced;
   wrapping a new entry point (a server, here) around existing logic is
   exactly when such conventions get silently violated for the first
   time, and is worth deliberately testing for cwd-independence whenever
   a new, differently-invoked caller is added to code with any relative-
   path convention. Promoted as `L-131` (`CLAUDE.md` §1).
2. **Every one of this phase's five planning-amendment rounds found a
   real defect the previous round's own independent review had missed
   or introduced** (§17's "two more call sites," §17.8's declined-then-
   reopened finding, §17.9's "three vs four" undercount, §18.4's own
   premature-review-closure finding). No single review round was
   sufficient on its own; the discipline that mattered was re-reviewing
   after every correction, not trusting a clean-looking fix. The same
   pattern repeated at implementation time: both stage audits found one
   real, previously-unnoticed gap each, closed the same day rather than
   deferred — and it repeated a third time at the terminal-audit level
   itself (see "What didn't work"), where a second, independent
   re-audit found a real gap the first re-audit pass had missed.
   Promoted as `L-132` (`agent-led-development.md` §1).
3. **A scratch-copy demonstration, done rigorously (fresh HEAD pin,
   byte-identical reapplication of an already-documented mutation,
   independent reproduction by a reviewer with no access to this
   session), is genuinely strong evidence for a test's own correctness
   and a context record's own relevance — but it is still not evidence
   that the real target's real gap is closed.** Keeping these two claims
   visibly separate (plan §12.2's own instruction) mattered in practice,
   not just in principle: it is tempting to read "PASS against the
   correct scratch copy" as "the real Ledgerkit test now passes," and
   that would have been a real overclaim. Promoted as `L-133`
   (`context-quality-evaluation.md` §1).
4. **A stage-level audit's own persisted report is not optional just
   because the phase it belongs to is still open.** The mechanical
   check guaranteeing a persisted audit record only fires once a phase
   is marked `done` — it structurally cannot catch a missing
   stage-level report mid-phase. Promoted as `L-134`
   (`release-phase-auditor.md` + `agent-led-workflow.md`).

## Process-improvement feedback

- Recommend: a stage/phase audit is not complete until its own report
  is actually written to `planning/retros/`, not merely reported in the
  moment — add this as an explicit step alongside the verdict itself,
  not an afterthought (now codified as `L-134`).
- Recommend continuing the stage-level-audit-before-terminal-audit
  pattern for any future multi-stage phase — it caught stage-specific
  gaps while the relevant code was still fresh and small.
- The terminal audit's own two-pass FAIL→FAIL→PASS history suggests the
  retro-template-completeness check deserves the same explicit,
  named weight in `release-phase-auditor`'s own checklist as the
  docs-drift-audit-existence check already has — both were accepted
  too leniently on a first pass before a second, more careful pass
  caught them.

## Candidate learnings filed

`L-131` (promoted — `CLAUDE.md` §1, user-approved per §0), `L-132`
(promoted — `agent-led-development.md` §1), `L-133` (promoted —
`context-quality-evaluation.md` §1), `L-134` (promoted —
`release-phase-auditor.md` + `agent-led-workflow.md`). All four
triaged by `knowledge-curator`, landed in commit `4763fcb`.

## Where we're going

Phase 89 (incremental knowledge and documentation reconciliation) is
next — independently deliverable, not dependent on this phase's MCP
server existing (`decisions/0085` §3), since its own change-detection
trigger runs on Phase 84's API and Phase 87's doc surface directly.
Phase 90 (comparative development trials) is the gate both this phase
and Phase 89 feed: it needs Phase 83/84/87/88/89's knowledge, assurance,
MCP, documentation, and reconciliation capabilities all genuinely
operable at once. This phase confirmed the planned trajectory rather
than changing it — the MCP surface works as designed, the scratch-copy
demonstration fallback was exercised for real and held up, and nothing
found here reshapes Phase 89 or 90's own scope. The one open item this
phase leaves behind for a future, separately-authorised task: landing
the demonstration's own test (and, if ever needed, a fix — none is
needed here) in the real `~/projects/ledgerkit` checkout, closing
`CL-BFS-005`'s own honestly-still-open gap statement.

## Time / cost note

Five planning-amendment rounds across several sessions (2026-11-12
through 2026-11-15), followed by Stage 88A, Stage 88B, the Ledgerkit
demonstration, learnings triage, and a two-pass terminal audit, all
within the same multi-day window. No token-consumption metering was
available to this agent directly; no economic or productivity
comparison is claimed or implied anywhere in this phase's work — that
remains Phase 90's own, separately gated scope. The terminal audit
itself ran long relative to the stage audits (two full passes, ~650s
and ~653s of dispatch time respectively) — consistent with a terminal,
whole-phase audit genuinely re-verifying more ground than a stage audit
does, not a process inefficiency.
