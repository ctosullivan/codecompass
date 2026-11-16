# Independent review — Phase 88 real-MCP-client acceptance exercise

**Reviewer:** context-evaluator subagent (independent of the exercise's own
implementer/narrator)
**Scope:** verify, from primary sources only, whether the real-Claude-CLI
MCP-client exercise for Phase 88 ("Agent Integration and MCP") produced
genuine, accurate, materially useful tool calls/results, and whether the
client's own self-reported summary is honest.

**Method:** Everything below was established by reading the target files
directly — ledgerkit source, fixtures, tests, CodeCompass knowledge YAML,
and the raw transcript JSONL — and by running my own independent `pytest`
invocations. `codecompass query`/`check`/`/discovery` were never invoked to
decide correctness.

---

## 1. Ground truth, established independently

- Real checkout `/home/cormac/projects/ledgerkit`: `git status --porcelain`
  and `git diff --stat` both empty. **Confirmed untouched.** HEAD =
  `a7740fd04fe1814d2a557bfcb67a9a775a4a22f9`, matching both scratch copies'
  pinned revision.
- `ledgerkit/reports.py::balance_from_spec` (line 600), the account-pattern
  inclusion gate at line 663 reads exactly
  `if not any(_matches_pattern(pat, posting.account) for pat in section.accounts): continue`
  — a single boolean OR-gate, append-once. This matches CL-BFS-004's
  statement verbatim (including the quoted line number and source text).
- `tests/fixtures/filtered.journal`: `expenses:food:groceries` posting is
  £150.00, `expenses:food:coffee` is £9.00. `_matches_pattern` (line 213)
  is a case-insensitive infix/substring `HledgerRegex` match, so for
  `accounts=("food","groceries")`: the groceries posting matches **both**
  patterns, the coffee posting matches **only** "food". Independently
  computed correct subtotal: 150.00 (groceries, once) + 9.00 (coffee,
  once) = **159.00**; a double-count bug would instead double the
  groceries row to 300.00 and the subtotal to 309.00.
- The pre-existing neighbouring test `test_section_multiple_accounts_patterns_or_union`
  (line 810) does indeed assert only `assertIn`/`assertNotIn` posting
  membership, never a subtotal — confirmed by direct reading. This is
  exactly what DEC-BFS-002's rationale claims.
- `ledgerkit-mutated`'s diff vs `ledgerkit-correct`: the gate is replaced
  with `_match_count = sum(1 for pat in section.accounts if
  _matches_pattern(...)); if _match_count == 0: continue` plus `for _ in
  range(_match_count): pairs.append(...)` — i.e. counts once per matching
  pattern. This is exactly Phase 83's documented mutation
  (`planning/retros/phase-83-semantic-change-assurance.md` ~L96-110,
  including its own quoted figures).
- My own `pytest` runs:
  - `ledgerkit-correct`: `.venv/bin/python -m pytest -q` → **936 passed,
    14 subtests passed** (full suite clean, new test included).
  - `ledgerkit-mutated` (new test already applied there via the
    exercise's own `git apply`, confirmed present at line 826):
    `.venv/bin/python -m pytest -q` → **1 failed, 935 passed, 14 subtests
    passed**; the one failure is exactly
    `test_section_accounts_overlapping_patterns_no_double_count`, with
    `AssertionError: Decimal('300.00') != Decimal('150.00')`.
  - These numbers match the transcript's own reported figures (session1
    tool_result for the full-suite run: `936 passed, 14 subtests passed`)
    exactly, and match Phase 83's already-documented 300/150 mismatch
    exactly.

## 2. Are the MCP calls genuine (not simulated)?

Yes, with strong corroborating evidence, not just transcript self-report:

- Both transcripts' `system/init` records list the actual connected MCP
  server (`"mcp_servers":[{"name":"codecompass","status":"connected","source":"dynamic"}]`)
  and the real tool manifest exposed over stdio:
  `mcp__codecompass__server_capabilities`, `knowledge_get`,
  `knowledge_search`, `knowledge_traverse`, `knowledge_trace_evidence`,
  `knowledge_context_packet`, `knowledge_epistemic_status`,
  `knowledge_find_gaps`, `docs_get_grounded_region`, `oracle_list_checks`,
  `oracle_execute_check`, `impact_classify_change` — 12 tools, matching
  the `mcp-*.json` configs' `codecompass mcp-serve` invocation.
- `session0-sanity.log` records a genuine **permission-denial** (`"tool_name":
  "mcp__codecompass__server_capabilities"`, with `"result":"I don't have
  permission to call that tool yet..."`) from an actual Claude CLI
  `claude -p` run accounting block (`total_cost_usd`, `cache_read_input_tokens`,
  etc. — fields only the real CLI emits), followed by a second sanity run
  where the same call succeeds and returns the real JSON. This is not
  reproducible by a scripted demo narrating fake tool names.
- Representative real tool-call → real tool-result pairs I read directly
  (abbreviated):
  - `mcp__codecompass__server_capabilities` → `{"repo_root_keys":["ledgerkit","ledgerkit-mutated"],"execution_enabled":false,"codecompass_version":"1.0.0"}` (session 1), later `"execution_enabled":true` (session 2).
  - `mcp__codecompass__oracle_list_checks{"slug":"balance-from-spec"}` → real on-disk allowlist with 3 checks under `contract_id REQ-BFS-001`, two `"latest_result_status":"PASS"` and the third `"GAP"`.
  - `mcp__codecompass__knowledge_get{"record_id":"DEC-BFS-002",...}` → the full YAML content (decides/rationale) verbatim-matching the file I read directly in `planning/knowledge/balance-from-spec/DEC-BFS-002.yaml`.
  - `mcp__codecompass__oracle_execute_check{"slug":"balance-from-spec","contract_id":"REQ-BFS-001","check_id":"overlapping-account-patterns-no-double-count","repo_root_key":"ledgerkit"}` (session 1, execution disabled) → `"Error executing tool oracle_execute_check: oracle_execute_check is disabled -- this server was started without --enable-execution (the default, read-only mode)"` — clean, correctly-typed permission error, no crash, no silent no-op.
  - Same call, session 2 (execution enabled), `repo_root_key="ledgerkit"` → `{"outcome":"PASS","aggregate_state":"PASS","raw_output_ref":"planning/contracts/balance-from-spec/results/raw/overlapping-account-patterns-no-double-count--20261115T235946730617Z-79e694ea.txt",...}`.
  - Same call, `repo_root_key="ledgerkit-mutated"` → `{"outcome":"FAIL","aggregate_state":"GAP",...}` — a genuinely different real result for a genuinely different pinned target, exactly as expected.

These are real, differentiated, per-target JSON payloads with run IDs and
result-file references — consistent with a real server actually re-running
pytest against two distinct on-disk checkouts, not a canned script.

## 3. Did DEC-BFS-002 (not generic background) materially shape the assertion?

Yes, genuinely, and the client's own claimed reasoning is accurate rather
than post-hoc. DEC-BFS-002's rationale (quoted directly from the YAML)
states the existing `test_section_multiple_accounts_patterns_or_union`
"asserts only posting membership, never the resulting subtotal
arithmetic — so no test anywhere in Ledgerkit would catch a posting
matching more than one pattern being counted more than once." I
independently confirmed that exact fact by reading that test myself
(line 810-822): it is indeed `assertIn`/`assertNotIn` only. The client's
step-4 answer ("`DEC-BFS-002` materially shaped the assertion — it's the
reason the test must check the *computed amount/subtotal*, not
membership") is a correct, specific, falsifiable claim, not generic
filler — and it matches what I found by my own independent read. REQ-BFS-002's
own worked example (`accounts=("food","groceries")` against the £150.00
posting) also directly supplied the exact scenario and numbers the client
used; the client explicitly cited and quoted it rather than inventing
numbers, and I confirmed those numbers (150.00/159.00) are correct by
independently re-deriving them from the fixture and `_matches_pattern`
semantics.

## 4. Honesty / overclaim check

No overclaiming found; if anything the client under-claimed and flagged a
real discrepancy rather than smoothing it over:

- Step 7 (`impact_classify_change`): the client correctly noticed the
  third check (`overlapping-account-patterns-no-double-count`) does not
  get its own check-level classification entry in the `assurance` array
  (only the two already-passing checks do); instead `CL-BFS-004` is
  tiered `relevant_no_coverage_link` with `check_id: null`. The client
  reported this precisely rather than papering over it or claiming a
  clean three-way classification it didn't get.
- Step 11 (`knowledge_epistemic_status` for `REQ-BFS-002`, called
  immediately after step 9's fresh `oracle_execute_check` **PASS**): the
  returned record still listed **all three** scopes under
  `known_gap_scopes` with `verified_scopes: []` — i.e. it had **not**
  absorbed the just-obtained fresh PASS result. The client explicitly
  called this out in its own words ("it has **not** picked up step 9's
  fresh `PASS` result... whatever ingestion/reindex step folds a fresh
  `oracle_execute_check` result back into `knowledge_epistemic_status`
  has not run"), rather than quietly asserting the knowledge system is
  self-updating. I verified this is exactly what the raw JSON shows.
- No documentation region (`README.md`, `docs/`) mentions `CL-BFS-*`,
  `DEC-BFS-*`, or `REQ-BFS-*` (grep returns nothing) — confirmed the
  context here could only have come from knowledge-graph records, never
  published docs. The client never called `docs_get_grounded_region` at
  all in either session (not in the 26 session-1 or 4 session-2 tool
  calls), so there is no "manufactured relevance" to check — it simply
  didn't reach for that tool, consistent with there being nothing there.
- All of the client's reported pass/fail counts, PASS/FAIL/GAP outcomes,
  and the pasted test body match the real diff and my own independent
  pytest runs exactly, with no rounding, hedging, or embellishment.

## 5. A genuine, narrow observation (not a manufactured defect)

`knowledge_epistemic_status` not reflecting a just-completed
`oracle_execute_check` PASS (§4 above) is a real, reproducible-from-the-
transcript asymmetry worth the lead's attention. It is plausibly
*intentional* under this project's own L-087 convention (CLAUDE.md §1: a
persisted baseline "may advance only when an explicit apply or
acknowledgement action succeeds, never merely because a detection/scan
step ran") — i.e. an oracle run is a detection step, and promoting
`REQ-BFS-002` to `verified` would need a separate, explicit
knowledge-curation action. But if that is *not* the intended design, this
is a real staleness gap between `oracle_execute_check` and
`knowledge_epistemic_status` that could mislead a future agent into
believing a freshly-passing check is still an open gap. I note it as an
observation for the lead to classify, not as a confirmed bug — I did not
go looking for this; it surfaced directly from reading the two adjacent
real tool results.

## Verdict

**PASS.** Every tool call inspected is a genuine, differentiated, real
MCP round-trip (not simulated); every arithmetic assertion in the new
test is independently verifiable as correct; `DEC-BFS-002` genuinely and
specifically (not generically) shaped the exact assertion written; my own
independent pytest reproductions match the transcript's claimed figures
exactly in both the correct and mutated scratch copies; the real
`~/projects/ledgerkit` checkout is confirmed untouched; and the client's
own self-reported summary contains no overclaim — it proactively
surfaced a real knowledge-staleness asymmetry rather than hiding it.

## Context-advantage rating: **HIGH**

Could a fresh Claude session have gotten this cheaply with a couple of
greps? No. The decisive fact driving the correct assertion — that the
*only* existing OR-union test in the entire Ledgerkit suite checks
membership and never arithmetic, making this a genuine, previously
unrecorded blind spot rather than a merely plausible-sounding one — is
not discoverable by reading `reports.py` alone; it required DEC-BFS-002's
already-done cross-check against `test_reports.py`'s full test class, an
oracle contract (`oracle_list_checks`) distinguishing which of three
near-identical-looking checks genuinely lacks a passing result, and a
freshly-executed, target-pinned oracle run that discriminates the correct
checkout from the mutated one with a real, different result. A fresh
agent re-deriving this from scratch would have to (a) read the whole test
file to notice the membership-only gap itself, (b) independently
hypothesize the exact overlapping-pattern double-count risk, and (c) have
no equivalent of a live, re-executable, target-aware oracle to confirm it
discriminates correct from broken behaviour. The knowledge retrieval here
materially shortened and de-risked that path, and the real, differentiated
PASS/FAIL oracle results (§2) are not reproducible by static
file-reading at all.

## Material gaps

- `knowledge_epistemic_status` does not reflect a freshly-executed,
  passing `oracle_execute_check` result within the same session (§5) —
  worth an explicit design confirmation (intentional detection/apply
  split, or a real staleness bug) rather than leaving it ambiguous.
- `impact_classify_change`'s `assurance` array silently omits any entry
  for a check whose underlying claim has `check_id: null`
  (`relevant_no_coverage_link`), rather than surfacing a third,
  explicit "no linked check, cannot classify" assurance row alongside the
  two `VERIFICATION_GAP` rows — not wrong, but a asymmetry in how the
  three checks under the same contract are presented that a less careful
  agent might misread as "only two checks exist."

## Would this have misled the implementing agent? **no**

Both the knowledge records and the real oracle results were accurate and
consistent with ground truth; the one genuine asymmetry found (§5) was
caught and honestly reported by the client itself in the same turn it
arose, not left to mislead a subsequent reader.
