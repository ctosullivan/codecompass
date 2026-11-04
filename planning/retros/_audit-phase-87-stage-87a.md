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
