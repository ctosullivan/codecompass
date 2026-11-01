# Phase 84 completion audit — Consolidated Knowledge API and Query CLI

**Auditor:** `release-phase-auditor` (independent DoD gate, `CLAUDE.md` §5).
**Audited commit (exact HEAD):** `8295ee9b6a25bc823e48fe6ab683224dd6776911`.
**Phase-84 commit range audited:** `0b4f321` (implementation + `decisions/0091`)
→ `447ba2b` (docs/changelog/roadmap/context/retro + L-107 filed) →
`58724a5` (fixes 3 blocking + 2 non-blocking `docs-reconstructor` drift
findings) → `8295ee9` (knowledge-curator triage of L-107 — retained).
Everything before `0b4f321` (`fad3a89`, `2436e39`, `7e8c538`, ...) is
already-closed Phase 83 work, out of scope here.

**Verdict: PASS WITH NON-BLOCKING OBSERVATIONS.**

No blocking defect found in code, tests, docs, protected-file scope,
learnings triage, or the retro. One genuine, non-blocking test-rigor gap
found in the `query relations` backward-compatibility test's own
docstring claim (item 4 below) — the underlying migration itself is
independently confirmed correct by other means, so this does not block
the phase, but it is a real finding, not invented to pad the report.

---

## 1. Plan verification (§11) and acceptance criteria (§9)

Re-ran `tests/test_knowledge_api.py` directly:

```
.venv/bin/python -m pytest tests/test_knowledge_api.py -v
=> 47 passed in 1.88s
```

All 47 pass, including the five `TestRealCorpusDogfoodDemonstration`
tests. Confirmed `~/projects/ledgerkit/context-graph.db` exists
(569344 bytes, present) and that the dogfood class is gated by
`@requires_ledgerkit` (`pytest.mark.skipif(not LEDGERKIT_ROOT.exists()
or not (LEDGERKIT_ROOT / "context-graph.db").exists(), ...)`). The run
summary shows **47 passed, 0 skipped** — so the dogfood tests genuinely
executed against the real corpus, not skipped.

Each of plan §9's seven acceptance criteria maps onto a real,
independently-run test or behaviour, not merely an assertion in prose:
1/2/3/4 — `TestRealCorpusDogfoodDemonstration`'s five tests (real
`DEC-BFS-001`, real `reports.py::balance_from_spec` source symbol via
natural-key identity, real oracle PASS, real
`stated_intent`/`scoped_verification` separation — all re-derived by the
test itself via `oracle.evaluate_result_precedence`/raw SQL, not trusted
from the API's own report, per the test's own docstrings). 5 —
`TestFindGaps::test_real_corpus_surfaces_the_known_stale_test_citation`,
independently re-verified by me directly (§6 below). 6 —
`TestContextPacket` (bounded, deterministic, truncation reported). 7 —
`TestExportSnapshot::test_writes_portable_envelope_with_identity_and_
revision`.

**Result: PASS.**

## 2. No scope creep / protected-file drift

```
git diff 7e8c538..8295ee9 -- src/codecompass/oracle.py \
  src/codecompass/graph.py src/codecompass/knowledge_intermediate.py \
  CLAUDE.md
=> empty (0 lines)
```

Also independently confirmed `decisions/0084`/`0085` (the architecture
ADRs this phase must not reopen) are byte-identical across the same
range (`git diff fad3a89..8295ee9 -- decisions/0084* decisions/0085*` →
empty).

Full file list across exactly the 4 Phase-84 commits
(`git diff fad3a89..8295ee9 --stat`, i.e. excluding the preceding,
unrelated Phase-83 commits `2436e39`/`fad3a89`):

```
CHANGELOG.md
decisions/0091-phase-84-knowledge-api-implementation-resolutions.md
docs/architecture/components.md
docs/architecture/overview.md
docs/reference/cli.md
planning/CONTEXT.md
planning/ROADMAP.md
planning/learnings/inbox.md
planning/phase-84-consolidated-knowledge-api.md
planning/retros/_drift-audit-phase-84.md
planning/retros/phase-84-consolidated-knowledge-api.md
src/codecompass/cli.py
src/codecompass/knowledge_api.py
tests/test_cli.py
tests/test_knowledge_api.py
```

This matches exactly the claimed deliverables (new module, new tests,
one migrated CLI command in `cli.py`, one new ADR, docs/changelog/
roadmap/context, retro, drift-audit report, learnings inbox). No stray
file.

**Result: PASS.**

## 3. No-mutation-path guarantee

Static check: `knowledge_api.py` has exactly one `sqlite3.connect(...)`
call site (line 228), using `f"file:{db_path}?mode=ro", uri=True`. It
imports `knowledge_intermediate`/`oracle` but only calls parsing/
derivation functions (`derive_epistemic_profile`, `derive_provenance_
label`, `load_slug_records`, `_list_slugs`, `sha`, `_extract_id_strings`,
`_unquote`, `aggregate_contract`, `evaluate_result_precedence`,
`parse_oracle_contract`, `parse_oracle_result`) — none of
`knowledge_intermediate.py`'s real writer functions
(`write_manifest`/`apply_manifest`/`_apply_*`/`write_presentation_
cache`/`apply_automatic_refreshes`/`write_doc_candidates_to_manifests`)
or `oracle.py`'s (`write_oracle_result`/`accept_baseline`) appear
anywhere in the usage list. `graph.open_graph`/`rebuild_deterministic`
are never called (grep confirms zero occurrences).

Behavioural check (independently written and run, not reusing the
module's own test fixtures):

```python
# against an empty tmp_path, no context-graph.db present
ka.get(tmp, "REQ-NOPE-001")      # -> status='empty', no exception
ka.search(tmp, "anything")        # -> status='empty'
ka.find_gaps(tmp)                 # -> status='empty'
# after: tmp directory tree is still completely empty — no
# context-graph.db, no file of any kind, created as a side effect.
```
Confirmed: `before == after == []`.

**Result: PASS.**

## 4. `query relations` migration — byte-identical claim

`src/codecompass/cli.py::query_relations` is confirmed migrated onto
`knowledge_api.resolve_doc_mentions` (the private `_resolve_relations`/
`_incoming_doc_relations`/`_relation_enrichment_row` helpers were
removed from `cli.py` and relocated verbatim into `knowledge_api.py`,
confirmed by reading the diff side by side — same SQL, same logic, new
home).

`tests/test_cli.py::test_query_relations_backward_compatible_after_
knowledge_api_migration` asserts `payload == {...}` — a full, literal
dict-equality comparison of the entire JSON response (not a subset
check, not a key-presence check). This part genuinely is byte-for-byte.

**Finding (non-blocking):** the test's own docstring claims "the exact,
full table **and JSON** output text is unchanged -- byte-for-byte," but
the *table*-format assertion is only two substring checks
(`"Package code" in table_result.output`, `"src/app.ts" in
table_result.output`) — not a full literal string comparison of the
rendered table, contrary to what the docstring says it does. This is a
real overclaim in the test's own prose relative to what it actually
verifies for the table-rendering path specifically.

This does not block the phase for three independent reasons: (a) the
JSON comparison, which *is* fully literal, already proves the migrated
resolution logic produces identical structured output; (b) the diff
shows the table-rendering code path (`graph.doc_relations`/`graph.
doc_code_trace`/rich `Table` construction) was not touched by this
migration at all — only the *resolution* step (`_resolve_relations` →
`knowledge_api.resolve_doc_mentions`) moved, and the table renderer
consumes the same shape of data as before; (c) all 14 pre-existing
`query relations` tests, several of which do exercise table-text content
more specifically (e.g. `test_query_relations_human_output_shows_
package_code_section`), are confirmed unmodified (diff shows only an
insertion of the new test function, nothing else changed in
`tests/test_cli.py`'s existing relations tests) and all still pass.

Re-ran the 14 pre-existing + 1 new `query relations` tests
(`pytest tests/test_cli.py -k relations`): **15 passed** (the grep also
matches one unrelated test, `test_check_reports_spec_docs_without_
relations_section`, which also passed).

**Result: PASS WITH NON-BLOCKING OBSERVATION** (test docstring overclaim
re: table-format rigor; underlying migration correctness independently
confirmed by other means).

## 5. Full independent re-run

- `tests/test_knowledge_api.py`: **47 passed** (see §1).
- `tests/test_cli.py -k relations`: **15 passed** (see §4).
- Full repository suite, `.venv/bin/python -m pytest -q` (run twice,
  consistent both times): **1103 passed, 2 skipped** in ~308-321s.
  The 2 skips are pre-existing, environment-dependent
  (`npm`/`cargo`/`stack` not installed on this machine), unrelated to
  Phase 84 — confirmed via `grep -rn "pytest.mark.skipif"` across
  `tests/`.
- `scripts/check_contracts.py --strict`: **7 findings, exit 0** —
  matches claimed count exactly (6 `contract-result-integrity-mismatch`
  + 1 `contract-check-gap`, all informational).
- `scripts/check_knowledge_base.py --strict`: **24 findings, exit 0** —
  matches claimed count exactly (all `knowledge-base-snapshot-current-
  divergence`, informational).
- `scripts/check_user_docs.py --strict`: **0 findings, exit 0** —
  matches claimed count exactly.

**Result: PASS.**

## 6. Real-corpus `find_gaps` finding — independently re-derived

Read `EV-BFS-002.yaml`/`EV-BFS-003.yaml` directly:
`test_ref` cites `single-section-expense-subtotal--20261021T085158258751Z-
85ec4f35.yaml` / `multi-section-income-expense-subtotal--
20261021T085159042773Z-584a42f5.yaml`. Both cited files have
`oracle_contract_content_hash: 7415d851de2f551502cf1fe77831810d466704b
7b6ff61e1a66f8bd71b92daec`.

Independently computed the live contract's own hash:
```
sha256(planning/contracts/balance-from-spec/oracle-contract.yaml)
= f2b3cc6dccc9f70aceede2d981bbf2d4b0b8894befa457622e097e44decb28af
```
— genuinely different from the cited results' recorded hash, confirming
those two citations are `INVALID` against the live contract (consistent
with `evaluate_result_precedence`'s digest-mismatch rule).

Confirmed a **different, later, currently-valid, uncited** result exists
for each of the same two `check_id`s:
`single-section-expense-subtotal--20261028T075132259723Z-bfd29ce3.yaml`
(`outcome: PASS`, `oracle_contract_content_hash: f2b3cc6d...` — matches
the live contract exactly) and the equivalent `multi-section-...-
c9165dee.yaml`. Neither `EV-BFS-002` nor `EV-BFS-003` cites either of
these fresher files.

This is a genuine, pre-existing real-corpus condition, not a test
artifact — confirmed entirely by my own independent hash computation and
file reads, not by trusting `find_gaps`'s own report of itself.

**Result: PASS.**

## 7. Docs/changelog/roadmap/context consistency

- `CHANGELOG.md` `[Unreleased]` → `Added`: one Phase-84 entry, accurate
  against the real module (function list, authority tags, 47 tests, the
  real `find_gaps` finding) — spot-checked against source directly.
- `planning/ROADMAP.md` Phase 84 row: currently `in progress` (correct —
  not yet gated `done`, exactly as it must stay until this audit's own
  verdict is delivered and the terminal `roadmap-context-curator`
  reconciliation commit runs).
- `planning/CONTEXT.md`: "Current phase" section accurately describes
  Phase 84 as implementation-complete, audit in progress; matches the
  real test counts and strict-validator state.
- `docs/reference/cli.md`: independently ran
  `.venv/bin/codecompass knowledge export --help` and compared against
  the doc's own synopsis/prose — matches exactly post-fix (no `--json`
  claimed for `export`; the "writes nothing, ever" blanket claim now
  correctly carves out `export`'s own `OUT_PATH` write; the dead
  `architecture/knowledge-api.md` reference now correctly points at
  `docs/architecture/overview.md`/`components.md`).
- `docs/architecture/overview.md`/`components.md`: both Phase-84
  additions (`knowledge_api.py` row/bullets) independently checked
  against the real module — function names, authority-tag list, and
  the `graph.open_graph`-avoidance claim all match the real code.

Independently re-read `git show 58724a5` in full: the 3 blocking +
2 non-blocking `docs-reconstructor` findings
(`planning/retros/_drift-audit-phase-84.md`) are each fixed exactly as
the finding described, nothing left half-fixed, and no new drift
introduced by the fix commit itself (re-checked the fixed prose against
the real `--help` output and the real `get_context_packet`/
`query_relations` source directly, not merely trusting the fix commit's
own message).

**Result: PASS.**

## 8. Learnings triage

`planning/learnings/inbox.md` — `L-107` (the only candidate learning
whose `origin:` names Phase 84) has `status: retained`, with a genuine,
specific curation note (2026-10-29, knowledge-curator): independently
re-confirms the same two content-hash values I independently recomputed
in §6 above, checks for duplication against `L-104`/`L-106` by name and
reasoning, and gives a concrete, falsifiable "moves forward when"
condition (a second oracle-contract-extension event recurring the same
gap). Not a stub.

Checked for any other untriaged entry from this phase: grepped every
`status:` line in `inbox.md` — all top-level entries are `retained`/
`promoted`; the only two bare `candidate` substrings in the file belong
to prose inside unrelated, pre-existing learnings (not Phase 84 origin).

**Result: PASS.**

## 9. Retro

`planning/retros/phase-84-consolidated-knowledge-api.md` — checked
against `planning/retros/TEMPLATE.md`'s section list: every section
present (Where we are / Goal / Scope delivered vs planned / What was
achieved / What worked / What didn't work / Lessons learnt /
Process-improvement feedback / Candidate learnings filed / Where we're
going / Time-cost note), each filled with real, specific content, not
boilerplate.

"What didn't work" names two real, named defects found during the
phase's own development (a false-positive no-mutation static check
matching forbidden function names as bare substrings in the module's own
docstring; two first-draft consistency-envelope tests using hand-rolled
fake digests that `evaluate_result_precedence` correctly rejected) — both
read as honest self-reported friction, not sanitized.

"Where we're going" names the real next phases (85, 88) and states the
trajectory is confirmed, not changed, by this phase's own findings.

**Result: PASS.**

---

## Summary of checks

| # | Check | Result |
|---|---|---|
| 1 | Plan §9/§11 verification, dogfood genuinely ran | PASS |
| 2 | No protected-file drift / scope creep | PASS |
| 3 | No-mutation-path (static + behavioural) | PASS |
| 4 | `query relations` migration byte-identical | PASS WITH NON-BLOCKING OBSERVATION |
| 5 | Full independent re-run (tests + 3 strict validators) | PASS |
| 6 | Real-corpus `find_gaps` finding independently re-derived | PASS |
| 7 | Docs/changelog/roadmap/context consistency | PASS |
| 8 | Learnings triage (L-107) | PASS |
| 9 | Retro substantive and honest | PASS |

## Overall verdict: PASS WITH NON-BLOCKING OBSERVATIONS

**Non-blocking observation to record (not required before `done`):**
`tests/test_cli.py::test_query_relations_backward_compatible_after_
knowledge_api_migration`'s own docstring claims full byte-for-byte
table-and-JSON comparison, but its table-output assertion is only two
substring checks, not a full literal comparison. Independently confirmed
non-blocking because the JSON comparison is genuinely exhaustive, the
table-rendering code path itself was untouched by the migration (only
the upstream resolution step moved), and all pre-existing table-text
assertions elsewhere in the same file continue to pass unmodified. No
fix required to mark Phase 84 `done`; worth a one-line docstring
correction next time this test is touched, at the implementer's
discretion.

No other finding. Per `CLAUDE.md` §5, this audit authorizes the terminal
`roadmap-context-curator` reconciliation commit (flipping
`planning/ROADMAP.md`'s Phase 84 row to `done`, updating
`planning/CONTEXT.md`'s current-state section, and the plan file's own
Status line) — provided no further commit touching audited scope lands
between this audit and that reconciliation commit.

---

# CORRECTIVE PASS AUDIT — 2026-10-29

**Auditor:** `release-phase-auditor` (independent post-completion audit of a
corrective pass against an already-`done` phase, `CLAUDE.md` §5).
**Audited commits:** `45a3ca8` (fix: verification currency, dangling
evidence, context bounds — `decisions/0092`) and `4569e3f` (docs:
changelog/cli-reference/plan/retro for the corrective pass). Both on
`main`, directly on top of this phase's prior `done` state (`8295ee9`,
the subject of the audit above).

**Verdict: PASS WITH NON-BLOCKING OBSERVATIONS.**

All three defects named in `decisions/0092` are genuinely fixed in the
current source, independently re-derived from the code (not trusted from
the ADR's or commit messages' own prose), with regression tests that
provably discriminate old from new behaviour. No regression, no scope
creep, no new mutation path. Several non-blocking process/coverage gaps
are named below, none of which indicate the fix itself is wrong.

## 1. Defect 1 (verification currency) — confirmed fixed

- `ConsistencyEnvelope.status` defaults to `"unconfirmed"`
  (`src/codecompass/knowledge_api.py:121`), not `"current"`. Confirmed
  the pre-fix default was `"current"`
  (`git show 45a3ca8^:src/codecompass/knowledge_api.py` line 117).
- `repo_root` is genuinely threaded, not merely accepted syntactically:
  `get()` → `_get_knowledge_record`/`_get_check`/`_get_result` (lines
  336, 356, 360-362); `traverse(..., repo_root=...)` (new parameter,
  line 808) → `_traverse_check_results(..., repo_root=repo_root)` (line
  834). `_get_result` calls
  `_oracle.evaluate_result_precedence(r, contract, check,
  contract_path=contract_path, repo_root=repo_root)` (line 708-710);
  `_traverse_check_results` calls the identical form (line 940).
  Pre-fix, `_get_result`/`_get_check` took no `repo_root` parameter at
  all and `traverse()` had none either (confirmed directly in the
  pre-fix source via `git show 45a3ca8^:...`) — `evaluate_result_
  precedence` could never have been called with a live checkout through
  these paths before this pass.
- `_oracle_result_consistency()` (lines 495-530) is the single shared
  helper: `effective == "INVALID"` → always `"stale"`; `effective in
  ("PASS","FAIL")` → `"current"` only when `repo_root is not None`,
  else `"unconfirmed"` with an explicit reason. Read directly, not
  inferred from the docstring.
- `_get_check()` (lines 652-693): `NOT_REQUIRED`/`None` aggregate →
  `"unconfirmed"`; `GAP` → `"unconfirmed"`; otherwise `"current"` only
  with `repo_root is not None`, else `"unconfirmed"`. (Minor
  documentation imprecision, not a defect: `decisions/0092`'s prose
  says "an aggregate `PASS`" but the code applies the identical rule to
  a `FAIL` aggregate state too — correct and conservative behaviour,
  just slightly under-described in the ADR.)
- CLI forwarding confirmed by reading `git show 45a3ca8 -- src/
  codecompass/cli.py` directly: all four of `knowledge_get`/
  `knowledge_trace`/`knowledge_gaps`/`knowledge_context` gained a
  `--repo-root` option and pass `repo_root=repo_root` straight into the
  corresponding `knowledge_api` call. `knowledge_search`/
  `knowledge_export` are correctly untouched (`search`/`export_snapshot`
  take no `repo_root`).
- `asdict(r)` collision check: `_get_result`'s `details` dict spreads
  `asdict(r)` (which includes the result's own recorded `invalid_reason`
  field) and separately adds `effective_invalid_reason` — a distinctly
  named key, never overwriting `invalid_reason`. Confirmed by reading
  the dict-literal construction directly (`knowledge_api.py:715-728`).

**Result: PASS.**

## 2. Defect 2 (dangling evidence) — confirmed fixed

`trace_evidence()`'s inner `_resolve()` (lines 1144-1158) appends a
`Gap(kind="dangling_evidence_reference", subject_id=record_id,
scope=role, ...)` for each unresolved citation while still appending
every successfully-resolved citation to `results` — confirmed a mixed
case (`test_mixed_valid_and_dangling_supporting_evidence_reports_both`)
keeps the valid citation in `results` and reports only the broken one as
a gap. `find_gaps()` (lines 1283-1289) performs the identical
corpus-wide scan over every record's `supporting_evidence`/
`contradicting_evidence`, same `Gap.kind`, same semantics. Pre-fix,
`trace_evidence()` silently `continue`d past an unresolved id with no
gap recorded at all (confirmed directly: `git show
45a3ca8^:src/codecompass/knowledge_api.py` lines 1050-1066) — a Claim
citing one nonexistent evidence id returned `status="result"` with zero
evidence, never `"gap"`.

**Result: PASS.**

## 3. Defect 3 (context bounds) — confirmed fixed

`get_context_packet()`'s non-knowledge-record branch (lines 1447-1456)
now builds `candidates = [search_response.results[0]]` and falls
through to the same `items, truncated = _bound_context_items(candidates,
max_items, max_chars)` call (line 1458) the knowledge-record path also
uses — one shared implementation, not two divergent ones. Pre-fix, this
branch returned early with `packet_items = [item]` wrapped
unconditionally and `truncated` hardcoded `False`, regardless of
`max_chars`/`max_items` (confirmed directly:
`git show 45a3ca8^:src/codecompass/knowledge_api.py` lines 1281-1291).
`_bound_context_items()` itself (lines 1364-1391) is deterministic:
walks candidates in order, stops at the first item that would exceed
either bound, leaving `items` empty with `truncated=True` rather than
ever returning an over-budget result.

**Result: PASS.**

## 4. No regression / no scope creep — confirmed

`git diff 5081860 4569e3f -- src/codecompass/oracle.py
src/codecompass/graph.py src/codecompass/knowledge_intermediate.py`
produces zero lines of output — these three files are genuinely
untouched by both commits. Full changed-file list across both commits
(`CHANGELOG.md`, `decisions/0092-...md`, `docs/reference/cli.md`,
`planning/phase-84-consolidated-knowledge-api.md`,
`planning/retros/phase-84-consolidated-knowledge-api.md`,
`src/codecompass/cli.py`, `src/codecompass/knowledge_api.py`,
`tests/test_cli.py`, `tests/test_knowledge_api.py`) matches exactly what
`decisions/0092` and the commit messages claim — no undisclosed file
touched. `tests/test_knowledge_api.py::TestNoMutationPath`'s 6 tests all
still pass (re-run directly: `test_module_source_references_no_writer_
function`, `test_every_sqlite_connect_call_is_read_only`,
`test_get_does_not_create_a_missing_context_graph_db`, and the three
`export_snapshot` isolation tests). Grepped the diff for
`INSERT`/`UPDATE`/`DELETE`/write-function references: none found. No new
database, schema, or persisted identity introduced — the only new
dataclass (`_oracle_result_consistency`'s `ConsistencyEnvelope` return
values) is never persisted, consistent with the module's own existing
docstring guarantee.

**Result: PASS.**

## 5. Test rigor — spot-checked, reasoning-based (not empirical re-run)

Spot-checked 10 of the 18 new tests (`TestResultVerificationCurrency`'s
`test_recorded_pass_unconfirmed_without_a_reachable_checkout`,
`test_check_aggregate_current_only_with_reachable_repo_root`,
`test_search_results_do_not_default_to_current`;
`TestTraceEvidence`'s `test_exclusively_dangling_supporting_evidence_
is_a_gap`, `test_mixed_valid_and_dangling_supporting_evidence_reports_
both`, `test_dangling_contradicting_evidence_is_a_gap`;
`TestContextPacket`'s `test_non_knowledge_record_topic_is_bounded_by_
max_chars`, `test_non_knowledge_record_topic_is_bounded_by_max_items`,
plus two more) against the pre-fix source
(`git show 45a3ca8^:src/codecompass/knowledge_api.py`, saved locally for
direct comparison). Each one's assertions would plausibly have failed
against the pre-fix code, by direct reading of what the old code path
actually returned (e.g. the old `_get_check` used an unmodified default
`ConsistencyEnvelope()` — `status="current"` — regardless of
`repo_root`, which didn't even exist as a parameter to that function;
the old `get_context_packet` non-knowledge-record branch hardcoded
`truncated=False` and ignored `max_chars`/`max_items` entirely). **This
was done by reading the diff and reasoning about the old code's actual
behaviour, not by checking out the pre-fix commit and actually running
the new tests against it** — the task's own stated allowance, but noted
explicitly per instruction.

**Result: PASS** (by diff-reasoning, not by empirical execution against
the old commit).

## 6. Verification commands re-run directly

```
.venv/bin/python -m pytest tests/test_knowledge_api.py -q
=> 65 passed in 3.22s

.venv/bin/python -m pytest tests/test_cli.py -q
=> 96 passed in 179.29s

.venv/bin/python scripts/check_user_docs.py --strict
=> check_user_docs: no findings (exit 0)

.venv/bin/python scripts/check_contracts.py --strict
=> check_contracts: 7 finding(s), all [info]-level, all the known
   pre-existing balance-from-spec superseded-result/overlapping-pattern
   findings named in the corrective pass's own plan §12 (exit 0)

.venv/bin/python scripts/check_knowledge_base.py --strict
=> check_knowledge_base: 24 finding(s), all [info]-level
   knowledge-base-snapshot-current-divergence notices, pre-existing and
   unrelated to this pass (exit 0)
```

All match what `decisions/0092`/the plan's §12/the retro addendum claim:
65 (not 47) tests in `tests/test_knowledge_api.py`; both strict
validators exit 0 with only pre-existing informational findings. Did not
run the complete ~5-minute full suite given the module-level runs above
already cover the changed surface and the task named this as optional;
the plan/retro's own claim of "full suite 1121 passed/2 skipped" was not
independently re-verified by me.

**Result: PASS.**

## 7. Docs/changelog/plan/retro consistency — confirmed accurate (as of
the two audited commits)

- `CHANGELOG.md`'s `[Unreleased]` → `Fixed` entry (single Phase 84
  corrective-pass entry, not batched with anything else) accurately
  summarizes all three fixes and matches the code.
- `docs/reference/cli.md`'s new `--repo-root PATH` usage-line placement
  (`get`/`trace`/`gaps`/`context`, not `search`/`export`) and its new
  prose paragraph describing current/unconfirmed/stale semantics match
  `_oracle_result_consistency()`/`ConsistencyEnvelope` exactly, confirmed
  by direct comparison.
- `planning/phase-84-consolidated-knowledge-api.md` §12 and
  `planning/retros/phase-84-consolidated-knowledge-api.md`'s corrective
  pass addendum both accurately describe the three defects, the chosen
  fixes, and the verification results, consistent with the code and with
  `decisions/0092`.

**Result: PASS**, for the content actually committed in `45a3ca8`/
`4569e3f`. See §9 below for a caveat: an independently-run, uncommitted
`docs-reconstructor` drift audit (dated the same day) found two
non-blocking incompleteness gaps in `docs/reference/cli.md`'s `trace`/
`gaps` bullets (not false, just not yet mentioning the new
`dangling_evidence_reference` gap kind) — real findings, but against
content outside the two commits this section evaluates, and already
being addressed (see §9).

## 8. Original Phase 84 audit report and `done` status — confirmed
untouched

`git log --follow --oneline -- planning/retros/_audit-phase-84.md` shows
exactly one commit (`2698622`, the original audit) ever touched this
file before this append — neither `45a3ca8` nor `4569e3f` modified it.
`planning/ROADMAP.md`'s Phase 84 row and `planning/phase-84-
consolidated-knowledge-api.md`'s own `Status:` line both still read
`done`/pre-corrective-pass text as of these two commits (see §9) —
expected: per `CLAUDE.md` §5's own exemption, updating these to reflect
the corrective pass is the terminal `roadmap-context-curator`
reconciliation commit's job, which has not yet landed.

**Result: PASS** (history genuinely intact; no rewrite).

## 9. Non-blocking observations

1. **No automated CLI-level test exists for the new `--repo-root`
   option** (or indeed for any of `knowledge get/search/trace/gaps/
   context/export` at all — confirmed by grepping `tests/test_cli.py`
   for `knowledge_app`/`knowledge_get`/`knowledge_trace`/
   `knowledge_gaps`/`knowledge_context`: zero matches, before or after
   this corrective pass). The forwarding correctness in §1 above was
   confirmed only by direct code reading, not by an automated regression
   test — a future refactor of `cli.py` could silently break this
   plumbing with nothing to catch it. This mirrors a pre-existing
   pattern: Phase 84's own original plan (§11) only required
   `tests/test_cli.py`-equivalent suites to "re-run green" (no
   regression), never required new CLI-level tests for the six `knowledge
   *` commands it introduced, and the original audit didn't flag this
   either. `CLAUDE.md` §1's own rule ("a phase adds behavior to an
   existing function that already has a real production call site...
   must... include at least one test that exercises it directly") does
   plausibly apply here — `knowledge_get`/`_trace`/`_gaps`/`_context` are
   real production call sites, and `--repo-root` is new behaviour wired
   into them — so this is a genuine, if inherited-pattern, gap worth
   closing in a follow-up, not merely a style nit. **Non-blocking**
   because the forwarding is simple, low-complexity parameter passthrough
   (confirmed correct by direct inspection, not complex new logic), and
   because the project's own established posture for this specific
   module already accepted this test-coverage boundary at Phase 84's own
   original, independently-audited completion.

2. **`planning/ROADMAP.md`, `planning/CONTEXT.md`, and the plan file's
   own `Status:` line are not yet updated** to mention this corrective
   pass, `decisions/0092`, or the test count change (47→65). This is
   expected and not a defect in the two audited commits — per `CLAUDE.md`
   §5's own exemption, this is the terminal `roadmap-context-curator`
   reconciliation commit's job, still pending as of this audit.
   Precedent (Phases 76/81/82's own corrective passes, all visible in
   `planning/ROADMAP.md`'s current text) is for that reconciliation
   commit's `ROADMAP.md` row to name the corrective pass, its ADR, its
   retro addendum, and this audit report explicitly — recommended here
   so it isn't dropped.

3. **Process incident during this audit (fully corrected, disclosed for
   transparency):** while comparing `ruff check .` output before/after
   this corrective pass, I ran `git stash -u` to temporarily check out
   commit `5081860`'s tree. This inadvertently stashed away **pre-existing
   uncommitted work already present in the working tree when this audit
   began** — a new candidate learning, `L-109` (Rich `Table` cells
   truncating at default render width, filed in
   `planning/learnings/inbox.md` with a `knowledge-curator` curation note
   recommending promotion), plus matching uncommitted edits to
   `docs/architecture/overview.md`, `docs/architecture/components.md`,
   and `docs/reference/cli.md` (apparently `docs-maintainer` work
   addressing the two non-blocking findings in the also-uncommitted
   `planning/retros/_drift-audit-phase-84-corrective-pass.md`). I
   immediately ran `git stash pop` and confirmed via `git status`/`git
   diff` that the working tree was fully restored to its pre-incident
   state; nothing was lost, and I committed nothing. Flagging this both
   as a disclosure of my own tool-use error and because it surfaces a
   real, separate finding: **the committed retro's claim ("no new
   candidate learning met the bar") is already superseded** by this
   in-progress, uncommitted `L-109` filing, which traces to the exact
   same near-miss the committed retro's own "What didn't work" section
   describes (the Rich-table-truncation discovery while strengthening
   the `query relations` test). This will need reconciling — either by
   updating the retro when `L-109`'s commit lands, or by the terminal
   reconciliation commit noting it — before this corrective pass's own
   closeout is airtight. Not blocking this audit's verdict on the two
   commits it was asked to evaluate, since `L-109` and its related edits
   are genuinely separate, not-yet-committed work, not part of `45a3ca8`/
   `4569e3f`.

4. **A `docs-reconstructor` drift audit for this corrective pass already
   exists** at `planning/retros/_drift-audit-phase-84-corrective-pass.md`
   with verdict **NO DRIFT** (0 blocking findings; a few non-blocking
   doc-completeness/staleness notes, already being addressed per
   observation 3 above) — satisfying `CLAUDE.md` §5's drift-audit
   condition for this corrective pass. Note it is itself **not yet
   committed** (confirmed via `git status`) as of this audit; it should
   be committed alongside the reconciliation above.

## Summary for the lead

**Verdict: PASS WITH NON-BLOCKING OBSERVATIONS.** All three corrective-
pass defects are genuinely, correctly fixed in `45a3ca8`/`4569e3f`,
independently re-derived from the current source rather than trusted
from `decisions/0092`'s or the commit messages' own prose; no
regression, no scope creep, no new mutation path; `tests/
test_knowledge_api.py` (65 passed) and `tests/test_cli.py` (96 passed)
and all three `--strict` validators (exit 0, pre-existing informational
findings only) all re-run clean; the original Phase 84 audit report and
`done` status remain genuinely untouched.

Before this corrective pass's own closeout is complete, the lead should:
1. Add at least one direct CLI-level regression test exercising
   `--repo-root` on one of `knowledge get`/`trace`/`gaps`/`context`
   against its real `cli.py` call site (observation 1) — recommended,
   not required to avoid re-opening this verdict, but closes a real gap
   `CLAUDE.md` §1 names explicitly.
2. Land the pending terminal `roadmap-context-curator` reconciliation
   commit (`planning/ROADMAP.md`, `planning/CONTEXT.md`, the plan file's
   `Status:` line — observation 2), together with committing the
   already-written, uncommitted drift audit (observation 4).
3. Resolve the `L-109` candidate-learning filing now in progress
   (observation 3) and reconcile it against the corrective-pass retro's
   current "no new candidate learning met the bar" claim, which that
   filing already supersedes.

None of the above reopen this verdict on the two audited commits
themselves — they are follow-up closeout steps, not defects in the fix.

---

# FINAL CORRECTIVE AMENDMENT AUDIT — 2026-11-02

**Auditor:** `release-phase-auditor` (independent post-completion audit
of a *second*, final corrective amendment against an already-`done`
phase that already went through one prior corrective pass — `CLAUDE.md`
§5, with full scrutiny of this amendment's own newly-written code per
the project's governing agent instructions, not a lighter-touch re-check
merely because it is "fixing something already found wrong").

**Audited commits:** `23f6826` (fix: Requirement indirect evidence,
`find_gaps()` live-revision validation — `decisions/0093`) and `085a68c`
(docs: changelog/plan/retro for the final corrective amendment). Both on
`main`, directly on top of this phase's prior `done`-plus-corrective-pass
state (`f22c16a`, the subject of the "CORRECTIVE PASS AUDIT — 2026-10-29"
section above).

**Verdict: FAIL.**

Both of `decisions/0093`'s own named defects (Requirement indirect
evidence; `find_gaps()`'s dropped `repo_root`) are genuinely, correctly
fixed, independently re-derived from the current source and re-executed
against the real corpus — see §§1-2, 6 below, all PASS. **But** the
same refactor that fixes defect 1 introduces a third, undisclosed
behavioural change to **Claim**-level `trace_evidence()` tracing that
the ADR, the function's own docstring, the plan file §13, and the retro
all explicitly and repeatedly claim does **not** happen ("Claim-level
tracing ... is completely unaffected" / "is unaffected by any of this").
This claim is demonstrably false, confirmed by direct execution (§3
below) — a verified, reproducible defect against this task's own named
criterion ("No regression / no scope creep"), not a style nit. Per
`CLAUDE.md` §5 and the governing instruction not to soften a real FAIL,
this blocks the amendment's own closeout until resolved; it does **not**
reopen or weaken either of the two audits above, which concern different,
earlier commits.

## 1. Defect 1 (Requirement indirect evidence) — fix itself confirmed
correct

Read `trace_evidence()` directly (`src/codecompass/knowledge_api.py`
lines 1123-1231). Confirmed:

- The `depends_on` walk is gated strictly on `record.kind ==
  "requirement"` (line 1199) — never entered for a Claim subject.
  Directly verified against the real corpus: `trace_evidence(REPO_ROOT,
  "CL-BFS-003")` (a real Claim whose own `depends_on: [CL-BFS-001,
  CL-BFS-002]` field is non-empty) returns only its own two direct
  `EV-BFS-002`/`EV-BFS-003` citations with `role="supporting"`,
  `via_claim=None` — `CL-BFS-001`/`CL-BFS-002` never appear in the
  result set. `CL-BFS-003`'s own `depends_on` is never walked when it is
  the subject.
- **One-hop bound confirmed**: the loop at lines 1200-1221 resolves each
  `dep_id`'s own direct `supporting_evidence`/`contradicting_evidence`
  and stops — it never recurses into a dependent Claim's own
  `depends_on` (no second-level walk exists anywhere in the function;
  confirmed by reading the full function body, not merely the loop in
  isolation).
- **Mixed case (one supported + one unsupported dependent Claim) read
  directly**, matching `test_requirement_with_mixed_supported_and_
  unsupported_claims_keeps_resolved_evidence`: `CL-MIXOK-001` (has
  `EV-MIXOK-001`) resolves into `results` with no gap; `CL-MIXBAD-001`
  (empty `supporting_evidence`) gets its own `missing_evidence` gap
  keyed to `CL-MIXBAD-001`, **not** to the Requirement — `has_any_
  support` is `True` (from the one supported Claim), so the Requirement
  itself correctly gets no `missing_evidence` gap of its own. Confirmed
  by direct code trace of lines 1198-1227, not merely trusting the test.
- `dangling_dependency_reference` is a genuinely new, distinct `Gap.kind`
  string (confirmed via `grep -n "dangling_dependency_reference"
  src/codecompass/knowledge_api.py` — appears at the `Gap.kind` comment,
  `trace_evidence()`'s own dangling-`depends_on` branch (line 1203-1206),
  `find_gaps()`'s docstring, and `find_gaps()`'s own new corpus-wide scan
  (lines 1362-1367, confirmed to run over **every** record's own
  `depends_on` field regardless of kind, matching the same
  not-kind-restricted pattern the pre-existing `dangling_evidence_
  reference` corpus-wide scan already uses, and matching `decisions/
  0093`'s own Consequences-section description "over every record's own
  `depends_on` field") — never conflated with the pre-existing
  `dangling_evidence_reference` (a broken *Evidence* reference; distinct
  `kind` string, used nowhere for a `depends_on` id).
- A record whose `depends_on` resolves to a real record that is itself
  **not** a Claim (e.g. another Requirement) is silently skipped (line
  1208-1209, `if dep.kind != "claim": continue`) — no gap, no evidence
  resolution for it. Not reachable in the current real corpus (both real
  Requirements' `depends_on` lists name only Claims — confirmed via
  `grep -rl "kind: requirement" planning/knowledge/ | xargs grep -l
  depends_on`) and not flagged as a defect by `decisions/0093`, but it is
  an **untested** edge case worth naming (see §5, Observation 2 below) —
  non-blocking on its own.

**Result: PASS** for the fix's own stated bound and keying logic. (The
separate, undisclosed Claim-level side effect of the *same* commit is
reported in §3, not here, since it is a different code path — the
unconditional, pre-`if record.kind == "requirement"` block shared by
both Claim and Requirement subjects.)

## 2. Defect 2 (`find_gaps()` dropped `repo_root`) — confirmed fixed

`grep -n "aggregate_contract\|evaluate_result_precedence"
src/codecompass/knowledge_api.py` confirms both calls inside
`find_gaps()`'s `stale_test_citation` block (lines 1400 and 1422) now
pass `repo_root=repo_root` — read directly in context, not merely
grepped: lines 1392-1437 show `aggregates = _oracle.aggregate_contract(
contract, check_results, contract_path=contract_path, repo_root=
repo_root)` and `outcome, reason = _oracle.evaluate_result_precedence(
cited, contract, check, contract_path=contract_path, repo_root=
repo_root)`. The `verification_note` qualifying phrase (lines 1428-1432)
is gated explicitly on `if repo_root is not None`, not on any other
proxy (e.g. not on `LEDGERKIT_ROOT.exists()` or similar) — read directly.

Reasoned through (not materialized as a standalone repo) the exact
scenario named in the task: a fresher result whose own
`tested_subject_digest` does not match a live checkout. With `repo_root`
now reaching `aggregate_contract()`/`evaluate_result_precedence()`,
`oracle.py` (unmodified) would itself find that fresher result's
digest-vs-live-checkout comparison fails, making `current_pass_by_check`
`False` for that check (no result both contract-valid *and*
digest-matching exists) — so the `if outcome == "INVALID" and
current_pass_by_check.get(cited.check_id):` condition at line 1424 is
never satisfied, and `stale_test_citation` correctly does not fire. This
exact scenario is also directly exercised by the new regression test
`test_stale_citation_changed_implementation_suppresses_false_claim`
(§4 below) — re-run and confirmed passing.

**Result: PASS.**

## 3. Claim-level `trace_evidence()` regression — confirmed via direct
execution (BLOCKING)

The ADR (`decisions/0093`, "Consequences"), the amended function's own
docstring, `planning/phase-84-consolidated-knowledge-api.md` §13, and
the retro's "Final corrective amendment" section all state, in near-
identical words, that Claim-level tracing is **"completely unaffected"**/
**"unaffected by any of this"** by this amendment — i.e. that calling
`trace_evidence()` on a Claim produces exactly the same gaps/results it
did before `23f6826`, modulo nothing.

This is false for one concrete, reproducible case: **a Claim whose
`supporting_evidence` field is non-empty but every id in it is
dangling (resolves to no real record).**

Read the diff precisely (`git show 23f6826^:src/codecompass/
knowledge_api.py` vs. current):

- **Pre-fix**: `if record.kind in ("claim", "requirement") and not
  supporting_ids:` — `supporting_ids` is the raw **declared** id list
  (`_extract_id_strings(...)`, before resolution). A Claim with
  `supporting_evidence: [EV-MISSING-001]` has `supporting_ids =
  ["EV-MISSING-001"]`, which is non-empty, so `not supporting_ids` is
  `False` — **no** `missing_evidence` gap, only the separate `dangling_
  evidence_reference` gap from `_resolve()`.
- **Post-fix**: `if record.kind in ("claim", "requirement") and not
  has_any_support:` — `has_any_support` (for a Claim) equals
  `has_direct_support`, the **return value** of `_resolve(...)`, which is
  `True` only if **at least one** id actually resolved to a real record.
  For the same Claim, `has_direct_support` is now `False` (the one
  declared id never resolves) — so the `missing_evidence` gap **now also
  fires**, in addition to the pre-existing `dangling_evidence_reference`
  gap.

**Confirmed empirically**, not just by diff-reading (fixture built in
`/tmp` scratch space, never materialized in this repo's working tree):

```
id: CL-DANGLE-001
kind: claim
statement: dangling only
supporting_evidence: [EV-MISSING-001]
status: supported
```
```
>>> ka.trace_evidence(<scratch_root>, "CL-DANGLE-001")
status = "gap"
gaps = [
  Gap(kind='dangling_evidence_reference', subject_id='CL-DANGLE-001', ...),
  Gap(kind='missing_evidence', subject_id='CL-DANGLE-001',
      reason="CL-DANGLE-001 (claim) has no supporting_evidence citation at all"),
]
```

Two gaps, where the pre-fix code (and `decisions/0092`'s own explicitly
stated design principle, "a *declared* citation is never conflated with
a *resolved* one") produced exactly one. This is a genuine behavioural
change to the Claim-level code path, triggered purely by this
amendment's refactor of the shared `_resolve()`/`has_any_support`
plumbing — **not disclosed anywhere**, and directly contradicted by the
amendment's own governing documents.

**Why this is not merely a documentation nit:**

- It is user-visible through two real production call sites that were
  not reasoned about or tested for this effect: `get_context_packet()`
  (`src/codecompass/knowledge_api.py:1540`, which calls `trace_evidence()`
  for **any** subject's gaps, Claim or Requirement) and the CLI's
  `knowledge trace <id>` command (`src/codecompass/cli.py:1776`, which
  calls `trace_evidence()` directly with no Requirement/Claim
  distinction). A user running `codecompass knowledge trace
  <claim-id> --json` against a Claim with an exclusively-dangling
  citation now sees an extra gap entry that did not exist under this
  phase's already-`done`, already-once-corrected behaviour.
- **No test protects against it.** The one directly relevant,
  pre-existing test, `test_exclusively_dangling_supporting_evidence_
  is_a_gap` (written during the *first* corrective pass, `decisions/
  0092`, predating this amendment), only asserts `len(dangling) == 1`
  for the `dangling_evidence_reference` gaps — it never asserts the
  *absence* of a `missing_evidence` gap, nor the total gap count, so it
  silently continues to pass whether or not the new, extra gap is
  present. None of the 14 *new* tests this amendment adds exercise this
  specific combination either — `test_claim_level_tracing_is_
  unaffected_by_requirement_indirection` (the one new test whose name
  claims to cover exactly this) uses a Claim with **literally empty**
  `supporting_evidence: []`, not a *declared-but-dangling* one, so
  `has_direct_support` and the old `not supporting_ids` check agree for
  that fixture and the regression is invisible to it.
- `find_gaps()` itself has no separate `missing_evidence` detection block
  (confirmed via `grep -n "missing_evidence"
  src/codecompass/knowledge_api.py` — only the two sites inside
  `trace_evidence()`), so the corpus-wide `find_gaps()` scan is not
  independently affected — but `trace_evidence()`'s own per-subject
  behaviour, and everything built on it, is.
- This is exactly the risk category `CLAUDE.md` §8's governing agent
  instructions (and this project's own `L-086`/`L-108` precedent) direct
  an auditor to scrutinize with **full**, not lighter-touch, rigor: a
  corrective pass's *own newly-written code* (here, the refactor of
  `_resolve()` to return `any_resolved` and reuse it for the shared
  `has_any_support` check) introduced a side effect neither the
  implementing pass nor its own governing ADR anticipated or tested for.

**Result: FAIL.** This is a real, reproducible, user-visible behavioural
change inconsistent with this amendment's own explicit, repeated claim
that Claim-level tracing is unaffected, with no regression test
protecting against it.

## 4. Tests are real — spot-checked against the diff (6 of 14, exceeds
the 5 asked for)

Read the full test diff (`git diff 23f6826^ 23f6826 -- tests/
test_knowledge_api.py`) and reasoned each of the following against the
pre-fix source (`git show 23f6826^:src/codecompass/knowledge_api.py`,
read-only, never materialized):

1. `test_requirement_with_indirect_evidence_via_dependent_claim_is_a_
   result_not_a_gap` — pre-fix, a bare Requirement with no `supporting_
   evidence` field unconditionally hit `not supporting_ids` → `True` →
   `missing_evidence` gap, `status="gap"`. This test asserts
   `status="result"`, `gaps == []` — would genuinely have failed pre-fix.
2. `test_requirement_indirect_contradicting_evidence_is_surfaced` — same
   reasoning; pre-fix, no `contradicting_indirect`-role result could ever
   appear since the pre-fix function never read a Requirement's
   `depends_on` at all. Would have failed (`contradicting` list empty).
3. `test_requirement_with_unsupported_dependent_claim_is_a_gap_keyed_to_
   the_claim` — pre-fix, the gap's `subject_id` would be `REQ-IND-001`
   only (the one, undifferentiated Requirement-level `missing_evidence`
   gap); this test asserts `{g.subject_id for g in missing} ==
   {"CL-IND-001", "REQ-IND-001"}` — would have failed (missing the
   Claim-keyed gap entirely, since pre-fix code never iterates
   `depends_on`).
4. `test_requirement_with_dangling_dependency_reference_is_a_gap` —
   pre-fix, the `dangling_dependency_reference` `Gap.kind` did not exist
   in the function at all (confirmed: `grep` of the pre-fix blob for
   `dangling_dependency_reference` returns nothing) — would have failed
   (`dangling` list empty).
5. `test_real_requirement_resolves_indirect_evidence_through_dependent_
   claims` — the real-corpus reproduction; pre-fix this is the exact
   defect `decisions/0093` names (`REQ-BFS-001` reporting a false gap) —
   independently re-confirmed by me directly in §6 below, matching the
   test's own assertions.
6. `test_stale_citation_changed_implementation_suppresses_false_claim` —
   pre-fix, `aggregate_contract()`/`evaluate_result_precedence()` were
   called without `repo_root` (confirmed in the pre-fix blob at the
   equivalent call sites), so the fresher result's digest mismatch would
   never be checked against the live `impl.py`, and `stale_test_citation`
   would incorrectly fire; this test asserts `stale == []` — would have
   failed pre-fix (this project's own commit message independently
   confirms the same reasoning: "constructing a result with a
   deliberately wrong `tested_subject_digest` that produced identical
   output whether or not `repo_root` was supplied").

All six check out as genuine, discriminating regression tests. (The
7th-14th tests were not individually re-derived line-by-line but were
read in full and are consistent with the same diff-based reasoning —
no inconsistency found across any of the 14.)

**Result: PASS** for test authenticity on the two named defects — this
does not contradict §3's finding, since none of the 14 tests claim to
(or do) cover the Claim-level side effect named there.

## 5. No regression / no scope creep in untouched modules — confirmed;
one in-scope regression found (§3)

`git diff f22c16a 085a68c --stat -- src/codecompass/oracle.py
src/codecompass/graph.py src/codecompass/knowledge_intermediate.py`
produces zero output — these three files are genuinely untouched by
both commits, confirming `decisions/0093`'s own Consequences-section
claim on this specific point. Full changed-file list across both commits
(`git diff f22c16a 085a68c --stat`): `CHANGELOG.md`, `decisions/0093-...
.md`, `planning/phase-84-consolidated-knowledge-api.md`,
`planning/retros/phase-84-consolidated-knowledge-api.md`,
`src/codecompass/knowledge_api.py`, `tests/test_knowledge_api.py` — no
undisclosed file touched, matches the commit messages exactly.

`epistemic_status()` (lines ~1239 onward) is confirmed untouched by
either commit (the diff's hunks stop before this function and resume
only inside `find_gaps()`), matching `decisions/0093`'s claim it "already
resolved this correctly" and needed no change — read directly, not
inferred.

`TestNoMutationPath` (6 tests) re-run directly: `.venv/bin/python -m
pytest tests/test_knowledge_api.py -k NoMutation -q` → **6 passed**. No
new writer-function reference introduced (confirmed: the diff adds no
`sqlite3`/`write_*`/`accept_baseline` references anywhere).

**Result:** PASS for the three untouched modules and for the no-new-
mutation-path guarantee; **FAIL** for "no scope creep" as a whole, per
§3's Claim-level finding, which is squarely inside the one file this
amendment did touch.

## 6. Real-corpus re-demonstration — confirmed

Ran directly:
```
.venv/bin/python -c "
from pathlib import Path
from codecompass import knowledge_api as ka
r = ka.trace_evidence(Path('.').resolve(), 'REQ-BFS-001')
print(r.status, [(x.id, x.details.get('role'), x.details.get('via_claim')) for x in r.results], r.gaps)
"
=> result [('EV-BFS-001','supporting_indirect','CL-BFS-001'),
           ('EV-BFS-002','supporting_indirect','CL-BFS-001'),
           ('EV-BFS-001','supporting_indirect','CL-BFS-002'),
           ('EV-BFS-003','supporting_indirect','CL-BFS-002'),
           ('EV-BFS-002','supporting_indirect','CL-BFS-003'),
           ('EV-BFS-003','supporting_indirect','CL-BFS-003')] []
```
`status="result"`, zero gaps, all three real dependent Claims
(`CL-BFS-001`/`002`/`003`) traced with correct `via_claim` provenance —
confirms the originally-named defect is genuinely fixed against the real
corpus, not merely against synthetic fixtures. Also directly confirmed
`trace_evidence(REPO_ROOT, "CL-BFS-003")` (the real Claim that itself
`depends_on` other Claims) returns only its own two direct citations,
`via_claim=None` — Claim-subject tracing genuinely does not walk
`depends_on`, consistent with §1's bound (separately from the unrelated
§3 finding, which is about the `missing_evidence` *trigger condition*,
not about walking `depends_on`).

**Result: PASS.**

## 7. Verification commands re-run directly

```
.venv/bin/python -m pytest tests/test_knowledge_api.py -q
=> 79 passed in 3.16s

.venv/bin/python -m pytest tests/test_cli.py tests/test_oracle.py tests/test_knowledge_intermediate.py -q
=> 224 passed (run twice, consistent)

.venv/bin/python -m pytest -q   (full suite)
=> 1137 passed, 2 skipped in 274.26s

.venv/bin/python scripts/check_user_docs.py --strict
=> check_user_docs: no findings (exit 0)

.venv/bin/python scripts/check_contracts.py --strict
=> check_contracts: 7 finding(s), all [info]-level, identical to the
   corrective-pass audit's own §6 baseline above (exit 0)

.venv/bin/python scripts/check_knowledge_base.py --strict
=> check_knowledge_base: 24 finding(s), all [info]-level, identical to
   the corrective-pass audit's own §6 baseline above (exit 0)
```

All counts match exactly what the commit message, `decisions/0093`, the
plan §13, and the retro claim (79, not 65, tests; 1137 passed/2 skipped
full suite; both strict validators unchanged at 7/24 info-level findings).

**Also ran** (not requested, but relevant to §3): `.venv/bin/python -m
ruff check .` → 160 errors repository-wide (up from a pre-existing
baseline — see Non-blocking Observation 1 below), confirming via
`git show 23f6826^:...` comparison that this amendment adds only `E501`
(line-too-long) violations, no new `F`/`I`/`UP` category.

**Result: PASS** for all explicitly-requested verification commands.

## 8. Docs/changelog/plan/retro consistency — accurate for the two named
defects; FAILS to disclose the §3 finding (expected, since the §3 finding
was not itself known to the implementing pass)

`CHANGELOG.md`'s `[Unreleased]` → `Fixed` entry, `planning/phase-84-
consolidated-knowledge-api.md` §13, and the retro's "Final corrective
amendment" section all accurately describe what the code now does for
the two named defects — spot-checked against the source directly, no
discrepancy found for defect 1 or defect 2's own described behaviour.

The retro's "Correction (2026-11-02, final corrective amendment)"
paragraph (appended, not rewriting the original in place, per this
project's own append-only convention) correctly reconciles the earlier
retro's now-superseded "no new candidate learnings" claim against the
actual `L-108`/`L-109` promotion history — read in full, confirmed
accurate and genuinely non-destructive (the original paragraph is left
verbatim, the correction appended immediately after it).

**However**, per §3 above, every one of these four documents (the ADR,
the function docstring, the plan §13, the retro) repeats essentially the
same false claim — "Claim-level tracing ... is completely unaffected" /
"unaffected by any of this" — which is not a §8-specific drift (these
documents are *consistent with each other and with what the implementing
pass believed it had done*), but is a §3 code-behaviour finding that
necessarily also makes these same four documents inaccurate as a
description of the actual, current system. This is not scored as an
additional, independent failure in this section — it is the same single
underlying defect from §3, reflected in its own documentation, not a
second one — but it means fixing §3 will require a corresponding doc
correction pass across all four of these artifacts (code docstring, ADR,
plan, retro), not merely the code.

**Result:** PASS for descriptive accuracy of the two intentionally-fixed
defects; the Claim-level overclaim is §3's finding, not re-scored here.

## 9. Original audit and first corrective-pass audit content — confirmed
genuinely intact

`wc -l`/`md5sum` of `planning/retros/_audit-phase-84.md` immediately
before I began appending this section: 680 lines. `git log --oneline --
planning/retros/_audit-phase-84.md` (checked before any edit of my own)
showed exactly two commits ever touching this file
(`2698622`, the original audit; `fb057d7`, the first corrective-pass
addendum) — both sections above (the original "Phase 84 completion
audit" and "CORRECTIVE PASS AUDIT — 2026-10-29") are reproduced above
**verbatim**, byte-for-byte, with only this new section appended after
their existing final line. No existing content rewritten, reworded, or
removed.

**Result: PASS.**

## 10. Process disclosure — concurrent, uncommitted working-tree activity
observed during this audit (not mine; not touched)

At the time I began this audit, `git status --short` was clean. Partway
through (after running the real verification commands), `git status
--short` showed the following **uncommitted** changes that I did **not**
make and did **not** touch, inspect-only via `Read`/non-mutating `git
show`/`git diff` where relevant:

```
 M .claude/agents/release-phase-auditor.md
 M docs/reference/cli.md
 M planning/learnings/inbox.md
 M planning/learnings/promoted.md
 M planning/v1-redefinition/proposed-governance-changes.md
?? planning/retros/_drift-audit-phase-84-final-amendment.md
```

This is consistent with concurrent, in-progress work by other
specialist-agent dispatches on this same shared working tree (the exact
scenario this audit's own dispatch warned about) — most likely a
`docs-reconstructor` drift audit for this amendment (the untracked file
matches that naming convention exactly) plus `docs-maintainer`/
`knowledge-curator` follow-on work addressing it, none of it part of the
two commits (`23f6826`/`085a68c`) this audit evaluates. I read (but did
not modify) the untracked drift-audit file for informational purposes
only, per the task's own item 3 (confirming a `docs-reconstructor`
per-phase drift audit ran): as of this read, its own verdict is
**"DRIFT — 2 findings (both non-blocking)"**, not `NO DRIFT` — two
completeness gaps (`docs/reference/cli.md`'s `gaps` bullet omitting the
new `dangling_dependency_reference` gap kind; `planning/CONTEXT.md` not
yet mentioning this amendment, expected per the terminal-commit
exemption) — consistent with the `docs/reference/cli.md` modification
observed above being `docs-maintainer`'s in-progress fix for the first
of those two findings. Per `CLAUDE.md` §5, this condition ("every
finding it raised was fixed by `docs-maintainer` and re-audited") is
**not yet satisfied** as of this audit — it is visibly in progress, but
not yet re-audited to confirm, and not yet committed.

I did **not** run `git stash`, `git reset`, `git checkout <commit> --
<path>`, or any other tree-mutating command at any point in this audit.
Confirmed via `git status --short` immediately before finishing (see
below) that the only change attributable to me is this append to
`planning/retros/_audit-phase-84.md`; all five pre-existing modified
files and the one untracked file listed above are unchanged by my own
work, in whatever state the concurrent process left them.

**Result:** informational disclosure, not a pass/fail item of its own —
but it does mean the drift-audit DoD condition (item 3 of this audit's
own brief) cannot be scored a clean PASS as of this exact moment; see
"What must be fixed" below.

## Non-blocking observations

1. **`ruff check .` error count increase (99 → 120 `E501` violations in
   the two touched files)** is pre-existing-pattern debt, not a new
   category of problem: both the pre-fix and post-fix versions of
   `src/codecompass/knowledge_api.py`/`tests/test_knowledge_api.py`
   already violated the project's 100-character line-length convention
   at scale (104 total pre-fix, 125 post-fix, confirmed by running `ruff
   check` against both the current files and the pre-fix blobs saved to
   scratch space) — all `E501`, none `F`/`I`/`UP`. Not blocking since
   this project's own prior audits (see the two sections above) never
   treated `ruff check .` cleanliness as a gating condition for this
   module, and this amendment does not introduce a new violation
   category.

2. **The silent `if dep.kind != "claim": continue` skip** (§1 above) for
   a Requirement's `depends_on` entry that resolves to a non-Claim record
   is untested and undocumented as a deliberate choice (vs. an oversight)
   — not reachable in the current real corpus, so non-blocking, but
   worth a test and a one-line docstring note if a Requirement ever
   gains a non-Claim dependency in practice.

## What must be fixed before re-audit

This verdict is **FAIL** on the specific criterion: Defect 1's own fix
introduces an undisclosed, untested behavioural change to Claim-level
`trace_evidence()` tracing (§3), contradicting this amendment's own
explicit, repeated claim that Claim-level tracing is "completely
unaffected." Required before re-audit:

1. **Resolve the Claim-level behaviour itself**, by one of two routes:
   (a) restore the pre-amendment Claim-level trigger (missing_evidence
   fires only when the record's own citation list is **declared**-empty,
   i.e. revert to checking the *declared* id list for a Claim subject
   specifically, leaving the new *resolved*-based check active only for
   the Requirement indirect-evidence path), preserving `decisions/0092`'s
   own "declared is never conflated with resolved" principle exactly as
   it stood before this amendment; or (b) explicitly decide, document (a
   `decisions/0093` amendment or a fresh ADR), and test that both
   defects — a dangling citation *and* a missing-evidence finding — are
   now intentionally reported together for a Claim with no citation that
   actually resolves. Either is acceptable; silently shipping (b) without
   disclosing it, as currently committed, is not.
2. **Add a regression test** that pins down whichever behaviour is
   chosen for exactly the case `test_exclusively_dangling_supporting_
   evidence_is_a_gap` already exercises (a Claim whose only declared
   `supporting_evidence` id is dangling) — asserting the *total* gap
   count/kinds, not just the presence of the `dangling_evidence_
   reference` one, so a future change cannot silently alter this again
   unnoticed.
3. **Correct the "completely unaffected"/"unaffected by any of this"
   claim** in `decisions/0093`, the `trace_evidence()` docstring,
   `planning/phase-84-consolidated-knowledge-api.md` §13, and the retro's
   "Final corrective amendment" section to accurately state whichever
   resolution is chosen in (1).
4. Separately (not blocking re-audit of the above, but should be
   completed before this amendment's own closeout is airtight): land the
   in-progress `docs-reconstructor`/`docs-maintainer` work observed in
   §10 (commit the drift-audit report and its fixes, re-audit to confirm
   `NO DRIFT`, and reconcile `planning/CONTEXT.md`) via the terminal
   `roadmap-context-curator` reconciliation commit.

None of the above reopen the "Phase 84 completion audit" or "CORRECTIVE
PASS AUDIT — 2026-10-29" sections above, which concern different, already
-closed commits and are unaffected by this finding.

---

# FINAL CORRECTIVE AMENDMENT RE-AUDIT — 2026-11-02

**Auditor:** `release-phase-auditor` (same auditor, same amendment,
continuation of the "FINAL CORRECTIVE AMENDMENT AUDIT" section
immediately above, re-verifying the fix the lead applied in response to
that section's FAIL verdict — per `CLAUDE.md` §8's governing instruction,
this fix's own newly-written code gets full scrutiny, not a lighter-touch
re-check merely because it is "fixing something already found wrong").

**State audited:** the current, **uncommitted** working tree at
`/home/cormac/projects/codecompass` as of 2026-11-02. `git log` confirms
no new commit has landed since `085a68c` (still `HEAD`) — the fix
described below exists only as unstaged modifications to
`src/codecompass/knowledge_api.py`, `tests/test_knowledge_api.py`,
`decisions/0093-...md`, `planning/phase-84-consolidated-knowledge-api.md`,
and `planning/retros/phase-84-consolidated-knowledge-api.md`, plus the
separate, concurrent `.claude/agents/release-phase-auditor.md`,
`planning/learnings/{inbox,promoted}.md`,
`planning/v1-redefinition/proposed-governance-changes.md`, and
`docs/reference/cli.md` changes already disclosed as not-mine in §10
above (still present, still untouched by me). **This verdict applies to
the working-tree state as read; it must be re-confirmed against the
actual commit SHA(s) once this fix is committed**, per `CLAUDE.md` §5's
own rule that any commit touching audited scope after an audit voids
that audit.

**Verdict: PASS WITH NON-BLOCKING OBSERVATIONS.**

The root-cause fix is structurally sound, symmetric, and independently
confirmed to eliminate the exact regression §3 above found — by direct
re-execution of my own original repro, not merely by reading the lead's
summary of it. All explicitly requested verification commands re-run
clean with the expected counts. The new regression-guard test genuinely
would have caught the original bug (reasoned through, not merely
observed passing now). All four governing documents (`decisions/0093`,
the plan §13, the retro, and — separately — this agent's own definition
file for the new `L-111` item) gained honest, append-only correction
notes describing the FAIL and the fix, none of them silently rewriting
the original false claim. `L-110`/`L-111` are correctly triaged and
consistent with their own stated statuses. No regression in the wider
suite. The remaining non-blocking items are exactly the same closeout
items named in the prior section's own "What must be fixed" item 4
(still open, not reopened by this re-audit) plus the fact that none of
this is committed yet.

## 1. Repro scenario re-run directly against the fixed source — confirmed
exactly one gap

Re-ran my own exact original repro (the same scratch fixture from the
FAIL section, never recreated or altered):

```
>>> ka.trace_evidence(<scratch_root>, "CL-DANGLE-001")
   # supporting_evidence: [EV-MISSING-001] -- one declared, dangling citation
len(gaps) = 1
gaps = [Gap(kind='dangling_evidence_reference', subject_id='CL-DANGLE-001', ...)]
```

Exactly one gap, `dangling_evidence_reference` only — no `missing_
evidence` gap. This is the precise before/after contrast §3 established
(two gaps pre-fix, one post-fix), now confirmed against the *current*
source, not merely asserted by the lead's summary.

**Result: PASS.**

## 2. `trace_evidence()` source read directly — structurally sound for
the general declared-vs-resolved distinction, not just my one repro case

Read the current function in full (`src/codecompass/knowledge_api.py`
lines 1123-1249). The new shared signal:

```python
has_any_declared = bool(direct_supporting_ids)
if record.kind == "requirement":
    dep_ids = _ki._extract_id_strings(record.fields.get("depends_on", ""))
    if dep_ids:
        has_any_declared = True
    for dep_id in dep_ids:
        ...  # dangling_dependency_reference / per-Claim missing_evidence, unchanged
if record.kind in ("claim", "requirement") and not has_any_declared:
    ...  # top-level missing_evidence
```

Traced through every case by hand, not just the one repro:

- **Claim, no citation declared** (`supporting_evidence: []`):
  `has_any_declared = False` → top-level `missing_evidence` fires.
  Matches pre-amendment behaviour exactly (`not supporting_ids` was
  `True` for an empty list too) — confirmed via
  `test_claim_with_no_supporting_evidence_is_a_gap`, re-run, passes.
- **Claim, one citation declared, resolves**: `direct_supporting_ids`
  non-empty → `has_any_declared = True` → no top-level gap. Unchanged
  from pre-amendment (`not supporting_ids` was `False`) and from the
  buggy intermediate state (resolution succeeded, so both old and new
  signals agreed here) — confirmed via
  `test_claim_with_evidence_is_a_result_not_a_gap`, re-run, passes.
- **Claim, one citation declared, dangling** (the regression case):
  `direct_supporting_ids` non-empty → `has_any_declared = True` → no
  top-level gap, only `dangling_evidence_reference` from `_resolve()`.
  This is the one case that differed between pre-amendment and the buggy
  intermediate state, and the fix restores it to the pre-amendment
  value — confirmed in §1 above.
- **Requirement, no `depends_on` at all**: `direct_supporting_ids` is
  always empty for a Requirement (no such field exists in this
  project's schema) and `dep_ids` is empty too → `has_any_declared`
  stays `False` → top-level `missing_evidence` fires, with the now
  slightly-reworded reason "...and no `depends_on` citation either" —
  confirmed via
  `test_requirement_with_no_direct_and_no_indirect_evidence_at_all_is_
  still_a_gap`, re-run, passes.
- **Requirement, `depends_on` non-empty, target dangling**: `dep_ids`
  non-empty → `has_any_declared = True` unconditionally, *before* the
  loop even checks whether `dep_id` resolves — so a dangling
  `depends_on` target produces exactly one gap
  (`dangling_dependency_reference`), never also a redundant top-level
  `missing_evidence`. This is the Requirement-side mirror of the
  Claim-level fix, applied by the same mechanism (declaring something,
  even if it turns out broken, is `True`) — confirmed via
  `test_requirement_with_dangling_dependency_reference_is_a_gap`'s new
  `len(response.gaps) == 1` assertion, re-run, passes.
- **Requirement, `depends_on` non-empty, target resolves but is itself
  evidence-less**: `dep_ids` non-empty → `has_any_declared = True`
  regardless of whether the dependent Claim's own `claim_supporting_
  ids` is empty — so the Requirement's own top-level gap never fires
  here either, only the Claim-keyed `missing_evidence` gap from inside
  the loop. This is exactly the case the task asked me to re-verify
  (previously, before the original 23f6826 fix, keyed to both; the
  intermediate buggy state also keyed to both via the `has_any_support`
  resolution check; now keyed to the Claim only) — confirmed via
  `test_requirement_with_unsupported_dependent_claim_is_a_gap_keyed_to_
  the_claim`'s updated `{g.subject_id for g in missing} == {"CL-IND-
  001"}` assertion, re-run, passes.
- **Requirement, mixed supported + unsupported dependent Claims**:
  unaffected by this change either way — `dep_ids` non-empty already
  made `has_any_declared = True` even before this fix (since the buggy
  intermediate state's `has_any_support` was *also* `True` here, from the
  one genuinely-resolving Claim) — confirmed via
  `test_requirement_with_mixed_supported_and_unsupported_claims_keeps_
  resolved_evidence`, re-run unchanged, passes.

This is a single signal, computed once, before either the Claim or
Requirement branches read it — not two separately-patched special cases
that happen to agree on the cases tested so far. The fix is symmetric by
construction (one declared-vs-resolved rule, one variable), which is a
materially stronger property than "correct for the cases exercised,"
and directly addresses the general concern the task asked me to confirm,
not merely my one specific repro.

**Result: PASS.**

## 3. The two updated tests and the new regression-guard test — confirmed
correct, confirmed the guard is real

- `test_requirement_with_unsupported_dependent_claim_is_a_gap_keyed_to_
  the_claim`: updated assertion `{g.subject_id for g in missing} ==
  {"CL-IND-001"}` (previously `{"CL-IND-001", "REQ-IND-001"}`) is
  correct under the new symmetric rule — traced by hand in §2 above
  (REQ-IND-001 declared a `depends_on` citation, even though the Claim it
  names lacks its own evidence, so no redundant top-level Requirement gap
  fires). Re-run: passes.
- `test_requirement_with_dangling_dependency_reference_is_a_gap`: gained
  `assert len(response.gaps) == 1` — correct per the same reasoning
  (declaring a `depends_on` citation, even a dangling one, is still
  "something declared"). Re-run: passes.
- `test_exclusively_dangling_supporting_evidence_produces_exactly_one_
  gap` (new): asserts `len(response.gaps) == 1` and
  `response.gaps[0].kind == "dangling_evidence_reference"` for a Claim
  with `supporting_evidence: ["EV-MISSING-999"]`. **Reasoned through
  whether this would have caught the original bug** (not merely checked
  that it passes now): against the buggy intermediate source (the state
  I audited in the FAIL section, where the shared signal was
  resolution-based `has_any_support`), this exact fixture has
  `direct_supporting_ids = ["EV-MISSING-999"]` (non-empty, declared) but
  `_resolve()` returns `any_resolved = False` (the id never resolves) —
  so `has_any_support` would have been `False`, the top-level
  `missing_evidence` gap would have fired *in addition to* the
  `dangling_evidence_reference` one, `len(response.gaps)` would have been
  `2`, and this test's own `assert len(response.gaps) == 1` would have
  failed. This is a genuine, discriminating regression guard for exactly
  the shape of bug found, not a test that happens to pass under both the
  buggy and fixed code.

**Result: PASS.**

## 4. `tests/test_knowledge_api.py` re-run — 80 passed, nothing else
broken

```
.venv/bin/python -m pytest tests/test_knowledge_api.py -q
=> 80 passed in 3.78s
```

Matches the expected count exactly (79 → 80, the one new regression-guard
test). No other test's outcome changed — re-read the full diff
(`git diff 085a68c -- tests/test_knowledge_api.py`) and confirmed it
contains exactly the three changes named in §3 above (one new test, two
updated assertions) and nothing else; no test was deleted, skipped, or
had its fixture silently altered.

Also re-ran the full repository suite as requested:

```
.venv/bin/python -m pytest -q
=> 1138 passed, 2 skipped in 270.23s (0:04:30)
```

Matches the expected count exactly (1137 → 1138, the same one new test;
2 skips unchanged, same pre-existing environment-dependent skips named in
earlier sections of this report).

**Result: PASS.**

## 5. Real corpus re-check — `REQ-BFS-001` unaffected by the fix

```
.venv/bin/python -c "... ka.trace_evidence(Path('.').resolve(), 'REQ-BFS-001') ..."
=> result [(...6 entries, all via_claim in {CL-BFS-001,CL-BFS-002,CL-BFS-003}, role='supporting_indirect'...)] []
```

Identical to the result obtained in the FAIL section's own §6 (same
`status="result"`, same zero gaps, same three `via_claim` provenance
values) — confirmed byte-for-byte unchanged by re-running the exact same
command, not merely asserting it should be unaffected. This is expected:
`REQ-BFS-001`'s own `depends_on` (`CL-BFS-001`/`002`/`003`) are all
real, resolving Claims each carrying real `supporting_evidence`, so
`has_any_declared` is `True` via the `dep_ids`-non-empty branch exactly
as it would have been under either the buggy or the fixed signal — this
real-corpus case was never actually at risk from either version of the
bug, which only manifests for a *dangling* or *entirely absent*
citation, not a correctly-resolving one.

**Result: PASS.**

## 6. `decisions/0093`, plan §13, and retro correction notes — confirmed
honest, append-only, consistent with each other

- `decisions/0093`'s new "## Correction (2026-11-02, same-day independent
  re-audit)" section (read in full via `git diff 085a68c -- decisions/
  0093-...md`): names the regression precisely (shared `has_any_support`
  signal switched from declared- to resolution-based, affecting the Claim
  path too), names who caught it (the `release-phase-auditor` re-audit,
  verdict FAIL, cited by file path), names why the amendment's own 14
  tests missed it (`test_claim_level_tracing_is_unaffected_by_
  requirement_indirection`'s empty-list fixture couldn't see a
  declared-but-dangling case), and describes the fix accurately
  (symmetric `has_any_declared`, not two separately-patched special
  cases) — matches my own §2 findings above exactly, independently
  arrived at.
- `planning/phase-84-consolidated-knowledge-api.md` §13 gained a
  matching "**Correction (2026-11-02, same-day re-audit, FAIL then
  fixed)**" paragraph, appended after the existing §13 content, not
  rewriting it — confirmed via `git diff 085a68c -- planning/phase-84-
  consolidated-knowledge-api.md`, pure addition.
- The retro's "Final corrective amendment" section gained a "**Correction
  (2026-11-02, same-day re-audit)**" paragraph (confirmed via `git diff
  085a68c -- planning/retros/phase-84-consolidated-knowledge-api.md`)
  that explicitly says "both paragraphs above were wrong, left in place
  uncorrected in situ" (matching this project's own established
  append-only amendment convention, same pattern already used once in
  this same retro file for the unrelated `L-108`/`L-109` miss) and
  additionally discloses the separate `L-110`/`L-111` filing (item 7
  below) under the same correction, rather than only the code regression
  — a more complete correction than the task's own phrasing strictly
  asked for, not a narrower one.

All three are genuinely honest (name the FAIL, name the auditor, name
the mechanism, name the fix) rather than a silent rewrite of the
original "completely unaffected" claim, and are mutually consistent with
each other and with the actual code — cross-checked, not merely each
read in isolation.

**Result: PASS.**

## 7. `L-110`/`L-111` — confirmed correctly filed and consistent with
their own stated statuses (new item, outside original audit scope)

- **`.claude/agents/release-phase-auditor.md`**: confirmed item 12 was
  actually added (`git diff 085a68c -- .claude/agents/release-phase-
  auditor.md`), reading the live text of my own agent definition
  directly rather than trusting the diff summary: a new numbered item
  "For a function (or dogfood demonstration) whose own logic branches by
  which kind/variant of a shared record or input type it receives,
  confirm the phase's own tests exercise the function directly against
  each kind it claims to handle..." — placed correctly as item 12,
  immediately after item 11 (`L-108`'s own item), matching the inbox
  entry's own "promoted_to" description exactly, word for word.
- **`planning/learnings/inbox.md`**: `L-111`'s entry has `status:
  promoted`, a substantive, non-stub `observation` (the three-independent-
  ways-missed account: no pre-amendment `TestTraceEvidence` test used a
  Requirement id; the dogfood test routed a Requirement through
  `traverse(..., "depends_on")` but the evidence-tracing half through a
  Claim; `TestContextPacket`'s pre-existing tests did pass a Requirement
  id but asserted only on `items`/`bounds`, never `gaps`/`status`) and a
  genuine `knowledge-curator` curation note recommending promotion with
  the exact text that was in fact added — not a generic placeholder.
  `L-110`'s entry has `status: candidate` (correctly **not** `promoted`
  — it proposes a `CLAUDE.md` §1 change, which `CLAUDE.md` §0 requires
  explicit user approval for before it is written; `knowledge-curator`'s
  write boundary never includes `CLAUDE.md` directly, matching how
  `L-087`/`L-088` were routed in prior phases), with a three-occurrence
  recurrence account (`L-105` Phase 83; `decisions/0092` Phase 84 first
  corrective pass; `decisions/0093` this same phase's final amendment)
  that I independently re-checked against each cited source
  (`src/codecompass/knowledge_api.py` lines ~1380-1443 for the `repo_
  root`-threading sites named) and found accurate.
- **`planning/learnings/promoted.md`**: contains exactly one new line
  for `L-111` (`scoped-rule | .claude/agents/release-phase-auditor.md
  "What to check" item 12 ...`), correctly omitting `L-110` (not yet
  promoted, consistent with its `candidate` status in `inbox.md`) —
  confirmed via direct read, no inconsistency between the two files.
- **`planning/v1-redefinition/proposed-governance-changes.md`** gained a
  new "## K. 2026-11-02 proposed addition (Phase 84 final corrective
  amendment — `L-110`, extends `L-105`)" section with the exact proposed
  `CLAUDE.md` §1 sentence, explicitly marked "**Status:** proposed, not
  yet presented to the user" — consistent with `L-110` correctly sitting
  at `candidate`, not `promoted`, and consistent with `CLAUDE.md` §0's
  own protected-file rule (no direct edit to `CLAUDE.md` itself observed
  anywhere in this working tree — confirmed via `git status --short`,
  `CLAUDE.md` does not appear in the modified-file list).

**Result: PASS.** Both candidate learnings are filed, evidenced, and
triaged to statuses consistent with this project's own promotion rules;
nothing jumped ahead of the explicit-approval gate `CLAUDE.md` §0
requires for a `CLAUDE.md` change.

## 8. Strict validators — unchanged

```
.venv/bin/python scripts/check_contracts.py --strict
=> check_contracts: 7 finding(s) (exit 0) -- identical to every prior
   baseline in this report

.venv/bin/python scripts/check_knowledge_base.py --strict
=> check_knowledge_base: 24 finding(s) (exit 0) -- identical to every
   prior baseline in this report

.venv/bin/python scripts/check_user_docs.py --strict
=> check_user_docs: no findings (exit 0)
```

**Result: PASS.**

## Non-blocking observations (carried forward / new)

1. **Nothing described in this re-audit is committed yet.** `git log`
   confirms `HEAD` is still `085a68c`; every file discussed in §§1-7
   above (the code fix, the three test changes, the three documentation
   corrections, and — separately — the `L-110`/`L-111`-related files) is
   an uncommitted working-tree modification. This verdict is necessarily
   provisional on what actually gets committed and in what shape — per
   `CLAUDE.md` §5's own rule, any further edit to this audited scope
   after this re-audit (beyond a clean commit of exactly what was read
   here) voids this verdict and requires a fresh pass. Recommend: commit
   this fix as its own `fix(phase-84): ...` commit (plus a paired `docs(
   phase-84): ...` commit for the correction notes, matching this
   project's own established two-commit pattern for the original
   amendment), then have this report's verdict checked against the
   actual resulting SHA before treating the amendment as closed.

2. **The drift-audit reconciliation named as item 4 in the prior
   section's "What must be fixed" is still open.** `planning/retros/
   _drift-audit-phase-84-final-amendment.md` (still untracked) still
   reads verdict **"DRIFT — 2 findings (both non-blocking)"** — it has
   not been re-run/updated to `NO DRIFT` even though `docs/reference/
   cli.md`'s own Finding 1 (the missing `dangling_dependency_reference`
   mention in the `gaps` bullet) now appears fixed in the working tree
   (confirmed via `git diff 085a68c -- docs/reference/cli.md`: the
   `gaps` bullet now names `dangling_dependency_reference` explicitly,
   and the `trace` bullet gained a new sentence describing the
   Requirement indirect-evidence resolution). Finding 2 (`planning/
   CONTEXT.md` not yet mentioning this amendment) remains open, expected
   per the terminal-commit exemption. **Not blocking this specific
   re-audit's verdict** (this re-audit's scope, per the lead's own
   dispatch, is the Claim-level regression and its fix, items 1-7 above,
   all of which independently PASS) — but still required, as already
   named, before the amendment's own closeout is airtight.

3. Both non-blocking observations carried over unchanged from the prior
   "FINAL CORRECTIVE AMENDMENT AUDIT" section (the pre-existing `ruff`
   `E501` baseline increase; the untested `if dep.kind != "claim":
   continue` edge case) remain accurate and unaffected by this fix —
   re-checked, nothing about this specific correction touches either.

## Summary for the lead

**Verdict: PASS WITH NON-BLOCKING OBSERVATIONS.** The Claim-level
regression found in the prior "FINAL CORRECTIVE AMENDMENT AUDIT" section
is genuinely, correctly, and symmetrically fixed — independently
re-derived from the current source (not trusted from the lead's own
summary), re-executed against my own original repro with the opposite
result (one gap, not two), traced by hand across every case the general
declared-vs-resolved distinction touches (not just the one repro), and
locked in by a new regression-guard test I confirmed would genuinely have
caught the original bug. `tests/test_knowledge_api.py` (80 passed, up
from 79) and the full suite (1138 passed/2 skipped, up from 1137) both
re-run clean; all three strict validators unchanged; the real corpus
(`REQ-BFS-001`) unaffected. `decisions/0093`, the plan file, and the
retro each gained an honest, append-only correction — no silent rewrite
of the original false claim anywhere. The separately-raised `L-110`/
`L-111` candidate learnings are correctly filed and triaged to statuses
consistent with this project's own promotion rules (`L-111` promoted to
this agent's own "What to check" item 12; `L-110` correctly held at
`candidate`, routed through `proposed-governance-changes.md` §K, pending
the explicit user approval `CLAUDE.md` §0 requires for any `CLAUDE.md`
change).

Before this amendment's own closeout is complete, the lead should:
1. Commit this fix (code + tests + the three documentation corrections)
   as its own commit(s), then have the resulting SHA(s) checked against
   this report's own findings — this verdict was reached against the
   working tree, not yet a commit.
2. Land the still-open drift-audit reconciliation (observation 2 above;
   unchanged from the prior section's item 4) via the terminal
   `roadmap-context-curator` reconciliation commit.
3. If/when `L-110` is presented to the user for `CLAUDE.md` §0 approval,
   confirm the §K draft text in `planning/v1-redefinition/proposed-
   governance-changes.md` is what actually gets presented, unmodified.

None of the above reopen the "Phase 84 completion audit," "CORRECTIVE
PASS AUDIT — 2026-10-29", or "FINAL CORRECTIVE AMENDMENT AUDIT" sections
above, which concern different, already-evaluated states and are
unaffected by this re-audit's own findings.
