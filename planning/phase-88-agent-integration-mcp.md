# Phase 88: Agent Integration and MCP — plan

## 0. Status

**Planned and independently reviewed: READY WITH NON-BLOCKING
OBSERVATIONS** (§15 — four blocking findings from the review, all
fixed in this same session). Planning-only task ("CodeCompass
Orchestrator — Phase 88 Planning"). **Implementation is explicitly
still unauthorised** — a READY verdict satisfies this task's own §11
gate, not a separate, affirmative decision to implement, per this
phase's own precedent (every phase from 83 onward split planning and
implementation authorisation, several across separate sessions).

## 1. Verified current state (re-confirmed this session, not assumed)

- `HEAD` at planning time: see git log; `main` clean, `origin/main` in
  sync. **Phase 87 is `done`** (`planning/retros/_audit-phase-87.md`,
  re-audit **PASS WITH NON-BLOCKING OBSERVATIONS**) — re-confirmed
  directly against `planning/ROADMAP.md`/`planning/CONTEXT.md`, not
  assumed from this plan's own governing prompt.
- `decisions/0084`/`0085` govern this phase's existence and boundary:
  the old merged "Agent Integration, MCP, and Incremental Knowledge/
  Documentation Reconciliation" Phase 88 was split (`decisions/0085`
  §3) into **Phase 88 — Agent Integration and MCP** (this plan) and
  **Phase 89 — Incremental Knowledge and Documentation Reconciliation**
  (a separate, independently deliverable phase, not a prerequisite of
  this one or vice versa). `planning/v2-roadmap.md` §88 (lines
  592-645) is the authoritative roadmap-depth scope statement; this
  plan operationalises it, corrects nothing in it.
- No MCP code exists anywhere in the repository (`grep -r mcp
  src/codecompass/` returns nothing); no `mcp`-family dependency is
  declared in `pyproject.toml`; no `vendor/mcp/` digest exists. The one
  prior MCP mention is the long-deferred, now-superseded "Phase 25 —
  MCP server (`query_vendor`)" backlog item (`pre-v1-disposition.md`
  §4, deferred pending "real post-v1 CLI/Skill usage patterns" — this
  phase supersedes that item's own revisit trigger with a different,
  v2-era design; the old item is not reopened or implemented as such).
- `pyproject.toml`: `requires-python = ">=3.11"`, `license =
  "GPL-3.0-or-later"`, runtime deps `typer>=0.27`, `rich>=15`,
  `anthropic>=0.109`, `pipdeptree>=4.2`, `pyyaml>=6.0`. No `tomli`
  (stdlib `tomllib`, `decisions/0009`).

### 1.1 Source-verified capability inventory (independent fork research,
this session — exact names/signatures confirmed by direct source
reading, not assumed from the governing prompt's own descriptions)

**`src/codecompass/knowledge_api.py`** (Phase 84, packaged under `src/`,
read-only — opens `context-graph.db` via `file:...?mode=ro`, never
`graph.open_graph`):

| Function | Signature (abridged) | Purpose |
|---|---|---|
| `get` | `(project_root, record_id, *, repo_root=None) -> ApiResponse` | Any canonical id (`REQ-/CL-/EV-/OBS-/DE-/DEC-`) or natural-key string (`symbol:/vendor:/doc:/contract:/check:/result:`) |
| `search` | `(project_root, text, kinds=None) -> ApiResponse` | Bounded substring match |
| `traverse` | `(project_root, record_id, relation, depth=1, *, repo_root=None) -> ApiResponse` | `depends_on`/`supporting_evidence`/`contradicting_evidence`/`observations`/`decision` (+`_reverse`), `cites`/`cited_by`/`checks`/`results`/`doc_mentions` |
| `trace_evidence` | `(project_root, record_id, *, repo_root=None) -> ApiResponse` | `missing_evidence`/`dangling_evidence_reference`/`dangling_dependency_reference` gaps; Requirement evidence resolved one `depends_on` hop (`decisions/0093`) |
| `epistemic_status` | `(project_root, record_id, *, repo_root=None) -> ApiResponse` | Wraps `knowledge_intermediate.derive_epistemic_profile`: `intended`/`observed`/`contested` + `verified_scopes`/`known_gap_scopes`/`unconfirmed_scopes` |
| `find_gaps` | `(project_root, slug=None, *, repo_root=None) -> ApiResponse` | Corpus-wide gap report |
| `get_context_packet` | `(project_root, topic, *, max_items=20, max_chars=6000, repo_root=None) -> ApiResponse` | Fixed priority order, deterministic truncation, `details.bounds.truncated` |
| `export_snapshot` | `(project_root, slug, out_path, *, project_id="codecompass") -> ApiResponse` | **The one write side effect** — refuses any path under `planning/knowledge/`/`planning/contracts/`. Not exposed via MCP (§3.5). |

`ApiResponse{status: result|empty|gap, results, gaps, message}`;
`KnowledgeResult{id, kind, authority, summary, details, consistency}`.
Authority tags: `primary_evidence`/`derived_index`/`stated_intent`/
`accepted_obligation`/`scoped_verification`/`editable_projection`/
`presentation_artifact`. `ConsistencyEnvelope.status` ∈
`{"current", "stale", "unconfirmed"}` (default `"unconfirmed"`,
fail-closed by construction, `decisions/0092`) — **there is no
`"historical"` `ConsistencyEnvelope` value**; that word names a
*different*, `derive_provenance_label` classification elsewhere. The
`knowledge` CLI sub-commands (`cli.py:1747-1876`) are exact 1:1 thin
wrappers over these eight functions — confirms the API surface is
already the real, exercised contract, not a parallel path.

**`src/codecompass/oracle.py`** (Phase 82, packaged, 826 lines):
`OracleContract`/`OracleCheck`/`OracleResult` schema; `evaluate_result_
precedence`/`aggregate_contract` — **`CheckAggregate.state` is only
ever `PASS`/`GAP`/`NOT_REQUIRED`; there is no aggregate `FAIL`** (a
`FAIL` only ever appears as a per-result/fresh-evaluation outcome).
`evaluate_check(contract, check, *, contract_path, repo_root,
raw_output_dir, baseline_id=None, environment_descriptor=None) ->
OracleResult` is the controlled-execution primitive: runs real `pytest`
against `check.check_reference` and `repo_root` via `run_pytest_check`
(pins the target repo's own interpreter/`PYTHONPATH`, classifies from
junit-xml, rejects all-skipped as `INVALID`, catches launch `OSError`
as `INVALID`). It does **not** persist its result — the caller must
separately call `write_oracle_result`. **Verified this session: `run_
pytest_check`'s `subprocess.run` call (`oracle.py:540-547`) has no
`timeout` argument at all** — a real, narrow gap for MCP exposure (§5.3
below); `accept_baseline` is wholly separate and never automatic.

**`scripts/assess_change_impact.py`** (Phase 83, **638 lines, under
`scripts/`, confirmed by `grep` to have zero references anywhere in
`cli.py` — not a shipped command, not packaged**): `main()` (argparse:
`--target-repo-root`, `--target-graph-db`, `--knowledge-root`, `--slug`,
`--changed path:start-end` repeatable, `--run-checks`, `--json`);
`resolve_changed_range`/`resolve_intersecting_symbols` →
`classify_symbol` → `no_recorded_relationship`/`relevant_no_coverage_
link`/`behavioural_risk`; with `--run-checks`, calls `oracle.
evaluate_check` fresh and classifies `CONFIRMED_REGRESSION`/
`INVALID_ASSESSMENT`/`VERIFIED_SCOPE`/`VERIFICATION_GAP` from that
one fresh result's own effective outcome alone (never the aggregate,
`decisions/0087` §1). Requires the **target repo's own already-synced
`context-graph.db`**.

**Correction to the governing task's own framing, found by direct
verification, not assumed**: the task describes this as "Phase 83's
impact-analysis logic" as if directly importable. It is not — it is an
unpackaged maintainer script (`[tool.setuptools.packages.find] where =
["src"]` excludes `scripts/` from any wheel), loaded today only via
dynamic, source-tree-relative import — **the identical installed-wheel
execution-boundary gap Phase 87D already found, reproduced, and
disclosed for `docs compile`** (`planning/retros/
phase-87-stage-87d-deterministic-reference-assurance.md`). The same
applies to `scripts/check_self_knowledge_quality.py` and `scripts/
check_knowledge_placement.py` (both also under `scripts/`, both expose
an importable `run_all(...)` but carry the same packaging exclusion;
`check_self_knowledge_quality.run_all`'s `repo_root` parameter defaults
to a hardcoded `DEFAULT_LEDGERKIT_ROOT` module constant that must never
be relied on implicitly).

**Resolution adopted by this plan (§3.3, §5)**: rather than accept a
second maintainer-only capability gap for a feature this phase's own
objective names as essential (change-impact assessment), `scripts/
assess_change_impact.py`'s core logic is **relocated**, unchanged, into
a new packaged module `src/codecompass/change_impact.py`; the existing
`scripts/assess_change_impact.py` becomes a thin CLI wrapper importing
from it, preserving the maintainer entrypoint's existing behaviour
exactly. This is a relocation (category 2 — thin adapter, §3 below),
not new logic and not a reimplementation of Phase 83's own design —
`decisions/0085` §3's prohibition is on duplicating the *logic* inside
the MCP server, which this plan does not do. `check_self_knowledge_
quality.py`/`check_knowledge_placement.py` are **not** relocated — their
marginal value over the already-packaged `knowledge_api.find_gaps` is
not essential to Phase 88's MVP (§3.6, category 4 — deferred).

**Phase 87 documentation layer**: `cli.py`'s `docs` sub-app commands
are `schema-init`, `compile`, `record-review`, `publish`, `maintain`
(exact names, `cli.py:1877/1936/2035/2188/2573`). Only `compile` calls
`_load_script_module` (and triggers a real Anthropic API call inside
the clean-room broker) — confirmed maintainer-only, already established
by Phase 87D, **not reopened here**. `knowledge_intermediate.
parse_grounding_markers(text)` (packaged, `knowledge_intermediate.py:
176`) already parses one doc's raw text and returns every `(cited_ids,
region_body, region_id)` triple from its `<!-- codecompass-grounded-by:
<ids> region:<id> -->...<!-- /codecompass-grounded-by -->` markers,
filterable by `region_id` — the exact primitive an MCP "documentation +
its grounding" tool needs, with zero new mechanism. **Correction, found
by independent planning review**: `find_grounded_doc_regions`
(`knowledge_intermediate.py:240-243`, signature `(project_root,
record_id, doc_names=("README.md", "CONTRIBUTING.md"))`) is a
*different* function — it looks up by **Claim/Evidence id** across a
fixed, pre-Phase-87 two-document default set (`_DEFAULT_GROUNDED_DOCS`,
`knowledge_intermediate.py:270`, the older Observation-ledger grounding
mechanism `maintain_document` still reconciles against), not by
`(doc_path, region_id)` the way an MCP tool needs to query. The real
five Phase 87 schema-governed documents are a **separate** mechanism
(`docs maintain` derives its own `doc_names` from each `**/*.schema.yaml`
file's `document:` field) — not interchangeable with `_DEFAULT_
GROUNDED_DOCS`, and not to be conflated with it.

**`src/codecompass/cli.py` full command inventory** (so no MCP tool
invents a name that doesn't exist): top-level `init`, `sync`, `index`,
`check`, `chat`, `undo`; sub-apps `query` (`vendors`/`vendor`/`symbol`/
`skills`/`relations`/`topology`/`source`/`source-symbol`), `enrich`
(`apply`), `knowledge` (`get`/`search`/`trace`/`gaps`/`context`/
`export`, plus the reconciliation-only `render`/`select-candidates`/
`apply`/`status`/`doc-select-candidates`/`doc-acknowledge-stale`/
`doc-acknowledge-chunks`), `docs` (`schema-init`/`compile`/
`record-review`/`publish`/`maintain`). `src/codecompass/graph.py`'s
read functions (`symbol_profile`, `source_file_profile`,
`source_symbol_profile`, `doc_relations`, `doc_code_trace`,
`vendor_profile`, `topology_profile`) are already packaged, read-only
over an already-opened connection — these back `knowledge_api.get`'s
own natural-key dispatch for `symbol:`/`vendor:` ids, so **first-party
source-symbol lookup is already covered by `knowledge_get`, not a
separate tool**.

## 2. Objective

An existing frontier coding agent (Claude Code first) completes a
genuine Ledgerkit development change using CodeCompass's knowledge,
assurance, and generated documentation **through a standard MCP
interface**, not a bespoke workflow or privileged file access —
matching `planning/v2-roadmap.md` §88 exactly. CodeCompass supplies
context, verification, and evidence; the coding agent remains
responsible for implementation; CodeCompass never spawns or
coordinates agents (`CLAUDE.md` §8, unchanged).

## 3. Capability-reuse matrix

### 3.1 Directly exposable, no adapter

- `knowledge_api.get`/`search`/`traverse`/`trace_evidence`/
  `epistemic_status`/`find_gaps`/`get_context_packet` — read-only,
  packaged, installed-wheel-safe. Cover knowledge discovery, evidence
  tracing, task-specific context, behavioural-contract discovery
  (`traverse` relation=`checks`/`results`), and knowledge-gap
  reporting.
- `knowledge_intermediate.parse_grounding_markers` — documentation +
  grounding retrieval (§1.1's correction: not `find_grounded_doc_
  regions`, a different, id-keyed function).
- `graph.py`'s read functions — already consumed transitively through
  `knowledge_api.get`'s natural-key dispatch; no direct MCP exposure
  needed.

### 3.2 Requiring a thin adapter

- **Server-side repo-root pinning** (new, small): `repo_root`/
  `target_repo_root` must never be an agent-supplied filesystem path
  (§5.2). The MCP server resolves a caller-supplied symbolic key
  (e.g. `"ledgerkit"`) against a fixed mapping configured at server
  startup, never a raw path from the tool call.
- **`oracle_list_checks`** (new): reads the real, committed
  `planning/contracts/<slug>/oracle-contract.yaml` plus each check's
  latest result (via `traverse`) to surface the allowlist itself to
  the calling agent, rather than only enforcing it silently.
- **`oracle_execute_check`** (new, wraps existing `evaluate_check`/
  `write_oracle_result`): validates `(slug, contract_id, check_id)`
  against the real on-disk contract (§5.2), requires the server's own
  `--enable-execution` opt-in (§5.1), and persists through the
  existing append-only `write_oracle_result` — no new persistence
  mechanism.
- **`docs_get_grounded_region`** (new, thin): wraps `parse_grounding_
  markers` (§1.1's correction) plus a `knowledge_api.get` resolution of
  each cited Claim, so the response names the grounding's *current*
  status, not just raw ids.
- **`slug` validation** (new, small — found by independent planning
  review, §15): `knowledge_find_gaps`, `oracle_list_checks`, and
  `impact_classify_change` all accept a `slug` string that existing
  code (`knowledge_api.find_gaps`, `knowledge_intermediate.slug_dir`,
  `load_slug_records`) uses directly in a filesystem path join with no
  sanitisation against `..`/absolute-path components — safe today only
  because every existing caller is a trusted local maintainer, and
  newly reachable from an untrusted remote MCP caller for the first
  time. The MCP wrapper validates every `slug` input against the
  server's own real, enumerated slug list (`knowledge_intermediate.
  _list_slugs(project_root)`) before passing it into any delegate —
  an unrecognised slug is a validation error, never silently passed
  through.
- **Revision/provenance envelope** (new, small, shared by every tool
  response): `project_revision` (git `rev-parse HEAD` of
  `project_root`) and, where a pinned target repo was consulted,
  `target_revision` — satisfying §5.9 ("stable, reproducible results
  associated with the relevant repository revision").
- **Response-size bounding for `search`/`traverse`** (new, small): confirmed
  by direct reading that neither function bounds its own result-list
  length the way `get_context_packet` already bounds `max_items`/
  `max_chars`. The MCP wrapper (not `knowledge_api.py` itself, to avoid
  touching Phase 84's shipped CLI contract) truncates to an explicit,
  documented cap and reports `truncated: true` when it does — reusing
  `get_context_packet`'s own existing truncation-disclosure convention,
  never a silent cut.

### 3.3 Genuine missing prerequisites (small, named, justified)

- **`src/codecompass/change_impact.py`** (relocation of `scripts/
  assess_change_impact.py`'s core logic — §1.1, §6 for detail). Without
  this, change-impact assessment cannot be exposed from an installed
  wheel at all, which would mean the MVP's own named essential
  capability ("assess proposed source changes using existing Phase 83
  capabilities," governing task §4) is maintainer-only by accident
  rather than by a reviewed decision. This is the one piece of new
  non-trivial code motion in this plan; it changes no classification
  logic.
- **A bounded execution timeout in `oracle.run_pytest_check`/
  `evaluate_check`** (§5.3) — a real, verified gap (no `timeout=`
  argument exists today), newly load-bearing once a check can be
  triggered remotely through an MCP tool call rather than only by a
  maintainer at a terminal who can interrupt a hang themselves.

### 3.4 Deferred rather than recreated

- `scripts/check_self_knowledge_quality.py`/`check_knowledge_
  placement.py`'s richer, corpus-wide checks — `knowledge_api.
  find_gaps` already satisfies the governing task's "knowledge gaps"
  tool requirement; promoting these two scripts into `src/` is real,
  separable future work (named here, not silently built).
- Any semantic cross-document-consistency checking (§U.3, Phase
  87's own deferred item) — unrelated to MCP, not reopened.
- Incremental knowledge/documentation reconciliation — **Phase 89**,
  independently deliverable, not a Phase 88 prerequisite
  (`decisions/0085` §3).
- A second, richer knowledge-placement-aware MCP tool beyond
  `knowledge_get`/`traverse` — not named essential by the governing
  task's own §4 list; deferred pending real post-MVP usage evidence,
  matching this project's own established Priority-A/C precedent of
  not building ahead of demonstrated need.

### 3.5 Explicitly not exposed (write/generation paths, out of a
read-mostly server's scope per `decisions/0085` §3)

`docs compile`/`publish`/`maintain`/`record-review`/`schema-init`,
`knowledge apply`/`select-candidates`/`render`, `export_snapshot`. None
of these is a knowledge-retrieval or controlled-verification primitive;
exposing any of them would mean MCP clients mutating canonical
knowledge or generated documentation, which `decisions/0085` §3's
"minimal, bounded, read-mostly MCP server" framing and this plan's own
§9 non-goals both forbid.

## 4. MCP architecture and trust boundaries

```
Coding agent (Claude Code, or any MCP-capable client)
      │ stdio (MCP: tools/list, tools/call)
      ▼
codecompass mcp-serve  (new: src/codecompass/mcp/)
      │  ├─ security.py   — repo-root pinning, execution-mode gate,
      │  │                   contract/check allowlist resolution,
      │  │                   response-size bounding
      │  └─ tools.py      — one function per MCP tool, each a thin
      │                      wrapper delegating to:
      ▼
knowledge_api.py (84) · oracle.py (82, +timeout) ·
change_impact.py (83, relocated) · knowledge_intermediate.py (81/87)
      │  read-only SQLite (file:...?mode=ro) · planning/knowledge/ ·
      │  planning/contracts/ · real target-repo checkout (read-only,
      │  pinned path only)
      ▼
context-graph.db / planning/knowledge/ / planning/contracts/
(canonical knowledge model, provenance semantics, and source-of-truth
boundaries — completely unchanged by this phase)
```

**Trust boundaries**: the MCP server process runs with the same
filesystem access as the maintainer who started it (no sandboxing
claim is made or needed — the privileged boundary is *what the server
will do*, not *what the OS lets the process touch*). The server treats
every MCP tool **input** as untrusted (validated, never interpolated
into a shell command or file path without confinement) and every
upstream **repository/document/oracle-raw-output byte** it returns to
the client as untrusted *data* the client must never treat as
instructions (§5.5) — this server never parses its own tool responses
for embedded directives, and the responses themselves are structured
JSON, not free text formatted to resemble further protocol messages.

Read-only tools (§3.1, §3.2 except `oracle_execute_check`) have zero
side effects — confirmed by construction (every delegate opens
`context-graph.db` read-only or reads static files). Exactly one tool,
`oracle_execute_check`, is privileged: it runs a real subprocess
(`pytest`) and writes a new, append-only result file. This is the only
execute-classified operation in the entire surface — see §5.1 for its
gating.

## 5. Security and independent assurance

### 5.1 Read/write/execute separation

- **Read**: `knowledge_get`, `knowledge_search`, `knowledge_traverse`,
  `knowledge_trace_evidence`, `knowledge_epistemic_status`,
  `knowledge_context_packet`, `knowledge_find_gaps`,
  `docs_get_grounded_region`, `impact_classify_change`,
  `oracle_list_checks`, `server_capabilities`.
- **Execute** (exactly one): `oracle_execute_check`. Gated on the
  server having been started with `--enable-execution` (default:
  absent, i.e. read-only mode). A server started without this flag
  rejects every call to this tool with a structured, explicit
  permission error — never a silent no-op, never a degraded "GAP"
  masquerading as a legitimate epistemic state.
- **Write**: none. `export_snapshot` is not exposed (§3.5); `oracle_
  execute_check`'s only persisted artifact is a new, append-only
  `OracleResult` file via the existing, unmodified `write_oracle_
  result` — it never overwrites or deletes an existing result.

### 5.2 No arbitrary execution; explicit allowlisting; path confinement

- `oracle_execute_check` never accepts a raw `check_reference`/pytest
  node id or an arbitrary `repo_root` from the caller. It accepts only
  `(slug, contract_id, check_id)`; the server resolves these against
  the real, committed `planning/contracts/<slug>/oracle-contract.yaml`
  on disk — if the tuple doesn't resolve to an existing check in that
  file, the call is rejected before any subprocess is considered. The
  contract file **is** the allowlist; there is no separate,
  independently-maintained allowlist to drift out of sync with it.
- `repo_root`/`target_repo_root` for both `oracle_execute_check` and
  `impact_classify_change` is never a caller-supplied path. The server
  accepts only a symbolic key (e.g. `"ledgerkit"`) resolved against a
  fixed `--repo-root <key>=<path>` mapping given at server startup by
  whoever launched the process — a coding agent connected over MCP can
  select *which* pinned target to use, never *where* on disk to look.
- No tool exposes shell execution, arbitrary file read/write, or a
  general subprocess primitive. The only subprocess CodeCompass ever
  launches on behalf of an MCP call is the existing, unchanged `pytest
  -q --junit-xml=... <check_reference>` inside `run_pytest_check`.
- **`slug` confinement** (found by independent planning review, §15):
  `knowledge_find_gaps`, `oracle_list_checks`, and `impact_classify_
  change` all take a `slug` string. Direct source verification found
  `knowledge_api.find_gaps`, `knowledge_intermediate.slug_dir`, and
  `load_slug_records` all use a supplied `slug` directly in a
  filesystem path join with no sanitisation against `..`/absolute-path
  components — a real, bounded directory-traversal/arbitrary-YAML-probe
  primitive once reachable from an untrusted remote caller, never
  exercised before because every existing caller is a trusted local
  maintainer. Every MCP tool accepting `slug` validates it against the
  server's own real, enumerated slug list (`knowledge_intermediate.
  _list_slugs(project_root)`) before it reaches any delegate — an
  unrecognised slug is rejected, never passed through.

### 5.3 Bounded resource consumption

**Real gap found and corrected (not assumed fine)**: `oracle.
run_pytest_check`'s `subprocess.run` call has no timeout today — fine
for a maintainer at a terminal who can interrupt a hang, unacceptable
for a remotely-triggerable MCP tool. This plan's implementation adds
an explicit, configurable timeout (a new keyword parameter, a sane
documented default — e.g. 300 seconds, matching this project's own
real `pytest` run durations against Ledgerkit's current suite size,
to be confirmed at implementation time rather than guessed here)
around the existing `subprocess.run` call; `subprocess.TimeoutExpired`
is caught and classified `INVALID` with an explicit reason, following
the exact same pattern `run_pytest_check` already uses for a launch
`OSError`. This is a change to shared, already-shipped Phase 82 code
(`oracle.py`) — its own existing test suite must be re-run unchanged
(no regression in normal-speed behaviour) plus one new regression test
proving a genuinely slow/hanging check is killed and classified
`INVALID`, not left to hang the MCP server process. Response-size
bounding for `search`/`traverse` (§3.2) and `get_context_packet`'s
already-existing `max_items`/`max_chars` cover output-size limits.

### 5.4 Fail-closed behaviour and accurate PASS/FAIL/GAP/INVALID semantics

- `ConsistencyEnvelope.status` (`current`/`stale`/`unconfirmed`,
  default `unconfirmed`) is surfaced verbatim in every `knowledge_*`
  tool response — an MCP client is never told a historical `PASS` is
  "current" without a live reconfirmation actually happening
  (`decisions/0092`, unchanged, reused not re-derived).
  `CheckAggregate.state` (`PASS`/`GAP`/`NOT_REQUIRED`, no aggregate
  `FAIL`) and `oracle_execute_check`'s own fresh per-result outcome
  (`PASS`/`FAIL`/`GAP`/`INVALID`) are both surfaced together, never
  collapsed into one token (`CLAUDE.md`'s own precedent, `L-072`: "a
  verdict token answers exactly one question").
  `CONFIRMED_REGRESSION`/`INVALID_ASSESSMENT`/`VERIFIED_SCOPE`/
  `VERIFICATION_GAP` is the relocated `change_impact.assess()`'s own
  `--run-checks` classification — **this plan's `impact_classify_
  change` tool deliberately never sets `run_checks=True`** (§6, §5.1:
  it is read-only classification only; triggering a fresh check is
  `oracle_execute_check`'s job alone, the one execute-classified tool).
  Where a future revision ever did wire this classification through,
  it would need to be reported from the one fresh result's own
  effective outcome alone, exactly matching `decisions/0087` §1 — never
  the aggregate state; not applicable to this plan's own MVP surface.
- When a pinned target repo is unreachable, every tool that would
  otherwise claim "current" instead reports `unconfirmed`/a GAP with
  an explicit reason — never silently reporting the historical value
  as if freshly confirmed.

### 5.5 Untrusted content

Repository content, document text, and oracle raw output are returned
as plain structured data fields (e.g. `raw_output_text`, `summary`,
`details`), never as directives the server itself executes or acts on.
This server performs no "read a doc, then act on what it says" step at
all — every tool does exactly the one delegated, parameter-driven
retrieval or check it was asked to do, nothing conditioned on parsing
response content for further instructions. (The coding-agent side of
this boundary — not re-executing instructions it finds inside returned
document text — is the client's own responsibility and out of this
server's control; this plan's test suite (§5.10) still verifies the
server itself never special-cases content that looks like an
instruction.)

### 5.6 Reproducibility and provenance

Every tool response carries `project_revision` and, where a pinned
target repo was consulted, `target_revision` (§3.2) plus whatever
content/tree digest the underlying record already carries
(`source_files.content_hash`, `OracleResult`'s own digest fields) —
reused, not reinvented.

### 5.7 Independent assurance, never self-certified

No tool call result — including `oracle_execute_check`'s own fresh
`PASS` — is ever treated by this plan as sufficient evidence of the
*phase's own* correctness. Phase 88's own Definition of Done (§11)
still requires a fresh, independent `release-phase-auditor` dispatch
covering the real repository state, exactly as every prior phase; an
agent's MCP-mediated report of a successful verification is data about
the demonstration, not a substitute for that audit.

### 5.8 Tests (§11.3 names the concrete list; summarised here)

Malformed-input tests per tool (wrong id shape, out-of-range
`max_items`, unknown `relation` value, unknown `slug`); a permission-
bypass test (`oracle_execute_check` called against a server started
without `--enable-execution`, and called with a `(contract_id,
check_id)` pair not present in the real contract file); a prompt-
injection test (a crafted `planning/knowledge/` record or doc region
containing text engineered to look like a further tool-call directive,
confirmed returned verbatim as inert data, never triggering a second,
unrequested tool invocation); an unauthorised-execution test
(attempting to invoke a pytest node id not named by any real contract
check); a repo-root-path-injection test (a tool call attempting to
pass a raw filesystem path where only a pinned symbolic key is
accepted, confirmed rejected).

## 6. Proposed MCP tool/resource surface

Transport: **stdio**, via the official `mcp` Python SDK (PyPI package
`mcp`, MIT-licensed, Python 3.10+ floor — compatible with this
project's own `>=3.11` floor; `anthropic`/`typer`/`rich`-style
dependency, not vendored source). Considered and rejected for this
phase: leaner third-party alternatives (e.g. `chuk-mcp`) — lighter
dependency footprint, but not the spec-reference implementation and
not what other MCP-capable clients are built/tested against; §6's own
compatibility-with-other-clients goal outweighs the dependency-weight
cost here. The exact transitive dependency count was not verified
against a real `pip install` during this planning task (no runtime
dependency was installed, per this task's own §12 instruction) — this
project's own `pipdeptree` dependency (already a direct dependency,
`decisions`-unrelated, pre-existing) should audit the real resulting
tree at implementation time before the dependency is finalised in
`pyproject.toml`.

All tools below use MCP's `tools/call` primitive (parameterised
actions), not static `resources/list` entries — every one of
CodeCompass's real read operations takes required arguments (a record
id, a search string, a slug), so a parameterless "resource" framing
would not fit without inventing an enumeration CodeCompass doesn't
have today. One lightweight exception (`server_capabilities`, below)
is included because a calling agent otherwise has no way to discover
which target-repo keys and execution mode are available before trying.

| # | Tool | Delegates to | R/W/X | MVP (88A/88B) |
|---|---|---|---|---|
| 1 | `knowledge_get` | `knowledge_api.get` | R | 88A, essential |
| 2 | `knowledge_search` | `knowledge_api.search` (+ wrapper cap) | R | 88A, essential |
| 3 | `knowledge_traverse` | `knowledge_api.traverse` (+ wrapper cap) | R | 88A, essential |
| 4 | `knowledge_trace_evidence` | `knowledge_api.trace_evidence` | R | 88A, essential |
| 5 | `knowledge_epistemic_status` | `knowledge_api.epistemic_status` | R | 88A, essential |
| 6 | `knowledge_context_packet` | `knowledge_api.get_context_packet` | R | 88A, essential |
| 7 | `knowledge_find_gaps` | `knowledge_api.find_gaps` | R | 88A, essential |
| 8 | `docs_get_grounded_region` | `knowledge_intermediate.find_grounded_doc_regions` + `knowledge_api.get` | R | 88A, essential |
| 9 | `server_capabilities` | new, trivial (reads server startup config) | R | 88A, essential |
| 10 | `impact_classify_change` | new `change_impact.assess(..., run_checks=False)` | R | 88B, essential |
| 11 | `oracle_list_checks` | reads `oracle-contract.yaml` + `knowledge_api.traverse` | R | 88B, essential |
| 12 | `oracle_execute_check` | `oracle.evaluate_check` + `write_oracle_result` | **X** | 88B, essential |

Each tool's full spec (input/output JSON schema, error/GAP/
INDETERMINATE behaviour, size limits):

### 1. `knowledge_get`
- **Purpose**: retrieve one Requirement/Claim/Decision/Evidence/
  Observation/Derivation, or one natural-key record (symbol/vendor/doc/
  contract/check/result), by id.
- **Input**: `{record_id: str, repo_root_key: str | null}`.
- **Output**: `ApiResponse`-shaped JSON (`status`, `results`,
  `gaps`, `message`) plus `project_revision`/`target_revision`.
- **R/W/X**: R.
- **Validation**: `record_id` non-empty string; `repo_root_key`, if
  given, must be a key present in the server's own startup mapping —
  unknown key is a validation error (not silently ignored).
- **Error/GAP**: unknown id → `status: "empty"` (matches `knowledge_
  api.get`'s own existing behaviour, never raises). Unknown
  `repo_root_key` → tool error, `isError: true`.
- **Limits**: single record, already small; no truncation needed.
- **MVP**: essential.

### 2. `knowledge_search`
- **Purpose**: bounded substring search across the knowledge corpus.
- **Input**: `{text: str, kinds: list[str] | null, limit: int = 20}`.
- **Output**: `ApiResponse` with `results` truncated to `min(limit,
  100)`; `truncated: true` set when the underlying result set was
  larger.
- **R/W/X**: R.
- **Validation**: `text` non-empty; `limit` clamped to `[1, 100]`,
  out-of-range values clamped (not rejected) with the clamp disclosed
  in the response, not silently applied.
- **MVP**: essential.

### 3. `knowledge_traverse`
- **Purpose**: one-hop (or `depth`-hop) relation traversal — also the
  mechanism for "discover applicable contracts, checks and recorded
  results" via `relation="checks"`/`"results"`.
- **Input**: `{record_id: str, relation: str, depth: int = 1, limit:
  int = 20, repo_root_key: str | null}`.
- **Output**: `ApiResponse`, truncated per `knowledge_search`'s own
  convention.
- **Validation**: `relation` must be one of the fixed enum named in
  §1.1; an unrecognised value is a validation error, never silently
  treated as "no relation."
- **MVP**: essential.

### 4. `knowledge_trace_evidence`
- **Purpose**: evidence tracing — provenance, supporting/contradicting
  evidence, dangling-citation gaps.
- **Input**: `{record_id: str, repo_root_key: str | null}`.
- **Output**: `ApiResponse`; `status: "gap"` with an explicit gap kind
  (`missing_evidence`/`dangling_evidence_reference`/`dangling_
  dependency_reference`) is a normal, successful response, not an
  error — the gap *is* the answer.
- **MVP**: essential.

### 5. `knowledge_epistemic_status`
- **Purpose**: verification currency — `intended`/`observed`/
  `contested`, `verified_scopes`/`known_gap_scopes`/`unconfirmed_
  scopes`.
- **Input**: `{record_id: str, repo_root_key: str | null}`.
- **Output**: `ApiResponse`.
- **MVP**: essential.

### 6. `knowledge_context_packet`
- **Purpose**: bounded, task-specific context packet for a topic.
- **Input**: `{topic: str, max_items: int = 20, max_chars: int = 6000,
  repo_root_key: str | null}`.
- **Output**: `ApiResponse`; `details.bounds.truncated` surfaced
  verbatim (existing convention, unmodified).
- **Validation**: `max_items`/`max_chars` clamped to the same ceiling
  `knowledge_api.get_context_packet` already enforces internally — the
  wrapper adds no new ceiling here since one already exists.
- **MVP**: essential.

### 7. `knowledge_find_gaps`
- **Purpose**: corpus-wide (or slug-scoped) gap report — "report
  missing, stale, conflicting, or unverified knowledge without
  inventing missing facts."
- **Input**: `{slug: str | null, repo_root_key: str | null}`.
- **Output**: `ApiResponse`.
- **MVP**: essential.

### 8. `docs_get_grounded_region`
- **Purpose**: retrieve a published documentation region and its
  current grounding (cited Claim ids + each one's live status).
- **Input**: `{doc_path: str, region_id: str | null}`.
- **Output**: `{status: "result"|"empty", regions: [{region_id,
  body, grounded_by: [{claim_id, status}]}], project_revision}`.
- **Validation**: `doc_path` confined to the repository's own
  schema-governed document set (`README.md`, `docs/getting-started.md`,
  `docs/concepts/adapter.md`, `docs/concepts/vendor-and-ecosystem.md`,
  `docs/concepts/knowledge-model.md` — Phase 87's own five, re-verified
  at implementation time rather than hardcoded from this plan's own
  memory) — a path outside this set is a validation error, never an
  arbitrary-file-read primitive.
- **MVP**: essential.

### 9. `server_capabilities`
- **Purpose**: let a calling agent discover, before trying, which
  `repo_root_key` values are configured and whether execution mode
  (`oracle_execute_check`) is enabled at all.
- **Input**: `{}`.
- **Output**: `{repo_root_keys: [str], execution_enabled: bool,
  codecompass_version: str}`.
- **MVP**: essential (small, but removes a whole class of "try it and
  see" failure mode).

### 10. `impact_classify_change`
- **Purpose**: assess a proposed source change's relationship to
  existing knowledge/evidence — read-only classification, no check
  execution.
- **Input**: `{repo_root_key: str, slug: str, changed: [{path: str,
  start: int, end: int}]}`.
- **Output**: **correction, found by independent planning review** —
  the relocated `change_impact.assess()` genuinely returns, per
  changed range, a `RangeReport` with `status ∈ {"resolved",
  "partially_resolved", "stale_index", "cannot_map"}` **plus** a
  separate `symbol_classifications` list (each with its own
  `classification ∈ {"no_recorded_relationship",
  "relevant_no_coverage_link", "behavioural_risk"}`), across
  potentially multiple ranges and multiple intersecting symbols per
  range — not one scalar `classification` field. The original
  single-scalar schema this plan first proposed would either crash or
  silently discard real information the underlying function returns.
  Corrected output: `{status, ranges: [{path, start, end,
  range_status: "resolved"|"partially_resolved"|"stale_index"|
  "cannot_map", symbol_classifications: [{symbol, classification:
  "no_recorded_relationship"|"relevant_no_coverage_link"|
  "behavioural_risk", evidence_ids}]}], target_revision}` — a
  lossless pass-through of the real per-range/per-symbol structure,
  including the previously-omitted `cannot_map` status.
- **Validation**: `repo_root_key` resolved per §5.2; `slug` validated
  against the server's own enumerated slug list (§3.2/§5.2's `slug`-
  confinement correction) and must name a real `planning/knowledge/
  <slug>/` directory; `changed` ranges validated against the target
  file's own current extent — a partially-resolved range is reported
  as such (`resolve_intersecting_symbols`'s existing `partially_
  resolved`), never silently narrowed.
- **Error/GAP**: `stale_index`/`cannot_map` (the target's live content
  hash doesn't match the graph's recorded hash, or a changed range
  can't be mapped to any symbol at all) are both first-class, explicit
  per-range outcomes, never a crash or a silent fallback to guessing.
- **MVP**: essential.

### 11. `oracle_list_checks`
- **Purpose**: surface the real, on-disk allowlist for a given slug —
  what `oracle_execute_check` will actually accept.
- **Input**: `{slug: str}`.
- **Output**: `{checks: [{contract_id, check_id, description,
  required: bool, check_reference, latest_result_status}]}`.
- **MVP**: essential.

### 12. `oracle_execute_check`
- **Purpose**: the one controlled-verification execute operation.
- **Input**: `{slug: str, contract_id: str, check_id: str,
  repo_root_key: str}`.
- **Output**: `{outcome: "PASS"|"FAIL"|"GAP"|"INVALID",
  invalid_reason: str | null, raw_output_ref: str, run_id: str,
  target_revision: str}`.
- **R/W/X**: **X** (subprocess execution) + one new, append-only,
  persisted result file.
- **Validation**: rejects immediately (before any subprocess) if (a)
  the server was not started with `--enable-execution`; (b)
  `(slug, contract_id, check_id)` does not resolve against the real
  `oracle-contract.yaml`; (c) `repo_root_key` does not resolve against
  the server's own pinned mapping.
- **Error/GAP/INDETERMINATE**: `INVALID` (including the new timeout
  case, §5.3) is a legitimate, fully-specified outcome, never an
  uncaught exception crossing the MCP boundary.
- **Limits**: bounded by the new timeout (§5.3); raw output capped at
  a documented size (reusing whatever cap, if any, `write_oracle_
  result` already enforces — confirmed/added at implementation time).
- **MVP**: essential — this is the "controlled verification" the
  governing task names as core.

## 7. Dependency and licence assessment

| Package | Source | Licence | Compatibility |
|---|---|---|---|
| `mcp` | PyPI, official `modelcontextprotocol/python-sdk` | MIT | Permissive; compatible as a dependency of a GPL-3.0-or-later project. Python 3.10+ floor, within this project's `>=3.11`. |

No vendored source is added (matches this project's existing
dependency convention — `anthropic`/`typer`/`rich`/`pipdeptree`/
`pyyaml` are all PyPI dependencies, not vendored). **Flagged for
implementation time, not resolved here**: adding `mcp` to
`pyproject.toml`'s `dependencies` list means `CLAUDE.md`'s own
dependency-digest table (the one listing `anthropic`/`pipdeptree`/
`rich`/`typer` with their `vendor/<name>/DEPTREE.md` links) would, by
its own established convention, gain a new row — but `CLAUDE.md` is a
**protected file** (`CLAUDE.md` §0): "any change to this file, however
small, must be presented to the user as a diff and receive explicit
approval before it is written or committed." This plan does **not**
pre-approve that edit; implementation must present the diff separately
and obtain explicit §0 approval before committing it, exactly as
`L-116`/`L-117`'s own pending `CLAUDE.md` §1 proposals are already
sitting, unapplied, for the same reason.

## 8. Threat model summary (full detail: §5)

| Threat | Mitigation |
|---|---|
| Arbitrary shell/command execution via MCP | Only one subprocess path exists (`pytest` via the existing `run_pytest_check`); no tool accepts a raw command/path for execution. |
| Unauthorised oracle check execution | Explicit allowlist resolved against the real on-disk contract file; execution mode opt-in at server startup. |
| Path traversal / arbitrary file access | `repo_root_key` is a pinned symbolic key, never a caller-supplied path; `docs_get_grounded_region`'s `doc_path` confined to the real schema-governed doc set; every `slug` input validated against the server's own real, enumerated slug list before reaching any delegate (§5.2). |
| Resource exhaustion (hang, unbounded output) | New subprocess timeout (§5.3); response-size caps on `search`/`traverse`/`context_packet`. |
| Prompt injection via repository/document content | Server returns content as structured data, never re-interprets it as directives; tested explicitly (§5.10). |
| Stale/historical result presented as current | `ConsistencyEnvelope` status and aggregate/per-result outcome semantics surfaced verbatim, never collapsed (§5.4). |
| Agent self-reporting a verification as authoritative | Phase-level DoD still requires an independent `release-phase-auditor` pass (§11); no MCP tool result is treated as self-certifying. |

## 9. Explicit non-goals

No new canonical knowledge storage or second graph; no
reimplementation of `knowledge_api`/`oracle`/the impact engine's own
*logic* (relocation of `assess_change_impact.py` for packaging is not
a reimplementation — §3.3); no agent spawning, task scheduling, or
workflow orchestration; no general-purpose code execution; no local/
offline model routing; no cross-project semantic overlays; no
automatic source-change-driven reconciliation (Phase 89); no
general-purpose architectural-convention enforcement or CI policy
gating; no Phase 90 comparative trials or later release-hardening;
no PR policy gating or Orchestrator.inc-specific integration (§10).
`scripts/check_self_knowledge_quality.py`/`check_knowledge_
placement.py` are not promoted to `src/` this phase (§3.4).

## 10. Orchestrator-platform independence

The server is a plain stdio MCP process (`codecompass mcp-serve`) with
zero Claude-Code-specific or Orchestrator.inc-specific code — any
MCP-capable client spawns it the same way. Claude Code is the first,
directly-tested client (Stage 88C); the exact client-side registration
syntax (Claude Code's own MCP-server configuration convention) is
verified against Claude Code's current documentation at implementation
time, not guessed here (avoiding a speculative, possibly-wrong config
snippet in this plan). Because every tool delegates to an
already-independently-callable function (`knowledge_api.*`,
`oracle.evaluate_check`, the new `change_impact.assess`), a future
headless CLI/CI assurance gate can call the same underlying functions
directly without MCP existing at all — already true today for
`knowledge_api`/`oracle`, and preserved for change-impact assessment by
the relocation in §3.3/§6.

## 11. Staged implementation sequence

Two stages, not three — justified below (§11.4).

### 11.1 Stage 88A — MCP foundation (read-only)

**Deliverables**: `src/codecompass/mcp/` (`server.py`, `tools.py`,
`security.py`); `codecompass mcp-serve` CLI command (`--repo-root
<key>=<path>` repeatable, `--project-root`, no `--enable-execution`
flag yet needed at this stage since no execute tool exists); tools
1-9 (§6); the revision/provenance envelope; response-size bounding for
`search`/`traverse`; `mcp` added to `pyproject.toml` (pending `CLAUDE.md`
§0 approval for the table edit, §7); `decisions/0095` (architecture
ADR, drafted during planning — see companion file, ratified at
implementation).

**Tests**: protocol-contract tests (each tool's declared JSON schema
matches its actual accepted/returned shape); malformed-input tests per
tool; a `repo_root_key`-path-injection rejection test; a prompt-
injection test against `knowledge_search`/`docs_get_grounded_region`
(crafted content returned inert); truncation-disclosure tests for
`search`/`traverse`/`context_packet`.

**Acceptance criteria**: every tool's output independently verified
against the real corpus (not only synthetic fixtures — `L-113`'s own
established discipline) to match what the equivalent `knowledge get`/
`search`/`trace`/`gaps`/`context` CLI command already returns for the
same input, byte-for-byte on the shared fields. Full regression suite
and `ruff check .` clean; `check_user_docs.py --strict` clean.

**Independent verification checkpoint**: a fresh `release-phase-
auditor`-style review of 88A alone before 88B begins — confirms no
Phase 84 logic was duplicated, confirms the read/write separation holds
even at this read-only stage, confirms `CLAUDE.md` wasn't touched
without the required separate approval.

### 11.2 Stage 88B — Assurance integration

**Deliverables**: `src/codecompass/change_impact.py` (relocated from
`scripts/assess_change_impact.py`, which becomes a thin wrapper — its
own existing 27+ tests re-run unchanged against the relocated code,
plus one new test confirming the CLI wrapper's output is identical
pre/post relocation); the bounded timeout in `oracle.py` (§5.3, with
its own new regression test); tools 10-12 (§6); `--enable-execution`
flag on `codecompass mcp-serve`.

**Tests**: the adversarial set named in §5.10 (permission-bypass,
unauthorised-execution, allowlist-rejection); a real end-to-end
`oracle_execute_check` call against the real `balance-from-spec`
contract's two already-passing checks (confirms the full chain
produces an identical outcome to the existing `scripts/run_balance_
from_spec_oracle.py` path, not a divergent one); a real `impact_
classify_change` call against Ledgerkit's real, synced graph.

**Acceptance criteria**: full regression suite, `ruff check .`, all
relevant strict validators (per the baseline-aware policy established
in Phase 87D — `L-114`'s 26-blocking debt stays unrelated and
unchanged); no behavioural change to `oracle.py`'s existing callers
(`scripts/run_balance_from_spec_oracle.py`, `check_contracts.py`)
beyond the new timeout parameter accepting its own documented default.

**Independent verification checkpoint**: a fresh `release-phase-
auditor`-style review of 88A+88B together, specifically re-verifying
the adversarial security tests actually exercise the described attack
(not merely reaching the code path, matching `L-108`'s established
discipline for corrective-pass-style new code).

### 11.3 Stage 88C — Real Ledgerkit demonstration and closeout

**Deliverables**: Claude Code configured against the real
`codecompass mcp-serve` process; the real demonstration task (§12);
`docs/reference/mcp.md` (new, user-facing); `architecture/` update
describing the MCP integration design; phase retro; learnings triage;
`planning/ROADMAP.md`/`planning/CONTEXT.md`/`CHANGELOG.md`
reconciliation.

**Independent verification checkpoint**: full-phase `release-phase-
auditor` dispatch per `CLAUDE.md` §5, covering all of Phase 88 against
the final committed state — not merely Stage 88C's own diff, matching
Phase 87's own established terminal-audit precedent.

### 11.4 Why two stages, not three

The governing task's own suggested 88A/88B/88C maps naturally onto
"read-only foundation" / "assurance + execution" / "demonstration," but
a demonstration stage with no new code of its own (Stage 88C adds zero
new tools — it only *uses* 88A+88B's already-complete surface) does
not need its own independent architectural review checkpoint the way
88A and 88B each do; it needs a *completion* audit, which is the same
terminal `release-phase-auditor` dispatch every phase already requires
(`CLAUDE.md` §5). This plan therefore treats 88A and 88B as the two
real implementation stages, each with its own acceptance criteria and
mid-phase verification checkpoint, and folds "88C" into this plan's own
§12 (demonstration) + §13 (closeout) rather than giving it a separate
numbered implementation stage with nothing structurally new to review.
This is a documentation-structure simplification only — every
deliverable the governing task's own §8 names for "88C" is still
present, just not under a third stage heading.

## 12. Real Ledgerkit development demonstration

**Verified this session** (independent fork research, read-only, no
Ledgerkit modification): Ledgerkit checkout at
`~/projects/ledgerkit`, HEAD `7224bb5c113cd3aad7e86e994365703cd0070154`
at research time (re-confirmed fresh at Stage 88C's own start, not
assumed current from this plan).

### 12.1 Primary candidate

`planning/contracts/balance-from-spec/oracle-contract.yaml` already
declares a third **required** check, `overlapping-account-patterns-
no-double-count`, whose `check_reference`
(`tests/test_reports.py::TestBalanceFromSpec::
test_section_accounts_overlapping_patterns_no_double_count`) names a
test that **does not exist yet** in the real `~/projects/ledgerkit`
checkout — confirmed by direct grep. This is a real, pre-existing,
repeatedly-named gap (`CL-BFS-005.yaml` states it explicitly; Phases
83/84/86/87's own retros all name it as outstanding), not manufactured
for this demonstration.

- **Relevant knowledge/evidence**: `REQ-BFS-002` → `CL-BFS-004`/
  `CL-BFS-005` → `EV-BFS-001` (`source_ref: ledgerkit/reports.py:600`,
  confirmed current — `source_symbols` already indexes `balance_from_
  spec` at line 600 in Ledgerkit's own already-synced `context-
  graph.db`) + `EV-BFS-002`/`EV-BFS-003` → `DEC-BFS-002`.
- **Behavioural requirement/contract**: the existing `balance-from-
  spec` oracle contract's third required check, already specified,
  never executed.
- **Impact-assessment opportunity**: `impact_classify_change` against
  `reports.py` lines around `balance_from_spec` should report
  `behavioural_risk` (a Claim bridges Evidence to this exact gap),
  confirmed feasible today since Ledgerkit's graph is already synced
  and current.
- **Independently executable verification**: once the missing test is
  written, `oracle_execute_check` (or, equivalently, the existing
  maintainer path `scripts/run_balance_from_spec_oracle.py
  --check-id overlapping-account-patterns-no-double-count`) produces a
  new, real, permanent result file — never overwriting the two
  existing passing results (Phase 82's append-only convention,
  unchanged).
- **Documentation relevant to the task**: `docs_get_grounded_region`
  against whichever published region (if any) cites `CL-BFS-004`/
  `CL-BFS-005` — confirmed/named at implementation time against the
  real current publication state, not assumed here.
- **Implementation already believed correct, not yet oracle-
  confirmed**: `reports.py:663`'s `if not any(_matches_pattern(pat,
  posting.account) for pat in section.accounts): continue` is a single
  boolean gate, not a per-pattern double-counting loop — the fixture
  `tests/fixtures/filtered.journal`'s existing £150.00 groceries
  posting (matching both `"food"` and `"groceries"` patterns) is
  already in place to exercise it. The demonstration's real value is
  closing the gap between "believed correct by source reading" and
  "oracle-confirmed," using the MCP surface end to end.

### 12.2 Fallback

No second real contract family exists in the corpus today (`ls
planning/contracts/` — `balance-from-spec` only). Ledgerkit's own
genuinely deferred feature (`; report`/`; end report` journal-comment
`ReportSpec` parsing, `dev-docs/api-spec.md`, `[DEFERRED — Milestone
3]`) is real but too large and has zero existing contract/Evidence
coverage — rejected as a demonstration candidate for that reason, not
reconsidered. No `TODO`/`FIXME`/`NotImplementedError` marker anywhere
in Ledgerkit's own source offers a smaller independent alternative
(confirmed by grep). **The honest fallback is the same candidate,
executed against a disposable scratch copy of Ledgerkit rather than
the real checkout** (mirroring Phase 83's own scratch-copy mutation-
testing precedent) — used only if the cross-repository write
authorisation for the real `~/projects/ledgerkit` checkout isn't
granted at Stage 88C's own start. This exercises the identical MCP/
knowledge/impact/oracle chain without permanently landing in
Ledgerkit's real history; Stage 88C's own closeout report must name
explicitly which of the two actually ran, since the scratch-copy
variant is a weaker, not equivalent, substitute.

### 12.3 Independent context-quality assessment

A fresh, independent reviewer (matching this project's existing
`context-evaluator` role and rubric, `docs/*/packet-sufficiency.md`
precedent) separately assesses whether the context retrieved through
the MCP surface during the real demonstration was correct, relevant,
and useful — inspecting Ledgerkit directly to establish ground truth,
never running CodeCompass to check CodeCompass (matching that agent's
own existing charter). This is a context-quality check, not a
Phase 90 productivity comparison (§12.4).

### 12.4 Explicitly not a productivity claim

This is an integration demonstration, not a comparative trial.
Development effort, token consumption, context usefulness, and
verification cost are recorded where feasible (matching the governing
task's own §7 instruction), but no economic or productivity advantage
is claimed from one case with no baseline arm — that comparison is
Phase 90's own, separately gated, scope.

## 13. Definition of Done, mapped to the governing exit gate

| Governing exit gate element | Satisfied by |
|---|---|
| "The agent completes a genuine development change" | §12.1's real `overlapping-account-patterns-no-double-count` test, landed via the MCP surface. |
| "using CodeCompass's context, independent assurance, and documentation" | Tools 1-9 (context/documentation), 10-12 (assurance) — all exercised, not merely available. |
| "through supported interfaces — not merely 'the MCP server starts'" | §12.1's full chain: retrieve knowledge → see unmet contract → write test → `impact_classify_change` → `oracle_execute_check` → real new PASS result — all via MCP tool calls, confirmed in the demonstration's own transcript, never a bespoke script or direct file access. |
| `CLAUDE.md` §5 (per-phase DoD) | Code + tests implemented; `docs/`/`architecture/`/`decisions/` updated; independent `docs-reconstructor` drift audit; `CHANGELOG.md` entry; `CONTEXT.md` updated; phase retro; learnings triaged; independent `release-phase-auditor` PASS/PASS WITH NON-BLOCKING OBSERVATIONS against the final committed state. |
| §11 independent planning review (this task) | Fresh `Plan`-type reviewer dispatch, §15 below — resolved before implementation begins. |

## 14. Risks, bottlenecks, and genuinely unresolved decisions

- **Risk, named explicitly by the governing roadmap itself**: scope
  creep toward reimplementing Phase 84/83's own logic inside the
  server. Mitigated structurally — every tool in §6 is a thin
  delegate; §3.3's one relocation is logic-preserving, not a rewrite.
- **Bottleneck**: the exact `mcp` SDK dependency footprint is
  unverified until implementation time (§7) — if the transitive tree
  proves unacceptably heavy, the `chuk-mcp` alternative (§6) should be
  reconsidered at that point, not silently substituted without
  updating this plan's own §7 table.
- **Unresolved, requires explicit user approval before landing**: the
  `CLAUDE.md` §0 dependency-table edit (§7) — a diff must be presented
  separately.
- **Unresolved, requires explicit authorisation before Stage 88C**:
  writing the real missing test into the real `~/projects/ledgerkit`
  checkout (a cross-repository action) — matching this project's own
  established precedent (Phase 83's own identical, still-separately-
  gated item) of never treating a cross-repository write as silently
  pre-authorised by a planning task.
- **Estimated relative effort**: Stage 88A (foundation, 9 thin tools +
  security/provenance wrapper) is the larger implementation effort;
  Stage 88B (3 tools + one relocation + one timeout fix) is smaller
  but carries the higher-stakes security surface (the one execute
  tool) and therefore the heavier review burden per tool.

## 15. Independent planning review

A fresh `Plan`-type reviewer, with no reliance on this plan's or the
companion ADR's own self-assessment, independently re-verified every
tool-to-capability mapping, the security design, the Ledgerkit
demonstration's real feasibility, the licence/SDK reasoning, the
Phase 89/90 boundary, and the staging justification — against the
real source (`knowledge_api.py`, `oracle.py`, `scripts/assess_change_
impact.py`, `knowledge_intermediate.py`, `cli.py`, `pyproject.toml`,
`CLAUDE.md`, `decisions/0085`/`0087`, `planning/v2-roadmap.md`'s real
Phase 88/89/90 sections) and the real `~/projects/ledgerkit` checkout,
not by trusting this plan's own citations.

**Verdict: READY WITH NON-BLOCKING OBSERVATIONS**, contingent on four
blocking findings, all fixed in this same session (none required
re-architecting the plan):

1. **`docs_get_grounded_region` cited the wrong primitive and the
   wrong doc-name scope.** `find_grounded_doc_regions` (id-keyed,
   fixed pre-Phase-87 two-doc default) is not the same mechanism as
   the five real Phase 87 schema-governed documents (`docs maintain`'s
   own `**/*.schema.yaml`-derived set). Fixed: §1.1, §3.1, §3.2, §6
   tool 8 now cite `parse_grounding_markers` and correctly distinguish
   the two mechanisms rather than conflating them.
2. **An unaddressed `slug`-parameter path-traversal gap**, newly
   exposed by MCP remoting (`knowledge_find_gaps`/`oracle_list_checks`/
   `impact_classify_change`'s `slug` reaches `knowledge_intermediate.
   slug_dir`/`load_slug_records` with no sanitisation against
   `../`-style components — safe only while every caller was a trusted
   local maintainer). Fixed: §3.2, §5.2 both now require every `slug`
   input validated against the server's own enumerated slug list
   before it reaches any delegate.
3. **`impact_classify_change`'s output schema was lossy/wrong** — the
   real relocated `assess()` returns a per-range `RangeReport`
   (`status` including a `cannot_map` value this plan had omitted)
   plus a separate per-symbol `symbol_classifications` list, not one
   scalar `classification` field. Fixed: §6 tool 10's output schema
   now passes through the real nested structure losslessly; a related
   internal inconsistency in §5.4 (which had implied this tool runs a
   fresh check, contradicting §6's own `run_checks=False` design) was
   also found and corrected during the same pass.
4. **`planning/ROADMAP.md`'s Phase 88 row asserted "independently
   reviewed" before this review had concluded.** Fixed: the row now
   names the review as pending at the time it was written, and records
   this section's own actual outcome.

Everything else the reviewer independently checked — the eight
`knowledge_api` signatures, `ConsistencyEnvelope`/`CheckAggregate`
value sets, the `oracle.py` timeout gap (explicitly re-verified by
direct line-level reading, confirmed real), the relocation-vs-
duplication distinction against `decisions/0085` §3's actual wording,
the SDK/licence reasoning, the Ledgerkit demonstration's real
feasibility (contract, missing test, fixture, fallback honesty, all
independently re-confirmed against the live `~/projects/ledgerkit`
checkout), platform independence, staging justification, DoD
objectivity, and the Phase 89/90 boundary — held up exactly as stated
and required no change. This review's own findings are preserved here
as the actual history, not retrospectively smoothed into a claim that
the first draft was already correct.
