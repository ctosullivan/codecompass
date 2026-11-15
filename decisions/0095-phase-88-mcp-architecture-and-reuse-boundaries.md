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

## Amendment (2026-11-14): path confinement and the oracle-execution
trust model, corrected and made explicit

**Status note**: this amendment is appended, not an in-place rewrite —
positions 1-5 and the Context/Decision/Consequences/Alternatives above
are left exactly as originally accepted, matching the pattern
`decisions/0067` already established for a pre-implementation
correction (Phase 88 has not been implemented; nothing has shipped
under this ADR yet, so this amendment is still pre-implementation in
the same sense `decisions/0066`'s own first four amendments were).

A second governing task ("CodeCompass Orchestrator — Phase 88 Plan
Amendment and Independent Verification") found two real, independently
re-verified defects in how this ADR's own positions 3 and 5 were
originally stated — not a reversal of either position, a correction to
their completeness:

1. **Position 3 did not name `impact_classify_change`'s own
   `changed[].path` confinement gap.** Direct re-verification confirmed
   `resolve_changed_range` (`scripts/assess_change_impact.py:213-216`)
   joins `target_repo_root / changed.path` with zero rejection of an
   absolute path, a `..` component, or a symlink escape — the same
   class of problem position 3 already solved for `repo_root`/
   `check_reference`, just not extended to this parameter. **Decided**:
   the MCP wrapper (`security.py`) rejects any `changed[].path` that is
   absolute, contains `..`, or resolves (symlink-aware) outside the
   pinned `target_repo_root`, before any delegation — reusing
   `doc_compiler.py:566-568`'s and `git_topology.py:455-456`'s own
   existing confinement pattern, not a new mechanism. This extends
   position 3's own scope; it does not change its chosen mechanism
   (server-side pinning + validation-before-delegation).
2. **Position 3's framing of `oracle_execute_check` implied stronger
   containment than exists.** "Allowlisting" was stated without also
   stating that it bounds *which* check runs, not *what that check's
   own code does* once it runs — a materially incomplete trust-model
   description for a tool whose whole scenario is executing code a
   connected coding agent may have just written or modified. **Decided**:
   this ADR's own position 3 is read, from this amendment forward,
   together with the plan's own §5.2 trust-model paragraph (added this
   round): the target checkout is the least-trusted party in this
   model; `--enable-execution` is equivalent to granting the connected
   MCP client the ability to run `pytest` on this machine directly;
   Phase 88 implements no sandbox, container, or restricted user, and
   does not claim to. This does not change the decided mechanism
   (opt-in + allowlist + append-only result persistence) — it corrects
   the accuracy of what that mechanism is understood to guarantee.
3. **Position 5's timeout fix was necessary but incomplete.** Direct
   re-verification found `run_pytest_check`'s `subprocess.run(...,
   capture_output=True)` buffers the entire subprocess output in memory
   before any cap could apply, and that killing the pytest parent alone
   does not reach a descendant process it spawns. **Decided**: the same
   `oracle.py` change adds a bounded, read-while-running output cap
   (terminate early on breach, classify `INVALID`) and launches the
   subprocess in its own process group, killing the whole group on
   timeout or output-cap breach (POSIX `os.killpg`), not only the
   direct child — disclosed as addressing the common case, not a
   hermetic guarantee against every process-escape technique. This is
   an elaboration of position 5's own already-decided mechanism
   (an explicit, disclosed, `OSError`-pattern-matching timeout), not a
   different one.

No position's chosen mechanism is reversed by this amendment. The
plan's own §16 records the full six-finding list (two of which —
output-schema fidelity and the Ruff gate — are plan-level acceptance-
criteria corrections with no bearing on this ADR's own architectural
positions, so they are not duplicated here).

4. **Position 3's path-confinement scope did not reach `knowledge_
   get`'s own `symbol:` natural-key live-read step.** §16 (above, via
   the plan) correctly rejected a reviewer's claim that
   `knowledge_api._get_symbol` permits an arbitrary-unindexed-path
   probe — its SQL gate genuinely prevents that. A later, narrower
   re-examination (the plan's own §17) found that rejection correct on
   its own specific claim but incomplete: the SQL gate establishes only
   that a caller-supplied path *was once* legitimately indexed, not
   what currently exists at that location. Since a connected coding
   agent is already granted write access to the target checkout
   (position 3's own trust model, elaborated above), it can replace an
   already-indexed path with a symlink escaping `project_root` after
   sync, and `_get_symbol`'s live re-confirmation read
   (`knowledge_api.py:572-574`) had no confinement of any kind,
   disclosing the external target's freshly computed hash in its own
   `"stale"` response. **Decided**: `_get_symbol`'s live read is
   confined (`.resolve()`/`is_relative_to`, reusing position 3's own
   established pattern) and opened via `O_NOFOLLOW` rather than a
   plain, symlink-following read, so a final-component symlink
   substitution is refused atomically; a confinement failure or
   refused open reports `unconfirmed`, never a leaked hash. **A fresh
   independent reviewer then found this same defect shape recurs in
   two more call sites** — `_traverse_cites` and `find_gaps`'s
   evidence-scanning loop (`knowledge_api.py:969-987`/`1427-1434`),
   reached from the already-essential `knowledge_traverse`/
   `knowledge_find_gaps` tools, one of them disclosing actual parsed
   result fields rather than only a hash — contradicting this
   amendment's own first-draft claim that `_get_symbol` was the one
   exception. **Decided, corrected in place**: the same confinement +
   `O_NOFOLLOW` fix is shared by all three call sites via one new
   helper, plus one new optional, backward-compatible parameter on
   `oracle.parse_oracle_result` so the two YAML-parsing sites don't
   reopen the file a second time and reintroduce the same race. This
   extends position 3's own scope to three read paths it had not yet
   covered; it does not change any already-decided mechanism, and it
   does not touch `sync.py`'s own indexing walk (a separate,
   maintainer-trusted-action property, not reopened here) or any other
   existing caller of `oracle.sha256_file`/`oracle.parse_oracle_result`
   (used elsewhere under a different, already-accepted trust model, and
   unaffected since the new parameter defaults to the existing
   behaviour).
5. **Item 4's own "already covered by the `slug` allowlist" disposition
   for `find_gaps`'s `slug`-driven contract/results resolution was
   itself incomplete.** The allowlist (`_list_slugs`-membership) really
   does close a caller-supplied traversal *string* — unaffected by this
   item. It did not separately establish that a listed slug *name*'s
   own on-disk entry is confined to the knowledge/contracts root rather
   than a symlink, because `_list_slugs` (`knowledge_intermediate.py:
   2494-2498`) itself enumerates via `p.is_dir()`, which follows
   symlinks. **Decided**: `_list_slugs` is hardened to exclude a
   symlinked entry (`and not p.is_symlink()`), closing this at its
   source for every consumer that trusts its output; one new shared
   helper in `knowledge_api.py`, reusing position 3's own
   `.resolve()`/`is_relative_to` plus `O_NOFOLLOW` pattern (already
   extended for files in item 4), is applied at `find_gaps`'s own four
   raw-`slug` call sites (one in the knowledge tree, three in the
   contracts tree);
   `load_slug_records`/`_load_slug_results`/`_results_by_test_ref` each
   gain the same per-file symlink exclusion already specified for item
   4's three functions, so a symlinked file inside an otherwise-real
   slug directory is excluded, never read. This is a correction to
   item 4's own disposition, not a reversal of position 3's chosen
   mechanism (allowlist + confinement together, not either alone) —
   `_find_contract`'s own `contract_id`-keyed scan remains a named,
   out-of-scope residual requiring a trusted party's prior action,
   unchanged by this item, matching the already-accepted sync-time-
   symlink precedent in item 1's own elaboration above.

6. **Item 5's own confinement helper validated a path, then handed
   callers a `Path` they re-walked by name, undoing the descriptor-
   level guarantee for every access after the one validating open.**
   Decided: the helper now returns (via a context manager) an open
   directory file descriptor, not a `Path`; every subsequent child
   lookup (`load_slug_records`, `_load_slug_results`, `_results_by_
   test_ref`, `find_gaps`'s own four call sites) is performed relative
   to that descriptor (`os.scandir(dir_fd)`, `os.open(name, ...,
   dir_fd=dir_fd)`), so a substitution of the `slug` entry after the
   descriptor was opened cannot affect it — a genuinely persistent,
   not merely point-in-time, guarantee. Position 3's/item 4's file-
   level mechanism (`_read_confined_bytes`, open-then-read-in-one-step)
   needed no equivalent change, confirmed by re-reading it for this
   same defect shape. Separately, the Ledgerkit demonstration's
   documentation-use evidence is redirected from an admittedly-
   unrelated `docs_get_grounded_region` plumbing check to genuinely
   relevant `knowledge_get`-surfaced records (`EV-BFS-001`,
   `CL-BFS-004`, `CL-BFS-005`, `DEC-BFS-002`) that materially inform
   the task, independently checked for relevance; and `oracle_
   execute_check`'s MCP response schema is split into a fresh
   per-execution `outcome` (`PASS`/`FAIL`/`INVALID`) and a separately-
   derived `aggregate_state` (`PASS`/`GAP`/`NOT_REQUIRED`, via
   `aggregate_contract`, unchanged), correcting a schema that
   contradicted this project's own `decisions/0081` semantics. Full
   detail: plan §18.

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
