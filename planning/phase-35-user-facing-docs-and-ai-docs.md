# Phase 35: User-facing docs rewrite + `ai-docs/` folder

## Status

`done`

## Context

codecompass's own user-facing docs have drifted toward assuming the reader
already knows the project. `README.md` has no real setup walkthrough beyond
`pip install -e ".[dev]"` — nothing states the required Python version, that
`git` must be installed locally (vendor cloning shells out to it), or that
`ANTHROPIC_API_KEY` is the environment variable gating AI enrichment (`chat.py`
/`relation_enrichment.py`/`enrichment.py` all call `anthropic.Anthropic()` with
no explicit `api_key=`, relying entirely on the SDK's own env-var read —
confirmed by direct grep, and undocumented anywhere in the repo). There is also
no single place answering "what do I get for free vs. what costs money" — that
story is scattered across `README.md`'s Core-idea bullets, `docs/
cli-reference.md`'s per-command Phase A/B blocks, `architecture/overview.md`'s
~1,900-line Cost Model section, and `examples/README.md`'s real `--budget 0`
transcript (genuinely strong content, just hard to find).

Separately, nothing plays the role an `AGENTS.md`/`llms.txt` file would: a
plain overview telling an agent what codecompass does and — just as
importantly — what it deliberately does *not* do. That boundary already exists
as a set of hard invariants scattered across several ADRs (enrichment is
optional and usage-driven, relation labeling never invents a relationship,
`/discovery` is read-only by convention rather than mechanical enforcement,
codecompass never writes to a spec doc's own file) but has never been
assembled into one place for an agent to read.

Found and requested directly by the user, not surfaced via `/discovery`. Added
to v1.0's blocking scope alongside Phases 30-33 (already `done`), at explicit
user request — Phase 23 Part B (the actual PyPI publish) now also waits on
this phase and Phase 36.

Renumbering note: originally scoped as "Phase 34" during planning, before
Phase 34 (the fenced-code-block chunking fix, found via live `/discovery`
dogfooding) was implemented and claimed that number. Renumbered to 35 with no
scope change — confirmed against `planning/ROADMAP.md`'s current state before
implementation began.

## Scope

**Covers:**
- `README.md` restructured: a new **Setup** section (Python `>=3.11` per
  `pyproject.toml:10`; `git` required locally for vendor cloning;
  `ANTHROPIC_API_KEY` as an *optional* env var, required only for Phase B),
  and a new standalone **"AI enrichment vs. no-AI usage"** section stating
  plainly what's free/always-on (Phase A: trees, API surface, context graph,
  `check`, generated Skills/routing, `/discovery`, `undo`) vs. what Phase B
  specifically adds and costs — reusing `examples/README.md`'s real
  `--budget 0` transcript rather than inventing a new example. Existing
  sections (Core idea, Quick example, How it works, Documentation,
  Contributing, Roadmap, License) are kept, reordered so Setup and
  AI-vs-no-AI sit right after "What it is."
- New `ai-docs/README.md` — a plain-English overview of what codecompass is
  and does, an explicit **"what this does NOT do"** list with each claim
  traced to a real ADR, and 4-6 example prompts mapped to the command/doc an
  agent should reach for.
- New `ai-docs/CLAUDE.md` — a short entrypoint: "if you're an agent asked to
  work in or understand this repo, start here," pointing onward to
  `ai-docs/README.md`, root `CLAUDE.md` (only relevant if contributing code),
  `architecture/overview.md`, `decisions/`, `planning/ROADMAP.md` +
  `CONTEXT.md`. States explicitly that it does not replace or duplicate root
  `CLAUDE.md`'s process-governance content.
- `CONTRIBUTING.md`: remove the stale closing line ("This will expand once
  the `src/codecompass/` package has real modules...", still present at line
  125 — inaccurate 35 phases later).
- `planning/ROADMAP.md`: this phase's row, plus a new dated note (not an edit
  to the existing, now-resolved "v1.0 scope note") recording that Phases
  35-36 are added to v1.0's blocking scope.

**Explicitly does not cover:**
- Any change to `docs/cli-reference.md` or `docs/config-schema.md` content —
  both confirmed current and accurate.
- Fixing `architecture/overview.md`'s existing drift relative to Phase 32's
  `doc_chunking.py`/`doc_chunks` table — that's a documentation gap in a
  *kept-in-sync* doc that should have landed with Phase 32 itself, not this
  phase's job to backfill.
- Any edit to root `CLAUDE.md`. Per `CLAUDE.md` §0, any change to it requires
  a standalone, explicitly-approved diff — never bundled into another
  commit. A one-line pointer from root `CLAUDE.md` to `ai-docs/` is a
  plausible future follow-up, flagged back to the user after this phase
  lands, not assumed or included here.
- The automated doc/code drift-checking tooling itself (Phase 36) — this
  phase is hand-authored content only.
- A docs site / mkdocs evaluation — already out of scope per Phase 23.

## Design decisions

- **Reuse `examples/README.md`'s real transcript rather than writing a new
  example.** It already shows genuine output (`error: estimated cost $0.02
  ... exceeds --budget $0.00`, a real Phase-A-only `CLAUDE.md`) — inventing a
  second, hand-typed example would risk drifting from real behavior in a way
  the existing one doesn't.
- **`ai-docs/CLAUDE.md` is a plain pointer file, not a duplicate of root
  `CLAUDE.md`.** Claude Code only auto-loads `CLAUDE.md` from the working
  directory and its parents, so `ai-docs/CLAUDE.md` won't auto-load unless an
  agent's cwd is under `ai-docs/` or it's referenced explicitly (e.g. from
  root `README.md`'s Documentation section, added by this phase) — accepted,
  since its job is to be findable once pointed at, not to auto-load.
  Root `CLAUDE.md` itself is intentionally left untouched (see Scope).
- **Every "what this does NOT do" claim in `ai-docs/README.md` cites the ADR
  that backs it**, rather than asserting boundaries from memory — verified
  against the actual ADR text during this phase (0026, 0031, 0038, 0040,
  0045), not paraphrased from an earlier planning pass.

## Files

- `README.md` — restructured (Setup + AI-vs-no-AI sections added; existing
  sections reordered).
- `ai-docs/README.md` — new.
- `ai-docs/CLAUDE.md` — new.
- `CONTRIBUTING.md` — stale closing line removed.
- `planning/ROADMAP.md` — new Phase 35 row + new dated note for v1.0 scope.
- `CHANGELOG.md` — new `[Unreleased]` entry.
- `planning/CONTEXT.md` — updated once both Phase 35 and 36 land.

## Verification

- Manual read-through: can a reader who has never seen this repo answer,
  using only `README.md`, "do I need an API key," "what do I get for free,"
  "what does Python/git/setup require," and "how do I install it"?
- Each `ai-docs/README.md` "does NOT do" claim checked against its cited ADR
  text directly (not assumed).
- `ai-docs/CLAUDE.md` confirmed not to duplicate root `CLAUDE.md`'s content.
- `CONTRIBUTING.md`'s stale line confirmed gone.
- `ruff check .` clean (no code changes in this phase, but ruff also lints
  `scripts/` once Phase 36 adds it — not applicable here).

**Confirmed live:** the read-through checklist above passes — `README.md`'s
Setup section states the Python version, `git` requirement, and
`ANTHROPIC_API_KEY`'s optional/Phase-B-only role explicitly; the AI-vs-no-AI
section reuses `examples/README.md`'s real transcript verbatim. Each
`ai-docs/README.md` "does NOT do" claim was checked against its cited ADR's
actual text (0026, 0031, 0038, 0040, 0045) while writing it, not assumed.
`CONTRIBUTING.md`'s stale closing line is gone. Phase 36's
`check_user_docs.py`, once written, independently confirmed `README.md`
mentions `ANTHROPIC_API_KEY` and that `ai-docs/` has no empty/missing files.
