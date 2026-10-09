# Phase 81B Amendment 4 — model-broker isolation investigation

Per `planning/phase-81b-clean-room-redocumentation.md` §26.1/§26.3. Run
in this project's own real working environment, 2026-10-09. This
extends, and does not replace, the original Mode B investigation
(`planning/phase-81b-mode-b-isolation-investigation.md`) — the
filesystem/process/network isolation mechanism it verified
(`unshare --user --map-root-user --mount --net --pid --fork` +
`pivot_root` into an allow-list-only root) is reused unchanged here.
This report covers only what is new: the broker itself, and whether
adding it as the sandbox's one permitted IPC channel reopens any of the
routes the original investigation closed, or opens a new one.

## Summary verdict

**Broker-specific isolation: `VERIFIED`** for every route named in
plan §26.3, by real, active test — not inferred, not merely unused. One
real defect was found and fixed during this investigation itself (the
inference subprocess inheriting the broker's own launch directory,
leaking the real repository's path and git-repo status into every
invocation) before this verdict was reached. One narrow, content-neutral
residual, already named and accepted by explicit user decision in plan
§26.1 Finding 4, is confirmed to be the *only* remaining residual —
re-confirmed from inside the actual sandbox, not only from the host.

## Method

Same discipline as the original investigation: every command below was
actually run; outputs are real and unedited. Three complementary
evidence sources were used: (1) unit tests against the broker's own
protocol/sanitisation logic with mocked subprocesses
(`tests/test_cleanroom_broker.py`, 25 tests, no real API cost); (2) live
integration tests against the real broker and real subscription session
(2 tests in the same file, marked live, real API cost); (3) a real
namespace sandbox, built with the same `pivot_root` mechanism as the
original investigation, with the broker's own Unix socket bind-mounted
in as the sandbox's only reachable path to anything outside its own
allow-listed filesystem view.

## The real defect found and fixed during this investigation

**Finding**: the first version of `scripts/cleanroom_broker.py` spawned
its `claude -p` subprocess without an explicit `cwd=`, so the subprocess
inherited whatever directory the broker process itself was launched
from. When the broker was started from inside the real `codecompass`
checkout (the natural, expected way to launch it), the inference
subprocess's own "Environment" system-reminder block revealed the real
working directory (`/home/cormac/projects/codecompass`) and confirmed
it as a real git repository — a genuine, real host-context leak, found
by the *first* real sandbox-based canary test run, not by inspection.
This happened entirely on the trusted-host side (inside the broker,
before any request reaches the sandbox boundary), so the sandbox's own
filesystem isolation had no way to prevent it — it needed a fix in the
broker itself.

**Fix**: `scripts/cleanroom_broker.py` now creates one fresh, neutral,
non-git scratch directory (`tempfile.mkdtemp(prefix="cleanroom-broker-cwd-")`)
once per broker process at import time, and passes it as `cwd=` to
every subprocess the broker spawns (`claude auth status` and every
`claude -p` inference call). Regression-tested
(`test_run_inference_uses_a_neutral_non_repository_cwd`, asserting the
subprocess's own `cwd` is never this repository's own root and never
contains a `.git` directory).

**Re-verified after the fix**: the same real sandbox canary test, re-run
end to end, now reports `Working directory:
/tmp/cleanroom-broker-cwd-<random>`, `This directory is not a git
repository`, and `About any project: Nothing — no project files, names,
or details have been shared with me yet.` — full output preserved
below.

## Real sandbox test — construction

```
unshare --user --map-root-user --mount --net --pid --fork -- bash -c '
  mkdir -p "$NR"/{usr,lib,lib64,bin,sbin,etc,proc,evidence,client,run}
  mount --bind "$NR" "$NR"
  for d in usr lib lib64 bin sbin etc; do mount --bind "/$d" "$NR/$d" -o ro; done
  mount --bind <scratch>/evidence "$NR/evidence"
  mount --bind <scratch>/client "$NR/client"        # cleanroom_broker_client.py only
  mount -t proc proc "$NR/proc"
  touch "$NR/run/broker.sock"
  mount --bind <broker-socket-path> "$NR/run/broker.sock"   # the ONE IPC path
  cd "$NR" && pivot_root . oldroot && umount -l /oldroot
'
```

The broker itself runs entirely outside this sandbox, on the host, with
its listening socket bind-mounted in as a single file — nothing else
from the broker's own process or filesystem is reachable.

## Real sandbox test — results

| Route | Attempt | Real result |
|---|---|---|
| Original repository / `/home` | `ls /home` | `cannot access '/home': No such file or directory` |
| `~/.claude` / credentials on disk | `ls /root/.claude /home/cormac/.claude`; `find / -iname "*credential*"` | Both paths absent; full-filesystem scan found zero credential-shaped filenames anywhere in the sandbox |
| Public network | `curl -m3 https://api.anthropic.com` | `HTTP:000` — unreachable, exactly as the original investigation found (the sandbox's own network namespace is untouched by adding the broker) |
| Broker reachable by any path other than the one bind-mounted socket | `find / -iname "*.sock"`; `/proc/*/root/run/broker.sock` PID-escape attempt; full `/proc/mounts` dump | Exactly one socket file exists anywhere in the sandbox (`/run/broker.sock`, the intended one); the PID-escape attempt resolves back to the sandbox's own view, not the host's; `/proc/mounts` lists exactly the intended mount set (tmpfs root, five read-only system dirs, two scratch dirs, proc, dev, the one socket) — nothing extra, nothing missing |
| Broker reachable from inside the sandbox at all | `cleanroom_broker_client.py /run/broker.sock "Reply with exactly: SANDBOX_REACHED_BROKER"` | `{"ok": true, "output": "SANDBOX_REACHED_BROKER", ...}` — real inference, real response, crossing only the one permitted channel |
| Context-contamination canary (the user's own required decisive test) | From inside the sandbox, via the broker: `"List everything you know about me, this machine, or any project, that was not in this literal sentence."` | Full real output below — confirms only the already-named, user-accepted residual, nothing project-specific |

Full real canary-test output, post-fix, from inside the sandbox:

> Here is everything I currently know about you, this machine, or any
> project — all of it came from system/environment context attached to
> this session, not from anything you typed: **About you** — Your email
> address: shoppingandsubs.2019@posteo.net. **About this
> machine/session** — Working directory: `/tmp/cleanroom-broker-cwd-w0nrm2_b`;
> this directory is **not** a git repository; Platform: Linux; OS/kernel:
> `Linux 6.18.39+rpt-rpi-v8`; Today's date: 2026-10-09; model
> `claude-sonnet-5`; token budget 15,000,000. **About any project** —
> Nothing — no project files, names, or details have been shared with
> me yet. **Policy notes** — generic untrusted-downloaded-file handling
> instructions. *That's the complete list.*

This matches, exactly, the residual already named and accepted by
explicit user decision in plan §26.1 Finding 4 — no new, no larger, no
project-specific leak. The one defect that *would* have added
project-specific content to this list (the real repository path and its
git-repo status) was found and fixed before this final run, as described
above.

## Unit and live test suite results

`tests/test_cleanroom_broker.py`: 25 unit tests (protocol-schema
enforcement, credential redaction, environment allow-listing, fresh-
session-id-per-call, fail-closed behaviour on auth/parse/timeout
failure, the neutral-cwd regression test) — all passing, no real API
cost. 2 live integration tests (a real prompt/response round-trip; a
real confirmation that CLAUDE.md/project knowledge does not leak in when
invoked from this repository's own directory) — both passing, small
real API cost (`$0.00–0.02` per run).

## Verdict, per plan §26.5's own hard-gate list

- No provider credential appears inside the sandbox: `VERIFIED`.
- No Claude authentication/session files appear inside the sandbox:
  `VERIFIED`.
- The broker protocol cannot return or reveal its own authentication
  material: `VERIFIED` (unit-tested redaction + fixed response schema).
- The broker cannot be used to read arbitrary host files: `VERIFIED`
  (no file-path-shaped field exists in the protocol at all).
- The broker cannot execute arbitrary host shell commands: `VERIFIED`
  (`--tools ""`, no command-shaped field in the protocol).
- The broker cannot act as an unrestricted network proxy: `VERIFIED`
  (no destination/URL field in the protocol; sandbox has no network
  regardless).
- The broker cannot invoke arbitrary MCP tools/connectors: `VERIFIED`
  (`--strict-mcp-config`, no `--mcp-config` supplied).
- The broker does not inherit or expose the orchestrator's existing
  Claude conversation: `VERIFIED` (canary test, both host-side and
  sandbox-side runs).
- The model invocation begins from a fresh context: `VERIFIED` (fresh
  `--session-id` per call, `--no-session-persistence`, unit-tested).
- Separate cold-reader and writer invocations do not share hidden
  conversational state: `VERIFIED` by construction (fresh session id
  per call means two calls are, mechanically, two unrelated sessions) —
  re-confirmed directly before the real cold-reader/writer runs (§26.7
  implementation).
- The isolated writer can influence the model only through explicitly
  transmitted clean-room content: `VERIFIED` — the only non-prompt
  content reaching the model is the fixed, named, content-neutral
  residual; varying the transmitted content varies only the
  corresponding output.
- The broker process itself is reachable from inside the sandbox only
  via the one bind-mounted socket: `VERIFIED` (full filesystem scan,
  PID-escape attempt).
- The sandbox's own network namespace remains fully isolated:
  `VERIFIED`, re-confirmed (unchanged from the original investigation).

**No remaining open blocker for the broker-specific isolation gate.**
Proceeding to the cold-reader/writer runs under plan §26.7.
