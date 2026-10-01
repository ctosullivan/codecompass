# Extending CodeCompass: how-to guides for contributors

**Provenance tier: CONFIRMED-BY-READING, grounded in CONFIRMED-LIVE
precedent.** Source: `phase80-implementation-reconstruction.md` §7. Each
recipe below is concrete and actionable, naming real files and real
tests as precedent — but, like the rest of the code these recipes touch,
could not be exercised end-to-end in the Stage 2 sandbox (see
`05-runtime-pipelines.md`). Where a recipe references `PythonAdapter` or
`graph.py`, that reference point is itself CONFIRMED-LIVE (its tests
ran).

## Add a new ecosystem adapter

1. Subclass `EcosystemAdapter` (`adapters/base.py`).
2. Implement the five abstract methods: `installed_version`,
   `source_location`, `readme_and_api_surface`, `repository_url`,
   `dependency_tree`. `PythonAdapter` is the concrete, working reference
   implementation for this interface, and its tests are
   CONFIRMED-LIVE — read it first.
3. Optionally override the sixth method, `symbols()` — it is concrete,
   not abstract, with a default implementation that walks the adapter's
   `source_location()` and dispatches each file to a symbol extractor.
   The code's own comments cite a hypothetical "external-process"
   adapter (a language with no in-process extractor available) as the
   reason this one method is concrete rather than abstract — override it
   only if the default walk-and-extract approach genuinely doesn't apply
   to your ecosystem.
4. Register the new class in `adapters/__init__.py`'s dispatch dict,
   keyed by the `Ecosystem` enum member it serves.
5. Add the new value to `core.py`'s `Ecosystem` enum.
6. Widen `graph.py`'s `vendors.ecosystem` CHECK constraint to accept the
   new value, with an accompanying migration function following the
   existing pattern (`_migrate_vendors_ecosystem_constraint`, the
   precedent for widening this exact constraint) — see
   `04-architecture-persistence.md`'s "Migrations" section for why this
   must be introspection-gated, not a version-bump check.

Note that the abstractness of the five required methods is genuinely
enforced, not just documented convention: a dedicated, passing test
instantiates a deliberately incomplete subclass and confirms Python's
own `ABC`/`TypeError` machinery rejects it. If you forget one of the
five methods, you will get a real `TypeError` at class-instantiation
time, not a silent partial adapter.

## Add a new CLI command

1. Add an `@app.command()` function (or `@query_app.command()`/
   `@enrich_app.command()` for a subcommand) in `cli.py`.
2. Follow the existing pattern: a plain function with Typer-annotated
   parameters, printing via the project's shared `rich.Console`
   instance, raising `typer.Exit(code=1)` on failure rather than letting
   exceptions propagate uncaught.
3. If the command needs ordinary graph access, use the existing
   `_graph_session`/`_open_graph_or_note` context-manager pattern rather
   than opening a raw `sqlite3.connect` call directly. This gets you the
   established "graceful note, no traceback, no silent empty-database
   creation" behavior for free — see `07-agent-orientation.md` for why
   this specific guarantee matters to a caller. **Correction, 2026-10-02:**
   if your command also needs to distinguish "database exists but this
   specific thing was never indexed" (as `query topology`/`query
   source`/`query source-symbol` do), use `_open_graph_if_exists`
   (`cli.py:895-912`) instead — a related but distinct helper this
   draft originally conflated with the one above; found by an
   independent `context-evaluator` assessment of a packet built from
   this draft (`_part4-coding-context-packet-evaluation.md`).

## Add a new graph row or table

1. Add a dataclass row type in `graph.py`, next to the existing ones.
2. Add a `CREATE TABLE IF NOT EXISTS` clause to `_SCHEMA_SQL`.
3. Add an insertion/sync helper function: an `_insert_*`-style function
   for a clear-and-reinsert-every-sync table, or a `_sync_*`-style
   function for a table upserted by natural key — see
   `04-architecture-persistence.md` for which existing tables use which
   pattern.
4. Wire the new table into `rebuild_deterministic`'s own signature and
   body.
5. If the new table must survive a rebuild the way `vendor_enrichment`
   does, key it by a plain natural-key TEXT column, **not** a foreign
   key to a table that gets wiped — follow `doc_relation_enrichment`'s
   own documented precedent for this exact concern.

## Add a new manifest-based discovery source

Add a `discover_<ecosystem>(manifest: Path) -> list[str]` function in
`discovery.py`, and register both the function and its manifest filename
in the existing manifest-handler registry. See `03-configuration.md` for
the two currently-known, docstring-documented limitations of the
existing discoverers (optional Python dependencies not scanned; hpack
conditional Haskell dependencies not expanded) as a reminder that a new
discoverer's own limitations should be stated in its own docstring the
same way, not left implicit.
