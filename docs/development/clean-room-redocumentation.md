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

**Amendment 5 (corrective, 2026-10-14)** hardened the reusable
preparation/isolation machinery itself after a review found real defects
in it — narrative leakage through a broadly allow-listed directory,
`documented_revision` not actually enforced against the Git object
database, a self-referential manifest field, and manifest validation
that depended on the live parent repository. None of this reopened or
redid the documentation reconstruction itself (`README.md`/`docs/` on
this repository and on `codecompass-template` are unchanged, still the
Amendment 4 output) — see
`planning/phase-81b-clean-room-redocumentation.md` §27 for the full
account. The description below reflects the corrected mechanism.

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
export the allow-listed tree AT THAT EXACT REVISION from the Git
object database (never the working tree) + build a self-contained,
content-addressed manifest (payload_tree_sha256)
         ↓
run scripts/verify_cleanroom_isolation.py — a repeatable, executable
preflight gate, not a one-off investigation — then verify Mode B
isolation for the real run itself the same way: mechanically, by
active escape attempt, not by inspection — INCLUDING a context-
contamination canary test
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

`scripts/verify_cleanroom_isolation.py` (Amendment 5) turns the checks
above into a repeatable, executable preflight instead of a one-off
investigation to re-read and manually re-type: it builds a real,
disposable instance of the same namespace/`pivot_root` sandbox, bind-
mounts scratch evidence/output and a fake, local, content-neutral
stand-in broker (never real inference), and actively tests all eleven
of filesystem/sibling-repository/`.git`-history/environment-secret/
network/GitHub/broker-IPC-boundary/parent-agent-context conditions,
honestly reporting (never silently passing) any it cannot mechanically
evaluate. Run it directly before trusting Mode B for a real run:

```
python3 scripts/verify_cleanroom_isolation.py
```

## File-level narrative isolation

An allow-listed *directory* (`src`, `tests`, `scripts`) is swept in by
`git ls-tree`, not reviewed file by file the way an individually-named
path is. A doc-shaped file (`.md`/`.rst`/`.txt`) found beneath one of
these three must appear in `prepare_cleanroom_branch.py`'s own
`_CLASSIFIED_KEEP_DOC_PATHS` (genuine structural/machine-fixture
evidence) or `_CLASSIFIED_EXCLUDE_DOC_PATHS` (narrative/historical/
project-process prose) — an unclassified one fails the build closed
rather than silently riding along either way. A real corrective review
(Amendment 5) found six genuine narrative leaks this way: a test-suite
README and five fixture docs nested under `tests/fixtures/
ledgerkit_lifecycle_demo/`, none of them the real `README.md`/`docs/`/
`architecture/`/`ai-docs/` tree, which the allow-list has excluded by
name since Amendment 2.

## Exact-revision export and handoff identity

`prepare_cleanroom_branch.py build` exports every allow-listed path from
the Git object database at the exact `--documented-revision` given — via
`git ls-tree`/`git cat-file`, never by reading the live working tree —
and, for a path nested inside a Git submodule, resolves the exact gitlink
commit the superproject recorded at that same revision, never the
submodule's currently-checked-out `HEAD`. Either resolution failing
(an unresolvable revision, or a gitlink commit missing from the
submodule's own object database) fails the build closed.

The manifest (`CLEANROOM-MANIFEST.yaml`) binds every writer-visible
payload file by content hash, plus one canonical `payload_tree_sha256`
top-level digest — the manifest file itself is the sole, explicit,
non-circular exception to that digest's own input (a file cannot name
its own identity without changing it). `prepare_cleanroom_branch.py
validate` checks a staged tree purely against its own manifest, with
**no access to the parent repository required** — it can validate a
clean-room branch's checkout on its own, anywhere.

The manifest no longer tries to record its own commit SHA (the earlier
`handoff_commit` field required a second, after-the-fact commit purely
to update it, and was always one commit stale relative to wherever the
tree actually, finally lived — this convention is superseded, not
retroactively rewritten on branches that already used it). The actual
branch/commit holding a given payload is recorded externally, in this
project's own plan file and retro, where self-reference isn't circular.

## The broker, briefly

`scripts/prepare_cleanroom_branch.py` builds and validates the
clean-room branch; `scripts/verify_cleanroom_isolation.py` is the
repeatable isolation preflight; `scripts/cleanroom_broker.py` is the
inference broker; `scripts/cleanroom_broker_client.py` and
`scripts/cleanroom_prompt_assembler.py` are what the sandbox itself
uses to reach the broker and assemble a request from its own mounted
evidence. See their own module docstrings and
`tests/test_cleanroom_broker.py` / `tests/test_cleanroom_prompt_assembler.py`
/ `tests/test_prepare_cleanroom_branch.py` /
`tests/test_verify_cleanroom_isolation.py` for the full, tested
contract. These are maintainer-only tooling, not part of the installed
`codecompass` package.

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
   with a fail-closed validator proving the two stay consistent, that
   every allow-listed file is genuinely git-tracked at the exact
   declared revision (never the working tree, never a raw filesystem
   walk), and that any doc-shaped file swept in by a broad directory is
   explicitly classified rather than assumed safe.
2. Build and verify the Mode B sandbox for that project specifically —
   don't assume a prior verification transfers; run `scripts/
   verify_cleanroom_isolation.py` as a cheap, repeatable first gate, and
   the project-specific active-escape tests beyond it; the alternative
   is a false sense of security.
3. Run the cold-reader gate and iterate on real, checked gaps — expect
   more than one round on a project with any real complexity.
4. Preserve the writer's first output before touching legacy docs.
   Use legacy docs only as a gap detector, and verify every candidate
   gap against primary evidence before reconciling anything.
5. Keep the per-project documentation scope honest — a small scaffold
   project needs a small number of pages, not a mechanically-scaled-
   down copy of a larger project's own structure.
