# Release-phase audit — Phase 51 (Re-run Ledgerkit evaluation — GATE DC)

**Auditor:** `release-phase-auditor` (independent, read-only).
**Scope inspected:** uncommitted working tree (`git diff` / `git status`)
against `planning/phase-51-rerun-ledgerkit-evaluation.md`.

## Verdict: PASS WITH NON-BLOCKING OBSERVATIONS

The phase's substantive engineering/evaluation content — the GATE DC
re-run, its before/after claims, the drift audit, and the retro — all
independently re-verify clean. The open items are (a) the
explicitly-disclosed, not-yet-run `roadmap-context-curator`
final-reconciliation step (`CHANGELOG.md`/`ROADMAP.md`/`CONTEXT.md`/plan
`Status:` header/commit hashes) — the same category of outstanding item
the Phase 49 audit (`planning/retros/_audit-phase-49.md`) also passed
with, not a defect in this phase's substance — and (b) one genuine gap:
two learnings (`L-012`, `L-015`) that were explicitly flagged, by name,
for a Phase-51 revisit decision were not touched this phase. Neither
rises to a FAIL. Numbered list of what must happen before Phase 51 is
formally `done` is below.

## What I re-ran myself (not trusted from any summary)

1. **`pytest`** (full suite): `557 passed, 2 skipped in 156.94s` —
   matches the retro's claim exactly.
2. **`ruff check .`** → `All checks passed!`
3. **`python scripts/check_user_docs.py --strict`** → `check_user_docs: no
   findings` (exit 0).
4. **Confirmed no `src/codecompass/` change this phase**: `git diff
   --stat` against the full working tree shows only 7 modified files (all
   `planning/**`) + 3 new untracked files (the phase-51 plan, retro, and
   drift-audit report). `git status --porcelain` matches this exactly —
   no `src/`, `tests/`, `docs/`, `architecture/`, `ai-docs/`, `CLAUDE.md`,
   or `decisions/` changes anywhere. **No protected-file drift** and
   **no scope creep** beyond the plan's own Files section (the
   `planning/reference-projects/README.md` registry-row update and the
   `planning/v1-redefinition/roadmap.md` `Plan:` link line are both
   conventional additions matching every prior phase's pattern, not new
   scope).
5. **Confirmed the CLI-on-`PATH` claim**: the venv's `codecompass` is an
   editable install pointing at this working tree (`pip show -f
   codecompass` → `Editable project location:
   /home/cormac/projects/codecompass`), and the working tree's HEAD is
   `cea0b1c` with a clean `src/codecompass/` (matches the plan's claimed
   CodeCompass revision exactly).
6. **Confirmed the Ledgerkit clone is genuinely on the claimed pin**:
   `git log -1` in
   `/tmp/.../scratchpad/ledgerkit` → `05218e3acced83dd8e980206668ca5ee83ebf103`.
   The only local diff there is CodeCompass's own generated `CLAUDE.md`
   routing-table block and an untracked `vendor.toml` — both pre-existing
   mechanical side effects of `codecompass` having been run in that
   clone, not phase content.
7. **Rebuilt the graph from scratch and independently re-ran both live
   queries**, not trusting the write-up:
   - Deleted the clone's `context-graph.db`, ran `codecompass --budget 0`
     (mechanical-only rebuild; the $0 cap correctly aborted the one
     AI-enrichment batch, consistent with the retro's "no AI enrichment
     spend" claim).
   - `codecompass query relations dev-docs/hledger-compatibility.md` →
     honest empty `(none)` relations table, exit 0. No "not found" error.
   - `codecompass query relations
     dev-docs/planning/core-redefinition/17-query-semantics-brief.md`
     (the brand-new file) → same honest-empty shape, exit 0.
   - `codecompass query relations
     dev-docs/planning/core-redefinition/07-query-regex.md` (Phase 46's
     original nested-path failure) → same honest-empty shape, exit 0.
   - Control case: `codecompass query relations
     dev-docs/totally-does-not-exist.md` → plain `error: '...' not found
     in context-graph.db`, exit 1 — confirms the fix didn't erase the
     genuine-not-found path.
   - Control case for `L-016`'s disambiguation: wrote a scratch
     `uncovered-test-file.md` (outside any spec-doc glob), ran `query
     relations` against it → the new disambiguated message (`exists as a
     file but was not detected as a spec/vendor doc ...`), exit 1, exactly
     as `cli.py::_relations_not_found_error`'s docstring and the phase's
     claims describe. Deleted the scratch file afterward.
8. **Queried the rebuilt `context-graph.db` directly via `sqlite3`**
   (Python's `sqlite3` module — no `codecompass query` involved), not
   taking the write-up's database claims on faith:
   - `dev-docs/hledger-compatibility.md` (id 18) and
     `dev-docs/planning/core-redefinition/17-query-semantics-brief.md`
     (id 35) both confirmed present as `kind='spec_doc'` rows.
   - `doc_relations_edges` has exactly 8 rows total, and all 8 target
     `target_doc_artifact_id=1`, which is confirmed to be
     `.claude/skills/codecompass/SKILL.md` (`kind='skill'`) — independent
     confirmation of the claim that mechanical mention-detection in this
     project graph fires only on the literal string "codecompass", which
     is why the relations tables for all three `dev-docs/` files are
     honestly empty rather than partially populated.
9. **Spot-checked source claims directly**: `_DEFAULT_GLOBS` in
   `src/codecompass/spec_docs.py` includes `"dev-docs/**/*.md"`;
   `cli.py::_relations_not_found_error` implements exactly the
   file-exists-but-undetected disambiguation described. Both match the
   phase's and the drift audit's claims.
10. **Verified the append-only claim on `00-baseline.md` and
    `01-query-semantics.md` directly** (read both files in full): the
    Phase 51 sections are appended after the original Q2/Task-01 content
    with no edits to the original text, and their own technical claims
    (line-count growth of `hledger-compatibility.md`, `07-query-regex.md`
    being byte-identical since `9c33e37`, `17-query-semantics-brief.md`'s
    single commit being `f86dd28` — postdating the original pin) all
    independently re-confirmed via `git diff`/`git show`/`git log` against
    the clone. One trivial discrepancy: the write-up says the file grew
    "238 → 273 lines"; `git show a3cf2a77:... | wc -l` gives 237 and the
    working copy gives 272 — an off-by-one, immaterial to any claim made
    on top of it (the new section and its content are exactly as
    described).
11. **Independent `docs-reconstructor` drift audit** exists at
    `planning/retros/_drift-audit-phase-51.md`, verdict `NO DRIFT`, and is
    itself substantive: it independently diffed every changed file,
    checked the append-only claim per-file with insertion/deletion
    counts, read all four current-truth doc locations' `query relations`
    prose against the actual `doc_mapping.py`/`graph.py` mechanism, and
    flagged (correctly, as a non-drift nuance rather than a finding) that
    `reference-projects/README.md`'s status cell was replaced rather than
    appended. This is genuine independent verification, not a rubber
    stamp.
12. **Retro** at `planning/retros/phase-51-rerun-ledgerkit-evaluation.md`
    checked section-by-section against `planning/retros/TEMPLATE.md`:
    every section present and substantive. "Where we are" gives real arc
    context (closing the loop Phase 47→49 opened). "What was achieved"
    and the comparison table match `findings.md`'s GATE DC section
    exactly. Crucially, the retro does **not** round the result up — it
    states plainly that the advantage ceiling (LOW) did not move and
    names the structural reason why it can't with this fix, matching the
    task's explicit ask to avoid an oversold "clean win" framing. "Where
    we're going" correctly frames the Stage D vs. Stage F/G choice as the
    user's strategic call, quoting `v1-redefinition/roadmap.md`'s own
    Phase 51 exit language verbatim and accurately (independently
    confirmed against `roadmap.md:609-613`).

## Outstanding items (must be done before Phase 51 is `done`)

1. **`CHANGELOG.md`** has no `[Unreleased]` entry for Phase 51 yet.
   Required per `CLAUDE.md` §3/§5. (Correctly, no `src/codecompass/`
   change occurred this phase, so this entry should be a measurement/
   evaluation entry, not a Fixed/Changed one — don't invent a code change
   that didn't happen.)
2. **`planning/ROADMAP.md`** line 336 still shows Phase 51 status
   `planned`, not `done`. Required per `CLAUDE.md` §2/§5.
3. **`planning/CONTEXT.md`** still describes Phase 51 as the "immediate
   next step" (e.g. lines ~1038-1048) rather than reflecting it as
   completed, and still frames Phase 49 as the most recent closeout.
   Required per `CLAUDE.md` §4/§5.
4. **The phase plan file's own `**Status:**` header**
   (`planning/phase-51-rerun-ledgerkit-evaluation.md:3`) still reads
   `planned`.
5. **The retro's own "Commit(s)" field** (`*(pending — this phase's
   closeout commit)*`) needs backfilling once committed.

None of these are defects in the phase's substantive work — they are the
disclosed `roadmap-context-curator` reconciliation step this audit was
run ahead of, identical in kind to the outstanding-items list the Phase
49 audit passed with.

## Non-blocking observations

1. **Two learnings with an explicit "revisit at Phase 51" checkpoint were
   not actioned.** `planning/reference-projects/ledgerkit/findings.md`
   §6 (Phase 47) explicitly flagged `L-012` ("flagged for a
   promote/discard decision at Phase 51's re-run if still uncorroborated
   by then") and `L-015` ("revisit at Phase 51's re-run or a second
   occurrence"). `git diff --stat -- planning/learnings/` is empty —
   neither entry was touched this phase, and the retro's "Candidate
   learnings filed: none new" is true on its own narrow terms (no *new*
   candidates arose) but doesn't address the two *existing* candidates
   that named this phase as their own review trigger. This wasn't in the
   plan file's own Scope/Files section, so it isn't scope creep to have
   skipped it, but it is a dropped commitment the project made to itself
   two phases ago. Recommend `knowledge-curator` make an explicit
   retain/discard call on both before or alongside the pending roadmap-
   context-curator reconciliation, rather than let the checkpoint pass
   silently — this is cheap (neither requires new evidence-gathering;
   `L-015`'s question, Q1/optional-deps, wasn't in this phase's re-run
   scope at all, and `L-012` is a self-test-only finding that has now
   gone 7 phases with no reference-project corroboration).
2. **Trivial line-count discrepancy** in `00-baseline.md`'s Phase 51
   section ("238 → 273 lines" vs. the actual 237 → 272) — off by one in
   both directions, doesn't affect any claim built on top of it (the new
   section's existence and content are correctly described). Not worth a
   fix on its own; mention if the file is touched again.
3. The drift audit's own noted nuance (`reference-projects/README.md`'s
   Status cell being a same-line replacement rather than a pure append)
   is correctly reasoned as not misleading and not a drift finding — I
   independently agree with that assessment on rereading the diff myself;
   no further action needed on it.

## Scope / protected-file check

- `git status --porcelain` (full repo): 7 modified files (all under
  `planning/reference-projects/**`, `planning/ROADMAP.md`,
  `planning/v1-redefinition/roadmap.md`) + 3 untracked files (the phase's
  own plan, retro, and drift-audit report). No `src/`, `tests/`, `docs/`,
  `architecture/`, `ai-docs/`, `CLAUDE.md`, or `decisions/` entries
  anywhere in the diff — independently confirmed, not assumed from the
  drift audit's own claim.
- This matches the plan file's Files section exactly, modulo the
  conventional `reference-projects/README.md` registry-row touch-up and
  the `v1-redefinition/roadmap.md` `Plan:` link line, both of which match
  the pattern used by every prior phase in that file (`grep -n "^\- \*\*Plan:\*\*"` shows the identical line added for Phases 39-44 onward).
- No `planning/phase-52-*.md` or Stage D scoping note was written — correct, since the plan said to write one only "if GATE DC's result plus other evidence justifies continuing," and the retro/findings.md both correctly frame that as an open strategic question, not a settled "yes."

## Independence notes

- All live-CLI verification above was run by me from scratch (fresh
  `context-graph.db`, `PATH` explicitly set to this repo's `.venv/bin`),
  not by re-reading the phase's own transcript.
- The `sqlite3`-level checks (item 8) were done independently of both the
  phase's own `context-evaluator` write-up and of `codecompass query`
  itself, per the plan's own "not via `codecompass query`/`check`"
  ground-truth requirement for `context-evaluator`'s method — I held the
  audit to the same standard.
