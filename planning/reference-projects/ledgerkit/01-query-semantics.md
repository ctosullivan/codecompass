# Ledgerkit task 01 — hledger 1.52 query-term semantics (`acct:`/`desc:`/`date:`/`depth:`/`status:`/`not:`)

Phase 46's genuine-task run (`reference-project-protocol.md` §2.4).
Task reconfirmed live at commit `9c33e37cf8a1eec057e1fb79a83e379d9413a189`
(2026-09-13, "chore: add standing commit/push cadence; scope Stage C
Phase 1") — Ledgerkit's own `ROADMAP.md`/`CONTEXT.md` currently scope
this exact question ahead of any `ledgerkit/query/` code being written.
CodeCompass revision: `b0717ee`.

<!-- context-evaluator: add your independent section below this line,
     under its own heading. Do not edit the reference-project-tester
     section above it. -->

## reference-project-tester friction log

### Task and setup

- **Ledgerkit clone:** scratch location (session scratchpad, outside
  this repo), checked out at `9c33e37cf8a1eec057e1fb79a83e379d9413a189`.
- **CodeCompass artifacts in the clone:** `context-graph.db` and
  `vendor.toml` already rebuilt by the lead before this evaluation began
  (`codecompass --budget 0`, 0 vendors — genuinely 0 runtime deps,
  matching Phase 45's baseline). Independently re-confirmed below rather
  than taken on the lead's word.
- **Task:** determine hledger 1.52's `acct:`, `desc:`, `date:` (simple
  form), `depth:`, `status:`, and `not:` query-term semantics — real,
  current, already-scoped by Ledgerkit's own `hledger-researcher`
  workflow ("producing a semantics brief... before any `ledgerkit/query/`
  code is written", per the clone's `CONTEXT.md`), not invented for this
  evaluation.
- **This is a read-only evaluation.** No file was written into the
  Ledgerkit clone as part of this exercise — see the non-invasiveness
  check at the bottom.

### Finding 1 — CodeCompass contributed genuinely nothing (independently re-verified)

Re-ran the exact commands against the clone's own rebuilt
`context-graph.db`:

```
$ codecompass query vendors
┏━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━┳━━━━━━━━━━┓
┃ Vendor ┃ Ecosystem ┃ Version ┃ Used ┃ Enriched ┃
┡━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━╇━━━━━━━━━━┩
└────────┴───────────┴─────────┴──────┴──────────┘

$ codecompass query relations dev-docs/hledger-compatibility.md
error: 'dev-docs/hledger-compatibility.md' not found in context-graph.db

$ codecompass query relations dev-docs/planning/core-redefinition/07-query-regex.md
error: 'dev-docs/planning/core-redefinition/07-query-regex.md' not found in
context-graph.db
```

0 vendors is correct and expected (Ledgerkit genuinely has 0 runtime
deps; matches Phase 45). Both `dev-docs/` paths — including
`07-query-regex.md`, the file that actually answers this task — return
the identical "not found" error as a genuine typo would (this is
`L-016`'s point, re-confirmed here on a live task rather than a
hypothetical). Root cause is the same as `CG-002`: no `dev-docs/**/*.md`
entry in `spec_docs._DEFAULT_GLOBS`
(`src/codecompass/spec_docs.py`) — re-confirmed by inspection, not
assumed. There is no other CodeCompass mechanism to fall back to for
this task: no Skill mentions hledger or query semantics, `query
vendors` is empty, and there is no "what matters for this task"
retrieval yet. **CodeCompass's contribution to this task was a complete
zero, not merely thin** — no vendor, no doc relation, no Skill, nothing.

### Finding 2 — Ledgerkit's own prior planning work, found by one grep, fully answered the task

```
$ grep -rn "query" dev-docs/planning/core-redefinition/ | grep -i "acct:\|desc:\|date:\|depth:\|status:\|not:"
dev-docs/planning/core-redefinition/07-query-regex.md:21:| `status:` (`*`/`!`/none) | cleared/pending/unmarked | ...
```

Reading `dev-docs/planning/core-redefinition/07-query-regex.md` §7.1
directly (independently re-read in full as part of this verification,
not taken on the lead's summary) gives a complete table for all 6 terms:

| Term | Meaning | Ledgerkit today |
|---|---|---|
| `acct:REGEX` (and bare pattern) | account name match | `Query.account`, substring-or-regex — informal, not hledger's exact regex dialect |
| `not:` prefix on any term | negation | `Query.not_account` only, not general |
| `desc:REGEX` | description match | `Query.payee`, same caveat |
| `date:PERIODEXPR` | date range | `Query.date_from`/`date_to`, simple dates only — smart/period expressions explicitly "Undecided / Future" |
| `depth:N` | tree-depth cutoff | `Query.depth`, present |
| `status:` (`*`/`!`/none) | cleared/pending/unmarked | not implemented as a query term (parsed fields, not yet queryable) |
| implicit AND, explicit OR-by-repetition | boolean combination | not implemented — `Query` is a flat AND of distinct fields only |

Plus a phasing plan (§7.1's last paragraph: these 6 terms are Stage C's
initial target; `tag:`/`cur:`/smart dates are follow-on) and an
architecture diagram (§7.2) for where the query parser/evaluator will
live. This is Ledgerkit's **own** prior planning output — the lead did
not derive or infer any of it, and CodeCompass had no part in surfacing
it. Total cost to find it: one `grep -rn`, seconds, one file read.

### Finding 3 — the external hledger.org manual is a real but expensive fallback, distinct from the internal `dev-docs/` gap

The lead separately tried `WebFetch` against
`https://hledger.org/1.52/hledger.html#queries` as a hypothetical
fallback source (i.e., "what would this task look like with no
Ledgerkit-internal doc to find at all"). It correctly confirmed:

- `acct:`/`desc:` are infix, case-insensitive regex matches;
- `depth:N` semantics (top-N levels, or `REGEXP=NUM` scoped limiting);
- `status:` has `status:`/`status:!`/`status:*` forms.

But **two separate fetch attempts both failed to surface the page's
AND/OR combination logic or its `not:` prefix documentation** — the
manual page is large enough that the specific section wasn't reliably
extractable. This is a real, evidenced cost, not a hypothetical: had
`07-query-regex.md` not already existed, this task would have needed a
third fetch attempt (or a different retrieval strategy) just to get the
`not:`/combination-logic portion of the answer that Ledgerkit's own
internal doc already had in one table cell. Filed separately as `L-017`
(distinct from `CG-002`/`CG-003`: this is about the *retrieval cost* of
a live fetch, not about whether CodeCompass should model manuals at
all — that hypothesis is already named in `ledgerkit-plan.md` §1 and
scheduled for Phase 53).

### Summary of friction

| Instance | Category (per `reference-project-protocol.md` §2.4 step 3) |
|---|---|
| `query vendors` / `query relations` on both `dev-docs/` paths | context no better than direct inspection — strictly worse: it returned nothing where a `grep`+read found the complete answer |
| finding `07-query-regex.md` via `grep` | manual search done because context was missing (CodeCompass's `query relations` gave no path to this file at all) |
| `not:`/AND-OR logic missing from two WebFetch attempts | a technical dependency (external reference manual) CodeCompass cannot represent at all, compounded by the fallback channel itself being unreliable for section-specific content |

No stale or incorrect relationship was found (there was no relationship
returned at all to be stale or incorrect), and no excessive irrelevant
context was returned (the empty vendor table and "not found" errors are
minimal, not noisy) — those two friction categories from §2.4 step 3
don't apply to this task; the dominant shape here is "context missing
entirely," not "context present but wrong or excessive."

### Candidate learnings / gaps filed

- **`L-017`** (`planning/learnings/inbox.md`) — live WebFetch of a large
  external manual is an expensive, unreliable fallback for
  section-specific content; distinct from the manual-modeling question
  itself.
- **`CG-003`** (`planning/context-gaps/inbox.md`) — the external
  `hledger.org` manual has zero CodeCompass representation of any kind,
  and — unlike `CG-002` — no glob-list fix could ever cover it (it isn't
  a file in the repository at all). First concrete instance of the
  reference-doc/manual dependency-kind hypothesis
  (`conditional-generalisation.md` §2.3) actually blocking a real task.
- Not re-filing `CG-002`/`L-015`/`L-016` — this task's finding 1 is a
  direct, independently-verified recurrence of `CG-002`'s exact root
  cause and `L-016`'s exact symptom, not a new gap. Logged as
  corroborating evidence in the `context-use-log.md` entry instead of a
  duplicate filing.

### `context-use-log.md`

One entry added: `2026-09-13 · Phase 46 (Ledgerkit genuine task — query
semantics) · reference-project-tester · codecompass query vendors /
query relations against Ledgerkit's own rebuilt context-graph.db (pinned
9c33e37)` — advantage rated LOW (at the floor: zero actual contribution,
not merely marginal), not wrong or misleading.

### §2.7 non-invasiveness check

Verified in writing, live, at the end of this evaluation:

- `git status` in the Ledgerkit clone, run as part of this evaluation,
  shows: `HEAD detached at 9c33e37`; `modified: CLAUDE.md`;
  `Untracked files: vendor.toml`. Both of these **predate this
  evaluation** — they are the mechanical output of the lead's setup step
  (`codecompass --budget 0` rebuilding `context-graph.db`/`vendor.toml`
  and CodeCompass's own generated-block injection into `CLAUDE.md`,
  the `<!-- codecompass:start -->`/`<!-- codecompass:end --> ` empty
  vendor table), done *before* this evaluation began and stated as such
  in the task brief. Confirmed by timestamp: `CLAUDE.md`/`vendor.toml`/
  `context-graph.db` all carry the same `2026-09-13 06:11` mtime, all
  before this evaluation's own work started.
- **This evaluation itself wrote zero files into the Ledgerkit clone.**
  All commands run against the clone in this task were read-only
  (`codecompass query vendors`, `codecompass query relations <path>`,
  `grep`, `git status`, `git log`, `git diff`, `stat`, reading
  `07-query-regex.md`). No file inside the clone was created, edited, or
  deleted by this evaluation.
- **No CodeCompass repair was made** to force this task to succeed —
  `CG-002`'s glob-coverage gap was left exactly as found; no
  `_DEFAULT_GLOBS` edit, no `src/codecompass/` change, no workaround that
  would make `query relations` succeed on the `dev-docs/` paths. The task
  outcome (CodeCompass returns nothing; the answer comes from direct
  inspection) stands as filed.

---

## Context-quality evaluation

**Reconstructed note:** `context-evaluator` ran concurrently with
`reference-project-tester` against this same file path; its first write
was overwritten by the tester's subsequent full-file write (a `Write`
vs. `Write` race — a process gap in itself, noted below). This section
reconstructs its findings faithfully from its own returned summary,
which the lead did not alter beyond formatting.

### Setup

- **Reference project:** Ledgerkit, pinned commit
  `9c33e37cf8a1eec057e1fb79a83e379d9413a189`
- **CodeCompass revision:** `b0717ee`
- **Task:** determine hledger 1.52's `acct:`/`desc:`/`date:`(simple)/
  `depth:`/`status:`/`not:` query-term semantics — Stage C Phase 1,
  confirmed live against `ROADMAP.md`/`CONTEXT.md` (`hledger-researcher`
  producing `17-query-semantics-brief.md`, not yet written at this
  commit).
- **Context CodeCompass supplied:** nothing — `query vendors` empty,
  `query relations` "not found" for both `dev-docs/hledger-compatibility.md`
  and `dev-docs/planning/core-redefinition/07-query-regex.md`,
  independently re-run against the clone with the CodeCompass venv on
  `PATH` (not trusted from the lead's or tester's report).

### Ground truth (established by direct inspection, not via CodeCompass)

`dev-docs/planning/core-redefinition/07-query-regex.md` §7.1 already
contains a substantive, on-topic draft table for all six named query
terms plus a phasing paragraph whose term list verbatim-matches the
task's own scope — a strong prior an implementing agent would want,
though Ledgerkit's own process treats it as provisional pending
`hledger-researcher` verification, not yet final. `spec_docs.py::_DEFAULT_GLOBS`
independently traced: no `dev-docs/**/*.md` entry at any depth —
confirms `CG-002` transfers unchanged and additionally extends to
arbitrarily nested `dev-docs/**` paths, not just top-level files.

### Criteria assessment

| Criterion | Rating | Notes |
|---|---|---|
| Accuracy | weak | "Not found" is a confidently authoritative claim of non-existence for a file that is real, current, and directly load-bearing for in-progress work. |
| Relevance | n/a | Nothing relevant returned; query terminated in error. |
| Completeness | weak | Zero content for the single document that already answers the task. |
| Freshness | n/a | No content returned to assess. |
| Grounding / provenance | weak | No claim traceable — the failure is total. |
| Noise | strong | No noise, but only because nothing came back. |
| Safety / trustworthiness | weak | Reads as authoritative non-existence, not a hedge — the same shape as Phase 45's Q2. |

### Verdict: FAIL

Rated FAIL, not merely "thin but honest" (contrast Phase 45's Q1/Q3):
the "not found" error is a confidently authoritative claim about
non-existence for a real, directly load-bearing, in-progress-relevant
file — the identical failure shape as Phase 45's baseline Q2, this time
hitting live current work rather than a spot-check question. An honest
"no relations" (Phase 45's `README.md`/`docs/journal-format.md`
precedent) would have been PASS WITH GAPS; this is not that.

### Context advantage: LOW (negative)

Could a fresh Claude session get this trivially? Yes, and better —
`grep -rn "query" dev-docs/planning/core-redefinition/` finds the
answer in seconds; CodeCompass's contribution here is not merely
absent but actively worse than doing nothing, identical in kind to
Phase 45's Q2 finding.

### Material gaps / failures

- **Distinct from `CG-002`**, flagged independently here and
  corroborating `reference-project-tester`'s separately-filed `CG-003`:
  even a fixed `CG-002` would only ever surface **Ledgerkit's own prior
  prose** about hledger — CodeCompass has no mechanism at all for
  representing the external, non-package technical dependency (real
  hledger 1.52 behaviour/manual) that is the task's actual authoritative
  source. A glob fix closes the internal visibility gap; it cannot make
  CodeCompass *correct* about hledger itself. This independently
  corroborates `CG-003` (filed by `reference-project-tester` from the
  WebFetch-cost angle) from the "no representation of the dependency
  kind at all" angle — same underlying gap, two angles of evidence.

### Would this have misled the implementing agent? yes

Same reasoning as Phase 45's Q2: an agent trusting "not found" would
conclude no prior work exists on this question and either duplicate
`hledger-researcher`'s in-flight brief from scratch or fall back to
general hledger knowledge from training data, missing Ledgerkit's own
already-recorded scoping decisions (e.g. `date:` simple-only, `tag:`/
`cur:` deferred).

### Process note (not a product finding)

Two agents (`context-evaluator`, `reference-project-tester`) were
dispatched concurrently and told to write to the same shared file path,
each instructed to check the file's current state first — this was
insufficient to prevent a `Write`-vs-`Write` race, since `Write`
replaces the whole file rather than appending. `context-evaluator`'s
original content was lost and had to be reconstructed by the lead from
its returned summary. Filed as a process-improvement note in the
Phase 46 retro, not a `CG`/`L` entry (this is about the *agent-led
workflow*, not CodeCompass's product).

---

## Phase 51 re-run (2026-09-14) — GATE DC re-evaluation of Task 01

Independent re-evaluation after Phase 49's fix landed, run against
Ledgerkit's own further progress: Stage C Phase 1 (the exact work this
task originally evaluated) is now `[DONE]` — `hledger-researcher`
produced `dev-docs/planning/core-redefinition/17-query-semantics-brief.md`
(didn't exist at the original `9c33e37` pin), and a standalone, tested
`ledgerkit/query/` subpackage now implements the six in-scope terms
(not yet wired into `reports.py`/`cli.py`). This section independently
re-runs the original task's commands and adds one new check for
`17-query-semantics-brief.md`, per the phase's design decision that the
new file is a bonus check, not the primary before/after measurement.

### Setup

- **Reference project:** https://github.com/ctosullivan/ledgerkit
- **Pinned commit:** `05218e3acced83dd8e980206668ca5ee83ebf103`
- **CodeCompass revision:** `cea0b1c3f80d2600667d832f2b6f178d9fc2c8ed`
- **Task:** unchanged — hledger 1.52's `acct:`/`desc:`/`date:`/`depth:`/
  `status:`/`not:` query-term semantics.
- **Context CodeCompass supplied (independently re-run, venv on `PATH`,
  from the clone root):**

```
$ codecompass query vendors
┏━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━┳━━━━━━━━━━┓
┃ Vendor ┃ Ecosystem ┃ Version ┃ Used ┃ Enriched ┃
┡━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━╇━━━━━━━━━━┩
└────────┴───────────┴─────────┴──────┴──────────┘

$ codecompass query relations dev-docs/hledger-compatibility.md
(none) / empty Package code — same shape as the Q2 re-run above

$ codecompass query relations dev-docs/planning/core-redefinition/07-query-regex.md
(none) / empty Package code

$ codecompass query relations dev-docs/planning/core-redefinition/17-query-semantics-brief.md
(none) / empty Package code
```

All three now return the identical honest-empty shape (full Rich table
output reproduced verbatim in the Q2 re-run section above; omitted here
for brevity since the shape is byte-for-byte the same three times over).
No "not found" error for any of the three paths, including the file
that didn't exist at the original pin.

### Ground truth (re-established by direct inspection)

- All three paths are confirmed, by direct `sqlite3` query against the
  clone's own rebuilt `context-graph.db`, to be registered `doc_artifacts`
  rows (`kind='spec_doc'`, `origin='project'`):
  `dev-docs/hledger-compatibility.md`,
  `dev-docs/planning/core-redefinition/07-query-regex.md`, **and**
  `dev-docs/planning/core-redefinition/17-query-semantics-brief.md`. The
  fix generalises to a file that did not exist when `CG-002`/`L-016` were
  first filed — it isn't special-cased to the two originally-flagged
  paths.
- **`07-query-regex.md`** is unchanged since the original pin (`git diff
  9c33e37...05218e3 -- dev-docs/planning/core-redefinition/07-query-regex.md`
  produces no output) — it remains the same provisional §7.1 table
  (informal term-by-term notes, explicitly "finalised at implementation
  time," not yet source-verified).
- **`17-query-semantics-brief.md`** (new, read in full) is a rigorous,
  source-cited answer to essentially the entire task: for each of the six
  terms it cites exact `hledger` Haskell source lines
  (`hledger-lib/Hledger/Query.hs`, `Dates.hs`, `AccountName.hs`,
  `Posting.hs`), the manual section, and — where one exists — the
  upstream test-suite fixture, and it resolves the task's hardest edge
  case precisely: `not:acct:a not:acct:b` is `And [Not(Acct a), Not(Acct
  b)]` (must match neither), not `Or` — with an explicit note that this
  specific sub-case rests on source-only evidence, not an executable
  test, flagged as the top-priority fixture for `compat-differential-
  tester`. It also documents the exclusive-end-date footgun for `date:`
  ranges and the `HledgerRegex`/`PythonRegex` compatible-subset boundary
  in detail.
- **`hledger-compatibility.md`** (re-read in full; see the Q2 re-run
  section's ground truth for the whole file) has itself grown a new
  "## Query Language (Stage C)" section since the original pin,
  presenting the same six-term semantics as an implementation-status
  table and pointing at `17-query-semantics-brief.md` by name as its
  grounding — i.e. the task's answer is now duplicated, in summary form,
  in a *second* tracked doc as well.
- Root cause of the still-empty relations, re-confirmed as in the Q2
  re-run: the graph's 8 total `doc_relations_edges` rows all target the
  CodeCompass Skill by literal name-mention; none of these three files
  mention "codecompass," so `(none)` is the mechanically correct result
  for all three, independent of how much genuinely relevant content each
  contains.

### Criteria assessment

| Criterion | Rating | Notes |
|---|---|---|
| Accuracy | strong | No false claim for any of the three paths, including the newly-created one — a meaningful generalisation check the original task couldn't run. |
| Relevance | n/a | Nothing returned to judge. |
| Completeness | weak | Zero surfaced content from `17-query-semantics-brief.md`, the single document that most completely answers this task of any artifact in either evaluation round. |
| Freshness | strong | Correctly reflects the current `dev-docs/` tree, including a file that postdates the original evaluation — the strongest freshness evidence available in this re-run. |
| Grounding / provenance | adequate | The `(none)` results are honestly traceable to the mention-detection mechanism (verified directly); no false provenance anywhere, but no path to the actual content either. |
| Noise | strong | Three empty tables, no fabricated filler. |
| Safety / trustworthiness | strong | The Phase 46 failure mode (authoritative-sounding "not found" for real, load-bearing, in-progress-relevant files) is gone across all three paths, old and new alike. |

### Verdict: PASS WITH GAPS  *(moved from FAIL)*

Same structural improvement as the Q2 re-run, now confirmed across three
files including one that didn't exist at the original failing
evaluation — this is evidence the fix is a genuine mechanism change, not
a two-file patch. It is still not a clean PASS: `17-query-semantics-
brief.md` is, by a wide margin, the single most valuable artifact either
evaluation round has encountered for this task, and CodeCompass's
`query relations` surfaces literally none of it. An agent relying on
`codecompass query relations` alone learns that the file exists and is
tracked but gets zero indication of its content or why it matters.

### Context advantage: LOW  *(moved off LOW-negative, but still LOW, not positive)*

Could a fresh Claude session get this trivially, and better? **Yes.**
`grep -rn "query" dev-docs/planning/core-redefinition/` (the same
one-line search the original Task 01 evaluation used) still finds
`07-query-regex.md` in seconds, and `ROADMAP.md`/`CONTEXT.md` name
`17-query-semantics-brief.md` explicitly as Stage C Phase 1's completed
output — a diligent agent doing ordinary repository orientation would
find both files without CodeCompass's involvement at all. CodeCompass's
fixed behaviour removes the actively-harmful signal but adds no
retrieval value over that cheap path; the advantage remains at the
floor, not above it.

### Material gaps / failures

- Confirms, on a live/current task rather than the earlier spot-check,
  that even a fully-working `query relations` (tracked doc, glob
  coverage correct) has no mechanism to surface *why* a doc matters or
  what it says — only whether it name-mentions a vendor/Skill. For a
  project with 0 tracked vendors, this ceiling means `query relations`
  can never contribute positively to this class of question, independent
  of any future glob fix. This is the same underlying limitation named in
  the Q2 re-run's material-gaps entry, now corroborated by a second,
  independent artifact (`17-query-semantics-brief.md`) that a working
  discovery mechanism still could not connect to anything.
- The `query relations` empty-table output gives no explicit nudge (unlike
  `_relations_not_found_error`'s disambiguation hint for the genuinely
  unregistered case) suggesting the caller read the tracked file's actual
  content directly. This is a softer risk than Phase 46's false negative
  — an agent that understands "(none)" means "tracked but unrelated,
  not absent" is not misled — but an agent skimming past three
  consecutive empty tables without that context could plausibly conclude
  there's nothing worth reading here, when the opposite is true for
  `17-query-semantics-brief.md` specifically.

### Would this have misled the implementing agent?  no  *(changed from yes)*

The specific Phase 46 failure — "not found" read as "no prior work
exists," risking either duplicating `hledger-researcher`'s brief from
scratch or falling back to ungrounded training-data hledger knowledge —
no longer occurs for any of the three paths tested, including the new
one. An agent would correctly infer these files are known to the project
and would need to read them directly for content, which is also the
correct and cheap next step regardless of CodeCompass's involvement.

### Comparison table — before (Phase 45/46) vs. after (Phase 51)

| | Baseline Q2 (hledger-compatibility.md) | Task 01 (query-term semantics) |
|---|---|---|
| Original verdict | FAIL | FAIL |
| Original advantage | LOW (negative) | LOW (negative) |
| Original "misled?" | yes | yes |
| Re-run verdict | PASS WITH GAPS | PASS WITH GAPS |
| Re-run advantage | LOW (not negative) | LOW (not negative) |
| Re-run "misled?" | no | no |
| What moved | The false "not found" claim is gone; the doc is now correctly tracked. | Same, generalised across two pre-existing files and one brand-new file. |
| What didn't move | Zero of the doc's actual compatibility content is surfaced by `query relations`. | Zero of `17-query-semantics-brief.md`'s (or any of the three docs') actual semantic content is surfaced. |

### GATE DC assessment (this phase's exit question)

**Did measured context quality improve? Yes, materially, but only on the
dimension the fix targeted.** Both re-evaluations moved from FAIL to PASS
WITH GAPS, and from "would have misled the agent: yes" to "no" — the
specific, evidenced, high-severity failure mode (confidently-authoritative
false non-existence for real, load-bearing project docs) that drove both
original FAILs is gone, independently reconfirmed by direct inspection and
by this evaluator's own `codecompass`/`sqlite3` commands, not assumed from
the lead's report. **It did not, and structurally could not, close the
completeness gap**: `query relations`'s mechanism (literal vendor/Skill
name-mention detection) has no way to surface a spec doc's own subject
matter, so for a project with 0 tracked vendors, the advantage ceiling for
this entire class of question stays at LOW regardless of glob coverage.
Phase 49's fix should be judged a success on its own, narrow terms — it
is not evidence that Ledgerkit-style dev-docs questions are now
well-served by CodeCompass overall.
