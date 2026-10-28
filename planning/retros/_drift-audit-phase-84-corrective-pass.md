# Docs-drift audit — Phase 84 corrective pass (commits 45a3ca8, 4569e3f)

**Scope:** the two commits landed on top of already-`done` Phase 84:
`45a3ca8` (src/codecompass/knowledge_api.py, src/codecompass/cli.py,
tests, decisions/0092) and `4569e3f` (CHANGELOG.md,
docs/reference/cli.md, planning/phase-84-consolidated-knowledge-api.md,
planning/retros/phase-84-consolidated-knowledge-api.md). Independent
read-only audit against current-truth docs (`README.md`, `docs/**`,
`architecture/**` — there is no top-level `architecture/` directory in
this repo, only `docs/architecture/`, confirmed — and `ai-docs/**`).

## Verdict: **NO DRIFT** (0 blocking findings; 2 non-blocking doc-
completeness observations in `docs/reference/cli.md`; 2 separate
non-blocking staleness notes in `planning/CONTEXT.md`, out of this
audit's governing scope but flagged per the lead's instruction)

---

## 1. `docs/reference/cli.md` — Phase 84 knowledge section

Checked against the actual code (`_oracle_result_consistency`,
`ConsistencyEnvelope`, the `cli.py` option wiring) rather than the
commit message's own self-description.

- **`--repo-root` placement — correct.** The usage block (lines
  165-171) lists `--repo-root PATH` on `get`, `trace`, `gaps`, and
  `context` only, not `search` or `export`. Verified directly against
  `src/codecompass/cli.py`: `knowledge_get`, `knowledge_trace`,
  `knowledge_gaps`, `knowledge_context` each gained a `repo_root:
  Path | None = typer.Option(None, "--repo-root", ...)` parameter;
  `knowledge_search`/`knowledge_export` were untouched by the diff.
  `find_gaps`'s own body does use `repo_root` for real (threaded into
  `derive_epistemic_profile` for each claim's required-scope check,
  `knowledge_api.py` ~line 1305), so the inclusion of `gaps` in the
  `--repo-root` list is substantively correct, not just mechanically
  wired.
- **Currency semantics prose (lines 226-233) — accurate.** "Every
  oracle-backed result/check is only ever reported `current` when it
  was positively (re)confirmed against this live checkout; without it,
  a historically recorded `PASS` is reported `unconfirmed`, never
  `current`... An actively disagreeing result... is reported `stale`
  regardless of `--repo-root`." This matches
  `_oracle_result_consistency()` exactly: `effective == "INVALID"` →
  always `status="stale"` (unconditional on `repo_root`);
  `effective in ("PASS","FAIL")` with `repo_root is not None` →
  `"current"`; same with `repo_root is None` → `"unconfirmed"`. Also
  matches `ConsistencyEnvelope`'s new fail-closed default
  (`status: str = "unconfirmed"`) and `_get_check`'s parallel logic
  (`GAP`/`NOT_REQUIRED` → `"unconfirmed"`; `repo_root is not None` →
  `"current"`; else `"unconfirmed"`). No false statement found here.

### Non-blocking: two bullet descriptions are now incomplete, not false

- `docs/reference/cli.md:199-200` (the `trace` bullet): "`--evidence`
  instead runs `trace_evidence` (supporting + contradicting evidence,
  reporting an explicit **gap** when an obligation-bearing record has
  no evidence at all)." This was the complete gap story before this
  corrective pass; `trace_evidence()` now also reports a
  `dangling_evidence_reference` gap for *any* record whose
  `supporting_evidence`/`contradicting_evidence` cites an id that
  doesn't resolve — not limited to obligation-bearing (claim/
  requirement) records. The sentence isn't false (it doesn't claim
  exhaustiveness), but a reader would not learn about the new gap
  kind from this bullet alone.
- `docs/reference/cli.md:202-206` (the `gaps` bullet): enumerates
  `unverified_required_scope`, `contradiction`, `stale_test_citation`,
  and `missing_contract` as the gap kinds `gaps` reports, reading as an
  exhaustive list. `find_gaps()`'s own docstring (`knowledge_api.py`
  ~line 1260) now documents a fifth kind, `dangling_evidence_reference`
  ("applied corpus-wide rather than to one subject at a time"), added
  by this exact corrective pass, and the bullet was not updated to
  match. Same non-blocking character as above — incomplete, not
  contradicted.

Neither finding contradicts anything the diff actually changed about
`--repo-root` or currency semantics (which is what this corrective
pass's own docs commit targeted and got right); both are pre-existing-
style enumeration gaps that this corrective pass's new gap kind now
makes stale. Recommend `docs-maintainer` add the fifth gap kind to the
`gaps` bullet and a short clause to the `trace` bullet in a follow-up,
but this does not misdescribe current behavior strongly enough to block
anything — a reader following the documented gap kinds will not be told
a false thing, just an incomplete one.

## 2. `docs/architecture/overview.md` and `docs/architecture/components.md`

Both files' `knowledge_api.py` entries (`overview.md` point 4 and its
"logical consolidation" bullet; `components.md`'s table row) describe
the module only at the level of: read-only, logical consolidation, a
per-item authority tag, "a response-time consistency envelope," and
pointers to `decisions/0084`/`0085`/`0091` and the Phase 84 plan file.
Neither file states or implies specific "current" vs. "unconfirmed" vs.
"stale" semantics, a default status value, or anything about whether
`repo_root` was previously threaded through. **They remain accurate at
their existing level of generality — no finding here.** They do not cite
`decisions/0092`, but neither committed diff updated them to do so
either, and omitting a citation to a bug-fix ADR at this level of
generality is not a false statement (unlike `docs/reference/cli.md`,
neither file describes the specific currency *rule* that changed).
Recommend (non-blocking, optional) adding `0092` to the `decisions/0084`/
`0085`/`0091` citation lists in both files for completeness, but their
current text does not misdescribe anything.

## 3. Grep sweep for `knowledge_api`, `ConsistencyEnvelope`, `trace_evidence`,
`find_gaps`, `get_context_packet` across `docs/` and `architecture/`

Hits: `docs/reference/cli.md` (covered above), `docs/architecture/
overview.md` and `docs/architecture/components.md` (covered above,
mention `knowledge_api.py` by filename only, not the other four
symbols), `docs/decisions.md` (an ADR index table, covered below).
`docs/concepts/knowledge-model.md` was also checked since it discusses
closely-related "current vs. historical verification" semantics (its
own §"Current vs. historical verification" at line 33) — but that
section describes `knowledge_intermediate.py::derive_epistemic_profile`'s
`verified_scopes`/`unconfirmed_scopes`/`known_gap_scopes`, a mechanism
this corrective pass did not touch (confirmed: the commit's own message
states "No change to oracle.py, graph.py, or knowledge_intermediate.py,"
and the diff confirms it — `find_gaps()` and `_knowledge_consistency()`
*call* `derive_epistemic_profile` but do not modify it). That section
remains accurate and out of scope. No `knowledge_api.py`/
`ConsistencyEnvelope`/`trace_evidence`/`find_gaps`/`get_context_packet`
mentions found in `README.md` or `ai-docs/**`.

`docs/decisions.md` lists ADRs through `0086` in its table body and its
own header line states (line 5) the index "runs `0001`-`0085`." This is
stale (actual `decisions/` directory runs through `0092`, including this
pass's own `0092`), but confirmed via `git log -- docs/decisions.md`
that this file was already behind before either of this pass's two
commits (last touched for `0086`'s own docs commit, well before Phase
84's original completion). **Out of this audit's scope** — it is a
pre-existing gap this corrective pass did not create or worsen, not a
new drift finding against the diff under audit. Flagged here only as an
FYI for whoever next reconciles `docs/decisions.md` generally; not
counted toward this audit's verdict.

## 4. `planning/CONTEXT.md` — explicitly out of this audit's governing
scope (CLAUDE.md §5 names `README.md`/`docs/`/`architecture/`/
`ai-docs/` as the drift-reconstructor's targets, not `CONTEXT.md`), but
checked per the task's own instruction, as a non-blocking note only —
**not counted toward the verdict above**:

- `planning/CONTEXT.md:32` states `query relations migrated onto this
  API's own doc_mentions relation, confirmed byte-identical before/
  after`. This corrective pass's own test-docstring fix
  (`tests/test_cli.py::test_query_relations_backward_compatible_after_
  knowledge_api_migration`) now explicitly documents that only the
  **JSON** output was ever actually confirmed byte-for-byte; the
  **table** output was only ever substring-asserted, and a true
  full-table literal comparison was confirmed infeasible at the
  command's own default render width (Rich truncates some cells).
  `CONTEXT.md`'s unqualified "confirmed byte-identical before/after" is
  now a demonstrated over-claim for the table-output half of that
  command, by this corrective pass's own investigation. Worth folding
  into the separate roadmap/context reconciliation step.
- `planning/CONTEXT.md:32-33` also still says "47 new tests
  (`tests/test_knowledge_api.py`)" — now stale; the file has 65 test
  functions after this corrective pass's 18 additions (confirmed by
  direct count: `grep -c '^    def test_' tests/test_knowledge_api.py`
  → 65, matching the corrective-pass commit message's own "47 -> 65"
  claim).

Both are presentation/count staleness in a file this mode's scope
doesn't own; neither is a "current-truth doc" finding under §5's gate.

## 5. Docstrings in `src/codecompass/knowledge_api.py` / `src/codecompass/cli.py`
not touched by this diff

Checked `ConsistencyEnvelope`'s own class docstring (unchanged by this
diff, pre-existing text): "`status` is `"current"` only when every
applicable piece could be positively (re)confirmed; `"unconfirmed"` when
a piece exists but could not be live-reconfirmed... `"stale"` when a
piece was *actively* found to disagree." This text was already present
pre-fix (describing the *intended* semantics) and is now, post-fix,
actually true of the implementation — no contradiction, in fact the
reverse of drift: the code caught up to what this docstring always
claimed. Checked `get()`'s and `traverse()`'s own top-level docstrings
(both pre-existing, untouched by this diff) — neither makes any claim
about `repo_root`, default status, or currency semantics one way or the
other, so there is nothing in them to contradict. No stale docstring
found.

## Scope note

Checked: `src/codecompass/knowledge_api.py` and `src/codecompass/cli.py`
diffs directly (not the commit message's own summary); `docs/reference/
cli.md`'s Phase 84 section line-by-line against the code; a full grep
sweep of `docs/`, `README.md`, `ai-docs/` for every symbol this diff
touched; `docs/architecture/overview.md` and `docs/architecture/
components.md`'s existing `knowledge_api.py` entries; `docs/decisions.md`
and `docs/concepts/knowledge-model.md` as grep hits; `planning/
CONTEXT.md`'s Phase 84 section (explicitly out-of-scope per CLAUDE.md
§5, checked anyway per task instruction, flagged non-blocking only).

Not checked / deliberately out of scope: `tests/test_knowledge_api.py`
and `tests/test_cli.py` content beyond confirming the test-count claim
and reading the corrected docstring (tests are not a "current-truth doc"
under §5); `decisions/0092`'s own content (an ADR, not subject to this
drift-audit mode — its *existence and citation* were checked only
insofar as `docs/reference/cli.md` cites it correctly, which it does);
`planning/phase-84-consolidated-knowledge-api.md` and `planning/retros/
phase-84-consolidated-knowledge-api.md`'s own new sections (planning
docs, not `docs/`/`architecture/`/`README.md`/`ai-docs/`, out of this
mode's governing scope). No domain-claim staleness check performed:
`docs/domain/` does not exist in this repository (confirmed: no such
directory), so per this role's own instructions that check is skipped
entirely.

## Domain-claim staleness candidates

None — `docs/domain/` does not exist yet in this repository.
