# Audit: Phase 87, Stage 87C corrective-closeout pass

**Scope**: independent audit of the four corrective commits that followed
Stage 87C's own already-`done`, already-PASS-audited completion —
`f434883..9034b98` (`9db863f`, `d52d18e`, `90e844f`, `9034b98`). This is
**not** a re-audit of Stage 87C itself; `planning/retros/
_audit-phase-87-stage-87c.md` is confirmed byte-unchanged
(`git diff f434883..HEAD -- planning/retros/_audit-phase-87-stage-87c.md`
is empty) and its own PASS verdict is not revisited here.

**Verdict: PASS** (the one gap this report's prior pass found — missing
`CHANGELOG.md` entry — is now fixed, and the fix is accurate and
adequate; everything else was already verified clean in the prior pass
and nothing in that scope has regressed).

## Re-audit of the fix (commit `a860825`)

1. **The fix exists and is additive-only.** `git diff 9034b98..a860825 --
   CHANGELOG.md` (equivalently `9034b98..HEAD`) shows a pure 36-line
   insertion at the top of the existing `[Unreleased]` / `### Added`
   block, immediately above the original (unmodified) Stage 87C entry —
   append-style, not a rewrite, consistent with this project's own
   established convention. No other line of `CHANGELOG.md` changed.

2. **Covers findings A-E accurately**, cross-checked directly against
   this report's own prior verification of each finding:
   - Finding A (seeded annotation removed via two genuine `codecompass
     knowledge apply` cycles, never a hand-edited baseline) — named
     explicitly, matches.
   - Finding B (canonical-mutation violation: `CL-ADPT-005.yaml` had
     been edited in place; fixed by restoring it verbatim with `status:
     superseded` and writing a new superseding `CL-ADPT-012.yaml` +
     `DE-ADPT-012.yaml`, with both dependent published regions' citations
     swapped) — named explicitly and accurately, including the
     "underlying fact was never reverted, only the record structure was
     corrected" nuance.
   - Finding C (corrected coverage accounting: `CONTRIBUTING.md` was
     never schema-governed; real figures 5 schema-governed documents, 4
     with compiler-published regions, 6 compiler-published regions, 1
     further Phase-81-era region) — figures match exactly what this
     report's prior pass independently re-derived.
   - Finding D (six-point limitations assessment +
     capability-vs-efficiency distinction added to the comparator
     write-up, both original verdicts unchanged) — named explicitly,
     matches.
   - Finding E (L-125-L-129 triage re-confirmed substantive, no new
     action taken) — named explicitly, matches.
   - Points to the retro's own "Addendum: Stage 87C corrective-closeout
     pass (2026-11-10)" section (confirmed present at
     `planning/retros/phase-87-stage-87c-knowledge-compiled-documentation.md:607`)
     and to this audit report, exactly as the prior pass's fix
     instruction asked for.

3. **Correctly discloses `CL-ADPT-005` is now superseded.** The new
   entry states plainly: "...fixed by restoring `CL-ADPT-005.yaml` to
   its exact original text (now `status: superseded`) and writing a new
   superseding Claim, `CL-ADPT-012.yaml`... with the two dependent
   published regions' citations swapped to it..." This closes the
   specific gap the prior pass identified — a reader of `CHANGELOG.md`
   alone can now learn `CL-ADPT-005` is superseded and `CL-ADPT-012` is
   the live record, without needing to find the retro.

4. **Explicitly states the original entry/audit are unchanged**: "Stage
   87C's own original `done` status and its original completion audit's
   PASS verdict are unchanged by this pass" — correct; confirmed the
   original entry (now at lines 48-80) is byte-identical to its
   pre-fix text, and `_audit-phase-87-stage-87c.md` remains untouched.

5. **Format matches this project's own established precedent exactly.**
   `grep -n "post-\`done\`"` across `CHANGELOG.md` confirms the same
   `**Phase N** (post-\`done\`, ... corrective pass ...)` phrasing
   pattern used for Phase 74, 76, 81 (three separate entries), 82
   (two entries), 83, 84 — the new entry's "**Phase 87, Stage 87C**
   (post-\`done\`, corrective-closeout pass, separately authorised, five
   findings from a fresh review of the already-PASS-audited stage):"
   opening follows the identical convention, substituting "Stage 87C"
   for a bare phase number consistent with this stage's own existing
   naming (matching Stage 87B's own two post-closeout entries at lines
   46 and 84 of the current file).

## Confirmation that nothing previously-audited scope regressed

`git diff 9034b98..HEAD --name-only` returns two files, not one:
`CHANGELOG.md` and
`planning/phase-87-documentation-schema-knowledge-compiled-documentation.md`.
**This is a factual correction to this dispatch's own premise** ("only
`CHANGELOG.md` changed") — an intermediate commit, `35d8ebd` ("apply
independent planning review's corrections"), sits between the audited
commit `9034b98` and the `CHANGELOG.md` fix `a860825`, and it further
amended the Stage 87D plan file.

This does **not** invalidate the present audit or require re-verifying
previously-audited scope, for two independent reasons:

- The prior pass's own point 13 already recorded that this same plan
  file (at its `9034b98` state, i.e. the Stage 87D plan's initial draft)
  was already part of what was in scope and accounted for — it is Phase
  87's *next*, not-yet-authorised stage's plan, not a retroactive edit to
  Stage 87C's corrective work.
- `35d8ebd`'s diff (read in full above) is confined to §U/§V of that plan
  file: correcting CLI subcommand counts, a parsing-convention
  description, a textual overstatement about `decisions/0085`, and
  naming a module path for a not-yet-built checker — plus appending an
  independent planning-review section whose own text states explicitly
  "implementation does not proceed from this review — a separate
  authorisation is required." It touches none of Stage 87C's audited
  artifacts (no file under `docs/concepts/`, `planning/knowledge/`,
  `decisions/`, `src/`, or the Stage 87C retro/audit files was touched).

Verdict stands as **PASS**, with this discrepancy recorded below as a
non-blocking observation rather than folded into the PASS token, per the
rule against one verdict silently answering two different questions.

## Notes, non-blocking

- The re-audit dispatch's stated premise ("confirm via `git diff
  9034b98..HEAD --name-only` that only `CHANGELOG.md` changed") does not
  hold literally — a second, unrelated file (the Stage 87D plan) was also
  touched by an intervening commit. The conclusion it was offered in
  support of (no previously-audited scope could have regressed) is still
  correct, verified independently above, not merely assumed from the
  now-corrected premise.
- Everything else from the prior pass (full regression suite 1363
  passed/2 skipped, `docs maintain`'s five-state output, all four strict
  validators, no protected-file drift, no stray knowledge/baseline edits,
  the original Stage 87C audit byte-unchanged, and all five findings A-E
  independently re-derived as factually sound) was not re-run from
  scratch in this pass, consistent with the dispatch's own instruction,
  since no commit since that verification touched any of that scope.
