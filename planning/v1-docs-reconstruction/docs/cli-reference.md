# CLI reference

Every command below was captured by actually running `codecompass
--help` and `codecompass <command> [<subcommand>] --help` against this
checkout's installed console script (`pyproject.toml`'s
`[project.scripts] codecompass = "codecompass.cli:app"`), then
cross-checked against `src/codecompass/cli.py`. Nothing here is
reconstructed from memory of what the tool "should" do.

## Top-level

```
$ codecompass --help
Usage: codecompass [OPTIONS] COMMAND [ARGS]...

  Grounded, version-pinned dependency reference docs for AI coding agents.

Options:
  --yes                Skip Phase B's (AI enrichment) confirmation prompt.
  --budget <float>      Cap estimated Phase B enrichment spend (USD) for
                        this run; aborts before any API call if the
                        estimate exceeds it. Omit for no cap.
  --install-completion  Install completion for the current shell.
  --show-completion     Show completion for the current shell.
  --help                Show this message and exit.

Commands:
  init    Bulk-discover dependencies from named manifests, write vendor.toml.
  sync    Regenerate digests/trees for one or all vendors.
  index   Regenerate the CLAUDE.md routing table and tool-level Skill.
  check   Staleness gate + coverage-gap report.
  chat    Terminal REPL grounded in one vendor's digest.
  undo    Best-effort cleanup of everything codecompass generated.
  query   Query the context graph.
  enrich  Apply agent-authored enrichment to a mechanical edge.
```

Bare `codecompass` (no subcommand) is itself a command — see below.

## `codecompass` (no subcommand)

**Signature:** `codecompass [--yes] [--budget <float>]`

Runs the zero-question bootstrap (`cli.py`'s `main` → `_bootstrap`),
Phase A then Phase B — see [`quickstart.md`](quickstart.md) for the full
walkthrough of what each phase does and a real transcript. In short:

- **Phase A** (`_bootstrap`, always runs, never costs money): manifest
  auto-discovery, `vendor.toml` write/idempotent-extend, source cloning
  and digest generation for any *newly* discovered vendor only,
  `context-graph.db` rebuild.
- **Phase B** (`_maybe_run_enrichment`, conditional): if the graph
  rebuild finds usage-proven candidates with no current enrichment,
  discloses estimated cost and model, and proceeds on confirmation
  (`--yes` skips the prompt) or `--budget` permitting.
- `_refresh_generated_artifacts` always runs last (success or a
  budget-abort `typer.Exit`): re-rebuilds the graph, the root
  `CLAUDE.md` routing table, the tool-level Skill, and `/discovery`, so
  they reflect this run's actual outcome.

```bash
codecompass
codecompass --yes
codecompass --budget 1.00
```

## `codecompass init`

**Signature:** `codecompass init --scan <path> [--scan <path> ...] [--output <path>]`

```
Options:
  --scan <path>   Manifest file to scan; repeat for multiple. [required]
  --output <path> Where to write the generated vendor.toml. [default: vendor.toml]
```

The explicit, scripted/CI-friendly synonym for bare `codecompass`'s
auto-discovery (`decisions/0017`) — you name the manifests instead of
relying on root-level auto-detection. **Errors if `vendor.toml` already
exists** at the target path (`discovery.write_vendor_toml`) — unlike
bare `codecompass`, which idempotently extends an existing file. Free:
no cloning, no AI call — that only happens on `sync`/bare `codecompass`.

```bash
codecompass init --scan package.json --scan pyproject.toml --scan Cargo.toml
```

## `codecompass sync`

**Signature:** `codecompass sync [<vendor>] [--yes] [--budget <float>]`

```
Arguments:
  vendor <str>  Sync only this vendor; omit to sync all.
Options:
  --yes                 Skip Phase B's confirmation prompt.
  --budget <float>       Cap estimated AI spend (USD); no effect on
                         `sync <vendor>`, which never triggers Phase B.
```

Regenerates digests and trees for one vendor, or all of them.

- **Whole-project** (no vendor argument): regenerates every vendor's
  deterministic output, then rebuilds `context-graph.db` and runs the
  same Phase B trigger bare `codecompass` has (`decisions/0033`), then
  refreshes the routing table/tool Skill/`/discovery`.
- **Single-vendor** (`sync <name>`): regenerates only that vendor's
  `FILETREE.md`/`DEPTREE.md`/`CLAUDE.md` and re-clones its source.
  **No graph rebuild, no Phase B trigger** (`decisions/0025`) — errors
  with a red `error:` line and exit code 1 if `<name>` isn't in
  `vendor.toml`.

```bash
codecompass sync
codecompass sync anthropic
codecompass sync --yes
codecompass sync --budget 1.00
```

## `codecompass index`

**Signature:** `codecompass index` (no options besides `--help`)

Regenerates the routing table injected into the project's root
`CLAUDE.md` (between fixed marker comments,
`src/codecompass/index.py`'s `_MARKER_BLOCK_RE`) and the tool-level
Skill, from already-synced state — it does not re-run `sync` itself, so
it stays cheap. A vendor that's never been synced shows `_not synced_`
in its Version column rather than erroring. Idempotent.

```bash
codecompass index
```

## `codecompass check`

**Signature:** `codecompass check [--strict] [--fix]`

```
Options:
  --strict  Pure gate: exit non-zero on major/unclassifiable drift or a
            failed live version read. Never regenerates anything.
  --fix     Regenerate every stale vendor's digest in place (same logic
            as `sync`).
```

`--strict` and `--fix` are **mutually exclusive** — passing both errors
immediately (`error: --strict and --fix are mutually exclusive`, exit
1), before touching anything.

With no flags: always exits 0. Prints a `Vendor | Recorded | Live |
Severity | Notes` table (recorded version from the vendor's already-
synced `CLAUDE.md`; live version from a real, fresh adapter read) plus,
if `context-graph.db` exists, report-only coverage-gap sections:

- **Unused vendors** — tracked but never actually used in project
  source (`graph.unused_vendors`).
- **Documented but unused** / **Used but undocumented** — symbol-level
  mismatches between what's documented and what's actually referenced
  (`graph.documented_but_unused`/`used_but_undocumented`).
- **Third-party skill mentions with no backing vendor/symbol** — a
  hand-written or third-party Skill/`.mdc` file that mentions no known
  vendor or source file.
- **Spec docs with no detected relations** / **Vendor docs with no
  detected relations** (`graph.spec_docs_without_relations`/
  `vendor_docs_without_relations`).

None of these coverage-gap sections affect `--strict`'s exit code —
that's governed by version-drift severity alone (patch delta: silent;
minor: warns without failing; major, or an unparseable version on
either side: hard-fails).

If `context-graph.db` doesn't exist yet, the coverage-gap sections are
replaced by a one-line note (`no context-graph.db yet — run
codecompass sync first`) rather than an error.

```bash
codecompass check
codecompass check --strict
codecompass check --fix
```

## `codecompass chat`

**Signature:** `codecompass chat <vendor>` (argument required)

Terminal REPL grounded in one vendor's **already-generated** digest
(`vendor/<name>/CLAUDE.md`, plus `OVERVIEW.md` if enriched) — it never
calls `sync` itself (`decisions/0023`), so starting a chat never
re-clones or regenerates anything. Errors (exit 1) if `<vendor>` isn't
in `vendor.toml`. Works before enrichment too, with thinner grounding
plus a hint to run `sync`.

```bash
codecompass chat anthropic
```

## `codecompass undo`

**Signature:** `codecompass undo [--yes] [--dry-run]`

```
Options:
  --yes       Skip the confirmation prompt.
  --dry-run   Print what would be removed, without deleting anything.
```

Best-effort cleanup (`decisions/0036`) of everything codecompass
generated: every tracked vendor's `vendor/<name>/` directory,
`vendor.toml`, `context-graph.db`, every codecompass-generated
Skill/`.mdc`/slash-command artifact, and the root `CLAUDE.md`
routing-table marker block (stripped in place; surrounding hand-written
content is untouched). Never removes a hand-written or third-party
Skill/`.mdc` file, and **never runs a git command** — committing the
result is left to you.

Two enumeration strategies (`cli.py`'s `_codecompass_generated_paths`):
if `context-graph.db` exists, a precise graph-backed enumeration (every
`doc_artifacts` row tagged `codecompass_tool`/`codecompass_vendor`,
never `third_party`); otherwise a pattern-based fallback matching
`skill.py`/`commands.py`'s exact generated-name conventions.

```bash
codecompass undo --dry-run
codecompass undo
codecompass undo --yes
```

## `codecompass query`

A `query` subcommand group over `context-graph.db`. Every subcommand
supports `--json` for raw JSON instead of a Rich table, and prints a
one-line `no context-graph.db yet — run codecompass sync first` note
(rather than erroring) if the database doesn't exist.

### `query vendors`

**Signature:** `codecompass query vendors [--unused] [--json]`

Every tracked vendor's ecosystem, installed version, usage status
(`used: yes/no`, from real detected source usage), and enrichment
status. `--unused` filters to vendors with zero detected usage anywhere.

```bash
codecompass query vendors
codecompass query vendors --unused --json
```

### `query vendor`

**Signature:** `codecompass query vendor <name> [--json]`

One vendor's full profile: symbols (name, purpose, export kind, note),
usage count, real `(file, line)` usage sites, documenting artifacts,
routed Skills, and `depends_on` vendors. Errors (`error: 'x' not found
in context-graph.db`, exit 1) if `<name>` isn't a known vendor in the
graph.

```bash
codecompass query vendor anthropic
codecompass query vendor anthropic --json
```

### `query symbol`

**Signature:** `codecompass query symbol <name> [--json]`

Every symbol named `<name>`, across **every** vendor — symbol names
aren't globally unique. Each row: vendor, purpose, usage count,
documenting artifacts, used-at locations. Prints a plain notice (not an
error) if nothing matches.

```bash
codecompass query symbol Anthropic
```

### `query skills`

**Signature:** `codecompass query skills [--unused-mentions] [--json]`

Every agent-context artifact under the project — Skills
(`.claude/skills/**`), Cursor `.mdc` rules (`.cursor/rules/`), and the
`/discovery` slash command — with its kind, origin, and what it
mechanically mentions. `--unused-mentions` filters to artifacts
mentioning no known vendor or source file.

```bash
codecompass query skills
codecompass query skills --unused-mentions
```

### `query relations`

**Signature:** `codecompass query relations <name> [--json]`

Accepts three shapes for `<name>` (`cli.py`'s `_resolve_relations`,
tried in order): a spec-doc path (its outgoing mechanical mentions), a
vendor name, or another doc artifact's `name` field (a Skill's
frontmatter name, a dependency doc's own name) — the latter two are
reverse lookups: which spec docs mechanically mention it. Each relation
row shows a `relation_label` (once AI-enriched: `documents_
configuration_of`, `explains_usage_of`, `contrasts_with`, `supersedes`,
or `other`) and an `ai_summary` (or `"mentioned, not yet enriched"`).
Also prints a "Package code" trace — real project-source usage sites for
whatever `<name>` mentions/documents/is. `--json` output is
`{"relations": [...], "package_code": [...]}` — two different shapes,
never merged into one list.

If `<name>` matches nothing at all, but is a real file on disk that
simply wasn't detected as a spec/vendor doc, the error names that
specifically (spec-doc glob coverage), rather than reading as plain
non-existence (`cli.py`'s `_relations_not_found_error`).

```bash
codecompass query relations architecture/overview.md
codecompass query relations anthropic
```

## `codecompass enrich apply`

**Signature:** `codecompass enrich apply <entries_file> --agent <name>`

```
Arguments:
  entries_file <path>  JSON file: a list of {source_doc_path,
                       target_vendor_name?, target_doc_path?,
                       ai_summary, relation_label} objects. [required]
Options:
  --agent <str>  Name of the agent supplying this enrichment. Recorded
                 as model=f'agent:{agent}'. [required]
```

**Agent/developer-facing** — not a command you'd run by hand day to
day. Writes agent-authored enrichment for `doc_relations_edges` rows
(`decisions/0054`), the second, non-automated producer alongside
`sync`'s own batched Anthropic-API path. **Mechanically enforced trust
boundary**: an entry is only accepted if it matches a row
`relation_enrichment.select_candidates` currently lists as pending — a
real, mechanically-detected edge that's new or changed since its last
enrichment. Rejects (with a per-entry reason, printed) anything that
doesn't match, has an invalid `relation_label` (must be one of
`graph.RELATION_LABELS`), or is missing `ai_summary`. Exits non-zero if
anything was rejected, even if some entries were accepted.

```bash
codecompass enrich apply entries.json --agent context-enrichment-agent
```

## `/discovery` — not a `codecompass` CLI command

`/discovery` is a generated **Claude Code slash command**
(`.claude/commands/discovery.md`), typed inside a Claude Code session,
not a shell. There is no `codecompass discovery` — running that at a
shell prompt errors like any unrecognized subcommand. It's generated
(free, no AI cost) by the same trigger points as the tool-level Skill:
bare `codecompass` and `codecompass index`. It's read-only by
construction (`allowed-tools` frontmatter grants only
`Read`/`Grep`/`Glob`/`Bash(codecompass query:*)`/`Bash(codecompass
check:*)`/`Bash(sqlite3 context-graph.db:*)` — no `Write`/`Edit`) and its
body repeats, in plain instructional text, that answering a question
that would require a code/config change means stopping and saying so,
not making the change.

```
# typed inside a Claude Code session, not a shell:
/discovery
```
