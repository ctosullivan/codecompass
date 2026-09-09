# Project learnings

A lightweight, repository-managed queue for what agents learn while
developing and testing CodeCompass. **Not a knowledge base** — a
pipeline that moves observations toward the artifact that should own them
(a test, an ADR, an architecture doc, a `CLAUDE.md` proposal, a rule, a
skill, a roadmap row, `CONTEXT.md`, `CHANGELOG.md`) — or discards them.

Full design: `planning/v1-redefinition/learning-lifecycle.md`.
Owner: the `knowledge-curator` agent (once Phase 40 creates it).

> **An agent observation does not become authoritative merely because an
> agent recorded it.** It is authoritative once it lands in a test / ADR
> / doc — not while it sits here.

## Lifecycle

```
observation → candidate → evidence/recurrence → curation → promote | retain | merge | discard
```

## How to add a candidate

Append an entry to [`inbox.md`](inbox.md) using
[`TEMPLATE.md`](TEMPLATE.md). Keep it cheap — a few lines. Required
fields: `id`, `title`, `origin`, `date` (absolute), `project_revision`,
`observation`, `evidence` (a real file:line / command output / artifact —
not "seemed like"), `classification`, `status`.

The curator assigns the `id` (`L-NNN`, never reused) if you don't, and
does a lightweight accept.

## Files

| File | Role |
|---|---|
| `inbox.md` | the live queue — candidates + evidence-gathering |
| `TEMPLATE.md` | the candidate format |
| `promoted.md` | append-only log of what was promoted and where (pointers, not content) |
| `candidates/` | one file per candidate, once `inbox.md` gets unwieldy (optional; created when needed) |

## Classification → destination

See `planning/v1-redefinition/learning-lifecycle.md` §4. Summary:
invariant → test; decision → ADR; current architecture → `architecture/`;
project-wide rule → `CLAUDE.md` proposal; scoped rule → `.claude/` rule;
workflow → skill; future improvement → `ROADMAP.md`; open work →
`CONTEXT.md`; user-visible → `CHANGELOG.md`; uncertain → retain;
unsupported → discard.

## Status

Operational since Phase 41 (2026-09-10). The `knowledge-curator` agent
owns triage; `scripts/check_user_docs.py` enforces candidate provenance
and `promoted.md` consistency (and, informationally, flags stale
`evidence-gathering` candidates).
