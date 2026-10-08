# Phase 81B — Mode B isolation investigation

Per `planning/phase-81b-clean-room-redocumentation.md` §6.3's own
required first implementation step. Run in this project's own real
working environment, 2026-10-08. This is **investigation/retro evidence
only** (per Amendment 3, third revision) — it is not, and does not claim
to be, the durable repeatable-workflow document
(`docs/development/clean-room-redocumentation.md`), which is published
only once a verified full redocumentation run has actually succeeded
(§17/§18 item 13). This report is linked from the phase retro.

## Summary verdict

**Mechanical isolation: a materially stronger result than Phase 79/80's
own `UNMET` finding — every named escape route except one was
successfully, mechanically closed and actively verified, not merely
unused.** **Authoritative writer run: still `BLOCKED`**, for a distinct,
precisely-identified reason: there is no way, in this environment, to
provision a documentation-writing process (necessarily an LLM-API-backed
agent, since no local/offline model exists here) with its own model-API
credential without either reusing this session's own broader account
credentials — which would not constitute "credentials are genuinely
inaccessible" — or requiring an external resource (a separately-scoped
API key) this environment does not have.

This is not the same finding as Phase 79/80's own `UNMET` — it is a
narrower, more precise one: the *isolation mechanism itself* is now
`VERIFIED` against every tested route except model-API credential
provisioning, which is a categorically different problem (an
infrastructure/provisioning gap, not an isolation-boundary gap) that the
original planning investigation (§1.4) already flagged, by name, as an
open sub-problem before this investigation began.

## Method

Per `decisions/0066`'s own five-route preflight protocol, extended with
the backlog item's own required *active* escape attempts (not passive
probing), run against a disposable, scratch fixture — never against real
project content or a real clean-room branch. Every command below was run
directly; outputs are the real, unedited results.

### Candidate mechanism

Linux namespaces (`unshare --user --map-root-user --mount --net --pid
--fork`), combined with `pivot_root` into a freshly-constructed root
containing only explicitly bind-mounted system directories
(`usr`/`lib`/`bin`/`sbin`/`etc`, read-only) plus two allow-listed
directories (`/evidence`, `/output`) — an **allow-list** construction, not
a deny-list. `busybox` (already present in this environment) was
available as a fallback minimal toolchain; the real system directories
were used instead once the bind-mount approach worked, since a real
writer needs a real, working toolchain (Python, test runners, etc.) to
satisfy the plan's own "writer may run local project commands" allowance
(§6.4).

### Attempt 1 — deny-list (rejected after testing)

First attempt: a single shared mount namespace with `tmpfs` mounted
*over* the real project checkout and `~/.ssh`/`~/.claude`, everything
else left as-is. Real result:

```
--- 2. parent paths: can it see another checkout? ---
codecompass
codecompass-adaptor-haskell
codecompass-adaptor-protocol
codecompass-chess-tutor
codecompass-template
hledger
ledgerkit
```

**A real, genuine escape**: hiding the one checkout did nothing for its
siblings — a deny-list approach requires enumerating every path to
block, is fragile by construction, and is exactly the "separate directory
or an instruction alone does not qualify" posture
`strict-isolation-for-documentation-reconstruction.md` already warns
against. **Rejected.**

### Attempt 2 — allow-list via `pivot_root` (succeeded)

```
NR=<scratch>/newroot
mount --bind "$NR" "$NR"                      # make it its own mountpoint
mount --bind /usr "$NR/usr" -o ro              # (same for /lib /lib64 /bin /sbin /etc)
mount --bind <scratch>/evidence "$NR/evidence"
mount --bind <scratch>/output "$NR/output"
mount -t proc proc "$NR/proc"
cd "$NR" && pivot_root . oldroot && umount -l /oldroot
```

Real results, each independently, actively attempted (not merely
unused):

| Route | Attempt | Real result |
|---|---|---|
| Filesystem (original repo) | `ls /home/cormac/projects/codecompass` | `/home` does not exist in this view at all |
| Parent-path traversal | `ls /evidence/..`, sibling checkouts | Resolves to the sandbox's own root; sibling checkouts (`codecompass-template`, `hledger`, `ledgerkit`, etc.) not reachable by any path |
| `.git` history/objects | `find / -iname ".git"` | Empty — no `.git` directory exists anywhere in the sandbox |
| Other branches / Git remotes | (implied by no `.git` existing at all) | N/A — nothing to check out from |
| Public GitHub / network | `curl -m3 https://github.com` | `HTTP:000`, curl exit 6 ("could not resolve host") — DNS resolution itself fails, not just the connection |
| Credentials/SSH keys (filesystem) | `ls /root/.ssh`, `cat /etc/passwd` | No SSH keys present anywhere; `/etc/passwd` shows only the ordinary system user table, no secret |
| Credentials (environment) | `env \| grep -iE "token\|key\|secret\|credential"` | **Found one real leak on the first attempt**: `CLAUDE_CODE_MESSAGING_TOKEN` inherits into the sandboxed process's environment unless explicitly cleared — namespace isolation does **not** sanitize environment variables by itself. **Fixed**: launching with `env -i PATH=/usr/bin:/bin ...` (an explicit, minimal environment) instead of a bare `unshare ... -- cmd` removes every credential-shaped variable — re-tested, confirmed zero matches and only 4 harmless variables (`PWD`, `SHLVL`, `PATH`, `_`) remain. |
| MCP/connectors | `find / -iname "*mcp*"` | Only unrelated kernel driver files for Microchip MCP23xxx/MCP251x hardware peripherals (GPIO/CAN chips) — zero Model Context Protocol configuration anywhere, consistent with there being no `/home` at all |
| Agent/project shared context | `find / -iname "*.claude*"` | Empty — no Claude Code session state, config, or memory reachable; a process started this way is a genuinely fresh OS process with no inherited conversation state by construction |
| PID-namespace / `/proc` escape | `ls /proc` (only real sandbox PIDs 1/14/15 visible), `ls /proc/1/root/`, `ls /proc/self/root/../../../..` | Only the sandbox's own 3 processes visible; both classic `/proc`-based container-escape attempts resolve back to the sandbox's own root, not the host's |
| Output boundary | write to `/output/test.txt`, read back | Works — the writer has a genuine, separate place to put its own output |
| Evidence boundary | read `/evidence/README.md` | Works — the allow-listed content is genuinely reachable |

**Every one of these routes is now `VERIFIED` closed** by active,
documented attempt — not inferred, not merely unused.

## The one remaining, unresolved blocker

A real documentation-writing agent in 2026 is, in practice, backed by a
large language model reached over a network API (this project has no
local/offline model available — checked directly: no `ollama`,
`llama.cpp`, or local model weights found anywhere in this environment).
Operating such a writer **inside** the verified sandbox above requires
granting it exactly two things the sandbox otherwise correctly denies to
everything else:

1. **A scoped network route** to the model provider's own API host —
   technically achievable (a network namespace with only that one
   destination routable, rather than zero destinations), not yet built
   or tested in this investigation since item 2 below makes it moot for
   now.
2. **A credential** to authenticate to that API. This environment has no
   separately-provisioned, narrowly-scoped API key (`ANTHROPIC_API_KEY`
   or equivalent) distinct from this session's own broader Claude Code
   account credentials — confirmed directly: no such environment
   variable exists, and the `claude` CLI's own authentication is tied to
   this session's own account state (`~/.claude/`), not a portable,
   independently-scoped secret. Provisioning the sandbox with this
   session's own credentials would not satisfy "credentials are
   genuinely inaccessible" — it would just be a different, still-real
   credential crossing the boundary, defeating the point.

**Without a separately-scoped model-API credential, no AI writer can be
operated inside the verified boundary at all** — not "operated with
weaker isolation," but not operated. This is a provisioning/
infrastructure gap, categorically distinct from an isolation-mechanism
gap, and was already named as the one real open sub-problem during Phase
81B's own planning stage (§1.4: "if the writer itself is an AI agent, it
needs some network path back to its own model provider to function at
all — 'no network' and 'no agent' are the same outcome").

The plan's own §6.3 outcome 2 names two possible paths around this
problem: a fully offline/local writer (confirmed unavailable, checked
directly above), or a human operating the isolated shell directly
(not available to an autonomous orchestrator — there is no human
performing this phase's own implementation). Neither is available here.

## Verdict, per the plan's own required four-way separation (§21 point 4)

- **Isolation**: `VERIFIED` for every tested route except model-API
  credential provisioning, which is not an isolation-boundary question —
  a materially stronger, more complete result than Phase 79/80's own
  `UNMET` (which failed even the passive preflight on every route).
- **Workflow completion**: not attempted — gated on the authoritative
  writer run, which cannot proceed (see below).
- **Documentation accuracy / coding-context usefulness**: not applicable
  — no writer run occurred.
- **Authoritative redocumentation run**: **`BLOCKED`**, per
  `planning/phase-81b-clean-room-redocumentation.md` §6.3/§18's own hard
  gate — the isolation mechanism itself is proven, but no real writer can
  be operated inside it in this environment. Per Amendment 3 (third
  revision), `docs/development/clean-room-redocumentation.md` is **not**
  created or published as a result of this investigation, in any form.

## What would unblock this

Either (a) a separately-provisioned, narrowly-scoped model-API credential
(e.g. a dedicated `ANTHROPIC_API_KEY` with no other account privileges)
becomes available in this project's own working environment, allowing
the scoped-egress design in §6.3 outcome 1 to actually be built and
tested, or (b) a genuinely local/offline model becomes available,
allowing the fully-offline-writer path in §6.3 outcome 2. Either
satisfies the backlog item's own "a genuinely separate execution
substrate becomes available" revisit trigger on its own terms — the
namespace/`pivot_root` mechanism documented here is the substrate; what's
missing is a way to run a real writer inside it.

## Confirmation against the real clean-room branch

The same mechanism was re-confirmed against **real** content, not only
the disposable fixture above: the real `cleanroom/redoc-46601a1` branch
(`handoff_commit` `468cffa4e013e56ad17df6c7536dd32a5774cd4b`, pushed to
`origin`) was extracted via `git archive` and placed inside a fresh
instance of the same namespace/`pivot_root` sandbox. Results: the real
handoff content (`planning/documentation-handoff/README.md` and the rest
of the real allow-listed tree) was readable exactly as expected; `/home`
did not exist (the original repository checkout genuinely unreachable);
`curl -m3 https://github.com` returned `HTTP:000` (network genuinely
blocked). This closes the gap between "the mechanism works in the
abstract" and "the mechanism works for CodeCompass's own real clean-room
branch specifically."

A real, genuine implementation bug was also found and fixed during this
step: the first build of the clean-room tree used a raw filesystem walk
(`shutil.copytree`), which silently included three local, `.gitignore`d,
regenerated test-fixture artifacts
(`tests/fixtures/ledgerkit_lifecycle_demo/{CLAUDE.md,context-graph.db,vendor.toml}`)
that exist on disk locally but are not tracked by Git at all — the
manifest claimed they were included, but `git add -A` correctly refused
to commit them, and the branch validator's own "manifest-listed path is
missing" check caught the resulting mismatch immediately. Fixed by
switching `scripts/prepare_cleanroom_branch.py` to build its file list
from `git ls-files` rather than a raw directory walk, so the manifest can
never claim more than what a real commit would actually contain. Re-run
end to end after the fix: `git archive` → validator → `PASS`, zero
findings.

## Disposable fixtures used

All testing was performed against a scratch directory under this
session's own scratchpad (never a real clean-room branch, never real
project content) — deleted at the end of this investigation, leaving no
trace in either the real repository or any real branch.
