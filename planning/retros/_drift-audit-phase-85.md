# Drift audit — Phase 85 (Self-Curation and Knowledge-Quality Validation)

**Scope:** commit `ff856d6` (implementation) — the real dogfood against
`planning/knowledge/first-party-source-symbols/`, the new `docs/
workflows/self-curation-loop.md`, the new `scripts/check_self_knowledge_
quality.py`, the new `planning/retros/phase-85-self-curation-
investigation-log.md`, and the two amended agent briefs (`.claude/agents/
context-researcher.md`, `.claude/agents/knowledge-curator.md`). Audited
against current-truth docs: `README.md`, `docs/**`, `architecture/**`
(none exists as a top-level dir in this repo; docs live under `docs/
architecture/`), `ai-docs/**`. Confirmed first, independently, via `git
diff ff856d6~1 ff856d6 -- src/codecompass/knowledge_api.py src/
codecompass/oracle.py src/codecompass/knowledge_intermediate.py`: empty
diff — no canonical-module behaviour changed this phase.

**Method:** read `docs/workflows/self-curation-loop.md`, `scripts/
check_self_knowledge_quality.py`'s own module docstring in full, both
amended agent briefs' new mode sections, and the real investigation-log
file, comparing each claim line-by-line against the real source they
describe; grepped `docs/`, `README.md`, `ai-docs/` for `missing_contract`
and `find_gaps` to check for any now-incorrect severity/corpus-size
claim; read `docs/development/contributing.md`'s "Maintainer-only
tooling" section and `docs/development/testing.md`'s test-module
enumeration in full; read `docs/concepts/knowledge-model.md`'s validator-
related claim; read `ai-docs/README.md` in full; confirmed `planning/
knowledge/` (6 slugs) and `planning/contracts/` (1 contract) counts
directly via `ls`. Checked for a `docs/domain/` directory (none exists —
that check does not apply). Did not re-derive or second-guess the six
new `planning/knowledge/first-party-source-symbols/` records' own
content/correctness — a knowledge-corpus-quality question, not a
narrative-docs-drift question, outside this audit's own remit. Did not
audit `CHANGELOG.md` (outside this mode's scope: `README`/`docs`/
`architecture`/`ai-docs` only). No `git stash` or any tree-mutating
command was used — read-only throughout.

## Verdict: DRIFT — 2 findings, both non-blocking (fixed same day, commit `55f7008`)

No current-truth doc made a statement about Phase 85's changes that was
actively **false**; both findings below are stale-by-omission
enumeration gaps, not misleading claims.

### Finding 1 (non-blocking, fixed) — `docs/development/contributing.md`, "Maintainer-only tooling (`scripts/`)" section, lines 20-29

This section presents what reads as a complete catalog of maintainer-
only `scripts/` tooling (`check_knowledge_base.py`, `check_user_docs.py`,
`check_contracts.py`, `run_balance_from_spec_oracle.py`,
`assess_change_impact.py`, `prepare_cleanroom_branch.py`), each with a
one-paragraph description. It did not mention `scripts/check_self_
knowledge_quality.py`, added this phase — confirmed by direct
inspection that the new script's own module docstring states it
"mirrors `scripts/check_knowledge_base.py`/`scripts/check_contracts.
py`'s own exact `Finding(rule, message, strict)` convention," i.e. it is
exactly the kind of tool this section exists to catalog.

**Fixed** (commit `55f7008`): added an entry analogous to the existing
ones, summarizing its five composed checks and its `missing_contract`-
is-always-informational rule.

### Finding 2 (non-blocking, fixed) — `docs/development/testing.md`, line 9

Enumerated test modules for maintainer-only `scripts/` tooling without
"e.g." (`tests/test_check_knowledge_base.py`, `tests/test_check_
contracts.py`, `tests/test_check_user_docs.py`, `tests/test_prepare_
cleanroom_branch.py`, `tests/test_cleanroom_broker.py`, `tests/test_
cleanroom_prompt_assembler.py`), reading as exhaustive. Confirmed by
direct `ls tests/` that `tests/test_check_self_knowledge_quality.py`
exists (added this phase) and was omitted. Note for scoping honesty:
this enumeration was already stale before this phase in one other
respect — `tests/test_assess_change_impact.py` (Phase 83) is also
missing from it, pre-existing context, not this phase's own drift to
introduce.

**Fixed** (commit `55f7008`): added the new test module, and changed the
list to "e.g." so it no longer reads as exhaustive (closing the
pre-existing Phase 83 gap incidentally, since the list is honestly
non-exhaustive either way now).

## Checked, no drift found

- **`docs/workflows/self-curation-loop.md`** accurately describes the
  real, current behaviour of `scripts/check_self_knowledge_quality.py`
  and both amended agent briefs, confirmed field-for-field against each
  source artifact directly (the eight-step loop, the five-outcome
  table, the Observation-`method` reproduction-bucket split, the
  investigation-log schema, the validator's severity-rule summary).
- **`ai-docs/README.md`** — a high-level capability/boundary overview
  that does not enumerate specific maintainer scripts, specific record
  kinds beyond its general "persistent, human/AI-tool-editable
  knowledge layer" line, or `planning/retros/` contents at all; nothing
  in it is contradicted by the new investigation-log artifact or
  validator.
- **Corpus-size/severity claims**: `planning/knowledge/` (6 slugs),
  `planning/contracts/` (1 contract) match the new script's own
  docstring exactly; no other doc anywhere makes a claim about
  `find_gaps()`'s severity rules or corpus counts that this phase's
  changes could have made incorrect.
- **`docs/concepts/knowledge-model.md`** line 18's claim ("there is no
  shipped validator for an adopting project's own `planning/knowledge/`
  tree beyond `knowledge_intermediate.py` itself — the maintainer-only
  `scripts/check_knowledge_base.py` is hard-coded to this one
  repository…") remains true in substance — `check_self_knowledge_
  quality.py` is equally hard-coded to this one repository (its own
  `DEFAULT_LEDGERKIT_ROOT` points at `~/projects/ledgerkit`) — so no
  false statement results; not a standalone finding.

## Note on this record's own provenance

This audit record was reconstructed, same day, from the full report of
the docs-reconstructor dispatch that actually performed this pass —
found missing as a persisted artifact by the independent `release-
phase-auditor` pass (`planning/retros/_audit-phase-85.md`), whose own
"What to check" item 3 requires it. The underlying pass genuinely ran
before `55f7008` landed (that commit's own message cites these same two
findings, independently re-confirmed as real and correctly fixed by the
auditor); only the standalone artifact recording its full scope was
missing, not the pass itself. Reconstructed verbatim from the dispatch's
own returned report rather than re-run, per the auditor's own offered
alternative ("or re-run docs-reconstructor fresh if reconstructing the
record isn't preferred") — reconstruction was chosen since the original
pass's full method and findings were still available in full, not
summarized or lossy.
