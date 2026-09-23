# Domain-corpus freshness reconciliation — Phase 66

**Role:** `domain-skeptic`, per `development-methodology.md`'s "Domain-corpus
freshness and reconciliation" section (`decisions/0060`).

**Scope:** the two domain-claim staleness candidates `docs-reconstructor`'s
Phase 66 drift audit (`planning/retros/_drift-audit-phase-66.md`) flagged —
line-number citation drift into `planning/v1-redefinition/roadmap.md`, and
`connector.md`'s file-list claim about `planning/CONTEXT.md`. Both traced to
Phase 66's own edits (the `L-021` status fix; the `CONTEXT.md` rewrite from
~2449 to ~126 lines). Neither candidate required new investigation into what
any concept *means* — both resolved with a direct, real check.

## Verdict: BOTH RESOLVED — citation staleness confirmed, no content or
domain-meaning drift, nothing escalated

## Candidate 1 — off-by-one line citations into `v1-redefinition/roadmap.md`

**Checked directly**, not taken on the audit's account:

- `git show cc650cd..HEAD -- planning/v1-redefinition/roadmap.md` confirms
  the `L-021` fix commit (`2e184c4`) changed a 3-line hunk to a 4-line hunk
  at the file's pre-commit lines 1030-1039 — net **+1 line**, shifting every
  subsequent line down by one.
- Compared `git show cc650cd:planning/v1-redefinition/roadmap.md` (pre-shift)
  against the current file at HEAD, line by line, around the cited content:
  - The "A specific naming collision to resolve..." paragraph (cited by
    `evidence.md:135`, `decision.md:117`, `claim.md:126` as
    `v1-redefinition/roadmap.md:1060-1086`) begins at pre-shift line 1060,
    now begins at **line 1061**; the citation's own closing bound (end of the
    enclosing Phase 57 CONDITIONAL stanza, "demonstrably required.") was at
    pre-shift line 1086, now at **line 1087**.
  - The Phase 57 bullet text ("distinguishing source-derived fact / doc
    statement / observed behaviour / test result / ADR / agent inference;
    per-claim version + evidence route + confidence state," cited by
    `provenance.md:99` and `:117` as `:1080-1086`) sits under a header at
    pre-shift line 1080, now at **line 1081**; its closing bound shifts from
    1086 to **1087**.
- **The underlying prose is byte-for-byte unchanged** in both spans — this
  is pure citation-location drift, not a content or domain-meaning change.
  Confirmed by direct text comparison, not assumed from the diffstat alone.

**Correct citations** (for whoever applies the fix — see "Not fixed here,"
below):

| File | Current (stale) citation | Correct citation |
|---|---|---|
| `evidence.md:135` | `v1-redefinition/roadmap.md:1060-1086` | `:1061-1087` |
| `decision.md:117` | `v1-redefinition/roadmap.md:1060-1086` | `:1061-1087` |
| `claim.md:126` | `v1-redefinition/roadmap.md:1060-1086` | `:1061-1087` |
| `provenance.md:99` | `v1-redefinition/roadmap.md:1080-1086` | `:1081-1087` |
| `provenance.md:117` | `v1-redefinition/roadmap.md:1080-1086` | `:1081-1087` |

The four concept pages' own internal line numbers (`evidence.md:135`,
`decision.md:117`, `claim.md:126`, `provenance.md:99,117`) were also
independently re-checked against the current file content of each concept
page — all still point at the right line within their own file. Only the
*target* line range inside `v1-redefinition/roadmap.md` is stale.

**New Evidence produced:** `OBS-SKEP-003.yaml`, `EV-SKEP-002.yaml`
(`planning/knowledge/codecompass-domain/`).

## Candidate 2 — `connector.md`'s file-list claim about `planning/CONTEXT.md`

**Checked directly**: ran `grep -ni "connector"` against each of the seven
files `connector.md`'s Definition section (lines 20-29) names as listing
"connector" purely as a research-candidate term.

```
decisions/0060-scope-plan-domain-design-implement-methodology.md:44   -> present
planning/phase-63d-domain-reconstruction.md:48,194                     -> present
planning/v1-redefinition/development-methodology.md:75                 -> present
planning/v1-redefinition/roadmap.md:1561                               -> present
planning/ROADMAP.md:352                                                 -> present
CHANGELOG.md:91,396                                                     -> present
planning/CONTEXT.md                                                     -> ABSENT (0 matches)
```

Six of the seven files still contain the word exactly as `connector.md`
describes. `planning/CONTEXT.md` no longer does, because Phase 66 (commit
`c2526e5`) deliberately rewrote it from a ~2449-line running history to
~126 lines of current-only state (per `CLAUDE.md` §4) — the old
Phase-63D-era term-enumeration paragraph that used to contain "connector"
lived in the history that was intentionally cut, not restored anywhere in
the new file.

**This is a stale citation, not a domain-meaning change.** `connector.md`'s
central, substantive claim — "'Connector' is not a real, distinct
CodeCompass concept" — rests on `EV-ADPT-004`'s independent repository-wide
grep of `src/`, `docs/`, `architecture/`, `ai-docs/`, `decisions/*.md` ADR
bodies, and `tests/`, which never depended on `planning/CONTEXT.md`'s
content at all. Only the illustrative enumeration in the Definition
section's category-1 list is now inaccurate for one of its seven named
files.

**New Evidence produced:** `OBS-SKEP-004.yaml`, `EV-SKEP-003.yaml`
(`planning/knowledge/codecompass-domain/`).

## Not fixed here — write-boundary

Both corrections are narrow, mechanical, and would not change either
page's substantive meaning if applied — but `docs/domain/` (the approved
corpus) is never edited by `domain-skeptic`, under any circumstance,
including for an obviously-correct one-line fix, per this role's own
charter and `decisions/0060`. That restriction is not waived by a
dispatch instruction proposing otherwise; it is a structural rule this
role exists to hold, not a discretionary default. The exact corrections
needed are named precisely above (table for candidate 1; the single
`planning/CONTEXT.md` list-entry removal/update for candidate 2) for
whoever holds write access to `docs/domain/` to apply.

Both new Evidence records (`EV-SKEP-002`, `EV-SKEP-003`) also state this
plainly in their own `what_it_shows` field, so the write-boundary reason
is on record alongside the finding itself, not just in this report.

`python scripts/check_knowledge_base.py` run after adding all four new
records: `no findings` (clean).

## Resolved myself vs. escalated

- **Resolved myself, with new Evidence**: both candidates. Real checks
  (`git show`, `git diff`, `grep -n`, line-by-line text comparison) run
  directly, not inferred from the audit's account. Recorded as
  `OBS-SKEP-003`, `EV-SKEP-002` (candidate 1) and `OBS-SKEP-004`,
  `EV-SKEP-003` (candidate 2) in `planning/knowledge/codecompass-domain/`.
- **Escalated to the user**: nothing. Neither candidate turned out to be a
  genuine product/domain ambiguity — both are citation-location drift with
  the underlying claims' own substance fully intact, confirmed by direct
  re-verification of the cited source text itself, not merely by re-reading
  the citing page's own prose.

## Bottom line

Both Phase 66 domain-claim staleness candidates are **citation drift, not
content or domain-meaning drift**. Four concept pages' `v1-redefinition/
roadmap.md` line-range citations are off by exactly one line each (table
above gives the corrected ranges); `connector.md`'s seven-file enumeration
is accurate for six files and stale for the seventh
(`planning/CONTEXT.md`, now absent the word). Both findings are backed by
new, checkable Evidence in `planning/knowledge/codecompass-domain/`; neither
requires a Claim revision, a Decision, or user escalation — only a
mechanical text edit to `docs/domain/concepts/evidence.md`, `decision.md`,
`claim.md`, `provenance.md`, and `connector.md`, which is outside this
role's own write boundary and is named above for the lead (or
`context-researcher`) to apply.
