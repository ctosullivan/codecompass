# MCP server (Phase 88)

`codecompass mcp-serve` exposes one CodeCompass-indexed project's
knowledge, provenance, contextual retrieval, change-impact analysis,
documentation grounding, and (opt-in) controlled verification to a real
coding agent — Claude Code, or any other MCP-capable client — over the
standard [Model Context Protocol](https://modelcontextprotocol.io) stdio
transport.

This is a thin, read-mostly layer: every tool delegates to CodeCompass's
already-shipped `knowledge_api` (Phase 84), `oracle` (Phase 82), and
`change_impact` (Phase 83) modules. No new knowledge store, impact
engine, or verification framework is introduced here.

## Starting the server

```
codecompass mcp-serve [--repo-root KEY=PATH ...] [--project-root PATH] [--enable-execution]
```

- `--project-root PATH` — the CodeCompass-indexed project whose own
  knowledge this server exposes. Defaults to the current working
  directory.
- `--repo-root KEY=PATH` — repeatable. Pins a symbolic key to a real
  target-repository path. A connected agent selects *which* pinned key
  to consult (e.g. `"ledgerkit"`) via a tool's own `repo_root_key`
  parameter — it can never supply a raw filesystem path itself. Omit
  entirely if no tool needs to consult a live target checkout.
- `--enable-execution` — turns on `oracle_execute_check` (Stage 88B).
  Off by default. See **Trust model and limitations** below before
  enabling it.

Configuring a client (e.g. Claude Code) to connect over stdio typically
looks like:

```json
{
  "mcpServers": {
    "codecompass": {
      "command": "codecompass",
      "args": [
        "mcp-serve",
        "--project-root", "/path/to/this/project",
        "--repo-root", "ledgerkit=/path/to/ledgerkit"
      ]
    }
  }
}
```

Call `server_capabilities` first in any session — it reports which
`repo_root_key` values are actually configured and whether execution
mode is enabled, so a client never has to "try it and see."

## Tools

| Tool | Purpose |
|---|---|
| `knowledge_get` | Retrieve one Requirement/Claim/Decision/Evidence/Observation/Derivation record, or one natural-key record (`symbol:`/`vendor:`/`doc:`/`contract:`/`check:`/`result:`), by id. |
| `knowledge_search` | Bounded substring search across the knowledge corpus. |
| `knowledge_traverse` | One-hop (or `depth`-hop) relation traversal — also how an agent discovers applicable contracts/checks/results (`relation="checks"`/`"results"`). |
| `knowledge_trace_evidence` | Provenance, supporting/contradicting evidence, and dangling-citation gaps for one record. |
| `knowledge_epistemic_status` | Verification currency for one record: intended/observed/contested, plus verified/known-gap/unconfirmed scopes. |
| `knowledge_context_packet` | A bounded, deterministic, task-specific development-context packet for a topic. |
| `knowledge_find_gaps` | Corpus-wide (or slug-scoped) report of missing, stale, conflicting, or unverified knowledge. |
| `docs_get_grounded_region` | A published documentation region and its current grounding (cited Claim ids plus each one's live status). |
| `server_capabilities` | Discover configured `repo_root_key` values and whether execution mode is enabled. Call this first. |
| `impact_classify_change` | Assess a proposed source change's relationship to existing knowledge/evidence — read-only classification, no check execution. |
| `oracle_list_checks` | Surface the real, on-disk check allowlist for a slug — what `oracle_execute_check` will actually accept, and each check's latest aggregate status. |
| `oracle_execute_check` | The one controlled-verification execute operation. Disabled unless the server was started with `--enable-execution`. |

Every tool response except `server_capabilities` (which has no
repository state to describe) carries `project_revision` (this
project's own current git HEAD) and, when a `repo_root_key` was
consulted, `target_revision` (that target repository's current git
HEAD) — so a caller can tell exactly which state a response describes.
Every knowledge-record result also carries its own `consistency` envelope
(`current`/`stale`/`unconfirmed`) — a historical fact is never presented
as freshly reconfirmed when it wasn't.

## Validation and confinement

- `repo_root_key` is always a symbolic key resolved against the fixed
  `--repo-root` mapping given at startup. An unconfigured key is a
  structured tool error, never silently ignored or treated as "no
  target."
- `slug` (on `knowledge_find_gaps`) is validated against this server's
  own real, enumerated slug list before it reaches any delegate — an
  unrecognised or traversal-shaped value is rejected outright.
- `doc_path` (on `docs_get_grounded_region`) is confined to this
  project's own schema-governed document set, re-derived from the real
  `**/*.schema.yaml` files at server startup (never a hardcoded guess) —
  a path outside this set is rejected, never read.
- `relation` (on `knowledge_traverse`) must be one of the fixed,
  recognised relation names — an unrecognised value is a validation
  error, never silently treated as "no relation."
- An already-indexed source file, oracle result, or slug directory that
  has since been replaced by a symlink pointing outside the intended
  root is never followed: every live read confines and atomically
  opens its target (`O_NOFOLLOW`, `dir_fd`-relative where a whole
  directory's contents are read), reporting the existing
  `unconfirmed`/empty-result outcome rather than leaking content from
  outside the root. See `decisions/0095` for the full security design
  history.
- `changed[].path` (on `impact_classify_change`) is rejected — before
  any assessment runs, naming every offending path — if it is absolute,
  contains a `..` component, or resolves (following symlinks) outside
  the pinned target repository.
- `oracle_execute_check` accepts only `(slug, contract_id, check_id)`;
  the server resolves these against the real, on-disk `oracle-
  contract.yaml` — a tuple that doesn't match the real contract/check
  is rejected before any subprocess is considered. `repo_root_key` is
  resolved the same way every other tool resolves it; the actual
  subprocess is bounded by a timeout and a total-output cap, with a
  process-group-wide kill (not only the direct `pytest` child) on
  either breach.

## Trust model and limitations

- This server treats every tool **input** as untrusted (validated,
  never interpolated into a path or command without confinement) and
  every repository/document/oracle-output **byte it returns** as
  untrusted *data* — it never re-parses its own responses for embedded
  instructions, and a client should treat returned content the same
  way.
- Read-only tools have zero side effects. The one exception is
  `oracle_execute_check`: it runs a real `pytest` subprocess and writes
  one new, append-only result file. Enabling `--enable-execution`
  grants the connected MCP client the ability to execute real code
  from a pinned target checkout under this server process's own OS
  privileges — equivalent to letting that client run `pytest` on this
  machine directly. **No sandbox, container, or restricted user is
  implemented.** Allowlisting bounds *which* check runs, never what
  that check's own code does.
- This server implements no authentication and is designed for exactly
  one local operator running it for one connected client over stdio —
  never a shared, multi-tenant, or network-exposed service.
- Phase 88 is planning-and-implementation only for the surface named
  above; a full sandbox is named future work, not built now.
