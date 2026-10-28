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
