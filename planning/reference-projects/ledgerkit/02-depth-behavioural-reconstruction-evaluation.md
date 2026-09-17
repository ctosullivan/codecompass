# Context-quality evaluation — hledger `depth:`/`--depth` behavioural reconstruction (Phase 54b)

Independent evaluation of two fresh-agent runs (baseline vs. CodeCompass-
assisted treatment) on the task defined in
`planning/phase-54b-ledgerkit-behavioural-understanding-experiment.md`.
Ground truth below was re-derived independently from the pinned hledger
source, manual, and binary — **not** from either report's own claims, and
**not** from Ledgerkit's own compat-register YAML or Stage C Phase 5 retro
(per the governing instructions, those were not read).

## Ground truth, independently established

Pinned hledger clone: `/home/cormac/projects/hledger`, commit
`33fa849e7ae841968bd21c427094c4fb4a4ec38d` (tag `1.52.4`, confirmed via
`git log -1`). Pinned binary: `/home/cormac/.local/bin/hledger` reports
`1.52.4-g33fa849e7-20260910, linux-aarch64` — matches. Verified directly
by reading `MultiBalanceReport.hs`, `PostingsReport.hs`,
`Cli/Commands/Accounts.hs`, `Cli/Commands/Stats.hs`, `Data/Ledger.hs`,
`Reports/EntriesReport.hs`, `Query.hs`, the manual's `.SH Depth` and
`depth:` sections (`hledger.1:7054-7098`, `7320-7332`, `11441-11460`), and
by building a hand-written test journal and running all five commands
against the real pinned binary with and without `--depth`/`depth:`.

| Command | Actual behaviour (independently confirmed) |
|---|---|
| `balance` | **Clips/aggregates, never excludes.** `depthlessq = filterQuery (not . queryIsDepth) query` (`MultiBalanceReport.hs:211`) strips depth before postings are gathered; depth is reapplied only in `markAccountBoring` (`:315-336`, `tooDeep = d > qdepth`) and the row at the limit uses `bdincludingsubs`, absorbing everything below it. Confirmed live: `balance --depth 2` on a nested test journal produced one aggregated `assets:bank` row summing all deeper balances; `--depth 0` produced a single `...` row netting to the grand total, not an empty report. |
| `register` | **Clips/truncates, never excludes.** `beforeandduringq`'s `depthless = filterQuery (not . queryIsDepth)` (`PostingsReport.hs:172-174`) strips depth before selecting postings; `clipOrEllipsifyAccountName` (`:195`) only renames the displayed account. Confirmed live: identical line count with/without `--depth 2`, only account-name text changed. |
| `accounts` | **Clips/truncates**, with de-duplication as an incidental side effect of clipping (`Accounts.hs:64-70,103-110`, `nodepthq` then `nub . map (clipAccountName dep)`). Confirmed live: 7 distinct accounts → 5 clipped/deduped names. |
| `stats` | **The one genuine exception — a real, partial exclusion.** `Stats.hs` calls `ledgerFromJournal q j` with the **full**, depth-*included* query. `Ledger.hs:59-67`'s own doc comment states this outright ("the ledger's journal will be depth limited, but the ledger's account tree will not"); `j'' = filterJournalPostings depthq j'` drops postings (not whole transactions — `filterJournalPostings` "can leave unbalanced transactions") whose account nesting exceeds the limit. `showLedgerStats` computes `Accounts`/`depth` from postings surviving in that pruned journal (no clipping — survivors keep full names) while `Txns`/`Txns span`/`Payees-descriptions` come from the *transaction* list, which is never shrunk by posting-level filtering. Confirmed live: `Txns` unchanged (4→4) while `Accounts` dropped 7→2 at `--depth 2`. Note: `stats` never prints which accounts survived (no `--verbose` account listing either) — "nothing was renamed" for named survivors is a valid inference from source, not something directly observable in `stats`'s own output. |
| `print` | **No effect at all.** `EntriesReport.hs:42`: `filterJournalTransactions (filterQuery (not.queryIsDepth) $ _rsQuery rspec)` strips depth from the query before any filtering; `Print.hs` contains zero mentions of "depth" (grepped directly, confirmed). Confirmed live: `diff` between `print`, `print --depth 2`, and `print depth:2` output was empty in all cases. |

**Conclusion: behaviour is not uniform.** Three qualitatively distinct
treatments across the five commands: pure display-clip/aggregate
(`balance`, `register`, `accounts`), genuine partial exclusion (`stats`),
and complete inertness (`print`). This matches, independently, the shape
the phase plan's own §1.1 describes (which I did not consult).

---

# Run 1 — Baseline (no CodeCompass)

## Setup

- **Reference project:** hledger, pinned commit `33fa849e7ae841968bd21c427094c4fb4a4ec38d` (tag `1.52.4`)
- **CodeCompass revision:** n/a — this run used no CodeCompass by design (ordinary `Read`/`Grep`/`Bash`/`WebFetch` against the raw pinned clone only)
- **Task:** determine hledger's `depth:`/`--depth` behaviour for `balance`, `register`, `accounts`, `stats`, `print`, citing evidence, stating whether uniform or varies.
- **Report:** `/tmp/claude-1000/-home-cormac-projects-codecompass/0b2afcc0-cb03-48e4-8480-bf16722dc977/scratchpad/phase54b-baseline-report.md`

## Criteria assessment

Note: since no CodeCompass context was supplied, "criteria" here assess the correctness/rigour of the baseline agent's own independently-produced findings — the comparator this evaluation measures the treatment run against.

| Criterion | Rating | Notes |
|---|---|---|
| Accuracy | strong | Every citation I independently re-checked (`MultiBalanceReport.hs:206-211,315-336`, `PostingsReport.hs:172-174,232-251`, `Accounts.hs:64-66,103-110`, `EntriesReport.hs:36-42`, `Stats.hs`/`Ledger.hs`) resolved to the exact claimed content at the exact claimed lines. No fabricated relationship or misquoted source found. |
| Relevance | strong | Every source file read is a real, direct consumer of `depth:`/`Depth` for one of the five named commands; no tangent (e.g. `aregister`) was chased beyond noting it as corroborating context. |
| Completeness | strong | All five commands traced to multiple real consumers each (not stopping at `Query.hs`'s `Depth` constructor); additionally covers `register --monthly`'s aggregation-under-interval nuance, which the task didn't strictly require but strengthens the "never excludes" claim for `register`. |
| Freshness | strong | Explicitly pinned to the correct commit/tag; live binary version string checked and matches. |
| Grounding / provenance | strong | File:line citations throughout, independently verified accurate; test-journal construction and exact commands run are logged, making every "confirmed by run" claim reproducible. |
| Noise | strong | Investigation log stays scoped to the five commands; no irrelevant detours retained in the final table. |
| Safety / trustworthiness | strong | No claim presented with more confidence than the evidence supports; the one point of self-correction (`stats`) is disclosed as a revision, not hidden. |

## Verdict: PASS

Every material claim checked against the real pinned source, manual, and executable output was accurate, correctly scoped, and reproducible. The one classification choice worth flagging — labelling `stats` as "other (a genuine hybrid)" rather than a flat "excludes" — is a defensible, arguably more precise reading (it only excludes at the posting/account level, not the transaction level) rather than an error.

## Context advantage: N/A (this is the no-CodeCompass control arm)

This run is the baseline the treatment run is measured against, not itself a CodeCompass-assisted result — there is no "context CodeCompass supplied" to rate for advantage. What it does establish: a **diligent agent with only `Read`/`Grep`/`Bash`/`WebFetch` against the raw pinned clone reached a fully correct, fully complete answer**, including the `stats` exception, without any indexed/curated material. This is the yardstick the treatment run's own advantage (or lack of it) is measured against below.

## Material gaps / failures

- None found. The one plausibly-debatable point (stats classified "other" vs. "excludes") is a labelling nuance, not an inaccuracy.

## Would this have misled the implementing agent? no

---

# Run 2 — Treatment (CodeCompass-indexed reference material)

## Setup

- **Reference project:** hledger, pinned commit `33fa849e7ae841968bd21c427094c4fb4a4ec38d` (tag `1.52.4`); working copy: scratch Ledgerkit clone at `.../scratchpad/ledgerkit-scratch-54b`, pinned at commit `c6168b2630b430da7eed972e2b59ac10909b95a7` (confirmed via `git log -1` in that clone — matches "Stage C Phase 5 ... closeout", consistent with the phase plan's stated pin)
- **CodeCompass revision:** `d85ac34fe5fd8cc8ed181b9a8bc613458fc4c09b` (current `HEAD` of this repo)
- **Task:** identical to the baseline run.
- **Context CodeCompass supplied:** 19 extracted, provenance-tagged Markdown files under `dev-docs/hledger-reference/` (each with YAML frontmatter: `source_url`, `requested_ref: 1.52.4`, `resolved_commit: 33fa849e7ae8...`, exact `path`/`lines`, `content_hash`, `extracted_at`) — independently re-read a sample of these (`hledger-ledger-hs.md`, `hledger-entriesreport-hs.md`, `hledger-multibalancereport-hs-a.md`, `hledger-postingsreport-hs-a/b.md`, `hledger-accounts-hs.md`) against the real pinned source and found every excerpt byte-for-byte accurate at the claimed line range. `codecompass query relations <file>` on the 9 depth-relevant files returned `(none)`/empty for every one, as the treatment report claims — **independently re-verified** by querying the clone's own `context-graph.db` directly: all 19 `dev-docs/hledger-reference/*` rows (`doc_artifacts` ids 19-37) are registered, tracked artifacts, but appear in **zero** of the graph's 16 total `doc_relations_edges` rows (all 16 are unrelated `mentions_artifact` edges pointing at `.claude/skills/codecompass/SKILL.md` or a couple of internal `dev-docs/` cross-references, none touching the hledger-reference set). `symbols`/`source_files` tables are empty (0 rows) — confirms no Haskell code-structural indexing exists yet, as the phase plan's scope boundary states.
- **Report:** `/tmp/claude-1000/-home-cormac-projects-codecompass/0b2afcc0-cb03-48e4-8480-bf16722dc977/scratchpad/phase54b-treatment-report.md`

### Spot-check of the treatment's own CodeCompass-specific claims

- **"`query relations` returned empty for all 8 files checked"** — confirmed true (mechanically re-verified via direct graph inspection above). Minor counting slip: the treatment's own log lists 9 files in step 4 but says "8 files above" in step 5; immaterial, since the substantive claim (all indexed hledger-reference docs are relation-less) holds for the full set of 19, not just the 8 or 9 named.
- **"the indexed material was missing `Stats.hs`, forcing a fallback to the raw clone for `stats`"** — confirmed true. Listed `dev-docs/hledger-reference/` in the scratch clone directly: 19 files, none named for/derived from `Stats.hs`, and a case-insensitive `grep -rli stats` across the whole directory returns zero hits. The gap is real, not an excuse.

## Criteria assessment

| Criterion | Rating | Notes |
|---|---|---|
| Accuracy | strong | Every sampled excerpt file's frontmatter (path, line range, resolved commit, content hash) and content matched the real pinned source exactly. The mechanical `query relations` "(none)" result is an honest, correctly-computed empty result, not a false "not found" (contrast the FAIL shape in `01-query-semantics.md`, where genuinely-tracked real files returned a hard "not found" error). One agent-side (not CodeCompass-side) slip: the treatment's own synthesis table cites `EntriesReport.hs:56-62` for the print-command filter line — the real file is only 50 lines long and the actual line is 42, matching both the real source and the treatment's *own* correctly-provenanced reference file (`hledger-entriesreport-hs.md`'s frontmatter says `lines: [1, 42]`). This is a transcription error in the agent's prose, not a fault in the CodeCompass-supplied material itself, which was accurate throughout. |
| Relevance | strong | All 9 depth-relevant reference files are genuinely on-topic; the agent also correctly identified and set aside 7-8 tag-query/date-query files as noise left over from an unrelated prior task, rather than treating them as relevant. |
| Completeness | weak | Real, material gap: the curated set covers `balance`/`register`/`accounts`/`print` fully but has **no file at all** for `stats` — the one command carrying the task's single genuine exception. The agent recovered only by falling back outside the indexed material (a disclosed, permitted move per the phase plan), so completeness of *what CodeCompass's index actually offered* is the weakest link, even though the final report ends up complete. |
| Freshness | strong | Every file's frontmatter pins the same `resolved_commit: 33fa849e7ae8...` as the actual pinned clone; nothing stale found. |
| Grounding / provenance | strong (material) / one agent-side slip | The indexed material's own provenance (content hash + pinned commit + exact line range per file) is stronger, more independently checkable grounding than the baseline report's own plain in-text citations. The one line-citation drift noted above (Accuracy row) is the only blemish, and it's attributable to the agent's transcription, not the supplied context. |
| Noise | adequate | 19 files indexed, 10 of them (tag-query and date-query excerpts) irrelevant to this task and explicitly flagged as unused leftovers by the agent — correctly filtered, but real noise nonetheless in the material CodeCompass surfaced as "the reference set for this project." |
| Safety / trustworthiness | strong | No misleading claim anywhere; the empty `relations` result and the missing-`Stats.hs` gap were both disclosed candidly by the treatment agent rather than glossed over, and both were independently confirmed true, not merely plausible. |

## Verdict: PASS WITH GAPS

No incorrect or misleading claim was found in what CodeCompass actually supplied (the extracted material and the mechanical `relations` output). But a material piece of context was missing — the one file (`Stats.hs`) covering the task's single genuine exception was absent from the indexed set, forcing an out-of-index fallback exactly where the stakes were highest. That the fallback succeeded is a credit to the agent, not to CodeCompass's coverage. This is precisely the "trustworthy but incomplete" shape the verdict definition describes.

## Context advantage: LOW

Could a competent fresh Claude session have obtained equivalent context trivially through ordinary repository inspection? **Yes — and the baseline run in this same experiment proves it directly**, reaching an equally complete and accurate answer with plain `Read`/`Grep`/`Bash` against the raw clone, without hitting the `Stats.hs` gap at all. The treatment run's CodeCompass-specific mechanism (`query relations`) contributed zero relational information (mechanically confirmed via direct graph inspection: 0 of 16 edges touch any of the 19 indexed files). The one thing CodeCompass's layer added beyond a raw grep — per-excerpt content-hash/commit provenance metadata — is a genuine but narrow trustworthiness property (an agent can cryptographically confirm an excerpt hasn't drifted from its stated source), not a discovery or relational advantage; it doesn't help find what's relevant or notice what's missing, both of which the raw-clone route handled better in this instance. Net: LOW, consistent with `context-quality-evaluation.md`'s definition ("marginal on this task, common and expected for this class of question").

## Material gaps / failures

- **The single most important gap:** the indexed `dev-docs/hledger-reference/` set had no coverage of `Stats.hs`, the file that carries the task's one command-specific exception — exactly the kind of omission Phase 1's real historical mistake (stopping at one plausible piece of evidence) could have been compounded by, had the treatment agent not independently chosen to fall back to the raw clone. This should be filed as a candidate learning: curated reference-material sets built for a specific investigation are only as complete as their human/agent curator's own upfront judgment about "which files matter" — there is no CodeCompass mechanism yet (correctly, per the phase's explicit scope boundary — that's Phase 60's job) that would have caught this gap automatically.
- `query relations` contributes no positive signal for a document set with 0 tracked vendors and no `mentions_artifact` edges into this directory — the same structural ceiling already recorded in `01-query-semantics.md`'s Phase 51 re-run, now reconfirmed on a fresh material set.
- Minor: the treatment agent's own synthesis mis-cited one line range (`EntriesReport.hs:56-62` vs. the real/correctly-provenanced `1-42`) despite having the accurate citation available in its own indexed material — a downstream transcription slip, not a CodeCompass defect, but worth noting since it slightly undercuts the "grounded in indexed material" story for that one claim.

## Would this have misled the implementing agent? no

The gaps found are real but did not cause any wrong or overconfident claim to reach the final report — the agent disclosed both the empty-relations result and the missing-`Stats.hs` gap honestly and worked around them correctly. An agent trusting this report's conclusions would not be misled about hledger's actual behaviour.

---

# Comparison and execution-path-completeness ratings

## Head-to-head

| | Baseline (no CodeCompass) | Treatment (CodeCompass-indexed) |
|---|---|---|
| Verdict | PASS | PASS WITH GAPS |
| Context advantage | N/A (control arm) | LOW |
| Final answer accuracy | Fully correct, all 5 commands | Fully correct, all 5 commands |
| Hit the `stats`/`Stats.hs` gap | No — read `Stats.hs` directly as a matter of course | Yes — indexed set omitted it; recovered via disclosed fallback |
| Extra rigor beyond the minimum | Yes (`register --monthly` aggregation nuance) | Yes (noticed the manual's own "match (or display, depending on command)" line as an implicit non-uniformity hint) |
| Citation accuracy (sampled) | 100% of checked citations correct | 1 line-citation error found (agent-side, not material-side) |

**The delta is the primary finding, per this project's own established methodology (`context-quality-evaluation.md` §1):** CodeCompass's document/reference-layer contribution on this task was **not merely non-additive, it was mildly *negative* on completeness relative to the baseline's own path** — the treatment run hit a real coverage gap (missing `Stats.hs`) that the baseline, working from the raw clone with no curation step in between, never encountered at all. Both agents ended up at the identical, fully correct conclusion, but the treatment did so *despite* the indexed material, not *because* of it, for the one command that mattered most (the `stats` exception). The mechanical `query relations` layer added literally zero relational information in either direction (0-of-16 edges touch any of the 19 indexed files) — the same structural finding already on record from `01-query-semantics.md`.

This is an honest, expected, non-failure outcome for this phase, exactly as the phase plan and the governing spec anticipate: the document/reference layer being tested here is explicitly *curated by hand*, not discovered by CodeCompass, and the phase plan itself (§4.4, §8) already names "does the agent still have to fall back to raw source reading" as the open question Phase 60's Haskell adapter is meant to address. This run answers that question with a concrete "yes, and for the one command where it mattered most."

## Execution-path-completeness (Phase 54b §5 addendum)

| Run | Rating | Justification |
|---|---|---|
| Baseline | **complete** | Found and correctly characterised all five commands, explicitly revised its own initial (wrong) assumption about `stats` mid-investigation after tracing `ledgerFromJournal`/`filterJournalPostings` rather than stopping at `Stats.hs`'s call site alone, and correctly distinguished `print`'s full depth-blindness. Traced real per-command consumption in every case (`MultiBalanceReport.hs`, `PostingsReport.hs`, `Accounts.hs`, `Ledger.hs`+`Stats.hs`, `EntriesReport.hs`) rather than generalising from the `Query.hs` `Depth` constructor alone — the specific trap Stage C Phase 1 fell into. |
| Treatment | **complete** | Also found and correctly characterised all five commands, including the `stats` exception and `print`'s no-effect finding, and also traced real per-command consumption (indexed material for four commands, direct source read for `stats` after explicitly noticing the indexed material was "suggestive but not conclusive" on its own). Did not stop at the `Depth`/`matchesAccount` definition alone despite that file (`hledger-query-hs-matchesaccount.md`) being one of the indexed excerpts available to it — correctly treated it as background, not as the answer, avoiding Phase 1's specific mistake even though the indexed material would have made that shortcut easy to take. |

Neither run reproduced Stage C Phase 1's real historical mistake. Both are rated **complete**, not **partial** or **premature** — this experiment did not catch either agent taking the shortcut it was designed to test for, on this occasion.
