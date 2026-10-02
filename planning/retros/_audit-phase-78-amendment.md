# Independent audit — Phase 78 corrective amendment of the exit decision

**Scope.** Not a standard phase-DoD audit. This audits whether the
corrective amendment to Phase 78's own exit decision (`decisions/0070`,
superseding `decisions/0069`) was reasoned and applied correctly against
its own governing prompt
(`planning/phase-78-amendment-corrective-exit-decision-prompt.md`),
checked against the exact commit `e1e56d8`.

## Verdict: **PASS**

No blocking defect found. The corrective interpretation at the heart of
this amendment (point 3 below) is, on independent re-derivation, the
textually correct reading of the governing prompt — I agree with
`decisions/0070`'s own central conclusion, not merely its paperwork.

---

## 1. Re-derived materiality finding directly from the treatment trace

Read `planning/reference-projects/ledgerkit/06-stage-d-reportspec-stage1-treatment-report.md`
("Research trace" section) directly, not through the re-evaluation's or
ADR's own summary.

Confirmed exactly as `07-cg001-corrective-reevaluation.md` and
`decisions/0070` describe:

- "Files read" items 1-12 (full/targeted reads of `api-spec.md`,
  `ROADMAP.md`, `models.py` full, `reports.py` full,
  `06-core-architecture.md` full, `python-api.md` targeted, `parser.py`
  two targeted ranges, `cli.py` full, plus greps) are all completed
  **before** any CodeCompass query appears in the "CodeCompass queries
  invoked" list.
- Queries 1 (`source-symbol ReportSpec`) and 10 (`source-symbol
  balance_from_spec`) are explicitly self-described in the trace as
  adding "no new facts" / "confirmed index currency a second time" —
  i.e., confirmatory, not discovery.
- Queries 3-4 (`query relations ReportSpec` / `balance_from_spec`) are
  the one place the agent actually tested the relationship question;
  both error `not found in context-graph.db`. The trace's own
  "Duplicated-research note" explicitly characterizes this as a
  self-corrected, immaterial cost ("redundant with each other... no
  further investigative path was blocked or re-walked because of it"),
  corrected within two calls by reading `--help`.
- The relationship answer (`ReportSpec`/`ReportSection` ↔
  `balance_from_spec`) came from the `reports.py`/`models.py` full-file
  reads (items 4-5), reads the agent needed anyway for the design
  task's other sections.

**Confirmed true as stated**: the relationship question was answered at
near-zero marginal cost from reads already required for other reasons,
and the two failing `query relations` calls cost only a few
self-corrected seconds.

## 2. Existing-vs-proposed relationship split, independently confirmed against real source

Read `/home/cormac/projects/ledgerkit/ledgerkit/reports.py` and
`models.py` directly (real repo, pinned commit
`6c90b4ca3e6c10951cb400e43db4b90bfccc5909`, confirmed clean and
unmodified — see §7 below):

- `reports.py:600`: `def balance_from_spec(journal: Journal, spec:
  ReportSpec, query: Query | None = None) -> list[ReportSectionResult]`
  — genuinely exists today and already takes a `ReportSpec` parameter.
- `models.py:198-237`: `ReportSection` (line ~198) and `ReportSpec`
  (line ~219) frozen dataclasses — genuinely exist today.
- `cli.py:23`: `COMMANDS = ("balance", "register", "accounts", "print",
  "stats", "check")` — genuinely has **no** `"report"` entry.

Confirms the one existing-to-existing link and the four proposed links
exactly as both the re-evaluation and `decisions/0070` state.

## 3. The critical interpretive question — independent answer

**Does a partial applicability finding map to "reopen" (0070's
conclusion) or to "proceed to the cost test, retain closure if
not-recurred" (the reading the `07` re-evaluation's own Part 3 actually
produced)?**

Read the governing prompt's points 3, 4, and 8 directly, independent of
either downstream document's framing.

- Point 3 names **three** applicability levels: "adequately tested...
  tested it only partially... or was inconclusive."
- Point 4's decision tree, read literally, has only **two** top-level
  branches keyed to "did not adequately exercise" vs. "exercised them"
  — it does not explicitly say where "partial" (as opposed to adequate
  or inconclusive) falls.
- Point 8 is the clause that actually resolves this gap, and it is
  explicit: it names "**Inconclusive/partially applicable**" as one
  single bundled outcome, and assigns it one disposition: "reopen the
  exit decision and plan one narrowly scoped follow-up using a genuine
  existing cross-module change whose relevant source relationships
  already exist."

This is decisive. Point 8 is the prompt's own outcome-level vocabulary,
not a looser paraphrase — it explicitly groups "partially applicable"
with "inconclusive," not with "not-recurred" or "recurred." A task whose
decision tree (point 4) must map onto one of the outcomes point 8
actually names cannot plausibly route a partial-applicability finding
into the not-recurred/recurred branches reserved for a task that
"exercised" the relevant relationships (where "exercised" naturally
reads as adequately exercised, given point 3's own three-way vocabulary
immediately above it in the same document). Treating "exercised them"
in point 4 as satisfied by a thin, 1-of-5-link exercise would collapse
point 3's and point 8's own three-way distinction back into the
two-outcome scheme the whole amendment exists to correct.

**My own independent conclusion: `decisions/0070`'s reading is correct.**
A partial applicability finding must reopen, not retain closure, even
where the thin slice actually tested reads `not-recurred`. The `07`
re-evaluation document's own Part 3 — which carves out "the thin slice
that was genuinely exercised," applies the tree only to that slice, and
recommends retaining closure "on this basis alone" (its own words) —
is the reading that conflicts with the governing prompt's explicit
point 8 text. `decisions/0070` correctly did not adopt that part of the
re-evaluation's own recommendation, while correctly preserving the
re-evaluation's materiality finding itself as real, cited evidence
(it does not discard or contradict the `07` document — it treats the
applicability-partial finding as decisive over the re-evaluation's own
downstream recommendation not to reopen, a distinction `decisions/0070`'s
own "Applying the corrected decision tree" section states explicitly:
"This is not a rejection of the re-evaluation's own materiality
finding... it is a recognition that a single, mostly-inapplicable trial
is too weak a test... to settle a whole priority track's own future").

I note the textual gap in point 4 itself (its literal two-branch tree
does not, in isolation, visibly encode point 3's three-way distinction)
as a genuine ambiguity in the governing prompt — but it is a drafting
gap in point 4 alone, fully resolved by point 8's own explicit, named
bundling. This is not a close call once point 8 is read.

## 4. Symmetric evidence rule check

`decisions/0070`'s rule: a differently-shaped, independently-derived
instance of `CG-001`'s broader hypothesis is evidence at the **track**
level (Priority A open/closed) only, "regardless of whether its own
result reads `recurred` or `not-recurred`," and "never by itself
transitions `CG-001`'s own `status` field in either direction."

This is genuinely symmetric on the axis point 5 names (positive vs.
negative evidence treated identically with respect to `CG-001`'s own
status field). It resolves the asymmetry named in `decisions/0070`'s own
§"A third flaw" (plan's Outcome 1 let positive evidence "satisfy the
recurrence bar" while the triage declined the same for negative
evidence) by applying one rule to both directions.

Checked for the specific contradiction named in the audit brief (using
this trial's result to inform the track-level reopening decision while
declaring a differently-shaped instance "incapable" of affecting
`CG-001`): this is not a contradiction, because the ADR cleanly
separates two different objects — the **track** (Priority A, which this
trial's applicability finding does inform) and the **entry**
(`CG-001`'s own `status` field, which it does not). Point 1 of the
governing prompt itself mandates exactly this kind of object-level
separation ("Separate the two questions completely"). No asymmetry
found.

## 5. No alteration of original evidence

```
git diff 3b751c8..e1e56d8 -- \
  planning/reference-projects/ledgerkit/06-stage-d-reportspec-stage1-baseline-report.md \
  planning/reference-projects/ledgerkit/06-stage-d-reportspec-stage1-treatment-report.md \
  planning/reference-projects/ledgerkit/06-stage-d-reportspec-priority-a-validation.md \
  decisions/0069-priority-a-closed-cg-001-tested-and-not-recurred.md
```
→ empty. Confirmed no alteration of any original trial evidence or the
superseded ADR.

## 6. Follow-up candidate task live-verified

Read `/home/cormac/projects/ledgerkit/ledgerkit/cli.py`, `models.py`,
`reports.py` directly:

- `cli.py:23`/`:451`: `"stats"` is in `COMMANDS` and dispatched
  (`elif args.command == "stats": s = reports.stats(...)`).
- `models.py:474`: `Journal.stats(self, query=None) -> JournalStats`
  exists and delegates to `reports.stats`.
- `reports.py:182`/`:496`: `JournalStats` dataclass and `stats(...)`
  function exist.

Confirmed: `stats` is a genuinely already-fully-wired existing feature,
not itself partially-existing the way the `ReportSpec` task was. The
follow-up sketch's own live-verification claims check out exactly.

## 7. Scope/hygiene checks

- `git diff --stat 3b751c8..e1e56d8 -- src/codecompass/` → empty.
- `git diff 3b751c8..e1e56d8 -- CLAUDE.md` → empty.
- Full changed-file list (`git diff --stat 3b751c8..e1e56d8`): 10 files
  — `CHANGELOG.md`, `decisions/0070-*.md`, `planning/CONTEXT.md`,
  `planning/ROADMAP.md`, `planning/context-gaps/inbox.md`,
  `planning/phase-78-amendment-corrective-exit-decision-prompt.md`,
  `planning/phase-78-amendment-followup-plan.md`,
  `planning/reference-projects/ledgerkit.md`,
  `planning/reference-projects/ledgerkit/07-cg001-corrective-reevaluation.md`,
  `planning/retros/phase-78-amendment-corrective-exit-decision.md` —
  matches exactly the set the governing prompt's point 7 calls for
  (new ADR, new review record, new re-evaluation, named-not-approved
  follow-up sketch, and reconciliation of `CG-001`, ROADMAP, CONTEXT,
  CHANGELOG, reference-project registration). No scope creep.
- `/home/cormac/projects/ledgerkit`: `git status --short` clean,
  `HEAD` = `6c90b4ca3e6c10951cb400e43db4b90bfccc5909` — untouched, same
  pinned commit Phase 77/78 used.
- `.venv/bin/python -m pytest -q`: **767 passed, 2 skipped** — clean.
- `.venv/bin/ruff check .`: **All checks passed!**
- `.venv/bin/python scripts/check_user_docs.py --strict`: **no
  findings**.

## 8. Internal consistency of CONTEXT.md / ROADMAP.md / CHANGELOG.md

- `planning/CONTEXT.md`: states plainly that Phase 78's exit decision
  "has been corrected by amendment," that the original rule was
  logically insufficient, and that "**Priority A is reopened, not
  closed**." No section describes Priority A as currently closed.
- `planning/ROADMAP.md`'s Priority A row: preserves the original
  closure narrative as history (§7.2 Branch A text, unedited) and
  appends, in the same cell, the full corrective-amendment narrative
  ending "**Priority A is reopened, not closed**... `CG-001` stays
  `candidate`, explicitly unaffected by this correction either way."
  Consistent, no lingering "closed" claim.
- `CHANGELOG.md`: a distinct "**Phase 78 amendment**" entry (separate
  from the original Phase 78 entry, not folded into it) states the
  same corrected conclusion. Consistent.
- `planning/context-gaps/inbox.md`'s `CG-001` entry gained a dated
  curation note stating the same correction, explicitly affirming its
  own `status` field is unaffected (still `candidate`, confirmed at
  line 1587). Consistent.
- `planning/reference-projects/ledgerkit.md` Row 06 gained a
  cross-reference to the correction and the named (not run) Row 07
  follow-up. Consistent.

No contradiction found anywhere in the reconciled documentary state.

---

## Summary

All eight checks in the audit brief pass. The one consequential,
genuinely interpretive question (point 3) was independently re-derived
from the governing prompt's own text, not inherited from either the
re-evaluation's or the ADR's own framing, and **I agree with
`decisions/0070`'s conclusion**: a partial applicability finding must
reopen Priority A, not retain its closure, per the governing prompt's
own point 8 explicitly bundling "inconclusive/partially applicable"
into one reopening outcome. No alteration of original evidence, no
scope creep, no protected-file drift, clean tests/lint/docs, and fully
reconciled planning documents.

**Verdict: PASS.**
