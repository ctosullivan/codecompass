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


---

# Re-audit — 2026-11-20 (independent re-verification against committed HEAD `88b6e30`; three targeted concerns from a subsequent source review)

**Auditor:** `release-phase-auditor` (independent, read-only pass; never
the implementer; does not trust the two prior sections' own narrative,
re-reproduces material claims directly). **Scope:** re-verify Stage
89B's committed implementation at `88b6e30` end to end (Part A/B of the
governing dispatch), investigate three specific concerns a subsequent
source review raised (Part C: an unavailable-checkout suppression gap
in `pending_contradicting_findings`; an authored-prose-vs-structured-
state inconsistency surfaced via `get()`/`get_context_packet()`; a
missing explicit unrelated-source negative control for the full
documentation-reconciliation chain), and re-confirm quality/completeness
(Part D).

## Verdict

**FAIL.**

Two independently confirmed, real, blocking defects — one correctness
gap (C.1) and one process/governance-completeness gap this pass found
while re-verifying DoD item 5 (candidate-learnings triage), which
neither prior audit section above checked for Stage 89B at all. C.2 and
C.3 are not blocking (see below — C.3 is a real, now-closed process gap,
not a code defect; C.2 is a confirmed design fact, not a defect). Full
suite, both strict validators, `ruff`, and committed-source-drift are
all unregressed and match the prior audit's own figures exactly.

## Part A/B — re-verification of the prior PASS's own material claims

All independently reproduced again, with my own fixtures (not merely
re-reading the prior sections' account):

- **`pending_contradicting_findings`/`claim_contradicted_by_fresh_check`
  correctness** (own from-scratch fixture, mirroring but not reusing
  `tests/test_knowledge_api.py`'s own fixture helpers): a genuine FAIL
  `OracleResult`, written via the real `oracle.evaluate_check`/
  `write_oracle_result`, cited from a hand-written pending manifest item
  with `contributing_labels: ["regression"]`, correctly surfaces exactly
  one gap, labelled `"regression"`, via a direct `knowledge_api.
  find_gaps` call. Read-only confirmed (no file touched by the scan).
  Ran the dedicated 11 tests directly: `tests/test_knowledge_api.py -k
  ClaimContradictedByFreshCheckGap` → **11 passed**.
- **Plain-text CLI label-escaping fix still holds**: `src/codecompass/
  cli.py` lines 1976-1977 still read `label_suffix = _rich_escape(f"
  [{g.label}]") if g.label else ""` / `console.print(f"...{g.reason}
  {label_suffix}")` — unchanged since the prior re-audit. Ran
  `tests/test_cli.py -k label_not_swallowed` directly → **1 passed**.
- **Real Ledgerkit documentation-cascade mechanics** (disposable scratch
  Ledgerkit + disposable scratch `balance-from-spec` knowledge/contract
  copies, never the real checkouts): built a fresh disposable schema-
  governed document, published and baselined a region citing
  `CL-BFS-001` via the real `doc_compiler.publish_section`/
  `maintain_document` (no AI call needed for this mechanical leg),
  confirmed `established_new` on first run. This scratch setup was then
  reused directly for C.3 below.
- **Governance**: `git diff --stat -- src/codecompass tests/` since the
  commit this file's prior sections examined shows **no change** — the
  committed source this pass examined is byte-identical to what the
  prior two audit sections examined (`git log --oneline -1 -- src/
  codecompass/source_reconciliation.py src/codecompass/knowledge_api.py
  src/codecompass/cli.py tests/test_knowledge_api.py tests/test_cli.py`
  → `d25371a`, unchanged). No ADR/`CLAUDE.md` drift (`git diff --stat
  d86f93e..88b6e30 -- decisions/ CLAUDE.md` → empty).

## Part C — the three targeted concerns

### C.1 — Unavailable verification checkout silently suppresses a pending contradiction. **CONFIRMED REAL AND BLOCKING.**

Reproduced directly with a from-scratch fixture (two byte-identical
projects, differing only in the manifest item's own recorded
`repo_root` string): a genuine, freshly-executed FAIL `OracleResult`
cited by a pending `source_reconciliation` manifest item.

- With `repo_root` pointing at the fixture's own (reachable) project
  directory: `find_gaps` reports exactly one
  `claim_contradicted_by_fresh_check` gap, `label="regression"`.
- With the identical fixture, only the manifest item's own `repo_root`
  field changed to a path that does not exist (e.g. a cleaned-up
  scratch checkout): `find_gaps` reports **zero** gaps of this kind for
  this item — confirmed via `src/codecompass/source_reconciliation.py`
  lines 1207-1210 (`item_repo_root = Path(item_repo_root_str) if
  item_repo_root_str else repo_root; if item_repo_root is None or not
  item_repo_root.is_dir(): continue`): this `continue` drops the entire
  loop iteration for this finding, before any FAIL/PASS re-validation
  is even attempted, with **no gap of any kind, and no error, raised in
  its place** — a genuinely pending, unreviewed, unapplied contradiction
  becomes invisible to `find_gaps` purely because the checkout it was
  originally verified against is not reachable *right now*, which is
  exactly the false "no gaps found" impression the dispatch's own
  concern describes.
- This directly contradicts an established, already-landed precedent
  two files away in the same module family: `knowledge_intermediate.
  _apply_source_reconciliation`'s own identical "repo_root missing or
  no longer exists" condition (line ~2750) explicitly **fails closed**
  — it refuses to apply and returns `ApplyOutcome(False, item, "cannot
  re-validate against the target checkout: repo_root is missing or no
  longer exists -- refusing to apply (fail-closed)")`, a visible,
  actionable signal — never a silent, unreported absence. The new gap
  kind's own scanning function does the opposite: it disappears the
  finding instead of surfacing "could not be live-reconfirmed."
  `knowledge_api.find_gaps`'s own pre-existing `stale_test_citation`
  gap kind already has the exact wording convention this new gap kind
  should mirror (`knowledge_api.py` lines ~1753-1757): `verification_
  note = "live-reconfirmed against the current implementation" if
  repo_root is not None else "contract-relative only -- not live-
  reconfirmed; no repo_root supplied"`.
- **Recommended minimal fix** (not implemented by this pass, per
  instruction): when `item_repo_root` is unavailable, do not `continue`
  past the whole finding. Instead, fall through and re-validate the
  cited result with `repo_root=None` (contract-relative only, via the
  same `evaluate_result_precedence` call already used two lines below)
  — if it still re-validates as `FAIL` on that weaker, contract-relative
  basis, still report the gap, with the `reason` text qualified using
  the same "contract-relative only -- not live-reconfirmed" phrasing
  `stale_test_citation` already established, rather than either
  silently dropping it or claiming a live reconfirmation that never
  actually happened. This mirrors `_apply_source_reconciliation`'s own
  fail-closed philosophy (never represent "could not verify" as either
  "confirmed" or "silently resolved") without copying its specific
  refuse-to-apply behaviour, which is not appropriate for a read-only
  detection function.

### C.2 — Claim prose vs. structured verification state. **Confirmed design facts, not a defect — reported for Stage 89C planning.**

Built a disposable scratch copy of the real `balance-from-spec`
knowledge base plus a disposable scratch Ledgerkit copy (the real
overlapping-pattern test added, confirmed passing against the real,
unmutated checkout, then a real `oracle.evaluate_check` run produced a
genuine PASS `OracleResult`), to directly compare `knowledge_api.get`/
`get_context_packet` before and after simulating Task A's own effect on
the real `CL-BFS-004` (adding a test-kind Evidence citation,
`evidence_support_state: partially_supported` → `supported` — never the
real repository, confirmed clean before and after):

- **`_apply_source_reconciliation`'s own docstring confirms the design
  is intentional**: "`statement`/`derivation`/`timestamp`/every other
  field is never touched." The real `CL-BFS-004.yaml`'s own authored
  `statement` genuinely still says "not yet" tested after the
  simulated mutation — confirmed directly (`"not yet" in fields
  ["statement"]` → `True` post-mutation).
- **`get()`'s one-line `summary`** (`_summarize_record`, reads straight
  off the `statement` field, truncated to 280 chars) reflects **only**
  the stale authored prose, pre- and post-mutation identically — never
  the derived `evidence_support_state`. The raw `evidence_support_state`
  field itself **is** visible, but only via `get()`'s own
  `details.fields` dict (`_get_knowledge_record` includes the full
  `dict(record.fields)`).
- **`get_context_packet()`'s own per-item `details`** is a reduced
  subset — `{"slug": ...}` only, confirmed directly by inspecting the
  real packet JSON — **never** the raw `fields` dict, so
  `evidence_support_state` is **not** exposed anywhere in a context
  packet item, only indirectly via its own `consistency` envelope.
- **Whether `consistency.status` differs pre/post, and whether
  `repo_root` is required to see that**: for this specific real Claim,
  it does **not** differ at all, with or without `repo_root` —
  `consistency.status` is `"unconfirmed"` in all four combinations
  tested (pre/post × with/without `repo_root`). Root cause, confirmed by
  reading `derive_epistemic_profile` directly (`knowledge_intermediate.
  py` lines ~1245-1266): it loops over **every** check in the slug's
  whole oracle contract, not only the scope(s) a given Claim actually
  claims to cover. `CL-BFS-004` cites no Evidence at all for the other
  two required checks in `balance-from-spec`'s contract
  (`single-section-expense-subtotal`, `multi-section-income-expense-
  subtotal`), so `known_gap_scopes` is always non-empty for this record
  regardless of Task A, which routes `_knowledge_consistency` to
  `status="unconfirmed"` unconditionally (pre: `"3 required scope(s)
  have no passing evidence at all"`; post, no `repo_root`: `"1 scope(s)
  have only a historically recorded PASS, not live-reconfirmed"`; post,
  reachable `repo_root`: `"2 required scope(s) have no passing evidence
  at all"` — the now-verified scope silently drops out of the reason
  text once it stops being a gap). **`evidence_currency`/`reasons` do
  differ pre/post, visibly, without needing `repo_root`** — so a reader
  of `get()`'s `consistency.reasons` (not `status`) could notice Task
  A's effect without `repo_root`; a reader of `get_context_packet()`'s
  coarser per-item `consistency.status` field alone could not, with or
  without `repo_root`, for this specific real Claim — this is an
  artifact of this pre-existing (not Stage-89B-introduced) "profile
  against the whole contract" behaviour, not of Task A or Stage 89B's
  own new gap kind. Not a Stage 89B defect; a fact Stage 89C's own
  context-packet-generation design needs to account for directly if it
  relies on `status` (rather than `reasons`/`evidence_currency`) to
  detect an evidence-state change.

### C.3 — Missing explicit end-to-end unrelated-source negative control. **Confirmed genuinely missing from both stages' own retros; closed by this pass.**

`grep -n "noop\|unrelated"` against both Stage 89B retro files finds
only "unrelated *region*" checks (a sibling region staying `noop` while
a *different*, actually-changed region in the same document correctly
flips) — never an entirely unrelated *source* edit chained all the way
through `docs maintain`. Stage 89A's own retro (`phase-89-stage-89a.md`)
names an "unrelated file edit... confirmed nothing proposable" negative
control, but that predates Stage 89B's documentation cascade entirely —
it never runs `docs maintain` at all. Ran the full chain myself, for
real, against a disposable scratch Ledgerkit + disposable scratch
`balance-from-spec` knowledge/contract copies + a disposable schema-
governed document (one region citing `CL-BFS-001`, hand-published via
`doc_compiler.publish_section`, baselined via `maintain_document`):
appended a genuinely new, unrelated function to `ledgerkit/writer.py`
(not in the contract's `tested_paths`/any check's `test_input_paths`),
updated its `context-graph.db` content hash directly (the established
lightweight re-sync technique), then:

- `detect-changes --probe-coverage --json` → `"changed": []`,
  `"new_files": []` — nothing detected.
- `verify-changes --json` → `"proposed_findings": 0`,
  `"manifest_path": null` — no manifest written at all.
- `md5sum` of every `balance-from-spec` Claim/Evidence/contract file,
  before and after → byte-identical — zero canonical mutation.
- `docs maintain` → `noop: ['id:single-section-subtotal']`, every other
  outcome list empty — the one grounded region correctly reported
  `noop`, never `claims_changed`/`doc_candidate`.

Full chain (unrelated source change → zero reconciliation → zero
canonical mutation → zero documentation invalidation) confirmed, for
real, for the first time across either stage's own retros. Real
`~/projects/ledgerkit` and the real `planning/knowledge/balance-from-
spec`/`planning/contracts/balance-from-spec` confirmed untouched
throughout (`git status --porcelain` empty for both, before and after).

## An additional defect this pass found while re-verifying DoD item 5 (not one of the three dispatched concerns). **CONFIRMED REAL AND BLOCKING.**

`planning/retros/phase-89-stage-89b.md`'s own "Candidate learnings
filed" section states: "One new candidate learning naming the
composer-prompt-generalization finding above (see `planning/learnings/
inbox.md` for its exact id, filed alongside this stage's own triage of
`L-135`/`L-136` from Stage 89A...)." **This is false.** `grep -n
"Stage 89B\|89b\|composer" planning/learnings/inbox.md planning/
learnings/promoted.md` → **zero matches**. The highest learning id
anywhere in `inbox.md` is `L-137` (Stage 89A's own third-audit triage,
confirmed filed and promoted correctly — see that file's own content).
`planning/learnings/candidates/` is empty. `CHANGELOG.md`'s own Stage
89B entry does not mention a candidate learning being filed either.
Neither of the two prior audit sections in this same file checked DoD
item 5 (candidate-learnings triage) for Stage 89B at all — an omission
from both prior checklists, not a re-introduced regression. Per
`CLAUDE.md` §5, a phase/stage is not done until "candidate learnings
from the phase — including any surfaced by the retro — have been
triaged by the `knowledge-curator`." The retro's own prose already
identifies the substance of the candidate (the composer-prompt
hedging/mechanism-overclaim generalization gap found during the real
AI-composition iteration) in its "Lessons learnt" section — only the
actual filing-and-triage step named in "Candidate learnings filed"
never happened.

## Full suite / validator / ruff — reproduced directly, this pass

- **`pytest -q`** (full suite, repo root): **`4 failed, 1547 passed, 2
  skipped in 467.31s`** — identical to the prior re-audit's own figure.
  All 4 failures confirmed genuinely environmental by reading what they
  actually assert, not merely trusting the label: `tests/
  test_execute_doc_example.py::test_real_bare_codecompass_against_a_
  zero_candidate_fixture_is_deterministic`/`test_real_budget_zero_
  against_toy_project_refuses_before_any_api_call`/`test_real_query_
  vendors_shows_both_fixture_vendors_as_used` all fail with `env:
  'codecompass': No such file or directory` (no `codecompass` on
  `PATH` inside the `unshare`/`pivot_root` sandbox in this environment)
  and `test_real_pip_install_succeeds_fully_offline` fails with `ERROR:
  No matching distribution found for codecompass-context` (no network
  access for `pip` in this environment) — both genuinely environmental,
  unrelated to any Stage 89B code, confirmed by reading the actual
  assertion failures directly, not merely the test names.
- **`scripts/check_knowledge_base.py`**: 24 informational
  `knowledge-base-snapshot-current-divergence` findings, exit 0 —
  unchanged.
- **`scripts/check_contracts.py`**: 7 findings (6 `contract-result-
  integrity-mismatch`, 1 `contract-check-gap`), exit 0 — unchanged.
- **`ruff check .`**: **167 errors** — unchanged from the established
  baseline.
- **Committed-source drift check**: `git log --oneline -1 -- src/
  codecompass/source_reconciliation.py src/codecompass/knowledge_api.py
  src/codecompass/cli.py tests/test_knowledge_api.py tests/test_cli.py`
  → `d25371a` (no later commit touches these files); `git status
  --porcelain -- src/codecompass tests/` → empty throughout this pass's
  own work.
- **No Stage 89C implementation work exists**: confirmed no
  `ReportSpec`/combined-section changes anywhere in `~/projects/
  ledgerkit` (clean, `a7740fd04fe1814d2a557bfcb67a9a775a4a22f9`
  throughout), and `git diff --stat -- planning/retros/phase-89-
  ledgerkit-two-task-demonstration.md` since Stage 89A → empty.
  **Disclosed, non-blocking observation**: during this pass's own work,
  the live working tree (not caused by, or interacted with by, this
  pass beyond observing) picked up two *uncommitted* changes unrelated
  to Stage 89B — `planning/ROADMAP.md` (Stage 89C row updated to note an
  implementation-ready *plan*, not implementation) and a new, untracked
  `planning/phase-89-stage-89c-task-b-controlled-comparison.md` plan
  file — consistent with `CLAUDE.md` §1's "plan before implementing"
  and explicitly describing itself as "planning only; Stage 89C itself
  is not started." This is **Stage 89C planning**, not implementation,
  landing concurrently in the same live repository while this audit ran
  (presumably the lead's own parallel work) — it touches neither
  Stage 89B's own audited files (`src/codecompass/`, `tests/`, Stage
  89B's own retro/audit files) nor this pass's own verdict, and this
  pass did not revert, edit, or otherwise interact with it beyond this
  observation.
- **Self-disclosed incident, confirmed harmless**: this pass's own
  scratch-reproduction shell command for C.3 contained a scripting
  error that briefly ran a real `codecompass --yes sync` against the
  real repository root (instead of only the intended disposable scratch
  Ledgerkit copy), for approximately two minutes before being killed by
  this pass once noticed. Confirmed afterward: `git status --porcelain`
  showed no tracked file touched by this (only the two unrelated,
  pre-existing Stage 89C planning changes above, and gitignored
  `context-graph.db`/vendor-digest regeneration); `sqlite3 PRAGMA
  integrity_check` on the real repository's own regenerated
  `context-graph.db` → `ok`. No ANTHROPIC_API_KEY is configured in this
  environment, so no real paid API call could have completed even had
  Phase B enrichment triggered. Disclosed for completeness, not because
  it affected any audited finding.

## What must be fixed before re-audit

1. **C.1 — fix `source_reconciliation.pending_contradicting_findings`'s
   silent suppression of a pending contradiction when the manifest
   item's own recorded `repo_root` is unreachable.** Never represent
   "could not be live-reconfirmed" as "no gap" — surface it, qualified,
   mirroring `stale_test_citation`'s own already-established "contract-
   relative only -- not live-reconfirmed" wording convention, rather
   than silently dropping the entire finding via the current `continue`.
2. **File and triage the candidate learning `planning/retros/
   phase-89-stage-89b.md`'s own "Candidate learnings filed" section
   already claims exists** (the composer-prompt hedging/mechanism-
   overclaim generalization finding, already described substantively in
   that same retro's "Lessons learnt" section) — to `planning/learnings/
   inbox.md`, with a real `knowledge-curator` disposition, exactly as
   the retro already claims was done. Correct the retro/`CHANGELOG.md`
   if the actual disposition differs from what either currently implies.
3. Re-run the full suite, both validators, and `ruff check .` after
   both fixes land (expected unaffected except for whatever new test(s)
   item 1's fix adds).

No other item blocks this verdict. C.2 and C.3 are not defects — C.2 is
a confirmed, now-documented design fact relevant to Stage 89C's own
planning; C.3 is a real but now-closed process gap (the missing
negative control is reproduced and recorded above, closing it).

## Explicit statement on Stage 89C planning

**Stage 89C planning may proceed in parallel** (the concurrent
`planning/phase-89-stage-89c-task-b-controlled-comparison.md` work noted
above is itself still at the planning stage, consistent with `CLAUDE.md`
§1, and does not depend on either fix above). **Stage 89C
*implementation* should not begin, and Stage 89B should not be marked
`done`, until both required fixes above are made and this file receives
a fresh, passing re-audit section** — C.1 is a correctness gap in a
mechanism Stage 89C's own context-packet work may build on or interact
with (C.2's own finding is directly relevant to that design), and item 2
is a real, currently-unmet Definition-of-Done condition for Stage 89B
itself.

## Scope/governance check for this pass's own edit

`git diff --stat -- planning/retros/_audit-phase-89-stage-89b.md`
(verified immediately after this section was written) shows only
insertions for this file — no existing line edited or removed; this
section is appended at the end, exactly as both prior sections already
established as this file's own convention.

# Re-audit — 2026-11-20 (focused re-check of the two FAIL items from the preceding re-audit: C.1 silent gap-suppression, and the missing candidate learning)

**Scope:** only the two blocking items the preceding "Re-audit — 2026-11-20"
section listed under "What must be fixed before re-audit." Does not
re-litigate anything already confirmed sound by that pass (Stage 89B's
detection logic, read-only guarantee, scope-eligibility exclusions, the
real documentation-invalidation cascade, C.2, C.3). **Audited state:**
working tree at dispatch time, uncommitted, on top of committed HEAD
`88b6e30` — confirmed via `git diff HEAD --stat` for every touched file
before and after this pass's own work.

## Verdict

**PASS.** Both fixes are real, correctly scoped, and independently
reproduced below (not merely read or trusted from the implementer's own
description). No new defect found in either fix's own code.

## Fix 1 — C.1, silent gap-suppression on unreachable `repo_root`

**Diff read directly** (`git diff HEAD -- src/codecompass/source_reconciliation.py
src/codecompass/knowledge_api.py`): `PendingContradiction` gained
`live_reconfirmed: bool = True`; `pending_contradicting_findings`'s
former `if item_repo_root is None or not item_repo_root.is_dir(): continue`
is now `live_reconfirmed = item_repo_root is not None and
item_repo_root.is_dir()`, with `validation_repo_root = item_repo_root if
live_reconfirmed else None` passed to `evaluate_result_precedence` in
place of the unconditional `item_repo_root` — the `continue` that
silently dropped the whole finding is gone; the function now always
proceeds to validation, falling back to `evaluate_result_precedence`'s
own pre-existing `repo_root=None` contract-relative-only mode rather than
skipping. `knowledge_api.py::_find_gaps_for_slug_contract` now builds a
`verification_note` from `pc.live_reconfirmed` and interpolates it into
the gap's `reason` text.

**Wording-convention match confirmed by direct grep**: `knowledge_api.py`
line ~1771's `else` branch reads exactly `"contract-relative only -- not
live-reconfirmed; the manifest item's own repo_root is unreachable right
now"` and the `if` branch reads `"live-reconfirmed against the target
checkout"` — both exactly as specified by the dispatch, and both mirror
`stale_test_citation`'s own pre-existing lines (`"live-reconfirmed
against the current implementation"` / `"contract-relative only -- not
live-reconfirmed; no repo_root supplied"`, found at
`knowledge_api.py:1753-1756`) — same convention, different, correctly
distinguished sentence for the different (manifest-item-repo_root vs.
no-repo_root-supplied-at-all) cause.

**Read `oracle.py::evaluate_result_precedence` directly** (lines
978-1040) to independently confirm the fallback's own guarantees: when
`repo_root is None`, the `tested_subject_digest`/`test_input_digest`
recomputation block is skipped (pre-existing, documented behaviour, not
new leniency invented by this fix) — but the contract-hash check
(`oracle_contract_content_hash` vs. the live `oracle-contract.yaml`),
the `contract_id`/`oracle_contract_id` match, the raw-output tamper
check (`sha256_file(raw_path) != result.raw_output_sha256`), and the
scope check all run unconditionally regardless of `repo_root`. This
means the contract-relative fallback can still independently reject a
tampered/invalid result — it is not a bypass for tamper detection, only
a narrowing of which digests get live-recomputed.

**Reproduced the original defect directly**, independent of the new
tests: `git stash push -- src/codecompass/source_reconciliation.py
src/codecompass/knowledge_api.py tests/test_knowledge_api.py` to put
`src/` back to pre-fix `HEAD` content, then `git diff stash@{0}^
stash@{0} -- tests/test_knowledge_api.py` reapplied via `git apply` to
restore only the three new tests on top of pre-fix source. Ran
`pytest tests/test_knowledge_api.py::TestClaimContradictedByFreshCheckGap
-v`: **2 of 3 new tests failed against pre-fix source** —
`test_reachable_repo_root_is_reported_as_live_reconfirmed` failed because
the reason text had no `"live-reconfirmed against the target checkout"`
qualifier at all (pre-fix code never added any qualifier);
`test_unreachable_repo_root_still_surfaces_the_gap_not_silently_dropped`
failed with `assert 0 == 1` — the gap vanished entirely, exactly the
originally-confirmed defect, reproduced fresh by this pass, not merely
quoted from the prior audit. `git checkout -- tests/test_knowledge_api.py
&& git stash pop` restored the working tree to its exact pre-pass state;
confirmed via `md5sum` of all three touched files matching their
pre-restore values, and `git diff --stat` afterward showing the same
629-line/7-file change set as at dispatch (no net content change from
this pass's own stash/restore cycle).

Ran the full `TestClaimContradictedByFreshCheckGap` class against the
real, current (post-fix) working tree: **14 passed**, including all
three new tests
(`test_reachable_repo_root_is_reported_as_live_reconfirmed`,
`test_unreachable_repo_root_still_surfaces_the_gap_not_silently_dropped`,
`test_unreachable_repo_root_tampered_result_still_excluded`). Read each
test body directly: the first two exercise the fix precisely (a
`repo_root_override` pointing at a path that genuinely does not exist,
confirmed via `tmp_path / "this-checkout-does-not-exist"`, vs. the
default reachable `project_root`); the third combines the unreachable
`repo_root_override` with `raw_output_ok=False` (a hand-tampered
`raw_output_ref` file whose content no longer matches its own recorded
`raw_output_sha256`) and asserts the gap is still correctly excluded —
exercising exactly the tamper-detection-still-works guarantee the dispatch
asked this pass to confirm, not merely the happy path.

**Disposition: FIXED, confirmed sound.**

## Fix 2 — the missing candidate learning

`grep -n "L-138" planning/learnings/inbox.md planning/learnings/promoted.md
planning/ROADMAP.md` → present in all three. Read the full `L-138` entry
in `inbox.md` (lines 13271-13450) directly, in full: every required field
present (`origin`, `date`, `project_revision`, `observation`, `evidence`,
`classification`, `status`, `recurrence` overlap-check against
`L-137`/`L-119`/`L-120`, `promoted_to`, plus a `knowledge-curator`
curation note explaining why this entry exists — to make true the claim
Stage 89B's own retro already made). `status: promoted`. Content is
substantive, not a placeholder: it names the two specific sections
(`overlapping-patterns`/`CL-BFS-004`, `multi-section-sign-inversion`/
`CL-BFS-002`), the specific round counts (4 and 3) and what each round's
failure actually was (overclaim with no hedge; hedge read as
meta-commentary; self-referential epistemic-provenance framing;
unevidenced mechanism detail beyond the oracle record's stated scope),
and correctly cross-references/distinguishes itself from `L-137`
(same meta-pattern, different artifact) and `L-119`/`L-120` (same
function, different concern) rather than merely restating the retro's
prose.

Confirmed the cited evidence is real: `planning/retros/
phase-89-stage-89b-ledgerkit-demonstration.md` exists, and
`grep -n "Review iteration"` finds `## Review iteration
(semantic-support + editorial-quality)` at line 52 — the section the
entry cites genuinely exists and (already read by the preceding pass,
and spot-checked again here) substantiates the 4-round/3-round account
`L-138` summarizes.

Confirmed the destination row: `planning/ROADMAP.md`'s "Future-improvement
backlog (unscheduled)" table has the `L-138` row (read directly, lines
~250), worded identically to the draft text `inbox.md`'s own curation
note proposed, with `FUTURE-IMPROVEMENT` / `not started` / a concrete
revisit trigger — matching the established `L-122`/`L-124`/`L-131`
convention in the same table. `promoted.md` line 118 (`L-138 | 2026-11-20
| future-improvement | ...`) present and consistent.

Confirmed `planning/retros/phase-89-stage-89b.md`'s "Candidate learnings
filed" section's own claim ("One new candidate learning naming the
composer-prompt-generalization finding above... see
`planning/learnings/inbox.md` for its exact id") is now true, with no
further edit to that retro section needed — the entry's own curation note
makes this same point explicitly, and this pass independently confirms
it by direct `grep`/read rather than trusting that note.

**Disposition: FIXED, confirmed sound and substantive — not hollow.**

## Full suite / validator / ruff — reproduced directly, this pass

- **`pytest -q`** (full suite, repo root, real run, not reused from the
  prior pass): **`4 failed, 1550 passed, 2 skipped in 474.01s`** —
  matches the dispatch's own stated claim exactly (1550 passed / 2
  skipped / 4 failed). Failures confirmed genuinely environmental by
  reading the actual output: three `tests/test_execute_doc_example.py`
  tests fail with `env: 'codecompass': No such file or directory` (no
  `codecompass` on `PATH` in this sandboxed environment) and one fails
  with `ERROR: No matching distribution found for codecompass-context`
  (no network access for `pip` in this environment) — identical in kind
  and count to the four failures the preceding re-audit section already
  characterized as environmental, unrelated to any Stage 89B code or
  either of this pass's two fixes.
- **`scripts/check_knowledge_base.py`**: 24 informational
  `knowledge-base-snapshot-current-divergence` findings, exit 0 —
  unchanged from the established baseline.
- **`scripts/check_contracts.py`**: 7 findings (6
  `contract-result-integrity-mismatch`, 1 `contract-check-gap`), exit 0
  — unchanged from the established baseline.
- **`ruff check .`**: **167 errors** — unchanged from the established
  baseline, confirmed by direct re-run, not assumed.
- **Real-checkout cleanliness**: `git status --porcelain` for
  `~/projects/ledgerkit` → empty; `git status --porcelain -- planning/
  knowledge/balance-from-spec planning/contracts/balance-from-spec` →
  empty. Both untouched throughout this pass's own work, confirmed
  directly.
- **Scope check on the two fixes' own diff**: `git diff HEAD --stat --
  src/codecompass tests/` shows only
  `knowledge_api.py` (+8/-1 net via the quoted hunk), `source_reconciliation.py`
  (+34/-2 net), and `test_knowledge_api.py` (+50/-2 net) touched — no
  change to `cli.py` (confirmed `git diff HEAD -- src/codecompass/cli.py`
  is empty) or any other `src`/`tests` file; no scope creep beyond what
  the dispatch described.
- **Candidate-learning file scope**: `git diff HEAD -- planning/learnings/
  inbox.md` adds exactly one new `### L-` heading (`L-138`); no other
  learning entry edited.
- **Note (non-blocking, out of this pass's dispatched scope, disclosed
  for completeness)**: `planning/ROADMAP.md`'s own working-tree diff (not
  touched by either of this pass's two fixes) now also reflects Stage
  89B's commit hash (`88b6e30`) and Stage 89C's plan-drafted status —
  consistent with the preceding re-audit's own disclosed observation
  about concurrent Stage 89C planning landing in the live repository;
  this pass did not interact with or evaluate that content beyond
  confirming it does not touch any file either of the two dispatched
  fixes changed.

## Scope/governance check for this pass's own edit and its own
scratch reproduction

`git diff --stat -- planning/retros/_audit-phase-89-stage-89b.md`
(checked immediately before writing this section) showed only
insertions for every prior section of this file; this section is
appended at the end, preserving that convention — no existing line
edited or removed.

This pass materialized a prior revision's content onto the live tracked
paths `src/codecompass/source_reconciliation.py`,
`src/codecompass/knowledge_api.py`, and `tests/test_knowledge_api.py`
(via `git stash`/`git apply`) to reproduce the pre-fix defect. Per this
role's own hard rule on restoring any such comparison: `git checkout --
tests/test_knowledge_api.py && git stash pop` was run immediately after
the reproduction, and `git status --porcelain` plus `md5sum` of all
three files were used to confirm the working tree returned to its exact
pre-reproduction state before any further verification (the validator/
ruff/full-suite re-runs above were all executed against the restored,
real current working tree, not the temporarily-reverted one).

## Overall disposition

Both of the preceding re-audit's two blocking items are fixed, each
confirmed by direct re-derivation (diff reading, live defect
reproduction against pre-fix source, test execution against both
pre-fix and post-fix source, and direct reading of the filed learning's
own content and destinations) rather than by trusting either fix's own
description. Full suite, both validators, and `ruff` all reproduce the
dispatch's own claimed baseline exactly. No new defect found. Stage 89B
may now proceed to the remaining Definition-of-Done steps (commit,
`roadmap-context-curator` closeout) per `CLAUDE.md` §5 — this pass does
not itself authorize marking the stage `done`, since that determination
belongs to the lead reading this report alongside the rest of Stage 89B's
already-confirmed-sound scope.
