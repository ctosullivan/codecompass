# 0076. The clean-room sandbox is given a model-inference capability, never a credential — and a fixed, content-neutral context residual is accepted rather than engineered away

## Status

Accepted (2026-10-09/10, direct user instruction — Phase 81B Amendment
4). Implemented; the authoritative clean-room writer run this decision
unblocked has already completed successfully (see
`planning/retros/phase-81b-clean-room-redocumentation.md`'s own
"Amendment 4" section).

## Context

Phase 81B's original implementation reached a real, precisely-
characterised `BLOCKED` outcome
(`planning/phase-81b-mode-b-isolation-investigation.md`): a Linux
namespace/`pivot_root` mechanism was `VERIFIED` against every named
escape route — filesystem, `.git` history, network, credentials on disk
and in the environment, MCP, the orchestrating agent's own prior
context — except one. No AI documentation writer could be operated
inside that verified boundary at all, because doing so needs a model-API
credential, and this environment had no separately-scoped one to give
the sandbox. Giving the sandbox this session's own broader account
credentials would not have satisfied "credentials are genuinely
inaccessible" — it would just have been a different, still-real
credential crossing the boundary.

Two design questions needed resolving to unblock this without
weakening isolation:

1. **How does the sandbox get model output without ever holding a
   credential?**
2. **Investigation found that invoking the installed `claude` CLI, even
   fully isolated and with its environment sanitised, still attaches a
   fixed, non-suppressible reminder bundle to every call** (the
   authenticating account's email, today's date, a token-budget figure,
   OS/kernel type, a generic security-policy reminder) — no combination
   of documented CLI flags removed it. Is this residual acceptable, or
   does it disqualify the whole approach?

## Decision

**1. A narrowly-scoped broker process, not a credential, crosses the
boundary.** `scripts/cleanroom_broker.py` runs entirely outside the
sandbox, on the trusted host, and holds the real subscription
authentication (the existing, already-logged-in session —
`~/.claude/.credentials.json`, never copied, never bind-mounted
anywhere). It exposes exactly one capability to the sandbox, over a
local Unix-domain-socket IPC channel the sandbox cannot use for
anything else: a fixed `{system_prompt, messages} -> {ok, output,
usage}` protocol. The protocol has no syntax for a file path, a shell
command, a URL, or a tool/MCP config — not merely a runtime refusal of
one. Every request spawns a fresh, isolated `claude -p` subprocess
(new `--session-id`, `--restricted --strict-mcp-config --tools ""
--no-session-persistence --setting-sources ""`, an explicit
allow-list-only environment via `env -i`, never a deny-list), and the
broker's own response is sanitised against credential-shaped content
in any field before it ever reaches the socket.

This is a capability, not a credential, in the sense that matters: the
sandbox can ask for "one inference, given exactly this input" and
nothing else — it cannot extract, reuse, or exfiltrate anything that
would let it authenticate independently of the broker.

**2. The fixed account-level reminder residual is accepted as a named,
tested, non-disqualifying property — not engineered away.** Investigated
directly: this residual carries no CodeCompass-specific or project-
specific content (confirmed by a direct query from a genuinely neutral
working directory, and by a decisive canary test — a secret phrase
mentioned only in the live orchestrator conversation, never written to
any file, was unreachable from inside the sandbox). It is a harness/
account-level property of how the authenticating account's own session
attaches context to every inference call it makes, not a sandbox leak
specific to this mechanism, and not something any tested combination of
CLI isolation flags could suppress. Put to the user directly rather than
decided unilaterally (`CLAUDE.md` §1 — an assumption not already
settled): **accepted as an explicitly-named, regression-tested residual**
(`tests/test_cleanroom_broker.py`'s canary-adjacent tests), not silently
tolerated and not papered over by claiming perfect isolation.

## Alternatives considered

- **Give the sandbox this session's own broader credentials directly.**
  Rejected — explicitly named by the user's own governing prompt as not
  satisfying "credentials are genuinely inaccessible." Would have been a
  real, if differently-shaped, security regression.
- **Proxy the sandboxed writer's full agentic tool-use loop through the
  broker** (so the writer could browse its own evidence interactively
  rather than receiving it pre-assembled). Rejected as unnecessary scope
  expansion for this phase: the allow-listed evidence export comfortably
  fits a single large context-window request for a project of this size,
  and building a full tool-call proxy is a materially harder, riskier
  mechanism to verify than a fixed, narrow `{prompt} -> {output}`
  protocol. Left as an explicitly-named open problem for a much larger
  project in `docs/development/clean-room-redocumentation.md`'s own
  "Known, accepted limits" section, not solved here.
- **Treat the fixed reminder residual as disqualifying and leave Phase
  81B blocked a second time.** Rejected after direct investigation
  established the residual's own content-neutrality; the plan's own
  hard isolation gate (`decisions/0066` and this amendment's own §26.5)
  was not relaxed to reach this conclusion — the residual was evaluated
  against, and found not to violate, what that gate actually protects
  against (credential/project-content exposure), not merely declared
  acceptable to make the blocker go away.

## Consequences

- Phase 81B's authoritative writer run became possible and has already
  succeeded, producing a complete, real documentation reconstruction
  for both CodeCompass and `codecompass-template`
  (`planning/phase-81b-clean-room-redocumentation.md` §26,
  `planning/phase-81b-template-redocumentation.md`).
- The broker's own protocol is deliberately narrow and project-agnostic
  — reusable for a future clean-room run on a different project without
  redesign, per `docs/development/clean-room-redocumentation.md`'s own
  "Reusing this for another project" section.
- The fixed reminder residual is a permanent, documented property of
  this specific mechanism (reusing the installed `claude` CLI's own
  subscription session) — a future, materially different inference
  backend (e.g. a genuinely separate, narrowly-scoped API key) might not
  carry the same residual, but would need its own fresh investigation,
  not an assumption that this ADR's finding transfers.
