# Template usability exercise 2: complete, commit-permitting run

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
  complete, real, reproducible commit history (13 commits) of the
  exercise project, `tinytodo2`. Clone it directly:
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

## Final verdicts for this exercise

**Workflow completion**: fully achieved — every step the sixth
amendment asked for, with real commits throughout, nothing left
`UNCOMMITTED`.

**Strict clean-room isolation**: **UNMET** — honest, mechanically-verified
best-effort compliance for the two genuinely isolation-sensitive
dispatches; no mechanical enforcement boundary exists in this
environment. Full detail: `tinytodo2-final-tree/planning/knowledge/isolation/isolation-summary.md`.
