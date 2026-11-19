# Audit — Phase 89, Stage 89B ("New gap kind + real documentation-cascade demonstration")

**Audited state:** working tree at dispatch time, on top of committed
`61591f4` (Stage 89A, both corrective passes). Stage 89B's own
implementation (`src/codecompass/knowledge_api.py`,
`src/codecompass/source_reconciliation.py`, `src/codecompass/cli.py`,
`tests/test_knowledge_api.py`) was **staged/modified in the working
tree, not yet committed**, at the time of this audit — confirmed via
`git diff HEAD --stat` for each file; no commit hash exists yet for this
work, matching the governing dispatch's own framing of this as an
independent, from-scratch audit of a not-yet-closed deliverable.

**Auditor:** `release-phase-auditor` (independent, read-only pass; never
the implementer).

**Scope:** Stage 89B's own named deliverables only (plan §5.4's new
`claim_contradicted_by_fresh_check` `find_gaps` gap kind; the real
Ledgerkit documentation-invalidation cascade demonstration for both
existing detectors, plan §6.2's doc-invalidation leg). Does not
re-litigate Stage 89A or either of its two corrective passes (see
`planning/retros/_audit-phase-89-stage-89a.md` for that history — all
confirmed sound there, including a fourth, process-completeness-only
pass completed by this same auditor immediately before this report).

## Verdict

**FAIL.**

The new gap kind's own detection logic, its read-only guarantee, its
scope-eligibility exclusions (aggregate/superseded Claim, tampered
result, already-applied/rejected item, duplicate-manifest
deduplication), and the real documentation-invalidation cascade this
stage builds on top of unmodified Phase 87 machinery are all genuinely
sound — independently reproduced below, not merely read or trusted from
the implementer's own demonstration log. The FAIL is one real,
independently confirmed, user-facing defect in this stage's own new
`cli.py` change: **the plain-text (non-`--json`) output of
`codecompass knowledge gaps` silently drops the new `label` field**
(`"regression"`/`"newly_discovered_failure"`) for every gap of this new
kind, because the new code embeds `f" [{g.label}]"` directly into a
`rich` `console.print()` call without escaping it, and `rich` interprets
`[regression]`/`[newly_discovered_failure]` as (invalid, silently
dropped) markup tags rather than literal text. This defeats the gap
kind's own stated purpose — the plan's own §5.4 rationale, and this
stage's own doc-string, both explicitly justify the label's existence as
"so a human is never told something broke that was never shown to have
worked" — for exactly the output mode a human running the plain CLI
command (not `--json`) actually sees. Zero test coverage anywhere in
`tests/test_cli.py` exercises this rendering path, so nothing caught it
before this audit.

## What was independently reproduced, not merely read

All work below ran against either a disposable scratch Python fixture
(no project-tracked path touched) or a disposable `cp -r
~/projects/ledgerkit <scratch>/ledgerkit` + disposable scratch copies of
`planning/knowledge/balance-from-spec/`/`planning/contracts/
balance-from-spec/` (never the real checkouts). The real
`~/projects/ledgerkit` checkout (`git status --porcelain` empty, `git
rev-parse HEAD` = `a7740fd04fe1814d2a557bfcb67a9a775a4a22f9`) and this
repository's own real `planning/knowledge/balance-from-spec/`/`planning/
contracts/balance-from-spec/` (`git status --porcelain` empty for both
paths) were confirmed clean both before this audit's work began and
after it concluded.

### 1. The new gap kind's correctness (own scratch fixture, independent of the project's own test suite)

Built a from-scratch fixture (project root, `oracle-contract.yaml`,
two Claims — `CL-AUDIT-001` eligible, `CL-AUDIT-002` an aggregate
Claim via `depends_on: ["CL-AUDIT-001"]` — and a real, freshly-executed
`FAIL` `OracleResult` via the real `oracle.evaluate_check`/
`oracle.write_oracle_result`, never a hand-typed result file) and a
hand-written manifest citing it for both Claims. Confirmed, by directly
calling `knowledge_api.find_gaps`:

- Exactly one gap reported, for `CL-AUDIT-001` only, `label="regression"`
  — **the aggregate Claim `CL-AUDIT-002` is never reported**, even
  though an identical pending item exists for it in the same manifest.
- **Read-only**: `md5`/byte-for-byte comparison of the manifest file and
  the Claim file before and after the scan — unchanged.
- **Tampered-result exclusion**: built a second, fully independent
  fixture (a tampered `OracleResult`'s own `raw_output_ref` file content
  no longer matching its recorded `raw_output_sha256`, confirmed first
  that the *untampered* case is genuinely reported, then tampered and
  re-ran) — the gap correctly disappears once tampered. (Caught and
  fixed one mistake in my own first draft of this reproduction — copying
  a project directory tree does not relocate an `OracleResult`'s own
  absolute `raw_output_ref` path, so the first attempt tampered a file
  the scan never actually reads; the corrected, from-scratch
  `evaluate_check` fixture avoided this.)
- **Disappears once applied**: set `decision = "accept"` and ran the
  real `knowledge_intermediate.apply_manifest` — the gap disappears for
  `CL-AUDIT-001` immediately after.

Also ran the project's own 11 dedicated tests directly
(`tests/test_knowledge_api.py -k ClaimContradictedByFreshCheck`): **11
passed**. Read every test body in full (not only the names) — each
genuinely exercises what it claims, including the rejected-item,
already-applied, duplicate-manifest-deduplication, and
stale-duplicate-already-resolved-via-sibling cases this audit's own
from-scratch fixture did not separately re-derive.

### 2. A real Ledgerkit reproduction (detector (a), CL-BFS-002 regression — independently re-run end to end)

Against a disposable scratch Ledgerkit + disposable scratch
`balance-from-spec` knowledge/contract copies, via the real
`/home/cormac/projects/codecompass/.venv/bin/codecompass` CLI (not a
direct Python call):

1. `codecompass sync --yes` — graph populated correctly (confirmed via
   direct `sqlite3` query); the known, non-fatal `anthropic` SDK
   `TypeError` (no API key configured in this environment) printed,
   exit code 0 (`L-081`/`L-136`'s own already-documented behaviour,
   unrelated to this stage).
2. `detect-changes --establish-baselines --json` against the clean,
   unmutated checkout — baseline recorded.
3. Applied the real sign-inversion mutation (`reports.py`'s own `if
   section.invert:` guard disabled). Confirmed directly via the scratch
   checkout's own `pytest`: `test_multi_section_correct_values` fails
   (`Decimal('-6000.00') != Decimal('6000.00')`); `test_single_
   section_rows_and_subtotal` is unaffected — exactly as the
   demonstration log claims.
4. Re-synced the one changed file's content hash; `detect-changes
   --json` → `symbol_change` for `ledgerkit/reports.py`, exactly as
   claimed.
5. `verify-changes --json` → one-item manifest,
   `record_id = "CL-BFS-002"`, `contributing_labels = ["regression"]`,
   `contributing_target_fields = ["contradicting_evidence"]`, citing a
   real, freshly-executed `FAIL` `OracleResult` — the manifest file's
   raw content was read directly, not just the JSON summary.
6. **`codecompass knowledge gaps --repo-root <scratch>`, before any
   review** — the new `claim_contradicted_by_fresh_check` gap for
   `CL-BFS-002` fires correctly in `--json` output (`"label":
   "regression"`), confirmed byte-for-byte unchanged manifest/Claim
   files before and after (`md5sum -c`). **This is also where the
   plain-text-output defect (verdict, above) was found**: the
   equivalent non-JSON `codecompass knowledge gaps` invocation never
   prints the `[regression]` suffix at all — confirmed by raw byte
   inspection (`od -c`) of the actual command output, and independently
   confirmed via a direct Python call to `cli._print_api_response` with
   a wide `rich.Console` and a short reason string (ruling out terminal
   line-wrapping as an alternative explanation) and via a minimal
   `rich` repro (`console.print('hello [regression] world')` → `'hello
   world'`, the bracketed word silently vanishes).
7. Accepted and applied → `applied: recomputed evidence_support_
   state='conflicting'; evidence: EV-BALANCEFROMS-004` — confirmed via
   direct read of `CL-BFS-002.yaml`: `supporting_evidence:
   [EV-BFS-001, EV-BFS-003]` (preserved, not erased),
   `contradicting_evidence: [EV-BALANCEFROMS-004]`,
   `evidence_support_state: conflicting`. `find_gaps` re-run
   immediately after: the gap for `CL-BFS-002` correctly disappears.

### 3. The documentation-invalidation cascade's mechanical leg (real, unmodified Phase 87 code, no AI call available in this environment)

No `ANTHROPIC_API_KEY` is configured in this environment and this
auditor has no agent-dispatch capability of its own, so the AI-composed
drafting and independent-review legs of `docs compile`/the
`general-purpose` review dispatches could not be independently
re-run end to end (the same constraint any credential-less audit would
face). The genuinely mechanical legs — which do not require an AI
call, and which this audit confirmed by reading `doc_compiler.
compile_document`'s own control flow directly before relying on it —
were independently reproduced, against the real, already-mutated
`CL-BFS-002` record from step 2 above:

- Hand-published (via the real, unmodified `doc_compiler.
  publish_section`, never an AI call) two grounded regions in a
  disposable scratch document — one citing `CL-BFS-002`, one citing the
  untouched control `CL-BFS-001` — and established their baseline via
  the real `doc_compiler.maintain_document`.
- Mutated `CL-BFS-002`'s own on-disk content a second time (a harmless,
  real content touch) and re-ran `maintain_document`: **`claims_changed
  == ["id:audit-demo-bfs002"]`**, **`noop == ["id:audit-demo-bfs001"]`**
  — the correct region, and only that region, flips; the unrelated
  control region stays `noop`. Restored the Claim file to its real
  post-apply content afterward.
- Separately confirmed the pre-existing `contradiction` gap-kind
  check inside `doc_compiler.find_section_gaps`/`compile_document`
  (unmodified by this stage — `git diff HEAD --stat` for
  `doc_compiler.py` is empty) correctly short-circuits to
  `gap_blocked` for the `CL-BFS-002` section **before** ever reaching
  the AI composition step — proved this by passing a
  `compose_and_validate` stub that raises if called at all, and
  confirming the `CL-BFS-002` section's own result never reaches that
  stub (status `gap_blocked`, gap list includes `"contradiction"`),
  while a comparison section not involving a contradicted Claim does
  reach the stub (confirmed it is the only one whose gap list excludes
  `"contradiction"`).
- Confirmed the pre-existing `concurrent_conflict` protection
  (`detect_grounded_region_changes`'s own four-way case logic,
  unmodified by this stage) fires correctly when a region's own prose
  is hand-edited *and* its cited Claim's content changes in the same
  window: `concurrent_conflicts == ["id:audit-demo-bfs002"]`, the
  hand-edit preserved byte-for-byte, the unrelated region unaffected.

These three mechanical reproductions, together, independently confirm
the demonstration log's own central documentation-cascade claims
(correct-region-only `claims_changed`, unrelated-region `noop`,
contradiction-gap blocking, concurrent-edit protection) using the real
production code against the real, already-mutated `balance-from-spec`
records — the only leg not independently re-run is the AI-composition/
independent-review leg itself, for the stated credential/capability
reason, not because it was skipped as unimportant.

### 4. Governance/scope checks

- `git diff HEAD --stat -- src/codecompass/doc_compiler.py
  src/codecompass/knowledge_intermediate.py` — **empty for both.** The
  pre-existing `contradiction`/`concurrent_conflict` mechanisms
  exercised above are genuinely untouched by this stage, confirmed by
  diff, not merely by the stage's own documentation claiming so.
- `grep -n "^import\|^from" src/codecompass/source_reconciliation.py` —
  no `mcp` import anywhere; the new `PendingContradiction`/
  `pending_contradicting_findings` code imports only `contextlib`/`os`/
  `re`/`sqlite3`/`subprocess`/dataclasses/`datetime`/`Path` plus
  `codecompass.change_impact`/`knowledge_intermediate`/`oracle` — no new
  documentation compiler, knowledge store, or scheduler introduced.
- `git diff HEAD --stat -- planning/retros/
  phase-89-ledgerkit-two-task-demonstration.md` — empty. `grep -rn
  "claim_contradicted_by_fresh_check\|pending_contradicting_findings"`
  against that file — zero matches. Stage 89C (Task B's own
  pre-registration) is untouched and unaltered.
- `tests/test_source_reconciliation.py` (Stage 89A's own integrity
  suite): re-ran directly — **75 passed**, unchanged in count and
  behaviour from the figure Stage 89A's own prior audits established.
- Real `~/projects/ledgerkit` and this repository's own real
  `planning/knowledge/balance-from-spec/`/`planning/contracts/
  balance-from-spec/`: confirmed clean (`git status --porcelain`) both
  before this audit's work began and after it concluded.

## Test / validator / ruff counts — reproduced directly

- **Focused new tests**: `tests/test_knowledge_api.py -k
  ClaimContradictedByFreshCheck` → **11 passed**.
- **Full suite**: `.venv/bin/python -m pytest tests/ -q` →
  **`4 failed, 1546 passed, 2 skipped in 476.18s`** — matches the figure
  named in the governing dispatch exactly. All four failures are the
  known, pre-existing `tests/test_execute_doc_example.py::test_real_*`
  environmental failures (`@requires_real_sandbox`, no `codecompass` on
  `PATH`/no network for `pip` in this environment) — not a regression
  from this stage (that test file is untouched by this stage's own
  diff). Collected-total arithmetic: this run's `1546 + 4 + 2 = 1552`;
  Stage 89A's own last-confirmed figure (the fourth audit above, via a
  clean `61591f4` worktree) was `1541`; `1552 - 1541 = 11`, exactly
  matching this stage's own 11 new tests.
- **`scripts/check_knowledge_base.py`**: 24 informational
  `knowledge-base-snapshot-current-divergence` findings, exit 0 —
  identical in kind and count to every prior Phase 89 audit's own
  observation, none newly introduced.
- **`scripts/check_contracts.py`**: 7 informational findings (6
  `contract-result-integrity-mismatch`, 1 `contract-check-gap`), exit 0
  — identical to every prior Phase 89 audit's own observation.
- **`ruff check .`**: **167 errors** — unchanged from the established
  whole-repo baseline. **`ruff check src/ tests/`**: **163 errors** —
  unchanged from the established scoped baseline. **`ruff check
  src/codecompass/knowledge_api.py src/codecompass/source_
  reconciliation.py src/codecompass/cli.py tests/test_knowledge_api.py`**
  (the four files this stage actually touches): **130 errors** — exactly
  matching the sum of each file's own already-known pre-existing count
  (68 + 0 + 5 + 57, per the third Stage 89A audit's own baseline
  table) — **zero new `ruff` findings introduced by this stage's own new
  code**, at every scope checked.

## What must be fixed before re-audit

1. **Fix the plain-text `codecompass knowledge gaps` output's silent
   loss of the new `label` field.** The one-line change at
   `src/codecompass/cli.py`'s `_print_api_response` (`label_suffix =
   f" [{g.label}]" if g.label else ""` then embedded directly in
   `console.print(f"...{label_suffix}")`) must escape the label before
   interpolation (e.g. `rich.markup.escape(g.label)`, or avoid `rich`
   markup parsing for this string entirely, e.g. via `console.print(
   ..., markup=False)` for this specific call, or a plain `print()`) —
   confirmed via direct, repeated reproduction (both the real CLI's
   actual output and a minimal, isolated `rich.Console` repro) that
   `[regression]`/`[newly_discovered_failure]` are currently silently
   dropped, not merely visually wrapped, by `rich`'s markup parser.
2. **Add a dedicated test** (`tests/test_cli.py` or equivalent) asserting
   the plain-text `gaps` command's own rendered output genuinely
   contains the literal label text for a labelled gap — the complete
   absence of any such test is why this defect reached this audit
   uncaught; the fix in (1) should not be treated as done until a
   regression test exists that would have caught it.
3. Re-run the full suite, both validators, and `ruff check .` after the
   fix (expected to be unaffected in every figure above except the
   `cli.py` test count, which should increase by whatever this stage
   adds in item 2).

No other item blocks this verdict. The gap kind's own detection logic,
read-only guarantee, scope-eligibility exclusions, and the real
documentation-cascade mechanics it feeds are all independently confirmed
sound, via genuine reproduction against real Ledgerkit records and the
real, already-mutated `balance-from-spec` knowledge base — not merely
read or trusted from the implementer's own demonstration log.

---

# Re-audit — 2026-11-19 (focused re-check of the plain-text label-escaping fix)

**Auditor:** `release-phase-auditor` (independent, read-only pass; never
the implementer). **Scope:** narrow, as dispatched — verify only that
the required fix from the FAIL verdict above (the plain-text
`codecompass knowledge gaps` output silently dropping the new `label`
field, because of an unescaped `f" [{g.label}]"` suffix interpreted by
`rich` as markup) is genuinely complete and correct. Does not re-verify
the new gap kind's own detection logic, read-only guarantee,
scope-eligibility exclusions, or the documentation-cascade mechanics —
all independently confirmed sound by the audit above and not re-checked
here.

## Verdict

**PASS.**

## What was independently reproduced, not merely read

1. **Read the fix directly** (`src/codecompass/cli.py`,
   `_print_api_response`): `from rich.markup import escape as
   _rich_escape` is imported, and the gap-rendering line now reads
   `label_suffix = _rich_escape(f" [{g.label}]") if g.label else ""`
   followed by `console.print(f"[red]gap[/red] ({g.kind}) {g.subject_id
   or ''}: {g.reason}{label_suffix}")` — the *entire* bracketed suffix
   (including the literal `[`/`]` characters) is escaped before
   interpolation, not just `g.label`'s own text, which is exactly what
   the FAIL verdict's required-fix item 1 specified. `git diff HEAD --
   stat -- src/codecompass/cli.py` confirms this is a minimal, scoped
   change (+12/-1 lines, one new import plus the one rendering line),
   no other scope creep.
2. **Ran the real CLI end to end against a disposable scratch fixture**
   (built via direct calls to the real `codecompass.oracle`/
   `codecompass.knowledge_intermediate` — contract, Claim, a genuine
   `OracleResult` persisted via `oracle.write_oracle_result`, and a
   hand-written pending `source_reconciliation` manifest item with
   `contributing_labels: ["regression"]` — the same fixture shape
   `tests/test_cli.py`'s own new regression test builds, reproduced
   independently, not merely re-run as the existing test):
   - `codecompass knowledge gaps clidemo --json` → the
     `claim_contradicted_by_fresh_check` gap's JSON payload correctly
     carries `"label": "regression"`.
   - `codecompass knowledge gaps clidemo` (plain text, no `--json`) →
     raw byte inspection via `od -c` on the actual process output
     confirms the literal text `[regression]` genuinely appears at the
     end of the corresponding line (`...that has not yet been reviewed
     [regression]\n`) — not swallowed, not merely visually present
     through terminal-wrapping luck (checked the raw bytes, not a
     rendered terminal).
3. **Ran the dedicated new test directly**:
   `.venv/bin/python -m pytest tests/test_cli.py::
   test_knowledge_gaps_plain_text_output_shows_the_label_not_swallowed_by_rich_markup
   -q` → `1 passed`.
4. **Confirmed the test would have genuinely failed against the
   original, unescaped construction** — reproduced the exact historical
   defect shape directly with `rich.console.Console` in a disposable
   scratch Python snippet (never reverting any tracked file), using the
   real pre-fix code pattern verbatim: `label_suffix = f" [{g.label}]" if
   g.label else ""` embedded in `console.print(f"[red]gap[/red] (...)
   {...}{label_suffix}")`. Result: `'[regression]' in output` →
   `False` — the bracketed label is silently dropped, exactly matching
   the audit's own original finding. Also reproduced the "insufficient
   first fix attempt" the fix's own code comment and `CHANGELOG.md`
   both reference (escaping only `g.label`'s inner text, e.g.
   `f" [{escape(label)}]"`, leaving the surrounding literal brackets
   unescaped): this too silently drops `[regression]` — confirming the
   currently-landed fix (escaping the *whole* bracketed suffix,
   brackets included) is the one that actually matters, not an
   incidental detail.
5. **Confirmed `CHANGELOG.md`'s own account of this fix** (the entry
   describing the defect, the fix, the rejected insufficient first
   attempt, and the new dedicated test) matches the real code and test
   file content in every particular checked above — no discrepancy
   found.

## Validator/test/ruff counts — re-run directly by this pass

- `.venv/bin/ruff check .` → **167 errors** — unchanged from the
  established whole-repo baseline (compared directly against the figure
  this same audit file's own prior section, and the Stage 89A audit
  history, both independently derived).
- `.venv/bin/python -m pytest -q` (full suite, from the repo root) →
  **4 failed, 1547 passed, 2 skipped in 469.94s** — the 4 failures are
  the pre-existing `tests/test_execute_doc_example.py::test_real_*`
  environmental failures (`@requires_real_sandbox`, no `codecompass` on
  `PATH`/no network for `pip` in this environment), matching the figure
  named in the governing dispatch exactly and consistent with every
  prior Phase 89 audit round's own account of these same four failures
  as pre-existing and unrelated to any work in this phase.

## Scope/governance check

`git status --porcelain` before and after this pass's own work is
identical (confirmed directly) — no tracked file was modified by this
audit; all reproduction happened against disposable scratch paths under
this session's own scratchpad directory, deleted afterward. This
section is appended at the end of this file with no existing line
edited or removed — confirmed via `git diff --stat` showing only
insertions for this file both before and after this section was
written.

