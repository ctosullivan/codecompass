# Phase 66 retro — Roadmap + context reconciliation

- **Date:** 2026-09-24
- **Commit(s):** `598460c` (plan + ROADMAP row split), `4b0f10f`
  (roadmap audit findings), `2e184c4` (audit fixes), `c2526e5`
  (`CONTEXT.md` rewrite), `3a6e26b` (drift audit), `b7d0bf3` (domain
  freshness corrections).
- **Agents used:** `roadmap-context-curator` (`ROADMAP.md` full-table
  audit), a `fork` (`CONTEXT.md` information-loss cross-check),
  `docs-reconstructor` (per-phase drift audit), `domain-skeptic`
  (domain-corpus freshness reconciliation).

## Where we are

Stage G's third phase, immediately following Phase 65 (done,
2026-09-23, PASS). This phase's own named scope
(`ROADMAP.md`/`CONTEXT.md` reflect the shipped v1, deferred work
clearly parked) is small on paper but carried one substantial,
long-deferred piece of real work: `CONTEXT.md`'s own append-only drift,
flagged as a non-blocking observation by Phase 65's own
`release-phase-auditor` audit and explicitly named as this phase's job
in that same closeout's "Next concrete step."

## Goal

Audit `planning/ROADMAP.md`'s full table against actual project state;
confirm every deferred/not-funded/conditional item is clearly parked
with a stated revisit trigger; rewrite `planning/CONTEXT.md` to comply
with `CLAUDE.md` §4's own explicit "overwrite, don't append" instruction.

## Scope delivered vs planned

Delivered exactly as planned:

- **§1.1 `ROADMAP.md` audit**: full table read (Phase 0 through Stage
  G). Three real, minor findings — a status-legend omission ("not
  funded" used but never defined), a stale present-tense claim about
  `L-021`'s approval status in `v1-redefinition/roadmap.md`, a missing
  plan-file link on row 55 — all fixed. GATE DD/Stage E confirmed
  legibly, deliberately open (not an oversight); Phases 24/25/48/50's
  revisit triggers confirmed still accurate.
- **§1.2 `CONTEXT.md` compaction**: rewritten from 2449 lines to 126,
  following `CLAUDE.md` §4's own four named fields plus a "Known
  standing gaps" section for genuinely current-state facts with no
  natural home in a retro. A dedicated fork cross-check confirmed no
  genuine information loss before the rewrite; the fork's own read
  covered the full prior file, not a sample.

One real, unplanned finding surfaced by this phase's own per-phase
drift audit: the `CONTEXT.md` rewrite broke `docs/domain/concepts/connector.md`'s
own citation (a file-list claim that named `CONTEXT.md` as one of six
places "connector" appears as a research term — no longer true after
the rewrite), alongside four off-by-one line citations from the
`L-021` fix's own one-line insertion. Both resolved via the
domain-corpus freshness reconciliation mechanism (`domain-skeptic`),
not silently patched by the lead.

## What was achieved

`ROADMAP.md` is now internally consistent (legend matches usage, no
row's prose contradicts its own status column, deferred/conditional
work is legibly parked). `CONTEXT.md` now actually complies with the
rule that has governed it since `CLAUDE.md` §4 was first written —
future sessions resuming from it read a current-state summary, not a
multi-day history lesson. The domain corpus's own citation accuracy
into `v1-redefinition/roadmap.md` and `CONTEXT.md` is current again.

## What worked

- **Dispatching a fork specifically to cross-check for information
  loss before a large deletion**, rather than trusting the lead's own
  read-through of a 2449-line file, is exactly the kind of
  independent-verification discipline this project applies everywhere
  else (drift audits, DoD audits) applied to a one-off compaction task.
  It found real corroborating evidence (the two "undocumented decision"
  callouts, the git-hosting-org detail) for every claim it checked,
  giving genuine confidence the deletion was safe — not just an
  assumption that retros "probably" cover everything.
- **The domain-corpus freshness reconciliation mechanism caught a real,
  non-obvious cross-file staleness case on its first non-trivial
  exercise since Phase 63D's own approval.** `connector.md`'s own
  staleness didn't come from anything touching `docs/domain/` directly
  — it came from an edit to a completely unrelated file (`CONTEXT.md`)
  that happened to be one of six files a concept page cited by name.
  This is precisely the kind of drift `docs-reconstructor`'s own
  domain-claim staleness check (added at Phase 63D) was designed to
  catch, and it worked as designed on the first real case that wasn't
  the trivial "nothing to check" result Phase 64/65 both had.
- **`domain-skeptic` correctly declined to edit the corpus itself even
  when this dispatch's own prompt suggested it could** ("you may
  resolve this yourself... a one-line citation fix is not a change to
  any claim's own meaning"). The agent's own charter is stricter than
  the dispatching lead's own suggestion, and it held that line rather
  than deferring to the dispatch instruction — exactly the write-
  boundary discipline `decisions/0060` intends, working correctly even
  against a lead's own (mistaken) invitation to bend it.

## What didn't work

**The lead's own dispatch prompt to `domain-skeptic` suggested it could
apply a "obviously-correct" citation fix directly, contradicting that
role's own explicit, unconditional write-boundary rule** ("read-only
toward... the approved domain corpus itself — never edits any of them
... even an obviously-correct one-line fix to a concept page is not
yours to make"). No harm resulted — the agent correctly declined and
named the fix for the lead instead — but the prompt itself was wrong to
suggest otherwise, and relied on the agent's own discipline rather than
the lead's own prompt being correct in the first place.

## Lessons learnt

- **A file need not be under `docs/domain/` itself to cause a
  domain-corpus staleness finding** — any file a concept page cites by
  name is a dependency the corpus's own accuracy relies on, and an edit
  to that file (even one entirely unrelated to domain meaning, like a
  `CONTEXT.md` compaction) can silently invalidate a citation. Worth
  keeping in mind for any future large edit to a file `docs/domain/`
  might reference by name.
- **When dispatching an agent with a hard, unconditional write-boundary
  rule, don't suggest an exception to it in the dispatch prompt, even
  for what looks like an obviously-safe case** — the rule exists
  precisely because "obviously safe" is a judgment call the role itself
  isn't supposed to make, and a prompt that invites the exception is a
  real (if harmless-this-time) drafting mistake, not a neutral
  suggestion the agent is free to take or leave.

## Process-improvement feedback

None beyond the lesson above — no new mechanism needed, just care when
drafting future `domain-skeptic` dispatch prompts.

## Candidate learnings filed

None identified by the lead. Given this project's own established
precedent of not trusting a "nothing to file" call at face value
(`L-030`, `L-035`/`L-036`, `L-038`), `knowledge-curator` should
independently confirm this during closeout rather than the lead's own
unilateral judgment standing unchecked.

## Where we're going

Phase 67 (final validation: self-dogfood + Ledgerkit + Stage F
smoke-test confirmation) is next — a lightweight confirmation pass, not
a full re-run. No gate blocks Phase 67 — Phase 66 confirmed the planned
trajectory without changing it. Its own plan does not yet exist and
must be written per `CLAUDE.md` §1 before implementation begins.

## Time / cost note

Four agent dispatches (one `roadmap-context-curator`, one fork, one
`docs-reconstructor`, one `domain-skeptic`), two full `pytest` runs. No
`src/codecompass/` change — pure `planning/`/`docs/domain/` work.
