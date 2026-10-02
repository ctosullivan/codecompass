# Context-quality evaluation — Ledgerkit Stage D `ReportSpec` journal-comment parsing (Phase 78, Priority A second trial, Stage 2)

Independent `context-evaluator` assessment. Ground truth established by
reading the real target repository and by re-running CodeCompass queries
directly against the synced treatment clone myself — never by trusting
either dispatched agent's self-report, per
`context-quality-evaluation.md` §1 and the Phase 77 precedent this phase's
own plan (`planning/phase-78-priority-a-closeout-and-second-ledgerkit-trial.md`
§5.3.2) explicitly invokes.

## Setup

- **Reference project:** Ledgerkit (local clone of
  `/home/cormac/projects/ledgerkit`), forked into two scratch clones.
- **Pinned commit:** `6c90b4ca3e6c10951cb400e43db4b90bfccc5909` (identical
  commit Phase 77's own trial used; re-verified unchanged at dispatch
  time). Confirmed directly: `git rev-parse HEAD` in
  `.../scratchpad/ledgerkit-treatment` returns this exact SHA.
- **CodeCompass revision:** HEAD at Phase 78's dispatch time
  (`012a92a` base + Phase 78's own in-progress commits; Phases 73-77
  `done`). Treatment clone's `context-graph.db` was synced from this
  revision per `06-fixture-equivalence.md`.
- **Task (Stage 1, discovery/design only):** "Ledgerkit's own
  `dev-docs/api-spec.md` marks journal-comment-based `ReportSpec` parsing
  (`; report` / `; end report` syntax) `[DEFERRED — Milestone 3]`;
  `ROADMAP.md` reclassifies it to Stage D (Reporting), not yet started.
  Investigate this repository and produce: relevant existing source, the
  producer/consumer relationships a real implementation would need to
  respect, the end-to-end execution path, existing vs. net-new test
  coverage, relevant docs, open design questions, and a proposed design.
  Discovery/design only — no implementation." Identical wording, baseline
  (`ledgerkit-baseline`, ordinary tools only) vs. treatment
  (`ledgerkit-treatment`, plus `codecompass query source` / `query
  source-symbol` / `query relations` / `query symbol` / `query vendor` /
  `check`, synced Skill). Read-scope symmetry confirmed for both arms by
  the boundary-check files (`06-stage-d-reportspec-stage1-{baseline,
  treatment}-boundary-check.md`).
- **Context CodeCompass supplied (verbatim, independently re-run by me and
  confirmed identical to the treatment agent's own reported output):**
  - `query source-symbol ReportSpec` → one row, `ledgerkit/models.py`
    class, line 219, `public`, full docstring ending "...is deferred to
    Milestone 3." (confirmed byte-for-byte against the live file's real
    docstring — the stale "Milestone 3" wording is the *source's own*
    staleness, accurately echoed, not a CodeCompass error).
  - `query source-symbol balance_from_spec` → one row, `ledgerkit/
    reports.py`, function, line 600, `public`, full docstring (matches
    live source).
  - `query source ledgerkit/cli.py` → full symbol index (`_fmt_amount`,
    `_fmt_balance`, `_abbreviate_account`, `_build_parser`,
    `_resolve_files`, `main`) — confirmed by direct `grep`/read: no
    `report`-command or `ReportSpec`/`balance_from_spec` reference
    anywhere in `cli.py`.
  - `query source ledgerkit/reports.py` → full symbol index confirming
    `balance_from_spec` is the only `ReportSpec`/`ReportSection`-aware
    function in the file.
  - `query relations ReportSpec` → `error: 'ReportSpec' not found in
    context-graph.db` (exit 1) — **re-ran myself, identical result.**
  - `query relations balance_from_spec` → `error: 'balance_from_spec' not
    found in context-graph.db` (exit 1) — **re-ran myself, identical
    result.**
  - `query symbol ReportSpec` → `no symbol named 'ReportSpec' found...`
    (exit 0) — **re-ran myself, identical result.**
  - `query vendor hledger` → `error: 'hledger' not found...` (exit 1) —
    **re-ran myself, identical result.**
  - `query relations --help` → confirms (re-read myself) the surface is
    scoped to `doc_relations_edges` (spec-doc ↔ vendor ↔ Skill mechanical
    mentions) plus a "Package code" vendor-usage trace — **not** a
    symbol-to-symbol or caller/callee relationship lookup of any kind.
  - `query relations dev-docs/api-spec.md` → a doc-mention table, all
    rows "mentioned, not yet enriched"; no `ReportSpec`-specific content.
  - `check` → clean graph, no unused/undocumented vendor findings, four
    unrelated "spec docs with no detected relations," none of the three
    docs relevant to this task.

## Criteria assessment (per `context-quality-evaluation.md` §3)

| Criterion | Rating | Notes |
|---|---|---|
| Accuracy | **Strong** | Every CodeCompass claim I independently re-ran matched live source exactly: the `ReportSpec` docstring (verbatim, including the stale "Milestone 3" line, which is the *source's* own staleness, not a misrepresentation), `balance_from_spec`'s signature/line/docstring, `cli.py`'s six-symbol index (confirmed zero `report`-related code via direct `grep`), and every error case (`query relations`/`query symbol`/`query vendor` correctly report "not found" rather than fabricating a false positive). Zero affirmatively wrong claims found. |
| Relevance | **Adequate** | The four working queries (`source-symbol ReportSpec`/`balance_from_spec`, `source cli.py`/`reports.py`) pointed precisely at the real consumer machinery for this exact task, not generic output. |
| Completeness | **Weak on the relationship dimension specifically, otherwise adequate** | `query relations`/`query symbol`/`query vendor` could not answer "which functions in `reports.py`/`cli.py` reference `ReportSpec`, and which do not yet call `balance_from_spec`" at all — confirmed by me re-running both calls (exit 1, "not found"). This is a disclosed, structural gap (Phase 78 plan §0: zero first-party-symbol edge tables exist in the schema), not a surprise. The agent still obtained the full, correct answer, but entirely through direct reading, exactly as the baseline arm did. |
| Freshness | **Strong** | Content hash matched the live file at the pinned commit; no staleness in CodeCompass's own index — the one piece of "stale" content surfaced (`ReportSpec`'s "Milestone 3" docstring) is the real source's own staleness relative to `ROADMAP.md`, correctly and transparently reflected rather than silently reconciled. |
| Grounding / provenance | **Strong** | Every claim traceable to an exact file/line (`models.py:219`, `reports.py:600`) via the query output itself. |
| Noise | **Strong** | Compact, single-purpose tables; no irrelevant clutter. |
| Safety / trustworthiness | **Strong** | No incorrect or misleading claim presented as authoritative. Errors are explicit ("not found"), never silent false negatives dressed as confirmation. |

## `CG-001` three-outcome verdict (§4 of the Phase 78 plan)

**Applicability — confirmed, not Outcome 3.** The task genuinely required
tracing a real producer/consumer chain: both agents' own §2 sections
independently derived the identical chain — `parser.py` (new producer,
must intercept inside the existing unconditionally-discarding comment-line
branch) → `models.py`/`Journal` (new storage field) → `loader.py`
(`merge_journals` must be extended) → `reports.py::balance_from_spec`
(existing, unchanged consumer) → `cli.py` (new consumer, does not exist
today). This is exactly `CG-001`'s founding shape, confirmed by direct
reading of `ledgerkit/parser.py` lines 985–1109 (verified by me: a
column-0 `;`/`#` line matches `stripped.startswith(";") or
stripped.startswith("#")`, and unless it is an indented follow-on under an
open `account`/`commodity`/transaction, falls through unconditionally to
the final `continue` — both reports' "always silently skipped" claim is
exactly right) and `ledgerkit/cli.py` (`COMMANDS` tuple has no `report`
entry; `balance_from_spec` is referenced nowhere in the file — confirmed
by `grep`).

**Outcome: `not-recurred`.**

Evidence:

1. **CodeCompass's existing surfaces genuinely could not answer the
   relationship question, even in combination** — confirmed directly by
   me, not just by the treatment agent's own trace: `query relations
   ReportSpec` and `query relations balance_from_spec` both error
   `'...' not found in context-graph.db` (exit 1); `query relations
   --help` confirms the surface is scoped only to
   spec-doc↔vendor↔Skill mechanical mentions (`doc_relations_edges`),
   with no first-party symbol-to-symbol or caller/callee edge of any
   kind — matching the Phase 78 plan's own §0 schema finding verbatim
   (no edge table exists between two `source_symbols` rows anywhere).
2. **Despite this, the treatment agent reconstructed the identical,
   correct chain at a cost no worse than the baseline's own direct
   exploration.** Both arms read the same decisive files directly
   (`models.py`, `reports.py`, `parser.py`'s main loop at the same
   ~955–1240 line range, `cli.py`) and produced comparably thorough
   reports (744 vs. 772 lines; 8 vs. 6 open design questions; near-
   identical §2 producer/consumer diagrams reaching the same
   conclusions independently). The treatment agent's own trace shows
   it had already derived the full chain via direct reading *before*
   running any CodeCompass query (the queries appear at the end of its
   own research-trace listing and are themselves described, correctly
   on independent cross-check, as confirmation rather than discovery:
   content-hash/index-currency checks that added no new fact beyond
   what direct reading had already established). This satisfies §4
   Outcome 2's bar exactly: "the chain-tracing step was completed with
   existing surfaces at a cost no worse than the baseline's own direct
   exploration."
3. **No material, avoidable cost was imposed on the treatment arm by
   the tooling gap.** The two failed `query relations` calls (entries 3
   and 4 in the treatment's own trace) were a self-corrected,
   few-seconds-cost mistaken assumption about tool scope, not a
   material investigative dead-end — the agent read `query relations
   --help`, corrected course immediately, and lost no net ground. Each
   arm also independently surfaced one finding the other missed
   (baseline: `merge_journals`'s pre-existing `declared_account_tags`/
   `declared_commodity_tags` omission, confirmed real by me reading
   `loader.py:239-248`; treatment: the open question of whether `;
   report` is a real hledger construct or a Ledgerkit-native
   extension) — classic agent-diligence variance (`L-027`), not a
   tooling-caused asymmetry, since both arms had identical raw-source
   access to both findings.

This is this entry's second, genuinely separate instance of the
hypothesis (different project, different concrete chain, independent
observer) — evidenced, applicable, and resolved in the negative. Per §4
this is a real, usable data point for `not-recurred`, not a repeat of the
prior evidence-neutral/reverted calls from Phase 75.

## Verdict: PASS WITH GAPS

No incorrect or misleading claim was found anywhere in CodeCompass's
supplied context (every claim I independently re-checked against live
source was accurate, including its own correct echo of the source's own
stale docstring). The material gap — no first-party symbol-relationship
capability, so the producer/consumer/caller question had to be answered
entirely by direct reading — is a known, already-disclosed boundary
(Phase 77's own deferred item), not a surprise defect, and did not impose
a materially higher cost than the baseline's own ordinary exploration.
This matches the definition of PASS WITH GAPS exactly: trustworthy but
incomplete on one specific, already-named dimension.

## Context advantage: LOW

**Could a competent fresh Claude session have obtained equivalent context
trivially through ordinary repository inspection?** Yes. Every fact
CodeCompass's working queries supplied (`ReportSpec`/`ReportSection`'s
shape, `balance_from_spec`'s signature, `cli.py`'s symbol list) is
directly visible in two or three full-file reads of `models.py`,
`reports.py`, and `cli.py` — which both arms in fact performed, at
comparable total effort (the treatment agent's own research trace shows
its CodeCompass queries came after, and merely confirmed, work already
done by direct reading). On the one dimension (`CG-001`'s relationship
question) where CodeCompass could have added genuine, hard-to-replicate
value, it returned nothing usable (`query relations` errored for both
symbols queried) — so the one place a MODERATE/HIGH rating might have
been earned is exactly where the tool came up empty, and the agent fell
back to the same direct reading the baseline used. This is a small,
well-organised codebase (Ledgerkit's own established profile across
Phases 75/77), which is the honest, expected setting for a LOW result,
not a failure to hide.

## Material gaps / failures

- **No first-party symbol-relationship/caller-graph capability exists**
  (confirmed directly: `query relations`/`query symbol`/`query vendor`
  all fail for first-party symbols; the schema has no edge table between
  two `source_symbols` rows). This is `CG-001`'s own named gap,
  re-confirmed on a second, independent instance — already tracked, not
  a new finding, and (per this trial's own `not-recurred` result) does
  not, by itself, justify building the capability.
- `query relations <doc-path>` cannot surface a doc's *content* relevant
  to an unimplemented feature (e.g. `dev-docs/api-spec.md`'s own
  `[DEFERRED]` note) — only mechanical doc-to-doc/vendor mentions. Both
  arms found the relevant doc lines via direct `grep`/read instead. A
  Completeness gap, not a Safety one — consistent with prior trials.
- Minor, self-corrected efficiency loss: two `query relations` calls
  against first-party symbols before checking `--help` (treatment's own
  trace entries 3–4) — immaterial, already disclosed by the agent itself,
  does not change the verdict.

## Would this have misled the implementing agent? no

Every CodeCompass claim I independently verified against live source was
accurate, including its correct, transparent echo of the source's own
stale docstring (not a false claim of currency). Every failure mode
(`query relations`/`query symbol`/`query vendor` against a first-party
symbol) surfaced as an explicit, unambiguous error — never a silent false
negative or a confidently wrong positive — so there is no path by which
an implementing agent could have been led to a wrong conclusion by
trusting CodeCompass's output here.

## Stage 3 decision (my own call, per plan §5.3.2/§8): do not run

Stage 3 (shared-contract implementation check) is not warranted. Reasons:

1. The `CG-001` question — this trial's entire reason for existing — is
   already decisively answered at Stage 1, with direct, independently
   re-run evidence (`query relations` erroring for both `ReportSpec` and
   `balance_from_spec`, combined with both arms completing the chain at
   equal cost). Implementation-stage work would exercise the *same*
   structural gap (no symbol-relationship edges) in the *same* four
   files; there is no reason to expect a different outcome at
   implementation time, since the gap is schema-level and
   phase-independent, not something that only manifests once code is
   actually being written.
2. Stage 1's own open design questions (§6 in both reports — grammar
   shape, `-q`/`--query` composition, hledger-nativeness, strict-vs-
   lenient error handling) are genuine product-design uncertainties that
   do not hinge on CodeCompass availability at all; resolving them via a
   lead-drafted shared contract and re-dispatching fresh implementation
   agents would mostly re-measure design-taste and typing-speed
   differences, not context quality, which is the exact confound §5.3's
   three-stage restructuring was designed to avoid.
3. No ambiguity surfaced at Stage 1 whose *resolution* would plausibly
   change how much CodeCompass helps during coding — the one real gap
   (no relationship graph) is already fully exercised and already
   costed out. Spending further trial resources on Stage 3 would add
   redundant, not incremental, evidence to the one question Phase 78's
   plan set out to answer (§7.2's exit question, which §5.3.2 states
   this Stage 2 evaluation alone is sufficient to decide).

## Independent cross-check of the dispatched agents' own self-reports

Per this task's explicit instruction not to trust either report's framing
at face value: the treatment agent's own closing claim ("CodeCompass
confirmed direct-reading findings rather than surfacing new facts") is
**independently corroborated**, not merely accepted — by (a) its own
research-trace ordering (direct reads precede all CodeCompass queries),
(b) my own re-run of every query showing no output beyond what live
source already contains, and (c) the near-identical depth/correctness of
the baseline report, which had zero CodeCompass access at all and reached
the same conclusions by the same means. This is a case where the
dispatched agent's self-assessment happens to be accurate — confirmed by
independent ground-truth inspection, not assumed from the report's own
polish.
