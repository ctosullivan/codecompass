# Project learning lifecycle plan (required output 5)

A lightweight, repository-managed process for capturing what agents learn
while developing and testing CodeCompass — without free-form AI memory
becoming the project's source of truth.

Implemented by Phase 41. Owned by `knowledge-curator`
(`agent-led-development.md` §2.6). Scaffold created now at
[`../learnings/`](../learnings/).

## 1. Guiding principle

> **An agent observation does not become authoritative merely because an
> agent recorded it.**

Canonical knowledge lives in explicit, reviewable repository artifacts
(tests, ADRs, `architecture/`, `CLAUDE.md`, docs, roadmap) and in
external evidence (a dependency's source, a spec, a manual, a
compatibility test). The learning lifecycle is the *pipeline* that moves
a raw observation toward one of those artifacts — or discards it.

There is deliberately **no giant permanent "AI learnings" document.**
`planning/learnings/inbox.md` is a transient queue, not an archive.

## 2. The lifecycle

```
observation                     an agent notices something during a phase
    ↓                           (cheap to capture — one inbox entry)
candidate learning              curator accepts it into the queue with an ID
    ↓
supporting evidence /           it recurs, or a second agent hits it, or
recurrence                      a concrete artifact/line is cited
    ↓
knowledge curation              curator classifies + picks a destination
    ↓
promote  /  retain  /  merge  /  discard
```

- **observation → candidate:** any agent may append to
  `planning/learnings/inbox.md`. Cost: ~5 lines. The curator does a
  lightweight accept (assign ID, check provenance is present) — it does
  not have to be *true* yet, just *specific*.
- **candidate → evidence:** a candidate sits in the inbox gaining
  `evidence:` / `recurrence:` annotations across phases. A candidate with
  no new evidence after ~3 phases is a discard candidate (curator's call).
- **evidence → curation:** at each phase's step 10, and in bulk at each
  milestone's own closeout (Phase 69 for the redefined-v1 milestone;
  Phase 47 was this project's own first standing bulk-review checkpoint,
  though no dedicated bulk disposition actually ran there — see below),
  the curator reviews the queue.
- **A candidate's own curation note may commit to a numbered forcing
  point** ("if still unresolved at the Phase N bulk review, force a
  promote/discard"). **That commitment must, in the same edit, also be
  mirrored as a concrete line in Phase N's own `planning/phase-N-*.md`
  plan file** once that file exists (or, if Phase N's plan doesn't exist
  yet, added to a short running "forcing points due" list in this
  section) — so it is checkable from the destination phase's own scope
  list (`CLAUDE.md` §1), not only readable by someone who happens to
  open `inbox.md` and notice the phase number has arrived. **A standing
  bulk-review cadence (like Phase 47's own, above) is itself a scope
  item of whichever phase lands on that number** — not an obligation
  floating free of any specific phase's own plan. Confirmed necessary
  at Phase 69 (`L-045`): `L-003`'s own Phase 43b curation note committed
  to a forced decision "at the Phase 47 bulk review," and this section's
  own text already named Phase 47 as a standing checkpoint — but nothing
  in Phase 47's own plan listed the bulk review as a scope item, so no
  bulk disposition actually ran there, and the miss went uncaught for a
  further 21 phases until Phase 69's own dedicated milestone-scale
  review happened to re-read the whole queue end to end.
- **curation → outcome:** one of four (see §4).

## 3. Candidate learning format

One entry per candidate in `planning/learnings/inbox.md` (or, once large,
one file per candidate under `planning/learnings/candidates/`). Fields:

| Field | Required | Notes |
|---|---|---|
| `id` | yes | stable, `L-NNN`, never reused |
| `title` | yes | one line |
| `origin` | yes | originating task / phase / session (e.g. "Phase 46, Technical Clipper task 3") |
| `date` | yes | absolute (`2026-09-09`), not "today" |
| `project_revision` | yes | CodeCompass git SHA (short) when observed; + target repo SHA for reference-project findings |
| `observation` | yes | what was noticed, factually |
| `evidence` | yes | file:line, command output, a specific artifact — not "it seemed like" |
| `classification` | yes | see §4 — one of: `invariant` / `decision` / `architecture` / `project-rule` / `scoped-rule` / `workflow` / `future-improvement` / `open-work` / `user-visible` / `uncertain` / `unsupported` |
| `status` | yes | `candidate` / `evidence-gathering` / `promoted` / `retained` / `merged:<id>` / `discarded` |
| `recurrence` | no | appended each time it re-appears |
| `promoted_to` | when promoted | the artifact + commit that now owns it |

Template lives at `planning/learnings/TEMPLATE.md` (Phase 41).

## 4. Classification → destination (promote into the artifact that owns it)

| Classification | Promote to | Who finalises |
|---|---|---|
| required behavioural **invariant** | a regression **test** | lead / ad-hoc implementer |
| architecture **decision** / rationale | a new numbered **ADR** | lead (ADR process) |
| description of **current architecture** | `architecture/` doc | `docs-maintainer` |
| recurring **project-wide** agent rule | proposed **`CLAUDE.md`** change (`proposed-governance-changes.md` → gate G4) | user approves, lead writes |
| **scoped** recurring rule | a Claude **rule / agent-brief / skill config** (`.claude/`) | lead |
| repeatable **workflow** | a Claude **skill** (`.claude/skills/`) | lead |
| **future improvement** | a **roadmap** row (`ROADMAP.md`) | `roadmap-context-curator` |
| unresolved **current work** | **`planning/CONTEXT.md`** "next step / outstanding" | `roadmap-context-curator` |
| **user-visible** change already shipped | **`CHANGELOG.md`** entry | whoever shipped it |
| **uncertain** but plausible | stays a **retained** candidate | curator |
| **unsupported** / irrelevant | **discard** (with a one-line reason) | curator |

`retain` is for real-but-not-yet-actionable observations. `merge` folds a
candidate into a related one (`status: merged:L-042`) so recurrence
counts aggregate correctly.

## 5. Storage layout (`planning/learnings/`)

```
planning/learnings/
├── README.md          how the lifecycle works (points here), how to add a candidate
├── inbox.md           the live queue — candidates + evidence-gathering
├── TEMPLATE.md        the candidate format (Phase 41)
├── candidates/        one file per candidate once inbox.md gets unwieldy (Phase 41+, optional)
└── promoted.md        append-only log: id, date, classification, promoted_to (artifact + commit)
```

`promoted.md` is the *only* long-lived file, and it holds pointers, not
content — "L-017 → test_usage.py::test_vendor_dir_excluded, commit abc123".
It exists so a future session can see *that* a learning was captured and
where it went, without the content living in two places.

## 6. Hygiene (wired into `docs-sync`, Phase 41)

`scripts/check_user_docs.py` gains checks:
- every `inbox.md` candidate has all required fields;
- no candidate is `status: promoted` without a `promoted.md` line;
- no candidate has been `evidence-gathering` for more than a
  configurable number of phases without a curator note (report-only —
  prompts a discard/promote decision, doesn't force one).

## 7. Relationship to CodeCompass's own product

CodeCompass may eventually *index* `planning/learnings/` and `promoted.md`
as spec-doc-like artifacts and relate them to the code/tests/ADRs they
concern (the same mechanical mention detection it already does for
`docs/` and `decisions/`). That is a Stage C/E candidate, not committed
here, and it does **not** change where truth lives: the learning is
authoritative once it's in the test / ADR / doc, not while it's a
candidate, regardless of whether CodeCompass has indexed it.
