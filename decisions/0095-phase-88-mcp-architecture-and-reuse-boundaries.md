# 0095. Phase 88 MCP server: official SDK over stdio, read/execute
separation via server-side repo-root pinning and contract-file
allowlisting, change-impact logic relocated into `src/` rather than
accepted as maintainer-only, and a new oracle execution timeout

## Status

Accepted (2026-11-12, direct user request — "CodeCompass Orchestrator —
Phase 88 Planning"). Planning only: this ADR authorises no
implementation. Governed by `decisions/0084`/`0085` (the v2 roadmap
realignment that created and then split this phase) and
`planning/v2-roadmap.md` §88, neither of which this ADR reopens.

## Context

Phase 88 ("Agent Integration and MCP") must expose existing
CodeCompass capabilities — Phase 84's knowledge API, Phase 82's oracle
execution, Phase 83's change-impact assessment, Phase 87's
documentation layer — to external coding agents through a standard
Model Context Protocol (MCP) interface, without duplicating any of
that logic inside the server itself (`decisions/0085` §3's explicit
constraint) and without introducing a security regression. Five
non-obvious tradeoffs were decided during planning, verified against
the real source and real external research, not assumed:

### 1. MCP SDK choice: the official `mcp` package, not a leaner alternative

The official Python MCP SDK (PyPI package `mcp`, MIT-licensed, Python
3.10+ floor) is the spec-reference implementation other MCP-capable
clients are built and tested against, but pulls a non-trivial
transitive dependency tree (pydantic/httpx/anyio-family packages).
Leaner third-party implementations (e.g. `chuk-mcp`) exist with a
much smaller footprint. **Decided**: adopt the official SDK. Phase
88's own governing requirement (`planning/v2-roadmap.md` §88;
governing task §6) is explicit cross-client compatibility with any
MCP-capable host, including a hypothetical Orchestrator.inc-style
client — a non-reference implementation risks subtle protocol
divergence that would only surface against a client this project
cannot test against directly. The dependency-weight cost is accepted
and named (`planning/phase-88-agent-integration-mcp.md` §7, §14) as a
revisit trigger if the real transitive tree proves unacceptably heavy
at implementation time. MIT is permissively compatible with this
project's own `GPL-3.0-or-later` licensing as a dependency.

### 2. Transport: stdio first, no premature HTTP/SSE server

The governing task's own §4 instruction ("prefer an initial local
stdio transport unless investigation establishes a compelling
alternative") was investigated, not merely accepted: Claude Code (the
first, mandatory client) spawns local MCP servers over stdio as its
primary supported mechanism, and nothing in this phase's own
read-mostly, locally-scoped design needs a network listener. No
compelling alternative was found. **Decided**: stdio only for Phase
88; an HTTP/SSE transport is not built, named as plausible future work
only if a genuinely remote client emerges (none is scoped for Phase
88-91).

### 3. Read/execute separation enforced by server-side repo-root
pinning and contract-file allowlisting, not by trusting caller input

The governing task's §5 names "strict separation between read-only
knowledge retrieval and privileged oracle execution" and "explicit
allowlisting of executable contracts/checks" as mandatory. Direct
source verification of `src/codecompass/oracle.py::evaluate_check`
confirmed it is generic over any `(contract, check, repo_root)` triple
— nothing internal to it prevents an MCP tool from passing an
arbitrary, caller-supplied `repo_root` or a synthesised `check_
reference`. **Decided**: the MCP server itself never accepts a
filesystem path from a tool call for either `repo_root` or `target_
repo_root` — only a symbolic key resolved against a fixed mapping
given at server startup by whoever launches the process. Similarly,
`oracle_execute_check` resolves `(slug, contract_id, check_id)` only
against the real, committed `planning/contracts/<slug>/oracle-
contract.yaml` on disk — the contract file *is* the allowlist, with no
separately-maintained list that could drift out of sync with it. This
mirrors Phase 82's own existing discipline (contracts as the single
source of truth for what's required) rather than inventing a parallel
permission model.

### 4. `scripts/assess_change_impact.py`'s core logic is relocated into
a new packaged module, not exposed as a second maintainer-only
capability

Phase 87D (`planning/retros/phase-87-stage-87d-deterministic-
reference-assurance.md`) already found, reproduced, and disclosed that
`scripts/` is excluded from the installed wheel
(`pyproject.toml`'s `[tool.setuptools.packages.find] where = ["src"]`),
making `docs compile` maintainer-only by mechanical necessity. Direct
source verification this session confirmed `scripts/assess_change_
impact.py` (Phase 83's change-impact tool) carries the identical
packaging exclusion and is not wired into `cli.py` at all today. Unlike
`docs compile` (which also triggers a real paid Anthropic API call and
is correctly maintainer-only on that independent ground too),
change-impact assessment has no such independent reason to stay
maintainer-only — and the governing task's own §2 objective names
change-impact assessment as one of Phase 88's essential MVP
capabilities. Silently accepting a second, undisclosed maintainer-only
gap for an explicitly essential capability would repeat exactly the
kind of imprecise disclosure Phase 87D's own corrective work already
corrected once. **Decided**: `scripts/assess_change_impact.py`'s core
functions (`resolve_changed_range`, `resolve_intersecting_symbols`,
`classify_symbol`, the `--run-checks` classification logic) are
relocated, behaviour-unchanged, into a new packaged module
`src/codecompass/change_impact.py`; `scripts/assess_change_impact.py`
becomes a thin CLI wrapper importing from it, preserving the existing
maintainer entrypoint exactly. This is a relocation for packaging
reach, not a reimplementation — `decisions/0085` §3's prohibition on
duplicating Phase 83's *logic* inside the MCP server is satisfied
because the logic itself does not change or get rewritten, only where
it physically lives. `scripts/check_self_knowledge_quality.py`/
`check_knowledge_placement.py` are deliberately **not** relocated by
this same reasoning — `knowledge_api.find_gaps` (already packaged)
already satisfies the governing task's named "knowledge gaps" MVP
requirement, so promoting these two scripts' additional checks is real,
separable, non-essential future work, not silently built here.

### 5. A new, previously-absent subprocess timeout in `oracle.py`

Direct source verification confirmed `oracle.py::run_pytest_check`'s
`subprocess.run` call has no `timeout=` argument today — a tolerable
gap when every caller is a maintainer at a terminal who can interrupt
a hang themselves (every existing caller: `scripts/run_balance_from_
spec_oracle.py`, `check_contracts.py`, `scripts/assess_change_
impact.py`), but a genuine resource-exhaustion exposure once a remote
MCP tool call (`oracle_execute_check`) can trigger the same subprocess
without any human present to interrupt it. The governing task's §5
names "bounded resource consumption, timeouts and output limits" as a
mandatory security design requirement. **Decided**: add an explicit,
configurable timeout around the existing `subprocess.run` call,
catching `subprocess.TimeoutExpired` and classifying it `INVALID` —
following the exact pattern `run_pytest_check` already uses for a
launch `OSError`, rather than inventing a new outcome category. This
is the narrowest correction identified for this real gap (governing
task §5's own "identify the narrowest correction necessary"
instruction), not a redesign of `oracle.py`'s execution model.

## Decision

Adopt all five positions above for Phase 88's implementation-ready
plan (`planning/phase-88-agent-integration-mcp.md`). None of these
reopens `decisions/0078`-`0094` or Phase 82-87's own already-`done`
design; each is additive, scoped to this new phase, or a narrow,
disclosed correction to a real, independently-verified gap in existing
shared code (`oracle.py`'s timeout) carried forward unchanged in every
other respect.

## Consequences

- `pyproject.toml` gains a new runtime dependency (`mcp`) — its
  `CLAUDE.md` dependency-table consequence (a new row) requires
  separate, explicit `CLAUDE.md` §0 approval before that file is
  edited; this ADR does not pre-approve it.
- `oracle.py`'s new timeout parameter is a behavioural change to
  already-shipped, Phase 82-86-relied-upon code; its own existing test
  suite must be re-confirmed unchanged for normal-speed execution, plus
  one new regression test for the timeout path itself, before this is
  considered safe to ship.
- `scripts/assess_change_impact.py`'s relocation changes which module
  owns the real logic; its own 27+ existing tests must be re-run
  against the relocated code with identical results, plus one new test
  confirming the thin CLI wrapper's own output is unchanged pre/post
  relocation.
- A future MCP transport beyond stdio, or exposure of `check_self_
  knowledge_quality.py`/`check_knowledge_placement.py` beyond what
  `knowledge_api.find_gaps` already covers, remains open, undecided
  future work — not authorised or precluded by this ADR.

## Alternatives considered

- **Accept `scripts/assess_change_impact.py` as a second, disclosed
  maintainer-only capability**, matching `docs compile`'s own
  precedent exactly, instead of relocating it. Rejected: `docs
  compile`'s maintainer-only status rests on two independent grounds
  (packaging exclusion *and* a real paid-API call it makes) — only the
  first applies here, and accepting a packaging-only restriction on an
  explicitly-named-essential MVP capability, when the fix is a
  behaviour-preserving relocation rather than new development, is a
  materially weaker outcome for no real savings.
- **A leaner, non-reference MCP library** (`chuk-mcp` or a from-scratch
  stdio implementation). Rejected for this phase on cross-client-
  compatibility grounds (see position 1); named as a reconsideration
  trigger if the official SDK's real dependency weight proves
  unacceptable.
- **Trust caller-supplied `repo_root`/`check_reference` directly**,
  validating only that the path exists. Rejected: this is exactly the
  "arbitrary execution target" shape the governing task's §5 explicitly
  requires confinement against; a symbolic, server-pinned key with no
  caller-controlled path component is a strictly stronger, still simple,
  boundary.
- **Leave `oracle.py` untouched and enforce a timeout only at the MCP
  wrapper layer** (killing the whole tool call after N seconds without
  the subprocess itself being bounded). Rejected: an orphaned, still-
  running `pytest` subprocess would persist after the MCP call
  returns, continuing to consume resources and potentially still
  writing to the real target repo's test artifacts — the timeout must
  bound the actual subprocess, not merely the tool call that launched
  it.
