> **SELF-TEST / INSTRUMENT SANITY CHECK — NOT A REAL REFERENCE-PROJECT
> DATAPOINT.** This evaluates CodeCompass's own repository against
> itself, per Phase 44's instrument sanity check
> (`planning/phase-44-reference-project-protocol.md`). It exists to check
> that `TEMPLATE-evaluation.md` produces a coherent report and that the
> "inspect directly, don't use CodeCompass to check CodeCompass" rule is
> followable — not to score CodeCompass's real-world usefulness. **Do not
> aggregate this into Phase 47/62-63 findings.**

# Context-quality evaluation — typer usage + version (self-test)

## Setup

- **Reference project:** CodeCompass's own repository (self-test — not
  an external reference project)
- **Pinned commit:** `bf6db6ec0b93f8d6b6ac6179abfb26d0bfd23386`
- **CodeCompass revision:** 1.0.0.dev0 (`pyproject.toml` `version`),
  same commit as above
- **Task:** What does this project use `typer` for, and at what version?
- **Context CodeCompass supplied:**

```
$ codecompass query vendor typer
typer (python) 0.27.2 — usage count: 43
[symbol table with mechanically-sourced purpose blurbs, truncated]

$ codecompass query symbol Typer --json
[
  {
    "id": 2367,
    "vendor": "typer",
    "name": "Typer",
    "purpose": "`Typer` main class, the main entrypoint to use Typer.\n\nRead more in the\n[Typer docs for First Steps](https://typer.tiangolo.com/tutorial/typer-app/).\n\n## Example\n\n```python\nimport typer\n\napp = typer.Typer()\n```",
    "usage_count": 2,
    "used_at": [
      {"source_file_path": "src/codecompass/cli.py", "line": 51},
      {"source_file_path": "src/codecompass/cli.py", "line": 54}
    ],
    "documenting_artifacts": [
      {"id": 32, "path": "vendor/typer/src/README.md", "kind": "vendor_doc"}
    ]
  }
]
```

(Retrieved by the lead against a freshly-rebuilt `context-graph.db`,
mechanical-only sync, no `ANTHROPIC_API_KEY` set — no AI enrichment ran
this cycle.)

## Ground truth established (direct inspection, no `codecompass` commands run)

- `src/codecompass/cli.py:51` — `app = typer.Typer(help="Grounded,
  version-pinned dependency reference docs for AI coding agents.")` — the
  root CLI application object.
- `src/codecompass/cli.py:54` — `query_app = typer.Typer(help="Query the
  context graph (context-graph.db).")`, then line 55 —
  `app.add_typer(query_app, name="query")` — a nested subcommand group
  for `codecompass query ...`.
- `typer` usage is confined entirely to `src/codecompass/cli.py` (no
  other `src/` file imports it). Within that file, the module's other
  API surface is used extensively beyond the two `Typer()`
  instantiations: `typer.Option` ×17, `typer.Exit` ×13, `typer.Argument`
  ×5, `typer.confirm` ×2, `typer.Context` ×1 (verified by
  `grep -oE "typer\.[A-Za-z_]+" src/codecompass/cli.py | sort | uniq
  -c`). This is how every CLI option, positional argument, controlled
  exit code, and the Phase B confirmation prompt are actually
  implemented — the fuller answer to "what is typer used for."
  `typer.testing.CliRunner` is additionally used in three test files
  (`tests/test_cli.py`, `tests/test_chat.py`, `tests/test_undo.py`) to
  functionally exercise the CLI.
- `pyproject.toml:21` declares `"typer>=0.27"` — a floor, not an exact
  pin.
- The actually-installed/resolved version in this environment's `.venv`
  is `typer==0.27.2` (`.venv/lib/python*/site-packages/typer-0.27.2.dist-info`).
  `vendor/typer/DEPTREE.md` independently records `typer@0.27.2`,
  consistent with the installed version.
- Note on freshness cross-check: the **committed** (HEAD) `CLAUDE.md`
  vendor table (shown to me at session start as the checked-in file)
  still lists typer at `0.27.1`, enriched `yes` — a stale snapshot from
  before this session's resync. The repo's **current, uncommitted**
  working-tree `CLAUDE.md` (visible via `git diff CLAUDE.md`, and already
  flagged `M` in `git status`) has been mechanically regenerated to show
  typer at `0.27.2`, enriched `no` — exactly consistent with the task's
  description of "freshly-rebuilt context-graph.db, mechanical-only
  sync, no AI enrichment." This is a good sign for freshness, not a
  contradiction: CodeCompass's query output matches the *current* repo
  state, not the stale committed doc.
- A precise-as-possible reconciliation of "usage count: 43": naive
  `grep -c "typer\."` across `src/`, `tests/`, `scripts/` gives 48
  (40 in `cli.py`, plus 5 textual/string matches in
  `tests/test_check_user_docs.py` that are about a docstring describing
  `Typer` decorators rather than live typer calls, plus 3
  `typer.testing.CliRunner` imports in test files). I could not exactly
  reproduce "43" from any single counting convention I tried, but every
  plausible convention lands in the low-to-high 40s — i.e. the figure is
  clearly in the right ballpark and not evidence of a wrong count, just
  not independently reproducible to the exact digit.

## Criteria assessment

| Criterion | Rating | Notes |
|---|---|---|
| Accuracy | strong | Version (0.27.2) is exactly correct against both the installed `.venv` package and `vendor/typer/DEPTREE.md`. Both `used_at` line numbers (51, 54) are exactly correct — verified by direct reading. The `Typer` class purpose blurb accurately reflects the class's role and matches upstream Typer's own doc wording. The one unverifiable figure ("usage count: 43") is in the right ballpark against direct grep (~40-48 depending on convention) and not demonstrably wrong. |
| Relevance | strong | Both queries target exactly the dependency and symbol the task asks about; nothing off-topic in what was shown. |
| Completeness | adequate | The version half of the task is fully and precisely answered. The "what is it used for" half is only partially answered by what was shown: the two `Typer()` app-construction call sites (main app + nested `query` subcommand group) are correctly surfaced, but the visible context does not mention that the bulk of the 43 usages — `typer.Option`, `typer.Exit`, `typer.Argument`, `typer.confirm`, `typer.Context` — is what actually implements every CLI option, argument, exit code, and confirmation prompt. That is the more complete answer to "what is typer used for" and it is not visible in what was supplied (it may be in the truncated symbol table, which I cannot credit or fault since it wasn't shown to me). Also not surfaced: `pyproject.toml` only floors the dependency at `>=0.27`; the resolved `0.27.2` is reported as if it were the version, without noting the constraint allows drift. |
| Freshness | strong | 0.27.2 matches the actually-installed and actually-vendored version in this environment right now, not a stale pin — corroborated by the repo's own (uncommitted) regenerated `CLAUDE.md` vendor table already showing 0.27.2/unenriched, matching the task's "mechanical-only sync, no AI enrichment" framing exactly. |
| Grounding / provenance | strong | Both `used_at` citations point to real, exact lines I independently verified. The purpose blurb is explicitly traced to a named vendor doc artifact (`vendor/typer/src/README.md`). |
| Noise | strong (for what was shown) / n/a (for the truncated portion) | The JSON symbol result is compact and on-topic. The `query vendor typer` table was truncated in what was delivered to the lead, so I cannot rate the noise level of the part that wasn't shown. |
| Safety / trustworthiness | strong | No claim shown was incorrect or misleading; nothing was presented with unwarranted authority. |

## Verdict: PASS WITH GAPS

No claim in the supplied context is incorrect or misleading — every
verifiable figure (version, both line-number citations, the purpose
text) checks out exactly against direct inspection of the repository and
the installed environment. It falls short of a clean PASS only because
the "what is `typer` used for" half of the task is materially
under-answered by what was actually shown: querying the `Typer` *class*
symbol alone surfaces app-construction but omits the option/argument/
exit-code/confirm API surface that accounts for the large majority of
actual usage and is the more complete story of "what this project uses
typer for." That is an incompleteness, not a wrongness, so PASS WITH GAPS
(not FAIL) is the correct call per the spec's verdict definitions.

## Context advantage: LOW

Could a competent fresh Claude session have obtained equivalent context
trivially through ordinary repository inspection? **Yes.** `grep -rn
"typer" src/` immediately shows the dependency is confined to one file;
reading the first ~60 lines of `cli.py` shows both `Typer()`
instantiations and the `add_typer(..., name="query")` relationship in
context (with the docstring naming the CLI's actual commands); `grep
typer pyproject.toml` reveals the `>=0.27` floor in one line; and `pip
show typer` (or inspecting `.venv`) gives the exact resolved version.
That's three cheap commands plus one short file read — arguably yielding
a *more* complete answer than what CodeCompass's two commands showed here
(a fresh read of `cli.py` would surface the Option/Exit/Argument/confirm
usage and the `>=0.27` floor-vs-resolved distinction directly, neither of
which appeared in the supplied context). CodeCompass's genuine
contribution on this task is speed and an exact grounded citation without
needing a second `pip show` step — real, but marginal, for a
single-file, single-dependency case like this one.

## Material gaps / failures

- The `symbol Typer --json` query, scoped to one symbol, does not
  surface the other `typer` API members (`Option`, `Exit`, `Argument`,
  `confirm`, `Context`) that make up the bulk of the vendor's reported
  43 usages and are the fuller answer to "what is this used for" — a
  reader relying only on what's shown here would undersell typer's role
  to "constructs two app objects" rather than "implements every CLI
  option, argument, exit path, and confirmation prompt in the tool."
- The vendor-level version report (0.27.2) does not distinguish
  "declared constraint" (`typer>=0.27`, a floor) from "currently
  resolved version" (0.27.2) — reporting only the latter, unqualified,
  could read as an exact pin to someone who hasn't also checked
  `pyproject.toml`.
- The `query vendor typer` symbol table was truncated in what was
  delivered to the lead; its completeness and noise level can't be
  evaluated from the record, which is itself worth flagging as a gap in
  what got captured for this evaluation rather than in CodeCompass's
  underlying output.
- The reported usage count (43) could not be exactly reproduced by direct
  grep under any counting convention I tried (yielded 40-48 depending on
  what's included); not wrong, but not independently verifiable to the
  exact digit either — a minor, non-material grounding soft-spot worth
  noting for the instrument itself (usage-count provenance isn't
  currently traceable the way per-symbol `used_at` line citations are).

## Would this have misled the implementing agent? no

Nothing shown was incorrect or authoritatively wrong; an agent trusting
this context on the version question would be exactly right, and on the
"what for" question would be directionally right (it does build the
CLI's app objects) but would understate the breadth of typer's actual
role unless it also read `cli.py` itself — an incompleteness, not a
misdirection.
