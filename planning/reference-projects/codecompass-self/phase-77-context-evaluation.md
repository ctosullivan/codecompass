<!-- Structure per planning/v1-redefinition/context-quality-evaluation.md §2.
     Priority A task-context comparison for Phase 77 (first-party source
     awareness). Ground truth established by an independent fresh clone
     and direct source reading, per that spec's §1 ground rules — did not
     use `codecompass query`/`check`/`/discovery` to judge Ledgerkit's own
     source, only to test CodeCompass's own CLI behaviour where the task
     explicitly called for that (criterion 3). -->

# Context-quality evaluation — Phase 77 first-party source awareness (Ledgerkit DataFrame-export task)

## Setup

- **Reference project:** https://github.com/ctosullivan/ledgerkit
- **Pinned commit:** `6c90b4ca3e6c10951cb400e43db4b90bfccc5909` — confirmed
  by fresh `git clone` + `git checkout` into scratch
  (`/tmp/.../scratchpad/ledgerkit-eval/ledgerkit-ground-truth`), matching
  both the fixture-equivalence check and both agent reports' own stated
  pin.
- **CodeCompass revision:** `b473e848eaa2bbc52204aa143cb6289cba452a6e`
  (current `HEAD`; matches the installed `~/.local/bin/codecompass` CLI's
  own `source_symbols.py`/`cli.py` at the commit that introduced Phase
  77, `03f8519`).
- **Task:** locate where DataFrame export of a report result is
  implemented; identify where and how an external dependency (pandas) is
  used to implement it; list every report-result type supporting
  DataFrame export. Dispatched identically to a baseline agent (no
  CodeCompass access) and a treatment agent (CodeCompass installed and
  synced against a byte-identical fork of the same clone), per the
  seed-then-fork protocol recorded in
  `planning/reference-projects/ledgerkit/phase-77-fixture-equivalence.md`.
- **Context CodeCompass supplied:** `codecompass query source
  ledgerkit/reports.py` / `ledgerkit/models.py` / `ledgerkit/_pandas_compat.py`
  (full per-file top-level symbol listings with docstrings); `codecompass
  query source-symbol to_dataframe|require_pandas`; `codecompass query
  symbol DataFrame|to_dataframe|require_pandas`; `codecompass query
  vendor pandas`; `codecompass query vendors`; `codecompass query
  --help`. Verbatim treatment tool-call log and self-disclosed limitation
  reproduced in `planning/reference-projects/ledgerkit/phase-77-treatment-report.md`.

## Independent ground truth (established directly, not via either report or CodeCompass)

Read `ledgerkit/reports.py`, `ledgerkit/models.py`,
`ledgerkit/_pandas_compat.py`, `pyproject.toml`, `tests/test_dataframe.py`,
and `ledgerkit/cli.py` directly from the fresh pinned clone. Confirmed:

- **Exactly five `to_dataframe()` methods, across two files, at the exact
  line numbers both reports cite:** `BalanceResult.to_dataframe` (`reports.py:65`,
  class at `:39`), `RegisterResult.to_dataframe` (`:116`, class `:93`),
  `AccountsResult.to_dataframe` (`:171`, class `:149`),
  `ReportSectionResult.to_dataframe` (`models.py:252`, class `:244`),
  `Journal.to_dataframe` (`models.py:479`, class `:296`). A repo-wide
  `grep -rn "to_dataframe\|as_dataframe\|\.DataFrame("` across every
  `.py` file (including files neither agent opened, e.g. `cli.py`,
  `checks.py`, `query/*.py`) turns up no sixth implementation and no
  CLI-level DataFrame export — the feature is library-API-only, exactly
  as both reports frame it.
- **`JournalStats` (`reports.py:182`) genuinely has no `to_dataframe()`** —
  both reports' claim that it's the one report-result type *without*
  DataFrame support is correct.
- **Pandas mechanism confirmed exactly as both reports describe:**
  `pyproject.toml` `dependencies = []` (unconditional), `[project.optional-dependencies]
  pandas = ["pandas>=1.3"]`; `_pandas_compat.py` imports pandas only
  under `TYPE_CHECKING` at module scope, and its one function,
  `require_pandas()`, does the real `import pandas as pd` inside a
  `try/except ImportError`, raising `pip install ledgerkit[pandas]`.
  Every one of the five `to_dataframe()` bodies calls
  `from ledgerkit._pandas_compat import require_pandas` inside the method
  body — genuinely lazy, genuinely optional, never imported at package
  import time.
- Both reports are **factually correct on every material claim in items
  1–3 of the task.** Neither missed an implementation, misstated the
  optional/lazy mechanism, nor misidentified a report-result type. This
  is a case where the ground-truth check found nothing to overturn.

## Criterion 3 — the treatment agent's self-disclosed CodeCompass limitation, independently reproduced

Reproduced directly, not taken on the treatment report's word: installed
`codecompass` synced against a fresh copy of the same pinned clone
(`ledgerkit-codecompass-test`).

- `codecompass query source ledgerkit/reports.py` returns `BalanceResult`,
  `RegisterResult`, `AccountsResult`, `JournalStats`, and the module-level
  functions (`_matches_pattern`, `accounts`, `balance`, `register`,
  `stats`, `balance_from_spec`, etc.) with docstrings — **no
  `to_dataframe` entry appears anywhere in the output**, despite three of
  those four classes having one.
- `codecompass query source-symbol to_dataframe` returns `no source
  symbol named 'to_dataframe' found in context-graph.db` — a genuine
  miss, reproduced exactly as the treatment agent reported.
- `codecompass query source-symbol require_pandas` **does** succeed
  (module-level function, not a method) — confirms the boundary is
  specifically "top-level only," not "first-party indexing is broken."
- Root cause confirmed by reading `src/codecompass/source_symbols.py`
  directly: `_extract_python_source_symbols` calls
  `ast.iter_child_nodes(tree)` — direct children of the *module* only.
  A method defined inside a `ClassDef` body is never visited; the
  extractor has no recursion into class bodies at all, for any language.
- Confirmed **documented, not accidental**, at three independent levels:
  (1) `planning/phase-77-first-party-source-and-template.md` §2 lists
  "Nested/member symbols (a class's own methods...) — first-party symbol
  extraction stays top-level only" as an explicit non-goal; (2)
  `codecompass query --help` and `query source-symbol --help` both say
  "top-level implementation symbol" in their one-line descriptions,
  surfaced *before* a user runs the failing query; (3)
  `docs/cli-reference.md` states the same top-level-only scope in its
  user-facing CLI reference.

**Verdict on this specific claim: accurate, and it is the tool working
exactly as documented, not a defect.** It is also correctly and honestly
self-disclosed by the treatment agent — the agent did not claim
CodeCompass told it something false; it explicitly says CodeCompass
"correctly told the agent the five containing classes exist... but could
not tell it that `to_dataframe()` methods exist on them at all." That is
a precise, non-misleading characterization of a documented scope
boundary, not a bug report.

One narrower observation, evaluated against the context-gaps queue's own
explicit scope: the bare `no source symbol named 'to_dataframe' found in
context-graph.db` message (`src/codecompass/cli.py:1172`) does not
restate the top-level-only scope inline, unlike the `--help` text a step
away. In principle a less careful agent than either one dispatched here
could over-read that message as "this symbol doesn't exist in the source
at all." In practice this did not mislead the treatment agent (it
independently checked `--help` at call 9 and grepped for the real
answer regardless), and the scope is already disclosed at three other
surfaces before this query is even run. **This is not filed as a new
`CG-NNN` context-gap**: `planning/context-gaps/README.md`'s own "What
does NOT belong here" list explicitly excludes "feature requests for
`query` output formatting" — a request to add a scope-reminder string to
an existing, accurate negative-result message is exactly that, not a
missing graph relationship. Filing it would misuse the queue (which is
reserved for edges the graph structurally cannot represent, not message
wording). No entry added to `planning/context-gaps/inbox.md`.

## Criterion 2 — exploratory tool-call counts (13 vs. 17)

Both logs independently re-counted from the verbatim reports (not taken
on their own summary numbers): baseline is genuinely 13 numbered calls,
treatment is genuinely 17.

**CodeCompass access increased total exploration here, not decreased
it.** Walking the treatment log: calls 2, 5, 6 (`query source` × 3) were
productive (confirmed the two-file/five-class shape with docstrings);
calls 3, 4 (`source-symbol to_dataframe`, `symbol DataFrame`) were dead
ends caused directly by the top-level-only boundary; call 8 bundles four
sub-calls (`symbol to_dataframe`, `symbol require_pandas`, `vendor
pandas`, `vendors`) of which three are negative/confirmatory-of-absence
rather than informative; call 9 (`--help`) is a self-diagnostic
triggered by the preceding dead ends; call 10 includes one failed
dotted-path attempt before the bare-name form succeeds. That is roughly
6–7 of the treatment's 17 calls spent discovering or working around
CodeCompass's own scope boundary — calls that have no baseline
counterpart at all, because the baseline agent never had a tool boundary
to discover in the first place. After that, the treatment agent still
had to run essentially the same direct-source sequence the baseline used
unaided (calls 7, 11–17: grep + full reads of `reports.py`, `models.py`,
`_pandas_compat.py`, `pyproject.toml`, `tests/test_dataframe.py`) to get
the method-level facts the task actually turns on. The baseline's own
targeted `grep -n "pandas\|DataFrame\|def \|^class "` (its calls 4 and
6) is a genuinely efficient one-shot technique that surfaces classes
*and* methods together in a single pass — arguably sharper than the
treatment agent's multi-step CodeCompass-then-grep sequence for this
specific task shape.

## Criterion 4 — first-pass correctness, hedging, backtracking

Neither agent's **substantive final conclusions** show a wrong
first-pass answer later corrected — both reports are internally
consistent from first claim to last, and both match ground truth. The
only "correction-shaped" moment in either log is mechanical, not
reasoning-related: the treatment agent's call 10 tries a dotted path
(`ledgerkit._pandas_compat.require_pandas`) against `query symbol` before
falling back to the bare name that the tool actually expects — a CLI
syntax/UX friction point, not a wrong belief about the codebase that had
to be walked back. Both agents independently and correctly flagged
`Journal.to_dataframe` as the one entry not strictly a "report result"
type, and both independently and correctly confirmed `JournalStats` has
no DataFrame export — convergent, not corrected-after-error.

## Criterion 5 — did the treatment arm do meaningfully less total work for equal-quality output?

No. Both arms reached identical, complete, correct final answers. The
treatment arm did **more** total tool calls (17 vs. 13), a meaningful
fraction of which were spent discovering or confirming a documented tool
boundary rather than making progress on the task, and it still had to
fall back to the same direct-read strategy the baseline used from the
start for every method-level fact the task's three questions actually
require (the pandas mechanism's exact lazy-import shape, the DataFrame
column lists, `Journal.to_dataframe`'s existence at all). The genuine,
real value CodeCompass added was narrow but real: `query source
reports.py`/`models.py` gave the treatment agent a fast, well-grounded
confirmation of "these are the right two files, these are the right
three/two classes, here are their one-line purposes" before it had to
grep for anything — a legitimate quick-orientation win. But that same
orientation is obtainable from one or two greps (`grep -n "^class "
reports.py models.py`, which the baseline effectively did, faster, in
fewer calls) — so per §5 of `context-quality-evaluation.md`, this
counts as **acceleration that a diligent baseline agent already
achieved by cheaper means**, not a case where CodeCompass surfaced
something the baseline couldn't plausibly have gotten to itself.

## Criteria assessment

| Criterion | Rating | Notes |
|---|---|---|
| Accuracy | strong | Every claim CodeCompass's output made (5 classes, docstrings, line numbers, file/language identity) is correct against the pinned source. It never asserted anything false. |
| Relevance | adequate | `query source`/`source-symbol` output was on-topic (the right files, the right classes) but structurally could not reach the task's actual decisive unit (the methods), so relevance tops out at file/class granularity for this task. |
| Completeness | weak | Missed the existence of all five `to_dataframe()` methods, the exact pandas lazy-import mechanism, and `Journal`'s own DataFrame support entirely — the three things the task specifically asked for. This is a documented scope limit, not a bug, but it is genuinely incomplete for *this task's* granularity. |
| Freshness | strong | `content hash`/line numbers matched the pinned commit exactly; no staleness observed. |
| Grounding / provenance | strong | Every symbol shown cites its own file/line; nothing was asserted without a traceable source location. |
| Noise | adequate | Docstrings are long (the `accounts`/`balance`/`register`/`stats` entries reproduce multi-paragraph internal docstrings) — informative but voluminous relative to what this task needed, and the four extra `vendor`/`vendors` probes in the treatment log (confirming pandas is untracked) added calls without adding decision-relevant signal. |
| Safety / trustworthiness | strong | Nothing was presented as authoritative that was wrong or misleading; the one negative-result message (`no source symbol named 'to_dataframe' found`) is honest about non-presence in the graph and does not claim non-existence in the source — a real minor UX-clarity gap (undisclosed scope inline) but not a trust violation. |

## Verdict: PASS WITH GAPS

No incorrect or misleading claim was found anywhere in CodeCompass's
output for this task — everything it asserted checked out exactly
against the independently-cloned, pinned source. The gap is
completeness, not correctness: for a task whose entire substance lives
at method granularity, a tool that is architecturally confined to
top-level symbols by design cannot supply the decisive facts, and both
dispatched agents correctly had to fall back to direct source reading
for every one of them. That gap is disclosed (by the plan, the `--help`
text, the docs, and the treatment agent's own honest report) rather than
hidden, which is what keeps this at PASS WITH GAPS rather than FAIL —
per this evaluation's own governing rule, incorrect/misleading content
would outrank incomplete content, but nothing here was incorrect.

## Context advantage: LOW

Could a competent fresh Claude session have obtained equivalent context
trivially through ordinary repository inspection? **Yes.** A single
`grep -n "pandas\|DataFrame\|def \|^class " ledgerkit/reports.py
ledgerkit/models.py` (exactly the baseline agent's own technique)
surfaces every class, every method, and every pandas usage site in one
pass, at lower tool-call cost than the treatment arm's CodeCompass-first
sequence — and unlike `codecompass query source-symbol`, it does not
stop at the class boundary. The treatment arm's CodeCompass queries
correctly confirmed which files/classes mattered, but that confirmation
was not hard to get any other way for a codebase this size (two files,
five classes), and the treatment arm still needed the same greps plus
full reads of `_pandas_compat.py`, `pyproject.toml`, and
`tests/test_dataframe.py` to answer the task at all. Net tool-call count
went up, not down, with several calls spent specifically discovering a
documented tool boundary the baseline never had to navigate. This is an
honest LOW-advantage result for this task shape, not a rounded-up
MODERATE — consistent with §5's own note that LOW is an expected,
non-failure outcome for a task whose decisive facts sit below the
tool's indexed granularity.

## Material gaps / failures

- `codecompass query source`/`source-symbol` cannot surface methods —
  confirmed independently, confirmed to be a documented Phase 77
  non-goal (not a defect), and confirmed to have real task-relevant
  cost here: on a DataFrame-export task where the entire feature is
  implemented as five methods, the tool's class-level output correctly
  named the right containers but supplied none of the decisive
  method-level facts, forcing a full grep/read fallback that consumed
  more tool calls than the baseline used from the start. No new
  `CG-NNN` filed for this — it is the documented top-level-only scope
  working as designed, and the queue's own README explicitly excludes
  the one narrower, real observation here (the negative-result message
  not inline-restating that scope) as a query-output-formatting request,
  not a missing-relationship gap.
- The treatment arm's net tool-call count (17) exceeded the baseline's
  (13) for an equal-quality outcome — a measurable efficiency cost, not
  merely a wash, that should inform how Phase 77's own "does first-party
  symbol awareness help" framing gets reported at any future
  aggregation (`context-quality-evaluation.md` §6): this task is a
  concrete data point that method-level opacity can make CodeCompass net
  more expensive to consult than to bypass, for exactly the class of
  task ("how does this concrete method work") that first-party symbol
  awareness was intended to help with.

## Would this have misled the implementing agent? no

Nothing CodeCompass produced was incorrect, and the one real limitation
(no method-level symbols) was accurately self-disclosed by the treatment
agent rather than silently masked — the final treatment report is exactly
as trustworthy as the baseline's, just arrived at via more total
exploration. An implementing agent relying on either report today would
be correctly informed.
