# Coding-context packet: add `codecompass query source-stats`

A packet assembled from `codecompass-overview@v1` (the frozen Phase 80
project-wide snapshot) and its Stage 2/3 companion evidence, for one
specific, bounded coding task — not a topic overview of `cli.py`/`graph.py`.

## The task

Add a new CLI command, `codecompass query source-stats`, that prints how
many first-party source files are currently indexed, broken down by
`symbol_index_status` (`indexed`/`indexed_partial`/`unsupported`/
`parse_error`/`unreadable`), with a `--json` flag matching the existing
`query` subcommands' own convention.

## Evidence cited, and why each piece

- **`codecompass-overview@v1#CL-CTXT-006`** (git-topology vs. content-
  graph distinction) — not directly relevant to this task's own
  mechanics, but establishes that `source_files` is one of the four
  "content entities" (`vendors`/`symbols`/`source_files`/
  `doc_artifacts`) a `query` subcommand traverses, confirming this new
  command fits the established `query` family rather than needing a
  new top-level verb.
- **Stage 2 model-blind reconstruction, §2 (CLI surface)** — the
  existing `query source PATH`/`query source-symbol NAME` commands are
  the direct precedent: both are `@query_app.command()` functions, both
  accept `--json`, both use the graph's own open-or-note pattern.
- **Stage 2 reconstruction, §3 (graph schema)** — `source_files` table:
  `path UNIQUE`; `symbol_index_status` nullable, `CHECK IN indexed/
  indexed_partial/unsupported/parse_error/unreadable`. This is the exact
  column to group by.
- **Stage 2 reconstruction, §7 (extension points: new CLI command)** —
  "add an `@app.command()` (or `@query_app.command()`/
  `@enrich_app.command()`) function in `cli.py`, following the existing
  pattern of a plain function with Typer-annotated parameters, printing
  via the shared `rich.Console` instance, and raising `typer.Exit(code=1)`
  on failure rather than letting exceptions propagate. Commands needing
  the graph should use the existing `_graph_session`/`_open_graph_or_note`
  context-manager pattern rather than opening `sqlite3.connect` directly,
  to get the established 'graceful note, no traceback, no silent
  empty-DB creation' behavior for free."

## What was deliberately left out

- The full `graph.py` schema beyond `source_files` — not needed for a
  read-only aggregate query over one table.
- `sync.py`'s own rebuild pipeline — this task only reads the graph, it
  never writes to it.
- The adapter pattern and `config.py` — unrelated to this task.

## What the packet establishes

### The pattern to follow, precisely

Every existing `query` subcommand (`vendors`, `vendor`, `symbol`,
`skills`, `relations`, `topology`, `source`, `source-symbol`) is a
`@query_app.command("<name>")`-decorated function in `cli.py`, taking a
`--json: bool = False` option (and whatever positional/named arguments
the query needs), opening the graph via `_graph_session`/
`_open_graph_or_note` (never raw `sqlite3.connect`), and rendering
either a `rich.Table` (human-readable) or `json.dumps(...)` (machine-
readable) depending on the flag.

### The new command's shape

```python
@query_app.command("source-stats")
def query_source_stats(json_output: bool = typer.Option(False, "--json")) -> None:
    with _graph_session(Path.cwd()) as conn:
        if conn is None:
            return
        # aggregate: SELECT symbol_index_status, COUNT(*) FROM source_files
        # GROUP BY symbol_index_status
        ...
```

A `NULL` `symbol_index_status` (a source file discovered but never
actually indexed — distinct from the project never having run topology/
symbol indexing at all, which `meta.source_index_version`'s absence
already distinguishes per the reconstruction's own `graph.py` §3
findings) should be rendered as its own explicit bucket (e.g.
`"not_yet_indexed"`), not silently dropped from the count or folded into
one of the five named statuses — consistent with this project's own
established "never collapse a real null state into false certainty"
pattern (the same discipline `query topology`'s own three-state
rendering already follows, per the reconstruction's §2 entry for that
command).

### Test coverage expected

Following the existing `query`-command test pattern (check
`tests/test_cli.py` for the sibling commands' own test shape before
writing new ones): a test with a populated `context-graph.db` containing
source files across multiple `symbol_index_status` values (including at
least one `NULL`), asserting both the human-readable table output and
the `--json` output group counts correctly; a test with no
`context-graph.db` at all, asserting the graceful one-line note (not a
traceback); a test with a `context-graph.db` present but zero
`source_files` rows, asserting a clean "nothing indexed yet" output
rather than an empty/malformed table.

## Independent assessment

Not yet performed — this packet is a draft until an evaluator who
inspects `src/codecompass/cli.py`/`graph.py`/`tests/test_cli.py`
directly rates whether it gave a genuine advantage over cold-reading the
code (LOW/MODERATE/HIGH), per this project's own
`planning/v1-redefinition/context-quality-evaluation.md` rubric.
