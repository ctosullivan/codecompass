# Independent completion audit — Phase 87, Stage 87A only

**Audited commit range**: `cf7f9a4` (plan) .. `fe664b7` (negative controls),
plus one additional commit, `b81ace7` ("docs: note compile_doc_section.py's
second, non-sandboxed broker caller"), which landed *during* this audit
session — incorporated below since it is now HEAD. Stage 87B/87C are
explicitly out of scope and confirmed NOT implemented (see §6).

**Verdict: FAIL**

This is not a finding against the code itself — the Stage 87A
implementation, its tests, and its real end-to-end demonstration are all
independently re-verified below and hold up well. The FAIL is driven
entirely by a complete, multi-artifact absence of the process-tracking
side of `CLAUDE.md` §5's Definition of Done: `planning/CONTEXT.md`,
`planning/ROADMAP.md`, and `CHANGELOG.md` were never touched by any of the
seven real implementation commits; no phase retro exists; no persisted
`docs-reconstructor` drift-audit report exists; and no candidate-learnings
triage exists. These are not stylistic nits — §5 names each as a
necessary, independently-checkable condition of "done," and right now
none of the five is satisfied for Stage 87A.

---

## 1. Deliverable re-derivation (plan §D.1) — all present and tested

Re-derived directly from the plan's own §D.1 list, not assumed:

| Deliverable | File | Confirmed |
|---|---|---|
| Minimal schema format (§B) | `README.md.schema.yaml` | exists, matches §B's example shape exactly |
| `resolve_section_ids`/`check_record_currency`/`find_section_gaps`/`resolve_section_packet` | `src/codecompass/doc_compiler.py` | all four present (`:91`, `:126`, `:146`, `:217`); 31 tests in `tests/test_doc_compiler.py` |
| `scripts/check_doc_schema.py` | exists | 14 tests in `tests/test_check_doc_schema.py` |
| `scripts/compile_doc_section.py` | exists | 15 tests in `tests/test_compile_doc_section.py` |
| `docs_app` CLI (`schema-init`/`compile`/`publish`/`maintain`) | `src/codecompass/cli.py:1873-2070ish` | all four `@docs_app.command(...)` present; **only 3 of 4 have any CLI-level test** (see §9 below — `docs publish` is untested at the CLI layer despite being the actual command used to publish the real demonstration and the command that caught a real `schema_slug` defect) |
| `publish_section`/`maintain_document` five-state reconciliation | `doc_compiler.py:425`, `:491` | both present, both directly tested, including reordering and cross-document duplicate-id negative controls (`fe664b7`) |
| Real end-to-end demonstration | `README.md`, `README.md.schema.yaml`, `planning/retros/phase-87-pending-review/readme-md/vendor-digest-concept.json` | reproduced independently, see §5 |

## 2. Full test suite — matches claim

Ran `cd /home/cormac/projects/codecompass && .venv/bin/python -m pytest -q`
myself, twice (once foregrounded via background task, once again to
confirm determinism):

```
1274 passed, 2 skipped in 363.92s / 391.68s
```

This is consistent with the commits' own claimed "1272 passed" (the delta
is `fe664b7`'s own 2 new negative-control tests landing after that
message was written) and well above the task's "around 1272+" floor.

**Correction to the task's own framing of the 2 skips**: re-ran with
`pytest -q -rs` and got:

```
SKIPPED [1] tests/test_adapter_cargo.py:110: cargo not installed
SKIPPED [1] tests/test_adapter_npm.py:176: npm not installed
```

These are **not** "the L-114/L-107 baseline." `L-114`/`L-107`
(`planning/learnings/inbox.md:137`, `:972`) describe pre-existing
knowledge-debt categories reported by
`scripts/check_self_knowledge_quality.py --strict` (confirmed by direct
re-read of both learnings and by re-running that validator myself — its
findings are all `balance-from-spec`-related `unverified_required_scope`/
`stale_test_citation` items, nothing about pytest skips). The 2 pytest
skips are simply this environment's missing `npm`/`cargo` binaries,
gating each adapter's own live-smoke test — a long-stable, unrelated
baseline (traced back via `git log`/`grep` to well before Phase 85, e.g.
`planning/learnings/inbox.md:8136`'s "623 passed, 2 skipped"). Several of
this phase's own commit messages (e.g. `a9667b5`: "1272 passed, 2 skipped
(L-114/L-107 baseline unchanged)") inherited this mislabeling from
precedent set in earlier phases' commit messages — it predates Phase 87
and isn't something Stage 87A introduced, but it is factually wrong and
worth correcting going forward. Not a blocking finding on its own.

## 3. `ruff check` — clean for everything Stage 87A actually added

```
ruff check src/codecompass/doc_compiler.py scripts/check_doc_schema.py \
  scripts/compile_doc_section.py src/codecompass/cli.py \
  tests/test_check_doc_schema.py tests/test_compile_doc_section.py \
  tests/test_doc_compiler.py tests/test_cli.py
```

→ 6 findings, all `E501` (line too long), **zero** inside any Phase-87-new
file or inside the new `docs_app` region of `cli.py` (lines ~1873-2070).
All 6 are at `cli.py:1762/1780/1785/1795/1802` (the `knowledge_app`
`search`/`traverse`/`gaps` commands) and `tests/test_cli.py:1460`.
`git blame` on every one of those 6 lines resolves to commit `0b4f321`
(2026-10-29) or `45a3ca8` (2026-10-29) — both predate Phase 87's first
commit (`cf7f9a4`, 2026-11-04) by six days. Confirmed pre-existing and
unrelated. (Minor note: the task described "5 pre-existing" violations;
there are actually 6 — `tests/test_cli.py:1460` is also pre-existing, just
not in `cli.py` itself. Doesn't change the conclusion.)

## 4. The four integration-defect corrections (§G) — independently re-verified as real code, not just plan prose

- **§G.A (region-id format)**: `knowledge_intermediate.py:167`'s
  `_REGION_ID_RE = re.compile(r"\bregion:([A-Za-z0-9_-]+)\b")` is
  confirmed **unchanged** (still permits `_`, no `.`) — the plan's claim
  that it's reused as-is, not modified, holds. `scripts/check_doc_schema.py:65`
  separately defines and enforces the narrower `_SECTION_ID_RE =
  re.compile(r"^[a-z0-9-]+$")`, applied to every section `id` (`:107`) and
  to `publish_section`'s own `region_id` parameter
  (`doc_compiler.py:436`). Reordering and cross-document duplicate-id
  tests both exist and pass (`test_region_identity_survives_reordering_
  within_a_document`, `test_duplicate_region_id_across_two_documents_is_
  rejected`).
- **§G.B (runtime evidence handoff)**: read `scripts/compile_doc_section.py`
  directly. Confirmed: no import of or call into
  `prepare_cleanroom_branch.py` anywhere in the file; `write_section_
  packet` uses `tempfile.mkdtemp(prefix="doc-compiler-section-packet-")`
  (`:100`), explicitly documented as "never under `project_root`, never a
  git-tracked path, never committed." Hash-verification
  (`verify_packet_integrity`) and staging-directory-exactness assertion
  (`assert_staging_dir_contents`) both present and separately tested.
- **§G.C (provenance vs. grounding)**: `README.md.schema.yaml` uses
  `citation_display: none` (not `provenance`); `check_doc_schema.py:43`'s
  `_VALID_CITATION_DISPLAY = {"inline", "none"}` is the only enum
  validated. `doc_compiler.publish_section` (`:425`) has **no**
  `citation_display`/`provenance` parameter at all — its own docstring
  states the marker is unconditional — confirmed by reading the function
  body: the `codecompass-grounded-by` marker is built and written on
  every call, with no conditional branch that could omit it.
- **§G.D (untagged factual statements)**: the real demonstration's own
  evidence file (`planning/retros/phase-87-pending-review/readme-md/
  vendor-digest-concept.json`) shows exactly the three-question split in
  practice — `citation_findings` entries are explicitly scope-only
  (`"reason": "citation resolves within this section's own packet (scope
  check only; semantic support is verified separately, by independent
  AI-assisted dispatch)"`), and the commit message for `a9667b5` describes
  two real, independent dispatch rounds that actually failed and were
  fixed before a third passed — this is real exercised behaviour, not
  just asserted.

## 5. Real demonstration — independently reproduced

- `README.md:103-107` contains the real `codecompass-grounded-by:
  CL-CTXT-005 region:readme-md-vendor-digest-concept` marker wrapping the
  "## Understanding Digests" section. Confirmed by direct read.
- `planning/knowledge/codecompass-domain/CL-CTXT-005.yaml` was read
  directly: its `statement` field genuinely supports every sentence in
  the published section (VendorDigest object, file tree/dependency
  tree/API surface, the five rendered output files, unconditional
  per-vendor rendering). No invented content found.
- Ran `.venv/bin/codecompass docs maintain README.md.schema.yaml` myself
  from the repo root (venv active). Output:
  ```
  established_new: []
  noop: ['id:readme-md-vendor-digest-concept']
  doc_candidates (never auto-regenerated): ['id:intermediate-knowledge-layer']
  claims_changed (reported, not auto-regenerated): []
  concurrent_conflicts (lead-resolved only): []
  ```
  Confirms exactly the claimed behaviour: the new section is `noop`
  (already baselined), and the pre-existing `intermediate-knowledge-
  layer` region is correctly left alone as `doc_candidate`.
- **Side effect disclosed and cleaned up**: running that command wrote a
  new, un-requested reconciliation manifest
  (`planning/knowledge/codecompass-domain/reconciliation/
  20261104T083355Z-doc.toml`, a near-duplicate of the already-committed
  `20261104T081241Z-doc.toml`) to the working tree as an untracked file —
  `maintain_document`'s `doc_candidate` path writes a fresh
  timestamped manifest on every invocation, not only when nothing already
  covers the same candidate. I deleted this file before finishing (`rm`
  + confirmed `git status --short` clean) per this audit's own
  read-only/no-material-left-behind obligation. This is itself worth the
  lead's attention as a possible design gap (repeated `maintain` calls
  with no decided-and-applied candidate will keep accumulating near-
  identical manifest files) but I am not fixing it — reporting only.
- Read `planning/knowledge/codecompass-domain/reconciliation/
  20261104T081241Z-doc.toml` (the one real, committed manifest): well-
  formed TOML, `region_text` matches the live README.md region verbatim,
  `cited_ids`/`base_region_hash` consistent, `state = "pending"`,
  `decision = "undecided"`, `semantic_change = false`. No false claim
  found in it.

## 6. Stage 87A exclusions — confirmed genuinely absent, not assumed

- `find . -iname "run_example_command*"` → nothing.
- `find . -iname "*.schema.yaml"` → only `README.md.schema.yaml`.
- No deterministic CLI-reference-generation code found in `scripts/` or
  `src/codecompass/`.
- No matched-baseline comparative-experiment artifacts found anywhere.

## 7. Protected-file drift — none found

- `git diff cf7f9a4 fe664b7 -- CLAUDE.md` → empty. `git log -- CLAUDE.md`
  confirms the file's last real change predates Phase 87's first commit.
- `git diff cf7f9a4^..fe664b7 -- decisions/` → empty; `ls -la decisions/`
  confirms no file numbered after `0094` exists — no new ADR was added
  for Phase 87, and no existing ADR was edited.
- `b81ace7` (the one commit that landed after `fe664b7`, during this
  audit session) touches only `docs/development/clean-room-
  redocumentation.md` — confirmed via `git show --stat`.

## 8. Uncommitted changes — none, after cleanup

`git status --short` is clean at the end of this audit (see §5's
disclosed cleanup of a self-caused side effect).

## 9. Findings that drive the FAIL verdict

1. **`planning/CONTEXT.md` was never updated for Stage 87A's
   implementation.** `git log --oneline -- planning/CONTEXT.md` shows its
   last touch was `80eb242` ("record independent planning-review
   verdict"), which predates the plan's own restructuring (`db4aa5b`) and
   every real implementation commit (`b2fbc23`, `a54be15`, `d2e51f6`,
   `e73a6c7`, `a9667b5`, `fe664b7`). The file, as committed right now,
   still reads: *"Phase 87 — ... — is `planned`, not started."* This is
   false — Stage 87A is fully implemented, tested, and demonstrated
   end-to-end against the live repository. `CLAUDE.md` §4/§5 both
   require this file to reflect current state.
2. **`planning/ROADMAP.md` was never updated.** Confirmed by `git diff
   --stat b2fbc23^..fe664b7 -- planning/ROADMAP.md` (empty) and by
   reading the live row: it still reads *"Phase-planned, independently
   reviewed -- READY WITH NON-BLOCKING OBSERVATIONS ...; not started"*
   and status `planned`. `CLAUDE.md` §2 requires this updated in the same
   commit as any phase-scope change; none of the seven implementation
   commits touched it.
3. **No `CHANGELOG.md` entry exists for Phase 87 at all.** Checked the
   full `[Unreleased]` section; the most recent entry is Phase 86's.
   `CLAUDE.md` §3 requires an entry in the same commit as the change,
   every phase, no exceptions.
4. **No phase retro exists.** `planning/retros/phase-87-pending-review/`
   contains only the demonstration's own evidence JSON
   (`readme-md/vendor-digest-concept.json`) — not a retro. There is no
   `planning/retros/phase-87-<slug>.md` anywhere. `CLAUDE.md` §5 requires
   this for every phase (a few lines would suffice even for a stage this
   size, but zero lines do not).
5. **No persisted `docs-reconstructor` drift-audit report exists.**
   Commit `b81ace7`'s own message states a docs-reconstructor-style drift
   audit ran and found/fixed one real gap (the clean-room-
   redocumentation.md trust-boundary omission) — so the *activity*
   happened, consistent with past-phase practice — but unlike every prior
   phase (`_drift-audit-phase-82.md`, `_drift-audit-phase-86.md`, etc.),
   no `planning/retros/_drift-audit-phase-87*.md` file exists recording
   its full scope/findings/verdict. The one fix it produced is real and
   good; the missing durable record of the audit itself is still a §5 gap.
6. **No candidate-learnings triage exists for Phase 87.** Searched
   `planning/learnings/inbox.md` and `promoted.md` for any Phase-87
   reference — none found, despite this implementation having found and
   fixed multiple real defects during its own work (the stray-space
   citation-stripping bug, the `schema_slug` dot-truncation bug, the
   originally-committed `check_doc_schema.py`'s wrong field-shape). Each
   of these resembles exactly the kind of "real defect caught by direct
   execution, not assumed" pattern this project's own learning pipeline
   usually captures. Whether any should be promoted/retained/discarded is
   a judgment call for `knowledge-curator` — but that judgment was never
   recorded at all.
7. **`docs/reference/cli.md` was not updated for the new `docs` CLI
   subcommand group.** Every other command group in the file
   (`query`, `knowledge`, `enrich`, etc.) has its own documented section,
   including Phase 84's `knowledge get|search|trace|gaps|context|export`.
   `codecompass docs schema-init|compile|publish|maintain` has none.
   `CLAUDE.md` §2 requires `docs/` updated in the same commit as any CLI
   behaviour change.
8. **No `architecture/` doc describes the new compilation pipeline.**
   `grep -rl "doc_compiler" architecture/` finds nothing. A substantial
   new subsystem (the 9-step pipeline, the schema contract, the five-state
   reconciliation) has zero living architecture documentation.

## 10. Non-blocking observations (would not alone drive FAIL)

- `scripts/docs_maintain` CLI command passes `(schema["document"],)` — a
  single-element tuple — to `doc_compiler.maintain_document`, even though
  that function's own docstring states `doc_names` "must cover every
  schema-governed document in one call" for the duplicate-id check to be
  genuinely project-wide. Currently harmless (there is exactly one
  schema-governed document in the whole repository), but the CLI has no
  mechanism today to pass more than one, which will need to change before
  Stage 87B (two documents) can safely reuse `docs maintain` as-is.
- `docs publish` (the actual CLI command used to publish the real
  demonstration, and the command whose `_schema_slug` dot-handling defect
  was caught live during that real run) has **zero** automated test
  coverage at the CLI layer — no test invokes `app, ["docs", "publish",
  ...]` at all, blocking-verdict path or success path. The underlying
  `doc_compiler.publish_section` is well-tested directly, and
  `_schema_slug`'s dot-handling fix has its own unit test, but the
  command's own verdict-gating logic (`semantic_verdict`/
  `editorial_verdict` must both clear) is untested.
- `maintain_document`'s `doc_candidate` path appears to write a fresh,
  timestamped manifest file on every invocation rather than recognising
  an existing, undecided candidate already covers the same region/hash —
  confirmed empirically in §5 (a second `docs maintain` run produced a
  near-duplicate manifest). Worth the lead's attention before Stage 87B's
  real multi-section maintenance cycles make this noisier.
- No new ADR was written for this restructuring/correction pass. The
  plan file's own §G-M sections function as the historical record, which
  is defensible, but several prior phases of comparable non-obvious-
  tradeoff weight (e.g. Phase 86's finding → `decisions/0094`) did
  produce a dedicated ADR. Not required by the letter of `CLAUDE.md` §2
  ("as applicable"), but worth the lead considering.

## 11. What must be fixed before re-audit

1. Update `planning/CONTEXT.md`'s "Current phase" section to accurately
   describe Stage 87A's real, current state (implemented, tested,
   demonstrated; 87B/87C not authorised).
2. Update `planning/ROADMAP.md`'s Phase 87 row to reflect Stage 87A's
   real status (not `planned`/"not started").
3. Add a `CHANGELOG.md` `[Unreleased]` entry for Stage 87A.
4. Write `planning/retros/phase-87-stage-87a-<slug>.md` (or equivalent),
   filling every `planning/retros/TEMPLATE.md` section substantively,
   including where-we-are / what-worked / what-didn't / where-we're-going
   (87B/87C gate ahead).
5. Persist a `planning/retros/_drift-audit-phase-87.md` (or
   `-stage-87a.md`) recording the docs-reconstructor pass's actual scope
   and findings (the clean-room-redocumentation.md gap `b81ace7` already
   fixed, plus confirmation nothing else current-truth was missed).
6. Have `knowledge-curator` triage whatever candidate learnings this
   stage raised (at minimum, consider the three real defects named in
   finding 6 above) and record outcomes.
7. Add a `docs/reference/cli.md` section documenting `codecompass docs
   schema-init|compile|publish|maintain`.
8. Add or extend an `architecture/` doc describing the new
   knowledge-compilation pipeline (even briefly, matching Stage 87A's own
   bounded scope).
9. (Recommended, not blocking) Add at least one CLI-level test for `docs
   publish`'s verdict-gating behaviour (both the blocked path and the
   success path).

Once 1-8 are done (and 9 ideally), this stage should re-audit cleanly —
the underlying implementation, its tests, and its real demonstration are
all independently confirmed solid.

---

## Re-audit after DoD fix list (2026-11-04)

**Scope**: independent, read-only re-verification of all 9 fix-list items
above, against HEAD = `61182a8`. Nothing in this section trusts any prior
commit message or audit-dispatch prompt — every claim below was checked
directly against the live repository.

### Item-by-item

1. **`planning/CONTEXT.md` — FIXED.** Read the "Current phase" section
   directly (lines 8-57). It now correctly states: Phase 87 "restructured
   into three stages (87A/87B/87C); Stage 87A implemented and
   independently re-audited; Phase 87 overall remains `not done`"; names
   the specific commits; narrates the restructuring, the four
   implementation-contract defects, and the real three-round
   demonstration; and explicitly states "**Stage 87B and 87C are not
   implemented and not authorised**". The "Next concrete step" section
   (line 979-996) separately and correctly restates the same state and
   names the concrete next action (explicit authorisation for Stage 87B).
   No stale "planned, not started" language remains anywhere describing
   Stage 87A's own status.

   **Non-blocking observation**: the "What was just completed" section
   (line 624 onward) still opens with Phase 83 corrective-pass content,
   not anything about Stage 87A — this file's own established structure
   puts the live, current narrative in "Current phase" and lets "What was
   just completed" lag (this predates Phase 87 by many phases and is not
   something this fix pass introduced or was asked to fix). Separately,
   neither `L-118` nor `L-119` is named anywhere in `CONTEXT.md` (`grep -n
   "L-118\|L-119" planning/CONTEXT.md` → no output), unlike the directly
   analogous `L-116`/`L-117` (also `status: retained`, also pending user
   `CLAUDE.md` §0 approval), which **are** named explicitly in "Next
   concrete step" (lines 974-978) as an open item requiring a future
   human decision. This is a real, if narrow, completeness gap in the
   session-resumption document — a future session reading `CONTEXT.md`
   alone would not learn that two more learnings are sitting at
   `retained`, awaiting the same kind of approval `L-116`/`L-117` already
   get flagged for. Not blocking: the underlying facts are accurately and
   fully recorded elsewhere (`inbox.md`, `proposed-governance-changes.md`
   §N/§O), and nothing in `CONTEXT.md` is actually false.

2. **`planning/ROADMAP.md` — FIXED.** Read the Phase 87 row directly
   (line 190). It now narrates the restructuring, the four
   implementation-contract defects, and states explicitly: "**Stage
   87A — implemented, independently audited PASS WITH NON-BLOCKING
   OBSERVATIONS (2026-11-04)**... **Stage 87B**... **and Stage 87C**...
   are planned... but **not authorised or started**. Phase 87 overall
   remains not done until 87C's own exit gate is met." This is accurate
   and matches every other field I independently verified.

   **Non-blocking observation**: the row's own Status column (the single
   word after the long description cell) still literally reads `planned`
   — the same word it held before this fix pass, since this table's own
   status vocabulary (confirmed by `grep`-counting every row: 17 `done`,
   5 `not started`, 1 `planned` — Phase 87 is the only `planned` row) has
   no finer-grained "partially implemented"/"in progress" bucket. `planned`
   is not false (the phase genuinely isn't `done`), and the fix-list
   item's own instruction ("not `planned`/'not started'") is satisfied by
   the cell's prose, which is accurate and detailed — but the bare status
   word by itself, read in isolation from the prose, still looks
   unchanged from the pre-fix state. Worth the lead considering a fourth
   vocabulary word for exactly this shape (a phase with a `done` sub-stage
   and `not done` overall status) before Stage 87B closes, but not a
   defect in what's actually claimed.

3. **`CHANGELOG.md` — FIXED.** Read the `[Unreleased]` section directly
   (lines 8-46). A real, substantive, first entry — "Phase 87, Stage
   87A: Documentation Schema and Knowledge-Compiled Documentation —
   knowledge compilation proven" — names `decisions/0084`/`0085`, lists
   every real deliverable (`doc_compiler.py`, `check_doc_schema.py`,
   `compile_doc_section.py`, the CLI group), narrates the real
   three-round demonstration including the two correctly-failed earlier
   rounds, states the independent-audit verdict, and explicitly scopes
   Stage 87B/87C as "planned but not yet authorised or started; Phase 87
   overall is not yet `done`." Matches `CHANGELOG.md`'s own Keep a
   Changelog convention and this project's per-phase, non-batched
   entries. Only one phase's work is covered by this entry — confirmed.

4. **Phase retro — FIXED.** Read
   `planning/retros/phase-87-stage-87a-knowledge-compilation.md` in full.
   Checked it section-by-section against `planning/retros/TEMPLATE.md`'s
   own required headings: `Where we are` (orients Stage 87A within the
   Phase 86→87 arc and the three-stage restructuring, not just this
   stage in isolation), `Goal`, `Scope delivered vs planned` (names the
   one real deviation — the DoD paper trail itself — rather than hiding
   it), `What was achieved`, `What worked` (four specific, evidenced
   points, not vague praise), `What didn't work` (names the DoD-paper-
   trail failure explicitly as "the session's one real process failure,"
   plus two other genuine misfires — the vague-prompt-revision failure
   and the untested-separator slug bug), `Lessons learnt`, `Process-
   improvement feedback`, `Candidate learnings filed` (`L-118`/`L-119`,
   cross-referenced), `Where we're going` (87B/87C's own separate
   authorisation requirement, named explicitly), `Time/cost note`. Every
   section is present and substantive — none is a stub. The retro is
   honest: it does not spin the FAIL as anything other than a real
   process failure, consistent with the audit that found it.

5. **Drift-audit report — FIXED, content cross-checked against the real
   fix commit.** Read
   `planning/retros/_drift-audit-phase-87-stage-87a.md` in full. It is a
   complete report (verdict, scope/method, 5 numbered findings, a
   "not checked" section with reasoning, a disposition section) — not a
   stub. Cross-checked finding 4 (the one non-blocking, fixed finding)
   against `b81ace7`'s actual diff directly (`git show b81ace7`): the
   drift report describes the gap as "`docs/development/clean-room-
   redocumentation.md`'s... trust-boundary framing described
   `cleanroom_broker.py` as reachable only from inside a verified Mode B
   namespace/`pivot_root` sandbox... `compile_doc_section.py`'s
   `compose_section` calls `cleanroom_broker.run_inference` directly from
   the host process — a second, legitimate but structurally different
   (non-sandboxed) caller" and states it was "fixed... a short note added
   explaining the deliberate, bounded exception." `b81ace7`'s actual diff
   adds exactly a 16-line note titled "A second, narrower caller (Phase 87
   Stage 87A)" making exactly that point, in the same file. The report's
   own account of what was found and what was fixed matches the real
   commit precisely — no embellishment, no mismatch. Finding 2 (the
   explicitly-deferred `cli.md` item) is also consistent with item 7's
   own resolution below.

6. **Learnings triage — FIXED, with the metadata correction itself
   independently re-verified.** Read `L-118` and `L-119` in
   `planning/learnings/inbox.md` directly (lines 11239-11497). Both show
   `status: retained` (not `candidate`). `L-118`'s `project_revision`
   field now reads: "`e73a6c7` (the fix, 2026-11-04 16:19:15 +0800).
   **Correction**... the original filing wrongly cited `a9667b5`... as
   'the first real demonstration run, pre-fix.' There is no commit
   capturing the pre-fix state at all." Independently re-ran the exact
   verification: `git show -s --format="%H %ci" e73a6c7` →
   `2026-11-04 16:19:15 +0800`; `git show -s --format="%H %ci" a9667b5` →
   `2026-11-04 16:20:24 +0800`. `e73a6c7` is confirmed strictly earlier;
   the corrected field's claim ("no commit capturing a pre-fix state...
   the bug was hit and fixed live, in the uncommitted working tree") is
   consistent with this timing and is no longer self-contradictory as the
   original filing was. `planning/v1-redefinition/proposed-governance-
   changes.md` §N and §O (lines 1015-1194) both exist as real, detailed
   draft sections — each with Context, a concrete proposed `CLAUDE.md` §1
   sentence, an "Alternatives considered" subsection, and "Consequences if
   approved" — not placeholders. Confirmed `CLAUDE.md` itself was **not**
   touched: `git log --oneline -- CLAUDE.md` shows its last real change
   is `1c3981b` (2026-10-07), well before this session; `git diff
   4a2b077..HEAD -- CLAUDE.md decisions/` is empty. Both §N and §O
   explicitly state "pending the user's own explicit `CLAUDE.md` §0
   approval — not yet applied," correctly deferring self-application.

7. **`docs/reference/cli.md` — FIXED.** Read the new section directly
   (lines 250-298, `## codecompass docs schema-init|compile|publish|
   maintain (Phase 87, Stage 87A)`). It follows the file's own
   established per-command-group convention exactly — compared directly
   against the `knowledge get|search|trace|gaps|context|export` (Phase
   84) section immediately above it (lines 163-248): a fenced usage
   block, a prose paragraph naming the module/architecture-doc
   cross-reference, then one bullet per subcommand describing its real
   behaviour. Spot-checked two claims against real source:
   `doc_compiler.py:425`'s `publish_section` docstring/body do gate on
   both verdicts and always emit the grounding marker regardless of
   `citation_display` (matches "never auto-resolved... Always emits...
   regardless of the schema's own reader-visible `citation_display`
   setting"); `maintain_document`'s five states (confirmed present at
   `doc_compiler.py:491` in item 1 of the original audit) match "never
   regenerates a `doc_candidate`... or a `concurrent_conflict`
   automatically." Correctly scoped: explicitly states "no deterministic
   CLI-reference generation yet... no execution harness... (Stage 87B)...
   no matched-baseline quality comparison yet (Stage 87C)."

8. **Architecture docs — FIXED, spot-checked against real source.** Read
   `docs/architecture/documentation-compilation-pipeline.md` in full and
   the new `doc_compiler.py` row in `docs/architecture/components.md`
   (line 36). The pipeline doc opens with an explicit scope statement
   ("Current state: **Stage 87A only**... This page describes what
   exists today, not the full eventual design") and its 9-step pipeline
   section matches the real function names and line numbers I
   independently confirmed exist (`resolve_section_ids`,
   `check_record_currency`, `find_section_gaps`, `resolve_section_packet`,
   `validate_section_citations`, `publish_section`, `maintain_document` —
   all found at `grep -n "^def "` against `doc_compiler.py`, same line
   numbers the doc cites). The "Clean-room composition" section's claims
   (no new sandbox, no new broker, `cleanroom_broker.run_inference`
   invoked directly, the ephemeral `tempfile.mkdtemp()` staging dir, hash
   re-verification, the isolation preflight subprocess, the embedded
   file-path-marker rejection) were checked directly against
   `scripts/compile_doc_section.py`'s real source (read in full) and
   match exactly, including the specific function names
   (`write_section_packet`, `verify_packet_integrity`,
   `assert_staging_dir_contents`, `run_isolation_preflight`,
   `compose_section`). No overclaiming of 87B/87C found anywhere in
   either doc.

9. **CLI-level `docs publish` test — ADDED AND CONFIRMED GENUINE.** Read
   `tests/test_cli.py:2716-2749`,
   `test_docs_publish_refuses_without_both_verdicts_passing`, in full. It
   genuinely exercises both paths in one test: first invokes `docs
   publish` with `--semantic-verdict unsupported --editorial-verdict
   pass`, asserts `exit_code == 1` and that the target doc file was
   **not** created; then invokes the same command with
   `--semantic-verdict supported --editorial-verdict pass` against the
   same pending-review fixture, asserts `exit_code == 0` and that the
   published content actually landed in the target file. This is a real
   refuse-then-accept pair against the actual CLI entry point, not a
   isolated call to the underlying `doc_compiler` function. Ran it
   directly: `.venv/bin/python -m pytest tests/test_cli.py -q -k
   docs_publish` → `1 passed, 102 deselected in 4.22s`.

### Baseline re-confirmation

- **Full suite**: `cd /home/cormac/projects/codecompass && .venv/bin/python
  -m pytest -q` → `1275 passed, 2 skipped in 335.48s (0:05:35)`.
  Cross-checked against `pytest --collect-only -q` → `1277 tests
  collected` (1277 − 2 skipped = 1275 passed, self-consistent). This is
  the prior audit's own `1274 passed, 2 skipped` baseline plus exactly
  one new test (`test_docs_publish_refuses_without_both_verdicts_
  passing`, item 9) — the arithmetic is exact, not approximate. The 2
  skips are the same pre-existing, unrelated `cargo`/`npm`-not-installed
  gates the original audit already correctly identified and distinguished
  from the `L-114`/`L-107` knowledge-debt baseline.
- **`ruff check`**: `ruff check .` across the whole repository reports
  176 findings (171 `E501`, 2 `F841`, 1 `UP037`, 1 `I001`, 1 `F401`).
  Directly confirmed **none** touch any Stage 87A file: `ruff check .
  --output-format=concise | grep -E "doc_compiler|compile_doc_section|
  check_doc_schema"` → no output. The 176 findings are spread across
  pre-existing files this phase did not touch (`scripts/assess_change_
  impact.py`, `scripts/check_self_knowledge_quality.py`,
  `src/codecompass/knowledge_api.py`, and the same pre-existing
  `cli.py:1762-1802` lines the original audit already traced to commits
  from six days before Phase 87 began). Consistent with — not a
  regression from — the original audit's scoped-clean finding.
- **No `CLAUDE.md`/`decisions/*.md` drift**: `git diff 4a2b077..HEAD --
  CLAUDE.md decisions/` is empty. `ls decisions/` confirms the newest
  file is still `0094-knowledge-placement-policy-and-review.md` — no new
  ADR landed as part of this fix pass, consistent with the fix pass's own
  claim that none of the 9 items required one.
- **`git status --short`**: clean, both before and after this re-audit's
  own read-only checks (no `docs maintain` or other mutating command was
  re-run during this pass; nothing needed restoring).
- **HEAD**: confirmed at `61182a8`, matching the task's stated range
  exactly; `git log --oneline -5` confirms the expected commit sequence
  (`61182a8`, `e368155`, `b8d8263`, `b81ace7`, `fe664b7`).

### Verdict

**PASS WITH NON-BLOCKING OBSERVATIONS.**

All 9 items from the prior FAIL's fix list — including the originally
"recommended, not required" 9th item — are genuinely, substantively
closed, independently re-verified against the real repository state
rather than trusted from any commit message. The underlying
implementation, tests, and real demonstration were already confirmed
solid by the original audit and remain unchanged and unregressed (full
suite green at 1275/2 skipped, `ruff` clean for every Stage 87A file, no
protected-file drift, clean working tree).

Two narrow, non-blocking observations from this re-audit (neither
reopens any of the 9 items, neither is new scope creep, neither
contradicts the fix pass's own claims):

1. `planning/CONTEXT.md` does not name `L-118`/`L-119` anywhere, unlike
   the directly analogous `L-116`/`L-117` (same `retained`-pending-
   `§0`-approval status), which are named explicitly in "Next concrete
   step." A future session reading `CONTEXT.md` alone would miss that
   these two learnings are waiting on the same kind of decision. Nothing
   stated is false; this is a completeness gap, not an accuracy one.
2. `planning/ROADMAP.md`'s Phase 87 row's single-word Status column
   still reads `planned` (unchanged from before the fix pass) — accurate
   under this table's own existing done/not-started/planned vocabulary
   (confirmed: Phase 87 is the only `planned` row in the whole table),
   and the row's own prose fully and accurately narrates Stage 87A's real
   status, but the bare status word alone does not visually distinguish
   "stage implemented, phase not done" from "nothing started yet."

Neither observation drives a FAIL. Both are suggestions for the lead's
own consideration, not defects blocking Stage 87A's own DoD closure.
