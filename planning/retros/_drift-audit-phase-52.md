# Docs-drift audit — Phase 52 (context edge lifecycle / agent-driven enrichment)

**Scope:** uncommitted working-tree diff (`git status`/`git diff`, all
changes unstaged) implementing `planning/phase-52-context-edge-lifecycle.md`.
Independent re-derivation from source, not from `docs-maintainer`'s or any
other agent's summary of what it changed.

**Verdict: DRIFT — 2 findings, both non-blocking.**

## What was checked

- `src/codecompass/cli.py`'s real `enrich_apply` function (read in full,
  lines 1104-1206) against `docs/cli-reference.md`'s new
  `codecompass enrich apply` section.
- `src/codecompass/relation_enrichment.py::apply_results`'s real new
  signature (`apply_results(conn, results, *, model=_MODEL)`) and
  docstring against every place `architecture/overview.md` quotes or
  describes that signature (found two: line ~1467 and line ~1554).
- `relation_enrichment.select_candidates` (the "pending" test
  `enrich_apply` validates against) and `graph.RELATION_LABELS`, to
  confirm the CLI's rejection logic and the docs' description of it are
  literally the same thing.
- `ai-docs/README.md`'s "never invents a relationship," "never writes
  AI-generated content into your own hand-authored files," and "AI
  enrichment is optional" boundary claims, re-verified against the new
  `enrich apply` code path specifically (not just against the doc's own
  restated claim about itself).
- Ran the new tests directly (`.venv/bin/python -m pytest tests/test_cli.py
  -k enrich` → 13 passed; `tests/test_relation_enrichment.py -k model` → 2
  passed) and `ruff check` on both touched modules — clean — plus
  `scripts/check_user_docs.py --strict` — no findings. Confirms the
  reported test/lint status rather than trusting it.
- Grepped every `.md` file for `context-use-log` and `enrich apply` to
  find every doc that could now be stale, not just the ones the phase
  plan says it touched.
- README.md's own "what's implemented" enumeration, and its `decisions/`
  references, for a Phase-52-shaped gap.

## Findings

### 1. (non-blocking) `architecture/overview.md:1467` quotes `apply_results`'s old two-argument signature, now inconsistent with the same file's own updated quote 87 lines later

`architecture/overview.md:1464-1469` (unchanged by this diff — the
"non-negotiable boundary" paragraph, dating to Phase 22):

> Enforced structurally, not just by convention — `apply_results(conn,
> results) -> None` doesn't accept a `project_root` parameter at all, so
> it has no filesystem handle to a spec doc to even attempt writing to
> one.

The real, current signature (verified in `relation_enrichment.py`) is
`apply_results(conn: sqlite3.Connection, results: list[RelationEnrichmentResult], *, model: str = _MODEL) -> None`.
The *substance* of the sentence is still true (there is still no
`project_root` parameter, so the structural argument still holds), but
the signature as literally quoted is now stale — and inconsistent within
the same file, since `docs-maintainer` did correctly update the *other*
place this signature is quoted, 87 lines later at line 1554: `` `apply_
results(conn, results, model=_MODEL) -> None` ``. One of two quotes of
the same function's signature in the same doc was updated in this diff;
the other, earlier one wasn't.

Non-blocking: doesn't make any claim to a user false, just leaves one
sentence's signature-rendering behind the other. Should be updated to
`apply_results(conn, results, *, model=_MODEL) -> None` (or simply
dropped down to `apply_results(...)`) for internal consistency the next
time this section is touched.

### 2. (non-blocking) `docs/cli-reference.md`'s `enrich apply` section overstates what's printed on success

`docs/cli-reference.md:227-228`:

> Prints a per-entry accepted/rejected summary and exits non-zero if
> anything was rejected.

The real code (`cli.py:1198-1206`) prints a **count**, not a per-entry
list, for accepted results:

```python
console.print(
    f"[green]applied[/green] {len(results)} agent-enrichment result(s) "
    f"from {agent!r}"
)
if rejected:
    console.print(f"[yellow]rejected {len(rejected)} entrie(s):[/yellow]")
    for reason in rejected:
        console.print(f"  - {reason}")
    raise typer.Exit(code=1)
```

Only the *rejected* side is genuinely per-entry (one bulleted reason per
rejected entry); the accepted side is a single aggregate count
(`applied N agent-enrichment result(s) from 'agent'`), with no per-entry
breakdown of which edges were actually written. "Per-entry
accepted/rejected summary" reads as if both sides list entries
individually; only one does.

Non-blocking: the exit-code claim and the rejection-reason claim are
exactly right, and a user/agent relying on this section to interpret
real output won't be misled about behavior that matters (whether
something was rejected, and why) — just about how granular the success
message is.

## Verified as accurate (no drift)

- `docs/cli-reference.md`'s new `codecompass enrich apply` section: the
  argument shape (`entries.json` positional, `--agent` required option),
  the `model=f"agent:{name}"` recording convention, the rejection
  conditions (not-pending, invalid `relation_label`, missing
  `ai_summary`), "built from the matched candidate's own `content_hash`,
  never an agent-supplied one," and "never touches a graph-fact table"
  all match `cli.py`'s real `enrich_apply` body exactly, verified
  line-by-line against `relation_enrichment.select_candidates` and
  `graph.RELATION_LABELS` (not against the plan's stated intent).
- `docs/cli-reference.md`'s top blockquote listing `enrich apply` among
  implemented commands — accurate.
- `architecture/overview.md`'s Phase 52 paragraph (lines 1558-1569+)
  describing the new signature, the second-producer relationship, and
  "the trust boundary is enforced by `enrich apply` itself, not by agent
  instruction" — matches the real code's validation-before-write
  ordering (candidates are computed and checked *before* any
  `apply_results` call, inside the same `with _graph_session` block).
- `ai-docs/README.md`'s extended "mechanical relationship detection"
  bullet, describing two producers (batched API call, or a narrow Claude
  Code agent via `enrich apply`) — accurate description of the new
  second path.
- `ai-docs/README.md`'s "What it does NOT do" boundary claims
  ("never invents a relationship that isn't mechanically detected
  first," "never writes AI-generated content into your own hand-authored
  files," "AI enrichment is optional") all independently re-checked
  against the new code path, not just against the doc's own restated
  claim: `enrich_apply` only accepts entries matching
  `select_candidates`'s pending list (pre-existing, mechanically-detected
  edges — no new-relationship invention possible), writes only to
  `context-graph.db` via `apply_results`/`graph.record_relation_
  enrichment` (no filesystem write to any spec doc, no `project_root`
  parameter to do so with), and is an entirely separate, opt-in CLI
  invocation that bare `sync`/`init`/`check` never call — AI enrichment
  (of either kind) remains non-required. All three claims still hold
  exactly as stated, with the new producer folded in.
- No current-truth doc (`README.md`, `docs/`, `architecture/`,
  `ai-docs/`) or `.claude/agents/*.md` treats `planning/context-use-log.md`
  as the live instrument. The only remaining `.claude/agents/` reference
  (`reference-project-tester.md:50`) explicitly frames it as historical
  ("superseding the old `context-use-log.md` 4-liner"). `planning/
  context-use-log.md` itself carries a correct "superseded" pointer note
  at its top, and `planning/context-observations/README.md`/`inbox.md`
  both correctly describe themselves as the successor. `planning/
  agent-led-workflow.md` step 4 was correctly retargeted.
  (`planning/` itself isn't a current-truth doc under this audit's
  charter, but the task specifically asked this question checked
  everywhere, including `.claude/agents/`.)
- `README.md`'s "Status" line (`bare codecompass, init, sync, index,
  check, query, chat, and undo, all fully implemented`) was considered
  for staleness given it doesn't list `enrich`, but it's explicitly
  scoped to "the foundation (phases 0-38)," a milestone `enrich apply`
  (Phase 52) postdates — same pattern the line already tolerates for
  other post-38 CLI additions (e.g. `query relations`, not separately
  named there either). Not drift.

## Out of scope for this audit, flagged anyway

- `CHANGELOG.md` has no `[Unreleased]` entry for Phase 52 yet (`git diff
  CHANGELOG.md` is empty). Not a `README.md`/`docs/`/`architecture/`/
  `ai-docs/` finding and not this audit's job to fix, but worth the lead
  knowing before calling this phase's DoD (§3 of `CLAUDE.md`) satisfied.
- `planning/ROADMAP.md`'s Phase 52 row status is `planned`, not `done`
  (expected — the phase isn't closed out yet).

## Scope note

Checked: `cli.py`'s new `enrich_apply` function and its interaction with
`_graph_session`/`select_candidates`/`RELATION_LABELS`;
`relation_enrichment.py`'s `apply_results` signature/docstring change;
`decisions/0054`; `.claude/agents/context-enrichment-agent.md`; the
`docs/cli-reference.md`, `architecture/overview.md`, `ai-docs/README.md`
diffs in full; every `.claude/agents/*.md` and `planning/agent-led-
workflow.md` change for the `context-use-log.md` → `context-observations/`
retarget; `README.md` for a parallel-enumeration gap. Not independently
re-verified: the `tests/fixtures/ledgerkit_lifecycle_demo/` fixture
content itself, the `planning/context-observations/{README,TEMPLATE,
inbox}.md` new files' internal correctness (planning-only, not a
current-truth doc under this audit's charter), and `planning/context-gaps/
TEMPLATE.md`'s new discard-reason vocabulary (also planning-only).
