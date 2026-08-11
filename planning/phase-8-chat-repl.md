# Phase 8: Single-vendor chat REPL

## Scope

**Covered:**
- `src/depcompass/chat.py` (new) — grounding + conversation loop for
  `depcompass chat <vendor>`:
  - `_build_system_prompt(vendor_dir, config)` — reads
    `vendor/<name>/CLAUDE.md` (required) and `vendor/<name>/OVERVIEW.md`
    (optional) as raw text and assembles the system prompt
    (`decisions/0023`).
  - `_call_anthropic(system_prompt, messages)` — one plain multi-turn
    text-completion call against `claude-haiku-4-5-20251001`
    (`decisions/0003`), no forced tool-use. The monkeypatch seam tests
    replace, mirroring `grounded_description._call_anthropic`
    (`decisions/0016` — never a live call in tests).
  - `ChatError` — raised when a vendor was never synced (no
    `vendor/<name>/CLAUDE.md`) or the API call fails.
  - `run_chat(config, project_root, console)` — the REPL loop itself:
    context-indicator line, prompt/response loop via Rich, clean exit on
    `exit`/`quit`/EOF/`Ctrl-C`.
- `src/depcompass/cli.py` — real `chat <vendor>` command replacing the
  `_not_implemented("chat")` stub; removes `"chat"` from
  `_PHASE_BY_COMMAND`.
- Tests: `tests/test_chat.py` (new) — `_build_system_prompt` grounding
  variants, `_call_anthropic` request/error shape, CLI integration via
  `CliRunner` with scripted stdin.
- Same-commit doc updates: `docs/cli-reference.md`, `README.md`,
  `architecture/overview.md` (mark explicit-vendor `chat` implemented),
  `planning/ROADMAP.md`, `planning/CONTEXT.md`, `CHANGELOG.md`.

**Explicitly deferred:**
- Bare `depcompass chat` project-root mode, Tier 1/2 routing, and the
  whole-project dependency rollup — Phase 9 (`decisions/0012`,
  `decisions/0013`; ROADMAP Post-MVP row 9). This phase builds only
  explicit single-vendor mode.
- Streaming responses.
- Conversation-length/token capping or truncation for long sessions.
- Cumulative-cost display or budget gating for chat turns — each turn is
  a small Haiku call the user explicitly triggers by typing; revisit if
  real usage shows a need.
- A Cursor-side equivalent of `chat` — out of scope entirely (Cursor has
  no REPL concept to hook this into), not deferred to a later phase.
- A structured `VendorDigest` read-back/serialization path
  (`decisions/0023`) — `chat` reads persisted markdown as opaque text
  instead.

## Design decisions

See `decisions/0023-chat-grounds-on-persisted-files-not-live-
regeneration.md` for the full reasoning. Summary:
- `chat` never calls `sync_vendor` — it reads `vendor/<name>/CLAUDE.md`
  and, if present, `vendor/<name>/OVERVIEW.md` directly as prompt text.
  This avoids re-incurring `promote`'s clone + AI-generation cost on
  every REPL session start.
- `chat` works on a vendor at any depth. A `surface` vendor (or a `full`
  vendor whose description generation failed, i.e. `OVERVIEW.md` absent)
  gets thinner grounding from `CLAUDE.md` alone, plus a one-line hint at
  session start pointing at `depcompass promote <vendor>` — not a hard
  block, matching every other command's depth-agnostic behavior.
- The conversation loop is plain multi-turn text completion — no forced
  tool-use, no file-exploration/tool-use loop, no escalation to a bigger
  model mid-conversation (`decisions/0013` already rejected that: it
  "breaks the REPL's cost/speed model, which depends on staying
  digest-only and Haiku-only"). On scope overflow, Phase 9's routing/
  Skill-folder handoff is the eventual answer — Phase 8 has no fallback
  beyond the model's own text response.
- `chat <vendor>` takes a required vendor name argument. There is no
  bare `depcompass chat` in this phase (project-root mode is Phase 9);
  the CLI should give a clear "vendor argument required" error, not a
  degraded project-mode attempt.

## Files

- `src/depcompass/chat.py` (new) — see Scope above.
- `src/depcompass/cli.py` — `chat` command implementation; loads
  `vendor.toml` via the existing `_load_config()` helper, filters for
  the named vendor (same pattern as `sync`/`promote`), errors clearly on
  an unknown vendor name or a vendor never synced (no
  `vendor/<name>/CLAUDE.md`), otherwise calls `chat.run_chat(...)`.
- `tests/test_chat.py` (new).
- `docs/cli-reference.md`, `README.md`, `architecture/overview.md`,
  `planning/ROADMAP.md`, `planning/CONTEXT.md`, `CHANGELOG.md` — updated
  in place, same commit as the implementing change (`CLAUDE.md` §2).

## Verification

- `pytest` — full suite passes, `tests/test_chat.py` included; no test
  makes a live Anthropic API call or real terminal I/O beyond
  `CliRunner`'s scripted stdin (`decisions/0016`).
- `ruff check .` — clean, including the new module.
- Manual, against a real project with at least one `full`-depth vendor
  and one `surface`-depth vendor:
  - `depcompass chat <full-depth vendor>` — context indicator shows
    `depth=full`, no promote hint; ask a question answerable from that
    vendor's `OVERVIEW.md`/`CLAUDE.md` content and confirm a grounded
    reply; `exit` cleanly quits; `Ctrl-C` mid-session exits cleanly with
    no traceback.
  - `depcompass chat <surface-depth vendor>` — promote hint shown,
    thinner grounding, still answers from `CLAUDE.md` content.
  - `depcompass chat nonexistent-vendor` — clear CLI error, no REPL
    starts.
  - `depcompass chat <a vendor listed in vendor.toml but never synced>`
    — clear "run `depcompass` first" error, no REPL starts.
  - Per `decisions/0016`'s established posture (the same caution applied
    to `promote` in Phase 7), the actual conversational exchange against
    the real Anthropic API should be run manually by a human — not
    something an agent verifies automatically as part of this phase's
    sign-off.
- `git status` after implementation touches: `src/depcompass/chat.py`
  (new), `src/depcompass/cli.py`, `tests/test_chat.py` (new), plus the
  same-commit docs listed above — `decisions/0023-*.md` is already
  written as of this plan, not part of the implementation commit's diff.
