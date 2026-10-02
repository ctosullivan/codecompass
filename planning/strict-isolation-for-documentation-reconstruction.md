---
status: backlog candidate — not funded, not scheduled, no phase number.
  Recorded 2026-10-02 at direct user request. Does not implement
  anything and does not gate current or future documentation-
  reconstruction work; Phases 79 and 80 remain `done` under their own,
  honestly-reported `UNMET`/`best-effort` isolation verdicts.
---

# Strict mechanical isolation for documentation-reconstruction stages

## Problem

CodeCompass's own clean-room documentation-reconstruction methodology
(`decisions/0066`/`0067`/`0068`, exercised at Phase 79 on one topic and
at Phase 80 project-wide) depends, at three of its five stages, on one
stage genuinely not having seen another: a model-blind implementation
reconstruction must not have seen the conceptual knowledge snapshot or
legacy documentation; a fresh documentation draft must not have seen
legacy narrative documentation; legacy reconciliation must happen only
after the fresh draft is already committed.

**No mechanism in current use actually enforces any of these
boundaries.** Every dispatch to date has used either a curated export
directory (content the dispatch is *pointed at*, not prevented from
reaching anything else) or instruction-only scoping (full tool access,
told what to stick to). Verification after the fact — a mechanical
transcript/boundary-check script reading a dispatch's own raw tool-call
log for out-of-scope `Read`/`Glob`/`Grep`/`Bash` references — is real,
useful, and has caught genuine deviations (one `knowledge-curator`
dispatch at Phase 79 read two out-of-scope files; a Tier-1 preflight
probe reached every excluded route it was pointed at). But it is
*detection*, not *prevention*: it tells you what a dispatch did, never
what it was mechanically unable to do. Both Phase 79 and Phase 80
therefore honestly report strict clean-room isolation as **UNMET**,
separately from and without weakening their own, independently-audited
**PASS** verdicts on workflow/template completion.

This is not a new finding — it is the single most consistently
reconfirmed result across both phases (see "Existing isolation work,
linked not duplicated" below) — and it is reasonable to expect a third,
fourth, and further application of this same methodology to keep
reconfirming the identical gap unless the gap itself becomes a funded
capability.

## Existing isolation work, linked not duplicated

- `decisions/0066` — establishes the Tier 1 (`Agent(isolation:
  "remote")`)/Tier 2 (same-host curated export) split, the required
  five-route preflight (filesystem/search/command/network/delegation),
  and the permanent `best-effort` label for Tier 2 "regardless of any
  single probe's own incidental result" (§ cited verbatim: "a
  same-host curated export... provides no architectural guarantee
  regardless of what one test finds").
- `planning/knowledge/first-party-source-symbols/isolation/tier1-preflight.md`
  — the real, dispatched Tier 1 preflight probe. **Result: failed all
  five routes** in this environment (filesystem, search, command,
  network, and environment-identity all reached content the probe was
  told to treat as excluded) — `Agent(isolation: "remote")` behaved as a
  same-host git worktree, not a genuinely separate environment, here.
- `planning/knowledge/first-party-source-symbols/isolation/isolation-evidence-inventory.md`
  — the corrected, final accounting (fifth amendment): what a genuine
  strict-isolation claim would require (manifest, raw transcript, access
  log, a boundary mechanism that makes violation *impossible* not merely
  *unobserved*), a per-dispatch inventory of what actually existed for
  six Phase 79 pilot dispatches, and the explicit correction of an
  earlier, wrongly-worded "Track 2: PASS" to the honest "UNMET."
  Promoted the now-standing project rule: honest `best-effort` labelling
  being confirmed compliant is never the same claim as isolation being
  achieved.
- `planning/knowledge/first-party-source-symbols/isolation/boundary_check.py`
  — the real, reusable mechanical transcript-analysis script (parses a
  dispatch's own original JSONL transcript for out-of-scope tool-call
  paths). Detection-only, as above; reused at Phase 80 unchanged for the
  same purpose.
- `planning/phase-79-clean-room-understanding-and-documentation-reconstruction.md`
  and `planning/phase-80-codecompass-documentation-reconstruction.md` —
  both phases' own plan files state, in advance, that this gap is
  expected and acceptable for their own scope ("best-effort separation
  is permitted; strict isolation remains UNMET unless mechanically
  demonstrated").

This item does not restate or re-derive any of the above — it proposes
funding the capability those records all independently conclude does
not yet exist.

## Proposed scope

**1. Stage-specific enforced boundaries.** Three distinct input
contracts, not one generic "isolated dispatch":

- *Implementation reconstruction* receives runnable primary
  implementation evidence — source, tests, fixtures, and whatever
  transitive dependencies those tests/source actually require to run —
  and nothing else. It must not be able to reach conceptual knowledge
  (`planning/knowledge/`), legacy documentation (`README.md`, `docs/`,
  `architecture/`, `ai-docs/`), or any prior reconstruction's own
  narrative output.
- *Fresh documentation drafting* receives the approved, frozen knowledge
  snapshot, the implementation-reconstruction report, and the comparison
  findings between them — and nothing else. It must not be able to reach
  legacy narrative documentation (the exact material Phase 79/80's own
  draft-before-reconciliation ordering already keeps *procedurally*
  separate, but not *mechanically*).
- *Legacy reconciliation* receives both the fresh draft and the legacy
  documentation, but only once the fresh draft already exists as a real,
  committed artifact — ordering, not merely scoping, must be the thing
  enforced.

**2. A genuinely isolated execution mechanism.** Evaluate containers, a
separate worker process/machine, or another mechanism capable of all of:
fresh agent context with no inherited conversation history; an
allowlisted input set (not an instructed one); and enforcement — not
merely absence of a route tried so far — against parent-directory
traversal, Git history (including from a shared `.git` or any reachable
remote), symlinks, mounts, retrieval tools (`WebFetch`/`WebSearch`), and
any network route (the open, likely-unclosable leak `decisions/0066`
already identified for a public repository: network egress through a
granted `Bash` bypasses filesystem isolation entirely). **A separate
directory or an instruction alone does not qualify** — this is the
literal Tier-2 posture already tried and already labelled
`best-effort`.

**3. Runnable, reproducible inputs.** Whatever is actually fed to an
isolated stage must be recorded as a manifest: file list, revision, and
a content hash per file (the same discipline `check_knowledge_base.py`'s
own snapshot format already uses for evidence citations). Must include
whatever transitive implementation dependencies and test fixtures a
reconstruction stage needs to actually *run* what it's given — Phase
80's own Stage 2 reconstruction found exactly this gap in its own
bounded export (several sibling modules excluded by design, one test-
fixture directory missing by oversight), so isolation that prevents
verification is itself a defect, not a success. A manifest must
distinguish a deliberate exclusion from an accidental omission.

**4. Meaningful acceptance checks.** Not merely "the dispatch complied
this time" — demonstrate the permitted inputs are sufficient for the
stage's own selected real workflow(s) to actually execute and produce a
usable result, and separately attempt real access to forbidden files,
repository history, and the escape routes named in point 2; every
attempt must be mechanically denied, not merely unused. Also verify
draft-before-reconciliation ordering holds mechanically (the
reconciliation stage's own environment should not even contain the
legacy documentation until after the draft's own commit exists), and
retain the evidence (manifest, transcript, denial log) the same way
`isolation-evidence-inventory.md` already does for the current
best-effort approach.

**5. Honest failure handling.** If true mechanical enforcement cannot be
established in whatever environment this runs, report strict isolation
as **UNMET** and say why, exactly as Phase 79/80 already do — never
silently fall back to best-effort and drop the label. Any fallback that
is used must be explicitly labelled `best-effort`, not folded into an
unqualified "isolation: PASS." Documentation-workflow completion,
documentation accuracy, coding-context usefulness, and isolation itself
must remain four separately reported results (per `L-079`, Phase 80 —
`planning/v1-redefinition/context-quality-evaluation.md` §1 — these
operate at different levels of granularity and are not substitutes for
each other; the same principle applies to isolation, which is a
mechanism-level property distinct from all three outcome-level ones).

**Template**: `codecompass-template` adoption of any resulting mechanism
stays optional and concise — a short pointer in
`optional-clean-room-workflow/README.md` at most, once a working
approach exists. No template changes now.

## Explicitly out of scope for this item

- Implementing any part of the above now.
- Making this a new gate, requirement, or blocker for any current or
  future documentation-reconstruction phase. Phase 79 and Phase 80 both
  remain `done`, with their own honestly-reported `UNMET` isolation
  verdicts standing as final, correct, and unaffected by this item's
  existence.
- Reopening, reordering, or depending on Phase 78 (Priority A backlog
  rationalisation + second Ledgerkit trial) or any of Priorities A-C/E-F.
- Any change to `codecompass-template` beyond, eventually, a brief
  pointer once a real mechanism exists.

## Dependencies

- A genuinely separate execution substrate this project's own
  environment can actually reach (a container runtime, a separate
  worker/VM, or an equivalent) — not yet confirmed available; the one
  mechanism tried so far (`Agent(isolation: "remote")`) failed its own
  preflight on every route in this environment and cannot be assumed to
  behave differently without re-testing in whatever environment
  eventually attempts this.
- `decisions/0066`'s own five-route preflight protocol (reusable as the
  acceptance-check baseline, extended per point 4 above with active
  escape-route attempts, not just passive route probing).
- `planning/knowledge/first-party-source-symbols/isolation/boundary_check.py`
  (reusable, detection-side building block — real mechanical transcript
  analysis, independent of whatever enforcement mechanism point 2
  eventually selects).

## Acceptance criteria (for whenever this is actually planned and run)

1. At least one of the three stage boundaries in point 1 demonstrated
   with a real, mechanically-enforced boundary (not a curated export,
   not an instruction) — containers or an equivalent separate-worker
   mechanism, confirmed by denied real access attempts against every
   escape route named in point 2, not merely an unused one.
2. A real manifest (files, revisions, hashes) for whatever was fed to
   that stage, with every transitive dependency/fixture needed for the
   stage's own real workflow to run — confirmed by actually running that
   workflow inside the enforced boundary and getting a usable result,
   not just confirming the boundary holds for an empty or trivial task.
3. Draft-before-reconciliation ordering demonstrated mechanically for at
   least one topic, not merely via commit-order inspection after the
   fact.
4. A written, final verdict using the same four-way-separated reporting
   this item itself requires (isolation / workflow completion /
   documentation accuracy / coding-context usefulness), with isolation
   reported as `verified` only if every probe and every active escape
   attempt failed to reach excluded content, `best-effort` otherwise,
   `UNMET` if no enforcement mechanism could be established at all.
5. Independent `release-phase-auditor` completion audit, per
   `CLAUDE.md` §5, same as any other phase.

## Suggested priority

**Priority D cross-reference, unscheduled.** This capability only has
value because Priority D's own documentation-first workflow (Phase 77
template delivery, Phase 79/80 clean-room methodology) exists and is in
active, repeated use — it hardens that workflow's own weakest,
repeatedly-reconfirmed link, rather than opening new product surface.
Not urgent: both phases that found this gap closed successfully with an
honestly-reported `UNMET` verdict, and nothing about CodeCompass's own
shipped functionality depends on it. Revisit when either (a) a third
independent application of the clean-room methodology reconfirms the
same gap a third time (the recurrence bar this project's own learning
lifecycle already uses elsewhere, e.g. `context-gaps/README.md`'s "a
second independent occurrence" bar), or (b) a genuinely separate
execution substrate becomes available/confirmed in this project's own
working environment, whichever comes first.
