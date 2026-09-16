# Context-quality evaluation — Ledgerkit `tag:` query semantics brief (Phase 54, baseline vs. treatment)

## Setup

- **Reference project:** Ledgerkit, `/home/cormac/projects/ledgerkit` (real, independently-developed clone)
- **Pinned commit:** `05218e3acced83dd8e980206668ca5ee83ebf103` (confirmed live == `origin/main` at inspection time)
- **hledger reference source:** `/home/cormac/projects/hledger`, confirmed at `33fa849e7ae841968bd21c427094c4fb4a4ec38d` (tags `1.52.4`/`hledger-1.52.4`/`hledger-lib-1.52.4`)
- **CodeCompass revision:** working tree at `72961e0` (post-Phase-53)
- **Task:** produce an `hledger-researcher`-shaped semantics brief + proposed compat-register evidence for Ledgerkit's Stage C `tag:` query term (explicitly deferred, confirmed live in `ROADMAP.md` line 285 and `dev-docs/hledger-compatibility.md:218`), run twice — once with today's real manual `WebFetch`/`grep` workflow (baseline), once using only the Phase 54 ingestion pipeline's CodeCompass-queryable extracted material (treatment).
- **Context supplied:** see `baseline-tag-query-brief.md` and `treatment-tag-query-brief.md` in this directory (read verbatim; not restated here).

## Independent findings (ground truth, not the briefs' self-report)

1. **Baseline's claimed WebFetch omission is real.** `hledger.1:7372-7394` / `hledger.m4.md:5798-5808` contain three inheritance bullets: accounts inherit from parent accounts (line 7390), postings inherit from account+transaction (7392), transactions acquire from postings (7394). The baseline's quoted WebFetch output lists only two of these (splitting the postings rule into two and omitting the account-level rule entirely) — the baseline's write-up of "what was and wasn't captured" is accurate.
2. **Extraction byte-accuracy: 5 of 6 confirmed exact, 1 has a real defect.** Diffed `hledger-tag-query-parser.md`, `-account-match.md`, `-posting-match.md`, `-transaction-match.md`, `-pattern-match.md` against the live pinned source at their declared line ranges — all five are byte-identical, and all eight `references.lock` SHA-256 hashes (including the two `date-query-*` files) were independently recomputed from the real source and matched exactly. **`hledger-tag-query-manual.md` is the defect**: its declared range (`hledger.1:7372-7392`) is byte-accurate to that range, but that range **excludes lines 7393–7394**, which contain the third inheritance rule ("Transactions also acquire the tags of their postings"). The file's own frontmatter description nonetheless claims "the three inheritance rules (accounts from parents, postings from account+transaction, **transactions from postings**)" are in this excerpt — they are not; only two of three are. The treatment brief compounds this, stating as fact that the ingested material has "all three inheritance rules present and precise... verbatim" — independently false; the third rule is absent from the artifact actually queried.
3. **"Zero mechanical relations" claim confirmed true by direct code reading**, not by trusting the write-up. `spec_docs.py::scan_spec_docs` always constructs `DocArtifactRow(..., name=None)` (never passes `name=`); `DocArtifactRow.name` defaults to `None`; `doc_mapping.py`'s own docstring states "a doc artifact with no `name` set is never a match target." A `spec_doc`-kind row can never populate `name`, so `mentions_artifact` can never fire for it — both briefs' claim is mechanically correct, independently re-derived.
4. **Evidence-matching fallback is real, not asserted.** Read `LK-COMPAT-QUERY-DATE-001.yaml` directly: its `evidence.ref` citations are exactly `hledger-lib/Hledger/Data/Dates.hs:429` and `1132-1148`, matching the treatment's claim verbatim. Ran the experiment's own test suite directly (`pytest .../tests/test_reference_pipeline.py`, not trusting its report): 12/12 pass, including `test_match_compat_register_evidence_finds_real_overlap`, confirming the fallback mechanism is real and works as described.
5. **Usability for a real `LK-COMPAT-QUERY-TAG-001.yaml`:** both briefs reach the same correct substantive answer (syntax, infix matching, `payee`/`note` synthetic-tag framing, three-way inheritance, `parseTag`/`matchesAccountExtra`/`matchesPosting`/`matchesTransaction`/`patternsMatchTags` citations) and both correctly flag the still-open `compatible` vs. `unsupported` classification question pending Ledgerkit's own `ledgerkit/query/parser.py` (matches `dev-docs/hledger-compatibility.md:218`, "Not implemented"). Neither brief consults hledger's own test suite, which `hledger-researcher.md` step 2/4 explicitly calls for — a shared, undisclosed gap in both, not a differentiator.

## Criteria assessment

| Criterion | Baseline | Treatment | Notes |
|---|---|---|---|
| Accuracy | adequate | **weak** | Baseline's substantive claims are correct; its citation range is a forgivable ±2-line human approximation, self-disclosed as imprecise (via the flagged WebFetch gap). Treatment's citation is machine-generated with a SHA-256 "trust without re-checking" provenance guarantee, yet its own description over-claims what the hashed range contains — a false completeness claim in the artifact itself. |
| Relevance | strong | strong | Both directly on-task. |
| Completeness | adequate | adequate | Both miss hledger's own test-suite consultation; otherwise both cover syntax, matching semantics, and inheritance. |
| Freshness | strong | strong | Both correctly pinned at the confirmed live commit/tag. |
| Grounding/provenance | adequate | **weak** | Baseline citations are traceable but approximate. Treatment citations look more precise (hash + commit + line range) but that precision is what makes the manual excerpt's false "all three rules" claim more actively misleading — it invites trust that isn't warranted. |
| Noise | strong | strong | Neither is bloated. |
| Trustworthiness | adequate | **weak** | Baseline is honest about its own gap. Treatment presents a false completeness claim about its own trusted artifact without disclosing it — precisely the "confidently wrong, presented authoritatively" failure mode. |

## Verdict — Baseline: PASS WITH GAPS

Substantively correct and self-aware of its own limitation (the WebFetch account-rule omission is disclosed, not hidden), with only a minor, disclosed citation-precision gap. No misleading claim is presented as authoritative.

## Verdict — Treatment: FAIL

The ingested material's own frontmatter/description for `hledger-tag-query-manual.md` claims a fact about its own content ("the three inheritance rules... present") that is independently false — only two of three are in the excerpt the pipeline actually indexed and hashed. The treatment brief repeats this as an unqualified claim ("all three inheritance rules present and precise... verbatim"), and the experiment's own methodology explicitly requires disclosing any fallback beyond the ingested material (§4 of the plan) — no such disclosure appears, so the final brief's correct three-rule answer is not actually traceable to anything the treatment run says it used. Per the evaluation's own ground rule, a confidently-wrong claim presented authoritatively outranks an otherwise-strong result (accurate hashes for 7 of 8 selections, a real and independently-verified evidence-matching fallback, a correctly-derived "zero relations" finding).

## Context advantage: LOW

Could a fresh Claude session have gotten equivalent context cheaply? **Yes** — the baseline shows exactly that: one `WebFetch` plus one `grep` plus reading two line ranges produced a materially correct, self-aware brief in "two tool calls." The treatment's pre-extraction/hashing saves a live network call and a manual line-number lookup, but that convenience is offset by a real, undisclosed accuracy defect the cheap manual path did not have (the manual `grep`, read directly, would show the researcher the full three-bullet list in context; the pre-sliced excerpt hides the third bullet behind a wrong summary line). Net: no material advantage over the existing workflow on this task, and a new failure mode the existing workflow lacks.

## Material gaps / failures

- `hledger-tag-query-manual.md`'s declared range (`hledger.1:7372-7392`) excludes the third tag-inheritance rule (lines 7393-7394); its own description falsely claims all three are present — candidate learning: extraction line-range selection must be validated against what the accompanying description claims, not hand-picked from a partial re-read of the section.
- Neither brief consults hledger's own test suite, contrary to `hledger-researcher.md` step 2/4 — shared gap, not treatment-specific.
- The treatment run's "identical in substance" resulting brief does not disclose that its correct three-rule answer required information outside the artifacts it says it used exclusively — an experimental-discipline gap, not just a content gap.
- Neither brief checks Ledgerkit's own `ledgerkit/query/parser.py` to confirm the `compatible`-vs-`unsupported` classification — both correctly flag this as open, so it's a disclosed gap, not a defect.

## Would this have misled the implementing agent? yes (treatment) / no (baseline)

**Treatment: yes, partially.** A real `hledger-researcher`-equivalent trusting the pre-extracted, hashed `hledger-tag-query-manual.md` file as sufficient (the whole point of pre-extraction) would believe the manual excerpt already substantiates all three inheritance rules and could cite `hledger.1:7372-7392` for a `LK-COMPAT-QUERY-TAG-001.yaml` evidence block describing all three — an evidence citation that does not actually cover the third rule. **Baseline: no** — its self-disclosed WebFetch gap is corrected within the same brief before the citation is finalized, and its final evidence block is materially sound.
