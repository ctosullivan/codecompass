# Phase 54: Heterogeneous reference-material experiment — plan

**Status:** done (2026-09-16). Review gate implicitly resolved: the
user's "Implement the plan" approved both named judgment calls (the
Phase 54 renumbering; keeping the ingestion pipeline outside
`src/codecompass/`) without redirection. Implemented and run for real:
`planning/reference-projects/ledgerkit/reference-experiment/` (a real,
tested Git-backed resolve/lock/fetch/extract pipeline, 13 passing
tests), a real two-run comparison task (`tag:` query semantics brief,
baseline vs. treatment) against a scratch copy of Ledgerkit (never the
real clone), independently evaluated by `context-evaluator`: **baseline
PASS WITH GAPS, treatment FAIL, context-advantage LOW** — not a
mechanism failure but a real, caught-and-fixed extraction-boundary
defect (a hand-drawn line range silently excluded one of three
documented rules while its own description claimed all three; fixed,
regression-tested, the original FAIL preserved as the honest record).
Four real findings filed: detection generalises with zero schema change
(`OBS-007`); mechanical `mentions_artifact` structurally cannot relate
two `spec_doc` artifacts (`CG-004`); `origin`'s closed enum has no
externally-pinned-reference value (`CG-005`); a working YAML-evidence-
matching relation fallback was demonstrated real against Ledgerkit's own
already-published compat-register data but isn't wired into
CodeCompass's graph (`OBS-008`). `L-020` (content-hash pinning proves an
excerpt hasn't changed, not that its boundary matches its own claimed
content) filed and recommended for promotion by `knowledge-curator`. No
`src/codecompass/` change this phase — pure evidence-gathering for Phase
55/GATE DD. `release-phase-auditor` → **PASS** (first round).
`docs-reconstructor` drift audit not required (no current-truth doc
touched — no `src/`/`docs/`/`architecture/`/`ai-docs/` change this
phase). Retro:
`planning/retros/phase-54-heterogeneous-reference-material-experiment.md`.
Full verbatim request:
`planning/phase-54-heterogeneous-reference-material-prompt.md`.

This is Stage D's substantive goal, finally getting a phase slot: Phases
52 and 53 both retargeted their own numbers to unrelated, user-requested
scope (context edge lifecycle; legacy feature rationalisation), leaving
Stage D's actual work — deeper Ledgerkit dogfooding — without a number.
By issuing this prompt, the user resolves the open "Stage D vs. Stage
F/G" strategic decision from Phase 51's retro in Stage D's favour. This
phase does not implement anything; per the prompt's own explicit "do not
begin implementation until the phase plan has been produced and
reviewed," it stops at a reviewed plan.

## 0. Confirming the exact next-phase objective (orchestrator step 1)

`planning/v1-redefinition/roadmap.md`'s Stage D section already sketched
this work, twice, before either slot got spent on something else:

- Its own **Phase 52** stanza's original sketch: "Continue genuine
  Ledgerkit Core development" (retargeted to the context-edge-lifecycle
  work).
- Its own **Phase 53** stanza's original sketch: **"Heterogeneous doc /
  reference / manual dependencies"** — "Test whether CodeCompass can
  usefully index + relate reference material (hledger manuals,
  journal-format spec, command docs) to Ledgerkit's local implementation
  and compatibility tests — as evidence nodes with provenance, without a
  schema commitment" (retargeted to legacy-feature-rationalisation).
- `planning/v1-redefinition/ledgerkit-plan.md` §2's more detailed
  version of the same sketch, titled **"Phase 53 — Doc / reference
  test"**: "can CodeCompass usefully index and relate reference material
  ... as evidence nodes with provenance, without a premature schema
  commitment? Try it with the mechanisms that already exist: register
  the manual text the way vendor upstream docs are registered
  (`kind='vendor_doc'` precedent, Phase 27/29); see whether mechanical
  mention-detection + the doc-relations graph produce anything
  trustworthy."

This is exactly the objective the user's prompt names. **A real
numbering conflict had to be resolved before assigning it a slot**:
`v1-redefinition/roadmap.md`'s **Phase 54** stanza is not empty — it
already holds its own distinct sketch, "External executable /
behavioural context" (`ledgerkit-plan.md`'s "Phase 54 — Behavioural /
executable test": ingesting *executable* hledger-comparison evidence,
not doc/reference material — a different experiment). Per this
project's own established lesson (Phase 47's retro: "check which
sketch the actual evidence matches before defaulting to the next
sequential number"), the doc/reference-material work does not belong in
Phase 54's existing slot by coincidence of arithmetic — but the
sequence's own original ordering (doc/reference test, *then*
behavioural/executable test, *then* the decision gate) already put the
doc/reference work immediately before whatever now sits at 54. Since 53
is spent, **Phase 54 is retargeted** (same retarget-and-amend precedent
as Phases 52 and 53 themselves) to the doc/reference-material work that
was always meant to come right before it; the executable/behavioural
sketch is not discarded, just left without a claimed number, alongside
Phase 55's still-open GATE DD decision gate (unaffected, un-renumbered).

**Confirmed objective for Phase 54**: test whether CodeCompass can make
external technical reference material — specifically the hledger
manual/specification and source — materially useful to an agent working
on a real, current Ledgerkit task, evidence-first and without
prematurely committing to a new graph ontology. The prompt's own
`references.toml → resolve → lock → fetch/cache → extract → index →
relate` pipeline is evaluated as *one candidate mechanism* against this
objective, not adopted as the answer up front (§2 below).

## 1. Current-state inspection (orchestrator step 2)

**CodeCompass**: Phase 53 done (`60371ef`); contributor-licensing terms
added since (`65afede`, unrelated to this phase). No open `src/` work in
flight. `context-graph.db` schema: `doc_artifacts.kind` is a closed,
7-value CHECK enum (`claude_md, overview, skill, cursor_mdc,
slash_command, spec_doc, vendor_doc`); `doc_artifacts.origin` is a
closed, 5-value CHECK enum (`codecompass_tool, codecompass_vendor,
third_party, project, vendor_upstream`) — both have been extended by
exactly one value per phase historically (Phase 17, 21, and the
`vendor_doc`-introducing phase), never restructured. `doc_artifacts.
vendor_id` is nullable (`spec_doc` rows already use `NULL`).
`doc_relations_edges.relation_kind` is `mentions_dependency` (matches a
tracked `vendors` row's name) or `mentions_artifact` (word-boundary
matches *any* `doc_artifacts` row with a non-null `name`, regardless of
`kind` — not restricted to Skills). `spec_docs.py::_DEFAULT_GLOBS`
already includes `dev-docs/**/*.md` (Phase 49's own fix, evidenced by
this exact reference-project's own Phase 45 finding).
`doc_relation_enrichment.relation_label` has two live producers as of
Phase 52 (`decisions/0054`): the batched Anthropic-API path, and
`codecompass enrich apply` for a Claude Code agent.

**Ledgerkit** (`/home/cormac/projects/ledgerkit`, a real, live,
independently-developed clone — never written to by CodeCompass or this
phase): re-confirmed live against `origin/main` this session — **no
drift since Phase 51's `05218e3` pin** (`git fetch origin`; local HEAD
== `origin/main` HEAD, both `05218e3`). Current state: **Stage C (Query
system) is `[IN PROGRESS]`, Phase 1 done** — `hledger-researcher`'s
`dev-docs/planning/core-redefinition/17-query-semantics-brief.md` plus a
standalone, tested `ledgerkit/query/` subpackage implementing `acct:`/
`desc:`/`date:`(simple)/`depth:`/`status:`/`not:`; 7 new
`dev-docs/compat-register/*.yaml` entries, all `status: proposed`
(pending `compat-differential-tester`'s executable verification, out of
this phase's scope). **`tag:`/`cur:`/smart-dates/`PythonRegex` extension
are explicitly deferred**, and Stage C's "next phase not yet scoped" per
Ledgerkit's own `ROADMAP.md`.

**The hledger reference material itself** (`/home/cormac/projects/hledger`,
a real, pinned, local clone — Ledgerkit's own `hledger-researcher`/
`compat-differential-tester` tooling already references it by path,
per `dev-docs/planning/core-redefinition/10-source-assisted-development.md`
§10.5, "a pinned local clone of `hledger`... lives outside the
Ledgerkit repository... referenced by path... never vendored"): confirmed
live at commit `33fa849e7ae841968bd21c427094c4fb4a4ec38d`, tagged
`1.52.4`/`hledger-1.52.4`/`hledger-lib-1.52.4` (`git describe --tags`,
`git tag --points-at HEAD`) — **exactly matching every `pinned_at:
"1.52.4 (commit 33fa849e...)"` citation already written into Ledgerkit's
own compat-register entries.** This is not a hypothetical source to set
up; it already exists, at the exact commit Ledgerkit's own process has
already independently pinned and cited by hand.

**The concrete gap, read directly from a real compat-register entry**
(`LK-COMPAT-QUERY-DATE-001.yaml`, one of the 7 Stage-C-Phase-1 entries):

```yaml
evidence:
  - kind: manual
    ref: "https://hledger.org/1.52/hledger.html#queries (date:, hledger.1:7295-7314)"
    pinned_at: "1.52.4"
  - kind: source
    ref: "hledger-lib/Hledger/Data/Dates.hs:429 (single-date span), 1132-1148 (doubledatespanp, exclusive end)"
    pinned_at: "1.52.4 (commit 33fa849e7ae841968bd21c427094c4fb4a4ec38d)"
```

`hledger-researcher`'s own brief (§"What to do" in
`.claude/agents/hledger-researcher.md`) produces exactly this: a manual
URL/anchor and a source file/line-range, gathered by manually reading
`hledger.org` and grepping the pinned local clone by hand, once per
feature researched. **This is the real, live, already-happening workflow
this phase's experiment targets** — not an invented scenario.

## 2. Selected genuine task (orchestrator step 3)

**Task**: produce the `hledger-researcher`-shaped semantics brief and
compat-register-entry evidence for the next explicitly-deferred Stage C
query feature — **the `tag:` query term** (named as deferred alongside
`cur:`/smart-dates/`PythonRegex` in Ledgerkit's own Stage C row) — once
using CodeCompass-ingested, pinned reference material, once using
today's real baseline (manual `WebFetch`/`grep` against the local
pinned clone, exactly as `hledger-researcher`'s own brief instructs).

Why this task, not an invented one: it is Ledgerkit's own next
unscoped unit of Stage C work, in the same feature family (query
semantics) as the 7 entries already `proposed`, requiring exactly the
same two evidence sources (`hledger.org`'s manual, the pinned hledger
source) those entries already cite — a genuine like-for-like comparison,
not a contrived best case. **This phase does not write anything into
the Ledgerkit repository** (no PR, no file added to `ledgerkit/`,
`tests/`, or `dev-docs/`) — consistent with Phase 46's own precedent of
running a real task read-only against a live, independently-developing
sibling project. The brief/evidence this phase produces is a CodeCompass
evaluation artifact (`planning/reference-projects/ledgerkit/`), never
submitted to Ledgerkit.

## 3. Evaluating the proposed mechanism against what already exists (orchestrator steps 4–6)

The prompt's own `references.toml → resolve version/tag → immutable
commit → references.lock → fetch/cache → extract → index with
provenance → relate` pipeline is a sound *shape* — it matches, point for
point, what Ledgerkit's own `10-source-assisted-development.md` §10.5
already does *by hand* ("a pinned local clone... at the tag matching the
current baseline... re-clone, re-pin, re-verify" on a version bump). The
question this phase must answer is **how much of it needs new
CodeCompass mechanism, versus how much the existing graph/discovery
machinery already covers** — checked directly against real code, not
assumed:

1. **`doc_artifacts.kind`/`origin`**: both are small, closed CHECK
   enums, already extended by exactly one value per phase historically
   (never a new table). The `ledgerkit-plan.md` sketch's own
   recommendation — "register the manual text the way vendor upstream
   docs are registered (`kind='vendor_doc'` precedent)" — reuses an
   *existing* value rather than adding a new one. Whether that reuse is
   sufficient, or whether the provenance this phase needs (a Git commit
   SHA + a manual URL/anchor + a content hash, none of which
   `vendor_upstream` currently carries) forces one new `origin` value
   (e.g. `pinned_reference`) is the phase's first concrete finding to
   produce, not a decision made in this plan.
2. **Detection/glob coverage**: `spec_docs.py::_DEFAULT_GLOBS` already
   includes `dev-docs/**/*.md` — if extracted reference excerpts are
   materialized as Markdown files under a `dev-docs/`-shaped path in a
   **scratch copy** of the Ledgerkit tree (never the real repo),
   CodeCompass's existing mechanical spec-doc detection picks them up
   with **zero code change**. This is the single cheapest hypothesis to
   test first, and is tested first (§4, Cycle 1).
3. **Relating to Ledgerkit's own docs/compat-register entries**:
   `doc_mapping.build_doc_relations_edges`'s `mentions_artifact` kind
   already matches *any* `doc_artifacts` row with a non-null `name`
   against a source doc's full text via word-boundary search — not
   restricted to Skills. If the ingested reference excerpts are given a
   distinctive `name`, a compat-register YAML or `dev-docs/hledger-
   compatibility.md` mentioning that name would produce a real,
   mechanically-detected edge, at zero additional code cost beyond
   populating `name` correctly. Whether Ledgerkit's real prose (which
   currently cites URLs/file:line ranges, not a CodeCompass-minted
   identifier) actually contains anything that word-boundary-matches is
   an open, empirically-testable question — plausible failure mode:
   **the existing mention-detection mechanism may find nothing**,
   because Ledgerkit's provenance citations are structured YAML fields
   (`evidence.ref`), not prose mentions of a name string. This phase
   explicitly tests for that failure and reports it as a real finding
   either way (see §5.2 — a **direct parse of the YAML's own
   `evidence:` block** is the fallback hypothesis, arguably more
   reliable than prose-mention inference since the citation is already
   structured data, not something to infer).
4. **`vendor_id`**: nullable already (spec_docs use `NULL`); no new
   column needed to represent "this doc_artifact isn't a `vendor.toml`-
   tracked ecosystem package."
5. **Enrichment**: `doc_relation_enrichment` + `RELATION_LABELS` already
   supports an AI (or agent-driven, Phase 52) one-line summary of *how* a
   mechanically-detected relation relates. `'other'` already exists as
   the closed-taxonomy fallback (`decisions/0045`) — this phase does not
   propose a new label unless a real produced relation turns out to need
   one no existing label covers (tested, not assumed).

**Conclusion for this plan**: the ingestion *pipeline itself*
(references.toml/resolve/lock/fetch-cache/extract/hash) has no existing
CodeCompass equivalent and is new, narrow, experimental code (§4). What
it *feeds into* — detection, relation, provenance storage, enrichment —
is tested against the existing graph mechanisms first, escalating to a
minimal (single CHECK-enum-value) schema change only if the zero-schema
path demonstrably fails to represent something the task actually needs.
**No `TechnicalDependency` (or any other new table/ontology) is
introduced by this plan** — per the prompt's own instruction, that
question is explicitly Phase 55/GATE DD's to answer, informed by this
phase's evidence (§7).

## 4. Experiment design (orchestrator step 4)

**The ingestion pipeline** (new, narrow, `planning/reference-projects/ledgerkit/reference-experiment/`
— **deliberately outside `src/codecompass/`** for this phase; see
"Design decisions"):

1. `references.toml` — one entry: `hledger`, `source = "git"`, `url =
   "https://github.com/simonmichael/hledger"` (or Ledgerkit's own
   already-pinned local clone path, confirmed identical content — see
   "Design decisions" on which to prefer), `requested_ref = "1.52.4"`.
2. **Resolve**: `git ls-remote --tags`/local-clone tag lookup → the
   human-friendly tag resolves to an exact commit SHA. Confirmed
   expected result before writing any code: `33fa849e7ae841968bd21c427094c4fb4a4ec38d`
   (already verified live, §1).
3. `references.lock` — records `source`, `requested_ref`,
   `resolved_commit`, `fetched_at`, and, per selected path, its own
   `content_hash` (sha256) — the exact fields the prompt specifies
   ("preserve source, requested ref, resolved commit, selected
   paths/sections and content hashes").
4. **Fetch/cache**: a content-addressed local cache
   (`.cache/references/hledger/<commit>/`), populated either by a shallow
   `git clone --revision <commit>` or by copying from the already-present
   pinned local clone at that exact commit (both produce byte-identical
   content; the phase's implementation records which it used and why).
5. **Extract selected files/sections**: exactly the two hledger sources
   real Ledgerkit compat-register entries already cite for the
   `date:`/`tag:` family — the `hledger.1` man-page's "queries" section,
   and `hledger-lib/Hledger/Data/Dates.hs`'s tag-adjacent parsing logic —
   as small, self-contained Markdown files, each carrying a frontmatter
   provenance block (source, resolved commit, original path, line range,
   content hash, extracted-at timestamp).
6. **Index with provenance / relate**: run CodeCompass's real,
   unmodified `codecompass sync`/`index` against a **scratch copy** of
   the Ledgerkit tree (never the real clone) with the extracted files
   materialized under a `dev-docs/`-shaped path (§3.2's zero-schema-change
   hypothesis, tried first) or, if that proves insufficient, registered
   via a small integration point reusing `kind='vendor_doc'`/`origin=
   'vendor_upstream'` (§3.1's fallback). Either way, the *reference
   experiment's* own code never edits `context-graph.db`'s schema
   directly and never bypasses `graph.py`'s existing writer functions —
   same discipline `decisions/0038`/`decisions/0054` already establish
   for every other producer.

**The comparison task** (§2's chosen task, run twice):

- **Baseline** (today's real workflow): the lead, acting as
  `hledger-researcher` would, manually reads `https://hledger.org/1.52/hledger.html#queries`
  (via `WebFetch`) and greps the pinned hledger clone directly, to
  produce the `tag:` semantics brief + evidence citations — no
  CodeCompass reference-ingestion involved at all.
- **Treatment**: the lead attempts the same brief using only what the
  ingestion experiment made queryable through CodeCompass (`codecompass
  query relations`/`query vendor`-equivalent against the scratch copy,
  or direct inspection of the extracted, provenance-tagged Markdown
  files) — not falling back to a fresh manual fetch/grep unless the
  ingested material is confirmed insufficient, itself a recordable
  finding.

## 5. Reuse of Phase 52's context-observation lifecycle (orchestrator step 7)

Every real point of friction from both runs — useful, irrelevant,
misleading, or missing context — is filed as a
`planning/context-observations/OBS-NNN` entry (Phase 52's queue, not a
new mechanism), using its existing edge-correctness/task-usefulness
split. This phase is explicit dogfooding of that lifecycle a second
time, per the prompt's own instruction, not a new instrument.

Distinct from `context-observations` (experience with an edge that
exists): if the baseline run needs a relationship CodeCompass's ingested
material genuinely lacks (e.g., a `cur:`-family source excerpt never
extracted), that's a `planning/context-gaps/CG-NNN` entry instead
(`decisions/0051`) — the two queues' existing, already-established
distinction, unchanged.

## 6. Evaluation design (orchestrator step 8)

Follows `reference-project-protocol.md`'s established per-task procedure
exactly (the same one Phases 45/46/51 already used): the lead attempts
the task; `reference-project-tester` records friction live for **both**
runs; `context-evaluator` independently inspects Ledgerkit and the
pinned hledger clone directly (never through CodeCompass) and rates
**both** the baseline and the treatment output against the same rubric
— PASS / PASS WITH GAPS / FAIL, plus a LOW / MODERATE / HIGH
context-advantage rating (`context-quality-evaluation.md`'s existing
instrument, unchanged). The central comparison is the **delta** between
the two verdicts/ratings for the *same* task and the *same* underlying
evidence sources — not either run in isolation.

**Explicit acceptance of a negative or inconclusive result**
(orchestrator step 9): "the ingested material produced no material
improvement over the existing manual workflow" and "the two runs were
indistinguishable" are both valid, fully-reportable outcomes — this
phase's own "Done when" (§9) does not require the treatment run to win.
A negative result here is itself evidence for Phase 55/GATE DD (§7):
possibly that Ledgerkit's `hledger-researcher` workflow is already
efficient enough that pinning/indexing adds process weight without
material benefit at this project's current scale, distinct from "the
mechanism doesn't work" — the plan's own retro must distinguish these
two very different negative-result readings.

## 7. Evidence this phase must produce for Phase 55/GATE DD (orchestrator step 10)

Regardless of verdict, this phase must leave Phase 55 able to answer, with
real evidence rather than speculation:

1. **Did the zero-schema-change hypothesis (§3.2, `dev-docs/`-glob
   reuse) work, or was a minimal schema addition (one `kind`/`origin`
   enum value) actually needed?** — the single most load-bearing finding
   for "what is the smallest model that covers the demonstrated need"
   (`ledgerkit-plan.md`'s own Phase-55-decision framing).
2. **Did mechanical `mentions_artifact` detection find any real edge
   between Ledgerkit's own docs/compat-register and the ingested
   material, or did it require the YAML-`evidence`-field-parsing
   fallback (§3.3)?** — bears directly on whether "provenance" needs to
   become a first-class graph concept (structured citations) or stays
   representable as ordinary mechanically-detected mentions.
3. **Was the treatment run's evidence (manual anchor + source file/line
   + content hash + resolved commit) at least as precise and
   reproducible as `hledger-researcher`'s own hand-gathered citations in
   the 7 real compat-register entries already on file?** — a concrete,
   checkable bar, not a subjective impression.
4. **Context-advantage rating and verdict for both runs**, with the
   `context-evaluator`'s full reasoning — the standard instrument's own
   output, feeding the same aggregation `findings.md` already uses.
5. **Every `OBS-NNN`/`CG-NNN` filed**, and whether any recurred against
   Phase 45/46/51's own prior Ledgerkit findings (the established
   recurrence-based promotion bar, `learning-lifecycle.md`).
6. **An explicit recommendation** (not a decision — Phase 55/GATE DD's
   own job): fold the experiment's pipeline into `src/codecompass/` as a
   real feature; keep it Ledgerkit-specific and out of `src/`; or drop it
   as not worth generalising — each with the evidence line above that
   justifies it.

## Scope

**In scope:**

- `planning/reference-projects/ledgerkit/reference-experiment/` — the
  new ingestion pipeline (`references.toml` parsing, tag→SHA resolution,
  `references.lock` writing, fetch/cache, extraction with provenance
  frontmatter), real and tested (`pytest`-covered), but **not** inside
  `src/codecompass/` this phase (see "Design decisions").
- Zero or one CHECK-enum-value addition to `doc_artifacts.kind`/`origin`
  in `src/codecompass/graph.py`, **only if** §3.2's zero-schema-change
  hypothesis is empirically shown insufficient during the experiment —
  not decided in advance.
- A scratch copy of the Ledgerkit working tree (never the real clone) to
  run `codecompass sync`/`index`/`query` against, with the extracted
  reference material materialized into it.
- The two-run comparison (baseline vs. treatment) for the `tag:` query
  semantics brief task, per `reference-project-protocol.md`'s standard
  procedure, both directions run and rated.
- `planning/context-observations/` and `planning/context-gaps/` entries
  for every real friction point from both runs.
- `planning/reference-projects/ledgerkit/findings.md` gains a new dated
  section (its own established append-pattern, per its own header note)
  recording this phase's outcome as input to Phase 55/GATE DD.

**Explicitly deferred / out of scope** (per the prompt's own exclusions,
restated for this specific plan):

- Any new relationship type beyond what `RELATION_LABELS`/
  `relation_kind` already support, unless a produced relation
  demonstrably needs one (tested, not assumed up front).
- Embeddings, vector search, or any semantic-similarity mechanism —
  extraction/relation stays mechanical (exact file/line/name matching),
  matching every existing CodeCompass detection mechanism's own
  no-AI-for-detection posture (`decisions/0031`/`0045`).
- Hosted infrastructure, multi-repo support, MCP work, IDE interfaces —
  none of this phase's mechanism requires any of them.
- A generalised `TechnicalDependency` (or equivalent) ontology, a graph
  schema rewrite, or `vendor.toml` configurability for reference sources
  — explicitly Phase 55/GATE DD's call, informed by (not pre-empted by)
  this phase.
- The "External executable / behavioural context" experiment
  (`ledgerkit-plan.md`'s own Phase 54 sketch, now displaced by this
  retarget) — still a valid future direction, unclaimed, no number
  assigned.
- Wiring the ingestion pipeline into `sync`/`init`/any stable CLI
  surface, or documenting it in `README.md`/`docs/` as a shipped
  feature — this stays an evaluation instrument until Phase 55 decides
  otherwise.
- Any change to the real Ledgerkit repository — read-only throughout,
  same discipline as Phase 46.

## Design decisions

- **The ingestion pipeline lives outside `src/codecompass/` for this
  phase.** Stage D's own stated goal (`v1-redefinition/roadmap.md`) is
  "decide whether v1 scope must exceed package-source grounding, using
  ... evidence" — shipping the mechanism into the real package before
  that decision is made would pre-empt Phase 55/GATE DD rather than
  inform it, and risks exactly the "generic ontology" over-commitment
  the prompt explicitly warns against. Real, tested, re-runnable code —
  just not yet a CodeCompass *feature*. Mirrors `tests/fixtures/
  ledgerkit_lifecycle_demo/`'s own precedent (Phase 52): a real,
  committed, tested artifact outside the shipped package.
- **Prefer the already-pinned local hledger clone
  (`/home/cormac/projects/hledger`) as the fetch source for this
  experiment's cache**, confirmed byte-identical to a fresh clone at the
  same commit (both are the same Git object graph) — but the resolution
  step (`references.toml`'s tag → `references.lock`'s commit SHA) is
  still exercised for real via `git ls-remote`/local tag lookup, not
  hard-coded, so the mechanism is genuinely validated, not faked from a
  known-good answer.
- **Try the zero-schema-change path first, always.** Every escalation
  (a new `doc_artifacts.kind`/`origin` value, a YAML-`evidence`-parsing
  fallback for relation detection) is gated on the cheaper path being
  empirically shown insufficient, mirroring this project's own
  "smallest justified fix" precedent (Phase 47/49's own narrow-glob-fix
  decision, explicitly validated as correct by Phase 51's re-run).
- **No `vendor.toml` entry for hledger.** It is not an ecosystem package
  any `EcosystemAdapter` installs; forcing it through that pipeline would
  itself be a premature-ontology move the ingestion experiment is meant
  to avoid, not repeat via a different door.
- **URL + SHA-256 stays available for a reference source with no usable
  Git history** (the prompt's own "consider... URL + SHA-256 only where
  appropriate") — not exercised in this phase (hledger has a clean,
  already-pinned Git source), but the `references.toml` schema is
  designed to accept a `source = "url"` variant alongside `source =
  "git"` from the start, so a future non-Git reference source (e.g. a
  standalone spec PDF) doesn't require a schema redesign — this is
  schema *breadth for the ingestion tool itself*, not the graph-ontology
  breadth the prompt warns against; the two are different surfaces.

## Files

- `planning/reference-projects/ledgerkit/reference-experiment/` — new:
  `references.toml`, the resolve/lock/fetch/extract pipeline code,
  its own tests.
- `planning/reference-projects/ledgerkit/reference-experiment/references.lock`
  — generated output, committed (small, human-readable, itself a
  provenance record worth keeping).
- A scratch copy of the Ledgerkit tree — **not committed to this repo**
  (matches every prior reference-project evaluation's own working-copy
  discipline); referenced by path from the experiment's own README.
- `src/codecompass/graph.py` — **only if** the zero-schema-change
  hypothesis fails empirically; one `kind`/`origin` CHECK-enum value
  each, same shape as every prior enum extension.
- `planning/reference-projects/ledgerkit/<NN>-tag-query-semantics-reference-experiment.md`
  — the per-task evaluation report (`TEMPLATE-evaluation.md`), covering
  both runs.
- `planning/reference-projects/ledgerkit/findings.md` — new dated
  section recording this phase's outcome, appended below the existing
  GATE DB section per its own header's stated convention.
- `planning/context-observations/inbox.md`, `planning/context-gaps/inbox.md`
  — new entries from both runs.
- `docs/`, `architecture/`, `ai-docs/README.md` — updated only if the
  zero-schema-change path fails and a real `graph.py` change lands
  (`docs-maintainer`'s normal reconciliation); no change expected if the
  zero-schema-change hypothesis holds.
- `planning/retros/phase-54-heterogeneous-reference-material-experiment.md`
  — the phase retro.

## Verification

- The ingestion pipeline's own test suite: tag→SHA resolution against
  the real hledger repository (live `git ls-remote`, or a recorded fixture
  if a live network call is judged too flaky for CI — the phase's
  implementation decides and discloses which, consistent with
  `decisions/0014`'s existing "tests never make a real external call
  live" posture for the ecosystem adapters), `references.lock` content
  matching the resolved commit + correct content hashes for every
  extracted file, idempotent re-runs producing a byte-identical lock
  file and cache.
- `codecompass sync`/`index`/`query relations` run against the scratch
  Ledgerkit copy, before and after the reference material is
  materialized into it — confirming detection (or its absence) directly,
  not by assertion.
- Both the baseline and treatment runs of the `tag:` semantics brief
  task produce a real, checkable artifact (the brief itself, plus its
  evidence citations) — `context-evaluator`'s independent verdict for
  each, not the lead's own self-assessment.
- `pytest`/`ruff check .`/`python scripts/check_user_docs.py --strict`
  clean throughout — the experiment's own new tests included, whether or
  not it lives inside `src/codecompass/`.

## Done when

Standard DoD (`CLAUDE.md` §5) + both runs of the comparison task
completed and independently rated + every real friction point filed via
Phase 52's context-observation/context-gap queues + §7's evidence
checklist fully answered (with real findings, not placeholders) +
`planning/reference-projects/ledgerkit/findings.md` updated + the
phase's own retro explicitly states whether the result was positive,
negative, or inconclusive, and why, without pressure toward any
particular outcome + `release-phase-auditor` PASS or PASS WITH
NON-BLOCKING OBSERVATIONS.

**Not done merely because code was written or a run completed** — done
only once `context-evaluator`'s independent verdict exists for both
runs and the evidence checklist (§7) is answered with real findings.

---

## Review gate

Per the prompt's own explicit "do not begin implementation until the
phase plan has been produced and reviewed": this plan is presented for
review now. Two things worth the user's explicit attention before
implementation starts, since both are judgment calls this plan makes
that a different call would meaningfully change the phase's shape:

1. **The Phase 54 renumbering** (§0) — retargeting the existing
   "External executable / behavioural context" sketch's slot rather
   than inserting a fresh number. If a different resolution is
   preferred (e.g., inserting this as an unnumbered sub-phase, or
   renumbering the executable/behavioural sketch and the GATE DD gate
   forward), say so before the roadmap docs are finalized in this
   phase's own commit.
2. **Keeping the ingestion pipeline outside `src/codecompass/` for this
   phase** (Design decisions) — a deliberate choice to avoid pre-empting
   Phase 55/GATE DD, but if the user's intent was for this phase to
   produce shippable `src/` code directly (not just evidence toward a
   later generalisation decision), that changes the scope materially.
