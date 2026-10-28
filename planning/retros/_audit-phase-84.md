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
