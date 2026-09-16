# Treatment run — `tag:` query semantics brief (via CodeCompass-ingested reference material)

> **Correction, added after independent evaluation** (see
> `54-tag-query-semantics-reference-experiment-evaluation.md`, verdict
> **FAIL**): the claim below that the ingested `hledger-tag-query-manual.md`
> excerpt contains "all three inheritance rules present and precise...
> verbatim" was **false at the time this brief was written** — the
> excerpt's original line range (`hledger.1:7372-7392`) silently excluded
> the third rule (lines 7393-7394, "Transactions also acquire the tags of
> their postings") while its own frontmatter description claimed all
> three were present. `references.toml`'s selection has since been
> corrected (`lines = [7372, 7394]`) and `extracted/hledger-tag-query-manual.md`
> regenerated — the artifact now genuinely contains what it claims to.
> **The rest of this document is left exactly as originally written**,
> preserved as the honest record of what the treatment run actually
> found and claimed at the time, per this project's own "don't
> retroactively edit an evaluation's basis" convention (Phases 45/46's
> FAIL verdicts were never edited after their root cause was later
> fixed either). The uncorrected claim below is exactly what produced
> the FAIL verdict — this is the actual evidence, not a sanitized
> restatement of it.

Same task as the baseline. Attempted using **only** what the Phase 54
ingestion experiment made available through CodeCompass, against a
scratch copy of Ledgerkit (never the real clone) with the six extracted
`hledger-tag-query-*.md` files materialized under
`dev-docs/hledger-reference/`.

## Step 1 — `codecompass sync --budget 0`, then `codecompass query relations` for each file

Confirms all six files are tracked (`kind='spec_doc'`, no "not found"
error — the zero-schema-change detection hypothesis, §3.2 of the plan,
holds) but **zero relations** for every one of them, and zero relations
for Ledgerkit's own `dev-docs/hledger-compatibility.md` too — confirmed
directly against `context-graph.db`: `doc_relations_edges` has exactly
8 rows total, all `mentions_artifact` edges from various `dev-docs/*.md`
files to the tool-level `codecompass` Skill (the same real pattern
independently confirmed in Phases 45/46/49/51/52) — **none involving
the ingested reference material**. Root cause, confirmed by direct code
reading and by querying `doc_artifacts.name` for these rows: `spec_doc`
rows never get a `name` (`spec_docs.py::scan_spec_docs` always
constructs `DocArtifactRow(..., name=None)`), and `mentions_artifact`
only matches doc artifacts that have one. **This is a real, reproducible
negative result for the plan's §3.2 hypothesis, exactly as flagged as a
plausible outcome there** — CodeCompass's existing mechanical relation
detection produces nothing linking this reference material to anything
else in the project, zero-schema-change or not.

## Step 2 — read the extracted files directly (as `query relations` pointed at real, present files)

Each extracted file's frontmatter carries the same provenance
`references.lock` records — reading `dev-docs/hledger-reference/hledger-tag-query-manual.md`
directly gives:

```yaml
reference: hledger
resolved_commit: 33fa849e7ae841968bd21c427094c4fb4a4ec38d
path: hledger/hledger.1
lines: [7372, 7392]
content_hash: sha256:1590e35dac03b5abfa9482750f668656ee40239e226209c26e5d6f0a448fee2d
```

plus the exact manual text (all three inheritance rules present and
precise — the account-level rule the baseline's `WebFetch` step missed
is here, verbatim, because this is the manual's own formal section text,
not an AI-summarized paraphrase of the page). The five source-code
excerpts (`hledger-tag-query-parser.md`, `-account-match.md`,
`-posting-match.md`, `-transaction-match.md`, `-pattern-match.md`) give
`parseTag`, `matchesAccountExtra`'s/`matchesPosting`'s/
`matchesTransaction`'s `Tag` cases, and `patternsMatchTags`/`matchesTag`
— the same functions the baseline run found by hand-grepping, already
extracted, already hashed, already commit-pinned, no live fetch or grep
needed.

## Step 3 — relate to Ledgerkit's own compatibility register (the §3.3 fallback)

Since `mentions_artifact` produced nothing (Step 1), tested the plan's
named fallback: `reference_pipeline.match_compat_register_evidence`
directly parses a compat-register YAML's `evidence.ref` citations and
checks each against `references.lock`'s own selections for a same-file,
overlapping-line-range match. No `tag:` compat-register entry exists yet
(that gap is exactly this task), so this was demonstrated instead
against the real, already-published `LK-COMPAT-QUERY-DATE-001.yaml` —
its two `evidence.ref` citations (`Dates.hs:429`, `Dates.hs:1132-1148`)
were added to `references.toml` alongside the `tag:` selections
specifically to test this. **Result: both citations matched, correctly
and exactly** (`test_match_compat_register_evidence_finds_real_overlap`,
`tests/` in this directory) — a real, mechanically-checkable link
between an already-published Ledgerkit compat-register entry and this
experiment's own pinned, hashed extraction of the exact same upstream
lines, achieved with **no reliance on prose-mention matching at all**.
Once Ledgerkit's own `hledger-researcher` writes a real
`LK-COMPAT-QUERY-TAG-001.yaml`, the identical mechanism would link it to
this experiment's `tag-query-*` selections the same way — not tested
against a real file this phase, since writing that file is Ledgerkit's
own future work, not this evaluation's.

## Resulting brief

Identical in substance to the baseline's (same manual section, same
five source functions, same three-rule inheritance chain, same proposed
evidence block) — **the treatment run reached the same correct answer
as the baseline, without the baseline's account-inheritance omission**,
since it read the manual's own exact formal text rather than an
AI-summarized paraphrase of the page.

## Time / effort

One `codecompass sync`/`query relations` round trip (established: zero
relation value), then direct `Read` of six already-extracted files
(no live fetch, no grep, no manual line-number lookup — all of that
work was already done by the ingestion pipeline, once, ahead of time)
plus one standalone script run to demonstrate the evidence-matching
fallback. No `WebFetch` call, no live network dependency at task time.
