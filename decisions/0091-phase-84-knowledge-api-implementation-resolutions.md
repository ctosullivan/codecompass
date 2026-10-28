# 0091: Phase 84 implementation resolutions — response shape, identity encoding, context packet, read-only access

**Status:** accepted (2026-10-29). Governing prompt: "CodeCompass
Orchestrator — Close Phase 83 and Implement Phase 84" (2026-10-29).
`planning/phase-84-consolidated-knowledge-api.md` (`decisions/0084`/
`0085`) is the approved, implementation-ready plan; this ADR records the
concrete design choices its own §10 "Unresolved decisions" deliberately
deferred to "this phase's own first implementation commit," plus a small
number of further implementation-level choices the plan sketched at a
level this ADR now pins down exactly. None of this reopens `decisions/
0084`/`0085`'s own settled architecture (one logical model, unchanged
physical storage; natural-key identity over a new persisted id; reuse of
existing epistemic/precedence mechanisms) — every choice below is a
resolution within that architecture, not a change to it.

## Context

The plan's own §10 named the `ContextPacket` shape as explicitly
unresolved pending real implementation experience. Separately, writing
`src/codecompass/knowledge_api.py` surfaced four further concrete
choices the plan's prose described at a conceptual level (a "typed
result/empty/gap shape," "natural-key identities," "a response-time
consistency envelope," "bounded context retrieval") without pinning down
the exact Python shapes or encodings needed to actually implement them.

## Decisions

### 1. One uniform `ApiResponse` envelope, not a bespoke type per function

Every public function (`get`/`search`/`traverse`/`trace_evidence`/
`epistemic_status`/`find_gaps`/`get_context_packet`/`export_snapshot`)
returns one `ApiResponse` dataclass: `status` (`"result"`/`"empty"`/
`"gap"`), `results: list[KnowledgeResult]`, `gaps: list[Gap]`, `message`.
The plan's own prose sketched per-function return types (`KnowledgeView
| Gap`, `EvidenceTrace`, `ContextPacket`); a single uniform envelope was
chosen instead so every call site handles the three-way shape
identically (one `if response.status == ...` idiom everywhere, in both
the library and the CLI), and so a CLI/JSON consumer never needs
per-function parsing logic. `status` rules, fixed project-wide:
`"empty"` means the requested identity/query/slug matched nothing at
all; `"gap"` is reserved for `trace_evidence`/`find_gaps`, where a
specific, nameable obligation (a required check, a claim's own
citation) exists but nothing currently resolves it; every other
function only ever reports `"result"`/`"empty"`. A resolved identity
with zero edges for the *specific relation asked* (e.g. `traverse(id,
"contradicting_evidence")` on a claim with none) is `"result"` with an
empty list — a confirmed, informative zero, never collapsed into
`"empty"`, which is reserved for the identity itself not resolving.

### 2. Natural-key identities are plain, parseable, typed strings

Every §3.A natural-key fact gets one deterministic string encoding,
never a tuple/dict the caller must know the shape of: `symbol:<path>:
<name>:<kind>:<line>`, `vendor:<name>`, `doc:<path>`, `contract:
<contract_id>`, `check:<contract_id>:<check_id>`, `result:<contract_id>:
<check_id>:<run_id>`. Canonical `REQ-`/`CL-`/`EV-`/`OBS-`/`DE-`/`DEC-`
ids are used bare, unprefixed (already globally unique by this
project's own established convention). `get()`/`traverse()` dispatch
purely on the string's own shape (a fixed set of regexes), so a single
`record_id: str` parameter serves every identity kind — matching
`decisions/0079` §5's own qualified-reference precedent of a plain,
inspectable string rather than a structured object, and keeping the
public API surface to one scalar type throughout.

### 3. Read-only `context-graph.db` access never goes through `graph.open_graph`

`graph.open_graph` creates the database file if it doesn't already
exist and runs schema-migration `ALTER`/`UPDATE` statements as a side
effect of opening it — exactly the kind of incidental, surprising
mutation plan §6 ("no mutation path of any kind... no function in that
module issues an `INSERT`/`UPDATE`/`DELETE`") rules out, even though the
module's own explicit no-writer-import test (§7) only names
`knowledge_intermediate.py`/`oracle.py` and doesn't literally forbid
`graph.open_graph` by name. `knowledge_api.py` instead opens
`context-graph.db` with a plain `sqlite3.connect(f"file:{path}
?mode=ro", uri=True)`, the exact convention `scripts/
assess_change_impact.py` already established for a read-only external
target graph (`decisions/0086`). A missing or unreadable graph file is
treated as "no graph available" (`"empty"`, or a `derived_index` fact
reported `"unconfirmed"`) — never silently created. This means every
call to `knowledge_api.py` is safe to run against a project that has
never been synced at all, with zero filesystem side effect.

### 4. `project_root` is single-project-scoped; no new federation mechanism

Every public function takes one `project_root: Path`, used for both
`context-graph.db` and `planning/knowledge/`/`planning/contracts/` —
matching every existing `codecompass` command's own assumption
(`Path.cwd()` serves both roles today). A caller wanting a *different*
project's own source-symbol identity (the dogfood's own Ledgerkit
symbol resolution) simply calls `knowledge_api.get(ledgerkit_root, ...)`
as a second, independent, read-only call against that project's own
graph — exactly as a human or agent would run two separate `codecompass`
invocations from two separate directories today. This is deliberately
**not** a cross-project resolution feature inside the module itself
(no function accepts two project roots at once, no merged response
spans two projects) — Layer B/C federation (`decisions/0079`) remains
entirely out of scope, per plan §6.

### 5. `traverse`'s `relation` is a fixed, named vocabulary, not a query language

`relation` is one of: the four existing knowledge-record cross-reference
fields (`depends_on`, `supporting_evidence`, `contradicting_evidence`,
`observations`, plus `decision` for a Requirement's own cited Decision),
each with a `_reverse` counterpart; `cites`/`cited_by` (an Evidence's own
`source_ref`/`test_ref` target, and its reverse); `checks`/`results`
(contract → its checks, check → its results); `doc_mentions` (the
mechanical `doc_relations_edges` web, plan §4.3's migration target).
`depth > 1` repeats one more hop per level over whichever records were
just reached. This is deliberately bounded and enumerable — never a
general graph-query language, never an interprocedural call-graph walk —
matching plan §6's own exclusion and §4.E's "prefer a straightforward
deterministic design over speculative... new agent infrastructure."

### 6. `ContextPacket` — the plan's own deferred decision, now resolved

A fixed, non-negotiable priority order, never re-ranked by a heuristic
or an AI call: (1) the subject record itself; (2) its direct
`depends_on`/`depends_on_reverse`/`supporting_evidence`/
`contradicting_evidence` neighbours (one hop); (3) `trace_evidence`'s
own gaps for that one subject. Deduplicated by id as items are
collected (never the same record twice). Two independent, caller-
configurable bounds — `max_items` (default 20) and `max_chars` (default
6000, applied against each item's own rendered summary text) — enforced
by simply stopping once either is reached, in the fixed priority order
above, with `bounds.truncated` set to `True` whenever either bound was
actually hit, so a caller never mistakes a truncated packet for a
complete one. No embedding search, no relevance ranking, no token
counting against a real tokenizer — a deliberately simple, inspectable,
reproducible retrieval (`get_context_packet` called twice against
unchanged state returns byte-identical `items`), matching plan §4.E's
own explicit preference.

## Consequences

- Every call site (library callers, the six new `knowledge *` CLI
  commands, the migrated `query relations`) handles exactly one
  response shape (`ApiResponse`) and one identity shape (a plain
  string) — confirmed by `tests/test_knowledge_api.py` (47 tests) and
  the CLI's own `_print_api_response` helper, which renders any
  response without per-function branching beyond `status`.
- `knowledge_api.py` never creates `context-graph.db`, never migrates
  its schema, and is safe to call against an unsynced project —
  confirmed by `TestNoMutationPath::test_get_does_not_create_a_missing_
  context_graph_db`.
- `traverse`'s fixed relation vocabulary means a caller asking for a
  relation this project's own knowledge model doesn't actually have
  (e.g. a hypothetical "calls" relation) gets an explicit `"empty"` with
  a named-unknown-relation message, never a silent empty result that
  could be mistaken for "no edges of that kind exist."
- No change to `oracle.py`, `graph.py`, or `knowledge_intermediate.py` —
  every decision above is achieved by how `knowledge_api.py` calls their
  existing, unmodified public surface.

## Alternatives considered

- **A `ContextPacket` ranked by naive keyword relevance scoring against
  free text.** Rejected — plan §4.E explicitly prefers a deterministic
  design over "speculative ranking," and a scoring function would need
  its own test suite proving it doesn't silently drop something
  relevant; the fixed structural priority order needs no such proof,
  since it is just "follow the recorded relationships, in this order."
- **Passing raw `sqlite3.Connection`/tuple identities between library
  functions and the CLI**, mirroring `graph.py`'s own existing
  `conn`-threading convention. Rejected for this module specifically —
  a single, stable, string-typed identity is what a non-Python,
  machine-readable consumer (an agent, per plan §4's own "provide
  machine-readable output suitable for coding agents") can actually
  round-trip through JSON and a CLI argument unchanged.
