# The clean-room redocumentation workflow

A proven, repeatable process for reconstructing a project's own
documentation from zero — evidence-grounded, never a copy of the
documentation it replaces — using an isolated AI writer that genuinely
cannot see the project's existing narrative docs, history, or this
session's own conversation. Run successfully, end to end, against this
repository (Phase 81B) and, in a lighter form, against
`codecompass-template` (Phase 81B Amendment 4).

This document describes the **proven** process. The credential-
provisioning gap that originally blocked it (Phase 81B, before Amendment
4) is recorded as history in `planning/phase-81b-mode-b-isolation-investigation.md`
and `planning/phase-81b-broker-isolation-investigation.md` — not
repeated here.

## Why this exists

An AI writer asked to "document this project" while sitting inside the
same conversation, repository checkout, and project instructions that
produced the *existing* documentation cannot help being anchored by
them — it will tend to paraphrase or lightly edit what's already there,
even when asked for a from-scratch rewrite. The only way to get a
genuinely independent reconstruction is to make independence
*structural*: the writer runs somewhere that mechanically cannot reach
the existing docs, the git history, the orchestrating session's own
context, or the open internet, and can prove it.

## The trust boundary

```
TRUSTED HOST (the orchestrating session's own machine)
    │
    ├── a narrowly-scoped model-inference broker
    │     - holds the real subscription/provider authentication
    │     - spawns one fresh, isolated inference subprocess per request
    │       (fresh session id, sanitised environment, no tools, no MCP)
    │     - exposes only {system_prompt, messages} -> {output, usage} —
    │       the protocol has no syntax for a file path, shell command,
    │       or tool/MCP config, not merely a runtime refusal of one
    │
────┼──────────────── mechanical isolation boundary ────────────────
    │   (Linux user/mount/network/PID namespaces + pivot_root into an
    │    allow-list-only root — nothing outside explicit bind-mounts
    │    exists in the sandbox's view at all)
    │
    └── one bind-mounted Unix socket — the sandbox's only reachable
        path to anything outside its own mounted filesystem view
                │
                ▼
        CLEAN-ROOM WRITER (inside the sandbox)
        - sees only an explicitly allow-listed evidence export
        - no original repository, no sibling checkouts, no .git
        - no existing narrative documentation in any form
        - no ~/.claude, no provider credentials, no MCP config
        - no parent-agent conversation (verified by canary test)
        - no general network access
```

## The full lifecycle

```
prepare & validate canonical knowledge (if the project has one)
         ↓
freeze a documented_revision (an ordinary commit on main)
         ↓
build + validate a manifest-checked clean-room branch (handoff_commit)
         ↓
verify Mode B isolation — mechanically, by active escape attempt,
not by inspection — INCLUDING a context-contamination canary test
         ↓
run a cold-reader inside verified Mode B: is the evidence sufficient?
         ↓
   ┌─────┴─────┐
 GAPS FOUND   SUFFICIENT
   │             │
   ↓             ↓
invalidate    run the authoritative writer, fresh context,
handoff,      inside the same verified boundary
reconcile           │
evidence,           ↓
repeat        preserve the first complete result, unedited,
              before any comparison with legacy documentation
                    │
                    ↓
              legacy-document gap review (legacy docs as a gap
              detector only — never copied in; every candidate gap
              independently re-verified against primary source)
                    │
                    ↓
              targeted revision writer pass (fresh context again,
              given only verified facts + their real source
              locations, never legacy prose) for any real gap found
                    │
                    ↓
              documentation disposition: replace/delete/archive the
              real repository's own existing docs; reconcile links
                    │
                    ↓
              persist this document (only now — a run that reached
              SUFFICIENT and completed disposition)
```

## What "verified" means for Mode B, concretely

Not "the design should prevent X" — an actual, adversarial attempt at
each route, with the real command and real output recorded:

- Filesystem/parent-path traversal: attempt to reach the original
  repository or a sibling checkout from inside the sandbox.
- `.git` history/branches/remotes: confirm no `.git` directory exists
  anywhere in the sandbox's view at all.
- Network: a real `curl` attempt to a real external host.
- Credentials, on disk and in the environment: a full filesystem scan
  for credential-shaped files, and an explicit environment dump —
  this is how the original investigation found a real leak (a session
  token inherited into the sandbox's environment unless the
  environment was rebuilt from an empty base, not merely filtered).
- MCP/connector configuration and the orchestrating agent's own prior
  session state: confirmed absent by direct search.
- The context-contamination canary: a unique secret mentioned only in
  the orchestrator's own live conversation, never written to any file,
  is used as a probe — a fresh model invocation through the broker,
  from inside the sandbox, is directly asked to produce or demonstrate
  knowledge of it. It must not be able to.

A mechanism that passes every route except model-API credential
provisioning is `VERIFIED` for isolation and `BLOCKED` for the
authoritative writer run — these are different findings, and
conflating them produces a false "verified" claim. The broker
(Amendment 4) exists specifically to close that one remaining gap by
giving the sandbox a narrow *inference capability* instead of a
*credential*.

## The broker, briefly

`scripts/prepare_cleanroom_branch.py` builds and validates the
clean-room branch; `scripts/cleanroom_broker.py` is the inference
broker; `scripts/cleanroom_broker_client.py` and
`scripts/cleanroom_prompt_assembler.py` are what the sandbox itself
uses to reach the broker and assemble a request from its own mounted
evidence. See their own module docstrings and
`tests/test_cleanroom_broker.py` / `tests/test_cleanroom_prompt_assembler.py`
for the full, tested contract. These are maintainer-only tooling, not
part of the installed `codecompass` package.

## Known, accepted limits

- A fixed, content-neutral residual (the authenticating account's
  email, today's date, a token-budget figure, OS/kernel type, a
  generic security-policy reminder) reaches every inference call
  regardless of isolation flags tested — a harness/account-level
  property, not a sandbox leak, and confirmed to carry no project-
  specific content. Named and accepted explicitly
  (`planning/phase-81b-clean-room-redocumentation.md` §26.1) rather
  than silently tolerated.
- The writer has no tool access inside the broker-mediated protocol —
  evidence must be fully assembled into the request up front, not
  browsed interactively. For a project whose allow-listed evidence
  comfortably fits a large context window, this is a non-issue; for a
  much larger project, chunking the evidence export is an open problem
  this run did not need to solve.
- Each writer invocation is a single large completion, not an
  iterative, multi-turn authoring session — real but bounded by how
  much a single response can hold.

## Reusing this for another project

1. Define an explicit allow-list (structural source/tests/config —
   never pre-existing narrative documentation) and an exclusion list,
   with a fail-closed validator proving the two stay consistent and
   that every allow-listed file is genuinely git-tracked, not an
   artifact of a raw filesystem walk.
2. Build and verify the Mode B sandbox for that project specifically —
   don't assume a prior verification transfers; the active-escape
   tests are cheap and the alternative is a false sense of security.
3. Run the cold-reader gate and iterate on real, checked gaps — expect
   more than one round on a project with any real complexity.
4. Preserve the writer's first output before touching legacy docs.
   Use legacy docs only as a gap detector, and verify every candidate
   gap against primary evidence before reconciling anything.
5. Keep the per-project documentation scope honest — a small scaffold
   project needs a small number of pages, not a mechanically-scaled-
   down copy of a larger project's own structure.
