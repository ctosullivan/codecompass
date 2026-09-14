# Release-phase audit — Phase 52 (context edge lifecycle / agent-driven enrichment)

**Auditor:** `release-phase-auditor` (independent, read-only pass)
**Scope:** uncommitted working tree implementing
`planning/phase-52-context-edge-lifecycle.md`. Everything below was
re-derived from source/re-run directly — nothing taken on the lead's or
any other agent's summary alone.

## Verdict: PASS WITH NON-BLOCKING OBSERVATIONS

The phase's substance (code, tests, ADR, new agent, docs, drift-audit
remediation, retro, learnings/observations triage, protected-file
posture, scope discipline) is sound and independently re-verified below.
**One genuine, but already-disclosed and expected, gap remains: the
mechanical `CHANGELOG.md` / `planning/CONTEXT.md` / `planning/ROADMAP.md`
(`done` row) reconciliation has not happened yet.** Per `CLAUDE.md` §5
these are literal DoD conditions — the phase is **not yet actually
"done"** until that reconciliation lands, but this is not a defect this
audit is reporting as newly discovered; it's the pre-announced next step
(`roadmap-context-curator`), and everything this audit exists to check
independently (correctness, honesty, completeness of substance) holds.
No re-audit of substance should be needed once that bookkeeping step
completes — only confirmation it actually happened.

## What was re-run / re-verified myself

1. **`pytest`** — full suite, from a clean shell activation of `.venv`:
   `567 passed, 2 skipped in 156.61s`. Matches the retro's claimed count
   exactly (557 + 10 new).
2. **`ruff check .`** — `All checks passed!`
3. **`python scripts/check_user_docs.py --strict`** — `check_user_docs: no
   findings`.
4. **Counted new tests directly in the diff** (not trusting the retro's
   count): `git diff | grep -cE "^\+\s*def test_"` → **10**, split 4
   (`tests/test_cli.py`, `enrich apply` accept/reject paths, including
   the invalid-`relation_label` case the plan's Verification section
   specifically named) + 2 (`tests/test_relation_enrichment.py`, the
   `model` param) + 4 (`tests/test_check_user_docs.py`, the new
   `check_context_observation_fields`, including a test specifically for
   the edge-correctness/task-usefulness-collapse case). All read in full;
   assertions are real (row-level SQL checks, exit codes, message
   substrings), not just "doesn't crash."
5. **Read `src/codecompass/relation_enrichment.py` and `src/codecompass/cli.py`'s
   real diffs in full**, not the plan's description of them. `apply_results`
   gained exactly the one backward-compatible keyword-only `model`
   parameter described; every other call site untouched. `enrich apply`'s
   validate-before-write ordering, `content_hash` sourced only from the
   matched candidate (never agent-supplied), and DB-level
   `_RELATION_LABEL_CHECK_SQL` backstop all confirmed by direct code
   reading, not the ADR's or plan's claims about them.
6. **Live-reproduced the two-cycle fixture demonstration myself**, in an
   isolated copy (`/tmp/.../scratchpad/demo_repro/`, not the tracked
   fixture), with `.venv/bin` prepended to `PATH`, following
   `DEMO.md`'s own "Reproducing this demo" steps:
   - Cycle 1 `codecompass --budget 0` → mechanical `mentions_artifact`
     edges written for both `dev-docs/retros/README.md` and
     `dev-docs/planning/README.md`, status "mentioned, not yet enriched"
     — confirmed via `query relations`.
   - `codecompass enrich apply cycle1-enrichment.json --agent
     context-enrichment-agent` → `applied 2`, exit 0; confirmed via a
     direct `sqlite3`-equivalent (`python`) row read: `ai_summary`/
     `model='agent:context-enrichment-agent'`/`relation_label` all
     correct.
   - Snapshotted `doc_relation_enrichment`, re-ran `codecompass --budget
     0` (cycle 2's mechanical rebuild) — **the two cycle-1 rows came back
     byte-identical**, confirmed by diffing a full column dump before and
     after. This independently confirms `decisions/0038`'s natural-key
     persistence claim, not just the transcript's assertion of it.
   - Resubmitted the two-entry cycle-2 batch (`architecture.md` new +
     `retros/README.md` already-enriched) once: `applied 1, rejected 1`
     (the new edge legitimately accepted, the stale one correctly
     rejected on the *first* attempt in my reproduction — see Observation
     3 below for the one nuance this surfaces). Resubmitted the identical
     batch again: **`applied 0, rejected 2`, exit code 1**, both
     rejections reading "not a pending mechanical-edge candidate — the
     edge doesn't exist, or is already enriched and unchanged" —
     word-for-word the same final-state proof `DEMO.md` step 10 and the
     retro both claim. The rejection-path guarantee is real and
     reproduces.
7. **Independently re-verified both `docs-reconstructor` drift-audit
   fixes** by reading the real files, not trusting "already fixed":
   `architecture/overview.md:1467` now reads `apply_results(conn,
   results, *, model=_MODEL) -> None` (matches the real signature and is
   now internally consistent with the second quote at line 1554);
   `docs/cli-reference.md:228-229` now reads "Prints an aggregate
   accepted count, plus a per-entry reason for each rejection" — matches
   `cli.py`'s real `console.print` calls exactly (aggregate count on
   accept, per-entry bullets only on reject).
8. **Confirmed the phase's own Verification bullet 4** ("zero
   `context-graph.db` writes originate from `planning/context-observations/**`
   or `planning/context-gaps/**`") mechanically, not just by assertion:
   read `spec_docs.py::_DEFAULT_GLOBS` directly — `planning/**` is not and
   was not added to the glob set this phase, so these directories were
   never reachable by doc-scanning before or after this diff.
9. **Confirmed no protected-file drift**: `git diff -- CLAUDE.md` empty.
   No existing ADR file touched (`git diff --name-only -- decisions/`
   empty; `decisions/0054` is new/untracked only).
10. **Confirmed the fixture's own `.gitignore` actually excludes what it
    claims to** (`git add -n`/`git check-ignore -v`): `context-graph.db`,
    `vendor.toml`, `CLAUDE.md` are excluded from what would be staged;
    everything else (including `.claude/skills/codecompass/SKILL.md` and
    `.claude/commands/discovery.md`) would be committed.
11. **Confirmed `SKILL.md`/`discovery.md` are deterministic across runs**:
    diffed my reproduction's regenerated copies against the checked-in
    fixture's committed copies — byte-identical. Re-running the demo
    won't produce spurious fixture diffs.
12. **Spot-checked the `context-use-log.md` → `context-observations/`
    migration for content loss**: all 4 original dated entries
    (2026-09-10/12/12/13) map 1:1 onto `OBS-001`–`OBS-004`; every
    substantive claim (row counts, file paths, advantage ratings, "wrong
    or misleading?" verdicts) carries over verbatim, with the new
    edge-correctness/task-usefulness split added, not substituted for
    the old content.
13. **Confirmed the `.claude/agents/context-evaluator.md` "pointer
    retarget" the plan named was in fact a no-op, correctly**: grepped
    the file for `context-use-log`/`context-observations` — no match, in
    the current diff or in the file's git history — so there was nothing
    to retarget there. Not under-delivery.

## DoD checklist (`CLAUDE.md` §5)

| Condition | Status |
|---|---|
| Code implemented | **Yes** — verified by reading the real diffs |
| Plan's verification step passes | **Yes** — pytest/ruff/check_user_docs all re-run clean |
| `docs/`/`architecture/`/`decisions/` updated, accurate | **Yes** — both prior drift-audit findings independently re-verified fixed |
| Independent `docs-reconstructor` drift audit, no remaining drift | **Yes** — `planning/retros/_drift-audit-phase-52.md` exists, verdict DRIFT→2 non-blocking→both fixed, independently re-confirmed by me |
| Changelog entry (this phase only) | **Not yet** — `git diff CHANGELOG.md` empty. Expected/pending (see Verdict) |
| `planning/CONTEXT.md` reflects new state | **Not yet** — untouched. Expected/pending |
| `planning/ROADMAP.md` marks phase `done` | **Not yet** — row says `planned`. Expected/pending |
| Phase retro exists, substantive | **Yes** — `planning/retros/phase-52-context-edge-lifecycle.md`, all `TEMPLATE.md` sections filled with real content, including "Where we are"/"Where we're going" and the honest step-9 complication (not smoothed over — cross-checked against `DEMO.md` step 9 itself, matches) |
| Candidate learnings/observations triaged | **Yes** — `L-019` triaged with real re-verification against `DEMO.md`, correctly `retained` (no generalized destination exists yet, reasoning given); `OBS-005`/`OBS-006` triaged, `status: resolved` confirmed correct per the queue's own investigate-vs-record rule |
| No protected-file drift | **Yes** — confirmed |
| Changed files match plan's Files section | **Yes, with justified additions** (see Scope section) |
| `release-phase-auditor` pass | **This report** |

## Scope / Files check

Every file the plan named was touched as described. `.claude/agents/context-evaluator.md`
was correctly *not* touched (it never referenced `context-use-log.md` —
confirmed by grep and git history; nothing to retarget). Files touched
that the plan's own "Files" list didn't explicitly enumerate —
`ai-docs/README.md`, `architecture/overview.md`, `planning/learnings/inbox.md`
(the `L-019` entry), the retro, the drift-audit report, the plan file
itself — are exactly the docs-sync/process artifacts `CLAUDE.md` §2/§3/§4/§5
already obligate regardless of whether a plan's own Files section named
them; none is a `src/` change or unrelated surface. No scope creep found.

**The deliberate narrowing (doc-relation enrichment only, `relation_enrichment.py`,
not vendor/symbol-level `enrichment.py`) is disclosed, not silently
under-delivered** — named in the plan's own "Explicitly deferred" section
before implementation, and restated accurately in the retro's "Scope
delivered vs planned" section with the same reasoning (vendor enrichment
needs cloned source material + disk writes; doc-relation enrichment is
DB-only and sufficient to prove Scenario A).

**`decisions/0054` accurately describes what was actually built** — every
mechanism it claims (no schema change, `model` column distinguishes
producers, `enrich apply` enforces the boundary mechanically, a narrow
new agent rather than extending `knowledge-curator`) was independently
verified against the real `cli.py`/`relation_enrichment.py` code and the
new agent file, not just cross-checked against the ADR's own prose.

## Non-blocking observations (for the lead, not required before Phase 52 substance is called sound — but items 1 must resolve before the phase is *closed*)

1. **`CHANGELOG.md`/`planning/CONTEXT.md`/`planning/ROADMAP.md`
   (done-marking) reconciliation is outstanding.** This is a real,
   literal DoD gap right now, not a hypothetical — but it's the explicitly
   pre-announced next step (`roadmap-context-curator`), not something
   this phase skipped. Flagging so it isn't lost: Phase 52 is not "done"
   under `CLAUDE.md` §5 until this lands.
2. **Plan-vs-implementation wording mismatch, `relation_label` validation.**
   The plan text says `enrich apply` should "Validate `relation_label` via
   the existing `_normalize_relation_label`" — the shipped code instead
   does a direct `graph.RELATION_LABELS` membership check and hard-rejects
   anything outside it. This is arguably *better* for this specific path
   (`_normalize_relation_label` silently falls back to `'other'` rather
   than rejecting, which would weaken `enrich apply`'s own "hard
   rejection, not silent tolerance" design principle) — but it's a
   deviation from the plan's literal text that no doc/retro called out
   explicitly. Not a defect; worth a one-line note if anyone revisits this
   plan file later.
3. **`DEMO.md`'s "Reproducing this demo" framing slightly overstates
   what's a "hand-authored fixture input."** It says "only the
   hand-authored `.md`/`SKILL.md`/`*.json` files are [committed fixture
   inputs]," but `SKILL.md`, per `L-019`'s own honest account, was
   originally a hand-written *placeholder* that the tool itself
   mechanically overwrote on the very first sync — what's actually on
   disk now is the tool-regenerated content, not the original hand-authored
   text. Separately, `.claude/commands/discovery.md` is also a
   tool-generated file (confirmed via `commands.py`/`skill_scan.py`) that
   gets committed as if it were a fixture input, but isn't named in the
   `.gitignore` rationale alongside `CLAUDE.md`/`vendor.toml`/
   `context-graph.db` (the other three tool-regenerated files). I
   confirmed both `SKILL.md` and `discovery.md` are deterministic/stable
   across repeated runs (byte-identical in my reproduction vs. the
   checked-in copies), so this doesn't break reproducibility in practice
   — it's a documentation-precision nit in a test-fixture transcript, not
   a current-truth doc, and genuinely minor.
4. **My reproduction did not reproduce the exact step-9 anomaly** (the
   "unexpectedly accepted" resubmission) — in my run, `dev-docs/retros/README.md`'s
   stale resubmission was correctly rejected on the *first* attempt, not
   the second. This is expected, not a red flag: the checked-in fixture's
   `SKILL.md` is already past the one-time placeholder-regeneration
   transient `L-019` documents (it's already in its final, regenerated
   form), so there's no longer a hash mismatch to trigger the anomaly.
   This actually corroborates `L-019`'s own classification (a one-time
   bootstrap-order artifact of that specific live session, not a standing
   defect) rather than undermining it — but it does mean a future reader
   literally re-running "Reproducing this demo" will see the *correct*
   behavior throughout, not the documented step-9 hiccup, which is fine
   but could confuse someone expecting to reproduce that specific
   complication.
5. **`enrich apply` has no defensive handling for a non-dict entry** in
   the JSON list (e.g. `["not-a-dict"]` would raise an unhandled
   `AttributeError` from `.get()` rather than a clean CLI error). Outside
   the plan's own Verification scope (which named three specific
   accept/reject scenarios, not malformed-shape input), and a narrow edge
   case given the command's documented contract assumes well-formed
   entries — flagged for future hardening, not blocking.
6. **`.claude/agents/knowledge-curator.md`'s triage cadence** was
   generalized from "Phases 47 and 55" to "milestone consolidations" in
   this diff — a reasonable clarification, not called out explicitly in
   the plan's "extend to triage `context-observations/`" scope line, but
   harmless and consistent with the rest of the file's intent.

## Files most relevant to this audit

- `/home/cormac/projects/codecompass/planning/phase-52-context-edge-lifecycle.md`
- `/home/cormac/projects/codecompass/decisions/0054-agent-driven-enrichment-is-a-second-non-authoritative-producer.md`
- `/home/cormac/projects/codecompass/src/codecompass/cli.py` (`enrich_apply`, ~line 1104)
- `/home/cormac/projects/codecompass/src/codecompass/relation_enrichment.py` (`apply_results`)
- `/home/cormac/projects/codecompass/.claude/agents/context-enrichment-agent.md`
- `/home/cormac/projects/codecompass/.claude/agents/knowledge-curator.md`
- `/home/cormac/projects/codecompass/tests/fixtures/ledgerkit_lifecycle_demo/DEMO.md`
- `/home/cormac/projects/codecompass/planning/context-observations/{README,TEMPLATE,inbox}.md`
- `/home/cormac/projects/codecompass/planning/context-use-log.md`
- `/home/cormac/projects/codecompass/planning/learnings/inbox.md` (`L-019`)
- `/home/cormac/projects/codecompass/planning/retros/phase-52-context-edge-lifecycle.md`
- `/home/cormac/projects/codecompass/planning/retros/_drift-audit-phase-52.md`
- `/home/cormac/projects/codecompass/architecture/overview.md`, `docs/cli-reference.md`, `ai-docs/README.md`
