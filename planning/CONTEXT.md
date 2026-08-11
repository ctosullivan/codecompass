# Project context

This file reflects the *current* state of the project — overwritten at
each stopping point, not appended to. See `CHANGELOG.md` and git history
for the log of how it got here.

## Current phase

**Phase 8: Single-vendor chat REPL — done. All eight MVP phases (0-8) are
now complete** (`decisions/0022`). The `CLAUDE.md` §6 release-promotion
step (a dated `[Unreleased]` → version-tagged `CHANGELOG.md` section) is
now applicable, but cutting an actual `v0.1` tag/release is a separate,
not-yet-made decision — it hasn't been done yet, and isn't implied by all
phases being `done`.

## What was just completed

Implemented `planning/phase-8-chat-repl.md` in full. New
`src/depcompass/chat.py`:
- `_build_system_prompt(vendor_dir, config)` — reads
  `vendor/<name>/CLAUDE.md` (required; raises `ChatError` if the vendor
  was never synced) and `vendor/<name>/OVERVIEW.md` (optional) as raw
  text, concatenated under a grounding-only instruction preamble. No call
  to `sync_vendor`, no reconstructed `VendorDigest` — `decisions/0023`,
  settled in the prior planning session.
- `_call_anthropic(system_prompt, messages)` — plain multi-turn text
  completion against `claude-haiku-4-5-20251001`, no forced tool-use
  (unlike `grounded_description`'s single-shot structured call). The
  monkeypatch seam tests replace (`decisions/0016` — no live API call in
  any test).
- `run_chat(config, project_root, console)` — the REPL loop: prints a
  context-indicator line (vendor name, depth) plus a one-line `promote`
  hint whenever `OVERVIEW.md` is absent (works at any depth, not gated on
  `depth = full`); reads input via `rich.prompt.Prompt.ask`; exits
  cleanly on `exit`/`quit`/EOF (`Ctrl-D`)/`Ctrl-C` (caught
  `KeyboardInterrupt`, no traceback); a mid-conversation API failure is
  reported inline and the loop continues rather than ending the session.

`cli.py`'s `chat` command is now real: `chat <vendor>` (required
argument — no bare project-mode `chat`; that's Phase 9's routing/rollup
work, not built here), replacing the `_not_implemented("chat")` stub.
`_PHASE_BY_COMMAND`/`_not_implemented` were removed as dead code — no
stub commands remain.

Same-commit docs updated: `docs/cli-reference.md` (`chat <name>` marked
implemented, header note updated), `README.md` (Status section now says
MVP complete, Quick example shows a working `chat` invocation),
`architecture/overview.md` (top status paragraph, the Grounded
description section's Phase 8/9 cross-reference, and the Chat REPL
section — explicit-vendor mode marked implemented, project-root mode
still Phase 9, and the grounding description corrected to say
`CLAUDE.md`/`OVERVIEW.md` specifically rather than "all digest files"),
`planning/ROADMAP.md` (Phase 8 → done, "MVP done when" now states all
eight phases are done), `CHANGELOG.md`.

**Verification**: `pytest` reports 218 passed, 1 skipped (Cargo live
smoke test, unchanged since Phase 2), up from 207 at the end of Phase 7;
`ruff check .` is clean. Manually verified in a scratch directory: bare
`depcompass` bootstrap of a real `requirements.txt` project (free,
already-covered ground), then `chat`'s free code paths directly against
the real CLI entry point — unknown vendor name (clear error, exit 1),
a vendor listed in `vendor.toml` but never synced (clear "not yet
synced... run `depcompass` first" error, exit 1), and a synced
`depth = surface` vendor's REPL startup banner (context indicator +
promote hint shown correctly, `exit` typed immediately as the first
input so no API call is reached, clean exit 0). A real
`ANTHROPIC_API_KEY` was present in this environment, so — consistent
with `decisions/0016`'s posture and the same caution applied to
`promote` in Phase 7 — the actual conversational exchange against the
live Anthropic API was **not** exercised by the agent; a human should
run `depcompass chat <vendor>` and have a real exchange at least once
before trusting output quality.

## Decisions made this session not already captured in an ADR

- None — `decisions/0023` (written in the prior planning session) already
  covers this implementation's grounding/scoping decisions in full; no
  new tradeoff surfaced during implementation itself.

## Next concrete step

**All eight MVP phases are done.** Nothing is currently planned or
requested. Two things that could reasonably come next, neither started
nor requested yet:
1. Deciding whether/when to cut the `v0.1` tag and promote
   `CHANGELOG.md`'s `[Unreleased]` section to a dated release
   (`CLAUDE.md` §6) — now applicable per `decisions/0022`, but a separate
   explicit decision, not automatic.
2. Planning Phase 9 (project-root-aware REPL routing + whole-project
   rollup + Skill-folder escalation) — per `CLAUDE.md` §1, would need its
   own `planning/phase-9-*.md` written and approved before any
   implementation starts. Post-MVP — not required for v0.1.

Surface both as open options next session rather than assuming which one
(if either) the user wants first.

**Still outstanding, not a blocker but worth remembering**:
- Once a Rust toolchain is available anywhere in the pipeline,
  `decisions/0014` requires validating the Cargo adapter's fixture
  assumptions (including `repository_url()`) and regex-based `pub`
  extraction against real `cargo metadata` output and a real crate —
  currently entirely unverified, and `promote`'s end-to-end flow against
  a real Cargo vendor is likewise untested.
- `extract_npm_symbols` (Phase 3) is untested against real-world `.d.ts`
  authoring styles beyond hand-written fixtures.
- `depcompass.grounded_description` (Phase 7) and `depcompass.chat`
  (Phase 8) have never been run against the real Anthropic API in this
  environment — a human must do this manually at least once before
  trusting output quality (`decisions/0016`).
- `staleness.py`'s custom version parser (Phase 6) has no real PEP 440 or
  full-semver correctness — flag if it misclassifies a real-world version
  string once used against real projects.
- A formal trigger-accuracy evaluation harness for per-vendor Skills
  (decisions/0013's Consequences) was not built in Phase 7 — Skill
  generation itself works and is tested, but nothing automatically
  verifies a generated trigger description actually fires on relevant
  questions.
- Cursor `.mdc` export has no `globs` field (description-based relevance
  only) — glob scoping to wherever a vendor is actually imported in the
  consuming codebase is a documented future refinement, not implemented.
- `chat` has no conversation-length capping, no streaming, and no
  cumulative-cost display — all explicitly deferred in
  `planning/phase-8-chat-repl.md`, revisit if real usage shows a need.
