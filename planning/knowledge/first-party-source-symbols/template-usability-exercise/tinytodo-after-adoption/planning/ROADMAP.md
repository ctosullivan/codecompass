# Roadmap

An at-a-glance view of what's done, in progress, or planned. Not a
detailed spec for each item — that belongs in the item's own plan (if it
had one) or in `decisions/` for any real tradeoff it involved.

Update this file whenever something starts, finishes, or its scope
changes materially — in the same change that does the starting/
finishing/re-scoping, not as a separate housekeeping pass later.

| Item | Status | Notes |
|---|---|---|
| Adopt `codecompass-template` | done | 2026-10-01. `CLAUDE.md`, `.gitignore`, `vendor.toml`, `docs/`, `decisions/`, `planning/` copied in; project's own `README.md` and `LICENSE` deliberately kept/omitted (see `planning/CONTEXT.md`). CodeCompass itself not installed — `vendor.toml` stays empty and `codecompass sync`/`query` steps are skipped, as expected for a project not running the actual tool yet. |
| Document `_next_id`'s id-reuse design via the heavier-weight knowledge workflow | done | 2026-10-01. Assertion `planning/knowledge/assertions/task-ids-001.md`, snapshot `planning/knowledge/snapshots/task-ids@v1.toml` (partially frozen — see its own header note), conceptual doc `docs/task-ids.md`, decision `decisions/0001-task-ids-are-never-reused.md`. |

Status values: `planned` / `in progress` / `done` / `deferred` (on the
list, not scheduled — say why) / `dropped` (say why, briefly, so it
isn't silently reconsidered later without that context).
