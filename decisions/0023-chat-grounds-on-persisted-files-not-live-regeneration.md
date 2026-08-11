# 0023. Chat grounds on persisted digest files, not live regeneration

## Status

Accepted

## Context

Phase 8 ("Single-vendor chat REPL," `planning/ROADMAP.md`) needs a
concrete answer for how `depcompass chat <vendor>` obtains the content it
grounds its answers in. No read-back path for a `VendorDigest` exists
today — every command that needs one (`sync`, `promote`, `check --fix`)
calls `sync_vendor` fresh (`src/depcompass/sync.py:36`), which for a
`depth = full` vendor clones the vendor's upstream repository
(`decisions/0021`) and runs a billed grounded-description AI call
(`decisions/0019`). `chat` is a REPL a user may start many times across a
session; if it called `sync_vendor` on every invocation the way other
commands do, each `chat` invocation would silently re-incur that clone
and AI-generation cost — the exact cost `promote`'s confirmation gate
(`decisions/0018`) exists to make explicit and one-shot. `decisions/0012`
already frames the generated markdown (`CLAUDE.md`, `OVERVIEW.md`,
`FILETREE.md`, `DEPTREE.md`) as "backing store" for the REPL rather than
something the REPL regenerates, but nothing had pinned down what "reads
the backing store" means mechanically — whether that's a new structured
read-back of a `VendorDigest`, or something simpler.

Separately, Phase 8's scope (per its own plan,
`planning/phase-8-chat-repl.md`) is limited to explicit single-vendor
mode (`chat <name>`) — no routing, no multi-vendor context. That's
already settled by the ROADMAP's Phase 8/Phase 9 split, not a new
decision here, but it bounds what "grounding" needs to cover: one
vendor's own files, nothing more.

Also unresolved before this: whether `chat` should require a vendor
already be promoted to `depth = full`, since only `full` vendors get an
AI-generated `conversational_overview`/`OVERVIEW.md`. Every other command
in the CLI works at any depth; only the AI-generation commands themselves
(`promote`, and `sync`/`check --fix` for already-`full` vendors) are
depth-gated.

## Decision

`chat <vendor>` builds its system prompt by reading the vendor's already
-persisted files directly as text — `vendor/<name>/CLAUDE.md` (always
required; its absence means the vendor was never synced) and
`vendor/<name>/OVERVIEW.md` (read if present) — with no call to
`sync_vendor`, no reconstruction of a `VendorDigest` object, and no new
digest-serialization format. `chat` works on a vendor at any depth: a
`depth = full` vendor with a successful `OVERVIEW.md` gets full grounding
(metadata, API surface, known gotchas, and the technical + conversational
description); a `depth = surface` vendor (or a `full` vendor whose
description generation failed) gets thinner grounding from `CLAUDE.md`
alone, plus a one-line hint printed at session start suggesting
`depcompass promote <vendor>` for deeper answers — not a hard block. The
conversation loop itself is plain multi-turn text completion (a `system`
prompt plus a growing `messages` list) against Haiku, with no forced
tool-use and no file-exploration/tool-use loop, consistent with
`decisions/0013`'s explicit rejection of escalating a REPL query to a
more capable model or a live-exploration loop.

## Alternatives considered

- **Call `sync_vendor` fresh on every `chat` invocation**, matching every
  other command's pattern. Rejected — re-clones the repository and
  re-runs the AI generation call every session start for a `full`
  vendor, defeating the entire point of `promote`'s one-shot
  cost-confirmation gate.
- **Add a `VendorDigest.to_json`/`from_json` persisted sidecar and a
  `load_digest` reconstruction function**, giving `chat` (and any future
  command) a proper structured read-back path. Rejected for this phase —
  `chat` only ever needs the already-rendered markdown as prompt text; it
  never needs to inspect `VendorDigest`'s individual fields
  programmatically. Building a serialization format and reconstruction
  function to satisfy a need that doesn't exist yet is exactly the kind
  of premature abstraction this project avoids. Revisit if a later phase
  (e.g. Phase 9's project-wide rollup) turns out to need structured
  access rather than raw text.
- **Require `depth = full` before `chat` works at all.** Rejected —
  would be the only depth-gate in the CLI outside the AI-generation
  commands themselves, and there's no correctness reason a `surface`
  vendor's `CLAUDE.md` (metadata, API surface, known gotchas) can't
  ground a useful, if thinner, conversation.

## Consequences

- `chat`'s grounding quality is coupled implicitly to
  `render_vendor_claude_md`'s section layout (`src/depcompass/
  claude_md.py`) — `chat` treats the whole file as opaque prompt text, so
  a future change to that renderer changes what `chat` sees without
  `chat.py` itself needing to change. Acceptable: `chat` never parses
  individual sections beyond what already exists
  (`read_installed_version`'s regex, reused elsewhere, is not needed by
  `chat` at all).
- A vendor directory that doesn't exist yet (never synced) has nothing
  for `chat` to read — `chat` must detect this explicitly and fail with a
  clear "run `depcompass` first" message rather than starting a REPL with
  empty or missing grounding.
- No structured digest read-back path exists after this decision either —
  if a later phase needs one, it's a new, separate design decision, not
  implied by this one.
