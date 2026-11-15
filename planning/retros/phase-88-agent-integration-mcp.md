# Phase 88 retro: Agent Integration and MCP

## Goal

Deliver a minimal, model-neutral, read-mostly MCP server exposing
CodeCompass's existing knowledge, provenance, contextual retrieval,
change-impact analysis, documentation grounding, and controlled
verification to a real coding agent, and prove its usefulness through
a genuine Ledgerkit development task — without duplicating Phase
82/83/84's own existing logic or expanding into Phase 89/90 scope.

## Delivered vs planned

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

**Stage 88B** (not yet committed as of this retro — see "Outstanding"):
all three assurance tools, as planned. `change_impact.py`'s relocation
and `oracle.py`'s §5.3 hardening both matched the plan's own design
exactly. Independently audited PASS WITH NON-BLOCKING OBSERVATIONS (one
gap, closed same day; one process-evidence gap — no persisted Stage 88A
audit record — also closed same day).

**Demonstration** (`planning/retros/
phase-88-ledgerkit-demonstration.md`): run against disposable scratch
copies, not the real `~/projects/ledgerkit` checkout, per this task's
own cross-repository constraint — the **weaker**, not equivalent,
variant named in the plan's own §12.2 fallback. All three of its claims
(a correct new regression test; genuinely relevant, materially-used
knowledge context; the real checkout left untouched) independently
verified by a fresh reviewer. The real Ledgerkit gap itself
(`overlapping-account-patterns-no-double-count` has no passing result
against the real checkout) remains open, honestly, pending a separate
cross-repository authorisation this task was not given.

**Not delivered / deferred, matching the plan's own exclusions, never
silently dropped**: a real sandbox/container for `oracle_execute_check`
(named future work, §5.2); landing the new test in the real Ledgerkit
checkout (requires separate authorisation); Phase 89 (incremental
knowledge/documentation reconciliation) and Phase 90 (comparative
development trials) — both explicitly out of this phase's scope and
untouched.

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
   path convention.
2. **Every one of this phase's five planning-amendment rounds found a
   real defect the previous round's own independent review had missed
   or introduced** (§17's "two more call sites," §17.8's declined-then-
   reopened finding, §17.9's "three vs four" undercount, §18.4's own
   premature-review-closure finding). No single review round was
   suffilcient on its own; the discipline that mattered was re-reviewing
   after every correction, not trusting a clean-looking fix. The same
   pattern repeated at implementation time: both stage audits found one
   real, previously-unnoticed gap each, closed the same day rather than
   deferred.
3. **A scratch-copy demonstration, done rigorously (fresh HEAD pin,
   byte-identical reapplication of an already-documented mutation,
   independent reproduction by a reviewer with no access to this
   session), is genuinely strong evidence for a test's own correctness
   and a context record's own relevance — but it is still not evidence
   that the real target's real gap is closed.** Keeping these two claims
   visibly separate (plan §12.2's own instruction) mattered in practice,
   not just in principle: it is tempting to read "PASS against the
   correct scratch copy" as "the real Ledgerkit test now passes," and
   that would have been a real overclaim.

## Process-improvement feedback

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
  Recommend continuing this pattern for any future multi-stage phase.
- One real process gap this phase surfaced and fixed in itself: an
  audit's own verdict being reported without a persisted record to
  back it (Stage 88A's audit was reported accurately but not written
  to `planning/retros/` until Stage 88B's own audit flagged the
  absence). Recommend: a stage/phase audit is not complete until its
  own report is actually written to `planning/retros/`, not merely
  reported in the moment — add this as an explicit step alongside the
  verdict itself, not an afterthought.

## Outstanding at the time of this retro

- Stage 88B's own commit is staged but not yet landed (`git commit` was
  blocked by this environment's own automated commit-control classifier
  three times across this phase's work; each time the changes were left
  staged and the block reported rather than bypassed, per this
  project's own established practice). The lead/user's own `git commit`
  + `git push` remains the next manual action.
- The terminal, whole-phase Definition-of-Done audit (`CLAUDE.md` §5)
  has not yet run.
- Candidate learnings from this retro have not yet been triaged by the
  `knowledge-curator`.
- `planning/ROADMAP.md`'s Phase 88 row has not yet been flipped to
  `done` — correctly, since the above remain open.
