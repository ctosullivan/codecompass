# Template usability exercise 2: complete, commit-permitting run

**Corrected 2026-10-02 (Phase 80, defect 2 of the initiating prompt)**:
this exercise's own `id-reuse-001` assertion (step 3 below) overgeneralized
its causal rule to "reuse depends on whether the most-recently-deleted
task held the current maximum id." Independently reproduced as false —
`add 1,2,3 → delete 2, then 3 → add` yields id `2`, not the rule's own
predicted `3`, and id `3` is never reused in that sequence at all. The
bundle and final-tree below now include four further real commits (14–17)
correcting the assertion (`id-reuse-002.md`, superseding `id-reuse-001.md`,
which is preserved with a correction notice, not rewritten), its
downstream documentation and coding-context packet, a new snapshot
version (`id-reuse@v2.toml`), and an independent falsification review
that tried, and failed, to break the corrected claim. Full detail:
`tinytodo2-final-tree/corrections/id-reuse-reference-model.md`. The
steps below (1–13) describe the exercise's original run; they are
historically accurate for what happened at the time, not for the
assertion's own final, correct content — read step 3 together with this
notice, not in isolation.

Phase 79 sixth amendment, correction 3. Distinct from
`../template-usability-exercise/` (the original exercise, which
prohibited commits and left its snapshot `UNCOMMITTED`, and whose
`tinytodo-after-adoption/` evidence tree contains a real, now-corrected
false conceptual claim — see `../template-usability-exercise/corrections/`).
This is a fresh, separate run, in a disposable git repository that
permitted real commits throughout, completing every step the original
run could not.

## What's here

- **`tinytodo2-full-history.bundle`** — a `git bundle` containing the
  complete, real, reproducible commit history (17 commits, after the
  2026-10-02 correction added 4 more) of the exercise project,
  `tinytodo2`. Clone it directly:
  `git clone tinytodo2-full-history.bundle tinytodo2` to get a fully
  working repository with every commit, in order, independently
  re-inspectable. This is the authoritative record — real commits, not a
  narrated description of what happened.
- **`tinytodo2-final-tree/`** — the same project's final working-tree
  state (its `.git` directory stripped), for browsing without needing to
  extract the bundle first.

## What the 13 commits demonstrate, in order

1. Initial `tinytodo2` project (the known id-reuse defect still present,
   unmodified from the original exercise's own source).
2. Adopt `codecompass-template` (`70f0a12`) — following its own,
   now-fixed adoption instructions (`README.md`/`LICENSE` correctly not
   overwritten).
3. **Research** (fresh `context-researcher` dispatch, full project
   access, no isolation needed by design): writes
   `planning/knowledge/assertions/id-reuse-001.md`, independently
   discovering the real, conditional id-reuse bug by testing three
   distinct deletion scenarios (not just the one the original exercise's
   own test happened to cover).
4. **Adversarial review** (fresh `domain-skeptic` dispatch, full project
   access by design): independently re-derives all three scenarios plus
   eight further adversarial ones, confirms the assertion holds, appends
   corroborating evidence without editing the Claim.
5. **Frozen snapshot** (`id-reuse@v1.toml`) — fully committed, real
   historical git-blob hashes throughout, no `UNCOMMITTED` fields
   anywhere (unlike the original exercise, whose own no-commit
   constraint made this structurally impossible).
6. **Model-blind implementation reconstruction** (fresh
   `implementation-reconstructor` dispatch, isolated to a curated
   source+tests-only export, mechanically confirmed via its own real
   transcript to have read nothing else): independently rediscovers the
   same bug from the code alone.
7. **Alignment comparison** (fresh `domain-skeptic` dispatch, comparison
   mode): classifies `aligned`, names real gaps the assertion doesn't
   cover (CLI error handling, concurrency, etc.) as separate candidates.
8. **Documentation draft** (fresh `docs-reconstructor` dispatch, isolated
   to a snapshot-only export, mechanically confirmed clean): writes
   `docs/id-reuse.md`, preserving the claim's own conditional nature
   rather than rounding it to a flat yes/no.
9. **Coding-context packet** (`knowledge-curator`, instruction-scoped):
   `planning/knowledge/context-packet-fix-id-reuse.md`, for the bounded
   task "fix `_next_id` so ids are genuinely never reused."
10. **Independent evaluation of both outputs**: a documentation-only
    Q&A (5/5 correct) and a `context-evaluator` packet assessment (PASS,
    LOW advantage — the target function is small enough that the
    packet's own edge over cold-reading the code is modest, an honest
    result, not a packet defect).
11. **The real fix**: `_next_id` rewritten to persist a `next_id`
    high-water-mark counter instead of recomputing `max(current ids)+1`.
    Three new regression tests added, confirmed (by direct comparison
    against the pre-fix code) to actually catch the original bug.
12. **Propagation demonstration**: mechanically confirmed the fix
    surfaces as real evidence-staleness divergence against the frozen
    snapshot (historical integrity intact; the cited source/test
    evidence no longer matches what was frozen), and that this single
    signal, through the one shared snapshot, reaches and flags *both*
    the documentation and the coding-context packet as needing
    reassessment — not two separately-chased checks.
13. **Isolation evidence**: real, mechanically-derived boundary checks
    (from the two isolation-sensitive dispatches' own original
    transcripts) confirming both stayed within their assigned export
    directories, plus an honest, explicit statement that this does not
    amount to strict, mechanically-enforced isolation.

## Correction commits (14–17, added 2026-10-02)

14. **Correct `id-reuse-001`'s overgeneralized causal rule**: both
    counterexamples named in the correction request reproduced directly
    against the real, unmodified pre-fix `_next_id`, confirming the
    "most recently deleted task held the max" rule predicts the wrong
    specific id in the first sequence. A reference model tracking every
    id ever assigned (not inferring it from a single deletion) confirms
    the real mechanism: `candidate = max(live)+1`, reuse iff that
    candidate was ever assigned before. `id-reuse-001.md` gets a dated
    correction notice, original text preserved unedited below it;
    `id-reuse-002.md` records the corrected mechanism.
15. **Independent falsification review**: a fresh dispatch, given only
    `id-reuse-002`'s own corrected claim, tried to actively break it —
    its own independently-written reference model, 18 self-designed
    sequences (none from the assertion's own examples), several
    thousand operations, plus a CLI subprocess cross-check. No
    counterexample found; the claim survived.
16. **Correct downstream documentation and coding-context packet**:
    `docs/id-reuse.md` and `context-packet-fix-id-reuse.md` both
    repeated the overgeneralized rule throughout. Both corrected and
    re-cited to `id-reuse-002`; the context packet's recommended fix
    (persist a high-water-mark counter) was already correct regardless
    of the precise trigger rule and is unchanged, but its bug-mechanism
    description and regression-test rationale were corrected, and a new
    required test case was added matching the actual falsifying
    counterexample.
17. **Freeze snapshot `id-reuse@v2.toml`**, superseding `id-reuse@v1`:
    cites `id-reuse-002` and its supporting evidence (the pre-fix source/
    tests at the same unchanged historical hashes as v1, the reference-
    model reproduction, and the falsification review). Verified clean
    against the real `check_snapshot_completeness`/
    `check_snapshot_historical_integrity` checks.

## Final verdicts for this exercise

**Workflow completion**: fully achieved — every step the sixth
amendment asked for, with real commits throughout, nothing left
`UNCOMMITTED`.

**Strict clean-room isolation**: **UNMET** — honest, mechanically-verified
best-effort compliance for the two genuinely isolation-sensitive
dispatches; no mechanical enforcement boundary exists in this
environment. Full detail: `tinytodo2-final-tree/planning/knowledge/isolation/isolation-summary.md`.
