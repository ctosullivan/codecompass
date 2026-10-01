# Retro: Phase 79 — clean-room conceptual understanding and documentation reconstruction

## Where things stood before this

Prior phases (75, 77) had already demonstrated that a Domain-stage
research role, working with restricted context, could produce
evidence-backed assertions. This phase asked a harder question: could
that same discipline run genuinely isolated from an existing conceptual
model, be checked afterward against an independently-reconstructed
as-built implementation, and land in real published documentation — not
a review-gated artifact requiring a human-acceptance gate that doesn't
otherwise exist in this project's workflow. The plan itself went through
four amendment rounds before implementation began, each round catching a
real design defect (snapshot integrity confused with legitimate
supersession, a fail-open list-validation gap, a propagation
demonstration that never exercised source-to-evidence discovery, two
stale cross-references).

## Goal

Implement the amended workflow, validate it on one real,
currently-undocumented CodeCompass topic (the Phase 77 first-party
source/symbol subsystem) end to end — research, adversarial review,
freeze, independent implementation reconstruction, alignment comparison,
publication, legacy reconciliation, and two independent verification
passes — and deliver nine portable workflow templates to
`codecompass-template`. Report isolation honestly: `verified` only where
actually achieved, `best-effort` everywhere else.

## What happened

Delivered in full, on the real pilot topic, with real commits at every
stage (not a single end-of-phase commit): four checker functions plus 14
tests landed and passed against the real project corpus (which required
fixing 15 pre-existing YAML block-list violations the new fail-closed
check correctly caught); the Tier-1 isolation preflight was run for
real and failed on all five routes in this environment (filesystem,
search, command, network, and environment-identity all reached content
they were supposed to exclude — `Agent(isolation: "remote")` produced a
same-host git worktree here, not a separate environment); every
downstream stage was run and reported as Tier 2 / best-effort
accordingly, never rounded up. The pilot topic produced 8 reviewed
Claims, a frozen and re-frozen (v1→v2) snapshot with working
historical-integrity and current-divergence checks (verified against
real git fixtures and against the live corpus), a model-blind
implementation reconstruction, an alignment comparison that promoted one
Claim to `verified` and surfaced two genuine knowledge-base gaps, a
disposable propagation-demonstration fixture proving the full
source→evidence→assertions→transitive-dependents→snapshots→both-outputs
chain including real cycle-safety, published documentation (merged into
existing `architecture/` pages, not a new page — see below), and two
independent verification passes, one of which found and fixed a real
pre-existing documentation defect unrelated to this phase's own new
content. Nine template files landed in `codecompass-template` and passed
a fresh-clone link-integrity check before pushing.

One deliberate scope correction mid-phase: the original plan's target
list named `docs/domain/` as a possible publication destination. On
reaching that step, `docs/domain/` turned out to be a separate,
already-approved corpus (its own domain-owner sign-off) covering
CodeCompass's own meta-level concepts, not implementation-level
subsystem detail — this topic's real existing content already lived in
`architecture/`. Corrected in the plan's own reconciliation step rather
than either forcing a mismatched destination or silently deviating
without recording why.

## What worked

- **The fail-closed list-validation redesign immediately proved its own
  worth**: it found 15 real production violations the narrower,
  block-pattern-matching design had missed entirely, on its very first
  run.
- **Testing the isolation claim rather than assuming it** produced a
  genuinely more honest result than the plan's own prior guess (which
  expected Tier 1 to fail only on the network dimension) — it failed on
  every dimension, a stronger and more useful finding.
- **A curation bug in a hand-built export was caught because the
  downstream dispatch's own report was read carefully, not rubber-stamped**
  — the false "internal inconsistency" finding in the first
  implementation-reconstruction pass would have silently corrupted the
  knowledge base's own gap-tracking if trusted uncritically.
- **Running two independent domain-skeptic passes (adversarial review,
  then a separate comparison-mode pass) rather than one combined pass**
  surfaced a real new gap (CL-FPSS-008) that the first pass's own scope
  didn't cover, and correctly kept "alignment" from being conflated with
  "verification" throughout — only one Claim actually met the
  `verified` bar, via a real separate check, not via alignment alone.
- **The two independent verification passes were genuinely worth
  running separately from the work they verify**: the documentation Q&A
  check found a real, pre-existing wording defect
  (`core.Ecosystem has one value`) that had survived unnoticed through
  the ADR, the plan, and this phase's own legacy-reconciliation
  classification pass — none of which had checked that specific sentence
  against `core.py` directly until a reader's plain-reading Q&A exposed
  it.

## What didn't work

- **Building the curated schema-extract export by hand with `sed` line
  ranges was error-prone** — two separate truncation bugs (a dataclass
  cut off mid-definition; a dangling function signature) made it into
  the first implementation-reconstruction dispatch's input, producing a
  wasted first pass and a real, disclosed false finding before the
  re-run. A small script asserting the extracted block actually parses
  as valid Python (or otherwise self-validating) before handing it to a
  dispatch would have caught both immediately, for near-zero cost.
- **`L-023`'s "not immediately dispatchable by name" limitation resolved
  itself partway through the session** (the newly-created
  `implementation-reconstructor` type became dispatchable by name later
  the same session, confirmed by a system notification, after being
  used via the `general-purpose` substitute earlier) — worth refining
  the learning's own wording to note it is a startup-latency condition,
  not a whole-session block, so a future phase doesn't assume the
  substitute is needed for the entire session once confirmed needed once.

## Anything worth remembering

- The `Ecosystem`-cardinality documentation defect and its root cause
  (an ambiguous sentence in `decisions/0065`'s own already-Accepted
  prose, echoed verbatim into `architecture/overview.md`, propagated
  through this phase's own evidence records as an accurate *quotation*
  of the ADR without being cross-checked against `core.py` until the
  independent verification step) is worth a `planning/learnings/` entry:
  quoting a source document accurately is not the same as the source
  document being correct, and a legacy-reconciliation pass that
  classifies a claim `supported` because it matches existing prose still
  needs the prose itself checked against primary evidence at least once,
  not only checked for internal agreement between documents.
- The `L-023` refinement above is also worth a `planning/learnings/`
  update to the existing entry rather than a new one.

## What's next

Learning triage (`knowledge-curator`), a docs drift audit
(`docs-reconstructor` MODE 1) scoped to this phase's diff, an independent
completion audit (`release-phase-auditor`) checking both the
workflow/template-completion track and the strict-isolation track
separately, and the terminal `roadmap-context-curator` reconciliation —
in that order, per this project's own Definition of Done.

## Addendum: fifth amendment (2026-10-01, the day after `done`)

A direct review of the delivered, already-`done` result found four real
defects, corrected by `decisions/0067` and the plan's own §0 "Fifth
revision" entry (full technical detail there, not repeated here). Worth
recording here specifically because each defect was a genuine miss by
this phase's own closeout process, not a hypothetical:

- **The fail-closed snapshot-validation redesign (§5.3, fourth revision)
  was itself still fail-open at the edges it didn't anticipate.** It
  correctly fixed hashing-against-the-live-file, but never validated that
  a snapshot's own *inventory* was complete — a sidecar with real content
  removed still validated clean, because the check only ever examined
  entries already present. The lesson generalizes past this specific
  checker: a fail-closed redesign that fixes the *mechanism* it was asked
  to fix can still leave a *different* fail-open gap at the mechanism's
  own edge (here: completeness, not integrity), and "add a test for the
  exact scenario named" doesn't substitute for asking "what would a
  maximally-reduced malicious or accidental input look like, and does
  this still catch it."
- **A merge step silently dropped information a prior step had carefully
  added.** The clean-room draft's own citations existed, were correct,
  and were lost specifically at the one step (legacy reconciliation) that
  wasn't itself re-checked for having preserved them — the independent
  verification passes that *did* run (documentation Q&A, coding-context
  evaluation) happened to check factual accuracy, not citation presence,
  so neither caught this. Worth a general habit: when a merge/
  reconciliation step is expected to preserve prior structure (not just
  prior facts), check for that structure's survival explicitly, not only
  for whether the resulting prose is still accurate.
- **"Honestly labelled" and "achieved" are different claims, and a
  closeout report can accidentally conflate them in exactly the place
  that matters most** — a verdict line. Every piece of evidence behind
  this phase's own Track 2 "PASS" was itself accurate (the labelling
  really was honest, really was checked); the defect was purely in how
  that accurate finding got summarized into one word. Worth a durable
  habit for any future honesty-as-the-control workflow: a verdict line
  for "was X achieved" and a verdict line for "was the claim about X
  honest" should never share one `PASS`/`FAIL` token, even when both
  happen to be favorable, because a reader cannot tell which one a
  shared token refers to.
- **A rerun's own transcripts turned out to still be real, original
  evidence worth recovering**, not just a lesson for next time. The
  original pilot dispatches' raw JSONL transcripts were still present on
  local disk; a mechanical pass over them produced genuine boundary-check
  evidence (including a real, previously-undetected finding) that didn't
  require fabricating anything or claiming a fresh rerun was equivalent
  to the original execution. Worth remembering structurally: this
  project's own local Claude Code session state is itself a source of
  recoverable evidence for a reasonable window after a dispatch
  completes, not just the dispatch's own self-report — worth checking
  before assuming evidence is unrecoverable.
- **A link-resolution check and a usability check are different
  instruments measuring different things**, and the former is cheap
  enough to reach for by default even when the latter is what was
  actually asked for. The real exercise (a fresh agent actually adopting
  the template against a real small project) found a defect
  (README/LICENSE collision) that is structurally invisible to any
  link-checker, since every individual link in the offending instruction
  resolves fine — the defect is in what a literal reading does to a
  *second*, pre-existing file on the target side, a category of failure
  a link-checker cannot model at all.

Candidate learnings from this addendum are included in the triage
dispatched for this amendment, alongside this phase's own original
candidates.
