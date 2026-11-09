# Independent re-audit: Phase 87, Stage 87B post-closeout hardening pass, self-certification fix (commit `9cdbb6f`)

**Auditor:** `release-phase-auditor` (independent dispatch)
**Audited commit:** `9cdbb6f` ("fix(phase-87): correct a self-certification defect in the hardening-pass changelog entry")
**Preceding (FAILed) commit:** `1e3301f` ("fix(phase-87): Stage 87B post-closeout hardening -- draft integrity, schema freshness, narrower write-boundary race")
**First audit (FAIL) on `1e3301f`:** `planning/retros/_audit-phase-87-stage-87b-hardening.md` (preserved unchanged, not overwritten)
**Date:** 2026-11-09
**Verdict: PASS**

This re-audit is scoped to the correction commit `9cdbb6f` and confirms
the overall state at current `HEAD` (`9cdbb6f`). The first audit
(`_audit-phase-87-stage-87b-hardening.md`) already did deep, direct
verification of the underlying code, tests, and three fixes (Findings
A/B/C) against `1e3301f` and found all of it genuinely correct; this
pass does not re-derive that from zero, but independently re-confirms
a representative sample of it directly rather than taking the prior
report's word for all of it (see "Direct spot-checks" below), per this
dispatch's own instruction. No new commit landed between the first
audit and this one — `9cdbb6f` is the one and only correction, and it
is the commit under audit here.

## 1. Scope of `9cdbb6f` confirmed narrow

`git show 9cdbb6f --stat`:

```
CHANGELOG.md                                                       |  35 +--
planning/retros/_audit-phase-87-stage-87b-hardening.md             | 248 +++++++++++++
planning/retros/phase-87-stage-87b-knowledge-change-demonstration.md|  54 +++--
3 files changed, 309 insertions(+), 28 deletions(-)
```

No code file, no test file, and no other documentation file changed.
The new file added is the first audit's own FAIL report itself (being
persisted into history by this commit) — not new implementation. This
matches the task's description exactly: a pure narrative correction.

## 2. `CHANGELOG.md`'s corrected entry — no premature audit claim remains

Read the full, current Stage 87B post-closeout hardening entry
(`CHANGELOG.md` lines 12-77) directly. It now reads, in its closing
lines:

> A first independent `release-phase-auditor` pass against this commit
> returned **FAIL**: this entry's own earlier draft falsely claimed an
> audit had already run and passed, before any audit had actually been
> dispatched — a self-certification defect the auditor caught
> directly, independent of the (confirmed correct) underlying code.
> Corrected here; see `planning/retros/_audit-phase-87-stage-87b-
> hardening.md` for the full FAIL account and the re-audit once it
> runs. Stage 87B's closure against this hardened code is **pending**
> that re-audit. Phase 87 overall remains not `done`; Stage 87C remains
> separately planned, unauthorised, and unstarted.

Confirmed:
- No claim anywhere in this entry states or implies an audit of this
  fix has already returned PASS. The only audit outcome asserted is
  the FAIL on the *prior* commit, correctly attributed and correctly
  cited to the real file that documents it.
- The entry honestly states Stage 87B's closure is **pending** this
  re-audit — exactly the state of affairs at the time `9cdbb6f` was
  written, and exactly what this dispatch exists to resolve.
- The citation `planning/retros/_audit-phase-87-stage-87b-hardening.md`
  is real, exists, and is the correct FAIL account (confirmed present
  and unmodified from the first audit's own write).

No self-certification defect remains in this entry.

## 3. "14 of 15" accounting — internally consistent, no stray "13"

- `CHANGELOG.md` line 52: "a fresh independent audit directly
  reproduced 14 of the 15 ... (the 15th, a determinism property, is
  correctly not expected to catch anything)." Searched the entire
  Stage 87B hardening entry (lines 12-77) for any remaining "13" —
  none found.
- `planning/retros/phase-87-stage-87b-knowledge-change-demonstration.md`'s
  "Verification" paragraph (corrected by this commit) now reads "14 of
  the 15 testing new mechanism behavior were directly confirmed to fail
  against the pre-fix code ... the 15th (a determinism property already
  true pre-fix) correctly passes in both regimes," and explicitly notes
  "An earlier draft of this section mistakenly still counted it among
  'the other 2,' undercounting the real catches as 13 — corrected here
  to the true figure, 14." No remaining "13" in this section's own
  content.
- The retro's new "Audit, first pass (commit `1e3301f`): FAIL"
  subsection also correctly states the true figure as 14, consistent
  with the Verification paragraph above it.
- Confirmed (via `grep`) that the only other "13" occurrences in either
  file belong to the **unrelated, earlier Stage 87A hardening pass**
  (`CHANGELOG.md` lines 215/217/231: "13 newly-written tests ... all 13
  of the newly-written `test_cli.py` tests confirmed failing ...").
  This is correctly out of this pass's scope, per the task's own
  instruction, and is not flagged.

## 4. Direct spot-checks of the underlying code/tests (not merely trusting the first audit)

- **`src/codecompass/doc_compiler.py`**: read directly. `class
  DocPublishConflictError(DocCompilerError)` (line 623), `def
  document_identity(doc_path: Path) -> str` (line 638, returns
  `"absent"` for a missing file else `sha256_text` of its content),
  `def _atomic_write_text(path, content)` (line 652, `tempfile.mkstemp`
  + `os.replace`, cleans up the temp file on any exception). Confirmed
  `publish_section`'s own `expected_document_identity` parameter: when
  given, `document_identity(doc_path)` is recomputed at the very top of
  the function (line 711) and compared before any read/write of the
  document; mismatch raises `DocPublishConflictError` without writing
  anything (lines 710-718). Confirmed all three of `publish_section`'s
  own write call sites (lines 728, 747, 751 — new-file, same-region
  replace, and append-new-region) go through `_atomic_write_text`,
  with no other write path in the function.
- **`src/codecompass/cli.py`**: read directly. `def
  _reviewed_draft_integrity_error(manifest) -> tuple[str | None, str |
  None]` (line 2288) recomputes `sha256_text(tagged_draft)` against the
  manifest's own `draft_sha256`, and separately recomputes
  `strip_citation_tags(tagged_draft).strip()` against the manifest's
  `draft_body`, returning the *derived* body — never
  `manifest["draft_body"]` trusted directly — as the one value
  downstream logic uses. `def _reread_pending_at_write_boundary()`
  (line 2386) re-reads `pending_path` fresh from disk inside the lock,
  re-runs the same integrity check against that fresh copy, and
  cross-checks `draft_sha256`/`evidence_sha256`/`schema_section_sha256`
  against the pre-lock snapshot. `document_identity(document_path)` is
  called at line 2494, immediately before `publish_section`, and passed
  through as `expected_document_identity`.
- **Full regression suite**, run directly by me, independently, after
  the first audit's own run (not reused): `.venv/bin/python -m pytest
  -q` → **`1352 passed, 2 skipped in 426.10s`** — exactly matching both
  the `CHANGELOG.md` claim and the first audit's own figure.
- **Targeted re-run** of the two files carrying all 15 new regression
  tests, run directly by me as a second, independent pass:
  `.venv/bin/python -m pytest -q tests/test_doc_compiler.py
  tests/test_cli.py` → **`184 passed in 176.02s`**.
- **`ruff check .`**: **176 errors** — exactly matching the claimed
  pre-existing baseline count; confirmed directly that none are in
  `src/codecompass/cli.py`, `src/codecompass/doc_compiler.py`,
  `tests/test_cli.py`, or `tests/test_doc_compiler.py` (grep for each
  path against the full findings list: zero matches).
- **`scripts/check_doc_schema.py --strict`**: `no findings`.
- **`scripts/check_user_docs.py --strict`**: `no findings`.
- **`scripts/check_knowledge_base.py`**: 24 pre-existing
  `knowledge-base-snapshot-current-divergence` info findings
  (`CL-EVID-*`/`CL-FPSS-007`), none naming `EV-CTXT-021` or anything
  this pass touched.
- **`scripts/check_knowledge_placement.py`**: 10 pre-existing
  `decision-citation-superseded` info findings in `chat.py`, `cli.py`
  (two *other*, pre-existing lines: 316, 326 — distinct from this
  pass's own new code), `doc_mapping.py`, `graph.py`, `skill.py`,
  `source_resolution.py`. None touch this pass's new code.
- **`scripts/check_contracts.py`**: 7 findings, entirely confined to
  the pre-existing `balance-from-spec` domain.
- **`scripts/check_self_knowledge_quality.py`**: findings entirely
  confined to `CL-BFS-*` records in the same pre-existing domain.
- **`docs/architecture/components.md`**,
  **`docs/architecture/documentation-compilation-pipeline.md`**,
  **`docs/reference/cli.md`** diffs (from `1e3301f`) read directly:
  all three accurately describe `document_identity`,
  `DocPublishConflictError`, the atomic write-then-rename, the
  reviewed-draft-integrity re-derivation, and the live schema-freshness
  re-read, matching the code exactly, including the honest "narrows,
  does not fully close" framing repeated in both code docstrings and
  docs.
- **`planning/knowledge/codecompass-domain/EV-CTXT-021.yaml`** and
  **`planning/learnings/inbox.md`**'s `L-123`/`L-124` entries: read
  directly, unchanged since the first audit (not touched by `9cdbb6f`),
  both still correctly `status: candidate`, matching the governing
  task's description of a deliberately separate, not-yet-run
  reconciliation step.

## 5. No new protected-file drift

`git diff e0de671 9cdbb6f --name-only` (the full span from the
pre-hardening parent through current `HEAD`) touches:

```
CHANGELOG.md
docs/architecture/components.md
docs/architecture/documentation-compilation-pipeline.md
docs/reference/cli.md
planning/knowledge/codecompass-domain/EV-CTXT-021.yaml
planning/learnings/inbox.md
planning/retros/_audit-phase-87-stage-87b-hardening.md
planning/retros/phase-87-stage-87b-knowledge-change-demonstration.md
src/codecompass/cli.py
src/codecompass/doc_compiler.py
tests/test_cli.py
tests/test_doc_compiler.py
```

`git diff e0de671 9cdbb6f --stat -- decisions/ CLAUDE.md` returns
**empty** — confirmed directly, no `CLAUDE.md` change and no
`decisions/*` file touched by either `1e3301f` or `9cdbb6f`.

## 6. Out-of-scope working-tree note (does not affect this verdict)

The working tree has a real, deliberately-uncommitted modification to
`planning/phase-87-documentation-schema-knowledge-compiled-documentation.md`
(a new "§S. Stage 87C plan" section, 334 insertions). Confirmed this is
not part of either `1e3301f` or `9cdbb6f` (absent from both commits'
diffs) and is correctly still uncommitted — Stage 87C planning is a
separate, later step gated on this very audit passing first. Noted for
awareness only; out of this audit's scope, does not affect the verdict
either way.

## Verdict

**PASS.** The specific defect the first audit found blocking — a
`CHANGELOG.md` entry falsely claiming an independent audit had already
run and returned PASS before one had actually been dispatched — is
fully corrected in `9cdbb6f`: the premature claim and stale citation
are removed, replaced with an honest statement that closure is pending
this very re-audit, and the entry now correctly cites the real FAIL
report. The related "13 of 15" accounting error is also corrected to
the true figure of 14, consistently, in both `CHANGELOG.md` and the
retro, with no stray "13" remaining in either file's own hardening-pass
content (the unrelated Stage 87A "13" references are correctly out of
scope). The correction commit itself is narrowly scoped — no code,
test, or other file touched beyond the intended narrative correction
and the persisted first-audit report. The underlying three technical
findings (A: reviewed-draft integrity, B: live schema freshness, C:
narrower write-boundary race) remain genuinely correct and well-tested,
independently re-confirmed here by direct code inspection, a fresh full
suite run (`1352 passed, 2 skipped`), a fresh targeted run of all 15 new
tests' own files (`184 passed`), and re-running every strict
validator/checker, with no new finding of any kind. No protected-file
drift. Stage 87B's closure against this hardened code is confirmed as
of this audit.

## What remains, for the record (not blocking this verdict)

- Stage 87B's closure against the hardened code (flipping any
  remaining "pending" language in `CHANGELOG.md`/the retro to a closed
  state) is a follow-up reconciliation step, not something this audit
  performs itself (read-only, no repair). The lead should land that
  narrow reconciliation commit now that this PASS exists, citing this
  file.
- The uncommitted Stage 87C plan addition noted in §6 is unaffected by
  this verdict and remains a separate, later, already-correctly-gated
  step.
