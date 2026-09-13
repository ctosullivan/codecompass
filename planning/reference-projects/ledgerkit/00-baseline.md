# Context-quality evaluation — Ledgerkit baseline (3 questions)

Phase 45's baseline datapoint. Three questions evaluated independently
against the pinned Ledgerkit clone; each is a standalone instance of
`TEMPLATE-evaluation.md`'s structure. Ground truth for all three was
established by reading the Ledgerkit clone directly (`pyproject.toml`,
`dev-docs/hledger-compatibility.md`, `ROADMAP.md`, `CONTEXT.md`) and, for
root-cause confirmation, this repo's own `src/codecompass/` source
(`spec_docs.py`, `discovery.py`, `cli.py`) — **no `codecompass query` /
`codecompass check` / `/discovery` command was run** as part of this
evaluation.

---

# Q1 — Runtime dependencies

## Setup

- **Reference project:** https://github.com/ctosullivan/ledgerkit
- **Pinned commit:** `a3cf2a77ca0075fabd4f7153d2a19f45c6e69b97`
- **CodeCompass revision:** `6c3f34e` (this repo's HEAD at baseline time)
- **Task:** "What does Ledgerkit depend on (runtime dependencies)?" — the
  kind of question a development agent asks before touching packaging,
  auditing the dependency surface, or reasoning about install footprint.
- **Context CodeCompass supplied:** `codecompass query vendors` → an
  empty table (0 vendors tracked). Bare `codecompass` auto-discovery
  found 0 newly-discovered vendors from `pyproject.toml`.

## Ground truth (read directly from the clone)

`pyproject.toml`:
```
[project]
...
dependencies = []
...
[project.optional-dependencies]
pandas = ["pandas>=1.3"]
```
`dependencies` is a literal empty list — Ledgerkit has **zero required
runtime dependencies**. It has exactly one **optional** runtime
dependency, `pandas>=1.3`, declared as an extra (`pip install
ledgerkit[pandas]`). This isn't a dead/aspirational entry: it gates a
real, tested, documented feature — `ledgerkit/_pandas_compat.py` imports
`pandas` behind a try/except, `tests/test_dataframe.py` exercises it, and
`README.md` / `docs/python-api.md` / `docs/getting-started.md` all
document `pip install ledgerkit[pandas]` for DataFrame export.

Confirmed against CodeCompass's own source that this is a **documented,
deliberate** scope limitation, not a bug: `discover_python()`
(`src/codecompass/discovery.py`) reads only
`data["project"]["dependencies"]` and explicitly notes
`[project.optional-dependencies]` is not scanned.

## Criteria assessment

| Criterion | Rating | Notes |
|---|---|---|
| Accuracy | strong | "0 vendors" is literally correct for the strict `dependencies` array — no false claim made. |
| Relevance | strong | Directly answers "what does it depend on." |
| Completeness | weak | Silently omits the one real optional runtime dependency (`pandas`) and gives no indication that optional-dependencies aren't scanned at all — a materially different picture from "this project has no runtime dependency surface whatsoever." |
| Freshness | n/a | `pyproject.toml` unchanged; no staleness risk here. |
| Grounding / provenance | adequate | The "0 vendors" figure is mechanically traceable to the vendors table / `discover_python()`, but the CLI surfaces no caveat about the optional-dependencies exclusion — that context exists only in source-code comments and a planning doc, invisible to whoever runs the command. |
| Noise | strong | An empty table for an empty result is appropriately minimal. |
| Safety / trustworthiness | adequate | Not misleading in the sense of asserting something false, but an agent that treats "0 vendors" as "no dependency surface to worry about" would be wrong about the pandas extra, and CodeCompass gives no signal to catch that. |

## Verdict: PASS WITH GAPS

No incorrect or misleading claim was made — "0 tracked vendors" is true
of the graph and true of the strict `dependencies` array. But the
optional `pandas` extra is a real, tested, documented dependency that a
question phrased as "what does Ledgerkit depend on" would reasonably
expect to surface, and CodeCompass's answer (both the query and the
auto-discovery message) gives zero indication it exists or that
optional-dependencies are out of scope for discovery. That's a material,
if narrow, completeness gap on an otherwise-honest answer.

## Context advantage: LOW

Could a fresh Claude session get equivalent (or better) context
trivially? **Yes — and it would get more.** `pyproject.toml` is a single
53-line file; a fresh agent reading it sees `dependencies = []` **and**
the adjacent `[project.optional-dependencies]` block in the same glance,
at effectively zero cost. CodeCompass's answer here isn't just "no
advantage over a cheap search" — for this specific question, a cheap
direct read of the one obvious file is strictly more complete than what
CodeCompass returned.

## Material gaps / failures

- CodeCompass's vendor-discovery model has no representation of
  `[project.optional-dependencies]` at all, and neither `codecompass
  query vendors` nor the bare-discovery summary emits any caveat that
  optional dependencies exist but are unscanned — an agent gets no signal
  to go check `pyproject.toml` itself. (Already the subject of a
  documented, deliberate scope decision per
  `planning/phase-4-sync-index-init.md`; this is evidence the silence at
  the CLI layer, not the scope decision itself, is the gap worth
  revisiting.)

## Would this have misled the implementing agent? partially

Only if the task in question touches the optional extra (a dependency
audit, a packaging change, anything involving DataFrame export) — for a
question strictly about *required* runtime deps, "0 vendors" is
sufficient and correct. For the broader, more natural reading of "what
does this project depend on," relying on this answer alone would miss a
real, shipped, tested dependency.

---

# Q2 — What governs Ledgerkit's hledger-1.52 journal-format compatibility

## Setup

- **Reference project:** https://github.com/ctosullivan/ledgerkit
- **Pinned commit:** `a3cf2a77ca0075fabd4f7153d2a19f45c6e69b97`
- **CodeCompass revision:** `6c3f34e`
- **Task:** "What governs Ledgerkit's hledger-1.52 journal-format
  compatibility?" — a development agent asking this before touching the
  parser, adding a directive, or reasoning about what a `ParseError`
  should do needs to find Ledgerkit's own compatibility contract, not
  invent one from general hledger knowledge.
- **Context CodeCompass supplied:** `codecompass query relations
  dev-docs/hledger-compatibility.md` → `error: 'dev-docs/hledger-
  compatibility.md' not found in context-graph.db`.

## Ground truth (read directly from the clone)

`dev-docs/hledger-compatibility.md` **exists, is current, and is exactly
the governing document** the question asks about. It is a 238-line
narrative spec: supported file formats (`.journal`/`.ledger` only, not
hledger's `.j`/`.hledger` aliases), the transaction-block grammar,
per-feature In Scope / Out of Scope / Undecided tables (dates, amounts,
comments, all nine directives with `[IMPLEMENTED]` tags, validation
checks, balance-assertion syntax), and multiple explicit, deliberate
**deviations from hledger 1.52** called out inline (e.g. alias rules do
NOT propagate into `include`d files, unlike real hledger; Python's
`glob.glob()` dot-file inclusion differs from hledger's exclusion). It
references `https://hledger.org/1.52/hledger.html` by section throughout.
`ROADMAP.md` names this file as a Milestone-0 foundational artifact and
lists "`dev-docs/hledger-compatibility.md` updated" as an explicit exit
criterion for Milestones 1 and 4. A machine-readable counterpart lives in
`dev-docs/compat-register/` (25 `status: proposed` entries), but that
register's own README states the narrative doc "remains the primary
reference until every relevant row has a `status: final` register entry
to link instead" — i.e. at this pinned commit, this file **is** the
authoritative answer to the question.

**Root cause, confirmed by reading `src/codecompass/spec_docs.py`
directly:** `_DEFAULT_GLOBS` contains `docs/**/*.md`,
`architecture/**/*.md`, `decisions/**/*.md`, `spec/**/*.md`,
`specs/**/*.md`, `rfcs/**/*.md`, `ai-docs/**/*.md`, and a few root-level
names — there is no `dev-docs/**/*.md` entry. `discover_spec_docs()`
never even visits Ledgerkit's `dev-docs/` tree, so the file was never
registered as a `spec_doc` row at all.

**Root cause of the specific error message, confirmed by reading
`src/codecompass/cli.py`:** `query relations` calls `_resolve_relations`;
when a name isn't a known doc artifact/vendor/Skill at all, that
function returns `None` and the CLI raises `_not_found_error` — a
distinct code path from "known doc artifact, zero relations" (which
prints an empty `Relation` table, not an error). This confirms the task
framing precisely: this is categorically different from an honest
"found, but nothing to relate" result (which is what a `docs/**/*.md`
file with no vendor/Skill mentions would correctly get) — it is "this
path does not exist in our model of the project" for a file that
demonstrably does, and demonstrably is the single most relevant document
in the repository for this exact question.

## Criteria assessment

| Criterion | Rating | Notes |
|---|---|---|
| Accuracy | weak | Technically true of the tool's internal state ("not in context-graph.db"), but the practical claim it makes to the asker — "no such artifact is known here" — is false: the file exists, is current, and is the project's own designated compatibility-governance document. |
| Relevance | n/a | Nothing relevant was returned; the query terminated in an error before any content could be judged. |
| Completeness | weak | Zero content returned for the single most important governance artifact bearing on the question. |
| Freshness | n/a | No content returned to assess for staleness. |
| Grounding / provenance | weak | No claim can be traced to any source because none was surfaced — the failure is total, not partial. |
| Noise | strong | No noise, but only because nothing came back at all. |
| Safety / trustworthiness | weak | An "not found" error reads as an authoritative statement about what exists in the project, not a hedge — a trusting agent has no reason to suspect the file is real and simply unindexed. |

## Verdict: FAIL

An incorrect/misleading result outranks an incomplete one (governing
rule 3). This is not an honest "no relations found" for a doc CodeCompass
knows about — it is a confident-sounding "not found" for a file that is
real, current, and is precisely the artifact the question is asking
about. Per the task's own framing (and confirmed independently by
reading the source): this is a materially more serious failure mode than
a thin/empty result, because it actively risks convincing the asker that
no such governance document exists.

## Context advantage: LOW (and actually negative here)

Could a fresh Claude session get this trivially? **Yes, more easily than
by trusting CodeCompass.** `ls dev-docs/` or a `grep -ril hledger
dev-docs/` surfaces `dev-docs/hledger-compatibility.md` in seconds, and
its filename alone makes its purpose unambiguous. CodeCompass's
contribution to this question isn't merely "no advantage over a cheap
search" — it is actively worse than doing nothing, since it supplies a
confident-sounding negative that a cheap direct search would immediately
contradict.

## Material gaps / failures

- `src/codecompass/spec_docs.py::_DEFAULT_GLOBS` has no `dev-docs/**/*.md`
  entry, so any project (Ledgerkit or otherwise) that names its
  developer-facing spec/architecture docs `dev-docs/` rather than `docs/`
  or `architecture/` is invisible to `query relations` (and to spec-doc
  discovery generally) with no warning that this has happened. This is
  the same category of glob-coverage gap Phase 37 already found and fixed
  for `ai-docs/`, this time surfaced by an external reference project.
  Already filed as `planning/context-gaps/CG-002` per the registration
  record (`planning/reference-projects/ledgerkit.md`).
- `query relations`'s "not found" error is indistinguishable, from the
  caller's point of view, between "this path was never scanned as a doc
  artifact" (a discovery-glob gap, silently wrong) and "this path is
  simply misspelled" (a genuine user error) — both produce the identical
  message, which makes the former look like the latter and gives no
  signal to check the glob coverage.

## Would this have misled the implementing agent? yes

An agent asking this question and receiving "not found" has every reason
to conclude Ledgerkit has no documented hledger-compatibility contract,
and would either (a) proceed to modify parser/directive behaviour without
consulting the project's own deliberate, non-obvious deviations from real
hledger (e.g. the alias/`include` non-propagation, the dot-file glob
divergence, `.j`/`.hledger` rejection), or (b) fall back to general
hledger knowledge from training data that directly contradicts
Ledgerkit's documented choices. Either path produces work that
contradicts the project's own stated compatibility contract.

---

## Phase 51 re-run (2026-09-14) — GATE DC re-evaluation of Q2

Independent re-evaluation of this same question after Phase 49's fix
(`dev-docs/**/*.md` glob coverage + `query relations`'s not-found
disambiguation) landed. Ground truth re-established by reading the
Ledgerkit clone directly at the commit below; CodeCompass's own source
(`src/codecompass/spec_docs.py`, `src/codecompass/cli.py`) re-inspected
directly; the `context-graph.db` produced by the fixed code was also
queried directly via `sqlite3` (not through `codecompass query`) to
confirm the doc-artifact row exists, independent of what the CLI prints.

### Setup

- **Reference project:** https://github.com/ctosullivan/ledgerkit
- **Pinned commit:** `05218e3acced83dd8e980206668ca5ee83ebf103`
  (2026-09-13, "docs: confirm and pin the hledger reference binary")
- **CodeCompass revision:** `cea0b1c3f80d2600667d832f2b6f178d9fc2c8ed`
  (includes Phase 49's fix)
- **Task:** unchanged — "What governs Ledgerkit's hledger-1.52
  journal-format compatibility?"
- **Context CodeCompass supplied (independently re-run, venv on `PATH`,
  from the clone root):**

```
$ codecompass query relations dev-docs/hledger-compatibility.md
┏━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━┓
┃ Relation ┃ Other ┃ Heading ┃ Label ┃ AI summary ┃
┡━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━┩
│ (none)   │       │         │       │            │
└──────────┴───────┴─────────┴───────┴────────────┘
Package code
┏━━━━━━━━┳━━━━━━━━┳━━━━━━┳━━━━━━┳━━━━━━━━━┳━━━━━┓
┃ Vendor ┃ Symbol ┃ File ┃ Line ┃ Heading ┃ Via ┃
┡━━━━━━━━╇━━━━━━━━╇━━━━━━╇━━━━━━╇━━━━━━━━━╇━━━━━┩
└────────┴────────┴──────┴──────┴─────────┴─────┘
```

No error, no "not found" — a structurally different result from Phase
45's `error: 'dev-docs/hledger-compatibility.md' not found in
context-graph.db`.

### Ground truth (re-established by direct inspection)

- `dev-docs/hledger-compatibility.md` still exists and is still current —
  it has in fact **grown** since Phase 45's pin (238 → 273 lines): `git
  diff a3cf2a77...05218e3 -- dev-docs/hledger-compatibility.md` shows a
  new "## Query Language (Stage C)" section (lines 199–231) added,
  documenting `acct:`/`desc:`/`date:`/`depth:`/`status:`/`not:` semantics
  and cross-referencing `17-query-semantics-brief.md` as the
  hledger-source-verified grounding for each row. It remains exactly the
  file the question asks about.
- Direct `sqlite3` query against the clone's own rebuilt
  `context-graph.db` confirms the file **is** now a registered
  `doc_artifacts` row: `('dev-docs/hledger-compatibility.md', 'spec_doc',
  'project')`. This is the mechanical confirmation that the empty
  `(none)` result above is an honest "tracked, zero mechanical relations
  found" — not a masked non-existence claim.
- Root cause of the fix, re-confirmed by reading
  `src/codecompass/spec_docs.py` directly: `_DEFAULT_GLOBS` now includes
  `"dev-docs/**/*.md"` (added by Phase 49, commit `780e97b`), where
  Phase 45's pin had no such entry.
- Root cause of *why* the table is still empty despite the doc now being
  tracked, re-confirmed by reading `src/codecompass/doc_mapping.py`
  directly and by querying `doc_relations_edges` in the rebuilt graph:
  the whole project graph contains only **8** `doc_relations_edges` rows
  total, and every one of them targets `doc_artifacts` row id 1
  (`.claude/skills/codecompass/SKILL.md`, name `codecompass`) — i.e.
  mechanical mention-detection in this project fires only where a doc
  happens to say the literal string "codecompass" by name. Nothing in
  `hledger-compatibility.md` mentions "codecompass" or any tracked
  vendor (Ledgerkit genuinely has 0 runtime dependencies), so an empty
  relations table is the mechanically correct output — the mechanism
  was never capable of surfacing this doc's actual hledger-compatibility
  content, fixed glob or not.

### Criteria assessment

| Criterion | Rating | Notes |
|---|---|---|
| Accuracy | strong | The empty table is literally and practically correct: the file is tracked, and it mechanically mentions no vendor/Skill. No false claim of any kind. |
| Relevance | n/a | Nothing was returned to judge for relevance — the query engine correctly had nothing mechanical to report. |
| Completeness | weak | Zero of the file's actual compatibility-governance content (the deviations from real hledger, the new Query Language section) is surfaced — the same completeness gap as before, just no longer disguised as non-existence. |
| Freshness | strong | The graph correctly reflects the file's current, grown state as a tracked artifact at the pinned commit — no staleness. |
| Grounding / provenance | adequate | The "(none)" result is honestly traceable to the mechanical mention-detection model (verified directly against `doc_relations_edges`); there is no false provenance claim, but also no path from this result to the file's actual content. |
| Noise | strong | Minimal — an empty table stays empty, no fabricated filler. |
| Safety / trustworthiness | strong | This is the material change from Phase 45: an empty, present-tense result reads as "tracked, nothing mechanically related," not as "this doesn't exist." Confirmed by direct inspection that the doc-artifact row is real. |

### Verdict: PASS WITH GAPS  *(moved from FAIL)*

The confidently-wrong "not found" claim that drove Phase 45's FAIL is
gone — verified independently, not taken on the lead's word. No
incorrect or misleading claim remains. But this is not a clean PASS:
the *only* reason the result changed from misleading to honest is that
the file is now correctly registered as a tracked artifact; the
underlying inability to surface any of the file's substantive
compatibility content is completely unchanged and remains a real,
material gap for this exact question.

### Context advantage: LOW  *(moved off LOW-negative, but still LOW, not positive)*

Could a fresh Claude session get this trivially? **Yes, and it still
gets a strictly better answer.** Reading `dev-docs/hledger-
compatibility.md` directly (single file, `cat`/`Read`) gives the
complete, current compatibility contract in seconds, including the new
Query Language section. CodeCompass's fixed output no longer actively
misleads, but it still contributes nothing toward answering the actual
question — the advantage is not "negative" anymore (Phase 45's "worse
than doing nothing"), but it has not moved past the floor: a diligent
agent gains zero net benefit from running `codecompass query relations`
here versus going straight to the obvious file.

### Material gaps / failures

- `CG-002`/`L-016`'s glob-coverage root cause is fixed and independently
  reconfirmed here. The **distinct**, not-yet-addressed gap: mechanical
  `doc_relations_edges` construction has no representation of a spec
  doc's own subject-matter content — only literal name-mentions of
  vendors/Skills. For a project with 0 tracked vendors (like Ledgerkit),
  this means `query relations` on *any* spec doc will structurally
  return `(none)` regardless of how substantive that doc's content is.
  This was visible before the fix only because the "not found" error
  masked it; now that the error is gone, this is the accurately-exposed
  remaining limitation.

### Would this have misled the implementing agent?  no  *(changed from yes)*

An agent running this exact command now receives an honest "tracked,
no mechanical relations" signal rather than a confident false claim of
non-existence. It would not be misled into believing no governance
document exists. It would, however, learn nothing about the document's
actual content from this command alone and would still need to read
`dev-docs/hledger-compatibility.md` directly to get any real value —
exactly what a diligent agent would do next regardless.

---

# Q3 — Ledgerkit's current development-stage / roadmap state

## Setup

- **Reference project:** https://github.com/ctosullivan/ledgerkit
- **Pinned commit:** `a3cf2a77ca0075fabd4f7153d2a19f45c6e69b97`
- **CodeCompass revision:** `6c3f34e`
- **Task:** "What is Ledgerkit's current development-stage / roadmap
  state?" — an agent picking up work needs to know what's done, what's
  superseded, and what's next before proposing a task.
- **Context CodeCompass supplied:** nothing. CodeCompass's generated
  `CLAUDE.md` routing-table block in the Ledgerkit clone is an empty
  table (0 vendors); CodeCompass has no command or mechanism that reads
  or summarises a target project's own roadmap/stage-tracking files.

## Ground truth (read directly from the clone)

`ROADMAP.md` at the pinned commit: a 2026-09-12 "Core redefinition" note
states Milestones 0–4 are `[DONE]` (retained as completed history) and
**Milestone 5 ("CLI Filter Flags") is `[SUPERSEDED]`** — the underlying
need is folded into the new Stage C instead of being built as originally
scoped. Forward work now runs as **Stages A–I**: **Stage A `[DONE]`**
(2026-09-12, user-confirmed — agent roster, compatibility harness,
learning/doc lifecycle, with two explicitly named deferred follow-ups),
**Stage B `[PLANNED]`** next (core model / journal-accounting review,
Editor-compatibility confirmation), Stages C–I all `[PLANNED]`.
`CONTEXT.md` corroborates and adds working-memory detail: the just-
completed response was committing/pushing Stage A's work; open blockers
are that Stage B isn't yet scoped/approved, no local `hledger` binary
exists yet for the differential tester (needed from Stage C onward), and
the finer-grained compat-register migration is an open (non-blocking)
follow-up.

## Criteria assessment

| Criterion | Rating | Notes |
|---|---|---|
| Accuracy | n/a | No claim was made, so none can be wrong. |
| Relevance | n/a | No content returned. |
| Completeness | weak | Zero coverage of a real, well-documented, directly relevant class of information (the project maintains exactly this in `ROADMAP.md`/`CONTEXT.md`). |
| Freshness | n/a | Nothing returned to assess. |
| Grounding / provenance | n/a | No claim to trace. |
| Noise | strong | No noise — critically, no fabricated or stale "current stage" claim either. |
| Safety / trustworthiness | strong | The honest absence is safe: it does not assert anything false about the project's state, unlike Q2's "not found." |

## Verdict: PASS WITH GAPS

Nothing incorrect or misleading was produced — this is an honest,
structural absence, not a wrong answer dressed as a right one.
CodeCompass has never been designed to read or summarise a target
project's own roadmap/stage-tracking documents (`ROADMAP.md`,
`CONTEXT.md`, or equivalents); that's a real and complete gap for this
question, but it's the *expected* kind of gap for a package-relationship
tool being asked a project-management question, not a defect that
produced a false claim.

## Context advantage: LOW

Could a fresh Claude session get this trivially? **Yes, essentially for
free.** `ROADMAP.md` and `CONTEXT.md` are two files at the project root,
purpose-built to answer exactly this question, and reading both takes
seconds. CodeCompass currently contributes nothing to this question by
design — this is an honest, expected LOW-advantage result for a class of
question the tool was never built to answer, not a shortcoming worth
chasing on its own.

## Material gaps / failures

- No candidate learning filed for this one on its own merits — the
  registration record (`planning/reference-projects/ledgerkit.md`)
  already correctly notes this "is not a gap CodeCompass has ever claimed
  to fill." Recorded here for completeness of the baseline, not as a new
  finding.

## Would this have misled the implementing agent? no

Nothing false was asserted. An agent that asks CodeCompass this question
and gets nothing back has an accurate signal ("CodeCompass has no opinion
here") and would correctly go read `ROADMAP.md`/`CONTEXT.md` directly —
which is also the cheap, correct path a diligent agent would take
unprompted.
