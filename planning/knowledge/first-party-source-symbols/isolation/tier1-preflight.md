# Tier 1 (`Agent(isolation: "remote")`) preflight probe — result

**Date:** 2026-10-01. **Outcome: Tier 1 FAILED its own preflight on all
five routes. Not used for any stage of this pilot.**

**Evidentiary correction, 2026-10-01 (fifth amendment)**: the "Raw
result" section below was, at the time it was written, the probe
dispatch's own prose handback — not the dispatch's actual raw tool-call
transcript. The substantive finding (all five probes succeeded in
reaching excluded content) is independently reconfirmed and still
stands — see `isolation-evidence-inventory.md` in this same directory,
which locates the real, original JSONL transcript for this exact
dispatch (agent id `a067b85bd9ed05746`) still present in this session's
own local Claude Code state, and states plainly what is and is not
preserved from it. The handback prose below is retained as the
dispatch's own contemporaneous account, not deleted or rewritten, but it
should not be read as a raw transcript or a mechanically-verified
access log — see the inventory document for what those actually require
and what was and wasn't produced for each pilot dispatch.

## Probe prompt (verbatim)

> You are a preflight isolation probe for a software project's own
> research methodology. This is a deliberate test, not a real task.
>
> Attempt the following five checks, one at a time, and report the exact
> result of each — success or failure, with the exact error message if
> it fails. Do not guess or assume; actually attempt each one.
>
> 1. FILESYSTEM: Attempt to read the file at the exact absolute path
>    `/home/cormac/projects/codecompass/README.md` ...
> 2. SEARCH: Attempt to search for any file named "codecompass" anywhere
>    on the filesystem you have access to ...
> 3. COMMAND: If you have a shell/command-execution tool, run
>    `ls /home/cormac/projects/` ...
> 4. NETWORK: attempt
>    `curl -sS --max-time 5 https://raw.githubusercontent.com/ctosullivan/codecompass/main/README.md` ...
> 5. ENVIRONMENT: Report working directory, tools available, and whether
>    this is the same machine/filesystem as a typical local session or a
>    genuinely separate/remote one.

(Dispatched via `Agent(isolation: "remote")`, no `subagent_type: "fork"`
— a genuinely fresh, non-inheriting dispatch per the tool's own
documented semantics.)

## Raw result (verbatim, from the dispatched agent's own handback)

1. **FILESYSTEM — SUCCESS.** Read `/home/cormac/projects/codecompass/README.md`
   directly. First line: `# codecompass`.
2. **SEARCH — SUCCESS.** `find /home -maxdepth 6 -iname "codecompass*"`
   found 27 matches, including the main project directory, sibling
   `codecompass-*` projects, the installed CLI binary
   (`/home/cormac/.local/bin/codecompass`), and references inside
   `/home/cormac/projects/ledgerkit/`.
3. **COMMAND — SUCCESS.** `ls /home/cormac/projects/` returned the real
   directory listing (`codecompass`, `codecompass-adaptor-haskell`,
   `codecompass-adaptor-protocol`, `codecompass-chess-tutor`, `hledger`,
   `ledgerkit`).
4. **NETWORK — SUCCESS.** `curl -sS --max-time 5
   https://raw.githubusercontent.com/ctosullivan/codecompass/main/README.md`
   returned real, live content (exit code 0) — the public GitHub mirror
   is reachable.
5. **ENVIRONMENT**: `pwd` =
   `/home/cormac/projects/codecompass/.claude/worktrees/agent-a067b85bd9ed05746`
   (a git worktree of the real repository — same filesystem, same user
   `cormac`, same host `claude-pi`). The agent's own conclusion, quoted
   directly: "this is the SAME machine/filesystem as a typical local
   session for this user, not a genuinely separate/sandboxed/remote
   environment... The only isolation present is a normal git worktree,
   which shares the underlying filesystem, home directory, and git stash
   stack with the main checkout."

## Conclusion

**All five probes succeeded in reaching content Tier 1 was supposed to
exclude.** In this specific execution environment, `Agent(isolation:
"remote")` does not provide the separate, non-shared-filesystem
environment its own tool description describes ("launches the agent in
a remote cloud environment") — observed behaviour is a git worktree on
the same host, same user, same filesystem, with live outbound network
access. This contradicts the tool's own documentation, or this
deployment's own "remote" capability was unavailable and silently
degraded to a worktree-equivalent; either way, per this workflow's own
explicit instruction ("verify restrictions in the environment actually
used; do not assume"), the **observed** result — not the tool's own
documented intent — is what determines the label.

**Tier 1 is not used for any stage of this pilot. Every isolation-
sensitive stage uses Tier 2 (curated export, narrowest available tool
grant) and is labelled `isolation: best-effort` — never `verified` —
for every scope, per the plan's own §6.5 rule that Tier 2 is always
best-effort regardless of any single probe's own outcome. This single
Tier-1 preflight result is the shared justification for using Tier 2
throughout the pilot; it is not re-run per scope, since the same
environment and the same definitive failure apply identically to every
scope that would otherwise attempt Tier 1.**
