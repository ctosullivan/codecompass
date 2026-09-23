# Drift audit — Phase 66 (roadmap + context reconciliation)

**Auditor:** `docs-reconstructor`, MODE 1 (per-phase docs-drift audit).
**Diff audited:** `cc650cd..HEAD` (5 commits: plan, roadmap-audit findings
commit, a fix commit applying `roadmap-context-curator`'s findings, and
the `CONTEXT.md` rewrite).
**Verdict: NO DRIFT** against the checked category (`README.md`,
`docs/**`, `architecture/**`, `ai-docs/**`).

## Scope note

`git diff --stat cc650cd..HEAD` (verified directly, not taken on trust)
touches exactly five files, all under `planning/`:

```
planning/CONTEXT.md                                          | 2537 +--
planning/ROADMAP.md                                          |   11 +-
planning/phase-66-roadmap-context-reconciliation.md          |  165 ++
planning/retros/_roadmap-audit-phase-66.md                   |  203 ++
planning/v1-redefinition/roadmap.md                          |    5 +-
```

`git diff --stat cc650cd..HEAD -- README.md docs/ architecture/ ai-docs/
src/codecompass/` returns **empty output** — confirmed by running it
myself, not assumed. There is no `src/codecompass/` change (no
observable-behaviour change of any kind: no CLI flag, config schema,
generated-file format, module responsibility, data model, default, or
user-facing error message changed), and none of the four checked
current-truth doc trees were touched at all.

`documentation-lifecycle.md` §2.5's checked category is specifically
`README.md`/`docs/`/`architecture/`/`ai-docs/`; `planning/ROADMAP.md` and
`planning/CONTEXT.md` are explicitly outside it (they're governed by
`CLAUDE.md` §§2/4/6 and audited by `roadmap-context-curator`, not by this
per-phase drift audit). So there is nothing in this phase's own scope for
this audit to check under the DRIFT verdict — this is a legitimate,
expected `NO DRIFT`, not an audit that found nothing to look at.

Step 4 (reverse check — did the change make an *existing* README/docs/
architecture/ai-docs sentence false?) is satisfied trivially here since
nothing observable changed, but I checked anyway for pointers into the
two files this phase heavily edited, in case any of them made a claim
about `CONTEXT.md`'s *shape* (length, structure) that the rewrite could
have broken:

- `README.md:215` — "`planning/CONTEXT.md` reflects the current state" —
  still true, and arguably *more* true post-rewrite (the file dropped
  from ~2449 to ~126 lines specifically to stop being an
  ever-appended history and start being current-only, per `CLAUDE.md`
  §4).
- `docs/cli-reference.md:363` — points to `planning/CONTEXT.md` "for the"
  (context) with no claim about its length or structure — unaffected.
- `architecture/overview.md:27-28` — "for milestone/phase status, see
  `planning/ROADMAP.md` and `planning/CONTEXT.md` rather than this
  document" — a pointer, not a content claim — unaffected.
- `ai-docs/CLAUDE.md:22-23` — same kind of pointer, unaffected.

None of these make a claim this phase's edits could have falsified.

## Domain-claim staleness check

`docs/domain/` exists (19 concept pages under `docs/domain/concepts/`,
approved 2026-09-23, Phase 63D), so this check applies. I grepped every
concept page for citations of the three planning files this phase
touched (`planning/v1-redefinition/roadmap.md`, `planning/ROADMAP.md`,
`planning/CONTEXT.md`) and found two genuine candidates worth flagging to
`domain-skeptic` — the lead's framing that this check would find nothing
turned out to be only half right:

**1. Line-number citations into `v1-redefinition/roadmap.md` are now
off by one.**

This phase's fix commit changed 3 lines to 4 lines at
`planning/v1-redefinition/roadmap.md:1030-1039` (the `L-021`
approval-status correction), net **+1 line** inserted into the file
before the content several concept pages cite by line range. Confirmed
directly:

- `docs/domain/concepts/evidence.md:135`, `decision.md:117`,
  `claim.md:126` all cite `v1-redefinition/roadmap.md:1060-1086` for
  "the graph-level naming-collision note." The paragraph they mean
  ("A specific naming collision to resolve...") was at line 1060 before
  this phase's commit and is at **line 1061** now (`grep -n` confirms
  both).
- `docs/domain/concepts/provenance.md:99,117` cites
  `v1-redefinition/roadmap.md:1080-1086` twice for the Phase 57
  candidate-provenance-generalisation paragraph — same +1 shift applies.

This is a citation drift, not a content drift: the cited paragraphs
still exist and say what the concept pages claim they say, just one line
lower than stated. Harmless to a human reader (off-by-one in a ~25-line
range), but it is a factually stale citation, and it's exactly the kind
of thing `domain-skeptic`'s freshness pass should sweep up and correct
in bulk next time it touches these four files, rather than my fixing it
here (read-only mandate).

**2. `connector.md`'s claim about `planning/CONTEXT.md` no longer holds
textually.**

`docs/domain/concepts/connector.md:23-27` asserts that six named
planning files — including `planning/v1-redefinition/roadmap.md`,
`planning/CONTEXT.md`, `planning/ROADMAP.md`, and `CHANGELOG.md` —
"every one of these lists 'connector' alongside 'adapter, protocol,
reference, decision, invariant' purely as a term *to research*." I
grepped all three planning files this phase touched for the literal
string `connector`:

```
planning/ROADMAP.md:352            -> present (Phase 63D row, unedited by this phase)
planning/v1-redefinition/roadmap.md:1561 -> present (unedited by this phase)
planning/CONTEXT.md                -> ABSENT (zero matches)
```

`planning/CONTEXT.md` no longer contains the word "connector" anywhere,
because this phase rewrote it from a ~2449-line running history down to
~126 lines of current-only state (per `CLAUDE.md` §4 — this was the
phase's explicit purpose, not an oversight). The old, historical
Phase-63D-era term list that `connector.md` was citing lived in the
*history* that got deliberately cut. `connector.md`'s enumerated claim
is therefore now false for one of its six cited files — not because
anyone edited `connector.md` or because CodeCompass's own concept of
"connector" changed, but because a planning-process document it cited
for evidentiary support was legitimately rewritten out from under it.

This is squarely a domain-claim staleness candidate, not a DRIFT
finding: it doesn't misdescribe README/docs/architecture/ai-docs system
behaviour, and I'm not asserting `connector.md`'s substantive conclusion
("connector is not a real, distinct CodeCompass concept") is wrong —
only that one of its supporting citations no longer matches the cited
file's current text. That's `domain-skeptic`'s call to make at the next
freshness-reconciliation pass.

Both candidates trace back to the same root cause: this phase edited two
files (`v1-redefinition/roadmap.md`, `CONTEXT.md`) that pre-existing
`docs/domain/concepts/*.md` pages cite by content/line-number, without
anyone checking those citations at edit time — which is exactly the
gap this staleness check exists to catch.

## Summary

- **DRIFT verdict: NO DRIFT.** Confirmed empty diff against
  `README.md`/`docs/`/`architecture/`/`ai-docs/`/`src/codecompass/`; no
  observable system behaviour changed; no reverse-drift on existing
  pointer sentences into the two heavily-edited planning files.
- **Domain-claim staleness candidates (not counted toward the DRIFT
  verdict): 2** — (a) four line-number citations
  (`evidence.md:135`, `decision.md:117`, `claim.md:126`,
  `provenance.md:99,117`) into `v1-redefinition/roadmap.md` now off by
  one line; (b) `connector.md:23-27`'s claim that `planning/CONTEXT.md`
  lists "connector" as a research term is no longer textually true post
  rewrite. Both flagged for `domain-skeptic`, not fixed here.
