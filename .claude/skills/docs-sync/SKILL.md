---
name: docs-sync
description: >-
  Maintainer-only check for drift between this repo's own user-facing docs
  (README.md, docs/, ai-docs/) and its own code. Run `python
  scripts/check_user_docs.py` to see what it flags, then fix findings by
  judgment — this skill never auto-fixes anything.
---

# docs-sync

Keeps codecompass's own hand-authored docs honest against its own code —
this is meta-tooling for maintaining this repo, not a codecompass product
feature (it's not shipped, not a `codecompass` subcommand).

## What it checks

```bash
python scripts/check_user_docs.py           # report-only, always exits 0
python scripts/check_user_docs.py --strict   # exits 1 if any finding
```

Five mechanical rules, no AI, never edits a file:
1. Every `@app.command()`/`@query_app.command()` name in `src/codecompass/cli.py` is mentioned in `docs/cli-reference.md`.
2. `README.md`'s "phases 0-N" claim matches the highest `done` phase in `planning/ROADMAP.md`.
3. `README.md` mentions `ANTHROPIC_API_KEY`.
4. Every `VendorConfig` field (`src/codecompass/core.py`) is mentioned in `docs/config-schema.md`.
5. Every file directly under `ai-docs/` exists and is non-empty.

## How to use this skill

1. Run the script above.
2. For each finding, read the actual code/doc it points at and decide the
   right fix by judgment — a finding is a pointer to investigate, not
   something to mechanically resolve (e.g. a new CLI command needs a real,
   well-written reference section, not a one-line stub that merely
   satisfies the substring check).
3. Apply the fix to the doc content itself, by hand.
4. Follow this project's normal per-phase discipline for whatever you
   touch: a `CHANGELOG.md` entry, and `planning/CONTEXT.md` updated at the
   end, per `CLAUDE.md`.
5. Re-run the script to confirm the finding is gone.

Rule set is intentionally small (five checks) — this is a maintainer smoke
check, not an exhaustive doc linter. See
`planning/phase-36-docs-sync-tooling.md` for what's explicitly out of scope.
