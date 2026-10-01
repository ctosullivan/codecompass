# CLI reference

**Provenance tier: CONFIRMED-BY-READING, not CONFIRMED-LIVE.** Source:
`phase80-implementation-reconstruction.md` §2. The Stage 2 reconstruction
could not execute `codecompass --help`, `codecompass --help` on any
subcommand, or `cli.py` at all in its sandbox — the bounded export it
worked from was missing transitive dependencies (`enrichment`,
`relation_enrichment`, `chat`, `index`, `skill`, `source_resolution`,
`staleness`, `filetree`, `symbols`, and others), so `import codecompass.cli`
itself fails with `ImportError`. Everything below was read directly from
`cli.py`'s real Typer decorators, function signatures, and docstrings —
a careful read, not a run. **If a command's exact flag spelling or exit
code matters for your use case, confirm it by actually running
`codecompass <command> --help` yourself** rather than trusting this page
alone; that is a strictly stronger source than this reconstruction.

CodeCompass is built as a `typer.Typer` application (`app`) with two
nested sub-apps, `query` and `enrich`.

## Bare `codecompass`

Invoked with no subcommand. Options: `--yes` (boolean), `--budget`
(float, optional). Runs an auto-bootstrap sequence: discover manifests in
the project root → write or append `vendor.toml` → sync only the
newly-discovered vendors → rebuild the project graph → conditionally run
AI enrichment (cost-gated, confirmable; calls into `enrichment`/
`relation_enrichment`, both **out of scope for this draft** — see
`08-limitations-and-provenance.md`) → always refresh generated artifacts
(the `CLAUDE.md` routing table, Skill, discovery command), even if the
enrichment step was aborted.

## `init`

Explicit, scriptable/CI equivalent of auto-discovery. `--scan PATH`
(repeatable, required); `--output`/`vendor_toml PATH` (default
`vendor.toml`). Errors if `vendor.toml` already exists — it will not
silently overwrite one.

## `sync [VENDOR]`

- No vendor name: whole-project sync. Rebuilds the graph; may trigger
  enrichment.
- A vendor name: single-vendor sync only. Never touches the graph and
  never triggers enrichment — an explicit design choice stated in the
  code's own comments, not independently verifiable from this evidence
  base beyond that it is what the code itself says.

Options: `--yes`, `--budget`.

## `index`

No arguments. Regenerates the `CLAUDE.md` routing table, the tool Skill,
and the discovery command from the current `vendor.toml` state. Calls
into `codecompass.index`/`codecompass.skill` — **both out of scope for
this draft**; their regeneration logic is not independently verified
here.

## `check`

`--strict`, `--fix` (mutually exclusive). Prints a staleness table plus
report-only coverage-gap sections (unused vendors; documented-but-unused
or used-but-undocumented symbols; orphaned skill mentions; spec/vendor
docs with no relations) if `context-graph.db` exists. With no flags, this
command always exits 0.

## `query vendors`

`--unused`, `--json`. Lists `vendors` table rows, joined against
graph-computed "unused" and "has enrichment" status.

## `query vendor NAME`

`--json`. Full profile for one tracked vendor.

## `query symbol NAME`

`--json`. Profile for a symbol by name. **Symbol names are not globally
unique across vendors** — this command's own behavior depends on that
fact, so a name may resolve ambiguously if more than one vendor exports
it.

## `query skills`

`--unused-mentions`, `--json`. Lists generated Skills and flags mentions
that no longer resolve to anything real.

## `query relations NAME`

`--json`. Resolves `NAME` in order: a spec-doc path, then a vendor name,
then any other documented artifact name. Also shows a "package code"
trace.

## `query topology`

`--json`. Reports git-repository/worktree/submodule topology. Three
distinct "not indexed" states are rendered honestly rather than
collapsed into one: no graph database at all; a graph database that has
never been topology-synced; and a genuinely indexed, populated result.

## `query source PATH`

`--json`. Profile for one first-party source file. Gated on a
source-index version marker being present in the graph; never triggers a
rebuild itself.

## `query source-symbol NAME`

`--json`. Profile for a first-party (non-vendor) source symbol.

## `chat VENDOR`

Calls into `codecompass.chat` (**out of scope for this draft** beyond
this bare signature — its actual conversational behavior is not
independently verified here). What is confirmed by reading the call
site: it is grounded only in already-generated `vendor/<name>/CLAUDE.md`/
`OVERVIEW.md` content and never regenerates anything itself.

## `undo`

`--yes`, `--dry-run`. Best-effort removal of everything CodeCompass
itself generated: tracked `vendor/<name>/` directories, `vendor.toml`,
`context-graph.db`, and every doc-artifact row tagged as tool- or
vendor-generated (never a row tagged third-party). Falls back to a
pattern-based filesystem scan (generated Skills, Cursor rules, the
discovery slash command) if no graph exists yet to query. Strips —
never deletes — a marker-delimited routing-table block from the root
`CLAUDE.md`, leaving hand-written content around it untouched. Never
invokes `git`.

## `enrich apply ENTRIES_FILE --agent NAME`

Reads a JSON list of enrichment entry objects and writes them as
agent-authored (non-API) enrichment — but **only** for entries that
exactly match a currently-pending candidate from a candidate-selection
mechanism (`relation_enrichment.select_candidates`, **out of scope for
this draft**). This matching is a real mechanical trust boundary, not
merely an instruction to the caller: an entry that does not match a
pending candidate, or that would re-enrich an edge that hasn't actually
changed, is rejected and reported, and the whole command exits non-zero
if anything was rejected. See `07-agent-orientation.md` for why this
matters to an agent calling this command.

## Removed: `promote`

A former `promote` command has been removed; invoking it now produces
Typer's standard "no such command" error. (Confirmed by a dedicated,
passing test in the reconstruction's evidence base — this is the one
piece of CLI-surface information in this file that is CONFIRMED-LIVE,
via the test runner, rather than read-only, since the test itself
executed successfully even though `cli.py` as a whole could not be
imported for live `--help` output.)

## A consistent pattern across graph-dependent commands

**CORRECTED 2026-10-02** (found by an independent `context-evaluator`
assessment downstream of this draft — see
`_part4-coding-context-packet-evaluation.md`): every `query`/`enrich`
subcommand that needs the graph does, uniformly, return cleanly with a
one-line note rather than crashing or silently creating an empty
database when `context-graph.db` doesn't exist — that much is accurate.
What this draft originally got wrong is claiming that's all *one*
pattern/helper pair: `query topology`/`query source`/`query
source-symbol` actually use a distinct helper (`_open_graph_if_exists`)
with an additional gate on whether that specific thing has ever been
indexed, printing their own specific "not yet indexed" message rather
than the shared generic note. See `07-agent-orientation.md` for why the
*outcome* (clean, no traceback) is worth relying on either way if you
are an agent calling these commands programmatically — but do not assume
all graph-reading commands share one literal code path.
