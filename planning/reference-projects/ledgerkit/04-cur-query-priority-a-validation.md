# Context-quality evaluation — Ledgerkit `cur:` query-term design/discovery (Phase 75, Priority A validation)

## Methodological note (read first)

This evaluator was told that both dispatched agents' full raw reports
(including their raw tool-call/file-access logs) were "already in this
conversation's history." They were **not** present in the context this
evaluator actually received — only the lead's own summary of key claims
(in the dispatch prompt) was available, plus the two scratch clones on
disk. Per this evaluation's own hard rule ("never trust either agent's
own report as ground truth"), this is treated as an opportunity rather
than a blocker: every claim attributed to either agent below was checked
against (a) this evaluator's own independent reading of the real
Ledgerkit source, the real pinned hledger source, and the real hledger
1.52.4 manual, and (b) live re-execution of the specific `codecompass`
commands the treatment run is said to have used, inside the actual
treatment scratch clone. Neither scratch clone (`ledgerkit-baseline`,
`ledgerkit-treatment`) contains any leftover written artifact from either
agent (`git status` clean, no untracked files in either) — both
agents' work products apparently existed only as their returned messages,
which this evaluator did not receive verbatim. Where a claim could not be
independently confirmed either way (chiefly: the exact wording either
agent used in its own five-question answers), this is stated explicitly
rather than assumed. This materially limits a few sub-assessments below
(noted inline) but does not block the core ground-truth work, which this
report performs from the real repositories directly, as required.

## Setup

- **Reference project:** Ledgerkit (local checkout, `/home/cormac/projects/ledgerkit`)
- **Pinned commit:** `6c90b4c` (both scratch clones confirmed at this exact
  commit; the real checkout's own `HEAD` is also `6c90b4c` as of this
  evaluation)
- **CodeCompass revision:** working tree at `d4f5e0a` (`pyproject.toml`
  version `1.0.0`); treatment clone synced with **0 tracked vendors**, no
  AI enrichment (no API key available) — confirmed live (`codecompass
  query vendors` returns an empty table; `.claude/skills/codecompass/SKILL.md`
  reads "Vendors (0 tracked, 0 enriched)").
- **Task:** implement hledger's `cur:` query term in Ledgerkit's query
  engine (`ledgerkit/query/`) — a real, named, deferred Stage-C
  follow-on item (`dev-docs/hledger-compatibility.md:276`,
  `07-query-regex.md`). Two independently-dispatched fresh agents (no
  access to each other, no access to this evaluation) were asked to
  produce design/discovery material only — not implementation — answering
  five fixed questions (match target/multiplicity, own-term-vs-alias,
  structural precedent, test cases, open uncertainty). Baseline: ordinary
  tools + `WebFetch` against the public hledger 1.32/1.52 manuals, no
  CodeCompass. Treatment: CodeCompass installed/synced against its own
  clone, encouraged to use `codecompass query`/Skills first.
- **Context CodeCompass supplied (reproduced live by this evaluator, not
  taken from the treatment's own report):**

  `codecompass query relations dev-docs/hledger-compatibility.md --json`
  returns exactly 11 `mentions_artifact` relations, all
  `ai_summary: null` ("mentioned, not yet enriched"), targeting:
  `dev-docs/api-spec.md`,
  `dev-docs/planning/core-redefinition/09-compatibility-system.md`,
  `.../10-source-assisted-development.md`,
  `.../17-query-semantics-brief.md`,
  `.../19-tag-query-semantics-brief.md`,
  `.../20-tag-parsing-syntax-brief.md`,
  `.../21-stage-c-phase-5-depth-and-verification-plan.md`,
  `.../23-tag-query-matching-design.md`,
  `.../25-query-regex-empty-pattern-matrix.md`,
  `.../26-query-regex-empty-pattern-design.md`,
  `.../27-query-shim-convergence-design.md`. "Package code" trace: empty
  (no vendor code involved). `codecompass query symbol Posting` →
  `no symbol named 'Posting' found in context-graph.db`; `codecompass
  query symbol Amount` → same, empty, for `Amount`. Both reproduced
  live, exactly as the treatment run is reported to have found them.

## Criteria assessment

| Criterion | Rating | Notes |
|---|---|---|
| Accuracy | strong | Every one of the 11 `mentions_artifact` edges returned is a real, independently spot-checked citation relationship (each target doc genuinely appears via a real name-match under `dev-docs/hledger-compatibility.md`'s own text). Nothing false or fabricated was returned — no AI-generated summary exists to be wrong, since 0 vendors/no enrichment; the tool never asserted a semantic claim about `cur:` itself, only "this doc mentions that doc." |
| Relevance | adequate | Most of the 11 surfaced docs are genuinely on-topic (the `tag:` family as structural precedent; the regex-dialect/empty-pattern design docs, directly relevant to any new regex-taking term; the compat/shim framework docs). But relevance here is a pure citation-network artifact (word-boundary title match), not task-semantic relevance — see Material gaps: it missed the single most task-specific document in the whole corpus. |
| Completeness | weak | On the two hardest, most technical of the five required questions — what `cur:` matches against (`Posting`/`Amount`, single- vs. multi-commodity) — CodeCompass contributed **nothing at all**: `query symbol Posting`/`Amount` returned empty because CodeCompass has zero symbol-level index of a project's own first-party source (confirmed structurally, see Gaps). Its only real contribution was doc-surfacing, and even that missed the most directly relevant single doc (`07-query-regex.md`, which has the literal `cur:REGEX | commodity match | not implemented` table row). |
| Freshness | adequate | All 11 relations reflect the actual pinned `6c90b4c` file tree (every target path was independently confirmed to exist, with real matching content, at that commit). No AI-enrichment staleness risk exists in this run (there is no enrichment to go stale). |
| Grounding / provenance | strong | Every claim CodeCompass makes here is a `(source path, target path, heading)` triple traceable to a literal, checkable citation in real file text — independently spot-verified for several of the 11 (e.g. the `tag:` family docs are genuinely named inside `hledger-compatibility.md`'s "Query Language" section). |
| Noise | adequate | 11 relations for one query is a reasonable, readable set; a couple (`10-source-assisted-development.md`, `api-spec.md`) are more general/process docs than task-specific, but nothing egregious. |
| Safety / trustworthiness | strong | CodeCompass never presented an incorrect or misleading relationship as authoritative — every edge shown is real, and the tool's own "not yet enriched" labelling is honest about the absence of any AI-generated interpretive claim to scrutinise. |

## Verdict: PASS WITH GAPS

No claim CodeCompass actually made was wrong or misleading — every
`mentions_artifact` edge it returned is real and independently
verifiable, and it made no unearned semantic claims about `cur:` itself.
That rules out FAIL. But the context was materially incomplete for the
task in two independent, structural ways confirmed directly against the
real system: (1) it has literally no way to help with the core technical
question ("what does `Posting`'s/`Amount`'s commodity representation
look like, and is it single- or multi-commodity per posting") because
`context-graph.db`'s `symbols` table only ever holds tracked-vendor
symbols (Ledgerkit's own `vendor.toml` is empty, and even a populated one
would only add the *vendor's* symbols, never the project's own), and (2)
its one genuinely useful surface — `query relations` on the compatibility
doc — missed `07-query-regex.md`, the single document in the whole
corpus that most directly names this exact task ("`cur:REGEX` |
commodity match | not implemented"), because that document happens not to
be cited by name inside `hledger-compatibility.md`'s own text (confirmed
directly: `grep -c "07-query-regex" dev-docs/hledger-compatibility.md` →
`0`). Trustworthy, but not sufficiently complete to stand alone.

## Context advantage: LOW

**Could a competent fresh Claude session have obtained equivalent context
trivially through ordinary repository inspection?** Yes, largely — and in
one respect a plain grep does *better* than the CodeCompass call the
treatment agent itself rated as "the single most useful."

Three independent lines of evidence support LOW rather than MODERATE/HIGH:

1. **The confound this evaluation was explicitly told to check (`L-027`)
   holds, and removes the one flashy claimed finding entirely.** The
   treatment agent's own most valuable-sounding discovery — hledger's
   real `cur:` uses anchored (`^...$`) full-string matching, a documented
   divergence from every other term's infix matching — was found by
   reading the real pinned hledger source at
   `/home/cormac/projects/hledger/hledger-lib/Hledger/Query.hs:320`
   (`parseQueryTerm _ (T.stripPrefix "cur:" -> Just s) = (,[]) . Sym
   <$> toRegexCI ("^" <> s <> "$") -- support cur: as an alias`),
   confirmed by this evaluator directly, plus the embedded test suite at
   lines 1186-1191 (`toSym "shek"` does **not** match `"shekels"`,
   confirming the anchor). CodeCompass never surfaced this path in any
   way — the treatment agent found it by noticing an absolute-path
   citation inside one of Ledgerkit's own planning docs, then running an
   **unscoped** `find / -iname Query.hs`. The baseline agent ran a
   **scoped** `find . -iname "*.hs"` (its own working directory only) and
   found nothing. Both commands were equally available to both agents —
   nothing about CodeCompass's presence or absence gated this discovery
   (confirmed: this is an ordinary filesystem `find`, not a CodeCompass
   surface, and the real hledger checkout sits on the same host
   filesystem both scratch clones share, entirely outside either clone's
   own directory tree). Per `context-quality-evaluation.md` §1's own
   standing rule, this is agent-diligence variance, not a
   context-quality result, and is not credited to CodeCompass.

2. **This evaluator's own further check makes the point even stronger:
   the same decisive fact was already sitting in the very manual the
   baseline agent had already fetched.** hledger's own manual source
   (`hledger/hledger.m4.md`) was inspected at both pins the baseline used.
   At `1.32` (2023-12-01), there is **no dedicated "cur: query" reference
   section at all** — only an ambiguous one-line example
   ("`cur:EUR` amounts with commodity symbol containing EUR", which reads
   like ordinary infix matching, with the anchor behaviour undisclosed).
   At `1.52` (the exact pin this task targets, and the version the
   baseline agent is reported to have `WebFetch`ed), there **is** a
   dedicated `### cur: query` section, unambiguous: *"Match postings or
   transactions including any amounts whose currency/commodity symbol is
   fully matched by REGEX. (Contrary to hledger's usual infix matching. To
   do infix matching, write `.*REGEX.*`.)"* — this is the exact fact
   attributed to the treatment's source-reading. It was available to the
   baseline agent in plain English, in the very manual page it is
   reported to have already fetched, with no source access and no
   CodeCompass involved at all. (git-blame confirms this manual passage
   landed at commit `85428d5ca`, 2024-12-06, well inside the `1.32→1.52`
   window, so this is not an artifact of comparing the wrong versions.)
   If the baseline's own final report did not surface this, that points
   to a `WebFetch`-summarisation/extraction gap on the baseline's side,
   not evidence that finding this fact required either local source
   access or CodeCompass.

3. **The one contribution genuinely attributable to CodeCompass — the
   `query relations` doc-surfacing call — is demonstrably no better than,
   and on one important axis worse than, a single grep.** A plain
   `grep -rl "cur:" dev-docs/` (independently run by this evaluator)
   returns 20 files including `07-query-regex.md` — the exact document
   `query relations dev-docs/hledger-compatibility.md` missed, and
   arguably the single most task-relevant document in the corpus (its own
   table row reads `cur:REGEX | commodity match | not implemented`). The
   29-file `dev-docs/planning/core-redefinition/` directory is also
   self-descriptively numbered/titled (`19-tag-query-semantics-brief.md`,
   `23-tag-query-matching-design.md`, `07-query-regex.md`) — a plain `ls`
   plus a skim gets most of the way there with zero tooling beyond what
   every session already has. On the task's actual technical core
   (`Posting`/`Amount` shape), reading `ledgerkit/models.py` directly (one
   file read) answers the question completely and immediately; CodeCompass
   contributed nothing here at all (confirmed live, `query symbol
   Posting`/`Amount` both empty).

Taken together: the one flashy finding is not CodeCompass's (and, per
finding 2, arguably not even source-access-gated at all), and the one
narrow thing CodeCompass genuinely did contribute (a doc short-list) is
matched or beaten by a single grep. This is the honest, expected LOW
outcome `context-quality-evaluation.md` §5 describes for a task whose
substantive content mostly lives in plain-text docs and a project's own
small, first-party source tree, neither of which CodeCompass's current
model (vendor-symbol index + doc-citation graph) is built to help with.

## Material gaps / failures

- **CodeCompass has zero symbol-level index of a project's own
  first-party source — only tracked vendor dependencies.** Independently
  confirmed both structurally and live: `src/codecompass/sync.py::rebuild_project_graph`
  populates `symbol_rows` only by iterating `configs: list[VendorConfig]`
  (i.e. `vendor.toml` entries) and calling `adapter.symbols()` per
  vendor — there is no code path anywhere that walks the project's own
  source tree to extract its own classes/functions into the `symbols`
  table, in any ecosystem, regardless of how many vendors are tracked.
  The schema enforces this structurally too:
  `symbols.vendor_id INTEGER NOT NULL REFERENCES vendors(id)` — a symbol
  row cannot exist without a `vendors` row to hang off, and a project is
  never itself a `vendors` row. Live-reproduced: `codecompass query
  symbol Posting`/`Amount` both return "no symbol named ... found in
  context-graph.db" for Ledgerkit's own `ledgerkit/models.py::Posting`/
  `Amount` dataclasses, in a clone with 0 tracked vendors (`vendor.toml`
  empty). Filed as new context-gap `CG-009` (see below) — not a
  restatement of `CG-008` (which was about a *vendor's* symbols failing
  to reach the graph for one ecosystem, already fixed) or `CG-001`
  (CodeCompass's *own* intra-`src` modules, a different project and
  mechanism).
- **`query relations` is a citation-graph surface, not a task-relevance
  surface, and this is a real, demonstrated blind spot, not merely a
  theoretical one.** It missed `dev-docs/planning/core-redefinition/07-query-regex.md`
  — the document with the literal `cur:` table row — solely because
  `hledger-compatibility.md` never cites that file by name or title
  anywhere in its own text (confirmed: zero occurrences). This is not a
  `CG-006` recurrence (that gap is specifically about *filename*
  citations being missed even though a title-match mechanism exists;
  here there is no citation of any kind, so no mechanism could have
  caught it) — it is the same broader §2.6 "task-oriented retrieval
  needs new edges, not just joins" hypothesis `CG-001` already names, on
  a genuinely different concrete edge (two independently-tracked,
  correctly-named spec docs, topically inseparable for this task, joined
  by nothing but shared subject matter — no citation, no shared symbol).
  Per the precedent `CG-001`'s own curation notes already set (a second
  instance of the *same hypothesis* on a *different concrete edge* is
  recorded as a cross-reference, not a promotion to `recurred`), this is
  noted here as a second, independent instance of that hypothesis for
  whichever phase next revisits `CG-001`/§2.6 — not filed as its own new
  `CG-NNN`, since it is the same underlying pattern `CG-001` already
  holds the canonical record for.
- **The phase's own task framing (not CodeCompass's output) contains a
  minor, independently-caught imprecision worth correcting for whoever
  does the real implementation:** hledger's `cur:` is not "an alias for a
  live `sym:` query term a user could also type" — `git log` on
  `hledger-lib/Hledger/Query.hs` shows `sym:` was the *original* surfaced
  prefix, later judged "unintuitive," with `cur:` added as a friendlier
  alias (`e42e58fd2`) that fully superseded it; the current `1.52.4`
  `queryprefixes` list (`Query.hs:255-275`) contains `cur` and **not**
  `sym` at all — a user typing `sym:USD` against real hledger 1.52.4
  gets a parse error. The internal AST constructor is still named `Sym`
  (a historical relic), which is presumably what produced the "alias for
  sym:" framing in the first place. This does not change the practical
  design conclusion (Ledgerkit needs its own `Cur`-shaped `QueryNode`,
  not a new `sym:` string-syntax term), so it is not itself a material
  gap in either agent's likely conclusion — but it is exactly the kind of
  subtle, easily-inherited framing error worth flagging independently
  rather than silently passing through into a real design document.
  Neither this evaluator's available material nor CodeCompass's own
  output could confirm whether either dispatched agent caught this on
  their own; it is recorded here as ground truth for the lead's own
  cross-check against whichever agent's Q2 answer is used going forward.

## Would this have misled the implementing agent? no

Nothing CodeCompass actually asserted was false, and its honest "not yet
enriched" / empty-result labelling (rather than a fabricated summary or a
silently-wrong claim) meant an agent relying on it would never have been
steered toward an incorrect belief about `cur:`'s semantics — it would
simply have gotten less help than expected on the task's hardest
questions and had to do the real work (reading `models.py`, reading the
`tag:` precedent, reading hledger's actual manual/source) by hand, which
is exactly what both dispatched agents in fact did. The risk here is
**under-delivery, not misdirection** — a real difference this report
treats as material for the verdict (PASS WITH GAPS, not FAIL) but not as
"misleading."

---

## Lead gap analysis (Part 6 dimensions)

Written after both dispatched reports and the independent
`context-evaluator` verdict above were in hand. Each dimension is judged
against what CodeCompass actually surfaced, not what either agent
happened to find by hand.

- **Relevant docs/design material.** Adequate-but-incomplete. The one
  `query relations` call surfaced 11 real, mostly on-topic docs, but
  missed `07-query-regex.md` — the single doc with the literal `cur:`
  table row — for the structural reason `context-evaluator` names (no
  citation string exists for a title/filename matcher to find). A plain
  `grep -rl "cur:" dev-docs/` or an `ls` of the self-descriptively
  numbered `core-redefinition/` directory gets there faster and more
  completely.
- **Relevant tests as evidence.** No contribution either way. Neither
  agent used or needed a CodeCompass surface to find the query test
  suite — both located it by directory convention
  (`find tests -path "*query*"`), the same way any fresh agent would.
  CodeCompass has no query-to-test-coverage mapping at all.
- **Producers/consumers.** No contribution. CodeCompass has no
  representation of which code produces/consumes `Posting`/`Amount` —
  confirmed live, `query symbol` empty for both. This was answered
  entirely by reading `ledgerkit/models.py` directly.
- **Sibling implementations.** No contribution. The `tag:` precedent
  (the correct structural analog for `cur:`) was found by both agents
  via grep across `ledgerkit/query/`, not via any CodeCompass surface —
  CodeCompass's `query relations` returned some of the `tag:`-family
  *design docs* (a citation-graph hit) but never pointed at `tag:`'s own
  *code* (`ast.py`/`parser.py`/`eval.py`) as the implementation
  precedent, because it has no code-to-code sibling-implementation
  relation of any kind.
- **Execution/behavioural path** (entry point → parser/IR →
  interpretation/evaluation → observable output). No contribution.
  Tracing `-q`/`--query` → `parser.py` → `ast.py` → `eval.py` →
  `balance`/`register` output was done entirely by hand in both runs;
  CodeCompass has no execution-path or call-graph representation for a
  project's own first-party source at all. **This gap substantially
  matches `CG-007`'s own named shape** (symbol-level/execution-path
  cross-reference has no representable relation kind) — though `CG-007`
  was originally filed against `spec_doc`-excerpt-to-`spec_doc`-excerpt
  linkage (externally-pinned reference material), and this instance is
  project-own-source-to-project-own-source, which is `CG-009`'s
  territory (no symbols exist for either side to link in the first
  place) even before `CG-007`'s missing-relation-kind problem would
  apply. **Conclusion: this instance is better explained by `CG-009`
  (no first-party symbols exist to link) than by `CG-007` (a relation
  kind is missing between symbols that do exist)** — `CG-007` remains
  about a narrower, still-unconfirmed-a-second-time case (pinned
  reference-doc excerpts specifically), not the general case this task
  exercised.
- **Task-oriented relevance** (relevant-to-this-task vs.
  merely-present-in-the-graph). Weak. `query relations` returned a
  citation-graph result, not a task-relevance-ranked one — it could not,
  and did not, distinguish "this doc is central to `cur:`" from "this
  doc happens to be cited by the one doc I queried." **This gap
  substantially matches `CG-001`'s own named hypothesis** (§2.6,
  "task-oriented retrieval needs new edges, not just joins") — see
  disposition below.
- **Explicit uncertainty.** CodeCompass made its own limits obvious in
  the technical-core case (`query symbol` returned an explicit "not
  found" error, not silence or a fabricated answer) — an agent could not
  mistake this for "there is nothing to know here." It did *not* make
  the `07-query-regex.md` omission obvious at all: `query relations`
  returned a plausible-looking, non-empty 11-row result, with nothing
  flagging that a more directly relevant document existed outside that
  result set. This asymmetry (loud absence for symbols, silent
  incompleteness for relations) is itself worth naming: the tool is
  honest about *known* absence but cannot signal *unknown* incompleteness
  in a relational result.
- **Rediscovery burden.** Once the `L-027` agent-diligence-variance
  confound is separated out (per `context-evaluator`'s finding 1 above),
  the treatment run needed essentially the same manual rediscovery as
  baseline for every one of the task's hard parts (reading
  `models.py`, reading `tag:`'s implementation, reading/fetching
  hledger's real manual or source) — CodeCompass eliminated no
  rediscovery work on the task's substantive core, and saved at most a
  few minutes of doc triage on the periphery, an amount `context-evaluator`
  found a single grep matches or beats.

## `CG-001` / `CG-007` / `CG-009` disposition

**`CG-001` (task-oriented retrieval — "relevant to this task" vs.
"present in the graph") — final status: stays `candidate`.** *(Addendum,
2026-09-28: this section originally recommended moving `CG-001` to
`recurred` on this phase's evidence. `knowledge-curator`'s own
independent same-phase triage reviewed that call and reversed it, and
the lead has reviewed and concurred with the reversal — see
`planning/context-gaps/inbox.md`'s own `CG-001` entry, which is the
single authoritative record of this decision. The reasoning below is
left as written, for the historical record of what this report
originally argued, but the final outcome is the one stated in this
addendum, not the "moved to `recurred`" conclusion the original
paragraph reaches.)* The original argument: this phase produced a
third, and by far the most concrete, instance of the exact §2.6
hypothesis: a live, independently-reproduced case where the one
task-relevant document (`07-query-regex.md`) was invisible to
CodeCompass's only relevant surface despite being topically
inseparable from the query CodeCompass actually answered. `knowledge-curator`'s
own reversal reasoning: this report's own text (immediately above, in
the "Context advantage: LOW" section) had already characterized this as
"noted here as a second, independent instance... not filed as its own
new `CG-NNN`" and explicitly invoked "the precedent `CG-001`'s own
curation notes already set (a second instance of the same hypothesis on
a different concrete edge is recorded as a cross-reference, not a
promotion to `recurred`)" — the disposition section below then
contradicted that same report's own earlier section without new
justification tied to `context-gaps/README.md`'s actual recurrence bar,
which every one of `CG-001`'s three prior curation passes (Phase 43c,
47, 72) applied consistently (same edge recurring, not merely a
stronger instance of the same broader hypothesis). The Phase 75 finding
is retained as a valuable third cross-reference for the general §2.6
hypothesis, not promoted to `recurred` on it alone.

**`CG-007` (symbol-level cross-reference between externally-pinned
reference-doc excerpts) — unchanged, stays `candidate`.** This phase's
task never exercised `spec_doc`-to-`spec_doc` excerpt linkage (no
pinned external reference material was ingested this run) — no new
evidence for or against this entry's specific mechanism. The
project-own-source execution-path gap this task *did* surface is a
different, broader mechanism (see `CG-009` below and the
execution/behavioural-path analysis above), not a second occurrence of
`CG-007`'s narrower pinned-excerpt case. Still single-occurrence,
unpromoted.

**`CG-009` (no first-party-source symbol index, filed this phase by
`context-evaluator`) — the dominant explanatory gap for this task's
technical core, but not recommended for immediate funding either.**
It fully explains why CodeCompass contributed nothing to the two
hardest of the five required questions. But per `context-evaluator`'s
own finding 3, even this gap's fix would have saved at most one file
read (`models.py` answers the question completely and immediately by
hand) — the fix is also architecturally non-trivial (a schema change:
`symbols.vendor_id` is `NOT NULL`-FK-constrained to `vendors`, so
representing "the project's own symbols" needs either a nullable FK or
a synthetic always-present project row, a real design question, not a
one-line change). Pending `knowledge-curator` triage per the standard
context-gap lifecycle.

**Overall, per the user's own explicit instruction** ("if a different,
smaller gap explains most of the observed disadvantage, prefer that
smaller fix"): no single gap here clears the bar of "clearly worth
building and clearly better than existing plain tools" on the evidence
this one trial produced. `CG-009` explains the *size* of the technical
gap; `CG-001` explains the *shape* of the relational gap; but
`context-evaluator`'s own repeated finding — a plain grep/ls already
matches or beats CodeCompass's one genuine contribution on this task —
means neither is yet a well-evidenced "build this" case on its own.

## Next-phase recommendation

**Outcome, per the user's own named options: closest to Outcome E
("current CodeCompass adds little value — record honestly, reconsider
Priority A approach before adding architecture"), tempered by this
project's own standing `L-027` single-trial discipline** (a lone N=1
trial cannot license either full abandonment of Priority A or funding a
specific fix — both would over-read one data point). The honest
reading: for a task whose substantive difficulty lives in a project's
own first-party source and an external upstream binary/manual, neither
of which CodeCompass's current model (vendor-symbol index + doc-citation
graph) targets, current CodeCompass measurably under-delivered relative
to plain repository tools (LOW advantage, PASS WITH GAPS) — but this is
one task, one project, one trial, and this project's own
`context-gaps/README.md` recurrence discipline explicitly exists to
prevent committing architecture on less evidence than this.

**Recommended Phase 76: a second, differently-shaped Priority A
validation trial** — not a Priority A capability build, and not
abandonment of Priority A. Deliberately choose a task next time that
stresses a *different* one of the two candidate gaps more cleanly than
this task did:
- either a task inside **CodeCompass's own source** (where `CG-001`'s
  original motivating shape — one feature spread across `src/`
  modules — actually lives, and where "just grep/ls the directory" is
  demonstrably *not* how this project's own Phase 43 CLI-widening work
  found its own multi-module coordination need), or
- a task requiring genuine **cross-file symbol/execution tracing** in a
  reference project with a less self-descriptively-organized doc corpus
  than Ledgerkit's `core-redefinition/NN-title.md` convention (which
  itself may be part of why a plain `ls` did so well this trial).

If a second trial also shows LOW advantage under the same rigor
(independent `context-evaluator` ground-truthing, explicit `L-027`
confound check), that is sufficient evidence to formally deprioritize
Priority A relative to Priorities B-F — several of which
(`decisions/0062`) already have stronger internal evidence of proven
value (Priority E's `context-evaluator`/independent-evaluation
discipline, notably, just outperformed both dispatched agents in *this
very phase* — it caught the `L-027` confound, found a more decisive
fact than either agent via more careful primary-source reading, and
named a real structural gap neither agent's own report surfaced by
itself). If a second trial instead shows real, demonstrated advantage,
that licenses moving `CG-001`/`CG-009` into an actual funding decision
with real, now-doubled evidence behind it — Outcome A/B territory,
decided by that trial's own results, not pre-committed here.

**Is current CodeCompass ready for routine Ledgerkit use today?**
Conditionally: yes for doc-discovery triage on a large, unfamiliar
`dev-docs/` tree (its one genuinely-useful, honestly-labelled surface),
no as a substitute for reading a project's own source or its upstream
reference material directly — an agent should keep doing exactly what
both dispatched agents in fact did for those two things.
