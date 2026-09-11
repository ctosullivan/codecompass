# Drift audit — Phase 43b (two `check_user_docs.py` rules from GATE DA)

**Mode:** 1 — per-phase drift audit
**Verdict: NO DRIFT**

## What I checked

The phase's stated purpose is fixing pre-existing drift in
`architecture/overview.md` (4 passages, catalogued as items 33-36 in
`planning/v1-redefinition/architecture-split-candidates.md` §C). I
verified each corrected passage against `src/` directly, without relying
on the lead's or docs-maintainer's characterization of the fix:

1. **`git diff -- architecture/overview.md`** — read the full diff
   (3 hunks) to see exactly what prose changed, independent of any
   summary.

2. **Fix 1 (~L1903-1911, plus the deleted footgun bullet above it):**
   - `src/codecompass/sync.py::sync_vendor` docstring, read in full:
     "Deterministic and idempotent — every output file listed below is
     fully overwritten on each call, no diffing against previous output,
     and no AI call is ever made from this function." Confirms the
     deleted "Grounded description is fully regenerated ... re-purchased
     ... on every sync run" bullet was false — no AI call happens in
     `sync_vendor` at all now. Deletion is correct.
   - `src/codecompass/enrichment.py`: confirmed `_RAW_TEXT_CHAR_CAP =
     50_000` (line 49), `_DOCS_FILE_CAP = 5` (line 50), and
     `_ESTIMATED_COST_PER_BATCH_USD = 0.02` (line 45) — all three exist
     with exactly the values the corrected bullet states, in
     `enrichment.py` not the deleted `grounded_description.py`. Correct.

3. **Fix 2 (~L1947-1953, the `sync_vendor` full-overwrite bullet):**
   - Confirmed in `sync.py`: the copy/clone path (`_copy_source_snapshot`,
     lines ~376-377) does an unconditional `shutil.rmtree(dest)` +
     `shutil.copytree(source, dest, ...)` — no `depth` branch, no
     conditional gating. The rewritten text ("the entire
     `vendor/<name>/src/` snapshot is deleted and recopied each time, not
     merged, for every vendor ... no `depth`-gating survives") matches.
     The removed "(for `depth = full`)" qualifier was false. Correct.

4. **Fix 3 (~L1157-1160, the `VendorConfig.depth`/`apply_results`
   passage):**
   - `src/codecompass/core.py::VendorConfig` (lines 21-33): fields are
     exactly `name: str` and `ecosystem: Ecosystem` — no `depth` field,
     confirming the old text ("it's set to `Depth.FULL` as the closest
     existing label") was describing a field that no longer exists.
   - `src/codecompass/enrichment.py::apply_results` docstring (lines
     385-401) — its own already-correct prose ends with: "`VendorConfig`
     no longer carries a `depth` field at all (Phase 16,
     `decisions/0035`) — enrichment eligibility is purely usage-driven
     (`decisions/0031`), so there was never a real value to set here in
     the first place." The `architecture/overview.md` fix reproduces this
     near-verbatim. Correct.

5. **Reverse check — did the fix leave any other passage in
   `architecture/overview.md` now contradicting the 4 corrected ones, or
   still asserting a retired name/value as live?** Grepped the whole file
   for `Depth`/`depth`/`grounded_description`/`_ESTIMATED_COST_PER_CALL_USD`/
   `_ESTIMATED_COST_PER_BATCH_USD`/`codecompass promote` (18 hit lines
   total) and read every one in context (lines 15-59, 249-307, 291-299,
   470-494, 739-813, 1085-1170, 1770-1810, 1880-1954). Every remaining
   mention is explicitly historical — "retired", "removed in Phase 16",
   "no longer gated on", "used to", "originally implemented ... since
   Phase 15 ... is retired" — none asserts a retired name/value as
   current behaviour. No contradiction found.

6. **Other current-truth docs:** grepped `README.md`, `docs/`, `ai-docs/`
   for the same retired-name set (`grounded_description`, `Depth.FULL`,
   `depth = full`, `_ESTIMATED_COST_PER_CALL_USD`, `codecompass
   promote`) — zero hits. Nothing outside `architecture/overview.md` was
   implicated by this phase's change, and nothing there is drifted either.

7. **Ran the tools myself** rather than trusting the reported numbers:
   `python scripts/check_user_docs.py --strict` → `check_user_docs: no
   findings` (0 findings, confirming the phase's own two new checks and
   the 12 pre-existing ones all pass against this repo's real docs).
   `python -m pytest tests/test_check_user_docs.py -q` → `46 passed`
   (includes the 9 new tests for the two new checks).

## Maintainer-tooling note (out of audit scope, no drift claim)

`scripts/check_user_docs.py` and `.claude/skills/docs-sync/SKILL.md` are
maintainer tooling, not current-truth product docs, so they're outside
this audit's scope. For what it's worth: I read both and they agree with
each other and with the code — `SKILL.md` items 13-14 accurately describe
`check_no_deleted_names_as_live`'s retired-name list and
`check_generated_artifacts_match_source`'s two artifact/generator pairs
(`.claude/skills/codecompass/SKILL.md` vs `skill.render_tool_skill`,
`.claude/commands/discovery.md` vs `commands.render_discovery_command`),
matching the function definitions at `scripts/check_user_docs.py:649` and
`:701`. No disagreement found.

## Scope note

This phase touched `scripts/check_user_docs.py`, `tests/test_check_user_docs.py`,
`.claude/skills/docs-sync/SKILL.md` (maintainer tooling — out of
current-truth-doc scope per the assignment), and 4 prose passages in
`architecture/overview.md` plus a bookkeeping update to
`planning/v1-redefinition/architecture-split-candidates.md` (a planning
doc, not current-truth). No `src/codecompass/` behaviour changed. I did
not re-audit the rest of `architecture/overview.md` beyond the drift
touched/implicated by this phase's change (that's the blank-slate
reconstruction's job, a separate milestone activity) — I did, however,
read considerably more than the 4 corrected passages themselves (all 18
`depth`/`grounded_description`-related hit lines in the file) specifically
to rule out the reverse-drift case the assignment asked me to check.

## Verdict

**NO DRIFT.** All 4 corrected passages in `architecture/overview.md`
independently verified accurate against `src/codecompass/sync.py`,
`enrichment.py`, and `core.py`. No other passage in the file contradicts
them. No other current-truth doc (`README.md`, `docs/`, `ai-docs/`)
references the retired names this phase's fix touched.
